# VERDICT:CX-CLAIM-8 — CONFIRMED (arithmetic exact), and the claim understates its own scope by 5.7x

**Refuter pass, read-only, September 19 2026, at master `727cf88a` … `f52df77f` (clean).**
Default verdict was REFUTED. Every figure below is the output of a probe I ran myself,
under `LLM_MODE=mock`, no key, no network. Nothing was modified; no git-mutating
command was run.

---

## 0. VERDICT IN ONE LINE

**CONFIRMED.** The corpus is 447 at `f7008582`/`b4a27a15` and **449** from CX-2
(`5fc3d5c8`) through HEAD; the memo/spec still say 447. **But the claim is filed too
small in three ways and too large in one.** It is not "three places in the memo" — it
is **17 CX-authored live occurrences across six files**, two of which are **not
documentation** (a production code comment and a test docstring), and **two of which
the row's own final commit re-typed and left**. Against that, **severity P4 is right
and should not be raised**: no conclusion moves by more than 0.11 percentage points,
and the one substantive claim underneath ("the corpus moves 0 rows") I re-measured at
449 and it still holds.

---

## 1. THE ARITHMETIC REPRODUCES EXACTLY — every digit

`probes/p8_world_dist.py`, run over `git show <sha>:tests/data/parser_golden_corpus.json`
for all eight commits from `f7008582` to `f52df77f`:

```
f7008582  entries=447      b4a27a15  entries=447   <- CX-1, still 447
5fc3d5c8  entries=449   <- CX-2 adds two           2c3535b5  449
704df816  entries=449   <- THE MEMO IS WRITTEN HERE c73749c3  449
727cf88a  entries=449                              f52df77f  449
```

The world split, and the `692` the memo divides by:

```
pre-CX f7008582 : worlds {'1805': 147, 'any': 245, 'legacy': 55}
                  'any' counted twice  ->  245*2 + 55 + 147 = 692   <- exactly the memo's denominator
                  live_only=4   mock_only=49
HEAD   727cf88a : worlds {'1805': 147, 'any': 245, 'legacy': 57}
                  245*2 + 57 + 147 = 694
                  live_only=4   mock_only=49
```

So: **692 IS the 447 arithmetic** (claimed, and true — I derived it independently rather
than accepting it); at HEAD the same computation gives **694**. `live_only = 4` and
`mock_only = 49` reproduce **exactly, and are genuinely unchanged** by the two new rows.

The two added ids are exactly the ones claimed (`probes/p8b_distinct.py`, set difference
of ids between the two corpora):

```
ADDED   ['i-question-still-help-legacy', 'parseneg-can-i-attack-mack-legacy']
REMOVED []
```

and CX-2's own commit message says so in words — *"`parseneg-can-i-attack-mack` and
`i-question-still-help` (scoped to 1805, legacy twins added)"*. Both new rows are
`world: legacy`, both `expected.action: "help"`.

---

## 2. ⛔ WIDER THAN FILED — 17 occurrences in SIX files, not three in the memo

Every live `447` in the tree, blamed line by line (`git blame -L <n>,<n>`), excluding
`docs/archive/`, `docs/audits/cx_recon_2026_09_19/` and the unrelated hits
(`447 battles`, `15,447/3`, `:446-449` line refs):

| file | lines | n | written at |
|---|---|---|---|
| `docs/COMMAND_EXPERIENCE_SPEC.md` | 87, 228, 518, 519 | 4 | **`b4a27a15` (CX-1)** |
| `docs/COMMAND_EXPERIENCE_SPEC.md` | 512, 639 | 2 | `704df816` |
| `docs/audits/CX_THE_HAND_ON_THE_KEYBOARD_2026_09_19.md` | 89, 249, 255, 256, 366 | **5** | `704df816` |
| `docs/BUG_FIXES.md` | 12896 (CX-X2) | 1 | `704df816` |
| `docs/BUG_FIXES.md` | 12869 (CX-1a) | 1 | **`f52df77f`** |
| `docs/STATUS.md` | 118 (CX-X2) | 1 | `704df816` |
| **`backend/ai/clause_guards.py`** | **606** | **1** | **`b4a27a15` (CX-1)** |
| **`tests/test_cx1_a_question_never_orders.py`** | **371** | **1** | **`b4a27a15` (CX-1)** |
| **`tests/test_cx1_a_question_never_orders.py`** | **73** | **1** | **`f52df77f`** |
| | | **17** | |

