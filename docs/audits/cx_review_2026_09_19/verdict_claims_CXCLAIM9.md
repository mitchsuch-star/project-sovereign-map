# VERDICT: CX-CLAIM-9 — **NARROWED**

**Refuter pass, September 19 2026, at master `727cf88a` (clean, verified
`git status --porcelain` empty). Read-only: nothing under `backend/`,
`godot-client/`, `tests/`, `docs/` or `tools/` was modified; no git-mutating
command was run.** Every figure below is the output of a probe I wrote and ran
myself, on the shipped 126-province 1805 board, `LLM_MODE=mock`, no key, no
network. Probes under `…/scratchpad/cx_review/probes/`:

| probe | what it does |
|---|---|
| `v9c.py` | drives `CommandParser` → `CommandExecutor` exactly as `backend.main` does, on the real `from_scenario` 1805 world; renders `help` and four question roads |
| `v9_tree.py` | the same render inside a tree extracted by `git archive` at an arbitrary SHA |
| `v9d_variance.py` | re-renders across every reachable `get_mission_skill_multiplier` arm, both levers, and a diplomat-less world |
| `v9e_history.py` | extracts the `help_text` literal from `meta_executor.py` at five SHAs via `git show` and measures it |

Control trees extracted read-only with `git archive` into
`…/scratchpad/cx_review/tree_f7008582/` (pre-row) and `tree_5fc3d5c8/`
(post-CX-2, pre-CX-3).

---

## 1. WHAT REPRODUCES — EXACTLY

| assertion | my measurement | verdict |
|---|---|---|
| rendered `help` at HEAD on the 1805 board | **12,720 chars / 236 lines** (`v9c.py`) | ✓ EXACT |
| needles `status` / `where is` / `who holds` / `how many men` | **0 / 0 / 0 / 0** | ✓ EXACT |
| `why did that fail` → the router | **exactly 370 chars** | ✓ EXACT |
| 12,717 is the correct PRE-CX-3 figure | `5fc3d5c8` → **12,717 / 236** (`v9_tree.py`) | ✓ EXACT |
| the +3 is CX-3's `Ulm` → `Swabia` | bisected: `f7008582` **12,717**, `5fc3d5c8` **12,717**, HEAD **12,720**; the ONLY `meta_executor.py` change between `5fc3d5c8` and HEAD is that one line (`git log f7008582..HEAD -- backend/commands/meta_executor.py` = CX-2 and CX-3; CX-2's 90-line diff adds `_route_unanswered_question` and the early return and does **not** touch the literal) | ✓ EXACT, and now proven by experiment rather than by diff-reading |

**So the claim's headline number is right, and its causal story is right.** That
half stands.

---

## 2. WHY IT IS NARROWED — FOUR CORRECTIONS

### (a) The census is wrong in BOTH directions — it is four, not two

> *"two comments WRITTEN BY THIS ROW state 12,717 in the present tense"*

`grep -rn --include=*.py --include=*.gd --include=*.json "12,717\|12717"` over
`backend/ tests/ tools/ godot-client/…/scripts/`:

```
HEAD 727cf88a — 9 sites, of which FOUR are production code:
  backend/ai/counsel.py:19          "The COMMAND REFERENCE — 12,717 characters…"
  backend/ai/counsel.py:310         "…returned the 12,717-character COMMAND REFERENCE"
  backend/ai/llm_client.py:1820     "…instead of printing a 12,717-character manual"
  backend/ai/question_desk.py:394   "…returned the SAME 12,717-character COMMAND REFERENCE"
  + tests/data/parser_golden_corpus.json:243, tests/test_cx2_…:15, :161,
    tests/test_fa_slice7_…:649, tests/test_napoleon_np1_hand.py:265

pre-row f7008582 — 0 sites.
```

The claim **missed `llm_client.py:1820` and `counsel.py:310`**. It is the larger
miss of the two, because `llm_client.py:1820` is one of only two genuinely
present-tense sites — see (b).

### (b) One of the two it DID name is not stale

`question_desk.py:394` reads, verbatim:

> *"Every one of the ten **returned** the SAME 12,717-character COMMAND REFERENCE"*

That is **past tense**, describing the pre-CX-2 recon measurement, which was
accurate — I measured 12,717 at `5fc3d5c8` myself. Same for `counsel.py:310`
(*"…returned the 12,717-character…"*). All five test/corpus sites are past tense
too (*"used to return 12,717 characters"*), and so are all four doc sites
(`SPEC:285`, `MEMO:211`, `MEMO:353`, `STATUS:61`).

**The genuinely stale, present-tense pair is `counsel.py:19` and
`llm_client.py:1820`** — and the claim named one of them and the wrong
partner.

### (c) The 9,630 is NOT an error, and it is NOT this row's

The claim files it under `shipped_by_this_row: true` and calls it "a dated
Sept-4 measurement, but the file now carries two different numbers for one
thing."

Measured (`v9e_history.py`, `git show <sha>:backend/commands/meta_executor.py`):

```
SHA                                       literal chars   literal lines
727cf88a  HEAD                                  11,636             217
5fc3d5c8  pre-CX-3                              11,633             217
f7008582  pre-row                               11,633             217
764d0ffc  FA slice 7 — the 9,630 comment lands   9,630             186
764d0ffc^ its parent                             9,630             186
```

`764d0ffc` is **2026-09-04**. IQ-4's `_missions_help_block` splice landed at
`4413c834`, **2026-09-14** — ten days later. So on September 4 the rendered
reply had no splice and **was exactly the literal: 9,630 characters.**
`question_desk.py:20` is a dated, attributed, and **numerically exact**
historical measurement. The line is pre-existing (present in the pre-row tree at
`question_desk.py:23`) and row CX neither wrote it nor broke it.

