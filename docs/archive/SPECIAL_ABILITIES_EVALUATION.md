# Special Abilities Evaluation

Design proposals for Davout's Iron Marshal ability, roster planning for 1805, and audit of existing abilities.

**IMPLEMENTATION STATUS:** Design C (Counter-Punch Mastery) implemented with +20% attack bonus. See `backend/models/marshal.py` and `backend/game_logic/combat.py`. 22 tests in `tests/test_marshal_abilities.py`.

---

## Part 1: Davout's Iron Marshal Ability

### Context

Davout was Napoleon's finest corps commander — methodical, devastating in defense, and lethal on the counterattack. At Austerlitz he held the right flank outnumbered then crushed the Allied left. At Auerstedt he destroyed a Prussian army twice his size by absorbing the assault then punching back.

**Previous state:** Davout had a placeholder ability `"Iron Marshal"` with trigger `"morale_drops_below_50"`. **Now implemented as "Counter-Punch Mastery"** (+20% attack after defending, any outcome, any target).

**What Davout already gets from cautious personality (free, no ability needed):**
- Counter-Punch: Free attack (0 AP) after successful defense
- +5% additional defense in defensive stance (total +20%)
- +10% defense when outnumbered
- -5% attack in aggressive stance (hesitant)
- -10% attack at bad odds (ratio < 1:1)
- +3%/turn fortify rate (not +2%), max 20%
- +5% instant fortify bonus on first turn

**Design direction:** High-powered counter-punch that rewards careful planning and defensive counterattack. NOT a passive defense bonus (that's Wellington's identity). Davout should reward the player who absorbs an enemy attack and then strikes back hard — deliberate, methodical, devastating.

---

### Design A: "Iron Resolve" (RECOMMENDED)

**Concept:** While fortified, Davout's army coils like a spring. Each turn fortified builds "resolve" — when he finally strikes, it's devastating.

**Trigger:** While Davout is fortified in a region, he accumulates resolve stacks — 1 per turn fortified (max 3 stacks). Stacks persist until consumed by attacking, or cleared by moving/breaking.

**Effect:** When Davout attacks, he gets **+8% attack per stack of resolve**. Stacks are consumed on attack.
- 1 stack: +8% attack
- 2 stacks: +16% attack
- 3 stacks: +24% attack

**Implementation details:**
- New field on Marshal: `iron_resolve_stacks: int = 0` (Davout-only, capped at 3)
- Increments in `world_state.py _process_tactical_states()` when fortified + ability name match
- Applied in `marshal.py get_attack_modifier()` via ability name check
- Consumed on attack in `combat.py` (AFTER `get_attack_modifier()` reads the value)
- Cleared on move in `marshal.py move_to()`
- Serialized via `to_dict()`/`from_dict()`

**System interactions:**
| System | Interaction |
|--------|-------------|
| Fortify bonus | Stacks build WHILE fortifying. Davout gets both defense (fort bonus up to 20%) and attack buildup simultaneously. The fort bonus only helps if attacked (defense), while resolve only helps when attacking — no overlap. |
| Counter-punch | Perfect combo: enemy attacks fortified Davout → he defends with fort bonus + cautious bonuses → wins → counter-punch fires WITH resolve stacks → devastating. This IS the Auerstedt fantasy. |
| Drill | Can't drill while fortified (different action). Davout must choose: drill for shock_bonus (+20% attack, 2 turns) or fortify for resolve (+8-24% attack, 1-3 turns). Drill is faster but weaker per turn; resolve is slower but includes defense bonus. Interesting tradeoff. |
| Terrain | No interaction. Resolve is independent of terrain. |
| Phase 7 coordination | Stacks multiplicatively with coordination bonuses (combined arms, relationship, adjacent support). Hard cap (+25% atk) applies to coordination bonuses only, not marshal abilities. A fully-wound Davout with allies is devastating but requires 3+ turns of setup. |
| Morale | No interaction. Resolve doesn't affect morale. |
| Trust | No interaction. Building resolve doesn't affect trust. |
| Strategic orders (HOLD) | HOLD order keeps Davout in place and fortified → naturally builds resolve. Player can issue "Davout, hold Rhineland" and watch him build up over 3 turns. |

