# COALITION_SPEC.md — v1.1

> **Companion to:** DIPLOMACY_SPEC.md v2.2
> **Status:** DRAFT — Awaiting design gate approval
> **Scope:** Threat accumulation, coalition formation, coalition structure, coalition AI, coalition breaking, dissolution
> **Design principle:** Threat from success + diplomatic windows + coalition splitting = the Napoleonic strategic puzzle

---

## §1. Overview & Design Principles

### §1a. The Problem

Without coalitions, a skilled player conquers nations sequentially. Historically, every French victory *increased* the likelihood of a larger alliance forming. The game needs this pressure curve: **the better you play, the harder Europe pushes back.**

### §1b. Core Loop

```
Player wins battles / captures territory / annexes land
  → Threat rises
    → Talleyrand warns ("the courts of Europe grow restless")
      → Player chooses: moderate expansion OR push harder
        → If threat hits 60: Coalition Brewing (3-turn warning)
          → Player can defuse diplomatically (spend DP, offer treaties)
          → Or push through and face coordinated war
            → Coalition forms → player must break it (defeat in detail, diplomacy, economic pressure)
              → Coalition broken → threat decays → cycle resets
```

### §1c. Design Principles

| Principle | Application |
|-----------|-------------|
| Telegraphed & player-controlled | Threat shown openly. Thresholds documented. No hidden rolls. |
| Commanding personalities, not pieces | Talleyrand warns about coalition risk. Leader personality shapes coalition posture. |
| Building Blocks | Coalition AI uses same executor as player. No special combat rules. |
| Deterministic rules engine | All threat math is `int()`, all thresholds are fixed, all formulas are explicit. |
| LLM for flavor only | Talleyrand's warnings are template-driven. Coalition names are flavor. Mechanics are deterministic. |
| Emergent escalation | No coded "2nd coalition is harder." Escalation emerges from accumulated threat, broken treaties, hostile relations. |

---

## §2. Threat Accumulation

### §2a. Threat Source Table

Threat is tracked on `WorldState.threat_level`, clamped `int(0–100)`.

| Trigger | Threat | When Applied | Historical Basis |
|---------|--------|--------------|------------------|
| Declare war | +20 | On declaration (DIPLOMACY_SPEC §5c) | Direct aggression alarms all courts |
| Capture enemy capital | +15 | When capital region controller changes to France | Ulm, Vienna, Berlin — each shocked Europe |
| Vassalize a nation (treaty) | +5 | On treaty vassalage acceptance (DIPLOMACY_SPEC §8a) | Willing client states cause less alarm |
| Vassalize a nation (conquest) | +25 | On military vassalage (DIPLOMACY_SPEC §8a) | Forced subjugation terrifies all courts |
| Win any battle | +3 | On `resolve_combat` where France wins | Military dominance signals threat |
| Win decisive battle | +5 | Additional, when casualty ratio > 2:1 AND total casualties > 10,000 (per DIPLOMACY_SPEC §6e) | Austerlitz, Jena — decisive victories escalate fear |
| Annex territory in peace deal | +8 per region | On peace treaty acceptance that transfers regions | Treaty of Tilsit drove the Fifth Coalition |
| Control >60% of regions (12+) | +1/turn | During `advance_turn` | Continental dominance |
| Control >70% of regions (14+) | +2/turn | During `advance_turn` (replaces +1) | Near-total hegemony |
| Control >80% of regions (16+) | +3/turn | During `advance_turn` (replaces +2) | Empire at its zenith |

**Notes:**
- "Win any battle" and "Win decisive battle" stack: a decisive victory = +3 + +5 = **+8 total**.
- "Capture enemy capital" stacks with "Win any battle" if a battle was fought for the capital.
- Region control % uses `len(france_controlled) / len(all_regions)`. France starts with 8/19 = 42%.
- All values are `int()`. No fractional threat.
- **Alliance formation does NOT generate threat.** Only aggressive actions (war, conquest, vassalization, battles, annexation) raise threat. Defensive alliances formed by other nations are their response to threat, not a source of it.

### §2b. Threat Reduction Table

| Trigger | Threat | When Applied |
|---------|--------|--------------|
| Per-turn baseline decay | -1/turn | During `advance_turn`, always |
| Per-nation peace bonus | -1/turn per nation at peace with France | During `advance_turn` |
| Decay cap | max -3/turn total | Decay never exceeds -3 in a single turn |
| Release vassal voluntarily | -8 | On voluntary release (not rebellion) |
| Return territory in peace deal | -5 per region returned | On peace treaty that returns regions |
| Diplomatic concession (generous peace) | -3 | When France offers peace terms below war score entitlement |
| Continental System active | -1/turn | While `continental_system_members` has 2+ nations (DIPLOMACY_SPEC §9c) |

**Decay formula:**
```python
peace_nations = [n for n in ALL_NATIONS if n != france  # Exclude self!
                 and get_diplomatic_state(france, n) in ("PEACE", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE")
                 and n not in vassals]
raw_decay = 1 + len(peace_nations)  # 1 base + 1 per peaceful nation
decay = min(raw_decay, 3)  # Cap at 3
# Continental System bonus (separate, not subject to cap)
if len(world.continental_system_members) >= 2:
    decay += 1
threat_level = max(0, threat_level - decay + threat_gained_this_turn)
```

**IMPORTANT:** `ALL_NATIONS` must exclude France from the peace nation count. The `get_diplomatic_state()` default for a self-pair would return "PEACE" and incorrectly inflate decay.

**Starting game:** France at peace with Austria + Saxony, at war with Britain + Prussia.
Decay = 1 + 2 = 3 (at cap). Net: -3/turn when no events occur.

### §2c. Threat Pacing (Worked Example)

> **TUNING NOTE:** All threat values are balance-tunable. The following simulation validates pacing for a 25-30 turn aggressive game. If playtesting shows coalitions form too early or too late, adjust the source table (§2a) rather than the thresholds (§3a).

**Aggressive player scenario (declares war on Austria turn 8):**

| Turn | Event | Threat Gained | Decay | Net Threat |
|------|-------|---------------|-------|------------|
| 1 | Win battle vs Prussia | +3 | -3 | 0 |
| 2 | Win battle vs Britain | +3 | -3 | 0 |
| 3 | Decisive victory at Waterloo | +8 | -3 | 5 |
| 4 | Capture Berlin (capital) | +15+3 | -3 | 20 |
| 5 | Advance, no battle | 0 | -3 | 17 |
| 6 | Win battle | +3 | -3 | 17 |
| 7 | Vassalize Saxony (conquest) | +25 | -2 | 40 |
| 8 | Declare war on Austria | +20 | -1 | 59 |
| 9 | Capture Vienna (capital) | +15+3 | -1 | 76 |
| 10 | — | — | — | **BREWING (turn 9)** |

Coalition brewing starts turn 9 (threat crossed 60 on turn 8, but at 59 — actually crosses 60 on turn 9 capture of Vienna at 76). Player has 3 turns to defuse. If they don't, coalition declares turn 12. Note: with conquest vassalization (+25 instead of +10), threat accumulates faster — this creates tighter pressure on aggressive players who conquer rather than negotiate. Treaty vassalization (+5) would delay brewing by several turns.

> **Correction from v1.0:** Vassalization threat now uses DIPLOMACY_SPEC §8a values (+5 treaty, +25 conquest) instead of flat +10. Worked example uses conquest path. Treaty vassalization of Saxony (+5 instead of +25) would yield net threat 20 at turn 7, 39 at turn 8, 56 at turn 9 — brewing wouldn't start until turn 10-11, rewarding diplomatic over military vassalization.

**Cautious player scenario (never declares war on Austria):**

| Turn | Event | Threat Gained | Decay | Net Threat |
|------|-------|---------------|-------|------------|
| 1-5 | Battles vs Britain/Prussia | +3 avg/turn | -3 | 0 |
| 6 | Capture Berlin | +18 | -3 | 15 |
| 10 | Peace with Prussia (annex Rhineland) | +8 | -3 | ~14 |
| 15 | Ongoing war with Britain only | +3 occasional | -3 | ~12 |
| 20 | Stalemate | 0 | -3 | ~5 |

Cautious play keeps threat well below 40. **Coalition never forms.** This is correct — if France isn't steamrolling, Europe doesn't unite.

---

## §3. Coalition Formation

### §3a. Threshold Tiers

