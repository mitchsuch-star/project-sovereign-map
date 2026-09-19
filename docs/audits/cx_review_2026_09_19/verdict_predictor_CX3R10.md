# VERDICT — `CX3-R10` · **CONFIRMED (wider than filed) / PRE-EXISTING**

Filed by lens `predictor` at P4. Default verdict was REFUTED. It survives.

**The defect reproduces byte-for-byte, is ~4× wider than the row says, and is
100% of its own case — while three of the row's supporting claims are FALSE and
its prescribed fix location is measured un-buildable.**

Baseline `727cf88a`, clean tree. My probes: `probes/r10/r10_{a..i}_*.py`, plus
my own `git archive` export of the pre-row tree at `probes/r10/tree_prerow/`.
Nothing under `backend/`, `godot-client/`, `tests/`, `docs/` or `tools/` was
written; no git command that mutates was run.

---

## 1. Does it reproduce AT ALL, exactly as stated? — **YES**

My own harness, fresh shipped-1805 board per utterance, real `POST /command`
(`r10_a_repro.py`):

```
  'Ney, hold'   success=True  AP 4->2  loc Rhineland->Rhineland
      order: {"type": "None", "target": "Rhineland", "path": []}
      msg  : Ney will hold Rhineland. Holding position.
             (Our maps read Rhineland as the province nearest your order, Sire.)
             Ney: "Standing guard while others win laurels. As you command."
             (2 AP - a standing strategic order to hold this ground turn after
             turn. For a single-turn tactical hold, order 'defend' at 1 AP.)
```

The player named no province. The game says it read one *for* them. The
mechanism is as filed: `strategic_executor.py:1686` calls
`movement_executor.destination_grounding_note(raw_input, hold_loc)` where
`hold_loc = target or marshal.location`, and the helper discloses whenever the
resolved name's tokens are absent from the raw text.

---

## 2. It is **WIDER than filed** — the row's own predicate is too narrow by half

The row says the helper *"has no branch for 'the player named no province'"*.
Measured, that is not the shape of the defect. The real predicate is *"the
resolved province is not among the typed tokens"* — and on a HOLD the province
is **derived from where the man stands**, so nothing the player can say grounds
it except the province name itself, which is the one thing they are not saying
when they say *hold your ground*.

**`r10_b_breadth.py` — 8 of 8 player marshals on the shipped boot:**

```
  Ney at Rhineland      AP 4->2  NOTE=True      Murat at Franche-Comte  NOTE=True
  Davout at Rhineland   AP 4->2  NOTE=True      Bernadotte at Franconia NOTE=True
  Soult at Lorraine     AP 4->3  NOTE=True      Massena at Milan        NOTE=True
  Lannes at Franche-C.  AP 4->2  NOTE=True      Napoleon at Lorraine    NOTE=True
```

**9 phrasings, not 1** — every natural English way of saying it:

| typed | false note |
|---|---|
| `Ney, hold` | ✗ fires |
| `Ney, hold position` | ✗ fires |
| `Ney, hold your position` | ✗ fires |
| `Ney, hold the line` | ✗ fires |
| `Ney, hold your ground` | ✗ fires |
| `Ney, stand your ground` | ✗ fires |
| `Ney, stand fast` | ✗ fires |
| `Ney, hold here` | ✗ fires |
| `Ney, hold there` | ✗ fires |
| `Ney, hold Rhineland` | silent (correct) |
| `Ney, hold at Rhineland` | silent (correct) |

**And it is 8 of the project's OWN committed golden-corpus rows**
(`r10_i_corpus_drive.py`, every corpus hold row that names no province, driven
at `/command`):

```
  'Gen. Ney, hold'                             FALSE-NOTE=True
  'Marshal Bernadotte, hold'                   FALSE-NOTE=True
  'Ney, hold position'                         FALSE-NOTE=True
  'Ney, hold here and attack next turn'        FALSE-NOTE=True
  'Ney, hold until Davout arrives then attack' FALSE-NOTE=True
  'Ney, hold your position, do not attack'     FALSE-NOTE=True
  'Ney, hold. Do not attack.'                  FALSE-NOTE=True
  'Ney, unless attacked, hold position'        FALSE-NOTE=True

  driven: 25   printed the false disclosure: 8
```

Every corpus row that reaches a hold execution on a live 1805 marshal without
naming a province prints it — **8 of 8, 100% of its own case.** These are not
contrived shapes: the project authored them into its own regression corpus as
how a player says *hold*, and `_execute_help` teaches the bare `'hold'`.