**Why it feels like Davout:**
- **Deliberate:** Requires 1-3 turns of patient fortification — no instant gratification
- **Methodical:** Stacks build predictably, rewarding planning
- **Devastating:** A 3-stack counter-punch on an enemy that just attacked you is +24% attack (on top of cautious counter-punch's free AP). That's Auerstedt
- **Not defensive:** The bonus is purely offensive. Davout fortifies not to turtle but to prepare a devastating counterstrike
- Contrast with Wellington: Wellington gets +5% defense always (passive shield). Davout gets +24% attack after setup (loaded spring)

**Balance assessment:**

Maximum Davout attack modifier with full setup (3 stacks + aggressive stance + no bad odds):
`1.0 × 1.15 (aggressive) × 1.24 (resolve) × 0.95 (cautious penalty) = ~1.35 (+35%)`

Compare to Ney with drill + aggressive stance:
`1.0 × 1.15 (aggressive) × 1.20 (drill) × 1.15 (personality) × 1.05 (drill synergy) = ~1.67 (+67%)`

Davout's max is significantly below Ney's — appropriate because Davout also gets superior defense. The tradeoff: Ney hits harder but crumbles, Davout is indestructible but slower to wind up.

**Degenerate strategy check:**
- "Turtle forever": Stacks cap at 3 (3 turns), no benefit past that. Enemy can bypass a stationary Davout on the 19-region map.
- "Never move Davout": Viable strategy but enemy AI will eventually attack or bypass. Stacks are only useful when Davout ATTACKS, forcing eventual action.
- "Counter-punch abuse": Requires enemy to attack Davout. Player can't force this. If enemy avoids Davout, resolve stacks go unused — self-balancing.

**Player communication:**
- **Tooltip:** "IRON RESOLVE: While fortified, Davout builds resolve (+8% attack per turn, max 3 stacks). When he strikes, his troops unleash a devastating counterattack."
- **Berthier advisory (building):** "Sire, Marshal Davout has been fortifying his position for [X] turns. His resolve builds — [X] stacks (+Y% attack bonus). The Iron Marshal is coiling for a devastating strike."
- **Berthier advisory (triggered):** "The Iron Marshal unleashes his resolve! Davout's counter-punch strikes with [X] stacks of pent-up fury (+Y% attack bonus)."
- **Battle report label:** "Iron Resolve (3 stacks): +24%"

---

### Design B: "Auerstedt" — Outnumbered Attack Bonus

**Concept:** Davout fights better when outnumbered. At bad odds, where other cautious generals hesitate, Davout's iron discipline turns the disadvantage into an advantage.

**Trigger:** When Davout attacks an enemy whose strength is greater than his own (strength ratio < 1.0).

**Effect:** +20% attack bonus when attacking outnumbered.

**Implementation details:**
- Applied in `marshal.py get_attack_modifier()` with ability name check + strength_ratio parameter
- No new state fields needed (reads strength_ratio already passed to modifier function)
- Self-contained in a single modifier line

**Key interaction — cancels cautious penalty:**
- Cautious personality gives -10% attack at bad odds
- Iron Marshal gives +20% at bad odds
- Net: +10% when outnumbered. Davout is the ONLY cautious general who doesn't suffer at bad odds — he thrives

**System interactions:**
| System | Interaction |
|--------|-------------|
| Cautious -10% bad odds | Directly counteracts: -10% + 20% = net +10%. Elegant. |
| Outnumbered defense (+10%) | Davout already gets +10% defense when outnumbered (personality). Combined: +10% defense AND +10% net attack when outnumbered. He's just better at everything vs larger forces. |
| Counter-punch | Natural combo: attacked by larger force → defend successfully → counter-punch → enemy still outnumbers him → +20% attack bonus on counter-punch. |
| Phase 7 coordination | If allies are nearby, Davout might NOT be outnumbered anymore. Creates interesting tension: coordination gives bonuses but may remove outnumbered trigger. Davout may be better alone. Matches Auerstedt (alone against the main Prussian army). |

**Why it feels like Davout:**
- Captures the Auerstedt fantasy directly — he's BETTER when outnumbered
- Creates a unique identity: "send Davout where you're outnumbered"
- Simple, clean, always-on when relevant

**Balance assessment:**
- Net +10% when outnumbered is meaningful but not broken
- Only triggers at bad odds — a niche condition
- Compare to Ney's +15% always-on: narrower but higher power when active

**Degenerate strategy check:**
- "Never recruit to stay outnumbered": Silly — fewer troops = more casualties regardless of +20%
- "Always attack larger forces": The +20% doesn't compensate for 2:1 odds. It helps at marginal disadvantages (0.7:1 to 1:1), not suicide attacks

**Concern:** More passive than Design A. The bonus just happens automatically when outnumbered — no player decision to make beyond "which battle to pick." Less strategic depth.

---

### Design C: "Counter-Punch Mastery" — Enhanced Counter-Punch Damage

**Concept:** When the Iron Marshal strikes back, he strikes to shatter. Davout's counter-punches are uniquely devastating.

**Trigger:** When Davout uses his counter-punch (free attack earned from successful defense).

**Effect:** Counter-punch attacks deal +25% attack damage AND inflict -10 additional morale on the enemy (on top of normal morale effects).

**Implementation details:**
- New flag: `is_davout_counter_punch: bool` passed through combat resolution
- Applied in `combat.py resolve_battle()` when flag is set
- Morale penalty applied after normal morale calculation

**System interactions:**
| System | Interaction |
|--------|-------------|
| Counter-punch | Directly enhances the cautious personality's existing mechanic. Makes Davout's counter-punch stronger than other cautious marshals'. |
| Drill | If Davout drilled before being attacked, shock_bonus applies to counter-punch. Combined: +20% (drill) + 25% (mastery) = +45% attack. Very strong but requires being attacked mid-drill (-25% defense penalty). High risk, high reward. |
| Phase 7 | Stacks normally with coordination. |

**Why it feels like Davout:** Amplifies the "absorb then strike" pattern. Counter-punch is already Davout's playstyle; this makes his version uniquely powerful.

**Balance assessment:**
- +25% attack on a free action is very strong
- But requires enemy to attack Davout first — purely reactive
- If enemy avoids Davout, ability does nothing
- Compare: Ney gets +~25% in aggressive stance FOR FREE every attack. Davout gets +25% only on counter-punches.

**Concern:** Narrowest of the three designs. Only affects counter-punches. If enemy doesn't attack Davout, ability is dead. Less strategic depth than Design A. Also, "make existing mechanic better" is less interesting than "add new mechanic."

---

### Recommendation

**Design A (Iron Resolve)** is the strongest design because:

1. **Creates player decisions:** "Do I keep fortifying for more stacks, or strike now?"
2. **Rewards planning:** The 1-3 turn buildup is deliberate — you choose when to unleash
3. **Natural counter-punch combo:** Being attacked while building resolve → defending → counter-punching is the full Auerstedt arc
4. **Unique rhythm:** No other marshal has a "build up then spend" attack mechanic. Recklessness is automatic (win → escalate). Resolve is deliberate (fortify → choose when to strike).
5. **Clean Phase 7 interaction:** Just another multiplicative modifier
6. **Not degenerate:** 3-stack cap, requires eventual attack to benefit, enemy can bypass

Design B is a clean alternative if simplicity is preferred. Design C is the weakest (narrow, passive, less interesting).

---

## Part 2: General Roster Planning for 1805

### Roster Design Principles

1. **Only historically distinguished commanders get unique special abilities.** Most generals are personality-driven only (like Grouchy). A unique ability should create a distinct tactical decision point, not just be "another combat bonus."

2. **Personality IS identity for most generals.** An aggressive cavalry commander already has: +15% attack, recklessness system, 2-tile range, cavalry limits. That's a complete gameplay identity without any special ability.

3. **One ability per general, maximum.** No stacking unique abilities. Keep it simple.

4. **Abilities should create decisions, not just passive bonuses.** Good: "Ney gets +2 shock when attacking" (encourages attacking). Bad: "+5% to everything" (no decision).

5. **Enemy general abilities are NOT a priority for Waterloo testbed.** The Waterloo map is for building systems. Enemy nation general abilities will be designed when we build 1805 rosters.

6. **Roster size should match nation's strategic importance.** France needs the most generals. Minor nations need fewer.

### Estimated Roster Sizes (1805 EA Scope)

| Nation | Role | Estimated Generals | Notes |
|--------|------|-------------------|-------|
| France | Player | 6-8 | Currently 4 in Waterloo (Ney, Davout, Grouchy, Drouot). Add Murat, Lannes, Soult, possibly Massena/Bernadotte. |
| Austria | Major enemy | 4-5 | Main opponent at Austerlitz/Ulm. |
| Russia | Major enemy | 3-4 | Austrian ally, arrives late in campaign. |
| Prussia | Conditional enemy | 3-4 | Neutral in 1805, joins War of the Fourth Coalition (1806). Could be expansion content. Already has Blucher/Gneisenau from Waterloo. |
| Britain | Naval/peripheral | 2-3 | Primarily naval in 1805. Already has Wellington/Uxbridge from Waterloo. |
| Spain | French ally | 2-3 | If included. Minor land role in 1805. |
| Ottoman | Peripheral | 1-2 | If included. Very minor role. |
| Sweden | Peripheral | 1-2 | If included. Very minor role. |

### Special Ability Candidates by Nation

**France (player marshals):**

| Commander | Ability Concept (1-line) | Priority |
|-----------|------------------------|----------|
| Ney | Bravest of the Brave (+2 shock) | WIRED |
| Davout | Iron Marshal (see Part 1) | NEXT |
| Drouot | Sage of the Grand Army (15% fort degradation) | WIRED |
| Murat | "King of Cavalry" — supreme cavalry charge bonus, shock multiplier | High |
| Lannes | "Roland of the Army" — morale boost to nearby allies when wounded/outnumbered | Medium |
| Soult | "Hand of Iron" — maneuver warfare, movement bonus or flanking bonus | Medium |
| Massena | "Child of Victory" — defensive last-stand, bonus when cornered | Low |
| Others | Personality-driven only (Bernadotte, Oudinot, Mortier, etc.) | None |

**Austria:**

| Commander | Ability Concept (1-line) | Priority |
|-----------|------------------------|----------|
| Archduke Charles | "Habsburg's Finest" — morale recovery after defeat, army doesn't break easily | High |
| Schwarzenberg | "Coalition Diplomat" — coordination bonus with allied nation generals | Medium |
| Mack | No ability (historically incompetent, personality-driven only) | None |
| Others | Personality-driven only | None |

**Russia:**

| Commander | Ability Concept (1-line) | Priority |
|-----------|------------------------|----------|
| Kutuzov | "The Old Fox" — strategic retreat mastery, reduced retreat casualties, scorched earth | High |
| Bagration | "The Eagle" — aggressive last-stand, fights harder at low strength | Medium |
| Others | Personality-driven only | None |

**Prussia (existing + expansion):**

| Commander | Ability Concept (1-line) | Priority |
|-----------|------------------------|----------|
| Blucher | Vorwärts! (+3k pursuit) | WIRED |
| Gneisenau | Staff Work (+5% to allies in same region) | DEFERRED to Phase 7 |
| Others | Personality-driven only | None |

**Britain (existing):**

| Commander | Ability Concept (1-line) | Priority |
|-----------|------------------------|----------|
| Wellington | Reverse Slope Defense (+5% defense) | WIRED |
| Uxbridge | Pursuit Master (+5k cavalry pursuit) | WIRED |
| Moore | Personality-driven only (if added) | None |

### Key Principle: Don't Over-Ability

Out of ~30-40 total generals across all nations in 1805 EA, **only ~10-12 should have unique wired abilities**. The rest are personality-driven. This keeps abilities feeling special and reduces implementation/balance burden.

---

## Part 3: Existing Ability Review

### Ney — "Bravest of the Brave" (+2 Shock when attacking)

- **Balance:** +2 shock → ~+10% attack damage via `shock_multiplier = 1.0 + (shock / 20.0)`. Combined with +15% aggressive base, Ney hits ~+25% in aggressive stance without drill. Strong but appropriate.
- **Phase 7 interaction:** Combined arms (+10-20%) and coordination (+3%/+5% per ally) stack multiplicatively. With full coordination + combined arms, Ney could hit +40-50% total attack. The hard cap (+25% atk on coordination bonuses only) limits the ceiling. Marshal abilities are NOT subject to the coordination cap, which is correct — they're identity bonuses, not coordination bonuses.
- **Verdict:** Clean, balanced, no concerns.

### Drouot — "Sage of the Grand Army" (15% fort degradation)

- **Balance:** Niche. Only matters against fortified positions. Self-balancing: if enemy isn't fortified, ability does nothing. When relevant, 15% vs 10% standard (or 5% non-artillery) is a meaningful but not game-breaking advantage.
- **Phase 7 interaction:** Minimal. Fort degradation is independent of coordination. Phase 7b SUPPORT bombardment could let Drouot degrade forts while supporting allies — future design consideration.
- **Verdict:** Clean, no concerns.

### Wellington — "Reverse Slope Defense" (+5% defense always)

- **Balance:** Modest but always-on. Wellington has defense 10 + cautious personality. Total defense modifier in defensive stance, outnumbered, fortified (16%): `1.15 × 1.16 × 1.05 × 1.10 × 1.05 ≈ 1.63 (+63%)`. Very tanky but he's meant to be the best defender in Europe.
- **Phase 7 interaction:** Coordination defense cap is +20%. Wellington's +5% is a marshal ability, not coordination — correctly exempt from cap. With full coordination (+20%) + ability (+5%) + stance + fortify, Wellington becomes very hard to break. This is intended — breaking Wellington should require numbers or flanking.
- **Verdict:** Clean. The +5% is small enough that Phase 7 stacking is manageable.

### Blucher — "Vorwärts!" (+3k pursuit casualties)

- **Balance:** Flat 3k bonus on retreat. Good against small armies (~18k Uxbridge), less impactful against large ones (~68k Wellington). Self-balancing. Floor of 1000 prevents zero-damage retreats.
- **Phase 7 interaction:** Pursuit is post-battle, independent of coordination bonuses. No interaction.
- **Verdict:** Clean, no concerns.

### Uxbridge — "Pursuit Master" (+5k pursuit casualties, cavalry only)

- **Balance:** Stronger than Blucher (5k vs 3k) but requires cavalry flag. Appropriate for a dedicated cavalry pursuit specialist. The cavalry requirement is meaningful (limits who can trigger it).
- **Phase 7 interaction:** Same as Blucher — pursuit is post-battle, independent.
- **Verdict:** Clean, no concerns.

### Overall Assessment

All 5 existing wired abilities are clean, well-balanced, and won't interact badly with Phase 7 coordination mechanics. The key safeguard is that the coordination hard cap (+25% atk/+20% def) applies only to coordination bonuses, not to marshal signature abilities. This prevents runaway stacking while preserving each marshal's identity.

No changes needed to existing abilities before Phase 7.

---

## Part 4: UI Surface Audit for Abilities

### Every Place Abilities Appear

| # | Surface | File(s) | Auto-detects? | Manual wiring needed? |
|---|---------|---------|---------------|----------------------|
| 1 | Marshal Management screen | `marshal_overview.py` | Reads `marshal.ability` dict automatically | YES — must add name to `_WIRED_ABILITY_MARSHALS` set for `ability_active=True` |
| 2 | Combat resolution (attack modifiers) | `combat.py`, `marshal.py` | NO — hardcoded ability name checks | YES — must add ability-specific code in `get_attack_modifier()` or `get_defense_modifier()` or `resolve_battle()` |
| 3 | Battle reports (modifier snapshots) | `battle_report.py` | Personality modifiers auto-captured. Ability-specific observations require manual templates. | PARTIAL — personality auto, ability-specific observations need manual template + priority tier |
| 4 | Morning Dispatch | `dispatch.py` | NO ability references. Reports marshal status (broken, retreating, fortified) but not abilities. | NO — no changes needed for new abilities |
| 5 | Map tooltips | `map.gd` | NO ability display in current tooltips | NO — abilities not shown on map hover |
| 6 | Executor (ability state) | `executor.py` | NO — ability consumption/blocking is hardcoded per ability | YES — if ability has consumable state (counter-punch, resolve stacks), must add consumption/blocking logic |
| 7 | World state (turn processing) | `world_state.py` | Counter-punch expiration is generic field check | YES — if ability has per-turn state changes (stack increment, expiration countdown) |
| 8 | Godot marshal management | `marshal_management.gd` | Reads all fields from `/marshal_overview` endpoint | AUTO — displays whatever backend sends |
| 9 | Strategic Ledger | `ledger.py` | No ability display | NO |
| 10 | Campaign Log | `campaign_log.py` | Events auto-captured | NO — ability effects generate events through normal channels |
| 11 | Notification bar | `notifications.py` | No ability-specific notifications currently | MAYBE — could add Berthier advisory notifications for ability state (e.g., "Davout's resolve: 3 stacks") |

### Summary: Files Requiring Manual Update When Adding a New Wired Ability

**Always required:**
1. `marshal.py` — Ability definition in `create_*_marshals()`, state fields, `to_dict()`/`from_dict()`
2. `marshal.py` or `combat.py` — Mechanical effect (modifier application or combat-time check)
3. `marshal_overview.py` — Add name to `_WIRED_ABILITY_MARSHALS` set
4. `tests/` — Ability tests

**Required if ability has state:**
5. `executor.py` — State consumption, blocking logic
6. `world_state.py` — Per-turn state processing (increment, expiration)

**Optional (quality):**
7. `battle_report.py` — Ability-specific Berthier observation templates
8. `notifications.py` — Advisory notifications for ability state changes

**Auto-detected (no changes):**
- `dispatch.py` — No ability display
- `map.gd` — No ability display in tooltips
- `marshal_management.gd` — Reads whatever backend sends
- `ledger.py` — No ability display
- `campaign_log.py` — Events flow through normal channels
