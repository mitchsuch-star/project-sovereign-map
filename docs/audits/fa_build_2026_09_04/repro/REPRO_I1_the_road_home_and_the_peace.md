# REPRO I1 -- slice 12 "The Road Home and the Peace": FA-33, FA-N61, FA-N73

Agent i1, read-only, master `a1ed5c9d`, shipped 1805 `boot()` world, mock parser, every turn a
REAL `POST /command end turn` unless stated. Probes under `<scratchpad>\repro\i1\`.

## Summary

- **FA-33 -- NARROWED (defect real, seam correct, scope claim geometry-dependent, cost re-derived).**
  `_issue_road_home_orders` stamps `issued_turn=current_turn`; `process_strategic_orders` skips it as
  "first step already executed"; no first step ever ran. Measured: Davout at Vienna stands still on
  the peace turn, surplus drops 3 -> 2 = `EVACUATION_WARNING_MARGIN`, and a marching corps is warned
  on EVERY turn it stands on soil that needs the treaty (on the row's own road that IS every turn,
  t2..t5, because Austria -- still at war with Bavaria -- captures Swabia at t2 and Franconia at t3
  under his feet; on the Volhynia fixture road it would not be). The omitted mechanical cost: the
  slack is spent before the march begins, so ONE unanswered cannon-fire ask on the road leaves 1
  turn, two leave 0, three intern him -- measured, Davout interned at Bohemia on turn 6 on the row's
  own geometry with the ask left unanswered; and GR5 is broken the other way: the AI's stranded
  corps walks on the SAME end turn (rung P1.2 runs in the enemy phase and never reads
  `issued_turn`). Both filed fix shapes restore the full slack (home turn 5, zero warnings, expiry
  unchanged); shape (i) is inert for the AI, shape (ii) makes the AI corps double-hop.
- **FA-N61 -- REPRODUCED, and organically on the row's own board.** Davout at Vienna + peace:
  Bernadotte (Franconia, Bavarian) and Massena (Milan, Italian) are legal at the peace, get no order,
  are stranded by Austria's captures on t2-t3, are warned 2/1/0 and INTERNED on turn 7 -- "two
  French marshals destroyed in six turns", to the digit. The filed top-up saves both, but as filed
  it re-issues an order the player CANCELLED every tick (the road becomes un-refusable) and every
  topped-up order inherits FA-33's lost turn unless FA-33 lands first.
- **FA-N73 -- REPRODUCED exactly as filed.** Holland and KingdomOfItaly are co-belligerents in
  `war_1` on France's side, so `ensure_war_instance_for_pair` returns `war_instance_side_conflict`
  and the graceful `continue` skips all five consequences; Switzerland (not in the war) takes the
  WAR exit and gets all five. The filed fall-through fix would make the graceful exit announce
  "War declared." twice (the ARMISTICE exit already does, measured) and WOULD move
  `BASELINE_SERIES`: KingdomOfItaly leaves France gracefully at t11 on the ambient board.

## Per row

### FA-33 -- the road-home order loses its first turn

**Ran:** `probe_1_fa33_geometry.py` (row geometry, real end turns, + Mack-on-French-soil mirror),
`probe_2_fa33_steady_march.py` (arm A interrupts answered, arm B interrupts suppressed, arm C clean
AI mirror), `probe_3_fa33_fix_arms.py` (control / shape i / shape ii, both sides on one peace),
`probe_7_road_controllers.py` (why allied legs read as needing the treaty),
`probe_6_ambient_corridor_census.py` arms 0 and i (the 40-turn harness replica).

**Evidence.**

Issuance (probe 1/2): `set_diplomatic_state(w,'France','Austria','PEACE','probe')` at turn 1 with
Davout at Vienna ->
```
grants={'Austria|France': 8}   Davout order=MOVE_TO->Franche-Comte issued_turn=1 started_turn=1
path=['Vienna','Bohemia','Franconia','Swabia','Franche-Comte'] is_road_home=True
beat: 1 corps stands on the wrong side of the new frontier. Berthier has given them the road home --
      Davout to Franche-Comte. They have safe passage for 7 turns while they march.
