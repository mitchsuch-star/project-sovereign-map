# UI Visual Foundation Sweep — Spec

> **Status:** ▶ NEXT (queued July 12, 2026). Design proposal + all third-party assets
> already gathered and license-verified; build not yet started.
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

> **Status:** researched + design-recommended July 12, 2026; needs a small style gate before art.
> **Decision locked:** **no camera tilt** → **baked 2.5D pieces on the existing 2D map** (additive
> layer; the mature map / DEF-9..13 stays untouched). Real-time 3D was rejected for map pieces
> (a static piece gains nothing from it) — the win is dimensional pieces baked to sprites.
> **Reference artifacts:** the "War Table — Pieces & the 2.5D Pipeline" style guide and the
> "Visual Foundation" proposal (both generated this session). Research sources: Kriegsspiel
> (kriegsspiel.org, Wikipedia), tin flats/Zinnfiguren (Wikipedia *Toy soldier*), round soldiers
> (Lucotte, W. Britain), Napoleon's 1805 pin table (Bacler d'Albe, frenchempire.net).

**Goal:** physical "war-table" pieces — one each for **infantry / cavalry / artillery** — that a
marshal pushes across the map, like Kriegsspiel or a diorama. Color = side is universal; branch
always needs a second channel.

**Recommended style (gate item G1):** a **round sculpt on a Kriegsspiel-shaped base, faction-tinted.**
The sculpt gives the diorama look + the volume a baked contact shadow needs; the base footprint
restores the *shape* channel that rescues the weak lone-infantry read; the tint codes the side.
Ranked fallbacks: pure Kriegsspiel blocks (safe/cheap) → pure round soldiers → tin flats (fights
2.5D) → flags/pins (no branch info; keep as a secondary objective/HQ layer only).

**Per-arm spec — three redundant legibility channels** (base footprint + silhouette + faction color),
so any two can fail at 48–64px and it still reads:
- **Infantry** — widest/longest base; rank of 2–3 shako figures + flag → *wide vertical bristle*.
- **Cavalry** — compact square base; single mounted rider, sabre up, taller → *tall organic mass*.
- **Artillery** — smallest base; cannon (barrel + one big wheel), one gunner → *low horizontal wheel*.
- Matched-set rules: identical base height/bevel, identical baked shadow, one shared light + fixed
  3/4 angle, matte toy-paint. One piece = one corps (inf/art are small clusters, never a lone man).
  No fine detail at 64px — strength/facings/pips live in hover/zoom.

**2.5D render pipeline** (model in 3D, bake to a flat sprite once — 2D at runtime):
1. Model piece in Blender (round sculpt + shaped base; CC0 base mesh kitbash or low-poly primitives).
2. ONE **orthographic** camera at a fixed ~45° 3/4 angle, shared by all pieces (ortho = no
   position-dependent distortion across the map).
3. Light once (fixed key + soft fill) → bakes volume + guarantees a matched set.
4. Bake the **contact shadow as a separate sprite** (shadow-catcher / AO pass) — it glues the piece
   to the table.
5. Render PNG+alpha at 2–3× size. Optional neutral **tint-mask** so ONE render recolors to all 20
   nations via `modulate` (reuse `Utils.NATION_COLORS`); optional 4–8 facing angles.
6. Godot: `Sprite2D` at the province anchor + shadow child; **Y-sort** for fake depth; **tween**
   position along the march path for the "sliding piece" feel. The 2D map is unchanged.

**Tooling — how it gets built:** Blender is Python-scriptable (`bpy`) and runs headless
(`blender --background --python`), so the render RIG (camera/light/shadow), materials, faction-tint
batch, geometric pieces (bases, cannon, blocks), batch-rendering, and the Godot placement code are
**fully automatable + iterable** (render → inspect PNG → adjust). Detailed *organic* sculpts
(realistic horse/soldier) come from a CC0 base mesh or an artist; a **stylized low-poly / carved-toy**
look is fully script-generatable and reads well small — **gate item G2: hybrid-realistic (CC0 meshes)
vs. stylized-low-poly (fully generated).**

**Effort:** ~2–4 days art (3 pieces + one reusable render rig) · 1 code slice (placement/Y-sort/
tween, additive to the 2D map) · ~free runtime (baked sprites).

**Open gate items (decide before art):** G1 style (hybrid vs pure Kriegsspiel) · G2 realism path
(CC0-mesh vs low-poly) · G3 tint-mask-recolor vs per-faction render.

**Completion definition:** the three arm pieces render as baked PNG+alpha sprites with a separate
contact shadow, faction-tint working via `modulate`, placed + Y-sorted on the map at marshal
locations and tweening on move; the 2D map/zoom/labels untouched (0 `SCRIPT ERROR`).

**Test:** extend `tests/test_ui_visual_foundation.py` — assert the 3 piece sprites (+ shadow) exist
in `assets/ui/pieces/` and that each active marshal renders a piece keyed to its dominant arm.
