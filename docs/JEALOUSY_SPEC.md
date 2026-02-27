# Jealousy System — Design Spec

> **Status:** DRAFT v2 — Needs design gate approval before implementation.
> **Phase:** 7b (final item before Phase 8)
> **Prerequisite:** V2b Defiance COMPLETE, Tactical Triangle COMPLETE, Relationship system COMPLETE.

---

## Design Philosophy

"Jealousy makes marshals self-serving, not passive." They don't do less — they pursue their own agenda. Every personality type feels jealousy. What differs is how they act on it. The system routes through existing mechanics (relationships, coordination, defiance, objections) rather than creating parallel penalty tracks.

Historical anchor: Marshal rivalries were Napoleon's constant headache. Ney and Davout despised each other. Grouchy's inaction at Waterloo while hearing Ney's guns is the quintessential Literal jealousy moment. These weren't failures of skill — they were failures of ego management. That's the player's job.

---

## 1. Trigger: Glory Score

### Glory Tracking (replaces simple win count)

Track a **glory score** per marshal, not raw battle wins. Rolling 5-turn window. Glory captures *magnitude* of achievement — a marshal who won two garrison stomps shouldn't trigger jealousy in one who won a decisive pitched battle.

```
Glory per battle:
  Base:             +1 per victory
  Decisive win:     +1 bonus (casualty ratio >= 2:1 in your favor)
  Territory taken:  +1 bonus (captured a region this battle)
  Outnumbered:      +1 bonus (won when enemy had more troops)
  Garrison stomp:   +0 (defeating a garrison — no glory in that)
```

Each glory event is stored as `(turn_number, glory_points)`. At evaluation, sum points within the 5-turn window.

### Trigger Conditions

```
glory_delta = target.glory_score - self.glory_score

Standard threshold:     delta >= 2
Accelerated threshold:  delta >= 1 (when self.idle_turns >= 3 consecutive)
```

**Literal personality uses a DIFFERENT trigger** — see §3.

### Authority Polarity (FLIPPED from draft v1)

Low authority ACCELERATES jealousy. High authority SUPPRESSES it. This mirrors history — Napoleon's marshals were at each other's throats during the Hundred Days precisely because they were losing. When things go badly, everyone looks for someone to blame.

```
Authority > 70:  Suppresses jealousy entirely (winning cures ego problems)
Authority < 30:  Accelerates jealousy (threshold always delta >= 1, idle >= 2 turns)
Capital threatened (enemy in capital or adjacent): Suppresses (survival overrides pettiness)
```

This creates a historically accurate death spiral: losing breeds infighting, which breeds more losing. The player must actively manage morale WHILE losing.

### Additional Suppression Conditions

Jealousy is suppressed (never fires) when:
- Target marshal is currently broken or retreating
- Source marshal is currently broken or retreating

### Evaluation Timing

Checked at **end of turn** during `advance_turn()`, after battle results are processed and `process_battle_relationships()` has run. This ensures battle outcomes are fully resolved before jealousy evaluation.

---

## 2. Scaled Duration

Duration scales with the glory delta that triggered jealousy. A barely-triggered flare-up is different from a festering wound.

```
duration = 2 + (glory_delta - threshold)
  Minimum: 2 turns
  Maximum: 5 turns

Examples:
  delta=2 (barely triggered at default threshold): 2 turns
  delta=3: 3 turns
  delta=4: 4 turns
  delta=5+: 5 turns (cap)
```

Timer counts down each turn. At 0, jealousy expires (with no resolution surge — timer expiry is NOT the "I showed them" moment). Resolution via action clears immediately regardless of remaining timer.

---

## 3. Personality Expressions

Each personality type expresses jealousy differently. The core output is always a **temporary relationship degradation** (-1 toward the glory target), which flows through existing coordination, objection, and defiance systems automatically. On top of that, each personality has a unique behavioral expression.

### Aggressive (Ney)

**Expression:** Autonomous glory-seeking attack. Hot, loud, dangerous — to enemies AND to your plans.

