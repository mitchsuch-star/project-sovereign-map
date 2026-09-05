# REPRO H2 - "the enemy phase reads the field" (FA-23, FA-N21, FA-N33, FA-N75)

Read-only reproduction at master `a1ed5c9d`, Sept 5 2026. Every claim below is
tied to a probe output under `<scratchpad>\repro\h2\`. Line numbers in the
rows were NOT used; every seam is named by symbol.

## Summary

- **FA-23 - REPRODUCED, NARROWED in three places.** The hold path of
  `combat_executor._resolve_garrison_combat` emits only a private
  `garrison_assault` result event (0 `event_log` rows) and
  `main._filter_enemy_phase_by_visibility` keys its region check on the
  ASSAULTER's province, so the ordinary P4.25 row (assaulter PARTIAL) is
  dropped - even though the assault itself has just lit the ASSAULTED
  province FULL through `WorldState.update_intel_from_battle`. Narrowings:
  (1) "invisible on every surface" over-claims - the hold writes a diplomacy
  `battle_records` row and a `battles_this_turn` row, the province takes
  war damage, and the player receives the generic fog line; (2) the
  UNFORTIFIED fall path is not invisible at all - it emits `conquest` with
  `captured_from`, survives fog at PARTIAL and renders "Region captured";
  only the fortified fall (`garrison_destroyed` + `occupation_started`)
  shares the client blindness, and that row SURVIVES the fog filter;
  (3) the geometry does not exist on the shipped boot - no enemy marshal
  stands adjacent to any French garrison, and Moore@London is refused at
  Normandy by the NV-4 host rule - it needs a player detachment or a
  mid-campaign position; with a detachment the P4.25 rung picks it itself.
- **FA-N21 - DUPLICATE of FA-23's render seam** (the same defect, one of
  its three seams). Its fix shape (structured `.gd` arms, never the server
  `message`) is correct and NECESSARY, but alone it is production-dead for
  the ordinary P4.25 case because the row never reaches the client; its
  test (1) ("adds 0 rows to `world.event_log`") is mutually exclusive with
  FA-23's fix shape (which logs a row) - the build must pick one.
- **FA-N33 - REPRODUCED at the dialog, NARROWED.** Not "in silence": the
  campaign log prints `Rhineland captured by Austria (secure)`, the
  dispatch leads with `home_captured` (weight 99) and the map flips; only
  the enemy-phase dialog prints "- Mack moves to Rhineland" with no
  capture line, while the player's own mirror march prints "Bohemia falls
  to France! (was Austria)". The row's "no choice suffix" clause is wrong
  for the AI: `_attempt_region_capture` returns `capture_choice`
  (auto-decided, and plunder is live since IGR-E) - the move producer
  simply never stamps it on the event.
- **FA-N75 - REPRODUCED exactly.** Shipped: 1 collapsed row, `coordination:
  []`, `weak_link: None`, one bar, one member line, zero Target buttons.
  Collapse disabled: 3 rows, 3 coordination pairs, weak link Austria (WE 55;
  Britain/Russia fogged to None), Targets Austria + Russia. Plus a BACKEND
  consumer the row never named: `diplomatic_advisory.
  _build_situation_recommendation` reads `coalition.weak_link` from
  `build_active_wars` (masked on the boot board by the design rung and the
  weakest-ally arm). Fix (a) hoist closes 2 of the 5 surfaces; only fix (b)
  `coalition_member_rows` + three `.gd` loop edits closes all 5.

## Per row

### FA-23 (P2, VERIFIED Sept 2) - the enemy garrison assault on French soil

**Ran:** `probe_1_garrison_assault.py` (Parts A-F), `probe_1b_fog_keying.py`.

**Boot geometry (Part A):**
```
Mack: Austria @ Swabia str 52000 personality literal
Swabia vis: partial | Rhineland vis: full
Rhineland controller: France garrison: 0 detachment: False fort: False capital: False
Marshals standing in Rhineland: ['Ney', 'Davout']
French garrisons at boot: [('Paris', 25000, ...), ('Normandy', 12000, ...), ('Flanders', 12000, ...)]
   Paris enemy marshals adjacent: []
   Normandy enemy marshals adjacent: [('Moore', 'Britain', 'London', 'unknown')]
   Flanders enemy marshals adjacent: []
