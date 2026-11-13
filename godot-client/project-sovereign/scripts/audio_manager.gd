extends Node
class_name AudioManager

# =============================================================================
# PROJECT SOVEREIGN — AudioManager (Music & Sound Core, wiring half)
# =============================================================================
# The game's audio engine, in the codebase's established singleton idiom
# (class_name statics, like Utils / UiSettings — NOT a project.godot autoload:
# the parse harness compiles scripts under a bare SceneTree where autoload
# globals never resolve, and this project's compile gate matters more than the
# autoload convenience). A lazy instance node self-installs under the scene
# root on first use; main.gd calls AudioManager.boot() once in _ready().
#
# Owns:
#   • the runtime buses  Master / Music / SFX / UI / Ambience / Ceremony
#     (created idempotently; volumes persisted through UiSettings, sliders in
#     Settings → SOUND). Session UI-5 (November 12, 2026): Ambience carries
#     every bed; Ceremony is a sub-bus of SFX for bugles, bells, fanfares and
#     stingers, and a sidechain compressor on Music dips the score under it;
#     a hard limiter on Master keeps stacked cues from clipping.
#   • the cue registry — every sourced file in assets/audio/ keyed by the
#     docs/MUSIC_SOUND_SPEC.md §2 cue map (variants round-robin; per-cue
#     trim + throttle so button spam or piece fleets never machine-gun;
#     UI-5: per-cue pitch / volume variation and a voice cap)
#   • the music program — menu / peace / war / crisis rotations with
#     crossfade and rests between pieces, a court scene for the Cabinet and
#     the Congress, a one-shot overlay lane (La Marseillaise, the courts'
#     anthems, the campaign end's triumph and lament), ducking for the
#     diorama, "now playing", a skip and the Music Room
#   • the ambience — the Emperor's study (wind, fire, clock), the season's
#     layer from the calendar, sparse distant drums while at war
#   • named loops (scribble / wind / sea / crowd / march / bed ...)
#   • the global hooks: every BaseButton clicks through one seam (node_added),
#     CheckButton/CheckBox get the toggle sound, any button can opt out with
#     set_meta("no_click_sfx", true); UI-5 adds the hover tick (opt-out
#     "no_hover_sfx"), a tick when a dropdown item is chosen and a soft tick
#     on a RichTextLabel link
#   • the window's focus: the game goes quieter (or mute) in the background
# Display-only (Golden Rule 6): nothing here reads or writes game state.
# =============================================================================

const AUDIO_ROOT := "res://assets/audio/"

# Cue registry: cue -> {files: [...], bus, db (trim), throttle_ms, max_s,
#                       start_s, pitch, vary_db, max_voices}
# `max_s` caps a one-shot that is LONGER THAN ITS MOMENT and fades it out over
# 0.8s (`_fade_stop`). Sourced CC0 assets are frequently whole ambiences rather
# than single hits — letter_open is 38.6s of paper, church_bells_peal is 77s —
# and a cue with no cap plays to the end of the file no matter how brief the
# interaction that fired it. Cap anything whose asset outlives its beat; leave
# it off when the file is already the right length.
# UI-5: `pitch` (± fraction of the playback rate) and `vary_db` (± dB) vary a
# repeated foley sound so the hundredth click is not the first one again;
# never on a bugle, bell or other music-like cue. `max_voices` caps how many
# copies of one cue may sound at once (a further play is skipped).
const CUES := {
	# ── UI chrome ──
	# Aug 8, 2026 (user): the Interface-pack synth blips read as "laser" on the
	# screen-nav buttons — the war room clicks in wood and leather now. The old
	# click_primary/click_soft/select_item files stay on disk as pool variants
	# (MUSIC_SOUND_SPEC §2 cue table carries the swap).
	"click": {"files": ["ui/wood_tap_1.ogg", "ui/wood_tap_2.ogg", "ui/wood_tap_3.ogg"], "bus": "UI", "db": -7.0, "throttle_ms": 90, "pitch": 0.04, "vary_db": 1.5, "max_voices": 3},
	"toggle": {"files": ["ui/toggle_switch.ogg"], "bus": "UI", "db": -7.0, "throttle_ms": 90},
	"select": {"files": ["ui/leather_tap_1.ogg", "ui/leather_tap_2.ogg"], "bus": "UI", "db": -7.0, "throttle_ms": 120, "pitch": 0.04, "vary_db": 1.0},
	"tick": {"files": ["ui/tick_subtle.ogg"], "bus": "UI", "db": -14.0, "throttle_ms": 90, "pitch": 0.05},
	# UI-5: the hover tick — the quietest sound in the game, and throttled so a
	# sweep across a row of buttons is one soft brush, not a drum roll.
	"hover": {"files": ["ui/hover_tick.ogg", "ui/hover_tick_2.ogg"], "bus": "UI", "db": -22.0, "throttle_ms": 70, "pitch": 0.06, "vary_db": 1.5, "max_voices": 1},
	"confirm": {"files": ["ui/confirm_chime.ogg"], "bus": "UI", "db": -5.0},
	"error": {"files": ["ui/error_soft.ogg"], "bus": "UI", "db": -5.0},
	"question": {"files": ["ui/question_open.ogg"], "bus": "UI", "db": -5.0},
	# Aug 8, 2026 (user, round 2): the panel/dismiss whooshes were the LAST
	# Interface-pack synths on the screen-nav path — opening the ledger still
	# read as "laser". The big screens now open and close as the books they
	# are, and a dismissal is a leather tap. Old files stay on disk as pool
	# variants (MUSIC_SOUND_SPEC §2 carries the swap).
	"panel_open": {"files": ["ui/book_open.ogg"], "bus": "UI", "db": -7.0, "throttle_ms": 200},
	"panel_close": {"files": ["ui/book_close.ogg"], "bus": "UI", "db": -7.0, "throttle_ms": 200},
	"back": {"files": ["ui/leather_tap_2.ogg"], "bus": "UI", "db": -8.0, "throttle_ms": 200, "pitch": 0.03},
	"page_turn": {"files": ["ui/page_turn_1.ogg", "ui/page_turn_2.ogg", "ui/page_turn_3.ogg"], "bus": "UI", "db": -7.0, "throttle_ms": 150, "pitch": 0.04, "vary_db": 1.0},
	"book_open": {"files": ["ui/book_open.ogg"], "bus": "UI", "db": -7.0},
	"book_close": {"files": ["ui/book_close.ogg"], "bus": "UI", "db": -7.0},
	"parchment_open": {"files": ["ui/parchment_open_snd_use_map.wav"], "bus": "UI", "db": -7.0},
	"parchment_close": {"files": ["ui/parchment_close_snd_close_map.wav"], "bus": "UI", "db": -8.0},
	"door_open": {"files": ["ui/door_open_heavy.ogg"], "bus": "UI", "db": -7.0},
	"door_close": {"files": ["ui/door_close_heavy.ogg"], "bus": "UI", "db": -7.0},
	"latch": {"files": ["ui/latch_close.ogg"], "bus": "UI", "db": -7.0},
	"cloth": {"files": ["ui/cloth_rustle.ogg"], "bus": "UI", "db": -9.0, "throttle_ms": 200},
	# UI-5: the map's paper (a wheel zoom), an envoy's knock, the Congress gavel.
	"paper_slide": {"files": ["ui/paper_slide.ogg"], "bus": "UI", "db": -13.0, "throttle_ms": 260, "pitch": 0.05, "vary_db": 1.5, "max_voices": 1},
	"door_knock": {"files": ["ui/door_knock.ogg"], "bus": "UI", "db": -4.0, "throttle_ms": 600, "max_s": 2.4},
	"gavel": {"files": ["ui/gavel.ogg"], "bus": "UI", "db": -4.0, "throttle_ms": 600, "max_s": 0.9, "fade_s": 0.25},
	# ── the desk: command flow, paper, seal ──
	"quill_flick": {"files": ["ui/quill_flick.mp3"], "bus": "UI", "db": -6.0, "pitch": 0.03},
	"quill_sign": {"files": ["ui/quill_sign.mp3"], "bus": "UI", "db": -5.0},
	"wax_seal": {"files": ["ui/wax_seal.mp3"], "bus": "UI", "db": -4.0},
	"command_ack": {"files": ["ui/command_ack_click.ogg"], "bus": "UI", "db": -6.0, "throttle_ms": 150, "pitch": 0.03},
	"letter_open": {"files": ["ui/letter_open.mp3"], "bus": "UI", "db": -7.0, "throttle_ms": 300, "max_s": 1.4, "start_s": 1.9},
	"paper_crumple": {"files": ["ui/paper_crumple.mp3"], "bus": "UI", "db": -5.0, "max_s": 2.4},
	"notification": {"files": ["ui/notification_bell.mp3"], "bus": "UI", "db": -5.0, "throttle_ms": 400},
	# UI-5: a notice's priority is heard — 1 adds the ship's bell, 2 is the
	# Assembly call (the bar hints the priority; `play("notification")` reads it).
	"notification_high": {"files": ["ambient/ship_bell.mp3"], "bus": "Ceremony", "db": -5.0, "throttle_ms": 800, "max_s": 2.6},
	"notification_critical": {"files": ["music/bugle_assembly.mp3"], "bus": "Ceremony", "db": -3.0, "throttle_ms": 2500, "max_s": 3.2},
	"coins_small": {"files": ["ui/coins_small.ogg", "ui/coins_small_2.ogg"], "bus": "UI", "db": -5.0, "pitch": 0.04, "vary_db": 1.0},
	"coin_pour": {"files": ["ui/coin_pour.mp3"], "bus": "UI", "db": -5.0, "max_s": 3.0},
	"end_turn": {"files": ["ui/end_turn_drum_roll.mp3"], "bus": "UI", "db": -5.0},
	# ── battle ──
	"cannon": {"files": ["battle/cannon_thud.ogg"], "bus": "SFX", "db": 0.0, "pitch": 0.03},
	"cannon_distant": {"files": ["battle/cannon_distant.ogg"], "bus": "SFX", "db": -7.0, "throttle_ms": 300, "pitch": 0.05, "vary_db": 2.0},
	"drum_sting": {"files": ["battle/drum_sting.wav"], "bus": "Ceremony", "db": -1.0},
	"musket_volley": {"files": ["battle/musket_battle_volley.mp3"], "bus": "SFX", "db": -2.0, "max_s": 4.2},
	"musket_shot": {"files": ["battle/musket_shot_1.ogg", "battle/musket_shot_2.ogg", "battle/musket_shot_3.ogg"], "bus": "SFX", "db": -5.0, "throttle_ms": 120, "pitch": 0.05, "vary_db": 2.0},
	"cavalry": {"files": ["battle/cavalry_gallop.mp3"], "bus": "SFX", "db": -2.0, "max_s": 3.2, "start_s": 4.6},
	"whinny": {"files": ["battle/horse_whinny.ogg"], "bus": "SFX", "db": -6.0},
	"sword_draw": {"files": ["battle/sword_draw.mp3"], "bus": "SFX", "db": -3.0, "max_s": 2.4},
	"march_step": {"files": ["battle/army_march_loop_short.mp3"], "bus": "SFX", "db": -12.0, "throttle_ms": 1500, "max_s": 0.65},
	# ── UI-5: an order heard as it is carried out (`play_result`) ──
	"order_march": {"files": ["battle/army_march_loop_short.mp3"], "bus": "SFX", "db": -7.0, "throttle_ms": 400, "max_s": 1.4},
	"spade": {"files": ["battle/spade_dig.ogg"], "bus": "SFX", "db": -5.0, "throttle_ms": 400, "max_s": 2.4, "pitch": 0.04},
	"drum_cadence": {"files": ["battle/drum_cadence.ogg"], "bus": "SFX", "db": -5.0, "throttle_ms": 600, "max_s": 3.0},
	"hammer": {"files": ["battle/hammer.ogg", "battle/saw.ogg"], "bus": "SFX", "db": -5.0, "throttle_ms": 400, "max_s": 2.6, "pitch": 0.03},
	"horse_trot": {"files": ["battle/horse_trot.ogg"], "bus": "SFX", "db": -5.0, "throttle_ms": 400, "max_s": 2.6, "pitch": 0.03},
	"boots": {"files": ["battle/boots_halt.ogg"], "bus": "SFX", "db": -6.0, "throttle_ms": 250, "max_s": 1.6, "pitch": 0.04, "vary_db": 1.5},
	"bugle_to_arms": {"files": ["music/bugle_fix_bayonets.mp3"], "bus": "Ceremony", "db": -3.0, "throttle_ms": 2000, "max_s": 3.2, "fade_s": 1.2, "max_voices": 1},
	"bugle_charge": {"files": ["music/bugle_fix_bayonets.mp3"], "bus": "Ceremony", "db": -2.0, "throttle_ms": 2000, "max_s": 3.2, "fade_s": 1.2, "max_voices": 1},
	"bugle_retreat": {"files": ["music/bugle_tattoo.mp3"], "bus": "Ceremony", "db": -4.0, "throttle_ms": 2000, "max_s": 3.2, "fade_s": 1.2, "max_voices": 1},
	# ── world / ceremony ──
	"bells_peal": {"files": ["ambient/church_bells_peal.mp3"], "bus": "Ceremony", "db": -1.0, "max_s": 5.2},
	"bell_toll": {"files": ["ambient/bell_toll_single.mp3"], "bus": "Ceremony", "db": -2.0, "max_s": 3.2, "throttle_ms": 2500, "max_voices": 1},
	"ship_bell": {"files": ["ambient/ship_bell.mp3"], "bus": "Ceremony", "db": -4.0, "throttle_ms": 400},
	"crowd_cheer": {"files": ["ambient/crowd_cheer.ogg"], "bus": "Ceremony", "db": -3.0, "throttle_ms": 1500, "max_s": 3.2, "max_voices": 1},
	"distant_drums": {"files": ["ambient/distant_drums.ogg"], "bus": "Ambience", "db": -13.0, "throttle_ms": 8000, "max_s": 3.2, "pitch": 0.03, "vary_db": 2.0},
	# ── field music used as one-shot cues (capped where long) ──
	"reveille": {"files": ["music/bugle_reveille.ogg"], "bus": "Ceremony", "db": -4.0, "throttle_ms": 2000, "max_s": 4.2, "fade_s": 2.0},
	"mail_call": {"files": ["music/bugle_mail_call.ogg"], "bus": "Ceremony", "db": -4.0, "throttle_ms": 2000},
	"first_call": {"files": ["music/bugle_first_call.mp3"], "bus": "Ceremony", "db": -4.0, "max_s": 4.2},
	"to_the_color": {"files": ["music/bugle_to_the_color.ogg"], "bus": "Ceremony", "db": -3.0, "max_s": 5.2, "fade_s": 2.0},
	"fanfare": {"files": ["music/fanfare_erafnaf.ogg"], "bus": "Ceremony", "db": -1.0, "throttle_ms": 2000, "max_s": 5.2},
}

