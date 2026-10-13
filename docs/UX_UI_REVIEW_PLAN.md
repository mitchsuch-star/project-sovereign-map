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

1. **Grips** on the ~~five~~ **six** *(the user's ruling, S9: the Diplomatic Ledger too)* big screens that lack one: the Strategic Ledger, the
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
4. **The override diet.** The ~~268~~ **72** *(at S9's start — UXR-1's sweep had removed 196)* font-size overrides become named theme-size
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

### Landing record — UXR-2 (Pre-Deploy S9, October 12, 2026)

> Built in slices on master (A the routed families → B the named sizes and
> scroll → C the grips and the refit → D the anchors → E the landing re-shoot).
> Rows `BUG_FIXES.md` §UXR-2; pins `tests/test_uxr2_*.py`.

**The rulings of the session (the user, before the build):**
1. **Scope.** S9 builds the five parts, plus UXR-X5 / X6 (the done-when's readability half) and UXR-D5 (the grips). UXR-D1 (a Text-size slider), D2 (High contrast), D3 (HUD Centred + Fit Europe) and UXR-X4 (map labels follow the scale) move to a new **S9b** row in `PRE_DEPLOY_PLAN.md` §2, before UXR-3, each keeping its done-when and its test. UXR-D4 (the Side Desk) keeps its own gate.
2. **Six screens get grips, not five.** The Diplomatic Ledger is included. The list above was written beside §0's miscounted "four grips" grep and was never corrected with it.
3. **The font ladder is pixel-identical.** There is one named step per size in use. Folding 24 → 22 and 30 → 28 is UXR-3's R4 call, made with frames.

**The plan's numbers, corrected by the reconnaissance:**
- There were **72** raw font-size overrides at S9's start (44 `.tscn` + 28 `.gd`), not 268. UXR-1's sweep had already removed 196.
- UXR-X5 was **not** the tray's cap (see Slice A).
- Part 5's two cited incidents are not the `fit_content` class. IGR-F was a floorless ScrollContainer squeezed by its chrome. SF7-X17 was an engine-API trim. The class's real history is PS18-10 / 14 / R4 and UXR-X3.

**Slice A — the routed families read.**
- **UXR-X6 (the war-detail popup).** The bar's own text, the score and both side tags, takes the theme's Caption. Before, it was `max(7, font_size − 3)` = 8 / 7 px for the tags and 11 / 9 px for the score. Both bars are 22 px, and the tags sit past the track's 14-px rim cap (UXR-X8, which the first readable frame showed).
- **UXR-X5 (the battle diorama).** The cause was measured, not assumed. The tray scale is exactly 1.0 at all five resolutions. The 8.8 px came from design sizes 10–14 multiplied by each rank's `1 − 0.12·depth`. The fix splits a block in two: its **art** (figures, standard, locket) recedes with depth, and its **text** reads at the theme's sizes at every depth (name 16; strength, status, faith, odometer captions, skip hint, reserve tail at Caption 14). Only the text's anchors follow the depth.
  - The status line joins the faith caption **under the feet**: two lines at the floor's sizes fit between ranks, three do not. This is the one visible design change, shown at the review pause.
  - `_mk_label` takes a theme variation, never a size.
  - The engraved display type keeps five literal sizes: the clash 26, the odometer figures 24, the banner 30 and the plate 19.
- **New IQ-10 boards** (the states no board had shot): a rout with a conquest, four contingents a side (reserve tails, a reinforcer, depth-2 faith), a fleet action, and the war-detail coalition view (boot and t20). 142 shots.
- **Found by the four-contingent board, and present at HEAD before any change (UXR-X7):**
  - The next rank's standard stood over a name or strength line. Fix: every rank's words draw above every standard (`TEXT_Z`), with a thin dark rim on the name and strength.
  - The reserve tail, one step beyond the last rank, ran across the depth-2 name. Fix: it sits in the baize's outboard bottom corner, over the reserve shelf.
- **Filed, not fixed: UXR-X9** (UXR-3 S12). The verdict's worst-case four lines can touch the nameplate. The scroll census allowlists `_verdict` as free-positioned.
- **The reading:**
  - The five diorama boards went from **RED 84 / P1 151** at HEAD `95ea0459` (shot from a pristine worktree) to **0 / 0**.
  - The routed families and the new boards total **55 readings, RED 0 / P1 0**: `docs/audits/uxr0/readability_routed_2026_10_12.json`, pinned by `tests/test_uxr2_the_routed_families.py`.
  - The whole-client ratchet (32 / 92) stays until Slice E's full re-shoot.
- **Conscious pin flips:** `test_iq5_both_sides_of_the_butchers_bill.py` (the faith caption's anchor follows the depth, on the fate line) and `test_sf7_s9_the_frames.py` (the tail no longer follows the steps).

**Slice B — the named sizes (part 4) and scroll where unbounded (part 5).**

*Part 4, the diet.* The theme gained a size-only ladder, one named step per size in use (the user's ruling: pixel-identical):

| Step | Size |
|---|---|
| `BodyLarge` / `BodyLargeRich` | 17 |
| `Lead` / `LeadRich` | 18 |
| `ScreenTitle` | 20 |
| `DialogTitle` | 22 |
| `DialogTitleLarge` | 24 |
| `DisplayTitle` | 28 |
| `DisplayTitleLarge` | 30 |

These sit beside the Caption family (14), the theme's own 16, and `HeadingLabel` (22, styled). Each rich step defines exactly the sizes the overrides it replaced had set, so no `[b]` or `[i]` span moves.

The conversions:
- **The 44 scene overrides.** The 22 that were the theme's own 16 were deleted (17 of them on Buttons). The other 22 became `theme_type_variation`. Every one was a Label, and none already carried a variation.
- **The script overrides.** The campaign end's body becomes `BodyLargeRich`. The log's tiers are `LeadRich` / `CaptionRich`, and `TIER_FONT_SIZES` is retired. The terminal's suggestion row now takes no override: the theme's RichTextLabel 16 is the LineEdit's 16, and the CX-7 driven pin keeps the two equal. The notice title is `BodyLarge` and the diorama verdict is `BodyLargeRich`.
- **The ratchet.** Raw overrides fell from **72 to 18**, every one a named exemption with an exact count: the map's world-space furniture 7 (UXR-X4, now S9b); the dev smoke scene 1; the title screen's display type 5; the tableau's engraved display 5.

`tests/test_uxr2_override_diet.py` checks seven things:
- It counts every override, literal or computed, plus the `set(...)` and string-call dodges. This closes the loophole UXR-X5 and X6 escaped through.
- It pins a ledger of non-literal sizes.
- It pins the ladder exactly.
- Every step except `HeadingLabel` must be size-only.
- Every caption-sized step must be in the instrument's own `_CAPTION_VARIATIONS`.
- Every variation reference must exist and fit its node's class: 100+ in scenes, 60+ in scripts, 30+ resolved to a class.
- A ratchet of 2 on BBCode `[font_size=` sizes.

**Proof:** the full IQ-10 set at 1600×900 and scale 1.0, shot before and after.
- **140 of 142 frames are pixel-identical,** with **0 text-record differences** (path, class, text, size, em).
- **The other two are the main menu,** whose files were not touched. Its painting's Ken Burns drift is timing.
- **Two flips:** `test_uxr1b_settings_additions.py` and `test_sf7_s8_the_screen_says.py` now read the 18 / 16 / 14 and the 17s off the theme; the CX-7 docstring is re-seated.

*Part 5, scroll where unbounded.* `tests/test_uxr2_scroll_where_unbounded.py` has three arms:
- **Scene arm.** Every `fit_content` RichTextLabel must have a ScrollContainer somewhere in its whole ancestor chain. 13 such labels; 12 resolve, and the tutor body is allowlisted.
- **Script arm.** Every code-built one must resolve through its parents to a scroll. 12 labels, 9 resolved: the wizard's 8 and the log's rows.
- **Toggle arm.** A label switched to `fit_content` must switch back to a bounded scroll.

Four entries stand outside, each with a proof the test checks:

| Entry | Why it may stand outside a scroll |
|---|---|
| The tutor body | It bounds itself |
| The rail's detail body | It bounds itself |
| The terminal's suggestion row | It is count-capped |
| The diorama verdict | It is free-positioned (UXR-X9) |

Floorless ScrollContainers are a ratchet at 8. The census was shown to fail on a synthetic case for each arm.

**The one real fix.** The rail's detail body, unbounded payload text in a panel with no maximum height, now fits the room below the panel and scrolls past it. It uses `Utils.bound_rich_body`, the tutor card's toggle as one helper, and refits when the viewport changes.

**The two plan incidents, corrected.** IGR-F was a floorless scroll. SF7-X17 was an engine-API trim.

`tests/_godot_scenes.py` is now the one scene parser: the clamp pins' helpers moved there verbatim, `test_ui_visual_foundation.py` re-imports them under its old names, and the full-tree parser was added.

**Slice C — the grips and the refit (parts 1 + 3).**

*The grip.* `scripts/resize_grip.gd` (`class_name ResizeGrip`) is the command window's grip made shared, with three ways to host it:
- `make()` gives the look alone. The command window keeps its own fixed-corner geometry in `main.gd`, every pinned line kept.
- `attach_centered(panel, name)` serves a clamped screen.
- `attach_edge(panel, name, corner)` serves an edge-anchored HUD panel (Slice D's war-status panel).

How it behaves:
- It is the panel's last sibling and accepts every left-button event, so a press never reaches the close-on-click overlay.
- A drag grows the panel about its centre. A click that does not move commits nothing; this was UXR-X13 on the command window. A double-click restores the authored size.
- It joins the `resize_grips` group, which Reset layout calls.

*The store.* `ui_settings.gd` holds `PANEL_LIMITS` (terminal, war status, the six screens), `has / get / set / clear_panel_size` and `clear_all_panel_sizes`, in logical px. `[terminal] width/height` is byte-identical on disk; the terminal functions are one-line wrappers. Reset layout clears every panel.

*The clamp.* `clamp_centered_panel` reads a `clamp_user_size` meta in place of the authored rect, larger or smaller. It is read after the `design_size` cache and before the `clamp_ceiling_override` and the viewport caps. The guard and the call string are unchanged, so the player's size is still fitted to any viewport, display-only.

*The six screens* are clamped and gripped: the ledger, the Generals, the dispatch, the log, the Gazette and the Diplomatic Ledger. Each calls `ResizeGrip.attach_centered($PanelContainer, "<key>")` in `_ready`. The Generals filigree now rides inside its panel (UXR-X11).

*The one live-refit road* (UXR-X10):
- `main._on_root_resized` → `DialogManager.refit_visible()` + `top_bar.refit_active_screen()` + the sizing card.
- Each step runs `Utils.refit_surface`, which takes a surface's own `refit()` first; the diorama, the interrupt and petition popups gained one.
- The main menu refits on `resized`, and the war-status panel on `size_changed`.
- The sizing card lost a width floor that defeated its clamp (UXR-X12).

*The census.* `tests/test_uxr2_layout_law.py` puts every top-level Control of every CanvasLayer scene (all 34, not only the 101–122 band) in one class: ANCHORED-FULL, CLAMPED (reached by the refit road), CLAMPED+GRIPPED (every layer-50 screen, with distinct keys `PANEL_LIMITS` knows), FITTED (a named fitter reached by `size_changed` or `refit()`), CHROME, or ALLOWLISTED.
- **The allowlist** is a ratchet of 2: the war-detail popup and the rail slot, both owned by Slice D.
- **Code-built surfaces** carry checked proofs.
- **All nine violation codes** are each shown able to fail. Run on HEAD's Generals scene, the census flags both filigree corners.
- **Mechanics pins:** the road, the meta's order in the clamp, the store, a click is not a resize, Reset layout reaching every grip.

*The driven proof — "the screens resize and remember".* `tests/test_uxr2_grips_driven.py` runs `tools/uxr2_grip_harness.gd`: the real `main.tscn` behind an API stub, in a real 1600×900 window parked past the desktop (a headless root viewport is 64×64, where nothing can move), with `UiSettings` in memory and `_persist` false. For each of the six screens it shows:
- the grip sits on the corner;
- a drag of (+80, −60) gives +160 / −120 about the centre, and the screen stays open;
- the size is stored and returns on the next open;
- a double-click restores the authored size and forgets the stored one;
- a click stores nothing.

Then a ledger grown to 1080 px is refit inside the 1066-px viewport of scale 1.5, and Reset layout forgets every size: **33 pins**.

**The Slice C review** was an adversarial fleet over the committed diff: four lenses (GDScript runtime, player behaviour, persistence and harness safety, the census's soundness), with two refuters per finding. 16 findings; 13 survived; deduplicated, they are **nine defects, all fixed in the review commit:**
- **UXR-X14 (P2).** The grip harness reached the player's live 8005 backend through the top bar's real client.
- **UXR-X15 (P2).** The scene parser dropped any node with `groups=[...]` in its header.
- **UXR-X13, extended.** A jittered click still froze the command window's size. It now has the shared grip's threshold and grab offset.
- **UXR-X16.** The census was lenient: CHROME, commented calls, three codes never shown failing.
- **UXR-X17.** Three smaller truths: the tooltip wording, a 3600-px store ceiling that stopped a drag on the 5120 panel, and a "remembers" pin satisfied by the node's meta instead of the store.

Three findings were refuted with reasons.

**Slice D — the anchors (part 2).** `utils.gd` gained the ANCHORED half's helpers:
- **`TOP_BAR_HEIGHT` (36) and `HUD_MARGIN` (8).** These are the one source for the five numbers that had each re-typed the bar's height: the command window's reserve 36, the region panel's dock 48, the tutor card's top 44, the rail slot's top 42 and the centre clamp's 88. The census pins every authored number to its derivation.
- **`fraction_px(view, frac, min, max, reserve)`.** A viewport fraction, never wider than the room the viewport leaves.
- **`clamp_anchored_panel(panel)`.** The edge-anchored twin of the centre clamp, whose pinned guard stays. It caps a point axis to the band under the top bar, keeping its grow edge, relaxes the descendant minimums, and slides the rect back inside the band.

The HUD family is anchored:

| Surface | Before | Now |
|---|---|---|
| Rail slot | A bare 360 | `fraction_px(vw, .12, 360, 520)`, on `size_changed`; the rail fills it |
| War HUD (UXR-X18) | A hidden edge band | A grip and a fraction (above) |
| Region panel | A fixed 344 | `fraction_px(vw, .15, 344, 560)` |
| Tutor card (UXR-X19) | Over the rail | Its pinned width rule, capped to the screen, beside or below the rail |
| War-detail popup (UXR-X20) | A fixed 330×440 rect | A fraction docked beside the war HUD's live edge, under `clamp_anchored_panel` |

The census's allowlist is **empty** (ratchet 0), and every HUD surface is FITTED by a named function its `size_changed` or `refit()` reaches. The driven harness gained the war HUD's grip: **36 pins**.

The frames found one more thing: the war-detail popup's button row is an HFlowContainer whose wrapped height is known only after layout. The popup therefore re-fits once more a frame later, and `clamp_anchored_panel` places it by its real minimum size. At 800×450 the header had sat under the top bar; at 533×300 the header's width pushed it off the left edge.

**Slice E — the landing re-shoot.** The whole client was re-shot from the committed tree (`7ce88863`) at the five physical resolutions with the derived scale: **142 surfaces × 5 = 710 readings, 7,555 text rows: RED 0 / P1 0**. The record is `readability_after_all_2026_10_12.json`. On Oct 9 it read 137 surfaces, RED 32 / P1 92, every flag on UXR-X5 / X6. The map's own furniture is its own tier: 336 small rows, unchanged, which are UXR-X4's (S9b).
- **The named set**, read off the same shoot: 11 surfaces, RED 0 / P1 0 (`readability_after_named_2026_10_12.json`).
- **The run:** 0 SCRIPT ERROR, 0 clipped text, 0 buttons off-screen.
- **`tests/test_uxr0_readability.py`:** the ratchet went to 0 / 0. Its routed-families exemption retired into `test_no_flagged_reading_anywhere`, plus a pin that the five boards UXR-2 added are shot at every resolution.
- **Frames at 5120×1440:** `UXR2_AFTER_WAR_ROOM_TUTORIAL_*`, `UXR2_AFTER_LEDGER_GRIPPED_*` and `UXR2_DIORAMA_FOUR_RANKS_BEFORE_AFTER_*` in `docs/audits/uxr0/`.

**The done-when is MET on the instrument:**
- The census reads every surface as anchored or clamped-and-gripped, with an empty allowlist.
- The six screens and the war HUD resize and remember (driven).
- UXR-0 reads 0 RED, and 0 P1, on every surface at every resolution.

⚠ The user's half — the screens feel right in the hand at 5120×1440 — is UXR-4's eyes. **S9b is next** (UXR-D1 Text size, D2 High contrast, D3 HUD Centred + ⌂ Fit Europe, X4 the map follows the scale).

### Landing record — S9b, UXR-2's adjustability extras (Pre-Deploy S9b, October 12, 2026)

> Built in slices on master: A Text size → B HUD width + ⌂ → C the map's furniture → D High contrast. Routing `PRE_DEPLOY_PLAN.md` §2 row S9b; rules `SYSTEMS_REFERENCE.md` §112; rows `DESIGN_REFINEMENT.md` UXR-D1 … D3, `BUG_FIXES.md` §UXR-2's extras.

**The rulings of the session (the user, at the plan):**
1. **⌂ Fit Europe** goes in a `[− ⌂ +]` map-control cluster at the bottom-centre of the HUD band. There was no on-screen zoom control to sit beside; zoom and recentre were keys only.
2. **UXR-X4** is met with a screen-space floor: the map's furniture holds a minimum on-screen size as the view zooms out, as the province names already do.
3. **Text size** runs from 100 % to 175 %.

**Slice A — UXR-D1, Text size.**

*What it is.* Settings → INTERFACE → *Text size* (100–175 %, 5 % steps, `display/text_size`) scales the project theme's type sizes alone: the default 16, the Label / Button / RichTextLabel / LineEdit sizes and the whole ladder from Caption 14 to DisplayTitleLarge 30. `Utils.apply_text_size` captures the authored sizes once and writes `round(authored × factor)` through one `Theme.merge_with`. At the factor already applied it does nothing, so 100 % at boot changes nothing. The Interface Scale, the panel rects, the eighteen named raw overrides and the two BBCode titles do not move.
- The slider is live on every step and persisted when the drag ends. Its `text_size_changed` puts every open surface on the live-refit road.
- Both boots apply the stored size. Reset layout returns it to 100 %.

*Found while building (the 150 % frames were the first to grow a one-line row past its box):*
- **UXR-X22.** The top bar is one line of buttons, 36 px at 100 % and 45 px at 150 %, and five numbers cleared its authored 36. The rail slot sat 3 px under it. At 175 % the full-text bar ran off a 1920-px screen, because compact mode switched at a fixed 1,180 px.
  - Now the bar publishes its drawn height (`Utils.top_bar_growth()`); the rail, the tutor card, the region dock, the command window's reserve and both clamps clear it.
  - Compact mode's threshold scales with the text.
- **UXR-X21.** The command window's stats line was one 513-px HBox line (726 px at 150 %). It floored the window above the size it was asked for: 572 against 537 at 1080p even at 100 %, and 760 at 150 %. It wraps now (an `HFlowContainer`). The wrap exposed the command line's own default floor of 4 em (about 100 px at 150 % on 1080p), so the line now holds 8 em. The window's width floor is its input row: 413 px at 100 %, 569 at 150 %.
- **UXR-X24 (filed, owner Slice B).** The war room's boot sometimes leaves keyboard focus on the output rather than the command line: 1 capture in 3, present at HEAD before any S9b change. The capture record now carries the focus owner.

*The reading* (the done-when's test): the five named surfaces were shot as a pair at Interface Scale 1.0 and the five resolutions, once at 100 % and once at 150 %, and `tools/uxr2b_text_size_check.py` read the pair (`docs/audits/uxr0/readability_text150_named_2026_10_12.json`, pinned by `tests/test_uxr2b_text_size.py`):

| | Readings | Text rows | RED / P1 | Scaled exactly | Clipped / off-screen |
|---|---|---|---|---|---|
| 150 % | 35 | 550 | **0 / 0** | **550 of 550** | 0 / 0 |
| 175 % (the slider's top) | 35 | 547 | 0 / 0 | 528 of 528 paired | 0 / 0 |

- **The panels.** The dispatch and the Generals screen, the clamped screens, keep their rects at both sizes. Only surfaces whose size *is* their text move, each by its rule:
  - the top bar's strip grows by its line (36 → 45 px), and the rail slot and the tutor card move down by exactly that;
  - the tutor card and the war HUD shrink-wrap taller cards, their widths and anchored edges fixed;
  - the command window keeps its width wherever its input row fits (every screen from 2560 up). On a 1080p screen it widens to that row's floor, 538 → 617 px (the command line holds 8 em), and it grows 45 px taller because every line is taller.
- **At 175 % on a 1080p screen** three content floors widen a little. The command window (its input row), the war HUD (230 → 265) and the tutor card (422 → 470) each widen to hold one unbreakable line; nothing clips or leaves the screen.
- The 175 % record is `readability_text175_named_2026_10_12.json`.
- Frame: `docs/audits/uxr0/UXR2B_TEXT_SIZE_100_150_WAR_ROOM_TUTORIAL_5120x1440_2026_10_12.jpg` (the user's panel, 100 % above 150 %).

*Driven* (`TestTheTextSizeSlider`, on the live war room): a click on the slider re-themes the LineEdit 16 → 24, the output 16 → 24 and a Caption 14 → 21, and stores 1.5. Reset layout from the panel returns 16 / 14 and 1.0. The command window is drawn at its footprint or at its input row's floor.

*Regression:* the full IQ-10 set at 1600×900 × {1.0, 2.0} at Text size 100 % was shot against the pristine HEAD worktree (`c8e65997`). **274 of 284 frames are pixel-identical.** The war room's frames were re-shot after the command line's 8-em floor; the floor touches only `main.tscn`'s war room. The other ten differ as follows:
- **The six war-room frames.** The stats line wraps and the command window sits at the width it was asked for. Every text is identical in content and size; only positions move.
- **The main menu's four.** Two are its painting's Ken Burns drift. The other two are Settings, whose new Text size row and Reset-layout hint are the run's **only** text-record differences.

The run had 0 SCRIPT ERROR, 0 clipped text and 0 buttons off-screen, and the war-room frames end with focus on the command line.

*Open for the review pause:* the command window's header carries a control labelled **"Text Size"** (UI-2c, July) that steps the *Interface Scale*. Settings now also has a real *Text size*. One of the two needs another name; the user rules which (UXR-X23).

**Slice B — UXR-D3, HUD width: Full · Centred, and the `[− ⌂ +]` map controls.**

*What it is.* Settings → DISPLAY → *HUD width* (`display/hud_width`, default Full; Reset layout returns Full). `Utils.hud_band(view)` is the HUD's band: the viewport at Full, and 2560 logical px about the centre at Centred (on a viewport wider than that and its margins). Every HUD surface measures its edge and its fraction from the band, each through its existing fitter, so the layout-law census is unchanged and green:
- the command window and its restore button (`_terminal_left` / `_hud_room`);
- the top bar's two clusters (two code-built pads at the ends of the bar's layout; the strip stays full-bleed; compact mode compares the band);
- the rail slot and the war HUD;
- the region panel and the tutor card;
- the war-detail popup (it docks to the war HUD).

*The map controls* (the user's ruling: the band's bottom-centre; the map had no on-screen zoom). Three chips, − ⌂ +, that never take the command line's focus. ⌂ is `fit_europe()`: the boot's contain-fit zoom and the centre, where Home only re-centres. The cluster slides right of the command window when it reaches past the centre, and stacks above the war HUD's corner when there is no room between them (an 800-px logical screen). The map's labels dodge it.

*Found and fixed:*
- **UXR-X25.** A zoom still easing in (a 0.2-s tween) landed after Home's re-centre and after ⌂, and undid them. Found by the driven harness: + three times, then ⌂ mid-ease, read 0.97 against a fit of 0.90. Both now kill the tween first.
- **UXR-X23** (the user's ruling). The header's + / − read **"Scale"**: they step the Interface Scale. Settings' Text size grows the words alone.
- **UXR-X24, a harness defect, not a game defect.** The failing boot's focus left the command line at frame 70 for the next control in tab order, a Tab press: the capture window is foreground when it opens, so the player's own keystrokes reached it. The harness now ignores OS input (`gui_disable_input`) and records the focus owner, every focus change and any stray input.

*The test* (the done-when). `tools/uxr2_grip_harness.gd` in band mode boots the real war room in a 5120×1440 window at scale 1.4, the panel's derived scale (`tests/test_uxr2b_hud_band.py`).
- **Centred:** the band is 548–3108 of a 3657-px viewport. The command window, its restore button, both clusters, the rail slot, the war HUD, the region panel and the map controls all lie inside it; the strip spans the screen; the chips sit at the band's bottom-centre.
- **Full:** every edge is where S9 left it.
- **⌂ pressed mid-zoom** lands on the fit (0.899).
- The layout-law census still passes.

*Regression:* the full IQ-10 set at 1600×900 × {1.0, 2.0} at Full against Slice A's frames: **274 of 284 pixel-identical.** The ten others are the six war-room frames (the cluster, "Scale" and the map's labels dodging the chips), Settings' four (the HUD width row and the hints; two of them are the main menu's Ken Burns drift). The run had 0 SCRIPT ERROR, 0 clipped and 0 off-screen, and every war-room frame ends with focus on the command line and **0 stray input**. The Centred war room at all five resolutions shows the same.

*Frame:* `docs/audits/uxr0/UXR2B_HUD_FULL_CENTRED_WAR_ROOM_TUTORIAL_5120x1440_2026_10_12.jpg` (the user's panel at 1.4, Full above Centred).

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
