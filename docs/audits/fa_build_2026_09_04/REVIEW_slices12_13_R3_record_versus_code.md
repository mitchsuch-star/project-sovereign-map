# FA slices 12+13 review round - lens report R3_record_versus_code

Transcribed VERBATIM from the agent return value. Review fleet run at
master 43691f14 against a git-archive snapshot; 3 lenses x 2 refuters per
finding, 53 agents, 0 errors.

## Verdict

Twelve findings, three of them P2, and none of the three is a fix that failed to run — all three are the fixes running exactly as written and being wrong about who the player is. The road-home latch cannot tell a refusal from a forced retreat (measured: `offer_road_home` returns [] with the latch True and returns the order with it False, on the identical board, and Ney is interned at t5); the new unbounded grace freezes the internment clock for every corps of the nation, not just the frozen one (measured: nobody interned in 31 turns vs both at t5 in control, grant 7→37); and the new mid-treaty beat tells France that Berthier ordered an Austrian marshal home, twice addressing the Emperor in one sentence, while the campaign log tells France its peace is "with France". The fog arms themselves are correct — a corridor between two foreign powers is properly invisible — but the renderers assume the marshal's nation is always the reader. On the client side the Alt arm is layout-hostile in two independent ways (AltGr presents as Ctrl+Alt, so AltGr+E ends the turn and eats the character; the bare map keys match `physical_keycode` while the new arm matches `keycode`), and Alt+Tab is a key Windows never delivers — already being fixed in the uncommitted tree. The highest-value item I was asked to attack came back CLEAN: I ran build.bat's licence block verbatim, comments and all, from a foreign working directory, and all 16 notices plus the umbrella file land at errorlevel 0; `copy` sets and resets errorlevel exactly as the code assumes, including on a zero-match wildcard. Serialization is clean, and the parse harness genuinely covers the `Utils.launch_hint()` call — proven by measuring that `load()` returns non-null for a bad static while `reload()` returns 43.

## Findings

### [P2] The road-home latch treats an order the ENEMY destroyed as the player's refusal — the corps is never re-offered and is interned

- **inside the slice:** True
- **seam:** backend/game_logic/withdrawal.py::offer_road_home (the `existing is None and ... road_home_offered` guard) + backend/models/marshal.py::Marshal.road_home_offered

**Measured**

Snapshot 43691f14, real 1805 board, Ney parked at Bohemia, France->Austria PEACE through the real chokepoint `diplomacy.set_diplomatic_state`. Corridor issues `Ney -> Franche-Comte`, `road_home_offered = True`. I then set `strategic_order = None` — VERBATIM what `combat_executor.py:3689` does on a forced retreat, one line below a CRITICAL notification whose own body is "Their MOVE_TO order has been cancelled." (siblings at :3593 encircled-retreat and :3777 shattered).

Causality arm, identical board, ONE boolean flipped:
  road_home_offered=True  -> re-issue: []
  road_home_offered=False -> re-issue: [{'marshal': 'Ney', 'nation': 'France', 'from': 'Bohemia', 'to': 'Franche-Comte'}]
  lever THE_ROAD_IS_OFFERED_WHILE_HE_IS_STRANDED=False -> re-issue: [{'marshal': 'Ney', ...}]

Ticking the corridor with the latch standing: evacuation_lapsing t2/t3/t4 (turns_left 2/1/0), `marshal_interned` t5, and `"Ney" not in world.marshals` — the corps is off the board.

The latch is therefore the sole cause of the refusal.

**Repro**

1) WorldState.from_scenario(europe_1805.json); 2) marshals['Ney'].location='Bohemia'; strategic_order=None; road_home_offered=False; 3) diplomacy.set_diplomatic_state(w,'France','Austria','PEACE') — Ney gets the road, latch goes True; 4) marshals['Ney'].strategic_order=None (the forced-retreat site does exactly this); 5) withdrawal.offer_road_home(w,'France') returns []; 6) loop `w.current_turn += 1; withdrawal.process_evacuation_grants(w)` — warned t2/t3/t4, interned t5.

