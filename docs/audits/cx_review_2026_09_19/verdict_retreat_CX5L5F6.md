# VERDICT — CX5-L5-F6

**CONFIRMED at P4, shipped by row CX, not player-reachable — with four
corrections to the row, one of which means the suggested fix must not be
built as written.**

Tree `master 727cf88a`, clean, nothing under the repo modified. Everything
below measured on the shipped 1805 board (`parser_eval.build_world("1805")`)
driven at `POST /command` through `TestClient`, `LLM_MODE=mock`,
`SOVEREIGN_SEED=historical`, one fresh board per utterance. Attribution is
always by flipping `llm_client.A_RETREAT_CAN_BE_A_NOUN` and re-driving the
same sentence, never by reading the diff.

Probes (mine, not the finder's):
`probes/p1_inert_rows.py`, `p2_seedsweep.py`, `p3_widen_cx1.py`,
`p4_consequence.py`, `p5_falsegreen_causes.py`, `p6_corpus_blind.py`.
All import `_drive` / `_assert_inert` **from the shipped test file** so the
fidelity to what pytest actually asserts is exact.

---

## 1. BOTH HALVES REPRODUCE, DIGIT FOR DIGIT

### (a) 3 of the 10 pinned rows pass with CX-5 deleted

`TestTheRetreatIsSometimesANoun.SOMEBODY_ELSES`, 6 reps each, lever both ways:

```
utterance                                      lever ON     lever OFF (fix deleted)
Lannes, cut down the retreat                   6/6 inert    0/6 inert   binds
Lannes, cut off the retreat                    6/6 inert    0/6 inert   binds
Lannes, press the retreat                      6/6 inert    0/6 inert   binds
Lannes, block the retreat                      6/6 inert    0/6 inert   binds
Lannes, exploit the retreat                    6/6 inert    0/6 inert   binds
Lannes, punish the retreat                     6/6 inert    0/6 inert   binds
Lannes, ride down the retreating Austrians     6/6 inert    0/6 inert   binds
Lannes, harry the retreat                      6/6 inert    6/6 inert   INERT PIN
Lannes, cover the retreat                      6/6 inert    6/6 inert   INERT PIN
Lannes, screen the withdrawal                  6/6 inert    6/6 inert   INERT PIN
```

and the stated causes are the actual causes — the lever-OFF messages are:

```
harry the retreat      -> "Cannot find 'Retreat' to pursue."          (PURSUE branch)
cover the retreat      -> Berthier's shrug                            (_mentions_screening_idiom, July 18 2026)
screen the withdrawal  -> Berthier's shrug                            (_mentions_screening_idiom, July 18 2026)
the other seven        -> "Lannes … retreats from Franche-Comte to Lorraine … -45% effectiveness"
```

These three also escape CX-5's *other* two sweep mutations: under CX5-4
(screening idiom removed) `_retreat_is_a_noun("cover the retreat")` and
`("screen the withdrawal")` both still return True, so those rows stay green
there too. They are inert with respect to **every** CX-5 mutation.

They are not worthless tests — they pin the pre-existing guards — but the
class groups them under CX-5 and `BUG_FIXES`/the memo present all ten as
fixed by this row. The attribution is what is wrong, not the assertions.

### (b) `_assert_inert` passes with a live retreat order behind a modal

Sixty `random.seed(N)` values, lever OFF, every act-on row:

```
Lannes, press the retreat                   FALSE GREEN on 6/60 seeds -> [31, 32, 43, 49, 55, 57]
Lannes, block the retreat                   FALSE GREEN on 6/60 seeds -> [31, 32, 43, 49, 55, 57]
Lannes, exploit the retreat                 FALSE GREEN on 6/60 seeds -> [31, 32, 43, 49, 55, 57]
Lannes, cut down the retreat                FALSE GREEN on 6/60 seeds -> [31, 32, 43, 49, 55, 57]
Lannes, cut off the retreat                 FALSE GREEN on 6/60 seeds -> [31, 32, 43, 49, 55, 57]
Lannes, punish the retreat                  FALSE GREEN on 6/60 seeds -> [31, 32, 43, 49, 55, 57]
Lannes, ride down the retreating Austrians  FALSE GREEN on 6/60 seeds -> [31, 32, 43, 49, 55, 57]
```

At `random.seed(31)`, `Lannes, press the retreat`, fix reverted, `_assert_inert`
**PASSES**:

```
footprint : {"ap": [4,4], "admin": [2,2], "gold": [800,800], "turn": [1,1],
             "moved": [], "battle": false}
message   : Lannes respectfully raises concerns: 'Retreat? We can still fight!'
pending_objection : True
non-empty response keys include: objection, concern_level, severity, choices,
             awaiting_response, suggested_alternative, compromise, tone
```

The finder's diagnosis of the mechanism is right: for this family `moved` is
the only live discriminator. AP is 0 either way (retreat is free), no gold, no
turn, no battle, no admin. All six false greens are the same cause — a
MODERATE objection, verified individually (`p5`).

### (c) the supporting claim about the corpus holds

`parser_eval.run_corpus()` under both arms: `passed=688 failed=0` and
`passed=688 failed=0`. The golden corpus is blind to the whole slice.

---

## 2. FOUR CORRECTIONS TO THE ROW

### C1 — the title UNDERSTATES its own second clause: it is seven rows, not three

"3 more can go green by luck" is what the finder happened to observe
(press / block / exploit). The measured property belongs to **all seven**
binding rows, on the identical seed set. Worse than filed, not better.

### C2 — the sweep's 35/35 KILLED is sound; the consequence is bounded

The row's sentence *"the file reports KILLED while three rows assert nothing
about the fix"* is literally true and I confirm it. But the framing invites
the reading that CX-5's protection has a hole, and measured, it does not.

Run the way pytest actually runs the class — **one continuous RNG stream for
the whole class**, not a reseed per row — with the lever OFF (= sweep row
CX5-1), eight independent runs:

```
run 0: 6 red / 4 green   RED (mutant killed)    luck-green: press
run 1: 5 red / 5 green   RED (mutant killed)    luck-green: cut off, exploit
run 2: 7 red / 3 green   RED (mutant killed)
run 3: 6 red / 4 green   RED (mutant killed)    luck-green: punish
run 4: 7 red / 3 green   RED (mutant killed)
run 5: 7 red / 3 green   RED (mutant killed)
run 6: 5 red / 5 green   RED (mutant killed)    luck-green: press, punish
run 7: 7 red / 3 green   RED (mutant killed)
-> mutant killed in 8/8 runs
```

Seven rows at ~10% each; all seven missing together is ~1e-7. This is a
**pin-attribution and per-row-bindingness** defect, not an undetected
regression path. P4 is right and nothing higher is defensible.

### C3 — the stated cause of the flakiness is wrong: there is no randomised ordering here

The row attributes the run-to-run variation to *"pytest's randomised
ordering"*. **`pytest-randomly` is not installed in this checkout** —
`import pytest_randomly` → `ModuleNotFoundError` — and `pyproject.toml`
configures no randomisation plugin.

The variation is real; its cause is that **nothing seeds the module RNG for
the suite.** `tests/conftest.py::_isolate_sovereign_seed` pins
`SOVEREIGN_SEED` (the *campaign* seed, AI-0b), and nothing pins `random`, so
CPython seeds it from OS entropy once per interpreter and the objection roll
differs per pytest *run*.

This matters for the fix: the durable answer is not "make the pins
order-independent" or "pin the RNG". It is that a driven pin standing over a
probabilistic objection must assert something the objection cannot satisfy.

### C4 — ⛔ THE SUGGESTED FIX WOULD SHIP A RED PIN AS WRITTEN

The row prescribes *"assert on the message and on `pending_objection` too"*.
Measured at HEAD across all ten rows:

| candidate | catches the 6 false greens | safe at HEAD |
|---|---|---|
| `assert not response.get("pending_objection")` | **6 / 6** | **yes** (0/4 for all ten) |
| `assert "retreats from" not in message` | 0 / 6 | yes — but redundant with `moved` |
| `assert "retreat" not in message.lower()` | 0 / 6 | **NO — REDS `Lannes, harry the retreat`** |

`harry the retreat`'s HEAD refusal is literally `Cannot find 'Retreat' to
pursue.` The obvious spelling of the message half reds it — and that is one
of the very three rows the finding wants split out of the class. The
objection line (`Lannes respectfully raises concerns: 'Retreat? We can still
fight!'`) contains no retreat-execution vocabulary at all, so **no message
assertion catches the measured hole**.

**Build only the `pending_objection` assertion.** It closes 6/6 and is safe.
The message half is either useless or a regression depending on how it is
spelled, and should be dropped from the prescription.

---

## 3. THE WIDENING THE ROW DID NOT ASK FOR (new, worth recording)

`_assert_inert` is the whole file's helper, not CX-5's. I checked whether the
same hazard holes CX-1's own headline pins. **It does — by a different
mechanism**, and one of them is the row's named headline pin.

With `clause_guards.A_QUESTION_NEVER_ORDERS = False` (the pre-CX-1 defect),
40 seeds each:

```
why not attack Mack     40/40 FALSE GREEN   <- THE HEADLINE
why not retreat         40/40 FALSE GREEN
why not fortify         40/40 FALSE GREEN
what about attack Mack  40/40 FALSE GREEN
how about attack Mack   40/40 FALSE GREEN
attack?                 40/40 FALSE GREEN
can Ney attack Mack      0/40               binds
retreat?                 0/40               binds
```

Not the objection: the board genuinely does not move, because row CX's own
**sibling arm** catches it —

```
why not attack Mack, A_QUESTION_NEVER_ORDERS = False
  -> "There is no 'why not' in the order of battle, Sire. Whom did you intend?"
     (CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA reads "why not" as an unbound addressee)
```

So `test_why_not_attack_mack_fought_a_battle_before_this_slice` — the pin
written *"as its own pin so the reach is not lost in a parametrize list"* —
passes with `A_QUESTION_NEVER_ORDERS` reverted. `can Ney attack Mack` and
`retreat?` still bind, so sweep rows CX1-2 and CX1-5 are still legitimately
killed by the class; but the headline pin is held by the wrong arm of the
same commit, which is the same defect one slice over.

Consequence for the fix: whatever is done for the retreat class should be
done **file-wide**, and the two-arm interaction says the CX-1 pins want the
same treatment the row prescribes here — assert the *refusal the arm
produces*, not merely that nothing moved.

---

## 4. ATTRIBUTION AND REACHABILITY

* **shipped by row CX: TRUE.** `grep -rln "_assert_inert" tests/` returns
  only `tests/test_cx1_a_question_never_orders.py`;
  `git log -S "_assert_inert" -- tests/` returns exactly `b4a27a15` (CX-1,
  wrote it) and `c73749c3` (CX-5, touched it). The retreat class is CX-5's.
  No pre-existing instance of this helper exists elsewhere in the suite.
* **player-reachable: FALSE.** Nothing in the shipped game behaves
  differently. All ten utterances are inert at HEAD in 6/6 reps each and none
  raises an objection (0/4 each). This is entirely a test-quality defect; no
  `main.gd` redirect question arises.
* **severity P4: CONFIRMED**, per C2.

---

## 5. RECOMMENDED WORK (corrected)

1. Add `assert not response.get("pending_objection")` to `_assert_inert`
   (file-wide — it is safe for every current caller I measured).
   **Do not add a message assertion**; see C4.
2. Split `harry the retreat` / `cover the retreat` / `screen the withdrawal`
   into their own class named for the guards that actually hold them, so the
   CX-5 class is only what CX-5 causes, and correct the "10 of 10" wording in
   `BUG_FIXES` / the memo.
3. Record C3 on the row: the cause is an unseeded module RNG, not plugin
   ordering.
4. Consider §3 (the CX-1 headline pin held by its sibling arm) as its own
   row — it is the same class, it is CX-1's, and it is not what CX5-L5-F6
   filed.
