# War Purpose + Score Semantics Spec

> **Status:** Draft v1.0
> **Date:** April 16, 2026
> **Phase placement:** Design Refinement queue item 3. After `Memory and Pressure` (substrate shipped) and `Bilateral Peace Hardening` (queue item 2). Before `War Bargains` (queue item 3.5).
> **Origin:** War System Overhaul items in `DESIGN_REFINEMENT.md` §War System Overhaul: War Objectives + Ticking War Score, Vassalage Power Cap, Forced Alliance, Liberation. Playtest audit (March 29, 2026) identified defensive-play dominance and war-score opacity as core balance problems.
> **Companion docs:** `DIPLOMACY_SPEC.md` (§5c war declaration, §6e war score formula), `COALITION_SPEC.md` (threat from war actions), `WAR_BARGAIN_SPEC.md` (war-objective settlement hook, §2), `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` (later), `BILATERAL_PEACE_HARDENING_SPEC.md` (peace preview extensibility)

---

## 1. Purpose

This spec defines **why wars start**, **what war score means politically**, and **what settlements can legitimately do**.

Today, wars in Sovereign Map start for one reason (France declares war) and score for one purpose (generic military pressure). Territory, battles, and capital control produce a number between -100 and +100 that shifts acceptance formula results, but the number has no political identity. The player never chooses what they are fighting for, and the game never tells them what victory entitles them to.

This creates three failures:

1. **Defensive play dominance** — holding ground scores identically to advancing. There is no ticking incentive to pursue objectives.
2. **Settlement illegibility** — war score says "you're winning" but not "you've earned the right to demand X."
3. **War sameness** — every war is mechanically identical. A punitive expedition to seize Rhineland looks the same as a war to subjugate Prussia entirely.

This spec adds war objectives, ticking war score, power-gated vassalage, forced alliance, and liberation — giving wars political purpose and making score meaningful.

---

## 2. Problems To Solve

### P1. No declared war purpose

When France declares war, the game records who attacked whom and tracks a bilateral war score. But France never states why — there is no casus belli system beyond a binary flag, no chosen objective, and no political framing. This makes wars feel mechanical rather than political.

### P2. Defensive play is optimal

The current war score formula (DIPLOMACY_SPEC §6e) rewards territory held (+5 per enemy starting region), battles won (+3 each), decisive battles (+10 each), and capital capture (+20). All of these are **one-time** bonuses. Once France captures Rhineland, the +5 is permanent whether France holds it for 1 turn or 20. There is no reason to hold forward positions — the score is the same.

This means the optimal strategy is to raid, score, and retreat to defensible positions. Historically, this is the opposite of Napoleonic warfare, where holding conquered territory was the prerequisite for dictating peace.

### P3. Vassalage has no power gate

France can vassalize Austria (a great power with 60,000 troops and 4 regions) if war_score exceeds 60 and France holds Vienna. Historically, Napoleon vassalized Saxony, Bavaria, and the Confederation of the Rhine — **minor states** — not great powers. The current system has no concept of "this nation is too powerful to vassalize."

### P4. No forced-alliance mechanic

Napoleon's primary war objective was often forced alliance (Tilsit with Russia, Pressburg with Austria). The current system can upgrade diplomatic state through the acceptance formula, but there is no "war goal forces this specific outcome." The player must manually propose alliance after peace, with no mechanical advantage from having won the war for that purpose.

### P5. No liberation mechanic

Coalition wars historically aimed to liberate French client states (Bavaria, Saxony, Westphalia). The current system has no war objective for this — coalitions fight to reduce war score, not to free specific nations.

### P6. War score has no political interpretation

War score is a number. +45 means "France is winning." But does +45 entitle France to demand Rhineland? Vassalize Saxony? Force alliance? The player has no framework for what a given score "means" in settlement terms — they must trial-and-error through the acceptance formula.

---

## 3. Goals

- Add **war objectives** chosen at declaration time that frame the political purpose of a war.
- Add **ticking war score** as a 5th component: holding the objective's target region accumulates score over time, creating an incentive to advance and hold rather than raid and retreat.
- Add a **vassalage power cap**: only nations below a national power threshold can be vassalized.
- Add a **forced alliance** clause type: a war goal that forces the defeated nation into ALLIANCE + Continental System membership.
- Add a **liberation** war goal: coalition wars can target the release of French vassals.
- Add **war score legibility**: map war score ranges to named settlement tiers so the player knows what their score entitles them to demand.
- Keep the existing war score formula (territory + battle + decisive + capital) intact as the first four components. Ticking is the 5th, additive component.

---

## 4. Non-Goals

- No common peace or allied settlement allocation. Those belong to `Ally Participation + Common Peace` (queue item 4).
- No dynamic power tiers with per-turn recalculation. Power scoring for the vassalage cap is evaluated at vassalage-proposal time, not tracked as a per-turn state.
- No multi-objective wars (one objective per war per nation in v0.1).
- No AI-selected Subjugation or Forced Alliance in v0.1. AI-vs-player wars rely on the defender's auto-Defense objective; AI-AI opportunistic wars default to Conquest so the war has a readable purpose.
- Coalition settlement mechanics are deferred to WPS-C, but WPS-A records coalition-side Liberation/Defense objectives and ticking when coalition wars form.
- No war-exhaustion rework. The existing coalition war-exhaustion system (COALITION_SPEC §10a) remains independent.

---

## 5. Design Principle

War purpose follows one rule:

**Wars should resolve toward recognizable political outcomes, not generic pressure.**

That means:

- The player chooses what they are fighting for at declaration time
- Holding the objective over time earns score (ticking) — rewarding advance, not stagnation
- Score translates into named settlement tiers: the player knows "at +60, I can demand vassalage"
- Settlement legitimacy gates (power cap, forced alliance, liberation) constrain what victory can actually produce
- AI wars have auto-assigned purposes that the player can read

