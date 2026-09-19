# VERDICT:CX-CLAIM-6 — NARROWED

**Filed by lens `claims` as P3.** Verdict: **NARROWED — the defect is real, is
wider than filed in one direction and narrower in two others, and the claim's own
replacement figure is mis-derived.**

Tree: `master f52df77f` (task text said `727cf88a`; `f52df77f` is one docs commit
on top and touches none of the four lines at issue — verified by blame below).
Read-only throughout. No git mutation. Probes in `probes/`.

---

## 1. What I ran (not what I was handed)

I did not take the claim's `probes/p01` figures. I rebuilt the census from the
archive.

**`probes/p_census.py` — the denominator.** All 32 files in
`tools/playtest_scripts/`, every string under `turns` → **1,456 commands**.
`typed_road.json` is **40** of them and `git log --diff-filter=A` dates it to
**`704df816`, row CX itself**. 1,456 − 40 = **1,416 exactly** — so the row's
denominator is the 31 pre-CX scripts, and my census is the same census.

**`probes/p_verbhead.py` — the instrument check.** Verb head after stripping the
addressee. It reproduces the row's own weighted table to ≤0.2pp on every row,
which is what licenses everything below:

| memo/spec | my measurement |
|---|---|
| fortify + unfortify 15.3% | 15.32% |
| move + march 14.2% | 14.12% |
| status 14.1% | 14.12% |
| drill 6.6% | 6.57% |
| assess 3.7% | 3.67% |
| **recruit 3.2%** | **3.18%** |
| **build 2.8%** | **2.82%** |
| hold 1.9% | 1.91% |

**`probes/p_rowmap.py` — the actual question.** Every one of the 1,416 commands
mapped onto a row of the memo's own 38-intent verdict sheet (`memo:114–151`;
CLICK WINS = rows 3,12,13,14,15,16,17,18,19,22,25,26,27,28,29,30,31,32,33,35,36,37).

```
CLICK WINS rows (unambiguous):        252   17.80%
PARITY rows:                          556   39.27%
TYPED WINS rows:                      235   16.60%
attack — row 2 TYPED *or* row 3 CLICK: 227   16.03%   (adjacency is not in the text)
no row / undecidable:                 146   10.31%
CLICK floor  (no attack counted):           17.80%
CLICK ceiling(every attack co-located):     33.83%
```

**`probes/p_build_improve.py`** enumerates the two buckets that decide the shape.

---

## 2. Does it reproduce? — YES for the core, on my own arithmetic

`docs/SYSTEMS_REFERENCE.md:5915` (verbatim, `awk`-addressed):

> **Measured: 38 intents, TYPED 9 / CLICK 22 / PARITY 7 — and the 22 click wins
> are ~6% of issued commands.**

Under its literal reading — *the set of 22 CLICK WINS rows accounts for ~6% of
issued commands* — that is **false by at least 3×**: the floor is **252 / 1,416 =
17.80%**, and the ceiling is 33.83%.

The claim's strongest argument is its internal-contradiction one, and it holds on
my numbers. The memo's own weighted table **two lines above the sentence** prints
`| propose / invest / declare / mission | ~7% | click-only |`. I measure that
bucket at propose 26 + invest 19 + declare 17 + mission 42 = **104 / 1,416 =
7.34%** — one click-only bucket, by itself, larger than the figure said to cover
all twenty-two rows.

---

## 3. Four corrections — why NARROWED and not CONFIRMED

### (a) The two cited sites are not the same sentence

The title says *"the false compression is the version in SYSTEMS_REFERENCE **and
STATUS**."* They differ, and it matters:

* `SYSTEMS_REFERENCE.md:5915` — **bare**. No scope clause. This one is simply wrong.
* `STATUS.md:19-20` — *"the 22 click wins are **~6% of issued commands**, **because
  only recruit and build are per-turn routine**."* The scope is named **in the same
  sentence**. It is loose ("are ~6%" where it means "of which the routine part is
  ~6%"), but a reader is told exactly which two verbs the 6% is.

One bare site, one scoped-but-loose site. The claim lumps them.

### (b) The claim's replacement figure is mis-derived — its magnitude is luck

The claim asserts *"the verbs whose 38-intent row is CLICK WINS total 247."* Three
of its eighteen named verbs **have no row in the 38-intent sheet at all**:

| verb | count | reality |
|---|---:|---|
| `guarantee` | 10 | `guarantee_nation`, a D5 instrument — no row |
| `release` | 3 | `release_vassal` — no row |
| `sponsor` | 3 | `sponsor_design` — no row |
| (`buy off …`) | 3 | 3 of the 16 `buy` are `buy off Britain's design` — no row |

= **16 commands with no row**, counted as CLICK WINS rows.

And it **omits the largest click-only family in the corpus** — row 28 *"Send an
envoy / mission"*, CLICK WINS — sole road: **42 × `improve relations with <court>`
= 2.97%**, nearly half the disputed 6% on its own.

The errors roughly cancel, which is why the claim lands near the truth by accident.
My strict row-mapped figure is **252 = 17.80%** (250 = 17.66% if the two absurdist
`send somebody, anybody, to take Munich` strings are excluded) — *higher* than the
claim's 247.

### (c) A finding the claim MISSED, and it kills the claim's own premise

The claim opens: *"The memo (:173) and spec (:118) state it correctly."* **They do
not.** Of the 40 `build` commands, **21 are the literal string `build ships`** —
and the memo's own **row 34, "Build ships", is graded PARITY**, not CLICK WINS.
Only 19 are rows 14/15.

```
build ships (row 34, PARITY):               21  = 1.48%
build structures (rows 14/15, CLICK WINS):  19  = 1.34%
recruit (row 12, CLICK WINS):               45  = 3.18%
=> "recruit (3.2%) and build (2.8%), 6.0% together"  RECOMPUTES TO  4.52%
```

So all **four** sites carry a wrong number: two by compression
(`SYSREF:5915`, `STATUS:19`) and two by arithmetic (`memo:173`, `spec:118`). The
defect is wider than filed — but not in the direction the claim argued.

### (d) The row-3 point is right in direction, wrong in kind

*"row 3 (attack a co-located enemy) is a CLICK WIN inside the 14.34% attack share"*
— true that the 6% figure does not touch attacks. But row 2 (adjacent, **TYPED
WINS**) and row 3 (co-located, **CLICK WINS**) are the **same typed string**
`Ney, attack Mack`; adjacency lives on the board, not in the archive. The 227-command
attack bucket (16.03%) **cannot be split from the scripts**. It is a floor/ceiling
band, not a number, and the claim states it as though it were measurable.

---

## 4. Severity — HELD at P3, and it was close to P4

**Keeps it at P3:** `SYSTEMS_REFERENCE.md` §50 is the *rules* file a future session
reads as authoritative; this project already files exactly this shape (PR-D4 *"a
documented table does not reproduce"*; IQ1-2's retired `457×`, now guarded by a
correction-marker census in `tests/test_iq1_iq1_3_the_granary.py:873`); and the
error is in **four** files, not the two filed.

**Caps it at P3:** the ruling the sentence sits under does not rest on the figure —
`spec:130` says so in writing: *"its load-bearing fact is that the click road cannot
START a march. **Nothing else in it depends on a figure that can drift.**"* And every
error runs in the direction that makes the row's conclusion **stronger** (less routine
click-win volume, more click-only breadth), so no reader is steered to a wrong
decision — only to a wrong number.

---

## 5. Player-reachable — **NO** (claim agrees, and it is right)

Four markdown files. Zero backend, zero `.gd`, zero client surface. Nothing a player
can type or click reaches it. `main.gd`'s 114-form diplomatic redirect is irrelevant here.

## 6. Shipped by row CX — **YES**, confirmed by blame

```
docs/SYSTEMS_REFERENCE.md:5915  ->  704df816  (row CX)
docs/STATUS.md:19               ->  704df816  (row CX)
docs/COMMAND_EXPERIENCE_SPEC.md:118 -> b4a27a154 (row CX)
docs/audits/CX_...:173          ->  704df816  (row CX)
```

Not pre-existing — §50, the STATUS entry and the memo were all created by row CX.

## 7. Would the suggested fix ship a regression?

**No test regression risk.** `grep -rn` over `tests/` and `tools/` for
`"click wins" | "38 intent" | "6.0% of issued" | "TYPED 9" | "PARITY 7"` returns
**nothing**. The only test that reads `docs/STATUS.md`
(`test_iq1_iq1_3_the_granary.py:879`) is scoped to the retired `457` figure.

**But the claim's implied fix — substituting 17.4% — would ship a worse record**,
for three reasons: 17.44% is derived from a verb set that includes three rowless
verbs and omits the mission family; it would leave the **4.52 vs 6.00** arithmetic
error standing in the memo and spec, so the four files would still disagree; and a
single percentage cannot honestly represent a quantity whose attack bucket is a
16.03% band the archive cannot split.

**The honest fix is three parts:**
1. `memo:173` + `spec:118` — **6.0% → 4.52%**, naming `build ships` as row 34 PARITY
   (19 of 40 `build` commands are structures).
2. `SYSREF:5915` — say what it means: *of the 22, only recruit and build recur every
   turn — together ~4.5% of issued commands; the 22 rows together are ~18%.*
   `STATUS:19` already carries its scope clause and needs only the 6% → ~4.5% number.
3. If ~18% is published at all, publish it as a **floor** with the 16.03% attack band
   named — and follow the correction-marker idiom the suite already enforces for `457×`.
