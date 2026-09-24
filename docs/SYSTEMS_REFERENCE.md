# Ink & Iron: Systems Reference

Consolidated reference for all game systems. Read when modifying related code.

> **Shipped world (July 2, 2026):** the running game is the 20-nation / 126-province 1805 campaign (real-map cutover complete July 2, 2026). Legacy 5-nation / 19-region numbers in older sections below describe the test-fixture world unless marked otherwise.
>
> **Editorial note:** this doc contains duplicate section numbers (two §6b, two §17, two §18) from historical accretion — deliberately NOT renumbered, because cross-references elsewhere depend on them.

---

## Table of Contents

1. [Combat System](#1-combat-system)
2. [Disobedience & Trust](#2-disobedience--trust)
3. [Marshal State Machine](#3-marshal-state-machine)
4. [Strategic Commands](#4-strategic-commands)
5. [LLM Integration](#5-llm-integration)
6. [Cavalry Limits](#6-cavalry-limits)
6b. [Artillery Unit Type](#6b-artillery-unit-type)
7. [Redemption System](#7-redemption-system)
8. [Economy System](#8-economy-system)
9. [Fog of War](#9-fog-of-war)
10. [Manpower Pools](#10-manpower-pools)
11. [Campaign Log](#11-campaign-log)
12. [Top Bar & Screen Management](#12-top-bar--screen-management)
13. [Reinforcement System](#13-reinforcement-system)
14. [Win/Loss Relationship Formula](#14-winloss-relationship-formula)
15. [Phase 7 UI Integration (Session 66)](#15-phase-7-ui-integration-session-66)
16. [Diplomacy Data Layer](#16-diplomacy-data-layer)
17. [Coalition System](#17-coalition-system)
18. [War Declaration Command](#18-war-declaration-command)
19. [Ultimatum Command](#19-ultimatum-command)
20. [Diplomatic Trust Reactions](#20-diplomatic-trust-reactions)
21. [Diplomatic Reliability](#21-diplomatic-reliability)
22. [Popup Priority Queue](#22-popup-priority-queue)
23. [Building Blocks Principle](#23-building-blocks-principle)
24. [Map Renderer Architecture](#24-map-renderer-architecture)

---

## 23. Building Blocks Principle

All nations use identical **SYSTEMS** — same AP spending, same DP generation formula, same economy pipeline, same combat resolution, same executor. Nations differ in their **INPUT VALUES** (AP budget, DP pool, gold income, manpower regen, marshal personalities) representing each country's bureaucratic capacity, diplomatic skill, and economic power.

France may have 6 AP while Prussia has 4 — this represents Prussian bureaucratic limitations, not a different system. The rule is: **no parallel mechanics, no AI-only shortcuts.** AI nations spend AP the same way France does, just with different budgets.

### What Building Blocks means in practice:

| System | Same for all | Differs by nation |
|--------|-------------|-------------------|
| Combat | `resolve_battle()`, modifier formulas, coordination | Marshal personalities, skill values, unit types |
| Economy | `_execute_recruit()`, building costs, income formula | Region count, starting gold, manpower pools |
| Diplomacy | `calculate_dp()`, acceptance formula, state transitions | Diplomat skill, diplomat personality, starting relations |
| AI Actions | Same executor, same validation, same AP cost | AP budget per nation, priority weights |
| Coordination | Same co-location, reinforcement, flanking formulas | Relationship values, friction multipliers |

### Verified compliance:
- **DP generation:** `_process_dp_regen()` iterates all nations with same `calculate_dp()` formula
- **Combat:** AI attacks route through same `executor.execute()` as player
- **Admin phase:** AI uses same `_execute_recruit()`, `_execute_garrison()`, `_execute_build()`
- **Reinforcements:** Both sides receive reinforcements via same `_calculate_reinforcements()`
- **Coordination:** AI earns dedicated coordination through co-location duration (equivalent to player's SUPPORT order)

### What Building Blocks does NOT mean:
- AI does NOT need the same UI, parser, or strategic command system (AI uses priority tree, not NL parser)
- AI does NOT need the same information access (fog of war applies to player, AI is omniscient for decision-making but uses same combat math)
- AI CAN have different budget values — this is how difficulty and nation identity are expressed

**Key references:** `docs/VISION.md` §2, `docs/MULTI_MARSHAL_SPEC.md` §Building Blocks, `docs/COALITION_SPEC.md` §5d

---

## 1. Combat System

### Single-Source-of-Truth Pattern (CRITICAL!)

Combat modifiers are calculated in ONE place only. This prevents bugs where bonuses apply twice.

```
marshal.py                          combat.py
-----------------------------------  ---------------------------------
get_attack_modifier()               Uses marshal's modifier
  - Personality base bonus          Generates messages about bonuses
  - Stance modifier                 Handles state changes (drill consumed)
  - Drill/shock bonus               DOES NOT recalculate modifiers
  - Returns final multiplier

get_defense_modifier()              Uses marshal's modifier
  - Personality base bonus          Generates messages about bonuses
  - Stance modifier                 DOES NOT recalculate modifiers
  - Fortify bonus
  - Outnumbered bonus (Davout)
  - Returns final multiplier
```

### Attack Modifier Formula

From `marshal.py` `get_attack_modifier()`:

```python
modifier = 1.0

# Stance modifiers
if stance == AGGRESSIVE:
    modifier *= 1.15  # +15%
elif stance == DEFENSIVE:
    modifier *= 0.90  # -10%

# Drill/shock bonus
if shock_bonus > 0:
    modifier *= (1.0 + shock_bonus * 0.10)  # +20% if shock_bonus=2

# Strategic combat bonus (if any)
if strategic_combat_bonus > 0:
    modifier *= (1.0 + strategic_combat_bonus / 100.0)

# Personality modifiers (see get_attack_modifier_for_personality)
# - Aggressive: +15% base, +5% if aggressive stance, +5% if drill
# - Cautious: -5% if aggressive stance, -10% if bad odds
# - Literal: no special attack modifiers

# Recklessness bonus (aggressive + cavalry only)
modifier *= (1.0 + recklessness_attack_bonus)

# Exhaustion penalty (multiple attacks per turn)
modifier *= (1.0 - exhaustion_penalty)

return modifier
```

### Defense Modifier Formula

From `marshal.py` `get_defense_modifier()`:

```python
modifier = 1.0

# Stance modifiers
if stance == DEFENSIVE:
    modifier *= 1.15  # +15%
elif stance == AGGRESSIVE:
    modifier *= 0.90  # -10%

# Fortify bonus (stored as decimal)
if fortify_bonus > 0:
    modifier *= (1.0 + fortify_bonus)  # 0.16 = +16%

# Drilling penalty (caught drilling = vulnerable)
if drilling or drilling_locked:
    modifier *= 0.75  # -25%

# Personality modifiers (see get_defense_modifier_for_personality)
# - Aggressive: -5% if aggressive stance, -5% off defensive bonus
# - Cautious: +5% if defensive stance, +10% if outnumbered
# - Literal: +15% if holding position

# Recklessness penalty (aggressive + cavalry only)
modifier *= (1.0 - recklessness_defense_penalty)

return modifier

# Wellington's "Reverse Slope Defense": +5% defense always
if ability.name == "Reverse Slope Defense":
    modifier *= 1.05
```

### Marshal Signature Abilities

Each marshal has a unique ability defined in `marshal.py` ability dict (4 string fields: name, description, trigger, effect). Abilities are wired in either `marshal.py` (modifier-based) or `combat.py` (post-resolution effects), respecting Golden Rule #1.

| Marshal | Ability | Effect | Trigger | Location | Status |
|---------|---------|--------|---------|----------|--------|
| Ney | Bravest of the Brave | +2 Shock when attacking | `when_attacking` | `combat.py` (shock block) | Wired (Phase 2.3) |
| Drouot | Sage of the Grand Army | Fort degradation 10% → 15% on attack | `when_attacking_fortified` | `combat.py` (degradation block) | Wired (Phase 6.5) |
| Wellington | Reverse Slope Defense | +5% flat defense always | `when_defending` | `marshal.py` `get_defense_modifier()` | Wired (Phase 6.5) |
| Blucher | Vorwärts! | +3k pursuit casualties on retreat, floor 1000 | `when_enemy_retreats` | `combat.py` (pursuit block) | Wired (Phase 6.5) |
| Uxbridge | Pursuit Master | +5k pursuit casualties on retreat (cavalry), floor 1000 | `when_enemy_retreats` | `combat.py` (pursuit block) | Wired (Phase 6.5) |
| Davout | Counter-Punch Mastery | +20% attack after defending (any outcome, any target) | `after_defending` | `marshal.py` `get_attack_modifier()` + `combat.py` (trigger) | Wired |
| Grouchy | Literal Obedience | Never questions orders | `receiving_orders` | `disobedience.py` (partial) | Deferred |
| Gneisenau | Staff Work | +5% atk/def to allies in region | `when_in_same_region_as_ally` | — | Deferred (Phase 7 S58) |
| ArchdukeCharles | Habsburg Resolve | +3% flat defense always | `when_defending` | `marshal.py` `get_defense_modifier()` | Wired (Phase 8 S1B) |
| Schwarzenberg | — | — | — | — | Deferred |
| Reynier | — | — | — | — | Deferred |

**Pursuit system (Phase 6.5):**
- Fires when attacker wins AND defender has `forced_retreat=True` (morale ≤ 25)
- Only attacker's ability applies (no stacking)
- Uxbridge requires `cavalry=True` — infantry with same ability dict won't fire
- Floor: defender strength cannot go below 1000
- Pursuit casualties added to `defender_casualties` in result dict (included in totals)
- Result dict fields: `pursuit_damage` (int), `pursuit_message` (string or None)

**Fort degradation ability (Phase 6.5):**
- Base rates: infantry 5%, artillery 10%, Drouot 15%
- Only fires when `defender.defense_bonus > 0`
- Result dict field: `drouot_ability_triggered` (string or None)

### Combat Modifier Tables by Personality

#### NEY (Aggressive) -- "Bravest of the Brave"

| Modifier | Value | Condition | Code Reference |
|----------|-------|-----------|----------------|
| Base attack bonus | +15% | Always | `NEY_MODIFIERS["base_attack_bonus"] = 0.15` |
| Aggressive stance attack | +5% additional | `stance == AGGRESSIVE` | `NEY_MODIFIERS["aggressive_stance_attack_bonus"] = 0.05` |
| **Total aggressive stance attack** | **+20%** | Combined | |
| Aggressive stance defense | -5% | `stance == AGGRESSIVE` | `NEY_MODIFIERS["aggressive_stance_defense_penalty"] = 0.05` |
| Defensive stance defense | +10% only | `stance == DEFENSIVE` | `NEY_MODIFIERS["defensive_stance_defense_penalty"] = 0.05` (reduces from +15% to +10%) |
| Drill synergy | +5% additional | `shock_bonus > 0` | `NEY_MODIFIERS["drill_shock_bonus"] = 0.05` |
| Max fortify cap | 8% | Impatient *(B1: was 10%)* | `NEY_MODIFIERS["max_fortify_bonus"] = 0.08` |

**Behavioral Traits:**
- Objects to defensive orders (defend, wait, hold, retreat, fortify)
- Objects less if outnumbered 2:1+ AND morale <=40%
- Trust bonus for attack orders, penalty for prolonged defense

#### DAVOUT (Cautious) -- "Iron Marshal"

| Modifier | Value | Condition | Code Reference |
|----------|-------|-----------|----------------|
| Defensive stance defense | +5% additional | `stance == DEFENSIVE` | `DAVOUT_MODIFIERS["defensive_stance_defense_bonus"] = 0.05` |
| **Total defensive stance defense** | **+20%** | Combined with base +15% | |
| Outnumbered defense | +10% | `strength < attacker_strength` | `DAVOUT_MODIFIERS["outnumbered_defense_bonus"] = 0.10` |
| Aggressive stance attack | -5% | `stance == AGGRESSIVE` | `DAVOUT_MODIFIERS["aggressive_stance_attack_penalty"] = 0.05` |
| Bad odds attack | -10% | `strength_ratio < 1.0` | `DAVOUT_MODIFIERS["bad_odds_attack_penalty"] = 0.10` |
| Fortify rate | +3%/turn | Instead of +2% | `DAVOUT_MODIFIERS["fortify_rate_bonus"] = 0.01` |
| Max fortify cap | 12% | Patient defender *(B1: was 20%)* | `DAVOUT_MODIFIERS["max_fortify_bonus"] = 0.12` |
| Instant fortify | +5% | First fortify turn | `DAVOUT_MODIFIERS["instant_fortify_bonus"] = 0.05` |
| Scout range | +1 region | Extended recon | `DAVOUT_MODIFIERS["scout_range_bonus"] = 1` |

**Special Ability: Counter-Punch**
- **Trigger:** After successfully defending against an attack
- **Effect:** `counter_punch_available = True`, grants one FREE attack
- **Duration:** Must be used within 1 turn or expires
- **Implementation:** Set in `combat.py`, checked in `executor.py`

**Behavioral Traits:**
- Objects to risky attacks (outnumbered, bad odds)
- Trust bonus for defensive actions
- Penalty for attacking at bad odds

#### GROUCHY (Literal)

| Modifier | Value | Condition | Code Reference |
|----------|-------|-----------|----------------|
| Hold position defense | +15% | `holding_position == True` | `GROUCHY_MODIFIERS["hold_position_defense_bonus"] = 0.15` |

**Special Ability: Immovable**
- **Trigger:** Player issues `hold` command
- **Effect:** Sets `holding_position = True`, `hold_region = current_location`
- **Bonus:** +15% defense while holding
- **Breaks when:** Marshal moves or attacks
- **Implementation:** `marshal.py` fields, `executor.py` hold handler

**Behavioral Traits:**
- Never improvises or takes initiative
- Follows orders exactly (the "Grouchy Moment")
- May require clarification for vague orders
- Strategic commands cost 1 action (not 2)
- +15% effectiveness for explicit, unambiguous orders

#### BALANCED / LOYAL — RETIRED BY CONTRACT (MC-4, July 10, 2026)

These two types are **not implemented and cannot boot**: the MC-4 gate
retired them behind a three-arm guard (`personality.IMPLEMENTED_PERSONALITIES`
is the single source; the scenario validator hard-fails `balanced`/`loyal`;
`create_marshal_from_data` raises). The re-open owners are the Jealousy-gate /
MC-exit-review lineage, and a revived type must never be named "loyal" (the
diplomat `loyalist` collision). See `MARSHAL_CONTENT_PASS_SPEC.md` §9.
Historical design notes for the retired types live in the git history of this
file — they are deliberately not reproduced here so no scenario author reads
them as authorable (Aug 2026 health-check audit).

### Fortify Mechanics

- Stored as decimal: `0.12` = 12%
- Display: `int(value * 100)` = "12%"
- Rate: +2%/turn standard, +3%/turn for cautious (Davout)
- Max: **12% standard, 8% for aggressive (Ney), 12% for cautious (Davout)** *(B1 balance: reduced from 15/10/20)*
- Instant fortify: +5% on first turn for cautious (Davout)
- **IMPORTANT:** Cautious personality defensive stance bonus (+5%) is a SEPARATE permanent stat from fortification. It is NOT affected by bombardment stripping. Fortification is strippable. Personality stance is not.

### Fortification Degradation (Session 31)

When a fortified defender is attacked, their `defense_bonus` degrades by 5% (0.05) per battle. This represents siege damage wearing down prepared positions.

- Applied in `combat.py` AFTER all combat resolution (damage, retreats, recklessness tracking)
- Only triggers if `defender.defense_bonus > 0`
- Capped at 0 (can't go negative)
- If defense_bonus reaches 0: fortification is destroyed
- Result dict includes: `fortification_degraded`, `fortification_old`, `fortification_new`

**Berthier Observations (Priority 6c):**
- `fort_degraded_attacker/defender`: "The enemy earthworks crumble under our bombardment"
- `fort_destroyed_attacker/defender`: "Their fortifications are reduced to rubble"
- Priority 6c fires between P6 (won/fort held) and P7 (won drilled)

**Key code:** `combat.py::resolve_combat()` (degradation), `battle_report.py::_pick_observation()` (P6c), `battle_report.py::_OBSERVATIONS` (templates)

### Bombardment Fortification Stripping (B1 Balance)

Artillery bombardment strips 5% (0.05) of the defender's raw `defense_bonus` (fortification level) per hit. This is IN ADDITION to the existing degradation from regular combat above.

- Applied in `combat_executor.py::_execute_bombardment()` AFTER bombardment damage resolution
- Only triggers if `defender.defense_bonus > 0`
- Strips 0.05 per bombardment hit (not per unit of damage)
- Fortification level cannot go below 0
- Result dict includes: `fortification_stripped`, `fortification_old`, `fortification_new`

**What bombardment strips vs. what it does NOT:**
- **Strips:** Marshal's `defense_bonus` (accumulated fortification from `fortify` action)
- **Does NOT strip:** Cautious personality defensive stance bonus (+5%) — this is a permanent personality stat, not fortification
- **Does NOT strip:** Terrain defense bonuses, ability bonuses (e.g., Wellington's Reverse Slope +5%)

**Tactical implication:** Drouot (artillery) becomes the designated counter to Wellington's defensive stacking. Bombard 2-3 times to strip all fortification (12% cap / 5% per hit = 3 bombardments), then assault with infantry. This costs 3-4 AP (full turn commitment) but breaks the defensive deadlock.

**Key code:** `combat_executor.py::_execute_bombardment()` (stripping), `marshal.py::defense_bonus` (fortification field)

### Drill/Shock Bonus

- 2-turn drill process: `drilling` (turn 1) -> `drilling_locked` (turn 2) -> `shock_bonus` set
- Shock bonus: +20% attack modifier when consumed (shock_bonus=2, * 0.10 = +20%)
- Consumed after first attack (cleared AFTER `get_attack_modifier()` reads it)
- Drilling penalty: -25% defense while drilling or drilling_locked

### Example Calculations

**Ney (aggressive cavalry) in aggressive stance with drill bonus:**
```
Base: 1.0
x 1.15 (aggressive stance)
x 1.20 (drill shock_bonus=2)
x 1.15 (aggressive personality base)
x 1.05 (aggressive stance personality bonus)
x 1.05 (drill synergy personality bonus)
= ~1.81x attack modifier (+81%)
```

**Davout (cautious infantry) in defensive stance, outnumbered, fortified 12% (B1 cap):**
```
Base: 1.0
x 1.15 (defensive stance)
x 1.12 (fortify bonus — B1 cap, was 1.16)
x 1.05 (defensive stance personality bonus)
x 1.10 (outnumbered personality bonus)
= ~1.49x defense modifier (+49%)
```

### Source File Reference (Combat)

| Mechanic | Primary File | Secondary Files |
|----------|--------------|-----------------|
| Personality modifiers | `personality_modifiers.py` | `marshal.py` (applies them) |
| Objection triggers | `personality.py` | `disobedience.py` |
| Counter-Punch | `combat.py` (sets flag) | `executor.py` (uses it) |
| Immovable | `marshal.py` | `executor.py` (hold command) |
| Recklessness | `marshal.py` | `executor.py`, `world_state.py` |
| Cavalry limits | `world_state.py` | `marshal.py` (counters) |
| Combat calculation | `combat.py` | `marshal.py` (modifiers) |

### Battle Report (Berthier's After-Action Report)

After every player-visible combat, `battle_report.py` generates a structured report attached to the battle result.

**Architecture:**
- **Snapshots** taken BEFORE `get_attack_modifier()`/`get_defense_modifier()` (which consume one-shot bonuses like strategic_combat_bonus)
- `snapshot_attacker_modifiers()` — reads stance, drill/shock, strategic bonus (peek only, NOT zeroed), personality, recklessness, exhaustion, cavalry terrain, flanking, glorious charge, counter-punch mastery. Coordination entries (combined arms, per-ally, dedicated, adjacent, total) intentionally omitted (Gate 4) — Berthier's narrative observation handles coordination; detailed numbers deferred to Battle History screen (Phase 8.5).
- `snapshot_defender_modifiers()` — reads stance, fortify bonus, strategic defense (peek only), drilling penalty, personality, recklessness, terrain defense, fortification building. Coordination entries intentionally omitted (Gate 4).
- `generate_battle_report(battle_result, player_nation)` — assembles modifier_breakdown, casualty_summary, observation

**Perspective-aware observations:** Berthier always speaks from Napoleon's side. `_pick_observation()` uses `attacker_nation`/`defender_nation` from the battle result to determine which side is French. When the enemy attacks a French marshal, "we won" means the defender (our marshal) won. Templates use `{marshal}`, `{enemy}`, `{ally}`, `{relationship}`, `{coordination_bonus}`, and `{arrival_score}` placeholders filled via `.replace()` (graceful degradation — unfilled placeholders become empty strings). The `player_nation` param (default "France") is passed from `combat.py`.

**Observation priorities** (first match wins, `random.choice()` from 2-3 templates):

| Priority | Condition (from French perspective) |
|----------|-----------|
| 0.5 | Full combined arms triangle (3 unit types co-located) — Session 65 |
| 0.7 | Reinforcement arrived (ally marched onto field) — Session 65 |
| 0.8 | Reinforcement failed (ally didn't arrive in time) — Session 65 |
| 1 | Mutual destruction (both sides lost >50%) |
| 2 | We lost + enemy had fortification |
| 3 | We lost + bad stance matchup (aggressive into defensive) |
| 4 | We lost + enemy had terrain advantage >= 15% |
| 5 | We won + heavy casualties (>40% of our original strength) |
| 5.5 | Hostile marshal fought alongside under SUPPORT order — Session 65 |
| 6 | We won + broke through enemy fortification |
| 7 | We won + our troops were drilled |
| 8 | We lost + no drill + narrow margin (<15% of our strength) |
| 9 | We won decisively (2:1+ casualty ratio in our favor) |
| 10 | Stalemate |
| 11 | Default combat observation |
| 12 | Hostile marshal stood idle (refused coordination) — Session 65 |
| 13 | Devoted synergy (devoted ally amplified coordination) — Session 65 |
| 15 | Rival relationship improved after shared battle — Session 65 |

**Two-pass observation picking (Session 65):** Initial observation picked inside `resolve_battle()` (combat.py), which has no coordination/reinforcement/relationship data. After `executor.py` injects `coordination_context`, `reinforcement_results_for_report`, and `relationship_changes` into the battle result dict, the observation is re-picked if any coordination data is present. This avoids modifying `combat.py`.

**Data flow:**
```
combat.py (snapshots + generate_battle_report)
  → resolve_battle() return dict includes "battle_report" (initial observation)
  → executor.py injects coordination_context, reinforcement_results_for_report,
    relationship_changes → re-picks observation with full data
  → executor.py (5 passthrough sites: attack, 3 sally, charge)
  → world_state.py (1 passthrough: auto-charge event)
  → main.py (1 passthrough block)
  → Godot main.gd (_display_berthier_report)
```

**Godot display:** BBCode formatted with dark goldenrod header, light gray report lines, goldenrod observation quote. Comma-formatted numbers via `_format_number()`.

**Key code:** `battle_report.py` (snapshots + report), `combat.py:~189` (snapshot insertion point), `combat.py:~561` (return dict), `main.gd::_display_berthier_report()`

### Casualty Distribution (Session 62)

When 2+ same-nation marshals are in the battle region, casualties are distributed proportionally among participants instead of being applied entirely to the primary combatant.

**`resolve_battle(apply_casualties=False)` contract (C1/C2):**
- Computes all combat math (modifiers, dice, casualties) normally
- Returns raw casualties, morale deltas (int), and projected-strength outcome
- Does NOT modify marshal state (except fortification degradation — battle-triggered)
- Caller distributes casualties and applies effects per-participant

**Distribution formula:**
- Each participant's share = `int(raw_casualties * (participant.strength / total_strength))`
- **Artillery rear-position advantage:** When fighting alongside non-artillery units, artillery takes 50% of proportional share (`ARTILLERY_CASUALTY_FACTOR = 0.5`). No reduction when fighting alone or with only other artillery.
- **Cavalry receives NO casualty reduction** in combined arms. Cavalry charges and takes full proportional casualties — their combined arms benefit comes from combat bonuses (+10%/+20% attack, +5%/+10% defense), not reduced losses. This makes cavalry feel powerful but vulnerable: the decisive arm that wins battles at a cost. Infantry absorbs the bulk of casualties as the frontline unit type.
- Remainder (from rounding) assigned to strongest non-artillery marshal (falls back to strongest overall if all artillery)
- Capped at each marshal's current strength

**Participant eligibility:**
- Same-nation, in battle region, alive, not broken/retreating/recovering
- Hostile relationship (-2) WITHOUT SUPPORT order → Non-Participating (0% casualties)
- Hostile relationship (-2) WITH active SUPPORT order → Participating (D3: takes casualties, 0% coordination)

**Per-participant effects:**
- Casualties: proportional by strength
- Morale: UNIFORM delta (same for all on that side — psychological, not physical)
- battles_won/lost: all participants increment

**Primary-only effects:**
- Recklessness increment/reset: primary attacker only
- Counter-punch (cautious): primary defender only
- Counter-Punch Mastery (Davout): primary defender only
- Pursuit damage: primary attacker ability vs primary defender

**Solo battles (1v1):** `apply_casualties=True` (default) — zero behavior change.

### Battle Morale Deltas (W6-11 E-CA-1 — symmetric since July 10, 2026)

Casualty-scaled morale loss applies to **both sides in every outcome** — a
winner's delta = outcome bonus − the same `_scaled_morale_loss(rate, base)`
curve the loser pays in that arm (before W6-11 a winning/holding defender
took zero casualty loss — live audit: Mack at morale 95 through 15k+
losses). Both copies (normal path + `_build_deferred_result`) share the
table; `DEFENDER_MORALE_CURVE_FACTOR = 1.0` (blessed; band floor 0.75)
dampens only the defender's curve if playtests over-shift.

| Outcome | Attacker delta | Defender delta |
|---|---|---|
| mutual_destruction | −scaled(rate, 20) | −scaled(rate, 20) |
| defender_victory | −scaled(rate, 20) | **+10 − scaled(rate, 20)** |
| attacker_victory | **+10 − scaled(rate, 20)** | −scaled(rate, 20) |
| defender_tactical_victory (holds the line) | −scaled(rate, 10) | **+5 − scaled(rate, 10)** |
| attacker_tactical_victory | **+5 − scaled(rate, 10)** | −scaled(rate, 10) |
| stalemate | −scaled(rate, 5) | −scaled(rate, 5) |

`_scaled_morale_loss` is unchanged: `max(base, int(base × min(rate/0.15, 2.5)))`.
Counter-punch grants and the forced-retreat threshold (25) are untouched.
Pinned by `tests/test_w6_balance_duo.py` (incl. the audit battle-2 replay:
the 50k holder's delta moves +5 → −5).

### Battle Records (ESP-EV-3 — unified since July 11, 2026)

**Tactical victories COUNT toward `battles_won`/`battles_lost` on every
path.** The coordination caller always counted them (atk_won/def_won
include `*_tactical_victory`); the solo path in `combat.py` now keeps the
same books — a marshal's record, and his ES-7 reward expectation, no
longer depend on whether allies happened to march. Stalemate: no records
move. Mutual destruction: both sides log a loss. Consequence for tuning:
expectation accrues faster in grinding wars (the eval's Mack-grind now
feeds the Cost-of-Success) — `REP_STEP`/`EXPECTATION_CAP` remain in-band
tunable, and E5's "caps ~turn 15–20" guidance should be re-measured at the
next band check. Pinned by
`test_estate_second_pass.py::TestUnifiedWinSemantics`.

**Key code:** `combat.py::_build_deferred_result()`, `executor.py::_distribute_casualties()`, `executor.py::_get_casualty_participants()`, `executor.py::_execute_attack()` coordination branch.

---

## 2. Disobedience & Trust

### System Overview

The disobedience system creates dynamic tension between player orders and marshal personalities. Marshals don't just blindly follow orders -- they evaluate them based on their personality, trust in the player, and situational context.

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| DisobedienceSystem | `disobedience.py` | Main orchestrator, objection creation/handling |
| Severity Calculator | `severity.py` | Calculates objection severity (0.0-0.95) |
| Personality System | `personality.py` | Defines personality triggers and base severities |
| Trust System | `trust.py` | Manages trust values and obedience probability |
| Authority Tracker | `authority.py` | Tracks player authority to prevent sycophancy |
| Vindication Tracker | `vindication.py` | Tracks who was proven right/wrong |

### Order Processing Flow

```
1. Player issues command
   |
2. CommandExecutor calls DisobedienceSystem.evaluate_order()
   |
3. analyze_order_situation() determines situation type
   |
4. get_base_severity() gets personality-specific base severity
   |
5. Apply multiplicative modifiers:
   - Trust modifier (0.7 to 1.6x)
   - Vindication modifier (0.85 to 1.15x)
   - Performance modifier (0.85 to 1.15x)
   - Override modifier (1.0 to 1.3x)
   - Authority modifier (1.0 to 1.25x)
   |
6. Apply random variance (tiered by severity level)
   |
7. Cap at 0.95
   |
8. Determine objection type:
   - < 0.20: No objection -> execute order normally
   - 0.20-0.49: Mild objection -> auto-resolve with grumbling
   - 0.50-0.95: Major objection -> present player with choices
```

### Severity Thresholds

| Severity | Type | Result |
|----------|------|--------|
| 0.00 - 0.19 | None | Marshal obeys without comment |
| 0.20 - 0.49 | Mild | Marshal grumbles but obeys |
| 0.50 - 0.95 | Major | Player must choose: Trust, Insist, or Compromise |

### Modifier Application

All modifiers are **multiplicative**, applied in this order:

1. **Trust Modifier** - Based on marshal's trust in player
2. **Vindication Modifier** - Based on track record of being right
3. **Performance Modifier** - Based on recent battle outcomes
4. **Override Modifier** - Based on how often this marshal is overridden
5. **Authority Modifier** - Based on player's overall authority

### Variance System

Random variance is applied based on severity level:

| Severity Range | Variance | Purpose |
|----------------|----------|---------|
| 0.00 - 0.19 | None | Below threshold, no variance needed |
| 0.20 - 0.34 | +/-3% | Predictable for mild objections |
| 0.35 - 0.59 | +/-8% | Moderate variance |
| 0.60+ | +/-12% | High unpredictability for major decisions |

### Personality Triggers

#### AGGRESSIVE (Ney, Blucher, Murat)

| Trigger | Severity | Type | Description |
|---------|----------|------|-------------|
| `defend` | 0.60 | Major | Ordered to defend |
| `wait` | 0.50 | Major | Ordered to wait/hold |
| `wait_with_enemy_nearby` | 0.65 | Major | Wait when enemy adjacent |
| `retreat` | 0.70 | Major | Ordered to retreat |
| `hold_position` | 0.60 | Major | Hold position (alias for defend) |
| `fortify` | 0.55 | Major | Dig trenches |
| `drill_enemy_nearby` | 0.45 | Mild | Drill when enemy is close |
| `defensive_stance` | 0.55 | Major | Adopt defensive stance |
| `neutral_stance_from_aggressive` | 0.35 | Mild | Stand down from aggressive |

#### CAUTIOUS (Davout, Wellington)

| Trigger | Severity | Type | Description |
|---------|----------|------|-------------|
| `certain_death` | 0.80 | Major | Attack at 5:1+ odds |
| `attack_outnumbered_3to1` | 0.70 | Major | Attack at 3:1 odds |
| `attack_outnumbered_2to1` | 0.60 | Major | Attack at 2:1 odds |
| `attack_outnumbered_1_5to1` | 0.50 | Major | Attack at 1.5:1 odds |
| `attack_without_intel` | 0.55 | Major | Attack unknown enemy (TODO) |
| `attack_fortified` | 0.60 | Major | Attack fortified position |
| `forced_march` | 0.45 | Mild | Forced march order |
| `aggressive_stance` | 0.40 | Mild | Adopt aggressive stance |
| `aggressive_stance_outnumbered` | 0.60 | Major | Aggressive stance when outnumbered |

#### LITERAL — never objects (W6-5 Literal Doctrine)

The literal marshal **does not object by design** — "generals who do what
they're ordered" is the fantasy (Wave 6 gate, July 10, 2026; supersedes the
old R59/R153 literal-objection trigger table that stood here). His texture
is elsewhere: the verbatim-quote doctrine, the CR-5 ASK arm, Immovable holds,
and the Jealousy Vindicated Garrison. Soult is LITERAL (reassigned at the
CR-5 gate — canonized as character at MC-4), not "balanced".

*(The BALANCED/LOYAL trigger tables that stood here described types retired
by MC-4 — removed in the Aug 2026 health-check audit so no builder
resurrects them from this page; see the retirement note above.)*

### Quick Reference: Who Objects to What

| Order | Ney (Aggressive) | Davout (Cautious) | Grouchy (Literal) |
|-------|------------------|-------------------|-------------------|
| Attack | Happy | Objects if outnumbered | Obeys |
| Defend | **Objects** (0.60) | Happy | Obeys |
| Hold | Mild objection (0.45) | Happy | Obeys |
| Wait | **Objects** (0.50-0.65) | Happy | Obeys |
| Fortify | **Objects** (0.55) | Happy | Obeys |
| Drill | Mild if enemy nearby (0.45) | Happy | Obeys |
| Retreat | **Strongly objects** (0.70) | Happy if losing | Obeys |
| Aggressive Stance | Happy | Objects (mild/major) | Obeys |
| Defensive Stance | **Objects** (0.55) | Happy | Obeys |
| Move | Usually fine | Usually fine | Obeys |

### The Literal Doctrine (W6-5, July 10 2026 — user gate; supersedes R59/R153)

> A literal marshal executes the letter of the order: no improvisation, no
> initiative, no objection. He is cheaper to command (strategic orders cost
> 1 AP, not 2), immovable on the defense (+15% literal hold — "Immovable
> (literal hold)" in the battle report), and utterly predictable. What he
> will never do is march to the sound of the guns without your written word
> ("Soult, support Ney" authorizes him — the Grouchy Rule).

Literal marshals **never object, BY DESIGN** (`PERSONALITY_TRIGGERS[LITERAL]`
is deliberately empty; the disobedience layer bypasses literal entirely —
pinned by `test_w6_literal_doctrine.py`). Their engagement surfaces instead:
**order echo** (acknowledgment + completion quote the verbatim
`original_command` — voice bank `backend/game_logic/marshal_voice.py`,
deterministic rotation, no RNG); the **fidelity beat** (`literal_fidelity`
campaign-log/dispatch event when an adjacent own-nation battle didn't move
him, his PURSUE/SUPPORT quarry shifted, or his MOVE_TO destination changed
hands — pure narration, no interrupt, no trust change, cap 1/marshal/turn);
**precision captions** (the 1-AP discount named at order creation); the
dispatch status note "(to the letter)"; and the W6-4 muster row that names
who won't march and how to authorize him.

### Trust Change Values

| Choice | Trust Change | Authority Change |
|--------|--------------|------------------|
| **Trust** | +12 | -3 |
| **Insist (obeys)** | -10 | +2 |
| **Insist (disobeys)** | -15 | +0 |
| **Compromise** | +3 | -1 |

### Trust -> Severity Multiplier (4-Tier Steep Curve)

| Trust Level | Range | Multiplier | Effect |
|-------------|-------|------------|--------|
| Very High | 80+ | 0.7x | Much less likely to object |
| Neutral | 40-79 | 1.0x | Baseline |
| Low | 20-39 | 1.3x | More likely to object |
| Very Low | <20 | 1.6x | Much more likely to object |

### Trust -> Obedience Chance (when player insists)

| Trust Level | Range | Obedience Chance | Description |
|-------------|-------|------------------|-------------|
| Loyal | 80+ | 100% | Guaranteed obedience |
| Reliable | 60-79 | 90-99.5% | Very likely to obey |
| Questioning | 40-59 | 70-89.5% | May question orders |
| Strained | 20-39 | 50-69.5% | Significant disobey risk |
| Broken | <20 | 30-49.5% | Very likely to refuse |

### Vindication System

#### Vindication Score Effects (3-Tier System)

| Score | Range | Multiplier | Meaning |
|-------|-------|------------|---------|
| Proven Wrong | <=-2 | 0.85x | Marshal was wrong, less bold |
| Neutral | -1 to +2 | 1.0x | No strong track record |
| Proven Right | >=+3 | 1.15x | Marshal was right, bolder |

#### Score Changes

| Choice | Battle Outcome | Vindication Change |
|--------|----------------|-------------------|
| Trust | Victory | +1 (marshal was right) |
| Trust | Defeat | -1 (marshal was wrong) |
| Insist | Victory | -1 (marshal was wrong to object) |
| Insist | Defeat | +1 (marshal was right) |
| Compromise | Any | 0 (shared responsibility) |

### Authority System

#### Authority Thresholds

| Authority | Level | Severity Modifier | Trust Gain Modifier |
|-----------|-------|-------------------|---------------------|
| 80+ | High | 1.0x | 1.0x |
| 50-79 | Moderate | 1.1x | 0.8x |
| <50 | Low | 1.25x | 0.5x |

#### Authority Changes

| Pattern | Effect | Reason |
|---------|--------|--------|
| Always Trust | -5 per response | Sycophancy detected |
| Mostly Trust (60-80%) | -2 per response | Leaning too soft |
| Balanced (30-60%) | +1 per response | Good leadership |
| Mostly Insist | +1 (maintain) | Firm leadership |

#### Excessive Trust Penalty (V2b)

`check_excessive_trust()` runs on every `record_response()`. Uses a 10-turn sliding window:
- **>80% trust** in window (min 3 responses): -3 authority
- **>65% trust** in window (min 3 responses): -2 authority
- Replaces the old trust-ratio branch in `_evaluate_authority()`

#### Authority Major Victory/Defeat (V2b)

Fires ONCE per battle (multiple criteria don't stack):
- **+5 authority**: Outnumbered win (attacker ≤ defender strength) or capital capture
- **-5 authority**: Outnumbering loss (attacker > defender strength) or capital loss

#### Threshold Events

- **Authority 70**: "Some marshals grow bold, sensing leniency."
- **Authority 50**: "The command structure wavers. Marshals question openly."
- **Authority 30**: "Your authority has collapsed. Expect frequent defiance."

### Defiance System (V2b)

Post-insist event: after player sees MODERATE/STRONG/EXTREME objection and insists, the marshal may defy the order.

#### Defiance Chance Formula

`base + vindication_mod + authority_mod + trust_mod + variance` (hard cap 0.40)

| Component | Value |
|-----------|-------|
| Base (MODERATE) | 5% |
| Base (STRONG) | 15% |
| Base (EXTREME) | 35% |
| Vindication | +10% per vindication stack |
| Authority ≥80 | -10% (strong leader suppresses) |
| Authority <50 | +10% (weak leader emboldens) |
| Trust ≤20 | +15% (broken trust) |
| Trust ≥80 | -10% (loyal) |
| Variance | ±8% random |
| **Hard cap** | **40%** |

Special: Literal personality (Grouchy) NEVER defies. Broken/retreating marshals cannot defy. Cooldown prevents re-defiance (3 turns after defiance, 1 turn after failed roll). AP cost follows the defiant action taken (not the original order).

#### Defiance Fallback Table

| Personality | Defiant Action | When Ordered To |
|-------------|---------------|-----------------|
| Aggressive | Attack (bombardment if artillery) | defend, fortify, hold, wait, retreat, SUPPORT, MOVE_TO |
| Cautious | Fortify | attack, SUPPORT, MOVE_TO |
| Literal | Never defies | — |

#### Defiance Outcome Table

| Outcome | Trust | Vindication | Authority | Cooldown |
|---------|-------|-------------|-----------|----------|
| Marshal **RIGHT** (`True`) | +2 | +1 | -5 | 3 turns |
| Marshal **WRONG** (`False`) | -5 | Reset to 0 | +3 | 3 turns |
| **INCONCLUSIVE** sulk (`None`) | 0 | No change | No change | 3 turns |
| Roll **fails**, obeys | -3 | Reset to 0 | No change | 1 turn |

#### Defiance Success Criteria

- **Attack/bombardment**: Won AND casualties < 50% (not pyrrhic)
- **Defend/fortify**: Not broken AND not retreating
- **Retreat**: Marshal survived (strength > 0)
- **Wait/sulk**: Always inconclusive

### Vindication Escalation (V2b)

Inserted between base objection trigger and mood variance:
- `vindication_score > 0` → escalate concern +1 level (e.g. MILD→MODERATE)
- `vindication_score < 0` → de-escalate concern -1 level
- NONE never promotes (prevents fake objections from vindication alone)
- MILD is the floor (never drops to NONE from de-escalation)

#### Vindication Decay

`_process_vindication_decay()` runs each turn in `advance_turn()`:
- -1 per 3 idle turns (no objection), symmetric toward 0
- Timer resets after each decay tick
- Stale defensive vindication entries (>5 turns old, no enemy attack) are cleared

#### Defensive Vindication

Created when player chooses "trust" and marshal's alternative was defend/fortify/hold:
- Stored in `vindication_tracker.pending_defensive_vindication`
- Resolved after enemy phase: held position = +1, broken/retreating = -1
- Stale entries (>5 turns, no attack) are cleared during vindication decay

### Relationship-Based SUPPORT Objection (V2b)

When issuing SUPPORT orders, relationship with the target marshal is checked:
| Personality | Hostile (-2) | Rival (-1) | Neutral+ |
|-------------|-------------|------------|----------|
| Aggressive | STRONG | MILD | NONE |
| Cautious | MODERATE | MILD | NONE |
| Literal | NONE | NONE | NONE |
| Other | MILD | NONE | NONE |

Takes priority if higher than personality-based concern. Includes timed SUPPORT compromise option (`condition.max_turns = 3`).

### V2b Frontend Display (Session 3)

| Data | Display Location | File |
|------|-----------------|------|
| Defiance result (action, outcome, Berthier text, stat changes) | Bordered "DEFIANCE" block in terminal | `main.gd` `_display_defiance_result()` |
| Authority threshold event | Bordered "AUTHORITY" block in terminal | `main.gd` `_display_authority_event()` |
| Authority value + label | Strategic ledger Forces tab header | `ledger.py` + `strategic_ledger.gd` |
| Authority value + label | Morning dispatch SITUATION section | `dispatch.py` + `dispatch_view.gd` + `main.gd` |
| Vindication score | Marshal management cards | `marshal_overview.py` + `marshal_management.gd` (already wired Sessions 1-2) |

### Compromise Rules

#### Basic Action Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Attack | Defend | **Move** (approach but don't engage) |
| Defend | Attack | **Move** (advance cautiously) |
| Attack | Move | **Move** |
| Move | Attack | **Defend** (hold ground) |
| Move | Defend | **Defend** |
| Defend | Move | **Move** |

#### Tactical Action Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Fortify | Attack | **Defend** (hold but stay mobile) |
| Fortify | Move | **Defend** |
| Fortify | Drill | **Drill** (active preparation) |
| Attack | Fortify | **Defend** |
| Drill | Attack | **Defend** |
| Drill | Move | **Defend** |
| Drill | Defend | **Defend** |
| Attack | Drill | **Defend** |

#### Retreat Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Retreat | Defend | **Defend** (hold, don't flee) |
| Retreat | Attack | **Defend** (neither attack nor flee) |
| Defend | Retreat | **Fortify** (dig in) |
| Attack | Retreat | **Defend** |

#### Stance Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Defensive Stance | Aggressive Stance | **Neutral Stance** |
| Aggressive Stance | Defensive Stance | **Neutral Stance** |

### Alternative Generation by Personality

All candidates validated via `_can_execute_suggestion()` (Master Rule #1). If entire chain exhausts, returns None → executor demotes to MILD (Master Rule #2).

#### AGGRESSIVE
When ordered to defend/fortify/hold/wait/form_square/drill/retreat/stance_change — unified fallback chain:
1. **Attack** nearest enemy (if target exists)
2. **Move** toward enemy (if valid path)
3. **Drill** (if not the ordered action and can_drill passes)
4. **Aggressive Stance** (if can change)
5. → None (demote to MILD)

#### CAUTIOUS (Context-Aware)
When ordered to attack:
- 3:1+ outnumbered: **Retreat** → **Fortify** → **Defend**
- 2:1 outnumbered: **Fortify** → **Defensive Stance** → **Defend**
- 1.5:1 or default: **Defensive Stance** → **Fortify** → **Defend**

When ordered to move (through enemy): **Fortify** → **Defensive Stance** → **Defend**

When ordered to defend/fortify (artillery streak): **Attack** → **Move** → **Defensive Stance** → None

#### BALANCED/LITERAL/LOYAL
- Attack ordered: **Defend**
- Defend ordered (with enemy nearby): **Attack** → **Move**
- Otherwise: Follow default fallback

### Compromise Generation by Personality

Compromises must differ from BOTH original order AND preferred alternative. Validated via `_can_execute_suggestion()`.

#### AGGRESSIVE
Chain: **Aggressive Stance** → **Drill** (skip if ordered) → **Move toward enemy** → **Defend**

#### CAUTIOUS
Chain: **Defensive Stance** → **Fortify** → **Defend**

#### Other / COMPROMISE_RULES table
Falls through to static table. If no distinct compromise found → None (demote to MILD).

### Master Rule #2: Exhaust→MILD Demotion

After `_generate_alternative` and `_find_compromise` run, executor validates:
- If preferred is None → demote
- If preferred == original → demote
- If preferred == compromise → demote
Demoted concerns become MILD (flavor text, no popup). This catches mood-variance-promoted MILDs that can't produce real popups.

### Strategic Command Objections (Phase M)

Strategic commands (HOLD, MOVE_TO, PURSUE, SUPPORT) have their own objection system, separate from tactical objections. These fire at command **issuance**, not during execution.

#### Strategic Objection Triggers

| Personality | Strategic Type | Trigger | Base Severity | Compromise |
|-------------|---------------|---------|---------------|------------|
| Aggressive (Ney) | HOLD | No enemies adjacent to hold position | 0.72 | Timed HOLD (3 turns) |
| Cautious (Davout) | PURSUE | Target ratio < 1.2 (bad odds) | 0.68 | Auto-cancel below ratio |
| Cautious (Davout) | MOVE_TO | Path crosses enemy-occupied region | 0.65 | Safe route if available |
| Cautious (Davout) | HOLD (distant) | Path crosses enemy-occupied region | 0.65 | Safe route if available |
| Cautious (Davout) | SUPPORT | Path crosses enemy-occupied region | 0.65 | Safe route if available |
| Literal (Grouchy) | Any | **Never objects** | N/A | Uses clarification popup for vague orders |

#### Strategic vs Tactical Objections

| Aspect | Tactical | Strategic |
|--------|----------|-----------|
| When | Action execution | Command issuance |
| Storage | `world.pending_objection` | `world.pending_strategic_objection` |
| Trigger | Personality vs action type | Personality vs situation |
| Recovery bypass | No objections during retreat_recovery | No objections during retreat_recovery |

#### Dangerous Path Objection (Cautious Only)

Cautious marshals (like Davout) object to any strategic command that requires marching through enemy-occupied territory:

1. **MOVE_TO through danger** - "That path passes through [enemy region]. We would be walking into danger, Sire."
2. **HOLD (distant) through danger** - "To hold [target], we must march through [enemy region]. A dangerous gambit, Sire."
3. **SUPPORT through danger** - "To reach [ally], we must pass through [enemy region]. That path invites disaster, Sire."

If a safe path exists (no longer than 2x the direct path), compromise offers "Accept: Safe route" option.

### Disobedience Triggers by Action

| Action | Aggressive | Cautious | Literal |
|--------|------------|----------|---------|
| `defend` | 0.60 (Major) | No trigger | No trigger |
| `hold` | 0.45 (Mild) | No trigger | No trigger |
| `wait` | 0.50 (Major) | No trigger | No trigger |
| `wait` (enemy nearby) | 0.65 (Major) | No trigger | No trigger |

### Configuration Constants

| Constant | Value | Location |
|----------|-------|----------|
| MAX_MAJOR_OBJECTIONS_PER_TURN | 2 | `disobedience.py:25` |
| SEVERITY_CAP | 0.95 | `severity.py:94` |
| NO_OBJECTION_THRESHOLD | 0.20 | `disobedience.py:403` |
| MILD_OBJECTION_THRESHOLD | 0.50 | `disobedience.py:407` |
| VINDICATION_MIN/MAX | -5/+5 | `vindication.py` |
| TRUST_MIN/MAX | 0/100 | `trust.py` |
| AUTHORITY_MIN/MAX | 0/100 | `authority.py` |

### Post-Objection Action Routing (`_execute_post_objection`)

Single choke point for all post-objection execution (trust/insist/compromise). Defiance bypasses this entirely.

| Action | Handler | AP Pool | Signature | Notes |
|--------|---------|---------|-----------|-------|
| attack | `_execute_attack(marshal, target, world, game_state)` | Military | Marshal obj + target name | |
| defend | `_execute_defend(marshal, world, game_state)` | Military | Marshal obj | |
| move | `_execute_move(marshal, target, world, game_state)` | Military | Marshal obj + target name | |
| scout | `_execute_scout(marshal, target, world, game_state)` | Military | Marshal obj + target name | |
| recruit | `_execute_recruit(command, game_state)` | Admin | Command dict | |
| build | `_execute_build(command, game_state)` | Admin | Command dict | |
| repair | `_execute_repair(command, game_state)` | Admin | Command dict | |
| fortify | `_execute_fortify(command, game_state)` | Military | Command dict | |
| drill | `_execute_drill(command, game_state)` | Military | Command dict | |
| unfortify | `_execute_unfortify(command, game_state)` | Military | Command dict | |
| form_square | `_execute_form_square(command, game_state)` | Military | Command dict | |
| break_square | `_execute_break_square(command, game_state)` | Free | Command dict | |
| retreat | `_execute_retreat_action(marshal, world, game_state)` | Free | Marshal obj | |
| stance_change | `_execute_stance_change(command, game_state)` | Military | Command dict | Variable cost (0-2 AP) |
| hold | `_execute_hold(marshal, world, game_state)` | Military | Marshal obj | |
| wait | `_execute_wait(marshal, world, game_state)` | Military | Marshal obj | |
| bombardment | `_execute_bombardment(marshal, target, world, game_state)` | Military | Marshal + nearest enemy | Added Session 7b-audit |
| garrison | `_execute_garrison(command, game_state)` | Military | Command dict | Added Session 7b-audit |
| strategic | `_execute_strategic_command(parsed, command, game_state)` | Military | Via strategic routing | Only if `is_strategic` flag set |

### Known Limitations

**Phase 3 Features (Not Yet Implemented):**
1. **Ambiguous Order Detection** - Requires LLM to detect unclear commands
2. **Contradictory Orders** - Requires order history tracking
3. **Frequent Order Changes** - Requires order history tracking
4. **Fog of War** - `attack_without_intel` cannot trigger
5. **Ally Abandonment** - Requires ally position tracking
6. **Political Intrigue** - `betray_emperor` cannot trigger
7. **Suicidal Order Expansion** - Currently only checks ratios

**Design Decisions:**
1. **Variance can cross thresholds** - A 0.22 severity can become 0.19 with bad variance roll. This is intentional to avoid predictability.
2. **Compromise not always available** - If no compromise rule exists for an action pair, the compromise button is hidden. This is by design.
3. **Authority bonus ineffective at high trust** - High-trust marshals already have 100% obedience, so authority modifier has no effect. This is a known limitation.
4. **LITERAL personality rarely triggers** - Most LITERAL triggers require Phase 3 features.

---

## 3. Marshal State Machine

### States (Multiple Can Be Active Simultaneously)

```
+-------------+     +-------------+     +-------------+     +-------------+
|   STANCE    |     |  TACTICAL   |     |  RECOVERY   |     |   COMBAT    |
|  (1 of 3)   |     |  (flags)    |     |  (blocking) |     |  (temp)     |
+-------------+     +-------------+     +-------------+     +-------------+
| AGGRESSIVE  |     | fortified   |     | retreat_    |     | broken      |
| NEUTRAL     |     | drilling    |     | recovery=N  |     | (morale<25%)|
| DEFENSIVE   |     | drilling_   |     | (blocks     |     |             |
|             |     |   locked    |     |  attack,    |     | Triggers    |
| Affects:    |     | holding_    |     |  fortify,   |     | forced      |
| -attack mod |     |   position  |     |  drill,     |     | retreat     |
| -defense mod|     |             |     |  scout,     |     |             |
|             |     | Affects:    |     |  aggr.stance|     |             |
|             |     | -defense    |     |             |     |             |
|             |     | -attack     |     | Decrements  |     |             |
|             |     | -mobility   |     | each turn   |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
```

### State Interactions
- `retreat_recovery` BLOCKS: fortify, drill, attack, scout, aggressive_stance
- `drilling_locked` BLOCKS: attack, move (until drill completes)
- `fortified` + move = lose fortify bonus
- `broken` -> forced retreat -> `retreat_recovery=3`

### State Tracking Fields (from `marshal.py`)

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `personality` | str | required | Determines objection triggers and modifiers |
| `cavalry` | bool | False | Enables cavalry mechanics |
| `movement_range` | int | 1 | Attack range (1=infantry, 2=cavalry) |
| `stance` | Stance | NEUTRAL | Current stance |
| `drilling` | bool | False | In turn 1 of drill |
| `drilling_locked` | bool | False | In turn 2 of drill |
| `shock_bonus` | int | 0 | Attack bonus from drill (2 = +20%) |
| `fortified` | bool | False | Currently fortified |
| `defense_bonus` | float | 0 | Fortify percentage as decimal |
| `counter_punch_available` | bool | False | Free attack available (cautious) |
| `counter_punch_turns` | int | 0 | Turns remaining to use |
| `holding_position` | bool | False | Immovable active (literal) |
| `hold_region` | str | "" | Where holding |
| `recklessness` | int | 0 | Recklessness level 0-4 |
| `turns_in_defensive_stance` | int | 0 | Cavalry limit counter |
| `turns_fortified` | int | 0 | Cavalry limit counter |

### Retreat and Broken State

When morale drops to 25% in combat, the marshal is "broken":
- Forced retreat triggers automatically (bypasses objection system)
- `retreating = True`, `retreat_recovery` counts stages 0 → 3 (one per turn baseline; stage 3 = recovered, flags clear). Effectiveness penalty by stage: −45% / −30% / −15% (`marshal.get_retreat_stage_penalty`, consumed by `get_combat_effectiveness`)
- If surrounded (no safe retreat): army SHATTERS — `broken = True`, 3–10% survivors flee to safe spawn, `broken_recovery` counts 0 → 4 (recruit-only until recovered)
- Blocked actions during recovery: attack, fortify, drill, scout, aggressive_stance
- Allowed actions during recovery: move, wait, recruit, defend, defensive_stance, neutral_stance
- No objections during recovery -- marshals are demoralized and compliant

### Command Skill: The Rally (MC gate Q3, July 10 2026)

The `command` skill is consumed at exactly one mechanic — how fast and how well a beaten army reconstitutes. Single source `marshal.py` (`get_rally_stages_per_turn`, `get_retreat_stage_penalty`; constants `RALLY_FAST_COMMAND=8`, `RALLY_POOR_COMMAND=3`, `RALLY_POOR_EXTRA_PENALTY=0.10` — in-band tunable). Applied at the single `_process_tactical_states` tick → GR5-symmetric (both sides, all marshals).

| Command | Effect |
|---------|--------|
| ≥ 8 | Recovery advances 2 stages/turn: retreat recovers in 2 turns (not 3), broken in 2 (not 4). Rally note rides the recovery events |
| 4–7 | Baseline (byte-identical to pre-wiring behavior — the shipped 1805 roster is flat-5 until MC-2 lands authored values; the LEGACY fixture/rollback roster's Ney 8 / Davout 9 / Wellington 9 hit the fast tier, deliberately) |
| ≤ 3 | Retreat-recovery penalties run 10pp deeper (−55% / −40% / −25%); recovery TIME unchanged; the tick message shows the deepened number (shown = applied). Broken state has no effectiveness channel — the poor arm is retreat-only by design |

Every player-facing recovery number derives from the marshal helpers (post-landing review swept them all): dispatch ETA (`_derive_marshal_status`), executor retreat/broken action-block messages, voluntary-retreat copy + stage-0 penalty display (`movement_executor.py`), forced-retreat flee + surrounded/shattered messages (`combat_executor.py`), and the map hover tooltip — the backend ships derived `retreat_penalty` / `broken_turns_left` in `tactical_state` and `map_renderer_base.gd` renders those, never a hardcoded table.

Deliberately does NOT touch the W6-11 blessed in-battle morale curve. Tests: `tests/test_mc_q3_command_rally.py`. (The 1805 roster's authored command values have been live since MC-2 — fast tier Davout 9 / ArchdukeCharles 8, poor tier Mack/Massena/Buxhowden/Hohenlohe 3.)

### Administration Skill: The Intendance (MC-2b, MC exit review July 11 2026)

The `administration` skill is consumed at exactly one mechanic — how efficiently the marshal's staff raises troops. Single source `marshal.py` (`get_recruit_cost_modifier`; constants `INTENDANCE_THRIFTY_ADMIN=8`, `INTENDANCE_WASTEFUL_ADMIN=3`, `INTENDANCE_COST_SWING=0.15` — in-band tunable). Applied LAST inside `economy_executor._calculate_recruit_cost`'s **Europe-scoped** nation-pricing block, composing on the capital/settling × war ×3 × over-limit price (N1: the legacy fixture world's economy pins do not move). The AI pays and *pre-budgets* the same price through the same helper (GR5 — both `_pick_admin_action` affordability checks pass the marshal).

| Administration | Effect |
|----------------|--------|
| ≥ 8 | Recruits cost 15% less (×0.85, rounded) — 1805 tier: Davout, ArchdukeCharles, Moore |
| 4–7 | Baseline, byte-identical |
| ≤ 3 | Recruits cost 15% more (×1.15) — 1805 tier: Ney (3), Murat (2), Massena (3) |

Shown = applied: the recruit message appends `(Davout's intendance: -15%)` exactly when the modifier priced the levy, the event carries `intendance_pct` (int), and the marshal card ships `admin_tier`/`admin_note` plus the administration skill row — **on Europe worlds only**; on the legacy rollback world the mechanic is inert and the card keeps the row hidden (GR9: no advertised stat that does nothing; the backend omits the key, `marshal_management.gd` skips absent keys). Code-verified numbers: peace 200 → 170/230; at war 600 → 510/690; the 1805 boot (war ×3 + ~45% over force limit) prices infantry at Rhineland 872 → Davout 741 / Ney 1003. Tests: `tests/test_marshal_content_mc2b_administration.py`.

### Ally Covers Retreat

```
retreated_this_turn: True if marshal retreated THIS turn

When attacked while retreated_this_turn=True:
  1. Check for covering ally (same region, same nation, not retreated)
  2. If ally exists -> ALLY fights instead (swapped defender)
  3. If no ally -> EXPOSED (+30% AI targeting bonus)

Cleared at: START of next player turn (protection lasts enemy phase)
Set by: Forced retreat, manual retreat
```

### Recklessness System (Aggressive + Cavalry)

#### Prerequisites

The Recklessness System only activates when BOTH conditions are met:
- `personality == "aggressive"`
- `cavalry == True`

**Property check:** `marshal.is_reckless_cavalry` (computed property in `marshal.py`)

#### Current Marshals with Recklessness

- **Ney** (France) - aggressive + cavalry

#### Recklessness Levels

| Level | Attack Bonus | Defense Penalty | Stance Restrictions | Special |
|-------|--------------|-----------------|---------------------|---------|
| 0 | - | - | None | Normal combat |
| 1 | +5% | - | None | Can use `charge` command |
| 2 | +10% | -5% | Cannot use DEFENSIVE stance | Warning message |
| 3 | +15% | -10% | Cannot use DEFENSIVE or NEUTRAL | Popup before attack |
| 4+ | +20% | -15% | Cannot use DEFENSIVE or NEUTRAL | Auto-charge at turn start |

#### How Recklessness Changes

**Increases (+1):**
- Win a battle AS ATTACKER
- Capped at level 4

**Resets to 0:**
- Lose any battle (as attacker or defender)
- Execute Glorious Charge

#### Glorious Charge (Level 3+)

When attacking at recklessness 3+, player receives popup:

| Choice | Effect |
|--------|--------|
| "Let him charge!" | 2x casualties both sides, -20 enemy morale, recklessness resets to 0 |
| "Restrain attack" | Normal attack, -5 trust, recklessness follows normal rules |

**Terrain blocking (Phase 6.1.B):** If the target is on charge-blocked terrain (mountains/forest/urban):
1. Executor scans for alternative enemies within cavalry range (2 regions) on allowed terrain
2. Alternatives sorted by `(distance, strength)` — nearest first, weakest as tiebreaker
3. If alternatives found: redirect popup offers best alternative target (`pending_glorious_charge=True, charge_redirected=True`)
4. If no alternatives: falls through to normal attack (no charge bonus), recklessness preserved
5. Recklessness does NOT reset when terrain blocks the charge

#### Auto-Charge (Level 4)

At turn start, before player input:
1. Check for enemies in range (2 regions for cavalry)
2. If enemy found -> Attack weakest enemy automatically (free action)
3. If no enemy -> March toward nearest enemy
4. If movement blocked -> "strains at the reins" message, stays at level 4
5. If target on charge-blocked terrain -> downgrade to normal attack, recklessness preserved (does NOT reset)

#### AI Behavior

AI marshals at recklessness 3+ always charge (no popup decision needed).

#### Code Locations (Recklessness)

| Functionality | File | Key Functions |
|--------------|------|---------------|
| Recklessness state | `marshal.py` | `is_reckless_cavalry`, `_get_recklessness_attack_bonus()` |
| Combat bonuses | `marshal.py` | `get_attack_modifier()`, `get_defense_modifier()` |
| Stance restrictions | `marshal.py` | `can_use_stance()` |
| Glorious Charge | `executor.py` | `_execute_charge()`, `_execute_restrain()` |
| Charge redirect | `executor.py` | Charge terrain blocked section (~line 1617) |
| Cavalry terrain msg | `combat.py`, `executor.py`, `main.py`, `main.gd` | Passthrough chain + Godot display |
| Auto-charge | `world_state.py` | `_process_reckless_cavalry_turn_start()` |

---

## 4. Strategic Commands

### Pipeline Overview

```
Player Input ("Ney, march to Belgium")
    |
    v
1. FAST PARSER          llm_client.py:~442     Keywords -> action="move"
    |
    v
2. STRATEGIC DETECTION  parser.py:316          detect_strategic_command()
    |                   strategic_parser.py:~218 -> returns is_strategic, strategic_type, etc.
    |
    v
3. VALIDATION           validation.py:117      VALID_STRATEGIC_TYPES check
    |
    v
4. EXECUTOR INTERCEPT   executor.py:863        if is_strategic -> _execute_strategic_command()
    |                   executor.py:1984       Creates StrategicOrder
    |                   executor.py:2118       marshal.strategic_order = order
    |                   executor.py:872        _skip_routing = True (bypass tactical)
    |
    v
5. FIRST STEP           executor.py:~2080      Executes first move/action immediately
    |                                          (costs 2 actions, 1 for LITERAL)
    |
    v
6. TURN-END PROCESSING  turn_manager.py:140    StrategicExecutor.process_strategic_orders()
    |                   strategic.py:40        Iterates marshals with active orders
    |                   strategic.py:74        _execute_strategic_turn() per marshal
    |
    v
7. COMMAND HANDLERS     strategic.py:127       _execute_move_to()
                        strategic.py:274       _execute_pursue()
                        strategic.py:398       _execute_hold()
                        strategic.py:573       _execute_support()
```

### Stage 1: Fast Parser (Keyword Detection)

**File:** `backend/ai/llm_client.py`
- **Line 262:** `parse_command()` -- entry point
- **Line 408-442:** Strategic keyword detection in `_parse_with_mock()`
  - "march", "advance", "move to" -> action="move" (MOVE_TO)
  - "pursue", "chase", "hunt" -> action="move" (PURSUE)
  - "reinforce", "support" -> action="move" (SUPPORT)
  - "hold position", "hold the line" -> action="hold" (HOLD)
- **Key:** Fast parser sets `action="move"`. It does NOT set `is_strategic`. That's Stage 2.

### Stage 2: Strategic Detection

**File:** `backend/ai/strategic_parser.py`
- **Line ~218:** `detect_strategic_command(text, marshals, regions, world)` -- main entry
- **Line 189:** `_detect_strategic_type(text)` -- classifies: MOVE_TO, PURSUE, HOLD, SUPPORT
- **Line 264:** `_classify_target(target, regions, marshals, world)` -- target_type: region, marshal, battle, generic
- **Line 348:** `_parse_condition(text)` -- parses: until_marshal_arrives, until_marshal_destroyed, max_turns, until_battle_won

**File:** `backend/commands/parser.py`
- **Line 314-326:** Injection block -- calls `detect_strategic_command()` and injects:
  - `result["is_strategic"] = True`
  - `result["strategic_type"]` = "MOVE_TO" | "PURSUE" | "HOLD" | "SUPPORT"
  - `result["target_snapshot_location"]` (for friendly marshal targets)
  - `result["strategic_condition"]` (StrategicCondition dict)
  - `result["attack_on_arrival"]` (bool)
  - `result["command"]["target_type"]` (str)

### Stage 2a: Compound orders — the tail never eats the head (CR-7-1, September 22, 2026)

**File:** `backend/commands/parser.py` — `_split_sequential_orders` (the `then` /
`and then` / `;` / `and <Marshal>` boundaries) and `_and_clause_is_a_second_order`
(FA-50's bare `and <verb>` arm). A compound order executes its **HEAD** and reports
the tail in `dropped_sequel` + the "One order at a time" warning. The one exemption
is **positive**: a tail beginning with `attack|engage|assault` fuses onto the head
ONLY when the head can **carry an arrival** —

- `strategic_parser.clause_can_carry_an_arrival(head)`: a MOVE_TO or PURSUE keyword
  from `STRATEGIC_KEYWORDS` (the ONE routing table — never a second hand list)
  **with a destination**; `ARRIVAL_CARRYING_TYPES = {MOVE_TO, PURSUE}` are the two
  order types whose executor reads `attack_on_arrival` (HOLD / SUPPORT never do, so
  a tail fused onto them is stamped and lost);
- or a standing order carrying `until` (`clause_is_a_standing_order`), the engine's
  one implemented condition — `hold until Davout arrives then attack` stays one parse.

Everything else — fortify, scout, drill, defend, retreat, unfortify, form square,
garrison, bombard, recruit, wait — keeps its own order. Before this rule the
exemption enumerated FA-7's stand-still vocabulary, so 40 of 40 other heads had the
tail **replace** the head (`Ney, fortify then attack Mack` marched and fought).
Riders: `_strip_conditions` consumes `and then` whole (no more "Vienna And");
`_detect_attack_on_arrival` reads a boundary (`then` / `and then` / `and` / `;`);
a tactical `move to` / `go to` head with an arrival tail is promoted to `march to`
before any reader (`promote_tactical_move_with_arrival_tail`) while bare `move to`
stays the 1-AP tactical move by design. Flip lever `parser.TAIL_FUSES_ONLY_ONTO_A_MARCH`.
Tests: `tests/test_cr7_1_the_tail_stops_eating_the_head.py`. ⚠ The golden corpus is
688/688 in BOTH arms of this rule — pins for compound orders must drive
`CommandParser.parse` or `POST /command`, never the corpus alone.

### Stage 2b: Conditions — one vocabulary, honest referents, the echo (CR-7-4, September 22, 2026)

**File:** `backend/ai/condition_grammar.py` — the ONE list every reader derives from.
`strategic_parser._strip_conditions` (what is REMOVED from the target text) and
`_parse_condition` / `detect_strategic_command` (what is READ) used to hold different
vocabularies, so `hold Lorraine till Ney arrives` held the phantom province
"Lorraine Till Ney Arrives". Rules:

1. A clause the engine reads never reaches the target text (`strip_condition_text`
   removes exactly the READ spans + the generic `until …` tail + the arrival tail).
2. A referent the engine cannot meet is REFUSED at 0 AP, by cause, never minted:
   `until X arrives` names a friendly marshal on the board or is refused as
   `unknown_referent` / `enemy_referent` / `self_referent` / `fallen_referent`
   (`refusal_copy` — a sentence about a friendly arrival never blames the enemy).
   `until relief|reinforcements|help arrives` is `until_relieved`. `for 0 turns` is
   refused; `until turn N` is read as `for (N − now) turns` and said so; word-numbers
   and the `Marshal <Name>` honorific are read.
3. Shown == applied: the confirmation and the Strategic Ledger render a condition
   through `describe_condition` (drift-pinned); how a clause was read is echoed
   ("'for three turns' read as for 3 turns"); a subordinate clause the engine could not
   read is NAMED ("'unless attacked' is not a clause I can hold — the order stands
   without it") rather than dropped in silence.
4. `until the battle is won` reads THIS order's battle: the order-scoped
   `last_combat_result` first, the marshal-scoped one only when
   `marshal.last_combat_turn >= order.started_turn` (both combat seams stamp the
   turn; issuance clears the holder's stale result; a legacy result with no turn
   fails closed).

A refusal rides the parse as `refusal="condition"` + `refusal_detail={"kind": …}`;
main.py answers it with `refusal_copy`. Tests: `tests/test_cr7_4_the_engine_says_what_it_heard.py`.

### Stage 2c: The relay — nothing is dropped in silence (CR-7-3, September 22, 2026)

**File:** `backend/commands/relay.py`; the parser's sentence is `parser.sequel_note`.
A compound order's dropped tail rides EVERY arm of the response — success, refused
head, objection, clarification, interrupt — as `dropped_sequel` + `relay_kind` +
`relay_note`, and is handed back for the player's seal as `relay_command` (the client
fills the command line at `set_input_enabled(true)` and NEVER sends) only when sending
it now is coherent:

| kind | when | `relay_command` |
|---|---|---|
| `ready` | the head completed this turn and the tail does not undo it, or the tail names another marshal | the tail, re-addressed |
| `contradiction` | the marshal's LIVE state is fortified / square / drilling / defensive and the tail moves him; or a standing HOLD / SUPPORT that an executor override verb would end | none — named |
| `moment` | the head left a live MOVE_TO / PURSUE (a five-hop march outlives the memory of its tail) — destination + ETA named | none |
| `refused_head` | the head did not go out; the tail is never promoted to a new head | none |
| `question` | objection / clarification / interrupt pending — stashed on `world._pending_relay` (transient, never serialized, one command's life, cleared at the turn boundary) and re-judged against the live state when the answer lands (`/respond_to_objection`, `/strategic_response`, the typed answer) | none |

Boundaries (`parser._split_sequential_orders` + `_and_clause_is_a_second_order` +
`_comma_clause_is_a_second_order`): `then` / `and then` / `;` / `and <Marshal>` / a bare
`and <verb>` with its own object / **a bare comma before an order verb** (CQ-10) — the
address comma never splits (a bare name, a diplomatic addressee, a unit named like a
verb, a whole sentence the guards refuse, and emphasis in the head's own verb family
are all controls). A third clause behind the arrival idiom is reported. A relayed tail
pays its own AP when sent; nothing is queued (Stage 2e). `CommandRequest.relayed` →
`command_history[].relayed` is the CR-7-8 re-open instrument.
Tests: `tests/test_cr7_3_the_tail_comes_back.py`.

### Stage 2d: The third verdict and the arrival object (CR-7-5 / CR-7-6, September 22, 2026)

**CR-7-5** — `clause_guards.strip_condition_clauses_with_handoff` returns REFUSE /
BLANK / **HAND-OFF**: `when|if|once|as soon as <friendly marshal> arrives` (and a
LEADING `until … ,`) is handed to the strategic layer as `until_marshal_arrives` when
the residue is a HOLD (`strategic_parser.clause_is_a_hold_order`), the name is on the
friendly roster, and it is the sole condition — fails closed otherwise. The nine
REFUSING words and the two-word floor are untouched; the blank stays index-preserving;
a refusal stays terminal. The condition verdict is ALSO taken on the pre-negation text
(`attack Mack if he is not fortified` fought before); a trailing `should <determiner |
marshal> …` is the inversion; punctuation glued to a marker is skipped before the floor
is measured (the comma leak). Tests: `tests/test_cr7_5_the_third_verdict.py`.

**CR-7-6** — `StrategicOrder.arrival_target` (declared, serialized, nested in the
marshal dict) carries the man an arrival tail NAMED; `strategic.pick_contact_enemy`
prefers him among the enemies met at the first-step, mid-path and arrival seams and
falls back to `enemies[0]` as before. Measured before the fix: with Mack and Charles
both at Swabia, `march to Swabia then attack Archduke Charles` engaged Mack.
Tests: `tests/test_cr7_6_the_arrival_order_carries_its_object.py`.

### Stage 2e: There is no queue (CR-7-8, September 22, 2026)

Orders are never held for a later turn — `COMMAND_ROBUSTNESS_SPEC.md` §11.1 carries
the ruling, its measured reasons and two instrumented re-open conditions; the census
is `tests/test_cr7_8_the_queue_is_retired.py`.

### Stage 2f: The conditions say what they mean (CR-7-9, September 22, 2026)

**The connector.** Several condition arms on one order combine by the word that joins
them, read by `condition_grammar.read_connector`: `and` = **all-of** (`StrategicCondition
.require_all`, serialized), `or` / a comma / no word = **any-of**, whichever comes first —
the engine's own reading since conditions existed, now SAID. A bare second clause reads
without its own `until` (`until Davout arrives or the battle is won`); a dangling connector
never reaches the target; both `and` and `or` in one order read as any-of and the echo says
so; an arrival referent already at the marshal's side is noted. The ONE sentence
(`describe_condition`) renders `… or … — whichever comes first` / `… and … — both` (`— all
3`), ticks off a met arm `(met)` and, with `only_unmet`, names what is still waited for.

**The latch.** `StrategicOrderProcessor._condition_arms` is the one per-arm reader (the
personality-voiced completion labels unchanged, plus a plain `fact` per arm). Any-of: the
first met arm ends the order on its own line. All-of: a newly met arm is LATCHED on
`StrategicOrder.condition_progress` (serialized) — an arm that was true and passed stays
counted — and reported as a **progress beat** on that tick's own report line (`Davout has
arrived. Ney holds on — until the battle is won as well.`); the order ends when every arm
has landed, on the line of the arm that closed the set (`Victory achieved! With that, every
condition of Ney's order is met.`). The hold handler's own expiry never fires an all-of.

**The timer.** ONE rule, `strategic.count_order_turns`, read by the checker, the hold
handler's expiry, the skip branch and the Ledger: a HOLD (or any non-SUPPORT order)
**counts the turn it was given** — its enemy phase is fought with him holding, and the tick
that reads the timer runs at that turn's end before the counter advances, so the issuing
turn's tick now reads the condition and `hold for 1 turn` ends with the turn it was given;
a SUPPORT **counts from the turn after arrival** — the enemy phase precedes the strategic
tick that lands him, so `support Davout for 3 turns` is three enemy phases at his side. The
Ledger reads the same function with `including_current=False`, so "N turn(s) remaining" is
the end-turns still to play and is never 0 on a live order (it was, for a whole turn).
`until turn N` therefore ends the hold as turn N begins.

**The let-go.** Rule 5's stash (Stage 2c) still lives for one command, but it is never
dropped mute: the question note says for how long it waits, and a command that neither
answers the question nor re-types the tail — or the turn's end — is SAID on the reply
that dropped it (`relay_let_go` + Berthier's line, from `relay.let_go_line`, spoken once by
`build_base_response` off the transient `world._relay_let_go`); the consuming routes
(the typed objection answer, the popup routes, and now the typed interrupt answer, which
had dropped the tail in silence) clear it. Tests:
`tests/test_cr7_9_the_conditions_say_what_they_mean.py`; sweep `tools/_sweep_cr7_9.json`.

### Stage 2g: What the sentence forbids is never the order (CRT-1, September 23, 2026)

**The vocabulary is ONE regex.** `clause_guards._negation_re()` — read by
`negation_marker_spans`, `strip_negated_clauses`, and through them by
`dialogue_routing.text_the_player_still_means` for every dialogue family — holds every
way English says "not that": the plain negatives PARSE-NEG shipped, and (CRT-1) the modal
ones (`would/could/might/may/ought/need/dare + not`, contracted or not), the perfect
(`have/has/had + not`), the past copula (`was/were + not`), the idioms of reluctance (`'d
rather not`, `had better not`), the contracted auxiliaries (`I'd not`, `we'll not`), the
deliberative openers `ought we` / `have we` (no imperative begins with them — and `have`
must stay OUT of `is_question`'s lead, because `have Ney attack Mack` is the causative
order), and the negative indefinites (`nobody`, `no one`, `none`, `not one`, `not a man`,
`no man/corps/…`). A negative indefinite is its clause's SUBJECT: it left `_COLLECTIVE`
(a prohibition on everybody is not an address the auto-assign serves), it stays in
`_NEVER_AN_ADDRESS`, and a vocative comma typed straight after it belongs to its clause
(`Nobody, retreat` is `Nobody retreat`). A bare `not` and a bare `no` stay outside the
vocabulary (CR-4's `not you, Davout`; `no quarter`). A new member of the class is a pin
in `test_crt1_what_the_sentence_forbids.py`, not a new row.

**The reason is not the order.** `strip_reason_clauses` (lever
`THE_REASON_IS_NOT_THE_ORDER`) blanks — same-length, never splicing, never choosing — a
THIRD-PARTY reason clause: a subordinator (`as`, `because`, `since`, `now that`, `seeing
that`) or a bare comma, then `they` / `he` / `she`, `the enemy` / any `the <demonym>`
(morphological: `-ians`, `-ans`, `-ish`, `-ese`), or a foe on the roster in EITHER
register (`llm_client.foe_names_for_guards`: keys and printed forms — `ArchdukeCharles`
and `Archduke Charles`), then an auxiliary + verb or a hostile third-person verb. `it` is
never a subject (`it is time to attack Mack` is an order); a friendly name never is (`as
Davout arrives` is timing, Stage 2d's). Sited AFTER `is_question` and the condition guard,
so a condition keeps its refusal or hand-off. **It is applied at all three readers of the
raw text** — the mock chain, the strategic layer's read (`parser.py`), and the parser's
fuzzy target scan — because a blank that reaches only one reader is the FA slice-1
defect. A sentence that is ONLY the enemy's movements is refused by name
(`refusal == "reason"`, `main.py`) with its clause quoted, never shrugged at.

### Stage 3: Validation

**File:** `backend/ai/validation.py`
- **Line 117:** `VALID_STRATEGIC_TYPES = {"MOVE_TO", "PURSUE", "HOLD", "SUPPORT"}`
- **Line 118-123:** If `is_strategic=True` and `strategic_type` not in valid set -> falls back to tactical (clears `is_strategic`, `strategic_type`)

### Stage 4: Executor Interception

**File:** `backend/commands/executor.py`
- **Line 863-876:** Strategic interception block:
  ```python
  if is_strategic and strategic_type:
      result = self._execute_strategic_command(command, world, game_state)
      _skip_routing = True
  ```
- **Line 1984:** `_execute_strategic_command()` method:
  1. Validates marshal has actions (costs 2, or 1 for LITERAL)
  2. Builds path using personality-aware pathfinding (cautious avoids enemies)
  3. Creates `StrategicOrder` dataclass (line 2118)
  4. Sets `marshal.strategic_order = order` (line 2133)
  5. Executes first step (move or action)
  6. Returns result dict with `strategic_order_set: True`

**Key flags:**
- `_skip_routing` (line 872): Prevents falling through to tactical action routing
- `_strategic_execution` (line 456): When True, skips action cost, objections, override checks
- `_sortie` (line 457): Prevents advancing into conquered region on victory (HOLD sally)

### Stage 5: Turn-End Processing

**File:** `backend/game_logic/turn_manager.py`
- **Line 140-144:** After enemy phase, before `advance_turn()`:
  ```python
  strategic_exec = StrategicExecutor(self.executor)
  strategic_results = strategic_exec.process_strategic_orders(world, game_state)
  ```

**File:** `backend/commands/strategic.py`
- **Line 40:** `process_strategic_orders(world, game_state)` -- iterates all marshals
- **Line 74:** `_execute_strategic_turn(marshal, order, world, game_state)`:
  1. **Line ~81:** Retreat recovery check (pauses order if recovering)
  2. **Line ~91:** Condition check via `_check_condition()`
  3. **Line ~100:** Interrupt check via `_check_interrupts()`
  4. Routes to command-specific handler

### Stage 6: Command Handlers

#### MOVE_TO (strategic.py:127)
- Moves one step along path per turn
- Recalculates path if stale (personality-aware)
- Completes when marshal reaches destination
- If `attack_on_arrival=True`, attacks first enemy at destination

#### PURSUE (strategic.py:274)
- Recalculates path to enemy marshal each turn (target moves)
- Uses personality-aware pathfinding
- Attacks when in same region as target
- Completes on victory or target destroyed

#### HOLD (strategic.py:398)
- Sets `holding_position=True` (Grouchy gets +15% defense)
- **Sally mechanic:** Aggressive marshals attack adjacent enemies then return
  - Move to adjacent -> attack (with `_sortie=True`) -> return to hold position
- Completes when condition met (max_turns, etc.)

#### SUPPORT (strategic.py:573)
- Moves toward ally marshal
- If `follow_if_moves=True`, tracks ally movement
- If `join_combat=True`, joins ally's battles
- Completes when `until_battle_won` condition triggers

### Data Structures

#### StrategicOrder (marshal.py:75)
```python
@dataclass
class StrategicOrder:
    command_type: str          # "MOVE_TO", "PURSUE", "HOLD", "SUPPORT"
    target: str                # Region name or marshal name
    target_type: str           # "region", "marshal", "battle", "generic"
    path: List[str]            # BFS path from current to target
    conditions: StrategicCondition
    turns_active: int = 0
    attack_on_arrival: bool = False
    follow_if_moves: bool = False
    join_combat: bool = False
    target_snapshot_location: str = ""
    last_combat_result: str = ""
    last_combat_turn: int = 0
```

#### StrategicCondition (marshal.py:37)
```python
@dataclass
class StrategicCondition:
    max_turns: Optional[int] = None
    until_marshal_arrives: Optional[str] = None
    until_marshal_destroyed: Optional[str] = None
    until_battle_won: bool = False
    until_relieved: bool = False
    auto_cancel_below_ratio: Optional[float] = None
```

#### Key Marshal Fields (Strategic)
- `marshal.strategic_order` (marshal.py:299) -- active order or None
- `marshal.in_strategic_mode` (marshal.py:492) -- property, True if order exists
- `marshal.precision_execution_active` -- Grouchy clarity bonus flag
- `marshal.strategic_combat_bonus` -- consumed in combat
- `marshal.strategic_defense_bonus` -- consumed in combat

### Cross-Cutting Systems

#### Personality-Aware Pathfinding
**File:** `backend/commands/strategic.py`
- **Line 1046:** `_get_personality_aware_path(marshal, destination, world)`
- **Line 1038:** `_get_enemy_occupied_regions(nation, world)`
- Cautious: avoids enemy-occupied regions (falls back to direct if no safe route)
- Aggressive/Literal/Others: direct path

#### Blocked Path Handling
**File:** `backend/commands/strategic.py`
- **Line 881:** `_handle_blocked_path(marshal, next_region, order, world, game_state)`
- Literal: silently reroutes around obstacle
- Aggressive: auto-attacks at >=0.7 ratio, otherwise asks player
- Cautious: always asks player for decision

#### Interrupt Detection
**File:** `backend/commands/strategic.py`
- **Line 707:** `_check_interrupts(marshal, order, world, game_state)`
- Uses `world.get_battles_within_range()` (world_state.py:864)
- LITERAL personality skips cannon fire interrupts ("The Grouchy Moment")

#### Condition Evaluation
**File:** `backend/commands/strategic.py`
- **Line 792:** `_check_condition(marshal, order, world)`
- Evaluates: `max_turns`, `until_marshal_arrives`, `until_battle_won`, `until_marshal_destroyed`
- `until_battle_won` triggers on both victory AND stalemate

### Battle Tracking (for Cannon Fire)

**File:** `backend/models/world_state.py`
- **Line 59:** `self.battles_this_turn: List[Dict] = []`
- **Line 849:** `record_battle(region, attacker, defender)` -- called by combat resolver
- **Line 864:** `get_battles_within_range(location, range)` -- BFS distance check
- **Line 873:** `clear_turn_battles()` -- called at turn start

### Strategic Objection Pattern

**CRITICAL:** Strategic objections use `world.pending_strategic_objection`, NOT `world.pending_objection` (which is for tactical objections).

**Flow:**
```
1. User issues strategic command (HOLD, PURSUE, MOVE_TO, SUPPORT)
2. _execute_strategic_command() calls check_strategic_objection()
3. If objection triggers:
   a. Store objection data in world.pending_strategic_objection
   b. Return {pending_objection: True, objection: {...}}
4. Frontend shows popup, user chooses trust/insist/compromise
5. Frontend calls /respond_to_objection endpoint
6. handle_objection_response() checks for pending_strategic_objection FIRST
7. Routes to _handle_strategic_objection_from_endpoint()
8. Maps choices (trust->preferred, insist->proceed) and re-executes
```

### Override & Cancel

When a player issues a tactical command to a marshal with an active strategic order:
- **Override actions** (attack, move, defend): Silently cancel strategic order, execute tactical
- **Non-override actions** (wait, scout): Execute alongside strategic order
- **Explicit cancel** ("halt", "cancel"): Cost 1 action, -3 trust
- Implementation location: `executor.py` (inline in `execute()` — override handled via direct strategic order cancellation)

---

## 5. LLM Integration

> The parser/LLM hardening phase plan (slices CR-0..CR-7) lives in `docs/COMMAND_ROBUSTNESS_SPEC.md`. CR-3 (July 4, 2026) modernized the live provider: model pin `claude-haiku-4-5`, forced tool-use structured output (no free-text JSON extraction on the primary path), LLM strategic verbs remapped to executor-dispatchable base actions at the provider seam, the dead `dialogue` output field cut, an `llm_error` signal that guarantees at most ONE blocking LLM call per request, a `diplomatic_data["action"]` allowlist at the validation seam, and the cheat gate keyed off the parse result's `key_source` instead of the LLM_MODE env var.

### Command Parsing Pipeline

```
User Input: "Ney, attack Wellington"
                |
                v
+===============================================+
|           LLMClient.parse_command()           |
|              (llm_client.py)                  |
+===============================================+
                |
                | STEP 1: Always run fast parser first
                v
+-----------------------------------------------+
|        Fast Parser (keyword matching)         |
|        _parse_with_mock()                     |
|                                               |
|  Returns ParseResult with confidence score:   |
|  - 0.95 = marshal + action + target           |
|  - 0.9  = action + one identifier             |
|  - 0.8  = action only                         |
|  - 0.5  = unknown (couldn't parse)            |
+-----------------------------------------------+
                |
                | STEP 2: Check if LLM fallback needed
                |
                | Skip LLM if:
                |   - Mock mode (LLM_MODE=mock)
                |   - High confidence (>= 0.7)
                |   - No game_state provided
                |   - Meta command (help, debug, etc.)
                |
                v
        [confidence < 0.7 AND live mode?]
               /              \
              NO              YES
              |                |
              v                v
     Return fast result   +-----------------------------------+
                          |   AnthropicProvider.parse()       |
                          |        (providers.py)             |
                          |   claude-haiku-4-5, forced tool   |
                          |   call (PARSE_TOOL + tool_choice) |
                          |   -> structured input, no brace   |
                          |   extraction on the primary path  |
                          |   API failure sets llm_error      |
                          |   (suppresses 2nd LLM call:       |
                          |   Berthier + CR-2 forced retry)   |
                          +-----------------------------------+
                                        |
                                        | strategic verb remap:
                                        | pursue->attack,
                                        | march/support/reinforce->move
                                        v
                          +-----------------------------------+
                          |   validation.validate_parse_result|
                          |   (catches hallucinations +       |
                          |   CR-3 diplomatic_data["action"]  |
                          |   allowlist)                      |
                          +-----------------------------------+
                                        |
                              Return validated result
```

### LLM Files Reference

| File | Purpose |
|------|---------|
| `backend/ai/llm_client.py` | Main entry point. Fast parser + LLM fallback logic |
| `backend/ai/providers.py` | Provider abstraction (Anthropic, Groq stub) |
| `backend/ai/schemas.py` | ParseResult, ProviderConfig dataclasses |
| `backend/ai/validation.py` | Validates LLM output against game rules |
| `backend/ai/prompt_builder.py` | Builds context-aware prompts |

### Configuration

```bash
# .env file
LLM_MODE=mock          # mock | anthropic | groq (groq not yet implemented)
ANTHROPIC_API_KEY=sk-ant-api03-...   # Required if LLM_MODE=anthropic
```

### Cost Estimation (claude-haiku-4-5, CR-3 measured on the 1805 boot)
- Per request: ~5K input + ~300 output tokens = **~$0.0065**
- 1,000 ambiguous commands = **~$6.50**
- Fast parser catches most commands (only sub-0.7-confidence parses reach the LLM), so real cost is much lower

### Strategic Score & Ambiguity

ParseResult scoring fields drive gameplay mechanics:
- `strategic_score` (0-100): How complex/strategic the command is
- `ambiguity` (0-100): How unclear the command was

**Active effects:**

| Score | Effect |
|-------|--------|
| Ambiguity 0-20 | +15% combat buff (Grouchy explicit order bonus) |
| Ambiguity 21-40 | +10% combat buff |
| Ambiguity 41-60 | +5% combat buff + warning |
| Ambiguity 61+ | No buff, triggers Grouchy clarification popup |
| High strategic | +authority, +morale (Napoleon in his element) |

### Berthier Parse Recovery

When a command can't be parsed (Unknown action, Marshal 'None' not found), Berthier — Napoleon's chief of staff — responds in character instead of showing a raw error.

**Two intercept points in `main.py`:**

| Error | Where | Example |
|-------|-------|---------|
| `"Unknown action"` | Before executor | `"dance with the moon"` |
| `"Marshal 'None' not found"` | After executor | `"scout"`, `"move to Belgium"` (no marshal named) |

**Mock mode:** Template responses from `_berthier_mock_response()` in `llm_client.py`. Three categories (marshal recognised, target recognised, nothing recognised), 2-3 variants each, uses real game-state names.

**Live mode:** One LLM call via `build_berthier_recovery_prompt()` in `prompt_builder.py`. Berthier character: nervous, meticulous, reacts to the Emperor's tone (insults, absurdity, rudeness). Falls back to mock templates on API failure.

**CR-3 latency guard:** when the parse-stage LLM call for the same request already failed at the API layer (`llm_error` on the parse dict), both intercept points pass `skip_llm=True` and Berthier answers from the mock templates immediately — the old behavior stacked a second ~5s timeout on top of the first (~10s worst case).

**Files:**
- `prompt_builder.py`: `build_berthier_recovery_prompt()` — system + user prompt
- `llm_client.py`: `generate_berthier_recovery()` + `_berthier_mock_response()`
- `parser.py`: `partial_marshal` / `partial_target` fields in failure dicts
- `main.py`: Two early-return blocks (before and after executor)

**Does NOT change:** No new actions, no new popups, no state changes, no serialization, no executor changes. Same `success: False` response shape — Godot needs no changes.

### Key Insight

**Executor stays rule-based.** LLM helps with parsing ambiguous commands, but game mechanics are 100% deterministic. No LLM randomness in combat, movement, or AI decisions.

---

## 6. Cavalry Limits

### Mechanics

Cavalry units (like Ney) cannot hold defensive positions for extended periods. Horses need to move.

| Counter | Triggers At | Effect | Trust Penalty |
|---------|-------------|--------|---------------|
| `turns_in_defensive_stance` | 3 turns | Auto-switch to AGGRESSIVE | -3 |
| `turns_fortified` | 3 turns | Auto-unfortify | -3 |

**Maximum penalty per turn:** -6 (if both trigger simultaneously)

### Unit Type Comparison

#### CAVALRY (`cavalry=True`, `movement_range=2`)

**Movement:**
- Can attack enemies up to 2 regions away
- Still only moves 1 region per turn (attack range != movement)

**Defensive Limits (from `world_state.py`):**

| Counter | Trigger | Effect | Trust Penalty |
|---------|---------|--------|---------------|
| `turns_in_defensive_stance` | 3+ turns in DEFENSIVE stance | Auto-switch to AGGRESSIVE | -3 |
| `turns_fortified` | 3+ turns fortified | Auto-unfortify, defense_bonus = 0 | -3 |

#### INFANTRY (`cavalry=False`, `movement_range=1`)

**Movement:**
- Can only attack adjacent regions
- Standard 1-region movement

**No Defensive Limits:**
- Can hold defensive stance indefinitely
- Can stay fortified indefinitely
- No automatic stance changes

### Turn Flow

```
TURN START
    |
    +-> _check_cavalry_limits()
    |       |
    |       +-> If cavalry in defensive stance for 3+ turns:
    |       |       - Switch to AGGRESSIVE
    |       |       - Reset turns_in_defensive_stance = 0
    |       |       - trust.modify(-3)
    |       |       - Return "cavalry_stance_forced" event
    |       |
    |       +-> If cavalry fortified for 3+ turns:
    |               - Set fortified = False
    |               - Reset defense_bonus = 0
    |               - Reset turns_fortified = 0
    |               - trust.modify(-3)
    |               - Return "cavalry_fortify_forced" event
    |
    +-> Events shown in tactical messages at turn start

TURN END (in _process_tactical_states)
    |
    +-> For cavalry in defensive stance:
            turns_in_defensive_stance += 1
        For cavalry that is fortified:
            turns_fortified += 1
```

### Counter Resets

- Both counters reset when marshal moves (`move_to()` method)
- `turns_in_defensive_stance` resets when switching to non-defensive stance
- `turns_fortified` resets when unfortifying

```python
# marshal.py move_to()
if getattr(self, 'cavalry', False):
    self.turns_in_defensive_stance = 0
    self.turns_fortified = 0
```

### Event Types

| Event Type | Message Example |
|------------|-----------------|
| `cavalry_stance_forced` | "Ney's cavalry is too restless! Auto-switched to AGGRESSIVE. Trust -3" |
| `cavalry_fortify_forced` | "Ney's horses cannot stay still! Auto-unfortified. Trust -3" |
| `cavalry_restless_warning` | "Warning: Ney's cavalry growing restless (turn 3 of 3)..." |

---

## 6b. Artillery Unit Type

Artillery units are a third marshal type alongside infantry and cavalry. They provide powerful bombardment but sacrifice mobility.

### Core Properties

| Property | Value |
|----------|-------|
| `artillery` flag | `True` (mutually exclusive with `cavalry`) |
| `movement_range` | 1 (same as infantry) |
| Attack restriction | Cannot attack the turn they move (`moved_this_turn`) |
| Win behavior | Stay in position after adjacent win — no advance, no capture |
| Banned actions | Glorious Charge, PURSUE auto-promotion |
| Defense penalty | -25% when `moved_this_turn` is True |

### moved_this_turn Lifecycle

1. **Set True** — on successful move in `_execute_move` (after `marshal.move_to()`)
2. **Blocks attack** — early return in `_execute_attack` if artillery + moved_this_turn
3. **Applies defense penalty** — -25% in `get_defense_modifier()` if moved_this_turn
4. **Reset False** — at turn start in `advance_turn()` (with other per-turn resets)

### Combat Interactions

| Interaction | Effect | Location |
|-------------|--------|----------|
| Cavalry vs Artillery | +30% shock_multiplier | `combat.py` (target-type, NOT marshal intrinsic) |
| Fort degradation | 10% per artillery attack (vs 5% for non-artillery) | `combat.py` |
| No advance on win | Artillery stays at origin, target NOT captured | `executor.py` |
| Ranged bombardment | Dedicated `_execute_bombardment()` path when attacker.location != defender.location | `executor.py` |
| Same-region combat | Normal `resolve_battle()` rules apply (full return damage, counter-punch possible) | `executor.py` → `combat.py` |

### Starting Marshals

| Marshal | Nation | Location | Strength | Personality |
|---------|--------|----------|----------|-------------|
| Drouot | France | Paris | 25,000 | cautious |

### Exhaustion Exemption (Session 2)

Artillery is exempt from exhaustion penalties — sustained bombardment is their core function. `_get_exhaustion_penalty()` returns 0.0 for artillery. Combat messages skip exhaustion display. Battle report snapshots skip exhaustion for artillery attackers.

### Cavalry Momentum (B5 Balance)

Cavalry gains momentum from repeated attacks instead of suffering exhaustion. `_get_exhaustion_penalty()` returns a NEGATIVE value (bonus) for cavalry:

| Attack # | Infantry | Artillery | Cavalry |
|----------|----------|-----------|---------|
| 1st | 0% | 0% (exempt) | 0% |
| 2nd | -10% | 0% (exempt) | **+5% bonus** |
| 3rd | -20% | 0% (exempt) | **+10% bonus** |
| 4th+ | -30% | 0% (exempt) | **+10% (cap)** |

- Implemented in `marshal.py::_get_exhaustion_penalty()` — returns negative value for cavalry, applied via same `(1.0 - penalty)` formula (negative penalty = bonus)
- Stacks with existing recklessness system for aggressive cavalry (Ney gets BOTH momentum + recklessness bonuses)
- Balanced/cautious cavalry marshals benefit from momentum alone
- Thematic: cavalry charges gain devastating momentum through sustained pressure. Infantry tires; cavalry accelerates.

**Key code:** `marshal.py::_get_exhaustion_penalty()`, `marshal.py::attacks_this_turn`

### Bombardment Streak (Session 2)

Tracks consecutive bombardments on the same target:

| Field | Type | Description |
|-------|------|-------------|
| `last_bombardment_target` | string\|null | Region of last bombardment target |
| `bombardment_streak` | int | Consecutive attacks on same target |

- **Increments:** When artillery attacks same target region as previous bombardment
- **Resets to 1:** When artillery attacks a different target
- **Resets to 0:** When artillery moves (`_execute_move`)
- **Cleared:** On broken state recovery

### Berthier Bombardment Advisory (Session 2)

After artillery bombardment, if defender's `defense_bonus <= 0` AND region `fortification_bonus < 0.15`, Berthier advises: "Sire, the enemy fortifications at {location} are crumbling. An infantry assault would now have favorable odds." Returned as `bombardment_advisory` in result dict.

### Personality Objections (Session 51 — BOMBARDMENT_SPEC §7.1)

| Personality | Trigger | Condition | Level |
|-------------|---------|-----------|-------|
| Cautious | `ordered_into_melee` | Artillery attack on enemy in same region | STRONG |
| Cautious | `reckless_repositioning` | Artillery move + streak >= 2 + adjacent target defense_bonus > 0 | MODERATE |
| Cautious | `ordered_to_cease_fire` | Artillery defend/fortify + streak >= 1 + adjacent target defense_bonus > 0.05 | MODERATE |
| Cautious | `wasted_fire` | Artillery attack + target defense_bonus == 0 + target strength < 8000 | MILD |
| Cautious | `last_shot_advisory` | Artillery attack + bombardments_this_turn == 1 + multiple adjacent targets | MILD |
| Aggressive | `wasted_fire` | Artillery attack + target defense_bonus == 0 + target strength < 8000 | MILD |
| Literal | (none) | Never objects | — |

### AI Artillery Behavior (Session 2)

**P2 Screen Check:** If artillery has no friendly infantry screen (same/adjacent region) AND enemy cavalry within 2 regions, retreat toward nearest friendly infantry. Priority 2 (survival).

**P4 Bombardment Sort:** Artillery sorts valid targets by bombardment value: fortified+fort_building > fortified_only > unfortified, then by distance. Cavalry prefers exposed (unscreened) artillery targets.

**P7 Anti-Oscillation:** If artillery has adjacent enemies and hasn't moved this turn, skip P7 strategic movement (stay and bombard). If artillery must move, uses `_score_artillery_position()` for destination evaluation.

**Position Scoring (`_score_artillery_position`):**
- +30 hills terrain
- +25 adjacent fortified enemy
- +20 friendly infantry screen co-located, +10 adjacent
- -30 exposed to enemy cavalry (within 2, no screen)
- +10 own territory
- **Frontline penalty:** -50 if on enemy border without infantry screen, -30 with co-located infantry screen. Prevents artillery advancing to front-line regions.
- **Behind-screen bonus:** +15 if not on front line AND friendly infantry holds an adjacent front-line region. Rewards safe rear positions for bombardment support.

**Helper Functions:**
- `_artillery_has_screen(marshal, nation, world)` — friendly non-cavalry, non-artillery in same/adjacent region
- `_enemy_cavalry_within_range(marshal, nation, world, max_range)` — BFS to depth max_range
- `_score_artillery_position(region, marshal, nation, world)` — position quality score
- `_find_nearest_friendly_infantry(marshal, nation, world)` — BFS for retreat target

### Bombardment Resolution (Session 48)

Ranged bombardment now uses a dedicated `_execute_bombardment()` method in executor.py instead of the old 50% return casualties hack in combat.py.

**Routing rule:** In `_execute_attack()`, after target resolution: if `marshal.artillery` AND `marshal.location != enemy_marshal.location` → route to `_execute_bombardment()`. Same-region artillery combat still uses full `resolve_battle()`.

**Damage formula:**
```
raw_damage = defender.strength × 0.04 × (1.0 + shock_skill/15.0) × terrain_modifier
final_damage = int(raw_damage × uniform(0.80, 1.20))
return_casualties = int(marshal.strength × 0.015 × uniform(0.80, 1.20))
```

**Terrain bombardment modifiers (region.py `TERRAIN_BOMBARDMENT_MODIFIER`):**

| Terrain | Modifier | Reason |
|---------|----------|--------|
| Plains | 1.10 | +10% — open ground, no cover |
| Forest | 0.80 | -20% — trees obscure targets |
| Hills | 0.75 | -25% — defilade behind ridgelines |
| Mountains | 0.60 | -40% — deep cover, hard to range |
| Urban | 0.70 | -30% — buildings provide shelter |
| River Crossing | 1.00 | Neutral — rivers don't help vs shells |

**Per-bombardment effects:**
- Fort degradation: -0.10 (always artillery rate), floors at 0
- Defender morale: -3
- Attacker morale: unchanged
- No winner/loser, no battles_won/lost, no counter-punch
- `bombardments_this_turn` incremented (max 2 per turn)
- `attacks_this_turn` incremented (shares exhaustion counter)
- Bombardment streak tracking (same as Session 43)

**Defender destroyed:** Delegates to `_apply_forced_retreat_or_break()` for consistent break behavior. Region NOT captured (artillery doesn't advance).

**Per-turn limit:** `bombardments_this_turn` field on marshal, reset to 0 in `advance_turn()`. Max 2 bombardments per turn.

### Collateral Damage (Session 49)

After primary bombardment resolves, stray shells can hit other forces in the target region:

```
For each non-primary marshal in target region (strength > 0, not broken/retreating):
  40% chance of hit:
    collateral_raw = primary_raw_damage × 0.25
    collateral_casualties = int(collateral_raw × uniform(0.80, 1.20))
    force.take_casualties(collateral_casualties)
    force.adjust_morale(-1)
```

**Friendly fire:** When collateral hits a marshal of the same nation as the artillery:
- Trust penalty: -5 on the hit marshal
- Relationship penalty: -1 between hit marshal and artillery marshal
- If trust drops to <= 20, normal redemption event triggers

**Region-name targeting:** When player says "bombard Waterloo" (region name, not marshal name), the strongest enemy marshal in that region is auto-selected as the primary target. Other marshals become collateral candidates.

**Scope:** Collateral only affects marshal objects. Capital garrisons and player garrison detachments (region attributes) are NOT affected.

**Collateral array in result dict and event log:**
```python
"collateral": [
    {"name": "Uxbridge", "nation": "Britain", "casualties": 998, "friendly_fire": False},
    {"name": "Davout", "nation": "France", "casualties": 750, "friendly_fire": True},
]
```

### Berthier Bombardment Observations (Session 52)

After each bombardment, Berthier provides a contextual observation embedded in `bombardment_result.berthier_observation`. Selection priority:

| Priority | Condition | Observation Key |
|----------|-----------|----------------|
| P1 | Defender reduced to 0 | `bombardment_target_broken` |
| P2 | Collateral hit friendly force | `bombardment_friendly_fire` |
| P3 | Fort degraded this bombardment | `bombardment_fort_cracking` |
| P4 | Terrain modifier < 0.80 | `bombardment_terrain_difficulty` |
| P5 | Casualties < 3% of defender's pre-bombardment strength | `bombardment_ineffective` |
| P6 | Default | `bombardment_effective` |

Templates use `{marshal}`, `{enemy}`, and `{terrain}` placeholders. Terrain names have underscores replaced with spaces.

**Godot display:** `_display_bombardment_report()` in `main.gd` shows terrain effectiveness, casualties, fort degradation, collateral (with friendly fire highlighting), bombardments remaining, and the observation quote. Separate from the melee `_display_berthier_report()`.

### Strategic HOLD Bombardment (Session 51)

Artillery marshals on strategic HOLD auto-bombard adjacent enemies instead of using personality-specific sally/fortify behavior.

**Routing:** In `_execute_hold()`, if `marshal.artillery == True` and at hold position → dispatch to `_execute_hold_bombardment()`.

**Target selection by personality:**
- **Cautious:** Crack forts first (highest `defense_bonus`), then biggest army
- **Aggressive:** Finish the weak first (lowest `strength`)
- **Literal:** Lock on previous target (`order.bombardment_target`), fall back to default if target left

**Edge cases handled:**
- Enemy enters artillery's region → HOLD breaks, requests orders
- `bombardments_this_turn >= 2` → "already fired today" message, order continues
- No adjacent targets → "maintaining readiness" message, order continues
- Broken/retreating/dead targets excluded from selection
- Executor failure → graceful fallback message, order continues
- Timed expiry and not-at-position checked BEFORE artillery dispatch

**New serialization field:** `bombardment_target` on `StrategicOrder` — stores locked target name for literal personality. Defaults to `None`.

### Key Files

| File | What changed |
|------|-------------|
| `marshal.py` | `artillery` flag, `moved_this_turn`, defense modifier, exhaustion exemption, `bombardment_streak` + `last_bombardment_target`, `bombardments_this_turn`, serialization, starting marshals, **`bombardment_target` on StrategicOrder (Session 51)** |
| `combat.py` | Cavalry counter (+30%), fort degradation (10%), cavalry_counter_message, artillery exhaustion message skip |
| `executor.py` | Can't attack after moving, no advance on win, glorious charge ban, PURSUE block, recruit type logic, bombardment streak tracking, Berthier advisory, broken state cleanup, **`_execute_bombardment()` (Session 48)** |
| `world_state.py` | Artillery constants, pool regen, `get_artillery_regen_rate()`, moved_this_turn reset, **bombardments_this_turn reset (Session 48)** |
| `enemy_ai.py` | moved_this_turn gate, pool-aware recruit, cost-aware admin, P2 screen check, P4 bombardment sort + cavalry preference, P7 anti-oscillation + position scoring, 4 helper functions |
| `strategic.py` | **`_execute_hold_bombardment()` + `_hold_no_targets()` (Session 51)** |
| `battle_report.py` | Artillery observation templates, exhaustion snapshot skip for artillery, **6 bombardment observation categories + `_pick_bombardment_observation()` + `generate_bombardment_report()` (Session 52)** |
| `objection_v2.py` | **5 artillery triggers: ordered_into_melee (STRONG), reckless_repositioning (MODERATE), ordered_to_cease_fire (MODERATE), wasted_fire (MILD), last_shot_advisory (MILD) (Session 51)** |
| `disobedience.py` | **5 artillery flavor text keys under cautious personality (Session 51)** |
| `llm_client.py` | Artillery keywords (bombard, barrage, shell, cannonade), Drouot in known_marshals |
| `prompt_builder.py` | Drouot bombardment few-shot example |

---

## 6b. Square Formation (Session 67 — Tactical Triangle Part A)

Infantry marshals can form a defensive square — highly effective against cavalry but vulnerable to artillery fire. Part of the Tactical Triangle (infantry ↔ cavalry ↔ artillery).

### Actions

| Action | AP | Type | Description |
|--------|-----|------|-------------|
| `form_square` | 1 | Normal | Infantry enters square formation |
| `break_square` | 0 | Free | Returns to line formation |

### Eligibility (form_square)

| Check | Blocks if |
|-------|-----------|
| Unit type | `cavalry == True` or `artillery == True` |
| Already square | `square_formation == True` |
| Fortified | `fortified == True` (mutual exclusion) |
| Broken | `broken == True` |
| Retreating | `retreating == True` |
| Drilling | `drilling == True` or `drilling_locked == True` |

### Combat Interactions

| Attacker Type | Effect | Implementation |
|---------------|--------|----------------|
| Cavalry vs Square | -40% damage (`shock_multiplier *= 0.60`) | `combat.py` |
| Artillery vs Square | +50% damage (`shock_multiplier *= 1.50`) | `combat.py` |
| Infantry vs Square | No special modifier | — |
| Square defense | +5% defense modifier | `marshal.py get_defense_modifier()` |

Both normal and deferred (`apply_casualties=False`) combat paths handle these interactions.

### Bombardment vs Square

- **+50% damage:** `square_bombardment_bonus = 1.50` applied to `raw_damage` in `_execute_bombardment()`
- **-15 extra morale:** Total morale hit = -18 (3 base + 15 square penalty)
- Packed formation is a perfect artillery target

### Auto-Break

Square automatically breaks when marshal receives any active order:

| Breaks on | Does NOT break on |
|-----------|-------------------|
| attack, move, fortify, drill, recruit, garrison, stance_change, glorious_charge | form_square, break_square, wait, end_turn |

`_auto_break_square(marshal, action_name)` called at top of each `_execute_*` method. Returns message string for display.

### Coordination & Reinforcement

| Rule | Effect |
|------|--------|
| Attack coordination | 0% (excluded, same as fortified) |
| Defense coordination | Normal (still contributes) |
| Adjacent support | Excluded from count |
| Reinforcement | Cannot reinforce (Rule #15) |

### Strategic Order Cancellation

Forming square cancels any active strategic order, including HOLD with `holding_position` and `hold_region` clearing.

### Objection Triggers (V2a)

| Personality | Trigger | Level |
|-------------|---------|-------|
| Aggressive | form_square (any) | MODERATE |
| Cautious | form_square when fortified | MILD |
| Cautious | form_square when artillery adjacent, no cavalry | MILD |
| Universal | form_square when both cavalry AND artillery adjacent | MILD |

### Enemy AI (P2.5)

Between P2 (critical survival) and P3 (threat response):

- **Form square:** When infantry + enemy cavalry adjacent/co-located + no enemy artillery adjacent/co-located + cooldown <= 0
- **Break square:** When in square + no enemy cavalry adjacent/co-located. Sets `ai_square_cooldown = 2`
- **Anti-oscillation:** Cooldown decrements per turn in `_process_tactical_states()`. Uses transient `ai_square_cooldown` field (not serialized, managed via `getattr/setattr`)

### Tactical State Clearing

- Square clears on `broken == True` or `retreating == True` (in `_process_tactical_states()`)
- AI cooldown decrements each turn

### Battle Report

3 new Berthier observation categories (Priority 6e):

| Key | Condition | Templates |
|-----|-----------|-----------|
| `square_cavalry_repulsed` | Cavalry attacker + defender in square | 3 templates |
| `square_artillery_punished` | Artillery attacker + defender in square | 3 templates |
| `square_held_defense` | Defender in square + defender won | 3 templates |

Snapshot entries: "Square formation (vs cavalry)" penalty 40%, "Square formation (vs artillery)" bonus 50%, "Square formation" defense bonus 5%.

### Serialization

| Field | Type | Default | Location |
|-------|------|---------|----------|
| `square_formation` | bool | false | `marshal.py` `to_dict()`/`from_dict()` |

### Key Files

| File | What changed |
|------|-------------|
| `marshal.py` | `square_formation` field, +5% defense modifier, serialization |
| `combat.py` | Cavalry -40%, artillery +50%, deferred path params |
| `executor.py` | `_execute_form_square`, `_execute_break_square`, `_auto_break_square`, bombardment bonus, coordination exclusions, reinforcement Rule #15, SUPPORT advisory |
| `world_state.py` | AP costs (1/0), tactical state clearing, AI cooldown decrement |
| `objection_v2.py` | 4 triggers (aggressive, cautious×2, universal) |
| `enemy_ai.py` | P2.5 form/break square logic |
| `battle_report.py` | 3 observations, snapshot entries |
| `validation.py` | `form_square`, `break_square` in VALID_ACTIONS |
| `parser.py` | `form_square`, `break_square` in valid_actions |
| `llm_client.py` | Mock parser keywords |

---

## 16b. Auto-Bombardment & Overwatch (Session 68)

### Auto-Bombardment (SUPPORT Artillery Pre-Fire)

When a marshal attacks, all same-nation artillery on SUPPORT targeting that marshal automatically fire bombardment against the defender BEFORE `resolve_battle()`.

**Timing:** After `_calculate_coordination_context()` and overwatch, before `resolve_battle()`.

**Eligibility (all required):**
- Same nation as the attacker
- `artillery == True`
- Active SUPPORT order targeting the attacker (`strategic_order.command_type == "SUPPORT"` and `strategic_order.target == attacker.name`)
- `bombardments_this_turn < 2`
- `strength > 0`
- NOT `broken`, NOT `retreated_this_turn`, NOT `retreat_recovery > 0`, NOT `moved_this_turn`
- Adjacent to or co-located with battle region

**Behavior:**
- Calls existing `_execute_bombardment()` — same damage formula, collateral, fort degradation, streak
- Does NOT consume player AP
- Fires for BOTH player and AI attacks (Building Blocks principle)
- Only fires when supported marshal is the ATTACKER (not when they're defending)
- Increments `bombardments_this_turn` on the artillery marshal

**Dead-Defender Check:** If bombardment kills the defender (`strength <= 0`):
- Loop breaks (remaining artillery don't fire)
- `resolve_battle()` is skipped entirely
- Defender removed from `world.marshals`
- Attacker advances (unless artillery) and attempts capture

**Fog of War:** When auto-bombardment fires from an adjacent region (not co-located) and the defender is the player nation, the player gets PARTIAL intel on the artillery's source region via `update_intel_from_transit()`.

**Note:** SUPPORT order is cleared post-battle by the reinforcement system (A-C2 step 5) because artillery "arrives" as an adjacent reinforcer. This is existing Session 61a behavior.

### Overwatch (Passive Artillery Defense)

Enemy artillery in the defender's region passively debuffs all attackers by -3% per eligible gun, capped at 3 guns (-9% max).

**Where applied:** `marshal.py get_attack_modifier()` — after coordination bonus, before return.

**Field:** `overwatch_penalty` (transient, NOT serialized). Set via assignment, read via `getattr(m, 'overwatch_penalty', 0.0)`. Cleared after combat via `_COORDINATION_FIELDS`.

**Eligibility (all required):**
- In the defender's region (same location as battle)
- Different nation from attacker
- `artillery == True`
- `strength > 0`
- NOT `broken`, NOT `retreated_this_turn`, NOT `retreat_recovery > 0`, NOT `moved_this_turn`

**Cap:** `min(artillery_count, 3)`, penalty = `capped * 0.03`.

**Does NOT apply to:**
- Bombardment (ranged fire, separate code path)
- Coordination cap (independent of coordination bonus)

### AI Awareness

`_evaluate_target_ratio()` in `enemy_ai.py` factors overwatch into ratio calculation:
- Counts same-nation artillery in target's region
- Applies `(1.0 - capped_art * 0.03)` multiplier to effective ratio
- Eligible checks match executor overwatch checks

### Battle Report

3 new Berthier observation categories:

| Key | Priority | Condition | Templates |
|-----|----------|-----------|-----------|
| `support_bombardment_effective` | 0.6 | Auto-bombardment fired, significant damage | 3 templates with `{artillery}` placeholder |
| `support_bombardment_minimal` | 0.6 | Auto-bombardment fired, minimal damage | 3 templates with `{artillery}` placeholder |
| `overwatch_repelled` | 6f | Overwatch active (≥1 enemy artillery in region) | 3 templates |

Snapshot entries:
- "Artillery overwatch" penalty (int % value) in `snapshot_attacker_modifiers()`
- `{artillery}` placeholder in `_fill()` for support bombardment templates

### Key Files

| File | What changed |
|------|-------------|
| `marshal.py` | `overwatch_penalty` in `get_attack_modifier()` (transient, not serialized) |
| `executor.py` | `_calculate_overwatch()`, auto-bombardment loop in `_execute_attack()`, dead-defender early exit, `overwatch_penalty` in `_COORDINATION_FIELDS` |
| `battle_report.py` | 3 observation categories, snapshot entry, `{artillery}` placeholder |
| `enemy_ai.py` | Overwatch factor in `_evaluate_target_ratio()` |

---

## 7. Redemption System

### Trigger

When trust falls to <=20, a redemption event triggers via `check_redemption_threshold()` in `disobedience.py`. The centralized helper gates on: trust <= 20, not already pending, not autonomous, not administrative, not on cooldown, player nation only. Wired at: V1 objection resolution, tactical defiance success, strategic defiance success, strategic endpoint fallthrough, bombardment collateral, strategic interrupt trust penalties (7 sites), and cavalry forced-stance/unfortify penalties. **FA slice 9 (September 5, 2026):** every other trust-LOWERING write goes through ONE helper, `disobedience.stage_redemption(world, marshal, result=, events=)` — the ES-7 erosion tick (which returns its events onto the end-turn list), the attack's failed-reinforcer -3, and jealousy's petition docks at `/marshal_petition_response` — and a per-turn NET in `WorldState._check_trust_warnings` puts every player marshal at <= 20 to the checker at the turn boundary. The slice-9 review round added the tactical failed-roll −3, the mid-march `cancel` −3 and the attack's own reply (covering vindication's in-pipeline writes) to the staged seams; **only a man who STANDS is asked** (a prisoner or a destroyed corps is refused at the checker, and a stale question releases its latch — `REDEMPTION_ASKS_THE_LIVING`); the `administrative_role` answer's frozen man is exempt from the attrition sweep (`world_state.ADMINISTRATIVE_EXEMPT_FROM_ATTRITION`); and a question staged with no response carrier is **re-raised on the end-turn response** (`REDEMPTION_RERAISED_AT_END_TURN`) — the client's once-per-turn `GET /pending_redemption` poll (PT-B1) is a backstop, not the road, because it drops under an open modal. The checker's own guards make every call idempotent; levers `REDEMPTION_AT_EVERY_TRUST_WRITE` / `REDEMPTION_NET_ACTIVE`. Godot frontend handles redemption_event in `_on_command_result`, `_on_objection_response`, `_on_interrupt_response`, and deferred through the end-turn dialog chain (`_on_enemy_phase_dismissed`, `_on_strategic_report_dismissed`, `_process_next_interrupt`).

**FA-S9-D2 (slice 14, ruling 4) — HE SERVES WHILE THE QUESTION STANDS.**
A marshal with a live redemption question keeps taking orders, and that is
the recorded design, not an oversight. Measured by the slice-9 review round:
Murat asked at trust 15 still fought and still marched. Option (a) — gating
his orders behind an honest refusal — was considered and DECLINED: the man is
demanding an audience, not mutinying, and a corps frozen on a question the
player has not yet seen is a worse failure than a fiction that reads loosely.
The window is now ordinary (slice 9 widened the moments a question stands),
so gating would idle a marshal for a whole turn on a modal the client
intercepts before it is even sent. **Do not "fix" this**: it is a decision
with a landing record, and the answer's consequences (autonomy, the desk, or
dismissal) are what change his standing.

**FA-S9-D1 / FA-71 (slice 14, ruling 3) — THE DESK IS NOT A ONE-WAY DOOR.**
The `administrative_role` answer freezes the man's corps, buys +1 military
action and says his troops await assignment. `recall <marshal>` is the verb
that keeps that promise: 1 ADMIN action point, the corps restored at
`recruitment.find_spawn_region` (the capital while held, else the richest
still-held homeland province), the bonus action handed back, and
`redemption_cooldown_until` gating how soon he may be asked again. The loop is
AP-neutral across the two pools — the freeze buys a military action, the
recall spends an administrative one — and he returns at the trust that broke
him, so the question re-fires. **The name rides `command["target"]`, never
`command["marshal"]`** (the `recruit_marshal` precedent): a man at the desk
has `strength = 0` and `location = None`, so he is absent from the
live-derived roster and from every marshal pre-gate, and carrying him as a
marshal made the whole command parse to `None`.

**The restore destination is the GATE's wording, not the row's.** FA-71's
`fix_shape` says "at `administrative_location`/capital" and that is the
measured hazard — the old province may be in enemy hands, and the debug arm's
`or 'Paris'` fallback would put 22,000 men inside it with no battle. The debug
cheat now DELEGATES to the verb, so the two cannot drift and the cheat
inherits the held-soil rule it never had.

**The three fields are serialized as of this slice, and that was a P2 of its
own.** `administrative`, `administrative_strength` and `administrative_location`
were ad-hoc attributes declared nowhere; one save deleted all three. Measured:
the slice-9 attrition exemption stopped covering the frozen man and the sweep
DESTROYED him; `get_admin_marshals()` returned 0 so the max-one-admin gate
re-opened and save-freeze-load-repeat was an **unbounded +1-military-action
farm**; and he counted as a field marshal again. A campaign saved before this
has the flag but not the men, and the verb refuses honestly rather than
restoring an empty corps and charging for it.

### Available Options

| Option | Troops | Marshal | Bonus | Availability |
|--------|--------|---------|-------|--------------|
| **Grant Autonomy** | Keep | 3 turns independent, uses AI | Trust +5 to +40 based on performance | Always |
| **Administrative Role** | Frozen (stored) | Sidelined, restorable in Phase 4 | +1 action/turn | If >=2 field marshals AND no existing admin |
| **Dismiss** | Transfer to ally <=3 regions OR disband | Gone forever | +10 authority | If >=2 field marshals |

### Key Rules

1. **Last Marshal Protection:** If only 1 field marshal remains, ONLY Grant Autonomy is available
2. **Admin Cap:** Maximum 1 marshal can be in administrative role at a time
3. **Admin Troops Frozen:** Troops stay with admin marshal (stored in `administrative_strength`)
4. **Dismiss Range Limit:** Troops only transfer to ally within 3 regions, otherwise disband
5. **5-Turn Cooldown:** After resolving a redemption event, the same marshal cannot trigger another for 5 turns (`redemption_cooldown_until = current_turn + 5`)

### Redemption Choices (from disobedience reference)

| Choice | Effect |
|--------|--------|
| Grant Autonomy | Marshal acts independently for 3 turns, then returns at trust 50 |
| Dismiss | Remove marshal, transfer troops to nearest ally |
| Demand Obedience | Marshal stays but has 80% disobey chance |

### State Fields (Marshal)

```python
marshal.redemption_pending = True       # Redemption event triggered, awaiting choice
marshal.redemption_cooldown_until = 12  # Turn when redemption can next fire
marshal.administrative = True           # In admin role
marshal.administrative_strength = 72000 # Stored troop count
marshal.administrative_location = "Belgium"  # Stored location
```

### State Fields (WorldState)

```python
world.bonus_actions = 1                 # From admin role transfer
world.calculate_max_actions()           # Returns 4 + bonus_actions
```

### Helper Methods (WorldState)

```python
world.get_field_marshals()              # French marshals not in admin
world.get_admin_marshals()              # French marshals in admin role
world.find_nearest_marshal_within_range(from_location, nation, max_distance)
```

---

## Terrain System (Phase 6.1)

**Status: Sessions 6.1.A + 6.1.B + 6.1.C COMPLETE. Phase 6.1 Terrain fully implemented.**

See `docs/TERRAIN_SPEC.md` for full spec. Implementation details:

### Terrain Types (6)

| Terrain | Defense | Movement | Supply | Cavalry Eff. | Charge Blocked |
|---------|---------|----------|--------|-------------|----------------|
| plains | 0% | 1.0x | 1.0x | 1.2x | No |
| forest | 10% | 1.3x | 0.8x | 0.5x | Yes |
| hills | 15% | 1.2x | 0.9x | 0.8x | No |
| mountains | 25% | 2.0x | 0.5x | 0.3x | Yes |
| urban | 20% | 1.0x | 1.2x | 0.5x | Yes |
| river_crossing | 15% | 1.5x | 1.0x | 0.6x | No |

### Architecture

- **Constants** (single source): `region.py` — `VALID_TERRAINS`, `TERRAIN_DEFENSE_BONUS`, `TERRAIN_MOVEMENT_COST`, `TERRAIN_SUPPLY_MODIFIER`, `TERRAIN_CAVALRY_EFFECTIVENESS`, `TERRAIN_CAVALRY_ATTRITION_BONUS`, `CHARGE_BLOCKED_TERRAIN`
- **Region model**: `terrain` field with validation, 4 computed properties (`defense_bonus`, `movement_cost`, `supply_modifier`, `cavalry_effectiveness`)
- **Combat**: `combat.py` reads `TERRAIN_DEFENSE_BONUS` for defender bonus, `TERRAIN_CAVALRY_EFFECTIVENESS` to scale recklessness attack bonus. Legacy terrain values ("open", "fortified", "mountain", "river") still work.
- **Executor**: All 5 `resolve_battle()` call sites in `executor.py` read terrain from defender's region. Charge blocking at two layers: popup suppression (with redirect to alternatives) + safety net fallthrough to normal attack.
- **Charge redirect**: When charge blocked by terrain at recklessness 3, executor scans for alternative enemies within cavalry range on allowed terrain. Offers redirect popup if found, falls through to normal attack if not. `cavalry_terrain_message` forwarded as separate field through `main.py`.
- **Auto-charge**: `world_state.py` auto-charge at recklessness 4+ reads terrain and blocks charge bonus on mountains/forest/urban (downgrades to normal attack, recklessness preserved).
- **REGIONS_DATA**: All 19 regions assigned terrain. Distribution: plains(6), hills(4), urban(4), forest(2), mountains(1), river_crossing(1). Note: "urban" counts regions with `terrain: "urban"` (Paris, Berlin, Vienna, Milan).
- **Serialization**: `terrain` field roundtrips through `to_dict()`/`from_dict()`. Missing terrain defaults to "plains" (backward compat).

### Weighted Pathfinding (6.1.C)

Two new methods on `WorldState` alongside existing BFS:

- **`find_weighted_path(start, end, avoid_regions=None)`** — Dijkstra using `TERRAIN_MOVEMENT_COST` as edge weight. Edge weight = destination region's cost. Returns start-inclusive path or None.
- **`get_weighted_distance(start, end)`** — Returns total weighted cost of optimal path. Returns `float('inf')` if unreachable.

**Which commands use which pathfinding:**

| Command | Pathfinding | Rationale |
|---------|------------|-----------|
| MOVE_TO | **Weighted (Dijkstra)** | Strategic marches should pick lower-attrition routes |
| PURSUE | BFS (hop count) | Chasing doesn't pick scenic routes |
| HOLD | **Weighted (Dijkstra)** | March to hold position avoids expensive terrain |
| SUPPORT | BFS | Following allies directly |
| AI retreat | **Weighted** | Retreat destination sort by weighted distance to capital |
| AI movement (P7, stagnation) | BFS | Single-hop adjacent comparisons |
| Scout range | BFS | Hop count is the right metric for range checks |

**Terrain display:** Scout output includes terrain name and defense bonus (e.g., "Terrain: Hills (+15% defense)"). `get_game_state_summary()` map_data includes `terrain` field for Godot frontend.

### Remaining (Phase 6.2+)

- Movement cost enforcement in executor (AP cost scaling by terrain — Phase 6.2 Economy)
- Supply modifier wiring (Phase 6.2 Economy)
- Cavalry attrition bonus in combat

### Known TODOs

- `backend/full_game.py` (dead code, 3 sites): `resolve_battle()` calls still use hardcoded `terrain="open"`. Marked with TODO comments — wire from region if file is revived.

---

## Action System Reference

### Action Types

| Action | Type | Cost | Description |
|--------|------|------|-------------|
| `attack` | Combat | 1 | Engage enemy forces |
| `defend` | Tactical | 1 | Smart defend - shifts to defensive stance or fortifies |
| `hold` | Tactical | 1 | **Alias for defend** - same mechanics, different flavor |
| `wait` | Free | 0 | **Free action** - marshal passes turn, no state change |
| `move` | Movement | 1 | Move to adjacent region |
| `retreat` | Movement | 1 | Withdraw from combat |
| `scout` | Intel | 1 | Gather intelligence |
| `recruit` | Economic | 1 Admin AP | Raise troops (uses admin AP, not CP). Cost: base 200/300/400 gold (infantry/cavalry/artillery, `world_state.py:90-92`) with capital ×0.75 / settling-stability ×1.5, **then (W6-11 E-CA-3, Europe-scoped) ×3 while the recruiting nation is at war (blessed; band 2–4) composed with ×(1 + over-limit overage ratio) above the ES-3 force limit** (`economy_executor._calculate_recruit_cost`; the AI pays the same price through the same helper and its admin pre-checks price through it too — GR5). Legacy fixture world unaffected (N1 — it boots at war). Morale dilution. |
| `reinforce` | Movement | 1 | Move to ally marshal |
| `fortify` | Tactical | 1 | Dig in for defense bonus |
| `unfortify` | Tactical | 1 | Abandon fortifications |
| `drill` | Training | 1 | Train troops for shock bonus |
| `stance_change` | Tactical | 0-2 | Change combat stance |
| `help` | Meta | 0 | Show help |
| `end_turn` | Meta | 0 | End current turn |

### Hold vs Wait vs Defend

| Action | Mechanics | Stance Change | Bonus | When to Use |
|--------|-----------|---------------|-------|-------------|
| **defend** | Smart routing | Yes (to defensive) | Defense + fortify | Want maximum defense |
| **hold** | Same as defend | Yes (to defensive) | Defense + fortify | Prefer "hold the line" wording |
| **wait** | None | No | None | Conserve actions, maintain position |

**Key Difference:** `hold` and `defend` change the marshal's stance and potentially fortify, costing actions. `wait` does nothing and costs nothing.

### Action Addition Policy

**DO NOT ADD NEW ACTIONS WITHOUT EXPLICIT APPROVAL.**

Actions must be coordinated across multiple files and systems:
- `parser.py` - Valid actions list
- `executor.py` - Execution handlers
- `llm_client.py` - Keyword detection
- `personality.py` - Disobedience triggers
- `disobedience.py` - Message templates and routing

Adding an action without updating all systems will cause silent failures, dead code, or runtime errors.

---

## Example Scenarios

### Scenario 1: Ney Ordered to Fortify

```
You: "Ney, fortify your position"

Ney (Aggressive, Trust 75):
"Dig trenches? You want me to dig trenches like a coward?!"
[MAJOR OBJECTION - Severity 0.55]

Suggested Alternative: Attack Wellington

Your Choices:
1. TRUST - Let Ney attack instead (+12 trust, -3 authority)
2. INSIST - Force Ney to fortify (-10 trust, +2 authority)
3. COMPROMISE - Ney defends (holds position but stays mobile) (+3 trust, -1 authority)
```

### Scenario 2: Davout Ordered to Attack Superior Force (2:1 odds)

```
You: "Davout, attack Wellington" (Wellington has 96k, Davout has 48k)

Davout (Cautious, Trust 85):
"The odds are not in our favor. May I suggest we dig in and fortify?"
[MAJOR OBJECTION - Severity 0.60]

Suggested Alternative: Fortify current position
```

### Scenario 3: Grouchy Given Clear Orders

```
You: "Grouchy, move to Belgium"

Grouchy (Literal, Trust 65):
[NO OBJECTION - Grouchy follows orders exactly]
```

---

## 8. Economy System

### Region Types (Phase 6.2.A)

Each region has a `region_type` field that determines its base income:

| Region Type | Income | Examples |
|-------------|--------|----------|
| `capital` | 300 | Paris, Berlin, Vienna |
| `major_city` | 200 | Lyon |
| `city` | 150 | Milan, Marseille, Saxony, Bohemia |
| `town` | 100 | Belgium, Rhineland, Bavaria, Normandy, Hanover, Dresden, Tyrol |
| `rural` | 50 | Netherlands, Waterloo, Brittany, Bordeaux |

**Constants (single source of truth in `region.py`):**
- `VALID_REGION_TYPES` — set of 5 valid type strings
- `REGION_TYPE_INCOME` — dict mapping region_type → income value

**Important:** `region_type` and `terrain` are independent axes. Terrain affects combat and movement. Region type affects income.

### Per-Nation Gold (Phase 6.2.A)

Gold is tracked per nation in `world_state.nation_gold` dict. Starting values have a SINGLE SOURCE in `backend/nation_config.py`: `DEFAULT_NATION_GOLD` for the legacy fixture world (France 800, Britain 1500, Prussia 800, Austria 600, Saxony 200) and `EUROPE_NATION_GOLD` for the shipped 1805 world (France 800; Russia 1500 post-retune), applied on the Europe path via `build_europe_nation_gold()`.

**Convenience property:** `world.gold` reads/writes `nation_gold[player_nation]`. All existing code referencing `world.gold` continues to work unchanged.

**Income calculation:** `calculate_turn_income(nation=None)` works for any nation. Defaults to player_nation. Uses `region.get_effective_income()` (applies stability + war damage modifiers). Income breakdown includes per-region stability, damage, and effective income details.

**Income application:** `apply_turn_income(nation=None)` wraps `process_income_phase()` which handles income - occupation - upkeep + admin bonus.

### Upkeep + Bankruptcy (Phase 6.2.B; ES-3 force limit July 9, 2026)

**Upkeep (Europe worlds — ES-3, blessed E3):** `(marshal.strength // 1000) * 8` per marshal, PLUS a super-linear over-limit surcharge on total nation strength above the force limit `60,000 + 2,500 × controlled regions` (`get_force_limit`, cached region index): the band up to 150% of the limit pays 1.5× (surcharge +4/1,000), above 150% pays 2.0× (surcharge +8/1,000) — marginal bands, not a cliff. `calculate_turn_upkeep` returns `total/base/surcharge/force_limit/total_strength/over_limit` with `total == base + surcharge` guaranteed (the ledger renders base and surcharge as separate lines that sum to Net — §3 invariant). **Legacy fixture world:** flat `* 5`, no limit (pinned substrate, N1).

**Mercy (E6):** bankruptcy halves base AND surcharge (both rates even → exact).

**Income phase:** `process_income_phase(nation)` = income - occupation - dotation_skim - rente_cost - upkeep + admin bonus (rente_cost = ES-7 second pass §0.6.8). Runs for ALL nations during turn resolution.

### Occupation Cost (ES-2, July 9, 2026)

**Europe worlds only (legacy fixture pays none — N1).** Every controlled province NOT in the nation's `nation_starting_regions` pays a per-turn occupation cost = stability-tier fraction × the region's BASE `income_value`: Hostile 0.50 / Unrest 0.35 / Settling 0.20 / Stable 0.10 — a permanent floor, conquered soil never pays zero. Constants `OCCUPATION_*_FRACTION` + `Region.get_occupation_fraction()` live in `region.py` next to the income modifier (same tier boundaries, single source). Computed inside `calculate_turn_income`'s existing per-region loop (GR8 — no extra scan) and returned as a separate signed `occupation` key — `income` stays GROSS everywhere, so the ledger renders an "Occupation" line that reconciles to Net (forced by the `NET_GOLD_COMPONENTS` guard in `test_economy_ledger_reconciliation.py`). Recapture-reset and marshal pacification are free (they ride the existing stability ramp); vassal soil is never lord-charged (`get_nation_regions` keys on controller). Mercy (E6): bankruptcy halves the occupation total. Zero new serialized fields. ES-7 estate (dotation) provinces are EXEMPT — his household administers them (amendment 4, named test).

### Estate Endowments / Dotations (ES-7 "The Cost of Success", July 9, 2026)

**Europe worlds only (N1).** A marshal who wins battles builds a reward **expectation** = `min(REP_STEP 40 × battles_won, CAP 300)` g/turn (derived — no new field). The player meets it by **endowing him with an estate in a conquered province** (`grant_dotation`, surfaced as "endow Ney with Swabia"): the province's **FULL effective income** is redirected to his household each turn (§0.6.7 amendment 1 — no skim constant exists) and he gains a province-derived title ("Duke of Swabia" — flavor only, GR6, derived at render time). Constants + helpers in `backend/game_logic/dotation.py`.

- **Grant** (1 admin AP + 200g investiture fee IN-executor, `economy_executor._execute_grant_dotation`): eligibility = player-held / non-capital / non-vassal (structural) / un-dotated / NON-HOMELAND (amendment 4). The fee creates the TITLE (first estate); adding land to an existing title is fee-free; a marshal stripped of ALL estates re-pays it (the title lapsed with the land). **ZERO trust on grant** — paying stops the bleed, never buys trust (named negative assertion).
- **Reconciliation** (`WorldState._process_dotation_state`, post-income pre-bankruptcy, idempotent per turn): prunes estates whose controller changed (cede/recapture/rebellion/vassal-grab — state-driven, no seam hooks; estate-lost notification), then `shortfall = expectation − satisfaction`; after a **4-turn grace window** (`expectation_grace_turn`, serialized; retuned from 2 on Aug 23, 2026 — `dotation.GRACE_TURNS` is the single source, read it rather than this sentence) erosion fires: `modify_trust(−min(3, ceil(shortfall/50)))` per turn. `modify_trust` ONLY — never `modify_relationship` (grep-guard test). Marshal removal frees his estates.
- **Ledger/UI:** signed `dotation_skim` Net component ("Dotations" line, forced by `NET_GOLD_COMPONENTS`); dispatch situation + "Unmet Marshals" roll-up; treasury report per-estate lines; both turn-end messages + Godot banner; marshal card Expectation/Estates/Shortfall + title + exact-command Endow hint (`marshal_overview._build_estates`); eroding objection tag (cosmetic).
- **AI (GR5):** `_pick_admin_action` rung (below urgent recruit) endows the most-shortfalling marshal (threshold 80) with the richest eligible province through the same executor; AI marshals erode identically.
- **Serialized:** `Marshal.dotation_regions` + `Marshal.expectation_grace_turn` only (save-compat: absent → `[]` / `-1`, no retroactive erosion). Tests: `test_economy_es7_dotation.py` (57) + `test_economy_e1_band.py` (the stacked band acceptance).

### The Rente + The Steward (ES-7 second pass §0.6.8, July 11, 2026)

**The reward portfolio — territory is one instrument, not the only one.** Satisfaction = estate income **+ rente face** (`get_satisfaction` = `get_estate_income` + `Marshal.pension`, captured marshals excluded, W6-7).

- **Rente** (`grant_pension` / `revoke_pension`, 1 admin AP each, no fee, mock keywords pension/rente/annuity — revoke verbs revoke/withdraw/rescind only): grant sets `pension = expectation − estate income` (REPLACE semantics — re-grant after new wins is the top-up). The treasury pays **`ceil(RENTE_PREMIUM 1.5 × face)`/turn** — computed in `calculate_turn_income` (`rente_cost` key, `get_nation_rente_bill`), subtracted in `process_income_phase`, rendered as the signed "Rentes" line (ledger `NET_GOLD_COMPONENTS`, dispatch, both turn-end messages, treasury report per-marshal, Godot banner). **No bankruptcy mercy** (deliberate — DESIGN_REFINEMENT ESP-4 owns the arrears/default beat). ZERO trust on grant. AI (GR5): the grant rung prefers land, falls back to the rente when no province is eligible and treasury ≥ max(400, 10× cost).
- **The Steward:** estate provinces gain/lose stability growth by their holder's administration — `Marshal.get_estate_stability_bonus()` (≥8 → +5/turn, ≤3 → −2, 4–7 byte-identical), applied in `process_stability_growth` via `dotation.get_estate_steward_map` (one marshal-count map per tick; never respected-occupied soil). This is why the portfolio is a genuine decision: land is the better rate AND appreciates (fastest under an able lord) but is lumpy, conquest-gated, and lootable; the rente is instant, precise, war-safe, revocable — premium-priced, static, titleless.
- **Foresight:** `estate_cession_warning` (player-controlled + player-marshal estates only) renders at every territory surface — settlement review (inline WARNING rows), guided offer labels, the bilateral terms-guidance wizard, bilateral confirm (annotated + summary), incoming settlement offers.
- **Legibility:** dispatch `expectation_rises` (serialized `Marshal.last_expectation_seen` reconciled at dispatch build) + grace-countdown/pension on Unmet Marshals + `rente_cost`; `DOTATION_EXPECTATION` notification on shortfall-OPEN; battle-report `expectation_note` on decisive player victories; erosion advice names the rente, and says "no conquered province remains to endow" when the eligible list is empty.
- **Dead-zone fix:** eligibility honors only LIVE claims (controller match / respected / **capture-choice pending** — the W6-8 question keeps its claim alive); grants eagerly strip dead foreign claims through the shared `log_estate_lost` path.
- **UI:** the Generals card `[Reward…]` bbcode link (meta_clicked) opens the **Marshal's Reward dialog** (`reward_dialog.gd`, layer 109) — estate buttons with income/coverage/investiture, the rente offer with face AND true cost, revoke; buttons issue the standard typed commands; the screen refreshes in place. Serialized: `Marshal.pension`, `Marshal.last_expectation_seen`. Tests: `test_estate_second_pass.py` (66).

### War-Coupling (EC-W pass 3, July 17, 2026)

**Europe worlds only (N1); all four mechanics BOOT-ZERO by construction; GR5-symmetric through the shared income/battle/settlement seams; zero new serialized fields.** Gate record: `docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md` §3 (user-delegated). Fixes the July-17 playtest defect (treasury +7,500% while the army fell −66% and Britain stood in Orleanais). Upkeep stays billed on live fielded strength (user steer: "salaries") — these are the missing expenses:

- **EC-W1 "Contributions of War":** a region whose controller is at war with a present enemy-nation marshal (`strength ≥ DISRUPTION_MIN_STRENGTH 1000`, not captured) yields NOTHING to its owner that turn — `WorldState.get_disrupted_regions()` (one marshal pass, GR8), consumed in `calculate_turn_income` as the signed `contributions` Net component ("Contributions" line). A disrupted ESTATE feeds nobody (`get_estate_income` applies the same rule → the marshal's satisfaction falls with his lands); ES-2 occupation + infrastructure still bill. The region bleeds `DISRUPTION_STABILITY_DRAIN 2`/turn instead of growing (`process_stability_growth`). Suspension only — occupier-side extraction is DESIGN_REFINEMENT EWC-D1. Boot case: Mack@Swabia disrupts Bavaria (the real Sept-1805 occupation; pinned solvent).
- **EC-W2 "The War Effort" → EB-1 "THE CHARGES OF EMPIRE" (Econ Balance gate, Aug 7 2026 — `docs/audits/ECON_BALANCE_GATE_2026_08_07.md`, authoritative):** the WE accrual model is unchanged (France +8/turn at war / −5 decay, the defender battle arm, R49 partial-peace guard), but the WE-only hoard tax was ABSORBED into ONE condition-priced rate: `calculate_state_charges` = `int(max(0, treasury − CHARGES_HOARD_FLOOR 2000) × rate // 2500)` where `rate = WE + crown 30 (always) + war establishment 50 (any war) + wars-go-ill 75 (side score < −20, read via `sum_stored_side_score`) + restless interior 75 (≥1 held province disrupted or stability ≤50) + grip falters 50 (imperial grip < 70)` — `get_state_charges_rate` returns the NAMED terms every surface renders (shown = applied). The signed Net component is **`state_charges`** ("Charges of Empire" line); the `war_effort` key is RETIRED everywhere. Why: the measured Aug-7 disease was that treasury runaway is a PEACETIME disease (Prussia +298/turn, Spain +1,010/turn linearly forever — the only brake switched off exactly when a nation did well) and condition-blind at war. Now the treasury is a CONDITIONAL fixed point: golden peace pays ~1.2%/turn above the floor (may grow rich — the user's carve-out), ordinary war plateaus ≈20k, collapse bleeds toward ≈11k. Boot byte-identical by construction (max boot treasury = the 2,000 floor). Companion components landed at the same gate: **`requisitions`** (+0.25 × base income per disrupted enemy province to the STRONGEST disruptor — EWC-D1 built, la guerre nourrit la guerre) and **`overseas`** (authored `overseas_income` on navies rows — Britain 500 / Spain 250 / Holland 150 / Portugal 150, France none by design — holder ×(1−CS closure) floor 0.4, ×0 blockaded, ×0.25 at war with the dominance holder; the Continental System's economic target; subsidy tier 4 = 500 above 15k treasury, cap 500).
- **EC-W3 "The Butcher's Bill":** every resolved non-bombardment battle charges each side `int(own_casualties × MATERIEL_RATE 0.05)` at once (50g/1,000 — below the 60g/1,000 war recruit price, hierarchy pinned). One-time flow OUTSIDE Net (plunder precedent) in `_post_combat_pipeline` step 13b + the auto-charge copy; surfaced as the "[Materiel]" battle-message line.
- **EC-W4 "Peace with Teeth":** AI settlement offers price the indemnity to the payer's purse — `min(base 500 + 50×war_age + |war_score|×40 + treasury×0.15, treasury×0.40)`; an empty chest degrades to white peace (`_settlement_offer_build_terms`, both directions). The player-ask baseline scales too: `max(300, court_balance×0.25)`, still capacity-capped (settlement_baseline).
- **EC-W5 fixes:** AI personality auto-plunder now pays the same rate as the player (single source, `world_state.PLUNDER_INCOME_MULTIPLIER` — **×1.75 at EC-W5, retuned to ×4 by IGR-E**); the treasury report's net includes infrastructure (was silently omitted). ⚠ **The parity was nominal until IGR-E**: the AI branch read a non-existent attribute and could never fire, so "the same as the player" was true of the constant and false of the behaviour.

Tests: `test_econ_war_coupling.py` (33) + re-blessed EC-W4 pins in `test_settlement_incoming_offers.py`.

**Bankruptcy:** `nation_bankruptcy_turns` tracks consecutive turns with negative gold. Turn 1-2: warnings + halved upkeep. Turn 3+: desertion (5% strength loss per marshal).

**Admin AP:** 2/turn, recruit uses admin AP (not CP). Unused admin AP * 25 = gold bonus.

### Region Stability (Phase 6.2.C)

**Stability field:** `region.stability` (int, 0-100). Controls income via tiered modifier.

| Stability | Label | Income Modifier |
|-----------|-------|----------------|
| 0-25 | Hostile | 0% (no income) |
| 26-50 | Unrest | 25% |
| 51-75 | Settling | 75% |
| 76-100 | Stable | 100% |

**Boundary values fall into LOWER tier:** stability=25 → Hostile, stability=50 → Unrest, stability=75 → Settling.

**On capture:** Stability set to 25 (Hostile/Secured), then the player answers the Plunder/Secure
choice (see "Plunder/Secure Capture Choice" above — shipped Feb 2026; the stale TODO here was cleared
by IGR-E).

**On battle:** -10 stability per battle in the region.

**Growth per turn:** +5 base, +5 if friendly marshal present (garrison bonus). Capped at 100.

### War Damage (Phase 6.2.C)

**War damage field:** `region.war_damage` (float, 0.0-0.5). Reduces income multiplicatively.

**Sources:**
- Normal battle (<50k combined pre-battle troops): +0.10
- Major battle (50k+ combined): +0.20
- Stacks across multiple battles in same turn
- Capped at 0.50

**Recovery:** -0.02/turn natural recovery. 0.10 damage recovers in 5 turns.

**Combined income formula:**
```python
effective_income = int(income_value * stability_modifier * (1.0 - war_damage))
```

Example: Paris (300 base), Unrest (50 stability = 0.25 mod), 0.10 damage → `int(300 * 0.25 * 0.90)` = 67 gold.

### Turn Resolution Order

```
1. Clear per-turn flags
2. Process tactical states (fortify, drill)
3. Turn counter increment
4. Stability growth (all regions)     ← Phase 6.2.C
5. War damage recovery (all regions)  ← Phase 6.2.C
6. Bankruptcy desertion (all nations) ← Phase 6.2.B
7. Income phase (all nations)         ← Phase 6.2.A+B
8. Reset actions, cavalry limits, trust warnings, reckless cavalry
```

### Serialization

- `nation_gold` serialized as `{"France": 800, "Britain": 800, ...}` in `to_dict()`
- `gold` key still emitted for backward compatibility (player nation's gold)
- `from_dict()` prefers `nation_gold` key; falls back to old `gold` field for pre-6.2 saves
- `region_type` serialized on each Region; defaults to `"town"` if missing (backward compat)
- `stability` defaults to 100, `war_damage` defaults to 0.0 for backward compat

### Recruitment (Phase 6.2.D)

**Morale dilution:** Green conscripts have 40% base morale. Army morale becomes weighted average:
```python
RECRUIT_MORALE = 40
new_morale = int((old_strength * old_morale + 10000 * RECRUIT_MORALE) / (old_strength + 10000))
```

**Cost table:**

| Situation | Gold Cost | Condition |
|-----------|-----------|-----------|
| Capital region | 150 | `region.region_type == "capital"` |
| Settling region (stability 51-75) | 300 | 50% premium |
| Stable region (stability 76+) | 200 | Base cost |
| Hostile/Unrest (stability ≤ 50) | **Blocked** | Cannot recruit |

**Capital discount always wins:** If capital has stability 51-75 (unlikely), capital discount (150) takes priority over settling premium (300).

**Location resolution:**
- `"recruit for Ney"` → recruit at Ney's current location
- `"recruit at Lyon"` → recruit at Lyon, troops go to nearest marshal
- `"recruit"` (default) → recruit at capital (Paris), 150 gold

**Stability gate:** Recruitment blocked when `region.stability <= 50` (entire Unrest tier). Matches tier boundaries from 6.2.C.

**Controller check:** Recruitment location must be controlled by player's nation. Cannot recruit in enemy territory.

**Admin AP:** Uses admin AP pool (not CP). AP deduction handled by executor routing layer, not inside `_execute_recruit()`.

**Event fields:** `morale_before`, `morale_after`, `gold_cost`, `stability_premium`, `capital_discount`, `troops_added`, `new_strength`. All `int()`.

**Morale Warning (Session 31):** Recruitment result includes warning labels when post-recruit morale is dangerously low:
- `[WARNING]` when new morale < 40%: "consider drilling before battle"
- `[DANGER]` when new morale < 25%: "troops may break in combat"

**Unit-type lock (BY DESIGN):** Marshals always recruit their own unit type — `artillery=True` marshals recruit artillery, `cavalry=True` recruit cavalry, all others recruit infantry. Player cannot override this. Berthier returns a soft correction message if the player specifies a different type. This is intentional: marshal identity is tied to unit type (Drouot is *the* artillery marshal, Ney is *the* cavalry marshal). This is NOT a bug.

**Key code:** `economy_executor.py::_execute_recruit()`, `economy_executor.py::_calculate_recruit_cost()`

### Plunder/Secure Capture Choice (Phase 6.2.E)

When a **player** captures a region, a popup asks: **Plunder** or **Secure**?

| Choice | Stability | War Damage | Gold | Buildings | Plundered Flag |
|--------|-----------|------------|------|-----------|----------------|
| Plunder | 10 | +0.35 | **= base income × 4** | Destroyed | True |
| Secure | 25 | +0.00 | 0 | Damaged | False |

- **The rate is `world_state.PLUNDER_INCOME_MULTIPLIER = 4.0`** — the single source, read through
  `world_state.plunder_yield(region)` by the player payout, the AI branch AND the pre-choice preview
  (shown = applied). **IGR-E** (gate Q4, `INGAME_REVIEW_FIXES_SPEC.md` §5) retuned it from 1.75 and
  renamed it; **blessed and in-band tunable** (the band is "~3–5 turns of its income"), but changing the
  *shape* escalates — and per the recorded dissent, a second failed multiplier re-opens at option (b),
  the stability-vs-authority recut, rather than a third tuning.
- **The prompt quotes the figure before the choice** (`build_capture_choice` → `plunder_gold`, rendered
  on the modal button, the terminal sentence and both refusal restatements). Deliberately reads BASE
  income: a just-captured province sits at stability ≤ 25 where the stability modifier is 0.0, so an
  effective-income reading would pay 0 everywhere.
- **AI captures** auto-decide by personality: aggressive → plunder, all others → secure —
  via `world_state.ai_prefers_plunder` (GR5). Until IGR-E this branch was **dead code**: it read a
  `personality_type` attribute `Marshal` does not have, so the AI could never plunder. **Own-soil
  guard** (IGR-E post-landing review): an AI never sacks a province whose *starting controller* is
  its own nation — recapturing home soil always secures. The player's own-soil modal is untouched.
  Plunder's EFFECTS live in ONE place both sides call: `world_state.apply_plunder_effects`.
- `pending_capture_choice` blocks commands until resolved (same pattern as `pending_objection`)
- Plundered flag clears when stability recovers above 50
- Endpoint: `POST /capture_choice` with `{"choice": "plunder"}` or `{"choice": "secure"}`
- Key code: `executor.py::handle_capture_choice()`, `executor.py::_apply_plunder()`, `executor.py::_apply_secure()`

### Building System (Phase 6.2.E)

Four building types, constructed via `build <type> at <region>`:

| Building | Cost | Time | Effect |
|----------|------|------|--------|
| Supply Depot | 300g | 2 turns | +50 base income (before modifiers) |
| Fortification | 400g | 3 turns | +25% defense (stacks with terrain) |
| Training Ground | 250g | 2 turns | Recruit morale 55% (instead of 40%) |
| Market | 350g | 2 turns | +25% base income multiplier (after depot, before stability/damage) |

**Building slots:** Capital: 2, Major City/City: 1, Town/Rural: 0

**Validation:** Region must be controlled, stability > 50, sufficient gold, available slots, no duplicate type, no existing construction.

**Construction timers** process during turn resolution (after tactical states, before turn counter advance).

**Battle damage:** Battles damage civilian buildings — markets, supply depots, training grounds (100% if 50k+ troops, 25% chance otherwise). **Fortifications are immune** to battle damage — they're built to withstand combat and provide contested capture holdout value (6.2.F). Plunder destroys all buildings (including forts). Secure damages all buildings (including forts). Construction cancelled on any capture.

**Repair:** `repair <region>` = 150 gold, -0.15 war damage. `repair <building> at <region>` = 150 gold, restores damaged building. Uses admin AP.

**Key code:** `region.py::BUILDING_TYPES`, `executor.py::_execute_build()`, `executor.py::_execute_repair()`, `world_state.py::process_construction_timers()`

### Supply Limits & Attrition (Phase 6.2.F)

**Supply Capacity:** Each region has a max troop capacity derived from region type + buildings + terrain.

| Region Type | Base Capacity |
|-------------|---------------|
| Capital | 50,000 |
| Major City | 40,000 |
| City | 40,000 | *(B2: was 30,000)*
| Town | 35,000 | *(B2: was 25,000)*
| Rural | 15,000 |

Supply depot adds +10,000 to base. Terrain modifier applied (mountains 0.5x, urban 1.2x, etc.). Capacity is a computed property — not serialized.

**Home Territory Supply Bonus + The Ally's Table (PC15-D2, Aug 15 2026):** Marshals in their own nation's territory — or on soil controlled by an `ALLIANCE`/`DEFENSIVE_ALLIANCE`/`VASSAL` host (`WorldState.ALLY_SUPPLY_STATES`) — get `HOME_SUPPLY_MULTIPLIER` (1.5×) effective supply capacity via the single seam `get_effective_supply_cap` (HC-4a's naval shore verdicts key off the same fed predicate). NON_AGGRESSION/OPEN_BORDERS hosts feed nobody: transit rights are not magazines (the Ansbach line). Defending home or allied ground is sustainable; invading is not; the supply-strain dispatch headline names the legal dispersal split with real numbers, and the AI's P6.5 dispersal rung reads the same effective cap (shown = applied both directions).

**Supply Attrition:** Runs during turn resolution (after stability/war damage recovery, before bankruptcy). Calculated per-marshal with individual effective capacity. When total troops in a region exceed a marshal's effective capacity, attrition is continuous: `min(0.03, excess_ratio * 0.015)` where `excess_ratio = (total_troops - capacity) / capacity`. This replaces the old tiered system (1%/3%/5%) with a smooth curve that caps at 3%.

**Movement Attrition:** Applied every time a marshal moves. Base rate 1% (retreat 0.5%). Large armies (>20k) get a size penalty: `min(0.02, (strength - 20000) / 500000)` capped at 2%. Total rate on plains: 1% (20k) to 3% (120k+). Terrain multiplier from destination (mountains 2.0x, etc.). Moving through enemy fortified region adds 4% harassment. Enemy garrison detachments add 2% harassment (stacks with fort for 6% total). Capital garrisons do NOT cause harassment. Cavalry 2-tile moves apply attrition for both tiles. Broken army flee to capital: no attrition (already shattered). **Friendly stable territory (own region, stability 76+): no march attrition** — good roads and supply lines eliminate march losses.

**Depot Forward Logistics (Phase 6.2.H):** Supply depots project a logistics benefit to adjacent regions. If the destination or any adjacent region has a friendly undamaged supply depot, movement attrition is halved (0.5x after terrain). Does NOT stack, does NOT affect retreat/harassment/supply attrition. This makes depots an offensive logistics tool: build a depot at the border before pushing into enemy territory.

**Capture Hint (Session 31):** After a player marshal moves, adjacent enemy regions that are undefended (no enemy marshals, no garrison >= 5k, no player-placed garrison) and have FULL or PARTIAL visibility get a `[HINT]` in the move result message. Also adds `capture_hints` list to result dict for Godot UI. Enemy marshals don't receive hints.

**Key code:** `region.py::SUPPLY_BY_TYPE`, `region.py::supply_capacity`, `world_state.py::process_supply_attrition()`, `executor.py::_calculate_movement_attrition()`, `executor.py::_has_depot_supply_bonus()`, `executor.py::_execute_move()` (capture hint block)

### Contested Capture (Phase 6.2.F)

When capturing a region with a **functional fortification** (undamaged), instant capture is blocked. Instead, the marshal starts an **occupation**:
- **Ungarrisoned fort:** 1 turn to capture
- **Garrisoned fort** (defenders beaten this turn): 2 turns to capture
- **Damaged fort:** Instant capture (no holdout)

During occupation:
- Marshal is **blocked** from most actions (only wait/retreat/end_turn/status)
- Occupation ticks at turn start in `_process_tactical_states()`
- If marshal **leaves** the region, occupation is abandoned
- If marshal is **forced to retreat**, occupation is cleared
- AI marshals with occupation in progress are **skipped** by enemy AI evaluator

On occupation completion, capture + plunder/secure choice fires normally.

**Key code:** `marshal.py::occupation_*` fields, `executor.py::_attempt_region_capture()`, `world_state.py::_process_tactical_states()` (occupation progression), `world_state.py::_apply_occupation_capture_effects()`

### Capital Garrison System

Capital regions have a standing garrison that must be defeated before the capital can be captured. This prevents instant capital snipes and makes capital defense meaningful.

**Setup:** All capital regions start with 15,000 garrison troops (`garrison_strength` field on Region). Garrison regenerates +2,000 per turn, capped at 15,000.

**Garrison Combat:** When a marshal moves into a capital with garrison >= 5,000, simplified garrison combat is triggered:
- **Garrison effective defense** = `garrison_strength × (1 + terrain_bonus) × (1 + fort_bonus)` where `fort_bonus = 0.25` if fortification building exists
- **Proportional damage exchange:** Attacker damage ratio capped at 0.35, garrison damage ratio capped at 0.50
- **Minimum losses enforced:** 2% attacker, 10% garrison — prevents stalemates
- **If garrison drops below 5,000:** Garrison destroyed, attacker moves in, capture proceeds normally
- **If garrison holds (>= 5,000):** Attacker stays in place, damage dealt but no capture

**Below threshold:** If garrison is between 0-4,999 when a marshal enters, it collapses immediately (set to 0) and normal capture proceeds.

**AI Integration:**
- **P-1:** AI marshals don't recklessly abandon capitals — garrison check added to retreat logic
- **P4.25:** AI evaluates garrison assault — handles both capital garrisons (>= 5k) and detachment garrisons (any size)
- **P4.5:** AI skips garrisoned regions (>= 5k or detachment) when looking for undefended captures

**Capital Proximity Alerts:** When enemy marshals are adjacent to the player's capital, a warning event is generated in tactical events.

**Key code:** `region.py::garrison_strength`, `executor.py::_resolve_garrison_combat()`, `world_state.py::_setup_initial_control()` (init), `world_state.py::advance_turn()` (regen), `enemy_ai.py::_find_garrison_attack()`, `turn_manager.py::_check_capital_proximity()`

### Player Garrison Command (Session 31)

Players and AI can detach 3,000 troops from a marshal to garrison a controlled region. Uses the same `garrison_strength` field as capital garrisons, distinguished by `garrison_detachment` boolean (renamed from `garrison_player_placed` in AI Garrison session).

**Mechanics:**
- **Cost:** 2 AP (real commitment — unified across player and AI)
- **Troops detached:** 3,000 from marshal
- **Minimum marshal strength:** 8,000 (player), 20,000 (AI — `AI_GARRISON_MIN_STRENGTH`)
- **Nation cap:** Maximum 3 garrisons per nation (`GARRISON_MAX_PER_NATION`), includes capital garrisons. Berthier warning on cap, no AP consumed.
- **Region requirements:** Controlled by marshal's nation, no existing garrison, no enemies present

**Differences from capital garrison:**
| Property | Capital Garrison | Detachment Garrison |
|----------|-----------------|---------------------|
| Regeneration | +2,000/turn (cap 15k) | None |
| Collapse threshold | < 5,000 auto-collapses | Fights to destruction (> 0) |
| `garrison_detachment` | `False` | `True` |

**Garrison combat:** Both types use `_resolve_garrison_combat()`. Detachment garrisons fight until `garrison_strength <= 0`.

**Detachment harassment:** Enemy garrison detachments cause 2% attrition to armies moving through the region (including retreats). Capital garrisons do NOT harass — forts already cover that. Stacks with fort harassment (4% + 2% = 6%). This gives detachments passive area-denial value beyond just blocking capture.

**AI garrison placement (P6.75):** AI uses same `_execute_garrison()` (Building Blocks). Heuristic: garrison border regions with excess strength. Max 1 per nation per turn. See `docs/ENEMY_AI_REFERENCE.md` for full conditions.

**P4.25 garrison awareness:** AI evaluates ALL garrisons for attack — capital garrisons >= 5k AND detachment garrisons of any size. P4.5 (undefended capture) skips detachment garrisons, deferring them to P4.25.

**Serialization:** `garrison_detachment` in `region.py` `to_dict()`/`from_dict()`. Backward compat: `from_dict` accepts both `garrison_detachment` and old `garrison_player_placed` key.

**Key code:** `executor.py::_execute_garrison()`, `region.py::garrison_detachment`, `world_state.py::advance_turn()` (regen exclusion), `enemy_ai.py::_consider_garrison()` (P6.75), `enemy_ai.py::_find_garrison_attack()` (P4.25)

### AI Admin Phase (Phase 6.2.G)

AI nations get an admin phase each turn, using the same executor as the player (Building Blocks principle).

**Admin AP:** 2 per turn (hardcoded, not serialized — computed fresh each turn).

**Priority order** (evaluated top-to-bottom, first valid action wins each AP):

| Priority | Action | Condition |
|----------|--------|-----------|
| 1 | Recruit | Any marshal below 40% strength |
| 2 | Build fortification | At border regions (adjacent to enemy) |
| 3 | Repair building | Any damaged building in controlled region |
| 4 | Repair war damage | Any region with war_damage > 0 |
| 5 | Save AP | No valid action — unused AP converts to +25 gold each |

**Implementation:**
- `enemy_ai.py::execute_admin_phase()` — main entry point (7 methods: main entry + 5 helpers + `_pick_admin_action`)
- `_acting_nation` field in command dict — lets executor check correct nation's control and treasury (not player's)
- Wired in `turn_manager.py` — runs after enemy military phase, before strategic orders

**Economy command:**
- `_execute_economy()` in `executor.py` — free action (0 AP), shows nation's financial summary
- Aliases: `economy`, `treasury`, `finances`
- Wired in parser, validation, mock parser

**Turn summary financial report:**
- `_execute_end_turn()` appends financial report showing income, occupation (when > 0), upkeep, net gold, and balance for the player's nation

**UI wiring:**
- Occupation fields (`occupation_region`, `occupation_turns_held`, `occupation_turns_required`) added to `tactical_state` dict in `main.py::_get_map_data()` for Godot marshal tooltip display

### AI Homeland Defense (P3.7)

When a nation has lost regions it originally controlled, the AI redirects the nearest available marshal to recapture. Evaluated between P3.5 (Fortification Opportunity) and P4 (Attack Opportunity). Tracks claimed targets in `_homeland_recapture_targets` to prevent multiple marshals converging on the same region. Uses `world.nation_starting_regions` to identify lost territory.

**Key code:** `enemy_ai.py::_find_homeland_recapture()`, `world_state.py::nation_starting_regions`

### Session 11-12 Balance Changes

| Change | Detail | Code |
|--------|--------|------|
| **Victory threshold** | `VICTORY_REGION_FRACTION = 0.75` (was hardcoded 0.5). Both `world_state.py` and `turn_manager.py` use the constant. | `world_state.py` constant |
| **British naval income** | `150 + 50 * coastal_count` (max 300). Coastal: Netherlands, Normandy, Brittany, Bordeaux, Marseille. | `world_state.py` |
| **Admin AP gold rate** | 25g per unused admin AP (was 75g → 35g → 25g across sessions). | `world_state.py::_calculate_admin_bonus()` |
| **Futility decay** | Per-turn decay (was every-3-turn). AI retries targets faster. | `world_state.py::_process_futility_decay()` |
| **WE manpower penalty** | Infantry regen scaled by war exhaustion: halved at WE=100, zero at WE=200, floor 1000. Cavalry/artillery unaffected. | `world_state.py::_process_manpower_regen()` |
| **Stagnation variety** | `random.choice(fallback_dests)` replaces deterministic `[0]` selection. | `enemy_ai.py` |

---

## 9. Fog of War

> **Full spec:** `docs/FOG_OF_WAR_SPEC.md` (16 sections)
> **Implementation plan:** `docs/FOG_IMPLEMENTATION_PLAN.md` (Sessions 33-36)
> **Status:** COMPLETE (Sessions 33-36, Feb 2026)

### Core Principle

**"Fog filters information, not mechanics."** Game mechanics (combat, pathfinding decisions, sally ratios) use real world data — the executor is deterministic (Golden Rule #6). Fog only filters what the player sees in messages and UI. The simulation is accurate; the player's view is filtered.

Exceptions where fog affects mechanics:
- **PURSUE pathfinding** uses last-known location from intel store
- **Cautious pathfinding** only avoids PARTIAL+ visible enemies

### Visibility Levels

| Level | Source | What You See |
|-------|--------|-------------|
| **FULL** | Own region w/ army (**ephemeral**), scouted (2 turns), post-battle (2 turns) | Names, exact strength, morale, stance, buildings |
| **PARTIAL** | Adjacent to army, watchtower, own region w/o army, transit | Names, strength band only |
| **STALE** | 3-4 turns since last update | Frozen snapshot, marked with age |
| **LAST_KNOWN** | 5+ turns since last update | Old snapshot, position likely wrong |
| **UNKNOWN** | Never scouted, no adjacency | Region exists, controller known, no military intel |

### Visibility Calculation (`calculate_visibility()`)

Runs at: game init, end of `_advance_turn_internal()`, after save load, **after each player move**.

Priority order (highest wins):
1. **Pre-pass:** Ephemeral marshal_present downgrade — regions FULL from marshal presence lose FULL when marshal leaves (falls back to scout/battle FULL if recent, otherwise drops to PARTIAL for main loop to handle)
2. **Step 0:** Marshal-present → FULL (any region with a friendly marshal)
3. **Step 1:** Own region → PARTIAL military + FULL economic
4. **Step 2:** Adjacent to friendly army → PARTIAL
5. **Step 3:** Adjacent to active watchtower in own region → PARTIAL
6. **Decay:** Regions not refreshed → age from `last_updated_turn`

### FULL Visibility: Ephemeral vs Persistent

- **Ephemeral FULL** (marshal_present): Only while your army stands in the region. When the marshal leaves, FULL is lost immediately. The region drops to whatever the next applicable source provides (PARTIAL from adjacency, own-territory, etc.).
- **Persistent FULL** (scout, battle): Lasts for 2 turns after the scout/battle. Both scout and battle set `last_scouted_turn`. If a marshal was present AND the region was scouted/battled, the persistent FULL survives the marshal leaving.

This makes scouting valuable — it's the only way to lock in detailed intel on a region you don't occupy.

### Decay Timeline

Same for FULL and PARTIAL, offset from `last_updated_turn`:
- Turns 0-2: Stays at current level (FRESH_TURNS = 2)
- Turns 3-4: Degrades to STALE (STALE_TURN_START = 3)
- Turns 5+: Degrades to LAST_KNOWN (LAST_KNOWN_TURN_START = 5)

### Strength Bands (PARTIAL/STALE)

| Band | Range |
|------|-------|
| No forces | 0 |
| Screening force | 1 – 4,999 |
| Small force | 5,000 – 14,999 |
| Substantial force | 15,000 – 39,999 |
| Large force | 40,000 – 69,999 |
| Massive force | 70,000+ |

Multiple enemies in same region: combined total → single aggregate band.

### Key Files

| File | Purpose |
|------|---------|
| `backend/models/intel.py` | RegionIntel class, visibility constants, strength bands |
| `backend/intel_report.py` | Berthier Intelligence Report (fog-filtered status) |
| `backend/models/world_state.py` | `calculate_visibility()`, `decay_intel()`, `get_region_intel()`, `get_last_known_location()`, `get_visible_enemies_in_region()`, `get_filtered_game_state_summary()` |
| `backend/commands/strategic.py` | PURSUE fog validation, cautious pathfinding `fog_aware`, contact interrupt discovery messages |
| `backend/commands/disobedience.py` | Davout PURSUE fog-aware objection |
| `backend/main.py` | `_filter_enemy_phase_by_visibility()`, `_filter_tactical_events_by_visibility()` |

### Intel Sources

Scouts, battles, transit, and adjacency update the intel store:
- **Scout:** `update_intel_from_scout()` → FULL on target region. Watchtower synergy: +1 turn freshness.
- **Battle:** `update_intel_from_battle()` → FULL on battle region. Wired at all 6 `resolve_battle` sites.
- **Transit:** `update_intel_from_transit()` → PARTIAL on regions an army passes through without stopping (cavalry 2-tile moves, strategic multi-step movement). Snapshots enemy names + strength band.
- **Adjacency/watchtower:** Refreshed each turn by `calculate_visibility()`.

### Display Filtering

All API responses go through `get_filtered_game_state_summary()` (replaced 29 call sites):
- Enemy marshals hidden at UNKNOWN
- Strength band only at PARTIAL/STALE
- Exact data at FULL
- Own region economic data always full

Enemy phase: `_filter_enemy_phase_by_visibility()` — battles involving player always shown, FULL actions shown, below-FULL suppressed.

Tactical events: `_filter_tactical_events_by_visibility()` — player events always shown, enemy events require PARTIAL+.

### Strategic Command Fog Interactions

- **PURSUE:** Reads target from intel store via `get_last_known_location()`. UNKNOWN → reject. STALE → pathfind to last known. Empty arrival → auto-cancel with intel age message.
- **SUPPORT:** Safety check uses `get_visible_enemies_in_region()`. Reports only visible enemies.
- **Cautious pathfinding:** `_get_enemy_occupied_regions(fog_aware=True)` for player marshals. Only avoids PARTIAL+ enemies.
- **HOLD sally:** Adjacent-only scan, no fog filter needed (adjacency guarantees PARTIAL).
- **Contact interrupt:** Discovery language for fogged regions ("Enemy forces discovered!"), standard for FULL.
- **Direct MOVE fog-awareness:** Destination enemy check is fog-filtered for player marshals. Below PARTIAL → walk in blind, discover enemies on arrival. FULL/PARTIAL → blocked with "use ATTACK" suggestion.
- **Destination blocked (all personalities):** When enemy holds the destination itself (not mid-path), all personality types halt instead of offering "go around". Literal halts. Aggressive auto-attacks at good odds or halts. Cautious halts. Interrupt type: `destination_blocked`.
- **Attack suggestion fog filter:** Out-of-range attack "Targets in range" and literal pursue popup only list PARTIAL+ visible enemies. Null-target auto-find uses `find_nearest_enemy(filter_fn=...)` for visibility check.

### Watchtower Building

| Property | Value |
|----------|-------|
| Cost | 250 gold, 2 turns |
| Effect | PARTIAL on all adjacent regions |
| Scout synergy | +1 turn FULL freshness |
| Damage | Major battle → damaged. Plunder → destroyed. Under construction + any damage → destroyed. |
| Repair | 150 gold, 2 turns |
| AI priority | P6.5 (after repair, before low-priority recruit) |

Dedicated field on Region (not a building slot). Every region type allowed.

### AI and Fog

**Superseded (Scale Readiness Phase 2.3, April 19, 2026):** enemy AI is no longer omniscient on scale-sensitive queries. The nation-perspective live-visibility seam is landed — enemy AI routes scale-sensitive contact queries through `_should_use_fog_aware_enemy_query()` and the fog-aware cached contacts in `_get_enemy_contacts()` (`enemy_ai.py:540-573`); player autonomous AI keeps the player-facing RegionIntel view. Direct `world.marshals` / `get_enemies_in_region()` reads survive only on non-scale-sensitive paths (war-gated — see §16). Auto-charge still ignores fog (spec §9.2 — reckless cavalry finds trouble). The old "revisit at 80+ regions" deferral is overtaken — the 126-province map shipped July 2, 2026.

### Objection System + Fog

**V1 (disobedience.py):** Davout PURSUE objection is fog-aware (FULL: exact odds, PARTIAL: band comparison, STALE/UNKNOWN: staleness objection).

**V2a (objection_v2.py) — fog-migrated in V2b Session 2:** All objection helpers now use fog-filtered data. Key behaviors:

- **Step 0 rule:** Own region always FULL visibility (friendly marshal present → sees everything). Enforced in `_get_region_visibility()`.
- **Type A scan queries** (`_check_enemy_adjacent`, `_get_friendly_to_enemy_ratio`, `_path_crosses_enemy`/`_path_has_enemies`): Only detect enemies at PARTIAL+ visibility. STALE/UNKNOWN enemies invisible. Zero visible enemies → ratio 999.0.
- **Type B target queries** (`_get_attack_odds_ratio`, `_check_attack_target_fortified`): FULL=exact data, PARTIAL=band midpoint strength, STALE/UNKNOWN=1.0 odds / no fort info.
- **Band midpoints:** At PARTIAL visibility, exact strength replaced by band midpoint (2500/10000/27500/55000/85000) for ratio calculations.
- **4 fog-specific triggers:**
  - Attack into UNKNOWN: cautious → STRONG, aggressive → no concern
  - Attack on STALE intel: cautious → MODERATE, aggressive → MILD
  - Scout-shows-weakness: handled by fog-filtered ratio (no visible enemies = "defending nothing")
  - PURSUE no intel: cautious → STRONG, aggressive → MILD
- **Auto-propagated functions** (`_get_enemy_to_friendly_ratio`, `_is_outnumbered_2to1`, `_is_actually_threatened`): Fog-aware via delegation — no code changes needed.

### Map Visualization (Godot)

Backend sends `visibility_status` per region in `get_filtered_game_state_summary()`. Godot renders fog:

| Visibility | Region Overlay | Marshal Icon | Region Tooltip |
|-----------|---------------|-------------|----------------|
| **FULL** | No overlay (bright) | Full icon + name | Full detail |
| **PARTIAL** | Slight dim (30% alpha) | Dimmed silhouette + "?" | Full detail + "Intel: Partial" |
| **STALE** | Medium grey (50% alpha) | Faded silhouette + "?" | Full detail + "Intel: Stale" |
| **LAST_KNOWN** | Dark grey (65% alpha) | Not shown | Minimal: name, controller, "Last known (outdated)" |
| **UNKNOWN** | Near-black (75% alpha) | Not shown | Minimal: name, controller, "No intelligence" |

**Shipped Europe map:** province fog rides the owner-fill shader palette instead — `_refresh_owner_fill_palette()` (map_renderer_base.gd) composites the `FOG_OVERLAYS` color into each province's palette slot, with the hue lerp scaled by `FOG_HUE_LERP_SCALE = 0.6` (Slice 7.5). The Region Overlay alpha column above describes the legacy circle map only.

Fogged enemies (PARTIAL/STALE) use `fogged_forces[]` from backend response. Tooltip shows name, nation, strength band, intel quality.

Key files: `map.gd` (`_draw_fogged_force_icons()`, `_draw_fogged_tooltip()`, `FOG_OVERLAYS` const).

---

## 10. Manpower Pools

Nation-level infantry/cavalry/artillery reserve pools that gate recruitment. Cavalry and artillery are precious and slow to rebuild.

### Core Concept

Marshal type (`cavalry: bool`, `artillery: bool`) auto-determines which pool is drawn from. No player choice needed — the strategic choice is *which marshal to reinforce*.

| Marshal type | Pool | Batch | Gold cost | Example |
|-------------|------|-------|-----------|---------|
| `artillery: True` | artillery | 3,000 | 400g base | Drouot |
| `cavalry: True` | cavalry | 5,000 | 300g base | Ney, Uxbridge |
| neither | infantry | 10,000 | 200g base | Davout, Wellington |

### Starting Pools

| Nation | Infantry | Cavalry | Artillery |
|--------|----------|---------|-----------|
| France | 80,000 | 15,000 | 10,000 |
| Britain | 50,000 | 8,000 | 5,000 |
| Prussia | 60,000 | 10,000 | 5,000 |

Legacy fixture values above. The shipped 1805 world seeds pools from `EUROPE_MANPOWER_POOLS` in `backend/nation_config.py` — all 20 nations, the same three pool types, sized so coalition majors can fund 1-2 rebuilt armies (not endless waves).

### Regen (per turn)

- Infantry: 2,500/turn base (no territory dependency; halved S8, scaled down by war exhaustion — deliberately flat, an anti-snowball rubber band per the July-9 EC-2 gate)
- Cavalry: 250/turn base + min(150 per plains region + 750 per stables building, 1,500 summed-bonus cap `CAVALRY_REGEN_BONUS_CAP`) (ES-1b, July 9, 2026 — France's 24 plains were +12,250/turn at the old rate 500)
- Artillery: 150/turn base + 80 per arsenal region (`region_type ∈ {city, major_city, capital}`), total hard-capped at 600 `ARTILLERY_REGEN_CAP` (ES-1a, July 9, 2026 — the old urban-terrain keying was dead code on the real map)
- Pool caps: 100,000 infantry, 30,000 cavalry, 20,000 artillery (NOT nation-size-scaled — cut at the July-9 gate)
- Damaged/under-construction stables don't contribute
- Eliminated nations (0 regions) get NO regen (DLF-11)

### Stables Building

| Property | Value |
|----------|-------|
| Gold cost | 300g |
| Build time | 2 turns |
| Allowed in | capital, major_city, city |
| Cavalry regen bonus | +750/turn |

### Cost Modifiers

Same `_calculate_recruit_cost(region, world, base_cost)` for both types:
- Capital: 75% of base (infantry 150g, cavalry 225g)
- Settling (stability 51-75): 150% of base (infantry 300g, cavalry 450g)
- Normal: base (infantry 200g, cavalry 300g)

### Error Messages (Berthier Voice)

All recruitment failures use Berthier's voice. Pool empty error includes regen rate and estimated turns.

### AI Awareness

- `_find_weakest_marshal_for_admin` skips marshals whose pool can't support a recruit
- `_pick_admin_action` uses correct gold cost per marshal type (400g artillery, 300g cavalry, 200g infantry)
- Priority 4.5: Build stables when cavalry pool < 60% cap and nation has cavalry marshals
- Artillery moved_this_turn gate in `_find_attack_opportunity` — AI won't attack with artillery that moved this turn

### HUD Display

Manpower pools are displayed permanently in the Godot status bar alongside Turn, Actions, Admin, and Gold.

- **Location:** StatusSection → ManpowerDisplay (HBoxContainer after GoldDisplay)
- **Format:** `Inf: 80,000  Cav: 15,000` with comma formatting
- **Colors:** Infantry green `(0.6, 0.8, 0.6)`, Cavalry reddish `(0.8, 0.5, 0.5)`
- **Low-pool warnings:** Color shifts to orange then red when pools drop below thresholds
  - Infantry: orange < 40k, red < 20k
  - Cavalry: orange < 10k, red < 5k
- **Data source:** `game_state.manpower_pools.infantry` / `.cavalry` (player nation only)
- **Update sites:** All 10 response handlers in `main.gd` (mirrors gold update pattern)

### Key Files

| File | What changed |
|------|-------------|
| `world_state.py` | Constants, `manpower_pools` field, `_process_manpower_regen()`, `get_cavalry_regen_rate()`, `get_artillery_regen_rate()`, serialization, `get_game_state_summary()` (manpower in API) |
| `region.py` | `"stables"` in `BUILDING_TYPES` |
| `economy_executor.py` | `_execute_recruit` (pool drawing, type-based costs, Berthier voice), `_calculate_recruit_cost(base_cost)`, `_extract_building_type` (stables), `_execute_economy` (manpower section) — live in `backend/commands/economy_executor.py` since the R13A split, not `executor.py` |
| `enemy_ai.py` | Pool/cost-aware recruit, `_should_build_stables()`, `_find_best_stables_region()`, Priority 4.5 |
| `main.py` | `manpower_pools` in `/test` endpoint response |
| `main.tscn` | ManpowerDisplay nodes (InfLabel, InfValue, CavLabel, CavValue) |
| `main.gd` | `_apply_manpower()`, `_update_manpower_display()`, 10 update sites |
| `llm_client.py` | Optional `requested_type` extraction for soft correction |
| `schemas.py` | `requested_type` field on ParseResult |


## 11. Campaign Log

Fog-filtered event log overlay (Phase 6.5). Player can browse all narrative events grouped by turn.

### Event Types (14)

| Category | Types |
|----------|-------|
| Combat | `battle`, `bombardment`, `retreat`, `marshal_broken`, `marshal_recovered` |
| Territory | `region_captured` |
| Economy | `recruitment`, `building_started`, `building_completed`, `building_damaged`, `bankruptcy`, `desertion` |
| Command | `objection`, `strategic_order` |

### Fog Filtering Rules

| Event type | Rule |
|-----------|------|
| Player-nation events | Always shown |
| `objection`, `strategic_order` | Always shown (player-generated) |
| `battle`, `bombardment` | Player marshal involved OR region FULL visibility |
| `retreat`, `marshal_broken`, `marshal_recovered` | Player marshal involved OR region PARTIAL+ |
| `region_captured` (enemy) | Region PARTIAL+ |
| `bankruptcy` | Always shown (public knowledge) |
| Economy events (enemy) | Region PARTIAL+ |
| `intel_updated`, `intel_decayed`, `target_not_found` | Never shown (not in whitelist) |

### One-Liner Format

All one-liners include nation tags on marshal names: `Ney (France)`, `Wellington (Britain)`.
Missing nation fields gracefully omit the tag.

| Type | Format |
|------|--------|
| battle | `Ney (France) attacked Wellington (Britain) at Waterloo — Ney victory (8,000 / 5,000 casualties)` |
| bombardment | `Drouot (France) bombarded Waterloo — 3,000 casualties` |
| retreat | `Wellington (Britain) retreated from Waterloo to Brussels` |
| marshal_broken | `Wellington (Britain) was broken at Waterloo` |
| marshal_recovered | `Wellington (Britain) recovered at Brussels` |
| region_captured | `Brussels captured by France (secure)` |
| recruitment | `Ney (France) recruited 5,000 infantry` |
| building_started | `Construction started: Stables in Paris` |
| building_completed | `Construction complete: Stables in Paris` |
| building_damaged | `Building damaged: Stables in Waterloo` |
| bankruptcy | `Britain treasury bankrupt — desertion imminent` |
| desertion | `Desertion: Wellington (Britain) lost 2,000 troops` |
| objection | `Ney objected to attack (overruled)` |
| strategic_order | `Ney ordered to move to Brussels` |

### Godot Overlay

- Toggle: L key via top bar. Close: Esc, click outside, or L again.
- CanvasLayer 50 (information screen layer, managed by top bar).
- Turn headers expand/collapse on click. Most recent turn expanded by default.
- Empty turns (0 events after fog filtering) hidden.
- Turn 0 displayed as "Turn 0 — Setup".
- Category-colored BBCode icons: combat (gold X), territory (green >), economy (warm $), command (lavender !).

### Key Files

| File | Purpose |
|------|---------|
| `backend/campaign_log.py` | Type whitelist, fog filter, category map, one-liner formatter |
| `backend/main.py` | `GET /campaign_log` endpoint (groups by turn, strips battle_report, int wrapping) |
| `godot-client/.../campaign_log.gd` | Overlay UI, expand/collapse, BBCode rendering |
| `godot-client/.../campaign_log.tscn` | Scene layout |
| `tests/test_campaign_log.py` | 57 tests (whitelist, fog, format, defaults, endpoint) |

## 12. Top Bar & Screen Management

Unified top bar UI framework (Session A). Controller-based architecture: top bar owns buttons and state tracking, screens are independent CanvasLayers.

### Architecture

| Layer | Contents |
|-------|----------|
| Base | Map (Control node, no CanvasLayer) |
| 50 | Information screens (Event Log, Ledger, Generals, Dispatch) |
| 75 | Top bar + notification expanded detail panel |
| 100 | Modal dialogs (9 existing: objection, redemption, enemy_phase, etc.) |
| 101 | Pause menu |

### Behavior

- **One screen at a time.** Opening a new screen closes the current one.
- **Click active button = toggle off.**
- **All screens close on turn transition** (both manual and auto-advance paths, plus before enemy phase).
- **Terminal input stays active** while screens are open. Map interaction is blocked.

### Hotkeys

| Key | Action |
|-----|--------|
| L | Event Log (campaign log) |
| T | Ledger (strategic overview) |
| G | Generals (marshal management) |
| D | Diplomatic Ledger (4-tab diplomacy view) |
| R | Dispatch re-read |
| Esc | Close screen first, then pause menu |

### Input Blocking (3 levels)

| State | Map | Map hotkeys | Screen hotkeys | Terminal | Esc |
|-------|-----|-------------|----------------|----------|-----|
| Nothing open | Yes | Yes | Yes | Yes | Opens pause |
| Screen open | Blocked | Blocked | Yes (switches) | Yes | Closes screen |
| Modal open | Blocked | Blocked | Blocked | Blocked | Dialog handles |

### Dispatch Re-read

- Backend stores `last_morning_dispatch` on WorldState each turn (via `build_morning_dispatch()`)
- `GET /dispatch` endpoint returns stored dispatch
- Godot `dispatch_view.gd` renders BBCode (duplicated from main.gd — documented tech debt)
- Empty dispatch shows "No dispatch available yet."

### Dispatch Rewrite (W6-3, July 10 2026 — EXP-N1 "Berthier tells the story")

- **Headline (§5.1):** `dispatch["headline"]` = the turn's top fog-visible
  event as one prose sentence + ≤2 `sub_beats`, scored by
  `dispatch.HEADLINE_WEIGHTS` (home-captured 100 · marshal-captured 95 ·
  own-broken 90 · own-mauled ≥25% 85 · enemy-on-our-soil 80 · region-lost
  75 · war-touches-us 70 · ally-broken 60 · estate-eroding 55; everything
  else stays out). Display-only weights — tune freely. Absent on quiet turns.
- **Danger flags (§5.2):** every marshal row carries `danger` ("" if none):
  co-located enemy ≥1.5× own strength (fog-legal — the player's own intel
  entry, never omniscient reads), morale <40, fell back last phase, supply
  attrition 2 consecutive turns (supply events now mirror into the event
  log for history).
- **Arc memory (§5.3):** per-marshal chains derived at build time from the
  last-5-turn event-log window — `hunted_by` (same attacker 2+ consecutive
  turns), `consecutive_defeats`, `fled_across`; max 3 arc lines per
  dispatch, highest stakes first; the arc line replaces `status_note` and
  also rides `arc_note`. No new serialized state.
- **Cause lines (§5.4):** `vassal_loyalty` events carry `reason` (top
  same-sign contributors named at emission, e.g. "puppet resentment, war
  weariness") + a display `message` rendered in dispatch TURN EVENTS
  (warning severity when falling); the Berthier closing note answers the
  headline class when one exists; the intel report's NO INTELLIGENCE wall
  collapses to "No word from N provinces beyond the frontiers of …" (≤8
  frontier names = unknown regions adjacent to known ones).
- Tests: `test_w6_dispatch_rewrite.py`.

### Strategic Ledger (Session B)

- Backend: `build_strategic_ledger(world)` in `ledger.py` with 5 sections: forces, territories, economy, intel, manpower
- All values `int()` wrapped — no floats to Godot
- Forces: status priority chain (broken > retreating > drilling > fortified > strategic modes > idle), special flags, strategic order summary
- Territories: supply status (OK / Over capacity, no "Strained"), war_damage as `int(war_damage * 100)`, income via `get_effective_income()`, no `fortification_level` field
- Economy: treasury, income, occupation, upkeep, net, bankruptcy, construction queue, income breakdown
- Intel: fog-filtered enemy sightings, BAND_MIDPOINTS for estimated strength, nation summaries, unknown region count
- Manpower: `get_manpower_regen_rates(nation)` extracted as single source of truth (used by both `_process_manpower_regen()` and ledger), dynamic regen rates, `turns_until_full` calculation
- `GET /ledger` endpoint
- Godot: sub-tabbed screen (CanvasLayer 50), number keys 1-5 switch tabs, color coding for status/trust/morale/supply/bankruptcy/manpower

### Diplomatic Ledger (Session 8B)

- Backend: `build_diplomatic_ledger(world)` in `diplomatic_ledger.py` with 4 tabs: nations, treaties, balance_of_europe, talleyrand
- All values `int()` wrapped — no floats to Godot
- Nations: diplomatic state (WAR/ALLIANCE/NON_AGGRESSION/NEUTRAL/etc), relation value, fog-filtered army strength via nation-level visibility
- Treaties: nation pair, type, clauses, duration (int or "permanent"), cancel cost (always 1 DP)
- Threat & Coalition: threat level (0-100), tier (LOW/MODERATE/HIGH/CRITICAL), bar calculation (20 chars), brewing status, active coalition
- Talleyrand: trust label (Loyal/Cooperative/Wary/Distrustful/Treacherous), active mission, pending envoy count, DP remaining/max
- `GET /diplomatic_ledger` endpoint
- Godot: sub-tabbed screen (CanvasLayer 50), number keys 1-4 switch tabs, BBCode color coding for states/relations/threat

### Top Bar Diplomatic Fields (Session 8B)

- 4 new fields in top bar right section: DP counter, threat indicator, Talleyrand status, envoy indicator
- DP counter: always visible, format "DP: X/Y"
- Threat indicator: hidden at ≤29, amber 30-59, red 60+, pulsing when coalition brewing
- Talleyrand status: shows current mission summary or "Idle"
- Envoy indicator: hidden at 0, amber badge when >0, clickable (types advisory command)
- Fields update on every `/command` response via 6 fields: `diplomatic_points`, `max_diplomatic_points`, `threat_level`, `coalition_brewing`, `talleyrand_mission_summary`, `pending_envoy_count`

### Key Files

| File | Purpose |
|------|---------|
| `godot-client/.../top_bar.gd` | Controller: screen registration, toggle, close, button highlighting |
| `godot-client/.../top_bar.tscn` | CanvasLayer 75, bar layout with buttons + notification area + turn label |
| `godot-client/.../dispatch_view.gd` | Dispatch re-read screen (CanvasLayer 50) |
| `godot-client/.../dispatch_view.tscn` | Dispatch scene layout |
| `godot-client/.../strategic_ledger.gd` | Strategic ledger screen (CanvasLayer 50), 5 sub-tabs |
| `godot-client/.../strategic_ledger.tscn` | Ledger scene layout |
| `godot-client/.../diplomatic_ledger.gd` | Diplomatic ledger screen (CanvasLayer 50), 4 sub-tabs |
| `godot-client/.../diplomatic_ledger.tscn` | Diplomatic ledger scene layout |
| `backend/game_logic/dispatch.py` | Morning dispatch builder (also stores on WorldState) |
| `backend/game_logic/ledger.py` | Strategic ledger builder (5 sections) |
| `backend/game_logic/diplomatic_ledger.py` | Diplomatic ledger builder (4 tabs: nations, treaties, threat, talleyrand) |
| `backend/main.py` | `GET /dispatch`, `GET /ledger`, `GET /diplomatic_ledger` endpoints |
| `tests/test_dispatch_view.py` | 8 tests (storage, serialization, endpoint, no-float) |
| `tests/test_ledger.py` | 54 tests (all sections + cross-cutting) |
| `tests/test_session8b_ledger_ui.py` | 30 tests (diplomatic ledger data + top bar fields + hotkeys) |


## 13. Reinforcement System

Adjacent marshals automatically attempt to join ongoing battles before combat resolves. Both attacker and defender sides receive reinforcements independently (Building Blocks — AI uses identical code).

### Eligibility (13 Rules)

A marshal can reinforce if ALL of: same nation, adjacent region (not same region), strength > 0, not broken, not `retreated_this_turn`, `retreat_recovery == 0`, not fortified, not on HOLD (`holding_position`), not engaged (no enemies in their region), not drilling/drilling_locked, not `reinforced_this_turn`, not `moved_this_turn` (A-D2), not Hostile without SUPPORT (A-D4).

### Grouchy Rule (Personality Gate)

Literal-personality marshals are **blocked from reinforcing** unless they have a SUPPORT or PURSUE strategic order targeting a marshal who is **in the battle region** (A-D1 region-match). This is checked BEFORE arrival score — a blocked literal never rolls.

### Arrival Score Formula

```
score = base(50) + logistics*5 + relationship_mod + terrain_mod + personality_mod + support_bonus + variance
```

| Component | Values |
|-----------|--------|
| Base | 50 |
| Logistics | skill × 5 (range 5–50) |
| Relationship mod | -2→-20, -1→-10, 0→0, +1→+10, +2→+20 |
| Terrain penalty (departing) | plains: 0, forest: -10, hills: -5, mountains: -20, urban: 0, river_crossing: -5 |
| Personality mod | aggressive: +5, cautious: -5, literal: 0, balanced: 0, loyal: +3 |
| Support bonus | +10 if SUPPORT order targets primary combatant |
| Variance | random.randint(-8, 8) |

### Variable Threshold

| Condition | Threshold |
|-----------|-----------|
| Has SUPPORT or PURSUE order targeting participant | 60 |
| No relevant order | 65 |

### Fumble Roll (I3)

When score > 80: 5% failure chance (`random.randint(1, 20) == 1`). Prevents guaranteed success even with perfect stats.

### Trust Penalty

Failed reinforcement → -3 trust, UNLESS marshal personality is Literal. (Hostile marshals without SUPPORT are excluded at eligibility by Rule #13 and never enter the pipeline.)

### Physical Relocation & Ordering (A-C2)

On successful arrival:
1. Record `arrived_via_support` flag (if SUPPORT order active)
2. Relocate marshal to battle region (`marshal.location = battle_region`) — **except artillery** (Gate 4: artillery provides fire support from adjacent position, does NOT advance to front line)
3. Set `reinforced_this_turn = True` (all unit types, including artillery)
4. Clear path (but **NOT** strategic order yet)
5. Calculate coordination context (order still active for bonuses)
6. **THEN** clear strategic order (after coordination)
7. Artillery reinforcements explicitly added to casualty distribution participants despite not being in battle region

### Retreat on Loss

Reinforcers who relocated to the battle region return to their pre-arrival location if their side loses (spec: "reinforcer retreats with primary if battle lost"). Implemented via `reinforcer_origin` dict that tracks each reinforcer's location before relocation. After combat:
- If attacker lost: attacker-side reinforcers return to origin
- If defender lost: defender-side reinforcers return to origin
- Artillery never relocated in the first place (stays at origin regardless)
- Morale-based forced retreat (`<= 25`) runs first and takes priority

### Interaction with Coordination

- Arrived reinforcers (non-artillery) are **excluded** from adjacent ally count (`exclude_from_adjacent` parameter) because they relocated to battle region and are now same-region allies
- **Artillery exception (Gate 4):** artillery is NOT added to `arrived_names`/`exclude_from_adjacent` because it stays in its adjacent position — still counts as adjacent ally for +2% attack bonus
- Arrived non-artillery reinforcers **join** same-region coordination (counted as allies in battle region)
- Path B2: Reinforcers who arrived via SUPPORT count for `_has_dedicated_support()` check
- `reinforcement_results` passed through `_calculate_coordination_context()` → `_has_dedicated_support()`

### Serialization

`reinforced_this_turn` (bool, default False) is serialized on Marshal. Cleared at turn start in `world_state.py`.

### Key Files

| File | What changed |
|------|-------------|
| `executor.py` | `_is_reinforcement_eligible()`, `_calculate_arrival_score()`, `_calculate_reinforcements()`, wired into `_execute_attack()` |
| `marshal.py` | `reinforced_this_turn` field + serialization |
| `world_state.py` | Turn-start clearing of `reinforced_this_turn` |
| `objection_v2.py` | §6 SUPPORT objection triggers (aggressive→defensive, cautious→reckless) |
| `tests/test_reinforcement.py` | 49 tests across 12 classes |
| `tests/test_reinforcement_edge_cases.py` | 22 tests: rules 12-13, PURSUE region-match, Berthier advisory, SUPPORT objection triggers |

## 13b. Retreat Doctrine (W6-1, July 10 2026 — BUG-CA-2/E-CA-2)

`world_state.get_safe_retreat_destination` owns ALL retreat destination
selection (player-ordered, forced, and — via a GR5 mirror of its tier-5
rule — the enemy AI fallback in `enemy_ai._find_retreat_destination`).

**Priority tiers** (adjacent regions only): 1. friendly with ally cover ·
2. friendly/neutral empty · 3. foreign (NOT at-war) with ally · 4. foreign
(NOT at-war) empty · **5. at-war soil (desperation-only — chosen only vs
encirclement)** · None = encircled. Regions holding enemy marshals are
never candidates.

**Homeward bias inside each tier:** homeland (`nation_starting_regions`)
first, then lower `get_distance` to the nation's capital, THEN further
from the attacker, then ally strength. "Away from the attacker" no longer
dominates direction — this is what marched the audit's Bernadotte
17,000→316 across four at-war provinces.

**Explicit destinations** ("retreat to Rhineland",
`movement_executor._execute_retreat_action(target=...)`): honored when
adjacent + not enemy-held + not at-war soil; otherwise substituted with
the doctrine's choice and the message NAMES the substitution and the
reason. Never silently discarded. Tests: `test_w6_retreat_doctrine.py`.

## 13c. Marshal Fates (W6-7, July 10 2026 — EXP-M1)

Broken armies carry a person-shaped stake. At the single forced-retreat
seam (`combat_executor._apply_forced_retreat_or_break`, fate check FIRST):

- **Trigger:** post-battle strength < **5,000** (band 3k–8k), OR the only
  retreat is at-war desperation soil (W6-1 tier 5), OR pure encirclement.
- **Encirclement = captured outright.** Otherwise **escape 60% / captured
  40%** (combat RNG, seedable). An **aggressive player marshal** gets the
  last-stand `pending_interrupt` (carries `marshal`; options
  `fight_to_the_last` — one final defense at **+25%** that bleeds and
  HALTS the pursuer, survivors captured after — or `attempt_breakout`,
  the roll at −10%). **Aggressive AI marshals** decide deterministically:
  fight on homeland/capital-adjacent ground, else break out (GR5 — Mack
  is capturable by the player, pinned).
- **Captured state:** serialized `captured_by`/`captured_turn`; held at
  the captor's capital at strength 0 (attrition elimination guards
  prisoners); half the remaining men return to the owner's manpower pool
  by unit type; excluded from dispatch roster (`dispatch["prisoners"]`
  line), muster, reinforcement and AI scans; marshal card reads
  "PRISONER of X since Tn"; **ES-7 expectations freeze** while captured.
- **Release paths (§9.2):** clause `prisoner_return` (a treaty demand
  naming the marshal — armistices are the live mid-war ransom vehicle;
  AI values it at **500g** / **800g** for a major's marshal via the
  acceptance demand walk); and the `set_diplomatic_state` chokepoint
  auto-returns ALL mutual prisoners on any WAR/ARMISTICE → PEACE
  transition (bilateral treaties, settlements, armistice expiry alike).
  Released: own capital, **5,000** strength, morale 50.
- **Recorded cuts (spec §9.2):** no escape mechanic in pass 1; the AI
  accepts/values ransom clauses but does not initiate them; no new typed
  phrasing landed (ransom rides treaty demands + the peace auto-return),
  so no corpus row was needed — decide-in-session outcome recorded.
- Events: `marshal_captured` (headline weight 95) / `last_stand` /
  `marshal_released`, all through the full checklist.
  Tests: `test_w6_marshal_fates.py`.

## 14. Win/Loss Relationship Formula

After a shared battle with 2+ same-nation participants, each ordered pair (A, B) rolls independently to check if A's opinion of B changes. Fires after `resolve_battle()` in `_execute_attack()`, before destruction/retreat processing. Casualties are read from `battle_result["attacker"]["casualties"]` (nested dict — both normal and deferred paths). SUPPORT orders are preserved through relationship processing so Hostile+SUPPORT marshals are correctly detected as Participating.

### Trigger

- 2+ same-nation marshals in the battle region
- Both attacker and defender sides processed independently
- Hostile marshals without SUPPORT order targeting primary are Non-Participating (excluded)

### Battle Severity

Based on winner/loser casualty exchange ratio:

| Severity | Condition |
|----------|-----------|
| Decisive | `ratio < 0.5` (winner took less than half loser's casualties) |
| Standard | `0.5 <= ratio <= 0.8` |
| Narrow | `ratio > 0.8` (nearly even) |

Special case: `loser_casualties == 0` → always decisive.

### WIN Formula (base 30)

```
score = 30 + severity_bonus + relationship_modifier + variance
```

| Component | Values |
|-----------|--------|
| Severity bonus | decisive: +15, standard: 0, narrow: -10 |
| Relationship modifier | Hostile(-2): -20, Rival(-1): 0, Professional(0): 0, Friendly(+1): -10, Devoted(+2): -20 |
| Variance | random.randint(-10, 10) |

**Threshold:** `score > 50` → relationship improves +1.

### LOSS Formula (base 15)

```
score = 15 + severity_bonus + relationship_modifier + variance
```

| Component | Values |
|-----------|--------|
| Severity bonus | decisive: +10, standard: 0, narrow: -5 |
| Relationship modifier | Hostile(-2): +15, Rival(-1): +5, Professional(0): 0, Friendly(+1): 0, Devoted(+2): 0 |
| Variance | random.randint(-10, 10) |

**Threshold:** `score > 50` → relationship degrades -1.

### Intentional Asymmetry

| Scenario | Max Score | Outcome |
|----------|-----------|---------|
| Hostile WIN (decisive) | 30+15-20+10 = **35** | NEVER improves (M1) |
| Devoted WIN (decisive) | 30+15-20+10 = **35** | NEVER improves (M1) |
| Rival WIN (decisive) | 30+15+0+10 = **55** | ~24% chance improvement |
| Hostile LOSS (decisive) | 15+10+15+10 = **50** | NEVER degrades — strict >50 (M2) |
| Professional LOSS (decisive) | 15+10+0+10 = **35** | NEVER degrades |

### Ordered Pairs (D4)

Uses `itertools.permutations(participants, 2)`. 3 marshals = 6 calls. Each direction (A→B, B→A) is independent — different relationships, different cooldowns, may produce different results.

### Cooldown

3 turns per direction. Tracked in `marshal.last_relationship_change_turn[other_name]`. A→B cooldown does NOT block B→A.

### Range & Per-Battle Cap

- Relationship range: [-2, +2] (enforced by `modify_relationship()`)
- Per-battle cap: ±1 maximum change per pair per battle

### Key Files

| File | What changed |
|------|-------------|
| `backend/game_logic/relationship.py` | `calculate_battle_severity()`, `check_shared_battle_relationship()`, `get_battle_participants()`, `process_battle_relationships()` |
| `backend/commands/executor.py` | Wired into `_execute_attack()` after combat notifications; SUPPORT clearing deferred to after relationship processing |
| `tests/test_relationship_formula.py` | 34 tests across 9 classes |
| `tests/test_casualty_distribution.py` | 63 tests (includes W-1 timing + conformance tests) |

## 15. Phase 7 UI Integration (Session 66)

### Coordination Readiness Tooltip (map.gd)

Region tooltips show coordination readiness when 2+ player marshals are co-located:
- **Combined arms count:** Number of distinct unit types (infantry/cavalry/artillery)
- **Co-location pairs:** Per-pair status ("dedicated" if ≥2 turns, "X turns" if accumulating)

Marshal tooltips show color-coded relationship lines: Hostile (red), Rival (orange), Professional (white), Friendly (green), Devoted (gold).

### Inline-Dramatic Reinforcement Display (main.gd)

Gold-bordered BBCode blocks for reinforcement arrival (green) and failure (red). Zero new popup types per MULTI_MARSHAL_SPEC §14.

### First-Time Coordination Tutorial

Fires ONCE per campaign when player's marshals achieve combined arms (type_count >= 2) in attack. Tracked by `coordination_tutorial_shown: bool` on WorldState. Displays Berthier's report explaining combined arms bonuses, relationship-based coordination improvement, and proportional casualty sharing.

### Backend Data for Tooltips

`get_game_state_summary()` includes per-player-marshal:
- `relationships`: dict of marshal_name → {value: int, label: str}
- `co_location_turns`: dict of ally_name → int (turns co-located)

All values `int()`-wrapped for Godot safety.

### Key Files

| File | What changed |
|------|-------------|
| `backend/commands/executor.py` | Tutorial trigger after coordination context calculation |
| `backend/models/world_state.py` | `coordination_tutorial_shown` field + relationship/co-location in game state summary |
| `backend/main.py` | `reinforcement_messages` and `coordination_tutorial` passthrough |
| `godot-client/project-sovereign/scripts/main.gd` | `_display_reinforcement_messages()`, `_display_coordination_tutorial()` |
| `godot-client/project-sovereign/scenes/map.gd` | Relationship lines in marshal tooltip, coordination readiness in region tooltip |
| `godot-client/project-sovereign/scripts/enemy_phase_dialog.gd` | Reinforcement messages in enemy phase battles |
| `tests/test_session66_integration.py` | 32 tests across 7 classes |

---

## 16. Diplomacy Data Layer

Phase 8 Sessions 1A+1B foundation. Full spec in `docs/DIPLOMACY_SPEC.md`.

### Nations

Legacy fixture world: 5 nations (France player, Britain, Prussia, Austria, Saxony), 19 regions (expanded from 13). **The running game (July 2, 2026 cutover) is 20 nations / 126 provinces**, built via `create_europe_regions()` + `create_europe_diplomats()` — 15 additional diplomats beyond the named cast below, voiced through the chancery fallback until DEF-1 Roster Voices lands.

### Diplomatic States

Stored as alphabetically-sorted nation-pair keys in `world.diplomatic_states`:
- Key format: `"Austria|France"` (always sorted)
- States: `WAR`, `PEACE`, `NON_AGGRESSION`, `OPEN_BORDERS`, `DEFENSIVE_ALLIANCE`, `ALLIANCE`
- Default: `PEACE` (via `get_diplomatic_state()` fallback)

Starting states (§1e): France at WAR with Britain + Prussia. Austria at PEACE (hostile). Saxony at PEACE (French-leaning). Austria-Britain NON_AGGRESSION.

### War Gating (CRITICAL)

**`is_at_war()` must gate ALL enemy detection.** Only `WAR` state makes nations enemies.

- `get_enemies_in_region(region, nation)` — filters by `is_at_war()`. Used in 30+ locations (executor, strategic, objections, combat).
- `_find_nearest_enemy_for_nation(region, nation)` — skips non-war nations. Used for reckless cavalry.
- Enemy AI inline checks — all `m.nation != nation` patterns in `enemy_ai.py` include `world.is_at_war()`.

**Pattern for enemy detection:**
```python
# CORRECT — war-gated
enemies = [m for m in world.marshals.values()
           if m.location == region
           and m.nation != nation
           and m.strength > 0
           and world.is_at_war(nation, m.nation)]

# WRONG — treats all non-same nations as enemies
enemies = [m for m in world.marshals.values()
           if m.location == region
           and m.nation != nation
           and m.strength > 0]
```

### Nation Relations

`world.nation_relations` — numeric -100 to +100 sentiment per pair. Modified via `modify_nation_relation()`. Used by future diplomatic acceptance formula.

### Key Files

| File | Purpose |
|------|---------|
| `world_state.py` | `_make_diplo_key()`, `is_at_war()`, `get_diplomatic_state()`, `modify_nation_relation()`, `get_enemies_in_region()`, `_find_nearest_enemy_for_nation()` |
| `enemy_ai.py` | All inline enemy checks use `world.is_at_war()` |
| `region.py` | 19 legacy fixture regions (`REGIONS_DATA`), `NATION_CAPITALS`, `starting_controller`; the shipped 126-province world comes from `create_europe_regions()` |
| `marshal.py` | `create_enemy_marshals()` — 7 enemy marshals across 4 nations (legacy fixture; the 1805 campaign roster is scenario-authored) |
| `tests/test_session_1b.py` | 56 gate tests for Session 1B |
| `tests/test_diplomatic_war_gating.py` | 16 regression tests for war gating |

### Diplomats

| Nation | Name | Personality | Skill | Trust | Notes |
|--------|------|-------------|-------|-------|-------|
| France | Talleyrand | schemer | 10 | 55 | Player's diplomat. DP formula: `2 + skill//3 + authority//20 + capital_bonus`. |
| Britain | Castlereagh | hawk | 7 | 65 | Implacable. Views French advantage as threat to balance of power. |
| Prussia | Hardenberg | hawk | 6 | 65 | Demands respect, offers little. |
| Austria | Metternich | schemer | 9 | 55 | Spider diplomat, delays & leverages. |
| Saxony | Einsiedel | dove | 4 | 65 | Fears aggression, hopes for peace. |

---

## 17. Vassal System (Phase 8 Session 5)

Nations can become vassals via treaty (requires OPEN_BORDERS+) or conquest. Single source of truth: `backend/game_logic/vassal.py`.

### Autonomy Levels

| Level | Name | Drift/Turn | Tribute Rate | Marshal Control |
|-------|------|-----------|--------------|-----------------|
| 0 | Puppet | -4 | 100% | Lord controls (trust=40) |
| 1 | Satellite | -2 | 75% | Lord controls (trust=40) |
| 2 | Autonomous | +1 | 50% | Vassal keeps own marshals |

### Loyalty Formula (per turn)

Base drift (autonomy level) + **lord's garrison presence (flat +2 — VP-D1 wired July 16, 2026: a lord-nation corps standing in the vassal capital, or a lord-CONTROLLED capital with real `garrison_strength`, via single-source `lord_garrison_present`; never scales, full value in the VS-R spiral)** + gold investment clause (amount//100) + shared enemy (+2 per shared war) + lord winning battles (+1/win, max +3) + lord losing battles (-2/loss, max -6) + relation modifier (relation//20) + VS-R imperial-grip term (−2 when the lord's grip < 30). Clamped [0, 100].

### Rebellion

Loyalty = 0 triggers: diplomatic state → WAR, assimilated marshals return to vassal nation, all other vassals -10 loyalty (cascade), threat -10, relation -50.

### Defection Cascade

When lord's war_score < -30 AND vassal loyalty < 50: roll `random() < (50-loyalty)/100`. Fires AT MOST once per war pair (tracked in `cascade_triggered`). On success: loyalty is set to **0** (`LOYALTY_MIN`). *(Corrected by IQ-7, Sept 16, 2026 — this line said "-20 loyalty"; the code has always set the floor.)*

### Investment

1 DP + 200g → +10 loyalty. 3-turn cooldown per vassal.

### Autonomy Change

1 DP. Upgrade (more autonomy): +10 loyalty. Downgrade (less autonomy): -15 loyalty. Updates tribute rate.

### Continental System

Members lose trade income with Britain (-75g/turn cap per member, 200g/turn total cap). PUPPET/SATELLITE vassals auto-join if lord is a member.

### AP/Turn Treaty Clause

Requires war_score > 80. Reduces target nation's `nation_actions` by amount per turn (minimum 1).

### Enemy Vassal Courting

AI nations with 2+ DP can court player's vassals (loyalty < 50; the VS-R spiral widens the unlock and scales the bite ×1.5). Cost: 2 DP. Loyalty reduction: -15 (positive relation) or -5 (negative). 3-turn cooldown.

**The courting cap (WO-8, September 1, 2026).** Three guards, all behind `vassal.COURTING_TARGET_CAP_ACTIVE`: at most **one successful court per TARGET vassal per turn, world-wide** (first courtier in enemy-nation order wins; the rest skip ABOVE the DP debit, so they spend nothing and may try again next turn); **no self-courting**; and **no courting a fellow satellite of one's own lord** (compared lord-to-lord, not against the player, since a carved client or a defected satellite has a non-player lord). State is a `courted_turn` stamp on the vassal row — zero new serialized fields. Before it, all three throttles were keyed per-COURTIER, so on the 1805 board all nineteen enemy nations spent their first court on the same satellite in one tick, stripping it 47→0 and triggering rebellion — with Holland and KingdomOfItaly among the courtiers and Switzerland courting itself.

### Vassal Depth (July 16, 2026 — `VASSAL_DEEPENING_SPEC.md` §8 build record)

- **Land grants (VS-3):** `grant_region_to_vassal` — cede a conquered, non-capital, non-estate province adjoining the vassal (contiguity waived for landless vassals + homeland returns). Loyalty `min(25, 10 + income_value//200)`, NEVER spiral-blunted; 1 DP, 3-turn per-vassal cooldown; `granted_regions` provenance reclaims on a WAR-path rebellion/defection. F1-wizard province picker + typed "cede X to Y". GR5 lord-neutral.
- **Call-to-arms tiers (VS-4):** `vassal_military_contribution` — loyal ≥60 full; wavering 35–59 = assimilated ex-vassal marshals (`original_nation`) withheld from auto-reinforce/muster unless SUPPORT-ordered; disaffected <35 = refuses NEW war-cascade auto-joins (`vassal_refuses_call` family; never a mid-war exit).
- **Settlement vassalage (VS-5):** creation (`vassalage`/`subjugation`) + `liberation` are guided-surface live; NEW `vassal_transfer` clause `{from: from_lord, to: to_lord, vassal}` re-homes a satellite at the peace table via shared `transfer_vassal` (loyalty resets to 30, marshals re-key, granted_regions cleared, no release cooldown).
- **The Defection (VS-6):** `attempt_vassal_bribe` (AI diplomatic phase, post-courting, resolves immediately) — a nation at WAR with the lord bribes a satellite at loyalty <35 (or <50 in the lord's grip spiral). Outcomes: transfer to the briber (600g + WPS-B cap) or FREE + guaranteed WAR with the former lord (300g). Probabilistic, grip-scaled; per-pair 5-turn cooldown + per-vassal 1-turn latch.
- **AI shore-up (VP-D6):** enemy-AI admin rung P1.6 — a lord with a slipping satellite (loyalty <40 or grip <30) invests → cedes a province → grants autonomy, through the shared executor at player prices (nation_dp/nation_gold).

### Key Files

| File | Purpose |
|------|---------|
| `vassal.py` | Core engine: creation, loyalty (incl. garrison presence + grip term), rebellion (+VS-3 reclaim), cascade, tribute, investment, autonomy, land grants, transfer, defection bribe, assimilation, warnings, contribution tiers |
| `world_state.py` | Fields (vassals incl. nested granted_regions/grant_cooldown, cooldowns, cascade_triggered, continental_system_members), advance_turn steps 5-7, AP/turn clause |
| `diplomacy.py` | AP clause validation, Continental System application, war-cascade vassal auto-join + VS-4 refusal, wizard vassal actions (incl. Cede Territory) |
| `turn_manager.py` | Enemy vassal courting + VS-6 bribe phases |
| `enemy_ai.py` | P1.6 vassal shore-up rung (VP-D6) |
| `settlement_*.py` | Vassalage/subjugation/liberation clauses + VS-5 vassal_transfer lifecycle |
| `dispatch.py` | Vassal loyalty warnings (Trigger 3) + refusal/transfer/defection templates |

---

## 18. Talleyrand Defiance System (Phase 8 Session 6)

Talleyrand can secretly modify diplomatic proposals before delivery. Mirrors V2b combat defiance pattern. Single source: `backend/commands/diplomatic_defiance.py`.

### Defiance Probability (§3a)

Base 0.05 + authority modifier + trust modifier. Floor: 0.02 (SCHEMER personality). Cap: 0.30. Loyalist personality: always 0.0. Cooldown (>0): always 0.0.

| Authority | Modifier | Trust | Modifier |
|-----------|----------|-------|----------|
| >= 80 | -0.05 | >= 80 | -0.05 |
| >= 60 | 0.00 | >= 50 | 0.00 |
| >= 40 | +0.05 | >= 30 | +0.05 |
| < 40 | +0.15 | < 30 | +0.10 |

### Sabotage Types (§3b)

| Priority | Condition | Type | Effect |
|----------|-----------|------|--------|
| 1 | AP/turn demand | ap_downgrade | Converts to 200g/turn |
| 2 | Unit trade demand | unit_overpay | Doubles unit amount |
| 3 | 3+ territory demands | softened | Removes 1 territory region |
| 4 | Harshness > 0.7 | softened | Cuts gold 40% |
| 5 | Harshness < 0.3 | hardened | Adds/increases gold 30% |
| 6 | Default | stalled | Delivery delay +1 turn |

### Discovery (§3c)

40% base + 10% per turn hidden (cumulative). Checked during Morning Dispatch. On discovery: confrontation dialogue with Confront (trust -10, authority +5, cooldown 5) or Overlook (trust +3).

### Redemption (§3d)

Fires when trust <= 20 and not Loyalist. 3 choices: Apologize (trust +15, authority -5), Replace with Loyalist (personality→loyalist, skill→6, trust→50), Continue (authority -10).

### Pre-Proposal Objection (§3e)

V2a ConcernLevel pattern: NONE/MILD/MODERATE/STRONG. War declarations default to STRONG unless trust >= 70. Harshness 0.7+ with low trust → STRONG. Merged inline into dialogue flow.

### Override History (§10c)

Tracks last 5 overrides. Dispatch notes: "pessimistic" if good outcome, "prescient" if bad.

### Key Files

| File | Purpose |
|------|---------|
| `diplomatic_defiance.py` | Defiance probability, sabotage, discovery, confrontation, redemption, objection |
| `diplomatic_templates.py` | T21-T27 templates, enemy diplomat voice resolution |
| `diplomatic_dialogue.py` | Pre-proposal objection merge into dialogue flow |
| `dispatch.py` | Discovery check, override notes, redemption triggering |
| `world_state.py` | 3 fields (cooldown, sabotage, override_history), advance_turn processing |
| `notifications.py` | VASSAL_REBELLION, VASSAL_LOYALTY_CRITICAL types |
| `executor.py` | invest_vassal, change_autonomy, make_vassal commands |

---

## 17. Coalition System

**File:** `backend/game_logic/coalition.py` (Session 7). **Spec:** `docs/COALITION_SPEC.md` v1.1.

The coalition system creates the core Napoleonic puzzle: the better you play, the harder Europe pushes back.

### Threat Accumulation (§2a)

| Trigger | Amount | Source Key |
|---------|--------|------------|
| France wins battle | +3 | `battle_victory` |
| Decisive victory (ratio >2:1, casualties >10k) | +5 additional | `decisive_victory` |
| Capital captured by France | +15 | `capital_capture` |
| France declares war | +20 | `war_declaration` |
| Diplomatic downgrade | per DOWNGRADE_PENALTIES | `diplomatic_downgrade` |
| Treaty vassalization | +5 | `treaty_vassalization` |
| Conquest vassalization | +25 | `conquest_vassalization` |
| Treaty annexation | +8 per region | `treaty_annex` |

### Threat Decay (§2b)

Per turn: `-(1 base + peaceful_nations)`, capped at 3 (excluding France and vassals from peaceful count). Continental System members provide uncapped additional decay. Threshold checks use FINAL post-decay value (EC-15).

### Threat Reduction

| Trigger | Amount | Source Key |
|---------|--------|------------|
| Territory return (treaty) | -5 per region | `territory_return` |
| Vassal rebellion | -10 | `vassal_rebellion` |
| Voluntary vassal release | -8 | `voluntary_vassal_release` |
| Generous peace (sweeteners, no territory demands, war_score > 20) | -3 | `generous_peace` |

### Coalition Formation (§3)

| Threat Level | Effect |
|-------------|--------|
| < 60 | No coalition activity |
| ≥ 60 | Brewing starts (3-turn countdown) |
| ≥ 80 | Instant declaration (skip brewing) |
| ≥ 90 | Overrides 5-turn cooldown |

**Qualifying nations:** relation with France < -10, not a vassal, not already at WAR with France.

**Brewing cancellation:** Threat drops below 40 OR zero qualifying nations remain.

### Coalition Structure (§4)

- **Leader:** Highest score: `military_strength // 1000 + abs(relation_with_france) + authority`. Tiebreak: most marshals, then alphabetical.
- **Strategic posture:** Based on coalition war score (army-weighted average). Aggressive (war score > 30), cautious (war score < -10), defensive (default). Leader personality can override (aggressive leader → always aggressive if score > 0).
- **Coalition naming:** "First Coalition", "Second Coalition", etc. Based on `coalition_count`.

### Coalition AI (§5)

- **Convergence bias:** Coalition members' P7 movement scoring adds +12 (aggressive) / +4 (defensive) / +0 (cautious) toward regions adjacent to French territory.
- **Friction:** Cross-nation coalition coordination reduced by mutual relation: ≥30 → 1.0×, ≥0 → 0.75×, ≥-20 → 0.5×, else → 0.25×. Applied to adjacency bonus AND co-location bonus (N3 balance). Flanking unaffected.
- **Attack threshold:** Aggressive posture -0.15 threshold, cautious +0.15.
- **is_ally replacement:** `is_coalition_member()` replaces the TODO-1805 hack for cross-nation ally detection.
- **EC-9 member protection:** Coalition members cannot attack each other (executor block + AI target filter). Frozen bilateral conflicts resume on dissolution.

### Coalition Breaking (§6)

- **Loyalty penalty:** `min(-15 + war_exhaustion // 10, 0)` on acceptance formula. Halved via diplomatic wedge (non-WAR relation with any coalition member).
- **War exhaustion:** +casualties//1000 per battle (cap 20/battle), +5/turn at war, -5/turn at peace. Coalition shock: +5 to all other members on decisive defeat of one member.
- **Separate peace:** remove_coalition_member() handles leader transition (next-highest score), betrayal penalty (-10 relation with remaining members).

### Dissolution (§7)

Triggers: <2 active members, all members at peace with France, or threat < 20 with coalition active.

5-turn cooldown after dissolution. During cooldown, no new coalition can form (unless threat ≥ 90 overrides).

### EC-2: In-Transit Proposal Voiding

When a coalition forms, any in-transit proposal to a joining nation is voided. Talleyrand returns to IDLE (or ON_MISSION if a mission is active), and DP spent on the proposal is refunded.

### British Subsidy (§4e)

200g/turn to coalition member with lowest relation to Britain, if Britain gold > 500 and is a coalition member.

### War Exhaustion Per-Turn

| Condition | Change |
|-----------|--------|
| AI nation at war with France | +8/turn (R11; was +5) |
| AI nation at peace with France | -5/turn |
| **France at war with anyone (EC-W2, July 17, 2026)** | **+8/turn (same constants — GR5)** |
| France at full peace | -5/turn |

Battle WE: the LOSER of every France-involved battle accrues `casualties//1000`
(cap +20/battle) — EC-W2 added the missing "France loses as defender" arm.
WE's ECONOMIC consumer is `calculate_state_charges` (EB-1 "Charges of Empire",
Aug 7 2026 — WE rides as one named term inside the condition-priced rate; the
old WE-only `calculate_war_effort_cost` is retired, §8 War-Coupling).
Peace resets a nation's WE only when it has NO other active wars (R49).

### Key Files

| File | Purpose |
|------|---------|
| `coalition.py` | Coalition engine (all logic) |
| `world_state.py` | 7 fields, advance_turn hook, per-turn clearing, treaty wiring |
| `executor.py` | Threat after battles, war exhaustion, coalition shock |
| `diplomacy.py` | War declaration threat, downgrade threat, acceptance formula coalition penalty |
| `vassal.py` | Vassalization threat via add_threat() |
| `enemy_ai.py` | Coalition member detection, friction, convergence bias, posture threshold |
| `dispatch.py` | Coalition section in Morning Dispatch |
| `diplomatic_templates.py` | T28-T34 templates |
| `notifications.py` | 7 coalition notification types |

---

## 18. War Declaration Command

**Phase 4 (R10).** Player can declare war via natural language: "declare war on Prussia", "go to war with Austria", etc.

### Flow

1. Mock parser (`llm_client.py`): War keywords matched BEFORE marshal detection to prevent "war on Prussia" → military attack
2. `_parse_diplomatic_command()`: Routes to `action = "diplomatic_declare_war"`
3. Executor: `_execute_diplomatic_declare_war()` — 1 DP cost

### Keywords (trailing space prevents false matches)

`"declare war on"`, `"declare war against"`, `"go to war with"`, `"go to war against"`, `"war on "`, `"war against "`, `"open hostilities"`, `"declare hostilities"`

### Behavior

- 1 DP cost
- Validates target nation exists (via `get_known_nations(world)` — includes vassals)
- Validates not already at WAR
- Talleyrand STRONG objection if target is neutral and `world.threat_level > 50` → sets `world.diplomatic_objection_popup`
- Calls `declare_war(world, player_nation, target_nation, casus_belli=has_casus_belli)`
- Fires marshal trust reactions (see §20)
- Logs to `diplomatic_history`

### Casus Belli

If `casus_belli[diplo_key]` is True (set by rejected ultimatum), war declaration relation penalties are halved in `diplomacy.py:declare_war()`.

---

## 19. Ultimatum Command

**Phase 4 (R21).** Player issues ultimatums: "ultimatum to Britain", "final offer to Austria", etc.

### Keywords

`"ultimatum"`, `"submit or"`, `"final offer"`, `"accept or face war"`

### Behavior

- 2 DP cost
- Military threat bonus: +15 if any French marshal adjacent to target's marshal, else +10
- -10 relation regardless of outcome
- Talleyrand STRONG objection if `threat_level > 50`
- Acceptance roll via `calculate_acceptance()` with threat bonus
- On acceptance: sets diplomatic state to PEACE (if at war)
- On rejection: `world.casus_belli[diplo_key] = True` (halves future war declaration penalties)
- Logs to `diplomatic_history`

### Disambiguation from "demand"

"demand"/"insist"/"require" WITHOUT ultimatum context → `diplomatic_proposal` with `tone="demand"`. Only explicit ultimatum keywords trigger the ultimatum command.

---

## 20. Diplomatic Trust Reactions

**Phase 4 (R23).** Marshal trust changes in response to diplomatic events, varying by personality.

### Reaction Table

| Event | Aggressive | Cautious | Literal | Balanced |
|-------|-----------|----------|---------|----------|
| `war_declaration` | +3 | -3 | 0 | -1 |
| `treaty_signed` | -2 | +3 | +1 | +2 |
| `treaty_break` | +2 | -5 | -3 | -2 |
| `ultimatum_issued` | +3 | -2 | 0 | 0 |
| `vassal_created` | +2 | -1 | 0 | +1 |
| `alliance_formed` | -1 | +3 | +1 | +2 |

### Rules

- Per-turn cap: +/-5 total trust change from diplomatic events
- Applied via `_apply_diplomatic_trust_reactions()` in executor
- Uses string personality keys (not PersonalityType enum)
- Wired into: `_execute_diplomatic_declare_war()`, `_execute_diplomatic_break()`, `_execute_make_vassal()`

---

## 21. Diplomatic Reliability

**Memory and Pressure v2.4.3.** Long-term reputation tracking for treaty honoring, narrowed to the live nation-keyed shape.

### Scoring

- +5 per treaty honored for 10+ turns (legacy Phase 4 behavior; current v2.4.3 implementation narrows the gameplay impact rather than re-expanding the score surface)
- -10 per treaty break (applied in `break_treaty()`)
- Stored in `world.diplomatic_reliability` keyed by nation name

### Acceptance Formula Impact

- Component: `reliability_modifier` capped at `-6..+6`
- Formula: `max(-6, min(6, diplomatic_reliability[asker] // 10))`
- Added to `calculate_acceptance()` result

Legacy note: older docs and saves may still reference diplo-keyed reliability and the `±10` Phase 4 shape. Treat those as pre-v2.4.3 history, not the live contract.

---

## 22. Popup Priority Queue

**Phase 4 (R76).** Only the highest-priority popup is included per response cycle.

### Priority Order (highest → lowest)

1. `coalition_popup`
2. `diplomatic_sabotage_popup`
3. `vassal_rebellion_imminent_popup`
4. `talleyrand_redemption_popup`
5. `diplomatic_objection_popup`
6. `incoming_proposal_popup`
7. `commitment_paradox_popup` (legacy `alliance_paradox_popup` accepted on load)

### Implementation

`_include_popup_passthroughs()` in `main.py` iterates this priority list. Only the first non-None popup is added to the response dict with clear-after-read. Remaining popups stay on `world` for the next response cycle.

### Pass-through Coverage (R87/R88)

All early-return paths in `/command` and `/respond_to_objection` call `_include_popup_passthroughs()`:
- Tactical objection, strategic objection, clarification, glorious charge, strategic interrupt, capture choice (R87)
- Objection proceed/override/cancel responses (R88)

---

## 24. Map Renderer Architecture

### Scene Hierarchy

`map_renderer_base.gd` builds a SubViewport-isolated map world at runtime:

```
MapArea (Control, full-rect)
├── ViewportBackground (ColorRect, MAP_BACKGROUND_COLOR)
├── MapViewportContainer (SubViewportContainer, stretch=true)
│   └── MapViewport (SubViewport)
│       └── MapRoot (Node2D)
│           ├── MapCamera (Camera2D, enabled=true)
│           ├── WorldLayer (show_behind_parent)
│           ├── VisualMapLayer
│           ├── OwnerFillLayer (Slice 6 — political owner-fill fragment shader over the lookup bitmap; bitmap maps only)
│           ├── ProvinceHighlightLayer
│           ├── ConnectionLayer (MapConnectionLayer)
│           ├── RegionLayer
│           ├── ForceLayer
│           └── GarrisonLayer
├── MapLabelLayer (screen-space zoom-LOD name labels, `scenes/map_label_layer.gd` — bitmap maps only)
└── TooltipLayer (MapTooltipLayer, outside viewport — screen-space)
```

### Camera2D Zoom Convention

**Direct convention:** `_zoom_level` equals `camera.zoom` (higher = zoomed in).

```gdscript
map_camera.zoom = Vector2(_zoom_level, _zoom_level)
```

Key constants (post-Slice-7.5 / DEF-9): `min_zoom` is floored at the contain-fit ratio and recomputed on every resize; `max_zoom = 2.5`; `ZOOM_SPEED = 0.1`. `INITIAL_CAMERA_OVERSCAN` is deleted.

Initial zoom is the exact contain-fit ratio — boot shows the whole theater, no overscan.

### Coordinate Conversion

Screen-to-world uses Godot's `canvas_transform` for guaranteed accuracy:

```gdscript
func _screen_to_map_position(screen_position: Vector2) -> Vector2:
    var local_pos = screen_position - global_position
    return map_viewport.canvas_transform.affine_inverse() * local_pos
```

`SubViewportContainer` with `stretch=true` gives 1:1 screen-to-viewport mapping, so `global_position` subtraction handles any MapArea offset. The `canvas_transform` inverse encodes camera position and zoom — no manual formula needed.

### Zoom-at-Point

Preserves the world point under the cursor during zoom:

```gdscript
var map_point_before = _screen_to_map_position(point)
_set_camera_zoom_level(new_zoom)
var local_point = point - global_position
var viewport_center = size / 2.0
var target_position = map_point_before - (local_point - viewport_center) / new_zoom
map_camera.position = _clamp_camera_position(target_position)
```

### Input Routing

- `_input(event)` — keyboard pan keys (arrows), zoom keys (+/-/Home), focus release
- `_unhandled_input(event)` — mouse wheel zoom, click, drag pan
- `_process(delta)` — continuous arrow-key panning at `PAN_SPEED / _zoom_level`
- `_should_handle_map_pointer_event(event)` — guards mouse events to MapArea bounds
- Province hover uses `_lookup_region_from_color_map()` which samples `province_lookup_image`

### Key Files

| File | Role |
|------|------|
| `map_renderer_base.gd` | Base class: layers, camera, input, province lookup, hover/click, draw |
| `map.gd` | Post-Slice-7: the Europe game map, on the chain `map_renderer_base.gd` → `europe_map.gd` → `map.gd` — adds only game glue (backend `/map_topology` handoff, shared color scheme). Smoke logic lives in `europe_map_smoke.gd` |
| `map_connection_layer.gd` | Connection line drawing |
| `map_tooltip_layer.gd` | Screen-space tooltip rendering (outside SubViewport) |

---

## 25. Imperial Settlement — Slice H Ally Petition Constants (landed July 3, 2026)

Named per the approved D-H4 gate decision (`docs/SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md` v1.0). All live in `backend/game_logic/settlement_offers.py`; the dial-protection set lives in `settlement_baseline.py`.

| Constant | Value | Meaning |
|----------|-------|---------|
| `ALLY_PETITION_COOLDOWN_TURNS` | 5 | Per-(war, ally) absolute cooldown after ANY petition resolution (matches `REQUEST_TERMS_COOLDOWN_TURNS`) |
| `ALLY_PETITION_MAX_LIVE` | 2 | At most 2 live ally-petition dialogues, salience-ordered (bargain honor > restoration > reward; ties by material contribution share) |
| `ALLY_PETITION_DECLINE_RELATION_DELTA` | -3 | The D-H2 advisory-tier decline dip — the ratify-time shut-out / bargain-breach pipelines own the real teeth (never a double penalty) |
| `ALLY_PETITION_DECLINED_MEMORY_TURNS` | 10 | Expiry of the `petition_declined` settlement memory (the sold-out presentation window) |
| `ALLY_PETITION_GOLD_REWARD_AMOUNT` | 200 | Gold fallback for a reward petition when no region candidate survives validation (clamped to the payer's budget headroom) |
| `SETTLEMENT_DIAL_PROTECTED_AUTHORS` | `{"player", "ally_petition"}` | D-H1: clause provenances the dial sweep never silently drops — per-row Remove is the deliberate revocation verb |

---

## 26. Jealousy System (v3.2, landed July 11, 2026)

**Spec:** `docs/JEALOUSY_SPEC.md` (v3.1 body blessed; §0 build record authoritative). **Core:** `backend/game_logic/jealousy.py`. **Tests:** `test_jealousy_v32.py` (107).

"Jealousy makes marshals self-serving, not passive." Marshals accrue **glory** from battles (rolling 5-turn window: +1 win, +1 decisive/territory/outnumbered, 0 for garrison stomps; losses cost glory unless outnumbered — floor 0). Each marshal eyes the man **one rung above** on his nation's glory ladder; when the gap crosses his relationship-scaled threshold (Devoted immune / Friendly 4 / Professional 2 / Rival 1 / Hostile 1+idle≥2), a **grievance** fires (2/turn/nation cap, most-aggrieved first).

- **The temporary −1** toward the target is DERIVED in `Marshal.get_relationship` (never mutated/serialized) — it cascades through coordination scaling, SUPPORT objections, reinforcement eligibility/arrival, muster, enemy-AI ally picks, and self-restores on clear.
- **Expressions:** aggressive — autonomous glory-attack on the weakest adjacent enemy (warned one turn ahead in dispatch; ANY player order cancels the cycle; fires at end-turn top via `_strategic_execution`, no AP; +15% solo-attack buff; hard 0.0 pair coordination). Cautious — withholds (the derived −1 + worse-direction pair scale). Literal — the **Vindicated Garrison**: sidelined 3+ consecutive turns while peers act → obsessive patrols lift his sector's fog one step (PARTIAL→FULL) until reassigned or resolved.
- **Resolution** is battle-time (pipeline step 9.5, before Win/Loss relationships — EC-F): aggressive needs a win vs enemy ≥70% raw strength; cautious a shared victory with the target or a 3-participant win; literal any enemy contact (attack, unbroken defense, strategic-order battle). Passing the target on the ladder also resolves. Action resolutions grant a 1-turn **surge** (+10% attack/defense; literal keeps the intel one extra turn); timer expiry grants nothing.
- **Crowned with Glory:** the ladder's #1 (glory > 0, no tie) carries **+1 shock/defense/administration** — `get_effective_skill` + `get_admin_with_crown` (the crown can flip Intendance/Steward tiers; MC-1 Precision never leaks into admin). Announced in dispatch on transfer.
- **Authority polarity (amended):** >70 adds +1 to every threshold (winning calms, never anesthetizes); <30 collapses all thresholds to 1 and waives the hostile idle gate; capital-threatened suppresses outright. Enemy nations use the EC-M proxy (capital+majority home = 75 / broken = 25 / else 50).
- **Escalation:** a fire at Rival-or-worse (or the 3rd lifetime fire) advances the pair's level — 1: staff warning · 2: PERMANENT −1 both directions · 3: mutual spiral (the target auto-resents him back, forced targeting). Levels ride `jealousy_history["__levels__"]`.
- **The marshal-petition channel** (ONE pipeline: `world.pending_marshal_petition` + PopupQueue `marshal_petition` + POST `/marshal_petition_response` + `marshal_petition_dialog.tscn` layer 114) serves: §6 first-time confrontations (Acknowledge / Promise-Glory 1 AP −2 turns / Rebuke trust−5 −1 turn + personality rider), §6b rivalry confrontations on downward transitions (probability arms, authority-gated mediation, **Separate Them** flag + proximity warnings), ESP-1 Fontainebleau, ESP-2 war-weary.
- **Enemy jealousy** runs the same mechanical core with no UI (spec §9b); a jealous aggressive enemy takes the P3.9 glory-attack rung. Enemy literal intel enhancement is a documented no-op (fog is player-only).
- **Surfaces:** dispatch events (restlessness pre-warning at threshold−1, fired/target-notice/warning/resolved/ladder-shift/crown/separation), Berthier closing-note tier, campaign log (player-court only), battle-report `jealousy_note`, marshal card glory/grievance block, the Generals screen "THE LAURELS OF THE ARMY" ladder header.
- **ESP riders:** ESP-1 Fontainebleau (≥3 eroding → collective petition: concede rentes / refuse trust−8 / promise grace+3 authority−2; latched + 8-turn cooldown) · ESP-2 war-weary (fully-met expectation ≥160 petitions NEW player wars at the declare-war seam, once per pair) · ESP-4 rente default (negative treasury lapses the largest rente with a bounced-charge refund, GR5).

## 27. Marshal Recruitment — "The Marshalate" (landed July 11, 2026)

**Spec:** `docs/MARSHAL_RECRUITMENT_SPEC.md`. **Core:** `backend/game_logic/recruitment.py` + `economy_executor._execute_recruit_marshal`. **Tests:** `test_marshal_recruitment.py` (34).

Nations with an authored `marshal_pool` (France 6 / Austria 3 / Russia 3 / Prussia 3 / Britain 2) commission new marshals: authored gold price + 1 admin AP + a 5,000-man corps from the infantry pool; arrival at the capital (or richest held homeland province); symmetric relationship seeds; ladder entry at 0 glory, expectation 0. Typed verbs: `commission X` / `recruit marshal X` / `appoint X to the marshalate` (mock branch BEFORE troop-recruit, pension-guarded). AI rung P1.75 (at war + roster <3 + treasury ≥ cost+1000) through the same executor (GR5). UI: the Generals screen's Commission view (bench cards with █░ bars + honest availability). Word of enemy commissions is a fog-ruled dispatch event.

## 28. Nation Agendas — "The Designs of the Powers" (NA-0..NA-3 landed July 17, 2026; NA-5 + NA-6a/6b July 18, 2026; NA-6c/6d July 19, 2026)

**Spec:** `docs/NATION_AGENDAS_SPEC.md` (§0 gate record; §12/§13/§14/§16/§17/§20/§21 landing records authoritative, §21.1 = the post-landing audit). **Core:** `backend/game_logic/agendas.py` (derivation) + `backend/game_logic/formations.py` (NA-6 formation, creation, identity). **Tests:** `test_nation_agendas.py` (168) + `test_nation_agendas_ultimatums.py` (35) + `test_nation_agendas_formables.py` (225) + `test_na6d_audit.py` (23).

Nations carry authored historical **decks** (scenario `agendas` key: Austria `redeem_italy`/`primacy_germany`, Prussia `hanoverian_prize`/`armed_neutrality`, Britain `low_countries`/`paymaster`, Russia `arbiter_of_europe`, plus minors and the dormant KingdomOfItaly/Holland satellite decks); the ONE active agenda per nation is **derived each turn** (deck order = priority; first live predicate wins) through the cached chokepoint `get_active_agenda` (per-turn `_agenda_cache`, flushed by `invalidate_bloc_members_cache`). Five code-owned types: `acquire_regions`, `deny_regions` (hegemon-bloc-anchored), `contain_hegemon`, `paymaster`, `guard_neutrality`. Vassals never activate decks (dormancy — satellites wake on independence); the universal **survival override** ("The Knife at the Throat": capital or majority homeland lost) outranks every deck, even on deckless worlds. Serialized: `world.agendas` (deck store) + `world.nation_agenda_seen` (shift-beat dedup) — nothing else; every NA-2/NA-3 mechanic is derived.

- **Legibility (NA-1):** Nations-tab `agenda` row + stance line; war-room per-belligerent design lines + the rung-1.5 "Satisfy their design" executable counsel; `agenda_pursuit` motive register (5 registers + named overrides); the once-per-shift dispatch beat (`agenda_shift`, first observation silent).
- **Formable Dreams (NA-6):** two classes. **Class T (transform)** — a deck entry may carry a `forms` block; when it satisfies while the nation is FREE, the nation proclaims itself once and permanently (KingdomOfItaly→**Italy**, Holland→**United Netherlands**). The internal TAG never changes (save safety) — only the display identity, through two chokepoints (backend `formations.get_display_identity` + the `nation_display_overrides`/`nation_flag_overrides` response maps; Godot `Utils.display_nation_name`/`nation_flag_path` consult the override store first, flushing `_flag_path_cache`). **Class C (create)** — at a peace settlement the winning side carves a NEW client out of the DEFEATED party's soil via the `create_client` clause, keyed to a scenario `formable_nations` template (`formations.create_client_nation`: the only RUNTIME nation-minting path in the project — it appends to `world.enemy_nations`, seeds capital/gold/manpower/AP/authority/diplomat/deck/homeland, writes a vassal row under the carver at loyalty 30, flips controllers). Eligibility is ONE predicate: every template province held by the carver's bloc AND its registry `starting_controller` equal to the court being carved. Both classes fire **The Proclamation** (PopupQueue slot, CanvasLayer 117) — a creation emits it directly, because `process_formations` skips every vassal and a carved client is one from birth. §11.9 `aggrieved` lists cost each named court −30 with both the new state and its sponsor, then feed derived coalition-threat contributors sharing `AGENDA_GRUDGE_CAP` with the post-peace grudge. **Since NA-6d each formation emits under its OWN source key `formation_grudge:<tag>`** with an authored `grudge_label` ("The Polish Question", "The Roman Question") resolved by `diplomatic_ledger._threat_source_label` for both the Balance-of-Europe panel and the Talleyrand advisory; the bare `formation_grudge` key survives only as the fallback label for an unlabelled formation and for pre-NA-6d saves. The two families split one budget, and within the formation family the split is **floor-first fair share** (pass 1: 1 each; pass 2: top up toward the court count) rather than first-come-takes-all — greedy allocation made the naming unreachable, since `AGENDA_GRUDGE_CAP` is 2 and each authored formation aggrieves two courts, so the earliest one swallowed the whole remainder. **The C→T chain (NA-6d):** a CREATED client is not thereby formed — a carved Duchy of Warsaw that wins its independence still proclaims **Poland** through the ordinary Class T machinery, and its stored creation `sponsor` is who the aggrieved courts blame (Berlin blames Paris). Serialized: `world.nation_formations` (the once-only latch — records carry `template` from creation onward, preserved across a later formation, plus an explicit `formed: true` permanence marker; identity resolves DECK-entry-first, template second) + `world.formable_nations` (the catalogue — read at runtime, and the source carved capitals are re-derived from on load since `nation_capitals` is project-wide unserialized).
- **The Formables button (NA-6d §11.6-8):** `GET /formables` → `formations.build_formables_payload` → the F1 wizard's step-3 browser. One row per Class C template and per Class T watcher; rows are never hidden and **never dead** — an unavailable row must name at least one unmet gate term, and availability is the real settlement predicate (`evaluate_create_client_eligibility`) run over **active** war instances only (`_iter_active_war_instances`). Gate terms mirror every condition the predicate checks, including soil provenance and the total-annexation floor; `test_na6d_audit.py` pins payload-vs-predicate equality across a war-score sweep so the two surfaces cannot drift.
- **Diplomacy teeth (NA-2):** `agenda_acceptance_mod` ±12/−8 as a standalone acceptance term outside the composite floor (components/feedback/preview/snapshot labels — "Advances their design" / "Entrenches their denial"); covets unification (`get_agenda_covets` first source, profile fallback) through suggested terms + bargain interest + stage-4 commentary; hawk check-time −2 type-cooldown on design-advancing asks; the P1 **Pressburg arm** (`agenda_separate_peace_ready`: satisfied deck-head or survival → sue at war_score < −30 instead of −50); covets-scoped courting bias.
- **War coupling (NA-3):** `get_agenda_resolve_delta` on `effective_p1_threshold` (advancing −8 fights longer / satisfied or survival +10 sues sooner / irrelevant 0); enemy-AI target bias on **`get_agenda_military_targets` — acquire-type designs ONLY** (§3.1: deny is "never self-conquest") (P4 tiebreak + 2-hop distance credit, P7 target-choice credit, strategic-region agenda-first ordering — gates untouched, deckless byte-identical, call-sites spy-pinned); the **paymaster generalization** (`get_paymaster_nation`: any coalition member with a live authored paymaster POSTURE pays, treasury-tiered 200/300/400 cap 400; the war-attribution resolver takes the actual `supporter`; deckless legacy worlds keep the Britain literal); the **post-peace grudge** (`agenda_grudge` +1/turn per denied post-peace court, cap 2, threat-panel label "Denied national designs" — **derived per-nation from `participant_meta`**, so a separate-peace exiter grudges from its own exit while the coalition war burns on; dissolves when the targets come home); the **Ansbach trap** (`process_agenda_violations`: a belligerent's ≥1,000-man column in an ACTIVE guard region — never its own or a client's soil — → one-time −25 relation per pair per 10 turns with a rolled-log fail-safe, dispatch + campaign-log `agenda_violation`, GR5 both directions); the settlement scorer's 11th per-court component `agenda_settlement_mod` (±12/−8, "National design"); peace-class R17d previews scored on suggested terms (the +12 row reachable, one counting-pinned memo shared with the war-context snapshot).
- **Ultimatums (NA-5, spec §8/§16):** a hostile at-peace court with an active ACQUIRE design on player-DIRECT-held soil and a fielded army ≥1.25× the player's issues an **ultimatum** instead of a war it cannot declare (`ai_diplomacy._generate_agenda_ultimatum`, between P7 and P8; 15-turn per-nation cooldown set at ISSUE, max one live world-wide, bandwagon-throttle exempt). Terms via the player's own `generate_ultimatum_terms` (issuer/demand_regions params — the design target IS the demand; never the player's capital). Surface: dtype `incoming_ultimatum` on the mailbox transport (lapses end-of-turn; lapse ≠ rejection), the incoming-proposal popup's crimson ULTIMATUM register, **Yield/Defy**. Yield transfers demands player→issuer through the shared `_apply_ultimatum_demands` arms (beneficiary param; no player-threat add). Defy: no war (the coalition remains the war-maker) — `coalition.record_ultimatum_rejection` plants an expiring marker (`ultimatum_rejection_pressure`, 8 turns / +2 each / cap 4, "Defied an ultimatum") as the fifth standing threat contributor. Issuing never lowers the player's threat.
- **Consumption rule:** every consumer reads ONLY `get_active_agenda`/`get_agenda_covets`-family helpers — a latent deck entry prices nothing anywhere (the §5.9 latent-guard pin), and the sole exception is documented: the §5.7 paymaster is a POSTURE read independently of deck priority (Pitt's gold flowed while the Low Countries design stayed announced).

## 29. AI Intent Stage C — "The Bargaining Table" (AI-2/2b/2c/2d/2e + AI-4a steps 1-4, landed July 24, 2026)

Landing record: `docs/AI_INTENT_SPEC.md` §15. The peacetime diplomatic game — Europe talks, and France can answer — with zero new wars (Stage D owns the war decision).

- **The D5 counter-instruments (`backend/game_logic/instruments.py`, AI-2b):** three serialized world stores (§5 pin 8). **Directed sponsorship** — ONE record `{kind, payer, recipient, aim, amount_per_turn, started_turn, expiry_turn}` covering the paid form, the **licence** (`amount_per_turn: 0` — permission sold instead of gold, pin 23: the bond is identical) and **sell-neutrality** (`kind="neutrality"` — the opposite flow). Reneging is DIRECTIONAL: a sponsorship binds the payer (warring the recipient, or guaranteeing the aim); a neutrality compact binds the recipient (entering the war against the payer). **Compensation bargains** suspend the bought-off design at the `get_active_agenda` chokepoint (§3.1a b — the deck advances past it; the want sleeps, it does not die); renege (warring the bought-off court, or the payer's side retaking a granted province) wakes the design carrying `WEIGHT_RENEGED_BARGAIN` (+15) against the breaker. **Guarantees** deter coveters (−8 intent weight vs a guaranteed obstacle, shown = applied) and stake credibility: unhonoured within `GUARANTEE_GRACE_TURNS` (2) of the ward being attacked → the `guarantee_abandoned` grievance — the enforcement `protection_promised` never had. All renege marks ride the EXISTING directed grievance store (`betrayal_history`, `_betrayal_key` = unsorted `"{breaker}|{victim}"`); `grievance_modifier` prices them in acceptance (−30/flag) and Stage D adds the casus belli. Per-turn pass `process_instruments` in `advance_turn` beside the recurring-payments seam (GR8: iterates the three lists only).
- **Player verbs (1 DP each, in-executor):** `sponsor_design` ("sponsor Prussia against Austria, 200 gold"; licence verbs default the amount to 0), `buy_off_design` (price DERIVED and NAMED — `300 + 12×weight`, D4 no fog), `guarantee_nation`. Honest-availability refusals throughout (no design to sponsor / survival has no price / aim mismatch names the real design). Full 12-step wiring incl. 4 golden-corpus rows.
- **Beat 4 — The Broken Bargain (§4.6a):** a player renege delivers the cold envoy through `proposal_result_popup` (Voice Bible register, named diplomat) + HIGH notification + dispatch `broken_bargain`; an AI renege gets log + notification (the beat that lands hardest is the player's own doing).
- **Statecraft (AI-2c, §3.4):** `nation_config.NATION_STATECRAFT` (the honor-bias idiom: authored constants, `world.get_statecraft` chokepoint, neutral default) — Austria the patient revanchist (align-first, HARDENS under coercion −15), Prussia the hesitant opportunist (gold-first, FOLDS +10), Russia the distant arbiter (sponsor-first, honour −10, never haggles), Britain the paymaster (sponsor-first, the SUBSIDY WALL −40 **derived** from `hostile_army_on_home_soil` — pin 10: with an at-war army on British home provinces the wall drops and the ordinary path decides). Biases FOUR things only: ask ordering (`order_asks_by_statecraft`, always below the NA-2 design-front rule), the coercion delta at the player-ultimatum seam, the AI-AI haggle arm, and `weight_mod` (authored 0 on every 1805 court — boot-neutral by construction). Light profiles for six secondaries; `test_ai_intent_aliveness.py` is the homogeneity guard.
- **The intent-driven rungs (AI-2, §4.2):** P-Intent BEFORE P3 (the design outranks the threat-shelter ask), the AI-AI trigger 0 (design asks → the pin-8 refusal record; alignment pacts), the widened P-Bandwagon (any ≥50% hegemon, intent-driven, boot-dormant), the sponsor branch (Russia pays Austria from turn 1 — witnessed politics), and the §4.2c delivery budget (`INTENT_ASK_BUDGET_PER_TURN = 2`, its own lane beside the bandwagon cap; the opportunism valve bypasses the NATION cooldown when the obstacle fights two wars). Full rung table: `ENEMY_AI_REFERENCE.md` §Diplomatic proposal triggers.
- **The allegiance auction (AI-2d, §12.6):** serialized `allegiance_auctions`; a minor's `bandwagon` crest is ANNOUNCED (campaign log + dispatch + notification, always-visible — pin 11), biddable for 3 turns through the same D5 records, resolved by relations + patronage (10g/turn = 1 lean point); the player wins an OFFER, never an imposition; passed crests lapse (§3.1a — a reading, never a latch).
- **The paymaster duel (AI-2e, §3.7):** the subsidy is VISIBLE (campaign log `british_subsidy`, dispatch `paymaster_subsidy`, the Balance-of-Europe "THE PAYMASTER'S PURSE" block naming payer/client/amount/counterplay, per-nation "Compacts:" ledger lines for every live instrument) and CONTESTABLE — `get_british_subsidy_recipient` skips a member whose standing sponsorship from the coalition's target matches the subsidy (the outbid rides AI-2b's directed record) or who holds a live compensation bargain with it (a bought client is not worth funding).
- **AI-4a steps 1-4 (§4.4a):** `world.threat_by_target` + `threat_level` as a property over the player's slot (the `gold` idiom); `add_threat`/`reduce_threat` optional ACTOR target; source entries carry `target`. Byte-identical against the pre-migration baseline (the PYTHONHASHSEED-pinned 40-turn subprocess harness, `test_ai_intent_threat_migration.py`); steps 5-6 landed with Stage D (§30).

## 30. AI Intent Stage D — "War and Peace" (AI-3 + AI-3c + AI-4a steps 5-6 + §4.4b + AI-4b + AI-4c, landed July 24, 2026)

Landing record: `docs/AI_INTENT_SPEC.md` §17 (gate record §16 — the ⛩ re-check). The missing first link: an AI nation can now DECIDE to go to war — fore-warned, priced, courtable — and other people's wars hurt and END.

- **The War Council (`backend/game_logic/war_council.py`, AI-3):** the crisis lifecycle over ONE new serialized field `world.war_intents` — a court at intent `fight` with an acquire design, a climbed ladder (2 serialized refusals or a §3.3 renege grievance), and passing restraints (no existing wars, treasury ≥ 500, 1.25× the target + its guarantors, the `can_declare_war` preview, D1's world-wide cap of 2) opens a foregrounded crisis (beat 2, honestly-gated instruments), delivers the refused coercive demand (beat 3), and declares at 2 turns of foregrounded tenure — `declare_war` called at the ANNOUNCEMENT (§4.3a-1; the combat seam finds the war live). One foregrounded crisis world-wide; background crises climb silently. Every foregrounded crisis ENDS on screen (pin 21): the war, or beat 7 with its cause (satisfied/bought off/deterred/starved — a stalled predicate starves out after 4 polls). AI-vs-AI only in v1 (player-targeted designs: NA-5 coerce, coalition fight). War instances carry `ai_initiated`/`design_id`/`stated_reason`; the objective's `target_regions` are the DESIGN's provinces. AI producers on the crisis: the folds-statecraft holder buys off; one protector/turn guarantees; an AI guarantor JOINS at the declaration; France's pledge produces the ward's plea + the abandonment clock.
- **§4.3a at the combat seams:** refused declarations ABORT both attack paths (pin 15 — a refused declaration leaves the world byte-identical), and the `OPEN_MOVEMENT_STATES` capture hole is closed: an attack on a peace-nation's region always requires a successful declaration (AI) or the WPS staging (player). `exit_shared_wars_for_defection` (the VS-6 idiom lifted) unblocks the co-belligerent defection declaration for scripted use.
- **AI-3c (§13.1):** `get_intent_frontier` anchors P7 movement on the design's unmet provinces — corps mass on the border because `_can_ai_move_to` stalls them there (GR5: same rungs, new input); released the turn the crisis cools; deckless byte-identical.
- **AI-4a steps 5-6:** every threat producer passes its ACTOR as target (battle/capture/annex/liberation/forced-alliance/declaration/downgrade/breach/ultimatum/vassal families); the non-player `hegemony_passive` increment is wired (D3's fuel); per-nation region-control loops; the four standing contributors carry written STAYS-FRANCE-ONLY decisions in-code; per-target decay on the player's schedule; France's 40-turn series BYTE-IDENTICAL (verified in isolation AND with AI-4c live — `BASELINE_SERIES` unedited).
- **§4.4b (the exclusive ruling, gate §16.1-8):** one coalition world-wide; the eclipse pass brews (never instant — pin 16c) against a non-player power only when its bloc share exceeds France's and nothing else stands; the player is never enrolled; an eclipse coalition dissolves for France (`coalition_dissolved_for_france`) the turn France's alarm crosses brewing, cooldown zeroed. All coalition anchors take/read the target (`target_nation` key; legacy records default player byte-identically); `coalition_leadership_score`'s hostility anchor re-keyed to the target (the one semantics change).
- **AI-4c:** the exhaustion tick keys on `get_nations_at_war_with(nation)` on Europe worlds (legacy verbatim — pin 17c); both combat copies gained the explicit third-party loser-bears-its-dead arm; pin 17(a) both-belligerents-monotone green; boot deltas measured + blessed (§17). Ledger: the nations-tab `war_weariness` line ("National exhaustion across all wars… at war with …") + its `diplomatic_ledger.gd` render.
- **Third-party settlements (`backend/game_logic/settlement_third_party.py`, AI-4b):** the loser sues through `effective_peace_threshold` (P1's formula EXTRACTED to one seam — `ai_diplomacy.py`); the winner scores through `settlement_scoring.calculate_common_peace_acceptance` (the standing patch seam; hard stops veto; the victor's-consent arm accepts surrender-shaped terms and mutual-exhaustion white peace); terms via the accepter-general `_settlement_offer_build_terms` (the `player` param RENAMED) + up to 2 design-province cessions (a great power's capital never; a minor's may — D2); the headless ratify (plan → apply → transitions → treaties → invalidations → formations) never touches the dialogue manager (pin 19c). Beat 6 names consequences. The broker: a close-to-the-table court asks France (`broker_peace` incoming proposal); Accept convenes at the broker margin, +10 relations both courts on success. Campaign-log count 134 → 140.

## 31. The Wooden Wall — the naval abstraction (DEF-5, NV-0..NV-3, landed August 2, 2026)

Landing record: `docs/NAVAL_SPEC.md` §14 (the spec's §1–§13 are the design of record). NO naval map layer: a nation's navy is ONE record in the ONE serialized store `world.fleets` (ships / readiness 40–100 / posture guard|blockade + camp/diversion/window counters + the authored ports/dockyards/island/admiral/trade_dominance pass-throughs; ships-0 rows are ports-only closure weights; the `__naval__` dunder holds beat baselines). The sea exists through FOUR consequences (`backend/game_logic/naval.py`, all boot-zero on fleet-less worlds):

- **The crossing gate (§4.1):** `crossing_check(world, mover, from, to)` — one predicate at EVERY movement seam, both sides (GR5): player moves (before the enemy-presence check — fog never smuggles an army past the RN), cavalry 2-hop legs, ATTACKS (amphibious assaults refused: "a blockade that stops MOVE but not ATTACK is not a blockade"), reinforcement rule 2b, glorious-charge advance, general-attack steps, reckless-cavalry auto-moves, all 18 `_can_ai_move_to` candidate sites (origin-threaded — the AI never burns AP on a doomed order), forced retreats (covered crossings DEMOTED, with the Corunna clause: a cornered army takes to the boats). Coverage: a guard fleet covers links touching its own provinces; a blockade fleet covers links touching ANY at-war enemy's provinces (untargeted, v1.0.3). Pass ≥1.25× pooled effective (co-belligerent allies/vassals ×0.8 — H6), window floor 0.9×. Refusals name both numbers; strategic stalls break via the PF-8 `blocked_naval` arm; a notable AI turn-back logs `naval_turnback`.
- **The blockade (§4.2):** under blockade (an at-war blockade-mode enemy ≥1.25× your own effective; requires an authored navies row) — trade ×0.5 as the signed "Blockade" Net component (chokepoint stays GROSS, the EC-W1 pattern; applied at `process_trade_income`), readiness rots −5/turn to floor 50, build rate halves, island nations bleed +2 WE/turn. War fleets bill 2g/ship ("Admiralty" component; laid up free at peace). `trade_dominance` absorbs both Britain naval_income literals — income site ×(1−CS closure) floor 0.4 and suspended under blockade; power site STATIC.
- **The expedition (§4.3):** `naval_expedition` — ≤15,000 men, quote-then-confirm on the clarification channel (odds shown = applied; curve in §14: boot Ireland 12k = 64, Channel 15k = 12), embark from an owned yard (home) or any coast (the beachhead return), landings run the SAME `_attempt_region_capture` pipeline. Failure = turned back (small attrition, readiness −10) or intercepted at decisive coverage (corps −30% + a fleet action). **Free Ireland** rides it: hold Ulster+Munster at war with Britain → the `create_client` clause for the authored Ireland formable (dormant `erin_free` deck wakes on independence; "The Irish Question").
- **The fleet action (§4.4) & the Descent (§5.3):** `resolve_fleet_action` — two triggers only (failed expedition slip, failed diversion); loser 20%+15%×min(r−1,1), winner 8%/max(r,1), ±10% seeded jitter; ≥1.5× decisive = the `trafalgar` beat + loser WE +8; pooled allies bleed together. The Descent: ≥40k in authored camp provinces ticks `camp_turns` (staged at 2 = `boulogne_camp`); Britain's DERIVED reaction flips blockade→guard (the blockade lapses — two-front tension, §6); `naval_diversion` once per war, seeded 45% → `window_turns=2` (coverage halved, floor 0.9) or interception at bad readiness. Readiness economy (§3.3): blockading holds/climbs to 100; blockaded rots to 50; everyone else +5 toward the war drill ceiling 75 vs a superior hostile fleet (100 at peace / for the superior). Green crews: new hulls fold in at 40.
- **CS 2.0 (§5.1):** closure = Σ authored ports of (at-war-with-target + their puppet/satellite vassals + CS members) ÷ 26 continental ports; boot fact 10/26 = 38%; tiers ≥40/60/80% add +1/+2/+3 WE/turn to the trade_dominance holder; `cs_tier_shift` beat. The legacy −75g/member pinch stays (the members' sacrifice).
- **Surfaces (§9):** THE ADMIRALTY ledger block (fleet, Blockade board both directions, CS %, Crossings verdict lines, honest gate terms), map sea-link verdict tints + port anchor glyphs (`naval_overlay` on the game-state summary), region-panel "Lay down ships (400g)" chip on owned yards, war-room `naval_line`, 10 dispatch beats (state-change only). AI (§6): island fleets blockade at war (guard on a staged enemy camp/live window); everyone else guards; the P1.8 admin build rung lays keels through the same verb.

Verbs: `build_fleet` (1 admin AP + 400g, national rate 2/turn — 1 blockaded; conquest grants YARDS, never ships) · `set_fleet_posture` · `naval_expedition` · `naval_diversion`. Constants in `naval.py` = the spec's N-table, in-band tunable. Tests: `test_naval_substrate/blockade_cs/channel_gate/free_ireland/descent.py` (140).

**NUI "The Admiralty on the Map" (September 23, 2026; `NAVAL_SPEC.md` §17) — the
naval UI rules.** (1) **ONE crossing sentence:** `naval.crossing_line(world, a, b,
verdict, player)` is the only place a crossing's verdict is put into words — THE
ADMIRALTY's Crossings row, the map's sea-link tooltip and the region panel's THE SEA
block read it; never compose a second. (2) **The fleets are on the map payload:**
`naval.fleet_pieces` → `naval_overlay.fleets` (public counts, the §9 ruling) — a fleet
in commission stands at its SENIOR yard, `controlled_dockyards(...)[0]`, the yard the
"Lay down ships" chip names; no yard, no piece. (3) **The chip reads one summary:**
`naval.player_naval_summary` → `naval_overlay.player_summary` → `top_bar.update_admiralty`,
fed by `main._update_admiralty_chip` on every map refresh (and the boot bootstrap). (4)
**Three doors, one room:** a fleet piece, a hovered crossing (open water only — land
wins the hover), THE SEA's link and the chip all call `main._open_admiralty` →
`top_bar.open_ledger_to_tab(6)`; a naval surface is never a second screen. (5) **The
top bar fits the logical viewport** (`top_bar._fit_bar`, IQ10-X1): below 1,180 px the
nav goes icon-only with the hotkey letter as the no-icon fallback; a new bar control
must survive 800×450 — `tools/nui_top_bar_harness.gd` measures it. (6) A new naval
map/bar surface is DRIVEN before it is landed (`tools/nui_map_capture.gd`, the CN-3
harness), and every driven harness is named in `godot_parse_check.gd`'s TOOL_SCRIPTS.

## 32. The settlement offer on the desk (FA slice 10, landed September 5, 2026)

Landing record: the boxed SLICE 10 block in `docs/BUG_FIXES.md` §Final
Whole-Game Audit. Two rules and one repair, all in the settlement package.

**An incoming offer is MAIL, never a DRAFT.** `settlement_routes` publishes two
sets, and they are not the same question:

- `SETTLEMENT_FAMILY_DIALOGUE_TYPES` — everything in the settlement family,
  offer included. Used by the defensive guards that want to recognise any
  settlement surface.
- `settlement_draft_dialogue_types()` — the family MINUS
  `incoming_settlement_offer`. This is what SC-26 means by "a settlement is
  already on the table", and it is read at exactly three places, which must
  always agree: the collision arm in `_settlement_dialogue_active`, the
  mounted-draft reader `_mounted_settlement_dialogue`, and the staging
  tail's same-war replace arm in `settlement_staging`. Flip lever
  `OFFER_IS_MAIL_NEVER_A_DRAFT`.

  **`_mounted_settlement_dialogue` itself has THREE callers**, and narrowing
  it changed the verdict at all three: `stage_settlement_confirm` (the
  cross-war collision and the same-war refresh/scope-replace),
  `settlement_routes.evaluate_war_detail_actionability` (the war-detail
  recovery gate) and
  `settlement_validation.evaluate_pair_peace_substitute_eligibility` (the
  pair-substitute CTA). FA-N18's own filed fix shape warned against narrowing
  this helper and named the other two sites; the warning was CONSCIOUSLY
  OVERRULED, because a letter is not a mounted draft at those gates either.
  An AST census pins the caller count, so a fourth reads as a failure rather
  than a surprise.

A letter is a persistent soft-stop mailbox item the player may hold for turns.
It never blocks opening a settlement, on its own war or another. It follows
that **the two arms that answer an offer stage FIRST and consume the offer only
on success** — `pop()` PROMOTES the next queued item, and the promotion was
then read as a rival draft. Because the staging tail has re-queued the offer
behind the new review by the time it is consumed, removal goes through
`dialogue_manager.remove_matching` (`_consume_offer_dialogue`), not `pop`. A
refused accept leaves the letter standing and answerable, with `must_reopen`
False and no SC-14b reopen attempt spent.

**The offering courts consent by construction.** Accepting an AI offer stages a
review of terms THEY wrote, so their willingness is not re-litigated. The accept
stamps three display-and-scoring keys on the staged dialogue —
`consenting_courts`, `consent_terms`, `consent_offer_id` — and they are
honoured at BOTH scoring seams:

- `settlement_baseline.compute_per_court_acceptance` — a consenting court
  passes without meeting the threshold, keeps its real score (honest about what
  the peace is worth to them), and takes the `consented` band;
- `settlement_ratify.consenting_courts_for_ratification` — the fresh re-score
  at ratification reads the same consent, without which a Ratify button that was
  true when drawn is false when pressed.

Consent is granted to a SPECIFIC package: if `settlement_terms` no longer equals
`consent_terms` (an edit or a restage) it lapses and every court is scored
normally again. `consent_offer_id` is PROVENANCE and is deliberately unread —
lapsing on "the offer is no longer live" would kill the consent on the very
tick the accept consumes the letter. **Hard stops always
block** — consent says a court is willing, never that a clause is legal or a
pair is still at war. A covered court that has since left the war is dropped from the coverage
(`_live_covered_for_offer`) and named to the player in a sentence derived from
`participant_meta[...]['exit_path']`, so a court France destroyed is not
described as having settled; an offer whose courts have ALL departed is refused
as `offer_courts_all_settled`. The drop narrows the COVERAGE, so it must narrow
the TERMS with it: an accept whose package still NAMES a departed court
(`_terms_naming_departed_courts`, drift-locked to the validator's own
`_clause_role_nations`) is refused as `offer_terms_name_a_departed_court` with
the letter left standing, while Revise Terms — an editable draft — drops the
dead clause instead. Without that the review staged ratifiable and the
ratification rejected it: a button true when drawn and false when pressed.

**Elimination resolves its pairs.** `mark_participant_eliminated_in_all_wars`
moves the eliminated nation's `active_diplo_keys` entries to
`resolved_diplo_keys` with `pair_status: "resolved"`, `resolved_turn` and
`resolve_reason: "participant_eliminated"` (lever
`ELIMINATION_RESOLVES_ITS_PAIRS`). It does NOT stamp `ended_turn` /
`end_reason`: the war continues for everybody else, and an empty
`active_diplo_keys` already reads as "no unresolved hostile pairs" downstream.
Without this, a pair naming a nation that is on no side can never be returned by
`_active_cross_side_pairs` and can never be resolved by any peace, so
`revalidate_staged_settlement` refuses every ratification of that war forever.

**A dialogue that exists to interrupt takes the slot from mail.**
`DialogueManager.mount_over_mail(dialogue)` preempts when the current slot is
empty or holds a `SOFT_STOP_MAILBOX_TYPES` item (the letter re-queues, exactly
as `open_flow` already does) and otherwise falls back to `push`. It never
displaces a hard stop or a decision in progress. Used by the counter-offer
answer to France's own overture and by the commitment paradox. Two riders:
`clear_stale` spares a queued `PARADOX_DIALOGUE_TYPES` entry (a crisis whose
deletion is itself a decision), and `main._attach_modal_for_the_carried_question`
delivers the popup whose `dialogue_id` equals the carried dialogue's — slice
6's rule (a response that asks a question never carries a POPPED popup) still
holds for every other popup, because a bound popup is not a second question but
how that question is drawn.

**One treaty, two harshness questions.**
`diplomatic_templates.calculate_treaty_harshness` has two dialects — a
direction-blind `clauses` loop and a `demands` loop — and they must price the
same types (pinned as a census). For the bilateral ratification path use
`burden_on_nation(clauses, nation)`, which selects the clauses that nation PAYS
and prices them through the demands dialect: the treaty RECORD stores what the
peace cost the party it was asked of (DD8-4's escalating-harshness memory), and
the BPH-C separate-peace penalty reads the burden on the COMMON ENEMY. Summing
both sides books our own concessions as harshness against us.

**Direction in the offer copy.** The incoming-offer popup publishes `amount`
(what France is asked to pay) and `amount_offered` (what is offered TO France)
separately, and picks one of FOUR arrival registers — demand, `_concession`,
`_terms`, `_none`. The fourth exists because the register may not be chosen from
gold alone: `_settlement_offer_build_terms` drops the indemnity when the payer's
chest is empty and falls through to the carve gate, so the package the producer
builds for a beaten, bankrupt France — a white peace plus a `create_client` —
took the no-gold voice and told the player nothing changed hands.
`SUBSTANTIVE_NON_INDEMNITY_TYPES` is the set that forces `_terms`; a register
may never assert what the package does not do. AUD-c lets a losing court PAY to close a war, so a demand-shaped
default announces a concession as dunning. The incoming envoy popup's
"Assessment" label is likewise recomputed on the UN-oriented `demands` (the
burden on France) while its fallout warnings, which are about our allies'
reading of what we let the enemy off with, stay as they were.

## 33. The morning briefing tells the truth (FA slice 11, landed September 5, 2026)

Landing record: the boxed SLICE 11 block in `docs/BUG_FIXES.md` §Final
Whole-Game Audit. Five rules about the surfaces the player reads each turn.

**A satellite breaking free briefs itself, at the exit it took.**
`vassal.record_vassal_break(world, vassal=, lord=, exit_path=)` is called at
all THREE exits of `check_vassal_rebellion` — war, armistice, graceful
independence — and NOWHERE ELSE (an AST census pins the three call sites).
The review round corrected this paragraph: it had claimed the VS-6
free-defection arm's caller uses it too, which is false. A defection is
briefed by `attempt_vassal_bribe`'s own `diplomatic_vassal_defected`
dispatch line and `vassal_defected` log row; it never writes a
`vassal_broke_free` row, and the `vassal_lost` headline class reads BOTH
sources for exactly that reason. `record_vassal_break` does two things:

- queues the per-exit dispatch template
  (`diplomatic_vassal_rebellion` / `..._broke_free_armistice` /
  `..._broke_free_peace`) with the fog rule decided AT QUEUE TIME:
  `always` when the lord is the player, `partial_on_nation` otherwise. This is
  not a style preference. `_is_dispatch_event_visible`'s `player_vassal` arm
  reads `world.vassals` when the dispatch is BUILT, after the row has been
  deleted, so a rule evaluated then can never see the satellite that just
  left;
- writes ONE log row `vassal_broke_free` carrying `exit`, so the campaign log,
  `_build_headline`'s window and Le Moniteur can see a rebellion at all. Its
  campaign-log fog arm reads BOTH courts (`vassal` and `lord`), like every
  sibling vassal arm in `filter_campaign_log` — the first cut read the vassal
  alone, so a satellite breaking from a lord we watch closely was hidden when
  the satellite itself was dark.

The graceful-independence exit is the one to watch: it `continue`s early, and
on the 1805 board it is the exit both big satellites take (they cascade-join
France's war and hit the war-instance side conflict). Any future work here
must reach that branch, not only the war branch. The armistice exit ENDS at
its own arm and no longer falls through to the war tail.

**Every break completes itself.** `vassal.complete_vassal_break` holds the
four things that are true of a satellite leaving however it left — the freed
nation's assimilated corps come home, every sibling satellite loses 10
loyalty, the lord's coalition threat falls 10, and the pair's relation falls
50 — and all three exits call it. This is the review round's headline: the
`continue` that stopped the armistice exit narrating a war it had not
declared took those four with it, and the graceful exit had been dropping
them since long before the slice. What the helper deliberately does NOT hold
is the CRITICAL "War declared." banner and the `vassal_rebellion` event
(both false outside the war exit) and the VS-3 granted-province reclaim
(documented WAR-only — flipping provinces back during a respected armistice
would itself be a violation). The helper call sits INSIDE the same lever
gate as the armistice `continue`: with the briefing lever down that arm
falls through to the war tail, which applies the four itself, and a call
outside the gate doubles them.

**The CRITICAL rail banner is lord-gated.** It fires only when the lord is
the player. It was the last surface in this family left lord-blind, and once
the dispatch line and the log row became lord-aware it contradicted them —
measured, an Austria-lorded Bavaria rebelling raised *"Bavaria has rebelled
against Austria! War declared."* on FRANCE's own rail, ungated by fog. A
foreign lord's rebellion still reaches the player through the dispatch line,
which is.

`vassal_broke_free` REPLACED the inert `diplomatic_vassal_rebellion` entry in
`CAMPAIGN_LOG_TYPES`, so the count is unchanged at 160 and the NINE pins on
that number hold. `diplomatic_vassal_rebellion` remains a DISPATCH key.

**A lost satellite can lead the briefing.** `vassal_lost`, weight 84 — above
a bare province, below a broken corps of our own. It reads four sources:
`vassal_broke_free`, `vassal_defected`, `vassal_transferred`, and
`nation_eliminated` carrying a `lord` equal to the player. That last needs the
lord captured BEFORE `_eliminate_nation` tears the vassal row down (GR4), and
stamped on the event; reading `world.vassals` at briefing time cannot answer
it. Adding any class in the [84, 99] band means extending the diverse-tail
floor's ADMIT list in `test_the_floor_is_named_and_admits_the_marshal_fate_band`
— that pin passes in SILENCE for a class it does not enumerate.

**The soil alarm is one run, on home soil.** `enemy_on_our_soil`'s identity is
the CLASS, not `class:region`, so the standing-alarm ladder continues when the
enemy moves between home provinces and restarts only on a genuine gap; and the
arm skips a province that is not in `home_regions`, so ground France has
CONQUERED is not narrated as French soil.

**A shelling is a mauling.** `_build_headline`'s `own_mauled` arm accepts
`bombardment` as well as `battle`, and Le Moniteur's `_WAR_TYPES` carries it.
A bombardment event has no `location` key — its field is `defender_location`
— so the arm reads both or renders "mauled at the field".

**A prisoner is a prisoner on every surface.** `dispatch["prisoners"]` is
rendered by BOTH `main.gd` and `dispatch_view.gd`; `ledger._derive_status`
returns `captured` (captivity outranks every other status) and the FORCES row
carries `captured`/`captured_by`, which `strategic_ledger.gd` renders as "Held
by X at Y" in place of the location line. The model's truth is
`marshal.captured_by`; there is no `captured` boolean on the marshal.

**The enemy phase reports what happened to us.** Two carve-outs beside PT-E5's
in `main._filter_enemy_phase_by_visibility`: a `garrison_assault` /
`garrison_destroyed` event whose `region` the PLAYER controls survives the fog
gate (the gate keys on the assaulter's province, which is enemy ground; the
assault itself lights the assaulted province FULL). And a capturing `move`
event carries `region` and `capture_choice` alongside `captured_from`, so the
dialog can say the province fell, whose it was, and whether it was secured or
sacked. Both client arms are built from the STRUCTURED event, never from the
server `message`.

**The coalition card sees its members through the collapse.** CA8-D2 folds the
bilateral fronts of one coalition war into a single HUD row. That row now
carries `coalition_member_rows` — the folded pair rows, leader first, reduced
to the seven keys in `COALITION_MEMBER_ROW_KEYS` (the six the card reads plus
`opponent_display`, so a formed nation is never shown under its dead name).
Carrying WHOLE rows costs 10KB of `active_wars` on every response; carrying
these costs under 800 bytes. ONE reader unfolds them — `war_status._coalition_rows` for the metadata block and
the weak-link loop, `war_detail_popup._coalition_member_rows` for the card's
bar loop, member loop and Target loop. `_shared_coalition_war_id` deliberately
does NOT use it: it wants the war, not the members. Without this the card drew
one bar and no Targets for a three-power coalition, and
`diplomatic_advisory._build_situation_recommendation`'s "court the weak link"
counsel was dead on every multi-participant war.

**A day of losses is NOT collapsed** (FA-53, refuted). Several homeland
provinces falling in one turn produce one candidate each, and the page names
three. WO slice 4 (WO-D6) chose this deliberately: it answered the same
measured failure by splitting `capital_lost` out so the capital always leads,
and pinned the three-province page five ways. Do not collapse them without
re-opening that decision.

---

## 34. The road home is walked (FA slice 12, landed September 5, 2026)

Three rules on the WIN-D3 evacuation corridor. Build contract:
`docs/WAR_WITHDRAWAL_SPEC.md` §7a. Levers in
`backend/game_logic/withdrawal.py`; landing record in `BUG_FIXES.md`
§Final Whole-Game Audit.

**1. The treaty claims no first step it never took**
(`THE_TREATY_CLAIMS_NO_FIRST_STEP`). `StrategicOrder.issued_turn` means
exactly one thing — *"first step already executed by executor.py"* — and
`StrategicOrderProcessor.process_strategic_orders` skips any order carrying
this turn's stamp on that basis. The treaty's free MOVE_TO is the only
`StrategicOrder` in the codebase built outside `strategic_executor`, and it
executes nothing, so it no longer stamps. `started_turn` still records when
the order was made. Do not "restore" the stamp for symmetry: it cost the
corps the peace turn, which spent one of the three slack turns §6 promises,
and — because a marching corps' surplus is constant by design — put him at
the warning margin for every turn of an optimal march.

**2. A corps frozen on the game's own question is not loitering — and
that mercy is MARSHAL-scoped** (`A_STANDING_QUESTION_IS_NOT_LOITERING`). The
skip above `continue`d before `_check_interrupts`, so removing it un-shields
the issuance turn from the cannon-fire ask. A marshal awaiting the player's
word is therefore not judged — not warned, not interned — for the WHOLE
interrupt set, order-bound and standalone alike, since a cornered marshal
awaiting "fight or break out" cannot march home either.

**The scope is the rule, and the first cut got it wrong.** Routing this
through `_is_immobile` adds the marshal's NATION to `grace_nations` and
refreshes the whole corridor. Measured by the slice-12 review round: two
corps stranded, one frozen on a question and the other simply refusing to
march — the refuser was never interned, his warning read the identical
"2 turn(s) left" fourteen turns running, the corridor's expiry walked 10 → 23
and never closed, and since `has_evacuation_grant` gates the transit arm on
`can_enter_territory`, one unanswered modal bought permanent right of passage.
It was not exotic: an unattended 12-turn run picked up an organic
`cannon_fire` ask at t4 and held the corridor open for nine turns. A ROUT
still refreshes the whole corridor — that is pre-slice and bounded at 0–3
stages. **Do not clamp the rout bump to `EVACUATION_MAX_TURNS`** — `duration`
may legitimately exceed 12 for a trans-continental march, and the clamp
shortens that corridor. (Written, measured, removed.)

**3. The offer stands while he is stranded**
(`THE_ROAD_IS_OFFERED_WHILE_HE_IS_STRANDED`). Issuance ran once, at the
transition; the judge re-derives who is stranded every turn. So a corps
stranded AFTER the peace — the counterpart's other wars taking the ground
under him — was warned three times and interned without ever being handed a
road. `process_evacuation_grants` now calls the extracted
`withdrawal.offer_road_home` per nation with a standing grant, which is the
same body issuance uses, so all four guards are shared rather than re-earned.

**The refusal is remembered, and its siting is the design.**
`Marshal.road_home_offered` (serialized) is written where the road is GIVEN
and read where it would be given again. `strategic_order = None` is written
at many seams a player answer reaches — the typed cancel and
`POST /cancel_order` converge on `_execute_cancel`, but `_respond_blocked_path`
alone clears an order at five places, and the stalemate and cannon-fire
answers at more. A guard keyed on CANCELLATION would have been fixed only at
the seams somebody enumerated; keyed on ISSUANCE it covers every way the
order can be let go. The refusal keeps its consequence: a corps who declines
the road is still warned 2/1/0 and interned.

**It is cleared in three places, and each answers a different question.**
(a) When he reaches home — the offer is spent. (b) When a corridor opens for
a nation that had NO passage standing: a genuinely new treaty is a new offer,
but a SECOND concurrent one is not (the first cut cleared the whole nation
unconditionally, and an unrelated peace on the other side of Europe handed a
corps back the road he had refused). (c) When the ENEMY took the order rather
than the Emperor — `_the_enemy_took_his_order`, reading `retreating` or
`broken`, because three `combat_executor` sites null a `strategic_order` with
no player anywhere near it and a latch that cannot tell a refusal from a rout
interns a corps that refused nothing.

**Rejected, with the measurement:** converting a cancelled road-home order
into a HOLD (so the existing "the player's own order stands" guard would skip
him) makes a *cautious* marshal auto-fortify on the soil of the power we have
just made peace with, every turn, and puts an *aggressive* one on the sally
arm — an order the player did not give.

**The mid-treaty beat is told from the PLAYER's side of the table.**
`_offer_event` returns None for a counterparty corps, and that gate is not
optional: the fog arm for `evacuation_granted` admits any SIGNATORY, which is
right for the treaty's own beat (both courts signed it) and wrong for a
per-corps bulletin published every turn. Measured without it, France read
*"Berthier has put ArchdukeJohn on the road home to Bohemia"* about an
Austrian corps it could not see — his province, his destination, France's own
chief of staff's voice, and a campaign-log line reading "under the peace with
France". `_grant_message`, the producer beside it, carries a docstring
paragraph about exactly this, written after an early draft counted both sides.

It rides the existing `evacuation_granted` event type with one extra key,
`mid_treaty`, which three renderers branch on: `campaign_log.format_event_oneliner` (or it re-announces
a peace signed turns ago), the `dispatch.py` road-home identity (per-corps,
so two stranded corps are two pieces of news), and the headline class
`road_home_mid_treaty` (or it opens "the war with Austria is over" three
turns after it was). A new event type would have cost nine
`len(CAMPAIGN_LOG_TYPES) == 160` pins for a sentence.

**Two soft vassal exits ring the bell** (`vassal.A_QUIET_BREAK_STILL_RINGS_THE_BELL`).
`record_vassal_break` raises one HIGH, lord-gated tray alert for
`vassal_rebellion_independent` and `vassal_rebellion_armistice`. Never
CRITICAL — that is the war register — and the copy may not contain
"War declared", "rebelled against" or "ceased to exist", all three of which
are pinned bans. The four MECHANICAL effects live in `complete_vassal_break`
(slice-11 review round) and must not be duplicated here.

---

## 35. What the zip actually contains (FA slice 13, landed September 5, 2026)

Five rules about the SHIPPED build, not the source checkout. Landing record
in `BUG_FIXES.md` §Final Whole-Game Audit; pins in
`tests/test_fa_slice13_shipping_2026_09_05.py`.

**1. An instruction to the player must know which build is running.**
`Utils.launch_hint()` is the single source, and it branches on
`OS.has_feature("editor")` — verified on the engine: the editor binary
reports `editor=true / template=false`, an exported build the reverse. The
editor arm names `.venv\Scripts\python.exe -m backend.main`; the template arm
says to CLOSE the window and use `launch.bat`, deliberately not "double-click
launch.bat", because the batch runs `start /wait InkAndIron.exe` and would
queue behind the window it is telling them about. **No `.gd` file outside
`utils.gd` may name a Python command** — pinned as a census, because before
this the whole client had ZERO `has_feature` / `is_debug_build` /
`is_editor_hint` calls and three surfaces stated a dev command
unconditionally. `Utils.build_label()` reads `application/config/version`,
which project.godot must author or the version line renders empty.

**2. A licence notice ships WITH the game, and the copy route is not
optional.** Godot's `export_filter="all_resources"` walks the
EditorFileSystem and skips entries it types `TextFile` — which is what every
`*-OFL.txt` and `kenney-license.txt` is in the project's own filesystem
cache, while the `.ttf` are `FontFile` and the `.json` are `JSON`, which is
why those ride the `.pck`. So the notices are COPIED into `deploy\dist\...\
licenses\` by `build.bat`, and the two extension-less `LICENSE` files are
renamed on copy (Godot does not scan extension-less files at all). **Do not
widen `include_filter` to `*.txt`** — it sweeps the whole project. **Do not
use `xcopy /s`** — combined with `/i` it succeeds silently on an empty match,
so a future rename would leave the folder empty at errorlevel 0; there is a
pin against it. Every copy carries build.bat's own `if errorlevel 1 echo
[WARN]` arm. The pin is a DISTRIBUTION census derived from `git ls-files` at
test time; `test_ui_visual_foundation.py::test_ui1_font_ttf_and_ofl_present`
is a REPO-presence check and says nothing about the zip.

**3. A hotkey the game advertises must work in the state the game puts
itself in.** The command line holds focus after nearly every action (it is
re-grabbed at 35 sites) and a focused `LineEdit` eats printable keys before
`_unhandled_input` sees them. So every advertised key has an Alt form:
`_SCREEN_HOTKEYS` (PC15-18) for the six screens, and `main.gd::_alt_game_key`
for E, Tab, M, Home and +/−.

**Alt+Tab is the exception, and it is why the terminal's real focus-safe key
is Alt+`.** The Windows shell takes Alt+Tab before any application sees it,
and Windows is the only shipped target — so advertising it would have been a
fresh dead instruction in the slice whose whole thesis is that the keys the
game advertises must work. `KEY_TAB` is kept in the arm because it costs
nothing on a platform whose window manager lets it through; `KEY_QUOTELEFT`
is the one the README and the boot help teach.

**The E and Tab arms mirror the gate their unfocused twin obeys** — bare E
and Tab sit BELOW `_unhandled_input`'s `if _is_screen_open(): return`, so
their Alt arms check `_is_screen_open()` too, or Alt+E ends the turn with a
full-screen ledger open where bare E refuses. **The four MAP arms deliberately
DIVERGE from theirs**, and `_map_keys_live()` says so: the bare map keys live
in `map_renderer_base.gd::_unhandled_input`, whose only gates are
`text_focused` and `panning_enabled`, so they work under an open modal and
the Alt arms do not — a key pressed into a command line the player is typing
in, while a dialog awaits an answer, is not a map command.

**The map keys are CALLED, never re-emitted**: a re-emitted event lands on
the same `text_focused` guard, so the focused route goes through the public
`recenter_view()` / `zoom_step()` / `cycle_map_fill_mode()`. The Alt arm
consumes the event whether or not the gate allows the action, so Alt+E never
types an "e". The README and the boot help advertise the Alt form beside the
bare one — before this the README named "Alt" zero times.

**4. The School of War does not touch the campaign autosave.**
`save_manager.autosave` no-ops for `scenario_name == "tutorial"` (TUT-F2) and
`/new_game` says so in the same terminal. Three client surfaces claimed
otherwise. The restore promise ("Continue restores it") is CONDITIONAL on
`_saves.size() > 0`: the confirm row also shows in the `came_from_game and no
saves` arm, where nothing is on disk at all. The `Begin anew` confirm is
untouched — it is true.

**5. A source-text pin over a file you also wrote prose in is not a pin.**
Three of this slice's own mutations came back INERT because the licence
census matched `THIRD_PARTY_LICENSES.md` and `*-OFL.txt` inside the `::`
comment block explaining why they must be copied. Scope such a census to the
COMMANDS (`_build_commands()` strips `::` lines), and assert a dispatch
condition literally rather than the presence of the function it calls.

---

## 36. The rulings of slice 14 (FA slice 14 part 1, landed September 5, 2026)

Six rules the FA build turned into code. Landing record in `BUG_FIXES.md`
§Final Whole-Game Audit; pins in
`tests/test_fa_slice14_the_rulings_and_the_singles_2026_09_05.py`.

**1. A garrison assault's minimum-loss floor reads the DEFENDER**
(`GARRISON_LOSS_FLOOR_READS_THE_GARRISON`). Reading the attacker's own
strength made it a pure over-match tax — it binds if and only if effective
attacker exceeds **12.5×** effective garrison, so the bigger the corps the
more it paid for the same works, at a flat 25.4% however large it was. The
base moved; the 2% rate did not.

**The floor is not thereby dead, and a derivation that says so has dropped
the `min(0.35, …)` cap.** There are two regimes: uncapped (the proportional
term wins, and 0.02 never binds) and **capped** (`garrison / strength >
17.5`), where the floor binds again and a 1,000-man remnant assaulting
Vienna pays 500 rather than 175. That regime is reachable by the PLAYER and
by a naval landing and not by the AI, whose rung gates on a ratio — so **GR5
is true of the arithmetic and false of the reachability**, and the comment
says so. Do not "simplify" the constant away.

**The anti-stalemate promise is the DEFENDER's floor, not this one.**
`garrison_losses` carries WO-3's `+1`, so every landed assault kills at
least one defender and the fight always terminates; a 40,000-man corps
taking no casualties from a one-man garrison is the correct answer.

**Only the loss half of FA-D28 was ruled.** The assault COUNT is untouched
(⌈log₂N⌉+1, so 13 for a 3,000-man detachment), which means the grind still
costs 13 AP and 13 marshal-actions and now costs almost no blood. That half
stays open on the row.

**Quote the FIXTURE with any figure here.** Two correct tables that name no
fixture read as a contradiction: the resolver comment is Europe / Lorraine /
plains / cautious / combat-only, the pins are legacy / Paris / urban /
totals. Both reproduce to the digit on their own board.

**2. The garrison assault is on the record**
(`THE_GARRISON_ASSAULT_IS_RECORDED`). The resolver had no `log_event` at
all, so two of its three exits were invisible on every persistent surface:
the works HOLDING, and the garrison destroyed into an OCCUPATION. (The
third, fall-to-capture, was already covered by the `region_captured`
written downstream.) ONE emit site above the collapse branch, so log and
dialog cannot drift and the three exits cannot disagree;
`target_region.controller` is still the DEFENDER there, which is what lets
`_is_player_event` see the right side from either direction.

Two headline classes, because a headline carries one weight and the two
outcomes are not the same news: `garrison_stormed` 87 and `garrison_held`
82, both gated on the player being the DEFENDER — a garrison we storm
abroad belongs to the triumph ladder, and building it as a wound re-opens
CA8-D6. Neither is in `STANDING_HEADLINE_CLASSES`: this is current news, and
a state-derived class in that set repeats and buries everything else (PC-7's
`marshal_reversal` trap).

**`CAMPAIGN_LOG_TYPES` went 160 → 161 rather than swapping.** Slice 11's
move — retire an inert type for the new one — was measured unavailable: a
producer census finds exactly six types with no producer, every one of them
`diplomacy`, while all seventeen `combat` types have producers. Retiring a
diplomacy half-pair to make room for a combat type deforms a live family and
reds a pin anyway.

**A `battle_report` for garrison combat is REFUTED BY DESIGN, not deferred.**
`snapshot_defender_modifiers` takes a **Marshal**, so CA8-19's "requires a
defender object that does not exist" bites there: the defending half of
`modifier_breakdown` is structurally empty forever. It would also
double-render against slice 11's structured client arm and re-route the
muster "Attack Anyway" gate, which keys on `battle_report` being present.

**3. A field marshal is one who is not at a desk AND is standing.**
`capture_marshal` leaves `nation` unchanged and zeroes `strength`, so a
prisoner stayed in `get_field_marshals` forever while its three maintained
siblings all filtered him out — and Last Marshal Protection counted the
dead. The two clauses are additive and each is needed: an administrative
marshal is at strength 0 too, and a man at the desk with men on the books
is constructible.

**4. An answer to a redemption audience must be one the audience OFFERED**
(`REDEMPTION_ANSWER_MUST_BE_OFFERED`). The rules live in the option
BUILDER, so validating against a static list made Last Marshal Protection
and the one-admin rule presentation-only — measured, sending
`administrative_role` when it was not offered produced three admin marshals
and +3 actions. The guard sits in `handle_redemption_response`, **above the
latch clear and the cooldown stamp**, so every caller inherits it and a
refusal spends nothing. `world.pending_redemption` is cleared **only on
success**: clearing it unconditionally orphans the question the refusal
leaves standing.

**5. A frozen grace clock remembers what it covered**
(`Marshal.expectation_covered_at_freeze`, serialized, −1 = none). WO-18
freezes the clock on a met turn bought by a load-bearing rente so a
grant/revoke toggle cannot dodge erosion. Its safety argument — "a marshal
genuinely kept on a rente never erodes anyway" — fails the moment he WINS
AGAIN: the expectation rises, the branch flips to unmet, and `elapsed` reads
a stale anchor. The unmet branch now tells the two re-openings apart: a
shortfall **bigger** than what was covered means he earned more (a new
window is owed); one at or below it means the payment stopped (no new
window). One-shot — the stamp is consumed on the restart, so a neglected
marshal still erodes on time.

A zero-field version keyed on `pension > 0` was worked out and rejected: it
cannot tell a frozen clock from a running one, so a marshal on an
insufficient rente would restart his window every turn and never erode.

**6. A standing order is priced by the ORDER, except a retreat**
(`STRATEGIC_ORDERS_ARE_PRICED_BY_THE_ORDER`). `free_actions` holds BASE
actions, and the mock chain's WAIT arm sits above hold/move — it must, or
"wait for reinforcements" becomes a SUPPORT order — so any sentence that
also says "wait" parsed to a free verb and skipped **both** the AP pre-gate
and the charge, discarding the `variable_action_cost: 2` the strategic
executor returns. It was a total bypass: at 0 AP a player set five standing
orders and marched four marshals a province each.

The rule sits ABOVE the `is_strategic_execution` override, which must keep
winning — the per-turn step of a standing order is free because the order
was paid for at issuance.

**⛔ And `retreat` is exempt, by design and by measurement.** It is the one
`free_actions` entry with its own comment at the list, and six phrasings
parse `retreat` WITH a strategic type. Without the exemption
`withdraw from the alliance` — a general retreat of the whole army — costs
an AP and is REFUSED at 0 AP, which is the one state in which a retreat
matters. Any future free verb that can carry a strategic type re-opens this;
the census that finds them is `validation.NEVER_STRATEGIC_ACTIONS` (30 of
the 33 are blocked at the parser; only `wait`, `retreat` and `break_square`
can reach the executor with a strategic type).

**7. The desk may be ADDRESSED, from one vocabulary**
(`clause_guards.DESK_ADDRESS_RE` / `strip_desk_address`). `Berthier, status`
and `Berthier, help` worked while `Berthier, end turn` shrugged. The
vocabulary lives in `clause_guards` — the lowest layer, which `llm_client`
imports — and the client mirrors it in `main.gd::_strip_desk_address` with a
two-directional parity pin. **At most ONE address** is stripped, so
`Berthier, Sire, end turn` is not an end turn and `Berthier, Ney, …` is
still an order to Ney. The PHRASING vocabulary is untouched; this widens the
address, not the word list.

**Client-only would have been sufficient and backend-only is harmful.**
`_send_end_turn` canonicalises — whatever the client gate accepts, the
server receives the literal `"end turn"` — so widening the backend alone
advances the turn behind the unanswered-envoys confirm. If this is ever
split across commits, the `.gd` lands first or with it.

**8. Prose inside a file is code, when a pin reads that file.** Two pins in
this slice were redded by COMMENTS: one containing a forbidden word inside
the region a pin slices, one quoting the pin's own slice anchor verbatim and
truncating the harvested body to nothing. `main.gd`'s function ORDER is
load-bearing for six such pins — the end-turn gate and `_execute_end_turn`
must stay adjacent, and helpers go below the pair.

---

## 37. The purse and the window (FA slice 14 part 2b, landed September 6, 2026)

Four rules the FA build turned into code. Landing record in `BUG_FIXES.md`
§Final Whole-Game Audit; pins in
`tests/test_fa_slice14b_the_purse_and_the_window_2026_09_06.py`.

**1. An indemnity is priced to the payer's purse on BOTH channels, and it
takes two levers to say so** (`PURSE_SCALED_BILATERAL_INDEMNITY` +
`P8_REDUCER_READS_THE_PURSE`). EC-W4's formula is one source,
`ai_diplomacy.purse_scaled_indemnity`, read by the multilateral settlement
offer and the bilateral P8 arm alike.

**⛔ Never ship the builder lever alone.** `_reduce_p8_demands` halves exactly
once and then falls to a token, so any built figure above twice the largest
acceptable lump collapses to that token — pricing the BUILDER alone delivers
*less* than the unfixed defect (measured 200 on 5 of 5 ambient firings against
220/352/266/277/243). `max(legacy, purse)` does not rescue it either: `max`
protects the built figure, and the built figure is not what ships.

**What the `max()` IS for** is the war-score ladder on a poor payer. A
replacement returns the `0.40 × treasury` cap at every war score the cap binds
on, so the demand stops reading the war entirely; the floor form keeps
`demand(80) > demand(50)`.

**`gold_mult` multiplies the final `min(scaled, cap)`.** Multiplying `scaled`
alone and leaving the cap raw collapses hawk onto neutral wherever the cap
binds — every poor payer, and every rich one above war score ~60 — so R115's
personality signal disappears exactly where it is loudest. Multiplying both
terms is the same function (`min(int(a·g), int(b·g)) == int(min(a,b)·g)` for
`g > 0`), so there were only ever two candidates. The effective ceiling
therefore widens to `treasury × 0.40 × gold_mult` on the bilateral channel;
that is conscious, and it never reaches the player because the reducer
re-floors at 15%.

**A reduction never raises the demand, and BOTH arms need the clamp.** The
fallback's is obvious. The halve step's looks dead — its output is normally
rejected and the fallback decides — but retry 2 drops a non-gold demand and
returns the halved dict directly, and there an unclamped floor turned a built
300 into a delivered 450.

**Anything measured on `make_world()` is vacuous for the reducer.** France
holds 800 there and the purse floor exceeds the flat 200 only above a treasury
of 1,333.

**The war age comes from `pair_war_age`, never from a diplo key.**
`world.war_instances` is keyed by war id; a `_make_diplo_key` lookup returns
nothing and silently prices every peace at age 0. One coalition instance
covers France against Austria *and* Britain, so every court in it prices the
same age — and the term is inert wherever the cap binds.

**2. Seam 3 is decided, not built.** `DEMAND_VALUES["gold_lump"]` is linear
and uncapped while every other harsh term saturates, which caps a
*deliverable* bilateral lump at ~491 gold however rich the payer. Re-pricing
it is the correct model and **nothing in the suite pins it** — a 5× softening
of that rate leaves 2,032 of 2,032 gold-touching tests green. So a real
indemnity is a demand the player may REFUSE, carried by `_force_send`, and the
refusal is not free: a schemer court's peace rejection plants +2 coalition
threat per turn for five turns (roughly five turns of decay suspended, not a
one-off +2), and the same rejection feeds `record_diplomatic_refusal`, which
the AI-3 crisis ladder counts with **no type filter** at a threshold of two.
Re-open at the acceptance formula if that proves wrong; do not tune it twice.

**3. A window forecast is TWO calls, and therefore four arms**
(`naval.window_forecast`). Turn T is the live board with `window_turns` set
and nothing else changed. Turn T+1 is that, then `derive_ai_postures`, then
`_readiness_tick` — **in that order**, because the tick reads
`blockaded_nations` which reads postures. Those are literally steps 1 and 3 of
`process_naval_turn`, so both are exact by construction.

The single-call hybrid (window + derive, no tick) is neither turn and is wrong
in 8 of 24 states. The fourth clause arm — shut on T, OPEN on T+1 — is
reachable at turn 3 of the natural play, so a three-arm clause renders a lie
through its fall-through.

**A forecast is pure or it is a cheat.** It deep-copies `world.fleets` and
restores it **in place, all the way down**, inside a `try/finally`. In place
because `_meta` hands out `fleets.setdefault(META_KEY, {})` and a tick binds
each `rec`; a rebind restores the values and breaks the identity. The
`finally` because without it one exception grants a free two-turn window, a
lifted blockade and +5 readiness to every navy in Europe — on a press of L.
**A two-clean-calls purity pin passes either way; the exception arm is the one
that binds.**

**A ranking is a pipeline: `_rank_links` is the only one.** Camp province,
then army mass, then the sorted key. Every reader shares it — the chip, the
confirm and the outcome sentence — and the outcome sentence ranks over EVERY
tracked link, not only the opened ones, or the report of an act names a
different crossing from the forecast of it.

**Quote the number that opens it, not the rounded ratio.** `crossing_check`
allows on `mover / coverage >= floor`, so the least sufficient mover is
`ceil(coverage × floor)`; `round` is off by one on exactly the states the
clause exists for. The epsilon is float hygiene (`50.0 × 0.9` evaluates to
45.000000000000007).

**A remedy must be gated on the state it names**, or it becomes the defect it
is fixing one layer down.

**4. "Once per war" means the naval war** (`naval.has_naval_war`), read by the
reset and by the gate term so the two cannot drift; and **the Boulogne camp is
an ARMY fact**, walked with `iter_fleet_records` rather than the ships > 0
iterator, so a nation that has lost its navy can still pull the Royal Navy
home — the one move it has left.

---

## 38. The School sees the answer (FA slice 14 part 2c, landed September 6, 2026)

Rules for the tutorial overlay. Landing record in `BUG_FIXES.md` §Final
Whole-Game Audit; pins in
`tests/test_fa_slice14c_the_school_sees_the_answer_2026_09_06.py`.

**1. Every handler that answers a BLOCKING question feeds the tutor.** Six did
not. At the lesson's own two modal beats the card went on asking for an answer
the player had already given — and the typed route the card named is
UNREACHABLE, because `_execute_command` disables the command line,
`_route_response_ui` returns before re-enabling it, and the objection dialog
has three buttons, no close and no ESC. Six literal `tutorial_overlay.observe(`
sites, never a shared helper: extracting one reds T-G2 (`count >= 2` sees 1)
and makes T-G3 raise rather than fail.

**Placement is at the TOP of each handler**, above the early returns —
`_on_objection_response` has five, and `_on_capture_choice_response` returns
into the W6-8 estate stage before anything else.

**The census, not the count, is the pin.** T-G2's `count(...) >= 2` is
satisfied by 2 and by 8 alike and was green for a month while two beats were
blind; it survives only as a floor. The replacement is a call-only closure over
comment-stripped function bodies, with a sensitivity arm and an exemption list
that states a reason per row. Measured: the {call-syntax, comment-strip} matrix
gives **10 / 10 / 44 / 85**, so call syntax is the only load-bearing guard —
excluding `.connect(` / `.bind(` is measurably nothing and must not be written
as though it were the fix.

**2. A card names what the player can PRESS.** The modal's buttons are built at
runtime and carry the marshal's name and the trust figures, so a card may name
only the stable leading words (Trust / Proceed as Ordered / Compromise;
PLUNDER / SECURE). The headless driver still answers with the typed token, so
any pin binding the driver's policy to the card's counsel must map the two
rather than share a literal.

**3. The tutor branches on STATE, never on a transient event.**
`game_state.enemies` rides every response; a battle event rides one route.
⚠ **That entry is FOG-MASKED** — `strength` reads 0 at PARTIAL against a truth
of 900–1,500, and `location` can name a province the executor refuses to
pursue to. Read it for a NEGATIVE test only, test the fog clause BEFORE the
location clause, and never render either field. A missing row means
LAST_KNOWN, UNKNOWN or gone-from-the-roster, which are indistinguishable, so
it is `lost` and never `taken`.

**4. `turn_gate` gates DISPLAY, not ADVANCE.** `observe()` evaluates the
current step's predicate unconditionally; the gate only decides whether
`_render()` prints the chip or the "Berthier resumes" line. **Any predicate
that can be true before its gate consumes its step invisibly** — measured, an
early release on card VII walked the player past VII and VIII with no chip on
either and parked them on IX from turn 4.

**5. A branch arm lives in a nested `alt` dict**, after the step's own
`"suggest"`, re-using the `"suggest"` / `"suggest_action"` key names (T-B1
extracts those by regex, so a new key name ships the chips unpinned) and
carrying no `"id":` (the slice-8 census splits STEPS on that key and would mint
a phantom step). A second entry at the same `turn_gate` is not an alternative:
`STEPS.size()` is in the badge and `_derive_step_for_turn` resumes at the first
step of the highest gate.

**⛔ 6. In Godot 4 a `const` Dictionary is READ-ONLY AT RUNTIME, and the parse
harness cannot see the violation** — it loads scripts but never calls
`_render()`. Writing `STEPS[i]["body"] = …` ships a hard script error that
passes every pin and does not appear in the campaign boot smoke either, because
that boots the campaign and not the lesson. `duplicate()` before merging, and
verify branch rendering by EXECUTING it on the engine.

**7. Seed derived state on `on_world_swap`.** `/load` carries the roster and
`_derive_step_for_turn` can resume on a branching card, so a member reset to
its empty value renders the default arm over a board that has moved on.

**8. `_pred_capture_resolved` reads the pending question, not only the answer.**
W6-8's estate stage mutates the stage-1 response in place, so an answer that
mounts it carries `capture_choice` and `pending_capture_choice` together.

**9. The objection predicate is deliberately loose and that is the self-heal.**
`pending_objection` is ABSENT from every resolving response — typed, button and
an ordinary command alike — so it cannot be hardened by a key-presence check,
and any successful command heals a stale card. That is why observing the
letter-book is safe: it changes WHEN the card heals, not whether.

---

## 39. The door and the fallen lord (FA slice 14 part 2d, landed September 6, 2026)

The two rulings slice 12 filed against itself. Landing record in
`BUG_FIXES.md` §Final Whole-Game Audit; pins in
`tests/test_fa_slice14d_the_door_and_the_fallen_lord_2026_09_06.py`.

**1. A peace leaves a door open for three turns, even when it stranded
nobody** (`world.corridor_windows`, `CORRIDOR_MINIMUM_WINDOW = 3`). Without
it the outcome for two identically stranded corps turned on whether a THIRD
corps happened to be caught out when the ink dried.

**⚠ A WINDOW IS NOT A RIGHT OF TRANSIT.** It is a memory that a peace
happened here, it lives in its OWN store, and it is invisible to
`has_evacuation_grant` — no marshal can walk on one. It confers nothing until
a corps is actually found stranded under it, at which point a REAL corridor is
written. That is what closes the Trojan-corridor question by construction, and
it is also why the row flips no existing pin: `evacuation_grants` behaves
byte-identically.

**⛔ The promotion must write a PROVISIONAL grant before it measures.**
`distance_home` routes WITH the corridor — the corridor IS the road — so
asking how far a corps is from home before opening the door asks him to walk a
road that does not exist, and he answers "no road". This shipped broken once
and driving it is what caught it; `open_evacuation_corridor` has always solved
it the same way.

**The corridor is sized at DISCOVERY, never at the peace.** Sizing from the
treaty turn hands a corps a clock that has already been running for three
turns. A pin asserting only a floor on the surplus is INERT — compare the
surplus at two discovery delays instead.

**An EXPIRED window is refused, both rollback branches write one, and a
resumed war purges it.** The all-cut-off branch gets a window because
withholding it would mean a peace that stranded people we could not help
affords LESS than a peace that stranded nobody; it is near-inert by design,
since promotion needs a reachable road.

**The honest limit is part of the rule: a corps stranded more than
`CORRIDOR_MINIMUM_WINDOW` turns after the peace is not covered.** That is the
only place the constant is falsifiable and it is pinned in both directions.

**2. Elimination is a FOURTH way to stop being a satellite** — and the one
that actually fires on the shipped board. Only the threat relief ships
(`ELIMINATION_RELIEVES_THE_LORD`, `reduce_threat(..., 10,
"vassal_lost_to_conquest", target=lord)`), sited **AFTER**
`self.vassals.pop(nation, None)`: before it, the departing row still satisfies
`other_state["lord"] == lord` and the empire docks ITSELF.

**Each of the three declines is stated in code AND pinned**, because a decline
nobody can see is indistinguishable from an omission. The −50 relation (no
court left to be angry with). The corps hand-back on the satellite path
(neither siting is right — an assimilated contingent flies the LORD's flag).
The sibling −10 shock (a defiance-is-contagious signal, and a satellite EATEN
by a rival demonstrates the opposite; it is also the only arm that costs
France a province, which against the FA-D27 gate makes an already-overrun
France strictly worse). `amount = 8` — the `release_vassal` figure — is
measured WORSE: it makes the series' largest single-turn fall non-unique.

**3. There is a FIFTH exit and it is worse than the fourth**
(`FREED_SATELLITE_KEEPS_ITS_ARMY`). When a LORD is eliminated the same handler
freed its satellites in total silence AND destroyed the satellite's own
assimilated corps, tombstoning it under the lord's flag, because the marshal
sweep keys on `m.nation` — while the satellite survived with its provinces and
no army. **The hand-back therefore runs BEFORE the sweep, which is the
opposite siting from the satellite path**, reading the rows sixty lines before
they are deleted (the FA-38 `_lord_of_the_fallen` idiom).

**Reuse `vassal_broke_free` with `exit: "lord_eliminated"`; do not mint a
type** (a new one costs twelve pins across twelve files and forfeits the fog
arm, the one-liner switch and the dispatch consumer). **But reuse is not
free**: without its own arm in `format_event_oneliner` the exit falls through
to "…has broken free of {lord}. War." — wrong in every clause.

---

## 40. The instrument sees (FA slice 15, landed September 6, 2026)

Two halves. Part a is a save-killer found while measuring; part b is the
playtest driver, which is the instrument the whole final audit was read off.

### 40.1 A serialized field is never deleted

`Marshal.original_nation` is declared, serialized, and was `delattr`'d by
`vassal.release_vassal`. `Marshal.to_dict` reads it **bare**, so from that
moment every `to_dict` raised and `save_game` swallowed the `AttributeError`
into a `success: False` with the reason in a field nobody reads. The campaign
stops being saveable and never says so.

**The rule: a field that is written into `to_dict` is never deleted from the
object. Set it to `None`.** If a field genuinely may be absent, `to_dict`
must read it with `getattr(self, "x", default)` — that is the exempt idiom.

Enforced by an AST census in
`tests/test_serialization_enforcement.py::TestASerializedFieldIsNeverDeleted`:
no `to_dict` may read `self.X` bare for any `X` that is `delattr`'d or
`del`'d anywhere under `backend/`. Its own helpers are exercised on synthetic
source, because a census that is green over the real tree cannot be killed by
a mutation that removes one of its arms — which is what two INERT pins on the
first sweep were saying.

⚠ **"If it exists on the object, it must serialize" reads the object as
CONSTRUCTED.** It was structurally blind to this class, which has now bitten
twice (IGR-X1 was `del marshal._recovery_destination`).

### 40.2 What the digest must say

`tools/playtest_driver.py` is a measuring instrument, and every one of these
is a rule about not reporting an absence you did not observe.

**An empty enemy phase is not an empty turn.** `Digest.enemy_phase` must not
return early on `not actions`: the payload carries `fog_hidden_summary` /
`fog_hidden_nations`, and 12 of 40 turns on the ambient board have no visible
action at all. One helper `fog_sentences(phase)` serves both arms. `summary`
outranks `nations` — the engine emits the summary form when NOTHING is
visible, so it is the stronger statement.

**The digest is the FOGGED view.** 93 of 1,185 enemy actions on a 40-turn
board (7.8%). An absence in a digest is therefore **not** evidence of an
absence on the board. `docs/PLAYTESTING.md` says so; do not let that sentence
drift again.

**Read `GET /campaign_log` per turn, never once at the end.**
`MAX_EVENT_LOG_SIZE` is 500 and the log rolls: at turn 40 the earliest block
still served is turn 14. This is the IGR-B eviction trap.

**Every name in `AI_AI_LOG_TYPES` must exist in `CAMPAIGN_LOG_TYPES`** — the
row that asked for the allowlist named a type that does not exist.

**The rail carries CRITICAL.** A `priority == "HIGH"` filter drops the
severest notices the game has, and CRITICAL sorts first so a same-turn HIGH
burst cannot evict it under the cap.

**A borrowed method may not reach for `self._private` or a class constant.**
Five stub `Digest`s in the test files borrow real methods. This is slice 8's
rule; slice 15 extends its census to every public method and moves
`MAX_RAIL_ROWS` / `MAX_FOG_ROWS` to module scope.

### 40.3 Parse provenance

`parse_mode` / `parse_confidence` ride the `/command` response from a
`contextvars` ContextVar. Display-only (GR6) and census-pinned: `main.py` is
the only file allowed to name them.

Three things that are easy to get wrong, each measured:

- **Stamp the PLAYER's parse only.** `parser.parse` is called three times in
  `main.py`; the other two are the CR-5 delegation re-issues, which re-parse
  a sentence the ENGINE composed and clobber `parsed`.
- **Read it in `build_base_response`, not `_build_result_response`.**
  `/command` has three response roads and the two early ones — `status`, and
  the refusal arms — build straight through the base builder.
- **`confidence` is on the nested `command`, not the envelope.** The envelope
  carries `mode`, `strategic_score` and `ambiguity`.

The digest prints the mark only when the mode is not `mock`, so a mock run's
digest stays byte-identical line for line and archived comparisons hold.

### 40.4 What the review round added to the rules

**A dedupe on a per-turn surface is keyed per TURN.** The hazard is
intra-turn (a drain follow-up re-running the scan; the strategic processor
re-emitting a parked decision). A run-lifetime key silently reports an
absence you did observe: measured, a ten-turn standing order printed two
rows.

**Read every log block, not the newest one.** `GET /campaign_log`'s
`turns[0]` is the just-BEGUN turn, and the fog filter re-derives the whole
log against the CURRENT world on every call, so old blocks keep gaining
events. Dedupe on `(block turn, type, text)` and re-reading is free.

**Derive an allowlist from the engine; never restate it.**
`campaign_log.COURT_TO_COURT_EVENT_TYPES` is the engine's own definition of
an AI-vs-AI beat and `filter_campaign_log` consumes it. Any consumer's
census runs BOTH ways — every name exists, and every engine name is covered
or named in an exclusion set with its reason.

**One `kind`, one schema.** A jsonl record written from two arms must carry
the same keys with the same types on both.

**No silent caps** — a truncated block says how many it did not list.

**A per-request stamp is CONSUMED by its response.** A `contextvars` value
that is only read outlives a direct in-process call and marks the next
response in that context.

**A borrowed method may reach for nothing that is not module-level.** Not a
private helper, not eagerly-created state, and NOT a class constant. Both
halves are exercised on synthetic source, because a green tree has no
instance of either and a sweep over the real tree reports them INERT.

**A census must be scoped to CODE, and `_code_lines` strips docstrings as
well as comments.** The fog drift pin was satisfied by the driver's own
docstring; rewriting the code tuple to `("x1","x2")` left it green.

**A structural property is asserted structurally.** "The read is inside the
turn loop" is an AST predicate with a synthetic hoisted fixture that must be
REJECTED — a textual "appears before `finish`" is satisfied by the very
regression it names.

---

## 41. The collapse is legible (IQ-2, landed September 14, 2026)

**The rule.** A realm reduced to `COLLAPSE_PROVINCE_CEILING` (1) province or
fewer has COLLAPSED, and every surface that speaks of it reads ONE source:
`backend/game_logic/collapse.py::get_collapse_state(world, nation=None)`. It
returns None off-sandbox (the legacy world keeps its own terminal rules), when
the realm stands, and when the lever `THE_COLLAPSE_IS_LEGIBLE` is False;
otherwise `{tier: "fallen"|"last_province", provinces_held, provinces, capital,
capital_held, capital_holder, standing, standing_men, prisoners, sovereign,
sovereign_captor}`. Surfaces compose from its phrase builders
(`realm_sentence`, `capital_clause`, `forces_clause`, `sovereign_clause`,
`summary_line`) so the same fact is worded the same way everywhere. **Never
add a second collapse predicate.**

**Legible, never terminal.** The module is a READER. Nothing built on it may
end, block or shorten the campaign, and no sentence may say or imply "the
campaign ends", "game over", defeat as an outcome, or the player
"eliminated". Where the player needs to know the game continues, one sentence
says so: `CAMPAIGN_CONTINUES`. What a collapse MEANS mechanically belongs to
the Victory & Objectives Pass.

**The player never leaves the roster.** `world_state.get_active_nations()`
keeps the player even at 0 provinces (`PLAYER_NEVER_LEAVES_THE_ROSTER`) — the
player is never eliminated (`_eliminate_nation` returns early for her), so a
landless France is still billed upkeep, still goes bankrupt and deserts, still
regenerates manpower, and still pays and receives recurring settlement gold.

**Who reads it.**

| surface | where | what it says |
|---|---|---|
| headline `empire_reduced` | `dispatch._build_headline` (weight 100, standing, identity = class) | the summary line; at one province the soil alarm is folded in and its own candidate dropped |
| Berthier's close | `dispatch._pick_berthier_note` — answers the `empire_reduced` headline; on the PC-7 hand-back a rung BELOW broken / bankrupt / bleeding and above the rest | tier-, forces- and treasury-aware; says "it pays" only when the province is not disrupted, and promises no treasury in deficit |
| Talleyrand | `dispatch._build_talleyrand_report` | only what the score measures (*"Sire, {court} would treat with us now."* — no cause it does not measure); the idle nudge names the open question |
| defeat warning | `turn_manager.get_defeat_imminent_state` sandbox arm | heading *THE EMPIRE IN EXTREMIS*; rail titles *The Empire Without Soil* / *One Province Remains* |
| end turn | `meta_executor.collapse_turn_end_fields` (both paths) | one banner line; `collapse_line` + `provinces_held` on the `turn_end` event |
| war room | `diplomatic_advisory._assess_situation` and siblings | *Our own state* first; honest alarm, no-war, rung-4, fallback, overview, Tilsit arms |
| diplomatic ledger | Balance of Europe `collapse_line` / `headline_note`, exposure, the France mirror | the alarm fell because France threatens no one; the courts still at war |
| strategic ledger / status | `ledger.collapse_note`, `intel_report` STATE OF THE EMPIRE | the summary line + `CAMPAIGN_CONTINUES` |
| Le Moniteur | `gazette._collapse_lead`, realm-reduced special edition (97) | the fact, in the period voice |
| chronicle | `WorldState.log_event` stamps `holdings_left`/`holdings_realm` on the player's own losses | *"— France holds no province"* |

**Client keys.** `turn_end.collapse_line`, `defeat_imminent_warning.heading`,
`situation.no_field_army`, `collapse_note`, `levy.closed_reason`,
`depot_closed`, `settlement_tier_side`, `captured_from` on conquest events,
Balance `collapse_line`/`headline_note`, marshal-card `status_note`. Every
read falls back to the pre-IQ-2 render when the key is absent.

## 42. The league is spent (IQ-3, landed September 14, 2026)

**The rule.** When a coalition dissolves for `insufficient_members` and the
dissolution was caused by a TREATY — the `set_diplomatic_state` ejection arm
(PEACE or VASSAL from WAR or ARMISTICE, `reason != "nation_eliminated"`),
which alone passes `remove_coalition_member(..., by_treaty=True)` —
`dissolve_coalition(world, reason, spent_by_treaty=True)` spends the alarm
against the league's `target_nation`:

```
before = threat_by_target[target]
kept   = min(before, this turn's positive LEAGUE_SPEND_EXEMPT_SOURCES rows for target)
after  = (before - kept) // LEAGUE_SPENT_DIVISOR + kept
reduce_threat(world, before - after, "league_spent", target=target)
```

`league_spent_alarm(world, target)` is the pure computation; the dissolution
applies it. The exempt sources are the treaty's own alarm (`treaty_annex`,
`treaty_vassalization`, `conquest_vassalization`, `forced_alliance`), read from
`threat_sources_this_turn` — `add_threat`'s own record, cleared per turn.
Settlement ratification adds that alarm BEFORE its pair transitions eject the
members; the bilateral ratifier adds it after the state write, where it is not
halved in the first place. Either way the peace never forgives its own
conquest, and the result does not depend on the order in which pairs resolve.

**What never spends:** the low-threat tick, the greater-danger pivot,
elimination (`_eliminate_nation` removes without the flag and its teardown
carries `nation_eliminated`), a truce (ARMISTICE keeps membership), a separate
peace that leaves two or more members standing, and every direct call without
the flag.

**Invariant.** `100 // LEAGUE_SPENT_DIVISOR < THREAT_BREWING_MIN`, so the tick
after a spend can neither brew nor fire the ≥90 cooldown override from the
halved alarm alone. No timer is added. The window lasts until the target's own
conduct carries the alarm back to 60.

**Talleyrand reads the projection.** `declaration_would_gather_a_league(world,
aggressor, casus_belli)` returns `{from, to, courts, cooldown}` when no league
stands, the alarm is below 60, the declaration's own alarm
(`diplomacy.declaration_alarm` — the single source `declare_war` applies)
would carry it to 60 or more, and some court qualifies. The declare-war
objection fires on it below the old >50 arm, and speaks conditionally while
the courts' cooldown runs.

**Surfaces.** The dissolution notice and event (`league_spent_clause`); the
`coalition_dissolved` log dict carries `alarm_spent: {from, to}`, and in the
spend arm `courts_at_war` is `[]` (the IQ-2 read runs mid-ratification); the
campaign-log one-liner; the threat label `league_spent`; the cooldown-ended
notice below 60; the Balance-of-Europe COOLDOWN `headline_note` (not under the
collapse); the war-room gate line. Levers: `THE_LEAGUE_SPENDS_ITS_ALARM`,
`TALLEYRAND_READS_THE_PROJECTION` — both False reproduce the pre-IQ-3 game
byte-for-byte.

**Review-round amendments (September 14, 2026).**
- `diplomacy.UNILATERAL_PEACE_REASONS` (`treaty_break`): a war or truce ended
  without a signature still ejects the member (PT-J1) but never spends.
  `break_treaty` maps a broken ARMISTICE to PEACE, and a repudiation must not
  buy half of Europe's alarm.
- `WorldState._eliminate_nation(nation, by_treaty=False)`: the settlement
  cession, the carve and the bilateral cession pass `True`; the battlefield
  capture never does.
- `add_threat` stamps `applied` on a row when the 100 cap clipped it.
  `league_spent_alarm` halves `before − applied` and adds the requested amounts
  back: `after = min(before, pre // D + requested)`. The result is the same in
  every pair order.
- `coalition.treaty_in_flight(world, courts)` is a transient context manager,
  never serialized, that names the courts signing in a ratification. Both
  settlement ratifiers open it, and the spend arm's `courts_at_war` leaves out
  only those courts.
- `qualifies_for_coalition(..., relation_shift=0)` /
  `get_qualifying_nations(..., relation_shift=0)`: the projection counts courts
  after the declaration's own indirect relation cost
  (`diplomacy.declaration_relation_penalties`). It returns None while a league
  against the aggressor stands or brews (an eclipse league does not silence
  it), and it needs a qualifying court besides the declaration's target.

## 43. The Cabinet is visible (IQ-4, landed September 14, 2026)

**One source.** `diplomatic_dialogue.mission_status(world)` is the only reader
of a running mission. It returns the type and target display names;
`effect_per_turn`, the skill-scaled figure the tick writes; `drift_per_turn`,
from `diplomacy.relation_drift_step`, the decay's own step; `net_per_turn`; the
relation and its descriptor; the pause state and its reason; and
`remaining_kind`/`remaining_turns`/`remaining_note` from
`project_mission_turns`. It also returns `dp_spent`, `recall_command` and, for
COURT, `favour_now`/`favour_cap`. It returns None unless `mission_is_live`.

Every surface reads it or `mission_effect_text`, and none computes a figure of
its own:
- the Strategic Ledger's `cabinet` block (`ledger.build_cabinet`), which
  renders above the Orders tab's rows and never as a row in `orders`;
- the notice rail;
- the help block;
- the Talleyrand tab;
- the wizard's effect text.

**Endings.** A mission ends in one of these ways:
- A relation mission completes on the tick its write lands on the ±100 clamp
  (MS-9b). `_before == _after` never held, because step 4c's decay returned
  100 to 99 in the same turn.
- GATHER completes when its duration runs out.
- UNDERMINE completes when the alliance breaks.
- Any mission can be recalled (free), replaced by a new one, or collapse after
  three starved turns.

Each end calls `record_mission_end` exactly once. That writes a
`diplomatic_mission_ended` log row (reason ∈ ceiling, duration,
alliance_broken, recalled, replaced, starved; GATHER's row carries
`regions_revealed` and `expiry`) and rings the rail's ending beat.
Elimination keeps its own `…_cancelled_eliminated` row. Campaign-log types go
163 → 164.

**The Court's Favour** (PR-D3, ⚠ **RULED, FOR USER CONFIRMATION**).
`court_favour_mod(world, proposal)` adds +2 per funded turn Talleyrand has
spent at the target's court, capped at +10. Conditions:
- The offer is the player's own non-aggression, open-borders,
  defensive-alliance or alliance offer to that court. The type is lowercased
  at the gate.
- The mission is live, and the two courts are not at war.

It is a standalone term outside the composite floor, labelled "Talleyrand's
courting". Because the favour ends with the mission, COURT never completes at
the ceiling: it holds the court until recalled, and the Cabinet and the rail
say so ("the favour stands at +10 and holds while he stays"). COURT's decay
exemption freezes only the courted pair, and only while the mission is live.

**The counsel** (`_recommendation_and_mission`). When no proposal would be
accepted today:
1. `_mission_counsel` prices the two relation missions against each other on
   the best *offered* cooperative treaty still below ACCEPT.
2. The price comes from `forecast_mission_to_accept`, which steps the tick's
   own arithmetic on `acceptance_relation_term` (the acceptance formula's
   relation term, single source). The courted pair is exempt from drift and
   the favour is added. It is a forecast ("≈"). Its constant terms are the
   formula's own `relation_free_score`, rounded ONCE per step as the formula
   rounds. Measured against real ticks, 674 of 674 match, over odd and even
   relations at skills 10 and 5. (The first cut double-rounded every odd
   relation.)
3. The rule picks the road with the fewest DP, ties going to fewer turns.

When COURT wins, Talleyrand recommends it with both roads' turns and DP, or
says "Relations with X can do no more for this treaty" when improving never
gets there. Otherwise the Improve counsel stands, and names the quicker Court
road beside it. `get_diplomatic_preview` carries the named mission as
`recommended_mission` (display-only, GR6).

The original cell was an alliance leap past relation's cap. It is unpayable in
play: a courting France holds 3 DP, and the leap costs 4–6.

**Rail.** There is at most one `diplomatic_mission` row:
- An event beat (begun, paused_transit, blowback, completed, recalled,
  collapsed, eliminated) re-issues the row, so it gets a new id and one bell.
- A standing turn refreshes it in place.
- A resume after a starved pause re-issues it, so its HIGH priority can fall.

The Recall button (`action_command`) rides every live beat except
`paused_transit`. The EC-Q transit gate refuses mission orders while
Talleyrand carries a proposal, so `mission_status` blanks `recall_command`
then, and the Cabinet's [Recall] hides.

**Also:**
- REASSURE_ALLY is offered only at ALLIANCE; at DEFENSIVE_ALLIANCE, IMPROVE
  (+8 at the same 1 DP) strictly dominated it.
- A counter-offer return restores Talleyrand
  (`world_state.COUNTER_OFFER_RETURN_RESTORES_HIM`). The live mission resumes,
  and a failed counter no longer strands him IN_TRANSIT.
- A launch never raises "Diplomatic Action Rejected".
- A mismatched or completed recall is refused by name.
- The confirm and messages name the court (R7).
- Settlement gratitude reads the offer's type in either case.

Every lever, set False, reproduces master `7bbf82b8` on its own surface. Zero
new serialized fields.

**Review-round amendments (September 14, 2026).**
- **COURT.** At WAR it is *suspended*: no favour, the relation work goes on,
  and the favour returns at the peace. The note never advises a recall. At
  ALLIANCE it says the alliance is signed. The courted pair is spared decay
  only; below −10 it still thaws (`COURT_EXEMPTION_KEEPS_THE_THAW`).
- **Net per turn** = the clamped effect plus the drift at the relation the
  effect leaves. The morning progress line reads after the same tick's decay
  (`MISSION_PROGRESS_READS_AFTER_DRIFT`).
- **UNDERMINE.** The note states the downgrade ladder: an ALLIANCE falls to a
  defensive alliance, still allied, and the break needs a second run of five.
  The mission ends on the turn step 13 breaks the pair
  (`UNDERMINE_ENDS_ON_THE_BREAK`, `_complete_undermine_if_broken`). Its end
  record and recall line read the target↔ally pair. The Cabinet names his own
  work "a turn from him", never a net.
- **The counsel.** Its COURT sentences state the blowback. Under a hard-reject
  posture it names the posture and when it lifts, and prescribes Improve only
  while relations would still fall short once it lapses
  (`_hard_reject_counsel`).
- **Other surfaces.**
  - A completed record no longer silences Talleyrand's idle nudge
    (`dispatch.IDLE_NUDGE_READS_THE_LIVE_MISSION`).
  - The wizard's cancel row reads `mission_status`.
  - A blowback row falls back to NORMAL on the next standing turn.
  - Chip and rail echoes are humanised.

## 44. Both sides of the butcher's bill (IQ-5, landed September 14, 2026)

**One figure, one name.** In a coordinated battle the report's casualty figure
for a side is the LEAD's own share, and the army's total rides the event. The
two are never shown under one name:
- `casualty_summary["attacker_casualties_scope"]` / `["defender_casualties_scope"]`
  are "own corps" when the figure is the lead's while others on that side bled.
- The event side dicts (`battle_result["attacker"|"defender"]`, which reach the
  enemy-phase action) carry `casualties_scope: "army"` and `lead_remaining`.
- The predicate is the casualty DISTRIBUTION, not `raw != share`: a side that
  fought alone is never labelled, even when the overkill cap or the rubble rule
  makes the two figures differ.
- `CombatExecutor._reconcile_report_survivors(..., atk_distribution=None,
  def_distribution=None)` falls back to `raw != share` for a legacy call.

**Every surface speaks it.**
- The terminal Berthier line: "Casualties: Moore 4,688 | Ney's own corps 2,725".
- The enemy-phase dialog: "Ney's army: 6,814 casualties — Ney's own corps:
  17,275 remaining", and a Casualties line in its Berthier report.
- Co-located stacks are named: "Ney fought with Davout beside him — massed
  effective strength: …", with the ally-loss line.
- The campaign log is bounded by the field (`*_field_before`), not the lead.
- The morning dispatch's `own_mauled` names the man who bled
  (`*_participant_losses`).
- The playtest digest prints both scopes.
- Reinforcement lines are coloured green for arrival, red for a real no-show
  marker, and report grey otherwise.

**Trust names its price** (FA-D23's copy).
- `pair_contribution_breakdown(lead, ally)` returns `{scale,
  relationship_scale, trust_factor, grievance, relationship, trust}`. It is the
  single source: `_pair_contribution_scale` returns its `scale`,
  arithmetic-identical, drift-pinned over 1,000 cells.
- The muster row is branched on cause:
  - the relationship alone keeps "…are at odds; expect about half his weight"
    verbatim;
  - trust alone gives "…his faith in you is spent (trust N); expect half the
    weight he would otherwise bring";
  - both give "…a quarter of his weight".
- The trust number is printed, never the word "Broken" (the card's labels
  disagree between trust 21 and 29).
- `battle_report["trust_note"]` names the man and his committed figures, on
  either side of the field. The enemy's variant carries no number and appears
  only where the player fought.
- The diorama shows a `faith` caption.
- The jealousy card reads the breakdown.
- The coordination percentage stays trust-blind.

**Levers:** `CombatExecutor.BOTH_SIDES_NAME_THEIR_SCOPE` and
`TRUST_NAMES_ITS_PRICE`. Both are display-only (GR6): no mechanical figure
moves. **Routed:** IQ5-R1, splitting the pool by committed bodies
(`BUG_FIXES.md`).

**Review round (September 16, 2026; `BUG_FIXES.md` §Both Sides of the Butcher's Bill → THE IQ-5 REVIEW ROUND, IQ5-RV1..RV9).**
- **Every faith sentence is RELATIVE.** `_faith_share_clause(trust_factor)` —
  "he brought half what he otherwise would" — is the one clause behind both
  diorama captions and the enemy trust note; `trust_factor` is the ratio of
  what he committed to what he would have committed with his faith intact, so
  it is true whatever the relationship or grievance also did. Never
  `weight_phrase(scale)` under a trust-only sentence: that blames trust for
  the quarrel's halving.
- **The jealousy card prices the grievance's increment.**
  `pair_contribution_breakdown(lead, ally, without_grievance=True)` reads the
  pair without the grievance off the same single source; `_standing_cost_detail`
  branches on the difference — NONE when the scale falls to 0, "quarrel or no
  quarrel" when an already-Hostile pair is unchanged, the lost goodwill when
  a Friendly pair drops from 1.25 to 1.0, else the IQ5-8 arm.
- **One display function for every reinforcement name.**
  `CombatExecutor._reinf_name` humanises with `BOTH_SIDES_NAME_THEIR_SCOPE`
  up and is the identity down (IQ5-10's arrival rename now sits behind the
  lever). The prose lists are built beside the raw lists that key the
  distribution lookups and dedupes.
- **The co-located ATTACKER is named** when nobody arrived ("Mack fought with
  Archduke John beside him — …", "Mack's supporting ally lost …"); the arrival
  arm keeps the literal CO-6 / Session-66 strings.
- **The realised loss is one map.** Share + the rubble `take_casualties`
  zeroed, read after the loops and before pursuit/capture/retreat, feeds the
  ally-loss line, `*_participant_losses` and the diorama together.
- **A lone side carries one figure.** When the rubble rule or the overkill
  cap destroys a corps that fought alone, the executor stamps display-only
  `applied_casualties` on its event dict (`<side>_applied_casualties` on the
  log event), rewrites the description's phrase and reconciles the report;
  the dialog, the terminal and the log one-liner prefer it on a LONE side
  only. The mechanical `casualties` never move.
- **The enemy-phase colours follow the side** (`IQ5_COLOUR_BY_SIDE`): keyed
  on the battle's attacker nation, never on prose; "ARMY DESTROYED!" is red
  when the destroyed defender is France's.
- **The diorama's faith caption sits under the corps**, outboard, wrapped in
  a 150 px block-local width; the shelf never reads it.
- **`lead_remaining == remaining` by construction** (both are the lead's
  post-battle strength; pursuit updates both) — IQ5-2's fix was the label.
- **One `_join_names`**: `backend.game_logic.battle_report._join_names`.

## 45. Europe speaks its mind (IQ-6, landed September 16, 2026; built September 14)

**The narration was never silent — the instrument was deaf (PR-X4).** The
Stage-F routine intent lines (`intent_hardens` MEDIUM, `intent_eases` and
`intent_movement_tail` LOW) are ordinary dispatch rows. The driver's rail
printed HIGH and CRITICAL only, and nothing else of `diplomatic_events` reached
`digest.md` or `digest.jsonl` — 30 of 122 diplomatic rows on the commanded
historical arm, 39 of 148 on ulm. The producer fires on every board: 8 unique
routine lines on the ambient historical run (the floor pin), never more than 2
a dispatch (the ceiling pin that already stood).
- `tools/playtest_driver.py`, lever `THE_DIGEST_READS_THE_WHOLE_DISPATCH`:
  every row is recorded in the jsonl as `dispatch_row` (`dtype`, `priority`,
  full `text`), outside the rail cap; the three Stage-F types print as
  `- COURTS: <text>`; one `- DIPLO +N medium/low (<types>)` tally a turn
  counts the MEDIUM/LOW rows not printed; `meta.json` carries
  `dispatch_type_counts`. Lever False = the pre-IQ-6 digest, byte for byte.
- `tools/ai_v_sweep.py` `derive_metrics` returns `routine_intent_lines_total`
  (deduplicated on type, `queued_turn` and vars).
- No backend change: `BASELINE_SERIES` and M1–M7 are identical by
  construction.

**The volte-face fires on the ordinary route.** §3.6-4's predicate demanded a
courtship to relation 40 inside 15 turns of the peace. From the boot relations
(−80) the game's own best lever — Improve Relations at Talleyrand's ×1.5, plus
the thaw — reaches 40 at best 16 turns after the peace, so a perfect player
stood at 29 when the door closed; and the "defeat still shows" clause's
exhaustion arm could never overlap the courtship (R49 zeroes a court's
exhaustion at the peace that ends its last war, and the coalition tick decays
it 5 a turn at peace, so a mark of ~70 is under 40 within ~6 turns). Four
rulings in `backend/game_logic/emergent_designs.py` and `ai_diplomacy.py`,
each behind its own lever (False = the prior predicate, byte for byte):
- **V1 `THE_WINDOW_FITS_THE_COURTSHIP`** — `VOLTE_FACE_WINDOW` 15 → **20**
  (`VOLTE_FACE_WINDOW_BEFORE_IQ6 = 15`; ceiling `VOLTE_FACE_WINDOW_CEILING =
  25`, pinned: Austria's routine ladder alliance landed 25 turns after the
  war, and a window of 26+ would announce it as a volte-face).
- **V1b `THE_SEPARATE_PEACE_ENDS_THE_WAR`** (found while building) — a
  BILATERAL peace never counted as a defeat: `exited_turn` is stamped only
  when a court leaves the whole war, and after Pressburg Austria stays at war
  with Bavaria and the Kingdom of Italy, so `_war_with_ended_recently` read
  "not recently beaten" forever. `_war_end_turns` now asks the pair's own
  `diplo_key_meta[pair]["resolved_turn"]` first.
- **V2 `THE_VOLTE_COURIER_IGNORES_ROUTINE_COOLDOWN`** — P-VolteFace passes
  `skip_nation_cooldown=True` to `_is_on_cooldown`; the alliance TYPE
  cooldown, the 12-turn `{nation}|volte_face` cooldown and
  `_has_pending_proposal_from` still hold. (The nation key is shared by the
  acceptance and rejection cooldowns, so a rejected routine ask no longer
  holds the courier either; a rejected alliance still does, through its type
  key.)
- **V3 `THE_DEFEAT_IS_THE_SOIL`** — the exhaustion arm is RETIRED under GR9;
  the defeat shows on the map only (homeland soil in the hegemon's bloc's
  hands). The promise is struck from `AI_INTENT_SPEC.md` §3.6-4 and §18 with
  a dated note. Re-open condition: a row that records the war's OUTCOME on
  the war instance, under a user ruling on the zero-new-serialized-fields
  contract.
- **V4 `VOLTE_FACE_SPEAKS_ITS_MIND`** — `volte_face_failing_clauses(world,
  power, hegemon, *, exhaustive=False)` is the single source (it stops at
  the first failure in the old read order, so `volte_face_receptive`'s
  boolean is byte-identical — pinned on a 1,152-cell identity grid);
  `volte_face_courtship` gives an ints-only view (relation, floor,
  `last_signing_turn`, `turns_left = end + window − 2 − turn`: the
  diplomatic phase runs before `advance_turn` and a court's letter is
  answered the turn after it is written, so it counts the courting ticks
  that still land in time); `volte_face_counsel_line` is the one sentence
  both surfaces print — Talleyrand's per-court counsel
  (`diplomacy._recommendation_and_mission`, priced by the new
  `forecast_relation_to`, the relation half of `forecast_mission_to_accept`)
  and the war room (`diplomatic_advisory._assess_situation`'s "open door"
  block, majors only; `context["volte_openings"]` exists only when a door
  is open, so the lever-down payload is key-for-key the old one). When the
  relation cannot reach 40 in time the line says so rather than promising it.

**Measured.** Bilateral peace through the real `_ratify_treaty`: receptive
exactly at the forecast turn; the courier proposes that turn (V2 down: held two
turns by the routine cooldown); the alliance signs through the conflict confirm
with exactly one `volte_face` event and one dispatch. Uncourted: never. Window
15: never (relation 35 when it closes). The committed courting script
`tools/playtest_scripts/volte_court_austria.json` (`commanded_full40.json` plus
"Talleyrand, improve relations with Austria" from loop 5 — re-issuing the order
is not refused, it replaces the live mission with an identical one) carries
`volte_face` exactly once, turn 21, on every surface; the plain commanded arm 0.

**Gates.** `BASELINE_SERIES` and M1–M7 byte-identical without re-record, with
the reason measured: the ambient board has no France–great-power peace, so the
courier and the ratify hook never reach a changed read, and the counsel is
display only. Zero `.gd`. Pins flipped consciously: five
`test_ai_intent_emergent_designs.py` fixtures now stage the defeat on soil
(they staged it through exhaustion alone; all 43 pass unchanged with V3 down),
and `test_ai_intent_assurance.py::test_volte_face_signed_and_aimed_at_a_third_party`
became `test_staged_exhaustion_tilsit_no_longer_reverses` — the scripted
Russia qualified only through the retired arm (lever down: receptive at t11,
fires at t12; lever up: never). **Routed:** IQ6-D1..D4 in
`DESIGN_REFINEMENT.md`.

## 46. The satellites have a position (IQ-7, landed September 16, 2026)

> **A loyal satellite is the Empire's settled frontier: it pays its tribute, feeds and passes the Grande Armée, marches in France's wars, and holds for France the conquered provinces France hands it. Its loyalty is standing — only a loyal client (60 or more) may petition the Emperor — and a client whose petitions are honoured becomes a bonded one that holds its own position against the ordinary drift without further attention. Refused or ignored, it spends that standing until a rival court can buy it.**

**Why the row moved.** After IQ-3 a commanded France is at PEACE from turn 5 to
turn 29, and at peace a satellite's only live loyalty term is the −2 drift
(the +2 shared-enemy term dies with the war, grip is dormant above 30, the
relation term was 0 because nothing ever wrote a France–vassal relation). A
well-played France therefore lost 2 / 3 / 3 of its three satellites by turns
30–33 on three seeds, and the only vassal decision it ever saw was the
rebellion modal 0–2 turns before the break.

**The Client's Petition** (`backend/game_logic/vassal.py`).
- **Standing.** A satellite may petition when loyalty ≥ `PETITION_LOYAL_MIN`
  (= `CONTRIBUTION_LOYAL_MIN`, 60), `PETITION_GRACE_TURNS` (5) after its
  `created_turn`, `PETITION_INTERVAL_TURNS` (8) after its last petition
  (`petitioned_turn`, stamped at issue whatever the answer), with no province
  disrupted, no remission running, and a lord who can pay `PETITION_DP_COST`
  (1). At most one petition per LORD per turn, in sorted tag order.
- **The ladder** (`petition_subject`): THE PROVINCE — a grantable province
  (`list_grantable_regions`, `grant_cooldown` clear), preferring one in the
  satellite's own authored `acquire_regions` deck (`in_design`, with a
  `design_note`), else the richest; THE RELIEF — when
  `forecast_vassal_loyalty` is negative, `REMISSION_COLLECTIONS` (8) tribute
  collections forgone, priced at `vassal_tribute_owed × 8`. A landless or
  wholly-disrupted client has nothing to be relieved of and asks nothing.
- **Prices** (`petition_terms`, the single source the popup, the card and
  the executor all read): GRANT — the province through
  `grant_region_to_vassal` (its own 1 DP and worth-scaled gain), or the relief
  (1 DP, `PETITION_RELIEF_LOYALTY` 10 × `get_authority_lever_multiplier`,
  `remission_left = 8`); both add `PETITION_RELATION_STEP` (+20) to the
  vassal→lord relation, capped at `PETITION_BOND_CAP` (40) — step 6's
  `relation // 20` turns each step into +1 loyalty a turn, so two honoured
  petitions cancel the satellite drift. REFUSE or LAPSE
  (`AN_UNANSWERED_PETITION_IS_REFUSED`) — `PETITION_REFUSAL_LOYALTY` −10
  (never blunted) and −20 relation; no DP; never an AI-3 ladder refusal
  (`diplomatic_refusals`, the rejection cooldowns and the schemer record are
  untouched). *(Amended by the review round, September 18, 2026.)* Every answer
  runs ONE re-validation ladder, `_grant_verdict`: row → lord → THE DEED →
  the fixed subject → DP. A petition whose row is gone or whose lord changed is
  WITHDRAWN on both arms (no charge, no penalty); a province petition whose
  region the vassal ALREADY holds from the lord's own `granted_regions` (the
  typed `cede` or the wizard) is **FULFILLED** on both arms — the capped bond
  step once, no DP, no second loyalty gain, never a refusal
  (`petition_is_fulfilled`, lever `THE_DEED_HONOURS_THE_PETITION`); a province
  lost OUTSIDE the lord's hands (fallen in war, not to his marshal's estate or
  another of his vassals) is withdrawn on the refuse arm; a lord who cannot pay
  1 DP, or whose own doing made the province ungrantable (an estate, a cooldown
  from ceding another province, ceded to another client), has NOT answered (a
  province the WORLD made ungrantable — lost contiguity — is withdrawn free) —
  the Grant press **STANDS** (`THE_LORD_PAYS_TO_GRANT`): the petition stays
  pending with the question re-carried and Grant disabled with its reason, so
  only Refuse or the lapse can end it (an AI lord's `stands` is a refusal at the
  same price, GR5); a relief whose live tribute is 0 is withdrawn on the grant
  arm only (`A_RELIEF_OF_NOTHING_IS_WITHDRAWN`). Endowing a marshal with the
  petitioned province and letting it lapse is a refusal.
- **GR5.** `process_vassal_petitions` walks every lord; a player lord gets
  the letter through `deliver_ai_proposal`; an AI lord resolves in place —
  grants when it can pay and (for a province) the region is not in its own
  active acquire design, else refuses at the same prices. Latent on the
  shipped boot (no AI lord holds a satellite); pinned on a staged transfer.
- **State:** two vassal-row keys only — `petitioned_turn`, `remission_left`
  (consumed by `process_vassal_tribute` itself, so "8 collections" is exact).
  `process_vassal_loyalty` writes neither. No model field.
- **One tribute source.** `vassal_tribute_owed(world, vassal)` — effective
  income over the vassal's undisrupted provinces × `tribute_rate`, 0 while a
  remission runs — is read by the engine, the strategic ledger's projection,
  `diplomatic_ledger._build_vassals` and `get_diplomatic_preview`'s
  `vassal_tribute` mirror (which had omitted the EC-W1 disruption skip).
- **Levers** (HOST_RULE_ACTIVE idiom): `THE_CLIENT_PETITIONS`,
  `AN_UNANSWERED_PETITION_IS_REFUSED`, `COURTING_SPARES_THE_LORDS_ALLIES`,
  `THE_WAVERING_LINE_IS_HONEST`. Down, no petition is issued and no display
  key is stamped; a stored remission is still honoured and a pending petition
  can still be answered after a load. The constants are ⚠ FOR USER
  CONFIRMATION (in-band tunable).

**The transport** (`ai_diplomacy._build_client_petition_dialogue`,
`mailbox_payloads.client_petition_clauses`, `diplomatic_executor`). The
petition rides the `incoming_proposal` dtype with exactly two options,
"Grant the petition" / "Refuse the petition" (multi-word — a bare "Grant" would
label-match `grant Ney a rente`), Counter refused free and left pending; the
popup shows `is_petition` with the clause lines (design note, grant line,
refuse line, lapse line) and no acceptance hints; `PROPOSAL_TYPE_DISPLAY`
"A Client's Petition"; `deliver_ai_proposal` titles it "Petition from
{court}". A petition still pending at `end_turn` lapses through
`refuse_petition(how="unanswered")`. The campaign log gains
`client_petition_answered` (164 → 165, conscious): *"The Kingdom of Italy's
petition for Tyrol — granted."*, *"Switzerland's petition for relief from
tribute — left unanswered, refused."* The Vassals ledger card shows standing,
next petition, the bond and "Tribute remitted: N collections".

**Riders.**
- **R1** the "wavering" crossing line no longer promises regiments the
  satellites do not have (no boot satellite has a marshal): it names what the
  60 boundary costs NOW — the standing to petition — and appends the
  regiments clause only when the lord fields a marshal whose
  `original_nation` is the vassal (VS-4 Rule 1b is then real).
- **R2** a lord's ALLIES stop courting its satellites
  (`courtier_is_the_lords_ally`, beside the WO-8 guards — Spain courted
  France's Switzerland at turn 29 on marengo).
- **R3** the rebellion modal's Garrison option says what the handler does:
  "2 AP → Loyalty +10 now. No corps moves: a corps standing in {capital} adds
  +2 every turn."
- **R4** the driver's LEDGER row carries `vassals Holland 88 · Kingdom of
  Italy 84 · Switzerland 71` (`THE_DIGEST_SEES_THE_WEB`; the digest had shown
  0 of 67 loyalty ticks), and `--client-petition {grant,refuse}` answers the
  petition (absent → mirrors `--diplomacy`).
- **R7, fixed in passing:** the rail notices for a rebellion, a break-free and
  a VS-6 defection printed the raw tag ("KingdomOfItaly has rebelled"); the
  dispatch templates now use the PR-2 `_display` suffix ("Sire — the Kingdom
  of Italy has rebelled against France.").
- **IQ7-X4, fixed while integrating:** `main._respond_to_dialogue_sync`'s
  PL-14 safety net minted a fallback `proposal_result` ("Diplomatic Action",
  outcome derived from the message — REJECT for a GRANTED petition) whenever
  the handler's own popup had already been delivered by the first response
  build; the mint is now guarded on the response's own `proposal_result`,
  for every handler (`offer_vassalage` measured the same on the wire).

**Correction to §17:** the defection cascade sets loyalty to **0** on
success; the "−20 loyalty" there was wrong.

**Routed (Golden Rule 9):** VD-C "The Contingent" (`VASSAL_DEEPENING_SPEC.md`
§9), IQ7-D2 the Suitor (declined, re-open condition), IQ7-D3 Holland's
unpayable design, IQ7-X1..X3, IQ7-X5 (`BUG_FIXES.md` §IQ-7).

**The review round (September 18, 2026) — the rules that changed.**
- **Shown = applied at every read.** The subject and region are frozen at issue; ONE
  arithmetic (`_price_petition`, behind `petition_terms` and `reprice_petition`) re-prices
  the FIXED subject from live state at `/pending_envoy`, `/mailbox/activate`, the safety
  valve, the delivery passthrough and inside the answer handler immediately before the
  grant — never the ladder, so the subject can never change under the player. The loyalty
  gain is clamped to the ceiling in the copy ("+6 (to the 100 ceiling)").
- **The province price names its parts, with its sign** (`province_grant_price` /
  `province_price_line`): income forfeited, tribute returned at today's rate, the ES-2
  occupation cost relieved, the ES-3 surcharge delta — the net is drift-pinned against the
  ledger's applied net (stability 25 / 40 / 60 / 80 / 100 = +63 / +30 / −10 / −35 / −35). A
  freshly conquered province is a GAIN to grant and the line says so.
- **Vocabulary.** The vassal→lord relation term is the **bond** on every surface (never
  "drift", which is the −2 satellite term, never "standing", which is eligibility only);
  refusal and lapse lines quote the APPLIED, clamped figures.
- **The card's verdict** is the producer's own gate ladder (`petition_gate_verdict`):
  "may petition" only when every gate passes, else the blocking reason; the remission
  countdown counts the collection the card's turn has not yet taken.
- **The transfer sheds the remission.** `transfer_vassal` (VS-5 / VS-6) pops
  `remission_left` and `petitioned_turn` (`THE_TRANSFER_SHEDS_THE_REMISSION`); the new
  lord's next collection is paid in full; `created_turn` is not reset.
- **The lapse is priced aloud — display only** (DECIDED: no mount over a settlement offer
  or an ultimatum, no delivery re-ordering): the rail body, the end-turn receipt, the
  `vassal_loyalty` event ("−13: refused petition, satellite drift, …"), LAPSED ENVOYS,
  the end-turn gate's `pending_lapsing_petitions`, the campaign-log tails.
- **The matter noun is an addressee** (`dialogue_routing.MATTER_NOUN_FAMILIES`,
  `matter_mismatch_refusal`, both seams): a typed line naming a petition / ultimatum /
  settlement while such a dialogue is QUEUED and the active one is not of that family is
  refused, naming the court and Envoys; the petition's own vocabulary
  (`PETITION_ANSWER_KEYWORDS`) answers it when it is current; a negated or deferred answer
  never grants.
- **The School of War issues no petitions** (`petitions_live`, ONE predicate read by the
  producer, the card keys and the ledger gate). **A dead id-bound popup is never
  delivered** with no dialogue pending (`main._popup_dialogue_is_current`, IQ7-X5).
- **Passes 2 and 3 — the typed answer to a client petition is a CLOSED grammar that FAILS
  CLOSED** (`dialogue_routing.petition_plain_answer`, lever
  `A_PETITION_IS_ANSWERED_PLAINLY`). A typed line answers a CLIENT petition only if every
  token is in a literal allowlist written beside the function: the address (`sire`,
  `please`, the diplomat words — `Talleyrand, grant the petition` answers), the petition
  nouns, the petition's OWN court forms, the petition's OWN subject (province: `province` +
  the region; relief: `relief`, `remission`, never `tribute`), seventeen function words,
  seven emphasis phrases, and answer words that all name ONE action; the auxiliaries
  answer in STATEMENT order only (`shall` / `will` after `we` / `i`; `do` after `we` / `i` or
  before an answer word), so no question can be built from the list. It is never derived
  from `_ANSWER_FILLER_WORDS`. A line that is answer-led or diplomat-addressed but not plain
  — or comma-addressed to a non-marshal, or a diplomat-addressed `no` — is re-prompted IN
  PLACE (`petition_line_reprompt`) — nothing is ever mounted over a
  current petition by a line that was trying to answer it. An unaccepted phrasing is a
  re-prompt by design; the only defects this surface can have are an execution the line
  does not plainly give, a displaced petition, or a regression of a pinned positive.
- **A question is never an answer, for any dialogue** (`A_QUESTION_NEVER_ANSWERS`): a line
  with `?`, one `is_question` flags, or one carrying a subject-auxiliary inversion anywhere
  (`then shall we ratify`) resolves nothing at `match_dialogue_answer` or the free-text
  button route; exact ids, digits, exact labels and a line carrying every word of a
  question-shaped LABEL are exempt. The DEFERRAL half
  for non-petition families (`accept the offer later` still signs) is `BUG_FIXES.md`
  IQ7-X7, owned by CR-6 proper and pinned as current behaviour.
- **The matter guard reads the table** (`THE_MATTER_GUARD_READS_THE_TABLE`): at the
  `/command` router seam it fires only for an ANSWER-SHAPED line, so a typed order that
  merely contains the noun (`send ultimatum to Austria`) reaches the executor; a verb the
  ACTIVE dialogue offers is never claimed for a queued petition; with a client petition
  current the COURT guard speaks first. **The button route reads the court**
  (`THE_BUTTON_ROUTE_READS_THE_COURT`) when — and only when — it is sent free text.
- **A change in the world withdraws; the lord's own doing stands.** `_grant_region_refusal`
  classifies the refusal: an estate (the lord's doing) → `stands`, priced at the lapse;
  lost contiguity → `withdrawn`, free on Grant, Refuse and the lapse. A moot petition quotes
  no price it will not charge (`lapse_forecast` decides the popup's lines). The Vassals
  card reads "petition on the desk" (`standing_key = "pending"`) while the ask is pending.
- **The suite's save floor.** `tests/conftest.py` sets `INK_IRON_SAVE_DIR` at import, so a
  module-scoped fixture or a child process can never write the developer's `saves/`.
- **⚠ FOR USER CONFIRMATION:** the seven-seed ambient re-read breaches the contract's ±1
  passive-France band on eylau (3 against 6 at turn 40; memo §3).

## 47. The harness tells the truth (IQ-8, landed September 18, 2026)

> **A measurement that cannot name the tree, the platform, the seed and the board it ran on is not a measurement. The driver records what was REQUESTED and, separately, what was RESOLVED; a table may cite only an archived run whose record matches the row; and two processes on the same board write the same digest whatever their hash seed.**

**Why the row moved.** PR-D4 (a published commanded-arm table of 20 / 24 / 22
provinces that measured 23 / 24 / 21 on the next machine at "the same commit")
could not be root-caused after the fact: no `meta.json`, no digest and no
driver stamp existed for the published side, and the stamp the driver did
write (`driver_revision`) hashed raw bytes, so one commit carried two stamps on
a CRLF and an LF checkout. PR-X5 was wider than filed — the record wrote four
REQUEST values as if they were resolved (`scenario` empty on a default run,
`seed` on a `--from-save` run a hybrid of two seeds, the board environment the
driver popped and `backend.main`'s `load_dotenv()` put back, "160 of 160 AP"
the script's line count). Measured first: the hash seed does NOT move the board
(commanded 12 and 40 turns and ambient 20 turns at `PYTHONHASHSEED` 0 / 1 /
12345 are the same game; the one order-dependent site was a naval display
walk).

**Provenance** (`tools/playtest_driver.py`, lever `META_NAMES_WHAT_WAS_PLAYED`).
`meta.json` carries four blocks: `requested` (the flags as typed), `resolved`
(read off the booted world — campaign seed, `dice_label`, scenario name, map,
region count, player nation, starting turn, and `env`, the six `SOVEREIGN_*`
/ `LLM_MODE` / `DEBUG_MODE` values read AFTER `import backend.main`), `platform`
(Python version, OS, `pythonhashseed`) and `engine_revision` (`git rev-parse
HEAD` + a `dirty` flag scoped to `backend/`, the driver and the maps folder —
`"unknown"` on a checkout without git — plus `content_hash`, an LF-normalised
sha256 over `backend/**/*.py` and the three map / scenario JSONs). The digest
header prints `resolved` and `platform`. `driver_revision` is LF-normalised
(`THE_REVISION_IGNORES_LINE_ENDINGS`): `4094eb4a` = `9f00997bc24a` on either
line ending; the `iq7-*` archives' `edb714263e80` is the CRLF stamp of a tree
whose LF stamp is `56e82b4305cd`.

**The from-save seed rule** (`THE_SAVE_OWNS_ITS_SEED`). A `--from-save` run
plays the SAVE's campaign seed; `requested.seed` is `""` when no flag was
given ("the save decides"); an explicit `--seed` on a from-save run drives the
module dice only, is recorded as `resolved.dice_label` beside
`resolved.campaign_seed`, and prints a WARNING naming both seeds in the digest
header. No silent hybrid.

**The board environment** (`THE_DRIVER_SETS_THE_BOARD_ENV`). The driver SETS
`SOVEREIGN_SCENARIO=""`, `SOVEREIGN_SMOKE_START=""` and `SOVEREIGN_MAP=europe`
(their no-op values) and boots `SOVEREIGN_SEED` from its own argument instead
of popping them, so a repo `.env` cannot reshape the board through
`load_dotenv()`; `resolved.env` records what the backend actually read. The
`PYTHONHASHSEED` re-exec pin stays.

**Action points** (`THE_HARNESS_COUNTS_ACTION_POINTS`, class
`ActionPointMeter`). `counters.ap_available` / `ap_spent` are read off the
`/ledger` `actions_remaining` field the driver already fetches at turn start,
before `end turn` and after every POST; `cmd_refused` counts refused commands.
Measured on the three IQ-8 commanded archives: **85 / 80 / 76 of 160** spent
and **52 / 51 / 57 of 200** refused (the September-12 81 / 77 / 75 reproduce
from the archived warning text).

**Determinism across hash seeds.** `naval._tracked_links_for` walks
`sorted(get_sea_link_pairs(world), key=_link_key)` — a pure ordering fix with
no lever (the row's one exception, recorded): the walk had followed a
frozenset's iteration order, so `link_verdicts_for`, `_emit_verdict_flips` and
the serialized `fleets["__naval__"]["verdicts"]` varied with the hash seed and
one `strait_open` rail line moved inside a turn. Two commanded subprocesses at
`PYTHONHASHSEED` 0 and 1 now write byte-identical `digest.jsonl`
(`TestCrossHashSeedSentinel`); the sort is order-only (a 40-turn run before and
after holds the same 729-line multiset, France 28 both).

**The table rule** (`docs/PLAYTESTING.md`, pinned by `TestTheTableRule`).
Every measured table carries platform, commit, hash seed, flags and the
archived digest names; a row whose archive's `meta.json` does not match it, or
which has no archive, is marked **UNCITABLE**. PR-D4 closes as *cause
unrecoverable, no archive* with the measured fact that the hash seed does not
move the board; its 20 / 24 / 22 row is UNCITABLE and the IQ-8 row reads
**28 / 28 / 29** (`docs/audits/playtest_digests/iq8-cmd-*`).

**The rotation begins with the campaign** (IQ6-X1,
`battle_report.THE_ROTATION_BEGINS_WITH_THE_CAMPAIGN`). FA-D24's
`_OBSERVATION_COUNTS` is emptied by `reset_observation_rotation()` at the ONE
chokepoint every world passes, `WorldState.__init__` (a census pin says nothing
else constructs a world), so an in-process second campaign prints what a fresh
process prints. **A loaded campaign restarts its rotation** — the counter is
display-only and never serialized (FA-D24's own contract) — exactly as loading
that save in a fresh process would; "rotates within a campaign" holds from the
creation onward.

**The scene-4 positive** (IQ6-D4, `tools/ai_v_sweep.py --script france_soil`).
The scripted arm gains a second schedule that hands Lithuania (a non-capital
Russian homeland province; a lost capital would promote Revanche and shut the
door) to France at `_turn_11`, the reading `emergent_designs._lost_homeland`
makes, so the Tilsit volte-face fires on the ordinary predicate: receptive at
t11, the courier at t12, `volte_face` at t13 aimed at `gulf_and_straits`, on
all three scripted seeds. The `france` arm plays the game it did (the
re-worded negative stays); `run_all` runs both.

**Never do:** cite a figure with no archive; read a request value as a
resolution; hash a source file without normalising its line endings; walk a
set in a display path that is serialized or printed; reset the rotation
anywhere but the world's own creation.

## 48. The keyless parser gate (IQ-9, landed September 18, 2026)

> **The escalation path — the 0.7 gate's live arms, the SDK call, the typed-error ladder and everything the parser does with a live answer — is exercised deterministically, without a key and without a network, by replaying recorded or authored answers at the one seam where our code hands a body to the SDK. The suite is keyless by CONSTRUCTION, not by discipline: every test runs `LLM_MODE=mock` and behind a network guard, and a test that reaches the model anyway asserts the NUMBER of live calls it made.**

**Why the row moved.** The `--llm anthropic` arm was the only check on the
escalation path, it cannot run in CI or without a key, and it was recorded as
NOT RUN by two re-scores. Measured first: `AnthropicProvider._make_parse_request`
(the `stop_reason` truncation discard) and `_post_messages` (the typed-exception
ladder the July-18 SDK migration added) were referenced by ZERO test files —
every "live" test stubbed ABOVE them — and three test ids in two files built
ENV-DERIVED clients that escalated to the real API on any checkout whose
`.env` said `LLM_MODE=anthropic` (3 of 3 with `provider_name: anthropic`
before the floor; 0 after).

**The seam.** `AnthropicProvider.bind_sdk_client(client)` — the ONE production
addition. `_client()` is unchanged and only reads the attribute the seam sets,
so live behaviour cannot change; a fake client's `messages.create(**body)` is
the last line of our code before the SDK, and exactly what the recorder
wraps, so replay and record share one shape. Replay support =
`tests/_parser_replay.py`; cassettes = `tests/data/parser_cassettes/`
(17, ALL `provenance: "authored"` from the prototype's measured shapes, with
`MANIFEST.json` and `phrasings.json`); the recorder =
`tools/record_parser_cassettes.py` (opt-in `--record`, refuses without a key
after its own `load_dotenv`, `--dry-run`, `--refresh-drifted`, field diff,
no-overwrite default). **The suite never records; the user promotes cassettes
to `recorded` in one run (~17 calls, ≈ $0.07).** `parser_eval.run_corpus(...,
parser=None)` + `--replay` (default byte-identical) drive the four `live_only`
corpus rows through the same tier.

**The T0 floor** (`tests/conftest.py`): `LLM_MODE=mock` as a MODULE-LEVEL
assignment (`backend.main` builds its parser singleton at import, before any
fixture runs) plus an autouse per-test pin, and the network guard installed at
conftest import — both `httpx` transports and `socket.socket.connect`, loopback
ALLOWED (asyncio's Windows self-pipe, the TestClient, the IQ-8 driver's server),
everything else refused. Through the SDK the guard surfaces as
`APIConnectionError` with the `RuntimeError` as `__cause__` (the base client
wraps transport exceptions after its retries), not a bare `RuntimeError`. The
census instrument `tests/_escalation_census.py` (opt-in `-p`, never
auto-registered) re-runs the env-derived ids under `LLM_MODE=anthropic` with
the guard up and asserts every env-derived client is mock.

**Rules (each measured):** a cassette miss is a `BaseException` — an
`Exception` miss is swallowed by both catch-alls into a green
`llm_error=True` fallback; the cassette key is `(kind, utterance, world)`,
never the prompt hash (+355 chars the moment one order is in history); prompt
drift is tallied against the manifest and must be acknowledged or fails; every
pin that involves the model asserts the number of live calls; a request's
invariants (forced tool, temperature 0, the model pin, `max_tokens`, no tools
on the Berthier body) are checked on every replayed call.

**What the gate covers, deterministically and keylessly:** the 0.7 gate's live
arms; prompt/body assembly invariants (forced tool, temperature 0, model pin,
max_tokens, no tools on the Berthier body); `_post_messages`'s typed-exception
ladder and `to_dict`; the `stop_reason` truncation/refusal discard; tool_use
extraction and the text fallback; the strategic-verb remap; every
`validate_parse_result` arm on a real result; the parser's consumers of a live
result (`mode`, `key_source`, `flavor` lift, `requested_type` derivation, the
CR-2 retry chain, `llm_error` stamping on success and failure); CR-5
`parse_resolved_to_action` + `route_arm` + both executed arms + the literal
override; CR-5b `flavor_passes_register` on a live string and the
modal-withholding rule; the Berthier `skip_llm` rule; **the number of live
calls per request** on every branch; the SDK's retry count and typed-error
construction (transport tier); the executor dispatch decision for each
replayed row.

**What it does not cover:** whether today's Haiku answers a phrase this way (a
cassette is a witness of one day's answer, or an authored shape); what the
model returns to a prompt that has DRIFTED since recording; prompt quality
(few-shots, rubric wording — the `TestPromptModernization` pins keep those);
the `groq` stub; real network behaviour (timeouts, DNS, TLS — the SDK's);
token cost; the PARSE-NEG refusal arm (terminal BEFORE the provider, already
pinned in mock); anything the mock corpus already covers at ≥ 0.7.

**Measured corrections to the recon, recorded:** S3 (a string tool input) is
REJECTED by `Message.model_validate`, so the prototype's S3 had gone through
the catch-all — `message_from_wire` falls back to `Message.construct` and S3
now measurably takes the no-parse road; "Zorglub, attack Mack" ends in the
CR-2 `unknown_name` clarification (the deterministic addressed-token guard
outranks the model's `marshals: []`), not "Which marshal?"; the recon's sweep
row 22 was INERT BY CONSTRUCTION (the bad-odds modal sets `requires_input`
AND `pending_interrupt`) and now deletes the pair.

**Routed (GR9, `BUG_FIXES.md` §The Keyless Parser Gate):** IQ9-X1 the CR-2
forced retry cannot rescue the word-scan family; IQ9-X2 the fuzzy suggestion
can name a FOGGED enemy; IQ9-X3 a live-road failure stamps `parse_mode:
"mock"`. All three pinned as CURRENT behaviour by name.

**Never do:** record from the suite; key a cassette on the prompt hash; raise
an `Exception` for a miss; ban loopback; put the `LLM_MODE` pin in a fixture
alone (the import-time singleton escapes it); read the repo `.env` anywhere
but the recorder.

## 49. The client pass (IQ-10, landed September 19, 2026)

> **A client surface is proven by a FRAME plus a machine record of that frame, shot
> from the real scene against a payload captured off a staged board — and every
> surface is proven twice, at Interface Scale 1.0 and at 2.0.**

**The instrument** (committed; two commands re-shoot everything):

```bash
.venv/Scripts/python.exe tools/iq10_capture_payloads.py --out <dir>
.venv/Scripts/python.exe tools/iq10_run_captures.py --payload-dir <dir>
```

- `tools/iq10_capture_payloads.py` — REAL endpoint payloads off STAGED boards,
  in-process (TestClient, mock parser, sandboxed `INK_IRON_SAVE_DIR`). Each capture
  records its staging sentence and its own measured FACTS, which the index carries
  beside the frame so a reader can tell what the frame must show.
- `tools/iq10_surface_screenshot.gd` — ONE generic offscreen capture. It instantiates
  the real scene, calls its real entry method (`call` / `api_stub` for the five
  self-fetching screens / `map_stub` for the region panel), sets
  `root.content_scale_factor`, and saves the PNG **plus every visible string, every
  `BaseButton` whose rect lies outside the logical viewport, and every RichTextLabel
  taller than its box**. Windowed (a headless viewport returns no image) and parked
  past the primary monitor; Dummy audio; `UiSettings` shimmed to an in-memory
  `ConfigFile` so the player's own settings are never read or written.
- `tools/iq10_run_captures.py` — the surface table (one row per shot: scene, entry,
  payload, and the sentence the frame is read against), the launch, the
  `SCRIPT ERROR` grep between the harness's own markers, and the index JSON.

**The rules this pass established.**

- **Interface Scale 2.0 is a first-class case, not an afterthought.** The logical
  viewport HALVES (1600×900 → 800×450), and a surface authored at a fixed size does
  not fit. Two of the row's seven defects were this, in two different disguises:
  an early return that skipped `Utils.clamp_centered_panel` (the empty letter-book),
  and a `custom_minimum_size` floor the clamp cannot cross (the diorama).
- **A composed tableau fits by SCALING, never by reflowing.** `clamp_centered_panel`
  rewrites centre offsets and relaxes child height minimums — right for a document,
  wrong for a diorama whose children are placed absolutely in design pixels. The
  diorama scales about its own centre (`_fit_tray_to_viewport`) and is a no-op at 1.0.
- **The ground the backend PRICED is the honest predicate**, not the ground the
  player owns (H1: the region panel now renders the levy wherever
  `recruit_price_here` / `substitute_price_here` is set, which the backend sets only
  where a French corps stands).
- **A sentence the game PRINTS must be a sentence the parser knows** (IQ10-6), and it
  is pinned as a drift test between the producer's copy and the parser's keywords.
- **A payload is a fixture with a date**: re-capture after a backend change or the
  frame renders the old copy.

---

## 50. The hand on the keyboard (row CX, landed September 19, 2026)

**Owning spec:** `docs/COMMAND_EXPERIENCE_SPEC.md` — the gate ruling, the
model ruling, the predictor's measurements and the per-slice landing records.
**Memo:** `docs/audits/CX_THE_HAND_ON_THE_KEYBOARD_2026_09_19.md`.
**Technical record for the parse pipeline:** `COMMAND_ROBUSTNESS_SPEC.md` §10.

### 50.1 The two roads are complements, not substitutes

The chips ARE typed commands (`region_panel.gd` emits the literal string a
player would type), so for most intents both roads converge at the fast
parser — **and a chip removes naming risk, never gate risk.** But each road is
CLOSED on a set the other owns:

* the **typed** road cannot reach the diplomatic family at all — the client
  intercepts 114 keyword forms on the typed path and only there (ruling G1);
* the **click** road has no movement verb it can offer on its own. Every
  movement button in the client is raised by an ambiguous TYPED order, and
  there is no marshal-selection gesture (`grep "selected_marshal"` over every
  `.gd` → zero).

**Measured: 38 intents, TYPED 9 / CLICK 22 / PARITY 7 — and the 22 click wins
are ~6% of issued commands.** A player can complete an ordinary turn typing
only. A player cannot complete one clicking only: the first `move` ends it.

> **The click road wins the catalogue; the typed road wins the turn.** Typing
> owns the army and the question. Clicking owns the cabinet. Build each for
> its own job.

And the asymmetry that decides every close call: **the chips are priced and
the typed verbs are blind.** Every CLICK WINS verdict was won on information —
the levy's live price, the building's yield, the expedition's odds — not on
clicks.

### 50.2 A QUESTION NEVER ORDERS (`clause_guards.A_QUESTION_NEVER_ORDERS`)

`is_question` is the only thing between a question and the imperative inside
it. Five arms, and the reason for each is the sentence that executed:

| arm | rule |
|---|---|
| (a) | `who` / `whom` / `whose` / `why` lead a question on their own — no English imperative opens with them. **Exactly four words**: the corpus pins `when ready then retreat` as a RETREAT |
| (b) | the deliberative openers `what about …`, `how about …`, `is it time to …` |
| (c) | the copular and perfect leads (`is are was were am does did has had`) have no imperative form at all. `have` is EXCLUDED — the causative imperative |
| (d) | **the subject decides** for leads that DO have an imperative form. Stands down before a trailing clause (an inverted conditional) |
| (e) | an UNADDRESSED line ending in `?`. An addressed one keeps its order |

**Deliberately still executing, and stated:** `end turn?` (FA-R4 strips the
`?` on purpose), `Ney, attack Mack?`, `can you attack Mack`, `do attack Mack`.

### 50.3 AN ADDRESS NEEDS NO COMMA (`CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA`)

With no comma the addressee is the leading run of words BEFORE the first order
verb — empty for a genuinely bare order. The run must contain no function word
and no collective (`can you attack Mack` is a polite imperative; `all marshals
attack` addresses the army).

### 50.4 The question desk answers the BOARD, from the seam the mechanic reads

`question_desk.classify_board_question` / `answer_board_question`, lever
`THE_DESK_ANSWERS_THE_BOARD`. Nine kinds beyond the five FACT kinds, matched
AFTER them; `answer_question` is guarded to its own five.

**The rule: every answer reads the seam the MECHANIC reads** —
`_build_economy`, `get_war_score_for`, `get_active_agenda`,
`find_path(passable_for=…)`, `_build_muster_preview` **and its own
`_format_muster_lines` renderer**, `region.can_build`, the levy pricer. A
quoted figure is the applied figure. *"What happens if I attack Mack"* prints
the exact string the order would print, and spends nothing.

### 50.5 ONE source for counsel (`backend/ai/counsel.py`)

`what_can_i_do(world, nation)` is read by the desk's `options` kind, by
Berthier's shrug and by the question router. **Never add a second.** It asks
`MovementExecutor.move_refusal_probe` before proposing a march, reads
`get_visible_enemies`, and never proposes a diplomatic verb — it names the
Cabinet as a door. Before it, the shrug hardcoded `declare war on Prussia` at
a France at PEACE with Prussia.

### 50.6 A question the desk cannot take gets a ROUTER, not the manual

Berthier's sentence, the surface that holds the answer (*"the campaign log
(press L)"*) and the orders that would be carried out — 370 characters against
12,717. A **syntax** question (`how do I attack?`) still gets the reference,
because there it is the answer (`llm_client._SYNTAX_QUESTION_RE`).

### 50.7 ⛔ THE GAME MUST NOT OFFER A SENTENCE IT CANNOT READ

IQ10-6 was one instance. It is now a census
(`tests/test_cx3_the_predictor.py`): every command-shaped string the game
offers — the completer's verb table read out of the `.gd`, and every phrasing
quoted in the COMMAND REFERENCE — is filled with real names from the shipped
board and driven through the real parser **and the real executor**.

**Run it at the EXECUTOR.** `"Davout, hold Ulm"` parses perfectly and is then
refused *"Region 'Ulm' not found"*; a parser-level census calls that green.

### 50.8 The predictor is client-side, session-only, and inside the terminal

* Its only board source is the `/command` response's own `game_state`, whose
  `enemies` dict the backend has already fog-filtered. **No endpoint, no new
  fog surface.**
* History is **never persisted**. 4.7% of archived commands name a marshal
  fogged at boot, and those names execute — a `user://` history would carry
  them into a campaign that never saw them.
* It draws **inside the terminal's VBox**, never on a CanvasLayer, so it
  inherits `content_scale_factor` rather than fighting the layer ladder. IQ-10's
  two P3s were both fixed-size surfaces that failed at Interface Scale 2.0.
* **It never sends.** Tab fills the line; the player presses Enter. The
  tutorial's own rule.
* `MAX_HISTORY` is 50 **because** the walk is prefix-filtered. Lengthening an
  unfiltered walk makes the feature worse (16.3% vs 14.8%); filtered, the same
  change is worth 12.6% → 21.4%. Never change one without the other.

### 50.9 The model follows the question, not the order

Measured: escalation fires on **3.39%** of real play, **0.00%** on a commanded
campaign and **0.00%** on the chip road; **86%** of what it catches is a
sentence the corpus says must be REFUSED; the deterministic chain carries
**twelve times** its measured value (49 `mock_only` rows against 4
`live_only`); and every confident-and-wrong defect sits at 0.90–0.95, above
the gate. **Keep escalation, re-aim it at open-ended questions — the only road
with no deterministic answer — and keep the desk deterministic first**,
because the shipped default is `LLM_MODE=mock`.

### 50.10 The retreat is sometimes a NOUN

`"retreat"` after a determiner is somebody ELSE'S retreat, acted upon — not
an order to run. Only a small set of verbs (`sound` / `order` / `begin` /
`call` / `signal` … *the retreat*) means carry one out, and that set is the
allowlist; everything else falls through to Berthier, which is FA-73's own
recorded ruling. Lever `llm_client.A_RETREAT_CAN_BE_A_NOUN`.

⛔ **The general lesson, and this project keeps meeting it.** The guard this
replaces stated its own failure mode perfectly and then closed it with four
verbs. Seven more phrasings were the same defect one word over, and each
marched a marshal away at confidence 0.90 — above the escalation gate, so no
key in any mode could have corrected it. **When a guard names VERBS, ask what
SHAPE it is really about; and when the shape has a small closed exception
set, invert the allowlist.**

### 50.11 Who was addressed — ONE source, and the comma is the mark

`clause_guards.address_of(text, roster)` is the single source for *who did the
player address*. Both the question guard's arm (e) and
`executor._unbound_addressee` read it; nothing else decides it. Row CX shipped
two rules about the same sentence in one commit and they disagreed — one half
titled AN ADDRESS NEEDS NO COMMA while the other required one, so
`Ney, attack Mack?` fought and `Ney attack Mack?` was swallowed as a question
on 86 of 128 measured orders.

**The rule, in two lines.**

* **A comma or colon MARKS a run as an address.** The player said so; the game
  answers for that run rather than sending somebody else. This is FA-22 and it
  is unchanged.
* **With nothing marked, a run is an address only if it LOOKS LIKE A NAME** —
  after the article and the HONORIFIC come off, one to three tokens, none of
  them a word that cannot be a name, and either a token capitalised as typed
  or a token within one keystroke of a roster name.

**Two things stand down on BOTH arms**, because on both the game has a better
answer than a refusal: the **collective** (`all marshals`, `everyone`,
`someone`, `whoever is closest`) — the marshal-less arm exists to serve it —
and the **interjection** (`Well, attack Mack`, `Ok, retreat`), because a comma
after one is ordinary punctuation and nobody commands an officer called Well.
~~What may appear INSIDE an addressed noun phrase (`Prince of Moskowa`, `the
Bravest of the Brave`) disqualifies a run on the bare arm only.~~ **Superseded
by §51 (CX-R1, September 22, 2026):** a connective BETWEEN two name tokens is
part of the name on the bare arm too, so `the Prince of Moskowa attack Mack`
is claimed — and refused — as its comma twin always was.

The residue is stated, not discovered later: an all-lowercase INVENTED name
(`zorglub attack mack`) is no longer claimed and reaches the marshal-less arm
as it did before row CX. The near-miss that matters (`nay` → Ney) is still
caught at any case.

⛔ **The lesson, one row after IQ-7 wrote it.** CX-1 asked *is this run NOT a
name?* against a hand-written list of grammar words, and English has more
adverbs than that list will ever hold: measured, **256 of 261 cells** —
`quickly attack Mack`, `cavalry attack Mack`, `ok retreat`, `someone attack
Mack` — refused as unknown officers. IQ-7's review round had already written
the rule: *a rule built by stripping what you recognise is only as safe as the
list it strips.* It scoped itself to an irreversible priced answer; **the
scope was too narrow.** A free refusal is cheap per occurrence and ruinous in
aggregate, because it lands on the road the player uses most. **Ask the
question in the direction that fails CLOSED, and where a class must be
enumerated, enumerate a CLOSED class** — the `-ly` adverb is closed by
morphology, not by listing, and that one rule covers the whole productive
family.

⚠ **And the same list under-refused in the other direction.** The verbs a head
is measured against were hand-maintained too, and missing `pull back` and
`recon`, so `Zorglub pull back` ran a whole-army retreat — FA-22's own defect,
still live a year later. **One hand-written list, both signs.** ~~The remaining
27 of 40 belong to CR-6 proper, and the durable fix there is to derive the
list from the parser's routing table rather than widen it again.~~ **Done — §51
(CX-R1, September 22, 2026): the list is generated from the parser's routing
branches and a census keeps the two in step.**

### 50.12 A name the game PRINTS must be a name the game READS

`_question_subjects` carries both the scenario key and the display form,
composed through R7's own chokepoint (`display_names.humanize_entity_name`).
Before CX-7 it carried the key alone, so `can Archduke Charles attack Mack`
**fought** — AP 4→3, five corps moved — while `can Mack attack Ney`, one word
shorter, asked. The commanders the game shows the player were exactly the ones
the guard could not match.

This is the NPC-cluster through-line — *the player names a thing the way the
game printed it and the game acts on something else* — and it is worth
stating as a standing rule: **any roster a guard matches the player's typing
against must hold the form the player SEES, not the form the scenario file
stores.** The display chokepoint already exists; call it.

### 50.13 A pin on a probabilistic outcome is not a pin

Two lever pins in row CX drove an order end to end and asserted on the
footprint. An aggressive marshal's objection to a retreat is a **roll**, so
one of them read a real order as inert whenever the marshal objected, and the
other was green alone and red beside `test_parse_negation` — the review round
found it before a CI run did.

**Where a lever governs a PARSE or a PREDICATE, pin it there**, and keep the
end-to-end arm for the verbs with no roll on them. And note the sibling trap
that produced the first one: an end-to-end footprint can read a real order as
inert for two more reasons — a retreat is free by design (FA-R3), so no AP
moves, and the endpoint re-seats `world`, so a captured reference goes stale.

### 50.14 The client can be DRIVEN, and a census cannot see behaviour

`tools/cx7_predictor_harness.gd` instantiates the real `main.tscn` under
Godot headless, swaps an API stub in before `_ready` can fetch, and presses
real `InputEventKey`s at it — IQ-10's shape, one phase per frame with a hard
limit. `tests/test_cx7_predictor_driven.py` reads its JSON and **skips when
the engine is absent**, so the suite stays green on a machine without Godot.

It exists because CX-3 wrote, in a docstring, that *"there is no headless way
to press Up in this project, and the alternative is no pin at all"* — and
**four confirmed defects were living behind that belief**, with two source
censuses on the very function that held them green about every one. A census
can only see what is WRITTEN. Where a `.gd` behaviour is worth a rule, drive
it; keep the census for the intent.

⛔ **And make the harness faithful before convenient.** The first cut of this
one answered the topology request synchronously, which flipped
`_initial_map_bootstrapped` and handed the boot handler an arm it takes in no
real boot — so a pin **passed with its own fix reverted**. The stub records
that call and never answers it, which is what the real client does.

## 51. The unbound name spends nothing (CX-R1, landed September 22, 2026)

Build contract + landing record = `docs/audits/PARSER_AUTOFILL_ASSURANCE_2026_09_20.md`
§CX-R1 LANDING RECORD. Pins = `tests/test_cx_r1_the_unbound_name_spends_nothing.py`.

### 51.1 An addressed name must take the order, or nothing happens

`CommandExecutor._unbound_addressee` runs for **every** player order, not only
FA-22's marshal-less field family. If the player addressed a name
(`clause_guards.address_of`, §50.11) and that name is not somebody the game
knows who takes THIS order, the executor refuses before any cost, and the
state footprint is empty. Who takes which order (`_takes_this_order`):

| Addressee | Takes |
|---|---|
| one of our marshals (by name, or a typo the parser repaired) | any order |
| the desk — Berthier, or the sovereign's title (`clause_guards.DESK_ADDRESSEES`) | an order of STATE only — never a field order (FA-22) |
| the foreign minister (`llm_client.DIPLOMAT_ADDRESS_NAMES`, the parser's own routing words) | anything the parser routed to his Cabinet |
| the admiral (`fleets[nation]["admiral"]`) | the fleet's orders (`parser._NAVAL_META_VERBS`) |

The **field family** is FA-22's five marshal-less types plus
`general_defensive`. Reads and housekeeping (`validation.NON_ORDER_ACTIONS`, a
failed parse) are exempt — they spend nothing and keep their answers. **A
marshal the parser bound on an ORDER is trusted** (the live parser may bind an
epithet this rule cannot read); only the rewards (`grant_pension`,
`revoke_pension`, `grant_dotation`), whose `marshal` slot holds the recipient,
are checked against the address. Lever
`CommandExecutor.THE_UNBOUND_NAME_SPENDS_NOTHING`.

The refusal for an order of STATE (`META_ACTIONS` ∪ `ADMIN_ACTIONS`) says the
order was not given and nothing was spent, and hands the order back without
the name; an order a marshal carries keeps FA-22's line, *"There is no 'X' in
the order of battle, Sire. Whom did you intend?"*. Both carry
`kind: marshal_not_found`.

### 51.2 The verb set is generated from the router, never written

Where an order begins in `Zorglub build ships` is decided by
`clause_guards.order_verb_re()`, compiled from
`backend/ai/routed_order_words.py` — a **generated** module
(`python -m tools.gen_routed_order_words`). The harvest reads the fast
parser's own routing branches (the mock chain and its sub-routers): every
branch that assigns the action or hands to a sub-router, its POSITIVE test
only, helper predicates and keyword constants followed one hop, plus
`STRATEGIC_KEYWORDS`; it keeps each keyword's verb-position word and drops the
closed classes, the honorific and the router's addressee words. A word of five
letters or more matches as a prefix (the router's substring reach); a shorter
word matches whole with its inflections.

⛔ **After changing the parser's keywords, regenerate the module** — the
census in the CX-R1 test file re-derives it from the live source and fails on
drift. It is generated rather than harvested at import because the shipped
build is frozen and carries bytecode, not source. Lever
`clause_guards.ORDER_WORDS_ARE_DERIVED` (False restores the old hand list).

### 51.3 An unmarked address is the name at its head

With no comma, the address is the NAME the leading run opens with — article
and honorific in front, name-shaped tokens, a connective only between two of
them, a title that closes an epithet — and filler after it is filler
(`Zorglub just attack Mack`, `Zorglub's corps attack Mack`). The run's first
word still decides: `quickly attack Mack` names nobody. A comma that follows
an order closes a clause, not an address (`Zorglub attack Mack, then hold` is
addressed to Zorglub; `attack Bern, then hold` to nobody). Arms of service
(`cavalry attack Mack`) stay CX-7's ruling — not a name, not claimed. Lever
`clause_guards.THE_ADDRESS_IS_ITS_HEAD`.

## 52. The chip names the man (CN-1 … CN-4 landed September 22, 2026)

Landing records = `docs/audits/RECRUIT_ARM_UX_2026_09_20.md` §CN-1 + CN-2, §CN-3 and
§CN-4 LANDING RECORD. Pins = `tests/test_cn_the_chip_names_the_man.py`,
`tests/test_cn3_the_chip_tells_the_truth.py`, `tests/test_cn4_the_chip_honesty_census.py`.

**The arm is a selection key, never an override.** A marshal IS his corps, and his
arm (`world_state.recruit_arm_of` — the one rule the levy raises by) is fixed. So:

* a NAMED marshal raises his own arm whatever arm the sentence names — `Davout,
  recruit cavalry` raises infantry and says so first (PF-7's surfaced correction);
* where the game chooses the man (`recruit cavalry in Rhineland`, `recruit cavalry`),
  the arm is the key: `find_nearest_marshal_to_region(region, arm=...)` picks only a
  marshal of that arm, nearest first (strength breaks the tie). None in range → a free
  refusal naming who IS in range and what he commands, and the remedy derived from the
  board — the nearest commander of that arm with the order that reaches him, else the
  cheapest bench candidate of that arm with his price. With `arm=None` the selector is
  the pre-CN rule byte-for-byte. Lever `economy_executor.THE_ARM_CHOOSES_THE_MAN`.

**One quote.** `economy_executor.recruit_quote(world, region, arm=None)` answers "what
would this levy do?" with the executor's own steps in the executor's order — admin
action, selector (`WorldState.ready_marshals_near`, the pure core the selector is built
on), location gate, CO-4 field cap, pool, price (with the recipient's Intendance),
treasury — and the executor refuses through the same message builders. It ships as
`map_data[p]["recruit_here"]` (one quote per arm) only where the recruit row renders:
own soil, and friendly soil that feeds a French corps (where it carries the executor's
refusal — recruiting does not open on ally soil, ruling D5). `recruit_price_here` is
what a bare `recruit in <province>` would charge, 0 where it would refuse. ⛔ **A check
added to the executor and not the quote reds the drift pin**, which drives the real
`/command` on every province × arm.

**The ground speaks first (CN-3).** Where the game chooses the man — a province named,
or the bare levy at the capital — the province's own gates (unknown province, whose soil
it is, unrest) refuse BEFORE a man is chosen, because no marshal can remedy them: ONE
source `economy_executor.recruit_ground_refusal`, called by the executor's two no-marshal
branches and by the quote. The NAMED road keeps its order — there the ground is the named
man's own. A remedy's "give him the order yourself: '<Name>, recruit <arm>'" is offered
only where that man's own ground would levy.

**The chip says what the quote says (CN-3).** `region_panel.gd` renders the recruit row
where `recruit_here` is non-empty — one chip per arm, ENABLED only where the quote is
`ok`, stating its `terms` (the man, the men, the gold, the pool), otherwise dimmed beside
its `short` (said once when every arm is refused for one reason). Both strings are built
by the backend (`_recruit_quote_display`); the panel re-derives nothing. `feeds_us` gates
the substitute market only. The ordinance line reads `get_levy_status["ordinance_mult_pct"]`
(the pricer's own `1 + overage`; 100 on the legacy world). **The price and its named terms
are one computation**: `_recruit_cost_terms` returns both, `_calculate_recruit_cost` is its
price, and the recruit result's note is its terms list — so the note cannot name a term
the price did not apply. ⛔ **The client pins are DRIVEN**: `tools/cn3_region_panel_harness.gd`
runs the real panel headless on the live payload and every `do:recruit` url it renders is
sent through `/command` (they skip without the engine; a skip is not a pass).

**Every chip is honest, and a census proves it (CN-4).** A chip is offered only where the
order it sends would act on what it names; otherwise it is dimmed beside the executor's own
reason. The reasons come from single sources the executors read too:

* **Drill / Fortify** — `tactical_executor.drill_refusal` / `fortify_refusal` (`(sentence,
  short)`), one builder `order_refusal_response`, read by the pre-objection battery (so an
  order the executor will refuse is refused BEFORE any objection), both executors, and the
  payloads (`tactical_state.drill_refusal` / `fortify_refusal`; the Generals card's
  `drill_refusal` / `fortify_refusal`). Gate order = the player's road: stance, engagement,
  then the executor's own. ⚠ `_execute_drill` passes `stance_gate=False`: the executor's road
  (the AI, and the player's strategic/autonomous executions) never had the drill stance gate,
  and giving it one moves `BASELINE_SERIES` — filed as CQ-22, pinned as current.
* **Substitutes** — `economy_executor.substitute_quote` (the executor's gates in
  `_execute_purchase_levy`'s order, shared message builders), shipped as
  `map_data[p]["substitute_here"]`; the quote CHOOSES the recipient (the first infantryman
  standing there) and the chip names him.
* **The keel** — `naval.build_ships_refusal`, one gate for the Admiralty's chip and the region
  panel's (`naval_overlay.ship_build_refusal`).
* **Attack** — offered only against a court France is at war with
  (`marshal_data["at_war_with_player"]`, display-only, foreign marshals only); a neutral's
  marshal gets no chip — a declaration of war is the wizard's decision. Names are printed
  (`Utils.humanize_entity_name`) on the row, the label and the command.
* **Wizard echoes** — every structured action's echo, typed, must do what the structured road
  does, or be listed in `diplomacy_wizard.ECHO_IS_DISPLAY_ONLY` (today: the white peace), which
  `main.gd` keeps off the up-arrow and discloses beside the echo.

The census (`tests/test_cn4_the_chip_honesty_census.py`) renders the real panel, the real
Generals cards and the real wizard's `_build_command` headless (`tools/cn3_region_panel_harness.gd`,
`tests/_chip_census.py`) and drives every rendered chip; `TestTheInventoryIsComplete` fails on any
chip url in any client `.gd` it has not reviewed. ⛔ **A new chip gets a census row, or the
suite goes red.**

## 53. The offer is reachable (CX-R2, landed September 23, 2026)

**The rule, one layer deeper than CX-3.** CX-3 made the command-line completer obey *the game
must not offer a sentence it cannot read* and pinned it at the parser, where it held (280 of 280
lines parsed). CX-R2 draws it at the executor: **the game must not offer a sentence it will
refuse.** Measured on the 1805 boot before: 169 of 280 offered lines refused (60.4%; the memo
measured 59.3% at `15c498cb`) — every target pool ended in `out.sort()`.

**Every pool is nearest-first, and each is the executor's own answer.** `_MARSHAL_VERBS` gives
each verb a slot letter naming its pool:

| Slot | Pool | Source of truth |
|---|---|---|
| `E` | enemies France is AT WAR with, nearest over the lawful road | `enemies[].at_war_with_player` (the executor's `is_at_war`, both fog branches) |
| `R` | provinces his march can reach — own soil and `passable_nations`, through no sea crossing the navy shuts | `passable_nations` (`can_enter_territory(..., ignore_evacuation=True)` once per nation) + `naval_overlay.sea_link_verdicts` |
| `A` | provinces his `move to` enters | `tactical_state.move_open` = `movement_executor.move_open`, the move executor's own pure probe over his `movement_range` |
| `S` | provinces within his scouting reach | `tactical_state.scout_range` = `movement_executor.scout_range` (read by `_execute_scout`) |
| `H` | the province he stands in — a detachment is never sent ahead | the executor garrisons `marshal.location`; a named province that is not his is REFUSED with the road to it (`_execute_garrison`) |
| `M` | our other marshals ON THE MAP, nearest over the lawful road | the payload's marshals and their map entries |

A no-target verb is offered only where its `<verb>_refusal` in `tactical_state` is empty
(`_VERB_GATE_FIELD`: `fortify`, `unfortify`, `drill`, `defend`, `garrison` — each the executor's
own predicate: `fortify_refusal`, `unfortify_refusal`, `drill_refusal`, `defend_refusal`,
`EconomyExecutor.garrison_refusal`). A verb whose pool is empty is not offered at all. The
distances are a breadth-first walk of `/map_topology` (`map.gd get_region_topology`); before the
topology arrives the `R` and `S` pools are empty and the others come back alphabetically.

**Hidden, not dimmed.** The completer PREDICTS a line; a line the executor will refuse is not
predicted. The dimmed-with-its-reason idiom belongs to the chips (CN-4), which are affordances a
player browses; a player who types a hidden verb anyway gets the executor's own reason.

**A garrison is left where the corps stands.** The `H` slot names only his province, and
`_execute_garrison` REFUSES a named province that is not his — with the road to it — instead of
garrisoning his own ground under another name (the latent substitution the memo's correction 1
warned about). A nation named gets the region matcher's own answer. The AI names no province, so
its road is unchanged.

**The continuations are drawn where they happen.** `then attack` offers enemies nearest the
march's DESTINATION; `until … arrives` offers marshals nearest the ground HELD; a head his lawful
road does not reach offers nothing (a refused first step refuses the two-step order).
`_continuation_head` cuts at the first `then` / `until` / `for` WORD, which may be the first word
(`hold until` holds where he stands).

**Retreat reads the map, not the executor — deliberately.** The executor's danger test
(`world.is_in_danger`) counts corps the player cannot see; shipped on every response it would say
where a hidden enemy stands. The completer offers `retreat` only when an enemy at war, seen now
(a STALE sighting is not a position), stands in his province or one march off. It may leave out
a retreat the executor would take; it never offers one refused for want of danger.

**The marshal's STATE is not this row's.** Fortified (no move, no attack), locked in drill,
recovering from a retreat, broken, zero action points — a state that refuses whole families of
orders at once — is the chips' CQ-21 class; the completer's side is **CQ-24**, owned by the CR-6
triage, beside **CQ-28** (the drill lock refuses every tactical order, retreat included, yet a
standing order is taken for its AP and waits out the drill). A marshal off the map (a prisoner, or
on administrative duty) is offered nothing.

**Proof is driven.** `tools/cx_r2_completer_harness.gd` boots the real `main.tscn` headless and
records what `_build_completions` offers on real payloads; `tests/test_cx_r2_the_offer_is_reachable.py`
sends every offered line to POST /command (the boot, a staged board, the turn-10 and turn-20
fixtures), pins each pool against an independent Python computation, and pins each payload field
against the executor directly. ⛔ **A new completer verb gets a slot letter whose pool is the
executor's own answer, or a `<verb>_refusal` in `tactical_state` — and the driven census.**

## 54. First contact (landed September 23, 2026)

**The rule:** a line that is neither an order nor a question about the board
gets an answer that names a DOOR, never the shrug. ONE source,
`backend/ai/first_contact.py`, holds both the vocabulary the mock chain routes
on and the copy the help executor prints, so the two cannot drift.

* **Kinds:** `greeting` (hello / bonjour / how are you / a bare "Berthier"),
  `escape_menu` (quit / exit / restart / menu / settings / new game / load game
  / how do I save / I give up → *press Esc; nothing relayed*), `undo` (undo /
  go back / oops → *there is no unsaying an order; `cancel <marshal>` stands a
  standing order down; the pause menu recalls a save*), `options` (what now /
  I'm stuck / help me / any suggestions / `?` → the question desk's options
  answer — ONE source with `what can I do`, `ai/counsel.what_can_i_do`) and
  `goal` (win the war / how do I win / what is the goal → the open-ended
  campaign, read from `sandbox_mode`, + today's counsel).
* **Anchored, whole-line, closed vocabulary**; the address is stripped; every
  pattern is matched against the whole line, so an order to a marshal ("Ney,
  go back") never reaches the desk and no order verb appears in any pattern.
* **Sited** in `llm_client._parse_with_mock_chain` before the clause guards and
  the question arm, and never in front of `save …` / `load` / `debug`. The
  route mints `help` (kinds answered by `meta_executor._execute_help` via
  `answer_first_contact`) or `status` (`options`), confidence 0.9 → no LLM.
* **The three doors** (`first_contact.THREE_DOORS` — `what can I do` / `status`
  / `help`) close every generic shrug; the marshal-only shrug names the
  player's capital (`_home_example`); the place-only shrug walks the road law
  first (`_place_suggestion`: every fielded corps through `strategic.plot_route`
  + `issuance_road_refusal`; the shortest LAWFUL road is named, `attack` only
  against a court we are at war with; a naval refusal names the sea and THE
  ADMIRALTY).
* **The tactical `move to` belt reads the road law** (`movement_executor`,
  the auto-upgrade belt): `plot_route` + `issuance_road_refusal` before an AP
  is charged, player-only verdict, AI road byte-identical. `Ney, move to
  London` and `Ney, march to London` give ONE verdict.
* **The question desk** answers the whole army (`own_army`, subjectless) and
  `is <X> strong|dangerous|…` (the `how_many` name4 arm).
* **A verb is never a place:** `attack_vocabulary.guard_attack_verb_forms()`
  (every attack verb + inflections) is in the fuzzy target scan's skip list —
  `destroy Austria` reaches the nation refusal, not Deroy.
* **Example provinces are on the map:** `economy_executor.example_region`
  (the player's capital); the manual says `repair Lorraine`.
* Pins: `tests/test_first_contact_keyless.py`; sweep `tools/_sweep_first_contact.json`.

## 55. The School of War is unbreakable (landed September 23, 2026)

Eighteen cards in `tutorial_overlay.gd` `STEPS`, mirrored by
`backend/game_logic/tutorial_state.py` (drift-pinned), driven headless by
`tools/tutorial_overlay_harness.gd`.

* **Three release roads, none of them the whole-tutorial Skip:** (1) a refusal
  of the card's OWN suggested order releases the step at once — `main.gd`
  calls `tutorial_overlay.note_sent(command)` at its three send sites (typed,
  wizard, structured chip) and `_refused_our_order` reads `success == false`
  with no question on the response (an objection, a capture choice or a
  Cabinet confirm is not a refusal); the next card says why; (2) **Skip this
  lesson ▸** on every card but the last (`skipstep:` → `_release_step`);
  (3) the gate+2 turn catch-up stays as the floor and now says so.
* **The Cabinet card opens the real wizard** (`open_cabinet(nation)` →
  `_on_tutorial_open_cabinet` → `diplomacy_wizard.open_for_nation`, the F1
  guards) — typed diplomatic verbs are redirected by ruling G1, so no typed
  chip. Its predicate reads `talleyrand_mission_summary` on the base response
  (the sentinel `"None"` = no mission).
* **The overlay stays observe-only:** it never sends (the `send_command`
  substring is pinned absent); it is TOLD what was sent.
* **The three new lessons** are honest about the lesson board: envy is dormant
  (`jealousy_dormant`) and the card says so; there is no fleet and the card
  says so.
* The driver's `missions` dial gains `begin` / `decline`; both lesson scripts
  open the Cabinet on loop 3 under `begin` (the T-B1 / gate-drift pins are
  unchanged: the Cabinet card carries no typed suggest).
* Pins: `tests/test_tutorial_unbreakable_2026_09_23.py` (driven; skips without
  Godot — a skip is not a pass); sweep `tools/_sweep_tutorial.json`.

## 56. The first ten minutes (row EP F1, landed September 23, 2026)

Five rows from the September 23 live review (`BUG_FIXES.md` §Live Review);
plan and rulings = `docs/ENDGAME_PLAN.md` §1 F1.

* **Every live campaign has a briefing from its first morning (LV-1).**
  `dispatch.build_morning_dispatch(world, boot=True)` is the turn-1 briefing:
  the pure halves (situation, marshal status, intelligence, the headline read
  with `record=False`, the war block, the envoys) plus `today` — the counsel's
  own orders (`ai/counsel.what_can_i_do`, `FIRST_MORNING_ORDER_LIMIT = 4`) and
  first contact's `THREE_DOORS` + `CABINET_DOOR`. It skips EVERY consuming
  arm — the expectation latch, the headline-lead memory, both warnings (they
  write the rail), Talleyrand's report (its cooldowns), the Session-6 sabotage
  roll, the diplomatic-event queue (read and cleared by the next real
  dispatch). Its only write is `last_morning_dispatch`. `main.py`
  `_ensure_first_morning` builds it in `_reset_world_state` (the process boot,
  `/new_game`, the School of War) and in `/load` for a save without a stored
  briefing; `/new_game` and `/load` carry it as `morning_dispatch` through
  `_readable_dispatch` — the ONE reader `GET /dispatch` also uses (UX23-R4's
  unmet-marshals re-derivation, onto a copy). Pinned: the world after
  `/new_game` differs from a fresh `from_scenario` world ONLY in
  `last_morning_dispatch`, and the next real dispatch is identical with or
  without it. Lever `dispatch.THE_FIRST_MORNING_HAS_A_BRIEFING`.
* **The client prints the briefing, then the help, after every world swap.**
  `main.gd` `_print_boot_help()` is the one home of the boot help;
  `_apply_world_swap_response` (Begin, Continue, Load, the School) renders
  `morning_dispatch` and then the help, above the capture / interrupt /
  redemption arms. Both dispatch renderers draw a TODAY section. The Dispatch
  screen's empty arm says only "Berthier has no dispatch on the table."
* **A modal the command did not ask for waits behind its result (LV-12).**
  The six `_post_hud_response_routes` entries marked `result_first` —
  commitment paradox, marshal petition, incoming proposal, incoming
  settlement offer, sabotage discovery, vassal rebellion — are popped off the
  PopupQueue and merely ride a response; `_on_command_result` passes
  `_render_own_result`, so the order's result (Berthier's report, the tactical
  events, the glory attacks, the field dispatches, or the refusal line) prints
  first. The unmarked routes ARE the command's result or render it themselves.
* **One fog sentence (LV-13).** A wholly fogged enemy phase is ONE line naming
  up to three courts ("… and 6 other courts stirred, but their formations
  remain beyond our sight."); one court keeps its own sentence. Lever
  `main.THE_FOG_IS_ONE_SENTENCE`.
* **The courts at war (LV-7).** The SITUATION count reads only controllers at
  war with the player and stamps `enemy_regions_are_at_war`; `Utils.enemy_regions_sentence`
  says "The courts at war hold N regions." (legacy / lever down: the old
  count and wording). Lever `dispatch.ONLY_THE_COURTS_AT_WAR_ARE_COUNTED`,
  Europe-scoped (N1).
* **A war purpose's targets are one sentence (LV-8).**
  `war_status.objective_target_summary` is the ONE source: a defence purpose
  over the homeland (`objective_is_the_homeland`) → "the homeland — 28 of 28
  provinces held" / "the homeland is lost"; any other list → eight names,
  ", and N more" (`PURPOSE_TARGETS_NAMED`). The dispatch line, the war row's
  `objective.target_summary` and the snapshot's `war_objective.target_summary`
  read it; `Utils.objective_targets_text` renders it on the war tooltip, the
  war-detail popup and both War Summaries. Absent off the Europe board or with
  lever `war_status.THE_PURPOSE_IS_ONE_SENTENCE` down.
* Pins: `tests/test_ep_f1_the_first_ten_minutes.py` (the client classes drive
  the real `main.tscn` through `tools/ep_f1_first_ten_minutes_harness.gd`; they
  skip without Godot — a skip is not a pass); sweep `tools/_sweep_ep_f1.json`.


## 57. The fleet rides at anchor (NUI-2, landed September 24, 2026)

Landing record: `docs/NAVAL_SPEC.md` §18. The rules:

* **A coastal flag means the painted map draws a coast.** `tools/gen_port_anchors.py
  --audit` is the check (dev-only, Pillow + numpy): open sea = the lookup's
  no-province pixels painted sea (R−B < 45) in a water body of at least
  5,000 px; a coast = at least 100 px of the province within 4 px of it. A
  flag that disagrees is either corrected or recorded in the tool's
  `ART_EXCEPTIONS` with its reason — today the DEF-8 five (the stylised
  Adriatic reaches them; the flag follows the landlocked place) and Estonia
  (a DEF-7 sea-link end kept coastal by rule G3; its only water is a lake
  pocket). After changing the map art or a flag, run `--audit` and `--check`.
* **`is_coastal` is read**, for the shore itself: landing targets, embarking
  from a foreign shore, `shore_supply_state`, the AI's beach search (and the
  legacy Britain income/power arms on fleet-less worlds). Coverage keys off
  `sea_links`, closure off `ports`, building off `dockyards` — never the flag.
* **A dockyard stands on the sea.** A yard on an inland province is a
  validation ERROR (`validator._validate_navies`, boot path and CLI path). On
  the Europe registry a yard also needs open water to moor at, a registry
  `port_anchor`; a flag alone cannot see a province like Estonia, which is
  coastal as a sea-link end and has no open water. The
  1805 yards: Britain London / East Anglia / Cornwall · France Brittany /
  Provence / Normandy / Bordelais · Spain Galicia / Cartagena · Denmark
  Copenhagen · Ottoman Constantinople · Holland Friesland · Russia Livonia ·
  Portugal Lisbon · Sweden Stralsund · Naples Naples. Flanders stays a France
  CAMP province (the camp never asks for a coast).
* **Every coastal province carries a `port_anchor`** in the registry — the base
  of a fleet piece on open water off its OWN shore (the nearest province to it
  is itself, ≤ 40 px out, the piece's box on water; yards moor first, 40 px
  apart). Derived from the art by `gen_port_anchors.py --write`; hand edits are
  overwritten, and `--check` fails when the registry drifts from the art.
  Estonia carries none (it hosts no yard).
* **The map draws a fleet at its senior yard's `port_anchor`** and a blockade
  glyph beside it (`map_renderer_base._fleet_anchor`,
  `PORT_GLYPH_BESIDE_SHIP`); a map without anchors falls back to the old
  offset from the province centre.
* **An old save comes ashore on load** (`save_manager.load_game` →
  `world_state.reconcile_saved_registry_corrections`, registry worlds only):
  the corrected flags (`SAVE_COAST_CORRECTIONS`, targeted — a mod may author
  `is_coastal` through `region_overrides`) and the retired yards
  (`naval.RETIRED_DOCKYARDS`: Amsterdam → Friesland, Flanders → Normandy,
  Estonia → Livonia). Never on the scenario path. A future flag correction or
  yard move adds its row to these tables (both are drift-pinned).
* **The naval orders are buttons.** THE ADMIRALTY (T, then 7) opens with
  "Orders to the Admiralty" under the fleet lines — Blockade / Recall, the
  Grand Diversion, Lay down ships — and then the expedition's NEXT step
  (`naval.expedition_road_chips`): land a ready corps (up to four landings,
  enemy shores first, then odds, then nearest), else march a corps under the
  lift to the nearest yard the road law accepts, else commission the cheapest
  marshal the gate would pass — disabled with the gate's own refusal while the
  treasury cannot pay. Each button is the typed command the terminal takes;
  its enabled state is the executor's gate. The Admiralty does not object:
  naval orders carry no marshal's voice.
* **The gate is asked, never copied.** `recruitment.check_commission(...,
  treasury=)` answers "would he pass with this gold?" over the one rule;
  `cheapest_commission_if_funded` and the Admiralty read it.
* **The Emperor is never the expedition's counsel** (FA-D16, all surfaces):
  the lift refusal, the expedition term (`no_small_corps_line`), the region
  panel's withheld landing and the march buttons (`_small_corps`) all leave the
  Guard out, and name a new marshal's 5,000-man corps as the road — with its
  price when the treasury cannot pay (lever `THE_LIFT_COUNSEL_NAMES_THE_PRICE`).
* Pins: `tests/test_nui2_the_fleet_rides_at_anchor.py` (the registry against the
  art through the stdlib PNG decoder; the driven map and ledger classes skip
  without Godot — a skip is not a pass); sweep `tools/_sweep_nui2.json`.

## 58. The names match the map (DEF-14, landed September 24, 2026)

Record: `docs/MAP_IMPLEMENTATION_PLAN.md` DEF-14. The rules:

* **A province's name sits where the art paints it, relative to its
  neighbours.** `tools/audit_province_names.py` is the check (standard library
  only): each name's real coordinates (its `GAZETTEER`) are fitted to the art
  by a local affine transform over its ten nearest provinces, trimming the
  three worst-fitting neighbours; the miss is scored in units of local
  spacing, and a score of 1.5 or more is an outlier. `--check` exits 1 on an
  outlier that is not recorded.
* **Every outlier is renamed or recorded.** `STYLISED` holds the recorded
  cases with their reasons: "outlier" (the audit flags it and the name is
  kept on purpose — the Paris-basin shuffle, inland Amsterdam, the compressed
  North Sea and Baltic coasts) and "art" (the name fits its neighbours but the
  painted sea or coast does not — the Black Sea trio, the Adriatic five,
  Estonia's lake pocket).
* **A rename moves the name, never the game.** The nine DEF-14 renames kept
  every owner, shape, adjacency, yard and capital, and every scenario
  reference was rewritten to point at the same region (`BASELINE_SERIES`
  and M1–M7 were byte-identical).
* **An old save is renamed on load**, on the raw dict before `from_dict`
  (`world_state.rename_provinces_in_save_data`, table
  `RENAMED_PROVINCES`). It must run first, because the registry reconciles
  only run on a world whose every province the registry knows. The table is
  applied SIMULTANEOUSLY, because three names were reused for a different
  region; a save is recognised as old by a name that exists only before the
  rename. Prose that merely mentions a province stays as written.
* **After renaming a province:** add the pair to `RENAMED_PROVINCES`, move its
  entry in the audit's `GAZETTEER`, rewrite the scenario's references to the
  same region, re-run `python -m tools.audit_province_names --check`,
  re-measure the WO-13 collision census (`BOOT_COLLAPSES`) — a new name can
  sit within a typed mistake of a marshal's — and re-stamp the AUTHORED IQ-9
  parser cassettes: the parse prompt carries the alphabetical province list,
  so every 1805 parse prompt drifts (`docs/PLAYTESTING.md`, drift policy).
  Check the fuzzy suggestions too: a name that outranks an existing one moves
  a pinned typo ("Valencia" took "Venetia" from Vienna, so Toledo became
  Cartagena), and the senior yard is alphabetical (Spain's fleet piece now
  stands off Cartagena, not Galicia).
* **A title is not a name.** In the parser's word scan, a word right after
  "of" that matches no marshal and no target is a title's territory ("the
  Prince of Moskowa", "the Duke of Elchingen"), so the address is left whole
  to the executor's unbound-addressee refusal (CX-R1), which names what the
  player typed. A bare unknown name ("Moskowa, attack Mack") still gets the
  CR-2 question. Until DEF-14 "Moskowa" was refused properly only because it
  fuzzy-matched the old province "Oslo".
* Pins: `tests/test_def14_the_names_match_the_map.py`; sweep
  `tools/_sweep_def14.json`.

## 59. The fuse is longer (row EP F4, landed September 24, 2026)

The reward curve (§ES-7 "The Cost of Success") is DEED-keyed. Gate record
`ENDGAME_PLAN.md` D11; landing record `ENDGAME_PLAN.md` §1 F4.

* **An expectation rises only on a deed.** (a) A decisive victory with the
  marshal as LEAD — `dotation.is_decisive_victory`: the beaten corps broken
  or destroyed outright (`attacker_victory` / `defender_victory`), or its
  commander taken or gone from the field by the time the pipeline reaches
  the seam, or the war score's own decisive exchange
  (`battle_scale.is_decisive_exchange`: above 10,000 dead with one side
  bleeding more than 2:1 — the ONE predicate `diplomacy.record_battle` reads
  too). (b) A rise in his glory RANK that his own positive accrual earned
  that turn (`dotation.observe_glory_rank`, from the jealousy pass after the
  crowns, every nation's ladder; the first observation is silent; a rank
  handed over by a rival's decay or capture is not a deed). A reinforcer, a
  stalemate, a battle won on points with both corps standing, a garrison
  stomp (that path never reaches the seam — CA8-19's exemption) raise
  nothing.
* **One write.** `dotation.raise_expectation(marshal, world, cause)` owns the
  floor (`EXPECTATION_FIRST_TURN = 6`), the cooldown
  (`EXPECTATION_RISE_COOLDOWN = 4`, on `last_expectation_rise_turn`) and the
  cap; `expectation_rise_blocked` says why not. The field-deed call sits in
  the post-combat tail of `_execute_attack` that the player's and the AI's
  attacks share (GR5); the enemy AI's grant rung reads the same predicates.
* **The count is its own field.** `Marshal.expectation_steps` prices the
  claim (`REP_STEP × steps`, capped); `battles_won` stays the printed RECORD
  and still ratchets for every other reader. A pre-F4 save backfills
  `expectation_steps` from `battles_won` at load. `glory_rank_seen` is the
  rank memory (1-based; 0 = off the ladder or never observed).
* **The collective petition waits.** `jealousy.check_fontainebleau` needs
  turn ≥ `FONTAINEBLEAU_MIN_TURN` (12) and ≥ `FONTAINEBLEAU_MIN_UNMET_GOLD`
  (300) across the petitioners, on top of the three eroding men and the
  cooldown; checked after the re-arm, so a count that fell during the wait
  still re-arms.
* **The UNMET block is an alarm.** `dotation.build_unmet_marshals` names a
  man only within `UNMET_BLOCK_WINDOW_TURNS` (2) of erosion or already
  eroding; a captive is never an alarm. The rail row still opens with the
  shortfall and counts the whole window; the per-victory "raises his
  expectation" line and the dispatch's `expectation_rises` stay.
* **Levers, one per arm of the attribution:** `dotation.EXPECTATION_RISES_ON_DEEDS`
  (the deed rule AND the first-turn floor; down, `get_expectation` reads
  `battles_won` again), `dotation.EXPECTATION_RISE_COOLDOWN_ACTIVE`,
  `jealousy.THE_COLLECTIVE_PETITION_WAITS`, `dotation.THE_UNMET_BLOCK_WAITS`.
  All four down is the pre-F4 game byte-for-byte. The ambient
  `BASELINE_SERIES` is byte-identical under every combination — measured, with
  the reason (`tools/_f4_series_arms.py`, `tools/_f4_ambient_reason.py`): the
  reward economy's outputs (AI grants, petitions) never reach a
  threat-bearing decision inside 40 turns.
* **Measured on the review's own board** (`flagship_1805.json`, 14 turns,
  mock): first rise Lannes on turn 7, Massena on turn 11, first grace clocks
  turns 7–8, no collective petition. Re-open: a 40-turn commanded campaign
  that never sees a collective petition lowers the gate to turn 9.
* Pins: `tests/test_ep_f4_the_fuse_is_longer.py`; sweep
  `tools/_sweep_ep_f3_f4.json`.

## 60. The client layout pass (row EP F3, landed September 24, 2026)

Seven live-review rows on four client surfaces; landing record
`ENDGAME_PLAN.md` §1 F3; driven by `tools/ep_f3_client_layout_harness.gd`.

* **A closed petition arm names its reason above the fold.**
  `marshal_petition_dialog` renders every closed arm as "<arm> is closed —
  <reason>" in `GateLabel` under the header (an arm shut only by the purse
  names its price); the body sizes to its own text one frame after layout
  (`_fit_body`, bounded 120–360) and is `relax_last`, so the clamp shrinks
  the options list first; a reason is never printed twice.
* **The settlement rail is one row per court.** `_add_settlement_tier2_buttons`
  builds an `HFlowContainer` per court (name, then its Press/Ease/Drop) and a
  last row for coverage suggestions inside `Tier2ButtonContainer`
  (a `VBoxContainer`); the rail's floor is derived per open from the row count
  (42px a row + 10, capped at 30% of the logical viewport). A court can never
  be folded out of sight by a fixed grid floor.
* **Wizard chips wrap.** `_add_action_button` sets `Button.autowrap_mode`
  (a 4.4 property) with the chip filling the width; a gate reason is its own
  11px line under the chip and the chip's tooltip; the list's horizontal
  scroll is disabled. Step 1 pins the prompt to one line
  (`_lay_out_prompt(1)`); steps 2 and 3 expand. `refit()` is the live clamp,
  public, for a surface rendered offline (the IQ-10 harness feeds
  `_render_nations` / `_render_preview` a captured payload).
* **The Sponsor chip says what the money does.** For a court whose design is
  aimed at France the detail reads "Fund the design they already pursue
  against us — a bribe, not a purchase.", and the chip is not offered while
  at war with that court (`diplomacy.get_available_diplomatic_actions`).
* **Log rows carry glyphs.** `campaign_log._category_icon` prefixes each row
  with the category's phosphor glyph (sword / flag / coins / scroll /
  handshake) through `Utils.bb_icon`; the letters are the fallback only for a
  glyph missing on disk.
* **The capture waits behind the report.** The capture route is
  `result_first` in `_post_hud_response_routes`; `_display_result` stamps
  `_result_rendered` on the response it prints and `_show_capture_choice_dialog`
  prints the message only when nothing has — so the command path and the
  muster road (`_on_interrupt_response` renders, then routes) both print
  Berthier's report once and the message once before "Plunder or Secure?".
* **The recap modal is retired (D13).** `_show_strategic_reports` prints the
  "--- Strategic Order Updates ---" block and continues straight to
  `_on_strategic_report_dismissed` (an order that needs an ANSWER still
  raises its own interrupt popup from there). The dispatch's MARSHAL STATUS
  carries each order's reading from ONE arithmetic —
  `strategic.order_turns_remaining` (the report's own `turns_remaining`;
  `including_current=False` on a start-of-turn surface) and
  `strategic.order_eta_phrase` ("— arrives next turn", "— 3 turns out",
  "— holds 2 more turns", "— closes next turn", "— joins him next turn").
  `strategic_report_popup` stays registered and is never raised at turn
  start.
* **Evidence:** six IQ-10 frames `docs/audits/IQ10_{PETITION_COMMAND_CLOSED,
  SETTLEMENT_THREE_COURTS,WIZARD_STEP1,WIZARD_STEP2_AUSTRIA,WIZARD_STEP2_PRUSSIA,
  CAMPAIGN_LOG_GLYPHS}_2026_09_24.png` (+`_X2`), the capture group
  `layout_f3` in `tools/iq10_capture_payloads.py`. Pins
  `tests/test_ep_f3_the_client_layout_pass.py`; sweep `tools/_sweep_ep_f3_f4.json`.
