# The Metamorphic Census — DD-0 S3 instrument 2, October 10, 2026

**Routing:** `PRE_DEPLOY_PLAN.md` §3.0 (DD-0 the instrument, item 2); rules `SYSTEMS_REFERENCE.md` §101 (the families, the applicability, the ratchet) and §100 (the parse trace every failure carries); generator `backend/ai/parser_metamorphic.py`; harness `tests/test_dd0_metamorphic_corpus.py`; CLI `tools/metamorphic_census.py`; ledger `tests/data/metamorphic_known_failures.json`.

## The method
Every ORDER row of the golden corpus (128 of the 614 — the marshal-order families, single-clause, no condition / compound / carryover / relative word) is varied by twelve families whose relation to the original is known by construction, and each variant is parsed beside its original on a fresh board per world (legacy and 1805) with the mock parser. A `same` family must not move the harness's own keys; a `refusal` family must come back as PARSE-NEG's refusal with its kind; a `question` family must not execute the order. The judgement is against the parse of the ORIGINAL, never against the row's `expected` — so a failure is the parser's. Each failure carries the variant's parse trace, and the census groups them by the trace's last stage.

## The reading
**2,100 cases, 161 failed.**

| family | relation | failed / cases | what breaks |
|---|---|---|---|
| dash_aside | same | 70 / 338 | the aside after a dash becomes part of the province: `Ney, advance on Swabia — thank you` → target `Swabia — Thank You`; `Gen. Ney, hold — thank you` → `— Thank You`; `recruit infantry in Swabbia - at once` → no target |
| second_name_role | same | 31 / 45 | `Ney, attack Mack with Lannes in support` → a SUPPORT order with a generic target: CRT-11's "in support" rule takes the whole line and the FIRST man's attack is lost — the one `same` class on this instrument that changes what is DONE |
| please | same | 30 / 453 | `please, cancel` / `cancel, please` refused; `Ney, retire, please` refused; `please, I will march to Lorraine` loses the sovereign (NP-1 reads a line that STARTS with "I"); `please, hold on, Ney, retreat` → hold |
| reason_tail | same | 18 / 338 | `Ney, hold position because the men are ready` → the province `Because The Men Are Ready` (the reason guard strips the ENEMY's reasons only); `cancel, the men are rested` refused |
| word_order | same | 8 / 77 | `retire, Ney` / `wait, Ney` refused; `protect Davout, Ney` loses the marshal; `protect Davout's flank, Ney` → Davout supports `Davout'S Flank` |
| verb_typo | same | 3 / 27 | `someone attcak Mack`, `everyone reterat` — the repair pass reads the LEADING verb position only |
| honorific | same | 1 / 83 | `Marshal Ney moves to Lorraine` — the inflected-order rewrite does not read through the honorific |
| lowercase | same | 0 / 150 | — |
| contraction | same | 0 / 1 | (one order row holds a contractable form) |
| **negation** | refusal | **0 / 190** | every `do not <verb>` / `never <verb>` on a single-clause order is PARSE-NEG's refusal with its kind |
| **modal_question** | question | **0 / 60** | every `should <Name> <order>?` is a question |
| **hedge** | question | **0 / 338** | every `maybe` / `perhaps` line is a question, a refusal or the help desk |

By the trace's last stage: `strategic · target_overrides_tactical` 90, `parser · validation_failed` 47, `mock_chain · result` 11, `strategic · strip_marshal_prefix` 8, `strategic · detected` 2, `strategic · self_target_unbound` 2, `parser · fuzzy_error` 1.

**The flip families all hold.** Nothing negated ran and no question ordered — the "0 executed-other-than-meant" half of DD-0's done-when, measured on 588 flip cases. The `same` failures are READINGS that moved, and all but one class (`second_name_role`) move the target or refuse; the second-name class changes the order itself and is S4's first row.

## What the generator was found unfair on, and excluded (the first run read 183)
- A negation inserted before a FILLER or a first person ("do not hold on, Ney, retreat", "do not I want you to move") — a negated order needs a verb; `ORDER_VERBS` gates the negation, the modal and the typo families.
- A negation on a two-clause line ("do not wait, hold position" is a HOLD) — the flip families fire on a single clause only.
- "Gen. Ney, hold" read as the name "Gen." — the address regex reads through the honorific.
- The 22 cases these exclusions removed were the generator's, not the parser's; the record keeps the number so the first run's 183 is not mistaken for a fix.

## Addendum — after the S3b fixes (the same day)
The user's "fix the bugs": the pre-parse rewrites of `backend/ai/dd0_rewrites.py` and the widened arms (`SYSTEMS_REFERENCE.md` §103) re-read on the corpus grown to 641 rows (140 order rows, 2,246 cases): **30 failed** — dash aside 70 → **0**, please 30 → **0**, honorific 1 → **0**, reason tail 18 → 8 (the comma form `, the men are rested` is left — a comma aside is any clause), second name 31 → 9 (the `take <province>` and `stand your ground` heads, where the role rewrite's order check and the take rewrite disagree), word order 8 → 10 (on the larger corpus; `retire, Ney` / `wait, Ney` / `protect Davout, Ney` — the bare verb with a trailing name), typo 3 (the `someone attcak` position). The flip families still 0 / 623. The ledger is rewritten at 30 (`LEDGER_CAP = 30`).

## The ratchet
The 161 ids were the committed ledger at the landing; after S3b it holds 30. `tests/test_dd0_metamorphic_corpus.py` pins that no failure outside it lands and that its count only falls (`LEDGER_CAP = 161`); a row that now passes is printed for pruning. **S3 changed no parser rule** — the ledger is S4's worklist, pre-attributed by stage; S4's `Reading` object (spans, not a mutated string) is the structural answer to the 90 `target_overrides_tactical` rows, and its exit predicate to the second-name class.
