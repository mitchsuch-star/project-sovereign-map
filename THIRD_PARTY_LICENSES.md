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

Free to embed and ship. Obligation: bundle each family's `OFL.txt` (saved beside
the `.ttf` in `assets/fonts/` in the source tree).

**In the shipped build these travel to `licenses/fonts/`, and the other two
families' notices to `licenses/`** — `deploy/build.bat` copies them and
`tests/test_fa_slice13_shipping_2026_09_05.py` derives the census from
`git ls-files`, so a new notice that is not carried reds the suite. This
paragraph is the THIRD credit surface (with the in-game Settings screen and
`README_TESTER.txt`); before FA-43/FA-N84 all three pointed at a directory
that was not in the zip. No in-game credit. Do not reuse a Reserved Font Name if modified.

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
| **Phosphor Icons** (Regular) | MIT | `assets/ui/icons/phosphor/` (52 SVG — `lock-simple.svg` added by Session UI-4) | Neutral UI chrome — menus, carets, arrows, gear/search/info/warning, save/load, tabs | Retain `LICENSE`; no in-game credit |
| **Game-icons.net** (curated) | CC-BY 3.0 | `assets/ui/icons/game-icons/` (24 SVG) + `_packs/game-icons-net.zip` (master pool) | Thematic core — units, combat actions, economy, diplomacy | **Visible credit required — see CC-BY** |

| **The stat glyphs** (Session UI-2, November 11, 2026) | CC-BY 3.0 (Game-icons.net) | `assets/ui/icons/glyphs/` (36 SVG, extracted unmodified from `_packs/game-icons-net.zip`, the black fill turned white for `modulate`; each `.import` mipmapped so it renders at 16–28 px) | One glyph per category — gold, DP, authority, threat, foot / horse / guns, the six marshal skills, garrison, supply, stability … | **Visible credit required — see CC-BY.** Per-glyph source icon and author: `assets/ui/icons/glyphs/GLYPHS.txt` (Lorc, Delapouite, Skoll, Sbed, HeavenlyDog) |

