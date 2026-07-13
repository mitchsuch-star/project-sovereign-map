# Third-Party Asset Licenses — Project Sovereign

All UI assets below live under `godot-client/project-sovereign/assets/`. Every license
and source URL was verified against its live source page before download.

**Git-tracking policy (UI-0, July 12, 2026):** the `assets/` directory is blanket
git-ignored, but the **usable shipped assets are force-tracked** (`git add -f`) so the repo
is self-contained and the portability tests pass on any clone — fonts (`.ttf` + `OFL.txt`),
portraits, icon/border/heraldry/ornament/decor SVG+PNG+JPG, the two icon `LICENSE` files,
textures, and audio WAVs (198 files, ~77 MB). **Deliberately NOT tracked** (remain ignored to
keep git history lean): the working `*.zip` master pools, the source `*.psd` files, and the
stray `movies.avi`. Adding a new asset to a tracked subdir therefore needs another `git add -f`.
Godot `.import` sidecars are generated + committed in UI-1 (the editor has not imported yet).

**Attribution obligations at a glance:** the fonts, textures, icons, audio, flags,
ornaments, and portraits require **no in-game credit** except two items. The **only**
assets that require a visible/bundled credit are **Game-icons.net** and the
**RPG GUI Construction Kit (Lamoot)** — see the CC-BY section.

---

## Fonts — SIL Open Font License 1.1

Free to embed and ship. Obligation: bundle each family's `OFL.txt` (already saved beside
the `.ttf` in `assets/fonts/`). No in-game credit. Do not reuse a Reserved Font Name if modified.

| Family | Source |
|--------|--------|
| Cinzel | https://fonts.google.com/specimen/Cinzel |
| Marcellus SC | https://fonts.google.com/specimen/Marcellus+SC |
| Playfair Display | https://fonts.google.com/specimen/Playfair+Display |
| Cormorant Garamond | https://fonts.google.com/specimen/Cormorant+Garamond |
| IM Fell English | https://fonts.google.com/specimen/IM+Fell+English |
| UnifrakturMaguntia | https://fonts.google.com/specimen/UnifrakturMaguntia |
| EB Garamond | https://fonts.google.com/specimen/EB+Garamond |
| Source Sans 3 | https://fonts.google.com/specimen/Source+Sans+3 |
| Source Serif 4 | https://fonts.google.com/specimen/Source+Serif+4 |
| Spectral | https://fonts.google.com/specimen/Spectral |
| Libre Caslon Text | https://fonts.google.com/specimen/Libre+Caslon+Text |
| Alegreya Sans | https://fonts.google.com/specimen/Alegreya+Sans |
| Fira Sans | https://fonts.google.com/specimen/Fira+Sans |

---

## Textures & Borders — CC0 1.0 (public domain, no attribution required)

| Asset | Author / Source |
|-------|-----------------|
| Paper 001, Paper 005, Leather 026 | ambientCG — https://ambientcg.com |
| Fabric Leather 01 | Poly Haven — https://polyhaven.com/a/fabric_leather_01 |
| Paper Textures Seamless | Leschge — https://opengameart.org/content/paper-textures-seamless |
| Old Parchment Paper | cron — https://opengameart.org/content/old-parchment-paper |
| Fantasy UI Borders | Kenney — https://kenney.nl/assets/fantasy-ui-borders |
| UI Pack | Kenney — https://kenney.nl/assets/ui-pack |
| Golden UI | Buch — https://opengameart.org/content/golden-ui |
| Card Template | Cethiel — https://opengameart.org/content/card-template-0 |
| Buttons and Frame | https://opengameart.org/content/buttons-and-frame |

---

## Icons — curated two-set system (July 12, 2026 curation pass)

The first-pass grab of six generic packs was pruned to a **thematic core + neutral UI companion**.

| Set | License | Location | Role | Credit |
|-----|---------|----------|------|--------|
| **Phosphor Icons** (Regular) | MIT | `assets/ui/icons/phosphor/` (51 SVG) | Neutral UI chrome — menus, carets, arrows, gear/search/info/warning, save/load, tabs | Retain `LICENSE`; no in-game credit |
| **Game-icons.net** (curated) | CC-BY 3.0 | `assets/ui/icons/game-icons/` (24 SVG) + `_packs/game-icons-net.zip` (master pool) | Thematic core — units, combat actions, economy, diplomacy | **Visible credit required — see CC-BY** |

