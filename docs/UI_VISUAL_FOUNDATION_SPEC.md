# UI Visual Foundation Sweep — Spec

> **Status:** ▶ IN PROGRESS. **Session U1 (UI-0 + UI-1) ✅ LANDED July 12, 2026** — font stack +
> `ui/main_theme.tres` + typed Button styleboxes registered project-wide, boot-smoke 0 `SCRIPT ERROR`,
> `tests/test_ui_visual_foundation.py` (15) green. **Session U2 Part 1 ("UI Scale & the Expandable
> Command Window") ✅ LANDED July 12, 2026** — the command window is now user-resizable (corner
> drag-grip, double-click reset) + text-scalable (A− / A+), a global Interface Scale slider
> (`content_scale_factor`) lives in the pause-menu Settings, all persisted via the new
> `scripts/ui_settings.gd` (`user://ui_settings.cfg`); the DEF-13 fixed-HUD baseline pin is RETIRED
> for a mechanism pin; boot-smoke 0 `SCRIPT ERROR`; `tests/test_ui_scale_expandable_terminal.py` (12)
> green. **Session U2 Part 2 ("Colour Centralization + Theme Sizes + Native Map") ✅ LANDED July 12,
> 2026** — recurring navy/gold/state Colors centralized into a `Utils.UI_*` palette and the HUD/ledger/
> popup chrome migrated to it; per-type theme font sizes (`Label`/`LineEdit`/`RichTextLabel`) declared;
> the map SubViewport now renders at **physical resolution** under `content_scale_factor` (displayed
> through a `STRETCH_SCALE` `TextureRect`, the stretch-drawing `SubViewportContainer` removed, pointer/
> pan/zoom conversions scaled by `_viewport_pixel_scale()`); boot-smoke 0 `SCRIPT ERROR` (import +
> game-scene + `europe_map_smoke` runtime); `tests/test_ui2_part2_color_and_map.py` (10) green. **The
> only open item is the user's ≥2560 visual sign-off on map crispness** (the spec's visual gate, §8
> Part 2). **Session U2c ("Global Text Size + pop-up-wide scaling") ✅ LANDED July 12, 2026** — the
> user-requested follow-on: the command window's A− / A+ pair became a labelled **"Text Size"**
> control (a "Text Size" label beside a stacked **+ / −**), and it now drives the **global**
> `content_scale_factor` (the same value the pause-menu slider writes) instead of the retired
> terminal-only font scale — so one control enlarges the command window **and every CanvasLayer
> pop-up / ledger** (verified: the viewport final-transform applies to CanvasLayers), map still crisp;
> the pause slider re-syncs on open; `tests/test_ui2c_global_text_size.py` (5) +
> `test_ui_scale_expandable_terminal.py` retargeted + the DEF-13 mechanism pin updated; boot-smoke 0
> `SCRIPT ERROR`. Its 7-agent review confirmed one stale-copy fix (pause-menu hint) and filed one
> **owned pre-existing** follow-up: **UI-2d — modal viewport-safety** (fixed-size decision modals can
> overflow a short viewport at scale ≈ 2.0; not on the ≥2560 display; contract + DoD in
> `docs/BUG_FIXES.md` §UI-2d). Design proposal + all third-party assets gathered and
> license-verified. **The War-Table Pieces style gate is CLOSED (July 12, 2026) — tin flats on a round
> base (§7), references gathered.** The sweep is segmented into build sessions **U1–U5** in **§8
> (Session Segmentation Ledger)** — U1 + U2 (Parts 1, 2, 2c) + **U3 (texture / icon / portrait polish)
> ✅ LANDED July 12, 2026** + **U4 (War-Table Pieces ART) ✅ LANDED July 12, 2026** (24 tin-flat
> sprites in `assets/ui/pieces/`, 2D pipeline `tools/gen_war_table_pieces.py` — Blender not installed,
> conscious §8-U4 deviation) + **U5 (War-Table Pieces Godot placement) ✅ LANDED July 13, 2026** all
> done — **the sweep is U1–U5 COMPLETE** (pending the standing U2/U3/U5 visual sign-offs).
> **Session U5 (War-Table Pieces CODE) ✅ LANDED July 13, 2026** — `scenes/war_table_piece.gd`
> (`class_name WarTablePiece`: 4 stacked ground-anchored `Sprite2D` layers, faction `modulate` on the
> coat only + a dark-hue value floor) placed by a persistent y-sorted `pieces_layer` under `world_layer`
> and a DIFF updater `_update_war_table_pieces()` (retire/snap-recenter/tween-real-move/spawn, facing-flip
> by heading), keyed to a NEW display-only backend `arm` field (fog-safe — enemies carry arm only at FULL
> visibility) so enemy corps no longer all draw as infantry; bitmap-mode gated (legacy fixture keeps its
> square icons); the piece ART re-touched (cavalry redrawn, infantry/artillery upscaled, the occluded
> contact shadow made visible). Boot-smoke 0 `SCRIPT ERROR` (probe-confirmed 3 pieces keyed to
> infantry/cavalry/artillery); `test_ui_visual_foundation.py` +3, `test_fog_of_war.py::TestMarshalArmField`
> +4. **Also this session (UI bar-fill fixes the user flagged):** the war-score tug-of-war bar
> (`war_status_panel.gd` + `war_detail_popup.gd`) switched from fixed `bar_width` inner coords to anchor
> fractions so the centre line + fills track a `SIZE_EXPAND_FILL` container (they had bunched into the
> left ~80px of a wider bar); the marshal-card skill `█░` bars re-ordered bar-first so the varying label
> width no longer staircases the bar column.
> **Session U3 ("Texture / Icon / Portrait Polish") ✅ LANDED July 12, 2026** — the 37 PD marshal
> portraits render as `[img]` thumbnails on the Generals cards + Commission bench (Abdurrahman → gold
> monogram); the curated icon sets, preprocessed to white silhouettes, are tinted gold onto the close-X
> of all 5 command screens, the 5 top-bar nav buttons, the terminal resize-grip, and the Generals unit/
> laurel/commission headers (game-icons CC-BY credit shipped in the pause-menu Settings); gold filigree
> corners frame the Generals panel; a navy-tinted leather `StyleBoxTexture` grains the theme
> `PanelContainer` (terminal + popups). **Deviation (GR9-documented, §8 U3):** the crisp `StyleBoxFlat`
> gold borders on the big command screens were KEPT (+ filigree) rather than replaced by muddy
> full-texture 9-slice frames — the sole frame asset is a dark brown that `modulate` cannot gild without
> degrading legibility. Boot-smoke 0 `SCRIPT ERROR`; parse-harness report regenerated;
> `tests/test_ui_visual_foundation.py` (+11 UI-3 assertions); suite 13,022 passed / 3 skipped. **Open:
> user visual sign-off** on leather subtlety / top-bar icon size / filigree placement / portrait aspect
> (§8 U3, matches the U2 map-crispness gate).
> **Session U6 ("Interaction & Heraldry Sweep") ✅ LANDED July 16, 2026** — the clickability slice
> (user directive: vassal buttons + UI review + clickable items everywhere): a **VASSALS tab** in the
> diplomatic ledger (per-vassal cards — flag, loyalty bar, honest next-turn forecast via the NEW shared
> `vassal.forecast_vassal_loyalty` helper, tribute, VS-4 contribution tier, garrison/subsidy levers —
> plus honest-availability action chips Invest / Loosen / Tighten / Cede / Release riding the wizard's
> own `get_available_diplomatic_actions` rows and typed-command echoes); the **Region Action Panel**
> (`region_panel.gd/.tscn`, layer 26) — the map's dead `region_clicked` seam finally connected: click a
> province for fog-honest info + context chips (recruit / build depot / negotiate / per-marshal
> Fortify-Drill); **heraldry wired** (16 PD flags → ledger rows, wizard nation buttons + header, war HUD
> cards + armistice rows, war-detail header); **notification rail glyphs** (phosphor SVGs replace the
> 3-letter codes, legacy fallback kept); **top-bar gear button** (pause menu was ESC-only); **Generals
> card order chips** (Fortify/Unfortify/Drill) + a Talleyrand-tab **[Assess the Situation]** chip
> (W6-9); shared `Utils.bb_icon/bb_button_chip/nation_flag_path` helpers + `_format_number` de-duped
> (4 copies → `Utils.format_number`); the U5 clustering residual CLOSED (`_marshal_slot_offset_2d`
> two-rank spread for 3+ co-located standees, shared by pieces/labels/hitboxes). A 23-agent 5-lens
> find→verify review confirmed 15 findings (9 distinct) — **ALL FIXED**: subsidy term added to the
> loyalty forecast + wizard/ledger trend unified on the shared helper; chip terms now render
> backend-derived grip-effective gains (never a hardcoded +10 the executor blunts); the "scenario"-path
> boot vassals no longer mislabeled as conquests; a shared in-flight latch kills chip double-sends;
> the gear honors the ESC pause-never-over-a-screen invariant; objection resolutions refresh open
> screens; region-panel depot check fixed to the canonical `supply_depot` key; parse-harness report
> regenerated. Boot-smoke 0 `SCRIPT ERROR` (×2); `tests/test_ui6_interaction_sweep.py` (44); suite
> 13,521 / 3. ~~Open: user visual sign-off~~ **✅ SIGN-OFF RECORDED July 16, 2026** (user-directed
> self-served pass — screenshot-verified in-game at the native ≥2560 display; record in STATUS.md's
> ⚔️ July-16 section: region panel + vassal cards w/ flags + nations-tab flags + Generals ladder/cards +
> gear invariant + two-rank pieces + map crispness all PASS; same session redrew Hanover/Ottoman/Saxony
> for 1805 date accuracy). The U2/U3/U5 sibling gates closed in the same pass.
> **Session UI ("The Gilt Frame, the War Table and the Dressed Page") ✅ LANDED November 11, 2026**
> — one drawn window frame for every screen, the title face, the primary button, the map a sheet on
> a leather desk, the books as cards; the record is §9.
> **Session UI-2 ("The Imperial Desk") ✅ LANDED November 12, 2026** — figures before prose (strips,
> tables, meters, badges), 36 stat glyphs, one button language, the 16:9 HUD on 32:9, popups that fit;
> blind readers 7 / 7 / 7 before and after (mean 6.77 → 6.93) — the record and what holds it at 7 are §10.
> **Owner row:** ROADMAP §Current Phase Queue row **UI** (this spec is authoritative).
> **Supersedes/absorbs:** DEF-13 "UI-Scale Mini-Pass" (folds in as phase **UI-2**;
> its baseline pin `test_map_slice8_balance.py::test_def13_fixed_hud_baseline_pins` is honored).
> **Proposal artifact:** the "Project Sovereign — Visual Foundation" artifact (palette, button
> mockups, font pairing, phased plan) generated July 11, 2026.
> **Assets on disk:** `godot-client/project-sovereign/assets/` (git-ignored); tracked license
> manifest at repo root `THIRD_PARTY_LICENSES.md`.

