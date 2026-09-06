# FA-S7-D1 — the unknown-action prompt line

Probes: `…/scratchpad/s14/E_prompt/probe_{corpus,unknown_shape,unknown_shape2,vacuity,escalation,hygiene,notaction_vacuity,harm,callcount,murat}.py`

## VERDICT: **NARROWED on the harm · REFUTED on the fix**

The mechanism is real and the prompt gap is real. But the row's own example marshal is structurally immune to the harm it names, and **the second half of the ruling — "flip the two FA-73 live twins to `action: unknown`" — cannot be built as written**: one spelling fails the eval in every possible outcome, the other reds a named hygiene pin and is provably vacuous. The corpus schema cannot express `action: "unknown"`.

---

## 1. What reproduces

### The prompt gap — REPRODUCED exactly
`backend/ai/prompt_builder.py::build_parse_prompt`, the f-string at **line 411**, header at **419–420**:

```
419:## Valid Actions
420:{actions_list}
421:
422:## Valid Regions
```

`actions_list = ", ".join(sorted(VALID_ACTIONS))` (line 401). Measured: **54 actions, and `"unknown"` is NOT one of them** — it lives in `validation.META_ACTIONS`, not `VALID_ACTIONS`. Grep for `bayonet | screening | screen | restore order | no listed action` in `prompt_builder.py`: **zero hits**. The word "unknown" appears 5× in the built prompt, all inside the `## Personality Rules` block (lines 442–449), and only for delegation.

Both twins escalate: fast parse returns `action='unknown'`, **confidence 0.5**, below the 0.7 gate, not a refusal, not `NON_ORDER_ACTIONS` → the live model decides.

### The harm — REPRODUCED, but the row names the wrong marshal
Roster census, 1805 boot — **`is_reckless_cavalry` is true for exactly one Frenchman:**

| marshal | personality | cavalry | reckless_cav | recklessness |
|---|---|---|---|---|
| Ney, Davout, Soult, Lannes, Bernadotte, Massena, Napoleon | — | **False** | **False** | 0 |
| **Murat** | aggressive | True | **True** | 0 |

Driving `/command` with a faked live provider answering `charge` (`probe_harm.py`):

| utterance / model answer | result |
|---|---|
| `Ney, fix bayonets` → `charge` (no target) | success=False, **AP 4→4**, *"Ney is not cavalry and cannot execute a Glorious Charge."* |
| `Ney, fix bayonets` → `charge` target=Mack | success=False, AP 4→4, same refusal |
| `Murat, fix bayonets` → `charge`, recklessness 0 | success=False, AP 4→4, *"needs to build momentum first"* |
| `Ney, cover the retreat` → `retreat` | **success=True, Ney MOVED Rhineland→Lorraine, AP 4→4 (free)** |
| `Ney, fix bayonets` → `repair` | success=False, AP 4→4, *"Specify a region"* |

Give Murat recklessness 2 and an adjacent enemy (`probe_murat.py`):

```
'Murat, fix bayonets' → charge
   success=True, AP 4 → 3
   Murat  22,000 → 3,840   (-18,160 — 83% of his corps)
   Mack   52,000 → 41,478  (-10,522)
   "[Cavalry][Combat] GLORIOUS CHARGE! Murat leads a devastating cavalry assault!"
```

**So: the row's magnitude is right and then some — an order containing no verb and no target destroys 18,160 men — but it is reachable only for Murat, mid-campaign, and BOTH corpus twins address Ney, who cannot charge on any board.** The twins as written can never observe the harm the row exists to prevent.

---

## 2. What is false

| claim | measured |
|---|---|
| *"The live parser reads … as a cavalry CHARGE"* → implies the pinned utterances are at risk | Both twins name **Ney**. `charge` on Ney is refused at 0 AP for free by `_execute_charge`'s `is_reckless_cavalry` gate (`combat_executor.py:7753`). The harm needs Murat. |
| *"then flip the two live twins to `action: unknown`"* | **Not expressible.** See §4 — the eval engine returns before the `action` check on any `success:false` entry, and an unknown parse is always `success:false`. |
| *"a deliberate two-call live eval"* | **Four**, not two: both twins are `world: "any"`, and `worlds_for_entry` runs them on legacy AND 1805 unless `--world` is passed. Measured. |
| *"The prompt has no rule for a deed no action models"* — implied as the whole gap | The **schema already carries half the fix**: `providers.PARSE_TOOL`'s `action` description (lines 164–172) already says *"or the string \"unknown\" … an order you cannot map to any action. \"unknown\" is a legitimate answer; never substitute a guessed action for it."* That is PC15-8's fix. The **prompt** never repeats it outside the delegation rule. |
| FA-73's parent row's *"optionally one prompt line"* | The machine record (`_id: FA-73`, `_status: NARROWED_2026_09_02`) marks the prompt line **optional**; slice 7 built the mandatory half. FA-S7-D1 promoted the optional half. |

