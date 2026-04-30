# Imperial Settlement: War Settlement + Ally Participation Spec

> **Status:** v1.22 PRE-A1 SYNTHESIS HARDENING - A1 is foundation-only and must start with mapped-nation capital helper safety, settlement containers, old-save defaults, empty index/cache scaffolding, and cache invalidation hooks before any behavioral settlement work. Current settlement participants must exist in scenario/map data; future nations enter one by one through the `ADDING_CONTENT.md` nation checklist plus settlement readiness fixture when the map/scenario adds them. A2 owns `war_id` threading; A3 owns always-on post-merge war-instance invariant assertions; B owns contribution-before-war-score-gate hooks; C owns raw harshness, explicit common-peace tuning escalation, settlement dialogue taxonomy, settlement cooldown serialization, and settlement dialogue overflow retry storage; C2 must pass a manual settlement-review comprehension gate before D1 starts; D owns ratification cache-ordering. Coding may start from `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.19.
> **Last Updated:** April 30, 2026
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
- Repeated war-instance lookups use per-turn indexes (`war_instances_by_leader`, `war_instances_by_participant`) built from active `war_instances` and invalidated by the same mutation paths that change participants, leaders, pair status, or archive state. Use dirty-flag lazy rebuilds so a common peace touching multiple pairs marks the indexes dirty once and rebuilds at most once before the next reader.
- Player-facing advisory rows use deterministic salience filtering: top 5 default rows, grouped overflow behind "View all participants."
- Dispatch and notification output is aggregated. No settlement may emit one popup or rail notice per participant.
- `war_instance` grouping is additive over pairwise diplomacy. Pairwise `diplomatic_states`, `war_scores`, and WPS `war_objectives` remain the mechanical source of truth.
- Focused tests must build synthetic full-Europe fixtures instead of relying on the current small live map: at least the canonical 13 DG-1 internal nation ids (`France`, `Britain`, `Austria`, `Prussia`, `Russia`, `Spain`, `Ottoman`, `Sweden`, `Naples`, `Bavaria`, `Saxony`, `Portugal`, `Denmark-Norway`), 100+ region ids where territory logic is exercised, 20 active pair keys, one cache/index fixture with 20 active `war_instance` records, and one 6+ participant side. Display names such as `Ottoman Empire` or `Naples/Two Sicilies` are aliases, not fixture ids. Fixture helpers that do not monkeypatch active-nation lookup must extend the fixture world's active roster, including `world.enemy_nations` / runtime nation setup, before adding synthetic regions/controllers; regions alone do not make a future nation active.
- **Mapped-nation settlement model:** A nation participates in settlement only if it exists in the current scenario/map state or in an explicit synthetic fixture with authored regions/controllers and relevant nation config. Britain is a normal mapped participant in the current runtime because it controls mapped regions and has `NATION_CAPITALS["Britain"] == "Netherlands"` as the current-map home/spawn region. Russia and other future nations are absent from settlement until scenario/map data adds them. Britain's later Channel/naval reachability problem belongs to a naval/movement abstraction, not settlement identity.
- **Capital helper safety:** Settlement code may add `get_settlement_home_capital(nation)` as a helper over `NATION_CAPITALS.get(nation)`, but missing capital data must not infer participation. Capital-dependent components must tolerate `None` by skipping the capital-specific term or scoring it as `0`, and real mapped major nations missing a capital should produce a validation warning/test failure in the owning fixture.
- **A1 opening gate:** Slice A1 is a foundation slice, not a behavioral settlement slice. Before any `war_instance` creation path, settlement scoring, or common-peace flow is implemented, A1 must land the mapped-nation capital helper, `WorldState` settlement containers, save/load defaults, empty war-instance index/cache scaffolding, and cache invalidation hooks. A2, B, C, and D may not borrow those responsibilities forward; they must consume the A1 foundation through tests.

### 0.1 Future Nation Onboarding Contract

Imperial Settlement must remain buildable as Europe grows one nation at a time. Production settlement logic must read the active scenario/map/config data and must not hard-code the canonical 13-nation full-Europe fixture roster. The canonical 13 ids are test-fixture coverage targets, not a runtime whitelist.

`docs/ADDING_CONTENT.md#adding-new-nations` is the operational checklist for adding a new settlement-capable nation. A nation is eligible to participate in settlement only after the nation addition checklist supplies, or explicitly defaults with validation, all of the following:

- Stable internal nation id and optional display aliases. Pair keys, `war_instance` participants, memories, bargain references, and save data use the internal id only.
- `power_tier` authored in scenario/config data. Do not rely on the silent `secondary` fallback for settlement tests, leader scoring, side-pressure scoring, major-power consultation, or Balance of Europe reactions.
- Mapped capital/home region through `NATION_CAPITALS` and existing scenario/map region data. `None` is allowed only for incomplete fixtures or future scenario data under construction; it does not make an active settlement participant.
- Controlled starting regions, or an explicit "absent from this scenario" status. Absent nations do not receive `WAR` pair keys, contribution scores, settlement standing, or common-peace evaluation.
- Economy/action/manpower/diplomat data sufficient for the normal diplomacy loop. Default nation-config fallbacks may supply generic economy/action/authority values, but settlement-ready scenario data must still define capital/home, diplomat, tier, pair states, and relations.
- Diplomatic pair state and relation entries against every other active scenario nation. Adding the 14th active nation means adding the 13 new bilateral pairs needed for diplomacy and settlement grouping.
- Settlement interest data: `NATION_DESIRE_PROFILES` entry, Talleyrand commentary or generic fallback, AI counter-offer desire entry, and `SPECIAL_BONUSES` entry or an explicit empty dict when the nation has no clause-specific bonuses.
- Fixture coverage proving the new nation can be added alone: capital helper lookup, active-nation detection, pair-key creation, at least one war-instance participant path, side-pressure/standing behavior at its authored tier, and graceful behavior when optional desire/profile fields are empty.

Full-Europe tests may still synthesize all 13 DG-1 ids at once to stress scale, but production onboarding is incremental. A future nation should be able to land with one checklist, one focused fixture, and no unrelated settlement rewrites.

### 0.2 Pair Key Conventions

Settlement groups existing diplomatic data; it does not replace the key conventions those systems already use.

| Convention | Shape | Used by | Rule |
|------------|-------|---------|------|
| Sorted diplomatic pair key | `"A|B"` with alphabetical order | `diplomatic_states`, `nation_relations`, `war_scores`, `battle_records`, `war_objectives`, `active_diplo_keys`, `resolved_diplo_keys`, `diplo_key_meta` | Always build through `world._make_diplo_key(a, b)` or the equivalent sorted helper. |
| Directional grievance key | `"actor|victim"` | `betrayal_history`, `settlement_shut_out` grievance flags, hard-reject posture reads | Never sort. Use the existing directional betrayal helper semantics. |
| War Bargain cooldown key | `"promiser|beneficiary::target_enemy"` | `diplomatic_commitments[*]["cooldown_key"]` | Preserve source-pair direction and named enemy; do not collapse into a sorted diplomacy key. |
| War identity | `"war_{sequence}"` | `war_instances`, `war_contribution_scores`, settlement dialogues, dispatch/ledger routes | Groups pair keys. It is not a replacement for pair keys and must be rewritten atomically on merges. |

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

Defensive-coalition settlements use the same mechanics but a different voice. If France is the defender-side leader in a coalition war it did not start, the flow is still parameterized by `proposer_side`, but presentation should shift from imperial overreach to defensive settlement counsel: preserving the coalition, ending the emergency, and judging which allies earned a say after the defense. Slice E owns that copy distinction; the mechanical rules remain the same.

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
- War-entry integration: `compute_war_entry_score()` / war-entry score formula, hard blocks, `join_opportunity`, counter-bargains, `repudiate_bargain` (WB-C)
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
- This spec does not model neutral mediation, neutral broker pressure, or pre-settlement mediation offers.
- This spec does not model a Congress of Vienna-style multipolar settlement where no single side leader accepts terms. Current common peace remains leader-mediated; a future "Congress System" phase may own neutral hosts, great-power plenipotentiaries, agenda bargaining, and AI-vs-AI multipolar settlements.
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

This is intentionally distinct from `COALITION_SPEC.md`'s `coalition_war_score`. `coalition_war_score` summarizes a coalition's live military situation for coalition behavior; `side_pressure_score` summarizes the proposer's pressure against the specific covered enemies in one settlement package and feeds common-peace acceptance.

For a proposed common peace, compute pressure from the proposer side against each covered enemy participant.

**Covered enemy participant definition:** a covered enemy participant is an enemy-side nation included in the proposed common-peace package. A nation is covered when at least one term names it as `from` / payer / ceder, when the package burdens it through vassalage / forced alignment / liberation, or when it is the opposing side leader. Empty covered-enemy sets are invalid before scoring.

```python
pressure_terms = []
for enemy in covered_enemy_participants:
    active_pairs = [
        get_war_score_for(world, side_member, enemy)
        for side_member in proposer_side_participants
        if world.is_at_war(side_member, enemy)
    ]
    if not active_pairs:
        # Hard stop: no proposer-side member is at war with this covered enemy
        return hard_stop("no_direct_war_score_for_covered_enemy", enemy=enemy)
    direct_score = max(active_pairs)
    weight = {"major": 3, "secondary": 2, "minor": 1}.get(
        world.get_power_tier(enemy) or "secondary",
        2,
    )
    pressure_terms.append((direct_score, weight))

side_pressure_score = round(
    sum(score * weight for score, weight in pressure_terms)
    / sum(weight for _, weight in pressure_terms)
)
```

Rules:

