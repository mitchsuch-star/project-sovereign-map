# Music & Sound (Core) — Spec & Asset Book

**Owner:** ROADMAP §THE ROAD TO EA, position 4 ("Music & Sound (Core)", user-ordered
forward Aug 7, 2026: *"we have no sound"*).
**Status:** ✅ **SOURCING HALF COMPLETE August 7, 2026** (§1–§2 = its landing record)
→ ✅ **WIRING HALF LANDED August 7, 2026, same day** (user-directed "wire all sounds";
§3 = its landing record — the whole §2 cue map is live: ~75 `AudioManager.*` call
sites across 27 scripts + `audio_manager.gd` itself; parse harness EXIT=0 over the
42-script list, boot smoke 0 SCRIPT ERROR / 0 missing-file warnings) →
✅ **§3.5 AUDITION GATE PASSED August 7, 2026 (user)** — the live listening session
was played; no trims, swaps, or re-fetches were requested. **THE ROW IS COMPLETE.**
The §3.6 pool rows stay deliberately unwired (no seam was picked at audition — they
remain variants per §3.6's own "or stays a variant" arm, re-openable at any future
audio pass; no player-facing promise exists).
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
| `bugle_first_call.mp3` | First Call — solo bugle | US military bugle call — PD | **0:09** (9.22 s — was recorded `~0:15`; corrected UX23-R7) |
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

### §1a Measured lengths — every `ui/`, `battle/` and `ambient/` file (UX23-R7)

> The three sections above are prose, and carried no length at all; `music/`
> carried lengths but one of them (`bugle_first_call.mp3`) was wrong by 6
> seconds. That is how a 38.6-second envelope-open shipped as a UI click.
>
> Measured with the same stdlib header parse the standing pin uses
> (`tests/test_ux_fixes_2026_08_23.py` — `_asset_duration`), so this table and
> the test cannot disagree. **`cue(s)`** names the registry entries that point
> at the file; **`cap`** is its `max_s`. *(unwired)* means the file is on disk
> and credited but no cue references it — kept deliberately as pool variants
> and future material, not a promise to anybody.

### ui/ — 40 files



| file | measured | cue(s) | cap |

|---|---|---|---|

| `back_dismiss.ogg` | 0.07 s | *(unwired)* | — |

| `book_close.ogg` | 0.23 s | `panel_close`, `book_close` | — |

| `book_open.ogg` | 0.15 s | `panel_open`, `book_open` | — |

| `click_primary.ogg` | 0.01 s | *(unwired)* | — |

| `click_soft.ogg` | 0.01 s | *(unwired)* | — |

| `cloth_rustle.ogg` | 0.42 s | `cloth` | — |

| `coin_pour.mp3` | 8.72 s | `coin_pour` | 3.0 |

| `coins_small.ogg` | 0.85 s | `coins_small` | — |

| `coins_small_2.ogg` | 0.34 s | `coins_small` | — |

| `command_ack_click.ogg` | 0.45 s | `command_ack` | — |

| `confirm_chime.ogg` | 0.54 s | `confirm` | — |

| `door_close_heavy.ogg` | 0.60 s | `door_close` | — |

| `door_open_heavy.ogg` | 1.41 s | `door_open` | — |

| `end_turn_drum_roll.mp3` | 4.83 s | `end_turn` | — |

| `error_soft.ogg` | 0.10 s | `error` | — |

| `latch_close.ogg` | 0.26 s | `latch` | — |

| `leather_tap_1.ogg` | 0.34 s | `select` | — |

| `leather_tap_2.ogg` | 0.31 s | `select`, `back` | — |

| `letter_open.mp3` | 38.64 s | `letter_open` | 1.4 |

| `notification_bell.mp3` | 2.74 s | `notification` | — |

| `page_turn_1.ogg` | 0.77 s | `page_turn` | — |

| `page_turn_2.ogg` | 0.43 s | `page_turn` | — |

| `page_turn_3.ogg` | 0.23 s | `page_turn` | — |

| `panel_close.ogg` | 0.15 s | *(unwired)* | — |

| `panel_open.ogg` | 0.15 s | *(unwired)* | — |

| `paper_crumple.mp3` | 0.60 s | `paper_crumple` | — |

| `parchment_close_snd_close_map.wav` | 1.62 s | `parchment_close` | — |

