# VERDICT: CX5-L5-F1 — NARROWED (defect real, cause and fix both wrong)

**Tree:** `master 727cf88a`, clean. Nothing under the repo was modified.
**Method:** every number below is from a probe I ran myself, on the shipped
1805 board (`WorldState.from_scenario(europe_1805.json)`), `LLM_MODE=mock`,
`provider=MOCK key_source=none` (no live call is possible), one fresh world
per utterance. Probes:
`probes/{drive,p1_repro,p2_arms,p3_prerow,p4_parse_prerow,p5_client_gate,
p6_fix_regression,p7_severity,p8_reach,p9_better_fix,p10_regression_drive,
p11_vocab,p12_clause_robust,p13_mirror,hoist_plugin,clause_plugin}.py`.

---

## 1. DOES IT REPRODUCE? — YES, 8 of 8, exactly as filed

`POST /command` through `TestClient`, one fresh 1805 board each. The filed
headline case, verbatim:

```
Ney, screen the withdrawal as they fall back
   _mentions_screening_idiom = True     _retreat_is_a_noun = True
   -> "Ney bristles at the retreat order but obeys. Ney retreats from
       Rhineland to Lorraine.  Army begins recovery (currently at -45%
       effectiveness). Will recover over 3 turns."
      AP 4->4, Ney Rhineland -> Lorraine
```

and all seven siblings, each `AP 4->4`, each `retreats from ... to Lorraine`,
each `-45% effectiveness ... 3 turns`. The structural claim is exact: the
branch at `llm_client.py:2099-2110` is a four-arm disjunction; CX-5 put
`_retreat_is_a_noun` on arm 1 (`"retreat" in`) and arm 3 (`"withdraw" in`),
and arms 2 (`"fall back"`) and 4 (`_mentions_plain_retreat`) carry neither it
nor `_mentions_screening_idiom`. Arm attribution, measured per sentence:

| utterance | noun | screen | arm that fires | parse |
|---|---|---|---|---|
| Ney, screen the withdrawal as they fall back | **True** | **True** | 2 | retreat/**0.9** |
| Ney, cover the retreat as they fall back | **True** | **True** | 2 | retreat/0.9 |
| Ney, cover the rear as they fall back | False | **True** | 2 | retreat/0.9 |
| Lannes, cut off the retreat as they fall back | **True** | False | 2 | retreat/0.9 |
| Lannes, harass their withdrawal as they fall back | **True** | False | 2 | retreat/0.9 |
| Lannes, ride down the enemy as they pull back | False | False | 4 | retreat/0.9 |
| Lannes, hit them as they fall back | False | False | 2 | retreat/0.9 |
| Lannes, punish the Austrians as they pull back | False | False | 4 | retreat/0.9 |

Confidence **0.9 > the 0.70 escalation gate**, so the filed "a key cannot
correct it" holds.

---

## 2. ATTRIBUTION — PRE-EXISTING, and now verified properly

⚠ The lens attributed by flipping **one** lever, `A_RETREAT_CAN_BE_A_NOUN`.
Row CX is six commits and also changed `clause_guards.py`, `counsel.py`,
`question_desk.py`, `executor.py`, `meta_executor.py` and **425 lines of
`main.gd`** — a single-lever flip cannot attribute across that. So I extracted
the **true pre-row tree** (`git archive b4a27a15^ backend`, read-only) and ran
the same sentences against it. The executed outcome is RNG-flaky (the
objection roll fires on some worlds), so I attributed on the **parse**, which
is pure:

```
head    | Ney, screen the withdrawal as they fall back      | retreat | 0.9
prerow  | Ney, screen the withdrawal as they fall back      | retreat | 0.9
   ... all eight byte-identical, retreat/0.9 on both trees ...
controls (what CX-5 DID move):
head    | Lannes, cut off the retreat  | None     <- refused
prerow  | Lannes, cut off the retreat  | retreat/0.9
head    | Lannes, press the retreat    | None     <- refused
prerow  | Lannes, press the retreat    | retreat/0.9
```

**`shipped_by_this_row: false` is CORRECT**, and now on stronger evidence than
was filed.

---

## 3. PLAYER-REACHABLE — YES, verified against the shipped client

The only client-side interception on the typed road is
`main.gd::_redirect_diplomatic_command` (called at `main.gd:1689`; the CX-3
predictor is Tab-completion and never sends). I ported that function and
**extracted its lists from HEAD `main.gd` rather than retyping them** —
115 family keywords, 18 no-home, 2 war-room, 13 nation-anywhere, 6 diplomat
names, 20 address-exempt, 7 advisory:

```
Ney, screen the withdrawal as they fall back      -> reaches backend
... all eight                                     -> reaches backend
declare war on Austria                            -> REDIRECTED  [family:declare war on]
Talleyrand, propose peace to Prussia              -> REDIRECTED  [family:propose peace]
```

`claims player-reachable: true` — **CONFIRMED.**

---

## 4. SEVERITY — P2 stands for the class; the harm is clean and deterministic

30 seeds per utterance with `random.seed()` set immediately before the
request (the earlier objection variance was ambient RNG state, not a
mitigation):

```
'Ney, cover the retreat as they fall back'      {'retreated': 30, 'objection': 0, 'other': 0}
'Ney, screen the withdrawal as they fall back'  {'retreated': 30, 'objection': 0, 'other': 0}
'Lannes, cut off the retreat as they fall back' {'retreated': 30, 'objection': 0, 'other': 0}
```

No objection modal intercepts. AP 4→4 (free), marshal displaced, −45%
effectiveness for three turns, unreachable by LLM escalation. That is the
identical harm CX-5 itself shipped a slice to close.

**But the reachable surface is much narrower than the filed text implies**, and
this is the one place severity should be read down. The mock chain is an elif
ladder and the attack/charge/pursue/hold branches sit **above** the retreat
branch, so the leak can only bite a verb none of them claims. 28 verb-phrases
× 5 trailing clauses, marshal-addressed, measured:

```
                    as they fall back   as they pull back   while they fall back   when they pull back   (no tail)
attack/charge/pursue/crush/smash/engage/rout/destroy/assault/harry/intercept/
hunt down/shell/finish them   ->  attack|charge on every tail      -- IMMUNE
cut off|cut down|press|block|exploit the retreat, punish|hit|harass|bleed them,
ride down the enemy, screen the withdrawal, cover the retreat|rear, cut them up
                    retreat*            retreat*            None                   None                  None
```

**28 of 140 cells leak.** Every verb the attack vocabulary knows is safe; a
`while`/`when` tail is safe; only an `as they fall/pull back` tail with a verb
outside the attack vocabulary reaches the branch. PARSE-NEG is clean
(`Ney, do not fall back` → None; `Ney, hold your ground while they fall back`
→ hold).

---

## 5. ⛔ THE FILED CAUSE IS WRONG FOR 3 OF ITS OWN 8 EXEMPLARS

`Lannes, ride down the enemy as they pull back`, `Lannes, hit them as they
fall back` and `Lannes, punish the Austrians as they pull back` have
**`_retreat_is_a_noun = False` and `_mentions_screening_idiom = False`**. They
are not instances of "the guard can return True and the marshal retreats
anyway" — no guard returns True for them. The finding's own sentence,
*"the row's own predicate already answers correctly for three of them"*,
under-counts in the wrong direction: the guards fire for **5** of the 8, and
the other **3 are not the filed mechanism at all**.

They are a **different defect with a different owner**: `hit`, `punish`,
`bleed`, `harass`, `ride down` and `cut up` are colloquial battle verbs missing from
`backend/ai/attack_vocabulary.py`. Measured against the module itself:

```
  hit        mentions_attack('hit them')     = False  -> 'Ney, hit them as they fall back'    -> retreat
  punish     mentions_attack('punish them')  = False  -> ...                                  -> retreat
  bleed      mentions_attack('bleed them')   = False  -> ...                                  -> retreat
  ride down  mentions_attack(...)            = False  -> ...                                  -> retreat
  cut up     mentions_attack(...)            = False  -> ...                                  -> retreat
  harass     mentions_attack('harass them')  = False  -> ...                                  -> retreat
  finish     mentions_attack('finish them')  = TRUE   -> ...                                  -> attack
```

`finish` is the control: it is in the vocabulary, `mentions_attack` sits above
the retreat branch, and the identical tail parses `attack`. ⛔ I struck `shell`
from this list before publishing — it also parses `attack` but
`mentions_attack('shell them')` is **False**; it is claimed by the artillery
branch, which is a different door. Add the six verbs and three of the eight
filed sentences become attacks, which is what the player meant, without
touching the retreat branch at all.

---

## 6. ⛔ THE SUGGESTED FIX SHIPS A REGRESSION, AND THE CORPUS AND SUITE ARE BLIND TO IT

The filed fix — *"put the two guards on all four arms (or, better, hoist them
above the disjunction)"* — was simulated exactly, without touching the repo:
`_names_a_destination` is called in precisely three places (arm 2, arm 3, and
the first line of `_mentions_plain_retreat` = arm 4), and arm 1 is already
guarded, so forcing it True whenever a guard fires **is** the hoist.

```
rule                        leaking cells   genuine retreat orders kept   golden corpus
HEAD                            28/28                17/17                  688/688
filed fix (hoist)               12/28                13/17 (parse) / 3 real   688/688
clause-aware on arms 2/4         0/28                17/17                  688/688
```

**It closes 16 of 28 cells (5 of the 8 filed sentences) and REFUSES four
orders that parse as a retreat today — of which THREE are verified to execute
a real retreat end to end at HEAD** (driven, `random.seed(7)`, `POST
/command`):

```
Ney, fall back, the enemy is retreating     -> Ney Rhineland->Lorraine, -45%/3 turns   ** breaks **
Ney, pull back, their retreat has begun     -> Ney Rhineland->Lorraine, -45%/3 turns   ** breaks **
Ney, fall back, a retreat is our only hope  -> Ney Rhineland->Lorraine, -45%/3 turns   ** breaks **
Ney, fall back and cover the retreat        -> "I could not make out a destination in
                                                that order, Sire" (no retreat at HEAD)
```

⛔ I struck my own fourth case before publishing: it parses `retreat` but does
not execute one, so the fix breaking it is not a regression. **The regression
is three orders, not four.**

The first of these is the **retreat twin of CX-5's own recorded win** — the
record celebrates that *"`Ney, march to Swabia, the enemy is retreating` … no
longer turns a march into a rout."* The filed fix breaks the same sentence
with `fall back` as its head.

**Which pin would red? NOT ONE — I ran the whole suite to find out.** With the
fix applied through a `-p hoist_plugin` monkeypatch (no repo file touched):

```
golden corpus                        688/688   (0 rows moved, either direction)
7 retreat-adjacent test files        604 passed
FULL SUITE  pytest tests/ -x         23,656 passed, 4 skipped   (12m24s)
```

**That is the hazard, not a comfort.** A builder who follows the filed
instruction gets a green corpus, a green 23,656-test suite, and three silently
broken orders — which is verbatim this row's own CX-6 lesson (*"NOTHING PINNED
EITHER, on either side of the change, which is why no test run could have
found it"*), one layer out.

---

## 6b. ⛔ THE MIRROR — FOUND BY ATTACKING THE FIX, AND WORSE THAN THE FINDING

Probing the clause hypothesis turned up the same blindness one door **UP** the
elif ladder, where `mentions_attack` matches a verb inside the subordinate
clause of a **plain retreat order**. Driven, `random.seed(3)`, fresh 1805
board, reaches the backend (client gate checked):

```
Ney, retreat as they attack          ap 4->3   casualties {Ney 1924, Davout 1728,
Ney, pull back, they are attacking   ap 4->3    Lannes 1195, Murat 1460, Napoleon 664}
  -> "Your words named no foe our maps know, Sire - Ney marches on Mack at Swabia,
      the nearest in sight." MUSTER - five French corps INCLUDING THE EMPEROR,
      6,971 casualties, 1 action point spent.
Ney, retreat, we are beaten          ap 4->4   -> retreats correctly (control)
```

Parse is `attack/0.9` (and `charge/0.9` for *"fall back as they charge"*) on
**both** HEAD and `b4a27a15^`, so this is pre-existing too — but it is
strictly worse than CX5-L5-F1: it spends an action point, commits the
Emperor's Guard and costs ~7,000 men, where the filed defect is free. A player
typing the reason for his own retreat gets a general engagement.

Not part of this verdict's ruling; **routed as a sibling for the owner**, and
it is the strongest evidence that the root is the subordinate clause rather
than the guard wiring. **Recommended P1 on the row's own calibration**:
`BUG_FIXES` CX-1a is P1 for *"a question fought a real battle — one action
point and six French corps bled"*, which is this case to the digit. By the same
table CX5-L5-F1 itself sits at **P2** (no AP, no casualties, a real state
change), which is where it was filed — that part of the finding I do not move.

---

## 7. THE ROOT, MEASURED

Both existing guards are about the **object** (*"the retreat"* after a
determiner). The leak is about the **clause**: arms 2 and 4 match a bare
substring anywhere in the sentence, including inside a trailing subordinate
clause with a third-party subject. Gating those two arms on the retreat phrase
being the **head of the order** rather than the content of an `as they fall
back` clause closes **28 of 28** and keeps **17 of 17** genuine orders, corpus
688/688 — the only one of the three rules that is strictly better than HEAD on
both axes.

```python
_SUBORDINATE = re.compile(
    r"\b(?:as|while|whilst|when|after|before|once|because|since)\s+"
    r"(?:they|he|she|it|the\s+\w+|\w+s)\s+(?:are\s+|is\s+)?"
    r"(?:fall|falls|falling|pull|pulls|pulling)\s+back\b")
# arms 2 and 4 yield when EVERY occurrence of the phrase is inside such a clause
```

Measured under the same instruments as the filed fix: golden corpus
**688/688**, and the seven retreat-adjacent test files **604 passed** under a
`-p clause_plugin` monkeypatch. Offered as the measured shape of a correct
fix, not as a prescription — the owner's call, and it needs its own pins on
`Ney, fall back, the enemy is retreating` and on `Ney, cover the retreat as
they fall back` in both directions, neither of which anything pins today.

---

## 8. SMALLER CORRECTIONS TO THE FILED TEXT

* *"the golden-corpus NEGATIVE pin `ney-cover-the-retreat` plus five words"* —
  four words (`as they fall back`). The pin is real:
  `{"success": false, "error_contains": "Unknown action"}`.
* *"Fixing it is one line per arm"* / *"Closes eight reproduced cases"* —
  measured, one line per arm fixes **5** of the 8 sentences it is offered for
  (16 of 28 cells) and breaks 3 working orders. The literal reading ("guards on
  all four arms") and the hoist are behaviourally identical here: arm 2 and
  arm 3 short-circuit on `_names_a_destination`, arm 4 on
  `_mentions_plain_retreat`’s first line, arms 1 and 3 already carry both.
* The lens's own executed transcript shows all eight retreating; on my first
  unseeded run `Ney, cover the retreat as they fall back` **objected** instead.
  Both are the same retreat order; the outcome is RNG. Any pin written for this
  family must assert the parse or `pending_objection`, not `moved` — which is
  the lens's own F6 point, and it applies to its own F1 evidence.
* The clause rule was checked for false positives on nine genuine fall-back
  orders that carry a subordinate clause (`Ney, fall back as they advance`,
  `Ney, as they fall back, pull back to the ridge`, …): **0 of 9** move.
* A grep over `tests/` and `docs/` for `as they fall back`, `as they pull
  back`, `retreat as they` and `they are attacking` returns **zero hits**
  outside the corpus data file. Neither this defect nor the mirror is pinned
  or documented anywhere, in either direction — which is why the filed fix
  can be built, be green, and break three working orders.

---

## VERDICT

**NARROWED.** The defect is real, reproduces 8 of 8 exactly as filed, is
player-reachable through the shipped client, is **pre-existing** (verified on
`b4a27a15^`, not merely on CX-5's lever), and is worth **P2** for its harm
class. But the finding's *cause* accounts for only 16 of the 28 measured cells
and 5 of its own 8 exemplars, and its *fix* would close 57% of the leak while
silently refusing three genuine retreat orders — verified end to end — with a
green corpus and a green suite. Build the clause rule, not the guard rewiring.
