# Audit Prompt: Map Readiness §4.3 — Offline Color-Map Validator

> **For:** A reviewing agent with no prior context on this session.
> **Commit under review:** `d6a4435` ("Land Map Readiness §4.3: offline color-map validator")
> **Repo:** `C:\Users\User\PycharmProjects\project-sovereign-map`
> **Branch:** `master` (already pushed)

---

## What you are auditing

The author landed `tools/validate_province_map.py` plus
`tests/test_province_map_validator.py` (22 tests) plus doc updates in
`CLAUDE.md`, `docs/STATUS.md`, and `docs/SCALE_READINESS_PLAN.md`.

The change implements **Map Readiness Section 4.3** — an offline color-map
validator for commissioned art deliveries. The spec lives at
`docs/SCALE_READINESS_PLAN.md` Section 4.3. The §4.2 runtime loader
(`map_renderer_base.gd::_load_map_images()`) already enforces dimension
match and lookup-color presence at load time; §4.3 was scoped to add the
offline acceptance checks the runtime cannot do well.

You are an independent reviewer. The author claims:

- 22 new tests pass; full Python suite is green at **8480 passed, 2 skipped**.
- Ruff clean on the two new files.
- The shipped placeholder JSON passes all registry-only checks.
- The validator deliberately does NOT duplicate the §4.2 runtime checks blindly.

Verify these claims, then go beyond them.

---

## Files to read (in order)

1. **Spec:** `docs/SCALE_READINESS_PLAN.md` Section 4.3 (around lines 977-1010
   after the edit). Also read Section 4.2 immediately above it so you understand
   what the runtime loader already does.
2. **Tool:** `tools/validate_province_map.py` (single file, ~480 lines).
3. **Tests:** `tests/test_province_map_validator.py` (22 tests).
4. **Adjacent context:** `tests/test_map_bitmap_contract.py` (existing §4.2
   tests; the new validator borrows the PNG fixture writer pattern from here).
5. **Adjacent context:** `tests/test_map_placeholder_assets.py` (pins the
   placeholder JSON schema the validator reads).
6. **Renderer:** `godot-client/project-sovereign/scenes/map_renderer_base.gd`
   `_load_map_images()` function — the §4.2 runtime checks the validator must
   COMPLEMENT, not duplicate blindly.
7. **Doc claims:** `docs/STATUS.md` (Quick Stats + the "Map Readiness Closure
   Pass — §4.3 Color-Map Validator COMPLETE" item), `CLAUDE.md` "Up Next"
   bullet for §4.3.

---

## What to check

Audit the change against this checklist. For each finding, report:
**severity** (BLOCKER / MAJOR / MINOR / NIT), **location** (file:line),
**what is wrong**, **why it matters**, and **suggested fix**.

### A. Spec conformance

A1. Does the validator implement every check the spec lists in Section 4.3?

  - "Sentinels/background colors are only used where intended and are not
    assigned to provinces"
  - "No unexpected colors exist after import (anti-aliasing / stray-pixel
    detection)"
  - "Every province in the registry appears in the lookup image with at
    least N pixels"
  - "Flags tiny pixel islands (< 5 pixels of a color) as likely export
    artifacts"
  - "Emits a CI-readable failure report before any commissioned art is
    accepted"

A2. The spec says "do not duplicate the runtime loader's size-match and
    lookup-color-presence checks blindly. §4.2 now enforces those at load
    time; §4.3 should focus on offline acceptance checks that are expensive,
    noisy, or art-pipeline-specific."

    Does the validator stay on the right side of this rule? Where it does
    overlap with §4.2 (e.g., `SIZE_MISMATCH`, `UNMAPPED_COLOR`), does it
    add value the runtime cannot — for example, collecting all findings
    instead of bailing on the first failure?

A3. The spec also says "Run: Before integrating any new art delivery. Also
    runs in CI." Is the tool wireable into CI? (Stdlib-only, no project
    imports, no env requirements?) Is it documented how to wire it in?

### B. Implementation correctness

B1. **PNG decoder.** It is hand-rolled (`zlib` + `struct`). Walk through:

  - Signature check.
  - IHDR parsing — does it actually validate `compression`, `filter_method`,
    and `interlace` and reject unsupported values?
  - bit_depth/color_type guard — does it accept 8-bit RGB (2) and RGBA (6)
    only and clearly reject everything else?
  - IDAT concatenation — multiple IDAT chunks should be supported (real PNGs
    often have several). Try a synthetic test if you doubt it.
  - Decompressed length check — `expected_len = (1 + width * bpp) * height`
    is correct for non-interlaced filtered scanlines.
  - `_unfilter_scanlines()` — read it carefully. Filter types 0-4 (None,
    Sub, Up, Average, Paeth) are the full set. The math should match the
    PNG spec (Sub uses left, Up uses up, Average uses `(left+up)>>1`,
    Paeth uses the Paeth predictor on left/up/up-left). Does the function
    correctly handle the first row (no `up`) and the first `bpp` bytes of
    each row (no `left`)?

B2. **Color counting.** `_count_colors()` iterates every pixel building a
    counts dict and a first-seen coordinate. Is the first-seen coordinate
    in the form expected by the rest of the code (`(x, y)` not `(y, x)`)?