# Named ambient loops: tag -> {file, bus, db}
# UI-5: every bed rides the Ambience bus (its own slider); the two quill loops
# stay on UI — they are the desk's work, not the room. The diorama's verdict
# has its OWN scribble tag: one shared tag let the tableau's close cut the
# command line's quill mid-order.
const LOOPS := {
	# UI-5: the loops' seams measured (tools/ui5_audio_prep.py) — both quill
	# takes stepped 21–24 dB where they wrapped, and seven more (the creak, the
	# crowd, the march, the battle bed, the fire, the rain, the winter wind)
	# stepped 8–30 dB or clicked; their "_seamless" re-makes blend the tail
	# into the head (the originals stay on disk). The clock wraps on its beat.
	"scribble": {"file": "ui/quill_scribble_loop_seamless.ogg", "bus": "UI", "db": -13.0},
	"scribble_long": {"file": "ui/quill_scribble_long_seamless.ogg", "bus": "UI", "db": -15.0},
	"scribble_verdict": {"file": "ui/quill_scribble_loop_seamless.ogg", "bus": "UI", "db": -13.0},
	"wind": {"file": "ambient/wind_map_loop.mp3", "bus": "Ambience", "db": -18.0},
	"sea": {"file": "ambient/sea_loop.mp3", "bus": "Ambience", "db": -11.0},
	"creak": {"file": "ambient/ship_creak_1_seamless.ogg", "bus": "Ambience", "db": -17.0},
	"crowd": {"file": "ambient/crowd_murmur_seamless.ogg", "bus": "Ambience", "db": -15.0},
	"march": {"file": "battle/army_march_loop_short_seamless.ogg", "bus": "Ambience", "db": -11.0},
	"march_long": {"file": "battle/army_march.mp3", "bus": "Ambience", "db": -11.0},
	"battle_bed": {"file": "battle/battlefield_ambience_seamless.ogg", "bus": "Ambience", "db": -11.0},
	"campfire": {"file": "ambient/campfire_loop.mp3", "bus": "Ambience", "db": -19.0},
	# UI-5: the Emperor's study and its seasons.
	"fire": {"file": "ambient/fire_loop_seamless.ogg", "bus": "Ambience", "db": -20.0},
	"clock": {"file": "ambient/clock_loop.ogg", "bus": "Ambience", "db": -26.0},
	"birds": {"file": "ambient/birds_loop.ogg", "bus": "Ambience", "db": -20.0},
	"rain": {"file": "ambient/rain_loop_seamless.ogg", "bus": "Ambience", "db": -18.0},
	"winter_wind": {"file": "ambient/winter_wind_loop_seamless.ogg", "bus": "Ambience", "db": -16.0},
}

# The music program (docs/MUSIC_SOUND_SPEC.md §2, §6). Rotations crossfade on
# mood change and advance on track end — after a rest of ambience when the
# player keeps "Pauses between pieces" on (UI-5). "menu" is the Main Menu's
# slot (position 6): the §2 title theme, alone in its rotation so the
# refill-on-empty behaviour loops it with a crossfade.
# UI-5: the war rotation no longer plays the American fife tunes (Brandywine,
# the "Yankee Doodle" medley, the medley on the Marines' Hymn melody); their
# files stay on disk. "crisis" is the war going badly; "court" is the scene
# the Cabinet and the Congress push while they are open.
const MUSIC := {
	"menu": ["music/theme_eroica_i.ogg"],
	"peace": ["music/theme_eroica_i.ogg", "music/calm_haydn_lark_adagio.ogg",
			"music/calm_mozart40_andante.ogg", "music/calm_goldberg_aria.mp3",
			"music/peace_mozart_k465_ii.ogg", "music/peace_mozart_k421_ii.ogg",
			"music/peace_magic_flute_overture.ogg"],
	"war": ["music/tension_coriolan.ogg", "music/drums_rage_of_cornwallis.ogg",
			"music/marche_militaire_francaise.mp3", "music/war_egmont.ogg",
			"music/war_beethoven5_i.ogg", "music/war_eroica_iii.ogg"],
	"crisis": ["music/crisis_mozart40_i.ogg", "music/war_beethoven5_i.ogg",
			"music/tension_coriolan.ogg", "music/crisis_mozart40_iv.ogg"],
	"court": ["music/court_figaro_overture.ogg", "music/court_mozart40_iii.ogg",
			"music/court_haydn_lark_i.ogg", "music/court_mozart_quartet.ogg",
			"music/court_beethoven_op18_6_ii.ogg"],
}
const MUSIC_ONESHOTS := {
	"marseillaise": "music/marseillaise_navy_band.ogg",
	"triumph": "music/triumph_eroica_iv_finale.ogg",
	"lament": "music/lament_eroica_ii_marcia_funebre.ogg",
}
# UI-5: the courts' anthems — ONLY tunes in use in 1805 (docs/MUSIC_SOUND_SPEC
# §6): Haydn's Kaiserhymne (1797) for Austria; God Save the King for Britain
# and, on the same tune, Prussia's "Heil dir im Siegerkranz", Hanover's and
# Sweden's "Bevare Gud vår kung" (1805); the Marcha Real; the Wilhelmus; the
# Polish Legions' Mazurka (1797) for the Duchy of Warsaw. A court missing here
# is heard as the drum sting.
const ANTHEMS := {
	"Austria": "music/anthem_austria_kaiserhymne.ogg",
	"Britain": "music/anthem_britain_god_save.ogg",
	"Prussia": "music/anthem_britain_god_save.ogg",
	"Hanover": "music/anthem_britain_god_save.ogg",
	"Sweden": "music/anthem_britain_god_save.ogg",
	"Spain": "music/anthem_spain_marcha_real.ogg",
	"Holland": "music/anthem_holland_wilhelmus.ogg",
	"Denmark": "music/anthem_denmark_kong_christian.ogg",
	"DuchyOfWarsaw": "music/anthem_warsaw_dabrowski.ogg",
	"Warsaw": "music/anthem_warsaw_dabrowski.ogg",
	"Poland": "music/anthem_warsaw_dabrowski.ogg",
}
const ANTHEM_CAP_S := 20.0
const ANTHEM_FADE_S := 3.0

