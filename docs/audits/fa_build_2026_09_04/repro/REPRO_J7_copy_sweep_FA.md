# REPRO J7 - slice 16 original-audit rows (23) - read-only reproduction pass

Repo at master `a1ed5c9d`. Every probe under
`<scratchpad>/repro/j7/`. Nothing in the repo was touched.

## Summary

| row | verdict | measured mechanism (one line) |
|---|---|---|
| FA-44 | REPRODUCED (narrow) | `_pick_observation` has no scale gate: a 1-vs-58 exchange with a defender terrain bonus 20 returns the `lost_despite_terrain` bank verbatim. |
| FA-45 | REPRODUCED | `build ships` at the 1805 boot prints "readiness 69 (new crews come aboard green at 40 ...)"; France is `self_blockaded_by: Britain` and the blockade rot (-5/turn) is never named. |
| FA-49 | REPRODUCED | The cannon-fire report dict carries `options: ['investigate','continue_order','hold_position']` and NO cost key at all; `continue_order` charges -2, `hold_position` -3, `investigate` 0. |
| FA-51 | REPRODUCED | Yard gate (`naval_executor.py:290`) fires strictly before the lift gate (`:308`); "land Soult in Munster with 12,000 men" is answered "must stand at one of our yards" and the "12,000" is never read. |
| FA-52 | REPRODUCED, but duplicates FA-49's tax half | Under a HOLD order: "Davout reluctantly continues the march, ignoring cannon fire at Franconia. Davout fortifies Rhineland." trust 85 -> 83, order still HOLD; the battle was Blucher vs Hohenlohe (nation-blind). |
| FA-56 | REPRODUCED (dead code, proven by control) | Writer stamps `literal_intel_paused_turn`; reader at `world_state.py:2902` reads `_literal_intel_paused_turn`. Control: setting the underscore darkens the sector, setting the real field does nothing. |
| FA-58 | REPRODUCED | `max(FLOOR, r - TICK)` at `naval.py:1675`: France blockaded at readiness 40 becomes **50** after one tick; 45 becomes 50. |
| FA-59 | REPRODUCED verbatim | Forced diversion loss on the 1805 boot: message "loses 49 sail" while `losses['France'] = {France 25, Spain 17, Holland 7}` and France held 45. The dispatch beat carries `loser_ships_lost: 49` too. |
| FA-61 | REPRODUCED and WIDER than filed | "78,676 if all march" resolved to 84,266 with 3 of 6 candidates absent. TWO causes, not one: the arrival weighting, AND the sovereign aura (+10%) which is stamped only at resolve. The row's own prescribed fix prints 90,172 while the resolver can reach 96,790. |
| FA-63 | REPRODUCED (authored premise falsified) | Tutorial, Senarmont to Munich on T1: Charles leaves Hungary in the T1 enemy phase, stands at Tyrol at T2, attacks Senarmont in the T2 enemy phase; Charles + Schwarzenberg + Kienmayer all attack in the T3 phase. The `_comment` promises turn 8+. |
| FA-64 | REPRODUCED | Typed confirm: "...fights at readiness 59. Sail? (yes/no)" - no camp clause. The Admiralty chip for the same action, same world: "...; no army is staged to use the open water". |
| FA-65 | REPRODUCED, and the "dead zone" claim is REFUTED | Loyalty 41 -> 39 gives `recovery_hint == ''`; 38 -> 36 the same. BUT a THIRD producer, `diplomatic_ledger.py:683-684`, carries the hint at 39/36/30 and NOT at 45 - the exact inverse gate. |
| FA-67 | REFUTED as headlined; a narrower half survives | A won battle DOES add trust: `combat_executor.py:2646` -> `VindicationTracker.resolve_battle` -> 'trust'+'victory' = **+3** via `marshal.modify_trust`. The surviving half: a win raises `get_expectation` 0 -> 40 (measured), deepening a dotation shortfall. |
| FA-69 | REPRODUCED verbatim | "Sire - Bohemia sustains Marshal ArchdukeCharles's household" while the SAME sentence routes the nation through `formed_display_name`. FOUR sites, one of them `.gd`. |
| FA-70 | REPRODUCED at source | `war_detail_popup.gd:439` `else:` binds to `if naval_line != "":` (:437), not to `if we != null:` (:424, closes unclosed at :431). |
| FA-81 | REPRODUCED | `deploy/README_TESTER.txt:100` "Seven marshals stand ready in the east"; `docs/TUTORIAL_SCRIPT.md` has **0** occurrences of "Napoleon"; the boot roster has 8 (Napoleon, Lorraine, sovereign). |
| FA-82 | REPRODUCED | `set_tutorial_done(true)` at `tutorial_overlay.gd:452` is the ONLY setter call anywhere; `on_world_swap` (:280) disarms on the latch; `_on_tutorial_pressed` (**:438**, not :409) never clears it. |
| FA-93 | REPRODUCED verbatim | `[Square broken - Ney breaks formation to attacks]` / `to moves to]` / `to fortifies]`. |
| FA-95 | REPRODUCED | Both f-strings (`diplomatic_executor.py:686` and `:695`) print the DECREMENTING cooldown as elapsed time; set to 4 at `world_state.py:10174`. Bonus: both print the raw nation KEY. |
| FA-98 | REPRODUCED | `dispatch.py` and `campaign_log.py` contain **zero** `scenario_name` references; the archived tutorial digest line 55 reads "Sire - Ney, crowned four turns ago, has been beaten in the field." |
| FA-100 | REPRODUCED (half a); the row is a CHIMERA | `threat_sources_this_turn` = 4 after end_turn, `from_dict` restores 4, `load_game` wipes to 0. The row's `_corrected` describes a DIFFERENT defect (a `command_clarification` surviving from_dict) - see the warning below. |
| FA-101 | REPRODUCED (docs-only) | FOUR live sites claim "owner = row WO slice 12"; row WO is closed and slice 12 landed with no objection work. `main.py` site is at **:4487**, not :4120. |

Nothing in this set is REFUTED outright except **FA-67's headline**, and
**FA-65's "full dead zone"** sub-claim. **FA-52** is substantially a
duplicate of **FA-49** (see below).

---

## Per row

Grouped by file, for file-by-file landing.

---

### `backend/game_logic/battle_report.py`

#### FA-44 - the terrain verdict has no scale gate

**Probe** `p1_reports.py`. Sept-2 verdict NARROWED; `_corrected` read first.

```
=== FA-44 ===
  obs: Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  obs: Massena held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
```
(input: attacker_casualties 1, defender_casualties 58, defender_original_strength 58,
defender terrain bonus 20, player France defending)

**Verdict: REPRODUCED.** The mechanism is exactly as `_corrected` states.

(a) **True seam by symbol:** `battle_report._pick_observation`, the loss
ladder. Today: priority 1 `mutual_destruction` (`:812`), priority 2 fort
(`:817-822`), priority 3 stance (`:825-831`), **priority 4 terrain
(`:834-838`)**. `_mod_value(their_mods,"terrain","bonus") >= 15` and
`_mod_value(our_mods,...)` are the only conditions; `attacker_casualties`
and `defender_casualties` are already bound in scope at `:635-636` and
never consulted. Banks at `:333-342`.

(b) **What the filed fix would break:** the fix shape says "at the top of
the loss ladder ... before :818". That position is ABOVE the two
fortification arms (priority 2). A sub-1000 loss against a fortified
enemy would then print a "skirmish" line instead of the fort verdict, and
the fort verdict is arguably the MORE informative one for a tiny action
(you attacked works and bounced). The floor belongs at priority 4 only,
or between 3 and 4 - not at the head of the ladder. Also note the
`_corrected` text itself says "before line 815, priority 2" while
`fix_shape` says "before :818" - the two disagree by one priority tier.

(c) **Minimal correct fix:** in `_pick_observation`, immediately before
the priority-4 terrain pair, `if we_lost and (attacker_casualties +
defender_casualties) < 1000: return _fill(random.choice(
_OBSERVATIONS["lost_skirmish"]))` with a new bank. Do NOT touch
priorities 1-3.

(d) **Existing pins:** none flip. Every `_pick_observation` fixture I
found uses 5,000-25,000 casualties (`tests/test_battle_report.py`,
`tests/test_pt_d_battle_report.py`,
`tests/test_creative_audit_ca8_2026_08_04.py`). A new bank name must be
added to any bank-count census if one exists (I found none).

**Unresolved:** the Sept-2 note "a same-audit sibling already owns half of
it" does not resolve against the visible rows. FA-9 (the 1,218-man
remnant taking provinces) is adjacent but is a movement/retreat-doctrine
row, not a narration row. Whoever lands this should re-read FA-44's
`player_consequence` field (not in my extract) before writing the fix.