| `parchment_open_snd_use_map.wav` | 1.52 s | `parchment_open` | — |

| `question_open.ogg` | 0.33 s | `question` | — |

| `quill_flick.mp3` | 0.89 s | `quill_flick` | — |

| `quill_scribble_long.ogg` | 54.24 s | `scribble_long`, `scribble_long (loop)` | — |

| `quill_scribble_loop.ogg` | 6.00 s | `scribble`, `scribble (loop)` | — |

| `quill_sign.mp3` | 2.64 s | `quill_sign` | — |

| `select_item.ogg` | 0.04 s | *(unwired)* | — |

| `tick_subtle.ogg` | 0.02 s | `tick` | — |

| `toggle_switch.ogg` | 0.61 s | `toggle` | — |

| `wax_seal.mp3` | 1.37 s | `wax_seal` | — |

| `wood_tap_1.ogg` | 0.28 s | `click` | — |

| `wood_tap_2.ogg` | 0.35 s | `click` | — |

| `wood_tap_3.ogg` | 0.26 s | `click` | — |



### battle/ — 13 files



| file | measured | cue(s) | cap |

|---|---|---|---|

| `army_march.mp3` | 36.79 s | `march_long`, `march_long (loop)` | — |

| `army_march_loop_short.mp3` | 7.58 s | `march_step`, `march`, `march (loop)` | 0.65 |

| `battlefield_ambience.mp3` | 5:45 (345.99 s) | `battle_bed`, `battle_bed (loop)` | — |

| `cannon_distant.ogg` | 0.92 s | `cannon_distant` | — |

| `cannon_thud.ogg` | 1.80 s | `cannon` | — |

| `cavalry_gallop.mp3` | 25.15 s | `cavalry` | 3.2 |

| `drum_sting.wav` | 1.55 s | `drum_sting` | — |

| `horse_whinny.ogg` | 2.27 s | `whinny` | — |

| `musket_battle_volley.mp3` | 22.80 s | `musket_volley` | 4.2 |

| `musket_shot_1.ogg` | 0.46 s | `musket_shot` | — |

| `musket_shot_2.ogg` | 0.37 s | `musket_shot` | — |

| `musket_shot_3.ogg` | 0.26 s | `musket_shot` | — |

| `sword_draw.mp3` | 0.76 s | `sword_draw` | — |



### ambient/ — 9 files



| file | measured | cue(s) | cap |

|---|---|---|---|

| `bell_toll_single.mp3` | 31.71 s | `bell_toll` | 3.2 |

| `campfire_loop.mp3` | 11.06 s | `campfire`, `campfire (loop)` | — |

| `church_bells_peal.mp3` | 1:17 (77.24 s) | `bells_peal` | 5.2 |

| `crowd_murmur.mp3` | 28.06 s | `crowd`, `crowd (loop)` | — |

| `sea_loop.mp3` | 35.06 s | `sea`, `sea (loop)` | — |

| `ship_bell.mp3` | 2.98 s | `ship_bell` | — |

| `ship_creak_1.ogg` | 0.66 s | `creak`, `creak (loop)` | — |

| `ship_creak_2.ogg` | 0.83 s | *(unwired)* | — |

| `wind_map_loop.mp3` | 41.21 s | `wind`, `wind (loop)` | — |

**One registry cue has no call site anywhere in the client** — `first_call`.
Its FILE is wired as sourcing for the bugle family, but nothing calls
`AudioManager.play("first_call")`. Dead configuration rather than a broken
player-facing promise, and recorded here rather than deleted: the asset is
licensed, credited and usable.

> ⚠ **Correction, same day (review round).** The first version of this
> paragraph said the same of **`march_step`**, and it was wrong:
> `scenes/war_table_piece.gd:162` plays it on every piece move, with a comment
> explaining the design — *"one cadence per update batch; the cue's own
> throttle collapses a fleet of simultaneous moves into a single play"*. The
> grep behind the claim covered `scripts/` and the war-table piece lives in
> `scenes/`. Its 0.65 s cap is load-bearing on a 7.5 s loop file, and retiring
> the row on that claim would have silenced every march on the map.

---

## §2 The cue map — surface → sound

The wiring session implements this table. "Shown = played": a cue listed here is a
promise; if a row is cut, cut it here explicitly (Golden Rule 9).