**Fix**

The latch must record a PLAYER decision, not the absence of an order. Two shapes, either works: (a) keep the issuance-keyed write but CLEAR `road_home_offered` at the three engine sites that destroy an order the marshal did not choose to drop — the `clear_order_bound_interrupt(marshal)` calls at combat_executor.py:3593/:3689/:3777 are already the exact three lines, so add `marshal.road_home_offered = False` beside each; or (b) invert it — stamp the refusal in `_execute_cancel` and the answer routes and leave issuance alone. (a) is smaller and keeps the docstring's argument intact for the cancel seams it was written for. Either way the docstring's claim that issuance-keying "covers every way the order can be let go" must be narrowed in place: it also covers ways the player never chose.

### [P2] One unanswered modal freezes the internment clock for EVERY corps of that nation in the corridor, without bound

- **inside the slice:** True
- **seam:** backend/game_logic/withdrawal.py::_is_immobile / _awaiting_the_players_word, and the `if grace_nations.intersection(parts)` refresh in process_evacuation_grants

**Measured**

Snapshot 43691f14. Two French corps (Ney, Davout) stranded at Bohemia, France->Austria PEACE. Davout's order cancelled in both arms (a deliberate loiterer). Only difference: Ney carries `pending_interrupt = {'interrupt_type': 'cannon_fire', ...}`.

  frozen=False: interned [(5,'Ney'), (5,'Davout')]; corridor CLOSED at t6.
  frozen=True : interned NOBODY across 31 turns; grant expiry walks 7 -> 37 and is still climbing; Davout still on the board at Bohemia.

Before this slice `_is_immobile` was `retreat_recovery > 0`, bounded 0-3, so grace was bounded. `_awaiting_the_players_word` is unbounded, `grace_nations` is keyed per NATION, and the refresh `grants[key] += 1` is keyed per PAIR — so the frozen corps buys immunity for every colleague in that corridor and the `continue` above skips them entirely.

**Repro**

1) Park Ney and Davout at Bohemia; 2) set_diplomatic_state France/Austria PEACE; 3) `marshals['Ney'].pending_interrupt = {'interrupt_type':'cannon_fire','marshal':'Ney'}`; 4) `marshals['Davout'].strategic_order = None`; 5) loop 30x `current_turn += 1; process_evacuation_grants(w)` — no internment ever fires and `evacuation_grants['Austria|France']` grows monotonically.

**Fix**

Scope the grace to the marshal, not the nation and not the pair: in the judging loop, `if _is_immobile(marshal): continue` already skips HIM — the pair-wide `grants[key] += 1` is what over-reaches. Either drop the pair refresh and let the frozen corps simply not be judged (his own surplus is preserved because he has not moved, which is the same effect the refresh was buying), or track `grace_marshals` and refresh only if EVERY stranded marshal of the pair is immobile. The comment's bound argument ("expiry - current_turn is CONSTANT under grace") is true for the frozen corps and false for the others, and should be corrected in place.

### [P2] The new mid-treaty headline tells France that BERTHIER put an Austrian marshal on the road home, and says "Sire" twice

- **inside the slice:** True
- **seam:** backend/game_logic/withdrawal.py::_offer_event (the `message` string) + backend/game_logic/dispatch.py `_HEADLINE_TEMPLATES['road_home_mid_treaty']`

**Measured**