- Empty `pressure_terms` is a hard stop: common peace has no valid covered enemy.
- If live confirm revalidation strips every covered enemy because of separate peace, armistice expiry, elimination, rebellion, or pair-status changes, the staged proposal is voided with `no_covered_enemy_participants` and no mutation. Do not coerce an empty covered set into white peace.
- Implementation must build `direct_scores` before calling `max()`. A covered enemy with no active direct pair against the proposer side is a hard stop for that enemy: `no_direct_war_score_for_covered_enemy`.
- Settlement preview / confirm computes `direct_scores` once per `(war_id, proposer_side, covered_enemy_participants, current_turn, draft_terms_hash)` evaluation and reuses that memoized map for side pressure, direct-score gates, burden penalties, territory-legitimacy `weak_pressure_penalty` checks, and advisory rows. Do not call `calculate_war_score()` repeatedly for the same pair inside one draft preview.
- Scores are clamped to the existing `[-100, 100]` war-score range after aggregation.
- `side_pressure_score` is a headline/base component. It is not blanket authorization for target-specific demands.
- Terms against a non-leader enemy with `direct_score < 20` are legal only as extreme terms and add the Step 4 burdened-participant penalty.
- Use `round()`, not floor division, so small coalition wars do not lose several pressure points to integer truncation.
- Within each covered enemy, `direct_score = max(active_pairs)` selects the strongest proposer-side pressure against that enemy. Slice C must include a fixture where the side leader is losing or barely winning while a minor ally has the selected high score; debug output must name the selected `direct_score_source` so designers can see when the maximum pair, not the leader pair, drove acceptance.
- The enemy-power weighted average can dilute a strong major-vs-major score when many minor covered enemies are included. This is intentional anti-farming behavior, but Slice C must pin at least one weighted-dilution fixture so future tuning changes are explicit.
- Mixed-strength coverage guard: the weighted average must be tested against a partial-coverage exploit. A package that covers a crushed minor and a lightly pressured major will often produce lower `side_pressure_score` than a narrow package against only the minor; that is expected as target-specific legitimacy, but it must not make full coalition settlements mechanically irrational. Slice C must include a fixture comparing narrow minor-only coverage against full minor+major coverage with identical non-coverage components. If the full package falls from acceptable to rejected solely because the low-pressure major is covered, tune the common-peace constants before lock. The first tuning knob remains a small `base_side_pressure` scaling adjustment from the `0.65` baseline; do not add a separate breadth bonus unless the fixture proves scaling/threshold tuning cannot preserve both anti-farming and full-settlement viability.
- Common-peace incentive guard: Slice C must also compare narrow coverage, full common peace, and serial bilateral/separate peace against the same war state. If serial settlements gain a large pressure advantage that the serial fallout penalty cannot plausibly offset, adjust the primary common-peace tuning knob or serial-fallout constants before lock. The headline feature must remain a rational option after decisive coalition victories, not only a roleplay choice.

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
    "created_sequence": int,              # from world.next_war_instance_id
    "originator": "France",
    "origin_target": "Austria",
    "origin_diplo_key": "Austria|France",
    "objective_keys": ["Austria|France"],  # WPS-A war_objectives keys, not a new objective store
    "active_diplo_keys": ["Austria|France", "France|Prussia"],
    "resolved_diplo_keys": [],
    "diplo_key_meta": {
        "Austria|France": {
            "attacker": "France",
            "defender": "Austria",
            "joined_turn": 12,
            "pair_status": "war",  # war | armistice | resolved
            "resolved_turn": None,
        },
    },
    "attacker_leader": "France",
    "defender_leader": "Austria",
    "leader_source_by_side": {           # side-scoped; never infer one side from the other
        "attackers": "originator",       # originator | coalition_leader | scripted
        "defenders": "origin_target",    # origin_target | coalition_leader | scripted
    },
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
    "ended_turn": None,
    "end_reason": None,
}
```

### 7.2 Relationship to current diplomacy state

`war_instance` does not replace pairwise war state.

- `diplomatic_states` remains the source of truth for whether two nations are at war.
- `war_instances` group those pairs into one political conflict for reporting and settlement.
- `world.next_war_instance_id: int = 1` allocates IDs. Creating a new instance uses `war_id = f"war_{world.next_war_instance_id}"`, stores that integer as `created_sequence`, then increments the counter. Do not derive `war_id` from turn number, side names, or `diplo_key`; full-Europe simultaneous declarations can collide.
- Create a skeleton `war_instance` before `_process_war_cascade()` runs with the originator and origin target only, then pass `war_id` through the cascade path so honored/refused/vassal entries append to `attackers`, `defenders`, `side_by_nation`, `active_participants`, and `participant_meta` as each entry resolves.
- Cascade entrants attach to the existing `war_id` of the declaration that pulled them in.
- War Bargains created at war entry (WB-C `join_opportunity`) attach to the same `war_id`.
- **Active pair-key ownership:** pairwise war membership lives in `active_diplo_keys`, `resolved_diplo_keys`, and `diplo_key_meta`. `objective_keys` are historical WPS objective references only and must never be used as the active pair-key index.
- **Invariant:** a `diplo_key` can appear in at most one active `war_instance` at any time. Creating a new active `war_instance` with a `diplo_key` already present in an active instance is invalid unless the operation explicitly reuses or merges the existing instance.
- **Reuse rule:** if a declaration or cascade involves a pair already present in an active compatible `war_instance`, append any new participants and pair metadata to that existing `war_id` rather than creating a duplicate.
- **Late-join rule:** a new coalition member, ally, bargain entrant, or vassal that joins an already tracked coalition war attaches to that existing `war_id` as participant/pair expansion. It is not a merge unless the entrant or new pair already belongs to a different active compatible `war_instance`.
- **Creation seam:** every path that intends to set a pair to `WAR` and then call `_process_war_cascade()` must call `validate_war_declaration(world, originator, origin_target, *, entry_path, reason)` and `ensure_war_instance_for_pair(...)` before mutating `diplomatic_states`. This includes player/AI declarations, coalition declarations, vassal rebellions, commitment-paradox outcomes, scripted war entry, combat-triggered auto-war, and any future executor path that combines WAR state with cascade. The helper either creates a skeleton instance, reuses a compatible active instance, or returns a hard stop. A `war_instance_side_conflict` must be detected pre-commit; do not set the pair to `WAR` and then discover that the cascade would place a nation on both sides.
- **Merge rule:** merge is transitive. If a declaration or cascade connects multiple active compatible instances, compute the full connected component of `war_instances` linked by the cascade (visiting each active instance at most once; bounded by the count of active instances, typically < 20), validate all side assignments for the merged result simultaneously, and merge into the instance with the oldest `created_sequence`. Preserve the older `created_turn`, union active participants and pair keys, preserve all participant episodes, preserve every WPS objective reference as an independent objective context, and choose leaders using section 7.4. If any side mapping in the connected component would put the same nation on both sides, the triggering declaration/cascade aborts without mutation and returns a player-facing `war_instance_side_conflict` hard stop naming the conflicted nation.
- Merge operations also preserve the surviving instance's `war_id` and older `created_sequence` so the unique `war_id` allocator remains monotonic and archived references stay stable. Any `war_bargain.war_id`, contribution event, pending settlement dialogue, dispatch route, or ledger reference that points to an absorbed instance is rewritten to the surviving `war_id` during the merge transaction.
- After every merge transaction, run `assert_war_instance_invariants(world, *, context="post_merge")` before returning reader-visible state. The assertion verifies: every live `diplomatic_states[diplo_key] == "WAR"` appears in exactly one active `war_instance.active_diplo_keys` with `diplo_key_meta[diplo_key]["pair_status"] == "war"`; no active instance claims a non-`WAR` pair as `pair_status == "war"`; no absorbed `war_id` remains in live `diplomatic_commitments`, `war_contribution_scores`, `pending_settlement_dialogues`, dispatch route payloads, or ledger payloads; and `side_by_nation` matches attacker/defender membership with no nation on both sides. Normal merge paths must fail fast in tests and debug if this assertion fails; explicit load-repair/debug-import tooling may downgrade it to a structured repair report only when that tooling owns the repair.
- **Merge transaction order:** (1) compute the connected component and validate all side assignments without mutating state; (2) choose the surviving oldest `war_id`; (3) merge `participant_meta`, active/resolved pair keys, side lists, and episode records into an in-memory merged shape; (4) choose leaders per section 7.4; (5) rewrite `war_bargain.war_id` references; (6) rewrite `war_contribution_scores` and contribution-event `war_id` references; (7) rewrite pending settlement/dialogue/dispatch/ledger references; (8) atomically replace the survivor record and remove absorbed active instances; (9) mark `war_instances_by_leader` and `war_instances_by_participant` dirty before any reader uses the merged state. Any conflict before step 8 aborts the whole merge. The connected-component visit is bounded by active instance count, not participant count, and must not recursively rebuild indexes during the merge.
- **Merged objective rule:** a merged `war_instance` never chooses one dominant objective. `objective_keys` remains the union of historical WPS diplo-key references from every absorbed instance. Readers resolve objective context from `world.war_objectives[diplo_key][declaring_nation]` when available and must keep the originator, target, objective type, and target regions distinct per original pair. Common-peace `war_objective_alignment` selects the relevant proposer-side objective against the covered enemy being burdened; it must not treat the merged war as having one global purpose.
- **Merged contribution rule:** contribution events and episode records are rewritten to the surviving `war_id`, but standing thresholds are computed from the post-merge current-episode side totals at settlement time. Historical/debug panels may show each absorbed war's pre-merge share, but advisory standing, shut-out grievances, and reward eligibility use the merged denominator after the transaction. This prevents a 30% contributor in a small absorbed war from retaining `seat` standing in a later megawar unless their post-merge material share, power tier, bargain, beneficiary, or direct-stake rules still justify it.
- Merge is not assumed rare for correctness. Full-Europe coalition chains can connect existing wars, so merge support must be tested with connected-component fixtures; it is still not an `advance_turn()` hot path and should only be optimized if profiling proves repeated merges in ordinary play.
- **Direct WAR-entry rule:** every transition into `WAR` must attach to a `war_instance`, even if the path does not call `_process_war_cascade()`. `ensure_war_instance_for_pair(...)` owns declaration/cascade creation; direct join or resumption paths may call a narrower `attach_pair_to_war_instance(...)` / `attach_participant_to_war_instance(...)` helper that reuses or merges the compatible instance and stamps `diplo_key_meta[pair]["pair_status"] = "war"`. Required call sites include player/AI declarations, coalition declarations, vassal rebellions, vassal-release rebellions, commitment-paradox outcomes, scripted war entry, combat-triggered auto-war, `resolve_join_opportunity()`, `accept_counter_bargain()`, and armistice collapse (`ARMISTICE -> WAR`).
- **Historical objective references:** `objective_keys` are references to WPS `war_objectives` diplo keys. Readers must tolerate missing objective records because WPS cleanup may remove concluded objective details after their retention window.

### 7.3 End condition

A `war_instance` ends when no unresolved hostile or suspended pairs remain between the two sides, or when one side has no active participants remaining.

Separate peace removes a nation from the active participant list without ending the whole war.

Pair status is explicit:

- `pair_status = "war"` for pairs currently in `WAR`.
- `pair_status = "armistice"` for pairs in `ARMISTICE`. The pair remains in `active_diplo_keys` and the same `war_id`; it is suspended, not resolved.
- `pair_status = "resolved"` for pairs whose hostile relationship has reached `PEACE` or a less hostile treaty state.

ARMISTICE never archives a `war_instance` by itself. If an armistice collapses back to `WAR`, the pair reuses the same `war_id` and the same active participant episode unless a nation had separately exited and re-entered under section 7.5. If an armistice converts to `PEACE`, move that `diplo_key` from `active_diplo_keys` to `resolved_diplo_keys`, stamp `resolved_turn`, and set `pair_status = "resolved"`. Contribution ticking and staying-power credit pause for a participant only when that participant has no active `WAR` pair left inside the `war_instance`.

When a `war_instance` ends:

- Set `ended_turn = world.current_turn`.
- Set `end_reason = "all_pairs_resolved"` or `"no_active_participants"`.
- Keep the terminal record in `world.war_instances` for 10 turns so contribution, settlement, dispatch, and ledger readers can resolve recent references.
- After the 10-turn retention window, move the record to `world.archived_war_instances` and remove it from active `war_instances`.
- Active-war queries filter on `ended_turn is None`.

### 7.4 War leaders

Common peace uses side leaders, not majority votes:

- The originator is the attacker leader unless a coalition declaration supplies `active_coalition.leader` for the attacker side.
- The origin target is the defender leader unless a coalition declaration supplies `active_coalition.leader` for the defender side.
- `leader_source_by_side[side]` records each side independently. A coalition source on one side never implies coalition scoring for the other side.
- If a leader exits by separate peace or elimination, leadership passes to the active same-side participant with the highest `war_leader_score()`.
- If no eligible replacement exists, that side has no eligible leader. If the side also has no active participants, the `war_instance` ends. Otherwise the settlement is blocked with `no_eligible_leader` until explicit coalition/scripted leadership rules assign one or the war resolves by other legal means.

The opposing leader can accept a package that burdens non-leader allies. This is intentional Napoleonic drama, not a veto gap. The sold-out participant receives a primary enemy-side reaction in §14.6, and severe non-leader burdens feed the Step 4 acceptance penalty.

Settlement confirmation is leader-sensitive. A staged `settlement_confirm` records `proposer_side`, `accepting_side`, and the leaders for both sides at staging time. On `confirm`, re-read the live `war_instance` leaders before any mutation:

- If the proposer-side leader changed, void the staged settlement with `{"success": False, "error": "proposer_leader_changed", "must_reopen": True}`. The player or AI must reopen the settlement so standing, warnings, and terms are rebuilt from live state.
- If the accepting-side leader changed but the proposer-side leader is unchanged, recompute standing, direct-score gates, acceptance components, and warnings against the new accepting leader before resolving.
- If either side has no active leader because the side has no active participants or no eligible leader, reject with `inactive_war_instance` or `no_eligible_leader` and do not mutate state.
- Re-read every covered `diplo_key` and its `diplo_key_meta[pair]["pair_status"]`. If any covered pair is no longer active in the same `war_id`, has moved from `war` / `armistice` to `resolved`, or has changed sides since staging, reject with `active_pair_changed` and do not mutate state. This closes the armistice-expiry race where a staged settlement outlives the pair state it was built from.
- Re-read proposer-side active participants, standing inputs, beneficiary eligibility, and term beneficiaries. If any staged beneficiary or material proposer-side participant exited, rebelled, was eliminated, changed side, or no longer qualifies for the term it receives, reject with `active_participant_changed` or `beneficiary_ineligible`, return `mutated: False`, and reopen the settlement review from live state.

`war_leader_score(nation, war_instance, world)` is settlement-specific:

```python
side_anchor = (
    war_instance["originator"]
    if nation in war_instance["attackers"]
    else war_instance["origin_target"]
)
relation = get_relation(world, side_anchor, nation)  # ordered pair helper / nation_relations lookup
relation_to_side_anchor_bias = 0 if nation == side_anchor else clamp(relation // 10, -5, 5)

war_leader_score =
    power_tier_weight              # major=300, secondary=200, minor=100
    + active_army_strength // 1000
    + relation_to_side_anchor_bias # same-side light tie-break only
```

`active_army_strength` means the nation's active marshal troop strength in the war theater: marshals in any active war pair's contested region, controlled front region, or one-hop adjacent region for that `war_instance`. It is not total national military strength. `relation_to_side_anchor_bias` is intentionally tiny; it must never let a minor outrank a secondary or major by relation alone. The bias must always point at the same-side anchor: `originator` for attackers and `origin_target` for defenders. Defender-side leader replacement must never use the attacker's relation as a tie-break.

Use `coalition_leadership_score()` only for the side whose `leader_source_by_side[side] == "coalition_leader"` and whose active coalition target is the same political conflict. Non-coalition wars and the opposite side in a coalition war must not feed coalition-specific hostility/target assumptions into leader replacement.

If `war_leader_score()` ties, keep the current leader when it is still an eligible same-side active participant; otherwise choose the alphabetically earliest stable nation id. This final tie-break is deterministic and must be part of the A3 leader-replacement tests.

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

Contribution readers must filter event records by the active episode turn range:

```python
joined_turn <= event["turn"] and (
    exited_turn is None or event["turn"] <= exited_turn
)
```

Old-format battle records without `war_id` are attributed only to the first matching episode for that pair and never retroactively split across re-entry episodes.

Late-joiner examples:

- Sweden joins on turn 15, fights decisively at turn 16, and earns `consult` or `seat` through battle/occupation contribution even though its `staying_power` is low.
- A minor joins on turn 18, never fights, and receives only the small `staying_power` earned since entry.

---

### 7.6 Elimination exit

If a mapped nation loses all controlled regions and has no vassals while it is an active participant in a `war_instance`, it exits through elimination:

- A1 does not add a separate absence exemption. Nations absent from the scenario/map are not settlement participants; Britain is treated as a normal mapped participant in the current runtime. Future naval/island reachability rules must be owned by a separate movement/naval spec before they change elimination behavior.
- Remove the nation from `active_participants`.
- Stamp `participant_meta[nation]["exited_turn"] = world.current_turn` and `exit_path = "eliminated"`.
- Close the active episode with the same `exited_turn`.
- Freeze contribution through the elimination turn.
- If the eliminated nation was a side leader, run leader replacement per §7.4.
- Elimination does **not** fire the separate-peace settlement reaction pass. The nation is dead, not cutting a deal.
- If one side has no active participants after elimination, end the `war_instance` per §7.3.

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

Standing is rule-based with numeric thresholds, not a fuzzy formula. Personalities color the reaction, not the bucket. Assign the highest matching level: evaluate `seat`, then `consult`, then `beneficiary_only`, then `no_standing`.

Standing is evaluated in two passes. The draft advisory pass uses the current draft settlement terms; if the player has not drafted terms yet, draft standing excludes `rival_strengthened` and term-specific beneficiary effects. The confirmation pass recomputes standing from the locked `settlement_terms` immediately before `settlement_confirm.confirm`. Confirmation-time standing is authoritative for warnings, relation fallout, gratitude, grievance flags, and acceptance components.

Definitions used by the buckets:

- `material_contribution_points = battle + occupation + support`
- `staying_power` alone can create a low visible participation note, but cannot by itself trigger `seat`, 15% / 25% contribution dispatches, or a major shut-out grievance.
- A `secondary` co-belligerent with any material contribution has at least `consult` standing. This prevents Spain, Sweden, Naples, Denmark, or the Ottoman Empire from vanishing in an 8-participant coalition where contribution shares are naturally diluted.

**`seat`** — any of:
- Active `major` power on the same side
- Active war bargain whose named enemy or claim region is directly involved in a term being decided
- Own capital, survival, or core territory being decided
- Material contribution share >= 25% and `material_contribution_points > 0`

**`consult`** — any of:
- Material contribution share >= 10% and `material_contribution_points > 0`
- `secondary` power with any material contribution
- Region claim or territorial interest directly affected by a term
- Treaty ally (ALLIANCE / DEFENSIVE_ALLIANCE) materially involved in the war
- `rival_strengthened` applies for a `major` or `secondary` power: a settlement transfers territory or alignment control to a rival / opposing-bloc nation adjacent to this nation or inside its local sphere. For `minor` powers, `rival_strengthened` alone surfaces an INFO warning but does not promote to `consult` unless `material_contribution_points > 0`.

**`beneficiary_only`** — any of:
- `minor` / vassal / liberated state receiving or losing a direct outcome
- Low contribution but a specific term names them as beneficiary or target
- Active same-side participant with `material_contribution_points > 0` that does not meet `consult` thresholds

**`no_standing`** — none of the above apply.

**Vassal and forced-origin clause:** Vassal auto-joins (nations entering via cascade because they are vassals of the war leader) receive at most `beneficiary_only` standing unless they independently meet material-contribution thresholds for `consult` or `seat`. Forced-alliance co-belligerents (nations with `forced_origin=True` on their alliance) share the same standing rules as voluntary allies — they are genuine co-belligerents, not subordinates. Vassal contribution counts independently in the side total and is never folded into the lord's share.

### 8.3 Standing inputs

Standing is computed from:

1. **Material contribution share** — `material_contribution_points / total_side_material_contribution`, using battle + occupation + support only. Seat/consult thresholds use this share so staying-power padding cannot dilute a material contributor below standing.
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
    "current_episode_id": "France_12_1",
    "episodes": {
        "France_12_1": {
            "joined_turn": int,
            "exited_turn": int | None,
            "battle": int,
            "occupation": int,
            "staying_power": int,
            "support": int,
            "total": int,
        }
    },
    "historical_total": int,
}
```

Side-local score. Normalized into percentage shares at settlement time:

```python
total_contribution_share[nation] = current_episode_total(nation) / total_side_current_episode_contribution
material_contribution_share[nation] = current_episode_material_total(nation) / total_side_material_contribution
standing_share[nation] = material_contribution_share[nation]
```

If `total_side_current_episode_contribution <= 0`, first apply absolute standing rules from §8.2: active `major` powers still receive `seat`, active bargain/direct-survival/direct-core stakes still receive their normal standing, and direct beneficiaries receive at least `beneficiary_only`. After those overrides, the leader receives `seat` and all other participants resolve to `no_standing`.

If `total_side_current_episode_contribution > 0` but `total_side_material_contribution <= 0`, every `material_contribution_share` defaults to `0`. Total contribution remains available for history and staying-power display, but contribution standing, threshold dispatches, and material shut-out grievances fall through to non-contribution rules rather than dividing by zero.

Settlement standing uses the active episode only. Historical panels may show `historical_total`, but settlement expectations and shut-out reactions must not credit earlier episodes after a nation exited and re-entered the same war. On re-entry, create a new `episode_id` instead of overwriting the old episode. Contribution readers filter battle, occupation, support, and staying-power events by the episode turn range: `joined_turn <= event.turn` and `(exited_turn is None or event.turn <= exited_turn)`.

Contribution episode ids are canonical: `episode_id = "{nation_slug}_{war_sequence}_{episode_index}"`, where `war_sequence` is the surviving `war_instance.created_sequence` and `episode_index` starts at `1` for that nation in that war. The `exited_turn` boundary is inclusive because same-turn settlement, elimination, and separate-peace events must still read the final active-turn contribution.

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

# If per-nation casualty exposure is available from the battle result, use
# risk_adjusted_theater_strength in place of raw theater strength. This rewards
# nations that actually absorbed losses and prevents safe rear-area mass from
# farming full battle credit.
risk_adjusted_theater_strength[nation] =
    nation_theater_strength[nation] *
    (1 + min(0.5, casualties_suffered_by_nation[nation] / max(1, pre_battle_strength[nation])))

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

The Slice B v1 baseline does not require a per-nation casualty map. If `casualties_suffered_by_nation` / `pre_battle_strength` is absent, use raw `nation_theater_strength` exactly as recorded at battle time. Adding per-nation casualty exposure later is a compatibility extension, not a prerequisite for settlement contribution.

If `side_theater_strength <= 0`, the battle awards no contribution points and emits a debug warning; do not divide by zero or fall back to all participants. If an otherwise valid detected participant has `nation_theater_strength <= 0`, use a floor of `1` for that participant before risk adjustment so routed or adjacent political participants are not silently dropped.

Occupation contribution is attributed by event, not by side total guesswork. Controller-change, liberation, and capital-capture paths emit:

```python
{
    "type": "war_occupation_event",
    "war_id": "war_12",
    "actor_nation": "France",
    "side": "attackers",
    "region": "Saxony",
    "from_controller": "Austria",
    "to_controller": "France",
    "occupation_kind": "enemy_region_captured",  # enemy_region_captured | enemy_capital_captured | allied_region_restored | liberated_region_restored | treaty_transfer
    "turn": 18,
    "episode_id": "occupation-18-4",
}
```

Per-nation `occupation_raw[nation]` is the sum of that nation's active-episode occupation events: `20` for `enemy_region_captured`, `40` for `enemy_capital_captured`, and `15` for `allied_region_restored` or `liberated_region_restored`. `treaty_transfer` events are ignored for contribution unless a future settlement-followup explicitly marks them as wartime occupation credit.

Normalize each bucket against the side total for that bucket, multiply by the bucket weight, and store integer points:

```python
if side_bucket_raw <= 0:
    bucket_points[nation] = 0
else:
    bucket_points[nation] = round((nation_bucket_raw / side_bucket_raw) * bucket_weight)
```

If a side bucket has zero raw contribution, it awards zero points and its unused weight is not redistributed. Support counts only when an actual support event exists; Britain or another paymaster receives support contribution for real gold / subsidy / AP / manpower support, while `major` auto-seat prevents a major war funder from disappearing when a war has no recorded support events.

Standing thresholds use `material_contribution_share`, not total contribution share. `staying_power` remains visible in total contribution displays and history panels, but it cannot dilute or inflate the battle/occupation/support denominator that decides `seat`, `consult`, threshold dispatches, or major shut-out grievance eligibility.

Rounding note: bucket normalization uses `round()`. Bucket point sums may land one point below or above the nominal bucket weight in evenly split cases; final contribution shares are derived from stored totals, so this is acceptable and deterministic.

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
    "source": "treaty_clause",  # treaty_clause | coalition_subsidy | command | scripted_ai | settlement_followup
    "episode_id": "support-18-3",
}
```

Emission hooks are event-driven only: treaty-clause ratification, per-turn treaty-clause processing, explicit support commands, scripted AI support, and any future settlement follow-up that transfers support. Ownership follows the natural emitter: coalition subsidy emission is owned by `backend/game_logic/coalition.py` advance-turn processing; one-time treaty-clause gold / AP / manpower transfer emission is owned by `WorldState._ratify_treaty()` in `backend/models/world_state.py`; recurring `gold_per_turn`, `ap_per_turn`, and future recurring support clauses emit from `WorldState._process_treaty_clauses()` as each payment is actually applied; explicit support-command emission is owned by the command executor that applies the support. Existing British coalition subsidy delivery must emit one `war_support_delivered` event per turn per recipient with `source: "coalition_subsidy"`. Treaty-clause support events use `source: "treaty_clause"` and a source detail such as `ratification`, `gold_per_turn`, or `ap_per_turn`. Contribution readers dedupe by `episode_id` and ignore support where either side is not an active same-side participant in `war_id` on that turn. Access/supply support uses `value = 1` per qualifying turn and is capped at `5` raw support points per `(war_id, supporter, support_kind)` across the whole war instance. Re-entry into the same `war_id` does not reset this cap.

British coalition subsidy war attribution is deterministic because `_process_british_subsidy()` currently has no `war_id` argument and may choose a recipient who is active in more than one war. If the recipient has exactly one active `war_instance` where Britain is a same-side supporter or coalition backer, emit that `war_id`. If multiple active wars qualify, choose the active coalition war with the same target first, then the war with the highest overlap between active coalition members and `war_instance.active_participants`, then oldest `created_sequence`. If no unique or ranked eligible war exists, emit an unattributed support event with `war_id = None` / `source_detail = "unattributed_subsidy"` for logging only; it must not add contribution until a later event can be tied to a single war.

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

Contribution from battles is accrued at battle-resolution time into `war_contribution_scores`. Settlement readers must not reconstruct historical contribution by scanning old `world.battle_records`; those raw records may still be pruned by existing war-score cleanup. The extended battle record is the emission payload for accrual and for recent/debug display, not the canonical long-term contribution store.

The existing war-score battle writer ignores battles below `1000` total casualties. Settlement contribution must not inherit that filter. When a battle has valid `war_id`, side, and theater-participant data, emit and accrue the battle-contribution event before the war-score casualty gate returns. Sub-1000-casualty battles still add zero pairwise war-score battle component, but they can add settlement contribution using the same `battle_raw` formula. If a future implementation deliberately chooses to make skirmishes worth zero contribution, that must be a named balance constant and tested for minor-power wars; do not let the existing war-score gate silently decide it.

Participant detection:

- A nation participates if it has an active marshal in the battle region or in any one-hop adjacent region during the turn of the battle.
- If a full-Europe map provides `campaign_theater_id` / front grouping metadata, the battle writer must include it and credit active same-side participants with marshals in that same theater during the turn. This is an extension of theater attribution, not a whole-war credit rule.
- Only active participants in the same `war_instance` side can be credited.
- Event readers filter by the participant's active episode turn range per §7.5.
- Credit is divided by `nation_theater_strength` among detected participants on that side.
- Casualties still matter to the existing pairwise war-score record, but settlement contribution reads theater strength and battle result, not a new per-nation casualty map.
- This deliberately captures the Blucher-at-Waterloo pattern: an adjacent allied army can matter politically even when combat resolution treated the battle as one attacker and one defender.

The one-hop rule is the Slice B baseline. It must not silently erase coalition effort in a 100+ region map. A synthetic 6-participant / 3-theater fixture must prove that nations fighting on separate fronts gain contribution through their own battle, occupation, or support events even when they are not credited on an unrelated front. Do not credit all same-side participants across the whole war just because a battle occurred somewhere in the `war_instance`.

Without this theater record, any contribution system will mis-credit coalition battles at full-Europe scale. The canonical long-term battle-record writer is `backend/game_logic/diplomacy.py::record_battle()`; `backend/commands/combat_executor.py` field, garrison, charge, and future battle-resolution paths must pass the theater fields into that writer. `WorldState.record_battle()` is only the transient `battles_this_turn` signal path for same-turn UI/effects and is not the canonical contribution or war-score writer. Readers still need adapters for old records.

### 9.5 Contribution accrual performance contract

Contribution must comply with the project hot-path rule:

- Battle contribution accrues event-driven at battle resolution time.
- Occupation contribution accrues event-driven at region-controller change / treaty-transfer time.
- Staying power is the only per-turn accrual; it iterates active participants in `war_instances`, not all regions.
- Region ownership lookups use existing cached helpers such as `get_nation_regions()` where needed. Do not add per-region scans to `advance_turn()`.
- Any repeated leader-scoped lookup in a turn, such as AI common-peace proposal search or war-status grouping, must build a per-turn `war_instances_by_leader` / side-leader index instead of filtering all active instances repeatedly. Invalidate this index with the same war-state mutation paths that invalidate `war_instance` readers.
- Cross-war reaction lookups must use a per-turn `war_instances_by_participant` index keyed by active participant. Build it from active `war_instances`, not from all nations or all regions, and invalidate it whenever participants, leaders, pair status, or archive/end state changes.
- Common-peace ratification is a sub-transaction for cache timing: after it mutates participants, leaders, pair status, or archive/end state, invalidate or rebuild `war_instances_by_leader` and `war_instances_by_participant` before any cross-war reaction reader runs.
- Same-turn episode filtering depends on event resolution order: battle, occupation, and support events for the turn must be emitted before elimination, separate-peace, or settlement exits stamp `exited_turn`. The inclusive `event.turn <= exited_turn` boundary in section 7.5 is correct only under that ordering.

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
    5 * recently_exited_same_side_enemies,
    15,
)
```