---

## 6. War Objectives

### 6.1 Objective types

Five objective types, divided into player-chosen (offensive) and auto-assigned (defensive/reactive):

| Objective | Chooser | Ticking Target | Ticking Rate | Score Cap | Description |
|-----------|---------|----------------|--------------|-----------|-------------|
| **Conquest** | Player (offensive); AI-AI default | Enemy capital | +2/turn | +25 | Seize and hold the enemy capital to dictate terms |
| **Subjugation** | Player (offensive) | Enemy capital | +3/turn | +25 | Total defeat — vassalize the enemy (requires power cap clearance) |
| **Forced Alliance** | Player (offensive) | Enemy capital | +2/turn | +25 | Force enemy into ALLIANCE + Continental System |
| **Defense** | Auto (defender) | Any enemy-held friendly region | +1/turn per region | +25 | Reclaim lost territory |
| **Liberation** | Auto (coalition) | Each vassal capital held by France | +1/turn per capital | +25 | Free French client states |

**Auto-assignment rules:**

- **Defense** is assigned automatically to the nation that was attacked (the target of `declare_war()`). The defender does not choose — defense is always the reactive objective.
- **Liberation** is assigned automatically to coalition members when France holds vassal capitals. The coalition does not choose — liberation is always a coalition-driven objective.
- France receives the same automatic **Defense** objective when attacked. Because France is the player, France may upgrade that auto-defense objective once via `set_war_purpose` to Conquest, Forced Alliance, or (if applicable) Subjugation. Keeping Defense is valid and continues to tick under the Defense rules.

### 6.2 Objective selection flow

**At war declaration time:**

1. Player types "declare war on Prussia"
2. Parser routes to `_execute_declare_war()` in `diplomatic_executor.py`
3. **NEW:** Before war fires, a **War Purpose popup** surfaces:
   - Lists available objectives for this target (Conquest always available; Subjugation if power cap allows; Forced Alliance always available)
   - Shows ticking rate and political consequence for each
   - Player selects one objective
   - The popup returns the chosen objective as a `war_objective` field on the staged war-declaration command result; `_execute_declare_war()` reads it before mutating war state
   - War declaration fires with the chosen objective

4. If player backs out of objective selection, war declaration is cancelled (no DP spent)

**When France is attacked:**

1. Enemy AI declares war on France (or cascade pulls France into war)
2. No automatic War Purpose popup — France begins with an auto-assigned Defense objective
3. Player may upgrade Defense once during the war via "set war purpose [Conquest/Subjugation/Forced Alliance] against [nation]" command
4. Setting or upgrading an objective costs 0 AP (it is a political declaration, not an action). A non-Defense objective can only be set once per war — changing mid-war is not allowed in v0.1.

**Action-wiring trace:** `set_war_purpose` follows CLAUDE.md "Adding a New Action": add to `VALID_ACTIONS`, parser valid-actions, `_action_costs` in `world_state.py` (0 AP), mock parser keywords (`set war purpose`, `war purpose`), `ACTION_DISPLAY`, and campaign-log type `war_objective_declared`.

### 6.3 Objective validation

**Conquest:**
- Always valid when declaring war
- Target: enemy capital region

**Subjugation:**
- Valid only if target nation's national power ≤ 50% of France's national power (see §8 Power Cap)
- Target: enemy capital region
- If power cap check fails, Subjugation is greyed out in the War Purpose popup with reason: "Prussia is too powerful to subjugate. National power: 72% of France."

**Forced Alliance:**
- Always valid when declaring war
- Target: enemy capital region
- Historical context: Napoleon's primary diplomatic weapon

**Defense:**
- Auto-assigned to the attacked nation
- Target: any enemy-held region belonging to the defender
- Ticking accumulates on *all* held regions simultaneously (+1/turn per region), not just one

**Liberation:**
- Auto-assigned to coalition members
- Valid only when France holds at least one vassal capital
- Target: each vassal capital under French control
- Ticking accumulates on *all* held vassal capitals simultaneously (+1/turn per capital)

### 6.4 Objective persistence

Objectives are stored under the war's canonical `diplo_key`, then under the declaring nation. This keeps one war record while allowing both sides to maintain separate objectives:

```python
world.war_objectives[diplo_key] = {
    "France": {
        "type": "conquest",              # conquest | subjugation | forced_alliance | defense | liberation
        "declaring_nation": "France",
        "target_nation": "Prussia",
        "target_regions": ["Berlin"],     # ticking target(s)
        "accumulated_ticking": 0,
        "created_turn": 5,
        "ticking_active": False,          # True once target region is held
        "objective_met_turn": None,       # turn when ticking cap reached (informational)
    },
    "Prussia": {
        "type": "defense",
        "declaring_nation": "Prussia",
        "target_nation": "France",
        "target_regions": ["Berlin", "Rhineland"],
        "accumulated_ticking": 0,
        "created_turn": 5,
        "ticking_active": False,
        "objective_met_turn": None,
    },
}
```

**Defense target_regions** includes all regions whose `starting_controller` matches the defending nation at war-declaration time — not just the capital.

Each side of the war may have its own objective. France may have `conquest` while Prussia has `defense`. Both accumulate ticking independently toward the same war's score.

---

## 7. Ticking War Score

### 7.1 The 5th component

Ticking war score is the 5th component of the war score formula. The existing four components (territory, battle, decisive battle, capital) are unchanged.

```python
war_score = territory_score + battle_score + decisive_battle_bonus + capital_score + ticking_score
```

### 7.2 Ticking rules

Ticking accumulates each turn when the declaring nation **holds** the target region(s):

