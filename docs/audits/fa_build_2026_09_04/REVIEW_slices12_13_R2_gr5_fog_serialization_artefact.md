# FA slices 12+13 review round - lens report R2_gr5_fog_serialization_artefact

Transcribed VERBATIM from the agent return value. Review fleet run at
master 43691f14 against a git-archive snapshot; 3 lenses x 2 refuters per
finding, 53 agents, 0 errors.

## Verdict

Two real defects inside slice 12's own fixes, one of them a P1: the FA-33 grace rider has no ceiling and no scope, so a single unanswered question freezes the withdrawal deadline for every stranded corps of both signatories indefinitely — measured, the corridor never closes over 14 turns while the lapsing warning repeats the identical \"2 turn(s) left\" forever — and FA-N61's new mid-treaty beat has no side filter and no fog check, so France is told in Berthier's voice where an unseen Austrian corps stands and where it is marching, which is exactly the defect the peace-turn producer it sits beside carries a docstring paragraph about avoiding. Slice 13's Godot half is clean (parse harness EXIT=0, every gate I attacked held); its one residue, the README advertising Alt+Tab, is already being fixed in the working tree.

## Findings

### [P1] One unanswered question freezes the withdrawal deadline for EVERY stranded corps of both signatories, forever — the corridor never closes and the lapsing warning never counts down

- **inside the slice:** True
- **seam:** backend/game_logic/withdrawal.py::_is_immobile / process_evacuation_grants (the `grace_nations` refresh block)

**Measured**

Flip-arm probe on the landed snapshot (43691f14), driving `withdrawal.process_evacuation_grants` on the real 1805 board. Two French corps (Davout, Ney) both parked at Moravia, distance home 5, both declining the treaty's road; ONLY Davout carries an unanswered interrupt.

CONTROL (nobody has a question):
  t=2..4 grants={'Austria|France': 9}  evacuation_lapsing x2
  t=5    Ney=GONE Davout=GONE  marshal_interned x2
  t=6    grants={}  -> corridor closed, as designed

WITH ONE question parked on Davout:
  t=2  grants={'Austria|France': 10} Ney=stands Davout=stands
  ...
  t=15 grants={'Austria|France': 23} Ney=stands Davout=stands
Ney — who has no question, can march, and is refusing to — is never interned. The warning he gets is byte-identical every single turn, fourteen times running:
  "Ney is no nearer home - 5 march(es) still to go from Moravia, and 2 turn(s) of safe passage left before his corps is interned."
The 2 never becomes 1.

Second arm, flip-attributed on the lever itself (`withdrawal.A_STANDING_QUESTION_IS_NOT_LOITERING` set in the child process, no file edit), over 12 REAL `POST /command {"command":"end turn"}` calls through TestClient:
  lever True : t=2..13, grants 10 -> 21, `has_evacuation_grant(France,Austria)` = True at t=13
  lever False: t=2..8, grants held at 9, corridor CLOSED at t=9, `has_evacuation_grant` = False
The lever is the sole cause.

Reachability is not exotic and does not need a player to be devious. In that same unattended 12-turn run, Bernadotte picked up an ORGANIC `cannon_fire` interrupt at t=4 and carried it for the remaining 9 turns, holding the corridor open by himself after Davout had been captured. And `muster_is_live` returns `(True, "")` unconditionally for a REGION target (a garrison assault), so such a question never retires and the player can simply never answer it while ending turns normally — measured: all 12 end turns returned HTTP 200 with `pending=muster_confirm` throughout.

Consequences measured: (a) `evacuation_grants` is serialized and its int grows without bound; (b) `has_evacuation_grant` gates the `can_enter_territory` transit arm (`diplomacy.py::can_enter_territory`), so a stranded corps keeps permanent right of transit through the ex-enemy; (c) internment — the entire WIN-D3 §6 consequence — becomes unreachable for the nation.

**Repro**

Snapshot tree. Build `WorldState.from_scenario(europe_1805.json)`; move Davout and Ney to Moravia with `strategic_order = None`; `set_diplomatic_state(w, 'France', 'Austria', 'PEACE')`; clear both orders again; set `davout.pending_interrupt = {'interrupt_type': 'cannon_fire', 'marshal': 'Davout'}`; loop `w.current_turn += 1; withdrawal.process_evacuation_grants(w)` 14 times and print `w.evacuation_grants` and whether Ney is still in `w.marshals`. Probe file: scratchpad/probe/p8_everybody.py. The end-turn arm is scratchpad/probe/p4_who.py.