```
The row's own synthetic row (Mack@Swabia vs a Rhineland garrison) behaves
as filed - `total_actions before 1 after 0 | Swabia vis partial`, and with
Swabia forced FULL `after 1`. But the Rhineland garrison is 0 at boot with
Ney and Davout standing there, so this exact board does not exist.

**The shipped board's only adjacent enemy (Part E) cannot assault:**
```
crossing_allowed(Britain, London->Normandy): False
assault 1: success=False events=[] ... event_log+1 ['naval_turnback'] | survives_fog=0
   message: Normandy is enemy country, Sire, and the French fleet still watches that water. An army does not march ashore onto a defended coast - that is a landing, not a m
```
The NV-V record's "grinding the depot down in two garrison assaults"
predates the NV-4 host rule. The P4.25-against-France case is a
mid-campaign shape, or the player's own detachment.

**The reachable geometry, picked by the rung itself (Part F):** a player
`garrison Rhineland` detachment (8,000, `garrison_detachment=True`), Ney and
Davout moved out, visibility recomputed:
```
Swabia vis: partial | Rhineland vis: partial | field army in Rhineland: False
P4.25 _find_garrison_attack(Mack) -> {'marshal': 'Mack', 'action': 'attack', 'target': 'Rhineland'}
executor events: ['garrison_assault'] | garrison now 4000 | event_log+ 0
   | battles_this_turn: [{'location': 'Rhineland', 'attacker': 'Mack', 'defender': 'Rhineland_garrison', 'result': 'defender_victory', 'turn': 1}]