---

## 3. The real seam

| what | symbol | file |
|---|---|---|
| the prompt block to edit | `build_parse_prompt` f-string, `## Valid Actions` at line **419–420**; the two existing `unknown` instructions at **442–449** | `backend/ai/prompt_builder.py` |
| the action list source | `actions_list = ", ".join(sorted(VALID_ACTIONS))` (line 401); `"unknown" ∉ VALID_ACTIONS`, `∈ META_ACTIONS` | `backend/ai/validation.py` |
| where `unknown` becomes a refusal | `CommandParser._validate_command` → `f"Unknown action: {action}"` (**parser.py:2121**), because `"unknown"` is not in `self.valid_actions` (line 756) | `backend/commands/parser.py` |
| the META bypass that lets `unknown` through validation untouched | `validate_parse_result`: `if result.action in META_ACTIONS: return result` | `backend/ai/validation.py` |
| what the player then sees | `main.py` Berthier recovery, `if not parsed.get("success") and (parsed.get("error") or "").startswith("Unknown action")` | `backend/main.py` (~3273) |
| the mock-side rule the prompt never learned | `_mentions_screening_idiom` (**llm_client.py:605**) and the `"fix "` drop (**llm_client.py:2034–2042**) — both docstrings already say *"screening is not a modelled action"* / *"falls through to unknown → Berthier asks"* | `backend/ai/llm_client.py` |
| the eval engine | `parser_eval.evaluate_entry` | `backend/ai/parser_eval.py` |

---

## 4. What the filed fix would break

### (a) The corpus half is unbuildable. Measured five ways.

`evaluate_entry` reads `expected_success = expected.get("success", True)`, checks success, then **`if not expected_success: return mismatches`** — *before* `command` is read at all. An unknown parse is always `success: False` (measured: `error='Unknown action: unknown'`, `command.action=None`).

Cross-product of the four candidate spellings × five possible model answers (`probe_unknown_shape2.py`), utterance `Ney, cover the retreat`:

| `expected` | model→unknown | →charge | →**retreat** | →repair | mock |
|---|---|---|---|---|---|
| **A** `{'action':'unknown'}` ← *the ruling verbatim* | **FAIL** | FAIL | FAIL | FAIL | FAIL |
| **B** `{'success':false,'action':'unknown'}` | PASS | FAIL | FAIL | FAIL | PASS |
| **C** `{'success':false,'error_contains':'Unknown action'}` | PASS | FAIL | FAIL | FAIL | PASS |
| **D** `{'not_action':'retreat'}` ← *today* | **FAIL** | PASS | **FAIL** | PASS | FAIL |

- **A fails in every world**, including the one the fix creates.
- **B passes vacuously.** Proven (`probe_vacuity.py`): `{'success':false,'action':'unknown'}` also PASSES against `Kutuzov, attack Mack` (*"commands for Russia, Sire"*) and `Zzzqqx, attack Mack` (*"Marshal 'Zzzqqx' not found"*). The `action` key is never read.
- **B also reds a pin by name.** `tests/test_command_robustness_cr1_eval_harness.py::TestCorpusHygiene::test_failure_entries_carry_no_dead_command_expectations` allows only `{success, error_contains, not_action}` on a failure entry — verbatim simulation (`probe_hygiene.py`) returns `RED → never-evaluated keys {'action'}`. That pin was written for exactly this mistake (`ney-xyzzy` carried a dead `marshal` key).
- **D is today's row and it goes RED the moment the fix works** — implicit `success: True` versus a refusal.

Note the schema advertises what the engine cannot check: `test_expected_actions_are_known_ids` explicitly allows `'unknown'` in its `known` set.

### (b) The prompt line's real blast radius, and the two rows it can break

A prompt line can only move a parse that reaches the model. Census of every live-run corpus evaluation (`probe_escalation.py`):

```
live-run evaluations : 604   (49 mock_only rows skipped)
  ESCALATE to model  :  26   (4.3%)
  short-circuit      : 578   (543 at conf ≥ 0.7, 33 PARSE-NEG refusals, 2 at 0.75)
```

