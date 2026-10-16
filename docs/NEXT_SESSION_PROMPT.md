# NEXT SESSION PROMPT — Pre-Deploy S13e part 3: the scores and the clock (PC-R4, PC-R5, PC-R6 and part 3's F-rows)

> Overwritten each time a session hands off. Current hand-off: **October 16,
> 2026, after S13e part 2 landed** (one commit on master through the hook).
>
> **What part 2 delivered** (`SYSTEMS_REFERENCE.md` §123; owners `COALITION_SPEC.md` §6a.2 / §6a.3; pins
> `tests/test_pc_rulings.py`):
> - **PC-R2 the victor's truce** — the ledger and the war's age survive the truce and the collapse
>   (`diplomacy.truce_keeps_the_ledger`, `set_diplomatic_state`'s stamp rule), exhaustion holds in a truce
>   (`coalition.truce_holds_exhaustion`; PC-X9), the two signed exits and the collapse from ONE predicate
>   (`armistice_expiry_exit`; `truce_hope_alive` read by the expiry and by P1's ask; the sureties filed at the
>   truce on the war instance), the one wording (`truce_words`; the client prints it), F69 / F82 / F87 / PC-X8.
> - **PC-R3 what the AI may dictate** — `dictated_tier` / `dictated_demands` / `dictated_settlement_clauses`,
>   `war_priced_indemnity` (a lump plus a stream with `surety_regions` held until paid — both channels), the offer
>   history on the war instance (`record_dictated_offer`, `note_dictated_refusal`, `dictated_ratchet`),
>   `refused_peace_standing` (the Charges, the petitions, the war panel's `next_letter` / `refused_peace`),
>   `successor_peace` (the regime arm on the exile story), F65 / F76's harsh register.
> - **PC-R1 (v)** — the ally's bill from the desire profile (`_desire_profile_claims_for_ally`), F81's
>   `pre_cleanup_standings`, the two Pressburgs' line (`emergent_designs.revanche_line_for_terms` /
>   `revanche_line_after`), F70's beneficiary on the hand-off; PC-X10 (the balance projection's double count);
>   PC-X11 (the HUD card's truce tooltip ran wider than the 5120 screen — `Utils.wrap_text`, one part a
>   line) and PC-X12 (the counsel's "1 turns" — `{clock_turns}`).
> - **The table's holes** F54 (the capital leads the offer rows), F56 (the preview validates), F52
>   (`settlement_validation.occupied_homeland_cession_ok`, the ONE rule; the ratifier's `take_dropped_clauses`),
>   F62 (the gold credit summed per pair); **the drafts** F13 (prisoners as one term; the losing draft eased
>   around them), F22 (the sabotage re-estimated, the flip walked back).
> - The series: `tools/_pc_s13e2_series_arms.py` (seams L / E / H / T / I; byte-identical on seven arms; the
>   exhaustion-hold seam unreached in the ambient sim). The austerlitz window: `tools/_pc_s13e2_austerlitz_drive.py`.
>   The ulm turn-18 board: `tests/fixtures/pc_boards/ulm_t18_paris_fallen.json` (Paris fallen at 15; Britain +39).
>   The Part IV M7 / M8 frames re-shot at 5120×1440 on the turn-6 board (`docs/audits/peace_client/`;
>   `TestPCR2::test_k` reads them: the letter, the card's tooltip, the popup on both turns, the wizard, the table).
>   The DD-1 sweep A = 0 / B = 0 on ten arms (3,118 promises); the fuzzer ten seeds × 1,000 steps, 0.
>
> **The seams part 3 builds on (and must not re-pin blind):** `truce_hope_alive` (the AI's ask between the
> threshold and −70 reads it — H's subsidy term and E's per-court read both touch its inputs); `dictated_tier`'s
> `DICTATED_SCORE_STEP` (70) and P8's 40 are ±100 literals G re-reads; `coalition.next_war_exhaustion` now has
> three arms (war / truce / peace) — H's occupation / subsidy / finance terms go into the WAR arm, the truce arm
> HOLDS; `calculate_concession_credit` sums gold per pair — E's "payee credited in full" stacks on it;
> `project_balance_after_settlement` moves a province from its holder (PC-X10) — the Balance of Europe reads it.
>
> **Traps part 2 paid for:**
> - The harness's backend is a code SNAPSHOT: an edit after `pc4_play.py start` is not in the running game
>   (the wizard read "1 turns" from stale code). To re-shoot after an edit: `POST /save` on the run's port
>   (lands in `<run>/saves`), `stop`, `start --seed-save <file>` on a fresh `--out` / port, "click Looks right",
>   "click Continue". A save is a wrapper — read it with `save_manager.load_game(path)["world"]`.
> - A Godot tooltip never wraps a line of its own — a long reading goes through `Utils.wrap_text` (PC-X11).
> - A new campaign-log type (`surety_returned`) moves FIFTEEN count pins (`assert len(CAMPAIGN_LOG_TYPES) == N`
>   in fourteen files + `test_iq7`'s census of them) and the SR-6c tier census (`LOG_TIER_*`): re-seat every
>   one with the flip note, in the same commit.
> - A Bash heredoc with apostrophes or `\n` breaks silently: write edit scripts with the Write tool and run them;
>   GDScript is tab-indented — splice by markers, never by a typed pattern.
> - `edit()` lists assert before writing: a stale pair aborts the whole file — keep one file per list.
> - A clause key the table's validator does not know (`surety_regions`) is an `invalid_clause_schema` refusal:
>   `settlement_scoring.CANONICAL_CLAUSE_TYPES` is where a new optional key goes.
> - `_apply_settlement_terms` never sees the war instance by object — it reads `world.war_instances[war_id]`.
> - The HTTP idiom on a board: swap `M.world`, `M.game_state["world"]` and `M.parser` together
>   (`_swap_in` in `tests/test_pc_rulings.py`); `board_env` boots the default world.
> - A pending envoy on the turn-6 saves returns no wizard rows: `_board` pops the dialogue manager.
> - The reaction summary's keys are `proposer_side_reactions` / `enemy_side_reactions`.
> - The Godot harness (`pc4_play.py`) refuses to start while any Godot runs — the suite's engine group included;
>   run Mode C after the suite.
> - The austerlitz window is seed-specific: report truce counts per seed, never as a law (both arms signed two).
>
> **Nothing waits on the user** (a code-signing certificate and the UXR-4 review are theirs before S15,
> not before this part). Paste everything below the line as the opening message of a fresh session.

---

> - **The next prompt (S13e part 3), pre-decided:** read this block, `PEACE_CONUNDRUM_2026_10_15.md` §46 (E, H, G) and §40 E / H / G, `SYSTEMS_REFERENCE.md` §122 and §123 (what parts 1–2 built: `carried_in_allies`, `court_own_readiness`, `truce_words` / `truce_hope_alive` / `armistice_expiry_exit`, `dictated_tier` / `dictated_demands` / `war_priced_indemnity`, the offer history on the instance, `occupied_homeland_cession_ok`), and `BUG_FIXES.md` §PC rows PC-R4, PC-R5, PC-R6 and part 3's F-rows (F23, F63, F71, F60, F55, F61, F20; F42, F31; F27, F26, F38, F39, F84; the coalition's shape F58, F66, F77, F79, F80; the sea F64, F68). Build **PC-R4** first (E: each court on its OWN pair at the table — the per-court base reads the court's pair score, not the side mean (`settlement_baseline.compute_per_court_acceptance`, `settlement_scoring.calculate_base_side_pressure`'s per-court read); the stake floor is `CONSULT_MATERIAL_SHARE_THRESHOLD` (0.10) — one ladder for both sides; the payee credited in full and the side at `side_gold_credit_share()` (built in part 1); the tier legitimacy reads the court's OWN tier so the −10 white-peace charge stops biting a victor in Vienna; the AI's settlement letter dry-run reads the same per-court scorer as the player's — pinned on the Vienna-held board: Britain alone reads 6/50 beside Austria's 79 on one table), then **PC-R5** (H: the +8 clock kept; occupation +1 a turn per own home province the enemy holds, subsidy −2 to the recipient / +2 to the paymaster while it flows, finance +2 while the chest is under one turn of upkeep — `coalition.next_war_exhaustion`'s terms, named, and the truce's hold from part 2 kept; the league gate reads the live rate, not the constant (`ai_diplomacy.py`'s `BREAK_RANKS_EXHAUSTION` read against the rate); the components ride the war popup — F42), then **PC-R6** (G: the caps kept, decay then cap in `calculate_war_score`; the `defense` ticking STOPS accruing for a court whose capital the enemy holds and resumes when it is regained — the shield down with Vienna held; the fill shown per component ("Battle 15/15 — full") on the war popup and the HUD; every ±100 literal re-read — P1 −40/−70, P8 40, break-ranks −50, the Congress −40, the exhausted-pair band 15), then part 3's F-rows: the two scores F63, F71, F60, F55, F61, F23, F20; the clocks F42, F31; the AI's reads F27, F26, F38, F39, F84; the coalition's shape F58 (the welded instance's leader vs the league's), F66, F77, F79, F80; the sea F64 (the blockade credits France), F68. Sibling sweep after each (file PC-X11 onward); a series attribution where a fix reaches the AI (`tools/_pc_s13e2_series_arms.py` is the pattern — copy to `_pc_s13e3_series_arms.py`; seams, never module levers; the ratchet caps them at 231); the DD-1 sweep and fuzzer re-run where a predicate moves. Mode A drives on COPIES of the turn-6 boards and the ulm turn-18 board (`tests/fixtures/pc_boards/`); never ports 8005/8006; `SOVEREIGN_PORT` 8010+ and `INK_IRON_SAVE_DIR` in the scratchpad. Commit through the hook; close with the Part IV frames that show the war popup's components (M1's tooltip, M8's popup) re-shot and read, STATUS naming part 4 next with its prompt pre-decided, and a hand-over note. Done when: Britain alone reads 6/50 beside Austria's 79 on one table; the clock's components on the war popup; the shield down with Vienna held; the blockade credits France; `tests/test_pc_rulings.py` green with `TestPCR4` / `TestPCR5` / `TestPCR6`.
