# GPT Next Audit Brief

> Purpose: run a focused follow-up audit that answers the next unresolved questions after `docs/GPT_AUDIT_PLAN_RESULTS.md`.
>
> This is not another omnibus "check everything" pass. It is a targeted audit of the areas most likely to decide whether the current game feels compelling, fair, and extensible:
>
> 1. Does the first hour reveal the game's strengths, or bury them behind friction?
> 2. Are combat, diplomacy, and defeat states legible enough for a new player to form plans?
> 3. Is the enemy AI smart enough, distinct enough by personality, efficient enough, and organized enough in code to keep scaling?

---

## Why This Audit Exists

The broad synthesis audit already answered the big structural question:

- the game is "promising but obscured"
- the strongest immediate problems are opening-friction, diplomacy interruption burden, combat teaching, and sudden defeat clarity
- full-map expansion is still blocked by renderer and scale issues, but that is not the highest-value discovery target for the very next audit

At the same time, the latest playtest surfaced four fresh issues that are mostly player-experience problems, not generic architecture problems:

- `PL-26` combat feels hopeless
- `PL-27` AI proposal spam blocks play
- `PL-28` defeat arrives with no warning
- `PL-29` no new-game endpoint

The next audit should therefore focus on the part of the project that can still most easily hide or destroy the fun:

- the player's first 30-60 minutes
- the clarity of counterplay and pacing
- enemy AI behavior, personality differentiation, fairness, efficiency, and maintainability

---

## Primary Questions

### A. First-Hour Experience

- Does the game teach the player how to succeed before it punishes them for ignorance?
- Do the first few obvious actions produce understandable outcomes?
- Does the command -> response loop feel dramatic and strategic, or mostly interruptive?
- Are the strongest systems visible early, or only discoverable after too much friction?

### B. Combat and Counterplay Clarity

- Is the common Ney -> Wellington opener a balance trap, a teaching failure, or both?
- Are defender bonuses, terrain, stance, support, and personality effects stacking in a way the player can realistically learn?
- Does the game communicate how bombardment, coordination, regrouping, or flanking improve outcomes?
- Are losses frustrating in a fair way, or do they feel arbitrary and hopeless?

### C. Diplomacy Pacing and Modal Burden

- Do incoming diplomatic proposals create strategic texture, or mostly steal turns from the player?
- Should proposals remain blocking, become queueable, or become selectively blocking?
- Are diplomacy popups frequent enough to feel alive but rare enough to preserve operational momentum?

### D. Defeat-State Legibility

- Can the player tell how close they are to losing?
- Are defeat rules fair, telegraphed, and aligned with the design fantasy?
- Are the current defeat conditions visible through the dispatch, notifications, ledger, or top bar?

### E. Enemy AI Quality

- Is the enemy AI smart enough to feel like a capable opponent instead of a script with lucky bonuses?
- Does AI behavior actually differ by personality and nation in ways that matter in play?
- Does the AI win because it makes good decisions, or because it benefits from hidden knowledge and stacked advantages?
- Does the AI create interesting pressure, or mostly repetitive/opaque punishment?

### F. Enemy AI Structure and Efficiency

- Is `backend/ai/enemy_ai.py` still organized enough to keep extending without regression-heavy edits?
- Are scale-sensitive AI decisions doing unnecessary repeated scans or omniscient queries?
- Can the current AI architecture support future fog-aware and 80-100 region behavior without a rewrite?
- Is the AI code "long but coherent," or "long enough that correctness now depends on memory and luck"?

---

## Audit Rules

1. Treat docs as hypotheses, not truth.
2. Prefer current code, tests, and direct command/play evidence over historical notes.
3. Separate these categories clearly:
   - balance problem
   - onboarding/teaching problem
   - UX flow problem
   - AI decision-quality problem
   - AI fairness problem
   - AI architecture/efficiency problem
4. Do not confuse "AI wins" with "AI is smart."
5. Do not confuse "AI is different by numbers" with "AI is meaningfully different by personality."
6. Do not recommend a rewrite unless the audit proves that extension risk or scale cost is unacceptable.
7. If a problem can be solved by better teaching, better surfacing, or one cleaner contract, do not jump straight to mechanical overhaul.
8. Every finding must include evidence: code reference, test evidence, probe, play evidence, or reproducible scenario.

---

## Read First

- `docs/GPT_AUDIT_PLAN_RESULTS.md`
- `docs/BUG_FIXES.md` sections `PL-26` through `PL-29`
- `docs/STATUS.md`
- `docs/VISION.md`
- `docs/DESIGN_REFINEMENT.md`
- `docs/ENEMY_AI_REFERENCE.md`
- `docs/ROADMAP.md` sections on map scale, AI scale, and Pre-EA polish

Priority code surfaces:

- `backend/ai/enemy_ai.py`
- `backend/ai/ai_diplomacy.py`
- `backend/game_logic/combat.py`
- `backend/game_logic/turn_manager.py`
- `backend/models/world_state.py`
- `backend/main.py`
- `godot-client/project-sovereign/scripts/main.gd`

---

## Recommended Audit Setup

Use a fresh audit thread, but keep the scope tight. This audit should be run as focused passes, not as one giant freeform review.

Recommended pass order:

1. Baseline snapshot
2. First-hour experience pass
3. Combat and counterplay pass
4. Diplomacy pacing pass
5. Defeat-state clarity pass
6. Enemy AI gameplay and personality pass
7. Enemy AI organization and efficiency pass
8. Final synthesis

If time is limited, do not skip passes 1, 2, 6, or 7.

### Scope Boundaries

- `PL-29` should be verified as a real usability gap, but it does not need its own deep audit pass unless investigation uncovers state-reset or save/load corruption risk.
- Full renderer replacement is not the primary target of this audit. Only revisit it if it directly blocks first-hour clarity or AI evaluation.
- Full 80-100 region optimization is not the primary target either. This audit should instead identify the current AI and contract assumptions that would obviously fail at that scale.

---

## Phase 0: Baseline Snapshot

Record:

- current branch
- commit hash audited
- clean `HEAD` vs dirty tree
- current claimed test count from `docs/STATUS.md`
- exact code/tests/play surfaces inspected
- whether the audit covers local uncommitted work

Outputs:

- audit date
- branch
- commit hash
- scope note

---

## Phase 1: First-Hour Experience Pass

This is the highest-priority pass.

### Method

- Play or probe the first 5-10 turns as a new player, not as an insider optimizing around known systems.
- Prefer the most obvious commands a new player would try first.
- Record where the game teaches, misleads, interrupts, or punishes.
- Note whether each frustrating moment is caused by numbers, missing explanation, or UI flow.

### Evaluate

- opening momentum vs paralysis
- "obvious first move" outcomes
- usefulness of objections and suggestions
- clarity of combat consequences
- timing/frequency of diplomacy interruptions
- whether the player can tell what a good turn looks like
- whether reports and popups support planning or just add process

### Required Deliverable

Produce:

- top 5 first-hour strengths
- top 5 first-hour friction points
- 3 moments where the game taught well
- 3 moments where it punished before teaching
- verdict: `clear`, `promising but obscured`, or `structurally hostile`

---

## Phase 2: Combat and Counterplay Pass

This pass should explicitly investigate `PL-26`.

### Method

- Reproduce the common early Wellington fight and adjacent alternatives.
- Compare naive attack, bombardment-first, better coordination, and regrouped attacks.
- Check whether the attacker has any understandable path to success without insider knowledge.

### Evaluate

- defender advantage stacking
- attacker reward for superiority and preparation
- common-opener trap design
- clarity of battle output
- whether battle text actually teaches the counterplay it expects
- whether tutorial, dispatch, popup, or tooltip surfaces should carry more of the teaching load

### Required Deliverable

Produce:

- verdict on `PL-26`: `balance`, `teaching`, `starting-state trap`, or `mixed`
- smallest fix that improves fairness without flattening combat depth
- specific recommendation on whether to tune numbers, add guidance, change setup, or all three

---

## Phase 3: Diplomacy Pacing Pass

This pass should explicitly investigate `PL-27`.

### Method

- Observe several short turn sequences where AI proposals are likely.
- Count proposal frequency, repeat frequency, and how often they block normal play.
- Distinguish "proposal quality is good" from "proposal delivery is too interruptive."

### Evaluate

- AI proposal frequency and cooldown reality
- same-nation repeat annoyance
- blocking vs queueable response design
- whether modal dialogue belongs before or after core operational actions
- whether proposals feel urgent enough to justify their interruption cost

### Required Deliverable

Produce:

- verdict on `PL-27`: `frequency`, `cooldown`, `blocking flow`, or `mixed`
- recommendation: keep blocking, partially queue, or fully queue
- concrete anti-spam rules worth adding if needed

---

## Phase 4: Defeat-State Clarity Pass

This pass should explicitly investigate `PL-28` and also cross-check the still-suspect capital-loss rule.

### Method

- Reproduce or inspect defeat-state transitions.
- Determine the exact loss conditions in code and what the player is told beforehand.
- Compare what the player needs to know with what the UI currently surfaces.

### Evaluate

- actual defeat conditions
- defeat-warning timing
- visibility of danger in dispatch / notifications / HUD / ledger
- fairness of the rule itself
- consistency between docs, tests, and code

### Required Deliverable

Produce:

- a player-readable explanation of current defeat logic
- verdict on `PL-28`: `warning gap`, `bad rule`, `bad threshold`, or `mixed`
- recommended warning ladder: 1-step, 2-step, or 3-step escalation

---

## Phase 5: Enemy AI Gameplay and Personality Pass

This is the new mandatory pass that the previous synthesis only covered partially.

### Goal

Determine whether enemy AI is:

- competent
- fair
- personality-distinct
- strategically interesting

### Method

- Inspect the P-priority flow in `enemy_ai.py`.
- Probe representative decisions across at least aggressive and cautious personalities.
- Compare outcomes in combat, retreat, recapture, regrouping, bombardment, garrisoning, and diplomacy if relevant.
- Record whether observed differences matter in play, not just in constants.

### Evaluate

- attack vs hold thresholds by personality
- retreat and survival instincts
- recapture behavior and front pressure
- use of coordination, artillery, and support opportunities
- personality-consistent risk appetite
- variety vs repetition
- whether AI feels "humanly legible" rather than erratic or omniscient
- whether AI-generated pressure creates interesting choices for the player

### Red Flags

- different personalities collapsing into the same behavior in practice
- AI making obviously bad repeated moves
- AI pressure deriving mostly from hidden information
- AI exploiting narrow player pain points instead of playing broadly well
- personality labels that matter in docs more than in gameplay

### Required Deliverable

Produce:

- AI scorecard on `competence / fairness / personality differentiation / pressure quality`
- 3 examples of smart AI behavior
- 3 examples of weak, unfair, repetitive, or misleading AI behavior
- verdict: `smart and characterful`, `smart but flat`, `flavorful but weak`, or `unfairly effective`

---

## Phase 6: Enemy AI Organization and Efficiency Pass

This pass checks whether the AI can keep growing without turning into an unmaintainable hazard.

### Goal

Determine whether the AI code is still extensible enough for near-term shipping and future scale work.

### Method

- Inspect `backend/ai/enemy_ai.py` and its main dependencies.
- Identify repeated world scans, omniscient lookups, duplicated logic, and extension chokepoints.
- Cross-check the AI code against current tests and architecture notes.
- If practical, estimate hot-path cost from code structure or lightweight profiling; if not, document the likely cost drivers by inspection.

### Evaluate

- responsibility boundaries inside `enemy_ai.py`
- whether major decision layers are linear and understandable
- how often AI reaches into raw world state vs helper seams
- omniscient helper usage on paths that should become fog-aware later
- scale risk for 80-100 regions
- ease of adding new behaviors without editing many unrelated branches
- test protection around AI regressions

### Key Questions

- Is the AI code "large but coherent" or "large and brittle"?
- Which behaviors are safe to extend now?
- Which scale or fairness assumptions must be fixed before 80-100 regions?
- Is there one high-leverage structural improvement that would make future AI work safer?

### Required Deliverable

Produce:

- subsystem rating: `safe to extend`, `fragile but manageable`, or `likely to regress`
- top 3-5 AI architecture risks
- top 3-5 AI efficiency or scale risks
- smallest structural improvements worth doing next

---

## Phase 7: Final Synthesis

The audit should end with the following outputs:

1. Executive verdict
   - Is the current game experience becoming clearer or still burying its best ideas?
   - Is the enemy AI good enough for the present 19-region game?
   - Is the enemy AI structurally ready for future scale work?

2. Findings list
   - ordered by severity and player impact

3. Problem classification
   - which issues are primarily numbers
   - which are teaching
   - which are UI flow
   - which are AI quality
   - which are AI structure/scale

4. Priority roadmap
   - fix now
   - tune via playtesting
   - design-gate next
   - defer until map-scale work

5. Confidence statement
   - direct verification vs inference

---

## Severity Rubric

### Critical

Blocks fairness, ruins the first-hour experience, makes AI feel cheating/stupid, or creates reckless scale risk.

### Major

Strong player frustration, repeated pacing failure, weak AI identity, or meaningful extension/regression risk.

### Moderate

Noticeable weakness, but survivable with the rest of the game intact.

### Low

Polish or clarity improvement with limited immediate impact.

### Note

Useful observation, but not yet worth active change.

---

## Success Criteria

This audit is successful if it answers:

- whether the game's best ideas are visible in the first hour
- whether the player has a learnable path to winning early conflicts
- whether diplomacy interruptions are adding strategy or just stealing tempo
- whether defeat is fair and telegraphed
- whether enemy AI is competent, distinct, fair, efficient, and maintainable enough for continued development

If the audit only produces balance notes, it was too shallow.
If it only produces architecture notes, it missed the player.
If it only says "AI should be smarter" without specifying competence, personality, fairness, and structure separately, it was not rigorous enough.

The correct follow-up audit should connect player experience, design clarity, and AI survivability in one focused pass.