Of the 26, **9 evaluations / 7 ids expect SUCCESS** — these red if the model starts answering `unknown`:

| id | utterance | fast action / conf | risk |
|---|---|---|---|
| **`cr5-deleg-aggressive-ney-resolves-live`** | `Ney, deal with Mack` | `unknown` / 0.5 | **HIGH** |
| **`cr5-deleg-cautious-davout-resolves-live`** | `Davout, deal with Mack` | `unknown` / 0.5 | **HIGH** |
| `emperor-address` | `Emperor, attack Mack` | `attack` / 0.55 | low (named verb) |
| `naey-attack-wellington` | `Naey, attack Wellington` | `attack` / 0.55 | low |
| `soutl-attack-mack` | `Soutl, attack Mack` | `attack` / 0.55 | low |
| the two FA-73 twins | — | `unknown` / 0.5 | the target of the fix |

**The two rows most at risk from this fix are the other two `live_only` rows.** The Personality Rules block already carries two "set action unknown" instructions and a catch-all (*"a delegation you cannot classify resolves to action unknown"*); a third, broader "answer unknown" rule sits directly beside them and raises the model's prior for `unknown` on exactly the delegation family. Those two rows are the CR-5 aggressive/cautious arms' only live evidence.

### (c) It doubles the live API cost for this class
Measured (`probe_callcount.py`), `Ney, fix bayonets` through `/command`:

```
model answers 'charge' : parse=1  berthier=0  TOTAL 1
model answers 'unknown': parse=1  berthier=1  TOTAL 2
```

`main.py` passes `skip_llm=bool(parsed.get("llm_error"))`; a *healthy* parse returning unknown has no `llm_error`, so `generate_berthier_recovery` makes a full second call. This is a **pre-existing** two-call class (the literal-delegation rule already produces it) that the fix **widens** — and it contradicts the CLAUDE.md environment note *"at most ONE blocking LLM call per request"*. No test pins it (`test_berthier_skip_llm_uses_template_without_api_call` covers only the error path), so nothing goes red — but the claim in the docs is already too broad.

### (d) Drive-by, found while measuring the engine: 20 corpus rows carry an INERT `not_action`
`probe_notaction_vacuity.py`: **20 rows** have `success:false` **and** `not_action`; mutating `not_action` to `"ZZZ_NOT_AN_ACTION"` leaves **20/20 passing identically**. The hygiene pin *allows* `not_action` on a failure entry, but `evaluate_entry` returns before the check. Affected: the whole `parseneg-*` family (8), the whole `fa7-*` delay family (9), `fa6-*` (3). Every one of them reads as *"and it must not become an attack"* and asserts nothing of the kind — the `success:false` carries the whole contract.

---

## 5. Pins that flip

Current state, all green (`-p no:randomly`):

| selection | result |
|---|---|
| `tests/test_command_robustness_cr1_eval_harness.py` | **686 passed** |
| `test_pc15_8_delegation_nation_arm.py` + `cr5` + `cr5b` + `berthier_recovery` + `cr3_llm_modernization` | **269 passed** |
| `test_playtest_command_and_ui_2026_07_18.py` + `test_parse_negation.py` | **197 passed** |
| `python -m backend.ai.parser_eval` (mock) | **675/675, 4 live_only skipped** — corpus = **436 rows**, 49 `mock_only`, 4 `live_only` |

| change | flips |
|---|---|
| prompt line only | **NOTHING.** No test asserts the absence of such a line. `test_prompt_literal_row_names_the_no_guess_action` is a substring-presence check (`assert 'set action "unknown"' in src`) — unaffected. Mock CI never builds a live parse prompt (`_should_fallback_to_llm` returns False at `provider_name == "mock"`). |
| corpus twins → `{'success':false,'action':'unknown'}` | **`TestCorpusHygiene::test_failure_entries_carry_no_dead_command_expectations` REDS by name** |
| corpus twins → `{'action':'unknown'}` | nothing in mock CI (rows are `live_only`, skipped) — but the next `--live` run **fails both, guaranteed** |
| corpus twins → `{'success':false,'error_contains':'Unknown action'}` | hygiene green, eval green, non-vacuous |
| add a negative few-shot | no count pin exists; `test_few_shot_coverage_of_previously_uncovered_verbs` / `test_strategic_examples_teach_base_actions` / `test_few_shots_use_live_roster_names` are presence/absence checks. Use `{m1}` placeholders — a literal `Wellington`/`Grouchy`/`Drouot`/`Rhineland` reds `test_few_shots_use_live_roster_names` and `test_fogged_live_world_teaches_generic_not_wellington`. |
| moving the `not_action` check above the early return | would make 20 currently-inert rows real; safe (a failed parse has `command={}`, so `action` is `None` and never equals the forbidden value) |

