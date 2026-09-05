# REPRO J4 - "The Diversion and the Recall" (FA-31, FA-S9-D1)

Read-only reproduction, master `a1ed5c9d`, mock parser, sandboxed saves.

## Summary

- **FA-31 - NARROWED.** The row's *outcome* reproduces at the natural timing (camp staged
  end of turn 4 -> a won roll opens a strait at ratio 0.79 same-turn / 0.70 next-turn, SHUT
  both ways), but all three legs of its *mechanism* are wrong and its conclusion is
  inverted: staging the camp is the CURE for the blockade rot, not its cause
  (`derive_ai_postures` flips Britain blockade->guard at `camp_turns>=2`, France leaves
  `blockaded_nations`, readiness climbs +5/turn to 75 and the window ratio reaches 0.91 by
  turn 7 and 1.05 by turn 9). The surviving defect is one layer smaller and sharper:
  **no surface forecasts the crossing the once-per-war card is spent to open, the chip's
  only warning fires in the safe state and falls silent in the trap state, and the window's
  own first turn is measurably stronger than its second because `resolve_diversion` never
  re-derives postures.**
- **FA-S9-D1 - BUILDABLE, WITH ONE BLOCKER FOUND BY MEASUREMENT.** `administrative`,
  `administrative_strength` and `administrative_location` are ad-hoc attributes set by
  assignment and are in NEITHER `Marshal.to_dict` NOR `from_dict`. Measured: after one
  save/load the flag is gone, 22,000 frozen men are deleted, `bonus_actions` (which IS
  serialized) stays at 1 forever, and `get_admin_marshals()` returns 0 while
  `get_field_marshals()` counts the ghost. `recall <marshal>` on a loaded campaign would
  restore **0 men at `None`**. Serialize the three fields FIRST or the verb ships broken.

---

## Per row

### FA-31 - the Grand Diversion is quoted blind

Probes: `probe_1_boot.py`, `probe_2_rot.py`, `probe_3_exact.py`, `probe_4_posture_flip.py`,
`probe_5_chip_and_ai.py`.

#### What reproduces (the row's own arithmetic, on the shipped 1805 boot)

`probe_1_boot.py`:

```
France rec: {'ships': 45, 'readiness': 70, 'posture': 'guard', 'camp_turns': 0, ...,
             'camp_provinces': ['Flanders', 'Artois', 'Normandy', 'Brittany']}
Britain rec: {'ships': 100, 'readiness': 100, 'posture': 'blockade', 'island': True}
blockaded_nations: ['France', 'Holland', 'Spain']
camp_strength(France): 0   min needed 40000
crossing_check France Normandy->London (no window):
   allowed False, verdict shut, coverage 100.0, mover_effective 53.8, ratio 0.54, floor 1.25
after forcing window_turns=2 and re-deriving postures:
  Britain posture: guard
  covering_fleets: [('Britain', 55.2)]
  crossing_check: allowed True, verdict window, coverage 55.2, mover 53.8, ratio 0.97, floor 0.9
```

The row's "53.8 vs the halved 55.2 = 0.97 OPEN" is exact. So is the 45/70, 30/65, 12/70
pooling (`31.5 + 0.8*19.5 + 0.8*8.4 = 53.82`).

The outcome claim also reproduces. `probe_5_chip_and_ai.py` runs the honest sequence
(50,000 men into a camp province from turn 3, four `process_naval_turn` ticks):

```
t=4 staged=True camp_turns=2 readiness=50 blockaded=['France','Holland','Spain'] GBposture=blockade
=== forcing the WON arm on this board ===
  same turn : shut 0.79 allowed False
  next turn : shut 0.7  allowed False
```

So: **at the earliest realistic staging turn, a WON roll does leave London-Normandy SHUT.**

#### What is FALSE (three legs, all measured)

**(1) "the RN's halved 55.2" is the NEXT turn's number, not the diversion turn's.**
`resolve_diversion` sets `window_turns = WINDOW_TURNS` and returns; it never calls
`derive_ai_postures`. Britain therefore stays on `blockade` for the rest of that turn, and
`covering_fleets` pools by MATCHING posture - so Russia's 20-ship *guard* squadron is
excluded and the halved coverage is **50.0**, not 55.2. On the next `process_naval_turn`,
step 1 `derive_ai_postures` sees the live enemy window and flips Britain to `guard`, Russia
joins the pool (100 -> 110.4), and the halved coverage becomes 55.2.
`probe_4_posture_flip.py`:

