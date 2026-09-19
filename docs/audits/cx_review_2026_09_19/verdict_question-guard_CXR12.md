# VERDICT: CXR1-2 — **PRE-EXISTING** (behaviour confirmed; attribution refuted;
# breadth corrected in both directions; the prescribed fix would not close it)

Refuter pass on lens "question-guard"'s finding CXR1-2, at master `f52df77f`
(HEAD; row CX = `b4a27a15`..`727cf88a`, plus the docs-only `f52df77f`).

Every number below comes from a probe **I wrote and ran**, not from the filed
report. Mine are under
`…/scratchpad/cx_review/probes/refute_CXR12/` — `rh.py` (my own harness),
`p1_repro.py`, `p2_attribution.py`, `p3_fixes.py`, `p4_e2e_fix.py`,
`p5_client_gate.py`, `p6_breadth.py`, `p7_harm.py`, `p8_inconsistency.py`,
`p9_last.py`. Fresh shipped-1805 board per utterance through `POST /command`;
`LLM_MODE=mock`; no network call. The repo was not modified (every candidate
fix is a runtime monkeypatch, restored in a `finally`; one stray `harm.json`
my harness's `os.chdir(REPO)` dropped in the repo root was moved out and
`git status` is clean).

---

## 1. Does it reproduce? **YES — all twelve rows, exactly as filed.**

`p1_repro.py`, fresh board per utterance:

```
'can Ney attack Mack'                    q=True   inert          <- control
'can Ney attack Mack, Berthier'          q=False  AP 4->3 gold 800->533 BATTLE  moved Davout,Lannes,Napoleon,Ney
'can Ney attack Mack, sire'              q=False  AP 4->3 gold 800->517 BATTLE
'may Ney attack Mack, Berthier'          q=False  AP 4->3 gold 800->483 BATTLE
'can Ney attack Mack, do you think'      q=False  AP 4->3 gold 800->499 BATTLE
'can Ney attack Mack, or should Davout'  q=False  AP 4->3 gold 800->483 BATTLE
'has Ney attacked Mack, Berthier'        q=False  AP 4->3 gold 800->483 BATTLE
'is Swabia defended'                     q=True   inert          <- control
'is Swabia defended, Berthier'           q=False  AP 4->3  "All forces take defensive positions: Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena, Napoleon"
'is Swabia defended, and is Vienna'      q=False  AP 4->3  whole-army defend
'is Swabia defended, Napoleon'           q=False  AP 4->3  Napoleon -> DEFENSIVE
'does Ney hold Rhineland, Berthier'      q=False  AP 4->2  a standing HOLD order
```

The masking explanation also reproduces: `did we attack Mack, Berthier`,
`are we at war with Prussia, Berthier` and `is Swabia defended, I wonder` are
inert, and `_FIRST_PERSON_RE` is why. Gold figures differ from the filed ones
by tens (combat RNG); the verdicts and the footprints are stable.

The mechanism is stated correctly: `_TRAILING_CLAUSE_RE` is `,\s*\S`, arms (c)
and (d) stand down on any match, and a vocative satisfies it.

**And the lens is right that the builder's grid could not see it.** The row's
own instrument is committed at `tools/_cx_sweep_both_arms.py`: `LEADS × VERBS`
plus an `EXTRA` list. **Not one of its 684 cases carries a trailing comma.**
That is this repo's recorded lesson firing for the sixth time — the reviewer
adds the one clause the builder held constant.

---

## 2. Attribution: **`shipped_by_this_row: true` is FALSE.** ⛔

This is the decisive correction, and the lens did not test it.

`p2_attribution.py` runs three arms over the same twelve utterances —
**SHIPPED**, the row's own flip lever `A_QUESTION_NEVER_ORDERS=False`, and
**PRE-ROW**: the literal `is_question` from `git show b4a27a15^` loaded as its
own module (it is self-contained — only `re` and `typing`) and patched into
*both* readers (`clause_guards` and `llm_client`, which imports it by name).

