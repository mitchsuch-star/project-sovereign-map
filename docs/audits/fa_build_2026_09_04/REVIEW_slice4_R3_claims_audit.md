# Claims audit — FA slice 4 "The AI Reads the Board" (`d2ca0228`) and the slice-3 review round "The Redirect Reads the Answer" (`85130a6f`)

> Transcribed verbatim from the reviewer's return (the harness refused the report-file write); every artifact it cites is under the session scratch directory `reviewS4_R3/`. Findings were disposed by the slice-4 review round "The Board Reads Back" — see the boxed block in `docs/BUG_FIXES.md` §Final Whole-Game Audit; the record corrections listed at the end were applied in that round.

Method. `git archive 85130a6f` → `reviewS4_R3/tree` (and a second copy `tree_sweep` for the mutation sweeps); `git archive d2ca0228^` (= `16921a6b`) → `tree_pre`. Every probe ran with `cwd` + `sys.path[0]` on an extracted tree, `LLM_MODE=mock`, the mock parser (`CommandParser(use_real_llm=False)`), `PYTHONHASHSEED=0` **exported before the interpreter started** (setting it inside the process silently does nothing — my first six arms were wrong for exactly that reason and were thrown away), `SOVEREIGN_SEED=historical`, `random.seed(10000+turn)` over 40 `TurnManager.end_turn` calls. The eleven-arm attribution was reproduced with my own runner (`run_arm.py`: levers set in-process per arm, `EnemyAI._execute_action` / `_find_garrison_attack` / `_get_counter_punch_action` wrapped for counters), plus a pre-slice arm on `tree_pre` and a slice-2-board arm with the review round's three P0 levers down. Both sweeps were re-run on `tree_sweep` with only its `PY` constant pointed at the repo venv. The repo was never written to. Extraction caveat: `git archive` omits `.git` and `.env`; nothing here needed either (LLM defaults to `mock` without `.env`). Verdicts default to WRONG until reproduced. Artifacts: `arms/*.json` (+`.log`), `arms_analysis.txt`, `probe_rows_s4*.out.txt`, `probe_s3r*.out.txt`, `probe_bohemia.*.out.txt`, `probe_arrival_reach.out.txt`, `probe_fa27.out.txt`, `probe_n38.*.out.txt`, `sweep_s4.log`, `sweep_s3r.log`, `pins.log`, `row_tails.txt`.

