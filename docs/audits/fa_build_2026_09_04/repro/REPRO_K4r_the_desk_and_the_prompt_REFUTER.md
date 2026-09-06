I have enough. Writing up.

---

# REFUTER REPORT — FA-S7-D1 (the unknown-action prompt line)

**Material context the report does not state:** the working tree is **not clean**. A slice-14 build is in flight and **the FA-S7-D1 fix is already applied** — `prompt_builder.py` +6 lines, and both live twins already flipped to `{"success": false}`. Several of the report's numbers were measured pre-fix; I say so where it matters. (`llm_client.py` is also modified, but that is FA-R4 and unrelated.)

Probes: `…/scratchpad/s14/refute_E_prompt/p{1..7}_*.py`

---

## CONFIRMED

**CLAIM — the prompt gap.** `unknown ∉ VALID_ACTIONS`, `∈ META_ACTIONS`; the list under `## Valid Actions` has 54 entries.
**MY MEASUREMENT** — `len(VALID_ACTIONS)=54`, `'unknown' in VALID_ACTIONS: False`, `in META_ACTIONS: True`. HEAD prompt contains `unknown` 5×; working tree 6×. **CONFIRMED.**

**CLAIM — both twins escalate at confidence 0.5.**
**MY MEASUREMENT** — `fast_parse` on both: `action='unknown' matched=False confidence=0.5 refusal=None`, below the 0.7 gate. **CONFIRMED.**

**CLAIM — corpus 436 / 49 mock_only / 4 live_only; mock eval 675/675, 4 skipped.**
**MY MEASUREMENT** — identical on all five figures. **CONFIRMED.**

**CLAIM — 604 live-run evaluations, 26 escalate (4.3%).**
**MY MEASUREMENT** — `604 / 26 / 4.3%`, short-circuit 578 = {conf≥0.7: 545, refusal: 33, NON_ORDER: 0}. The report's "543 + 2 at 0.75" is a sub-split of my 545. **CONFIRMED.**

**CLAIM — §4(a) cross-product (shapes A–D × five model answers).**
**MY MEASUREMENT** — reproduced cell-for-cell: A fails in all six columns; B and C pass only on the two unknown columns and on mock; D passes on charge and repair and **fails on `retreat`** and on unknown. **CONFIRMED.**

**CLAIM — the hygiene pin allows only `{success, error_contains, not_action}`, so option B reds it by name.**
**MY MEASUREMENT** — `allowed_on_failure = {"success", "error_contains", "not_action"}`, verbatim, in `test_failure_entries_carry_no_dead_command_expectations`. B leaves `dead={'action'}`. **CONFIRMED.**

**CLAIM — B is vacuous; C discriminates.**
**MY MEASUREMENT** — B passes against `Kutuzov, attack Mack` (*"commands for Russia"*) and `Zzzqqx, attack Mack` (*"not found"*); C fails both. **CONFIRMED.**

**CLAIM — 20 rows carry an inert `not_action`; families parseneg/fa7/fa6.**
**MY MEASUREMENT** — 20 candidates, `{parseneg: 8, fa7: 9, fa6: 3}`; mutating `not_action → "ZZZ_NOT_AN_ACTION"` changed **0/20** pass-fail outcomes. **CONFIRMED exactly.** `evaluate_entry` returns before the `not_action` check on a failure entry — verified by reading.

