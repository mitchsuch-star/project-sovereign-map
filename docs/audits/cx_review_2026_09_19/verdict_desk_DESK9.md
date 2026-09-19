# VERDICT:DESK-9 — CONFIRMED, and corrected on four points

**Row CX review · refuter pass · tree `f52df77f` (row head `727cf88a`), clean**
**Default verdict on entry: REFUTED. It survived.**

---

## 0. The short answer

| question | filed | measured |
|---|---|---|
| reproduces? | at hand-set `actions_remaining = 0` | **yes — and on the ORDINARY road, after two legal orders on turn 1** |
| severity | P3 | **P3 — correct** |
| player-reachable? | yes | **yes, by THREE roads, two of which need no question at all** |
| shipped by row CX? | yes | **two of three arms are NEW; the third is PRE-EXISTING and row CX made it worse** |
| fix shape | "drop the AP-priced lines at 0 AP (the free verbs … remain)" | **would ship a regression; its parenthetical is measurably false — ZERO counsel verbs are free** |
| blamed seam | `counsel._is_free_to_order` | **mis-sited — that is a per-MARSHAL predicate; AP is a per-NATION pool** |

---

## 1. Reproduction — mine, not the one I was given

All probes drive the **real `POST /command` endpoint** against the shipped
1805 board (`parser_eval.build_world("1805")`, seed `historical`,
`LLM_MODE=mock`). Probes live in
`…/scratchpad/cx_review/probes/refute_desk9/`.

### 1a. The ordinary road — nothing is hand-set (`p2_natural.py`)

The lens set the counter by hand. I played the board instead. On the shipped
1805 boot France has **4 military AP / 2 admin AP**, and `fortify` costs **2**
because the executor auto-shifts the stance first. So **two ordinary orders on
turn 1** empty the military pool:

```
boot AP: (4, 2)
   ('Ney, fortify',    True, (4,2) -> (2,2), 'Ney grumbles about defensive orders but complies.
                                              [Auto-shifted to DEFENSIVE stance first — cost 2 AP]')
   ('Davout, fortify', True, (2,2) -> (0,2), '[Auto-shifted to DEFENSIVE stance first — cost 2 AP]
                                              Davout fortifies position')
military AP = 0   admin AP = 2
```

Now the question, over `/command`:

```
> what can I do
These orders would be carried out today, Sire:
  Ney, attack Mack
  Ney, march to Lorraine
  Ney, unfortify
  Soult, fortify
  build supply depot in Rhineland — 300g
  build fortification in Rhineland — 400g
For any matter of state, press F1 for the Cabinet.

> Ney, attack Mack
success = False   Not enough actions! Need 1, have 0.
```

### 1b. Every offered line, tried on an identical board (`p9_ordinary_state.py`)

At the state 1a reaches by playing — **military 0 / admin 2** — each of the six
lines was sent to `/command` on its own fresh copy of that board:

```
REFUSED     | Ney, attack Mack                      Not enough actions! Need 1, have 0.
REFUSED     | Ney, march to Lorraine                Not enough actions! Need 2, have 0.
REFUSED     | Ney, fortify                          Not enough actions! Need 1, have 0.
REFUSED     | Ney, drill                            Not enough actions! Need 1, have 0.
CARRIED OUT | build supply depot in Rhineland — 300g   (gold 800 -> 500)
CARRIED OUT | build fortification in Rhineland — 400g  (gold 800 -> 400)

>> 4 of 6 lines the game says "would be carried out today" are REFUSED.
>> `end turn` (0 AP, the one thing that DOES work): success = True
   — named in the answer? False
```

Two corrections to the filed reproduction fall out of this:

* **The military and admin pools are separate.** The lens zeroed both, which is
  the convenient case. The *ordinary* case is military 0 / admin 2, and there
  the list is **half true** — four lines refused, two carried — under one
  sentence that makes no distinction. A player cannot tell which is which.
* **`Ney, march to Lorraine` costs 2 AP, not 1**, so the counsel is wrong at
  **1** AP too, a state every turn passes through
  (`p10_one_ap.py`: at military AP 1, `Ney, march to Lorraine` →
  *"Not enough actions! Need 2, have 1."*).

