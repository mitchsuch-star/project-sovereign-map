# REPRO H1 -- "The briefing tells the truth" (slice 11: the morning-dispatch narration rows)

Agent `h1`, read-only, master `a1ed5c9d`, September 5, 2026. Every claim below is tied to a probe under `<scratchpad>\repro\h1\` (inventory at the end). Line numbers are quoted only as measured today; navigate by symbol.

## Summary

| Row | Verdict | Measured mechanism (one sentence) |
|---|---|---|
| FA-2 (P1) | NARROWED -- core REAL, two details wrong, fix wrong at one exit | `check_vassal_rebellion` queues `diplomatic_carved_vassal_dissolved` ("X has ceased to exist.", fog `always`) at :878, deletes the row at :882, and the true line `diplomatic_vassal_rebellion` (:1031, fog `player_vassal`) is dropped at RENDER time because `_is_dispatch_event_visible` reads live `world.vassals` -- queue ORDER is irrelevant (proven), the whitelist entry `diplomatic_vassal_rebellion` IS in `CAMPAIGN_LOG_TYPES` (the row says absent), and the graceful-independence exit `continue`s at :984 BEFORE the notification/queue/log site the fix names, so a `log_event` "beside the notification" never fires for Holland/KoI -- which on the shipped board is the exit those two satellites actually take. |
| FA-N19 (P2) | REPRODUCED | `_defect_vassal_free_and_hostile` queues the same "ceased to exist" line (:2238) beside the caller's `diplomatic_vassal_defected`; seeds 1/3/4/7/8 land `free_hostile`; Switzerland keeps Bern at WAR with France; the transfer outcome does NOT carry the false line. |
| FA-N74 (P2) | REPRODUCED (and wider) | Exactly two `world.log_event` calls in `vassal.py` (`transfer_vassal` :1677, `attempt_vassal_bribe` :2509); all three rebellion exits only `events.append`; `filter_campaign_log`, `_build_headline`'s window and the gazette never see a rebellion; the `diplomatic_vassal_rebellion` whitelist entry AND the gazette's `_COURT_TYPES` entries `vassal_rebellion`/`vassal_created` are producer-less. |
| FA-12 (P2) | REPRODUCED on BOTH worlds, verbatim | identity `enemy_on_our_soil:{region}` + `break` after the first qualifying intel region: T3 "3 turns now", T4 the base template re-fires for the next province, T6 "3 turns now" again, T7 "4 turns". |
| FA-N14 (P2) | REPRODUCED on BOTH worlds | `_build_headline`'s soil loop gates only `region.controller != player_nation`; France holding Swabia (1805) / Waterloo (legacy) with an enemy on it fires the class and by T3 says "enemy colours on French soil". |
| FA-53 (P3) | NARROWED -- core real and wider; captor half = NPC-15 (OPEN); `_DISPATCH_EVENT_TYPES` mechanism FALSE; digest citation = harness artefact | The page is 1 + `SUB_BEAT_SLOTS`=2 lines; a 5-province day shows 3, an 8-province day shows 3, and with a mauled marshal on the page only 2 (the diverse tail is bounded by `DIVERSE_TAIL_MAX_WEIGHT_DROP`=15 and `own_mauled` 85 is inside it); `region_captured` never rides `tactical_events`, so `_DISPATCH_EVENT_TYPES` is irrelevant; the digest's `DISPATCH:` line is `first_line(text, 200)` = the headline only. |
| FA-38 (P2) | REPRODUCED (title over-counts) | 28 classes in `HEADLINE_WEIGHTS`, none a vassal loss; `_build_headline` branches on no `vassal_*` type; Holland bribed + Switzerland eliminated + Berry lost in one tick -> "Berry has fallen" with EMPTY sub-beats; satellites alone -> headline None; our own satellite's death reads "Switzerland has been eliminated from the war." |
| FA-25 (P2) | NARROWED -- seam right, consequence overstated | A real `_execute_bombardment` logs `{type, attacker, attacker_nation, defender, defender_nation, attacker_location, defender_location, attacker_casualties, defender_casualties, terrain, terrain_modifier, fort_degraded, fort_old, fort_new, collateral, turn}` -- NO `location` key -- so the `own_mauled` arm (`etype == "battle"`) never fires and the gazette `_WAR_TYPES` lacks it; but the player DOES see it in the enemy-phase dialog (`_format_bombardment`) and the campaign log. |
| FA-32 (P2) | NARROWED -- title false | `dispatch["prisoners"]` is built and NO `.gd` reads it (measured key census of both renderers); the Generals card says "PRISONER of Austria since T1." and the client renders "held prisoner"; the Strategic Ledger lists him -- WRONGLY: an `idle` corps at `Vienna`, `strength 0`, `No active orders`, no captivity marker. |

## Per row

### FA-2 -- the rebellion is briefed as "X has ceased to exist" (P1)

Probe: `probe_1_fa2_n74_rebellion.py` (four arms, direct `advance_turn()` AND HTTP `end turn`, plus an order test and a producer census).

Evidence, ARM A (Switzerland loyalty 0 -> the WAR exit; Switzerland is the only satellite NOT cascade-joined into `war_1`):
```
PENDING DISPATCH QUEUE after advance_turn (type | fog_rule | vars | visible-at-render?)
 - diplomatic_vassal_rebellion_imminent | player_vassal | {'nation': 'Switzerland'} | False | Switzerland is on the verge of rebellion!
 - diplomatic_carved_vassal_dissolved   | always        | {'carved_name': 'Switzerland'} | True | Switzerland has ceased to exist.
 - diplomatic_vassal_rebellion          | player_vassal | {'nation': 'Switzerland'} | False | Switzerland has rebelled!
