# NEXT SESSION PROMPT — Pre-Deploy S10b: CODE-2c, the two DD-1 left whole

> Overwritten each time a session hands off. Current hand-off: **October 13,
> 2026, after S10 (CODE-2b) closed and every open decision was ruled.**
> `execute_command`, `format_event_oneliner` and `_execute_strategic_command`
> are each a driver of named stages; functions over 500 lines 33 → 30;
> `score_run check` identical at every cut. The staging tool now lives in
> `tools/`.
>
> **Closing S10 found the gap this session fills.** CODE-2 named eight
> functions and DD-1 was to absorb two of them. It never split them:
> `DiplomaticExecutor._process_dialogue_choice` is still 2,210 lines and
> `WorldState._ratify_treaty` 1,024. The user ruled them **S10b, CODE-2c**,
> before UXR-3.
>
> **Nothing waits on the user.** On October 13 the user said "make all
> decisions". EG-D1 … D3, UXR-D4 (now row S12b) and CODE-5 / CODE-6 (S16–S17,
> after the deploy) are ruled, and the design ledger reads 0 open. UXR-4, the
> user's own eyes, is scheduled at S15 with the deploy.
>
> Records: `docs/CODE_HEALTH_PLAN.md` §CODE-2b landing records (slices 1–3)
> and §CODE-2c (the contract, with the elif-chain design decided on
> measurement). Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2, row S10b. The
> Score Finish residue stays PAUSED until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S10b — CODE-2c, the two monster functions DD-1 left whole.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S10b.
- Work directly on master per `CLAUDE.md`, and commit and push each slice.
- Run `git fetch origin` first and read `git log -5 --stat` before touching anything.
- **Every decision is already made** (the user's ruling, October 13, 2026: "make all decisions … nothing hanging"). This prompt is the approved plan:
  - Do not stop for Plan Mode approval, and do not pause between slices.
  - Run slice 1, commit and push, then slice 2, commit and push, then close.
  - The rules under "If something breaks" settle every fork; ask the user nothing.

**The work.** `docs/CODE_HEALTH_PLAN.md` §CODE-2 holds the recipe and the earlier records; §CODE-2c holds this row's contract.
- **Slice 1: `WorldState._ratify_treaty`** (`backend/models/world_state.py`, 1,024 lines).
  - Shape: 76 top-level statements, 61 local imports, one nested `try`, three bare `return None`s. The largest statement is the 292-line `if is_player_treaty:`.
  - Its `TARGETS` entry: `src="backend/models/world_state.py"`, `cls="WorldState"`, `func="_ratify_treaty"`, `params=["proposal"]`, `prefix="_ratify_"`, `ctx_class="RatifyTreatyContext"`, `mode="body"`, `confine=True`.
  - Cut at the statement families: the state map, the clause loops, the forced-alliance block, the player-treaty block and the close. Name each stage after its family.
  - Its guard sequence already lives in `treaty.can_sign` (DD-1 S7 Slice B); do not move it back.
- **Slice 2: `DiplomaticExecutor._process_dialogue_choice`** (`backend/commands/diplomatic_executor.py`, 2,210 lines).
  - Shape: 73 local imports. Its head is a docstring, three `from … import`s and `target_nation = dialogue.get("target_nation", "")`.
  - Then ONE `if action == "dismiss": … elif …` chain: 2,195 lines and 73 arms. The largest arm is 187 lines (`execute_ultimatum`). No test binds a name, and the chain ends in its own `else` (the unknown-action reply).
  - **Build the elif-chain mode** in `tools/stage_fn.py` (`mode="elif"`) to the design `CODE_HEALTH_PLAN.md` §CODE-2c records:
    - Each stage is one `if t_k: … elif …` run, with a synthetic final `else: return _NEXT_STAGE`.
    - Every arm body moves UNTOUCHED. A matched arm that falls off its end returns `None`, as the old function did, so no `return None` is appended.
    - The last stage keeps the original `else` and gets no synthetic one.
  - **The proof refuses unless:**
    - every arm body is AST-equal to the old one, with the shared names as `ctx.<name>`;
    - the tests appear in the old order;
    - each non-final stage's only addition is its synthetic `else`;
    - the original `else` sits in the last stage;
    - no stage is over 500 lines.
  - **The context.** Only one arm runs per call, so it holds only `action`, `selected`, `dialogue`, `world` and `target_nation`. The three head imports take the tool's existing repeat-per-stage road. The symtable check still refuses any stage that reads an old local it never bound; that is how the F2 class (a local import shadowing a module name) surfaces, so keep it on.
  - **Naming.** The `TARGETS` entry takes `prefix="_choice_"` and `ctx_class="DialogueChoiceContext"`, with `cls="DiplomaticExecutor"` and `params=["action", "selected", "dialogue", "world"]`. Cut the runs at the arms' family boundaries (settlement, proposal, ultimatum, modify, mission, alliance, the rest), about 5–8 stages, each named after its family.
- **Done when:**
  - neither function is over 500 lines;
  - `FUNCTIONS_OVER_500_CAP` in `tests/test_code_health_ratchet.py` reads 28 (30 now);
  - CODE-2's own done-when (none of the eight named over 500) is recorded as MET.

**The tool:** `tools/stage_fn.py`, plus `tools/pin_scan.py` and, as a model, `tools/oneliner_sweep.py`.
- **How it runs:**
  - `.venv/Scripts/python.exe tools/stage_fn.py <target>` is a dry run that writes the gitignored `tools/stage_fn_out/<target>_staged.py`.
  - `--apply` writes the source; `--no-confine` compares against slice 1's rule.
  - Each target is a `TARGETS` entry.
- **What it proves:** every stage AST-equal to the old body, with the shared names as `ctx.<name>`. A symtable check refuses any stage that reads an old local it never bound.
- **S10's four changes are in it:**
  - `confine=True` turns on two rules:
    - **confine:** a name bound only inside branches that always return or raise stays local;
    - **split:** a name every stage binds before reading stays local.
  - an import road for a module with no `typing` line;
  - the `{x=}` refusal reads the f-string's source text;
  - the proof expects `simple=0` on an annotated `ctx.` target.
- **Already checked for both targets:** neither module uses `field`, `dataclass` or `_NEXT_STAGE` as a name, and both already import `typing`, so the tool's default imports apply.

**Read first, in this order:**
- `CODE_HEALTH_PLAN.md` §CODE-2, the CODE-2b slice 2–3 records and §CODE-2c.
- `tests/test_code2b_the_strategic_order_is_staged.py`, the method-driver shape pin to model `tests/test_code2c_the_ratifier_is_staged.py` and `tests/test_code2c_the_dialogue_choice_is_staged.py` on.
- `tests/_staged_functions.py`, the generic helper: add an owner tuple per new driver, as `strategic_command()` does.
- `tests/test_code_health_ratchet.py` and `tools/_code_health_census.py`.

**The net.** A split that passes all of these byte-for-byte has not changed behaviour:
- DD-1's own instruments: `tests/test_dd1_sign_ability_sweep.py`, `test_dd1_treaty_fuzzer.py`, `test_dd1_answer_binding_shuffle.py`, `test_dd1_s7_can_sign.py`, `test_dd1_s7_one_exit.py`, `test_dd1_s8_the_verbs.py`;
- the settlement suites;
- `score_run check`:
  - run `tools/score_run.py check --run docs/audits/score_runs/2026_10_05_sfr` (about 7 s);
  - it rewrites four archive files, so run `git checkout -- docs/audits/score_runs/2026_10_05_sfr/` after each run;
  - diff the stdout before and after the cut.
- `BASELINE_SERIES` + M1–M7.
- For slice 2, also a before/after dialogue sweep modelled on `tools/oneliner_sweep.py`:
  - every `action` string the chain tests, through `_process_dialogue_choice`, on a fresh 1805 world with a stub dialogue;
  - outputs and exceptions written to JSON on the tree before the cut and after, the two files identical.

**Find the pins BEFORE the run — S10 found four of its five this way; the hook found the fifth:**
- `tools/pin_scan.py <src> <staged>` lists every test string literal that matched the file before the cut and not after. A shared local now reads `ctx.world`, so a pin on `world.get_marshal(target)` must name `ctx.world.get_marshal(ctx.target)`. Same assertion, where the code now lives.
- Grep the tests for each function's name AS A STRING. A census that selects functions by name (S10's NPC-12) passes VACUOUSLY over a short driver. Name the stages, read off the driver.
- Grep the tests for censuses that EXTRACT an expression and compare it for equality (S10's WO-17 `passable_for` census wanted `marshal.location` exactly). The literal scan cannot see these, because the old text survives as a substring of the `ctx.` form.

**If something breaks — decided in advance:**
- **The proof refuses a stage:** move the cut or fix the tool's rule. Never hand-edit moved code to satisfy the proof.
- **A pin fails on text:** re-point it to where the code now lives, with the same assertion. Never weaken it or delete it.
- **A net moves by a byte:** the cut is wrong. Revert the apply, find the cause, cut again. Never re-record a series and never re-score.
- **A stage is over 500 lines:** cut that run finer.
- **The hook dies with a `MemoryError`:** retry it plainly.
- **Any other failure:** fix the cause and commit again; never use `--no-verify`.
- **If slice 2's elif mode cannot be proven inside the session:**
  - land slice 1 alone;
  - record slice 2's state in §CODE-2c, with the tool's progress committed;
  - rewrite this file for slice 2.
  - The row is not struck until both functions land.

**Traps — earlier sessions paid for each of these:**
- **`PYTHONDONTWRITEBYTECODE=1` in the shell** fails two `test_fa_slice8_…` stale-bytecode pins on any tree. Check `env | grep PYTHON` first, and run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE`.
- **Line endings.** Working copies can be CRLF while the blobs are LF (`core.autocrlf=true`; some test files are CRLF on disk, some LF). An edit script must detect the file's own newline. A `sed` replacement carrying `\r` mixes them.
- **Memory is thin on this machine** (about 1–6 GB free). Never run two Godot engines at once.
- **The hook.** It runs ruff and the full parallel suite (about 6 min; 30,723 tests on October 13).
  - Commit with `run_in_background: true` from Bash, using a message file.
  - Make no tracked edit while it runs.
  - Read the hook log's `[pre-commit]` and `EXIT=` lines before believing a commit.
- **Shell.** A Bash heredoc mangles backslashes, and `sed` escapes are a trap. Write scripts with the Write tool and run them by path.
- **Git.** Never `git add -A`; stage by name.
- **Ledgers.** A new OPEN row in `BUG_FIXES.md` needs an `⟨SF step=… · pillar=…⟩` tag (`test_score_finish_step0.py`).
- **Running things.** `ruff` is not on Bash's PATH: use `".venv/Scripts/python.exe" -m ruff check backend/`. Never kill a `-m backend.main` process.
- **Docs caps.**
  - `CLAUDE.md` sits at 61,981 / 62,000 B: pay for every new word by trimming the oldest LIVE STATE row.
  - `STATUS.md` keeps seven ▶ blocks at most; the oldest goes to `docs/archive/STATUS_2026_Q4.md`, newest first.

**Code-health rules in force:**
- A new lever lives one session past its attribution, then retires at the next slice's head (`tools/retire_lever.py`). CODE-1's November batch takes its head once October closes.
- A fix lands in the stage that owns it:
  - a combat fix in its `_attack_<stage>`;
  - a standing-order fix in its `_strategic_<stage>`;
  - a log line in its `_oneliner_<family>`;
  - and, after this session, a dialogue answer in its `_choice_<family>` and a ratification clause in its `_ratify_<stage>`.
- A new font size is a theme step, not an override (`RAW_RATCHET` 11). Any dim grey goes through `Utils.toned` / `toned_hex` / the COLOR tokens.

**The records each commit carries:**
- `CODE_HEALTH_PLAN.md`: a CODE-2c landing record per function, with the stage list written BEFORE the cut.
- `PRE_DEPLOY_PLAN.md` §2: the S10b row, struck when both land.
- `STATUS.md` ▶ NEXT UP.
- `CLAUDE.md`:
  - the LIVE STATE line;
  - the File Reference row for `diplomatic_executor.py`;
  - the "Before Modifying" rows for diplomacy execution and the settlement's ratifier.
- At the close, this file rewritten for S11 (UXR-3, `UX_UI_REVIEW_PLAN.md` §UXR-3), with every S11 decision made in it as this one was, so nothing waits on the user.

**Open with the user:** nothing. UXR-4 (their eyes at 5120×1440) is scheduled at S15 with the deploy.

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a ratchet, re-record a series without a stated reason, or tune an instrument to a fix.