**Fix**

The rider's intent is right (a corps frozen on a question must not be interned for the game's own silence) but it is applied at the wrong scope and with no ceiling. Two changes: (1) make the grace MARSHAL-scoped, not nation-scoped — skip the warn/intern for the immobile marshal only, and do NOT add his nation to `grace_nations`, so a corps that CAN march still runs out of road; (2) bound the refresh — either cap total grace turns per grant (`grants[key] = min(grants[key] + 1, current + EVACUATION_MAX_TURNS)` is what was written and removed; the honest alternative is a separate serialized `grace_spent` counter so a legitimately long corridor is not shortened), or refresh only while the question is younger than N turns. Either way, `test_the_grant_window_does_not_widen_under_grace` asks the wrong question and must be joined by a pin that asserts the corridor EVENTUALLY CLOSES and that `has_evacuation_grant` eventually goes False.

### [P2] The new mid-treaty beat has no side filter and no fog check — the player is told, in Berthier's voice, where an unseen ENEMY corps stands and where it is marching

- **inside the slice:** True
- **seam:** backend/game_logic/withdrawal.py::_offer_event (and its consumers backend/campaign_log.py::format_event_oneliner and backend/game_logic/dispatch.py::_build_headline)

**Measured**

Unforced reproduction of FA-N61's own stated cause, mirrored onto the counterparty. Snapshot tree, 1805 board, France is the player. A French corps at Moravia gives the corridor a reason to exist; ArchdukeJohn sits at Tyrol on Austrian home soil with NO order and `road_home_offered` False (nothing about the flag is touched). The ground under him then changes hands to a power Austria is at peace with — exactly "the counterpart's OTHER wars capturing the ground under him" from the row.

  John stranded: True
  John visible to France: False

One tick of `process_evacuation_grants`, nothing forced:

  EVENT nation_a=Austria nation_b=France marshals=['ArchdukeJohn']

FRENCH CAMPAIGN LOG (via `filter_campaign_log`):
  * "ArchdukeJohn put on the road home from Tyrol to Bohemia under the peace with France - 7 turns"

FRENCH MORNING DISPATCH sub-beat (weight 69, above `region_taken`):
  "Sire - under the peace with Austria. ArchdukeJohn is on the wrong side of the frontier at Tyrol, Sire - the ground changed hands under him. Berthier has put him on the road home to Bohemia; he has 7 turn(s) of safe passage."

Four defects in one sentence, all measured:
 1. FOG. France is handed an unseen enemy corps' exact province AND its destination. The campaign-log fog rule for `evacuation_granted` is `player_nation in (nation_a, nation_b)`, and its own comment says the beat "names corps and the provinces they are marching to, so it is army intelligence wearing a treaty's clothes" — that rule was written for a beat both signatories already know (the treaty they signed), not for per-corps intelligence published every turn.
 2. WRONG VOICE. Berthier is France's chief of staff; he did not order an Austrian marshal anywhere.
 3. WRONG MIRROR. France's own log reads "under the peace with France".
 4. RAW KEY. `ArchdukeJohn` reaches the player un-humanised — the NPC-1/NPC-12 class.

The peace-turn producer it sits beside does NOT have this defect, and its docstring says exactly why: `_grant_message` filters to `side = player if player in pair`, because "an early draft counted every stranded marshal on both sides and announced '3 corps' while naming one, because the other two were Russian." The slice re-created that defect one layer over, per-marshal and with the province named. I confirmed by reading the diff that `_offer_event` is the only new `evacuation_granted` producer and it carries no side filter of any kind.

**Repro**

Snapshot tree. Build the 1805 world; `dav = w.get_marshal('Davout'); dav.location = 'Moravia'; dav.strategic_order = None`; `set_diplomatic_state(w, 'France', 'Austria', 'PEACE')`; then `w.regions['Tyrol'].controller = 'Ottoman'` (a power Austria is at PEACE with, so the soil turns impassable) and invalidate the caches; `w.current_turn += 1; withdrawal.process_evacuation_grants(w)`. Print `filter_campaign_log(new_events, w)` through `format_event_oneliner`, and `dispatch._build_headline(w, 'France')`. Probe file: scratchpad/probe/p6_unforced.py.

