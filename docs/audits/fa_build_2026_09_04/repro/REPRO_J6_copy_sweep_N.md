# REPRO J6 - slice 16 FA-N copy/small-mechanism family (24 rows)

Repo at master `a1ed5c9d`. Read-only. All probes under
`<scratchpad>/repro/j6/`. Every verdict below is backed by a quoted probe
line or a quoted source line at TODAY's line numbers.

## Summary

| Row | Verdict | Measured mechanism |
|---|---|---|
| FA-N27 | REPRODUCED | `fmt["turns"] = _run` is the display run; measured turn 16 headline says "gone unrewarded 3 turns" for a 16-turn arrears |
| FA-N28 | REPRODUCED | order-free `last_stand` -> `('awaiting', 'Awaiting orders.')`; the pending-decision arm is nested under `in_strategic_mode` |
| FA-N29 | REPRODUCED | roster carries `Ney: awaiting_decision` and `berthier_note` is still "Your armies stand ready, Sire. The initiative is ours." |
| FA-N30 | REPRODUCED | `_format_dispatch_event_text` returns `'Diplomatic event: settlement_offer_arrival'`; producer's bare dict has no `fog_rule`, so it defaults to `always` |
| FA-N31 | REPRODUCED | Austria's vassal rebels -> CRITICAL `vassal_rebellion` notification on the FRENCH rail; four siblings in the same file are lord-guarded |
| FA-N32 | NARROWED | the unclamped expression is real (`800 -> 1000`, +200) but the branch was NOT reachable in 62 staged charges: the loser is annihilated to 0 first and the block is gated on `enemy.strength > 0` |
| FA-N36 | REPRODUCED | ledger row `{'status': 'moving_to', 'strategic_order': 'March Swabia (1 turns left)'}` for the same marshal the dispatch calls `awaiting_decision` |
| FA-N47 | REPRODUCED (2 of 3 arms measured) | refused march: square destroyed, message is only "Region 'Moscow' not found."; successful SUPPORT: square destroyed, notice eaten by the nested `execute()` |
| FA-N50 | REPRODUCED verbatim | `[Square broken - Soult breaks formation to MOVE TO]` |
| FA-N52 | REPRODUCED, one claim CORRECTED | 6 collector keys are outside `CAMPAIGN_LOG_TYPES`; but 3 of them DO have producers (dispatch/payload events), so the row's "no producer of any kind" is wrong for `glory_crown_lost` |
| FA-N53 | REPRODUCED | option + confirm say "3 turns"; `build_unmet_marshals` says 7 and erosion actually resumes 7 turns later |
| FA-N55 | REPRODUCED | 3 backend producers emit int percent; `enemy_phase_dialog.gd` re-multiplies by 100 at 4 reads, `main.gd` does not |
| FA-N57 | REPRODUCED | square advisory never fires (`_auto_break_square` at :525 clears the flag ~1,140 lines before the `elif` at :1667); the `fortified` sibling fires |
| FA-N58 | REPRODUCED | `retreat_recovered` is produced and `_build_turn_events` returns `[]`; the `>= 3` severity arm is dead by the producer's own `new_stage < 3` guard |
| FA-N64 | REPRODUCED (both halves) | `record_override(..., "override")` -> `get_override_dispatch_note` is `None`; substituting `"good"` returns the line. `talleyrand_override_note` is read by 0 .gd |
| FA-N65 | REPRODUCED | prisoner row `{'location': 'Vienna', 'strength': 0, 'morale': 100, 'status': 'idle'}` and an ORDERS row "No active orders" |
| FA-N66 | REPRODUCED | only own-soil carve-out is `captured_from == player_nation`; both `occupation_started` producers carry no ownership key and one is in `_execute_attack`, outside FA-23's stated seam |
| FA-N69 | REPRODUCED | key-parity scan: `talleyrand_report` and `coalition_status` in main.gd, absent from dispatch_view.gd |
| FA-N70 | REPRODUCED verbatim | "Strategic order (MOVE_TO) cancelled." / "(HOLD)" / "(SUPPORT)" |
| FA-N71 | REPRODUCED | `war_objectives` = 0 hits across all .gd |
| FA-N81 | REPRODUCED | `_mission_action` reads `tal_state`; `_proposal_action` and the inline declare_war / send_ultimatum / break_treaty / downgrade rows never do, while the executor refuses them all |
| FA-N82 | REPRODUCED with A/B | ships 45 -> camp_turns 4, staged, Britain guards, blockade lifted. ships 0 -> camp_turns 0, not staged, Britain blockades, France blockaded |
| FA-N83 | REPRODUCED | France at war only with Austria: `diversion_used` still True after 3 ticks, while the report's own term 2 reads "at war with a naval power: False" |
| FA-N85 | REPRODUCED | boot `coalition_count == 1` under `name == 'Third Coalition'`; next formation names itself "The Second Austria Coalition" |

No row in this family is a DUPLICATE of another in the list, but three
PAIRS must land together (see Cross-row findings): N28+N29+N36,
N47+N50+N57+N70, N64+N69+N71.

---

## Per row, grouped by FILE

### GROUP 1 - `backend/game_logic/dispatch.py` (N27, N28, N29, N30, N58; renderer riders N69, N71)

#### FA-N27 - `estate_eroding` {turns} is the display run, not the arrears age
Probes: `probe_estate.py`, `probe_estate3.py`, `probe_estate4.py`.

Evidence (probe_estate3.py, one eroding marshal, `expectation_grace_turn = 0`):
```
turn  6 age= 6 run=3 lead_class='estate_eroding'
    HEADLINE: 'Sire - Marshal Ney has now gone unrewarded 3 turns. ...'
turn 12 age=12 run=9
    HEADLINE: "Sire - Marshal Ney's grievance is 9 turns old ..."
```
Arm (b) is worse and reproduces exactly as filed (probe_estate4.py, two
eroding marshals, the first settled with a pension at turn 14):
```
turn 16: runs={'estate_eroding:Davout': 3}   Davout true age = 16
    HEADLINE: 'Sire - Marshal Davout has now gone unrewarded 3 turns. ...'
```
The constant offset is `run = age - GRACE_TURNS + 1` because `is_eroding`
(dotation.py:305) requires `(current_turn - grace) >= GRACE_TURNS` (=4)
before the candidate can first appear, so the copy under-reports by 3 in
the single-marshal case and by an unbounded amount in the two-marshal
case.