Snapshot 43691f14. Corridor opened by a stranded Davout, Davout then brought home so nothing French is lapsing; Mack stranded at Silesia (Prussian soil, France's `get_region_intel('Silesia').visibility == 'unknown'`); turn advanced 3 so the original peace beat leaves the 2-turn window.

FRANCE's morning-dispatch HEADLINE, verbatim:
  class  = road_home_mid_treaty
  weight = 69
  text   = "Sire — under the peace with Austria. Mack is on the wrong side of the frontier at Silesia, Sire — the ground changed hands under him. Berthier has put him on the road home to Moravia; he has 3 turn(s) of safe passage."

Three faults in one lead item: (a) Berthier is FRANCE's chief of staff, reported issuing marching orders to an Austrian marshal; (b) the template prefixes "Sire —" and the message contains a second one; (c) it names a foreign corps' exact province and destination in a province France's own intel reads `unknown`.

(c) is not a NEW fog class — `evacuation_granted`'s filter is the recorded WIN-D3 signatory exemption (`player_nation in (nation_a, nation_b)`), which I verified holds: a corridor between two foreign powers is correctly filtered out. But the original beat fired ONCE at the treaty; this one can fire on any turn of the corridor and, unlike the original, is routinely about a corps standing on a THIRD power's soil.

**Repro**

1) Davout to 'Bohemia', Mack to an Austrian home province, both `road_home_offered=False`; 2) set_diplomatic_state France/Austria PEACE (grant written: {'Austria|France': 7}); 3) move Davout to a French home province so he is not lapsing; 4) Mack.location='Silesia', strategic_order=None, road_home_offered=False; 5) `w.current_turn += 3`; process_evacuation_grants(w); 6) `dispatch._build_headline(w, 'France')`.

**Fix**

`_offer_event` must compose its sentence from the READER's side, not the marshal's. Pass the player nation (or make the message a template rendered at dispatch time): when `offer['nation'] != player_nation`, drop "Berthier has put him" for something reader-true ("Vienna has recalled him" / "he has been put on the road home"), and strip the embedded "Sire" so the headline template owns the address exactly once. The same builder feeds the campaign log, so fixing it here fixes L2-4's sibling.

### [P3] The mid-treaty campaign-log line names the READER as the counterparty — France reads "under the peace with France"

- **inside the slice:** True
- **seam:** backend/campaign_log.py::format_event_oneliner, the `if event.get("mid_treaty")` branch inside `if event_type == "evacuation_granted"`

**Measured**

Snapshot 43691f14, same board as L2-3. FRANCE's own campaign log, through `filter_campaign_log` then `format_event_oneliner`:

  "Mack put on the road home from Silesia to Moravia under the peace with France — 5 turns"

