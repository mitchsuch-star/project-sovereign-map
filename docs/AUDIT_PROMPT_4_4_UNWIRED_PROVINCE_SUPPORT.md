# Audit Prompt: Map Readiness §4.4 — Unwired Province Support

> **For:** A reviewing agent with no prior context on this session.
> **Commit under review:** `3cbe327` ("Land Map Readiness §4.4: unwired province support")
> **Repo:** `C:\Users\User\PycharmProjects\project-sovereign-map`
> **Branch:** `master` (already pushed)

---

## What you are auditing

The author landed §4.4 of the Map Readiness Closure Pass: unwired
province support in the renderer. The change touches:

- `godot-client/project-sovereign/scenes/map_renderer_base.gd` — new
  constants, helpers, overlay function, click/tooltip gating.
- `tests/test_map_renderer_cutover.py` — +10 source-level tests.
- `tests/test_map_unwired_overlay.py` — NEW file, +6 behavioral fixture
  tests that mirror the overlay math in Python.
- `docs/STATUS.md`, `CLAUDE.md`, `docs/SCALE_READINESS_PLAN.md` — §4.4
  marked complete; SRP tracker row updated.

The spec lives at `docs/SCALE_READINESS_PLAN.md` Section 4.4
(post-edit). Related context lives in Sections 4.1 and 4.2 immediately
above it — §4.1 introduced the `wired` / `interactive` flags on the
province registry and gated `update_all_regions()` on `wired`; §4.2
added the bitmap loader path. §4.4's job is to make unwired provinces
visually, tactically, and informationally distinct from wired ones
without breaking the §4.1 / §4.2 seams.

You are an independent reviewer. The author claims:

- 16 new tests pass; full Python suite is green at **8503 passed, 2 skipped** (was 8487).
- Ruff clean on the two modified / new Python test files.
- The placeholder `session8_placeholder_provinces.json` still has ALL 19
  provinces wired — the §4.4 code paths exercise only when a future
  scenario declares an unwired region.
- The overlay applies uniformly on BOTH texture-build paths (circle
  fallback and bitmap), ordered AFTER `province_lookup_image` is set but
  BEFORE the visual texture is created.
- The `_lookup_region_from_color_map()` hit-test path was deliberately
  NOT modified — unwired provinces stay hoverable.
- The click gate and tooltip dispatch path both route through a single
  helper `_is_region_wired()`.

Verify these claims, then go beyond them.

---

## Files to read (in order)

1. **Spec:** `docs/SCALE_READINESS_PLAN.md` Section 4.4 (around lines
   1016-1043 after the edit). Then re-read Sections 4.1 and 4.2
   immediately above so you understand the seams §4.4 integrates with.
2. **Renderer change:** `godot-client/project-sovereign/scenes/map_renderer_base.gd`
   — focus on these regions:
   - The constants block near the top (look for `UNWIRED_GREY_*`).
   - `_is_region_wired()`, `_unwired_lookup_keys()`, and
     `_apply_unwired_grey_overlay()` — new helpers.
   - `_build_map_textures()` circle fallback — where the overlay call
     was inserted.
   - `_load_map_images()` bitmap path — where the overlay call was
     inserted in the success path.
   - The `MOUSE_BUTTON_LEFT` branch in the input handler (search
     `MOUSE_BUTTON_LEFT`).
   - `_draw()` — the dispatch branches.
   - `_draw_unwired_region_tooltip()` — new helper.
   - `_lookup_region_from_color_map()` — UNCHANGED from §4.1, but
     re-read it to confirm that claim.
   - `_refresh_hover_state()` — ALSO UNCHANGED, but note the distance
     fallback still gates on `interactive`.
3. **Source-level tests:** `tests/test_map_renderer_cutover.py` — read
   the ten new tests at the bottom of the file.
4. **Behavioral tests:** `tests/test_map_unwired_overlay.py` — read the
   full file (new, ~180 lines).
5. **Adjacent placeholder contract:** `tests/test_map_placeholder_assets.py`
   — pins that the 19 current provinces are all `wired: true` so the
   §4.4 code paths don't fire on the current placeholder.
6. **Doc claims:** `docs/STATUS.md` (Last Updated header, Quick Stats
   row, the new "§4.4 Unwired Province Support COMPLETE" item, Real Map
   Readiness Gate bullets), `CLAUDE.md` "Up Next" bullet (§§4.1-4.4
   line), `docs/SCALE_READINESS_PLAN.md` §4.4 + tracker row.

