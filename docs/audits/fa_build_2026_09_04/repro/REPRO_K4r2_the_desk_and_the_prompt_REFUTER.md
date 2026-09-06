All arms measured. Report follows.

---

# REFUTATION — FA-R4 (the end-turn vocabulary, both gates)

**Method note that reframes everything below: the tree is NOT clean.** My prompt (and the reporter's) says "HEAD 9ef38da8, clean". `git status` shows **27 modified files, +508/−37**, including `clause_guards.py`, `main.gd`, `llm_client.py` — **the FA-R4 fix is already built in the working tree** — plus `world_state.py` (+60), `combat_executor.py` (+83), `dispatch.py` (+71), `campaign_log.py` (+57), `disobedience.py` (+36), `executor.py` (+39), `marshal.py` (+29). Every behavioural probe I ran therefore had to be run in **two arms** (HEAD's predicate monkeypatched back vs the shipped worktree). Any figure in the report that says "the shipped board" is ambiguous about which tree, and one of them does not survive that ambiguity.

Probes: `r1_slice_pins.py`, `r2_command_matrix.py`, `r3_exposure.py`, `r4_exposure_diag.py`, `r5_live_escalation.py`, `r6_harness_blind.py`, `r7_differential.py`, `r8_case_and_fuzzy.py`, under `.../scratchpad/s14/refute_D_endturn/`. Nothing in the repo was modified.

---

## CLAIM 1 — "the gate would have armed on 10 of 12 turns"

**MY MEASUREMENT.** I ran the identical 12-`end turn` probe **five times** on the identical tree, reading `pending_lapsing_count` / `pending_marshal_decisions` off the real `POST /command` response:

| run | armed / 12 | turns reached | note |
|---|---|---|---|
| A | **8** | 2→13 | decisions 0 throughout |
| B | **12** | 2→**5** | turn stopped advancing at 5 |
| C | **9** | 2→13 | decisions=**1** at step 8 |
| D | **4** | 2→**4** | stalled |
| E | **6** | 2→**6** | stalled |

