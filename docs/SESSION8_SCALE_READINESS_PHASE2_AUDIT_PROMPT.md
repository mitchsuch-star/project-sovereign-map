# Session 8 Scale Readiness Phase 2 Audit Prompt

> Copy everything below the line into a fresh audit session after checking out the latest `master`.
>
> Prior scale findings doc: [docs/SCALE_READYNESS.md](docs/SCALE_READYNESS.md)

---

## PROMPT START

You are conducting a focused implementation audit of Scale Readiness Phase 2 in the strategy game project "Ink & Iron" inside the current local repository.

Do not write code. Do not start with rewrite ideas. Inspect the current code and tests, then report whether this specific scaling-hardening slice was implemented correctly, incompletely, or incorrectly.

This is not a whole-project audit. Stay focused on Scale Readiness Phase 2:

- Phase 2.1: `get_distance()` caching + BFS queue fix
- Phase 2.2: marshal spatial-index seam wired into AI hot paths
- Phase 2.3: live nation-perspective fog visibility for AI nations

## Mission

Answer these questions with evidence:

1. Was Phase 2 implemented in a way that matches the current spec in `docs/SCALE_READINESS_PLAN.md`?
2. Are there correctness bugs, stale-cache risks, or behavior regressions in the new distance / visibility / AI-index seams?
3. Did the implementation materially reduce the two targeted blockers from `docs/SCALE_READYNESS.md`:
   - uncached BFS distance calls
   - omniscient AI enemy-contact scans
4. What important work, if any, still remains inside Phase 2 before the project should call it complete?

## Read First

Read these files before producing findings:

- `docs/SCALE_READINESS_PLAN.md` (Phase 2 only)
- `docs/SCALE_READYNESS.md`
- `docs/STATUS.md`
- `backend/models/world_state.py`
- `backend/ai/enemy_ai.py`
- `tests/test_scale_readiness_phase2.py`
- `tests/test_session7_backend_hardening.py`
- `tests/test_r9_r20_session8.py`
- `tests/test_terrain_pathfinding.py`
- `tests/test_enemy_ai_bugs.py`

Read other files only as needed to support or challenge a finding.

## Audit Rules

1. Treat docs as hypotheses, not proof.
2. Prefer current code, tests, and direct command probes over status claims.
3. Every finding must include evidence: file references, tests, or command probes.
4. For every `High` or `Medium` finding, do at least one disconfirming check. If you could not, say so.
5. Separate these problem types explicitly:
   - correctness bug
   - stale-cache / invalidation bug
   - fairness / information-model bug
   - remaining hot-path inefficiency
   - missing test / guardrail
6. Do not spend audit budget on unrelated gameplay balance, UI, or diplomacy issues unless they directly expose a Phase 2 regression.

## Required Method

Follow this order:

1. Capture a baseline snapshot.
2. Verify the Phase 2 spec against the current implementation.
3. Audit the distance-cache seam.
4. Audit the marshal-index seam.
5. Audit the live-visibility seam.
6. Audit the focused tests and identify blind spots.
7. End with a completion verdict: `complete`, `complete with follow-up`, or `not ready`.

If time is limited, do not skip:

- distance-cache invalidation behavior
- AI enemy-contact visibility behavior
- whether indexed helpers are actually used from AI code

## Baseline Snapshot

Record:

- audit date
- branch
- commit hash audited
- whether the tree is clean or dirty
- whether you audited clean `HEAD`, local uncommitted work, or both
- what test commands you ran

## Mandatory Investigation Areas

### 1. Phase 2.1: Distance Cache + BFS

Check:

- `get_distance()` no longer uses `queue.pop(0)`
- repeated mirrored queries share one symmetric cache entry
- controller changes do not invalidate the cache
- explicit topology mutation plus `invalidate_distance_cache()` does change results
- `find_path()` also uses `deque`

Required output:

- verdict: `correct`, `mostly correct`, or `incorrect`
- any stale-cache or invalidation risks
- any missing enforcement tests

### 2. Phase 2.2: Marshal Spatial Index Into AI

Check:

- `WorldState` exposes public AI-safe indexed helpers instead of teaching AI code to read `_marshals_by_region` directly
- AI refreshes marshal indexes at the right evaluation boundaries
- the new indexed seam is actually used in enemy-AI hot paths
- the implementation did not silently change correctness-first public helpers like `get_marshals_in_region()`
- remaining direct `world.marshals.values()` scans in `enemy_ai.py` are categorized:
  - truly global scan
  - local region scan that should have used the index

Required output:

- verdict: `materially improved`, `partially improved`, or `not meaningfully improved`
- top remaining non-indexed scan risks
- whether any direct private-cache reads escaped into AI code

### 3. Phase 2.3: Live Nation-Perspective Fog

Check:

- player-facing `get_visible_enemies()` still uses `RegionIntel`
- AI nations use the new live visibility seam instead of omniscient `get_enemies_of_nation()` for enemy-contact queries
- live visibility is current-state only and does not serialize stale intel/history
- sight rules match the intended baseline:
  - own regions
  - friendly marshal presence
  - adjacency to friendly marshals
  - adjacency to active watchtowers in own-controlled regions
- AI still knows its own marshals, but does not see enemy marshals outside live sight

Required output:

- verdict: `correct seam`, `correct but narrow`, or `still unfair`
- concrete cases where AI still appears omniscient, if any
- any mismatch between the written sight rules and the actual helper behavior

### 4. Tests And Guardrails

Check:

- whether the focused tests actually prove the new guarantees
- whether there is a missing regression test for:
  - cache invalidation after topology edit
  - non-player live visibility
  - player path staying on `RegionIntel`
  - indexed helper contract / refresh boundary

Required output:

- verdict: `guarded enough`, `thin but workable`, or `too easy to regress`
- smallest additional tests worth adding if anything is still missing

## Output Format

Organize the audit in this order:

### 1. Baseline Snapshot

### 2. Executive Verdict

Answer directly:

- Does the current implementation satisfy Scale Readiness Phase 2?
- What are the top 3 risks still left in this slice?
- What parts are solid enough to carry forward into Phase 3?

### 3. Findings

List findings ordered by severity. For each finding include:

- severity
- category
- why it matters
- evidence
- disconfirming check
- recommended next action

### 4. Completion Call

One of:

- `complete`
- `complete with follow-up`
- `not ready`

If you choose `complete with follow-up` or `not ready`, name the smallest next code or test slice required.

## PROMPT END