The memo alone has **five**, not three. And three findings the claim does not make:

### (a) Two of the seventeen are NOT documentation

`backend/ai/clause_guards.py:606` — a **production source comment**, present tense,
sitting immediately above the shipped lever:

> `# all begin real phrasings the game already accepts. Measured against all 447`
> `# corpus entries, the four-word rule moves 0 rows.`
> `A_QUESTION_NEVER_ORDERS = True`

and `tests/test_cx1_a_question_never_orders.py:371`, the docstring of the pin that is
*about the corpus size*:

> `"""447 golden-corpus entries over both worlds, under BOTH arms of the lever."""`

This is the **same class as CX-CLAIM-9** (two CX-written comments stating 12,717 in the
present tense). Filed as a docs-staleness row, this one reads like a citation nit; it is
in fact a stale figure inside shipped source and inside a test's own statement of what it
measures. If CX-CLAIM-9 is worth filing, these two belong on the same row.

### (b) ⛔ The row's LAST commit re-typed two of them and left the 447 standing

`f52df77f` is *"docs(cx): correct the row's own headline figure — it understated its fix
by 4x"* — a deliberate figure-correction pass, made on a 449-entry tree. Its diff
(`git show f52df77f -- docs/BUG_FIXES.md tests/test_cx1_a_question_never_orders.py`)
**rewrites the exact sentences that carry the stale number**:

```
-  ...sweep goes 30 executing -> 9...  The golden corpus moves 0 of 447 rows under either arm
+  ...grid run under BOTH arms goes 121 executing -> 9... The golden corpus moves 0 of 447 rows under either arm
```

```
-the slice the same sweep executed 30. The golden corpus moves **0 of 447
-entries** under either arm of the lever (`TestTheCorpusDoesNotMove`).
+The golden corpus moves **0 of 447 entries** under either arm
+(`TestTheCorpusDoesNotMove`).
```

So this is **not** a CX-2 oversight nobody revisited. The author touched the sentence,
corrected a *different* number inside it, and carried the stale one through — which is
the strongest evidence the claim has and which the claim does not use.

### (c) The provenance is SPLIT, and 6 of the 17 were TRUE when written

`git blame` puts **6** occurrences at `b4a27a15` (CX-1), when the corpus *was* 447 —
including both non-documentation sites. Those are not "the row published a wrong
number"; they are **"CX-2 moved a denominator and did not sweep its own predecessor."**
The other **11** (nine at `704df816`, two at `f52df77f`) were false the moment they were
typed. The claim's flat `shipped_by_this_row: true` is right, but the interesting half —
that the row invalidated its own CX-1 prose two commits later and then walked past it
twice — is not stated.

---

## 3. NARROWED — severity P4 is correct and must not be raised

### (a) No published conclusion moves

| figure | on 447 | on 449 | delta |
|---|---|---|---|
| `111` client-blocked | 24.83% | 24.72% | **−0.11 pp** |
| `4` live_only | 0.89% | 0.89% | **0.00 pp** |
| `49` mock_only | 10.96% | 10.91% | −0.05 pp |
| `45 / 692` escalating | 6.50% | 6.48% (÷694) | −0.02 pp |

And the numerator `111` is almost certainly unmoved too: the two added rows carry the
**identical utterance text** as rows already in the corpus (`can I attack Mack?` /
`Can I attack Mack?`), and neither contains any member of `DIPLO_FAMILY_KEYWORDS`
(measured: `hits = []` for both). Distinct utterances are **437 on both sides** — the
two additions are world-scope twins, not new sentences.

