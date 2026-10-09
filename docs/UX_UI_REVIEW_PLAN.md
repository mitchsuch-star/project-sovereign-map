# UX / UI Review Plan — readable first, then the full look-and-feel pass

> **Status: PLAN, October 8, 2026.** Ordered by `docs/PRE_DEPLOY_PLAN.md` §2.
> Rows UXR-0 … UXR-4. Written from the user's report: *"in tutorial i cant read
> most text even on ultra wide only some boxes are adjustable."* The report is
> correct and the reasons are in the tree (§0). Deep dive DD-A = UXR-0 + UXR-1.
>
> **Gate on every UXR slice:** the readability instrument's reading (UXR-0)
> before and after, frames at the four resolutions in `docs/audits/`, the parse
> harness EXIT=0, boot 0 `SCRIPT ERROR`, and — for anything the player sees —
> the user's eyes at their own monitor (UXR-4). No backend series moves; a UXR
> slice that touches `backend/` does so for payload text only.

## 0. Why the text is unreadable (measured October 8, 2026)

| Fact | Where |
|------|-------|
| **No stretch mode.** `project.godot` sets `window/size/mode=2` (maximised) and nothing under `display/window/stretch`, so the GUI draws at 1 logical px = 1 physical px on any monitor. | `godot-client/project-sovereign/project.godot` |
| **No DPI or resolution detection.** `grep DisplayServer.screen|screen_get_dpi|get_screen_size` over every `.gd` returns nothing. The default Interface Scale is **1.0** and the cap is **2.0**. On a 3440×1440 or 3840×2160 panel 1.0 is unreadable and 2.0 is marginal. | `scripts/ui_settings.gd` (`DEFAULT_UI_SCALE`, `MAX_UI_SCALE`) |
| **The tutorial card is a fixed 396-px rect of 12–13-px type**, top-right anchored, with no grip and no viewport-fraction width. | `scenes/tutorial_overlay.tscn` (offsets −404 … −8; `font_size = 12/13`) |
| **268 font-size overrides** (174 in `.tscn`, 94 in `.gd`) sit beside a theme whose default is 16 — most of them smaller (12–13), so the theme floor does not protect them. `main.tscn` alone carries 29. | grep `theme_override_font_sizes` / `add_theme_font_size_override` |
| **90 `custom_minimum_size` sites** author fixed rects; **31 surfaces** call `Utils.clamp_centered_panel` to shrink into a small viewport, but nothing GROWS a panel into a large one. | `scripts/utils.gd:604` |
| **Four surfaces have a grip** (the terminal, the region panel, the diplomatic ledger, the war-status panel); every other screen and popup is a fixed rect. | grep `grip` over `.gd` |
| **The capture harness never shot the user's frame.** IQ-10 runs a 1600×900 window at Interface Scale 1.0 and 2.0 and checks "nothing clipped"; it has no physical-size census, so 12-px type at 1.0 on a 1600-px window reads as a pass. | `tools/iq10_surface_screenshot.gd`, `tools/iq10_run_captures.py` |

The UI foundation sweep (`UI_VISUAL_FOUNDATION_SPEC.md`, July 2026) fixed the
font stack, the theme and the colour palette, and U2c made Interface Scale
global. It never set a floor in physical pixels and never asked what monitor
the player has. That is UXR-1.

## UXR-0 — The readability instrument (0.4 session; lands with UXR-1)

Extend the IQ-10 harness rather than build a second one.

