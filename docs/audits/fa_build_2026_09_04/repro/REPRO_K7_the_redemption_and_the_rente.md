Repo untouched. Report follows.

---

# FA-N46 / FA-N76 / FA-N77 — reproduction report

Tree `9ef38da8`, clean before and after. All probes under
`…/scratchpad/s14/G_redemption/`:
`p1_n77_n76.py`, `p2_n76_tight.py`, `p3_filed_fix_regression.py`, `p4_n46.py`,
`p5_n46_options.py`, `p6_series_reach.py`, `p7_series_diff.py`, `p8_blast.py`,
`p9_misc.py`, plugins `plug_n46.py` / `plug_n76_literal.py` /
`plug_n76_corrected.py` / `plug_n77.py`, non-inert check `test_probe_live.py`.

**Headline: all three reproduce. FA-N76's own filed fix shape ships a P1
dead-channel regression, measured. FA-N46's filed fix shape is one of the rare
correct ones — I measured two zero-new-field alternatives and both fail, one
catastrophically.**

---

## FA-N46 — the rente-payer forfeits his grace window

### VERDICT: **REPRODUCED** (exactly as filed; magnitude confirmed, one sub-claim corrected)

### What Reproduces (`p4_n46.py`)

Same script, same shortfall, only the *instrument* differs. `GRACE_TURNS=4`,
`EROSION_MAX=3`, `SHORTFALL_PER_POINT=50`, `expectation_for_wins` = 0/40/80/120/160.

| | ARM A — paid by **rente** | ARM B — paid by **estate** |
|---|---|---|
| t=2 clock opens | `grace=2` | `grace=2` |
| t=3 paid | met → **FROZEN at 2** | met → **RESET to −1** |
| t=11 (8 quiet paid turns) | `grace=2`, trust 85 | `grace=−1`, trust 85 |
| `battles_won` 1→3 | exp 40→120 | exp 40→120 |
| t=12, first turn after | `eroding=True`, **trust 85→83** | `eroding=False`, **trust 85→85**, fresh `grace=12` |
| t=16 | **trust 75** (−10) | trust 83 (−2) |

`elapsed = 12 − 2 = 10` vs `GRACE_TURNS=4`. The rente-payer is **five turns
into erosion the instant he wins**, and shortfall 80 → `min(3, ceil(80/50)) = 2`
trust/turn. The estate-payer's shortfall is *larger* (70 vs… no — 70 vs 80, so
the rente-payer has the bigger gap by 10g, which is itself an artefact of the
estate being worth 50 against an expectation of 40) and he still loses 2 rather
than 10.

**ARM C confirms the guard's own case is untouched** — the grant/revoke churn
dodge still erodes at t=6 (trust 85→83 by t=8), exactly `first_unmet + GRACE_TURNS`.

**ARM D confirms the row's charge against the pin.**
`test_a_genuinely_kept_rente_never_erodes_and_charges_the_bill` holds
`battles_won` fixed at 5 for `GRACE_TURNS+3` turns; every turn takes the met
branch, so the frozen clock is never read and the pin is green about a case it
cannot see.

### What Is False / needs correcting on the row