diplo state France-Switzerland: WAR | Switzerland regions: ['Bern']
HEADLINE: None (direct) / region_lost "Swabia has been taken by Austria" (HTTP, enemy phase ran)
DIPLOMATIC EVENTS: ... 'Switzerland has ceased to exist.' ... 'Spain enters the war via alliance with France.' 'Bavaria enters the war via alliance with France.' ... 'Relations with Switzerland have worsened significantly (-50 this turn).'
event_log rows added: [... 'defensive_cascade' x2, 'vassal_auto_join_war' x2 ...]   <- no vassal_rebellion* row
filter_campaign_log sees: no rebellion row; oneliners: 'Defensive cascade: Unknown joins war via France' x2, "Vassal Holland joined France's war.", "Vassal KingdomOfItaly joined France's war."
NEW notifications: ('vassal_rebellion', 'Switzerland REBELLED!', 'Switzerland has rebelled against France! War declared.'), ('vassal_rebellion_imminent', 'Switzerland Critical!', ...)
tactical_events vassal_rebellion*: [('vassal_rebellion', 'Switzerland has REBELLED! All vassal marshals have returned to Switzerland. War declared.')]
HTTP response tactical_events / events: the same vassal_rebellion row survives the fog filter
```
ORDER TEST:
```
visible while row exists: True
visible after the row is deleted (same queued event): False
```
Census: `diplomatic_carved_vassal_dissolved` has exactly two producers (`vassal.py:878` rebellion, `vassal.py:2238` bribe-free); `diplomatic_vassal_rebellion` has exactly one (`vassal.py:1031`).

ARM D (Holland loyalty 0 -- Holland is in `war_1` on France's side, like KingdomOfItaly):
```
tactical_events: [('vassal_rebellion_independent', 'Holland breaks free of France and stands alone - an independent power, though no war is declared.')]
DIPLOMATIC EVENTS about Holland: 'Holland has ceased to exist.' ONLY  (no rebellion line queued at all, no -50 relation line)
NEW notifications: [('vassal_rebellion_imminent', 'Holland Critical!', ...)]   <- NO 'REBELLED' notification
state F-Holland: PEACE | Holland regions: ['Gelderland', 'Brabant', 'Amsterdam', 'Friesland']
```
ARM C (forced ARMISTICE state):
```
tactical_events: [('vassal_rebellion_armistice', 'Switzerland breaks free but the armistice holds - no war declared.'), ('vassal_rebellion', 'Switzerland has REBELLED! ... War declared.')]
NEW notifications: ('vassal_rebellion', 'Switzerland REBELLED!', 'Switzerland has rebelled against France! War declared.')   <- state stays ARMISTICE
```
ARM B (KingdomOfItaly loyalty 0): NO rebellion -- `process_vassal_loyalty` runs before `check_vassal_rebellion` inside `process_diplomacy_turn` and lifted it `0 -> 2 ("the garrison's presence, a common enemy")` (Massena at Milan). The row's `loyalty = 0` recipe does not fire for KoI on the real turn path; it fires for Holland and Switzerland.

Verdict: NARROWED. The core is real and reproduces on the shipped board through both `advance_turn()` and `POST /command end turn`: the dispatch's DIPLOMATIC EVENTS rail (rendered by BOTH `main.gd::_display_morning_dispatch` and `dispatch_view.gd` -- both read `diplomatic_events`) says "Switzerland has ceased to exist." while Switzerland stands at Bern at WAR, and the campaign log has no rebellion row. The committed fixture `tests/fixtures/playtest_saves/fixture_t20_ambient.json:13311` carries the same false line in its `last_morning_dispatch`, so the ambient board hits it.

The two wrong details:
1. "deletes the vassal row BEFORE queueing" frames it as an ordering bug. It is not: `_is_dispatch_event_visible` (dispatch.py, `player_vassal` arm) reads `world.vassals` when the dispatch is BUILT, after `advance_turn`, so the line is dropped whichever side of the `del` the queue sits on (order test above). Any fix that only reorders the two statements is a no-op.
2. "absent from CAMPAIGN_LOG_TYPES" -- `diplomatic_vassal_rebellion` IS in `CAMPAIGN_LOG_TYPES` (campaign_log.py :132) with a fog arm (:886) and a one-liner (:1916, "Vassal rebellion: Switzerland has broken free!"); it is inert because nothing ever writes it to `world.event_log` (that is FA-N74). What is absent is the executor-local `vassal_rebellion*` triple.

The player is NOT left uninformed on the WAR exit: the CRITICAL rail row "Switzerland REBELLED!" and the end-turn terminal line (the `vassal_rebellion` row rides `tactical_events` -> `events`, printed by `main.gd::_on_command_result` :2666-2671) both say it. What is false/missing is the DISPATCH (including the re-read screen) and the LOG. On the graceful-independence exit (Holland, KingdomOfItaly -- every satellite that cascade-joined France's war, which on the 1805 boot is the two big ones) there is NO rail row, NO rebellion dispatch line and NO -50 line: the ONLY dispatch trace is "Holland has ceased to exist." That exit is where the P1 bites hardest and where the filed fix does not reach.

Seam by symbol: `backend/game_logic/vassal.py::check_vassal_rebellion` (the `queue_dispatch_event(... "diplomatic_carved_vassal_dissolved", ..., "always")` at :878; the `player_vassal` queue at :1031; the graceful `continue` at :984) and `backend/game_logic/dispatch.py::_is_dispatch_event_visible` (`player_vassal` arm reads live `world.vassals`).

What the filed fix would break / miss:
- "queue the rebellion event with fog_rule 'always'": renders correctly on the shipped board (France is the only lord at boot: `lords on the 1805 boot: ['France']`), but under GR5 after a VS-5/VS-6 transfer a Britain-lorded satellite's rebellion would print "X has rebelled!" with no lord named. Decide the rule at queue time instead: `"always" if lord == world.player_nation else "partial_on_nation"` and carry `lord` in `template_vars` so the template can say against whom. The sibling `diplomatic_vassal_rebellion_imminent` queued in the same tick is dropped by the same render-time read (harmless -- superseded).
- "call world.log_event at vassal.py:1002 beside the notification": the graceful-independence branch `continue`s at :984, before the transfer-back, the -50, the notification and the queue; a log call sited beside the notification never fires for `vassal_rebellion_independent`. The log call must sit at each of the THREE `events.append` sites (:890, :974, :1023).
- "the 158->159+ log-type pins move consciously": the count is 160 today, pinned in NINE files, not five (list under "Existing pins").
- Nothing pins "ceased to exist" on the rebellion PATH (only the template itself, `test_pc3_pc9_composition.py::test_the_dissolution_line_reads_both_ways`, via `_format_dispatch_event_text`), so dropping the queue at :878 flips no test.

Minimal correct fix: in `check_vassal_rebellion`, delete the :878 `diplomatic_carved_vassal_dissolved` queue; queue ONE truthful line per exit with visibility decided at queue time (rebelled-and-at-war / broke-free-in-peace / broke-free-under-armistice); `world.log_event` at each of the three `events.append` sites (or one type with an `exit` key) and give it a `CAMPAIGN_LOG_TYPES` entry + one-liner + fog arm (replacing the inert `diplomatic_vassal_rebellion` entry); then fix the armistice-branch copy (see cross-row 2).

Existing pins that would flip or must be watched:
- `tests/test_campaign_log.py:138`, `tests/test_bph_a_term_ownership.py:303`, `tests/test_ca9_row3_a7_jealousy_note.py:456`, `tests/test_ca9_row3_phase_a.py:154`, `tests/test_ca9_row3_q2_council_command.py:433`, `tests/test_igr_a_honest_copy.py:197`, `tests/test_igr_b_campaign_log_readable.py:546`, `tests/test_igr_f_envoy_digest.py:824`, `tests/test_wo_slice4_the_capital_speaks.py:785` -- all `assert len(CAMPAIGN_LOG_TYPES) == 160`. Replacing the inert entry with three real types gives 162; adding one type with an `exit` key gives 161 (or 160 if the inert entry is retired at the same time).
- `tests/test_fa_slice8_the_instrument_2026_09_02.py::test_the_families_this_row_was_filed_for_are_graded_high` (:733-739) pins `_DIPLOMATIC_EVENT_PRIORITY["diplomatic_vassal_rebellion"] == "HIGH"` -- keep the dispatch key (or re-grade the replacement HIGH).
- `tests/test_session8d_dispatch_polish.py::test_vassal_rebellion_appears_in_dispatch` (:323-331) queues `diplomatic_vassal_rebellion` with `player_vassal` on a world whose vassal row still EXISTS and asserts "rebelled" renders; `::test_player_vassal_visible_for_own_vassal` / `::test_player_vassal_hidden_for_non_vassal` (:463-476) pin the render-time rule itself. None flips if the producer changes its fog rule; all flip if someone "fixes" `_is_dispatch_event_visible` instead of the producer.
- `tests/test_vassal_call_to_arms.py::test_refusal_dispatch_event_visible_under_player_vassal_rule` (:296-310) pins that `template_vars["nation"]` must be the VASSAL for the `player_vassal` rule -- the same trap in the other direction.

### FA-N19 -- the VS-6 defection says "ceased to exist" beside "THE DEFECTION" (P2)

Probe: `probe_2_n19_bribe.py`.
```
seed 1: outcome ['free_hostile']
  queued: [('diplomatic_carved_vassal_dissolved','always',True), ('diplomatic_vassal_defected','always',True)]
  rail_lines: ['Switzerland has ceased to exist.', "THE DEFECTION: Britain's gold turns Switzerland against France.", 'Relations with Switzerland have worsened significantly (-50 this turn).']
  headline: None | vassal_regions: ['Bern'] | state_F_v: WAR | in_vassals: False
  event_log_added: [... 'vassal_defected'] ; campaign_log_visible: [..., "THE DEFECTION: Britain's gold turns Switzerland against France - the freed satellite takes the field."]
  notifs: [('vassal_rebellion', 'Switzerland DEFECTS!')]