(a) True seam BY SYMBOL: producer `dispatch._build_headline`'s ES-7 block
(the `_add("estate_eroding", identity=..., marshal=m.name)` call, which is
followed by `break` - **at most one estate_eroding candidate exists per
turn**, which is what starves the second marshal's run); consumer is the
`_STANDING_ESCALATION` block that sets `fmt["turns"] = _run`. The truth is
`Marshal.expectation_grace_turn`, already serialized.

(b) What the filed fix would break: nothing - and it is correct that
`fmt["turns"] = _run` must NOT be changed to prefer a producer field,
because `enemy_on_our_soil`'s three variants in the same dict genuinely
mean "turns reported". But the fix as filed is incomplete: with two
eroding marshals only ONE is ever a candidate, so an `{age}` field fixes
the number while the SECOND man stays invisible until the first is
settled. State that as a known limit or drop the `break`.

(c) Minimal correct fix: pass `age=max(0, world.current_turn - int(getattr(m,
'expectation_grace_turn', world.current_turn)))` as a producer field and
interpolate `{age}` in the three `estate_eroding` variants only.

(d) Pins that would flip: none found. `_STANDING_ESCALATION` has no
direct test; grep for `"unrewarded"` / `"without settlement"` /
`"grievance is"` in `tests/` returns nothing.

#### FA-N28 - an order-free pending decision reports "Awaiting orders."
Probe: `probe_dispatch.py` section A.
```
A1 order-free last_stand -> ('awaiting', 'Awaiting orders.')
A2 order + contact_bad_odds -> ('awaiting_decision', 'HALTED at Swabia - Mack bars the way. Awaiting your word.')
```
(a) Seam: `dispatch._derive_marshal_status` - the `_pending =
getattr(marshal, "pending_interrupt", None)` block is inside `if
marshal.in_strategic_mode:` and `Marshal.in_strategic_mode` is literally
`self.strategic_order is not None` (marshal.py:892-894).
`strategic.STANDALONE_DECISION_TYPES = {"last_stand", "muster_confirm"}`
is the complement set that never has an order.

(b) What the filed fix would break: the hoist itself is safe. **But the
row's "read by no .gd" is a NARROWING, not a fact:** `awaiting_decision`
is not a *key* in any .gd, yet the status IS consumed - it falls through
the `match m_status:` blocks in `main.gd:3487-3505` and
`dispatch_view.gd:188-205` to `_: icon = "-"`, i.e. it silently renders
the same glyph as "awaiting". The NOTE ("HALTED at ... Awaiting your
word.") already renders correctly. So the backend hoist alone is a real
fix; the glyph half is cosmetic.

(c) Minimal correct fix: hoist the pending-decision block out of the
`in_strategic_mode` branch (above it, below broken/retreating). Prefer
`strategic.standalone_decision(marshal)` / the raw `pending_interrupt`
depending on whether an order-bound interrupt with no order is possible.

(d) Pins: `tests/test_creative_audit_2026_07_19.py::test_marshal_with_pending_interrupt_is_not_reported_as_marching`
- `assert status == "awaiting_decision", status` - uses a `_FakeMarshal`
with `in_strategic_mode = True` hard-set, so it stays GREEN under the
hoist. Its sibling `::test_marshal_without_interrupt_still_reports_its_order`
(`assert status == "en_route"`) is the falsifiable control and also stays
green. **No flip.**

*.gd flag:* only if the optional glyph arm is added (main.gd AND
dispatch_view.gd -> Godot parse harness + boot smoke).

#### FA-N29 - "Your armies stand ready" over a halted marshal
Probe: `probe_dispatch.py` section A.
```
A3 roster statuses: {..., 'Ney': 'awaiting_decision', ...}
A4 berthier_note: 'Your armies stand ready, Sire. The initiative is ours.'
```
(a) Seam: `dispatch.py:3158` `non_ready_statuses = {"broken",
"retreating", "drilling", "idle_restless"}` inside the berthier-note
ladder.

(b) Filed fix breaks nothing - it is the same one-word extension CA8-8
made for `idle_restless`.

(c) Minimal correct fix: add `"awaiting_decision"` to the set. **Also add
`"arrived"`?** No - `arrived` is a legitimately ready state; leave it.

(d) Pins: `tests/test_creative_audit_ca8_2026_08_04.py::test_an_idle_army_is_never_called_ready`
- `assert "stand ready" not in note.lower(), note` - pins the same
direction, stays green. **No flip.**

#### FA-N30 - three event types print their raw internal key
Probe: `probe_dispatch.py` section C.
```
settlement_offer_arrival -> 'Diplomatic event: settlement_offer_arrival'
hegemony_relaxation_aside -> 'Diplomatic event: hegemony_relaxation_aside'
diplomatic_mission_blowback -> 'Diplomatic event: diplomatic_mission_blowback'
```
Reachability is structural, not lucky: `_is_dispatch_event_visible`
(dispatch.py:4190) does `fog_rule = event.get("fog_rule", "always")` and
returns True for `"always"`, and `turn_manager.py:631` appends a bare dict
with no `fog_rule`. So the line is shown whenever the producer fires. I
confirmed `settlement_offer_arrival` is NOT in
`settlement_presentation.SETTLEMENT_ROUTES` (only `settlement_summary` and
`settlement_digest` are), so it cannot escape through the settlement arm.

(a) Seam: fallback `return f"Diplomatic event: {event_type}"` in
`dispatch._format_dispatch_event_text` (dispatch.py:4315); producers
`turn_manager.py:631`, `coalition.py:634`, `diplomacy.py:10135/10142`.

(b) Filed fix ("return '' and drop empty rows in
`_build_diplomatic_events_section`") would silence a future producer
rather than leak - which is what the row wants - but it also removes the
only signal a developer gets. Recommend the drop PLUS the AST census the
row's own test proposes, in the same slice, or the class goes quiet
instead of getting fixed.

(c) Minimal correct fix: three real templates in
`_DIPLOMATIC_EVENT_TEMPLATES` + route `settlement_offer_arrival` through
`queue_dispatch_event` (its `message` is already composed at
turn_manager.py:596-599), and change the fallback to `''` + drop.

(d) Pins: none. `grep -rn "Diplomatic event:" tests/` = 0 hits.

#### FA-N58 - `retreat_recovered` dropped at the whitelist
Probe: `probe_dispatch.py` section B.
```
B1 raw tactical events: [('retreat_recovered', None)]
B2 built turn events: []
B3 'retreat_recovered' in _DISPATCH_EVENT_TYPES: False | broken_recovered: True
```
The producer's own guard (`world_state.py:11762 if new_stage < 3:`) makes
`dispatch.py:2856`'s `severity = "good" if int(event.get("stage", 0)) >= 3
else "info"` unreachable, and the comment above it asserts the invariant
PC15-14 broke.

(a) Seam: `dispatch._DISPATCH_EVENT_TYPES` (the set at dispatch.py:2718)
and the severity ladder in `_build_turn_events`.

(b) Filed fix breaks nothing.

(c) Minimal correct fix: add `"retreat_recovered"` beside
`"broken_recovered"` in the whitelist and in the `good` severity tuple;
delete the dead `>= 3` arm.

(d) Pins: none found for `retreat_recovered` in `tests/*.py` (only
fixture JSON hits for the `retreat_recovery` FIELD, which is unrelated).

#### FA-N69 / FA-N71 - dispatch keys no renderer reads
Probe: `probe_gd_parity.py` (a full top-level key parity scan over the
1805 boot payload).
```
key                               main.gd  view.gd
  coalition_status                   True    False   <<< DIVERGES
  talleyrand_report                  True    False   <<< DIVERGES
  talleyrand_discovery              False    False
  talleyrand_override_note          False    False
  war_objectives           in payload=False  main.gd=False  view.gd=False
```
**Correction to my own scan:** it also flagged `talleyrand_redemption` as
main.gd-only, but every main.gd hit is inside a PL-23 comment ("popup
removed"), so the real dispatch_view divergence is exactly the two keys
FA-N69 names. A substring scan over `.gd` hits comments - the builder's
parity pin must strip comments or it will be satisfied by a dead line.

(a) Seams: `dispatch_view.gd._on_dispatch_received` (missing
`talleyrand_report` / `coalition_status` blocks, FA-N69);
`main.gd._display_morning_dispatch` + `dispatch_view.gd` (missing
`war_objectives`, FA-N71).

(b) FA-N71's fix is "correct and unobservable" by the row's own
admission - the key is written only `if war_objective_lines:`
(dispatch.py:2137-2139) and the boot payload does not carry it. Land it
with FA-D4 or it renders nothing.

(c) Minimal correct fix: FA-N69 = two blocks copied from
`main.gd:3680-3706` into `dispatch_view.gd`, zero backend change.
FA-N71 = one block in each renderer.

(d) Pins: the paired-file idiom already exists -
`tests/test_pt_c_numbers_on_buttons.py::test_both_client_surfaces_render_the_label`
(`for name in ("main.gd", "dispatch_view.gd"): ... assert
'situation.get("treasury_delta_label"' in src`). Nothing flips.

*.gd flag:* BOTH rows touch `.gd` (dispatch_view.gd; N71 also main.gd) ->
Godot parse harness + boot smoke.

---

### GROUP 2 - `backend/game_logic/ledger.py` (N36, N65) - **land together**

Probe: `probe_dispatch.py` section A5/A6.
```
A5 ledger Ney row: {'name':'Ney','location':'Rhineland','status':'moving_to',
                    'strategic_order':'March Swabia (1 turns left)'}
A6 ledger prisoner FORCES row: {'name':'Davout', ..., 'location':'Vienna',
   'strength':0, 'morale':100, 'status':'idle', 'strategic_order':'None', ...}
A6 ledger prisoner ORDERS row: {..., 'order_type':'No active orders',
   'condition':'idle', 'has_order':False}
A6 _derive_status(prisoner) = idle
```
(a) Seam: `ledger._derive_status` (no `pending_interrupt` arm, no
`captured_by` arm; `grep -c captured_by backend/game_logic/ledger.py` =
0), `ledger._derive_strategic_order_summary`, `ledger._build_forces`
(nation-only filter), `ledger._build_orders` (nation-only filter).

(b) **What FA-N65's filed fix gets wrong:** it says the ORDERS row should
read "Prisoner of Austria" and that this needs "zero .gd change". The
FORCES half is right - `strategic_ledger.gd:267` renders
`status.replace("_", " ").capitalize()`, so returning `"prisoner"` prints
"Prisoner" with no client edit. But the ORDERS half is NOT renderable
from the payload: `strategic_ledger.gd:936` hard-codes the literal
`" | No active orders"` and never reads the payload's `order_type`. So
either the prisoner is EXCLUDED from `_build_orders` (backend-only, my
recommendation) or the fix touches `.gd`.

(c) Minimal correct fix, one edit serving both rows: give
`_derive_status` a two-arm head - `if getattr(marshal, 'captured_by',
''): return "prisoner"` then `if getattr(marshal, 'pending_interrupt',
None): return "awaiting_decision"` - above the `in_strategic_mode`
branch, and have `_build_orders` skip captured marshals. Do NOT "extract
the dispatch's own predicate" as FA-N36 proposes without reading FA-N65's
note first: the dispatch predicate is nested under `in_strategic_mode`
TODAY (that is FA-N28), so extracting it before FA-N28 lands copies the
bug into a second file.

(d) Pins: `tests/test_ledger.py::test_forces_status_idle_default`
(`assert d["status"] == "idle"`) - the fixture marshal has all flags off
and is not captured, so it stays green. **No flip found.**

---

### GROUP 3 - the square family: `tactical_executor.py`, `executor.py`, `strategic_executor.py`, `combat_executor.py` (N47, N50, N57, N70) - **land together**

Probe: `probe_square.py`, `probe_square2.py` (real `/command`, mock parser).

#### FA-N50 - raw order enum in the break line
```
march (after square): '\n[Square broken - Soult breaks formation to MOVE TO]\n
                       Soult begins march to Lorraine. ...'
```
(a) Seam: `tactical_executor._auto_break_square` line 496
`display = _action_display_name(action_name)`, called from
`strategic_executor.py:525` with `strategic_type or "strategic order"`.
`display_names.action_display_name` falls through to
`action.replace("_", " ")`; `ACTION_DISPLAY` has no `MOVE_TO` key (the
`"MOVE_TO": "March"` at display_names.py:241 is inside
`STRATEGIC_ORDER_DISPLAY`, a different dict, imported on the SAME line of
strategic_executor.py as `action_display_name`).

(b) Filed fix is right and correctly notes FA-93's fix alone leaves
"MOVE TO" standing.

(c) Minimal correct fix: in `_auto_break_square`, route a strategic order
type through `get_strategic_display` (lower-cased for the infinitive
frame), otherwise the existing map.

(d) Pins: none - `grep -rn "Square broken" tests/` = 0 hits.

#### FA-N57 - the square advisory is production-dead
```
support Ney (after square): square_formation now: False
      Berthier square advisory in msg: False
      fortified advisory fires: True
```
(a) Seam: `strategic_executor._execute_strategic_command` - the function
opens at :467, calls `_auto_break_square` at :525 (which sets
`square_formation = False`), and the advisory `elif getattr(marshal,
'square_formation', False):` is at **:1667** (the row's `:1562` is
stale), ~1,140 lines later inside the same call. `_execute_form_square`
is the only writer of True and is not on this path.

(b) Filed fix (capture `was_in_square` before :525) is correct, and its
note that the COPY must change too is correct - by the time it prints the
square is gone.

(c) Minimal correct fix: `was_in_square = getattr(marshal,
'square_formation', False)` immediately above :525; branch the `elif` on
the local; reword to the consequence.

(d) Pins: none.

#### FA-N47 - a refused order destroys the square and says nothing
Two of the row's three arms measured:
```
ARM 1 (refused march):
  pre: square_formation = True
  march to a bogus province: success=False
      msg="Region 'Moscow' not found. Did you mean 'Oslo'?"
  post: square_formation = False
  '[Square broken' in msg: False        events: []

ARM 2 (successful SUPPORT, nested execute):
  support Ney: success=True
      msg='Soult moves to support Ney (at Rhineland). Moves to Rhineland. ...'
      square_formation now: False       (no '[Square broken' anywhere)
```
Arm 1 fires because `movement_executor.py:368` calls
`_auto_break_square` as the FIRST statement, above the destination
validation. Arm 2 fires because the strategic route runs a nested
`execute()` for the first step, and `executor.py:991` clears
`self._pending_square_break_msg = ""` at the TOP of every `execute()`.

**A third arm the row lists did NOT reproduce:** `drill` while
`drilling_locked` kept the square (`post square_formation: True`). The
command is refused by an executor-level pre-block ("Soult is locked in
drill exercises and cannot receive orders.") before `_execute_drill` -
and therefore before `_auto_break_square` at tactical_executor.py:186 -
is reached. So the row's "every one of the 10 call sites fires before its
own validation" is true of the code POSITION but not of every refusal
path. (Census correction: there are **12** call sites today, not 10:
combat_executor x3, economy_executor x2, movement_executor x1,
strategic_executor x1, tactical_executor x3, plus the two in
`executor.py`'s delegate list.)

(a) Seams: `tactical_executor._auto_break_square` (parks the notice on
`self._executor._pending_square_break_msg`), `executor.execute` line 991
(clear) and line 2660 (emit, gated on `result.get("success")`).

(b) **What the filed fix would MISS - a real hazard.** The row says to
"make the clear at :905 re-entrancy-aware". Making only the CLEAR
depth-aware moves the bug rather than fixing it: with the clear skipped
on the nested call, the nested `execute()` reaches :2660 with the notice
set and its own successful move result, prepends the notice onto the
INNER message, and consumes it - and the strategic route discards that
inner message. **The EMIT at :2660 must be outermost-only too.** Both
edits, or arm 2 stays broken while looking fixed.

(c) Minimal correct fix: a depth counter around `execute()`; clear only
at depth 0 on entry; emit + consume only at depth 0 on exit; drop
`result.get("success")` from the emit condition. Optionally append a
`square_broken` event (there is no such event type anywhere in the
backend today).

(d) Pins: none.

#### FA-N70 - `form square` cancels a march and prints the raw enum
```
form square msg: 'Davout forms square at Lorraine! ... Strategic order (MOVE_TO) cancelled.'
'hold at Rhineland' -> cancel clause: 'Strategic order (HOLD) cancelled.'
'support Ney'       -> cancel clause: 'Strategic order (SUPPORT) cancelled.'
```
(a) Seam: `combat_executor._execute_form_square`, line **7644** (the
row's :7433 is stale): `strategic_cancel_msg = f" Strategic order
({old_order.command_type}) cancelled."` - the sole hit for
`"Strategic order ("` in the whole backend.

(b) The row names `strategic.py:2961` as a second site of the same class.
**That line does not exist today.** The nearest is `strategic.py:1872`
`f"Unknown strategic command: {order.command_type}"`, an unreachable
error path, not player copy. Do not chase it.

(c) Minimal correct fix: `from backend.display_names import
get_strategic_display` and emit `f" His
{get_strategic_display(old_order.command_type).lower()} order is
cancelled."`.

(d) Pins: none (`grep -rln "Strategic order (" tests/` returns only
`test_serialization.py`, an unrelated substring).

---

### GROUP 4 - `backend/game_logic/vassal.py` (N31)

Probe: `probe_misc.py`.
```
lord was: Austria | player: France
events: [(None,None), (None,None), ('vassal_rebellion','Austria')]
NOTIFICATION: vassal_rebellion 2 'Switzerland REBELLED!'
```
(a) Seam: `vassal.check_vassal_rebellion` - the
`world.notifications.add(_cr_notif(_VR_CONST, _NP.CRITICAL, ...))` block
at vassal.py:1015-1021, with no lord test in scope. Siblings at
vassal.py:734 and :741 both carry `if lord == getattr(world,
'player_nation', 'France'):`.

(b) Filed fix is correct and minimal; it explicitly and rightly leaves
the `events.append` and `queue_dispatch_event` alone.

(c) Minimal correct fix: wrap the notification block in the sibling
guard.

(d) Pins: none. `VASSAL_REBELLION` hits in `tests/test_audit_part2.py` are
priority-ordering imports, not behaviour on this seam.

**Bonus defect found in passing (NOT filed anywhere I can see):** the
notification and the `events.append({"type": "vassal_rebellion", ...
"War declared."})` sit at 8-space indent, i.e. OUTSIDE the
`if current_state == "ARMISTICE": ... else:` split at vassal.py:888/896.
So a vassal breaking free under a respected armistice emits BOTH
`vassal_rebellion_armistice` ("the armistice holds - no war declared")
AND `vassal_rebellion` ("War declared."), plus a CRITICAL alert saying
"War declared." The armistice branch's own event is contradicted three
lines later. Worth folding into FA-N31's slice - it is the same block.

---

### GROUP 5 - `backend/models/world_state.py` (N32)

Probes: `probe_rout.py`, `probe_rout2.py`, `probe_rout3.py`.

**NARROWED.** The code defect is real and exactly as described:
```
old=800 rate=0.05  world_state=1000  combat_executor=800   NET GAIN: +200
```
`world_state.py:12494` and `:12536` read `max(1000, int(x *
survival_rate))`; the maintained sibling `combat_executor.py:3735` reads
`min(old_strength, max(1000, int(old_strength * survival_rate)))` with a
comment naming this exact case. Neither auto-charge arm has the clamp.

**But the branch was not reachable in 62 staged charges.** The block is
gated on `combat_result["defender"]["forced_retreat"] and enemy.strength
> 0` and, at every disparity I could stage that produces a rout, the
loser is annihilated to 0 first:
```
  atk=26000 dfn=4200: strength=0 broken=True captured_by='' loc=Swabia
  atk=3000  dfn=1200: strength=0 broken=True captured_by='' loc=Swabia
  (ATTACKER arm) the shatter arm was not reached in 36 staged charges
```
For the divergence to bite, the loser must END the battle at 1..999 men
AND have no safe retreat AND still be flagged `forced_retreat`. I could
not produce that state. There IS no minimum-strength gate on the defender
in `_process_reckless_cavalry_turn_start` (the guards at :12283-12292 are
all on the CHARGER), so I cannot prove it unreachable either.

(a) Seam: `WorldState._process_reckless_cavalry_turn_start`, the two
"Surrounded - broken army" arms.

(b) Filed fix (extract a shared `combat.rout_survivors` helper and call it
from all three sites) is correct and safe, and it is the right shape
BECAUSE the branch is rare - a shared helper costs nothing and cannot
regress the > 1000 case (`min(old, ...)` is a no-op there).

(c) Minimal correct fix: exactly the filed one.

(d) Pins: none - the row's suggested home
`tests/test_cavalry_recklessness.py` has no assertion on the shatter
arm today. **Warning for the builder: the row's own proposed test
("assert `defender.strength <= 800` over the seed range that reaches the
shatter arm") cannot be written as stated** - no seed in 0..19 reached the
arm on the shipped board at four different force ratios. Pin the pure
helper instead, or the test is vacuous by construction.

Re-priced: this is a P4 hygiene fix, not a P3 player-facing bug, until
someone shows the branch firing.

---

### GROUP 6 - `backend/game_logic/gazette.py` (N52)

Probe: `probe_gazette.py`.
```
collector keys: 30
NOT in CAMPAIGN_LOG_TYPES: ['coalition_formed', 'glory_crown_lost',
    'incoming_ultimatum', 'marshal_petition', 'vassal_created', 'vassal_rebellion']
dead keys with a literal 'type': producer anywhere in backend/:
    glory_crown_lost -> jealousy.py
    incoming_ultimatum -> ai_diplomacy.py
    vassal_rebellion -> vassal.py
  coalition_declared / coalition_dissolved / ultimatum_issued /
  ai_ultimatum_accepted / vassal_defected / vassal_transferred: all True
```
REPRODUCED on the join, **one claim CORRECTED**: the row says
`glory_crown_lost` and `marshal_petition` "have no producer of any kind"
and should therefore be DELETED. `glory_crown_lost` has a producer
(`jealousy.py:570`, a turn-event dict) and is in
`dispatch._DISPATCH_EVENT_TYPES` (dispatch.py:2764) with a `warning`
severity arm. `vassal_rebellion` and `incoming_ultimatum` likewise have
turn-event / payload producers. What is true of all six is narrower and
sharper: **they are never written to the CAMPAIGN LOG**, and
`compose_issue` filters only `filter_campaign_log(...)` output
(campaign_log.py:593 drops any type outside `CAMPAIGN_LOG_TYPES`).

(a) Seam: `gazette._WAR_TYPES` / `_COURT_TYPES` / `_ARMY_TYPES`
(gazette.py:31-47).

(b) What the filed fix would break: deleting `glory_crown_lost`
forecloses the better fix (the crown changing heads IS gazette-worthy and
already has a producer and a dispatch severity arm). Re-key the three
near-misses, and for `glory_crown_lost` / `marshal_petition` decide
consciously rather than deleting on a false premise.

(c) Minimal correct fix: `coalition_formed -> coalition_declared`;
`incoming_ultimatum -> ultimatum_issued` + `ai_ultimatum_accepted`;
`vassal_rebellion` / `vassal_created` -> `vassal_defected` /
`vassal_transferred`; then a structural pin that the three collector sets
are a SUBSET of `CAMPAIGN_LOG_TYPES`.

(d) Pins: none on the collectors. **Attribution flag:** if the builder
instead ADDS campaign-log types, `assert len(CAMPAIGN_LOG_TYPES) == 160`
is pinned in **nine** test files (test_bph_a_term_ownership.py:303,
test_ca9_row3_a7_jealousy_note.py:456, test_ca9_row3_phase_a.py:154,
test_ca9_row3_q2_council_command.py:433, test_campaign_log.py:138,
test_igr_a_honest_copy.py:197, test_igr_b_campaign_log_readable.py:546,
test_igr_f_envoy_digest.py:824, test_wo_slice4_the_capital_speaks.py:785).
The collector-set-only fix touches none of them.

---

### GROUP 7 - `backend/game_logic/jealousy.py` (N53)

Probe: `probe_estate2.py`.
```
GRACE_TURNS = 4 FONTAINEBLEAU_PROMISE_GRACE = 3
OPTION detail: 'Their patience extends 3 turns; the court hears you buy time with words (authority -2).'
CONFIRM message: '"The next conquest is yours." Their patience extends 3 turns - but the court heard you buy time with words.'
expectation_grace_turn now: 23 (current_turn 20)
build_unmet_marshals grace_turns_left: 7 eroding: False
erosion resumes at turn 27 => the promise bought 7 turns
```
Two surfaces contradict on the same turn: the modal says 3, the
Unmet-Marshals row (rendered by `dispatch_view.gd:166` as "patience holds
7 more turns") says 7, and 7 is the truth.

(a) Seam: `jealousy.py:118` `FONTAINEBLEAU_PROMISE_GRACE = 3`, read by
the option `detail` at :2236 and the confirmation at :2994-2995; the
mechanic is `marshal.expectation_grace_turn = current_turn +
FONTAINEBLEAU_PROMISE_GRACE` at :2991 inside
`_apply_fontainebleau_choice`; erosion fires at `current_turn - grace >=
dotation.GRACE_TURNS`.

(b) Filed fix is right to leave the MECHANIC alone. Changing :2991 would
red the mechanic pin (below) and move a balance number.

(c) Minimal correct fix: `FONTAINEBLEAU_PROMISE_WINDOW =
dotation.GRACE_TURNS + FONTAINEBLEAU_PROMISE_GRACE` and use it in the two
strings only.

(d) Pins: `tests/test_estate_riders_esp.py::TestFontainebleau::test_promise_extends_grace_and_dents_authority`
- `assert m.expectation_grace_turn == world.current_turn +
J.FONTAINEBLEAU_PROMISE_GRACE` - pins the MECHANIC, stays green under the
copy-only fix. **No flip.** (If anyone "fixes" the mechanic instead, this
is the pin that reds.)

---

### GROUP 8 - `godot-client/.../enemy_phase_dialog.gd` (N55)

Read-only source verification (no probe needed - it is a producer/consumer
type mismatch settled by reading both ends).

Producers, all int percent:
- `combat.py:1005-1006` and `:1090-1091` `"fortification_old": int(fortification_old * 100)`
- `combat_executor.py:4135-4136` (bombardment event) and `:4188-4189` (`bombardment_result`)

Consumers:
- `main.gd:3180-3181` `int(result.get("fort_old", 0))` - CORRECT
- `enemy_phase_dialog.gd:382,383,520,521` `int(event.get(..., 0) * 100)` - RE-SCALED

`defense_bonus` is a fraction (tactical_executor.py:402 sets 0.02 on the
first fortify), so `fort_old` arrives as 2..20 and prints as 200%..2000%.

(a) Seam: the four `.gd` reads. (b) Filed fix is right, and its "do NOT
instead divide in the backend" is load-bearing: `combat_executor.py:4159-4160`
passes the RAW FRACTION to `generate_bombardment_report`, so the two
shapes genuinely coexist by design and a backend change would break the
Berthier report. (c) Minimal correct fix: drop the four `* 100`.
(d) Pins: `tests/test_bombardment.py:140` `assert br["fort_old"] == 20  #
int percentage (P1-22 fix)` and `tests/test_final_audit_s1.py:191-194`
(FINAL-8 int enforcement) both pin the PRODUCER side and both confirm the
client is the wrong half. **No flip.**

*.gd flag:* touches `enemy_phase_dialog.gd` -> Godot parse harness + boot
smoke.

---

### GROUP 9 - `backend/main.py` fog (N66)

Read-only verification.
- `main.py:2091` `if evt.get("captured_from") == player_nation:` is the
  ONLY own-soil carve-out (`grep -n captured_from backend/main.py` = 1
  hit).
- `combat_executor.py:3073` (post-garrison) and `:5231` (inside
  `_execute_attack`, the unopposed march) both append
  `{"type": "occupation_started", "marshal", "region", "turns_required"}`
  with no ownership key.

(a) Seam: the carve-out in the enemy-phase visibility filter in
`backend/main.py`.
(b) The row is itself a CORRECTION to FA-23 and is right: FA-23's
"ONE producer seam: `_resolve_garrison_combat`" reaches only one of the
two producers. Do not stamp ownership producer-side.
(c) Minimal correct fix: a shared `_event_is_on_player_soil(evt, world,
player_nation)` returning True for today's `captured_from` rule OR for an
event whose `type` is in a named `OWN_SOIL_EVENT_TYPES` set AND whose
`region` is player-owned. **Note the region-ownership half is required**:
at the moment the event fires the region is still the player's (the
occupation has not completed), so the predicate has a live truth to read.
(d) Pins: none found on `occupation_started` in the fog filter.

---

### GROUP 10 - `backend/commands/diplomatic_defiance.py` (N64)

Probe: `probe_dispatch.py` section D.
```
D1 history: [{'proposal_type':'peace','override_result':'override','turn':1}]
D2 get_override_dispatch_note: None
D3 with 'good' substituted: "Talleyrand's assessment appears to have been... pessimistic. ..."
D4 dispatch['talleyrand_override_note']: <the line>
```
Both halves REPRODUCED. `grep -rn "record_override(" backend/ --include=*.py`
returns exactly one non-`def` hit, `diplomatic_executor.py:5467`, passing
the literal `"override"`. And `talleyrand_override_note` is read by 0 of
the 55 `.gd` files (confirmed by `probe_gd_parity.py`).

(a) Seams: writer `diplomatic_executor.py:5467`; reader
`diplomatic_defiance.get_override_dispatch_note` (:632/:637); renderer
gap in `main.gd._display_morning_dispatch` + `dispatch_view.gd`.
(b) Filed fix is right that the outcome must be stamped where the
proposal RESOLVES (`world_state._process_proposal_in_transit`), and right
that the renderer must land in the same slice.
(c) Minimal correct fix: send-time writes `"pending"`; the resolution
path rewrites the latest entry to `"good"`/`"bad"`; add the render block.
(d) Pins: `tests/test_session6_diplomacy.py::TestHonestyProblem::test_good_override_note`
/ `::test_bad_override_note` pass the literals `"good"` / `"bad"` DIRECTLY
to `record_override` - **they are exactly the vacuity the row names** and
they stay green either way. `::test_old_override_no_note` and
`::test_history_capped_at_5` likewise. **No flip.**

*.gd flag:* the renderer half touches main.gd + dispatch_view.gd.

---

### GROUP 11 - `backend/game_logic/diplomacy.py` (N81)

Read-only verification.
- `_mission_action` (diplomacy.py:10976) opens with `if tal_state ==
  "IN_TRANSIT": available = False; reason = "Talleyrand in transit"`.
- `tal_state` is computed once at `diplomacy.py:10965` and grep shows it
  is read at exactly ONE place, :10980 - so no other builder reads it.
- The inline rows (`{"action": "declare_war" ...}` x4,
  `{"action": "send_ultimatum" ...}` x5, `break_treaty` x3,
  `downgrade` x3 - lines 11124..11243) never read it.
- The gate they all hit is `diplomatic_executor.py:137-142`, sited BEFORE
  the action dispatch table at :156+, exempting only
  `diplomatic_feasibility`.

(a) Seam: `diplomacy.get_available_diplomatic_actions`.
(b) Filed fix (a post-pass before `return actions`) is correct and is the
right shape - eleven `propose_*` rows plus four inline families is too
many call sites to edit individually. Its one risk: the post-pass must
NOT blanket every row, or `diplomatic_feasibility` and the advisory rows
get falsely disabled. Enumerate the executor-gated ids.
(c) Minimal correct fix: exactly that post-pass, keyed on an explicit id
set.
(d) Pins: no `IN_TRANSIT` assertion in
`tests/test_da2_player_feedback.py`. **No flip found.**

---

### GROUP 12 - `backend/game_logic/naval.py` (N82, N83) - independent, same file

Probe: `probe_misc.py`.

#### FA-N82 - the camp dies with the fleet
```
{'ships': 45, 'camp_turns': 4, 'camp_staged': True,  'britain_posture': 'guard',     'france_blockaded': False}
{'ships': 0,  'camp_turns': 0, 'camp_staged': False, 'britain_posture': 'blockade',  'france_blockaded': True}
```
Exactly the row's A/B. Three readings of one rule:
`camp_staged` (naval.py:1541) uses `get_fleet` (ships-agnostic);
`_camp_tick` (naval.py:1699) iterates `iter_fleets` (docstring: "REAL
fleets only - ships > 0"); `derive_ai_postures` (naval.py:1652-1656)
re-implements the staged test inline over the same iterator.

(a) Seam: `naval._camp_tick` + `naval.derive_ai_postures`.
(b) Filed fix is right and is the same rule the Aug-30 housekeeping loop
(naval.py:1910-1918) already applies with a comment naming this trap.
(c) Minimal correct fix: `iter_fleet_records(world)` beside `iter_fleets`;
use it in `_camp_tick`; have `derive_ai_postures` call `camp_staged(world,
enemy)` over that record set.
(d) Pins: `tests/test_naval_descent.py::TestBoulogneCamp::*` all run
France with its authored 45-ship fleet, so widening the walk keeps them
green. **Blast radius is provably France-only:** I read the authored
`navies` block - only France has `camp_provinces` (Flanders, Artois,
Normandy, Brittany); every 0-ship record (Austria, Prussia, Hanover,
KingdomOfItaly, PapalStates) has none.
**ATTRIBUTION FLAG:** this changes Britain's posture, hence the blockade,
hence France's income, in any run where France's fleet reaches 0 ships
with 40k men in a camp province. If the ambient harness ever reaches that
state, `BASELINE_SERIES` moves. Run the flip experiment.

#### FA-N83 - "once per war" enforced as "once until total peace"
```
still at war with France: ['Austria']
naval powers at war with France: []
diversion_used after 3 ticks: True
diversion_terms: [('a fleet in commission', True),
                  ('at war with a naval power', False),
                  ('the diversion not yet spent this war', False)]
```
The contradiction is INSIDE one report: term 2 already reads "this war"
as "a naval power is at war with us" (iterating `iter_fleets`), while the
reset at naval.py:1917 reads "no war at all".

(a) Seam: `naval.process_naval_turn` step 4, line 1917 - the ONLY clearing
site (`grep -n diversion_used backend/game_logic/naval.py` = 1 setter at
:1593, 1 clearer at :1917).
(b) Filed fix is right, including extracting `naval.has_naval_war` so the
reset and term 2 cannot drift again.
(c) Minimal correct fix: exactly that.
(d) Pins: `tests/test_naval_descent.py::TestGrandDiversion::test_the_spent_feint_resets_at_peace`
sets EVERY enemy to PEACE, so the narrowed predicate still clears. **No
flip.** `::test_once_per_war` is unaffected (same turn, no tick).
**ATTRIBUTION FLAG (mild):** the Diversion has an AI rung, so returning
the card earlier can change AI naval behaviour.

---

### GROUP 13 - `godot-client/.../assets/maps/europe_1805.json` (N85)

Probe: `probe_misc.py`.
```
boot coalition_count: 1
boot active_coalition name: Third Coalition
after re-form: count = 2 name = The Second Austria Coalition
```
(a) Seam: the authored `"coalition_count": 1` at europe_1805.json:69,
directly above the authored `"name": "Third Coalition"` at :72; consumed
only by `coalition.form_coalition` (coalition.py:1549/1552/1553).
(b) Filed fix is correct and its N1 reasoning holds - I confirmed by grep
that `coalition_count` has exactly three production readers, all in
`form_coalition`'s naming block, plus `to_dict`/`from_dict`. It touches
no mechanic.
(c) Minimal correct fix: `"coalition_count": 3`.
(d) **Pin that WOULD FLIP:**
`tests/test_europe_1805_scenario.py::test_third_coalition_seeded` line
347 - `assert world1805.coalition_count == 1`. It must be re-blessed to
3 in the same commit, with the reason on the line (the row's own proposed
test (1) is this same assertion inverted). Three other test files set
`world.coalition_count = 1` by hand (test_da2_player_feedback.py:468,
test_session7_coalition.py:319/745, test_systems_audit_session5.py:349) -
those are local fixtures and stay green.

---

## Cross-row findings

1. **Three clusters must land as units.**
   - `dispatch._derive_marshal_status` + `ledger._derive_status`: FA-N28
     hoists the predicate out of `in_strategic_mode`, FA-N29 teaches the
     readiness list, FA-N36 mirrors it in the ledger, FA-N65 adds the
     captivity arm to the SAME ledger function. FA-N36's fix shape says
     "best done by extracting the dispatch's own predicate" - **that is
     wrong until FA-N28 lands**, because today's dispatch predicate is
     itself nested under `in_strategic_mode`; extracting first copies the
     bug into a second file. Order: N28 -> N29 -> N36+N65.
   - The square family (N47, N50, N57, N70) touches one shared mechanism
     (`_auto_break_square` and the notice channel). N50 and N70 are the
     same class of defect (a raw order enum reaching the player) at two
     sites and should share one helper, as FA-N70's own fix note asks.
   - N64 + N69 + N71 are the same shape: a dispatch key that is built and
     never rendered. One parity pin closes all three and forbids the
     class.

2. **A fourth silent dispatch key nobody has filed.**
   `probe_gd_parity.py` finds `talleyrand_discovery` (written
   unconditionally at dispatch.py:2127 and set at :3546 when the
   confrontation fires) is read by NEITHER `main.gd` nor
   `dispatch_view.gd`. That is a Talleyrand sabotage-discovery
   confrontation going to a key no renderer touches - a bigger loss than
   FA-N71's war-objectives section. Not in my row list; worth a new row.

3. **A substring parity scan over `.gd` hits comments.** My first pass
   flagged `talleyrand_redemption` as a main.gd-only key; every hit is
   inside a PL-23 "popup removed" comment. Whoever writes FA-N69's parity
   pin must strip comments, or the pin can be satisfied by dead text.

4. **FA-N31's block contains a second, unfiled defect.** The CRITICAL
   notification and the `vassal_rebellion` event ("War declared.") sit
   OUTSIDE the `if current_state == "ARMISTICE": ... else:` split at
   vassal.py:888/896, so an armistice-respected break emits both
   `vassal_rebellion_armistice` ("no war declared") and `vassal_rebellion`
   ("War declared.") on the same tick. Fold it into the same slice.

5. **Two rows carry a wrong factual claim that changes the fix.**
   - FA-N52: `glory_crown_lost` DOES have a producer (jealousy.py:570)
     and a `_DISPATCH_EVENT_TYPES` severity arm; the row's instruction to
     delete it "because it has no producer of any kind" is false and
     forecloses the better fix.
   - FA-N65: "strategic_ledger.gd:267 already renders 'Prisoner' with
     zero .gd change" is true for the FORCES row and FALSE for the ORDERS
     row, whose "No active orders" string is hard-coded in the client at
     :936 and never read from the payload.

6. **One row's own proposed test cannot be written as stated.** FA-N32
   asks for "the seed range that reaches the shatter arm". No seed reached
   it in 62 staged charges at four force ratios; the loser is annihilated
   to 0 first and the block is gated on `enemy.strength > 0`. Pin the
   extracted pure helper instead.

7. **One row's own fix shape is insufficient.** FA-N47 says to make the
   CLEAR at `executor.execute()` re-entrancy-aware. The EMIT at
   executor.py:2660 must be made outermost-only in the same edit, or the
   nested `execute()` consumes the notice onto an inner message the
   strategic route discards - the same loss, one frame down.

8. **Stale line numbers, as warned.** Measured drift on the rows I
   navigated by symbol: FA-N27 :1181 -> ~:1181 (ok), FA-N28 :2579 ->
   :2579 (ok), FA-N47 :905 -> :991 and :2493 -> :2660, FA-N50 :480 ->
   :496, FA-N57 :1562 -> :1667 and :512 -> :525, FA-N70 :7433 -> :7644,
   FA-N31 :993 -> :1015, FA-N32 :12429/:12471 -> :12494/:12536, FA-N82
   :1597 -> :1699, FA-N83 :1815 -> :1917, FA-N64 :5419 -> :5467, FA-N65
   :76 -> :74, FA-N81 :10964 -> :10976, FA-N66 :1798 -> :2091. **Roughly
   80% stale, as the preamble says.**

9. **Rows whose fix touches `.gd`** (each forces a Godot parse harness +
   boot smoke): FA-N55 (`enemy_phase_dialog.gd`), FA-N69
   (`dispatch_view.gd`), FA-N71 (`main.gd` + `dispatch_view.gd`), FA-N64's
   renderer half (`main.gd` + `dispatch_view.gd`), FA-N28's optional glyph
   half (`main.gd` + `dispatch_view.gd`), FA-N65's ORDERS half if the
   builder wants "Prisoner of Austria" (`strategic_ledger.gd`). All others
   are backend-only.

10. **Rows that could move an AI decision / the series**: FA-N82 (camp
    tick -> Britain's posture -> blockade -> France's income) and, mildly,
    FA-N83 (the Diversion's AI rung). Everything else in this family is
    copy, a display flag, or an unreached branch. **No row here adds a
    serialized field**; FA-N27 reads one that already exists. **No row
    here changes `len(CAMPAIGN_LOG_TYPES)`** as long as FA-N52 is fixed at
    the collector sets (adding types would flip nine pins).

11. **Harness note.** Every probe used `probe_env.boot()`; the 1805
    default boots with `is_dotation_world(world) == True`, which is why
    the FA-N27 arithmetic reproduces on the shipped board. Beware
    `d.get("headline")` - it is a DICT (`{class, weight, text,
    sub_beats}`), not a string; slicing it raises `KeyError:
    slice(None, 170, None)`, which cost me a probe cycle.

---

## Probe inventory

All under
`<scratchpad>/repro/j6/`:

| file | rows it serves |
|---|---|
| `probe_gazette.py` | FA-N52 (collector/campaign-log set difference + producer census) |
| `probe_dispatch.py` | FA-N28, FA-N29, FA-N36, FA-N65, FA-N58, FA-N30, FA-N64 |
| `probe_estate.py` | FA-N27 first cut (run vs age table) |
| `probe_estate2.py` | FA-N53 (option/confirm/dispatch/erosion numbers) |
| `probe_estate3.py` | FA-N27 (the rendered escalation sentence, turns 4-12) |
| `probe_estate4.py` | FA-N27 arm (b) (two eroding marshals, first settled at t14) |
| `probe_square.py` | FA-N50, FA-N57, FA-N47 |
| `probe_square2.py` | FA-N70 (all three order types) |
| `probe_rout.py` | FA-N32 (arithmetic + defender-arm reachability, 20 seeds) |
| `probe_rout2.py` | FA-N32 (six force ratios + the expression side-by-side) |
| `probe_rout3.py` | FA-N32 (attacker arm, 36 staged charges) |
| `probe_misc.py` | FA-N82, FA-N83, FA-N31, FA-N85 |
| `probe_gd_parity.py` | FA-N69, FA-N71, FA-N64 (dispatch key parity census) |