> **§2a — CUE LENGTH IS PART OF THE CUE (added August 23, 2026).**
>
> User report from a live campaign: *"when clicking envoys and such the paper
> noise goes on for a really long time."* `ui/letter_open.mp3` is **38.64
> seconds** long. It was registered as a one-shot with no cap, so opening an
> envoy started 38 seconds of paper — and its 300 ms throttle let a second
> copy start over the first.
>
> The sourced CC0 libraries are full of whole *ambiences* rather than single
> hits (`church_bells_peal` 77.2 s, `bugle_to_the_color` 42.4 s,
> `fanfare_erafnaf` 36.5 s, `bell_toll_single` 31.7 s, `cavalry_gallop` 25.2 s,
> `musket_battle_volley` 22.8 s). **A cue's budget now lives in the `CUES`
> registry as `max_s`**, honoured by `_play_cue` with an 0.8 s fade; an
> explicit `AudioManager.play(cue, seconds)` argument still wins. Eleven cues
> are capped. `tests/test_ux_fixes_2026_08_23.py` walks every registry entry,
> measures its asset with a stdlib header parse (no ffmpeg — its absence is
> already recorded in §0), and fails any cue whose effective length outlives
> the moment that fires it, with deliberate ceremonies allowlisted by name.
>
> Corrections to this document, from the same measurement pass — **both
> discharged August 23, 2026 (UX23-R7)**:
> * ~~§1 records `bugle_first_call.mp3` as `~0:15`; it is **9.221 s**.~~ Fixed
>   in the `music/` table.
> * ~~The `ui/` and `ambient/` inventories have no length column.~~ §1a now
>   carries a measured length for every `ui/`, `battle/` and `ambient/` file,
>   with its cue and cap beside it.
>
> **⚠ Acceptance condition — MEASURED August 23, 2026, and it was half
> right.** The worry was exact: *"if the head of a capped file is a fade-in or
> room tone, the capped cue is worse than the bug."* I cannot listen, but that
> question is measurable, and the venv has no mp3/ogg decoder while **Godot
> decodes both natively** — so `tools/audio_envelope_probe.gd` routes each
> capped cue through an `AudioEffectCapture` bus and reads the PCM back. (It
> fails loudly if Godot hands it a dummy audio driver, because a silent device
> would otherwise "prove" every cue is a fade-in.)
>
> **Two of the eleven caps were cutting the sound off entirely:**
>
> | cue | cap | sound ONSET | verdict |
> |---|---|---|---|
> | `letter_open` | 1.4 s | **2.05 s** | the cap ended before the paper rustled |
> | `cavalry` | 3.2 s | **4.9 s** | a gallop that approaches; the capped window is the empty road, 30 dB down |
>
> Raising the caps would restore the length the player complained about, so
> both instead carry a new registry field **`start_s`** — play from past the
> dead head, for the same short window. The other nine onsets all land inside
> their caps (0.15–1.65 s) and carry no offset.
>
> **What still owes ears** is much narrower than "the eleven capped cues":
> only phrase-completeness on the three bugle/fanfare cues (`reveille`,
> `to_the_color`, `fanfare`), where the measurement can say the sound is
> present and loud but not whether a musical phrase is cut mid-figure. That
> remainder is **row UX23-R9**, with an owner, a landing slice and a
> completion definition, in `BUG_FIXES.md` §UX23-B — not a floating sentence.
>
> **Measured August 31, 2026, and it narrowed the row further (`tools/ux23_r9_phrase_probe.py`).** A phrase boundary is a gap materially longer than the gaps between notes, and that IS measurable from the uncapped renders. Where each cap falls:
>
> | cue | `max_s` | envelope at the cap | next phrase boundary |
> |---|---|---|---|
> | `reveille` | 4.2 s | 52% of peak | 6.28 s — 2.08 s out, past the fade |
> | `to_the_color` | 5.2 s | 8% of peak | 14.52 s — 9.32 s out |
> | `fanfare` | 5.2 s | 16% of peak | 5.40 s — 0.20 s out, INSIDE the fade |
>
> So `fanfare` already ends into a phrase break; **`to_the_color` has no phrase boundary within 9 s of its cap at all**, which makes the row's "move `max_s` to the next phrase boundary" instruction unsatisfiable for it — the 0.8 s fade is the only lever; and `reveille` alone has a real choice, at 6.28 s, costing a 7.1 s cue once per turn against 5.0 s today. **Nothing was retuned** — the ear still decides, but it now chooses between priced options.
>
> **The §3.5 audition gate has a structural blind spot, recorded here rather
> than treated as carelessness:** an audition hears each cue once, in
> isolation, judging character in the first second. It never sits through 38
> seconds and never stacks four copies. Length needs the automated pin above,
> not a listener.
>
> Still open, routed to `BUG_FIXES.md` §Live UX Report: there is **no stop API
> for one-shots** (`stop_loop` and friends iterate `_loop_players` only), so a
> cap shortens each instance but "closing the panel silences it" is still not
> true; and every notification refresh mints a new uuid while the client's
> chime dedupes on that id, so the desk bell re-rings per unmet marshal per
> turn.

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
| Button press | click | `ui/wood_tap_1/2/3.ogg` (rotate) — **re-cued Aug 8, 2026**: the user flagged the Interface-pack blips as "laser, not thematic" on the screen-nav buttons; the war room now clicks in wood (Kenney RPG `bookPlace1/2/3`, CC0, extract-unmodified + cue-rename). `click_primary/click_soft` stay on disk as pool variants |
| Chip / tab / small control | click2 | `ui/click_soft.ogg` or `tick_subtle.ogg` |
| List row select / map province click | select | `ui/leather_tap_1/2.ogg` (rotate) — same Aug-8 re-cue (Kenney RPG `handleSmallLeather1/2`); `select_item.ogg` stays as a pool variant |
| Toggle | toggle | `ui/toggle_switch.ogg` |
| Screen/panel open · close | panel | `ui/book_open.ogg` · `book_close.ogg` *(Aug 8 round 2: the Interface-pack `panel_open/close.ogg` whooshes read as "laser" on the ledger — the big screens open as the books they are; old files stay as pool variants)* |
| Map open · close (the two orphaned WAVs, finally assigned) | map | `ui/parchment_open_snd_use_map.wav` · `parchment_close_snd_close_map.wav` |
| Ledger/dispatch tab switch | page | `ui/page_turn_1/2/3.ogg` (rotate) |
| Campaign log open · close | book | `ui/book_open.ogg` · `book_close.ogg` |
| Modal dismiss / ESC | back | `ui/leather_tap_2.ogg` *(Aug 8 round 2 — same synth family as the panel whooshes; a dismissal is a leather tap now; `back_dismiss.ogg` stays as a pool variant)* |
| Accept / confirm | confirm | `ui/confirm_chime.ogg` |
| War-room transitions (optional flavor) | door | `ui/door_open_heavy.ogg` · `door_close_heavy.ogg` / `latch_close.ogg` |

