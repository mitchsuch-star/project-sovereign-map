# Bombardment Spec Audit Prompt (v2)

> **Purpose:** Paste this into a fresh Claude session to get a second-pass audit of the expanded Bombardment Spec.
> **Pre-requisite:** The session needs access to the codebase.
> **Context:** The spec has already been through one audit pass that added terrain modifiers, collateral damage, strategic HOLD, AI changes, and expanded objections. This second audit focuses on internal consistency, math validation, and edge cases across the new systems.

---

## Prompt

You are performing a **second-pass audit** of a game design specification for **Ink & Iron**, a Napoleonic strategy game. The spec has already gone through one major audit that expanded it significantly. Your job is to find problems the first audit may have introduced or missed.

### Game Context

**Core loop:** Player types commands like "Marshal Ney, attack Wellington." Marshals have personalities (aggressive, cautious, literal) and can object based on a deterministic ConcernLevel system (NONE/MILD/MODERATE/STRONG/EXTREME). MILD = flavor text only, MODERATE+ = popup requiring player choice. Trust rises when the player listens, falls when they override.

**Unit types:**
- **Infantry** (Davout, Grouchy): Standard troops. Movement range 1. Fight decisive battles.
- **Cavalry** (Ney, Uxbridge): Movement range 2. Recklessness system — winning attacks builds recklessness, at 3+ triggers "Glorious Charge" popup (2x damage).
- **Artillery** (Drouot, PrinceAugust): Can attack adjacent regions (ranged). Can't attack after moving. Cavalry counter: +30% when cavalry attacks artillery. 2x fort degradation rate.

**Strategic commands:** Multi-turn autonomous orders (MOVE_TO, PURSUE, HOLD, SUPPORT) that marshals execute each turn without player input. Cost 2 AP. Key mechanic: aggressive marshals on HOLD sally out (attack adjacent enemies, then return).

**AP system:** 4 base AP per turn. Standard attack costs 1 AP. Strategic orders cost 2 AP to issue (0 per turn to execute via `_strategic_execution`).

### Your Task