```
 ticks=0 fr_read=70 | SAME TURN posture=blockade  cov= 50.0 ratio=1.08 allowed=True
                    | NEXT TURN posture=guard     cov= 55.2 ratio=0.97 allowed=True
 ticks=1 fr_read=65 | SAME TURN posture=blockade  cov= 50.0 ratio=1.0  allowed=True
                    | NEXT TURN posture=guard     cov= 55.6 ratio=0.9  allowed=False
 ticks=2 fr_read=60 | SAME TURN posture=blockade  cov= 50.0 ratio=0.92 allowed=True
                    | NEXT TURN posture=guard     cov= 56.0 ratio=0.82 allowed=False
 ticks=3 fr_read=55 | SAME TURN posture=blockade  cov= 50.0 ratio=0.84 allowed=False
                    | NEXT TURN posture=guard     cov= 56.0 ratio=0.75 allowed=False
```

`probe_3_exact.py` gives the tick-1 case unrounded: `ratio=0.897302` against floor 0.90 -
**the second turn of a two-turn window closes by 0.0027**, for a reason (an enemy posture
flip that the player's own window caused, which ADDS a third navy to the coverage pool) that
appears on no surface at all.

**(2) "four turns of blockade rot ... SHUT even inside the window" is not terminal - it
reverses.** `probe_2_rot.py` arm B (camp occupied from turn 3):

```
 t 3 read={'France': 55,...} blk=['France','Holland','Spain'] camp_turns=1 staged=False | ratio=0.75
 t 4 read={'France': 50,...} blk=[]  camp_turns=2 staged=True  GBposture=guard | ratio=0.7
 t 5 read={'France': 55, 'Spain': 55, 'Holland': 55,...}       camp_turns=3    | ratio=0.77
 t 6 read={'France': 60,...}                                                    | ratio=0.84
 t 7 read={'France': 65,...}                                                    | ratio=0.91 allowed=True
 t 9 read={'France': 75,...}                                                    | ratio=1.05 allowed=True
```

`derive_ai_postures` (naval.py) pulls an island fleet home to `guard` whenever an enemy camp
is staged or an enemy window is live; `guard` is not `blockade`, so `blockader_against`
stops returning Britain, France leaves `blockaded_nations`, and `_readiness_tick` switches
from the -5 rot to +5 toward `NAVY_DRILL_CEILING` 75. **Staging the camp is what un-blockades
France.** The row has this exactly backwards. The arc is not dead; it is *delayed by three to
five turns that nothing tells the player about*.

**(3) "staging the camp takes >=4 turns of marching" is right for the wrong province.**
`probe_3_exact.py` / `probe_4_posture_flip.py`:

```
  Ney         Rhineland      24000 -> Normandy 5 hops, Flanders 2 hops
  Davout      Rhineland      26000 -> Normandy 5 hops, Flanders 2 hops
  Soult       Lorraine       30000 -> Normandy 4 hops, Flanders 2 hops
  Napoleon    Lorraine       10000 -> Normandy 4 hops, Flanders 2 hops
  sea links touching London: [('London', 'Normandy')]
```

`camp_staged` is satisfied at Flanders in 2 marching turns + 2 standing turns (staged end of
t4) - but **NV-8c left London exactly one sea link, and it is Normandy**, which is 4 hops for
the nearest 40,000-man pair (Soult 30k + Napoleon 10k) and 5 for Ney+Davout. So the flag that
flips Britain to guard and the beach the army must actually embark from are different
provinces, and the arithmetic that matters (men standing at Normandy) is a turn-5 event at
best.

#### The defect that survives - stated precisely

Every surface that offers the once-per-war card quotes the roll and nothing about the water:

- `naval.py::build_admiralty_report`, the `diversion_terms` list - three booleans:
  `[('a fleet in commission', True), ('at war with a naval power', True),
    ('the diversion not yet spent this war', True)]` (`probe_5`).
- the Diversion chip's `note` (same function, chips block) -
  `'45% - and once only, this war; no army is staged to use the open water'` (`probe_3`).
- `naval_executor.py::NavalExecutor::_execute_naval_diversion`, the `not confirmed` arm
  (`probe_5`): *"...45 times in 100 the strait opens for 2 turns; otherwise she is caught
  coming home and fights at readiness 40. Sail? (yes / no)"*

`diversion_used` is set on success AND failure and clears only at full peace
(`process_naval_turn`: `if rec.get("diversion_used") and not world.get_nations_at_war_with(nation)`),
so the card is unrecoverable. The player learns the truth only afterwards, from the Crossings
line: `London-Normandy: SHUT - the Royal Navy at 2.6x` (`probe_5`).

**And the chip's one warning is inverted in effect.** It fires while the camp is UNSTAGED -
which is precisely the window in which the ratio is still winnable (ticks 0-2, same-turn
1.08/1.00/0.92) - and it goes SILENT once the camp is staged, which on the natural timing is
the state where the strait is certainly shut (t4, 0.79/0.70). That silence is pinned today
by `tests/test_naval_host_rule.py::test_the_warning_clears_once_the_camp_is_staged`.

**GR5 sibling, same blindness, worse:** `naval.find_ai_diversion` *gates on* `camp_staged`
("no army on the beach - a window would open onto nothing"), i.e. the AI is steered into
exactly the state the measurement shows is worthless.

**A published-number gap worth recording:** the §14/§15 anchors (0.53 shut / 1.07 window /
0.74 no-Spain) are produced by `tests/test_naval_descent.py::_at_drill_ceiling`, whose own
docstring says "§5.3.4's *steady state*": Britain forced to `guard`, France/Spain/Holland
forced to `NAVY_DRILL_CEILING` 75. That is a state the shipped board reaches only *after*
staging lifts the blockade and five turns of recovery. **No test measures the crossing at any
readiness the player actually holds during the run-up**, which is why this was invisible.

#### (a) True seam, by symbol

- `backend/game_logic/naval.py::build_admiralty_report` - the local `diversion_terms` list
  and the Diversion entry in the `chips` list (the row's `naval.py:2091` is the *function
  head* of `build_admiralty_report`, not `diversion_terms`; there is no `diversion_terms`
  symbol to add a row to).
- `backend/commands/naval_executor.py::NavalExecutor._execute_naval_diversion` - the
  `if not confirmed:` quote arm.
- `backend/game_logic/naval.py::resolve_diversion` - the success arm that sets
  `window_turns` without re-deriving postures.
- `backend/game_logic/naval.py::derive_ai_postures` + `::covering_fleets` (the
  `match_posture` pooling) - the mechanism that makes the flip a coverage change.
- `backend/game_logic/naval.py::find_ai_diversion` - the GR5 sibling.

#### (b) What the row's own filed fix would BREAK

1. **It would make the forecast lie in the opposite direction.** The row prescribes
   evaluating `crossing_check` "with ... the island fleet's derived-guard posture". That is
   the NEXT turn's coverage (55.2/55.6/56.0). On the diversion turn the player marches under
   the *same-turn* postures (50.0). At tick 1 the row's forecast would print `0.90 - even a
   success leaves it shut` while a success actually opens the strait that turn at 1.00. A
   shown != applied fix that ships a new shown != applied.
2. **"make it a fourth `diversion_terms` row" would disable the verb.**
   `report["diversion_available"] = all(t["met"] for t in diversion_terms)` and the chip is
   built from it - a forecast row with `met: False` turns the Grand Diversion chip
   `enabled: False`, contradicting the design decision recorded at the chip
   ("A warning, never a lie: it stays clickable, because it works") and flipping
   `tests/test_naval_host_rule.py::test_the_diversion_chip_warns_about_the_trap_it_cannot_gate`
   (`assert diversion["enabled"] is True`) plus `::test_every_term_carries_both_phrasings`
   (every term needs an `unmet` phrasing) and the dark-chip-needs-a-reason census.
3. **The hardcoded `London-Normandy` breaks GR5.** `find_ai_diversion` is nation-generic;
   the forecast must derive its link from the actor's own sea links to an island war enemy
   (`_island_war_enemies` + `get_sea_link_pairs`), not from a literal.
4. Its quoted numbers ("41.3 vs 55.2") are unreachable on the shipped board - the row's own
   repro sets `fr['ships']=49` (four keels built). The board's number is 39.3.

#### (c) Minimal correct fix

1. **One pure helper**, `naval.window_forecast(world, actor)` - the `blockade_forecast`
   idiom. Save `actor_rec["window_turns"]` and every fleet record's `posture` in a
   `try/finally`; set `window_turns = WINDOW_TURNS`; run `crossing_check` for each sea link
   between the actor's provinces and an island war-enemy's; restore. Return the best link:
   `{link_a, link_b, ratio, floor, coverage, mover_effective, would_open}`.
2. **Resolve the same-turn/next-turn ambiguity at the source, not in the copy:** have
   `resolve_diversion`'s success arm call `derive_ai_postures(world)` immediately after
   setting `window_turns`, so the window's two turns are the same strength and the forecast
   is a single honest number. This is a *conscious behaviour flip* (boot same-turn 1.08 ->
   0.97, still OPEN, so the §14 A4 anchor is unaffected; the tick-1 case 1.00 -> 0.90 flips
   SHUT and must be measured). If that flip is not wanted, the forecast must quote the
   *worst* of the two and say why.
3. **Three readers, none of them a gate:** a new `report["diversion_forecast"]` key beside
   `diversion_terms` (never inside it - `diversion_available` must stay a three-boolean
   product); the chip `note`, which keeps `enabled: True`, keeps "45% - and once only", keeps
   the camp clause as a *second* clause and gains the forecast sentence; and the
   `_execute_naval_diversion` confirm message.
4. **Say the remedy, since it exists:** when the forecast is shut and the actor is blockaded,
   the honest sentence is that staging the camp lifts the blockade and readiness recovers
   +5/turn to 75 - the measured arc (t4 0.70 -> t7 0.91 -> t9 1.05). That turns the row from
   a warning into the tutorial the Descent never had.

#### (d) Tests that pin today's behaviour and would flip

| test | assertion |
|---|---|
| `tests/test_naval_host_rule.py::test_the_diversion_chip_warns_about_the_trap_it_cannot_gate` | `assert diversion["enabled"] is True` ; `assert "no army is staged" in diversion["note"]` ; `assert str(naval.DIVERSION_SUCCESS_PCT) in diversion["note"]` |
| `tests/test_naval_host_rule.py::test_the_warning_clears_once_the_camp_is_staged` | `assert "no army is staged" not in chips["order the diversion"]["note"]` - survives textually but stops being a pin; needs a positive assertion |
| `tests/test_naval_host_rule.py::test_every_term_carries_both_phrasings` | every `diversion_terms` row needs `unmet` - reds if a forecast row is added there |
| `tests/test_naval_host_rule.py` (dark-chip census, ~line 445) | `for chip in ...["chips"]: if not chip["enabled"]: assert chip["reason"]` |
| `tests/test_naval_host_rule.py::test_a_withheld_chip_reads_forwards_not_backwards` | `assert diversion["reason"] == "the diversion is already spent this war"` |
| `tests/test_pc15_fix_slice_2026_08_15.py::test_bare_diversion_quotes_and_does_not_burn_the_attempt` (:651) | asserts the confirm arm and `assert not world.fleets["France"].get("diversion_used")` (:674) - the message text changes |
| `tests/test_pc15_fix_slice_2026_08_15.py::test_confirmed_diversion_resolves` (:677) | `assert world.fleets["France"].get("diversion_used") is True` |
| `tests/test_naval_descent.py::TestTheDescentArc::test_the_combined_fleet_with_a_window_opens_it` (:143) | `assert verdict["ratio"] == pytest.approx(1.07, abs=0.03)` - green either way (fixture already forces guard), but a BOOT-readiness pin must be added beside it |
| `tests/test_naval_descent.py::test_without_a_window_the_strait_is_hopeless` / `::test_no_proper_subset_opens_it` | `0.53` / `0.74`, both via `_at_drill_ceiling` |
| `tests/test_wo_slice6_the_admiralty_speaks_plainly.py` | reads chips/terms |

---

### FA-S9-D1 - the `recall <marshal>` verb (design reconnaissance)

Probe: `probe_6_admin_serial.py`.

#### (a) The debug restore - every line of state it touches

`backend/commands/meta_executor.py::_execute_debug`, the `elif ability == "admin" or ability
== "administrative":` arm (the RESTORE half, when `marshal.administrative` is already True):

```python
marshal.administrative = False
strength = getattr(marshal, 'administrative_strength', 0)
location = (getattr(marshal, 'administrative_location', None)
            or world.get_nation_capital(marshal.nation) or 'Paris')
marshal.strength = strength
marshal.location = location
marshal.clear_iron_resolve()          # MC-1c: back on the map, no coil
world.bonus_actions = max(0, getattr(world, 'bonus_actions', 0) - 1)
# message quotes world.calculate_max_actions()
```

Five writes plus one derived read. Notes for the build: it does NOT clear
`administrative_strength`/`administrative_location` (stale values survive); it does NOT
rebuild the marshal index (`world._build_marshal_index()`) after changing `location` from
`None`; and its fallback is the literal string `'Paris'`, which is wrong for a fallen capital
and wrong for any non-France actor.

#### (b) What the redemption arm freezes

`backend/commands/disobedience.py::handle_redemption_response`, `elif choice ==
'administrative_role':`

```python
# Store data for future restoration (Phase 4)
marshal.administrative = True
marshal.administrative_strength = marshal.strength
marshal.administrative_location = marshal.location
marshal.strength = 0
marshal.location = None
marshal.clear_iron_resolve()
world.bonus_actions = getattr(world, 'bonus_actions', 0) + 1
```

Measured end-to-end (`probe_6`):

```
handler: True Murat has been transferred to administrative duties. Their 22,000 troops
         await future assignment. You now have 5 actions per turn.
after : administrative True strength 0 loc None admin_strength 22000
        admin_location Franche-Comte bonus_actions 1 max_actions 5
```

#### THE BLOCKER - the frozen state is not serialized

```
Marshal.to_dict has 'administrative'      : False
Marshal.to_dict has 'administrative_stren': False
Marshal.to_dict has 'administrative_locat': False
WorldState.to_dict has 'bonus_actions'    : True

AFTER SAVE/LOAD:
  administrative      : <absent>
  administrative_stren: <absent>
  administrative_locat: <absent>
  strength/location   : 0 None
  bonus_actions       : 1 max_actions 5
  get_field_marshals  : 8 admin: 0
=> the debug restore after a load would give him strength 0 at None
```

Consequences, all measured or read:
- the 22,000 men are **deleted** by a save/load;
- the `+1 action` is **kept forever** (`bonus_actions` is serialized);
- `get_admin_marshals()` returns 0, so the one-admin rule is reset and a second marshal may
  be sent to the Staff for a second permanent AP;
- `world_state.py`'s attrition exemption reads `getattr(m, "administrative", False)`, so the
  slice-9 fix `ADMINISTRATIVE_EXEMPT_FROM_ATTRITION` is defeated by a load - the zero-strength
  ghost becomes eligible for the sweep again;
- `tests/test_serialization_enforcement.py::test_all_marshal_fields_serialized` cannot see
  this: its field census is `{k for k in vars(obj).keys() if not k.startswith('_')}` on a
  FRESH object (`:40`), and these three attributes exist only after the redemption arm runs.

**Build order consequence: declare the three fields in `Marshal.__init__` and add them to
`to_dict`/`from_dict` BEFORE writing the verb.** Otherwise `recall` restores 0 men at `None`
on every loaded campaign, and the slice ships a worse bug than the one it fixes.

#### (c) The 12-step checklist, with `recruit_marshal` quoted at every site

| # | Site | `recruit_marshal` precedent (verbatim) | what `recall_marshal` must do |
|---|---|---|---|
| 1 | `backend/ai/validation.py` `VALID_ACTIONS` | `:99` `"recruit_marshal",` | add `"recall_marshal"` |
| 1b | same file, `ADMINISTRATIVE_ACTIONS` | `:197` `"grant_pension", "revoke_pension", "grant_dotation", "recruit_marshal",` | **mandatory** - otherwise `NEVER_STRATEGIC_ACTIONS` misses it and `recall Murat to Paris` upgrades into a 2-AP MOVE_TO (the FA slice-7 `withdraw Ney's rente` pathology, documented in that block's own comment) |
| 2 | executor body | `backend/commands/economy_executor.py:787` `def _execute_recruit_marshal(self, command: Dict, game_state) -> Dict:` | new `_execute_recall_marshal`; `economy_executor` is the closest home by symmetry (it already owns `grant_dotation`/`grant_pension`), `meta_executor` by subject |
| 2b | dispatch | `backend/commands/executor.py:2315` `elif action == "recruit_marshal":` / `:2316 result = self._economy._execute_recruit_marshal(command, game_state)` | one `elif` |
| 2c | admin-AP seam | `backend/commands/meta_executor.py:31` `ADMIN_ACTIONS = {"recruit", "build", "repair", "grant_dotation", "grant_pension", "revoke_pension", "recruit_marshal", "build_fleet"}` | add `"recall_marshal"` - this is what makes it 1 *admin* AP |
| 3 | `backend/commands/parser.py` `valid_actions` | `:836` `"recruit_marshal",  # "commission Grouchy" - 1 admin AP + gold` | add the row |
| 3b | parser target arm | `:1012-1030` (the `recruit_marshal` "marshal"->target move, because a candidate is not a live marshal) | **hazard, opposite direction:** the recall target IS in `world.marshals` but has `strength == 0` and `location is None`, and the roster helpers deliberately exclude him - `clarification.py:139` (`if m.strength > 0`), `world_state.py::find_nearest_marshal_within_range` (`:3651-3654`, comment "Must be alive and in field (not administrative)"), `world_state.py::get_marshals_by_nation` (`and marshal.strength > 0`). Verify the addressee resolution finds an administrative marshal, or add an explicit lookup. |
| 4 | `backend/models/world_state.py` `_action_costs` | `:976` `"recruit_marshal": 1,` | `"recall_marshal": 1` |
| 5 | `backend/ai/llm_client.py` mock parser | `:1971-1980` the `elif (("commission" in command_lower and not _mentions_pension(...)) or re.search(r'\brecruit\b.{0,12}\bmarshal\b', ...) ...): action = "recruit_marshal"` block, with its explicit ORDERING RULE comment | new arm - and it **must sit BELOW the `set_fleet_posture` arm at `:1966-1969`** (`re.search(r'\bfleet\b', ...) and re.search(r'\b(guard|recall|port|station)\b', ...)`). `recall` is claimed as a guard noun and a posture verb by `naval.py::_GUARD_NOUN_RE` (`:173`) and `::_POSTURE_VERB_RE` (`:200`), so `recall the fleet` must stay `set_fleet_posture` and `recall Murat` must be the new verb. Pin both directions. |
| 5b | target extraction | `:2188-2196` `if action == "recruit_marshal": _rm = re.search(r'\b(?:commission\|appoint)\s+(?:marshal\s+)?([a-z][a-z\'-]+)', ...)` | only needed if 3b shows the ordinary ladder misses him |
| 6 | `backend/ai/prompt_builder.py` few-shot | **zero hits for `recruit_marshal`** - the precedent shipped with no few-shot (the Valid Actions block is generated from `VALID_ACTIONS`) | optional; one line if the live parser confuses it with `retreat`/`cancel` |
| 7 | `backend/commands/disobedience.py` `objection_actions` | **zero hits** - an administrative act draws no objection | leave out, deliberately, and pin the absence |
| 8 | serialization | n/a for `recruit_marshal` (no new fields) | **the blocker above**: `administrative`, `administrative_strength`, `administrative_location` into `Marshal.__init__` + `to_dict` + `from_dict` (`.get()`-defaulted), then `docs/SAVE_FORMAT_REFERENCE.md` |
| 9 | `backend/display_names.py` | `:49` `"recruit_marshal": "commissions",` ; `:164` `"recruit_marshal": "commissioning a marshal",` ; `:213` `"recruit_marshal": "commissioned a marshal",` | three rows |
| 10 | `backend/campaign_log.py` `_DEFIANCE_DISPLAY` / `_OBJECTION_DISPLAY` (~:21 / ~:43) | inherits from `display_names` | mirror |
| 11 | `backend/campaign_log.py` event type | `:258` `"marshal_commissioned",` in `CAMPAIGN_LOG_TYPES` ; `:363` `"marshal_commissioned": "command",` ; `:988` in the always-visible list ; `:1553` `if event_type == "marshal_commissioned":` in `format_event_oneliner` | four sites; **the standing `len(CAMPAIGN_LOG_TYPES) == N` pins in five files must be flipped consciously** |
| 12 | `tests/data/parser_golden_corpus.json` | 4 rows (`entries`, 436 total): `jv32-commission-grouchy`, `jv32-recruit-marshal-suchet`, `jv32-appoint-marshalate`, and the negative guard `jv32-recruit-infantry-unharmed` | same shape: two positives (`recall Murat`, `recall Murat to the field`), plus **two** negative guards - `recall the fleet` -> `set_fleet_posture` and `recall the fleet to home waters` -> `set_fleet_posture`. `tests/test_command_robustness_cr1_eval_harness.py`'s action-coverage gate FAILS CI for any mock-reachable action with zero corpus coverage, so this step is mandatory, not optional. |

