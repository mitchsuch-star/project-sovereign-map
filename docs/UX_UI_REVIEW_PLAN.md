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
| ~~**Four surfaces have a grip** (the terminal, the region panel, the diplomatic ledger, the war-status panel)~~ **ONE grip — the terminal's (saved) — and a hidden 6-px edge-drag on the war HUD (no cursor, forgotten on every `update_wars`)**; every other screen and popup is a fixed rect. *(Corrected October 9, 2026 by the read-only census: the grep had matched* the Emperor's grip *in `diplomatic_ledger.gd` and `region_panel.gd`.)* | `main.gd:1548-1609`, `war_status_panel.gd:39-143` |
| **The capture harness never shot the user's frame.** IQ-10 runs a 1600×900 window at Interface Scale 1.0 and 2.0 and checks "nothing clipped"; it has no physical-size census, so 12-px type at 1.0 on a 1600-px window reads as a pass. *(And the user's monitor is ONE 5120×1440 panel at 100% — not 3440×1440 — on which the harness had been parking its window at x = 2565: the right half of the screen.)* | `tools/iq10_surface_screenshot.gd`, `tools/iq10_run_captures.py` |

The UI foundation sweep (`UI_VISUAL_FOUNDATION_SPEC.md`, July 2026) fixed the
font stack, the theme and the colour palette, and U2c made Interface Scale
global. It never set a floor in physical pixels and never asked what monitor
the player has. That is UXR-1.

## UXR-0 — The readability instrument (0.4 session; lands with UXR-1)

Extend the IQ-10 harness rather than build a second one.

