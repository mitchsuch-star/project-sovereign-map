# Bombardment Spec Audit Prompt

> **Purpose:** Paste this into a fresh Claude session to get a comprehensive audit of the Bombardment Spec.
> **Pre-requisite:** The session needs access to the codebase (or paste the spec + referenced files).

---

## Prompt

You are auditing a game design specification for **Ink & Iron**, a Napoleonic strategy game where players type commands to AI marshals who have personalities and can object to orders. The game has a Godot 4 frontend and FastAPI backend.

### Game Context

**Core loop:** Player types commands like "Marshal Ney, attack Wellington." Marshals have personalities (aggressive, cautious, literal) and can object based on a deterministic ConcernLevel system (NONE/MILD/MODERATE/STRONG/EXTREME). MILD = flavor text only, MODERATE+ = popup requiring player choice (trust/insist/compromise). Trust rises when the player listens, falls when they override.

**Unit types:**
- **Infantry** (Davout, Grouchy): Standard troops. Movement range 1. Fight decisive battles.
- **Cavalry** (Ney, Uxbridge): Movement range 2. Recklessness system — winning attacks builds recklessness (0-4), at 3+ triggers "Glorious Charge" popup (2x damage dealt AND taken). Aggressive + cavalry = reckless cavalry.
- **Artillery** (Drouot, PrinceAugust): Can attack adjacent regions (ranged). Can't attack after moving. Cavalry counter: +30% when cavalry attacks artillery. 2x fort degradation rate.

**Strategic commands:** Multi-turn autonomous orders (MOVE_TO, PURSUE, HOLD, SUPPORT) that marshals execute each turn without player input. Cost 2 AP. Key mechanic: aggressive marshals on HOLD will sally out (attack adjacent enemies, then return to position). Literal marshals on HOLD stay put no matter what (the "Grouchy moment" — ignoring cannon fire nearby).

**Current problem:** Ranged bombardment (artillery attacking from an adjacent region) runs through the same `resolve_battle()` as melee combat, producing nonsensical results — artillery "losing" bombardments, taking 20% casualties at range, defenders earning counter-punch from being shelled.

### Your Task

Read `docs/BOMBARDMENT_SPEC.md` thoroughly, then provide:

---

### PART 1: Scorecard

Rate each category 1-10 with brief justification:

| Category | What to evaluate |
|----------|-----------------|
| **Fun** | Will this be enjoyable to play? Does it create interesting decisions? Is the risk/reward compelling? |
| **Historical Accuracy** | Does this feel like Napoleonic artillery? Would a history buff nod along? |
| **Balance** | Is artillery too strong? Too weak? Does it respect the unit type triangle (cavalry > artillery > infantry fortifications > cavalry)? |
| **Mechanical Clarity** | Will players understand what's happening and why? Are the rules intuitive? |
| **Integration Risk** | How likely is this to introduce bugs? Does it interact cleanly with existing systems? |
| **Personality/Drama** | Does this create interesting marshal personality moments? Does artillery feel characterful? |
| **AI Compatibility** | Will the enemy AI (PrinceAugust) use this well? Any decision tree issues? |

---

### PART 2: Artillery Objection Redesign

The spec proposes new objection triggers for cautious artillery (Drouot). But there's a design tension:

**A cautious general commanding artillery WOULDN'T object to bombardment — that's exactly what cautious artillery wants to do (safe, methodical, low-risk).** The current objection triggers feel forced.

Analyze this problem and recommend:

1. **When SHOULD artillery object?** What situations create genuine personality-driven drama for a cautious artillerist? Think about what Drouot would actually care about — ammunition conservation? Target priority? Being ordered away from a good position? Being told to stop firing?

2. **When SHOULD artillery object for an aggressive artillerist?** (Future-proofing — not in current game but design the mechanic.) An aggressive gunner might want to advance closer, fire more aggressively, resist being pulled back.

3. **What about the bombardment limit (2/turn)?** Should objections interact with this? E.g., "Sire, I have one salvo remaining today — let me choose the target" when player orders bombardment with 1 remaining.

4. **Cross-marshal objection opportunities:** Could other marshals object to artillery behavior? E.g., Ney (aggressive) objects when artillery is "wasting time" bombarding instead of letting him charge. Davout (cautious) objects when artillery is ordered to stop bombarding and join a melee.

