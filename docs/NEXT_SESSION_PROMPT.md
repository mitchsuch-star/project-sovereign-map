# NEXT SESSION PROMPT — Pre-Deploy S7b: CODE-3 "every broad except speaks" + DD-C "nothing fails silently"

> Overwritten each time a session hands off. Current hand-off: **October 12,
> 2026, after S8 landed DD-1 Step 3 THE VERBS** — `ask <ally> to return
> <province>` (SFR-D42), `bid for <court>` (SFR-D40) and the truce's
> followers announced (SFR-D28's announce half), each through the shared
> executor, a corpus row and a wizard chip, each reading ONE gate in words;
> **SFR-D28 / D40 / D42 FIXED; the sweep A 0 / B 0 with its chip poll
> widened to the new chips; the fuzzer and the shuffle 0; `BASELINE_SERIES`
> + M1–M7 byte-identical.** The head was **CODE-1 batch 4** (`world_state.py`
> / `combat_executor.py` / `enemy_ai.py` / `main.py`: 67 of 100 retired, 32
> October ones kept, `LITERALS_DRILL_TO_HEAL` kept as a decided `False`;
> levers 496 → 429; the ratchet lowered). Landing records
> `docs/PRE_DEPLOY_PLAN.md` §3.1 "DD-1 S8 landing record" and
> `docs/CODE_HEALTH_PLAN.md` §CODE-1 BATCH 4; rules `SYSTEMS_REFERENCE.md`
> §109; pins `tests/test_dd1_s8_the_verbs.py` (37). Routing authority:
> `docs/PRE_DEPLOY_PLAN.md` §2 (the order — S8 STRUCK; **S7b = CODE-3 +
> DD-C is NEXT**; CODE-2a follows) → `CODE_HEALTH_PLAN.md` §CODE-3 and
> `PRE_DEPLOY_PLAN.md` §3 DD-C; `docs/STATUS.md` ▶ NEXT UP and the
> `CLAUDE.md` LIVE STATE line point there. The Score Finish residue
> (`SCORE_FINISH_SPEC.md` §3 Step 9) stays PAUSED behind the plan until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S7b — CODE-3 "every broad except speaks" + DD-C "nothing fails silently".** Routing authority = `docs/PRE_DEPLOY_PLAN.md` §2 → `docs/CODE_HEALTH_PLAN.md` §CODE-3 (the rule, the recipe, the done-when) + `docs/PRE_DEPLOY_PLAN.md` §3 "DD-C" (the weak spot, the instrument, the done-when). Work directly on master per `CLAUDE.md`'s workflow; commit and push at the clean slice. `git fetch origin` first and read `git log -3 --stat` before touching anything. **The head of this session is CODE-1 batch 5** (`docs/CODE_HEALTH_PLAN.md` §CODE-1 BATCH 4's "Next batches": the 116 levers in the `game_logic/` modules over 3,000 lines — `dispatch.py` 50, `coalition.py` 18, `ai_diplomacy.py` 15, `congress.py` 13, `settlement_offers.py` 11, `diplomatic_templates.py` 4, `settlement_staging.py` 3, `settlement_actions.py` 2; the October 2026 ones keep their session). Record which batch you take in the landing record; lower `LEVERS_CAP` in `tests/test_code_health_ratchet.py` to the census's reading.

**Read first, in this order:** `CODE_HEALTH_PLAN.md` §CODE-3 whole (the `errors.py` contract — `swallow(ctx, notify=)` / `report(exc, site)`, de-duplicated per site per process, `world.error_tally` display-only; the recipe's four steps; the done-when — 0 silent handlers in `save_manager.py`, `world_state.py`'s serialization, `main.py`'s save/load routes and `llm_client.py`, under 60 elsewhere each with a site string); `PRE_DEPLOY_PLAN.md` §3 DD-C (fault injection on `save_game` / `autosave` / `load_game` — disk full, a non-serializable field planted on a marshal, a truncated file — once per turn over a 40-turn driver run; the round-trip equality check on every autosave; the client's save/load surfaces asserted to SHOW the failure); `tools/_code_health_census.py` (the silent-handler census: 367 today, by file — `state_desk.py` 36, `game_end.py` 20, `counsel.py` 18, `diplomacy.py` 17, `world_state.py` 17, `main.py` 15, `llm_client.py` 15); `tests/test_code_health_ratchet.py` (`SILENT_HANDLERS_CAP` 367 — the pin that must fall every slice); `backend/save_manager.py` and `main.py`'s `/save` / `/load` / autosave routes; `backend/notifications.py` (the rail notice `notify=` pushes); `docs/PLAYTESTING.md` Mode A (`tools/playtest_driver.py`, the 40-turn run the injection rides).