- **Autonomous attack** against a nearby enemy (glory-seeking target priority — see §7)
- Costs **1 AP** from the player's budget (only fires if AP > 0; if AP = 0, marshal rages but can't act)
- **+15% attack modifier** on solo attacks while jealous (jealousy as fuel — this is INTENDED as a valid strategy, not an exploit)
- **0% coordination** with the jealousy target (refuses to cooperate)
- If no valid attack target exists: just the relationship penalty, no autonomous action
- Autonomous attack is **announced 1 turn in advance** via Morning Dispatch (see §7)

**Resolution:** Win a battle where enemy strength >= 70% of yours (no stomps). Cleared immediately on qualifying victory.

### Cautious (Davout, Drouot)

**Expression:** Withholds full cooperation. Technically present in coordination but doesn't commit full strength. Cold, professional, lasts longer.

- Coordination contribution scaled to **50%** via temporary relationship downgrade (-1)
- No solo bonus — Cautious marshals don't seek glory, they withhold it
- Campaign log flavor: critical reports undermining the rival

**Resolution:** Shared victory with the jealousy target (both marshals participate in the same winning battle). Time alone doesn't fix it — they need proof the other marshal is competent.

### Literal (Grouchy) — DESIGN PENDING

> **Status:** Two candidate designs below. Needs evaluation and selection before implementation.
> The Literal trigger is settled (see below). The EXPRESSION is the open question.

**Trigger (SETTLED):** DIFFERENT from other personalities. Literals don't care about glory — they care about being treated as competent. Literal jealousy triggers when the marshal has been on **HOLD or garrison duty for 3+ consecutive turns** while other same-nation marshals received attack or move orders. They resent being sidelined, not outshone.

**Resolution (SETTLED):** Successfully complete a meaningful strategic order (MOVE_TO reach destination, SUPPORT join ally battle, PURSUE engage target). NOT: HOLD. Timer expiry is a safety valve, not a satisfying resolution.

**Design constraints for expression:**
- NOT a combat stat/number modification
- NOT a binary flag override (like join_combat=False)
- NOT already covered by core Literal mechanics (which handle "follows orders exactly")
- Must create a FELT experience the player notices and adapts to
- Must have a DUALITY (upside AND downside) — not purely punitive
- Must route through existing systems where possible
- Historically resonant with Grouchy at Waterloo

---

#### Candidate A: "The Silent Front" (Communications Blackout)

**Historical anchor:** The failure at Waterloo was information flow, not combat. Napoleon had no idea what was happening around Grouchy. The catastrophe was the gap between what command knew and what was actually happening.

**Expression:** Grouchy withdraws from the reporting network. Still follows orders, still fights at full strength — but stops actively reporting to headquarters.

**Three effects:**
- **Dispatch Omission** — Grouchy's entry removed from Morning Dispatch marshal status. Replaced with: *"No dispatch received from Marshal Grouchy."* Player must check Marshal Management (G key) manually.
- **Intel Degradation** — Grouchy's `marshal_present` skipped in `calculate_visibility()`. His region drops from FULL → PARTIAL. Adjacent regions lose his scouting contribution. Fog thickens around him on the map.
- **Enemy Sighting Suppression** — Enemy forces near Grouchy excluded from dispatch intelligence section unless another source detects them independently.

**Upside:** None (this is the problem).
**Downside:** Blind spot on Grouchy's front. Player may miss enemy movements.

**Concern:** Purely punitive. Makes the already-least-exciting marshal even worse. Aggressive jealousy has a duality (+15% attack but uncontrollable). Cautious jealousy has a duality (still present, just cold). Silent Front Grouchy is just... worse. No interesting decision beyond "give him orders to fix it."

---

#### Candidate B: "The Vindicated Garrison" (Obsessive Competence)

**Historical anchor:** Grouchy's actual pursuit of the Prussians was competent. He found them, engaged them at Wavre, did his job. The catastrophe was that his excellent work on the wrong objective meant he wasn't where Napoleon needed him. The failure was strategic, not tactical.

**Expression:** Jealous Grouchy becomes obsessively good at his current assignment. He throws himself into garrison duty to prove it matters — aggressive scouting, detailed reporting, extra patrols. His sector becomes the best-informed part of the map.

