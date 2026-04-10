# GPT Next Audit Prompt

> Copy everything below the line into a fresh GPT audit session.

---

## PROMPT START

You are conducting a focused audit of the strategy game project "Ink & Iron" in the current local repository.

Do not write code. Do not propose implementation details first. Your job is to inspect the current project state and produce a rigorous audit with findings backed by evidence.

This is a follow-up audit. It is intentionally narrower than a full-project omnibus review.

## Your Mission

Answer these questions with evidence:

1. Does the first hour of play reveal the game's strengths, or bury them behind friction?
2. Are combat, diplomacy pacing, and defeat states legible enough for a new player to form plans?
3. Is the enemy AI smart enough, distinct enough by personality, efficient enough, fair enough, and organized enough in code to keep extending safely?

You must treat these as the priority questions. Do not get distracted into a broad restatement of every known architecture issue unless it directly affects those questions.

## Read First

Read these files before producing findings:

- `docs/GPT_NEXT_AUDIT_BRIEF.md`
- `docs/GPT_AUDIT_PLAN_RESULTS.md`
- `docs/BUG_FIXES.md` sections `PL-26` through `PL-29`
- `docs/STATUS.md`
- `docs/VISION.md`
- `docs/DESIGN_REFINEMENT.md`
- `docs/ENEMY_AI_REFERENCE.md`
- `docs/ROADMAP.md`

Priority code surfaces:

- `backend/ai/enemy_ai.py`
- `backend/ai/ai_diplomacy.py`
- `backend/game_logic/combat.py`
- `backend/game_logic/turn_manager.py`
- `backend/models/world_state.py`
- `backend/main.py`
- `godot-client/project-sovereign/scripts/main.gd`

Read other files only as needed to support or challenge a finding.

## Audit Rules

1. Treat docs as hypotheses, not truth.
2. Prefer current code, tests, and direct probes over historical claims.
3. Separate these problem types explicitly:
   - balance problem
   - onboarding/teaching problem
   - UX flow problem
   - AI decision-quality problem
   - AI fairness problem
   - AI architecture/efficiency problem
4. Do not confuse "AI wins" with "AI is smart."
5. Do not confuse "different constants" with "meaningful personality differentiation."
6. Do not recommend a rewrite unless you can prove the current structure is not survivable.
7. Every finding must include evidence: file references, tests, command probes, or directly observed behavior.

## Required Method

Follow this order:

1. Capture a baseline snapshot.
2. Audit first-hour experience.
3. Audit combat and counterplay clarity.
4. Audit diplomacy pacing and modal burden.
5. Audit defeat-state clarity.
6. Audit enemy AI gameplay quality and personality differentiation.
7. Audit enemy AI organization, efficiency, and future scale risk.
8. End with a synthesis and priority roadmap.

If time is limited, do not skip:

- first-hour experience
- enemy AI gameplay/personality
- enemy AI organization/efficiency

## Baseline Snapshot

Record:

- audit date
- branch
- commit hash audited
- whether the tree is clean or dirty
- whether you audited clean `HEAD`, local uncommitted work, or both
- current claimed test count from `docs/STATUS.md`

## Mandatory Investigation Areas

### 1. First-Hour Experience

Determine whether the game teaches before it punishes.

Check:

- opening momentum vs paralysis
- obvious first moves and their outcomes
- whether objections help or mostly interrupt
- whether reports/popups support planning or add process
- whether the game communicates what a good turn looks like

Required output:

- top 5 first-hour strengths
- top 5 first-hour friction points
- 3 moments where the game taught well
- 3 moments where it punished before teaching
- verdict: `clear`, `promising but obscured`, or `structurally hostile`

### 2. Combat and Counterplay Clarity

This must explicitly investigate `PL-26`.

Check:

- the common Ney -> Wellington opener
- naive attack vs better-prepared attack
- defender bonus stacking
- whether the player has a learnable path to success
- whether battle text teaches the counterplay it expects

Required output:

- verdict on `PL-26`: `balance`, `teaching`, `starting-state trap`, or `mixed`
- smallest fix that improves fairness without flattening combat depth
- whether the main remedy is numbers, surfacing, setup, or mixed

### 3. Diplomacy Pacing and Modal Burden

This must explicitly investigate `PL-27`.

Check:

- AI proposal frequency
- same-nation repeat pressure
- cooldown reality vs intended anti-spam logic
- whether proposals are too blocking for the core campaign loop
- whether proposal delivery is the problem even when proposal logic is sound

Required output:

- verdict on `PL-27`: `frequency`, `cooldown`, `blocking flow`, or `mixed`
- recommendation: keep blocking, partially queue, or fully queue
- concrete anti-spam rules if needed

