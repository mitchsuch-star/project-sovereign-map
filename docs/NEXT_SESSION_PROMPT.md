# NEXT SESSION PROMPT — verify the Final Whole-Game Audit before anyone builds from it

> Overwritten each time a session hands off. Current hand-off: **September 2,
> 2026.** The final whole-game audit is committed, pushed, and named as the
> current item in `docs/STATUS.md`. It has **not** been verified end to end, and
> the next build session is meant to work straight out of it — so this session
> makes it trustworthy first.
>
> **This prompt was red-teamed before hand-off.** Four agents cold-started the
> work with nothing but this document; every fact below was re-measured against
> the repo on September 2, and their corrections are folded in. Where the audit
> or this prompt was wrong, the wrong version is named rather than quietly
> replaced.
>
> Paste everything below the line as the opening message of a fresh session.

---

You are verifying an audit before it is used as a build contract. Read
`CLAUDE.md`'s Golden Rules first; work directly on master per the project
workflow.

**Repo state:** master `97c64eba`, pushed, suite green (19,387 passed / 4
skipped). Everything the audit names is committed. **The one uncommitted file is
`docs/NEXT_SESSION_PROMPT.md` — this document.** Commit it on its own or leave
it; do not sweep it into an unrelated commit.

## What exists

The **Final Whole-Game Audit**, held September 1, 2026 at master `ccf5f111`:

| artifact | what it is |
|---|---|
| `docs/audits/FINAL_AUDIT_2026_09_01.md` | the memo of record. §0 method and limits · §1 verdict · §2 campaigns · **§3 the findings** · §4 refuted · §5 what works · §6 build order · §7 top recommendation · §8 method notes |
| `docs/audits/final_audit_2026_09_01_findings.json` | the untruncated machine record. **Do all row work here**, not in the memo |
| `docs/audits/FINAL_AUDIT_2026_09_01_HAND_VERIFIED.md` | 37 notes the previous session reproduced by hand, in parallel with the fleet |
| `docs/BUG_FIXES.md` §Final Whole-Game Audit | filed rows **FA-1..FA-102** (defects, absences, harness) |
| `docs/DESIGN_REFINEMENT.md` §FA-D | filed rows **FA-D1..FA-D26** (tie-ins) |
| `docs/audits/playtest_digests/audit-*` | the nine archived campaigns it was argued from (~200 played turns); see `docs/PLAYTESTING.md` |

**Counts, reconciled — the documents disagree and here is why.** The machine
record holds **130 rows**. **128 are filed** (FA-1..FA-102 + FA-D1..FA-D26);
the other **2 carry `_id: null`** — they are the REFUTED rows, live only in memo
§4, and are in no routing table. `STATUS.md` and `CLAUDE.md` say "128 findings
filed"; both numbers are right about different things. **Your scope is the 128
filed rows.**

Severity across the filed rows: **9 P1 · 41 P2 · 63 P3 · 15 P4.** Kinds: 70
defects, 26 tie-ins, 25 harness, 7 missing.

**§3 is grouped by KIND, not severity**, so do not navigate by it: §3a P1
defects (9) · §3b **P2 defects only, 25 of the 41 P2s** · §3c missing (7) · §3d
tie-ins P1/P2 (7) · §3e tie-ins P3/P4 (19) · §3f defects P3/P4 (36) · §3g
harness (25). **Filter by `_sev` in the JSON instead.**

### The machine record's schema, because the natural guesses silently return None

Underscore-prefixed: `_id`, `_sev` (P1..P4), `_status`, `_corrected`, `_hv`.
Plain: `kind` (defect/tie_in/harness/missing), `file`, `line`, `title`,
`summary`, `player_consequence`, `evidence`, `repro`, `fix_shape`,
`behaviour_test`, `already_filed`, `refuters` (list of `{lens, verdict,
reason}`), `merged`. FA-6's amendment sits under a plain `amendment` key plus a
top-level `amendments` array.

**Two traps in that schema:**

- **`summary` is the finder's ORIGINAL text; `_corrected` is the refuter's
  corrected reading.** They differ on exactly the 36 refuted rows and are
  byte-identical on the other 94. **Always read `_corrected`.** Reading
  `summary` on a NARROWED row means verifying the claim a refuter already
  corrected, at a seam it already moved — silent wrong work on the rows most
  likely to be wrong.