Client sites (not in the 12, but the verb is player-facing): `redemption_dialog.gd:77-79`
(the admin button text/tooltip, fed from the option `text`/`description`), `main.gd:4327`
(the typed-choice hint line), `main.gd:4350-4354` and `:4405-4412` (the "TRANSFERRED TO THE
STAFF" banner, WO-36's fix), and the Generals card if a chip is wanted (the UX23-A
`action_command`/`action_label`/`action_detail` idiom is the precedent).

#### (d) The richest-home-province helper already exists

`backend/game_logic/recruitment.py::find_spawn_region(world, nation)` (`:95`):

```python
"""The capital while held; otherwise the richest still-held homeland
province; None when the nation has no soil to raise a corps on."""
```

It reads `world.get_nation_capital`, checks `capital_region.controller == nation`, then walks
`world.nation_starting_regions[nation]` by `region.get_effective_income()`. **Reuse it
verbatim** - it is exactly the blessed wording ("the capital or richest home province") and
it already handles the fallen-capital case the debug arm gets wrong (`or 'Paris'`).
Preference order for the recall should be `administrative_location` if still held by the
nation, else `find_spawn_region`, else refuse honestly.

#### (e) What the copy promises now, and what it must say

Two strings, both live:

- option description, `disobedience.py::_create_redemption_event` option builder:
  `f"{marshal.name} joins the administrative staff. Troops frozen for future restoration. You gain +1 action per turn."`
