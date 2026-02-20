# Phase 7 Multi-Marshal Coordination: Spec Amendments
> **Status:** FINAL — Three audit passes complete, all findings resolved
> **Audit 1:** February 19, 2026 (19 findings)
> **Audit 2:** February 20, 2026 (20 findings)
> **Audit 3:** February 20, 2026 (8 consistency fixes across Audit 1/2)
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
| `counter_punch_available` (Davout) | lines 460–462, 479–481, 494–496 | Skip. Caller sets per marshal. |
| Recklessness `_increment_recklessness()` | line 573 | Skip. Caller handles on primary attacker only. |
| Forced retreat check | lines 534–545 | Skip. Caller checks each participant. |
| **Fortification degradation** | ~line 556 | **KEEP inside** — battle-triggered, not casualty-triggered. |

**New return fields required when `apply_casualties=False`:**
```python
"attacker_raw_casualties": int(attacker_casualties),
"defender_raw_casualties": int(defender_casualties),
"attacker_morale_delta": int(attacker_morale_change),  # negative = loss, MUST be int
"defender_morale_delta": int(defender_morale_change),   # negative = loss, MUST be int
"raw_outcome": outcome,  # from projected strength (see C2)
```

> **Morale delta type:** `int`, not `float`. `adjust_morale()` (marshal.py:876) does `self.morale + change` directly — passing a float would create a float morale value, violating Golden Rule #2 (all numbers to Godot: `int()`). The existing `_scaled_morale_loss()` already returns `int`.

**Morale scaling source for coordinated battles:** The morale delta returned by `resolve_battle()` is computed using `_scaled_morale_loss()`, which scales by the **primary combatant's** casualty rate in the 1v1 projection. The caller does NOT recompute morale based on distributed casualties. This is intentional: the morale delta represents the psychological severity of the overall battle, not each participant's individual losses. A crushing defeat crushes morale for everyone present — the 1v1 projection captures the "how bad was this battle" signal, and all participants feel it equally. If this proves too harsh in playtesting (coordinated battles should feel somewhat safer psychologically since losses are shared), Session 62 may switch to total-side casualty rate: `raw_casualties / sum(p.strength for p in participants)`. But start with the simpler 1v1-projection approach and tune if needed.

**Caller responsibilities in `_execute_attack()` after `_distribute_casualties()` runs:**

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

**Confirmed bug:** `executor.py` lines 4172–4175 — when a new strategic order replaces an old one, `holding_position` is NOT explicitly cleared. Only the cancel path (~line 8372) and tactical override path (~line 937) clear it.

**The bug is broader than SUPPORT.** Any HOLD → SUPPORT, HOLD → PURSUE, or HOLD → MOVE_TO transition leaves `holding_position = True`. The fix should cover all strategic-to-strategic replacements:

**Fix:** In `_execute_strategic_command()`, when setting any new strategic order:
```python
# In _execute_strategic_command(), when setting new order (line ~4172):
old_order = marshal.strategic_order
if old_order and old_order.command_type == "HOLD":
    marshal.holding_position = False  # HOLD posture cleared by any new strategic order
    marshal.hold_region = ""          # mirrors pattern at line 937 (tactical override path)
marshal.strategic_order = new_order
```

This mirrors the existing pattern at line 937 where the tactical override path clears both flags. The fix is a 2-line addition before the assignment, not a SUPPORT-specific check.

**Add to §17 Gotchas table:**
| Issue | Solution |
|---|---|
| Any strategic order over HOLD leaves `holding_position = True` | Before setting `marshal.strategic_order`, check if old order was HOLD and clear `holding_position = False` and `hold_region = ""` |

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

**Coordination bonus is always relationship-scaled regardless of participation. The floor is 0%, never negative:**
- A Hostile marshal with a SUPPORT order: Participating (takes casualties) BUT coordination scaling = 0.00 (Hostile)
- The SUPPORT order makes them fight. It cannot make them cooperate. It cannot make them disrupt.

**Add to §17 Gotchas table:**
| Issue | Solution |
|---|---|
| Hostile marshal + SUPPORT order = free repositioning exploit | Hostile + SUPPORT = Participating for casualties. Check `marshal.get_relationship(target) == -2 AND marshal.strategic_order.command_type == "SUPPORT"` — if both true, classify as Participating. |

**Berthier observation opportunity:** When a Hostile marshal fights under SUPPORT orders and takes casualties, this is narratively rich. Add to §11 observation categories:

| Priority | Category | Condition |
|---|---|---|
| P6 | `coordination_hostile_forced` | Hostile marshal participated via SUPPORT — took casualties, 0% coordination |

> **Priority P6** (promoted from P14 — see A-M4). This is the most narratively interesting forced-cooperation event and should fire reliably, below critical coordination observations (P0.5–P0.8) but above generic fallbacks.

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

**The getattr pattern in modifier methods — A-C1 SUPERSEDES this section for modifier application:**

> ⚠️ **Do NOT apply four separate `*=` factors.** See A-C1 below. The modifier methods use a single `total_coordination_attack_bonus` / `total_coordination_defense_bonus` field. The four individual fields (`combined_arms_attack_bonus`, `coordination_attack_bonus`, `dedicated_coordination_bonus`, `adjacent_support_bonus`) exist only as `_display_*` prefixed fields for battle report display. See A-C1 for the correct pattern.

