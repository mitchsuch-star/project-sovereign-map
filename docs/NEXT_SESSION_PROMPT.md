# NEXT SESSION PROMPT — Pre-Deploy S10b: CODE-2c, the two DD-1 left whole

> Overwritten each time a session hands off. Current hand-off: **October 13,
> 2026, after S10 (CODE-2b) closed.** `execute_command`, `format_event_oneliner`
> and `_execute_strategic_command` are each a driver of named stages; functions
> over 500 lines 33 → 30; `score_run check` identical at every cut.
>
> **Closing S10 found the gap this session fills.** CODE-2 named eight
> functions and DD-1 was to absorb two of them. It never split them:
> `DiplomaticExecutor._process_dialogue_choice` is still 2,210 lines and
> `WorldState._ratify_treaty` 1,024. The user ruled them **S10b, CODE-2c**,
> before UXR-3.
>
> Records: `docs/CODE_HEALTH_PLAN.md` §CODE-2b landing records (slices 1–3) and §CODE-2c (the contract).
> Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2, row S10b, with `docs/STATUS.md` ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line pointing there. The Score Finish residue (`SCORE_FINISH_SPEC.md` §3 Step 9) stays PAUSED until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S10b — CODE-2c, the two monster functions DD-1 left whole.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S10b. Work directly on master per `CLAUDE.md`'s workflow, and commit and push at each clean slice. Run `git fetch origin` first and read `git log -5 --stat` before touching anything. Use Plan Mode first (the user's standing preference for a non-trivial session). **Two slices, one commit each, with the review pause between them:** slice 1 `_ratify_treaty`, then slice 2 `_process_dialogue_choice`.

**The work.** `docs/CODE_HEALTH_PLAN.md` §CODE-2 holds the recipe, the CODE-2a record and the three CODE-2b records; §CODE-2c holds this row's contract.
- **Slice 1: `WorldState._ratify_treaty`** (`backend/models/world_state.py`, 1,024 lines, 61 local imports, one nested `try`, three bare `return None`s).
  - It runs as ordinary top-level statements: a state map, the clause loops, the forced-alliance block, and the 292-line `if is_player_treaty:`.
  - The tool's body mode cuts it as it stands. Its `TARGETS` entry takes `cls="WorldState"` and `confine=True`.
  - Its guard sequence already lives in `treaty.can_sign` (DD-1 S7 Slice B); do not move it back.
- **Slice 2: `DiplomaticExecutor._process_dialogue_choice`** (`backend/commands/diplomatic_executor.py`, 2,210 lines, 73 local imports, two `try`s).
  - After a few imports, its body is ONE statement: `if action == "dismiss": … elif …`, 2,195 lines. No top-level cut can split it, so the tool needs an **elif-chain mode**: each run of arms becomes a stage.
  - The chain is the body's last statement. An arm that matched and fell off its end therefore returned `None` from the function.
  - So in a stage, every arm body that can complete gets an appended `return None`, and the stage ends `return _NEXT_STAGE` when no test in its run was true.
  - The proof must show three things: the old tests evaluated in the same order; each arm body AST-equal to the old one, with only that appended `return None`; and the `else:` (if any) kept in the last stage.
  - Check first that no arm's TEST binds a name (walrus) and that nothing reads a name an earlier arm bound.
- **Done when:** neither function is over 500 lines and `FUNCTIONS_OVER_500_CAP` reads 28 (30 now). CODE-2's own done-when (none of the eight named over 500) is then MET; record it.

**The tool:** `stage_fn.py`, plus `pin_scan.py` and `oneliner_sweep.py` as models, in the S10 session's scratchpad (`C:\Users\User\AppData\Local\Temp\claude\C--Users-User-PycharmProjects-project-sovereign-map\a2cd1502-3e0b-446c-8899-677b29a146c5\scratchpad`). If that folder is gone, slice 1's original is in `…\2788afd1-1293-4154-ae05-3021bb6a0ce0\scratchpad`, but it lacks S10's four changes:
- `confine=True` turns on two rules, each recorded in slice 2's landing record:
  - **confine:** a name bound only inside branches that always return or raise stays local.
  - **split:** a name every stage binds before reading stays local, under a conservative definite-assignment pass.
- an import road for a module with no `typing` line;
- the `{x=}` refusal reads the f-string's source text;
- the proof expects `simple=0` on an annotated `ctx.` target.

What the tool does:
- `python stage_fn.py <target>` is a dry run (it writes `<target>_staged.py` beside the tool); add `--apply` to write the source; `--no-confine` compares against slice 1's rule.
- It proves every stage AST-equal to the old body, with the shared names as `ctx.<name>`. A symtable check refuses any stage that reads an old local it never bound.

**Read first, in this order:**
- `CODE_HEALTH_PLAN.md` §CODE-2, the CODE-2b slice 2–3 records and §CODE-2c.
- `tests/test_code2b_the_strategic_order_is_staged.py`, the method-driver shape pin to model each new `tests/test_code2c_*` on.
- `tests/_staged_functions.py`, the generic helper: add an owner tuple per new driver, as `strategic_command()` does.
- `tests/test_code_health_ratchet.py` and `tools/_code_health_census.py`.