B3. **`validate_images()` semantics.**

  - Sentinel pixels in the lookup are skipped from both `UNMAPPED_COLOR`
    and `TINY_ISLAND` reporting. Is that the right call? (A registry can
    have provinces whose `lookup_color` matches the sentinel — that is
    caught at the registry pass, not the image pass. Could a sentinel
    pixel ever indicate a real bug the validator misses?)
  - What happens when the visual and lookup PNGs have different sizes?
    Currently `SIZE_MISMATCH` is reported and the function continues with
    the lookup-image checks. Is that the right behavior, or should it bail?
  - `MISSING_PROVINCE` (0 pixels) and `INSUFFICIENT_COVERAGE` (1 to
    `min_coverage_pixels-1`) are mutually exclusive per province by
    construction. Confirm the branching is correct.
  - `UNMAPPED_COLOR` and `TINY_ISLAND` can both fire on the same color.
    Is that intentional? (The author says yes — they're different
    concerns.) Does the test pin this overlap?

B4. **Registry validation.**

  - `load_registry()` raises `ValueError` for malformed input. Does it
    catch the cases that matter (missing `regions`, missing
    `no_province_color`, missing `lookup_color`, malformed RGB triple)?
  - `validate_registry()` does sentinel collision and duplicate detection.
    Could there be other registry-side problems worth catching at this
    stage (e.g., negative `lookup_color` channels — already caught by
    `load_registry`; identical `province_id`s — not caught here, but
    `tests/test_map_placeholder_assets.py` has a separate uniqueness test;
    is that division of responsibility the right place for it)?

B5. **CLI contract.**

  - Does `--visual` without `--lookup` exit 2 with a clear message?
  - Does `--strict` correctly promote warnings to a non-zero exit?
  - Does `--json` emit valid JSON that downstream CI can parse?
  - Are the default thresholds (50 / 5) reasonable for the eventual
    Europe-scale art? The spec says "at least N pixels" without naming N.
    Comment on whether 50 is defensible.

### C. Test quality

C1. Are the tests genuinely BEHAVIORAL (asserting what the validator does
    given specific inputs) or do they short-circuit through the
    implementation? Spot-check 3-5 tests.

C2. Coverage of the PNG decoder: the tests pin all five filter types
    (`test_png_decoder_handles_all_five_filter_types`). Does the fixture
    actually exercise the unfiltering math, or does it accidentally use
    filter type 0 throughout?

C3. Are there obvious test gaps? Some specific things to check:

  - Multiple IDAT chunks
  - Very tall or very wide images (e.g., 1x1000)
  - All-sentinel images
  - Empty `regions` registry
  - Color tuple equality with same RGB but different alpha (the validator
    drops alpha — confirm this is tested with an RGBA fixture where alpha
    varies)
  - A registry whose `no_province_color` is non-black (say `[255, 0, 255]`)
    — does the sentinel-collision path still work?

C4. The tests all use filter-type-0 RGBA fixtures except the one explicit
    all-five-filter-types test. Is that adequate coverage for filters 1-4
    on the rest of the validator surface, or could a filter-type-2 PNG
    fed to `validate_images()` reveal a bug not surfaced by the
    decoder-only test?

### D. Docs / claims accuracy

D1. The author claims `8480 passed, 2 skipped` (+27 from baseline
    `8453`). Run the suite and confirm. Note any test added that is NOT
    part of the new file.

    ```
    cd C:\Users\User\PycharmProjects\project-sovereign-map
    .venv\Scripts\python.exe -m pytest tests/ -q
    ```

D2. The author claims ruff is clean on the new files. Verify:

    ```
    .venv\Scripts\python.exe -m ruff check tools/validate_province_map.py tests/test_province_map_validator.py
    ```

D3. Does `docs/STATUS.md` accurately reflect the implementation? Look
    specifically at:

  - The "Last Updated" header
  - The Quick Stats row
  - The "Map Readiness Closure Pass — §4.3 Color-Map Validator COMPLETE"
    item (item #5 under "Actionable now")
  - The "Real Map Readiness Gate" item #6 (validator)
  - The "Next bug-owned implementation slice" line
  - The "Current Session 8 progress" paragraph

D4. Does `docs/SCALE_READINESS_PLAN.md` Section 4.3 accurately describe
    what shipped? Does the tracking checklist row mark §4.3 DONE?

D5. Does `CLAUDE.md` "Up Next" reflect §4.3 as complete and §4.4 as the
    only remaining non-art map-readiness item?

D6. Is there anywhere ELSE in the docs that still says "§4.3 is open" or
    "next: §4.3"? Grep for it.

### E. Real-world art delivery scenarios

Imagine a commissioned Europe map arrives next week as two PNGs and an
updated registry JSON. Walk through:

E1. The art studio sends an indexed-color PNG (color_type 3) instead of
    RGB/RGBA. What happens? Is the error message clear enough that the
    studio knows what to fix?

E2. The studio sends a 4096x4096 visual + lookup. How long does the
    validator take? (Not a blocker if slow, but flag if it is unusable.)

E3. The studio uses anti-aliasing on province borders, producing thousands
    of tiny color islands. Does the report stay readable, or does it
    drown the user in 5,000 `TINY_ISLAND` warnings? Should there be an
    aggregate cap or summary?

E4. The registry forgets one province but the lookup PNG has a color for
    it. How does the validator describe the failure?

E5. The registry adds a province that doesn't exist in `REGIONS_DATA` (the
    backend region table). The validator does not check this — should it?
    Or is that out of scope for §4.3 and properly belongs in a different
    test?

### F. Things that worry you

Do a "smell pass" — read the code with no checklist and write down
anything that feels off, even if you cannot point to a specific bug. The
author is open to refactoring suggestions if the smell is real.

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