**Dropped in the curation pass (not shipped):** Lucide, Tabler, Iconoir, Feather (redundant
generic line sets), Font Awesome Free (generic + attribution burden). Their zips were deleted.

**Recolor note:** each Game-icons SVG ships a black `512×512` background square — strip the first
`<path>` and set the foreground to `currentColor`/`modulate` to tint gold-on-navy. Phosphor is
already drop-in recolorable.

---

## Audio — `assets/audio/ui/` (CC0 — no attribution)

Kenney Interface Sounds + RPG Audio (CC0), an OpenGameArt CC0 cannon/bang pack, and two CC0
parchment open/close WAVs. Covers click/hover/confirm/error, coins, cloth, distant cannon,
panel open/close. Gaps (deferred, not blocking): a drum/fife turn-start sting, dedicated
quill-scratch, dedicated wax-seal stamp — approximated from the RPG pack for now.

## Heraldry — `assets/ui/heraldry/` (Public Domain, Wikimedia)

16 period national flags for the 1805 roster (France, Britain 1801 Union, Austria, Russia,
Prussia, Spain, Naples, Bavaria, Sweden, Denmark, Ottoman, Portugal, Holland, Papal States,
Sardinia, Saxony), named `<Nation>.svg`. Public domain — no attribution required.

## Ornaments & map decor — `assets/ui/ornaments/`, `assets/ui/decor/`, `assets/textures/decor/` (CC0 / PD)

Flourishes, laurel wreaths, corner filigree, fleurons, a wax-seal graphic; an antique compass
rose (1595), a Cassini cartouche (1744), an ornamental frame, antique parchment, and Kenney
smoke/dust particle PNGs. All CC0 or public domain — no attribution required.

---

## CC-BY — **visible attribution required if these ship**

Credit these in an in-game credits screen and/or this file. Only required for the specific
icons/borders actually used in the shipped build.

- **Game-icons.net** (thematic icons) — CC-BY 3.0. Per-icon authors differ.
  Required form: *"Game icons by Lorc, Delapouite & contributors (game-icons.net), CC BY 3.0"* —
  track which icons ship. https://game-icons.net
- **RPG GUI Construction Kit** — CC-BY 3.0.
  Required form: *"RPG GUI by Matjaž Lamut (Lamoot), CC BY 3.0"*.
  https://opengameart.org/content/rpg-gui-construction-kit-v10

---

## Marshal Portraits — Public Domain (PD-art), via Wikimedia Commons

37 portraits in `assets/portraits/`, named by the game's internal marshal key
(e.g. `Ney.jpg`, `Wellesley.jpg` = Arthur Wellesley / Duke of Wellington,
`Frederick.jpg` = Frederick VI of Denmark). All are 19th-century painted portraits in
the public domain (PD-art). No legal attribution required; courtesy credit: "Portraits
via Wikimedia Commons (public domain)."

Not downloaded: **Abdurrahman** (Ottoman roster entry) — no confident public-domain
portrait of the correct historical figure was found; left unillustrated by design
rather than risk a wrong likeness.

---

## War-Table Pieces — ORIGINAL generated art (`assets/ui/pieces/`)

The infantry / cavalry / artillery "tin flat" map pieces — 24 sprites named
`{arm}_{layer}_{facing}.png` (layers: base / shadow / coat / body; facings r, l)
— are **100% original art**, generated procedurally by
`tools/gen_war_table_pieces.py`. **No third-party pixels are used or derived** —
every silhouette is drawn from scratch. They carry no license encumbrance and
need no attribution.

**Courtesy reference-inspiration note (no texel copied):** the Zinnfigur
"flat"/*standee-on-a-round-base* aesthetic was studied from — but no pixels
taken from — these public reference sets: Plassenburg Zinnfiguren-Museum /
Thomas Quine (CC BY 2.0), Louis Liljedahl 30 mm Napoleonic flats (CC BY-SA 3.0),
Roscheider Hof (CC BY 4.0), Zinnfiguren-Museum Goslar (CC BY-SA 3.0), and the
W. Schweizer engraved slate mould (CC BY-SA 4.0). Per `UI_VISUAL_FOUNDATION_SPEC`
§7 these credits become a *required* attribution only if a future revision
directly derives pixels from a reference image.