5. **Provide specific ConcernLevel, trigger condition, and flavor text** for each recommendation.

---

### PART 3: Strategic Command — "BOMBARD" (Artillery Hold Variant)

The game has a strategic HOLD command where aggressive marshals sally out (attack nearby enemies, then return). There's an idea for an **artillery-specific strategic command** that works similarly:

**Concept:** A strategic order where artillery holds position and automatically bombards adjacent enemies each turn — similar to how Ney on HOLD sallies out, but artillery on this order fires bombardments instead.

Evaluate this idea:

1. **Is this a good idea?** Does it add meaningful gameplay or is it just automation of something the player could do manually?

2. **How should it work mechanically?** Consider:
   - Should it use the existing HOLD command with artillery-specific behavior (like aggressive HOLD → sally)?
   - Or should it be a new command type (BOMBARD)?
   - How many bombardments per turn under strategic control? (The spec limits manual to 2/turn)
   - Should the artillery pick its own target based on personality? (Cautious picks fortified targets, aggressive picks weakest?)
   - What happens when no targets are adjacent? Hold and wait? Report to player?

3. **Target priority AI:** If artillery auto-selects targets under strategic command, what should the priority be?
   - Fortified enemies (crack the walls)?
   - Weakest enemies (finish them off)?
   - Enemies threatening a friendly marshal?
   - The same target each turn (sustained bombardment) vs spreading fire?

4. **Personality interaction with strategic bombardment:**
   - Cautious artillery (Drouot): Methodical. Picks fortified targets. Consistent. Would he switch targets if a bigger threat appears? Or stubbornly crack the walls first?
   - How does the cannon fire interrupt work? If Drouot hears a battle nearby, does he redirect fire? Or stay on his assigned target? (The Grouchy Moment for artillery)

5. **Objection on receiving the order:** Would Drouot object to "hold and bombard"? (Probably not — it's exactly what he wants.) What about being told to stop? THAT should be the objection trigger.

6. **Provide a complete mechanical design** if you think this is worth building.

---

### PART 4: Enemy AI Fixes

The spec mentions AI changes are "transparent" but review the current enemy AI artillery behavior and identify issues:

Current AI artillery (PrinceAugust) behavior:
- P2: Screen check — retreat if exposed to enemy cavalry without infantry screen
- P4: Attack — prefers fortified targets for bombardment value
- P7: Anti-oscillation — stays in place if adjacent targets exist
- Position scoring: Prefers spots adjacent to enemies, with infantry screen, friendly territory

With the bombardment redesign:
1. **What AI changes ARE actually needed?** The spec says "none" — is that true?
2. **Should AI artillery use the new strategic BOMBARD command?** If so, when?
3. **Should AI artillery behavior change based on bombardment limit?** (Currently unlimited, becoming 2/turn)
4. **Target selection:** Current AI picks by fort value. With bombardment being a separate path, should priority change?
5. **Identify any edge cases** where AI artillery could get stuck, oscillate, or make obviously bad decisions under the new system.

---

### PART 5: Overall Recommendations

Provide a prioritized list of changes to the spec, categorized as:
- **MUST FIX** — Spec has a design flaw that will cause problems
- **SHOULD CHANGE** — Improvement that significantly enhances the design
- **NICE TO HAVE** — Polish items for later

For each recommendation, explain the problem and your proposed solution.

---

### Reference Files to Read

Read these files in order:
1. `docs/BOMBARDMENT_SPEC.md` — The spec being audited
2. `docs/VISION.md` — Game vision and design philosophy
3. `docs/SYSTEMS_REFERENCE.md` — Section 6b (Artillery Unit Type)
4. `backend/game_logic/combat.py` — Current combat resolution (lines 406-423 for ranged bombardment)
5. `backend/commands/objection_v2.py` — Lines 772-861 for current artillery triggers
6. `backend/commands/strategic.py` — HOLD command implementation (sally mechanic)
7. `backend/ai/enemy_ai.py` — Artillery AI sections (P2 screen, P4 attack, P7 positioning)
8. `backend/models/marshal.py` — Drouot and PrinceAugust definitions (lines 1252-1441)
9. `CLAUDE.md` — Project conventions and golden rules