**Three effects:**
- **Intel Enhancement** (`calculate_visibility`) — Grouchy's scouting output increases. Adjacent regions get boosted visibility (PARTIAL → FULL, UNKNOWN → PARTIAL). He's sending out extra patrols, mapping enemy supply lines, tracking movements. The player gets *better* intelligence from Grouchy's sector than anywhere else.
- **Reassignment Dispatch** (popup pattern) — When the player issues a strategic order to move Grouchy away, a dispatch popup appears. Not an objection (Literal never objects) — an intelligence briefing. Grouchy reports what he's found: enemy positions, supply lines, strategic value of his sector. Player acknowledges, order proceeds. But the information makes them *think* about whether pulling him is the right call.
- **Intel Withdrawal** (`calculate_visibility`) — If the player reassigns Grouchy, enhanced intel from his sector immediately drops to normal. Player *feels* the loss. No new system needed; the boost just stops.

**The dilemma:** Grouchy is doing something useful that you didn't ask for. Do you:
- **Leave him** — benefit from enhanced intel, but he stays jealous and relationship penalty persists
- **Pull him out** — resolve jealousy by giving him a real mission, but lose the best intelligence source on the map

**Upside:** Enhanced intel is genuinely valuable. Some players may WANT Grouchy jealous.
**Downside:** Relationship penalty persists. He's "stuck" being excellent at the wrong thing.

**Historical resonance:** Grouchy at Waterloo was excellent at his assignment. The problem was Napoleon needed him elsewhere. Jealous Grouchy recreates this exact dilemma — he's great where he is, but you might need him somewhere else.

**Open question:** Does "visibility level change" count as the kind of stat modification the constraints exclude? It's informational, not combat — he fights exactly the same. But it IS a system value changing.

---

#### Evaluation Criteria for Next Session

When choosing between A and B (or proposing C), evaluate:

1. **Duality test:** Does the expression create a genuine tradeoff, or is it just a penalty?
2. **Decision test:** Does the player face an interesting choice, or just "fix it ASAP"?
3. **Identity test:** Does it feel like GROUCHY, or could any marshal do this?
4. **Parallel test:** Is it as interesting as Aggressive (+15% but uncontrollable) and Cautious (cold but present)?
5. **Implementation test:** Does it route through existing systems cleanly?
6. **Waterloo test:** Does it capture the historical spirit of Grouchy's failure?

---

## 4. Resolution Surge Buff

When jealousy resolves via **action** (not timer expiry), the marshal gets a 1-turn "I showed them" buff. This turns jealousy into a narrative arc with a payoff — not just a penalty to remove, but a story with a conclusion.

| Personality | Surge Buff (1 turn) |
|---|---|
| Aggressive | +10% attack |
| Cautious | +10% defense |
| Literal | PENDING — depends on expression design. Surge should complement whichever candidate is selected. |

---

## 5. Berthier Pre-Warning ("Restlessness")

When glory delta reaches `threshold - 1` (one win away from triggering), add a Morning Dispatch line. For Literal, when HOLD/garrison duration reaches 2 consecutive turns. This gives the player agency to **prevent** jealousy, not just react to it.

**Aggressive/Cautious:**
> *"Berthier notes that Ney has grown restless. He has not seen action while Davout wins laurels. I recommend giving him meaningful orders soon."*

**Literal:**
> *"Berthier notes that Grouchy has been holding position for some time while others receive commands. He may begin to feel... overlooked."*

Berthier closing note priority: Below broken/bankrupt/bleeding treasury, above idle_restless/all-ready.

---

## 6. Jealousy Confrontation Popup

When jealousy fires for the **first time** between two marshals, create a popup event (using the existing objection popup pattern in `executor.py` → `main.py` → Godot).

**Aggressive:**
```
"Sire, Ney has expressed... displeasure about Davout's recent recognition.
 He requests a command worthy of his talents."

[Acknowledge]     — Jealousy proceeds normally. No cost.
[Promise Glory]   — Costs 1 AP. Duration -1 turn. But if marshal doesn't
                    win a qualifying battle within 2 turns, trust -5
                    (broken promise).
[Rebuke]          — Trust -5 immediately. Duration -1 turn. Aggressive
                    won't launch autonomous attack this cycle (respects
                    the Emperor's anger, briefly).
```

