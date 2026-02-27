# DIPLOMACY_SPEC Audit Resolution Log

> **Audit:** DIPLOMACY_AUDIT_RESULTS.md (Feb 27, 2026)
> **Spec Version:** v2.0 → v2.1
> **Resolution Date:** Feb 27, 2026

---

## Summary

| Category | Total | Resolved | Deferred | Notes |
|----------|-------|----------|----------|-------|
| Critical | 3 | 3 | 0 | All resolved |
| Major | 8 | 8 | 0 | All resolved (M8 resolved as explicit deferral) |
| Minor | 8 | 7 | 1 | m4 partially addressed |
| Exploits | 11 | 6 | 1 | E7 deferred, E1/E2/E5/E6/E9/E10 already blocked |
| Edge Cases | 15 | 15 | 0 | All added to §12 |
| **Total** | **45** | **39** | **2** | **4 were already blocked in v2.0** |

---

## Critical Issues

| Finding | Resolution | Location in Spec |
|---------|-----------|-----------------|
| C1: DP Authority Threshold | Fixed §10c to say "Authority >= 60 → +1 DP" matching §4a | §10c Integration Points table |
| C2: Harshness Formula | Added §6c.1 Harshness Value Table with per-clause values, formula, and worked example | §6c.1 (new section) |
| C3: Session 1 Risk | Split into Session 1A (regions) + 1B (marshals). Both rated HIGH. Added mandatory pre-session codebase audit per DD6 | §14 Session Plan |

---

## Major Issues

| Finding | Resolution | Location in Spec |
|---------|-----------|-----------------|
| M1: Dispatch Event Types | Added §10d with 21 enumerated event types following JEALOUSY_SPEC pattern | §10d (new section) |
| M2: Notification Templates | Added §10e with 11 notification types, priority levels, and templates | §10e (new section) |
| M3: Counter-Offer Algorithm | Defined deterministic 5-step algorithm with per-nation desire table | §9b (expanded) |
| M4: Vassal Marshal Transition | Added EC-K.1 specifying Trust (40), dict membership, relationships, serialization | §12 EC-K.1 |
| M5: Conflicting Alliance Obligations | Added §5b.3 with explicit resolution rule (higher-relation partner wins) | §5b.3 (new section) |
| M6: Session 3 Risk | Split into Session 3A (parser routing) + 3B (AI proposals). Both rated HIGH | §14 Session Plan |
| M7: Save Migration Plan | Added save-breaking version bump to Session 1A scope + Integration Risk Points | §14 Session 1A + Risk table |
| M8: AI-AI Diplomacy Scope | §9c explicitly marked DEFERRED TO SESSION 6 with blockquote deferral notice and impact assessment | §9c (deferral notice added) |

---

## Minor Issues

| Finding | Resolution | Location in Spec |
|---------|-----------|-----------------|
| m1: Authority annotation | Fixed "authority ~60" to "authority ~100, well above ≥60 threshold" | §4a DP Generation |
| m2: Starting economy trade income | Added explicit note about trade income from PEACE states (+100g for France, +100g for Austria) | §1d (after British Naval Income) |
| m3: Vassal courting session | Assigned to Session 4 scope | §14 Session 4 |
| m4: Continental System check | Added simplified participation check formula (not full acceptance) with 3 conditions and timing | §5d (within code block) |
| m5: War score "starting regions" | Defined `nation_starting_regions` dict in §13 as static data from §1b | §13 v2.1 New Fields |
| m6: DiplomaticRepresentative serialization | Added field-by-field `to_dict()`/`from_dict()` with types and defaults | §13 (after class definition) |
| m7: Godot int() wrapping | Added to Integration Risk Points table in §14 | §14 Integration Risk Points |
| m8: Nation relations vs marshal relationships | Added terminology clarification paragraph to §1a | §1a (after AP paragraph) |

---

## Exploits

| Finding | Resolution | Location in Spec |
|---------|-----------|-----------------|
| E1: Treaty-break-repropose loop | Already blocked in v2.0 (relation math self-corrects) | — |
| E2: Armistice chaining | Already blocked in v2.0 (§5b.2 cooldown) | — |
| E3: Turn-1 Saxony vassalization | Added OPEN_BORDERS minimum requirement for treaty vassalage | §5b transition rules (both locations) |
| E4: Uncapped deal sweetener | Added +30 cap on all sweetener clauses combined | §6b (after sweetener table) |
| E5: Alliance flip-flop | Already blocked in v2.0 (severe penalties) | — |
| E6: Decisive battle farming | Already blocked in v2.0 (±20 cap per war) | — |
| E7: Defiance avoidance at max stats | DEFERRED — flagged for Building Blocks-aligned redesign. Current 2% floor retained as spec value | §3a (deferral note added) |
| E8: Free protection guarantee | Reduced bonus from +5 to +3 when guarantor already at war with all of target's enemies | §6b sweetener table (parenthetical) |
| E9: Trade income cycling | Already blocked in v2.0 (monotonic) | — |
| E10: Continental System overstack | Already blocked in v2.0 (200g cap) | — |
| E11: Post-treaty-break state | Clarified: returns to one level below the broken treaty | §7d (new bullet) |

