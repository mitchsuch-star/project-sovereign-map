# Music & Sound (Core) — Spec & Asset Book

**Owner:** ROADMAP §THE ROAD TO EA, position 4 ("Music & Sound (Core)", user-ordered
forward Aug 7, 2026: *"we have no sound"*).
**Status:** ✅ **SOURCING HALF COMPLETE August 7, 2026** (this document §1–§2 is its
landing record) → **▶ WIRING HALF NEXT** (§3 is its build contract; multi-session row).
**License ledger:** every file below is also recorded in repo-root
`THIRD_PARTY_LICENSES.md` (the authoritative license table). One NEW visible-credit
obligation ships with this batch — see §5.

---

## §0 The sourcing session record (August 7, 2026)

The user's directive: *"find good sounds including music, for clicks for battles etc.
and maybe a writing sounds for when text is generating in imperial log? and when you
send a command etc, anything else you can think of."*

**Method.** An 11-agent research workflow (5 category finders with self-run curl
reachability checks → 5 adversarial license verifiers → 1 gap critic, ~1.8M tokens)
plus 1 targeted follow-up agent for the two starved cues. 99 candidates found,
**90 passed adversarial license verification**, 42 files downloaded (+ 28 curated out
of the three CC0 zips already on disk), every file magic-byte- and duration-verified.

**Decisions made in-session, on the record:**

