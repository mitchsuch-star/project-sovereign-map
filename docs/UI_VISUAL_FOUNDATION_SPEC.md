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
> (Session Segmentation Ledger)** — U1 + U2 (Parts 1, 2, 2c) done, resume at **U3** (texture / border /
> icon / portrait polish).
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

### Session U3 — UI-3: texture / border / icon / portrait polish (excludes pieces)
- **Entry:** U2 landed.
- **Spots checklist:**
  - [ ] Parchment/leather panel fills; convert war-room / dispatch / ledger panels to `StyleBoxTexture` 9-slice frames.
  - [ ] Filigree corners on marshal cards.
  - [ ] Wire the Phosphor + Game-icons sets onto their target HUD/buttons (strip the Game-icons 512² black bg `<path>`, recolor gold via `modulate`); add the Game-icons + Lamoot **CC-BY visible credit** if those assets ship.
  - [ ] Wire the 37 portraits into the Generals screen + character-sheet cards; **Abdurrahman → monogram/silhouette fallback** (graceful, no wrong likeness).
  - [ ] Boot engine → `grep SCRIPT ERROR` == 0.
- **Exit:** UI-3 completion definition (§4).
- **STATUS line:** record UI-3 base-polish landing.

### Session U4 — War-Table Pieces ART (tin-flat-on-round-base, Blender)
- **Entry:** U1 landed (independent of U2/U3; recommended after U3). Reference set = §7.
- **Spots checklist:**
  - [ ] Build the Blender rig: **locked dead-broadside** ortho camera, single low-angle key + soft fill, shadow-catcher plane.
  - [ ] Author 3 broadside textures — infantry (rank + taller colour bearer) / cavalry (horse+rider, sabre raised) / artillery (gun + big spoked wheel + trail + 1–2 crew) — traced from the §7 PD Zinnfiguren refs; matte enamel + engraved-line rim.
  - [ ] Round base disc primitive (3 footprint sizes) + diametral slot; **line-shaped** contact-shadow bake.
  - [ ] Neutral **coat tint-mask**; base + metal on neutral channels.
  - [ ] **Mirrored L/R facing pair** per arm.
  - [ ] Export PNG+alpha (2–3×) → `assets/ui/pieces/` (figure + base + shadow + mask, per arm × 2 facings).
  - [ ] Add the CC-BY reference attributions (Plassenburg/Quine, Liljedahl, Roscheider Hof, Goslar, Schweizer) to `THIRD_PARTY_LICENSES.md` if any art is traced from them.
- **Exit:** all sprites present in `assets/ui/pieces/` per the naming above.
- **STATUS line:** record the piece-art landing + attribution updates.

### Session U5 — War-Table Pieces CODE (Godot placement)
- **Entry:** U4 art exists.
- **Spots checklist:**
  - [ ] `Sprite2D` (flat) + round-base child + shadow child at each active marshal's province anchor, keyed to dominant arm.
  - [ ] **Y-sort** for depth; **tween** position along the march path on move; **flip facing** by travel heading.
  - [ ] Faction `modulate` on the coat mask via `Utils.NATION_COLORS`.
  - [ ] Additive layer — the 2D map / zoom / labels untouched.
  - [ ] Boot engine → `grep SCRIPT ERROR` == 0.
  - [ ] Extend `tests/test_ui_visual_foundation.py`: the 3 flat sprites (+ base + shadow, both facings) exist; each active marshal renders a piece keyed to its dominant arm.
- **Exit:** §7 pieces completion definition.
- **STATUS line:** record the pieces-code landing; the War-Table Pieces sub-item CLOSED.