`SOVEREIGN_SEED: campaign seed 'historical'` printed on every run; save dir fresh per run (uuid'd), so no autosave carry-over.

**VERDICT: REFUTED as stated.** "10 of 12" is one sample of a **nondeterministic** process presented as a property of the board. The ambient combat RNG is not covered by the campaign seed — CLAUDE.md already records this (PC15-9: *"root cause = ambient combat RNG, which no campaign-seed pin covers"*) and the reporter's table has the shape of a single unrepeated run. The **qualitative** claim survives and I would keep it: the gate armed on every one of steps 1–5 in all five runs, so "this is the normal condition of the board, not a corner case" is right. **The number must not go in a landing record.** If a figure is wanted it needs an N-run distribution, not a table.

---

## CLAIM 2 — "There is no server-side backstop for the typed route"

**MY MEASUREMENT.** Runs B, D and E all stalled, and the diagnostic printed why:

```
step  4  turn 4->4  lapsing=2 decisions=0  *** DID NOT ADVANCE
     success : False
     message : You must decide how to handle the captured region first! |
               Your forces have taken Swabia. Plunder it for 600 gold ... ('plunder' or 'secure')
     pending_capture_choice: True
```

Typed `end turn` was **refused by the server** — 3 of 5 runs, as early as turn 4.

**VERDICT: REFUTED.** There is a server-side backstop for the typed route, and the reporter's own cited source says so. Their quote of `_auto_end_turn_defer_notice`'s docstring includes the sentence *"the pending-choice block at the head of `execute` refuses every command, `end turn` included."* They read that and then wrote the opposite. The true, narrower claim is: **there is no server-side backstop for unanswered envoys or an unanswered marshal decision on the typed route** — which is what `executor.py:909`'s *"Review them or end the turn explicitly to let them lapse"* actually says. Fix the sentence; the argument it supports (the client confirm is the only guard for those two) is unaffected.

---

## CLAIM 3 — the vocabularies are identical at HEAD, 0 divergence

**MY MEASUREMENT.** Beyond the 32-fixture check I ran a **differential fuzz**: 25,088 generated strings (leading whitespace × 10 address forms × 7 separators × 14 cores × 7 punctuation tails) against backend `is_bare_end_turn` and a line-for-line Python transcription of the `.gd` predicate (including `begins_with` / `lstrip(" \t")` / the loop's non-`break` fall-through).

```
fuzzed 25088 strings
disagreements: 0
```

**VERDICT: CONFIRMED, and strengthened.** Parity is now measured over a wide space rather than asserted over 32 fixtures — in both the HEAD shape and the built shape.

---

## CLAIM 4 — the mock and live tables

**MY MEASUREMENT.** HEAD arm, real `POST /command`, fresh 1805 world per case, 25 commands:

```
'end turn'/'next turn'/'end_turn'/'end turn.'/'END TURN'  bk=T cl=T succ=T  1->2
'Berthier, end turn' 'Sire, end turn' 'Berthier: end turn'
'Berthier, next turn' 'Sire, next turn'                   bk=F cl=F succ=F  1->1
'end the turn' 'finish turn' 'end turn now' 'end my turn'  bk=F cl=F succ=F  1->1
'Berthier, status' / 'Berthier, help'                      bk=F cl=F succ=T  1->1
soft-lock predicate: 0 of 25
```

Live escalation (pure, no network call — `fast_parse` + `_should_fallback_to_llm`):

```
HEAD:  'Berthier, end turn' unknown 0.50 -> model? True
       'Sire, end turn'     unknown 0.50 -> model? True
       'end the turn'       unknown 0.50 -> model? True
       'do not end turn'    unknown 0.50 -> model? False   (negation holds)
WORKTREE: all addressed forms -> end_turn 0.80 -> model? False
```

**VERDICT: CONFIRMED, exactly.** Both tables reproduce cell for cell, including the negation arm not escalating and `Berthier, status`/`help` resolving at 0.80.

**One NARROWING on the live headline.** The reporter's soft-lock demonstration **stubbed the provider** to return `end_turn`. The machinery is proven (escalation is real; a returned `end_turn` does advance the turn behind a `False` client gate) and `end_turn` is genuinely in `VALID_ACTIONS:119`, so the model *can* return it — but *"which is what a competent model returns"* is an assumption, not a measurement. State it as: **the escalation is measured; the model's answer is assumed.**

---

## CLAIM 5 — canonicalisation, and "backend-only is strictly harmful"

**MY MEASUREMENT.** Read at HEAD: `_is_end_turn_phrasing(command)` (1484) → `_execute_end_turn()` (1403) → `_send_end_turn()` (1420), whose body at **1435** is `api_client.send_command("end turn", _on_command_result)`. The typed text is discarded; `_add_to_history("end turn")` too.

**VERDICT: CONFIRMED.** And `main.gd:1435` is **exact** — it cites the `send_command` line, not the `func` line. I initially suspected a stale number here and was wrong. The consequence (client-only sufficient, backend-only harmful, `.gd` must land first or together) follows directly and my HEAD/worktree matrix is consistent with it.

---

## CLAIM 6 — the six slice pins and the function-order hazard (§5d)

**MY MEASUREMENT.** Six pin sites confirmed at **258, 277, 687** (`test_fa_slice1…`) and **691, 1303, 1314** (`test_review_2026_08_30`) — exact. Slicing the body at HEAD vs worktree:

| | HEAD | WORKTREE |
|---|---|---|
| slice length | 1369 | 2530 |
| `"attack" in body` | **False** | **True** |

```
$ pytest tests/test_review_2026_08_30.py -k "ordinary_command_is_not_swallowed"
FAILED ... assert "attack" not in body and "recruit" not in body
E   'attack' is contained here:
E     ier, Ney, attack` is still an order to Ney, and `Berthier, Sire,
1 failed, 7 passed
```

**VERDICT: CONFIRMED — and it is already live.** The reporter predicted this hazard and the in-flight build walked straight into it: not via the inserted helper but via the new **comment** inside `_is_end_turn_phrasing`, which uses `Berthier, Ney, attack` as its worked example. `tests/test_fa_slice1_the_two_words_2026_09_02.py` is 147/147 green, so this is the only red pin in the family.

---

## CLAIM 7 — the parity harness is blind (§5c)

**MY MEASUREMENT.** I re-derived `_client_gate` verbatim over the live `.gd` and over a copy with `\tc = _strip_desk_address(c)\n` deleted:

| command | harness (live) | harness (sabotaged) | REAL client |
|---|---|---|---|
| `end turn` | True | True | True |
| `Berthier, end turn` | **False** | False | **True** |
| `Sire, end turn` | **False** | False | **True** |

```
needles with strip   : ['end turn', 'end_turn', 'next turn']
needles without strip: ['end turn', 'end_turn', 'next turn']
IDENTICAL -> pin is inert for the strip: True

fixture ('Berthier, end turn', True):  backend PASS / client FAIL
```

**VERDICT: CONFIRMED, and worse than filed.** The reporter says the pin goes *inert*. It is also **actively wrong**: the harness's docstring claims it *"EVALUATES both gates against the same fixture set rather than grepping for keywords"*, and it now returns `False` for a command the shipped client accepts. Deleting the fix from the `.gd` leaves it green. This is the highest-priority item for the builder and recommendation #4 should be treated as mandatory, not optional.

---

## CLAIM 8 — series/harness cannot move

**MY MEASUREMENT.** `grep -c` over both files: `parse` **0**, `CommandParser` **0**, `/command` **0** in `tests/test_ai_intent_threat_migration.py` and `tests/test_combat_sweep_metrics.py`. Single caller confirmed: `is_bare_end_turn` has exactly one reference outside its definition, `llm_client.py:1782` (worktree) = **1778** at HEAD. `enemy_ai.py` and `turn_manager.py` contain zero `CommandParser`/`parse_command`.

**VERDICT: CONFIRMED.** The structural argument holds; GR5 is not at risk because the AI never types.

---

## CLAIM 9 — line numbers and symbol names

Checked every one. **All exact at HEAD** except two, both in the decider table row #5:

| cited | actual | |
|---|---|---|
| `_auto_end_turn_defer_notice` at `executor.py:862` | **868** | stale by −6 |
| `should_auto_end_turn` at `executor.py:2669` | **2708**, and it is a **local boolean variable**, not a function | wrong line *and* wrong kind |

**VERDICT: NARROWED.** Everything else — `clause_guards.py:129/132`, `main.gd:1377`/`:1403`/`:1420`/`:1435`/`:1484`, `llm_client.py:1778`, `_should_fallback_to_llm:863`, `validation.py:119`, `test_review:710`, all six slice-pin lines, "11 corpus rows", "22 marshals" — reproduces exactly. The body claim of that row (the defer notice reads `pending_capture_choice` + `has_current_turn_offers()` and **not** `pending_marshal_decisions`) is CONFIRMED by reading the function.

---

## CLAIM 10 — the fuzzy-collision table (§6)

**MY MEASUREMENT** (`FuzzyMatcher.match` against the live 126 regions / 22 marshals):

```
over    region=('Hanover',100)     marshal=None        ✓ matches report
all     region=('Cornwall',100)    marshal=None        ✓
done    region=('London',86)       marshal=('Ney',80)  ✓
pass    region=('Nassau',75)       marshal=('Massena',75) ✓
end     region=('Posen',80)        marshal=('Buxhowden',80)  report said Bergen
turn    region=('Trondheim',75)    marshal=None              report said Asturias
next/finish/advance -> no match    ✓
```

**VERDICT: NARROWED.** Seven of nine reproduce; two name a different region at the same score (almost certainly a tie broken by iteration order). The point the table exists to make — these words collide at auto-correct grade — stands.

---

## CLAIM 11 — the `Massena` marshal-decision instance

**MY MEASUREMENT.** `pending_marshal_decisions` was `0` on all 12 turns in three of five runs; it fired **once**, at step 8, in run C. Never at turn 11, never named in my output.

**VERDICT: NARROWED.** The architectural half — the confirm reads two conditions, and the second is the FA-16 cornered-marshal last stand — is CONFIRMED by reading `_execute_end_turn` (`if _current_lapsing_count > 0 or not _current_decision_names.is_empty()`). The specific measured instance does not reproduce and should not be quoted.

---

# What the reporter MISSED that a builder must know

1. **A pin is RED on the working tree right now.** `test_review_2026_08_30::TestTheEndTurnSynonymsMeetTheGate::test_an_ordinary_command_is_not_swallowed` fails because the new comment inside `_is_end_turn_phrasing` uses the word `attack`. Reword the example (e.g. `Berthier, Ney, hold`) or move the comment above the `func` line. The reporter *warned* about this seam; nobody checked it after the build.

2. **The client helper is case-SENSITIVE where the backend regex is IGNORECASE — and its own docstring claims otherwise.** Measured at helper level, without the caller's `to_lower()`:

   | input | backend `strip_desk_address` | client `_strip_desk_address` |
   |---|---|---|
   | `Berthier, end turn` | `end turn` | `Berthier, end turn` |
   | `SIRE, end turn` | `end turn` | `SIRE, end turn` |
   | `berthier, end turn` | `end turn` | `end turn` |

   `DESK_ADDRESS_RE.flags & re.IGNORECASE` is **True**. The `.gd` docstring says *"Mirrors the backend's `clause_guards.DESK_ADDRESS_RE`"* — it does not, in the case dimension. Parity survives today **only** because `_is_end_turn_phrasing` lowercases before calling. The moment a second client caller appears (a desk chip, a `Berthier, status` client route) the two gates diverge. This is precisely the class the last three review rounds keep finding: *a fix that touches one reader of a pipeline*. Either lowercase inside the helper or pin the invariant.

3. **No golden-corpus row for the new form.** The corpus has 436 rows; exactly **one** is desk-addressed (`fa-slice7-berthier-is-the-desk` → `Berthier, status`), and **zero** cover `Berthier, end turn`. New-action-checklist step 12 is undischarged. (The builder *did* touch the corpus in this tree — but only to convert two `live_only` FA-73 rows from `not_action` to `success: false`, which is FA-S7-D1 work, not FA-R4.)

4. **The parity harness does not merely go inert — it now mis-models the shipped client.** See claim 7. Any future fixture added there will fail on the client half even when the `.gd` is correct, which will look like a code bug and get "fixed" in the wrong place.

5. **The echo lies slightly.** `_send_end_turn` calls `add_output("► end turn")`, so a player who types `Berthier, end turn` sees `► end turn` echoed back. Harmless, but it is a visible consequence of the canonicalisation the row should mention rather than have reported as a bug later.

6. **The tutorial suggest chip is a client caller, not a bypass.** `tutorial_overlay.gd:39` declares `signal suggest_command(cmd: String)` and `:424` emits it to `main.gd`; the file contains **zero** `api_client.send_command` calls. The reporter lists "the tutorial's suggest chips" among the non-client callers justifying the backend half. That justification is wrong (the remaining ones — `tools/playtest_driver.py`, raw HTTP — are real, and sparing an API call is a good reason on its own).

7. **`tools/godot_parse_report.json` is already regenerated** in this tree, so recommendation #5's staleness pin looks discharged — but the engine boot / `SCRIPT ERROR` grep is not something I can verify read-only, and the new `_strip_desk_address` uses a `"""…"""` string literal containing `\\s` escapes as a pseudo-docstring. Worth an actual boot rather than trusting the parse report.

8. **Any "measured on the shipped board" figure in this row needs a tree stamp.** The in-flight slice changes `world_state`, `combat_executor`, `dispatch`, `campaign_log`, `disobedience`, `marshal` and `executor` — that is why my exposure runs cannot be compared to the reporter's, and why claim 1 could not be salvaged by re-running it more carefully.