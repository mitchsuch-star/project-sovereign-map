# Audit Prompt: Imperial Settlement Slice A1 — Foundation Gate

> **For:** A reviewing agent with no prior context on this session.
> **Commit under review:** `<FILL IN COMMIT SHA>` ("Land Slice A1: Imperial Settlement foundation")
> **Repo:** `C:\Users\User\PycharmProjects\project-sovereign-map`
> **Branch:** `master`

---

## What you are auditing

The author landed Slice A1 of the Imperial Settlement / Ally Participation
work — the **foundation-only** gate. A1 must NOT contain any behavioral
settlement work (no `war_instance` creation tied to declarations, no
contribution accrual, no common-peace scoring, no settlement reactions).
Its sole job is to land the substrate that A2/A3/B/C/D will consume:

- Mapped-nation capital helper safety.
- `WorldState` settlement containers (`next_war_instance_id`,
  `war_instances`, `archived_war_instances`).
- Save/load defaults so old saves keep loading cleanly.
- Empty-safe `war_instances_by_leader` and `war_instances_by_participant`
  index/cache helpers with a single dirty-flag invalidation hook.
- Touched elimination helpers refactored to use cached nation-region
  lookups instead of raw `world.regions.values()` scans.
- Invariant assertion helper(s) covering "every WAR pair has exactly one
  active `war_instance`" once instances exist.
- A synthetic 20-active-`war_instance` fixture proving the index/cache
  helpers behave at target scale.