# UI-5: what the Music Room and "Now playing" say about each piece. Every
# recording is public domain (THIRD_PARTY_LICENSES.md carries the source).
const MUSIC_META := {
	"music/theme_eroica_i.ogg": {"title": "Symphony No. 3 \"Eroica\" — I. Allegro con brio", "composer": "Beethoven", "year": 1804, "performer": "Musopen Symphony Orchestra"},
	"music/calm_haydn_lark_adagio.ogg": {"title": "String Quartet Op. 64 No. 5 \"The Lark\" — II. Adagio cantabile", "composer": "Haydn", "year": 1790, "performer": "Musopen String Quartet"},
	"music/calm_mozart40_andante.ogg": {"title": "Symphony No. 40 — II. Andante", "composer": "Mozart", "year": 1788, "performer": "Musopen Symphony Orchestra"},
	"music/calm_goldberg_aria.mp3": {"title": "Goldberg Variations — Aria", "composer": "Bach", "year": 1741, "performer": "Kimiko Ishizaka"},
	"music/tension_coriolan.ogg": {"title": "Coriolan Overture", "composer": "Beethoven", "year": 1807, "performer": "Musopen Symphony Orchestra"},
	"music/drums_rage_of_cornwallis.ogg": {"title": "Drum feature: The Rage of Cornwallis", "composer": "Traditional", "year": 1781, "performer": "US Army Old Guard Fife and Drum Corps"},
	"music/marche_militaire_francaise.mp3": {"title": "Marche militaire française", "composer": "Saint-Saëns", "year": 1880, "performer": "US Marine Band"},
	"music/fife_drum_brandywine.ogg": {"title": "Brandywine Quickstep", "composer": "Traditional", "year": 1777, "performer": "US Army Old Guard Fife and Drum Corps"},
	"music/fife_drum_field_medley.ogg": {"title": "Field medley", "composer": "Traditional", "year": 1776, "performer": "US Army Old Guard Fife and Drum Corps"},
	"music/fife_drum_warlike_medley.ogg": {"title": "Warlike medley", "composer": "Traditional", "year": 1776, "performer": "US Army Old Guard Fife and Drum Corps"},
	"music/peace_mozart_k465_ii.ogg": {"title": "String Quartet No. 19 in C, K465 \"Dissonance\" — II. Andante cantabile", "composer": "Mozart", "year": 1785, "performer": "Musopen String Quartet"},
	"music/peace_mozart_k421_ii.ogg": {"title": "String Quartet No. 15 in D minor, K421 — II. Andante", "composer": "Mozart", "year": 1783, "performer": "Musopen String Quartet"},
	"music/peace_magic_flute_overture.ogg": {"title": "Die Zauberflöte — Overture", "composer": "Mozart", "year": 1791, "performer": "Musopen Symphony Orchestra"},
	"music/war_egmont.ogg": {"title": "Egmont Overture", "composer": "Beethoven", "year": 1810, "performer": "Musopen Symphony Orchestra"},
	"music/war_beethoven5_i.ogg": {"title": "Symphony No. 5 — I. Allegro con brio", "composer": "Beethoven", "year": 1808, "performer": "Skidmore College Orchestra (Musopen)"},
	"music/war_eroica_iii.ogg": {"title": "Symphony No. 3 \"Eroica\" — III. Scherzo", "composer": "Beethoven", "year": 1804, "performer": "Musopen Symphony Orchestra"},
	"music/crisis_mozart40_i.ogg": {"title": "Symphony No. 40 — I. Molto allegro", "composer": "Mozart", "year": 1788, "performer": "Musopen Symphony Orchestra"},
	"music/crisis_mozart40_iv.ogg": {"title": "Symphony No. 40 — IV. Allegro assai", "composer": "Mozart", "year": 1788, "performer": "Musopen Symphony Orchestra"},
	"music/court_figaro_overture.ogg": {"title": "Le nozze di Figaro — Overture", "composer": "Mozart", "year": 1786, "performer": "Musopen Symphony Orchestra"},
	"music/court_mozart40_iii.ogg": {"title": "Symphony No. 40 — III. Menuetto", "composer": "Mozart", "year": 1788, "performer": "Musopen Symphony Orchestra"},
	"music/court_haydn_lark_i.ogg": {"title": "String Quartet Op. 64 No. 5 \"The Lark\" — I. Allegro moderato", "composer": "Haydn", "year": 1790, "performer": "Musopen String Quartet"},
	"music/court_mozart_quartet.ogg": {"title": "String Quartet No. 15 in D minor, K421 — III. Menuetto", "composer": "Mozart", "year": 1783, "performer": "Musopen String Quartet"},
	"music/court_beethoven_op18_6_ii.ogg": {"title": "String Quartet Op. 18 No. 6 — II. Adagio ma non troppo", "composer": "Beethoven", "year": 1800, "performer": "Musopen String Quartet"},
	"music/marseillaise_navy_band.ogg": {"title": "La Marseillaise", "composer": "Rouget de Lisle", "year": 1792, "performer": "US Navy Band"},
	"music/triumph_eroica_iv_finale.ogg": {"title": "Symphony No. 3 \"Eroica\" — IV. Finale", "composer": "Beethoven", "year": 1804, "performer": "Musopen Symphony Orchestra"},
	"music/lament_eroica_ii_marcia_funebre.ogg": {"title": "Symphony No. 3 \"Eroica\" — II. Marcia funebre", "composer": "Beethoven", "year": 1804, "performer": "Musopen Symphony Orchestra"},
	"music/anthem_austria_kaiserhymne.ogg": {"title": "Gott erhalte Franz den Kaiser", "composer": "Haydn", "year": 1797, "performer": "US Navy Band"},
	"music/anthem_britain_god_save.ogg": {"title": "God Save the King", "composer": "Traditional", "year": 1745, "performer": "US Navy Band"},
	"music/anthem_spain_marcha_real.ogg": {"title": "Marcha Real", "composer": "Traditional", "year": 1770, "performer": "US Navy Band"},
	"music/anthem_holland_wilhelmus.ogg": {"title": "Het Wilhelmus", "composer": "Traditional", "year": 1572, "performer": "US Navy Band"},
	"music/anthem_warsaw_dabrowski.ogg": {"title": "Mazurek Dąbrowskiego", "composer": "Traditional", "year": 1797, "performer": "US Navy Band"},
	"music/anthem_denmark_kong_christian.ogg": {"title": "Kong Christian stod ved højen mast", "composer": "Traditional", "year": 1779, "performer": "US Navy Band"},
}
# UI-5: the measured loudness of every file, as trims (docs/MUSIC_SOUND_SPEC
# §6). FILE_TRIM_DB brings each cue / loop file to one reference loudness
# (a cue's "db" is then its class level on the ladder: interface quiet <
# effects < ceremony); MUSIC_TRIM_DB brings every piece to one target, so the
# rotation never jumps 11 LU from a string quartet to an overture.
# <ui5-trims> generated by tools/ui5_audio_prep.py --apply from
# docs/audits/audio_loudness_2026_11_12.json — do not edit by hand.
const FILE_TRIM_DB := {
	"ambient/bell_toll_single.mp3": -3.6,
	"ambient/birds_loop.ogg": 5.4,
	"ambient/campfire_loop.mp3": 3.0,
	"ambient/church_bells_peal.mp3": -6.3,
	"ambient/clock_loop.ogg": 15.3,
	"ambient/crowd_cheer.ogg": 4.5,
	"ambient/crowd_murmur_seamless.ogg": 12.7,
	"ambient/distant_drums.ogg": -5.3,
	"ambient/fire_loop_seamless.ogg": 4.3,
	"ambient/rain_loop_seamless.ogg": -3.9,
	"ambient/sea_loop.mp3": 16.5,
	"ambient/ship_bell.mp3": 3.4,
	"ambient/ship_creak_1_seamless.ogg": 0.2,
	"ambient/wind_map_loop.mp3": 18.3,
	"ambient/winter_wind_loop_seamless.ogg": -8.0,
	"battle/army_march.mp3": 8.8,
	"battle/army_march_loop_short.mp3": 13.8,
	"battle/army_march_loop_short_seamless.ogg": 14.2,
	"battle/battlefield_ambience_seamless.ogg": -1.9,
	"battle/boots_halt.ogg": 1.6,
	"battle/cannon_distant.ogg": -1.1,
	"battle/cannon_thud.ogg": -1.1,
	"battle/cavalry_gallop.mp3": -2.5,
	"battle/drum_cadence.ogg": 3.5,
	"battle/drum_sting.wav": 0.7,
	"battle/hammer.ogg": 2.4,
	"battle/horse_trot.ogg": -1.1,
	"battle/horse_whinny.ogg": 6.0,
	"battle/musket_battle_volley.mp3": -8.5,
	"battle/musket_shot_1.ogg": 1.0,
	"battle/musket_shot_2.ogg": -1.0,
	"battle/musket_shot_3.ogg": 3.4,
	"battle/saw.ogg": 6.5,
	"battle/spade_dig.ogg": 17.9,
	"battle/sword_draw.mp3": 3.3,
	"music/bugle_assembly.mp3": -4.1,
	"music/bugle_first_call.mp3": -0.6,
	"music/bugle_fix_bayonets.mp3": -7.3,
	"music/bugle_mail_call.ogg": -6.1,
	"music/bugle_reveille.ogg": -1.4,
	"music/bugle_tattoo.mp3": -3.3,
	"music/bugle_to_the_color.ogg": -2.7,
	"music/fanfare_erafnaf.ogg": -5.4,
	"ui/book_close.ogg": -3.9,
	"ui/book_open.ogg": 10.5,
	"ui/cloth_rustle.ogg": 6.7,
	"ui/coin_pour.mp3": -6.3,
	"ui/coins_small.ogg": -1.2,
	"ui/coins_small_2.ogg": 7.9,
	"ui/command_ack_click.ogg": 5.9,
	"ui/confirm_chime.ogg": -6.8,
	"ui/door_close_heavy.ogg": -4.9,
	"ui/door_knock.ogg": 21.7,
	"ui/door_open_heavy.ogg": -3.3,
	"ui/end_turn_drum_roll.mp3": -0.7,
	"ui/error_soft.ogg": -6.9,
	"ui/gavel.ogg": -1.7,
	"ui/hover_tick.ogg": -4.4,
	"ui/hover_tick_2.ogg": -5.7,
	"ui/latch_close.ogg": -5.7,
	"ui/leather_tap_1.ogg": 10.6,
	"ui/leather_tap_2.ogg": 15.4,
	"ui/letter_open.mp3": -0.9,
	"ui/notification_bell.mp3": -4.5,
	"ui/page_turn_1.ogg": -1.5,
	"ui/page_turn_2.ogg": 7.3,
	"ui/page_turn_3.ogg": 3.6,
	"ui/paper_crumple.mp3": -1.8,
	"ui/paper_slide.ogg": 30.9,
	"ui/parchment_close_snd_close_map.wav": -1.0,
	"ui/parchment_open_snd_use_map.wav": -2.9,
	"ui/question_open.ogg": -9.4,
	"ui/quill_flick.mp3": 21.8,
	"ui/quill_scribble_long_seamless.ogg": -1.4,
	"ui/quill_scribble_loop.ogg": 15.2,
	"ui/quill_scribble_loop_seamless.ogg": 15.0,
	"ui/quill_sign.mp3": 9.9,
	"ui/quill_strokes.ogg": -0.5,
	"ui/tick_subtle.ogg": -4.4,
	"ui/toggle_switch.ogg": -0.1,
	"ui/wax_seal.mp3": 9.0,
	"ui/wood_tap_1.ogg": -5.3,
	"ui/wood_tap_2.ogg": -4.9,
	"ui/wood_tap_3.ogg": -5.8,
}
const MUSIC_TRIM_DB := {
	"music/anthem_austria_kaiserhymne.ogg": -1.0,
	"music/anthem_britain_god_save.ogg": -5.2,
	"music/anthem_denmark_kong_christian.ogg": -3.5,
	"music/anthem_holland_wilhelmus.ogg": -4.9,
	"music/anthem_spain_marcha_real.ogg": -3.8,
	"music/anthem_warsaw_dabrowski.ogg": -4.6,
	"music/calm_goldberg_aria.mp3": 7.6,
	"music/calm_haydn_lark_adagio.ogg": 5.7,
	"music/calm_mozart40_andante.ogg": 1.0,
	"music/court_beethoven_op18_6_ii.ogg": 5.1,
	"music/court_figaro_overture.ogg": -2.9,
	"music/court_haydn_lark_i.ogg": 3.3,
	"music/court_mozart40_iii.ogg": 0.2,
	"music/court_mozart_quartet.ogg": 5.1,
	"music/crisis_mozart40_i.ogg": -2.0,
	"music/crisis_mozart40_iv.ogg": -1.8,
	"music/drums_rage_of_cornwallis.ogg": 1.5,
	"music/lament_eroica_ii_marcia_funebre.ogg": 2.0,
	"music/marche_militaire_francaise.mp3": 2.9,
	"music/marseillaise_navy_band.ogg": -2.6,
	"music/peace_magic_flute_overture.ogg": -4.7,
	"music/peace_mozart_k421_ii.ogg": 4.8,
	"music/peace_mozart_k465_ii.ogg": 2.3,
	"music/tension_coriolan.ogg": -3.8,
	"music/theme_eroica_i.ogg": -0.6,
	"music/triumph_eroica_iv_finale.ogg": -0.2,
	"music/war_beethoven5_i.ogg": 3.4,
	"music/war_egmont.ogg": -3.9,
	"music/war_eroica_iii.ogg": 0.4,
}
# </ui5-trims>