**Corrections the reads established (do not re-derive):** every `except Exception` that neither logs nor re-raises counts (the ratchet's own regex — read it before writing `errors.py`, so the helper's shape is one the census recognises as NOT silent); the save failure that broke every save for the rest of a campaign is the P1 this row exists for — the save path RAISES a typed `SaveError` the route turns into `success: False` WITH a `message` the client renders, the autosave the same; `main.py`'s route-level handlers return the error's class and site under `debug_error` only when `debug_mode` is on; a per-turn loop's `report` logs once per site, never 500 times.

**Slices, each landed with its pin:**
1. **`backend/errors.py` + the ratchet's new arm** — `swallow` / `report`; the census counts a handler that calls either as spoken; `SILENT_HANDLERS_CAP` starts falling.
2. **The save path (DD-C)** — `save_manager.save_game` / `autosave` / `load_game` raise `SaveError`; the routes answer with the sentence; the rail notice; the fault-injection harness (`tools/`, a driver hook once per turn) and its pins (`tests/test_dd_c_nothing_fails_silently.py`): every injected fault reaches the player as a sentence and the log at WARNING with the site; the round trip `to_dict(from_dict(x)) == x` on every autosave over 40 turns.
3. **The conversion by file, largest first** — `state_desk.py`, `game_end.py`, `counsel.py`, `diplomacy.py`, `world_state.py`, `main.py`, `llm_client.py`; narrow where the type is obvious (`KeyError`, `ValueError`, `json.JSONDecodeError`, the SDK's typed errors), keep the breadth and `report` where a display line is guarded.

**Done when:** the census reads 0 silent handlers in `save_manager.py`, `world_state.py` serialization, `main.py` save/load routes and `llm_client.py`, under 60 elsewhere each with a `report` site string; DD-C's injected faults all reach the player; `BASELINE_SERIES` + M1–M7 byte-identical (no behaviour change — a logged exception is the same exception); the ratchet's caps lowered to the readings.

**Records the commit carries:** `CODE_HEALTH_PLAN.md` §CODE-3 landing record + §CODE-1 BATCH 5 record, `PRE_DEPLOY_PLAN.md` §3 "DD-C landing record" + the §2 S7b row struck, `STATUS.md` ▶ NEXT UP (seven ▶ blocks at most — move the oldest to `docs/archive/STATUS_2026_Q4.md`, newest first), the `CLAUDE.md` LIVE STATE line (62,000-byte cap, lower-only; the ratchet also wants it within 8,000 of the cap — pay for a new row by shortening an older one), `SYSTEMS_REFERENCE.md` §110, `BUG_FIXES.md` rows struck if any, `docs/SAVE_FORMAT_REFERENCE.md` untouched unless a field moves, this file rewritten for S8b (CODE-2a, `_execute_attack` split into named stages).

**Traps.** A Bash heredoc turns `\b` into a BACKSPACE byte, a `'` inside an inline `python - <<EOF` aborts the command, and a heredoc with non-ASCII prose aborts outright — write every script AND every doc append with the Write tool, run it by path. `git add -A` never; the hook runs ruff + the full parallel suite (~6 min, the three dd1 pins run live instruments): commit in the background with a message file, never `--no-verify`, never edit a tracked file while it runs. `ruff` is not on Bash's PATH — `".venv/Scripts/python.exe" -m ruff check backend/`. The console is cp1252: every tool reconfigures stdout to UTF-8. `tools/retire_lever.py --list` takes DIRECTORIES (a file path lists nothing) and blames every lever — run it in the background with a long timeout. A `False` lever with a ruling (AIDR-D1's `LITERALS_DRILL_TO_HEAL`) is a decision, not a lever — it stays. A new wizard `_build_command` arm with a local var must teach BOTH harnesses (`test_cn4_the_chip_honesty_census.py`'s `_compose` and `test_fa_slice17_g…`'s `eval` namespace). `tools/sign_ability_sweep.py --arms X` rewrites the arm's committed record's timing fields — `git checkout` it unless the counts moved. **The fuzzer's live pin walks differently per PYTHONHASHSEED** — reproduce with `PYTHONHASHSEED=<n> pytest -k test_two_seeds` for n in 0…5 before fixing anything. `score_run check` rewrites four archive files — run `check` only on a scratch `--out`. `core.autocrlf=true`: keep each file's own newline. Never kill a `-m backend.main` process. The blind census files stay blind.

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever (land a change with its attribution test instead), edit a committed blind file, weaken a gate, swallow an exception the player must see, tune the instruments to the fixes.