survives fog: 0 | what the player gets instead: ['Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.']
Rhineland war_damage: 0.2 stability: 90
```
**The real hold path via `EnemyAI._execute_action` (Part B, 12k capital-style
garrison):** `events: [{"type": "garrison_assault", ..., "garrison_losses":
6000, "attacker_losses": 3000, "garrison_remaining": 6000}]`, `has
battle_report: False`, `event_log rows added: 0`, `battles_this_turn added:
1`, `battle_records added: 1`, `_build_visible_enemy_phase` -> `survives: 0`
plus the `fog_hidden_summary` line; with Swabia FULL -> `survives: 1` and the
`.gd` arm mirror renders `- Mack attacks Rhineland` and nothing under it.

**The sharper mechanism (probe_1b):**
```
pre-assault:  Swabia partial | Rhineland partial
post-assault: Swabia partial | Rhineland full          <- update_intel_from_battle lit it
post-recalc:  Swabia partial | Rhineland full          <- persistent (last_scouted_turn)
survives with marshal @ Swabia(partial), event.region=Rhineland(full): 0
same row, assaulter relocated onto the lit province -> 1
same row with the event stamped captured_from=France (PT-E5 arm) -> 1
```
`update_intel_from_battle`'s own docstring: "Battle grants FULL visibility on
the battle region." The intel model already tells the player where the
assault happened; the enemy-phase filter reads `ai_marshal.location`
(Swabia) and never `evt["region"]` (Rhineland).

**The fall paths (Part C):** unfortified (C1) -> `conquest` carrying
`captured_by: Austria, captured_from: France, capture_choice: secure`,
`event_log rows added: [('region_captured', 'Rhineland', 'France',
'Austria')]`, `survives fog (Swabia partial): 1`, client renders `Region
captured: Rhineland (secured)`. Fortified (C2) -> `garrison_destroyed` +
`occupation_started`, `event_log rows added: []`, `Rhineland controller now:
France`, and it SURVIVES the fog filter at Swabia PARTIAL because Mack has
marched onto the lit province - the client then renders `- Mack attacks
Rhineland` and nothing under it (no arm for either type).

**Log census (Part D):** `garrison_assault` / `garrison_destroyed` /
`occupation_started` / `conquest` are all absent from `CAMPAIGN_LOG_TYPES`
(160 entries) and from gazette `_WAR_TYPES`; `format_event_oneliner` on a
synthetic row returns `'Event: garrison_assault'`; `filter_campaign_log`
keeps `0` of it (unknown types are dropped at the `if event_type not in
CAMPAIGN_LOG_TYPES` gate). Nine test files pin `len(CAMPAIGN_LOG_TYPES) ==
160`, not five (list under Cross-row findings).

**Verdict: REPRODUCED, NARROWED** (three narrowings above).

**Seams by symbol:**
1. Fog: `backend/main.py::_filter_enemy_phase_by_visibility` - the
   `involves_player` arms (`battle`/`bombardment` events, `ai_action.target`
   is a player marshal, `captured_from == player`, NV-9 naval) have no
   garrison arm, and the region check keys on `ai_marshal.location`.
2. Render: `godot-client/project-sovereign/scripts/enemy_phase_dialog.gd::
   _format_action` - the events loop has arms for `battle` / `bombardment` /
   `conquest` only (the `.gd` census for `garrison_assault` /
   `garrison_destroyed` / `occupation_started` / `garrison_remaining` /
   `attacker_losses` / `garrison_losses` / `captured_by` / `captured_from`
   returns ZERO files).
3. Record (optional): `combat_executor._resolve_garrison_combat` calls
   `world.log_event` zero times; the pipeline is entered with
   `skip_log_battle_event` and `is_garrison` so step 2 never logs either.

**What the filed fix would break** (log `garrison_assault`/`garrison_destroyed`
to `event_log` stamped `nation` = the assaulted region's controller plus
"captured_from-style ownership keys"):
- `filter_campaign_log` drops the row silently until `CAMPAIGN_LOG_TYPES`
  gains the entries (measured 0 kept), and `format_event_oneliner` prints
  `Event: garrison_assault` until an arm exists - so half-landing the fix
  shape ships an invisible or debug-token row; landing it flips the NINE
  `len == 160` pins consciously (161-163).
- The 500-row cap (`WorldState.MAX_EVENT_LOG_SIZE = 500`): a detachment
  garrison fights to destruction with a >= 1-man floor (WO-3: "40 assaults"
  on one garrison), and P4.25 re-offers the same target every turn, so one
  siege writes one row per assaulter per turn - the IGR-B eviction trap.
  Do NOT log the hold; log the fall only, or nothing (the occupation's
  completion already logs `region_captured` via
  `_apply_occupation_capture_effects`, and C1 already logs it).
- Stamping `nation` = the DEFENDER's nation on a row whose `marshal` is the
  ATTACKER inverts the one-liner's `_name_tag(attacker, atk_nation)`
  convention (Mack would tag as French if the battle formatter is reused)
  and turns `_is_player_event` into "always show" for the wrong reason.
  Carry `attacker_nation` + `defender_nation` explicitly, as the `battle`
  event does.
- Stamping `captured_from` on a HOLD lies (nothing was captured); probe_1b
  shows it would pass the PT-E5 arm, but the gazette's `region_captured`
  branch and any future unification read that key as a capture.
- Readers by type would NOT start reacting (measured set: agendas
  `create_client`/`peace`; war_council `war_declaration`; instruments
  `british_subsidy`/`guarantee_abandoned`; strategic `cannon_fire`/`battle`/
  `glorious_charge`/`strategic_order`; diplomacy `create_client`/
  `forced_alliance`/`war_bargain`; marshal_voice `battle`/`region_captured`;
  dispatch `battle`), so mechanics are safe; only presentation moves.

**Minimal correct fix (three seams, in order):**
1. `main._filter_enemy_phase_by_visibility`: one arm beside PT-E5 - an
   event of type in `{garrison_assault, garrison_destroyed,
   occupation_started}` whose `region` is controlled by `player_nation`
   sets `involves_player` (leaks nothing: the garrison and the soil are ours,
   and the assault already lit the province FULL). Alternatively key the
   region check on `evt["region"]` for those types - the intel model already
   answers FULL. Prefer the own-soil arm: it is the stated reasoning of
   PT-E5/NV-9/CA8-15 and is independent of the intel side effect.
2. `enemy_phase_dialog.gd::_format_action`: two arms from structured fields
   - `garrison_assault` -> "The <region> garrison holds - <garrison_losses>
   lost, <garrison_remaining> remain; <marshal> loses <attacker_losses>" and
   `garrison_destroyed` (+ the sibling `occupation_started` line "must hold
   N turn(s)") in the `_format_bombardment` style, with `cannon_distant`.
   Never the server `message` (CA8-6's reason stands).
3. Optional record: a single `garrison_destroyed` `event_log` row at the
   FALL (not the hold), added to `CAMPAIGN_LOG_TYPES` + a one-liner arm +
   gazette `_WAR_TYPES`, carrying `attacker_nation`/`defender_nation`/
   `region`; flip the nine 160-pins consciously. The hold stays a
   result-event-only surface by design (the cap).

**Existing pins found:**
- `tests/test_fog_endpoint_filters.py::TestEnemyPhaseFilter::
  test_battle_involving_player_always_shown`, `test_action_in_fogged_region_
  suppressed`, `test_enemy_event_in_fogged_region_suppressed` (event type
  `"fortify"`), `test_player_marshal_name_match`, `test_player_nation_events_
  always_shown`, `test_enemy_attrition_shown_at_full_visibility` - none
  uses a garrison event; a garrison own-soil arm flips none.
- `tests/test_pt_e_turn_report.py::TestABloodlessCaptureIsReported::
  test_the_filter_reads_that_field` - `assert 'evt.get("captured_from") ==
  player_nation' in src` (source-text; untouched by an additive arm).
