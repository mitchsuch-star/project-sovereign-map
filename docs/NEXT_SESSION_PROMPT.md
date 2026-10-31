# NEXT SESSION PROMPT — Row RE "Affairs of State": RE-1 the engine, unarmed (the events before the deploy)

> Overwritten each time a session hands off. Current hand-over: **October 31, 2026 — the re-route recorded**: the user's
> word ("NOPE EVENTS FIRST DO IT IN NEW SESSION") moved the whole row RE ahead of S15; S15 the deploy follows RE; S16 (the
> `main.gd` split) and S17c (the `main.py` router move) stay after the deploy, so every client slice lands on today's unsplit
> scripts and the safety valve RE-2 edits stays at its address. Recorded in `docs/RECURRING_EVENTS_SPEC.md` §0c (the ruling
> verbatim; every placement line points there), `docs/PRE_DEPLOY_PLAN.md` §2 (the RE row before S15), `docs/ROADMAP.md`
> (the row in "Before the deploy"), `docs/STATUS.md` ▶ NEXT UP and CLAUDE.md's Current Phase. **Nothing of RE is built.**
>
> **What RE is:** the build contract is `docs/RECURRING_EVENTS_SPEC.md` §5–§16 read with §6.5 (the Haiti letter), §12b (the
> Correspondence and the letter's dress), §12c (the reaction layer), §16b (the eight slices and the four tiers) and §17b; the
> rulings §0 (Q1–Q14, October 27) and §0b (P1–P20, October 30, "Take the defaults"). Eight slices in §16's order, each its own
> commit through the hook and a pause for the user's review before the next: RE-1 the engine unarmed → RE-2 the client and the
> dress → RE-3 the three armed with H0 → RE-H the Haiti letter → RE-C the Correspondence → RE-R the reactions → RE-6 the
> Edicts → RE-5 the close. Four shippable tiers (the letter 5.5; + the home 6.75; + the reactions 7.5; + the squadron 8.75;
> with the Edicts 10.5), each its own STATUS line and done-when.
>
> **Traps the row will meet (do not re-discover them):** `set(MO.OPS)` is pinned (`tests/test_moments_engine.py`, 7 → 9 → 10
> across the slices); the four shipped moment ids are pinned in `tests/test_moments_armed.py`; HC-0 (no calendar reads in
> mechanics) is pinned; `mechanical_block` in `tools/_s14c_sweep_record.py` hashes every non-`deck` key of the scenario's
> `moments` block, so arming anything new fails `tests/test_moments_pacing.py` until the S14c sweep is re-recorded (at RE-3 and
> RE-H) — RE-1 stays unarmed and byte-identical (`historical` reproduces today's boot); `pick_marshal_voice` picks
> `bank[key % len(bank)]`, so new lines go under a NEW situation key; a seeded outcome's namespace carries the issued turn
> (`_pct_roll` in `naval.py`); `expedition_slip_odds` is the one naval model (add the `escort` override, never a clone); the
> event log rolls at 500 rows — anything the Correspondence re-reads lives in the moment's state row; the ratchets
> (`to_dict` 497 of 500, levers 231, functions over 500 lines 28, `SCRIPT ERROR` 0); every number to Godot an `int`; no
> per-region scans in hot paths; a new dialogue type needs the `main.gd` dtype whitelist; the first-open line ≤ 220 characters;
> every answer is a button. Subagents on Sonnet or Haiku; grep-verify any agent's bulk `.gd` edits. Golden Rule 9 and Rule 10.
> The pre-commit hook runs the full suite (~11 minutes): commit from Bash in the background with
> `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` and read the log's EXIT line; never edit tracked files while it runs.
>
> **For the user:** the review after each slice; the certificate (the build is unsigned until it arrives); S14d's A1 as
> applied, AO's three questions (`REFORMS_SPEC.md` §5a), SF-NAV-1-D1.
> Paste everything below the line as the opening message of a fresh session.

---

Row RE "Affairs of State" — **RE-1 the engine, unarmed** — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log --format=%h -5` for the head). Plan Mode first; build on approval; land green through the hook; commit; a STATUS session entry; this prompt rewritten for RE-2; then STOP for the user's review before RE-2.

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/RECURRING_EVENTS_SPEC.md` §0c (the re-route), §16 "RE-1 — the engine, unarmed" with §16b's RE-1 row (the look-ahead P8, the latch mask and `grace` P7, the form frozen in `bind` P18, the state rows' `receipt` / `echo` / `outcome_line` / `remark_by` P19, `register` and the `outcome` phase, `ends` in the validator, `mechanical_block` descending into `affairs.deck`, `DISPLAY_KEYS` + `ANSWER_DISPLAY_KEYS`, the premise memo) and "Pins flipped when built", §5 (the attribute block), §7 (pacing — the moments blind to affairs), §8 (one function, France's content), §9 (the engine extended, not forked; the trace), §10 (seeds — timing only), §11 (saves), §13 (Rule 8), §0b P7 / P8 / P18 / P19; `docs/EVENTS_SPEC.md` (S14c's engine); `backend/game_logic/moments.py` (the store `world.moments = {block, state, due}`, `plan` / `answer` / `_tick`, `OPS`, `PREDICATES`, `ANCHORS`); `backend/modding/validator.py` (the moments rules: dated windows, the decline's barred ops, the alarm sources); the scenario's `moments` block in `godot-client/project-sovereign/assets/maps/europe_1805.json`; `tests/test_moments_engine.py` (`set(MO.OPS)` pinned; HC-0), `tests/test_moments_armed.py`, `tests/test_moments_pacing.py` and `tools/_s14c_sweep_record.py` (the deck hash); CLAUDE.md's Golden Rules.

Scope: **RE-1 as §16 and §16b write it** — `moments.py`: occurrence ids and their rows, the moments' blindness to `#` rows and the free withdrawal, `deliver_due` from `tick`, the lord in the plan, `purse_of`, the `authority` and `admin` ops with the grip floor and `bites`, the look-ahead, the latch mask and `grace`, the form frozen in `bind`, the state rows' `receipt` / `echo` / `outcome_line` / `remark_by`, `register` and the `outcome` phase with the one-liner's arm; `affairs.py`: the premises and their memos, the pulse, the Watch reader, a `resolve_courts` that does nothing; the runtime store and its `store_from_data` line; `_validate_affairs` and `backfill_affairs` (with `ends`); the trace extended (§9); `mechanical_block` descending into `affairs.deck` to strip display keys; **ERR-2:** "The Cabinet" → "the Secretariat" at `moments.py:91` and `dialogue_manager.py:651`, re-pinned at `tests/test_moments_engine.py:510` (the top bar's "The Cabinet (F1)" is the diplomacy wizard); CLAUDE.md's Document Map row, paid for by a trim (the cap 62,000 LF bytes, `tests/test_code_health_ratchet.py`). **The seams** named in `tests/_affairs_seams.py` (AF0, AFB, AFP, AFN, AFA); the series tool `tools/_affairs_series_arms.py` chained from the prior record. Done when: the shipped boot is unarmed; `BASELINE_SERIES` is byte-identical with every reach counted at 0; the ratchet is unchanged (`to_dict` 497, levers 231, functions over 500 lines 28); the conscious flips are named (`set(MO.OPS)` 7 → 9, the store's key-set pins); the pins of `tests/test_affairs_engine.py` (§16's list: ids, rows and their frozen `{lord, bind, tier}`; derived cooldowns and caps; the pulse on `historical` and ten seeds, no `random` / `ai_rng`; shown = applied for both ops on three boards including the grip floor on a war-score −35 board; `bites`; the moments' arrival turns invariant armed against unarmed, and the free withdrawal; a save round trip and the backfill; at least 25 validator refusals; the Rule 8 census; the alarm-untouched pin; the trace's teeth) and `tests/test_affairs_pacing.py`'s look-ahead measure on the ten `SWEEP_SEEDS` (§17b's "the first affair about T13", UNVERIFIED until RE-1); the full suite green through the hook. Then the STATUS entry (archive the oldest entry to `docs/archive/STATUS_2026_Q4.md` if the seven-entry cap bites), `SYSTEMS_REFERENCE.md`'s rules section, this prompt rewritten for RE-2, and the review pause.
