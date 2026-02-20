# Phase 7 Multi-Marshal Coordination: Spec Amendments
> **Status:** FINAL — All audit findings resolved
> **Audit Date:** February 19, 2026
> **Amends:** `docs/MULTI_MARSHAL_SPEC.md`
> **Authority:** Where this document conflicts with the original spec, **this document wins.**

---

## HOW TO USE THIS DOCUMENT

Read this alongside the original spec before each session. Items marked with a session tag apply starting from that session.

- ⚡ `[S57]` — Must apply before Session 57 starts (apply NOW)
- `[S60]` — Apply before Session 60
- `[S61]` — Apply before Session 61
- `[S62]` — Apply before Session 62
- `[S63]` — Apply before Session 63
- `[S64]` — Apply before Session 64
- `[S65]` — Apply before Session 65
- `[S66]` — Apply before Session 66

---

## CRITICAL ISSUES

---

### C1 · `resolve_battle()` Side Effects — Expanded Contract ⚡ `[S62]`

**Original spec §8 says:** when `apply_casualties=False`, skip strength modification and forced retreat.

**CORRECTION:** `resolve_battle()` has FIVE categories of side effects, not two. When `apply_casualties=False`, ALL of the following must be deferred to the caller:

| Side Effect | Location in combat.py | Action |
|---|---|---|
| `take_casualties()` — strength | lines 434–435 | Skip. Caller distributes. |
| `adjust_morale()` | lines 455–497 | Skip. Return deltas in result dict. |
| `battles_won` / `battles_lost` | lines 457–458, 469–470 | Skip. Caller increments per participant. |
| `counter_punch_available` (Davout) | lines 460–462, 479–481, 494–496 | Skip. Caller sets on primary defender only (see N1). |
| Recklessness `_increment_recklessness()` | line 573 | Skip. Caller handles on primary attacker only. |
| Forced retreat check | lines 534–545 | Skip. Caller checks each participant. |
| **Fortification degradation** | ~line 556 | **KEEP inside** — battle-triggered, not casualty-triggered. |

**New return fields required when `apply_casualties=False`:**
```python
"attacker_raw_casualties": int(attacker_casualties),
"defender_raw_casualties": int(defender_casualties),
"attacker_morale_delta": int(attacker_morale_change),  # negative = loss
"defender_morale_delta": int(defender_morale_change),
"raw_outcome": outcome,  # from projected strength (see C2)
```

**Caller responsibilities in `_execute_attack()` after `_distribute_casualties()` runs:**

**Morale is UNIFORM, not fractional.** Strength loss is proportional (physical damage scales with troop contribution). Morale loss is uniform (psychological impact — being present for a crushing defeat demoralizes a 1,000-man unit as much as a 50,000-man one). All participating marshals receive the FULL morale delta from the battle result.

```python
# ── ATTACKER SIDE: primary attacker + attacking allies ──
for participant in attacking_participants:  # excludes Non-Participating Hostile
    # Proportional strength loss (physical — scales by troop contribution)
    their_casualties = distribute_proportionally(participant, total_raw_attacker_casualties)
    participant.take_casualties(their_casualties)

    # UNIFORM morale (psychological — everyone in the battle feels the result)
    participant.adjust_morale(battle_result["attacker_morale_delta"])

    # All participants record the battle
    if won:
        participant.battles_won += 1
    else:
        participant.battles_lost += 1

    # Forced retreat: check each participant independently after morale applied
    if participant.morale <= 25 and participant.strength > 0:
        _apply_forced_retreat_or_break(participant, ...)

# ── DEFENDER SIDE: primary defender + defending allies ──
for participant in defending_participants:
    their_casualties = distribute_proportionally(participant, total_raw_defender_casualties)
    participant.take_casualties(their_casualties)

    # UNIFORM morale for defender side too
    participant.adjust_morale(battle_result["defender_morale_delta"])

    if won:  # "won" from defender's perspective
        participant.battles_won += 1
    else:
        participant.battles_lost += 1

    if participant.morale <= 25 and participant.strength > 0:
        _apply_forced_retreat_or_break(participant, ...)

# ── PRIMARY-ONLY EFFECTS ──
# Recklessness: primary cavalry attacker only
primary = attacking_participants[0]  # the marshal who issued the attack command
if getattr(primary, 'is_reckless_cavalry', False):
    if won:
        primary._increment_recklessness()
    else:
        primary.reset_recklessness()

# Counter-punch: primary defender only (see N1)
defender = defending_participants[0]
if getattr(defender, 'personality', '') == 'cautious' and not attacker_won:
    defender.counter_punch_available = True
    defender.counter_punch_turns = 2
```

