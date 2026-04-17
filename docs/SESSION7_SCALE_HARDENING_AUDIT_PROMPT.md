# Session 7 Scale Hardening Audit Prompt

> Copy everything below the line into a fresh GPT audit session.
>
> Prior findings doc: [docs/SCALE_READYNESS.md](docs/SCALE_READYNESS.md)

---

## PROMPT START

You are conducting a focused scale-readiness audit of the strategy game project "Ink & Iron" in the current local repository.

This audit is specifically about whether the current 19-region shell can safely grow into a full Europe map.

Assume the target expansion means materially more regions, more nations, more marshals, denser diplomacy traffic, more UI density, and a larger static content surface. If the code or docs prove a different target, state that explicitly.

Do not write code. Do not start with implementation ideas. Inspect the current project state and produce a rigorous audit backed by evidence.

This is not a general gameplay audit. Only discuss combat feel, onboarding, diplomacy pacing, or defeat rules when they reveal a full-Europe scaling blocker or a smaller-map assumption that will not survive expansion.

## Prior Findings To Verify

Start from `docs/SCALE_READYNESS.md`.

That file is the prior findings register for this audit. Treat it as a list of hypotheses to verify, narrow, overturn, or extend from current code.

You must explicitly report whether each top claim in that doc is:

- `confirmed`
- `changed`
- `not reproduced`
- `new missing risk`

Do not merely restate the same list.

## Your Mission

Answer these questions with evidence:

1. What parts of the current game are the biggest blockers to scaling to a full Europe map?
2. What smaller-map assumptions are still embedded in code, data, UI, prompts, and pacing?
3. Which issues are true pre-expansion blockers, and which can wait until after the first larger-map prototype exists?
4. Which risks in `docs/SCALE_READYNESS.md` are still correct, which have changed, and what important risks are missing?

## Read First

Read these files before producing findings:

- `docs/SCALE_READYNESS.md`
- `docs/STATUS.md`
- `docs/ROADMAP.md`
- `docs/GPT_AUDIT_PLAN_RESULTS.md`
- `docs/VISION.md`
- `docs/DESIGN_REFINEMENT.md`

Priority code surfaces:

- `backend/models/region.py`
- `backend/models/world_state.py`
- `backend/ai/enemy_ai.py`
- `backend/ai/prompt_builder.py`
- `backend/commands/parser.py`
- `backend/nation_config.py`
- `backend/models/diplomat.py`
- `backend/models/marshal.py`
- `godot-client/project-sovereign/scenes/map.gd`
- `godot-client/project-sovereign/scenes/map_renderer_base.gd`
- `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`
- `godot-client/project-sovereign/scripts/strategic_ledger.gd`
- `godot-client/project-sovereign/scripts/marshal_management.gd`
- `godot-client/project-sovereign/scripts/war_status_panel.gd`

Read other files only as needed to support or challenge a finding.

## Audit Rules

1. Treat docs as hypotheses, not truth.
2. Prefer current code, tests, command probes, and directly observed contracts over historical notes.
3. Every finding must include evidence: file references, tests, command probes, or directly observed behavior.
4. For every `Critical` or `Major` finding, do at least one disconfirming check. If you could not perform one, say so explicitly.
5. Separate these problem types explicitly:
   - data-model / content-coupling problem
   - AI quality / fairness problem
   - AI efficiency / hot-path problem
   - renderer / UI density problem
   - pacing / scenario-tuning problem
   - tooling / test / workflow problem
6. Separate:
   - problem already visible on the 19-region shell
   - problem that mainly appears at Europe scale
   - problem that is already visible now and certain to worsen later
7. Do not propose a speculative rewrite unless current structure is clearly not survivable.
8. Do not count "more code will be needed" as a useful finding. The point is to identify brittle assumptions, hidden scaling cost, or missing seams.
9. Do not spend audit budget on polish unless it clearly blocks scale-readiness.

## Required Method

Follow this order:

1. Capture a baseline snapshot.
2. Audit map and content-model hardcoding.
3. Audit pathfinding, world-query, and AI hot paths.
4. Audit AI information model and fairness assumptions at larger scale.
5. Audit frontend map rendering and high-density UI surfaces.
6. Audit nation roster, capital, pacing, and scenario assumptions.
7. Audit tests, validation, and tooling coverage for map expansion.
8. End with a blocker ranking and phased roadmap.

If time is limited, do not skip:

- map/content-model hardcoding
- pathfinding/world-query cost
- AI visibility and decision hot paths
- renderer/UI density assumptions

## Baseline Snapshot

Record:

- audit date
- branch
- commit hash audited
- whether the tree is clean or dirty
- whether you audited clean `HEAD`, local uncommitted work, or both
- current claimed test count from `docs/STATUS.md`
- current region count, nation count, and any explicit map-scale assumptions you found

## Mandatory Investigation Areas

### 1. Map And Content Model

Determine how much of the current map is data-driven versus code-coupled.

Check:

- static region tables
- adjacency wiring
- capital definitions and proxy capitals
- nation color / display metadata
- prompt geography and parser geography
- whether frontend and backend derive from one shared source or drift separately
- how many files must change to add one new region, one new nation, or one new capital

Required output:

- subsystem verdict: `mostly data-driven`, `mixed`, or `code-coupled`
- top 3-5 map/content coupling risks
- smallest shared-data improvements worth doing before Europe wiring

### 2. Pathfinding, Distance, And World-Query Cost

Determine whether region graph operations and repeated scans will survive a much larger map.

Check:

- `get_distance`, `find_path`, and related helpers
- repeated BFS/path calls inside AI loops
- repeated full-world scans by region, marshal, or nation
- whether static graph information is recomputed instead of cached
- likely cost drivers if regions, marshals, and fronts multiply

Required output:

- verdict: `acceptable now and later`, `acceptable now but scale-risk`, or `clear blocker`
- top 3-5 cost drivers
- whether the right next move is caching, precomputation, seam cleanup, or something else

### 3. AI Information Model And Fairness At Scale

Determine whether enemy AI still depends on hidden knowledge or global scans that break fairness and cost assumptions on a Europe map.

Check:

- fog-aware versus omniscient helper usage
- enemy discovery/contact assumptions
- whether AI decision quality depends on global truth the player does not have
- how many decisions would become expensive if each nation tracks more fronts and more enemies
- whether the AI architecture has natural seams for a scale-aware information model

Required output:

- verdict: `scale-safe`, `fragile but patchable`, or `not ready`
- top fairness risks
- top scale risks
- smallest next structural change that would materially improve Europe readiness

### 4. Frontend Renderer And High-Density UI

Determine whether the frontend still assumes "small map, show everything, refresh everything."

Check:

- full map refresh behavior
- dynamic node rebuild behavior
- fallback map metadata duplication
- ledger and panel rendering of large datasets
- marshal management assumptions
- whether the player could still parse the UI with far more regions, nations, and armies

Required output:

- verdict: `serviceable`, `needs redesign before Europe`, or `will fail quickly`
- top 3-5 renderer/UI density risks
- which items are true blockers before Europe wiring versus later polish

### 5. Scenario, Roster, And Pacing Assumptions

Determine which runtime assumptions are still tuned to the current shell.

Check:

- hardcoded nation roster assumptions
- diplomat and marshal roster setup
- campaign length assumptions
- authority/gold/action tuning assumptions
- capital-loss or victory assumptions tied to the current shell
- whether scaling the map implies a systems rebalance instead of mere content expansion

Required output:

- verdict: `mostly scalable`, `needs rebalance plan`, or `hardcoded to current shell`
- top 3-5 pacing/roster assumptions that will not survive Europe
- what must be decided before content expansion starts

### 6. Tests, Validation, And Expansion Workflow

Determine whether the project has enough validation seams to expand safely.

Check:

- tests protecting map and AI assumptions
- validation for unsupported rosters or bad map content
- whether there is a safe workflow for adding many regions/nations without silent drift
- whether frontend/backend metadata drift would be caught automatically

Required output:

- verdict: `guarded enough`, `thin but workable`, or `too easy to regress`
- highest-value validation gaps
- smallest guardrails worth adding before Europe work

## Output Format

Organize the audit in this order:

### 1. Baseline Snapshot

### 2. Executive Verdict

Answer directly:

- Is the project structurally ready to start full-Europe wiring now?
- What are the top 3 blockers?
- What smaller-map assumptions are most dangerous?
- Which parts are already good enough to carry forward?

### 3. Findings

List findings ordered by severity and expansion risk.

For each finding, include:

- title
- severity
- category
- evidence
- counter-evidence considered
- why it matters for Europe scale
- smallest credible fix direction
- blocker class: `must fix before Europe wiring`, `fix during first Europe prototype`, or `defer until after expansion starts`

### 4. Prior Findings Delta

Cross-check `docs/SCALE_READYNESS.md`.

For each top prior item, report:

- status: `confirmed`, `changed`, `not reproduced`, or `missing risk added`
- evidence
- whether it matters now, only at Europe scale, or both
- whether the prior doc overrated, underrated, or correctly sized the issue

### 5. Blocker Ranking

Rank the top blockers to full-Europe expansion from highest to lowest.

### 6. Phased Roadmap

Use these buckets:

- before Europe wiring
- during first Europe prototype
- after Europe map exists

### 7. Confidence Statement

Separate:

- directly verified
- strong inference
- not verified

## Severity Rubric

### Critical

Almost certain to break correctness, fairness, content wiring, or runtime cost at Europe scale.

### Major

Strong chance of painful expansion cost, regression-heavy work, or unusable high-density UX.

### Moderate

Noticeable weakness, but survivable if handled in the right phase.

### Low

Real but not urgent.

### Note

Useful observation, not yet clearly actionable.

## Final Constraint

If your audit only says "make things more data-driven" or "optimize pathfinding," it is too shallow.

The audit must identify which current assumptions are actually dangerous, where they live, how confident you are, and when each one must be addressed relative to full-Europe expansion.

## PROMPT END