1. **The craigsmith provenance trap, applied consistently.** The battle-SFX verifier
   discovered that freesound user *craigsmith*'s CC0-labelled sounds are digitized
   Hollywood studio tape effects (USC Cinema / Sunset Editorial chain) he does not
   own, and rejected five of them. One more of his files (`G28-10 Indoor Crowd
   Murmur`) had PASSED the world-SFX verifier — same defect, so it was rejected here
   by cross-category consistency and replaced (IENBA's `Small Crowd Walla`, CC0).
   **Standing rule: no craigsmith uploads, and no uploads whose description reveals
   the uploader digitized someone else's recordings.**
2. **The 78rpm gramophone family was rejected on register, not license.** Three
   French marches (Chant du Départ, Sambre-et-Meuse, Marche Lorraine) passed license
   review as pre-1926 US-PD shellac rips — but heavy surface noise would clash with
   the clean Musopen orchestral pool (the gap critic's warning). Not shipped. If a
   deliberate "gramophone register" is ever wanted, that family is re-openable —
   the URLs are in the Aug 7 workflow record.
3. **The French-march slot is filled by an 1880 composition, disclosed.** No US
   federal ensemble recording of Chant du Départ / Sambre-et-Meuse exists reachable
   (marineband.marines.mil is bot-blocked 403; music.army.mil does not resolve; DVIDS
   has none). The US Marine Band's *Marche militaire française* (Saint-Saëns, 1880)
   is the stock "French military march" register in a clean modern PD recording —
   taken with the anachronism ON THE RECORD here. The Marseillaise (US Navy Band,
   modern, PD) is period-true and carries the French-anthem weight.
4. **`ink_dip` was considered and CUT** — no clean sub-second candidate; both
   survivors were long multi-dip compilations needing editing we cannot do (no
   ffmpeg). No player-facing promise exists, no owner row needed.
5. **Freesound files are the public HQ previews (~128 kbps MP3/OGG), not the
   login-gated originals.** Legally identical (the license covers the work). For
   quiet UI foley this is fine; §3.5 makes "does any cue sound muddy in-engine?" an
   explicit wiring-session check, with the manual re-fetch route named.
6. **Nobody has LISTENED to these files yet.** Headers, licenses, durations and
   sources are verified; ears are not. The wiring session's live boot auditions
   every cue before it lands (§3.5) — same discipline as the war-table pieces'
   visual sign-off.

---

## §1 Asset inventory — `godot-client/project-sovereign/assets/audio/`

`assets/` is blanket-gitignored; every file below is force-tracked (`git add -f`),
per the UI-0 tracking policy. The three CC0 zips remain untracked master pools.

### `music/` (18 files, ~62 MB — the game had ZERO music before this)

| File | What it is | Performer / license | Length |
|---|---|---|---|
| `theme_eroica_i.ogg` | Beethoven, Symphony No. 3 *Eroica* (1804) — I. Allegro con brio. THE Napoleonic symphony, originally dedicated to Bonaparte. | Musopen Symphony Orch. — PD (Musopen Kickstarter commission) | 15:11 |
| `lament_eroica_ii_marcia_funebre.ogg` | *Eroica* — II. Marcia funebre | same | 15:28 |
| `triumph_eroica_iv_finale.ogg` | *Eroica* — IV. Finale | same | 11:45 |
| `tension_coriolan.ogg` | Beethoven, *Coriolan* Overture (1807) — dark, urgent | same | 8:19 |
| `calm_haydn_lark_adagio.ogg` | Haydn, *Lark* Quartet Op. 64/5 — II. Adagio cantabile (1790) | Musopen String Quartet — PD | 4:52 |
| `calm_mozart40_andante.ogg` | Mozart, Symphony No. 40 — II. Andante (1788) | Musopen Symphony Orch. — PD | 7:36 |
| `calm_goldberg_aria.mp3` | Bach, Goldberg Variations — Aria. The one solo-piano slot: the Emperor's study at night. | Kimiko Ishizaka (Open Goldberg) — CC0 | 4:59 |
| `marseillaise_navy_band.ogg` | La Marseillaise (1792) — ceremonial band | **US Navy Band** — PD (US federal work) | 1:19 |
| `marche_militaire_francaise.mp3` | Saint-Saëns, *Marche militaire française* (1880 — anachronism disclosed §0.3) | **US Marine Band** — PD (federal) | 4:14 |
| `fife_drum_brandywine.ogg` | Brandywine Quickstep — period fife & drum | **US Army Old Guard Fife & Drum Corps** — PD (federal) | 1:53 |
| `fife_drum_field_medley.ogg` | Reveille Variation / Drum Call / Slow & Quick Scotch / Yankee Doodle medley | same | 2:22 |
| `fife_drum_warlike_medley.ogg` | Soldiers Farewell Fanfare / Montezuma / March of War medley | same | 2:17 |
| `drums_rage_of_cornwallis.ogg` | Drum Feature: The Rage of Cornwallis — massed field drums | same | 2:05 |
| `fanfare_erafnaf.ogg` | ERAFNAF Fanfare — brass/field fanfare | same | 0:37 |
| `bugle_first_call.mp3` | First Call — solo bugle | US military bugle call — PD | ~0:15 |
| `bugle_reveille.ogg` | Reveille — solo bugle | same | 0:21 |
| `bugle_mail_call.ogg` | Mail Call — solo bugle | same | 0:05 |
| `bugle_to_the_color.ogg` | To the Color — honors bugle call | same | 0:42 |

### `ui/` (28 files — desk, paper, quill, chrome)

Sourced this session (freesound CC0 unless noted): `quill_scribble_loop.ogg` (6.0s
steady quill-on-parchment texture — THE text-streaming loop), `quill_scribble_long.ogg`
(54s variety take), `quill_flick.mp3` (one short stroke — command send),
`quill_sign.mp3` (signature flourish), `wax_seal.mp3` (genuine seal press),
`letter_open.mp3` (envelope/letter), `paper_crumple.mp3`, `notification_bell.mp3`
(desk bell), `coin_pour.mp3`, `end_turn_drum_roll.mp3` (snare buzz roll).

Curated from the on-disk CC0 zips (Kenney Interface Sounds / RPG Audio, extracted
unmodified and cue-renamed, the `cannon_thud.ogg` precedent): `click_primary`,
`click_soft`, `tick_subtle`, `select_item`, `toggle_switch`, `confirm_chime`,
`error_soft`, `question_open`, `panel_open`, `panel_close`, `back_dismiss`,
`page_turn_1/2/3` (bookFlips), `book_open`, `book_close`, `coins_small`,
`coins_small_2`, `command_ack_click` (metal click — reads as a musket-lock cock),
`latch_close`, `door_open_heavy`, `door_close_heavy`, `cloth_rustle` (all `.ogg`).
Pre-existing: the two parchment map-open/close WAVs (finally assigned — §2).

### `battle/` (13 files)

Sourced: `musket_battle_volley.mp3` (**CC-BY 4.0 — the batch's one credit
obligation, §5**; real black-powder musket reports layered into rolling fire, 23s),
`cavalry_gallop.mp3` (6 horses, CC0), `horse_whinny.ogg` (Wikimedia PD),
`sword_draw.mp3` (CC0), `army_march.mp3` (37s cadenced boots, CC0),
`army_march_loop_short.mp3` (7.5s loop foley, CC0), `battlefield_ambience.mp3`
(5:45 Revolutionary-War reenactment field recording — real flintlock volleys, drums,
shouts, CC0 own-recording).
Curated from the bang pack (CC0): `musket_shot_1/2/3.ogg`, `cannon_distant.ogg`.
Pre-existing: `cannon_thud.ogg` (CC0), `drum_sting.wav` (self-authored,
`tools/gen_battle_audio.py`).

### `ambient/` (9 files)

Sourced (freesound CC0): `church_bells_peal.mp3` (celebration peal),
`bell_toll_single.mp3` (solemn toll), `ship_bell.mp3` (two chimes), `sea_loop.mp3`
(surf), `campfire_loop.mp3` (designed loop), `wind_map_loop.mp3` (designed gentle
wind loop), `crowd_murmur.mp3` (walla, no intelligible speech).
Curated from the RPG pack (CC0): `ship_creak_1/2.ogg`.

---

## §2 The cue map — surface → sound

The wiring session implements this table. "Shown = played": a cue listed here is a
promise; if a row is cut, cut it here explicitly (Golden Rule 9).

### The command flow (the user's named ask)
| Moment | Cue | Asset |
|---|---|---|
| Player submits a typed order | command_send | `ui/quill_flick.mp3` |
| Order acknowledged / executes | command_ack | `ui/command_ack_click.ogg` |
| **Text streaming into the imperial log / terminal** (the typewriter effect, incl. the diorama's typed verdict) | scribble loop | `ui/quill_scribble_loop.ogg` — START with stream, STOP on completion; `quill_scribble_long.ogg` for long streams |
| Command refused / error | refusal | `ui/error_soft.ogg` (sharper flavor alt: `paper_crumple.mp3`) |
| Clarification question ("Which marshal, Sire?") | question | `ui/question_open.ogg` |

### The turn cycle
| Moment | Cue | Asset |
|---|---|---|
| End turn pressed | end_turn | `ui/end_turn_drum_roll.mp3` |
| Morning dispatch arrives | dispatch | `music/bugle_reveille.ogg` (it IS morning), quiet |
| Notification chip appears | notify | `ui/notification_bell.mp3` |
| Letter-book / envoy digest arrives | mail | `music/bugle_mail_call.ogg` or `ui/letter_open.mp3` |

### Battle & the diorama
| Moment | Cue | Asset |
|---|---|---|
| Cannon (existing diorama wiring) | cannon | `battle/cannon_thud.ogg` (KEPT) |
| Drum sting (existing) | sting | `battle/drum_sting.wav` (KEPT) |
| Infantry volley beat | volley | `battle/musket_battle_volley.mp3` (trim-in ~0-6s) or `musket_shot_*` |
| Cavalry piece moves / charge | cavalry | `battle/cavalry_gallop.mp3` + optional `horse_whinny.ogg` |
| Diorama bed, big battles | bed | `battle/battlefield_ambience.mp3` at low volume |
| Enemy-phase battle line | distant | `battle/cannon_distant.ogg` |
| Victory verdict | fanfare | `music/fanfare_erafnaf.ogg` |
| Defeat / rout verdict | lament sting | `ambient/bell_toll_single.mp3` (single toll) or drum_sting reuse |
| Marshal petition / confrontation modal | steel | `battle/sword_draw.mp3` |
| Army movement on the map | march | `battle/army_march_loop_short.mp3` (loop under tween) |

### Diplomacy, ceremony, economy
| Moment | Cue | Asset |
|---|---|---|
| Treaty signed / settlement ratified | sign+seal | `ui/quill_sign.mp3` → `ui/wax_seal.mp3` |
| The Proclamation (NA-6b) / nation formation | bells | `ambient/church_bells_peal.mp3` |
| Honors / Crowned with Glory / The Rally | honors | `music/bugle_to_the_color.ogg` (short in) |
| Payment / subsidy / rente | coins | `ui/coins_small.ogg`; large sums `ui/coin_pour.mp3` |
| Plunder choice taken | plunder | `ui/coin_pour.mp3` |
| Incoming proposal popup | letter | `ui/letter_open.mp3` |
| Court / negotiation ambience (optional) | walla | `ambient/crowd_murmur.mp3` |

### Naval (The Wooden Wall)
| Moment | Cue | Asset |
|---|---|---|
| Admiralty screen open | bell | `ambient/ship_bell.mp3` |
| Admiralty ambience | sea | `ambient/sea_loop.mp3` + `ship_creak_1/2.ogg` |
| Naval diorama | (reuses cannon + sea bed) | existing + `sea_loop` |

### Screens & chrome
| Moment | Cue | Asset |
|---|---|---|
| Button press | click | `ui/click_primary.ogg` |
| Chip / tab / small control | click2 | `ui/click_soft.ogg` or `tick_subtle.ogg` |
| List row select / map province click | select | `ui/select_item.ogg` |
| Toggle | toggle | `ui/toggle_switch.ogg` |
| Screen/panel open · close | panel | `ui/panel_open.ogg` · `panel_close.ogg` |
| Map open · close (the two orphaned WAVs, finally assigned) | map | `ui/parchment_open_snd_use_map.wav` · `parchment_close_snd_close_map.wav` |
| Ledger/dispatch tab switch | page | `ui/page_turn_1/2/3.ogg` (rotate) |
| Campaign log open · close | book | `ui/book_open.ogg` · `book_close.ogg` |
| Modal dismiss / ESC | back | `ui/back_dismiss.ogg` |
| Accept / confirm | confirm | `ui/confirm_chime.ogg` |
| War-room transitions (optional flavor) | door | `ui/door_open_heavy.ogg` · `door_close_heavy.ogg` / `latch_close.ogg` |

### The music program
| Slot | Track(s) |
|---|---|
| Main theme / title | `theme_eroica_i.ogg` (fade or loop-trim ~4–5 min in) |
| Map, peace | rotate `calm_haydn_lark_adagio` · `calm_mozart40_andante` · `calm_goldberg_aria` (+ `wind_map_loop` bed when music paused) |
| Map, at war | `tension_coriolan.ogg`; field color: `fife_drum_brandywine` / `fife_drum_field_medley` / `fife_drum_warlike_medley` / `drums_rage_of_cornwallis` |
| France goes to war / Grande Armée moments | `marseillaise_navy_band.ogg`, `marche_militaire_francaise.mp3` |
| Victory (war won / triumph screen) | `triumph_eroica_iv_finale.ogg` |
| Defeat, marshal death, Paris falls | `lament_eroica_ii_marcia_funebre.ogg` |
| Night camp flavor (optional) | `ambient/campfire_loop.mp3` |

---

## §3 The wiring half — build contract (NEXT session)

1. **`audio_manager.gd` autoload** (there is none): four buses **Master / Music /
   SFX / UI** (ambience routes to SFX; revisit only if mixing demands a fifth),
   `play_ui(cue)` / `play_sfx(cue)` / `play_music(track, crossfade)` /
   `start_scribble()·stop_scribble()` keyed to the §2 names, stream caching,
   round-robin for multi-take cues (page turns, clicks).
2. **Settings surface**: volume sliders (Master/Music/SFX/UI) on the pause menu
   beside Interface Scale, persisted via the `ui_settings.gd` config pattern; the
   existing **`battle_sfx` toggle is honored** (it becomes "SFX" or stays a named
   toggle — wiring session's call, recorded there).
3. **Integration seams** (each one boots the engine after — the XR-1 rule):
   `main.gd` (command send/ack/refusal, typewriter loop), `battle_diorama.gd`
   (replace direct `AudioStreamPlayer` with the manager; add volley/cavalry/bed),
   `dispatch_view.gd`/top bar (dispatch bugle, notification bell), popups
   (letter/seal/bells via `popup_base.gd` or per-dialog), `strategic_ledger.gd` +
   screens (page turns, panel open/close), map (province click, army march), pause
   menu (sliders). Music state machine last (peace/war/victory/defeat).
4. **Godot import**: every new file needs its `.import` sidecar committed (generated
   this session via `--headless --import`); music OGGs should get `loop` enabled in
   the import options where the slot loops.
5. **The audition gate**: every §2 cue is listened to in-engine before its wiring
   lands; any muddy freesound preview gets re-fetched at original quality (free
   freesound login — manual user step, flagged per-file) or swapped from the zips'
   remaining pool. Any cue that fails audition is re-sourced or its row cut HERE.

## §4 Gaps & routed items

- **`ink_dip`** — CUT (§0.4). No owner row needed; no promise exists.
- **British period airs** (e.g. Marine Band "Roast Beef of Old England", PD,
  verified reachable) — NOT taken; a future Britain-flavor pass may fetch it; noted
  here so the URL trail (Aug 7 workflow record) isn't lost. No promise made.
- **Gramophone register family** — rejected on register (§0.2); re-openable.
- **Original-quality freesound WAVs** — owner: §3.5 audition gate.
- **Music loop-points / trimming** (Eroica I is 15 min) — owner: §3.1 (Godot import
  loop flags + fade logic in the manager; no destructive editing needed).

## §5 Licenses

Authoritative table: repo-root `THIRD_PARTY_LICENSES.md` (updated this session).
Everything is CC0 / PD (US federal works, Musopen/Open Goldberg commissions,
Wikimedia PD) **except ONE file**: `battle/musket_battle_volley.mp3` is **CC-BY 4.0**
and requires visible credit — *"Musket battle sounds by aaronsiler & Benboncan
(freesound.org), CC BY 4.0"* — alongside the existing Game-icons.net and RPG GUI
credits. If that file is ever dropped, drop the credit line with it.