1. **Physical mode.** `tools/iq10_run_captures.py --physical` shoots each
   surface at **five** window sizes — **1920×1080, 2560×1440, 3440×1440,
   5120×1440 (the user's own), 3840×2160** *(the fifth added October 9 by
   decision 1 of the review)* — with Interface Scale set as a player at that
   size would have it (after UXR-1: the auto-derived value; before it: 1.0, the
   shipped default, so the BEFORE frames show the user's experience). The
   window is real, parked PAST the desktop (x = 5200 — proven to render at
   5120×1440 and 3840×2160; the old 2565 sat on the user's single panel).
2. **The text census.** For every visible `Label` / `RichTextLabel` / `Button`
   / `LineEdit`, record the rendered font's **cap height in physical pixels**
   (`font.get_height(size) × content_scale_factor × the node's effective
   scale`), the node path and its text's first 40 characters, into the
   existing per-frame machine record (`iq10_surface_screenshot.gd` already
   writes every visible string and every overflowing label — this adds one
   number per row).
3. **The floor.** *(As ruled October 9, decision 2 — stated on the EM, not the
   cap height, because a 16-px cap is a 23-px em in this face and would have
   marked the theme's own body red; the cap and x heights are recorded beside
   it.)* A **body-class** row under **16 physical px em** is RED, under **13**
   a P1; a **caption-class** row (`theme_type_variation` Caption /
   CaptionButton / CaptionRich) under **14** is RED, under **12** a P1; the
   map's world-space furniture is a third tier, counted beside the floor
   (UXR-X4). The user may move the four numbers after seeing the frames. The
   report lists red rows by surface and resolution, worst first.
4. **The frame the user sees.** One captured frame per named surface at
   **5120×1440** and 1.0 is committed under `docs/audits/uxr0/UXR0_BEFORE_*.png`
   as the before-picture (shot from a pristine HEAD worktree, the client's
   commit named in the record); the same set after UXR-1.
5. **Pin.** `tests/test_uxr0_readability.py` runs the census on the committed
   records (not on Godot) and fails on any P1 row; the RED count is a ratchet.

**Done when:** the four-resolution census exists for all 127 IQ-10 surfaces and
the tutorial, dispatch, terminal, top bar and Generals rows are reported.

## UXR-1 — The scale fix with the widest reach (0.6 session; = DD-A)

1. **Auto-derived Interface Scale at first boot.** `ui_settings.gd` gains
   `derive_default_ui_scale()`: from `DisplayServer.screen_get_size()` and
   `screen_get_dpi()` of the window's screen, ~~scale = clamp(longest side ÷
   1920 blended with dpi ÷ 96, 1.0, 3.0)~~ **scale = max(dpi/96, (dpi/96 +
   height/1080)/2), +0.25 on a 32:9 panel (width/height ≥ 3.0), clamped
   [1.0, 3.0]** *(decision 3 of the review: "longest side ÷ 1920" derives 2.67
   on a 5120×1440 panel and a 1920×540 logical screen)*, rounded to 0.05. It is
   written to `user://ui_settings.cfg` ONLY when no `display/ui_scale` exists,
   so a player who already chose a scale keeps it. A monitor change re-derives
   only if the stored value was auto (a second key `display/ui_scale_auto = true`).
2. **The cap** `MAX_UI_SCALE` 2.0 → **3.0**; the pause slider and the
   terminal's +/− follow; the map's `_viewport_pixel_scale()` and the
   `clamp_centered_panel` budget already read the live factor (verify at 3.0:
   the ledger's eight tabs, the settlement popup's relax pass, the top bar's
   compact mode — three pins).
3. **The theme floor.** `main_theme.tres` gains the named sizes ~~`Caption`
   (13), `Small` (14), `Body` (16), `Heading` (22)~~ **`Caption` /
   `CaptionButton` / `CaptionRich` (14) beside the theme's Body (16) and
   `HeadingLabel` (22)** *(one caption size, not two — 13 at scale 1.0 is red by
   the floor's own rule)*; every `.tscn`/`.gd` override under 14 is replaced by
   the Caption family or, on a body surface, dropped to the theme's 16; every
   override AT 14 is decided by a table (a dialog's action button and a body
   description drop; chrome and sub-lines take Caption); the theme's Button
   size 15 → 16 — **no raw type under 15 logical px anywhere** outside two
   recorded exemptions, pinned by a census over the scene and script files.
   (The overrides at ≥ 15 shrink to named-size references in UXR-2; UXR-1
   only lifts the floor.)
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

### Landing record — UXR-0 + UXR-1 (Pre-Deploy S1a, October 9, 2026)

> Rules `SYSTEMS_REFERENCE.md` §99; the ruling `docs/audits/UXR_ADJUSTABILITY_REVIEW_2026_10_09.md`
> §7 (seven decisions, all at the defaults — "go"); pins `tests/test_uxr1_scale_fix.py`
> (the derivation driven through the engine, the floor's census, the card, the tutor
> card, the pause menu, the instrument) + `tests/test_uxr0_readability.py` (the
> committed records); rows `BUG_FIXES.md` §UXR-0 / UXR-1 (UXR-X1 … X4) +
> `DESIGN_REFINEMENT.md` §UXR (UXR-D1 … D5); records + frames `docs/audits/uxr0/`.

**UXR-0, the instrument.** The IQ-10 harness gained the text census (em / cap / x in
PHYSICAL px per visible node, with the tier — `get_screen_transform()` does not carry
`content_scale_factor`, measured), a `main` mode that boots the REAL `main.tscn` behind
a stub (the connection test and the topology answered with real captures; the APIClient
swapped AFTER `_ready` creates it; the boot WAITED FOR on `_initial_map_bootstrapped` —
the first war-room frame shot its map black because frames are not time off-screen),
`wait_for` / `read` / `@property` steps, and the SubViewport-aware visibility rule.
`tools/iq10_run_captures.py --physical` shoots the five resolutions (the fifth, 5120×1440,
is the user's own) with `--physical-scale auto|1.0`, `--project` shoots another checkout
with this repo's harness, and the index names the client's commit; six new shots
(`war_room_boot`, `war_room_tutorial`, `war_room_pause_settings`, `tutorial_card`,
`main_menu`, `main_menu_settings`) and a `war_room` payload group. The window moved
off the desktop (`[5200, 20]`; the old `[2565, 20]` sat on the user's single panel —
the IQ-10 pin flipped consciously). `tools/uxr0_readability_report.py` holds the floor
and writes the record.

**UXR-1, the fix.** The derivation (§99.1) and its chosen-beats-derived contract (§99.2);
the cap 3.0; the menu applies the resolved scale in `_ready` (UXR-X1); the first-run
card `ScaleCard` (§99.3); the theme floor (§99.4: three Caption variations, Button 15 → 16,
the recorded sweep over **189 sites** — 145 under 14 and 44 at 14 — leaving no raw type
under 15 outside two exemptions); the tutor card sized by the screen and height-bounded
(§99.5, UXR-X3); the pause menu's Settings unsqueezed (§99.6, UXR-X2); the menu column
re-fitted on short logical viewports (its last two buttons fell off an 800×450 frame
at scale 2.0 — found by the regression below).

**The reading — the named set (eleven surfaces × five resolutions = 55 readings), the
BEFORE shot from a pristine HEAD worktree (`05bbee2c`) at the shipped 1.0, the AFTER on
this tree at the derived scale (1.00 / 1.15 / 1.15 / 1.40 / 1.50):**

| | rows | RED | P1 |
|---|---|---|---|
| BEFORE (`readability_before_named_2026_10_09.json`) | 1,170 | **255** | **750** |
| AFTER (`readability_after_named_2026_10_09.json`) | 1,260 | **0** | **0** |

Every flag was real: at 1.0 the command window's output (11 px) read P1 and the tutor
card's body (13 px — the P1 line itself) RED on every monitor; the 5120×1440 frames
`docs/audits/uxr0/UXR0_BEFORE_*` and `UXR0_AFTER_*` (JPEG, the two war-room-tutorial
frames at full size, the rest at half) are the before/after picture of the user's own
screen. **The
done-when is MET on the instrument** (0 RED / 0 P1 on every named surface at every
resolution with the derived scale; the ratchet pinned at 0); ⚠ the user's half — "reads
the tutorial card on their monitor without changing anything" — is **UXR-4's eyes**.
The whole-client census (every IQ-10 surface at the five resolutions, before from the
worktree and after on this tree — UXR-0's "exists for all 127 surfaces") was still
shooting when S1a was committed (≈ 700 frames each) and lands with S1b as
`readability_{before,after}_all_2026_10_09.json` (counts + the worst five rows per
reading); the map's furniture is its own tier (UXR-X4).

**Found and corrected while building:** the ruling's own aspect term (2.3 crossed by a
21:9 panel — 3.0 in both twins, the driven table pins it); the review plan's "four
grips" (one); the pause-menu squeeze (X2), the unbounded tutor card (X3) and the unapplied
boot scale (X1) from the census; the 14-px body rows and the theme's own Button 15 from
the first AFTER reading (both decided, §99.4). **Regression:** the full IQ-10 set at
1600×900 × {1.0, 2.0} — 137 shots, 274 frames, 0 `SCRIPT ERROR`, 0 clipped text, the one
off-screen case fixed (the menu column). Parse harness EXIT=0 (the card and the probe
added to its lists), the class cache rebuilt for `ScaleCard`.

~~**Still open in S1 (S1b, the Settings additions — the review's decision 4/5):** window
mode + size picker, the terminal's default footprint as a viewport fraction, the scale
hotkeys, Reset layout, the CONTROLS reference, the Plain-font option; and the Settings
button that opens the sizing card on demand.~~

### Landing record — S1b, the Settings additions (October 9, 2026, the same session)

> Rules `SYSTEMS_REFERENCE.md` §99.8–§99.10; pins `tests/test_uxr1b_settings_additions.py`
> (26); rows `BUG_FIXES.md` §UXR-1b (UXR-X5, UXR-X6 routed).

**Built (decisions 4 + 5):** Settings → **DISPLAY** (Window: Maximized · Fullscreen ·
Borderless · Windowed; Size for Windowed, only the sizes that fit the screen; applied at
once and at the menu's boot; a no-op under a capture harness) · **INTERFACE** (the reset is
*Size for this screen (N%)* — the derivation, stored auto — not the old 100%; *Preview with
a sample…* opens the sizing card on the menu AND in the campaign, on its own layer above the
pause menu; *Body text: Garamond · Plain (Source Sans 3)*, swapped live on the project
theme's body faces only; *Reset layout*: the scale to the derivation, the command window to
its fraction, the window to Maximized — sound, the key and the School's latch kept) ·
**CONTROLS** (the key reference in four lines) · **Ctrl+= / Ctrl+− / Ctrl+0** on both input
roads and on the menu (the map's bare +/− ignore a Ctrl press) · **the command window's
default footprint = 28% × 32% of the logical viewport** (1,000 × 329 logical on the user's
panel at 1.40 where 400 × 270 had been), re-derived until the grip is dragged; the grip's
double-click and Reset layout clear the stored size · going to Settings answers a standing
first-run card.

**The floor's residue, from the whole-client census:** the campaign log's tiers 14 / 12 / 11
→ 18 / 16 / 14 (routine in `CaptionRich`); the end screen's bold 15 → 17 (its body); the six
literal 15s (four dialog titles / messages, the pause menu's two confirm buttons) dropped to
the theme — `FIFTEEN_TSCN` in the recorded sweep. **Routed:** UXR-X5 (the diorama's tableau
labels, 8–12 design px under a tray scale that never exceeds 1.0) and UXR-X6 (the
war-detail bar tags, `max(7, font_size − 3)`), both UXR-2's.

**The reading.** The named set on the S1b tree: **55 readings, 1,355 rows, RED 0, P1 0**
(the AFTER record and the 5120×1440 AFTER frames re-taken on this tree). The whole client
(137 surfaces × 5 resolutions): BEFORE (the worktree at `05bbee2c`, scale 1.0) **RED 1,565 /
P1 4,120**; after S1a RED 62 / P1 127; **after S1b RED 32 / P1 92** — on six surfaces, every
one UXR-X5's (`diorama_aadj` / `diorama_dadj`: 14 RED + 20 P1 each) or UXR-X6's (the four
`war_detail_*`: 1 RED + 13 P1 each); `readability_after_all_2026_10_09.json`, pinned as a
ratchet with the routed-families invariant in `tests/test_uxr0_readability.py`. Regression at 1600×900 × {1.0, 2.0} over the changed surfaces: 28 frames, 0
`SCRIPT ERROR`, 0 clipped, 0 off-screen; the new sections all present in the census. Parse
harness EXIT=0.

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