- `tests/test_wo_slice12_copy_sweep.py::test_the_enemy_phase_keeps_an_ai_
  attack_capture_of_our_soil` - stamped vs bare `conquest` through the
  filter; untouched.
- `tests/test_garrison_system.py::test_garrison_assault_returns_events` -
  `assert event["type"] in ("garrison_assault", "garrison_destroyed")`;
  `test_garrison_destroyed_event_on_collapse` - `assert "conquest" in
  event_types or "garrison_destroyed" in event_types`. Pin the TYPE names;
  renaming the event would flip them.
- `tests/test_r1_characterization.py::TestGarrisonPipeline::
  test_garrison_hold_records_diplo_battle` - `assert
  _count_battle_records(world) > initial_records` on the HOLD path: an
  existing pin that already contradicts FA-N21's "no other trace" premise.
- `.gd` source-text pins that read `enemy_phase_dialog.gd`:
  `tests/test_creative_audit_ca8_2026_08_04.py:334/344/374` (CA8-6 verb
  arms), `tests/test_pt_g_voice_and_naming.py:377/384/450`,
  `tests/test_ca9_row3_a7_jealousy_note.py:445`,
  `tests/test_marshal_voice_tier1.py:307`,
  `tests/test_creative_audit_ca9_2026_08_08.py:2523` - none asserts on the
  event loop's type arms; adding arms flips none.
- The nine `len(CAMPAIGN_LOG_TYPES) == 160` pins (only if seam 3 lands).

### FA-N21 (P2) - the render half

**Ran:** the same probes; the `.gd` census.

**Evidence:** `grep` for any of the six garrison keys plus `captured_by` /
`captured_from` over `scripts/*.gd` and `scenes/*.gd` returns nothing; the
only backend reader outside the producer is `executor.py`'s
`_res.get("occupation_started")` (the "walked in unopposed" arm). With the
row forced visible the mirror of `_format_action` renders exactly
`- Mack attacks Rhineland` and `<NO ARM for event type 'garrison_assault'>`.

