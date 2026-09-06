All arms measured. Report follows.

---

# FA-R4 — the end-turn vocabulary, both gates

**Row lives in `docs/DESIGN_REFINEMENT.md:81`, not `BUG_FIXES.md`** (BUG_FIXES.md:1634-1638 only cross-references it in the slice-7 review round's "Recorded, not fixed" block). It is **not** in the machine record `final_audit_2026_09_01_findings.json` — it was filed Sept 5, 2026 by the slice-7 review round as R1-13, after the audit. There is no Sept-2 verdict to read.

## VERDICT: **WIDER** — the mechanism is right, the consequence is understated in three ways, and the ruling's *direction* is backwards.

Probes: `p1_vocab.py`, `p2_command.py`, `p3_live.py`, `p5_widen.py`, `p6_exposure.py`, `p7_pin_blindness.py`, `p8_asymmetry.py`, `p9_edges.py` — all under `.../scratchpad/s14/D_endturn/`. Nothing in the repo was modified.

---

## 1. The two vocabularies, verbatim, and the set difference

**Backend** — `backend/ai/clause_guards.py:129` + `:132` (both line numbers **exact**, not stale):

```python
END_TURN_PHRASINGS = ("end turn", "end_turn", "next turn")

def is_bare_end_turn(text: str) -> bool:
    stripped = (text or "").strip().lower().rstrip(".!? \t")
    return stripped.strip() in END_TURN_PHRASINGS
```

**Client** — `godot-client/project-sovereign/scripts/main.gd:1377` (the prior repro's `:1297` is **stale by −80**; its consumer `:1404` is now **`:1484`**):

```gdscript
var c := command.to_lower().strip_edges()
while c.length() > 0 and ".!? \t".find(c[c.length() - 1]) != -1:
    c = c.substr(0, c.length() - 1)
c = c.strip_edges()
return c == "end turn" or c == "end_turn" or c == "next turn"
```

**Set difference (p1):**

| direction | result |
|---|---|
| backend − client | `[]` |
| client − backend | `[]` |
| identical | **True** |

Evaluated against **32 fixtures** (bare forms, case, whitespace, all four punctuation marks, both addressed forms with `,` and `:`, five near-misses, two negations, two desk verbs): **0 disagreements**. The punctuation-strip sets are also identical (`".!? \t"` both sides), so `next turn.` and `end turn?` agree too.

**→ There is no live divergence.** The row's "mirrors the backend's vocabulary word for word" is exactly true. The fix must *create* parity at a wider point; nothing today is out of sync.

---

## 2. What actually reproduces — and it is not a shrug

### Mock mode (p2, real `POST /command`, fresh 1805 world per case)

| command | backend gate | client gate | success | turn |
|---|---|---|---|---|
| `end turn` / `next turn` / `end_turn` / `end turn.` | True | True | True | **1→2** |
| `Berthier, end turn` | False | False | False | 1→1 |
| `Sire, end turn` | False | False | False | 1→1 |
| `Berthier: end turn`, `Berthier, next turn`, `Sire, next turn` | False | False | False | 1→1 |
| `end the turn`, `finish turn`, `end turn now`, `end my turn` | False | False | False | 1→1 |
| `Berthier, status` / `Berthier, help` | — | — | **True** | 1→1 |

Soft-lock predicate (server advanced ∧ client gate False): **0 of 20**.

The two addressed forms shrug **differently** — `Berthier,` gets the "peers at the dispatch with concern" template, `Sire,` gets the marshal-relay one. Two different unhelpful answers to the same intent.

### Live mode — **this is the part the row does not have** (p3)

`.env` sets `LLM_MODE=anthropic`; that is the shipped default when a key is present. Measured with **no network call** (`_should_fallback_to_llm` evaluated directly, then a stubbed provider):

| command | fast action | conf | refusal | escalated to model? |
|---|---|---|---|---|
| `end turn` | `end_turn` | 0.80 | — | False |
| `Berthier, end turn` | `unknown` | 0.50 | None | **True** |
| `Sire, end turn` | `unknown` | 0.50 | None | **True** |
| `end the turn` | `unknown` | 0.50 | None | **True** |
| `finish turn` | `unknown` | 0.50 | None | **True** |
| `end turn now` | `unknown` | 0.50 | None | **True** |
| `Berthier, status` | `status` | 0.80 | — | False |
| `do not end turn` | `unknown` | 0.50 | **negation** | False |
| `Berthier, do not end turn` | `unknown` | 0.50 | **negation** | False |

With the provider stubbed to return `end_turn` (which is what a competent model returns for "Berthier, end turn"), driven through the real `/command`:

```
'Berthier, end turn'   model consulted=True  success=True  turn 1->2  client_gate=False  *** SOFT-LOCK
'Sire, end turn'       model consulted=True  success=True  turn 1->2  client_gate=False  *** SOFT-LOCK
'end the turn'         model consulted=True  success=True  turn 1->2  client_gate=False  *** SOFT-LOCK
```

**The soft-lock the row says the fix *would* create already exists, today, in the mode the shipped game defaults to.** "A player who addresses Berthier to end the turn is shrugged at, once, and types `end turn`" is a **mock-mode-only** description of the symptom. In live mode he is not shrugged at — the turn goes, and the lapse warning never appears.

The negation guard already protects `do not end turn` / `never end turn` on both sides (refusal → terminal, never escalated). That arm is safe and must stay safe.

---

## 3. What the client confirm is, and exactly when it fires

`main.gd:1403 _execute_end_turn()`:

```gdscript
if _awaiting_end_turn_confirmation:       # second press → send
if _current_lapsing_count > 0 or not _current_decision_names.is_empty():
    _show_lapse_confirmation(); return
```

It arms on **two** conditions, not one:
- `_current_lapsing_count` ← `pending_lapsing_count` (`main.py:539` → `dialogue_manager.get_lapsing_count()`), set at `main.gd:4011`.
- `_current_decision_names` ← `pending_marshal_decisions` (`main.py:717 _pending_marshal_decisions` → `strategic.pending_marshal_decisions`), set at `main.gd:4034` — the FA-16-review cornered-marshal last stand, **which FA-1 decides for him when the enemy phase begins.**

So the row's "unanswered envoys" is half the blast radius. The other half is an irreversible fate decision on a corps.

**Exposure, measured (p6, 12 consecutive `end turn`s on the shipped 1805 board):**

| turn | lapsing | decisions | gate would arm |
|---|---|---|---|
| 2 | 3 | 0 | ✔ |
| 3–7 | 2 | 0 | ✔ |
| 8 | 1 | 0 | ✔ |
| 9 | 2 | 0 | ✔ |
| 10 | 1 | 0 | ✔ |
| 11 | 1 | **1 — `Massena`** | ✔ |
| 12, 13 | 0 | 0 | ✘ |

**The confirm would have armed on 10 of 12 turns.** This is the normal condition of the board, not a corner case.

**There is no server-side backstop for the typed route.** `executor.py:909` says so in its own words: *"Review them or end the turn explicitly to let them lapse."* The only backend deferral, `executor.py:862 _auto_end_turn_defer_notice`, fires on **AP-exhaustion auto-advance only** and reads `pending_capture_choice` + `has_current_turn_offers()` — **not** `pending_marshal_decisions`. (Adjacent gap, not this row: the auto-advance path also skips the cornered-marshal warning.)

---

## 4. Every "is this an end turn" decider

| # | symbol / file | contents | notes |
|---|---|---|---|
| 1 | `clause_guards.END_TURN_PHRASINGS` / `is_bare_end_turn` (`backend/ai/clause_guards.py:129,132`) | `("end turn","end_turn","next turn")`, whole-command, trailing `.!? \t` stripped | **exactly one consumer**: `llm_client.py:1778` |
| 2 | `main.gd::_is_end_turn_phrasing` (`:1377`) | same three, same strip, hardcoded — a **mirror**, not a shared source | one consumer, `:1484` |
| 3 | **the live model** | **unbounded** | gated only by `llm_client.py:863 _should_fallback_to_llm` and the tool enum `validation.VALID_ACTIONS:119`. **This is the third vocabulary, and it is what makes today's live soft-lock.** |
| 4 | client routes that bypass #2 but still reach `_execute_end_turn()` | End Turn button (`:628`), `KEY_E` (`:950`, `:1153`), bare Enter (`:1464`) | these **do** arm the confirm — they are correct today |
| 5 | `executor.py:2669 should_auto_end_turn` + `:862 _auto_end_turn_defer_notice` | AP exhaustion | server-side, own deferral list, misses marshal decisions |
| — | `parser.py:758 valid_actions`, `validation.py:119/185`, `context_carryover.py:54`, `enemy_ai.py:7236` | action-**name** sets | not phrasing vocabularies |

---

## 5. **What the filed fix would break** — the highest-value finding

### (a) The row's direction is backwards. `main.gd:1435` canonicalises.

```gdscript
func _send_end_turn():
    _add_to_history("end turn")
    api_client.send_command("end turn", _on_command_result)
```

**The typed text is discarded.** Whatever `_is_end_turn_phrasing` accepts, the server receives the literal `"end turn"`. Therefore:

- **Client-only is *sufficient*** for the row's done-when. A widened `_is_end_turn_phrasing` arms the confirm *and* sends a string the **unchanged** backend already accepts (measured p2).
- **Backend-only is strictly *harmful*.** Measured (p8), with `is_bare_end_turn` given the desk-address strip exactly as the prior repro prescribes, in **mock** mode:

```
'Berthier, end turn'   success=True  turn 1->2  client_gate=False  lapsing_at_send=3  *** REGRESSION
'Sire, end turn'       success=True  turn 1->2  client_gate=False  lapsing_at_send=3  *** REGRESSION
'Berthier, next turn'  success=True  turn 1->2  client_gate=False  lapsing_at_send=3  *** REGRESSION
```

Three envoys lapsed with no warning. **Backend-first manufactures the exact bug in mock mode that the model already causes in live mode.** If the slice is split across commits, the `.gd` must land first or with it — never after.

### (b) "Widen BOTH gates" read as *adding phrasings* reds two deliberate pins

- `tests/test_fa_slice1_the_two_words_2026_09_02.py::test_the_vocabulary_itself_is_unchanged` (`:283-286`)
- `tests/test_review_2026_08_30.py::TestEveryEndTurnPhrasingMeetsTheGate::test_the_backend_vocabulary_is_the_same_three` (`:707-708`)

Both assert `END_TURN_PHRASINGS == ("end turn","end_turn","next turn")`. The second's docstring exists to say so: *"if the parser grows a fourth phrasing this pin fails, rather than the gate silently going porous again."* Adding a phrasing is a **conscious pin flip**, and the slice must say so.

### (c) The parity harness is structurally blind to an address strip

`tests/test_fa_slice1_the_two_works...py::TestTheClientGateSpeaksTheSameVocabulary._client_gate` (`:249-265`) re-derives the client predicate with `re.findall(r'c\s*==\s*"([^"]+)"', body)` — **equality needles only**. Demonstrated (p7) against an in-memory `.gd` carrying a correct `RegEx`-based strip:

| command | harness before | harness after **correct** `.gd` fix |
|---|---|---|
| `end turn` | True | True |
| `Berthier, end turn` | False | **False** |
| `Sire, end turn` | False | **False** |

Two consequences: **(A)** adding `("Berthier, end turn", True)` to `FIXTURES` fails the *client* half even when the `.gd` is right; **(B)** deleting the strip from the `.gd` again leaves the harness **green** — the parity pin goes **inert for the one behaviour this row adds.** The harness must be re-derived (strip-aware) or replaced by something that drives the real predicate (`tools/wo7_matcher_smoke.gd` already loads `res://scripts/main.gd` and calls real predicates — that is the existing pattern).

### (d) Function ORDER in `main.gd` is load-bearing

Six pin sites slice the body with `src[src.index("func _is_end_turn_phrasing("):]` then `body[:body.index("func _execute_end_turn():")]`:
`test_fa_slice1_the_two_words_2026_09_02.py:258, 277, 687` · `test_review_2026_08_30.py:691, 1303, 1314`.

`_is_end_turn_phrasing` must stay **immediately above** `_execute_end_turn`. And `test_review_2026_08_30::test_an_ordinary_command_is_not_swallowed` asserts over that same slice:
- `"find(" in body` — survives (the punctuation loop keeps it; verified True before and after an in-memory fix), but a rewrite that drops the loop reds it *and* reds `test_fa_slice1:690` which pins `"c.substr(0, c.length() - 1)"`;
- `"attack" not in body and "recruit" not in body` — a helper inserted **between** the two functions mentioning either word reds it.

### (e) `.gd` edit ⇒ the Godot report goes stale

`main.gd` is in `tools/godot_parse_check.gd::SETTLEMENT_CRITICAL_SCRIPTS`, and `tests/test_godot_parse_harness.py::test_godot_parse_report_is_not_stale_relative_to_settlement_godot_sources` compares the committed `tools/godot_parse_report.json` timestamp against filesystem mtime. **It goes RED on the edit** until the harness is re-run with Godot and the report regenerated. There is no behaviour pin over `main.gd` in Godot — only this syntax/load harness; every behaviour pin is a Python-side source grep.

---

## 6. Collisions, if anyone widens the word list instead of stripping the address

**Address strip — collision-free on the shipped board** (p4, p9). 22 marshals / 126 regions / 20 nations: **zero** whose name the strip eats, **zero** starting with `berthier`/`sire`. `_DESK_ADDRESS_RE = ^\s*(?:berthier|sire)\s*[,:]\s*`. Edges hold:

| command | today | after strip |
|---|---|---|
| `Berthier, end turn`, `Sire, end turn`, `Berthier: next turn`, `berthier,end turn`, `  Sire , end turn ` | False | **True** |
| `Berthier, do not end turn`, `Sire, never end turn` | False | False |
| `Berthier, end turn please`, `Berthier, end turn now`, `Berthier, end the turn` | False | False |
| `Ney, end turn`, `Talleyrand, end turn`, `Sirens, end turn`, `Sire, what happens next turn` | False | False |

**Word-list widening — three real hazards, measured:**

| candidate | current fast-parse | verdict |
|---|---|---|
| `pass` / `pass turn` / `pass the turn` | **`wait` @ 0.80** | **steals a live action** |
| `hold` | `hold` @ 0.80 | never add |
| `wait` | `wait` @ 0.80 | never add |
| `proceed to next turn` | `unknown` @0.50, **refusal=deferral** | claimed by FA-7's deferral guard |
| `end the turn`, `end my turn`, `end turn now`, `finish turn`, `finish the turn` | `unknown` @0.50, no refusal | **safe** |
| `next`, `done`, `finish`, `over`, `all`, `end`, `turn` | `unknown` @0.50 | see fuzzy below |

Fuzzy-name collisions at auto-correct-grade scores (`backend/utils/fuzzy_matcher.FuzzyMatcher.match`, the CA8-28 / WO-13 class):

```
'over'  -> region Hanover  @100      'all'  -> region Cornwall @100
'done'  -> region London   @86  / marshal Ney @80
'end'   -> region Bergen   @80  / marshal Buxhowden @80
'pass'  -> region Nassau   @75  / marshal Massena  @75
'turn'  -> region Asturias @75
'next', 'finish', 'advance' -> no match (clean)
```

Golden corpus already constrains this: **11 rows** touch the vocabulary, including `fa6-attack-and-end-turn-keeps-the-attack` ("Ney attack Mack and end turn" → attack, `not_action: end_turn`), `fa6-leading-next-turn-is-not-a-command`, `fa6-fortify-until-next-turn-fortifies`. None flips under the address strip (none carries a `Berthier,`/`Sire,` prefix). None flips under the safe widenings either — but the corpus needs a **new row** for whatever is added (new-action checklist step 12).

---

## 7. Pins that flip

| pin | flips under strip? | flips under widening? |
|---|---|---|
| `test_fa_slice1...::test_both_gates_agree` (`:267-270`) | **YES if a `Berthier,` fixture is added** — client half fails against a correct `.gd` (harness blind, §5c) | no |
| `test_fa_slice1...::test_the_vocabulary_itself_is_unchanged` (`:283`) | no | **YES** — conscious flip |
| `test_fa_slice1...::test_the_client_no_longer_uses_a_substring_test` (`:271`) | no | no |
| `test_fa_slice1...::test_the_client_body_still_strips_trailing_punctuation` (`:680`) | no, if the loop is kept | no |
| `test_review_2026_08_30::test_the_backend_vocabulary_is_the_same_three` (`:707`) | no | **YES** — conscious flip |
| `test_review_2026_08_30::test_the_client_speaks_the_parsers_vocabulary` (`:686`) | no | no (grep-only) |
| `test_review_2026_08_30::test_the_helper_claims_every_phrasing...` (`:1298`) | no | no |
| `test_review_2026_08_30::test_an_ordinary_command_is_not_swallowed` (`:1312`) | only if `find(` is dropped or a helper with `attack`/`recruit` is inserted in the slice | same |
| `test_ux_fixes_2026_08_23.py:467 _DISPATCH` | no — a body change, not a call-site change | no |
| `test_godot_parse_harness::..._is_not_stale...` (`:109`) | **YES on any `.gd` edit** — regenerate `tools/godot_parse_report.json` | same |

Baseline, run narrow just now: `test_fa_slice1_the_two_words` + `test_review_2026_08_30` end-turn selection **42 passed**; `test_ux_fixes_2026_08_23` latch selection **5 passed**. All green today.

⚠ `test_review_2026_08_30:710` asserts the literal source line `"elif is_bare_end_turn(command_lower):"`. **Change the function body, not the call site** — `is_bare_end_turn(_desk_text)` reds it.

---

## 8. Series / harness risk: **none, structurally**

- `is_bare_end_turn` has **exactly one caller in the entire backend** (`llm_client.py:1778`), inside `_parse_with_mock`, reachable only from `parse_command` / `parse_command_structured` / `fast_parse` — the player-typed path. The AI never types a command.
- `tests/test_ai_intent_threat_migration.py` (`BASELINE_SERIES`): `grep -c "parse"` = **0**; zero `CommandParser`, zero `/command`, zero `.execute(` (its 13 "executor" hits are all comment text).
- `tests/test_combat_sweep_metrics.py` (M1–M7): `grep -c "parse"` = **0**; same, 11 comment-only "executor" hits.
- `main.gd` is not Python and is not imported by either.

Neither can move. This is a structural argument, not an "it happened not to change" observation.

---

## 9. Recommended build shape

1. **Client first, or same commit.** Add a leading desk-address strip to `main.gd::_is_end_turn_phrasing`, *inside* the function, keeping the punctuation loop and keeping the function immediately above `_execute_end_turn`. This alone discharges the done-when (the client canonicalises to `"end turn"` on the wire).
2. **Backend second, in the same commit**, for the non-client callers (`tools/playtest_driver.py`, raw HTTP, the tutorial's suggest chips) and to stop paying for an API call that resolves deterministically: strip `_DESK_ADDRESS_RE` **inside `is_bare_end_turn`'s body**, leaving `END_TURN_PHRASINGS` and the call site `elif is_bare_end_turn(command_lower):` untouched. Both "vocabulary unchanged" pins stay green; `:710` stays green.
3. **Do NOT add phrasings to `END_TURN_PHRASINGS` in this row.** If a widening is wanted, it is a separate decision with two conscious pin flips, and `pass`/`pass turn`/`hold`/`wait`/`proceed to next turn` are off the table on measurement.
4. **Re-derive the parity harness.** `_client_gate` must model the strip, or better: drive the real GDScript predicate the way `tools/wo7_matcher_smoke.gd` already does. Otherwise the row's new behaviour ships with an inert pin — the exact failure the last three slices' review rounds keep finding.
5. **Regenerate `tools/godot_parse_report.json`** and boot the engine once (`grep SCRIPT ERROR`) — the standing rule for any `.gd`-touching slice.
6. **Correct the row's own text** on landing: the vocabularies do not currently diverge; the live-mode soft-lock is pre-existing, not a hazard of the fix; the confirm guards a cornered marshal as well as envoys; and it would have armed on 10 of 12 turns of the shipped board.
7. **Consider filing** the adjacent gap found in passing: `executor.py:862 _auto_end_turn_defer_notice` defers on capture-choice and envoys but **not** on `pending_marshal_decisions`, so the AP-exhaustion auto-advance also runs past an unanswered last stand. Same class, different route, out of this row's scope.