### The music program
| Slot | Track(s) |
|---|---|
| Main theme / title | `theme_eroica_i.ogg` (fade or loop-trim ~4–5 min in) — **WIRED Aug 8, 2026**: the Main Menu (position 6) plays it on a dedicated AudioManager `"menu"` mood (a one-track rotation, so the refill-on-empty idiom loops it with a crossfade); entering the campaign hands off to peace/war via the existing first-war-data flip, and the theme doubles as the peace rotation's opener so the transition is musically continuous |
| Map, peace | rotate `calm_haydn_lark_adagio` · `calm_mozart40_andante` · `calm_goldberg_aria` (+ `wind_map_loop` bed when music paused) |
| Map, at war | `tension_coriolan.ogg`; field color: `fife_drum_brandywine` / `fife_drum_field_medley` / `fife_drum_warlike_medley` / `drums_rage_of_cornwallis` |
| France goes to war / Grande Armée moments | `marseillaise_navy_band.ogg`, `marche_militaire_francaise.mp3` |
| Victory (war won / triumph screen) | `triumph_eroica_iv_finale.ogg` |
| Defeat, marshal death, Paris falls | `lament_eroica_ii_marcia_funebre.ogg` |
| Night camp flavor (optional) | `ambient/campfire_loop.mp3` |

---

## §3 The wiring half — ✅ LANDED August 7, 2026 (landing record)