**Fix**

Two separate gates, because they answer different questions. (a) VOICE/SIDE: only emit `_offer_event` for the player's own nation, or give it a side-aware message the way `_grant_message` does — a counterparty top-up is either silent or reported as observed movement, never as an order Berthier gave. (b) FOG: if a counterparty beat is kept at all, gate its `region`/`destinations` on the player's visibility of that province the way every other enemy-movement surface does, and run the name through `display_names.humanize_entity_name`. Pin it with the mirror case (an Austrian corps topped up while France is the player) — nothing in the slice's 39 pins drives the counterparty side of `offer_road_home` at all.

### [P3] The README rewrite advertises Alt+Tab, which the Windows window manager eats — the row's own class of defect, freshly shipped

- **inside the slice:** True
- **seam:** deploy/README_TESTER.txt (HOTKEYS block) / godot-client/project-sovereign/scripts/main.gd::_alt_game_key KEY_TAB arm

**Measured**

Landed README_TESTER.txt reads `Tab       - Collapse/restore the terminal (Alt+Tab while typing)`. FA-N56's stated defect was that "the README named 'Alt' ZERO times, so even the six keys PC15-18 fixed were advertised in their dead form"; the rewrite fixes five of the six and gives Tab a form that is dead on the only platform the build ships for. `_alt_game_key`'s KEY_TAB arm is therefore unreachable in the shipping build. I did not drive the client to confirm the OS interception (I have no interactive Godot session), so this is read-from-code plus platform behaviour, not a keystroke measurement.

NOTE: the live working tree already carries an in-flight fix (`KEY_TAB, KEY_QUOTELEFT` with a comment saying Alt+Tab never reaches the game), so another lens or the builder has this. Reported for completeness against the landed SHA, and because the README half of the fix must move with it — the working-tree diff I read changes main.gd and README_TESTER.txt together, so it appears to be in hand.

**Repro**

Read the HOTKEYS block of deploy/README_TESTER.txt at 43691f14; press Alt+Tab in the exported build on Windows.

**Fix**