```python
if objective.type == "conquest":
    if world.regions[target].controller == declaring_nation:
        objective["accumulated_ticking"] += 2
elif objective.type == "subjugation":
    if world.regions[target].controller == declaring_nation:
        objective["accumulated_ticking"] += 3
elif objective.type == "forced_alliance":
    if world.regions[target].controller == declaring_nation:
        objective["accumulated_ticking"] += 2
elif objective.type == "defense":
    for region in target_regions:
        if world.regions[region].controller != declaring_nation:
            # enemy or third party holds our region — tick
            objective["accumulated_ticking"] += 1
elif objective.type == "liberation":
    for capital in vassal_capitals:
        if world.regions[capital].controller == "France":
            # France still holds vassal capital — tick for liberator
            objective["accumulated_ticking"] += 1

objective["accumulated_ticking"] = min(objective["accumulated_ticking"], 25)
objective["ticking_active"] = (objective["accumulated_ticking"] > 0)
```

**Direction convention:** Ticking always contributes positively to the declaring nation's war score. For Defense objectives where the enemy holds regions, the ticking represents the defender's mounting political pressure to reclaim territory — it adds to the *defender's* score (which subtracts from France's war_score since the formula is relative).

**Defense controller convention:** In v0.1, defense ticking fires whenever a target region's controller is not the defending nation, regardless of which nation currently holds it. Third-party occupation is rare on the current map. A future generalization may restrict this to the specific war opponent if multi-party occupation becomes common.

### 7.3 Ticking contribution to war score

The ticking component is the declaring nation's accumulated ticking minus the opposing nation's accumulated ticking:

```python
war_obj = war_objectives.get(diplo_key, {})
ticking_a = war_obj.get(nation_a, {}).get("accumulated_ticking", 0)
ticking_b = war_obj.get(nation_b, {}).get("accumulated_ticking", 0)
ticking_score = ticking_a - ticking_b  # clamped by total war_score ±100 cap
```

### 7.4 Ticking does not decay

Unlike battle score (which decays at -2/turn after 3 turns of no battles), ticking score is permanent once accumulated. Holding territory for 10 turns represents a durable political claim, not fading momentum.

### 7.5 Ticking and the existing war score decay

The existing -2/turn battle score decay (DIPLOMACY_SPEC §6e) is unchanged. It still applies only to the battle component before ticking score is added. Implementations must not subtract decay from the final stored `war_scores` total, because that would decay ticking score too. Ticking provides the strategic counterweight: battles give immediate score that fades, objectives give slow score that sticks.

### 7.6 Ticking pauses during armistice

If the two nations are at ARMISTICE, ticking pauses for both sides. Territory control may not change during armistice (no combat), so continued ticking would reward passive waiting. Ticking resumes if the armistice ends and war resumes.

---

## 8. Vassalage Power Cap

### 8.1 National power formula

National power is evaluated at the moment of vassalage proposal or conquest-vassalage check:

```python
def calculate_national_power(nation: str, world) -> int:
    """Calculate national power from controlled regions and vassal contribution."""
    power = 0

    # Base: sum of income_value for all controlled regions
    for region in world.regions.values():
        if region.controller == nation:
            power += region.income_value

    # Vassal contribution: 50% of vassal regions' income
    for vassal_nation, vassal_data in world.vassals.items():
        if vassal_data.get("lord") == nation:
            for region in world.regions.values():
                if region.controller == vassal_nation:
                    power += region.income_value // 2

    return power
```

**Implementation note:** This helper is evaluated at vassalage proposal / conquest-vassalage check time, not as a per-turn hot path. If one proposal evaluation needs multiple national-power reads, cache the result for that evaluation or per `world.current_turn` so the `world.regions.values()` scan does not violate CLAUDE.md Golden Rule 8 at scale.

### 8.2 Power cap rule

A nation can be vassalized (treaty or conquest) only if:

```python
target_power = calculate_national_power(target, world)
france_power = calculate_national_power("France", world)
if target_power > france_power // 2:
    # Vassalage blocked — target too powerful
```

This is a **hard gate**, not a soft penalty. If the target is too powerful, vassalage proposals are blocked and conquest-vassalage does not trigger.

### 8.3 Power cap display

When the power cap blocks vassalage:

- **Treaty path:** Vassalage option greyed out in diplomacy wizard. Tooltip: "[Nation] is too powerful to vassalize (power: X% of France's)."
- **Conquest path:** When France holds enemy capital + war_score > 60 but target exceeds power cap, the capture result says "Prussia submits, but France cannot impose vassalage on so large a nation. Demand terms at the peace table instead."
- **War Purpose popup:** Subjugation objective greyed out with power ratio display.

### 8.4 Power cap interaction with territory

Territory cessions in a peace deal change the power calculation. If France demands three regions from Prussia and then proposes vassalage in the same treaty package, the power check should evaluate **post-cession** power, not pre-cession. This prevents the absurdity of "Prussia is too powerful to vassalize, but if you take all their regions first..."

Implementation: evaluate power cap after applying all territory-transfer clauses in the same package, before evaluating the vassalage clause.

Use a pure projection helper for preview and ratification validation:

```python
project_power_after_terms(world, terms, proposer, target) -> dict[str, int]
```

Rules:

1. Build a local `projected_controller_by_region` map from the current world state; do not mutate `WorldState`.
2. Apply only valid same-package territory-transfer clauses in proposal order. Invalid region names, duplicate transfers, or transfers from a nation that no longer controls the region are ignored by the projection and handled by normal treaty validation.
3. Compute projected national power from the projected controller map plus the existing naval-income and vassal-contribution rules in §8.1.
4. Use the same helper for treaty preview and final ratification validation so a saved or delayed proposal cannot pass with stale pre-cession power.
5. Vassalage-cap validation reads the projected values for France and the target after cession terms, before the vassalage clause itself changes subject status.