---

### C2 · Victor Determination When `apply_casualties=False` ⚡ `[S62]`

**Problem:** With `apply_casualties=False`, strength is never modified. The existing victor check (`attacker.strength <= 0`) always sees full-strength marshals, making destruction outcomes impossible in coordinated battles.

**Fix:** Compute victor from **projected** strength without modifying actual `.strength`:

```python
# When apply_casualties=False — compute outcome from projections
projected_attacker = attacker.strength - attacker_casualties
projected_defender = defender.strength - defender_casualties

if projected_attacker <= 0 and projected_defender <= 0:
    outcome = "mutual_destruction"
    victor = None
elif projected_attacker <= 0:
    outcome = "defender_victory"
    victor = defender
elif projected_defender <= 0:
    outcome = "attacker_victory"
    victor = attacker
# ──────────────────────────────────────────────────────────────
# IMPORTANT: This threshold MUST match combat.py line 473 (1.5).
# Do NOT change to 1.2 or any other value. If the threshold changes
# in combat.py, update it here too.
# ──────────────────────────────────────────────────────────────
elif attacker_casualties > defender_casualties * 1.5:
    outcome = "defender_tactical_victory"
    victor = defender
elif defender_casualties > attacker_casualties * 1.5:
    outcome = "attacker_tactical_victory"
    victor = attacker
else:
    outcome = "stalemate"
    victor = None
```

Return as `raw_outcome` in the result dict. Caller uses this after distributing casualties to determine retreat logic. Never pass this into morale/battle record logic inside `resolve_battle()`.

---

### C3 · Wellington–Blucher Cross-Nation Coordination — Deferred to Phase 7b ⚡ `[S57]`

**Decision: Option B — Defer.**

