All probes under `…/scratchpad/s14/refute_G_redemption/`: `r1_n77_n76.py`, `r2_n46.py`, `r3_n46_controlled.py`, `r4_filed_fix_p1.py`, `r5_filed_fix_p1b.py`, `r6_series.py` + `r7_diff.py`, `r8_misc.py`, `r9_opt3_pin.py`. Repo untouched.

**Method note first, because it changes how these probes must be re-run.** The working tree at the moment I ran is **not clean** — 27 modified files carrying an in-flight slice-14 build of *all three* rows (`disobedience.py` +36, `main.py` +27, `marshal.py` +29, `world_state.py` +60, `test_administrative_role.py` +20). The reporter's "clean before and after" was true when they ran; it is not true now, and anyone re-running their scripts against the live tree will measure the **fix**, not the defect. I measured defects against a `git archive 9ef38da8` snapshot at `…/refute_G_redemption/head/`, and fix-side claims against the live tree.

---

## FA-N77 — prisoners counted as field marshals

**CLAIM** `get_field_marshals()` returns 8 with 7 prisoners while `get_marshals_by_nation` returns 1; the last standing man is offered `dismiss`; dismissing him empties the roster.

**MY MEASUREMENT** (`r1_n77_n76.py`, committed snapshot, 1805 boot, every French marshal but Lannes captured):

```
standing (strength>0):  ['Lannes']
get_field_marshals() -> 8   strengths {Ney:0 … Lannes:18000 … Napoleon:0}
get_marshals_by_nation('France') -> 1
check_redemption_threshold OFFERED: ['grant_autonomy','administrative_role','dismiss']
WITH FILTER  -> 1 ;  OFFERED ['grant_autonomy']
control (2 standing): offer byte-identical before and after
POST /respond_to_redemption {"dismiss"} -> True
  "Lannes has been relieved of command. 18,000 troops dispersed - no nearby commanders…"
  fallen_marshals ['Lannes'] ; French standing after: []
```

**VERDICT: CONFIRMED**, verbatim, including the six-caller census (`clarification:139`, `context_carryover:331`, `delegation:295`, `disobedience:1572`, `meta_executor:1520/1574`) and the "exactly four unguarded" split.