```
                                          SHIPPED            PRE-ROW (b4a27a15^)
'can Ney attack Mack'                 q=True  inert      |  q=False AP4>3 BATTLE   <- MOVED
'can Ney attack Mack, Berthier'       q=False AP4>3 BATTLE|  q=False AP4>3 BATTLE   <- SAME
'can Ney attack Mack, sire'           q=False AP4>3 BATTLE|  q=False AP4>3 BATTLE   <- SAME
'may Ney attack Mack, Berthier'       q=False AP4>3 BATTLE|  q=False AP4>3 BATTLE   <- SAME
'can Ney attack Mack, do you think'   q=False AP4>3 BATTLE|  q=False AP4>3 BATTLE   <- SAME
'can Ney attack Mack, or should …'    q=False AP4>3 BATTLE|  q=False AP4>3 BATTLE   <- SAME
'has Ney attacked Mack, Berthier'     q=False AP4>3 BATTLE|  q=False AP4>3 BATTLE   <- SAME
'is Swabia defended'                  q=True  inert      |  q=False AP4>3           <- MOVED
'is Swabia defended, Berthier'        q=False AP4>3      |  q=False AP4>3           <- SAME
'is Swabia defended, and is Vienna'   q=False AP4>3      |  q=False AP4>3           <- SAME
'is Swabia defended, Napoleon'        q=False AP4>3      |  q=False AP4>3           <- SAME
'does Ney hold Rhineland, Berthier'   q=False AP4>2      |  q=False AP4>2           <- SAME
```

**Row CX moved exactly 2 of the 12 rows, and both moved from executing to
inert.** The ten comma cases are byte-for-behaviour identical to the pre-row
game. Read the pre-row source and it is obvious why: `can` and `is` were
already in the lead set before CX (the only lead CX *added* is `has|had`), and
pre-row `is_question` ended at

```python
return (lead_word in _WH_WORDS
        and bool(_AUXILIARY_RE.search(text[lead.end("lead"):])))
```

so `can Ney attack Mack, Berthier` returned False then too, with no comma
anywhere in the reasoning.

`_TRAILING_CLAUSE_RE` does not **cause** these executions. It **declines to
fix** them — it stands down *to the behaviour that was already there*. The
title's "so the row's own flagship controls execute one comma later" reads as
though the controls started executing; they never stopped.

---

## 3. But the row **does** amplify it — in a way the lens missed. ⚠

Pre-existing does not mean harmless here, and the honest version of this
finding is stronger than the filed one on this point.

**(a) The row created the inconsistency.** `p8_inconsistency.py`, over the 55
measured harm sentences (§4), comparing the bare form against the comma form:

```
PRE-ROW  (b4a27a15^): bare and comma forms DISAGREE in   0 of 55 pairs
SHIPPED  (f52df77f) : bare and comma forms DISAGREE in  55 of 55 pairs
```

Before the row the game was *consistently* wrong — both halves fought, so a
player learned "this game does not do questions" and stopped typing them.
After it, the bare half is fixed and the comma half is not, so the game now
contradicts itself on the same sentence.

**(b) CX-3's Predictor teaches the shape and then contradicts it in nearly
identical words.** `p9_last.py` drives the pair and diffs the two messages:

```
'can Ney attack Mack'            -> "Were you to give the order, Sire:
                                     MUSTER — Ney (24,000; 78,676 if all march,
                                     up to 96,789 if every corps arrives) vs Mack …"
'can Ney attack Mack, Berthier'  -> "MUSTER — Ney (24,000; 78,676 if all march,
                                     up to 96,789 if every corps arrives) vs Mack …"
                                     + a real battle, an AP, ~300 gold

lines in the forecast: 13; in the battle: 15; IDENTICAL lines: 11
```

**Eleven of the forecast's thirteen lines are byte-identical to the real
battle's.** The only text that distinguishes a free prediction from a fought
battle is the single preamble line *"Were you to give the order, Sire:"* —
and the sentence that picks between them differs by one comma. CX-3 built
that forecast, and CX-3's own census is titled *"the game must not offer a
sentence it cannot read"*. This is that rule's mirror image, and it belongs on
the row.