**Verdict: DUPLICATE (of FA-23) - one defect, three seams.** FA-23 is the
row of record (VERIFIED Sept 2; it names fog + render + log); FA-N21 names
the render seam only. Merge FA-N21's correct render prescription ("build
from the structured fields, never pipe `message`", `cannon_distant`) into
FA-23's step 2 and strike FA-N21 as absorbed.

**What FA-N21's own fix would break:** nothing in code - but it ships
production-dead for the ordinary P4.25 geometry (the row is dropped
upstream; Part F `survives fog: 0`), and it renders only on the two
survivable rows (assaulter FULL, or the fortified fall where the assaulter
has moved onto the lit province). Its test (1) asserts the hold "adds 0
rows to `world.event_log`" - incompatible with FA-23's `log_event` shape;
the recommendation above (log only the fall) satisfies both.

### FA-N33 (P3) - the enemy army walks into a French province

**Ran:** `probe_2_move_capture.py`.

**Evidence (AI side, geometry manufactured - at boot no AI marshal at war
with France is adjacent to an undefended French province):**
```
Driving: Mack (Austria) @ Swabia move -> Rhineland (controller France, garrison 0)
message: Mack moves from Swabia to Rhineland. Rhineland falls to Austria! (was France) (1,560 lost to march)
events: [{"type": "move", "marshal": "Mack", "from": "Swabia", "to": "Rhineland",
          "captured_from": "France", "captured_by": "Austria", "march_losses": 1560}]
event_log rows added: [('region_captured', 'Rhineland', 'France', 'Austria', 'secure')]
survives _build_visible_enemy_phase: 1
any battle/bombardment/conquest event: False
client would render: - Mack moves to Rhineland
                     <NO ARM for event type 'move' (keys [...captured_by, captured_from...]) -> renders nothing>
campaign log keeps the region_captured row: 1 ['Rhineland captured by Austria (secure)']
dispatch headline: {"class": "home_captured", "weight": 99,
                    "text": "Sire - Rhineland has fallen. Enemy colours fly over French homeland soil."}
```
**Player mirror:** `Bernadotte @ Franconia -> Bohemia (held by Austria)`:
`message: Bernadotte moves from Franconia to Bohemia. Bohemia falls to
France! (was Austria) (170 lost to march) ... Your forces have taken
Bohemia. Plunder it for 800 gold ... or secure it ...`,
`pending_capture_choice: True`. The terminal states the capture and asks
the question; the enemy phase states neither.

**Verdict: REPRODUCED at the dialog, NARROWED** - the province does not
fall "in silence"; the campaign log, the dispatch headline and the map all
carry it. The silent surface is the one whose job is the report, which is
the PT-E5 argument again one layer down: PT-E5 made the row SURVIVE fog and
nobody gave the client an arm to read what it carries.

**Seam by symbol:** `enemy_phase_dialog.gd::_format_action` - the events
loop's `conquest` arm has no sibling for a `move` event carrying
`captured_by`. The producer (`movement_executor._execute_move`, the
`captured_on_move` block) and the fog filter (PT-E5 arm) are correct;
`main._collapse_enemy_move_chains` / `_forced_march_entry` preserve every
hop event, so the arm also works under a collapsed forced march.

**What the filed fix would break:** nothing - no client file reads the
key, and the collapse keeps it. One correction to the row: "there is no
per-hop plunder/secure choice on a march, so no choice suffix" is false for
the AI. `_attempt_region_capture` returns `"capture_choice": ai_choice`
(measured: the log row carries `secure`; `_apply_ai_capture_choice` can
return `plunder` since the IGR-E addendum made AI plunder live). The move
producer just never stamps it on the event, so an AI plunder-on-march would
render as a bare capture while the campaign log reads "(plunder)".

