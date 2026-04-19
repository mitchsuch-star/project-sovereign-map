# Europe Scale Readiness — Implementation Plan

> Derived from `SCALE_READYNESS.md` audit (April 16, 2026).
> This document replaces the audit's phased roadmap with a concrete, ordered work plan.
> Each item has files to touch, what to change, dependencies, and estimated effort.

---

## How to Use This Document

Work top-to-bottom within each phase unless a phase explicitly declares an internal execution order. Phase 0 (design gates) still governs design-dependent scale work, but Phase 1 was intentionally completed early as low-risk test infrastructure. Within code phases, items are ordered by dependency unless a phase note says otherwise.

**Estimated total effort:** 8-12 focused sessions across all phases.

---

## Phase 0: Design Gates

These are decisions, not code. Each one affects downstream implementation. The Phase 0 decisions are now recorded inline below and define the constraints for later scale work. Phase 1's test safety net was pulled forward safely, but the remaining code phases should follow these gate decisions rather than inventing policy during implementation.

### DG-1. Nation Roster & Starting Situation

**Decision needed:** Which nations ship in EA? How many marshals per nation? What starting diplomatic relationships?

**Why first:** Every other decision (diplomacy model, cascade depth, AP budget, victory conditions) depends on knowing whether this is 8 nations or 15.

**Options to evaluate:**
- **Option A: 8-10 nations** — France, Britain, Prussia, Austria, Russia, Spain, Ottoman Empire, Sweden, plus 1-2 minor (Saxony, Bavaria). Keeps diplomacy manageable.
- **Option B: 12-15 nations** — Add Denmark, Netherlands, Naples, Portugal, Poland. More historically accurate, but diplomacy UI must change.

**Downstream impact:** Determines urgency of bilateral pair explosion fix (CC2), coalition retuning, UI density work.

**DECIDED — April 17, 2026: Current 1805 draft uses 13 independent nations; architecture is not capped there and supports 20+.**

The current France-led 1805 draft scenario uses 13 independent nations in three tiers. That is authored scenario content, not an engine cap. All systems (diplomacy, dispatch, UI, cascade, AI) must be architected to handle 20+ nations so larger maps or later scenarios can grow post-EA without structural rework.

**Tier 1 — Major Powers (5):** France, Britain, Austria, Prussia, Russia. Core antagonists, full marshal rosters, full diplomatic agency.

**Tier 2 — Active Secondary Powers (4):** Spain (French ally → enemy, Peninsular War), Ottoman Empire (eastern tension, Russian pressure), Sweden (Third Coalition, Bernadotte), Naples/Two Sicilies (Italian theater, Murat).