**Clearing after combat (updated per A-C1):**
```python
# In _execute_attack(), after resolve_battle() returns:
COORDINATION_FIELDS = [
    'total_coordination_attack_bonus', 'total_coordination_defense_bonus',
    '_display_combined_arms_atk', '_display_combined_arms_def',
    '_display_coordination_atk', '_display_coordination_def',
    '_display_dedicated_atk', '_display_dedicated_def',
    '_display_adjacent_atk',
]
for m in [marshal] + coordinating_allies:
    for attr in COORDINATION_FIELDS:
        if hasattr(m, attr):
            setattr(m, attr, 0.0)
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
# After computing score and determining arrival threshold (see A-I4):
HAS_EXPLICIT_ORDER = (
    order is not None
    and (
        (order.command_type == "SUPPORT" and order.target == primary_combatant.name)
        or (order.command_type == "PURSUE" and pursue_target_in_battle_region)
    )
)
ARRIVAL_THRESHOLD = 60 if HAS_EXPLICIT_ORDER else 65  # A-I4: orders lower the bar
arrived = score > ARRIVAL_THRESHOLD
near_miss = False
near_miss_reason = ""

# Minimum tension check: even high-scoring arrivals can fail on a critical fumble
# 1-in-20 chance of last-minute failure regardless of score (applies only if score > 80)
if arrived and score > 80:
    if random.randint(1, 20) == 1:  # 5% chance
        arrived = False
        near_miss = True
        near_miss_reason = "Even the best-laid plans can go awry at the crucial moment."
```

> ⚠️ **A-I4 integration:** The `ARRIVAL_THRESHOLD` variable comes from A-I4 (no-order threshold raised to 65). This code block is the single source of truth for arrival determination — it incorporates BOTH the variable threshold AND the fumble roll. Do not hardcode `score > 60` elsewhere.

**Update §7 Arrival Score Formula** with this note:
> *"**Minimum tension clause:** Even if score > 80 (near-certain arrival), a 1-in-20 roll can cause failure. This ensures no reinforcement is ever truly guaranteed — Devoted relationships bring the probability to ~95%, not 100%. This only applies to score > 80; scores in the 60-80 range are unaffected."*

**Update §7 Inline-Dramatic Display** — add a near-miss failure template:
```
┌─────────────────────────────────────────────────┐
│  GNEISENAU — DELAYED                            │
│  Every road pointed to Waterloo. Every plan     │
│  was perfect. A broken axle outside Wavre       │
│  cost him an hour. He was not there.            │
│  [Score: 84 — Fate intervened]                  │
└─────────────────────────────────────────────────┘
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
3. `marshal.get_attack_modifier()` — reads transient fields via `getattr`
4. `resolve_battle()` — uses effective strengths from step 3
5. `generate_battle_report()` — uses snapshots from step 2
6. Clear transient fields (cleanup)

**Session 65 must extend** `snapshot_attacker_modifiers()` and `snapshot_defender_modifiers()` in `battle_report.py` to capture `total_coordination_attack_bonus`, `total_coordination_defense_bonus`, and the `_display_*` breakdown fields via `getattr(marshal, 'field', 0.0)`. If step 2 doesn't capture them, step 3 reads them, and step 5 sees zeroes — the battle report would silently omit all coordination bonuses.

> ⚠️ **Updated per A-C1:** The snapshot captures the single `total_coordination_*_bonus` fields (used in modifiers) AND the `_display_*` fields (used in report breakdown). Both sets must be captured at step 2.

---

### N3 · Near-Miss Data Flow Through Reinforcement Results `[S61]`

The I3 fumble roll produces a `near_miss: bool` flag and `near_miss_reason: str` that must flow through the reinforcement system:

```python
# In reinforcement result dict:
{
    "marshal": gneisenau.name,
    "arrived": False,
    "score": 84,
    "threshold": 65,  # variable per A-I4 — 60 with orders, 65 without
    "near_miss": True,              # NEW — triggers special display
    "near_miss_reason": "...",      # NEW — flavor text
    "reason": "fate_intervened",    # NEW — enum for template selection
    # ... existing fields (logistics_bonus, relationship_mod, etc.)
}
```

The inline-dramatic display selects from four templates:
- `arrived=True, hostile_support=False` → standard arrival template (gold border)
- `arrived=True, hostile_support=True` → Hostile+SUPPORT arrival template (see A-D4)
- `arrived=False, near_miss=False` → standard failure template
- `arrived=False, near_miss=True` → near-miss template (score shown with "Fate intervened")

---

### M1 · "Almost Never" → "NEVER" for Hostile/Devoted WIN Formula `[S64]`

**In §9 WIN Formula, Asymmetry section:**

Replace: *"Decisive wins with Rivals sometimes improve (+15 + 0 ± 10 = 35-55 → ~30% chance). Hostile marshals almost never improve from wins (30 + 15 - 20 ± 10 = 15-35 → never)."*

With: *"Decisive wins with Rivals sometimes improve (+15 + 0 ± 10 = 35-55 → approximately one in four (~24%) chance). Hostile marshals **never** improve from wins — max score 35 cannot reach threshold 50. Devoted marshals also **never** improve from wins — max score 35 cannot reach threshold 50. This is intentional: Hostile is already the floor (cannot improve), Devoted is already the ceiling (cannot improve further)."*

> ⚠️ **A-M1 applied inline:** The "~30%" figure corrected to "approximately one in four (~24%)" — see A-M1 below for derivation.

---

### M2 · LOSS Formula Threshold Note `[S64]`

**In §9 WIN/LOSS Relationship Formula, add footnote to the threshold:**

> *"The threshold is strict `> 50`, not `>= 50`. This is intentional: the Hostile LOSS maximum possible score is exactly 50 (15 + 10 + 15 + 10 = 50), which does NOT trigger degradation. Once Hostile (-2), shared losses cannot worsen the relationship further — the floor has been reached. If you find yourself tempted to change `>50` to `>=50`, don't. Check this note first."*

---

### M3 · Adjacent Support Cap — Documented as Self-Balancing `[S60]`

**Add to §5 Adjacent Support Bonus, after the Rules section:**

> *"**Cap reachability:** The +25% attack cap from all coordination sources is theoretically reachable via 5 adjacent marshals (5 × 2% = 10%) + 3/3 combined arms (20%) = 30% → capped to 25%. This requires concentrating 6+ marshals in a tight geographic cluster. Supply attrition for a 6-marshal stack in any single region would be severe — the cap is self-balancing without special-casing."*

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
        and ally.nation != world.player_nation  # works for Phase 7 only — see TODO-1805
        and ally.strength > 0):
```