Read `docs/BOMBARDMENT_SPEC.md` thoroughly (it's ~940 lines), cross-reference against the actual codebase, then provide all 5 parts below. **Be specific with line references and code citations.**

---

### PART 1: Internal Consistency Check

The spec was expanded in one pass, adding terrain (§4.1), collateral (§4.4), strategic HOLD (§9), and AI changes (§10). These systems interact. Check for:

1. **Math validation:** Run the damage formulas manually for several scenarios:
   - Drouot (shock 7, 25k) bombards Wellington (68k) on each terrain type. Do the numbers make sense? Is any terrain too punishing or too lenient?
   - Area bombardment on a region with 3 forces (2 enemy, 1 friendly). What's total damage dealt vs. friendly fire taken? Is the ratio reasonable?
   - Drouot at bombardment_streak 4 with diminishing returns hook active. What's effective DPS? Still worth doing?
   - Collateral damage on a 5k garrison detachment. Does it survive? Should it?

2. **Contradictions:** Does any section contradict another? E.g.:
   - §4.6 says "no stance modifiers" — does this interact with any existing stance-dependent code paths?
   - §9 says HOLD fires 1/turn for cautious — but §4.5 says max is 2/turn. If the player cancels HOLD mid-turn after 1 strategic bombardment, can they manually fire 1 more? The spec implies yes but verify.
   - §7.1 "cease fire" trigger needs bombardment_streak >= 1. §9 fires 1/turn. After turn 1 of HOLD, streak = 1. Does the trigger fire immediately on cancel? Is that too aggressive?

3. **Missing interactions:** What happens when:
   - Artillery on HOLD has a target in the same region AND adjacent targets? (§9.5 says HOLD breaks, but what if the enemy retreated INTO artillery's region mid-turn?)
   - Collateral damage kills a marshal that was the primary target of another pending strategic order (PURSUE)?
   - Area bombardment hits a marshal that's currently retreating or broken?
   - Friendly fire hits a marshal that's at trust <= 20 (redemption threshold)?

---

### PART 2: Collateral System Deep Dive

The collateral/area bombardment system (§4.4) is entirely new and the most complex addition. Stress-test it:

1. **Is 40% collateral chance too high?** In a region with 4 forces, expected collateral hits = 1.2 forces per bombardment. With 2 bombardments/turn, that's ~2.4 collateral hits. Does this make targeted bombardment feel uncontrolled?

2. **Is 25% collateral damage the right ratio?** Compare: primary takes ~4k, collateral takes ~1k. Is 1k enough to matter? Too much for an "accident"?

3. **Area bombardment at 60% — is this ever the right choice?** Compare: targeting the weakest enemy for a kill vs. spreading 60% damage across everyone. When is area bombardment strategically optimal? If the answer is "never," the mechanic is dead weight.

4. **Friendly fire trust penalty (-5) — is this too harsh?** The player ordered the bombardment, but the game chose to hit their friend. Does punishing the player for a probabilistic outcome feel fair? Compare to other trust changes in the game.

5. **Friendly fire + objection interaction:** If Drouot's collateral hits Ney, and next turn the player orders Drouot to bombard again, can Ney's "friendly fire victim" V2b objection trigger? What's the timing?

6. **Parser routing for area vs targeted:** The spec says "if target matches a region name instead of a marshal name, route to area bombardment." But what if a region and a marshal have similar names? What if the player says "bombard the enemy at Waterloo" — is that area or targeted? Define the disambiguation rule.

---

### PART 3: AI Behavior Verification

Cross-reference §10 against `backend/ai/enemy_ai.py` to verify:

1. **Where exactly in the priority tree does the bombardment limit check go?** §10.1 says "in `_find_attack_opportunity()`" — but there are multiple entry points to attack. Is that the only place? What about P0 engagement, P3.25 counter-punch?

2. **The ratio bypass:** §10.1 says skip ratio checks for ranged bombardment. But `_find_attack_opportunity()` has personality-specific ratio thresholds at multiple points. Trace the exact code path PrinceAugust takes and identify every ratio check that needs bypassing.

3. **Collateral awareness:** §10.4 says "acceptable for now" that AI doesn't avoid friendly fire. But if PrinceAugust area-bombards a region where a Prussian ally is positioned, that's a real gameplay problem. How likely is this scenario given the current map and starting positions?

4. **Post-bombardment behavior:** After PrinceAugust fires 2 bombardments, the AI falls through to P5+. What does PrinceAugust actually do? Fortify? Position? What's the expected AI turn sequence for PrinceAugust?

5. **AI and terrain:** Does the AI consider terrain bombardment modifiers when selecting targets? §10.2 sorts by fort value and density but not terrain. Should the AI prefer targets on plains (+10% damage) over targets in mountains (-40%)?

---

### PART 4: Strategic HOLD Edge Cases

The HOLD bombardment (§9) adds a new behavior path to an already complex system. Verify:

1. **Interaction with timed HOLD (Phase M):** §9 doesn't mention timed holds. If a player issues "Drouot, hold Belgium for 3 turns" — does the timed expiry check in `_execute_hold()` still fire correctly before the artillery override?

2. **Interaction with HOLD en-route:** §9 says "add artillery path before existing personality checks." But the HOLD handler first checks if the marshal is AT the hold position (line 1175). The artillery override should only fire when at position. Verify the insertion point is correct.

3. **`bombardment_target` field lifecycle:** When is it set? When is it cleared? What happens on save/load mid-HOLD? What if the target marshal is destroyed — does the field become a dangling reference?

4. **Strategic HOLD + manual bombardment in same turn:** Player issues HOLD on turn 5. Strategic executor fires 1 bombardment. Player then cancels HOLD (1 AP) and manually fires. `bombardments_this_turn` should be 1 from strategic + 1 from manual = 2. Verify the counter is shared correctly.

5. **Objection cascade:** Player cancels HOLD → "cease fire" MODERATE objection → player insists → trust drops. Now the player tries to manually bombard → "last-shot advisory" MILD fires. Is two objections in one action sequence too much?

---

### PART 5: Final Verdict

1. **Top 3 MUST FIX items** — things that will cause bugs or bad gameplay if shipped as-is.

2. **Top 3 SHOULD CHANGE items** — things that will work but aren't good enough.

3. **One thing to CUT** — identify the weakest new addition that adds complexity without enough value. Recommend removing it from the spec entirely.

4. **Implementation order** — given all the systems in the spec, what's the safest order to build them? What can be deferred to a follow-up without blocking the core bombardment redesign?

---

### Reference Files to Read

Read these files in order:
1. `docs/BOMBARDMENT_SPEC.md` — The spec being audited (~940 lines)
2. `CLAUDE.md` — Project conventions and golden rules
3. `docs/SYSTEMS_REFERENCE.md` — Section 6b (Artillery Unit Type)
4. `backend/game_logic/combat.py` — Current combat resolution
5. `backend/commands/objection_v2.py` — Current artillery objection triggers
6. `backend/commands/strategic.py` — HOLD command implementation (~line 1130-1365)
7. `backend/ai/enemy_ai.py` — Artillery AI sections (P2 screen ~1312, P4 attack ~1379, P7 positioning ~2786, helpers ~4154)
8. `backend/models/marshal.py` — Marshal class, bombardment fields
9. `backend/models/region.py` — Terrain tables (lines 15-54), verify no `TERRAIN_BOMBARDMENT_MODIFIER` exists yet
10. `backend/commands/executor.py` — `_execute_attack()`, bombardment streak tracking (~line 3030)
11. `backend/models/world_state.py` — `_action_costs` (~line 154), `_process_tactical_states()` for turn resets
