# REPRO J2 -- "The Garrison and the Free Verb" (FA-D28, FA-R3)

Read-only reproduction pass, master `a1ed5c9d`, Sept 5 2026. All probes under
`scratchpad/repro/j2/`. No repo file was touched.

## Summary

- **FA-D28 -- REPRODUCED (exactly on its own headline case), with two
  corrections.** A 40,000-man corps clears a detachment garrison of 3,000 /
  12,000 / 25,000 in **13 / 15 / 16 assaults** (the row's counts, to the digit)
  losing **10,156 / 13,396 / 18,122** men on plains. The mechanism is the
  `max(attacker_losses, int(marshal.strength * 0.02))` floor, which **binds if
  and only if the attacker's effective strength exceeds 12.5x the garrison's**
  -- so it is a pure over-match tax. The row's totals for the 12k and 25k cases
  (24,973 / 16,570 remaining) are NOT reproducible on a plains province and are
  not explained by terrain; only case A reproduces exactly.
- **FA-R3 -- REPRODUCED, and WIDER by one verb.** `Davout, hold Rhineland and
  wait` -> AP 4->4 with `HOLD:Rhineland` standing and the reply saying "2 AP";
  `Ney, march to Lorraine and wait there` -> AP 4->4, `MOVE_TO` standing AND
  Ney actually marched; **`Davout, support Ney and wait` -> AP 4->4 with a
  SUPPORT order standing** -- a third shape the row does not name. `hold
  Rhineland and stay put` is already FIXED (4->2), as the row itself predicts.
  The root is `executor.py::CommandExecutor.execute`: `action_costs_point =
  action not in free_actions` is computed off the BASE verb, so for
  `action == "wait"` both the AP pre-gate AND the charge block are skipped and
  the `variable_action_cost: 2` that `_execute_strategic_command` returns is
  silently discarded.

---

## Per row

### FA-D28 -- the garrison formula

Probes: `p1_garrison_baseline.py`, `p2_model_and_fix.py`,
`p3_series_garrison_count.py`, `p4_series_fix_delta.py`, `p5_which_pins_flip.py`.

#### Verdict: REPRODUCED (headline case exact; two of the row's three loss
totals are not reproducible and one of its generalisations is false)

`p1` -- Kutuzov 40,000 (France's Lorraine, plains, no fort, attack modifier
1.00) vs a French **detachment** garrison, resolver called in a loop:

```
garrison=3000   assaults=13  attacker 40000 -> 29844 (lost 10156)
garrison=12000  assaults=15  attacker 40000 -> 26604 (lost 13396)
garrison=25000  assaults=16  attacker 40000 -> 21878 (lost 18122)
    #1  attacker  40000 ->  39200   garrison   3000 ->   1500
    #2  attacker  39200 ->  38416   garrison   1500 ->    750
    ...
    #13 attacker  31394 ->  29844   garrison      1 ->      0
```

- **Assault counts 13 / 15 / 16 match the row to the digit.**
- **Case A's total matches to the digit** (40,000 -> 29,844).
- The row's B and C totals (24,973 / 16,570) do NOT reproduce. `p2` scans every
  terrain: plains 27,273 / 22,197, forest 26,862 / 21,278, hills 26,657 /
  20,691, urban 26,449 / 20,016, mountains 26,245 / 19,305 (combat losses only,
  before march attrition) -- **no terrain reaches the row's figures**. The row's
  probe must have used a fortified province or a sub-1.0 attack modifier. The
  shape stands; two of its numbers do not.
- **The row's generalisation "loses more men than the garrison had" is true at
  13:1 (10,156 vs 3,000) and at 3.3:1 (13,396 vs 12,000) but FALSE at 1.6:1
  (18,122 vs 25,000).** The absurdity is an over-match tax, not a universal.
- `p2` also isolates the last-assault jump (case A #13 costs 1,550 where #12
  cost 640): that is the **collapse-turn march attrition**
  (`_calculate_movement_attrition`), 923 / 669 / 319 men in the three cases. It
  is a cost of taking the province and survives any fix; the model figures below
  are combat-only.

#### (a) The true seam, by symbol

`backend/commands/combat_executor.py::CombatExecutor._resolve_garrison_combat`
-- the six arithmetic lines between the `attacker_effective <= 0` guard and
`# Apply losses`:

