# Claims audit — commit `aa6faa01` (FA slice 2, "No Word Came") — September 4, 2026

Third of three review lenses on the slice-2 commit (R1 = the resolution and
the brakes; R2 = the question's lifecycle; R3 = every claim the landing
record makes, re-derived). All probes ran against `git archive` extractions
of 915c6a32 and aa6faa01 under the session scratch; the sweep against a
copy; nothing in the repo was touched. Findings were disposed by the
slice-2 review round ("The Word Is Owed") — see the boxed block in
`docs/BUG_FIXES.md` §Final Whole-Game Audit.

| # | Claim | Verdict |
|---|---|---|
| 1 | "Austria's six actions were six `[P0 ENGAGEMENT] -> ATTACK Massena`, 8,000 → 4,129 → 2,349 → 1,379 → 694 → 416 → 259, still standing, still asked; rail row (x3)" | **VERIFIED** on 915c6a32 (exactly those numbers). **Caveat:** "the REAL enemy phase on the shipped board" is a *staged* corner — Massena 8,000/morale 30 at Milan, Mack 60k/Charles 40k/John 30k moved to Piedmont, `nation_actions["Austria"]=6`, seed 21 — the ambient run never produced it. The phase code path is real. Same staging on aa6: 2 attacks, captured on the second. |
| 2 | Eight-arm attribution: arm 0 byte-identical; A at [29]; B at [19]; C inert; AB==ABC; AC==A; BC==B; France 25/Austria 12 (was 26/10); fallen {Murat}; captured {Lannes, Massena, Ney, Bennigsen, Buxhowden, Davout, Mack, ArchdukeJohn, Paget}; A: 22/14; B: 29/6 with Lannes/Massena/Ney "a few hundred men each" | **VERIFIED** in every particular (B: Lannes 206 / Massena 410 / Ney 288 at Podolia). |
| 3 | WO-10 note: 17→18 collapses, 6 `Leon→Napoleon` + 12 `Gascony→Ney`, ungated series re-recorded, writes 31/11 → 34/16 | **VERIFIED**. |
| 3b | "Ney stands one turn longer in the south" | **HALF WRONG.** He does survive one turn longer — but at Bohemia→Franconia, NORTH of Vienna. Also the series-pin note's "(every WO-10 collapse falls at turns 6–27)" was stale by one: the 18th fell at turn 28. *(Both corrected in the review round.)* |
| 4 | WO-9 note: "a French corps that is captured rather than ground to dust changes the courts' spare actions from turn 29 on, and Switzerland's courting arrives two turns later" | **WRONG as attribution.** Capped rebellion turn by lever: arm 0 → 33, **A alone → 30, B alone → 30, AB → 35**. The +2 was an A×B interaction, not the capture alone; Switzerland's loyalty already differed by turn 25 (B's [19] divergence). *(Corrected in the review round.)* |
| 5 | ai_v_sweep: "turn 36 carried Prussia both hardening and easing"; "the prior board never had two consecutive producing turns" | **VERIFIED.** |
| 6 | "the gate sits under `should_check_objection`, which already excludes both" (cancel, `_strategic_execution`) | **VERIFIED — but the same predicate also has `not is_strategic_command`, so the gate never saw a strategic order.** The substantive finding; fixed by the review round (the gate is hoisted above the predicate for every marshal-bearing verb). |
| 7a | tests "(63)" | **WRONG — 61** collected. *(Corrected.)* |
| 7b | "32 mutations, 32 killed, 0 inert" | **VERIFIED** (re-run on an extracted copy). |
| 7c | suite green | **CONSISTENT, not independently reproduced green** (clean extraction collects 19,767 = 19,763 + 4 skipped; the one repo failure was a mid-edit artefact of the parent session). M1–M7 11/11 on the clean tree; ruff clean. |
| 8 | FA-1 row's test | **Covered** (both arms, never a third time standing, sovereign, lever, shipped-board). |
| 8 | FA-16 row's test (1)–(3) | (1) behaviour holds through the endpoint — **but the slice's own endpoint test pinned only the RETIRED path**; (2) covered; (3) sovereign by construction. *(The live promotion arm was added in the review round.)* |
| 8 | FA-35 row's test | **Half covered.** Stub latch pinned; "toward the capital" asserted as measured only. |
| 8 | FA-N13 / FA-N68 / FA-N25 | **Covered.** |
| 8 | FA-N72 | **Partly.** The row's "repeat with `ai_attack_futility = 3`" clause was neither built nor pinned; the non-stub "forever across turns" half was open with the row marked FIXED. *(Built in the review round — `P0_READS_FUTILITY`.)* |
| 9 | FA-S2-D1 wording | **VERIFIED honest** — no `raised_turn`/`raised_by_ai` exists; the row words them as a stamp to add. |

**The one substantive finding.** "No order but the answer (or cancel) reaches a marshal with a standing last stand" was WRONG for strategic orders: driven through the real `/command` endpoint on a cornered Ney with Mack *adjacent*, `Ney, march to Paris` issued a MOVE_TO and overwrote the last stand with `contact_bad_odds` (the "third destroyer" the record said was closed — still live); `Ney, march to Bavaria` marched him with the ask parked; `Ney, hold Belgium` issued a 2-AP HOLD over the question. With Mack co-located the pre-existing "engaged" rule masked it, which is why the slice's tests were green.

**Other things noticed.** CLAUDE.md said the six reproduction reports were "in STATUS"; STATUS said "in the session scratch"; they were committed nowhere *(now committed beside this file)*. `dismiss_marshal_ask`'s docstring said "one helper, five callers"; there are seven call sites *(corrected)*. On the prior board the Emperor was captured by Russia at turn 37 and was not on the slice-2 board — a delta the record did not mention. The typed-path HTTP response dropped `last_stand_pending` *(now on the allowlist)*.