### 4. Defeat-State Clarity

This must explicitly investigate `PL-28`.

Also cross-check the capital-loss defeat issue documented in the previous synthesis.

Check:

- exact defeat logic in current code
- whether defeat danger is visible before loss
- warning delivery through dispatch, notifications, ledger, or HUD
- fairness and design coherence of the rule itself
- consistency between code, tests, and docs

Required output:

- a player-readable explanation of current defeat logic
- verdict on `PL-28`: `warning gap`, `bad rule`, `bad threshold`, or `mixed`
- recommended warning ladder: 1-step, 2-step, or 3-step

### 5. Enemy AI Gameplay and Personality

This is mandatory.

Determine whether enemy AI is:

- competent
- fair
- personality-distinct
- strategically interesting

Check:

- attack vs hold thresholds by personality
- retreat and survival instincts
- recapture behavior
- use of artillery, coordination, support, regrouping, and positioning
- whether different personalities actually behave differently in practice
- whether AI pressure feels legible or omniscient/opaque

Required output:

- AI scorecard on `competence / fairness / personality differentiation / pressure quality`
- 3 examples of smart AI behavior
- 3 examples of weak, unfair, repetitive, or misleading AI behavior
- verdict: `smart and characterful`, `smart but flat`, `flavorful but weak`, or `unfairly effective`

### 6. Enemy AI Organization and Efficiency

This is mandatory.

Determine whether `backend/ai/enemy_ai.py` and related seams are still extensible enough.

Check:

- responsibility boundaries in `enemy_ai.py`
- duplicated or repeated world scans
- omniscient helper usage that will become dangerous at scale
- ease of adding new behavior without editing many unrelated branches
- whether the AI code is long-but-coherent or long-and-brittle
- likely scale risks for 80-100 regions
- whether test coverage protects the dangerous AI paths

Required output:

- subsystem rating: `safe to extend`, `fragile but manageable`, or `likely to regress`
- top 3-5 AI architecture risks
- top 3-5 AI efficiency or scale risks
- smallest structural improvements worth doing next

## Practical Expectations

You should use a mix of:

- code inspection
- targeted test execution where useful
- backend command probes where useful
- direct comparison against the project docs

If you cannot run a test or probe, say so clearly and explain the limitation.

## Scope Boundaries

- `PL-29` should be verified as a real usability gap, but it does not need a deep standalone audit unless it uncovers state-reset or save/load corruption risk.
- Full renderer replacement is not the primary target of this audit unless it directly blocks first-hour clarity or AI evaluation.
- Full 80-100 region optimization is not the primary target either; instead, identify current AI and contract assumptions that would clearly fail at that scale.

## Output Format

Organize the audit in this order:

### 1. Baseline Snapshot

### 2. Executive Verdict

Answer directly:

- Is the first-hour experience clear or still obscured?
- Is combat currently learnable and fair?
- Is diplomacy pacing helping or hurting the game?
- Is defeat properly telegraphed?
- Is the enemy AI good enough for the current 19-region game?
- Is the enemy AI structurally ready for future scale work?

### 3. Findings

List findings ordered by severity and player impact.

For each finding, include:

- title
- severity
- category
- evidence
- why it matters
- smallest credible fix direction

### 4. First-Hour Scorecard

Include the required strengths/frictions/teaching-vs-punishment outputs.

### 5. Enemy AI Scorecard

Include both gameplay/personality and organization/efficiency outputs.

### 6. Problem Classification

Bucket the major problems into:

- numbers
- teaching
- UI flow
- AI quality
- AI structure/scale

### 7. Priority Roadmap

Use these buckets:

- fix now
- tune via playtesting
- design-gate next
- defer until map-scale work

### 8. Confidence Statement

Separate:

- directly verified
- strong inference
- not verified

## Severity Rubric

### Critical

Blocks fairness, ruins the first hour, makes AI feel cheating/stupid, or makes future AI scale work reckless.

### Major

Strong player frustration, repeated pacing failure, weak AI identity, or meaningful extension/regression risk.

### Moderate

Noticeable weakness, but survivable.

### Low

Polish or clarity improvement with limited immediate impact.

### Note

Useful observation, not yet clearly actionable.

## Final Constraint

If your audit only produces balance notes, it is too shallow.
If it only produces architecture notes, it missed the player.
If it says "AI should be smarter" without separating competence, personality differentiation, fairness, and code structure, it is not rigorous enough.

Your job is to connect player experience, design clarity, and AI survivability in one focused audit.

## PROMPT END