### 1c. The filed case reproduces verbatim (`p1_repro.py` part D)

```
AP = (0, 0)
These orders would be carried out today, Sire:
  Ney, attack Mack …
> Ney, attack Mack   ->   success = False   "Not enough actions! Need 1, have 0."
```

The AP gate fires **before** the objection battery, so the refusal is reliable
and free — nothing is spent, nothing is corrupted.

**Verdict on reproduction: CONFIRMED, and stronger than filed.**

---

## 2. Player-reachable — yes, by three roads

I checked `main.gd` as instructed. `what can I do` is **not** redirected:
`_redirect_diplomatic_command` calls `_is_advisory_question` (`main.gd:2055`)
before any family match, and `"what"` is the first entry of
`DIPLO_ADVISORY_STARTS` (`main.gd:1997-2005`), so the sentence falls open to
`api_client.send_command` at `main.gd:1699`.

But the question is not the main road. The same list is served by **three**
consumers of `counsel.what_can_i_do`, and two of them need no question at all
(`p6_postrow_shrug.py`, all at 0/0 AP):

| consumer | trigger | the promise it makes |
|---|---|---|
| `question_desk._answer_options` (`:817`) | typing `what can I do` | *"These orders **would be carried out today**, Sire:"* |
| `meta_executor._route_unanswered_question` (`:693`) | **any** question the desk cannot take (`what is the weather`, `how many horses do we have`) | *"What I **CAN do today**:"* |
| `llm_client` shrug (`:1389`) | **any** unparseable sentence (`xyzzy foobar`) | *"A clear order might be: 'Ney, attack Mack' or 'Ney, march to Lorraine'."* |

Measured at 0/0 AP, **none of the three mentions `end turn`** — the only thing
the player can legally do.

That is the sharp edge of the finding and the lens under-states it: these are
the surfaces a player reads **at the moment they are stuck**, and the row's own
through-line is that the game must not offer a sentence it cannot honour.

**Mitigation, recorded honestly:** the client HUD shows the true figure —
`main.gd:4205-4212` renders `actions_value` as `0/4` in **red** at ≤1 AP and
`admin_value` greyed at 0. The player has the number on screen. That is why
this is P3 and not P2.

**Verdict on reachability: CONFIRMED and widened.**

---

## 3. Shipped by row CX? — PARTLY. One arm is pre-existing, and the row made it worse.

I ran the same probes against the pre-row tree (`b4a27a15^` == `f7008582`;
verified byte-identical to the blob for `question_desk.py`, `llm_client.py`,
`main.py` after LF normalisation — `p5_prerow.py`, which asserts
`backend.ai.counsel` does not import).

**PRE-ROW, at 0/0 AP:**

```
> what can I do
  -> the 12,717-character COMMAND REFERENCE.
     contains "would be carried out": False
     contains "What I CAN do today":  False

> flurble the wumpus
  Berthier: "…A clear order might be: 'Ney, attack Mack' or 'end turn'. …"
```

So:

* **The desk arm is NEW.** Pre-row, `what can I do` got the manual, which
  proposes nothing and promises nothing. `_answer_options` does not exist in the
  353-line pre-row `question_desk.py`. ✔ shipped by row CX.
* **The router arm is NEW.** `_route_unanswered_question` is a CX-2 addition.
  ✔ shipped by row CX.
* **The shrug arm's AP-blindness is PRE-EXISTING.** The pre-row third template
  already named `Ney, attack Mack` at 0 AP. ✘ not shipped by row CX.

**But — and this is the part nobody filed — row CX regressed the shrug.**
Pre-row the second slot was the literal string `end turn`
(`llm_client` pre-row template 3). Row CX replaced it with `counsel[1]`
(`llm_client.py:1392`, `_second = (_counsel[1] if len(_counsel) > 1 else "end turn")`).
Measured, same template, same 0/0 AP board:

```
PRE-ROW :  "A clear order might be: 'Ney, attack Mack' or 'end turn'."     <- 1 of 2 works
POST-ROW:  "A clear order might be: 'Ney, attack Mack' or 'Ney, march to Lorraine'."   <- 0 of 2 work
```

The one free suggestion the recovery text had at 0 AP was **displaced by the
counsel**. That is a regression this row shipped, inside DESK-9's own subject,
and it is the reason I am not downgrading the row to PRE-EXISTING.

**Verdict on attribution: NARROWED — 2 of 3 arms new, 1 pre-existing but
made worse. The finding's flat "shipped by this row: true" is wrong as
written and right in effect.**

---

## 4. Severity — P3 is right

* **Not P2.** The refusal is honest, free, non-destructive and immediate
  (*"Not enough actions! Need 1, have 0."*); no gold, no AP, no state moves
  (measured: `gold 800 -> 800`, `AP (0,2) -> (0,2)`). The true figure is on the
  HUD in red at the same moment.
* **Not P4.** The copy makes an explicit, falsifiable promise — *"would be
  carried out today"* / *"What I CAN do today"* — on the game's own recovery
  surface; it reaches the player by three roads; it reproduces after two
  ordinary turn-1 orders; and at the state where it fires, the answer it gives
  is 100% wrong for the military pool and silent about the one legal move.

---

## 5. The filed fix would ship a regression, and its parenthetical is false

Filed: *"drop the AP-priced lines at 0 AP (the free verbs and the Cabinet line
remain), or soften the sentence to name the cost."*

### 5a. "the free verbs remain" is measurably false (`p7_fix_regression.py` A)

Read out of the executor's own `world_state._action_costs`:

```
attack 1 · move 1 · fortify 1 · unfortify 1 · drill 1 · recruit 1 · build 1
end_turn 0   <- the only free one, and the counsel never emits it

verbs the counsel emits: 7
of those, FREE: NONE
>> "the free verbs remain" leaves 0 lines.
```

Dropping AP-priced lines at 0 AP **empties the counsel outright**.

### 5b. What an empty counsel does to each consumer (`p8_fix_regression2.py`)

Simulated by patching `counsel.what_can_i_do` to return `[]` — **not** by
flipping `COUNSEL_IS_DERIVED_FROM_THE_BOARD`, which is the wrong simulation
because the lever guard short-circuits `_route_unanswered_question` to `None`
one frame earlier than the real fix would (p7 part B shows the lever version
falling all the way back to the manual; that is an artefact of the lever,
and I am recording it so nobody repeats it):

```
1. the DESK      -> "Nothing can be ordered this turn, Sire. For any matter of state, press F1…"
2. the ROUTER    -> "I cannot answer that from the dispatches, Sire."
                    + Cabinet line + "Type 'help'…"      (173 chars, body GONE)
3. the SHRUG     -> "…await clear commands — 'Ney, attack Mack', perhaps?"
                    "…A clear order might be: 'Ney, attack Mack' or 'end turn'."
```

Three regressions, each nameable:

1. **The shrug falls back to the hardcoded string CX-2 exists to kill.**
   `llm_client.py:1390` — `_offer = (_counsel[0] if _counsel else
   f"{first_marshal}, attack {first_enemy}")`. At 0 AP that resolves to
   **`Ney, attack Mack`**, the identical refused order, now proposed by the
   hardcoded copy instead of the board. **The fix does not fix the shrug at
   all** — it only changes which line of code tells the lie.
   (Pinned today by `test_the_counsel_lever_restores_the_hardcoded_shrug`,
   `tests/test_cx2_berthier_answers_the_board.py:326`.)
2. **The router loses its whole body.** *"What I CAN do today"* is the second
   of the three parts and, per the function's own docstring
   (`meta_executor.py:669`), *"the second is the one that matters"*. At 0 AP a
   stuck player would get the pre-CX shrug with extra steps.
3. **The desk's replacement sentence is a NEW lie in the other direction.**
   *"Nothing can be ordered this turn, Sire."* is false: `end turn` is 0-cost
   and succeeds (measured), and at the ordinary military-0/admin-2 state
   **both build lines succeed** (measured, §1b).