The spec lives in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.24.
The coding handoff is `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
v1.21. Read both before starting; A1's exact surface is in the spec
**Section 0** (Scale and Ownership Contract) and the implementation plan
**Slice A** "Build" / "Gate" sections, especially the bullets explicitly
labelled "A1" or "A1 foundation gate".

You are an independent reviewer. The author claims:

- A1 is foundation-only; no behavioral settlement code shipped.
- 10-14 focused tests landed in `tests/test_war_settlement_instances.py`
  (or the foundation-specific test file already in repo:
  `tests/test_war_settlement_foundation.py`). The suite passes.
- Old saves (no settlement fields at all) load cleanly with
  `next_war_instance_id == 1`, `war_instances == {}`,
  `archived_war_instances == []`.
- `get_settlement_home_capital(nation)` returns the mapped capital from
  `NATION_CAPITALS` only when the region exists in the current world;
  returns `None` for unconfigured/absent nations and never infers
  settlement participation.
- Britain currently maps to `Netherlands` per scenario data; the helper
  treats this as configured mapped data, not a separate settlement
  identity.
- The empty-safe `war_instances_by_leader` /
  `war_instances_by_participant` helpers exist, return empty results
  before any instance is created, and rebuild at most once per turn
  phase via dirty-flag invalidation.
- A 20-active-`war_instance` synthetic fixture proves the helpers behave
  at scale.
- Every elimination helper that A1 touched now uses the cached
  `get_nation_regions()` / `get_active_nations()` helpers — no new raw
  `world.regions.values()` scans.
- The invariant assertion helper exists and passes against an empty
  world and against the 20-instance synthetic fixture.

Verify these claims, then go beyond them.

---

## Files to read (in order)

1. **Spec — Section 0 first, then 7.1 / 7.5 / 7.6 / 17.5 for what NOT to
   ship in A1:** `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`. Pay
   special attention to the v1.24 status block at the top — it
   enumerates exactly which responsibilities are A1 vs deferred to
   A2/A3/B/C/D.
2. **Implementation plan — Slice A "Build" + "Gate":**
   `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`. The
   Scale Rules block at the top is also load-bearing for A1 — every
   "no per-turn scan of all regions" / "no broad
   `world.regions.values()` loops" / "active-nation roster" rule
   applies.
3. **WorldState changes:** `backend/models/world_state.py` — focus on:
   - `__init__` (around line 109) — new fields and their defaults.
   - `to_dict` (around line 3372) and `from_dict` (around line 3658) —
     serialization round-trip.
   - `get_settlement_home_capital(...)` (already at ~line 1497 before
     A1) — confirm its behavior matches the spec's helper contract or
     was extended cleanly.
   - The new index/cache helpers (`get_war_instances_by_leader`,
     `get_war_instances_by_participant`, or equivalent names) and their
     dirty-flag hook.
   - Any elimination helper touched by A1 — confirm the refactor used
     `get_nation_regions(...)` / `get_active_nations(...)` rather than
     raw region iteration.
4. **Optional separate module:** if A1 created
   `backend/game_logic/settlement_helpers.py`, read it end to end. The
   plan permits a shared module only when surrounding implementation
   needs it.
5. **Tests:** `tests/test_war_settlement_foundation.py` (existing) plus
   any new tests under `tests/test_war_settlement_instances.py`. The
   foundation file currently has 4 tests pre-A1; A1 should bring the
   foundation gate to 10-14 focused tests total.
6. **Save/load reference:** `docs/SAVE_FORMAT_REFERENCE.md` — confirm
   the new fields are documented with their defaults.
7. **Doc claims:** `docs/STATUS.md` and `CLAUDE.md` "Up Next" — A1
   should be marked complete, the A2 follow-up clearly named.

---

## What to check

Audit the change against this checklist. For each finding, report:
**severity** (BLOCKER / MAJOR / MINOR / NIT), **location** (file:line),
**what is wrong**, **why it matters**, and **suggested fix**.

### A. Foundation scope discipline (critical for A1)

A1. **No behavioral settlement code shipped.** A1 is a foundation slice.
    Verify the diff does NOT contain:
    - Any call site that allocates a `war_instance` from a real
      declaration / cascade / vassal-rebellion / armistice-collapse
      path. (Those belong to A2.)
    - Any contribution accrual logic, theater attribution, or
      `war_contribution_scores` writes. (Those belong to Slice B.)
    - Any common-peace scoring helper, `compute_side_pressure_score`,
      `project_balance_after_settlement`, or settlement-confirm
      executor wiring. (Those belong to Slice C.)
    - Any settlement memory writes, `settlement_gratitude_mod`,
      `sold_out_by_war_leader` posture, or cross-war reaction. (Those
      belong to Slice D.)
    - Any presentation payload extension for settlement summary,
      digest, or notification rail. (That belongs to Slice E.)
    If you find ANY of the above shipped under A1, that is a BLOCKER —
    A1 has overshot its gate and risks blocking the slice ordering
    promised by the implementation plan.

A2. **Helper contract: `get_settlement_home_capital(nation)`.** The
    spec (Section 0, "Capital helper safety") demands:
    - Returns the configured mapped capital from `NATION_CAPITALS`
      when the region exists in the current world.
    - Returns `None` for absent / unconfigured nations.
    - `None` MUST NOT be inferred as "settlement-capable". Capital-
      dependent scoring components must skip or score `0` when the
      helper returns `None`.
    Verify the implementation matches. The pre-A1 baseline at
    `backend/models/world_state.py:1497` already does the right thing;
    confirm A1 didn't regress it or duplicate it elsewhere with weaker
    semantics.

A3. **Britain-on-current-map identity.** The current scenario maps
    Britain's capital to `Netherlands`. This is configured mapped
    scenario data — NOT a separate "Britain-without-mapped-home"
    settlement identity. Verify a Britain fixture test pins
    `get_settlement_home_capital("Britain") == "Netherlands"` and
    proves Britain follows normal mapped-nation rules (no special-case
    branch in elimination/standing/scoring code).

A4. **Future-nation exclusion.** Confirm a fixture proves nations
    absent from `NATION_CAPITALS` / scenario data (Russia, Spain,
    Ottoman, etc., which exist in `NATION_POWER_TIERS` but not in the
    current 5-nation runtime) are NOT silently treated as settlement
    participants. They must be excluded from `get_active_nations()`
    and the helper must return `None` for their capital.

A5. **Missing-capital safety fixture.** A synthetic fixture should
    monkeypatch a mapped nation into `NATION_CAPITALS` with an
    imaginary region not present in `world.regions`, and prove
    `get_settlement_home_capital(...)` returns `None` rather than
    crashing. The existing test
    `test_settlement_home_capital_requires_region_in_current_world`
    covers this — confirm A1 did not weaken it.

### B. Containers and serialization

B1. **`__init__` defaults.** Confirm the three new fields exist with
    exactly the spec defaults:
    - `self.next_war_instance_id: int = 1`
    - `self.war_instances: Dict[str, Dict] = {}`
    - `self.archived_war_instances: List[Dict] = []`
    Type hints should match. Walk the new field block and confirm
    nothing else was sneaked in (e.g., a half-finished
    `war_contribution_scores` field belongs to Slice B, not A1).

B2. **`to_dict` writes all three fields.** Search for each field name
    in `WorldState.to_dict()` and confirm it appears in the output.
    A common bug: defining the field but forgetting to serialize it,
    so save/load silently resets to defaults.

B3. **`from_dict` uses `.get(key, default)` with the right default
    for each field.** Spec is explicit: `1` / `{}` / `[]`. Old saves
    must load with these values. Walk through each field; flag
    anything using a different default.

B4. **Old-save round-trip test.** A1 must include a test that loads a
    serialized world WITHOUT any of the three fields and asserts they
    initialize to `1` / `{}` / `[]`. Confirm such a test exists; if
    only a write+read round-trip exists, that's not enough — explicit
    "no field present in input dict" coverage is required.

B5. **`SAVE_FORMAT_REFERENCE.md` updated.** The three new fields
    should be documented with type, default, and one-line purpose.
    Flag if missing.

B6. **Serialization enforcement test.** Run
    `pytest tests/test_serialization_enforcement.py -v` and confirm it
    passes. CLAUDE.md's "Serialization Enforcement (MANDATORY)" section
    requires this for any new field.

### C. Index / cache helpers

C1. **Empty-safe by construction.** Both
    `war_instances_by_leader` and `war_instances_by_participant`
    helpers must return empty (dict or list, depending on signature)
    before any instance exists, without raising or producing
    misleading defaults. Walk through with `world.war_instances == {}`
    and confirm no KeyError, no None deref.

C2. **Single dirty-flag hook.** The plan demands a single dirty-flag
    invalidation hook so a multi-pair common peace marks the indexes
    dirty ONCE and rebuilds at most ONCE per turn phase. Find the
    invalidation function. Confirm:
    - It is callable (not just a private flag mutation).
    - There is exactly ONE such function (not separate
      `_mark_leader_dirty` and `_mark_participant_dirty` that drift).
    - The invalidation is idempotent — calling it 5 times in a row
      should not cause 5 rebuilds.
    - There is a test proving the rebuild fires at most once per
      phase.

C3. **No A2-flavored use.** A1 must NOT call the helpers from real
    declaration / cascade / armistice paths yet. Search for callers
    in production code (not tests) and flag any that are not pure
    test fixtures or invariant assertions.

C4. **20-active-`war_instance` fixture.** The plan explicitly demands
    a synthetic fixture creating 20 active `war_instance` records
    DIRECTLY in test world state (not through declaration paths) so
    helper behavior is proven at scale-readiness target. The fixture
    must:
    - Use the canonical 13 DG-1 nation roster (`France`, `Britain`,
      `Austria`, `Prussia`, `Russia`, `Spain`, `Ottoman`, `Sweden`,
      `Naples`, `Bavaria`, `Saxony`, `Portugal`, `Denmark-Norway`).
    - Cover at least one 6+ participant side.
    - Live in `tests/helpers/full_europe_settlement_fixtures.py` per
      the plan's "Full-Europe Test Fixture Contract".
    - Either monkeypatch active-nation lookup OR explicitly extend
      `world.enemy_nations` / runtime nation setup before adding
      synthetic regions/controllers; bare insertion into
      `world.regions` is not enough.
    Confirm. If the fixture lives inline in the test file rather than
    the shared helper, that's a MINOR deviation worth flagging.

C5. **Index rebuild correctness on the 20-instance fixture.** With
    20 `war_instance` records in place, the leader index should map
    each leader nation to the wars it leads, and the participant
    index should map each participant nation to the wars it belongs
    to (on either side). Confirm coverage:
    - Both indexes cover all 20 instances.
    - A nation with no participation appears in neither index (no
      empty-list value).
    - A nation that leads on one side but participates on another in
      a different war shows up in both indexes correctly.

C6. **Cache miss + invalidation idempotence test.** The plan's gate
    explicitly requires "cache invalidation idempotence" coverage.
    Confirm a test:
    - Builds the index.
    - Calls invalidate.
    - Calls invalidate again.
    - Reads the index — it should rebuild ONCE, not twice.

### D. Touched elimination helpers

D1. **Refactored to cached helpers, not raw scans.** The plan says
    "refactor any touched elimination helper to use cached
    nation-region lookups instead of raw `world.regions.values()`
    scans." Diff every elimination helper modified by A1; confirm
    raw `world.regions.values()` was replaced by `get_nation_regions(...)`,
    `get_active_nations(...)`, or another cached path. Flag any
    new raw scan as a BLOCKER for scale-readiness.

D2. **Same elimination semantics.** A1 keeps the existing
    mapped-nation elimination rule. There must be NO new exemption
    branch for absent future nations and NO Britain-specific override.
    The behavior change is internal (cached vs raw); externally the
    rules are the same. Confirm with at least one fixture
    cross-checking pre- and post-refactor behavior.

D3. **No separate-peace / settlement reaction wiring leaked in.** A1
    must not start firing settlement reactions on elimination. Verify
    the elimination code does not call any settlement-memory or
    cross-war-reaction helper.

### E. Invariant assertion helper

E1. **Invariant exists and is callable.** Find the helper (likely
    named `assert_war_instance_invariants(...)` or similar). Confirm
    it accepts a `world` argument and runs without crashing on an
    empty world (no `war_instances`).

E2. **Invariant content for A1 (lighter than A3).** A1's invariant
    target is the foundational assertion: every active
    `diplomatic_states[diplo_key] == "WAR"` must appear in exactly
    one active `war_instance.active_diplo_keys` with
    `pair_status == "war"`, and no active `war_instance` may claim
    a non-WAR pair as `pair_status == "war"`. With zero
    `war_instances` shipped in A1, this is trivially satisfied —
    but the helper must already exist so A2 can layer on it. A3
    promotes it to "always-on post-merge". Verify the helper API
    is stable and doesn't bake in A1-only assumptions.

E3. **Invariant test against the 20-instance fixture.** Confirm a
    test runs the invariant against the synthetic 20-instance
    fixture. If the fixture is intentionally invariant-clean (it
    should be), the assertion passes. A "bad fixture" companion test
    (deliberately corrupted to add a duplicate pair owner) proving
    the invariant catches the violation is a strong signal — flag if
    missing.

### F. Plan-level prohibitions

The implementation plan has a dense list of "Don't do this in A1" rules
hidden across the Build/Gate bullets and the Scale Rules. For each,
verify A1 honored it.

F1. **No `_process_war_cascade` signature changes.** A2 (not A1) is
    where `CascadeContext` may be introduced. Diff the function
    signature; confirm it is unchanged from pre-A1 master.

F2. **No `attach_pair_to_war_instance` / `attach_participant_to_war_instance`
    direct-entry helpers shipped.** Those are A2. Grep for them; if
    present in production code, that's a BLOCKER.

F3. **No `ensure_war_instance_for_pair`.** Same as F2 — it's the A2
    declaration-path helper. Grep and confirm absence.

F4. **No live elimination-rule changes.** The plan says: "Do not add
    a separate elimination exemption in A1/A3. Nations absent from
    scenario/map data are not active settlement participants. Britain
    follows the normal mapped-nation rules in the current runtime."
    Confirm.

F5. **No region-iterating loops in any new code.** Grep all new code
    for `world.regions.values()` and `for region in world.regions`.
    Cached helpers only — `get_nation_regions(...)`,
    `get_active_nations(...)`, etc.

F6. **No new per-turn cache key collisions.** If A1 added a new
    per-turn cache (likely for the index helpers), it must use a
    distinct cache key from existing per-turn caches
    (`_active_nations_cache`, `_nation_regions_cache`,
    `_distance_cache`, etc.) and have its own invalidation path.
    Walk each cache field; confirm naming/lifecycle separation.

### G. Test quality

G1. **Test count.** Plan demands 10-14 focused A1 tests. Count how
    many tests in `tests/test_war_settlement_foundation.py` and any
    new file landed under A1. Pre-A1 baseline is 4 (the existing
    foundation tests). A1 should add 6-10 more for a 10-14 total.
    Flag if the count is below 10 or above 14.

G2. **Plan gate coverage.** The plan's A1 Gate bullets enumerate
    specific fixtures. For each, confirm a test exists and exercises
    the named behavior:
    - Old saves load with `1` / `{}` / `[]` defaults.
    - Britain fixture proves `get_settlement_home_capital("Britain")`
      returns `Netherlands` and does not create a separate identity.
    - Missing-capital fixture proves a synthetic mapped nation with
      no `NATION_CAPITALS` entry does not crash capital-dependent
      scoring and is not active.
    - Empty war-instance index fixtures prove
      `war_instances_by_leader` and `war_instances_by_participant`
      build and invalidate safely before any active `war_instance`
      exists.
    - Elimination fixture proves the mapped-nation rule is explicit
      and absent future nations are ignored rather than evaluated.
    - 20-active-`war_instance` synthetic fixture covers index/cache
      helpers at scale.
    - Cache invalidation idempotence test exists.

G3. **No accidental dependence on the 5-nation runtime.** Plan
    explicitly says: "Tests that need active nations must either
    extend the fixture world's active roster (`world.enemy_nations` /
    runtime nation setup) before attaching synthetic regions/
    controllers, or monkeypatch the specific active-nation helper
    under test; they must not rely on the current 5-nation runtime
    roster." Walk every new test; flag any that silently expects
    Russia/Spain/Ottoman to be present without explicit setup.

G4. **Cache invalidation after fixture roster change.** Plan: "After
    changing the fixture roster or controllers, invalidate
    active-nation and nation-region caches before settlement
    assertions." Walk new tests; flag any that mutate
    `world.enemy_nations` / regions and then read cached helpers
    without calling the invalidation hooks.

G5. **No production code branched on test-only nations.** Plan: "Do
    not add production settlement branches for specific future
    nations." Search backend code for hard-coded references to the
    canonical-13 nation names that don't exist in the current
    scenario; flag any.

### H. Docs / claims accuracy

H1. **`docs/STATUS.md` updated.** Look for an A1 completion entry
    with the right date and the explicit "foundation only" framing.
    Confirm A2 is named as the next gate.

H2. **`CLAUDE.md` "Up Next" updated.** The pre-A1 line said "READY
    FOR SLICE A1 FOUNDATION GATE". After A1 it should say something
    like "Slice A1 COMPLETE; Slice A2 war-entry threading is the next
    gate". Confirm.

H3. **`SAVE_FORMAT_REFERENCE.md`** documents the three new fields with
    their defaults. (Already covered in B5.)

H4. **Test count + suite green.** Run:
    ```
    cd C:\Users\User\PycharmProjects\project-sovereign-map
    .venv\Scripts\python.exe -m pytest tests/ -q
    ```
    Confirm the suite is green. Note the new total vs the pre-A1
    baseline; the delta should match the test count claim.

H5. **Targeted A1 run:**
    ```
    .venv\Scripts\python.exe -m pytest tests/test_war_settlement_foundation.py tests/test_war_settlement_instances.py tests/test_serialization_enforcement.py -v
    ```
    Confirm green.

H6. **Ruff clean on touched Python files:**
    ```
    .venv\Scripts\python.exe -m ruff check backend/models/world_state.py tests/test_war_settlement_foundation.py
    ```
    Plus any new modules. Confirm.

H7. **Plan/spec drift.** If the author edited the plan or spec
    during A1, the changes should be confined to status/version
    headers (e.g., "v1.21 → v1.22"). Spec content in Sections 6+
    or plan content in Slices B/C/D/E should NOT change as part of
    A1. Diff and flag.

### I. Things that worry you

Do a "smell pass" — read the code with no checklist and write down
anything that feels off, even if you cannot point to a specific bug.
Specific concerns to watch for:

- Has A1 introduced any helper that "almost" does an A2 job
  (e.g., a `prepare_war_instance(...)` that's never called but
  takes declaration-path arguments)? Even unused, that's scope creep.
- Are the index-rebuild helpers private (`_build_*`) or public
  (`get_*`)? Settlement code in A2/A3/B/C/D will need stable callers,
  so a public read API is preferable; flag if the surface is
  awkward.
- Is `created_sequence` reserved on the `war_instance` shape, or is
  the field defined only when A2 starts allocating? The spec stores
  `created_sequence: int` in the shape (Section 7.1, line ~272). If
  A1 documents the shape but never instantiates it, that's fine; if
  A1 ships a serializer that assumes the field exists when reading
  archived instances, that's a smell.
- Are the new `war_instances_by_*` caches stored on `WorldState` or
  computed on demand? If stored, are they cleared on `from_dict`
  load? An unprimed cache survives load and could feed stale data.
- Does the elimination helper refactor introduce any subtle behavior
  change at the boundary (e.g., a nation with zero regions but a
  vassal — pre-refactor result vs post-refactor)? Test if uncertain.
- Are there any TODO / FIXME comments left in A1 that should be
  resolved or moved to a tracked issue?

---

## How to report

Format your report as one or more sections with the structure:

```
## Findings