**Tier 3 — Key Minors (4):** Bavaria (France's key German ally, later defection), Saxony (already in-game), Portugal (British ally, invasion target), Denmark-Norway (French ally post-1807).

**As vassals, not independent nations:** Netherlands/Batavian Republic, Poland/Duchy of Warsaw, Württemberg, Switzerland. The existing vassal system handles these — the player creates them through conquest and diplomacy.

**Scale note:** 13 nations = 78 bilateral pairs. Smart filtering (DG-2) keeps this manageable. At 20 nations = 190 pairs — the filtering and dispatch systems (DG-7) must handle this without UI changes.

### Phase 0 Cross-Cutting Taxonomy

**DECIDED — April 17, 2026. Canonicalized — April 17, 2026.**

This section is the canonical source for `power_tier` and related taxonomy. Any older language in other docs is superseded (see "Superseded language" at the bottom of this section).

**`power_tier` — canonical enum**

- Values: `major`, `secondary`, `minor`. No other values are valid. Do not use `great_power`, `secondary_power`, or `minor_power` in new code or new specs.
- `power_tier` is **authored scenario data**, stable for the lifetime of a campaign. It is never recomputed at runtime from controlled regions, income, or military strength.
- Any future runtime strength model (for AI threat weighting, coalition calculations, dispatch priority) must be a **separate field**, e.g. `power_score`. A runtime `power_score` must never overwrite `power_tier`. Nations that weaken or strengthen during play keep their authored tier.
- Storage shape: `power_tier` is a field on the authored nation record, colocated with other authored nation data (capital, color, starting AP). There is no separate tier map. The authored scenario config is the single source of truth; runtime code reads from it and does not mutate it.

**`political_status` — runtime state**

- Schema version `1` for scale work uses `independent`, `vassal`, and `protectorate`.
- `vassal` and `protectorate` are both `subject` statuses for DG-2 sphere membership and any later optional objective set that cares about subjection.
- Only `vassal` auto-enters under DG-4's `include_vassals = true`. `protectorate` does not create automatic war-entry on its own.
- `political_status` may change during play (`independent` -> `vassal` -> `independent` after rebellion, etc.) and must never be conflated with `power_tier`.
- Any future subject form must explicitly declare whether it counts as a `subject` for optional objectives, sphere membership, and war-entry. The default is "no" until authored.

**Scenario roster mapping (current DG-1 roster)**

The 13-nation DG-1 roster maps to the canonical enum as follows. This roster is the authoritative assignment; the older DG-1 prose labels ("Major Powers / Active Secondary Powers / Key Minors") are an explanatory gloss on the same tiers.

| `power_tier` | Nations |
|--------------|---------|
| `major`      | France, Britain, Austria, Prussia, Russia |
| `secondary`  | Spain, Ottoman Empire, Sweden, Naples/Two Sicilies |
| `minor`      | Bavaria, Saxony, Portugal, Denmark-Norway |

Future scenarios (1806, 1809, etc.) extend this roster by adding authored nation records with their own `power_tier` values, not by mutating existing entries at runtime.

**`strategic_power` — derived convenience set**

- `strategic_power` = non-French nations whose `power_tier` is `major` or `secondary` **and** whose authored scenario record sets `counts_for_strategic_power = true`.
- Used by: DG-2 salience filtering, dispatch priority, coalition weighting, and any later optional scenario-objective set that wants a "major powers that matter" bucket.
- The current 1805 draft scenario marks all 8 non-French `major` / `secondary` nations as `counts_for_strategic_power = true`, but that remains authored scenario data rather than a hardcoded global denominator.
- Off-map or partially wired interim builds must not infer strategic-power participation from map wiring alone; the authored scenario flag decides.
- **Not used for war entry.** Cascade legality is treaty-edge only per DG-4; tier does not create or block call-to-arms.

**Current full-map scope note**

- This scale-readiness plan targets the first full-map Europe prototype for the France-led 1805 campaign.
- The current 1805 draft scenario uses the full 13-nation DG-1 set, but the map and scenario schema are not capped there. Larger maps or later scenarios may author more nations.
- If an interim content build keeps a nation partially off-map or temporarily unwired, the scenario data must say so explicitly (`on_map`, `counts_for_strategic_power`, etc.) rather than silently changing salience, weighting, or AP assumptions.
- References to France, Paris, and the French sphere in DG-2 are intentional for that scope.
- Runtime hardening for `player_nation` remains valuable and should stay intact, but non-France full-map campaigns are not a prerequisite for "real map ready" in this plan.
- If a later scenario ships with a different player nation, translate these gates through scenario data (`player_nation`, `home_capital`, `player_sphere`) rather than silently hardcoding a second nation-specific variant.

**Superseded language**

- `docs/DESIGN_REFINEMENT.md` §"National Power Tiers (Great Power / Secondary / Minor)" described `power_tier` as dynamic numeric tiers recomputed from controlled regions, income, and military strength. That model is superseded. Tier is authored; any numeric strength-derived signal is a separate `power_score` field.
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §8.3 used the names `great_power / secondary_power / minor_power`. Those names are superseded by `major / secondary / minor`. The settlement-rights structure in §11 carries over under the new names unchanged.

---

### DG-2. Diplomacy Model — Bilateral vs. Regional Blocs

**Decision needed:** Does the player manage every bilateral relationship, or do nations group into blocs the player interacts with as units?

**Why it matters:** At 5 nations = 4 relationships. At 15 nations = 14 relationships + AI proposals from each. The current Talleyrand advisory, diplomatic ledger, and proposal system all assume individual bilateral management.

**Options:**
- **Option A: Keep bilateral, add smart filtering.** Talleyrand prioritizes top 3-4 threats. Ledger groups nations by relevance. Player still manages individual relationships but the UI helps them focus. Cheaper to implement.
- **Option B: Regional bloc system.** Nations belong to blocs (Iberian, Germanic, etc.). Player proposes to blocs. More historically authentic. Major new system.
- **Option C: Hybrid.** Major powers are bilateral. Minor nations follow their patron's diplomacy automatically (extend vassal-like behavior). Middle ground.

**Affected files if bilateral stays:** `diplomatic_advisory.py` (add prioritization), `diplomatic_ledger.gd` (add grouping/collapse), `ai_diplomacy.py` (throttle AI-AI proposal volume).

**Affected files if blocs:** New `bloc.py` system, rewrite `diplomatic_templates.py`, redesign `diplomatic_ledger.gd`, new bloc proposal flow in `diplomatic_executor.py`.

**DECIDED — April 17, 2026: Keep diplomacy bilateral, but make the presentation salience-filtered.**

The underlying diplomacy model stays bilateral. Do not add regional blocs or transitive patron automation as a prerequisite for Europe. The scale fix is presentation and prioritization, not a new diplomatic ontology.

**Forced-expand relationship states (precedence order, shared across all consumers):**

1. Any nation currently at war with France
2. Any nation with an active proposal or objection involving France
3. Any nation with an active Talleyrand mission
4. Any nation with active concern / betrayal-memory / `commitment_paradox` pressure involving France
5. Any nation with frontier contact against the French sphere

If more than 5 nations satisfy force-expand on the same turn, trim within that force-expand set by the same shared salience helper and the same locked tiebreak rules below. No screen may invent a second cutoff rule.

**French sphere definition:** France + current French subjects whose `political_status` is `vassal` or `protectorate` + regions currently occupied by France or a French vassal.

**Remaining visible slots:** Fill the remaining expanded rows by a weighted salience score. The score structure is locked:

- Inputs are exactly `power_tier`, `power_score_or_military_strength`, `recent_diplomatic_change`, and `coalition_threat`.
- `recent_diplomatic_change` means a treaty-state change, proposal created / expired / refused, war declaration / armistice / peace ratification, or `commitment_paradox` episode within the last 3 turns.
- `coalition_threat` reuses the coalition / threat scalar already maintained by the coalition model. If a nation has no current threat entry, treat it as `0` rather than inventing a second proxy.
- Exact coefficients are still picked in implementation review, but every consumer must use the same coefficients from the same helper.
- Tiebreak order is locked: higher force-expand precedence, then higher `power_tier`, then higher `power_score_or_military_strength`, then more recent diplomatic change, then stable nation-name sort.
- Implementation must expose one shared backend helper (for example `rank_diplomatic_salience(player_nation)`) used by Talleyrand, the Diplomatic Ledger, and any dispatch spotlight that ranks nations by relevance.

**UI cap (locked):** 5 expanded bilateral rows maximum. 4 is tight at 13 nations, 6 starts feeling like "show everything"; 5 is the authored choice and must not drift. Everything beyond 5 collapses into grouped rows such as `Secondary Powers` and `Minor Powers`. Grouped rows are clickable to expand a full list in a secondary view but do not occupy expanded-slot budget.

**Sphere definition for frontier contact:** The "French sphere" for the frontier-contact force-expand rule is France + current French subjects whose `political_status` is `vassal` or `protectorate` + regions currently occupied by France or a French vassal. This definition is shared with any other force-expand rule that references the sphere; do not re-derive it per consumer.

**Implementation note:** "Top 3-4 relevant nations" is not a vague design aspiration. The force-expand rules, the shared helper, the weighted salience score inputs, the locked tiebreak order, and the 5-row cap together are the contract.

---

### DG-3. Supply Lines

**Decision needed:** Does supply gain a distance-from-capital dimension?

**Why it matters:** Current supply is purely local (`region.supply_capacity`). A 50K army in Moscow sustains identically to one adjacent to Paris. At 80+ regions this removes the central Napoleonic tension of overextension.

**Options:**
- **Option A: Distance penalty.** Supply capacity degrades with pathfinding distance from nearest friendly supply depot or capital. Simple formula, big gameplay impact.
- **Option B: Supply route vulnerability.** Supply follows a traced path; enemies can interdict it. More complex, more interesting.
- **Option C: Defer to post-EA.** Ship Europe without supply lines, tune attrition higher to simulate. Cheapest but weakest.

**Affected files:** `world_state.py` (process_supply_attrition), `region.py` (supply_capacity), `enemy_ai.py` (AI must consider supply), `strategic_ledger.gd` (show supply status).

**DECIDED — April 17, 2026: Deferred. Build after Europe map is playable.**

Supply lines is a gameplay feature, not a scaling prerequisite. The current local `supply_capacity` per region already applies attrition — armies in distant regions take losses. Distance-from-capital supply would make the game *better* but does not block having a functional Europe map.

**Plan:** Ship Europe with current local supply. After first Europe playtest, evaluate whether the game *feels* like it needs overextension pressure or whether attrition + economy already create it. If needed, implement as a "Campaign Feel" pass — likely Option A (distance penalty) as the simplest high-impact choice.

**No code changes required for map scaling.** The existing `process_supply_attrition` and `region.supply_capacity` work at any region count.

---

### DG-4. War Cascade Depth Policy

**Decision needed:** What happens when declaring war triggers alliance chains at 10+ nations?

**Why it matters:** Current cascade (`diplomacy.py:2242`) is recursive with no depth limit. One `declare_war()` can trigger 8-12 new wars in a single turn, each generating dispatch events. Combined with vassal auto-enlistment, this is the most explosive single-action risk.

**Options:**
- **Option A: Cap cascade depth at 2.** Direct allies join immediately. Allies-of-allies get a "call to arms" that resolves next turn. Simple, predictable.
- **Option B: 1-turn delay for all cascade.** Direct allies get a "call to arms" popup. Player and AI can see it coming. More interactive.
- **Option C: Batch cascade into single event.** All cascade happens instantly but is presented as one "Coalition forms" event instead of N separate war declarations. Keeps mechanics, fixes UX.

**Affected files:** `diplomacy.py` (_process_war_cascade), `dispatch.py` (event batching), `vassal.py` (auto-enlistment depth).

**DECIDED — April 17, 2026: Direct-only bilateral call-to-arms. No transitive cascade.**

War-entry obligation travels one treaty edge only. When France declares war on Austria, Austria may call its direct allies and vassals. Those nations decide whether to join or refuse. Their own allies are not called through that acceptance. The same direct-only rule applies symmetrically on the attacker side so offensive alliance chains cannot recreate the explosion from the other direction.

**Rules:**

- Direct defender allies and defender vassals may receive a call-to-arms
- Defender-side `ALLIANCE` / `DEFENSIVE_ALLIANCE` honor calls auto-enter when legal. There is no soft-refusal path for an eligible defender-side obligation in schema version `1`; only hard illegality blocks entry.
- Direct attacker allies and attacker vassals may receive a call-to-arms when applicable
- Attacker-side `ALLIANCE` entry is discretionary and must route through one attacker-side decision seam that later war-entry UI can surface as a `join_opportunity`; do not hardcode a second silent path elsewhere.
- No transitive propagation, ever

**Qualifying entry relationships (locked list):** A nation receives a call-to-arms only if it holds one of the following direct relationships with the attacked or attacking nation:

- `ALLIANCE` — full alliance, offensive and defensive obligation
- `DEFENSIVE_ALLIANCE` — defensive obligation only; attacker-side call does not fire for defensive-only treaties
- Vassal relationship — vassals of the attacked or attacking nation auto-enter under the same direct-only rule, subject to existing vassal autonomy / loyalty gates in `vassal.py`

- For schema version `1`, only `political_status = vassal` satisfies the vassal auto-entry path. `protectorate` counts as a subject for DG-2 and any later optional objective set, but does **not** auto-enter here.

Any other bilateral state (guarantee, trade agreement, non-aggression, neutrality, etc.) does **not** produce a call-to-arms on its own. New treaty types added in future specs must explicitly declare whether they create call-to-arms obligation; the default is "no."

**Refusal event contract (concrete):** When a direct ally explicitly declines a surfaced attacker-side call-to-arms, emit a `commitment_paradox` episode in the Memory and Pressure substrate. Contract:

- `episode_type = "call_to_arms_refused"`
- `breaker` = the refusing ally
- `victim` = the nation that issued the call (attacked or attacking principal)
- `witnesses` = all nations holding `ALLIANCE` or `DEFENSIVE_ALLIANCE` with either the breaker or the victim at the moment of refusal (these are the parties whose future trust math should see the refusal)
- `severity` scales with the stakes of the refused war (principal's war score exposure, capital-threat presence, power_tier of the aggressor) — exact formula locked during implementation; the field must exist from day one
- Trust / honor fallout still applies on top of the episode; the episode is additional durable memory, not a replacement

Without this event contract the direct-only rule quietly becomes a pacifist switch — refusal must be visibly costly over time, which is what keeps the model's teeth.

Defender-side hard illegality blocks do **not** emit `call_to_arms_refused`; they are legality failures, not discretionary refusals.

**Later war entry:** Nations that did not enter through direct treaty obligation may still join later, but only through separate systems such as coalition threat, British subsidy, opportunistic AI entry, worsening opinion, or new bilateral agreements. Those are not part of cascade propagation.

**Presentation rule:** Same-turn ally entry is grouped in dispatch ("Austrian allies enter the war"), not emitted as an unreadable chain of line-by-line declarations.

#### DG-4 Amendment — April 17, 2026: Defender-side choice with memory cost

The original DG-4 auto-entered eligible defenders whenever the call was legal. That produces a sharp edge: loyal allies get dragged into hopeless wars with no agency and no memory signal distinguishing prudence from cowardice. This amendment splits defender-side resolution into three paths and routes the discretionary path through the Memory and Pressure substrate.

**Three-path resolution (replaces single "auto-enter if legal" rule):**

| Path | Condition | Outcome | Memory |
|------|-----------|---------|--------|
| **Hard-illegal** | Already at war with principal, no common frontier, active truce, etc. | Blocked | None — legality failure, not choice |
| **Impossible war** | Call evaluated as hopeless at the moment of the call (see predicate below) | Auto-decline | None — rational decision, not betrayal |
| **Discretionary** | Legal and not impossible | Player/AI choice: honor or refuse | Episode emitted in either direction |

The discretionary path is the behavioral change. Defender-side eligible calls that are legal and not impossible now route through the same explicit decision seam as attacker-side calls, and declining emits a durable memory episode — a larger one than attacker-side.

**Impossibility predicate (locked structure, tunable coefficients):**

Evaluated once at call-moment, not continuously. Inputs:

- `aggressor_coalition_power_score / defender_coalition_power_score` ratio exceeds an authored threshold
- Defender's capital is already under hostile threat or occupation
- Defender is already in a losing war on another front (war_score below authored floor)

Any one trigger fires the impossibility branch. Single shared helper (for example `is_impossible_defensive_call(caller, callee, world)`) used everywhere the predicate is needed. Same discipline as `rank_diplomatic_salience`. Exact coefficients picked in implementation review; `cascade_profile.impossibility_threshold` in the scenario schema.

**Critical rule:** impossibility is measured *at call moment only*. Otherwise players game it by stacking overwhelming force mid-war to shake loose enemy allies. The evaluation is snapshot-based.

**Player agency:** Even when impossibility auto-declines, the player may override and honor the call anyway ("hopeless last stand"). Override emits `call_to_arms_honored_costly`, not `_refused_defensive`. This preserves dramatic agency without reopening the pacifist-switch risk.

**Episode contract (extends DG-4 refusal event contract):**

Three episode types, each a distinct entry in the Memory and Pressure substrate:

| Episode type | Fires when | Severity baseline | Witness scope |
|--------------|-----------|-------------------|---------------|
| `call_to_arms_refused_offensive` | Attacker-side ally explicitly declines discretionary offensive call | Baseline (the DG-4 original) | ALLIANCE / DEFENSIVE_ALLIANCE counterparts of either side |
| `call_to_arms_refused_defensive` | Defender-side ally refuses a legal, not-impossible defensive call | **1.5–2.0x baseline** | **All nations with any active treaty with the refuser** (wider than offensive) |
| `call_to_arms_honored_costly` | Defender-side ally honors a call flagged as costly (impossibility predicate true, player/AI chose to honor anyway) | Positive episode | Same scope as `_refused_defensive` |

Payload fields (shared shape):

- `episode_type` — one of the three above
- `breaker` or `honorer` — the deciding nation
- `victim` — calling principal (attacked or attacking, by context)
- `witnesses` — per scope rule above
- `severity` — scaled by principal's war exposure, aggressor `power_tier`, and authored `honor_bias` if present
- `call_context` — `defensive` or `offensive`, plus snapshot of impossibility evaluation
- `episode_id` — continues through any downstream fallout per existing substrate rules

**Defender-side refusal severity is larger for two reasons:**

1. Historical weight: breaking a defensive oath was a more severe reputation event than declining an opportunistic offensive call.
2. Game balance: the direct-only cascade relies on memory accumulation to prevent a pacifist spiral. Defender refusal must bite harder than offensive refusal, or the expected value of refusal-always dominates.

**Victim-grade grievance (not a witness strike):**

The calling principal is not a witness — it is the victim. For defensive refusals, the victim takes a victim-grade strike (per §8.3 of `RELIABILITY_COMMITMENTS_SPEC.md`) and seeds a rivalry entry when rivalries expand. This is permanent until actively repaired via Make Amends; it is not a decaying relation modifier.

**Habitual-refusal compounding:**

N `call_to_arms_refused_defensive` episodes within M turns (authored — candidate `N=2`, `M=15`) promotes the refuser into a standing "oathbreaker" posture: any ALLIANCE or DEFENSIVE_ALLIANCE proposal to that nation auto-rejects for a cooldown window. This makes habitual refusal genuinely self-destructive and prevents the refuser from drifting between obligations for free. The posture decays with observed honoring of future calls.

**Anti-renewal cooldown:**

A refused defensive call blocks re-signing ALLIANCE or DEFENSIVE_ALLIANCE between the same pair for an authored window (candidate 15 turns). Re-alliance is possible afterward but not the same turn.

**Multi-victim compounding:**

If the same refuser receives multiple calls in the same turn (two allies attacked at once), each call resolves independently and each refusal emits its own episode. Severity stacks rather than deduplicates. A refuser who abandons two allies in one turn is worse than one who abandons one.

**Coalition-formation hook:**

The refuser's unreliability signal feeds the coalition-threat scalar already maintained for coalition formation. Nations that repeatedly break defensive obligations accumulate threat, making coalitions against them easier to brew.

**Chained-refusal inter-ally signaling (deferred):**

Within a single call to multiple allies, resolutions are simultaneous in schema version `1`. Ally X does not see ally Y refuse before deciding. Inter-ally gossip or sequential resolution is reserved for a later spec — the substrate can support it without rework.

**Audit trail:**

Every war's first-turn records a `war_entry_ledger` in campaign log: for each potentially called nation, the path taken (`hard_illegal` / `impossible_auto_declined` / `honored` / `refused_discretionary` / `honored_costly`) and the reason. The Diplomatic Ledger later surfaces this as "Russia has refused 2 defensive calls in the last 10 turns."

**Scenario authoring: `honor_bias`:**

Optional per-nation scalar (default `1.0`), authored in scenario config. Multiplies refusal severity and can shift episode decay rate. Lets scenario authors encode period texture — Prussia's rigid honor culture might be `1.15`, Spain's volatile loyalties `0.85`.

Amendment to `cascade_profile` in the DG-6 scenario schema:

```yaml
cascade_profile:
  mode: "direct_only"
  qualifying_treaty_states:
    defender_side: [ALLIANCE, DEFENSIVE_ALLIANCE]
    attacker_side: [ALLIANCE]
  include_vassals: true
  refusal_event_type_offensive: "call_to_arms_refused_offensive"
  refusal_event_type_defensive: "call_to_arms_refused_defensive"
  honored_costly_event_type: "call_to_arms_honored_costly"
  defender_refusal_allowed: true
  impossibility_threshold:
    power_ratio: 2.5                         # aggressor/defender coalition power
    capital_threat_auto_impossible: true
    losing_war_score_floor: -40
  defensive_refusal_severity_multiplier: 1.75
  oathbreaker_posture:
    refusals_required: 2
    window_turns: 15
    auto_reject_ally_proposals_turns: 10
  anti_renewal_window_turns: 15
```

**Vassal exception (unchanged):**

Vassals do *not* get the discretionary path. Vassal auto-entry still fires under existing autonomy / loyalty gates in `vassal.py`. A disloyal vassal that would "refuse" rebels through the existing rebellion path instead. Amendment does not add refusal UI or episodes to the vassal layer.

**Jealousy v3.1 hook (deferred):**

When Jealousy ships, defensive refusals and costly honorings are candidate signals for its input set. Hook is mentioned here so the Jealousy spec can reference it; no code added until Jealousy is approved.

**Affected specs:**

- `RELIABILITY_COMMITMENTS_SPEC.md` — new episode types, wider witness scope for defensive refusals, severity table row additions, oathbreaker posture (see §8.4 amendment)
- `RELIABILITY_IMPLEMENTATION_PLAN.md` — new slice for call-to-arms episode emission + player-facing UI
- `COMMITMENTS_PRESENTATION_SPEC.md` + `DIPLOMAT_VOICE_BIBLE.md` — three new event families need authored lines
- `diplomatic_templates.py` — spotlight/notice copy for the three episodes
- Phase 6 of this plan — player UI for the defensive-call decision (new item 6.6, specced when Phase 6 lands)

**Design success criteria (first-playtest):**

- Player never feels "my ally was obligated and it was ignored" (the sharp edge)
- Refuser never feels "I refused for free" (the pacifist-spiral failure mode)
- Witness cost is observable in future dealings with the refuser (acceptance formula, reliability signals, coalition threat)
- Impossibility auto-decline does not become the dominant refusal path — most refusals are discretionary with cost

---

### DG-5. Campaign Objectives / Victory Conditions

**Decision needed:** Does Europe need a mandatory hard victory condition at all?

**Current:** The codebase still has a global territory-fraction victory path, but that older tutorial-scale assumption does not define the shape of a full-Europe campaign.

**Options:**
- **Option A: Keep a hard win condition.** Re-spec hegemony / congress / score victory for the Europe map.
- **Option B: No mandatory hard victory.** Ship the Europe campaign as an open-ended sandbox, like EU4 / CK3 style play, and let the player stop when they consider the run complete.
- **Option C: Scenario-authored optional objectives.** Keep the base campaign open-ended, but allow later scenarios to layer in optional objective sets.

**Affected files:** None are required for the first Europe prototype. `world_state.py` / `turn_manager.py` only need changes later if a scenario explicitly opts into hard objectives.

**DECIDED — April 17, 2026. Reframed — April 17, 2026: No mandatory hard victory condition is required for Europe-map readiness.**

The France-led 1805 Europe prototype is an open-ended campaign by default. Real-map readiness does **not** depend on a global win screen, conquest fraction, or hegemonized-majority check.

**Campaign-objective contract:**

- Hard victory checks are optional scenario content, not a global engine requirement.
- If a scenario omits `objectives_profile`, the campaign runs with no mandatory hard victory condition.
- `strategic_power` remains a weighting / salience concept for AI and UI. It does not create a required global victory denominator in the base prototype.
- Existing defeat / collapse rules may still exist separately; this gate is only about mandatory win conditions, not about making the campaign impossible to lose.
- Any later hard-objective system must be scenario-authored and optional. Do not reintroduce a single global `VICTORY_REGION_FRACTION` rule for all campaigns.

---

### DG-6. Pacing — Turn Limit, AP Budget, Campaign Length

**Decision needed:** How long is a Europe campaign? How many actions per turn?

**Current:** 40 turns, 4 AP. At 100 regions: 0.4 turns/region (unwinnable), 4 AP to manage distributed warfare (impossible).

**Options:**
- **Option A: Scale linearly.** `max_turns = region_count * 2`, `base_AP = 4 + (nation_marshal_count // 3)`. Simple.
- **Option B: Scenario-configured.** Each scenario (19-region, Europe) defines its own turn limit and AP. More control.
- **Option C: Remove turn limit.** Victory/defeat by conditions only. AP scales with controlled territory.

**Affected files:** `world_state.py` (max_turns), `nation_config.py` (BASE_NATION_ACTIONS), `turn_manager.py` (time victory check).

**DECIDED — April 17, 2026: Scenario-configured pacing.**

Turn limit, AP budget, and related pacing rules are authored per scenario. Do not derive Europe pacing from a single global formula.

**Scenario pacing schema (initial contract):**

```yaml
scenario_schema_version: 1
player_nation: <nation>
home_capital: <region>
player_sphere:
  subject_statuses: [vassal, protectorate]
  include_occupied_regions: <bool>
nations:
  <nation>:
    capital: <region>
    power_tier: major | secondary | minor
    starting_political_status: independent | vassal | protectorate
    overlord: <nation> | null
    on_map: <bool>
    counts_for_strategic_power: <bool>
max_turns: <int>
base_ap:
  by_nation:
    <nation>: <int>
  by_tier_default:
    major: <int>
    secondary: <int>
    minor: <int>
objectives_profile: <optional>              # omit entirely for open-ended campaigns
cascade_profile:
  mode: "direct_only"                       # DG-4 locks this; future modes require a gate reopen
  qualifying_treaty_states:
    defender_side: [<state>]                # ALLIANCE, DEFENSIVE_ALLIANCE
    attacker_side: [<state>]                # ALLIANCE
  include_vassals: <bool>
  refusal_event_type: "call_to_arms_refused"
free_basic_actions:
  - <action_id>
```

**Schema notes:**

- `scenario_schema_version` is required from the first implementation so later scenarios have a migration path. Version `1` is the shape above; future shape changes bump the version and the loader gains a migration path.
- The shorthand `by_tier_default[power_tier]` means `by_tier_default[nations[nation].power_tier]`; the nation's tier comes from authored scenario data, not a separate runtime map.
- `player_nation`, `home_capital`, `player_sphere`, and authored `nations` are required in version `1`. Do not keep a hidden global nation table and layer scenario overrides on top of it.
- `base_ap` is a hybrid. `by_nation` entries always win for named nations. Nations present in authored scenario data but unnamed in `by_nation` fall back to `by_tier_default[nations[nation].power_tier]`. This is the intentional shape - neither pure-by-nation nor pure-by-tier works, because France and Britain are both `major` with different AP.
- `counts_for_strategic_power` is authored because map wiring / off-map presentation must not silently change strategic salience or any later optional objective set.
- `objectives_profile` is optional. Omit it entirely for open-ended campaigns. Any later hard-objective shape must be authored per scenario rather than assumed globally.
- `free_basic_actions` references the canonical command action IDs shared by parser / executor / meta-executor. DG-7 may group resulting events for dispatch, but dispatch categories are not action identifiers.

**Initial Europe target values:**

- `player_nation = France`, `home_capital = Paris`
- `player_sphere = {subject_statuses: [vassal, protectorate], include_occupied_regions = true}`
- `nations`: the current France-led 1805 draft authors the 13 DG-1 nations in scenario data; all are currently `on_map = true`; `counts_for_strategic_power = true` for Britain, Austria, Prussia, Russia, Spain, Ottoman Empire, Sweden, and Naples/Two Sicilies. Larger rosters remain valid in later scenarios.
- `max_turns = 80`
- `base_ap`:
  - `by_nation`: France 5, Britain 4, Prussia 4, Austria 3, Russia 3
  - `by_tier_default`: `major: 3`, `secondary: 2`, `minor: 2`
- `objectives_profile`: omitted for the base France-led 1805 sandbox campaign (no mandatory hard victory)
- `cascade_profile`: `mode = "direct_only"`, `qualifying_treaty_states = {defender_side: [ALLIANCE, DEFENSIVE_ALLIANCE], attacker_side: [ALLIANCE]}`, `include_vassals = true`, `refusal_event_type = "call_to_arms_refused"`
- `free_basic_actions`: authored from the canonical command action-ID set during Phase 5.5 implementation

The current 19-region scenario keeps its own authored pacing values and migrates to `scenario_schema_version: 1` when the loader lands. Future scenarios such as 1806 or 1809 extend the same schema rather than adding bespoke knobs in unrelated files.

---

### DG-7. Dispatch & Information Density

**Decision needed:** How does the player parse 30-50 events per turn?

**Current:** Morning dispatch presents all events in a flat list. At 5 nations this is 5-10 events. At 10+ nations with active diplomacy, war cascades, rivalry shifts, trade income, coalition friction — it's a wall of text.

**Options:**
- **Option A: Priority filtering + cap.** Critical events always shown. Minor events collapsed into summary line ("3 minor diplomatic shifts occurred"). Cap at ~20 visible events.
- **Option B: Categorized sections.** Military events, diplomatic events, economic events — each collapsible. Player reads the section they care about.
- **Option C: Urgent/routine split.** "Urgent" tab (wars, proposals, threats) shown by default. "Routine" tab (trade income, relation drift) available on click.

**Affected files:** `dispatch.py` (queue_dispatch_event, build), `dispatch_view.gd` (rendering), `diplomatic_advisory.py` (Talleyrand prioritization).

**DECIDED — April 17, 2026: Categorized sections with priority escalation. Must handle 20+ nations.**

Hybrid of Options A + B. Dispatches are grouped into themed sections with period-appropriate voices, and events within sections are filtered by priority. This matches how Napoleon actually received information — through different channels and aides.

**Four dispatch sections:**

| Section | Voice | Contains |
|---------|-------|----------|
| **Military Affairs** | Berthier | Battles, movements, retreats, garrison events, attrition, reinforcements |
| **Diplomatic Affairs** | Talleyrand | Proposals, treaty changes, war declarations, coalition shifts, rivalry events |
| **Imperial Treasury** | Narrator | Income, trade, bankruptcy warnings, upkeep, building completion |
| **Intelligence** | Berthier | Fog reveals, scouting results, enemy sightings, watchtower reports |

**Priority tiers (per event, not per section):**

| Priority | Behavior | Examples |
|----------|----------|----------|
| **CRITICAL** | Always shown, expanded | Wars declared on player, proposals requiring response, battles involving player marshals, capital threats, coalition formation |
| **MAJOR** | Shown, collapsed | AI-AI wars near player borders, relation shifts with neighbors, coalition brewing, ally requests |
| **MINOR** | Summarized as count | Distant AI-AI diplomacy, minor trade income, routine relation drift, minor attrition |

**Collapse rules:**
- Sections with zero events are hidden entirely
- MINOR events within a section collapse into a summary line: *"3 minor diplomatic developments occurred"* with expand option
- Cap: if a section exceeds 15 events after filtering, collapse MAJOR events too and show *"8 military developments — expand to review"*
- Empty sections don't render at all (at 5 nations, Treasury and Intelligence may be empty most turns)

**Scale behavior at 20+ nations:**
- At 13 nations: ~15-25 events/turn, most sections have 3-8 items. Manageable.
- At 20 nations: ~30-50 events/turn. MINOR collapse kicks in heavily. Player sees ~12-18 expanded items across 4 sections. Distant AI-AI noise vanishes into summary lines.
- At 30+ nations: Same structure holds. MAJOR collapse may trigger in Diplomatic Affairs. Player focuses on CRITICAL items, drills into sections on demand.

**Implementation approach:**
1. Add `category` field (`military`, `diplomatic`, `treasury`, `intelligence`) and `priority` field (`critical`, `major`, `minor`) to dispatch events in `dispatch.py`
2. `build()` groups events by category, sorts by priority within each group
3. `dispatch_view.gd` renders sections with headers, collapse/expand per section
4. No new UI screens — this replaces the flat list inside the existing dispatch view

**Affected files:** `dispatch.py` (event category/priority fields, grouped build), `dispatch_view.gd` (sectioned rendering, collapse/expand), `campaign_log.py` (event types may need category mapping).

---

## Phase 1: Test Safety Net — Session Spec

**Status:** COMPLETE (April 17, 2026).
**When:** Pulled forward before Phase 0 closure to establish regression coverage ahead of scale work.
**Why:** Regression safety before any structural changes. If BFS caching or fog extension breaks something, these tests catch it.
**Estimated effort:** 1-2 hours.
**Acceptance criteria:** All new tests pass. Full test suite still passes. No hardcoded `19` remains in any test assertion about region/world count.

---

### 1.1 Nation Config Completeness Test

**Create:** `tests/test_nation_config_completeness.py`

**Imports needed:**
```python
from backend.models.region import NATION_CAPITALS, REGIONS_DATA
from backend.nation_config import (
    DEFAULT_NATION_GOLD, BASE_NATION_ACTIONS, DEFAULT_NATION_AUTHORITY,
    RUNTIME_NATIONS, validate_runtime_nation_support,
)
from backend.models.diplomat import STARTING_DIPLOMATS
from backend.models.marshal import create_enemy_marshals
from backend.models.world_state import WorldState
```

**Tests to write (7 tests):**

1. **`test_all_capital_nations_have_gold_config`**
   - For every nation in `NATION_CAPITALS.keys()`, assert it exists in `DEFAULT_NATION_GOLD`
   - Error message: `f"{nation} in NATION_CAPITALS but missing from DEFAULT_NATION_GOLD"`

2. **`test_all_capital_nations_have_action_config`**
   - Same pattern against `BASE_NATION_ACTIONS`

3. **`test_all_capital_nations_have_authority_config`**
   - Same pattern against `DEFAULT_NATION_AUTHORITY`

4. **`test_all_capital_nations_have_diplomat`**
   - For every nation in `NATION_CAPITALS.keys()`, assert it exists in `STARTING_DIPLOMATS`
   - Error message: `f"{nation} has a capital but no starting diplomat"`

5. **`test_all_capital_nations_have_marshals`**
   - Create a fresh `WorldState()` (which calls `create_player_marshals` + `create_enemy_marshals`)
   - For every nation in `NATION_CAPITALS.keys()`, assert at least one marshal has that nation
   - `marshal_nations = {m.nation for m in world.marshals.values()}`
   - Error message: `f"{nation} has a capital but no marshals in default setup"`

6. **`test_validate_runtime_support_passes_current_roster`**
   - `errors = validate_runtime_nation_support(NATION_CAPITALS.keys())`
   - `assert errors == [], f"Current roster fails validation: {errors}"`

7. **`test_runtime_nations_matches_capitals`**
   - `assert set(RUNTIME_NATIONS) == set(NATION_CAPITALS.keys())`
   - Catches case where a nation is added to one surface but not `NATION_CAPITALS`

8. **`test_all_config_surfaces_consistent`**
   - Collect all 5 sets: `NATION_CAPITALS.keys()`, `DEFAULT_NATION_GOLD.keys()`, `BASE_NATION_ACTIONS.keys()`, `DEFAULT_NATION_AUTHORITY.keys()`, `STARTING_DIPLOMATS.keys()`
   - Assert all 5 sets are identical
   - Error message lists which sets differ and which nations are missing where

**Edge case — no false positive on current 5-nation roster:** Every test should pass on the current codebase before any changes. Run the test file first to confirm.

---

### 1.2 Fix Hardcoded Region Count in Tests

**8 assertions across 5 files** (the audit said 6 in 4 files — it missed 2):

| # | File | Line | Current | Replace With |
|---|------|------|---------|--------------|
| 1 | `tests/test_conftest_factories.py` | 124 | `assert len(world.regions) == 19` | `assert len(world.regions) == len(REGIONS_DATA)` |
| 2 | `tests/test_conftest_factories.py` | 162 | `assert len(world.regions) == 19` | `assert len(world.regions) == len(REGIONS_DATA)` |
| 3 | `tests/test_economy_foundations.py` | 148 | `assert len(REGIONS_DATA) == 19` | DELETE this line (the `for` loop on line 149 already validates every region) |
| 4 | `tests/test_systems_audit_session8.py` | 280 | `assert total_regions == 19` | `assert total_regions == len(REGIONS_DATA)` |
| 5 | `tests/test_terrain_data_layer.py` | 253 | `assert len(REGIONS_DATA) == 19` | DELETE this line (the `for` loop on line 254 already validates every region) |
| 6 | `tests/test_terrain_data_layer.py` | 290 | `assert len(regions) == 19` | `assert len(regions) == len(REGIONS_DATA)` |

**Additional hardcoded 19 references (not count assertions but still brittle):**

| # | File | Line | Current | Fix |
|---|------|------|---------|-----|
| 7 | `tests/test_systems_audit_session8.py` | 274 | `assert int(19 * VICTORY_REGION_FRACTION) == 14` | `region_count = len(REGIONS_DATA)` then `assert int(region_count * VICTORY_REGION_FRACTION) == int(region_count * 0.75)` |
| 8 | `tests/test_systems_audit_session12.py` | 70-72 | `threshold = max(1, int(19 * VICTORY_REGION_FRACTION))` / `assert threshold == 14` | `region_count = len(REGIONS_DATA)` then `threshold = max(1, int(region_count * VICTORY_REGION_FRACTION))` / `assert threshold == max(1, int(region_count * 0.75))` |

**Import to add** where needed: `from backend.models.region import REGIONS_DATA`

**Also rename test methods** that reference 19 in their name:
- `test_basic_has_19_regions` → `test_basic_has_all_regions` (`test_conftest_factories.py:122`)
- `test_all_19_regions_have_region_type` → `test_all_regions_have_region_type` (`test_economy_foundations.py:146`)
- `test_all_19_regions_have_terrain` → `test_all_regions_have_terrain` (`test_terrain_data_layer.py:252`)
- `test_threshold_calculation_19_regions` → `test_threshold_calculation_current_regions` (`test_systems_audit_session12.py:69`)

**Terrain distribution test — flag but don't fix now:**
`test_terrain_data_layer.py:267-272` hardcodes exact terrain counts (`plains == 7`, `hills == 4`, etc.). These will break when regions are added, but they're validating current map data, not a structural assumption. Leave them and let them break intentionally when new regions are added — that's what they're for. Add a comment: `# These counts are intentional for the current 19-region map. Update when regions are added.`

**Verification step:** After all edits, run:
```bash
".venv\Scripts\python.exe" -m pytest tests/test_conftest_factories.py tests/test_economy_foundations.py tests/test_systems_audit_session8.py tests/test_terrain_data_layer.py tests/test_systems_audit_session12.py -v
```

---

### 1.3 Adjacency Connectivity Test

**Add to:** `tests/test_map_consistency.py` (existing file, 79 lines currently)

**Tests to write (3 tests):**

1. **`test_adjacency_graph_is_connected`**
   - BFS from any region (e.g., `"Paris"`) using `REGIONS_DATA[region]["adjacent"]`
   - Assert all regions in `REGIONS_DATA` are reachable
   - Error message: `f"Disconnected regions: {unreachable}"`

   ```python
   def test_adjacency_graph_is_connected():
       start = next(iter(REGIONS_DATA))
       visited = set()
       queue = [start]
       while queue:
           current = queue.pop(0)
           if current in visited:
               continue
           visited.add(current)
           for neighbor in REGIONS_DATA[current]["adjacent"]:
               if neighbor not in visited:
                   queue.append(neighbor)
       unreachable = set(REGIONS_DATA.keys()) - visited
       assert not unreachable, f"Regions not reachable from {start}: {unreachable}"
   ```

2. **`test_adjacency_is_bilateral`**
   - Already tested by `test_godot_connections_match_backend_adjacency` for Godot, but not for backend self-consistency
   - For every region A with neighbor B, assert B also lists A as neighbor
   - Error message: `f"{a} lists {b} as adjacent, but {b} does not list {a}"`

   ```python
   def test_adjacency_is_bilateral():
       for name, data in REGIONS_DATA.items():
           for neighbor in data["adjacent"]:
               assert neighbor in REGIONS_DATA, f"{name} lists unknown region {neighbor}"
               assert name in REGIONS_DATA[neighbor]["adjacent"], (
                   f"{name} lists {neighbor} as adjacent, but {neighbor} does not list {name}"
               )
   ```

3. **`test_no_self_adjacency`**
   - No region should list itself as adjacent
   - `assert name not in data["adjacent"], f"{name} lists itself as adjacent"`

**Verification step:** After adding, run:
```bash
".venv\Scripts\python.exe" -m pytest tests/test_map_consistency.py -v
```

---

### 1.4 Validator VALID_NATIONS Fix (bonus — 2 minutes)

While touching test infrastructure, fix the trivial validator drift:

**File:** `backend/modding/validator.py:71`

**Current:**
```python
VALID_NATIONS = {"France", "Britain", "Prussia", "Austria", "Russia", "Spain", "Saxony"}
```

**Replace with:**
```python
from backend.models.region import NATION_CAPITALS
VALID_NATIONS = set(NATION_CAPITALS.keys())
```

**Verify:** Check that the import doesn't create a circular dependency. `validator.py` imports from `region.py`, which has no imports from `modding/`. Safe.

---

### Session Execution Order

1. Write `test_nation_config_completeness.py` (item 1.1)
2. Run it — all 8 tests should pass on current codebase
3. Fix the `== 19` assertions (item 1.2) — all 8 edits + 4 renames
4. Run those 5 test files — all should still pass
5. Add adjacency tests to `test_map_consistency.py` (item 1.3)
6. Run it — all 3 new + 3 existing tests should pass
7. Fix `validator.py` VALID_NATIONS (item 1.4)
8. Run full test suite: `".venv\Scripts\python.exe" -m pytest tests/ -v --tb=short -q`
9. Commit

**Expected new test count:** ~14 new tests (8 config + 3 adjacency + 3 existing map consistency remain)

**Done-done criteria:**
- [x] All new tests pass (11 new: 8 config + 3 adjacency)
- [x] Full suite passes (8,385 passed, 0 failures)
- [x] No hardcoded `19` in any test assertion about region/world count
- [x] `VALID_NATIONS` derives from `NATION_CAPITALS`
- [x] Test method names don't reference `19`

---

## Phase 2: Performance Infrastructure

**When:** After Phase 1 tests pass.
**Why:** The #1 and #2 blockers from the audit. Without these, AI turns take 2-4 seconds at 100 regions, and AI cheats by seeing through fog.
**Estimated effort:** 1-2 sessions.

**Clarification lock (April 17, 2026):**

- Phase 2.1 distance caching is for adjacency topology only. Region controller changes do **not** invalidate `get_distance()`.
- Phase 2.2 should keep `_marshals_by_region` private and expose AI-safe helpers instead of teaching AI code to read private cache fields directly.
- Phase 2.3 does **not** generalize `RegionIntel` into a serialized per-nation intel store. It adds a lightweight nation-perspective live visibility seam for AI decision-making only.

### 2.1 Cache `get_distance()` + Fix BFS

**Problem:** 32 `get_distance()` calls per marshal per turn, no caching, `queue.pop(0)` is O(n).

**Changes in `world_state.py`:**
1. Replace `queue.pop(0)` with `collections.deque.popleft()` in `get_distance()` (~line 2029) and `find_path()` (~line 2099)
2. Add `@lru_cache` or manual dict cache on `get_distance()`. Use a symmetric key so `("Paris", "Lyon")` and `("Lyon", "Paris")` share one entry.
3. Treat the cache as adjacency-topology-only: ordinary region capture / controller changes do **not** invalidate it because `get_distance()` only reads graph connectivity, not ownership.
4. Add `invalidate_distance_cache()` for future adjacency edits, synthetic benchmark setup, or any later topology mutation seam. Do **not** call it from capture logic unless region adjacency can actually change there.

**Test:** Benchmark before/after with 100-region synthetic graph. Verify the cache survives a controller change and only changes after an explicit adjacency mutation + invalidation call.

**Depends on:** Phase 1 (safety net tests passing)

---

### 2.2 Wire Spatial Index Into AI

**Problem:** As of April 17, 2026, `backend/ai/enemy_ai.py` still has 69 direct `world.marshals.values()` / `marshals.values()` scans. `_marshals_by_region` already exists at `world_state.py:1249`, but the current public `get_marshals_in_region()` deliberately stays linear for correctness because some callers and tests still mutate marshal locations outside indexed hot paths.

**Changes in `backend/ai/enemy_ai.py`:**
1. Re-count scan sites before each batch (`69` is the current baseline, not a permanent invariant)
2. Categorize each: needs all marshals? needs marshals in a region? needs marshals of a nation?
3. Replace region-specific scans with an AI-safe indexed helper on `WorldState`, **not** direct `world._marshals_by_region[...]` reads
4. Reuse the existing `get_marshals_by_nation(nation)` helper for nation-specific scans; add per-turn caching only if profiling shows it matters
5. Add `get_marshals_of_nations(nation_list)` only for repeated multi-nation unions that remain hot after the region-index pass

**Changes in `world_state.py`:**
- Keep `_marshals_by_region` private
- Add a clearly-scoped AI hot-path helper (for example `get_marshals_in_region_indexed(region_name)`) whose contract explicitly requires a fresh index
- Add `refresh_marshal_indexes()` / equivalent call sites so AI evaluation scopes rebuild the index before indexed reads; if a marshal relocation happens and later AI logic in the same turn depends on indexed reads again, rebuild before those reads rather than silently trusting stale cache state
- Preserve the existing correctness-first `get_marshals_in_region()` linear helper for general callers and tests
- Add `get_marshals_of_nations(nation_list)` only if the AI batching pass still needs it after the region-index conversions

**Test:** Run full test suite after each batch of replacements. Spot-check AI behavior in a few turns.

---

### 2.3 Extend Fog to All AI Nations

**Problem:** `backend/ai/enemy_ai.py` already has a fog-aware seam, but it currently only activates for the player nation because `RegionIntel` is intentionally player-perspective only. Enemy AI still falls back to omniscient contact scans.

**Clarified scope for this phase:** do **not** build a full per-nation serialized intel/history system yet. Phase 2 only adds a lightweight nation-perspective **live** visibility helper for AI decision-making.

**Changes in `backend/ai/enemy_ai.py`:**
1. Route scale-sensitive enemy-contact queries through the nation-perspective live-visibility helper instead of omniscient `get_enemies_of_nation()`
2. Expand `_should_use_fog_aware_enemy_query()` so AI nations use the new live visibility seam once it exists
3. Keep the allowed asymmetry narrow: AI nations always know their own marshal positions and own-controlled regions, but enemy positions still require visibility under the same live rules

**Changes in `world_state.py`:**
- Keep `get_visible_enemies(nation)` player-facing and backed by `RegionIntel`
- Add a separate live helper for arbitrary nation perspective (for example `get_live_visible_enemies(nation)` or `get_visible_enemies_for_nation(nation)`) that evaluates current sight rules without creating persistent intel history
- Baseline sight rules for the live helper should mirror the existing player visibility model where applicable: friendly-marshal presence, own-region sight, adjacency to friendly marshals, and watchtower adjacency
- No stale-memory persistence, per-nation intel event log, or save-format expansion in this phase

**Design note:** AI can be "smarter" than fog allows in narrow ways (for example knowing its own marshal positions), but it should not see enemy positions it has not currently revealed through the live visibility rules above.

**Test:** Add nation-perspective visibility tests for at least player, one AI nation, and one AI-vs-AI pair. Verify that player `RegionIntel` behavior is unchanged while AI contact queries stop seeing enemy marshals outside live sight.

**Depends on:** 2.2 (spatial index should be in place first)

---

## Phase 3: Data Pipeline

**When:** After Phase 2 performance work.
**Why:** Cannot add nations or regions without this. Currently adding one region requires 6-7 file edits.
**Estimated effort:** 1-2 sessions.

### 3.1 Nation Config Factory Pattern

**Problem:** 5 nations hardcoded across 5 config surfaces. Marshal/diplomat creation is 470-line hand-authored functions.

**Changes in `nation_config.py`:**
- Add `DEFAULT_NATION_DEFAULTS` dict with sensible fallback values for gold, AP, authority
- New nations only need to override what differs from defaults
- `validate_runtime_nation_support()` checks defaults + overrides

**Changes in `marshal.py`:**
- Create `create_marshals_from_data(nation, marshal_definitions)` factory
- `marshal_definitions` is a list of dicts: `{name, personality, ability, troops, cavalry, ...}`
- Keep existing `create_player_marshals()` / `create_enemy_marshals()` as wrappers that feed data into the factory
- New nations add a data list, not a 100-line function

**Changes in `diplomat.py`:**
- Similar factory: `create_diplomat_from_data(nation, diplomat_def)`
- Diplomat definitions: `{name, voice_style, ...}`

**Depends on:** DG-1 (need to know which nations to add)

---

### 3.2 Frontend Loads Adjacency From Backend — **DONE April 19, 2026**

**Landed:** Backend exposes `GET /map_topology` (adjacency + terrain + grid + nation_capitals). `map.gd` no longer hardcodes `REGION_CONNECTIONS`; `main.gd` fetches topology on connection test and hands it to `map_area.set_region_topology()`, which rebuilds the connection layer.

**Files changed:**
- `backend/main.py` — new `GET /map_topology` endpoint (sources `REGIONS_DATA` + `NATION_CAPITALS`).
- `godot-client/.../api_client.gd` — `get_map_topology(callback)` helper.
- `godot-client/.../scenes/map.gd` — hardcoded const removed; `_region_connections` dict populated via `set_region_topology()`.
- `godot-client/.../scripts/main.gd` — `_on_map_topology_received` handler wired after connection test.

**Tests:** 7 new endpoint tests in `tests/test_map_topology_endpoint.py` (success shape, adjacency/static-field parity, bilateral invariant, nation capitals, JSON-array grid serialization). `tests/test_map_consistency.py` now enforces a drift-prevention rule (`test_map_gd_has_no_hardcoded_connections`) — if anyone re-introduces the const, the test fails.

**Rationale for option A:** `REGIONS_DATA` remains the single Python source; the frontend consumes it via the already-established HTTP pattern. No build step or asset regeneration required.

---

### 3.3 Centralize Nation Colors

**Problem:** Nation colors duplicated in `map.gd:52-61`, `utils.gd` (NATION_COLORS), `war_detail_popup.gd`.

**Fix:**
1. `utils.gd` NATION_COLORS is the single source (it's already intended to be)
2. `map.gd` and `war_detail_popup.gd` import from `utils.gd` instead of defining their own
3. Add a test that greps for `Color(` + nation name patterns outside `utils.gd` to catch future drift

---

### 3.4 Fix Prompt Fallback & Parser Hardcoding

**Files:**
- `prompt_builder.py:567` — Replace hardcoded 19-region string with `', '.join(REGIONS_DATA.keys())`
- `parser.py:103-108` — Replace hardcoded 8 enemy marshal names with dynamic lookup from world state
- `backend/modding/validator.py:71` — Replace `VALID_NATIONS` set with `NATION_CAPITALS.keys()`

**Effort:** ~30 minutes total.

---

## Phase 4: Map Art Pipeline

**When:** Before artist handoff / commissioned Europe art integration.
**Why:** The current renderer proves the color-lookup concept but can't ingest real bitmap art. Without this phase, debugging asset pipeline failures happens at the same time as validating Europe gameplay.
**Estimated effort:** 1-2 sessions.

### 4.1 Province Registry Schema

**Problem:** Province metadata only has `anchor`, `radius`, `lookup_color`, `visual_tint`. Europe needs separate anchors for units/labels/garrisons, plus wired/unwired flags.

**Create:** `assets/map/province_registry.json` (or expand the existing placeholder JSON)

**Schema per province:**
```json
{
  "province_id": "paris",
  "lookup_color": [255, 0, 0],
  "visual_tint": [0.8, 0.2, 0.2],
  "anchor": [400, 300],
  "unit_anchor": [410, 310],
  "label_anchor": [400, 280],
  "garrison_anchor": [390, 320],
  "building_anchor": [420, 310],
  "wired": true,
  "interactive": true
}
```

**Changes in `map_renderer_base.gd`:**
- `_build_province_shapes()` reads new fields
- Hover/click rejects provinces where `interactive == false`
- `update_all_regions()` skips unwired provinces for gameplay data but still renders them

**Test:** Update `tests/test_map_placeholder_assets.py` to validate new schema fields.

---

### 4.2 External Bitmap Loading

**Problem:** `map_renderer_base.gd:261-282` generates circle textures instead of loading artist-delivered images.

**Changes in `map_renderer_base.gd`:**
1. Add `_load_map_images()` method that loads:
   - `assets/map/europe_visual.png` — the pretty map players see
   - `assets/map/europe_provinces.png` — the hidden color-map for hit detection
2. Fall back to current circle generation if files don't exist (preserves 19-region dev mode)
3. Keep the existing `province_lookup_image.get_pixel()` path unchanged

---

### 4.3 Color-Map Validator

**Create:** `tools/validate_province_map.py` (or `tests/test_province_map_assets.py`)

**What it validates:**
- Visual and lookup images have identical dimensions
- Every RGB color in the lookup image exists in `province_registry.json`
- Every province in the registry appears in the lookup image (at least N pixels)
- No unexpected colors exist (catches anti-aliasing artifacts)
- No province uses the sentinel/background color
- Flags tiny pixel islands (< 5 pixels of a color) as likely export artifacts

**Run:** Before integrating any new art delivery. Also runs in CI.

---

### 4.4 Unwired Province Support

**Problem:** Roadmap plans 120-150 outlined provinces with only 80-100 wired for EA v1.

**Changes:**
- `map_renderer_base.gd`: Render unwired provinces in grey tint. Hover shows "Province Name (not yet in play)". Click does nothing.
- `map.gd`: `update_all_regions()` skips unwired provinces for gameplay data
- Province registry: `wired: false` provinces have lookup colors for hover identification but no gameplay data

---

## Phase 5: Gameplay Scaling

**When:** During first Europe prototype (after regions are added).
**Why:** Game mechanics designed for 5 nations need retuning, not just performance fixes.
**Estimated effort:** 2-3 sessions.
**Depends on:** Phase 0 design decisions.
**Execution order inside this phase:** `5.5` first as schema/loader prerequisite, then `5.1`, `5.2`, `5.3`, and `5.6`. `5.4` is deferred unless a later scenario explicitly opts into hard objectives.

### 5.5 Scenario-Configured Pacing Loader

**Implements:** DG-6 decision (locked to scenario-configured pacing, schema version 1). This item is a prerequisite for `5.1` because `5.1` consumes `cascade_profile`.

**Files:** `world_state.py` (`max_turns`, per-nation AP init), `nation_config.py` (`BASE_NATION_ACTIONS`), new scenario config loader (e.g., `backend/scenario_config.py`).

**Changes:**
- Define a `scenario_config` data structure matching DG-6's schema: `scenario_schema_version`, `player_nation`, `home_capital`, `player_sphere`, authored `nations`, `max_turns`, `base_ap.by_nation`, `base_ap.by_tier_default`, optional `objectives_profile`, `cascade_profile`, `free_basic_actions`.
- Loader resolves AP per nation as: use `base_ap.by_nation[nation]` if present, else `base_ap.by_tier_default[nation.power_tier]`. This is the authored hybrid — both paths are required.
- In version `1`, the tier fallback comes from `scenario_config.nations[nation].power_tier`; do not look it up from a separate runtime tier map.
- Create a canonical command action-ID registry shared by parser / executor / meta-executor, then have `free_basic_actions` reference that registry instead of duplicated string lists.
- Migrate the current 19-region scenario to `scenario_schema_version: 1`. Its authored values stay the same (`max_turns = 40`, current AP per nation) but now live in the scenario config instead of global constants.
- Europe scenario authors its own values: `player_nation = France`, `home_capital = Paris`, all 13 DG-1 nations in `nations`, `max_turns = 80`, `base_ap.by_nation = {France: 5, Britain: 4, Prussia: 4, Austria: 3, Russia: 3}`, `base_ap.by_tier_default = {major: 3, secondary: 2, minor: 2}`.
- `world_state.py __init__` reads from scenario config. `BASE_NATION_ACTIONS` and any remaining legacy victory constants become fallback defaults only for older content; the Europe prototype does not depend on them.
- `cascade_profile` is consumed by `5.1`. `objectives_profile` is omitted for the base Europe sandbox and reserved for any later optional objective work.
- `free_basic_actions` reuses the canonical command action IDs already shared by parser / executor / meta-executor — no second classification.

**Test:** Load both scenarios end-to-end; verify 19-region scenario keeps historical turn count and AP, Europe scenario applies its own values, and a nation present in scenario data but omitted from `base_ap.by_nation` falls back to its tier default.

---

### 5.1 Direct-Only War Entry + Refusal Event

**Implements:** DG-4 decision (locked to `direct_only`, no transitive cascade).

**File:** `diplomacy.py` (~line 2242, `_process_war_cascade`)

**Changes:**
- Strip recursive propagation. A single call-to-arms pass fires for the defender's direct allies and vassals, and (when applicable) for the attacker's direct allies and vassals.
- `qualifying_treaty_states` per DG-4: defender-side `[ALLIANCE, DEFENSIVE_ALLIANCE]`, attacker-side `[ALLIANCE]`. Vassal auto-entry is modeled separately via `include_vassals = true`, not as a treaty state.
- Defender-side eligible treaty partners auto-enter if legal; defender-side hard illegality blocks do not create a soft-refusal branch.
- Attacker-side eligible `ALLIANCE` partners resolve through one explicit attacker-side decision helper that can later surface `join_opportunity`; accepted entries do NOT trigger a further pass on their own allies.
- Only explicit attacker-side declines emit `call_to_arms_refused`; defender-side legality failures do not.
- Batch cascade dispatch events into one grouped line per side: "Austrian allies enter the war: Russia, Prussia." Do not emit one line per ally.

**File:** `vassal.py` — Vassal auto-entry obeys the same direct-only depth rule, but only nations with `political_status = vassal` use this path. No recursive pull through a vassal's own subjects.

**File:** Memory and Pressure substrate (`diplomacy.py` / `world_state.py` commitment_paradox emission) — Emit `commitment_paradox` episode on explicit attacker-side refusal with `episode_type = "call_to_arms_refused"`, `breaker` = refusing ally, `victim` = calling principal, `witnesses` = all `ALLIANCE` / `DEFENSIVE_ALLIANCE` counterparts of either side at refusal moment, severity scaled by the principal's war exposure and aggressor `power_tier`.

**Test:** Synthetic 10-nation alliance chain verifying exactly depth-1 entry and zero transitive propagation. Refusal event emits a `call_to_arms_refused` episode with the expected witnesses list.

---

### 5.2 Categorized Dispatch Sections + Priority Escalation

**Implements:** DG-7 decision (locked to categorized sections with priority filtering, must handle 20+ nations).

**File:** `dispatch.py`

**Changes:**
- Add `category` field per event: `military`, `diplomatic`, `treasury`, `intelligence` (per DG-7 section table).
- Add `priority` field per event: `CRITICAL`, `MAJOR`, `MINOR` (per DG-7 priority tier table).
- `build()` groups events by category, sorts by priority within each group.
- Collapse rules per DG-7: zero-event sections hide entirely, MINOR events collapse into a summary line ("3 minor diplomatic developments occurred"), sections exceeding 15 events after filtering collapse MAJOR events too.
- Add `get_dispatch_summary()` that returns the category-grouped, priority-filtered view.

**File:** `dispatch_view.gd` — Sectioned rendering with per-section collapse/expand, voice headers (Berthier / Talleyrand / Narrator per DG-7 section table), and MINOR / MAJOR collapse controls.

**File:** `campaign_log.py` — Event types gain category mapping so campaign log can share the same taxonomy.

**Test:** Synthetic turn producing 40+ events across all 4 sections verifies collapse kicks in, CRITICAL always renders, and empty sections stay hidden.

---

### 5.3 Coalition Friction Density Scaling

**File:** `coalition.py` (~line 408-425)

**Changes:**
- Count each nation's number of adjacent enemy nations
- Scale friction inversely: `friction_per_neighbor = base_friction / max(1, adjacency_count - 1)`
- Cap total friction received per nation per turn at a reasonable ceiling (e.g., -6 total, not -3 per neighbor x 5 neighbors = -15)

**Test:** Synthetic test with dense adjacency graph verifying friction doesn't create perpetual war spiral.

---

### 5.4 Optional Scenario Objectives Hook

**Implements:** DG-5 only if a later scenario explicitly opts into hard objectives.

**Status:** Deferred. Not required for the first Europe prototype.

**Contract:** If a later scenario wants hard objectives, it must author them through optional `objectives_profile` data. Do not revive a single global `VICTORY_REGION_FRACTION` rule for all campaigns.

---

### 5.6 Bilateral Diplomacy O(N^2) Mitigation

**Problem:** At 15 nations = 105 bilateral pairs. Trade income, AI proposals, coalition checks all iterate pairs.

**File:** `diplomacy.py` (~line 2823, trade income iteration)
- Cache trade income per-turn, only recalculate on treaty change

**File:** `ai_diplomacy.py` (~line 570, proposal evaluation)
- Throttle: each AI nation evaluates proposals for at most 3 target nations per turn (prioritized by relationship + threat)
- Skip proposal evaluation for nations with active proposals pending

**File:** `ai_diplomacy.py` (~line 1211, coalition rivalry)
- Only check adjacency degradation for nations currently at peace (skip nations already at war)

---

## Phase 6: UI Density

**When:** During first Europe prototype, after gameplay scaling.
**Why:** UIs designed for 5-10 items break at 40+. Not crash bugs, but unnavigable.
**Estimated effort:** 1-2 sessions.

### 6.1 Marshal Management Pagination

**File:** `marshal_management.gd`

**Changes:**
- Replace single scrollable list with paginated view (10 marshals per page)
- Page navigation via arrow keys or prev/next buttons
- Number keys 1-9 select within current page, 0 = next page
- Filter buttons: "All / By Region / By Status"
- Lazy-load relationship sections (collapsed by default, expand on click)
- Reduce card height from 320px to responsive sizing

---

### 6.2 Strategic Ledger Sectioning

**File:** `strategic_ledger.gd` (~line 169-258)

**Changes:**
- Split marshal list by location or status (e.g., "In Combat / Marching / Idle")
- Each section collapsible, collapsed by default except "In Combat"
- Lazy-render: only build BBCode for expanded sections
- Keep existing number-key sub-tab switching

---

### 6.3 Incremental Map Updates

**File:** `map_renderer_base.gd` (~line 603-627, `_rebuild_dynamic_nodes()`)

**Changes:**
- Track which regions changed since last update (dirty-region set)
- Only rebuild force/garrison nodes for dirty regions
- `update_all_regions()` accepts optional `changed_regions` list; if provided, only updates those
- Full rebuild remains available for turn transitions

---

### 6.4 Diplomatic Ledger Collapsibles

**File:** `diplomatic_ledger.gd`

**Changes:**
- AI-AI relations section collapsed by default
- Each nation's relations expandable independently
- "Show major powers only" toggle to hide minor nations
- Group nations by relevance (at war with player, allied, neutral, minor)

---

### 6.5 Talleyrand Advisory Prioritization

**Implements:** GD6 from audit.

**File:** `diplomatic_advisory.py`

**Changes:**
- Rank nations by threat + relevance to player
- Top 3 recommendations shown by default, rest collapsed under "Other nations..."
- Add "Most urgent" framing: "Your Majesty, the most pressing matter is Prussia's mobilization..."
- Advisory text acknowledges when it's deliberately omitting minor nations

---

## Phase 7: Post-Prototype Polish

**When:** After first playable Europe prototype exists and has been playtested.
**Why:** These are real improvements but don't block a working prototype.
**Estimated effort:** 1-2 sessions.

### 7.1 Tooltip Caching

**File:** `map.gd` (~line 1553-1579)

Cache tooltip text per region. Regenerate only when region data changes (capture, battle, marshal movement). Eliminates O(n^2) relationship scan on every hover.

### 7.2 All-Pairs Distance Precomputation

**File:** `world_state.py`

Floyd-Warshall at map load time for O(1) distance lookup. Invalidate and recompute on region capture. Only worth doing if LRU cache from Phase 2.1 shows insufficient hit rate.

### 7.3 Save File Migration

**File:** `save_manager.py`

Handle loading 19-region saves into 80-region world. New regions initialize with default controller, no marshals. Warn player that saved game is from smaller map.

### 7.4 Coalition Full Retuning

**File:** `coalition.py`

After playtesting with real Europe prototype: adjust threat thresholds, friction rates, formation criteria, and dissolution timers for the actual nation count and density.

---

## Tracking Checklist

| # | Item | Phase | Status | Session |
|---|------|-------|--------|---------|
| DG-1 | Nation roster decision | 0 | DECIDED | April 17, 2026 |
| DG-2 | Diplomacy model decision | 0 | DECIDED | April 17, 2026 |
| DG-3 | Supply lines decision | 0 | DEFERRED | April 17, 2026 |
| DG-4 | War cascade policy | 0 | DECIDED | April 17, 2026 |
| DG-5 | Campaign objectives / victory conditions | 0 | DECIDED | April 17, 2026 |
| DG-6 | Pacing (turns, AP) | 0 | DECIDED | April 17, 2026 |
| DG-7 | Dispatch density | 0 | DECIDED | April 17, 2026 |
| 1.1 | Nation config test | 1 | DONE | April 16, 2026 |
| 1.2 | Fix hardcoded `== 19` | 1 | DONE | April 16, 2026 |
| 1.3 | Adjacency connectivity test | 1 | DONE | April 16, 2026 |
| 1.4 | Validator derives `VALID_NATIONS` from `NATION_CAPITALS` | 1 | DONE | April 16, 2026 |
| 2.1 | Cache `get_distance()` | 2 | DONE | April 19, 2026 |
| 2.2 | Wire spatial index into AI | 2 | DONE | April 19, 2026 |
| 2.3 | Extend fog to all AI nations | 2 | DONE | April 19, 2026 |
| 3.1 | Nation config factory | 3 | | |
| 3.2 | Frontend loads adjacency from backend | 3 | DONE | April 19, 2026 |
| 3.3 | Centralize nation colors | 3 | DONE | April 19, 2026 |
| 3.4 | Fix prompt/parser/validator hardcoding | 3 | DONE | April 19, 2026 |
| 4.1 | Province registry schema | 4 | | |
| 4.2 | External bitmap loading | 4 | | |
| 4.3 | Color-map validator | 4 | | |
| 4.4 | Unwired province support | 4 | | |
| 5.1 | Direct-only war entry + refusal event | 5 | | |
| 5.2 | Categorized dispatch sections + priority escalation | 5 | | |
| 5.3 | Coalition friction scaling | 5 | | |
| 5.4 | Hegemony victory check | 5 | | |
| 5.5 | Scenario-configured pacing loader | 5 | | |
| 5.6 | Bilateral diplomacy O(N^2) | 5 | | |
| 6.1 | Marshal management pagination | 6 | | |
| 6.2 | Strategic ledger sectioning | 6 | | |
| 6.3 | Incremental map updates | 6 | | |
| 6.4 | Diplomatic ledger collapsibles | 6 | | |
| 6.5 | Talleyrand advisory prioritization | 6 | | |
| 7.1 | Tooltip caching | 7 | | |
| 7.2 | All-pairs distance precomputation | 7 | | |
| 7.3 | Save file migration | 7 | | |
| 7.4 | Coalition full retuning | 7 | | |

---

## Key Principle

> The audit's most important finding: **Europe scaling is a game design problem first, code problem second.** Optimizing BFS and extending fog while leaving game mechanics unchanged produces a fast, fair, and completely unplayable Europe campaign. Phase 0 design gates exist because the code roadmap must follow from design decisions, not precede them.