### 8.5 Starting power values (19-region map)

| Nation | Controlled Regions | Base Income Sum | Naval | Power |
|--------|-------------------|----------------:|------:|------:|
| France | Paris(300) + Normandy(100) + Brittany(50) + Bordeaux(50) + Lyon(200) + Marseille(150) + Belgium(100) + Milan(150) | 1,100 | 0 | 1,100 |
| Britain | Netherlands(50) + Waterloo(50) + Hanover(100) | 200 | 200 | 400 |
| Prussia | Berlin(300) + Rhineland(100) | 400 | 0 | 400 |
| Austria | Bavaria(100) + Vienna(300) + Bohemia(150) + Tyrol(100) | 650 | 0 | 650 |
| Saxony | Saxony(150) + Dresden(100) | 250 | 0 | 250 |

**Naval income formula:** `min(300, 150 + 50 * coastal_count)`. Britain starts with 1 coastal region (Netherlands) → 200 naval income. Capturing more coastal regions (Normandy, Brittany, Bordeaux, Marseille) increases naval power up to the 300 cap.

**Power cap check at game start:**
- France (1,100) can vassalize: Saxony (250 = 23%), Prussia (400 = 36%), Britain (400 = 36%) — all under 50%
- France (1,100) **cannot** vassalize: Austria (650 = 59%) — exceeds 50% cap

This is historically accurate. Napoleon vassalized Saxony, the Rhineland states, and Italian principalities — never Austria or Prussia as great powers. After Tilsit, he forced alliance on Russia and Prussia, not vassalage.

**Note on Britain:** British naval income is included in power calculation. Britain starts at 200 naval income from the formula above and can rise to the 300 cap with additional coastal regions. This is intentional — Britain's power projection is real even without continental territory. Excluding naval income would make Britain appear weaker than Saxony, which is ahistorical.

### 8.6 Power cap and war objectives

The Subjugation war objective is gated by the same power cap:

- At war declaration time, if target exceeds 50% of France's power, Subjugation is unavailable
- If territory changes during the war shift the power balance (France conquers regions, increasing French power; target loses regions, decreasing target power), the cap is not re-evaluated mid-war. The objective check is at declaration time only.
- If the player set Conquest and the target's power drops below 50% during the war, the player may not retroactively switch to Subjugation (no objective changes mid-war in v0.1)

---

## 9. Forced Alliance

### 9.1 New clause type

Add a new treaty clause type: `forced_alliance`

```python
{
    "clause_type": "forced_alliance",
    "from_nation": "Prussia",         # the defeated nation being forced
    "to_nation": "France",            # the victor imposing alliance
    "includes_continental_system": True,
    "term_direction": "demand",
    "sweetener_value": -20,           # significant demand
    "display_label": "Prussia enters ALLIANCE with France and joins the Continental System"
}
```

Validity: if the target is already at `ALLIANCE` with France, the `forced_alliance` clause is invalid and greyed out in the proposal wizard. The clause imposes alliance on an enemy; it does not reinforce or re-label an existing voluntary alliance.

### 9.2 Mechanical effect

On treaty ratification containing `forced_alliance`:

1. Diplomatic state between the two nations is set directly to `ALLIANCE` (skipping intermediate states)
2. Target nation is added to `continental_system_members` if `includes_continental_system` is True
3. Relation modifier: forced alliance starts with relation = 0 (reset from whatever war-negative it was). The alliance is imposed, not earned — relation reflects grudging compliance, not friendship.
4. All active war states between the two nations end (WAR → ALLIANCE, including any armistice)
5. Ratification fires `cleanup_war_end()` before setting state to `ALLIANCE`, clearing `war_scores`, `battle_records`, `decisive_battles`, and `war_start_turns`, and cancelling strategic orders per DIPLOMACY_SPEC §5b.4.

### 9.3 Acceptance formula for forced alliance

Forced alliance uses the existing acceptance formula with modified base disposition:

```python
base_disposition = -15  # 45 below standard peace base 30 — nations resist forced alignment
```

Implementation: detect `forced_alliance` in the treaty clause list and override `base_disposition` to -15 before summing acceptance modifiers. Do not add a standalone proposal type.

Additional modifiers:

- War score > 70 AND capital held: +25 (Military Supremacy, same as existing §6b.1)
- Forced alliance is a **war reparation tier** demand: acceptance penalty of -20 (same tier as AP/turn demands)
- Combined: at war_score 80 with capital held, forced alliance is achievable but requires favorable conditions (relation, threat, sweeteners)

### 9.4 Forced alliance and war objectives

If France declared war with the **Forced Alliance** objective:

- The Forced Alliance clause is pre-populated in the peace proposal wizard as the primary demand
- Ticking war score accumulated under this objective contributes to the war score that drives acceptance
- The war summary in peace preview (per BILATERAL_PEACE_HARDENING_SPEC §8) shows "War Purpose: Forced Alliance" and the ticking progress

If France declared a different objective (Conquest, Subjugation), forced alliance is still available as a treaty clause — the objective does not restrict available terms. The objective only determines what ticks.

### 9.5 Forced alliance stability

A forced alliance is mechanically identical to a voluntary alliance after ratification, with two differences:

1. **Origin tag:** `world.alliance_origins[diplo_key] = "forced"` on ratification. Voluntary alliances either omit the key or store `"voluntary"`. In v0.1 the tag drives only the forced-alliance drift below; future systems (nation agendas, AI resentment) may read it.
2. **Automatic downgrade pressure:** Forced alliances apply an extra -10/turn to the relation between the two nations (on top of any existing drift). This means forced alliances naturally decay toward the -30-below-threshold auto-downgrade within ~5-8 turns unless France actively maintains the relationship. Historically accurate — Napoleon's forced alliances (Tilsit, Pressburg) eroded rapidly once French military pressure waned.