- handler message, `handle_redemption_response`:
  `f"{marshal_name} has been transferred to administrative duties. Their {marshal.administrative_strength:,} troops await future assignment. You now have {int(new_max_actions)} actions per turn."`

plus the code comment `# Store data for future restoration (Phase 4)` and the button label
`"Transfer {name} to Staff"` (client fallback `"Transfer to Staff (+1 action)"`).

Once the verb exists both strings must name it and its price, e.g. *"...their N troops are
frozen at <location>; order `recall <name>` to return him and them to the colours - one
administrative action, and not before turn X."* Until it exists the honest words are
"permanently" / "for the rest of the campaign" (option (b) of the gate).

#### (f) Tests that must move, and the serialization implications

Serialization: **yes, three new serialized fields** (see the blocker). Nothing else is new -
`bonus_actions` is already on `WorldState.to_dict`, the cooldown can reuse the existing
`redemption_cooldown_until` idiom in `disobedience.py`.

Files that grep `administrative` under `tests/`:
`test_administrative_role.py`, `test_ai_audit_2026_07.py`,
`test_command_robustness_cr2_clarification.py`, `test_economy_upkeep_bankruptcy.py`,
`test_endpoint_wiring.py`, `test_fa26_the_question_is_asked_2026_09_05.py`,
`test_fa_slice7_the_mock_speaks_plainly_2026_09_04.py`, `test_naval_channel_gate.py`,
`test_naval_host_rule.py`, `test_objection_v2.py`, `test_pt_j_rulings.py`,
`test_recruitment_rework.py`, `test_redemption_v2b.py`,
`test_ux23a_reward_where_he_stands.py`, `test_wo_slice18_answer_finds_its_question.py`.