The file does not carry "two different numbers for one thing" — it carries two
correct measurements of the same document ten days apart. (The row's own recon
at `cx_recon_2026_09_19/question_desk.md:567` calls it *"stale"*; **that call is
itself the misreading**, and the row was right not to act on it.)

### (d) The title over-reaches its own body

> *"the row states three different figures for it"*

The row states exactly **one**: 12,717, at thirteen sites. **12,720** is the
reviewer's own measurement, not a row statement; **9,630** is inherited and
correct. The honest form is *"the row states one figure for it, in four
production comments, and made it stale in its own next commit."*

---

## 3. WHAT THE CLAIM MISSED — AND IT IS BIGGER THAN THE ±3

Attacking the sentence instead of the number. `backend/ai/counsel.py:19`,
verbatim:

> *"**The COMMAND REFERENCE** — 12,717 characters with no world-derived content
> at all (no `{` placeholder anywhere in its 216 lines)."*

That sentence measures **three different objects in one breath**, and two of the
three are wrong independently of the +3:

**(i) 1,084 of those characters ARE world-derived.** `_execute_help` splices
`_missions_help_block(world)` into the literal, and its figures come from
`mission_effect_magnitude(world, …)` → `get_mission_skill_multiplier(world)`.
Driven across every reachable arm (`v9d_variance.py`):

```
skill 10  -> x1.5    "+8 relation/turn"  "-4 relation between targets/turn"
skill 9/3/1 -> x1.0  "+5 relation/turn"  "-3 relation between targets/turn"
skill 5   -> x0.75   "+4 relation/turn"  "-2 relation between targets/turn"
no diplomat -> x0.75 (same block, 1,084 chars)
```

The block is board-derived at every arm. **"No world-derived content at all" is
false about the very number the sentence quotes.** It happens not to change the
LENGTH only because every figure is single-digit at every multiplier — an
accident, not a property.

**(ii) The "216 lines" is off by one.** The literal is **217 lines** at HEAD and
at every pre-row SHA (table in §2c). 236 is the rendered count. 216 is neither.

**(iii) The "no `{` placeholder" is not evidence of what it is offered as
evidence of.** The splice is done by `str.replace()` on a named anchor, so a
placeholder census is **structurally blind** to it — the exact shape of pin this
project has been burned by repeatedly (the row's own CX-3 census exists because
a parser-level census called a broken sentence green).

**(iv) The figure is not a stable property of the document at all.** Flipping
`diplomacy.COURT_FAVOUR_ACTIVE` moves the rendered reply **12,720 → 12,683**;
`meta_executor.MISSION_HELP_BLOCK = False` gives **11,636**. A number quoted in
four production comments is a rendered length contingent on two levers and a
world read.

**(v) It has no committed archive.** The recon
(`question_desk.md:259`) attributes 12,717 to `drive_desk.py`; `git ls-files`
has no such file. The memo itself cites the IQ-8 table rule — *an un-archived
figure is UNCITABLE* — and then puts that figure into four production comments.
**That is the actual root**: not "the comment is three characters stale", but
"a rendered, lever-dependent, un-archived length was written into production
comments as if it were a property of a source file."

---

## 4. THE OTHER AXES

**Severity — P4 CONFIRMED, and generously so.** No player surface quotes the
number; `grep -rn "__doc__" backend/ --include=*.py` returns nothing outside
tests, so no module docstring is ever rendered. It is a comment-accuracy item.
I would hold it at P4 rather than raise it, but note that finding (3) above is
the part worth a row, not the ±3.

**Player-reachable — `false` CONFIRMED.** All nine sites are Python docstrings,
`#` comments, or a corpus `notes` field. Nothing reaches the client, so
`main.gd`'s redirect is not even in play.

**Shipped by row CX — SPLIT, and the claim's flag is half wrong.** The four
12,717 production citations: **yes** (0 pre-row → 4 at HEAD, all inside CX-2's
new `counsel.py` and its `llm_client.py` / `question_desk.py` additions). The
9,630: **no** — `764d0ffc`, September 4, and correct when written.

**Would the suggested fix ship a regression? No — but it is the wrong fix.**
No pin reds: the only sentinel is
`tests/test_cx2_berthier_answers_the_board.py:117
COMMAND_REFERENCE = "COMMAND REFERENCE"`, a substring, and no test asserts a
length anywhere. But "update 12,717 → 12,720":

* re-arms the identical drift on the next character added to the help;
* leaves `counsel.py:19`'s two *other* errors standing (the 1,084 world-derived
  characters, the 216-vs-217);
* would "correct" seven past-tense sites that are already accurate, and would
  wrongly rewrite `question_desk.py:20`'s 9,630, which is exact.

**Recommended instead:** drop the character count from the four production
comments entirely — it belongs in the dated audit docs, where it already is and
where it is correct — and repair `counsel.py:19`'s substantive sentence to say
what is true: *the reference is a ~217-line manual with one world-derived block
(IQ-4's missions rows) spliced in, and it answers none of the twelve questions.*
That is the sentence the module's argument actually needs, and it cannot go
stale by three.

---

## 5. VERDICT LINE

**NARROWED.** The number and its cause reproduce exactly. The claim's census is
wrong in both directions (four production sites, not two), one of its two named
sites is an accurate past-tense measurement, the 9,630 is pre-existing and
**exactly correct for its date** (measured: the literal was 9,630 chars on
2026-09-04, before the IQ-4 splice existed), the title's "three figures" is one,
and the sentence it quotes is wrong in two larger ways the claim never
measured.