### [SEVERITY] Short title
**Location:** file:line (or "N/A" for cross-cutting)
**What:** one paragraph describing the issue
**Why it matters:** one paragraph on impact
**Suggested fix:** one paragraph on what to change

(repeat for each finding)

## Verification log

Commands you ran and their results — at minimum the full pytest suite,
the targeted A1 run, the ruff check, and a grep audit for forbidden
A2/B/C/D code patterns (`ensure_war_instance_for_pair`,
`attach_pair_to_war_instance`, `compute_side_pressure_score`,
`settlement_gratitude`, etc.).

## Overall assessment

One paragraph: ship as-is / ship with minor fixes / needs rework before
A2 can start. Be direct. The bar is high — A1 is a foundation gate, and
A2 cannot start until A1 is genuinely green per the plan's wording.
```

Group findings by severity. If you find nothing wrong, say so plainly —
do not pad. Maximum report length: 1500 words unless the findings
genuinely require more.

**Do not edit any code.** This is a review pass only.

---

## Quick severity guide

- **BLOCKER** — A1 has shipped behavioral settlement code (A2/A3/B/C/D
  scope), broken save-load round-trip, introduced a raw region scan in
  a hot path, or weakened the capital-helper safety contract. Must fix
  before A2 starts.
- **MAJOR** — Plan-mandated test/fixture/invariant is missing,
  serialization gap, or a subtle cache lifecycle bug that won't surface
  until later slices. Should fix before A2 but can be sequenced.
- **MINOR** — Style / naming / minor test gap that won't block A2 but
  the author should know.
- **NIT** — Cosmetic only.