---

## Edge Cases (Audit EC-1 through EC-15)

| Audit EC | Spec EC | Resolution | Location |
|----------|---------|-----------|----------|
| EC-1: Player cedes Paris | EC-II | EXTREME objection, -1 DP permanent, skill -2 until recaptured, trust -5 all marshals | §12 EC-II |
| EC-2: Cross-proposal race | EC-JJ | Player proposals resolve first, second auto-cancelled | §12 EC-JJ |
| EC-3: Vassal marshal transition | EC-K.1 | Trust 40, joins world.marshals, Professional(0) relationships with French marshals | §12 EC-K.1 |
| EC-4: Breaking armistice | EC-KK | Enhanced penalties: -50 target, -30 all, +25 threat | §12 EC-KK |
| EC-5: French treaties → vassal territory | EC-LL | Yes for PUPPET/SATELLITE, independent for AUTONOMOUS | §12 EC-LL |
| EC-6: Nation bankruptcy | EC-MM | Gold floor 0, clause defaults after 3 turns, -5 relation per default | §12 EC-MM |
| EC-7: Mission target declares war | EC-NN | Mission auto-cancels, DP lost, Talleyrand IDLE | §12 EC-NN |
| EC-8: Decisive battles after re-war | EC-OO | Records persist for display, war score resets per EC-W | §12 EC-OO |
| EC-9: Conflicting alliances | §5b.3 | Must choose. AI: higher-relation partner. Added as full subsection | §5b.3 |
| EC-10: Continental System conquered | EC-PP | Auto-exit, members list updated | §12 EC-PP |
| EC-11: Successful sabotage | EC-QQ | Confront/Overlook choice persists even when outcome is positive | §12 EC-QQ |
| EC-12: Simultaneous vassal deterioration | EC-RR | Intended. Cascade is price of empire | §12 EC-RR |
| EC-13: DP drops below mission cost | EC-SS | 1-turn warning before auto-pause | §12 EC-SS |
| EC-14: Alliance cascade loop | EC-TT | cascade_processed set prevents re-processing | §12 EC-TT |
| EC-15: Sovereignty change + Continental System | EC-UU | Per-sovereign. PUPPET/SATELLITE auto-join, AUTONOMOUS independent | §12 EC-UU |

---

## Design Decisions (DD1-DD8)

| Decision | Resolution | Location |
|----------|-----------|----------|
| DD1: Vassal Carving | Full §8f added. Auto-generated + player rename. Size scaling. Grant to existing vassals. Edge cases EC-VV, EC-WW | §8f (new section) |
| DD2: Metternich personality | Metternich → Schemer (skill 9). Einsiedel → Dove. 4 types all in use. Opportunist NOT added per user override | §2a, §2b, §6b |
| DD3: Feasibility Requests | Full §2g added. 0 DP cost, 5 difficulty tiers, Schemer bias, discovery mechanic | §2g (new section) |
| DD4: Formula Feedback | Full §6f added. Component-to-natural-language table, implementation pattern | §6f (new section) |
| DD5: Sweetener Cap + Per-Turn | +30 cap added. Manpower/turn and AP/turn offer variants. Protection reduced contextually | §6b, §7a |
| DD6: Session Plan | Session 1 split (1A/1B), Session 3 split (3A/3B). All HIGH risk. Pre-session audit required | §14 |
| DD7: Deferred Items | Session 6 now has explicit table with 7 items, rationale, impact, and target | §14 Session 6 |
| DD8-1: British subsidy | Added to §9c as AI behavior. Deferred to Session 6 | §9c |
| DD8-2: Vassal defection cascade | Added to §8d as tipping point mechanic (war score < -30 trigger) | §8d |
| DD8-3: Armed mediation | Added to §5c as Schemer-specific AI behavior (+5 coalition bonus on rejection) | §5c |
| DD8-4: Escalating harshness | Added to §6c.1 as +5 modifier for previously defeated nations | §6c.1 |

---

## Deferred Items (with rationale per DD7)

| Item | Why Deferred | Impact | Target |
|------|-------------|--------|--------|
| E7: Defiance floor redesign | Needs Building Blocks-aligned redesign — should mirror V2b defiance pattern | Defiance floor stays at 2% (manageable). Players can trivially neutralize at max stats | Next design session |
| AI-AI diplomacy (§9c) | Not required for Walking Skeleton player-facing loop | World feels less alive | Session 6 |
| Continental System full | Economic warfare is flavor, not core | Minor tool missing | Session 6 |
| Fog-filtered diplomatic intel | Existing fog works | Slightly more info visible than intended | Session 6 |
| Campaign log diplomatic events | Display-only | No diplomatic history in log | Session 6 |
| Special acceptance bonuses (§6d) | Generic formula works | Nation-specific desires not reflected | Session 6 |
| British subsidy (DD8-1) | AI behavior polish | Britain doesn't finance coalitions | Session 6 |
| Armed mediation (DD8-3) | Schemer AI polish | No coalition bonus from rejected proposals | Session 6 |