| Threat Level | Tier | Effect |
|--------------|------|--------|
| **0–29** | Calm | No diplomatic concern. Threat not shown in top bar. |
| **30–39** | Tension | Threat indicator appears in top bar (amber). Talleyrand may comment. No mechanical effect. |
| **40–59** | Murmurs | Morning Dispatch includes diplomatic tension flavor. Talleyrand advisory warns "the courts grow restless." Notification: "European courts are concerned." |
| **60–79** | Brewing | **3-turn countdown begins.** Specific qualifying nations listed. Player can defuse. See §3c. |
| **80+** | Instant Declaration | Coalition declares **immediately**, skipping remaining countdown. See §3d. |

### §3b. Qualifying Nation Check

A nation qualifies for coalition membership if ALL conditions are met:

```python
def qualifies_for_coalition(nation, france, world):
    if nation == france:
        return False
    relation = world.get_relation(france, nation)
    is_vassal = nation in world.vassals
    already_at_war = get_diplomatic_state(france, nation) == "WAR"
    return relation < -10 and not is_vassal and not already_at_war
```

**At game start:** Austria (relation -30) qualifies. Saxony (+40) does not. Britain/Prussia already at war — they auto-join the coalition structure (§3e) but don't trigger formation.

**Minimum coalition size:** At least **1 qualifying nation** must be pulled in. A coalition cannot form if the only hostile nations are already at war with France — they're just individual belligerents, not a coordinated coalition.

### §3c. Brewing Window (Threat 60–79)

When threat first reaches 60:

1. **Snapshot qualifying nations.** Record which nations meet the check (§3b) at this moment.
2. **Start 3-turn countdown.** Track `coalition_brewing_turns_remaining` on WorldState.
3. **Notify player:** Persistent EU4-style notification: "A coalition is brewing against France. [Nation list]. 3 turns remain."
4. **Morning Dispatch:** "Your Majesty, diplomatic dispatches confirm that [nations] are consulting on joint action against France."
5. **Talleyrand advisory:** Proactive conversation offering to defuse ("Shall I approach [weakest member] with terms?").

**Each subsequent turn during brewing:**
- Decrement countdown.
- Re-check qualifying nations (nations may leave if relation improves above -10).
- Update notification with remaining turns and current member list.
- If qualifying nations drops to **zero**, cancel brewing. Notification: "The coalition effort has collapsed."

**Momentum rule:** Once brewing starts, it continues even if threat drops below 60. It ONLY cancels if:
- Threat drops below **40**, OR
- Zero qualifying nations remain, OR
- Player successfully defuses all potential members diplomatically (relation above -10 for all)

**On countdown expiry (0 turns remaining):** Coalition declares (§3e).

**Processing order (CRITICAL):** During `advance_turn()`, threat processing runs in this order:
1. Apply all threat sources from this turn's actions (battles, captures, vassalization).
2. Apply threat decay (§2b formula).
3. Check vassalization/diplomatic changes that affect qualifying nations.
4. Re-check qualifying nations list.
5. If brewing active: decrement countdown. If countdown = 0 AND qualifying nations > 0 AND threat ≥ 40 → declare. If threat < 40 OR qualifying nations = 0 → cancel.
6. If NOT brewing: check if threat ≥ 60 → start brewing. If threat ≥ 80 → instant declaration.

This order means: decay applies BEFORE threshold checks. If decay brings threat from 62 to 59, but momentum rule applies (only cancels below 40), brewing continues. If decay brings threat from 42 to 39, brewing cancels.

### §3d. Instant Declaration (Threat 80+)

If threat reaches 80 at any point (even during an existing brewing window):
- **Overrides active brewing** — skip remaining countdown, cancel brewing state.
- Coalition declares immediately.
- Talleyrand reaction: "It is too late, Sire. All of Europe has turned against us." (If he warned previously and was ignored.)
- Implementation: check instant threshold (step 6 in §3c) AFTER checking brewing (step 5). If brewing countdown just expired AND threat ≥ 80, the declaration happens via step 5 — step 6 is a fallback for when brewing wasn't active.

### §3e. Coalition Declaration

When a coalition declares (either countdown expiry or instant):

1. **Identify coalition members:**
   - All qualifying nations from §3b → enter WAR with France simultaneously.
   - All nations already at war with France → join the coalition structure automatically.
   - Vassals are excluded (they fight for France, unless they rebel).

2. **Apply diplomatic penalties:**
   - Each new war declaration: relation -30 with France (standard, per DIPLOMACY_SPEC §5c).
   - France does NOT pay the +20 threat per declaration (these are defensive wars against France).
   - Each new belligerent's relation with other coalition members: +10 ("united cause").

3. **Select coalition leader** (§4a).

4. **Set strategic posture** (§4c).

5. **Assign coalition ID:** `coalition_[turn_number]` (e.g., `coalition_12`). Used for tracking.

6. **UI events:**
   - **Dramatic popup:** "THE COALITION OF [LEADER]" — lists all members, their military strength, and the coalition's strategic posture.
   - **Morning Dispatch (next turn):** Full briefing on coalition composition and threat assessment.
   - **Notification:** Persistent: "Coalition active: [members]. Leader: [nation]."

7. **Talleyrand reaction** (varies by prior interaction):
   - If warned and ignored: "I counseled moderation, Sire. Now we face the consequences."
   - If warned and player tried to defuse but failed: "We tried, Sire. It was not enough."
   - If never warned (threat spiked past 60 to 80 instantly): "This is... unexpected. We must act swiftly."

### §3f. Coalition Naming (Flavor)

Coalitions are named after their leader: **"The Coalition of [Leader Nation]"**.

If Britain is leader: "The British Coalition." If Austria: "The Austrian Coalition."

For the second+ coalition in a game, append a numeral: "The Second Austrian Coalition."

Track `coalition_count` on WorldState for numbering.

---

## §4. Coalition Structure — Option B: Leader Sets Strategy

### §4a. Leader Selection

When a coalition forms, the leader is the member with the highest **leadership score**:

```python
def coalition_leadership_score(nation, world):
    military = sum(m.strength for m in world.marshals.values()
                   if m.nation == nation and m.strength > 0) // 1000  # In thousands!
    hostility = abs(world.get_nation_relation("France", nation))
    authority = world.nation_authority.get(nation, 60)
    return int(military + hostility + authority)
```

**Components (all normalized to similar scale, ~0-100 each):**
- **Military strength:** Total troop count in thousands (`// 1000`). Range: 0-100+.
- **Hostility:** Absolute value of relation to France (more hostile = more motivated to lead). Range: 0-100.
- **Authority:** Nation's internal authority score (DIPLOMACY_SPEC §13). Range: 0-100.

**Tiebreaker:** If scores are equal, the nation with more marshals leads. If still tied, alphabetical.

**At game start (if coalition formed turn 1, hypothetically):**
- Britain: 76 + 80 + 60 = **216**. Prussia: 72 + 60 + 60 = **192**. Austria: 60 + 30 + 60 = **150**.
- Britain leads. Historically correct — Britain financed and organized most coalitions.

### §4b. Leader Transition

If the leader signs a **separate peace** with France:

1. Leadership passes to the member with the next highest leadership score.
2. Recalculate scores at time of transition (military strength may have changed).
3. New leader sets new strategic posture (§4c).
4. Notification: "[Old leader] has left the coalition. [New leader] now leads the [Coalition Name]."
5. Coalition morale penalty: -5 relation between remaining members ("the alliance frays").

If no valid successor exists (< 2 members), the coalition dissolves (§7).

### §4c. Strategic Posture

**Coalition war score** is the weighted average of individual member war scores against France, weighted by each member's current army size (total troops across all marshals). Formula:

```
coalition_war_score = sum(war_score[member|France] * army_size[member] for member in members) // sum(army_size[member] for member in members)
```

