# GPT Audit Plan

> Purpose: run an independent GPT-led audit that answers four questions with evidence:
> 1. Is the game fun turn-to-turn?
> 2. Is the design coherent, legible, and strategically interesting?
> 3. Is the codebase organized enough to keep shipping without collapsing under regressions?
> 4. Can the current 19-region implementation scale to a full Europe map without a rewrite?

> This is an audit plan, not an implementation plan. It tells the auditor what to inspect, how to judge it, and what deliverables to produce.

---

## Why This Audit Exists

The project already has strong bug-fix and architecture history:

- `docs/STATUS.md` tracks current phase and test counts
- `docs/ARCHITECTURE_AUDIT_REPORT.md` identifies structural root causes
- `docs/ARCHITECTURE_REFACTORING_PLAN.md` tracks architecture work already completed
- `docs/DESIGN_REFINEMENT.md` tracks post-bug design opportunities
- `docs/MANUAL_TEST_PLAN.md` covers Godot smoke testing
- `docs/ADDING_CONTENT.md` documents map expansion and content growth

That history is valuable, but it is not enough by itself. This audit must verify current reality in code and play, not just trust prior documentation.

---

## Audit Goals

### Goal A: Fun and Strategic Quality

Determine whether the game is actually enjoyable for a player who does not already know the internal systems.

Questions:

- Does the command -> response loop feel satisfying?
- Are marshal personalities creating interesting decisions instead of friction for its own sake?
- Do diplomacy, war, economy, and objections produce meaningful tradeoffs?
- Are losses frustrating in a fair way, or arbitrary and opaque?
- Does the game generate memorable situations instead of repetitive chores?

### Goal B: Design Coherence

Determine whether the game's systems support the same fantasy and strategic identity.

Questions:

- Do the mechanics reinforce the Napoleonic command fantasy?
- Are there dominant strategies that flatten player choice?
- Are system explanations clear enough that players can form plans?
- Do UI surfaces expose the right information at the right time?
- Are any systems present but not yet pulling their weight?

### Goal C: Code Structure and Expandability

Determine whether the codebase can keep growing without multiplying regressions.

Questions:

- Are core pipelines centralized, or are important side effects still scattered?
- Are backend/frontend contracts explicit and stable?
- Is serialization disciplined enough for large feature growth?
- Are tests catching the dangerous categories of regression?
- Can new content be added without touching too many files?

### Goal D: Full-Map Scalability

Determine whether the current architecture can scale from the 19-region map to the planned 80-100 region Europe map described in `docs/ROADMAP.md`.

Questions:

- Which systems scale linearly and are fine?
- Which systems are acceptable at 19 regions but break down at 80+?
- Which assumptions are currently hardcoded around map size, nation count, marshal count, or AI omniscience?
- What must be refactored before full-map implementation starts?
- What should be deferred until the full-map branch actually exists?

---

## Audit Rules

1. Treat docs as hypotheses, not truth.
2. Prefer current code, tests, and runtime behavior over historical notes.
3. Separate "not implemented yet" from "implemented badly."
4. Findings must include evidence: file references, test evidence, play evidence, or reproducible scenarios.
5. Distinguish clearly between:
   - bug
   - design flaw
   - architecture risk
   - future scaling risk
6. Do not recommend large rewrites unless the audit proves the current structure will not survive growth.
7. Whenever possible, propose the smallest structural fix that prevents an entire class of bugs.

---

## Recommended Audit Setup

Use fresh GPT audit threads with narrow scopes instead of one giant omnibus review.

Recommended passes:

1. Gameplay and fun pass
2. Design and balance pass
3. Architecture and code health pass
4. Backend/frontend contract pass
5. Test and regression coverage pass
6. Full-map scalability pass
7. Final synthesis pass

Each pass should produce findings first, then a short summary, then concrete next actions.

---

## Phase 0: Baseline Snapshot

Before making any judgments, capture the current project state.

The auditor should record:

- current branch
- working tree status
- latest claimed test count from `docs/STATUS.md`
- actual targeted test results for touched systems
- current phase and roadmap assumptions
- major uncommitted work that may affect audit validity

Outputs:

- audit date
- branch name
- commit hash audited
- note on whether the audit covers `HEAD`, local uncommitted changes, or both

---

## Phase 1: Gameplay and Fun Audit

This is the most important phase. A well-structured codebase that is not fun still fails.

### Method

- Run several short campaign slices or scripted play sessions
- Include both "play to win" and "play like a curious new player" styles
- Use both backend-only interaction and Godot UI interaction where practical
- Record where the game produces delight, tension, confusion, or boredom

### What To Evaluate

- Opening turns: do they create momentum or paralysis?
- Core command loop: is typing orders satisfying and reliable?
- Objections: helpful drama or constant interruption?
- Combat: understandable enough to plan around?
- Diplomacy: real alternative to brute-force conquest, or mostly noise?
- Dispatch, ledgers, and reports: decision support or information overload?
- Failure states: fair consequences or opaque punishment?
- Mid-game pacing: do turns get more interesting or more tedious?

### Required Deliverable

Produce:

- Top 5 fun strengths
- Top 5 fun killers
- 3 examples of memorable emergent play
- 3 examples where the game asked too much effort for too little payoff
- A verdict: "fun already," "promising but obscured," or "structurally unfun"

---

## Phase 2: Design and Balance Audit

This phase asks whether the systems fit together into a coherent strategy game.

### Read First

- `docs/VISION.md`
- `docs/DESIGN_REFINEMENT.md`
- `docs/BUG_FIXES.md`
- relevant system specs for the currently active gameplay slice

### Evaluate