---

## SECOND AUDIT FINDINGS (February 20, 2026)

---

### A-C1 · Coordination Bonus: Additive Sum, Single Multiplier ⚡ `[S57]`

**Problem:** The D5 `getattr` pattern (now superseded — see D5 update above) applied four separate `*=` factors:
```python
modifier *= (1.0 + combined_arms_attack_bonus)    # e.g., 0.20
modifier *= (1.0 + coordination_attack_bonus)      # e.g., 0.03
modifier *= (1.0 + dedicated_coordination_bonus)   # e.g., 0.05
modifier *= (1.0 + adjacent_support_bonus)         # e.g., 0.02
```
Four multiplicative factors compound to 1.319 (+31.9%), not 1.30 (additive sum) and certainly not 1.25 (capped). The hard cap cannot be correctly enforced across four separate fields.

**Fix:** `_calculate_coordination_context()` sums all four sources, applies the hard cap to the sum, then sets **two fields only**:

```python
# In _calculate_coordination_context():
raw_atk = combined_arms_atk + coordination_atk + dedicated_atk + adjacent_atk
raw_def = combined_arms_def + coordination_def + dedicated_def
capped_atk = min(raw_atk, 0.25)  # hard cap
capped_def = min(raw_def, 0.20)

# Set on marshal — only these two fields are used by modifier methods:
marshal.total_coordination_attack_bonus = capped_atk
marshal.total_coordination_defense_bonus = capped_def

# Individual fields kept for battle report display only:
marshal._display_combined_arms_atk = combined_arms_atk
marshal._display_combined_arms_def = combined_arms_def
marshal._display_coordination_atk = coordination_atk
marshal._display_coordination_def = coordination_def
marshal._display_dedicated_atk = dedicated_atk
marshal._display_dedicated_def = dedicated_def
marshal._display_adjacent_atk = adjacent_atk
# etc. — prefix with _display_ to signal read-only reporting use
```

**In `get_attack_modifier()` and `get_defense_modifier()`:**
```python
# SINGLE multiplier — already capped by _calculate_coordination_context():
modifier *= (1.0 + getattr(self, 'total_coordination_attack_bonus', 0.0))
# (defense modifier uses total_coordination_defense_bonus)
```

**Add to §17 Golden Rules:**
> *"Coordination bonuses are ADDITIVE with each other (sum first), then capped, then applied as ONE multiplier. Never apply them as four separate `*=` factors — multiplicative compounding silently exceeds the hard cap."*

---

### A-C2 · SUPPORT Order Cleared Before Coordination Calculation `[S61]`

**Problem:** §7 says "clear `marshal.strategic_order = None` after reinforcement relocation." §4 Path B checks if any ally has a SUPPORT order targeting the combatant. If the order is cleared at relocation (step 2), the dedicated bonus check at step 4 fails — the 2 AP spent on SUPPORT is wasted.

**Fix:** Defer order-clearing until AFTER `_calculate_coordination_context()` completes.

```python
# In _execute_attack(), reinforcement and coordination sequence:
# Step 1: Count adjacent marshals
# Step 2: Run reinforcement checks — record arrived_via_support on result dict BEFORE clearing
for result in reinforcement_results:
    if result["arrived"]:
        arriving_marshal = world.get_marshal(result["marshal"])
        order = getattr(arriving_marshal, 'strategic_order', None)
        result["arrived_via_support"] = (
            order is not None
            and order.command_type == "SUPPORT"
            and order.target == primary_combatant.name
        )
        arriving_marshal.location = battle_region  # relocate
        # DO NOT clear strategic_order here

# Step 3: Recalculate adjacent count (arrivals removed)
# Step 4: _calculate_coordination_context() — checks live strategic_order AND arrived_via_support
# Step 5: AFTER coordination context is complete — NOW clear strategic orders for arrivals
for result in reinforcement_results:
    if result["arrived"]:
        arriving_marshal = world.get_marshal(result["marshal"])
        arriving_marshal.strategic_order = None  # cleared here, after bonus captured
```