If no member is at war with France (shouldn't happen in an active coalition, but defensive), coalition war score = 0. All values are `int()`.

The coalition leader determines the coalition's **strategic posture**, reassessed each turn during the enemy AI phase. The posture biases AI decision-making for all coalition members.

| Posture | Condition | AI Effect |
|---------|-----------|-----------|
| **Aggressive Advance** | Coalition war score > +10 OR leader is Aggressive/Reckless personality | Coalition marshals prioritize moving toward French-controlled territory. Attack priority (P2-P4) boosted by +15 score. |
| **Defensive Containment** | Coalition war score between -10 and +10 | Coalition marshals prioritize holding current positions and counterattacking. Defense priority (P5-P6) boosted by +10. |
| **Cautious Retreat** | Coalition war score < -10 AND leader is Cautious/Professional personality | Coalition marshals avoid risky engagements. Retreat threshold raised. Movement prioritizes own territory. |

**Leader personality override:**
- An Aggressive leader maintains **Aggressive Advance** even at war score -10 to -20 (switches to Cautious Retreat only below -20).
- A Cautious leader switches to **Defensive Containment** even at war score +10 (never reaches Aggressive Advance unless war score > +30).
- Other personalities use the default thresholds.

**Posture is advisory, not binding.** Individual marshal AI still filters through personality. A cautious Austrian marshal in an Aggressive Advance coalition will advance more slowly than a reckless Prussian. The posture adjusts priority *scores*, not priority *order*.

### §4d. Coalition Coordination Bonus

While a coalition is active, all coalition members receive:

- **Adjacency scoring boost:** P4.77 ally adjacency bonus applies across ALL coalition nations (already implemented in `enemy_ai.py` — the TODO-1805 `is_ally` check will be updated to use formal coalition membership instead of the current "not player" hack).
- **No additional mechanical bonuses.** Coalition strength comes from *numbers*, not magic buffs. This preserves Building Blocks: same combat rules for everyone.

### §4e. British Subsidy (Leader-Specific)

If **Britain** is a coalition member (regardless of leadership), the British subsidy mechanic from DIPLOMACY_SPEC §9c activates:

- Britain allocates **200 gold/turn** to the coalition partner with the lowest relation to Britain (minimum relation > -20, per DIPLOMACY_SPEC §9c).
- Effect: +5 relation/turn with that partner (Britain's wealth IS its diplomatic tool).
- No DP cost. Passive AI behavior.
- Requires Britain to have gold > 500.
- Player can counter via Continental System (reduces British naval income) or military conquest (reduces British holdings).

This is not a coalition-specific mechanic — it's an existing DIPLOMACY_SPEC feature that naturally activates during coalition wars. **Note:** The recipient is chosen by lowest relation to Britain, not lowest gold reserves — Britain subsidizes to strengthen political bonds, not just fill treasuries.

**Implementation session:** Session 7 (Coalition). British subsidy is implemented alongside coalition logic since coalitions are the primary context where subsidies matter.

---

## §5. Coalition AI Behavior

### §5a. No Shared Fog of War

**Coalition members do NOT share fog of war.** Each nation sees only what its own marshals and intel sources reveal.

**Rationale:** Historical coalitions had terrible intelligence sharing. At Austerlitz (1805), Kutuzov didn't know Mack had surrendered at Ulm. Napoleon's ability to defeat enemies in detail by exploiting poor coalition coordination is a core strategic element.

**What coalition members DO know:** The positions of allied marshals (their own coalition partners). This is natural — they're on the same side and would communicate general positions even if specific enemy intelligence isn't shared.

**Implementation:** The existing `enemy_ai.py` already handles this — `_get_ally_adjacency_bonus()` uses coalition marshal positions for scoring without requiring fog data.

### §5b. Convergence Bias

During a coalition war, AI strategic movement (P7) receives a **convergence bias** toward French-controlled territory:

```python
# During coalition war, add bias toward regions adjacent to French territory
if is_coalition_active and marshal.nation in coalition_members:
    for candidate_region in reachable_regions:
        if any(adj in french_regions for adj in candidate_region.adjacent_regions):
            score += 8  # Convergence bias
```

This makes coalition armies naturally advance toward France from multiple directions — the historical coalition strategy — without requiring explicit coordination.

**Posture modifier:**
- Aggressive Advance: convergence bias +12 (instead of +8)
- Defensive Containment: convergence bias +4
- Cautious Retreat: convergence bias 0 (no advance)

### §5c. Historical Friction

Coalition members with **low mutual relation** coordinate poorly:

```python
def get_coalition_friction(nation_a, nation_b, world):
    """Reduces adjacency bonus between coalition members who don't like each other."""
    mutual_relation = world.get_relation(nation_a, nation_b)
    if mutual_relation >= 30:
        return 1.0   # Full coordination
    elif mutual_relation >= 0:
        return 0.75   # Moderate friction
    elif mutual_relation >= -20:
        return 0.5    # Significant friction
    else:
        return 0.25   # Near-hostile "allies"
```

Applied as a multiplier to the P4.77 adjacency bonus when the adjacent ally is from a different coalition nation. Same-nation allies always get full bonus. **Golden Rule #2:** The result of `int(adjacency_bonus * friction)` must be used — friction returns float, final value must be int() before reaching Godot.

**Example:** Austria (relation +30 with Prussia) gets full adjacency bonus near Prussian marshals. But if Austria's relation with Prussia drops to -10 (perhaps France diplomatically drove a wedge), the bonus is halved. This rewards diplomatic play against the coalition.

### §5d. Building Blocks Compliance

Coalition AI uses the **same executor** as player and individual AI. No special combat rules, no bonus damage, no hidden advantages. The coalition's threat comes from:
1. More armies on the map (numbers)
2. Convergence bias (strategic coordination)
3. Adjacency scoring (tactical positioning)

All of which use existing systems.

**Bilateral wars with non-France nations:** Coalition members may have pre-existing bilateral wars or diplomatic states with non-coalition nations (e.g., Austria at war with Saxony). These are **unaffected** by coalition membership — the coalition is specifically anti-France. Pre-existing wars continue independently. Coalition strategic posture only affects movement decisions against French-controlled territory.

---

## §6. Coalition Breaking

### §6a. Separate Peace (Primary Method)

Individual coalition members can be peaced out through standard DIPLOMACY_SPEC bilateral diplomacy:

1. **Player initiates:** "Talleyrand, propose peace to Austria" (2 DP).
2. **Acceptance formula** (DIPLOMACY_SPEC §6) applies normally, with one modifier:
   - **Coalition loyalty penalty:** -15 to acceptance score while in an active coalition. Members are reluctant to break ranks.
   - This penalty decreases as the member's war exhaustion rises: `penalty = min(-15 + war_exhaustion // 10, 0)`. A battered Austria with high war exhaustion becomes increasingly willing to negotiate. At 0 exhaustion: penalty = -15. At 100 exhaustion: penalty = -5. At 150+: penalty = 0.
3. **If accepted:** Nation leaves coalition. Relation with remaining coalition members: -15 ("betrayal").
4. **Coalition persistence check:** If < 2 members remain, coalition dissolves (§7).

### §6b. Decisive Victory Impact

When France wins a **decisive battle** (casualty ratio > 2:1, total casualties > 10000) against a coalition member:

- That member's **war exhaustion** increases by +15 (standard battle impact — no additional shock bonus for the defeated member; the defeat itself is the penalty).
- All OTHER coalition members: +5 war exhaustion ("our allies are being crushed").
- Coalition leader reassesses posture (§4c) — may shift from Aggressive to Defensive.

This creates the Austerlitz dynamic: one crushing victory doesn't just beat the army in front of you — it demoralizes the entire coalition.

### §6c. Diplomatic Wedge

Talleyrand can specifically target coalition members for diplomatic outreach:

- **Advisory suggestion:** "Austria is the weakest link. Their war exhaustion is high and their army is battered. Shall I approach Metternich?"
- **Mechanic:** Standard proposal (2 DP) with the coalition loyalty penalty (§6a).
- **Bonus:** If the target member's relation with the coalition leader is below +10, the coalition loyalty penalty is halved (-7 instead of -15). Disgruntled members are easier to peel off.

### §6d. Continental System (Economic Pressure)

If France activates the Continental System (DIPLOMACY_SPEC mechanic):

- Britain's gold income is reduced (per DIPLOMACY_SPEC §9c).
- If Britain's gold drops below 500, British subsidies (§4e) stop.
- Without subsidies, coalition members with low gold reserves face attrition and manpower issues.
- Threat decay bonus: -1/turn while Continental System has 2+ members (§2b).

This is a slow-burn coalition weakener, not an instant fix. It takes multiple turns to starve the coalition of British money.

### §6e. Vassal Cascade Link

Per DIPLOMACY_SPEC §8d: when France's war score drops below -30 against ANY coalition member, the vassal defection cascade fires. This is the **Leipzig moment** — the empire crumbles from within while facing external pressure.

The coalition doesn't directly cause the cascade, but losing a coalition war makes it highly likely. The two systems create a dramatic feedback loop:
1. Coalition forms → multiple fronts → France loses battles → war score drops.
2. War score < -30 → vassal cascade → France loses territory → threat drops → but also loses strength.
3. Weakened France → coalition pushes harder → more losses → more defections.

This is the historical trajectory from 1813 to 1814. It should feel inevitable if the player is losing, and avoidable if the player is winning.

---

## §7. Coalition Dissolution

### §7a. Dissolution Triggers

A coalition dissolves when ANY of these conditions is met:

| Trigger | Effect |
|---------|--------|
| **< 2 members remain** | Last member is just "at war," not in a coalition. Coordination bonuses end. |
| **All members sign peace** | Coalition has no belligerents. Dissolves immediately. |
| **Threat drops below 20** | Europe no longer perceives France as a threat. Remaining members may continue individual wars but lose coalition structure. |

**Note:** Threat dropping below 20 during an active coalition war is rare (France would need to lose significant territory). This is a safety valve, not a primary dissolution path.

### §7b. Post-Coalition Effects

When a coalition dissolves:

1. **Coalition coordination bonuses end.** P4.77 reverts to same-nation-only adjacency scoring.
2. **Convergence bias ends.** AI returns to individual nation priorities.
3. **Threat does NOT reset.** It continues to decay naturally per §2b.
4. **Relations persist.** All war/peace states from the coalition remain. Nations at war with France are still at war — they just lose coalition coordination.
5. **"Coalition dissolved" notification.** One-time notification + Morning Dispatch entry.

### §7c. Cooldown

After a coalition dissolves, a **5-turn cooldown** begins before a new coalition can form. This prevents:
- Instant re-coalition after peacing out members.
- Cheese where the player peace-then-war cycles to keep resetting the coalition.

Track `coalition_cooldown` on WorldState. Decrement each turn. New brewing cannot start while cooldown > 0.

**Exception:** If threat reaches **90+** during cooldown, the cooldown is overridden and a new coalition forms immediately. This represents "France has gone too far — even recently-burned nations re-mobilize."

---

## §8. Talleyrand Integration

### §8a. Pre-Coalition Warnings

Talleyrand provides escalating warnings based on threat tier:

| Threat Tier | Talleyrand Behavior |
|-------------|---------------------|
| 30–39 (Tension) | Passive observation in advisory: "The courts are... uneasy, Sire." |
| 40–59 (Murmurs) | Proactive advisory conversation: "Your Majesty, I must speak frankly about the diplomatic climate." Offers concrete suggestions (improve relations, offer concessions). |
| 60+ (Brewing) | STRONG concern: "A coalition is forming. We have [X] turns to prevent it." Suggests specific diplomatic actions targeting the weakest qualifying nation. |

### §8b. During Coalition

Once a coalition is active, Talleyrand's advisory shifts to strategic counsel:

- **Identify weak links:** "Austria's war exhaustion is mounting. They may be amenable to separate terms."
- **Assess leader:** "Britain leads this coalition from across the Channel. Their gold finances the armies we face. The Continental System would strike at the root."
- **Recommend targets:** "If we can defeat Prussia decisively, the coalition's resolve will waver."
- **Track momentum:** "The coalition's advance has stalled. Now is the time to propose terms — from a position of strength."

### §8c. Post-Coalition Counsel

After a coalition dissolves (via French victory):

- **If player won through military dominance:** "A triumph, Sire. But I counsel moderation in the peace terms. Harsh demands breed the next coalition."
- **If player won through diplomacy (split the coalition):** "Divide et impera — the oldest strategy, and still the finest."
- **If coalition dissolved due to low threat:** "The danger has passed. For now."

### §8d. Template Slots Required

New template categories for `diplomatic_templates.py`:

| Category | Slot | Example |
|----------|------|---------|
| `coalition_murmur` | `{threat_level}`, `{hostile_nations}` | "At threat {threat_level}, the courts of {hostile_nations} grow restless." |
| `coalition_brewing` | `{qualifying_nations}`, `{turns_remaining}` | "{qualifying_nations} are forming a coalition. {turns_remaining} turns remain." |
| `coalition_declared` | `{coalition_name}`, `{member_list}`, `{leader}` | "The {coalition_name} has declared against us. {leader} leads {member_list}." |
| `coalition_member_weak` | `{nation}`, `{war_exhaustion}` | "{nation}'s resolve is faltering. War exhaustion: {war_exhaustion}." |
| `coalition_advice_split` | `{target_nation}` | "I recommend approaching {target_nation} with terms. They are the weak link." |
| `coalition_dissolved` | `{coalition_name}` | "The {coalition_name} has collapsed. A moment of respite." |
| `coalition_harsh_warning` | `{threat_increase}` | "These terms will add {threat_increase} to our threat. Another coalition may follow." |

---

## §9. UI & Feedback

### §9a. Threat Display

**Top Bar** (per DIPLOMACY_SPEC §10a):
- Threat 0–29: Not shown.
- Threat 30–59: Amber indicator: `Threat: 45`.
- Threat 60+: Red indicator: `THREAT: 72 [!]`.
- During brewing: Red pulsing: `COALITION BREWING: 2 turns`.

**Diplomatic Ledger Tab 3** (Threat & Coalition):
- Threat meter: 0–100 bar with color zones (green/amber/red).
- Threat breakdown: table showing each source and its contribution this turn.
- Qualifying nations list: which nations would join a coalition right now.
- Coalition status: "No coalition" / "Brewing (X turns)" / "Active: [name]".
- Active coalition details: member list, leader, posture, war exhaustion per member.

### §9b. Notifications

| Event | Type | Persistence |
|-------|------|-------------|
| Threat reaches 30 | Info | Dismissible |
| Threat reaches 40 (Murmurs) | Warning | Persistent until threat < 30 |
| Coalition Brewing starts | Alert | Persistent with countdown, updates each turn |
| Coalition Declared | Critical | Persistent until dismissed, triggers popup |
| Coalition member peaced out | Info | Dismissible |
| Coalition dissolved | Info | Dismissible |
| Cooldown ended | Info | Dismissible ("A new coalition may form") |

### §9c. Morning Dispatch Integration

Morning Dispatch coalition section (added to `dispatch.py`):

```
=== DIPLOMATIC SITUATION ===

Threat Level: 52 (Murmurs)
- Recent battle victories: +6
- Capital capture (Berlin): +15
- Decay: -3

Austria and Saxony remain at peace, but Austrian hostility (-30) places
them within coalition range. Talleyrand advises diplomatic outreach.
```

During active coalition:
```
=== THE BRITISH COALITION (Active — Turn 3) ===

Leader: Britain (Aggressive Advance)
Members: Britain, Prussia, Austria
- Britain: War exhaustion 12, Gold 2400
- Prussia: War exhaustion 28, Strength 45k
- Austria: War exhaustion 8, Strength 52k

Talleyrand's assessment: "Prussia is battered. A generous peace offer
may separate them from the coalition."
```

### §9d. Coalition Declaration Popup

Full-screen dramatic popup (same pattern as defiance confrontation popups):

```
╔══════════════════════════════════════════╗
║                                          ║
║      THE COALITION OF BRITAIN            ║
║                                          ║
║   Britain  ·  Prussia  ·  Austria        ║
║                                          ║
║   "All of Europe stands against you."    ║
║                                          ║
║   Combined strength: 188,000             ║
║   Strategic posture: Aggressive Advance  ║
║                                          ║
║          [ Continue ]                    ║
║                                          ║
╚══════════════════════════════════════════╝
```

---

## §10. Serialization

### §10a. New WorldState Fields

```python
# Coalition tracking
self.threat_level: int = 0                    # 0-100 CLAMPED (already exists per DIPLOMACY_SPEC §13)
self.threat_sources_this_turn: List[Dict] = [] # [{"source": "battle_win", "amount": 3}] — for UI breakdown
self.active_coalition: Optional[Dict] = None   # See §10b
self.coalition_brewing: Optional[Dict] = None  # See §10c
self.coalition_cooldown: int = 0               # Turns until new coalition can form
self.coalition_count: int = 0                  # Total coalitions formed this game (for naming)

# War exhaustion per nation (used in §6a coalition loyalty penalty formula)
# Key: nation name. Value: int 0-200 CLAMPED.
# Increases: +casualties_taken // 1000 after each battle (capped at +20 per battle).
# Increases: +8 per turn while at war with France.
# Decreases: -5 per turn while at peace with France (floor 0).
# Historical basis: prolonged war weakens resolve — a battered Austria becomes willing to negotiate.
self.war_exhaustion: Dict[str, int] = {}  # Default 0 for all nations
```

### §10b. Active Coalition Dict

```python
active_coalition = {
    "id": "coalition_12",               # str — unique ID
    "name": "The British Coalition",     # str — display name
    "leader": "Britain",                 # str — nation name
    "members": ["Britain", "Prussia", "Austria"],  # List[str]
    "formed_turn": 12,                   # int
    "strategic_posture": "aggressive",   # str — "aggressive" | "defensive" | "cautious"
    "posture_last_updated": 12,          # int — turn when posture was last reassessed
}
```

### §10c. Coalition Brewing Dict

```python
coalition_brewing = {
    "qualifying_nations": ["Austria"],   # List[str] — nations that will join
    "turns_remaining": 2,                # int — countdown
    "started_turn": 9,                   # int
    "threat_at_start": 62,               # int — for reference
}
```

### §10d. Serialization Checklist

All new fields use standard patterns:

```python
# to_dict
"threat_sources_this_turn": self.threat_sources_this_turn,
"active_coalition": self.active_coalition,  # Already a plain dict or None
"coalition_brewing": self.coalition_brewing,
"coalition_cooldown": self.coalition_cooldown,
"coalition_count": self.coalition_count,
"war_exhaustion": self.war_exhaustion,

# from_dict
self.threat_sources_this_turn = data.get("threat_sources_this_turn", [])
self.active_coalition = data.get("active_coalition", None)
self.coalition_brewing = data.get("coalition_brewing", None)
self.coalition_cooldown = data.get("coalition_cooldown", 0)
self.coalition_count = data.get("coalition_count", 0)
self.war_exhaustion = data.get("war_exhaustion", {})
```

**`threat_level` already exists** in DIPLOMACY_SPEC §13. No duplication needed.

### §10e. Implementation File Locations

Coalition logic lives in the existing diplomacy engine — no new files for Session 7:

| Function | File | Notes |
|----------|------|-------|
| `process_threat_sources()` | `diplomacy.py` | Called from executor after battles, captures, vassalization |
| `process_threat_decay()` | `diplomacy.py` | Called from `advance_turn()` |
| `check_coalition_formation()` | `diplomacy.py` | Called from `advance_turn()` after threat processing |
| `evaluate_coalition_posture()` | `diplomacy.py` | Called during enemy AI phase |
| `get_coalition_friction()` | `diplomacy.py` | Called from `enemy_ai.py` adjacency scoring |
| `get_convergence_bias()` | `enemy_ai.py` | Inline in P7 movement scoring (small addition) |
| Coalition UI templates | `diplomatic_templates.py` | 7 new template categories (§8d) |
| Coalition declaration popup | `main.gd` | Same pattern as defiance confrontation popups |
| Coalition notifications | `notifications.py` | 7 new notification types (§9b) |

**Hook points in existing code:**
- `executor.py` `_execute_attack()`: call `process_threat_sources()` after battle win
- `executor.py` `_execute_end_turn()`: call `process_threat_decay()` + `check_coalition_formation()`
- `enemy_ai.py` P7: add convergence bias to movement score
- `enemy_ai.py` P4.77: replace `is_ally` hack with coalition membership check

---

## §11. Edge Cases

### EC-1: Threat spikes past multiple thresholds in one turn

**Scenario:** France captures a capital (+15), wins decisive battle (+8), and controls >60% regions (+1) in one turn. Threat jumps from 35 to 59.

**Rule:** Process all threat sources, THEN check thresholds. If threat crosses 60, brewing starts. If it crosses 80, instant declaration. Only one threshold event fires per turn (the highest crossed).

### EC-2: Coalition forms while player has in-transit proposal

**Scenario:** Talleyrand is en route to Austria with a peace proposal. Coalition declares, pulling Austria into war.

**Rule:** The in-transit proposal is **voided**. Austria is now at war — peace proposals require a different diplomatic context (war-time peace, not peacetime alliance). Talleyrand returns. DP is refunded. Notification: "Your envoy to Austria has been recalled — they have joined the coalition."

### EC-3: Coalition member is vassalized during brewing window

**Scenario:** France vassalizes Saxony during the 3-turn brewing window. Saxony was a qualifying nation.

**Rule:** Remove Saxony from qualifying nations. If qualifying nations drops to zero, cancel brewing. (Vassalization also adds +5/+25 threat per §2a, which might push threat higher — but vassals can't be in coalitions.)

### EC-4: All coalition members peaced out on same turn

**Scenario:** Through simultaneous peace treaties (unlikely but possible with multiple in-transit proposals resolving), all coalition members sign peace in one turn.

**Rule:** Coalition dissolves immediately. Cooldown starts. Process all peace treaties, then check coalition persistence.

### EC-5: Player declares war during brewing window

**Scenario:** Threat is at 62 (brewing, 2 turns left). Player declares war on a neutral nation (+20 threat → 82).

**Rule:** Threat exceeds 80 → instant declaration, overriding the brewing countdown. The player's aggression accelerated the inevitable.

### EC-6: Minimum coalition (2 members)

**Scenario:** Only Austria qualifies as a new member. Britain is already at war. Coalition = Britain + Austria (2 members).

**Rule:** Valid. 2 members is the minimum. If one signs peace, coalition dissolves (< 2 members).

### EC-7: Vassal rebellion during coalition war

**Scenario:** France is fighting a coalition. War score drops below -30. Vassal cascade fires (DIPLOMACY_SPEC §8d). Saxony rebels.

**Rule:** Saxony enters WAR with France (per vassalage rebellion rules). Saxony does NOT automatically join the coalition — they're fighting their own war of independence. However, if Saxony's relation with France is < -10 (likely after rebellion), they qualify for the next coalition.

**Design choice:** Keeping rebellions separate from coalitions prevents overwhelming the player with a single cascading event. The rebel fights alone, at least initially.

### EC-8: Britain has no land to lose

**Scenario:** Britain has off-map territory (or only island regions). France can't march on London.

**Rule:** Britain can only be peaced out diplomatically. War score against Britain uses battle results and territory held (Netherlands, Waterloo, Hanover — Britain's continental holdings). If France captures all British continental holdings, Britain's war score drops, making them amenable to peace.

If Britain has zero continental territory, they become a "phantom belligerent" — still in the coalition, still providing subsidies, but untouchable militarily. The player must use the Continental System or ignore them.

### EC-9: Coalition member at war with another coalition member

**Scenario:** Austria and Prussia are both in the coalition, but have a separate territorial dispute.

**Rule:** Coalition membership does not override bilateral conflicts. However, DIPLOMACY_SPEC §5b.3 (conflicting alliance obligations) applies — nations cannot maintain alliance with two nations at war with each other. In practice, both being at war with France takes priority. Any bilateral conflicts are frozen (no attacks between coalition members) while the coalition is active.

**Implementation:** During coalition war, coalition members cannot declare war on or attack each other. Frozen conflicts resume if the coalition dissolves.

### EC-10: Coalition forms with Saxony as a member

**Scenario:** Player has alienated Saxony (relation dropped below -10, not vassalized).

**Rule:** Valid. Saxony can join a coalition. Their small military (10k starting) makes them a minor member, but they add a front. This is the player's punishment for mismanaging the one nation that started friendly.

### EC-11: Threat reaches 60 during cooldown

**Scenario:** Coalition just dissolved. Cooldown = 4 turns. Threat is 65.

**Rule:** Brewing does NOT start during cooldown. Exception: if threat reaches 90+ during cooldown, override (§7c).

### EC-12: Re-coalition with same members

**Scenario:** First coalition (Britain + Austria) dissolved. After cooldown, threat rises again. Austria qualifies again.

**Rule:** New coalition forms normally. Named "The Second [Leader] Coalition." Members may differ from the first (if relations changed). The coalition_count field tracks this.

### EC-13: Coalition member at zero military strength

**Scenario:** All of Austria's marshals are at 0 strength during a coalition war. Austria has no fighting capability.

**Rule:** Austria remains a coalition member. Zero-strength members still count for membership (they may recruit/reinforce). However, if Austria's war exhaustion is high enough, the AI will seek peace (DIPLOMACY_SPEC §9a P1: losing badly → armistice/peace). If Austria signs separate peace, coalition membership check proceeds normally. Austria's leadership score drops to near-zero (0 military + hostility + authority), so leadership naturally transfers to a stronger member.

### EC-14: Nation rejoins coalition after leaving

**Scenario:** Austria peaced out of a coalition (turn 20). On turn 23, France declares war on Austria again. The original coalition (Britain + Prussia) still exists.

**Rule:** Austria enters WAR with France but does NOT automatically rejoin the existing coalition. Austria fights as an individual belligerent. However, on the next coalition formation check, if a NEW coalition would form (threat ≥ 60, brewing, etc.), Austria qualifies and joins the new coalition along with existing belligerents. There is no mechanism for mid-war coalition joining — this prevents the exploit of cycling peace→war to repeatedly trigger coalition coordination bonuses.

### EC-15: Threat gained and decay cancel to exactly threshold

**Scenario:** Threat is 57. France wins a battle (+3 → 60). Decay is -3 (→ 57). Net: exactly 57.

**Rule:** Per processing order (§3c): sources are applied first (57 + 3 = 60), THEN decay (60 - 3 = 57). Threshold check happens AFTER both. Final threat 57 < 60 → no brewing. The momentary crossing to 60 does NOT trigger brewing because the threshold check is on the final value after all processing.

---

## §12. Worked Examples

### Example A: Coalition Forms and Player Breaks It

**Setup:** Turn 12. France has captured Berlin, vassalized Saxony, and is winning against Britain/Prussia. Threat has been climbing.

| Turn | Threat | Event |
|------|--------|-------|
| 12 | 58 | France wins battle vs Prussia (+3). Threat → 61. |
| 12 | 61 | **BREWING STARTS.** Qualifying nations: Austria (relation -35, not at war, not vassal). |
| 12 | — | Notification: "A coalition is brewing. Austria is consulting with Britain and Prussia. 3 turns remain." |
| 13 | 58 | Decay -3. Player sends Talleyrand to Austria (2 DP): "Propose non-aggression pact." |
| 14 | 55 | Decay -3. Talleyrand arrives. Austria's acceptance: base -35 relation = low. Rejected. |
| 14 | — | Notification: "Coalition brewing. 1 turn remains. Austria has rejected our overture." |
| 15 | 52 | Decay -3. **Countdown expires.** Threat still above 40 — momentum rule applies. |
| 15 | — | **COALITION DECLARED.** "The British Coalition" — Britain (leader), Prussia, Austria. Combined 168k troops. |
| 15 | — | Strategic posture: Aggressive Advance (Britain leads, war score positive for coalition). |
| 16-18 | — | Three-front war. Austrian army advances from the east. |
| 19 | — | France wins decisive battle vs Austria at Bavaria (+8 threat, but also +20 war exhaustion on Austria). |
| 20 | — | "Talleyrand, propose peace to Austria." Austria's acceptance: base low, but war exhaustion high (+28), coalition loyalty penalty reduced. **ACCEPTED.** |
| 20 | — | Austria leaves coalition. Relation with Britain/Prussia: -15. Coalition persists (2 members). |
| 20 | — | Leadership: Britain remains leader (highest score). Posture shifts to Defensive Containment (lost a member). |
| 22 | — | France captures Rhineland. Prussia war exhaustion: 40. Peace proposal accepted. |
| 22 | — | Prussia leaves coalition. **< 2 members.** Coalition dissolves. Britain alone at war. |
| 22 | — | 5-turn cooldown begins. |

**Player broke the coalition through decisive victory (Austria) + bilateral diplomacy (Prussia).** Total coalition duration: 7 turns. Historically plausible: Third Coalition lasted about 4 months (Austerlitz ended it).

### Example B: Cautious Player Avoids Coalition Entirely

**Setup:** Player focuses on defeating Britain/Prussia without expanding aggressively.

| Turn | Threat | Event |
|------|--------|-------|
| 1-5 | 0–5 | Battles vs Britain/Prussia. Threat oscillates near 0 (gains offset by -3 decay). |
| 6 | 18 | Capture Berlin (+15+3). |
| 8 | 14 | Steady decay. Win a battle (+3). |
| 10 | 10 | Peace with Prussia: return Berlin, take only Rhineland (+8, -5 return). Net +3 threat. |
| 12 | 6 | Continuing decay. Stalemate with Britain. |
| 15 | 2 | Near zero. Austria remains neutral (relation -30 but threat never reached 40). |
| 20 | 0 | Player focuses on economic development. No coalition ever threatened. |

**The cautious player traded slower expansion for diplomatic stability.** This is a valid Napoleonic strategy (the Consulate period, 1799–1804, was relatively peaceful and focused on internal reform).

---

## §13. Session Plan

Coalition features integrate into the DIPLOMACY_SPEC §14 unified session plan. Session numbering matches DIPLOMACY_SPEC and STATUS.md:

| DIPLOMACY Session | Coalition Features | Dependencies |
|-------------------|-------------------|--------------|
| **Session 2** (Diplomatic States + Acceptance Formula) | Threat accumulation (§2). Threat display in Ledger Tab 3. Threat sources tracking. | Requires nation relations from Session 1B. |
| **Session 3** (Talleyrand Commands + Dialogue) | Coalition qualifying check (§3b). No formation yet — just tracking who would qualify. | Requires war/peace states from Session 2. |
| **Session 5** (Vassals) | Vassalization threat (+5/+25 per path). Vassal exclusion from coalition. | Requires vassal system from Session 5. |
| **Session 6** (Talleyrand Defiance) | Pre-coalition warnings (§8a). Coalition advisory templates. | Requires Talleyrand from Session 3+. |
| **Session 7** (Coalition — NEW SESSION) | Full coalition system: formation (§3), structure (§4), AI behavior (§5), breaking (§6), dissolution (§7). Coalition declaration popup. Morning Dispatch coalition section. | Requires all Sessions 1-6 systems. |

**Session 7 implementation order:**
1. Formation logic: brewing window, qualifying check, declaration trigger.
2. Coalition structure: leader selection, posture determination.
3. AI behavior: convergence bias, friction modifier, `is_ally` update.
4. Coalition breaking: separate peace with coalition loyalty penalty.
5. Dissolution: persistence check, cooldown.
6. UI: popup, notifications, ledger tab, dispatch section.
7. Edge case handling + tests.

**Estimated test count:** ~35-45 tests for Session 7 (formation: 10, structure: 5, AI: 8, breaking: 8, dissolution: 5, edge cases: 10).

---

## §14. Audit Checklist

### §14a. Dimensional Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Strategic depth** | 9/10 | Threat-from-success creates meaningful expansion/safety tradeoffs. Coalition splitting rewards strategic thinking. |
| **Historical immersion** | 9/10 | Captures the coalition cycle that defined the Napoleonic era. No shared fog preserves defeat-in-detail. |
| **Player agency** | 9/10 | Player can prevent coalitions (moderate expansion), defuse them (diplomacy), or fight through them (military). Multiple valid strategies. |
| **Transparency** | 10/10 | Threat shown openly. Qualifying nations visible. Countdown displayed. No hidden mechanics. |
| **Simplicity** | 8/10 | Threat math is straightforward. Leader system adds modest complexity. Edge cases are numerous but well-defined. |
| **Integration** | 9/10 | Builds on existing DIPLOMACY_SPEC, existing AI coordination (P4.77), existing executor. No new combat rules. |
| **Replayability** | 9/10 | Coalition timing/composition varies based on player strategy. Different diplomatic approaches lead to different coalition experiences. |
| **Fun factor** | 9/10 | "All of Europe is against me" is a peak Napoleonic fantasy moment. Breaking coalitions through cunning diplomacy is deeply satisfying. |
| **Building Blocks** | 10/10 | Same executor, same combat, same AI priorities. Coalition is a strategic layer, not a mechanical one. |
| **Narrative impact** | 9/10 | Coalition names, Talleyrand warnings, dramatic popups, Morning Dispatch briefings — strong narrative moments. |

**Composite: 91/100**

### §14b. Cross-Document Consistency

| DIPLOMACY_SPEC Reference | COALITION_SPEC Usage | Consistent? |
|--------------------------|---------------------|-------------|
| §5c: War declaration +20 threat | §2a: Same value, same trigger | YES |
| §6: Acceptance formula | §6a: Used for separate peace with coalition loyalty modifier | YES — additive modifier |
| §6e: Decisive battle (ratio >2:1, casualties >10,000) | §2a: Same definition, +5 threat | YES (v1.1 fix — was 5000 in v1.0) |
| §8: Vassal system | §3b: Vassals excluded from coalition | YES |
| §8a: Vassalage threat (+5 treaty, +25 conquest) | §2a: Matches per-path values | YES (v1.1 fix — was flat +10 in v1.0) |
| §8d: Cascade tipping point | §6e: Referenced, not duplicated | YES |
| §9c: British subsidies (lowest relation, not gold) | §4e: Matches — lowest relation to Britain | YES (v1.1 fix — was "lowest gold" in v1.0) |
| §10a: Top bar threat indicator | §9a: Extends with coalition-specific states | YES — additive |
| §13: WorldState fields | §10a: New fields added, threat_level reused | YES |
| §14: Session plan (Sessions 1A-7) | §13: Session 7 added as coalition session | YES — uses same session numbering (v1.1 fix) |

### §14c. Golden Rule Compliance

| Rule | Status |
|------|--------|
| 1. Combat modifiers: single source in marshal.py | COMPLIANT — no new combat modifiers |
| 2. All numbers to Godot: int() | COMPLIANT — all threat math uses int() |
| 3. All marshals in ONE dict | COMPLIANT — coalition uses world.marshals |
| 4. State clearing: AFTER reading | COMPLIANT — threat_sources_this_turn cleared after dispatch reads it |
| 5. Enemy AI uses SAME executor | COMPLIANT — coalition AI uses same executor (§5d) |
| 6. LLM never affects mechanics | COMPLIANT — all coalition mechanics deterministic |
| 7. Port 8005 | N/A — no new endpoints required (uses existing diplomacy endpoints) |

---

## §15. Open Questions (For Playtesting)

These are intentionally deferred to playtesting rather than over-designed:

1. **Threat values tuning.** All §2a values are starting estimates. If coalitions form too early/late, adjust source values before thresholds.
2. **Coalition loyalty penalty (-15).** May need adjustment. Too high = coalitions unbreakable. Too low = trivially broken.
3. **Cooldown duration (5 turns).** May need adjustment based on game length. Shorter games may need shorter cooldown.
4. **Passive threat scaling (60/70/80% thresholds).** With 19 regions and France starting at 8, these may need adjustment based on typical game progression.
5. **Convergence bias values (+8/+12/+4).** May need tuning to make coalition advance threatening but not overwhelming.

---

## §16. Starting Situation Balance Analysis

> **Purpose:** Validate that the Waterloo testbed scenario provides viable diplomatic paths for the player. The game is more fun (and better for testing) when diplomacy can actually shift the balance rather than France just fighting everyone alone.

### §16a. Five Diplomatic Paths

#### Path 1: Saxony Alliance/Vassalage (EASY — Tutorial Target)

**Starting:** OPEN_BORDERS (R5), relation +40, 18k troops (R1), 2 regions (Saxony, Dresden).

**Alliance path:** OPEN_BORDERS → NON_AGGRESSION → DEFENSIVE_ALLIANCE → ALLIANCE. Each step: 1 proposal (1 turn transit + acceptance check). With Talleyrand (skill 10) vs Einsiedel (Dove, skill 4): diplomat bonus +12, personality ~+5, relation +20. Every step scores 57+ → instant ACCEPT.

**Timeline:** 3 proposals × 1 turn each = **3 turns to full alliance** (if player prioritizes it).

**Vassalage path:** Already at OPEN_BORDERS (R5, satisfies E3 prerequisite). Vassalage acceptance = base 10 + relation 20 + diplomat 12 + Dove -10 = 32 → COUNTER_OFFER. With moderate sweetener (+18): 50 → ACCEPT. **1-2 turns to vassalize.**

**Value:** Saxony at 18k (R1) is meaningful. As an ally: swings close battles, controls the central European crossroads. As a vassal: ~300g/turn tribute, 18k troops under player control, buffer zone shielding French flanks.

**Assessment:** Saxony is the diplomacy tutorial — easy to acquire, teaches the system. R1 makes the reward worth the effort. R5 removes 1 busywork step (proposing OPEN_BORDERS to a nation already in your orbit) while preserving the meaningful choice (vassalize vs ally).

#### Path 2: Prussia Flip (VERY HARD — Potentially Too Hard)

**Starting:** WAR, relation -60, 72k troops (Blücher + Gneisenau), Hawk diplomat (Hardenberg, skill 6).

**Required steps:** Win battles → build war score → offer armistice/peace → improve relations → upgrade through diplomatic states → eventually ALLIANCE.

**Armistice acceptance (France proposing, war score +40):**
```
Base 20 (winning side) + war_score 12 + relation -30 + diplomat +8 + Hawk -5 = 5 → REJECT
```

**Even at war score +60 with relation improved to -30:**
```
Base 30 (peace) + war_score 18 + relation -15 + diplomat +8 + Hawk -5 + sweetener +20 = 56 → ACCEPT (barely)
```

This requires: capturing Berlin, winning 5+ battles (including a decisive one), running 3+ IMPROVE_RELATIONS missions during the war, AND offering generous terms. Realistically **12-15 turns** to peace, then another **10-15 turns** to alliance.

**Timeline:** 20-25 turns total to flip Prussia. In a 25-30 turn game, this is the **entire game**. Viable but only as a game-long strategic commitment.

**Assessment:** This is appropriate difficulty for flipping a major enemy. The player should feel like flipping Prussia is a momentous achievement, not routine. No change needed.

#### Path 3: Austria Courtship (BLOCKED by Alliance Network)

**Starting:** PEACE, relation -30, 60k troops, DEFENSIVE_ALLIANCE with Britain AND Prussia.

**The problem:** Even if France improves relations with Austria to +20, attempting ALLIANCE triggers §5b.3 (conflicting alliance obligations). Austria must choose between France and Britain. At Austria-Britain relation +40 vs France-Austria +20: Austria chooses Britain.

**To ally Austria, France must either:**
1. Get France-Austria relation ABOVE Austria-Britain (+40) — requires 70+ points of improvement from -30, which is 7+ IMPROVE_RELATIONS missions at 2 DP each = months of effort.
2. Make peace with Britain first — removing the alliance conflict. But peace with Britain is endgame-tier difficulty (see Path 4).
3. Diplomatically damage Austria-Britain relations — no direct mechanic for this exists.

**Attack path:** France CAN attack Austria without triggering new wars (Britain/Prussia already at war). But this pushes Austria into the coalition (relation drops further) and adds threat.

**Assessment:** Austria is CORRECTLY a swing state that's hard to court. The DEFENSIVE_ALLIANCE with Britain is the real blocker. See §16b for a recommended adjustment that makes this path viable without making it easy.

#### Path 4: Britain Peace (ENDGAME ONLY)

**Starting:** WAR, relation -80, off-map, Hawk diplomat (Castlereagh, skill 7).

**Peace acceptance (war score +80, max practically achievable):**
```
Base 30 + war_score 24 + relation -40 + diplomat +6 + Hawk -5 = 15 → REJECT
```

Even at maximum war score with territory sweetener (+30 cap): 15 + 30 = 45 → COUNTER_OFFER.

Peace with Britain requires: capturing ALL continental holdings (Netherlands, Waterloo, Hanover), winning several decisive battles, AND offering generous terms. Plus improving relations from -80.

**Assessment:** Correctly endgame-only. Britain is the permanent strategic pressure that forces the player to manage threat and coalitions. No change needed.

#### Path 5: Diplomatic Victory (CURRENTLY NOT VIABLE)

The ideal game offers three strategic approaches:
1. **Military dominance:** Crush Prussia, then Austria, manage coalitions. **VIABLE.**
2. **Diplomatic finesse:** Flip Prussia, ally Austria, isolate Britain. **NOT VIABLE** — takes 20-25 turns for Prussia alone, Austria blocked by alliance network.
3. **Mixed:** Beat Prussia militarily, court Austria diplomatically. **PARTIALLY VIABLE** — but Austria courtship blocked by §5b.3.

**Root cause:** The acceptance formula makes diplomatic approaches extremely slow against hostile nations. The starting relations are too hostile for diplomacy to be a primary strategy within the game's timeframe.

### §16b. Balance Recommendations

> **Constraint:** Changes must serve BOTH the Waterloo testbed AND translate sensibly to the 1805 campaign. No Waterloo-only hacks.

#### R1: Boost Saxony Starting Strength (10k → 18k)

Saxony at 10k is too weak to matter as an ally. At 18k with a reasonable position (Dresden is the crossroads of central Europe), Saxony becomes a meaningful early-game ally — enough to swing a close battle.

**Justification:** Historically, Saxon forces at Waterloo-era numbered ~20k. The Rhine Confederation contributed ~160k across all members. 18k for a single German state is conservative.

**Impact:** If France vassalizes Saxony, they gain 18k (more meaningful tribute + military support). If they ally Saxony, 18k + DEFENSIVE_ALLIANCE creates a central European buffer that Austria must respect.

#### R2: Downgrade Austria-Britain to NON_AGGRESSION (was DEFENSIVE_ALLIANCE)

**Current:** Britain ↔ Austria: DEFENSIVE_ALLIANCE. This makes Austrian alliance with France impossible (§5b.3 conflict).

**Proposed:** Britain ↔ Austria: NON_AGGRESSION. Austria ↔ Prussia: DEFENSIVE_ALLIANCE remains.

**Justification:** Historically, Austria was the most uncommitted member of any anti-French coalition. They repeatedly negotiated with Napoleon (marriage alliance 1810, armed mediation 1813). A NON_AGGRESSION pact with Britain (rather than DEFENSIVE_ALLIANCE) means Austria CAN be courted by France without triggering alliance conflict — but it's still hard (relation -30, must improve significantly).

**Impact:** Creates a genuine "Austria courtship" path. France must choose between improving Austria relations (costly DP investment) vs conquering Austria (adds massive threat). Both are viable but mutually exclusive, creating a real strategic decision.

**1805 translation:** In 1805, Austria was NOT formally allied with Britain until they joined the Third Coalition — NON_AGGRESSION is more historically accurate.

#### R3: Add "Battlefield Diplomacy" Bonus

When France offers peace/armistice to a nation France has a POSITIVE war score against, add +10 acceptance bonus ("military reality demands negotiation"). This makes winning on the battlefield translate more directly into diplomatic leverage.

**Current:** War score of +40 only gives +12 acceptance. A player who has crushed an enemy army still faces near-impossible acceptance scores because of hostile relations.

**Proposed:** When war_score > 20 and proposer is winning: +10 flat acceptance bonus (stacks with war score modifier). This represents "they can see they're losing."

**Cap:** This bonus does NOT apply to vassalage proposals (already covered by Military Supremacy §6b.1 at war score ≥ 70).

**Impact:** At war score +40 with the battlefield bonus: acceptance jumps from +12 to +22 from war_score-related modifiers. Combined with sweetener and diplomat skill, this makes mid-war peace proposals viable without requiring 7+ turns of IMPROVE_RELATIONS.

**Where to define:** DIPLOMACY_SPEC §6b as a new component of the acceptance formula. Not a coalition-specific mechanic.

#### R4: Prussia Starting Relation -40 (was -60)

**Current:** France ↔ Prussia: -60. This makes diplomatic resolution extremely difficult (contributes -30 to acceptance).

**Proposed:** France ↔ Prussia: -40. Still hostile (at WAR), but leaves more room for war-time diplomacy.

**Justification:** Prussia at Waterloo was a reluctant belligerent — they had been Napoleon's ally just 3 years earlier (1812). -40 better reflects the ambiguity of the relationship.

**Impact:** Relation contribution to acceptance moves from -30 to -20. Combined with R3, an armistice with Prussia after capturing Berlin becomes:
```
Base 20 + war_score 12 + relation -20 + battlefield +10 + diplomat +8 + Hawk -5 = 25 → REJECT (close)
```
With sweetener (+10): 35 → COUNTER_OFFER. This feels right — hard but achievable.

**1805 translation:** In 1805, Prussia was neutral (relation ~0). In 1806, France-Prussia relations were -40 to -50 before Jena. -40 is appropriate for the Waterloo period.

#### R5: Saxony Starting Diplomatic State OPEN_BORDERS (was PEACE)

**Current:** France ↔ Saxony: PEACE (French-leaning). Player must propose open borders before any further diplomacy.

**Proposed:** France ↔ Saxony: OPEN_BORDERS. Relation remains +40.

**Justification:** Saxony was in the Confederation of the Rhine from 1806 — French troops moved freely through Saxon territory. Starting at OPEN_BORDERS reflects the existing friendly relationship without giving away the diplomatic endpoint (alliance or vassalage). The player still makes the meaningful choice: vassalize (3 DP, harsh) or pursue alliance (1 DP per step, gradual).

**Impact:**
- Saves 1 turn and 1 DP on any Saxony diplomatic path (vassalage in 1-2 turns, alliance in 3 turns)
- Trade income: +100 bilateral (up from +50 at PEACE) — minor economy boost for both sides
- France starting income increases by +50 gold/turn (OPEN_BORDERS +100 bilateral replaces PEACE +50 bilateral)
- Vassalage acceptance from OPEN_BORDERS: base 10 + relation 20 + diplomat 12 + Dove ~-10 = 32 (COUNTER_OFFER). With moderate sweetener (+18): 50 → ACCEPT. Still requires a real diplomatic decision, not free.
- Does NOT grant military access (OPEN_BORDERS allows movement through, not stationing)

**1805 translation:** In 1805, Saxony was nominally neutral but French-leaning. OPEN_BORDERS is historically accurate for the pre-Confederation period.

#### Summary: Starting Relation & State Adjustments

| Pair | Current | Proposed | Rationale |
|------|---------|----------|-----------|
| France ↔ Prussia | -60 | -40 | More historically accurate, opens diplomatic path |
| France ↔ Saxony (state) | PEACE | OPEN_BORDERS | Reflects existing French orbit, saves 1 step |
| France ↔ Saxony (relation) | +40 | +40 | No change — already correct |
| France ↔ Austria | -30 | -30 | No change — already correct |
| France ↔ Britain | -80 | -80 | No change — correctly endgame |
| Britain ↔ Austria | +40 (DEF_ALLIANCE) | +40 (NON_AGGRESSION) | Removes alliance conflict blocker |
| Saxony starting troops | 10k | 18k | Makes ally worth having |

#### Path Viability After Adjustments

| Path | Before | After | Notes |
|------|--------|-------|-------|
| Saxony ally | EASY (but worthless) | EASY (meaningful, faster) | R1: 18k troops matter, R5: 1 fewer step |
| Saxony vassal | 3 turns | 1-2 turns | R5: already at OPEN_BORDERS |
| Prussia flip | 20-25 turns (game-long) | 12-18 turns (late-game) | R3+R4: faster diplomacy |
| Austria courtship | BLOCKED | HARD but viable | R2: removes alliance conflict |
| Britain peace | Endgame only | Endgame only | No change — correct |
| Diplomatic victory | Not viable | Viable (ambitious) | All paths now reachable |

### §16c. Design Gate Required

**The balance adjustments in §16b affect DIPLOMACY_SPEC §1e (starting relations and diplomatic states) and §1c (starting forces).** These changes need user approval before implementation. Specifically:

1. **R1 (Saxony 18k):** Modify Reynier starting strength in §1c
2. **R2 (Austria-Britain NON_AGGRESSION):** Modify §1e starting diplomatic states
3. **R3 (Battlefield Diplomacy):** New acceptance formula component in DIPLOMACY_SPEC §6b
4. **R4 (Prussia -40):** Modify §1e starting relations
5. **R5 (Saxony OPEN_BORDERS):** Modify §1e starting diplomatic states, §1c trade income

These are additive changes — they don't break any existing spec mechanics. But they change the fundamental strategic texture of the game and should be playtested.

---

```
COALITION_SPEC v1.1 CONFIDENCE REPORT
=======================================
Threat accumulation:                    COMPLETE (v1.1: per-path vassalage, decisive threshold fixed)
Formation mechanics:                    COMPLETE (v1.1: processing order specified)
Leader question resolved:               YES — chosen option: B (Leader Sets Strategy)
AI behavior specified:                  COMPLETE
Breaking mechanics:                     COMPLETE (v1.1: loyalty penalty formula fixed)
Dissolution rules:                      COMPLETE
Talleyrand integration:                 COMPLETE
UI/feedback specified:                  COMPLETE
Serialization complete:                 COMPLETE
Edge cases (10+ required):              15/10 (v1.1: +3 new: zero-strength, rejoin, threshold exact)
Session plan mapped:                    YES (v1.1: aligned to DIPLOMACY_SPEC session numbering)
Cross-doc consistency with DIPLOMACY_SPEC: VERIFIED (v1.1: 4 mismatches fixed)
Golden Rule compliance:                 ALL 7 CHECKED

v1.1 AUDIT FIXES (from comprehensive adversarial audit):
  CRITICAL: Coalition loyalty penalty formula used max() instead of min() — fixed
  CRITICAL: Vassalage threat was flat +10, DIPLOMACY_SPEC §8a uses +5/+25 per path — aligned
  CRITICAL: Decisive battle threshold was 5000, DIPLOMACY_SPEC §6e uses 10,000 — aligned
  MAJOR:    Leadership score used raw troop count, should use //1000 — fixed in function
  MAJOR:    British subsidy criteria was "lowest gold," DIPLOMACY_SPEC §9c uses "lowest relation" — aligned
  MAJOR:    Session naming used DD# scheme, should use Session # matching DIPLOMACY_SPEC §14 — aligned
  MAJOR:    Decay formula didn't exclude France from ALL_NATIONS — self-exclusion guard added
  MAJOR:    Processing order (threat → decay → threshold check) was unspecified — added to §3c
  MINOR:    Friction multiplier returns float, needs int() wrapping before Godot — noted in §5c
  MINOR:    Worked example updated for conquest vassalage (+25), added treaty comparison note

OVERALL CONFIDENCE: 95/100

v1.2 MASTER AUDIT FIXES (Mar 2026 — final pre-implementation audit):
  CRITICAL: war_exhaustion field was used in §6a formula but never defined — added to §10a
  MAJOR:    "coalition war score" used in §4c thresholds but never defined — added formula
  MAJOR:    British subsidy session dependency — moved to Session 7 scope
  Added war_exhaustion to §10d serialization checklist
  Added implementation session note to §4e
```