**Cautious:**
```
"Sire, Davout has expressed reservations about the recognition afforded
 to Ney. He requests that his contributions be... noted."

[Acknowledge]     — Jealousy proceeds normally. No cost.
[Promise Glory]   — Costs 1 AP. Duration -1 turn. If no shared victory
                    within 2 turns, trust -5.
[Rebuke]          — Trust -5 immediately. Duration -1 turn. No additional
                    mechanical effect (Cautious already internalizes).
```

**Literal:**
```
"Sire, Grouchy has not sent his morning dispatch. Staff report he feels
 his current assignment is... beneath his abilities."

[Acknowledge]     — Jealousy proceeds normally. No cost.
[Reassign]        — Costs 1 AP. Duration -1 turn. If no strategic order
                    issued to Grouchy within 2 turns, trust -5.
[Rebuke]          — Trust -5 immediately. Duration -1 turn. Dispatches
                    resume for 1 turn only (a reluctant compliance before
                    silence returns).
```

Subsequent jealousy triggers between the same pair use the standard popup-free flow (just Morning Dispatch events). Only the FIRST occurrence gets the confrontation choice.

---

## 7. Autonomous Attack Target Priority (Aggressive Only)

When a jealous Aggressive marshal launches an autonomous attack, target selection follows glory-seeking logic — not strategic logic:

```
Priority:
  1. Weakest adjacent enemy (easiest glory — desperate, not smart)
  2. Enemy that the jealousy target recently defeated (steal THEIR glory)
  3. Any adjacent enemy
  4. No target available → no autonomous action (just relationship penalty)

NOT: the strategically optimal target
NOT: the strongest enemy (they want glory, not death)
```

**Advance Warning:** Autonomous attack is announced **1 turn in advance** via Morning Dispatch turn events:

> *"Ney is eyeing the Austrian position at [region]. I cannot guarantee he will wait for orders."*

The player gets 1 turn to redirect with new orders (costs AP). If they don't, the autonomous attack fires next turn. If the player issues ANY order to the jealous marshal (even "hold"), the autonomous attack is cancelled for that cycle (but jealousy persists).

---

## 8. Relationship Integration

Jealousy's primary mechanical output is a temporary relationship degradation (-1 toward the glory target). This cascades through existing systems automatically:

```
Jealousy fires
  → Relationship toward target: -1 (temporary, restored on resolution)
  → This automatically triggers:
     +-- Coordination penalty (via _RELATIONSHIP_SCALING in executor.py)
     |     Professional(0) → Rival(-1): contribution drops from 100% to 50%
     |     Rival(-1) → Hostile(-2): contribution drops to 0%
     +-- SUPPORT objection (via _evaluate_relationship_support in objection_v2.py)
     |     Hostile target = STRONG concern (Aggressive) or MODERATE (Cautious)
     +-- Elevated defiance chance (existing modifiers in defiance.py)
```

**Important:** The relationship change is TEMPORARY. It's restored when jealousy resolves. This distinguishes jealousy (transient emotional state) from genuine relationship degradation (permanent, from battle outcomes). Track the temporary modifier in a separate field from the permanent relationship value.

**Note:** Literal marshals still get the temporary relationship degradation. Even though their expression is informational rather than interpersonal, the resentment affects how they interact with the marshal who's getting all the "real" assignments.

---

## 9. Trust Policy

Jealousy is marshal-vs-marshal, NOT marshal-vs-Napoleon. **No trust changes** on jealousy fire or resolution.

**Exception:** The Confrontation Popup choices (§6) can affect trust as part of the player's explicit decision:
- [Promise Glory] → trust -5 if promise broken (2-turn window)
- [Rebuke] → trust -5 immediately

This keeps trust changes as consequences of player CHOICES, not automatic penalties.

---

## 10. Escalation System

### Escalation Triggers