---

## 4. Breadth: wrong in **both** directions.

### 4a. It is not the vocative. It is the comma.

`p6_breadth.py`, over the row's own committed `LEADS × VERBS` product (648)
plus the non-punctuation entries of its `EXTRA` list — 660 distinct cases on
my list. (Measured in passing, `p10_numbers.py`: the row's own full grid is
**684 cases but 678 distinct** — `EXTRA` repeats six rows the product already
contains, incl. `can Ney attack Mack` and `may Ney attack Mack`. Immaterial to
the row's 121→9, noted so the next reader's arithmetic reconciles.)

```
, Berthier            211 / 667 of the guard's questions become ORDERS again
, do you think        211 / 667
, or should Davout    211 / 667
, and is Vienna       211 / 667
, please              211 / 667
, roughly             211 / 667
```

Six unrelated tails, the same count every time, because the predicate is
`,\s*\S`. The filed body does mention tags and alternatives, but the title and
the `CAUSE` say "vocative", which reads as a narrow linguistic edge case. It
is not: **any comma followed by a word** disarms the arm, including `, please`
and `, roughly`.

### 4b. 206 flip the verdict; only **55** actually spend anything.

`p7_harm.py` drives every one of the 206 flips on a fresh board. 151 flip the
verdict and are refused downstream anyway (`is Mack recruit, Berthier`,
`has Ney end turn, Berthier`, `can Ney declare war on Prussia, Berthier` …).
**55 execute.** Of those, 16 are ungrammatical concatenations the grid
manufactures (`is Ney attack Mack`, `has Ney attack`) — **~39 are grammatical
English a player could type.**

So the filed seven understate the harm, and the guard-level number would have
overstated it. The measured set contains worse cases than any filed:

```
'are they going to retreat, Berthier'        GENERAL RETREAT of all eight corps
'could Davout recruit, Berthier'             gold 800 -> 59   (741 gold, 1 admin AP)
'can Ney build a depot in Paris, Berthier'   300 gold + 1 admin AP
'could Davout fortify, Berthier'             AP 4 -> 2
'did Ney retreat, Berthier'                  Ney falls back, army to -45% effectiveness
'can Ney hold Lorraine, Berthier'            AP 4 -> 2, a standing HOLD
```

### 4c. A caveat the lens did not state: **the question mark saves it.**

`p9_last.py`, five cases, both punctuations:

```
'can Ney attack Mack, Berthier'      q=False  AP4>3 BATTLE
'can Ney attack Mack, Berthier?'     q=True   inert
'could Davout recruit, Berthier'     q=False  gold 800->59
'could Davout recruit, Berthier?'    q=True   inert
'are they going to retreat, Berthier'   q=False  whole army falls back
'are they going to retreat, Berthier?'  q=True   inert
```

The top-of-function arm catches them (the line ends in `?` and
`_ADDRESSED_LINE_RE` does not match a lead-first sentence). The harm is the
**unpunctuated** comma form only. That narrows the population — though not the
design failure, since the entire reason arms (c)/(d) exist is that players
leave the `?` off.

---

## 5. Player-reachable: **YES, confirmed independently.**

`p5_client_gate.py` is my own port of `main.gd::_send_command` →
`_redirect_diplomatic_command` (main.gd:1666–2120), constants and all,
including `_contains_word`'s boundary rule.

```
'can Ney attack Mack, Berthier'          redirected=False  no cabinet family -> SENT
'is Swabia defended, Berthier'           redirected=False  -> SENT
'are they going to retreat, Berthier'    redirected=False  -> SENT
… all ten SENT …
'declare war on Austria'                 redirected=True   cabinet redirect (NOT sent)   <- control
'Talleyrand, propose peace to Prussia'   redirected=True   cabinet redirect (NOT sent)   <- control
```