The ones that actually pin the arm's state:

| test | assertion |
|---|---|
| `tests/test_administrative_role.py::test_admin_role_stores_strength` (:25) | `assert ney.administrative is True` ; `assert ney.administrative_strength == original_strength` ; `assert ney.strength == 0` |
| `::test_admin_role_stores_location` (:44) | stores `administrative_location` |
| `::test_admin_role_increments_bonus_actions` (:64) | `assert world.bonus_actions == 1` - the recall must decrement it |
| `::test_admin_role_increases_max_actions` (:80) / `::test_admin_role_result_includes_new_max_actions` (:95) | max actions 4 -> 5 |
| `::test_admin_role_not_available_if_one_exists` (:113) | `assert len(world.get_admin_marshals()) == 1` |
| `::test_get_field_marshals_excludes_admin` (:343) | `assert len(world.get_field_marshals()) == 3` ; `assert 'Ney' not in field_names` |
| `::test_get_admin_marshals_includes_admin` (:363), `::test_excludes_admin_marshals` (:437) | roster helpers |
| `::test_bonus_action_persists_after_advance_turn` (:298), `::test_multiple_turns_maintain_bonus` (:321) | the AP must survive turns - and must NOT survive the recall |
| `tests/test_fa26_the_question_is_asked_2026_09_05.py::test_an_administrative_man_survives_the_attrition_sweep` (:582) | `assert lannes.administrative is True and int(lannes.administrative_strength) == frozen` - green after serialization, and it is the natural place for a save/load arm |
| `tests/test_serialization_enforcement.py::test_all_marshal_fields_serialized` (:214) | field census via `vars()` on a fresh object (`:40`) - **blind today by construction**; it starts binding the three fields the moment they move into `__init__`, and will go RED until `to_dict`/`from_dict` carry them |

