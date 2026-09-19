# VERDICT: CX-CLAIM-2 — **REFUTED**

> **"`escalating corpus rows where the corpus wants a NEW ORDER | 0 / 29` is false
> on the memo's own denominator"** — filed P2 by lens `claims`.
>
> **Measured verdict: the published `0 / 29` is CORRECT, and reproduces exactly on
> BOTH trees at the production seam. The claim's `50 / 694`, `34 distinct rows` and
> its five named order-verb rows are an artefact of measuring at the WRONG SEAM —
> `LLMClient._parse_with_mock`, which sits UNDER two pre-parse repairs the shipped
> pipeline always runs. Every one of the five rows the claim names parses at
> confidence 0.95 and never reaches the gate at all.**
>
> Severity P2 → **INFO**. Not player-reachable. Not shipped by row CX (there is no
> defect to have shipped).

Read-only. Tree at `f52df77f` (clean; one commit past the `727cf88a` the task
names — `docs(cx)`, the CX-CLAIM-4 correction, which does not touch SPEC:517 /
MEMO:254; both lines are still at those exact line numbers). `LLM_MODE=mock`,
`tests/_parser_replay.install_network_guard()` up in every probe, no key, no
network, nothing under `backend/`, `godot-client/`, `tests/`, `docs/` or `tools/`
modified, no git-mutating command run (`git archive` only).

---

## 1. What I ran

Six probes under `…/scratchpad/cx_review/probes/`:

| probe | what it does |
|---|---|
| `v2_escalating_rows.py` | the census at the production seam, harness semantics |
| `v2b_arms_compare.py` | pure-mock parse vs. armed-provider parse (the recon's construction) |
| `v2c_denominators.py` | attributes **688 / 692 / 694** and **39 / 45** and **25 / 29** across four constructions × two corpora |
| `v2d_the_five.py` | the claim's five rows, one at a time, on the shipped 1805 board |
| `v2e_find_the_instrument.py` | five game_state / `world=` variants, hunting the claim's numbers |
| `v2f_seam_matters.py` + `v2i_confirm.py` | finds the seam that mints them, on both trees; runs the committed eval harness on the five |
| `v2g_levers.py` | all 8 positions of row CX's three levers |
| `v2h_pre_cx_tree.py` | the whole census re-run on a `git archive f7008582` copy |
| `v2j_residue.py` | the one honest residue |

The gate predicate is not mine: it is the **committed** one from
`tests/_escalation_census.py::install_census`, i.e. `_should_fallback_to_llm`
minus its provider-is-mock and no-key guards. The parse itself stays pure mock,
so the gate returns its real `False` and no live call is structurally possible.

---

## 2. The memo's figures reproduce EXACTLY — on both trees

Production seam = `CommandParser.parse(utterance, game_state, world=world)`.
That is the harness's own documented call shape (`backend/ai/parser_eval.py:15`)
and it is what production calls (`backend/main.py:2968`,
`parsed = parser.parse(command_text, llm_game_state, world=world)`).

| tree | entries | gate evals | escalations | distinct rows | `success: false` | rows with `expected.action` |
|---|---|---|---|---|---|---|
| **pre-CX `f7008582`** | 447 | **692** | **45** = 6.50% | **29** | **25** = **86%** | **0** |
| **HEAD `f52df77f`** | 449 | **694** | **45** | **29** | **25** = 86% | **0** |

`45 / 692 = 6.5%`, `25 / 29 = 86%` and **`0 / 29`** — all three of the memo's
numbers, from one run, at the seam the corpus harness documents. The `29` is
"all distinct escalating rows"; the `25` is those whose `expected.success` is
`false`; `25/29 = 86.2%`. Nothing is filtered and nothing is dropped.

I enumerated the 29 by hand (`v2c` output). **`emperor-address` is not among
them.** Neither is any `fa80-*` row nor `r7-hodl-lorraine-is-a-standing-hold`.

---

## 3. The five rows the claim names do not escalate — they parse at 0.95

`v2d_the_five.py`, the shipped 1805 board, production seam:

```
id                                        conf action       refusal NON_ORDER  WOULD ESCALATE   parsed
emperor-address                           0.95 attack         False     False          False    success=True action='attack'  marshal='Napoleon' target='Mack'
fa80-attak-reads-as-attack                0.95 attack         False     False          False    success=True action='attack'  marshal='Ney'      target='Mack'
fa80-mvoe-reads-as-move                   0.95 move           False     False          False    success=True action='move'    marshal='Ney'      target='Lorraine'
fa80-scuot-reads-as-scout                 0.95 scout          False     False          False    success=True action='scout'   marshal='Ney'      target='Swabia'
r7-hodl-lorraine-is-a-standing-hold       0.95 hold           False     False          False    success=True action='hold'    marshal='Davout'   target='Lorraine'
```

Identical on the pre-CX tree (`v2h`, `conf=[0.95] would=[False]` for all five).
And the **committed eval harness passes all five on both trees** (`v2i`:
`total=5 passed=5 failed=0`).

So the claim's load-bearing sentence — *"`emperor-address` has `expected.success
= true`, so it sits INSIDE the memo's own 29"* — is false at its first clause.
It is not inside the 29, because it does not escalate. The gate never opens on
it. Its own corpus note (*"reads as a leading address token, i.e. a FAILED name
attempt at 0.55 confidence"*) describes the behaviour **before NP-1**, which the
claim appears to have read as current.

---

## 4. Where the claim's numbers come from — attributed, not argued

`v2f` / `v2i`. Measure the SAME predicate one frame lower, at
`LLMClient._parse_with_mock` + the gate:

```
[head] WRONG SEAM (_parse_with_mock + gate): evals=694 esc=50 rows=34
[pre ] WRONG SEAM (_parse_with_mock + gate): evals=692 esc=50 rows=34
  of the claim's five: 5 -> ['emperor-address', 'fa80-attak-reads-as-attack',
                             'fa80-mvoe-reads-as-move', 'fa80-scuot-reads-as-scout',
                             'r7-hodl-lorraine-is-a-standing-hold']
  emperor-address                       conf=0.55 action='attack'  WOULD=True
  fa80-attak-reads-as-attack            conf=0.50 action='unknown' WOULD=True
  fa80-mvoe-reads-as-move               conf=0.50 action='unknown' WOULD=True
  fa80-scuot-reads-as-scout             conf=0.50 action='unknown' WOULD=True
  r7-hodl-lorraine-is-a-standing-hold   conf=0.50 action='unknown' WOULD=True