```python
attacker_damage_ratio = min(0.35, garrison_effective / max(attacker_effective, 1) * 0.25)
garrison_damage_ratio = min(0.50, attacker_effective / max(garrison_effective, 1) * 0.35)
attacker_losses = int(marshal.strength * attacker_damage_ratio)
garrison_losses = int(target_region.garrison_strength * garrison_damage_ratio)
attacker_losses = max(attacker_losses, int(marshal.strength * 0.02))
garrison_losses = max(garrison_losses, int(target_region.garrison_strength * 0.10), 1)
```

Two independent levers, and the gate's title names both:

1. `min(0.50, ...)` on `garrison_damage_ratio` -> the **assault count** is
   `ceil(log2 N) + 1` however overwhelming the attacker.
2. `max(..., int(marshal.strength * 0.02))` -> the **per-assault bill scales
   with the ATTACKER**, so a bigger corps pays more per assault for the same
   fight. `p5` derives the binding condition exactly: **the floor binds iff
   effective attacker > 12.5x effective garrison.**

The collapse rule is a third line (`if target_region.garrison_detachment:
garrison_collapsed = strength <= 0` else `< 5000`) and is what makes a
detachment take the full `log2` tail down to 1 man.

#### The two readings of "floor the attacker's losses at the GARRISON's strength"

I can see exactly two, and I measured both (`p2`):

