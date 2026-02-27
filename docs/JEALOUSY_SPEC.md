# Jealousy System — Design Spec

> **Status:** DRAFT — Needs design gate approval before implementation.
> **Phase:** 7b (final item before Phase 8)
> **Prerequisite:** V2b Defiance COMPLETE, Tactical Triangle COMPLETE, Relationship system COMPLETE.

---

## Design Philosophy

"Jealousy makes marshals self-serving, not passive." They don't do less — they pursue their own agenda. Every personality type feels jealousy. What differs is how they act on it. The system routes through existing mechanics (relationships, coordination, defiance, objections) rather than creating parallel penalty tracks.

Historical anchor: Marshal rivalries were Napoleon's constant headache. Ney and Davout despised each other. Grouchy's inaction at Waterloo while hearing Ney's guns is the quintessential Literal jealousy moment. These weren't failures of skill — they were failures of ego management. That's the player's job.

---

## 1. Trigger: Glory Imbalance

### Core Mechanic

Track **recent battle wins** per marshal (rolling 5-turn window). When the delta between two same-nation marshals exceeds a threshold, the marshal with fewer wins becomes jealous of the one with more.

```
Glory Delta = target.recent_wins - self.recent_wins

Threshold:
  Default:       delta >= 2
  Accelerated:   delta >= 1 (when self.idle_turns >= 3)
```

### Why Glory Imbalance Over "Idle Jealousy"