# How the Music Room groups the pieces, in the order it lists them.
const MUSIC_ROOM_SITUATIONS := [
	["menu", "The title"], ["peace", "Peace"], ["war", "War"], ["crisis", "Crisis"],
	["court", "The court"], ["oneshot", "Ceremonies"], ["anthem", "The courts' anthems"],
]

const MUSIC_DB := -10.0        # base trim under the Music bus
const CROSSFADE_S := 2.0
const SCENE_CROSSFADE_S := 3.0
const SCENE_DELAY_S := 4.0     # a court scene waits this long open before it plays (no flicker on a peek)
const DUCK_DB := -14.0         # extra music attenuation while the diorama holds the stage
const MAX_ONESHOT_PLAYERS := 14
# UI-5: France's worst war score at or under this is the crisis mood.
const CRISIS_SCORE := -30
# UI-5: the rests between pieces, in seconds (min, max) per mood.
const REST_RANGES := {"peace": [25.0, 70.0], "war": [25.0, 70.0], "crisis": [10.0, 30.0]}
# UI-5: the window in the background — "quiet" lowers Master by this much.
const BACKGROUND_QUIET_DB := -12.0
# UI-5: the war layer of the study — a distant drum or gun every so often.
const WAR_LAYER_GAP_S := [60.0, 120.0]
# UI-5: the season's layer, by calendar month (the top bar's own label).
const SEASON_OF_MONTH := {
	"january": "winter", "february": "winter", "march": "spring", "april": "spring",
	"may": "spring", "june": "summer", "july": "summer", "august": "summer",
	"september": "autumn", "october": "autumn", "november": "autumn", "december": "winter",
}
const SEASON_LAYER := {"spring": "birds", "summer": "birds", "autumn": "rain", "winter": "winter_wind"}
# UI-5: the order heard as it is carried out — verb -> cue (`play_result`).
const RESULT_CUES := {
	"move": "order_march", "march": "order_march", "move_to": "order_march",
	"pursue": "order_march", "support": "boots", "follow": "boots",
	"attack": "bugle_to_arms", "charge": "bugle_charge", "bombard": "cannon",
	"fortify": "spade", "unfortify": "spade", "drill": "drum_cadence",
	"recruit": "coins_small", "recruit_marshal": "coins_small", "garrison": "boots",
	"build": "hammer", "repair": "hammer", "watchtower": "hammer",
	"scout": "horse_trot", "retreat": "bugle_retreat", "defend": "latch",
	"hold": "latch", "wait": "tick", "stance_change": "tick", "form_square": "drum_cadence",
}
# UI-5: the quill's nib under the command line — a slice of a writing take.
const NIB_FILES := ["ui/quill_strokes.ogg", "ui/quill_scribble_loop.ogg"]
const NIB_DB := -18.0
const NIB_THROTTLE_MS := 35

static var _instance: AudioManager = null
# UI-5: the priority a notice hinted just before `play("notification")`, and
# when (a hint older than a breath is stale — a silent fill never plays).
static var _notify_hint_priority := 0
static var _notify_hint_ms := 0

var _streams: Dictionary = {}          # path -> AudioStream (lazy store)
var _rr: Dictionary = {}               # cue -> next round-robin index
var _last_played_ms: Dictionary = {}   # cue -> tick of last play (throttle)
var _loop_players: Dictionary = {}     # tag -> AudioStreamPlayer
# UX23-R1: cue -> [AudioStreamPlayer]. `_play_cue` kept NO handle on the
# one-shot it created, so nothing outside it could silence a cue early —
# and one-shots are children of this singleton, not of the scene, so they
# outlive `change_scene_to_file` as well as the panel that started them.
var _live_players: Dictionary = {}
var _oneshot_count: int = 0

var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _music_active_is_a := true
var _music_mood := ""                  # "", "menu", "peace", "war", "crisis"
var _music_rotation_key := ""          # the rotation the queue was drawn from
var _music_queue: Array = []           # shuffled remainder of the mood's rotation
var _music_overlay: AudioStreamPlayer  # one-shot lane (anthem); rotation pauses under it
var _overlay_key := ""                 # what the overlay lane is playing ("" = nothing)
var _overlay_token := 0                # bumps per overlay start: a stale cap timer no-ops
var _duck_depth := 0                   # diorama duck refcount
var _at_war := false
var _worst_war_score := 0
var _scene_stack: Array = []           # pushed scenes, top last ("court")
var _scene_requests: Dictionary = {}   # scene -> open requests (refcount)
var _scene_pending: Dictionary = {}    # scene -> request token while its delay runs
var _scene_token := 0
var _room_pick := ""                   # a Music Room choice playing now ("" = the situation)
var _resting := false
var _rest_timer: Timer
var _current_track := ""               # the file on the active rotation player
var _focus_offset_db := 0.0
# UI-5 review: the diorama's duck is an offset on the Music BUS (it once
# tweened each player's volume, and a crossfade tween writing the same
# player lost or stuck it); the crossfade's own tween is held so a second
# switch inside its window kills the first (whose delayed stop() would
# otherwise silence the player the second switch had just started).
var _duck_offset_db := 0.0
var _music_fade: Tween = null
var _nib_last_ms := 0
# The ambience: which layers the study wants now.
var _ambience_on := false
var _season := ""
var _war_layer_timer: Timer


# ── the static face (the game calls these; all compile-safe, all null-safe) ──

static func boot() -> void:
	"""Called once from main._ready(): installs the instance, starts the
	study's bed; music mood follows the first live war data. Idempotent —
	the world swap calls `start_ambience()` again after it silenced every
	loop (the dead-wind defect, UI-5)."""
	var inst := _inst()
	if inst == null:
		return
	inst._start_ambience()


static func start_ambience() -> void:
	var inst := _inst()
	if inst != null:
		inst._start_ambience()


static func stop_ambience() -> void:
	var inst := _inst()
	if inst != null:
		inst._stop_ambience()


static func set_calendar_label(label: String) -> void:
	"""The top bar's date ("September 1805") sets the season's layer."""
	var inst := _inst()
	if inst != null:
		inst._set_season_from_label(label)


static func play(cue: String, max_seconds: float = 0.0) -> AudioStreamPlayer:
	var inst := _inst()
	if inst == null:
		return null
	if cue == "notification":
		# UI-5: a notice's priority is heard. The bar hints it on the line
		# before it marks the notice seen; a hint older than 250 ms is a
		# silent fill's and is ignored.
		var priority := _notify_hint_priority
		var fresh := Time.get_ticks_msec() - _notify_hint_ms <= 250
		_notify_hint_priority = 0
		if fresh and priority >= 2:
			return inst._play_cue("notification_critical", max_seconds)
		if fresh and priority == 1:
			inst._play_cue("notification_high", 0.0)
	return inst._play_cue(cue, max_seconds)