⛔ **And the corpus is structurally blind to it**: `backend/ai/parser_eval.py`
contains the string `message` **zero** times — the gate stops at
`CommandParser.parse`. Eight rows reproduce the defect and the instrument that
runs them cannot see it.

---

## 3. Severity — **filed P4, I rule P3**, with the case for P4 stated

Up from P4 because:

* it is 100% of an ordinary action on 8 of 8 marshals and 9 phrasings, not an
  edge;
* it is the through-line this project keeps re-finding — *the system computes
  the right answer and tells the player a different one*; and
* the note is a **safety disclosure**. Its whole job is to be believed when
  `Soult, hold Mainz` silently becomes Maine. A player who meets it on every
  routine hold learns to skim it, which is a real cost charged to FA-54's own
  fix. Crying wolf on a warning is worse than a stray sentence.

Not higher than P3 because it is copy only: the order is a HOLD, at the right
province, at the documented price. No mechanical harm, nothing mis-charged.

---

## 4. Player-reachable? — **YES, measured, 16 of 16**

`r10_e_redirect.py` ports `_redirect_diplomatic_command` (`main.gd:2007`) with
the keyword tables **read out of `main.gd` itself**, not transcribed — 156
diplomatic keyword forms (`family=115`, `no_home=18`, `anywhere=13`,
`address=6`, `gated=2`, `war_room=2`; the brief's "114" is the family table
approximately, the total is 156).

```
  16 of 16 hold phrasings -> client SENDS to /command  (fail-open -> backend)

  control (must be CLAIMED):
    'declare war on Austria'    -> CLAIMED (CABINET)
    'request terms'             -> CLAIMED (WAR ROOM)
    'Talleyrand, court Bavaria' -> CLAIMED (CABINET)
```

No hold/stand/ground/position token appears anywhere in the redirect tables
(the only grep hit in `main.gd:1721-2006` is a comment). The typed road is real.

---

## 5. Did row CX introduce it? — **NO. PRE-EXISTING, and proven by experiment**

Not by reading a diff. I exported `b4a27a15^` (= `f7008582`, IQ-10, the commit
immediately before row CX) with `git archive` and ran the same probe against
that tree (`r10_c_prerow.py`):

```
TREE UNDER TEST: ...\probes\r10\tree_prerow\backend

  'Ney, hold'               AP 4->2  FALSE-NOTE   (identical sentence)
  'Ney, hold position'      AP 4->2  FALSE-NOTE
  'Ney, hold your ground'   AP 4->2  FALSE-NOTE
  'Ney, stand your ground'  AP 4->2  FALSE-NOTE
  'Ney, hold Rhineland'     AP 4->2  (silent)
  'Soult, hold Mainz'       AP 4->3  FALSE-NOTE
  'Davout, hold'            AP 4->2  FALSE-NOTE
  'Massena, hold'           AP 4->2  FALSE-NOTE
```

Byte-identical output. The helper and the HOLD branch both `diff` clean against
HEAD. The row's own `shipped_by_this_row: false` is correct.

### 5a. ⛔ But its amplification claim is **FALSE**

> *"CX-3 makes it routine by putting `hold` in the completer's top-five verbs
> for every marshal."*

`hold` is **9th of 12** in `_MARSHAL_VERBS` (`main.gd:6882`) — after attack,
march to, move to, scout, fortify, unfortify, drill, defend — and
`MAX_SUGGESTIONS` is **5**. I ported `_build_completions` /
`_add_verb_or_target` and censused the whole prefix universe
(`r10_d_completer.py`):

```
D1 -- the bare addressee prefix, all 8 marshals:
  Ney -> ['Ney, attack ', 'Ney, march to ', 'Ney, move to ',
          'Ney, scout ', 'Ney, fortify']        hold-offered=False
  ... 8 of 8: hold-offered=False

D3 -- CENSUS over every one- and two-letter prefix:
  prefixes driven               : 5832
  prefixes offering `<M>, hold` : 24
  ...of which at RANK 1         : 24
  the Tab-reachable prefixes    : ['Ney, h', 'Ney, ho', 'Davout, h', ...]
```

`hold` reaches the line at **24 prefixes of 5,832**, and all 24 are `<M>, h` /
`<M>, ho` — i.e. only after the player has typed `h` **for** hold. CX-3 does not
suggest the verb; it completes an intent the player already stated. The
amplification is real but it is *"one keystroke after you type h"*, not *"top
five for every marshal"*.

Given §2, the completer is a side road anyway: the 9 phrasings and the 8 corpus
rows need no completer at all.

