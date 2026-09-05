# Slice 10 review round — R3 — the record against the code

Read-only adversarial review of master `f1fe18ab` (FA slice 10, "The
Offer on the Desk"), September 5, 2026. Every finding below was put to
TWO independent refuters whose default verdict was REFUTED — one asked
to reproduce it, one asked whether it is already guarded, unreachable,
or pre-existing. Both verdicts are transcribed under each finding.

Transcribed verbatim from the agent's structured return value.

## The lens's own summary

I read the whole 3,504-line diff, the boxed SLICE 10 block in BUG_FIXES.md, the twelve status cells, the STATUS.md top entry, the CLAUDE.md pointer, SYSTEMS_REFERENCE §32, the DESIGN_REFINEMENT FA-N17 cell, the commit message and the new test file, then re-derived every number I could. Most of the record holds, and its single strongest evidence claim is exactly reproducible: I ran an instrumented copy of the BASELINE_SERIES 40-turn loop and FA-S10-1's producer fires twice, "Bavaria turn 9, KingdomOfItaly turn 10, each resolving one war_1 pair", with the series byte-identical. Also verified: 52 tests (52 passed, 0 skipped), 41 mutations in the sweep file, parser eval 675/675, `ruff check backend/` clean, zero `.gd` (and no client script reads `amount`, `amount_offered` or a numeric `harshness`, so "zero .gd" is genuinely sufficient), zero new serialized fields (the consent keys ride a dialogue, which serializes wholesale), the fixture's per-court triple "18/10/10 against a threshold of 50" and the pre-consent `can_ratify` False / blocker "Settlement legitimacy", the FA-N45 zero (a `gold_lump` clause had no branch in the clause dialect and now prices 0.324), FA-21's "6,994 becomes 200" (6,994 is exactly 0.40 x France's 17,487 EC-W4 cap; `_reduce_p8_demands` takes it to 200 with `_force_send`), and "Bavaria eliminated on two of four unseeded boot boards" (2 of 4, at turns 6 and 10). Two figures I could not reproduce and report as UNVERIFIED rather than wrong: the suite count 20,352/4 (forbidden to run) and the boot triple "Austria 5 / Britain -2 / Russia -2" (the seeded boot board gives -13/-13/-13 at turn 1 and passes through 1/-3/-3 at t5 and 10/5/5 at t6 — the shape and the conclusion hold, the exact triple does not appear on the board I could build). The claim "four INERT on the first sweep, all repaired, none loosened" is unfalsifiable from the tree, since the first sweep's output is not committed. What I did find is a cluster of pin-quality and census claims that overstate what is actually bound: three of the 41 "kills" are a source-text grep killing a source-text mutation of the very line it greps, the FA-17 behaviour test asserts its own writes, the back-out route the record says is "pinned (FA-N15)" is not, `settlement_actions.py` carries three production changes and zero mutations, and one of the three consent keys is written and never read.

## Surviving findings (5 of 5 raw)

### [P3 → CONFIRMED] Three of the 41 "killed" mutations are killed only by a source-text grep of the line they mutate, and the FA-17 behaviour pin asserts its own writes

**Seam:** `tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py` :: `TestTheAnswerReachesTheDesk.test_a_lapsed_counter_costs_the_player_a_cooldown / test_the_lapse_cooldown_is_wired_at_the_turn_seam / TestTheOfferSpeaksTheDirection.test_the_rail_says_offering_when_the_court_pays / TestTheRecordStoresOneSidesBurden.test_the_ally_penalty_reads_the_enemys_burden`

**Evidence**

Read `tools/_sweep_fa_slice10.json`: mutations 22 (`LAPSED_COUNTER_COSTS_A_COOLDOWN` -> `False`), 31 (`" Offering {offered} gold."` -> `" Asking ..."`) and 38 (`burden_on_nation(treaty_clauses, penalty_target)` -> `0.0`) each list exactly ONE test, and in all three cases that test is a `read_text()` + substring assertion over the source. I applied each mutation to the source string in a probe (agent_probes/p15_textpins.py) and confirmed the grep flips to False in each case — so the sweep's "killed" is real but establishes only that the literal is present, exactly the WO-slice-9 trap recorded in CLAUDE.md ("a text mutation is killed by a text pin by construction"). Worse, the one test that names itself as the behaviour pin, `test_a_lapsed_counter_costs_the_player_a_cooldown`, never invokes production: it builds `manager = TM.TurnManager(world)`, then `del manager`, and the loop that writes `world.player_proposal_cooldowns[row["nation"]] = 3` / `[f"{nation}_{ptype}"] = 5` is IN THE TEST BODY, guarded by reading `TM.LAPSED_COUNTER_COSTS_A_COOLDOWN` (which the mutation does not touch). Its two asserts therefore check the test's own writes. I separately drove the real loop (agent_probes/p7_fa17_live.py: fixture_t20 + a queued `counter_offer_response` + a full `TurnManager.end_turn`) and measured Russia 2 / Russia_peace 4 — i.e. the production code does set 3/5 and `advance_turn` then decays it, so the FIX is sound; only the pin is not. Grep confirms no other behavioural coverage: nothing in tests/ asserts the rail's "Offering" clause, and the only caller of `apply_separate_peace_penalties` in tests (`test_bph_c_fallout_conflicts.py:220`) passes a hard-coded 0.4, so nothing pins which harshness `_ratify_treaty` feeds it.

**Failure scenario**

A later slice edits `TurnManager.end_turn`'s lapse loop (say, moves the counter branch above `if nation:` so `nation` is empty, or drops the `player_proposal_cooldowns` write while leaving the comment and constant in place), or changes `burden_on_nation(treaty_clauses, penalty_target)` back to summing both sides while leaving the call spelled the same, or renames the rail clause. The suite stays green and the next sweep still reports 41/41 killed, because the greps only look for a literal. The 3-DP counter-offer treadmill FA-17 closed reopens silently, and the BPH-C ally penalty goes back to reading France's own concessions as the enemy's burden.

**Suggested fix**

Replace the vacuous FA-17 test with the real loop — the probe shape works and is 8 lines: push a `counter_offer_response`, call `TurnManager(world).end_turn({'world': world})`, assert `player_proposal_cooldowns['Russia'] == 2` and `['Russia_peace'] == 4` (post-decay), and add a lever-off arm asserting the keys are absent. Give the rail and the ally penalty behavioural arms too (build a promoted offer payload with `amount_offered` and assert the notification message contains "Offering"; ratify a peace where France concedes and assert the harshness handed to `apply_separate_peace_penalties` is the enemy's burden, via a spy). Keep the source censuses as drift guards, but do not let them be the only thing a mutation has to beat — and record in the landing block that these three kills were census kills.

**Refuter 1 — CONFIRMED (severity P3)**

CONFIRMED, with two of the finding's illustrative examples corrected (they would in fact red the census; I replaced them with five sabotages that do not).

TRUE STATEMENT: three of the slice's forty-one swept mutations — 22 (`LAPSED_COUNTER_COSTS_A_COOLDOWN` -> `False`), 31 (`" Offering {offered} gold."` -> `" Asking ..."`) and 38 (`burden_on_nation(treaty_clauses, penalty_target)` -> `0.0`) — are killed solely by a `read_text()` substring census of the line they mutate, and those three censuses are the ONLY coverage anywhere in tests/ of the three seams they guard. The test that names itself the FA-17 behaviour pin, `TestTheAnswerReachesTheDesk::test_a_lapsed_counter_costs_the_player_a_cooldown`, executes ZERO lines of the production block it describes (proven by a line tracer, not by reading): it constructs `TM.TurnManager(world)`, never calls `end_turn`, `del`s the manager, and re-implements the cooldown loop in its own body guarded by `TM.LAPSED_COUNTER_COSTS_A_COOLDOWN` — a constant mutation 22 does not touch. Its two asserts therefore check the test's own writes.

The production fixes are all SOUND — this is a test-durability finding, not a live defect. Measured on the committed t20 fixture through the real `TurnManager.end_turn`: lever ON writes Russia 3 / Russia_peace 5 (read back as 2 / 4 after `advance_turn` decays them), lever OFF writes nothing.

CORRECTIONS to the finding's failure scenario. Two of its named examples do NOT survive: deleting the `player_proposal_cooldowns` writes removes that substring from the block and reds the lapse census; "renames the rail clause" IS mutation 31 and reds the rail census. The censuses are nonetheless blind to the regressions that matter, which I demonstrated by sabotage — each of these keeps the pinned literal and passes all three pins:
 (a) `lapse["offer_type"] == "counter_offer_responseX"` — the FA-17 branch never fires, the 3-DP treadmill reopens;
 (b) the cooldowns written as `0` instead of 3/5 — same effect;
 (c) the `penalty_target = target_nation if proposer == self.player_nation else proposer` ternary inverted ONE LINE ABOVE the pinned call — the exact FA-N45 direction defect returns, France's own concessions again priced as the enemy's burden;
 (d) `treaty_clauses` doubled immediately before the pinned call — the both-sides sum FA-N45 removed;
 (e) the rail's two arms SWAPPED so `Asking` prices the concession and `Offering` prices the demand — the exact FA-N16 defect returns, and the census passes because both words are still in the block.

The absence of alternative coverage is a census, not an impression: `amount_offered` occurs in tests/ only inside this slice's file and only against `settlement_offers._offer_popup`, a different producer from the `turn_manager` rail; `"Offering"` occurs only in the census assert; the rail's message string `"has offered terms to settle"` has no test at all; and every caller of `apply_separate_peace_penalties`/`_compute_separate_peace_penalty`/`get_separate_peace_fallout_warnings` in tests/ passes a hard-coded `0.4`, with no test anywhere asserting `applied_penalties` or `separate_peace_ally` outside `test_bph_c_fallout_conflicts.py`, so which harshness `_ratify_treaty` feeds the ally penalty is behaviourally unpinned.

This is the WO-slice-9 trap the project already recorded in CLAUDE.md ("both WO-D9 pins were source-text greps, and a text mutation is killed by a text pin by construction — answered with four tests driving the real executor"), and the FA-17 pin is one notch worse than that precedent because it advertises itself as the behaviour half while `test_the_lapse_cooldown_is_wired_at_the_turn_seam` advertises itself as the census half; in fact BOTH are censuses and neither runs the loop.

SEVERITY: P3 is correct. No player-facing behaviour is wrong at f1fe18ab, and all three fixes are measurably live. The cost is that the sweep line "41/41 killed, 0 inert" overstates the assurance on three of the slice's own headline rows (FA-17, FA-N16, FA-N45), so a later slice can silently reopen them. The single sharpest sub-item — a pin that names a production behaviour and provably never reaches it — would be defensible at P2 on its own, but nothing is broken today, so P3 stands.

REMEDY SHAPE (not built, read-only review): replace the FA-17 pin's in-body loop with the drive I ran (queue a `counter_offer_response`, call the real `end_turn`, assert 2/4 with a lever-off arm asserting `{}`); assert the rail NOTIFICATION MESSAGE text produced by `promote_pending_settlement_offers` for a paying court rather than grepping the f-string; and drive `_ratify_treaty` on a two-sided clause list, capturing `apply_separate_peace_penalties`' third argument, so the direction — not the call spelling — is what is pinned.

<details><summary>What the refuter ran or read</summary>

All probes under scratchpad/agent_probes/, repo never written, tree clean at f1fe18ab throughout.

1) SWEEP SEMANTICS. Read `tools/mutation_sweep.py`: `subprocess.run([PY, "-m", "pytest", *m["tests"].split(), "-q", "--tb=no", ...])` — a mutation is run against ONLY its nominated node ids, so "killed" is scoped to those. Read `tools/_sweep_fa_slice10.json` (41 entries): index 22 -> `test_the_lapse_cooldown_is_wired_at_the_turn_seam`, index 31 -> `test_the_rail_says_offering_when_the_court_pays`, index 38 -> `test_the_ally_penalty_reads_the_enemys_burden`, one test each.

