# Audit Report: Map Readiness 4.4 - Unwired Province Support

## Findings

### [MAJOR] Active status docs still route future work to already-complete 4.4
**Location:** `docs/STATUS.md:123-131`; `docs/SCALE_READYNESS.md:29`; `docs/SCALE_READYNESS.md:653-656`

**What:** The top of `docs/STATUS.md` and the dedicated 4.4 entry correctly mark unwired province support complete, but the lower routing block still says the "Next bug-owned implementation slice" is 4.4 and that remaining non-art Session 8 work narrows to 4.4. `docs/STATUS.md` also points readers at `docs/SCALE_READYNESS.md` as the current audit context, yet that document still says Phase 4.1-4.4 are all "NOT DONE."

**Why it matters:** A cold-started contributor following the active status docs can reopen closed work or mis-prioritize the next slice. For a repo that relies heavily on handoff docs, contradictory routing is a planning bug, not just a cosmetic typo.

**Suggested fix:** Update or remove the stale routing paragraphs in `docs/STATUS.md`, and either refresh `docs/SCALE_READYNESS.md` or mark it explicitly as a historical snapshot so it cannot override the current closure-pass state.

### [MINOR] The unwired tooltip is barely distinguishable from the fogged-region tooltip
**Location:** `godot-client/project-sovereign/scenes/map_renderer_base.gd:1634`; `godot-client/project-sovereign/scenes/map_renderer_base.gd:1654`

**What:** The new unwired tooltip panel uses `Color(0.08, 0.08, 0.1, 0.92)`, while the fogged-region tooltip uses `Color(0.08, 0.08, 0.12, 0.95)`. That is only a very small blue-channel and alpha shift. The implementation does add different text content, but the panel treatment itself is not meaningfully distinct despite the docs claiming authors can never confuse the two states.

**Why it matters:** "Unwired" and "fogged" communicate different tactical meanings. If their hover chrome looks almost identical, the new 4.4 affordance loses clarity exactly where the spec was trying to make the states easy to tell apart.

**Suggested fix:** Give unwired a clearly different hue/value treatment, or add a stronger badge-style treatment for the suffix line so the state reads immediately without relying on subtle panel-color deltas.

### [MINOR] The new overlay tests do not cover alpha preservation
**Location:** `godot-client/project-sovereign/scenes/map_renderer_base.gd:510-512`; `tests/test_map_unwired_overlay.py:56-76`; `tests/test_map_unwired_overlay.py:146-164`

**What:** The runtime implementation correctly restores `base.a` after `base.lerp(...)`, but the Python mirror in `tests/test_map_unwired_overlay.py` models only RGB tuples. If a future edit removed `tinted.a = base.a`, the 4.4 behavioral tests would still all pass.

**Why it matters:** Commissioned art can include partially transparent pixels. If alpha starts drifting during the overlay pass, the visible regression will show up in shipped art while the dedicated 4.4 regression suite stays green.

**Suggested fix:** Extend the mirror to RGBA or add one targeted test that feeds a partially transparent pixel through the overlay contract and asserts that alpha is unchanged.

## Verification log

- `.\\.venv\\Scripts\\python.exe -m ruff check tests/test_map_unwired_overlay.py tests/test_map_renderer_cutover.py`
  - Result: `All checks passed!`
- `.\\.venv\\Scripts\\python.exe -m pytest tests/ -q`
  - Result: `8503 passed, 2 skipped in 20.33s`
- `git show --stat --oneline 3cbe327`
  - Result: commit touched 6 files; renderer, 2 Python test files, and 3 docs
- `rg -n "region_clicked\\.emit|region_hovered"` plus targeted reads of `map_renderer_base.gd`
  - Result: only one live `region_clicked.emit(...)` site exists, at the left-click path in `map_renderer_base.gd`; no downstream `region_hovered` / `region_clicked` consumers were found

## Overall assessment

Ship with minor fixes. The renderer-side 4.4 behavior is sound: the overlay runs in the right place on both texture paths, unwired provinces remain hover-identifiable, click suppression happens at the only live emit site, and 4.1's `update_all_regions()` gate still keeps unwired gameplay state out of the wired data structures. The issues I found are documentation drift, weak visual differentiation for the new tooltip state, and one worthwhile regression-test gap.
