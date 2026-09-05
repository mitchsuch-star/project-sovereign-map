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

When lord's war_score < -30 AND vassal loyalty < 50: roll `random() < (50-loyalty)/100`. Fires AT MOST once per war pair (tracked in `cascade_triggered`). On success: -20 loyalty.

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

**2. A corps frozen on the game's own question is not loitering**
(`A_STANDING_QUESTION_IS_NOT_LOITERING`). The skip above `continue`d before
`_check_interrupts`, so removing it un-shields the issuance turn from the
cannon-fire ask. `_is_immobile` therefore grants a marshal awaiting the
player's word the same grace it grants one recovering from a rout — for the
WHOLE interrupt set, order-bound and standalone alike, since a cornered
marshal awaiting "fight or break out" cannot march home either. The grant is
bumped by one per grace turn, so `expiry − current_turn` is CONSTANT: the
window never widens and the surplus is preserved rather than spent on the
game's own silence. **Do not clamp the bump to `EVACUATION_MAX_TURNS`** —
`duration` may legitimately exceed 12 for a trans-continental march, and the
clamp shortens that corridor. (Written, measured, removed.)

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
order can be let go. Cleared when a new corridor opens for his nation (a new
treaty is a new offer) and when he reaches home. The refusal keeps its
consequence: a corps who declines the road is still warned 2/1/0 and interned.

**Rejected, with the measurement:** converting a cancelled road-home order
into a HOLD (so the existing "the player's own order stands" guard would skip
him) makes a *cautious* marshal auto-fortify on the soil of the power we have
just made peace with, every turn, and puts an *aggressive* one on the sally
arm — an order the player did not give.

**The mid-treaty beat.** A road handed out mid-treaty rides the existing
`evacuation_granted` event type with one extra key, `mid_treaty`, which three
renderers branch on: `campaign_log.format_event_oneliner` (or it re-announces
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
for E, Tab, M, Home and +/−. **Each arm mirrors the gate its unfocused twin
obeys** — bare E and Tab sit BELOW `_unhandled_input`'s `if _is_screen_open():
return`, so their Alt arms check `_is_screen_open()` too, or Alt+E ends the
turn with a full-screen ledger open where bare E refuses. **The map keys are
CALLED, never re-emitted**: a re-emitted event lands on the same
`text_focused` guard in `map_renderer_base._unhandled_input`, so the focused
route goes through the public `recenter_view()` / `zoom_step()` /
`cycle_map_fill_mode()`. The Alt arm consumes the event whether or not the
gate allows the action, so Alt+E never types an "e". The README and the boot
help advertise the Alt form beside the bare one — before this the README
named "Alt" zero times.

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