2) THE THREE PINS ARE CENSUSES. `grep -n "read_text\|def test_" tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py` returns exactly three `read_text` sites besides the fixture loader — lines 767, 951, 1059 — the bodies of precisely those three tests. Each is `source.split(anchor)[1]...` + `assert "<literal>" in block`.

3) r_census_grep.py — applied each mutation as an in-memory string edit of the real source (repo untouched) and re-ran the census bodies:
   baseline: lapse (True,True,True) / rail (True,True) / ally (True,)
   mutation 22 -> lapse (False,True,True)  census FAILS
   mutation 31 -> rail  (True,False)       census FAILS, "Offering" occurrences in mutated block = 0
   mutation 38 -> ally  (False,)           census FAILS
   => the three kills are real but purely lexical.
   Same probe, "literal kept / behaviour broken": deleting both cooldown writes -> census (True,True,False) FAILS (so the finding's own example (a) is wrong); SWAPPING the two rail arms -> rail census (True,True) STILL PASSES.

4) r_census_grep2.py — sharper sabotages, all keeping the pinned literal:
   (a')  cooldowns written as 0 instead of 3/5        -> lapse census STILL PASSES
   (a'') `offer_type == "counter_offer_responseX"`    -> lapse census STILL PASSES
   (b')  `penalty_target` ternary inverted            -> ally  census STILL PASSES
   (b'') `treaty_clauses` doubled before the call     -> ally  census STILL PASSES

5) r_trace_pin.py (decisive on the tautology). Located the FA-17 branch and its two writes by CONTENT, not line number (turn_manager.py lines 181 / 184 / 188), installed a `sys.settrace` line tracer scoped to `game_logic/turn_manager.py`, and ran the single node id `...::TestTheAnswerReachesTheDesk::test_a_lapsed_counter_costs_the_player_a_cooldown` with `-p no:randomly`.
   OUTPUT: "1 passed in 1.85s / pytest rc: 0 / production FA-17 lines executed during the pin: NONE".
   The pin passes without entering the code it names.

6) r_live_fa17.py (is the fix sound?). SOVEREIGN_SCENARIO popped, LLM_MODE=mock, INK_IRON_SAVE_DIR redirected to scratchpad/agent_saves. Loaded tests/fixtures/playtest_saves/fixture_t20_ambient.json via WorldState.from_dict, cleared cooldowns, pushed a `counter_offer_response` for Russia with context proposal_type "peace", ran the REAL `TurnManager(w).end_turn()` twice with `TM.LAPSED_COUNTER_COSTS_A_COOLDOWN` toggled.
   OUTPUT: lever ON -> {'Russia': 2, 'Russia_peace': 4}; lever OFF -> {}.
   Production writes 3/5 and `advance_turn` decays them; the lever is causal. Independently reproduces the reviewer's measurement.

7) NO ALTERNATIVE COVERAGE (greps over tests/, .py only):
   - `amount_offered` -> only tests/test_fa_slice10_...py (popup payload tests via settlement_offers, not the turn_manager rail).
   - `Offering` -> only the census assert at line 955 (other hits are unrelated docstrings).
   - `has offered terms to settle` -> backend only, zero tests.
   - `INCOMING_SETTLEMENT_OFFER` in tests -> test_settlement_incoming_offers.py builds its OWN notification and asserts only the type.
   - `burden_on_nation` in tests -> the function-level `test_burden_reads_the_direction` plus the line-1062 census; no call-site coverage.
   - `apply_separate_peace_penalties` / `_compute_separate_peace_penalty` / `get_separate_peace_fallout_warnings` in tests -> every call passes a literal 0.4 (test_bph_c_fallout_conflicts.py).
   - `applied_penalties` / `separate_peace_ally` outside test_bph_c -> zero hits.
   - `lapse_pending_offers` -> read `backend/models/dialogue_manager.py::lapse_pending_offers`; it writes no cooldowns, so the FA-17 pin's asserts cannot be incidentally satisfied by production.

No git mutation, no full suite, no mutation_sweep run, no repo file written.

</details>

**Refuter 2 — NARROWED (severity P3)**

Real, this commit's responsibility, but smaller than filed and with NO current production defect.

WHAT SURVIVES (the core, unguarded): the FA-17 pair. `test_a_lapsed_counter_costs_the_player_a_cooldown` genuinely asserts its own writes — it builds `TM.TurnManager(world)`, immediately `del`s it, and executes the cooldown loop in the test body guarded by a read of `TM.LAPSED_COUNTER_COSTS_A_COOLDOWN` (a module constant the mutation does not touch, so it is inert against mutation `deliver/d`). Its partner `test_the_lapse_cooldown_is_wired_at_the_turn_seam` is the sole killer and is a source grep — and its window is WORSE than the finding says: `source.split("lapse_pending_offers()")[1].split("def ")[0]` measures 15,022 chars / 293 lines, i.e. the whole remainder of `end_turn`. It therefore detects only wholesale deletion of the FA-17 block; `3` -> `0`, a dropped `= 3` write, an inverted condition, or a wrong lapse key all pass both tests. A behavioural pin was trivially available: my 25-line probe (fixture_t20 + push a `counter_offer_response` + a real `end_turn`) measured Russia 2 / Russia_peace 4.

WHAT NARROWS (two of the three legs are partly guarded):
- `record/e`: the finding's stated failure ("goes back to reading France's own concessions as the enemy's burden") WOULD red. `burden_on_nation`'s direction semantics are behaviourally pinned by `test_burden_reads_the_direction`, and `_ratify_treaty`'s real path is driven by `test_a_gold_peace_no_longer_stores_zero` and `test_a_concession_is_never_booked_as_harshness`; the grep additionally binds the exact call text `burden_on_nation(treaty_clauses, penalty_target)`. The only escape is a change that preserves that call text — e.g. swapping `penalty_target`, which is a PRE-EXISTING (BPH-C) context line this commit did not touch.
- `dir/e`: the `amount` / `amount_offered` split IS behaviourally pinned (`test_a_concession_is_not_announced_as_a_demand`, `test_a_real_demand_still_reads_as_a_demand`). Only the rail sentence is grep-only, and its real hole is narrower than "renames the rail clause": an Asking<->Offering swap leaves both words in the window (measured: Asking x2, Offering x1) and passes.

NO PRODUCTION DEFECT: I verified the fix works end to end. `_gold_clause` reads `if amount: Asking / elif offered: Offering`, over payload fields that are behaviourally pinned; `harshness = burden_on_nation(treaty_clauses, penalty_target)` reads correctly; and the lapse cooldown fires on a real turn. This is a test-quality / future-regression-risk finding only. It IS this commit's (all three pins are new), it IS the project's own named recurring failure mode (CLAUDE.md WO-slice-9: "a text mutation is killed by a text pin by construction"), and the 41/41 sweep figure is correspondingly softer than it reads — but the concrete exposure is one pair, not three.

<details><summary>What the refuter ran or read</summary>

1) Read `tools/_sweep_fa_slice10.json` in full: mutations `deliver/d`, `dir/e`, `record/e` each name exactly one test, and each of those three tests is a `read_text()` + substring assert in `tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py`.

2) Read `test_a_lapsed_counter_costs_the_player_a_cooldown` (tests/test_fa_slice10...py, class TestTheAnswerReachesTheDesk). Verbatim: it pushes the dialogue, calls `lapse_pending_offers()`, does `manager = TM.TurnManager(world)`, then a loop `if (TM.LAPSED_COUNTER_COSTS_A_COOLDOWN and row["offer_type"] == "counter_offer_response"): world.player_proposal_cooldowns[row["nation"]] = 3; ...= 5`, then `del manager`, then asserts `== 3` and `== 5`. `manager.end_turn` is never called. Mutation `deliver/d` edits the `if (LAPSED_COUNTER_COSTS_A_COOLDOWN` line inside `backend/game_logic/turn_manager.py`, not the module constant, so this test is inert against it.

3) Coverage census (Bash grep over tests/): `apply_separate_peace_penalties` appears in tests only at test_bph_c_fallout_conflicts.py:220/232 with a hard-coded 0.4 and at the slice-10 grep. `amount_offered` appears in tests ONLY in the slice-10 file. Every other test mentioning `counter_offer_response` (test_bugfix_popup_chain, test_offer_lifetime, test_bugfix_session7, test_settlement_gate4_leg1_fixes, ...) exercises accept/reject or lifetime, never a lapse through a real `end_turn` asserting `player_proposal_cooldowns`.