static func hint_notification_priority(priority: int) -> void:
	_notify_hint_priority = priority
	_notify_hint_ms = Time.get_ticks_msec()


static func play_result(verb: String) -> void:
	"""UI-5: an order that SUCCEEDED, heard as it is carried out — the
	marching column, the spade, the drum, the bugle. An unknown verb is the
	musket-lock click of an order taken."""
	var inst := _inst()
	if inst == null:
		return
	var cue := str(RESULT_CUES.get(verb.to_lower().strip_edges(), "command_ack"))
	inst._play_cue(cue, 0.0)
	if cue == "coins_small":
		inst._play_cue("boots", 0.0)


static func hover() -> void:
	var inst := _inst()
	if inst != null and UiSettings.get_hover_sfx():
		inst._play_cue("hover", 0.0)


static func keystroke(soft: bool = false) -> void:
	"""UI-5: the quill's nib under a typed key (Settings → Typing sounds)."""
	var inst := _inst()
	if inst != null and UiSettings.get_typing_sfx():
		inst._play_nib(soft)


static func preview_bus(bus_name: String) -> void:
	"""A volume slider let go: a short sound on its own bus, at its new level."""
	var inst := _inst()
	if inst == null:
		return
	match bus_name:
		"Master":
			inst._play_cue("confirm", 0.0)
		"SFX":
			inst._play_cue("musket_shot", 0.0)
		"UI":
			inst._play_cue("click", 0.0)
		"Ambience":
			if inst._loop_players.is_empty():
				inst._play_cue("distant_drums", 0.0)
		_:
			pass


static func start_loop(tag: String) -> void:
	var inst := _inst()
	if inst != null:
		inst._start_loop(tag)


static func stop_cue(cue: String) -> void:
	"""Silence any live one-shot of `cue`, fading over 150 ms.

	UX23-R1 — "closing a panel should silence the sound it started". The
	Aug-23 caps bounded how long a cue can outlive its panel (6 s worst case);
	this ends it at the moment of the close.

	The rule the wiring follows, which the routed row did not draw: **an
	arrival sound stops on close; a departure sound IS the close.** So the
	envoy's paper and the diorama's cannon stop, and
	`capture_choice_dialog`'s coins — played inside the Plunder handler, one
	line before `hide()`, as the sound of the decision — deliberately do not.
	`popup_base.close_popup` itself plays "back" ON close for the same reason.
	"""
	var inst := _inst()
	if inst != null:
		inst._stop_cue(cue)


static func stop_player(p) -> void:
	"""Silence ONE live one-shot — the player `play()` handed back.

	Review round: `stop_cue(name)` is a global kill by cue name, so a closing
	panel silenced every live play of that name including other surfaces'.
	Measured shape: the tableau's close called `stop_cue("drum_sting")` and
	would have cut the strategic-interrupt popup's drum, still on screen.
	`_play_cue` has the handle in hand at the moment it registers it, so
	ownership can be real rather than nominal.

	The parameter is deliberately UNTYPED (Aug 28, 2026). Every one-shot
	frees itself when its sound ends (`finished` -> `queue_free` in
	`_play_cue`), so a claimed handle is routinely a freed object by the time
	its owner closes — and a `p: AudioStreamPlayer` annotation made GDScript
	throw "previously freed ... is not a subclass" AT THE CALL, before the
	`is_instance_valid` guard below could ever run. Crashed live in the
	diorama's `_on_close_pressed` after Napoleon attacked Mack."""
	var inst := _inst()
	if inst != null and is_instance_valid(p) and p is AudioStreamPlayer \
			and p.playing:
		inst._fade_out_now(p, 0.15)


static func stop_all_cues() -> void:
	"""Silence every live one-shot. The sibling `stop_all_loops` has always
	existed because the players live under this singleton and a scene change
	does not free them; one-shots have exactly the same property and had no
	equivalent, so `dialog_manager.hide_all()` on a world swap left a 5-second
	peal ringing into the freshly loaded campaign."""
	var inst := _inst()
	if inst == null:
		return
	for cue in inst._live_players.keys().duplicate():
		inst._stop_cue(cue)


static func stop_loop(tag: String) -> void:
	var inst := _inst()
	if inst != null:
		inst._stop_loop(tag)


static func start_scribble() -> void:
	start_loop("scribble")


static func stop_scribble() -> void:
	stop_loop("scribble")


static func set_war_mood(at_war: bool) -> void:
	var inst := _inst()
	if inst != null:
		inst._at_war = at_war
		inst._set_mood(inst._war_mood_now())
		inst._refresh_war_layer()


static func set_war_pressure(worst_score: int) -> void:
	"""UI-5: France's worst war score — at CRISIS_SCORE or under, the war's
	music turns to the crisis rotation (display only: the score is read)."""
	var inst := _inst()
	if inst != null:
		inst._worst_war_score = worst_score
		if inst._at_war:
			inst._set_mood(inst._war_mood_now())


static func announce_war(opponent: String, france_attacker: bool) -> void:
	"""UI-5's anthem rule, in ONE place: France the attacker hears La
	Marseillaise; France attacked hears the attacker's anthem, where a
	period-true recording exists — else La Marseillaise answers."""
	var inst := _inst()
	if inst == null:
		return
	if france_attacker or not inst._has_anthem(opponent):
		inst._play_music_once("marseillaise")
	else:
		inst._play_anthem(opponent)


static func play_anthem(nation: String) -> bool:
	"""A court's anthem on the overlay lane, about 20 s; a court with no
	period-true recording is the drum sting. True when an anthem played."""
	var inst := _inst()
	if inst == null:
		return false
	if inst._has_anthem(nation):
		inst._play_anthem(nation)
		return true
	inst._play_cue("drum_sting", 0.0)
	return false


static func set_menu_mood() -> void:
	"""Main Menu (position 6): the title theme on the rotation lane. Entering
	the campaign flips the mood via set_war_mood on the first live war data —
	and the theme doubles as the peace rotation's opener, so the hand-off is
	musically continuous."""
	var inst := _inst()
	if inst != null:
		inst._scene_stack.clear()
		inst._scene_requests.clear()
		inst._scene_pending.clear()
		inst._room_pick = ""
		inst._set_mood("menu")


static func request_scene_music(scene: String) -> void:
	"""UI-5: a screen that wants the court's music (the Cabinet, the Congress,
	the settlement table) asks on open; the scene plays only once the screen
	has stood SCENE_DELAY_S, so a glance does not flip the score."""
	var inst := _inst()
	if inst != null:
		inst._request_scene(scene)


static func release_scene_music(scene: String) -> void:
	var inst := _inst()
	if inst != null:
		inst._release_scene(scene)


static func stop_all_loops() -> void:
	"""Scene-change hygiene (game ↔ menu): the loop players live under the
	persistent AudioManager node, so a scene change does NOT free them — the
	departing scene's beds (wind, march, battle, sea, scribble) must be
	stopped explicitly."""
	var inst := _inst()
	if inst == null:
		return
	inst._ambience_on = false
	if inst._war_layer_timer != null:
		inst._war_layer_timer.stop()
	for tag in inst._loop_players.keys().duplicate():
		inst._stop_loop(tag)


static func play_music_once(name_key: String) -> void:
	var inst := _inst()
	if inst != null:
		inst._play_music_once(name_key)


static func duck_music(on: bool) -> void:
	var inst := _inst()
	if inst != null:
		inst._duck_music(on)


static func now_playing() -> Dictionary:
	"""{state: playing|resting|silent, file, title, composer, year, performer,
	situation} — what Settings → SOUND shows under "Now playing"."""
	var inst := _inst()
	if inst == null:
		return {"state": "silent"}
	return inst._now_playing()


static func skip_track() -> void:
	var inst := _inst()
	if inst != null:
		inst._skip_track()


static func music_room_tracks() -> Array:
	"""Every piece the game can play, grouped by situation, in the room's order:
	[{situation, situation_label, file, title, composer, year, performer}]."""
	var inst := _inst()
	if inst == null:
		return []
	return inst._music_room_tracks()


static func play_track(file: String) -> void:
	"""The Music Room's ▶: this piece now; the situation's music after it."""
	var inst := _inst()
	if inst != null:
		inst._play_room_pick(file)


static func resume_situation_music() -> void:
	var inst := _inst()
	if inst != null:
		inst._room_pick = ""
		inst._cancel_rest()
		inst._play_next_music_track(SCENE_CROSSFADE_S)


static func set_bus_volume(bus_name: String, linear: float, persist: bool = true) -> void:
	var inst := _inst()
	if inst != null:
		inst._set_bus_volume(bus_name, linear, persist)


static func get_bus_volume(bus_name: String) -> float:
	return UiSettings.get_audio_volume(bus_name)


static func _inst() -> AudioManager:
	if _instance != null and is_instance_valid(_instance):
		return _instance
	var ml := Engine.get_main_loop()
	if ml == null or not (ml is SceneTree):
		return null  # headless harness / bare SceneTree: audio is a no-op
	var root := (ml as SceneTree).root
	if root == null:
		return null
	_instance = AudioManager.new()
	_instance.name = "AudioManagerNode"
	root.add_child(_instance)
	return _instance


# ── instance lifecycle ──────────────────────────────────────────────────────

func _exit_tree() -> void:
	# S14E-X207: this node is the one that lives from the first scene to the
	# last (a child of the root, never freed by a scene change), so its exit IS
	# the game's exit - the window's close, `get_tree().quit()` and the
	# harness's quit all end here. The statics that hold Resources are let go,
	# so the engine's "2 resources still in use at exit" has nothing of ours.
	Utils.release_static_caches()
	PortraitLocket.release_static_caches()
	WarTablePiece.release_static_caches()


func _ready() -> void:
	_ensure_buses()
	_apply_saved_volumes()
	_music_a = _make_player("Music")
	_music_b = _make_player("Music")
	_music_overlay = _make_player("Music")
	_music_a.finished.connect(_on_music_finished)
	_music_b.finished.connect(_on_music_finished)
	_music_overlay.finished.connect(_on_overlay_finished)
	_rest_timer = Timer.new()
	_rest_timer.one_shot = true
	_rest_timer.timeout.connect(_on_rest_over)
	add_child(_rest_timer)
	_war_layer_timer = Timer.new()
	_war_layer_timer.one_shot = true
	_war_layer_timer.timeout.connect(_on_war_layer_tick)
	add_child(_war_layer_timer)
	# The global button hook — every current and future BaseButton.
	get_tree().node_added.connect(_on_node_added)
	_hook_existing(get_tree().root)