**Update `_has_dedicated_support()` to check both sources:**
```python
def _has_dedicated_support(self, marshal, same_region_allies, world, reinforcement_results=None) -> bool:
    # Path A: co-location duration (unchanged)
    # Path B: active SUPPORT order (unchanged — order still alive at this point)
    # Path B2: arrived via SUPPORT this battle (safety net — if order was cleared early)
    if reinforcement_results:
        for result in reinforcement_results:
            if (result.get("arrived_via_support")
                    and result["marshal"] in [a.name for a in same_region_allies]):
                return True
    return False
```

---

### A-C3 · Defender-Side Coordination Not Specified ⚡ `[S57]`

**Problem:** The spec describes `_calculate_coordination_context()` only from the attacker's perspective. §17 Golden Rule #5 says "Both sides get independent coordination," but provides no pseudocode for calculating the defender's coordination. A defender with three allies present would get 0% coordination — the spec leaves this entirely to implementer imagination.

**Fix:** Add to §3 Coordination Bonus, new subsection "Defender Coordination":

> *"`_calculate_coordination_context()` must be called TWICE in `_execute_attack()`:*
> *1. With the **attacker** as primary marshal and their same-nation allies — sets transient fields on attacker and attacking allies*
> *2. With the **defender** as primary marshal and their same-nation allies — sets transient fields on defender and defending allies*
>
> *Both calls happen BEFORE `resolve_battle()`. The defender's coordination flows into `get_defense_modifier()` via the same transient field pattern. No changes to `combat.py` — it already reads modifiers from both marshals.*
>
> *In `_calculate_coordination_context(nation, primary, world)`: pass `primary.nation` to filter same-nation allies correctly for each side."*

**Add to Session 57 and 58 test lists:**
- `test_defender_gets_coordination_bonus_from_allies`
- `test_defender_combined_arms_independent_of_attacker`
- `test_both_sides_coordination_in_same_battle`

---

### A-D1 · Grouchy Rule PURSUE Check — Region-Match Not Name-Match `[S61]`

**Problem:** The spec uses `order.target == defender.name`. If Grouchy has `PURSUE Wellington` and the battle is `Ney attacks Blucher` in a region where Wellington also stands, Grouchy is blocked despite his quarry being present.

**Fix:**
```python
# Replace name-match with region-match:
elif order.command_type == "PURSUE":
    pursue_target = world.get_marshal(order.target)
    if pursue_target and pursue_target.location == battle_region:
        has_relevant_order = True
```

---

### A-D2 · `moved_this_turn` Missing from Reinforcement Eligibility `[S61]`

**Problem:** A marshal who moved (via action) could reinforce, effectively moving a second time. Artillery that already moved (losing attack eligibility) could reinforce and move again.

**Fix:** Add eligibility rule #12 to §7:
> *"12. NOT `moved_this_turn` — troops cannot force-march twice in a turn"*

---

### A-D3 · SUPPORT Dedicated Bonus — One-Directional `[S59]`

**Decision: One-directional. Intentional.**

`SUPPORT Davout` gives Davout the +5%/+5% dedicated bonus (Path B). Ney (the supporter) does NOT get the dedicated bonus from Path B alone — only from Path A (2 turns co-located). The supporter's Path B benefit is the +10 arrival score bonus, not the dedicated combat bonus.

**Bidirectional dedicated bonus requires:** Both marshals issue SUPPORT targeting each other (4 AP total). The player pays for mutual readiness.

**Add to §4 Path B documentation:**
> *"**Path B is one-directional.** `SUPPORT Davout` gives Davout the dedicated bonus. Ney gains +10 on his reinforcement arrival score — not the dedicated bonus. To give both marshals dedicated bonus immediately via SUPPORT, issue SUPPORT in both directions: 'Ney, support Davout' AND 'Davout, support Ney' (4 AP total). Otherwise wait 2 turns co-located for Path A."*

---

### A-D4 · Hostile Reinforcement — Excluded Without SUPPORT `[S61]`

**Decision:** Hostile WITHOUT SUPPORT → excluded from auto-reinforcement entirely.

**Rationale:** A Hostile marshal who auto-reinforces without orders converts from +2% adjacent support to 0% coordination — a net-negative for the player. Rather than create a punitive edge case, simply block it: Hostile marshals must be explicitly ordered via SUPPORT to reinforce.

**Add eligibility rule #13 to §7:**
> *"13. NOT `get_relationship(primary_combatant.name) == -2` without an active SUPPORT order targeting the combatant. Hostile marshals cannot auto-reinforce — they must be explicitly ordered via SUPPORT and survive the objection system."*