- **Reading FLOOR (the row's own words: "floor the attacker's losses on the
  GARRISON's size, not his own")** -- replace `int(marshal.strength * 0.02)`
  with `int(target_region.garrison_strength * 0.02)`. Per-assault only, no new
  state.
- **Reading CAP (cumulative)** -- clamp the attacker's cumulative losses to the
  garrison's ORIGINAL strength. Needs the original strength remembered across
  assaults, i.e. a new field or a re-derivation.

Measured, combat losses only, plains, modifier 1.00:

```
variant    g=3000                   g=12000                  g=25000
today      13 assaults, lost   9233 15 assaults, lost  12727 16 assaults, lost  17803
floor      13 assaults, lost   1496 15 assaults, lost   5996 16 assaults, lost  12496
odds        1 assaults, lost    800  2 assaults, lost   4500  3 assaults, lost  10937
both        1 assaults, lost    750  2 assaults, lost   4500  3 assaults, lost  10937
cap_cum    13 assaults, lost   3000 15 assaults, lost  12000 16 assaults, lost  17803
```

**The measured absurdity demands the FLOOR reading, and CAP is strictly worse.**
CAP keeps all 13 assaults, keeps the whole grind, and its output is the tell:
the attacker pays *exactly* 3,000 against a 3,000-man detachment at 13:1 -- an
obviously artificial number reached only because the clamp bit. It also cannot
bind at all in case C (17,803 < 25,000), so it does nothing for two of the three
measured cases. FLOOR removes the over-match tax at its cause and satisfies the
acceptance criterion in all three: 1,496 / 5,996 / 12,496, each below its own
garrison's strength, and each still below it after the ~1k of march attrition.

One consequence the builder must decide consciously: with a garrison-based 2%
floor, `int(g * 0.02)` is *always* below the proportional term at modifier 1.0
and no terrain, so the floor becomes **effectively dead code** and the rule
reduces to the pure proportional loss. That is fine mechanically (the garrison
still loses `max(..., 1)` per assault, so the WO-3 no-stall guarantee is
untouched and no assault can stall), but "Ensure minimum losses on both sides"
in the comment stops being true of the attacker: a 40,000 corps storming a
3-man post pays 0. If that is unwanted, `max(int(g * 0.02), 1)` costs nothing.

#### (b) M1-M7: can the harness see a garrison assault? NO.

`tests/test_combat_sweep_metrics.py` contains **zero** occurrences of
"garrison" (measured, `grep -ic`). Every metric routes through `_resolve()` ->
`resolve_battle` on hand-built marshal pairs; the file never calls
`advance_turn`, `TurnManager` or `EnemyAI` (M7's `measure_m7` builds an
`EnemyCorps` and calls `_resolve` directly). The gate's own claim "M1-M7
unaffected (the harness never resolves a garrison)" is **correct**, and the
`BASELINE_SERIES` record already says so in prose.

#### (c) BASELINE_SERIES: does the ambient 40-turn run resolve garrisons? YES -- six times.

`p3` runs a faithful replica of
`tests/test_ai_intent_threat_migration.py::_emit_series` (same
`PYTHONHASHSEED=0`, `SOVEREIGN_SEED=historical`, same per-turn `random.seed`)
with a counting wrapper. It reproduces `BASELINE_SERIES` byte-for-byte
(`series matches BASELINE_SERIES: True`) and reports:

```
garrison-resolver calls in the 40-turn ambient run: 6
  by attacking nation: {'Austria': 6}
  detachment garrisons: 0   capital-flagged regions: 2
  t10 ArchdukeCharles 26167 vs Milan     10000 (KingdomOfItaly capital)
  t10 ArchdukeCharles 23522 vs Milan      5000
  t12 ArchdukeCharles 20147 vs Normandy  12000 (France, DEF-6 depot)
  t12 ArchdukeCharles 16814 vs Normandy   6000
  t27 ArchdukeCharles 27864 vs Flanders  12000 (France, DEF-6 depot)
  t27 ArchdukeCharles 24531 vs Flanders   6000
```

So the resolver **is** on the ambient board -- but no *detachment* garrison ever
is, and the odds never approach the floor's 12.5:1 threshold. `p4` computes,
for each of those six assaults, today's numbers against each candidate:

```
t10 Milan    g=10000 a=26167  applied=(2645,5000)  today=(2500,5000) floor=(2500,5000) odds=(2500,5000)
t10 Milan    g= 5000 a=23522                       today=(1250,2500) floor=(1250,2500) odds=(1250,5000)  <-- MOVES
t12 Normandy g=12000 a=20147  applied=(3333,6000)  today=(3000,6000) floor=(3000,6000) odds=(3000,6000)
t12 Normandy g= 6000 a=16814                       today=(1500,3000) floor=(1500,3000) odds=(1500,3000)
t27 Flanders g=12000 a=27864  applied=(3333,6000)  today=(3000,6000) floor=(3000,6000) odds=(3000,6000)
t27 Flanders g= 6000 a=24531                       today=(1500,3000) floor=(1500,3000) odds=(1500,6000)  <-- MOVES
```

**The FLOOR half is byte-identical on all six.** The 2%-of-attacker floor never
binds anywhere on the ambient board, so a floor-only fix changes nothing the
series can see: **no `BASELINE_SERIES` re-record is expected for the blessed
ruling.** (Verify by re-running the pinned series once, but the arithmetic says
it will not move.)

**The ODDS half MOVES two assaults** (4.7:1 and 4.1:1 clear a >=4:1 gate). Both
are collapse assaults either way, so the capture outcome is identical -- but the
logged `defender_casualties` doubles (2,500 -> 5,000 and 3,000 -> 6,000), which
feeds `record_battle`, the war score and the EC-W3 materiel bill
(`int(casualties * 0.05)` gold on the defender). That is a live economic ripple
into later AI decisions. **If the builder also takes the odds half, budget a
`BASELINE_SERIES` re-record with a two-arm flip attribution.**

#### (d) GR5: one resolver, both directions -- CONFIRMED

`_resolve_garrison_combat` has exactly two production call sites:
`combat_executor.py:5171` inside `CombatExecutor._execute_attack` (the
no-defenders branch) and `naval_executor.py:403`. `_execute_attack` is reached
by player and AI alike through `CommandExecutor.execute` (`executor.py:2920`) --
there is no separate AI garrison path. Measured both ways: the ambient run's six
assaults are all **AI** (Austria, two of them against France's own depots), and
the existing pins drive the **player** side (France's Ney/Davout) and a
third-party side (Britain's Wellington vs Paris,
`test_fa_slice4...::TestTheGarrisonAssaultCounts`).

#### What the row's own filed fix would BREAK

The row prescribes **two** changes; the relayed blessing names only the second.

1. *"scale the garrison damage with the odds (>= 4:1 -> the detachment falls in
   one assault; the 0.50 cap keeps only for a capital's own garrison)"* --
   this is the half that carries risk:
   - it MOVES two of the six ambient assaults (above), so it re-records
     `BASELINE_SERIES`;
   - the ">= 4:1" gate FIRES in six of the existing test geometries (`p5`:
     `garrison_system::attacker_2pct` 4.44, `r1_char::collapse` 7.50,
     `deep_audit::falls` 6.25, `systems_v3` 5.00, and both 13:1 detachment
     cases). None of those *assertions* flips (they all already collapse), but
     any future "Garrison holds" pin in a >=4:1 geometry would;
   - the row's own carve-out ("the 0.50 cap keeps only for a capital's own
     garrison") is under-specified: the two French DEF-6 depots at Normandy and
     Flanders are `is_capital: False` and `garrison_detachment: False`, so they
     fall in neither bucket. The rule needs three cases, not two.
2. *"floor the attacker's losses on the GARRISON's size, not his own"* -- safe,
   inert everywhere except >12.5:1, and it is what the blessed ruling names.

The gate's own pin line ("the three measured cases above as a before/after
table; M1-M7 unaffected") is correct on M1-M7 and **silent on
`BASELINE_SERIES`, which the odds half does move**.

#### Minimal correct fix

One line, inside `_resolve_garrison_combat`, behind a flip lever beside
`GARRISON_ASSAULT_COUNTS`:

```python
# FA-D28: the minimum bill is a function of the FIGHT, not of the
# attacker's own size. Keyed off `marshal.strength` it was a pure
# over-match tax -- it binds only above 12.5:1, and it is what made a
# 13:1 corps lose 10,156 men to a 3,000-man detachment.
attacker_losses = max(attacker_losses,
                      int(target_region.garrison_strength
                          * GARRISON_ASSAULT_MIN_LOSS_FRACTION))
```

with `GARRISON_ASSAULT_MIN_LOSS_FRACTION = 0.02` as the named constant (Golden
Rule 1: the number lives here). `shown = applied` is automatic -- both message
branches already interpolate `attacker_losses`.

Recommend building the floor half ALONE first and measuring: it satisfies the
gate's stated absurdity ("loses more men than the garrison had") in all three
cases, and it costs no re-record. The assault-count half is a separate,
`BASELINE_SERIES`-moving decision the gate should take on its own evidence.

#### Existing tests that pin today's numbers

`p5` evaluates every garrison geometry in `tests/`. Under the FLOOR fix the
floor binds in exactly **three** of them, and **none has an assertion that
flips**:

| test | geometry | floor binds? | assertion | flips? |
|---|---|---|---|---|
| `tests/test_garrison_system.py::TestGarrisonCombat::test_attacker_takes_at_least_2pct_losses` | 80k vs 15k urban | **no** (prop 4,500 > floor 1,600) | `assert attacker_losses >= 1600` | **no -- and the pin is VACUOUS today**: it names the 2% floor and never reaches it |
| `tests/test_garrison_system.py::TestGarrisonCombat::test_garrison_below_5k_collapses` | 50k vs 3k urban | **BINDS** (1,000 -> 899) | `garrison_strength == 0`, `location == "Paris"` | no |
| `tests/test_systems_v3_session4.py` fog case | 40k vs 3k Berlin | **BINDS** (800 -> 750) | intel mock called | no |
| FA-D28's own three cases | 40k vs 3k/12k/25k detachment | BINDS (A) / binds in the tail (B, C) | -- | (no pin exists) |
| `tests/test_r1_characterization.py::TestGarrisonPostCombat::*` | 60k vs 8k / 15k vs 40k | no | outcome-only | no |
| `tests/test_deep_audit_session1.py::TestFix6GarrisonWarScore::*` | 50k vs 8k / 15k vs 80k | no | `records[0]["winner"]` | no |
| `tests/test_ca8_gate_closeout_2026_08_07.py::test_a_repulsed_escalade_moves_no_glory` | 12k vs 60k | no | `"holds" in message`, `ney.strength < 12000` | no |
| `tests/test_creative_audit_ca8_2026_08_04.py` CA8-19 class | 40k-ish vs 3k/20k | (coordination-stamp pins) | stamp == 0.0 | no |
| `tests/test_marshal_content_mc1c_iron_resolve.py::test_garrison_assault_consumes_and_names_it` | 30k(+16%) vs 20k London | no | `"Garrison holds" in message` | no under FLOOR; **would need re-checking under ODDS** (odds 1.45, gate does not fire -- safe, but it is the pin nearest the edge) |
| `tests/test_fa_slice4_...::TestTheGarrisonAssaultCounts` | 40k vs 15k Paris | no | counters | no |

`tests/test_garrison_system.py::test_garrison_takes_at_least_10pct_losses`
(`assert garrison_losses >= 1500`) pins the *garrison* floor, which neither
variant touches.

---

### FA-R3 -- a standing order created at 0 AP behind a free base verb

Probes: `p6_far3_ap.py`, `p7_far3_parse.py`, `p8_far3_parse2.py`,
`p9_far3_dump.py`, `p10_far3_blast.py`, `p11_far3_edges.py`. All driven through
the real `POST /command` on a fresh 1805 boot (France, turn 1, AP 4), mock
parser.

#### Verdict: REPRODUCED, and one verb wider than filed

```
DEFECT 1  'Davout, hold Rhineland and wait'
   success=True  AP 4 -> 4   NEW standing orders: {'Davout': 'HOLD:Rhineland'}
   reply: Davout will hold Rhineland. Holding position. ... (2 AP - a standing
          strategic order to hold this ground turn after turn. ...)
   *** the reply claims 2 AP ***

DEFECT 2  'Ney, march to Lorraine and wait there'
   success=True  AP 4 -> 4   NEW standing orders: {'Ney': 'MOVE_TO:Lorraine'}
   reply: Ney begins march to Lorraine. Moves to Lorraine. ...

NEW       'Davout, support Ney and wait'
   success=True  AP 4 -> 4   NEW standing orders: {'Davout': 'SUPPORT'}

DEFECT 3  'Davout, hold Rhineland and stay put'
   success=True  AP 4 -> 2   (ALREADY FIXED by the slice-7 review round)

CONTROL   'Davout, hold Rhineland'          AP 4 -> 2   HOLD
CONTROL   'Ney, march to Lorraine'          AP 4 -> 2   MOVE_TO
CONTROL   'Soult, hold Lorraine'            AP 4 -> 3   HOLD  (literal, 1 AP)
CONTROL   'Soult, march to Gascony'         AP 4 -> 3   MOVE_TO (literal, 1 AP)
CONTROL   'wait for reinforcements'         AP 4 -> 4   (CR-2 clarification)
CONTROL   'Davout, wait for reinforcements' AP 4 -> 4   no order  (free, correct)
```

The literal marshal on the 1805 board is **Soult** (roster measured: Ney
aggressive, Davout cautious, **Soult literal**, Lannes/Murat/Massena
aggressive, Bernadotte cautious, Napoleon sovereign). Both his controls charge
1 AP, so `strategic_order_ap()`'s discount is live.

`p9` dumps the parse and shows the mechanism exactly:

```
Davout, hold Rhineland and wait ->
  command: {"marshal": "Davout", "action": "wait", "target": "Rhineland", ...}
  is_strategic: true,  strategic_type: "HOLD"

Davout, hold Rhineland ->
  command: {"marshal": "Davout", "action": "hold",  "target": "Rhineland", ...}
  is_strategic: true,  strategic_type: "HOLD"
```

Same order, same target, different base verb -- and the base verb is what the
AP gate reads.

Two additions to the row's account:

- **`support ... and wait` is a third shape** (SUPPORT at 0 AP). The row names
  only HOLD and MOVE_TO.
- **`Ney, pursue Mack and wait` is NOT affected** (parses `action: "attack"`,
  charged 2 AP) -- the defect is precisely the `free_actions` membership, not
  the "and wait" suffix.
- Found in passing: `Davout, hold your ground and wait` is **REFUSED** ("I could
  not make out a destination in that order, Sire") while `Davout, hold your
  ground` alone works and charges 2. The trailing wait clause defeats PF-6's
  bare stand-fast idiom. Not FA-R3's defect; filed here as a sibling.

#### (a) The true seam, by symbol

`backend/commands/executor.py::CommandExecutor.execute`, the action-economy
block:

```python
free_actions = ["status", "help", "end_turn", "unknown", "retreat", "wait", ...]
action_costs_point = action not in free_actions          # <-- THE SEAM
if is_strategic_execution:
    action_costs_point = False
```

`action_costs_point` then gates **both** halves:

- the **pre-gate** (`if action_costs_point and is_player_action_check and not
  counter_punch_waiver:`), whose strategic branch reads
  `marshal_for_cost.strategic_order_ap()`; and
- the **charge** (`if result.get("success", False) and action_costs_point and
  is_player_action and not is_free_action and not
  result.get("pending_objection"):`), which is the only reader of
  `variable_action_cost`.

`strategic_executor._execute_strategic_command` already returns
`"variable_action_cost": strategic_cost` (`strategic_executor.py:1747`; the
MOVE_TO upgrade does the same at `movement_executor.py:568`). **The order is
already priced correctly; the outer block just never looks at it.**
`Marshal.strategic_order_ap` (`backend/models/marshal.py:838`) is the correct
single source and needs no change.

#### (b) What the row's OWN filed fix would BREAK

The row offers two shapes. **Both are wrong.**

1. *"Charge the strategic cost from the ORDER in `_execute_strategic_command`"*
   -- if the sub-executor calls `world.use_action()` itself, then for a
   NON-free base verb (`hold`, `move`, `attack`/pursue) the outer block still
   runs and still spends `variable_action_cost`, so **`Davout, hold Rhineland`
   would be charged twice: 4 -> 0 instead of 4 -> 2.** That is a shipped
   regression on the commonest strategic sentence in the game, and it would
   red `tests/test_fa_slice5_the_road_law_2026_09_04.py::
   TestTheRoadLaw::test_fa13_the_first_hop_marches_on_the_lawful_road`
   (`assert world.actions_remaining == ap - 2`).
2. *"or refuse the strategic upgrade when the base action is free"* -- this
   **contradicts the row's own done-when**, which demands `hold Rhineland and
   wait` -> "AP 4->2 **and a HOLD order**". Refusing the upgrade would silently
   discard the player's HOLD and leave a bare WAIT -- the FA-N2/slice-1 class of
   defect (an answer read from text the guard blanked).

The row is also right that the parser cannot be the seam: `p8` confirms the mock
chain's WAIT arm (`llm_client.py:1839-1842`, `elif "wait" in command_lower or
"stand by" in ...`) sits **above** the hold family (`:1855`), the SUPPORT arm
(`:1993`) and move (`:1915`), and the file's own comment at `:629-630` records
why it must stay there ("moving it to the bottom would break 'Ney, wait for
reinforcements'"). The FA-80 stay-put arm at `:2164` is separately sited LAST,
which is why `and stay put` / `and rest your men` already price correctly.

#### (c) Minimal correct fix

Three lines in `CommandExecutor.execute`, inserted **between** the
`action_costs_point = action not in free_actions` line and the
`if is_strategic_execution:` override (so execution still wins):

```python
action_costs_point = action not in free_actions
# FA-R3: a STANDING ORDER is priced by the ORDER, never by the sentence's
# base verb. "Davout, hold Rhineland and wait" parses action="wait" (free)
# with is_strategic/strategic_type set, so the gate below was skipped and
# the 2 AP that `_execute_strategic_command` returns were discarded --
# a two-turn order for nothing, under a reply that says "2 AP".
if (STRATEGIC_AP_KEYS_OFF_THE_ORDER
        and parsed_command.get("is_strategic")
        and parsed_command.get("strategic_type")):
    action_costs_point = True
if is_strategic_execution:
    action_costs_point = False
```

Effects, each measured or read:

- **(i) counter-punch waiver** -- untouched. It is already gated on
  `action == "attack"` (never free) AND `not parsed_command.get("is_strategic")`,
  so no strategic order can reach it and no free verb can.
- **(ii) `is_strategic_execution`** -- stays FREE, because the existing override
  runs after the insert. Pin it.
- **(iii) auto-upgrade (`strategic_order_ap(auto_upgrade=True) == 1`)** --
  untouched: an auto-upgraded MOVE_TO parses `action: "move"` (measured, `p10`
  `Ney, march to Lorraine` -> `action=move`), which is not free, so the clause
  does not fire and the existing `variable_action_cost` path is unchanged.
  **Pre-existing mismatch worth a comment, not a fix here:** the pre-gate calls
  `strategic_order_ap()` with no `auto_upgrade`, so it demands 2 while the
  charge spends 1 -- a 1-AP auto-upgrade is refused at exactly 1 AP.
- **(iv) free verbs that are NOT order-creating** -- untouched, measured. `p10`
  and `p11` drive eighteen sentences; the clause fires on **exactly three**:

```
Davout, hold Rhineland and wait          action=wait  FREE  HOLD     4->4  WOULD NOW CHARGE
Ney, march to Lorraine and wait there    action=wait  FREE  MOVE_TO  4->4  WOULD NOW CHARGE
Davout, support Ney and wait             action=wait  FREE  SUPPORT  4->4  WOULD NOW CHARGE
Ney, pursue Mack and wait                action=attack -    PURSUE   4->2  unchanged
Davout, hold Rhineland and stay put      action=hold   -    HOLD     4->2  unchanged
Davout, retreat to Lorraine and hold there action=hold -    HOLD     4->2  unchanged
Davout, retreat                          action=retreat FREE -       4->4  unchanged
Davout, retreat to Lorraine              action=retreat FREE -       4->4  unchanged
Davout, wait at Rhineland / wait there   action=wait   FREE -        4->4  unchanged
Davout, wait for reinforcements          action=wait   FREE -        4->4  unchanged
```

  `retreat` -- the free verb with the loudest design intent ("retreat is FREE -
  strategic withdrawal") -- **never carries a `strategic_type`**, so it is
  structurally out of reach. `p11` re-runs every `wait`-bearing utterance in
  `tests/data/parser_golden_corpus.json` (`Ney, wait`, `Ney, wait for
  reinforcements`, `Ney, wait for Davout`, `Ney, wait for Davout then attack
  Mack`, `no wait, Ney, retreat`, `wait, hold position`, `stand by, Ney, move to
  Paris`, `Ney, stand by`, `Ney, stay here, then attack Mack`, `Davout, scout
  Swabia and remain there`): **not one carries a strategic type, so not one
  changes.** The corpus is safe by measurement, not by argument.

#### (d) Existing tests that assert AP after a strategic order

`grep -c "actions_remaining ==" tests/*.py` = **122 assertions**. The ones that
sit in a strategic context and must be run:

| test | assertion | flips? |
|---|---|---|
| `tests/test_fa_slice5_the_road_law_2026_09_04.py::TestTheRoadLaw::test_fa13_the_first_hop_marches_on_the_lawful_road` | `assert world.actions_remaining == ap - 2` (`"Ney, march to Normandy"`) | no -- base verb `move` |
| `tests/test_fa_slice5_...::test_the_lever_off_arm_reproduces_the_row` | `assert world.actions_remaining == ap - 2` | no |
| `tests/test_fa_slice5_...::test_the_cautious_avoid_set_is_the_one_source` | `assert world.actions_remaining == ap` (refused `"Ney, march to Frankfurt"`) | no |
| `tests/test_fa_slice5_...::test_a_hold_past_a_closed_border_is_refused_at_zero_ap` | `assert world.actions_remaining == ap` (`"Davout, hold Brunswick"`) | no -- base verb `hold` |
| `tests/test_fa_slice3_the_order_tells_the_truth_2026_09_04.py:290,307` | `assert M.world.actions_remaining == ap` | no |
| `tests/test_fa_slice3r_...:308,373` | `assert world.actions_remaining == ap` | no |
| `tests/test_fa_slice2_no_word_came_2026_09_04.py:377,455,489` / `test_fa_slice2r_...:162,215,355` | `assert world.actions_remaining == ap` | no |
| `tests/test_fa_slice1_the_two_words_2026_09_02.py:224` | `assert M.world.actions_remaining == 3` (`Berthier, retreat` at 0 AP) | no -- `retreat`, no strategic type |
| `tests/test_counter_punch_ap_gate.py:113,125` | `assert world.actions_remaining == before` / `== 0` | no -- attack, waiver already excludes strategic |
| `tests/test_ca9_row3_q2_council_command.py:240,262,381,395` | `== 4`, `== 4 - J.COMMAND_ARM_AP` | no |
| `tests/test_command_robustness_cr2/cr4/cr5*.py` | various | no `wait`+strategic sentence in any of them (`grep "and wait"` over `tests/` returns 4 hits, all parse-level: `test_creative_audit_ca9_...:3093`, `test_fa_slice7_...:389,726`, `test_command_robustness_cr4_...:269`) |

**Measured conclusion: no existing test flips.** The three sentences the fix
touches are not driven by any test today, which is exactly why the defect
survived -- and is the argument for pinning all three (plus the four controls,
plus `is_strategic_execution` staying free) in the slice's own file.

---

## Cross-row findings

1. **`action_info.cost` under-reports every 2-AP strategic order as 1.**
   Measured (`p6`): `Davout, hold Rhineland` -> `AP 4 -> 2 (cost reported: 1)`.
   The charge loop at `executor.py` is
   `for _ in range(variable_cost): action_result = world.use_action(action)`,
   and each `use_action` returns `action_cost: 1`, so the last iteration
   overwrites the first. `result["action_info"]["cost"]` is therefore wrong for
   every variable-cost action (strategic orders, stance changes). Pre-existing,
   display-only, not filed anywhere I could find. Whoever builds FA-R3 will be
   staring at this number and should not "fix" it by accident.

2. **`tests/test_garrison_system.py::test_attacker_takes_at_least_2pct_losses`
   is a vacuous pin.** Its geometry (80,000 vs 15,000 urban) produces a
   proportional loss of 4,500 against a 1,600 floor, so the floor it exists to
   test never binds. Deleting the floor entirely leaves it green. If the builder
   wants a real negative control for FA-D28 it must be built at >12.5:1.

3. **The FA-D28 gate's pin line is silent on `BASELINE_SERIES`,** which the
   odds half of its own fix shape moves (two of six ambient assaults). It is
   correct about M1-M7.

4. **The ambient board never contains a detachment garrison.** All six garrison
   assaults in 40 turns are against capital or DEF-6-depot garrisons
   (`garrison_detachment: False`). So FA-D28's headline geometry -- the case
   that motivates the gate -- is invisible to every standing harness, and the
   builder's only evidence will be the three-case before/after table.

5. **`Davout, hold your ground and wait` is refused** ("I could not make out a
   destination") while `Davout, hold your ground` alone creates a 2-AP HOLD.
   The trailing wait clause defeats PF-6's stand-fast idiom at the destination
   read. Sibling of FA-R3, not the same defect; unfiled as far as I can see.

6. **`CommandParser.parse` takes `(command_text, game_state, world)`** -- the
   second positional is the game_state DICT, not the world. Passing the world
   there returns a dict whose `command` sub-dict is empty of marshal/target and
   whose `is_strategic` is absent, which reads exactly like "the parser found
   nothing". Cost me a probe cycle; worth a line in the preamble.

---

## Probe inventory

All under
`<scratchpad>/repro/j2/`:

| file | what it does |
|---|---|
| `p1_garrison_baseline.py` | drives `_resolve_garrison_combat` in a loop for 40k vs 3k/12k/25k detachments; prints assaults-to-clear and the per-assault ladder |
| `p2_model_and_fix.py` | validates a faithful arithmetic model against the shipped resolver, attributes the row's own numbers across all five terrains, and runs the five fix variants (today / floor / odds / both / cap_cum) incl. a capital control |
| `p3_series_garrison_count.py` | replica of `_emit_series` with a counting wrapper; proves the replica reproduces `BASELINE_SERIES` and counts + dumps every garrison assault in the 40-turn ambient run |
| `p4_series_fix_delta.py` | for each of those six assaults, computes today's vs each variant's losses and reports which MOVE |
| `p5_which_pins_flip.py` | evaluates every garrison geometry used by an existing test for "does the 2%-of-attacker floor bind" and "does a >=4:1 odds gate fire" |
| `p6_far3_ap.py` | drives the real `/command` for the FA-R3 sentences + controls; AP before/after, order created, reply text |
| `p7_far3_parse.py` | fourteen sentences through parser + `/command` (first cut; wrong parse signature, kept for the AP half) |
| `p8_far3_parse2.py` | corrected parse call; action / is_strategic / strategic_type / free? per sentence |
| `p9_far3_dump.py` | full parse-dict dump for the five decisive sentences |
| `p10_far3_blast.py` | the blast radius: eighteen sentences, which would newly be charged |
| `p11_far3_edges.py` | every `wait`-bearing golden-corpus utterance + the `wait for <marshal>` idiom, measured for AP and order |