1. **`scripts/audio_manager.gd`** — **built as a `class_name` STATIC singleton, NOT
   a project.godot autoload** (recorded deviation with cause: the parse harness
   compiles scripts under a bare `--script` SceneTree where autoload globals do not
   resolve — `main.gd` failed compile with "Identifier not found" on the autoload
   route; the codebase's own `Utils`/`UiSettings` static idiom compiles in every
   context, so the manager follows it. A lazy instance node self-installs under the
   scene root; `main._ready()` calls `AudioManager.boot.call_deferred()`). Four
   runtime buses **Master/Music/SFX/UI**; cue registry (round-robin variants,
   per-cue dB trim + throttle — piece fleets and button spam collapse to one play);
   named ambient loops with runtime `loop=true` on OGG/MP3 streams; music program =
   **PEACE/WAR shuffled rotations with 2s crossfade**, a **one-shot overlay lane**
   (the anthem), `duck_music` refcount for the diorama, and `play_music_once` also
   exposing the RESERVED `triumph`/`lament` tracks for the Victory Pass.
2. **Settings**: four volume sliders (Master/Music/SFX/UI) on the pause menu,
   code-built beside the battle toggle, live-apply + persist via
   `UiSettings.get/set_audio_volume` (defaults 1.0/0.55/0.9/0.65). The `battle_sfx`
   toggle KEEPS its name and now gates every diorama-emitted cue (bed, volley,
   cavalry, verdict stings) exactly as it gated the cannon/drum.
3. **Seams landed** (~75 call sites, 27 scripts): the global BaseButton click hook
   (every button in every scene; CheckButton/CheckBox → toggle; opt-out
   `set_meta("no_click_sfx", true)`) · command send quill-flick + **scribble loop
   during the backend round-trip** (stop rides `set_input_enabled(true)`, the one
   chokepoint every response path passes) · refused command → soft error · end-turn
   snare roll · reveille (5s cap) on the morning dispatch · desk bell per NEW
   notification id · Mail Call on the letter-book raise · **war-driven music**: a war
   France had not seen → La Marseillaise overlay (the 1805 boot opener), a war
   concluded → fanfare, mood follows the live war count (`_process_active_wars`) ·
   wizard = panel + court-murmur loop · ledgers/screens = panel open/close +
   page-turn tabs · dispatch view = the two parchment WAVs (finally assigned) ·
   campaign log = book open/close · proposal result = quill-signature → wax seal
   (0.7s) or refusal tone · Proclamation = bells peal · petition/objection = sword
   draw · interrupt = drum sting · glorious charge = cavalry · rebellion = single
   toll · reward dialog = To the Color (6s cap) · capture = plunder coin-pour ·
   enemy phase = long march bed + distant cannon per battle line · war-table piece
   moves = throttled march cadence · diorama = music duck + battlefield bed (sea +
   creaks + ship's bell when naval), musket volley + cavalry/whinny by arms present,
   verdict typed over the quill scribble, triumph fanfare / defeat toll · pause menu
   = heavy doors, new-game paper crumple · save = confirm/error chimes · map wind
   bed from boot.
4. **Import**: `.import` sidecars committed for all 75 files (loops are set at
   RUNTIIME via the stream flag, so no import-option edits were needed).
5. ~~**▶ THE AUDITION GATE — the row's remaining work**~~ ✅ **PASSED August 7, 2026
   (user)**: the live play session was held; no cue failed audition, no trims or
   re-fetches were requested. The original-quality freesound re-fetch arm (§4) was
   not needed and is closed with the gate.
6. **The pool — DISPOSED WITH THE CLOSED GATE (Aug 14, 2026 health-check
   reconciliation): these files stay in the repo as VARIANTS ONLY.** The §3.5
   audition gate they were waiting on PASSED Aug 7, 2026 and requested no new
   wirings, so no seam-decision remains open and no future session owes them
   one; any later wiring is a fresh decision on its own merits, not a standing
   promise. Original sourcing note kept below for context: `command_ack` (order-executed feedback —
   the flick already marks the send; decide at audition), `coins_small` (awaits a
   clean payment-result seam), `musket_shot_1-3` (diorama cascade shots — audition
   call), `tick_subtle`/`latch_close`/`first_call`/`campfire_loop`/
   `quill_scribble_long`/`cannon_distant-as-cue`-in-terminal (alts and beds). The
   diorama's own `cannon_thud`/`drum_sting` calls were left on their original
   `_play_sound` path (now routed through the SFX bus).

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