func _notification(what: int) -> void:
	# UI-5: the window in the background goes quieter (or mute, or plays on),
	# by Settings → SOUND → Background; back in front it comes back.
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		var mode := UiSettings.get_background_audio()
		var target := 0.0
		if mode == "quiet":
			target = BACKGROUND_QUIET_DB
		elif mode == "mute":
			target = -80.0
		_fade_focus_to(target)
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		_fade_focus_to(0.0)


# ── buses & volumes ─────────────────────────────────────────────────────────

func _ensure_buses() -> void:
	# The order matters: a bus sends only to a bus left of it, so Ceremony —
	# a sub-bus of SFX — is made last.
	for bus_name in ["Music", "SFX", "UI", "Ambience", "Ceremony"]:
		if AudioServer.get_bus_index(bus_name) == -1:
			var idx := AudioServer.bus_count
			AudioServer.add_bus(idx)
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, "SFX" if bus_name == "Ceremony" else "Master")
	# UI-5: the music dips under a ceremony (a compressor keyed from the
	# Ceremony bus), and the master never clips under a stack of cues.
	var music_idx := AudioServer.get_bus_index("Music")
	if music_idx != -1 and not _bus_has_effect(music_idx, "AudioEffectCompressor"):
		var duck := AudioEffectCompressor.new()
		duck.threshold = -22.0
		duck.ratio = 3.0
		duck.attack_us = 2000.0
		duck.release_ms = 650.0
		duck.sidechain = &"Ceremony"
		AudioServer.add_bus_effect(music_idx, duck)
	var master_idx := AudioServer.get_bus_index("Master")
	if master_idx != -1 and not _bus_has_effect(master_idx, "AudioEffectHardLimiter"):
		var limiter := AudioEffectHardLimiter.new()
		limiter.ceiling_db = -1.0
		limiter.release = 0.12
		AudioServer.add_bus_effect(master_idx, limiter)


func _bus_has_effect(bus_idx: int, effect_class: String) -> bool:
	for i in AudioServer.get_bus_effect_count(bus_idx):
		var effect := AudioServer.get_bus_effect(bus_idx, i)
		if effect != null and effect.get_class() == effect_class:
			return true
	return false


func _apply_saved_volumes() -> void:
	for bus_name in ["Master", "Music", "SFX", "UI", "Ambience"]:
		_set_bus_volume(bus_name, UiSettings.get_audio_volume(bus_name), false)


func _set_bus_volume(bus_name: String, linear: float, persist: bool) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx == -1:
		return
	linear = clampf(linear, 0.0, 1.0)
	var offset: float = (_focus_offset_db if bus_name == "Master" else 0.0) + (_duck_offset_db if bus_name == "Music" else 0.0)
	AudioServer.set_bus_volume_db(idx, linear_to_db(maxf(linear, 0.0001)) + offset)
	AudioServer.set_bus_mute(idx, linear <= 0.001)
	if persist:
		UiSettings.set_audio_volume(bus_name, linear)


func _fade_focus_to(target_db: float) -> void:
	var tw := create_tween()
	tw.tween_method(_apply_focus_offset, _focus_offset_db, target_db, 0.4)


func _apply_focus_offset(offset_db: float) -> void:
	_focus_offset_db = offset_db
	_set_bus_volume("Master", UiSettings.get_audio_volume("Master"), false)


# ── one-shot cues ───────────────────────────────────────────────────────────

func _play_cue(cue: String, max_seconds: float) -> AudioStreamPlayer:
	if not CUES.has(cue):
		push_warning("AudioManager: unknown cue '%s'" % cue)
		return null
	var spec: Dictionary = CUES[cue]
	var throttle := int(spec.get("throttle_ms", 0))
	if throttle > 0:
		var now := Time.get_ticks_msec()
		if _last_played_ms.has(cue) and now - int(_last_played_ms[cue]) < throttle:
			return null
	if _oneshot_count >= MAX_ONESHOT_PLAYERS:
		return null
	var files: Array = spec["files"]
	var i := int(_rr.get(cue, 0)) % files.size()
	var stream = _stream(String(files[i]))
	if stream == null:
		return null
	# UI-5: a cue already sounding as many times as it may is skipped — before
	# the throttle stamp, so a skipped play poisons no window.
	var max_voices := int(spec.get("max_voices", 0))
	if max_voices > 0 and (_live_players.get(cue, []) as Array).size() >= max_voices:
		return null
	# Aug 23, 2026: the throttle stamp and the round-robin advance used to run
	# ABOVE the budget check and the missing-file check, so a play that never
	# happened still poisoned the window — a cue rejected for lack of a player
	# slot, or one whose file is absent, went silent for its whole throttle
	# period afterwards. Both are recorded only once the play is certain.
	_rr[cue] = i + 1
	if throttle > 0:
		_last_played_ms[cue] = Time.get_ticks_msec()
	var p := _make_player(String(spec["bus"]))
	p.stream = stream
	p.volume_db = float(spec.get("db", 0.0)) + float(FILE_TRIM_DB.get(String(files[i]), 0.0))
	# UI-5: the hundredth click is not the first one again.
	var pitch := float(spec.get("pitch", 0.0))
	if pitch > 0.0:
		p.pitch_scale = 1.0 + randf_range(-pitch, pitch)
	var vary := float(spec.get("vary_db", 0.0))
	if vary > 0.0:
		p.volume_db += randf_range(-vary, vary)
	_oneshot_count += 1
	p.finished.connect(func():
		_oneshot_count -= 1
		_forget_live(cue, p)
		p.queue_free())
	# UX23-1 follow-up, Aug 23 2026 — measured, not guessed. The Aug-23 caps
	# assumed the gesture sits at the head of the file. An envelope probe
	# through an AudioEffectCapture bus (tools/audio_envelope_probe.gd) says
	# otherwise for two of the eleven:
	#
	#   letter_open  cap 1.4 s, sound ONSET 2.05 s  -> the cap ended before the
	#                paper ever rustled. The fix "made" the reported cue silent.
	#   cavalry      cap 3.2 s, onset 4.9 s         -> a gallop that approaches;
	#                the capped window is the empty road, 30 dB down.
	#
	# Raising the caps would bring back the length the player complained about.
	# `start_s` skips the dead head instead, so the cue stays short AND is the
	# sound it is named for. The other nine measured onsets are all inside
	# their caps and carry no offset.
	_live_players.get_or_add(cue, []).append(p)
	var start_at := float(spec.get("start_s", 0.0))
	# An offset past the end of the file plays nothing at all — the very bug
	# `start_s` exists to fix, re-created through the new mechanism. Clamp with
	# a second of headroom so a mis-typed offset degrades to a short cue rather
	# than to silence (review round; the length census cannot see this field).
	var stream_len := 0.0
	if stream != null:
		stream_len = stream.get_length()
	if stream_len > 0.0 and start_at >= stream_len - 0.25:
		start_at = max(0.0, stream_len - 1.0)
	if start_at > 0.0:
		p.play(start_at)
	else:
		p.play()
	# Aug 23, 2026 (user: "the paper noise goes on for a really long time"):
	# a cue's cap now lives in the registry beside its file, not only in the
	# optional `max_seconds` argument. `_fade_stop` was NOT unreachable —
	# three call sites passed a cap (the diorama's volley, the reveille, the
	# reward fanfare) — but a cap a caller has to remember is a cap the other
	# 68 call sites did not have, so `letter_open` ran its full 38.6 SECONDS
	# every time an envoy was opened and the 300 ms throttle let a second
	# copy start over the first. The registry is the single source now; those
	# three sites dropped their arguments and their values moved here. The
	# argument still wins where it is passed, so a one-off ceremony can ask
	# for longer than its cue's own default.
	var cap := max_seconds if max_seconds > 0.0 else float(spec.get("max_s", 0.0))
	if cap > 0.0:
		# UX23-R9: how long the fade runs is per-cue. A cap does not fall in
		# a quiet place just because we chose it — measured on the uncapped
		# renders, `reveille`'s 4.2 s cut sits at 51.6% of peak and the music
		# RISES to 85% underneath the 0.8 s fade, and `to_the_color`'s starts
		# in a note gap only to have the next phrase hit 90.5% inside it. A
		# search over 3-9 s found no better cap for either (the best still
		# fades from ~60%): these are continuous bugle calls with no trough,
		# so the cap was never the lever. A long decrescendo reads as an
		# ending where a 0.8 s pull reads as someone hitting stop.
		_fade_stop(p, cap, float(spec.get("fade_s", 0.8)))
	return p


func _forget_live(cue: String, p: AudioStreamPlayer) -> void:
	var arr: Array = _live_players.get(cue, [])
	arr.erase(p)
	if arr.is_empty():
		_live_players.erase(cue)


func _stop_cue(cue: String) -> void:
	for p in _live_players.get(cue, []).duplicate():
		if is_instance_valid(p) and p.playing:
			_fade_out_now(p, 0.15)


func _fade_out_now(p: AudioStreamPlayer, secs: float) -> void:
	"""Fade a live one-shot to silence and retire it.

	`p.finished.emit()` is load-bearing and must not be replaced by a bare
	`queue_free`: the `finished` lambda in `_play_cue` is the ONLY thing that
	decrements `_oneshot_count` and drops the live-registry entry. A stop path
	that skips it leaks the MAX_ONESHOT_PLAYERS budget permanently, and the
	game goes quiet after fourteen cues — a worse bug than the one being
	fixed."""
	# Idempotent, and it has to be. Two fade paths can now reach the same
	# player: the `max_s` timer and a `stop_cue` from a closing panel. Without
	# this latch both build a tween, both callbacks pass `is_instance_valid`,
	# and `finished` fires TWICE — so the `_play_cue` lambda runs twice and
	# `_oneshot_count` is decremented twice for one player, quietly corrupting
	# the budget that exists to stop the game running out of voices. (Before
	# `stop_cue` existed only one path could fade, so the callback never
	# needed a second guard; the review round for this slice is what found it.)
	if p.has_meta("_retiring"):
		return
	p.set_meta("_retiring", true)
	var tw := create_tween()
	tw.tween_property(p, "volume_db", -50.0, secs)
	tw.tween_callback(_retire_faded.bind(p.get_instance_id()))