Neither `_is_advisory_question` (WH-words only — `can`/`is`/`may`/`has`/`does`
are deliberately excluded, and main.gd's own comment explains why) nor
`_matches_cabinet_family` claims them, so the raw string reaches
`POST /command`. "Berthier" is not in `DIPLO_ADDRESS_NAMES`.

Worth recording: main.gd already carries this exact lesson in the diplomatic
domain — *"a modal opens an ORDER at least as often as a question … 'should we
declare war on Prussia' (no question mark) all parse at confidence 0.95 and
SEND"*. The client learned it; the backend's military path is still learning
it.

---

## 6. Would the prescribed fix ship a regression? **One shape is safe and
incomplete; the other reds two pins.**

`p3_fixes.py` (guard-level + full golden corpus) and `p4_e2e_fix.py`
(end-to-end through the real parser). Baseline: corpus **688/688**, all four
`test_arm_c_stands_down_before_a_trailing_clause` assertions green, all 8
conditional pins green, 10/10 filed cases executing.

**FIX-A — "narrow the stand-down to a trailing clause that contains a verb"
(the lens's first shape): SAFE, but it does not close its own finding.**

```
closes 7 / 10 filed cases
corpus 688/688       pins: all green      conditional pins 8/8 green
STILL EXECUTES: 'can Ney attack Mack, do you think'
STILL EXECUTES: 'can Ney attack Mack, or should Davout'
STILL EXECUTES: 'is Swabia defended, and is Vienna'
```

Three of the lens's own seven survive it, because `do`, `should` and `is` are
verbs. A tag question and a coordinated question both carry one.

(Corpus note: `run_corpus()` reports **688** evaluations over **449** entries
on disk. `BUG_FIXES.md`'s CX-1a cell says "0 of 447 rows" — two short, and
stale rather than wrong in kind. Recorded so it is not re-derived as a
discrepancy later.)

**FIX-C — delete the stand-down (the maximal reading): closes 10/10 and reds
two pins.**

```
closes 10 / 10 filed cases
corpus 688/688   (the corpus is blind to this — worth knowing)
PIN RED: test_arm_c_stands_down_before_a_trailing_clause
         'is Mack advancing, fortify'    want=False got=True
         'should Mack advance, fortify'  want=False got=True
PIN RED: test_parse_negation::test_conditional_orders_are_refused_not_executed_now
         'Ney, should Mack advance, fortify'
           was: success=False refusal='conditional'
           now: success=True  refusal=None  action='help'  question=True
```

**The sentence it breaks is `Ney, should Mack advance, fortify`** — the
inverted conditional, which stops reaching the condition guard's refusal and
becomes a shrug instead.

The lens's second shape — "scope it to the ADDRESSED form" — is the closer
idea, since the pinned case is addressed and the filed cases are not; but
neither prescription names the real discriminator, which the measurements
point at directly: **the stand-down should ask whether the tail is an ORDER
the addressee could execute** (`fortify`, `attack Mack`), not whether it
contains a verb and not merely whether the line is addressed. A builder who
follows the filed `fix_shape` verbatim ships a fix that leaves three of the
seven filed sentences fighting.

---

## 7. Severity

**P2 — held, with the attribution corrected.** The harm is real, reachable,
and not undoable (an AP, a battle with thousands of casualties, a whole-army
retreat, 741 gold). It is not P1: the `?` form is correctly inert, the bare
form — the commoner phrasing, and the one the row was built for — is now
right, and the comma form is no worse than the game shipped for a year before
row CX.

## 8. What the row's record should say

- Strike `shipped_by_this_row: true`. This is **pre-existing**, and the
  pre-row arm proves it on the row's own twelve sentences.
- Re-title away from "vocative": the defeating token is `,\s*\S`, measured
  identical for `, please` and `, roughly`.
- Carry the two amplifications the row *is* answerable for: 0 → 55 pairs
  where the game contradicts itself, and the Predictor's 11-of-13 identical
  lines.
- Carry the harm number **55 of 206 flips (~39 grammatical)**, not 7 and not
  206, and carry the `?` caveat.
- Do not build the filed `fix_shape` as written.
