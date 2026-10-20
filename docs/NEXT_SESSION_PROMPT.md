# NEXT SESSION PROMPT — Pre-Deploy S14 part 2: PC-R7 (ii)'s second half — composed terms and the bond

> Overwritten each time a session hands off. Current hand-over: **October 20, 2026, after S14 part 1 ("the moderate
> peace" — the compensation clause) landed** (one commit through the hook — `git log -1`).
>
> **What part 1 delivered** (`SYSTEMS_REFERENCE.md` §133; the row `BUG_FIXES.md` §PC PC-R7 — first half built, OPEN for
> this part; siblings PC-X28 … X32 FIXED; pins `tests/test_pc_rulings.py::TestPCR7::test_ii_*`,
> `TestTheS14Part1Siblings`):
> - **`territory_compensate`** — `backend/game_logic/compensation.py` is the ONE module (the rule
>   `compensation_reading`, the price `table_credit` / `bilateral_value` / `harshness`, the apply arm
>   `apply_territory_compensate` both ratifiers call, the words, the candidates). Two forms read from the
>   province's holder: **paid** (a third party's frontier province a court of our side holds — Franconia, Bavaria's)
>   and **pointed** (a province a court outside the war holds, inside the compensated court's own design — the
>   Eastern Question); the pointed form suspends the designs ahead of it and licenses it through the D5 instruments'
>   records (`instruments.record_peace_compensation`, `grant_directed_sponsorship` at 0 gold).
> - **The moderate Pressburg carries** on the Vienna-held board (Tyrol for Franconia 71, with the Eastern Question
>   58; the harsh one 36); authored from the table's "Offers to <court>" rows; carried by the separate-peace hand-off;
>   asked by the beaten court's letter to the player where its desire profile values territory highly (GR5).
> - **The memory:** a compensated cession is not a partition (`record_punitive_cessions(…, offsets=…)` at all three
>   seams); the two Pressburgs' line says "compensated"; an ally made to pay with nothing gained is shut out
>   (`paid_for_the_peace`).
> - **The instruments:** `tools/_pc_s14_series_arms.py` (seams P = the letter's ask, D = PC-X30's desire names) —
>   every arm byte-identical to `BASELINE_SERIES` (unreached in the passive ambient sim); IQ-6's courted drive re-measured and attributed (Austria receptive 20 → 19 after the compensated peace — the ask held down reproduces 20); the DD-1 sweep A = 0 / B = 0 on nine arms; the fuzzer ten seeds × 1,000 steps, 0.
> - **The siblings:** PC-X28 (an offered province dropped by the hand-off), X29 (the peace-table promise), X30 (the desire profiles' legacy names), X31 (the ledger's raw clause keys), X32 (the table's bargain breach read only `regions`).
>
> **Traps part 1 paid for:**
> - The bash heredoc broke twice more on a multi-line payload (an unmatched quote in prose): every doc section and
>   every multi-line edit through the Write tool, then a short Python script that reads it.
> - `_court_demand_suggestions` sits near the 500-line ratchet: new rows go in a helper module (`compensation.
>   guided_suggestions`) and the long function gains a call, never a body.
> - The table's ratifier applies terms BEFORE the pair transitions, and the bilateral ratifier's clauses run after
>   its state write — read the war instance defensively (`compensation._sides` falls back to the pair).
> - The hand-off seed silently dropped an offered province until PC-X28: any new clause type that can be OFFERED
>   needs an arm in `_pair_substitute_seed_terms` AND a label path in `pair_substitute_dropped_clause_labels`
>   (the IGR-D census walks `_DEMAND_ADDABLE_CLAUSE_TYPES`).
> - The legacy map's names live in the desire profiles on purpose (the legacy fixtures read them): add the 1805 name
>   beside, never replace (PC-X30).
> - A manual full run from this shell inherits `PYTHONDONTWRITEBYTECODE=1`, which reds the two `fa_slice8` bytecode
>   tests — run it as `env -u PYTHONDONTWRITEBYTECODE …` (the hook's own env is clean).
> - A new clause type's readers are many (≈150 `territory_cede` sites): a read-only census agent (sonnet) listing only
>   the GAP sites found nine; brief it with the clause's exact shape in BOTH dialects.
> - `CLAUDE.md` stands 31 bytes under its 62,000-byte cap: swap its live-state rows, shorten as you swap.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14 part 2 — PC-R7 (ii)'s second half, "composed terms and the bond" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -1` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/PRE_DEPLOY_PLAN.md` §2 S14, `docs/BUG_FIXES.md` §PC row PC-R7, `docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §40 J and §46 J, `docs/SYSTEMS_REFERENCE.md` §133 (part 1 as built) and §122–§127, the War Purpose system (`diplomacy.create_war_objective`, `get_available_war_objectives`, the player's `diplomatic_executor._execute_set_war_purpose` / `_set_war_purpose_inner` and the `war_purpose_popup` the declaration stages, `settlement_scoring`'s objective alignment — `ALIGN_*`, `_term_matches_objective`), `COALITION_SPEC.md` §6a (the loyalty term) and `ai_diplomacy.coalition_break_ranks_reason` / `court_own_readiness`, `coalition._process_british_subsidy` / `projected_paymaster_subsidy` (the paymaster's subsidy the bond is priced from), and `backend/game_logic/instruments.py` (the D5 records the bond rides).

Scope — the design is pre-decided here (rule the details at the head, measured; flag any reversal):
1. **Size it at the head and write the split into the row.** If it is more than one session, the bond heads part 3 — named in the row with its pin, never a vague "later".
2. **Declared goals (Vic3's declared wargoals, §40 J):** the War Purpose popup and the AI's `war_objective` declare their articles at the declaration — the objective PLUS up to two named terms (a province of the target, an indemnity, a client) — each declared term priced at the declaration (the alarm/threat it costs, from the existing threat engine's per-province rates — derived, never invented) and stored on the war objective record (serialized; `SAVE_FORMAT_REFERENCE.md`). At the table a declared term is LEGITIMATE — it does not count toward the tier ceiling's surprise (the `TIER_LEGITIMACY_MISMATCH` read) — and an undeclared demand of the same kind is priced as now. **A declared term dropped at the peace refunds part of its cost** (half the declaration's threat, by `coalition.reduce_threat`, named on the aftermath line). GR5: the AI's declared terms ride the same record and the same refund.
3. **Composable articles at the table:** the table already composes; this part's deliverable is that the guided rows LEAD with the declared terms ("Declared at the war: Tyrol") and that the counsel prices the declared draft first.
4. **The coalition's no-separate-peace bond (Chaumont, 1814):** a priced, dated clause the paymaster pays for — when a league stands with two or more members at war with France, the paymaster (the `paymaster` design's court) may bind a member (a D5 directed record of a new `kind="bond"` beside `"neutrality"` — the payer buys the member's commitment NOT to sign a separate peace, for a term, at a subsidy per turn): the bonded member's break-ranks read (`coalition_break_ranks_reason`) tightens by the bond's strength, its own row at the table carries the bond's price as a named component, and breaking it (a separate peace inside the term) is `bargain_reneged` against the member. **France can bid for the league's cohesion:** the compensation clause or gold at the table offsets the bond's component (the loser's lever, §40 J) — priced, never a veto.
5. **Then SF-RR7 "the morning of the peace"** (SFR-B3, ruled "Europe waits on Paris"; with DDB-X4, the Congress's series arms flipping live levers) if the part has room; otherwise it heads part 3, named in STATUS.

Rules: reproduce each gap on a board before building (the Vienna-held board and the ulm board, `tests/fixtures/pc_boards/`); the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this part or heading the next); every change that reaches the AI runs the attribution arms (`tools/_pc_s14_series_arms.py`'s idiom: function seams and data seams, never a new lever) with `BASELINE_SERIES` byte-identical or every movement attributed and named; the DD-1 sign-ability sweep and the treaty fuzzer re-run where `can_sign` or a ratifier moves; the Godot parse harness if a `.gd` changes. New serialized fields: `to_dict` / `from_dict` with `.get` defaults and `tests/test_serialization_enforcement.py`. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when declared goals are declared, priced, legitimate at the table and refunded when dropped (both sides), the bond is minted by the paymaster, priced at the table and in the break-ranks read, and biddable by France — pinned in `tests/test_pc_rulings.py::TestPCR7` — the PC-R7 row is CLOSED (or names part 3 precisely), and STATUS ▶ NEXT UP names what follows with this file overwritten for it.
