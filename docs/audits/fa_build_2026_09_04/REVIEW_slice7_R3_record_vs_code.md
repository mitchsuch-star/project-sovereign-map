# Slice 7 review — lens R3 "the record against the code" (at master `764d0ffc`, September 5, 2026)

Method: every claim checked against the frozen snapshot, the committed docs, the build's own probe outputs, and re-runs of the build's 102-row probe idiom on **both** the parent archive (`ea719381`) and the committed tree, mock parser asserted on every run.

## 1. Claims table (abridged to the verdicts that changed the record)

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | "82 tests" | VERIFIED | `--collect-only` → 82. |
| 2 | "40 mutations, 40 killed" | STRUCTURE VERIFIED / KILLS UNVERIFIABLE | 40 entries, every `old` occurs exactly once; kills not re-run. |
| 3–4 | "corpus 589 → 647/647", "42 new rows" | VERIFIED | 20 `any` ×2 + 22 `1805` − 4 live skipped = 58. |
| 5 | "ten `mock_only`" | **FALSE** | **21** of the 42 new rows are `mock_only` (+ the two FA-73 rows flipped). Half the new vocabulary is pinned on the mock parser only. |
| 7 | "fifteen levers" | VERIFIED | Listed by file (two share the name `QUESTION_DESK_ACTIVE`). |
| 8 | "nine address regexes (llm_client ×2, clause_guards, parser, clarification, context_carryover ×3, delegation, strategic_parser)" | **FALSE / self-contradicting** | The parenthetical sums to **ten**; 14 composition sites in all. `clause_guards.py` comment also says "the nine regexes". |
| 11 | "BASELINE_SERIES and M1–M7 byte-identical WITHOUT re-record" | VERIFIED | Both pin files untouched; ran both on the committed tree: 29 passed. |
| 12 | "General Ney, attack Mack" with Ney captured MOVED him Vienna → Bohemia | VERIFIED | Re-reproduced on the parent: AP 4→2, a PURSUE order created. |
| 13–15 | gold −128; Deroy 2 of 12; Swabia PARTIAL | VERIFIED | Probe rows. |
| 16 | "77 of 102 rows changed, every change the designed one" | COUNT VERIFIED / QUALIFIER NARROWED | ≥10 of the 77 are randomness (battle rolls, `random.choice` template switches). |
| 18–21 | circular import; Levenshtein TWO for mvoe/scuot/hodl/retreta; `is_at_war_with` absent; the tuple respected | VERIFIED | |
| 22 | "FA-D25 … its own fix column … is what landed" | NARROWED | Five FACT kinds only; "is Mack fortified?" and "should Ney attack Mack?" name known entities and stay `help`. |
| 24 | "Still refused by design … `can Ney attack Mack` without a question mark" | **FALSE as worded** | It is EXECUTED (gold −115, four corps moved). The pin says "an order". |
| 25 | "now all three share it" (the Admiralty refusal) | NARROWED | `set_fleet_posture` keeps its own pre-existing copy. |
| 28 | `Ney, fall back` was a generic MOVE_TO | VERIFIED — and created at **0 AP** (see D2). |
| 31 | fallback gate reads `NON_ORDER_ACTIONS` | VERIFIED; unrecorded consequence: `economy/treasury/finances/cheat/meta_command` fast parses no longer escalate in live mode. |

## 2. Row-status audit
BUG_FIXES: exactly the 11 rows carry the FIXED marker; no other row touched. DESIGN_REFINEMENT: FA-D20 / FA-D25 carry the BUILT cells; neighbours untouched. STATUS / CLAUDE consistent.

## 3. Omissions (material)
`tests/test_parse_negation.py` pin flipped (in the commit message only); `_DESK_ADDRESS_RE` + `"berthier"` in `ADDRESS_NON_NAME_WORDS`; two pre-existing FA-73 rows modified; the LLM-fallback gate widened (live-mode change); `shall we attack Mack` (parent: FOUGHT −111) → `help`, a designed improvement never stated; REPRO_F's requested `join forces with Saxony` pin absent.

## 4. Defects found

| ID | Sev | Where | Reproduction | Fix shape |
|---|---|---|---|---|
| **R3-1** | P3 (P2 by the slice-1 standard) — introduced | the wait arm's stay-put predicate above scout/hold/defend/fortify/move | `Davout, scout Swabia and remain there`: scouted → "holds position" (0 AP, no intel). `fortify and remain in place` → not fortified. `move to Lorraine and remain there` → stays. | Site the predicate below the order verbs. |
| **R3-2** | P2 — pre-existing root, widened | the strategic AP charge keys off the base action's `free_actions` membership | Parent already: `Davout, hold Rhineland and wait` → AP 4→4, HOLD order, "(2 AP…)" in the message; `march to Lorraine and wait there` → 0-AP MOVE_TO. Commit adds `hold Rhineland and stay put` (4→2 → 4→4). | Charge the strategic cost from the ORDER, or refuse the upgrade when the base action is free. |
| R3-3 | P3 — introduced | `question_desk._resolve` roster order | `who holds Brunswick?` → "no word of Brunswick's whereabouts"; `who holds Hanover?` → "Hanover is held by Hanover." | Region first for who_holds/who_at. |
| R3-4 | P4 | `_answer_enemy` enemies-only visibility | `where is Deroy?` (ally at FULL) → "no word". | Read the region's intel for any non-player marshal. |
| R3-5 | P4 fog | `_answer_enemy` captivity unconditional | Mack captured by Russia at unknown Moscow → "prisoner of Russia". | Gate on the cell's visibility. |
| R3-6 | P4 | main appends the warning only on success | `Ney, marc to Swabia` refused with no note. | Append on refusals too. |
| R3-7 | P3 pre-existing | possessive targets / the HOLD executor | `guard Davout's flank` → HOLD on phantom "Davout'S Flank", 2 AP. | Strip the possessive; refuse a phantom HOLD. |
| R3-8 | P4 | `\bretire\b`; "forward to" | `retire the guns` → RETREAT; `send the wounded forward to Paris` → MOVE_TO. | Anchor both. |
| R3-9..13 | record | wording/counts: "refused by design" (it fights), nine→ten, ten→21 mock_only, "every change designed", the FA-73 `charge` observation homed nowhere. | Correct. |
| R3-14 | observation | SUPPORT objection voice | "I have concerns about this order, Sire." for every routed verb. | Author a SUPPORT line. |

## 5. Not checked
The mutation kills; the live-layer `charge` reading; REPRO_F's "110 probes"; the full suite; the "2-AP" figure for the rente march.

## Disposition (by the builder, September 5, 2026)
R3-1, R3-3..R3-8, R3-14 FIXED in the review-round commit; R3-9..R3-13 corrected in the record; **R3-2 filed as `DESIGN_REFINEMENT.md` FA-R3** (a pre-existing P2 with two measured sentences — the strategic AP charge keyed off the base action is a wider change than a review round should make).