The original "idle jealousy" (marshal didn't fight, another won) fires too often. On a typical turn, 1-2 marshals fight while 2-3 are idle. This makes jealousy the default state rather than a dramatic event. Glory imbalance requires *sustained* glory hoarding — the player must repeatedly favor one marshal over another before jealousy fires. This rewards rotating marshals into combat, which is already good strategy.

### Suppression Conditions

Jealousy is suppressed (never fires) when:
- Authority < 30 (desperate times unite people)
- Player capital is threatened (enemy in capital region or adjacent)
- Target marshal is currently broken or retreating
- Source marshal is currently broken or retreating

### Evaluation Timing

Checked at **end of turn** during `advance_turn()`, after battle results are processed and `process_battle_relationships()` has run. This ensures battle outcomes are fully resolved before jealousy evaluation.

---

## 2. Personality Expression

Each personality type expresses jealousy differently. The core output is always a **temporary relationship degradation** (-1 toward the glory target), which flows through existing coordination, objection, and defiance systems automatically. On top of that, each personality has a unique behavioral expression.

### Aggressive (Ney)

**Expression:** Autonomous attack. The marshal launches an unordered attack against a nearby enemy to grab his own glory. Hot, loud, blows over fast.

- Costs 1 AP from the player's budget (the marshal spends YOUR resources on HIS priorities)
- +15% attack modifier on solo attacks while jealous (jealousy as fuel)
- 0% coordination bonus while jealous (refuses to play with others)
- If no valid attack target exists, no autonomous action — just the relationship penalty

**Resolution:** 3-turn base. Cleared instantly by winning any battle (solo or coordinated). Fastest to resolve because giving them a fight is all they want.

### Cautious (Davout, Drouot)

**Expression:** Withholds full cooperation. Technically present in coordination but doesn't commit full strength. Cold, professional, lasts longer.

- Coordination contribution scaled to 50% (via temporary relationship downgrade)
- No solo bonus — Cautious marshals don't seek glory, they withhold it
- Campaign log flavor: critical reports undermining the rival ("Berthier notes that Davout has expressed... reservations about Marshal Ney's methods")

**Resolution:** 3-turn base. Cleared by shared victory with the jealousy target. Time alone doesn't fix it — they need proof the other marshal is competent.

### Literal (Grouchy) — DESIGN QUESTION, SEE §7

**Expression:** Malicious compliance. Follows orders to the letter in the least helpful interpretation. The Waterloo problem.

Candidate behaviors (all work through existing systems):
- **SUPPORT order:** Follows the target but `join_combat = False`. He arrives, he's physically present, but doesn't contribute coordination bonuses. The existing SUPPORT system already has a `join_combat` flag — jealous Literal just doesn't flip it.
- **MOVE_TO:** Arrives but doesn't fortify or prepare. No idle drill, no defensive stance. Just sits.
- **Attack order:** Executes the attack but doesn't pursue a broken enemy. Minimum effort, maximum compliance.

**Resolution:** 3-turn base. Cleared by giving clear direct orders that produce results (any successful action execution).

---

## 3. Relationship Integration

Jealousy's primary mechanical output is relationship degradation, which cascades through existing systems:

```
Jealousy fires
  → Relationship toward target: -1 (temporary, restored on resolution)
  → This automatically triggers:
     ├── Coordination penalty (via _RELATIONSHIP_SCALING in executor.py)
     │     Professional(0) → Rival(-1): contribution drops from 100% to 50%
     │     Rival(-1) → Hostile(-2): contribution drops to 0%
     ├── SUPPORT objection (via _evaluate_relationship_support in objection_v2.py)
     │     Hostile target = STRONG concern (Aggressive) or MODERATE (Cautious)
     └── Elevated defiance chance (existing modifiers in defiance.py)
```

**Important:** The relationship change is TEMPORARY. It's restored when jealousy resolves. This distinguishes jealousy (transient emotional state) from genuine relationship degradation (permanent, from battle outcomes). The marshal model needs a field to track the temporary modifier separately from the permanent relationship value.

---

## 4. Escalation

Repeated jealousy between the same pair (3+ times in a rolling 10-turn window) escalates:

1. **Warning (3rd trigger):** Morning Dispatch warning from Berthier. "Sire, the rivalry between Ney and Davout has become... persistent. I fear it may affect their cooperation in the field."

2. **Permanent degradation (4th+ trigger):** The temporary relationship penalty becomes permanent (-1 relationship that does NOT restore on resolution). This feeds into existing V2b SUPPORT objections and coordination penalties permanently.

### Escalation Tracking

```python
# Per-marshal, per-target: list of turn numbers when jealousy fired
jealousy_history: Dict[str, List[int]]  # target_name → [turn_5, turn_8, turn_12]

# Check: count entries within last 10 turns
recent_count = len([t for t in history if t >= current_turn - 10])
```

---

## 5. Surface to Player

### Morning Dispatch

New event type `jealousy_warning` added to dispatch event whitelist.

**Initial trigger (turn it fires):**
```
"Berthier reports that Ney appears envious of Davout's recent victories.
 He may act... impulsively."
```

**Escalation warning (3rd occurrence):**
```
"Sire, the rivalry between Ney and Davout has become a matter of concern
 among the general staff. Their cooperation cannot be relied upon."
```

**Berthier closing note priority:** Below broken/bankrupt/bleeding treasury, above idle/all-ready.

### Campaign Log

New event type `jealousy` added to `CAMPAIGN_LOG_TYPES` under "command" category.

Variants per personality:
- Aggressive: "Ney, envious of Davout's victories, grows restless for glory."
- Cautious: "Davout has grown distant toward Ney. Staff report reduced cooperation."
- Literal: "Grouchy has been... technically compliant with orders regarding Ney."
- Escalation: "The rivalry between Ney and Davout has become entrenched."

### Battle Report

If a jealous marshal participated in a battle, Berthier observations (P6c in battle_report.py) should note:

- Aggressive jealous marshal in solo attack: "Ney fought with particular ferocity — though one wonders if it was for France or for himself."
- Cautious marshal withheld coordination: "Davout's support was... measured."
- Literal marshal didn't join SUPPORT combat: "Grouchy was present. He did not engage."

---

## 6. New Marshal Fields

```python
# In marshal.py __init__
self.jealous_of: Optional[str] = None          # target marshal name, or None
self.jealousy_turns_remaining: int = 0          # countdown to auto-resolution
self.jealousy_relationship_modifier: int = 0    # temporary relationship penalty (restored on clear)
self.recent_battle_wins: List[int] = []         # turn numbers of wins (pruned to 5-turn window)
self.jealousy_history: Dict[str, List[int]] = {}  # target → [turn_numbers] for escalation tracking
```

All fields MUST be added to `to_dict()` and `from_dict()` with `.get()` defaults. Run `test_serialization_enforcement.py` after.

---

## 7. Open Design Questions

These need resolution before implementation.

### Q1: How should Literal jealousy work? (BIG QUESTION)

The Literal personality is built on "never objects, never defies." Malicious compliance is mechanically a defiance variant even if it's not flagged as one. Three options:

**Option A — Full malicious compliance (3 behaviors):**
SUPPORT with `join_combat=False`, MOVE_TO without fortify/drill, Attack without pursuit. Most thematically rich. Most implementation surface area (special-casing in SUPPORT logic, idle processing, and post-combat pursuit). Hardest to detect in-game, which may frustrate or delight.

**Option B — Single expression (SUPPORT only):**
Only the `join_combat=False` behavior. One flag check in one place. Most historically resonant (Grouchy at Waterloo). Detectable after the fact via battle reports. Clean to implement.

**Option C — Immune to jealousy:**
Literal marshals never get jealous. Preserves their identity as the "reliable, no-drama" option. Makes them mechanically valuable precisely because they don't cause problems. Simplest to implement. Loses the Waterloo fantasy.

**Recommendation:** Option B gives 80% of the flavor for 20% of the implementation cost. But this is a taste call.

### Q2: Should jealous Aggressive autonomous attacks burn player AP?

**Option: Yes (recommended).** The marshal spends YOUR resources on HIS priorities. Jealousy is always a cost. Prevents the exploit where players intentionally trigger jealousy for free attacks.

**Option: No.** The action is "free" but uncontrolled — the marshal acts on his own initiative, outside the action budget. Less punishing, more chaotic. The cost is unpredictability, not AP.

**Option: Compromise.** Costs 1 AP but only fires if the player has AP remaining. If AP=0, the marshal rages but can't act. This prevents the edge case where jealousy forces the player into negative AP or blocks their real orders.

### Q3: Cautious coordination withholding — flat penalty or percentage?

**Percentage (recommended):** Coordination from this marshal contributes at 50%. Scales naturally. Can be implemented by temporarily downgrading the relationship by -1 for coordination purposes, requiring zero new code in the coordination calculator.

**Flat penalty:** -5% coordination. Doesn't scale — devastating with 2 marshals, trivial with 4. Requires new code in coordination calculation.

The percentage approach is essentially what already happens when the relationship drops by -1 through the existing `_RELATIONSHIP_SCALING` table. If jealousy just degrades the relationship, this is free.

### Q4: Jealousy-as-motivation — +15% solo attack for jealous Aggressive?

This makes the system brilliant rather than just punitive. Ney is *better* when he's jealous — but uncontrollable. The player faces a real dilemma: a jealous Ney is dangerous to enemies AND to your plans.

**For:** Creates meaningful decisions. Historically accurate (Ney's reckless charges were devastating). Prevents jealousy from being purely negative.

**Against:** Might make players want Ney jealous. Could be exploitable (intentionally trigger jealousy before a big battle for the buff).

**If yes:** Should the buff apply only to solo attacks (no coordination), or to all attacks?

### Q5: "Council" command ("to my tent") as active resolution tool?

A new action where the player summons a marshal to discuss/resolve jealousy. Costs AP but clears the state.

**Recommendation: Defer to Phase 8 or later.** It's a full new action (validation.py, executor.py, parser.py, AP cost, LLM wiring). For now, the player resolves jealousy by rotating marshals into combat and managing assignments. If playtesting shows jealousy is too sticky without an active resolution tool, add this then.

### Q6: Should Literal malicious compliance be detectable before it matters?

If Option A or B for Q1:
- **Detectable after:** Berthier notes it in the battle report/dispatch. Player can't prevent it but can recognize the pattern. Patterns are strategic.
- **Detectable before:** Warning in the Morning Dispatch when issuing orders to a jealous Literal. Player can work around it. More forgiving.
- **Hidden entirely:** The surprise IS the point. Rewards attentive play (checking relationships, noticing idle turns). Most thematic. Most frustrating.

### Q7: Can jealousy fire toward enemy-nation marshals?

Current design assumes same-nation only. But what about: Ney sees an enemy marshal winning repeatedly while he's stuck garrisoning? Probably not worth the complexity, but worth explicitly ruling out.

**Recommendation:** Same-nation only. Enemy glory is just "the war going badly" — that's a morale/authority concern, not personal jealousy.

---

## 8. Implementation Outline

### Files to Modify

| File | Changes |
|------|---------|
| `backend/models/marshal.py` | New fields (§6), serialization, `clear_jealousy()` helper |
| `backend/models/world_state.py` | Jealousy evaluation in `advance_turn()`, window pruning |
| `backend/commands/executor.py` | Autonomous attack trigger (Aggressive), SUPPORT `join_combat` check (Literal), coordination modifier read |
| `backend/commands/strategic.py` | Literal SUPPORT `join_combat=False` when jealous |
| `backend/game_logic/relationship.py` | Temporary relationship modifier support |
| `backend/game_logic/dispatch.py` | `jealousy_warning` event type, Berthier closing note |
| `backend/game_logic/battle_report.py` | Jealousy-aware observations |
| `backend/campaign_log.py` | `jealousy` event type + formatter |
| `backend/notifications.py` | Jealousy notification (if EU4-style alert desired) |
| `backend/ai/enemy_ai.py` | Enemy marshals exempt from jealousy (or not — design question) |

### New File

`backend/game_logic/jealousy.py` — Core evaluation logic:
- `evaluate_jealousy(world)` — check all marshal pairs, fire triggers
- `resolve_jealousy(marshal, world)` — check resolution conditions
- `apply_jealousy(marshal, target, world)` — set fields, degrade relationship, log event
- `clear_jealousy(marshal, world)` — restore relationship, clear fields
- `check_escalation(marshal, target, world)` — escalation threshold check

### Test Coverage

- Trigger: glory delta >= 2, idle acceleration, suppression conditions
- Per-personality: Aggressive autonomous attack, Cautious coordination reduction, Literal behavior (TBD)
- Resolution: battle win clears, shared victory clears, timer expiry
- Escalation: 3-in-10 warning, 4th+ permanent degradation
- Relationship: temporary modifier applied/restored correctly, doesn't stack with permanent
- Serialization: all new fields round-trip
- Guard rails: authority < 30 suppression, capital threat suppression
- Edge cases: marshal jealous of broken marshal, jealousy during retreat, both marshals jealous of each other

---

## 9. What This Spec Does NOT Cover

- **Coalition Trigger** — moved to Phase 8
- **Council command** — deferred (see Q5)
- **Enemy marshal jealousy** — enemy AI marshals are exempt unless explicitly designed
- **Modding support** — jealousy thresholds/durations could be moddable, but not in initial implementation
- **LLM flavor text** — jealousy events use template strings, not LLM generation

---

## 10. Reference: Existing System Integration Points

| System | How Jealousy Connects |
|--------|----------------------|
| **Personality** | Determines expression: Aggressive=autonomous attack, Cautious=withholds, Literal=TBD |
| **Relationships** | Primary output: temporary -1 toward glory target |
| **Coordination** | Downstream: degraded relationship reduces coordination via `_RELATIONSHIP_SCALING` |
| **Objection V2** | Downstream: degraded relationship triggers SUPPORT objections via `_evaluate_relationship_support()` |
| **Defiance** | Downstream: jealousy could boost defiance chance (optional — not in current spec) |
| **Authority** | Guard rail: <30 suppresses jealousy |
| **Trust** | No direct trust impact (jealousy is marshal-vs-marshal, not marshal-vs-player) |
| **Morning Dispatch** | Surfaces warnings via Berthier note and turn events |
| **Campaign Log** | Logs jealousy events as "command" category entries |
| **Strategic Orders** | SUPPORT orders to jealousy targets become friction points |
| **Battle Report** | Post-battle observations note jealous behavior |