---

## What to check

Audit the change against this checklist. For each finding, report:
**severity** (BLOCKER / MAJOR / MINOR / NIT), **location** (file:line),
**what is wrong**, **why it matters**, and **suggested fix**.

### A. Spec conformance

A1. The spec says "Render unwired provinces in grey tint." The author
    chose a flat blend toward `Color(0.32, 0.32, 0.34, 1.0)` at 70%
    strength. Is the approach sound? Does it plausibly read as "not yet
    in play" rather than "fogged" or "unclaimed"? Keep in mind:
    - `FOG_OVERLAYS` in the same file darkens with near-black overlays
      of 30–75% alpha. Is the unwired tint distinguishable?
    - The tooltip panel color for unwired (`Color(0.08, 0.08, 0.1, 0.92)`)
      is intentionally different from the fogged tooltip color
      (`Color(0.08, 0.08, 0.12, 0.95)`) by one channel. Is that
      actually distinguishable at runtime?

A2. The spec says 'Hover shows "Province Name (not yet in play)".' The
    author implemented this as TWO lines in the tooltip: first the
    province name (large font), then `UNWIRED_TOOLTIP_SUFFIX` on its
    own line. Is that the intent? Or does the spec imply a single line
    like "Paris (not yet in play)"?

A3. The spec says "Click does nothing." The author gates inside the
    `MOUSE_BUTTON_LEFT` branch, returning before `region_clicked.emit()`.
    Is that the right gate-point? Could a different input path still
    surface a click (e.g., via `MOUSE_BUTTON_RIGHT`, keyboard, or some
    other emission of `region_clicked`)? Grep the codebase for other
    `region_clicked.emit` sites.

A4. The spec says 'Province registry: `wired: false` provinces have
    lookup colors for hover identification but no gameplay data'. Does
    `_lookup_region_from_color_map()` — which is the hit-test function
    — actually permit unwired provinces to be resolved? Confirm the
    absence of a `wired` gate there. Then confirm via the negative
    test (`test_lookup_region_from_color_map_still_returns_unwired_regions`)
    that this is pinned.

A5. The spec has one bullet: '`map.gd`: `update_all_regions()` skips
    unwired provinces for gameplay data'. The author left `map.gd`
    unchanged, citing that §4.1 already did this. Verify by reading
    `map_renderer_base.gd::update_all_regions()` that the filter is
    actually in place.

### B. Implementation correctness

B1. **Overlay math.** `_apply_unwired_grey_overlay()` uses
    `base.lerp(UNWIRED_GREY_COLOR, UNWIRED_GREY_BLEND)`. Confirm:
    - `Color.lerp(other, t)` in Godot interpolates component-wise. Is
      the alpha channel preserved correctly? The code explicitly does
      `tinted.a = base.a` after the lerp. Walk through a case where
      `base.a` is 0.5 and `UNWIRED_GREY_COLOR.a` is 1.0 — does the
      final alpha come out as 0.5?
    - The Python mirror in `tests/test_map_unwired_overlay.py` uses
      integer lerp (`_lerp`) on 8-bit channels. Does that match the
      Godot implementation closely enough to catch drift if someone
      changes the blend factor?

B2. **Overlay ordering.** In BOTH paths, the overlay must run AFTER
    `province_lookup_image` is set but BEFORE the visual texture is
    created. Confirm this by reading the two functions. If the order
    is wrong, the overlay might use a stale lookup image or the
    texture might capture the pre-overlay visual.

B3. **Overlay early-return paths.** `_apply_unwired_grey_overlay()`
    has three early returns: null image, empty unwired set, size
    mismatch. Each is defensible; confirm:
    - Null image: the caller passes real images from both paths, so
      this should never fire in practice. Is it worth keeping?
    - Empty unwired set: this is the hot path for the current 19-region
      placeholder. No pixel iteration = zero cost. Good.
    - Size mismatch: silent return. The §4.2 loader already guards
      size match with a `push_error`, so this should never fire from
      the bitmap path. The circle fallback builds both images at the
      same size so it can't fire there either. Is silent the right
      behavior, or should it `push_error` just in case?