Lifecycle rules for `alliance_origins`:

- Set `alliance_origins[diplo_key] = "forced"` only when a `forced_alliance` clause ratifies.
- Set `"voluntary"` only when an ordinary alliance treaty ratifies without a forced-alliance clause.
- If the same pair later ratifies another `forced_alliance` clause, keep or reset the origin to `"forced"`; do not overwrite it with `"voluntary"` in the same ratification.
- Clear the key when the diplomatic state drops below `ALLIANCE`, the pair enters `WAR`, or a vassal relationship supersedes the alliance.
- Apply the -10/turn forced-alliance drift only while the current state is `ALLIANCE` and `alliance_origins[diplo_key] == "forced"`.

### 9.6 Forced alliance and threat

Forcing alliance generates threat: +15 (between treaty vassalage at +5 and conquest vassalage at +25 — courts view forced alignment as more alarming than a willing client state but less than outright conquest).

Authoritative threat source: `COALITION_SPEC.md` §2a row `Force alliance in peace deal`. This is a coalition threat source only; it does not create a standalone acceptance `threat_modifier`.

### 9.7 Forced alliance and coalitions

Forced alliance membership does not prevent the forced nation from joining a coalition against France. If threat rises and a coalition forms, the forced alliance creates a contradiction — the forced nation must choose (per DIPLOMACY_SPEC §5b.3 conflicting alliance obligations). In practice, a forced nation at low relation with France will likely choose the coalition, breaking the forced alliance.

This is the historical dynamic: Napoleon's forced allies defected the moment a viable coalition formed.

---

## 10. Liberation

### 10.1 Liberation war goal

Liberation is a coalition-side war objective: free nations that France has vassalized.

```python
{
    "type": "liberation",
    "declaring_nation": "Austria",      # coalition member
    "target_nation": "France",
    "target_regions": ["Dresden"],       # vassal capital(s) under French control
    "vassal_nations": ["Saxony"],        # which nations to liberate
    "accumulated_ticking": 0,
    "created_turn": 12,
}
```

### 10.2 Liberation trigger

Liberation is auto-assigned when:

- A coalition forms against France (COALITION_SPEC §3)
- France currently holds at least one vassal
- At least one vassal capital is under French control (directly or through vassal governance)

The liberation objective targets all current French vassal capitals. If France has multiple vassals, all are included in the same liberation objective.

### 10.3 Liberation ticking