---

## Cross-row findings

1. **NEW, not filed anywhere I could find: the administrative-role state does not survive a
   save/load.** Three attributes absent from `Marshal.to_dict`/`from_dict`; measured
   consequences above (troops deleted, AP kept forever, one-admin rule reset, slice-9
   attrition exemption defeated). This is a P2 in its own right and a hard prerequisite for
   FA-S9-D1. It is adjacent to FA-N77 (`get_field_marshals` counting prisoners) but is a
   different defect: after a load, `get_field_marshals` counts the *administrative ghost*
   too, because the flag it filters on is gone.
2. **`resolve_diversion` does not re-derive postures**, so a two-turn window is not two
   equal turns: measured 1.08 -> 0.97 at boot, 1.00 -> 0.90 (`allowed=False`) at tick 1. The
   cause is that `derive_ai_postures` flips the island fleet to `guard` and `covering_fleets`
   pools by matching posture, so the guard flip *recruits* Russia's squadron into Britain's
   coverage (100 -> 110.4). Neither the flip nor the pooling change is on any surface.
3. **The `_at_drill_ceiling` fixture is why FA-31 was invisible.** Every published Descent
   number is measured on the post-blockade steady state. A boot-readiness pin on the descent
   arc is missing and should be added regardless of which fix lands.