Already being taken in the working tree: bind a second, reachable key (Alt+` / KEY_QUOTELEFT) and advertise THAT in the README. Add the Tab row to `test_prebuild_fixes_2026_08_14.py::test_hotkeys_match_main_gd`, which currently pins R/D/N in their Alt form and says nothing about Tab — which is why this shipped.

### [P4] `e.get('marshals', [''])[0]` in the new dispatch identity is the documented `.get`-default footgun, one refactor from a 500

- **inside the slice:** True
- **seam:** backend/game_logic/dispatch.py::_build_headline

**Measured**

`dispatch.py::_build_headline`: `_identity = (f"road_home:{e.get('marshals', [''])[0]}" if e.get("mid_treaty") else ...)`. `.get(key, default)` returns the default only for a MISSING key, never for a present-but-empty list — CLAUDE.md's own Don't-Do row and the exact trap TUT-F1/TUT-F3 were landed for. Unreachable TODAY: the ternary evaluates the condition first, `mid_treaty` is set only by `_offer_event`, and `_offer_event` always writes a one-element `marshals` list. So this is a latent IndexError, not a live one — I confirmed by reading every producer of `mid_treaty` in the tree (there is one).

**Repro**

Log an `{"type": "evacuation_granted", "mid_treaty": True, "marshals": []}` event and call `_build_headline` -> IndexError.

**Fix**

`(e.get('marshals') or [''])[0]`.

### [P4] The treaty's order now prints `issued turn None` in the strategic debug line, and the in-game credits promise a `licenses\` folder that does not exist in a source checkout

- **inside the slice:** True
- **seam:** backend/commands/strategic.py::StrategicOrderProcessor.process_strategic_orders (debug print) / godot-client/project-sovereign/scripts/settings_panel.gd::_build_credits_section

**Measured**

Two cosmetic residues, both read from code, neither driven.
(a) `strategic.py` prints `f"(issued turn {getattr(order, 'issued_turn', '?')})"` — with the stamp removed this reads `issued turn None` rather than the `?` the fallback was written for. Dev console only; the two real readers are safe: `strategic.py`'s timed-HOLD expiry uses `order.issued_turn or order.started_turn` (and the road-home order is a MOVE_TO with no condition), and `strategic_executor`'s `is_first_step` reads `started_turn`, which the slice still stamps. I verified by grep that these are the only three readers in backend/ plus the serializer.
(b) `settings_panel.gd` credits now read "THIRD_PARTY_LICENSES.md, beside the game, with the per-family notices in licenses\." — true for the exported zip after the build.bat change, false in a source checkout, where the same panel is what a developer sees. `Utils.launch_hint()` already establishes the two-arm idiom for exactly this.

**Repro**

(a) Sign a peace that strands a corps and read the `[STRATEGIC]` console line on the next end turn. (b) Open Settings from the editor build and read the credits line.

**Fix**

(a) `getattr(order, 'issued_turn', None) or 'the treaty'` — or leave it; it is a print. (b) Branch the tail on `OS.has_feature("editor")` the way `launch_hint()` does.

## Record corrections

- THE HEADLINE CORRECTION. The FA-33 rider's comment in `withdrawal.py::process_evacuation_grants` says the unbounded grace is "bounded in the only sense that matters: `expiry - current_turn` is CONSTANT under grace (both sides gain one), so the window never widens". That measures the offset and not the thing that matters. Measured on the landed tree: the window indeed never widens — and it never NARROWS, so the corridor never closes, `has_evacuation_grant` stays True indefinitely (grant int 9 -> 23 over 14 turns, 9 -> 21 over 12 real end turns), and internment becomes unreachable for every stranded corps of BOTH signatories, not just the frozen one. The commit's own pin, `test_the_grant_window_does_not_widen_under_grace`, asserts exactly the offset the comment measures and never asks whether the corridor expires — which is why this shipped.

- The commit message says "A clamp to EVACUATION_MAX_TURNS was written and REMOVED after measurement - it shortens a legitimately long corridor by three turns." The clamp being wrong does not make an UNBOUNDED refresh right; the measurement disposed of one candidate fix and was recorded as if it had disposed of the problem. The corridor needs a ceiling that is not the march length — a spent-grace counter, or a marshal-scoped exemption that does not refresh the grant at all.

- `test_an_unanswered_ask_never_costs_the_army` runs nine end turns and asserts Davout is still in `world.marshals`. It does not assert that the corridor is still bounded, and on the shipped code it is a demonstration of the defect rather than a pin against it: the same nine turns make every OTHER stranded French corps immortal too, which the pin's fixture (one marshal) cannot see.

- The FA-N61 rider says "Three renderers were wrong for it and are fixed". A fourth thing is wrong for it and was not fixed: the PRODUCER has no side filter. The peace-turn producer it sits beside carries a docstring paragraph explaining that the beat must be told from the player's side of the table, because an early draft "counted every stranded marshal on both sides and announced '3 corps' while naming one, because the other two were Russian". `_offer_event` reproduces that defect per-marshal, with the province and the destination named, and with no fog check — measured reaching France's campaign log and dispatch about an Austrian corps France cannot see.

- `main.gd::_map_keys_live()`'s docstring says its gate is "the same one their unfocused twin obeys (`_unhandled_input` returns above them when a screen is open)". main.gd's `_unhandled_input` never handles the map keys at all — they live in `map_renderer_base.gd::_unhandled_input`, whose gate is `text_focused or not panning_enabled`, and main.gd's `if _is_screen_open(): return` does not call `set_input_as_handled()`, so it stops nothing. The BEHAVIOUR happens to agree, but only because `_on_screen_changed` sets `panning_enabled = false`. The stated mechanism is wrong and the next person to read it will believe a guard exists where it does not.

- The commit reports an instrumented 40-turn replica with "zero standing-question graces". That is a fact about that board, not about the mechanism: on the very first unattended 12-turn run I drove (France/Austria peace at t1 with a corps at Moravia), Bernadotte acquired an ORGANIC `cannon_fire` interrupt at t=4 and carried it for the remaining nine turns, holding the corridor open on his own after the marshal I had planted the question on was captured. The grace-holder need not be a player refusing to answer.

## Unverified

"WHAT I COULD NOT OR DID NOT VERIFY.\n\n1. The live working tree is being edited underneath this review. `git status` during my run went from three modified files to five, and `backend/game_logic/withdrawal.py` was mid-edit and BROKEN at one point (`NameError: name '_nation_has_standing_grant' is not defined` from `open_evacuation_corridor`, raised on a real `set_diplomatic_state` call). Every measurement above was therefore re-run against the committed snapshot of 43691f14, asserted at import time by a guard in my bootstrap. I did not review the in-flight edits, and R1-F3's Alt+Tab fix is already among them.\n\n2. I did not run the full suite and did not run the mutation sweep (instructed not to). I ran no test files at all — my evidence is probes against production code, not pin verification.\n\n3. The Godot parse harness DOES pass on the landed tree: EXIT=0, 0 SCRIPT ERROR, 47 scripts / 7 scenes, zero errors, all six changed scripts covered (main.gd, utils.gd, main_menu.gd, menu_boot.gd, settings_panel.gd, map_renderer_base.gd), and main.tscn instantiates. I ran it against the snapshot after copying in the repo's `global_script_class_cache.cfg` — the snapshot is a `git archive`, so `assets/` (gitignored) is absent and my first run produced 2,782 spurious SCRIPT ERRORs from the missing class cache, not from the slice. I did NOT do an interactive boot smoke or press any key: every slice-13 keyboard claim below is read-from-code.\n\n4. Slice 13 attacks that came back CLEAN and are recorded as refutations, not findings: the pause menu IS covered by `_alt_game_key`'s gates (`pause_menu` is registered modal, so `_is_modal_dialog_open()` returns true); `map_area` is null-guarded in `_map_keys_live()` and the KEY_E arm is protected by `end_turn_button.disabled`, which `set_input_enabled(false)` sets, so Alt+E cannot re-enter a request in flight; neither `europe_map.gd`, `map.gd` nor `europe_map_smoke.gd` overrides `_center_view_on_map`, `_zoom_at_point` or `cycle_map_fill_mode`, so the two new public doors dispatch correctly in every subclass; `zoom_step` computes the same `global_position + size / 2.0` centre the bare-key arm uses; and the tutorial overlay is registered NON-modal, so Alt+E behaves exactly as bare E does there (parity, not a hole).\n\n5. Slice 12 attacks that came back CLEAN: a marshal on the soil of a nation we are STILL AT WAR with is not swept up by the per-turn top-up (`is_stranded` is False because at-war soil is passable — measured, `is_stranded(Davout in Berlin) = False`), so the top-up does not commandeer a corps mid-offensive; `_nearest_home_region` did NOT churn along the road on the geometry I measured (Moravia -> Vienna -> Bohemia -> Franconia -> Swabia -> Franche-Comte, destination stable at Franche-Comte on all five steps, zero re-issues, zero duplicate beats) — a fork geometry could still flip it and I did not search for one; the three `record_vassal_break` exits are mutually exclusive (`continue`) so the soft-exit notification cannot double-fire, and `NotificationCollector._identity` keys on (type, title, subject) so two different satellites breaking in one turn produce two rows; `_warn` and `_offer_event` both `world.log_event` consistently; and `road_home_offered` round-trips through `to_dict`/`from_dict` with a `.get(..., False)` default.\n\n6. I did NOT verify whether the July-19 exact-repeat headline demotion catches the frozen `passage_lapsing` lead. `passage_lapsing` (weight 74) is not in `STANDING_HEADLINE_CLASSES`, and under R1-F1 its sentence is byte-identical every turn, so it may or may not be demoted — if it is not, the morning dispatch leads with the same false deadline indefinitely, which is verbatim the PC-7 / CA8-9 defect class. Worth one measurement before the fix lands.\n\n7. R1-F1's exploitability by a deliberate player rests on `muster_is_live` returning `(True, \"\")` unconditionally for a REGION target, which I read rather than reached through play; the twelve real end turns I drove used a hand-planted region-target muster. The UNATTENDED reachability (Bernadotte's organic `cannon_fire`) needed no planting and is measured."
