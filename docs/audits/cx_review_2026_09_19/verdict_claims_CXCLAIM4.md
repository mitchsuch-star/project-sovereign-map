# VERDICT: CX-CLAIM-4 — **REFUTED as filed (stale); NARROWED to a smaller, different residue**

> *"The '684-case sweep, 30 executing → 9' does not exist: the committed grid is 114
> cases, the before-figure is 49-51, and the row publishes two different sizes"* — P3,
> filed by lens `claims`.

**Verdict in one line:** the 684-case grid **does exist, is committed, and has an
archive**; the claim's own 49–51 is the **one-lever** figure measured by a probe that
flips one of the row's two levers; the Soult sub-point is **pre-existing CR-6
behaviour** that bare `attack Mack` shows identically on the pre-row tree. What
survives is **smaller, P4, and was found by re-running the probe rather than by the
claim**: the BEFORE arm is non-deterministic, the grid contains six duplicated cases,
and the row committed **two copies of the same measurement that disagree**.

---

## 0. First, a fact the claim could not have known

**HEAD is `f52df77f`, not `727cf88a`.** The task text states the tree is at
`727cf88a` and clean. It is not:

```
f52df77f docs(cx): correct the row's own headline figure — it understated its fix by 4x
727cf88a fix(cx6): the object pronoun is not a subject …
```

`f52df77f` landed **13:33:45**. `claims.md` was written **13:52**. The correction
commit is *about this exact claim's subject*: it commits the 684-case probe, commits
its output as an archive, re-measures under both arms, and corrects the figure in the
spec, the memo, BUG_FIXES, STATUS **and the test docstring** (which is where the rogue
"677" lived).

So the claim was **true when it was written against `727cf88a`** and is **stale at
HEAD**. That is not the lens's fault; it is a fact the verdict has to carry.

---

## 1. Reproduction — what I actually ran

All probes under `probes/refute4/`, `LLM_MODE=mock`, shipped 1805 board, fresh world +
`TestClient` per case. I copied the committed probe rather than running it in place,
because it writes to the tracked file `tools/sweep_both_arms.out.txt` and this pass is
read-only.

### 1a. Does the 684-case grid exist? — **YES, at HEAD**

`tools/_cx_sweep_both_arms.py`, committed by `f52df77f`, with its output archived at
`docs/audits/cx_recon_2026_09_19/sweep_both_arms_measurement.txt`.

```
probes/refute4/r1_684_grid.py
GRID SIZE: 36 leads x 18 verbs = 648 + 36 extra = 684 cases (unique: 678)
```

684 exactly. The claim's *"does not exist"* is correct at `727cf88a`
(`git ls-tree 727cf88a tools/` holds only `_sweep_cx.json` and
`cx3_completer_screenshot.gd`) and **wrong at HEAD**.

### 1b. Does `121 → 9` reproduce? — **the 9 does, exactly; the 121 does not, quite**

Three full runs of the committed grid under both arms:

```
--- run 1 ---  BEFORE 119 of 684   AFTER 9 of 684 (controls 9, defects 0)
--- run 2 ---  BEFORE 120 of 684   AFTER 9 of 684 (controls 9, defects 0)
--- run 3 ---  BEFORE 121 of 684   AFTER 9 of 684 (controls 9, defects 0)

AFTER  union 9 / intersection 9  -> UNSTABLE 0
AFTER non-control (any run): []
BEFORE union 117 / intersection 113 -> UNSTABLE 4
  unstable: ['can Ney retreat', 'does Ney retreat',
             'how about Ney fortify', 'what about Ney fortify']
```

**The load-bearing half of the row's claim is exact and stable.** `AFTER = 9, all nine
the intended controls, zero defects` reproduced **3 of 3** on the 684 grid and **3 of
3** on the 114 grid (§1d). That is the safety statement, and it holds.

**The BEFORE half is a single draw from a range.** `121` is the *top* of what I
measured (119/120/121), not a fixed number.

### 1c. The row committed two copies of one measurement, and they disagree

```
$ diff docs/audits/cx_recon_2026_09_19/sweep_both_arms_measurement.txt \
       tools/sweep_both_arms.out.txt