1. **Every line number is stale.** `world_state.py:6145` → the real
   `_estate_covers` line is **6178**, the reset **6179–6180** (drift +33).
   `:6177` (`elapsed = …`) → real **6218** (+41). `dotation.py:85-101` → the
   WO-18 block is **88–108**; the quoted safety argument ("A marshal genuinely
   kept on a rente never erodes anyway…") is at **~101–108**, not 97–100.
   The `owner` cell `backend/models/world_state.py:6145` is wrong by 33 lines.
2. **The row understates the blast radius in one direction and overstates it in
   another.** It reads as a player-facing loyalty bug; the tick is
   nation-agnostic (GR5) and on the ambient board the *only* marshal whose
   outcome changes is **Austria's Archduke John** (see Series Risk).
3. The row's numbers ("clock frozen at 2, `is_eroding` True at turn 11") are
   truncated in the markdown; measured, it is frozen at 2 and `is_eroding`
   flips True at **turn 12** (the first tick after the win). Off by one in the
   row's own summary, immaterial.

### The Real Seam

- `WorldState._process_dotation_state` met branch — `_estate_covers` at
  **`backend/models/world_state.py:6178`**, the reset at **6179–6180**.
- `dotation.PENSION_CHURN_GUARD_ACTIVE` (**`backend/game_logic/dotation.py:108`**)
  is the flip lever; `GRACE_TURNS` at **:86**.
- The unmet read: `elapsed` at **`world_state.py:6218`**.
- `dotation.is_eroding` (**:297**) reads the same anchor, so the display and the
  mechanic agree — the row's "eroding" numbers are shown=applied.

### What The Filed Fix Would Break — **nothing; and it is the only shape that works**

The assignment asked me to think hard about a zero-new-field formulation. I
built and measured three (`p5_n46_options.py`), on the same five arms:

| | A rente+win (trust, Δ first turn) | B estate+win | C churn dodge | D kept rente | E grant/revoke |
|---|---|---|---|---|---|
| **OPT0 today** | **75, −2** | 83, 0 | ERODED ✔ | OK ✔ | OK ✔ |
| **OPT1 row's stamp** | **83, 0** ✔ | 83, 0 | ERODED ✔ | OK ✔ | OK ✔ |
| **OPT2 zero-field, `pension>0` re-anchor** | **85, 0** ✘ | 83, 0 | ERODED ✔ | OK ✔ | OK ✔ |
| **OPT3 zero-field, roll the anchor `+1` on a frozen met turn** | 81, 0 | 83, 0 | **DODGED** ✘ | OK ✔ | OK ✔ |

- **OPT2 is catastrophic**: the unmet branch cannot tell "first unmet turn of a
  run" from "the fifth", so the anchor re-sets *every* turn — measured `grace`
  ending at 16 with `current_turn` 16, i.e. **a rente-paid marshal becomes
  permanently immune to erosion**. Rejected by measurement.
- **OPT3 (roll) re-opens WO-18.** It is superficially attractive because
  `dotation.py:88`'s own heading says *"THE GRACE CLOCK KEYS ON UNMET-TURN
  COUNT"* and today's code does not. But it lets the churn dodge through
  (arm C trust unchanged at 85) and reds two assertions in
  `test_churn_now_erodes_after_grace_regardless_of_the_toggle`
  (`assert m.expectation_grace_turn == first_unmet` and
  `assert m.trust.value < trust0`). A conscious re-open, not a free win.
- A sentinel encoding inside the existing int (`≤−2` = "frozen with N elapsed")
  is algebraically identical to OPT3 and fails the same way.
- **`Marshal.last_expectation_seen` is NOT a usable substrate** for the stamp:
  it is written only in `dispatch.build_morning_dispatch` (`dispatch.py:2450`),
  **player-only** and gated on `m.strength > 0`, on a different tick from the
  dotation pass. Reusing it breaks GR5 and couples two orderings.

**Conclusion: the row is right — a stamp is required, and it must be
serialized.** Measured (`p9_misc.py` §3): a frozen clock survives `to_dict`/
`from_dict` (`grace=2, pension=40` before and after), so an unserialized stamp
reproduces the defect exactly on the first save/load inside a frozen era.
This is one of the few rows whose `fix_shape` is correct as written.

### Pins That Flip

**Zero.** Plugin `plug_n46.py` (OPT1) over
`test_wo_slice14_the_clock_and_the_flag.py` (16) + `test_economy_es7_dotation.py`
(57) + `test_estate_second_pass.py` (86) + `test_estate_riders_esp.py` (22) +
`test_ux23a_reward_where_he_stands.py` (73) + `test_ux23b_the_desk_is_quiet.py`
(66) + `test_pf5_notification_dedup.py` + `test_pc15_d_rulings_2026_08_15.py` +
`test_fa26_the_question_is_asked_2026_09_05.py` + `test_serialization_enforcement.py`
+ `test_economy_e1_band.py`:

```
BASELINE   445 passed
N46 OPT1   445 passed
```

The row's "~357 dotation pins" is a fair estimate — the six core dotation files
alone are **320**. All six WO-18 pins survive, including the two the row names.

**One pin you WILL have to write into**: `test_serialization_enforcement.py::
TestMarshalSerialization::test_all_marshal_fields_serialized` walks `__dict__`,
so the new int must go into `Marshal.to_dict()` (**`marshal.py:1638-1640`**) and
`from_dict()` (**:1828-1830`**) beside `expectation_grace_turn` / `pension` /
`last_expectation_seen`, plus a `SAVE_FORMAT_REFERENCE.md` row. My plugin used a
class attribute and therefore did *not* exercise that pin — the real build will.

### Series / Harness Risk

**BASELINE_SERIES: byte-identical, MEASURED, and not vacuously so.**
`p7_series_diff.py`, four arms, `PYTHONHASHSEED=0 SOVEREIGN_SEED=historical
LLM_MODE=mock` (the in-process run diverges at index 3 without the hash pin —
worth knowing).

```
ARM base  == BASELINE_SERIES: True   fires n46_reanchor=0
ARM n46   == BASELINE_SERIES: True   fires n46_reanchor=3
```

**The changed branch DOES fire on the ambient board — 3 times in 40 turns — and
it DOES change state.** Diffing the full trust dict:

```
base : ... 'ArchdukeJohn': 89 ...
n46  : ... 'ArchdukeJohn': 96 ...      (every other marshal identical)
```

So: the fix is live on the harness geometry, it moves an **AI** marshal's trust
by +7, and the series holds because no threat producer reads marshal trust.
Report it that way rather than as "inert".

Reachability census on the same run (`p6_series_reach.py`):
`freeze_events` 17, `unmet_with_open_clock` 233, `erosion_writes` 200.

**M1–M7: structurally inert.** `tests/test_combat_sweep_metrics.py` contains
zero references to `advance_turn`, `end_turn`, `_process_dotation_state`,
`expectation_grace_turn` or `get_field_marshals` — grep returns nothing. 11/11
green at baseline.

### Recommended Build Shape

One new serialized int on `Marshal`, `expectation_covered_at_freeze`, default
`-1`, `.get()`-defaulted like `expectation_grace_turn`, in `to_dict`/`from_dict`.

- **Met branch, `world_state.py:6178-6180`**: when the estate covers (or the
  guard lever is down) → `= -1` beside the existing reset. When the clock is
  open and the rente is load-bearing (the freeze) → `= int(expectation)`.
  *Note for the builder*: at every freeze `pension > 0` is guaranteed by
  construction — `shortfall <= 0` plus `estate < expectation` forces it — so
  the stamp is always "the expectation the rente is closing".
- **Unmet branch, before `elapsed` at `world_state.py:6218`**: if
  `cov >= 0 and expectation > cov` → `expectation_grace_turn = current_turn`
  and `cov = -1`. Once, then the ordinary machinery runs.
- Ride `PENSION_CHURN_GUARD_ACTIVE` as the single lever so the whole thing
  reverts with WO-18.
- Falsifiable pin: arm A above must end with `trust` unchanged on the first
  turn after the win and `grace_turns_left == GRACE_TURNS`; **the negative
  control is arm C** (the churn dodge must still erode) — without it the pin is
  satisfied by OPT2, which is wrong.

---

## FA-N77 — Last Marshal Protection counts prisoners

### VERDICT: **REPRODUCED** (verbatim; one row claim needs a correction, one is WIDER)

### What Reproduces (`p1_n77_n76.py` arms 1–3)

1805 boot, capture every French marshal but Lannes:

```
standing (strength>0):  ['Lannes']
get_field_marshals() -> 8  ['Ney','Davout','Soult','Lannes','Murat','Bernadotte','Massena','Napoleon']
  strengths:   {Ney:0, Davout:0, Soult:0, Lannes:18000, Murat:0, Bernadotte:0, Massena:0, Napoleon:0}
  captured_by: {all 'Austria' except Lannes}
check_redemption_threshold(Lannes @ trust 15) OFFERED:
  ['grant_autonomy', 'administrative_role', 'dismiss']
```

With the filter simulated: `get_field_marshals -> 1`, `OFFERED ->
['grant_autonomy']`. Control (two standing): offer byte-identical to today.

End-to-end through the endpoint (`p1` FA-N76 arm 1): `POST
/respond_to_redemption {"choice":"dismiss"}` → `success True`, *"Lannes has
been relieved of command. 18,000 troops **dispersed** — no nearby commanders"*,
`fallen_marshals {'Lannes': …cause 'dismissed'}`, **French standing after: `[]`**.
France ends the turn with no army and no commander.

### What Is False

1. **Line numbers, all of them.** `world_state.py:3575-3586`/`:3582` → real
   `get_field_marshals` is **3593–3604** (+18). `disobedience.py:1482` → real
   **1572** (+90); `:1500-1503` (the `field_count < 2` early return) → real
   **1593–1595** (+93). `get_marshals_by_nation :3670` → **3676**;
   `find_nearest_marshal_within_range :3634` → **3619** (drift is *negative*
   here — the row's siblings list is internally inconsistent).
   `capture_marshal :4572-4621` → **4604**. `clarification.py:139` → **140**.
2. **"the cheat surface is stricter than the shipping endpoint"** (this is in
   FA-N76's body, about the same protection) is **half false**. The cheat arms
   *are* stricter on the one-admin rule, but their last-marshal guards
   (`meta_executor.py:1521` and `:1575`) read the *same broken*
   `get_field_marshals`, so on prisoners the cheat surface is **equally** wrong.

### What Is WIDER

**Napoleon is in the count.** The 1805 French roster is eight, and the eighth is
the sovereign. He is not `administrative`, so `get_field_marshals` counts him;
he is capturable (my probe captured him). `meta_executor.py:1512` has an
explicit NP-0 never-do pin against dismissing him, and the redemption arc is
protected by his trust freeze — so no live exploit — but any `field_count`
arithmetic that treats him as a *substitutable* field marshal is one
never-do-pin away from a hole.

### The Real Seam

`WorldState.get_field_marshals`, **`backend/models/world_state.py:3593-3604`**.
Six production callers, exactly four unguarded (the row's "four unguarded
callers" is **correct**):

| caller | today | after `strength > 0` |
|---|---|---|
| `clarification.py:140` | already `m.strength > 0` | **no-op** |
| `delegation.py:295` | already gated at `:293` (`strength <= 0 → None`) | **no-op** |
| `context_carryover.py:330` `_field_marshal_names` | unguarded | behaviour change — see below |
| `disobedience.py:1572` | unguarded | **the fix** |
| `meta_executor.py:1521` (cheat dismiss) | unguarded | fix |
| `meta_executor.py:1575` (cheat admin) | unguarded | fix |

### What The Filed Fix Would Break — measured, nothing

The only caller whose *output* changes for a user is `context_carryover`
(`p8_blast.py`). With Ney captured:

```
TODAY        'Ney, do the same' -> {'kind':'rewrite','command':'Ney, move to Bavaria'}
WITH FILTER  'Ney, do the same' -> {'kind':'pass'}
```

Driven end to end through `POST /command` on a real TestClient, **both paths
produce the identical player-visible answer**, because slice 7's prisoner guard
catches it downstream:

> `Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.`

So the change shortens the path and removes a second copy of a rule, and is not
user-visible. **Residue worth noting, not caused by the fix**: the sibling arm
`'Ney, same target'` still rewrites (`{'kind':'rewrite','command':'Ney,
Bavaria'}`) — it goes through `_last_target`, not `_match_roster_name`, so
FA-N77 does not close it. Harmless for the same downstream reason.

### Pins That Flip

**Zero.** `plug_n77.py` over 17 files:

```
redemption family (9 files)   BASELINE 303 passed   N77 303 passed
carryover/clarification/delegation/fates/prisoners family (8 files)
                              BASELINE 514 passed   N77 514 passed
```

Including `test_administrative_role.py:260` / `:282` / `:348` / `:357-358`,
which all assert exact `get_field_marshals()` counts — they survive because
their fixtures `del world.marshals[...]` rather than capturing, **which is
precisely why the defect shipped**. `test_last_marshal_only_autonomy_available`
(`:249`) deletes three marshals from the dict; it has never seen a prisoner.

### Series / Harness Risk

**None, and measured.** On the ambient 40-turn board `get_field_marshals` is
called **exactly once** in 40 turns (from the single `redemption_event`), and
`gfm_returned_prisoner = 0` — at that moment no French marshal was captured.
`p7_series_diff.py` arm `n77`: series byte-identical, `n77_changed = 0`.
M1–M7 never reaches the symbol (structural).

### Recommended Build Shape

```python
and getattr(marshal, "strength", 0) > 0
and not getattr(marshal, "captured_by", "")
```

Both clauses. `strength > 0` alone is sufficient today (capture zeroes strength)
but the explicit `captured_by` states the intent and survives a future
non-zeroing capture. All four unguarded callers inherit it; the two guarded ones
are provably unaffected.

Pin as the row says, plus a **negative control**: with two standing marshals the
offered list must be byte-identical to today's three arms, so the fix cannot be
satisfied by breaking the builder. And a **sibling-drift pin**: assert
`get_field_marshals` returns a subset of `get_marshals_by_nation(player_nation)`
for any world — that is what stops the four helpers diverging again.

---

## FA-N76 — the choice is validated against a hardcoded list

### VERDICT: **REPRODUCED and WIDER** — and **the filed fix shape ships a P1**

### What Reproduces (`p2_n76_tight.py`)

The row's headline is the last-marshal case; the *bigger* live prize is the
one-admin rule. Three redemptions in a row on the 1805 boot, all through the
real endpoint:

```
max_actions at boot: 4, bonus_actions 0
Ney    OFFERED ['grant_autonomy','administrative_role','dismiss']
       POST administrative_role -> True | admins ['Ney']                 | actions 5
Davout OFFERED ['grant_autonomy','dismiss']        <-- admin NOT offered
       POST administrative_role -> True | admins ['Ney','Davout']        | actions 6
Soult  OFFERED ['grant_autonomy','dismiss']        <-- admin NOT offered
       POST administrative_role -> True | admins ['Ney','Davout','Soult']| actions 7
```

**The player farms +1 action per marshal, in an unbounded loop, by sending a
choice the audience did not offer.** `world.bonus_actions` 0 → 3,
`calculate_max_actions()` 4 → 7. That is an economy exploit, not a presentation
defect, and it is not in the row's title.

Everything the row states about the seam is otherwise correct: `main.py`'s
`valid_choices` is a static three-word list; `redemption_event['options']` is
never consulted before the handler is called; `handle_redemption_response`
dispatches on `choice` alone; the two debug cheat arms enforce both rules.

**The plumbing the fix depends on is sound** (`p1`, `p9_misc.py` §1): the option
list survives into `world.pending_redemption` and round-trips
`to_dict`/`from_dict` byte-identically. The Godot client already renders
dynamically from `options` (`redemption_dialog.gd:61-67`), so the client is
honest and only the wire is not.

### What Is WIDER — two extra findings

1. **`handle_redemption_response` clears the latch and stamps the cooldown
   BEFORE it dispatches** (`disobedience.py:1765` and `:1767`, inside the
   function, above every branch). `p1` arm 3: calling it with `choice="banana"`
   returns `success False` **and leaves** `redemption_pending False`,
   `redemption_cooldown_until 6`. Unreachable from HTTP today (main.py's static
   list catches it first) and there is no second production caller — but it is
   why the guard must sit above line 1765 if it sits in the handler at all.
2. **The playtest driver's default redemption policy is literally `"dismiss"`**
   (`tools/playtest_driver.py:153`, posted at `:1066`). So an unattended run
   answers every audience with the one option the rules are supposed to
   withhold. FA-N77 alone does not stop it — that is FA-N76's job.

### What Is False

- **Line numbers.** `main.py:3574-3596` / `:3581` → the endpoint is **4017-4048**
  and `valid_choices` is at **4045**. **Drift +464** — the worst in this batch,
  and the `owner` cell `backend/main.py:3581` currently points at unrelated code.
  `disobedience.py:1624` → `handle_redemption_response` is **1723** (+99);
  `:1481-1526` (the option builder) → **1551-1622** (+70).
  `meta_executor.py:1502-1506` → **1520-1524**; `:1556-1568` → **1574-1585** (+18).
- **The stated justification for the siting is false.** *"Siting it there rather
  than at main.py:3581 makes the endpoint, the playtest driver … [inherit it]"*
  — the driver posts to `/respond_to_redemption` over TestClient, so there is
  only ONE route and `handle_redemption_response` has exactly one production
  caller. The handler siting has a real merit (it is above the mutation), but
  not the one the row gives.

### What The Filed Fix Would Break — **measured, twice**

**(a) The literal fix shape reds 5 landed pins.** `plug_n76_literal.py`
implements the row verbatim — *reject any choice not in
`{o['id'] for o in redemption_event.get('options', [])}`*:

```
BASELINE      303 passed
N76 LITERAL     5 failed, 298 passed
  test_administrative_role.py::TestDemandObedienceRemoved::test_demand_obedience_returns_invalid
  test_autonomy.py::TestGrantAutonomy::test_grant_autonomy_sets_all_fields
  test_autonomy.py::TestGrantAutonomy::test_grant_autonomy_clears_redemption_pending
  test_redemption_v2b.py::TestRedemptionCooldown::test_cooldown_set_on_resolution
  test_redemption_v2b.py::TestRedemptionCooldown::test_cooldown_expires_allows_refire
```

Four of those build a hand-made event `{"marshal": "Ney", "type":
"redemption_event"}` with **no `options` key at all**; the empty set makes
`choice not in offered` unconditionally true, so the guard **refuses every
legitimate resolution**. Adding the `if offered and …` carve-out drops it to
**1 failed, 302 passed**, and the survivor is a message pin
(`test_administrative_role.py:474` asserts `'Invalid choice' in message`) which
is a deliberate copy improvement.

**(b) The P1: the filed siting leaves the marshal permanently silenced.**
`p3_filed_fix_regression.py` applies the row's own shape (guard at the top of
`handle_redemption_response`, above the latch clear, "leaving the question
standing (do not clear the latch, do not set the cooldown)") and measures what
actually happens:

```
Davout OFFERED ['grant_autonomy','dismiss']
POST administrative_role -> success False   <- THE RULE IS NOW ENFORCED (admins still ['Ney'])
>>> world.pending_redemption after the refusal = None
>>> Davout.redemption_pending = True
>>> standing_redemption(world) = None
>>> can Davout ask again NOW?          -> None
>>> after 10 turns (turn 11), ask again? -> None    (trust still 15)
```

Cause: **`main.py:4058` sets `world.pending_redemption = None`
unconditionally**, after the call, regardless of `result['success']`. The
handler-sited guard returns before clearing `marshal.redemption_pending`, so the
marshal keeps the latch while the world loses the question. `standing_redemption`
(`disobedience.py:663-694`) only releases a latch when it finds a *stored* event
— with `pending_redemption` already `None` it returns at the `isinstance` check
and never reaches the release at `:693`. `check_redemption_threshold` then
refuses forever at `:1688`. The only escape is `Marshal.modify_trust` lifting
him above 20 (`marshal.py:1464`), which an eroding marshal at 15 will not do.

**Building FA-N76 as filed shuts the trust-collapse channel for that marshal for
the rest of the campaign** — the identical class of defect the slice-9 review
round found in `clear_stale`, one slice ago.

The corrected shape is measured working in the same probe: with the clear made
conditional on `result['success']`, the refusal leaves `['grant_autonomy',
'dismiss']` standing and the follow-up `grant_autonomy` succeeds.

**There is a simpler correct siting the row missed.** `main.py`'s own refusal at
`:4046-4048` is an **early return, before `:4058`** — and `_refusal_response`
(`main.py:472-481`) does not touch `pending_redemption`. So replacing the static
list at `:4045` with the offered set is safe *by construction* and needs no
conditional clear.

### Pins That Flip

With the corrected shape: **exactly one**,
`tests/test_administrative_role.py::TestDemandObedienceRemoved::
test_demand_obedience_returns_invalid` (`:471-474`), a copy assertion
(`'Invalid choice' in result['message']`). A one-line, deliberate flip — record
it. Everything else in the nine-file redemption family (303) stays green, and
FA-N46/FA-N77 do not interact with it.

### Series / Harness Risk

**None.** `check_redemption_threshold` fires 298 times in the ambient 40 turns
and produces **1** event, which is never answered (nothing in the harness posts
to the endpoint). `options_would_change = 0`. M1–M7 never reaches
`respond_to_redemption`. `BASELINE_SERIES` unaffected.

### Recommended Build Shape

Three parts, all small:

1. **ONE shared predicate** in `disobedience.py` beside `standing_redemption` —
   `redemption_choice_is_offered(event, choice) -> bool`, returning `True` when
   the event carries no options list (so hand-built events and legacy saves
   still resolve; this is what keeps the four `test_autonomy` /
   `test_redemption_v2b` pins green).
2. **Call it at `main.py:4045`**, replacing `valid_choices` — the early return
   at `:4046-4048` leaves the question standing by construction, and the refusal
   names what *was* offered.
3. **Call it again at the top of `handle_redemption_response`, above
   `disobedience.py:1765`** (`marshal.redemption_pending = False`) — defence in
   depth for any future caller, and it also closes the latent
   invalid-choice-destroys-the-latch path from finding (1).
   **Do NOT rely on the handler alone**; if you site it only there, you must
   also make `main.py:4058` conditional on `result.get("success")`, or you ship
   the P1 above.

Falsifiable tests, on top of the row's two:
- **the exploit arm** — three consecutive `administrative_role` answers where
  only the first is offered must leave `bonus_actions == 1` and one admin;
- **the survival arm** — after a refusal, `standing_redemption(world)` still
  returns the event and a legal answer still resolves (this is the pin that
  would have caught the P1);
- **the driver arm** — the `"dismiss"` default policy against a one-standing-
  marshal board must be refused, since that is the live unattended path.

### Build order note

**FA-N77 before FA-N76.** N77 makes the *offer* correct; N76 makes the offer
*binding*. Landing N76 first would enforce a rule that is still computed from a
prisoner-inflated count, i.e. it would faithfully enforce the wrong answer. They
share `test_administrative_role.py` and neither touches the other's seam, so one
slice with N77's edit first is clean. FA-N46 is independent of both.