B4. **`_unwired_lookup_keys()` correctness.** It iterates
    `province_color_lookup.keys()`. Confirm:
    - The sentinel color (`NO_PROVINCE_COLOR`) is NOT inserted into
      `province_color_lookup` by `_build_province_shapes()`. If it WERE
      inserted, the overlay would tint the sentinel pixels too, which
      would be visually wrong. The author claims this is prevented by
      construction. Verify by reading `_build_province_shapes()`.
    - If `province_color_lookup` is empty (registry failed to load),
      what happens? The helper returns an empty dict, the overlay
      early-returns, circles-fallback path still draws shapes. Does
      anything break?

B5. **`_is_region_wired()` default.** For regions NOT in
    `province_shapes`, the helper returns `true`. Is that safe?
    Consider: a marshal object references a region name that isn't in
    the registry (shouldn't happen, but the code must not crash). The
    tooltip path would then fall through to the wired branch
    (`region_full_data.has(region_name)`) which also handles missing
    regions. Walk through and confirm no branch crashes on this case.

B6. **Click gate.** The gate is only on `MOUSE_BUTTON_LEFT`. Is that
    sufficient? The current renderer does not wire any other mouse
    button to `region_clicked`, so this seems right. But if a downstream
    consumer connects `region_hovered` to logic that acts on unwired
    regions as if they were wired, the hover signal STILL fires for
    unwired provinces. Does any existing consumer do this? (Search
    `region_hovered` / `region_clicked` usages.)

B7. **Tooltip branch order.** `_draw()` evaluates:
    1. marshal hover → marshal tooltip
    2. fogged force hover → fogged tooltip
    3. unwired region hover → unwired tooltip  ← NEW
    4. wired region hover + has full data → region tooltip
    5. fallback → clear

    Is this order correct? Specifically: could a marshal be hovered on
    an unwired region? If so, the marshal tooltip should win (as it
    does). But if an unwired region has no marshals (which it shouldn't,
    since `update_all_regions()` excludes unwired from `region_marshals`),
    this is moot. Confirm the exclusion.

### C. Test quality

C1. **Source-level tests.** The ten tests in
    `test_map_renderer_cutover.py` are string-grep tests on the GDScript
    source. They pin symbol presence and ORDER within a function body.
    Walk through at least three:
    - `test_build_map_textures_applies_unwired_overlay_in_circle_fallback`
      — correctly asserts overlay-before-texture ordering in the
      circle-fallback path?
    - `test_click_handler_gates_emit_on_wired_flag` — the test parses
      the click block by `split`ing on the next press-release anchor.
      If someone adds a new `elif` branch between LEFT and the release
      handler, does this test still produce a meaningful split? Is the
      test robust enough?
    - `test_draw_routes_unwired_regions_to_placeholder_tooltip` —
      verifies that the unwired branch appears BEFORE the
      `region_full_data.has` branch. Does it also verify the
      `_draw_unwired_region_tooltip()` call is inside the unwired
      branch, or could the branch fall through to the wired tooltip?

C2. **Behavioral overlay tests.** The six tests in
    `test_map_unwired_overlay.py` mirror the overlay math in Python.
    Spot-check:
    - `test_all_wired_overlay_is_a_no_op` — passes an empty unwired
      set. Good.
    - `test_overlay_blends_only_unwired_pixels_toward_grey` — uses
      Belgium as a stand-in for an unwired province. Is that a
      defensible shortcut, or does it falsely imply Belgium should be
      unwired?
    - `test_overlay_drives_pure_tint_toward_grey_color` — uses pure
      black as the base. Does the expected output confirm the correct
      lerp formula?
    - `test_overlay_ignores_sentinel_pixels_even_if_visually_flagged`
      — this is a "guarantee by construction" test. Does the actual
      assertion (`unwired_keys = set()`) exercise the safety, or is it
      just redocumenting the invariant?

C3. **Test gap analysis.** Things you might check:
    - Is there a test for the "wired region that has NO `region_full_data`
      entry" branch (fallback to `tooltip_layer.clear_tooltip()`)?
      That's pre-existing behavior but the new branch precedes it —
      make sure §4.4 didn't regress it.
    - Is there a test that verifies the overlay preserves alpha on
      a partially transparent base pixel? The code has
      `tinted.a = base.a` but no test exercises it directly.
    - Is there a test that a region with `interactive: false` AND
      `wired: false` is handled coherently? (Hover shouldn't fire
      because `interactive` gates the hit-test; unwired overlay still
      tints it.) Spec doesn't explicitly cover this combo — is it
      worth pinning?

C4. **Gate against regressions in §4.1 and §4.2.** The §4.1 tests pin
    `update_all_regions()` behavior and the non-interactive hover
    skip. The §4.2 tests pin the bitmap loader. Did §4.4 preserve all
    of these? Run both test files and confirm.

### D. Docs / claims accuracy

D1. The author claims `8503 passed, 2 skipped` (+16 from baseline
    `8487`). Run the suite and confirm:

    ```
    cd C:\Users\User\PycharmProjects\project-sovereign-map
    .venv\Scripts\python.exe -m pytest tests/ -q
    ```

D2. The author claims ruff is clean on the Python test files. Verify:

    ```
    .venv\Scripts\python.exe -m ruff check tests/test_map_unwired_overlay.py tests/test_map_renderer_cutover.py
    ```

D3. Does `docs/STATUS.md` accurately reflect what shipped? Look
    specifically at:
    - The "Last Updated" header — does it describe §4.4 correctly?
    - The Quick Stats row — tests count, current phase, blockers.
    - The "§4.4 Unwired Province Support COMPLETE" item (new in the
      Actionable-now list).
    - The "Suggested next cold-start sequencing" — is it coherent?

D4. Does `docs/SCALE_READINESS_PLAN.md` Section 4.4 accurately describe
    what shipped? Does the tracking table row (line ~1281) mark §4.4
    COMPLETE with the correct date?

D5. Does `CLAUDE.md` "Up Next" reflect §§4.1-4.4 as complete and remove
    §4.4 from the remaining list?

D6. Is there anywhere else in the docs that still says "§4.4 is open",
    "next: §4.4", or similar? Grep for it — including in the §4.2
    follow-ups section.

### E. Real-world art delivery scenarios

Imagine a commissioned Europe map arrives next week with 120 provinces
wired and 30 unwired outlined-only provinces. Walk through:

E1. A 4096x4096 bitmap with 30 unwired provinces — is the overlay
    performant? The helper iterates every pixel once; at 16M pixels
    that's a meaningful loop. Is this a one-time cost at scene load
    (fine) or does it re-fire on every update (bad)? Trace the call
    sites of `_build_map_textures()` and `_load_map_images()`.

E2. The bitmap has a pixel whose lookup color doesn't match ANY
    province in the registry. The §4.2 loader already rejects this. Is
    the §4.4 overlay impacted? (It shouldn't be — the overlay
    iterates `province_color_lookup.keys()`, not raw pixels, so unknown
    colors are ignored. Confirm.)

E3. The registry marks a province as `wired: false, interactive: true`.
    The player hovers — tooltip appears. Click — no-op. Now the same
    province: `wired: false, interactive: false`. The player hovers
    — NOTHING happens (because `_lookup_region_from_color_map` blocks
    the hit-test). Is that the right behavior? Or should non-
    interactive-and-unwired still let the player read the province
    name?

E4. An artist ships a bitmap where two provinces share the same
    `lookup_color` (one wired, one unwired). §4.3's validator would
    reject this at delivery, but if someone bypasses it, how does §4.4
    behave? The renderer's `province_color_lookup` would hold the
    LAST-written mapping, so one of them is "wrong" on hover. Is this
    a §4.4 concern or strictly a §4.3 concern?

### F. Things that worry you

Do a "smell pass" — read the code with no checklist and write down
anything that feels off, even if you cannot point to a specific bug.
The author is open to refactoring suggestions if the smell is real.

Specific things to watch for:
- Dead parameters, unused branches, or state that can't be reached.
- Constants that should be inlined, or inlined values that should be
  constants.
- GDScript subtleties — e.g., Dictionary as a set has keys that are
  strings here; is that the right key type given how
  `province_color_lookup` stores them?
- Does the overlay logic duplicate anything that should live in a
  shared helper with §4.2 validation?

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

Commands you ran and their results — at minimum the full pytest suite
and the ruff check.

## Overall assessment

One paragraph: ship as-is / ship with minor fixes / needs rework before
ship. Be direct.
```

Keep findings tight. Group by severity. If you find nothing wrong, say
so plainly — do not pad. Maximum report length: 1500 words unless the
findings genuinely require more.

**Do not edit any code.** This is a review pass only.