**Self-authored (CC0-clean):** `assets/ui/icons/ui5_caret_down.svg` — the dropdowns' gold
caret (Session UI-5, November 13, 2026; one stroked path drawn for this game, the theme's
`OptionButton/icons/arrow`).

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
(https://opengameart.org/content/25-cc0-bang-firework-sfx). 33 files are extracted
unmodified and cue-renamed into `ui/`, `battle/`, `ambient/` (the `cannon_thud.ogg`
precedent — e.g. `click_primary.ogg` = Interface `click_002`, `page_turn_1.ogg` =
RPG `bookFlip1`, `musket_shot_1.ogg` = bang-pack `shot_01`; **Aug 8, 2026 re-cue
pass:** `wood_tap_1/2/3.ogg` = RPG `bookPlace1/2/3`, `leather_tap_1/2.ogg` = RPG
`handleSmallLeather/2` — the new thematic button-click / row-select cues). CC0,
no attribution.

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

### Session UI-5 (November 12, 2026) — the full measure's new sounds

Every file below was sourced for Session UI-5 (`docs/MUSIC_SOUND_SPEC.md` §6) and
checked on its own page; the August rules hold (CC0 / public domain only; no
*craigsmith* upload; no re-digitized studio tape; an AI-generated candidate was
refused on provenance). Freesound files are the public HQ previews, unmodified.

**Foley and beds (freesound.org, CC0 — "Creative Commons 0" on each sound's page):**

| File | What | Uploader · page |
|---|---|---|
| `ambient/fire_loop.ogg` | fireplace crackle (the study's bed) | AlexanderChe · https://freesound.org/people/AlexanderChe/sounds/410404/ |
| `ambient/clock_loop.ogg` | a clock ticking, seamless loop | seth-m · https://freesound.org/people/seth-m/sounds/321582/ |
| `ambient/birds_loop.ogg` | spring countryside birds | BurghRecords · https://freesound.org/people/BurghRecords/sounds/456122/ |
| `ambient/rain_loop.ogg` | light rain on a window | derjuli · https://freesound.org/people/derjuli/sounds/824126/ |
| `ambient/winter_wind_loop.ogg` | a cold wind's howl | Kodack · https://freesound.org/people/Kodack/sounds/256862/ |
| `ambient/distant_drums.ogg` | snare rolls heard far off | aUREa · https://freesound.org/people/aUREa/sounds/475246/ |
| `ambient/crowd_cheer.ogg` | a crowd cheering | misjoc · https://freesound.org/people/misjoc/sounds/400590/ |
| `ui/door_knock.ogg` | a double knock on a wooden door | aoimotion · https://freesound.org/people/aoimotion/sounds/728289/ |
| `ui/gavel.ogg` | a wooden gavel (the first strike is played) | Aerny · https://freesound.org/people/Aerny/sounds/618138/ |
| `ui/quill_strokes.ogg` | a dry pen on paper (the typing nib) | UnderASpell · https://freesound.org/people/UnderASpell/sounds/611719/ |
| `ui/paper_slide.ogg` | a sheet slid across a desk | semccab · https://freesound.org/people/semccab/sounds/154403/ |
| `battle/horse_trot.ogg` | a horse's trot (foley) | oscarius3 · https://freesound.org/people/oscarius3/sounds/810320/ |
| `battle/hammer.ogg` | a hammer on a nail in wood | L.i.Z.e.L.l.E_+ · https://freesound.org/people/L.i.Z.e.L.l.E_+/sounds/707864/ |
| `battle/saw.ogg` | a hand saw through wood | Mateusz_Chenc · https://freesound.org/people/Mateusz_Chenc/sounds/519661/ |
| `battle/spade_dig.ogg` | a spade digging | rvdw2004 · https://freesound.org/people/rvdw2004/sounds/709677/ |
| `battle/drum_cadence.ogg` | a slow snare march beat | CVLTIV8R · https://freesound.org/people/CVLTIV8R/sounds/809828/ |
| `battle/boots_halt.ogg` | a boot's stamp | locky_Y · https://freesound.org/people/locky_Y/sounds/733165/ |

**Kenney Interface Sounds (CC0, the on-disk zip, extracted unmodified):** `ui/hover_tick.ogg`
(`tick_001`), `ui/hover_tick_2.ogg` (`tick_002`).

**Derived (CC0 / as their sources):** `ui/quill_scribble_loop_seamless.ogg` and
`ui/quill_scribble_long_seamless.ogg` — the August quill takes with their tails
crossfaded into their heads by `tools/ui5_audio_prep.py --make-loop` (the loops
stepped 21–24 dB where they wrapped).
Re-made the same way (November 13), the loops whose wraps stepped 8–30 dB or clicked:
`ambient/crowd_murmur_seamless.ogg`, `ambient/fire_loop_seamless.ogg`, `ambient/rain_loop_seamless.ogg`,
`ambient/winter_wind_loop_seamless.ogg`, `ambient/ship_creak_1_seamless.ogg`,
`battle/army_march_loop_short_seamless.ogg`, `battle/battlefield_ambience_seamless.ogg` — each as its
source (CC0 / the CC0 freesound takes above / the August files' families).

**Music, anthems and bugle calls (Session UI-5) — every recording public domain, checked on its own page:**

| File | What | Performer · licence · page |
|---|---|---|
| `music/war_egmont.ogg` | Beethoven, *Egmont* Overture, Op. 84 | Czech National Symphony Orchestra (as Musopen Symphony) · recording released to the public domain by Musopen (Commons `PD-author`), composition PD-old · https://commons.wikimedia.org/wiki/File:Beethoven_-_Egmont_Overture,_Op._84_(Musopen_Symphony).flac |
| `music/war_eroica_iii.ogg` | Beethoven, Symphony No. 3 *Eroica* — III. Scherzo | Czech National Symphony Orchestra (as Musopen Symphony) · recording released to the public domain by Musopen (Commons `PD-author`), composition PD-old · https://commons.wikimedia.org/wiki/File:Beethoven_-_Symphony_No._3_in_E_flat_major,_Op._55_'Eroica'_-_III._Scherzo._Allegro_vivace_(Musopen_Symphony).flac |
| `music/crisis_mozart40_i.ogg` | Mozart, Symphony No. 40, K550 — I. Molto allegro | Musopen Symphony · recording released to the public domain by Musopen (Commons `PD-author`), composition PD-old · https://commons.wikimedia.org/wiki/File:Mozart_-_Symphony_No._40_in_G_minor,_K550_-_I._Molto_allegro_(Musopen_Symphony).flac |
| `music/court_figaro_overture.ogg` | Mozart, *Le nozze di Figaro*, K492 — Overture | Musopen Symphony · recording released to the public domain by Musopen (Commons `PD-author`), composition PD-old · https://commons.wikimedia.org/wiki/File:Mozart_-_Le_nozze_di_Figaro,_K492_-_Overture_(Musopen_Symphony).flac |
| `music/court_mozart40_iii.ogg` | Mozart, Symphony No. 40, K550 — III. Menuetto | Musopen Symphony · recording released to the public domain by Musopen (Commons `PD-author`), composition PD-old · https://commons.wikimedia.org/wiki/File:Mozart_-_Symphony_No._40_in_G_minor,_K550_-_III._Menuetto._Allegretto_(Musopen_Symphony).flac |
| `music/court_haydn_lark_i.ogg` | Haydn, String Quartet Op. 64 No. 5 *The Lark* — I. Allegro moderato | Musopen String Quartet · recording released to the public domain by Musopen (Commons `PD-author`), composition PD-old · https://commons.wikimedia.org/wiki/File:Haydn_-_String_Quartet,_Op._64_No._5_in_D_major_'The_Lark'_-_I._Allegro_moderato_(Musopen_String_Quartet).flac |
| `music/court_mozart_quartet.ogg` | Mozart, String Quartet No. 15, K421 — III. Menuetto | Musopen String Quartet · recording released to the public domain by Musopen (Commons `PD-author`), composition PD-old · https://commons.wikimedia.org/wiki/File:Mozart_-_String_Quartet_No._15_in_D_minor,_K421_-_III._Minuetto_(Allegretto)_(Musopen_String_Quartet).flac |
| `music/court_beethoven_op18_6_ii.ogg` | Beethoven, String Quartet Op. 18 No. 6 — II. Adagio ma non troppo | Musopen String Quartet · recording released to the public domain by Musopen (Commons `PD-author`), composition PD-old · https://commons.wikimedia.org/wiki/File:Beethoven_-_String_Quartet_No._6_in_B_flat_major,_Op._18_No._6_-_II._Adagio,_ma_non_troppo_(Musopen_String_Quartet).flac |
| `music/anthem_austria_kaiserhymne.ogg` | Haydn, *Gott erhalte Franz den Kaiser* (1797; recorded as the German anthem) | United States Navy Band · US federal work (Commons `PD-USGov-Military-Navy`), composition PD-old · https://commons.wikimedia.org/wiki/File:German_national_anthem_performed_by_the_US_Navy_Band.ogg |
| `music/anthem_britain_god_save.ogg` | *God Save the King* | United States Navy Band · US federal work (Commons `PD-USGov-Military-Navy`), composition PD-old · https://commons.wikimedia.org/wiki/File:U.S._Navy_Band_-_God_Save_the_King.oga |
| `music/anthem_spain_marcha_real.ogg` | *Marcha Real* | United States Navy Band · US federal work (Commons `PD-USGov-Military-Navy`), composition PD-old · https://commons.wikimedia.org/wiki/File:Marcha_Real-Royal_March_by_US_Navy_Band.ogg |
| `music/anthem_holland_wilhelmus.ogg` | *Het Wilhelmus* | United States Navy Band · US federal work (Commons `PD-USGov-Military-Navy`), composition PD-old · https://commons.wikimedia.org/wiki/File:United_States_Navy_Band_-_Het_Wilhelmus.ogg |
| `music/anthem_warsaw_dabrowski.ogg` | *Mazurek Dąbrowskiego* (1797) | United States Navy Band · US federal work (Commons `PD-USGov-Military-Navy`), composition PD-old · https://commons.wikimedia.org/wiki/File:Mazurek_Dabrowskiego.ogg |
| `music/anthem_denmark_kong_christian.ogg` | *Kong Christian stod ved højen mast* | United States Navy Band · US federal work (Commons `PD-USGov-Military-Navy`), composition PD-old · https://commons.wikimedia.org/wiki/File:United_States_Navy_Band_-_Kong_Kristian_stod_ved_højen_mast.ogg |
| `music/war_beethoven5_i.ogg` | Beethoven, Symphony No. 5 — I. Allegro con brio | Skidmore College Orchestra (Musopen) · Public Domain Mark (the archive.org item mirrors the Musopen release on Commons) · https://archive.org/details/SymphonyNo.5 |
| `music/peace_mozart_k465_ii.ogg` | Mozart, String Quartet No. 19 *Dissonance*, K465 — II. Andante cantabile | Musopen String Quartet · Musopen Kickstarter recordings, Public Domain Mark (the archive.org item the August pass used) · https://archive.org/details/MusopenCollectionAsFlac |
| `music/peace_mozart_k421_ii.ogg` | Mozart, String Quartet No. 15, K421 — II. Andante | Musopen String Quartet · Musopen Kickstarter recordings, Public Domain Mark (the archive.org item the August pass used) · https://archive.org/details/MusopenCollectionAsFlac |
| `music/peace_magic_flute_overture.ogg` | Mozart, *Die Zauberflöte* — Overture | Musopen Symphony Orchestra · Musopen Kickstarter recordings, Public Domain Mark (the archive.org item the August pass used) · https://archive.org/details/MusopenCollectionAsFlac |
| `music/crisis_mozart40_iv.ogg` | Mozart, Symphony No. 40, K550 — IV. Allegro assai | Musopen Symphony Orchestra · Musopen Kickstarter recordings, Public Domain Mark (the archive.org item the August pass used) · https://archive.org/details/MusopenCollectionAsFlac |
| `music/bugle_assembly.mp3` | bugle call: Assembly | United States Navy Band Ceremonial Band · US federal work, Public Domain Mark · https://archive.org/details/BugleCalls (`Assembly.MP3`, unmodified) |
| `music/bugle_fix_bayonets.mp3` | bugle call: Fix Bayonets (the charge and the call to arms) | United States Navy Band Ceremonial Band · US federal work, Public Domain Mark · https://archive.org/details/BugleCalls (`FixBayonets.mp3`, unmodified) |
| `music/bugle_tattoo.mp3` | bugle call: Tattoo (the day's end and the retreat) | United States Navy Band Ceremonial Band · US federal work, Public Domain Mark · https://archive.org/details/BugleCalls (`Tattoo.MP3`, unmodified) |

Six further movements (Beethoven 6 I/V, Beethoven 8 II, Beethoven 5 IV and two US Army calls) were found on Commons but held there behind its rate limit for the whole session; the Musopen archive's Mozart movements above took their places in the rotations, and the Eroica finale stays the one triumph (as the August spec reserved it).

## Illustrations — `assets/ui/illustrations/` (Session UI-5, November 12, 2026)

Period paintings and engravings on the letters and reading screens
(`scripts/illustrations.gd`). Every source is a 2D work whose author died more
than 100 years ago, from Wikimedia Commons (PD-old, faithful reproductions under
the PD-Art rule) or a museum's CC0 photograph; nothing from Gallica/BnF; a
CC BY-SA photograph or edit was refused wherever one was offered. Each file is
made from its Commons thumbnail by `tools/ui5_illustrations.py` with one
treatment (a crop to 3:1 / 16:9 on the subject, a warm grade toward the
parchment, a soft vignette) — a faithful reproduction, re-framed. No credit is
legally required; the in-game credits name the source family and each picture's
hover names its work.

| Files | Work | Licence | Source page |
|---|---|---|---|
| `aboukir_banner.jpg`, `aboukir_plate.jpg` | The Battle of Aboukir — Antoine-Jean Gros (1806) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Antoine-Jean_Gros_-_Bataille_d%27Aboukir,_25_juillet_1799_-_Google_Art_Project.jpg |
| `arcole_banner.jpg`, `arcole_plate.jpg` | Bonaparte at the Pont d'Arcole — Antoine-Jean Gros (1796) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Antoine-Jean_Gros_-_Bonaparte_au_pont_d%27Arcole(1796).jpg |
| `berlin_banner.jpg`, `berlin_plate.jpg` | Napoleon Entering Berlin — Charles Meynier (1810) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Charles_Meynier_-_Entr%C3%A9e_de_Napol%C3%A9on_%C3%A0_Berlin._27_octobre_1806.jpg |
| `borodino_banner.jpg`, `borodino_plate.jpg` | The Battle of Borodino — Louis-François Lejeune (1822) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Battle_of_Borodino.jpg |
| `camp_banner.jpg`, `camp_plate.jpg` | Napoleon's Bivouac on the Eve of Wagram — Adolphe Roehn (1810) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Napoleon_bivouac_Wagram.jpg |
| `ceremony_banner.jpg`, `ceremony_plate.jpg` | The Legion of Honour Given at the Boulogne Camp — Philippe-Auguste Hennequin (1806) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Hennequin_-_Napol%C3%A9on_Ier_distribue_les_croix_de_la_l%C3%A9gion_d%27honneur_au_camp_de_Boulogne_le_16_ao%C3%BBt_1804_(grand).jpg |
| `congress_banner.jpg`, `congress_plate.jpg` | The Congress of Vienna — after Jean-Baptiste Isabey (1819) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Wiener_Kongress.jpg |
| `convoy_banner.jpg`, `convoy_plate.jpg` | The Crossing of the Berezina — Peter von Hess (1844) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Crossing_the_Berezina_River,_by_Peter_von_Hess.jpg |
| `copenhagen_banner.jpg`, `copenhagen_plate.jpg` | The Battle of Copenhagen, 2 April 1801 — Nicholas Pocock (1806) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:The_Battle_of_Copenhagen,_2_April_1801_RMG_BHC0529.tiff |
| `coronation_banner.jpg`, `coronation_plate.jpg` | The Coronation of Napoleon — Jacques-Louis David (1807) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Jacques-Louis_David_-_The_Coronation_of_Napoleon_(1805-1807).jpg |
| `council_banner.jpg`, `council_plate.jpg` | Kutuzov's Council of War at Fili — Aleksey Kivshenko (1880) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Kutuzov_fili.jpg |
| `courier_banner.jpg`, `courier_plate.jpg` | An Officer of the Chasseurs of the Guard, Charging — Théodore Géricault (1812) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:GericaultHorseman.jpg |
| `court_banner.jpg`, `court_plate.jpg` | The Distribution of the Eagle Standards — Jacques-Louis David (1810) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Jacques_Louis_David_-_Serment_de_l%27arm%C3%A9e_fait_%C3%A0_l%27Empereur_apr%C3%A8s_la_distribution_des_aigles,_5_d%C3%A9cembre_1804_-_Google_Art_Project.jpg |
| `disasters_banner.jpg`, `disasters_plate.jpg` | The Disasters of War, plate 30: Ravages of War — Francisco Goya (1810) | CC0 | https://commons.wikimedia.org/wiki/File:Plate_30_from_%27The_Disasters_of_War%27_(Los_Desastres_de_la_Guerra)-%27Ravages_of_war%27_(Estragos_de_la_guerra)_MET_DP817373.jpg |
| `fleet_banner.jpg`, `fleet_plate.jpg` | The Redoutable at Trafalgar — Louis-Philippe Crépin (1806) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:The_Redoutable_At_The_Battle_of_Trafalgar.jpg |
| `fontainebleau_banner.jpg`, `fontainebleau_plate.jpg` | Napoleon at Fontainebleau, 31 March 1814 — Paul Delaroche (1846) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Napoleon_at_Fontainebleau,_31_March_1814_(by_Hippolyte_Paul_Delaroche).jpg |
| `holland_banner.jpg`, `holland_plate.jpg` | Louis Bonaparte, King of Holland — Charles Howard Hodges (1809) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:LouisBonaparte_Holland.jpg |
| `horatii_banner.jpg`, `horatii_plate.jpg` | The Oath of the Horatii — Jacques-Louis David (1784) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Jacques-Louis_David,_Le_Serment_des_Horaces.jpg |
| `horses_banner.jpg`, `horses_plate.jpg` | The Horse Fair — Rosa Bonheur (1855) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Rosa_Bonheur,_The_Horse_Fair,_1852%E2%80%9355.jpg |
| `marengo_banner.jpg`, `marengo_plate.jpg` | The Battle of Marengo — Louis-François Lejeune (1801) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Lejeune_-_Bataille_de_Marengo.jpg |
| `moniteur_banner.jpg`, `moniteur_plate.jpg` | The Arrival of a Stage-coach at the Messageries — Louis-Léopold Boilly (1803) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Louis-L%C3%A9opold_Boilly_-_The_Arrival_of_a_Stage-coach_in_the_Courtyard_of_the_Messageries_-_WGA02356.jpg |
| `pius_vii_banner.jpg`, `pius_vii_plate.jpg` | Pope Pius VII — Jacques-Louis David (1806) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Portrait_of_Pope_Pius_VII_Chiaramonti_(by_Jacques-Louis_David)_%E2%80%93_National_Museum_of_the_Palace_of_Versailles.jpg |
| `reich_banner.jpg`, `reich_plate.jpg` | Francis II, the Last Holy Roman Emperor — Friedrich von Amerling (1832) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Francis_II,_Holy_Roman_Emperor_by_Friedrich_von_Amerling_003.jpg |
| `repression_banner.jpg`, `repression_plate.jpg` | The Third of May 1808 — Francisco Goya (1814) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:El_tres_de_mayo_de_1808_en_Madrid.jpg |
| `retreat_banner.jpg`, `retreat_plate.jpg` | Napoleon's Retreat from Moscow — Adolph Northen (1851) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Napoleons_retreat_from_Moscow_by_Adolph_Northen.jpg |
| `rising_banner.jpg`, `rising_plate.jpg` | The Second of May 1808 — Francisco Goya (1814) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:El_dos_de_mayo_de_1808_en_Madrid.jpg |
| `santo_domingo_banner.jpg`, `santo_domingo_plate.jpg` | The Capture of Gros-Morne, Saint-Domingue, 1802 — Martinet and Réville (1836) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Capture_of_Gros-Morne_by_Napoleonic_troops_in_August_1802_during_the_Leclerc_expedition_against_the_insurgent_slaves_of_the_colony_of_Saint-Domingue_(1836_engraving).jpg |
| `somosierra_banner.jpg`, `somosierra_plate.jpg` | The Battle of Somosierra — Louis-François Lejeune (1810) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Louis-Fran%C3%A7ois_Lejeune_-_Battle_of_Somosierra,_November_30,_1808.jpg |
| `study_banner.jpg`, `study_plate.jpg` | The Emperor Napoleon in His Study at the Tuileries — Jacques-Louis David (1812) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Jacques-Louis_David_-_The_Emperor_Napoleon_in_His_Study_at_the_Tuileries_-_Google_Art_Project.jpg |
| `talleyrand_banner.jpg`, `talleyrand_plate.jpg` | Talleyrand, Prince of Benevento — François Gérard (1808) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Charles_Maurice_de_Talleyrand-P%C3%A9rigord_by_Fran%C3%A7ois_G%C3%A9rard,_1808.jpg |
| `te_deum_banner.jpg`, `te_deum_plate.jpg` | Notre-Dame's Choir Dressed for the Coronation — Charles Percier (1804) | CC0 | https://commons.wikimedia.org/wiki/File:Projet_de_d%C3%A9coration_du_ch%C5%93ur_de_Notre-Dame_et_du_tr%C3%B4ne_pontifical_pour_le_sacre_de_Napol%C3%A9on._D.2159.jpg |
| `tilsit_banner.jpg`, `tilsit_plate.jpg` | The Meeting of Napoleon and Alexander I at Tilsit — Adolphe Roehn (1808) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Tilsitz_1807.JPG |
| `treasury_banner.jpg`, `treasury_plate.jpg` | The Port of Bayonne — Joseph Vernet (1755) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Vernet-port-Bayonne.jpg |
| `treaty_banner.jpg`, `treaty_plate.jpg` | The Meeting of Napoleon and Francis II after Austerlitz — Antoine-Jean Gros (1812) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Gros_-_Entrevue_-_1812.jpg |
| `ulm_banner.jpg`, `ulm_plate.jpg` | The Surrender of Ulm — Charles Thévenin (1815) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:Charles_Th%C3%A9venin_-_Reddition_de_la_ville_d%27Ulm.jpg |
| `wedding_banner.jpg`, `wedding_plate.jpg` | The Marriage of Prince Eugène and Princess Augusta of Bavaria — François-Guillaume Ménageot (1808) | Public domain (PD-old / PD-Art) | https://commons.wikimedia.org/wiki/File:M%C3%A9nageot_Matrimonio.jpg |

## Heraldry — `assets/ui/heraldry/` (Public Domain, Wikimedia + original)

33 period national flags, named `<Nation>.svg` — the 20 for the 1805 boot roster, plus 7
for nations that can only come into existence during a campaign (NA-6a/6b's Italy and United
Netherlands; NA-6c's Duchy of Warsaw, Poland, Duchy of Normandy and Roman Republic; DEF-5's
Ireland), plus the 6 crowns of DY-6 (`DYNAMISM_SPEC.md` §6, November 10, 2026) — `KingdomOfNaples.svg`,
`Westphalia.svg`, `Hungary.svg`, `Illyria.svg`, `Finland.svg`, `DuchyOfMilan.svg` — all
original simplified geometric renderings authored in-repo in the set's flat 500×300 style
(Murat's white-within-blue, Westphalia's blue over white, the red-white-green of Saint
Stephen's crown, Carniola's white-blue-red barry for the Illyrian Provinces, the Finnish
lion's gold fess on red, the red cross of Saint Ambrose for Milan); simple heraldic geometry
carries no copyright.

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

**The French First Empire eagle** — `assets/ui/ornaments/eagle_empire.svg` (Session UI-2,
November 11, 2026). Source: Wikimedia Commons, *File:Aigle Empire.svg* by Frédéric Michel
(User:-Strogoff-), 2009, licence **{{PD-self}}** (released into the public domain by its author),
a vectorisation of *File:Aigle Empire.png* — "Document datant de 1804", licence **{{PD-Art}}**.
Both read through the Commons API (`LicenseShortName: Public domain`, `Copyrighted: False`,
`AttributionRequired: false`) before shipping. Changes: the yellow detail set white (tinted gilt by
`modulate`), the black silhouette kept at 55 % opacity as its engraving shadow, the Inkscape
comment dropped. Used on the main menu, the campaign-end card.

---

## CC-BY — **visible attribution required if these ship**

Credit these in an in-game credits screen and/or this file. Only required for the specific
icons/borders actually used in the shipped build.

- **Game-icons.net** (thematic icons) — CC-BY 3.0. Per-icon authors differ.
  Required form: *"Game icons by Lorc, Delapouite & contributors (game-icons.net), CC BY 3.0"* —
  track which icons ship. https://game-icons.net
  The stat glyphs that ship are listed one by one with their authors in
  `assets/ui/icons/glyphs/GLYPHS.txt` (Session UI-2); the in-game line in Settings → CREDITS
  ("Lorc, Delapouite & contributors") covers Skoll, Sbed and HeavenlyDog as contributors.
- **RPG GUI Construction Kit** — CC-BY 3.0.
  Required form: *"RPG GUI by Matjaž Lamut (Lamoot), CC BY 3.0"*.
  https://opengameart.org/content/rpg-gui-construction-kit-v10
- **Musket battle volley** (`assets/audio/battle/musket_battle_volley.mp3`) — CC-BY 4.0.
  Required form: *"Musket battle sounds by aaronsiler & Benboncan (freesound.org), CC BY 4.0"*
  (the compilation's ricochets derive from Benboncan's CC-BY sounds, so BOTH are credited).
  https://freesound.org/people/aaronsiler/sounds/128981/ — if this file is ever dropped,
  drop the credit line with it.

---

## Main-Menu Battle Paintings — Public Domain (PD-art), via Wikimedia Commons

`assets/ui/paintings/` — the Main Menu slideshow (position 6, sourced August 8,
2026). Each file was fetched via the Commons API with the `LicenseShortName`
extmetadata verified **"Public domain"** before download; every artist died well
over 100 years ago. Scaled to ≤2560 px; no other modification. Attribution not
required (courtesy captions shown in-menu).

| File | Work | Artist | Commons source file |
|---|---|---|---|
| `gerard_austerlitz_pd.jpg` | *La bataille d'Austerlitz, 2 décembre 1805* | François Gérard (1770–1837) | `La bataille d'Austerlitz. 2 decembre 1805 (François Gérard).jpg` |
| `gros_eylau_pd.jpg` | *Napoléon sur le champ de bataille d'Eylau* | Antoine-Jean Gros (1771–1835) | `Napoleon on the Battlefield of Eylau (Antoine-Jean Gros).jpg` |
| `meissonier_friedland_pd.jpg` | *1807, Friedland* | Ernest Meissonier (1815–1891) | `1807, Friedland.jpg` |
| `vernet_jena_pd.jpg` | *Bataille d'Iéna* | Horace Vernet (1789–1863) | `Iena.jpg` |
| `turner_trafalgar_pd.jpg` | *The Battle of Trafalgar* | J. M. W. Turner (1775–1851) | `Turner, The Battle of Trafalgar (1822).jpg` |
| `david_alps_pd.jpg` | *Bonaparte franchissant le Grand-Saint-Bernard* — shipped as a landscape CROP of the upper composition (rider, horse's head, cape; Aug 8, 2026): the full portrait canvas cover-fit in the menu's wide viewport showed only the middle band | Jacques-Louis David (1748–1825) | `Napoleon at the Great St. Bernard - Jacques-Louis David - Google Cultural Institute.jpg` |

The application icon (`icon.png`, crossed quill & sabre) is ORIGINAL procedural
art generated by `tools/gen_app_icon.py` — no third-party pixels.

## Marshal Portraits — Public Domain (PD-art), via Wikimedia Commons

44 portraits in `assets/portraits/`, named by the game's internal marshal key
(e.g. `Ney.jpg`, `Wellesley.jpg` = Arthur Wellesley / Duke of Wellington,
`Frederick.jpg` = Frederick VI of Denmark). All are 19th-century painted portraits in
the public domain (PD-art). No legal attribution required; courtesy credit: "Portraits
via Wikimedia Commons (public domain)."

`Napoleon.jpg` (row NP, Aug 15 2026) is a portrait CROP derived in-repo from
the already-shipped `assets/ui/paintings/david_alps_pd.jpg` (*Bonaparte
franchissant le Grand-Saint-Bernard*, Jacques-Louis David, PD-art — see the
menu-paintings table above); no new download.

The secondaries' bench (SF-RR4, EG-D3, October 21, 2026), each the lead image of
its subject's Wikipedia article, marked public domain on Commons, re-encoded in-repo
(JPEG, at most 2,000 px; no other change):
`Wrede.jpg` — Carl Philipp von Wrede, lithograph by Franz Hanfstaengl (1828), `Karl Philipp Wrede.jpg`;
`LaRomana.jpg` — Pedro Caro y Sureda, Marquis of La Romana, Vicente López Portaña, Museo del Prado,
`Pedro Caro y Sureda, marqués de la Romana (Museo del Prado).jpg`;
`Blake.jpg` — Joaquín Blake y Joyes, by Manuel Ojeda, `El general Joaquín Blake y Joyes, por Manuel Ojeda.jpg`;
`Cuesta.jpg` — Gregorio García de la Cuesta, 19th-century portrait at the Casona de Tudanca (his
birthplace), `Gregorio García de la Cuesta.png` — the only painted likeness found on Commons, Europeana
or the Biblioteca Nacional de España (whose one print, an 1808 profile engraving, idealizes a younger
man), shipped upscaled 3× in-repo (Lanczos, a light unsharp mask) from its 200 × 268 original;
`Toll.jpg` — Johan Christopher Toll, by Johan Way, Nationalmuseum Stockholm (NMGrh 39749),
the Commons 1,280-px rendering of `Johan Kristoffer Toll, 1743-1817 (Johan Way) - Nationalmuseum - 39749.tif`;
`Adlercreutz.jpg` — Carl Johan Adlercreutz, after Carl Frederik von Breda (1846), Nationalmuseum Stockholm
(NMGrh 15479), the Commons 1,280-px rendering of its cropped TIFF.

The courts' benches and the 1805 field corps (S14k, October 28, 2026 — downloaded on
the user's yes), each the lead image of its subject's Wikipedia article unless noted,
marked public domain on Commons unless noted, re-encoded in-repo (JPEG, at most
1,100 px; no other change):
`BernardimFreire.jpg` — Bernardim Freire de Andrade, by G. F. de Queiroz (early 19th century),
`Bernardim Freire de Andrada e Castro - G.F. de Queiroz. Início do séc. XIX (cropped).png`;
`Silveira.jpg` — Francisco da Silveira, Count of Amarante, unknown 19th-century painter,
`Retrato do Conde de Amarante.jpg`;
`LeCoq.jpg` — Karl Christian Erdmann von Le Coq, lithograph by M. Knäbig after Rentzsch (c. 1840),
`Karl Christian Erdmann von Le Coq.jpg`;
`Emil.jpg` — Prince Emil of Hesse, circle of Franz Xaver Winterhalter (by 1852),
`Franz Xaver Winterhalter (circle) Prinz Emil von Hessen und bei Rhein.jpg` (the Commons 960-px rendering);
`Wallmoden.jpg` — Ludwig von Wallmoden-Gimborn, by George Dawe (the Military Gallery), `Walmoden.jpg`
(the Commons 960-px rendering);
`Alten.jpg` — Charles Alten, by Joseph Paelinck (1818), Bomann-Museum Celle,
`Ahlten BomannMuseum@20150903 03.JPG` (the Commons 960-px rendering);
`Janssens.jpg` — Jan Willem Janssens, by Jan Willem Pieneman, Rijksmuseum (SK-A-2219), the Commons
960-px rendering of its file;
`Fontanelli.jpg` — Achille Fontanelli, by Andrea Appiani, `PORTRAIT OF ACHILLE FONTANELLI.PNG`;
`Bachmann.jpg` — Niklaus Franz von Bachmann, by Felix Maria Diogg (1817), `Bachmann-Anderletz 1817.jpg`;
`ChristianAugust.jpg` — Christian August (Karl August) of Augustenborg, by Per Krafft the Younger (1809),
Nationalmuseum Stockholm (NMGrh 39744), the Commons 960-px rendering of its TIFF;
`Philippsthal.jpg` — Louis of Hesse-Philippsthal, by Johann Werner Kobold (1782),
`Ludwig Prinz von Hessen-Philippsthal.jpg` (the Commons 960-px rendering);
`Wattenwyl.jpg` — Niklaus Rudolf von Wattenwyl, by David Sulzer (1825), `Niklaus Rudolf von Wattenwyl.jpg`
(a Commons search; his article carries no image).

Not downloaded (S14k): **Zezschwitz** (no likeness on Commons), **Alemdar** (the only
image is a modern contributor's drawing, not a period likeness) and **YusufZiya** (his
article's photograph is of a later Ziya Pasha) — left unillustrated by design, the
gold-monogram fallback, rather than risk a wrong likeness.

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