**CLAIM** every line number in the row is stale. **MY MEASUREMENT:** the report's *corrections* are exact — `get_field_marshals` 3593‑3604, `find_nearest…` 3619, `get_marshals_by_nation` 3676, `capture_marshal` 4604, `field_count < 2` 1593. **VERDICT: CONFIRMED with two off-by-ones of its own** — `clarification.py`'s **call** is at 139 (the row's own number is right; 140 is the `strength > 0` guard), and `context_carryover`'s call is at **331**, not 330. The report also writes `meta_executor.py:1521`/`:1575` in the N76 section and `1520-1524`/`1574-1585` in the N77 table; the calls are at 1520/1574.

**CLAIM** the filed fix breaks nothing; `context_carryover` is the only caller whose output changes and both paths give the same player-visible answer. **MY MEASUREMENT** (`r8_misc.py`, both trees):

```
committed:  _field_marshal_names contains Ney -> True
live/built: _field_marshal_names contains Ney -> False
both trees, POST /command 'Ney, do the same'  -> "Marshal Ney is a prisoner of Austria, Sire…"
both trees, POST /command 'Ney, same target'  -> "Marshal Ney is a prisoner of Austria, Sire…"
```

**VERDICT: CONFIRMED.** One sub-claim **NARROWED**: the report's quoted fixture (`'Ney, do the same'` → `'Ney, move to Bavaria'`) is not reproducible on the 1805 board — `move to Bavaria` is refused (*"Bavaria is a nation, not a province"*). Don't copy that fixture.

**CLAIM** an administrative marshal is at strength 0, so the new clause is additive. **MY MEASUREMENT:** `administrative_role` → strength 24,000 → **0**, drops out of `get_field_marshals`. `grant_autonomy` → strength 26,000 → **26,000**, stays in. **VERDICT: CONFIRMED**, and the autonomy case (which the report did not name) is the one that could have been an unintended exclusion — it isn't.

---

## FA-N76 — the choice is not validated

**CLAIM** three consecutive `administrative_role` answers farm `bonus_actions` 0→3.

**MY MEASUREMENT** (`r1_n77_n76.py` arm 3, real endpoint, TestClient, all three of `M.world`/`M.game_state`/`M.parser` swapped):

```
max_actions at boot: 4  bonus 0
Ney    OFFERED [grant_autonomy, administrative_role, dismiss]
       -> True | admins ['Ney']                  | actions 5 | bonus 1
Davout OFFERED [grant_autonomy, dismiss]   <-- not offered
       -> True | admins ['Ney','Davout']         | actions 6 | bonus 2
Soult  OFFERED [grant_autonomy, dismiss]   <-- not offered
       -> True | admins ['Ney','Davout','Soult'] | actions 7 | bonus 3
```

**VERDICT: CONFIRMED** to the digit.

**CLAIM (the report's own extra finding)** the handler clears the latch and stamps the cooldown *before* dispatching, so an invalid choice is refused at a price. **MY MEASUREMENT:** `handle_redemption_response(..., choice="banana")` → `success False`, and `redemption_pending` False, `redemption_cooldown_until` 6. **VERDICT: CONFIRMED.**

### The P1 — the filed fix shape ships a dead channel

This is the claim most worth killing, so I built the geometry where the guard actually fires (Ney takes the admin post legitimately; Davout's audience then offers `['grant_autonomy','dismiss']`; post `administrative_role`). `r5_filed_fix_p1b.py`, committed snapshot:

```
BASELINE (no guard)   -> True  | admins ['Ney','Davout'] | bonus 2     <- the exploit
ARM 1 FILED SHAPE     -> False | admins ['Ney']  bonus 1              <- rule enforced
   world.pending_redemption   : None
   Davout.redemption_pending  : True
   standing_redemption(world) : None
   can Davout ask again NOW   : NO
   after 15 turns             : still NO (trust 15, pending True)
   a LEGAL answer             : False | "No redemption event pending."
ARM 2 CORRECTED (conditional clear)
   world.pending_redemption   : SET
   standing_redemption(world) : SET
   follow-up grant_autonomy   : True | "Davout has been granted autonomy…"
```

**VERDICT: CONFIRMED, exactly as filed.** The mechanism is also exactly as the report states: `standing_redemption` returns at its `isinstance(event, dict)` check when `pending_redemption` is already `None`, so it never reaches the latch release at `:693`, and `check_redemption_threshold` refuses forever at `:1688`.

**CLAIM** the "simpler correct siting" is `main.py:4045`, because its refusal at `:4046-4048` is an early return above the clear at `:4058` and `_refusal_response` (`:472`) does not touch `pending_redemption`. **MY MEASUREMENT** (`r4_filed_fix_p1.py` arm 3, posting a malformed id so the static list refuses): `pending_redemption` **SET**, `redemption_pending` True, `standing_redemption` SET, follow-up `grant_autonomy` → **True**. **VERDICT: CONFIRMED.**

**CLAIM** the corrected shape flips exactly one pin, the `'Invalid choice' in message` assertion at `test_administrative_role.py:471-474`. **MY MEASUREMENT:** against the live built tree, `test_administrative_role + test_autonomy + test_redemption_v2b + test_wo41 + test_fa26 + cr4_carryover + cr2_clarification + pf2_delegation + pc15_8_delegation` = **313 passed**, and `git diff` shows exactly one test body edited — that one, re-pointed consciously and strengthened (it now also pins `ney.redemption_pending is True` and `cooldown == 0`). **VERDICT: CONFIRMED.**

---

## FA-N46 — the rente-payer forfeits his grace window

**CLAIM** paid by rente he erodes on the turn the victory lands; paid by estate he gets a fresh window.

The report's own arms were **not instrument-controlled** (its rente arm carried an 80g shortfall against the estate arm's 70g — an artefact it flags itself). I rebuilt them with satisfaction held identical at 50g, expectation 40 → 120 at t=12, so the shortfall is 70 in **both** (`r3_n46_controlled.py`, committed snapshot, estate = Nivernais at 50):

```
OPT0 rente : t=12 eroding=True immediately … t=17 trust 73, grace frozen at 1
OPT0 estate: t=12 grace 12 (fresh window), erosion opens t=16 … t=17 trust 81
OPT0 churn : erodes on schedule … trust 79   <- WO-18's own case untouched
```

**VERDICT: CONFIRMED and STRENGTHENED** — with the artefact removed the gap is exactly the four grace turns (8 trust points), and the instrument is the only variable.

**CLAIM** a frozen clock survives `to_dict`/`from_dict`, so the stamp must be serialized. **MY MEASUREMENT:** grace 1 / pension 40 before and after; committed `to_dict` carries only `expectation_grace_turn` and `last_expectation_seen`. **VERDICT: CONFIRMED.**

**CLAIM** OPT2 (re-anchor on `pension > 0`) is catastrophic; OPT3 (roll the anchor) re-opens WO-18 and reds both assertions of `test_churn_now_erodes_after_grace_regardless_of_the_toggle`.

```
OPT2 rente arm: grace 12,13,14,15,16,17 … trust 85 forever  -> permanently immune
OPT3 on the PIN's own geometry (r9_opt3_pin.py, first_unmet=11, the pin's number):
   TODAY  grace=11 trust 85->82   assert grace==first_unmet PASS | assert trust<trust0 PASS
   OPT3   grace=13 trust 85->85   assert grace==first_unmet RED  | assert trust<trust0 RED
```

**VERDICT: CONFIRMED, both.** (I first thought the OPT3 "trust unchanged" was length-dependent — it is, in general, since the roll buys back exactly the paid turns — but on the pin's five-step geometry it is literally 85→85 and both assertions red. The report is right.)

### The series claim — the one I most expected to break

**CLAIM** series byte-identical, the branch fires 3 times in 40 turns, `freeze_events` 17, and **ArchdukeJohn 89 → 96** with every other marshal identical.

I ran the harness's own recipe (`PYTHONHASHSEED=0 SOVEREIGN_SEED=historical LLM_MODE=mock`, `random.seed(10_000 + turn)`, 40 `tm.end_turn`) twice on the **live built tree**, arm 0 neutralising the new field through a property so the stamp can never be read (`r6_series.py`/`r7_diff.py`):

```
arm0 series == BASELINE_SERIES : True
arm1 series == BASELINE_SERIES : True
provinces identical            : True
writes: arm1 freeze 17 clear 727 | arm0 freeze 17 clear 724   -> re-anchor fires 3
TRUST diffs (arm0 -> arm1): {'ArchdukeJohn': (89, 96)}
GRACE diffs: NONE
```

**VERDICT: CONFIRMED to the digit** — 17 freezes, 3 fires, ArchdukeJohn +7 and the only marshal who moves, series and province map unchanged. This is a measured claim, not an asserted one, and it survives on the *shipped* build rather than on a plugin.

**CLAIM** the six core dotation files are 320 pins. **MY MEASUREMENT:** 16 + 57 + 86 + 22 + 73 + 66 = **320**, exact; and those six plus serialization/e1_band = 210 green on the live built tree. **VERDICT: CONFIRMED.**

---

## What the reporter MISSED — a builder must know these

**1. `is_eroding` is stale for one phase after the FA-N46 fix, and one of its consumers is MECHANICAL, not cosmetic.** The report says *"`dotation.is_eroding` (:297) reads the same anchor, so the display and the mechanic agree — shown=applied."* Measured on the live built tree (`r8_misc.py`):

```
t=12 AFTER the battle, BEFORE the tick: exp 120 sat 40 grace 1 -> is_eroding True
t=12 AFTER the tick:                    grace 12          -> is_eroding False, trust 85
```

`is_eroding` is read by `marshal_overview.py:450` → `marshal_management.gd:531/540` and `reward_dialog.gd:50`, by `executor.py:2152` (the objection suffix), and — the one that matters — by **`jealousy.check_fontainebleau` (`jealousy.py:2256`)**, which counts eroding player marshals for the ESP‑1 collective petition. Ordering: `turn_manager.end_turn` runs `_jealousy_pass.process_turn` at `:302` and `world.advance_turn()` at `:312`, and `_process_dotation_state` is called at `world_state.py:9750` *inside* advance_turn. So Fontainebleau reads the **pre-tick anchor against the post-victory expectation**: a latched, 8-turn-cooldown petition can fire off a marshal the tick is about to spare. Either move the re-anchor decision into a pure predicate both readers share, or state the one-phase staleness on the record. Do not repeat "shown=applied".

**2. `debug_trigger_redemption` is the one production producer whose options do not reflect the board.** `main.py:5683` calls `_create_redemption_event(marshal)` with **no `world`**, taking the fallback at `disobedience.py:1649` — options are `['grant_autonomy']` only. Under FA-N76 a debug-triggered audience can no longer be answered with `dismiss` or `administrative_role` on any board. Pass `world` there, or record the debug-route change deliberately.

**3. FA-N76 + FA-N77 together make the playtest driver unable to resolve a redemption.** `tools/playtest_driver.py:153` defaults `"redemption": "dismiss"`, posted at `:1066` with no fallback. FA-N77 makes the offer-excludes-dismiss case *common* (it is exactly the last-standing-marshal state), and the corrected FA-N76 shape leaves the question **standing** after a refusal. The report flags the policy as a test arm but not the consequence: every future unattended digest can carry an unanswerable audience. Change the policy to first-offered in the same slice.

**4. FA-N76 silently changes what a refusal COSTS.** Today an invalid choice pays the latch clear and the 5-turn cooldown before refusing (measured: `pending False`, `cooldown 6`). The corrected shape refuses for free. That is the improvement — but it is a behaviour change to `redemption_cooldown_until`, and the single pin the report predicted would flip is precisely the one that had encoded the old cost. Name it in the record rather than letting it read as a copy tweak.

**5. Do not describe FA-N77 as a GR5 fix.** `get_field_marshals` is player-scoped by construction (`marshal.nation == self.player_nation`), so Last Marshal Protection has never existed for an AI nation and this row does not give it one.

**6. Build-order note stands, and is now load-bearing for a different reason.** The report's "FA-N77 before FA-N76" is right, and the in-flight tree has done both plus FA-N46 in one commit — which means points 2 and 3 above are live in that commit today.