**Hostile + SUPPORT arrivals:** A Hostile marshal who arrives via SUPPORT is Participating per D3 (takes casualties, 0% coordination, gets `battles_won/lost`). No additional impact roll mechanic — the cost of forced cooperation is already steep: the player spent 2 AP on SUPPORT, survived the objection system, and the Hostile marshal takes casualties while providing 0% coordination bonus. The punishment is bleeding for nothing. The coordination floor is 0%, never negative.

**Berthier observation:** `coordination_hostile_forced` at priority P6 (see D3) covers this narrative moment with a single template. No impact variants needed.

**Add to §17 Gotchas table:**
| Issue | Solution |
|---|---|
| Hostile auto-reinforcement is net-negative | Eligibility rule #13 blocks it. Hostile marshals reinforce ONLY via explicit SUPPORT order. |

---

### A-D5 · (Resolved by A-D3 — no separate entry needed)

---

### A-D6 · Bombardment Excluded from Coordination — Documented `[S57]`

**Intentional.** Coordination bonuses apply to ATTACK actions only, not BOMBARDMENT.

**Add to §1 Design Principles:**
> *"**Coordination applies to ATTACK only.** Bombardment has its own modifier system and does not receive coordination bonuses. The combined arms bonus from having artillery present in a region benefits the marshal issuing an ATTACK command — not the artillery marshal's own bombardment. Co-located artillery makes your attacks stronger; it does not make its own bombardment stronger."*

---

### A-D7 · Co-Location Tracking Timing — Before Turn Increment `[S59]`

**Fix:** Call `_update_co_location_tracking()` from inside `_process_tactical_states()`, which fires BEFORE `current_turn` increments (see `world_state.py` line 3041 vs. 3052). New co-location entries record `start_turn = self.current_turn` (old value). Dedicated bonus check `current_turn - start_turn >= 2` fires at START of 3rd turn of co-location (after 2 complete end-of-turn cycles).

**Add to §4 Tracking section:**
> *"Call from `_process_tactical_states()`, before `current_turn` increments. New entries record `start_turn = self.current_turn`. Threshold `current_turn - start_turn >= 2` fires at start of the 3rd co-location turn."*

---

### A-D8 · AI Priority Insertion Points `[S63]`

**Add to §10 AI Enhancements:**

> *"Concrete insertion order in `_evaluate_marshal()`:*
> - *P4.6 `_find_coordinated_attack()`: after P4.5 (undefended capture), before P4.75 (ally support)*
> - *P4.76 `_should_maintain_co_location()`: inside P7 strategic movement block as an early-return guard — if returns True, skip movement evaluation entirely*
> - *P4.77 cross-nation adjacency scoring: inside `_consider_strategic_move()` scoring function, NOT a separate priority node*
> - *P4.78 `_find_defensive_reinforcement_position()`: after P7 strategic movement, before P8 fallback/wait"*

---

### A-I1 · Defensive Coordination More Efficient Than Offensive — Keep

+5% per defending ally vs. +3% per attacking ally. Fortified marshals contribute to defense only. Defense hard cap +20% vs. attack +25%.

**Add to §1 Design Principles:**
> *"**Defensive coordination is more efficient per-ally (+5% def vs. +3% atk).** Attackers must achieve combined arms AND numerical superiority to overcome coordinated defense. This reflects Napoleonic doctrine: the defense had an inherent advantage."*

---

### A-I2 · All Defenders Take Casualties from Any Attack — Document `[S66]`

When multiple same-nation marshals co-defend, ALL take proportional casualties when ANY is attacked. This is a significant change from 1v1 combat. Players may not realize stacking 3 defenders means all three take damage.

**Add to first-time coordination tutorial (§12):**
> *"When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted."*

---

### A-I3 · Rival → Professional Arc — Flag for Berthier `[S65]`

Rivals winning a decisive battle together: ~24% chance of improvement per battle. With 3-turn cooldown: ~12 turns (4 decisive wins) to go from Rival to Professional on average.

**Add Berthier observation at P15** (after relationship change fires):
> *"Sire, I believe {marshal}'s opinion of {ally} is... shifting."*

---

### A-I4 · Logistics × 5 Kept, No-Order Threshold Raised to 65 `[S61]`

Davout (logistics 8): base score 90 before relationship/terrain. Always arrives from plains without SUPPORT.

**Decision: Keep logistics × 5. Raise no-order threshold to 65.**

The threshold for marshals WITHOUT an active SUPPORT or PURSUE order is raised from 60 to **65**:
```python
# In calculate_reinforcement_score():
HAS_EXPLICIT_ORDER = (
    order is not None
    and (
        (order.command_type == "SUPPORT" and order.target == primary_combatant.name)
        or (order.command_type == "PURSUE" and pursue_target_in_battle_region)
    )
)
ARRIVAL_THRESHOLD = 60 if HAS_EXPLICIT_ORDER else 65
arrived = score > ARRIVAL_THRESHOLD
```

> ⚠️ **I3 integration:** This threshold feeds into the I3 fumble check. See I3 above for the combined implementation. The I3 code block is the single source of truth for arrival determination — do not duplicate threshold logic.

**Effect:** Davout from plains/Professional without orders: base 90 ± 8 = [82, 98]. Still arrives reliably. But logistics 5 marshal from hills/Rival without orders: 50 + 25 - 10 - 5 ± 8 = [52, 68] — meaningful failure chance. Orders matter. Logistics helps. Neither alone guarantees arrival.