# S14E-X202: the fade's end reads the player by INSTANCE ID. The callback was
# a lambda capturing `p`, and a one-shot that finishes on its own mid-fade
# frees itself (`finished` -> `queue_free` in `_play_cue`) — the engine then
# refused the call with "Lambda capture at index 0 was freed" before the body's
# own `is_instance_valid` could run (18 plain ERROR lines in one replay, one
# per battle cue shorter than its cap). An id is a number: nothing to be freed.
func _retire_faded(player_id: int) -> void:
	var p = instance_from_id(player_id)
	if is_instance_valid(p) and p.playing:
		p.stop()
		p.finished.emit()


func _fade_stop(p: AudioStreamPlayer, after_s: float, fade_s: float = 0.8) -> void:
	var t := get_tree().create_timer(after_s)
	t.timeout.connect(_fade_stop_due.bind(p.get_instance_id(), fade_s))


func _fade_stop_due(player_id: int, fade_s: float) -> void:
	"""S14E-X202: the cap's timer, by instance id (see `_retire_faded`)."""
	var p = instance_from_id(player_id)
	if is_instance_valid(p) and p.playing:
		_fade_out_now(p, fade_s)


# ── the quill's nib (UI-5: typing ticks) ────────────────────────────────────

func _play_nib(soft: bool) -> void:
	"""A slice of a quill take: 60–100 ms from a random place in the file, a
	fast fade, a pitch a breath either way. Its own player, freed when done —
	inside the manager, the one owner of audio players."""
	var now := Time.get_ticks_msec()
	if now - _nib_last_ms < NIB_THROTTLE_MS or _oneshot_count >= MAX_ONESHOT_PLAYERS:
		return
	var stream = null
	var nib_file := ""
	for rel in NIB_FILES:
		if ResourceLoader.exists(AUDIO_ROOT + String(rel)):
			stream = _stream(String(rel))
			nib_file = String(rel)
			break
	if stream == null:
		return
	_nib_last_ms = now
	var length: float = stream.get_length()
	var slice := randf_range(0.06, 0.10)
	var at := randf_range(0.0, maxf(0.0, length - slice - 0.05))
	var p := _make_player("UI")
	p.stream = stream
	p.volume_db = NIB_DB + float(FILE_TRIM_DB.get(nib_file, 0.0)) - (6.0 if soft else 0.0) + randf_range(-1.5, 1.5)
	p.pitch_scale = 1.0 + randf_range(-0.07, 0.07)
	_oneshot_count += 1
	_live_players.get_or_add("_nib", []).append(p)
	p.finished.connect(_on_nib_finished.bind(p.get_instance_id()))
	p.play(at)
	_fade_stop(p, slice, 0.03)


func _on_nib_finished(player_id: int) -> void:
	var p = instance_from_id(player_id)
	_oneshot_count = maxi(0, _oneshot_count - 1)
	if is_instance_valid(p):
		_forget_live("_nib", p)
		p.queue_free()


# ── named ambient loops ─────────────────────────────────────────────────────

func _start_loop(tag: String) -> void:
	if _loop_players.has(tag) or not LOOPS.has(tag):
		return
	var spec: Dictionary = LOOPS[tag]
	var stream = _stream(String(spec["file"]), true)
	if stream == null:
		return
	var p := _make_player(String(spec["bus"]))
	p.stream = stream
	p.volume_db = float(spec.get("db", -16.0)) + float(FILE_TRIM_DB.get(String(spec["file"]), 0.0))
	_loop_players[tag] = p
	p.play()


func _stop_loop(tag: String) -> void:
	if not _loop_players.has(tag):
		return
	var p: AudioStreamPlayer = _loop_players[tag]
	_loop_players.erase(tag)
	if is_instance_valid(p):
		var tw := create_tween()
		tw.tween_property(p, "volume_db", -50.0, 0.35)
		tw.tween_callback(p.queue_free)


# ── the ambience (UI-5: the Emperor's study) ────────────────────────────────

func _start_ambience() -> void:
	"""The room under the map: the wind at the window, a low fire, the clock;
	the season's layer; distant drums while at war. Idempotent."""
	_ambience_on = true
	for tag in ["wind", "fire", "clock"]:
		_start_loop_if_present(tag)
	_apply_season_layer()
	_refresh_war_layer()


func _stop_ambience() -> void:
	_ambience_on = false
	if _war_layer_timer != null:
		_war_layer_timer.stop()
	for tag in ["wind", "fire", "clock", "birds", "rain", "winter_wind"]:
		_stop_loop(tag)


func _start_loop_if_present(tag: String) -> void:
	"""A bed whose file is absent is skipped quietly — the study plays the
	layers it has."""
	if not LOOPS.has(tag):
		return
	if ResourceLoader.exists(AUDIO_ROOT + String(LOOPS[tag]["file"])):
		_start_loop(tag)


func _set_season_from_label(label: String) -> void:
	var season := ""
	for word in label.to_lower().split(" ", false):
		if SEASON_OF_MONTH.has(word):
			season = String(SEASON_OF_MONTH[word])
			break
	if season == "" or season == _season:
		return
	_season = season
	if _ambience_on:
		_apply_season_layer()


func _apply_season_layer() -> void:
	var want := String(SEASON_LAYER.get(_season, ""))
	for tag in ["birds", "rain", "winter_wind"]:
		if tag != want:
			_stop_loop(tag)
	if want != "" and _ambience_on:
		_start_loop_if_present(want)


func _refresh_war_layer() -> void:
	if _war_layer_timer == null:
		return
	if _ambience_on and _at_war:
		if _war_layer_timer.is_stopped():
			_war_layer_timer.start(randf_range(WAR_LAYER_GAP_S[0], WAR_LAYER_GAP_S[1]))
	else:
		_war_layer_timer.stop()


func _on_war_layer_tick() -> void:
	if not (_ambience_on and _at_war):
		return
	if _duck_depth == 0:
		_play_cue("distant_drums" if randf() < 0.6 else "cannon_distant", 0.0)
	_war_layer_timer.start(randf_range(WAR_LAYER_GAP_S[0], WAR_LAYER_GAP_S[1]))


# ── music ───────────────────────────────────────────────────────────────────

func _war_mood_now() -> String:
	if not _at_war:
		return "peace"
	return "crisis" if _worst_war_score <= CRISIS_SCORE else "war"


func _rotation_key() -> String:
	if not _scene_stack.is_empty():
		return String(_scene_stack[-1])
	return _music_mood


func _rotation_files(key: String) -> Array:
	"""The rotation's files that are on disk — a missing file never stops the
	music."""
	var out: Array = []
	for rel in MUSIC.get(key, []):
		if ResourceLoader.exists(AUDIO_ROOT + String(rel)):
			out.append(rel)
	return out


func _set_mood(mood: String) -> void:
	if mood == _music_mood or not MUSIC.has(mood):
		return
	_music_mood = mood
	if not _scene_stack.is_empty() or _room_pick != "":
		return  # a scene or a chosen piece holds the stage; the mood waits under it
	_music_queue = _rotation_files(mood)
	_music_queue.shuffle()
	_music_rotation_key = mood
	# Null-safe: a static call can land before _ready has built the players
	# (the lazy install races scene setup — the call sites defer, this guards).
	if _music_overlay != null and _music_overlay.playing:
		return  # the overlay finishing will pull from the new mood's queue
	_cancel_rest()
	if _music_a != null:
		_play_next_music_track()


func _request_scene(scene: String) -> void:
	if not MUSIC.has(scene):
		return
	_scene_requests[scene] = int(_scene_requests.get(scene, 0)) + 1
	if _scene_stack.has(scene) or _scene_pending.has(scene):
		return
	_scene_token += 1
	_scene_pending[scene] = _scene_token
	var t := get_tree().create_timer(SCENE_DELAY_S)
	t.timeout.connect(_scene_delay_due.bind(scene, _scene_token))


func _scene_delay_due(scene: String, token: int) -> void:
	if int(_scene_pending.get(scene, -1)) != token:
		return
	_scene_pending.erase(scene)
	if int(_scene_requests.get(scene, 0)) <= 0 or _scene_stack.has(scene):
		return
	_scene_stack.append(scene)
	if _room_pick != "" or (_music_overlay != null and _music_overlay.playing):
		return
	_music_queue = _rotation_files(scene)
	_music_queue.shuffle()
	_music_rotation_key = scene
	_cancel_rest()
	_play_next_music_track(SCENE_CROSSFADE_S)


func _release_scene(scene: String) -> void:
	var left := int(_scene_requests.get(scene, 0)) - 1
	if left > 0:
		_scene_requests[scene] = left
		return
	_scene_requests.erase(scene)
	_scene_pending.erase(scene)
	if not _scene_stack.has(scene):
		return
	var was_top := String(_scene_stack[-1]) == scene
	_scene_stack.erase(scene)
	if was_top and _room_pick == "" and not (_music_overlay != null and _music_overlay.playing):
		_music_queue = _rotation_files(_rotation_key())
		_music_queue.shuffle()
		_music_rotation_key = _rotation_key()
		_cancel_rest()
		_play_next_music_track(SCENE_CROSSFADE_S)


func _has_anthem(nation: String) -> bool:
	return ANTHEMS.has(nation) and ResourceLoader.exists(AUDIO_ROOT + String(ANTHEMS[nation]))


func _play_anthem(nation: String) -> void:
	if not _has_anthem(nation):
		return
	_play_overlay("anthem:" + nation, String(ANTHEMS[nation]), ANTHEM_CAP_S)


func _play_music_once(name_key: String) -> void:
	# The one-shot lane (the anthem; triumph/lament when a campaign ends).
	# The rotation fades under it and resumes after.
	if not MUSIC_ONESHOTS.has(name_key):
		return
	var file := String(MUSIC_ONESHOTS[name_key])
	_play_overlay(name_key, file, 0.0)