Wellington is `nation="Britain"`, Blucher is `nation="Prussia"`. All coordination eligibility (§3), reinforcement eligibility (§7 rule #1), and win/loss relationship formula (§9) require **same nation**. Wellington and Blucher **cannot** coordinate in Phase 7. Their Devoted relationship only affects AI strategic movement scoring (P4.77).

**Apply these spec patches immediately (before Session 57):**

**Patch 1 — §2 Combined Arms Detection:** Add this note to the "Rules" subsection:
> *"France is the only nation capable of achieving 3/3 combined arms (+20% atk, +10% def). Britain caps at 2/3 (Wellington infantry + Uxbridge cavalry). Prussia caps at 2/3 (Blucher/Gneisenau infantry + PrinceAugust artillery). This asymmetry is intentional — it reflects Napoleon's integrated combined arms doctrine and is Phase 7's core player advantage."*

**Patch 2 — §3 Coordination:** Add to end of Eligibility Filters:
> *"Cross-nation coordination (e.g., Wellington ↔ Blucher, Britain ↔ Prussia) is deferred to Phase 7b alongside the Coalition Trigger system. Phase 7 coordination is same-nation only."*

**Patch 3 — §7 Reinforcement:** Add below eligibility rule #1:
> *"Coalition partner nations cannot reinforce each other in Phase 7. Their Devoted relationships affect only AI strategic movement scoring (P4.77) and cross-nation mechanics to be implemented in Phase 7b."*

**Patch 4 — §11 Battle Reports:** Remove the example line `"Reinforcement: Blucher arrived! (+4.5% def for Wellington)"` and the corresponding expanded view Blucher arrival block. Replace with a same-nation Davout example:

*Collapsed view replacement:*
```
Reinforcement: Davout arrived! (score 71, threshold 60)
```

*Expanded view replacement:*
```
── REINFORCEMENT ──
Davout: ARRIVED (score 71, threshold 60)
  Logistics 8 (+40), Rival (-10), Plains (+0), Cautious (-5), variance (+6)

Drouot: FAILED (score 54, threshold 60)
  Logistics 4 (+20), Professional (+0), Forest (-10), Cautious (-5), variance (-1)
```

**Phase 7b deferred item:** Add to §18 Deferred Items table:
| Feature | Phase | Description |
|---|---|---|
| Cross-nation coordination | 7b | Coalition partners (Britain/Prussia) coordinate as allied nations. Requires Coalition Trigger system or `allied_nations` mapping on WorldState. |

---

## DESIGN GAPS

---

### D1 · `holding_position` Not Cleared When Any Strategic Order Replaces HOLD ⚡ `[S61]`

**Confirmed bug:** `executor.py` lines 4172–4175 — when a new strategic order replaces an old one, `holding_position` is NOT explicitly cleared. Only the cancel path (~line 8372) and tactical override path (~line 937) clear it. A marshal going from HOLD → SUPPORT (or HOLD → PURSUE, HOLD → MOVE_TO) retains `holding_position = True`, failing reinforcement eligibility rule #8.

**Fix:** In `_execute_strategic_command()`, when replacing an existing HOLD order with ANY new strategic order, clear the HOLD posture:
```python
# Before assigning new order — clear HOLD state if old order was HOLD
old_order = marshal.strategic_order
if old_order and old_order.command_type == "HOLD":
    marshal.holding_position = False
    marshal.hold_region = ""
marshal.strategic_order = new_order
```

This mirrors the existing pattern at line 937 (tactical override path) and covers all strategic-to-strategic replacements: HOLD → SUPPORT, HOLD → PURSUE, HOLD → MOVE_TO.

**Add to §17 Gotchas table:**
| Issue | Solution |
|---|---|
| Any strategic order over HOLD leaves `holding_position = True` | In `_execute_strategic_command()`, check if old order was HOLD and clear `holding_position` + `hold_region` before assigning new order. |

---

### D2 · Who Gets `battles_won`/`battles_lost` in Coordinated Battles `[S62]`

**Decision:** All **participating** marshals increment `battles_won` or `battles_lost`. Hostile marshals who take 0% coordination and 0% casualties are **excluded** — they did not fight.

Rationale: The win/loss relationship formula (§9) requires a shared battle on both marshals' records. If allies don't have the battle recorded, the relationship formula cannot fire.

**Add to §8 Casualty Distribution:**
> *"After distributing casualties, all participating marshals (those who took proportional casualties — see D3 for Hostile SUPPORT edge case) increment `battles_won` or `battles_lost` as appropriate. Non-participating Hostile marshals do not."*

---

### D3 · Hostile Marshal + SUPPORT Order — Participating or Non-Participating `[S62]`

**Decision: Split.** SUPPORT + Hostile = **Participating for casualties, 0% coordination bonus.**

Rationale: Napoleon ordering Ney to support Davout means Ney fights — he doesn't get to refuse casualties just because he hates Davout. But hatred can't be ordered away, so coordination scaling remains 0%.

**Replace §8's Non-Participating rule with this expanded definition:**

**Participating marshals** (take proportional casualties, get `battles_won/lost`):
- Same-nation marshals in region at time of combat (not broken, not retreating, not recovering)
- **Hostile marshals who arrived via an active SUPPORT order targeting the combatant** — they fight under orders

**Non-Participating marshals** (0% casualties, 0% coordination):
- Hostile marshals present in the region **without** an active SUPPORT order — they refused to engage
- Hostile marshals who failed reinforcement arrival — not in region

**Coordination bonus is always relationship-scaled regardless of participation:**
- A Hostile marshal with a SUPPORT order: Participating (takes casualties) BUT coordination scaling = 0.00 (Hostile)
- The SUPPORT order makes them fight. It cannot make them cooperate.

**Add to §17 Gotchas table:**
| Issue | Solution |
|---|---|
| Hostile marshal + SUPPORT order = free repositioning exploit | Hostile + SUPPORT = Participating for casualties. Check `marshal.get_relationship(target) == -2 AND marshal.strategic_order.command_type == "SUPPORT"` — if both true, classify as Participating. |

**Berthier observation opportunity:** When a Hostile marshal fights under SUPPORT orders and takes casualties, this is narratively rich. Add to §11 observation categories:

| Priority | Category | Condition |
|---|---|---|
| P14 | `coordination_hostile_forced` | Hostile marshal participated via SUPPORT — took casualties, 0% coordination |

Template suggestion: *"Ney's presence brought numbers if not cooperation, Sire. He fought — as ordered — but every step beside Davout was teeth gritted."*

---

### D4 · Win/Loss Relationship Formula — Ordered Pairs `[S64]`

**Add to §9 Win/Loss Relationship Formula, after the `check_shared_battle_relationship` code block:**

> *"**Iteration pattern: ordered pairs, not unordered pairs.** For each ordered pair (A, B) among all participating marshals (including Hostile SUPPORT participants), call `check_shared_battle_relationship(A, B, ...)` AND `check_shared_battle_relationship(B, A, ...)` as separate calls. Each direction is fully independent — A's opinion of B can change while B's opinion of A does not, reflecting asymmetric relationships like Ney→Davout vs Davout→Ney.*
>
> *With 3 participating marshals (A, B, C): 6 total calls (A→B, B→A, A→C, C→A, B→C, C→B).*
>
> *The cooldown (`last_relationship_change_turn`) is per-direction: A→B cooldown does not affect B→A cooldown. Both can fire in the same battle."*

**Implementation in Session 64:**
```python
from itertools import permutations

participants = [m for m in all_marshals_in_battle if m.nation == primary.nation]
for a, b in permutations(participants, 2):
    check_shared_battle_relationship(a, b, battle_result, won, world)
```

---

### D5 · Transient Fields in `__init__` vs Serialization Test ⚡ `[S57]`

**Decision:** Use `getattr` pattern. Do NOT add transient coordination fields to `__init__`.

**In all spec sections §2, §3, §4, §5:** Replace every instance of `# Added to __init__ — NOT serialized` with:
```
# Set dynamically by _calculate_coordination_context() before each combat.
# NOT in __init__. Access via getattr(self, 'field', 0.0) in modifier methods.
# NOT serialized. Cleared by setting to 0.0 after resolve_battle() returns.
```

**The getattr pattern in modifier methods:**
```python
# In get_attack_modifier(), at end before return:
modifier *= (1.0 + getattr(self, 'combined_arms_attack_bonus', 0.0))
modifier *= (1.0 + getattr(self, 'coordination_attack_bonus', 0.0))
modifier *= (1.0 + getattr(self, 'dedicated_coordination_bonus', 0.0))
modifier *= (1.0 + getattr(self, 'adjacent_support_bonus', 0.0))
```

**Clearing after combat:**
```python
# In _execute_attack(), after resolve_battle() returns:
for attr in ['combined_arms_attack_bonus', 'combined_arms_defense_bonus',
             'coordination_attack_bonus', 'coordination_defense_bonus',
             'dedicated_coordination_bonus', 'adjacent_support_bonus']:
    if hasattr(marshal, attr):
        setattr(marshal, attr, 0.0)
    # Clear for allies too
    for ally in coordinating_allies:
        if hasattr(ally, attr):
            setattr(ally, attr, 0.0)
```

**Do NOT add these to `KNOWN_EXCLUSIONS` in `test_serialization_enforcement.py`.** The test should never see them because they're never in `__init__`.

---

### D6 · First-Time Coordination Tutorial — Player Side Only `[S66]`

**Correction to §12:**

Replace: *"Fires ONCE per campaign: the first time combined arms bonuses apply in any battle."*

With: *"Fires ONCE per campaign: the first time the **player's** marshals achieve combined arms bonuses in a battle the player commanded. The tutorial does NOT fire on AI-initiated battles, even if the AI achieves combined arms. Berthier narrates French victories, not enemy achievements."*

**Implementation gate:**
```python
# In _execute_attack(), after calculating coordination context:
if (not world.coordination_tutorial_shown
        and combined_arms_type_count >= 2
        and attacker.nation == world.player_nation):
    world.coordination_tutorial_shown = True
    # Display inline-dramatic tutorial block
```

---

### D7 · Reinforcer Retreat Destination — Location Timing `[S61]`

**Verify in Session 61:** Confirm `_apply_forced_retreat_or_break()` uses `marshal.location` (the current value, already updated to the battle region at time of reinforcement arrival) — not any cached pre-battle location variable.

Retreating to the reinforcer's original region is valid and expected behavior — it is adjacent to the battle region, so the retreat logic will naturally include it as an option.

**Add Session 61 test:**
```python
def test_reinforcer_retreats_from_battle_region_not_origin():
    """Reinforcing marshal who loses retreats from battle region adjacency, not their original region."""
    # Setup: Davout in Rhine, Ney in Waterloo (battle region), battle lost
    # After reinforcement: Davout.location = "Waterloo"
    # After lost battle: Davout should retreat to region adjacent to Waterloo
    # NOT necessarily Rhine (though Rhine would be valid if adjacent to Waterloo)
```

---

## INTERESTING INTERACTIONS — DOCUMENTED AS INTENTIONAL

---

### I1 · France's Exclusive 3/3 Combined Arms — KEEP

France: Ney (cavalry) + Davout/Grouchy (infantry) + Drouot (artillery) = 3/3 = **+20% atk, +10% def**
Britain: Wellington + Uxbridge = 2/3 max = **+10% atk, +5% def**
Prussia: Blucher/Gneisenau + PrinceAugust = 2/3 max = **+10% atk, +5% def**

**Documented as intentional design.** France's 3/3 advantage is the player's structural edge — Napoleon's Grande Armee was historically the first force to master fully integrated combined arms doctrine. The player's advantage isn't numbers, it's coordination quality. See §2 Patch 1 above.

---

### I2 · Ney-Davout Co-Location: 15% From Hatred — KEEP

A player who parks Ney and Davout together for 2 turns gets:
- Combined arms (cavalry + infantry): **+10% atk**
- Dedicated co-location (2 turns): **+5% atk / +5% def**
- Coordination scaling: **+0%** (Hostile)
- **Total: +15% atk, +5% def** despite their hatred

This is intentional dark comedy. The +15% is real — but they consume supply, Ney provides zero coordination scaling, and any narrative events referencing their relationship will be hostile. Players are rewarded for tolerating the tension. Keep as-is.

---

### I3 · Devoted Reinforcement — Floor Check Added `[S61]`

**Decision:** Add a floor check. Even Devoted pairs fail on minimum variance (~5% chance).

**Rationale:** 100% reliability removes all tension. The reliability gradient should reward Devoted relationships with *near-certainty*, not *certainty*. A 5% failure chance preserves narrative stakes ("even Gneisenau missed his moment") without undermining the system.

**Implementation — add independent fumble roll to `calculate_reinforcement_score()`:**
```python
# After computing score:
arrived = score > 60

# Minimum tension check: even high-scoring arrivals can fail on a critical fumble
# 1-in-20 chance of last-minute failure regardless of score (applies only if score > 80)
if arrived and score > 80:
    if random.randint(1, 20) == 1:  # 5% chance
        arrived = False
        near_miss = True
        near_miss_reason = "Even the best-laid plans can go awry at the crucial moment."
```

**Update §7 Arrival Score Formula** with this note:
> *"**Minimum tension clause:** Even if score > 80 (near-certain arrival), a 1-in-20 roll can cause failure. This ensures no reinforcement is ever truly guaranteed — Devoted relationships bring the probability to ~95%, not 100%. This only applies to score > 80; scores in the 60-80 range are unaffected."*

**Update §7 Inline-Dramatic Display** — add a near-miss failure template:
```
+---------------------------------------------------+
|  GNEISENAU -- DELAYED                             |
|  Every road pointed to Waterloo. Every plan       |
|  was perfect. A broken axle outside Wavre         |
|  cost him an hour. He was not there.              |
|  [Score: 84 -- Fate intervened]                   |
+---------------------------------------------------+
```

**Near-miss data flow:** The `near_miss` flag and `near_miss_reason` must be included in the reinforcement result dict. The display layer should select the near-miss inline-dramatic template when `near_miss=True`, showing the score with "Fate intervened" instead of the standard failure reason. Session 61 implementer wires this through `reinforcement_results[]` alongside existing `arrived`, `score`, `reason` fields.

---

## MINOR NOTES

---

### N1 · Counter-Punch: Primary Defender Only `[S62]`

**Clarification for C1:** `counter_punch_available` fires for the **primary defender only** — the marshal who was actually attacked. Allied defenders in the same region who took proportional casualties do NOT get counter-punch. They were present, but Davout's "Iron Marshal" ability is his personal tactical instinct, not a group buff. Never loop over allies for counter-punch; apply only to `defending_participants[0]`.

---

### N2 · Snapshot Timing: Coordination Fields Must Be Captured Before Consumption `[S65]`

**Order of operations in `_execute_attack()` with coordination:**

1. `_calculate_coordination_context()` — sets transient fields on marshals
2. `snapshot_attacker_modifiers()` / `snapshot_defender_modifiers()` — **MUST capture coordination fields** (extend in Session 65)
3. `marshal.get_attack_modifier()` — reads and consumes transient fields
4. `resolve_battle()` — uses effective strengths from step 3
5. `generate_battle_report()` — uses snapshots from step 2
6. Clear transient fields (cleanup)

**Session 65 must extend** `snapshot_attacker_modifiers()` and `snapshot_defender_modifiers()` in `battle_report.py` to capture `combined_arms_attack_bonus`, `coordination_attack_bonus`, `dedicated_coordination_bonus`, and `adjacent_support_bonus` via `getattr(marshal, 'field', 0.0)`. If step 2 doesn't capture them, step 3 consumes them, and step 5 sees zeroes — the battle report would silently omit all coordination bonuses.

---

### N3 · Near-Miss Data Flow Through Reinforcement Results `[S61]`

The I3 fumble roll produces a `near_miss: bool` flag and `near_miss_reason: str` that must flow through the reinforcement system:

```python
# In reinforcement result dict:
{
    "marshal": gneisenau.name,
    "arrived": False,
    "score": 84,
    "threshold": 60,
    "near_miss": True,              # NEW — triggers special display
    "near_miss_reason": "...",      # NEW — flavor text
    "reason": "fate_intervened",    # NEW — enum for template selection
    # ... existing fields (logistics_bonus, relationship_mod, etc.)
}
```

The inline-dramatic display selects from three templates:
- `arrived=True` → arrival template (gold border)
- `arrived=False, near_miss=False` → standard failure template
- `arrived=False, near_miss=True` → near-miss template (score shown with "Fate intervened")

---

### M1 · "Almost Never" -> "NEVER" for Hostile/Devoted WIN Formula `[S64]`

**In §9 WIN Formula, Asymmetry section:**

Replace: *"Decisive wins with Rivals sometimes improve (+15 + 0 +/- 10 = 35-55 -> ~30% chance). Hostile marshals almost never improve from wins (30 + 15 - 20 +/- 10 = 15-35 -> never)."*

With: *"Decisive wins with Rivals sometimes improve (+15 + 0 +/- 10 = 35-55 -> ~30% chance). Hostile marshals **never** improve from wins — max score 35 cannot reach threshold 50. Devoted marshals also **never** improve from wins — max score 35 cannot reach threshold 50. This is intentional: Hostile is already the floor (cannot improve), Devoted is already the ceiling (cannot improve further)."*

---

### M2 · LOSS Formula Threshold Note `[S64]`

**In §9 WIN/LOSS Relationship Formula, add footnote to the threshold:**

> *"The threshold is strict `> 50`, not `>= 50`. This is intentional: the Hostile LOSS maximum possible score is exactly 50 (15 + 10 + 15 + 10 = 50), which does NOT trigger degradation. Once Hostile (-2), shared losses cannot worsen the relationship further — the floor has been reached. If you find yourself tempted to change `>50` to `>=50`, don't. Check this note first."*

---

### M3 · Adjacent Support Cap — Documented as Self-Balancing `[S60]`

**Add to §5 Adjacent Support Bonus, after the Rules section:**

> *"**Cap reachability:** The +25% attack cap from all coordination sources is theoretically reachable via 5 adjacent marshals (5 x 2% = 10%) + 3/3 combined arms (20%) = 30% -> capped to 25%. This requires concentrating 6+ marshals in a tight geographic cluster. Supply attrition for a 6-marshal stack in any single region would be severe — the cap is self-balancing without special-casing."*

---

### M4 · `reinforced_this_turn` — Serialized Per-Turn Flag `[S61]`

**Correction to §7:** The spec says `reinforced_this_turn: bool` is "transient, not serialized." This is wrong per existing patterns.

**Decision:** Treat like `moved_this_turn`, `retreated_this_turn` — which ARE in `__init__`, ARE in `to_dict()`, and ARE in `from_dict()`. Per-turn flags must survive save/load mid-turn.

**Replace in §7:**
```python
# marshal.py __init__
self.reinforced_this_turn: bool = False  # ADD to __init__

# to_dict():
"reinforced_this_turn": self.reinforced_this_turn,  # ADD

# from_dict():
marshal.reinforced_this_turn = data.get("reinforced_this_turn", False)  # ADD
```

**`test_serialization_enforcement.py`:** Add `reinforced_this_turn` to the Marshal fixture fields.

---

### M5 · Grouchy Rule Narrative Never Fires for Coalition AI — OK

No fix needed. The Grouchy Rule is a player-facing narrative beat. No coalition marshal has `personality="literal"`. `PrinceAugust` is cautious. The rule firing exclusively for the French Grouchy is correct behavior.

---

### M6 · `{ally}` Template Placeholder Missing from `battle_report._fill()` `[S65]`

**Session 65 must extend `_fill()` in `battle_report.py` with coordination-specific placeholders:**

```python
def _fill(self, template: str, context: dict) -> str:
    """Fill template with context values."""
    result = template
    # Existing placeholders
    result = result.replace("{marshal}", context.get("marshal", ""))
    result = result.replace("{enemy}", context.get("enemy", ""))
    # NEW coordination placeholders (Session 65)
    result = result.replace("{ally}", context.get("ally", ""))
    result = result.replace("{relationship}", context.get("relationship", ""))
    result = result.replace("{coordination_bonus}", context.get("coordination_bonus", ""))
    result = result.replace("{arrival_score}", context.get("arrival_score", ""))
    return result
```

**Context dict for coordination observations must include:** `ally` (ally name), `relationship` (e.g., "Hostile", "Devoted"), `coordination_bonus` (e.g., "+4.5%"), `arrival_score` (e.g., "71").

---

### M7 · P4.77 Cross-Nation Check — Comment for 1805 `[S63]`

**In `enemy_ai.py` P4.77 implementation, add comment:**

```python
# Cross-nation ally scoring for strategic movement
# Current check works because coalition is always AI, France is always player.
# TODO-1805: Replace with _are_allied(ally.nation, marshal.nation) check
# when France can be AI-controlled or multiple player nations exist.
if (ally.nation != nation
        and ally.nation != world.player_nation  # works for Phase 7 only -- see TODO-1805
        and ally.strength > 0):
```

---

## SUMMARY TABLE

| ID | Severity | Decision | Apply Before |
|---|---|---|---|
| C1 | CRITICAL | `apply_casualties=False` defers 5 side effects; caller distributes all. Morale is UNIFORM (not fractional). Both attacker and defender sides handled. | S62 |
| C2 | CRITICAL | Victor from projected strength, never modify `.strength`. Tactical threshold 1.5 (matches combat.py) | S62 |
| C3 | CRITICAL | Defer cross-nation to 7b; France 3/3 is intentional advantage; patch §2,§3,§7,§11 examples | S57 ⚡ |
| D1 | DESIGN GAP | Clear `holding_position` + `hold_region` when ANY strategic order replaces HOLD | S61 |
| D2 | DESIGN GAP | All participating marshals get `battles_won/lost` | S62 |
| D3 | DESIGN GAP | SUPPORT + Hostile = Participating for casualties, 0% coordination | S62 |
| D4 | DESIGN GAP | Iterate ordered pairs for relationship formula (6 calls for 3 marshals) | S64 |
| D5 | DESIGN GAP | Transient fields use `getattr` pattern, NOT `__init__` | S57 ⚡ |
| D6 | DESIGN GAP | Tutorial fires on player-commanded battle only | S66 |
| D7 | DESIGN GAP | Verify `marshal.location` timing in retreat; test in S61 | S61 |
| I1 | INTERESTING | France 3/3 exclusive — documented as intentional | Keep |
| I2 | INTERESTING | Ney-Davout 15% from hatred — dark comedy, keep | Keep |
| I3 | INTERESTING | Devoted pairs get ~95% arrival (not 100%): 1-in-20 fumble roll when score > 80 | S61 |
| N1 | NOTE | Counter-punch: primary defender only, never allies | S62 |
| N2 | NOTE | Snapshots must capture coordination fields BEFORE get_*_modifier() consumes them | S65 |
| N3 | NOTE | Near-miss flag + reason in reinforcement result dict, 3 display templates | S61 |
| M1 | MINOR | "Almost never" -> "NEVER" for Hostile/Devoted WIN formula | S64 |
| M2 | MINOR | Note that `>50` (not `>=50`) is intentional for Hostile LOSS floor | S64 |
| M3 | MINOR | Cap reachability documented as self-balancing via supply attrition | S60 |
| M4 | MINOR | `reinforced_this_turn` serialized like `moved_this_turn` | S61 |
| M5 | MINOR | Grouchy Rule coalition AI gap — OK, intentional | No fix |
| M6 | MINOR | Extend `_fill()` with `{ally}`, `{relationship}`, coordination placeholders | S65 |
| M7 | MINOR | Add `TODO-1805` comment on P4.77 cross-nation check | S63 |

---

## SESSION READINESS CHECKLIST

**Before Session 57 (start NOW):**
- [ ] Apply C3 patches to §2, §3, §7, §11 (remove Wellington-Blucher examples)
- [ ] Apply D5: change all "Added to `__init__`" language in §2-§5 to `getattr` pattern
- [ ] Note France's 3/3 advantage as documented intentional design

**Before Session 60:**
- [ ] Apply M3: document cap reachability as self-balancing

**Before Session 61:**
- [ ] Apply D1: clear `holding_position` + `hold_region` when any strategic order replaces HOLD
- [ ] Apply D7: add Session 61 test for reinforcer retreat location
- [ ] Apply I3: add 1-in-20 fumble roll to `calculate_reinforcement_score()`
- [ ] Apply N3: wire `near_miss` flag + `near_miss_reason` through reinforcement result dict
- [ ] Apply M4: serialize `reinforced_this_turn`

**Before Session 62:**
- [ ] Apply C1: full expanded `apply_casualties=False` contract with uniform morale + both sides
- [ ] Apply C2: projected strength victor determination (threshold 1.5, matching combat.py)
- [ ] Apply D2: all participants get `battles_won/lost`
- [ ] Apply D3: SUPPORT + Hostile = Participating for casualties
- [ ] Apply N1: counter-punch on primary defender only

**Before Session 63:**
- [ ] Apply M7: add `TODO-1805` comment

**Before Session 64:**
- [ ] Apply D4: ordered pairs iteration pattern
- [ ] Apply M1: "almost never" -> "NEVER"
- [ ] Apply M2: note on `>50` threshold intent

**Before Session 65:**
- [ ] Apply M6: extend `_fill()` with coordination placeholders
- [ ] Apply N2: extend snapshot functions to capture coordination fields before consumption

**Before Session 66:**
- [ ] Apply D6: tutorial fires on player-commanded battle only