Escalation activates when:
- Jealousy fires AND current relationship is already **Rival (-1) or worse**
- OR jealousy fires for the **3rd time EVER** between this pair (lifetime count, not windowed)

### Progressive Effects

**1st escalation:** Berthier warning in Morning Dispatch.
> *"Sire, the rivalry between Ney and Davout has become a matter of concern among the general staff. Their cooperation cannot be relied upon."*

**2nd escalation:** Permanent -1 relationship (does NOT restore on jealousy resolution). This feeds into SUPPORT objections and coordination penalties permanently.

**3rd escalation:** Mutual jealousy — if A becomes jealous of B again, B **automatically** becomes jealous of A. Creates the Ney-Davout spiral. The player's only option is to physically separate them (assign to different fronts) or accept permanent friction.

### Escalation Tracking

```python
# Per-marshal, per-target: lifetime list of turn numbers when jealousy fired
jealousy_history: Dict[str, List[int]]  # target_name → [turn_5, turn_8, turn_22]

# Escalation level derived from len(history[target])
# Level 0: count < 3 (or relationship >= Professional)
# Level 1: first escalation trigger
# Level 2: second escalation trigger
# Level 3: mutual jealousy active
```

---

## 11. Surface to Player

### Morning Dispatch

New event types added to dispatch event whitelist:

| Event | When | Message |
|---|---|---|
| `jealousy_restlessness` | Pre-warning (§5) | "Berthier notes that {name} has grown restless..." |
| `jealousy_fired` | Jealousy activates | "Berthier reports that {name} appears envious..." |
| `jealousy_autonomous_warning` | Aggressive advance notice (§7) | "{name} is eyeing the position at {region}..." |
| `jealousy_silent_marshal` | Literal expression (§3) | "No dispatch received from Marshal {name}." |
| `jealousy_escalation` | Escalation triggers (§10) | "The rivalry between {a} and {b} has become..." |
| `jealousy_resolved` | Resolved via action | "{name}'s grievance appears satisfied." |
| `jealousy_surge` | Resolution surge active | "{name} fights with renewed purpose." |

Berthier closing note priority: Below broken/bankrupt/bleeding treasury, above idle_restless/all-ready.

### Campaign Log

New event type `jealousy` added to `CAMPAIGN_LOG_TYPES` under "command" category.

Variants per personality:
- Aggressive: "Ney, envious of Davout's victories, grows restless for glory."
- Cautious: "Davout has grown distant toward Ney. Staff report reduced cooperation."
- Literal: "Grouchy's dispatches have ceased. His front goes dark."
- Escalation: "The rivalry between Ney and Davout has become entrenched."
- Resolution: "Ney's victories have restored his spirits. He fights with renewed vigor."

### Battle Report

If a jealous marshal participated in a battle, Berthier observations (P6c in `battle_report.py`) should note:

- Aggressive in solo attack: "Ney fought with particular ferocity — though one wonders if it was for France or for himself."
- Aggressive with +15% buff visible: "His jealousy made him dangerous. Whether that danger serves us remains to be seen."
- Cautious withheld coordination: "Davout's support was... measured."
- Literal in battle (if they end up fighting): "Grouchy fought competently. His reports, however, remain absent."

### Notifications

New notification type `JEALOUSY_CONFRONTATION` (HIGH priority) for the first-time confrontation popup. Uses existing `NotificationCollector` and popup patterns.

---

## 12. New Marshal Fields

```python
# In marshal.py __init__

# ═══════ JEALOUSY SYSTEM ═══════
self.jealous_of: Optional[str] = None          # target marshal name, or None
self.jealousy_turns_remaining: int = 0          # countdown timer
self.jealousy_relationship_modifier: int = 0    # temporary relationship penalty (restored on clear)
self.jealousy_surge_turns: int = 0              # resolution surge countdown (1 = active)
self.jealousy_confrontation_response: Optional[str] = None  # "acknowledge"/"promise"/"rebuke"/None
self.jealousy_promise_deadline: int = 0         # turn by which promise must be fulfilled
self.jealousy_autonomous_warned: bool = False   # True = advance warning given, attack fires next turn

# Glory tracking
self.glory_events: List[Dict] = []              # [{turn: int, points: int}] — rolling 5-turn window

# Escalation
self.jealousy_history: Dict[str, List[int]] = {}  # target_name → [turn_numbers] lifetime

# Literal-specific
self.consecutive_hold_turns: int = 0            # HOLD/garrison consecutive turn counter
# Additional Literal fields TBD — depends on which expression candidate is selected
```