**CLAIM — Murat is the only reckless cavalryman; Ney's charge is refused free at 0 AP.**
**MY MEASUREMENT** — `is_reckless_cavalry` is True for **exactly one marshal in the entire world**, Murat (stronger than the report's "one Frenchman"). Ney: `success=False, AP 4→4, "Ney is not cavalry and cannot execute a Glorious Charge."` **CONFIRMED.**

**CLAIM — "two live calls" is really four; budget six.**
**MY MEASUREMENT** — both twins are `world: "any"` and appear in my census under `[legacy]` **and** `[1805]`; the two CR-5 delegation rows are `[1805]` only. 4 + 2 = 6. **CONFIRMED.**

**CLAIM — series/harness risk is structurally zero.**
**MY MEASUREMENT** — `grep -rn "parse|prompt|CommandParser|/command|llm"` over `test_ai_intent_threat_migration.py` + `test_combat_sweep_metrics.py` → **0 matches**. **CONFIRMED.**

**CLAIM — the prompt pins are substring-presence checks; the named selections stay green.**
**MY MEASUREMENT** — `test_prompt_literal_row_names_the_no_guess_action` is `assert 'set action "unknown"' in src`. Eval harness **686 passed**; the CR5/CR5b/CR3/berthier/pc15-8 selection **269 passed**. Both match the report. **CONFIRMED.**

**CLAIM — no CI runs `--live`.**
**MY MEASUREMENT** — `--live` appears only in docstrings and one corpus note. **CONFIRMED.**

**CLAIM — recommendation #3's shape is the right one.**
**MY MEASUREMENT — and this is the report's strongest, most load-bearing result, which it did not itself prove.** I drove a fake provider down **both** possible answer shapes:

| provider returns | route taken | final `error` |
|---|---|---|
| `matched=False, action="unknown"` | *"LLM couldn't parse command, using fast parser result"* | `'Unknown action: unknown'` |
| `matched=True, action="unknown"` | *"LLM parse successful: unknown by ['Ney']"* → META bypass | `'Unknown action: unknown'` |
| `matched=True, action="charge"` | validated | `None`, **success=True** |

Both unknown paths converge on the **identical** string, so `error_contains: "Unknown action"` is robust regardless of how the model sets `matched`. **CONFIRMED.**

---

## NARROWED

**CLAIM — "9 evaluations / 7 ids expect SUCCESS — these red if the model starts answering unknown."**
**MY MEASUREMENT** — 5/5 on the working tree; 9/7 on HEAD, because at HEAD the twins carry `{"not_action": …}` with no `success` key, so `expected.get("success", True)` counts them as expecting success. So the arithmetic is right — but **4 of the 9 are the twins themselves**, i.e. the fix's own targets, not collateral. The genuine residual blast radius is **5 evaluations / 5 ids**, of which the two CR-5 delegation rows are the only HIGH risk. **NARROWED** (headline number inflated ~2×).

**CLAIM — the mechanism is "META bypass → `_validate_command`".**
**MY MEASUREMENT** — that is one of two live paths; the other (`matched=False` → fast-parser fallback) never reaches `validate_parse_result` at all. The report describes only the second; the builder's corpus note describes only the first. Both are real. **NARROWED** — and it does not change the recommendation, because the outcome is identical.

**CLAIM — the harm: "an order containing no verb and no target destroys 18,160 men", reachable for Murat mid-campaign.**
**MY MEASUREMENT** — there is a **third gate the report never names: the model must also invent a target.** With `target=None` — the honest parse of a sentence naming no enemy — the full pipeline gives:

```
'Murat, fix bayonets' -> charge, target=None, recklessness=2, enemy co-located
   EXEC success=False   AP 4 -> 4
   "Charge requires a target! Try: 'Murat, charge [enemy name]'"   (no casualties)
```

Only when I hallucinate `target="Mack"` does it fire. The report's §1 table shows targetless refusals for Ney, then its Murat demo silently supplies a target — so "the magnitude is right and then some" **overstates reachability by one whole condition**. **NARROWED.**

**CLAIM — the figure −18,160.**
**MY MEASUREMENT** — six identical runs: −14,572 / −17,064 / −16,962 / −17,338 / −17,372 / −17,070. **RNG-dependent, and −18,160 never recurs.** Recommendation #5 wants this number in the row title; it must not be canonized. **NARROWED.**

---

## REFUTED

**CLAIM — the charge gate is at `combat_executor.py:7753`.**
**MY MEASUREMENT** — line 7753 is a bare `}`. The three `is_reckless_cavalry` sites are **4446, 6220, 7835**; the gate the report quotes is **7835**. **REFUTED** (stale by 82 lines).

**CLAIM — the Berthier seam is `main.py` (~3273), one call site.**
**MY MEASUREMENT** — two seams, **3294 and 3442**, both `skip_llm=bool(parsed.get("llm_error"))`. The 1→2 widening is real, but there are two doors, not one. **REFUTED as filed / mechanism confirmed.**

---

## What the reporter MISSED — and the builder must know

**The fix is already in the tree, and it shipped the report's *rejected* shape.** Both twins now read `{"success": false}` with no `error_contains`. Measured: that is **exactly as vacuous as option B** — it passes against `Marshal Kutuzov commands for Russia, Sire` and `Marshal 'Zzzqqx' not found`. Option C is hygiene-clean *and* discriminates. **Add `"error_contains": "Unknown action"` to both rows**; I proved above it holds on both provider shapes.

**The shipped prompt line asks the model for a field that does not exist.** It says *"is action \"unknown\" with confidence 0.3 or lower"*. `confidence` is **not** one of `PARSE_TOOL`'s 15 properties, `_to_parse_result` never reads it, and `providers.py:371` hardcodes `confidence=0.85` under the comment *"Telemetry only — there is no downstream confidence gate on an LLM result… this value can never loop back into routing."* The clause is inert; delete it.

**The line was sited exactly where the report warned not to put it.** It sits under `## Valid Actions` immediately after `{actions_list}` — a 54-item list that does not contain `unknown` — and the builder dropped the clause that reconciles that. Rendered, the block never tells the model `unknown` is available despite its absence. This is the precise failure mode that forced PC15-8 to fix the *schema* description instead.

**The prompt now quotes both acceptance utterances verbatim.** Whitespace-normalised, the built prompt contains `"fix bayonets"`, `"cover the retreat"`, `"restoring order in the ranks"` and `"screening or covering"`. The two `live_only` rows are `Ney, cover the retreat` and `Ney, fix bayonets` — so a green live eval demonstrates instruction-following on those exact strings, not generalisation to unmodelled deeds. Since **no CI runs `--live`**, this is the only acceptance evidence there will be, and it is close to circular. Evaluate at least one *unquoted* deed (`Ney, restore order in Vienna` already exists as a live-run row and expects failure).

**One hazard I hunted and cleared:** the new text tells the model *"drilling a specific manoeuvre"* is `unknown`, while `drill` **is** a valid action. Measured — every drill phrasing I tried (`Ney, drill`, `drill the men`, `drill your troops`, `drill the men in square formation`, `drill a specific manoeuvre`) fast-parses at confidence **0.9** and never reaches the model. Safe by short-circuit, not by design; if the fast parser's drill arm is ever loosened, this line becomes live.

**Recommendation #6 (the 20 inert rows) is correct and cheap, but note the safety argument is stronger than the report states:** on a failure entry `command` is `{}`, so `command.get("action")` is `None` and can never equal a forbidden action string — hoisting the check above the early return cannot red any of the 20. I verified 0/20 change under mutation today.