The new `mid_treaty` arm hard-codes `b = event['nation_b']` as "the other power". `_offer_event` sets `nation_a = offer['nation']` (the marshal's nation) and `nation_b = counterpart`, so `b` is whichever signatory happened not to own the marshal — it is correct for exactly one of the two readers and wrong for the other. The pre-slice arm ("Peace between {a} and {b}") was reader-independent; the new arm is not. `a` is assigned and never used in this branch.

**Repro**

As L2-3 steps 1-5, then `filter_campaign_log(new_events, w)` and `format_event_oneliner(...)` on the `evacuation_granted` row with `mid_treaty=True`.

**Fix**

`format_event_oneliner` already receives no player nation, so either render "under the peace between {a} and {b}" (symmetric, matching the sibling arm two lines below), or have `_offer_event` also stamp a display-only `counterpart_for_log` and pick the pair member that is not `nation_a` only when `nation_a` is the reader — the symmetric form is smaller and cannot go stale.

### [P2] AltGr is Ctrl+Alt on Windows, so the new Alt arm ends the turn when a European keyboard types a character — and swallows the character

- **inside the slice:** True
- **seam:** godot-client/project-sovereign/scripts/main.gd::_on_command_input_gui_input (`elif event.alt_pressed and _alt_game_key(...)`) and ::_alt_game_key KEY_E arm

**Measured**

NOT measured in-client (I have no non-US layout to switch to); reasoned from source plus the Windows key-modifier contract. `_on_command_input_gui_input` dispatches on `event.alt_pressed and _alt_game_key(event.keycode)` with NO `ctrl_pressed` guard, and `_alt_game_key` returns `true` on a match so the caller `accept_event()`s unconditionally ("Alt+E must never type an 'e'"). On Windows AltGr raises both VK_MENU and VK_CONTROL, so `alt_pressed` is true while the player is composing an ordinary character: AltGr+E is `ę` on Polish and `€` on several layouts. The result is both halves of a defect — the character never reaches the LineEdit AND the turn ends.

The pre-existing PC15-18 `_SCREEN_HOTKEYS` arm one `elif` above shares the hole, but its six actions are harmless screen toggles. This slice added END TURN — irreversible — and the terminal collapse to the same modifier.

**Repro**

Set the Windows input language to Polish (Programmers) or German, focus the command line, type AltGr+E. Expected: `ę` / `€` appears. Predicted actual: nothing types and the turn ends.

**Fix**

Add `and not event.ctrl_pressed` to BOTH Alt arms (the new game-key arm and the PC15-18 screen-key arm), or equivalently require `event.unicode == 0`. AltGr always presents as Alt+Ctrl on Windows and a real Alt shortcut never carries Ctrl, so the guard costs nothing and closes the pre-existing hole with the new one.

### [P3] Alt+Tab is the Windows window switcher — the README and the KEY_TAB arm teach a key the game can never receive

- **inside the slice:** True
- **seam:** godot-client/project-sovereign/scripts/main.gd::_alt_game_key KEY_TAB arm; deploy/README_TESTER.txt HOTKEYS block

**Measured**

Source: `_alt_game_key`'s `KEY_TAB` arm, and README_TESTER.txt's new line "Tab       — Collapse/restore the terminal (Alt+Tab while typing)". A windowed Godot app on Windows does not receive Alt+Tab; the shell consumes it and the app gets WM_KILLFOCUS. Not measured in-client. Windows is the only shipped target (deploy/build.bat, InkAndIron.exe).

ALREADY BEING FIXED in the uncommitted working tree, which I diffed against the snapshot: `KEY_TAB, KEY_QUOTELEFT` plus a README rewrite to "Tab / Alt+`". Reporting it because it is a defect in the LANDED commit 43691f14 and because the README rewrite is the only documented focus-safe way to collapse the terminal.

**Repro**

Focus the command line in the running client on Windows, press Alt+Tab. The OS switches windows; the terminal does not collapse.

**Fix**

Already taken in the working tree (Alt+` alongside Alt+Tab). When it lands, keep Alt+Tab in the match — it costs nothing and works on platforms whose window manager lets it through — and make sure the boot-help line in `_on_connection_test` names the backtick too, not only the README.

### [P3] The bare map keys match `physical_keycode`; the new Alt arm matches `keycode` — on a non-US layout the two routes answer different physical keys

- **inside the slice:** True
- **seam:** godot-client/project-sovereign/scripts/main.gd::_alt_game_key vs godot-client/project-sovereign/scenes/map_renderer_base.gd::_unhandled_input

**Measured**

Source, both seams read: `scenes/map_renderer_base.gd::_unhandled_input` does `match event.physical_keycode:` for KEY_EQUAL/KEY_KP_ADD, KEY_MINUS/KEY_KP_SUBTRACT, KEY_HOME, KEY_M. `scripts/main.gd::_alt_game_key` does `match keycode:` on the same six. `physical_keycode` is layout-independent (US position); `keycode` is the label. On AZERTY the key LABELLED M sits at the US-';' position, so bare M is dead there while Alt+M works, and the bare route instead fires on the ',' key. On QWERTZ the '-' key sits at US-'/', so bare '-' zoom-out is dead while Alt+'-' works. Not measured (no layout available).

Note the screen keys are consistent — `_SCREEN_HOTKEYS` and `_unhandled_input`'s L/T/G/D/R/N both use `keycode`. Only the four map keys disagree, and the disagreement is new because the Alt arm is new.

**Repro**

Switch Windows input to French (AZERTY). Unfocus the command line and press the key labelled M — nothing happens; press the key labelled , — the map view cycles. Focus the command line and press Alt+M — the map view cycles.

**Fix**

Pick one and use it on both routes. `keycode` (the label) is the better choice for keys the README names by their printed character (M, +, -, Home), so change `map_renderer_base._unhandled_input` to `match event.keycode:` — and pin the two seams against each other so they cannot drift again.

### [P4] `_map_keys_live()`'s docstring names the wrong twin, and the gates genuinely differ under a modal

- **inside the slice:** True
- **seam:** godot-client/project-sovereign/scripts/main.gd::_map_keys_live docstring; godot-client/project-sovereign/scenes/map_renderer_base.gd::_unhandled_input

**Measured**

The docstring says the map keys' gate is "the same one their unfocused twin obeys (`_unhandled_input` returns above them when a screen is open)". Measured by grep: `main.gd::_unhandled_input` has NO KEY_M / KEY_HOME / KEY_EQUAL / KEY_MINUS branch at all — the only handlers are in `map_renderer_base.gd:2227-2233`, whose gate is `text_focused or not panning_enabled`, with no modal check. So `_map_keys_live()`'s `not _is_modal_dialog_open()` is STRICTER than the twin: with a modal open, bare M still cycles the map view and Alt+M does not.

**Repro**

Open any modal popup that does not disable panning, press bare M (view cycles), then focus the command line and press Alt+M (nothing).

**Fix**

Correct the docstring to name `map_renderer_base._unhandled_input` and its real gate, and decide the modal rule once — either add `not _is_modal_dialog_open()` to the bare route or drop it from `_map_keys_live()`. The stricter Alt arm is the safer default, so widening the bare route is the honest fix.

### [P4] The "free win" — naming the map view you landed on — was given only to the Alt route

- **inside the slice:** True
- **seam:** godot-client/project-sovereign/scenes/map_renderer_base.gd::_unhandled_input KEY_M arm

**Measured**

`_alt_game_key`'s KEY_M arm captures `cycle_map_fill_mode()`'s String and prints "Map view: <mode>". `map_renderer_base.gd:2233` still calls `cycle_map_fill_mode()` bare and discards the return, which is the very discard the slice's own comment describes ("its only other caller discarded it"). So the same key tells you where you are only when you are typing.

**Repro**

Unfocus the command line, press M — the view changes silently. Focus it, press Alt+M — the terminal names the new view.

**Fix**

Emit the same line from the bare route (the renderer already has no terminal handle, so raise a signal the client renders, or move both routes through a single `main.gd` helper).

### [P4] `road_home` and `road_home_mid_treaty` share weight 69 inside a 2-turn window, so a top-up on the very next turn re-announces "the war with Austria is over"

- **inside the slice:** True
- **seam:** backend/game_logic/dispatch.py HEADLINE_WEIGHTS['road_home_mid_treaty'] and _build_headline's window

**Measured**

Snapshot 43691f14. `_build_headline`'s window is `turn >= current_turn - 1`. With the peace at t1 and a top-up at t2, both `evacuation_granted` rows are candidates at weight 69 and the ORIGINAL wins, so France's t2 headline reads "Sire — the war with Austria is over. 1 corps stands on the wrong side of the new frontier. Berthier has given them the road home — Davout to Franche-Comte...". Measured directly (probe E first run). Advancing 3 turns instead of 1 renders `road_home_mid_treaty`, confirming the tie is the cause.

Smaller than the defect the slice fixed (one turn stale rather than three), but it means the new template is skipped exactly on the turn a top-up is most likely.

**Repro**

Open the corridor at t1 with a stranded Davout; at t2 strand a second corps and run process_evacuation_grants, then _build_headline(w,'France').

**Fix**

Give `road_home_mid_treaty` weight 70 (or break the tie in favour of the newer event) so the later, more specific beat wins its own turn. The identity keys already differ, so nothing else needs to change.

### [P4] The Settings credits line hard-codes the SHIPPED layout in the same slice that created `Utils.launch_hint()` because layout depends on the build

- **inside the slice:** True
- **seam:** godot-client/project-sovereign/scripts/settings_panel.gd::_build_credits_section

**Measured**

settings_panel.gd now reads "Full terms: THIRD_PARTY_LICENSES.md, beside the game, with the per-family notices in licenses\\." unconditionally. In a source checkout — the arm `Utils.launch_hint()` exists to serve — THIRD_PARTY_LICENSES.md is at the repo ROOT, not beside the game, and `licenses\` does not exist at all (it is created by build.bat into deploy\dist). Verified: no `licenses` directory anywhere in the tracked tree; the folder appeared only when I ran the build block into a scratch dist.

**Repro**

Run the project from the editor, open Settings, read the credits line, then look for `licenses\` next to the running project.

**Fix**

Route the location clause through the same `OS.has_feature("editor")` split the slice already established — a `Utils.credits_location()` beside `launch_hint()` — or drop the location clause from the in-game string and leave it to the README, which is only ever read in the zip.

### [P4] The new soft-break tray alert carries no `details`, so its dedupe subject is empty and no consumer can read which vassal it is about

- **inside the slice:** True
- **seam:** backend/game_logic/vassal.py::record_vassal_break, the `world.notifications.add(_cr_notif(...))` call

**Measured**

Snapshot 43691f14, probe over `record_vassal_break`. Player-as-lord soft exits raise exactly 1 alert each:
  [1] Holland breaks free :: Holland is no longer our satellite. She stands alone — an independent power, and no war is declared.
  [1] Holland breaks free :: Holland is no longer our satellite. The armistice holds — no war is declared.
Foreign lord (Austria/Bavaria): 0 alerts, dispatch row queued `partial_on_nation`. Player-as-vassal (Prussia/France): 0 alerts, dispatch row on nation=France.

`create_notification` is called positionally with no `details`, so `NotificationCollector._identity`'s subject resolves to "" and identity is `(type, title, "")`. Titles differ per vassal so today nothing collapses — but the war-exit sibling at vassal.py:1229 has the same shape, and `_SUBJECT_KEYS` lists "vassal" specifically for this family. Latent, not live.

Correction to my own probe: I passed a fabricated `exit_path="vassal_rebellion_war"`; the real war exit passes `"vassal_rebellion"` (vassal.py:1245). Behaviour is identical (neither is in `_SOFT_BREAK_BODY`), so the finding stands unchanged. The lord-gate excluding the player-as-vassal case is CORRECT, not a bug — the body is written from the lord's mouth ("no longer OUR satellite") and would be nonsense addressed to the vassal.

**Repro**

`vassal.record_vassal_break(w, vassal='Holland', lord='France', exit_path='vassal_rebellion_independent')`, then inspect `w.notifications._pending[-1]` — no `details` key.

**Fix**

Pass `details={"vassal": vassal, "lord": lord}` as the sixth argument (the signature already accepts it), matching what `_SUBJECT_KEYS` expects, and do the same at vassal.py:1229 and :2756 while you are there.

## Record corrections

- withdrawal.py, the FA-33 rider comment at the grace refresh: "it is bounded in the only sense that matters: `expiry - current_turn` is CONSTANT under grace (both sides gain one), so the window never widens". Measured FALSE for everyone but the frozen corps. Two French corps stranded, one frozen on an unanswered interrupt: NOBODY is interned in 31 turns and the grant walks 7 -> 37, while the control arm interns both at t5 and closes the corridor at t6. `grace_nations` is per-NATION and the refresh is per-PAIR, so a corps who is not immobile and holds no order is skipped by `continue` indefinitely.

- withdrawal.py, `offer_road_home`'s docstring guard 4: "A guard keyed on CANCELLATION would have been fixed only at the seams somebody thought to name. Keyed on ISSUANCE, it covers every way the order can be let go, including ways nobody has enumerated." That is the argument FOR the bug: issuance-keying also covers the ways the player did not let it go. Measured: after a forced retreat clears the order (combat_executor.py:3689, which raises a CRITICAL "Their MOVE_TO order has been cancelled" in the same block), `offer_road_home` returns [] and Ney is interned at t5. Flip only `road_home_offered` to False on the identical board and it returns the order.

- The slice-12 commit subject and landing record, "a corps who declines it is not chased": the latch does not distinguish a decline from a destruction. Three engine sites (combat_executor.py:3593 encircled retreat, :3689 forced retreat, :3777 shattered) null the order without the player touching it, and all three leave the latch standing.

- withdrawal.py, `_offer_event`'s docstring: "The pair is the treaty actually affording him the passage, so the campaign-log fog arm (`player_nation in (nation_a, nation_b)`) and the dispatch arm both keep working unchanged." The FOG arms do keep working — I verified a corridor between two foreign powers is correctly invisible. The RENDERERS do not. Measured, France's own campaign log: "Mack put on the road home from Silesia to Moravia under the peace with France — 5 turns", and France's own headline: "Sire — under the peace with Austria. Mack is ... , Sire — ... Berthier has put him on the road home to Moravia". Both are written as if the marshal's nation is always the reader.

- main.gd, `_alt_game_key`'s docstring: "Each arm mirrors the gate its UNFOCUSED twin obeys, and that is load-bearing." True for KEY_E and KEY_TAB. FALSE for the four map keys: their unfocused twin is not in main.gd's `_unhandled_input` at all (grep finds no KEY_M/KEY_HOME/KEY_EQUAL/KEY_MINUS there) but in `scenes/map_renderer_base.gd:2227-2233`, whose gate is `text_focused or not panning_enabled` and which checks no modal. `_map_keys_live()`'s own docstring repeats the same wrong attribution.

- README_TESTER.txt and the slice-13 commit message: "Tab — Collapse/restore the terminal (Alt+Tab while typing)" and "the keys it advertises work while you type". Alt+Tab is the Windows window switcher and never reaches a windowed Godot app; Windows is the only shipped target. Already corrected in the uncommitted working tree (Alt+`), but the landed commit 43691f14 ships and documents a dead key.

- The slice-13 commit's claim that the six changed scripts being in the parse harness means the CALL is covered was worth checking and is CORRECT — but the harness's own `load_ok` alone would not have proved it. Measured on a purpose-built scratch Godot project: `ResourceLoader.load()` of a script calling a nonexistent static returns NON-NULL (load_ok would be true), and it is `script.reload()` — which the harness does call — that returns 43 / ERR_PARSE_ERROR. The coverage is real; it rests on the reload() step, not on the load.

## Unverified

"NOT MEASURED, stated as reasoned only:\n\n1. L2-5 (AltGr) and L2-7 (keycode vs physical_keycode). Both need a non-US Windows keyboard layout and the running client; I have neither in this session. The Windows AltGr = Ctrl+Alt contract and Godot's keycode/physical_keycode split are both well established, and both seams are unambiguous in source, but neither prediction was executed.\n\n2. L2-6 (Alt+Tab) was not driven in-client either. It is corroborated by the working tree already containing the fix.\n\n3. The template arm of `Utils.launch_hint()`. I measured the EDITOR arm empirically in a scratch Godot project (`OS.has_feature(\"editor\")=true`, `template=false`, `ProjectSettings.get_setting(\"application/config/version\")` reads back \"9.9.9 probe\"), which confirms `build_label()` and the editor branch. I did not run a Godot export, so the exported-template branch's runtime value is taken on Godot's contract.\n\n4. The slice-13 comment's claim about WHY the notices cannot ride the .pck (\"export_filter=all_resources walks the EditorFileSystem and skips entries it types TextFile\"). Verifying that needs an actual export; the build.bat copy makes it moot either way.\n\n5. I did NOT drive an end-to-end campaign. Everything backend is measured against the real 1805 scenario through the real `diplomacy.set_diplomatic_state` chokepoint and the real `withdrawal.process_evacuation_grants`, but by calling those functions rather than by ending turns over POST /command. L2-2's frozen-corps setup writes `pending_interrupt` by hand; the three producers of that field (combat_executor.py:3345, :3398, :5429) are all player-scoped, and `process_strategic_orders` is scoped to `m.nation == world.player_nation`, so I confirmed the state is player-reachable and AI-unreachable — but I did not reach it through gameplay.\n\nGR5 side-note I could not turn into a finding: `_awaiting_the_players_word` is nation-blind, and every producer of `pending_interrupt` is currently player-scoped, so an AI corridor can never take the unbounded grace a player's can. That is a latent asymmetry rather than a live one — if any future slice gives an AI marshal an interrupt, that nation's corridor becomes immortal with nobody able to clear it.\n\nMEASURED NEGATIVE RESULTS, reported because they were the lens's highest-value asks and they came back clean:\n\n- deploy/build.bat's licence block is CORRECT. I ran it verbatim, including its `::` comment block with its parentheses and quotes, from `%TEMP%`, writing into a scratch dist: all 16 tracked licence files plus THIRD_PARTY_LICENSES.md land (19 entries incl. dirs), exit errorlevel 0, zero WARNs. Specifically: `cd /d \"%~dp0..\"` makes cwd-independence real; `mkdir` creates the `licenses\\fonts` chain; a quoted destination ending in a backslash works for an internal command; `set \"X=...\"` at top level needs no delayed expansion (there are no blocks and no `!`); and `copy` sets errorlevel 1 on a missing source (T1), on a zero-match wildcard (T3 — so the comment's rename hazard IS caught), and on a missing destination directory (T4/T5), while RESETTING to 0 on success after a prior failure (T2) — so every `if errorlevel 1` in the block is sound. The classic leak is real for `set`/`echo`/skipped-`mkdir` (T6/T7/T8) but no `if errorlevel 1` in this file follows one of those.\n\n- `Utils` is a `class_name` global with NO autoload entry anywhere in project.godot, and pre-existing `Utils.backend_url()` statics already prove the pattern; the harness's `reload()` step catches a bad static (measured).\n\n- Serialization is clean: `tests/test_serialization_enforcement.py` 19 passed; `road_home_offered` is in to_dict and in from_dict with `.get(..., False)`; the SAVE_FORMAT_REFERENCE row exists; no other model carries a corridor field.\n\n- The FA-33 stamp removal is safe for every other consumer: the only arithmetic reader of `issued_turn` is `strategic.py:2633`, `order.issued_turn or order.started_turn`, and the treaty's order does set `started_turn`.\n\n- Fog: the mid-treaty event reuses the recorded WIN-D3 signatory gate correctly. A corridor between two foreign powers produced zero visible events for France.\n\n- Both slice test files are green on the landed snapshot: 62 passed, 2 skipped. The 2 skips are `git unavailable` — an artefact of my git-archive copy, and they pass in the real repo. Worth one line to the builder: the licence census pin degrades to SKIP rather than FAIL when git is absent, so in a packaging environment without git the only guard on the distribution obligation is silent.\n\nFORWARD-LOOKING NOTE on work already in flight. The working tree (uncommitted) replaces slice 12's unconditional `road_home_offered = False` reset in `open_evacuation_corridor` with one gated on `_nation_has_standing_grant(..., exclude=key)`. That closes a real hole, but it introduces a case worth pinning before it lands: a marshal who was CUT OFF (no `_nearest_home_region`, so `continue`d without an order) while carrying a stale latch will now NOT be reset when a second concurrent treaty opens, because his nation already has a standing grant. The landed unconditional reset covered him."