All fields MUST be added to `to_dict()` and `from_dict()` with `.get()` defaults. Run `test_serialization_enforcement.py` after.

---

## 13. Implementation Outline

### Files to Modify

| File | Changes |
|------|---------|
| `backend/models/marshal.py` | New fields (§12), serialization, `clear_jealousy()` / `get_glory_score()` helpers |
| `backend/models/world_state.py` | Jealousy evaluation in `advance_turn()`, glory window pruning, `calculate_visibility()` changes TBD per Literal design |
| `backend/commands/executor.py` | Autonomous attack trigger (Aggressive), confrontation popup result handling, coordination modifier read, glory event recording after battle |
| `backend/commands/strategic.py` | Track consecutive HOLD turns for Literal trigger |
| `backend/game_logic/relationship.py` | Temporary relationship modifier support (apply/restore) |
| `backend/game_logic/dispatch.py` | Restlessness warning, autonomous attack warning, Literal dispatch changes TBD per design |
| `backend/game_logic/battle_report.py` | Jealousy-aware Berthier observations |
| `backend/campaign_log.py` | `jealousy` event type + formatter variants |
| `backend/notifications.py` | `JEALOUSY_CONFRONTATION` notification type |
| `backend/ai/enemy_ai.py` | Enemy marshals exempt from jealousy evaluation |

### New File

`backend/game_logic/jealousy.py` — Core evaluation logic:
- `evaluate_jealousy(world)` — check all marshal pairs, fire triggers
- `evaluate_literal_jealousy(marshal, world)` — separate Literal trigger logic
- `resolve_jealousy(marshal, world)` — check resolution conditions per personality
- `apply_jealousy(marshal, target, world)` — set fields, degrade relationship, log event
- `clear_jealousy(marshal, world)` — restore relationship, clear fields, apply surge
- `check_escalation(marshal, target, world)` — escalation threshold + mutual trigger
- `get_glory_score(marshal, current_turn)` — sum glory within 5-turn window
- `record_glory(marshal, turn, battle_result)` — add glory event after battle

### Test Coverage

- **Trigger:** Glory delta >= 2, idle acceleration, Literal consecutive HOLD trigger, authority acceleration/suppression
- **Glory scoring:** decisive bonus, territory bonus, outnumbered bonus, garrison stomp = 0
- **Duration scaling:** delta-based duration 2-5 turns
- **Aggressive:** Autonomous attack fires, target priority (weakest first), AP cost, advance warning, +15% solo buff, 0% coordination with target, resolution requires >= 70% strength enemy
- **Cautious:** Coordination withholding via relationship, resolution requires shared victory
- **Literal:** Expression TBD (pending design selection), resolution via strategic order completion, Literal-specific trigger (consecutive HOLD)
- **Confrontation popup:** First-time only, acknowledge/promise/rebuke effects, promise deadline trust penalty
- **Resolution surge:** +10% attack (Aggressive), +10% defense (Cautious), intel surge (Literal), only on action resolution not timer
- **Escalation:** Rival-or-worse trigger, 3rd-lifetime trigger, permanent relationship damage, mutual jealousy spiral
- **Relationship:** Temporary modifier applied/restored correctly, doesn't stack with permanent
- **Pre-warning:** Restlessness dispatch event at threshold-1
- **Serialization:** All new fields round-trip
- **Suppression:** Authority > 70, capital threatened, broken/retreating marshals
- **Edge cases:** Both marshals jealous of each other, jealousy during retreat, marshal jealous of broken marshal, AP = 0 prevents autonomous attack, promise broken trust penalty

---

## 14. What This Spec Does NOT Cover