---

### `backend/game_logic/naval.py` + `backend/commands/naval_executor.py`

Four rows land together; they touch two files and share the "the naval
surface says the smaller of two true things" through-line.

#### FA-45 - `build ships` blames green crews for blockade rot

**Probe** `p2_naval.py`.

```
France ships/readiness before: 45 70
self_blockaded_by: Britain
msg: A keel is laid at Bordelais (400g). The fleet stands at 46 sail - readiness 69
     (new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
after: 46 69
```

**Verdict: REPRODUCED** exactly as filed (Sept-2 VERIFIED). The fold cost
is 1 point (70 -> 69); `_readiness_tick` will take 5 more at the turn
boundary. `NEW_SHIP_READINESS = 40`, `READINESS_TICK = 5` (`naval.py:49`,
`:78`).

(a) **Seam:** `NavalExecutor._execute_build_fleet` message at
`naval_executor.py:89-95`; the figure comes from `naval.lay_down_ship`
(`naval.py:2028-2047`) which returns only `{ships, readiness}`.

(b) **What the filed fix would break:** nothing structural, but "have
`lay_down_ship` return `readiness_before`" is a signature change on a
function with a second caller shape (the `ships <= 0` early-return arm at
`:2035-2042` returns a 2-key dict). Add the key to BOTH return dicts or
the executor's `outcome['readiness_before']` KeyErrors on a first keel.

(c) **Minimal correct fix:** `lay_down_ship` adds `"readiness_before"` to
both returns; the message quotes `(-N from the green crew` and, when
`naval.blockade_forecast(world, actor).get("self_blockaded_by")`, appends
the rot from the same single source the blockade order reads
(`naval.blockade_forecast_sentence` already exists at the posture seam).

(d) **Existing pins:** `tests/test_naval_substrate.py::TestBuild...
::test_build_costs_gold_and_folds_green_crews` (:238) - reads gold and
the fold, not the sentence; would not flip. No test asserts the
green-crew clause text (grep "only sea-time" in tests: 0 hits outside a
source census in `test_wo_slice6_the_admiralty_speaks_plainly.py:436`,
which slices on "The Grand Diversion is drawn up" and is unaffected).

#### FA-51 - the expedition gate order

**Probe** `p2_naval.py`.

```
Soult at Lorraine strength 30000 EXPEDITION_MAX_TROOPS 15000
msg (not at a yard): An expedition assembles at a dockyard, Sire - Soult must stand at
  one of our yards: Bordelais, Brittany, Flanders, Provence.
msg (at a yard): The transports lift 15,000 men; Soult commands 30,000 - 15,000 too many.
  He cannot be lightened: a garrison detaches a fixed 3,000, and we already hold our 3
  (3 of 3 in all). Send a corps of 15,000 or fewer instead - Napoleon stands at 10,000.
```

**Verdict: REPRODUCED** (Sept-2 VERIFIED). Both halves.

(a) **Seam:** `NavalExecutor._execute_naval_expedition`. Embark-position
gate at `naval_executor.py:290-302`; lift gate at `:308-316`.
`troops = int(marshal.strength)` at `:304` is unconditional and no seam
in `parser.py` / `validation.py` / `llm_client.py` reads a troop count
for `naval_expedition`.

(b) **What the filed fix would break:** reordering blind would put the
lift gate above the **inland-abroad** check at `:298-302` ("the boats
cannot reach him"). For a 30,000-man corps standing inland on foreign
soil the player would then be told about the lift and never about the
coast, which is the same defect mirrored. The lift gate must go above
the YARD arm only (`:290-296`), below the inland arm - or, better, both
refusals get composed into one sentence.

(c) **Minimal correct fix:** hoist the `troops > EXPEDITION_MAX_TROOPS`
block to just above `:290` and keep the inland check where it is
(reorder to: target resolve -> lift -> inland -> yard); when
`re.search(r'with\s+([\d,]+)\s*(men|troops)', raw)` matches, append "the
transports take a whole corps - there is no verb to embark N of M".

(d) **Existing pins:** `tests/test_wo_slice6_the_admiralty_speaks_plainly.py`
owns the over-lift SENTENCE (unchanged by a reorder);
`tests/test_naval_substrate.py`, `test_naval_channel_gate.py`,
`test_naval_free_ireland.py`, `test_naval_host_rule.py` drive the
expedition. Any test that stages a too-big corps NOT at a yard and
asserts the yard sentence would flip - I found none, but the landing
should grep `must stand at one of our yards` across `tests/` first
(2 hits, both in `test_naval_ui_clarity.py`-adjacent chip tests as of
this read).

#### FA-58 - the blockade "floor" RAISES a beaten fleet

**Probe** `p1_reports.py`.

```
blockaded nations: ['France', 'Holland', 'Spain']
France readiness 40 ->  50
France readiness 45 ->  50
France readiness 70 ->  65
```

**Verdict: REPRODUCED** (arithmetic, Sept-2 VERIFIED).

(a) **Seam:** `naval._readiness_tick`, `naval.py:1673-1677`:
`readiness = max(READINESS_BLOCKADE_FLOOR, readiness - READINESS_TICK)`.
Reachable states below 50 are minted by
`naval.diversion_failure_readiness` (`:1555-1565`, `max(40, r-20)`), the
expedition turn-back at `:1509-1511` (same shape), and `lay_down_ship`'s
`max(READINESS_MIN, ...)` at `:2045`.

(b) **What the filed fix would break:** nothing. `max(min(readiness,
FLOOR), readiness - TICK)` is correct and I checked both live pins:
`test_naval_substrate.py::TestReadinessTick::test_blockaded_fleet_rots_to_the_floor`
starts at 70 and ticks 6 times (70,65,60,55,50,50,50) - still 50, green;
`test_naval_descent.py::TestAdvanceTurnWiring::test_the_admiralty_tick_runs_inside_advance_turn`
asserts `r0 - READINESS_TICK` from 70 - green.

(c) **Minimal correct fix:** the one line as filed.

(d) **Existing pins:** the two above; both stay green (verified by hand
against their own fixtures - neither ever puts a blockaded fleet below
50).

#### FA-59 - the fleet-action loss line sums the pooled allies

**Probe** `p3_fleet_action.py`.

```
message: The diversion is caught coming home - the fleet is brought to battle at bad
         readiness and loses 49 sail. A decisive defeat: ...
losses dict: {'France': {'France': 25, 'Spain': 17, 'Holland': 7},
              'Britain': {'Britain': 4, 'Russia': 1}}
ships before: France 45 ... after: France 20
France OWN loss: 25
dispatch event: trafalgar {... 'loser_ships_lost': 49}
```

**Verdict: REPRODUCED verbatim** (Sept-2 VERIFIED, and the scope IS
wider than the title: the dispatch beat carries it too).

(a) **Seam:** `naval._apply_side_losses` (`naval.py:1317-1345`) returns a
per-MEMBER dict; `naval.resolve_fleet_action` (`:1275-1278`) stores it
under one SIDE key. Two consumers sum it:
`naval.resolve_diversion` at **`naval.py:1618`**
(`ships_lost = int(sum(action["losses"].get(nation, {}).values()))`) and
`naval._log_fleet_action` at **`naval.py:1366`**
(`"loser_ships_lost": int(sum(result["losses"].get(result["loser"], {}).values()))`),
which feeds `dispatch.py:3963` / `:3968`. A third,
`naval_executor.py:453`, is the expedition-intercept message and does the
same sum for the mover's nation.

(b) **What the filed fix would break:** "add `own_lost`/`allied_lost` to
the result" is fine, but doing it at three call sites (as `fix_shape`
literally reads) re-creates the one-rule-many-implementations pattern.
The Sept-2 note recommending ONE helper is right and I confirm no such
helper exists (`grep own_ships_lost backend/` = 0).

(c) **Minimal correct fix:** new pure `naval.own_ships_lost(action,
nation) -> int` and `naval.allied_ships_lost(action, nation) ->
Dict[str,int]`; all THREE sites call it. The diversion message and the
`trafalgar`/`fleet_action` template gain the allies' figures separately.
The `display_nation(loser)` half of the fix shape is a separate copy fix
and can ride along (`_action_waters` already imports `display_nation`).

(d) **Existing pins:** `tests/test_naval_descent.py` drives
`resolve_diversion` (:198, :209, :217) but asserts on `success` /
`window` / `diversion_used`, not on the sail figure;
`tests/test_naval_diorama.py` reads `action["losses"]` structurally.
I found no test asserting "loses N sail". Nothing flips.