func _play_overlay(key: String, file: String, cap_s: float) -> void:
	# UI-5: a second announcement while one sounds does not restart it — only
	# the campaign's end (triumph / lament) takes the lane from another.
	if _music_overlay == null:
		return
	if _music_overlay.playing and not (key == "triumph" or key == "lament"):
		return
	var stream = _stream(file)
	if stream == null:
		return
	_cancel_rest()
	if _music_fade != null and _music_fade.is_valid():
		_music_fade.kill()
	var fade := create_tween()
	_music_fade = fade
	fade.set_parallel(true)
	for p in [_music_a, _music_b]:
		if p.playing:
			fade.tween_property(p, "volume_db", -50.0, 1.0)
	fade.chain().tween_callback(_stop_rotation_under_overlay)
	_overlay_token += 1
	_overlay_key = key
	_music_overlay.stream = stream
	_music_overlay.set_meta("music_file", file)
	_music_overlay.volume_db = _music_level(file)
	_music_overlay.play()
	if cap_s > 0.0:
		var t := get_tree().create_timer(cap_s)
		t.timeout.connect(_overlay_cap_due.bind(_overlay_token))


func _overlay_cap_due(token: int) -> void:
	if token != _overlay_token or not _music_overlay.playing:
		return
	var tw := create_tween()
	tw.tween_property(_music_overlay, "volume_db", -50.0, ANTHEM_FADE_S)
	tw.tween_callback(_end_overlay.bind(token))


func _end_overlay(token: int) -> void:
	if token != _overlay_token:
		return
	_music_overlay.stop()
	_on_overlay_finished()


func _on_overlay_finished() -> void:
	_overlay_key = ""
	_play_next_music_track()


func _active_music_player() -> AudioStreamPlayer:
	return _music_a if _music_active_is_a else _music_b


func _play_next_music_track(fade_s: float = CROSSFADE_S) -> void:
	var stream = null
	var file := ""
	if _room_pick != "":
		file = _room_pick
		stream = _stream(file)
	if stream == null:
		var key := _rotation_key()
		if key == "":
			return
		if _music_queue.is_empty() or _music_rotation_key != key:
			_music_queue = _rotation_files(key)
			_music_queue.shuffle()
			_music_rotation_key = key
		if _music_queue.is_empty():
			return
		# Never the same piece twice in a row across a refill.
		if _music_queue.size() > 1 and String(_music_queue[0]) == _current_track:
			_music_queue.append(_music_queue.pop_front())
		file = String(_music_queue.pop_front())
		stream = _stream(file)
	if stream == null:
		return
	_resting = false
	if _music_fade != null and _music_fade.is_valid():
		_music_fade.kill()   # a switch inside the last crossfade: its stop() must not land
	var from := _active_music_player()
	_music_active_is_a = not _music_active_is_a
	var to := _active_music_player()
	_current_track = file
	to.stream = stream
	to.set_meta("music_file", file)
	to.volume_db = -50.0
	to.play()
	var tw := create_tween()
	_music_fade = tw
	tw.set_parallel(true)
	tw.tween_property(to, "volume_db", _music_level(file), fade_s)
	if from.playing:
		tw.tween_property(from, "volume_db", -50.0, fade_s)
		tw.chain().tween_callback(_stop_if_inactive.bind(from.get_instance_id()))


func _stop_rotation_under_overlay() -> void:
	"""The rotation's players stop once faded under an anthem — unless the
	anthem was skipped first and the rotation already came back."""
	if _overlay_key == "":
		return
	_music_a.stop()
	_music_b.stop()


func _stop_if_inactive(player_id: int) -> void:
	"""A crossfade's outgoing player stops at the fade's end — unless a later
	switch made it the active one again."""
	var p = instance_from_id(player_id)
	if is_instance_valid(p) and p != _active_music_player():
		p.stop()


func _on_music_finished() -> void:
	if _music_overlay.playing:
		return
	# A finished track only advances the program if it was the active one (the
	# crossfade's outgoing player also emits `finished` when it is stopped).
	if _active_music_player().playing:
		return
	if _room_pick != "":
		_room_pick = ""
	var key := _rotation_key()
	if UiSettings.get_music_rests() and REST_RANGES.has(key) and _scene_stack.is_empty():
		var span: Array = REST_RANGES[key]
		_resting = true
		_rest_timer.start(randf_range(float(span[0]), float(span[1])))
		return
	_play_next_music_track()


func _on_rest_over() -> void:
	if not _resting:
		return
	_resting = false
	_play_next_music_track()


func _cancel_rest() -> void:
	_resting = false
	if _rest_timer != null:
		_rest_timer.stop()


func _skip_track() -> void:
	_cancel_rest()
	_room_pick = ""
	if _music_overlay != null and _music_overlay.playing:
		_overlay_token += 1
		_music_overlay.stop()
		_overlay_key = ""
	_play_next_music_track(1.5)


func _play_room_pick(file: String) -> void:
	if not ResourceLoader.exists(AUDIO_ROOT + file):
		return
	_room_pick = file
	_cancel_rest()
	if _music_overlay != null and _music_overlay.playing:
		_overlay_token += 1
		_music_overlay.stop()
		_overlay_key = ""
	_play_next_music_track(1.5)


func _now_playing() -> Dictionary:
	var file := ""
	var situation := _rotation_key()
	if _music_overlay != null and _music_overlay.playing:
		file = str(_music_overlay.get_meta("music_file", ""))
		situation = "anthem" if _overlay_key.begins_with("anthem:") else "oneshot"
	elif _active_music_player() != null and _active_music_player().playing:
		file = _current_track
		if _room_pick != "":
			situation = "room"
	if file == "":
		return {"state": "resting" if _resting else "silent", "situation": situation}
	var meta: Dictionary = MUSIC_META.get(file, {})
	return {
		"state": "playing", "file": file, "situation": situation,
		"title": str(meta.get("title", file.get_file().get_basename())),
		"composer": str(meta.get("composer", "")),
		"year": int(meta.get("year", 0)),
		"performer": str(meta.get("performer", "")),
	}


func _music_room_tracks() -> Array:
	var out: Array = []
	var seen := {}
	for pair in MUSIC_ROOM_SITUATIONS:
		var situation := String(pair[0])
		var files: Array = []
		if MUSIC.has(situation):
			files = MUSIC[situation]
		elif situation == "oneshot":
			files = MUSIC_ONESHOTS.values()
		elif situation == "anthem":
			for f in ANTHEMS.values():
				if not files.has(f):
					files.append(f)
		for rel in files:
			var file := String(rel)
			if seen.has(file) or not ResourceLoader.exists(AUDIO_ROOT + file):
				continue
			seen[file] = true
			var meta: Dictionary = MUSIC_META.get(file, {})
			out.append({
				"situation": situation, "situation_label": String(pair[1]), "file": file,
				"title": str(meta.get("title", file.get_file().get_basename())),
				"composer": str(meta.get("composer", "")),
				"year": int(meta.get("year", 0)),
				"performer": str(meta.get("performer", "")),
			})
	return out


func _music_level(file: String) -> float:
	"""A piece's playing level: the base trim and its measured loudness trim
	(UI-5). The diorama's duck rides the Music bus (`_duck_offset_db`)."""
	return MUSIC_DB + float(MUSIC_TRIM_DB.get(file, 0.0))


# The diorama (and any full-stage moment) ducks the music under it.
func _duck_music(on: bool) -> void:
	_duck_depth = maxi(0, _duck_depth + (1 if on else -1))
	var target := DUCK_DB if _duck_depth > 0 else 0.0
	var tw := create_tween()
	tw.tween_method(_apply_duck_offset, _duck_offset_db, target, 0.5)


func _apply_duck_offset(offset_db: float) -> void:
	_duck_offset_db = offset_db
	_set_bus_volume("Music", UiSettings.get_audio_volume("Music"), false)


# ── the global button hook ──────────────────────────────────────────────────

func _on_node_added(node: Node) -> void:
	_hook_button(node)


func _hook_existing(node: Node) -> void:
	_hook_button(node)
	for child in node.get_children():
		_hook_existing(child)


func _hook_button(node: Node) -> void:
	if node is BaseButton and not node.has_meta("_audio_hooked"):
		node.set_meta("_audio_hooked", true)
		node.pressed.connect(_on_any_button_pressed.bind(node))
		# UI-5: the hover tick, and a dropdown's chosen item.
		node.mouse_entered.connect(_on_any_button_hovered.bind(node))
		if node is OptionButton:
			(node as OptionButton).item_selected.connect(_on_option_item_selected.bind(node))
	elif node is RichTextLabel and not node.has_meta("_audio_hooked"):
		# UI-5: a link in a page is a control too.
		node.set_meta("_audio_hooked", true)
		(node as RichTextLabel).meta_clicked.connect(_on_any_meta_clicked.bind(node))


func _on_any_button_pressed(btn: Node) -> void:
	if not is_instance_valid(btn) or btn.has_meta("no_click_sfx"):
		return
	if btn is CheckButton or btn is CheckBox:
		_play_cue("toggle", 0.0)
	else:
		_play_cue("click", 0.0)


func _on_any_button_hovered(btn: Node) -> void:
	if not is_instance_valid(btn) or btn.has_meta("no_hover_sfx") or btn.has_meta("no_click_sfx_hover"):
		return
	if (btn as BaseButton).disabled or not (btn as Control).is_visible_in_tree():
		return
	if UiSettings.get_hover_sfx():
		_play_cue("hover", 0.0)


func _on_option_item_selected(_index: int, btn: Node) -> void:
	if is_instance_valid(btn) and not btn.has_meta("no_click_sfx"):
		_play_cue("select", 0.0)


func _on_any_meta_clicked(_meta, label: Node) -> void:
	if is_instance_valid(label) and not label.has_meta("no_click_sfx"):
		_play_cue("tick", 0.0)


# ── internals ───────────────────────────────────────────────────────────────

func _make_player(bus_name: String) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.bus = bus_name if AudioServer.get_bus_index(bus_name) != -1 else "Master"
	add_child(p)
	return p


func _stream(rel_path: String, want_loop: bool = false):
	var key := rel_path + ("#loop" if want_loop else "")
	if _streams.has(key):
		return _streams[key]
	var full := AUDIO_ROOT + rel_path
	if not ResourceLoader.exists(full):
		push_warning("AudioManager: missing audio file " + full)
		return null
	var stream = load(full)
	if want_loop and stream != null:
		# OGG and MP3 streams expose a runtime loop flag; WAV loops are set at
		# import time. Duplicate so the non-loop entry stays clean.
		stream = stream.duplicate()
		if "loop" in stream:
			stream.loop = true
	_streams[key] = stream
	return stream