- Strategic clarity: can the player tell what a good turn looks like?
- Counterplay: can the player recover from setbacks with smart decisions?
- Personality system: meaningful flavor with gameplay consequences, or mostly friction?
- Diplomacy: live strategic layer, or just another menu tree?
- Economy: meaningful constraint, or bookkeeping tax?
- Coalition/threat systems: create tension at the right pace?
- Difficulty curve: challenge from interesting pressure, not hidden rules

### Red Flags

- one dominant opening or dominant diplomatic line
- one system invalidating another system's intended role
- mechanics that are technically deep but not player-legible
- UI surfaces that hide the exact information needed for planning
- flavor systems that trigger often but rarely change decisions

### Required Deliverable

Produce:

- design findings ordered by player impact
- "keep / tune / rethink / cut" classification for each major system
- a short list of balance issues that require playtesting rather than code inspection

---

## Phase 3: Architecture and Code Health Audit

This phase builds on the prior architecture work and checks where risks remain today.

### Priority Files

- `backend/models/world_state.py`
- `backend/main.py`
- `backend/ai/enemy_ai.py`
- `backend/game_logic/turn_manager.py`
- `godot-client/project-sovereign/scripts/main.gd`
- current hot-path modules under active development

### Evaluate

- pipeline centralization
- size and responsibility boundaries of major files
- state mutation discipline
- response construction consistency
- serialization completeness
- implicit coupling across backend modules
- Godot side contract handling and modal/popup lifecycle discipline

### Key Question

Can a future feature be added by extending existing seams, or does every feature still require editing the same giant files?

### Required Deliverable

Produce:

- findings with file references
- "safe to extend / fragile but manageable / likely to regress" rating for each core subsystem
- a list of the 3-5 highest-leverage architectural improvements still worth doing

---

## Phase 4: Backend/Frontend Contract Audit

This project lives or dies on response wiring.

### Evaluate

- Does backend response shape remain centralized?
- Do all important gameplay states reach Godot consistently?
- Are popup, dialogue, notification, ledger, and dispatch payloads versioned by convention or by luck?
- Are there duplicated assumptions between Python and GDScript?
- Are there UI flows that work only because both sides currently happen to agree?

### Required Deliverable

Produce:

- current contract hotspots
- any areas where a new field or new popup type is still too easy to miss
- recommendations for contract hardening before more UI and map work lands

---

## Phase 5: Test and Regression Audit

The game already has a large suite. This phase checks whether the suite protects the right things.

### Evaluate

- coverage around response wiring
- coverage around turn advancement
- coverage around save/load and transient state clearing
- coverage around current diplomacy stack
- coverage around map growth assumptions
- characterization tests for historically fragile paths
- gaps between backend test confidence and actual Godot risk

### Required Deliverable

Produce:

- categories well protected by tests
- categories still underprotected
- a short list of missing high-value regression tests
- a verdict on whether the suite is broad, deep, both, or misleadingly large

---

## Phase 6: Full-Map Scalability Audit

This phase is specifically about the jump from the current 19-region implementation to a full Europe map.

### Read First

- `docs/ROADMAP.md`
- `docs/ADDING_CONTENT.md` section "Expanding the Map"
- `docs/ARCHITECTURE_AUDIT_REPORT.md`
- any map-renderer and fog-related references relevant to scaling

### Evaluate

- hardcoded thresholds that assume 19 regions
- region-name assumptions spread through tests or UI
- AI assumptions that are acceptable only on a small map
- fog-of-war assumptions that become mandatory at 80+ regions
- UI surfaces that are fine for 19 regions but collapse under 80+
- performance risks in turn processing, visibility calculation, pathfinding, and rendering
- content authoring burden: how many files must change per new region, nation, or marshal?

### Scale Questions

- Can the ledger and dispatch still support planning with 30 marshals and 8 nations?
- Can the AI remain readable and performant with many more fronts?
- Can the player manage the game without stronger map, filtering, and summarization tools?
- Is the current map/content pipeline good enough for batch expansion?
- Which systems need dynamic formulas instead of fixed thresholds before expansion begins?

### Required Deliverable

Produce:

- "safe now / fix before full map / fix during full-map implementation / defer until playtesting" buckets
- a pre-expansion checklist
- a no-go list: issues that would make full-map implementation reckless if left unfixed

---

## Severity Rubric

### Critical

Will materially block fun, break core gameplay, corrupt state, or make full-map expansion reckless.

### Major

Does not immediately kill the project, but creates repeat regressions, large player frustration, or strong scaling risk.

### Moderate

Meaningful weakness, but survivable. Should be fixed after higher-order blockers.

### Low

Polish, clarity, or maintainability improvement with limited immediate risk.

### Note

Observation worth documenting, but not necessarily actionable yet.

---

## Final Synthesis Deliverable

The final GPT audit should end with five outputs:

1. Executive verdict
   - Is the game already compelling?
   - Is the design direction sound?
   - Is the codebase organized enough to keep shipping?
   - Is the project structurally ready for full-map growth?

2. Findings list
   - ordered by severity and impact

3. Priority roadmap
   - what to fix now
   - what to tune by playtesting
   - what to defer until full-map implementation starts

4. Confidence statement
   - what the audit verified directly
   - what remains inference

5. Ship-readiness verdict
   - current 19-region version
   - future 80-100 region expansion

---

## Success Criteria for This Audit

This audit is successful if it answers:

- whether the game is fun, not just correct
- whether the design is strategically rich, not just feature-complete
- whether the architecture still has dangerous growth bottlenecks
- whether the project can scale to the roadmap's full-map ambitions without accidental self-sabotage

If the audit only produces bug notes, it was too shallow.
If it only produces architecture notes, it missed the game.
If it only produces design opinions without code evidence, it was not rigorous enough.

The right audit covers all three: player experience, design quality, and structural survivability.