4. **`find_ai_diversion` gates on `camp_staged`**, i.e. the AI is *required* to be in the
   state the measurement shows is worthless. GR5 means any forecast fix must be readable by
   the AI rung too, not just by the three player surfaces.
5. **`recall` is already claimed vocabulary.** `naval.py::_GUARD_NOUN_RE` and
   `::_POSTURE_VERB_RE` both match it, and `llm_client.py:1969` routes
   `fleet` + `recall` to `set_fleet_posture`. The new verb must be pinned against both
   directions or it will eat "recall the fleet" (the FA slice-7 naval-verb-vs-addressed-
   marshal family, one verb further on).
6. **Harness note:** calling `naval.derive_ai_postures` from a probe to read a ratio
   *changes what you are measuring* - it applies next turn's posture to this turn's board.
   My probe 2 printed contaminated posture/blockade columns for that reason (the readiness
   trajectory it reports is uncontaminated, because `_readiness_tick` runs inside
   `process_naval_turn` before the helper touched anything). `probe_4`/`probe_5` measure both
   states explicitly and are the ones to trust.

## Probe inventory

All under `<scratchpad>/repro/j4/`:

- `probe_1_boot.py` - boot fleet records, blockade set, camp strength, the 53.8 / 55.2 / 0.97
  window arithmetic, per-fleet posture and pooling table.
- `probe_2_rot.py` - three arms over 10 turns (no camp / camp from t3 / camp from t1):
  readiness trajectories, blockade set, camp_turns, and the window ratio each turn.
- `probe_3_exact.py` - unrounded boot and tick-1 ratios (0.975000 / 0.897302), BFS distances
  from every French marshal to the camp provinces, the Crossings line, `diversion_terms` and
  the chip note.
- `probe_4_posture_flip.py` - same-turn vs next-turn coverage and ratio at ticks 0-4; the
  London sea-link census; Normandy vs Flanders hop counts.
- `probe_5_chip_and_ai.py` - the honest staged-camp board at t4, the typed confirm message,
  the forced-win crossing verdicts, and the source of `naval.find_ai_diversion`.
- `probe_6_admin_serial.py` - the redemption administrative arm end to end plus the
  `to_dict`/`from_dict` round trip that deletes it.