**Minimal correct fix:** (1) `enemy_phase_dialog.gd`: a `move` arm gated on
non-empty `captured_by`, emitting the conquest arm's exact line and suffix
vocabulary (`Region captured: <to>` + `(secured)`/`(plundered)`); (2) one
line in `movement_executor._execute_move`'s `captured_on_move` block:
`events[0]["capture_choice"] = capture_result.get("capture_choice")` (both
sides, GR5) so the suffix is honest. Note the two vocabularies already in
play: the campaign log prints "(secure)" (the `method` key) and the enemy
phase "(secured)".

**Existing pins found:**
- `tests/test_pt_e_turn_report.py::TestABloodlessCaptureIsReported::
  test_the_move_event_carries_the_capture` - `assert 'events[0]
  ["captured_from"] = _old_controller' in src` (untouched).
- `tests/test_enemy_phase_presentation.py::TestForcedMarchCollapse::
  test_capture_hops_keep_their_conquest_events` - builds a synthetic
  `{"type": "conquest", "region": "Wessex", "capture_choice": "secure"}` on
  a MOVE entry and asserts it survives the collapse. The move producer never
  emits a `conquest` event; the pin (and `_forced_march_entry`'s docstring
  "a capture-on-move keeps its conquest event") pass on a shape that does
  not exist. It would not flip under the fix, but it should be re-based on
  the real `move`+`captured_by` shape so it binds.

### FA-N75 (P2) - the coalition detail card after the CA8-D2 collapse

**Ran:** `probe_3_coalition_card.py`, `probe_3b_advisory_weak_link.py`.

**Evidence (1805 boot, `world.war_exhaustion = {Britain 20, Austria 55,
Russia 31}`):**
```
war_instances: {'war_1': {'active_diplo_keys': ['Britain|France', 'Austria|France', 'France|Russia', ...],
                          'side_by_nation': {France: attackers, Britain/Austria/Russia: defenders, ...},
                          'defender_leader': 'Britain'}}
=== SHIPPED (collapse ON) ===
wars: 1
   ('Britain', ['Britain', 'Austria', 'Russia'], in_coalition=True, leader=True, WE=None, 'war_1', multi=True)
coalition: {"name": "Third Coalition", "leader": "Britain", "posture": "aggressive", "coordination": [], "weak_link": null}
members visible to the card: ['Britain']   coordination pairs: 0 | weak_link: None
Target buttons the card would add: []
=== FLIP (collapse = identity) ===
wars: 3
   ('Britain', None, True, True, None, 'war_1', None)
   ('Austria', None, True, False, 55, 'war_1', None)
   ('Russia',  None, True, False, None, 'war_1', None)
coordination pairs: 3 [Britain-Austria Good, Britain-Russia Good, Austria-Russia Good]
weak_link: Austria
Target buttons: ['Austria', 'Russia']
nation visibility Britain = unknown | Austria = partial | Russia = unknown
legacy make_world() war_instances: {}
```
**Verdict: REPRODUCED exactly as filed.** The flip is the sole cause
(identity collapse restores every block).

**Seam by symbol:** `war_status.build_active_wars` - the statement `wars =
_collapse_shared_war_instance_rows(world, france, wars)` runs BEFORE the
`# -- Coalition metadata --` block, which derives `members`, the
`coordination` pair loop and `weak_link` from the already-collapsed list;
the authoritative `coalition_members` set built at the top of the function
is unused there. Client consumers of the same collapsed `wars`:
`war_detail_popup.gd::show_coalition` (the bar loop `for w in wars: if
w.get("in_coalition")` and the Target loop `... and not
w.get("is_coalition_leader")`), and `_render_coalition_detail` (the member
line loop). `main.gd` passes `_cached_wars = active_wars_data.get("wars")`
straight through. The Coordination and Weak-link blocks read
`coalition_data`, not `wars`.