```

**`50 / 694` at HEAD, `50 / 692` at pre-CX, `34` distinct rows, and precisely the
claim's five** — the claim's whole table, to the unit, on both trees. The five
extra rows are exactly the ones resolved by work that happens in
`CommandParser.parse` ABOVE that call:

1. **`CommandParser.parse` → `repair_leading_verb_typo`** (`parser.py:1608`), the
   FA-80 pre-parse rewrite. Its own docstring at `parser.py:1596` says why it
   must be there: *"the first cut rewrote only the mock chain's own text, so
   'Davout, hodl Lorraine' parsed as `hold` while the strategic layer read
   'hodl'"*. Four of the five.
2. **`_parse_text` → `normalize_sovereign_address`** (`parser.py:1668`), NP-1's
   sovereign rewrite, *"BEFORE every downstream stage"*, resolved through
   `_find_player_sovereign(world, game_state)` — which needs the `world` the
   production call passes. That is `emperor-address`.

`v2e` isolates the second half independently: keep the full production payload
but drop the `world=` kwarg and `emperor-address` alone starts escalating
(46 / 694, 30 rows). Pass `{"world": w}` as the whole game_state and it goes to
68 / 694, 52 rows — the trap CX-CLAIM-1 warns about, one step further than it
realised.

**The gap between 45 and 50 is not a predicate, a filter or a row exclusion. It
is two seams.**

---

## 5. Pre-existing? Did row CX move it?

No, and no — the number is invariant.

* `v2g`, all 8 positions of `A_QUESTION_NEVER_ORDERS` × `A_RETREAT_CAN_BE_A_NOUN`
  × `AN_ADDRESS_NEEDS_NO_COMMA`: **694 / 45 / 29 in every one**, symmetric-
  difference of the escalating id set against all-levers-on = `[]` at every
  position, and `five=0` at every position.
* `v2h`, the pre-CX tree extracted with `git archive f7008582`: **692 / 45 / 29**,
  `rows carrying expected.action : 0 []`, the five at 0.95.

The `0 / 29` line was authored by row CX (`git log -S`: `b4a27a15`, moved by
`704df816`), so the row *published* it — but it published a figure that is
correct at the seam the game actually uses, and that its own levers cannot move.

---

## 6. Would the suggested fix ship a regression? **Yes — a documentary one, and it inverts the row's ruling**

The claim's fix is *"restate as `5 / 34` (or `1 / 29`)"*.

* **No committed pin goes red** — I grepped `tests/` and `tools/` for `0 / 29`,
  `25 / 29`, `45 / 692` and their unspaced forms: **zero hits.** The figure has no
  test. That is a weakness of the row, not of the figure, and it is the only
  thing the claim is downstream-right about.
* **It would make the memo's own table incoherent.** `45 / 692 = 6.5%` and
  `25 / 29 = 86%` sit two lines above and are production-seam measurements that
  reproduce. Replacing the third line with a `_parse_with_mock` figure mixes two
  instruments inside one table.
* **The sentences it would break.** It would assert that `Ney, attak Mack`,
  `Ney, mvoe to Lorraine`, `Ney, scuot Swabia`, `Davout, hodl Lorraine` and
  `Emperor, attack Mack` are orders the deterministic chain needs a model to
  rescue. All five are resolved deterministically at 0.95, and four of them are
  pinned through the real `/command` endpoint at
  `tests/test_fa_slice7_the_mock_speaks_plainly_2026_09_04.py:405-410` (`TYPOS`)
  — **12 passed** when I ran that selection. Publishing `5 / 34` would put the
  spec in direct contradiction with a green pin.
* **It inverts the ruling it is aimed at.** §4's conclusion is *"the
  deterministic chain carries twelve times more measured value than the model"*
  and *"decision (iv) — keep escalation, RE-AIM it"* at the question desk. The
  five rows are the deterministic chain's best evidence FOR that conclusion.
  Counting them as model-rescues would mis-aim CR-6.

---

## 7. The one honest residue (INFO, not the claim)

The claim is wrong about which rows and wrong about the arithmetic, but it
gestures at a real ambiguity in the WORDING, and I record it rather than bury it.

Read strictly as published — *"escalating corpus rows where the corpus wants a
NEW ORDER"* meaning *rows whose `expected` names an order* — the answer is
**0 / 29**, measured, on both trees: **not one of the 29 carries an `expected.action`
key at all.**

Read loosely — *rows whose `expected` wants a successful, order-bearing parse* —
it is **4 / 29**, and those four are (`v2j` + the corpus):

| row | expected | what it is |
|---|---|---|
| `naey-attack-wellington` | `{success: true, marshal: "Ney"}` | marshal-typo rescue; parses `attack / Ney / Wellington` at conf **0.55** |
| `soutl-attack-mack` | `{marshal: "Soult"}` (implicit `success=True` per the harness's own rule) | marshal-typo rescue; parses `attack / Soult / Mack` at conf **0.55** |
| `cr5-deleg-aggressive-ney-resolves-live` | `{success: true, marshal: "Ney"}` | `live_only` delegation |
| `cr5-deleg-cautious-davout-resolves-live` | `{success: true, marshal: "Davout"}` | `live_only` delegation |

**The memo does not hide these.** Its ruling names them in the same breath:
*"Not (v) drop it: two rescue classes are real"* — and the two rescue classes are
exactly the marshal-typo family and the delegation family. So the table line and
the ruling are consistent; at most the line could say *"…where the corpus names a
NEW ACTION"*, or carry a four-word footnote. That is a copy nicety, not a P2, and
it is **not** what CX-CLAIM-2 argues.

---

## 8. A measured correction that belongs to CX-CLAIM-1, recorded here because I measured it

The memo's ⚠ note at SPEC:512 / MEMO:249 explains the 45-vs-50 gap as *"a
hand-written re-implementation of the same predicate"*. Measured, the gap is
**entirely the seam**: the identical committed predicate returns 50 / 34 at
`_parse_with_mock` and 45 / 29 at `CommandParser.parse`, on both trees, to the
unit. Whatever the first pass actually was, "re-implemented predicate" does not
explain the discrepancy and "the real-predicate figure is the one cited" is the
right call for the wrong stated reason. The honest note is: *the first pass
measured under the pre-parse repairs; the cited figure measures at the
production call shape.* CX-CLAIM-1's own reconstruction (`45 = 50 − 5`, five rows
"silently dropped") is also refuted by this: nothing was dropped —
`soutl-attack-mack` is inside the 29, and the other four never escalate.

**Also noted in passing, and already someone else's row (CX-CLAIM-8):** the
table's parenthetical *"447 entries × both worlds"* and its `692` are stale at
HEAD — 449 entries, **694** evaluations. The escalation count is `45` at both, so
`6.5%` → `6.48%`; the drift is cosmetic.

---

## 9. Verdict

**REFUTED.** `0 / 29` stands, measured at the production seam on the pre-CX tree
and at HEAD, invariant under all eight lever positions. `emperor-address` is not
in the 29; neither are the four typo rows. `1 / 29` and `5 / 34` are both wrong,
and the `34` denominator is a measurement taken one frame below the shipped
pipeline. Not player-reachable (a documentation figure; and the five utterances
it concerns all work correctly when typed). Nothing to fix.
