# NEXT SESSION PROMPT — Pre-Deploy S13e part 4: the stake, the memory, the instruments (PC-R7 and part 4's F-rows)

> Overwritten each time a session hands off. Current hand-off: **October 16,
> 2026, after S13e part 3 landed** (one commit on master through the hook).
>
> **What part 3 delivered** (`SYSTEMS_REFERENCE.md` §124; owner `COALITION_SPEC.md` §6a.4; pins
> `tests/test_pc_rulings.py`):
> - **PC-R4 each court on its own war** — `settlement_scoring.court_own_pressure` (the base AND the tier read
>   the court's own pair; `court_pressure_score` on the result and every row), `settlement_baseline.
>   stake_floor_consults` (under 0.10 of the side's war: covered, not consulted — `consulted`, `material_share`,
>   `stake_display`, `overall_acceptance.covered_not_consulted`; a burdened court always consulted; an empty
>   ledger consults everyone; the senior court always signs), `ai_diplomacy.letter_writer_and_score` (the writer
>   by contribution on its own pair — F63), `letter_consenting_courts` + `courts_the_letter_carries` (the writer,
>   the suing, the stakeless; a refusing court left its war — `offer["left_at_war"]`), `treaty.can_sign`'s
>   settlement arm passes the writer; F27 / F26 (`top_blocker_detail`, `SPOKEN_BLOCKER_TIER_BASE`) / F60
>   (`gold_land_rates`) / F61 (`counsel._carry_ladder`, `carry_line`).
> - **PC-R5 what wears a court down** — `coalition.war_exhaustion_terms` / `exhaustion_clock_terms` (the seam) /
>   `war_exhaustion_rate` / `war_exhaustion_lines`; the gate's `rate`; the war row's `exhaustion_terms` /
>   `exhaustion_line` (`war_status._exhaustion_block`, no fog — F42); F31 `silent_band_white_peace`; F20
>   `p2_league_gate` + `_one_envoy_for_this_war`, `_coalition_loyalty_base` reads `coalition.COALITION_LOYALTY_BASE`.
> - **PC-R6 the war score's shape** — `diplomacy.battle_score_from_records` (decay then cap),
>   `defense_ticking_gain` (the shield down with the capital held; −1 while nothing is held),
>   `war_score_component_caps` / `war_score_fill` / `war_score_fill_lines` (`breakdown_fill` on every row and
>   the snapshot's `war_score_fill`), `trend_glyph` (F84); the snapshot's nine components and
>   `settlement_tier_scope` (F38 / F39).
> - **The rest** — F55 `concessions_as_sweeteners`; F71 `acceptance_reads_the_field`; F66
>   `settlement_helpers.newcomer_joins_the_war` (+ `BARE_DECLARATION_ENTRY_PATHS`, `world._league_forming`, and
>   `_same_side_elsewhere` — the side conflict read across instances at the validator and the attach); F77 in `check_dissolution`;
>   F79 in `congress.price`; F80 `_signed_record` live + `_league_since_summons` (the summons records
>   `league_at_summons`) at the proclamation; F64 `naval.posture_blockade_answered`; F68 `cs_closes_no_port` +
>   `continental_system_cost_if_joined`.
> - The series: `tools/_pc_s13e3_series_arms.py` (twelve seams; byte-identical on fourteen arms). The DD-1 sweep
>   A = 0 / B = 0 on ten arms; the fuzzer ten seeds × 1,000 steps, 0. The M1 / M2 frames re-shot at 5120×1440 on
>   the Vienna-held board (`docs/audits/peace_client/`; `TestPCR6::test_h` reads them; the popup's foot is
>   `m2_war_detail_scrolled`).
>
> **The seams part 4 builds on (and must not re-pin blind):** every per-court row now carries `consulted` —
> a court's VETO is the floor's business, so a part-4 clause (the compensation clause, the ally's bond) must
> decide whether it BURDENS the court (burdened = consulted); the letter's writer is the court with the largest
> share — a title ("War for Bohemia") must read the instance's `stated_reason` / purpose, not the writer;
> `war_score_fill` is the one list of caps — a new component goes there first; `_league_since_summons` reads
> great powers only.
>
> **Traps part 3 paid for:**
> - The code-health ratchet caps functions over 500 lines at 28: `build_active_wars` sat at 507 after one
>   block and is 487 with it extracted (`_exhaustion_block`); extract before you add.
> - A hold condition is FATAL every end turn: the Congress's design lets the War of the Congress brew a league
>   the sitting goes on to win (the pressburg arm's Fourth Swedish Coalition) — F80 lives at the proclamation
>   and reads great powers, not in the hold. The GE-3 arms (`test_congress_review_round.py::TestTheArmsDriven`)
>   run in ~20 s each — drive them after any Congress change.
> - `can_sign`'s settlement arm dry-runs the AI's letter: a consent read that forgets the WRITER withholds every
>   spent league's letter (SR-1d / PR-D1d / request-terms pins go red together).
> - The stake floor must never leave a table with nobody consulted (Britain alone carried at 6/50).
> - An idempotent edit script must check the NEW text, not only the old: a re-run doubled a dict key (ruff F601).
> - `coalition.py` must not be imported at `ai_diplomacy.py`'s module level (read its constants lazily).
> - The pc4 harness (`pc4_play.py start --seed-save <board>` on 8021) seeds the menu's Continue from any save in
>   `<run>/saves`; `hover <card text>` records the tooltip on the hovered button; `scroll <x> <y> down <n>`
>   scrolls a popup; stop it before the commit (the hook's engine group).
> - The series tool's down-expressions are `eval`'d lambdas over `a` / `k`: a keyword-only seam needs `k[...]`.
>
> **Nothing waits on the user** (a code-signing certificate and the UXR-4 review are theirs before S15,
> not before this part). Paste everything below the line as the opening message of a fresh session.

---

> - **The next prompt (S13e part 4), pre-decided:** read this block, `PEACE_CONUNDRUM_2026_10_15.md` §46 (J, F) and §40 J, `SYSTEMS_REFERENCE.md` §122–§124 (what parts 1–3 built: `carried_in_allies`, `court_own_readiness`, `truce_words` / `armistice_expiry_exit`, `dictated_tier` / `war_priced_indemnity`, `court_own_pressure` / `stake_floor_consults` / `letter_writer_and_score`, `war_exhaustion_terms`, `battle_score_from_records` / `defense_ticking_gain` / `war_score_fill`), and `BUG_FIXES.md` §PC rows PC-R7 and part 4's F-rows (F41, F72; the AI's memory F57, F81, F74, F75, F83; F28, F29, F30, F33; F11, F14, F45; the instruments F85, F86, F87). Build **PC-R7 (i)** first (J: the war's PURPOSE is its title on every surface — "War for Bohemia", never "vs Britain" — `settlement_routes._war_label`, `war_status.build_active_wars`' `opponent_display`, the HUD card, the popup, the wizard, the dispatch, the Charges; the table titles the same object; F41 and F72 ride it), then **size PC-R7 (ii)** at the part's head (the `territory_compensate` clause — the loser paid in a third party's province or its design pointed elsewhere — validated, scored, ratified and offered by the AI; declared goals plus composable articles; the ally's bond priced; the moderate Pressburg, Salzburg for Tyrol, authorable and carrying on the Vienna-held board): if it fits, build it; if not, it HEADS S14 and the row stays OPEN — say which in STATUS. Then the AI's memory rows F57, F81 (its part-3 half is done), F74, F75, F83; F28, F29, F30, F33; F11, F14, F45; the instruments F85, F86, F87 (the staged fixtures regenerated by a drive); and **F's reactivity re-read** — §44's ten levers re-run on the Vienna-held board, each moving at least one court's answer (E, G, H and I each added a lever) — recorded in the report as §47. Sibling sweep after each (file PC-X19 onward); a series attribution where a fix reaches the AI (`tools/_pc_s13e3_series_arms.py` is the pattern — copy to `_pc_s13e4_series_arms.py`; seams, never module levers; the ratchet caps them at 231 and the functions over 500 lines at 28 — `build_active_wars` sits at 487); the DD-1 sweep and the fuzzer re-run where a predicate moves. Mode A drives on COPIES of the turn-6 boards and the ulm turn-18 board (`tests/fixtures/pc_boards/`); never ports 8005/8006; `SOVEREIGN_PORT` 8010+ and `INK_IRON_SAVE_DIR` in the scratchpad. Commit through the hook; close with the Part IV frames re-shot on both turn-6 boards so every peace moment names the road that carries and its price, the three Part V replays passing as tests, STATUS naming S13c part 2 (CC-3) next with its prompt pre-decided, and a hand-over note. Done when: "War for Bohemia" on every surface; a carve writes the punitive record; the staged fixtures regenerated by a drive; the reactivity read — ten levers, each moving at least one court's answer; 0 OPEN §PC rows (or PC-R7 (ii) alone OPEN and heading S14); `tests/test_pc_rulings.py` green with `TestPCR7`.