#### FA-64 - the typed Grand Diversion confirm drops the camp warning

**Probe** `p2_naval.py`.

```
camp_staged(France): False
confirm msg: The Grand Diversion is drawn up, Sire - once, and once only, this war.
  The fleet sails to draw the enemy squadrons off station: 45 times in 100 the strait
  opens for 2 turns; otherwise she is caught coming home and fights at readiness 59.
  Sail? (yes / no)
chip: {'command': 'order the diversion', ..., 'note': '45% - and once only, this war;
        no army is staged to use the open water'}
```

**Verdict: REPRODUCED** (Sept-2 NARROWED - two surfaces for the same
irreversible action disagree; that is the whole of it).

(a) **Seam:** the chip note is inline inside `naval.build_admiralty_report`
at `naval.py:2389-2395`; the typed confirm is
`NavalExecutor._execute_naval_diversion` at `naval_executor.py:606-614`.

(b) **What the filed fix would break:** nothing, provided the extraction
keeps the chip's `note` string byte-identical -
`tests/test_naval_host_rule.py:461` asserts `"no army is staged" in
diversion["note"]` and `:477` asserts it is ABSENT when a camp is
staged. A refactor that moves the phrase into a helper must keep both
directions.

(c) **Minimal correct fix:** extract `naval.diversion_note(world, nation)
-> str` returning the same "45% - and once only, this war[; no army is
staged ...]" string; `build_admiralty_report` calls it for `note`, and
`_execute_naval_diversion` appends its camp clause to the confirm
message.

(d) **Existing pins:** `test_naval_host_rule.py:461` and `:477` (both
stay green if the string is preserved);
`test_wo_slice6_the_admiralty_speaks_plainly.py:436` slices the SOURCE
on the literal `"The Grand Diversion is drawn up"` - keep that phrase as
the confirm's opening or that census breaks.

---

### `backend/commands/strategic.py` (+ `interrupt_popup.gd`)

#### FA-49 - the interrupt popup never shows its trust costs
#### FA-52 - obeying is taxed; a HOLDing marshal "continues the march"

One probe covers both: `p8b_cannon.py`.

```
order type: HOLD personality cautious
proc: {'marshal':'Davout','command':'HOLD','interrupt':'cannon_fire',...,
       'message': "Davout: 'Cannon fire at Franconia, Sire. Investigate?'",
       'options': ['investigate','continue_order','hold_position']}
message: Davout reluctantly continues the march, ignoring cannon fire at Franconia.
         Davout fortifies Rhineland.
trust 85 -> 83 | trust_change -2
order still: HOLD
report keys: ['battle_location','command','interrupt','interrupt_type','marshal',
              'message','options','requires_input']
```

The battle I recorded was **Blucher vs Hohenlohe** - neither belligerent
is France's - and the ask still fired.

**Verdict: BOTH REPRODUCED. FA-52's trust half is a DUPLICATE of FA-49**
(same seam, same numbers, same re-ask window). FA-52's unique residue is
(i) the fixed "continues the march" copy under a HOLD/SUPPORT order,
(ii) the free `investigate` (which CANCELS the order) versus the taxed
obedient arms, and (iii) the nation-blind trigger. Land them as ONE
slice; do not file two.

(a) **True seams by symbol** (all line numbers in the row are stale by
~660):
- `StrategicOrderProcessor._respond_cannon_fire`, `strategic.py:1231`.
  `continue_order` arm `:1353-1374` (`trust_change = -2` at `:1355`),
  `hold_position` arm `:1376-1393` (`-3` at `:1383`), `investigate` arm
  `:1238-1352` (`trust_change = 0`, never modified).
- The copy: `strategic.py:1367-1368`, `f"{marshal.name} reluctantly
  continues the march, ..."`. `_strategic_command_flavor` already exists
  at `strategic.py:28` and is used in the `investigate` and
  `hold_position` arms but NOT here.
- The re-ask window: `StrategicOrderProcessor._check_interrupts`,
  `strategic.py:3309`; suppression `ignored_turn >= world.current_turn - 1`
  at `:3327`; the nation-blind scan `world.get_battles_within_range(
  marshal.location, 2)` at `:3331` skips only battles the marshal
  himself is in.
- The renderer: `godot-client/.../interrupt_popup.gd`, `OPTION_LABELS`
  at `:23-36`, `btn.text = OPTION_LABELS.get(option_id, ...)` at `:70`.

(b) **What the filed fixes would break:**
- FA-49's `option_costs` shape must be built at EVERY interrupt report
  builder, not just the cannon-fire one - the blocked-path builders
  charge -3 too. If only the cannon-fire builder emits it, the popup
  renders costs on one interrupt type and not another, which is worse
  than none. Also `options` today is a **list of strings**; a dict of
  costs keyed by option id is additive and safe, but a naive change to
  a list of dicts would break `interrupt_popup.gd`'s `for option_id in
  options` loop AND `strategic.py`'s own `choice in pending["options"]`
  validation.
- FA-52's "charge 0 for HOLD/SUPPORT" arm is a **mechanics** change on a
  serialized trust value and is exactly the kind of thing that moves
  `BASELINE_SERIES` if any AI marshal ever answers a cannon-fire ask.
  I did NOT verify whether the AI ever reaches `_respond_cannon_fire`
  (the ask is a player question), but the trust write is on
  `marshal.trust`, which is read by the objection/defiance channel.
  Treat the number as a design question and land only the COPY half
  unless the user rules.

(c) **Minimal correct fix (copy-only, safe):**
1. `strategic.py:1367` -> key the sentence on
   `_strategic_command_flavor(order.command_type)`: "keeps his position,
   ignoring cannon fire at X" for HOLD, "continues the march" for
   MOVE_TO/PURSUE.
2. Every interrupt report builder in `strategic.py` adds
   `"option_costs": {"investigate": 0, "continue_order": -2,
   "hold_position": -3}` built from the SAME constants the arms spend
   (extract them to module constants first - they are inline literals
   today).
3. `interrupt_popup.gd:70`: append ` (trust -N)` when
   `interrupt_data.get("option_costs", {})` carries the id.

(d) **Existing pins:** grep across `tests/` for `"reluctantly continues"`
returns 0 hits and for `cannon_fire` returns hits only in
`test_strategic_*` / FA-slice-3 files that assert on `action_taken` and
`order_cleared`, not on the sentence. `interrupt_popup.gd`'s
`OPTION_LABELS` is not censused. Nothing flips for the copy-only fix.

**Flags:** touches a `.gd`. The trust-number half would change a
serialized value and needs a ruling.

---

### `backend/models/world_state.py`

#### FA-56 - the Rebuke's intel pause is dead

**Probes** `p1_reports.py` (positive) and `p2_naval.py` (control).

```
Soult personality: literal
paused==current_turn; scouted sector regions: ['Swabia', 'Brabant']
reader name in code reads '_literal_intel_paused_turn': False
--- control ---
Soult at Lorraine sector ['Lorraine','Swabia','Rhineland','Franche-Comte','Orleanais','Nivernais','Brabant']
with the UNDERSCORE field set,  scouted: []
with the SERIALIZED field set,  scouted: ['Swabia','Brabant']
```

**Verdict: REPRODUCED, with a falsifiable control in both directions.**

(a) **Seam:** `WorldState.calculate_visibility`, the Vindicated Garrison
block, `world_state.py:2894-2925`. Line **2902**:
`if getattr(marshal, "_literal_intel_paused_turn", None) == turn:`.
`turn = self.current_turn` (`world_state.py:2735`). The writer is
`jealousy.py:2724` `marshal.literal_intel_paused_turn = int(
world.current_turn) + 1` - so a stamp made on turn N matches the pass
run at the start of turn N+1. The field is serialized at
`marshal.py:663 / 1661 / 1857`.

(b) **What the filed fix would break:** nothing. The default must be `-1`
(not `None`), matching `marshal.py:663`, so the very first visibility
pass on a turn-(-1) world cannot accidentally match.

(c) **Minimal correct fix:** `world_state.py:2902` ->
`if getattr(marshal, "literal_intel_paused_turn", -1) == turn:`.

(d) **Existing pins:** `tests/test_ca9_row3_phase_a.py:376`
```
        for dead in ("_jealousy_rebuked_cycle", "_literal_intel_paused_turn"):
            assert dead not in vars(m)
