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

**Widened October 4, 2026 (§93.6, SF-CMD-2's remainder):** the carrying set
also takes `carry out` / `conduct` / `beat` / `perform` / `effect` /
`undertake` the retreat and *your* retreat, and a retreat CONTINUED is his
own (`keep` / `go on` / `carry on` / `resume retreating`, `keep falling
back`) — lever `THE_RETREAT_IS_CARRIED_OUT`. The fall-through is no longer
bare: Berthier says the retreat was read as the enemy's and gives both orders
— `'<marshal>, retreat'` and the attack on an at-war foe in sight — lever
`THE_SHRUG_OFFERS_THE_RETREAT`. The earlier text here claimed the set closed;
it was measured short.

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

## 61. The display-name pass (row EP F2, landed September 25, 2026)

NPC-12's first slice. The rule is one sentence: **a player-facing string
names a man, a court, a state and a count the way the game prints them
everywhere else — never the roster key, the tag, the enum or the `(s)`
hedge.** Landing record `ENDGAME_PLAN.md` §1 F2; pins
`tests/test_ep_f2_the_display_name_pass.py` (every string driven through
`/command` or the real client, plus the census pins).

* **The count and the noun agree.** `display_names.plural(n, noun)` is the
  ONE backend helper ("1 turn" / "2 turns"; irregulars in
  `_PLURAL_IRREGULAR` — men, corps, sail, envoys); `emergent_designs._turns`
  and `diplomatic_dialogue._plural` delegate to it. The client mirror is
  `Utils.plural(n, noun)`. A census pin forbids the `(s)` literal in any
  backend or client player string (allowlist: the parser eval's report, the
  provider prompts, the validator, `settlement_helpers`, `formations`).
* **The humaniser is a MODULE-LEVEL name in `combat_executor.py`.** A
  function-local `from backend.display_names import humanize_entity_name`
  inside `_execute_attack` made the name local to the WHOLE function, so a
  use above that line raised `UnboundLocalError` on every AI attack against
  a just-retreated corps — found because `BASELINE_SERIES` moved with every
  lever down. All six local imports are gone; an AST pin fails on any local
  import of the name that is used before its line, and on ANY local import
  of it inside `_execute_attack`.
* **The men are named.** The scout report and the adjacent scan
  (`movement_executor.py`) print `humanize_entity_name(m.name)` and the
  controller through `formed_display_name`; the capture hint is a sentence
  ("Bohemia lies undefended — an attack takes it."); the covering/shield
  lines and the muster header print the man. The client's diorama
  nameplate and the war-table piece label pass through
  `Utils.display_marshal_name`. An AST census over `movement_executor.py`
  and a string census over the covering builder forbid a raw `{m.name}` /
  `{enemy_marshal.name}` in a player string. **Still open under NPC-12:**
  `game_logic/combat.py`'s narration ("ArchdukeCharles holds the line") and
  `ledger.py` never import the humaniser — the F2 cover pin is scoped to
  the [Shield] line for that reason.
* **The states and the courts are printed.** `_ratify_treaty` says "Treaty
  signed: Peace → Open Borders with the Ottoman Empire." (`STATE_DISPLAY` +
  `with_definite_article(formed_display_name(...))`); the downgrade guard
  names the COURT, never "France" (an AI offer's `target_nation` is the
  player — read `player_counterpart`); a failed ratification opens "The
  Ottoman Empire's terms could not be ratified: …". The envoy popup payload
  carries `from_nation_display` and `choice_display`
  ({accept: "accepted", reject: "declined", counter: "countered", …}), which
  `main.gd`'s "Responding to" echo renders.
* **An incoming offer carries no hint.** Both acceptance hints are blank on
  `build_pending_envoy_popup_from_terms` (the client-petition arm's pattern);
  the player's OWN previews keep `build_acceptance_hints`.
* **The strategic report's copy.** Every row from `strategic.py`'s per-turn
  pass carries `command_display = get_strategic_display(cmd)` and an int
  `turns_remaining`, stamped once at the pass's return; the report messages
  read "(2 turns remaining)" / "(1 turn remaining)" and "The agreed 1 turn
  has passed."; the client's `strategic_report_popup` reads
  `command_display`, `Utils.plural`, and has icons for active/consumed/
  retired.
* **The advance toll stands beside the locked figure.** A victor's advance
  into the captured province bleeds march attrition; the report's
  `casualty_summary` carries `attacker_advance_losses` /
  `attacker_after_advance` and the diorama's lead card `advance_losses` /
  `after_advance`; the terminal's Strength line and the lead card print
  "22,181 → 21,863 after the advance". The lock point (the pre-advance
  figure the war score reads) does not move.
* **The defence line is split.** `battle_report.defense_personality_components`
  returns one labelled row per factor the personality modifier multiplies
  ("Personality (cautious) +5%", "Outnumbered (cautious) +10%", "Immovable
  (literal hold)"); the product of the rows IS the applied modifier, pinned
  over every personality × stance × outnumbered × holding cell.
* **One arrow.** "→" in the materiel capture line and the march route;
  " -> " is forbidden by pin.
* **The enemy phase says whom it was taken from.** Both the conquest and the
  field-battle capture branches of `enemy_phase_dialog.gd` print " (was X)"
  like the movement branch.

## 62. Bohemia is not empty (row EP F5, landed September 25, 2026)

Landing record `ENDGAME_PLAN.md` §1 F5; pins
`tests/test_ep_f5_bohemia_is_not_empty.py`; attribution
`tools/_f5_series_arms.py` (levers set IN THE CHILD).

* **One walk-in per corps per turn.** P4.5's `_find_undefended_capture`
  returns nothing for a corps that has already taken `movement_range`
  undefended provinces this phase (`EnemyAI._walk_ins_this_turn`, reset per
  nation phase, counted by the action loop off the rung's `walk_in` tag).
  Lever `enemy_ai.ONE_WALK_IN_PER_CORPS_PER_TURN`.
* **A literal corps takes the cautious strength check.**
  `_evaluate_capture_safety` runs the 1.5× counter-attack check for
  `literal` as well as `cautious` before a walk-in beside a stronger enemy
  (Deroy at Franconia refuses Bohemia at boot: 74,000 against 22,000). The
  cautious arm is byte-identical. Lever
  `enemy_ai.THE_LITERAL_TAKES_THE_CAUTIOUS_STRENGTH_CHECK`.
* **Measured:** with both levers down Bavaria's Deroy took Bohemia AND
  Carniola in one phase on the historical boot and Austria promoted its
  Revanche the same turn; with both up Bavaria takes at most one Austrian
  province on turn 1 on all three seeds (historical, ulm, austerlitz) and
  the Revanche fires on none. `BASELINE_SERIES` re-recorded ONCE with a
  four-arm attribution (arm 0 byte-identical to the prior record; the cap
  alone diverges at index 7, the check alone at 13, both at 7).
* **The legitimacy sentence names the courts.**
  `settlement_staging.legitimacy_sentence` — "London and Vilna are unbeaten
  — a whole-war peace needs their consent (Austria 12/50, Britain 4/50,
  Russia 4/50). Press Austria alone: the separate peace." — is appended to
  the whole-war blocker's heading. "Unbeaten" is the WAR's word: a holdout
  whose pair war score from our side is not positive; a court we hold the
  capital of and have beaten in the field is a holdout by the arithmetic and
  still the court to press alone. Lever
  `settlement_staging.THE_BLOCKER_NAMES_THE_COURTS`. The predicate is
  unchanged.
* **"Separate peace with <court>".** A covered court whose row is at or
  above the threshold with no hard stop gets the chip
  (`settlement_staging.separate_peace_chip`) in its `dial_actions`, routed
  to the existing pair-substitute tier (`seek_bilateral_peace`) with ITS
  court in the structured params; `_handle_pair_peace_substitute_action`
  honours `selected_target_nation` only when it names a COVERED court (a
  stale or foreign name falls back to the table's own). The chip takes the
  dials' own gate — PROPOSE mode, the player's editor caller — so a frozen
  REVIEW row and an observer table carry none. Availability is
  the tier block's + eligibility helper's own answer; the client's tier-2
  renderer honours `available` / `disabled_reason_display`. No shipped
  board puts a court at 50 on the review's staging, so the gate is pinned
  through the scorer's stable seam.

## 63. Settled once, reopened (row EP F6, landed September 25, 2026)

Landing record `ENDGAME_PLAN.md` §1 F6; pins
`tests/test_ep_f6_settled_once_reopened.py` (driven).

* **The mechanism.** A battle resolves a grievance by action (pipeline step
  9.5, `clear_jealousy(resolved_by_action=True)`); the end-of-turn jealousy
  pass's same-pass suppression (`cooled_this_pass`) remembers only the
  coolings IT performed, so the same pair can re-fire off the rival's fresh
  laurels the same turn. The trigger is legal and untouched (it feeds
  `jealous_of`, which combat reads) — what was missing was the card SAYING
  so. Zero series movement.
* **The card says so.** A confrontation card built within
  `SETTLED_ONCE_WINDOW_TURNS` (1) of a by-action settlement of the same pair
  opens with "Settled once at Tyrol — and reopened by Ney's laurels since."
  (`jealousy.settled_once_clause`, read off the `jealousy_resolved` event's
  own `location`, which every `check_battle_resolution` call site now
  stamps — pinned by an AST census over the three seams). A timer expiry is
  not a settlement. Lever `jealousy.THE_REOPENED_QUARREL_SAYS_SO`.
* **A stale card is replaced.** A card for that pair still standing
  undelivered from before the settlement is stale in its body; the re-fire
  retires it (`_retire_pending_petition`) and queues the fresh card instead
  of the latch handing the old one over. Another pair's card is never
  evicted. A card whose grievance no longer stands at all is still retired
  at delivery by `petition_is_still_live` (FA-S17-D4) — that half predates
  F6.
* **The staging trap.** A cautious man with a live grievance WITHHOLDS from
  his rival's battle, so he is never on the rival's winning side: the
  shoulder-to-shoulder resolution is staged with the jealous man as the
  ATTACKER and the rival reinforcing him.

## 64. The Verdict and the Fall (row EP GE-1, landed September 25, 2026)

Landing record `ENDGAME_PLAN.md` §6 GE-1; spec `GAME_END_SPEC.md` §2 (R1–R9);
pins `tests/test_ge1_the_verdict_and_the_fall.py` (driven — the real
`capture_marshal`, `destroy_marshal`, `_ratify_treaty`, `TurnManager.end_turn`,
`/command`, `/load`). The user's September 25 additions ride here: the
Emperor's death ("The Eagle Falls"), the generals' death-odds memo
(`docs/audits/GENERALS_DEATH_ODDS_2026_09_25.md`, recommend-only, design row
GE-D1) and the exile story.

* **The flag (R7).** The endings arm only where a scenario authors a
  `campaign_end` block — `game_end.endings_armed(world)` /
  `WorldState.endings_armed`, a NEW derived flag. `sandbox_mode` is never
  written or re-pointed (it still means "the Europe world" in nine modules).
  `europe_1805.json` authors the block; the tutorial and the bare flag world do
  not, so the suite's `SOVEREIGN_SCENARIO=none` pin leaves every sandbox test
  as it was. A pre-GE-1 save is backfilled at load from its scenario's own
  block (`save_manager._backfill_campaign_end`). Lever
  `game_end.THE_CAMPAIGN_CAN_END`.
* **One entry point, one list.** `game_end.record_ending(world, kind, cause)`
  is the only writer of `world.endings` (serialized; plural because a Humbled
  Peace and a Verdict must both stand). Each cause is stamped once; after a
  terminal ending nothing else is stamped. Terminal causes (`soil_or_sword`,
  `chains`, `eagle_falls`) set `game_over` / `victory = "defeat"`; marked
  causes (`humbled_peace`, `verdict`) never do. The record carries its
  `build_campaign_summary` taken at the moment, built with the record already
  in the list (so a Humbled Peace grades itself the eclipse); a TERMINAL
  record's summary is rebuilt ONCE when the war is closed (§64.1).
* **One per-turn caller.** `game_end.process_end_of_turn(world, turn_ended)`
  runs once per `TurnManager.end_turn`, after `advance_turn` — the fall clocks
  tick (`fall.tick_fall_clocks`, the ONE writer of `fall_clock`) and, at the
  end of `verdict_turn`, the Verdict is rendered. Never inside
  `_check_victory_conditions`, which runs twice a turn: its sandbox arm is now
  `game_end.victory_check` — a pure read of the recorded terminal ending (the
  unarmed dict is byte-identical). A fallen campaign does not keep turning
  (`end_turn`'s entry guard), the enemy phase stops the moment the Empire
  falls, the post-advance exit now clears the choices nobody can answer, and
  the last action point does not auto-advance past a fallen Empire.
* **The two clocks (R1), `backend/game_logic/fall.py`.** "The Empire Without
  Soil or Sword" — the realm at ≤ 1 province (the ONE collapse predicate,
  read and never forked) OR no free corps and no affordable commission — for
  `fall_grace_turns` (5) consecutive turns; "The Eagle in Chains" — the
  sovereign a prisoner — for `captivity_grace_turns` (10). **The Fall is a
  death in war:** the soil clock ticks only while France is at war with
  someone, PAUSES while its only quarrels stand in a truce, and resets at a
  general peace (a humbled rump is not a fallen Empire); the chains clock
  advances only on a turn France is at war with the captor and PAUSES (never
  resets) during a truce or a vassal treaty, resetting on release or on a
  fresh capture (the entry is keyed on the captor AND the turn he was taken).
  Exits are per disjunct — retake a province, commission a marshal or free a
  captive corps, make peace; for the chains, read from the live relation to
  the captor: at war, accept his terms (any peace frees him) or storm the
  city that holds him; in a truce, turn it into a peace; at peace, make war
  and storm. A TICKING arm outranks a paused one as the "soonest", and a
  paused arm has no fall date. Paris alone never
  triggers either arm (PL-31). GR5: `get_fall_state(world, nation)` answers
  for any nation; only the player's clocks are kept.
* **The captivity exit is reachable (R1's proof).** No existing captor offer
  was guaranteed inside the clock, so a court holding the player's sovereign
  OFFERS its terms on the clock's own cadence (chains turns 1, 4, 7 —
  `ai_diplomacy._captor_offer_due`, the FIRST rung, before P1, whose armistice
  would only pause the clock), priced to the purse by the one EC-W4 source,
  bypassing the P8 gate and the type cooldowns, never overwritten by a later
  rung (P1 carries `proposal is None` like every other wartime rung — the
  review round), and never dropped (the P8 reducer forces an unwelcome harsh
  peace through). The envoy names the release (`captor_terms` in the dialogue
  context; the clause "any peace with Austria frees the Emperor"). Accepting
  at an empty treasury is legal and frees him (pinned). Lever
  `ai_diplomacy.THE_CAPTOR_NAMES_HIS_PRICE`.
* **The warning.** `turn_manager.get_defeat_imminent_state` on an armed world
  reads `fall.warning_state` — the condition, the clock ("1 of 5 — the Empire
  falls at the end of turn 17 (4 turns remain)") and the exits, heading "THE
  FALL OF THE EMPIRE", plus a structured `fall` key threaded through
  `_build_defeat_imminent_warning`. It also warns for the two arms the collapse
  never covered. The IQ-2 tail `CAMPAIGN_CONTINUES` is replaced by
  `fall.scope_sentence(world)` at every surface (ledger note, status report,
  war room) where the rules are armed, and stays verbatim where they are not.
* **"The Eagle Falls" (Sept 25).** At the ONE removal seam
  (`WorldState.destroy_marshal`), an armed world's sovereign whose corps is
  annihilated on the battlefield (`battle` / `charge` / `bombardment` — never
  attrition, internment, dismissal, a nation's teardown, never a prisoner)
  dies with it on a seeded roll (`game_end.sovereign_death_roll`,
  `SOVEREIGN_DEATH_CHANCE_PCT = 15`, `campaign_variance.seeded_int` on
  `sovereign::death::{turn}::{name}::{cause}` — the historical seed still
  rolls; no module RNG). A corps the fighting zeroes never reaches the Guard's
  escape toll (`_check_marshal_fate` returns at strength 0), so the roll covers
  exactly the case the toll could not buy — the plan's "the toll runs first"
  is corrected here. Death is immediate and terminal: the tombstone and the
  `marshal_destroyed` event carry `sovereign: true`, the dispatch leads with
  `sovereign_dead` (weight 102, above `sovereign_captured`), Le Moniteur prints
  "THE EMPEROR IS DEAD" (105), the combat copy names him. A foreign sovereign
  takes the same roll (none is authored in 1805). Lever
  `game_end.THE_EMPEROR_IS_MORTAL`.
* **The Humbled Peace.** `game_end.note_ratification` runs ONCE per
  ratification in the two top-level ratifiers (`_ratify_treaty`,
  `ratify_settlement_confirm` — never inside `_apply_settlement_terms` or the
  carve applier, which run on headless paths). It reads the SIGNED terms (a
  province already occupied and signed away is ceded all the same) plus the
  applied carve, and stamps `humbled_peace` — marked, never terminal — when
  France signed away its capital, at least half its homeland, or its crown
  (made a vassal by this treaty). It also titles every signed cession and
  counts the player's peaces.
* **The Verdict of History (R2).** At the end of `verdict_turn` (44, Early
  July 1807) if the campaign stands; four tiers from `verdict_tier` — triumph
  (≥ 5), ascendant (≥ 2), contested (≥ −1), eclipse — over provinces held vs
  the opening 28, the capital, the Emperor, great powers knocked out (+2
  each, cap 4 — E4's verdict input) and each war with a great power (±1 at
  ±25), the satellites kept, the treasury; a Humbled Peace forces the eclipse.
  The status quo reads "contested". Thresholds in-band tunable.
* **`campaign_totals` (R4).** Display-only (GR6), player-scoped, written at the
  moment: every battle at `_post_combat_pipeline` step 8.5 (one pass per
  combat path; the world_state auto-charge mirrors it; a ranged bombardment is
  not a battle), captures at `capture_region` and the auto-charge bypass,
  marshals at `capture_marshal` / `destroy_marshal`, coalitions at
  `form_coalition` (+ the boot league seeded by `from_scenario`), peaces and
  cessions at the ratify seams.
* **`province_title` (§2.2).** `conquest` at `capture_region` and the
  auto-charge bypass; `treaty` at `_ratify_treaty`, `_apply_settlement_terms`,
  an ultimatum yield and every signed cession; popped on a return home; the
  per-turn `reconcile_province_titles` (advance_turn's NA block) restarts a
  conquest's quiet clock under a hostile army or a renewed war.
  `province_title_kind` / `titled_provinces` read the bloc as the leader plus
  its vassal chain, never its allies. **Reconciliation:** an EMERGENT design
  (the Revanche) drops the provinces its court signed away while the treaty
  stands (`agendas._entry_regions`, `game_end.reconciled_regions`); a fully
  reconciled Revanche reads inactive and NOT satisfied. Lever
  `game_end.A_SIGNED_CESSION_IS_RECONCILED`.
* **Global elimination (E2/E3/E4).** E2: `coalition.no_court_left_to_alarm`
  (structural, never "nobody qualifies right now") silences the player's
  passive threat producers, the murmurs, and the dispatch's coalition gauge,
  and the war room says "There is no Europe left to alarm". E3: a dead court
  (no province, no free corps) cannot be declared upon; it holds no trade
  dominance; its fleet is not drawn; the enemy phase posts no "No marshals
  (eliminated?)" row or duplicate elimination notice for it; its deck is kept
  (revival is real) and every reader already skips it; `continental_ports_total`
  is deliberately untouched (NV-10: closure must not fall on conquest). E4:
  the `enemy_eliminated` beat and the "a crown struck from the map" special
  already fire; the Verdict counts great powers knocked out.
* **WO-D10 (R8).** With no home soil left, `recruitment.find_spawn_region`
  returns the richest province still HELD (tie-broken by name; the cached
  index, GR8); the refusal now means "we hold none". Symmetric — the AI's
  commission rung reads the same gate. Lever
  `recruitment.THE_EXILE_COMMISSIONS`.
* **Saves (R6).** `metadata.ending` on every slot; after a Fall the autosave
  is NOT overwritten (Continue resumes the turn before the fall) and a
  "Final — <date>" save is written once (`save_manager.write_final_save`, from
  the autosave door and from a `/command` that ended the war); `list_saves`
  sorts a Final save after every playable one; `/load` carries the terminal
  `ending`; `/mailbox/activate` is guarded like its eleven siblings; every
  response's `game_state.endings` lists the stamped endings (compact). The
  END SCREEN payload is `game_end.screen_payload(record)` — the compact view
  plus the summary taken at the moment — on `ending` (the end-turn road,
  `/load`, a `/command` that ended the war) and on `GET /campaign_end` (every
  ending; read-only, alive after the war is over). Each ending also leaves
  one chronicle line (`campaign_ending`, category `command` — the log type
  count is 166).
* **The exile story.** `game_end.build_exile_story(world, ending)` —
  deterministic (GR6), every clause from a fact on the record with its source
  named in `facts`: the place (captured by Britain → the Bellerophon and St
  Helena; Austria → Olmütz; Prussia → Küstrin; Russia → Schlüsselburg; no
  captor → the abdication at Fontainebleau and Elba; death → the funeral), the
  men (the loyal by their bond to the sovereign and trust, the fallen by their
  BATTLEFIELD tombstones only — the memo's §5(c)(i) — the captives, the one who
  broke with him), the record (battles, the high-water mark and the worst day,
  the provinces lost and to whom, the coalitions, the peaces), the Verdict's
  closing line and one voice (the captor's diplomat, Berthier, or Talleyrand).
  A Humbled Peace gets the "signed" variant. It rides the summary as
  `epilogue`; GE-2 renders it.

### 64.1 The review round (September 25, 2026)

Landing record `ENDGAME_PLAN.md` §6 GE-1 (the review-round addendum); pins
`tests/test_ge1_review_round.py`, each named for its finding.

* **The war is closed at ONE seam.** `game_end.close_campaign(world)` runs at
  the head of `main.build_base_response` — every POST — and, for an
  enemy-phase death, in `TurnManager`'s `_attach_endings`, and in
  `save_manager.write_final_save`. The terminal summary is rebuilt ONCE
  (`closed` on the terminal record) on the FINISHED field
  (the battle that killed him counted, the province it took lost) and
  `game_end.clear_unanswerable` — the ONE list — empties every question
  nobody can answer (the dialogue and popup queues, the capture choice, both
  objections, the redemption, standing interrupts, an armed charge). Then
  `main._attach_terminal_ending` sets `game_over` / `victory` / `ending`
  (setdefault — the end-turn road's own payload wins) and writes the Final
  save. Lever `game_end.THE_WAR_IS_CLOSED_AT_ONE_SEAM`.
* **After the Fall nothing of the player's moves.** An enemy-phase death stops
  the killer's own turn (the per-marshal loop breaks on `game_over`; the admin
  phase is skipped) and the rest of the end turn skips the player's standing
  orders, the grievance pass and the autonomous marshals. No prestige moves
  for a sovereign killed in the battle; the `sovereign_dead` headline stands
  alone; the Marshalate is not offered.
* **The field he fell on.** `destroy_marshal(..., location=)` — the attack,
  the charge and the auto-charge pass the battle region for a destroyed
  attacker (who has not advanced); the tombstone, the event, the ending detail
  and the epilogue read it. Berthier's report carries "And the Emperor himself
  fell on that field." (`CombatExecutor._stamp_death_on_report`, beside the
  capture stamp).
* **No court at peace holds the Emperor.** A lapsed safe passage on the soil
  of a court the realm is at peace with escorts him home through the release
  seam (`withdrawal._escort_sovereign_home`; he keeps at most the released
  prisoner's escort). Lever `withdrawal.THE_EMPEROR_IS_ESCORTED_HOME`.
* **Titles.** A renewed WAR breaks what either side signed to the other:
  `game_end.break_signed_titles`, from the ONE diplomatic-state setter on
  every entry into WAR, turns the treaty record into a conquest record (quiet
  clock from now) — only between the courts that SIGNED it (§64.2) — and a
  carve is a treaty record too (§64.2). `reconciled_regions`
  reads a standing treaty record, not "any active
  treaty" (an armistice had re-reconciled the very province its war was over).
  A hand-off inside the holder's bloc carries the record to the new holder; a
  signed province occupied by the receiver's satellite is titled.
* **The treaty record.** `note_ratification` counts a signed territory term
  only when the province is no longer France's (or a French satellite's), and
  a carve only from the APPLIED clauses. A truce is not a peace: WAR →
  ARMISTICE passes `war_ending` false; an armistice that expires into peace is
  counted there (`game_end.count_peace`). A settlement's Humbled Peace names
  the courts the plan covered.
* **The words.** The chains cause line and epilogue give the time HELD when a
  truce paused the clock (`detail.held_turns`); the realm arm names the
  province still held; the Verdict's lines are chosen from what is true
  (`game_end._tier_lines`); provinces lost are counted distinct
  (`campaign_totals.lost_regions`) and worded by the count; a single
  coalition is never "the last".
* **Saves.** A second Final save on the same date takes the next free name;
  the record names its own file before the write. A pre-GE-1 save is
  backfilled with a record at load (`game_end.backfill_record`: the opening,
  `record_since_turn` — carried on the summary and said in the epilogue — and a
  conquest title record for every province held off its holder's homeland).
  `/mailbox/activate`'s game-over refusal carries the letter-book count.
* **E2/E3 and the goal.** `coalition.displayed_threat` shows 0 with no court
  left to alarm (the ledger gauge and tier, the top bar, every response; the
  ledger's projection line is `coalition.NO_EUROPE_LEFT_LINE`; the stored
  scalar is untouched). `diplomacy.dead_court_refusal` refuses a declaration
  on a dead court at the flow's first step (and in `declare_war`). A court
  eliminated inside the enemy phase gets no row (the roster read live). The
  goal answer after the Verdict is in the past tense and says the Empire can
  still fall.

### 64.2 The verification round (September 25, 2026)

Landing record `ENDGAME_PLAN.md` §6 GE-1 (the verification-round addendum);
pins `tests/test_ge1_verification_round.py` (55), each named for its
finding. Four lenses attacked the review round's FIXES (`e5d67800`), not its
findings.

* **The close clears on every response.** `game_end.close_campaign` rebuilds
  the terminal summary ONCE (`closed`) but runs `clear_unanswerable` on EVERY
  call, so a question left in a pause save written after the Fall, or
  re-seeded by a road that runs after the response seam, is never raised.
  The redemption is gated at every producer: the checker
  (`DisobedienceSystem.check_redemption_threshold`), the standing read
  (`disobedience.standing_redemption`), the end-turn hoist
  (`hoist_tactical_redemption`), `main._include_command_redemption_event`
  and the two endpoint writers — and `main._attach_terminal_ending` drops a
  question the result staged BEFORE the stamp. Lever
  `game_end.THE_WAR_IS_CLOSED_AT_ONE_SEAM` gates the close (the rebuild and
  the clearing) ONLY: the /command-only attach it once named was deleted, not
  kept behind the switch.
* **After an own-order death nothing moves.** The strategic pass breaks on
  `game_over` (both passes), and `TurnManager.end_turn` re-reads the terminal
  ending after it — the Emperor can fall in his OWN standing order, not only
  in the enemy phase.
* **A legacy Final save is adopted.** `save_manager.load_game` stamps a
  terminal record that does not name its Final file with the file it was
  loaded from, so a 975f1f13 Final save no longer mints "(2)", "(3)"… on
  every load.
* **A truce on its last turn.** `diplomacy.armistice_resolves_this_turn` —
  the war panel's own projection (`armistice_remaining`,
  `armistice_projected_outcome`), read for one pair — says whether a truce
  runs out at THIS end turn's advance and how. A fall arm paused by a truce
  that ends in war this turn is `resuming`: it carries its fall date, ranks
  as ticking for `soonest`, and raises `critical` severity; its sentence says
  "the truce ends this turn and the war resumes". A chains arm whose truce
  ends in peace says the peace frees him. A paused count is stated in turns
  OF WAR still to come ("falls after 2 more turns of war"). A truce at a count
  of nought is never "at peace" ("no clock runs while the truce holds").
* **No court out of war with his realm holds the Emperor.** Every
  diplomatic-state change that leaves a pair outside WAR and ARMISTICE —
  peace, a vassal treaty with his captor, a forced alliance, a captor
  satellite's release — frees a sovereign held by the other side
  (`fall.free_captive_sovereigns`, from the ONE setter; sovereigns only, the
  W6-7 prisoner rule unchanged). On an armed world the death guard's captor
  fallback offers only courts AT WAR, and a corps emptied with none to take
  him is set down at home at the head of the released prisoner's escort
  (`WorldState._set_sovereign_down_at_home`). A SPENT Guard's successful
  breakout pays no toll it cannot — the Emperor keeps his last men.
* **The escort home is on the record.** `sovereign_escorted_home` is on the
  dispatch whitelist (a warning); the release row carries `interned_at` and
  `corps_interned` (`release_captured_marshal(..., detail=)`) and the
  chronicle reads "THE EMPEROR …'s corps INTERNED at …"; a lapse warning is
  dropped for a marshal already inside his realm's home zone; every
  internment line names the soil by its adjective (`nation_adjective`).
* **The signature belongs to the courts that signed it.** Every title record
  carries its `house` — the court the title belongs to (the signatory of a
  treaty, the conquering bloc's leader for a conquest). A hand-off follows
  the house (a grant, and the lord's reclaim from a rebel); a signature is
  broken only by a renewed war between `from` and `house` — never a
  satellite's own war, never the settlement's ARMISTICE→WAR→VASSAL
  bookkeeping hop (`reason="common_peace_vassalage_ratification"`) — or by a
  treaty repudiated without war (`diplomacy.break_treaty`, the paradox
  choice). A Tilsit carve writes a `treaty` record with `carve: true` for
  each CARVED province (`game_end.record_carve_titles`, from
  `formations.apply_create_client_clause`) — `carve_broken` and the vassal-row
  carve arm are retired — so a carve reconciles only what was carved, and
  outlives the client's release.
* **The words.** The epilogue ranks the courts in the same unit as the count
  — distinct provinces, each credited to the court that took it last
  (`campaign_totals.lost_region_to`); a record kept before the distinct list
  (`lost_regions_partial`) counts the losses instead. A battle opens its
  sentence with its article (`game_end._battle_subject`). A Fall, like a
  Humbled Peace, is always the eclipse (`verdict_inputs["fallen"]`), and the
  Verdict's first line names the loss the province count cannot see — the
  Emperor dead or in chains, the capital lost. The abdication names the
  province still held. The chains cause line names "N of them at war" only
  when the counted pauses (`fall_clock.chains.paused_turns`) account for the
  rest. The Emperor TAKEN in his own attack (or as a participant) is named on
  the message, and his fate — fallen or taken — REPLACES Berthier's verdict
  about scale rather than being appended to it (an ordinary marshal's capture
  is still appended, as FA-S17-11 ruled); the diorama never says he
  "watched" such a field. The goal answer names the turn history judged
  (the stamped Verdict's own date) and title-cases the tier properly. With no
  Europe left the ledger raises no "courts are recovering" headline. A dead
  court keeps its article ("The court of the Papal States no longer
  exists").

## 65. The End Screen and the Clock Line (row EP GE-2, landed September 25, 2026)

Landing record `ENDGAME_PLAN.md` §6 GE-2; pins `tests/test_ge2_the_client.py`
(the client DRIVEN through `tools/ge2_campaign_end_harness.gd` on the real
`main.tscn`, every payload off the real endpoints).

* **One scene, four registers, one payload.** `scenes/campaign_end.tscn` +
  `scripts/campaign_end.gd` (CanvasLayer 122, above the diorama and the pause
  menu) renders `game_end.screen_payload(record)` — the compact view plus the
  summary taken at the moment — and recomputes nothing. `register` picks the
  colours, the cue and the buttons: `fall` (crimson; THE EXILE / THE FUNERAL
  from `summary.epilogue`, THE RECORD, THE VERDICT OF HISTORY; **Load a
  campaign / Main Menu**), `humbled_peace` (crimson-grey; THE PEACE;
  **Continue**), `verdict` (parchment; the tier as the heading; **Continue**),
  `imperial_peace` (gold; **Continue the reign / Retire to the Tuileries** —
  GE-3's register, declared in `game_end.CAUSE_IMPERIAL_PEACE` /
  `REGISTERS` / `REGISTER_TITLES` so its stamp needs no client change; marked,
  never terminal). An unknown register renders on the parchment unless the
  payload is terminal. ESC presses Continue on a marked ending and nothing on
  the Fall. The card fits by `Utils.clamp_centered_panel` and a scrolling
  body; the title block and the buttons stay pinned.
* **Stash-and-raise (the NA-6b discipline).** `api_client.response_received`
  emits every 200-OK body BEFORE its callback; `main._stash_ending` queues
  the response's own `ending` and, for a cause the compact list
  (`game_state.endings`) names that the client has not shown, fetches the
  record (`api_client.get_campaign_end` → `GET /campaign_end`) — the Humbled
  Peace ratified on the settlement road arrives so. `main._show_pending_ending`
  raises the next queued ending where control would otherwise return
  (`_return_control_to_player` after the diorama and before the Proclamation;
  the diorama's, the Proclamation's and the petition's dismissals; the command
  path's tail; the world-swap tail), and the record's late answer raises at
  once when control has already come back. **A cause is raised once per
  client session** (`_endings_shown`); a world swap
  (`_adopt_endings_on_world_swap`, from `_apply_world_swap_response` and the
  plain-entry `_on_connection_test`) adopts the arriving campaign's MARKED
  endings as history and leaves only a TERMINAL one to raise — `/load` of a
  Final save raises its Fall (R6), a plain entry onto a fallen backend
  fetches and raises it, a Verdict seen in an earlier sitting is not news.
* **The Fall closes the command line for good (R3).** Every road that reads
  `game_state.game_over` ends at `main._on_campaign_over`: `_campaign_over`
  is set, `set_input_enabled(true)` is refused while it stands (only the
  world swap's reset lifts it), the ending raises, and with nothing to raise
  the terminal record prints alone. **Load a campaign** hides the card for
  the Load dialog and `_on_load_cancelled` re-raises it (`reraise()` — no
  second cue); **Main Menu** is the pause menu's road. **Continue** on a
  marked ending resumes the interrupted tail (`_return_control_to_player`).
  A second response of the fallen campaign (the "The war is over." refusal
  carries `game_over` and the same `ending`) raises nothing new.
* **The terminal record.** `_show_game_over_screen(game_state, ending)` prints
  the register's title, date and cause line, THE RECORD from the ending's
  summary and the Verdict's closing — beneath the card, and ALONE when the
  card cannot be raised. De-legacied (GAME_END_SPEC R4): no French-only
  heading, no hard-coded thirteen-province board; without a summary it prints
  what `game_state` carries and claims no more. A marked ending prints one
  gold line (its title and tier) and the cause.
* **The clock line — ONE source, three surfaces.** `fall.clock_line(world,
  view)`: `"<ARM TITLE> — <turns> of <grace> · <clause>"` — ticking: "the
  Empire falls at the end of turn N (K turns remain)" / "the regency falls
  …"; at nought: "the clock starts at this end turn — … after N turns of
  war"; paused by a truce: "the clock stands still while the truce holds";
  paused by the captor: "the clock stands still — no war with his captor";
  a truce ending in peace: "…and the peace frees him"; `resuming`: "the
  truce ends this turn and the war resumes; …" dated. **Never a date while
  the clock stands still** (`falls_at_end_of_turn` is None exactly then).
  `fall.clock_severity`: `critical` (counting, ≤ 2 turns left), `warning`
  (counting), `paused`. `fall._arm_payload` stamps `clock_line` + `severity`
  on the warning's `fall.arms[]` (the end-turn banner,
  `main._add_fall_clock_lines`, and the R screen, `dispatch_view.gd`, print
  them under THE FALL OF THE EMPIRE); `fall.clock_lines(world, nation)` gives
  the Strategic Ledger its `fall_clock` (`ledger.build_strategic_ledger`,
  sandbox worlds only, present only while an arm holds; the Territories tab
  prints it under the collapse note, `strategic_ledger._fall_clock_lines`)
  and the war room its lines — one per HELD arm in the ARMS order, after "Our
  own state" and before the long sentence with the exits. Lever
  `fall.THE_CLOCK_HAS_ONE_LINE`; False is the GE-1 payloads byte for byte.
  GE-3's Congress gate line joins the same readers.
* **The driver.** `_note_new_endings` prints the END SCREEN's blocks under
  each new ending (`_end_screen_lines`: the date and register, THE VERDICT
  and its closing, THE RECORD, THE EXILE's paragraphs; lever
  `THE_DIGEST_RENDERS_THE_END_SCREEN`), so a headless arm is evidence about
  the screen's content. `--stop-on-ending` ends a run at a MARKED ending
  (status `ending-reached`; a Fall reports `game-over` as before).
  `tools/gen_ge2_ending_fixtures.py` writes the two STAGED saves the
  clocks' arms start from (`fixture_ge2_soil_or_sword.json`,
  `fixture_ge2_chains.json`); the four ending arms and their commands are in
  `docs/PLAYTESTING.md`.

## 66. The Congress of Paris (row EP GE-3, landed September 25, 2026)

Landing record `ENDGAME_PLAN.md` §6 GE-3 (with its review round); design
`ENDGAME_PLAN.md` §2 and §4 (RULED); pins `tests/test_congress_of_paris.py`,
`tests/test_congress_review_round.py` (the review's findings, numbered, and
the two arms DRIVEN through the real driver) and `tests/test_ge3_the_client.py`
(the client, driven on the real `main.tscn`). One module,
`backend/game_logic/congress.py`, and ONE serialized field, `world.congress`
(`SAVE_FORMAT_REFERENCE.md`).

* **Title is the count.** The summons and the hold read
  `game_end.titled_provinces(world, player)` (GE-1's `province_title`:
  homeland — a satellite's only at loyalty ≥ 40 — a treaty cession, a
  conquest held `title_turns` quiet turns, a client's soil). The count is the
  BLOC's (the Empire and its satellites); the gold card says so. The 1805 boot
  holds 35; `hold_titled` is 45 (50 until GE-V, Sept 25 2026 — the played reach measured 41 at best, so ENDGAME_PLAN §2.8's rule fired). Every number is read through
  `game_end.cfg(world, key, DEFAULT)` from the scenario's `campaign_end` block
  (the validator knows the twelve keys; a GE-1 save's four-key block falls
  back to the defaults).
* **The summons.** `summon the congress` (typed; the Cabinet's step-1 row) —
  1 administrative action (the executor's ADMIN arm) + 2 DP (charged after
  `congress.summon` succeeds) + the peace dividend on every rente already on
  the books from its own end turn (`summons_cost_text` prices it:
  "+Ng a turn"). The gate terms (`congress.gate_terms`, in executor order —
  the ONE list the wizard, the desk, the clock line and `summon_refusal`
  read; each carries its condition `text`, its `breach` for the clock line
  and its `refusal`): an administrative action · (conditional: the campaign
  has ended · the Imperial Peace already signed · a Congress already sitting
  · no great power left) · `hold_titled` titled provinces · the capital held
  · the Emperor free · no satellite at loyalty ≤ 10 · Europe's alarm below
  `hold_alarm_ceiling` (a summons the hold would break at its first end turn
  is refused) · no Congress dissolved within `congress_cooldown` turns · 2 DP.
  A refusal names the first unmet term and costs nothing; a TERMINAL term
  outranks a spent action on the wizard's disabled button.
* **The verb reads only an order.** The summons is recognized at the HEAD of
  the line — after an address (the Emperor's own, "Sire", or the minister's)
  and a word of filler — never in a clause that merely mentions it. A line led
  by a marshal is that marshal's order (the Congress route stands down; the
  Emperor is the one marshal who IS the summoner). A question fails closed
  (the strong `is_question`, and any line put to the minister that ends in
  "?"), and so does a hedge, a musing, a request for instructions or a
  deferral (`perhaps`, `could`, `whether`, `explain`, `advise`, `in two
  turns` …): answered, nothing spent. The sweetener line must name gold
  (`1000 gold`, `800g`, `a sweetener of 800 gold`), and a line naming a
  treaty (alliance, pact, peace …) is the Cabinet's. A court may be named by
  its seat ("Berlin"). The gold charged is the figure attached to gold in
  the GUARDED line (`congress.sweetener_amount`: negated and deferred clauses
  blanked; a year or a turn count never paid; two different sums refuse,
  naming both).
* **The table.** `congress.answer(world, court)` — the ONE derivation the
  tick, the table, the surfaces and the price finder read. Precedence: GONE
  (eliminated, or in the player's vassal chain) · RECOGNIZES BY TREATY (the
  latch) · SHUT OUT · at WAR: SUES at the pair war score ≤ `sue_score`
  or with its capital in the player's bloc, else REFUSES · withdrawn this
  sitting · RECOGNIZES AT THE TABLE (latched) · the at-peace formula. The
  war score is PRINTED from the Emperor's side ("our war score +30 — it sues
  at +40"), the number every other war surface prints; the predicate reads
  the score reckoned at the last end turn, and the clause names today's field
  when it already reads otherwise. Before a summons, a beaten court's SUES is
  a projection ("it would sue once the Congress sits") — no envoy comes until
  the Congress sits.
* **The treaty latch.** Only a SIGNED peace latches, and only two kinds
  (`congress.note_ratification`, from `game_end.note_ratification` in the two
  top-level ratifiers): a peace ratified while the Congress SITS (the sue
  rung's, or any peace signed at the table's time — it also lifts a
  withdrawal), or the peace of a BEATEN court (one that ceded provinces to
  the Emperor's bloc in that treaty — Pressburg, Tilsit). Any other peace
  feeds the formula. A truce that runs out into peace is not a signature.
  Broken by a new war between them, or by the EMPEROR's own capture from its
  bloc or of its covets (never a satellite's autonomous war).
* **SHUT OUT** (the authored trade-dominance court, GR5): Continental System
  closure ≥ `cs_shutout_pct` at every end turn of the sitting — the first end
  turn the PORTS fall short spends it for this Congress — and no corps of hers
  on THE CONTINENT, read live (`congress.mainland`: the land component of the
  summoner's capital, sea links removed — 92 of 126 provinces; a corps France
  can march to and drive off; Copenhagen and Stockholm are not on it).
* **The formula** (`recognition_score`, pure, counterfactual through
  `overrides`): raw relation + the design term (±12: an active design on the
  player's bloc's soil −12; a design bought off by the player or the
  highest-priority design satisfied +12; survival 0) + hegemony fear
  (−(bloc share − floor) × 100, 0 inside the player's bloc or allied; the
  floor is an active contain design's `share_floor` — Russia's arbiter 0.33
  — else 0.45) + war weariness ≥ 60 (+10) + beaten by the player within 15
  turns (+10) + the treaty (alliance +20, defensive +10, pact/open borders
  +5) + the sweetener (+10 per 1,000g, cap +20) + seeded jitter ±3 per
  Congress (0 on the historical seed; before a summons the table projects
  the NEXT Congress's mood, so the summons never re-rolls it). ≥
  `recognition_threshold` recognizes.
* **A signature holds.** A court that recognizes at the table is latched for
  the rest of the sitting (`take_the_signatures`, at the START of every end
  turn and at the tick — never on a read). The flip-backs: a French
  declaration (which breaks the hold anyway), the Emperor's capture by force
  from its bloc, the annexation of what it covets — and only a court that was
  SIGNING (recognizing or shut out, at peace) withdraws; a court at war or in
  a truce never does. A great power that seizes a titled province of the
  Emperor's bloc (at war with a satellite) withdraws too, and is counted
  among the courts that would not sign.
* **The price** (`congress.price`) — display-only counsel, never a bargain,
  and TRUE and PAYABLE: each lever's value is the score the formula moves by
  when that lever is applied, side effects included; the treaty lever is the
  best treaty the court's CURRENT relation lets `_ratify_treaty` accept
  (`STATE_RELATION_REQUIREMENTS`), else an alliance with the courtship it
  needs folded in; the design lever walks the chain, contain designs included
  (the arbiter's buy-off), and says a chain takes one order per design; the
  sweetener's gold is the smallest that buys the points given what is already
  laid down (quote = charge = receipt = the score's move). The bundle — gold,
  the design, the treaty, then relations, pruned to the cheapest — is verified
  by the formula. Alternatives lead it: in a truce, signing the peace; for
  the trade-dominance court, shutting the ports. At war: the sue score, the
  capital, a peace, the ports.
* **The sweetener refuses free** a court the formula does not answer for:
  one that withdrew, one that has signed, one shut out, one that already
  recognizes, and gold that buys nothing.
* **The sitting.** `game_end.process_end_of_turn` → `congress.
  process_end_of_turn` after the fall clocks and before the Verdict; then
  `gazette.recompose_congress_column` re-sets the morning's Moniteur column
  from the answers just taken (the paper goes to press inside the advance).
  Day 0 is the summons turn; the end of turn `summoned + congress_turns` is
  the eighth answer. Each tick: E1 first; the signatures; the answers (beats:
  a signature — counted in logging order — a withdrawal, "no longer shut
  out"); London's purse; the War of the Congress; the shut-out latch; the
  HOLD; the strip; the resolution; then, if it still sits, the owed petition
  and every standing quote re-stated.
* **The hold** (`hold_conditions`, seven, at every end turn): titled ≥
  `hold_titled` (a ceder's war on the Emperor reopens its cessions —
  GE-1's rule — and the condition names that war) · the capital held · the
  Emperor free · no satellite lost to rebellion OR defection (latched at
  `vassal.record_vassal_break` and at the VS-6 defection) · no titled
  province lost by force (latched at the capture seams BEFORE the controller
  changes) · no war declared OR JOINED by the Emperor since the summons (his
  declarations, and his entry into an ally's offensive war) · Europe's alarm
  below `hold_alarm_ceiling`. A failed condition dissolves the Congress that
  tick. A siege is lifted when its war ends (`SIEGE_ENDS_WITH_THE_WAR`, every
  nation) — no court completes a siege at peace.
* **Refusal has teeth** (all read through `congress`, dormant unless the
  Congress sits; every reader asks the LIVE answer, never last tick's): the
  refuser's intent against the summoner +`refuser_weight_per_turn` per end
  turn refusing, and its Revanche +10; the brewing gate
  `coalition.brewing_gate` (`congress_alarm_gate` while two great powers
  refuse — the ONE source every reader, mechanical and displayed, asks); a
  refusing great power at peace qualifies for the coalition whatever its
  relation; while it sits, a great power that ANSWERS the Congress
  (recognizes, shut out) or is in a truce with the Emperor is never marched
  into a new coalition (`congress.spared_from_coalition`, read first by
  `qualifies_for_coalition`). The War of the Congress: a refuser at peace
  JOINS the standing coalition (`coalition.join_coalition`, with
  `form_coalition`'s housekeeping for the joiner) one end turn after its
  fore-warning, which comes at its second refusing end turn — both only when
  `congress.march_blocker` is empty (a coalition stands, the court is not
  allied, in a truce, a vassal, freshly at peace, cooldown-bound, already a
  member); otherwise the table names what holds it. London's purse: a
  refusing trade-dominance court pays every other refuser `LONDON_SUBSIDY` a
  turn under the paymaster's rules (its authored treasury floor, never a
  court it is at war with or one the Emperor bought off, the war subsidy's
  recipient not twice, the Emperor's standing sponsorship outbids it). The
  sue rung above P1 sends a PEACE with the `congress_recognition` clause
  every `SUE_CADENCE` turns — unless a settlement offer for that war is
  already on the desk (FA-S17-15's one envoy per war).
* **The bills.** At the summons: the marshals' collective petition if any
  marshal is eroding (its arrival logged only when a card is queued; a
  blocked slot owes it to the next end turn the Congress still sits) and every
  satellite's ask. While it sits: every rente is ×1.5 from the summons' own
  end turn (`congress.peace_dividend`); a client petition's loyalty stakes ×2
  from day 1. Every quote is shown = applied: the reward rail and the desk's
  petition rows are re-stated at the summons, at every sitting tick and when
  the Congress ends; the collective petition's concede arm and the redemption
  audience's settle arm are priced at DELIVERY.
* **Resolution.** On the last tick, hold intact, every great power
  RECOGNIZES / SHUT OUT / GONE → the Imperial Peace (`record_ending(world,
  "victory", CAUSE_IMPERIAL_PEACE)`, marked, never terminal, stamped once);
  after it the CONGRESS tab shows the ending's own table. Otherwise the
  Congress DISSOLVES: alarm +`dissolve_alarm`, the cooldown, each REFUSER's
  grudge (+1 threat a turn for 10 turns — a court still suing is named apart,
  "it sued, and the Emperor did not sign its peace", and bears none), every
  marshal's expectation one rung up. Not a defeat (D8). A Fall ends a
  sitting Congress with it (`close_on_fall`: status `ended`; no surface says
  it sits).
* **E1, the Universal Monarchy.** With no great power standing, the first end
  turn with the capital held and the Emperor free stamps the Imperial Peace
  with route `universal_monarchy` — told as "no great power remained to
  contest the order", never as a signature; its card carries no dissolved
  Congress's strip. The Verdict's ascendant floor never lifts a captive
  Emperor's reign or one whose capital another court holds.
* **Surfaces — one payload, one line.** `congress.build_congress_payload`
  (the CONGRESS tab, `GET /congress`, the wizard row, the war room's rows —
  the countdown `war_in` only where the war can come, else `march_blocker`);
  `congress.state_line` / `clock_payload` (the end-turn dispatch and the R
  screen, the Territories tab, the war room). Talleyrand's rung 0 names the
  biggest blocker and its price; the declare-war objection warns that a
  declaration dissolves the sitting. Beats: congress_summoned, _warning,
  _war (told once — never again as a bare war headline, never for a war the
  Emperor began), _recognized, _withdrawn, _dissolved (the cooldown the gate
  reads that morning, the alarm after the rise), imperial_peace; the
  `congress` chronicle type (167); Le Moniteur's specials and a column every
  turn of the sitting, re-set after the tick.
* **Dormancy (D15).** `tools/_ge3_series_arms.py`: three arms (all levers
  down / the Congress alone / shipped) reproduce `BASELINE_SERIES`
  byte-for-byte and count ZERO writes to `world.congress` — the ambient board
  never summons or ratifies a France–great-power peace, so the arms measure
  DORMANCY, not an attribution of the live hooks (those are pinned by the
  driven arms). No re-record.


## 67. The Fortunes of War — the generals' mortality (VP-M1, GE-D1 RULED + landed September 25, 2026 in GE-V)

* **The roll.** `backend/game_logic/fortunes_of_war.py` — ONE roll at the
  post-battle seam both combat copies share (`CombatExecutor.
  _handle_forced_retreat`, after the rout and the capture have had their
  say): only the LEADING marshal of the LOSING side (`attacker_won` /
  `defender_won` decided; a stalemate rolls nobody) of a real battle
  (`battle_scale.is_a_battle` on both sides' dead) whose corps lost at least
  `LOSS_SHARE` (25%) of what it brought. A man taken or rubbled on the field
  never reaches it. The sovereign never rolls here — GE-1's "The Eagle Falls"
  owns him at the removal seam. One deterministic draw through the campaign
  seed (`seeded_int`, namespace `fortunes::<turn>::<name>::<nth battle this
  turn>`; the historical seed still rolls; no module RNG is consumed): killed
  `KILLED_PCT` 1%, wounded `WOUNDED_PCT` 8%, in-band tunable. GR5: both
  boards, the same odds. Lever `THE_GENERALS_ARE_MORTAL`.
* **A wound.** ONE serialized field, `Marshal.wounded_until_turn` (0 =
  unwounded; heals `WOUND_TURNS` = 3 turns on). While `current_turn` is below
  it: the executor refuses attack / bombard / charge / garrison assault
  BEFORE the objection battery (`wound_refusal` — no marshal objects to an
  order the executor is about to refuse); a PURSUE or HOLD order pauses
  (`strategic.py`, the recovery-pause idiom) while a MOVE_TO / SUPPORT
  marches on; the AI's P0 rung stands the wounded man down (defensive
  stance, then wait); the card carries `is_wounded` / `wounded_until_turn`
  (shown = applied); a wounded literal is neither sidelined nor reset
  (`jealousy.update_literal_hold_counters`). The corps stands, defends and
  marches under its colonels. Beat `marshal_wounded` (dispatch weight 84,
  own nation only; log type 167 → 168 flipped consciously; Le Moniteur's
  "a marshal of France wounded").
* **A death.** The corps lives: its men pass to the nearest friendly corps
  within `TRANSFER_RANGE` = 3 regions (`find_nearest_marshal_within_range`,
  the dismissal transfer) or disperse; then `WorldState.destroy_marshal(cause
  ="killed_in_action")` — the ONE removal seam, so the reward rows, the
  standing ask, the campaign totals, the bench note and the chronicle line
  all follow; the tombstone carries `men` and `men_to`. The dispatch's
  `marshal_destroyed` arm and the log one-liner read the cause ("KILLED at …
  — struck down at the head of his corps; 20,000 men pass to Davout").
* **What did not move.** `BASELINE_SERIES` byte-identical with the lever up
  (`tools/_vpm1_series_arms.py`: the seam reached 39 times in forty ambient
  turns, no qualifying draw produced an outcome) — no re-record. M1–M7
  byte-identical. Pins `tests/test_ge_d1_generals_mortality.py` (22 — the
  design row's nine named pins and the surfaces).

### 67.1 The Guard is Spent (GE-D2, RULED + landed the same day)

`CombatExecutor.GUARD_SPENT_FLOOR` = 1,000 (the 50-man `GUARD_RUBBLE_FLOOR`
stays the annihilation line `take_casualties` reads). The Guard's 30% escape
toll is refused — and the player ASKED (fight to the last / cut our way out)
— when paying it would leave the Emperor under the spent floor; before, the
toll paid the Guard down to a 55–255-man remnant and the next defeat
annihilated it with no question ever asked (0 asks in 80 sovereign fate
checks), so the player met GE-1's death roll without having chosen to fight
on. The breakout copy in `strategic.py` reads the same floor. The rail row
and the report line say WHICH question it is ("the Guard is SPENT" is not
"ENCIRCLED"). Pin `tests/test_gev_played_campaign.py::TestTheGuardIsSpent::
test_the_guard_asks_before_the_last_battle` (the design row's named pin).

### 67.2 A court is subjugated by fiat only once beaten (GE-V, September 25, 2026)

`vassal.subjugation_refusal(world, lord, vassal)` — the unilateral
`vassalize` / `subjugate` / `make vassal` road (a WAR-state target) needs the
war to have DECIDED it: the lord's bloc holds the court's capital, or the
court's war score against the lord is at or below `SUBJUGATION_WAR_SCORE`
(−40, the Congress's own sue line), or the court has no corps left standing
(captives do not count). Otherwise refused, naming all three roads and the
peace table. The settlement's signed `subjugation` clause arrives at
`create_vassal_conquest(..., by_treaty=True)` (the court signed — the
ratifier's gate). GR5: any lord. Measured before the fix: `vassalize
Austria` on turn 1 of the 1805 boot with no battle fought subjugated a great
power and assimilated Mack, Charles and John (`gev-probe1`). Lever
`A_COURT_IS_SUBJUGATED_ONLY_WHEN_BEATEN`; pins
`tests/test_gev_played_campaign.py::TestACourtIsSubjugatedOnlyWhenBeaten`.


## 68. The Road to Forty-Five — the reach levers (row EP follow-on VP-R1, landed September 25, 2026)

**Owner:** `DESIGN_REFINEMENT.md` GEV-D1 (landing record) · probes memo `docs/audits/VP_R1_PROBES_2026_09_25.md` · pins `tests/test_vp_r1_the_road_to_forty_five.py` (33). Three probes ran before any code and two contradicted the brief; the build is what the probes supported, each lever a flip lever for the series attribution (`tools/_vpr1_series_arms.py`), none a config surface.

### 68.1 The muster preview names its odds (`combat_executor.MUSTER_ROWS_NAME_THEIR_ODDS`)
- **The number was already honest.** The committed figure is the arrival-WEIGHTED expectation (PT-A2): on 74 supported strikes over the GE-V boards it sat within 20% of the Monte-Carlo mean on 74 of 74 (median 0.994). GE-V's "overstates by a third" compared the CEILING clause to the field. What lied was the LABEL ("X if all march" is neither the ceiling nor a promise) and the ROWS — 35 of 100 strikes printed "WILL JOIN — will march to the sound of the guns" for a corps the same arithmetic priced at 0% (46 of 248 candidates, all departing from MOUNTAINS: the spec's §7 departing-terrain −20 puts Ney and Murat at logistics 3–4 on 55 and 50 against a 65 threshold ±8).
- **The rule is untouched.** `_calculate_reinforcements`, the departing-terrain table (now `CombatExecutor._ARRIVAL_TERRAIN_PENALTY`, read by the score and by the row), M1/M1b/M4 and the series cannot move for a display change (arm 3 = arm 1 in the attribution).
- **What the player reads.** The headline: *"expect about 38,878 with the corps likely to arrive, up to 61,779 if all march"* — "if all march" is the CEILING's label now (the brief's own placement). Every WILL JOIN row off the field carries `arrival_odds` (P(arrive) × 100 off the SAME sum, threshold and jitter the resolver rolls — `_expected_arrival_weight`, drift-pinned) and `arrival_note`: *"— he will NOT make it from the mountains at Munich in time; order 'Ney, support Soult' and it rises to about 77%"* (the written SUPPORT order is +10 to the score and a 60 threshold; 40 of the 46 zero-odds corps become reachable under it; the lever is named only when it would help and he is not already under one). The odds band, `committed_strength` and `ceiling_strength` are byte-identical with the lever up or down.
- **GEV-D1's second completion item is MET by the existing arithmetic** and pinned as such (`test_the_muster_preview_quotes_the_expected_arrival`: 11 driven strikes on the driver's own seed, within 20% on ≥ 8 of 10).

### 68.2 A raiding party holds no homeland (`movement_executor.RAIDING_PARTY_HOLDS_NO_HOMELAND`, `RAIDING_PARTY_FLOOR = MARCH_HALTS_AT_GARRISON` = 5,000)
- **The rule.** A corps of fewer than 5,000 men annexes no province that opened the campaign as its CURRENT controller's own homeland (`nation_starting_regions`, the ES-2 idiom; Europe worlds only — the legacy fixture keeps its walk-ins). The march itself stays legal: the corps stands there and is told why it holds nothing (the FA-9 shape, `capture_refused_raiding_party` on the result). The brief's 3,000 would have stopped NEITHER measured raid (Shrapnel's 3,000 is not "fewer than 3,000"; Wellesley's 3,782 is more) — the floor is the movement law's own scale: a garrison of 5,000 halts a march, so a corps under 5,000 is a raiding party.
- **Read at every unopposed-occupation seam:** the MOVE walk-in (beside FA-9), the attack's undefended exit (refused BEFORE the march, the remedy named: *"March him in with 'move to Maine' to stand there, or bring 5,000"*), the naval landing's undefended arm (the corps is ashore, the homeland not held), and the AI's own rungs (P-1, the stored intent, P4.5, the unfortify-intent path, and `find_ai_expedition`'s open-BEACH candidate — a HOST shore is a door into the war, not a conquest, and stays) — so the AI never marches a corps for a province the executor then refuses (a refused attack is a two-turn ban in its own bookkeeping). GR5.
- **What stays contested.** Conquered ground: a 4,000-man corps still walks back a province that is not its holder's homeland (Piedmont under Austria is the Kingdom of Italy's). A BATTLE won takes the ground whatever the size — only the unopposed walk-in is refused. Britain's 30,000-man Descent is untouched.
- **The series moved for this lever alone** (`BASELINE_SERIES` re-recorded once, attributed: arm 0 byte-identical, arm 1 diverges at [8] with 212 refusals of 325 checks, arm 2 byte-identical, arm 3 = arm 1). Passive-France guard, honestly: the UNATTENDED France ends turn 40 with 17 provinces (was 4) — the ambient harness's passive board, not a balance claim, but the first time since slice 4 that a France issuing no orders is not overrun by raids.

### 68.3 The glory attack obeys the odds (`jealousy.GLORY_ATTACK_OBEYS_THE_ODDS`)
- **The defect.** The P3 probe replayed the ambient board and both GE-V openings under the real driver: three autonomous glory attacks fired, two at `unfavorable` by the muster's own reading — Murat at fortified Tyrol under Charles's 52,000 committed, ratio 0.198 (−9,891, "Murat stood alone"), and Murat at Franconia, 0.279 (−2,127). A delegation-inferred attack has been stopped at the 0.7 floor since CR-5; the attack nobody ordered obeyed no gate at all. An aggressive man charging bad odds UNASKED is in character when the player sent him (CA9 row 2); the glory hunt is the one road where nobody did.
- **ONE predicate, both boards.** `jealousy.glory_attack_held_by_the_odds` reads `CombatExecutor.muster_odds` — the same ladder (`_muster_reason`), the same two committed terms and the same band the preview prints (drift-pinned) — in the player processor BEFORE the standing order is voided (a held attack leaves the order, the hold and the interrupt untouched; the warning is spent; the grievance persists; the WO-28 refusal beat names the odds: *"the odds held him — 1 to 5 against Archduke John's position at Tyrol"*, `held_by_odds` on the event and the log row) and in the AI's P3.9 rung (GR5). "Fires WITH the muster" was already true — the resolver rolled his reinforcements; from the mountains they were priced at nothing.
- Inert on the ambient board (0 glory checks — no jealous aggressive AI marshal ever finds a target there): arm 2 byte-identical.

### 68.4 The objection names the deed (display only)
- `DisobedienceSystem.describe_alternative(order, world)` — ONE describer: the enemy's printed name and the province he stands on (*"attack Archduke Charles at Tyrol"*). The executor stamps it as `description` beside the alternative and the compromise (the mechanic reads `action`/`target`, untouched) and the objection sentence carries it: *"Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Archduke Charles at Tyrol instead.)"* — so the typed route and the digest read it too. `objection_dialog.gd`'s `_describe_order` prefers the backend's sentence and keeps its local fallbacks. **Found, not fixed (filed VP-R1-X1):** `_generate_alternative` proposes the nearest foreign corps IN RANGE as the attack alternative, an ALLY's included (Deroy's Bavarians at Franconia for a Ney at Munich) — the executor refuses the friendly fire, so the trust option can name an order the game will not take.

### 68.5 The shut-out line: `cs_shutout_pct` 60 → 50 (P2)
- 60% = 16 of 26 authored ports was unreachable from play: the boot closes 10 (38%), the Pressburg shape minus the fixture's gifts 11 (42%), a beaten Austria's forced-alliance clause 12, every Congress signatory in the System — a mechanic that does not exist — 15 (58%); 16 needs a war on the Pope or on Denmark. The France-vs-Britain war score reads 0 on every board (the SUES arm has no producer on a Continental campaign). **50% = 13** is reached from the Pressburg shape by Austria's clause plus ONE walk-in (Rome) or ONE neutral war (Denmark). Both homes moved (`congress.CS_SHUTOUT_PCT`, `europe_1805.json campaign_end`), the MODDING_FORMAT default, the two Congress fixtures regenerated. **A save carries the line it was authored under** — an older campaign's `campaign_end` keeps 60 until a new campaign is begun (the fixture generator was the migration; player saves are not rewritten). **Recorded, not built:** if SHUT OUT is still unreached on a played road, a court that RECOGNIZES the Congress by treaty should close its ports for the sitting (the Tilsit reading, 15 of 26 from the Pressburg shape alone).

### 68.6 The re-measure and the deeper gate (GEV-D1's first completion item NOT MET)
- Both GE-V openings replayed under the levers on the historical seed with the archived dials, then hand-played in chunks and run out to turn 40 (archives `docs/audits/playtest_digests/vpr1-played-*`, fifteen runs): **opening B** 40 titled at turn 8 (the archive 39), the gate held Murat's turn-3 charge, Tyrol and Brunswick taken — then Charles broke Massena at Milan and walked into Provence and Lyonnais, the accepting dial signed an Austrian armistice mid-conquest, Bavaria was eliminated, and the unattended tail ended turn 40 at **36 titled**; **opening A** (the correct dials from the start) 41 at turn 7 and 39 at turn 13 (the archive 35) with six conquests on the twelve-turn clock — then the dispersed corps at Carniola were beaten piecemeal, the Emperor and four marshals taken by turn 14 (32 titled at 18), and the campaign FELL before turn 40 (the Chains clock; 14 titled on the end screen).
- **The levers moved the early count by +2 to +4 and removed two of the six measured mechanics** (the raids; the suicidal charge) and made a third legible (the muster). **The deeper gate stands and is the user's:** four action points for eight corps, the 37,500 supply cap that scatters the army into pieces Charles beats one at a time, the marshals' capture cascade, and a harness dial (`--diplomacy accept`) that signs every armistice offered — the measured gap at turn 40 is 36 (B) and the Fall (A) against 45. Per the brief the number is NOT moved a second time; `test_a_played_arm_reaches_forty_five_by_turn_forty` is a strict xfail reading the archived digests, so the day a road reaches 45 it turns red and the record is corrected. **SR-1e (Score Mandate Chunk 1, September 26, 2026) re-drove the roads with SR-1a..1d landed — scripted from the archived typed orders, the popups answered by the driver's dials (the chunked hand-play was not possible that session): the AAR road 35 → 37 at turn 40, opening A 34 → 31 (three provinces titling on turn 44; it completes now instead of falling), opening B 39 at turn 9 → 16 (its unattended tail lost 27 → 8 provinces after turn 30). The best point on any road is 39 of 45 and every road erodes from its peak. 45 is NOT moved a third time; the four levers above are SR-D3's first questions with these numbers (`SCORE_MANDATE_PLAN.md` §4 Q0); the xfail reads all five archives (`sr1e-*` with `titled.json` series, `tools/sr1e_titled_probe.py`).**

## 69. The Release Build — what the zip runs (ROADMAP position 10, landed September 25, 2026)

**Owner:** `docs/ROADMAP.md` position 10 (landing record) · rows `docs/BUG_FIXES.md` §Pre-Build Review PB-1 … PB-6 · pins `tests/test_release_build_2026_09_25.py` · pipeline `deploy/build.bat` → `tools/build_stamp.py` → `deploy/ink_iron.spec` → `tools/release_smoke.py` → the Godot export → `tools/list_pck.py` → the zip. The zip is the first build of the 126-province game; the March 2026 build carried the deleted 19-region world and was never booted by its own pipeline.

- **The frozen server finds its scenario (PB-1).** `backend/main.py` is PyInstaller's ENTRY script and an entry script's `__file__` is `<bundle>\_internal\main.py` — `Path(__file__).resolve().parents[1]` therefore points at the bundle root, OUTSIDE `_internal`, where the spec ships nothing. `MAPS_DIR` derives from `backend.models.region.EUROPE_REGISTRY_PATH`, an IMPORTED module whose `__file__` mirrors the repo layout in both worlds; `_DEFAULT_SCENARIO_PATH` and `TUTORIAL_SCENARIO_PATH` are `MAPS_DIR / <file>`. Rule: **no path the frozen server reads may be built from `main.py`'s own `__file__`**; the spec's `_MAPS_DST` must equal the registry path relative to region.py's root (drift-pinned). `save_manager._backfill_campaign_end` already carries a `sys._MEIPASS` candidate for the same reason.
- **The build stamp (PB-4).** ONE stamp, `<yyyymmdd>-<short sha>[+dirty]`, written by `tools/build_stamp.py` BEFORE PyInstaller into `deploy/build_stamp.json` (generated, gitignored; the spec ships it at the `_MEIPASS` root) and copied AFTER into the bundle as `build_stamp.txt`. Readers: `backend/build_info.build_version()` (`"dev"` from source, `"unknown"` when a frozen build lost its stamp — the smoke refuses both), `GET /test` `version`, the main menu's version line ("build <stamp>"), the pause menu's, and `launch.bat`, which refuses to reuse a server already answering on 8005 whose `/test` version is not the zip's own (a stale zip or a developer's source server would play a different game under this client).
- **The logs (PB-4).** `backend/runtime_log.install()` runs before the server's first print: the console streams are made `errors="replace"` in EVERY world (the backend prints emoji; a redirected cp1252 stdout used to raise mid-turn), and when logging is on — a frozen build, or `INK_IRON_LOG_DIR` — stdout and stderr are teed into `%APPDATA%\InkAndIron\logs\server.log` (one previous session kept as `server.prev.log`) and every `POST /command` appends one line to `transcript.jsonl` (turn, order, success, action, `parse_mode`, the reply's first 1,200 characters). Off in the dev repo and under the suite. The server never prints any part of the key (the log is the file players are asked to send).
- **Smarter Parsing ships, honest (call C1, PB-3).** The Settings section is **SMARTER PARSING (OPTIONAL)** with Connect / Disconnect; its copy says where the key goes (this PC → the game's own local server → Anthropic, no one else) and what it costs. `POST /config/llm` CHECKS a connected key with one free authenticated GET (`_check_anthropic_key`: the Models API, the parser's pinned model, 6 s, no retries) and never installs a key Anthropic refuses (`rejected`, `no_model` → `success: false`, the parser stays as it was); `unreachable` installs it and says so. `key_status` ∈ {not_connected, configured, connected, rejected, no_model, unreachable}, each with its sentence in `KEY_STATUS_TEXT`; `providers._record_api_outcome` stamps every live request's outcome and `_live_parser_outcome_notice` reads it at `build_base_response`: a success lifts `configured`/`unreachable` to `connected` (never `rejected`), a failure sets the state and is said ONCE per session as `parser_notice` (a dim terminal line printed BEFORE routing in `main.gd`, beside the stash chain — never a modal, never a retry loop). A new key re-arms the notice. The once-ever keyless hint: `/test` carries `smarter_parsing`; on a campaign start with no key anywhere the client prints one dim Berthier line and latches it in `UiSettings` (`parser/hint_seen`) — the reactive-but-discoverable discipline.
- **The tester kit teaches orders the game takes (PB-2).** Every order the README and the boot help advertise EXECUTES on a fresh 1805 boot, driven through `POST /command` by the pin; every quoted example in `help` is READ (a parse failure or a name the game does not know is the defect; a refusal for a reason the board gives — the treasury, an enemy nearby, no intelligence — is honest). The debug commands are listed only in debug mode; the recruit refusal's remedy is DERIVED (`economy_executor.recruit_remedy`): the cheapest levy a standing corps can raise today as the order that raises it, else the price gap said plainly — never the old "recruit 10000 infantry with Ney" the treasury refused on turn 1.
- **The pipeline boots what it built (PB-1's done-when, PB-6).** `deploy/build.bat`: stamp → PyInstaller (`--noconfirm`) → the stamp txt → config/launcher/README/licences (FA-43 unchanged) → **`tools/release_smoke.py`**, which starts the frozen exe from a folder that is not the repo, in an environment stripped of the developer's key/DEBUG_MODE/scenario, on a spare port with a throw-away save and log folder, waits up to 90 s for `/test`, checks the stamp, starts a campaign, types `status` and `Ney, attack Mack`, ends a turn, and asserts the log and the transcript exist — exit 1 stops the build before the zip → the Godot import pass and a **RELEASE** export (`--export-release "Windows Desktop"`; the March build was a debug export) → **`tools/list_pck.py`** reads the pack's own directory (PCK format v2) and requires the two maps, the tutorial scenario and the two scenes → every old zip removed, `ink_iron_<stamp>.zip` written. `--anthropic-key-from-env` runs the row's live-key smoke (one hard phrasing through the live parser). The clean-machine confirmation is the first outside launch; on the dev PC the proxy is the smoke's own foreign cwd and stripped environment.
- **The README (PB-5).** SmartScreen ("More info → Run anyway", Unblock), THREE windows, the logs and the build number to send, the `help` / `what can I do` doors, the campaign's ending as it ships (the Verdict on turn 44; 45 provinces by title and the Congress for THE IMPERIAL PEACE; the Fall), the Smarter Parsing path and its status line, the lost-server remedy. Pinned strings from earlier rows are kept verbatim (the roster block, the hotkey table, SPEAK COMMANDS, the saves path).

## 70. The Road to the Congress — Score Mandate Chunk 1 (row SR, September 26, 2026)

**Owner:** `docs/SCORE_MANDATE_PLAN.md` §2 Chunk 1 (landing records per slice) · rows `BUG_FIXES.md` AAR-1 / AAR-12 / AAR-28, `DESIGN_REFINEMENT.md` AAR-D1 / AAR-D2 · attribution `tools/_sr1_series_arms.py` (+ `.json`).

### 70.1 Status quo is a cession (SR-1a — `game_end.STATUS_QUO_IS_A_CESSION`)
- **The rule.** A SIGNED war-ending peace titles, by treaty, what each signatory's bloc holds of the other's — the other's homeland, or ground captured FROM the other (a conquest record naming it) — at the signature (uti possidetis). Read at the ONE diplomatic-state setter (`diplomacy.set_diplomatic_state`), per pair, after the state write, when the pair leaves WAR or ARMISTICE for a state above them by a signed road: `game_end.SIGNED_PEACE_REASONS` = `treaty_ratification` (the bilateral treaty, AI-AI included), `common_peace_settlement` (the table and the third-party peace), `mutual_exhaustion` (the exhausted-pair exit), `treaty_vassalization`, `conquest_vassalization`. Nothing else titles: a truce that runs out (`armistice_expired_peace`), an elimination, a repudiated treaty, the cheat — a truce is not a signature.
- **The record.** `province_title[region] = {kind: "treaty", since, from: <the ceder>, holder, house: <the signatory's lord>, retained: true}`; a live SIGNED record is never overwritten; a satellite still at WAR with the ceder on its own account retains nothing until its pair is signed. The ordering against the clause appliers is harmless by construction (each writes its own title after the setter; a province ceded back in the same treaty ends with the applier's record).
- **What a retained title is and is not.** It COUNTS (`province_title_kind` -> `treaty`) and BREAKS like any signature (a renewed war between `from` and `house` makes it a conquest whose clock restarts). It is **not reconciled** — `reconciled_regions` skips it, so the ceder's designs still covet the ground and recognition is bought at the table. It does **not** latch the Congress's beaten-court recognition (that latch reads applied cessions).
- **Surfaces.** The ratification summary's terms list ("Status quo: … stay ours by the treaty — titled." / "… stays Austrian by the treaty."), the settlement result (`status_quo_titled`, the message), the `status_quo_titled` dispatch event for the player's bloc. The stash the ratifiers read is `world._status_quo_titled`, same-turn only, read-then-cleared (never serialized — the record is the title).
- **Balance.** Four arms byte-identical (`tools/_sr1_series_arms.json`); the ambient board writes ONE retention (Britain–Spain, `mutual_exhaustion`) the AI never reads.

### 70.2 The client's war is the lord's war (SR-1b — `diplomacy.THE_CLIENTS_WAR_IS_THE_LORDS_WAR`)
- **The rule (AAR-D1 at default (a)).** A lord's PEACE or ARMISTICE carries every client pair that follows — the lord's clients against the court, the court's clients against the lord's bloc, and client against client — to the same state by the same road: `diplomacy.follow_the_lord` = the setter with the SAME reason (SR-1a reads it as signed), the treaty truce's cooldown (5) or the pair exit's truce floor, and `cleanup_war_end` with the objectives concluded for a peace and left for a truce. The pure read is `client_pairs_that_follow`.
- **The four roads.** `WorldState._ratify_treaty` (after its own cleanup; the aftermath names the clients that followed); `settlement_ratify._resolve_pair_state_transitions` (a client pair in ANOTHER instance follows and is counted among the resolved pairs — same-instance client pairs were already in the plan); `settlement_third_party._process_exhausted_pair_exits` (on `PAIR_EXIT_TRUCE_FLOOR_TURNS`); `diplomacy._process_armistice_expiration` — a client's truce standing beside its lord's (`_client_truce_follows_the_lord`) is not decided on its own relation: it thaws or collapses with the lord's (`_client_truce_pairs`). NOT the setter: elimination, the cheat and direct test writes pass through it.
- **What follows from it.** A resolved client pair is not at war, so no enemy rung can target the client (the AAR's Piedmont -> Tyrol -> Milan sequence cannot recur); `resolved_turn` is stamped, so PR-1's fresh-peace floor covers it; a client's own truce with no lord pair beside it still decides itself.
- **The surface (AAR-28).** `build_war_context_snapshot(..., incoming=)`: a `clients_follow` fallout line ("Our clients follow us out of the war: …" / "Their clients follow them: …") beside the allies' `separate_peace_ally` lines, on the incoming offer and the player's preview; on an INCOMING offer the paradox conflict is a WARNING naming the ally that fights on alone; the player's own outgoing peace keeps its HARD_STOP (the send road honours it).
- **Balance.** Arms 2/3 byte-identical; the helper fired twice on the ambient board (the pair exits) and moved nothing.

### 70.3 Quick win AAR-12 — the last administrative spend leaves the day to the player (`executor.AN_ADMIN_SPEND_NEVER_ENDS_THE_DAY`)
- Spending the last ADMIN action with the military pool already dry used to auto-advance the turn with no word and none of the typed road's envoy-lapse guard. It no longer does: the receipt says "That was the last order the day could take, Sire — the turn ends when you say so." (`last_order_of_the_day` on the result) and `end turn` ends it. The military road's auto-advance is untouched (WO-22's defer aside). Pins `tests/test_sr1_quick_wins.py`.

### 70.4 The gate line teaches the road (SR-1c — display only)
- **ONE derivation, `game_end.title_roads(world, leader)`** — for every held-unsettled province of the bloc, its shortest road to title, read off the SAME `province_title` record `province_title_kind` reads (so road and count never disagree). Four kinds: `quiet` (a conquest on its clock at peace with the ceder: turns left, the turn it titles on, the clock restarted by a hostile army; a reopened cession says so), `peace` (a conquest whose ceder is still at WAR with us: a peace that leaves it ours titles it at the signature — SR-1a — else the clock runs from the peace, because `reconcile_province_titles` restarts it every turn of the war), `loyalty` (a satellite's own homeland under loyalty 40: invest, or grant its petition), `signature` (no record: no clock runs; only a treaty titles it). Each road carries `text` (the ledgers) and `short` (the paper, the desk); ints only.
- **Surfaces.** `congress.build_congress_payload` → `held_roads` (the Diplomatic Ledger's CONGRESS tab lists one line per province, up to 8) and `alarm_road`; `congress.clock_payload` → `held_roads` at the gate (the Strategic Ledger's Territories tab prints four under the clock line); the war room prints four under the gate line, nearest first, then "… and N more on the Diplomatic Ledger's CONGRESS tab"; the question desk's Congress answer appends "The held provinces and their roads: …"; the Moniteur's Congress column speaks at the GATE within `gazette.NEAR_MISS_PROVINCES` (5) of the summons ("THE CONGRESS OF PARIS — 42 of 45 provinces titled; 3 more and the Emperor may summon the powers. Vienna titles on turn 18.") and stays quiet on the boot's 35. The clock LINE (`congress.state_line`) is untouched — its shape is pinned and the driver reads its ending.
- **The alarm term names its road.** `congress.alarm_road`: "it falls N a turn (one, plus one for each court at peace with us, at most three[, plus one for the Continental System]); a treaty that dissolves a league halves it" — read off `coalition._calculate_threat_decay` and the league-spent lever; appended to the alarm gate term's `text` and carried as its `road`.
- **The counsel names its price (AAR-D5's counsel half).** ONE quote, `diplomacy.diplomatic_price_quote(world, proposal_type, court)` = `get_dp_cost` over `get_transition_dp_cost` from the live state with the player's diplomat's skill, beside `world.diplomatic_points`: the settlement blocker ("Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 2." — the pinned sentence kept intact) and the war room's request-terms rung ("(1 DP; you have 4)").
- **Gates.** Two `.gd` renderers touched (the two ledgers); parse harness EXIT=0 (61 scripts — it caught a `:=` inference from a Variant in the first cut), boot 0 SCRIPT ERROR. Display only: no series or M1–M7 movement by construction.

### 70.5 The league treats when spent (SR-1d — PR-D1b, `ai_diplomacy.THE_LEAGUE_TREATS_WHEN_SPENT`)
- **The defect.** The AI's multi-party settlement OFFER to the player was gated only structurally (the war live, multi-party, the player in it, a known leader, ≥ 2 turns old, off cooldown) — it read no exhaustion, no war score and no wants-peace term — so every coalition war against the player ended 3–4 turns after it started (the commanded arm's turn-4 "Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved)", the league then spent for half of France's alarm).
- **The gate.** P1's OWN coalition break-ranks clause, extracted as ONE helper `coalition_break_ranks_reason(world, nation, *, war_score, diplo_key)` → `score` (< −50) / `exhaustion` (> 80) / `long_war` (8+ turns at < −60 — found while extracting: subsumed by `score` and dead since it was written; kept for byte-identical behaviour, recorded) / `pressburg` (NA-2 §5.4, a satisfied design at < −30) / None. P1's clause reads the helper (the FA-S17-15 guard lines untouched). NOT `effective_peace_threshold` — the ruling's correction: simulated literally it kept the league at war until turns 26–36. `league_offer_gate(world, war, player=)` applies it to the OFFERING LEADER of the active coalition's war against the player only (`active_coalition.target_nation == player`, the opposing-side leader a member), in the producer loop `process_settlement_offer_phase` and at the two `request_terms` checkpoints — the click-time affordance (`settlement_routes.evaluate_request_terms_affordance` → `disabled`, reason `league_not_spent`, the honest clock "exhaustion N of 80; at most ⌈(81−N)/8⌉ turns, sooner if the war turns against it") and the answer-time resolver (`_resolve_settlement_terms_requests` → refused with the same clock, the request cooled). NEVER in `_settlement_offer_eligible_for_war` (mediation shares it; `process_mediation_offers` stays ungated by construction — pinned by source census) and never on the player's own peace PROPOSAL (a losing France can always offer terms).
- **The rider.** `_covered_members_envoy_pending`: while a covered member's own bilateral envoy for that war is on the desk or queued, the producer waits a turn (the ruling measured a member's armistice and the league's table arriving together on 2 of 3 seeds — "another matter has arrived since"); and the "A Armistice treaty would be a downgrade" article ("An Armistice …", `with_indefinite_article` capitalised at the sentence head).
- **Measured** (`docs/audits/playtest_digests/prd1b-cmd-{historical,austerlitz,marengo}`, the commanded arm `commanded_full40.json --diplomacy accept`, 40 turns, this platform, engine `759414f9` + the SR-1c/1d tree): the league's first offer **t4 → t9 / t10 / t11**, the war ending the same turn; France holds **28 / 25 / 28** provinces at turn 40 (the IQ-8 row: 28 / 28 / 29 with the war ending at t4) — FA-D27's re-open (a seed under 20) does not fire. On this board the gate behaves as the ruling said: Britain's exhaustion arm (+8 a turn) fires first. Ambient series: arms 4/5 of `tools/_sr1_series_arms.py` byte-identical — the gate refused the league's offer on turns 3–11 (9 refusals) and the passive France answers no offer either way.
- **Pins consciously re-seated, exactly the ruling's list** (each says why in its own docstring): `test_ai_intent_mediation.py` ×2 (`_weary_boot_war` seats Britain at WE 81); `test_iq6_europe_speaks_its_mind.py` — every drive runs with THIS lever down (`_PRE_SR1D_LEAGUE`; the subprocess control arm through the driver's new `--lever MODULE:NAME=0|1`, recorded in `meta.json` `levers`), because the volte-face geometry those arms measure (a peace at t4, the door at t20, the beat at t21) no longer fits a 23-turn drive on the shipped board — the board as shipped is measured by the `prd1b-cmd-*` archives instead; `test_iq6_volte_face.py` T7 — the same subprocess drive at 40 turns, which the pre-commit hook's full run caught carrying the beat ZERO times on the shipped board; same lever through `--lever`, same reason, re-seated before the commit landed; `test_iq7_review_round.py` `turn6_snapshot` and `test_iq7_satellites_have_a_position.py::TestT7Lapse` (a queued petition needs a letter holding the slot at turn 6; staged lever-down, stated). Pins `tests/test_sr1d_the_league_treats_when_spent.py` (30, incl. the archive-driven cadence).

### 70.6 PB-7 — the doc housekeeping (SR-1d's docs half, September 26, 2026)
- Nine rows said OPEN. **Eight verified closed at HEAD** and stamped with their evidence — two by probe at `POST /command` (CQ-31: `Ney, move to London` refused in the march's words with actions unchanged; NPC-8: `support Marshal Ney` supports Ney), six by the landed slice's pins (NP-X4 → IQ-9; EAS-1 → the pre-build fix pass; UI-2d-1 → F3 + IQ-10; EWC-F1 → FA slice 10's FA-3; WIN-H5 → FA slice 10 + the driver's settlement policy; the NV-P1 wheel check → PC15-18's census). **One measured still OPEN on the wire: CA9-F3** (`action_info.cost` reads 1 for a 2-AP march) — re-homed to SR-9. ROADMAP row 16's "the only open soft-lock class" corrected. **Every ownerless row carries a Score Mandate owner by pillar** (the map is on the PB-7 row in `BUG_FIXES.md`).

### 70.7 The rest of Chunk 1's reserve (September 26, 2026)
- **AAR-15 — an armistice is an armistice.** `WorldState._ratify_treaty` queues `armistice_ratified` (dispatch event; vars `other`, `turns` = `ARMISTICE_DURATION`, `thaw` = `ARMISTICE_AUTO_PEACE_RELATION`; priority HIGH) for WAR → ARMISTICE, and `peace_ratified` only for a peace; the briefing's `peace_ratified` arm branches on the log row's `state_transition` and raises `truce_signed` (weight 68, a notch under `peace_signed`; template "Sire — a truce with {other} is signed. {line}"; Berthier: "A truce is a clock, Sire, not a treaty."). No new campaign-log type: the log row already said "Armistice ratified".
- **GE-V §4 nits — the Congress price.** The war lever names the capital as the capital ("take its capital, Vilna" under a "(St Petersburg)" seat); for an island court (its capital off `congress.mainland`) the ports lever comes BEFORE the capital lever — a Descent most campaigns cannot mount does not lead the sentence.
- **The School of War's card XVII "The Congress of Paris"** (`tutorial_overlay.gd` + the `tutorial_state.STEPS` mirror): between XVI the Wooden Wall and the Instruments (now XVIII, gate 12; the hand-off XIX, gate 13; `_pred_turn_gte_13` added). The lesson authors no Congress, so the card TEACHES the great campaign's road — title by four roads, the summons at forty-five, the table, the sitting, the CONGRESS tab that names each held province's road (SR-1c) and the war room that prices the roads it counsels. 18 → 19 cards; the count pin flipped consciously.

### 70.8 SR-1e — the re-measure (September 26, 2026)
- **Instrument.** Three roads driven to turn 40 on the shipped tree with SR-1a..1d landed: the AAR road (`tools/playtest_scripts/sr1e_aar_road.json` — the hand-played typed orders of September 25, rebuilt from `aar-hand-played/commands.md`), GE-V's opening B (`sr1e_gev_b.json`, rebuilt from the `vpr1-played-b-*` digests' typed orders) and opening A (the committed `gev_pressburg_road.json`), with `--diplomacy accept --settlement decline --objection insist --client-petition grant`, snapshots at turns 9 / 13 / 18 / 30, and the count read off each save by `tools/sr1e_titled_probe.py` (through `congress.titled` — the digest prints the clock only at the gate). **Honest limit:** these are scripted replays, not the chunked hand-play the contract asked for (the previous session's chunk scripts are gone; a hand-played road answers its popups by hand) — the scripted opening B is therefore not the played B.
- **Measured (titled of 45, turns 9 / 13 / 18 / 30 / 40):** the AAR road 35 / 35 / 35 / 35 / **37**; opening A 34 / 34 / 34 / 31 / **31** (+3 on turn 44); opening B **39** / 37 / 37 / 35 / 16. No road reaches 45; the peak of any road is 39 (B, turn 9); every road erodes from its peak. The number is NOT moved; SR-D3 opens on these numbers.
- **Chunk 1's exit (FOR USER CONFIRMATION):** the ending 5.5 → 6.5 (the road teaches its cost; a player cannot yet reach it — target 7.0 not met, residue SR-D3), diplomacy 6.0 → 6.25, directional ≈7.0.

## 71. THE SCORE MANDATE — CHUNK 2 DIPLOMACY, "The table tells one truth" (September 26, 2026)

### 71.1 SR-2a — One verdict per screen
- **The table seats the covered leader (AAR-2).** `settlement_validation.accepting_leader_for_coverage(war_instance, side, covered)`: the war's side leader while it is covered, else the senior covered court in the side's own order. The preview's leader-level `acceptance`, the confirm dialogue's consent check and `staged_leaders`, and the ratification re-score all read it (`THE_TABLE_SEATS_THE_COVERED_LEADER`).
- **The per-court table IS the gate (AAR-2).** For a table with terms, `can_ratify = not hard_stops and per_court_carries and not empty` (`settlement_staging.THE_TABLE_TELLS_ONE_TRUTH`); the blocker is `overall_acceptance.carry_verdict_display` — the sentence the header prints — never a component label. A WHITE peace keeps the leader gate (G4F-19: an empty package is exempt from the per-court gate); its header can still disagree with a live Ratify — residue SR-2a-X1, recorded.
- **Consent on the revision route (AAR-3).** `request_settlement_revision` stages with the FA-3 trio (`consenting_courts` = the covered courts, `consent_terms` = the offered package, `consent_offer_id`); `settlement_staging.consent_kwargs_for_restage(dialogue, terms)` carries it through every restage of the SAME package (dials, focus, Submit for Review, Return to Terms) and returns `{}` — consent lapsed, every court scored normally — on the first changed term. Equality is over the package's SUBSTANCE (`settlement_validation.consent_terms_equal`: every field but provenance — the guided dials stamp `authored_by` on a clause they touch, and a magnitude re-set to the same figure is not a change); the ratification check reads the same equality.
- **The letter stands (AAR-3).** The offer is NOT consumed at revision staging (`settlement_offers.THE_LETTER_STANDS_UNTIL_THE_DRAFT_CHANGES`); it waits in the mailbox queue behind the draft (Back Out promotes it, Accept still works) and is retired by `consume_offer_by_id` when the draft first changes (the redraw seam) or when the consented draft ratifies (the ratify seam).
- **One harsh transform (AAR-7).** `diplomatic_templates.harden_proposal_terms(suggested, proposal_type=, round_num=, target_nation=)` is the executor's `modify_harsh` arithmetic; the T1 menu's `variant: "harsh"` option hardens then eases (`ease_suggested_terms`, the G4F-9 convergence); `collapse_identical_packages` drops a harsh option identical to its generous sibling and appends "<Court> will sign nothing harsher today.", and relabels an eased-but-distinct harsh package `HARSH_EASED_LABEL` ("Firmer terms").
- **The petition's arm is derived (AAR-26).** `settlement_offers.refresh_ally_petition_availability(world, dialogue)` sets Grant/Honor `available` from `_petition_table_is_open` (a mounted PROPOSE table or a suspended scoped draft) with `disabled_reason_display` naming the door; called at the build, `GET /pending_envoy` and `POST /mailbox/activate`. A refused Grant/Honor carries `must_reopen` + `reopen_target` (the settlement opens for the petition's court; the petition is retained).
- **The petition expires with its table (AAR-26).** `lapse_ally_petitions_without_a_table(world)` runs in `_advance_turn_internal` beside the draft discard: a petition whose war ended, or whose settlement is not MOUNTED at turn's end, is removed with a `petition_lapsed` notice on `pending_settlement_draft_notices` and its rail row dismissed (`A_PETITION_LAPSES_WITH_ITS_TABLE`).
- **The label names the courts at war (AAR-27).** `ai_diplomacy._settlement_request_war_label(war, war_id, player=)`: the player plus every ally with a live `war` pair against a court still at war with the player, "vs" the courts whose pair with the player is `war`; a bare roster dict (no pair record) keeps the full join.

### 71.2 SR-2b — The Talleyrand verbs
- **The recall's words (AAR-20a).** Inside the diplomat-addressed parse (`_parse_diplomatic_command`), `diplomatic_dialogue._RECALL_RE` (`recall`, `come home`, `bring him/Talleyrand/our envoy home|back`, `return to Paris`, `call him back`) is the CANCEL mission — `_recall_mission`, free, behind the transit gate. `recall <marshal>` and `recall the fleet` never enter this parse.
- **The nation list claims only the court (AAR-20b).** `dialogue_routing._line_is_only_the_court(line, label)`: an `expand_options` row (the proposal picker's nation list) claims a typed line on arms 1 and 3 only when the line is the court's name plus filler / a picking verb; an order naming a court falls to the parser and runs for that court. `diplomatic_executor._phrase_within` makes the resolver's containment arms whole-word ("russia" is not inside "Prussia").
- **The Cabinet's rules on every road (AAR-21 / CRT-8's mission half).** `diplomatic_dialogue.MISSION_ROWS_BY_STATE` mirrors `get_available_diplomatic_actions`' per-state mission rows (`mission_rows_for_state` folds `REASSURE_ONLY_AT_ALLIANCE`); `mission_state_refusal(world, court, mission)` refuses the typed road before the DP check — a vassal ("governed from the vassal ledger"), a belligerent ("intelligence and undermining are the missions a war allows"), an ally ("reassured, not courted"), reassurance outside a full alliance. CANCEL is never refused. Lever `THE_CABINETS_RULES_ON_EVERY_ROAD`. Census pin: offered on both roads or neither, every state × every mission type.

### 71.3 SR-2c — WO-32, PR-D1c, PR-D1d
- **A refused arm keeps the decision (WO-32).** The vassal-rebellion modal's arms run FIRST; the dialogue is retired and the rail row dismissed only on SUCCESS; a refused Invest (cooldown / gold / DP) or Garrison (2 AP) re-seats the modal from the ONE builder (`vassal.build_rebellion_popup` — the producer's too — via `rebellion_popup_for_dialogue`) with `refusal` on it and `vassal_rebellion_retained` on the response; Accept Risk retires it unconditionally. The rail row carries `details.vassal`; `dismiss_rebellion_row` dismisses that vassal's row (a pre-WO-32 row without the key is dismissed as before). Lever `A_REFUSED_ARM_KEEPS_THE_DECISION`.
- **The spend is the war's own (PR-D1c).** `declare_war` stamps `declaration_alarm` + `declared_by` on the pair it opened (`war_instances[...]["diplo_key_meta"][pair]`, serialized by construction; `attach_pair_to_war_instance` carries both across a re-attachment). `coalition.league_spent_alarm(world, target, league_members=)` keeps whole `declared_alarm_outside_the_league` — the standing stamps of the target's LIVE pairs (`pair_status == "war"`) it declared against courts not in the dissolving league — capped by the slot as it stood; `dissolve_coalition` reads the members before clearing. Lever `THE_SPEND_IS_THE_WARS_OWN`.
- **A new war is not a spent league (PR-D1d).** `ai_diplomacy.league_offer_gate` also gates a war the PLAYER declared — `player_declared_this_war` (any live pair of the player's carrying `declared_by == player`) — on its opposing LEADER's break-ranks clause (lever `THE_LEAGUE_GATE_COVERS_A_DECLARED_WAR`, the chosen default), reason `war_not_spent` with its own display, threaded to the producer's refusal record, `evaluate_request_terms_affordance` and the resolver. Levers (a) `THE_LEAGUE_GATE_COVERS_EVERY_WAR` and (b) `THE_WAR_AGE_IS_THE_PAIRS` (the producer's war-age floor reads the player-with-leader pair's `reopened_turn`, stamped when a `resolved` pair is re-attached) stay measured and down. Mediation and `_settlement_offer_eligible_for_war` are untouched.


### 71.4 The Chunk 2 quick-win reserve (September 26, 2026)
- **AAR-22 — raw tags and in-place walk-ins.** The guarantee refusal prints the court (`display_nation`) and the protector's adjective (`nation_adjective`), never the scenario tag. `naval_executor.intercepted_at_sea_line(outcome, marshal_name, target, sea_line)` is the ONE interception sentence — "the British squadrons catch the transports off Munster"; an unnamed coverer reads "the enemy squadrons". The undefended-capture exit of `_execute_attack` says "<marshal> takes <province> where he stands!" when the corps already stood there (the AI's priority −1 capture and a player's attack on the province under his feet), and keeps "marches from X into Y unopposed!" for a real march.
- **AAR-16 — foreign works name their owner (`world_state.FOREIGN_WORKS_NAME_THEIR_OWNER`).** `WorldState._construction_complete_message(region, building_type)` builds both the building and the watchtower completion lines: a foreign owner's work reads "Austria completes a market at Vienna." ("stables" takes no article), our own keeps "Construction complete: Market in Paris!". The event's `nation` is unchanged (PT-E6), so the fog filter and the briefing's player-only whitelist read as before. `campaign_log.format_event_oneliner(event, player_nation="")` renders a foreign `building_completed` row as "Austria completes a market in Vienna" when the caller names the player; `GET /campaign_log` and the Gazette do, every other caller is byte-identical.
- **AAR-30 — the capital discount is ours only (`economy_executor.THE_CAPITAL_DISCOUNT_IS_OURS_ONLY`).** `_recruit_cost_terms` applies the 25% discount only where `capital_is_the_nations_own(region, world, nation)` — the province is the recruiting nation's AUTHORED capital (`get_nation_capital`), not merely `region_type == "capital"`. An occupied enemy capital and a captured foreign seat pay the ordinary price, for the AI through the same pricer (GR5). A call with `nation=None` (the legacy direct-call sites) keeps the region-type rule. The recruit event's `capital_discount` / `stability_premium` flags are the terms the pricer applied (`price_terms`), so the receipt, the note and the event cannot disagree.
- **AAR-18 — the desk breaks ground without a corps (`question_desk.THE_DESK_BREAKS_GROUND_WITHOUT_A_CORPS`).** "what can I build" with no place named prefers the province a corps of ours stands on (unchanged); with none on our soil it answers from the executor's own gate — `_first_own_region_that_can_build` walks our provinces, the capital first then by income, and returns the first where `region.can_build` allows anything — prefixed "No corps of ours stands on our own soil, Sire, but ground is broken without one." Our soil with nothing buildable: "Nothing can be built on our soil today, Sire."; no province at all: the old "nowhere to break ground".
- **AAR-14 — the remedy names only open ground (`dispatch.THE_REMEDY_NAMES_ONLY_OPEN_GROUND`).** `_supply_strain_candidate`'s neighbour scan skips a province whose holder is at war with us (`_ground_is_contested`) BEFORE the headroom and the move probe — a march there is an attack on its garrison, not a dispersal. A province with an enemy CORPS on it was already the move probe's refusal (measured), so there is no second rule for it.
- **AAR-13 — the danger flag follows the province (`dispatch.THE_DANGER_FLAG_FOLLOWS_THE_PROVINCE`).** `_collect_supply_attrition_turns` returns `{marshal: {province: [turns]}}`; `_derive_danger` counts the trailing consecutive run at `marshal.location` only and `_latest_supply_cause(world, name, region=)` reads the cause there. A per-marshal list handed in directly (the legacy shape the fixtures pass) still reads as "wherever he was". Lever down, the collector returns the legacy shape and the old flag ("Starving — supply has failed at Munich" the morning after he left Swabia) is reproduced. Pins `tests/test_sr2_quick_wins.py`.

### 71.5 SR-2d — The letter tells the truth (the Chunk 2 exit residues, September 26, 2026)
- **The letter subtracts what it carves (SR-2-X2; `settlement_offers.THE_LETTER_SUBTRACTS_WHAT_IT_CARVES`).** `_derive_status_quo_lines(world, war, settlement_terms=None)`: a province that any clause of the SAME package moves (`settlement_scoring.cession_shaped_regions` — `territory_cede` and `create_client`, the `region` / `regions` / `provinces` dialects) is never "retained" by anybody. The ratifier's retention line already read that way because it reads the map AFTER the appliers; the letter agrees with it now. `build_incoming_settlement_offer_popup` passes the offer's terms; the mailbox re-show (`/mailbox/activate` rebuilds the popup) inherits it. A letter that moves no soil is byte-identical to the map read.
- **The ratified settlement names itself on the rail (SR-2-X3).** `main._settlement_proposal_result_fields(result)`: a SUCCESSFUL result of `dialogue_type == "settlement_confirm"` carrying the ratifier's `settlement_result_feedback` declares `proposal_type "Settlement"`, `outcome "ACCEPT"`, `title` = the feedback's title ("Settlement Ratified"), `target_nation` = the war label and `resolved_pair_count`; every other result declares nothing (`{}`) and the PL-14 net composes as before. `_queue_informational_diplomacy_notices` prefers a result's own `title` over the composed "<type> <outcome-word>". The net's outcome is read off the ratification, never off absent proposal fields or the sentence's words.
- **The letter's rail row leaves with the letter (SR-2-X3's rider; `settlement_offers.THE_LETTERS_RAIL_ROW_LEAVES_WITH_IT`).** `_dismiss_offer_rail_row(world, offer_id)` retires the `INCOMING_SETTLEMENT_OFFER` row whose `details.offer_id` names the letter (`NotificationCollector.add` refreshes a repeated row's details to the newest letter's, so the standing row names the letter answered); called at the three roads that consume a letter — `_consume_offer_dialogue` (accept; the revision route's consume-here arm), the reject arm, and `consume_offer_by_id` (SR-2a's deferred consumption). Another letter's row stands.
- **The review carries the letter's figure (SR-2-X4 — NOT REPRODUCED; pinned).** The accept route stages the offered `settlement_terms` verbatim; the revision route seeds the PROPOSE table with them and Submit for Review keeps them; a ledger move between the letter and the review changes nothing. Measured at the wire: Δ = 0 on all three routes. The exit's "5,406 → 5,398" was two runs' letters (the EC-W4 price reads 0.15 × the payer's chest at production, and an unseeded probe turn moves that chest), not a re-price between letter and review.
- **The mediator is named on every surface (SR-2-X5; `settlement_offers.THE_MEDIATOR_IS_NAMED_ON_EVERY_SURFACE`).** ONE clause `good_offices_clause(mediator)` → "under Russia's good offices" (`with_definite_article(display_nation(...))`, so "under the Papal States' good offices"). Readers: the rail row (`turn_manager` — title "Russia offers good offices", message "<proposer>'s terms to settle <war>, under Russia's good offices. Asking N gold.", `details.mediator`), the `settlement_offer_arrival` dispatch event (`mediator`, the same message), the mailbox row (`DialogueManager.get_mailbox_items` — `summary_text` "Under Russia's good offices — Settlement offer: <war>", the clause FIRST because the row is cut at 72 characters; `summary` "<proposer> — Settlement Offer, under Russia's good offices"), and the REVIEW the accept arm opens (`mediator` + `mediator_interest` stamped on the staged dialogue and the mounted one; `message` and Talleyrand's line led by the clause, the staging's own sentence following unchanged — a vocative keeps its capital). The belligerent's own letter: no mediator key anywhere, the old title, sentence and row.



### 71.6 SR-2e — Standing orders reliable, part (i): SUPPORT at one action, AAR-8 / AAR-9 / AAR-10 / AAR-11, CRT-4 (September 26, 2026)
*SR-D3 ruled (c) first: the standing order — the multiplier the design already intends — made reliable before any new action point is minted. Part (ii) (CRT-5, "an answer is read closed") is §71.7.*
- **SUPPORT costs one action for every marshal (`marshal.A_SUPPORT_ORDER_IS_ONE_ACTION`).** `Marshal.strategic_order_ap(auto_upgrade=False, order_type=None)`: a `"SUPPORT"` order is 1; MOVE_TO / PURSUE / HOLD stay 2 (1 for a literal marshal and the sovereign; 1 for an auto-upgrade). Every site that prices or quotes a strategic order passes the order's type — the executor's pre-check, the issuance charge, the `move to` belt, the attack→PURSUE upgrade, the relationship-SUPPORT objection's buttons, `_build_strategic_options` (proceed AND compromise), the compromise's own charge, and the "Which marshal?" affordability check — pinned by an AST census (`order_type=` at every call). **The compromise is priced as the order it softens** (it can never cost more than insisting on it): a literal marshal's compromise is 1 where it was a flat 2. The help text says "support 1 AP".
- **A march keeps its tail through a reinforcement (AAR-10; `strategic.A_MARCH_KEEPS_ITS_TAIL`).** The A-C2 step no longer clears an arriving reinforcer's standing order ("its path is now invalid" — obsolete: an emptied path is re-plotted from wherever he stands); his order-bound QUESTION is spent (`clear_order_bound_interrupt` — he has just fought at or beside the ground it asked about), and a PURSUE that fought its own quarry takes the pursuit's one-turn pause (`last_combat_enemy` / `last_combat_turn`, read by `_should_auto_attack`). The battle reply names what resumes (`strategic.kept_order_line`: "Massena answered the guns and stands at Bohemia; his march to Vienna stands and resumes next turn." — an artillery corps "fired in support from …"), composed AFTER the withdrawal and rout blocks so a man routed off the field (whose order the forced-retreat path clears with its own notice) is not promised a march. **A corps moves once a turn:** `process_strategic_orders` skips a marshal with `reinforced_this_turn` (after the issued-this-turn skip, before the interrupt deferral) with an active row "answered the guns this turn … resumes next turn" — without it he marched twice in one end turn and heard his OWN battle as cannon fire. **GR5:** the AI's road-home rung (P1.2) takes the same skip. The latent road-home defect this also closes: a corps on its road home that answered a battle's guns lost the road at A-C2 and `offer_road_home` then read the loss as a refusal. The void event `order_voided_by_battle` still fires with the lever down and on the jealousy seam (the autonomous attacker's own order, a different seam).
- **A question the player cannot answer is never shipped (AAR-8; `strategic.A_QUESTION_ROW_IS_ANSWERABLE`).** `question_row_is_live(world, row)`: a `requires_input` row is live only while its marshal holds a stored question of the row's type — a standalone decision (last stand, muster confirm), or an order-bound one whose order still stands (the Ledger's `_is_halted` rule). `reconcile_question_rows(world, reports)` REPLACES a dead row (a new dict — the stored interrupt is the same object as the row) with `overtaken_question_row`: "Davout's question was overtaken this turn — he answered a colleague's guns and stands at Swabia. His march stands." Two nets: the end of `process_strategic_orders` (after pass 3 — a colleague's battle LATER in the same pass spent the question: measured, a cautious man asked "destination blocked", then Ney's arrival battle recruited him) and `turn_manager` where the end turn ships `strategic_reports` (the advance, the grievance pass and the autonomous marshals can spend a question after its row). No `.gd` change: the client queues only `requires_input` rows.
- **The guns must be our war (AAR-9; `strategic.THE_GUNS_MUST_BE_OUR_WAR`).** `cannon_fire_is_lawful(world, marshal, battle)`: a participant resolves (`_cannon_fire_nation` — a live marshal's nation, a `<region>_garrison`'s owner, or a destroyed man's TOMBSTONE nation: his battle row outlives him until the turn advances) to a nation `marshal.nation` is at WAR with, or a war enemy of his still stands on the field. The aggressive redirect requires it; any other battle his nation has a stake in (an ally's third-party war — the Creative AAR's Bavaria-vs-Austria under the French peace) gets at most the ASK, which says whose war it is ("Cannon fire at Tyrol, Sire. Bavaria and Austria are at war; France is not in it. Investigate?", `cannon_fire_war_clause`, the row's `not_our_war`). `_cannon_fire_concerns` reads the tombstone before failing open. **Riders:** the redirect's step loop keeps a refused FIRST step's own reason ("Massena is fortified at Tyrol and cannot move…" — it said "no road leads there" for every refusal); the end turn's `cannon_fire_redirect` event says `action_taken: "ask"` for an ask (it said "redirect").
- **The vindication verdict is bound to its order (AAR-11; `vindication.THE_VERDICT_IS_BOUND_TO_ITS_ORDER`).** The entry was keyed on the marshal's NAME and judged whatever battle he next led, on any order, any number of turns later (the AAR: an insisted `fortify` judged by an ordered attack on Charles five turns on). Now: `record_choice(..., executed_order=, turn=)` stores the order the answer RAN (insist → the original, trust → the alternative, compromise → the compromise) — only a fighting order with a target (`BINDABLE_ACTIONS`: attack, charge, pursue, move, march) can be judged, any other clears the entry; `resolve_battle(..., defender_name=, battle_region=)` resolves only a battle that is the order's own (its defender is the target, or it is fought at the target province) — another battle leaves the question standing; a legacy entry (no `executed_order`) is dropped unjudged; the executor holds the marshal's entry ASIDE while the player's next ORDER to him runs (`CommandExecutor._hold_aside_vindication` at the outermost frame — a read, an act of state, a reward or a standing order's own step holds nothing) and expires it if the order ran, hands it back if it was refused (`settle_held`); the defiance arm clears it (the insisted order never ran). A caller that binds nothing (the tracker's own unit callers) keeps the name-keyed road — the production record and resolve sites are pinned by census to bind.
- **The road law is read where it is quoted and where it is taken (CRT-4 — DESK-3, DESK-10, CQ-31's remainder; `strategic.THE_ROAD_LAW_IS_READ_WHERE_QUOTED`).** ONE road reader `strategic.march_road(world, marshal, dest, strategic_type="MOVE_TO") → (road, refusal, kind)`: the strategic issuance's own steps in its order — the weighted road for a march or a hold, the cautious man's avoid-set, `plot_route`'s lawful-first ladder (the verdict read for the player), `issuance_road_refusal`, S5-D2's closed-frontier refusal; PURE. ONE state reader `march_state_refusal(world, marshal)` (recovering, broken, engaged — the executor's sentences — and the action pre-check's figures). ONE arrival law `march_turns(road_len, movement_range)` = `0 if L ≤ r else 1 + ceil((L − r)/r)` (the order takes the first `r` provinces, the issuing tick is skipped, then `r` a turn — 32 of 32 driven arrivals on a quiet board). Readers: the strategic executor's issuance; the `move to <far X>` belt (player only — it walks the march's cautious road and refuses in its words; the AI's belt is byte-identical); the pre-objection battery (a `move` beyond his reach asks `march_road` first, so a cautious man no longer OBJECTS to a crossing the march refuses free); and the desk's reach answer (`question_desk._answer_reach_by_the_march`): "Yes, Sire — Murat can reach Orleanais from Franche-Comte this very turn — the march arrives on the order: …", "… in 3 turns: …", a visible foe on the road named ("Mack stands on the road at Swabia — the march will meet him there"), the refusal in the march's own words ("No, Sire — the crossing from Normandy to London is barred …"), the state first ("Not today, Sire — a march costs 2 actions and only 1 action remains today. Once he can: …"). Measured: the desk answered Yes where the march refused on 33 destinations × all 8 French marshals (264 cells) → 0 (a 250-cell re-drive at the endpoint: 0 either way). **Decided:** exact `move`/`march` parity is scoped to the ROAD LAW — `move to Swabia` refuses an enemy-held destination (a one-step verb) where `march to Swabia` goes into the contact flow, by design. **Filed, not built (CRT-4-X1):** the order-ETA surfaces (the dispatch's "N turns out", the per-turn report row's `turns_remaining = len(path)`, the Ledger Forces tab's "(N turns left)", the relay's "~N turns") are range- and skip-blind — owned by Chunk 6's dispatch pass (SR-6a), `BUG_FIXES.md` CRT-4-X1.
- **Balance:** `BASELINE_SERIES` + M1–M7 + the AI-V assurance pins byte-identical (81 passed). The SUPPORT price, the questions, the cannon fire, the vindication and the desk are player-only by construction; the two seams the AI shares — the reinforcement seam and the P1.2 road home — were measured by the AAR-10 recon on the 40-turn ambient run (7 reinforcement arrivals, all French, none carrying an order) and the series pin re-run with the slice in.



### 71.7 SR-2e part (ii) — CRT-5 "An answer is read closed" (IQ7-X7; September 26, 2026)
*Every dialogue family's typed answer is read by ONE closed grammar that fails closed — IQ-7's lesson (for an irreversible priced answer, write the allowlist out) generalised from the client petition to every letter, ultimatum, settlement, confirm and picker. Record `COMMAND_ROBUSTNESS_SPEC.md` §12.13.*
- **The grammar (`dialogue_routing.closed_answer`; lever `AN_ANSWER_IS_READ_CLOSED`).** A typed line answers a dialogue only when the WHOLE line is one of the dialogue's answer phrases — a whole option label in order (filler allowed in its gaps); a label's head word when exactly one option's label leads with it (on the typed road only if the head word is a dialogue keyword; any head word on the button road, `any_head_word=True`); a keyword whose action the dialogue offers — plus words from the written-out allowlist: the function words (`_CLOSED_FUNCTION_WORDS`), the address words, the pronouns (`_CLOSED_PRONOUNS`), the matter's own nouns (`_CLOSED_MATTER_NOUNS`: offer, terms, petition, ultimatum, settlement, peace, alliance, and what a counter is made of — gold, money, land), and the pick words on the nation list. Everything else — later, tomorrow, next turn, soon, if / when / once / unless / until, but, not, yet, instead, a bare foreign court, a marshal, an order verb — fails CLOSED: the line claims nothing and executes nothing. Its steps, in order: an action id spelled out answers; a question never answers (`line_asks_a_question`, IQ-7 R3-9 — tags included); a negation marker outside a self-negating answer token is no answer (FA-N2 — `decline to reject it` is built of answer words, so the allowlist alone cannot see it); the dialogue's own court and the provinces its matter names are blanked; another court is blanked only in an addressee shape (`Prussia's offer`, `the offer from Prussia`), so the court guard downstream speaks — EXCEPT a court an option's own label names, which is part of the answer (`A_LABEL_COURT_IS_THE_ANSWER`: the paradox's "Honor alliance with Bavaria"); `never mind <the matter>` dismisses ANOTHER matter when this dialogue offers no dismissal; two different answers claim nothing; the auxiliaries answer in statement order only (`we shall accept`, never `shall we accept` — defence in depth under the question guard). A client petition keeps its own grammar (`petition_plain_answer`).
- **The roads.** The `/command` router (`match_dialogue_answer`, after the client-petition branch) and the button road's free text (`handle_diplomatic_dialogue_response`). A line the grammar refuses is RE-PROMPTED IN PLACE — `closed_reprompt_message` ("A deferral, a condition or a second matter is not an answer, Sire — nothing was relayed …") when the line tried to answer (`closed_line_tried_to_answer`: it carried one of this dialogue's answer words), the honest "I don't understand that choice" otherwise; nothing mounts over the letter. The router's soft-stop fall-through, in order: the petition's court guard → the matter guard → the petition re-prompt → `court_mismatch_refusal_for_a_line` (an answer-shaped line naming another court: "… would be delivered to …") → the full matter guard for a line that tried to answer and names no marshal → `dialogue_line_reprompt`.
- **The objection answer (`objection_answer_is_plain`; lever `AN_OBJECTION_ANSWER_IS_READ_CLOSED`).** `trust`, `insist` or `compromise` answers a standing objection only beside closed filler (`_OBJECTION_ANSWER_FILLER`) and our marshals' names — `trust him tomorrow` carries out nothing (it carried out the alternative and fought); `I trust him` answers.
- **Measured:** the recon's census, 20 families × 19 deferral and condition tails: claimed 349 → 0 of 380; plain answers 121 → 127 of 140 (the break-treaty confirm answers `proceed` for the first time; none lost). **Balance:** player-only — a dialogue answer is the player's; `BASELINE_SERIES` + M1–M7 byte-identical.

## 72. THE SCORE MANDATE — CHUNK 3 FIRST CONTACT & COMMAND, "The desk answers" (September 26, 2026)

### 72.1 SR-3a part (i) — CRT-3 "A question never orders", with CQ-30 and CX5-L5-F2
- **The Cabinet reads the shared verdict (CX-X1; `llm_client.THE_CABINET_READS_THE_SHARED_QUESTION`).** `LLMClient._parse_with_mock_chain` computes ONE question verdict — `clause_guards.is_question(original_text, _question_subjects(game_state))` — and hands it to every `_parse_diplomatic_command(command_text, command_lower, question=)` call site. Inside, the shared verdict makes the line a question and OUTRANKS the mission words, so a question routes to `diplomatic_advisory` (or `diplomatic_feasibility` on a feasibility keyword) and never to the war-purpose chooser, a downgrade, a break or a mission; `question=None` (a direct caller) keeps the parser's own weak test (a trailing "?" or four openers) alone. The client door mirrors the SUBJECT RULE (`main.gd` `_is_advisory_question`: `DIPLO_MODAL_QUESTION_STARTS` + `DIPLO_FIRST_PERSON_SUBJECTS` — a modal lead with a first-person subject is SENT; `DIPLO_NEVER_IMPERATIVE_STARTS` — the copular / perfect leads are sent whatever follows; `will you …` and `do declare …` stay claimed orders); `tests/test_wo_slice7_cabinet_door.py`'s mirror re-runs the same three lists.
- **The tail stands the arms down only on an order (CXR1-2; `clause_guards.THE_TAIL_STANDS_DOWN_ONLY_ON_AN_ORDER`).** `_trailing_clause_stands_the_arm_down(rest)`: the never-imperative arm and the subject arm of `is_question` stand down before a comma-and-clause only when the clause OPENS with an order verb (`order_verb_re()`) — the inverted conditional (`Ney, should Mack advance, fortify`); a vocative (`…, Berthier`) or an aside (`…, tell me`) leaves the question standing.
- **A hedge is a question (CXR1-4; `clause_guards.A_HEDGE_IS_NOT_AN_ORDER`).** `_HEDGE_LEAD_RE` at the head of the line (after the `so / and / but / ok / well` prefix and an optional comma address): `perhaps`, `maybe`, `possibly`, `worth <verb>ing`, `it might / may / could be worth`, `might as well`, `I suppose`, `I guess`, `I wonder if / whether`. Read BEFORE the lead. `time to …` is not a hedge (the triage's ruling). A hedged dialogue ANSWER (`maybe accept`) is therefore a question too and fails closed — CRT-5's ruling, one line early.
- **A leading run hides no question (CXR1-5 / CXR1-N2; `clause_guards.A_LEADING_RUN_HIDES_NO_QUESTION`).** When no interrogative lead matches, `_leading_run_hides_a_question(text)` tries a run of one to SIX leading words (`_LEADING_RUN_MAX`), none an order verb and none a negation marker — an interjection, a filler, `just wondering`, `tell me`, or a NAME without its comma — and reads the remainder as a question only when it opens with `why not` or one of `_DELIBERATIVE_OPENER_RE`'s openers (`what / how about`, `is it time to`, `what say`). The bare subject-WH leads are deliberately NOT read behind a run (a comma-free relative clause stays an order).
- **The interjections are never an address (CXR1-N3).** `hmm hm hmmm um umm er erm uh ah oh eh huh` are in `clause_guards._NEVER_AN_ADDRESS` (`hey` is not — the Ney-slip repair owns it). The parser's meta-addressee arm (`CommandParser._apply_fuzzy_matching`, the `_leading_addressed_token` read for `META_ACTIONS | PARSER_ONLY_META`) consults `never_an_address` before treating the comma-marked run as an officer.
- **A court is a subject (L2-7b; `clause_guards.A_COURT_IS_A_SUBJECT`).** `llm_client._question_subjects` adds every court the parser knows (`_known_nation_names`) plus `nation_adjective(court)` and its plural (`Prussian`, `Prussians`); `clause_guards._names_a_subject` strips a leading `the ` from the opening run. Diplomacy has no fog: naming a court leaks nothing.
- **The retreat noun takes a possessive (CX5-L5-F2; `llm_client.THE_RETREAT_NOUN_TAKES_A_POSSESSIVE`).** `_retreat_is_a_noun` reads `_RETREAT_NOUN_WIDE_RE`: a determiner that may be a demonstrative (`this / that / these / those`) or a proper possessive (`Mack's`), up to two modifiers, an optional `line / route / path / road / avenue of` bridge, then the noun; `_ORDER_THE_RETREAT_RE` (`sound / begin / continue … the retreat`) still wins. What the sentence then means is the chain's (`cover Ney's retreat` is a SUPPORT of Ney; `cut off Mack's line of retreat` is the shrug).
- **A near miss asks (CQ-30; `combat_executor.A_NEAR_MISS_ASKS`).** In `guessed_target_refusal`'s `auto_resolved` arm, `_near_miss_of_a_roster_name(raw_words, world, marshal, shared_words)` — a player's target word (≥ 4 letters) equal to, or one typed mistake from (`parser._plausible_name_typo`: same first letter, an edit or two), the surname token of any marshal not of our nation, a token two commanders share skipped — sends the order to the ASK arm instead of disclose-and-proceed, with the fog-honest question "No foe of that name is in sight, Sire — whom shall <marshal> engage?" (`clarification.build_attack_target_clarification(..., question=)`) and the VISIBLE foes offered. Descriptions (`the weakest enemy`, `give them hell`) still disclose and proceed; the exact fogged name still refuses with "no intelligence".
- **Gates:** `tests/test_crt3_a_question_never_orders.py` (72), `tests/test_crt6_the_retreat_is_a_word.py` (21), `tests/test_crt2_the_name_is_never_replaced.py` (13); sweep `tools/_sweep_sr3a_i.json` 18/18; the CR-1 corpus 791/791; `BASELINE_SERIES` + M1–M7 byte-identical (the AI never parses text); `main.gd` parse harness EXIT=0, boot 0 `SCRIPT ERROR`.

### 72.2 SR-3a part (ii) — CRT-7 "The desk answers what the order would do", with AAR-17 / AAR-19 / AAR-23 / AAR-29 / AAR-31
The through-line the CR-6 triage named, stated as code: **every desk answer asks the SEAM that would refuse or charge the order.** Each rule sits behind its own lever whose down arm reproduces the row it closes (measured at the real `POST /command` on the shipped 1805 boot before a line was written).
- **The war question and its kin (AAR-17; `question_desk.THE_DESK_ANSWERS_THE_WAR_QUESTION`, the kinds in `_WAR_QUESTION_KINDS`).** Seven answers where there was one shrug: `wars` ("who am I fighting and why" — the war banner's OWN rows via `war_status.build_active_wars`, the coalition collapsed to its one war-level score with its members named, our stated purpose in LV-8's sentence, every opposing court's active design, a truce listed under truce); `allies` (`are_allies`, the engine's predicate, plus the clients whose `lord` is us); `safe` ("is Vienna safe?" — the province, its holder, our corps there, a GARRISON only where the cell is in view at PARTIAL+, and every visible at-war corps within two marches with the report's band; a fogged corps is never named and the answer says how far our intelligence reaches); `truce_clock` (`ARMISTICE_DURATION − armistice_turns`, the rule `_process_armistice_turns` expires the truce by, and which way it falls at expiry by the relation against `ARMISTICE_AUTO_PEACE_RELATION`; a court named that holds no truce is told its actual state); `war_effort` (national weariness — ours in the clear, each court's at war with us through `diplomatic_ledger._build_war_weariness_line`, the courts it cannot read said so); `news` ("what happened last turn" — the morning dispatch's headline and events, or "the campaign has just opened"); and "what does X have with him" on the fact desk's `how_many` arm (`name5`). Diplomacy has no fog; the field does, and every field arm reads `get_visible_enemies` / the intel store.
- **A past-tense WH lead is a question (DESK-14; `clause_guards.A_PAST_TENSE_WH_IS_A_QUESTION`, `_PAST_TENSE_AFTER_WH_RE`).** `what happened`, `what became of`, `what went wrong`, `what occurred / transpired / befell / changed`, `what came of` — a closed list (`what took Vienna` is an order one word over and stays out). Before it, "what happened last turn" fell through `is_question` to Berthier's raw shrug.
- **The what-if is fog-honest (DESK-1; `THE_WHAT_IF_IS_FOG_HONEST`).** `_answer_what_if` reads fog FIRST: a foe whose cell is below PARTIAL is "no word of his whereabouts — there is no battle to weigh; scout for him before naming him"; a prisoner is answered through `prisoners.prisoner_refusal` (the cell named only in view). A seen foe out of reach still names his province.
- **The what-if refuses like the order (DESK-4; `THE_WHAT_IF_REFUSES_LIKE_THE_ORDER`).** Before any muster: `combat_executor.friendly_fire_refusal` (an ally, a vassal, our own — "the order would be refused, and nothing spent"), then the executor's own armistice block (`CommandExecutor._make_diplomatic_error`); a court at PEACE is not a refusal and the answer says the order would first put the declaration to the player. **Rider:** `_make_diplomatic_error` printed `armistice_cooldowns` — written ONCE at the truce's start (5, or the pair-exit floor) and never decremented — as "turns remaining" on every turn of the truce; it reads the truce's clock now, pluralised.
- **The price is the quote (DESK-2; `THE_PRICE_IS_THE_QUOTE`, `_answer_levy_price`).** `economy_executor.recruit_quote` (CN-1's single source) at the bare order's ground — the capital — first; where it refuses for want of a receiver, the cheapest levy a standing corps of ours raises, quoted AS the order that raises it (`recruit infantry in Rhineland`, the recipient, the men after the field cap, the gold); where nothing raises, the executor's own refusal (the gun remedy, the chest against the price). The counsel's levy line reads the same quote (`counsel.THE_LEVY_LINE_IS_THE_QUOTE`).
- **The income sentence sums (DESK-5; `THE_INCOME_SENTENCE_SUMS`, `_NET_LABELS`).** Built from `ledger.NET_GOLD_COMPONENTS` with their signs — "In: … Out: … Net ±N a turn" — so the figures named sum to the Net stated by construction, and a component added to the ledger prints (by its key) without a label here.
- **Who is winning reads the banner (DESK-7; `WHO_IS_WINNING_READS_THE_BANNER`, `_banner_rows` / `_row_name`).** The HUD's rows, not the courts with marshals on the board: the coalition is ONE war-level score with its members; a court whose army is elsewhere is still named; a truce is listed under truce.
- **The router reads whole words (DESK-8 / DESK-14; `MetaExecutor.THE_ROUTER_READS_WHOLE_WORDS`, `question_topic`).** The war effort, the allies, the treaties and the designs point at the Diplomatic Ledger; the war's own words at the banner; the acts of state at the Cabinet — "effort" no longer contains "fort".
- **The counsel reads the action points (DESK-9; `counsel.THE_COUNSEL_READS_THE_ACTION_POINTS`, `END_TURN_LINE`).** No military line when the military actions are spent, no purse line (`recruit` / `build` / `repair` are administrative) when the administrative ones are; `end turn — no military actions remain today` is named first.
- **The counsel reads the refusals (DESK-16, DESK-6; `THE_COUNSEL_READS_THE_REFUSALS`).** The works and the drill are offered only where `tactical_executor.fortify_refusal` / `drill_refusal` return nothing; a fortify from NEUTRAL needs two actions (the executor's own auto-shift) and is not offered on one; `_is_free_to_order` reads `drilling` / `drilling_locked`, the flags a Marshal carries (never `is_drilling`, which none has).
- **The counsel spreads the orders (DESK-13; `THE_COUNSEL_SPREADS_THE_ORDERS`).** One corps per line where the roster allows; a corps that marched today is not marched again; the march named is the lawful road (`move_refusal_probe`) that closes on the nearest enemy we can see (`get_distance`), never the road back. The attack candidates keep roster order (co-located first, then adjacent) — the boot's first line stays `Ney, attack Mack`, the line every first-contact door quotes; **the odds are the muster's business** and the what-if answers them.
- **The counsel reads the crossing (AAR-19; `THE_COUNSEL_READS_THE_CROSSING`, `_crossing_open`).** An adjacent attack is offered only where `naval.crossing_check_reach` — the attack's own gate — allows it; `Marmont, attack Moore` across the shut Channel is never printed.
- **The insist arm names its price (AAR-23; `tactical_executor.THE_INSIST_ARM_NAMES_ITS_PRICE`, `insist_terms(world, marshal, action) -> (ap_cost, note)`).** `(2, "he must first go defensive")` for a fortify from NEUTRAL, `(face value, "")` otherwise; the tactical objection payload carries `insist_ap_cost` + `insist_note`, its sentence says "(Insisting costs 2 actions — he must first go defensive.)", and `objection_dialog.gd` renders "Proceed as Ordered (2 AP — he must first go defensive, −N trust)". Display only — the executor charges as before.
- **Berthier suggests only orders the game takes (AAR-29; `LLMClient.BERTHIER_SUGGESTS_ONLY_ORDERS_THE_GAME_TAKES`, `sanitise_berthier_reply`).** The recovery prompt hands the model the counsel's own lines ("Orders the board takes this morning", `what_can_i_do`) with the instruction to quote only from them; the live reply's quoted suggestions are then read back through the fast parser (`_quoted_order_is_taken`: matched, a real order, no refusal, no question, not the diplomatic family the client redirects) and each that fails is replaced by the counsel's next order or cut. Deterministic, offline. The IQ9-X3 provenance half stays SR-3c's.
- **The objection names its concern (AAR-31; `strategic_executor.THE_OBJECTION_NAMES_ITS_CONCERN`).** `_generate_objection_message` reads the strategic type as its verb (`move_to` → `move`, `pursue` → `attack`) so the personality arms fire, the cautious march arm names the road, and the default names the order and its object — never "I have concerns about this order, Sire" alone.
- **Our own fallen are answered (DESK-15; `OUR_OWN_FALLEN_ARE_ANSWERED`, `own_fallen_names`).** The player's own tombstones join the desk's roster (`llm_client`'s `_marshals`) and `answer_question` answers them in the first person — "Marshal Ney fell at Rhineland on turn 1, Sire — his corps was destroyed and no order can reach him; the bench shows who may be commissioned in his place"; a DISMISSED marshal is not mourned (FA-47's rule).
- **DESK-11** (the muster prints display names) was already landed by row EP F2 and is pinned here; **DESK-12**'s dead `at peace with` half is deleted with its reason at the pattern.
- **The recovery prompt's counsel section is behind its own lever** (`prompt_builder.THE_RECOVERY_PROMPT_NAMES_THE_COUNSEL`): down, the prompt is the pre-slice prompt byte for byte — which is how the authored IQ-9 recovery cassette's re-stamp is attributed to this section alone.
- **Gates:** `tests/test_crt7_the_desk_reads_the_order.py` (110 — every row at `POST /command` on the shipped boot, a lever-down pin per rule, every counsel line on the boot sent through `/command` and none refused); sweep `tools/_sweep_sr3a_ii.json` 39/39 killed, 0 INERT at close (two first INERT, both the slice's own pins re-staged to the case that binds); two pins re-seated consciously (the CX-2 levy line on the quote; the session-3 armistice refusal on the truce's clock); `BASELINE_SERIES` + M1–M7 byte-identical (display and parser only — the AI never parses text and reads none of these surfaces); ONE `.gd` (`objection_dialog.gd`): parse harness EXIT=0, boot 0 `SCRIPT ERROR`.

### 72.3 SR-3b — CRT-2 "The name is never replaced" (CQ-17, CQ-29; CQ-30 landed in §72.1)

A name the sentence gives is the one acted on, or the order is refused free — saying which name it read. Landing record `COMMAND_ROBUSTNESS_SPEC.md` §12.10.

- **A reward goes to its object** (`parser.A_REWARD_GOES_TO_ITS_OBJECT`; `reward_recipient_from_text`, read in `_apply_fuzzy_matching` so the mock and live roads agree). An ADDRESSED `grant_pension` / `revoke_pension` / `grant_dotation` goes to the first of our marshals named after the address; the addressee is decoration. `Davout, grant Ney a rente` pensions Ney; `Davout, endow Ney with Swabia` endows Ney.
- **A fallen object is named as fallen** (`fallen_reward_object_refusal`, kind `fallen_recipient`, in `main.VERBATIM_PARSE_REFUSAL_KINDS` with WO-1's `enemy_addressee`): a reward naming one of our fallen — addressed or not — answers with the desk's DESK-15 sentence (`question_desk._answer_own_fallen`, FA-47's dismissed-is-not-dead rule kept) and spends nothing.
- **Accents never hide a name** (`llm_client.ACCENTS_NEVER_HIDE_A_NAME`, `fold_accents`): the fast parser's name matcher folds accents on both sides, one character for one, so positions are unchanged.
- **The named ground is kept** (`llm_client.A_NAMED_GROUND_IS_KEPT`, `named_ground_phrase`): for recruit / build / repair, the province after the last "in"/"at" — and `repair`'s direct object — is kept when no known name matched it. Never a place: a manner ("at once", "in haste"), a generic ("the capital"), a formation ("Ney's corps"), the thing mended ("the damage"). A further clause word, including another "in"/"at", ends the place.
- **The executor resolves or refuses** (`economy_executor.A_NAMED_PROVINCE_IS_NEVER_REPLACED`, `_reread_named_province`): an unresolved named province goes through the region matcher (the march road's own answers — the typo read, the nation's provinces, "not found" refused free); the verb re-runs on the read province and the FA-54 grounding note rides WHATEVER answer returns. A recruit is never raised at the capital in its stead. Exact names (every AI order) never reach the matcher. A NAMED marshal keeps PF-7's road — he levies where he stands.
- **A hold the game placed reads no name** (`strategic_executor.THE_DEFAULT_HOLD_READS_NO_NAME`; `target_placed_by_the_game` from the strategic parser's default, or a generic hold the executor resolved): no grounding note on a bare / "here" / "position" / "our lines" hold; a typed name still discloses.
- **Gates:** `tests/test_crt2_the_name_is_never_replaced.py` (49 new, 62 in the file with CQ-30's 13); corpus +11 `crt2-*` rows (791/791 mock; the eight defect rows fail on the pre-slice tree); sweep `tools/_sweep_sr3b.json` 20/20 killed, 0 INERT at close; `BASELINE_SERIES` + M1–M7 byte-identical (structural); zero `.gd`. Filed: CQ-37 (idioms: `at once` before a clause, `hold fast`) → the Chunk 3 reserve; CQ-38 (a reward to two marshals drops the second) → CRT-11.

### 72.4 SR-3c — L-1 "The prompt turns around", with IQ9-X1 + IQ9-X3

Landing record `COMMAND_ROBUSTNESS_SPEC.md` §12.11.

- **The parse prompt is static first** (`prompt_builder.THE_PROMPT_IS_STATIC_FIRST`): rules, the output contract and the board-independent examples, then the board (our marshals, the order's addressee, the enemy, the map orientation, the examples that name an enemy in view), then the order. The sections are the shipped text cut at its own headers; down, the prompt is the pre-slice prompt byte for byte. The same order one battle apart shares ~15,800 characters (was 84).
- **The addressee rides the board** (`prompt_builder.addressed_marshal`; both providers pass `marshal_name` / `personality`): "## The Order Is Addressed To" with the personality the marshals block prints.
- **The static examples do not move with the board** (`_format_examples(part="static")`, `_example_names_stable`): our first two marshals, the first court at war with us and its capital; the enemy-naming templates ride after the board (`part="board"`) and name only an enemy in view; each template is taught once.
- **Prompt caching stays off** — its structural obstacle is gone; enabling it is the user's decision.
- **The retry reads the marshal** (`parser.THE_RETRY_READS_THE_MARSHAL`): on the CR-2 retry the fuzzy pass does not word-scan a marshal the live model did not name (`trust_marshal_reading`); a named marshal is still validated; the primary road is unchanged.
- **A failure names its road** (`parser.A_FAILURE_NAMES_ITS_ROAD`, `CommandParser._failure_road`, `ParseResult.live_consulted`): a parse failure carries the live provider's mode when a live call was made, else "mock"; a success still names whose reading it acts on.
- **The IQ-9 cassettes** were re-stamped by attribution (`tests/data/l1_prompt_restamp.json`); a future prompt change re-stamps the same way — never by re-recording.
- **Gates:** `tests/test_l1_the_prompt_turns_around.py` (29, incl. the 16-cassette attribution) + `tests/test_cr6_retry_rescues_the_word_scan.py` (14); sweep `tools/_sweep_sr3c.json` 18/18 killed, 0 INERT at close; corpus 791/791 + replay 6/6; `BASELINE_SERIES` + M1–M7 byte-identical; zero `.gd`.

### 72.5 The Chunk 3 reserve — the boot help teaches the desk; CQ-37 the idioms; AAR-25 the counter-punch announced

Landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 3 (the reserve line).

- **The boot help teaches the desk** (`main.gd` `_print_boot_help`): "Ask Berthier: “who am I fighting”, “is Paris safe”, “what happened last turn” — an answer costs no action". The release census (`test_release_build_2026_09_25.py`) posts every quoted phrase of the boot help on a fresh boot; each of these is the desk's answer at 0 actions.
- **"at once" is never a condition** (`clause_guards.AT_ONCE_IS_NEVER_A_CONDITION`, `_AT_ONCE_RE`): a "once" whose PRECEDING word is "at" is the adverb, in both readers — `condition_marker_spans` (the condition grammar's) and `strip_condition_clauses_with_handoff` (the refusing guard). "once more" / "once again" were already exempt by the FOLLOWING word. A leading or mid-sentence "once <X>" still refuses; CR-7-5's "once <friendly marshal> arrives" hand-off is unchanged.
- **"hold fast" / "hold firm" / "hold steady" are a bare hold** (`strategic_parser.NON_REGION_TARGET_WORDS`): at his own province, with no reading note. The parse was always HOLD; the word was read as the order's province at target resolution, so the pin lives at the wire, not in the corpus.
- **The counter-punch is announced the morning it opens** (`dispatch.THE_COUNTER_PUNCH_IS_ANNOUNCED`; status `counter_punch`, glyph » in `main.gd` and `dispatch_view.gd`), below a standalone decision and broken / retreating, above a standing order: "Threw back the enemy — may strike once, free, this turn only." The enemy phase runs before the tick, so a strike earned there reads one turn at the morning and expires at the next end turn.
  - **The foe it names** (`dispatch.counter_punch_foe_in_reach`): the nearest foe in sight within the attack's own reach (hops within `movement_range`, as `CommandExecutor._attack_target_beyond_range`), from `get_visible_enemies` — at war, standing, fog-visible; a prisoner is no foe. None in sight leaves the note general: a garrison in reach is a strike too.
  - **The works:** a fortified man is refused the attack until he unfortifies, so the note says so at the executor's price. `tactical_executor.unfortify_is_free` (a cautious marshal breaks camp free) is the ONE source the executor charges by and the note quotes; every man who can earn the strike is cautious.
  - **What outranks it:** a man locked in drill is refused every order, so the drill line stands for him; an order-bound pending question outranks it.
- **The IQ10-X residue** (the top bar at 2.0, the petition fold) is closed on the Sept 23 / 24 frames and the driven top-bar harness that runs in every suite — no layout on either surface changed since.
- **Gates:** pins `tests/test_sr3_quick_wins.py` 34; corpus +2 `cq37-*` rows (both fail with the lever down); sweep `tools/_sweep_sr3_reserve.json` 22/22 killed, 0 INERT; `BASELINE_SERIES` + M1–M7 byte-identical (measured — display and parser only, and `unfortify_is_free` is behaviour-identical); TWO `.gd` (`main.gd`, `dispatch_view.gd`), parse harness EXIT=0, boot 0 SCRIPT ERROR.

### 72.6 L-D — "The boolean road" (September 26, 2026)

Landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 3 (the L-D line); record `COMMAND_ROBUSTNESS_SPEC.md` §12.14; contract `docs/audits/LOCAL_PARSER_FEASIBILITY_2026_09_20.md` §6.4.

- **The witness is the DelegationMatch** (`delegation.delegation_witness(parsed, match)`; lever `KEYLESS_DELEGATION_READS_THE_MATCH`). CR-5's three-way split — the aggressive man engages (a delegation-inferred PURSUE), the cautious man scouts, the literal man asks — was gated on `parse_resolved_to_action`, a MODE gate, so a keyless player only ever saw the ASK. The router now passes `route_arm` the witness: True for a LIVE parse that resolved an action (unchanged), or for a deterministic `detect_delegation` match whose sentence carried no order of its own (the fast parser resolved nothing, so the delegation verb IS the order).
- **Guardrail (e) where it was written:** a parse that resolved an action WITHOUT the live model — `Ney, deal with the attack on Mack` (the fast parser reads `attack` out of the delegation's object) — is the incidental case and still ASKS. That verdict is the parser's own, so there is no second keyword list. `parse_resolved_to_action` and `classify_arm` are unchanged.
- **The other guardrails are the arms' own:** the phase gate (`AGGRESSIVE_ATTACK_ARM_ENABLED`), the objection-first single modal (the bad-odds confirm; the flavor floor withheld on any modal), the personality pre-flight (the arm follows the authored personality). The CR-5b flavor line stays live-only: a keyless player hears the deterministic, register-gated floor (`describe_aggressive_delegation`, `describe_cautious_delegation`).
- **Gates:** pins `tests/test_ld_the_boolean_road.py` 28; sweep `tools/_sweep_ld.json` 6/6 killed, 0 INERT; zero `.gd`; the delegation family green (1,825 passed across the 18 files that send or pin a delegation); `BASELINE_SERIES` + M1–M7 byte-identical (player-only).

## 73. THE SCORE MANDATE — CHUNK 4 COMBAT LEGIBILITY & MARSHAL DRAMA, "The field says what it will cost" (September 26, 2026)

### 73.1 SR-4a part (i) — the garrison says what it is (AAR-4, AAR-24)

Landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 4 (the SR-4a line).

- **ONE garrison module** (`backend/game_logic/garrison_report.py`). `garrison_effective(region, strength=None)` is the resolver's formula (`strength × (1 + terrain) × (1 + works)`) and its only copy in `_resolve_garrison_combat` (the AI's P4.25 estimate keeps its float copy). `works_bonus(region)` is `REGION_FORTIFICATION_DEFENSE_BONUS` for a WORKING fortification (a damaged one does not count). `garrison_view(world, region, viewer)` is the map summary's fog rule — our soil or FULL: ("exact", n); PARTIAL/STALE: ("band", …); else nothing — pinned against `get_filtered_game_state_summary` on every province. `describe_garrison(world, region, viewer)` is the FULL-read sentence: ours; another court's at peace ("(Bavaria's)"); at war, a detachment that fights to the last man, a garrison at or above `MARCH_HALTS_AT_GARRISON` that must be assaulted (a capital's regrows `CAPITAL_GARRISON_REGEN_PER_TURN` a turn up to the holder's tier target), or one below it that gives way to the first corps that marches in; and the works.
- **The scout** (`_execute_scout`, lever `garrison_report.THE_SCOUT_NAMES_THE_GARRISON`): a targeted scout names the garrison ("No field army stands there. Garrison: 25,000 — it must be assaulted — a march halts before it; a capital's garrison, it regrows 2,000 a turn up to 25,000.") with structured `garrison` / `garrison_detachment` / `works_bonus` keys on the intel event; the no-target scan counts only a corps AT WAR with us (it counted an ally) and bands each province's garrison at the scan's PARTIAL. Display only — the AI never scouts.
- **The desk** (lever `THE_DESK_READS_THE_GARRISON_FOG`): `is Vienna safe?` reads the garrison through `garrison_view` (a band at PARTIAL — it printed the exact figure, more than the map allows); `who is at Vienna?` names a known garrison (it said "No army stands in Vienna" over the 25,000 at FULL).
- **The assault's muster** (`CombatExecutor.AN_ASSAULT_NAMES_ITS_TERMS`; the player's assaults only — GR5, the AI reads no message): `assault_muster_line` prefixes both exits with the resolver's own terms — "ASSAULT — Ney storms the works at Vienna alone: 24,000 men, 31,187 in the assault's reckoning (+13% from the corps at his side), against a garrison of 25,000. Murat, Soult and Bernadotte do not join an assault on the works; the garrison breaks below 5,000." — the coordination share read off the stamp before the modifier is taken; the corps named are ours at his side or around the works; on the hold, `assault_regen_clause` adds "It regains up to N a turn (to 25,000)." from `WorldState.capital_garrison_regen` — the ONE rule the regen loop now applies (`capital_garrison_regen`: a capital held by a nation, never a detachment, `min(CAPITAL_GARRISON_REGEN_PER_TURN, target − strength)`). The resolver's, the attack entry's and the landing's `5000` read `MARCH_HALTS_AT_GARRISON`.

### 73.2 SR-4a part (ii) — the band weighs the field (AAR-32)

- **The fold** (`objection_v2.inferred_attack_effective_ratio(…, fold_modifiers=True)`; lever `THE_BAND_WEIGHS_THE_STANDING_MODIFIERS`): the ratio carries both leads' standing modifiers as the resolver applies them to the whole side — `(A + cA) × attack_mod / ((D + cD) × (1 + terrain + works) × defense_mod)`, the solo raw ratio and the solo outnumbered test passed as `combat.py` passes them, the personal fortify term not counted twice. Both reads are PURE: `get_defense_modifier(…, consume=False)` is new (it zeroed the literal marshal's clear-order bonus on every read). Read by `_build_muster_preview` (the printed band, the cautious marshal's confirm) and `muster_odds` (the glory gate on both boards); the CR-5 delegation gates keep the lead-only read. **Recorded limit:** the battle-time stamps (coordination, overwatch, the Emperor's Presence, the jealous man's solo bonus) are written only when a battle resolves, so the fold reads them at rest; the Presence is named by its own muster note. Two spies in `tests/test_napoleon_npv_review.py` now sample the battle's consuming read, not the band's pure one.
- **The posture note** (`CombatExecutor._posture_note`, rendered by `_format_muster_lines`): the defensive stance whenever it costs him ("Massena attacks from a defensive stance (−10%)" — off `Marshal.STANCE_ATTACK_FACTOR`, the stance's ONE home, read by `get_attack_modifier`; Iron Resolve's release exempts it), the net cost when his modifiers weigh below 1, the ground (public), and the defender's stack only where we see him at FULL.
- **Not changed:** the band's thresholds (favorable ≥ 1.0, even ≥ 0.7). The measured calibration (win 18% at a folded 1.0, 54% at 1.2, 82% at 1.4) is `DESIGN_REFINEMENT.md` AAR32-D1, the user's call.
- **Gates:** pins `tests/test_sr4a_the_fields_price.py` 24 + `tests/test_sr4a_the_band_weighs_the_field.py` 14; sweep `tools/_sweep_sr4a.json` 33/33 killed, 0 INERT; zero `.gd`; the 305-file scout, garrison, muster, glory and desk family green (15,833 passed, then the four conscious re-seats below); `BASELINE_SERIES` + M1–M7 + the AI-V assurance pins byte-identical (66 passed). The band is read once on the 40-turn series (turn 16, a player-side glory gate, the same 0.876 folded) and never by the AI's rung — measured by the recon, so the series cannot move.


### 73.3 The session exit's residue (September 26, 2026)

The session exit (`docs/audits/SR_SESSION_EXIT_2026_09_26.md`) read two played arms on both trees; its residue slice fixed four findings, each behind its own lever:

- **The safe answer reads the holder** (`question_desk._safe_for_the_holder`; `THE_SAFE_ANSWER_READS_THE_HOLDER`): on soil not ours the threats are the corps at war with its HOLDER that we can see (ours always; any other only in view, PARTIAL+), within two marches, and on enemy soil the holder's own corps are named as its cover. Our own soil reads as before.
- **The what-if names its marshal, reads the odds, and weighs a province** (`THE_WHAT_IF_NAMES_ITS_MARSHAL`, `THE_DESK_READS_THE_ODDS`, `THE_WHAT_IF_WEIGHS_A_PROVINCE`): the corps the question names is weighed, or the order's own answer given (`_the_named_corps` — the reach, then the engagement rule; a foreign subject is not ours to order; a name the desk cannot place classifies nothing, so the older entry cannot weigh a substitute). A province is weighed in `_execute_attack`'s sequence (`_answer_what_if_region`): reach, engagement, the crossing gate, a corps at war standing there (fought whoever owns the ground), then the holder (ours: nothing to attack; an ally: refused; peace or truce: the declaration first), the works, open ground.
- **The garrison exchange is ONE method.** `CombatExecutor.garrison_exchange(attacker_strength, attacker_effective, garrison_strength, garrison_effective)` is `_resolve_garrison_combat`'s loss arithmetic (the proportional exchange, capped; the FA-D28 floor; WO-3's +1). `garrison_report.garrison_fights` / `garrison_breaks` are the order's stand and collapse rules, read by the attack entry, the resolver and the desk. A forecast (`garrison_report.assault_forecast`) takes the resolver's reads purely — the coordination stamp restored for every marshal, the attack modifier with `consume=False` — and `assault_forecast_text` prints the assault's own muster plus, where the garrison is counted, the exchange; at PARTIAL a band and no figure that would give the count away (`assault_muster_line(garrison_shown=…)`).
- **A quantity "how" and a conjecture "what if" are questions** (`clause_guards.A_QUANTITY_OR_CONJECTURE_ASKS`): "how long / many / much / far / soon / often" and "what if" open no imperative. The rule stands on its OWN lever, outside CX-1's block — CX-1's corpus pin requires every golden row to pass under both arms of its lever.
- **The digest keeps what a first line pushes down** (`playtest_driver.continuation_line`): an assault's result after its muster (`THE_DIGEST_KEEPS_THE_ASSAULT_RESULT`, `assault_result_line`) and the answer after a lead-in ending in ":" (`THE_DIGEST_READS_PAST_A_LEAD_IN`).
- **Gates:** pins `tests/test_sr_exit_residue_2026_09_26.py` (68); golden corpus +6 `sre-*` rows; sweep `tools/_sweep_sr_exit_residue.json` 34/34 killed, 0 INERT; `BASELINE_SERIES` + M1–M7 byte-identical; zero `.gd`.
### 73.4 SR-4c — The drama's fuse (AAR-D3; the Jealousy gate re-opened, September 26, 2026)

Record `JEALOUSY_SPEC.md` §0.7 (authoritative); landing `SCORE_MANDATE_PLAN.md` §2 Chunk 4 SR-4c. Four levers in `backend/game_logic/jealousy.py`:

- **The laurel floor** (`THE_LAUREL_FLOOR`; `is_laurel(a, b)` = `battle_scale.is_a_battle(a + b) or battle_scale.is_decisive_exchange(a, b)`, read at call time; unreadable input counts). `record_battle_glory` records NOTHING for an engagement that is not a laurel — no victory/defeat points, no DR-1 stalemate point, no participant ±1 — so the ladder, the crown, envy and F4's rank-rise deed all read one floor. It binds on raid and remnant fights; on the 40-turn ambient board and the AAR arm it binds 0 times (every glory-bearing battle there is ≥ 1,000 dead).
- **The crown wants laurels** (`THE_CROWN_WANTS_LAURELS`, `CROWN_MIN_GLORY = 3`, `crown_floor()`): `recompute_crowns` crowns the ladder's unique top only at 3 glory or more (it was any point above 0). Both boards. Ties still vacate.
- **The audience waits** (`THE_AUDIENCE_WAITS`, `AUDIENCE_COOLDOWN_TURNS = 6`; `audience_wait` / `last_audience_turn` / `_stamp_audience`). A player marshal whose §6 confrontation card QUEUED is stamped (`jealousy_history["__audience__"] = {"turn": N}` — the `__levels__` idiom, zero new serialized fields); a later §6 fire within six turns queues no card, leaves the level's latch key unstamped (it retries on the pair's next fire) and adds to the fire line "He asked for an audience on turn N, and will not ask again before turn N+6." Never waits: escalation level ≥ `ESCALATION_PERMANENT_LEVEL` (the crisis tier) and F6's replacement of his own stale card. The grievance itself, its timers and its combat effects are untouched.
- **The fires say why** (`THE_FIRES_SAY_WHY`, copy): a lost crown says where it went (`_crown_lost_cause` → passed to a man / level between men, "no one wears them" / faded); the campaign-log row carries `why` + `successor` (a legacy row keeps the old sentence). A rival who is broken or falling back (alive, same army) cools the grievance with the reason "the rival is broken" — "His rival's corps is broken or falling back — there is nothing in him to envy until it rallies." — and "There is no one left to envy." is kept for a rival destroyed, taken or gone from the army.
- **Gates:** pins `tests/test_sr4c_the_dramas_fuse.py`; sweep `tools/_sweep_sr4c.json`; `BASELINE_SERIES` byte-identical across the five-arm flip (`tools/_sr4c_series_arms.py` / `.json`: 0 of 28 glory calls sub-floor, 8 nation-turns of crown withheld with the series unmoved, 1 audience wait — player-side); M1–M7 byte-identical (M7 turn 1 on both arms); zero `.gd`.
### 73.5 PC15-10 B1 — The Antechamber (the petition tier split; `PETITION_POPUP_REVISIT_SPEC.md` §4 F1, §6 Q1(a)/Q2(a) RULED)

Record `PETITION_POPUP_REVISIT_SPEC.md` §9 (the B1 row, authoritative); landing `SCORE_MANDATE_PLAN.md` §2 Chunk 4 (the SR-4c line). Lever `jealousy.THE_ANTECHAMBER` (False = every card a crisis — the channel as it was).

- **The tier.** Every petition builder stamps `tier` inside the petition dict (`petition_tier_for(kind, context)` — no new serialized field): AUDIENCE = §6 confrontation levels 0/1, §6b rivalry @−1, the NP-3 shadow petition (a once-a-campaign request the ruled table predates, classified here); CRISIS = §6 levels 2/3, rivalry @−2, Fontainebleau, war-weary. `petition_tier(petition)` reads a standing card (no tier — a pre-B1 save's — is a crisis).
- **The road.** `_push_petition` routes by tier: a CRISIS takes the slot and the PopupQueue (the modal, the end-turn `deferred_marshal_petition`, the load re-prime — all unchanged); an AUDIENCE takes the slot WITHOUT the queue and is announced once (`_announce_audience`): a HIGH rail row of type `jealousy_confrontation` / `rivalry_confrontation` (both left `RAIL_EXEMPT_TYPES` and joined the rail's maps — `AUD` / `RIV`, the `scales` glyph) whose button (`review_target` `marshal_petition`, "Hear him") opens the card, a routine dispatch line (`marshal_audience`, capped with the pass's drama), the Generals card's chip (`build_glory_card_fields.seeks_audience`) and the top bar's badge (`marshal_audience` on every envelope, `_marshal_audience(world)` → `audience_summary`). The card is served on demand by **`GET /marshal_petition`** (affordability re-derived; a stale card retired with "The moment has passed — X no longer presses the matter.") and answered at the unchanged `POST /marshal_petition_response`.
- **Contention.** One card at a time. A CRISIS arriving while an AUDIENCE holds the slot EVICTS it (`_evict_audience`): the audience's latch key (`pair@Ln` / `pair@value` / `shadow@name`) and its SR-4c clock are un-stamped so it returns on the pair's next fire, its rail row goes, and the dispatch says "X's audience is set aside for a graver matter; he will ask again." Audience-vs-audience, audience-vs-crisis and crisis-vs-crisis: blocked, key unstamped (the B0 semantics).
- **Retirement.** An audience has no delivery seam, so the per-turn re-push asks the FA-S17-D4 liveness predicate first (both tiers): a card whose grievance has cooled is retired, its rail row with it, and an audience says "Berthier notes that X no longer presses the matter." (The per-kind predicates, supersede and the load-validity sweep are B2.)
- **The client.** `api_client.get_marshal_petition`; `main.gd._open_marshal_audience` (from the rail row's review target and the Generals chip's `audience_requested` signal; refused while a modal is open) shows the same `marshal_petition_dialog`; `top_bar.update_audience_badge` ("Generals (1)", amber, the name in the tooltip).
- **The driver.** Policy dial `audience` (`open` default — hear it when the envelope names it, the `petition` dial choosing the arm; `ignore`), logged as `POPUP marshal_audience`, so modals and audiences are two counts.
- **Measured:** **Measured on the session exit's AAR arm (18 turns, `--objection insist --diplomacy accept`, the driver's `audience open`):** where 13 petition modals had interrupted the campaign (11 after SR-4c's clock), **2 modals** remain — the Bernadotte–Ney breach (turn 10) and Lannes's level-2 crisis (turn 13) — and **9 audiences** were heard from the antechamber, one harsh-words audience set aside for the crisis on turn 13. `BASELINE_SERIES` byte-identical (the channel is the player's court); M1–M7 untouched (no combat); sweep `tools/_sweep_b1.json` 21/21 killed, 0 INERT; Godot parse harness EXIT=0; boot 0 SCRIPT ERROR.


### 73.6 The Chunk 4 reserve (September 26, 2026)

Landing `SCORE_MANDATE_PLAN.md` §2 Chunk 4 (the quick-win reserve line); rows `BUG_FIXES.md` AAR4-X1, AAR24-X1/X2/X3, AAR10-X1, SRX-7, SRX-8 and `DESIGN_REFINEMENT.md` AAR32-D1. Pins `tests/test_sr4_quick_wins.py`, `tests/test_sr4a_the_band_weighs_the_field.py::TestTheFavorableLine`, `tests/test_playtest_driver_instrument.py::TestSRX7TheUnratifiableTableCloses`, `tests/test_tutorial_unbreakable_2026_09_23.py::TestTheLessonRunsOnItsOwnDraws`; sweep `tools/_sweep_sr4_reserve.json`; attribution `tools/_sr4_reserve_series_arms.py` (+ `.json`); measurement `tools/_aar32_the_favorable_line.py` (+ `.json`). Every row stands behind its own lever whose down arm reproduces the row.

- **The captor raises his own garrison (AAR4-X1).** `WorldState.capture_region` — the ONE capture seam — clears the loser's garrison and its detachment flag when a province changes hands by force; a return to the same hands is no capture, and a treaty cession never passes here. A captured capital's garrison then grows for its new holder from nothing through `capital_garrison_regen` (the holder's tier, 2,000 a turn), so a scout of a captured capital reports the captor's garrison. Both boards (GR5). Lever `world_state.CAPTURE_CLEARS_THE_GARRISON`.
- **A gun corps does not storm the works (AAR24-X1).** `garrison_report.gun_corps_assault_refusal`: an artillery corps ordered to `attack` or `bombard` a province a fighting garrison holds, with no enemy corps at war standing in front of the works, is refused at the executor's pre-objection battery — free, before any objection, counter-punch or charge — with the reason and the remedy ("Infantry or cavalry must carry Vienna. Nothing was spent."). The AI's P4.25 has always kept the rule. Lever `garrison_report.GUNS_DO_NOT_STORM_WORKS`.
- **The counter-punch rides the assault (AAR24-X2).** The garrison exit of `CombatExecutor._execute_attack` carries the COUNTER-PUNCH line and `free_action` when the blow was spent there, as the field and capture exits do. The executor's Aug-30 belt had made the TYPED road free but silent; the insist road (`meta_executor._execute_post_objection`) and the AI never pass that belt and paid an action for the free blow. Lever `combat_executor.COUNTER_PUNCH_CREDITS_THE_ASSAULT`.
- **The objection reads what the attack engages (AAR24-X3).** `objection_v2.attack_engages`: the named marshal; for a province, the enemy the executor engages there (`get_enemy_at_location_for_nation`), else the garrison the assault's own rule says fights. `get_target_intel_level`, `_get_attack_odds_ratio` and `_check_attack_target_fortified` read it. A garrison is priced by `garrison_assault_price` — the garrison behind its ground and works over the attacker in the assault's reckoning (`garrison_report.assault_forecast`), exact at FULL, a band's midpoint at PARTIAL / STALE — and a cautious marshal's objection says that price (`garrison_objection_quote`, handed the world by the executor: a count and the expected loss only at FULL, "our intelligence gives no count" below). Measured: 60,000 against Vienna's 25,000 no longer objects "the enemy is too strong" (the price is 0.41); "attack Swabia" with Mack standing there prices as "attack Mack". Player-only (the AI never objects). Lever `objection_v2.THE_OBJECTION_PRICES_WHAT_THE_ATTACK_ENGAGES`.
- **Rule 12 is the guns' rule (AAR10-X1 — DECIDED).** `moved_this_turn` is set when a battery limbers and marches (and on a pursuer halted by a last stand); a foot or horse corps that marched may still answer the guns — the reinforcement is itself a same-day march to an adjacent field, priced by its arrival roll. A gun that limbered this turn now says so on the muster (`guns_limbered`: "limbered his guns and marched this turn — they cannot unlimber in time"); the reinforcement cooldown keeps "has already marched this turn". Display only. Lever `combat_executor.GUNS_LIMBERED_SAY_SO`.
- **The favorable line (AAR32-D1 — RULED September 26, 2026, by the user's direction).** The band's favorable line weighs the GENERALS with the resolver's own skill terms — `combat.tactical_dice_bonus` / `dice_damage_multiplier` / `shock_damage_multiplier` / `defense_casualty_share`, named out of `CombatResolver` arithmetic-identically and read by `objection_v2.generalship_factor` relative to a 5/5/5 pairing: "favorable" iff the folded ratio × the generalship factor ≥ `FAVORABLE_WEIGHED_RATIO` = 1.7. Measured over the real roster (7 French × 8 Austrian / Russian / British / Prussian commanders, 200 seeded fights each, open ground): at the old folded 1.0 line the attacker won 6.8% (0–30% by pairing) and 89% decided nothing; at a weighed 1.7 every pairing wins 58–70% (mean 59.7%) and none loses. "even" says what it promises (`odds_band_note`: "a hard fight that may well decide nothing", or below a weighed 1.0 "a hard fight that may go against us"), printed after the word on the muster's band line. "unfavorable" (folded < 0.7 — CA9 row 2's gate, the glory gate on both boards) is untouched, so no decision moves; the men-only CR-5 reads keep the folded 1.0 line. Lever `objection_v2.THE_FAVORABLE_LINE_WEIGHS_THE_GENERALS`.
- **The driver closes an unratifiable table (SRX-7).** Under an accepting policy the driver still presses one harsher dial on a settlement table the engine cannot ratify (the first answer every archived arm gave); if the table it re-shows still cannot be ratified it closes it (Back Out / withdraw / decline) and the digest line says why ("closed — still unratifiable after one harsher dial: …"). Per answer chain. Lever `playtest_driver.UNRATIFIABLE_TABLE_CLOSES`.
- **The lesson runs on its own draws (SRX-8).** The School of War's path is RNG-shaped — the engine's combat rolls, the objection's mood roll and the defiance roll draw on the unseeded module RNG — so a driven pin that needs the tutor on a given card by a given turn passed or failed on the luck of the process (measured: the Cabinet pin failed 1 run in 8 as its class, the tutor still on the objection lesson at turn 3; the "after its sibling" order the row recorded was how many draws ran first, not a leaked object). The `lesson` fixture runs the lesson on ONE fixed draw sequence (`_lesson_draws`, `LESSON_RNG_SEED` = the sha256 of "tutorial:lesson") and hands the caller's state back. The boot draws nothing from the module RNG (pinned). Test hygiene only — no production code.
- **Measured.** `BASELINE_SERIES` byte-identical across four arms with the reach counted (`tools/_sr4_reserve_series_arms.json`): the garrison lever fired once on the ambient board — one 10,000-man garrison cleared at a capture — and moved neither the series nor the end-state provinces; the counter-punch lever never fired there (no AI corps stormed works on a banked blow). M1–M7 + the AI-V assurance byte-identical (81 passed). Sweep `tools/_sweep_sr4_reserve.json` 29/29 killed, 0 INERT. The 176-file garrison, objection, muster, counter-punch, favorable-word and driver family green (8,639 passed) with no pin re-seated; the tutorial pin green alone, after its sibling, as its class (10 of 10), as its file and in the full suite. Zero `.gd`.

### 73.7 The session exit of September 27, 2026 — its residue

Memo `docs/audits/SR_SESSION_EXIT_2026_09_27.md` (SR-4c, B1 and the Chunk 4 reserve on three played arms against `23bd2e57`: the two committed exit arms and Chunk 4's evidence arm `tools/playtest_scripts/sr_exit_chunk4_field.json`); landing `SCORE_MANDATE_PLAN.md` §5; rows `BUG_FIXES.md` §Score Mandate Session Exit (September 27). Pins `tests/test_sr_exit_residue_2026_09_27.py` 17; sweep `tools/_sweep_sr_exit_residue_2026_09_27.json` 6/6 killed, 0 INERT; attribution `tools/_sr_exit_residue_2026_09_27_series_arms.py` (+ `.json`).

- **The crisis is not an audience (SRX-9).** B1 made "an audience" the routine tier's word; the §6 confrontation's title now follows its tier through `petition_tier_for` — an AUDIENCE card "Marshal X seeks an audience", a CRISIS card (level 2+) "Marshal X demands to be heard". Display only. Lever `jealousy.THE_CRISIS_IS_NOT_AN_AUDIENCE`.
- **A spent corps does not share the field (SRX-10).** `CombatExecutor._muster_reason`'s CO-LOCATED arm reads the resolver's own exclusions (`_get_casualty_participants`): a corps broken, retreated this turn or still recovering returns `broken_recovering` ("is in no condition to fight") instead of "shares the field". It reaches the band on both sides of the muster, the "does not stand alone" and shared-casualty lines, and `muster_odds` (the glory gate, both boards). A drift pin holds the arm's verdict equal to the participant rule flag by flag. Lever `combat_executor.A_SPENT_CORPS_DOES_NOT_SHARE_THE_FIELD`.
- **Measured.** The exit found SRX-10 on the evidence arm's turn 7 (a recovering Archduke John priced into "even — a hard fight that may go against us" before Murat broke Mack alone, 6,247 to 594). A two-arm flip: the lever changed 6 of 849 muster verdicts on the ambient board and moved no decision — `BASELINE_SERIES` byte-identical on both arms, the end-state provinces too; M1–M7 + the AI-V assurance byte-identical (81 passed). The jealousy family (6,100 passed) and the muster family (4,519 passed) green.

### 73.8 PC15-10 B2 — The petition dies with its subject (`PETITION_POPUP_REVISIT_SPEC.md` §4 F2 + F10, §6 Q3 CONFIRMED; September 27, 2026)

Record `PETITION_POPUP_REVISIT_SPEC.md` §9 (the B2 row, authoritative); landing `SCORE_MANDATE_PLAN.md` §2 Chunk 4 (the SR-4c line). Pins `tests/test_b2_the_petition_dies_with_its_subject.py` 32; sweep `tools/_sweep_b2.json` 25/25 killed, 0 INERT; attribution `tools/_b2_series_arms.py` (+ `.json`). Levers `jealousy.THE_PETITION_DIES_WITH_ITS_SUBJECT`, `jealousy.THE_NEWER_WORD_SUPERSEDES`, `world_state.THE_LOADED_POPUP_IS_STILL_TRUE`.

- **One predicate, every kind (F2).** `jealousy.petition_retirement_reason(petition, world)` returns `""` while a card still stands, else why it retires:
  - a §6 confrontation: `absent` (the man cannot press it — gone, broken to nothing, captured), `cooled` (he no longer resents the colleague it names), or `moved_on` (**S7**: the stamped `escalation_level` is read at last — a card written a rung behind the pair's live level never serves);
  - a §6b rivalry: `absent`, or `mended` (the STORED value between them — S4's rule, never the derived one — rose above the transition the card announced);
  - Fontainebleau: `provided` (no named petitioner still erodes);
  - war-weary: `court_gone`, or `at_war` (a war begun by another road — the stored declaration dies with it);
  - the shadow petition: `absent`, or `no_shadow` (he no longer stands on his sovereign's province).
  `petition_is_still_live` is its negation. No numeric TTL.
- **Every seam asks:**
  - the per-turn re-push, both tiers;
  - the ordinary drain — `main._pop_deliverable_popup` reaps a stale card and delivers the next popup in the same cycle (it was the one delivery seam that never asked);
  - the end-turn `deferred_marshal_petition` key — it retires at once instead of leaving the card for the next re-push;
  - the antechamber's `GET /marshal_petition` — the message names why;
  - the answer — `handle_petition_response`, for every kind but the §6 confrontation (which keeps A3's pinned guard), returns "The moment has passed — … Nothing was spent." and charges nothing;
  - the load (F10, below).
- **Nothing retires silently (Q3).** `jealousy.retire_petition(world, petition, reason)` is THE retirement: the slot, the queue copy and the antechamber's rail row go, and ONE receipt line — `petition_retired`, "Berthier notes that …", naming who and why — rides the turn events. It is whitelisted in `dispatch._DISPATCH_EVENT_TYPES` and exempt from the drama cap (`JEALOUSY_NARRATION_EXEMPT`: a receipt collapsed into "…further matters" would be semi-silent — B0's F3 reasoning). B1 had retired a stale CRISIS in silence.
- **The newer word supersedes (F1 item 5).** In `_push_petition`, before the occupancy rule, a card of a pair kind (`jealousy_confrontation` / `rivalry_confrontation`) about the same two men, in either order (`petition_supersedes`), replaces the standing card with a `superseded` receipt.
  - The older card's latch key stays stamped: its moment is subsumed, not withdrawn. That is what distinguishes supersede from B1's eviction of a DIFFERENT pair's audience (latch un-stamped, so it returns).
  - The mutual spiral's level-3 card from the other man now reaches the player instead of being blocked behind his rival's level-2 card.
- **The load asks too (F10).** `WorldState._retire_stale_restored_popups()` runs at the end of `from_dict`, once the marshals, treaties and dialogues are back. It retires:
  - the marshal petition, on F2's predicate (after the S9 re-prime, which it undoes for a stale card);
  - the rebellion warnings PC15-17 retired inline — now each with a receipt;
  - an envoy or settlement letter whose `dialogue_id` the manager no longer holds, or whose court has left the active nations;
  - a Proclamation for a nation with no formation record, or no longer active.
  Each leaves a `popup_retired` receipt ("Berthier notes that …", with its `slot`). `PopupQueue.to_dict`/`from_dict` — a third serialization path read by no production code — are deleted; `PopupQueue.snapshot()` is inspection only (persistence rides the world's popup properties).
  **A load primes no cache.** The pass reads `get_active_nations()` (and a war-weary card's predicate does too), which fills the per-turn nation and region caches; `from_dict` never filled them before, and a caller that re-draws the map straight after a load (every fixture that strips a province off a copied world) read the stale cache — four IQ-1 economy pins, found by the pre-commit hook. The pass ends with `invalidate_active_nations_cache()`.
- **Measured.** `BASELINE_SERIES` byte-identical on both arms of `tools/_b2_series_arms.py`, with the reach counted: the ambient board queues 23 petitions (re-pushes included) and retires ONE — a cooled confrontation, identical on both arms. There is no rivalry mend, no Fontainebleau and no supersede on a passive France, which is why the series cannot move (the channel is the player's court; F10 runs at load, which the sim never does). M1–M7 + the AI-V assurance byte-identical (81 passed). The 46-file petition and popup-queue family green (2,466 passed).
- **Pins re-seated consciously:**
  - B1's retirement-receipt pin — the type is `petition_retired` now (`marshal_audience` behind the lever);
  - FA slice 6's crisis fixture — its card was stamped level 2 on a pair at level 0, S7's own case, so the fixture's quarrel is made real at that rung;
  - the PopupQueue round-trip pins — the dead path is gone;
  - the drama cap's exempt-tuple pin (`test_ca9_row3_a13_drama_cap.py`) — `petition_retired` joins, found by the hook.
  Zero `.gd`.

### 73.9 PC15-10 B3 — The crisis survives a new flow (W7; `PETITION_POPUP_REVISIT_SPEC.md` §4 F6; September 27, 2026)

Record `PETITION_POPUP_REVISIT_SPEC.md` §9 (the B3 row, authoritative); landing `SCORE_MANDATE_PLAN.md` §2 Chunk 4. Pins `tests/test_b3_the_crisis_survives_a_new_flow.py` 10; sweep `tools/_sweep_b3.json` 10/10 killed, 0 INERT; attribution `tools/_b3_series_arms.py` (+ `.json`). Levers `dialogue_manager.HYBRIDS_SURVIVE_A_NEW_FLOW`, `diplomatic_executor.THE_HYBRID_MODAL_RETURNS`.

- **A new flow keeps what the player owns.** `DialogueManager.open_flow` starts a player-initiated flow (a declaration's war-purpose chooser, a proposal, a treaty break — 9 player-only openers). It preempts — keeps in the queue — a displaced MAIL dialogue (REV-3, Aug 30) and now a displaced HYBRID too (`HYBRID_SOFT_STOP_TYPES`: `vassal_rebellion_imminent`, `sabotage_confrontation`), which do not block commands and so could be displaced by a typed order. A transient planning step is still overwritten, so re-issuing a verb never piles up stale steps. `replace()` is unchanged.
- **The consumed modal comes back.** A hybrid's modal is consumed when first delivered, so a crisis kept in the queue returned with no modal to answer. When the player's answer to the modal comes back stale (the W6-0 id binding: another dialogue is current), `diplomatic_executor._reissue_displaced_hybrid` re-issues the modal of the QUEUED hybrid it names — the rebellion's via `vassal.rebellion_popup_for_dialogue` into `vassal_rebellion_imminent_popups` (the list, so another vassal's modal is never overwritten), the sabotage's via `diplomatic_defiance.build_sabotage_popup` (ONE builder, now read by the dispatch producer too) — never duplicated. The FA-N5 delivery gate holds it until its dialogue is current again, and the refusal adds "… waits behind it and will return to you."
- **Measured.** Reproduced at the wire before the build (the crisis destroyed; Back Out brought nothing back). After: the crisis survives the declaration, the stale answer is refused and the modal re-issued, Back Out makes the crisis current, and the modal is delivered again exactly once. `BASELINE_SERIES` byte-identical on both arms, `open_flow` reached 0 times on the ambient board; M1–M7 + the AI-V assurance byte-identical. Zero `.gd` — FA-N5 (Sept 2) had already given both hybrid popups their `dialogue_id` and both client handlers send it.

### 73.10 PC15-10 B4a — The order, justified (`PETITION_POPUP_REVISIT_SPEC.md` §4 F8, §6 Q5 RULED; September 27, 2026)

Record `PETITION_POPUP_REVISIT_SPEC.md` §9 (the B4 row, B4a half, authoritative); landing `SCORE_MANDATE_PLAN.md` §2 Chunk 4. Pins `tests/test_b4a_the_order_justified.py` 12; sweep `tools/_sweep_b4a.json` 7/7 killed, 0 INERT.

- **Nine slots, each justified.** `PopupQueue.PRIORITY_ORDER` (one popup per response cycle, lower index first): sabotage discovery · vassal rebellion imminent · the Proclamation · Talleyrand's objection · the marshal petition (crisis tier) · the current-turn envoy · the persistent settlement offer · the proposal RECEIPT · the commitment paradox. Each row says why it outranks the next in the comment table above the list; a census pins the table to the list.
- **The dead slot is retired whole.** `coalition_popup` had no producer (the coalition's formation reaches the player on the notice rail — `form_coalition`'s payload rides its result). Its order entry, response key, world property and save key are gone; a legacy save's key is dropped at load. The `alliance_paradox_popup` order entry (unreachable) is gone too; its alias is kept, so a legacy save that pushes under the old name lands in the paradox slot.
- **The receipt stays a receipt.** `proposal_result` is informational — no modal since FA-S17-D9 — and the backend lifts it onto the notice rail and the peace-summary line, the only surface for a proposal answered while Talleyrand travels.
- **The end-turn carry is declared.** The one documented exception to "one popup per response": the END-TURN response (it carries `enemy_phase`) defers every CHOICE popup — the route table would swallow the report — and CARRIES `PopupQueue.ENEMY_PHASE_CARRIED` beside it (`proposal_result`, the Proclamation, the crisis petition as `deferred_marshal_petition`), each popped outside `pop_highest` by `main._apply_command_popup_contract`, which also attaches the current hard stop as `deferred_dialogue` and blanks `envoy_digest`. A census and a behaviour pin hold the declaration to the code.
- **Measured.** `BASELINE_SERIES` + M1–M7 + the AI-V assurance byte-identical; the 203-file popup and response family green (8,556 passed). Zero `.gd`.

### 73.11 PC15-10 B4b — The one tail (`PETITION_POPUP_REVISIT_SPEC.md` §4 F9; September 27, 2026)

Record `PETITION_POPUP_REVISIT_SPEC.md` §9 (the B4 row, B4b half, authoritative); landing `SCORE_MANDATE_PLAN.md` §2 Chunk 4. Pins `tests/test_b4b_the_one_tail.py` 68 (census + six DRIVEN scenarios through `tools/b4b_one_tail_harness.gd`, the real `main.tscn` behind an API stub, on payloads from the real endpoints); sweep `tools/_sweep_b4b.json` 17/17 killed, 0 INERT; the shared helper `tests/_gd_calls.py`.

- **Nine surfaces are deferred, not routed:** the battle tableau, the ending, the capture question (on an end-turn response), the Proclamation, the letter-book, the redemption, a deferred hard stop, the marshal petition, and the next queued marshal question. The backend has already popped them, or they ride a response whose route table would swallow the report.
- **One stash.** `main._stash_pending_surfaces(response)` calls every stasher; every response ingest (the command result, the objection / interrupt / charge answers, the world swap) calls it before any routing or early return. Only the ending's own two seams (the game-over handler, the boot connection test) also stash the ending directly.
- **One chain, one order.** `_raise_pending_surfaces()` raises the first stashed surface, in this order: tableau · ending · capture question · Proclamation · letter-book · redemption · deferred hard stop · petition · the next queued question. It raises nothing over an open modal and then answers false, so control is handed back as before — a modal the player opened while a request was in flight (the pause menu, the Cabinet) never calls the tail when it closes. A route raised by the response itself (a capture question on an order's result) comes before the chain.
- **One tail.** `_return_control_to_player()` raises through the chain and hands the command line back only when nothing is waiting. Every control-return seam ends in it, and none re-enables the command line itself; a surface that takes the flow returns control through the tail again when it closes.
- **The answers route what they carry.** The objection and charge answers route through `_post_answer_response_routes` — the post-HUD table minus the redemption route, which would render the result a second time (the redemption rides the stash). An overridden attack that takes a province asks about its town, with the command line closed beneath the question; no answer handler re-enables the line before it raises one (the capture answer's estate stage included).
- **The queue is kept.** An interrupt answer never clears the interrupt queue. With questions still queued the chain decides what comes next (what the answer stashed first, then the next question); with the queue drained, `_process_next_interrupt()` closes the flow (the dispatch, then the tail).
- **A world swap forgets the old campaign.** The reset calls `_clear_pending_surfaces()` (every stash); the swap then stashes the ARRIVING campaign's surfaces and raises them through the tail.
- **Measured.** The four defects reproduced driven on the committed client (the question dropped, the queue emptied, two modals stacked, the old relayed order in the new command line) and all six scenarios resolve on the fix; 0 `SCRIPT ERROR`. Backend untouched: `BASELINE_SERIES` + M1–M7 byte-identical by construction.

## 74. THE SCORE MANDATE — CHUNK 5 ECONOMY & NAVAL, "The Laws" (SR-5r; September 27, 2026)

Gate record `REFORMS_SPEC.md` §0 (RULED September 27, 2026: laws with upkeep); the readings of §0.1 CONFIRMED the same day, with R3 + R8 replaced by **"The Arrears"**. Build contract §12, landing records §12.1+. One module, `backend/game_logic/reforms.py`; one serialized world field, `reforms`.

### 74.1 SR-5r RF-0 — The substrate (`REFORMS_SPEC.md` §1, §4, §5, §10)

Pins `tests/test_rf0_the_laws_substrate.py` 35; sweep `tools/_sweep_rf0.json` 19/19 killed, 0 INERT.

- **One store.** `world.reforms = {court: [row]}` — each court's authored deck, copied from the scenario at `from_scenario` (the agendas-deck idiom), in deck order (the AI's order). The in-force state lives ON the row: `enacted_turn` while a law is in force, `lapsed_turn` after a lapse until it is restored (the R8 clock; a repeal never writes it). `from_dict` reads the scenario and the save alike, so the two share one shape. Serialized; a legacy or tutorial world authors none and has none (N1).
- **The closed set (§4).** `EFFECT_TYPES` = `actions` · `manpower_regen` · `recruit_price` · `recruit_morale` · `drill_morale` · `supply_capacity` · `satellite_loyalty` · `cs_closure` · `blockade_denial` · `cures`. `WIRED_EFFECT_TYPES` names the types sited on their seam in this build — `actions` alone at RF-0 and RF-1 — and the validator refuses a row whose effect is not wired: a law does what it says the day it ships ("strike, never invent"). Every effect is DERIVED at its seam from the laws in force (`effect_clauses`), so a lapse or a repeal removes it by construction.
- **One predicate, one price.** `law_refusal(world, nation, law_id, admin_actions=None)` gates the verb, the chip, the AI rung and the preview, and refuses free in §2's order: not this court's law · already in force · the price · no admin action left (the AI passes its own admin budget). `restoration_price(world, nation, row)` is the ONE price every surface quotes (R8): a law that LAPSED restores within `ARREARS_WINDOW_TURNS` (10) for `ceil(price / 2)` plus its upkeep for every turn it lay dead, counting the turn whose upkeep bounced — the Staff costs 4,800 a turn after the lapse, 6,000 after five, 7,500 after ten, the full 9,000 on the eleventh; an authority law restores for half its authority plus its arrears in gold; a REPEALED law always costs its full price. `law_upkeep_bill` is the "Laws" Net component; `staff_actions` is the Staff's derived +1.
- **The authored decks (§5).** `europe_1805.json` `reforms`: each great power's Staff, one price for all (9,000 gold, 300 a turn, `actions` +1) — France's Grand Quartier Général, Austria's Corps d'Armée, Prussia's General Staff, Russia's Divisional System, Britain's Horse Guards Reforms. Nothing is in force (§1, Q7). The rest of the catalogue is RF-2's.
- **The validator** (`modding/validator._validate_reforms`): the required fields; ints ≥ 0; the closed, wired set; at most two clauses; exactly one Staff per court, at one price and one upkeep; no `enacted_turn` or `lapsed_turn` in a scenario.
- **Old saves.** `save_manager._backfill_reforms` arms a pre-reform save of the 1805 campaign (its `scenario_name`) with the decks its scenario now authors, nothing in force. A tutorial or modded save gets no deck, and a save already carrying a store is never overwritten.
- **Measured.** Nothing is in force at boot, so no seam reads anything: `BASELINE_SERIES` + M1–M7 cannot move.

### 74.2 SR-5r RF-1 — The player's road (`REFORMS_SPEC.md` §2, §5, §8 "The words"; T4, T5)

Pins `tests/test_rf1_the_players_road.py` 73; sweep `tools/_sweep_rf1.json` 54/54 killed, 0 INERT (the first pass found two INERT — the Emperor's exemption and the route's own hedge guard, each a defence in depth the shipped road never reaches; both are now pinned on the road they guard). Lever `reforms.THE_STATE_HAS_LAWS` (down: the state has no laws — the verbs refuse, nothing bills, nothing lapses, the Staff mints nothing).

- **The verbs.** `enact_law` and `repeal_law` go through the shared executor as `ADMIN_ACTIONS` — one admin action each, charged after success — and the price is charged in the executor (`reforms_executor.ReformsExecutor`, the naval_executor idiom).
  - The executor refuses through the predicate, free and in the predicate's own words (shown = applied).
  - On success it calls the ONE mutation, `reforms.enact_law`: it charges exactly `restoration_price`'s quote (gold into `record_gold_spent`; authority off the player's tracker or the court's `nation_authority`), stamps `enacted_turn`, clears `lapsed_turn`, and logs `law_enacted` with `restored`, `gold`, `authority` and `upkeep`.
  - An authority spend names every threshold it crosses (70 · 60 · 30, §3).
  - `repeal_law` takes the law out of force, refunds nothing (R4), never writes `lapsed_turn`, and logs `law_repealed`.
  - The AI will ride the same two functions (RF-3), GR5.
- **The words.**
  - A law is named by its id, its authored name (accents, case and a leading "the" ignored: `enact the Grand Quartier General`), a word short or long when one law holds it, or — for the court's one `actions` law — "the Staff" (`reforms.resolve_law`). A name no law holds is refused free, with the court's deck listed.
  - The parse branch sits above every family that would read a law's NAME as its own order word. The recon measured three: "the Military Reorganisation Commission" is recruit_marshal's noun, "the Train des Équipages" drill's verb, and "the Horse Guards Reforms" hold's.
  - The Congress's guards read the same way: a line led by a marshal stands down, and a QUESTION or a hedge is answered with the court's laws and their prices (`first_contact` kind `laws`). Nothing is enacted.
  - A law order put TO a marshal (`Ney, enact the Staff`, with or without the comma) parses with its marshal, so the executor refuses it in words, free: "The laws are the Emperor's to enact, Sire — Marshal Ney commands a corps, not the state." The foreign minister, "Sire", "Napoleon" and "the Emperor" are decoration on an act of state — never CR-2's "Did you mean Ney?".
  - `re-enact` folds to `reenact`, so the CX-R1 harvest learns whole verbs: `routed_order_words` gains `enact`, `reenact` and `repeal`.
- **The "Laws" line (§2.2).** `calculate_turn_income` bills `law_upkeep_bill` as `laws`; `process_income_phase` subtracts it and carries it in the applied record; `ledger.NET_GOLD_COMPONENTS["laws"] = -1` and `_build_economy` subtract it. Both end-turn banners (`meta_executor` and the executor's auto-advance twin) print "| Laws: -Ng"; the dispatch carries it (its Net is `_build_economy`'s); the treasury report names each law in force; the question desk names "the laws" among its Net labels; `strategic_ledger.gd` renders the line; `tools/playtest_driver.py` reads it. There is no bankruptcy mercy: an unpaid law lapses instead.
- **The lapse (§2.3, R5).**
  - `reforms.process_law_lapses(world)` runs after the income phase and the instruments, immediately BEFORE ESP-4's rente default (inside `_process_dotation_state`) and the bankruptcy check: the state sheds its machinery before it breaks faith with its marshals.
  - While a court's chest is negative and it has laws in force, the first law in `lapse_order` lapses: the largest upkeep; on a tie, the most recently enacted; then the later in the deck.
  - Its upkeep BOUNCED: the charge is refunded into the chest and folded out of the applied record (`laws` down, `net` up — Net equals the measured change in the chest, ESP-4's shape).
  - `lapsed_turn` is stamped (the Arrears clock starts) and `law_lapsed` is logged. The player's own lapse is told in the end-turn report (`tactical_events`), naming the Arrears price and the window.
  - GR5: every court, one rule.
- **The Staff at the refill (§5, T5).** `calculate_max_actions` adds `staff_actions` for the player (4 + `bonus_actions` + the Staff — at most 6 with an administrative marshal); the AI restore adds the same derived term to `base_nation_actions`. It is never written into `bonus_actions`. The refill runs before the lapse, so a law enacted mid-turn is felt at the next refill, and a law that lapses is lost at the refill after (the lapse message says so).
- **The log.** `law_enacted`, `law_repealed` and `law_lapsed` join `CAMPAIGN_LOG_TYPES` (168 → 171; the fourteen count pins flipped consciously), category economy, always shown — a court's laws are court knowledge (diplomacy has no fog). One-liners: "France enacts the Grand Quartier Général (300g a turn)", "Austria restores …", "Prussia cannot pay for the General Staff (300g a turn) — the law lapses".
- **The corpus and the prompt.** 15 golden-corpus rows (orders, names, the minister, the Emperor, a marshal, questions, a hedge, negations) pass under both arms of CX-1's lever. The parse prompt gains the two verbs in its action list and two board-independent examples, and the recovery prompt's verb list gains "enacts" and "repeals". The 17 authored IQ-9 cassettes are re-stamped, and both attribution records are re-derived for the common change: `tests/data/l1_prompt_restamp.json` (the L-1 lever still isolates the reorder) and CRT-7's recovery constant.
- **Measured.** `BASELINE_SERIES` + M1–M7 + the AI-V assurance byte-identical — nothing is enacted on the ambient board (the AI's rung is RF-3's). Parse harness EXIT=0, boot 0 `SCRIPT ERROR`.
- **Owned elsewhere, not built here:** the forecast on three surfaces, the dispatch beats, the rivals' laws on the nation cards and the help block's verbs (RF-4b); the LAWS tab (RF-4a); the other eight effect types and the catalogue (RF-2); the AI rung (RF-3).

### 74.3 SR-5r RF-2 — The catalogue (`REFORMS_SPEC.md` §4, §6, §11 T1/T2/T8)

Pins `tests/test_rf2_the_catalogue.py` 60; sweep `tools/_sweep_rf2.json` 36/36 killed, 0 INERT (four INERT on the first pass, each a weak pin of mine — rewritten on behaviour).

- **One reader per type**, each returning the law beside its term (`reforms.effect_terms`): the seam applies it and every surface quotes the same figure (shown = applied), named where it applies (T8), the same rule for every court (GR5). `CLAUSE_SHAPES` closes each type's parameters in the validator.
- **Where each type applies:** `manpower_regen` — infantry only, last in `get_manpower_regen_rates`. `recruit_price` — the DRAFT's pricer, before the Intendance; the substitute market passes `draft=False` (the RV-17 rule). `recruit_morale` — the draft's base, before the training ground and Moore's floor. `drill_morale` — `WorldState.drill_morale_gain`. `supply_capacity` — the FED multiplier only. `satellite_loyalty` — one term for the tick and the forecast, every client. `cs_closure` — the Berlin Decree counts an autonomous client (`naval.decree_clients` names them). `blockade_denial` — inside `naval.blockade_trade_loss`, the blockader's law; `naval.blockade_trade_words` is the one phrase every surface prints.
- **The catalogue:** 25 laws in five decks, the Staff first in each (the AI's order); France's Train des Équipages waits for DC-2.
- **Measured:** T1 — a saving France buys the Staff on turn 5 on three seeds; the user kept 9,000 for all. T2 — 36.7% of the control arm's mean Net on five laws, 45.3% with the Train (DC-2). the full suite green in the worktree before the carry (27,537 passed) — `BASELINE_SERIES` + M1–M7 + the AI-V assurance byte-identical, because no AI court enacts a law until RF-3 and nothing is in force at boot (every seam reads 1.0 / +0 there). Parse harness EXIT=0, boot 0 `SCRIPT ERROR`.

### 74.4 SR-5r RF-3 — The AI enacts (`REFORMS_SPEC.md` §3, §7, §11 T3)

Pins `tests/test_rf3_the_ai_enacts.py` 21; sweep `tools/_sweep_rf3.json` 21/21 killed, 0 INERT (five INERT on the first pass, each a weak pin of mine: four masked by a test chest whose EB-1 charges drove the forecast Net negative, one staging a Staff `law_refusal` refused on price).

- **The rung** (`reforms.find_ai_enactment`, admin chain P1.78 — `ENEMY_AI_REFERENCE.md`). Every AI great power enacts from its own authored deck, in deck order, at the player's prices, through the SAME `enact_law` verb and executor (GR5). It takes the first law `law_refusal` passes with the court's OWN admin budget and whose purse test passes; at most one enactment every `AI_ENACTMENT_EVERY_TURNS` (3), paced off the laws in force (zero new fields); it never repeals. Lever `reforms.THE_AI_ENACTS`.
- **The purse test** (`reforms.ai_purse_refusal`): the chest ≥ the price (an authority price asks no gold) + any Arrears + `AI_PURSE_RESERVE` (1,000) + `AI_PURSE_UPKEEP_TURNS` (5) × the slate's upkeep including the new law; the forecast Net (`ledger._build_economy`) stays ≥ 0 after the new upkeep; an authority price never takes the court below `AI_AUTHORITY_FLOOR` (30), nor leaves it fewer than `AI_DIPLOMACY_FLOOR` (3) diplomatic points a turn, read through `diplomacy.calculate_dp` at the authority after the act. The last clause is §3's "the AI rung weighs it", added as a floor, not struck.
- **The executor** defaults an AI actor to the one admin action its loop holds (`reforms.ADMIN_ACTIONS_PER_ACT`), so an AI enactment never reads the player's pool.
- **Measured:** T3 MET — every rival great power enacts on the ambient board, four courts by turn 10, sixteen laws in forty turns, 0 lapses. `BASELINE_SERIES` re-recorded ONCE with a two-arm attribution (`tools/_rf3_series_arms.py`; arm 0 byte-identical, arm 1 diverges at [7]); M1–M7 byte-identical. On the COMMANDED arm France holds 28 / 27 / 25 provinces at turn 40 with the rung down, 25 / 5 / 25 when only the rivals enact, 25 / 28 / 27 when France enacts too (archives `rf3-*`). Nine standing pins re-seated with the cause measured (`tools/_rf3_wo_attribution.py` — every prior figure returns with the lever down in the child). The doctrines' T8 predictor measured (only Austria's Staff, turn 33) and the save-for-the-Staff rule handed to DC-2.

### 74.5 SR-5r RF-4a — The LAWS tab (`REFORMS_SPEC.md` §8, §8a)

Pins `tests/test_rf4a_the_laws_tab.py` 53; sweep `tools/_sweep_rf4a.json` 35/35 killed, 0 INERT.

- **One source for what the player sees** (`reforms.py`): `effect_line` (a clause in numbers), `terms_line` (what enacting or restoring costs now and a turn, the Staff's order, the authority priced aloud; never ends in a full stop), `authority_line` (the ONE line for the chip, the confirm and the verb's result), `laws_payload` (one row per law in deck order; ONE chip whose enabled state IS `law_refusal` / `repeal_refusal` and whose reason is that predicate's words). The ledger carries it as `laws`; a deckless world carries nothing. `naval.blockade_cut_percent` is the one source for the deeper blockade cut.
- **Authority's lines, as the engine reads them:** the marshals' calm holds only ABOVE 70 (`jealousy`: authority > `AUTHORITY_SUPPRESS_ABOVE`); the extra diplomatic point at 60 and above; a point lost below 30 (`diplomacy.calculate_dp`). Every line crossed is named as lost; when none is, the nearest line that holds is named.
- **The enactment confirm** — the executor's quote-then-confirm on the command_clarification channel (the Admiralty's idiom; no new modal type), for the chip AND the typed road (a chip sends the typed order). The quote is free and comes from "The Council of State"; `yes` enacts, `no` withdraws free; a typed `… confirmed` (or `… confirm`) is one step; the marker is read off the raw words and never reaches the law's name. An AI court (`_acting_nation`) is never quoted. A refusal is never quoted. A repeal is not confirmed; its chip states what is lost.
- **A clarification answer refreshes the screens beneath it** (`main.gd` `_on_clarification_command_result` → `_refresh_open_info_screens`, which now includes the strategic ledger) — the Council's confirm and the Admiralty's Diversion confirm alike.
- **The client:** `LawsTab`, `KEY_8` under the digit-belongs-to-the-caret guard, `_render_laws_tab()`, one `_chip_row` for every book. Eight tabs fit at Interface Scale 2.0 (IQ-10 frames 2026_09_27).

### 74.6 SR-5r RF-4b — The laws everywhere else (`REFORMS_SPEC.md` §8, §8a; T7, T8)

Pins `tests/test_rf4b_the_laws_everywhere.py` 47; sweep `tools/_sweep_rf4b.json` 38/38 killed, 0 INERT.

- **The forecast** (`reforms.lapse_forecast`) is the lapse rule (`lapse_order`) run against the ledger's projection of this turn's end (the chest + `ledger._build_economy`'s Net): None while the slate is paid; else the law that lapses first, the gold that saves the whole slate (`shortfall`), the laws that would go after it (`doomed`) and the lever. ONE source for the LAWS tab (`laws["forecast"]`), the end-turn banner (the message's `THE LAWS:` line and `turn_end.law_forecast`) and the morning dispatch (`situation.law_forecast`).
- **The lever** (`reforms.repeal_plan`): the fewest repeals of the OTHER laws in force whose saved upkeep covers the shortfall — the cheapest single law when one suffices, else the largest first. The chip (`repeal_instead`: label, typed command, note, plan) is enabled only when `repeal_refusal` passes AND the admin actions cover the whole plan; otherwise it is withheld with its reason and the line says why.
- **The beats** (`reforms.queue_law_beat`, called by the ONE mutation and the lapse loop): a rival court's enactment or restoration (`law_enacted_abroad`, MEDIUM, the effect in numbers) and lapse (`law_lapsed_abroad`, MEDIUM); the player's lapse (`law_lapsed_home`, HIGH). The player's enactment is the verb's own answer. **The Staff's first refill** is derived at the dispatch (`reforms.staff_arrival` — the Staff enacted last turn) and named in SITUATION.
- **The nation card** carries `laws` (`reforms.laws_line` — the laws in force and their cost a turn; None omits the row).
- **The desk:** `reforms.law_named_in(world, nation, text)` reads a law's authored name or id words (whole words; "staff" names the court's Staff). An unanswered question that names a law is answered with the laws answer (`first_contact._laws_answer`), which says what is in force first and puts the named law first. The live topic router has a "laws" topic (`counsel.surface_pointer("laws")` — the Laws tab, T then 8); the legacy table is unchanged.
- **Named (T8):** the Manpower rows' `regen_terms` / `price_terms`, the vassal row's `law_terms` (the forecast's own term) and the Continental System's `decree_line` (`naval._decree_line` over `decree_clients`).

### 74.7 SR-5r DP-1 — The bank (`REFORMS_SPEC.md` §9; T6)

Pins `tests/test_dp1_the_bank.py` 22; sweep `tools/_sweep_dp1.json` 10/10 killed, 0 INERT.

- **The refill** (`diplomacy.dp_refill(regen, unspent) -> (pool, carried)`): carry = max(0, min(unspent, regen)); pool = min(`DP_BANK_CAP` = 7, regen + carry). `_process_dp_regen` reads the unspent pool (the player's `diplomatic_points`, an AI court's `nation_dp`) before the refill — zero new serialized fields — for every court (GR5). Lever `DIPLOMATIC_POINTS_CARRY`.
- **Shown = applied:** the regen dispatch breakdown adds "+N carried from last turn"; the refill's split rides the transient `world._dp_refill` (never saved), and `displayed_dp_ceiling` is max(the base ceiling + the Seat, regen + carried, the player's pool) — so after a load the ceiling is never under the pool.
- **Measured:** a fuller AI pool unlocks nothing on the ambient board (`tools/_dp1_measure.py` — 21 spends on both arms; the series byte-identical).

### 74.8 SR-5r RF-4c — The School card and the visual pass (`REFORMS_SPEC.md` §8a, §11 T7/T8)

Pins `tests/test_rf4c_the_school_and_the_census.py` 15; sweep `tools/_sweep_rf4c.json` 26/26 killed, 0 INERT.

- **The School's card XVIII "The Laws of State"** (gate 12; `tutorial_state.STEPS` mirrors the overlay, 20 cards): `"open": "ledger:7"` emits `open_ledger(tab)`, which `main.gd` `_on_tutorial_open_ledger` answers with `top_bar.open_ledger_to_tab(tab)` under the modal guard; `"suggest": "enact the Staff"`; `"advance": "_pred_law_enacted"`, a latch (`_saw_law`) set by a `law_enacted` event in `_note_observations`. The lesson scenario (`tutorial_1805.json`) authors France's 1805 deck verbatim.
- **The LAWS tab leads with its FORECAST**, before the rows.
- **The Staff's loss, ONE phrase** (`reforms.STAFF_LOSS`; `reforms.staff_loss_sentence(row)` is its sentence form, "" for any other law): read by the Repeal chip's note (`laws_payload`), the repeal verb's answer (`reforms_executor`) and the lapse's line (`process_law_lapses`).
- **The action count** is the command terminal's header ("Actions: N/M", `main.gd` `_update_status` from `action_summary.max_actions`); the top bar carries none.
- **Visual proof:** `tools/iq10_capture_payloads.py` `cap_laws()` stages `ledger_laws_staff`, `ledger_laws_forecast` and `diplo_laws_rival`; `tools/iq10_run_captures.py` shoots them (with `ledger_boot_laws`) at Interface Scale 1.0 and 2.0.

### 74.9 The session exit of September 28, 2026 — its residue

**The exit and its record.**
- Memo `docs/audits/SR_SESSION_EXIT_2026_09_28.md`. It read thirteen commits
  (B2–B5, SR-5r RF-0 → RF-4c, DP-1 and the AI drill fix) on four played arms
  against `6ceadabe`: the three standing exit arms and Chunk 5's laws
  evidence arm, `tools/playtest_scripts/sr_exit_chunk5_laws.json`.
- Landing `SCORE_MANDATE_PLAN.md` §5; rows `BUG_FIXES.md` §Score Mandate
  Session Exit (September 28).
- Pins `tests/test_sr_exit_residue_2026_09_28.py` 41; sweep
  `tools/_sweep_sr_exit_residue_2026_09_28.json` 23/23 killed, 0 INERT; zero
  `.gd`.

**The fixes.**
- **The bare word asks for the laws (SRX-11).** "laws", "the laws" and "our
  laws of state" are the laws answer when they are the whole line, after an
  address and a word of filler (`llm_client._names_the_laws`). Lever
  `THE_BARE_WORD_ASKS_FOR_THE_LAWS`.
- **A named law says what it does (SRX-12).** A laws question that names a law
  appends the law's authored `says`, whether the law is in force or not
  (`first_contact._laws_answer`). Lever `THE_LAW_NAMED_SAYS_WHAT_IT_DOES`.
- **A refused law states its price once (SRX-13).** `law_refusal`'s price
  sentence ("X costs N; the treasury holds M.") loses the price the line has
  already said, leaving "the treasury holds M" or "the court holds A
  authority" (`first_contact._refusal_after_the_price`). Every other refusal
  stays whole. Lever `A_REFUSED_LAW_STATES_ITS_PRICE_ONCE`.
- **The desk counts the points (SRX-14).** A desk kind `points`
  (`question_desk.classify_points_question`) is read **before** the
  diplomat's address, because "diplomatic" contains "diplomat" (one of
  `DIPLOMAT_ADDRESS_NAMES`). The count had opened Talleyrand's assessment,
  and its first options became a proposal.
  - `answer_board_question` → `_answer_points` reads what the top bar and the
    command header print:
    - the pool and its ceiling (`diplomacy.displayed_dp_ceiling`);
    - the refill's split (DP-1's transient `world._dp_refill`) and the bank's
      rule;
    - the day's orders and administrative actions
      (`world.get_action_summary`).
  - The minister may be its addressee: `parser.py`'s addressee exemption
    admits the `points` kind beside `laws`.
  - Free. Lever `question_desk.THE_DESK_COUNTS_THE_POINTS`.
- **Names as printed (SRX-15, SRX-16).** The humaniser now runs at five
  producers:
  - the soil alarm's clause (`dispatch._home_captured_lever`, "Archduke
    Charles's corps of …");
  - the fortify refusal's long form (`tactical_executor.fortify_refusal`);
  - both forms of the drill refusal (`drill_refusal`);
  - the attack road's truce refusal
    (`CommandExecutor._make_diplomatic_error`);
  - the pursue road's truce refusal (`StrategicExecutor`).

  The truce refusals also print the court by its display name. **The pursue
  road reads the truce's own clock** (`ARMISTICE_DURATION − armistice_turns`,
  the attack road's since SR-3a (ii)); it had read the war-entry floor in
  `armistice_cooldowns`. Display only, so no levers.
- **An eliminated court binds no instrument (SRX-17).**
  `DiplomaticExecutor._instrument_preflight` — the one gate of `guarantee`,
  `sponsor` and `buy off` — asks the invest verb's own predicate and sentence
  (`VassalExecutor._eliminated_court_refusal(world, target, tail=…)`, one
  source, each verb with its own tail): "The Kingdom of Italy no longer exists
  as a court — it was eliminated. No instrument can bind it." Nothing is
  charged. The guarantee's success line names both courts as printed. The AI
  never takes this road; only the parser emits the three actions.

**Pins re-seated.** Two, consciously:
- RF-1's `test_the_answer_puts_a_refusal_in_its_place` had pinned the double
  price.
- The corpus row for the points question is stated positively, because a
  `not_action: diplomatic*` row means a negated diplomatic order to the
  Cabinet-door census.

## 75. THE AI DRILL FIX — "we don't want them drilling when they can get attacked" (user-directed, September 27, 2026)

Rows `BUG_FIXES.md` §The AI Drill Fix (AIDR-1..5); pins `tests/test_ai_drill_fix_2026_09_27.py` 26; sweep `tools/_sweep_drill_fix.json` 21/21 killed, 0 INERT; the question `DESIGN_REFINEMENT.md` AIDR-D1.

### 75.1 The drilling penalty is read (GR4)
A corps caught drilling fights at −25% defence (`Marshal.get_defense_modifier`). `combat.resolve_battle` now cancels the drill (`combat._cancel_drill`) AFTER the defence modifier has read it; it used to cancel first, so the penalty the report printed ("(-25% defense)") and the battle report snapshotted ("Caught drilling") was never applied. Both sides. Lever `combat.DRILL_PENALTY_READ_BEFORE_THE_CLEAR`.

### 75.2 The one reach predicate
`enemy_ai.drill_reach_threat(world, marshal)` — the first corps AT WAR with the marshal's court that could reach and strike him before a drill ends, or None. Reach per hostile corps = (the drill's exposed enemy phases + 1) × its range (`movement_range`): a drill ordered on turn N stands through the enemy phases of N and N+1 (`DRILL_EXPOSED_PHASES` = 2; Soult's Drillmaster, 1), and in a phase a corps marches its range and strikes from its range — 3 regions for infantry, 6 for cavalry. Omniscient, like `_evaluate_capture_safety`. A court at peace and a prisoner (`captured_by`) are not threats. Distances are the cached `WorldState.get_distance`.

### 75.3 P4.9 "drill to heal"
`EnemyAI._consider_heal_drill`, sited after P4.8 and above P5 (a fortified corps cannot drill). A corps drills to restore its morale when: morale < `HEAL_MORALE_BELOW` (70); strength ≥ `STUB_STRENGTH_FLOOR`; not broken or recovering (`_corps_takes_no_ground`); the executor would take the order (`tactical_executor.drill_refusal`, `stance_gate=False`); `drill_reach_threat` is None; and no lower rung's more pressing duty applies — P6.5's supply move (`_supply_pressure_move`, the one P6.5 decision, extracted byte-identically), the AI-3c frontier (`war_council.get_intent_frontier`), P7.4's reinforcement (`_find_defensive_reinforcement_position`). It ignores P6's shock-bonus gate. Every personality but the literal (`LITERALS_DRILL_TO_HEAL`, held by the MC-V-2 ruling — AIDR-D1 DECIDED September 28, 2026: held out, the literal's rot in place is his character). Lever `AI_DRILLS_TO_HEAL`.

### 75.4 P6, the day's work, the default
- P6's shock drill also asks `drill_reach_threat` (`AI_DRILL_READS_THE_REACH`).
- A corps whose drill order succeeded is marked done for the phase (`DRILL_IS_THE_DAYS_WORK`).
- P8's default leaves a drilling corps be in every personality's branch (`EVERY_DEFAULT_LEAVES_THE_DRILL`; R1-5 covered the cautious branch alone).

### 75.5 Measured
- The ambient board (`tools/_drill_fix_series_arms.py`, seven arms): the old AI ordered 9 drills, 7 within reach of a corps at war; the shipped AI orders 1 (a heal), none within reach. `BASELINE_SERIES` re-recorded once — the shipped series equals the reach gate's own arm (the day's work and P8's guard move it only alone).
- The commanded board (`tools/_ai_drill_diag.py`): every non-literal debased corps that reached P4.9, not already drilling, healed; the reach gate refused none; the remaining debased turns are literals (MC-V-2) and corps recovering or engaged.

## 76. THE SCORE MANDATE — CHUNK 5, "The chest" (SR-5a; September 28, 2026)

Opened by the user's economy balance direction (September 27: Britain should be richer than France). Landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 5; rows `BUG_FIXES.md` §SR-5a The Chest; pins `tests/test_sr5a_the_chest.py` and the re-seated families named there; sweep `tools/_sweep_sr5a.json`; attribution `tools/_sr5a_series_arms.py`, `tools/_sr5a_wo_attribution.py`.

### 76.1 The ruled balance — Britain up, France trimmed (scenario data)
The 1805 campaign authors each province's `income_value` in `region_overrides` where the ruling moved it (`europe_1805.json`, `_economy_balance_comment`): every French homeland province yields three-quarters of the registry figure, rounded to ten (3,400 → 2,590 gold); London 500, East Anglia 300, Midlands 300, Northumbria 150, Scotland 150 (England 1,500 → 2,050). Britain's navies row carries `trade_dominance` 450 and `overseas_income` 1,000. Boot Net: Britain 2,851, France 1,032. France's homeland no longer pays for its whole boot army (−40 by the province-against-upkeep measure); its satellites' tribute and its trade carry it — France pays for its war by conquest and its clients. The registry, the tutorial and the legacy world keep their figures. A save written after EB-2 keeps its own authored overseas figure (`naval.OVERSEAS_INCOME_BACKFILL` fills only a missing key) and its own province incomes.

### 76.2 An administrative order asks only the administrative pool (AAR-6)
`recruit` is an objection action, so a marshal-addressed levy walks into the objection branch of `CommandExecutor.execute`, whose AP pre-check had read the military pool. That pre-check now skips an admin action (`is_admin_action`), which the head of `execute` already gates on `admin_actions_remaining`. A field order is still refused at zero military actions. Lever `executor.AN_ADMIN_ORDER_ASKS_ONLY_THE_ADMIN_POOL`.

### 76.3 The substitutes' named ground
`buy substitutes in <province>` means the strongest infantry marshal of ours standing there (the delivery is at his location); none there is refused in a sentence that keeps the name. An unknown name returns the fuzzy matcher's own refusal, never its dict inside `message`. Lever `economy_executor.THE_NAMED_GROUND_RECEIVES_THE_SUBSTITUTES`.

### 76.4 The ledger says why the bills moved (question (c), RULED "keep the rules, make it legible")
`ledger.why_the_bills_moved(world, nation, upkeep_data, state_charges, terms)` compares the ledger's projection with the turn the income phase last charged (`world._income_phase_results`, the transient applied cache):
- `upkeep_note` — "paid for the N men under arms — the fallen draw no pay", plus how the bill moved and by how many men.
- `state_charges_delta_note` — the move in the draw, split by the formula: the draw today's chest would pay at last turn's rate is the chest's part ("the chest is fuller" / "leaner"); the rest is the rate's, named by the terms that rose ("the long war wears on (+8)") or "the realm is calmer".
- The rate note ends "so a fuller chest pays more".
After a load the cache is empty and only the standing rule is said. Display only (GR6). Lever `ledger.THE_BILLS_SAY_WHY_THEY_MOVED`. The rules themselves are unchanged: upkeep is billed on fielded strength (the July 14 reversal of EC-U1) and the Charges of Empire are a share of the chest (EB-1).

### 76.5 A forecast prices tomorrow's war (IQ1-5-1)
`coalition.next_war_exhaustion(world, nation)` is the per-turn tick's single source (+8 at war capped at `WAR_EXHAUSTION_MAX`, −5 at peace floored at 0; the player's row on Europe only; an AI row at war with anyone on Europe, with the player on the legacy world) — `process_coalition_turn` writes it and every forecast reads it. The tick runs before the income phase inside the advance, so `get_state_charges_rate(nation, projected=True)` and `calculate_turn_income(nation, projected=True)` price the war-exhaustion term at tomorrow's value; `_build_economy`'s projection passes it, so the economy tab, the laws' lapse forecast and the AI's purse test quote the charge the advance levies (1,337 = 1,337 at a 40,000 chest; the stale quote read 1,216). The levy never passes the flag. Lever `world_state.THE_FORECAST_PRICES_TOMORROWS_WAR`.

### 76.6 The Vassals card reads tomorrow's standing
The producer asks for a client petition after the turn's loyalty tick, so the card's projected gate (a) reads the loyalty the client will have then — today's plus `forecast_vassal_loyalty`'s steady-state delta (the battle term is unknowable; a stated limit). The producer's own read is unchanged. Lever `vassal.THE_CARD_READS_TOMORROWS_STANDING`.

### 76.7 Struck and refuted
ES-4 development and ES-7b `confer_title` are struck by the user's ruling (`ECONOMY_REVISIT_SPEC.md` Track 3, each with a re-open condition). PTJ-D1 is refuted: `CombatExecutor._get_casualty_participants` admits only the lead's own nation, so a coordinated battle's pool never carries another court's dead (pinned as a precondition). IGR-X9 was decided on August 7 (EB-3.2: a ruin bills nothing) and is re-verified.

## 77. THE SCORE MANDATE — CHUNK 5, "The second road at sea" (SR-5b; September 28, 2026)

Landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 5 SR-5b; pins `tests/test_sr5b_the_second_road_at_sea.py`; evidence memo `docs/audits/SR5B_SHUT_OUT_ARM_2026_09_28.md`.

### 77.1 The expedition names its levers (AAR-D7)
`naval.expedition_odds_levers(world, nation, target, troops)` answers "what would make this landing a better throw". Each lever is `expedition_slip_odds` — the resolver's own odds — re-asked with ONE thing changed, through two overrides every live caller leaves at their defaults (`window=None` reads the record, `escort_extra=0.0` adds nothing): a won diversion first (`window=True`: the watch halved, +25), a 5,000-man corps (`EXPEDITION_LEVER_CORPS` = the Marshalate's `RECRUIT_MARSHAL_CORPS`, drift-pinned), the fleet at the readiness it climbs toward (`readiness_ceiling`, lifted out of `_readiness_tick` so the lever and the tick share one rule; never offered under blockade, where crews only rot), ten more sail (`EXPEDITION_LEVER_SAIL × NEW_SHIP_READINESS / 100` effective — exactly `lay_down_ship`'s green fold; only with a yard), and an ally's squadron (the H6 pooling rule's own terms: a court at war with the watcher, at peace with us, not yet pooled; `POOL_ALLIED ×` its effective strength). A lever is named only while it is a road this court can take (the diversion only while `diversion_terms_for` — ONE source now shared with THE ADMIRALTY — is all met) and only when it moves the odds by `EXPEDITION_LEVER_MIN_GAIN` (2) or more; each is quoted alone from today's board, never stacked; the three that move the odds most, most first. `levers_line` is the one sentence ("What moves the odds: a won diversion first (45 in 100) → 91 · a 5,000-man corps → 75") on the expedition confirm, the region panel's landing chip (a dim line under it) and THE ADMIRALTY's land chips. The landing-options payload memoises the line per (corps size, watcher, mode) — a watcher's coverage is its pooled strength, the same against every shore it watches — measured 15.8 → 3.4 ms with two corps at a yard, exact by a drift pin over every row. Lever `naval.THE_EXPEDITION_NAMES_ITS_LEVERS`.

### 77.2 The naval yard (NV-D9, RULED by the user "Build them in SR-5b")
`BUILDING_TYPES["naval_yard"]` = 1,200 gold, 4 turns, capital/major city/city; one administrative action (the `build` verb). The SITE gate is `naval.naval_yard_site_refusal`, read by `region.can_build` (so the executor, the counsel, the desk and the region panel agree by construction), in order: the lever; a naval layer; a court with an admiralty (a navies row — NV-0's ruling stands: no row, no establishment); an anchorage (the registry `port_anchor`, `naval.mooring_provinces` — the validator's own NUI-2 mooring test); not a dockyard already; at most `NAVAL_YARD_MAX_PER_NATION` (2) raised or rising in provinces the court holds (`raised_yards`, read off its own provinces — GR8). Then the works' own gates (a slot, stability, a work already rising, gold). A town is no site (0 slots) and the panel shows no yard chip there. On completion `process_construction_timers` calls `register_built_yard`: the province joins its builder's fleet record `built_dockyards` (rides the save verbatim; a province is one court's yard — a rebuild leaves the earlier builder's list). `all_dockyard_provinces` / `nation_dockyards` count a raised yard only while its work stands undamaged, so the ordinary works' rules apply: a plunder razes it (and frees the cap), a secure damages it, `repair` restores it, and control decides who builds there (conquest grants the yard, §3.4a). A yard is a SITE — keels may be laid down there and an expedition may embark from it — and NEVER a rate (`build_rate` stays national, §13.3) and never a port (`continental_ports_total` and `closure_against` read the authored `ports` only). The blockade glyph marks a raised yard of a blockaded court. Every "we hold no yard" surface names the build half of the road (`yard_road_clause`: the best lawful site and its price, or why not yet) — the keel refusal, the expedition refusal, THE ADMIRALTY's expedition term, the region panel's withheld landing reason — and THE ADMIRALTY's road chips offer "Raise a naval yard at X" first. The desk prices it ("how much is a naval yard"). The AI raises one at P1.81 (`find_ai_naval_yard`, GR5 — the same verb, price and gate): a court with a navy (a fleet record with crews) and no yard it controls, at war, with a chest above the price plus the keel rung's reserve, never a second while one rises. Lever `naval.NAVAL_YARDS_CAN_BE_BUILT`.

### 77.3 A refused order keeps the standing order (SR5B-1, found playing the shut-out arm)
The strategic override (Phase 5.2-C) cancels a marshal's standing order the moment an attack/move/defend/fortify/drill/retreat order names him — before the order runs — so a REFUSED order destroyed the march it never replaced (measured: Soult marching on Lisbon, `Soult, attack Lisbon` refused "cannot reach", the march gone with no word and the corps standing at Bearn for the rest of the campaign). The override now puts the order aside (`CommandExecutor._orders_set_aside`) and `execute` restores it — with its HOLD state and the question it had raised — when the order is refused (`strategic.attack_was_refused`: `success is False` and no battle of any shape). An order carried out still replaces the standing order. Lever `executor.A_REFUSED_ORDER_KEEPS_THE_STANDING_ORDER`.

### 77.4 Struck
NV-D3 privateers / a commerce-raid posture — struck by the user's ruling ("we can strike privateer"), `NAVAL_SPEC.md` §10.

## 78. THE SCORE MANDATE — CHUNK 5, "The Descent's second throw" (SR-5c; September 28, 2026)

Landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 5 SR-5c; pins `tests/test_sr5c_the_descents_second_throw.py`; sweep `tools/_sweep_sr5c.json`.

### 78.1 The Grand Diversion is thrown again (RULED by the user: "Readiness sets the odds, repeatable")
The fleet may sail the feint again `DIVERSION_WAIT_TURNS` (4) turns after its last throw, won or lost. The odds are `naval.diversion_odds` — the fleet's readiness less `DIVERSION_READINESS_OFFSET` (25), clamped to 5–95: 45 at the boot readiness 70 (the old flat odds, so a campaign's first throw is the throw it always was), 50 at the drill ceiling 75, 25 at the blockade floor 50. The odds are read before the throw changes anything (a failure docks readiness afterwards). So a failed throw leaves a fleet whose readiness must be rebuilt before the next throw is worth sailing — and a blockade, whose crews rot toward 50, forbids the rebuild: the second throw exists, and it is earned. State: the fleet record's `diversion_last_turn` (−1 = none this naval war) replaces the once-per-war `diversion_used`; the wait resets when the naval war ends (FA-N83's reading of "this war"); a save from before SR-5c migrates on load (`migrate_diversion_records`: a spent card becomes a throw on the load turn, the one fixed point the save offers). ONE source for the roll, the confirm ("37 times in 100 at her readiness (62) … she may try it again 4 turns from now"), THE ADMIRALTY's chip ("45 in 100 at readiness 70 — and again 4 turns after, whatever the outcome") and its third gate term (the wait, said), the Admiralty payload (`diversion_wait`, `diversion_odds`; `diversion_used` kept, meaning "may not sail the feint this turn"), the expedition's diversion lever (§77.1), the help, and the AI rung P1.9, which waits the same four turns (GR5). Lever `naval.THE_DIVERSION_IS_THROWN_AGAIN` (down = once per war at 45).

## 79. THE SCORE MANDATE — CHUNK 5 reserve (September 28, 2026)

Pins `tests/test_sr5_quick_wins.py`; sweep `tools/_sweep_sr5_reserve.json`.

### 79.1 An override names the order it set aside (SR5B-2)
An order carried out over a standing order closes its answer with one clause naming the order it ended — "Ney's hold at Rhineland is set aside." (march to / hold at / pursuit of / support of; `executor.set_aside_clause`). Never on a refusal (§77.3 restored that order, and a refused order is not "carried out" even under SR5B-1's lever down), never for an order still standing, and for the player's marshals only (`CommandExecutor._announce_set_aside`). Lever `executor.AN_OVERRIDE_NAMES_THE_ORDER_IT_SETS_ASIDE`.

### 79.2 A fleet action can lead the morning dispatch (FA-66)
Three headline classes read the naval layer's own fleet-action event (`trafalgar` / `fleet_action`, `naval._log_fleet_action`): `fleet_shattered` (94 — our fleet decisively beaten; between a broken corps and a destroyed marshal), `fleet_beaten` (83 — beaten, not broken; below a lost satellite), `fleet_triumph` (89 — our decisive victory, on the CA8-D6 triumph ladder under a broken corps of our own). The sentence is `naval.losses_sentence` — the loser's OWN sail with the allies beside (FA-59), never the pooled side; an indecisive win is no triumph, and a fleet action between two other courts is neither our wound nor our triumph (gate CA8-D6). Each class has its template and Berthier note; the line names the opponent (§79.3, SRX-19). Lever `dispatch.FLEET_ACTIONS_LEAD_THE_DISPATCH`.

### 79.3 The session exit's residue (the second exit of September 28, 2026)
Memo `docs/audits/SR_SESSION_EXIT_2026_09_28b.md`; rows `BUG_FIXES.md` §Score Mandate Session Exit (September 28, second), SRX-18 … SRX-23; pins `tests/test_sr_exit_residue_2026_09_28b.py`.
- **SRX-18 — the desk names a naval yard only where one could stand.** "what can I build" skips the naval yard wherever `naval.naval_yard_terms` is None (no anchorage, no admiralty, not a city). Before, it added "Not naval yard — Rhineland has no anchorage" to every inland answer. A refusal's reason drops its own closing period, so the answer ends on one, and when nothing can be built the refusal's sentence opens in capitals ("Sire. Supply depot — …").
- **SRX-19 — the fleet headline names the opponent.** The naval layer has no sea zones, so every battle name is "the France–Britain action", and "shattered at the France–Britain action" read as a place. §79.2's lines now read "The fleet is shattered in action with Britain — …" and "The fleet wins its action with Britain — …" (`formed_display_name` plus the definite article: "with the Ottoman Empire").
- **SRX-20 — the adjective before "fleet" and "patrols".** The strait-open beat ("draws the British fleet off station") and the landing line ("slips past the British patrols") take `display_names.nation_adjective`, as the interception line already did.
- **SRX-21 — an eliminated court by its name.** The rail notification (`WorldState._eliminate_nation`, through `formed_display_name`), the campaign-log line, the dispatch template (`{nation_display}`, PR-2's derived suffix, after "Sire — " as its siblings read) and the diplomatic preview's refusal (`GET /diplomatic_preview`) name the court, with the article where English wants it, capitalized at a sentence's head ("The Kingdom of Italy has been eliminated from the war."; "Prussia has been …"). Before, all four printed the tag ("KingdomOfItaly has been eliminated from the war."). The client's name net (`Utils.humanize_nation_keys_in_text`) translated it on the rail, in the log and in the dispatch view, but the diplomacy wizard prints a preview refusal as given.
- **SRX-22 — the proposing court by its name in the log.** `campaign_log._possessive_court` writes "Saxony's", "the Ottoman Empire's", "the Papal States'" (a plural name takes the bare apostrophe) on the accepted and rejected AI-proposal lines. Before: "We rejected PapalStates's open borders agreement proposal", which the client's net made "Papal States's" (a single-word tag such as Ottoman is not rewritten in prose). The formatter's nine non-possessive raw-`source` lines stay with NPC-12's display-name census (its next slice: SR-6b, Chunk 6's copy pass).
- **SRX-23 — an attack held for a declaration keeps the standing order.** SR5B-1's restore (§77.3) and SR5B-2's announcement (§79.1) now read ONE predicate, `executor.order_was_not_carried_out`: the order was refused (`strategic.attack_was_refused`), or it is held for a declaration the player must settle first (`awaiting_diplomatic_response` with no battle of any shape). Measured before: "Lannes, attack Tyrol" at peace with Austria answered "Choose your war purpose against Austria. Issue the attack again after the declaration is settled. Lannes's march to Bohemia is set aside." The attack never ran and the march was gone — for nothing, if the declaration was then cancelled. Lever `executor.AN_ATTACK_HELD_FOR_A_DECLARATION_KEEPS_THE_ORDER`.

## 80. THE TWO RULINGS OF SEPTEMBER 28, 2026 — SR5B-D1 and SRX-D1 (taken under the user's delegation: "make these decisions")

Rows `DESIGN_REFINEMENT.md` SR5B-D1 + SRX-D1; pins `tests/test_sr5b_d1_the_continent_kept_open.py`; sweep `tools/_sweep_sr5b_d1.json`.

### 80.1 The Continent kept open (SR5B-D1, RULED: keep the rule, name the corps)
The SHUT OUT reading (`congress._shut_out_reading`, GE-3 §2.4) is **unchanged**: the trade-dominance court is shut out of the Congress of Paris when the Continental System closes ≥ `cs_shutout_pct` (50% = 13 of 26) of the Continent's ports AND no corps of hers stands on the Continent (`corps_on_the_continent` — the summoner's mainland). SR-5b played the arc for 240 turns and the reading never held: every time the ports were shut, a British corps stood in Iberia (Wellesley, Moore, Paget, Shrapnel) — the Peninsular War, Britain's historical answer to the System, is what the rule already models, so the rule stays. What changes is the words. ONE source, `congress.continent_holders(world, court, viewer=None)`, names the corps that keep her on the Continent and where they stand, and three surfaces read it:
- **The Congress price** (`_ports_lever`, now passed the world): "shut 13 of 26 ports (now 10) and drive Wellesley from Lisbon"; with the ports already shut the corps is the whole lever — "drive Wellesley from Lisbon — 13 of 26 ports are already shut against her". Two corps in one province share a clause ("drive Wellesley and Paget from Lisbon").
- **The lapse beat** (`_shut_out_lapse_reason`): "Britain is no longer shut out — Wellesley at Lisbon keeps the Continent open to her" (`continent_kept_open_clause`).
- **THE ADMIRALTY's System line** (`congress.admiralty_shut_out_line` → `build_admiralty_report()["continental_system"]["shut_out_line"]`, rendered by `strategic_ledger.gd` under the notch line): what the System's endgame use takes and who holds the Continent open today — "Britain would be shut out of the Congress of Paris at 13 of 26 ports (10 now) with no British corps on the Continent — today Wellesley at Lisbon keeps the Continent open to her."; with the ports shut, "13 of 26 ports are closed to Britain, but Wellesley at Lisbon keeps the Continent open to her: drive it off and she is shut out of the Congress of Paris."; when the reading holds, "Britain is shut out of the Congress of Paris — …"; when the sitting's shut-out is spent, "Britain can no longer be shut out at this sitting — …". Only where the Congress is armed (the tutorial and a board without its `campaign_end` block carry no line) and never when the court is the player's or gone.

**Fog-honest (R5):** the reading's TRUTH is omniscient — it decides a stance, fogged or not — and its WORDS are not. A corps on a province the player sees at PARTIAL or better is named with its province; one out of sight is counted and never placed ("a British corps our scouts have not found"). The AI has no fog (`viewer` not the player → every corps named). Display only (GR6): no stance, price value, decision or AI read moves. Lever `congress.NAME_THE_CONTINENTS_HOLDERS` (down = the pre-ruling words, including the old lapse clause that placed every corps).

### 80.2 The long peace (SRX-D1, RULED: keep — no change)
SR-5a's ruled balance ("Britain up, France trimmed") makes Britain richer than France at the boot, where France pays for its war (boot Net 2,851 vs 1,032). Across a long French peace the two incomes are level (the second exit of September 28 measured France +2,545 / +2,028 against Britain +2,413 at turn 41). **Kept:** the EC-P3 gate ruled that "a golden peace may grow rich", and a France that ends its wars and rules thirty provinces earning what the island earns is the peace it bought. No lever is built; the recorded smallest lever (data, not code — Britain's overseas pool growing while at peace with the hegemon) stays unbuilt. Re-open condition: a played campaign in which a France at peace out-earns Britain by more than a third for ten turns running.

## 81. THE SCORE FINISH — STEP 1, "The peace holds" (RS-1 · RS-2 · RS-D1 · RS-10 · RS-16 · SF-V1 · SF-V5; September 29, 2026)

Landing record `SCORE_FINISH_SPEC.md` §3 Step 1; gate record for RS-D1 `SCORE_FINISH_SPEC.md` §6.1; rows `BUG_FIXES.md` §Full Play Retest (RS-1, RS-2, RS-10, RS-16) and §Score Finish Verification (SF-V1, SF-V5); design row `DESIGN_REFINEMENT.md` RS-D1; pins `tests/test_step1_the_peace_holds.py` + `tests/test_rs_d1_recognition_by_defeat.py`; sweep `tools/_sweep_step1.json`; attribution `tools/_step1_series_arms.py` → `tools/_step1_series_arms.json`. Every rule below sits behind its own lever; every lever DOWN reproduces the pre-Step-1 behaviour byte-for-byte.

### 81.1 The offensive cascade keeps a fresh peace (RS-1; lever `diplomacy.THE_CASCADE_KEEPS_A_FRESH_PEACE`)
ONE predicate, `diplomacy.offensive_call_bar(world, callee, target)`, says why an ally cannot be called into an OFFENSIVE war against `target` by a declaration — '' when nothing bars it — read in three places so they never disagree: the offensive loop of `_process_war_cascade` (BEFORE either road — the resolver or an explicit ally-entry decision; the court takes `path="hard_illegal"` with the reason, no penalty and no refusal episode, because it was never free to be called), `preview_war_declaration` (a new `offensive_barred: [{nation, reason}]` beside `offensive_joiners`, so the review never promises an ally the cascade then refuses), and — as its third reading — the Congress. The three readings, in order: **the fresh-peace floor** (PR-1's own `coalition.peace_with_target_is_fresh`, "fresh peace with X"); **the pair cooldown** (`armistice_cooldowns`, "a truce's cooldown binds it to X (N more turns)" — the store `declare_war` R99, the war council and the exhausted-pair exit already honour); **a court that answers the sitting Congress** (`congress.spared_from_coalition`: recognizing, shut out, or in a truce with the Emperor — RS-D1's rider, "it recognizes the Congress — the Congress of Paris sits"). The DEFENSIVE arm is untouched by design: there the aggressor reopens its own war and the defender's ally answers an attack, not a summons (pinned: France attacking a court whose allies just signed with France brings them in). `_resolve_offensive_call_path` keeps no copy of the bar — one seam.

**The settlement writes the pair cooldown** (lever `settlement_ratify.THE_SETTLEMENT_WRITES_THE_PAIR_COOLDOWN`). `settlement_ratify.write_settlement_peace_floors(world, resolved_pairs)` runs at the end of `_resolve_pair_state_transitions` — the ONE transition helper the player's table and the headless AI-vs-AI road (`settlement_third_party.attempt_third_party_settlement`) both call, so both inherit it (GR5): every pair the plan moved out of WAR or ARMISTICE into PEACE, the clients that followed their lord included, gets `max(existing, FRESH_PEACE_FLOOR_TURNS)` (5 — PR-1's own value; the truce's popped cooldown is replaced by the peace floor, `test_common_peace_c2_ratification::test_confirm_armistice_pair_resolves_to_peace_and_clears_armistice` re-seated consciously). Measured before the fix: the table set PEACE and stamped `resolved_turn` only, so a peace France ratified carried no truce floor at all. The KNOWN GAP at `settlement_third_party.PAIR_EXIT_TRUCE_FLOOR_TURNS` (PC15-15's residual, "a floored pair can be re-welded by a third court's fresh war") is CLOSED by the same predicate.

### 81.2 A war while the Congress sits contests, not breaks, the ceder's titles (RS-2; lever `game_end.A_CONGRESS_WAR_CONTESTS_NOT_BREAKS`)
While the Congress of Paris sits, a WAR entry the Emperor **neither declared nor joined** does not break the treaty titles the ceder gave him — it CONTESTS them: the record keeps `kind: "treaty"` and gains `contested: {by: <ceder>, turn}`, the count is unchanged, the hold's titled term names it ("Austria's war contests what it ceded (Bohemia, Carniola, Moravia …) — counted while the Congress sits", `congress._contested_by_war` ← `game_end.contested_titles`), a `congress/contested` event is logged (chronicle: `campaign_log._format_congress_event`; dispatch: headline class `congress_contested` at weight 87, one below the cannon) — player-house titles only (the Congress is France's). Who drew the sword is read off the ONE diplomatic-state setter's own argument order per reason (`game_end.player_drew_the_sword`: `war_declaration` and `offensive_cascade` → (aggressor/joiner, target) → the player drew it iff `nation_a` is the player; `defensive_cascade` → (joiner, root aggressor) → iff `nation_b` is the player; any other reason — a repudiation, a cheat — is read as the Emperor's so the shelter never widens by accident). **The contest ends with the war**, at the setter: a pair leaving WAR-or-ARMISTICE for anything else resolves it (`game_end.resolve_contested_titles`) — a SIGNED road (`SIGNED_PEACE_REASONS`, the retention pass's own vocabulary) drops the mark and the retention pass re-signs the titles at the same setter while `congress.note_ratification` latches the court (`table` while sitting); an UNSIGNED end (a truce that ran out into peace — `armistice_expired_peace` — an elimination, a repudiation) applies the deferred break then (`_reopen_record`: conquest kind, quiet clock from now, `reopened_by` the ceder). A truce is NOT the war's end: WAR → ARMISTICE keeps the mark, and the per-turn lapse (`game_end.lapse_contested_titles`, at the head of `reconcile_province_titles`) reads a truce as the war still on; the shelter lasts only while the Congress sits — once it has dissolved or concluded with the war still on, the lapse applies the break; a contest whose war ended by a road the setter did not carry (a load, a fixture) is over and the title stands. The reconciliation's backup break skips a contested record. A province actually LOST still breaks the hold (`congress.note_capture`, unchanged) — and a count that fell short names what TOOK it ("45 titled provinces (43 of 45) — Moravia, Carniola, Bohemia and Vienna taken by force", then a ceder's war that reopened its cessions); the contest clause is named only while the count stands (SF-END-1's finding: the first reading of the played dissolution had named the contest as the cause of a loss). The cooldown line carries the cause for the whole cooldown (`state_line`: "THE CONGRESS OF PARIS — dissolved on turn 28 — the titled provinces fell short (43 of 45) — Moravia, Carniola, Bohemia and Vienna taken by force; it may be summoned again on turn 38 (9 turns remain) · 43 of 45 titled"). The Emperor's own sword — a war he declared or an ally's offensive war he joined — breaks the titles as before. Measured on the retest's turn-24 save: 47 of 45 through the league's war on Austria (was 47 → 41 and a dissolution on the same end turn).

### 81.3 Recognition by defeat (RS-D1, RULED September 28, 2026 — §6.1; lever `congress.A_PEACE_THAT_KEEPS_THE_CAPITAL_RECOGNIZES`)
A SIGNED war-ending peace that leaves a great power's **capital** held by the Emperor or his vassal chain (`congress.capital_in_our_hands` = the `_capital_taken` read the sue rung, GEV-1 and the title rule already make; a carved client counts, an ally does NOT) latches that court's recognition as a third kind, `kind: "capital"` with the capital named — written by `congress.note_ratification(..., capital_kept=)`, whose caller `game_end.note_ratification` reads the map AFTER the clauses applied (a clause handing the capital back has already run). Kind precedence: `table` (signed while the Congress sits) > `beaten` (ceded by clause) > `capital`; a minor never latches; a truce, a truce expiring into peace (`game_end.count_peace`) or an elimination writes nothing; player only. **The breakers:** the two existing ones (a new war between the Emperor and the court — `note_war_entry`; the Emperor's capture from its bloc or of its covets — `note_capture`) and the new one — the capital leaving the bloc by any road (handed back, retaken, taken by a third party, its holder's rebellion), derived inside `_signed_record` with no new field, and stamped by the tick (`_take_answers`: `broken: {turn, reason: "Vienna left our hands"}`). **The price rider** (own lever `settlement_scoring.A_RETAINED_CAPITAL_IS_A_CAPITAL_LOST`): `capital_retained_by_proposer_bloc` — the accepting leader is a great power, its home capital stands in the PROPOSER LEADER's own bloc (the leader or its vassal chain — the same read as the latch; a co-belligerent ally holding it buys nothing and costs nothing), and no territory term hands it back — is wired into `calculate_common_peace_acceptance` step 6, where `calculate_leader_own_losses(..., capital_retained_by_proposer=True)` reads it as the capital LOST (−15) and forfeits the kept-all bonus (+5): recognition by defeat costs a defeat, not a white peace. Measured on the staged shape (France holding Vienna, a white peace plus 100 gold): Austria reads exactly 20 lower with the rider, the whole difference the rider's. **What the player reads:** the Congress row "RECOGNIZES — it signed the peace that left Vienna in our hands (turn N)"; the SUES projection's tail "; a peace that leaves Vienna in our hands recognizes the order" (a court whose capital we hold always SUES — it never reads REFUSES-at-war — so the road is named on the projection before a summons and on the suing court's price while it sits); the settlement REVIEW (`congress.recognition_by_capital_preview`, `recognition_note` on the confirm dialogue and appended to its text) and BOTH ratifiers' summaries (`congress.recognition_lines` via the same-turn stash `game_end.take_recognition_lines`, on the bilateral treaty's `terms_ratified` and the table's result message): "Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty." **Every courtship lever quotes its cost in turns** (lever `congress.THE_LEVERS_QUOTE_THEIR_TURNS`; `congress.courtship_clause(world, points)` ← `courting_rate` = the Cabinet's applied IMPROVE figure, +8 on the 1805 board): " — about 5 turns at +8 a turn; the Congress sits 8", " — about 9 turns at +8 a turn — not within this sitting (7 turns remain)", on the treaty lever's courtship arm, the relation lever (to the GAP, not to +100), the bundle's relation row (`turns_clause`) and the bundle sentence; the unpayable arm is left as it was (its "courting alone" clause would lie where relations cannot rise that far, and the arm is unreachable on the shipped board). **Amends SR-1a's ruling (2)** (`SCORE_MANDATE_PLAN.md` §2 Chunk 1): a retained province is still not reconciled (ruling (1) stands), but a retained CAPITAL now latches — `test_sr1a_status_quo_is_a_cession::TestTheAARShape::test_it_does_not_latch_the_congress` flipped consciously.

### 81.4 The gate warns about the league the summons makes possible (RS-10; lever `congress.THE_SUMMONS_NAMES_THE_LOWERED_GATE`)
`congress.league_warning(world, table=None)`: when the lowered gate is authored and at least two great powers would REFUSE, "the summons lowers the league's gate to 40 while two great powers refuse (Europe's alarm stands at 56): Russia and Austria would gather against us — once the alarm reaches 40" / " — it would brew at once" / " — a league already brews; it declares in N turns" (the refusers at peace with us and not our vassals are the courts it names; refusers already at war "already march"). Read on the summonable gate line (`state_line`, " · " after the Cabinet hint) and appended to the summons' own report. While it sits, `march_blocker` reads the BREWING league ("no coalition stands against us yet — a league brews and declares in N turns (alarm X against a gate of Y)") instead of "no coalition stands against us to join" while one gathers.

### 81.5 The alarm line is one forecast of the tick (RS-16; lever `congress.THE_ALARM_LINE_IS_A_FORECAST`)
`coalition.forecast_alarm_tick(world) → {now, gains: [(label, amount)], decay, next, net, capped}` is a pure mirror of the player-slot producers `process_coalition_turn` applies, in the tick's own order with the store's 100 cap (our share of Europe, our bloc's weight in Europe, the size of our army, our refused calls to arms, the peace overtures we spurned, the designs we deny, a formation's grudge, the refusers' grudge, the ultimatums we defied), against `_calculate_threat_decay`; pinned equal to the tick on the boot (70 → 68) and on the turn-24 save (56 → 57). `congress.alarm_road` reads it: "rising 1 a turn: our bloc's weight in Europe +3, the designs we deny +1 against 3 of decay (one, plus one for each court at peace with us, at most three); a treaty that dissolves a league halves it" / "falling 2 a turn: …" / "holding: nothing adds to it; …", plus " — the alarm cannot rise past 100" when capped. Before RS-16 the line read the gross decay alone ("it falls 3 a turn") on a board that rose 1 a turn for nine turns; the ending C3 probe (`tools/_score_probes.py::ending_c3_alarm_forecast`) now reads the signed net (the legacy "falls N" reads as −N). `test_sr1c_the_gate_line_teaches_the_road`'s two alarm-road pins re-seated consciously.

### 81.6 No AI offer the table refuses (SF-V1; lever `ai_diplomacy.NO_OFFER_THE_TABLE_REFUSES`)
`ai_diplomacy.treaty_offer_refusal(world, nation, proposal_type, recipient=None)` reads the ratifier's OWN two guards — the no-downgrade rule (`_UPGRADE_ORDER`: "already at ALLIANCE — DEFENSIVE_ALLIANCE would be no upgrade") and the relation floor (`check_relation_requirement` / `STATE_RELATION_REQUIREMENTS`: "relations −60 are below the 20 a DEFENSIVE_ALLIANCE needs") — for the four state treaties only (a peace, a truce, a gift, a petition or an ultimatum is not governed). `deliver_ai_proposal` withholds a player-addressed letter it would refuse (returns None; it reads the TERMS' type first, since an opportunistic ask ratifies as a non-aggression pact); the allegiance auction offers `best_ratifiable_treaty(world, nation, "defensive_alliance")` — the ladder walked down (alliance → defensive alliance → non-aggression → open borders) to the best pact the relation permits — or resolves `player_won_no_pact` when none is. The ratifier's refusal names the treaty and the floor: "Relations with Sweden stand at −60; a Defensive Alliance needs 20." Measured on five retest arms: 14 refusals of Sweden's defensive alliance from the auction at −60. Fixture rule for tests: a staged AI letter must be one the ratifier would sign (the relation at the treaty's floor) — seven fixture families corrected.

### 81.7 No whole-war letter the table refuses (SF-V5; levers `ai_diplomacy.THE_LETTER_COVERS_ONLY_THE_PAIRS_AT_WAR` + `THE_LETTER_IS_RATIFIABLE_WHEN_SENT`)
At the ONE emitter `_emit_settlement_offer_for_war` (periodic scan, the request-terms grant, the Arbiter's mediation): the letter covers only the opposing courts with a live WAR pair against a court on the player's side (ONE reader `settlement_staging.covered_courts_at_war`, which `ai_diplomacy._covered_at_war` delegates to — a truce is not a war to settle; `compute_direct_scores_by_enemy` reads WAR pairs only, which is why a truce court hard-stopped the review with `no_direct_war_score_for_covered_enemy`), the senior covered court writes it when the leader itself stands in a truce (`accepting_leader_for_coverage`), eligibility refuses a war with no covered court at war (`no_covered_enemy_at_war`), and the letter is DRY-RUN through the per-court table with the offering courts' consent (`_letter_would_carry` ← `compute_per_court_acceptance(..., consenting_courts=covered)`, SR-2a's trio) — a package that would not carry is not sent and spends no cooldown (the war is read again next turn). The three producers handle a withheld letter: the periodic scan and the mediation produce nothing; a player's request for terms lapses ALOUD ("No terms from Britain — … the request lapses. Ask again when the field has moved.", `resolve_reason: no_ratifiable_terms`, the request's own cooldown, a `settlement_terms_request_refused` log row). **The same reader at the ANSWER** (`settlement_offers._live_covered_for_offer`): a letter is persistent and the board moves under it inside the same phase — on the OP arm's turn 10 Russia's truce, signed the same enemy phase the letter arrived, made a letter that was ratifiable when SENT hard-stop when OPENED — so the accept drops a covered court that has since signed a truce with our side from the coverage, exactly as it drops a court that left the war (FA-3), and the note names it as what it is ("Russia stands in a truce with us; these terms now bind the courts that remain" — never "made her own peace"). Measured on the OP arm: Britain's letter covered Russia and Austria while each stood in a truce with every court on France's side; the turn-13 and turn-16 "re-sends" were the player's own request-terms answer and Russia's mediation through the same emitter, not a lifetime defect.

## 82. THE SCORE FINISH — STEP 2, "Berthier tells the truth" (SR-6a · SR-6b · SR-6c · SF-MD-1 · the reserve · SF-DIP-1; October 2, 2026)

Display and copy, no series moves. Landing record `SCORE_FINISH_SPEC.md` §3 Step 2. Every rule below sits behind a module lever (`UPPER_CASE = True`; False = the shipped behaviour byte for byte); `tools/_step2_series_arms.py` sets all 50 in the child and proves `BASELINE_SERIES` byte-identical both ways.

### 82.1 The sighting is live (AAR-5 / AAR4-X2 / AAR24-X4; `intel_surfaces.THE_SIGHTING_IS_LIVE` · `THE_SURFACES_NAME_THE_GARRISON` · `THE_ENEMY_WORKS_REGROW_ALOUD`)
`backend/game_logic/intel_surfaces.py` is the ONE module every enemy-sighting surface reads. `live_sightings(world, viewer)`: the men standing, this morning, in every province the viewer sees at FULL — exact strength, `intel_turn` = now, `source: "live"`; our own men, captives and empty corps never listed. `enemy_sightings` lays the live read first, then the frozen snapshots only where the fog is real (PARTIAL / STALE / LAST_KNOWN); a FULL label whose live read is empty is yesterday's label and is dropped; a `[partial]` row never outranks a live one. Readers: the dispatch's INTELLIGENCE rows (each row now carries `roster_name` and `source`), the Strategic Ledger's intel tab (humanised `name` + `roster_name`, the ledger vocabulary "last seen: band" / "unknown"), Berthier's report (a man confirmed live elsewhere leaves RECENT REPORTS). `known_garrisons` lists the garrisons of courts at war with the viewer through `garrison_report.garrison_view` (exact at FULL, a band at PARTIAL) as rows of their own, `kind: "garrison"` — a row that is a province, not a man; `garrison_regen_line` turns a foreign garrison's regrowth into a turn event ("Vienna's garrison regains 2,000: 23,000 -> 25,000."). **Rule for a probe or a test:** a live row agrees with the MAP at FULL, a snapshot row with the STORE; a garrison row is never looked up as a marshal.

### 82.2 One clock for every order ETA (CRT-4-X1; `strategic.ONE_CLOCK`)
`strategic.order_turns_remaining(order, current_turn, *, including_current=True, movement_range=1, before_tick=False)` is the ONE reader: an untimed road is `march_turns(steps, range)`, the issuing turn's tick is skipped, and `before_tick=True` adds the tick that has not yet run — the report rows read AT the tick, the Ledger / relay / desk read BEFORE it, and they agree to the turn. `order_eta_phrase(order, turn, *, movement_range=)` takes the marshal's range at the MARSHAL STATUS seam; the per-turn MOVE_TO row's `turns_remaining` is the same clock.

### 82.3 The dispatch's standing classes and their yields (RS-D2 · NPC-14 · NPC-15 · NPC-27 / NPC-D1 · RS-17 · RS-23 · IQ6-D3; `dispatch.*`)
- **The levy yields once stated** (`THE_LEVY_YIELDS_ONCE_STATED`, `LEVY_STATEMENTS` 3, `LEVY_LEAD_MAX` 1, `LEVY_HEADROOM_CHANGE` 0.20): a statement is a levy line the player actually READ (lead or sub-beat); after three with no material change — headroom ±20%, price, a new war — the candidate leaves the page for the Ledger's own line and returns on a flip (the gate closed and re-opened); the memory is `headline_lead_memory["levy_said"]` (no new field; popped when the page has no candidates). A page that would have carried only a thrice-stated levy says "a quiet morning on the front" ONCE (`quiet_morning`, weight 5) — narration F1's floor until Step 7b's front page.
- **The occupied homeland stands on the page** (`THE_FALLEN_HOMELAND_STANDS_ON_THE_PAGE`): `homeland_occupied` (81) is a STATE class — the capital first, at most three names plus "and N more", the holders named, silent on the morning the loss is fresh news (`home_captured` / `capital_lost` restate it), riding PC-7's cooldown and the escalation ladder. **It takes the levy's yield** (`HOMELAND_STATEMENTS` 3 statements of the SAME occupied set, then `HOMELAND_YIELDED_WEIGHT` 40 — on the page as a sub-beat, never the lead — until the set changes; memory `headline_lead_memory["homeland_said"]`, the yield applied in `_select_headline` before the ranking): the Step 2 exit measured the un-yielded class leading 6 of 9 mornings and burying the first erosion notice (55). `home_captured` names its captor ("Provence has fallen to Austria", `THE_FALLEN_PROVINCE_NAMES_ITS_CAPTOR`). **One voice on a collapsed realm:** while `collapse.get_collapse_state` is live (IQ-2's `empire_reduced` owns the page) the class is not manufactured at all — the occupied list and "the Empire is reduced to one province" are the same fact, and a second voice on it took the hand-back from the money rung the collapsed France needed to hear; it returns the morning the realm is no longer collapsed.
- **The grip beside the authority** (`THE_BRIEFING_SHOWS_THE_GRIP`): the situation's authority label reads "N at court; the Empire's grip G (firm ≥85 / shaken ≥60 / cracking >30 / broken)" off `authority.get_imperial_grip` when the two differ, "; the Presence at +P%" when a standing sovereign's aura is under full; `situation["imperial_grip"]` / `["grip_label"]` / `["aura_pct"]`. **The aura has its beat** (`THE_AURA_HAS_ITS_BEAT`): a band crossing — full / dimming ≥7 / fading ≥4 / guttering ≥1 / out, and the way back up — is `aura_dimmed` (83), told once per crossing on `headline_lead_memory["aura_band"]`; the Generals card's ability line states today's figure (`marshal_overview.THE_CARD_SHOWS_THE_PRESENCE_TODAY`).
- **The summonable gate is news** (`THE_SUMMONABLE_GATE_IS_NEWS`): the morning every gate term but the admin action is met, `congress_summonable` (86) leads once — "THE CONGRESS OF PARIS MAY BE SUMMONED — 47 of 45 titled provinces are held and Paris is ours. London and Vilna would refuse today … Summon it from the Cabinet (F1), or type 'summon the congress'." — with each refuser's price, the lowered-gate fuse (RS-10) and the ceder risk (RS-2) as `congress_summonable_term` (69) sub-beats; the latch `summonable_told` lives in `world.congress`, created only at the latch (a world that never summoned keeps `congress is None`) and cleared when any term blocks again.
- **The cascade is grouped** (`THE_CASCADE_IS_GROUPED`): `diplomacy._note_alliance_cascade` writes ONE rail row per ally per turn (`details["war_id"] = "cascade:<ally>:<turn>"`, the enemies in `against`) and `alliance_cascade_rail_text` renders "Prussia, Spain and Bavaria Enter War! … enter the war against Austria and Russia via their alliance with France."; the dispatch groups the family per ally and the campaign log names the enemy.
- **The intent narration has a dead band** (`intent.THE_NARRATION_HAS_A_DEAD_BAND`, `INTENT_DEAD_BAND` 5; `THE_TAIL_NAMES_ITS_COURTS`): the seen string is `want|price|weight`; a rung change whose weight moved less than the band keeps its anchor and prints no hardens/eases line; the tail names its courts ("And Spain and Holland stir at their own designs").
- The defenders' line is a serial join ("Lannes, Murat and Napoleon stand in his path", `THE_DEFENDERS_ARE_JOINED_IN_SERIES`); the famine ladder counts its dead ("1,351 men dead", `THE_FAMINE_COUNTS_ITS_DEAD`); the rank at the dispatch's six wound-and-death lines, the capture headline and the desk is the court's own (`THE_RANK_IS_THE_COURTS_OWN` → `display_names.marshal_honorific`, below).

### 82.4 The desk reads the table (SRX-5 · RS-14; `question_desk.THE_DESK_READS_THE_TABLE` · `THE_DESK_PLACES_A_COURT` · `THE_DESK_READS_THE_ALARM`; `clause_guards.TELL_ME_IS_A_QUESTION`)
Three wide kinds: `demanded` ("what did the Russians demand?" — the letter on the desk: its turn and terms, "the letter waits in the mailbox"; while the Congress sits, the court's refusal and its price; else the last `proposal_arrived` record, answered and gone; else "nothing was demanded"), `where_nation` ("where is Austria?" — "Sire — Austria: Mack at Swabia (large force); no word of Archduke Charles", confirmed exact at FULL, last reported otherwise), `alarm` ("why is Europe alarmed?" — the level, its label, the next tick's forecast, the Diplomatic Ledger's key). Demonyms resolve to courts (`_demonym_forms`); "remind me what … / tell me where …" is a question for the parser gate.

### 82.5 The settlement surfaces tell one truth (RS-9 · RS-19 · RS-18 · RS-21 · RS-22 · SRX-6 / SF-V2 · RS-20; `settlement_*`)
- The ratification record names its coverage (`settlement_ratify.THE_RECORD_NAMES_THE_COVERAGE` — the dialogue's own `war_label`); the review's coverage chips keep every court and list the uncovered ones (`settlement_presentation.THE_COVERAGE_LINE_KEEPS_EVERY_COURT`: `build_settlement_review(table_covered=…, leaders_for_label=…)`, `_uncovered_courts`, "Whole-war settlement" only when nothing is uncovered, a `coverage_label` stamped; `proposer_side` must be a string for the label).
- The voiced summary fills its two slots from `applied_clauses` (`THE_SUMMARY_FILLS_ITS_SLOTS`, `_summary_slots`: received = clauses the proposer's bloc is paid, paid = clauses it pays; a payment alone is never voiced as a return — the common-peace register instead).
- A warning names its component and its sign (`THE_WARNING_NAMES_ITS_COMPONENT`: "National design (+12)"); a review every covered court CONSENTED to carries no acceptance concern — `build_settlement_preview` returns `warnings` consent-filtered (`_warnings_after_consent`) and `warnings_before_consent` raw.
- The legitimacy sentence presses ONE court (`settlement_staging.THE_HINT_PRESSES_ONE_COURT`): "Press Austria alone: the separate peace. It costs N diplomatic points; you have H. The others — X and Y — can each be treated with alone, at N points apiece."
- A white peace speaks its own blocker (`diplomatic_templates.THE_WHITE_PEACE_SPEAKS_ITS_OWN_BLOCKER`, `SPOKEN_BLOCKER_PHRASES_WHITE_PEACE`, `spoken_blocker_phrase(component, fallback, *, white_peace=)`), at the dialogue's message and at every per-court holdout line (`resolve_multi_court_settlement_voice(white_peace=)` reads the G4F-19 "every term is the bare peace clause" derivation before the voice is built); "Will NOT carry as drafted" never stands beside a live Ratify button (`_verdict_beside_the_button`: "Carries on the leader's word — a white peace asks no court to sign away anything, and its leader's consent is the gate."; the per-court verdict kept as `per_court_verdict_display`).
- The player's own declaration (and its objection) carries `suppress_proposal_result_popup`; the PL-14 net's last fallback is RESOLVED → "Diplomatic Action Noted" (`main.THE_NET_FALLS_BACK_NEUTRAL`), never a REJECT the net did not see.
- The Congress's ports lever through a truce or a peace: "the System shuts a port only against a court at war with it — in a truce, no port is closed to her" (`congress.THE_SYSTEM_NAMES_ITS_CONDITION`); the decree reads "shuts its ports to Britain at war".

### 82.6 The field speaks display names; the rank is the court's own (RS-26 / NPC-12 · NP-X7 · RS-29; `combat.THE_FIELD_SPEAKS_DISPLAY_NAMES` · `display_names.THE_HONORIFIC_IS_THE_COURTS_OWN` · `strategic.A_SUPPORT_ORDER_IS_SINGULAR`)
`combat._field_names(text, *marshals)` replaces each combatant's roster key by its display name (whole word, longest key first) at the resolver's two `"description":` sites — the one seam the combat lines are composed through — and the muster hedge reads `humanize_entity_name`. `display_names.marshal_honorific(world, name)` → "the Emperor Napoleon" (a sovereign), "the Archduke John" (a rank word in the name), "General Kutuzov" (a foreign commander), "Marshal Ney" (the player's own); its docstring states that coverage. "his support order" is the SUPPORT flavour. NPC-12's OPEN REMAINDER (the ~426 other enemy-reachable interpolations) stays open and tagged; the census pin drives a real battle and scans every sentence of the reply, the report and the events.

### 82.7 Every man his own voice (SF-MD-1 / RS-24; `combat_executor.THE_VOICE_ROTATES_ON_HIS_OWN_RECORD` · `marshal_voice.THE_NAMED_BANK_FALLS_THROUGH` · `enemy_voice.THE_NAMED_BANK_FALLS_THROUGH`)
`combat_executor._voice_rotation_key_for(world, marshal, region, situation)` is the index both voice sites pass: `battles_won + battles_lost` (a decided battle, already counted by `resolve_combat` before the voice sites, subtracts itself back out) plus the stalemate rows naming him in the log (a draw counts on neither record; today's draw is not yet logged) — every battle advances the key by exactly one, both boards. `marshal_voice.voice_bank` / `enemy_voice.voice_bank`: the man's own row first, then his personality's lines, never a line twice; index 0 of every bank is unchanged. Every French marshal of 1805, both Archdukes, Kutuzov, Mack and Wellington carry rows in every situation they can speak; every personality bank holds five. The census: no man says a line twice within five of his own battles — structurally (every man × situation × five-key window) and on the 40-turn commanded arm (`tools/_sfmd1_voice_census.py`: 8 speakers, 26 battles, 0 repeats); the playtest driver's battle record carries `enemy_voice` beside `voice`.

### 82.8 The reserve and the dial (RS-5 / VP-R1-X1 / NPC-D4 · RS-13 · NPC-11 · NPC-13 · NPC-17 · NPC-21 · NPC-25 · NP-X5 · RS-28 · SF-DIP-1)
- **The objection offers a man we have seen** (`disobedience.THE_OBJECTION_OFFERS_A_MAN_WE_HAVE_SEEN`): for the player's marshal `_get_aggressive_preferred` takes its candidates from `get_visible_enemies`, places each where the player believes him (`strategic.pursue_known_location`), measures to that province, and asks the crossing gate (`_crossing_open`) — an adjacent foe behind shut water is skipped, and so is a pursuit whose first leg is the shut water. **The alternative is a foe at war** (`THE_ALTERNATIVE_IS_A_FOE_AT_WAR`): `get_enemies_in_range` keeps only courts at WAR with the marshal's and, for the player, only men in view. **A refused Trust keeps the objection** (`strategic_executor.A_REFUSED_TRUST_KEEPS_THE_OBJECTION`): when the preferred order's execution returns `success: False` with no battle, `pending_strategic_objection` is restored, the authority tracker put back as it was, and the reply says "The objection stands — 'insist' presses your original order". **The pursuit states its terms** (`THE_PURSUIT_STATES_ITS_TERMS`): an `attack <marshal>` that auto-upgraded (PURSUE with the command's action `attack` and `attack_on_arrival`) says it is a standing order — the pace, the turns to the sighting, the interrupt, the lapse, and `'<name>, cancel'`.
- **The pressed attack prints its muster** (`meta_executor.THE_PRESSED_ATTACK_PRINTS_ITS_MUSTER`): trust / insist / compromise pass `command={"_muster_confirmed": True}` — the band prints, the confirm popup stays off; the disobey arm (`_disobedience`) keeps none.
- **The literal quotes the typed order** (`combat_executor.THE_LITERAL_QUOTES_THE_TYPED_ORDER`): the auto-upgrade's `raw_input` is the command's `_raw_input`, the synthetic "X attack Y" only as a fallback.
- **The engaged-move refusal names the enemy** (`movement_executor.THE_ENGAGED_REFUSAL_NAMES_THE_ENEMY`): "Cannot advance while engaged with Mack at Swabia. He may fall back to friendly ground — Lorraine, Rhineland — or fight." / "No friendly province adjoins him: he must fight or stand."; the result carries `retreat_options` and a typed hint.
- **The muster names the lead** (`combat_executor.THE_MUSTER_NAMES_THE_LEAD`): no "if he marches" when the Emperor IS the attacker; "will not lift a finger for this marshal" → the lead's honorific. **The charge names its threshold** (`THE_CHARGE_NAMES_ITS_THRESHOLD`): "a single battle won as the attacker arms the charge (recklessness 0 of 1)".
- **A disabled option refuses with its reason** (`diplomatic_executor.A_DISABLED_OPTION_REFUSES_WITH_ITS_REASON`): on a `proposal_confirm` dialogue only — a typed "1" on the closed "Send as suggested" arm answers "'Send as suggested' is not open, Sire — <reason>" and the dialogue stays; the petition families keep their own refusal roads (a DP-short Grant STANDS, IQ7-RV2).
- **The Waterloo example validates**: `mods/examples/battle_of_waterloo.json` carries Britain's Netherlands and Prussia's Berlin off the map's edge (the runtime rule wants every nation's capital among the scenario regions). **RS-28**: the `fixed_rng` fixture pins `random.randint` (the 5% fumble was the one live die) — NOT the mechanism, which stays unisolated; the P1 test pins the aura's inputs before the attack.
- **The dial survives the drop** (`settlement_actions.THE_DIAL_SURVIVES_THE_DROP`): a cover drop keeps the standing terms and strikes only the clauses naming the dropped court (`clause_names_court` over `from/to/nation/court/vassal/lord/target/beneficiary/payer/recipient/client/subject/overlord/counterparty`); a cover add appends the baseline slice authored for the added court; the `peace` clause stays exactly once; the message names each court's change (`_terms_after_cover_edit`). A coverage change still lapses the letter's consent (`consent_kwargs_for_restage(…, covered)`).

### 82.9 The campaign log's tier and the Moniteur's open gate (EAS-2 · RS-17; `campaign_log.THE_LOG_HAS_AN_IMPORTANCE_TIER` · `gazette.THE_MONITEUR_SEES_THE_OPEN_GATE`)
`campaign_log.event_tier(event, world)` stamps every `GET /campaign_log` row with `tier` ∈ {lead, notable, routine} — `LOG_TIER_LEAD` / `LOG_TIER_NOTABLE` / `LOG_TIER_ROUTINE` partition `CAMPAIGN_LOG_TYPES` exactly (a new type fails the census until classified); `battle` leads when it took the province, destroyed or routed a corps, or was decisive; `region_captured` leads when the province is a capital (read off the world). Display only; the client half is Step 7's. The Moniteur's Congress column at a gap ≤ 0: "THE CONGRESS OF PARIS — N of M provinces titled: the Emperor may summon the powers." with the table as it stands, or "… yet the summons waits: <the one unmet term>" (`_open_gate_line`); the near-miss column is unchanged.

## 83. THE SCORE FINISH — STEP 3, "Europe acts without France" (RS-3 · SR-7a · SR-7b · SR-G7 · SR-7c · RS-27 · SF-LB-1; October 2, 2026)

Chunk 7 as one balance block. Every slice sits behind its own module lever (UPPER_CASE, `True`; lever down = the shipped behaviour byte for byte); Step 3 MOVES `BASELINE_SERIES` by design and it was re-recorded ONCE from the fifteen-arm attribution `tools/_step3_series_arms.py` → `tools/_step3_series_arms_final.json` (arm 0 reproduces the SR-5a series byte for byte; eight of thirteen levers move it alone; the ALL arm diverges at [13]). M1–M7 byte-identical. SR-7d "The Doctrines" is NOT in this step (next, `DOCTRINES_SPEC.md` §7).

### 83.1 A field win halts before the works (RS-3; `combat_executor.A_FIELD_WIN_HALTS_BEFORE_THE_WORKS`)
ONE sentence `combat_executor.works_halt_line(world, marshal, region)` — non-empty when the victor's court is at war with the province's holder and `garrison_report.garrison_fights(region)` (the march's own predicate) says the garrison stands: "{marshal} halts before {region}'s works — the garrison that fights to the last man of N still stands and must be assaulted." Read at the FOUR seams a field win advances through: the main advance (the pursuit halted, the movement line replaced), the capture branch (no conquest), the auto-bombardment kill's exit and the charge's exit. The loser flees; the province changes hands only by an assault on the works. Both boards (the AI's own wins halt the same way — 9–10 halts on the ambient series). Pins `tests/test_rs3_the_garrison_stands.py` (11): both boards, every seam, the scout's sentence true of the attack too, lever down = the old walk-in.

### 83.2 SR-7a "The AI's odds gate and its dithering" (AAR-D8 · CQ-22 · IQ5-R1 · XR-3)
- **A small garrison surrenders** (`garrison_report.A_SMALL_GARRISON_SURRENDERS`, `SMALL_GARRISON_SURRENDER_FLOOR = 500`, `detachment_surrenders(region)`): a detachment under 500 lays down its arms to the first corps that marches in — `garrison_fights` reads it, so the march, the AI's assault rung (P4.25), the undefended capture (P4.5), the intent validation, the walk-in and the capture hint all inherit it; the capture line says so ("The detachment of N at X lays down its arms."); `describe_garrison` names it on the scout. AAR-D8's grind (a 47-man garrison assaulted four turns running) cannot recur.
- **The AI obeys the muster gate** (`enemy_ai.AI_ATTACKS_OBEY_THE_MUSTER_GATE`): a CAUTIOUS effective personality whose chosen P4 target reads the muster band the player's own gate arms on (`jealousy.glory_attack_odds(...)["band"] == MUSTER_GATE_BAND`) holds instead (`_find_attack_opportunity` → None, recorded in `_held_by_the_odds_this_phase`). The same rule the player's delegation and the glory attack already obey, GR5.
- **A held corps is not idle** (`enemy_ai.A_HELD_CORPS_IS_NOT_IDLE`): the dither the first cut created — the stagnation breaker force-unfortifying an idle cautious corps at peace and the P2 threat-response re-fortifying it next phase — is closed three ways: a corps held by the odds is not "idle" to `_get_stagnation_action`; the P2 fortify site reads `ai_refortify_cooldown` / `_unfortified_this_turn`; the breaker keeps a corps's works when no enemy contact and no strategic enemy region exists (a corps at peace holds its works). AI C5 (the fortify dither) reads ✓.
- **One stance rule for drill** (CQ-22, `tactical_executor.ONE_STANCE_RULE_FOR_DRILL`; §6 row 5 rules the DIRECTION = the executor's): a drill in AGGRESSIVE stance is refused on every road — the player's executor (`order_refusal_response(..., stance_gate=)`), the pre-objection battery, the AI's P4.9 heal drill (`drill_refusal(..., stance_gate=)`) and P6 (`_aggressive_stance_refusal`). Measured first: 2 of the 3 AI drills on the ambient board were taken in AGGRESSIVE stance. `test_cn4_the_chip_honesty_census.py`'s asymmetry pin flipped consciously.
- **Bleed by the men committed** (IQ5-R1, `combat_executor.BLEED_BY_THE_MEN_COMMITTED`): `_distribute_casualties(raw, participants, lead=)` splits the pool by `_committed_weight` — the lead at full strength, a reinforcer at `COMMITTED_ALPHA × strength × _pair_contribution_scale` — so a half-committed man bleeds half a share (36 reinforced splits on the ambient series). `test_iq5_both_sides_of_the_butchers_bill.py` measured the full-strength split and runs with the lever DOWN by a module fixture; the split's own pins live in `test_sr7a_the_ais_odds_gate.py`.
- **An in-place capture marches nowhere** (XR-3, `combat_executor.AN_IN_PLACE_CAPTURE_MARCHES_NOWHERE`): capturing the province the corps already stands in charges no march attrition and narrates no march.
Pins `tests/test_sr7a_the_ais_odds_gate.py` (34).

### 83.3 SR-7b "The long peace, measured" + SR-G7 "The Armed Peace" (PB-D1; `coalition.THE_ARMED_PEACE`)
The baseline arms were the ruling's own research (§6.2); this step re-measured the three commanded seeds with the lever down (alarm 31 → 6 → 0 → 0 at turns 20/30/34/40 on marengo, no league in 40 turns, France 27 provinces) and up. **The mechanics as ruled, zero new serialized fields, one roster pass:** `armed_peace_reading(world)` — the hegemon leads the largest bloc at ≥ `ARMED_PEACE_SHARE_FLOOR` (1/3) of Europe's power, no league active or brewing, some court left to alarm, the Congress not sitting; `hegemon_quiet_turns` = the current turn minus the latest `last_battle_turn` among its standing marshals; the WATCH `ARMED_PEACE_WATCH = 45` (`armed_peace_decay`: decay stops at 45; below it no decay runs, so hegemony lifts a spent alarm back up); the FUSE `ARMED_PEACE_FUSE_TURNS` after which `armed_peace_rise` adds `ARMED_PEACE_RISE = 3` a turn (source `armed_peace`) up to the brewing gate (60), where it HOLDS (after the fuse no decay runs below the gate — the first cut's +3 above a fixed floor was undone by the next tick's decay and the gate was never reached); the existing countdown and `qualifies_for_coalition` do the rest. Hooked in `process_coalition_turn` (the player's slot and every per-target slot; the `armed_peace_watch` source row at 0 with its label when decay is withheld) and in `forecast_alarm_tick` (RS-16's forecast reads the same clamp and rise). **Surfaces:** the Balance-of-Europe rows "Europe watches — France leads 40% of Europe's power (floor 45)" / "The courts re-arm (+3)" (`diplomatic_ledger.balance_of_europe["armed_peace"]`); the war room's THE ARMED PEACE block (`diplomatic_advisory.armed_peace_war_room_lines`: the fuse's turns left, the courts that would consult, the four levers — a court raised above −10 will not join, a bloc under a third ends the watch, the Congress suspends it, a declaration takes the alarm from 45 to 65); the dispatch beat `diplomatic_armed_peace_fuse` on the lapse tick only (HIGH; no new campaign-log type).
**The fuse is 20, not the ruling's 16 — lengthened on measurement, inside the ruled band 12–20, by the ruling's own remedy ("If F1 breaks, lengthen the fuse; do not lower the watch").** At 16 the league declared on turn 31 on marengo and the commanded France (57,000 men at peace, the script never levies) was reduced from 27 to 11 provinces by turn 40 — the per-lever attribution on that arm names the Armed Peace alone (every other lever down leaves 11; the Armed Peace down leaves 27 and no league). At 20: historical brews t27 / declares t30 → France 26 at turn 40; austerlitz t37 / t40 → 28; marengo t32 / t35 → **19, one province under the F1 floor** (army 57k → 679 in five turns against the league). PB-D1's acceptance clause reads **3 of 3** (a league declares on France inside turns 12–40 on every commanded seed, not by cascade, the alarm rising after the peace); the F1 guard reads 2 of 3 and the miss is reported, not hidden — the band's end is reached and the next lever is the user's (§6.2 names none below the watch). The titled count on the Armed Peace's arms: see the landing record. Pins `tests/test_sr_g7_the_armed_peace.py` (36), every fuse pin reading `CO.ARMED_PEACE_FUSE_TURNS`.

### 83.4 SR-7c "Dispersion" (AAR-D4; `world_state.DISPERSION_IS_NOT_PUNISHED`, a module lever)
ONE reader `WorldState.crowding_press(region, marshals_here) → (press, free)`: the first `CROWDING_FREE_CORPS = 2` corps in a province are free of the crowding tax, `CROWDING_FREE_CORPS_CITY = 3` on a capital or major city, and a corps under SUPPORT whose lead stands in the province is not counted (a concentration ordered as one army is not a crowd). `supply_attrition_rate(..., free_corps=)` takes it; `process_supply_attrition`, the Ledger's supply verdict and the muster preview read the same press (shown = applied). The retreat scan's friendly set is `retreat_soil_is_friendly(marshal_nation, controller)` — own soil or any `ALLY_SUPPLY_STATES` court's (PC15-D1's law): Massena falls back to Milan, Davout to Munich. Pins `tests/test_sr7c_dispersion.py` (11). Ambient reach: 23 of 45 three-corps reads relieved.

### 83.5 RS-27 measured and pinned (`tests/test_rs27_the_volte_face_fires_on_its_arm.py`, driven)
The bisect the row asked for named Chunk 1's SR-1d (the league's offer t4 → t9 moved the courtship past the volte-face window) — and the first bisect read "LOG volte_face" off the digest, which DEDUPES a LOG row the rail already printed, so it reported a beat that fired as absent (the IGR-B trap, one instrument over). On the shipped tree the beat fires at turn 21 on `volte_court_austria.json`; the per-lever attribution on that arm reads every Step-3 lever down → 0 (the baseline's miss reproduces) and the works halt (RS-3) and the AI's odds gate EACH necessary: the opening war's course changed and the peace now lands where the courting reaches the floor inside the window. Disposition: pinned firing on its own arm (the arm is unchanged), both directions driven.

### 83.6 SF-LB-1 "Europe's own quarrels" (four levers + one authored deck entry)
- `ai_diplomacy.A_DESIGN_IS_ASKED_BEFORE_IT_IS_FOUGHT` (`DESIGN_ASK_RUNGS` = ask / buy / align / bandwagon): the design ask fires at every rung below coerce — Prussia at `align` (59) now asks Hanover (12–16 asks on the ambient series); before, an acquire design at align never asked, never collected AI-3's two refusals, never opened a war.
- `intent.A_REFUSAL_HARDENS_THE_ASKER` (`WEIGHT_REFUSED_ASK = 6`, cap `WEIGHT_REFUSED_ASK_CAP = 12`, inside `REFUSAL_MEMORY_TURNS`): each refused design ask on the record adds to the asker's weight, both boards.
- `agendas.AN_ALLY_IS_NOT_COVETED` (`ALLIED_STATES`): an acquire design whose target the asker's ally — or the ally's bloc — holds sleeps while the alliance stands (IQ6-D1: a reversed Austria advances to the authored follow-on).
- `agendas.A_CONTAIN_DESIGN_SLEEPS_IN_THE_ARMED_PEACE`: a contain design sleeps while `armed_peace_reading` holds for its hegemon and its court is at peace with him — Russia's `gulf_and_straits` wakes without a volte-face; a brewing league wakes `arbiter_of_europe` again.
- **Austria's deck** gains a third entry `the_eastern_question` (acquire Albania + Rumelia — the Ottoman frontier Vienna turned to whenever Italy and Germany were closed); the volte-face beat names the LIVE design (`emergent_designs.maybe_fire_volte_face` reads `get_active_agenda` first).
Measured honestly: the ambient 7-seed sweep still opens **0 AI-vs-AI wars** — an acquire design between two AI courts tops out at 71–81 against the `fight` bar of 85 (AI-3r's deliberate choice; `PRICE_THRESHOLDS`). The ≥ 3-of-7-seeds target is NOT met; the fight bar is the genuinely unruled question, put to the user with a recommendation in the landing record. Pins `tests/test_sf_lb1_europes_own_quarrels.py` (22).

### 83.6a The standing pins re-seated
**Twenty-two standing pins re-seated consciously, each with its attribution** (the full suite's first run: 22 failed / 28,389 passed): the four series-chain pins (the drill fix, DP-1, RF-3, VP-R1 — one more link: SR-5a's arm 1 is the prior Step 3's arm 0 reproduces, Step 3's ALL arm is the standing series); the WO slice-10 ambient-board figures (ungated seams 11 → 22 + 1, the pair split, the ungated series, cooldowns 12 / 0 → 22 / 0) and WO slice-9's rebellion turns (17 / 23 → 14 / 18; the Kingdom of Italy's elimination step at [12], −12) — **measured with every Step-3 lever down in the child, the SR-5a figures return verbatim** (`tools/_step3_wo_attribution.py` → `_step3_wo_attribution.json`); the FA-D28 grind runs with the small-garrison surrender down (measured lever by lever, the surrender is the sole mover: a 12,000-man garrison surrenders at 500 and the grind ends six assaults in); SR-exit's `garrison_fights` formula gains the 500 floor; the two WO crowding pins stage FOUR corps on a capital (three are free now); the two IQ-7 card pins stage the Swiss loyalty they measure the countdown against (the re-timed board took them under the loyal line); six FA-slice-15b driver pins were red only because the new exit-fix pin set a module lever bare — it uses `monkeypatch` now.

### 83.7 The exit's own fixes
- **Combat C1 — the answered contact prints its muster** (`strategic.THE_ANSWERED_CONTACT_PRINTS_ITS_MUSTER`; RS-13's family one road over): the `attack_anyway` answer to a `contact_bad_odds` question re-issues the attack with `_muster_confirmed`, and the muster gate builds its preview for a strategic re-issue the player confirmed (the gate itself stays off). Pins `tests/test_step3_the_contact_prints_its_muster.py` (3).
- **A prisoner is not a sighting** (`intel_surfaces.A_PRISONER_IS_NOT_A_SIGHTING`; narration C4 at the exit): a man the roster knows to be captured never rides as a frozen snapshot — the live read had skipped him (`captured_by`) while his three-turn-old label in a STALE province still led the morning's intelligence rows (CMD-H turn 40, Deroy taken at Franche-Comte, shown at Franconia). Pins `tests/test_step3_exit_fixes.py`.
- **The digest prints the answered interrupt's muster** (`playtest_driver.THE_DIGEST_PRINTS_THE_ANSWERED_MUSTER`): the reply to an answered contact question carries the muster the battle opened on, and the digest had printed the question and the battle with nothing between — the C1 fix above was invisible to its own instrument. One `↳` sub-line under the POPUP row. Pins `tests/test_step3_exit_fixes.py`.
- **The instrument:** combat F2 counts a BOARD refusal separately (§4.2 — a scout refused because the man is recovering is not a reading of the item; the reader looks across OP / FLD / CMD-H for a capital scout the board let through, else unmeasured with the refusals counted); combat C3 counts the works halt at a capital as the garrison NAMED; AI aliveness C6 reads the turns at war off the digest's own war and peace rows (the Armed Peace puts twenty quiet turns between two wars, and "every turn up to the last attack" had counted the peace against the AI); living-balance C4's court capture strips auxiliaries.

## 84. THE SCORE FINISH — STEP 3's eighth slice, SR-7d "The Doctrines" (DC-0 · DC-1 · DC-2 · DC-3a/b/c; October 3, 2026)

Gate record `DOCTRINES_SPEC.md` §0 (RULED Sept 27, 2026; the seven RV amendments confirmed); landing record §7.1; pins `tests/test_sr7d_the_doctrines.py` (70); sweep `tools/_sweep_sr7d.json` 61 rows → 61 killed, 0 INERT, 0 BROKEN at close (the first sweep found four pins inert and all four were real weaknesses, repaired: the homeland exemption had never had to decide a STRIPPED Paris; the with-support odds saturate at 99 for every French pair so the bar pin is staged at logistics 0 where 50 vs 60 decides it; the enemy's slow-concentration line had been staged on Archduke Charles, who refuses Mack by the authored hostile pair, so the note was empty and the pin conditional — Archduke John answers; the cures effect line had no pin of its own). ONE module `backend/game_logic/doctrines.py`; levers `DOCTRINES_ACTIVE` (master), `FRANCE_DOCTRINE` … `PRUSSIA_DOCTRINE`, `THE_CURES_HEAL`, and `reforms.THE_AI_SAVES_FOR_THE_STAFF` — down, the Step-3 tree byte for byte.

### 84.1 What a doctrine is, and where it lives
A strength and a flaw per great power, authored in `europe_1805.json` under `doctrines` (`{court: {name, says, strength, flaw, cured_by[, shared_on_purpose]}}`) beside the geography list `poor_country`; each clause `{type, value, name[, arm | stripped_at]}` from the closed set `arrival_bar` / `attack` / `defense` / `recruit_price` / `defeat_morale` / `supply` inside `doctrines.CLAUSE_BANDS` (validator `_validate_doctrines`). ONE serialized field `world.doctrines` `{courts, poor_country}` (`doctrines.store_from_data` reads the scenario's and the save's shape); a pre-doctrine 1805 save is backfilled at load (`save_manager._backfill_doctrines`); the legacy world, the tutorial and a created client carry none. In force from turn 1, never bought, never lost; only the flaw is removed — by the cure law while the court's Staff stands (RV-15, `doctrines.cure_status`, derived at every read). A doctrine is the ARMY's: every marshal of the court reads it through `marshal.nation`; a doctrine never overrides the man's character (RV-2) and never costs him trust (RV-16).

### 84.2 The standing term (RV-6)
`Marshal._doctrine_terms` `{attack, defense, defeat_morale (+ *_name)}` — derived, never serialized (declared in `Marshal.DERIVED_STANDING_FIELDS`; both serialization censuses exempt the union of the declared sets). ONE writer `doctrines.refresh_doctrine_terms(world)` (the last statement of `from_dict` and `from_scenario`, every enactment / repeal / lapse, a commission); ONE setter `doctrines.set_marshal_nation(world, marshal, nation)` for every change of a marshal's court (the six vassal writes, the elimination's freed satellites), with an AST census forbidding a bare `.nation =` elsewhere in the backend. Never in `COORDINATION_TRANSIENT_FIELDS`.

### 84.3 The seams
- **The arrival bar** (RV-1): `CombatExecutor._arrival_threshold(reinforcer, primary, region, world, assume_order=None, with_doctrine=True)` is the ONE bar — the resolver's inline `60 if … else 65` and the odds row's literal 60 both call it. `doctrines.arrival_bar_shift` moves the BAR (France −10, Austria / Russia +10), never the score; a negative shift is exempt where the man's own character keeps him away (Eyes on a Crown, a live grievance against the lead, a hostile pair). A roll between the unshifted and the shifted bar is `doctrine_delayed` (classified first; exempt from the Session-61a dock; named on the report and the shelf); a strength-decided arrival is `doctrine_arrived` and named. Rows carry `doctrine`, `base_threshold`, `origin`.
- **Attack / defence** (RV-4, Britain): `get_attack_modifier` × the term (a lead attacking, every reinforcer's committed weight); `get_defense_modifier` × the term before the 1.75 cap; `Marshal.doctrine_defense_share` prints the share that survived the cap (RV-7).
- **The lopsided-defeat morale** (Stubborn ×0.5, Brittle ×1.5): `doctrines.scaled_defeat_penalty` on the loser's term AFTER the penalty's own cap, both resolver paths; the result carries `doctrine_morale`.
- **The recruit price** (RV-17): `doctrines.recruit_price_term` is ONE named term on the DRAFT in `_recruit_cost_terms`, before the laws and the Intendance; the substitute market never reads it; the recruit result carries `doctrine_note` (the enemy-phase line's only term).
- **Living off the land** (RV-5): `doctrines.supply_factor` on `_supply_multiplier` — outside the court's 1805 homeland, never an ally's or vassal's soil, the listed poor country or war damage ≥ `stripped_at` (0.25): ×0.8. **Read forward:** `get_effective_supply_cap(…, forecast=True, extra_war_damage=0.0)` — a forecast reads today's damage less the recovery tick the pass runs first; the attrition pass passes `forecast=False`; the muster adds its own battle's 0.10 / 0.20. A depot is not a cure. The WO slice-8 invariant holds (identity and damage, never capacity).

### 84.4 The cures (DC-2)
`cures {flaw}` is a wired law effect (REFORMS_SPEC §4's tenth type); the Train des Équipages (France, a cure only), the Corps d'Armée and the Divisional System (Austria's and Russia's Staff, their cure as a second clause), the Militia Transfer, the Articles of War. `cure_status` = the cure law in force AND the court's Staff in force; the beats `doctrine_cured_abroad` / `doctrine_cure_lost_abroad` / `doctrine_cure_lost_home` fire from a before/after read at `enact_law`, `repeal_law` and the lapse loop (zero new fields); the player's enact answer names its cure. **The rung saves for the Staff** (`THE_AI_SAVES_FOR_THE_STAFF`, `AI_SAVES_FOR_THE_STAFF_FROM = 0.5`): once a court's chest passes half the Staff's price it enacts nothing cheaper until the Staff stands. T8: Austria cured turns 20–22, Britain 19–24 on the four ambient seeds, none before 10; Prussia and Russia never afford the Staff in forty turns (the chest half).

### 84.5 The surfaces (DC-3)
Generals OUR DOCTRINE (`/marshal_overview` `doctrine`); the nation card's one line (`nations[].doctrine`); the region panel and map tooltip marks (`map_data[].doctrine_supply`, fog applied by the producer, carried through the filtered summary on both branches; war damage below FULL is −1); the LAWS tab `cure_line`; the first morning's `today.doctrine`; the help entry; the desk kinds `doctrine_own` / `doctrine_nation`; the muster row's bar note, the enemy reinforcement line's slow concentration, the muster supply note; the battle report's `doctrine_lines` / `morale_line` / `doctrine_rows`; the diorama shelf; the enemy-phase recruit note; the supply headline's Train remedy. The driver's digest prints the report's doctrine lines (`THE_DIGEST_PRINTS_THE_DOCTRINE`).

### 84.6 Measured
`BASELINE_SERIES` re-recorded ONCE (nine arms; arm 0 byte-identical to Step 3's; France [12], Britain [13], Austria [6], Russia / Prussia byte-identical alone; shipped [13]); M1–M7 byte-identical; the WO slice-9/10 pins re-seated with every lever down reproducing Step 3's figures; the chain pins one link longer; the exit's flips in `DOCTRINES_SPEC.md` §7.1.

## 85. THE SCORE FINISH — STEP 4's head, SF-LB-2 "The Defenceless Prize" (October 3, 2026)

Gate record `SCORE_FINISH_SPEC.md` §6.4 (RULED October 3, 2026); landing record its addendum; pins `tests/test_sf_lb2_the_defenceless_prize.py`; sweep `tools/_sweep_sf_lb2.json` 28 rows → 28 killed, 0 INERT, 0 BROKEN at close (24 for the slice, 4 for the exit's intel fix) (five inert on the first sweep, all real weaknesses, repaired). Five levers, down = the SR-7d tree byte for byte: `intent.A_HOLDER_WITHOUT_AN_ARMY_IS_A_PRIZE`, `war_council.THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE`, `war_council.A_CRISIS_OPENS_ONLY_WHERE_IT_CAN_DECLARE`, `ai_diplomacy.A_COURT_ASKS_BEFORE_IT_DEMANDS`, `combat_executor.A_PROVINCE_OUTRANKS_A_FRIENDLY_NAMESAKE`; a sixth from SF-LB-2b (§85.8), `war_council.THE_COUNCIL_SPENDS_THE_TURNS_INCOME`, down = the SF-LB-2 tree byte for byte. Zero new serialized fields (`war_intents` records gain the display key `opened_at_price`).

### 85.1 The one reading
`war_council.holder_outmatched(world, asker, holder)`: the holder's standing strength plus its guarantors' (`_holder_scale`, the restraint gate's own arithmetic) is at most `HOLDER_OUTMATCHED_FRACTION` (0.5) of the asker's FREE strength (`get_free_strength`); an armyless holder counts; an asker with no free strength threatens nobody; the coveter's own pledge never enters the holder's scale. Read by the intent weight term and the crisis opening, never duplicated (the fraction is read in one place — an AST census pins it). `defenceless_prize(world, coveter[, view])` is the clause as a surface reads it: an AI-vs-AI ACQUIRE design on an outmatched holder, None for the player, a vassal, a deny/contain design, or with the lever down. `coveters_of_prize(world, holder)` is the chip's inverse.

### 85.2 Clause 1 — the weight
`_derive_weight` adds `WEIGHT_HOLDER_OUTMATCHED` (10) when the predicate holds for `against` — any design type, both boards. Boot: Prussia 69 / bandwagon over an armyless Hanover (was 59 / align). The counter: a guarantor's whole army enters the holder's scale, so a pledge from a court whose standing reaches half the asker's free strength lifts the term AND applies the −8 deterrent (the Emperor's pledge at peace); a guarantor at war pledges hollow (N3's +6 stands); a small court's pledge deters −8 and lifts nothing.

### 85.3 Clause 2 — the opening
`crisis_rung_holds(world, coveter, view)`: `fight` always; `coerce` only for a defenceless prize. ONE reading for step 3 (the opening) and step 1 (the liveness poll — a crisis opened at coerce would otherwise be read dead the next turn and cool `starved`). The coerce road opens only with the ladder climbed AND `_restraint_block_reason` None; under `A_CRISIS_OPENS_ONLY_WHERE_IT_CAN_DECLARE` the fight road reads the same predicate (a court the restraints forbid never fore-warns — pin 15 one gate over; a restraint that appears AFTER the opening still cools the crisis on screen through the soft stall). Everything after the opening is AI-3's: the two fore-warned turns, the coercive demand, the ladder and every restraint at the declaration. A guarantee of the holder after the opening passes the crisis `deterred`.

### 85.4 A court asks before it demands
`A_COURT_ASKS_BEFORE_IT_DEMANDS`: the AI-AI design ask (`_evaluate_ai_ai_proposal` arm 0a) also fires at `coerce` while `_ladder_climbed` is False; once climbed the court demands (the open crisis's coercive demand) and asks no more. The player-targeted road (NA-5) is untouched.

### 85.5 A province outranks a friendly namesake
`combat_executor` 4D-4: where no ENEMY answered the attack's target (WO-13's order stands) and the name is a friendly marshal's AND a province on the map, the province is the reading; a friend who is no province is still refused. The 1805 board's one collision is Brunswick (Prussia's marshal, Hanover's province beside Berlin); the validator already WARNS on such a name.

### 85.6 The surfaces
ONE composition `war_council.defenceless_prize_line` ("Hanover cannot defend itself — Prussia's design opens at an ultimatum, not at war"): the Diplomatic Ledger's Intent row (`build_intent_payload` → `summary`, `defenceless_prize`, `defenceless_prize_line`; the client renders `summary`, no `.gd` change); Talleyrand's war room (`_assess_situation` — one line per prize whose design has reached coerce or whose crisis is open, the guarantee named as the counter and DP-gated honestly: "(1 DP — 3 in hand)" / "needs 1 DP, none in hand" / "already stands" / "we are at war with them"; context `defenceless_prizes`); the wizard's Guarantee chip (`_instrument_actions` — `prize_coveters` + the effect text "our army in their scale lifts them out of Prussia's reach").

### 85.7 Measured
The exit's own fix (narration C4): `intel_surfaces.A_FULL_LABEL_KEEPS_ITS_LAST_SIGHTING` — a frozen snapshot in a province in full view today, whose live read no longer shows the man, rides as a `last_known` sighting with its own turn (the most recent knowledge wins the dedupe; the live read still outranks every snapshot); a man standing in a full-view province today gets no frozen row from anywhere (the live read spoke — an empty corps, a prisoner). Pins `TestAFullLabelKeepsItsLastSighting`.
Seven seeds (`tools/_sf_lb1_fight_bar_probe.py`, the harness): Prussia→Hanover opens at coerce on turn 9 (marengo 10), declares on 11 (12), the war ends by 14 (15) with Brunswick and the Hanover capital taken; no other crisis opens. Living balance C1 MET 7 of 7; the variance clause NOT MET ({9, 10} — the council's pre-income `penniless` read, `SCORE_FINISH_SPEC.md` §6 row 14, the user's). `BASELINE_SERIES` [70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48, 46, 33, 30, 27, 14, 11, 8, 5, 2, 7, 4, 1, 0, …] re-recorded ONCE, ten-arm attributed (W+C the sole mover at [28]; the shipped tree at [21] once N lets the army march); M1–M7 byte-identical; WO slice-9/10 re-seated with attribution; fourteen boot-weight pins re-seated. *(Superseded the same day by §85.8's re-record.)*

### 85.8 The chest the council can spend (SF-LB-2b, October 3, 2026 — `SCORE_FINISH_SPEC.md` §6 row 14, RULED + BUILT; the clause still not met → §6 row 15)
The council sits after the admin phase's spending and before the income phase (`_advance_turn_internal`), so the chest `_restraint_block_reason` read at the OPENING was the post-spending, pre-income purse — for an AI court that spends its whole purse every turn, a few hundred gold on every seed until its unseeded economy cleared `AI_WAR_TREASURY_FLOOR` on the same turn everywhere. **ONE seam** `ledger.chest_forecast(world, nation) → {chest, net, projected}`: the live chest plus the ledger's forward Net (`_build_economy` with no applied record — the LAWS tab's and the end-turn banner's own figure); `reforms.lapse_forecast` reads it (never its own copy — an AST census). **ONE lever** `war_council.THE_COUNCIL_SPENDS_THE_TURNS_INCOME`; **one parameter** `_restraint_block_reason(…, forecast=False)`: with `forecast=True` and the lever up the `penniless` gate weighs `projected`; `busy` / `outmatched` / `exposed` never read the arm. **Step 3 (the opening) passes `forecast=True`; step 1 (the declaration) and every other caller keep the live chest** (a call-site census) — a crisis may OPEN on the income the court will have, a war is never DECLARED from an empty chest (the fore-warned crisis soft-stalls `penniless` until the live chest clears). GR5: every court reads the same seam. Rules of thumb: a projection the AI acts on must be the one the player is shown (IQ1-5-1's family — never a second `chest + net`); the opening and the declaration are two readings by design, and the record says which (`opened_at_price` names the rung, the soft block names the gate); **when a restraint is in question, read the council's own call, never an after-turn snapshot** (the probe's snapshot sees the post-income chest and had hidden this for a day). Measured, seven seeds: Prussia→Hanover's FIRST opening is turn 5 on six seeds (historical, austerlitz, friedland, jena, ulm, marengo) and 9 on eylau — was 9 ×6 / 10; the declaration 9 ×5 / 11 / 12, the war over by 12 ×5 / 14 / 15; marengo's first crisis cools on its seeded dip (turns 5–8) and re-opens on 10. **The variance clause stays NOT MET ({5, 9}):** the ladder — any two refused asks of any type — is climbed after turn 3–4 on six seeds and turn 4's projected chest reads 497 against the floor of 500 on each (Prussia's seed-identical peacetime economy), so the chest decides on turn 5 by three gold; `SCORE_FINISH_SPEC.md` §6 row 15 carries the recommendation (seeded patience on the design ask), the user's. `BASELINE_SERIES` [70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48, 46, 33, 30, 27, 14, 11, 8, 5, 2, 0, …] re-recorded ONCE from `tools/_sf_lb2b_series_arms.py` (arm 0 byte-identical to SF-LB-2's; the shipped tree at [21]); WO slice-10's ungated series re-seated from index 15 (`tools/_sf_lb2b_wo_attribution.py`); M1–M7 byte-identical. Pins `tests/test_sf_lb2_the_defenceless_prize.py::TestTheChestTheCouncilCanSpend` + `TestTheDrivenBoard` (two strict xfails on the clause, one passing pin that the opening no longer waits on the spent purse, one on the record's shape) + `tests/test_ai_intent_assurance.py::TestTheStandingRuleOnCouncilWars` (the record bound to the live historical run; the three-turn span a strict xfail); sweep `tools/_sweep_sf_lb2b.json` 9 rows → 9 killed, 0 INERT, 0 BROKEN. The probe (`tools/_sf_lb1_fight_bar_probe.py`) records `restraint_forecast` / `chest` / `chest_forecast` per row and every opening per pair.

### 85.9 The patient ask (SF-LB-2c, October 3, 2026 — `SCORE_FINISH_SPEC.md` §6 row 15, RULED + BUILT; the clause MET)
A court that first stands at its design-ask rung against a holder (trigger 0a of `ai_diplomacy._evaluate_ai_ai_proposal`: `ask` / `buy` / `align` / `bandwagon`, and `coerce` while the ladder is unclimbed) waits a **seeded dwell** before its FIRST court-to-court design ask: `design_ask_patience(world, asker, holder)` = `campaign_variance.seeded_int(seed, "design_ask_patience::<asker>::<holder>", 0, DESIGN_ASK_PATIENCE_MAX=4)`, **0 on the historical seed** (the caller collapses — the raw helper is not historical-aware) and with `A_COURT_IS_PATIENT_BEFORE_IT_ASKS` down. `design_ask_patience_holds` writes the anchor `WorldState.design_ask_first_stood["{asker}>{holder}"]` on the first call that finds the court standing there (serialized; a pre-SF-LB-2c save reads {} and starts the dwell on load, bounded by 4 turns) and holds while `turn − anchor < patience`. Rules of thumb: the dwell delays the FIRST ask only — a pair with a design ask on the refusal record never waits; a zero dwell writes nothing (historical saves byte-identical); the wait skips the ask, never the pair (the dedupe window's idiom — triggers 0b and 1–5 still answer); AI-vs-AI only (the player-targeted design purchase never reads it — an AST census). This is AI-0b's §3.8 contract ("cooldowns and dwell are the seed's own terms") applied to the one cadence it missed: the refusal cooldowns were unseeded, so the ladder climbed on the same turns on every seed. Measured, seven seeds: Prussia→Hanover's first opening 5 / 7 / 7 / 5 / 8 / 5 / 13 (historical / austerlitz / friedland / jena / ulm / marengo / eylau; was 5 ×6 / 9), declared 9 ×4 / 10 / 13 / 15 — the dwell works through the rung (the design ask's own refusal lifts the weight to `coerce`). `BASELINE_SERIES` + M1–M7 byte-identical. Pins `tests/test_sf_lb2_the_defenceless_prize.py::TestThePatientAsk` + the three flipped variance pins; sweep `tools/_sweep_step5.json` (SF-LB-2c rows).

## 86. THE SCORE FINISH — STEP 4, SF-CL-1 "The forecast keeps its word" (October 3, 2026)

Landing record `SCORE_FINISH_SPEC.md` §3 Step 4; rows `BUG_FIXES.md` §SF-CL-1 (X1, X2) + `DESIGN_REFINEMENT.md` SF-CL-1-D1; pins `tests/test_sf_cl1_the_forecast_keeps_its_word.py`; sweep `tools/_sweep_sf_cl1.json` 17 rows → 17 killed, 0 INERT, 0 BROKEN.

### 86.1 The instrument
`tools/playtest_driver.py::ForecastLedger` is a `Transport` observer (the IQ-8 meter's idiom): every POST response the run receives is read once, and each prediction becomes a `forecast` jsonl row beside what the resolver then committed. Families: `muster` (the preview's lead / "expect about" / "up to" / band / WILL JOIN / WILL NOT / each WILL JOIN row's quoted arrival odds, beside `massed_strength` {lead, committed, total, arrived, contributors, absent-with-reason}, the casualty summary and the victor — `committed` is None when the same response carried no battle), `objection` (the message and the band it names — the wire carries the objection as a flag with the detail on the sibling `objection` key, read as the answerer reads it), `interrupt`, `scout` (the garrison figure), `garrison_assault` (garrison before = remaining + losses). `seq` orders rows so a judgement can be paired with the muster that followed it. Lever `THE_DIGEST_KEEPS_THE_FORECAST`. `tools/forecast_census.py <run>/arms` reads the rows into classes: `expected_miss` (every promised corps fought and the massed strength still fell outside [0.8 × expected, ceiling] — a lie), `shortfall_from_absences` (a promised corps whose die failed, reported with the odds the row quoted — the die, not a lie), `solo_mismatch`, `unpromised_arrival`, `band_disagreement` (an objection's or interrupt's band against the muster that followed), `scout_vs_assault` (regen allowed), `band_inversion` (C2's read). A probe's after-turn snapshot is not the engine's own read (SF-LB-2b's lesson one instrument over): the ledger reads the response the player got.

### 86.2 The wire
`muster_preview` (W6-4's structured block, never on the wire until now) and `massed_strength` (the CO-6 figures as a structured key — the lead's pre-battle corps plus the committed sum the resolver weighed over the men who arrived or stood beside him, with `arrived`, `contributors` and the `absent` shelf with the resolver's reason) ride `_COMMAND_RESULT_SIMPLE_FIELDS` and the two hand-enumerated roads (`_copy_truthy_result_fields` at the insist and the charge). Display only; lever `THE_REPORT_NAMES_THE_MASSED_STRENGTH`.

### 86.3 The muster prices the coordination (fix 1)
The resolver stamps `total_coordination_attack_bonus` (combined arms + per-ally + dedicated + adjacent, capped 0.25) on every eligible participant through `_calculate_coordination_context` BEFORE `_committed_reinforcement_strength`, and `get_attack_modifier` carries it — so the preview, which read the reinforcers' modifiers with nothing stamped, under-priced its expected figure and its ceiling by up to a quarter (and the odds band with them). `CombatExecutor._priced_coordination(marshal, joiners, enemy, enemy_joiners, world, battle_region)` is a context manager that stamps the SAME context for the hypothetical "every WILL JOIN present" set and restores every `COORDINATION_TRANSIENT_FIELDS` + `sovereign_presence` on both nations' marshals afterwards; `_build_muster_preview` reads the expected figure, the ceiling, the defender's committed term and the odds band inside it. **The mirror is the resolver's own semantics, not a better one:** the resolver relocates arrivals into the battle province and reads the lead's context in the lead's province, so a joiner is assumed present only when the lead already stands on the field, a joiner standing beside a lead who attacks from next door is marked GONE (he marches off), adjacent guns are never relocated, and every arrival leaves the adjacent count (`assume_present` / `assume_absent` on `_calculate_coordination_context` and `_count_unit_types`; `exclude_from_adjacent` as the resolver passes `arrived_names`). The consequence — a lead attacking from next door earns no coordination from his arrivals — is `DESIGN_REFINEMENT.md` SF-CL-1-D1, not this slice's. Player-only by construction (the preview is built for the player's marshal alone), so the AI's series cannot move; `committed_strength` still feeds the CA9-row-2 confirm gate, which now reads the band the resolver will fight at. Lever `THE_MUSTER_PRICES_THE_COORDINATION`; down = the pre-SF-CL-1 preview byte for byte (measured: the Emperor's battle 23% over its own ceiling).

### 86.4 Measured on the exit archive (`docs/audits/score_runs/2026_10_03_sf_cl1/arms`, the six player arms)
**44 forecast rows** (garrison_assault 4, muster 18, objection 16, scout 6); **expected_miss 0 · solo_mismatch 0 · unpromised_arrival 0 · band_disagreement 0 · scout_vs_assault 0**; shortfall_from_absences 1 (the die: CMD-M t1 Ney→Mack: 58,650 fought against 85,373 expected, Lannes (95%), Murat (76%) did not); promise rate 43/48 = 0.896; bands out-bleed even 1/1, favorable 13/15, unfavorable 0/1. The what-if and the order's muster are one renderer by construction (SR-exit residue Sept 26, pinned there); the scout's garrison is the map's own at FULL (SR-4a). SF-V7 (the Charges forecast one tick low, the LAW arm) is the same family and stays homed at Step 6 — the census does not read the LAW arm and did not trip over it.

## 87. THE SCORE FINISH — STEP 4, SF-CMD-1 "The unrehearsed line", part (i) THE CENSUS (October 3, 2026)

Memo `docs/audits/UNREHEARSED_CENSUS_2026_10_03.md`; rows `BUG_FIXES.md` §SF-CMD-1 census worklist (W1 … W9, OPEN); pins `tests/test_sf_cmd1_the_unrehearsed_census.py`.

### 87.1 The held-out census
`tools/playtest_scripts/unrehearsed_2026_10_03.json` — 150 orders with their intended reading and 150 questions with the answer they need, written BLIND (an author that never saw the corpus, the tests or the docs; only the roster, the map and the verb families) and never edited after the run. `tools/unrehearsed_census.py --blind … --out … [--llm mock|anthropic]` runs each line on a FRESH 1805 boot board through the real `POST /command` (one line, one board — the intended readings are boot-relative) and classifies every reply; `--reclassify <record>` re-reads a stored run with the current judge. Classes for an order: `as_meant`, `asked` (a clarification or an objection — read, not yet done), `board_refusal` (refused by the board with its reason, naming the man or the state order), `honest_refusal` (could not read it, spent nothing — the parser's worklist), `shrug`, `misread` (executed, not what was meant — DANGEROUS), `refused_as_meant`, `executed_when_refusal_meant` (DANGEROUS); for a question: `answered` / `shrug`.

### 87.2 The one judge
`tools/_score_probes.py` holds the judge's regexes as module constants — `ACTION_WORDS` (the words a reply uses when it did the family), `BOARD_GATE_RX`, `ASKED_RX`, `REFUSED_RX`, `SHRUG_RX` — read by the HOLD arm's `command_c3_hold_orders` AND the census runner, never copied (an AST pin). The HOLD rule stands: a board refusal counts as read only when it names the intended marshal (W9 is the consequence).

### 87.3 Measured (per-line, boot board)
Keyless: orders: as meant 53 · asked 28 · board refusal 25 · refused as meant 17 · honest refusal 18 · shrug 9 · **misread 0 · executed-when-refusal-meant 0**; questions: answered 36 · shrug 114. Keyed (26 live parses): orders: as meant 55 · asked 30 · board refusal 27 · refused as meant 17 · honest refusal 20 · shrug 1 · **misread 0 · executed-when-refusal-meant 0**; questions: answered 37 · shrug 113. **Nothing the player did not mean was executed on either arm** (the pin). The keyed arm closed 8 of 9 order shrugs and answered one more question — the desk is deterministic and the model is never asked a question, so the question worklist (W1) is the same on both arms. The spec's "resolution-aware confidence" item did not reproduce (the CX-R1 / CRT-2 guards refuse an unresolved target free); it stays a pin. Part (ii) — the fixes, W1 … W9 — is NEXT and sizes Chunk 3b.

## 88. THE SCORE FINISH — STEP 4, SF-CMD-1 "The unrehearsed line", part (ii) THE FIXES W1 … W9, with CRT-6 / CRT-8 / CRT-9's parts (October 3, 2026)

The blind census (§87) sized nine classes; each is a rule here. Every rule is lever-gated, and the lever's down arm reproduces the measured defect. Pins: `tests/test_sf_cmd1_part_ii_the_fixes.py`. Completion = the census re-run on a FRESH blind file (`tools/playtest_scripts/unrehearsed_2026_10_03_fresh.json`, written by a second blind author; record `docs/audits/unrehearsed/2026_10_03_fresh_keyless.json`): §88.10.

### 88.1 W1 / CRT-9 — the state speaks first: the desk's second table
`backend/ai/state_desk.py` is the question desk's second table, read AFTER every older kind (`classify_board_question` falls through to `classify_state_question`; `answer_board_question` routes `STATE_KINDS` to `answer_state_question`). It classifies by TOPIC WORDS over a normalised line plus the SUBJECTS it can resolve against the rosters the parser already has (our marshals, the foreign commanders it may name, the provinces, the courts and their demonyms, the Marshalate bench — `_bench_names`), never by one anchored regex per sentence, because the completion test is a fresh blind file. One kind per class: money (`net`, `levy_cost`, `commission_cost`/`bench`, `force_limit`, `upkeep`, `bills_moved`, the ledger `component`s, `tribute`), odds (`odds_natural`, `what_if_defence`, `hold_region`, `what_if_march`, `how_long`/`eta`), marshals (`trust`, `morale`, `ability`, `skill`, `relationship`, `marshal_state` — answers the word asked, "No, Sire — …", `anyone_state`, `orders`, `roster`, `strongest`, `closest`, `best_for`, `glory`, `jealous`, `expectation`, `army_total`, `authority`), naval (`fleet`, `foreign_fleet`, `crossing`, `landing_odds`, `build_time`, `closure`), diplomacy (`stance_nation`/`relation` with the intent reading, `coalition`, `alarm_natural`, `peace_forecast` — `calculate_acceptance` on a bare proposal, `vassals`, `vassal_status`, `loyalty`, `war_score`, `weariness_nation` — fogged at `_get_nation_visibility` < PARTIAL, `agenda`, `buyoff_price`, `why_war`, `winning_war`), the `rule` glossary (every verb, building, instrument and system named from its single-source constant where one exists — the AP costs from `strategic_order_ap` and `_action_costs`, the drill gains, the Presence percentage), the map (`terrain`, `adjacent`, `province_count`, `can_build_at`), the `calendar`, last turn (`enemy_moves`, `attacked_us`, `court_news` — the event log through `filter_campaign_log`), the ground (`garrison` through `garrison_view`, `stability`, `income_region`, `buildings` — a foreign province's works at FULL only, `enemy_at`, `enemies_near`, `nation_army`) and counsel (`counsel` = `military_counsel`, `readiness`).
**Fog:** our own marshals omniscient; a foreign commander through `_visible_foe` (PARTIAL for his position, FULL for his stance and works; a prisoner named as one; the last report named when unseen); diplomacy without fog (the standing rule).
**An unknown proper name is never substituted** — only a FACT shape (the five older kinds' regexes, or "is X ours") whose name no roster knows is `unknown_name`: a ONE-name typo within two edits of a roster name is disclosed and re-asked ("(I read 'Jhon' as Archduke John.) …", CQ-30's rule); otherwise the refusal names no marshal, province or court (`_GAME_TERMS` keeps "the Staff", "the Royal Navy", "AP" out of it).
**Three question leads** (`clause_guards.NATURAL_QUESTION_LEADS`): the apostrophe-less contraction ("whats mack doing"), the news lead ("any news from the courts"), and the conditional whose MAIN clause asks ("if Ney attacks Mack, what are his chances" — refused as a contingency before). **A question is never split** (`parser.A_QUESTION_IS_NEVER_SPLIT`: "how do Davout and Bernadotte get on" had been cut at "and Bernadotte"). **A hedge is left to the router** ("perhaps build ships" is a musing about an order). Lever `STATE_DESK_ACTIVE`.
**Measured on the committed census:** questions shrug **114 → 0 of 150**; every W1 answer spends nothing (pinned on the actions, the gold, the points and every marshal's ground).

### 88.2 W2 — the contingency phrasings, in CR-7's own vocabulary
`backend/ai/condition_grammar.py`, four pure readers, each lever-gated: **(a)** `strip_arrival_idiom` — "… and attack Mack when you get there" / "the moment you arrive" / "on arrival" is the ARRIVAL TAIL (CR-7-1 fuses it), not a condition; the idiom is cut at the head of `CommandParser.parse`; the plain movement verbs promote too (`_TACTICAL_MOVE_HEAD_RE`: ride / head / proceed / travel / push / advance to|for). **(b)** `split_premise` + `premise_refusal` — "if Mack is still in Swabia, attack him" is a PREMISE about the present board: read off the sentence (pure), checked ONCE in `main.py` before the parse against what the player can SEE — true, the rest runs now (the pronoun is the premise's man); false, refused free naming where our word places him; unseen, "no word of him — scout first". **(c)** `rewrite_engagement_support` — "once Ney engages Mack, hit his flank" is SUPPORT Ney (the friend must be ours; a flank/rear/join residue). **(d)** `strip_halt_tail` — "head for Swabia but stop if Mack turns on you" marches and keeps the tail WITHOUT a dispatch, saying why on the `warning` seam (`HALT_TAIL_NOTE`: the contact interrupt halts the column and asks). **"attack Mack if he moves" stays refused** — nothing watches an enemy's movement and §4 Stage 2e holds no order for a later turn — and the refusal names the road that does follow him: `'pursue Mack'`.

### 88.3 W3 — the basic forms
`END_TURN_PHRASINGS` widens to "end the turn" and its siblings (my / this turn, finish the turn, pass the turn, end of turn) in BOTH gates (`main.gd::_is_end_turn_phrasing` mirrors the tuple; `END_TURN_LEADING_FILLER` — "just end the turn" — and a trailing please/now are stripped in both); the FA-6 whole-command rule is unchanged (`test_the_fa6_controls_still_hold`). **A negated compound ("don't move anyone, just end the turn") is NOT ended:** the client's lapse-confirm gate reads the raw line and cannot see past the negation, so ending it server-side would advance the turn behind the unanswered-envoys confirm (UX23); the desk says what it heard and asks for the two words (`end_turn_asked`). `Ney, go` is a march with no destination → the movement executor asks where. `could Ney please fortify` is an ORDER (`A_PLEASE_IS_AN_ORDER`: a modal lead + a roster name + please/kindly, no "?"); `can Ney attack Mack` stays a question. `converge on` joins the mock's move list and `STRATEGIC_KEYWORDS["MOVE_TO"]`; a COLLECTIVE address ("Ney, Davout, Soult: everyone converge on Swabia") is FA-50's one-order-at-a-time — the first man takes it and the rest ride the relay as "Davout, Soult: converge on Swabia" (`_split_collective_address`). `keep an eye on` is a scout. `reward <marshal>` is the Reward desk (`_reward_request` → question kind `reward`): the man's expectation and each instrument's terms from the single sources the dialog reads, and the client opens his Reward dialog off `open_reward_for` (`_COMMAND_RESULT_SIMPLE_FIELDS`).

### 88.4 W4 / CRT-8 — the Cabinet's verbs without the address, and its rules
`THE_CABINET_VERBS_NEED_NO_ADDRESS`: a verb of state at the HEAD of the sentence (`_BARE_CABINET_VERB_RE`: propose / offer / negotiate / improve / court / guarantee / sponsor / make friends / seek peace / sue for / form an alliance / send an envoy …) naming a court the parser knows routes to `_parse_diplomatic_command`, unless a marshal is addressed or at the head (CX-R1's rule); `_asks_a_court_for_terms` ("ask Austria for terms") is the Request Terms lifecycle. **RS-7:** `normalize_relation_phrasings` rewrites every way of asking for warmer relations (improve / mend / warm / repair / strengthen our relations|ties|standing; make friends with; seek friendship) to the mission's own phrase. **CQ-36 (§6 row 8 at its default):** a boot bond with no treaty record (France–Spain, France–Bavaria) keeps the Break row DIMMED and its reason is honest — "An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it." — in the preview (`_boot_bond_break_reason`) and in the executor's refusal (the lever to use named). **CX-X3 (§6 row 7 at its default, CRT-8 §8a):** the typed `make_vassal` is gated at the VERB (`VassalExecutor.THE_VASSAL_VERB_IS_GATED`, the player's own orders; never in `create_vassal_conquest`, which the settlement clause and the AI rung call legitimately): at WAR the court must be BEATEN — GEV-1's three proofs through `vassal.subjugation_refusal`; at peace the order is the Cabinet's priced proposal (acceptance plus DP), to which it is routed. "make Bavaria a vassal" / "take Saxony as a vassal" parse (W7c).

### 88.5 W5 / CRT-11's seam — the second name is heard at a comma
`_split_sequential_orders` splits at ", <marshal of ours> <order verb>" as it already split at "and <marshal>" (`THE_SECOND_NAME_IS_HEARD_AT_A_COMMA`); the head keeps its man, the tail rides the relay. In the relayed tail, a pronoun after a SUPPORT verb is OURS — the marshal the last real order addressed (`context_carryover.A_SUPPORTED_PRONOUN_IS_OURS`, `_last_addressed_marshal`), read before the enemy arm that would have handed him Mack.

### 88.6 W6 — the epithets
`parser.rewrite_epithets`: an epithet in ADDRESS position (head + comma) is the man's roster name — the two famous ones (`MARSHAL_EPITHETS`: Iron Marshal → Davout, the Bravest of the Brave → Ney) plus every authored `ability.name` of our own marshals, read off the world at parse time (names only). A title the board does not carry stays refused.

### 88.7 W7 — the adverb and the reason clause (CRT-6's part)
`strategic_parser._clean_target_text` strips a phrasal verb's PARTICLE (down / out / off / away / up / back) — "hunt Mack down" pursued 'Mack Down'. A bare retreat verb with a trailing reason clause is a RETREAT (`parser.A_REASON_TAIL_IS_NOT_A_DESTINATION`: the mock read `retreat`; the strategic table's bare "fall back" had minted a march to the province "- I Don't Like Swabia"); only to/toward/into <place> makes it a march. `rewrite_telegraphic_march`: "<roster name> to <province>" / "Emperor to Rhineland" is "<Name>, move to <province>" — anchored at both ends, nothing else in the sentence.

### 88.8 W8 — the naval phrasings
The mock's posture arm reads `fleet` + home|back beside guard/recall/port/station; `naval._GUARD_NOUN_RE` gains home / back to port / come home and `_POSTURE_VERB_RE` bring / return / come home, so "bring the fleet home" is the guard posture on both halves (they agree by construction, FA-11's rule). The landing verb in the player's words: ship / transport / ferry / carry <corps> to|into|over to <shore>, and "by sea" (`naval_expedition`; "build ships" is the keel branch above it, "ship of the line" has no destination).

### 88.9 W9 / CRT-9 — a board refusal names the man and the order
`economy_executor._msg_treasury(cost, have, who, arm)` and `_msg_pool_short(…, who)` read "Murat's cavalry levy: Berthier shakes his head. 'The treasury cannot support this, Sire. Need 1,504 gold, have 800.'" — the man, the arm, the figures with their commas — at all three sites (the quote, the pool, the chest). The HOLD rule (a board refusal counts as read only when it names the marshal) reads it as the board's. **RS-4 / CQ-28 (CRT-9's backend half):** `strategic.march_state_refusal` gains the FORTIFIED and DRILL-LOCKED arms (`THE_STATE_SPEAKS_FIRST`), and `_execute_strategic_command` refuses the player's own march / pursuit / support to a fortified or drill-locked corps FREE at issuance, naming the remedy ('unfortify' first); HOLD is exempt (a fortified corps may hold where it stands). Scoped to the player's orders: the AI's rungs unfortify before they march (P0) and never drill a corps they then order — recorded so the ambient series stays untouched by construction.

### 88.10 Measured — the completion census
The FRESH blind file (`tools/playtest_scripts/unrehearsed_2026_10_03_fresh.json`, a second blind author; record `docs/audits/unrehearsed/2026_10_03_fresh_keyless.json`, re-read by the shipping judge): **questions answered 149 · shrug 1 of 150; orders: as meant 73 · asked 21 · board refusal 18 · refused as meant 24 · honest refusal 8 · shrug 4 · misread 1 · executed-when-refusal-meant 1 (both recorded designs)**. The first fresh reading was 42 question shrugs and 10 order shrugs; the classes it exposed were taken in-slice (afford / a foe's reach / personality / the fallen / the landing shores / the yards / the treaties / a court's frontier / "is X ours" / the possessive unknown name; "have a look at", "put up a fort", "give X a command", "ashore", "launch the diversion", "hold it", a dash as a clause end, "charge Mack when Ney engages", "hit <foe>", "send X after Y", the typo after an unmarked address, "pledge France to defend X", "work on <court>", "open our borders to"). **Two readings the judge files as dangerous are RECORDED designs**, pinned by name: `Berthier, propose peace to Austria` prepares the proposal (CX-R1 — the desk relays an order of state; the author expected the wrong-desk refusal) and `Davout, fortify Rhineland and hold it until Lannes arrives` takes ONE hold order (FA-50's hold idiom, pinned in the CR-7 family). The judge (`_score_probes.py`) learned the board's own refusal shapes (a foreign commander, a court that is no vassal, a name on no bench, an inland shore, a garrison left where the corps stands, an enemy named as a friend, an unknown target); the committed records re-read unchanged. The HOLD arm's six first-contact shrugs were taken too (`who_is`, `wars_leader`, `safe_natural`, `what_is_in`, `goal`, the epithet in a question).

## 89. THE SCORE FINISH — STEP 4, Chunk 3b trimmed to what the census confirms: CRT-11 · RS-11 · CRT-9's client half · CRT-10 led by SF-V4 · SF-V8 (October 3, 2026)

The blind census (§87, §88.10) sized Chunk 3b; the user trimmed it to the five things the census confirms. Each rule is lever-gated, and the lever's down arm reproduces the measured defect. Pins: `tests/test_crt11_the_second_name_is_heard.py`, `tests/test_rs11_take_and_sf_v8_the_named_corps.py`, `tests/test_crt9_the_state_speaks_first.py`, `tests/test_crt10_the_suggestion_is_honest.py`, plus the re-seated CX-R2 and CN-4 censuses; 18 corpus rows (`crt11-*`, `rs8-*`, `rs11-*`, `sfv4-*`, `sfv8-*`). The rows the census did not confirm are re-measured and homed in §89.7.

### 89.1 CRT-11 — a second name is a role, never a second order (RS-6, the HOLD arm's blind line)
`backend/ai/second_name.py`, `rewrite_support_role(text, friendly_names)`, runs at the head of `CommandParser.parse` beside W2's `rewrite_engagement_support`, BEFORE any reader sees the line, so the fast parser, the strategic layer, the word scan and the sequential split agree by construction. Four shapes, each restated as `<address>, support <Name>`: *(march / move / ride / come … / bring up your corps) in support of — to the aid, relief, rescue, assistance, succour of <ours>*; *to <ours>'s support / aid / side / help*; *follow <ours> (in / up / closely / into battle) (and back / support / cover / join … him / <ours> (up))*; *back <ours> up*. The movement lead is consumed with the phrase (left behind, "march" would claim the line as a MOVE_TO again); whatever follows is kept ("… until the battle is won", a second clause). **Only a marshal of OURS is restated** — "the aid of Mack" names no order the engine has. The typed text stays the record (`raw_input` / `original_command`). Readers: `strategic_parser._friendly_head` skips a leading "of"; `context_carryover.A_SAME_CLAUSE_FRIEND_IS_HIM` reads "him" in the same clause as the man that clause named, ahead of W5's last-addressed rule ("Lannes, follow Ney in and support him" supports Ney, not Lannes). A support order costs one action (SR-2e). Lever `THE_SUPPORT_ROLE_IS_HEARD`.

### 89.2 RS-8 — the destroy clause is heard
ONE alternation: `attack_vocabulary.ARRIVAL_TAIL_VERBS` (the battle verbs and the capture verbs) feeds the five readers of a march's tail — the parser's two arrival-tail patterns, the strategic parser's hint and arrival-object patterns, the condition grammar's arrival tail — each built by `levered_arrival_pattern`, which compiles the wide and the narrow (attack / engage / assault) forms and picks one at call time (`LeveredPattern`). The order-verb split lists gain `SECOND_ORDER_BATTLE_VERBS` (destroy / crush / smash / annihilate / obliterate / rout), so a head that cannot carry an arrival keeps its own order and relays the tail (CR-7-1's rule: "Ney, fortify and destroy Mack" had FOUGHT with the fortify swallowed). `strategic_parser._clean_target_text` strips a leading "against" ("march against Mack" was a march to the province "Against Mack"). Lever `attack_vocabulary.THE_DESTROY_CLAUSE_IS_HEARD`. **The P4 rider:** an EXPLICIT order's bad-odds interrupt names the muster as the inferred order's always has (`strategic.THE_EXPLICIT_INTERRUPT_NAMES_THE_MUSTER` — the first step in `strategic_executor`, the per-turn arrival and mid-path checks in `strategic.py`, all reading `_bad_odds_muster_note`): the interrupt had quoted Ney's 24,000 alone while the battle it would start drew 85,000 against Mack's 52,000. The marshal's own read stays solo.

### 89.3 RS-11 — "take <province>" is an objective
`parser.rewrite_take_objective(command_text, game_state, world)` (lever `TAKE_IS_AN_OBJECTIVE`), before the fast parser. "take" stays out of the parse-seam verb set (`attack_vocabulary`'s pinned exclusion: "take care of X", "what would it take"); the rule reads only an object the board knows. **A foe at war** → `attack <him>` (out of range, the attack road's own pursuit upgrade carries him). **A court** → the capture road's own answer ("… is a nation, not a province"). **A hostile province** (held by a court at war with us, or a foe we can see stands on it) **in the named marshal's reach** → `capture <it>`, the capture verbs' attack road and its muster; **beyond his reach** → `march to <it> and attack`, a standing march with the attack on arrival whose road the march law reads at issuance (CRT-4) and refuses free when there is none. **Any other province** → `march to <it>`. **No marshal named** → the man in reach takes it (S5-D1's pick), else the man with the shortest LAWFUL road, `strategic.nearest_lawful_marcher(world, dest)` (reads `march_road` for every field marshal standing, ties in roster order), named in the reply: *"Bernadotte has the shortest open road to Vienna, Sire (2 marches)."*; with no lawful road anywhere the line is left to the first-contact desk, which answers with the march law's own refusal (*"… Cannot enter Berlin, Sire — it is controlled by Prussia (diplomatic state: PEACE) …"*). An unknown addressee keeps CX-R1's refusal ("There is no Marshal 'Zorglub' …"); the epithets resolve (W6). Pinned exclusions: "take care of", "take the field", "what would it take".

### 89.4 CRT-9's client half — the screen reads the state (CQ-21, CQ-24)
`backend/commands/state_probe.py`: ONE pure probe, `order_state_refusal(world, marshal, verb)`, answers "would this order be refused for the marshal's STATE or for the action it costs?" in the order the executor meets its gates — the action pre-gate (a free retreat or wait; the counter-punch's waiver; a standing order priced by `strategic_order_ap(order_type=…)`, a tactical one by `get_action_cost`), the occupation lock, then the standing-order road's state arms (`march_state_refusal`'s family) or the pre-objection battery's (autonomous; drill-locked; fortified for an attack or a move; `defend_refusal`; wounded; recovering; broken; the sovereign skips the battery as the executor does), then the verb's own predicate (`drill_refusal`, `fortify_refusal`, `unfortify_refusal`). It reads the executor's fields with the executor's rules and writes nothing. **The payload:** `tactical_state.order_refusals` for every PLAYER marshal on the map summary, the same map on the Generals cards (`marshal_overview._order_refusals_of`), the turn's `action_pools` (`{"military", "admin"}`, on the summary and `/marshal_overview`), and each THE ADMIRALTY landing row's `refusal` (verb `land`). **The screens:** the region panel and the Generals screen dim each order chip with its short reason (`_dimmed_chips` groups the reasons); at zero administrative actions every build / repair / war-damage / keel / watchtower / naval-yard chip dims (`_admin_why`, off `action_pools`); the landing chip dims on the row's refusal; the command-line completer hides a line the state refuses (`main.gd::_state_open` through the `_STATE_PROBE_VERB` map, the continuation heads too — a refused `move to` falls back to `march to`). Player marshals only (the AI never reads a chip). Lever `THE_SCREEN_READS_THE_STATE` (False ships an empty map; the screens fall back to their own per-verb fields). **The driven census:** all twelve verbs for each of ten staged states (fresh, fortified, drill-locked, recovering from a retreat, broken, autonomous, no military action left, one left, no administrative action left, the counter-punch at zero) through `POST /command` — the probe refuses exactly what the executor refuses; CX-R2's board census runs with its `_state_gated` exemption DELETED; CN-4's chip census runs at zero actions on both surfaces. Parse harness EXIT=0 (62 scripts, 9 scenes); boot smoke 0 `SCRIPT ERROR`.

### 89.5 CRT-10 led by SF-V4 — a proper name asks (`SCORE_FINISH_SPEC.md` §6.3)
`backend/commands/proper_name.py` (lever `A_PROPER_NAME_ASKS`). **The grammar** (`proper_name_in(tail, world, viewer)`, pure): the words after the attack verb, up to the first comma, conjunction, preposition or clause word, hold a PROPER NAME when they do not open with a determiner, possessive or quantifier; when, after filler and generic words, a word is left that is no military noun, no -ly adverb and — written lower-case — no description (a participle, a superlative); and when that word resolves to no commander on any roster, no province, nation, demonym or prisoner (a province TYPO resolves: "Swabbia" still corrects; a title word — "archduke" — never resolves a name alone). **The dispatch seam** (`executor.py`, ahead of the objection gate and CR-6's bare-attack pick; the player's typed road only — the AI, strategic execution, an autonomous attack, a re-issued muster and a standing march's tail never reach it) answers, spending nothing: **the ask** — *"No foe called Zorglub is in sight, Sire. The nearest in sight is Mack at Swabia — shall Ney engage him?"*, the foes in sight (PARTIAL or better, at war) offered nearest first (yes / "attack him" / 1 / 2 … / cancel answer it; `clarification.build_proper_name_clarification`); **a near miss** (one slip; a transposition counts) — *"… did you mean Mack at Swabia?"*; **a fallen general** whose death was in view at its province — *"Archduke John fell at Tyrol on turn N, Sire — his corps is no more."* and the ask (NPC-6); an unseen death gets the plain ask; **a name on an enemy bench** — *"No intelligence on Paget's position, Sire. Scout for him before Soult can give chase."*, the same words before and after his commission (a commission never leaks); **nothing in sight** — *"No foe called Zorglub is in sight, Sire, nor any other — Ney will not charge at a guess."* The bare road (`attack Zorglub`) asks for the TARGET, never the marshal: a word in the OBJECT position of an attack verb is never read as an addressee (`parser._OBJECT_OF_ATTACK_RE`). **A march's arrival tail** naming an unknown proper name keeps the march and arms no attack, and the reply says so (`strategic_parser` → `arrival_object_note`, restated by the executor on the first step's interrupt). **A description keeps PS18-R1's disclosed substitution** ("smash the retreating column").

### 89.6 SF-V8 — a routed order word is never a name
`parser.A_ROUTED_WORD_IS_NEVER_A_NAME`: the parser's word scan skips a word of the generated CX-R1 verb set (`routed_order_words.ROUTED_ORDER_WORDS`) unless it IS a roster name. "land" had fuzzy-matched "Lannes" (partial ratio 75, over the 70 a four-letter word needs), so `land Oudinot in Munster` answered for Lannes four turns running on the baseline's descent arm; it now answers the unknown-name refusal at 0 cost, and `land Soult in Munster` prices Soult.

### 89.7 The rows the census did not confirm — re-measured, homed
Re-measured at the exit on a fresh boot through `POST /command`, with the same probe on a detached worktree at `e631f4bd` so every change is attributed. **CX5-L5-N2 is closed** — fixed by SF-CMD-1 part (ii) W7 and attributed with its lever (`A_REASON_TAIL_IS_NOT_A_DESTINATION` down reproduces "Region 'Now' not found."). The rest stand and are homed to Step 7's **SF-CMD-2 "the census's remainder"** with their done-whens: CQ-8, CQ-38 (CRT-11); CQ-33, CX5-L5-F3 … F7, N4, N5 (CRT-6); RS-12, RS-15 (CRT-9's desk half — the probe of §89.4 is now its seam); CX3-X2, CX3-X3, PC15-13 and CX-BEHAV-1's census re-key (CRT-10; its player-facing half was done since); NP-X1, NP-X8, NP-X9, NP-X10, NPC-9, NPC-10, NPC-18, NPC-26 (the parser riders); and SF-V9's HOLD worklist (§89.8). **Four of them still carry out an order the player did not give**, and SF-CMD-2 opens with them: CQ-33 (`with the Guard` → a 2-action HOLD), CX5-L5-F7 (`Ney, protect the rear` → a 2-action HOLD and a march), NPC-9 (`I will march to Lorraine myself and attack Mack` → a march to "Lorraine Myself", 1 action) and NP-X1 (the same phantom target on a board with no Emperor). Step 4's exit also owed two doctrine rows: **SR-7d-X2's T5 is measured** (§89.8); T9, T10 and SR-7d-X1 are homed to Step 7's **SF-DC-1 "Nothing unnamed"**. SF-CL-1-D1 (where the coordination is read) is put to the user as `SCORE_FINISH_SPEC.md` §6 row 16.

### 89.8 Measured at the exit
- **The instrument** (`tools/score_run.py` over the eight touched arms FC / OP / DL / HOLD / DESC / CMD-H / CMD-A / CMD-M, on this tree and on `e631f4bd` in a detached worktree): **one item flips, command C4 ✗ → ✓** ("all docked command lines execute or ask": RS-6, RS-8, RS-11 and SF-V4's lines on the DL arm); no other item moves between the two trees. Two instrument corrections, each pinned: C4's SF-V4 reading counts a battle as a substitution only when it comes BEFORE the player's answer to the question (the driver answers the clarification by its dial — `TestTheInstrumentReadsTheAnswer`), and the ONE judge reads the march law's engaged refusal as the board's (`… cannot begin a strategic march`; no committed census record carries it, so the pinned census counts stand). HOLD orders as meant 9 of 20 (8 at `e631f4bd`); questions shrugged 0 of 20.
- **T5 (`DOCTRINES_SPEC.md` §6), the road to 45 re-measured after the doctrines:** the three roads on this tree with the doctrines up and with `DOCTRINES_ACTIVE` down — the AAR road 32 / 31 / 31 / 23 against 36 / 36 / 36 / 36; opening A 35 / 35 / 35 / 35 (36 at turn 41) against 21 / 23 / 23 / 21; opening B 25 / 14 / 15 / 11 against 37 / 37 / 35 / 35 (turns 10 / 20 / 30 / 40). The best point falls from 37 (opening B, doctrines down) to 36 (opening A at turn 41; 35 through turns 10–40) — within the two provinces T5 allows, **a pass** (pinned: `tests/test_sr7d_the_doctrines.py::TestT5TheRoadToFortyFiveAfterTheDoctrines`); the doctrines re-rank the roads (A rises fourteen; the two unattended tails erode harder). Archives `docs/audits/playtest_digests/sf4-q0-*`.
- **Gates:** `BASELINE_SERIES` and M1–M7 byte-identical (the AI parses no text and never reads a chip; the probe writes nothing; the muster note is copy). Corpus 866 of 866 keyless.

## 90. THE SCORE FINISH — STEP 5, SR-8a VD-C "The Contingent" with IQ7-X1 · IQ7-X2 · IQ7-X3 (October 3, 2026)

A loyal satellite is FOR men. In a war it shares with its lord it raises a contingent scaled by its income and its loyalty; the contingent fights under its lord's flag, the satellite pays its men and grieves its dead, and when the shared war ends it marches home — crowned, decimated or merely home — and stands down. On a break it walks out of the lord's lines with its men. Gate record `VASSAL_DEEPENING_SPEC.md` §9.1 (R1–R12, the numbers in-band tunable), landing record §9.2. Every rule keys off the vassal row and the shared war, for every lord (GR5). Pins `tests/test_vassal_contingent.py`; sweep `tools/_sweep_step5.json`.

### 90.1 The call and the size
`contingent.process_vassal_contingents(world)` runs once a turn in `process_diplomacy_turn`, after the loyalty tick (which has already charged the contingent's dead) and before the rebellion check (a break walks it out at its own hook). A satellite raises when it is LOYAL (`vassal_military_contribution == "loyal"`, VS-4's ≥ 60), when its lord and it are at war with the same court (`shared_enemies`), when it is not resting (`contingent_rest_until` on the vassal row, written by a homecoming or a loss), when its lord fields no assimilated corps of its colours already, and when it has no contingent serving. **The size** (`contingent_size`): `income × 15 × loyalty // 100`, rounded down to 500, capped at 12,000 and at the satellite's infantry pool, and nothing below 3,000 — the income is the satellite's authored province income (`Region.income_value`). Boot: Holland 6,500, the Kingdom of Italy 7,500, Switzerland 4,500. **The commander** (`pick_commander`): the first of the scenario's authored `contingents` who is not serving, fallen or on any bench; past the list, "<Adjective> Contingent" with a numeral when the name is taken. `raise_contingent` mints him with the commissioning idiom (`create_marshal_from_data`) on the LORD's flag with `original_nation` set to the satellite, at the satellite's muster province (`recruitment.find_spawn_region`), debits the satellite's infantry pool and refreshes his doctrine terms. **No march is issued** (R10): he awaits the lord's orders; the beat names the nearest host (the lord's nearest standing field marshal by road). Lever `THE_CLIENT_SENDS_ITS_CONTINGENT` (False raises nothing; a record already on the board is still honoured).

### 90.2 The client pays its men
`calculate_turn_upkeep` skips the lord's serving contingents (`contingent.client_paid_names`) — no upkeep, and the total it returns (the force limit, the levy and the Grande Armée all read it) does not count them. Lever `THE_CLIENT_PAYS_ITS_MEN`. A satellite's own men in their own capital are not the lord's garrison: `vassal.lord_garrison_present` skips a marshal whose `original_nation` is the capital's controller (`A_CLIENTS_OWN_MEN_ARE_NOT_THE_LORDS_GARRISON`).

### 90.3 The dead, and the men kept from home
`process_vassal_loyalty` step 5b: `contingent_dead_tick` reads the fall in the contingent's strength since the last tick (all of it if the corps is gone or taken; a corps under another flag counts nothing) and records today's figure; the contribution is `−min(10, dead // 500)` — "the contingent's dead". While the record is homeward and the lord holds the corps with an order of his own (`contingent_kept_from_home`), −2 a turn — "its men kept from home". Both are 0 with no contingent serving, so a satellite with none ticks byte-identically.

### 90.4 The road home and the homecoming
When no shared war stands the record turns `homeward`: a free 0-AP MOVE_TO toward the satellite's muster province, without `issued_turn` (the WIN-D3 idiom, so the first step is walked), its `original_command` the contingent's own (`CONTINGENT_HOME_COMMAND` — the AI's P1.2 rung walks it with `contingent_next_step`, and the kept-from-home read tells it from an order the lord gave). A lost road is given again; a new shared war returns it to service; eight turns on the road and it stands down where it is ("by its own roads"). **On its own soil it stands down** (`stand_down`): the survivors go back to the satellite's infantry pool (any beyond the raised strength to the lord's), the marshal is removed by `WorldState.stand_down_marshal` — the one removal that is not a fall: no tombstone, no `marshal_destroyed` row, his reward rows and standing question dismissed; it refuses a prisoner and the sovereign — and the homecoming is judged: **crowned** (+8) for at least one victory since the raise and at least half the men home, **decimated** (−5) for fewer than half, otherwise plainly home; then six turns' rest. **Destroyed or taken in the field** (`lose_contingent`): decimated (−5) and rest.

### 90.5 The exits
`release_vassal` → `on_release` (a voluntary release recalls it — it stands down at once; a rebellion release walks it out); `transfer_vassal` → `on_transfer` (recalled: the men were lent to the old lord, never the new — read before the re-key loop); `complete_vassal_break` and `_eliminate_nation`'s freed-satellite loop → `on_break` (walks out: the record closes and the break's own hand-back loop puts the marshal under his own flag). Each hook is read BEFORE the mutation it precedes (Golden Rule 4). An exit nobody named is reconciled by the next pass: the record's corps still on the lord's flag stands down, one under the satellite's walks out, anything else is lost.

### 90.6 The surfaces
ONE beat shape (`contingent._beat`) for raised / marching_home / home / lost / walked_out: a `vassal_contingent` campaign-log row (171 → 172 types; category diplomacy; notable tier; fog: the player's own satellites always, a rival's at PARTIAL+), an end-turn event and a dispatch line (`diplomatic_vassal_contingent`, MEDIUM; `always` for the player's own satellites, `partial_on_nation` for a rival's). The raise line names the men, the payer and the host: *"Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief."*

### 90.7 The regiments clause comes true
The contingent's marshal carries `original_nation` = the satellite — the assimilated-corps marker VS-4 Rule 1b and IQ-7 R1 read — so a wavering satellite's contingent holds back from its lord's musters and reinforcements exactly as the tier line says, and `lord_fields_the_vassals_regiments` reads true for the boot satellites from turn 3 (it was never true on the 1805 board before: they fielded no marshal).

### 90.7a R12 — the client's general is not the Emperor's marshal
`contingent.is_clients_general(marshal)` — `original_nation` set to a court other than his flag's (a contingent, or a VS-4 assimilated corps) and the lever `A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL` up — is the ONE predicate: `jealousy.get_nation_ladder` gives such a corps no rung (so no crown), `jealousy.find_jealousy_target` returns None for it and never offers it as a target, and `dotation.get_expectation` returns 0 for it (the NP-0 sovereign cascade: no shortfall, erosion, Unmet line, collective or war-weary petition), with `expectation_rise_blocked` saying why ("his own court rewards him"). Its glory events still accrue (display only). It fights, obeys, musters and reinforces as any corps does.

### 90.8 IQ7-X1 — every lord's satellites are courted and cascade (GR5)
`attempt_vassal_courting` and `check_defection_cascade` walk every lord's satellites, not the player's alone (`THREATS_WALK_EVERY_LORD`). A lord never courts its own satellite; the courting's unlock and effectiveness read the satellite's OWN lord's grip (memoized per lord); the "detected courting" notification and the 60% dispatch roll fire only for the player's own satellites (a rival's courting draws no module-RNG roll); the cascade's dispatch line fires only when the player's own web broke. Each courting event names its `lord`.

### 90.9 IQ7-X3 — the recovery hint rides the turn of the trend
The recovery hint on a falling `vassal_loyalty` event is shown on the first fall after a tick that did not fall and on every FA-S17-D8 crossing tick (the 60 line) — never on every falling tick. The memory is `world.vassal_hint_spent` (the satellites whose hint is spent for the current downturn), re-armed by any tick that does not fall (a rise or a standstill), kept off the vassal row (VS-R Q6). Lever `THE_HINT_RIDES_THE_TURN`. Measured on the final tree's commanded arm: 11 / 8 / 6 hinted lines against 14 / 17 / 16 with the lever down, the board identical.

### 90.10 IQ7-X2 — the dead code is gone
`vassal.get_vassal_warnings` and `notifications.VASSAL_LOYALTY_CRITICAL` are deleted with the tests that imported them; `RAIL_EXEMPT_TYPES` is empty again (pinned by absence).

### 90.11 SF5-X1 / SF5-X2 — the typed interrupt route's two guards (found in passing)
`main.py`'s typed interrupt route (`PENDING STRATEGIC INTERRUPT CHECK`) runs before every other reader of the line. **A question never answers an interrupt** (`A_QUESTION_NEVER_ANSWERS_AN_INTERRUPT`): a question-shaped line (`dialogue_routing.line_asks_a_question`) that names one of the interrupt's own answers orders nothing — the response restates the interrupt's question with its answers, labelled as the popup labels them (`_INTERRUPT_OPTION_LABELS`, drift-pinned against `interrupt_popup.gd`), and re-carries `pending_interrupt` so the popup stands again; a question naming none of them goes on to the desk; an exact option id still answers. **A standing hard stop outranks the route** (`A_HARD_STOP_OUTRANKS_AN_INTERRUPT`): while one stands, the line falls through to the hard-stop gate, which names its own question, and the interrupt waits. Measured before: "should we attack?" FOUGHT Ney's bad-odds battle against Mack, and under the war-purpose question an "attack anyway" was refused downstream and the refusal destroyed the interrupt and Ney's standing order. Pins `tests/test_sf5_the_question_and_the_interrupt.py`.

### 90.12 The Step 5 quick check (October 4, 2026 — SF5-RV1 … SF5-RV12)
Two read-only reviewers attacked Step 5 at `fe720296`; twelve findings were reproduced and fixed, each behind its own lever (`BUG_FIXES.md` §Score Finish Step 5 quick check; pins `tests/test_sf5_quick_check_2026_10_04.py`; `BASELINE_SERIES` and M1–M7 byte-identical). **The lord does not fill the client's ranks** (`contingent.THE_LORD_DOES_NOT_FILL_THE_CLIENTS_RANKS`): ONE predicate, `contingent.lord_fill_refusal` / `levy_passes_over` — a named levy or substitutes into a serving contingent is refused free in its satellite's name; the levy's own selectors (`WorldState.ready_marshals_near(for_levy=True)`, `find_nearest_marshal_to_region(for_levy=True)`, the quote core, the no-recipient refusal, the capital branch, the levy status and the map payload) pass him over with the reason named, while the combat auto-pick keeps him (a contingent fights under its lord's orders); the substitute market never names him; the AI's `_find_weakest_marshal_for_admin` skips him (GR5). **A renewed war recalls the colours** (`THE_RENEWED_WAR_RECALLS_THE_COLOURS`): when the shared war resumes during the walk home, the satellite's own home order is withdrawn with the `back_to_the_colours` beat; an order the lord gave stands. **The raise beat keeps the fog** (`THE_RAISE_BEAT_KEEPS_THE_FOG`): the nearest host is named only for the player's own lord or where the player sees it at PARTIAL+. **An override keeps them from home** (`THE_OVERRIDE_KEEPS_THEM_FROM_HOME`): the executor's strategic override stamps a homeward contingent's record (`note_lord_override`, `kept_turn`) and the next loyalty tick charges the −2 once while the road stays cancelled; a refused override restores the home order (SR5B-1) and costs nothing. **A fallen crown disbands its men** (`THE_FALLEN_CROWN_DISBANDS_ITS_MEN`): a contingent whose satellite holds no province disbands (`contingent.disband` — no pool credit, no tombstone, no homecoming judged). **An order aimed at a general who stands down ends with him** (`WorldState.stand_down_marshal`, the elimination idiom). **The popup button waits on a hard stop**: `POST /strategic_response` reads `A_HARD_STOP_OUTRANKS_AN_INTERRUPT` like the typed route — nothing relayed, the waiting dialogue and its answers named, the interrupt kept. **No client's general is jealous**: the jealousy trigger loop and the restlessness warning skip `contingent.is_clients_general` outright (the literal branch's fallback to the ladder's top had bypassed R12). **The question re-prompt consumes nothing** (`main.A_QUESTION_REPROMPT_CONSUMES_NOTHING`): it rides the non-draining refusal builder with the interrupt passed in, so the FA-49 option costs are stamped and no queued popup is lost, and a CR-7 relayed tail waiting behind the interrupt is put back. **A satellite courts as its lord** (`vassal.A_SATELLITE_COURTS_AS_ITS_LORD`): `courtier_is_the_lords_ally` also spares a target whose lord is the courtier's lord's ally (the same-house case stays the courting cap's guard). **The hint memory follows the row** (`vassal.THE_HINT_MEMORY_FOLLOWS_THE_ROW`): the loyalty pass drops the spent mark of any court that is no satellite and `transfer_vassal` re-arms it. **The cascade line keeps the fog** (`vassal.THE_CASCADE_LINE_KEEPS_THE_FOG`): the `vassal_defection_cascade` event carries its lord and the satellite's capital for the end-turn fog filter, and speaks display names. Open: SF5-RV13 (an emphatic order with a rhetorical tail reads as a question) → Step 7's SF-CMD-2.

## 91. THE SCORE FINISH — STEP 5, SR-8b + SF-AGD-1 "The agendas arm" and SR-8c "the deck review" (October 3, 2026)

### 91.1 The played road
A carve through the settlement path to the Proclamation, played on a road the driver drives, with the formables gate flipping in play. **The board** (`tests/fixtures/playtest_saves/fixture_agd_tilsit.json`, regenerated by `tools/gen_agd_fixture.py`): SF-M's TILSIT board with one difference — Posen is still Prussian and Davout stands beside it in Silesia; Prussia's field army destroyed, Berlin and Silesia French, France at war with Prussia and Britain only (Tilsit's own shape: the Duchy of Warsaw was carved while Britain's war ran), every other war ended through the engine's own pair resolution with the settlement's truce floor. **The arm** (`tools/playtest_scripts/sf_agd1_tilsit_road.json`, arm `AGD` in `score_run.ARMS`, 3 turns, `--diplomacy accept`, saves each turn): loop 1 takes Posen (the Duchy's gate term "Posen held at the settlement table" flips to met); loop 2 opens the table with the typed opener the war panel sends, adds the carve and a 6,000-gold indemnity offer with the table's own guided rows, submits it for review and takes "Make peace with Prussia only" (the joint table covers the whole coalition war and cannot be sealed; the carve rides the separate peace — IGR-D's Tilsit road); Prussia accepts at the end turn and the Proclamation card fires (SF-M's probe on the same board: the bare carve COUNTERs at 30, the carve with 6,000 gold is ACCEPTed at 90).

### 91.2 The driver's click grammar
A script line beginning with `@` answers the dialogue on the desk with that action and its JSON `action_params`, posted to `POST /respond_to_diplomatic_dialogue` exactly as the client posts it (`Answerer.script_click`). While the NEXT script line is a click, the dialogue a line opened is HELD — said in the digest, never policy-answered (`Answerer.hold_dialogue` / `held_dialogue`). The digest records what a settlement table states (`settlement_terms` rows: every clause, the client a carve erects and the provinces it takes, the gold) before it is answered (`THE_DIGEST_STATES_THE_TERMS`).

### 91.3 The reader
Agendas **C5** ("on SF-AGD-1's arm, a carve states its terms and the Proclamation card fires") reads the `settlement_terms` records, the `nation_proclamation` popups and the gate-flip evidence (`_score_probes.agd_gate_flip`: the Duchy's gate terms on the fixture against the arm's first save). **Instrument correction** (C3 and C5 alike): a province-held gate term carries its holder while unmet — "… (currently Prussia-held)" — and drops it when met, so a reader keyed on the raw text could never see it flip; both key on `_gate_term_key` (the text without its "(currently …)" tail). Pins `tests/test_sf_agd1_the_agendas_arm.py`.

### 91.4 SR-8c — the deck review
**IQ6-D2, as ruled (§6 row 12): a client's partition is the hegemon's act.** The volte-face's NOT-HUMILIATED clause reads a punitive memory — and an emergent revanche — authored by ANY member of the hegemon's bloc, the bloc its BEATEN clause already reads (`emergent_designs.A_CLIENTS_PARTITION_IS_THE_HEGEMONS`). A partition by a court outside the bloc stays that court's quarrel. **IQ7-D3:** Holland's deck gains `ostfriesland` [East Frisia] (gate record `VASSAL_DEEPENING_SPEC.md` §9.1 R11) — non-capital, never French homeland, Hanover-held at boot, contiguous to Friesland — so a lord who takes it can grant it (VS-3) and the client's petition names it as its design (`in_design`); appended, so NA-6's post-formation goal stays deck index 1. **AI-V §7a scene 1, the Confederation of the Rhine — recorded UNREACHABLE BY DESIGN** (`AI_INTENT_SPEC.md` §7a): its 1805 half is the boot state (Bavaria's Bogenhausen alliance, authored as ALLIANCE), its 1806 half was Napoleon's act (the Treaty of Paris of 12 July 1806) — in this game the player's, through the vassalage road — and the German minors carry no deck, so their intent reads no want; authoring them a covet design would make a minor an asker refused by stronger courts, never the scene. Pins `tests/test_sr8c_the_deck_review.py`.

## 92. THE SCORE FINISH — STEP 6, SF-NAV-1 "The strangulation, played" with SF-V6 · SF-V7 · SF6-X1 (October 4, 2026)

### 92.1 The arm and its probe
`tools/playtest_scripts/sf_nav1_strangulation.json` (benchmark `NAV1-H/A/M`, 30 turns, a save every turn, `--decline-from Britain,Portugal,PapalStates,Naples`) plays the Continental System: France keeps its war with Britain alone, takes Lisbon, Rome and Naples, holds the Normandy beach and hunts every British corps that lands. `tools/sf_nav1_strangulation_probe.py` (read-only) reads each save through the Congress's own `_shut_out_reading` and `corps_on_the_continent`, and Britain's envoys off the digest. No checklist item reads it (v1 is frozen); `docs/audits/SF_NAV1_STRANGULATION_2026_10_04.md` is its record and `SCORE_FINISH_SPEC.md` §6 row 17 its open question (the A2 anchor).

### 92.2 SF6-X1 — sailing ends the standing order
A CONFIRMED `naval_expedition` (landed, intercepted or turned back) ends the corps' standing strategic order — HOLD state and the interrupts it raised included (`naval_executor.SAILING_ENDS_THE_STANDING_ORDER`). The quote (the unconfirmed order) touches nothing. GR5: the AI's expeditions ride the same executor (reach on the series board: 2 AI sailings in 40 turns, neither under a standing order).

### 92.3 SF-V7 — the driver records the applied bill
The playtest driver writes one `applied_bill` row per ended turn (`turn`, `charges`, `laws`, `materiel`) off the `turn_end` event both end-turn producers stamp (`playtest_driver.THE_DIGEST_RECORDS_THE_APPLIED_BILL`). The `economy` row written after an end turn is a `/ledger` forward projection — the NEXT turn's quote — and is never the bill; economy C3 (`_score_probes.economy_c3_quote_equals_applied`) holds the saved quote against the applied bill of the same turn. The bill is drawn on the same pre-income chest the quote reads, so they agree to the gold — except for the end turn's own battles: the enemy phase fights before the income phase draws the bill, and its Butcher's Bill (the record's `materiel`) and its dead (the pensions term) move the bill after the quote was read. `economy_c3_verdict` counts such a turn as explained and passes only when every battle-free turn bills its quote to the gold.

### 92.4 SF-V6 — the descent arm stages its landing
`tools/playtest_scripts/naval_descent.json` spends no gold before its loop-4 commission, marches Oudinot to the Normandy yard the loop he is raised and sails on loop 5; naval C3's reader (`score_run.r_naval_C3`) counts the capture question (`capture_choice[capture]: Munster`) as the province falling. The SEA arm (`sr_exit_chunk5_sea.json`) marches Oudinot to the Normandy yard the loop after his commission (SF6-X2): the Bordelais road crossed Britain's Peninsula corps once the board drifted.

## 93. THE SCORE FINISH — STEP 7, "What the wire says, the screen says" (October 4, 2026 — in progress)

### 93.1 §6 row 17's research and two driver dials
- **`policy_at` (the script's own dials, by loop).** A script may carry `"policy_at": {"<loop>": {<policy key>: <value>}}`; from that loop on the driver's policy takes the new value (the answerer holds the same dict) and the digest notes `POLICY <key> -> <value>`. Used by the Danube conquest draft to refuse Austria's peace until loop 9. A script without the key is byte-identical.
- **SF7-X1 — the decline list reads the stored shape** (`playtest_driver.THE_DECLINE_LIST_READS_THE_STORED_SHAPE`). `_court_of` reads `context.source_nation` (stamped only by the AI's envoy producers) and, on an `incoming_proposal`, `target_nation` — the STORED dialogue a stale answer's refusal re-carries. The player's own confirms (whose `target_nation` is the court France writes TO) are never read as an envoy's court.
- **The conquest road** — `tools/playtest_scripts/sf_nav1_conquest_danube.json` (Vienna first) and `sf_nav1_conquest_road.json` (the Step 6 arm plus Hanover) — is research, not benchmark: read with `tools/sf_nav1_strangulation_probe.py`, archived under `docs/audits/playtest_digests/sfnav1d1-*`, recorded in `docs/audits/SF_NAV1_D1_THE_A2_ANCHOR_2026_10_04.md`. The ruling it informed is `SCORE_FINISH_SPEC.md` §6.6 (the Tilsit clause; built in Step 7's row-17 slice).

### 93.2 SF-CMD-2's head — the four misreads that still executed, and the emphatic order
- **The Guard marches with the Emperor** (CQ-33; `parser.rewrite_guard_company`, lever `THE_GUARD_MARCHES_WITH_THE_EMPEROR`). Before any reader, "with / alongside / beside / together with the (Imperial / Old / Young) Guard" is taken out of the line and the sentence's own verb runs; an addressee who is not the Emperor gets the note "The Guard marches with the Emperor alone, Sire — <marshal> goes with his own corps." on the warning seam. "for the Guard" on a levy verb (recruit / raise / levy / enlist / conscript / draft) becomes "with <the Emperor>" — the Guard is his corps. The verb "guard" ("Ney, guard Paris", "guard home waters") is untouched. The typed line stays the record (`raw_input` / `raw_command`).
- **A reflexive is never a place** (NPC-9 / NP-X1; `parser.strip_self_markers`, lever `A_REFLEXIVE_IS_NEVER_A_PLACE`). The self-marker ("myself", "by myself", "in person") is read anywhere in the line, not only at its end: the sovereign normaliser strips every occurrence before its arms (so a mid-sentence marker still addresses the Emperor), and after the normaliser the marker is stripped on EVERY board — with no Emperor, the first person is nobody's and the ordinary marshal question follows.
- **A position is not a place** (CX5-L5-F7; `strategic_parser._POSITION_NOUN_RE`, lever `A_POSITION_IS_NOT_A_PLACE`). A HOLD whose object is one of the army's own positions — rear(guard), flank(s), retreat, line(s), position(s), ground, front, centre, wing(s), optionally "of the army" — has no target: it is the in-place HOLD. A friend's flank ("protect Ney's flank") is still read first as a SUPPORT of the friend.
- **An emphatic order is an order** (SF5-RV13; `clause_guards.strip_emphasis`, lever `AN_EMPHATIC_ORDER_IS_AN_ORDER`). A closed list of emphatic clauses (`EMPHATIC_CLAUSES`: "what are you waiting for", "do as I say / tell you", "do as you are told", "do what I say / tell you", "that is / that's / this is an order", "I command it", "I order it"), each a whole clause between separators (start, `,;:.!?—–`, "and", a spaced dash), is removed when an order verb remains in what is left; the residue then goes through every question test. Read at three seams: `is_question`, `dialogue_routing.line_asks_a_question` (a typed dialogue / interrupt answer) and the parser's pre-reader chain. A line that is only the rhetoric, or a question with rhetoric attached, is unchanged and still orders nothing (CRT-3).

### 93.3 §6 row 16 — the coordination is read on the field (SF-CL-1-D1, the user's ruling of October 3, 2026)
- **The lead's coordination context is read on the battle province** (`combat_executor.THE_COORDINATION_IS_READ_ON_THE_FIELD`; `_calculate_coordination_context(…, field=)`). The field-battle resolver hands both sides' context call `field=<the battle province>`. A field that is not the lead's own province — an attack from next door — replaces the region read: combined arms, per-ally coordination, the dedicated bonus and the Presence are read among the corps that stand on the field once the resolver has relocated its arrivals; the lead is counted present there and kept out of the adjacent count, which is read around the battle province (the adjacent-support docstring's own wording: "regions adjacent to the battle region"). A field that IS the lead's province — the defender always, a lead who stands on it — changes nothing. A corps that never marched no longer lends the lead per-ally coordination from the province he left; standing next to the field, it counts as adjacent support (+2% each) like every other friend there. The arrivals, stamped by the lead's call because they stand on the field, carry their own coordination into their committed share (`_committed_share` reads `get_attack_modifier`).
- **Scope: the field battle only.** The cavalry charge and the garrison assault keep the lead's own province: neither rolls reinforcements (`_calculate_reinforcements` has one caller), so no corps answers them and nothing relocates (`garrison_report.assault_forecast` mirrors the garrison path as before).
- **The forecast follows in lockstep** (`_priced_coordination._assumed`): a lead attacking from next door is priced on the field with every marching joiner present (and named in the adjacency exclusions, as the resolver's `arrived_names` are); an arriving gun corps fires from where he stands and stays IN the adjacent count — the resolver never puts a gun in `arrived_names` — where the old line had kept him out of it. Census rule (SF-CL-1): when every promised corps fights, the muster's ceiling equals the battle's massed strength to the man, with or without guns.
- **The gate reads the preview's context** (SF7-X4; `combat_executor.THE_GATE_READS_THE_PREVIEWS_CONTEXT`). `muster_odds` — the band the jealousy glory gate weighs on both boards (VP-R1 c) — computes under the same `_priced_coordination` the preview prints its band from, never off the transient stamps the last battle left.
- Levers down: the lead's own province, the gun's old exclusion, and the gate's unpriced read, as before. The series record (both levers, attributed) is the comment block above `BASELINE_SERIES` and `tools/_coord_field_series_arms_final.json`.

### 93.4 Slice 3b — the gun's expected weight and the counsel's purse (SF7-X2, SF7-X3)
- **An arriving gun is weighed by his own arrival roll** (`combat_executor.AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL`; `_expected_arrival_weight`). A gun that answers never relocates, but the resolver's Gate-4 block appends him to the participants and the committed term sums him whole, so the muster's expected figure prices him at the probability of the same roll every reinforcer makes, and his muster row states his odds (`MUSTER_ROWS_NAME_THEIR_ODDS`). A corps already on the field is 1.0 as before. The enemy AI's defender-muster price (`enemy_ai._muster_price`) reads the same weight (GR5).
- **Ground is broken without a corps** (`counsel.THE_BUILD_LINE_NEEDS_NO_CORPS`; `counsel._build_terms`). The counsel's build line reads the first province of ours with a corps on it, as before, and with none it reads the desk's finder `question_desk._first_own_region_that_can_build` (capital first, then by income) — the counsel half of AAR-18, which the desk's `can_build` answer already had. The levy line keeps its corps rule (a levy joins a marshal).
- Levers down: a gun priced at 0.0 and no odds on his row; a corps province or no build line.

### 93.5 Slice 4 — the Tilsit clause (§6 row 17, SF-NAV-1-D1; SF7-X5, SF7-X6)
- **The clause** `continental_system_join` — "joins the Continental System", canonical `{type, from, to}` (`from` the court that joins, `to` the court that imposes it), **no alliance**. The ruling wrote `continental_system`; the bare name is the alarm's source key and the separate peace's retired dropped-label key, and beside `continental_system_lifted` the verb names which way the clause moves (a naming deviation, FOR USER CONFIRMATION).
- **ONE membership write** `diplomacy.join_continental_system(world, nation, imposer, reason)` — the clause on both roads, both forced-alliance arms (membership and their single combined alarm unchanged) and `apply_continental_system`'s auto-join of the lord's satellites all write through it; each join is a `diplomatic_continental_system` dispatch beat (the court by its name, sentence-initial) and a campaign-log line `continental_system_membership` (category diplomacy, tier notable, always the player's business). The store stays a bare list.
- **ONE predicate** `diplomacy.continental_system_join_refusal(world, nation, imposer)` — `dependency_direction_invalid`, `cs_imposer_not_the_lord` (the System is the player's instrument: no AI writes the clause, GR5 by scope), `cs_no_ports` (an island or a portless court), `cs_trade_dominance_court`, `cs_already_member`, `cs_own_client` (a puppet or satellite of the imposer joins on its own). Read by the guided row (shown greyed with its reason for a member or the trade-dominance court; absent where the System has nothing to ask), the add verb, the validator (`settlement_validation.evaluate_continental_system_join_eligibility`) and both ratification arms, which re-run it (a full turn passes in transit).
- **The price** — harshness 0.2 in both dialects (half the forced alliance's 0.4; defiance dialect 0.15); `DEMAND_VALUES["continental_system_join"] = -10`; a material demand (the war-age penalty applies). Measured: at war age 10, France level with the court, Austria scores 24 and Russia 28 against the bar of 50; Austria signs at 60 points (52), Russia at 45 (52); the clause costs exactly 10 points over a plain peace. **The alarm** — `FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE` (+10) on the imposer at ratification, source `continental_system`, kept whole when a league is spent.
- **Carried by the separate peace** — `PAIR_SUBSTITUTE_CARRIED_TYPES` gains it; the seed carries `{"type": "continental_system_join", "value": 1}` only when `from` is the court and `to` the proposer leader; the bilateral `_ratify_treaty` applies it after the peace. The counter-offer never strikes it (the IGR-D carve rule); a peace carrying it is a stalemate, never a white peace, on the summary and the log.
- **The exit** (`diplomacy.A_MEMBER_AT_WAR_LEAVES_THE_SYSTEM`) — at `set_diplomatic_state`'s WAR transition a member at war with the System's lord leaves it ("— now at war with France"), a beat and a log line; the settlement's vassalage-ratification hop is exempt.
- **Shown** — the guided row's terms beside the clickable row too (`terms_display`, "closes 10 → 11 of 26 ports · +10 alarm", `continental_system_join_terms`); the court row line; the applied-clauses preview row (the alarm, the terms); the bilateral label; THE ADMIRALTY's System block names the members with their ports (`members_line`).
- **SF7-X5** (`settlement_actions.THE_PLAIN_ALLIANCE_KEEPS_NO_SYSTEM`) — the plain "Force X into alliance" link writes `includes_continental_system: False`; a keyless forced alliance reads as with the System on every display, as ratification reads it. **SF7-X6** — the toggle row names the court forced into the alliance.
- Levers down: a member at war keeps counting; the plain link writes no flag (the court joins the System).

### 93.6 Slice 5a — SF-CMD-2's remainder: the parser's words and the second name (CQ-8, CQ-38; CX5-L5-F3 … F6, N4, N5; NP-X8 … X10; NPC-10, NPC-18, NPC-26; SF7-X8)
- **The second name is heard** (CQ-8 / CQ-38; levers `parser.THE_SECOND_NAME_IS_HEARD`, `validation.THE_SECOND_NAME_RIDES_THE_RELAY`). An address of two or more of our marshals ("Ney and Soult, attack Mack") or a reward naming two ("grant Ney and Murat a rente") — `parser._split_second_name` — runs the FIRST man's order exactly as before; the second man's own order rides CR-7-3's relay for the player's seal, never sent by the game: beside an attack his SUPPORT of the first (the order the muster itself names), otherwise the same order re-addressed. A live reading that names two marshals takes the same road (`ParseResult.second_marshals`; the live road's "Multi-marshal commands coming in a future update!" is gone). The parser's sentence ends "<second>'s own waits behind it."; once the order has run the endpoint splices in what became of him (`relay.splice_second_name`): a man the muster already counts as marching, or whose rente would change nothing (`dotation.rente_would_change`), is acknowledged in one clause and NOT relayed (`relay.second_name_unneeded` — the line never holds an order the game would refuse); otherwise his order is on the line, priced when it is his support (`Marshal.strategic_order_ap(order_type="SUPPORT")` — 1 action since SR-2e). Every further name gets a clause ("Lannes marches already." / "… needs his own order."). His own order (not his support of the first) stands on its own — the first's refusal does not cancel it (`relay.build_relay(…, independent=True)`; Rule 4 is the sequence's rule); his support of a first order that did not go out is not relayed and says so. `parse_multiple` (zero production callers) is deleted; V2-61's invariants are pinned on the live splitter (`defend and hold` is never two names; an enemy name is never our second man; one man named twice is one man).
- **The retreat carried out, and continued** (CX5-L5-F3 / F4; lever `llm_client.THE_RETREAT_IS_CARRIED_OUT`). The carrying verbs also take `carry out` / `conduct` / `beat` / `perform` / `effect` / `undertake` (and "your retreat") — `_ORDER_THE_RETREAT_WIDE_RE`; a CONTINUED retreat is his own — `_retreat_is_carried_on`, the retreat branch's last arm ("keep / go on / resume / keep on retreating" had been caught by the participle rule, "keep / carry on falling back" and "keep pulling back" by nothing). "keep withdrawing" already retreated (the withdraw keyword) — measured, never claimed.
- **The shrug offers the retreat** (CX5-L5-F5; lever `THE_SHRUG_OFFERS_THE_RETREAT`). An addressed line that names a retreat and parses to nothing says how it was read and gives both orders: *"I read the retreat in your words as the enemy's, Sire. To withdraw <him> himself, say '<him>, retreat'; to strike at a foe who falls back, '<him>, attack <foe>'."* — the foe from `_hostile_first` (at war, in sight).
- **The CX-5 class's pins** (CX5-L5-F6). Each row is pinned at the PARSE on the guard that holds it, with both arms of its lever: the six the noun rule holds bind; `harry` (the pursuit branch) and `cover` / `screen` (the screening idiom) on their own guards; the end-to-end pin asserts the noun rule's own sentence (neither a retreat nor an objection to one produces it). "ride down the retreating Austrians" left the class — riding down a foe is an attack.
- **The pursuit names the man** (CX5-L5-N4; `strategic_parser._possessive_quarry`, lever `A_PURSUIT_NAMES_THE_MAN`). "pursue Mack's retreat / column / army / corps / rear(guard) / baggage" pursues Mack.
- **The disclosure keeps its tense** (CX5-L5-N5; lever `executor.THE_DISCLOSURE_KEEPS_ITS_TENSE`). The engine-picked target's disclosure on the branch that FOUGHT is past: "… <marshal> engaged <foe> at <province>, the nearest in sight." The branch that has not fought keeps "Name another and he will turn."
- **The inflected order is the order** (NP-X9; `parser.rewrite_inflected_order`, lever `THE_ORDER_VERB_LOSES_ITS_INFLECTION`). One of OUR marshals (or "the Emperor") at the head, then a third-person order verb from `_SOVEREIGN_ORDER_VERBS` ("moves", "marches", "fortifies"), is restated in the imperative before any reader. An enemy at the head stays narration; a line ending in "?" is the question guard's. No `moves` keyword in the mock chain: it was built and removed — it read "Mack moves to Swabia" as a move.
- **The dead fallback** (NP-X10). `_find_player_sovereign(world)` reads the live world only; the `game_state` branch (a key nothing produced) is deleted.
- **The anchor guard** (NP-X8). Every one of `_FIRST_PERSON_SUPPORT_ANCHORS` ("<marshal>, <anchor> me") is SUPPORT of the Emperor at `POST /command`; the guard iterates the set as the verb guard iterates the verbs (none inert when measured).
- **Talks are not a hold** (NPC-10; `parser.rewrite_hold_talks`, lever `TALKS_ARE_NOT_A_HOLD`). "hold talks / negotiations / a parley / a conference / a council / court with <court>" is "negotiate with <court>" — the diplomatic reading, never a HOLD on a province.
- **"the Emperor" is a referent** (NPC-18; lever `strategic_executor.THE_EMPEROR_IS_A_REFERENT`). On the support road "the Emperor" / "his Majesty" is the standing sovereign; the refusal's roster lists him as "the Emperor".
- **Riding down a foe, and the court named beside a province** (NPC-26; levers `attack_vocabulary.A_FOE_IS_RIDDEN_DOWN`, `combat_executor.A_NAMED_NATION_IS_ANSWERED`). "ride down <a foe>" is an attack (`RIDE_DOWN_A_FOE_RE` — never "ride down to …", "down the valley", nor somebody's retreat). A court named beside a province rides the parse as `target_nation_hint` (read only by the targetless reader and this arm); when no corps of that court is in sight in the province, the attack is a free refusal about THAT court — whose soil the province is, the nearest of them in sight, the order that reaches him (`combat_executor._named_nation_not_at_province`); never for the court that holds the province (its own refusal names it), never for the AI. **SF7-X8:** both named-court refusals take the court's adjective ("No Prussian force …", `display_names.nation_adjective`).
- Levers down: every reading above restores its shipped behaviour byte for byte (the named-court arm returns the province's own refusal; the second name is silent again; the live road's promise string returns).

### 93.7 Slice 5b — SF-CMD-2's remainder, part b: the desk, the map's names, the HOLD arm (RS-12, RS-15, CX3-X2, CX3-X3, PC15-13, CX-BEHAV-1, SF-V9; SF7-X9, SF7-X10, SF7-X11)
- **The what-if reads the order's state first** (RS-12; lever `question_desk.THE_WHAT_IF_READS_THE_ORDERS_STATE`). Before the range, `_the_named_corps` asks `state_probe.order_state_refusal(world, marshal, "attack")` — the executor's own gates in its own order (the action pool, the occupation lock, the pre-objection battery: fortified, drill-locked, wounded, recovering, broken) — and answers "The order would be refused, Sire: Davout is fortified — unfortify first. Nothing spent." instead of weighing a muster for an order the executor refuses.
- **The counsel's build line finds ground that takes a building** (RS-15; lever `counsel.THE_BUILD_LINE_FINDS_GROUND_THAT_TAKES_IT`). When the corps province can take nothing (stability under 51, its slots full, a work rising), the line falls back to the desk's `_first_own_region_that_can_build` — the same `region.can_build` gate.
- **A question names a place that exists** (CX3-X2; `clarification.destination_refusal`, lever `A_QUESTION_NAMES_A_PLACE_THAT_EXISTS`). An unaddressed march / move / hold whose place the map lacks is answered by the region matcher's own refusal, free, with no "Which marshal?" staged; a place the map has (or a typo it reads) still asks.
- **A printed guess keeps the first letter** (CX3-X3; lever `executor.A_PRINTED_GUESS_KEEPS_THE_FIRST_LETTER`). `_fuzzy_match_region` prints a suggest-band guess only with the typed word's first letter (or a plausible typo); a demoted auto-correct with a different first letter ("Jena" → Vienna) prints none; the low-confidence list prints only a guess within half the word's length in edits (`_a_guess_worth_printing` — "Bordeuex" → Bordelais stays). With no guess, the answer is the roads out of the marshal's province (`_roads_answer`, PC15-13's), else the refusal alone (`_no_guess_answer`). "Nearby:" — a spelling list, never geography — is retired with the lever up.
- **The march road reads its roads** (PC15-13; lever `strategic_executor.THE_MARCH_ROAD_READS_ITS_ROADS`). The strategic suggester passes the marshal's province as `near`; a single unknown name the CA8-28 swallow keeps out (a demoted guess) gets the roads answer from the seam's own fallback; a terrain noun keeps "The map knows no pass by that name".
- **The help census reads the judge** (CX-BEHAV-1). `tests/test_cx3_the_predictor.py`'s executor census is INVERTED and re-keyed to the ONE judge's classes: a manual phrasing passes only when it ran, the game asked, or the board refused a line it read right — any other refusal fails it. The judge learned four of the board's own refusals it did not know (`BOARD_GATE_RX`: "holds no rente", "No artillery marshals available", "cannot be summoned on", "summon the Congress first" — none in a committed census record), and the manual's sponsor / licence examples name the design Prussia holds on the boot (Hanover).
- **The HOLD arm's worklist** (SF-V9). A pronoun contraction is never a name (`clause_guards.A_CONTRACTION_IS_NEVER_A_NAME` — "We're short of guns - raise some artillery at Paris." is the levy, refused by the board for want of a gun commander); "get / send / find me some <troops>" is a levy (`llm_client.A_GET_ME_TROOPS_IS_A_LEVY`); a TRAILING "in case …" is a precaution, its clause blanked like `while` (`clause_guards.AN_IN_CASE_IS_A_PRECAUTION`) — a LEADING one keeps the contingency refusal; "get / have a <work> built" is the build (`llm_client.A_WORK_GOT_BUILT_IS_BUILT`). The generated verb set gains `get`, `find`, `fetch`, `see`. Re-measured: first contact C1 0 shrugs of 20 questions (16 at the baseline); every one of the eleven blind orders the row names reads as meant or is answered by the board or an objection.
- **The scout keeps its place** (SF7-X9; `llm_client.scouted_place_phrase`, lever `A_SCOUTED_PLACE_IS_KEPT`). "Ney, scout Alsace" — an unknown province — is refused free with the roads out of his province (it had run the bare scout of every neighbour for an action); a generic object ("the area", "ahead", "for the enemy") keeps the bare scout.
- **A condition's foe is never the target** (SF7-X10; lever `parser.A_BLANKED_CLAUSE_NAMES_NO_TARGET`). The parser's fuzzy target scan blanks condition clauses as it blanks reason clauses: "Ney, fall back while Mack advances" (and `before …`, and the trailing `in case …`) retreats with no "Mack cannot be reached".
- **A named levy ground is honoured** (SF7-X11; lever `economy_executor.A_NAMED_LEVY_GROUND_IS_HONOURED`). A named marshal still levies where he stands (PF-7), but a different province named beside him is refused free, naming both roads — "Davout, recruit infantry in Rhineland" with Davout at Lorraine had raised 3,000 men at Lorraine for 741 gold. Player orders only.
- Levers down: each reading restores its shipped behaviour.

### 93.8 Slice 6 — SF-DC-1 "Nothing unnamed": the doctrines' T9 and T10 as one instrument (SR-7d-X1, SR-7d-X2; SF7-X12 … X15; §6 row 20)

- **The instrument** (`tools/_doctrine_census.py`; `tools/playtest_driver.py --doctrine-census`, in-process only — over `--http` it records itself unmeasured). Off by default: it wraps five engine methods for the run and restores them at its end (`CombatExecutor._calculate_reinforcements` and `._doctrine_lines`, `CombatResolver.resolve_battle`, `WorldState.process_supply_attrition`, `EconomyExecutor._execute_recruit`). An exception inside it is recorded as `instrument_drift`, never swallowed (the transport swallows observer exceptions).
- **T9:** after every POST every marshal's `_doctrine_terms` is compared with `doctrines.derive_terms(world, nation)`; a difference is a `doctrine_drift` jsonl row.
- **T10:** each effect is captured where the mechanics decide it — an arrival the bar shift decided (`doctrine_arrived` and arrived, or reason `doctrine_delayed`, read in its final state), a scaled rout (`doctrine_morale` whose `morale_line` is not empty), the standing attack and defence rows (the resolver's own modifier snapshot), a supply bite (the attrition pass re-read with the clause neutralised; the census's doctrine-on reading must equal the engine's loss), a draft priced by the court's clause. Visible = the player a party, or the response carries it (the fog filter decides); an arrival also needs the reinforcer seen (the report's fog, read when the report was built). Named = the line on a route whose CLIENT function reads the key holding it; the routes and their renderers (`command` → `main.gd::_display_result`, `jealousy_attack` → `_display_jealousy_attacks`, `enemy_phase` → `enemy_phase_dialog.gd::_format_action`, `strategic_report` → `_show_strategic_reports`) are read from the `.gd` source at census time, function bodies with full-line comments stripped. A drawn doctrine line no effect of the run produced is a `doctrine_phantom`. Pass: 0 unnamed, 0 phantoms, ≥ 3 distinct named moments, one per great power that fought in sight. The verdict lands in `meta.json` (`doctrine_census`) and at the digest's foot.
- **The client draws what the wire carries** (SF7-X12 … X14): the enemy-phase dialog draws `doctrine_lines` and `morale_line` (after the trust note, before Berthier's observation, main.gd's order); it reads a levy's `doctrine_note` off the action entry — the executor's result — not `ai_action`, the AI's decision; a standing order's battle row renders Berthier's report through `_display_berthier_report`.
- **A supply bite names its clause** (SF7-X15; lever `world_state.THE_SUPPLY_BITE_IS_NAMED`): *"Supply shortage at Posen: Ney loses 1,440 troops — 576 of them to living off the land (this poor country feeds a French army 80%)"* ("all of them" when the clause alone caused the loss). The share is the engine's arithmetic re-read with the clause off — `get_effective_supply_cap(..., with_doctrine=False)`, exact because the clause is the multiplier's last step. Display only: the loss is the engine's; `doctrine` / `doctrine_losses` ride the event (GR6). Under the concentration tax the clause cannot bite (it lowers the cap; under it the rate is the press's).
- **An ally's war is its own** (§6 row 20, FOR USER CONFIRMATION; lever `emergent_designs.AN_ALLYS_WAR_IS_ITS_OWN`): the volte-face's NOT-HUMILIATED clause keeps IQ6-D2's bloc on its TREATY arm (a punitive memory) and reads its BATTLEFIELD arm (an emergent revanche) over the hegemon's vassal chain (`world._top_overlord(author) == hegemon`). Bavaria's conquest of Austrian homeland in Bavaria's own war no longer closes Austria's door; a partition signed for Bavaria at the table, or a conquest by France or a French vassal, still does.
- Levers down: each reading restores its shipped behaviour.


### 93.9 Slice 7 — the name and the rank, the overflowing queue, what a peace leaves (SF5-X3, NPC-12, S5-4, SF7-X7; SF7-X16)

- **ONE style for a marshal named in prose** (SF5-X3): `display_names.marshal_title(world, name, *, start=False)` — the court's own honorific (`marshal_honorific`) with the display name, never a roster key: "Marshal Ney", "General Mack", "the Archduke Charles", "the Emperor Napoleon", and now **"General Teulie" for a client's general** (lever `display_names.A_CLIENTS_GENERAL_IS_STYLED_GENERAL`; the predicate is R12's own `contingent.is_clients_general`, so with R12's lever down he is the Emperor's marshal again). `start=True` capitalises the article when the title opens a sentence ("The Archduke Charles WOUNDED at Bohemia"). A tombstone keeps `original_nation`, so the fallen keep their court's rank. Every template that styled a marshal object reads it: the executors' receipts and refusals (rente, estate, commission, recruit), the dotation and jealousy notices and petition titles, the capture and estate questions (the mount stamps `estate_holder_title` beside the machine key; a payload without it falls back to the display key), the dispatch templates (`{marshal}` is the title, filled through `dispatch._rank`), the crowned name abroad, the campaign log's fate lines (`format_event_oneliner(..., world=None)` — given the world it styles the man; without it he is humanised), the enemy-addressee refusal, Berthier's mock shrug, the desk's own fallen and the lost-marshal refusal. **The census** (`tests/test_sf7_s7_the_name_and_the_rank.py::TestTheCensus`): an AST walk over `backend/` fails on any literal "Marshal " before an interpolation — f-string or `.format` template, split literals included, docstrings excluded — outside a reasoned allowlist (a name the world does not know, the helper's own fallback, `_rank`'s lever-down arm, a producer-less template, a boot error, a debug print), and a stale allowlist row fails too.
- **The Admiralty takes the Emperor's orders** (SF7-X16, lever `naval_executor.THE_EMPEROR_COMMANDS_THE_ADMIRALTY`): `_admiralty_misaddressed` exempts the sovereign as the laws' `_misaddressed` does — the refusal says the Admiralty takes its orders from the Emperor, and under the court's own honorific it had become "not from the Emperor Napoleon in the field".
- **The name census** (NPC-12; `tools/_name_census.py`, `tools/playtest_driver.py --name-census`, in-process only): every string of every response, POST and GET (the driver's new `Transport.get_observers`), read for a roster key the reader should never see. The keys are derived from the world (every marshal whose display name differs from his key — on the 1805 board ArchdukeCharles and ArchdukeJohn). Out of scope by construction: a machine field (a whole-value key; a command, id, url or key field — the player's own order parses either way) and the two enemy-phase fields the client never renders (the phase's `summary[]`, an action's `message` — pinned by a source check over `enemy_phase_dialog.gd`). Verdict PASS needs zero leaks and at least one rendered display name (else VACUOUS). The producers it found fixed at their seams: the campaign log's garrison-assault, garrison-placed and last-stand lines; the strategic interrupts' blocked-path, combat-result, pursuit, hold and condition lines (`strategic.py`, `strategic_executor.py`); the cavalry auto-charge lines; the last stand's own message; the broken-army retreat; Berthier's capital alert; the petition's "Give him a command" detail; the ledger's ORDERS tab (`target_display` beside the machine `target`, read by `strategic_ledger.gd`). A dedupe key and a parsed command stay keys.
- **The queue overflows into the mailbox** (S5-4, lever `dialogue_manager.THE_QUEUE_OVERFLOWS_INTO_THE_MAILBOX`): at `QUEUE_CAP` (20) `push` keeps the arrival and `preempt` keeps the displaced dialogue — queued past the cap and listed by the mailbox — where both dropped silently. The queue stays bounded by the lapse rules (`lapse_pending_offers` at every end turn, `clear_stale`).
- **A peace names what each side keeps** (SF7-X7, lever `game_end.THE_PEACE_NAMES_WHAT_EACH_SIDE_KEEPS`): `game_end.status_quo_forecast(world, a, b, moved)` reads the ratifier's own `status_quo_retentions` before the peace (`forecast=True` — the pair is still at war and the bloc follows its lord, SR-1b), leaving out the provinces the package itself cedes or carves; `status_quo_forecast_lines` phrases it from the speaker's chair in the ratification summary's own sentences, and a WARNING for every province of the speaker's homeland the other side keeps ("Burgundy and Champagne stay with Austria by this peace — French soil behind a closed frontier once it is signed"), each province named once. A peace proposal from war or truce carries it (`proposal_terms_summary`, `annotated_terms` where that section renders, `status_quo_forecast`); a truce titles nothing and says nothing. The morning after, the dispatch names the soil the player's bloc ceded by the status quo (`status_quo_conceded`, HIGH) beside the soil it kept (`status_quo_titled`).
- Levers down: each reading restores its shipped behaviour (the honorific to "Marshal", the Emperor refused by the Admiralty, the drop at the cap, the silent peace).

### 93.10 Slice 8 — Chunk 9's client half: what the screen says (CX3-R2, R4, R5, R6, R9, R10, R11, R12; WO-V-D1, WO-V-D2, WO-D14; EAS-2's client half; the auto-end confirm's client half; the counter-punch row; §6 row 21)

- **A march with an empty destination slot asks where** (CX3-R2, lever `strategic_executor.A_BARE_MARCH_ASKS_WHERE`): `strategic_parser.march_slot_is_empty(raw_text)` is True when the line, trailing punctuation stripped, ENDS on a MOVE_TO keyword (`STRATEGIC_KEYWORDS`, longest first) whose last word takes an object (to / toward / towards / for / on / upon). The player's own order only (not an AI rung, not `_strategic_execution`): `clarification.build_move_destination_clarification(..., verb="march to", strategic_type="MOVE_TO")` answers with the adjacent provinces, each reissuing "<marshal>, march to <province>", the question priced at the marshal's own `strategic_order_ap`. Free. The AP pre-validation still runs first, so a man who cannot pay is refused before he is asked.
- **The drill verb is a word** (CX3-R5, lever `llm_client.THE_DRILL_IS_A_WORD`): `_DRILL_WORD_RE` — drill / train / exercise and their inflections as whole words; lever down = the substring read that made "Drillmaster of Boulogne" an order. The CX-R1 verb set (`backend/ai/routed_order_words.py`, generated by `tools/gen_routed_order_words.py` from the routing branches) carries the nine inflections the regex reads (348 words).
- **The manual's first recruit form is one the boot board takes** (CX3-R11): `recruit for Davout` (his corps, where he stands), then `recruit at Paris` / `recruit` with the reach condition stated.
- **The greyed separate-peace road names its price** (WO-D14, lever `settlement_validation.THE_GREYED_ROAD_NAMES_ITS_PRICE`): an `insufficient_resources` refusal ends "It costs N DP; you have M." — the figure the gate refused against, in the words of `diplomacy.diplomatic_price_quote` (a drift pin holds them equal). No new key; the refusal schema stays closed.
- **The counter-punch rail row carries its button** (lever `dispatch.THE_COUNTER_PUNCH_ROW_HAS_ITS_BUTTON`): `dispatch.counter_punch_notice(marshal, world)` is the ONE source of the row's message and details, read by the combat seam that posts it; `dispatch.counter_punch_target` the ONE reach (visible enemies within the man's movement range; the dispatch's `counter_punch_foe_in_reach` delegates to it). The button (`action_command` "<marshal>, attack <foe>", `action_label` "Strike <foe> — free", `action_detail`) only when `has_counter_punch()` (a cautious commander's unspent strike), a foe is in sight and reach, and the man is neither fortified (the note names the unfortify's price) nor locked in drill. `dispatch.restate_counter_punch_notices(world)` re-quotes every standing row in place (the collector's `refresh`; the row keeps its id) or dismisses it once the strike is spent, expired, or its man a prisoner; it runs on EVERY read of the rail — `main._pending_notifications(world)` is the ONE reader of `build_base_response`, `_finalize_command_notifications` and `GET /notifications`. The turn tick's CA9-N17 reconciliation stays (it reads the flag once a turn).
- **The client half** (`.gd`, driven where it can be): the terminal panel's `resized` re-runs `_reposition_after_layout` (CX3-R4); Tab is consumed by the command line whether or not anything is offered and Shift+Tab steps the highlight back (`_cycle_suggestion_back`, CX3-R6); `_add_verb_or_target`'s `_prefix` is unused on purpose (CX3-R12); `tools/cx3_completer_screenshot.gd` reads the real boot board (`tools/cx3_completer_board.json`) at the shipped terminal size (CX3-R9); the region panel's Build rows fold behind one header (`_build_open`, the `toggle:build` link — "▸ Build — N works" / "▾ Build"; WO-V-D1); no "Intel: Partial" / "Stale" line where the controller is the player (WO-V-D2); the campaign log sizes a row by its tier (`TIER_FONT_SIZES` lead 14 bold / notable 12 / routine 11; EAS-2); `_note_the_end_of_the_day()` at the end of `_update_status` — the End Turn button reads "End Turn (E) ▸" in gold while both pools are spent, and once a turn (`_auto_end_warned_turn`), with the administration spent and one or two actions left, the terminal prints `AUTO_END_WARNING`. No modal (§6 row 21).
- Levers down: each reading restores its shipped behaviour (the bare march priced at the nearest enemy, the substring drill, the bare refusal, the plain counter-punch row and no re-derivation).

### 93.11 Slice 9 — the frames: the screen says what the wire says (SF7-X17 … X32)

The IQ-10 re-shoot of every surface Steps 1–8 touched, at Interface Scales 1.0 and 2.0, and one five-turn Mode C session on the live client (France/1805, a sandboxed backend on port 8007). What they found, and the rules now in force:

- **The terminal keeps its scrollback** (SF7-X17, lever `main.THE_TRIM_KEEPS_THE_MESSAGES`): `add_output` is the ONE writer of the terminal and keeps every message it appends (`_output_messages`, BBCode intact); past `MAX_MESSAGES` the trim keeps the newest 75% of them. Godot 4's `append_text` never fills `RichTextLabel.text`, so the old trim — which split `.text` — kept 75% of nothing.
- **Bold and italic have faces** (SF7-X18): `main_theme.tres` names the RichTextLabel bold and bold-italic faces (EB Garamond at weight 700 on its own `wght` axis) and the italic face (`EBGaramond-Italic[wght].ttf`, its `.import` sidecar force-added — `assets/` is git-ignored). A theme's `default_font` answers every font item it leaves unset, so before this `[b]` and `[i]` rendered regular. An unset bold or italic SIZE falls back to the theme's 16px, so the two labels that use `[b]` for inline emphasis — the terminal (11) and the dispatch (12) — carry bold / italic / bold-italic sizes equal to their body; a `[b]` heading elsewhere keeps the 16 on purpose.
- **The day says what waits** (SF7-X19, lever `main.THE_DAY_SAYS_WHAT_WAITS`): the once-a-turn auto-end line (§93.10) is said after the order's own output (`call_deferred`), and while a current-turn envoy waits it says the day waits on the envoys (`AUTO_END_WAITS_WARNING`) — WO-22 defers the end of the day then, and the client's `pending_lapsing_count` is that deferral's own predicate (`dialogue_manager.get_lapsing_count`).
- **The famine counts its own turns** (SF7-X20, lever `dispatch.THE_FAMINE_COUNTS_ITS_OWN_TURNS`): the supply_strain candidate carries `age`, the province's trailing consecutive run of famine turns by the roster's window and rule (`dispatch._famine_run`), and the escalated headline's `{turns}` reads it; every other standing class keeps the page's run.
- **A covered map holds no hover** (SF7-X21, lever `map_renderer_base.THE_COVERED_MAP_HAS_NO_HOVER`): the map asks its owner whether a modal covers it (`pointer_blocked_check`, handed `main._is_modal_dialog_open`); covered, or dimmed by a screen (`panning_enabled` false), it clears its hover at once and takes no pointer event. **Our own soil carries no hedge** (SF7-X22, `OUR_SOIL_CARRIES_NO_HEDGE`): the tooltip twin of WO-V-D2.
- **The line fits the baize** (SF7-X23, lever `battle_diorama.THE_LINE_FITS_THE_BAIZE`): the tableau's outward and upward steps shrink to the room the stage leaves for the last contingent's locket; the authored 118 / 66px are the ceiling. **The reserve names its dead** (SF7-X29, `battle_diorama.THE_RESERVE_NAMES_ITS_DEAD`, both halves): the side payload's `reserve_casualties` (the unseated corps' own dead) rides the tail — "+1 corps in reserve — 258 lost" — so the baize and the odometer add up.
- **The books turn while you type** (SF7-X24, `ALT_TURNS_THE_BOOKS` in both ledgers): a bare digit turns a ledger's book unless a line edit holds focus; then Alt+digit does. The copy counts eight books.
- **The copy** (SF7-X25): a list with a tail joins once ("Berry, Burgundy, Corsica and 4 more", `dispatch.THE_LIST_JOINS_ONCE`); both treasury deltas read their thousands; "Morale: "; "no corps drawing 80% now; needs …" (`doctrines.THE_CURE_LINE_READS_CLEAN`); the table's narration says "Sire" once (`diplomatic_templates.THE_TABLE_SAYS_SIRE_ONCE`); a white peace's blockers name no terms (`SPOKEN_BLOCKER_PHRASES_WHITE_PEACE_NO_TERMS`, `THE_WHITE_PEACE_NAMES_NO_TERMS`); an ally's contribution petition fought beside the player (`settlement_offers.THE_PETITION_NAMES_ITS_SIDE`).
- **The colours know our friends** (SF7-X26, `main.THE_COLOURS_KNOW_OUR_FRIENDS` + `enemy_phase_dialog.THE_COLOURS_KNOW_OUR_FRIENDS`): every enemy-phase event naming its sides carries their standing toward the player (`main.battle_standing`: player · friend — ALLIANCE, DEFENSIVE_ALLIANCE or VASSAL either way · foe — WAR · neutral), stamped on COPIES of the producer's events (`_stamp_battle_standing`; the IGR-B trap). The dialog colours the result, both retreat lines and a garrison assault by ONE rule (`_standing_colour`: good news green, bad news red, a war not ours grey); an unstamped event keeps the France-only colour.
- **The question fits its box** (SF7-X27, `interrupt_popup.THE_QUESTION_FITS_ITS_BOX`): after the viewport clamp the panel shrinks to its content and re-centres, never grows — read two frames on, once the containers have sorted (the frame the text is set, a wrapping label with no width yet reports a per-character minimum: a fit read then is a no-op). **The Formables prompt hugs its quote** (SF7-X28, `diplomacy_wizard.THE_FORMABLES_PROMPT_HUGS_ITS_QUOTE`): step 3 lays its fixed quote out like step 1, not like step 2's assessment.
- **The petition names its table** (SF7-X30, `settlement_offers.THE_PETITION_NAMES_THE_TABLE`): both petition builders read `_petition_table_label` — our side's leader against every covered court, as the settlement dialogue names its table (G4F-7); a war-scoped line (the Grant option's "Open the settlement of … first") keeps the war's leader pair.
- **A garrison that gives way is said** (SF7-X31, `CombatExecutor.A_GARRISON_THAT_GIVES_WAY_IS_SAID`): a capital's garrison under the collapse line, cleared by the attack that finds it, is named — "The last N of the garrison at X give way." — and the conquest or occupation event carries `garrison_gave_way`, which the enemy phase prints. Both sides (GR5); display only.
- **"Decisive" is the result's word** (SF7-X32, `battle_report.THE_DECISIVE_WORD_IS_THE_RESULTS`): Berthier's two-to-one arm speaks of the exchange on a tactical result (`won_the_exchange`, both commanders named, never "we") and keeps "a decisive victory" for a decisive one.
- **The instrument** (IQ-10): the capture reads the marshal petition from `GET /marshal_petition` (B1's antechamber — a routine audience no longer rides the response that made it), a button inside a ScrollContainer is judged against the scroll's rect, not the logical viewport (a scrolled list is not off-screen), the closed-arm petition stages its grievance (B2 retires a card whose grievance does not stand), and two shots join the set (`interrupt_last_stand`, `wizard_formables_step3`). The mutation sweep's restore retries a locked file (`tools/mutation_sweep._restore`): a driven Godot test left `main.tscn` locked and the old restore died with the file MUTATED.
- Levers down: each reading restores its shipped behaviour.