### 5c. Which pin would it red? **None — and that is the finding underneath the finding.**

Both CX-2 fixtures build a *fresh* 1805 board
(`tests/test_cx2_berthier_answers_the_board.py:83-88` and `:90-105`), i.e.
4 military AP / 2 admin AP. An AP gate never fires in any of them, so the fix
is invisible to all 23,618 tests — including
`test_the_router_offers_orders_that_would_be_carried_out` (`:285`), a pin whose
**name asserts the exact claim its board can never exercise**. Same for the
twelve-question table's `("should I attack", ("cannot answer", "What I CAN do"))`
row (`:134`).

This is the row's own recorded lesson repeating: the pins were built on the
convenient board.

### 5d. The fix that does not regress

* Price each line against the pool it draws on — the two pools are separate,
  so the admin lines survive a dry military pool (measured: 2 of 6 carried).
* Where a line is unaffordable, either drop it **or** state its cost; the
  second half of the filed shape (*"soften the sentence to name the cost"*) is
  the sound half.
* **Always append `end turn`** when the military pool is empty, which keeps the
  counsel non-empty for all three consumers and stops the shrug ever reaching
  the hardcoded fallback. It also restores what row CX took out of the shrug's
  second slot.
* Do it at `what_can_i_do` / the per-line emit — **not** at
  `_is_free_to_order`.

---

## 6. The blamed seam is mis-sited

The finding says *"`counsel._is_free_to_order` checks strength, captured_by,
is_drilling and administrative, and never reads action points."* The first
clause is true (`counsel.py:62-73`), the conclusion is the wrong site:
`_is_free_to_order` is a per-**marshal** predicate and AP is a per-**nation**
pool. An AP test there returns `False` for every marshal at once and empties
`marshals` at `counsel.py:108` before any of the four emit loops run — which is
§5b's empty-list regression arrived at by a worse road, and it would also
make the function's own name a lie.

---

## 7. Neighbourhood — NOT part of DESK-9, recorded for whoever builds it

The same function skips gates that are not AP at all. `military_counsel` step 2
(the march) asks `MovementExecutor.move_refusal_probe`; **steps 3 and 4
(fortify / unfortify / drill) ask nothing.** Measured on the shipped boot:

```
military AP 1:  Ney, drill    -> "Ney cannot drill with enemy forces nearby!
                                  Mack is at Swabia, just one region away."   (p10_one_ap.py)
mid-turn board: Ney, fortify  -> "Ney cannot fortify while engaged with enemy
                                  forces! Enemy present: Mack."               (p4_snapshot.py)
```

Same shape as DESK-9 — *the answer is asked of the seam that describes the
board, not the seam that would refuse the order* — different gate. On the
shipped 1805 boot Ney stands one province from Mack at turn 1, so this one
fires on the **first** counsel a player ever sees.

---

## 8. Probes

| file | what it establishes |
|---|---|
| `p1_repro.py` | boot AP 4/2; the filed hand-set case reproduces over `/command` |
| `p2_natural.py` | **two ordinary fortify orders reach military AP 0 on turn 1** |
| `p3_which_lines_lie.py` | the `_action_costs` table; first (non-deterministic) per-line pass |
| `p4_snapshot.py` | per-line verdicts off one snapshotted mid-turn board; finds the 2-AP march and the engagement gate |
| `p5_prerow.py` | pre-row tree (`counsel.py` absent): the manual, and the shrug's `'… or end turn'` |
| `p6_postrow_shrug.py` | post-row shrug/router at 0/0 AP; `end turn` free and unnamed |
| `p7_fix_regression.py` | no counsel verb is free; the lever is the wrong simulation |
| `p8_fix_regression2.py` | the honest empty-counsel simulation across all three consumers |
| `p9_ordinary_state.py` | **4 of 6 refused at military 0 / admin 2** |
| `p10_one_ap.py` | wrong at 1 AP too (`Need 2, have 1`) |

Read-only throughout: no repo file was written, no git command mutated.