**Update §7 Arrival Score Formula:**
> *"Threshold: score > 60 if marshal has active SUPPORT or PURSUE order targeting the battle. Score > 65 otherwise. Orders lower the bar — logistics alone is not enough."*

---

### A-M1 · WIN Formula: ~30% → ~24% `[S64]`

Rival decisive win: scores 51–55 out of range [35–55] = 5/21 values ≈ 23.8%.

> Applied inline to M1 above. No separate action needed.

---

### A-M2 · Adjacent Support Attack-Only — Document `[S60]`

Adjacent support is +2% attack only, no defense component. Defenders benefit only from same-region allies.

**Add to §5:**
> *"Adjacent support is attack-only. Defenders benefit from same-region allies, not adjacent ones. To strengthen a defense, co-locate — don't just be nearby."*

---

### A-M3 · Fortified SUPPORT Marshal — Berthier Advisory `[S61]`

A fortified marshal with a SUPPORT order grants the dedicated bonus but cannot reinforce (eligibility rule #7). The player gets no warning.

**Add Berthier advisory:** Display when SUPPORT is issued to a fortified marshal:
> *"Sire, {marshal} is ordered to support {ally} but is fortified — they cannot march to reinforce from their current position. Consider unfortifying, or rely on the co-location coordination bonus."*

---

### A-M4 · `coordination_hostile_forced` Observation — Promoted to P6

> Applied inline to D3 above. The observation was originally P14, now P6.

---

### A-M5 · Coordination Preview Note `[S65]`

Preview shows pre-reinforcement combined arms. Actual battle may get 3/3 if artillery reinforces.

**Add single line to preview display:**
> *"Note: Adjacent reinforcements may modify these values."*

---

## THIRD AUDIT FINDINGS — Cross-Audit Consistency Fixes (February 20, 2026)

---

### X1 · D5 Clearing Code Superseded by A-C1 ⚡ `[S57]`

**Problem:** D5's clearing code references four field names (`combined_arms_attack_bonus`, `coordination_attack_bonus`, etc.) that A-C1 replaced with `total_coordination_attack_bonus` + `_display_*` prefixed fields. The D5 code block was stale.

**Fix:** D5 clearing code updated inline above to reference the A-C1 field names. The `COORDINATION_FIELDS` list in D5 is now the single source of truth for clearing.

---

### X2 · I3 Threshold Integrated with A-I4 `[S61]`

**Problem:** I3 originally hardcoded `arrived = score > 60`. A-I4 introduced a variable threshold (60 with orders, 65 without). Both were tagged `[S61]` but used different threshold values.

**Fix:** I3 code block updated inline above to use the `ARRIVAL_THRESHOLD` variable from A-I4. The I3 code block is now the single source of truth for arrival determination, incorporating both the variable threshold and the fumble roll.

---

### X3 · C1 Morale Delta Type and Scaling Source `[S62]`

**Problem:** C1 originally specified `float(attacker_morale_change)` for the morale delta return field. But `adjust_morale()` (marshal.py:876) takes `int` and does `self.morale + change` directly — a float would create float morale. Additionally, the morale scaling source (which casualty rate drives `_scaled_morale_loss`) was unspecified for coordinated battles.

**Fix:** C1 return type corrected to `int()` inline above. Morale scaling source documented: use the primary combatant's 1v1 casualty rate (the battle severity signal), with a note to tune in Session 62 playtesting if it proves too harsh. See updated C1 section.

---

### X4 · D3 Coordination Floor 0% Consistent with A-D4 `[S61/S62]`

**Problem:** D3 established "0% coordination" as the floor for Hostile+SUPPORT marshals. A-D4 originally included a negative impact roll that could reduce coordination below 0%.

**Fix:** A-D4 simplified to exclude Hostile from auto-reinforcement (rule #13) with no impact roll. Hostile+SUPPORT arrivals follow D3's rule cleanly: Participating for casualties, 0% coordination, `battles_won/lost` recorded. No negative coordination — the floor is 0%. D3 and A-D4 are now consistent.

---

### X5 · N3 Template Selection Updated for A-D4 `[S61]`

**Problem:** N3 listed three display templates. A-D4 Hostile+SUPPORT arrivals need a fourth template path.

**Fix:** N3 updated inline above with four template paths including `arrived=True, hostile_support=True`.

---

### X6 · N2 Snapshot Field Names Updated for A-C1 `[S65]`

**Problem:** N2 referenced the four original field names for snapshot capture. A-C1 renamed them.

**Fix:** N2 updated inline above to reference `total_coordination_*_bonus` and `_display_*` fields.

---

### X7 · Session 61 Scope Advisory `[S61]`

Session 61 carries 11 items — more than any other session and already flagged as "HIGHEST RISK SESSION" in the original spec. The items are: D1, D7, I3, M4, N3, A-C2, A-D1, A-D2, A-D4, A-I4, A-M3.

**Advisory:** If Session 61 runs long, the following items can safely defer to Session 62 without creating blocking dependencies:

| Item | Can Defer? | Reason |
|---|---|---|
| A-M3 (Berthier advisory) | Yes | Display-only, no mechanical dependency |
| A-D1 (PURSUE region-match) | Yes | Edge case, only matters when multiple enemies share a region |
| A-D4 (Hostile exclusion rule #13) | Yes | Low probability scenario, -20 penalty already near-blocks |

Core items that MUST ship in Session 61: D1, D7, I3, M4, N3, A-C2, A-D2, A-I4.

---

## SUMMARY TABLE

| ID | Severity | Decision | Apply Before |
|---|---|---|---|
| **AUDIT 1** | | | |
| C1 | CRITICAL | `apply_casualties=False` defers 5 side effects; caller distributes all (uniform morale, both sides). Morale delta is `int`, scaled from 1v1 projection. | S62 |
| C2 | CRITICAL | Victor from projected strength (threshold 1.5), never modify `.strength` | S62 |
| C3 | CRITICAL | Defer cross-nation to 7b; France 3/3 is intentional advantage; patch §2,§3,§7,§11 | S57 ⚡ |
| D1 | DESIGN GAP | Clear `holding_position` + `hold_region` for ANY strategic order replacing HOLD | S61 |
| D2 | DESIGN GAP | All participating marshals get `battles_won/lost` | S62 |
| D3 | DESIGN GAP | SUPPORT + Hostile = Participating for casualties, 0% coordination (floor is 0%, never negative) | S62 |
| D4 | DESIGN GAP | Iterate ordered pairs for relationship formula (6 calls for 3 marshals) | S64 |
| D5 | DESIGN GAP | Transient fields use `getattr` pattern, NOT `__init__`. **A-C1 supersedes modifier pattern — use single total field.** | S57 ⚡ |
| D6 | DESIGN GAP | Tutorial fires on player-commanded battle only | S66 |
| D7 | DESIGN GAP | Verify `marshal.location` timing in retreat; test in S61 | S61 |
| I1 | INTERESTING | France 3/3 exclusive — documented as intentional | Keep ✅ |
| I2 | INTERESTING | Ney-Davout 15% from hatred — dark comedy, keep | Keep ✅ |
| I3 | INTERESTING | Devoted pairs ~95% arrival: 1-in-20 fumble roll when score > 80. **Uses A-I4 variable threshold.** | S61 |
| N1 | NOTE | Counter-punch fires for primary defender only | S62 |
| N2 | NOTE | Snapshots capture `total_coordination_*_bonus` + `_display_*` fields BEFORE `get_*_modifier()` | S65 |
| N3 | NOTE | `near_miss` flag + reason in reinforcement result dict, **4** display templates (incl. Hostile+SUPPORT) | S61 |
| M1 | MINOR | "Almost never" → "NEVER" for Hostile/Devoted WIN formula. ~30% → ~24%. | S64 |
| M2 | MINOR | `>50` (not `>=50`) intentional for Hostile LOSS floor | S64 |
| M3 | MINOR | Cap reachability self-balancing via supply attrition | S60 |
| M4 | MINOR | `reinforced_this_turn` serialized like `moved_this_turn` | S61 |
| M5 | MINOR | Grouchy Rule coalition AI gap — OK, intentional | No fix ✅ |
| M6 | MINOR | Extend `_fill()` with `{ally}`, `{relationship}`, coordination placeholders | S65 |
| M7 | MINOR | Add `TODO-1805` comment on P4.77 cross-nation check | S63 |
| **AUDIT 2** | | | |
| A-C1 | CRITICAL | Coordination is additive sum → single multiplier. Four-field `*=` pattern replaced. **Supersedes D5 modifier pattern.** | S57 ⚡ |
| A-C2 | CRITICAL | SUPPORT order cleared AFTER coordination calc, not at relocation. `arrived_via_support` flag | S61 |
| A-C3 | CRITICAL | Defender-side coordination: call `_calculate_coordination_context()` twice. Add to S57/S58 tests | S57 ⚡ |
| A-D1 | DESIGN GAP | Grouchy PURSUE: region-match not name-match | S61 |
| A-D2 | DESIGN GAP | `moved_this_turn` = eligibility rule #12 (no double-marching) | S61 |
| A-D3 | DESIGN GAP | SUPPORT bonus one-directional. Document 4 AP for mutual dedicated bonus | S59 |
| A-D4 | DESIGN GAP | Hostile auto-reinforcement excluded (rule #13). No impact roll — 0% coordination floor preserved per D3. | S61 |
| A-D5 | — | Resolved by A-D3 | — |
| A-D6 | DESIGN GAP | Bombardment excluded from coordination — document in §1 | S57 ⚡ |
| A-D7 | DESIGN GAP | Co-location tracking runs before turn increment in `_process_tactical_states()` | S59 |
| A-D8 | DESIGN GAP | AI priority insertion points: P4.6 after P4.5, P4.76 as guard, P4.77 inside scoring, P4.78 after P7 | S63 |
| A-I1 | INTERESTING | Defense more efficient per-ally — document in §1 as intentional | Keep ✅ |
| A-I2 | INTERESTING | All defenders take casualties — warn in tutorial | S66 |
| A-I3 | INTERESTING | Rival → Professional arc: ~24%, ~12 turns. Add Berthier observation P15 | S65 |
| A-I4 | INTERESTING | Logistics ×5 kept. No-order threshold raised to 65. **Integrated into I3 code block.** | S61 |
| A-M1 | MINOR | WIN formula: ~30% → ~24%. **Applied inline to M1.** | S64 |
| A-M2 | MINOR | Adjacent support attack-only — document | S60 |
| A-M3 | MINOR | Fortified SUPPORT marshal: Berthier advisory | S61 |
| A-M4 | MINOR | `coordination_hostile_forced` promoted to P6. **Applied inline to D3.** | S65 |
| A-M5 | MINOR | Coordination preview: add "Adjacent reinforcements may modify these values" | S65 |
| **AUDIT 3 (CONSISTENCY)** | | | |
| X1 | FIX | D5 clearing code updated for A-C1 field names | S57 ⚡ |
| X2 | FIX | I3 threshold uses A-I4 variable `ARRIVAL_THRESHOLD` | S61 |
| X3 | FIX | C1 morale delta is `int`, scaling source documented | S62 |
| X4 | FIX | D3 0% floor consistent with A-D4 (no negative impact roll) | S61/S62 |
| X5 | FIX | N3 has 4 template paths (added Hostile+SUPPORT) | S61 |
| X6 | FIX | N2 snapshot field names updated for A-C1 | S65 |
| X7 | ADVISORY | Session 61 has 11 items. A-M3, A-D1, A-D4 can defer to S62 if needed. | S61 |

---

## SESSION READINESS CHECKLIST

**Before Session 57 (start NOW) — 5 items:** ⚡
- [ ] **C3**: Patch §2, §3, §7, §11 — remove Wellington-Blucher examples, document France 3/3 advantage
- [ ] **D5 + A-C1 (X1)**: Transient fields NOT in `__init__`. Single `total_coordination_*_bonus` multiplier in modifier methods. `_display_*` prefix for report-only fields. Clearing code uses `COORDINATION_FIELDS` list.
- [ ] **A-C3**: Defender-side coordination — add second call to `_calculate_coordination_context()` for defender. Add to S57/S58 test lists.
- [ ] **A-D6**: Document bombardment excluded from coordination in §1

**Before Session 59:**
- [ ] **A-D3**: Document SUPPORT one-directional in §4 (4 AP for mutual)
- [ ] **A-D7**: Co-location tracking in `_process_tactical_states()`, before turn increment

**Before Session 60:**
- [ ] **M3**: Cap reachability note in §5
- [ ] **A-M2**: Adjacent support attack-only — add documentation note

**Before Session 61 — 11 items (highest-risk session — see X7 for deferral options):**
- [ ] **D1**: Clear `holding_position` + `hold_region` for ANY strategic order replacing HOLD
- [ ] **D7**: Add retreat location timing test
- [ ] **I3 + A-I4 (X2)**: Variable threshold (60/65) + 1-in-20 fumble roll — single code block
- [ ] **M4**: Serialize `reinforced_this_turn`
- [ ] **N3 (X5)**: Wire `near_miss` flag + reason through reinforcement result dict, 4 templates
- [ ] **A-C2**: SUPPORT order cleared AFTER coordination calc. `arrived_via_support` flag on result dict.
- [ ] **A-D2**: Add `moved_this_turn` as eligibility rule #12
- [ ] **A-D4 (X4)**: Hostile auto-reinforcement blocked (rule #13). No impact roll — 0% floor per D3.
- [ ] **A-M3**: *(deferrable to S62)* Fortified SUPPORT Berthier advisory
- [ ] **A-D1**: *(deferrable to S62)* Grouchy PURSUE: region-match not name-match
- [ ] **A-I4**: *(integrated into I3 above — no separate action)*

**Before Session 62 — 5 items (+any deferred from S61):**
- [ ] **C1 (X3)**: Full `apply_casualties=False` contract (uniform morale as `int`, both attacker AND defender sides, 1v1-projection scaling)
- [ ] **C2**: Projected strength victor (threshold 1.5)
- [ ] **D2**: All participants get `battles_won/lost`
- [ ] **D3 (X4)**: SUPPORT + Hostile = Participating for casualties, 0% coordination floor
- [ ] **N1**: Counter-punch primary defender only

**Before Session 63:**
- [ ] **M7**: `TODO-1805` comment on P4.77
- [ ] **A-D8**: AI priority insertion points documented

**Before Session 64:**
- [ ] **D4**: Ordered pairs iteration (6 calls for 3 marshals)
- [ ] **M1 + A-M1**: "Almost never" → "NEVER", ~30% → ~24%
- [ ] **M2**: `>50` threshold intent note

**Before Session 65:**
- [ ] **M6**: Extend `_fill()` with coordination placeholders
- [ ] **N2 (X6)**: Snapshot timing — capture `total_coordination_*_bonus` + `_display_*` fields
- [ ] **A-I3**: Rival→Professional Berthier observation at P15
- [ ] **A-M4**: *(applied inline to D3 — no separate action)*
- [ ] **A-M5**: Coordination preview note

**Before Session 66:**
- [ ] **D6**: Tutorial fires on player-commanded battle only
- [ ] **A-I2**: Casualty sharing warning in tutorial