### 5b. ⛔ And *"(and it costs 2 AP)"* is not a defect

The row's own quoted message discloses it and names the cheaper alternative in
the same breath — `(2 AP — a standing strategic order… For a single-turn
tactical hold, order 'defend' at 1 AP.)`. It is also not universal: Soult
(literal) and Napoleon (sovereign) pay **1**. Struck as an aggravator.

---

## 6. Would the suggested fix ship a regression? — **YES, and invisibly**

### 6a. The fix cannot be built where the row points it

`r10_f_fixshape.py`, two measurements:

```
F2 -- the parser's own output:
  'Ney, hold'             action=hold marshal=Ney target='Rhineland'
  'Ney, hold your ground' action=hold marshal=Ney target='Rhineland'
  'Ney, hold Rhineland'   action=hold marshal=Ney target='Rhineland'
```

**The parser has already collapsed the distinction.** `target` is `'Rhineland'`
whether the player named it or not, so the HOLD call site cannot tell them
apart either.

```
F3 -- signature: destination_grounding_note(raw_text, resolved_name: str) -> str
      references `world`   : False
      references `regions` : False
```

The helper is pure. It has no roster, so *"the player named no province"* is not
a branch it can compute. **The one-line fix the row prescribes does not exist at
the address it gives.**

### 6b. The fix a builder would then reach for silences four real substitutions

With `target` indistinguishable, the cheap shape is *suppress when the held
province is where he already stands*. Measured (`r10_g_naivefix.py`) — what that
would silence:

```
  'Ney, hold Rhinland'   stands=Rhineland resolved=Rhineland note=True  SILENCED
  'Ney, hold Rheinland'  stands=Rhineland resolved=Rhineland note=True  SILENCED
  'Soult, hold Loraine'  stands=Lorraine  resolved=Lorraine  note=True  SILENCED
  'Soult, hold Lorrain'  stands=Lorraine  resolved=Lorraine  note=True  SILENCED
```

Those are **FA-54's own class** — a typo'd province name silently auto-corrected
on a *standing* order — and `Rheinland` / `Loraine` are the exonym spellings a
1805 player actually types. The cheap fix re-opens the row it is patching.

**It would red no pin.** The FA-54 class
(`tests/test_fa_slice1_the_two_words_2026_09_02.py:630-697`) pins
`Soult, hold Mainz` must disclose (Maine ≠ Lorraine, survives) and
`Soult, hold Lorraine` must not (survives). Nothing covers a typo that resolves
back to the marshal's own province, and nothing anywhere asserts the note fires
on a bare hold (`grep "Our maps read"` → 6 assertions, none of them this). The
regression would be invisible to all 23,618 tests. ⛔ *The project's own
recurring lesson, once more: attack the fix by adding the one clause the builder
held constant — here, a typo of the province he is standing on.*

### 6c. The fix shape that works

Distinguish a **stated** destination from a **derived** one, at the only place
that knows: give the executor a roster-aware wrapper (the executor has `world`;
the pure helper keeps its signature so
`test_the_two_routes_share_one_helper` stays green), and disclose only when the
player named *a province* that is not the one resolved. Or mark it at the
parser as `target_source: stated|derived`.

The pin must be the case 6b silences: **`Soult, hold Loraine` at Lorraine still
discloses, while `Soult, hold` does not.** A pin that only drives `Ney, hold`
green-lights the regression.

---

## 7. Found while refuting — recorded, not filed

`Massena, hold Milano` → resolves to Milan and stays **silent**, because
`name.lower() in raw` grounds `milan` inside `milano`. FA-54 closed the
`main`/`Maine` direction (typed shorter than the name) and not this one (typed
longer). I do **not** file it: the resolution is correct and the note exists for
wrong ones. Noted only because it is the same arm and a future fix will touch it.

---

## 8. Bottom line

| | |
|---|---|
| reproduces | **yes, exactly, and wider** |
| severity | filed P4 → **P3** |
| player-reachable | **yes** — 16/16 sent, redirect ported from `main.gd`'s own tables |
| shipped by row CX | **no** — byte-identical at `b4a27a15^`, proven on an exported tree |
| row's claim "top-five verbs for every marshal" | **FALSE** — 0 of 8 at the bare prefix; 24 of 5,832 prefixes, all `<M>, h` |
| row's claim "(and it costs 2 AP)" | **not a defect** — disclosed in the same sentence; 1 AP for Soult and Napoleon |
| fix as prescribed | **un-buildable at the named address**; the obvious substitute ships an unpinned regression |