+1/turn per vassal capital where France still controls the territory (directly or through the vassal's continued submission). The coalition accumulates score for the continuing existence of France's vassal empire.

### 10.4 Liberation settlement

On peace, if the coalition's war score justifies it, liberation clauses release French vassals:

```python
{
    "clause_type": "liberation",
    "vassal_nation": "Saxony",
    "from_nation": "France",           # France loses the vassal
    "sweetener_value": -15,            # significant demand on France
    "display_label": "Saxony is liberated from French vassalage"
}
```

Mechanical effect on ratification:

1. `release_vassal(world, "France", "Saxony")` fires
2. Saxony enters `DEFENSIVE_ALLIANCE` with the liberating coalition leader (not ALLIANCE — liberation creates gratitude, not forced alignment)
3. Saxony relation with France: -20 (resentment from subjugation period, unless loyalty was very high)
4. Saxony relation with liberator: +30
5. Threat reduction: -8 (same as voluntary vassal release)

### 10.5 Liberation and the acceptance formula

Liberation clauses are demands on France. Acceptance penalty:

- `-15` per vassal liberated (comparable to territory cession of 2-3 regions)
- Military Supremacy bonus still applies if coalition holds Paris and has high war score

### 10.6 Coalition liberation and separate peace

If a coalition member makes separate peace with France:

- That member loses the liberation objective
- Other coalition members retain the objective
- If the separating member was the sole holder of the liberation objective, it transfers to the next-highest-contribution coalition member

---

## 11. War Score Legibility

### 11.1 Settlement tiers

Map war score ranges to named settlement tiers. Display these in the War Status Panel and peace preview:

| War Score Range | Settlement Tier | What France Can Demand |
|----------------|----------------|----------------------|
| 0–19 | **White Peace** | Status quo ante, minor gold |
| 20–39 | **Favorable Terms** | Gold/turn, open borders, territory concessions (1-2 regions) |
| 40–59 | **Dictated Terms** | Territory (2-3 regions), forced Continental System, manpower |
| 60–79 | **Harsh Peace** | Territory (3+ regions), AP/turn, forced alliance (if capital held) |
| 80–100 | **Total Victory** | Vassalage (if power cap allows), forced alliance, punitive reparations |

**For negative war scores** (France losing), mirror the tiers — the enemy can demand proportionally harsher terms from France.

### 11.2 Tier display

The War Status Panel (`war_status_panel.gd`) shows the current settlement tier alongside the numeric war score:

```
WAR vs PRUSSIA
Score: +52 (Dictated Terms)
Objective: Conquest — Berlin [HELD, ticking +2/turn]
```

The peace preview panel (BILATERAL_PEACE_HARDENING_SPEC §8) includes the settlement tier in the war summary section.

### 11.3 Tier interaction with acceptance

Settlement tiers are **informational** — they describe what is politically plausible, not what is mechanically guaranteed. The acceptance formula still makes the final decision. A player at +52 who demands vassalage (Harsh Peace tier required) will see the acceptance formula reject it.

The tiers guide the player: "you need +60 before demanding forced alliance" is actionable information that prevents trial-and-error proposals.

### 11.4 Tier warnings in proposal wizard

When the player constructs peace terms that exceed their current tier:

```python
{
    "warning_type": "tier_mismatch",
    "current_tier": "dictated_terms",
    "demanded_tier": "harsh_peace",
    "severity": "WARNING",
    "display": "Your war score (+52) may not support these terms. Forced alliance typically requires Harsh Peace (+60)."
}
```

This warning integrates with the existing structured warnings system and the BILATERAL_PEACE_HARDENING_SPEC peace preview panel.

---

## 12. Data Model Additions

### 12.1 New WorldState fields

```python
# War objectives — keyed by diplo_key, then by declaring_nation.
# war_objectives[diplo_key][declaring_nation] = objective record
self.war_objectives: Dict[str, Dict[str, Dict]] = {}

# Forced alliance origin tracking
# Separate WorldState field keyed by diplo_key.
# alliance_origins[diplo_key] -> "forced" | "voluntary"
self.alliance_origins: Dict[str, str] = {}
```

### 12.2 War objective record shape

```python
{
    "type": str,                  # conquest | subjugation | forced_alliance | defense | liberation
    "declaring_nation": str,
    "target_nation": str,
    "target_regions": List[str],
    "accumulated_ticking": int,
    "created_turn": int,
    "ticking_active": bool,
    "objective_met_turn": Optional[int],
    "vassal_nations": List[str],  # liberation only
}
```

### 12.3 Serialization

- `war_objectives` added to `WorldState.to_dict()` / `from_dict()` with `.get("war_objectives", {})` default.
- `alliance_origins` added to `WorldState.to_dict()` / `from_dict()` with `.get("alliance_origins", {})` default.
- Run `pytest tests/test_serialization_enforcement.py -v` after implementation.
- Update `docs/SAVE_FORMAT_REFERENCE.md`.

### 12.4 Processing order in advance_turn()

Ticking accumulation runs after war score recalculation (step 4 in DIPLOMACY_SPEC §7f):

```
4.  War score recalculation — territory + quiet-turn-decayed battles + decisive + capital (§6e)
4a. War objective ticking — accumulate per §7.2, add to war score after battle-only decay (§7.3)
5.  Defection cascade check — if war score < -30, check vassals (§8d)
```

Implementation placement: in `process_diplomacy_turn(world)`, run ticking immediately after `apply_war_score_decay(world)` / battle-only score recomputation so future ticking is never consumed by battle decay.

Forced alliance auto-downgrade pressure (§9.5) runs before the automatic downgrade threshold check. Insert it as step 12a:

```
12a. Forced-alliance relation drift — for each `diplo_key` where current state is ALLIANCE and alliance_origins[diplo_key] == "forced", apply -10 relation drift.
13.  Automatic downgrade check — reads the post-drift relation and may downgrade if the pair has stayed 30+ below threshold for 5 turns.
```

Implementation placement: call forced-alliance drift immediately before `check_auto_downgrade(world)` so the downgrade check reads the post-drift relation.

### 12.5 War objective cleanup

When a war ends (peace ratified or transition out of WAR):

- The war objective record is preserved in `war_objectives` with a `"concluded_turn"` field added
- Concluded objectives do not tick
- Records are cleaned up after 10 turns (historical reference only, not mechanically active)

When a forced alliance later breaks:

- Clear `alliance_origins[diplo_key]` when the state drops below `ALLIANCE`, the pair enters `WAR`, or the relationship becomes `VASSAL`.
- If the same pair later ratifies a voluntary alliance, write `"voluntary"` and do not apply forced-alliance drift.

When an armistice begins:

- The war objective record is preserved, ticking pauses (§7.6)
- If the armistice transitions to PEACE, the objective concludes
- If the armistice is broken and war resumes, ticking resumes

---

## 13. AI Behavior

### 13.1 AI war declaration objectives

When AI declares war on France or on another AI nation:

- **Defensive response:** Auto-assigned `defense` objective (standard)
- **Coalition war:** Auto-assigned `liberation` if France has vassals; otherwise `defense`
- **Opportunistic war (future AI-AI wars):** Auto-assigned `conquest` by default

AI does not choose Subjugation or Forced Alliance in v0.1 — those are player verbs that give France its unique political-military toolkit.

### 13.2 AI peace timing with objectives

AI peace evaluation (`ai_diplomacy.py`) is extended:

- AI is **more willing** to accept peace when the enemy's ticking objective has high accumulated score (urgency to stop the clock)
- AI is **less willing** to accept peace when the AI's own defense ticking is accumulating (defender is gaining leverage over time)
- Specific modifier: `ticking_pressure = (opponent_ticking - own_ticking) // 5`, clamped to ±10, added to AI's internal peace-appetite evaluation

### 13.3 AI and power cap

AI vassalage proposals already use `calculate_acceptance()`. The power cap (§8) adds a hard pre-check: if target exceeds 50% of proposer's power, AI does not propose vassalage.

### 13.4 AI and forced alliance

AI does not propose forced alliance in v0.1. If France forces alliance on an AI nation:

- AI accepts if acceptance formula ≥ 50 (same as any treaty)
- Once in forced alliance, AI applies the -10/turn relation drift (§9.5)
- AI will break forced alliance via standard auto-downgrade when relation drops 30+ below threshold for 5 turns
- AI will choose coalition over forced alliance if coalition forms (§9.7)

### 13.5 AI liberation behavior

In coalition wars, AI coalition members with liberation objectives:

- Prioritize attacking vassal capitals (enemy AI decision tree extension)
- Accept peace terms that include liberation clauses
- Refuse peace terms that leave vassals in place when liberation was the objective and war score supports it

---

## 14. Player-Facing Surfaces

### 14.1 War Purpose popup (declaration)

New popup at war declaration time:

```
╔══════════════════════════════════════╗
║         WAR PURPOSE                  ║
║  France declares war on Prussia      ║
║                                      ║
║  Choose your objective:              ║
║                                      ║
║  [Conquest]                          ║
║    Seize Berlin. +2/turn while held. ║
║                                      ║
║  [Forced Alliance]                   ║
║    Force Prussia into alliance.      ║
║    +2/turn while Berlin held.        ║
║                                      ║
║  [Subjugation] (greyed)              ║
║    Prussia is too powerful (73%)     ║
║                                      ║
║  [Back Out]                          ║
╚══════════════════════════════════════╝
```

CanvasLayer 110 (modal, same range as existing diplomacy popups). Registers with `dialog_manager`.

### 14.2 War Status Panel extension

Extend `war_status_panel.gd` to show:

- War objective type and target
- Ticking status: "Berlin HELD — +2/turn (accumulated: +14)"
- Settlement tier: "Dictated Terms (+52)"
- For enemy objectives: "Prussia objective: Defense — recovering lost territory"

### 14.3 Peace preview extension

Extends BILATERAL_PEACE_HARDENING_SPEC §8.1 `war_context_snapshot` with:

```python
{
    ...existing fields...,
    "war_objective": {
        "type": "conquest",
        "target_regions": ["Berlin"],
        "accumulated_ticking": 14,
        "ticking_active": True
    },
    "settlement_tier": "dictated_terms",
    "tier_mismatch_warnings": []
}
```

### 14.4 Campaign log events

New campaign log event types:

| Event | Payload shape | One-liner template | Fog rule |
|-------|---------------|--------------------|----------|
| `war_objective_declared` | `{type, declaring_nation, target_nation, target_regions, turn}` | "{declaring_nation} declares {type} against {target_nation} (target: {target_regions})" | Public to all known courts. |
| `war_objective_ticking_started` | `{type, declaring_nation, target_region, accumulated_ticking, rate, turn}` | "{declaring_nation} holds {target_region} — ticking war score accumulating (+{rate}/turn)" | Visible to nations at war with `declaring_nation` and their allies. |
| `forced_alliance_imposed` | `{forced_nation, imposing_nation, treaty_location, includes_continental_system, turn}` | "Treaty of {treaty_location} forces {forced_nation} into alliance with {imposing_nation}" | Public to all known courts. |
| `vassal_liberated` | `{vassal_nation, former_lord, liberator_nation, turn}` | "{vassal_nation} liberated from {former_lord} by {liberator_nation}-led coalition" | Public to all known courts. |

Added to `CAMPAIGN_LOG_TYPES` in `campaign_log.py`.

### 14.5 Dispatch integration

Morning Dispatch includes:

- "War Purpose: Conquest — Berlin held for 7 turns (+14 accumulated ticking score)"
- "Settlement outlook: Dictated Terms (+52). Forced alliance achievable at +60."
- On forced alliance ratification: "The Treaty of [location] — Prussia enters forced alliance with France."
- On liberation: "Saxony has been liberated. Austria assumes defensive alliance with the former vassal."

Dispatch items use the same payload sources and fog rules as the campaign-log events in §14.4. If a court cannot see the underlying event, it does not receive the dispatch line.

---

## 15. Implementation Sequence

### Slice WPS-A: War objectives + ticking score (implemented with 50 tests after audit follow-up)

- Add `war_objectives` to WorldState with serialization
- Implement objective types (conquest, subjugation, forced_alliance, defense, liberation)
- War Purpose popup at declaration time
- Objective auto-assignment for defenders and coalition
- Ticking accumulation in `advance_turn()` after war score recalculation
- Ticking contribution to war score (5th component)
- Ticking pause during armistice
- Objective cleanup on war end
- Campaign log events for objective declaration and ticking start
- Wire `set_war_purpose` per CLAUDE.md "Adding a New Action": `VALID_ACTIONS` in `validation.py`, parser valid-actions, `_action_costs` in `world_state.py` (0 AP), mock parser keywords (`set war purpose`, `war purpose`), `ACTION_DISPLAY`, and campaign-log type `war_objective_declared`
- Tests: objective creation, validation, ticking accumulation, armistice pause, war score integration, serialization round-trip

### Slice WPS-B: Vassalage power cap (~15 tests)

- Implement `calculate_national_power()` function
- Hard gate on treaty vassalage proposals
- Hard gate on conquest-vassalage in capture flow
- Subjugation objective validation against power cap
- Post-cession power evaluation for treaty packages containing territory + vassalage
- Implement pure `project_power_after_terms(world, terms, proposer, target)` projection for preview and ratification validation; do not mutate `WorldState` during preview
- Power cap display in wizard and War Purpose popup
- Update starting power values documentation
- Tests: power calculation, cap enforcement (treaty + conquest), post-cession evaluation, edge cases (vassal contribution, naval income)

### Slice WPS-C: Forced alliance + liberation (~20 tests)

- Add `forced_alliance` clause type to treaty system
- Acceptance formula integration (base -15, reparation tier -20, Military Supremacy +25)
- Ratification: state jump to ALLIANCE + Continental System
- Relation reset to 0 on forced alliance
- Forced alliance origin tag (`alliance_origins`)
- `alliance_origins` lifecycle cleanup when alliance breaks, war resumes, or voluntary alliance replaces the forced origin
- Auto-downgrade pressure (-10/turn relation drift)
- Threat generation (+15) through `COALITION_SPEC.md` §2a; no acceptance `threat_modifier`
- Add `liberation` clause type
- Liberation settlement mechanics (release_vassal + DEFENSIVE_ALLIANCE with liberator)
- Liberation objective and ticking
- Coalition liberation and separate peace interaction
- Wire `forced_alliance` and `liberation` through the treaty pipeline: `_ratify_treaty()` handlers in `diplomacy.py`, harshness weights in `calculate_treaty_harshness()` / `diplomatic_templates.py`, `CLAUSE_DISPLAY` entries in `display_names.py`, `SWEETENER_VALUES` / `DEMAND_VALUES` entries in `diplomacy.py` (`forced_alliance: -20`, `liberation: -15`), and AI clause generation in `ai_diplomacy.py` (AI does not propose `forced_alliance` in v0.1; AI may propose `liberation` in coalition wars)
- Tests: forced alliance ratification, acceptance formula, origin tracking, auto-downgrade, liberation release, coalition interaction, threat

### Slice WPS-D: War score legibility + AI + surface polish (~18 tests)

- Settlement tier mapping and display
- War Status Panel extension (objective, ticking, tier)
- Peace preview extension with objective and tier data
- Tier mismatch warnings in proposal wizard
- Dispatch integration (objective status, settlement outlook)
- AI peace timing with ticking pressure
- AI power cap pre-check
- AI forced alliance response behavior
- AI liberation priority and peace evaluation
- Tests: tier classification, display correctness, AI ticking pressure modifier, AI power cap, AI liberation behavior

**Total: ~75 tests, ~4 sessions**

---

## 16. Risks

### R1. Ticking makes wars longer

If ticking rewards holding territory over time, players may stall wars to accumulate score rather than pursuing peace. **Mitigation:** +25 cap on ticking. After ~12 turns of conquest ticking, there is no further benefit. The cap is set low enough that ticking supplements the existing score components without dominating them.

### R2. Power cap frustrates late-game vassalage

If France conquers most of the map, its power rises and the 50% threshold becomes very permissive. Conversely, early-game vassalage of larger nations is blocked. **Mitigation:** this is the intended design. Early-game vassalage should be limited to minor nations (historically accurate). Late-game dominance should unlock more options. The 50% threshold creates a natural progression.

### R3. Forced alliance is too strong

If forced alliance gives France an instant full ally from a defeated enemy, it may be overpowered. **Mitigation:** relation starts at 0 with -10/turn extra drift. The alliance will naturally decay and break within 5-8 turns unless France invests heavily in maintaining it. This is a temporary political tool, not a permanent win condition.

### R4. Liberation breaks vassal gameplay

If coalition wars always liberate vassals, the player may never benefit from conquering them. **Mitigation:** liberation requires the coalition to win with sufficient war score. If France can defend its vassals militarily, they stay. The risk creates political tension: is this vassal worth the coalition anger?

### R5. Objective selection at declaration creates analysis paralysis

Three objectives (plus greyed subjugation) may slow down war declaration. **Mitigation:** objectives are simple to understand (conquest = seize capital, forced alliance = force alignment, subjugation = total control). The popup is one choice, not a configuration screen.

### R6. Defense ticking for AI creates runaway score

If multiple AI nations have Defense objectives with multiple held regions each, combined ticking could push AI war score very high very quickly. **Mitigation:** each objective has its own +25 cap. Even with 5 held regions ticking at +1/turn each, the cap prevents runaway. And combined ticking still competes with France's own ticking from the French objective.

### R7. Interaction with Bilateral Peace Hardening

If this spec ships before or after BILATERAL_PEACE_HARDENING_SPEC, the peace preview may be incomplete. **Mitigation:** both specs define extensible fields. War context snapshot (BPH §8.1) includes optional `war_objective` field that this spec fills. Settlement tier warnings (§11.4) integrate with BPH's structured warnings. Either order works.

---

## 17. Resolved Design Calls

- **One objective per war per nation:** Yes. Multi-objective wars would require an objective-priority system and split ticking. Complexity not justified in v0.1.
- **No mid-war objective changes:** Correct. Choosing an objective is a commitment — changing it mid-war would let the player game ticking by switching to whatever they're currently holding.
- **Ticking cap at +25:** Set to be meaningful (comparable to decisive battle bonus range ±20) but not dominant. The first four components can reach ±100; ticking adds ±25 on top, capped by the overall ±100 war_score limit.
- **Power cap at 50%:** Threshold that blocks Austria (59%) but allows Prussia (36%), Britain (36%), and Saxony (23%) at game start. Historically accurate dividing line.
- **Forced alliance includes Continental System:** Yes. Napoleon's forced alliances always included economic alignment. Makes the clause politically meaningful beyond military cooperation.
- **Liberation creates DEFENSIVE_ALLIANCE, not ALLIANCE:** Liberation is gratitude, not forced alignment. The liberator earns a defensive partner, not a military puppet. This mirrors historical patterns — liberated nations allied with liberators but maintained independence.
- **Naval income in power calculation:** Yes. Excluding it makes Britain appear weaker than Saxony, which is ahistorical and would make British vassalage trivially achievable.
- **AI offensive objective limits:** AI does not choose Subjugation or Forced Alliance in v0.1. AI-vs-player wars rely on the defender's auto-Defense objective; AI-AI opportunistic wars default to Conquest so status surfaces have a readable purpose.

---

## 18. Changelog

- **April 26, 2026** - WPS-A audit follow-up clarified France-on-defense semantics: attacked France receives auto-Defense and may upgrade it once with `set_war_purpose`; keeping Defense remains valid and ticking.

- **April 16, 2026** — v1.0 drafted. Covers war objectives (5 types), ticking war score (5th component), vassalage power cap (50% national power), forced alliance (new clause type), liberation (coalition war goal), war score legibility (settlement tiers). ~75 tests across 4 slices. Starting power values validated against DIPLOMACY_SPEC §1b region table. References WAR_BARGAIN_SPEC §2 (war-objective settlement hook), BILATERAL_PEACE_HARDENING_SPEC (peace preview extensibility), COALITION_SPEC (threat from forced alliance).