This is a positive acceptance modifier for France's next peace preview against remaining enemies on that side. It counts same-side enemy participants that made separate peace in the last 3 turns, is shown in acceptance components, and represents coalition confidence collapsing after a partner defects. It supplements, but does not replace, recalculated military war score.

Store `separate_peaced` as records, not bare nation names:

```python
{
    "nation": "Prussia",
    "side": "defenders",
    "exited_turn": 18,
    "peace_type": "separate_peace",
    "original_side_size": 4,
}
```

### 10.2 Common peace

A new war-scoped settlement mode. One package keyed to `war_instance`, not a sequence of bilateral deals.

Internally, terms are grouped by payer / target enemy:

- Terms imposed on Austria
- Terms imposed on Prussia
- Beneficiaries on the proposer side
- Side-wide political aftermath

If the settlement actor wants to resolve only Austria while the larger war continues and no ally-beneficiary / standing logic is needed, that is separate peace. Common peace may target a single covered enemy when the package includes ally-beneficiary terms, settlement standing evaluation, or war-level bargain/legitimacy logic. The distinction is not enemy count; it is whether war-scoped settlement machinery is required.

Common peace always resolves covered hostile pairs to `PEACE` or a less hostile treaty state produced by the ratified terms. It never creates `ARMISTICE`. Use the existing bilateral/separate-peace flow for armistice proposals so suspended-pair lifecycle remains owned by section 7.3 and the existing armistice rules.

### 10.3 Wizard routing

Keep the existing bilateral wizard for separate peace, armistice, and bilateral deals.

When allied participation matters, route into a dedicated settlement flow:

- Entry choice: **Separate peace** vs **Open settlement**
- Separate peace stays in the existing bilateral wizard, but now shows ally-fallout and bargain-breach warnings before send
- Open settlement launches a war-scoped flow keyed to `war_id`

**Open Settlement eligibility / grey-out rules:**

The **Open settlement** option is enabled only when all are true:

- `war_id` resolves to an active `war_instance` with `ended_turn is None`.
- The settlement actor is the current side leader for one side of that `war_instance`.
- The `war_instance` has at least one active unresolved pair between the two sides with `pair_status in {"war", "armistice"}`.
- At least one enemy participant is coverable: the opposing side leader, a participant named by a draft term, a participant needed for an active objective or bargain, or a participant with an active direct pair against the proposer side.
- No other active `settlement_confirm` or `incoming_settlement_offer` dialogue is currently blocking settlement review.

Grey-out / preview error reasons are deterministic: `inactive_war_instance`, `not_side_leader`, `no_unresolved_hostile_pairs`, `no_coverable_enemy`, or `settlement_dialogue_active`. A non-leader may still open read-only war status / contribution rows, but cannot stage common-peace terms.

### 10.4 Endpoint and dialogue contract

Open Settlement is a war-scoped flow, not a hidden variant of `propose peace`.

Preview endpoint extension:

```http
GET /diplomatic_preview?mode=settlement&war_id={war_id}
```

`GET` returns the initial, no-terms war-scoped advisory shell. Draft terms require a non-mutating request body so territory legitimacy, projected hegemony, standing, and acceptance diagnostics can be calculated from the proposed package:

```http
POST /diplomatic_preview
{
    "mode": "settlement",
    "war_id": "war_12",
    "proposer_side": "attackers",
    "settlement_terms": [
        {"type": "territory_cede", "from": "Austria", "to": "Prussia",
         "beneficiary": "Prussia", "regions": ["Saxony"], "war_id": "war_12"}
    ]
}
```

`POST /diplomatic_preview` is preview-only. It must never stage `settlement_confirm`, mutate terms, change ownership, or run WB-B fulfillment/breach.

Preview response minimum shape:

```python
{
    "mode": "settlement",
    "war_id": "war_12",
    "settlement_preview": {
        "war_instance": {...},
        "covered_enemy_participants": ["Austria", "Prussia"],
        "proposer_side": "attackers",
        "proposer_side_participants": ["France", "Saxony"],
        "standing": {"Saxony": {"level": "consult", "contribution_share": 0.18}},
        "active_bargains": [],
        "side_pressure_score": 42,
        "direct_scores": {"Austria": 48, "Prussia": 12},
        "warnings": [],
        "advisory_rows": [],
        "overflow_participants": [],
    },
}
```

Preview errors use structured response shapes:

```python
{"success": False, "error": "invalid_war_id" | "inactive_war_instance" | "not_side_leader", "war_id": "war_12"}
```

Command / confirmation contract:

```python
POST /command
{
    "command": "open settlement war_12",
    "settlement_terms": [
        {"type": "territory_cede", "from": "Austria", "to": "Prussia",
         "beneficiary": "Prussia", "regions": ["Saxony"], "war_id": "war_12"}
    ],
}
```

Mutating common peace commands must not ratify directly from `/command`. They create a mandatory `settlement_confirm` dialogue unless a hard stop rejects the package first.

`settlement_confirm` is a `DialogueManager.HARD_STOP` type. It blocks ordinary commands until the player confirms, backs out, revises terms, or the staged settlement is voided by live-state revalidation. The backend stores the internal dialogue key as `type: "settlement_confirm"` and may mirror it to API responses as `dialogue_type: "settlement_confirm"` for existing client conventions.

`settlement_confirm` minimum shape:

```python
{
    "type": "settlement_confirm",
    "dialogue_type": "settlement_confirm",
    "war_id": "war_12",
    "proposer_side": "attackers",
    "accepting_side": "defenders",
    "staged_leaders": {"attackers": "France", "defenders": "Austria"},
    "staged_turn": 24,
    "settlement_terms": [...],
    "settlement_preview": {...},
    "acceptance_components": {...},
    "warnings": [],
    "hard_stops": [],
    "actions": ["confirm", "back_out", "revise_terms"],
}
```

Incoming AI common-peace offers use a distinct current-turn offer dialogue before ratification. `incoming_settlement_offer` is a `DialogueManager.CURRENT_TURN_OFFER_TYPES` dialogue, browseable through the mailbox like other incoming proposals, not a `HARD_STOP`. It must have its own dialogue priority at the normal incoming-proposal tier and its own mailbox summary label, not the default fallback label. While one is active, Open Settlement eligibility returns `settlement_dialogue_active` for the same player/war. Accepting it stages a `settlement_confirm` hard stop from the locked offer payload and then the normal `settlement_confirm.confirm` action performs live revalidation and mutation.

```python
{
    "type": "incoming_settlement_offer",
    "dialogue_type": "incoming_settlement_offer",
    "war_id": "war_12",
    "offer_origin": "ai",
    "offering_side": "defenders",
    "receiving_side": "attackers",
    "staged_leaders": {"attackers": "France", "defenders": "Austria"},
    "settlement_terms": [...],
    "settlement_preview": {...},
    "acceptance_components": {...},
    "warnings": [],
    "actions": ["accept", "reject", "request_revision"],
}
```

Incoming offer responses:

```python
# Accept: promote into the same settlement_confirm hard stop; no treaty mutation yet.
{"success": True, "dialogue_type": "incoming_settlement_offer", "action": "accept",
 "promoted_to": "settlement_confirm", "dialogue_id": "settlement_war_12_turn_24",
 "mutated": False}

# Rejected by live-state validation / acceptance recheck; no mutation.
{"success": False, "dialogue_type": "incoming_settlement_offer", "action": "accept",
 "error": "proposer_leader_changed" | "inactive_war_instance" | "active_pair_changed" | "no_covered_enemy_participants",
 "must_reopen": True, "mutated": False}

# Reject.
{"success": True, "dialogue_type": "incoming_settlement_offer", "action": "reject",
 "cancelled": True, "mutated": False}

# Request revision.
{"success": True, "dialogue_type": "incoming_settlement_offer", "action": "request_revision",
 "revision_requested": True, "mutated": False}
```

`incoming_settlement_offer.accept` must only validate that the offer can still be promoted and must not ratify directly from the offer payload. The promoted `settlement_confirm.confirm` call uses the same live-state revalidation and mutation executor as player-staged common peace.

Dialogue action request contract:

```http
POST /respond_to_diplomatic_dialogue
{
    "dialogue_type": "settlement_confirm",
    "action": "confirm",  # confirm | back_out | revise_terms
    "war_id": "war_12",
    "dialogue_id": "settlement_war_12_turn_24"  # optional if the active dialogue is already settlement_confirm
}
```

Dialogue action response shapes:

```python
# Confirm accepted and ratified.
{"success": True, "dialogue_type": "settlement_confirm", "action": "confirm",
 "settlement_summary": {...}, "mutated": True}

# Confirm rejected by acceptance formula; no mutation.
{"success": False, "dialogue_type": "settlement_confirm", "action": "confirm",
 "rejected": True, "feedback": [...], "mutated": False}

# Live-state void; no mutation, settlement must be reopened.
{"success": False, "dialogue_type": "settlement_confirm", "action": "confirm",
 "error": "proposer_leader_changed" | "inactive_war_instance" | "active_pair_changed",
 "must_reopen": True, "mutated": False}

# Back out.
{"success": True, "dialogue_type": "settlement_confirm", "action": "back_out",
 "cancelled": True, "mutated": False}

# Revise terms; returns the prior draft context for the settlement review surface.
{"success": True, "dialogue_type": "settlement_confirm", "action": "revise_terms",
 "reopen_review": True, "settlement_terms": [...], "settlement_preview": {...}, "mutated": False}
```

Player actions:

- `confirm`: revalidates current leaders, active pair keys, hard stops, and acceptance components against live state. If the proposer-side leader changed, the staged settlement is voided and must be reopened. If only the accepting-side leader changed, recompute acceptance against the new leader before resolving. On success, ratifies and returns `{"success": True, "settlement_summary": {...}}`. On rejection, returns `{"success": False, "rejected": True, "feedback": [...]}` without mutating state.
- `back_out`: closes the dialogue and returns `{"success": True, "cancelled": True}` with no state mutation.
- `revise_terms`: returns to the settlement review surface with the prior `settlement_terms`, warnings, and acceptance diagnostics intact.

Godot surface:

- Reuse the diplomacy wizard shell for the entry choice.
- Render the war-scoped advisory in a dedicated settlement review panel. This is an information-screen surface in the CanvasLayer 50 family, so opening it must close or hide existing layer-50 screens (`diplomatic_ledger`, `strategic_ledger`, `dispatch_view`, `campaign_log`, and `marshal_management`) through the same one-screen-at-a-time top-bar ownership rule. The final confirm/back-out/revise choice is promoted through the existing popup/dialog manager when `settlement_confirm` is active.
- Warning payloads use the existing structured `warnings[]` shape. `HARD_STOP` blocks confirmation; `WARNING` and `INFO` do not.

### 10.5 Partial common peace and continuation

Common peace does not have to resolve every enemy in the `war_instance`. The proposed package covers a subset of enemy participants: the opposing side leader plus any non-leader enemies named, burdened, restored, or needed for an objective/bargain term. Every covered enemy must pass the direct-score gate in section 6.3.

If a package is accepted, resolve every `active_diplo_keys` pair where one nation is an active proposer-side participant and the other nation is a covered enemy participant. Enemy participants that are not covered, or that fail the direct-score gate and are removed from the draft package, retain every existing `WAR` or `ARMISTICE` pair against the proposer side in the same `war_instance`. The `war_instance` ends only when section 7.3 is true: no hostile pairs remain between the two sides or one side has no active participants.

Standing controls consultation, advisory salience, reward eligibility, and grievance reactions; it does not by itself keep a covered pair at war. If a `no_standing` participant is on a side whose covered hostile pairs are resolved by the accepted package, that participant receives no terms or advisory row by default, but its covered pair statuses still transition with the settlement.

Common-peace ratification must apply pair-specific treaty outcomes through the same state-transition and treaty-ratification helpers as bilateral peace. Do not implement common peace as a generic loop that sets every covered pair to `PEACE`. A covered enemy with a `forced_alliance` term resolves to the same post-WPS `ALLIANCE` / forced-origin state as the bilateral forced-alliance path; a covered enemy with only territorial/gold/manpower concessions resolves to `PEACE` unless another legal treaty state is explicitly produced by the package. If one package contains `territory_cede` and `forced_alliance` against the same enemy, territory and ownership mutate under the treaty terms and the pair's final diplomatic state is the forced-alliance result, not a subsequent downgrade back to `PEACE`.

An ARMISTICE pair in `active_diplo_keys` may be covered by common peace. If covered and accepted, that suspended pair resolves directly to `PEACE` or the treaty state produced by the package, clears armistice tracking/cooldown as the existing peace path does, and moves to `resolved_diplo_keys`. Uncovered ARMISTICE pairs remain suspended in the same `war_id`.

If the player wants to settle one enemy and the package has no ally-beneficiary, standing, objective, or bargain reason to use war-scoped settlement machinery, use separate peace instead. Partial common peace exists for cases where a subset settlement still needs ally standing, common-peace acceptance, beneficiary terms, or WB settlement evaluation.

---

## 11. Mechanical Flow

No peace-conference turns. No EU4/HOI4 bidding. Peace is a decisive settlement-actor action with visible consequences; in the current player campaign that actor is usually France.

The flow is parameterized by `settlement_actor`, `proposer_side`, and `accepting_side`, not hardcoded to attackers. In the current player campaign `settlement_actor` is usually France, but scoring and validation read `proposer_side_participants` from the live `war_instance`. When France is defender leader, the proposer side is the defending side and `covered_enemy_participants` means attacker-side nations.

### Step 1: Player opens peace

- From the diplomacy wizard or war status panel, the player chooses **Separate peace** or **Open settlement**.
- Separate peace routes to the existing bilateral wizard (with new ally-fallout warnings).
- Open settlement enters the war-scoped settlement flow.

### Step 2: Talleyrand advisory preview

The system computes draft standing (§8) from the current draft terms and generates structured warnings:

- Standing level per ally (seat / consult / beneficiary_only; `no_standing` is computed internally and omitted from the default advisory)
- Active war bargains and their status (fulfillable / at risk / impossible)
- Contribution shares and what each ally expects
- Territory legitimacy warnings (§12) for each demand
- Rival-strengthened / local balance warnings where a term strengthens a rival on another nation's border
- Hegemony impact preview

The advisory uses the same deterministic salience filtering pattern as DG-2 ledger scale work: show the top 3-5 allies by standing, contribution, bargain stake, territorial stake, and warning severity; group overflow behind "View all participants." The full list remains available, but the default preview must never become an 8-card wall in large coalition wars. WARNING and HARD_STOP concerns always surface above the capped standing list regardless of row count; the cap applies to standing/contribution summaries, not to critical warnings.

`rank_diplomatic_salience(row)` is deterministic. Sort by this tuple, descending unless noted: warning severity (`HARD_STOP`, `WARNING`, `INFO`, none), standing rank (`seat`, `consult`, `beneficiary_only`, `no_standing`), material contribution points, contribution share, active bargain stake, direct territorial/survival stake, `rival_strengthened`, power tier (`major`, `secondary`, `minor`), then ascending stable nation id/name as the final tie-break.