seeds 3, 4, 7, 8: identical; seeds 2, 5, 6: vassal_bribe_refused
TRANSFER arm (Britain 5000g): rail ["Switzerland passes from France's suzerainty to Britain's.", "THE DEFECTION: Britain's gold turns Switzerland against France."] -- no 'ceased to exist'
```
Verdict: REPRODUCED exactly as filed, scoped to the free outcome (the transfer outcome goes through `transfer_vassal`, which never queues the dissolved line). `random` is the module RNG (`vassal.py:16 import random`, `:2422 random.random()`), so `random.seed(1)` lands it.

Seam: `backend/game_logic/vassal.py::_defect_vassal_free_and_hostile` (the `queue_dispatch_event(... "diplomatic_carved_vassal_dissolved" ...)` at :2238, before `del world.vassals[...]` at :2242).

Filed fix (delete that one queue call) is correct and safe: `attempt_vassal_bribe` queues `diplomatic_vassal_defected` for every landed outcome (:2517-2522), and no test pins "ceased to exist" on this path (`grep ceased tests/` -> only the template test and the fixture JSON). After FA-2 and FA-N19 land, `diplomatic_carved_vassal_dissolved` has ZERO producers -- it becomes a dead template; either retire it or leave it for a real future dissolution (NA-6c's carve teardown does not use it today -- census above).

Pins: none flip. `tests/test_vassal_defection.py::test_dispatch_template_registered` (:283-291) pins only `diplomatic_vassal_defected`; `::test_campaign_log_one_liner` (:273-281) pins the log line.

### FA-N74 -- a rebellion is never written to `world.event_log` (P2)

Probe: `probe_1_fa2_n74_rebellion.py` (all four arms: `event_log rows added` never contains a `vassal_rebellion*` row; `filter_campaign_log` sees none), `probe_9_fixshape_checks.py`.
```
oneliner(vassal_rebellion)             -> 'Event: vassal_rebellion'             | in CAMPAIGN_LOG_TYPES? False | in gazette _COURT_TYPES? True
oneliner(vassal_rebellion_independent) -> 'Event: vassal_rebellion_independent' | False | False
oneliner(vassal_rebellion_armistice)   -> 'Event: vassal_rebellion_armistice'   | False | False
oneliner(diplomatic_vassal_rebellion)  -> 'Vassal rebellion: Switzerland has broken free!' | True | False
filter_campaign_log passes a raw vassal_rebellion row today? False
```
Census (grep, symbol-checked): `world.log_event` appears exactly twice in `vassal.py` -- `transfer_vassal` :1677 (`vassal_transferred`) and `attempt_vassal_bribe` :2509 (`vassal_defected`). `_build_headline`'s only source is `world.event_log` (`window = [e for e in world.event_log if e.get("turn", 0) >= world.current_turn - 1]`); `gazette._special_candidates`/the court rows read `filter_campaign_log` output.

Verdict: REPRODUCED, and wider: the gazette's `_COURT_TYPES` whitelists `vassal_rebellion` and `vassal_created`, and neither type has a producer anywhere in `backend/` (`grep '"type": "vassal_rebellion"'` hits only the local-events append at `vassal.py:1024`; `vassal_created` hits only a trust-reaction key). So the gazette's vassal entries are as inert as the campaign log's.

Seam: `backend/game_logic/vassal.py::check_vassal_rebellion` (the three `events.append` sites :890 / :974 / :1023).

Filed fix check: "replace the inert entry with the three real types and re-key the formatter arms" is right in substance; the one-liner MUST be re-keyed or the gazette (which now would see a logged `vassal_rebellion` through its live `_COURT_TYPES` entry) prints the raw fallback `Event: vassal_rebellion`. Note the fog arm at campaign_log.py:886 ("player vassal always shown") must become lord-aware once non-player lords exist (GR5) -- the new row should carry `lord`.

Pins: the nine `len(CAMPAIGN_LOG_TYPES) == 160` pins above; nothing else references the three types.

### FA-12 -- the soil counter resets when the leading province changes (P2)

Probe: `probe_3_fa12_n14_soil.py`.
```
LEGACY WorldState(): A = Paris, B = Belgium
  T1: enemy_on_our_soil | Wellington has crossed into Paris. Davout and Drouot stand in his path. | runs={'enemy_on_our_soil:Paris': 1}
  T3: 3 turns now with enemy colours on French soil...                                      | runs={'enemy_on_our_soil:Paris': 3}
  T4: Wellington has crossed into Belgium. Ney stands in his path.                          | runs={'enemy_on_our_soil:Belgium': 1}
  T6: 3 turns now with enemy colours on French soil...                                      | runs={'enemy_on_our_soil:Belgium': 3}
  T7: the enemy has stood on our ground 4 turns...