4) Production probe (scratchpad/agent_probes/p_s10_pins.py; INK_IRON_SAVE_DIR set to the scratchpad, SOVEREIGN_SCENARIO popped, no parser touched so no API billing): loaded tests/fixtures/playtest_saves/fixture_t20_ambient.json via WorldState.from_dict, cleared player_proposal_cooldowns, pushed {"type":"counter_offer_response","target_nation":"Russia","context":{"proposal_type":"peace"}}, ran the REAL `TM.TurnManager(world).end_turn({"world": world})`. Output: `cooldowns after real end_turn: {'Russia': 2, 'Russia_peace': 4}` — i.e. production writes 3/5 and advance_turn decays them. The FIX is sound; only the pin is not.

5) Grep-scope probe (scratchpad/agent_probes/p_s10_grep_scope.py): lapse block after `split("def ")[0]` = 15,022 chars / 293 lines, with LAPSED_COUNTER_COSTS_A_COOLDOWN x1 and counter_offer_response x1 (so deletion is caught, mutation of the values is not). Rail window (`for offer in promoted_offers:`[:2000]) = 42 lines, Offering x1 / Asking x2 / amount_offered x1 (so an Asking<->Offering swap passes). world_state.py contains `apply_separate_peace_penalties` twice (import + call) and the [:900] window after the FIRST does contain the exact call text (grep binds correctly).

6) Reading `backend/models/world_state.py` around the separate-peace block and the slice10.diff: the `penalty_target = target_nation if proposer == self.player_nation else proposer` line is unchanged context (pre-existing BPH-C), so the only residue escaping the record/e grep is not this commit's introduction.

</details>

### [P3 → CONFIRMED] "the back-out route ... pinned (FA-N15)" is false — settlement_actions.py carries three production changes, zero new tests and zero mutations

**Seam:** `backend/game_logic/settlement_actions.py` :: `_action_return_to_settlement_terms / _apply_scope_replace_confirm`

**Evidence**

FA-N4's status cell says "The two seams the design named as owed — `submit_settlement_for_review` and the back-out route — are covered by the same rule and pinned (FA-N15)". Grep of the slice's own test file returns ZERO hits for `return_to_settlement_terms` / `back_out`; FA-N15's pin (`test_submit_for_review_no_longer_collides_with_the_mail_behind_it`) drives `submit_settlement_for_review` only. The 41 mutations in `tools/_sweep_fa_slice10.json` touch settlement_routes, settlement_staging, settlement_offers, settlement_baseline, settlement_ratify, settlement_helpers, dialogue_manager, main, turn_manager, mailbox_payloads, diplomatic_templates and world_state — `settlement_actions.py` appears in none of them, although the slice deleted a `pop()` in two of its functions and added the `dialogue_mode=` argument in a third. The FA-N18 "found in passing" fix is half-pinned the same way: `test_the_scope_chooser_carries_the_callers_dialogue_mode` asserts only that the chooser's `incoming_request` carries "PROPOSE" (the producer side, in settlement_staging, which mutation 6 covers); nothing asserts the mode of the dialogue that answering "Replace" produces. I drove that end to end (agent_probes/p12_scope_replace.py, fixture_t20): two PROPOSE stagings -> `settlement_scope_replace_confirm` -> `replace_current_scope_draft` -> head is `settlement_confirm` with `dialogue_mode: PROPOSE`, `blocking: False`. The fix works today; nothing observes it. Pre-existing tests (test_settlement_gate4_leg1_fixes.py:1930ff) do exercise `return_to_settlement_terms`, so a plain break is caught — but not the mail-behind-it property the cell claims is pinned.

**Failure scenario**

Someone re-adds `world.dialogue_manager.pop()` to `_action_return_to_settlement_terms` (it is the obvious symmetry with every other dialogue-consuming arm, and its removal is justified only by a comment), or drops `dialogue_mode=str(incoming_request.get("dialogue_mode") or "REVIEW")` from `_apply_scope_replace_confirm`. Both regressions ship green: backing out of a review with a settlement offer queued behind it promotes the letter into the collision check and re-attaches a dialogue the manager no longer holds (FA-N15's exact symptom, every button `stale_dialogue`), and answering "Replace" on a PROPOSE flow lands a BLOCKING REVIEW with empty terms and no Return-to-terms option (FA-N18's exact symptom).

**Suggested fix**

Either add the two pins — a back-out from a war_2 REVIEW with a war_1 offer queued, asserting no `cross_war_settlement_collision` and that the handed-back dialogue IS the manager's head; and an end-to-end scope-replace asserting `dialogue_mode == "PROPOSE"` and `blocking is False` on the resulting head — plus two mutations in `settlement_actions.py`; or correct the FA-N4 cell to say the back-out route is covered by the rule but not pinned.

**Refuter 1 — NARROWED (severity P3)**

The finding's FACTS are all correct and I reproduced every one of them; its FAILURE SCENARIO is half wrong, and the half that is wrong is the half it leads with.

TRUE (verified): the commit makes three production changes to `backend/game_logic/settlement_actions.py` — a deleted `world.dialogue_manager.pop()` in `_action_submit_settlement_for_review`, the same deletion in `_action_return_to_settlement_terms`, and a new `dialogue_mode=str(incoming_request.get("dialogue_mode") or "REVIEW")` argument in `_apply_scope_replace_confirm`. The slice's own test file names none of the latter two seams (grep for `return_to_settlement_terms` in `tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py` returns zero). `tools/_sweep_fa_slice10.json` holds 41 mutations across 12 files and `settlement_actions.py` is in NONE of them (counted by loading the JSON). And the FA-N4 status cell does say verbatim "The two seams the design named as owed — `submit_settlement_for_review` and the back-out route — are covered by the same rule and pinned (FA-N15)", while `test_submit_for_review_no_longer_collides_with_the_mail_behind_it` drives only `submit_settlement_for_review`. So the cell's word "pinned" is inaccurate for the back-out route, and both unswept changes survive the whole neighbourhood green.