### (b) ⛔ The one claim that COULD have gone stale in substance did not — I measured it

*"The golden corpus moves 0 of 447 entries under either arm"* is the biggest of the
seventeen, and it was the one at genuine risk: **the two rows CX-2 added are the two
most question-shaped rows in the whole corpus** (`can I attack Mack?`), i.e. precisely
the sentences CX-1's `A_QUESTION_NEVER_ORDERS` lever governs. If any rows were going to
move, these were them.

`TestTheCorpusDoesNotMove` reads the corpus **dynamically** (`load_corpus()["entries"]`,
`live_only` filtered) — it hardcodes nothing — so it already covers them. My own
instrumented re-run of its walk, independently of the committed test:

```
corpus entries total        = 449
walked (non-live_only)      = 445
(entry, world) rows walked  = 688
all-entries x worlds        = 694
two CX-2 rows in the walk:  True

A_QUESTION_NEVER_ORDERS=False: failures=0  -> []      CX-2 rows among them: []
A_QUESTION_NEVER_ORDERS=True : failures=0  -> []      CX-2 rows among them: []
```

and the committed pin itself is green at HEAD:
`pytest tests/test_cx1_a_question_never_orders.py::TestTheCorpusDoesNotMove -p no:randomly` → **1 passed**.

So: denominator stale, **conclusion intact, and verified intact rather than assumed.**
That is what caps this at P4. It is not P3 — nothing is made uncitable, no ruling turns
on it, and no reader is misled about a behaviour.

### (c) Not player-reachable — confirmed, as claimed

All seventeen sites are prose: six `.md` files, one source comment, one test docstring.
None is rendered by the client, none is a string the game prints, and no `main.gd`
route touches any of them. `player_reachable: false` stands.

---

## 4. ATTACKING THE SUGGESTED FIX — a naive 447→449 would ship a NEW wrong number

It would red **no pin**: I grepped for any committed assertion on the corpus size
(`len(entries) ==`, `== 44x`, `== 45x`, `ENTRY_COUNT`, `CORPUS_SIZE` across `tests/` and
`backend/ai/parser_eval.py`) — **there is none**. Nothing in the suite asserts how many
entries the corpus holds.

But a find-replace would break two sentences, measured:

1. **`test_cx1_a_question_never_orders.py:371`, `:73`, `COMMAND_EXPERIENCE_SPEC.md:228`
   and `BUG_FIXES.md:12869`** all describe `TestTheCorpusDoesNotMove`, which **excludes
   `live_only` and walks 445 entries / 688 (entry, world) rows** — so **neither 447 nor
   449 is the right number for that claim.** Patching 447→449 converts a figure that was
   true-when-written into one that is wrong in a second, newer way. The honest edit names
   the unit: *"0 of 445 walked entries / 688 entry-world rows"*.
2. **`45 / 692` → `45 / 694`** would publish a ratio whose **numerator was never measured
   on the 449 tree**. The numerator is a count over rows, and two rows were added; you
   cannot fix that by moving the denominator. That seam belongs to CX-CLAIM-1 (which
   argues the numerator is 50 anyway) and should be **re-run, not re-divided**.

**Recommended fix, in order:** (i) fix the two non-doc sites first — `clause_guards.py:606`
and the test docstring — since they are shipped source; (ii) at each remaining site state
the *unit* (449 entries total / 445 walked / 688 walked rows / 694 entry-world pairs),
because this row has already proved that a bare count with no unit goes stale silently;
(iii) re-measure, never re-divide, anywhere the numerator is itself a count over rows.

---

## 5. METHOD NOTE (against myself)

My first extraction of `DIPLO_FAMILY_KEYWORDS` returned **115** members and I nearly
published it as a drive-by against CX-CLAIM-12's "114 ✓". Re-run excluding comment lines
it is **114** — one of the list's own explanatory comments contains a quoted phrase.
CX-CLAIM-12's figure is right; my probe was wrong. Recorded because this review exists to
catch exactly that, and it applies to me too.