---

## 0. Why (the problem)

The UI has a coherent art direction — dark navy + imperial gold, engraved-caps titles — but
no shared machinery to express it. Three structural gaps compound:

1. **No custom font.** Zero `.ttf`/`.otf` shipped; `project.godot` sets no `gui/theme/custom`.
   Every title and dispatch renders in Godot's default sans — the biggest "looks generic" factor.
2. **No central Theme.** No `.theme`/`.tres` resource; **299 hardcoded `StyleBoxFlat` /
   `theme_override_*` occurrences across 51 files**. Restyling means touching dozens of scenes.
3. **Unstyled buttons.** Controls override only `font_color` (e.g. `top_bar.tscn`); no
   background/hover/pressed StyleBox — buttons read as flat grey OS widgets.

The palette in `scripts/utils.gd` (`COLOR_GOLD` etc., `NATION_COLORS`) is good — the problem is
that nothing shared consumes it. The fix is one `main_theme.tres` registered project-wide, a
proper font stack, and typed Button/Panel styleboxes — which also becomes the clean single-source
hook the DEF-13 scale slider needs.

---

## 1. Scope + phase order

Front-loaded for payoff. **Land UI-1 first, then pause for review** (slice-review cadence).

| Slice | Title | Contents | Risk |
|-------|-------|----------|------|
| **UI-0** | Asset landing prep | Confirm the git-ignored asset tree is complete; decide git-tracking policy (force-add vs LFS vs leave-local); set `.svg`/font `.import` scale so icons/portraits stay crisp; keep `THIRD_PARTY_LICENSES.md` current. | none (bookkeeping) |
| **UI-1** | Font + Theme + Buttons | Install the Cinzel / EB Garamond / Source Sans 3 stack; author `ui/main_theme.tres` (default font, `HeadingLabel` variation, typed Button styleboxes, PanelContainer panel); register via `gui/theme/custom`. Fixes gaps #1 and #3 with almost no `.gd` logic. | **low** |
| **UI-2** | Color centralization + UI scale (**folds DEF-13**) | Migrate inline `Color()` duplicates to `Utils`/theme colors (existing `test_gdscript_color_centralization.py` guards this); wire `content_scale_factor` slider + `canvas_items`/`expand` stretch with the **map SubViewport kept native** (per DEF-13's dated decision); per-type font sizes. Retires the 299-override sprawl. | medium |
| **UI-3** | Texture / border / icon / portrait polish | Parchment + leather panel fills; convert war-room / dispatch / ledger panels to `StyleBoxTexture` 9-slice frames; filigree corners on marshal cards; wire the curated icon set into HUD/buttons; wire the 37 marshal **portraits** into the Generals screen + character-sheet cards. Cosmetic layering on the UI-1 theme. | cosmetic |

**Standing rule (honored every slice):** after any `.gd`/`.tscn` touch, boot the engine once and
grep the output for `SCRIPT ERROR` before landing (the W6 `headline` shadow that killed the client
is why this rule exists).

---

## 2. Blessed asset inventory (on disk, license-verified)

All under `godot-client/project-sovereign/assets/` (git-ignored). Full license terms +
attribution obligations: repo-root `THIRD_PARTY_LICENSES.md`.

### Fonts — `assets/fonts/` (13 families, SIL OFL 1.1)
Display: **Cinzel** (default), Marcellus SC, Playfair Display, Cormorant Garamond, IM Fell English,
UnifrakturMaguntia. Body/UI: **EB Garamond** + **Source Sans 3** (defaults), Source Serif 4,
Spectral, Libre Caslon Text, Alegreya Sans, Fira Sans. Each ships its `OFL.txt`.

### Textures — `assets/textures/` (CC0)
ambientCG Paper 001 / Paper 005 / Leather 026; Poly Haven Fabric Leather 01; Leschge Paper Textures
Seamless; cron Old Parchment (+alpha). Vignette generated in-engine (`GradientTexture2D`, radial).

### Borders / 9-patch — `assets/ui/borders/` (CC0 except Lamoot)
Kenney Fantasy UI Borders (default), Kenney UI Pack, Buch Golden UI, Cethiel Card Template,
Buttons and Frame. **RPG GUI Construction Kit (Lamoot) — CC-BY 3.0, attribution required.**

### Icons — `assets/ui/icons/` (curated two-set system, July 12, 2026)
- **`phosphor/`** — Phosphor Regular, 51 curated SVGs (MIT). Neutral UI chrome: menus, carets,
  arrows, gear/search/info/warning, save/load, tabs, notifications, scales, chart, plus semantic
  duals (sword/shield/crown/coins/horse/medal).
- **`game-icons/`** — Game-icons.net, 24 curated SVGs (**CC-BY 3.0, visible credit required**).
  Thematic core: units, combat actions, economy, diplomacy. Recolor gold via `modulate` (strip the
  512×512 black bg `<path>` first). `_packs/game-icons-net.zip` retained as the master pool.
- **Dropped** (first-pass grab, deleted): Lucide, Tabler, Iconoir, Feather, Font Awesome Free.

### Portraits — `assets/portraits/` (37, Public-Domain PD-art, Wikimedia)
Named by internal marshal key (`Ney.jpg`, `Wellesley.jpg` = Wellington, `Frederick.jpg` =
Frederick VI of Denmark, `Bernadotte.png`). Not present: **Abdurrahman** (no confident PD portrait;
left unillustrated by design — do not substitute a wrong likeness). Low-res-but-usable:
Armfelt (294×390), Hiller / Mack (~315×425) — optional higher-res swaps.

### Audio — `assets/audio/ui/` (CC0)
Kenney Interface Sounds + RPG Audio, an OpenGameArt CC0 cannon pack, and CC0 parchment open/close
WAVs. Covers click/hover/confirm/error, coins, cloth, distant cannon, panel open/close. Deferred
gaps (non-blocking): drum/fife turn-start sting, dedicated quill-scratch, dedicated wax-seal stamp.

### Heraldry — `assets/ui/heraldry/` (16 PD flags)
Period national flags for the roster, named `<Nation>.svg` (France, Britain 1801, Austria, Russia,
Prussia, Spain, Naples, Bavaria, Sweden, Denmark, Ottoman, Portugal, Holland, Papal States,
Sardinia, Saxony). Wire into the Diplomatic Ledger / war panels.

### Ornaments & map decor — `assets/ui/ornaments/`, `assets/ui/decor/`, `assets/textures/decor/` (CC0/PD)
Flourishes, laurel wreaths (incl. a golden hero wreath — pairs with the Crowned-with-Glory beat),
corner filigree, fleurons, a wax-seal graphic; an antique compass rose, a Cassini cartouche, an
ornamental frame, antique parchment, Kenney smoke/dust particle PNGs (for battle/movement feedback).

---

## 3. How to build UI-1 (Godot 4.4 — the load-bearing steps)

Target: fonts `assets/fonts/`, theme `ui/main_theme.tres`, pull navy/gold from `Utils` (never inline `Color()`).

1. **Install fonts** — drop `.ttf` into `assets/fonts/`; Godot auto-imports a `FontFile` + `.import`
   sidecar (**commit the `.import`**). Reference from the Theme, not scripts.
2. **Theme + register** — New Resource → Theme → `res://ui/main_theme.tres`; set `default_font`
   (EB Garamond) + `default_font_size` (16). Register: Project Settings → GUI → Theme → Custom
   (writes `[gui] theme/custom` — read at startup, restart to apply).
3. **Button styleboxes** — author `normal`/`hover`/`pressed`/`disabled` on the theme so
   `popup_base.gd::_apply_standard_theme()` and every `*_popup.gd` inherit one skin. Gold border,
   dark navy fill, 2px bottom border, corner radius 3.
4. **`HeadingLabel` variation** — `FontVariation` on Cinzel with a dark-navy outline; titles set
   `theme_type_variation = "HeadingLabel"` instead of per-node overrides.
5. **UI-2 scale** — `get_window().content_scale_factor = v` on a slider (0.75–2.0) over a
   `canvas_items`/`expand` baseline; keep `map_viewport.size` native per DEF-13.

---

## 4. Completion definition

- **UI-1 done when:** every screen inherits `main_theme.tres` via `gui/theme/custom`; no title/label
  renders in the default sans; Buttons show visible hover + pressed + disabled states; engine boots
  with **0 `SCRIPT ERROR`**; a font/theme-presence test passes (§5).
- **UI-2 done when:** the terminal, war panel, top bar, and centered screens render readable-
  proportional at ≥2560-wide with `map_viewport.size` still native (DEF-13 completion criterion);
  inline-`Color()` count materially reduced with `test_gdscript_color_centralization.py` green;
  the DEF-13 baseline pin is replaced by a chosen-mechanism pin.
- **UI-3 done when:** panels use the parchment/leather fills + 9-slice frames; the curated icons
  render on their target buttons; marshal portraits show on the Generals screen + character-sheet
  cards (portrait-present marshals; Abdurrahman falls back to a monogram/silhouette gracefully).

---

## 5. Tests (behavior, per GR9)

- `tests/test_ui_visual_foundation.py` (NEW):
  - `project.godot` has `gui/theme/custom` set and `ui/main_theme.tres` exists and parses.
  - `main_theme.tres` defines Button styleboxes for `normal`/`hover`/`pressed`/`disabled` and a
    `PanelContainer` `panel`, and a `HeadingLabel` type variation.
  - the expected default font families are present in `assets/fonts/` with their `OFL.txt`.
  - a portrait exists in `assets/portraits/` for every marshal key in `europe_1805.json`
    **except the documented Abdurrahman exception** (guards silent portrait rot).
- Reuse `test_gdscript_color_centralization.py` as the UI-2 drift gate.
- Reuse / replace `test_map_slice8_balance.py::test_def13_fixed_hud_baseline_pins` per DEF-13.
- Engine boot smoke: grep `SCRIPT ERROR` after each slice (manual gate, recorded in STATUS).

---

## 6. Non-goals / boundaries (GR9)

- Not a gameplay change — display only. No executor, serialization, or balance touch (Golden Rule 6).
- Does not re-open the map renderer / DEF-9..DEF-12 (those are closed); UI-2 only adds
  `content_scale_factor` with the map SubViewport untouched.
- Marshal-portrait *wiring into new dialogs* beyond Generals/character-sheet is out of scope for
  UI-3; additional surfaces get their own follow-up row if wanted.
- The CC-BY assets (Game-icons.net, Lamoot) ship only if actually used; the credits file already
  carries their attribution.

---

## 7. War-Table Pieces (UI-3 sub-item) — the 2.5D unit diorama

> **Status:** **style gate CLOSED July 12, 2026 — G1 / G2 / G3 all LOCKED** (user chose
> **tin flats on a round base**). Reference images gathered + license-verified this session
> (below). Art not yet started; owned by session **U4** (art) + **U5** (code) in the §8 ledger.
> **Decision locked (structural, unchanged):** **no camera tilt** → **baked 2.5D pieces on the
> existing 2D map** (additive layer; the mature map / DEF-9..13 stays untouched). Real-time 3D was
> rejected for map pieces — the win is dimensional pieces baked to sprites.
> **Research sources:** tin flats / Zinnfiguren (Plassenburg Zinnfiguren-Museum Kulmbach via
> Wikimedia/Thomas Quine; Louis Liljedahl 30 mm Napoleonic flats; Roscheider Hof; Goslar;
> W. Schweizer slate mould; Kieler & Rick Sanders collector catalogs). The July-12 five-style
> selection board (round-sculpt / Kriegsspiel-block / round-soldier / tin-flat / pin) is the
> historical decision artifact — the tin-flat arm won.

**Goal:** physical "war-table" pieces — one each for **infantry / cavalry / artillery** — that a
marshal pushes across the map, like a Kriegsspiel diorama. Color = side is universal; branch always
needs a second channel.

### Style — LOCKED (gate G1): tin flat on a round base ("the standee")

The piece is a **Zinnfigur tin flat** — an engraved, dead-broadside side-profile figure — standing
in a slot on a **round base disc**. The flat carries the branch **silhouette** (the read the user
chose for its folk-art character); the round base restores the **footprint** channel a bare flat
lacks and gives the **baked contact shadow** a disc to sit on — which cures the "flats fight 2.5D"
objection that had ranked pure flats 4th at the open gate. This is the tabletop
"standee-on-a-round-base" pattern.

- **G1 = tin-flat-on-round-base** — LOCKED (user, July 12, 2026).
- **G2 (production path) = billboard + painted broadside texture.** The "model" is a thin extruded
  blade / alpha-cut quad + a round base disc primitive (both trivial in Blender); the *art* is the
  painted broadside texture, traced from the public-domain Zinnfiguren references below. No 3D
  organic sculpt and no CC0-mesh kitbash is needed (that path was for the round-sculpt style).
- **G3 (recolor) = neutral tint-mask.** Faction color drives a **coat-mass mask** via Godot
  `modulate` (`Utils.NATION_COLORS`); bare pewter/metal and the base stay neutral so the "tin"
  identity survives every faction hue. One render → 20 nations.

### Per-arm spec (flats) — three redundant channels: round-base footprint + broadside silhouette + faction tint

All figures face one consistent direction (Zinnfigur convention = nose-right); a **mirrored L/R
pair** per arm lets a piece face its travel heading.
- **Infantry** — widest round base; a **rank of 2–3 broadside shako figures + a taller colour/eagle
  bearer** breaking the top line → *wide vertical bristle*.
- **Cavalry** — mid round base; a **single horse+rider in dead side-profile, sabre raised** clear of
  the shako → *tall galloping mass*.
- **Artillery** — wide, low round base; a **broadside gun (big spoked wheel + tapering barrel +
  trail spike) + 1–2 crew** in the same plane → *low horizontal wheel*.
- Matched-set rules: identical base-disc height/bevel, identical baked line-shadow, one shared
  locked light, matte toy-enamel, paper-thin edge rim. One piece = one corps. No fine detail at
  64px — strength/facings live in hover/zoom.

### 2.5D render pipeline (flats variant)

1. **Model** — a near-2D blade (a few mm of relief) or an alpha-cut billboard quad, set in a
   diametral slot on a round base disc (3 footprint sizes). Author the broadside texture by tracing
   the PD Zinnfiguren refs + matte enamel; engraved detail = shallow raised **lines**, not sculpted
   volume.
2. **Camera — LOCKED dead-broadside** (90° side-on, orthographic, level with the figure; at most
   ~5–10° top-down only so the base ellipse reads). **Never 3/4** — off-axis collapses a flat to a
   sliver. (This replaces the round-sculpt pipeline's 45° 3/4 rig.)
3. **Light once** — a single low-angle key + soft fill; a thin bright rim on the raised relief
   edges; the paper-thin silhouette edge is the "flat, not mini" tell.
4. **Bake a line-shaped contact shadow** — a narrow dark line-ellipse tight under the feet/wheel,
   feathering to the disc rim (a body-blob shadow reads as a rounded mini and is wrong for a flat).
5. **Render PNG+alpha at 2–3×** — neutral coat **tint-mask** + a **mirrored L/R facing pair** per
   arm; base + metal on neutral channels.
6. **Godot** — `Sprite2D` (flat) + round-base child + shadow child at the province anchor;
   **Y-sort** for depth; **tween** along the march path; flip to the L/R facing by travel heading;
   faction `modulate` on the mask. The 2D map is unchanged.

**Tooling:** the quad/blade + round base + slot + shadow bake are `bpy`-scriptable and headless-
batchable (`blender --background --python`; render → inspect PNG → adjust). The one real art task is
the three painted broadside textures — traced from the references below.

### Reference images (gathered + verified July 12, 2026)

Ship-able references are Wikimedia Commons under **CC BY / CC BY-SA** (attribution — add to
`THIRD_PARTY_LICENSES.md` if any texel is directly derived); collector catalogs are **look-only**
(trace the pose, don't ship the pixels).

**Flat-on-round-base + material read (start here — the exact target):**
- [Louis Liljedahl — 30 mm French Napoleonic flats on rounded bases](https://commons.wikimedia.org/wiki/File:Wiki_louis_4.jpg) — CC BY-SA 3.0. French marshal-era flats (2 mounted + 1 foot), dead broadside, each on a rounded tan plinth.
- [Liljedahl — single mounted cuirassier on a round base](https://commons.wikimedia.org/wiki/File:Wiki_louis_2.jpg) — CC BY-SA 3.0. Clean single silhouette + base + matte-enamel-over-relief.
- [Liljedahl — unpainted 30 mm flat (raw pewter relief)](https://commons.wikimedia.org/wiki/File:Wiki_louis_1.jpg) — CC BY-SA 3.0. The material before paint: shallow raised-line relief, matte pewter, knife-thin edge.
- [Roscheider Hof museum — flats on base slabs](https://commons.wikimedia.org/wiki/File:Konz,_Roscheider_Hof,_Zinnfiguren.jpg) — CC BY 4.0. Eye-level "flat blade rising off a base."
- [Zinnfiguren-Museum Goslar — flats on oval bases](https://commons.wikimedia.org/wiki/File:Zinnfiguren_Goslar_19_Kaiser.JPG) — CC BY-SA 3.0. Isolated silhouettes, base-under-figure geometry.
- [Engraved slate mould for flats (W. Schweizer)](https://commons.wikimedia.org/wiki/File:Gravur_einer_Zinngussform_f%C3%BCr_Flachfiguren_Wilhelm_Schweizer.jpg) — CC BY-SA 4.0. Why a flat looks the way it does (intaglio broadside relief).

**Infantry** (CC BY 2.0, Plassenburg Zinnfiguren-Museum / T. Quine):
- [Napoleonic riflemen](https://commons.wikimedia.org/wiki/File:Napoleonic_riflemen_(24797751511).jpg) · [Napoleonic soldiers — shako line](https://commons.wikimedia.org/wiki/File:Napoleonic_soldiers_(24734242121).jpg) · [Napoleonic marching band — standard/instrument-bearer analogue](https://commons.wikimedia.org/wiki/File:Napoleonic_marching_band_(24536875213).jpg)
- Look-only: [Rick Sanders — French flats (colour bearer + Guard bearskin)](https://www.ricksanderszf.com/france.html)

**Cavalry** (CC BY 2.0, Plassenburg / T. Quine):
- [Light cavalry](https://commons.wikimedia.org/wiki/File:Light_cavalry_(27305669784).jpg) · [Charging horsemen — raised sabre](https://commons.wikimedia.org/wiki/File:Charging_horsemen_(25372789301).jpg) · [Dragoons on the attack](https://commons.wikimedia.org/wiki/File:Dragoons_on_the_attack_(27853691975).jpg) · [Gen. Lasalle — single mounted figure](https://commons.wikimedia.org/wiki/File:General_Lasalle_in_the_field_(25922185200).jpg)

**Artillery** (CC BY 2.0, Plassenburg / T. Quine + look-only Kieler):
- [Model artillery — gun-silhouette library](https://commons.wikimedia.org/wiki/File:Model_artillery_(25303850485).jpg) · [Tiny artillery — flat + base at table scale](https://commons.wikimedia.org/wiki/File:Tiny_artillery_(27738350581).jpg)
- Look-only: [Kieler — French Napoleonic gun + crew flat plate (Hf 19)](https://www.kieler-zinnfiguren.de/Figures/FranzArtill2.jpg) — the exact cannon+crew broadside target.

Full open-license pool: [Category: Tin soldiers in Plassenburg Zinnfiguren-Museum](https://commons.wikimedia.org/wiki/Category:Tin_soldiers_in_Plassenburg_Zinnfiguren_Museum) (166 files, mostly CC BY 2.0).

### Modeling notes (distilled from the reference sweep)

- **Silhouette is the whole product.** Every prop (musket, sabre, shako, horse legs, spoked wheel,
  trail) must survive in pure outline. Colour/eagle bearer = the tallest silhouette in the infantry
  rank; cavalry = locked gallop + raised sabre clearing the helmet; artillery = wheel ≈ barrel
  length, crew tucked against the gun in-plane.
- **Lock the broadside camera** dead-level, nose-right; never 3/4. Mirror for the opposite travel
  direction rather than rotating.
- **Round base = the footprint channel.** Disc diameter ≈ figure width; figure plane bisects the
  disc; a small root/tab where feet/hooves/wheel fuse into the base kills the floating knife-edge.
  Default un-tinted base = ochre "ground."
- **Line-shaped contact shadow, not a body blob** — darkest where blade meets base, feathering to
  the rim.
- **Tint one channel.** Coat mass = faction mask (French navy w/ red facings as the authored base
  look); bare pewter/metal (sabre, barrel-bronze, tyres) + base stay neutral so "tin" survives any
  hue; a darker line-in-the-groove + lighter ridge-highlight makes the low relief pop at table scale.

**Effort:** ~2–3 days art (3 broadside textures + round base + line-shadow + the locked rig) · 1
code slice (placement / Y-sort / facing-flip / tween, additive) · ~free runtime.

**Completion definition:** the three arm flats render as baked PNG+alpha sprites (figure + round
base + line-shadow, mirrored L/R), faction tint working via `modulate` on the coat mask, placed +
Y-sorted on the map at marshal locations and tweening + facing-flipping on move; the 2D
map/zoom/labels untouched (0 `SCRIPT ERROR`); CC-BY reference attributions recorded in
`THIRD_PARTY_LICENSES.md` if any art is traced from them.

**Test:** extend `tests/test_ui_visual_foundation.py` — assert the 3 flat sprites (+ round base +
shadow, both facings) exist in `assets/ui/pieces/` and that each active marshal renders a piece
keyed to its dominant arm.

---

## 8. Session Segmentation Ledger — how the sweep is split across sessions

> **Purpose (GR9 completeness — "don't miss any spots"):** the sweep is bigger than one session.
> This ledger cuts it into session-sized slices, each with an **exact spots checklist**, entry/exit
> criteria, its test, and a STATUS line, so a fresh session can pick up a slice and finish it
> without a gap. **Standing per-session rule:** every session ends by (a) booting the engine + `grep`
> for `SCRIPT ERROR`, (b) landing that session's test green + the full suite green (pre-commit hook),
> (c) ticking its boxes below + updating `docs/STATUS.md`. **Land each session, then pause for review**
> (slice cadence) before the next. Dependency spine: **U1 → U2 → U3**; **U4 → U5** (pieces) depend
> only on U1's theme and may run any time after U1 — recommended after U3.

### Session U1 — Foundation: UI-0 + UI-1 (then PAUSE for review)
- **Entry:** master clean; the git-ignored `assets/` tree present (§2).
- **Spots checklist:**
  - [x] **UI-0** ✅ LANDED July 12, 2026 — audited `assets/` complete vs §2 (13 font families each w/ OFL; 37 portraits + the Abdurrahman exception; two-set icons; 16 flags); git-tracking policy applied = **force-add the usable shipped assets** (198 files, ~77 MB: `.ttf`+`OFL.txt`, portraits, icon/border/heraldry/ornament/decor SVG+PNG+JPG, the two icon `LICENSE` files, textures, audio WAVs) while the **`*.zip` master-pools, source `*.psd`, and the 265 MB `movies.avi` stay ignored**; `THIRD_PARTY_LICENSES.md` reconciled. **`.import` sidecars + `.svg`/font import-scale deferred to UI-1's import step** (Godot has not imported the assets yet — no sidecars exist to configure; UI-1's checklist owns "commit each `.import` sidecar").
  - [x] **UI-1 fonts** ✅ LANDED July 12, 2026 — the 3 UI-1 `.ttf` were already tracked (UI-0); Godot 4.4.1 `--headless --import` generated all 26 font `.import` sidecars; the 3 in-use sidecars (Cinzel `uid://cxiqku0m3u7af`, EB Garamond `uid://dnyhh3gjkf5ox`, Source Sans 3 `uid://3snjpsvwfje5`) are **force-added** (they sit under the git-ignored `assets/` + match the global `*.import` ignore; `.godot/imported/` cache stays regenerated, not committed).
  - [x] **UI-1 theme** ✅ LANDED — `ui/main_theme.tres` authored via a one-shot GDScript generator (guarantees correct type-variation + ext_resource serialization; generator deleted after run): `default_font` = EB Garamond @ 16; Button `normal`/`hover`/`pressed`/`disabled` (+ `focus`) styleboxes (navy fill / gold border / 2px bottom / radius 3); `PanelContainer/panel`; `HeadingLabel` = `Label` variation with a Cinzel `FontVariation` (wght 600) + navy outline (size 5).
  - [x] **UI-1 register** ✅ LANDED — `project.godot` gained `[gui] theme/custom="res://ui/main_theme.tres"`.
  - [x] Confirm inherit-the-skin ✅ — the project-wide theme now propagates to every `Control`; buttons that previously overrode only `font_color` (§0) inherit the new styleboxes. Per-node overrides (`popup_base.gd::_apply_standard_theme`, the 299-override sprawl) intentionally remain for **UI-2** to migrate — not ripped out here.
  - [x] Boot engine → `grep SCRIPT ERROR` == 0 ✅ — both a headless `--editor` open (parses every `.gd` + loads the theme) AND a headless game-scene run (`--quit-after 180`, executes `_ready()`) reported **0 `SCRIPT ERROR`** and no theme/font/resource load failure.
  - [x] Add `tests/test_ui_visual_foundation.py` ✅ (15 tests, all green): `gui/theme/custom` set + `main_theme.tres` parses + the four Button styleboxes + `PanelContainer panel` + `HeadingLabel` variation + default_font@16; the 3 font families present with `OFL.txt` + a committed `.import` sidecar; a portrait for every `europe_1805.json` marshal (21 active + 17 pool = 37) **except Abdurrahman** (exemption self-guarded).
- **Exit:** UI-1 completion definition (§4) met ✅; **PAUSE for user review.**
- **STATUS line:** ✅ recorded — UI-0 + UI-1 landed July 12, 2026; boot-smoke 0 `SCRIPT ERROR` (editor + game scene).

### Session U2 — UI-2: color centralization + UI scale (folds DEF-13)
- **Entry:** U1 landed + reviewed.
- **Split (July 12, 2026):** U2 was split into **Part 1 (UI scale + the user-requested
  expandable/scaling command window; ✅ LANDED)** and **Part 2 (colour migration + theme sizes +
  readability audit + true native-map compensation; ▶ REMAINS)** so the stateful new feature lands
  focused/reviewable, separate from the sprawling 51-file colour sweep (slice cadence).

- **Part 1 spots checklist — ✅ LANDED July 12, 2026:**
  - [x] **Expandable command window** (user request) — `BottomLeftUI` gains a top-right corner
    drag-grip (`main.gd` `_create_resize_grip`/`_on_grip_gui_input`/`_resize_terminal_from_mouse`,
    grows up+right from its bottom-left anchor, min 300×180 / max 1000×900 clamped to the window,
    double-click resets) + `A− / A+` header buttons that scale **every** terminal font crisply
    (`_apply_terminal_scale`, base sizes auto-discovered from the `.tscn` so it never drifts).
  - [x] Wire the UI-scale slider: `get_window().content_scale_factor` (0.75–2.0) in the pause-menu
    Settings (replaces the "coming soon" stub); `main.gd` owns applying + persistence. Stretch mode
    left **disabled** (lowest map risk); the map's on-screen coverage is unaffected at any scale.
    **`canvas_items`/`expand` baseline was NOT adopted** (Part 2 decides it against the map).
  - [x] Persistence — new `scripts/ui_settings.gd` (`class_name UiSettings`, `user://ui_settings.cfg`):
    terminal width/height, terminal scale, global ui_scale; clamped on read AND write.
  - [x] Replace `test_map_slice8_balance.py::test_def13_fixed_hud_baseline_pins` → the
    `test_def13_ui_scale_mechanism_landed` mechanism pin (war-status geometry still pinned).
  - [x] Boot engine → `grep SCRIPT ERROR` == 0 (headless editor parse + game-scene `_ready` run; the
    single `SubViewport` stretch warning is pre-existing, not introduced).
  - [x] Test: `tests/test_ui_scale_expandable_terminal.py` (12) + `test_gdscript_color_centralization.py`
    still green; the Godot parse report regenerated.

- **Part 2 spots checklist — ✅ LANDED July 12, 2026:**
  - [x] Migrate inline `Color()` duplicates → `Utils`/theme colors — a `Utils.UI_*` chrome palette
    (12 `Color` consts: `UI_GOLD`/`UI_GOLD_BRIGHT`/`UI_PANEL_BG`/`UI_ACTIVE_TAB_BG`/`UI_POPUP_BG`/
    `UI_TEXT_DIM`/`UI_ALERT`/`UI_WARNING` + the score/bar quad `UI_SCORE_POSITIVE`/`_NEGATIVE`/`_NEUTRAL`/
    `UI_BAR_BG`) now the single source; the recurring navy/gold/state literals migrated across the HUD/
    ledger/popup chrome (`top_bar`, both ledgers, `popup_base`, `war_status_panel`, `war_detail_popup`,
    `main` resize-grip, `campaign_log`, `marshal_petition_dialog`, `reward_dialog`, `objection_dialog`).
    The Part-1 resize-grip/settings gold literals folded in. Byte-identical values (imperceptible ≤0.003
    shift only on the one `0.851→0.85` gold precision unifier). `test_gdscript_color_centralization.py`
    green; `test_ui2_part2_color_and_map.py::test_migrated_literals_are_gone` pins the reduction.
    *Scoping note (GR9): `notification_bar`'s `PRIORITY_COLORS` severity ramp and the map-domain
    constants in `map_renderer_base` are coherent single-domain sets, deliberately NOT centralized.*
  - [x] Per-type font sizes on the theme — `main_theme.tres` now declares `Label`/`LineEdit`
    (`font_size` 16) and `RichTextLabel` (`normal_font_size` 16) explicitly (Button 15 / HeadingLabel 22
    already differentiated), completing per-type control. Sizes set to the current effective default 16
    = **zero visual regression** (the deliberate non-destabilising pass); the real ≥2560 up-scaling is
    the Part-1 `content_scale_factor` slider's job, now feeding a crisp map.
  - [x] **True native-resolution map compensation** — the map's SubViewport is displayed through a
    dedicated `STRETCH_SCALE` `TextureRect` (`map_display`, `EXPAND_IGNORE_SIZE`) and sized to PHYSICAL
    pixels (`size * content_scale_factor`) by `_refresh_map_viewport_resolution`, so it stays crisp at
    scale > 1.0 (1 render texel : 1 physical pixel). The stretch-drawing `SubViewportContainer` was
    removed. All four logical→viewport pointer/pan/zoom conversions (`_screen_to_map_position`, mouse-
    drag pan, key pan, `_zoom_at_point`) now scale by `_viewport_pixel_scale()` so hit-testing stays
    exact at any UI scale. `refresh_viewport_scale` re-asserts the resolution on scale change. **Still
    needs the user's ≥2560 visual sign-off** (the spec's visual gate — this is the "you sign off" path).
  - [x] Readability pass at ≥2560-wide — comfortable base (default 16 / Button 15 / headings 22) plus
    the Part-1 Interface Scale slider (0.75–2.0) now driving a physically-crisp map is the readability
    mechanism; no per-screen destabilisation.
  - [x] Boot engine → `grep SCRIPT ERROR` == 0 — headless `--import` (parse; validates the
    `const … = Utils.UI_*` aliases), a game-scene run, AND a `europe_map_smoke` runtime pass (confirmed
    `map_display` = TextureRect, stretch=SCALE, expand=IGNORE_SIZE, viewport = size×scale) all clean; the
    former pre-existing SubViewport stretch warning is gone.
- **Exit:** UI-2 completion definition (§4) met (map render-res physical; inline-`Color()` materially
  reduced; `test_gdscript_color_centralization.py` green; the DEF-13 pin replaced by the U2 Part 1
  mechanism pin) — pending only the user's visual sign-off on map crispness.
- **STATUS line:** ✅ recorded — U2 Part 1 + Part 2 landed July 12, 2026; UI-2 CLOSED pending user
  ≥2560 map-crispness sign-off; resume at **U3** (texture/border/icon/portrait polish).

### Session U3 — UI-3: texture / border / icon / portrait polish (excludes pieces)  ✅ LANDED July 12, 2026
- **Entry:** U2 landed.
- **Spots checklist:**
  - [x] **Panel texture + framing** — a navy-tinted **leather `StyleBoxTexture`** (seam-free
    `region_rect` crop of `fabric_leather_01_diff_1k.jpg`, `modulate_color` dark navy) is wired to the
    theme `PanelContainer/panel`, so the always-visible command terminal + non-overriding popups gain a
    subtle leather grain. **Deviation (conscious, documented — GR9):** the big command screens (Generals
    / both ledgers / dispatch / war detail) each carry a LOCAL crisp `StyleBoxFlat` (gold border + navy
    fill + rounded corners) and those were KEPT rather than converted to `StyleBoxTexture` 9-slice frames
    — the only frame asset on disk (`buttons-and-frame_frame.png`) decodes as a muddy dark-brown 56² and
    `modulate` cannot brighten a dark texture to gold, so a full-texture frame would have DEGRADED the
    crisp navy/gold legibility the project guards. The framing intent is met instead by the filigree
    corners below (readability-first, per the map-palette precedent).
  - [x] **Filigree corners** — two gold-modulated `corner_floral_01.svg` `TextureRect`s straddle the
    Generals panel's bottom corners (`mouse_filter=IGNORE`, semi-transparent so text reads through the
    line-art). Generals-scoped (the "marshal cards" panel). The ornament SVG was recolored `#000000`→
    `#ffffff` so the gold `modulate` lands (black × gold = black otherwise).
  - [x] **Icons on HUD/buttons** — the curated sets were preprocessed to WHITE silhouettes (game-icons:
    512² black bg `<path>` stripped; phosphor: `currentColor`→`#ffffff`) so the gold tint (`[img color=]`
    inline / `icon_normal_color` on buttons) lands. Wired: close-**X** → `x.svg` on all 5 command screens
    (shared `Utils.apply_icon_only_button`); the 5 top-bar nav buttons → phosphor `list`/`map-trifold`/
    `users-three`/`handshake`/`scroll` (`Utils.apply_button_icon`, labels + hotkey hints kept); the
    terminal resize-grip glyph → `arrows-out.svg`; Generals inline unit icons (game-icons
    `unit-infantry/cavalry/artillery`, tinted to the type colour) + `medal-military`/`crown` on the
    Laurels/Commission headers. The **game-icons CC-BY 3.0 visible credit** ships in the pause-menu
    Settings box (Phosphor is MIT; portraits PD). *(Text-Size +/− kept their glyphs — an icon is illegible
    at 24×14. Lamoot border art not shipped, so no Lamoot credit needed.)*
  - [x] **Portraits** — the 37 PD likenesses render as `[img]` thumbnails on the Generals marshal cards
    (60×76) AND the Commission bench candidates (48×60), keyed by internal marshal name (matches the
    coverage test's keys); a marshal with no likeness (**Abdurrahman** by design) degrades to a gold
    monogram, so no card is faceless.
  - [x] **Boot engine → `grep SCRIPT ERROR` == 0** — headless `--import` (re-imports the edited SVGs) +
    game-scene run (`main.gd`/`top_bar`/all four `add_child`'d screens run `_ready` at boot) both clean;
    the settlement parse-harness report regenerated (every covered script parse_ok + load_ok).
    `test_ui_visual_foundation.py` extended (+11 UI-3 assertions); full suite **13,022 passed / 3 skipped**.
- **Exit:** UI-3 completion definition (§4) met — panels textured (terminal/popup leather + filigree
  framing), curated icons render on their target buttons/HUD, portraits show on Generals + character-sheet
  cards with the Abdurrahman monogram fallback.
- ~~⚠ open (visual sign-off)~~ **✅ CLOSED July 16, 2026** — self-served screenshot pass (user-directed;
  record in STATUS.md ⚔️ July-16): leather subtlety, nav icon sizing, Generals filigree, and portrait
  aspect all verified in-game; no tunes needed.
- **STATUS line:** ✅ recorded — UI-3 texture/icon/portrait polish landed July 12, 2026; boot-smoke 0
  `SCRIPT ERROR`; resume at **U4** (War-Table Pieces art) or **DEF-1 voices** per the queue.

### Session U4 — War-Table Pieces ART (tin-flat-on-round-base)  ✅ LANDED July 12, 2026
- **Entry:** U1 landed (independent of U2/U3; recommended after U3). Reference set = §7.
- **Pipeline note (conscious deviation, GR9):** Blender is **not installed** on this
  machine, and a tin *flat* is by definition a 2D silhouette with shallow relief — so the
  art was authored with an equivalent **2D supersampled pipeline** (`tools/gen_war_table_pieces.py`,
  Pillow + numpy, offline dev-only, not in `requirements.txt` / not run by CI) instead of a
  headless `bpy` rig. Every §7 art requirement is met: dead-broadside nose-right silhouettes,
  matte-enamel coat + engraved-line **rim light / core-shadow / dark contour** relief pass baked
  from the figure silhouette, a beveled round base disc (per-arm footprint), a **line-shaped**
  contact shadow, a neutral faction **coat tint-mask** (metal/base stay neutral), and a
  **mirrored L/R** pair. Output is deterministic (re-export → zero diff). The reference photos
  were *studied, not traced* — **no third-party pixels used or derived** (so no mandatory
  attribution; a courtesy reference-inspiration note was added to `THIRD_PARTY_LICENSES.md`).
- **Spots checklist:**
  - [x] Locked **dead-broadside** framing, single low-angle key (relief pass = rim light on
    up-right-facing edges + core shadow on down-left + crisp dark contour), baked at 4× supersample.
  - [x] Author 3 broadside figures — infantry (tight-rank shako soldiers + a taller colour/eagle
    bearer whose banner is part of the tint-mask) / cavalry (galloping horse + rider, sabre raised
    clear of the shako) / artillery (bronze barrel + big spoked wheel + trail-with-spike + an upright
    gunner with ramrod) — matte enamel + engraved-line rim; verified legible at 64px map scale.
  - [x] Round base disc (per-arm footprint: infantry widest 0.80 / cavalry 0.58 / artillery 0.86)
    with a top-down bevel + rim highlight; **line-shaped** feathered contact-shadow layer.
  - [x] Neutral **coat tint-mask** (light-gray coat mass, Godot `modulate` multiplies it to the
    nation hue); base + metal + flesh on neutral channels so "tin" survives every faction colour.
  - [x] **Mirrored L/R facing pair** per arm (nose-right + horizontal flip).
  - [x] Export PNG+alpha (256², ≈2–3× map size) → `assets/ui/pieces/` = **24 sprites**
    `{arm}_{layer}_{facing}.png` (layers base/shadow/coat/body × facings r,l). Force-added
    (the `assets/` tree is git-ignored, like the U1 fonts / U3 icons).
  - [x] Reference-inspiration credits added to `THIRD_PARTY_LICENSES.md` (Plassenburg/Quine,
    Liljedahl, Roscheider Hof, Goslar, Schweizer) — courtesy only; no pixels derived.
  - [x] **Test:** `tests/test_ui_visual_foundation.py` extended (+5 piece tests, stdlib PNG parse,
    no Pillow dep) — the 24 sprites exist + exact-set, each 256² RGBA + non-truncated + non-blank,
    body/coat are real cutouts (alpha-coverage bounds). Full file green.
- **Exit:** all 24 sprites present in `assets/ui/pieces/` per the naming above; from-disk composite
  verified tinting correctly for multiple nations (France navy, Russia green) with metal/base neutral.
- **STATUS line:** ✅ recorded — War-Table Pieces ART landed July 12, 2026; **resume at U5** (Godot
  placement: Y-sort / tween / facing-flip / marshal→dominant-arm keying + its behaviour test).

### Session U5 — War-Table Pieces CODE (Godot placement)  ✅ LANDED July 13, 2026
- **Entry:** U4 art exists.
- **Spots checklist:**
  - [x] `Sprite2D` (flat) + round-base + shadow + coat layers per marshal at its
    province anchor, keyed to dominant arm — new `scenes/war_table_piece.gd`
    (`class_name WarTablePiece`): 4 stacked `Sprite2D` children (shadow/base/coat/
    body), ground-anchored at the node origin (centered=false, offset (−128,−210),
    node scale = frame_px/256) so feet sit on the province and y-sort orders by feet;
    static texture cache; `pieces_available()` asset gate.
  - [x] **Y-sort** (`pieces_layer.y_sort_enabled`, a persistent `Node2D` under
    `world_layer` distinct from the torn-down `force_layer`); **tween** province→
    province on a REAL region change (`WarTablePiece.move_to`, kills the prior
    tween); **facing flip** by travel-heading dx. `_update_war_table_pieces()` is a
    DIFF updater (retire gone / snap slot-re-centers / tween real moves / spawn new)
    called from both `update_all_regions` + `update_region`.
  - [x] Faction `modulate` on the COAT sprite only via `Utils.NATION_COLORS`
    (base/shadow/body neutral pewter); a value floor (`_legible_tint`) lifts very
    dark hues (Prussia) so the coat doesn't muddy into the relief.
  - [x] **Dominant arm keyed backend-side too** — added a display-only top-level
    `arm` to the base marshal dict in `world_state.get_game_state_summary` (derived
    from the existing `cavalry`/`artillery` flags, GR6); `tactical_state` is
    player-only, so without this every ENEMY corps drew as infantry. Fog-safe: the
    filtered summary keeps enemy marshals in `marshals[]` only at FULL visibility,
    reducing PARTIAL/STALE to `fogged_forces` (name/nation/band only) — arm never
    leaks (`tests/test_fog_of_war.py::TestMarshalArmField`, 4). `_marshal_arm` reads
    the top-level field first, `tactical_state` as the legacy fallback.
  - [x] Additive layer — the 2D map / zoom / labels untouched; bitmap-mode gated
    (`_bitmap_mode and WarTablePiece.pieces_available()`), so the legacy circle
    fixture keeps its square icons. The `force_layer` square is suppressed when
    pieces are active (name label + hitbox kept, aligned to the standee slot math).
  - [x] Boot engine → `grep SCRIPT ERROR` == 0 (headless `--import` + main-scene
    run; a temp `_piece_probe` scene confirmed 3 pieces instantiate keyed to
    `[infantry, cavalry, artillery]` + the move/retire path, then removed).
  - [x] `tests/test_ui_visual_foundation.py` extended (+3 static `.gd` assertions:
    the piece class shape, the renderer wiring, the bitmap-mode gate) — full file
    green. The "each marshal renders a piece keyed to arm" runtime behaviour is the
    manual boot-smoke gate (pytest can't boot Godot).
- **Piece ART re-touch (this session):** cavalry redrawn (deep-chested horse,
  arched neck + ears, clean gallop, raised curved sabre — the U4 pass read as
  spidery legs + a muddled head); infantry coat mass widened + figures upscaled
  ~12% for the 64px map read; artillery crew enlarged; the contact shadow was
  fully occluded by the opaque base disc (drawn at 0.82× base radius underneath) —
  now a soft halo peeking past the base rim so pieces read as grounded.
  Regenerated the 24 sprites; verified legibility + faction tint (France/Austria/
  Russia) at 48–80px.
- **Exit:** §7 pieces completion definition met — pieces placed + y-sorted + facing-
  flipping + tweening + faction-tinted on the map, the 2D map/zoom/labels untouched,
  0 `SCRIPT ERROR`.
- ~~⚠ open (visual sign-off)~~ **✅ CLOSED July 16, 2026** — self-served screenshot pass on
  the running 1805 map (record in STATUS.md ⚔️ July-16): piece size + two-rank
  clustering + tint + grounded shadows all read well at native res. One accepted nit
  (no tune): at minimum zoom the three ARMS are hard to tell apart — resolves on
  zoom; strategic-glance identity (whose army, how many stacks) is carried by the
  coat tint + name labels, which is the piece layer's actual job.
- **STATUS line:** ✅ recorded — War-Table Pieces CODE landed July 13, 2026; the
  War-Table Pieces sub-item CLOSED. **The UI Visual Foundation Sweep is now
  U1–U5 complete** (pending the standing U2 map-crispness / U3 / U5 visual sign-offs).

### Session U6 — Interaction & Heraldry Sweep ✅ LANDED July 16, 2026

**User directive:** "add buttons for vassal interactions and do another review of the ui … streamline
systems, add clickable items when possible."

- **VASSALS tab (diplomatic ledger, tab 6 / KEY_6):** backend `_build_vassals` section on
  `/diplomatic_ledger` — per player-vassal loyalty, autonomy, tribute (+rate), VS-4 contribution tier,
  warning band + grip-aware recovery hint, garrison/subsidy lever lines, granted-province provenance,
  and the **same** honest-availability `actions[]` rows the F1 wizard consumes
  (`get_available_diplomatic_actions` is the single gate source — chips can never disagree with the
  executor). Chips send the wizard-identical typed commands; **[Cede Province…]** hands off to the
  wizard's positive-path province picker (`open_for_nation`). Foreign satellites stay on the Nations
  tab. Empty state teaches the three vassalization routes.
- **Next-turn loyalty forecast:** NEW single-source `vassal.forecast_vassal_loyalty(world, lord, name)`
  — mirrors `process_vassal_loyalty` term for term (drift, garrison, **subsidy clauses**, shared enemy,
  relations, grip) minus only the transient battle term; consumed by the ledger tab AND the wizard
  preview trend (review fix UI6-VAS-1/-2 — the old wizard arrow read autonomy drift alone).
- **Region Action Panel (`region_panel.gd/.tscn`, CanvasLayer 26, non-modal):** the game map's
  `region_clicked` signal — emitted since the cutover, connected to nothing — now opens a fog-honest
  side panel rendered from the map node's own filtered stores (`region_full_data` / `region_visibility`
  / `region_marshals` / `region_garrisons`; zero extra fetch, zero fog leak). Context chips: own
  province → Recruit Infantry / Build Depot (hidden when a `supply_depot` exists); foreign controller →
  Negotiate (wizard handoff); own marshals → per-marshal Fortify/Unfortify/Drill gated on the
  tactical_state flat bools. Same visibility rule as the war HUD (never over a screen/modal).
- **Heraldry:** `Utils.nation_flag_path/bb_flag/apply_flag_icon` (cached, untinted — flags are colored
  art, never gold-tinted) wired into ledger nation rows + vassal cards, wizard step-1 buttons + step-2
  header, war HUD cards + armistice rows, war-detail popup header.
- **Notification glyphs:** `TYPE_ICON_SVGS`/`ROUTE_ICON_SVGS` map every notice family to a phosphor
  silhouette on the priority-colored pill; unmapped types keep the legacy 3-letter code. Glyph
  existence pinned by test.
- **Top-bar gear** (pause menu was ESC-only) honoring the ESC invariant (closes screens first);
  **Generals order chips** (Fortify/Unfortify/Drill per standing marshal) through the reward pipeline;
  Talleyrand-tab **[Assess the Situation]** chip (closes the ledger, sends the W6-9 verb).
- **Streamlining:** `Utils.bb_icon`/`bb_button_chip` single-source the chip idiom;
  `_format_number` de-duplicated (marshal_management / strategic_ledger / dispatch_view /
  notification_bar / diplomatic_ledger → `Utils.format_number`); stale "Generals is a placeholder"
  guard retired; nav hover style-jump fixed (flat hover/pressed styleboxes).
- **U5 residual CLOSED:** `_marshal_slot_offset_2d` — 3+ co-located standees split into two ranks
  (`WAR_PIECE_RANK_DEPTH=16`, y-sorted so the rear rank draws behind), shared by pieces, name labels,
  and hover hitboxes; 1–2 pieces keep the flat line byte-identical.
- **Adversarial review (23 agents, 5 lenses, find→verify):** 15 confirmed findings (9 distinct after
  dedup), all fixed: subsidy forecast term + trend unification (above); chip terms derive from
  backend fields (`dp_cost`/`gold_cost`/grip-effective `invest_gain`/`autonomy_up_gain` — never a
  hardcoded gain the VS-R spiral blunts, with the executor's own "faltering grip" disclosure);
  three-way path label ("scenario"-seeded 1805 vassals are "client state of the Empire", not
  conquests); shared `_chip_command_in_flight` latch (double-click = double spend); gear
  closes screens before pause (ESC invariant); `_on_objection_response` refreshes open info screens
  (chip-raised objections resolved after the chip's callback); region-panel depot check fixed to
  `supply_depot`; parse-harness report regenerated (settlement-critical .gd touched). 2 claims
  refuted, 1 downgraded-and-fixed-anyway.
- **Gates:** boot-smoke 0 `SCRIPT ERROR` (before and after review fixes); ruff clean;
  `tests/test_ui6_interaction_sweep.py` (44) green; full suite **13,521 passed / 3 skipped**.
- ~~⚠ open (visual sign-off)~~ **✅ CLOSED July 16, 2026** — self-served screenshot pass (user-directed
  "do visual check yourself for sign off"; record in STATUS.md ⚔️ July-16): vassal cards (flags +
  loyalty bars + tribute-cut copy + call-to-arms + garrison hints + actions-blocked banner), region
  panel (Swabia: flag, stats, honest allied-soil chips), ledger flag sizing (crisp at 14–18px incl.
  the redrawn 8-point Ottoman), gear invariant (verified against `main.gd:3790` UI6-GD-1), war-HUD
  flag + full-width war-score bar, and the two-rank piece spread on the 3-stack — ALL PASS, no tunes.

#### U6 follow-up (same day, user live-review): full province verb set + missing flags + sprite check

- **"clicking a province only has build depot/fortify/drill — there are more options":** the Region
  Action Panel now carries the full region-scoped verb set — **Recruit Infantry / Cavalry / Artillery**,
  **Build Depot / Fort / Training Ground / Market / Stables** (each hidden when built; whole row hides
  when the fog-filtered payload shows no free slot — towns/rural report 0), **Build Watchtower**
  (slot-exempt, own field), **Repair** (only when the payload shows damage), per-marshal **Scout** and
  **Attack <enemy>** chips (enemies ride `region_marshals` only at FULL visibility — fog-safe; capped
  at 2 per marshal row). Chips carry their full typed command in a generic `do:<command>` meta; the
  executor owns every gate. Chip command words verified against `_extract_building_type` +
  the mock-parser keyword blocks + corpus rows ("recruit cavalry at Lyon", "build market in Paris").
- **"some flags are missing":** the roster ships 20 nations; the heraldry set had 16. Authored the
  missing four in the set's simplified flat style (simple heraldic geometry, no license burden):
  **Hanover** (white/yellow), **Hesse** (red/white), **KingdomOfItaly** (the 1802–05 red field /
  white lozenge / green heart), **Switzerland** (white cross on red). `THIRD_PARTY_LICENSES.md`
  heraldry section updated 16 → 20; test now asserts EVERY `NATION_COLORS` nation (minus Neutral)
  has a flag on disk.
- **"look at Blender sprites for armies":** Blender is **still not installed** on this machine
  (checked PATH + Program Files + winget), so the §8-U4 3D-render pipeline remains unavailable —
  installing it is a user call. The current 24-sprite carved-wood 2D set was composite-inspected
  this session (France/Austria/Prussia tints × all three arms): coherent tabletop-mini read, clear
  faction rings + flag/shabraque accents, dark-nation floor working. Verdict: keep; revisit only
  if/when Blender lands (owner stays the §8-U4 deviation record).

---

## 9. Session UI — The Gilt Frame, the War Table and the Dressed Page ✅ LANDED November 11, 2026

> **The user's word:** "MAKE THE UI AND UX LOOK BETTER LOOK ONLINE IF NEEDED". Drafted in Plan Mode
> and approved; at the plan's head the user ruled **the content re-layout into the same session** and
> **a dark leather desk** around the map. Rules `SYSTEMS_REFERENCE.md` §212; pins
> `tests/test_ui_gilt_frame.py` (37, a headless engine probe among them, `tools/ui_gilt_probe.gd`);
> before / after pairs `docs/audits/ui_gilt/`. It supersedes `UX_UI_REVIEW_PLAN.md`'s "no visual
> redesign" by the user's word, and U3's deviation (the crisp flat borders kept over textured
> 9-slices): the frame is drawn, not textured, so it stays crisp.

**Why.** All 185 client surfaces shot at HEAD (`7c6edd74`) showed one flat box everywhere — a navy
fill inside a thick tan rounded border, thirty-four scene copies of it — titles in body type, every
button of one weight, the stock scrollbar / field / dropdown, a war room whose map filled 45 % of a
5120×1440 screen beside a flat tan void, and books that were walls of text. A found defect: DDB-R4's
"a spent day turns End Turn gold" added gold to words already gold — invisible since it landed. Online
research agreed with the frames (thin gilt double rules, tracked caps for titles, one filled primary
button, a desk round a map that does not fill an ultrawide screen, right-aligned tabular figures);
its yield was thin, so the direction rests on the frames.

**Two rules.** (1) *Same boxes, better skin* — content margins, Button margins, the separator's height
and the top bar's 36 px are what they were; only the command window's header is re-laid. (2) *The
words are untouched* — cards are painted behind the books' text and the figure column is invisible
spacers, so what a reader, an instrument or a driven test takes off a screen is character-identical.

**As built.**
- **The chrome kit:** `scripts/gilt_frame.gd` (a scripted StyleBox with StyleBoxFlat's property
  names — one frame for 35 scenes and the panels built in code, each keeping its own fill, tone and
  margins; three weights: window, HUD, hairline), `scripts/gilt_rule.gd` (every HSeparator), the
  theme's Button states (same margins), `PrimaryButton` / `PrimaryCaptionButton`, the title face on
  `ScreenTitle` / `DialogTitle` / `DialogTitleLarge` / `HudTitle`, slim gilt scrollbars, the text
  field, the dropdown's menu, the slider; `Utils.tab_styles()` — one tab strip for the top bar and the
  two ledgers. The Generals' two filigree corners are retired (the frame has its own corners).
- **The war room:** the map a sheet on a dark leather desk (a shader over the tracked leather; the
  sheet's shadow and neatline; `DESK_SURFACE` restores July); the top bar deeper, its nav one strip,
  its chips gilt pills; the command window in the frame over its leather, its header one band (the
  title face, compact scale steppers, the minimise glyph); **End Turn the gilt primary exactly when
  the day is spent**; the map's chips, the war HUD, the region panel and the notice rail in the frame.
- **The dressed page:** every marshal, corps, province, arm, court, treaty and client a card
  (`scripts/card_underlay.gd`, read from invisible marks in the page; it draws nothing on a page whose
  paragraphs disagree with its newlines); the portrait at a card's head ringed as a locket; the
  Economy book's gold figures one right-aligned column in lining tabular numerals
  (`Utils.bb_tabulate`).

**The measure.** Every surface re-shot at Interface Scale 1.0 and 2.0 against the HEAD baseline and
the harness's per-frame records diffed: words identical but the command window's title (its two emoji
swords dropped) and the minimise control (a glyph); titles one pixel taller (the face's line height);
readability RED 0 / P1 0 at both scales and at the five physical resolutions; contrast unchanged (the
same 19 / 15 pre-existing parchment-letter rows); fit 7 of 7 at 1920 / 3840 / 5120; consistency 0
hits on 145 surfaces; one new cut line at 2.0 — the docked Generals' Emperor portrait at the window's
foot, a box RR5-X4 cuts by design.

**From the plan, not built (each said with its reason):** the log did not take the 40 px the header
saved — at 800×450 logical the Table lesson's card would have covered five more figures, so the
window is 40 px shorter instead; the grip's hatch stays in the corner (inside the fillet it would sit
on text, against UXR3-F4); the top bar's date keeps the body face (the title face widens the full bar
near its compact threshold); a marshal's name stays under his portrait (one line break, kept so no
reader of the page changes).

**Open:** the user's own look — session H's walk (`UX_UI_REVIEW_PLAN.md` §UXR-4) reads the new skin
on the frames in `docs/audits/ui_gilt/`; each reversal is one line (`DESK_SURFACE`, a frame's `weight`
or `wash`, the rule's `lozenge`).

## 10. Session UI-2 — The Imperial Desk ✅ LANDED November 12, 2026

> **The user's word** (relayed by the session that started this one): raise the client from Session UI's own 7/10
> to 9/10 — a second visual pass over EVERY surface, nothing assumed; assets found online (licence-checked) or coded;
> three blind readers before and after; nothing cut without the user's word. Drafted in Plan Mode and approved (five
> rules, three slices, the measure). Rules `SYSTEMS_REFERENCE.md` §213; pins `tests/test_ui_gilt2_imperial_desk.py`
> (a headless probe among them, `tools/ui_gilt2_probe.gd`) and the driven Auto band in `tests/test_uxr2b_hud_band.py`;
> before / after pairs `docs/audits/ui_gilt2/`.

**The baseline, measured before planning** (HEAD `20ee32ff`): all 185 surfaces shot at Interface Scale 1.0 and 2.0
(0 `SCRIPT ERROR`) and at the five physical sizes; readability RED 0 / P1 0 (4,402 rows); consistency 0 hits on 145
surfaces; contrast 34 rows under 4.5 : 1 (every one a parchment letter's label declaring white over the paper).
**The blind reading:** three sonnet readers, a rubric frozen before the first reading (UXR-3's R1–R8 and visual
craft with period feel, anchored 1–10 on shipped strategy games), 30 fixed frames under neutral names — **7 / 7 / 7,
mean of the 90 marks 6.77**. Worst: the region panel (5); the 5120 war room, Economy, Territories, Manpower, the
Generals at T20, Nations, Vassals, the Balance, the settlement table, the petition, the war detail (6). Best (8): the
war room at 1.0, the diorama, the affair letter, the objection, the main menu. Their common verdicts: walls of small
text with no icons or visualisation; chips that look like links; panels floating in wasted space or voids; the
ultrawide HUD tiny in its corners; the command window eating the map at 2.0; names colliding on the map; dark slab
buttons on parchment.

**The research** (what was taken): Victoria 3's diaries #61 and #49 — figures before prose, icon + figure groups,
colour only at thresholds, a figure that clicks to its ledger; Total War Saga: Troy's UX deep dive — tables with
header rows and right-aligned numerals, one primary act per surface; Bycer's strategy-UI dos and don'ts — End Turn
always distinct, a tooltip that names the figure, its parts and the click; an ultrawide-scaling write-up — a 16:9
safe zone for the HUD on 32:9; Old World's notes and CK3's console diary — paper-native buttons on parchment, map
plaques in a palette distinct from the paper. The Game UI Database and Interface In Game did not answer.

**The assets** (licence-checked; `THIRD_PARTY_LICENSES.md`): the French First Empire eagle (Commons
`Aigle_Empire.svg`, {{PD-self}} vectorisation by F. Michel of an 1804 {{PD-Art}} source, read through the Commons API
before shipping); 36 stat glyphs from the shipped game-icons.net pool (CC BY 3.0, credited in Settings → CREDITS, each
glyph's author in `GLYPHS.txt`); a 4×4 white swatch (made here). The Moniteur's blackletter is the shipped
UnifrakturMaguntia (OFL). Nothing CC-BY-SA.

**The five rules:** figures before prose; one icon per category, everywhere; one button language; fit the content;
period craft at the ceremonies. Motion: a 160 ms fade as a surface opens (no close delay), Reduce motion in Settings.

**As built** (one commit — the slices' files interleave, and the user's standing rule is one commit a session):
- **The kit** (`SYSTEMS_REFERENCE.md` §213): the gilt button face (`scripts/gilt_button.gd`) with a dashed rim when it
  cannot act; four new steps (`EndTurnButton`, `ParchmentButton`, `StatFigure`, `Figure`); 36 stat glyphs and the
  eagle; every chip a rimmed one-cell table; exact meters, relation meters, striped tables, portrait rows, section
  heads (`dress_heads`), in-cell tags (`bb_tag`); a figure strip (`scripts/stat_strip.gd`); a 160 ms opening fade with
  **Reduce motion** in Settings.
- **The war room:** the top bar in three groups (resources, court, date), each figure opening its book; map plaques
  and nameplates (no overprint); the command window's status led by glyphs, End Turn on its own step, its header
  folded into one band under 600 logical px; the war score a gilt track with its figure in a medallion; the rail's
  roundels; the region panel in the kit; **Auto** HUD width (a 16:9 zone on 32:9) and the 32:9 derivation at 1.60.
- **The books:** figure strips over the Strategic Ledger; corps, law and order cards; the Territories and Intel tables;
  Economy's INCOME and CHARGES; the Generals' portrait rows with meters and tags; the Diplomatic Ledger's facts tables,
  the threat gauge and the Vassals' one chip row; the Cabinet's court and act rows (70 % of the window); the
  settlement table's per-court cards, meters and quote blocks; the Dispatch, the Moniteur and the enemy phase in cards
  with glyphs.
- **The letters, the popups, the ceremonies:** letters and popups fit their content (an arms row on nine popups; the
  compact view under 600 logical px); parchment buttons on paper; the objection's even grid where it fits; Settings a
  page; the main menu's shade and eagle; the diorama's frame and strength band; the end card's eagle and figure strip;
  the School of War's header strip and short paragraphs.
- **An audit before the record** found approved plan items unbuilt (the first "slices built" was wrong): ten builders
  on sonnet, one owner per file, built the remainder the same session; each script diff-read, parse-checked, shot and
  read by eye, and the defects the frames showed fixed (badges one letter a line inside table cells → `bb_tag`; the
  Territories table's columns; four contrast rows; the war HUD's arms on the side its colour fills toward).

**What the instruments caught after the build**, each fixed at its cause and pinned
(`TestWhatTheInstrumentsCaught`): the objection's even grid pushed a long answer onto a row of its own and stood the
dialog over the bar at 2.0 (now even only when every answer fits half a row); the alert red read 4.24–4.36 : 1 once
the figures took the 16-px `Figure` step (body type: `UI_ALERT_TEXT`); the contrast census measured the new rimmed
chips against the page (the harness now reads a one-cell table's own ground; the dimmed cell keeps the exempt pill's
ground); four new greys were literals (named tokens); the tooltip's shadow grew its popup window past the screen's
edge (PC-F47's driven pins — the shadow is dropped, the wider padding kept); the capture runner forced "full", so
Auto's zone had never been on a frame (it shoots the game's default now).

**The measure** (the final tree): every surface at Interface Scale 1.0 and 2.0 — 370 frames, 0 `SCRIPT ERROR`; readability RED 0 / P1 0 (5,196 rows); **contrast 0 rows under 4.5 : 1** (34 at the baseline); consistency 0 hits on 145 surfaces; the five physical sizes — 925 frames, 0 `SCRIPT ERROR`, readability RED 0 / P1 0 (13,052 rows); fit 185 of 185 surfaces at 1920×1080, 3840×2160 and 5120×1440. The per-frame word diff against the baseline: every changed word is in a class §213 names (the top bar's figures lost their words to their tooltips; the `═══` bars dressed away; new figure captions, badges and column heads; the Settings' Auto label). The full suite 39,574 passed at six workers, the readability record re-recorded (`docs/audits/uxr0/readability_after_{named,all}_2026_11_12.json`).

**The score:** three fresh sonnet readers, the identical prompt and frozen rubric, the same 30 frame ids under
neutral names, shot from the final tree: **7 / 7 / 7 — the median is 7, unmoved; the mean of the 90 marks 6.77 →
6.93**. Eight frames rose (Forces 7 → 8, Economy 6 → 7, Territories 6 → 7, Manpower 6 → 8, the Generals at T20
6 → 7, the region panel 5 → 6, the end card 7 → 8, the mailbox 7 → 8), nineteen held, three fell (the war room
8 → 7, the settlement table 6 → 5, the objection 8 → 7); eighteen frames unanimous, twelve a spread of one, none
wider. **The 9 was not reached.** What holds it at 7, with frames (the readers' consensus; the pairs in
`docs/audits/ui_gilt2/`):

1. **The prose on the face** — Nations, Vassals and the Balance (F11–F13, 6 each), the petition (F21, 6), the war
   detail (F25, 6), the region panel (F24, 6), Settings (F28, 7): every reader asks for the explanations behind an
   expander or a tooltip. This pass kept every word on the face by its own rule (the words are what the player learns
   from, and what the tests and the instruments read). Moving the prose is the largest lever left, and it is the
   user's to rule.
2. **The ultrawide** (F02, 6, unanimous): the HUD now frames the map in a 16:9 zone, but the map is a fixed-aspect
   sheet and the desk either side reads as wasted width. The lever: map art wider than the sheet, or a zoom-to-fill
   map mode.
3. **The settlement table** (F16, 5): one card per court and its meter did not lift it — four stacked scroll areas,
   the "more below" tag over a line, nine like buttons. The lever: one scroll and per-court action rows (the
   scene-order pins and the document fit hold the four areas today).
4. **Small reading windows** (the Cabinet's quote F15, the Dispatch F17, the Moniteur F18, the mailbox's second row
   F29): a still shows a window's first lines and its cut, and the readers mark it as clipping. The lever: reading
   windows sized to their content.
5. **The map at the whole-map zoom** (F01, 8 → 7): the names no longer overprint, but the plaques crowd the centre;
   the label layer yields 4 of 36 items (2 before).

**Built otherwise than the plan said, each with its reason:** the tooltip has no shadow (above); the objection's grid
is even only where every answer fits half a row (above); one commit, not three (above). The settlement table's four scroll areas are kept (above); the treaty tab's settlement-history rows and
the Talleyrand and Congress prose stay as lines (their url metas and pins); the Cabinet takes 70 % of the window, not
60 % (its height pins re-read); the redemption popup's Dismiss lost its red (the gilt face; one line to restore).

**Costs said once:** at the boot zoom the map's label layer yields 4 of 36 items to their neighbours (2 before) — the
plates are larger; each returns on zoom. On the user's 5120×1440 panel the interface derives 1.60, not 1.40 (logical
3200×900): the long armistice letter (PC-F46) still stands at 80 % with its whole cost above the fold, and its War
Summary, which PC-F46 put last, lies under the fold, as on any 900-px window. Each is one line to reverse
(`ULTRA_WIDE_BONUS` in both twins; the plaques' margins in `map_plaque.gd`).

**Open:** the user's own look — session H's walk reads the new desk on the frames in `docs/audits/ui_gilt2/`.

## 11. Session UI-3 — Past 7 ✅ LANDED November 12, 2026

> **The rulings** (asked in Plan Mode at the session's head, with frames and costs): lever 1, the prose on the face —
> the user's **"Fold, a switch restores"**; levers 2–4 delegated — **"DO BEST THING FOR GAME! IDC ABOUT TOKENS"** (the
> 32:9 screen), **"DO BEST"** (the settlement table), **"DO BEST OPTION"** (the windows and the map's crowding).
> Rules `SYSTEMS_REFERENCE.md` §214; pins `tests/test_ui_gilt3_folds_and_fill.py` (a headless probe,
> `tools/ui_gilt3_probe.gd`) and `tests/test_ui3_petition_figures.py`; before / after pairs `docs/audits/ui_gilt3/`.

**The rulings made under the delegation, each with its reason.** *The very wide screen* — the map fills the width
(⌂ toggles the whole sheet; Settings keeps the sheet as a choice): the readers' own lever; wider map art would need
painted terrain east and west of a crop that ends mid-land with no source PSD (a generated extension would read worse
than the desk); docking the HUD on the desk keeps the map at 45 % of the width, which is the complaint itself. *The
settlement table* — one scroll, each court's Demand / Ease / Drop as real buttons inside its own card (chips would
have lost keyboard focus, the disabled reasons and the driven probe). *The windows* — all three: reading windows fit
their content, the books take the room, crowded name plates gather at the whole-sheet view.

**As built** (one commit; seven sonnet builders on disjoint files after the lead landed the shared API, then the lead's
pass on the frames):
- **The folds** (§214): a page's lead-in behind an ⓘ at its heading; what a chip or button does as its hover, its
  figures on the face (a Vassals chip's cost, the petition's GRANT / REFUSE / LAPSE badges from a new display-only
  backend list); counsel and long prose from its first sentence, "▸ more" opened in place. Settings → INTERFACE →
  Explanations: On the page prints every word as before, byte for byte. Exempt by ruling: the Generals' reward
  explainer, first-open lines, the letters of state, the KEYS list.
- **The very wide screen:** the boot view fills the room's width at 2.6:1 and wider (5120x1440: zoom 2.0, Britain to
  Rome, the province names); ⌂ toggles the whole sheet; the boot view follows a resize until the player moves the map;
  Settings → DISPLAY → Wide map.
- **The settlement table:** a fitted head (the verdict, the beats, the treasury, the narration and advice as notes) and
  ONE body scroll — the first-open line, the courts as an accordion (the court in focus, or the first, as its whole
  card with its words and its three buttons; every other court one line with its score, its blocker and its three
  buttons, its words under its name), the table's closing line, coverage, Talleyrand's footer — and a "more below"
  strip under the scroll, never over a line; each court one line in the compact view.
- **Windows:** the Dispatch and the Moniteur open at a reading share (0.55 x 0.85, capped 900 x 1000) and fit what
  they hold; the books (both ledgers, the Generals, the log, the mailbox) at 0.62 x 0.85 (capped 1100 x 1000); the
  Cabinet's quote whole up to 40 % of the panel and the Cabinet itself 80 % of the screen's height; the mailbox's rows
  whole; Settings' scroll the page's whole room.
- **The map at the whole-sheet zoom:** a nation's touching name plates gather under their lead ("Napoleon · 2 more").

**What the frames and the instruments caught after the build**, each fixed at its cause: a straight apostrophe in a
hint printed the tag raw; the engine dash-underlined every hint; the "▸ more" link broke between its arrow and its
word; the body's "more below" tag lay over a line (it is a strip under the scroll now); a plain Control round the body
scroll left the whole-line pad nowhere to stand; a reading window's scroll minimum at the full room starved the
whole-line pad (six Dispatch frames cut their last line); the war detail's held line stood outside the tier's note;
the Settings page's scroll stood over a blank band; three whole court cards could not stand under the head at 1.0
(the accordion); the Cabinet's quote cap left the acts fewer than two rows at 2.0 (30 % there); a one-off grey the consistency census had passed by a mis-scanned
span (`MAP_CIRCLE_RIM`).

**The interim reading** (three fresh sonnet readers on the shoot, before the record; one reader's labels slipped a
frame from F15 on and its marks were set aside; the other two read 6.5 and 6.8, overall 7 and 7). What they named was
fixed at its cause before the final reading: the Balance's road cards drew their rules through each other's words
(every page's cards now reach into a neighbouring paragraph only when it is blank); the Cabinet's counsel ran into a
clipped scroll (it opens from the Recommendation's first sentence, and the Cabinet takes 80 % of the screen's height,
up from 70 %); the settlement's tail was a paragraph of instructions (it opens from its first sentence; a blank line
parts the first-open line from THE TABLE); the region panel's refused levies stood one bare chip a line (one row).

**The measure** — all 185 surfaces at Interface Scale 1.0 and 2.0 and at the five physical sizes (1,295 frames, 0
script errors): readability RED 0 / P1 0 (5,181 rows scaled, 13,028 physical); contrast 0 rows under 4.5 : 1 (4,168
and 11,250 measured); consistency 0 hits on 145 surfaces; fit 185 / 185; map overlaps 0; cut lines 53 against HEAD's
63, hidden map furniture 91 against 107. On the page, 181 of 185 surfaces keep HEAD's raw BBCode byte for byte — the
settlement table's three frames by its new structure, and the enemy phase by a line ending (a string literal written
across a line break; the file untouched, the words identical). Every changed surface read at 2.0. The figures and the
method: `SYSTEMS_REFERENCE.md` §214.

**The score** — three fresh sonnet readers, the frozen rubric, the prompt verbatim, the same 30 frames (pairs
`docs/audits/ui_gilt3/`; `tools/ui_rating/scores_ui3.py`):

| Reading | Overall | Mean of the marks | Median of frame medians |
|---|---|---|---|
| UI-2's after (the base, HEAD `8db8d10c`) | 7 / 7 / 7 | 6.93 | 7 |
| UI-3 interim (two readers; a third set aside) | 7 / 7 | 6.65 | 7 |
| **UI-3 final** | **7 / 7 / 7** | **7.00** | **7** |

**The overall marks did not pass 7.** Five frames rose (the 32:9 war room 6 → 7, Nations 6 → 8, Vassals 6 → 7, the
settlement table 5 → 6, the petition 6 → 7), three fell (Forces 8 → 7, the untouched main menu 8 → 7, the mailbox
8 → 7), 22 held; the readers agreed closely (19 frames unanimous, 11 one apart). One frame of an unchanged surface
moving a point is the instrument's own noise floor — a mean shift under a third of a point is within it.

**What holds it at 7 now** (the final readers' own reasons, by theme, frame ids as in the pairs): small body type and
text-heavy bodies across the ledgers and popups (all three OVERALL lines); the four frames all three marked 6 or
less — the Balance of Europe (F13: "make the coalition threat a large gauge and the designs progress cards"), the
region panel (F24: shot alone without the map, its chips small and ragged), the war detail (F25: "the score breakdown
as bars"), the settlement table (F16, 7 / 6 / 6: "a compact table with one status line per court"); on 32:9 the HUD's
panels cluster small in the middle of the filled map (F02: "anchor HUD elements to the screen edges"); at 2.0 the
command panel's prose stands clipped mid-sentence (F03); disabled and live buttons read alike (F10, F12) and the main
menu's buttons read as disabled (F27). These are the levers past 7 — the user's to rule (`docs/STATUS.md`, "Open with
you").

**Costs said once:** a first-time player meets explanations a hover or click away (On the page restores every word);
on the user's 5120x1440 the map opens magnified 2x with 55 % of its height off screen — ⌂ or Settings for the whole
sheet — its province edges as today's zoom-in draws them; at the whole-sheet zoom a crowded front shows one plate.