**A consumer the row did not name:** `diplomatic_advisory.
_build_situation_recommendation` (the W6-9 assess verb) reads `weak =
(coalition_info or {}).get("weak_link")` in its rung-2 fallback, with
`coalition_info` supplied in production by `build_active_wars(world)` -
so the "Court <weak link>" counsel is dead on every multi-participant war.
Measured: on the boot board it is masked twice over - the NA-1 design rung
answers first (`Satisfy their design (Britain)`), and with that stubbed the
weakest-ally arm answers (`Shore up Spain`) - so the dead fallback is
reachable only when France has no ally to shore. Its pin
(`tests/test_w6_assessment_verb.py::test_aggressive_coalition_recommends_
shoring_weakest_ally`) passes a literal `{"weak_link": "Prussia"}` and does
not pin the production join.

**Which of the five surfaces each fix restores:**
- (a) hoist the metadata block above the collapse: restores Coordination
  and Weak link (and the advisory fallback) with no `.gd` diff and no new
  key. The bars, the member lines and the Target buttons stay dead - they
  iterate `wars`, not `coalition_data`. Two of five. CAUTION: the metadata
  block sits AFTER the leader-first sort; if it is hoisted above the sort
  too, `members` order becomes `diplomatic_states` insertion order and
  `tests/test_war_status.py::TestCoalitionCoordination::
  test_coordination_quality_labels` (`assert coord[0]["nation_a"] ==
  "Britain"`) may flip. Sort the pair rows, derive the metadata, THEN
  collapse.
- (b) `_collapse_shared_war_instance_rows` stamps `combined
  ["coalition_member_rows"] = [the pair rows it folded, leader first]`
  (every key the card reads - `opponent`, `war_score`, `war_exhaustion`,
  `army_strength`, `is_coalition_leader`, `in_coalition` - is already on a
  pair row), and the metadata block reads `members`/`weak_link` off those
  rows (or is hoisted per (a)). `.gd` diff: one helper in
  `war_detail_popup.gd`, `_coalition_member_rows(wars)` returning the
  flattened `coalition_member_rows` of any row that carries it, else the
  `in_coalition` rows; used in the `show_coalition` bar loop, the
  `show_coalition` Target loop, and the `_render_coalition_detail` member
  loop. `_shared_coalition_war_id(wars)` and the HUD
  (`war_status_panel.gd`) are untouched. Five of five.

**What the filed fix would break:** (a) nothing beyond the sort caveat
above; (b) nothing measured - the key is additive on the combined row, the
HUD never reads it, and the CA8-D2 close-out pins
(`tests/test_ca8_gate_closeout_2026_08_07.py:250-267`) read
`is_multi_participant_war` / `opponents` on the collapsed row, which stay.

**Existing pins found:**
- `tests/test_war_status.py::TestCoalitionCoordination::
  test_coordination_quality_labels` (`assert len(coord) == 1`, `coord[0]
  ["nation_a"] == "Britain"`) and `TestCoalitionWeakLink::
  test_weak_link_highest_we` (`assert result["coalition"]["weak_link"] ==
  "Prussia"`) - both on `make_world()`, whose `war_instances` is `{}`
  (measured), so `_collapse_shared_war_instance_rows` returns its input
  unchanged and the pins pass today for exactly the reason the row states.
  They pass after either fix too; a new pin must be built on
  `from_scenario(europe_1805.json)`.
- `tests/test_ca8_gate_closeout_2026_08_07.py` rows 250-267 - read the
  collapsed row's `opponents`; untouched by an additive key.

## Cross-row findings

1. **The shipped boot cannot produce either the FA-23 or the FA-N33
   geometry.** No enemy marshal at war with France stands adjacent to a
   French garrison (Paris 25k / Normandy 12k / Flanders 12k) or to an
   undefended French province; Moore@London is refused at Normandy -
   `crossing_allowed(Britain, London->Normandy) = False` under the NV-4 host
   rule, with a `naval_turnback` row logged per attempt. The NV-V record's
   "grinding the depot down in two garrison assaults" predates that rule.
   Both rows are mid-campaign (or player-detachment) shapes; pins must
   build them.