- **Coalition Trigger** — moved to Phase 8
- **Council command** ("to my tent" active resolution) — deferred to Phase 8 or later
- **Enemy marshal jealousy** — enemy AI marshals are exempt
- **Modding support** — jealousy thresholds/durations could be moddable, but not in initial implementation
- **LLM flavor text** — jealousy events use template strings, not LLM generation
- **Jealousy toward enemy-nation marshals** — explicitly excluded (same-nation only)

---

## 15. Appendix: Literal Jealousy — Ideas Considered

All ideas explored for Grouchy's jealousy expression. Logged for future reference.

### CANDIDATE A: The Silent Front (Communications Blackout)

Grouchy withdraws from the reporting network. Dispatch omission + intel degradation + enemy sighting suppression. Three existing systems affected, no stat changes, no binary overrides. Creates the "Where IS Grouchy?" experience.

**Strengths:** Strongest historical resonance (Waterloo was an information failure). Felt experience (dispatch gap is immediately noticeable). Routes cleanly through dispatch.py, world_state.py, intel filtering.
**Weakness:** Purely punitive — no upside, no dilemma. Makes the least-exciting marshal even worse. Player's only choice is "fix it ASAP."

### CANDIDATE B: The Vindicated Garrison (Obsessive Competence)

Grouchy throws himself into garrison duty to prove it matters. Enhanced intel from his sector (adjacent regions get boosted visibility). Reassignment dispatch popup when player tries to move him. Intel drops back to normal when he leaves.

**Strengths:** Has a duality (enhanced intel vs. relationship cost). Creates a real dilemma (leave him for intel vs. pull him for resolution). Historically resonant (Grouchy was excellent at the wrong thing). Player might WANT him jealous.
**Weakness:** Intel enhancement could be seen as a stat modification (visibility levels change). The "reassignment dispatch" is dangerously close to an objection, which Literals never do.

### REJECTED: Malicious Compliance (draft v1)

SUPPORT with `join_combat=False`, MOVE_TO without fortify, attack without pursuit. Three behaviors that reduce Grouchy's effectiveness through deliberate minimum-effort execution.

**Why rejected:** Overlaps with core Literal identity (which is ALREADY "follows orders exactly"). join_combat is a binary flag override — indistinguishable from a bug to the player. "Malicious compliance" is a defiance variant wearing a different hat. No clear player-facing moment — the effects are hidden until battle results arrive.

### REJECTED: Precision Execution Loss (stat penalty)

Jealous Grouchy loses his +1 all-skills ability. Still follows orders, still fights, but performs at baseline instead of enhanced level.

**Why rejected:** Pure number modification. Player would need to check skill stats to notice. No felt experience — just slightly worse combat results. Boring.

### REJECTED: Immune to Jealousy (draft v1 Option C)

Literal marshals never get jealous. Preserves "reliable, no-drama" identity.

**Why rejected:** Loses the Waterloo fantasy entirely. Makes Literal marshals mechanically boring. Wastes the most historically dramatic personality type.

### CONSIDERED: Order Courier Interception

Grouchy, feeling sidelined, takes it upon himself to "assist" headquarters by carrying dispatches to other marshals — and interprets them with excessive literalism, garbling the intent. Orders to OTHER marshals get distorted when they pass through Grouchy's sector.

**Why shelved:** Breaks character. Marshals are corps commanders, not couriers — Napoleon had Berthier's staff for message delivery. Having Grouchy demote himself to courier duty doesn't fit his pride or his role. Also mechanically unclear: what does "distorted orders" mean in game terms? Would require a new system for order modification that doesn't exist.

**Salvageable kernel:** The idea of Grouchy's sector becoming an information dead zone that affects nearby marshals' awareness IS captured by the Silent Front's intel degradation (adjacent regions lose his scouting contribution).

### CONSIDERED: Hyper-Literal Pathing

When jealous, Grouchy interprets MOVE_TO with extreme literalism — takes the SHORTEST path even through dangerous territory. Normally marshals might path around enemy positions; jealous Grouchy takes the direct route because "the order says move to Belgium, not move safely to Belgium."