## Claims table

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| **Counts and sweeps** | | | |
| 1 | `test_fa_slice4_…py` "(35)" | VERIFIED | `--collect-only`: 64 across the two new files = 35 + 29; all pass on the `85130a6f` extraction (75 with M1–M7's 11). |
| 2 | `test_fa_slice3r_…py` "(29)" | VERIFIED | As above. |
| 3 | Sweep `_sweep_fa_slice4.json` 20/20 killed, 0 inert, 0 broken | VERIFIED | Re-run on `tree_sweep`: `swept 20: 20 killed, 0 INERT, 0 BROKEN, 0 anchor-failures`. |
| 4 | Sweep `_sweep_fa_slice3r.json` 20/20, 0 inert, 0 broken | VERIFIED, one entry NARROWED | Re-run: `swept 20: 20 killed, 0 INERT, 0 BROKEN`. But `gd/a` deletes the `_stash_deferred_dialogue(response)` line in `main.gd` and is "killed" by `test_the_client_stashes_raises_and_drains`, a source-text grep — a text mutation killed by a text pin by construction (the project's own slice-9 lesson). 19 of 20 are behavioural kills. |
| 5 | "one inert on the first sweep" (S4) / "first pass" (S3R) | UNVERIFIABLE | No first-sweep artifact is committed. |
| **Slice 4 — the eleven-arm attribution** | | | |
| 6 | Arm 0 byte-identical to the slice-2-review-round series | VERIFIED | `arm0` on `tree` == `armPRE` (untouched `16921a6b` code) == the list recorded at `16921a6b` (`…35, 32, 29`). |
| 7 | A [5], B [4], D [14], F [13], H [24], I [29] | VERIFIED | First divergence from arm 0 measured: 5 / 4 / 14 / 13 / 24 / 29 — all exact. |
| 8 | C / E / G byte-identical | VERIFIED (identity); reasons not re-measured | Each == arm 0 byte-for-byte. The stated reasons are plausible; I did not instrument them. |
| 9 | Full tree forks at [4] with B | VERIFIED | `armALL` diverges at index 4 (62 vs 72) and equals the recorded `BASELINE_SERIES`. |
| 10 | Ending state (commit + attribution comment): France 2 / Austria 23 / Britain 28 | VERIFIED | `armALL`: 2 / 23 / 28. |
| 11 | BUG_FIXES block: "France 3 / Austria 21 / Britain 28" | **WRONG** | Measured 2 / 23 / 28; the block contradicts the commit and the comment it points at. |
| 12 | "refused actions 23 → 7 (drill 14 → 0)" (commit, comment) | VERIFIED | arm 0: 23 (drill 14, move 4, attack 2, defend 2, stance 1); ALL: 7 (fortify 3, stance 2, attack 1, move 1), drill 0. |
| 13 | BUG_FIXES block: "refused actions 23 → 6" | **WRONG** | 7. |
| 14 | "decays to ZERO from [30]" (comment) | VERIFIED | `[28]=6, [29]=3, [30]=0`, measured identical. |
| 15 | BUG_FIXES block: "decays to ZERO from [32]" | **WRONG** | Index 30. |
| 16 | "garrison orders 15 → 27" (ALL); "15 → 4" (arm A / FA-8 bullet) | VERIFIED as rung EVALUATIONS; NARROWED as "orders" | `_find_garrison_attack` non-None returns: arm 0 = 15, A = 4, ALL = 27 (`[GARRISON ASSAULT]` prints agree). Executed attacks on a garrisoned province: 7 → 2 (A), 7 → 4 (ALL). More evaluations, fewer executed assaults. |
| 17 | Captured {Bernadotte, Davout, Lannes, Massena, Murat, Napoleon, Ney, Soult}, fallen {Deroy}, Emperor captured | VERIFIED | Exactly that set; Napoleon `captured_by = Britain`. |
| 18 | Arm B: "France 6 / Austria 16, refusals 23 → 3" | VERIFIED | 6 / 16 / 28; 3 refusals. |
| 19 | Arm D: "France 20 / Austria 7 — three suicidal free blows declined" | VERIFIED | 20 / 7 / 18; three `keeps his blow` lines, all Bennigsen at Vienna, field 0.05 under floors 1.18–1.39 (ALL: eight). |
| 20 | Arm F: Paget forced out (forks [13]) | VERIFIED | Fork at 13; F alone raises refusals to 25 (drill 17). |
| 21 | Arm H: "the two 'attacking ArchdukeCharles to support …' orders" | NARROWED | Only one names Charles: Buxhowden → ArchdukeCharles (turn 23); the other is Kutuzov → Liechtenstein (turn 28). Both gone in H. |
| 22 | Arm I: "refused drills 14 → 0" | VERIFIED | I: 9 refusals, drill 0. |
| 23 | "overrun by turn 32" (commit, STATUS, CLAUDE.md) | NARROWED | France by `end_turn` index: 27 at [11], 13 at [20], 5 at [22]–[28], 3 at [29]–[31], 2 from [32]. |
| 24 | "A first re-record … wrong from [18]" | UNVERIFIABLE | No artifact. |
| 25 | "levers set in the child … as module globals" | NARROWED | Eight are module globals; `GARRISON_ASSAULT_COUNTS` is a **`CombatExecutor` class attribute** (`combat_executor.py:3210`). |
| 26 | "the runner also counts the AI's refused actions and garrison orders" | NARROWED | The committed `_emit_series` counts nothing but series/threat/provinces/belligerents; the counting runner is uncommitted. |
| 27 | "M1–M7 byte-identical WITHOUT re-record" (both commits) | VERIFIED | 11 passed on the extraction; file untouched by either commit. |
| **Slice 4 — the row reproductions** | | | |
| 28 | FA-8: 2.32 walkover under 101,000 Frenchmen; executor fought the field twice | VERIFIED | `tree_pre`: `[GARRISON ASSAULT] ArchdukeCharles attacking garrison at Munich (ratio 2.32 >= 1.21)` with four visible French corps in Munich; P4 → None; executed twice: Charles 29,000 → 19,777 → 12,658, garrison untouched (record's 19,667/12,275 = same shape, different draw). `tree`: rung → None. |
| 29 | FA-N7: John 20k vs Massena 60k at 0.33; two 15k corps → one-man 1.33 while P4 declined | VERIFIED | `tree_pre`: counter-punch → Massena, executed free: 20,000 → 11,496 retreating (record 11,443, RNG); two 15k: counter-punch → Lannes, P4 → None. `tree`: `keeps his blow — the field at Milan is 0.33 against a floor of 1.28`. |
| 30 | FA-N54: "Paget sat at or over the limit 24 marshal-turns in 40" | NARROWED | Review-round board: `turns_in_defensive_stance >= 3` on **21** turns (22 counting the fortified limit); the counter climbs to 19 uninterrupted from turn 22. |
| 31 | FA-N59: three Vienna assaults all at the full modifier | VERIFIED | `tree_pre`: 1.15 ×3, counter 0; `tree`: 1.15 / 1.035 / 0.92, counter 1/2/3, `in_combat_this_turn` True. |
| 32 | FA-R2: all fourteen refused drills one shape | VERIFIED | 14/14 "is fortified and cannot drill. Abandon fortification first." |
| 33 | FA-R1: Buxhowden→ArchdukeCharles at ALLIANCE; the review-round board has two, both Russia→Austria; "the row's four was the slice-2 board" | VERIFIED | Austria\|Russia boots at ALLIANCE inside the Third Coalition; arm 0: Buxhowden→ArchdukeCharles (t23), Kutuzov→Liechtenstein (t28). Slice-2 board: exactly four ally refusals (Bagration→Wellesley, Shrapnel→Bagration, Wellesley→Hiller, Shrapnel→Liechtenstein) plus two engaged-elsewhere. |
| 34 | FA-N6: broken 1,000-man corps went P-1 `attack Lyon` | VERIFIED (mechanism); "Lyon" is the memo's placement | Legacy fixture: `_evaluate_marshal` → `attack <the province he stands on>` at priority 0 pre-slice; `wait` post-slice. |
| 35 | FA-27: "without [the P3 yield]: `stance_change, fortify` and no square ever" | VERIFIED | `fa27/d` mutation on a copy: phase `[stance_change defensive, fortify]`, no square; shipped `[form_square]`. |
| 36 | FA-27: `[form_square, attack Murat, fortify, unfortify, attack Berry, attack Gascony]` | VERIFIED | Verbatim on `tree_pre`; on `tree` the shape runs `[attack Berry, Gascony, Guyenne, Anjou]`, no square. |
| 37 | FA-N38 "collision claim does not hold (the old pin passed because a P4.5 capture supplied the attack)" | NARROWED | Premise holds (P4 → None, counter-punch fires; old pin asserted only "some attack after form_square"), but on the shipped pre-slice board the attack after the square IS the counter-punch (`attack Murat`); the "P4.5 supplied it" reading was under the filed gate, which I did not build. |
| 38 | "the filed two-producer gate double-draws the RNG" | VERIFIED (static) | `_get_mood_adjusted_threshold` draws `random.uniform`; P4 calls it. |
| 39 | FA-N54 correction: `commission_marshal(w, nation, name)` is not the signature | VERIFIED | `def commission_marshal(world, nation: str, candidate: Dict)`. |
| 40 | "the dispatch drops non-player events" | VERIFIED (static) | `dispatch.py:2501`. |
| 41 | "Four PT-F6 pins flipped consciously" | NARROWED | Two test functions changed (three assertions). |
| 42 | WO-10 29 (5+24) / cooldowns 29 vs 7 / WO-9 23/29 / AI-V mirror re-anchored | VERIFIED | Those pin classes pass on the extraction with real sims (~2.5 s setup each). |
| 43 | "No .gd. Corpus 589/589. ruff clean. ENEMY_AI_REFERENCE updated. TestGarrisonAI re-sited." | VERIFIED | Diff stat; `parser_eval` 589/589; `ruff` clean; reference rows changed; `TestGarrisonAI` passes. |
| 44 | Method note (file truncated by a helper; three fixture faults) | UNVERIFIABLE | Process history. |
| **Slice-3 review round** | | | |
| 45 | "Sixteen literals: thirteen order-driven + three answer arms" AND "AST census: sixteen `_strategic_execution` producers incl. jealousy.py" | NARROWED — two different sixteens | Text: 13 + 3 in the two strategic files (muster re-issue included, not `_strategic_execution`). AST (my walk agrees with the committed test): 12 `strategic.py` + 3 `strategic_executor.py` + 1 `jealousy.py` = 13 order-driven + **two** answer arms + jealousy. The counts coincide; the sets do not. |
| 46 | "the attack-on-arrival arm … reached by the typed out-of-range `attack <marshal>`" | **WRONG** | That route (`combat_executor.py:4889`) mints a **PURSUE**; `_handle_move_to_arrival` is called only from `_execute_move_to` (`strategic.py:1685/1785`); no PURSUE→MOVE_TO conversion exists; a PURSUE's flag is consumed by `_execute_pursue` (`:2201/:2261`). Measured: `Davout, attack Mack` two hops off → PURSUE fights via the pursuit arm, `_handle_move_to_arrival` never called. The arm is carried only by the parser's "march to X and attack" hint on a MOVE_TO, and even then the blocked-destination ask / contact arm pre-empt it in every geometry tried — R1's "practically unreachable" stands. |
| 47 | "a first step that captured Bohemia replied `events: []`" | VERIFIED | `tree_pre` seeds 1/2/15: Bohemia → France, `world.pending_capture_choice = Bohemia`, reply `events: []`, no capture key. `tree`: battle event + `pending_capture_choice: True` + `capture_data`. |
| 48 | Stale contact minted a PURSUE, marched at 0 AP, logged and deleted it | VERIFIED | `tree_pre`: to Brabant, AP 4→4, `strategic_order PURSUE` logged, "Assault failed — orders cancelled". `tree`: retired with "Mack has marched to Flanders", nothing moved. |
| 49 | Refused redirect destroyed the order | VERIFIED | `tree_pre`: interrupted, order None; `tree`: continues / attack_refused, MOVE_TO standing. |
| 50 | Font `.import` sidecars gitignored while `.ttf` tracked — force-added | VERIFIED; NARROWED in scope | `ls-tree 16921a6b`: both `.ttf` tracked, no `.import`; `85130a6f` adds both; `.gitignore:40`. **21 other tracked `.ttf` still have no sidecar.** |
| 51 | Series + M1–M7 byte-identical WITHOUT re-record (the round) | VERIFIED | `armALL` on `85130a6f` == the `d2ca0228` series; series pin passes; M1–M7 11 passed. |
| 52 | "every seam is player-only" | VERIFIED | Producers only in `strategic*.py` + `jealousy.py`; item 51 is the behavioural proof. |
| 53 | "ONE .gd — parse harness EXIT=0 / 47 scripts, boot 0 SCRIPT ERROR" | .gd + 47 VERIFIED; EXIT / boot UNVERIFIABLE | Only `main.gd` in the stat; committed report 47 scripts / 7 scenes; no Godot run here. |
| 54 | "six green FA-N3 pins → four; seam-level pin added" | VERIFIED | Literal `if not result.get("success"):` on a copy: 4 cluster failures + the new seam pin; 135 green. |
| 55 | "FOUR engaged refusals → TWO (the other four FA-R1's)" | VERIFIED | Slice-2 board: two engaged-elsewhere (Charles→Piedmont t27, →Provence t29), four coalition-ally (t31/34/35/36). |
| 56 | "seven call sites → eight" | VERIFIED | 8 non-def `dismiss_marshal_ask(` sites. |
| 57 | "FA-R1/R2 … the rows now say so" | **WRONG** | FA-R1's seam cell still reads `get_enemies_of_nation → _find_attack_opportunity`; FA-R2's still "find which precondition the rung does not read"; only a FIXED status was appended. |
| 58 | `test_cannon_fire_investigate` flipped consciously | VERIFIED | Diff + passes. |
| 59 | Reports committed; driver amended; `deferred_dialogue`; capture tail drains; `_stash_diorama` scans rows; `retract_order_log` | VERIFIED | Files present; each wire in the diff and pinned by a passing test. |
| **Routing** | | | |
| 60 | Slice 4 marks FA-8/27/N6/N7/N54/N80/N59/R1/R2 FIXED | VERIFIED | Each row tail carries the slice-4 FIXED status. |
| 61 | Slice 4 closes **FA-N38** | **WRONG** (not recorded) | No FA-N38 row in `BUG_FIXES.md` at either commit; its only row (`DESIGN_REFINEMENT.md:21`) is byte-identical before and after `d2ca0228`. |
| 62 | The review round marks no new rows | NARROWED | Correct that it files none, but FA-N42/N48 (one arm of three), FA-34 (answer-arm stalemate), FA-68 (driver half), FA-14 (the arrival arm) were materially completed by the round and their rows point only at the slice-3 block. |

## Substantive findings (a reader acting on the record would go wrong)

**S1. FA-N38 is not closed anywhere a reader will look.** Commit, CLAUDE.md, STATUS and the block all say "FA-27 + FA-N38 closed"; the row's only home (`DESIGN_REFINEMENT.md:21`) is untouched. Fix: append the FIXED status there, naming the landing block.

**S2. The FA-R1 / FA-R2 rows still teach the wrong seam** despite the round's "the rows now say so". A builder is still sent to P4's candidate list instead of `_find_ally_support_opportunity`'s `enemies_at_dest`, and told to hunt for a precondition that is `fortified`. Fix: rewrite both seam cells from the slice-4 block.

**S3. The attack-on-arrival reachability claim is false.** `attack <marshal>` out of range mints a PURSUE that never enters `_handle_move_to_arrival` (item 46). The only carrier is the parser's "march to X and attack" hint, and the contact / blocked-destination arms pre-empt the branch. Fix: "carried only by a MOVE_TO with the parser's `and attack` hint; practically unreachable (R1-F7b); pinned by a hand-built order" — and say so in `TestTheArrivalArmReadsTheAnswer`, whose fixture sets the flag by hand.

**S4. The block's ending state contradicts the commit and the series comment** (3/21/28, 23→6, [32] vs 2/23/28, 23→7, [30]). A reader re-measuring against the block would conclude the board drifted since landing; it has not. Fix: align the block with the attribution comment.

**S5. "Garrison orders 15 → 27" counts rung evaluations, not assaults.** Executed assaults on garrisoned provinces fell 7 → 4. Fix: "rung evaluations 15 → 27; executed garrison assaults 7 → 4".

**S6. The attribution recipe cannot be followed as written.** (a) `GARRISON_ASSAULT_COUNTS` is a class attribute; (b) the counting runner is not the committed `_emit_series`; (c) `PYTHONHASHSEED=0` must be in the child's *environment* — set in-process it silently does nothing and yields a different series (measured).

**S7. Two different "sixteens" are presented as one** (text 13+3 with the muster re-issue vs AST 13+2+jealousy). The committed census test states the AST partition correctly; the block's prose does not.

**S8. One of the twenty S3R kills (`gd/a`) is a text-pin kill by construction** — 19 behavioural + 1 structural, not "20 killed" as evidence of client behaviour.

**S9. The font-sidecar fix is scoped to the two fonts the test names**; 21 tracked `.ttf` still lack a committed `.import`. Nothing breaks (Godot regenerates), but "repo hygiene fixed" over-claims the class.

## Corrections to the record (wording-level)

- BUG_FIXES slice-4 block, "The series": "France 3 / Austria 21 / Britain 28" → "France 2 / Austria 23 / Britain 28"; "refused actions 23 → 6" → "23 → 7"; "decays to ZERO from [32]" → "from [30]".
- Attribution comment, arm H: → "the two ally-support strikes on coalition partners (Buxhowden → ArchdukeCharles, turn 23; Kutuzov → Liechtenstein, turn 28)".
- Attribution comment, ALL: "garrison orders 15 -> 27" → "garrison-rung evaluations 15 -> 27 (executed garrison assaults 7 -> 4)"; the FA-8 bullet's "15 -> 4 on the ambient board" is arm A alone — say so.
- Attribution comment: "levers set in the child" → "eight module globals + the `CombatExecutor.GARRISON_ASSAULT_COUNTS` class attribute, `PYTHONHASHSEED=0` in the child's environment"; "the runner also counts …" → "an uncommitted instrumented copy of the runner counted …".
- FA-N54 (block + memo): "24 marshal-turns" → "21 at the stance limit (22 with the fortified limit) on the review-round board".
- FA-N6 (block): "`attack Lyon`" → "`attack <the province he stands on>` (Lyon on the memo's placement)".
- Commit/STATUS/CLAUDE.md: "overrun by turn 32" → "down to five provinces by turn 23, two by turn 33; the Emperor taken by Britain".
- Slice-4 block: "Four PT-F6 pins flipped" → "two `test_ai_square_thrash.py` pins rewritten (three assertions)".
- Slice-3r block "Record corrections (R3)": state both partitions — text 13 + 3 (muster in, jealousy out); AST 13 + 2 + jealousy.
- Slice-3r block / STATUS / CLAUDE.md / commit: "reached by the typed out-of-range `attack <marshal>`" → per S3.
- Slice-3r block: "the rows now say so" → correct the rows or strike the sentence.
- Slice-3r block, hygiene: add "the other 21 tracked `.ttf` remain without sidecars".
- FA-N38: append FIXED to its `DESIGN_REFINEMENT.md` row (or file a BUG_FIXES row).
- FA-N42, FA-N48, FA-34, FA-68, FA-14 rows: add "+ the slice-3 review round (block above the SLICE 3 block)".
- S3R sweep JSON: annotate `gd/a` as a source-text pin kill.