**No CI ever runs `--live`.** Grep across `tests/`, `tools/`, `scripts/`, `.github`: `--live` appears only in docstrings and one corpus note. The four `live_only` rows are a manual instrument, so a flipped twin that is wrong stays wrong silently.

---

## 6. Series / harness risk: **ZERO, structurally**

`grep -n "parse\|prompt\|CommandParser\|/command\|llm"` over `tests/test_ai_intent_threat_migration.py` (1,160 lines, `BASELINE_SERIES` at :877) and `tests/test_combat_sweep_metrics.py` returns **no matches in either file**. Both drive `WorldState` directly; neither issues a typed command. `prompt_builder` is reachable only from `LLMClient._parse_with_live_provider`, which `_should_fallback_to_llm` short-circuits whenever `provider_name == "mock"` — the state both harnesses run in. A prompt-text edit and a corpus-JSON edit are invisible to them by construction, not by luck. No re-record, no flip-arm.

---

## 7. Recommended build shape

**1 — The prompt line, but sited where `unknown` is already a word.** Do **not** hang it under `## Valid Actions` alone: that header prints `actions_list`, which by measurement does not contain `unknown` (it is META, not VALID) — a rule that names a value absent from the list beneath it is precisely why PC15-8 had to fix the *schema* description instead. Put it in the Personality Rules block beside lines 442–449, or open a short block immediately after 420 that says the word:

> `"unknown"` is not in the list above and is always available: when the order names a deed no listed action models — screening or covering someone else's movement, fixing bayonets, drilling for its own sake, restoring order — set `action` to `"unknown"` and do not substitute the nearest listed action. Berthier will ask the Emperor to rephrase.

**2 — Add one negative few-shot.** All 17 `FEW_SHOT_TEMPLATES` are `matched: True`. One prose sentence against seventeen positive demonstrations is the weakest possible lever. `{"input": "{m1}, cover the retreat", "output": {"matched": false, "marshals": ["{m1}"], "action": "unknown", ...}}` — placeholders only.

**3 — Corpus: do NOT flip to `action: unknown`. Collapse instead.** The minimal honest shape, which the prompt line is what *earns*:

- delete `fa73-live-cover-the-retreat-is-not-a-retreat` and `fa73-live-fix-bayonets-is-not-a-repair`;
- remove `"mock_only": true` from `ney-cover-the-retreat` and `ney-fix-bayonets`, leaving `{"success": false, "error_contains": "Unknown action"}` on `world: "any"`.

One row per utterance, asserting the same contract in both modes — which *is* the fix: the mock's refusal becomes a promise the live layer keeps. It is hygiene-clean, non-vacuous (measured: FAILs on `retreat`, on `repair`, on `charge`), and it still catches the PS18-5 harm, because any resolved action makes `success` True. Mock total is unchanged at 675/675 (mock_only rows already ran; live_only rows were already skipped); corpus 436 → 434.

**4 — Budget the live eval honestly: 6 calls, not 2.** `--live --id ney-cover-the-retreat --id ney-fix-bayonets` = 4 (both `world: "any"`), **plus the two CR-5 delegation twins** = 2 more (`world: "1805"`). Those two are the rows this fix can break; evaluating the fix without them ships it untested against its own blast radius. Pin `--world 1805` to halve the first four only if you accept losing legacy coverage.

**5 — Rename the row.** *"reads … as a cavalry CHARGE"* is true only for Murat; the rows it points at name Ney. Retitle to the mechanism: *"the prompt never tells the model that `unknown` is an answer for an unmodelled deed"*, with the measured Murat consequence (−18,160 men from an order with no verb and no target) as the player harm.

**6 — Separate, own scope: the 20 inert `not_action` rows.** Either hoist the check above `if not expected_success: return mismatches`, or drop `not_action` from `allowed_on_failure`. Worth filing as its own row (suggest **FA-S14-1**) — it is a harness-integrity defect touching the PARSE-NEG and FA-7 families, not this gate's business.

**7 — Record, don't fix: the 1→2 API call widening,** and correct the CLAUDE.md environment claim *"at most ONE blocking LLM call per request"* — it is already false today on the literal-delegation path.