# LENS 5 — ATTACK THE RETREAT-AS-NOUN RULE (CX-5)

Tree: `master 727cf88a`, clean. Everything below was measured on the shipped
1805 board (`parser_eval.build_world("1805")`) driven at `POST /command`
through `TestClient`, one fresh board per utterance, `LLM_MODE=mock`, zero
live calls. Attribution to CX-5 is always by flipping
`llm_client.A_RETREAT_CAN_BE_A_NOUN` and re-parsing the same utterance, never
by reading the diff.

Probes: `probes/{drive,parse,lever,sweep,inert_pins,seedsweep,pension,falsegreen}.py`
and the utterance files beside them. Nothing under the repo was modified.

**Tree is green at HEAD**: `test_cx1_a_question_never_orders.py` +
`test_cx3_the_predictor.py` = 151 passed. Golden corpus 688/688.

---

## HEADLINE

The row's own thesis is right and its implementation is the same shape it
condemns. §50.10 says *"when a guard names VERBS, ask what SHAPE it is really
about; and when the shape has a small closed exception set, invert the
allowlist."* **Neither set is closed.** CX-5 replaced a 4-verb allowlist with
a **13-verb allowlist plus a 6-determiner allowlist**, and both leak:

* **12 of 12** hand-written natural *act-on-somebody-else's-retreat*
  phrasings still march the player's own marshal away — free, 0 AP, −45%
  for three turns — at confidence **0.90–0.95**, which is *above* the
  escalation gate, so a key cannot correct them. That is the exact property
  the commit message names as what made the original defect unfixable.
* **23 genuine retreat orders that worked before CX-5 are now refused.**
* And the predicate is wired into **2 of the 4 arms** of the disjunction it
  guards, so `_retreat_is_a_noun` can return **True** and the marshal
  retreats anyway. `Ney, cover the retreat as they fall back` — the golden
  corpus's own pinned sentence plus five words — **retreats Ney**.

A sharp way to see the incompleteness: the cases CX-5 *fixed* now sit at
confidence 0.5 and **do** escalate to the LLM with a key; every case it
*missed* sits at 0.90–0.95 and **never** escalates. The fix moved the solved
half into the recoverable band and left the whole unsolved half in the
unreachable one.

---

## F1 — P2 — THE GUARD IS WIRED INTO 2 OF THE 4 ARMS (`shipped_by_this_row: false`)

The branch is a four-arm disjunction. CX-5 added `_retreat_is_a_noun` to arm 1
(`"retreat" in …`) and arm 3 (`"withdraw" in …`). Arm 2 (`"fall back"`) and
arm 4 (`_mentions_plain_retreat` — `pull back` / terminal `retire`) carry
**neither** the new guard nor the old `_mentions_screening_idiom`. So a
sentence that both guards call "not an order to run" retreats anyway.

Reproduced, `POST /command`, one fresh 1805 board each:

```
Ney, screen the withdrawal as they fall back
   predicates: _mentions_screening_idiom=True  _retreat_is_a_noun=True
   -> "Ney bristles at the retreat order but obeys. Ney retreats from
       Rhineland to Lorraine. Army begins recovery (currently at -45%
       effectiveness). Will recover over 3 turns."
      AP 4->4, Ney Rhineland -> Lorraine

Ney, cover the retreat as they fall back        -> Ney retreats to Lorraine
Ney, cover the rear as they fall back           -> Ney retreats to Lorraine
Lannes, cut off the retreat as they fall back   -> Lannes retreats  (noun=True)
Lannes, harass their withdrawal as they fall back -> Lannes retreats (noun=True)
Lannes, ride down the enemy as they pull back   -> Lannes retreats
Lannes, hit them as they fall back              -> Lannes retreats
Lannes, punish the Austrians as they pull back  -> Lannes retreats
```

`Ney, cover the retreat` is golden-corpus row `ney-cover-the-retreat`, a
**negative pin**, FA-73's own case. Five words of trailing clause defeat it.