```
This pin is what PROVES the reader is dead and it stays green under the
fix (we change the reader, not the field). No test drives the pause
behaviourally - `grep -rln "literal_intel" tests/` returns only
`test_ca9_row3_phase_a.py` and the two playtest fixtures.

#### FA-67 - "give him a battle he can win"

**Probe** `p4_misc.py`.

```
[!] Lannes's trust is faltering (38). Trust his judgment when he objects, and give him
    a battle he can win - at 20 he will ask to be released.
expectation before a win: 0
expectation after  a win: 40
```

**Verdict: REFUTED as headlined.** A won battle DOES add trust. The chain
the row's grep missed:
`combat_executor.py:2646` (post-combat pipeline step 11) calls
`world.vindication_tracker.resolve_battle(marshal_name=attacker.name,
result="victory", ...)`; `VindicationTracker.resolve_battle`
(`vindication.py:69`) 'trust' + 'victory' arm sets `trust_change = +3`
(`vindication.py:118-121`) and applies it at `vindication.py:194`
`actual_trust_change = marshal.modify_trust(trust_change)`.
So the warning's two clauses are the two STAGES of one mechanic, in the
right order - the Sept-2 reading is correct and the row's census is
wrong because it looked for a trust write *inside* the combat files.

**What survives (narrow, real):**
1. The mechanic fires only when `has_pending(attacker.name)` - i.e. the
   marshal objected AND the player answered trust/compromise - and only
   for the **attacker**, and only `if not is_bombardment`. A marshal who
   objects and then wins on the DEFENSIVE earns nothing. The advice never
   says the objection is the prerequisite.
2. Measured: a win raises `dotation.get_expectation` from 0 to 40, so for
   an ES-7 eroding marshal the same victory deepens the shortfall that is
   eroding him. +3 (conditional) against a 40-point expectation rise.

(a) **Seam:** `WorldState._check_trust_warnings`, message at
`world_state.py:12127-12131`; the false-in-context comment at
`:12122-12125` ("a won battle is the reliable earner").

(b) **What the filed fix would break:** it says "delete the battle
clause". That would delete the ONLY true half. Deleting it makes the
warning name a single lever that by itself never pays (trusting an
objection with no battle resolves nothing - `resolve_battle` is the only
consumer of `pending`).

(c) **Minimal correct fix:** re-word to state the dependency rather than
delete it - "Trust his judgment when he objects, and let him win the
battle he asked for" - and, when `dotation.is_eroding(marshal, self)`,
append the reward remedy. The comment at `:12122-12125` should be
corrected to name `VindicationTracker` so the next census does not repeat
this.

(d) **Existing pins:** `grep -rn "give him a battle he can win" tests/`
= 0 hits. Nothing flips.

#### FA-61 - "if all march" is not a ceiling (seam is `combat_executor.py`)

**Probes** `p6_muster.py`, `p6b_muster.py`, `p6c_muster_math.py`.

```
MUSTER - Ney (24,000; 78,676 if all march) vs Mack (large force) at Swabia ...
  WILL JOIN Davout / WILL NOT Soult / WILL JOIN Lannes / WILL JOIN Murat /
  WILL NOT Bernadotte / WILL JOIN Napoleon
reinforcement_messages:
  "Davout's forces arrived ...", "Soult awaits explicit orders ...",
  "Lannes's forces arrived ...", "Murat could not reach the battlefield in time.",
  "Bernadotte hesitated ...", "Napoleon's forces arrived ...",
  "Massed effective strength: 24,000 (lead) + 60,266 committed
   (Davout, Lannes, Napoleon) = 84,266."
--- the arithmetic ---
preview (expected_at=region), 4 candidates: 54676.7 -> total 78676.7
ceiling (expected_at=None),   4 candidates: 66172.5 -> total 90172.5
resolver-semantics over the THREE who actually arrived: 54787.5
  Davout arrival_weight 0.976 / Lannes 0.950 / Murat 0.176 / Napoleon 0.950
```

**Verdict: REPRODUCED, and the causal story is INCOMPLETE - there are TWO
causes, not one.** `54787.5 x 1.10 = 60266.25`, which is the resolved
figure to the digit. The second cause is the **sovereign presence aura**:
`combat_executor.py:672-682` stamps `m.sovereign_presence =
sovereign_aura_strength(world, m.nation)` on every participant at RESOLVE
time, and `Marshal.get_attack_modifier` reads it. At PREVIEW time the
stamp is 0.0, so `_committed_reinforcement_strength` under-prices every
joiner by 10% whenever the Emperor marches.

(a) **True seams by symbol:**
- label: `CombatExecutor._format_muster_lines`, `combat_executor.py:1488`
  (built `:1494-1503`, emitted `:1504-1511`).
- number: `CombatExecutor._build_muster_preview`,
  `combat_executor.py:1219` (`"committed_strength": int(marshal.strength
  + committed_attacker)`), fed by
  `CombatExecutor._committed_reinforcement_strength`
  (`combat_executor.py:452`, the `expected_at` arm at `:506-508` and
  `_expected_arrival_weight`).
- the missing +10%: `combat_executor.py:672-682`.

(b) **What the filed fix would break:** it does NOT deliver what the row
itself quotes. `_committed_reinforcement_strength(..., expected_at=None)`
at preview time returns **90,172**, but the resolver with all four
arriving under the aura reaches **96,790** - which is the "up to 96,000"
the row's own suggested sentence names. So the prescribed
`ceiling_strength` would print a "ceiling" the game can exceed by 7%,
re-creating the exact defect one layer up. It is a shown != applied fix
that ships a new shown != applied.

(c) **Minimal correct fix:** compute the ceiling on the SAME modifier
basis the resolver uses - i.e. stamp `sovereign_presence` (or pass an
aura multiplier) into the preview's `_committed_reinforcement_strength`
call, then expose BOTH figures: `"~78,676 expected; up to 96,790 if every
corps arrives"`. Cheapest honest alternative if the aura threading is too
invasive for a P3: change the LABEL to "expected" and drop the ceiling
claim entirely - the number is already correct for what it measures.

(d) **Existing pins:** `grep -rn "if all march" tests/` - the phrase is
asserted in the CA9/PT-A2 family. The label text is load-bearing there;
changing it to "expected" flips those. The landing must grep first
(`tests/test_creative_audit_ca9_2026_08_08.py`,
`tests/test_pt_*` are the likely owners). Adding a SECOND clause after
the existing one is the change least likely to flip a pin.

**Flag: this row changes a displayed number derived from AI-visible
state but not an AI decision** - `committed_strength` is preview-only
(the resolver has its own call), so no `BASELINE_SERIES` work. Confirmed
by reading `_build_muster_preview`'s only consumers.

---

### `backend/game_logic/vassal.py` (+ `diplomatic_ledger.py`)

#### FA-65 - the recovery hint's band

**Probes** `p4_misc.py`, `p5_vassal_ledger.py`.

```
process_vassal_loyalty: at 41 -> 39, recovery_hint ''
                        at 38 -> 36, recovery_hint ''
diplomatic_ledger vassals tab, Switzerland:
  loyalty 45: recovery_hint ''            warning ''
  loyalty 39: recovery_hint 'Invest in them, grant them autonomy, garrison their
              capital, or cede them a province to steady them.'   warning 'warning'
  loyalty 36: (same)
  loyalty 30: (same)
```

**Verdict: REPRODUCED for the gate; the "full dead zone" claim is
REFUTED.** There are THREE producers, and the third has the INVERSE gate:

| producer | symbol | gate |
|---|---|---|
| per-turn drift line | `vassal.process_vassal_loyalty`, `vassal.py:711` | `delta < 0 and new_loyalty >= 40` |
| Talleyrand advisory | `dispatch.py:3435` | `loyalty < 35` (3-turn cooldown) |
| **VASSALS ledger tab** | `diplomatic_ledger.py:683-684` | `loyalty < 40` |