**Why shelved:** Interesting tactical consequence but narrow — only affects MOVE_TO orders. Would require new pathfinding logic (current strategic pathing doesn't have a "safe vs. direct" distinction). Risk of frustrating the player with seemingly bugged pathfinding. Could revisit if pathing system gets more sophisticated.

### CONSIDERED: The Formal Protest (Notification Spam)

Grouchy sends formal written protests to Napoleon about being sidelined. Creates persistent notifications that stack if ignored. Each unaddressed protest reduces authority by -1 (Grouchy undermines Napoleon's image among staff).

**Why shelved:** Historically authentic (Napoleon's correspondence IS full of petulant marshal letters). But mechanically it's just a notification annoyance + number penalty (authority drain). Doesn't create the visceral "blind spot" feeling. Could work as an ESCALATION effect layered on top of the Silent Front — if Grouchy stays jealous long enough, the protests start arriving. Worth revisiting.

### CONSIDERED: The Petition Chain (Multi-Marshal Poison)

Grouchy writes to OTHER marshals complaining about his assignment. Creates relationship degradation with MULTIPLE marshals, not just the jealousy target. Office politics — the passive-aggressive letter campaign.

**Why shelved:** Thematically strong (marshals DID politick behind Napoleon's back — Bernadotte was infamous for this). But spreads jealousy effects too wide for a first implementation. The relationship system handles pair-wise interactions well; poisoning multiple relationships simultaneously would need careful balancing. Better suited to BALANCED personality (Bernadotte) when that's implemented in the 1805 expansion. Filed for future use.

### CONSIDERED: The Over-Reporter (Noise Flood)

Instead of going silent, jealous Grouchy becomes ANNOYING — sends excessive pedantic dispatches about trivial matters. "A patrol of 12 enemy cavalry spotted 3 leagues east." "Supply wagon arrived with 40 barrels of flour." The Morning Dispatch gets cluttered with noise, burying important intel.

**Why shelved:** Funny and historically plausible (some officers DID flood HQ with trivia). But it's the opposite direction from the Waterloo parallel. Grouchy's failure was SILENCE, not noise. Also mechanically tricky — cluttering the dispatch UI with fake entries could frustrate more than engage. The concept of "important intel buried in noise" is interesting but better suited to a future fog-of-war enhancement than a jealousy expression.

### CONSIDERED: Rigid Re-positioning

If jealous Grouchy's region is attacked and he's pushed back via forced retreat, he RETURNS to his original hold position next turn instead of staying where he retreated to. "My orders say hold THIS region." Relentless literal compliance even after tactical displacement.

**Why shelved:** Interesting niche interaction but too narrow — only matters when Grouchy is attacked AND retreats, which may never happen during a jealousy window. Also mechanically close to a binary override (auto-return flag). The forced retreat system doesn't currently support auto-return behavior, so this would need new pathfinding and recovery logic for one edge case.

---

## 16. Reference: Existing System Integration Points

| System | How Jealousy Connects |
|--------|----------------------|
| **Personality** | Determines expression: Aggressive=autonomous attack, Cautious=withholds, Literal=silent front |
| **Relationships** | Primary output: temporary -1 toward glory target |
| **Coordination** | Downstream: degraded relationship reduces coordination via `_RELATIONSHIP_SCALING` |
| **Objection V2** | Downstream: degraded relationship triggers SUPPORT objections via `_evaluate_relationship_support()` |
| **Defiance** | Downstream: degraded relationship elevates defiance chance |
| **Authority** | Polarity: > 70 suppresses, < 30 accelerates |
| **Trust** | No automatic impact. Confrontation popup choices can affect trust. |
| **Fog of War** | Literal expression TBD: may boost or degrade visibility depending on candidate selected |
| **Morning Dispatch** | Pre-warnings, fire events, autonomous warnings, dispatch omission (Literal), resolution events |
| **Campaign Log** | Jealousy events as "command" category entries |
| **Notifications** | Confrontation popup (first-time only, HIGH priority) |
| **Strategic Orders** | Literal trigger (consecutive HOLD tracking), Literal resolution (order completion) |
| **Battle Report** | Post-battle observations note jealous behavior |