Lever check: all eight are byte-identical with `A_RETREAT_CAN_BE_A_NOUN`
False, so the behaviour is pre-existing — but it is the class CX-5 exists to
close, and the row's own predicate already answers correctly for three of
them. Fixing it is one line per arm.

**Fix**: put the two guards on all four arms (or, better, hoist them above
the disjunction — `if _retreat_is_a_noun(cmd) or _mentions_screening_idiom(cmd):
skip the whole retreat branch`).

---

## F2 — P2 — THE DETERMINER ALLOWLIST MISSES EVERY POSSESSIVE AND DEMONSTRATIVE (`shipped_by_this_row: false`)

`_RETREAT_NOUN_RE` names six determiners plus `enemy`/`enemy's`. It omits
`your`, `my`, `that`, `this`, `these`, `those` and every proper possessive
(`Mack's`, `Austria's`, `the Austrians'`). So the slice's **own seven verbs**
still march the marshal away one determiner over, and the `(?:\w+\s+)?`
single-adjective window means two adjectives or an intervening noun defeats
it as well — which kills the canonical Napoleonic phrase *line of retreat*.

Reproduced end to end (all AP 4→4, all "retreats from Franche-Comte to
Lorraine … −45% effectiveness … 3 turns"):

```
Lannes, cut down Mack's retreat               conf 0.95   <- the commit's own verb
Lannes, cut off their line of retreat         conf 0.90
Lannes, cut off Mack's line of retreat        conf 0.95
Lannes, block that retreat                    conf 0.90
Lannes, exploit this withdrawal               conf 0.90
Lannes, block your retreat                    conf 0.90
Lannes, press the Austrians' retreat          conf 0.90
Lannes, exploit Austria's withdrawal          conf 0.90
Lannes, cut off Kutuzov's withdrawal          conf 0.90
Lannes, punish the disorderly Austrian retreat conf 0.90  <- two adjectives
Lannes, cut off the Austrian army's retreat   conf 0.90
Lannes, take advantage of Mack's retreat      conf 0.95
Lannes, sever / bar / turn / forestall their line of retreat
```

**12 of 12** of my hand-written natural act-on phrasings retreat. Combinatorial
reach (`probes/sweep.py`, 628 rows of *act verb × determiner × noun*):
**308 still parse as the player's own retreat**, in nine determiner buckets.

Two of them are worse than a silent retreat — the target resolver prints a
non sequitur on top:

```
Lannes, cut off Mack's line of retreat
 -> "Lannes retreats from Franche-Comte to Lorraine. Mack cannot be reached,
     Sire - no such province is known to the staff; Lannes falls back to
     Lorraine instead."
```

None of these escalates: 0.90/0.95 are above the 0.70 gate.

**Fix**: the determiner side is open-ended by nature (any proper possessive).
Match the *shape* instead — a possessive/`'s` token or a determiner-class word
before a retreat noun, and allow the noun to be reached through `line of`,
`route of`, `path of`, or 1–3 intervening words.

---

## F3 — P3 — THE CARRY-OUT ALLOWLIST REFUSES 15 NATURAL RETREAT ORDERS THAT WORKED BEFORE (`shipped_by_this_row: TRUE`)

The record says the four verbs *"are the whole set a player reaches for."*
They are not. `_ORDER_THE_RETREAT_RE` ships 13, and these worked before CX-5
and are refused at HEAD. Lever-attributed, each measured both ways:

```
utterance                              pre-CX5             HEAD
Lannes, carry out the retreat          retreat/0.9   ->    refused
Lannes, proceed with the retreat       retreat/0.9   ->    refused
Lannes, complete the withdrawal        retreat/0.9   ->    refused
Lannes, finish the withdrawal          retreat/0.9   ->    refused
Lannes, authorise|authorize the retreat retreat/0.9  ->    refused
Lannes, permit the retreat             retreat/0.9   ->    refused
Lannes, sanction the withdrawal        retreat/0.9   ->    refused
Lannes, sanction a general retreat     retreat/0.9   ->    refused
Lannes, approve the withdrawal         retreat/0.9   ->    refused
Lannes, direct the retreat             retreat/0.9   ->    refused
Lannes, instruct the retreat           retreat/0.9   ->    refused
Lannes, effect the withdrawal          retreat/0.9   ->    refused
Lannes, press on with the retreat      retreat/0.9   ->    refused
Lannes, get on with the retreat        retreat/0.9   ->    refused
```

Driven end to end, e.g. `Lannes, carry out the retreat` → AP 4→4, nothing
moves, *"Berthier adjusts his spectacles… Perhaps: 'Lannes, attack Mack' or
'Lannes, move to Paris'?"*

The carry-out determiner set (`the|our|an?`) also omits the possessives, so
another family regresses on the determiner alone:

```
Lannes, sound his retreat / order their retreat / begin his withdrawal
/ continue his retreat         all: retreat/0.9  ->  refused
```

Combinatorial reach (1,584 rows of *carry-out verb × determiner × adjective ×
noun*): **736 worked before CX-5 and are refused now**, 576 of them from the
missing `his/her/their/its` determiners alone.

⚠ **Severity qualifier, measured.** These land at confidence **0.5** with
`refusal=False`, so `_should_fallback_to_llm` **does** escalate them — a
player with a key almost certainly gets the retreat. The regression is real
in **mock**, which is the shipped launcher default for a keyless tester.

---

## F4 — P3 — `\bretreating\b` IS UNCONDITIONAL, SO THE CONTINUATIVE IS DEAD (`shipped_by_this_row: TRUE`)

The code comment claims the participle *"is always adjectival ('the retreating
Austrians')"*. It is also the progressive verb, and `_ORDER_THE_RETREAT_RE`
requires a determiner, which a bare participle never has. All eight worked
before CX-5:

```
Lannes, keep retreating        retreat/0.9 -> refused
Lannes, continue retreating    retreat/0.9 -> refused
Lannes, begin retreating       retreat/0.9 -> refused
Lannes, start retreating       retreat/0.9 -> refused
Lannes, resume retreating      retreat/0.9 -> refused
Lannes, go on retreating       retreat/0.9 -> refused
Lannes, keep on retreating     retreat/0.9 -> refused
Lannes, stay retreating        retreat/0.9 -> refused
```

Driven: `Lannes, keep retreating` → AP 4→4, nothing moves, *"…Might you mean
'Lannes, scout' or 'Lannes, defend'?"*

This is reachable from the game's own vocabulary: the Generals card prints
**`RETREATING (stage: N)`**, the ledger status is `"retreating"`, the intel
report and dispatch both use the word. A player watching a retreat in progress
and typing *"Ney, keep retreating"* gets a shrug. (`continue the retreat`
works, because the determiner is there — so the behaviour is inconsistent
across two spellings of one order.)

The task's own two examples are **safe** and I record that: `Ney, stop
retreating` and `Ney, cancel the retreating order` both resolve to `cancel`
in both lever arms — the `stand_down` / cancel branches sit above the retreat
branch.

**Fix**: only treat the participle as adjectival when it is *not* the head of
the clause — e.g. require a following noun (`the retreating Austrians`,
`retreating column`) or a preceding determiner, and exempt a continuative
auxiliary (`keep|continue|start|begin|resume|go on|stay`).

---

## F5 — P3 — THE SHRUG THE PLAYER GETS IS THE PRE-CX-2 CANNED ROTATION, AND NEVER NAMES `retreat` (`shipped_by_this_row: false`; the record's claim is FALSE)

The record justifies the fall-through with *"Since CX-2 the shrug answers with
orders that would actually be carried out, so that fall-through is now useful
rather than bare."* **Measured: false for this fall-through.**

`_berthier_mock_response` has three template groups. CX-2 rewrote only the
`else:` group (nothing recognised) — that is the one that calls
`_counsel_lines(game_state)`. Every CX-5 refusal is an *addressed* order, so
`recognized_marshal` is always set and the answer always comes from the
**untouched** first group, chosen by `random.choice`:

```
"…Perhaps: '<M>, attack <first_enemy>' or '<M>, move to Paris'?"   <- Paris hardcoded
"…Valid orders include: attack, move, scout, defend, fortify, recruit."
"…Might you mean '<M>, scout' or '<M>, defend'?"
```

Verified for all ten refusals — every observed message is one of those three.

The offers do execute (`Lannes, move to Paris` → 2 AP march via Nivernais;
`scout`, `defend`, `attack Mack` all work), so they are not *lies*. But:

* **`retreat` is never named.** `recovery_action_vocabulary("typed")` returns
  **53** verbs and *does* contain `retreat`; the sample is hardcoded to
  `attack, move, scout, defend, fortify, recruit`. The one occasion where the
  player provably wanted the retreat verb is the one where it is withheld.
* Nothing in the shrug says *why*. For the intended refusals the player is
  never told the marshal cannot act on somebody else's retreat, so the rule
  is unlearnable; for the F3/F4 regressions the player is told to scout.

**Fix**: call `_counsel_lines` in the `recognized_marshal` group too, drop the
hardcoded Paris, and — cheapest and most valuable — when the retreat branch
yields to `_retreat_is_a_noun`, carry that fact into the shrug: *"He cannot
act on another army's retreat, Sire. `Lannes, attack Mack`, or `Lannes,
retreat` if you mean his own."*

---

## F6 — P4 — 3 OF THE SLICE'S 10 HEADLINE PINS ARE INERT, AND 3 MORE CAN GO GREEN BY LUCK (`shipped_by_this_row: TRUE`)

Re-running `TestTheRetreatIsSometimesANoun` with the lever forced down (a
scratchpad pytest plugin; no repo file touched):

```
0/6 inert  binds   | Lannes, cut down the retreat
0/6 inert  binds   | Lannes, cut off the retreat
0/6 inert  binds   | Lannes, press the retreat
0/6 inert  binds   | Lannes, block the retreat
0/6 inert  binds   | Lannes, exploit the retreat
0/6 inert  binds   | Lannes, punish the retreat
0/6 inert  binds   | Lannes, ride down the retreating Austrians
6/6 inert  INERT   | Lannes, harry the retreat        <- refused by the PURSUE branch
6/6 inert  INERT   | Lannes, cover the retreat        <- the pre-existing guard
6/6 inert  INERT   | Lannes, screen the withdrawal    <- the pre-existing guard
```

Three rows pass with CX-5 deleted. The 35/35-killed mutation sweep cannot see
this: a mutation of `_retreat_is_a_noun` reds the other seven, so the file is
"killed" while three of its rows assert nothing about the fix.

**Worse — `_assert_inert` can pass while the retreat order is live.** For this
family its only live discriminator is `moved`; AP is 0 either way and there is
no battle. On boards where the marshal *objects*, nothing moves although the
order was read as a retreat. Measured over 60 seeds with the fix reverted,
`Lannes, press the retreat`:

```
seeds where _assert_inert PASSES although the fix is REVERTED: 6/60
  seed 31: "Lannes respectfully raises concerns: 'Retreat? We can still fight!'"
```

and at seed 31, driven: `moved=[]`, `AP 4->4`, `battle=False`,
`pending_objection=True` with `{"type": "major_objection", … "message":
"Lannes respectfully raises concerns: 'Retreat? We can still fight!'"}` — a
blocking modal with a retreat order behind it and a Proceed button. Under
pytest's randomised ordering this shows up directly: repeated lever-off runs
of the class gave 8, 8, 9, 8 failures, with `press` / `block` / `exploit`
each sometimes green.

This is the slice's own ⛔ lesson, applied to the wrong pin: it hardened
`test_a_real_retreat_still_retreats` to assert the *behaviour* and left the
same hazard in `test_he_does_not_march_away`, which is the load-bearing one.

**Fix**: assert on the message and on `pending_objection` too — *"no retreat
was ordered and none is pending"* — and move `harry` / `cover` / `screen` into
their own class so the CX-5 set is only what CX-5 causes.

Context, not a finding: **the golden corpus is blind to the whole slice** —
688/688 green with `A_RETREAT_CAN_BE_A_NOUN = False`. The commit's "0 rows
moved" is true, and the fuller truth is that no standing regression
instrument can see either half. The four retreat phrasings in
`tools/playtest_scripts/*.json` are likewise lever-independent (0 of 4).

---

## F7 — P4 — `guard` / `protect` EAT THE SCREENING IDIOM BEFORE IT IS ASKED (`shipped_by_this_row: false`)

The HOLD family's bare `"guard"` / `"protect"` keywords sit *above* the
retreat branch, so `_mentions_screening_idiom` never gets a vote when either
word appears anywhere in the sentence:

```
Lannes, guard the retreat
 -> "Region 'Retreat' not found. Did you mean 'Crete'?"     AP 4->4

Lannes, cover the withdrawal of the guard      (screening idiom DOES match)
 -> "Lannes will hold Franche-Comte. Holding position. (Our maps read
     Franche-Comte as the province nearest your order, Sire.)"
    AP 4->2   <- two action points for a phrase that means screen the Guard
```

---

## F8 — P3 — A NOUN PHRASE STILL BUYS A FOUR-CORPS BATTLE (`shipped_by_this_row: false`)

The task's own item-2 example. `mentions_attack` claims it before the retreat
branch ever runs, so `_retreat_is_a_noun` — which correctly returns **True** —
is never consulted, and CR-6's guessed-target substitution takes over:

```
Lannes, smash the retreating column
 -> "Your words named no foe our maps know, Sire - Lannes marches on Mack at
     Swabia, the nearest in sight. Name another and he will turn.
     MUSTER - Lannes (18,000; 82,340 if all march…) vs Mack…"
    AP 4->3, battle fought, MOVED: Davout, Lannes, Napoleon, Ney -> Swabia
    (the Emperor's Guard committed)
```

Siblings: `Lannes, intercept the retreat` and `Lannes, harry the retreat` →
`"Cannot find 'Retreat' to pursue."` (inert); `Lannes, harry Kutuzov's
withdrawal` → attack on target `"Kutuzov'S Withdr…"`.

This is the documented guessed-target contract rather than a new defect, so I
file it as the honest answer to "find an eighth noun case it still treats as
an order" and leave the ruling to the owner: **a noun phrase naming no foe
should not commit four corps including Napoleon.**

---

## WHAT I CHECKED AND FOUND CLEAN

* **Item 4, the pension interaction: clean, and byte-identical under both
  lever arms.** With `Ney.pension = 120` on a real board: `withdraw Ney's
  rente` and `revoke Ney's rente` both revoke (pension 120→0, location
  unchanged, AP 4→4) with and without the fix; `withdraw Ney's pension` /
  `stop Ney's annuity` / `withdraw the rente from Ney` never march him. The
  new guard can only make the withdraw arm yield *earlier*, so it cannot
  displace `_mentions_pension`. Corpus rows `es7sp-withdraw-neys-rente` and
  `fa-slice7-withdraw-a-rente-is-not-a-march` green.
* **Item 5, AP: nothing is charged on any refusal.** All ten intended
  refusals and all 23 regressed orders measured `AP 4→4`, `admin 2→2`, gold
  unchanged, no battle, no marshal moved.
* **8 of 8 genuine retreat forms still retreat** (the record's claim holds):
  `retreat`, `fall back`, `pull back`, `retire`, and `sound|order|begin|call
  the retreat`. Also confirmed working: `order a general retreat`, `begin the
  immediate withdrawal`, `make a fighting retreat`-class adjectives, every
  `to <destination>` form, `tell Lannes to sound the retreat`, `order a
  general retreat, Lannes`, `all marshals retreat`, `when ready then retreat`.
* **Last-stand and forced-retreat dialogue answers are untouched.**
  `_INTERRUPT_KEYWORDS` contains no retreat vocabulary, and no dialogue option
  label anywhere in `backend/` names a retreat (`grep` over `"label"`/`"text"`
  and `"options"` → zero hits). The printed labels are *fight to the last* /
  *attempt a breakout* / *cut our way out*.
* **Player reachability: every finding is reachable through the shipped
  client.** `main.gd` contains no `"withdraw"` string at all, none of these
  phrasings carries a `DIPLO_*` keyword, and `retreat` is in both
  `DIPLO_ADDRESS_EXEMPT_WORDS` and the CX-3 `_MARSHAL_VERBS` predictor.
  Nothing is redirected.
* **The lever never mis-routes into a third action.** Across 2,212 swept rows,
  zero utterances changed to an action that is neither `retreat` nor a refusal.
* **A genuine win, recorded:** CX-5 rescues a real class the old guard lost —
  `Ney, march to Swabia, the enemy is retreating` and `Ney, march to Swabia,
  cut off the retreat` were `retreat` before and are `move` now (2 AP,
  strategic interrupt at the frontier). A trailing "the enemy is retreating"
  no longer turns a march into a rout.

---

## FALSE CLAIMS (measured)

1. **"Since CX-2 the shrug answers with orders that would actually be carried
   out, so that fall-through is now useful rather than bare."**
   (`COMMAND_EXPERIENCE_SPEC.md` §3.4, and the commit message.) False for this
   fall-through: CX-2 changed only the *nothing-recognised* template group,
   and every CX-5 refusal is an addressed order, so it always lands in the
   untouched `recognized_marshal` group with its hardcoded `move to Paris`.
   `_counsel_lines` is structurally unreachable from here.

2. **"`sound`, `order`, `begin` and `call` 'the retreat' … are the whole set
   a player reaches for."** (§3.4, `BUG_FIXES` §Row CX, and the code comment.)
   False: 15 natural verbs measured that worked before the fix and are refused
   now (`carry out`, `proceed with`, `complete`, `finish`, `authorise`,
   `permit`, `sanction`, `approve`, `direct`, `instruct`, `effect`, `press on
   with`, `get on with`, …). The supporting argument is also circular — *all*
   verbs retreated correctly before the fix, because the branch fired on the
   bare substring, so the pre-fix board contains no evidence whatever about
   which four are "the whole set". The shipped regex names 13 verbs, not 4.

3. **Code comment: "plus the participle, which is always adjectival ('the
   retreating Austrians')."** False: it is also the progressive verb. Eight
   continuative orders regressed (F4).

4. **`SYSTEMS_REFERENCE` §50.10: "when the shape has a small closed exception
   set, invert the allowlist."** The instance does not support the rule: the
   verb side leaks ≥15 members and the determiner side ≥9 (308 of 628 swept
   act-on rows still retreat). Either the guidance needs the caveat *only
   invert when the exception set is provably closed*, or the rule needs a
   different example.

5. **`BUG_FIXES` / the memo / the test class present all ten
   act-on phrasings as fixed by this row.** Three of the ten (`harry the
   retreat`, `cover the retreat`, `screen the withdrawal`) refuse for reasons
   CX-5 did not add, and their pins pass with the fix deleted (F6). The
   sentence "10 of 10 … now refuse free" is literally true; the attribution
   implied by grouping them is not.

---

## SUGGESTED ORDER OF WORK

1. **F1** — one line per arm, or hoist both guards above the disjunction.
   Closes eight reproduced cases including a defeated corpus pin.
2. **F4 + F3** — the two regressions this row shipped. F4 is a two-token rule
   (continuative auxiliary, or require a following noun); F3 wants the
   possessive determiners in `_ORDER_THE_RETREAT_RE` and either a much longer
   verb list or — better — inverting again: after a **carry-out-shaped** verb,
   *any* determiner means carry it out unless the object is a third party's.
3. **F2** — match the possessive/`'s` shape and reach the noun through
   `line|route|path of`; retire the single-adjective window.
4. **F6** — make the pins assert the message and `pending_objection`, and
   split the three non-CX-5 rows out of the class.
5. **F5** — carry the refusal's own reason into the shrug; it is the only
   change here that teaches the player the rule.
6. **F7 / F8** — owner's call.