- **`lens` is empty on all 130 rows.** Per-row agent attribution was not
  preserved; it survives only inside `refuters[].lens`. So systematic bias must
  be argued from content, not computed per lens.

## Why this session exists

The audit came from a sixteen-lens find-then-refute fleet that **ran out of
budget three times.** The finders all completed. The refuter pass did not, and
the ten pillar scorers never ran at all.

**The verification census, in the record's own vocabulary:**

| `_status` | rows | what it means |
|---|---|---|
| UNVERIFIED | 46 | **nobody tried to kill it.** Unexamined, not survived |
| AUTHOR_VERIFIED | 25 | hand-reproduced by the previous session's author |
| HARNESS_AUTHOR_CHECK | 23 | author-checked harness rows |
| PLAUSIBLE | 19 | one refuter examined it and said CONFIRMED |
| NARROWED | 15 | one refuter kept the defect but corrected it |
| REFUTED | 2 | killed (the two unfiled rows) |

**No row has status CONFIRMED, and none ever will:** the memo defines it as
"two refuters agreed" and **every refuted row got exactly one refuter.** So
`PLAUSIBLE` means one adversary tried and failed — not settled. When you write
verdicts back, use this vocabulary and add `VERIFIED_2026_09_02` /
`REFUTED_2026_09_02` / `DUPLICATE` / `UNREACHABLE` / `HARNESS_ARTIFACT` rather
than inventing a second meaning for CONFIRMED.

**34 of the UNVERIFIED rows are P1 or P2** — FA-1, FA-2, FA-3, FA-4, FA-8,
FA-9, FA-13, FA-14, FA-15, FA-16, FA-17, FA-18, FA-19, FA-20, FA-21, FA-22,
FA-23, FA-25, FA-27, FA-28, FA-29, FA-30, FA-31, FA-32, FA-33, FA-35, FA-38,
FA-42, FA-43, FA-D1, FA-D2, FA-D4, FA-D5, FA-D7.

**Two severity ladders share the P1–P4 labels.** For `defect` / `missing` /
`tie_in`, severity is player impact. For the **25 `harness` rows it is
evidential impact** — how badly this degraded the audit's own conclusions — and
10 of them state `player_consequence: "None…"` on purpose. FA-10 is correctly
P1 despite no player consequence, because it invalidated four flagship
conclusions. Do not re-grade a harness row down for having no player impact.