1. **Physical mode.** `tools/iq10_run_captures.py --physical` shoots each
   surface at four window sizes — **1920×1080, 2560×1440, 3440×1440,
   3840×2160** — with Interface Scale set as a player at that size would have it
   (after UXR-1: the auto-derived value; before it: 1.0, the shipped default, so
   the BEFORE frames show the user's experience). The window is real, parked
   as today (`iq10_run_captures.py` already handles a 2560-wide primary).
2. **The text census.** For every visible `Label` / `RichTextLabel` / `Button`
   / `LineEdit`, record the rendered font's **cap height in physical pixels**
   (`font.get_height(size) × content_scale_factor × the node's effective
   scale`), the node path and its text's first 40 characters, into the
   existing per-frame machine record (`iq10_surface_screenshot.gd` already
   writes every visible string and every overflowing label — this adds one
   number per row).
3. **The floor.** A row under **16 physical px** is RED; under **13** is a P1.
   The numbers are the plan's defaults (≈ 11 pt on a 27-inch 1440 panel at
   arm's length) and the user may move them after seeing the frames. The
   report lists red rows by surface and resolution, worst first.
4. **The frame the user sees.** One captured frame per surface at 3440×1440
   and 1.0 is committed under `docs/audits/UXR0_BEFORE_*.png` as the
   before-picture; the same set after UXR-1.
5. **Pin.** `tests/test_uxr0_readability.py` runs the census on the committed
   records (not on Godot) and fails on any P1 row; the RED count is a ratchet.

**Done when:** the four-resolution census exists for all 127 IQ-10 surfaces and
the tutorial, dispatch, terminal, top bar and Generals rows are reported.

## UXR-1 — The scale fix with the widest reach (0.6 session; = DD-A)

1. **Auto-derived Interface Scale at first boot.** `ui_settings.gd` gains
   `derive_default_ui_scale()`: from `DisplayServer.screen_get_size()` and
   `screen_get_dpi()` of the window's screen, scale = clamp(longest side ÷
   1920 blended with dpi ÷ 96, 1.0, 3.0), rounded to 0.05. It is written to
   `user://ui_settings.cfg` ONLY when no `display/ui_scale` exists, so a player
   who already chose a scale keeps it. A monitor change re-derives only if the
   stored value was auto (a second key `display/ui_scale_auto = true`).
2. **The cap** `MAX_UI_SCALE` 2.0 → **3.0**; the pause slider and the
   terminal's +/− follow; the map's `_viewport_pixel_scale()` and the
   `clamp_centered_panel` budget already read the live factor (verify at 3.0:
   the ledger's eight tabs, the settlement popup's relax pass, the top bar's
   compact mode — three pins).
3. **The theme floor.** `main_theme.tres` gains named sizes `Caption` (13),
   `Small` (14), `Body` (16), `Heading` (22); every `.tscn`/`.gd` override
   under 14 is replaced by `Small` or `Caption` — **no type under 13 logical
   px anywhere**, pinned by a census over the scene files. (The 268 overrides
   shrink to named-size references in UXR-2; UXR-1 only lifts the floor.)
4. **The first-run card.** On the main menu's first boot (and from Settings
   afterwards) a one-screen card: *"Can you read this comfortably?"* with the
   derived scale applied, a live sample of the terminal's body text and the
   tutorial's caption, a slider, and *"Looks right"*. It writes
   `display/ui_scale` and clears `_auto`. It is the only new surface in the
   plan.
5. **The tutorial card** gets its width as a viewport fraction (min 396 px,
   22% of the logical width, max 560) and its fonts from the theme sizes, so
   the auto scale reaches it. The rest of the card's layout is UXR-2's.

**Done when:** UXR-0 reads **0 RED rows** on the tutorial, the dispatch, the
terminal, the top bar and the Generals screen at all four resolutions with the
auto-derived scale, and the user reads the tutorial card on their monitor
without changing anything.

## UXR-2 — The layout law (1 session)

"Only some boxes are adjustable." One rule, applied everywhere:

> A surface is either **anchored** (its rect is a fraction of the viewport,
> with min and max in logical px) or **clamped-and-gripped** (a fixed authored
> rect that `clamp_centered_panel` shrinks and a grip lets the player resize,
> the size remembered in `ui_settings.cfg`). No surface is a bare fixed rect.

1. **Grips** on the five big screens that lack one: the Strategic Ledger, the
   Generals screen, the dispatch view, the campaign log, the Gazette — the
   terminal's grip (`main.gd`, U2 Part 1) becomes a shared `ResizeGrip` node
   with its persistence in `ui_settings.gd` (`get/set_panel_size(name)`).
2. **Anchors** for the HUD family: the top bar (already compact-mode aware),
   the war-status panel, the notification rail, the region panel, the tutorial
   card — viewport fractions with min/max.
3. **Clamp coverage census.** Every `CanvasLayer` popup (layers 100–122)
   either calls `clamp_centered_panel` on open or is anchored; a pin walks the
   `.tscn` files and fails on an uncovered fixed rect (today 31 of ~45 call
   it).