distance_home=4 expiry=8 surplus_now=3
```
The end-turn ordering is `TurnManager.end_turn`: enemy phase (:222) -> `process_strategic_orders`
(:270) -> `advance_turn` (:292, increments the turn at world_state.py `advance_turn`, then ticks
`process_evacuation_grants`). The processor's skip is `strategic.py` inside
`StrategicOrderProcessor.process_strategic_orders`:
```
issued = getattr(order, 'issued_turn', None)
if issued is not None and issued == world.current_turn:   # "first step already executed by executor.py"
```
Real end turns, interrupts suppressed (probe 2 arm B), the row's own road:
```
end turn #1 t1->2: Davout Vienna->Vienna | stranded=True dist=4 exp=8 surplus=2
   strategic: Davout is marching to Franche-Comte (5 turn(s) remaining).      <- the SKIP
   tactical[evacuation_lapsing]: ... 4 march(es) still to go from Vienna, and 2 turn(s) of safe passage left ...
end turn #2 t2->3: Vienna->Bohemia   dist=3 surplus=2  warned
end turn #3 t3->4: Bohemia->Franconia dist=2 surplus=2 warned
end turn #4 t4->5: Franconia->Swabia dist=1 surplus=2  warned
end turn #5 t5->6: Swabia->Franche-Comte  "Davout arrives at Franche-Comte."  HOME
WARNED ON TURNS: [2, 3, 4, 5]
```
Why every leg counts as stranded on THIS road (probe 7): `OPEN_MOVEMENT_STATES` includes ALLIANCE
and France-Bavaria is ALLIANCE, so Bavarian soil is passable without the treaty -- but Austria is
at WAR with Bavaria and captures the road under him:
```
t1 controllers: Franconia=Bavaria Swabia=Bavaria   (Mack at Swabia)
t2 controllers: Swabia=Austria      (captured in turn 1's enemy phase)
t3 controllers: Franconia=Austria   (ArchdukeCharles)
Davout@Franconia stranded=True passable_here(no grant)=False
```
So "warned EVERY turn until home" is true on the row's road only because the counterpart eats the
allied legs; the general shape is "warned on every turn he stands on soil that needs the treaty",
which on the test fixture's Volhynia road (war-passable Austrian legs) is fewer turns than the
march. That is the Sept-2 narrowing, re-derived.

The cost the row does not claim (probe 1 = the row's geometry with the cannon-fire ask left
unanswered, i.e. what an unattended turn does):
```
end turn #3 t3->4: Bohemia->Bohemia  surplus=1  strategic: Davout: 'Cannon fire at Milan, Sire. Investigate?'
end turn #4 t4->5: Bohemia->Bohemia  surplus=0  (same pending ask)
end turn #5 t5->6: tactical[marshal_interned]: Davout's corps failed to quit Austria soil ... interned.
fallen={'nation':'France','turn':6,'location':'Bohemia','cause':'interned'}
```
A road-home MOVE_TO is an ordinary order, so `_check_interrupts` raises the cannon-fire ask for a
non-literal marshal; a pending interrupt defers the march. With the full slack (3) the same three
stalls would end at "0 turn(s) left", not internment. Answering `continue_order` (probe 2 arm A)
executes a movement step at answer time (`Bohemia->Franconia`), so an ANSWERED ask costs no march --
but it costs **-2 trust** ("non-literal acting literal") on the treaty's own order, and the interim
warning reads "1 turn(s) of safe passage left".

GR5 (probe 2 arm C, probe 3 all arms): Mack at Orleanais gets `MOVE_TO->Tyrol issued_turn=1` from
the same peace and moves `Orleanais->Lorraine` on end turn #1 -- rung P1.2 (`enemy_ai.py`
"PRIORITY 1.2: THE ROAD HOME") reads `is_road_home_order` + `next_step_home` and never `issued_turn`.
The player's corps alone loses the turn.

Supply attrition as the cost: NOT measured to bite here (Vienna fed him, 26,000 constant on the lost
turn; 572 lost on the Vienna->Bohemia march). It bites wherever the lost turn is spent on a
short-supply province (the spec's own Volhynia case); not re-measured.

**Fix arms measured (probe 3; interrupts suppressed; Davout at Vienna AND Mack at Orleanais):**
```
ARM 0 control : Davout home turn 6, warned t2,t3,t4,t5; expiry 8; Mack walks on end turn #1
ARM (i)  issued_turn = current_turn-1 : Davout walks on the peace turn ("marches to Bohemia"),
         surplus 3 every tick, ZERO warnings, home turn 5; expiry 8 unchanged; Mack identical to control
ARM (ii) first hop at issuance : Davout@Bohemia at issuance, end turn #1 SKIPPED (premise now true),
         zero warnings, home turn 5; expiry 8 unchanged; Mack Orleanais->Lorraine AT ISSUANCE and
         Lorraine->Swabia in the same end turn's enemy phase = DOUBLE HOP
```
`issued_turn` reader census (grep, whole backend): writers `movement_executor.py:506`,
`strategic_executor.py:1273`, `:1987`, `withdrawal.py:691`; readers `strategic.py:898` (debug print),
`:901` (the skip), `:2633` (HOLD timed expiry, `order.issued_turn or order.started_turn` -- a MOVE_TO
never reaches it), `marshal.py` to/from_dict (None round-trips). `strategic_executor.py:2494`
`is_first_step = old_order.started_turn == world.current_turn` reads `started_turn`, untouched by
(i). No test asserts the treaty order's `issued_turn`.

**Verdict:** NARROWED as above.

**Seam by symbol:** `backend/game_logic/withdrawal.py::_issue_road_home_orders` (the stamp) vs
`backend/commands/strategic.py::StrategicOrderProcessor.process_strategic_orders` (the skip whose
premise "first step already executed by executor.py" is only true for
`strategic_executor.py`'s issuance path, which runs `_execute_movement_step` right after creating the
order). The judge `withdrawal.py::process_evacuation_grants` is correct and untouched.

**What the filed fix would break:** shape (i) `current_turn - 1` breaks nothing measured (both corps
home at 5, no warnings, AI unaffected) but writes a false issue turn that the `:898` debug line and any
future reader would repeat. Shape (ii) needs the executor and `game_state` threaded through
`set_diplomatic_state`'s three `open_evacuation_corridor` call sites (the opener takes only
`world`), runs a real movement (attrition, "marches to" narration) inside a diplomatic transition --
including the enemy-phase AI-AI peace and the settlement-ratify path -- gives the AI corps a second
hop on the peace turn (GR5 inverted), and reds
`tests/test_win_d3_road_home.py::TestFreeMarchOrders::test_the_order_carries_a_real_path_home`
(`assert order.path and order.path[0] == davout.location` -- measured after the hop the path is
`['Franconia','Swabia','Franche-Comte']` with Davout at Bohemia).

**Minimal correct fix:** do not stamp `issued_turn` on the treaty's order at all (leave the field's
default `None` -- its documented meaning is "first step already executed", which is false here);
the skip's predicate `issued is not None and issued == current_turn` then lets the same end turn's
processor walk him. Measured equivalent to shape (i) by the predicate (arm (i) was the run; `None`
was not run separately -- the builder's pin should drive the real `end turn` and assert the peace-turn
march). Optional: the beat's "safe passage for 7 turns" and the warning's "N turn(s) left" quote
different quantities; with the fix a marching corps is never warned, so the contradiction survives
only for a dawdler, which the spec accepts (T1/T2). GR5 needs nothing: P1.2 already walks on the
peace turn.

**Pins:** `tests/test_win_d3_road_home.py::TestSelfRefreshingCorridor::test_a_marching_corps_is_never_warned_and_never_interned`
(`_march_home` hand-moves `marshal.location = step` after `world.current_turn += 1`, never runs the
processor -- cannot see the skip; passes before and after), `::test_standing_still_earns_three_warnings_then_internment`
and `TestWhatThePlayerReads` (advance by `current_turn += 1` + `process_evacuation_grants`, no
processor -- unchanged by the fix; the T2 "runs out in 2 turn(s)" is a STANDING corps and stays).
No pin flips under `None`/(i). `BASELINE_SERIES` (`tests/test_ai_intent_threat_migration.py`):
the ambient 40-turn replica (probe 6, `PYTHONHASHSEED=0`) reproduces the pinned series byte-for-byte
and its only corridor is `t39 evacuation_granted Spain|Switzerland: Castanos can find no land route
home` -- no road-home order is ever issued to anyone in 40 turns; arm i (fix applied) is byte-identical
(`MATCHES BASELINE_SERIES: True`). No re-record expected, by construction.

### FA-N61 -- a corps stranded AFTER the peace is never handed the order

**Ran:** `probe_4_fan61_stranded_after_peace.py` (arm A the row's recipe, arm B the AI mirror, arm C
the standing-HOLD shape), `probe_8_fan61_organic_and_topup.py` (arm 0 organic on the row's board,
arm topup = the filed fix, arm topup+cancel = the refusal hazard). Interrupts suppressed so a
cannon-fire ask cannot confound the march.

**Evidence -- the row's recipe (probe 4 arm A):** Davout at Vienna, Ney at Franconia (Bavarian, ALLIANCE),
peace:
```
Davout@Vienna stranded=True order=MOVE_TO->Franche-Comte road_home=True
Ney@Franconia stranded=False dist=2 order=None      _evacuating_marshals(France)=['Davout']
FLIP Franconia -> Austria
Ney@Franconia stranded=True dist=2 surplus=5 order=None   _evacuating_marshals=['Ney','Davout','Bernadotte']
t4: Ney ... 2 march(es) ... 2 turn(s) of safe passage left   (order=None)
t5: ... 1 turn(s)        t6: ... 0 turn(s)
t7: tactical[marshal_interned] Ney: Ney's corps failed to quit Austria soil ... interned.
    fallen={'nation':'France','turn':7,'location':'Franconia','cause':'interned'}
```
**Organic on the shipped board (probe 8 arm 0)** -- nothing flipped by hand; Austria's continuing wars
with Bavaria and KingdomOfItaly do it:
```
boot: Bernadotte@Franconia(ctl=Bavaria)  Massena@Milan(ctl=KingdomOfItaly)   -- both legal at the peace
t2->3 capture: Franconia (from Bavaria)      Bernadotte stranded=True order=None
t3->4 capture: Milan, Piedmont (from KoI)    Massena stranded=True order=None
warnings 2/1/0 on t4/t5/t6 for both;  t7: Bernadotte AND Massena interned
FALLEN: Bernadotte {'turn':7,'location':'Franconia','cause':'interned'}  Massena {'turn':7,'location':'Milan',...}
```
That is the row's title, to the digit, from the row's own single-line recipe.

**GR5 mirror (probe 4 arm B):** ArchdukeCharles on own Moravia at the peace, Moravia flipped to
France after: `stranded=True order=None`, but the AI walked him `Moravia->Hungary` (home) on end turn
#1 on its OTHER rungs -- no P1.2 (no order), saved by being one march from home. The gap is symmetric;
the AI's escape here is geometry, not design.

**The filed fix, measured (probe 8 arm topup = `_issue_road_home_orders(world, *pair)` for every
standing non-WAR pair before the judging pass):** Bernadotte issued at the t2->3 tick, Massena at the
t3->4 tick; both walk home; nobody interned; `grants={}` at t6 (corridor retired because finished).
Two defects inside the fix:
1. **It inherits FA-33.** The tick runs AFTER the processor, stamps `issued_turn=current_turn`
   (post-increment), so the next end turn's processor SKIPS the fresh order: Bernadotte issued at
   t3 stood at Franconia through t4 (`surplus 2`, warned) and walked at t5. Every topped-up corps
   burns one of its three slack turns at issuance unless FA-33 lands first.
2. **The road becomes un-refusable** (arm topup+cancel): `Davout, cancel orders` -> "Davout halts his
   march and awaits new orders." `order_now=None`; next tick `order=MOVE_TO->Franche-Comte road=True`
   again, every turn. Spec `WAR_WITHDRAWAL_SPEC.md` s4.1: "cancellable, overridable"; the existing
   guard respects only a NON-road-home standing order, so a cancelled (None) corps is
   indistinguishable from a newly-stranded one.

**Verdict:** REPRODUCED (and wider: it fires organically within six turns of the row's own recipe).

**Seam by symbol:** `withdrawal.py::process_evacuation_grants` re-derives `_evacuating_marshals` every
tick while `withdrawal.py::_issue_road_home_orders` runs only from `open_evacuation_corridor`, whose
three call sites are `diplomacy.py::set_diplomatic_state` (WAR->non-WAR, and ARMISTICE->PEACE) and
`world_state.py` (the post-cession re-run). The stranding producers are ordinary captures by the
counterpart's still-running wars (`Austria|Bavaria`, `Austria|KingdomOfItaly`), which no opener sees.

**What the filed fix would break:** (1) and (2) above; plus the player is told of a NEW stranding
only by the lapsing warning at surplus 2 (the top-up issues silently; no beat).

**Minimal correct fix:** the top-up at the judge, as filed, with three riders: land FA-33 first (or
the top-up's own orders lose a turn); honour a refusal with zero new fields -- have the executor's
cancel of a road-home order convert it into an explicit HOLD at the current province (a player order
the existing guard already respects) with a sentence naming the lapse ("Davout holds Vienna; his safe
passage lapses in N turns"); and log one `evacuation_granted`-class beat naming each corps the tick it
is topped up. GR5 comes free (P1.2 reads the order).

**Pins:** `tests/test_win_d3_road_home.py::TestNeverDoPins::test_the_order_is_ordinary_and_overridable`
sets `davout.strategic_order = None` then runs `W.process_evacuation_grants(world)` and asserts only
"must not crash" -- it does NOT flip under the filed top-up but its stated intent ("nothing about the
corridor resists him") is exactly what the top-up violates; the builder should extend it to assert
the order is not re-issued, at which point the filed shape reds. `::test_a_standing_player_order_is_not_overruled`
(guard kept) passes. `TestFreeMarchOrders::test_no_order_is_invented_for_a_corps_with_no_road`,
`test_a_cut_off_corps_is_never_interned`, `test_the_corridor_still_expires_over_a_corps_it_cannot_help`
pass (the cut-off skip is inside `_issue_road_home_orders`). `tests/test_wo_slice13_corridor_direction.py`'s
bare-call census: the top-up adds no `has_evacuation_grant` call. `BASELINE_SERIES`: the ambient run's
only grant (t39, Castanos cut off) issues nothing under a top-up either -> no re-record expected;
verify with the flip arm at landing.

### FA-N73 -- the graceful-independence exit skips five consequences

**Ran:** `probe_5_fan73_rebellion_exits.py` (Holland, KingdomOfItaly, Switzerland at loyalty 0 on the
shipped boot with `Marshal('Daendels', nation='France', original_nation=<vassal>, 12000)` planted at
the satellite's capital; plus Holland with `diplomatic_states[key]='ARMISTICE'` pre-set), output in
`probe_5.out`; `probe_6` arm i for the ambient exits.

**Evidence.** Exit selection: `validate_war_declaration(<vassal> -> France)` returns
`ok=False error=war_instance_side_conflict` for Holland and KingdomOfItaly (both on `war_1`'s
attackers side `['France','Spain','Holland','Bavaria','KingdomOfItaly']` vs
`['Britain','Austria','Russia']`) and `ok=True` for Switzerland (in no war instance) -- "2 of France's
3 at the 1805 boot", confirmed.
```
GRACEFUL (Holland):  EVENTS [vassal_rebellion_independent]
  DIFF: siblings {Holland100,KoI100,Swiss100}->{KoI100,Swiss100}; state VASSAL->PEACE;
        dispatch [] -> ['diplomatic_carved_vassal_dissolved']       (queued BEFORE the exit split)
  UNCHANGED: corps ('France','Holland',12000,trust70,'Amsterdam'); relation unset; notifications 0;
             threat_by_target France 70
GRACEFUL (KingdomOfItaly): identical shape
WAR (Switzerland):   EVENTS [4 typeless cascade records, vassal_rebellion "War declared."]
  DIFF: corps -> ('Switzerland', None, 12000, 70, 'Bern'); siblings Holland 90, KoI 90; relation -50;
        state WAR (+ cascade wars Bavaria|Spain|Holland|KoI vs Switzerland); notification
        'Switzerland REBELLED!'; dispatch +diplomatic_alliance_cascade x2 +diplomatic_vassal_rebellion;
        threat France 70 -> 60
ARMISTICE (Holland pre-set): EVENTS [vassal_rebellion_armistice "no war declared", vassal_rebellion
  "...All vassal marshals have returned to Holland. War declared."]; the whole tail applies (corps
  handed back, siblings 90/90, relation -50, notification 'Holland REBELLED! ... War declared.',
  threat 70->60) while state stays ARMISTICE.
```
**Verdict:** REPRODUCED as filed. Five consequences skipped on the graceful exit; the ex-lord keeps
the satellite's assimilated corps permanently.

**Seam by symbol:** `backend/game_logic/vassal.py::check_vassal_rebellion`, the `ok=False` arm of the
`ensure_war_instance_for_pair` result (`settlement_helpers.py::ensure_war_instance_for_pair` ->
`validate_war_declaration`), which `continue`s past the shared tail.

**What the filed fix would break:** the shared tail is not exit-neutral -- its CRITICAL notification
body is "<vassal> has rebelled against <lord>! War declared." and its `vassal_rebellion` event says
"... War declared." A bare fall-through makes the graceful exit announce a war that does not exist,
exactly as the ARMISTICE exit already does (measured above: two contradictory events in one tick).
The VS-3 `granted_regions` reclaim is correctly WAR-only and must stay so. And it moves
`BASELINE_SERIES`: on the ambient board (probe 6 arm i, vassal tracking) **KingdomOfItaly LEFT lord
France at t11; state now PEACE; relation=unset** -- the graceful exit, live -- so the tail's
`reduce_threat(world, 10, 'vassal_rebellion', target='France')` would lower France's slot 55->45 at
t11 and re-shape the series from index ~11 (Switzerland at t25 already takes the WAR exit and already
pays). A re-record is EXPECTED for this row, attributable by a single flip arm (gate the
`reduce_threat` call).

**Should any of the five be skipped for a graceful exit?** Corps hand-back (a departing power takes
its own army; France keeping Holland's corps forever is the worst of the five), the -10 sibling shock,
the -10 lord threat reduction, the notification and the dispatch event all describe "the satellite
left" -- none should be skipped. The -50 relation is the only arguable term: a peaceful split is not a
betrayal; but loyalty 0 IS hostility in fact, and the same -50 already applies on the ARMISTICE exit.
Recommend keeping ONE tail with `war_declared` gating only the sentence (and, if the designer wants
it, a smaller graceful relation term as a stated number) rather than a second copy.

**Minimal correct fix:** replace the `continue` with `war_declared = False`, fall through, and make the
notification/event/dispatch sentences read the flag ("breaks free ... no war is declared" vs "War
declared.") -- fixing the ARMISTICE exit's existing lie in the same stroke.

**Pins:** `tests/test_playtest_fixes_2026_07_14.py::TestRebellionNoOrphan::test_blocked_war_allocation_becomes_independent`
asserts removal from `world.vassals`, state `PEACE`, and the `vassal_rebellion_independent` event;
its `_make_world()` is a real `WorldState()`, so the tail's `notifications.add`/`reduce_threat`/
`queue_dispatch_event` run -- survives a fall-through. No pin asserts the skipped tail on either
arm. `tests/test_ai_intent_threat_migration.py::BASELINE_SERIES` WILL flip (t11 KoI).

## Cross-row findings

1. **A THIRD shape of the same family, live in an archived campaign:** a corps under a standing player
   order at the peace gets no road (spec s4.1 "does not overrule the Emperor"), the beat names nobody
   -- measured `beat: The peace grants safe passage home.  marshals=['Davout'] destinations={}` (the
   `_grant_message` fallback fires because `orders` is empty while `marching` is not) -- and he is
   warned 2/1/0 while the cautious HOLD auto-fortifies ("Davout fortifies Vienna") and interned on
   turn 5 (probe 4 arm C). `docs/audits/playtest_digests/1b-pacifist-austerlitz-r1/digest.md` is this
   shape played: `Ney, hold position` / `Davout, hold position` / `Soult, hold position` on turn 1,
   peace with Austria accepted ~turn 21 with four corps at Austrian-held Swabia, "Lannes, Murat,
   Napoleon and Ney are no nearer home ... 2 turn(s)" / "1 turn(s)", then **"the Emperor himself is
   TAKEN. Austria holds him"** and "Marshal Ney's corps was interned at Swabia by Austria". Not
   caused by FA-33 or FA-N61; not fixed by either. Needs its own row: the beat must name the corps
   the treaty declined to move and the reason, and the lapse warning should say "he holds under your
   order".
2. **The ARMISTICE exit of `check_vassal_rebellion` lies twice** ("no war declared" then "War
   declared." in the same tick, plus the CRITICAL notification) -- pre-existing; the FA-N73 fix should
   take it.
3. **Four typeless records** in the WAR exit's returned event list: `_process_war_cascade` appends
   `{"defender","ally","previous_state"}` dicts (`diplomacy.py:8834` etc.) into the same list as
   typed events; consumers keyed on `type` see `None`. Pre-existing, cosmetic.
4. **`continue_order` on the treaty's own order costs -2 trust** ("non-literal acting literal") and
   `investigate` abandons the road; a road-home MOVE_TO is interruptible like any order. Design
   question, not a defect claim.
5. **Shape (ii) GR5 inversion:** executing the first hop at issuance gives the AI corps two hops on
   the peace turn (P1.2 walks again in the same enemy phase).
6. **Observed, not diagnosed:** after an enemy-phase Austria|Bavaria peace re-ran the opener (t2),
   Mack's road-home order was re-targeted (`MOVE_TO->Swabia issued_turn=2`) and he stood at Lorraine
   for two enemy phases before walking (probe 2 arm C, probe 3). Not on these rows' path.
7. **Harness notes.** The 40-turn replica of `_emit_series` (probe 6, `PYTHONHASHSEED=0`, unset seed)
   reproduces the pinned `BASELINE_SERIES` byte-for-byte, so its census is trustworthy: one corridor
   in 40 turns (t39 Spain|Switzerland, cut-off only), zero road-home orders, one graceful vassal exit
   (KoI t11), one WAR exit (Switzerland t25). The `event_log` 500-cap evicts rebellion events (the
   IGR-B trap) -- the vassal census reads `world.vassals` per turn instead. `set_diplomatic_state`
   direct (the rows' recipe) leaves `war_1`'s France|Austria pair standing; the corridor code checks
   the diplomatic state only, so the recipe is valid for these rows.
8. **Row text corrections.** FA-33's "warned EVERY turn until home" holds on the row's road for a
   reason the row does not state (Austria captures the allied legs); FA-33's `withdrawal.py:691`
   line is exact today, `strategic.py:260-264` is stale (the skip is at ~:901), `world_state.py:9388`
   / `:9789` are stale (~:9416 / ~:9820). FA-N61's line `:786` is exact. FA-N73's `:948-962` are
   stale (~:930-984); its measured numbers (Holland/KoI graceful, Switzerland war, siblings 100/90,
   relation unset/-50) all re-confirmed.

## Probe inventory

`<scratchpad>\repro\i1\`:
- `probe_1_fa33_geometry.py` -- row geometry through real end turns (+ Mack-on-French-soil mirror)
- `probe_2_fa33_steady_march.py` -- interrupts answered / suppressed / clean AI mirror
- `probe_3_fa33_fix_arms.py` -- control vs shape (i) vs shape (ii), both sides on one peace
- `probe_4_fan61_stranded_after_peace.py` -- the row's recipe, the AI mirror, the standing-HOLD shape
- `probe_5_fan73_rebellion_exits.py` (+ `probe_5.out`) -- all three exits + ARMISTICE
- `probe_6_ambient_corridor_census.py` (+ `probe_6_arm0.out`, `probe_6_armi.out`) -- the 40-turn
  harness replica with corridor/order/vassal census; arm i = FA-33 fix shape
- `probe_7_road_controllers.py` -- controllers along Davout's road per turn
- `probe_8_fan61_organic_and_topup.py` (+ `probe_8.out`) -- organic FA-N61, the top-up fix, the cancel hazard