Example warnings:
- *"Prussia contributed 31% and expects consideration over Saxony."*
- *"The bargain with Prussia over Hanover is fulfillable only if France secures the French claim."*
- *"Austria will view exclusion from Bohemia as deliberate humiliation."*
- *"Demanding unoccupied Rhineland without meaningful pressure against Prussia carries severe acceptance cost."*

### Step 3: Player finalizes terms

- One package. Terms grouped by target enemy.
- Player can include ally beneficiary terms (§13).
- No ally turns. The settlement actor decides; allies react.
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
    + projected_hegemony_mod            # where relevant
    + war_exhaustion                    # from existing coalition system
    + abandoned_by_ally_acceptance_mod   # if recent same-side enemies defected
```

Constants and clamps:

| Component | Range / clamp | Formula |
|-----------|---------------|---------|
| `base_side_pressure` | `[-50, 60]` | `round(side_pressure_score * 0.65)` using section 6.3, clamped after rounding. This is the initial Slice C lock, not a fallback knob. |
| `settlement_tier_legitimacy` | `[-20, 15]` | `+15 total_victory`, `+10 harsh_peace`, `+5 dictated_terms`, `0 favorable_terms`, `-10 white_peace`, then subtract `10` if package harshness exceeds the tier's maximum. For white peace, any non-trivial term exceeds the tier maximum; a zero-term white peace receives only the `-10` base. |
| `term_harshness_penalty` | `[-45, 0]` | `-min(45, round((min(raw_total_harshness, 1.5) / 1.5) * 45))`; `raw_total_harshness` is the unclamped treaty-harshness sum using the existing clause weights in `backend/game_logic/diplomatic_templates.py`. Do not call the current 1.0-clamped `calculate_treaty_harshness()` return directly. Slice C must add `calculate_raw_treaty_harshness(treaty)` or extend that helper with an explicit raw / `clamp_max=1.5` option while preserving existing bilateral callers' 1.0-clamped behavior. |
| `burdened_participant_penalty` | `[-60, 0]` | Sum the per-burdened-enemy penalties below, capped at `-30 * min(burdened_count, 2)` and never below `-60` |
| `leader_own_losses` | `[-25, 5]` | Acceptance is scored from the accepting leader's perspective: `-5` per accepting-leader-controlled region ceded, `-15` if the accepting leader's settlement home capital is ceded/forced-aligned, `+5` if the accepting leader keeps all owned territory and had at least one controlled region at settlement evaluation. A leader with no controlled regions at evaluation receives `0` for the "keeps all owned territory" bonus. Sum sub-components first, then clamp the final `leader_own_losses` component to `[-25, 5]`. `get_settlement_home_capital(nation)` returns the current configured mapped capital/home region when present; if it returns `None`, skip the capital-loss subcomponent rather than crashing or inferring separate nation status. |
| `war_objective_alignment` | `[-20, 15]` | `+15` if the package satisfies the proposer-side primary objective, `+5` if it partially satisfies it, `-15` if unrelated harsh terms dominate, `-20` if it contradicts the declared objective |
| `projected_hegemony_mod` | `[-20, 10]` | New common-peace-only component from `project_balance_after_settlement()`, distinct from live bilateral `hegemony_target_mod`: `-20` if package crosses or deepens a `60%` bloc-share band, `-10` at `50%`, `-5` at `33%`, `+10` for meaningful de-escalation |
| `war_exhaustion` | `[0, 20]` | `min(20, enemy_leader_war_exhaustion // 3)`; this component intentionally uses floor division while the other common-peace components use `round()` at their component boundary. War exhaustion is intentionally per-nation and cumulative across simultaneous wars in v0.1, matching the existing coalition system. |
| `abandoned_by_ally_acceptance_mod` | `[0, 15]` | `+5` per same-side enemy participant that made separate peace in the last 3 turns, capped at `+15` |

The burdened-participant penalty applies only to non-leader covered enemies. The accepting leader's own territorial and capital losses are represented by `leader_own_losses`, side pressure, tier legitimacy, war-objective alignment, and war exhaustion; do not double-charge the leader as a burdened participant.

Compute `burdened_participant_penalty` explicitly:

```python
penalty = 0
for enemy in burdened_non_leader_enemies:
    score = direct_score(enemy)
    if score < 0:
        penalty -= 30
    elif score < 20:
        penalty -= 15
    if world.get_power_tier(enemy) == "major":
        penalty -= 10
cap = -30 * min(len(burdened_non_leader_enemies), 2)
burdened_participant_penalty = max(penalty, cap, -60)
```

Acceptance thresholds:

- `score >= 50`: accept.
- `35 <= score < 50`: reject, but feedback marks the package "near acceptable" and names the top two fixable components.
- `score < 35`: hard reject.

Worked acceptance example, Pressburg-style:

| Component | Value | Rationale |
|-----------|-------|-----------|
| `base_side_pressure` | `+46` | `side_pressure_score = 70`, scale `0.65` |
| `settlement_tier_legitimacy` | `+10` | `harsh_peace` package within tier ceiling |
| `term_harshness_penalty` | `-11` | `raw_total_harshness = 0.36`, normalized over the `1.5` common-peace ceiling and rounded at component boundary |
| `burdened_participant_penalty` | `0` | Austria is the accepting leader; no non-leader enemy is sold out |
| `leader_own_losses` | `-10` | Two accepting-leader regions ceded; capital retained |
| `war_objective_alignment` | `+15` | Package satisfies France's primary objective |
| `projected_hegemony_mod` | `-5` | Settlement crosses or deepens only the `33%` projected band |
| `war_exhaustion` | `+13` | Austrian war exhaustion `40`, integer division by `3` |
| `abandoned_by_ally_acceptance_mod` | `0` | No recent same-side enemy separate peace |
| **Total** | **58** | Acceptable; debug output still names harshness, leader losses, and projected hegemony as material costs |

This example is a fixture seed, not a desired final balance target. The Slice C tuning gate below must prove at least one decisive French victory accepts meaningful terms without requiring `total_victory`.

Slice C tuning gate is mandatory: before locking constants in code, add at least eleven deterministic test fixtures: Pressburg-style accepting-leader losses, Tilsit-style non-leader burden, a coalition split by separate peace, decisive French victory without `total_victory`, total-victory harsh terms, minor-power limited common peace, mixed-strength partial-vs-full coverage, narrow-vs-full-vs-serial common-peace incentive comparison, a heavily tilted 6+ participant coalition war, Britain-led defense using current mapped holdings, and mapped-home/capital-loss cases with holdings lost/kept/restored. The Britain fixtures must include the live-code current-map home condition where `NATION_CAPITALS["Britain"] == "Netherlands"` and prove that settlement code treats it as the configured current-map home region, not as a separate settlement identity. Add a monotonicity test proving acceptance does not become worse as `side_pressure_score` increases with all other components held constant. At least one decisive French win must accept meaningful common-peace terms without requiring total victory, and at least one total-victory package with harsh but legal terms must not be reduced to a hopeless score by stacked downside modifiers alone. Add a full-Europe harshness calibration fixture that runs `territory_demand_cost` and `term_harshness_penalty` against historically plausible 5-8 region packages so large-map settlements are not rejected by raw region count alone. Add a multi-forced-alliance fixture that projects `+30` or more threat, surfaces crossed coalition thresholds in preview, and still routes final threat through the existing `add_threat(..., "forced_alliance")` seams on confirmation. Add an AI-defender fixture where the AI side's WPS objective is only `defense` and `war_objective_alignment <= +5`, proving that pressure, exhaustion, and leader-loss components can still produce a reasonable common-peace package when appropriate. The backend debug/preview component output must expose every common-peace acceptance component used by these fixtures, including `base_side_pressure`, `term_harshness_penalty`, `leader_own_losses`, `burdened_participant_penalty`, `projected_hegemony_mod`, `war_exhaustion`, and `abandoned_by_ally_acceptance_mod`.

Final gate coverage must also include a cross-war reaction fixture where more than three directly affected active wars fire in the same settlement pass, plus a full-pipeline stress fixture with two AI-generated settlements, 20 active wars, and all 13 canonical DG-1 nations in one `advance_turn()` evaluation.

Cross-formula validation is part of the Slice C gate. Focused tests must compare `calculate_acceptance()`, `compute_war_entry_score()`, and common-peace acceptance for monotonic military pressure: increasing relevant war score / side pressure must not make any of the three formulas worse when all non-military components are fixed. A package that is accepted as a bilateral peace must not be rejected as an equivalent one-covered-enemy common peace unless the debug output names a common-peace-only component such as projected hegemony, burdened non-leader cost, or ally standing fallout.

If the examples fail those design targets, tune in an explicit escalation order and adjust only one primary knob per test run before implementation lock. Start from the `0.65` scale and `1.5` harshness ceiling above. First move `base_side_pressure` by `0.05` and rerun the decisive-victory, total-victory harsh-terms, mixed-strength partial-vs-full, narrow/full/serial, and full-Europe harshness fixtures. If common peace is still mechanically dominated by serial settlement after military pressure is calibrated, lower the common-peace accept threshold from `50` to `40` and document the matching near-acceptable band in tests. If only total-victory packages fail because projected hegemony overwhelms legal victory terms, halve the `projected_hegemony_mod` penalty for `total_victory` only. If decisive military wins still fail without weakening the anti-farming fixtures, add a bounded `military_supremacy_bonus`. Do not add a `common_peace_coverage_bonus` unless the narrow/full/serial fixture proves breadth itself remains under-rewarded after the military-pressure and threshold knobs; if added, it must be `+3` per additional covered enemy beyond the first, capped at `+12`, and it must pass the mixed-strength partial-vs-full anti-farming fixture. Record the chosen knob in the Slice C tests, implementation notes, `SYSTEMS_REFERENCE.md` when a persistent constant or threshold changes, and acceptance debug output.

War-objective alignment uses the proposer-side objective context relevant to the covered enemy being settled. If there is no live objective record, score this component as `0` rather than guessing from terms. If multiple proposer-side objectives are live after a merge, do not collapse them. Select objectives in this order: side leader's objective against the accepting leader or covered enemy named by the harshest term, then objectives against other covered enemies in term order, then WPS priority order (`subjugation`, `forced_alliance`, `conquest`, `liberation`, `defense`), then oldest `created_turn`. Term-specific advisory warnings may evaluate multiple objective contexts, but the package-level `war_objective_alignment` debug row must name the selected `diplo_key`, declaring nation, target nation, and objective type.

| Objective | `+15` satisfies | `+5` partially satisfies | `-15` unrelated harsh terms dominate | `-20` contradicts |
|-----------|-----------------|---------------------------|----------------------------------------|-------------------|
| `conquest` | Objective enemy accepts material territorial, gold, alignment, or military concessions after the proposer controls the target capital / objective region. | The objective enemy is covered and peace is secured, but the package has no direct concession tied to the declared target. | Harsh terms mostly burden other covered enemies while the declared target receives no objective-tied concession. | The package returns the objective region to the accepting side or strengthens the declared target against the proposer. |
| `subjugation` | Target becomes a vassal or equivalent forced dependency and passes the WPS power-cap gate. | Target is reduced below the cap or forced into a lesser dependency, but not fully subjugated. | Harsh terms mostly burden other covered enemies while the target remains outside any dependency. | The package protects, restores, or strengthens the target's independence against the declared subjugation purpose. |
| `forced_alliance` | Target receives a `forced_alliance` clause. | Target enters `DEFENSIVE_ALLIANCE` / `ALLIANCE` or comparable alignment without the forced-origin clause. | Harsh terms mostly burden other covered enemies while the target receives no alignment change. | Target is left or moved into an opposing bloc, or an existing proposer alignment over the target is weakened. |
| `defense` | All occupied friendly/core regions named by the objective are restored or hostile control is removed. | Some, but not all, objective regions are restored. | Harsh offensive terms against unrelated enemies dominate while the defensive objective is only partially addressed. | The proposer cedes its own objective/core regions or leaves the main occupied target with the enemy while demanding unrelated terms. |
| `liberation` | All named vassals / client capitals in the objective are liberated. | At least one named vassal is liberated. | Harsh terms mostly burden other covered enemies while named dependents remain unliberated. | The package preserves, deepens, or rewards the targeted vassalage / forced alignment. |

All component calculations are integerized with `round()` at the component boundary. The final score is clamped to `[-100, 100]`. Empty covered-enemy sets are invalid before scoring.

Zero-region accepting leaders do not receive the `+5` "keeps all owned territory" bonus. Controlled holdings are scored by settlement terms, not by current occupation alone. If the leader had mapped holdings at war entry and the package permanently cedes, forced-aligns, or recognizes the loss of those holdings, add `lost_mapped_holdings = -5` per holding inside `leader_own_losses`, capped at `-10`, before clamping. If those holdings are merely occupied during the war and the package restores them, leaves them unresolved, or offers white peace, do not apply the lost-holdings penalty; side pressure and war exhaustion already model the pressure to stop fighting. Britain-specific current-map rule: `NATION_CAPITALS["Britain"] == "Netherlands"` is the configured current-map home/spawn region until a future map expansion replaces it with a real British capital; settlement must not infer a separate settlement identity from that proxy.

Settlement-tier harshness ceilings:

| Tier | Max harshness before `-10` mismatch |
|------|-------------------------------------|
| `white_peace` | `0.10` |
| `favorable_terms` | `0.25` |
| `dictated_terms` | `0.45` |
| `harsh_peace` | `0.70` |
| `total_victory` | `1.00` |

`term_harshness_penalty` and `burdened_participant_penalty` intentionally stack. The first scores overall package weight; the second scores the enemy leader's political cost of selling out non-leader participants.

`projected_hegemony_mod` uses the same bloc-share semantics and `33%` / `50%` / `60%` band thresholds as the live Balance of Europe / hegemony calculation. Its pure projection helper starts from cached nation-region and bloc data, applies settlement term deltas in memory, and never mutates live world state:

```python
project_balance_after_settlement(world, war_id, terms) -> {
    "pre_hegemon": str | None,
    "post_hegemon": str | None,
    "pre_share": float,
    "post_share": float,
    "crossed_band": None | 33 | 50 | 60,
    "deepened_band": None | 33 | 50 | 60,
    "hegemon_swap": bool,
    "modifier": int,
}
```

The projection starts from current bloc geometry, applies forced alliance, liberation, vassalage, and territory-transfer effects from the proposed package, and never mutates `WorldState` during preview. Implementation must use lightweight delta projection on affected alignment/ownership data only, not a full `WorldState` deep copy. Territory baselines come from cached helpers such as `get_nation_regions()`; preview loops must apply term deltas to those cached sets and must not iterate `world.regions.values()`.

`projected_hegemony_mod` is outside the bilateral `political_subtotal_clamped` floor by design because common-peace acceptance is a single war-scoped score clamped to `[-100, 100]`, not a bilateral memory subtotal. The asymmetry is intentional: bilateral hegemony resistance is persistent relationship friction, while common-peace projection scores the legitimacy of the proposed settlement package itself.

`base_side_pressure` is the war-level headline component. Every term that burdens a specific enemy must also pass the section 6.3 direct-score gate for that payer; a high side average cannot authorize harsh terms against a barely-defeated major.

If the accepting leader changes between proposal construction and acceptance evaluation, re-evaluate the package against the new leader before resolving. If the proposer-side leader changes, void the staged package and require reopening. If accepted, all covered active hostile pairs resolve; uncovered hostile pairs remain active under section 10.5. If rejected, the whole package fails. The player can then try separate peace with individual enemies or revise terms. Rejection feedback must identify the top 1-2 objectionable terms or acceptance components by absolute penalty so the player knows whether the problem was Silesia, forced alliance, insufficient direct pressure, a bargain conflict, or accumulated harshness.

Burdened non-leader rule:

- If a non-leader enemy pays territory, vassalage, forced alliance, or liberation costs, compute `direct_score = max(get_war_score_for(side_member, burdened_enemy))` across proposer-side participants.
- `direct_score >= 20`: normal non-leader burden; add `0` burdened-participant penalty unless another rule below applies.
- `0 <= direct_score < 20`: add `burdened_participant_penalty = -15` and surface a severe warning.
- `direct_score < 0`: add `burdened_participant_penalty = -30`; only occupied, objective-linked, or bargain-linked territorial terms are legal.
- If the burdened non-leader is a `major`, add an additional `-10` unless their capital is occupied or the term directly matches the war objective.

These penalties are not vetoes. They model the enemy leader's reluctance to sell out an ally and set up the post-ratification resentment in §14.6.

The aggregate cap scales with the number of burdened non-leaders: one burdened enemy caps at `-30`, two or more cap at `-60`. This prevents full-Europe packages from making three moderate sellouts cheaper per participant than one severe sellout.

### Step 5: Settlement reaction pass

After peace succeeds, every relevant party evaluates the outcome. Run for **both sides**. Proposer-side ally reactions are the main player-facing loop in the current France campaign, but enemy-side "sold out by leader" reactions are primary political events, not background flavor.

Common-peace ratification uses this ordering in one transaction: validate `settlement_confirm` live state -> snapshot every covered pair's war-instance data and contribution linkage before any cleanup -> ratify treaty terms -> mutate region ownership / alliances / forced alignment -> call `cleanup_war_end()` only after all covered-pair snapshots exist -> run WB-B fulfillment/breach evaluation -> invalidate `war_instances_by_leader`, `war_instances_by_participant`, Balance of Europe, hegemony, and bloc caches -> run settlement and cross-war reactions from fresh indexes -> fire threshold checks caused by the mutation -> build campaign log, dispatch, notification, and ledger payloads. Separate-peace fallout that makes a bargain impossible routes through the same WB-B breach helper immediately after the separate peace mutation, then invalidates the same affected caches before the smaller settlement reaction pass.

The reaction pass also checks active cross-war consequences. If a settlement changes region ownership, strengthens a rival on a border, changes forced alignment, affects a bargain target, or alters survival/capital stakes, use `war_instances_by_participant` to inspect active `war_instances` for participants in the affected nation set and evaluate their reaction. This is bounded by the affected terms and active participants; do not broad-scan every nation in Europe.

Complexity bound: build `affected_nations` from term payers, beneficiaries, region-adjacent controllers, bargain parties, and survival/capital targets. Then union `war_instances_by_participant[nation]` for those affected nations and inspect only those active wars. Directly affected wars are mandatory: if an active war contains a payer, beneficiary, active bargain party, capital/survival target, or nation whose owned region changes hands, inspect that war even if more than three such wars exist. The "at most 3" cap applies only to secondary local-balance scans whose sole connection is adjacency / sphere / `rival_strengthened`; select those secondary wars by highest overlap count with `affected_nations` and then oldest `created_sequence` as tie-break. Do not iterate all nations by all war instances.

Cross-war reactions that create `settlement_shut_out`, `rival_strengthened`, or equivalent settlement grievance flags use the same existing acceptance path as same-war reactions: write the grievance flag to `betrayal_history[pair]["grievance_flags"]`, surface rich context in `settlement_memories`, and let subsequent bilateral acceptance read it through `grievance_modifier` with the existing per-flag cap and composite-floor rules. Do not create a parallel cross-war acceptance modifier.

**Proposer-side reactions** (France-side in the current player campaign):

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

Forced-alliance threat is intentionally per clause and has no settlement-package cap in this settlement phase. A common peace that forces two or three enemies into alignment can therefore add `+30` or `+45` threat in one ratification. The settlement preview must aggregate that projected threat delta before confirmation, name any crossed coalition thresholds (`60` brewing, `80` instant-declaration risk, `90` cooldown override per `COALITION_SPEC.md`), and feed the projected Balance-of-Europe warning into the same concern list as `projected_hegemony_mod`. This is not a veto; it is the visible cost of an imperial-looking package.

### Step 6: Next-turn presentation

- Notification rail, dispatch, ledger, named diplomat voice.
- Do not spam one popup per ally. Aggregate reactions, then spotlight only major breaches or bargain fulfillment/breach.
- Mechanical grievance / gratitude / sold-out records all apply, but presentation dispatches are capped at 4 primary settlement beats per ratification. Remaining reactions are grouped into one settlement digest line using the DG-7 categorized-dispatch pattern.
- Campaign log emits exactly one `settlement_summary` entry per ratified common peace. Participant-level reactions are stored in `settlement_summary["participant_reactions"]` as structured data and the one-liner shows at most three named participants plus `+N more`.
- Settlement reaction events use their own settlement route metadata. Existing `bargain_*` events continue to use commitments routing, and `balance_of_europe_shifted` remains owned by Memory and Pressure.

Settlement event contract:

| Event | Payload minimum | One-liner | Fog rule | Route metadata |
|-------|-----------------|-----------|----------|----------------|
| `settlement_summary` | `{war_id, covered_enemy_participants, proposer_side, accepting_side, terms_summary, participant_reactions, warnings, balance_projection, turn}` | "Settlement of {war_name}: {terms_summary[0]}; {participant_1}, {participant_2}, {participant_3}{+N more} react." | Visible to France; visible to any court that can see at least one covered participant, resulting territorial/alignment change, or participant reaction involving itself. | `event_family="settlement"`, `review_target="settlement_review"` when the war remains active, otherwise `review_target="diplomatic_ledger"`, `route_id="settlement_summary:{war_id}:{turn}"`. |
| `settlement_digest` | `{war_id, hidden_reaction_count, top_reaction_types, turn}` | "{hidden_reaction_count} additional courts register the settlement aftermath." | Same as `settlement_summary`, filtered to courts that can see at least one hidden reaction. | `event_family="settlement"`, `review_target="diplomatic_ledger"`, `route_id="settlement_digest:{war_id}:{turn}"`. |

Settlement route metadata is separate from `COMMITMENTS_ROUTES`. Commitment-owned `bargain_*` events keep their existing routes; settlement-owned events point to the settlement review while the war is active and to the diplomatic ledger after the war archives.

---

## 12. Territory Demand Legitimacy

Territorial demands require a **pressure basis**. Occupation is not mandatory - Napoleon often dictated unoccupied concessions after decisive victories - but every region transfer must be justified. Demands without a pressure basis are legal only as extreme terms and carry severe acceptance and hegemony consequences.

`extreme_terms` is not a separate settlement tier. It is a warning/diagnostic label for any legal territorial demand that lacks occupation, objective, bargain, restoration, or strong direct-score basis. Extreme terms remain possible only when direct-score gates allow them, but they add severe territory-legitimacy warnings, feed `term_harshness_penalty`, and can make `war_objective_alignment` negative when unrelated harsh terms dominate.

### 12.1 Pressure bases

For every territorial term, evaluate:

| Basis | Strength | Description |
|-------|----------|-------------|
| `occupied_by_proposer_side` | Strong | Region is currently controlled by the settlement actor or a proposer-side ally |
| `war_objective_or_bargain` | Strong | Region is tied to declared war objective, liberation objective, or active war bargain |
| `high_pairwise_pressure` | Medium | The proposer side has strong pairwise war score against the `from` nation |
| `general_side_victory` | Weak | The proposer side is winning the overall war, but has little direct pressure on the `from` nation |

### 12.2 Penalty rules

```
territory_demand_cost =
    base_territory_demand
    + unoccupied_region_penalty          # if not held by proposer side
    + weak_pressure_penalty              # if low pairwise war score against `from`
    + excessive_land_burden_penalty      # if too many regions demanded from one enemy
    - occupied_discount                  # if held by proposer side
    - war_objective_discount             # if tied to declared objective
    - bargain_claim_discount             # if tied to active WB claim for France
    - liberation_claim_discount          # if restoring a liberated nation
```

First-pass constants:

| Term | Value |
|------|-------|
| `base_territory_demand` | `8` per region |
| `unoccupied_region_penalty` | `+12` when not controlled by proposer side |
| `weak_pressure_penalty` | `+10` when `direct_score < 20`, `+20` when `direct_score < 0` |
| `excessive_land_burden_penalty` | `+6` for the second region from same enemy, `+10` for each additional region |
| `occupied_discount` | `-6` |
| `war_objective_discount` | `-6` |
| `bargain_claim_discount` | `-4` for France's WB `claim_region`; does not apply to ally-beneficiary land because current WB claims are France-claim-scoped |
| `liberation_claim_discount` | `-8` |

Individual `territory_demand_cost` floors at `0` before package harshness accounting. Discounts can make a demand free, but never negative.

### 12.3 Edge cases

- **Region belongs to a non-participant:** Hard stop. Cannot demand territory from a nation not in the war.
- **`from` is only an enemy ally that the proposer side barely fought:** Very high acceptance penalty. The enemy war leader will resist giving away an ally's land when that ally is not the one who lost.
- **Region tied to a war bargain but unoccupied:** Bargain discount reduces but does not eliminate the unoccupied penalty. Promise legitimacy helps, but the enemy still knows the proposer side does not hold it.

### 12.4 Talleyrand warnings

Territory legitimacy feeds into the Step 2 advisory preview:

- *"We hold Saxony. Austria has little ground to refuse."*
- *"We demand Bohemia, but no French marshal has set foot there. Austria will resist fiercely."*
- *"Prussia is barely a party to this war. Taking Silesia from them is an act of imperial overreach."*

---

## 13. Term Ownership

### 13.1 Beneficiary fields on existing terms

The settlement actor can award territory to an ally. Use ownership fields on existing `territory_cede`, not a new term type:

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
- An active same-side participant with `seat` or `consult` standing, including treaty allies, coalition partners, and co-belligerents that are not formal allies
- A same-side `beneficiary_only` participant when the term directly names its survival, capital, core territory, liberation, restoration, or existing promise basis
- A liberated nation
- A former owner restored by treaty

"Ally" in player-facing copy can still describe treaty partners, but validation must use same-side participation plus standing/direct-stake rules. A non-treaty co-belligerent that earned `seat` or `consult` standing is eligible to receive a direct reward; a low-standing bystander is not.

### 13.3 Invalid settlement shapes

Do not support:

- Ally gives region to another ally through three-step chains
- Hidden off-screen transfer to non-participants
- Nested protectorate / vassal / subject distribution logic

Keep settlement packages direct and legible.

### 13.4 Competing ally claims on the same region

If multiple same-side participants have territorial interest in the same region, awarding it to one participant creates settlement reactions for the others. Interest can come from an active War Bargain, former ownership, core/restoration basis, local sphere, adjacency plus `rival_strengthened`, or a direct contribution/occupation claim recorded in contribution events.

Warnings must name the claim basis for every shown claimant. Example shape: `"Prussia expects Saxony by war bargain; Bavaria has an occupation claim; Saxony has a restoration claim."` Do not render bare "expects this region" copy without the reason.

Reaction rule:

- The recipient receives the normal beneficiary reward, relation bonus, and any eligible `settlement_gratitude`.
- Other interested participants receive an advisory warning during draft review.
- Other interested participants receive no grievance if they have only weak local-balance interest and no standing.
- Other interested participants can receive `settlement_shut_out` or a bargain breach/void route only when they had `seat` or `consult` standing, an active bargain, direct territorial/survival stake, or material contribution tied to the awarded region.
- The warning copy names the conflict of claims, not just the awarded recipient: "Prussia expects Saxony, but Bavaria would receive it."

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
- Ally had `seat` standing, strong claim interest, or high contribution (>= 20%)
- Effect: larger relation hit (`-15` to `-25`), `settlement_shut_out` grievance flag, possible treaty downgrade pressure

**Promise breach (war bargain):**
- France could have secured the active WB claim for France and chose not to
- Effect: route through existing WB-B breach pipeline → `bargain_breached` → betrayal strike + reliability hit + existing bargain breach presentation

**Major power humiliation:**
- `major` power with `seat` standing, excluded or visibly subordinated
- Effect: hard-reject posture risk, coalition drift through threat/bloc systems, possible `balance_of_europe_shifted` beat only if the existing threshold/swap contract is met

Seat standing is sufficient to surface a major-power consultation warning even when material contribution is low. Severity still depends on investment. A `major` with `seat` plus material contribution, direct territorial/survival stake, active bargain stake, or real support contribution can trigger the full major shut-out / humiliation bands. A zero-material `major` with no direct stake keeps `seat` standing for visibility, but exclusion is a reduced warning: relation impact `-5` to `-10`, no major shut-out grievance flag, and no hard-reject posture or downgrade pressure unless repeated later behavior creates a normal grievance basis. This preserves great-power diplomatic voice without making a zero-contribution participant cost the same as a 30% material contributor.

### 14.3 Rewarded ally memory

`they_chose_us` is a positive settlement memory, not just a one-time relation delta.

When a `seat` or `consult` ally receives a meaningful direct reward:

- Relation with France: `+5` for consult, `+10` for seat.
- Add a transient `settlement_gratitude` memory on the pair for 10 turns only if `material_contribution_points > 0` in the current episode. Zero-material beneficiary rewards may still receive the immediate relation bonus, but they do not create the reusable acceptance modifier.
- Subsequent deep-treaty and war-entry proposals from France to that ally receive `+5` acceptance while the memory is active.
- The bonus is capped at one active gratitude memory per pair; a subsequent rewarded settlement refreshes the expiry, not the value.

Acceptance hook: expose this as `settlement_gratitude_mod = +5` when an active `settlement_gratitude` memory exists with `actor="France"` and `subject=<proposal_target>`, and the proposal is a deep treaty (`DEFENSIVE_ALLIANCE` or `ALLIANCE`), a war-entry request, or a war-bargain / ally-entry proposal where the rewarded ally is being asked to support France again. The modifier is an upside component only, added after `political_subtotal_clamped`; it is not part of the clamped political subtotal and cannot bypass hard posture gates. Debug output and proposal previews name the component as `settlement_gratitude_mod`.

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

Combined relation impact is intentionally visible: BPH-C base penalty (`-5` to `-15`) plus settlement shut-out penalty (`-5` to `-25`, only when standing warrants) yields a possible total of `-10` to `-40` for one affected ally. The settlement pass must never re-apply the BPH-C base penalty.

Serial bilateral settlements are tracked per `war_id`. When France ratifies the third or later separate peace from the same `war_instance` in a rolling 5-turn lookback window `[current_turn - 5, current_turn)`, run an aggregate `serial_bilateral_settlement` warning/reaction for remaining same-side participants with `seat` or `consult` standing. This adds an extra `-5` relation hit per serial peace beyond the second, capped at `-15`, and can add `settlement_shut_out` only if the normal standing/material/direct-stake gates are met. This keeps separate peace as a weapon while preventing the player from avoiding common-peace acceptance by chopping a 6-8 participant war into consequence-light bilateral deals.

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
- While `sold_out_by_war_leader` is active, deep-treaty, war-entry, and bargain/ally-entry proposals from the former leader to the sold-out participant are hard-rejected unless the proposal includes concrete redress or the relation is already `>= 50`. This is a posture gate, not a new acceptance modifier, and it expires with the memory.

Combined posture-gate precedence: `sold_out_by_war_leader`, DG-4 `anti_renewal_cooldown`, hard-reject posture, oathbreaker posture, and other deep-treaty hard gates do not add their durations together, but a proposal remains blocked while any non-bypassable gate is active. Preview/debug output must list every active blocker and the effective unblock turn as the maximum active expiry. Concrete settlement redress or relation `>= 50` can bypass only `sold_out_by_war_leader`; it cannot bypass `anti_renewal_cooldown`, hard-reject posture, oathbreaker posture, or an invalid diplomatic-state transition unless that owning spec explicitly allows it.

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

Common-peace ratification is a treaty-ratification event for WB lifecycle purposes: settlement terms mutate region ownership during ratification, then WB-B fulfillment/breach evaluation runs in the same turn-end lifecycle pass. The settlement reaction pass reads the post-WB terminal status, so a bargain fulfilled by the package appears as `fulfilled`, not merely "at risk."

Ally-beneficiary land awards are separate settlement rewards. They may create `they_chose_us` / eligible material-contribution-gated `settlement_gratitude` and may satisfy standing expectations, but they do **not** fulfill the current WB claim because shipped War Bargains are France-claim-scoped.

### 15.2 Bargain breach at settlement

A war bargain is **breached** when:

- France could have secured the WB `claim_term.claim_region` for itself under the package and chose not to
- France cuts separate peace that makes the bargain impossible
- France awards the WB `claim_term.claim_region` to an ally, to a different third party, or back to the named enemy while fulfillment was feasible

Settlement-triggered breach routes through the existing WB-B breach pipeline: `bargain_breached` → betrayal strike + reliability hit + WB-D presentation.

Deterministic settlement classifier:

```python
classify_bargain_settlement_status(world, bargain, war_instance, settlement_terms, direct_scores) -> {
    "status": "dormant" | "fulfillable" | "fulfilled_by_terms" | "at_risk" | "impossible" | "breach_if_confirmed",
    "claim_region": str,
    "reason": str,
    "required_action": str | None,
}
```

`classify_bargain_settlement_status(...)` is a pure classifier. It must not mutate bargain state, treaty state, settlement terms, relations, memories, campaign log, dispatch, or dialogue queues. The implementation must make the draft `settlement_terms`, `direct_scores`, covered enemy set, and current live bargain snapshot explicit inputs so advisory preview and final confirmation can call the same classifier with different terms and receive deterministic results.

If a bargain is attached to a `war_instance`, settlement stores the original side/leader context as snapshot metadata (`war_id`, `side_at_creation`, `side_leader_at_creation`) rather than deriving it from the current `attacker_leader` / `defender_leader` at classification time. Leader replacement can change who has authority to stage or accept a settlement, but it must not rewrite the original bargain promise context or make an otherwise fulfillable bargain look impossible solely because leadership passed to a successor.

Classification rules, evaluated against the draft terms and current live state. The boundary between `dormant` and `at_risk` is enemy coverage: if the draft package covers the named enemy but leaves the live claim unresolved, it is `at_risk`; if the named enemy is not covered by the package, the bargain is `dormant`.

- `dormant`: bargain is not `active` / `triggered`, is not attached to this `war_id`, or the named enemy is not covered by the draft settlement.
- `fulfillable`: bargain is `triggered`, France and beneficiary were co-belligerents against the named enemy, France still holds `DEFENSIVE_ALLIANCE` or `ALLIANCE` with beneficiary, the claim basis still exists, and either France currently controls `claim_region` or a valid term can transfer `claim_region` from the named enemy / its subject to France.
- `fulfilled_by_terms`: same as `fulfillable`, and the draft package includes the valid transfer or recognition that leaves France controlling `claim_region`.
- `at_risk`: the bargain is relevant and live, the named enemy is covered by the draft settlement, and the draft package does not decide the claim region while leaving the named war or claim basis alive.
- `impossible`: fulfillment cannot be achieved because the claim region, named enemy, source treaty, co-belligerence, or claim-holder basis disappeared for a WB-B void reason not caused by this settlement package. It also fires when `claim_region` is currently controlled by a third party outside the covered settlement, by a same-side ally, or by any party from whom the current package has no legal transfer path to France without an intermediate settlement step.
- `breach_if_confirmed`: `fulfillable` is true, but the draft package gives `claim_region` to anyone other than France, returns it to the named enemy, normalizes with the named enemy while leaving the claim unresolved, or omits the French claim while resolving the covered enemy in a way that makes later fulfillment impossible.

The advisory surfaces `status`, `reason`, and `required_action`. Only `breach_if_confirmed` routes to WB-B breach on confirmation; `impossible` routes to WB-B void when the void cause is external / counterparty-owned.

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
- Projected costs for major ally fallout, including approximate relation delta and whether a `settlement_shut_out` grievance would add a future `grievance_modifier`
- Per-term marginal acceptance cost where available, so dropping a single region or forced alignment can explain the expected score change
- Whether a region is "theirs by contribution," "ours by bargain," "theirs by restoration," or "ours if we insist"

Default advisory rows are capped at 5 by `rank_diplomatic_salience()`: warning severity, `seat` over `consult`, material contribution over staying power, active bargain stake, direct territorial stake, rival-strengthened warning, power tier, and stable nation id/name. Compute this ordering once per preview/confirm evaluation and pass the ranked result through advisory rendering; do not recompute it for every UI row refresh. Overflow is grouped behind "View all participants." WARNING and HARD_STOP warnings are rendered above this list and are not suppressed by the row cap.

Advisory copy distinguishes earned standing from diplomatic weight. A participant with material contribution and `standing_share >= 25%` has "earned a voice through sacrifice"; a `major` with `seat` standing but low material contribution "demands a voice at the table" because of power-tier status. The standing level is the same, but the explanation should not imply a subsidy/support-only participant won battles it did not mechanically fight.

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

Full-Europe settlement review uses a sectioned information layout rather than one undifferentiated advisory list. The required sections are:

- `Terms`: proposed treaty terms, payers, beneficiaries, legitimacy basis, and per-term marginal acceptance cost where available.
- `Allies`: standing, contribution share, beneficiary status, competing-claim notes, and expected gratitude/grievance outcomes.
- `Warnings`: hard stops first, then top warnings, with overflow behind "View all concerns."
- `Acceptance`: total score, acceptability band, top fixable components, and full debug component breakdown when debug mode is active.

These sections may be implemented as tabs, segmented controls, or stacked collapsible sections, but they must preserve the top-five row cap, the warning cap, and the CanvasLayer 50 one-screen rule. Synthetic 6+ participant payload smoke tests must verify that text does not overlap and that no single section is required to render every participant, warning, and acceptance component at once.

### 16.3 Warning presentation

Settlement warnings use the same structured `warnings[]` approach as bilateral diplomacy:

- All `HARD_STOP` warnings render inline.
- Render the top 2 `WARNING` warnings inline after hard stops, severity- and salience-sorted.
- `INFO` warnings and any additional `WARNING` rows go behind "View all concerns."
- Settlement-specific warnings (promise breach, major ally fallout) outrank generic rivalry flavor
- The advisory row cap applies only to standing/contribution summaries. It must not hide hard stops or the top warning rows above.

### 16.4 Hard stops vs soft warnings

**Hard stop only for:**
- Impossible / invalid settlement shapes (e.g., demanding territory from a non-participant)
- Term packages that would create contradictory state

**Everything else is political cost, not veto:**
- Ally consultation skipped
- Major-power humiliation risk
- Shut-out risk
- Separate-peace fallout
- Promise breach warning (player can still choose to proceed)

### 16.5 AI behavior

AI uses the same settlement executor and validation paths as the player.

- AI war leaders may propose common peace only when they are the current side leader for a `war_instance`.
- AI proposes common peace only when there are no hard stops and either (a) the AI side is winning with `side_pressure_score >= 40` and direct score against the opposing leader is at least `20`, or (b) the AI side is losing with `side_pressure_score <= -40` and existing war exhaustion / ticking-pressure logic says continued war is strategically costly.
- AI common-peace proposal anti-spam: at most one active `incoming_settlement_offer` may exist for the player at a time; each `war_id` has a 3-turn AI common-peace proposal cooldown after reject, request-revision, expiry, or failed live-state validation; and AI may surface at most one new settlement offer to the player per turn across all wars. AI-vs-AI internal settlements use the same per-`war_id` 3-turn cooldown to avoid proposal churn. Store these cooldowns in `world.ai_settlement_cooldowns: Dict[str, int]` keyed by `war_id` with save/load default `{}`. This cooldown namespace is separate from existing bilateral `ai_proposal_cooldowns` / `player_proposal_cooldowns`; common peace does not consume a bilateral nation-pair cooldown unless the same action also sends a bilateral proposal.
- AI prefers common peace when two or more enemy participants are covered, or when settlement standing, ally-beneficiary rewards, or war-bargain settlement logic is relevant. AI prefers separate bilateral peace when only one enemy is targeted and there are no ally-beneficiary, standing, or bargain implications.
- AI covered-enemy selection includes the opposing leader plus any non-leader with `direct_score >= 30`, any occupied-return / restitution target, and any target needed to resolve an active bargain or objective. It does not cover every enemy by default.
- AI common-peace packages are conservative: prefer white peace / limited gold / occupied-region returns unless the AI side has `harsh_peace` or better settlement tier and direct pressure against each burdened participant.
- Before surfacing an AI common-peace offer, the AI must construct a concrete package and evaluate it through the same common-peace acceptance formula from the accepting side's perspective. If no package can reach `score >= 50`, the AI does not offer common peace and records `decision_reason="package_unacceptable"` / `top_failed_component` in debug output. Losing-side AI may offer concessions, occupied-region returns, or limited alignment terms only when the resulting package passes the same acceptance check; it must not spam white-peace offers into an obvious hard reject.
- AI defender packages in player-initiated wars often have only the WPS auto-`defense` objective. They must not rely on a guaranteed `+15` `war_objective_alignment` score. Package construction must tolerate `war_objective_alignment` of `0` or `+5` for defensive objectives and still evaluate whether side pressure, war exhaustion, leader-own-loss avoidance, and abandoned-ally pressure make the package acceptable.
- AI v1 does not create speculative ally-beneficiary land gifts. It may include ally-beneficiary terms only for restoration, liberation, occupied-region return, or a direct existing promise basis that passes section 13.2.
- AI separate peace uses the existing bilateral proposal path, then runs the same smaller settlement reaction pass for remaining co-belligerents.
- AI acceptance of a player common-peace package uses the Step 4 common-peace acceptance formula with projected hegemony, direct-score gates, and burdened-participant penalties.
- AI common-peace proposals that resolve AI-vs-AI wars do not create a player-facing `settlement_confirm` popup, but they must stage an internal `settlement_confirm` payload and pass through the same `confirm` validation executor before mutation.
- AI-vs-AI common peace emits one `settlement_summary` campaign-log entry and one fog-eligible Diplomatic Affairs dispatch line when the player has visibility into at least one covered participant or resulting territorial/alignment change. It must not emit one popup or rail notice per participant.
- AI common-peace proposals offered to the player create an incoming settlement-review dialogue, not an automatic ratification. The player sees covered enemies, terms, acceptance components, ally fallout, and actions to accept, reject, or request revision. Accepting the AI offer then stages/executes the same `settlement_confirm.confirm` path with leader revalidation and no direct mutation from the incoming offer.
- No AI path may bypass leader revalidation, active pair-key validation, hard stops, direct-score gates, WB-B lifecycle checks, or reaction-pass construction.
- AI never creates ally-beneficiary land terms that would violate the allowed-beneficiary rules in §13.2.
- AI never bypasses War Bargain fulfillment/breach checks; settlement-triggered promise outcomes route through WB-B/WB-D just like player outcomes.
- AI proposal reasons use deterministic `decision_reason` values: `common_peace_pressure`, `direct_score_insufficient`, `ally_burden_too_high`, `bargain_conflict`, `hegemony_projection`, and `settlement_tier_mismatch`.

---

## 17. Data Model Additions

### 17.1 New fields

```python
world.next_war_instance_id: int = 1
world.war_instances: Dict[str, Dict] = {}
world.archived_war_instances: List[Dict] = []
world.war_contribution_scores: Dict[str, Dict[str, Dict]] = {}
world.settlement_memories: Dict[str, List[Dict]] = {}
world.ai_settlement_cooldowns: Dict[str, int] = {}
world.pending_settlement_dialogues: List[Dict] = []
```

A nation may be an active participant in multiple concurrent `war_instance` records. Contribution, staying power, support, and episode ids accrue independently per `war_id`; never merge contribution across wars unless a section 7.2 war-instance merge transaction rewrites the absorbed `war_id` references first.

`war_contribution_scores[war_id]` is retained while the `war_instance` is active and through the same 10-turn terminal retention window as the ended `war_instance`. When the ended instance moves to `world.archived_war_instances`, contribution detail may be compacted to final per-nation totals unless an active campaign-log row, ledger row, settlement dialogue, dispatch route, or settlement memory still references episode-level detail.

`settlement_memories` stores positive/transient settlement records such as `settlement_gratitude` and enemy-side `sold_out_by_war_leader`. Keys use the canonical ordered pair string `actor|subject`. Negative proposer-side grievances use existing `betrayal_history[pair]["grievance_flags"]` with `grievance_type="settlement_shut_out"`; do not add a parallel grievance store.

`ai_settlement_cooldowns` stores common-peace AI anti-spam cooldowns by `war_id`. It is separate from bilateral `ai_proposal_cooldowns` / `player_proposal_cooldowns` and defaults to `{}` on old saves.

`pending_settlement_dialogues` stores settlement-owned deferred dialogue payloads when a `settlement_confirm` or `incoming_settlement_offer` would be created while the generic dialogue queue is at or near cap. It is not a general dialogue queue replacement. Each entry uses the same locked payload shape as the dialogue it will later stage plus `war_id`, `dialogue_type`, `created_turn`, `retry_after_turn`, and `expires_on_turn`. The retry loop attempts at most one deferred settlement dialogue per turn across all wars after expired entries are discarded, preserving deterministic ordering by `(created_turn, war_id, dialogue_type)`. Entries expire when their underlying `war_instance` is no longer active/recent, their covered pair keys are resolved in a way that invalidates the offer, or `current_turn > expires_on_turn`. If an entry cannot be promoted because live-state validation fails, remove it and apply the normal per-`war_id` AI settlement cooldown.

Settlement-memory per-turn cleanup removes inactive or expired memory entries where `current_turn > expires_on_turn`. Run cleanup after any settlement-memory acceptance modifiers or ledger queries for that turn have read active records, and before dispatch / presentation payload construction. Cleanup must not mutate existing `betrayal_history` grievance flags. Cleanup is deterministic from `current_turn` and stored record fields only; save/load at any point in the turn lifecycle must produce the same active/expired result after cleanup runs. `pending_settlement_dialogues` expiry is handled by the C2 retry loop above.

Settlement memories are idempotent by `(memory_type, actor, subject, counterparty, war_id, episode_id)`. If the same settlement writes the same gratitude or sold-out memory twice because cleanup was skipped or save/load replayed a staged confirm, refresh the existing record's `expires_on_turn` and payload instead of appending a duplicate. `settlement_gratitude` refreshes; it never stacks multiple `+5` acceptance bonuses for the same actor/subject/proposal target.

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

- `world.next_war_instance_id`, `world.war_instances`, `world.archived_war_instances`, `world.war_contribution_scores`, `world.settlement_memories`, `world.ai_settlement_cooldowns`, and `world.pending_settlement_dialogues` are saved and loaded through `WorldState.to_dict()` / `WorldState.from_dict()` with `1` / `{}` / `[]` defaults for older saves.
- `docs/SAVE_FORMAT_REFERENCE.md` must document all settlement fields in Slice A / B / C2 / D as each field lands.
- `settlement_memories` stores detail payloads that do not fit the existing grievance flag shape. Existing `grievance_flags` remain `{grievance_type, episode_id, turn, source_episode_type}` only.
- When a terminal `war_instance` leaves the 10-turn live retention window, move a compact terminal record to `archived_war_instances`: `war_id`, `created_turn`, `ended_turn`, `end_reason`, leaders, participants, resolved pair keys, separate-peace exits, and settlement summary references. Per-event contribution detail may be compacted to final episode totals unless an active `settlement_memory`, campaign-log entry, pending dialogue, or ledger reference still points to the detailed record. Enforce retention/compaction on every archive operation, not only on periodic cleanup, so rapid full-Europe war endings cannot grow the archive unbounded for a turn. This keeps full-Europe saves bounded without losing recent settlement context.

Mapped-nation capital helper:

```python
def get_settlement_home_capital(world, nation: str) -> Optional[str]:
    """Return the configured mapped capital/home region for settlement scoring."""
```

The helper may also be implemented as `WorldState.get_settlement_home_capital(self, nation)` if that fits the surrounding model code better; the semantics are identical.

Rules:

- Return `NATION_CAPITALS.get(nation)` when the nation exists in the scenario/map and the configured region exists.
- Return `None` only as a safe fallback for incomplete synthetic fixtures or future scenario data under construction.
- Do not infer settlement participation from `None`.
- Capital-dependent settlement components skip the capital-specific subcomponent when the helper returns `None`.
- Fixture validation should warn or fail when a real mapped major in a settlement test is missing a capital/home region unexpectedly.
- Britain currently returns `Netherlands` because that is the configured current-map home/spawn region; a future Europe map may replace it with a real British capital through normal scenario data.

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

# War instances track separate-peace exits for abandoned-ally acceptance pressure
war_instance["separate_peaced"] = [
    {
        "nation": "Prussia",
        "side": "defenders",
        "exited_turn": 18,
        "peace_type": "separate_peace",
        "original_side_size": 4,
    }
]

# Campaign log stores one aggregated common-peace event
settlement_summary_event = {
    "type": "settlement_summary",
    "turn": 24,
    "war_id": "war_12",
    "covered_enemy_participants": ["Austria", "Bavaria"],
    "proposer_side": "attackers",
    "accepting_side": "defenders",
    "terms_summary": ["territory_cede:Saxony->Prussia"],
    "participant_reactions": [],
    "warnings": [],
    "route": {
        "event_family": "settlement",
        "review_target": "settlement_review",
        "route_id": "settlement_summary:war_12:24",
    },
}
```

### 17.3 Derived at settlement time (not stored)

```python
total_contribution_share[nation] = contribution_total(nation) / total_side_contribution
material_contribution_share[nation] = material_contribution_total(nation) / total_side_material_contribution
standing_share[nation] = material_contribution_share[nation]
standing_level[nation] = classify_standing(nation, war_instance, standing_share, ...)
side_pressure_score = compute_side_pressure_score(war_instance)
direct_scores[payer] = compute_direct_scores_by_enemy(war_instance)

# Build term-beneficiary-adjacency map ONCE per evaluation, then pass to each call:
term_adjacency_map = build_term_adjacency_map(settlement_terms, world)
rival_strengthened[nation] = compute_local_balance_warning(nation, settlement_terms, term_adjacency_map)

balance_projection = project_balance_after_settlement(world, war_id, settlement_terms)
war_instances_by_leader = build_war_instances_by_leader(world)        # per-turn cache
war_instances_by_participant = build_war_instances_by_participant(world)  # per-turn cache
```

Implementation note: `compute_local_balance_warning()` is called per participant (6-8 times per settlement preview). Build the term-beneficiary-adjacency map once per settlement evaluation and pass it into each per-nation call. Do not re-derive region adjacency per participant. `war_instances_by_leader` and `war_instances_by_participant` are dirty-flag per-turn caches: mutations mark them dirty, the next reader rebuilds them once from active `war_instances`, and additional reads in the same turn phase reuse the rebuilt index.

### 17.4 Compatibility

- Keep `war_scores`, `battle_records`, `decisive_battles`, `war_start_turns`, `war_objectives`
- Do not migrate or delete existing pairwise structures
- Build the new layer on top of them
- `objective_keys` are historical references. Readers must tolerate missing `world.war_objectives[key]` records after WPS cleanup.
- Battle-record readers must adapt old single-attacker/single-defender records using section 9.6.
- `war_contribution_scores` is the canonical settlement contribution store. Raw `battle_records` may be pruned on their existing schedule without changing stored contribution totals; contribution cleanup follows the active/terminal/archive retention rule in section 17.1.

### 17.5 Turn lifecycle placement

Settlement adds no broad region scan to `advance_turn()`. The settlement-specific turn work runs in this order relative to existing diplomacy processing:

1. Resolve battle, occupation, subsidy/support, and treaty-ratification events for the turn; accrue battle/support/occupation contribution into `war_contribution_scores` as events fire.
2. Apply war-state changes: declarations, direct ally entries, cascade joins, armistice collapse/resolution, eliminations, separate peaces, common-peace ratification, region ownership/alignment mutation, `diplo_key_meta[pair]["pair_status"]` updates, and participant `exited_turn` stamps.
3. Run WB-B fulfillment/breach/void checks for ratified peace and separate-peace fallout.
4. Accrue staying-power contribution by iterating active `war_instance` participants only.
5. Recompute active war leaders and end/archive `war_instances` whose section 7.3 end condition is met. `ARMISTICE` pairs remain suspended in the active instance and do not satisfy the archive condition. When an ended instance leaves the 10-turn retention window, compact or archive its `war_contribution_scores[war_id]` according to section 17.1 after all settlement readers for the turn have consumed it.
6. Invalidate Balance of Europe / bloc caches and war-instance lookup caches, then fire any threshold checks caused by the war-state, treaty, or ownership changes above. If common-peace ratification changed participants or pair status, `war_instances_by_participant` must be rebuilt before cross-war reactions read it.
7. Read active `settlement_memories` for acceptance modifiers, war-entry previews, ledger rows, and dispatch payloads.
8. Remove expired transient `settlement_memories`; do not mutate `betrayal_history` grievance flags during this cleanup.
9. Build campaign log, dispatch, notification, and ledger payloads.

The ordering preserves same-turn contribution credit before exits, keeps bargain lifecycle decisions adjacent to treaty mutation, and ensures memory cleanup cannot erase a modifier before that turn's readers consume it.

---

## 18. Implementation Sequence

This sequence is post-Peace-Deals. All Peace Deals dependencies (BPH, WPS, WB) are landed.

The executable slice plan lives in `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`. If this overview and the plan disagree, the implementation plan owns file-level order, test allocation, and gate criteria; this spec owns mechanic intent and formulas.

### Slice A: War identity + read-only grouping

- **A1 foundation first:** add the mapped-nation capital helper, `next_war_instance_id`, `war_instances`, and `archived_war_instances` containers, old-save defaults, empty `war_instances_by_leader` / `war_instances_by_participant` cache helpers, and cache invalidation hooks. A1 may allocate/test monotonic ids and empty indexes, but it must not start behavioral common-peace scoring.
- **A2 war-entry threading:** create skeleton `war_instance` before `_process_war_cascade()`; allocate `war_id` from `next_war_instance_id`; pass `war_id` through the existing recursive cascade / vassal-entry / ally-entry paths and append resolved participants as they join. If this raises the live `_process_war_cascade(...)` parameter count, update every call site and test the signature explicitly rather than relying on the old 9-parameter note.
- Attach every direct transition into `WAR` to a `war_instance`, including `resolve_join_opportunity()`, `accept_counter_bargain()`, vassal-release rebellion, armistice collapse, scripted/debug war entry, and combat-triggered auto-war paths that bypass cascade
- Store active pairwise war ownership in `active_diplo_keys`, `resolved_diplo_keys`, and `diplo_key_meta`; keep `objective_keys` as WPS historical references only
- Add `diplo_key_meta[pair]["pair_status"] = "war" | "armistice" | "resolved"` and ensure ARMISTICE pairs stay in the same active `war_id` until they resume war or resolve to peace
- Before any treaty path calls `cleanup_war_end()` for a pair, including forced-alliance ratification, snapshot or attach the pair's war-instance data first so battle records, war scores, start turns, objective references, and contribution linkage are not lost before archival.
- Enforce one-active-`war_instance` per `diplo_key`; reuse compatible instances and merge same-declaration instances rather than creating overlaps
- Preserve per-originator/per-covered-enemy objective context when multiple wars merge; do not select one dominant merged objective
- Add side leaders, `war_leader_score()` leader replacement, `participant_meta`, active episodes, re-entry episodes, elimination exits, and WPS `war_objectives` key references
- Wire War Bargain `war_id` attachment at join_opportunity
- Expose participant lists in war status panel and debug endpoints
- Serialization: `to_dict` / `from_dict` round-trip for `war_instances` and `archived_war_instances`; update `SAVE_FORMAT_REFERENCE.md`
- Synthetic full-Europe fixtures cover at least 13 nations and a 6+ participant side even before the live map grows past 19 regions
- A1/A2/A3 gates total ~44-50 tests; A3 merge work must not start until A2 proves every direct and cascade-created `WAR` pair owns exactly one active `war_id`
- A1 must pass its foundation gate before A2 begins. The gate includes old-save defaults, mapped capital helper safety, Britain current-map home-region behavior, absent-future-nation exclusion, empty index build/invalidation safety, and monotonic id allocation.

### Slice B: Contribution tracker

- Add episode-scoped `war_contribution_scores` field with `current_episode_id`, `episodes`, and `historical_total`
- Add theater-level battle attribution (`battle_region`, `attacker_participants`, `defender_participants`, `nation_theater_strength`, `war_id`) at `backend/commands/combat_executor.py` battle-emission call sites and the canonical `backend/game_logic/diplomacy.py::record_battle()` writer; inventory the central `_post_combat_pipeline()` caller, the inline `_execute_attack()` diplomatic battle record path that calls the pipeline with `skip_diplo_record=True`, and the auto-dispatch charge path in `backend/models/world_state.py`. `_execute_glorious_charge()` already routes through `_post_combat_pipeline()` and must be covered as a pipeline call-site fixture, not listed as a non-pipeline path. Route non-pipeline emitters through the same theater-attribution helper or add equivalent participant detection; add old-record adapter
- Add optional `campaign_theater_id` / front-group attribution when full-Europe map metadata exists; the one-hop rule remains the baseline and whole-war credit remains forbidden
- Audit the existing advance-turn pipeline before wiring exits: battle, occupation, support, and treaty-ratification contribution must occur before elimination, AI separate-peace, common-peace ratification, or other exits stamp `exited_turn`
- Wire contribution accrual: battle and occupation event-driven, support event-driven, staying power per active participant episode turn, with episode turn-range filtering
- Add support contribution from recorded gold / subsidy / AP / manpower support, including British coalition subsidy with deterministic `war_id` attribution and treaty-clause transfers from `WorldState._ratify_treaty()`
- Cap access/supply support per `(war_id, supporter, support_kind)` across the whole war instance; re-entry does not reset the cap
- Add material-contribution gate so staying power alone cannot trigger `seat`, threshold dispatches, or major shut-out grievances
- Add contribution threshold dispatch signals at 15% and 25% with material contribution required
- Derive contribution shares at query time
- Standing classification: `classify_standing()` with rule-based bucket assignment, secondary co-belligerent floor, and late-joiner rules
- Serialization: `to_dict` / `from_dict` round-trip for `war_contribution_scores`; update `SAVE_FORMAT_REFERENCE.md`
- Synthetic contribution fixtures cover support-only Britain/major-power participation, a 6+ participant side, a 3-theater war, and late join / exit / re-entry episodes
- Split Slice B into mandatory B1/B2/B3 gates so no single implementation session owns the full contribution tracker:
  - **B1 contribution store and standing math:** data model, canonical store, save/load defaults, old-record adapter, current-episode model, standing classification, material-contribution gate, contribution-share query helpers. 18-22 tests.
  - **B2 event emitters and theater attribution:** battle, occupation, support, treaty-support, British subsidy, sub-1000 battle contribution, `_execute_attack()` inline diplo records, auto-dispatch charge records, and the glorious-charge pipeline fixture. 20-24 tests.
  - **B3 lifecycle, retention, and full-Europe fixtures:** turn-order/exits, same-turn separate peace, archive compaction, concurrent-war independence, contribution threshold signals, and three-theater / support-only major fixtures. 18-22 tests.

### Slice C: Common peace plumbing + territory legitimacy

- Add `Open settlement` entry point (separate from bilateral wizard)
- One-package term builder grouped by target enemy
- Ally beneficiary fields on `territory_cede`
- Territory demand legitimacy evaluation
- Common peace acceptance formula (opposing war leader)
- `side_pressure_score` weighted average as headline/base component only
- Common-peace pair resolution iterates `active_diplo_keys` and resolves only pairs between proposer-side participants and covered enemy participants; covered forced-alliance outcomes must use the existing WPS state-jump path instead of a generic PEACE write
- Per-target direct-score gates and burdened non-leader penalties
- Rejection feedback identifying the top 1-2 objectionable terms or acceptance components
- Rival-strengthened / local balance warning input
- `abandoned_by_ally_acceptance_mod`: `+5` per same-side enemy separate peace in the last 3 turns, capped at `+15`
- Projected post-settlement hegemony modifier via `project_balance_after_settlement(...)`
- Defender-side common-peace symmetry through `proposer_side`
- Endpoint and dialogue contracts for no-terms `GET /diplomatic_preview`, draft-terms `POST /diplomatic_preview`, `settlement_confirm`, `confirm`, `back_out`, and `revise_terms`
- Mandatory `settlement_confirm` before any common-peace ratification; `confirm` revalidates live leaders, terms, hard stops, and acceptance
- Verify and extend the already-registered `settlement_confirm` hard-stop dialogue type with proposer-leader-change voiding and accepting-leader-change rescoring
- Register `incoming_settlement_offer` as a current-turn offer / mailbox dialogue, not a hard stop; accepting it promotes to `settlement_confirm` and does not mutate until the confirm executor succeeds
- Add `DialogueManager.DIALOGUE_PRIORITY["incoming_settlement_offer"]` at the normal incoming-proposal tier and `DialogueManager.MAILBOX_SUMMARY_LABELS["incoming_settlement_offer"] = "Incoming settlement offer"` with backend/Godot mailbox tests so settlement offers do not inherit generic proposal ordering or labeling
- Keep common-peace AI cooldowns in a per-`war_id` namespace separate from bilateral proposal cooldowns
- Mandatory Slice C tuning gate for common-peace constants using at least eleven deterministic examples plus side-pressure monotonicity before implementation lock; include mixed-strength partial-vs-full coverage, narrow-vs-full-vs-serial settlement incentive comparison, total-victory harsh terms, Britain-led defense with current mapped holdings/home-region scoring, cross-formula acceptance validation, and acceptance debug components; start from `base_side_pressure` scaling `0.65` and the `1.5` harshness ceiling
- Talleyrand advisory preview: standing, bargains, territory legitimacy, rival-strengthened warnings, ally-fallout warnings, salience-filtered default rows
- Split Slice C into two mandatory sub-slices:
  - **C1 backend scoring/legitimacy:** `compute_side_pressure_score`, common-peace acceptance, tuning fixtures, monotonicity, multi-objective alignment selection, projected hegemony, abandoned-ally modifier, territory normalization, direct-score gates, pressure-basis warnings, defender-side symmetry, partial common-peace scoring
  - **C2 endpoint/dialogue/advisory/Godot routing:** settlement preview endpoints, `settlement_confirm` response contract, confirm/back-out/revise handling, pair-specific treaty-state resolution, leader-change void/rescore, two-pass standing, AI-to-player settlement review, advisory payloads, Godot settlement review and smoke
- Godot smoke gate after C2: launch the client, open the settlement review from a synthetic payload, verify `settlement_confirm` blocks ordinary commands, then back out/revise without mutation
- Manual comprehension gate before D1: run a complete common-peace settlement review with at least 4 participants. Within roughly 30 seconds, the reviewer must be able to identify the top blocker or political cost, the main affected ally/enemy, and the available next action (`confirm`, `revise_terms`, `back_out`, `accept`, `reject`, or `request_revision`). If the reviewer cannot do that from the default view, reduce UI payload density, copy, or section ordering before starting D1 reaction work.
- ~60 tests split across C1/C2

### Slice D1: Settlement memories and direct reactions

- Post-ratification reaction pass for both sides
- `settlement_shut_out` grievance flag on existing `betrayal_history` using the live `_add_grievance_flag(..., source_episode_type="settlement_reaction")` signature
- `settlement_gratitude`, `sold_out_by_war_leader`, and `settlement_context` records in `settlement_memories`
- `settlement_gratitude_mod` acceptance hook for subsequent deep-treaty, war-entry, and war-bargain / ally-entry proposals
- Zero-material major-power severity reduction
- Serial bilateral settlement fallout for third-plus separate peaces in one war instance within five turns
- Sold-out-by-leader posture gate for deep treaties and war-entry asks from the former leader
- Settlement-memory cleanup removes expired transient records
- `they_chose_us` upside for rewarded allies with subsequent acceptance bonus
- Serialization: `to_dict` / `from_dict` round-trip for `settlement_memories`; update `SAVE_FORMAT_REFERENCE.md`
- ~24-30 tests

### Slice D2: Bargain integration and cross-war reactions

- Wire war bargain fulfillment/breach at settlement through existing WB-B pipeline
- Separate peace fallout: smaller reaction pass for remaining co-belligerents
- Cross-war affected-participant reaction check evaluates all directly affected active wars, then bounds only secondary adjacency/sphere scans to at most three related active `war_instances`
- Cross-war affected-participant reaction check uses `war_instances_by_participant`; do not filter all active war instances repeatedly inside the reaction pass
- Competing ally-claim reactions for regions with multiple interested same-side participants
- Combined separate-peace relation impact documents BPH-C base penalty plus settlement shut-out penalty; settlement reaction does not duplicate BPH-C
- WB-B fulfillment/breach timing runs in the same turn-end lifecycle pass after treaty ratification
- Sold-out-by-leader Tilsit threshold for material losses only
- Hegemony/threat reaction through existing add_threat/reduce_threat/bloc invalidation seams
- ~28-34 tests

### Slice E: Presentation + ledger

- Settlement warnings in proposal preview
- War status panel: contribution shares, standing levels
- Separate settlement route metadata for settlement event families
- Dispatch: top 4 settlement beats plus digest overflow
- Notification rail: major settlement events (bargain fulfilled, major shut-out, promise breach)
- Named diplomat voice for settlement reactions (per Voice Bible), including explicit key families for `settlement_advisory_common_peace_*`, `settlement_advisory_defensive_*`, `settlement_acceptance_*`, `settlement_rejection_*`, `settlement_sold_out_by_leader_*`, `settlement_rewarded_ally_*`, and `settlement_excluded_ally_*`
- Ledger: post-settlement records
- Common-peace rejection preview shows top objectionable terms
- War Bargain / ally-beneficiary copy separates "Bargain: France secures {claim} (FULFILLED)" from "Settlement: {region} awarded to {ally} (REWARD)" so players understand France-claim fulfillment and ally rewards are separate mechanics.
- "View all participants" advisory overflow
- WARNING and HARD_STOP advisory rows surface regardless of the default participant-row cap
- Settlement review separates Terms, Allies, Warnings, and Acceptance sections so full-Europe payloads do not collapse into one dense advisory list
- Split Slice E into E1 backend presentation payloads and E2 Godot rendering if the Godot surface grows beyond the slice gate
- Godot smoke gate after E2: settlement review, war status rows, notification route, and ledger route render on current 19-region data plus a synthetic 6+ participant full-Europe payload with no overlapping text, scroll/overflow controls intact, and at least two defensive-settlement copy fixtures
- ~40 tests

**Estimated total: ~275 tests across A1/A2/A3, B, C1/C2, D1/D2, and E.** Slice boundaries are implementation gates: each slice owns its data fields, serialization/defaults, save-format documentation, focused backend tests, synthetic full-Europe fixtures, and any UI payload tests listed above.

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
18. Settlement reaction pass fires for both proposer-side and enemy-side participants.
19. Imperial-looking settlement uses existing threat/bloc seams and emits `balance_of_europe_shifted` only on threshold crossing or hegemon swap.
20. Dormant war bargains remain dormant through settlement; do not block peace.
21. Contribution threshold signals fire once at 15% and 25%, and do not create popups.
22. Old-format battle records adapt to single-participant contribution records.
23. Enemy ally sold out by its own leader receives relation damage toward both France and that leader.
24. Rewarded high-standing ally with current-episode material contribution receives `settlement_gratitude` subsequent acceptance bonus and cap/refresh behavior; zero-material beneficiary rewards do not create the reusable modifier.
25. Staying-power-only contribution never triggers `seat`, threshold dispatches, or major shut-out grievance.
26. Secondary co-belligerent with material contribution receives at least `consult` even in an 8-participant coalition.
27. `rival_strengthened` warning fires when a settlement strengthens a rival on an affected nation's border.
28. Theater-level battle attribution credits nations with marshals in or adjacent to the battle region by theater strength.
29. Late joiner contribution counts from `joined_turn`; decisive post-join battle credit is not reduced.
30. Common-peace rejection identifies the top 1-2 objectionable terms or acceptance components.
31. Cross-war settlement consequence check evaluates active participants in other `war_instances` when terms affect their interests.
32. Settlement presentation emits at most 4 primary dispatch beats plus one digest overflow line.
33. `sold_out_by_war_leader` fires only for material losses, not minor gold/manpower/AP costs.
34. `abandoned_by_ally_acceptance_mod` uses `+5`, a 3-turn window, and a flat `+15` cap.
35. `war_instances`, `archived_war_instances`, `war_contribution_scores`, and `settlement_memories` save/load with old-save defaults.
36. `settlement_shut_out` uses existing grievance flag shape and stores rich context in `settlement_memories`.
37. Common-peace `projected_hegemony_mod` uses projected post-settlement bloc share, not current bloc share, and is distinct from bilateral `hegemony_target_mod`.
38. A `diplo_key` cannot appear in more than one active `war_instance`.
39. Mid-war elimination exits the participant, freezes contribution, and triggers leader replacement without a separate-peace reaction pass.
40. Re-entry contribution filters battle/support records by active episode turn range.
41. Non-coalition war leader replacement uses `war_leader_score()`, not coalition-target-specific scoring, and defender-side replacement uses the defender `origin_target` as the same-side relation anchor.
42. Common peace with one covered enemy is valid when ally-beneficiary terms or war-level standing logic is present.
43. Defender-side common peace uses `proposer_side` and scores attackers as covered enemies.
44. `rival_strengthened` alone does not promote a minor with no material contribution to consult standing.
45. Material-contribution participants receive at least `beneficiary_only` standing.
46. WARNING and HARD_STOP advisory concerns surface even when more than five allies have standing rows.
47. British coalition subsidy emits `war_support_delivered` with `source="coalition_subsidy"` and deterministic `war_id` attribution, including a multi-war recipient tie-break fixture.
48. Access/supply support is capped per `(war_id, supporter, support_kind)` across the whole war instance.
49. `settlement_memories` cleanup removes expired records after active modifiers are read.
50. `objective_keys` readers handle missing WPS objective records after cleanup.
51. `combat_executor.py` field/garrison battle call sites and `diplomacy.py::record_battle()` include theater attribution for the canonical long-term record.
52. AI common-peace proposals and acceptance use the same executor, validation, and WB settlement lifecycle as the player.
53. `next_war_instance_id` allocates unique war IDs for same-turn declarations and survives save/load.
54. Active pair keys live in `active_diplo_keys` / `resolved_diplo_keys`, while `objective_keys` remain WPS historical references only.
55. Mutating common-peace commands stage `settlement_confirm`; `confirm` revalidates live leaders and terms before ratification.
56. `settlement_gratitude_mod` applies only to eligible subsequent proposals from material-contribution-gated memories and refreshes rather than stacks.
57. Slice C deterministic acceptance examples meet the decisive-victory, total-victory harsh-terms, and mixed-strength partial-vs-full coverage tuning gates.
58. Transitive merge of three compatible `war_instances` keeps the oldest `war_id`, rewrites absorbed `war_id` references, and hard-stops on side conflicts.
59. `settlement_confirm` voids if the proposer-side leader changes and rescoring occurs if only the accepting-side leader changes.
60. Zero-contribution active major still receives `seat` standing.
61. Occupation contribution is attributed by `war_occupation_event.actor_nation`.
62. Cross-war reaction checks inspect every directly affected non-settling active `war_instance` and no more than three secondary adjacency/sphere-only active `war_instances`.
63. AI common peace stages the same internal confirm payload and cannot bypass confirm validation.
64. Partial common peace resolves only covered enemies and leaves uncovered hostile pairs active in the same `war_instance`.
65. Draft settlement preview with `POST /diplomatic_preview` accepts `settlement_terms` and performs no mutation.
66. Battle contribution persists from `war_contribution_scores` even after raw `battle_records` pruning.
67. Same-turn battle contribution is credited before elimination or separate-peace `exited_turn` stamping.
68. AI-to-player common-peace offers create an incoming settlement review instead of immediate ratification.
69. Slice C acceptance score is monotonic with increasing `side_pressure_score` when all other components are fixed.
70. Synthetic full-Europe fixtures cover at least 13 nations, 100+ region ids for territory logic, 20 active pair keys, 6+ participants on one side, and explicit mapped/scenario data for every evaluated participant.
71. `settlement_confirm` hard-stop registration is verified in backend and Godot before adding new routing behavior.
72. Godot settlement smoke gates pass after Slice C2 and Slice E2.
73. ARMISTICE pairs remain in the same `war_instance`, pause as suspended pairs, and reuse the same `war_id` if hostilities resume.
74. Common peace resolves covered pairs to `PEACE` or treaty states, never to `ARMISTICE`.
75. Direct WAR-entry paths that bypass cascade (`resolve_join_opportunity`, `accept_counter_bargain`, vassal-release rebellion, armistice collapse, scripted/debug war entry) attach to an existing or new `war_instance`.
76. `settlement_confirm` dialogue responses use the typed confirm/back-out/revise contract and return no-mutation responses on rejection, void, back-out, and revise.
77. The Pressburg-style worked example is pinned as a deterministic Slice C fixture, and the tuning gate records any chosen primary balance knob.
78. AI-vs-AI common peace emits one fog-eligible dispatch line and one `settlement_summary` campaign-log entry without participant spam.
79. Open Settlement is enabled only for active side leaders with unresolved hostile or suspended pairs and at least one coverable enemy; grey-out reasons use the section 10.3 enum.
80. A nation active in two concurrent `war_instance` records accrues staying-power and support contribution independently per `war_id`.
81. `classify_bargain_settlement_status()` returns `fulfilled_by_terms`, `at_risk`, `impossible`, and `breach_if_confirmed` deterministically for active settlement drafts, with named-enemy coverage distinguishing `dormant` from `at_risk`.
82. AI common-peace offers obey one-active-offer, one-new-offer-per-turn, and per-`war_id` 3-turn cooldown rules without consuming bilateral proposal cooldowns.
83. `settlement_summary` route metadata, one-liner, and fog filtering match the section 11 Step 6 event contract.
84. Treaty-clause support emitted from `WorldState._ratify_treaty()` accrues contribution without requiring a nonexistent diplomacy-module `_ratify_treaty()` hook.
85. Competing ally claims on the same region produce recipient gratitude and non-recipient warnings/grievances only under the section 13.4 standing, bargain, direct-stake, or material-contribution gates.
86. Cross-war settlement grievance flags feed subsequent bilateral acceptance through the existing `grievance_modifier` path, not a parallel cross-war modifier.
87. `classify_bargain_settlement_status()` is pure: advisory and confirmation calls do not mutate bargains, treaties, memories, logs, dispatch, or dialogue queues.
88. Settlement review renders separate Terms, Allies, Warnings, and Acceptance sections on a synthetic 6+ participant payload with no overlapping text.
89. Sub-1000-casualty battles with valid theater participants accrue settlement contribution without adding pairwise war-score battle points.
90. Burdened-participant penalties cap at `-30` for one burdened non-leader and `-60` for two or more, so distributed sellouts are not cheaper per ally.
91. Defender-side settlements cover contribution, standing, sold-out reactions, acceptance worked example, and defensive Talleyrand advisory copy when `proposer_side == defenders`.
92. Three or more separate peaces in one `war_instance` within five turns trigger the serial bilateral settlement fallout path.
93. Material contribution share, not total contribution share including staying power, controls `seat`, `consult`, contribution-threshold dispatch, and major shut-out grievance eligibility.
94. A zero-material `major` with no direct stake receives a consultation warning but not full major shut-out grievance severity.
95. Recurring treaty support from `_process_treaty_clauses()` emits `war_support_delivered` as each payment is applied.
96. Zero-region accepting leaders do not receive the `+5` leader-owns-no-losses bonus, and mapped holdings apply a loss penalty only when the package permanently cedes, forced-aligns, or recognizes the loss.
97. `active_pair_changed` revalidation catches armistice expiry or pair resolution before `settlement_confirm.confirm` mutates state.
98. Competing-claim warnings name each claimant's basis: bargain, occupation, restoration, former ownership, local sphere, or contribution.
99. `sold_out_by_war_leader` memory creates a temporary hard-reject posture toward deep treaties and war-entry asks from the former leader unless redress or high relation exists.
100. Merged war instances preserve multiple proposer-side objectives and `war_objective_alignment` names the selected objective context instead of using a single merged objective.
101. Contribution standing after a merge uses post-merge current-episode side totals; pre-merge shares are display-only history.
102. Common-peace ratification resolves every active hostile pair between proposer-side participants and covered enemies, leaves uncovered pairs active, and applies forced-alliance state outcomes through the WPS path.
103. Cross-war reaction lookup uses `war_instances_by_participant` and does not repeatedly filter all active wars for each affected nation.
104. Slice C compares narrow common peace, full common peace, and serial separate settlements to prove common peace is not mechanically dominated by serial settlements after decisive wins.
105. A 6-participant / 3-theater contribution fixture proves distant-front participants earn contribution from their own theater events without receiving whole-war battle credit.
106. AI common-peace offers are generated only when a concrete package passes the accepting side's common-peace acceptance check; losing-side white-peace spam is rejected before surfacing.
107. Same-turn AI separate peace and battle contribution ordering preserves that turn's contribution before `exited_turn` is stamped.
108. Bargain classifier returns `impossible` when a claim region is controlled by a third party or same-side ally and no legal settlement term can transfer it to France.
109. Britain fixtures cover current mapped home-region behavior, subsidy-only major auto-seat copy, and holding cession/restoration scoring.
110. Live-code Britain fixture proves `NATION_CAPITALS["Britain"] == "Netherlands"` is treated as the current-map configured home/spawn region and can later be replaced by normal scenario data without creating a separate settlement identity.
111. Common-peace harshness tests prove Slice C uses raw treaty harshness from `diplomatic_templates.py` while existing bilateral callers keep the 1.0-clamped `calculate_treaty_harshness()` behavior.
112. Multi-forced-alliance common-peace preview aggregates `+30` or greater projected threat, names crossed coalition thresholds, and confirmation still emits per-clause `forced_alliance` threat through existing seams.
113. Combined posture-gate tests prove `sold_out_by_war_leader` and `anti_renewal_cooldown` list both blockers, use the max effective unblock turn, and allow redress to bypass only the sold-out gate.
114. AI defender common-peace fixture proves packages with only a `defense` objective and `war_objective_alignment <= +5` can still pass or fail on the full acceptance formula rather than objective alignment alone.
115. `incoming_settlement_offer` has its own dialogue priority, mailbox summary label, and Godot mailbox route.
116. `material_contribution_share` defaults to `0` when total material contribution is zero even if staying-power contribution is positive.
117. `settlement_confirm.confirm` rejects proposer-side participant exits, rebellions, eliminations, and beneficiary invalidation without mutation.
118. Side-scoped `leader_source_by_side` tests prove coalition leadership scoring cannot leak from one side to the other.
119. `leader_own_losses` clamps after summing sub-components, normal non-leader burden is a `0` penalty, and `war_objective_alignment` covers the `-15` unrelated-harsh-terms case.
120. Full-pipeline stress fixture runs two AI-generated settlements, 20 active wars, and all 13 canonical DG-1 nations in one `advance_turn()` evaluation.

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

When France leads a defensive settlement, "dictates" means France owns the final player choice, not that the copy should sound like conquest. Defensive-coalition presentation should foreground coalition preservation, allied claims, and exhaustion rather than imperial overreach.

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

- **April 30, 2026 - v1.22 synthesis hardening.** Added the final Codex/Claude synthesis follow-ups before coding: common-peace tuning now has an explicit escalation order for the narrow/full/serial incentive risk, `common_peace_coverage_bonus` is last-resort and anti-farming-gated, C2 must pass a manual 4+ participant settlement-review comprehension gate before D1 starts, and A3 merge transactions must run an always-on post-merge `assert_war_instance_invariants(...)` check for pair ownership, absorbed `war_id` references, and side-map consistency. The companion implementation plan is v1.19.
- **April 29, 2026 - v1.21 mapped-foundation readiness closure.** Closed the full-Europe scale-readiness audit follow-ups: synthetic fixture helpers must extend the active roster before adding future-nation regions/controllers, A1 cache fixtures must prove 20 active `war_instance` records before A1 closes, C2 owns serialized `ai_settlement_cooldowns` and `pending_settlement_dialogues`, dialogue overflow retries are deterministic and bounded, and already-landed settlement helper/dialogue scaffolding is marked for verification rather than re-addition. The companion implementation plan is v1.18.
- **April 29, 2026 - v1.20 future-nation onboarding hardening.** Made the settlement layer explicitly incremental for future nations: production code must consume scenario/map/config data instead of hard-coding the 13-nation stress roster, `docs/ADDING_CONTENT.md#adding-new-nations` is now the operational gate for new settlement-capable nations, and each new production nation must add a focused settlement readiness fixture covering internal ids, mapped capital/home, explicit `power_tier`, pair keys, `war_instance` participation, desire/profile fallback behavior, and save/load id stability. The companion implementation plan is v1.17.
- **April 29, 2026 - v1.19 mapped-scope audit hardening.** Reconciled the final Codex/Claude full-Europe readiness pass around the mapped-nation contract: added explicit 20-active-`war_instance` cache fixture coverage, late-join-versus-merge wording for coalition entrants, side-pressure source/dilution tuning fixtures, v1 battle-contribution fallback when per-nation casualty exposure is absent, the burdened-non-leader-only acceptance note, territory-demand cost floor, rolling 5-turn serial separate-peace lookback, and common-peace snapshot-before-cleanup ratification ordering. Older changelog references to separate nation requirements are superseded by the current mapped-nation contract.
- **April 29, 2026 - v1.18 mapped-nation A1 simplification.** Replaced the pre-A1 separate Britain/Russia requirement with a mapped-nation settlement contract: A1 now adds capital-helper safety, settlement containers, old-save defaults, empty index/cache scaffolding, and cache invalidation hooks, while absent future nations such as Russia stay out of settlement until scenario/map data adds them. Britain is treated as a current mapped participant using its configured current-map home/spawn region. Added the pair-key convention table, deterministic war-leader tie-break, per-nation shared war-exhaustion note, forced-alliance/`cleanup_war_end()` archival warning, dirty-flag war-instance index policy, bargain leader-context snapshots, full-Europe harshness calibration, dialogue overflow protection, and aligned common-peace ratification ordering so caches rebuild before settlement/cross-war reactions.
- **April 29, 2026 - v1.17 pre-A1 foundation gate closure.** Captured the Codex/Claude readiness synthesis as executable process gates before coding starts: A1 is now explicitly foundation-only and must land mapped-capital helper APIs, `WorldState` settlement containers, old-save defaults, empty index/cache scaffolding, and normal mapped-nation elimination behavior before behavioral settlement work; A2 owns `war_id` threading through declaration/cascade/direct-entry seams; B owns sub-1000 contribution accrual before the war-score gate; C owns raw treaty harshness plus `incoming_settlement_offer` priority/label taxonomy; D owns common-peace ratification cache ordering and cross-war reaction reads from fresh participant indexes.
- **April 29, 2026 - v1.16 full-Europe audit synthesis closure.** Folded Run 3 and the cross-audit findings into the handoff: side-scoped `leader_source_by_side`, a material-share zero-denominator guard, mapped-nation elimination behavior, proposer-side participant and beneficiary revalidation on settlement confirm, corrected Slice B battle call-site inventory, per-war-instance access/supply caps, war-instance cache invalidation timing, territory-legitimacy direct-score memoization, explicit acceptance-math edge cases, and final full-pipeline stress fixtures.
- **April 29, 2026 - v1.15 full-Europe audit closure.** Reconciled the full-Europe settlement pass with canonical DG-1 fixture ids, mapped Britain/Russia fixture coverage, plan/source routing, and full-map settlement scale assumptions before Slice A1 coding.
- **April 29, 2026 - v1.14 codebase synthesis closure.** Folded the latest Claude/Codex codebase findings into the handoff: settlement capital scoring now treats live `NATION_CAPITALS["Britain"] = "Netherlands"` as a proxy holding, not a true capital; Slice C explicitly owns a raw treaty-harshness helper in `diplomatic_templates.py` while preserving bilateral 1.0-clamped callers; common-peace preview must aggregate uncapped per-clause forced-alliance threat and name crossed coalition thresholds; stacked sold-out / anti-renewal / hard-posture gates now have precedence and bypass rules; and AI defender common-peace tuning must work when WPS objective alignment is only `defense`.
- **April 29, 2026 - v1.13 full-Europe audit reconciliation closure.** Folded the latest Codex/Claude synthesis into the handoff: merged wars now preserve per-originator objective contexts, post-merge contribution standing uses the merged denominator, common-peace ratification resolves exact covered proposer-side/enemy pair keys and honors forced-alliance state jumps, cross-war reactions require `war_instances_by_participant`, Slice C gains narrow/full/serial incentive fixtures and AI package-acceptance construction, Slice B gains turn-pipeline and three-theater contribution tests, Britain fixtures are explicit, WB classifier `impossible` covers third-party/same-side claim controllers, Slice A gates are split, and Slice E copy/UI density gates name defensive and settlement voice families.
- **April 29, 2026 - v1.12 Claude reconciliation closure.** Reconciled Claude's final formula/integration audit with the Codex audit: locked `base_side_pressure` at `0.65` / `[-50, 60]`, normalized common-peace harshness over raw `1.5`, added explicit war-objective alignment mapping for all five WPS objective types, required a Britain-led defense fixture, gated reusable `settlement_gratitude` on current-episode material contribution, identified non-pipeline battle-record call sites for Slice B, called out `vassal.py` and armistice expiration `war_id` threading in Slice A, added turn-lifecycle bloc-cache invalidation, and added War Bargain vs ally-beneficiary copy separation.
- **April 29, 2026 - v1.11 audit synthesis closure.** Closed the follow-up Codex/Claude merged audit: battle contribution now explicitly bypasses the pairwise war-score 1000-casualty gate, burdened-participant penalty caps scale to two burdened non-leaders, Pressburg tuning starts at `0.65`, defender-side coverage expands, serial separate-peace fallout is specified, common-peace formulas get cross-validation tests, zero-material major-power severity is reduced, recurring treaty support emits from `_process_treaty_clauses()`, `settlement_confirm` revalidates pair status with `active_pair_changed`, pre-declaration side-conflict validation is explicit, mapped-home leader-loss scoring is fixed, projected-hegemony floor asymmetry is documented, sold-out-by-leader memory has a posture consequence, competing-claim warnings name claim basis, and Slice D is split into D1/D2.

- **April 28, 2026 - v1.10 full-Europe synthesis closure.** Closed the follow-up Codex/Claude full-map audit: replaced `relation_to_originator_bias` with same-side `relation_to_side_anchor_bias`, documented no neutral mediation and no Congress-style multipolar settlement in this phase, added mixed-strength partial-vs-full coverage and total-victory harsh-terms tuning fixtures, required common-peace acceptance debug components, changed cross-war reactions to inspect all directly affected wars before capping secondary scans, clarified grievance routing through existing `grievance_modifier`, added competing ally-claim reactions, made `classify_bargain_settlement_status()` explicitly pure, required Terms / Allies / Warnings / Acceptance settlement review sections, and raised the handoff estimate to ~260 tests.
- **April 28, 2026 - v1.9 handoff precision closure.** Closed the post-synthesis implementation-seam audit: corrected the canonical battle writer to `diplomacy.py::record_battle()`, moved treaty-clause support emission to `WorldState._ratify_treaty()`, made cascade `war_id` threading an explicit 9-parameter recursive risk, defined `relation_to_originator_bias`, separated `incoming_settlement_offer` as a current-turn mailbox offer, clarified common-peace cooldown namespace, fixed bargain `dormant` vs `at_risk`, added contribution retention/compaction rules, and expanded synthetic full-Europe fixture requirements.
- **April 28, 2026 - v1.8 synthesis closure.** Folded the Codex/Claude full-audit synthesis into the handoff: added explicit ARMISTICE pair-status lifecycle inside `war_instance`, locked common peace to PEACE/treaty outcomes rather than armistice, required all direct WAR-entry paths to attach to a `war_instance`, added concrete `settlement_confirm` dialogue response contracts, pinned a Pressburg-style worked acceptance example, made the Slice C tuning gate mandatory with `0.6` side-pressure scaling as the first adjustment knob, required the C1/C2 split, added AI-vs-AI settlement dispatch/log visibility, documented transitive merge as a rare correctness transaction, and made settlement-memory cleanup/archive retention deterministic for save/load.
- **April 28, 2026 - v1.8 audit synthesis patch.** Closed the Codex/Claude merged audit clarifications without changing architecture: Open Settlement eligibility and grey-out reasons, same-side beneficiary eligibility beyond formal allies, deterministic bargain settlement status classification, incoming AI settlement offer contract and anti-spam, `settlement_summary` event/route/fog contract, warning cap wording, concurrent-war contribution semantics, and matching full-Europe tests.
- **April 28, 2026 - v1.7 final audit closure.** Closed the remaining Codex/Claude synthesis gaps: reconciled DIPLOMACY acceptance docs with live War Bargain modifiers, added draft `POST /diplomatic_preview`, explicit partial common-peace continuation, event-time contribution vs battle-record pruning, same-turn lifecycle ordering, merge transaction ordering, absent-major shut-out precedence, AI-to-player settlement review routing, expanded Slice C tuning fixtures with monotonicity, synthetic full-Europe fixtures, Slice C split guidance, and Godot smoke gates.
- **April 28, 2026 - v1.6 audit closure.** Synthesized the combined Codex/Claude full-Europe audit after v1.5: added hard-stop `settlement_confirm` taxonomy and leader-change behavior, fixed normalized common-peace harshness math, defined two-pass standing and zero-contribution major-power precedence, made war-instance merge transitive with absorbed-`war_id` rewrites, added explicit WAR-entry creation seams, added occupation contribution events and support-emitter ownership, renamed common-peace `hegemony_pressure` to `projected_hegemony_mod`, bounded cross-war reaction checks to three related wars, made salience ordering deterministic, added layer-50 ownership rules, idempotent settlement-memory writes, AI internal confirm routing, and new tests for the closure cases.
- **April 28, 2026 - v1.5 handoff hardening.** Synthesized Codex and Claude full-Europe audit follow-ups: added unique `next_war_instance_id` allocation, separated active pair-key ownership from historical `objective_keys`, made contribution storage episode-scoped, made `settlement_confirm` mandatory before common-peace ratification, added the `settlement_gratitude_mod` acceptance hook, expanded AI common-peace decision rules, added the Slice C acceptance tuning gate, and aligned the implementation plan/status routing for Slice A handoff.

- **April 28, 2026 - v1.4 full-Europe audit closure.** Reconciled the Imperial Settlement audit with Claude's full-Europe audit: fixed abandoned-ally acceptance constants, required projected hegemony pressure, added war-instance uniqueness / archiving / elimination exits, separated non-coalition leader scoring from coalition scoring, specified episode-range contribution filtering, added combat-executor theater attribution ownership, clarified penalty stacking and rival-strengthened standing guards, added settlement API / dialogue contracts, added AI settlement behavior, tightened cleanup / save-format / warning-priority rules, and expanded the slice plan and tests for 13-20 nation wars.

- **April 28, 2026 - v1.3 full-Europe scale hardening.** Added the implementation-plan handoff, exact common-peace acceptance constants and thresholds, canonical `from` / `to` territory-term ownership, live `location` battle-record compatibility, support-contribution event schema, live-state `rival_strengthened` data source, and one-entry campaign-log aggregation contract for common settlements.

- **April 28, 2026 — v1.2 full-Europe scale synthesis.** Added the explicit 13-20 nation / 50+ region scale contract; added no-unowned-deferrals ownership rule; added mid-war joiner and re-entry rules; changed battle contribution to theater-level attribution; added material-contribution gates, secondary co-belligerent standing floor, support contribution, rival-strengthened local-balance warnings, per-target direct-score gates, common-peace rejection diagnostics, cross-war reaction checks, dispatch/digest caps, Tilsit material threshold, live grievance-flag signature, canonical settlement-memory shape, serialization/save-format ownership, expanded implementation slices to ~200 tests, and expanded testing focus for full-Europe coalition play.

- **April 28, 2026 — v1.1 audit synthesis.** Reconciled the design/system audit findings: protected the "France dictates, allies react" design call; corrected War Bargain settlement fulfillment to the shipped France-claim-scoped WB-B lifecycle; moved settlement shut-out into existing `betrayal_history` grievance flags; added side leaders, sold-out enemy ally reactions, weighted `side_pressure_score`, contribution threshold foreshadowing, battle-record compatibility, performance constraints, separate-peace pressure on remaining enemies, settlement gratitude, separate settlement routing, and expanded the implementation/test budget to ~152 tests.