So loyalty 35-39 is NOT a hole: the ledger tab carries the hint there.
The true, narrower defect is that both **passive** surfaces - the line
that scrolls past during the turn and the `diplomatic_vassal_unrest`
dispatch template (`dispatch.py:3808`, "Talleyrand reports unrest in
{nation}.") - go silent exactly at the band where action is needed, and
the remedy survives only on a tab the player must open.

(a) **Seam:** `vassal.process_vassal_loyalty`, `vassal.py:710-712`.
Constants `BRIBE_ELIGIBLE_LOYALTY = 35`, `BRIBE_SPIRAL_LOYALTY = 50`
(`vassal.py:73-74`).

(b) **What the filed fix would break:** "drop the >= 40 clause" makes the
hint fire on EVERY negative delta at any loyalty, including a satellite
at 98 losing 1 - which is the noise the `>= 40` band was added to bound
in the other direction. It also duplicates the ledger row verbatim at
every band below 40, so the two surfaces would say the same sentence and
the ledger's gate becomes redundant.

(c) **Minimal correct fix:** change the gate to
`if delta < 0 and new_loyalty >= vassal.BRIBE_SPIRAL_LOYALTY` for the
"healthy drift" reminder AND add a distinct, urgent variant below 40
(the ledger's own string is already there and single-sourced through
`recovery_hint_for_grip`), plus attach `recovery_hint` to the
`diplomatic_vassal_unrest` template vars at `vassal.py:734-736`.

(d) **Existing pins:** `tests/test_vassal_recovery_lever.py` (VS-1's own
9 tests) owns the `>= 40` gate; grep it before landing - at least one
test almost certainly asserts the hint is EMPTY below 40 or PRESENT
above. `tests/test_ui6_interaction_sweep.py` owns the ledger VASSALS tab
rows.

---

### `backend/commands/capture_executor.py` (+ `capture_choice_dialog.gd`)

#### FA-69 - the estate stage prints the raw marshal key

**Probe** `p9_estate.py`.

```
message: Ney secures Bohemia.

Sire - Bohemia sustains Marshal ArchdukeCharles's household (the Duchy of Bohemia).
Confiscate the estate (+400 gold; Austria will not forgive it) or respect the title
(Austria will remember the courtesy)?
estate_holder: ArchdukeCharles | nation: Austria
_pending_prompt: the fate of Marshal ArchdukeCharles's estate at Bohemia awaits your
word: 'confiscate' or 'respect'.
```

**Verdict: REPRODUCED verbatim.** The Sept-2 note that the enumeration is
too narrow is correct - I count **FOUR** sites, not two:

1. `capture_executor.py:235` - the mount sentence (`Marshal {holder.name}`),
   which in the SAME f-string routes the nation through `formed_display_name`.
2. `capture_executor.py:186` - `CaptureExecutor._pending_prompt`, the
   stale/wrong-token restatement.
3. `backend/commands/executor.py:1097` - the blocking message ("You must
   decide the fate of Marshal {estate_holder}'s estate...").
4. `capture_choice_dialog.gd:60` - `region_label.text = "%s sustains
   Marshal %s's household"`.

Plus the client-side nation gap: `capture_choice_dialog.gd:62-63` render
`estate_holder_nation` raw (never `Utils.display_nation_name()`), so a
formed nation would print its dead tag on the buttons while the backend
sentence beside them prints the formed name.

(a) **Seam:** `CaptureExecutor._maybe_mount_estate_choice`,
`capture_executor.py:200-247` (the producer).

(b) **What the filed fix would break:** nothing, IF `estate_holder` stays
the machine key - `_handle_estate_choice` re-reads it at
`capture_executor.py:256` (`world.marshals.get(pending["estate_holder"])`)
and a humanised key would fail that lookup and produce "The estate
question has lapsed."

(c) **Minimal correct fix:** add `estate_holder_display =
humanize_entity_name(holder.name)` and `estate_holder_nation_display =
formed_display_name(world, holder.nation)` to `estate_pending`; use the
display forms at all three backend sentences; `capture_choice_dialog.gd`
reads the `_display` keys with a fallback to the raw ones. `_pending_prompt`
and `executor.py:1097` read `pending.get('estate_holder_display') or
pending.get('estate_holder')`.

(d) **Existing pins:** the `dialogue_id` and `estate_holder` keys are
asserted in the W6-8 / IGR-E families
(`tests/test_igr_e_plunder_prompt.py`, `tests/test_wo_slice15_*`).
Adding keys is additive; nothing flips. Any pin asserting the exact
sentence "sustains Marshal ArchdukeCharles's household" would flip -
grep `sustains Marshal` before landing.

**Flags:** touches a `.gd`; adds two display-only keys to a **serialized**
dict (`world.pending_capture_choice` round-trips), so the new keys must be
`.get()`-safe on a pre-fix save.

---

### `godot-client/project-sovereign/scripts/war_detail_popup.gd`

#### FA-70 - Enemy War Exhaustion printed twice, or never

Source read (no Godot run):

```gdscript
423	# War exhaustion
424	if we != null:
...
431		bbcode += "Enemy War Exhaustion: [color=" + we_color + "]" + str(we_int) + "[/color]\n"
432
433	# NV-12 (recon gap 8): the per-belligerent fleet line ...
436	var naval_line = str(w.get("naval_line", ""))
437	if naval_line != "":
438		bbcode += "Their fleet: " + Utils.humanize_nation_keys_in_text(naval_line) + "\n"
439	else:
440		bbcode += "Enemy War Exhaustion: [color=" + COLOR_DIMMED + "]Unknown[/color]\n"
```

**Verdict: REPRODUCED at source, exactly at the cited lines** (Sept-2
VERIFIED). `if we != null:` (424) closes at 431 with no `else`; the
`else:` at 439 binds to `if naval_line != "":` (437).

(a) **Seam:** `war_detail_popup.gd::_render_war_detail`.

(b) **What the filed fix would break:** nothing, but the fix must ALSO
keep the `Their fleet:` line reachable when `we == null`. Naively nesting
the naval block inside `if we != null:` would hide the fleet line for a
fogged opponent, which is the reverse regression.

(c) **Minimal correct fix:** move `else: ... Unknown` up to be the `else`
of `if we != null:` (i.e. insert it after line 431), and leave the naval
block at 436-438 as a standalone `if` with no `else`.

(d) **Existing pins:** `tests/test_naval_ui_clarity.py::TestClientSurfaces
::test_war_detail_consumes_naval_line` (:273-276) asserts
`"naval_line" in gd` and `"Their fleet:" in gd` - a text census, stays
green.

**Flag: `.gd`-only. Boot the engine (grep `SCRIPT ERROR`) before landing
per the XR-1 rule.**

---

### `backend/commands/tactical_executor.py`

#### FA-93 - "breaks formation to attacks"

**Probe** `p1_reports.py`.

```
'\n[Square broken - Ney breaks formation to attacks]'
'\n[Square broken - Ney breaks formation to moves to]'
'\n[Square broken - Ney breaks formation to fortifies]'
```

**Verdict: REPRODUCED verbatim** (Sept-2 VERIFIED).

(a) **Seam:** `TacticalExecutor._auto_break_square`,
`tactical_executor.py:496-497`:
```
display = _action_display_name(action_name) if action_name else "act"
msg = f"\n[Square broken - {marshal.name} breaks formation to {display}]"
```
`ACTION_DISPLAY` is third-person-present (`display_names.py:17-30`).
Consumed at `executor.py:2493-2494` and rendered by `main.gd::_display_result`.

(b) **What the filed fix would break:** adding an INFINITIVE map to
`display_names.py` risks a future caller picking the wrong map; and
`ACTION_DISPLAY` is a shared single source whose other consumers
(campaign log, objection dialog) need the third-person form. Do NOT
change `ACTION_DISPLAY` itself.

(c) **Minimal correct fix:** the second option in the row's own fix
shape is strictly better and touches one line:
`f"\n[Square broken - {marshal.name} breaks formation and {display}]"`.
No new map, no new single source, correct for every entry in
`ACTION_DISPLAY` ("and attacks", "and moves to", "and fortifies").
Consider `humanize_entity_name(marshal.name)` in the same line for the
AI copy (dead on screen today, live in the digests).

(d) **Existing pins:** `grep -rn "breaks formation" tests/` = **0 hits**.
Nothing flips. (Note FA-N47 in the FA-N set owns the fact that this
notice is DROPPED on a refused action - the two rows touch the same
string and should be landed together or the copy fix will be invisible.)

---

### `backend/commands/diplomatic_executor.py`

#### FA-95 - "rejected our last proposal only 1 turns ago"

Source read:

```python
689	cooldowns = getattr(world, 'player_proposal_cooldowns', {})
690	if target_nation in cooldowns and cooldowns[target_nation] > 0:
691	    remaining = cooldowns[target_nation]
...
694	   "message": f"Talleyrand advises patience, Sire. {target_nation} rejected our
                    last proposal only {remaining} turns ago.",
...
703	   "message": f"Talleyrand advises patience, Sire. {target_nation} rejected our
                    {_proposal_display_name(proposal_type)} proposal only {remaining} turns ago.",
```

`world.player_proposal_cooldowns[target] = 4` is written at
`world_state.py:10174` (and `:9971`, `:10211`) on rejection and
decremented by `CooldownManager.decrement_all`.

**Verdict: REPRODUCED at source** (Sept-2 VERIFIED). The value counts
DOWN to the moment you may ask again.

(a) **Seam:** `DiplomaticExecutor._execute_diplomatic_propose`,
`diplomatic_executor.py:686-704` (two f-strings). The correct sibling
idiom is already in the same file at `:3124-3125`: "we must wait
{ult_cd} more turns".

(b) **What the filed fix would break:** nothing found. But note the
fix shape's replacement string drops the word "only", and
`tests/test_bb4_grievance.py:579` asserts
```
assert "only" in result["message"] and "turns ago" in result["message"]
```
- that pin is on the **Make Amends** refusal
(`reparations_cooldown`), a DIFFERENT message in a different file, so it
does not flip; but the same "only N turns ago" idiom is used there and
whoever lands this should check whether that one has the same inversion
(it reads a cooldown too).

(c) **Minimal correct fix:** both f-strings ->
`f"Talleyrand advises patience, Sire. {display_nation(target_nation)}
refused us; the court will not receive another envoy for {remaining} more
turn{'s' if remaining != 1 else ''}."` The `display_nation` call is a
free bonus fix: today both strings print the raw key
(`KingdomOfItaly`, `PapalStates`).

(d) **Existing pins:** `grep -rn "advises patience" tests/` = 0 hits.
Nothing flips.

---

### `backend/game_logic/dispatch.py`

#### FA-98 - the crown beat leaks into the School

Source + archived evidence:

```
$ grep -c scenario_name backend/game_logic/dispatch.py backend/campaign_log.py
backend/game_logic/dispatch.py:0
backend/campaign_log.py:0

docs/audits/playtest_digests/audit-tutorial/digest.md:55
- DISPATCH: Sire - Ney, crowned four turns ago, has been beaten in the field.
```

**Verdict: REPRODUCED** (Sept-2 VERIFIED; the digest line is verbatim).

(a) **Seams:** `dispatch._compose_reversal_line`, the crown appositive at
`dispatch.py:1311-1317`; the arc builder `dispatch._build_marshal_arcs`
reads `glory_crowned` at `:1364`. The sibling producer is
`campaign_log.py:1531` ("stands crowned with glory"). The available
predicate is `jealousy.jealousy_dormant(world)` (`jealousy.py:204-212`,
`return getattr(world, "scenario_name", "") == "tutorial"`).
`jealousy.recompute_crowns` is correctly ungated by design (its docstring
says glory must keep accruing so the Generals screen stays honest).

(b) **What the filed fix would break:** gating on `jealousy_dormant`
inside `_compose_reversal_line` would silence the **whole** reversal
headline in the tutorial when the crown is merely one of two possible
ascents - the estate arm (`endowed with {estate_noun}`) is a separate,
legitimate beat. Gate the CROWN clause, not the line.

(c) **Minimal correct fix:** in `_compose_reversal_line`, treat
`crown_turn` as `None` when `jealousy.jealousy_dormant(world)`; the
existing `elif estate_noun:` arm then produces a correct sentence and the
`else` arm ("unreachable while rose is set") stays unreachable. Mirror it
at `campaign_log.py:1531`.

(d) **Existing pins:**
`tests/test_creative_audit_ca8_2026_08_04.py:795` `assert "three turns
ago" in line` and `:1230` (the run-on pin) both drive the CAMPAIGN world
and would stay green. `tests/test_tutorial_position7.py` /
`test_tutorial_school_fixes_2026_08_08.py` own the dormancy family.

**Routing note:** the Sept-2 verdict and the row itself both argue this
belongs beside **PC15-D3** (the same "shipped-but-untaught producer
speaks into the tutorial" design question, one producer over). It is a
one-line gate if the user rules the same way twice; do not land it as a
unilateral fix if PC15-D3 is still open.

---

### `backend/save_manager.py` (FA-100)

#### FA-100 - `load_game` wipes three fields `from_dict` restored

**Probe** `p4_misc.py`.

```
threat_sources_this_turn after end_turn: 4
after load, threat_sources_this_turn: 0
from_dict alone restores threat_sources: 4
```

**Verdict: REPRODUCED (the title's half).**

**WARNING CONFIRMED - this row is a CHIMERA and its two halves disagree.**
- Half (a): title / summary / repro / **fix_shape** all describe
  `save_manager.py:217/218/240` wiping `mild_concerns_this_turn`,
  `gold_spent_this_turn` and `threat_sources_this_turn`. That is what I
  reproduced.
- Half (b): `_corrected` describes something else entirely - a stale
  `command_clarification` dialogue surviving `from_dict` and eating the
  next command - and asserts "world_state.py:7718-7725 ... is the
  correct seam, **not** save_manager.py:217-240". That sentence rejects
  the fix shape printed two fields below it.

**Both halves are real; they are unrelated defects.** Land half (a) as
the row's title says, and file half (b) as its own row.

(a) **Seams:**
- half (a): `save_manager.load_game`, `backend/save_manager.py:217`
  (`world.mild_concerns_this_turn = []`), `:218`
  (`world.gold_spent_this_turn = {}`), `:240`
  (`world.threat_sources_this_turn = []`). The block's own comment
  already documents FIVE deliberate non-clears citing exactly the
  contract these three violate.
- half (b): `WorldState.from_dict`, the DialogueManager restore at
  `world_state.py:7730-7754`, whose `dm.remove_matching(...)` today
  discards only legacy `conflict_alert` items.
  `"command_clarification"` is a LOCAL_PLANNING type
  (`dialogue_manager.py:145`, `:170`; `clarification.py:30`).

(b) **What the filed fix would break:** deleting the three lines is
correct and consistent with the block's five existing non-clears. Note
`threat_sources_this_turn` is read by three live surfaces
(`diplomatic_ledger.py:992-1000`, `diplomatic_advisory.py:726`,
`main.py:5352`) and refilled mid-turn by the player's own battles
(`combat_executor.py`), so the wipe protects nothing.

(c) **Minimal correct fix:** delete `save_manager.py:217`, `:218`, `:240`
and extend the block comment with the sixth/seventh/eighth entries.

(d) **Existing pins:** `tests/test_ai_intent_threat_migration.py:1062`
`assert world.threat_sources_this_turn == []` - check its context before
landing (it is a turn-boundary clear pin, not a load pin, so it should
stay green). `tests/test_audit_part2.py:124-131` builds threat sources
directly. No test asserts the load-time wipe.

**Flag: half (a) changes what a loaded world contains and therefore what
the AI's coalition/threat surfaces read on the turn after a mid-turn
load. It does NOT change any deterministic turn-boundary value, so
`BASELINE_SERIES` is untouched (the series never loads mid-turn) - but
say so in the landing record rather than asserting it.**

---

### `deploy/README_TESTER.txt` + `docs/TUTORIAL_SCRIPT.md` (FA-81)

```
deploy/README_TESTER.txt:100   Seven marshals stand ready in the east; more can be raised
$ grep -c Napoleon docs/TUTORIAL_SCRIPT.md
0
```
The 1805 boot roster carries eight French marshals; Napoleon appeared in
my own muster probe as a WILL-JOIN candidate at 10,000 men.

**Verdict: REPRODUCED** (Sept-2 NARROWED - the row's
`player_consequence` overstates by one clause; the documentary facts all
hold).

(a) **Seam:** `deploy/README_TESTER.txt:100` and the YOUR MARSHALS block
`:103-130`; `docs/TUTORIAL_SCRIPT.md`.

(b) **What the filed fix would break:** nothing, but the existing pin is
the trap - `tests/test_prebuild_fixes_2026_08_14.py:241`
```
    def test_current_roster_present(self):
        text = self._text()
        for name in ("NEY", "DAVOUT", "SOULT", "LANNES", "MURAT",
                     "BERNADOTTE", "MASSENA"):
            assert name in text, name
```
hardcodes the stale seven and PASSES today. Adding a paragraph does not
flip it; the pin should be strengthened in place to derive the roster
from `europe_1805.json` (the row's own recommendation, and it is right).

(c) **Minimal correct fix:** docs-only, as filed.

(d) **Existing pins:** the one above (stays green either way);
`tests/test_prebuild_fixes_2026_08_14.py::test_hotkeys_match_main_gd` and
`::test_appdata_saves_documented` read the same file and are unaffected.

---

### `godot-client/.../main_menu.gd` + `tutorial_overlay.gd` (FA-82)

```
tutorial_overlay.gd:452	UiSettings.set_tutorial_done(true)      <- the ONLY setter call
tutorial_overlay.gd:280	if name != "tutorial" or UiSettings.get_tutorial_done():
			_active = false ; hide() ; return
main_menu.gd:438	func _on_tutorial_pressed() -> void:      <- never clears the latch
```

**Verdict: REPRODUCED** (Sept-2 VERIFIED). Line drift confirmed:
`_on_tutorial_pressed` is at **:438-449**, not `:409-419`.

(a) **Seams:** `MainMenu._on_tutorial_pressed` / `MainMenu._launch`
(`main_menu.gd`), `TutorialOverlay.on_world_swap` (`tutorial_overlay.gd:280`),
`UiSettings.set_tutorial_done` (`ui_settings.gd:113`).

(b) **What the filed fix would break:** putting the clear in
`_on_tutorial_pressed` misses the confirm path - that function only shows
the confirm box when `_saves.size() > 0 or MenuBoot.came_from_game`
(`:442-446`); the actual launch then happens in the confirm handler. The
clear must live in `_launch("tutorial")` (or in whatever the confirm
handler calls) or it silently does nothing for any player who has a save,
which is every player who would hit this.

(c) **Minimal correct fix:** in `MainMenu._launch`, when the argument is
`"tutorial"`, call `UiSettings.set_tutorial_done(false)` before the world
swap.

(d) **Existing pins:** `grep -rn "tutorial_done" tests/` = 0 hits.
Nothing flips.

**Flag: `.gd`-only. Boot smoke required.**

---

### `godot-client/.../popup_base.gd` + four scenes (FA-94)

Census run:

```
$ grep -n "_unhandled_input|_input|ui_cancel|KEY_ESCAPE" popup_base.gd
(no output)
$ for f in mailbox_panel proclamation_popup sabotage_discovery_popup \
          vassal_rebellion_popup capture_choice_dialog ; do grep -c ... ; done
mailbox_panel.gd: 0 / proclamation_popup.gd: 0 / sabotage_discovery_popup.gd: 0
vassal_rebellion_popup.gd: 0 / capture_choice_dialog.gd: 0
$ grep -l "extends PopupBase" *.gd
battle_diorama.gd commitment_paradox_popup.gd interrupt_popup.gd
proclamation_popup.gd proposal_result_popup.gd
```
and `main.gd::_unhandled_input`'s ESC ladder (`:980-1005`) has four arms -
wizard, top-bar screen, region panel (guarded `not _is_modal_dialog_open()`),
pause menu (`elif not _is_modal_dialog_open()`) - none of which reaches a
registered modal.

**Verdict: REPRODUCED at source** (Sept-2 NARROWED). `popup_base.gd` has
no input handler at all, and only ONE of the five named surfaces
(`proclamation_popup.gd`) extends it.

(a) **Seams:** `PopupBase` (`popup_base.gd`), `MailboxPanel::_on_close`
(`mailbox_panel.gd:314-321`), `Main::_unhandled_input` (`main.gd:975`).

(b) **What the filed fix would break:** giving `PopupBase` a default
`esc_control()` that presses "the single/rightmost non-destructive
button" would arm ESC on `interrupt_popup.gd`, `battle_diorama.gd`,
`commitment_paradox_popup.gd` and `proposal_result_popup.gd` too - and
`interrupt_popup` is a DECISION modal whose "rightmost" option
(`hold_position`) costs -3 trust and cancels a standing order (FA-49's
own finding). A default that presses a button is a P1 waiting to happen.
The default must be **null** (ESC does nothing) with an explicit opt-in
per scene.

(c) **Minimal correct fix:** `popup_base.gd` gains
`func _unhandled_input(event)` that maps `ui_cancel` to an overridable
`esc_control() -> Button` returning **null by default**;
`proclamation_popup.gd` overrides it to the Acknowledge button;
`mailbox_panel.gd` (a CanvasLayer, not a PopupBase) wires `ui_cancel`
directly to its existing `_on_close`. Leave
`sabotage_discovery_popup.gd` / `vassal_rebellion_popup.gd` /
`capture_choice_dialog.gd` alone - each is a forced choice among
consequential arms with no neutral option, i.e. UI-2d-1's class.

(d) **Existing pins:** `tests/test_popup_routing_registry.py` censuses
`main.gd`'s route table and inline `*_popup.show_*(` calls, not input
handlers. `tests/test_ui_visual_foundation.py` and
`tests/test_ui6_interaction_sweep.py` census `.gd` strings. Adding a
handler to `popup_base.gd` flips nothing I found, but the parse harness
must be re-run.

**Flag: `.gd`-only, five files. Boot smoke + parse harness required.**

---

### `backend/main.py` + docs (FA-101)

```
backend/main.py:4487	# answerable - declared as a P3 legibility gap, owner = row WO slice 12.
tests/test_wo_slice15_capture_question_holds.py:808	  ... owner = row WO slice 12. The sibling
tests/test_wo_slice15_capture_question_holds.py:816	  "owner = row WO slice 12",   <- inside KNOWN_SILENT_AT_LOAD
docs/WEIRD_OUTCOMES_SPEC.md:4441	  ... `pending_objection` stays KNOWN_SILENT
docs/BUG_FIXES.md   (the WO-35 row)
```

**Verdict: REPRODUCED (docs-only).** The Sept-2 correction "FOUR live
sites, not two documents" is right, and I confirm the `main.py` citation
has drifted from `:4120` to **`:4487`**. Row WO is build-complete and
slice 12's landing record contains no objection work.

(a) **Seams:** `backend/main.py:4487` (comment in the `/load` attach
block), `tests/test_wo_slice15_capture_question_holds.py:798-817` (the
`KNOWN_SILENT_AT_LOAD` dict - the string at `:816` is DATA read by the
census, so it is the load-bearing one),
`docs/WEIRD_OUTCOMES_SPEC.md:4441`, `docs/BUG_FIXES.md` WO-35.

(b) **What the filed fix would break:** the fix shape's alternative
("the 3-line attach guarded by `response.get('objection', {}).get('options')`")
would attach a **tactical** objection modal on load for a world that also
carries `pending_strategic_objection` - the two share the response key
(the census's own comment at `:809-812` says the block carries no
discriminator). Do not build the attach without a discriminator.

(c) **Minimal correct fix:** docs-only. Replace the four "owner = row WO
slice 12" strings with "ACCEPTED-UNREACHABLE" and the reachability
argument (the objection dialog is modal, `end_turn` is refused by
`executor.py`'s objection block, so the autosave cannot carry it; the
block names its own answer words).

(d) **Existing pins:** `tests/test_wo_slice15_capture_question_holds.py
::test_blocking_state_surface_census` reads the dict VALUE strings.
Changing `:816` changes census data; check whether the census asserts on
the value text (it appears to only require a value to exist). This is the
one test that WILL be touched by the docs edit.

---

### `godot-client/.../tutorial_1805.json` (FA-63)

**Probes** `p7_tutorial.py` (passive arm), `p7b_tutorial.py` (scripted).

Passive arm (no player order, 6 end-turns): Charles never attacks - the
lesson's actors never leave home, so no target exists.

Scripted arm (`Senarmont, move to Munich` on turn 1, the lesson's own
opening move):

```
--- world turn 2 ---  Charles at Tyrol | Schwarzenberg at Bohemia | Senarmont at Munich 13720
--- world turn 3 ---  battle ArchdukeCharles vs Senarmont
                      Charles at Tyrol | Schwarzenberg at Tyrol | Senarmont Munich 11441
--- world turn 4 ---  battle ArchdukeCharles vs Senarmont
                      battle Schwarzenberg vs Senarmont
                      battle Kienmayer  vs Senarmont
                      Senarmont at Munich 5472
--- world turn 5 ---  battle Schwarzenberg / Kienmayer vs Senarmont
                      Senarmont routed home to Franche-Comte, 2015
```
(each block lists battles logged in the PRECEDING enemy phase)

**Verdict: REPRODUCED - the authored premise is falsified.** Charles
leaves Hungary in the turn-1 enemy phase, stands at Tyrol by turn 2, and
attacks in the **turn-2** enemy phase; the COMBINED attack (Charles +
Schwarzenberg + Kienmayer) lands in the **turn-3** phase. The `_comment`
promises turn 8+. Senarmont's 14,000-man corps is at 2,015 and routed
home by turn 4.

I did NOT reproduce the Sept-2 "mis-attributes the attacker" narrowing -
on my arm Charles IS the first attacker, exactly as filed. My geometry
(Senarmont to Munich on turn 1) may be faster than the syllabus's own
pacing; the premise fails either way.

(a) **Seam:** `godot-client/project-sovereign/assets/maps/tutorial_1805.json`
`_comment` (line 2) and `docs/TUTORIAL_SCRIPT.md:350-351` (steps XII/XIII).
Charles is authored at Hungary; Schwarzenberg at Vienna; both `cautious`.

(b) **What the filed fix would break:** "start Charles one march further
east" is authoring guesswork - he moved from Hungary to Tyrol in ONE
enemy phase, so one more province buys one turn at most. "Give the pair
an authored HOLD/fortify posture" has no authoring hook I could find in
the scenario schema (`marshal_pool`/`agendas`/`relationships` exist;
there is no authored standing-order key). The row's third option
(rewrite steps XII/XIII) is the only one I can see landing cleanly today.

(c) **Minimal correct fix:** rewrite the `_comment` and
`TUTORIAL_SCRIPT.md` steps XII/XIII to describe what the engine does (the
reserve is on you by turn 3), and add a behaviour pin to
`tests/test_tutorial_scenario.py` asserting the reserve's first contact
turn so the next re-author cannot silently drift again.

(d) **Existing pins:** `tests/test_tutorial_scenario.py:98-110` and `:164`
author the pair's start and the road; neither covers timing. Nothing
flips.

---

## Cross-row findings

1. **FA-52 is substantially FA-49.** Same function, same constants, same
   re-ask window, same probe. Landing them separately doubles the work
   and risks two different fixes to `_respond_cannon_fire`. Merge:
   FA-49 = the numbers on the buttons, FA-52 = the sentence and the free
   `investigate` asymmetry.

2. **FA-93 and FA-N47 are the same string.** FA-93 fixes the verb in
   `[Square broken - ...]`; FA-N47 (FA-N set) says that notice is DROPPED
   whenever the action is refused and wiped by any nested `execute()`.
   Fixing the grammar of a string nobody sees is wasted work - land them
   together.

3. **A second, opposite failure of FA-61's label, from the project's own
   archived evidence.** `docs/audits/playtest_digests/audit-tutorial/
   digest.md:50-52`:
   `MUSTER - Ney (20,180; 24,218 if all march)` resolving to
   `Ney stood alone, Sire. Davout and Senarmont never came.` So the same
   label over-promises in one direction (nobody came) and is EXCEEDED in
   the other (my probe). Any fix must be honest in both directions - a
   pure "raise the ceiling" fix makes the first case worse.

4. **The FA-61 aura gap is a `shown != applied` seam nobody has filed.**
   `combat_executor.py:672-682` stamps `sovereign_presence` at resolve
   time only. Every preview surface that calls
   `_committed_reinforcement_strength` under-prices the whole army by
   exactly `SOVEREIGN_PRESENCE_ATTACK * aura` whenever the Emperor is a
   candidate. That is wider than the muster line; it also feeds the odds
   band the CA9 row-2 attack-confirm gate reads.

5. **FA-95's raw-nation-key leak** is a free rider on the same two
   f-strings: `{target_nation}` is the machine key, so a formed nation or
   `KingdomOfItaly` prints unspaced. Same class as FA-69, different file.

6. **FA-65's `_corrected` was wrong because it censused two producers and
   there are three.** The pattern generalises: any "no surface tells the
   player X" claim in this audit should be checked against
   `diplomatic_ledger.py` / `strategic_ledger.py`, which carry a lot of
   quietly-correct derived copy.

7. **Two rows carry a `fix_shape` that contradicts their own `_corrected`
   text.** FA-100 (documented above, chimera) and, more mildly, FA-44
   (`_corrected` says "before line 815, priority 2", `fix_shape` says
   "before :818" - one priority tier apart, and the earlier position is
   wrong).

8. **Harness note:** `StrategicOrderProcessor.handle_response` takes
   `(marshal_name, response_type, choice, world, game_state)` - five
   args. The row's repro line (`handle_response('Davout','cannon_fire',
   'continue_order',...)`) omits the world and TypeErrors. Also
   `Trust.value` is a read-only property; use `trust.set(n)`.

## Flags for landing

**Touches a `.gd`** (boot smoke + parse harness required):
FA-49 (`interrupt_popup.gd`), FA-69 (`capture_choice_dialog.gd`),
FA-70 (`war_detail_popup.gd`), FA-82 (`main_menu.gd`),
FA-94 (`popup_base.gd`, `mailbox_panel.gd`, `proclamation_popup.gd`).

**Moves or adds a serialized field / changes a save's contents:**
FA-69 (two display-only keys onto the serialized
`world.pending_capture_choice` - must be `.get()`-safe on old saves),
FA-100 half (a) (changes what a LOADED world contains; no new field).
No row in this set adds a campaign-log type.

**Could change an AI decision (`BASELINE_SERIES` attribution work):**
- FA-58 (readiness is read by `derive_ai_postures` and the AI build
  rung; today a blockaded fleet below 50 is LIFTED to 50, and the fix
  leaves it below - **this can change an AI posture/build decision and
  the descent window arithmetic. Attribution work required.**)
- FA-56 (fog only, player-scoped by the block's own guard - the block
  skips `marshal.nation != self.player_nation`, so no AI decision moves).
- FA-52's trust half IF built (trust is read by the objection/defiance
  channel) - **do not build the number without a ruling.**
- FA-65 IF the gate is widened rather than re-banded (the hint is
  display-only; the `>= 40` clause writes nothing mechanical). Low risk.
- Everything else in this set is display-only or docs-only.

## Recommended landing order

Cheap-and-certain first, `.gd` batched, the two that need a ruling last.

1. **FA-56** (`world_state.py`, one word) - a dead mechanic the spec
   promises; zero risk; the pin that proves it is already green.
2. **FA-58** (`naval.py`, one line) - but do the `BASELINE_SERIES` arm
   FIRST; both existing readiness pins stay green as measured.
3. **FA-59** (`naval.py`, one helper + three call sites) - the largest
   correctness win in the set; a player is told he lost 49 of 45 ships.
4. **FA-95** (`diplomatic_executor.py`, two f-strings) + the free
   `display_nation` fix.
5. **FA-93 + FA-N47 together** (`tactical_executor.py` + `executor.py`) -
   grammar is pointless without delivery.
6. **FA-69** (`capture_executor.py`, `executor.py`, + `.gd`) - four
   sites, one producer.
7. **FA-45 + FA-51 + FA-64** as ONE naval-copy slice
   (`naval.py` + `naval_executor.py`) - shared file, shared idiom, one
   review.
8. **FA-49 + FA-52 (copy half only)** (`strategic.py` + `.gd`) - merge
   the rows; carry the trust-number question to the user.
9. **FA-100 half (a)** (`save_manager.py`, three deletions) - and file
   half (b) as a new row rather than building it here.
10. **FA-70 + FA-82 + FA-94** as ONE `.gd` slice - one boot smoke, one
    parse-harness run.
11. **FA-44** (`battle_report.py`) - needs the `player_consequence`
    re-read the Sept-2 verdict demands; new bank, position at priority 4
    NOT at the head of the ladder.
12. **FA-61** (`combat_executor.py`) - the largest design content in the
    set; needs the aura decision (thread it, or drop the ceiling claim).
13. **FA-67** - do NOT build as filed. Re-word the warning to state the
    objection prerequisite; correct the false comment.
14. **FA-65** - re-band, do not un-gate.
15. **FA-81 + FA-101** (docs-only) - land beside each other; FA-81 should
    strengthen `test_prebuild_fixes_2026_08_14.py::test_current_roster_present`
    in place.
16. **FA-98** - hold for the PC15-D3 ruling; one-line gate once ruled.
17. **FA-63** - authoring/doc rewrite; add the missing timing pin.

## Probe inventory

All under `<scratchpad>/repro/j7/`:

| file | rows |
|---|---|
| `p1_reports.py` | FA-44, FA-93, FA-58, FA-56 (positive) |
| `p2_naval.py` | FA-56 (control, both directions), FA-45, FA-51, FA-64 |
| `p3_fleet_action.py` | FA-59 |
| `p4_misc.py` | FA-67, FA-65 (event half), FA-100 half (a) |
| `p5_vassal_ledger.py` | FA-65 (the third producer) |
| `p6_muster.py`, `p6b_muster.py`, `p6c_muster_math.py` | FA-61 |
| `p7_tutorial.py` (passive), `p7b_tutorial.py` (scripted) | FA-63 |
| `p8_cannon_estate.py` (superseded), `p8b_cannon.py` | FA-49, FA-52 |
| `p9_estate.py` | FA-69 |

Source-only (no probe needed, claims are structural):
FA-70, FA-81, FA-82, FA-94, FA-98, FA-100 half (b), FA-101.