**The net.** A split that passes all of these byte-for-byte has not changed behaviour:
- DD-1's own instruments: `tests/test_dd1_sign_ability_sweep.py`, `test_dd1_treaty_fuzzer.py`, `test_dd1_answer_binding_shuffle.py`, `test_dd1_s7_can_sign.py`, `test_dd1_s7_one_exit.py`, `test_dd1_s8_the_verbs.py`;
- the settlement suites;
- `score_run check` (`tools/score_run.py check --run docs/audits/score_runs/2026_10_05_sfr`; about 7 s; it rewrites four archive files, so run `git checkout -- docs/audits/score_runs/2026_10_05_sfr/` after each run and diff the stdout);
- `BASELINE_SERIES` + M1–M7.

A re-record needs a stated reason, and a pure refactor has none.

**Find the pins BEFORE the run — S10 found four of its five this way; the hook found the fifth:**
- `pin_scan.py <src> <staged>` lists every test string literal that matched the file before the cut and not after. A shared local now reads `ctx.world`, so a pin on `world.get_marshal(target)` must name `ctx.world.get_marshal(ctx.target)`. Same assertion, where the code now lives.
- Grep the tests for the function's name AS A STRING. A census that selects functions by name (S10's NPC-12) passes VACUOUSLY over a short driver. Name the stages, read off the driver.
- Grep the tests for censuses that EXTRACT an expression and compare it for equality (S10's WO-17 `passable_for` census wanted `marshal.location` exactly). The literal scan cannot see these, because the old text survives as a substring of the `ctx.` form.

**Traps — earlier sessions paid for each of these:**
- **`PYTHONDONTWRITEBYTECODE=1` in the shell** fails two `test_fa_slice8_…` stale-bytecode pins on any tree. Check `env | grep PYTHON` first, and run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE`.
- **Line endings.** Working copies can be CRLF while the blobs are LF (`core.autocrlf=true`; some test files are CRLF on disk, some LF). An edit script must detect the file's own newline. A `sed` replacement carrying `\r` mixes them.
- **`field` as a name.** If the module already uses `field` as a local or loop variable, ruff F402 flags the tool's `from dataclasses import dataclass, field`. Import the module (`import dataclasses`) instead, as `campaign_log.py` did.
- **Memory is thin on this machine** (about 1–6 GB free).
  - The hook can die in collection with a `MemoryError`; retry it plainly.
  - Never run two Godot engines at once.
- **The hook.** It runs ruff and the full parallel suite (about 6 min; 30,702 tests at slice 2). Commit with `run_in_background: true` from Bash, using a message file and never `--no-verify`, and make no tracked edit while it runs. Read the hook log's `[pre-commit]` and `EXIT=` lines before believing a commit.
- **Shell.** A Bash heredoc mangles backslashes, and `sed` escapes are a trap. Write scripts with the Write tool and run them by path.
- **Git.** Never `git add -A`; stage by name.
- **Ledgers.** A new OPEN row in `BUG_FIXES.md` needs an `⟨SF step=… · pillar=…⟩` tag (`test_score_finish_step0.py`).
- **Running things.** `ruff` is not on Bash's PATH: use `".venv/Scripts/python.exe" -m ruff check backend/`. Never kill a `-m backend.main` process.
- **Docs caps.** `CLAUDE.md` sits at 61,986 / 62,000 B: pay for every new word by trimming the oldest LIVE STATE row. `STATUS.md` keeps seven ▶ blocks at most; the oldest goes to `docs/archive/STATUS_2026_Q4.md`, newest first.

**Code-health rules in force:**
- A new lever lives one session past its attribution, then retires at the next slice's head (`tools/retire_lever.py`). CODE-1's November batch takes its head once October closes.
- A combat fix lands in the `_attack_<stage>` that owns it; a standing-order fix in the `_strategic_<stage>`; a log line in the `_oneliner_<family>`.
- A new font size is a theme step, not an override (`RAW_RATCHET` 11). Any dim grey goes through `Utils.toned` / `toned_hex` / the COLOR tokens.

**The records each commit carries:**
- `CODE_HEALTH_PLAN.md`: a CODE-2c landing record per function, with the stage list written BEFORE the cut.
- `PRE_DEPLOY_PLAN.md` §2: the S10b row (struck when both land).
- `STATUS.md` ▶ NEXT UP.
- The `CLAUDE.md` LIVE STATE line, and the "Before Modifying" rows for diplomacy execution and the settlement's ratifier.
- This file, rewritten for S11 (UXR-3, `UX_UI_REVIEW_PLAN.md` §UXR-3) when S10b closes.

**Open with the user:**
- UXR-4, the eyes-on sign-off at 5120×1440, including S9b's frames.
- EG-D1 … EG-D3.

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a ratchet, re-record a series without a stated reason, or tune an instrument to a fix.