1805 boot(): A = Berry, B = Artois -- identical shape (Moore), T4 'Moore has crossed into Artois' re-fires as fresh news
```
Verdict: REPRODUCED verbatim on both worlds. Seam: `backend/game_logic/dispatch.py::_build_headline`, the soil loop (`_add("enemy_on_our_soil", identity=f"enemy_on_our_soil:{region_name}", ...)` + `break`) and `_select_headline`'s `runs` rebuilt from identities present this turn.

Filed fix (key the identity on the CLASS, keep `region`/`enemy` in `fields`) is sound: the loop `break`s after one candidate so there is never a second `enemy_on_our_soil` candidate for CA8-5's `(class, identity)` dedupe to collapse; the escalation ladder's `fmt["marshal"] = identity.split(":")[-1]` becomes the literal class name but no `enemy_on_our_soil` variant uses `{marshal}`. What it does NOT do on its own: stop the base template from re-firing at run <= `STANDING_LEAD_MAX` when the province changes -- with a class key the run continues (3, 4, ...) so the ladder keeps escalating; only a genuine gap (no enemy on any home province for a turn) restarts it, which is the intended semantics. No test pins the `enemy_on_our_soil:<region>` identity string (`grep "enemy_on_our_soil:" tests/` -> nothing). `tests/test_pc2_pc7_enemy_phase_and_headline.py` drives `_select_headline` with synthetic identities -- unaffected. Serialized saves carry old per-province `runs` keys in `headline_lead_memory` (e.g. the t20 fixture's `"own_mauled:Bernadotte": 4`) -- stale keys are harmless (they only seed a run for an identity that is present).

Pins that stay green and should be run after the fix: `tests/test_w6_dispatch_rewrite.py::test_enemy_on_our_soil_from_fresh_intel` (:123-136, asserts class + "Blucher" + "Belgium" in text), `tests/test_wo_slice12_copy_sweep.py::test_one_defender_stands_in_his_path` (:540-553), `tests/test_wo_slice4_the_capital_speaks.py::test_a_standing_soil_alarm_does_not_evict_a_fallen_province` (:589-600).

### FA-N14 -- "enemy colours on French soil" fires for a conquered province (P2)

Probe: `probe_3_fa12_n14_soil.py`.
```
1805: France holds Swabia (Bavarian soil, not in France's 28 home regions), Mack (Austria, at war) stands on it
  T1: enemy_on_our_soil | Mack has crossed into Swabia. No French corps stands in his path.
  T3: enemy_on_our_soil | 3 turns now with enemy colours on French soil. ...
  T4: enemy_on_our_soil | the enemy has stood on our ground 4 turns. ...
LEGACY: France holds Waterloo (not in the 8 home regions), Wellington on it -- identical
```
Verdict: REPRODUCED on both worlds. Boot dormancy confirmed: on the 1805 boot France's controlled set == her 28 home regions exactly (`non-home controlled: []`), so the class is armed by the first conquest. Seam: the same soil loop in `_build_headline` (`if region is None or region.controller != player_nation: continue`); `home_regions` is built at the top of the function and used by the sibling `home_captured` arm.

Filed fix (`or region_name not in home_regions: continue`): golden-rule N1 holds -- `home_regions` is 28 on the 1805 boot and 8 on the legacy world, and every existing `enemy_on_our_soil` pin uses Belgium, which IS in the test factories' home set (`WorldFactory.basic()` / `WorldFactory.with_marshals()` -> France home = Belgium, Bordeaux, Brittany, Lyon, Marseille, Milan, Normandy, Paris). What the gate loses: an enemy corps standing on a CONQUERED French province produces no candidate at all (the enemy walking over Swabia/Venetia is then unnarrated until it takes a home province) -- a copy fix that keeps the candidate but says "{region}" instead of "French soil" for non-home ground is the wider-but-honest alternative the row's own `(or, under the copy fix, ...)` test clause anticipates. Either way, the FA-12 identity change and this gate touch the same eight lines; build them together.

### FA-53 -- multi-province days drop provinces and never name the captor (P3)

Probe: `probe_4_fa53_multi_province.py`.
```
LEGACY 5 provinces, one captor:      page = Belgium + Lyon + Milan   | missing: Marseille, Brittany | captor named? False | turn_events: []
LEGACY 5 provinces + mauled marshal: page = Belgium + Lyon + [Ney was mauled at Belgium ...] | missing: Milan, Marseille, Brittany
1805 5 provinces:                    page = Berry + Artois + Rhineland | missing: Gascony, Guyenne | captor named? False
1805 8 provinces, two captors:       page = Berry + Artois + Rhineland | missing 5 | captor named? False
1805 5 provinces + mauled marshal:   page = Berry + Artois + [Ney mauled at Rhineland] | missing: Gascony, Guyenne
1805 2 provinces:                    both on the page
IF region_captured rode tactical_events: _build_turn_events -> []   ('region_captured' not in _DISPATCH_EVENT_TYPES)
templates: home_captured = 'Sire - {region} has fallen. Enemy colours fly over French homeland soil.' (no {captor}); region_lost and capital_lost DO carry {captor}
producers of region_captured: capture_executor.py:115/:143, combat_executor.py:8493/:8579, world_state.py:579/:4132/:4166/:4195 -- all world.log_event, none appends to tactical_events
```
Verdict: NARROWED, as the Sept-2 pass said, and I can now state the three parts:
1. The captor half is a DUPLICATE of NPC-15 (OPEN, P2, `docs/BUG_FIXES.md:3314`: "Paris gets Nivernais's sentence, and no captor is named ... `home_captured` renders ... with no `{captor}`"); WO-D6 fixed only the Paris half (`capital_lost` carries `{captor}`).
2. The mechanism "`region_captured` is not in `_DISPATCH_EVENT_TYPES`, so any province beyond the third vanishes" is FALSE: `_build_turn_events` consumes `tactical_events`, and enemy captures are logged to `world.event_log` (and shipped in the enemy-phase payload) -- they never enter `tactical_events`, so that whitelist cannot drop or keep them. Adding `region_captured` to `_DISPATCH_EVENT_TYPES` would change nothing (measured: `_build_turn_events -> []` even when handed the events, and it would stay `[]` on the real path because the list is never handed them). The real mechanism is `SUB_BEAT_SLOTS = 2` (1 + 2 lines per page) -- not the `(class, identity)` dedupe, which keys `home_captured:{region}` per province and collapses nothing.
3. The digest citation is a harness artefact: `tools/playtest_driver.py::Digest.dispatch` writes `head = first_line(text, 200)` -- the FIRST line of the dispatch text -- so "turn 31 lost EIGHT and the dispatch read 'Sire -- Savoy has fallen'" shows only the headline; the two sub-beats (two more provinces) are never in the digest.
The surviving core is real on the shipped world and WIDER than filed: with a mauled marshal (or any candidate within `DIVERSE_TAIL_MAX_WEIGHT_DROP`=15 of 99 -- `own_mauled` 85, `marshal_captured` 95, `own_broken` 90 ...) the reserved last slot takes the fresh class and only TWO of five provinces survive.

Seam: `backend/game_logic/dispatch.py::_build_headline` (candidate construction per `region_captured` event) and `::_select_headline` (`SUB_BEAT_SLOTS`, the diverse tail).

What the filed fix breaks: siting the collapse in `_select_headline` reds `tests/test_wo_slice4_the_capital_speaks.py::TestTheTailIsOnlyEverAReordering::test_no_illegal_divergence_over_two_thousand_candidate_lists` (:630-680, a differential that forbids `_select_headline` dropping a beat or shortening the page vs the old loop) and `::test_the_marshal_capture_is_still_inside_the_floor` (:602-610, `"Soult" in head["sub_beats"][1]` with `T_LOST = ["Paris", "Limousin", "Berry", "Normandy"]` -- a collapsed page may have one sub-beat, IndexError). Build the collapse in `_build_headline` (one `home_captured` candidate carrying the joined province list via `_join_place_names`, keeping `capital_lost` separate) so the selection differential stays untouched; then `::test_a_foreign_congress_does_not_evict_a_fallen_province` / `::test_a_standing_soil_alarm_does_not_evict_a_fallen_province` (:578-600, `all("has fallen" in b for b in head["sub_beats"])`) pass vacuously on an empty tail and must be re-read, and `tests/test_w6_dispatch_rewrite.py::test_home_region_captured_is_the_top_story` (:46-66, "Lyon has fallen" in text, class `home_captured`) still holds for the single-province case. `tests/test_creative_audit_ca8_2026_08_04.py::test_two_different_marshals_still_get_two_beats` (:263-273) and `::test_another_marshals_break_is_not_absorbed` (:859) are the pins that forbid a naive one-beat-per-class rule.

### FA-38 -- losing a satellite can never lead the briefing (P2)

Probes: `probe_5_fa38_vassal_loss.py`, `probe_8_fa38_patched_bribe_and_ledger.py`, `probe_2_n19_bribe.py` (weights census).
```
HEADLINE_WEIGHTS: 28 classes; vassal/satellite/defect-named classes: []
_build_headline etype arms: battle, coalition_formed/brewing, crisis_brewing, crisis_passed, war_declaration(s), evacuation_*, marshal_broken/retreat, marshal_captured, marshal_destroyed, nation_eliminated, region_captured, third_party_peace -- vassal_defected/vassal_transferred/vassal_rebellion: not mentioned
ARM 1 (Holland bribed FREE + Switzerland eliminated + Berry lost, one tick):
  HEADLINE: home_captured | Berry has fallen. Enemy colours fly over French homeland soil. | sub: []
  rail: 'Holland has ceased to exist.' / "THE DEFECTION: Britain's gold turns Holland against France." / 'Switzerland has been eliminated from the war.' / relation -50
ARM 2 (TRANSFER outcome): HEADLINE identical; rail: "Holland passes from France's suzerainty to Britain's." + "THE DEFECTION: Britain's gold turns Holland against France."
ARM 3 (satellites only, no province lost): HEADLINE: None
nation_eliminated template: '{nation} has been eliminated from the war.'   (one template for enemy and own satellite alike)
```
Note the row's own repro (`Holland loyalty=30`, unpatched RNG) misses on seeds 1-8 -- chance is `(40-30)/100 * courting_effectiveness_scale(100)=1.0` = 10% -- and a refused attempt latches the pair for `BRIBE_COOLDOWN`=5 turns; patch `backend.game_logic.vassal.random.random` to `0.0` (the row's "with random patched to land").

Verdict: REPRODUCED; the title over-counts (the archived tick lost two, not three) but the load-bearing claim holds four ways. The `nation_eliminated` arm in `_build_headline` is gated on `_we_fought_them` (war-instance sides), so our own satellite's elimination correctly produces no `enemy_eliminated` candidate -- and no other candidate either. Note also: `_eliminate_nation` deletes the vassal row (`Switzerland in vassals? False` afterwards), so a `vassal_lost` class fed from `nation_eliminated` must read "was our vassal" from the EVENT (stamp `lord` at `_eliminate_nation`) or from the pre-teardown state, not from `world.vassals`.

Seam: `backend/game_logic/dispatch.py::HEADLINE_WEIGHTS` + `::_build_headline` (a new arm reading `vassal_defected` / `vassal_transferred` (from_lord == player) / the FA-N74 rebellion row / `nation_eliminated`-with-lord); the template table `_DIPLOMATIC_EVENT_TEMPLATES["nation_eliminated"]`.

What the filed fix depends on: the `vassal_rebellion` producer arm does not exist until FA-N74 lands (the headline reads `world.event_log`); the defection and transfer arms are live today. A weight "between `region_lost` 75 and `own_broken` 90" sits inside the diverse tail's 15-point window below `home_captured` 99 (`tests/test_wo_slice4_the_capital_speaks.py::test_the_floor_is_named_and_admits_the_marshal_fate_band` (:612-628) enumerates what the floor must ADMIT and REJECT -- a new class in [84, 99] must be added to its admit list or the pin is silently incomplete, not red). `tests/test_pc2_pc7_enemy_phase_and_headline.py::test_event_classes_are_not_standing` (:119-124) -- keep the new class out of `STANDING_HEADLINE_CLASSES`. `tests/test_wo_slice4_the_capital_speaks.py::test_no_godot_script_switches_on_a_headline_class` (:789-800) -- no `.gd` may branch on the class string.

### FA-25 -- bombardment casualties never reach the dispatch or Le Moniteur (P2)

Probe: `probe_6_fa25_bombardment.py`.
```
LEGACY synth (row recipe): Ney loses 28800 of 72000 -> headline: None | 'bombard' in dispatch payload? False | campaign log: 'Wellington (Britain) bombarded Belgium - 28,800 casualties'
1805 synth: Ney loses 9600 of 24000 -> headline: None | campaign log: 'Moore (Britain) bombarded Rhineland - 9,600 casualties'
bombardment in CAMPAIGN_LOG_TYPES? True | in gazette _WAR_TYPES? False | in _DISPATCH_EVENT_TYPES? False
REAL PRODUCER (Mack made artillery at Swabia, Ney moved adjacent to Rhineland, CombatExecutor._combat._execute_bombardment):
  BOMBARDMENT EVENT KEYS: ['attacker','attacker_casualties','attacker_location','attacker_nation','collateral','defender','defender_casualties','defender_location','defender_nation','fort_degraded','fort_new','fort_old','terrain','terrain_modifier','turn','type']
  BOMBARDMENT EVENT: {'type':'bombardment','attacker':'Mack','attacker_nation':'Austria','defender':'Ney','defender_nation':'France','attacker_location':'Swabia','defender_location':'Rhineland','attacker_casualties':903,'defender_casualties':1332,'terrain':'plains','terrain_modifier':110,'fort_degraded':False,'fort_old':0,'fort_new':0,'turn':1}
  result events: ['bombardment'] ; headline after: None (1,332/24,000 = 5.5%, below the 25% floor anyway)
```
Verdict: NARROWED. The seam is exactly right (`_build_headline`'s `elif etype == "battle"` arm is the only `own_mauled` producer; the gazette's `_WAR_TYPES` lacks `bombardment`). The consequence is overstated: the player sees an enemy bombardment in the enemy-phase dialog (`enemy_phase_dialog.gd::_format_bombardment` :503-528 renders "Bombardment of {defender_location} / X fires from Y on Z / Z: N casualties") and in the campaign log; what is structurally blind is the morning headline/sub-beats and Le Moniteur. `_DISPATCH_EVENT_TYPES` is irrelevant here for the same reason as FA-53 -- an AI bombardment never rides `tactical_events`.

Seam: `backend/game_logic/dispatch.py::_build_headline` (the battle arm) and `backend/game_logic/gazette.py::_WAR_TYPES`.

What the filed fix must get right (the trap in "also accept etype == 'bombardment'"): the battle arm reads `e.get("location", "the field")` and the bombardment event has NO `location` key -- its field is `defender_location` -- so a verbatim reuse renders "Ney was mauled at the field". Read `defender_location` for the bombardment arm. `pre = m.strength + casualties` works (strength is already reduced when the event is logged). Summing two shots a turn into one `own_mauled:{name}` identity is consistent with CA8-5 (`tests/test_creative_audit_ca8_2026_08_04.py::test_three_battles_by_one_marshal_take_one_slot` :253). Adding `bombardment` to `_WAR_TYPES` is safe: the gazette captions war rows through `format_event_oneliner`, whose `bombardment` arm exists (campaign_log.py :1358). No test pins `_WAR_TYPES` membership (`grep _WAR_TYPES tests/` -> nothing).

Pins: `tests/test_w6_dispatch_rewrite.py::test_own_mauled_from_casualty_fraction` (:84-93) and `tests/test_wo_slice12_copy_sweep.py` (:330 / :340, the WO-16 500-man floor) stay green; a `"shelled"` phrasing must keep the `{proportion}` the WO-16 pin asserts.

### FA-32 -- the "Prisoners" line is built and never rendered (P2)

Probes: `probe_7_fa32_prisoner.py`, `probe_8_fa38_patched_bribe_and_ledger.py` (ledger half).
```
capture_marshal(Ney,'Austria'): event_log added ['marshal_captured'] ; new notifications: []
SAME TURN dispatch headline: 'Sire - Marshal Ney has been taken. Austria holds him prisoner.' | prisoners: [{'name':'Ney','captor':'Austria','captured_turn':1}] | Ney in marshals? False
T+2: headline None | prisoners: [same] | Ney in marshals? False | 'Ney' anywhere else in the payload? []
GENERALS CARD: {'captured': True, 'captured_by': 'Austria', 'status': 'captured', 'status_note': 'PRISONER of Austria since T1.', 'location': 'Vienna', 'strength': 0}  (HTTP /marshal_overview identical)
STRATEGIC LEDGER forces row: {'name':'Ney','location':'Vienna','strength':0,'morale':100,'status':'idle','strategic_order':'None', ...}
STRATEGIC LEDGER orders row: {'marshal':'Ney','location':'Vienna','order_type':'No active orders','has_order':False}
client grep 'prisoners' -> main.gd:1639 (a comment) only; key census of main.gd::_display_morning_dispatch (:3401-) and dispatch_view.gd reads turn/situation/marshals/intelligence/headline/turn_events/diplomatic_events/lapsed_offers/pending_envoys/peace_settlements/... and never 'prisoners'
client renders captivity: marshal_management.gd:556-558 ('held prisoner - his rewards await his release'); strategic_ledger.gd: no 'captured'/'prisoner' string at all
```
Verdict: NARROWED, and the Sept-2 reading is confirmed in both directions. The core is real: `dispatch["prisoners"]` has no consumer, so after the two-turn `marshal_captured` window (`window = turn >= current_turn - 1`) the dispatch drops him entirely. The title "vanishes from every daily surface" is false: the Generals card names his fate correctly, and the Strategic Ledger lists him -- but the ledger is the surface that LIES: `ledger._build_forces` shows the prisoner as an `idle` corps standing in `Vienna` at strength 0 with "No active orders", and `strategic_ledger.gd` has no captivity marker to render. No notification is created on capture (`new notifications: []`).

Seam: `godot-client/project-sovereign/scripts/main.gd::_display_morning_dispatch` + `dispatch_view.gd` (render `data.get("prisoners", [])`); `backend/game_logic/ledger.py::_build_forces` (stamp `captured`/`captured_by` so the FORCES tab can say so); `backend/models/world_state.py::capture_marshal` / `::release_captured_marshal` (the rail row the row proposes).

Filed fix check: the client render half is correct and pin-safe (`tests/test_w6_marshal_fates.py::test_absent_from_dispatch_roster_present_in_prisoners` :223-230 pins the backend key and stays green). It misses the ledger's lie, which is the persistent surface the player actually opens. The rail-notification half needs a dismiss on release and must not fire for a captured ENEMY marshal (`capture_marshal` runs for both sides -- GR5).

## Cross-row findings

1. On the shipped board, a loyalty-0 rebellion by Holland or KingdomOfItaly takes the GRACEFUL-INDEPENDENCE exit, not the WAR exit (`probe_1` ARM D: both cascade-joined `war_1` on France's side, so `ensure_war_instance_for_pair` hits the side conflict -> `set_diplomatic_state(... "PEACE", "vassal_rebellion_independent")` + `continue`). That exit skips the marshal transfer-back, the -10 sibling shock, the threat relief, the -50 relation, the CRITICAL notification and the dispatch queue -- so the player gets NO rail row and the only dispatch line is the false "Holland has ceased to exist." Only Switzerland (not in the war) reaches the WAR exit the rows describe.
2. The ARMISTICE exit lies twice (`probe_1` ARM C): it appends `vassal_rebellion_armistice` ("no war declared") AND falls through to the shared tail, which appends `vassal_rebellion` ("War declared.") and creates the CRITICAL notification "Switzerland has rebelled against France! War declared." while the state stays ARMISTICE. Pre-existing; any FA-2 fix that adds a per-exit log row must gate the tail's copy.
3. `process_vassal_loyalty` runs before `check_vassal_rebellion` inside `process_diplomacy_turn`, so a satellite with a French garrison (KoI, Massena at Milan) is lifted `0 -> 2` before the check: the row's `loyalty = 0` recipe never fires for it on the turn path (`probe_1` ARM B). A pin for the KoI arm must call `check_vassal_rebellion` directly or set loyalty low enough to survive the drift.
4. `defensive_cascade` campaign-log one-liner prints "Defensive cascade: Unknown joins war via France": the producer (`diplomacy.py:8841`) writes `defender`/`ally`/`against`, the formatter (`campaign_log.py:2173`) reads `nation`/`ally`. Pre-existing dead name; measured twice on every rebellion/defection.
5. `_DIPLOMATIC_EVENT_TEMPLATES["diplomatic_vassal_defected"]` is one template for both outcomes ("THE DEFECTION: {briber}'s gold turns {vassal} against {lord}."), so the TRANSFER outcome (Holland now Britain's vassal, at PEACE with France) also prints "turns Holland against France" beside "passes from France's suzerainty to Britain's." (`probe_8` ARM 2). The campaign-log one-liner does branch on `outcome`; the dispatch template does not.
6. The gazette's `_COURT_TYPES` carries `vassal_rebellion` and `vassal_created`, neither of which any producer logs (`probe_9`, grep census) -- the same inert-whitelist shape as `diplomatic_vassal_rebellion` in `CAMPAIGN_LOG_TYPES`. Once FA-N74 logs a real `vassal_rebellion`, the gazette prints `Event: vassal_rebellion` unless the one-liner is keyed.
7. `len(CAMPAIGN_LOG_TYPES)` is 160 today and is pinned in NINE files (the task brief said five): test_bph_a_term_ownership.py:303, test_ca9_row3_a7_jealousy_note.py:456, test_ca9_row3_phase_a.py:154, test_ca9_row3_q2_council_command.py:433, test_campaign_log.py:138, test_igr_a_honest_copy.py:197, test_igr_b_campaign_log_readable.py:546, test_igr_f_envoy_digest.py:824, test_wo_slice4_the_capital_speaks.py:785.
8. Filed line numbers are stale across the family (FA-2's ":855-856/:860/:1005-1007" are :878/:882/:1031-1032 today; the Sept-2 pass itself cited :1009 which is also stale); the symbols named in the rows all still exist.
9. The playtest digest's `DISPATCH:` line is the dispatch's FIRST line only (`Digest.dispatch` -> `first_line(text, 200)`); any audit claim of the form "the dispatch read X" taken from a digest describes the headline, never the sub-beats.
10. The Strategic Ledger's FORCES and ORDERS tabs present a prisoner as a live idle corps at the enemy capital (cross-row 8 of FA-32) -- not filed anywhere I could find (`grep -n "prisoner\|captured" backend/game_logic/ledger.py` -> 0 hits).

## Probe inventory

All under `C:\Users\User\AppData\Local\Temp\claude\C--Users-User-PycharmProjects-project-sovereign-map\4c14c8c5-5ff1-4de1-aa3d-2c19936812cc\scratchpad\repro\h1\`:

- `probe_1_fa2_n74_rebellion.py` -- FA-2 / FA-N74: the three rebellion exits on the shipped board (direct `advance_turn` + HTTP `end turn`), the pending-queue visibility read, the queue-order test, the producer census.
- `probe_2_n19_bribe.py` -- FA-N19 (seeds 1-8, free vs transfer outcome) + the FA-38 unpatched recipe + `HEADLINE_WEIGHTS` census.
- `probe_3_fa12_n14_soil.py` -- FA-12 on both worlds (the row's recipe), FA-N14 on both worlds (Swabia / Waterloo).
- `probe_4_fa53_multi_province.py` -- FA-53 on both worlds (5 / 8 provinces, one or two captors, with and without a mauled marshal), the `_DISPATCH_EVENT_TYPES` mechanism check, the `region_captured` producer census.
- `probe_5_fa38_vassal_loss.py` -- FA-38 first pass (unpatched RNG, elimination of an own satellite, `_build_headline` arm census).
- `probe_6_fa25_bombardment.py` -- FA-25 synth on both worlds + the REAL `_execute_bombardment` producer (exact logged keys).
- `probe_7_fa32_prisoner.py` -- FA-32: capture -> T+2 dispatch, Generals card, ledger walk, client grep.
- `probe_8_fa38_patched_bribe_and_ledger.py` -- FA-38 with the RNG patched (free / transfer / satellites-only arms) + the FA-32 ledger forces/orders rows.
- `probe_9_fixshape_checks.py` -- one-liner fallbacks for the three rebellion types, `filter_campaign_log` behaviour, gazette whitelists, the digest `first_line` artefact.