< === BEFORE — both row-CX levers OFF — 121 of 684 executed ===
> === BEFORE — both row-CX levers OFF — 120 of 684 executed ===
>   DEFECT  'can Ney retreat'
<   DEFECT  'did Ney fortify'
<   DEFECT  'may Ney fortify'
< executed BEFORE  : 121
> executed BEFORE  : 120
```

The archive committed to satisfy the repo's own IQ-8 rule — *a figure with no archive
is uncitable* — **does not reproduce from its own probe**, and its sibling copy in the
same commit already says 120.

### 1d. Is the claim's "49–51" real? — **yes, but it is the ONE-LEVER figure**

This is the claim's load-bearing error and it is mechanical. Its own
`probes/p10_sweep.py` does:

```python
for arm in (True, False):
    CG.A_QUESTION_NEVER_ORDERS = arm
```

— and **never touches `CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA`**, which stays at
its shipped `True`. The row publishes *"run under BOTH arms of the two levers this row
adds"*. Same committed 114-case grid, three lever configurations, three runs each:

```
probes/refute4/r3_one_lever.py
                                                            run1  run2  run3
BOTH levers OFF   (what the ROW publishes as "before")        67    67    68
QUESTION lever OFF only (what the CLAIM's p10 measured)       50    49    50
BOTH levers ON    (shipped)                                    9     9     9
```

The claim's 49–51 reproduces **precisely** — under one lever. Under the row's stated
two-lever configuration the same grid gives 67–68.

So the claim takes a **one-lever number from the 114-case pin**, sets it against a
**two-lever number from the 684-case grid**, and concludes the row's figure "does not
reproduce". That is the same two-different-grids error the claim accuses the row of,
with a lever mismatch on top.

### 1e. The Soult sub-point — **PRE-EXISTING, and not about those two sentences**

The claim's "⚠ second, smaller point" is that `do attack Mack` and `can you attack
Mack` commit Soult, a marshal the player never named. The behaviour is real. The
attribution is not.

```
probes/refute4/r4_soult.py  — HEAD
  'do attack Mack'          ap 4->3   muster names 'Soult'
  'can you attack Mack'     ap 4->3   muster names 'Soult'
  'attack Mack'             ap 4->3   muster names 'Soult'   <-- no lead, no name
  'Ney, attack Mack'        ap 4->3   muster names 'Ney'
```

Bare `attack Mack` — no question lead, no emphatic `do`, no second person, nothing row
CX touched — resolves to Soult identically. This is CR-6's bare-attack resolution
(*resolve-and-rewrite at the dispatch seam*), which is shipped design.

Confirmed by date, on the pre-row tree (verified `b4a27a15^` by md5 of
`clause_guards.py`, `executor.py`, `parser.py`):

```
probes/refute4/r4_soult.py  — prerow_tree == b4a27a15^
  'do attack Mack'          ap 4->3   muster names 'Soult'
  'can you attack Mack'     ap 4->3   muster names 'Soult'
  'attack Mack'             ap 4->3   muster names 'Soult'
```

Identical, including the muster strings. **Row CX did not ship it**, and it is not a
property of the two controls named.

### 1f. The committed pin is green

```
tests/test_cx1_a_question_never_orders.py::TestTheSweep::test_only_the_controls_execute PASSED
```

---

## 2. The claim, assertion by assertion

| # | claim assertion | verdict |
|---|---|---|
| 1 | "a 684-case sweep does not exist" | **REFUTED at HEAD.** Committed probe + archive; I counted 684. True only at `727cf88a`. |
| 2 | "the committed grid is 114 cases" | **NARROWED.** 114 is `TestTheSweep`, a *different, smaller* pin. Nothing ever claimed it was the 684 grid. |
| 3 | "the before-figure is 49-51, not 30" | **REFUTED as a refutation.** 49–51 is the one-lever figure (reproduced: 50/49/50). Two-lever on the same grid is 67–68. |
| 4 | "the row publishes two different sizes (684 / 677)" | **TRUE at `727cf88a`, FIXED at HEAD** by `f52df77f`. (Piquant: 677 was nearly right for a number nobody was computing — the grid has **678 unique** cases.) |
| 5 | "the 30 does not reproduce" | **TRUE — and the row says so itself**, in four places, having self-caught it 19 minutes before the claim was filed. |
| 6 | "the 9, all nine controls, is good evidence" | **CONFIRMED.** 3/3 on the 684 grid, 3/3 on the 114 grid, zero non-controls in any run. |
| 7 | sub-point: two controls commit Soult | **PRE-EXISTING.** Bare `attack Mack` does it too, and all three are identical on `b4a27a15^`. |

---

## 3. What survives — and it is not what was filed

A **P4** measurement-hygiene residue, live at HEAD, found by re-running the probe:

1. **The BEFORE arm is non-deterministic** — 119/120/121 across three runs, four cases
   flipping (`can Ney retreat`, `does Ney retreat`, `how about Ney fortify`,
   `what about Ney fortify`). `121` is published as a fixed figure.
2. **The archive does not reproduce from its own probe** — the two copies committed in
   `f52df77f` say 121 and 120.
3. **The grid double-counts.** 684 cases, **678 unique**; six duplicates, of which five
   execute in BEFORE:
   ```
   x2 'can Ney attack Mack'   x2 'did Ney attack'      x2 'does Ney attack Mack'
   x2 'may Ney attack Mack'   x2 'why not attack Mack' x2 'would Davout hold Lorraine'

   archive BEFORE: 121 listed lines / 116 unique     AFTER: 9 / 9
   ```
   So the published **"112 defects to zero"** is really **≈107 distinct sentences**
   (116 − 9 controls), itself ±2 from the non-determinism. Having corrected an
   understatement of 4×, the row now overstates by ~5%.

**The AFTER figure is untouched by all three** — 9 lines, 9 unique, zero defects,
every run. The row's safety claim is sound; only its "how bad was it" number is soft.

---

## 4. Severity, reachability, ownership

* **Severity: P4**, not the filed P3. The defect is in a *published before-figure*, in
  a row whose load-bearing after-figure is exact and reproduces 3/3 on two grids.
* **Player-reachable: NO, by construction.** This is a number in `docs/` and a test
  docstring. Nothing here is a behaviour; there is no typed road and no client
  surface. (The Soult sub-point *is* player-reachable — and is pre-existing CR-6
  design, outside this row.)
* **Shipped by row CX: YES for the residue** — the duplicated grid, the
  non-deterministic figure and the two disagreeing archives all arrived in `f52df77f`,
  which is part of row CX. **NO for the claim as filed**, which is stale.

---

## 5. Would the claim's suggested fix ship a regression?

> *"publish **114** (or commit the 684-case probe as the archive the IQ-8 table rule
> requires), and re-measure or drop the '30'."*

* **"Publish 114" would make the record worse.** It would replace a correct grid size
  with the size of a *different* pin. It reds no test — and that is precisely the
  hazard: the docs would become less true with the suite green. The sentence it breaks
  is the row's own honest one, *"ONE 684-case grid … run under BOTH arms"*, which is
  the thing that makes the before/after comparable at all.
* **"Commit the probe"** — already done, by `f52df77f`.
* **"Re-measure or drop the 30"** — already done, by `f52df77f`.

So of the three limbs, two are landed and the third would introduce an error. **Do not
build this claim as filed.**

**The fix the residue actually wants**, if anyone takes it (P4, optional):
dedupe the case list to its 678 unique entries; publish the BEFORE as a distinct-count
with its range (`≈107 ± 2 distinct sentences → 0`) rather than a bare `121`/`112`,
since the arm is measurably non-deterministic; and reconcile or delete the second
archive copy so one number has one archive.

---

## 6. Method note

The claim was reproducible in every particular *and still wrong in its conclusion*,
because it compared two numbers taken under different lever settings on different
grids. The lens ran a real probe and got a real number; what it did not do was check
that its probe was in the configuration the row's sentence describes. Reading
`p10_sweep.py` next to the row's own words — *"both arms of the two levers"* — is what
settled it, and took one grep.
