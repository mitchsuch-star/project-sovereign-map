# Third-Party Asset Licenses — Project Sovereign

All UI assets below live under `godot-client/project-sovereign/assets/`. Every license
and source URL was verified against its live source page before download.

**Git-tracking policy (UI-0, July 12, 2026):** the `assets/` directory is blanket
git-ignored, but the **usable shipped assets are force-tracked** (`git add -f`) so the repo
is self-contained and the portability tests pass on any clone — fonts (`.ttf` + `OFL.txt`),
portraits, icon/border/heraldry/ornament/decor SVG+PNG+JPG, the two icon `LICENSE` files,
textures, and the unpacked audio files (as of the August 7, 2026 Music & Sound sourcing
pass: **75 cue-named audio files across `audio/{music,ui,battle,ambient}/` + their
`.import` sidecars are force-tracked**; the bulk of the Kenney/bang pools remains INSIDE
the untracked zips). **Deliberately NOT tracked** (remain ignored to
keep git history lean): the working `*.zip` master pools, the source `*.psd` files, and the
stray `movies.avi`. Adding a new asset to a tracked subdir therefore needs another `git add -f`.
Godot `.import` sidecars are generated + committed in UI-1 (the editor has not imported yet).

**Attribution obligations at a glance:** the fonts, textures, icons, audio, flags,
ornaments, and portraits require **no in-game credit** except three items. The **only**
assets that require a visible/bundled credit are **Game-icons.net**, the
**RPG GUI Construction Kit (Lamoot)**, and the **musket-volley battle sound
(aaronsiler & Benboncan, CC-BY 4.0)** — see the CC-BY section.

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
| UI Pack (RPG Expansion) — bar frames + fills (`assets/ui/bars/`) | Kenney — https://kenney.nl/assets/ui-pack-rpg-expansion |
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

## Audio — `assets/audio/` (CC0 / PD except ONE CC-BY file, flagged)

**Full cue map + per-file inventory: `docs/MUSIC_SOUND_SPEC.md`** (the Music & Sound
sourcing pass, August 7, 2026). Summary of provenance families:

**Master pools on disk (untracked zips, CC0):** Kenney Interface Sounds + Kenney RPG
Audio (https://kenney.nl), OpenGameArt "25 CC0 bang/firework sfx"
(https://opengameart.org/content/25-cc0-bang-firework-sfx). 28 files are extracted
unmodified and cue-renamed into `ui/`, `battle/`, `ambient/` (the `cannon_thud.ogg`
precedent — e.g. `click_primary.ogg` = Interface `click_002`, `page_turn_1.ogg` =
RPG `bookFlip1`, `musket_shot_1.ogg` = bang-pack `shot_01`). CC0, no attribution.

**`music/` (August 7, 2026 — 18 tracks, all PD/CC0 RECORDINGS, verified per file):**
- Musopen Kickstarter-commissioned recordings, released to the public domain
  (archive.org item `MusopenCollectionAsFlac`, licenseurl PD Mark): Beethoven *Eroica*
  mvts I/II/IV, *Coriolan* Overture, Haydn *Lark* Adagio, Mozart Sym. 40 Andante.
- Open Goldberg Variations (Kimiko Ishizaka), **CC0** (archive.org
  `OpenGoldbergVariations`): Goldberg Aria.
- **US federal-government works (PD):** La Marseillaise — United States Navy Band
  (Wikimedia Commons `La_Marseillaise.ogg`, sourced from navyband.navy.mil);
  *Marche militaire française* — "The President's Own" US Marine Band (archive.org
  `Retrospective_738`); five US Army Old Guard Fife & Drum Corps tracks (archive.org
  `Celebrating_50_Years-9015`, PD-marked): Brandywine Quickstep, two field-music
  medleys, The Rage of Cornwallis, ERAFNAF Fanfare; four US military bugle calls
  (Wikimedia Commons): First Call, Reveille, Mail Call, To the Color.

**Sourced SFX (August 7, 2026 — freesound.org CC0 previews unless noted, each
sound page's CC0 status independently verified by an adversarial license pass):**
`ui/` quill-scribble loop + long take, quill flick, signature, wax seal, letter
open, paper crumple, desk notification bell, coin pour, end-turn snare roll;
`battle/` cavalry gallop, sword draw, two marching-feet takes, Revolutionary-War
reenactment battlefield ambience (uploader's own field recording), horse whinny
(Wikimedia Commons PD `Wiehern.ogg`); `ambient/` church-bell peal, single toll,
ship's bell, sea surf, campfire loop, wind loop, crowd walla.
**Provenance rule applied:** uploads by freesound user *craigsmith* (digitized
Hollywood tape libraries mislabelled CC0) were rejected wholesale.

**`battle/musket_battle_volley.mp3` is the ONE exception — CC-BY 4.0, credit
required** (see the CC-BY section).

**Self-authored (CC0-clean):** `battle/drum_sting.wav`, synthesized deterministically
by `tools/gen_battle_audio.py`.

## Heraldry — `assets/ui/heraldry/` (Public Domain, Wikimedia + original)

26 period national flags, named `<Nation>.svg` — the 20 for the 1805 boot roster, plus 6
for nations that can only come into existence during a campaign (NA-6a/6b's Italy and United
Netherlands; NA-6c's Duchy of Warsaw, Poland, Duchy of Normandy and Roman Republic).

Of the NA-6c four, three are original simplified geometric renderings authored in-repo
July 19, 2026 — Polish white-over-red, the same bicolour under a gold crown for Poland, and
the 1798 Roman Republic's black-white-red vertical tricolour (simple heraldic geometry
carries no copyright). **`Normandy.svg` is adapted from a public-domain source**, following
the same provenance pattern as `Hanover.svg`: the two leopards passant guardant are taken
from **"Flag of Normandie.svg"** (Wikimedia Commons, uploaded 2009-04-02 by **Saebhiar**,
released into the **public domain worldwide** by the copyright holder — PD-self;
`https://commons.wikimedia.org/wiki/File:Flag_of_Normandie.svg`). Adapted for this project:
the source 3:2 canvas re-fitted to the set's 500×300, its own field rect replaced by one in
the game palette red, and the gold recoloured `#fcd41c` → `#e8b923` to match the rest of the
set; the azure tongue and dark outline are kept, since "armed and langued azure" is the
correct blazon and the outline is what lets the charge read at 44px. Public domain — no
attribution required, credited here as a matter of record. (Five hand-authored drafts
preceded it; see `NATION_AGENDAS_SPEC.md` §20.2 for why sourcing won.)

The boot roster (France, Britain 1801 Union, Austria, Russia,
Prussia, Spain, Naples, Bavaria, Sweden, Denmark, Portugal, Holland, Papal States,
Sardinia — Wikimedia PD; plus Hanover, Hesse, Kingdom of Italy, Switzerland, Ottoman, Saxony —
original simplified geometric renderings authored in-repo July 16, 2026, matching the set's
flat style; simple heraldic geometry carries no copyright). Public
domain — no attribution required. **Date-accuracy pass (July 16, 2026):** Hanover redrawn as
the Electorate's white Saxon Steed on red (the white-over-yellow bicolor is the post-1814
Kingdom flag), Ottoman's 5-point star replaced with the 8-point star of Selim III's 1793
naval ensign (5-point is the 1844 Tanzimat design), Saxony redrawn as the Electorate's
banner of arms — barry sable/or with the green crancelin bend (white-over-green is the
1815+ Kingdom bicolor). Kept-as-authored judgment calls: Switzerland's white cross on red
(the 1803–13 Mediation era had no federal flag; the cross is the medieval confederate war
sign), Naples' Angevin azure semé-de-lis with red label (the 1805 Bourbon state flag was
plain white with arms — illegible at thumbnail size). **Hanover steed upgrade (July 16,
2026):** the hand-drawn horse was replaced with the detailed heraldic Saxon Steed adapted
from Wikimedia Commons "Flag_of_Twente.svg" (released into the public domain worldwide by
its author; the Twente flag carries the same Saxon Steed emblem lineage), rescaled onto the
game-palette red field in `Hanover.svg`. Public domain — no attribution required.

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
- **Musket battle volley** (`assets/audio/battle/musket_battle_volley.mp3`) — CC-BY 4.0.
  Required form: *"Musket battle sounds by aaronsiler & Benboncan (freesound.org), CC BY 4.0"*
  (the compilation's ricochets derive from Benboncan's CC-BY sounds, so BOTH are credited).
  https://freesound.org/people/aaronsiler/sounds/128981/ — if this file is ever dropped,
  drop the credit line with it.

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