2. **The assault lights the assaulted province and the filter ignores it.**
   `WorldState.update_intel_from_battle` grants persistent FULL on the
   battle region (measured: Rhineland partial -> full, surviving
   `calculate_visibility`), while `_filter_enemy_phase_by_visibility` keys
   the region check on the assaulter's location. The intel model is more
   generous than the report on the same event.
3. **A PT-D4 pin and docstring assume an event the producer never emits.**
   `_forced_march_entry`'s docstring ("a capture-on-move keeps its conquest
   event") and `tests/test_enemy_phase_presentation.py::
   test_capture_hops_keep_their_conquest_events` both use a synthetic
   `conquest` event on a move hop; the real move producer emits
   `move`+`captured_by`. The fixture-fiction class again.
4. **A backend consumer of FA-N75's dead key:** `diplomatic_advisory.
   _build_situation_recommendation` rung-2 fallback (`Court <weak link>`),
   fed by `build_active_wars`; its pin passes a literal dict.
5. **FA-N21's "no other trace" premise is contradicted by an existing pin:**
   `tests/test_r1_characterization.py::test_garrison_hold_records_diplo_
   battle` asserts the hold writes a diplomacy `battle_records` row. The
   war score moves on an assault the player never sees.
6. **The `len(CAMPAIGN_LOG_TYPES) == 160` pin lives in NINE files, not five:**
   `test_bph_a_term_ownership.py`, `test_ca9_row3_a7_jealousy_note.py`,
   `test_ca9_row3_phase_a.py`, `test_ca9_row3_q2_council_command.py`,
   `test_campaign_log.py`, `test_igr_a_honest_copy.py`,
   `test_igr_b_campaign_log_readable.py`, `test_igr_f_envoy_digest.py`,
   `test_wo_slice4_the_capital_speaks.py`.
7. **Two vocabularies for one capture choice:** the campaign log one-liner
   prints `(secure)`/`(plunder)` (the `method` key) while the enemy-phase
   `conquest` arm prints `(secured)`/`(plundered)`.
8. **The AI's march-capture choice is decided but not carried:**
   `_attempt_region_capture` returns `capture_choice`, the log row carries
   it as `method`, the move event does not carry it - so FA-N33's "no
   choice suffix" clause is wrong for the AI (plunder is live since IGR-E).
9. **The fortified fall path survives the fog filter for the wrong reason:**
   the assaulter has marched onto the lit province, so
   `ai_marshal.location` is FULL - the row shows, then renders nothing
   (no arm for `garrison_destroyed`/`occupation_started`).
10. **Harness traps hit:** `Marshal.personality` (there is no
    `personality_type` - the IGR-E trap); `Region.buildings` are
    `{"type", "damaged"}` dicts, not strings; visibility must be recomputed
    after relocating marshals in a probe (a stale FULL produced a false
    fog verdict on my first C2 run); `_get_nation_visibility(nation, world)`
    takes the nation first.

## Probe inventory

All under `<scratchpad>\repro\h2\`:
- `probe_1_garrison_assault.py` - FA-23/FA-N21 Parts A-F (synthetic row,
  real hold path, both fall paths, log census, the Moore@London live case,
  the player-detachment geometry picked by P4.25).
- `probe_1b_fog_keying.py` - the update_intel_from_battle light vs the
  filter's assaulter-location key; the two arms that would carry the row.
- `probe_2_move_capture.py` - FA-N33 AI move-capture end to end + the
  player mirror.
- `probe_3_coalition_card.py` - FA-N75 build_active_wars ON/OFF the
  collapse, the Target-button set, the advisory consumer.
- `probe_3b_advisory_weak_link.py` - the advisory fallback with the design
  rung stubbed; the per-court WE fog gate.