WRONG — the back-out half of the failure scenario is NOT reachable. The finding predicts that re-adding the pop to `_action_return_to_settlement_terms` reproduces "FA-N15's exact symptom, every button `stale_dialogue`" because the promoted letter enters the collision check. It cannot, on this commit, because THIS SLICE'S OWN PRIMARY FIX removed it: `settlement_draft_dialogue_types()` excludes `incoming_settlement_offer`, so a promoted offer is not a rival draft and SC-26 never fires; and the staging tail's same-war REPLACE arm is now gated on that same draft set, so an offer-headed manager falls to `preempt` and the letter is re-queued rather than dropped. Measured directly (probe below, committed t20 fixture, REVIEW for war_1 mounted over Britain's standing offer): with the fix and with the pop re-added the arm is IDENTICAL on `success` (True both), `error` (None both), mounted `dialogue_mode` (PROPOSE both), `blocking` (False both), carried terms (1 both), the letter's survival (present both), and — the exact invariant FA-N15 is about — `handed_back.dialogue_id == manager head` (True both). The ONLY observable delta is mail ORDER: the queue goes `[incoming_settlement_offer, ally_settlement_petition]` with the fix and `[ally_settlement_petition, incoming_settlement_offer]` with the pop. That is a cosmetic reordering, not FA-N15. Re-adding that pop today ships green because it is very nearly inert, not because a real regression is unobserved.

RIGHT, and the whole of the finding's real weight: the `dialogue_mode` half IS a live, observable, wholly unpinned fix. Emulating its removal (make `build_settlement_confirm_dialogue` drop the kwarg when the caller frame is `_apply_scope_replace_confirm`) turns the answer to "Replace" on a PROPOSE flow from `dialogue_mode: PROPOSE`, `blocking: False`, actions `[settlement_dial_harsher, settlement_dial_generous, submit_settlement_for_review, suspend_settlement_editor]` into `dialogue_mode: REVIEW`, `blocking: True`, 0 terms, actions `[author_gold_indemnity_terms, author_gold_per_turn_terms, seek_bilateral_peace, seek_armistice_instead, open_war_detail, back_out_settlement]` — FA-N18's stated symptom exactly, a blocking empty review with no way back to the terms — and 2,258 tests stay green. The slice's `test_the_scope_chooser_carries_the_callers_dialogue_mode` asserts only the PRODUCER side (`chooser["incoming_request"]["dialogue_mode"] == "PROPOSE"`, which mutation 6 of the sweep covers in `settlement_staging`); `tests/test_settlement_scope_replace_confirm.py`, the file that exists for this exact route, contains not one occurrence of `dialogue_mode`, `blocking`, `PROPOSE` or `REVIEW`.

So: severity P3 stands, but it is a P3 about ONE seam, `_apply_scope_replace_confirm`, not three; the correct one-line title is "the scope chooser's `dialogue_mode` carry is unpinned and unswept — removing it silently restores the FA-N18 blocking-empty-REVIEW", with a secondary P4 note that the FA-N4 status cell overstates FA-N15's reach over the back-out route. One further correction to the finding's own reasoning: it says the back-out pop's "removal is justified only by a comment" and that pre-existing tests would catch "a plain break" — the route IS exercised (my mutation fired 6 times across the corpus), so the pre-existing coverage is real; what it does not observe is a property that, on this tree, no longer differs.

<details><summary>What the refuter ran or read</summary>

All runs from the repo root against the working tree at f1fe18ab, `.venv/Scripts/python.exe`, mock parser only, no repo file touched.

1. FACTS. `python -c "import json,collections; d=json.load(open('tools/_sweep_fa_slice10.json')); print(collections.Counter(m['file'] for m in d))"` → 41 mutations over settlement_offers(9), dialogue_manager(5), settlement_routes(4), settlement_staging(4), settlement_ratify(3), main(3), diplomatic_templates(3), settlement_baseline(2), settlement_helpers(2), turn_manager(2), mailbox_payloads(2), world_state(2). `settlement_actions.py`: 0. `grep -n "return_to_settlement_terms|scope_replace|dialogue_mode" tests/test_fa_slice10_...py` → 11 hits, none naming the back-out route; the only chooser test asserts `(chooser.get("incoming_request") or {}).get("dialogue_mode") == "PROPOSE"`. `grep -n "dialogue_mode|blocking|PROPOSE|REVIEW" tests/test_settlement_scope_replace_confirm.py` → no output. `grep -o` on docs/BUG_FIXES.md returns the "…and the back-out route — are covered by the same rule and pinned (FA-N15)" sentence verbatim.

2. BEHAVIOURAL PROBE (scratchpad/agent_probes/p_refute.py, committed `tests/fixtures/playtest_saves/fixture_t20_ambient.json` via `WorldState.from_dict`, no end turns, no parser). Seam A: stage a REVIEW for war_1 over the fixture's standing Britain offer, then call `handle_settlement_dialogue_action(action="return_to_settlement_terms", dialogue=head)` twice — once as shipped, once with the dispatch entry wrapped to `world.dialogue_manager.pop()` first. Output, fixed vs mutated: success True/True; error None/None; handed_back_id 25/25 with handed_is_head True/True; post head `settlement_confirm war_1 PROPOSE blocking=False terms=1` in BOTH; queue `['incoming_settlement_offer','ally_settlement_petition']` vs `['ally_settlement_petition','incoming_settlement_offer']`. Seam B: two PROPOSE stagings on war_1 with different covered sets produce `settlement_scope_replace_confirm`; answering `replace_current_scope_draft` gives, fixed vs mutated (kwarg dropped by caller-frame check): mode PROPOSE/REVIEW, blocking False/True, actions `[dial_harsher, dial_generous, submit_settlement_for_review, suspend_settlement_editor]` vs `[author_gold_indemnity_terms, author_gold_per_turn_terms, seek_bilateral_peace, seek_armistice_instead, open_war_detail, back_out_settlement]`.

3. "DOES IT SHIP GREEN". Private out-of-repo pytest plugin (scratchpad/agent_probes/refuter_p3_sa/p3plug.py, loaded with `-p p3plug` via PYTHONPATH; it counts its own firings and prints the count at sessionfinish, so an inert plugin cannot fake a pass). Corpus = every tests/*.py matching settle|diplo|dialog|offer|mail|slice10|carve|ux_fixes|petition|paradox = 78 files. Baseline: 2258 passed. `P3MUT=pop`: "[p3plug] mutation fired 6 time(s)", 2258 passed. `P3MUT=mode`: "[p3plug] mutation fired 1 time(s)", 2258 passed. (An earlier version of this run used a plugin file in the shared agent_probes root that a CONCURRENT reviewer overwrote mid-session; I discarded that result and re-ran everything from a private subdirectory with a unique env var — the numbers above are from the clean re-run.)

No git mutation, no repo edit, no full suite, no mutation_sweep.

</details>

**Refuter 2 — CONFIRMED (severity P3)**

CONFIRMED, with one correction to the failure scenario and one addition that makes the finding sharper than filed.

WHAT IS TRUE AS FILED. All three `settlement_actions.py` changes are introduced by f1fe18ab (parent a1ed5c9d has the pops at both arms and no `dialogue_mode` kwarg at the scope-replace call). The file appears in NONE of the 41 rows of `tools/_sweep_fa_slice10.json` — every other changed backend file is represented, `settlement_actions.py` is not. And the FA-N4 status cell's "the back-out route … pinned (FA-N15)" is false: `return_to_settlement_terms` has zero hits in the slice's test file, and both changes are measurably inert against the whole settlement test neighbourhood.

CORRECTION TO THE FAILURE SCENARIO. The finding says re-adding the pop makes "backing out of a review with a settlement offer queued behind it promote the letter into the collision check." That specific geometry is ALREADY GUARDED — by this slice's own primary rule, which is itself well pinned. With an `incoming_settlement_offer` queued behind the draft I re-added the pop by hand: `_mounted_settlement_dialogue` returns None (the letter is mail, not a draft), staging succeeds, no collision, and the staging tail's preempt arm re-queues the offer intact. So the offer geometry is not where the guard earns its keep.

The geometry where it DOES is a queued cross-war settlement DRAFT, and that is production-reachable through ordinary player verbs, because the three read-out preempts in `diplomatic_executor` are unconditional and a PROPOSE draft is non-blocking: Open Settlement for war_1 (PROPOSE) → "Talleyrand, assess our situation" (advisory `preempt` pushes the draft into the queue) → Open Settlement for war_2 (no collision now, because the advisory is current) → Submit for Review → Return to terms. Shipped: success, the war_2 PROPOSE surface comes back. With the pop restored: `cross_war_settlement_collision`, and the player's war_2 REVIEW draft is gone — war_1's draft is mounted in its place. So the removal is a real guard on a reachable path, observed by nothing.

THE ADDITION — the sharper half. FA-N15's own pin does not kill its own mutation either. I restored the pop in `_action_submit_settlement_for_review` and ran `test_submit_for_review_no_longer_collides_with_the_mail_behind_it`: it PASSES. For the same reason as above — with the letter no longer a draft, the pop-vs-no-pop ordering is not observable through that test's assertions. The landing record's "pinned by the invariant that catches the whole class: the dialogue an arm hands back IS the manager's head" is therefore false for the mutation it names, on BOTH arms. What actually caught the submit-side pop was an unrelated pre-existing test (`test_settlement_gate4_preflight_pf1.py::TestLosingBaselineValidity::test_generated_baseline_is_validated_before_staging_propose_and_submit`), incidentally. So the correct statement of the row is not "one of two arms is pinned" but "neither arm's pop removal is pinned by this slice; one is caught by accident, the other by nothing."

FA-N18's half is confirmed exactly as filed. The producer test asserts only that the chooser carries `dialogue_mode: PROPOSE`; nothing asserts the consumer reads it, and the pre-existing scope-replace tests all stage without a mode, so the `or "REVIEW"` fallback keeps them byte-identical. The path is a normal player one — `diplomatic_executor` stages Open Settlement with `dialogue_mode="PROPOSE"`, so PROPOSE is the ordinary conversational front, not the debug-only typed route.

SEVERITY. P3 holds. No shipped behaviour is wrong — both fixes work today, which the finding says itself. What is wrong is (a) a reachable guard with zero coverage in a file the sweep never touched, (b) a "0 inert" mutation claim that could not have covered this file, and (c) two false "pinned" claims in the record. The remedy is small: one test per arm on the geometry that actually distinguishes them (a queued cross-war DRAFT, not a queued offer), and an assertion on the mode of the dialogue that answering "Replace" produces.

<details><summary>What the refuter ran or read</summary>

All probes read-only, under scratchpad/agent_probes/, repo untouched, INK_IRON_SAVE_DIR redirected, no full suite, no mutation_sweep.

1. rf_backout_pop.py — fixture_t20, war_2 draft mounted, Britain's real war_1 `incoming_settlement_offer` pushed behind it, then the removed pop performed by hand:
   after the re-added pop, current = incoming_settlement_offer war_1
   _mounted_settlement_dialogue -> None
   RESTAGE with pop: True err= None
   VERDICT collision? False
   => the offer geometry the finding names is already guarded by the slice's primary rule.

2. rf_why2.py — production-only route to the geometry that does bite (stage war_1 PROPOSE; `DiplomaticExecutor._execute_diplomatic_advisory`; stage war_2 PROPOSE; submit for review; back out):
   advisory: True | current: advisory | queue: [('ally_settlement_petition','war_1'), ('settlement_confirm','war_1')]
   open war_2: True None | current: settlement_confirm war_2
   [SHIPPED]     BACK OUT -> success=True  err=None                          head=settlement_confirm:war_2:PROPOSE
   [POP-READDED] BACK OUT -> success=False err=cross_war_settlement_collision head=settlement_confirm:war_1:PROPOSE

3. rf_scope_mode.py — FA-N18 consumer, chooser reached and "Replace" answered:
   [SHIPPED] type=settlement_confirm mode=PROPOSE blocking=False actions=[settlement_dial_harsher, settlement_dial_generous, submit_settlement_for_review, suspend_settlement_editor]
   [MUTATED] type=settlement_confirm mode=REVIEW  blocking=True  actions=[author_gold_indemnity_terms, author_gold_per_turn_terms, seek_bilateral_peace, seek_armistice_instead, open_war_detail, back_out_settlement]

4. In-memory mutation plugins (rf_mutplug_lens.py / rf_mutplug_scoped.py — patch module attributes at pytest_configure, no file edits), run over tests/test_settlement*.py (42 files) + the slice file + test_incoming_offer_deferral_no_leaks.py:
   baseline                                   -> 1006 passed
   RFMUT=pop  (back-out pops first)           -> 1006 passed   [INERT]
   RFMUT=pop2 (submit pops first)             -> 1005 passed, 1 failed: test_settlement_gate4_preflight_pf1.py::TestLosingBaselineValidity::test_generated_baseline_is_validated_before_staging_propose_and_submit  [caught only incidentally, by a pre-existing test]
   RFMUT2=mode_scoped (drop dialogue_mode at _apply_scope_replace_confirm only, frame-scoped so the other two callers are untouched), + test_ux_fixes_2026_08_23.py -> 1061 passed  [INERT]

5. Targeted: RFMUT=pop2 against the FA-N15 test alone ->
   tests/test_fa_slice10_...::TestTheOfferIsMailNeverADraft::test_submit_for_review_no_longer_collides_with_the_mail_behind_it — 1 passed.
   (The class runs with no skips: TestTheOfferIsMailNeverADraft = 13 passed.)

6. Readings. `git show a1ed5c9d:backend/game_logic/settlement_actions.py` — pops present at :1686 and :1718, no `dialogue_mode` at the scope-replace call => all three changes introduced by this commit. `tools/_sweep_fa_slice10.json` = 41 rows over 12 files; settlement_actions.py absent. `diplomatic_executor.py:2850` stages Open Settlement with dialogue_mode="PROPOSE"; the advisory/mission/feasibility `preempt` calls carry no hard-stop or type guard; `mount_over_mail` and `open_flow` do NOT queue a draft (they push behind it / replace it), which is why the advisory route is the reachable one. grep: no test asserts `dialogue_mode` on the result of `replace_current_scope_draft`; the pre-existing back-out tests (test_settlement_gate4_leg1_fixes.py::TestPairSubstituteDisabledRendering) assert only `restaged["success"] is True` with nothing queued, so the pop is invisible to them.

</details>

### [P3 → NARROWED] The consent-lapse guard is narrower than published: `consent_offer_id` is written and never read, and a save-loaded dialogue that outlived its offer keeps its consent

**Seam:** `backend/game_logic/settlement_ratify.py` :: `consenting_courts_for_ratification (and settlement_staging.stage_settlement_confirm's consent_offer_id write)`

**Evidence**

The docstring of `consenting_courts_for_ratification` says consent lapses "If the staged terms are no longer the offered ones — an edit, a restage, A SAVE-LOADED DIALOGUE THAT OUTLIVED ITS OFFER", and SYSTEMS_REFERENCE §32 repeats it verbatim ("an edit, a restage, a save-loaded dialogue that outlived its offer"). The guard is `_term_lists_equal(dialogue['consent_terms'], dialogue['settlement_terms'])`, and `DialogueManager.to_dict` deep-copies the whole dialogue, so both keys travel together and are always equal after a round trip. Measured (agent_probes/p16_consent_saveload.py): accept Britain's fixture offer, clear `world.pending_settlement_dialogues`, `WorldState.from_dict(world.to_dict())` -> `consenting_courts_for_ratification(staged)` still returns ['Austria', 'Britain', 'Russia'] with `consent_offer_id: settlement_offer:war_1:3:1` intact. A repo-wide grep for `consent_offer_id` returns exactly four hits — one write in `settlement_offers` (stage_kwargs), the parameter and the write in `settlement_staging` — and NO reader in backend/, godot-client/ or tests/. FA-3's status cell and SYSTEMS_REFERENCE §32 both present it as one of three keys that are "honoured at BOTH scoring seams" / "display-and-scoring keys"; only two of the three participate in anything.

**Failure scenario**

A reader trusts the published guarantee and assumes a consented review cannot outlive its offer. It can: the staged review is a serialized dialogue carrying its own consent, and the only thing that revokes it is an edit to the terms. `consent_offer_id` — the one key that could implement the published rule, by checking the offer is still live — is dead state on every save. Concretely, a consented review saved and reloaded after the offer has been withdrawn by the producer still ratifies on the courts' consent, with the record saying it should not.

**Suggested fix**

Pick one and make the record match. Either read `consent_offer_id` in `consenting_courts_for_ratification` (lapse when the offer is no longer known to the world, via the existing `_is_offer_known_to_dialogue_manager` / `pending_settlement_dialogues`) and pin it, or delete the key and strike the "a save-loaded dialogue that outlived its offer" clause from both the docstring and SYSTEMS_REFERENCE §32, leaving the honest two-case rule (an edit, a restage).

**Refuter 1 — NARROWED (severity P4)**

The two mechanical observations are true, but the failure scenario is unreachable and the implied fix would re-open the P1 this slice closed. Severity drops P3 -> P4: this is a documentation over-claim plus one unread provenance key, not a guard that is narrower than it needs to be.

TRUE (established):
1. `consent_offer_id` has no reader. Repo-wide grep (all file types, .git/.venv excluded) returns exactly four code hits: one write in `settlement_offers.handle_incoming_settlement_offer_action` (stage_kwargs) and the parameter + the write in `settlement_staging.stage_settlement_confirm`. Nothing in backend/, godot-client/ or tests/ reads it.
2. A save/load never lapses consent. `DialogueManager.to_dict`/`from_dict` both `copy.deepcopy` the whole dialogue, so `consent_terms` and `settlement_terms` travel together and `_term_lists_equal` is trivially satisfied after a round trip. Reproduced.
3. Therefore the parenthetical example in `consenting_courts_for_ratification.__doc__` and in SYSTEMS_REFERENCE §32 — "an edit, a restage, a save-loaded dialogue that outlived its offer" — is wrong in its third item, and §32's "three display-and-scoring keys ... and they are honoured at BOTH scoring seams" over-claims for `consent_offer_id`, which participates in neither seam and is displayed nowhere.

REFUTED (the substance):
4. "A save-loaded dialogue that outlived its offer" is not an anomaly — it is the state of EVERY consented review, on the same tick it is staged, before any save. The accept arm calls `_consume_offer_dialogue` and `_remove_pending_settlement_offer` on the SAME call that stages the review (slice rule 2, "stage first, consume only on success"). Measured on the t20 fixture: immediately after a successful accept, live incoming_settlement_offer dialogues = [], no dialogue in head or queue carries the offer id, and there is no pending offer store entry — all before `to_dict` was ever called.
5. So the stated failure scenario — "a consented review saved and reloaded after the offer has been withdrawn by the producer" — has no producer. The offer is already gone at t+0; there is no later state in which it can be withdrawn out from under the review, and no observable difference between "offer withdrawn" and the normal path.
6. The reviewer's implied remedy is backwards. If `consent_offer_id` were read as a liveness check — "the one key that could implement the published rule, by checking the offer is still live" — `consenting_courts_for_ratification` would return [] on 100% of consented reviews, which is precisely FA-3, the P1 this slice exists to close (`can_ratify` False, blocker "Settlement legitimacy", no ratify option).
7. The rule that actually governs behaviour is stated correctly in both places ("if `settlement_terms` no longer equals `consent_terms` ... it lapses") and the guard implements exactly that, with hard stops and the ratify-time `validate_settlement_terms` revalidation as the orthogonal defences (§32 says so: "consent says a court is willing, never that a clause is legal or a pair is still at war").

Residue worth fixing, cheaply and in docs only: delete "a save-loaded dialogue that outlived its offer" from both the docstring and SYSTEMS_REFERENCE §32 (a save/load does not lapse consent, and outliving the offer is the designed normal state), and either demote `consent_offer_id` in §32 from "display-and-scoring key" to unread provenance, or drop the field — the offer identity is already echoed separately as `result["offer_id"]`.

<details><summary>What the refuter ran or read</summary>

Read (snapshot at f1fe18ab):
- `settlement_ratify.consenting_courts_for_ratification` — guard is `consenting_courts` non-empty AND `_term_lists_equal(consent_terms, settlement_terms)`; nothing else.
- `settlement_validation._term_lists_equal` — pure list/dict comparison.
- `settlement_offers.handle_incoming_settlement_offer_action` accept arm — on `result.get("success")` falsy it returns with the letter handed back; on success it calls `_consume_offer_dialogue(world, dialogue)` then `_remove_pending_settlement_offer(world, offer_id=offer_id, war_id=war_id)`.
- `models/dialogue_manager.DialogueManager.to_dict`/`from_dict` — `copy.deepcopy` of `_current` and every queue entry, no key whitelist.

Grep (working tree, all file types, .git and .venv excluded): `consent_offer_id` -> 4 code hits (settlement_offers.py write; settlement_staging.py param + write) + 2 doc hits (BUG_FIXES.md FA-3 cell, SYSTEMS_REFERENCE.md §32). No reader in backend/, godot-client/ or tests/.

Probe (scratchpad/agent_probes/p_refute_consent.py, run with .venv/Scripts/python.exe from the repo root, INK_IRON_SAVE_DIR redirected, SOVEREIGN_SCENARIO popped, no parser and no end turn so nothing was billed and no autosave touched). Built the world from the committed tests/fixtures/playtest_saves/fixture_t20_ambient.json via WorldState.from_dict, took Britain's current offer, called handle_incoming_settlement_offer_action(action="accept_settlement_offer") directly, then round-tripped WorldState.from_dict(world.to_dict()). Output verbatim:

  offer_id on the letter : settlement_offer:war_1:3:1
  covered                : ['Britain', 'Austria', 'Russia']
  BEFORE accept, live offers: (['settlement_offer:war_1:3:1'], None)
  accept success         : True
  staged type            : settlement_confirm
  staged consent_offer_id: settlement_offer:war_1:3:1
  consent at t+0         : ['Austria', 'Britain', 'Russia']
  AFTER accept, live offers: ([], None)
  dialogues still carrying that offer_id: []
  offer id present in pending store: False
  after save/load, staged type: settlement_confirm
  after save/load, consent    : ['Austria', 'Britain', 'Russia']
  after save/load, offer_id   : settlement_offer:war_1:3:1
  after save/load, live offers: ([], None)

The two lines that decide it are "AFTER accept, live offers: ([], None)" and "dialogues still carrying that offer_id: []" — printed BEFORE any serialization. The offer is gone the instant the review is staged, so the review outlives its offer by construction, and the reviewer's save/load result (which I reproduced identically) is the intended behaviour rather than a leak. Consulting `consent_offer_id` for liveness would return [] on this very case, which is the FA-3 dead affordance.

</details>

**Refuter 2 — REFUTED (severity P4)**

The failure scenario is refuted and the proposed remedy is harmful; only a P4 documentation/hygiene residue survives.

REFUTED (1) — the scenario is unreachable. A consented review can never coexist with its offer: on a successful stage the accept arm runs `_consume_offer_dialogue` (dialogue_manager.remove_matching) AND `_remove_pending_settlement_offer` immediately after the `if not result.get("success")` early return, so the offer named by `consent_offer_id` is gone from both stores the same instant the consent is stamped — not after a save, at birth. There is no "withdrawn by the producer" state: the producer's one-active-offer guard re-opens so it can mint a NEW offer with a different id, which is not a withdrawal of the consumed one.

REFUTED (2) — the proposed use of the key would re-open the P1 this commit closes. Because every consented review outlives its offer by construction, reading `consent_offer_id` as an offer-liveness check would evaluate False on turn one for every consented review, refuse every consented ratification, and restore FA-3 (the dead coalition-peace affordance). `tests/test_fa_slice10...::test_the_ratification_actually_signs_the_peace` would red.

REFUTED (3) — the published rule is terms-equality and is implemented exactly. SYSTEMS_REFERENCE §32 reads "if `settlement_terms` no longer equals `consent_terms` (an edit, a restage, a save-loaded dialogue that outlived its offer) it lapses" — one condition, three labels; the staging comment scopes it explicitly as "a save-loaded dialogue WHOSE TERMS NO LONGER MATCH". Only the ratify docstring's em-dash list reads loosely.

REFUTED (4) — the substantive worry (a stale consented review force-signing after the world moved) is guarded twice, and consent bypasses neither. Before consent is read, `ratify` runs `revalidate_staged_settlement`, then `validate_settlement_terms(..., world=world, war_instance=war_instance)` ("the terms we staged no longer hold against the present situation"), then a fresh `calculate_common_peace_acceptance`; `ratification_blocked` begins with `fresh_hard_stops or has_unknown_hard_stop`, and consent only suppresses the score/verdict arm. The §11.4 per-court gate re-runs as well.

SURVIVING RESIDUE (P4, introduced by this commit): `consent_offer_id` is write-only provenance — four hits repo-wide (one write in settlement_offers' stage_kwargs, the parameter and the write in settlement_staging.stage_settlement_confirm, one doc mention), no reader in backend/, godot-client/ or tests/, and no pin. SYSTEMS_REFERENCE §32's "three display-and-scoring keys ... honoured at BOTH scoring seams" over-reads by one: two are honoured, the third is provenance riding the payload. Fix is a one-word doc correction (say the third key is provenance) or deleting the key; not a behavioural defect.

<details><summary>What the refuter ran or read</summary>

Probe (read-only, mock-free — no parser touched, no turn advanced, INK_IRON_SAVE_DIR pointed at the scratchpad):
scratchpad/agent_probes/refute_consent_offer_id.py — load tests/fixtures/playtest_saves/fixture_t20_ambient.json via WorldState.from_dict, take the queued incoming_settlement_offer, call settlement_offers.handle_incoming_settlement_offer_action(world, action="accept_settlement_offer", dialogue=offer). Output:

  offer from queue: True
  offer_id: settlement_offer:war_1:3:1   pending count before: 0
  accept success: True None
  staged type: settlement_confirm   consent_offer_id: settlement_offer:war_1:3:1
  pending entries still naming that offer: 0
  queued dialogues still naming that offer: 0
  head is the offer?  False

i.e. the consent is stamped and the offer it names already exists nowhere.

Readings:
- backend/game_logic/settlement_offers.py :: handle_incoming_settlement_offer_action — `_consume_offer_dialogue(world, dialogue)` + `_remove_pending_settlement_offer(world, offer_id=..., war_id=...)` execute unconditionally on the success path, right after the failure early-return; `_remove_pending_settlement_offer`'s docstring states removal is required so the one-active-offer-per-war guard re-opens.
- backend/game_logic/settlement_ratify.py :: consenting_courts_for_ratification — guard is `_term_lists_equal(consent_terms, settlement_terms)`; leading clause of the docstring is "If the staged terms are no longer the offered ones", the em-dash list qualifies it.
- backend/game_logic/settlement_ratify.py (ratify body) — `validate_settlement_terms(..., world=world, war_instance=war_instance)` and the fresh `calculate_common_peace_acceptance` run BEFORE `consenting_courts = consenting_courts_for_ratification(dialogue)`; `ratification_blocked = fresh_hard_stops or has_unknown_hard_stop or (not accepting_leader_consents and ...)` — consent never suppresses a hard stop; the §11.4 `compute_per_court_acceptance` gate re-runs with the same consent.
- backend/game_logic/settlement_staging.py :: stage_settlement_confirm — comment scopes the save-load case as "a save-loaded dialogue whose terms no longer match".
- grep -rn "consent_offer_id" over *.py/*.gd/*.md: 4 hits — settlement_offers (write), settlement_staging (param + write), docs/SYSTEMS_REFERENCE.md. Zero readers, zero tests.
- tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py::TestTheOfferingCourtsConsent — test_the_ratification_actually_signs_the_peace drives accept -> confirm_settlement end to end and asserts PEACE for every covered court; an offer-liveness check on consent_offer_id would red it.

</details>

### [P4 → CONFIRMED] FA-21's MOVED cell mis-states the mechanism it moves the row for — `_reduce_p8_demands` prices ACCEPTANCE, never a purse

**Seam:** `docs/BUG_FIXES.md` :: `row FA-21 status cell (code: backend/game_logic/ai_diplomacy._reduce_p8_demands)`

**Evidence**

The cell (repeated in STATUS.md and CLAUDE.md) reads: "`_reduce_p8_demands` already prices the purse, taking the measured 6,994 to 200". Reading `ai_diplomacy._reduce_p8_demands`: it calls `calculate_acceptance(terms, world)` and returns early at score >= 20, then halves the gold_lump, then drops the weakest non-gold demand, then falls back to peace + 200 with `_force_send`. There is no treasury read anywhere in it. The purse is priced one function away, in the EC-W4 block of `_settlement_offer_build_terms`. I re-derived both halves on fixture_t20 (agent_probes/p6_fa21.py): France's treasury is 17,487, so the EC-W4 cap `int(treasury * SETTLEMENT_OFFER_MAX_TREASURY_FRACTION)` is exactly 6,994 — that is where the number comes from — and feeding a 6,994 gold_lump to `_reduce_p8_demands` returns `[{'type':'gold_lump','value':200}]` with `_force_send: True`. So the OUTCOME claim is verified; the stated cause is not.

**Failure scenario**

Slice 14 picks up FA-21, reads the cell, goes looking for the treasury read inside `_reduce_p8_demands` to reconcile with, and finds none — or, worse, concludes the P8 arm is already purse-aware and closes the row without building anything. The real finding (the acceptance-driven reducer shreds any purse-scaled demand to the 200 floor, so the filed fix is inert unless the reducer is taught about it) is the thing that has to survive to slice 14, and it is the thing the sentence obscures.

**Suggested fix**

Restate the cell: "a reproduction found the filed fix ships a SMALLER demand than the row wants — the EC-W4 formula's own cap on France's 17,487 purse is 6,994, and `_reduce_p8_demands`, which prices ACCEPTABILITY rather than the purse, drives that to the flat 200 floor with `_force_send`. Both the seam and the reducer need restating before it is built."

**Refuter 1 — CONFIRMED (severity P4)**

CONFIRMED (mechanism claim false, outcome claim true and understated). The FA-21 disposition cell — in docs/BUG_FIXES.md and repeated in docs/STATUS.md; NOT in CLAUDE.md, whose copy of the MOVE note omits it — states "`_reduce_p8_demands` already prices the purse, taking the measured 6,994 to 200". `_reduce_p8_demands` prices ACCEPTANCE and never reads a purse: its source contains zero occurrences of treasury / player_gold / nation_gold / FRACTION, and its only pricing oracle `diplomacy.calculate_acceptance` has zero treasury or gold terms across its full 555-line body (gold_lump is scored by a flat DEMAND_VALUES per-100 rate). It is a two-step acceptance clamp — halve every gold_lump (floor 200), drop the weakest non-gold demand, else fall back to peace + 200g with `_force_send`. The 6,994 comes from a different function on a different path: `_settlement_offer_build_terms`'s EC-W4 cap `int(payer_treasury * SETTLEMENT_OFFER_MAX_TREASURY_FRACTION)` = int(17,487 x 0.40).

The outcome half is right and is in fact WORSE than the cell implies. Measured on fixture_t20 (Britain vs France, ws +54), the reducer floors ANY lump at or above ~1,000 to exactly 200 with `_force_send=True`, irrespective of the payer's wealth: 200 to 200, 270 to 270, 500 to 250, 800 to 400, then 1000 / 1500 / 3000 / 3497 / 6994 / 17487 all to 200. A 17,487g chest and a 200g chest end identically. So the reducer is purse-BLIND in exactly the way FA-21 complains about, and the sentence says the opposite of the truth.

The thing that must survive to slice 14: `_reduce_p8_demands` runs UNCONDITIONALLY on every `harsh_peace` proposal (`if proposal.get("proposal_type") == "harsh_peace": proposal = _reduce_p8_demands(...)`), one statement after the `_build_proposal_terms` seam the filed fix touches. Therefore the filed ONE-seam fix is inert as written — any purse-scaled lump it builds is shredded to the 200 floor by the very next statement. Slice 14 must change the reducer (or teach the acceptance gold rate about the payer's purse) as well as the builder, or it will ship a no-op.

Severity P4 is correct and should NOT be raised: this is a docs-prose defect with zero runtime effect, and the cell's own next clause ("so the seam and the direction both need restating before it is built") already prevents the worst outcome of closing the row unbuilt. The realistic cost is a wasted hour hunting a treasury read that does not exist.

<details><summary>What the refuter ran or read</summary>

READ (snapshot + working tree, both at f1fe18ab):
1. `backend/game_logic/ai_diplomacy._reduce_p8_demands` — full body read. Calls `calculate_acceptance(terms, world)`; early-returns at score >= 20; halves gold_lump to `max(200, value//2)`; drops the weakest non-gold demand; falls back to `{peace, demands:[gold_lump 200]}` with `_force_send: True`. No treasury access.
2. `backend/game_logic/diplomacy.calculate_acceptance` — sliced the function body programmatically (def to next top-level def, 555 lines) and grepped for treasury / gold / player_gold / nation_gold: the only hit is a comment ("valued at the gold_lump rate") inside the prisoner_return arm. No purse term exists in the score.
3. `_settlement_offer_build_terms` — `cap = int(payer_treasury * SETTLEMENT_OFFER_MAX_TREASURY_FRACTION)`, with `SETTLEMENT_OFFER_MAX_TREASURY_FRACTION = 0.40`. This is the 6,994's real home.
4. `_generate_ai_proposal` call site: `if proposal.get("proposal_type") == "harsh_peace": proposal = _reduce_p8_demands(proposal, nation, war_score, world)` — unconditional for that arm, immediately before the score>=20 gate that `_force_send` bypasses.

RAN (probes under scratchpad/agent_probes/, repo untouched, LLM_MODE=mock, INK_IRON_SAVE_DIR redirected, SOVEREIGN_SCENARIO popped, world built via WorldState.from_dict on tests/fixtures/playtest_saves/fixture_t20_ambient.json):

refute_fa21.py output:
  turn 20 player France
  nation_gold France: 17487
  EC-W4 cap int(treasury*MAX_FRACTION) = 6994
  --- _reduce_p8_demands treasury/gold token census ---
    'treasury': 0   'player_gold': 0   'nation_gold': 0   'gold_reserves': 0   'FRACTION': 0
  Britain: state=WAR raw_ws=54
    IN  [{'type':'gold_lump','value':6994}] score -187
    OUT [{'type':'gold_lump','value':200}]  score 57  _force_send True
  Austria: raw_ws=26  -> same, score 53, force True
  Russia:  raw_ws=0   -> same, score 47, force True
  P8 harsh_peace line today: gold_demand = max(200, int(war_score * 5 * gold_mult))  -> 270 for ws 54

refute_fa21b.py output (lump sweep, Britain vs France, t20):
  200 -> 200 (57, force False)   270 -> 270 (53, False)   500 -> 250 (56, False)   800 -> 400 (33, False)
  1000 -> 200 (57, True)   1500 -> 200 (True)   2000 -> 200 (True)   3000 -> 200 (True)
  3497 -> 200 (True)   5000 -> 200 (True)   6994 -> 200 (True)   17487 -> 200 (True)

DOC LOCATIONS: `grep -rn "prices the purse|6,994|6994" docs/BUG_FIXES.md docs/STATUS.md CLAUDE.md` returns exactly two hits — BUG_FIXES.md FA-21 status cell and STATUS.md line 17. CLAUDE.md's MOVE note does not carry the claim (correcting the reviewer's "repeated in STATUS.md and CLAUDE.md").

No git mutation, no source edit, no full suite, no mutation sweep.

</details>

**Refuter 2 — NARROWED (severity P4)**

REAL BUT SMALLER, AND GUARDED IN THE SAME ROW.

What is true: `_reduce_p8_demands` does not price to the payer's purse in any sense. I established this by execution, not by reading: the identical 6,994g `gold_lump` demand scores **-187 at a French treasury of 500, of 17,487, and of 900,000** — byte-identical. `DEMAND_VALUES["gold_lump"]` is a flat `-3/100`, and the reducer's source contains no occurrence of `nation_gold`, `treasury`, or `FRACTION`. It prices ACCEPTANCE and floors at 200. In this project's own vocabulary the phrase collides head-on with the correct idiom: CLAUDE.md's EC-W4 entry uses "AI indemnities **price to the payer's purse**" for exactly the treasury-scaling the reducer does not do. So the wording is not merely loose, it means the opposite of the mechanism. This commit wrote it, so it is not pre-existing.

Four things narrow it, three of which the finding does not account for:

1. **The same row already states the mechanism correctly.** FA-21's summary column — the FIRST column a builder reads, the disputed phrase being in the LAST — says: "`_reduce_p8_demands` (:914-935) **can only lower it further toward a flat 200 floor**." That is precisely right, and it is the sentence the finding says has to survive to slice 14. It does survive; it is ten lines above the bad clause, in the same cell block.

2. **The named failure scenario is blocked by the sentence's own final clause.** The finding's headline harm is a builder concluding "the P8 arm is already purse-aware" and closing the row. The clause immediately after the disputed one reads "**so the seam and the direction both need restating before it is built**" — an explicit instruction that the row is still to be BUILT, with a restated seam. No reader gets "close it" out of that.

3. **The blast radius is two locations, not three.** The finding says the cell is "repeated in STATUS.md and CLAUDE.md". `grep -rn "prices the purse" --include=*.md .` returns **2** hits — BUG_FIXES.md and STATUS.md. CLAUDE.md, the always-loaded routing document and therefore the highest-traffic copy, carries only the correct half: "its filed fix ships a SMALLER demand than the row wants."

4. **The outcome half is right, and the finder agrees.** 6,994 → 200 with `_force_send: True`, reproduced. And 6,994 is exactly `int(17487 * 0.40)`, the EC-W4 cap, so the number's provenance is sound too.

Residual harm: a slice-14 builder loses a few minutes hunting for a treasury read that isn't there. The standing rule at the top of CLAUDE.md's live block — "reproduce before fixing, and read `_corrected` and the Sept-2 verdict BEFORE the title" — absorbs exactly that, and one probe surfaces the truth in about two minutes (it did for me).

The fix is a four-word edit in two files: "already prices the purse" → "already floors any gold demand at 200, blind to the purse". Worth making when slice 14 opens the row; not worth a commit of its own. P4 stands, and is arguably generous.

<details><summary>What the refuter ran or read</summary>

Probe: scratchpad/agent_probes/adj_fa21_purse.py, run against the working tree at f1fe18ab on the committed fixture tests/fixtures/playtest_saves/fixture_t20_ambient.json (turn 20, player France, treasury 17,487). It scores one identical peace proposal carrying `demands=[{"type":"gold_lump","value":6994}]` from Britain against three copies of the same world with France's `nation_gold` set to 500 / 17,487 / 900,000, then runs the real `ai_diplomacy._reduce_p8_demands` on it.

Output:
  DEMAND_VALUES['gold_lump'] = -0.03
  treasury=    500  score=-187  outcome=REJECT
  treasury=  17487  score=-187  outcome=REJECT
  treasury= 900000  score=-187  outcome=REJECT
  identical across purses: True
  result demands: [{'type': 'gold_lump', 'value': 200}]
  _force_send: True
  'nation_gold' in _reduce_p8_demands: False
  'treasury'   in _reduce_p8_demands: False
  'FRACTION'   in _reduce_p8_demands: False

Reading: backend/game_logic/ai_diplomacy._reduce_p8_demands (docstring + body) — calls calculate_acceptance, early-returns at score >= 20, halves gold_lump at max(200, v//2), drops the weakest non-gold demand, falls back to peace + 200 with _force_send. No treasury access. backend/game_logic/diplomacy.DEMAND_VALUES["gold_lump"] = -3/100, a flat per-100g rate; the gold_lump arm of the demand loop reads no purse.

Doc reading: `sed -n '2515p' docs/BUG_FIXES.md` (FA-21, summary column vs status column), `sed -n '12,22p' docs/STATUS.md`, `grep -n "FA-21" CLAUDE.md`. `grep -rn "prices the purse" --include=*.md .` -> 2 hits. Both hits appear as `+` lines in slice10.diff (lines 1850, 1885), so this commit introduced them; not pre-existing. `int(17487*0.40)` = 6994, confirming the number is the EC-W4 cap.

No git mutation, no suite run, no repo file touched.

</details>

### [P4 → CONFIRMED] Narrowing `_mounted_settlement_dialogue` changes three gates; the record enumerates one

**Seam:** `backend/game_logic/settlement_routes.py` :: `_mounted_settlement_dialogue`

**Evidence**

BUG_FIXES' slice-10 block and SYSTEMS_REFERENCE §32 both enumerate the blast radius as three readers of the type set and describe `_mounted_settlement_dialogue` as "the cross-war collision AND the same-war refresh/scope-replace arm in `stage_settlement_confirm`". A grep for `_mounted_settlement_dialogue` in backend/ shows THREE call sites, not one: `settlement_staging.py:3461` (the documented one), `settlement_routes.py:266` (the war-detail settlement recovery route, which refuses `settlement_collision_active` when a different war's settlement is mounted) and `settlement_validation.py:427` (the pair-substitute eligibility check, same refusal). Both undocumented sites read `mounted is not None and mounted['war_id'] not in ('', war_id_str)`, so with the offer no longer counting as mounted, a standing letter about war X stops refusing those two routes on war Y. The change is in the same direction as the slice's rule and I found no regression from it — but it is a behaviour change at two player-facing eligibility gates that neither the landing record, the row cells nor the new tests mention, in a slice whose own method lesson is "the census must be the SYMBOL".

**Failure scenario**

A later reviewer or builder reads the record's enumeration as complete and reasons about the war-detail recovery route or the pair-substitute CTA on the pre-slice assumption that a mounted offer blocks them. Nothing pins either gate's new verdict, so a future re-widening of the set (or a revert of the lever) silently moves two more surfaces than the record accounts for.

**Suggested fix**

Add the two call sites to the SYSTEMS_REFERENCE §32 paragraph and to the code comment above `SETTLEMENT_DRAFT_DIALOGUE_TYPES` — the symbol has three callers, and the narrowing reaches all three — and pin at least one of them (with an offer for war_1 mounted, `evaluate_open_settlement_eligibility`/the pair-substitute check for war_2 no longer refuses `settlement_collision_active`).

**Refuter 1 — CONFIRMED (severity P3)**

CONFIRMED, and understated in three ways. TRUE STATEMENT: `settlement_routes._mounted_settlement_dialogue` has THREE call sites, and narrowing it changed the verdict at all of them, but the record accounts for one. (a) The staging site (`settlement_staging.stage_settlement_confirm`) performs BOTH the cross-war `cross_war_settlement_collision` refusal AND the same-war refresh/scope-replace — I read the block — so the in-code comment's "the cross-war collision AND the same-war refresh/scope-replace arm in `stage_settlement_confirm`" describes that ONE site, not the other two. (b) SYSTEMS_REFERENCE §32 does not merely omit the other two; it affirmatively MIS-SCOPES the symbol: "the mounted-draft reader `_mounted_settlement_dialogue` (the one `stage_settlement_confirm` consults to raise `cross_war_settlement_collision`)". (c) FA-N18's own filed fix shape explicitly warned against this move and named both sites: "Do NOT narrow `_mounted_settlement_dialogue` itself as the first move: its two other consumers (settlement_routes.py:215 and settlement_validation.py:427) use it only for the cross-war …". The slice narrowed it anyway, which is defensible (the direction matches the rule), but no cell in BUG_FIXES, §32 or the boxed SLICE 10 block records that the row's warning was consciously overruled. Reachability is HIGHER than "two player-facing eligibility gates": `settlement_routes.evaluate_war_detail_actionability` is called from `war_status._evaluate_war_detail_actionability` inside `build_active_wars`, which rides EVERY response, so the changed verdict is computed and shipped to the client for every live war on every turn a letter stands. The reviewer is right that it is not a regression: pre-slice, a standing offer about war_1 made every OTHER war's detail row report `actionable: False / settlement_collision_active` — i.e. the FA-N18 defect at the HUD, telling the player to resolve a review they never opened. So the change is the fix extended, and the defect is a record + pinning gap, not a behaviour bug. Severity raised P4 -> P3 because the record actively contradicts the code at a symbol the slice's own method lesson ("the census must be the SYMBOL") exists to protect, and because the unpinned surface ships on every response.

<details><summary>What the refuter ran or read</summary>

READ (working tree at f1fe18ab, clean): `grep -rn "_mounted_settlement_dialogue" backend/` -> three call sites: settlement_staging.py:3461 (documented), settlement_routes.py:266 (`evaluate_war_detail_actionability`), settlement_validation.py:427 (`evaluate_pair_peace_substitute_eligibility`). Both undocumented sites read the identical guard `mounted is not None and str(mounted.get("war_id") or "") not in ("", war_id_str)` and return `settlement_collision_active`. Read settlement_staging.py:3457-3480 and confirmed its single call site performs BOTH the cross-war collision return AND the `active_war_id == war_id_str` same-war refresh, which is exactly what the in-code comment enumerates.

RAN (probe written with Write, executed from repo root; INK_IRON_SAVE_DIR pointed at the scratchpad; SOVEREIGN_SCENARIO popped; no parser, no end-turn, so no API spend and no autosave touched):
  scratchpad/agent_probes/p_mounted.py — load tests/fixtures/playtest_saves/fixture_t20_ambient.json via WorldState.from_dict(data["world_state"]) (it boots with Britain's real incoming_settlement_offer for war_1 CURRENT, and war_2 = France vs Switzerland live), then call evaluate_war_detail_actionability and evaluate_pair_peace_substitute_eligibility for both wars with SR.OFFER_IS_MAIL_NEVER_A_DRAFT True and False.
OUTPUT:
  CURRENT dialogue type: incoming_settlement_offer war_id: war_1
  [LEVER ON  (post-slice)] war_2/Switzerland: war_detail actionable=True  refusal=''                           | substitute eligible=True  refusal=None
  [LEVER ON  (post-slice)] war_1/Britain:     war_detail actionable=True  refusal=''                           | substitute eligible=True  refusal=None
  [LEVER OFF (pre-slice) ] war_2/Switzerland: war_detail actionable=False refusal='settlement_collision_active' | substitute eligible=False refusal='settlement_collision_active'
  [LEVER OFF (pre-slice) ] war_1/Britain:     war_detail actionable=True  refusal=''                           | substitute eligible=True  refusal=None
So both undocumented gates flip cross-war, driven solely by the lever; the same-war case is unchanged because the guard already exempted it.

PINNING: `grep -n "war_detail_actionability\|pair_peace_substitute\|actionable" tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py` -> zero hits in 1062 lines. The only pre-existing collision pins are tests/test_settlement_pair_substitute_ctas.py:519 (mounts a settlement_confirm via `_stage_rejected_dialogue`, read at :490-500) and tests/test_settlement_recovery_g2_slice6.py; `.venv/Scripts/python.exe -m pytest tests/test_settlement_pair_substitute_ctas.py tests/test_settlement_recovery_g2_slice6.py -q -p no:randomly` -> 29 passed, and they pass identically in both lever arms because neither ever mounts an offer. The offer-mounted verdict at both gates is unpinned suite-wide.

RECORD: read docs/SYSTEMS_REFERENCE.md §32 (line 3998ff), the boxed SLICE 10 block in docs/BUG_FIXES.md (line 447ff), and the FA-N18 / FA-N4 / FA-N15 row cells, plus the module comment at settlement_routes.py above SETTLEMENT_DRAFT_DIALOGUE_TYPES. None mentions `evaluate_war_detail_actionability` or `evaluate_pair_peace_substitute_eligibility`; §32's parenthetical scopes the helper to `stage_settlement_confirm` alone; FA-N18's fix cell contains the "Do NOT narrow ... its two other consumers" warning (itself truncated mid-sentence in the file).

No git mutation, no repo file written, no full suite, no mutation sweep.

</details>

**Refuter 2 — REFUTED (severity P4)**

The behaviour change is REAL and I reproduced it — but it is the slice's own rule applied where the rule belongs, it is structurally guarded, and the record's census is accurate as written. Three separate reasons the finding does not stand:

(1) THE RECORD IS NOT WRONG. The finder measured callers of `_mounted_settlement_dialogue` against a sentence that is a census of readers of the SET, not of that helper. SYSTEMS_REFERENCE §32 says `settlement_draft_dialogue_types()` "is read at exactly three places" and names `_settlement_dialogue_active`, `_mounted_settlement_dialogue`, and the staging tail. `grep -rn "settlement_draft_dialogue_types()" backend/` returns exactly those three call sites (settlement_routes:146, settlement_routes:425, settlement_staging:3663) plus the def. The census is EXACT. What the finder read as an incomplete enumeration is the parenthetical identifying gloss "(the one `stage_settlement_confirm` consults to raise `cross_war_settlement_collision`)" — a gloss naming the helper's most familiar caller, not a claim about how many callers it has. The in-file comment's phrasing is likewise role-shaped, not site-shaped: "the cross-war collision AND the same-war refresh/scope-replace arm", and "cross-war collision" is precisely what all three sites do with it.

(2) THE WAR-DETAIL SITE IS REACHABLE BUT GUARDED — and the guard is structural, not incidental. `evaluate_war_detail_actionability` runs on every response through `war_status.build_active_wars`, so the flip is live. But the advisory gate and the mutation gate (`stage_settlement_confirm`) read the SAME predicate, so they cannot desynchronise: moving the predicate moves both. Measured (probe p2, offer for war_1 mounted, staging war_2): under the new lever ADVISORY actionable=True / EXECUTOR success=True; under the flipped lever ADVISORY settlement_collision_active / EXECUTOR cross_war_settlement_collision. Advisory==executor in BOTH states — no false affordance is created in either direction. And the letter survives: after the successful stage the dialogue queue reads `['incoming_settlement_offer']`, i.e. the staging tail's preempt arm re-queued it exactly as the slice designed. The advisory's own output is inert besides: `peace_seeking_controls` has ZERO consumers in backend/ or godot-client/ outside the two producers.

(3) THE PAIR-SUBSTITUTE SITE IS UNREACHABLE FOR THE OFFER CASE. `evaluate_pair_peace_substitute_eligibility`'s click path is `_handle_pair_peace_substitute_action`, dispatched from `diplomatic_executor.handle_diplomatic_dialogue_response`, where `dialogue = world.pending_diplomatic_dialogue`. The handler's `war_id` is read off that same dict, and `_mounted_settlement_dialogue(world)` returns that same dict — so the war_ids are equal by construction and the collision arm is a no-op on that path both before and after the commit. An `incoming_settlement_offer` can never be the mounted dialogue when a `settlement_confirm` action is being answered. The render path (settlement_staging:2800) only runs on a popup that `stage_settlement_confirm` already built, so its verdict is consistent with the staging outcome that produced it.

WHAT SURVIVES, and it is P4 documentation precision only: the offer-specific verdict at those two gates is not pinned. The pre-existing pin `tests/test_settlement_pair_substitute_ctas.py::...settlement_collision_active` stages a real `settlement_confirm`, and I verified that pin's case still refuses under the new lever (probe p1, dtype=settlement_confirm: refused under BOTH lever settings) — which is why the slice never saw a red. So the DRAFT collision remains pinned at both undocumented gates; only the offer case moved, and it moved because the shared predicate moved. A future flip of `OFFER_IS_MAIL_NEVER_A_DRAFT` would move all three sites back together, which is the lever's stated purpose. There is no defect this commit is responsible for.

<details><summary>What the refuter ran or read</summary>

All probes read-only, run from the repo root at f1fe18ab with SOVEREIGN_SCENARIO=none and INK_IRON_SAVE_DIR pointed at the scratchpad. Probe files under scratchpad/agent_probes/.

A. CENSUS. `grep -rn "_mounted_settlement_dialogue" backend/ --include=*.py` -> 3 call sites: settlement_routes.py:266 (`evaluate_war_detail_actionability`), settlement_staging.py:3461 (`stage_settlement_confirm`), settlement_validation.py:427 (`evaluate_pair_peace_substitute_eligibility`). The finder's site list is correct.

B. THE RECORD'S OWN CENSUS IS EXACT. `grep -rn "settlement_draft_dialogue_types()" backend/ --include=*.py` -> settlement_routes.py:82 (def), :146 (`_settlement_dialogue_active`), :425 (`_mounted_settlement_dialogue`), settlement_staging.py:3663 (the tail). Exactly the three readers SYSTEMS_REFERENCE §32 names. `git show a1ed5c9d:backend/game_logic/settlement_routes.py` confirms the pre-slice body read `SETTLEMENT_FAMILY_DIALOGUE_TYPES`, so the change is real and introduced by this commit.

C. PROBE p1 — the flip, both gates, both dialogue types. Two synthetic wars (war_1 France-vs-Austria, war_2 France-vs-Britain), a dialogue pushed onto `world._dialogue_manager` for war_1, then both gates called for war_2, under both lever settings:
  dtype=incoming_settlement_offer lever=True  -> war_detail actionable=True refusal='' controls=['negotiate_peace']; pair_subst eligible=True refusal=None
  dtype=incoming_settlement_offer lever=False -> war_detail actionable=False refusal=settlement_collision_active controls=[]; pair_subst eligible=False refusal=settlement_collision_active
  dtype=settlement_confirm lever=True  -> both refused settlement_collision_active
  dtype=settlement_confirm lever=False -> both refused settlement_collision_active
So the behaviour change is confirmed at both undocumented sites, AND the draft case (what the existing pins cover) is unchanged — which is exactly why the suite stayed green.

D. PROBE p2 — does the advisory still agree with the executor, and does the letter survive? Same fixture with war_2 made multilateral (defenders Britain+Russia, so `stage_settlement_confirm` gets past the `one_to_one_war` refusal my first run hit). Offer for war_1 mounted; call the advisory for war_2, then actually stage war_2:
  lever=True  -> ADVISORY actionable=True, EXECUTOR success=True, current=settlement_confirm/war_2, queue=['incoming_settlement_offer'], AGREE=True
  lever=False -> ADVISORY actionable=False refusal=settlement_collision_active, EXECUTOR success=False error=cross_war_settlement_collision, current=incoming_settlement_offer/war_1, queue=[], AGREE=True
Advisory==executor in both states, and under the new lever the mounted letter is re-queued rather than dropped.

E. REACHABILITY OF THE PAIR-SUBSTITUTE PATH. `backend/commands/diplomatic_executor.py` `handle_diplomatic_dialogue_response` binds `dialogue = world.pending_diplomatic_dialogue` and passes it to `handle_settlement_dialogue_action`; `_handle_pair_peace_substitute_action` then reads `war_id = dialogue.get("war_id")` and calls `evaluate_pair_peace_substitute_eligibility`, which re-reads the same current dialogue via `_mounted_settlement_dialogue`. Same dict, equal war_ids, arm never fires — for the offer case the site is structurally unreachable in play.

F. INERTNESS OF THE CHANGED OUTPUT. `grep -rn "peace_seeking_controls" backend/ godot-client/ --include=*.py --include=*.gd` excluding settlement_routes.py and war_status.py -> no output. Nothing consumes it.

G. EXISTING PIN. `tests/test_settlement_pair_substitute_ctas.py` pins `refusal_code == "settlement_collision_active"` via `_stage_rejected_dialogue(world)`, which stages a `settlement_confirm`. Probe p1's dtype=settlement_confirm rows show that pin's case still refuses under the shipped lever — the draft collision at both undocumented gates remains pinned.

</details>