4. **The override diet.** The 268 font-size overrides become named theme-size
   references (`theme_type_variation = "Caption"` and kin); the census from
   UXR-1 pins that no raw number under 14 survives and that the count of raw
   overrides falls (ratchet).
5. **Scroll where content is unbounded.** The rule in `clamp_centered_panel`'s
   own docstring — a `fit_content` RichTextLabel outside a ScrollContainer
   cannot be clamped — is enforced by a scene census; the IGR-F letter-book
   clipping and the Step-7 "terminal's first trim wiped the scrollback" were
   both this class.

**Done when:** the census reads every surface anchored or clamped-and-gripped;
the five screens resize and remember; UXR-0 reads 0 RED rows on every surface
at every resolution.

## UXR-3 — The look-and-feel review (1 session to review, 1 to fix)

The "full look feel ux review", run the way the score was run: a fixed
checklist, blind readers, frames as evidence, item flips not impressions.

**Surfaces, by time on screen** (the review order): the war room (map +
terminal + top bar) → the morning dispatch → the Generals screen → the
diplomacy wizard and the settlement table → the Strategic Ledger (eight tabs)
→ the tutorial → the enemy-phase dialog and the battle diorama → the popups
(objection, interrupt, capture, petition, letter-book) → the main menu and
Settings → the campaign-end card.

**The checklist — 8 binary items per surface** (`docs/UX_CHECKLIST_V1.json`,
frozen before the first reading, the Score Finish's §4 pattern):

| # | Item | How it is judged |
|---|------|------------------|
| R1 | **Readable** — 0 RED rows in UXR-0 at all four resolutions | instrument |
| R2 | **Hierarchy** — the one thing the surface is for is the largest or first element; the eye lands on it in the frame | reader |
| R3 | **Contrast** — body text ≥ 4.5:1 against its panel, captions ≥ 3:1 (measured off the frame) | instrument |
| R4 | **Consistency** — chrome, chips, close-X, headings and spacing match the theme (no one-off colours or sizes; the override census) | instrument + reader |
| R5 | **Affordance** — everything clickable looks clickable and everything that looks clickable is; disabled states say why (honest availability) | reader, driven |
| R6 | **Feedback** — every action answers within the frame (a chip echoes, a send acknowledges, a save confirms) | driven |
| R7 | **Fit** — nothing clipped, nothing overflowing, nothing under a modal; works at 1920 and 3840 | instrument |
| R8 | **Discoverability** — the surface's key action is reachable without the manual (the IQ-10 "must_show" line, re-read as a new player) | reader |

**Readers:** three blind agents on the committed frames and the driven
records, reporting the median mark and the spread, as `tools/score_panel.py`
does for the score (`eyes RUN`). The user's marks override.

**Output:** `docs/audits/UXR3_REVIEW_<date>.md` — a surface × item table,
the worst five surfaces named, every ✗ filed as a `BUG_FIXES.md` row tagged
`⟨UXR-3 · <surface> · ui_ux⟩` with its frame. The fix session takes the worst
five first and re-reads only the flipped items.

**Done when:** every surface in the order above has a reading; the top five
surfaces by time on screen read 8 of 8; no surface reads under 6 of 8.

## UXR-4 — The user's eyes (0.5 session, the last before the deploy)

The sign-off convention stands: the user, at their monitor, in the real client.
A scripted twenty-minute walk — the tutorial end to end, one dispatch, one
peace table, one battle, the Generals screen, Settings — with the UXR-0 frames
beside it. Each stop is a yes/no; a no becomes a row and goes back to UXR-3's
fix slice. **Nothing deploys over an open UXR-4 no.**

## What this plan does not do

- No visual redesign. The theme, the palette, the fonts and the war-table
  pieces stand (the July foundation sweep and its sign-offs).
- No new screens beyond the first-run sizing card.
- No change to what the backend says; a row about COPY goes to the narration
  or command pillar's owner, not here.
- No stretch mode. `canvas_items` stretch would blur the native-resolution
  map (UI-2 Part 2 built the map at physical pixels on purpose); the fix is the
  scale factor, which is what the project already uses.