**There is precedent for finding the audit wrong, and that is the outcome the
owner wants when warranted.** After publication he challenged FA-6 ("attack next
turn ends the turn, forfeiting 4 AP") on the grounds that charging AP for a
deferred order makes no sense and would be a cheat. **He was right; the row was
amended P1 → P2 in place** (`97c64eba`): action points reset every turn
(`world_state.py:9608`), so nothing is banked and the fix must not queue the
order. What survived was narrower and re-measured — a *question* ("what happens
next turn") ends the turn. **Correct rows in place with a dated amendment; never
delete one.**

## Your three tasks

### 1. Are the bugs real?

Order: **the 34 UNVERIFIED P1/P2 rows first**, then the remaining UNVERIFIED,
then spot-check enough PLAUSIBLE/NARROWED/AUTHOR_VERIFIED rows to calibrate
whether single-refuter and author verification held up. (PLAUSIBLE and the
memo's "CONFIRMED" are the same 19 rows — do them once.)

Take the adversarial position; **default to REFUTED and make each row earn its
place**:

- Open the cited seam and read it. Does the code do what `_corrected` says?
- **Run the row's own `repro`.** All 130 carry one.
- **Reachability:** can a player actually hit this through a typed command, the
  client's routes, or the enemy phase? Some rows may be true of the code and
  unreachable in the shipped game.
- **Harness or game?** §3g lists 25 known harness effects — a passive France,
  the driver's answer policy, a digest counter that lies. Do not re-file those
  as game defects.
- **Duplication:** 126 of 130 rows carry an `already_filed` claim, and the
  documents to check against run to ~19,000 lines with no OPEN/FIXED index.
  **Scope this: check `already_filed` properly on the 34 priority rows only**,
  and spot-check the rest. If you build an index of currently-OPEN row ids and
  their seams, commit it — the next session will need it too.

**Already established mechanically on September 2 — do not redo, but note its
limit.** A scan of all 130 rows found every cited `file` exists, every `line` is
within its file, and every row carries a repro, a fix shape and a behaviour
test. **That scan covered the `file` and `line` fields only.** Paths *inside*
repro text were not checked, and **17 rows depend on gitignored
`tools/playtest_runs/` or `saves/` artifacts** (FA-1, FA-3, FA-4, FA-9, FA-17,
FA-19, FA-21, FA-37, FA-38, FA-39, FA-41, FA-76, FA-83, FA-85, FA-D13, FA-D14,
FA-D24). Those run only because the previous session's output is still on this
machine; on a fresh clone they do not. Re-derive or re-generate rather than
trusting them.

### 2. Are there adjacent bugs?

The audit's recurring shape is *one rule with two implementations and only one
maintained*. When you confirm a row, check its neighbourhood before moving on:

- The seam's other callers — an **AST or `grep -c` census**, never a
  single-file `re.search`; this project has been burned by that repeatedly.
- **The mirror.** Golden Rule 5 says enemy AI runs the same executor as the
  player, so a player-path defect usually has an AI-path twin.
- **The producer→renderer join** — a backend key no `.gd` reads, or a `.gd`
  read no producer emits. Several confirmed rows are exactly this.
- What the row's proposed fix would break in a sibling branch.

File new rows as **FA-N1, FA-N2, …** in the same tables with the same fields:
seam `path:line`, player consequence, runnable repro, the ONE seam to change,
and the behaviour test to write.

### 3. Does the prose make sense — all of it?

**Review prose against the JSON, not the memo.** The memo truncates long fields
by design — **408 ellipses**, some mid-word — so "truncated sentence" is the
memo's format, not a defect, and flagging it there wastes the pass.

What to look for, with the real starting points:

- **Dangling cross-references — the highest-yield real defect.** Six rows carry
  "finding N" self-references from a lens agent's private numbering: **FA-4,
  FA-46, FA-67, FA-74, FA-90, FA-D2.** FA-4's "finding 1" and FA-D2's "finding
  1" denote different rows, and because `lens` is empty they cannot be resolved
  mechanically. Rewrite each to name the row it means, or cut the reference.
- **Genuinely unbalanced brackets: FA-74, FA-93, FA-D24** (measured with
  backticked code spans masked). ⚠ **An earlier draft of this prompt sent the
  reader to FA-38 and FA-D15 — that was wrong.** Both are clean: their
  "unbalanced" parens are inside code quotations (`` `_add("` ``, `` `.get(` ``).
  A naive bracket check flags 12 rows and all 12 are that false positive. Do
  not "fix" a code citation into balance.
- **Claims that over-reach their evidence.** A row saying "verified by running"
  should name what was run. A title claiming more than its body supports gets
  the title corrected — exactly what happened to FA-6.
- **Severity honesty**, under the two-ladder rule above.
- **The memo's own prose sections** (§0–§2, §6–§8), not just the findings. In
  particular §6: are the eight slices coherent groupings, is the order
  defensible, and is the coverage note accurate? (Measured Sept 2: the slices
  name 59 of 128 rows; all 9 P1s are covered; 16 of the 50 P1/P2 rows are in no
  slice; 17 of the 26 FA-D rows sit outside. The memo now states this — check
  it is still true after your amendments.)
- **Cross-document agreement.** Every `FA-n` cited in prose should exist, and
  the memo, `BUG_FIXES.md`, `DESIGN_REFINEMENT.md`, `STATUS.md` and `CLAUDE.md`
  should say the same thing about the audit.

## Method rules this project holds you to

- **Reproduce before believing.** `docs/PLAYTESTING.md` is the document of
  record for driving the game: Mode A (`tools/playtest_driver.py`, in-process,
  seeded, digested) is the default; never pass `--archive` for a throwaway probe.
- **PLAYTESTING.md has no idiom for a single `POST /command` probe**, which is
  the shape many repros need. Use this, **from the repo root** (a copy in a
  scratch dir dies with `ModuleNotFoundError: backend`):

  ```python
  import contextlib, io
  from fastapi.testclient import TestClient
  import backend.main as M
  from backend.commands.parser import CommandParser
  from backend.models.world_state import WorldState
  P = "godot-client/project-sovereign/assets/maps/europe_1805.json"
  with contextlib.redirect_stdout(io.StringIO()):
      w = WorldState.from_scenario(P)
      M.parser = CommandParser(use_real_llm=False)   # load-bearing, see below
      M.world = w
      M.game_state = {"world": w}
  c = TestClient(M.app)
  d = c.post("/command", json={"command": "Ney, attack Mack"}).json()
  ```

  Swap `world` **and** `game_state` **and** `parser`; a partial swap does not
  error, it silently runs against a different world.
- **⚠ Money hazard the prompt must not leave implicit:** `.env` sets
  `LLM_MODE=anthropic`, so importing `backend.main` initialises a **live**
  parser. Overriding `M.parser` with `use_real_llm=False` is what keeps a probe
  free. A repro written as a bare `POST /command` will otherwise spend real API
  credit — and this session may run dozens.
- **Never set `PYTHONIOENCODING`** — it fakes six subprocess ERRORs and blocks
  the pre-commit hook. The ban is absolute, including for probes. Console
  stdout is cp1252 and **115 of 130 rows contain characters it cannot encode**,
  so call `sys.stdout.reconfigure(encoding="utf-8")` *inside* the snippet, or
  write to a UTF-8 file and read that.
- **A passing suite is not evidence about `BASELINE_SERIES` or M1–M7.** Those
  run in a fresh hash-seeded subprocess. This session should not move them at
  all.
- **Report-only for game behaviour** — decide what is real, do not fix it.
  **Docs are yours**: amendments, severity changes, prose repairs and new FA-N
  rows are the deliverable.
- Any test you do write, mutation-sweep (`tools/mutation_sweep.py`).
- Commit directly to master; the pre-commit hook runs `ruff` plus the full suite
  (~3 minutes). Do not bypass it.

### The amendment convention, as a checklist

FA-6 is the worked example but it did not land completely (its downgrade left a
stale "two P1s" claim in memo §6 that had to be fixed afterwards). Do all five:

1. **JSON row:** set `_sev` if it changed, suffix `_status` (e.g.
   `AUTHOR_VERIFIED (amended 2026-09-02)`), and add an `amendment` key stating
   what changed and why.
2. **JSON top level:** append to the `amendments` array.
3. **`BUG_FIXES.md` / `DESIGN_REFINEMENT.md`:** strike the old severity
   (`~~P1~~ **P2**`) and open the cell with a bolded **⚠ AMENDED** block.
4. **Memo §3:** correct the `####` heading *and* add a blockquoted amendment
   block under the row — do not silently rewrite the heading alone.
5. **Sweep for consequences:** grep the memo's §1, §6 and §7 for anything the
   change falsifies (counts, "two P1s", slice composition), and fix those too.

## What to produce

1. **`docs/audits/FINAL_AUDIT_VERIFICATION_2026_09_02.md`** — every filed row's
   verdict with the evidence, the new FA-N rows, and a section on **what the
   audit got wrong as a body of work**: its systematic biases, not just
   individual misses. Argue those from content (the `lens` field is empty).
2. **Amendments in place**, per the checklist, across the memo, the machine
   record and both routing tables.
3. **Updated headlines** in `docs/STATUS.md` and `CLAUDE.md`. ⚠ Both currently
   route the next session straight to the memo's §6 build order — that is the
   state this session is inserted in front of, and correcting it is part of
   this deliverable.
4. **A one-paragraph answer to the question the owner will actually ask:** *is
   this audit safe to build from, and which rows would you build first?*

Then commit and push.

## One honest caveat about the thing you are checking

The audit has **no pillar re-score** — the ten scorers never ran — so the August
16 priors stand. If your verification substantially changes the picture (say a
third of the P1/P2 rows fall), say so plainly rather than patching numbers, and
recommend whether a scoring pass is worth running before the build.
