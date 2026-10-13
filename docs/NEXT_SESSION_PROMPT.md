# NEXT SESSION PROMPT — Pre-Deploy S10: CODE-2b, the monster functions

> Overwritten each time a session hands off. Current hand-off: **October 13,
> 2026, after S9b landed UXR-2's adjustability extras** in four commits on
> master: A `1f91f761` Text size, B `a472497f` HUD width + `[− ⌂ +]`,
> C `786839b9` the map's furniture, D (the commit after it) High contrast.
> - **Text size** (Settings → INTERFACE, 100–175 %) scales the theme's named sizes alone. At 150 %, 550 of 550 text rows scale exactly, 0 RED.
> - **HUD width: Full · Centred** gathers the HUD into a 2560-px band, driven at 5120×1440. ⌂ fits Europe.
> - **The map's furniture** holds a 16-px screen-space floor (`map_small` 34 → 0).
> - **High contrast** raises every dim grey: contrast under the floor fell 20 → 0 on the five named surfaces.
>
> Records: `docs/UX_UI_REVIEW_PLAN.md` §UXR-2, the S9b landing record; rules `SYSTEMS_REFERENCE.md` §112; rows `BUG_FIXES.md` §UXR-2's extras (UXR-X21 … X28).
> Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2 (S9b STRUCK; **S10 is NEXT**), with `docs/STATUS.md` ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line pointing there. The Score Finish residue (`SCORE_FINISH_SPEC.md` §3 Step 9) stays PAUSED until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S10 — CODE-2b, the monster functions the two deep dives did not absorb.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S10. Work directly on master per `CLAUDE.md`'s workflow, and commit and push at each clean slice. Run `git fetch origin` first and read `git log -5 --stat` before touching anything. Use Plan Mode first (the user's standing preference for a non-trivial session). Land the first function, then pause for review.

**The work.** `docs/CODE_HEALTH_PLAN.md` §CODE-2: the recipe and its CODE-2a landing record. There, `_execute_attack` became twenty `_attack_*` stages behind one `AttackContext`, byte-identical.
- **The three functions for S10:** `execute_command`, `format_event_oneliner` and `_execute_strategic_command`, one each, as S8b did one.
- DD-0 already took `_parse_with_mock_chain` and `_execute_one`. DD-1 took `_process_dialogue_choice` and `_ratify_treaty`.
- **The recipe:**
  - Write the stage list in the landing record BEFORE editing.
  - Use one context object, built once, that never reaches the wire.
  - Move code, do not rewrite it.
  - Turn early returns into stage results the driver checks.
  - Run the fast gate after each stage.
  - The docstring becomes the stage index.
- **Done when:** none of the three is over 500 lines. The census pin caps "functions over 500 lines" at the new count (33 at S8b).

**Read first, in this order:**
- `CODE_HEALTH_PLAN.md` §CODE-2 and the CODE-2a landing record.
- `tests/test_code2a_the_attack_is_staged.py`, the shape pin to model a new one on.
- `tests/test_code_health_ratchet.py` and `tools/_code_health_census.py`.
- Each function's own file: `backend/commands/executor.py` (`execute_command`), `backend/campaign_log.py` (`format_event_oneliner`) and `backend/commands/strategic_executor.py` (`_execute_strategic_command`).

**The net.** `BASELINE_SERIES` + M1–M7 (`tests/test_combat_sweep_metrics.py`), the golden parser corpus, and the score arms. A split that passes all of them byte-for-byte has not changed behaviour.
- A re-record needs a stated reason, and a pure refactor has none.
- The function-local-import hazard (F2's regression) is pinned for the combat executor. Check any function you split for the same pattern.

**Traps — earlier sessions paid for each of these:**
- **Memory is thin on this machine.** About 1–5 GB is free while the user plays and browses.
  - The hook can die in collection with a `MemoryError`, or a subprocess-driven test (RS-27's 40-turn drive) can come back empty. Both passed on a plain retry. Check free memory before blaming the code.
  - **Never run two Godot engines at once:** two capture shoots crashed with 0xC0000005 (a null `mem`, a failed Vulkan swap-chain resize).
- **The hook.** It runs ruff and the full parallel suite (~7.5 min). Commit with `run_in_background: true` from Bash, using a message file and never `--no-verify`, and make no tracked edit while it runs. Read the hook log's `[pre-commit]` and `EXIT=` lines before believing a commit.
- **Shell.** A Bash heredoc aborts on a `'` inside `python - <<EOF` and mangles backslashes. Write scripts with the Write tool and run them by path.
- **Git.** Never `git add -A`; stage by name.
- **Ledgers.** A new OPEN row in `BUG_FIXES.md` needs an `⟨SF step=… · pillar=…⟩` tag (`test_score_finish_step0.py`).
- **Running things.** `ruff` is not on Bash's PATH: use `".venv/Scripts/python.exe" -m ruff check backend/`. Never kill a `-m backend.main` process; run a test pair beside the user's 8005 with `SOVEREIGN_PORT=8006`.
- **Docs caps.** `CLAUDE.md` sits near its 62,000 B cap: pay for a new LIVE STATE row by cutting the oldest. `STATUS.md` keeps seven ▶ blocks at most; the oldest goes to `docs/archive/STATUS_2026_Q4.md`, newest first.
- **Godot edits** (should S10 touch any): re-run the parse harness via `Start-Process`, read its exit code, and re-commit `tools/godot_parse_report.json`.
- **The capture window now ignores OS input** (UXR-X24): it used to take the user's keystrokes.

**Code-health rules in force:**
- A new lever lives one session past its attribution, then retires at the next slice's head (`tools/retire_lever.py`). CODE-1's November batch takes its head once October closes.
- A combat fix lands in the `_attack_<stage>` that owns it.
- The layout law is a census.
- A new font size is a theme step, not an override (`RAW_RATCHET` 11).
- Any dim grey goes through `Utils.toned` / `toned_hex` / the COLOR tokens (High contrast).

**The records each commit carries:**
- `CODE_HEALTH_PLAN.md`: a CODE-2b landing record per function.
- `PRE_DEPLOY_PLAN.md` §2: the S10 row (struck when all three land).
- `STATUS.md` ▶ NEXT UP.
- The `CLAUDE.md` LIVE STATE line, and its "Before Modifying" row if a function's navigation changes.
- This file, rewritten for S11 (UXR-3).

**Open with the user:**
- UXR-4, the eyes-on sign-off at 5120×1440. It now includes S9b's frames: Text size, Centred, the map's furniture (UXR-X28's crowding is S12's) and High contrast.
- EG-D1 … EG-D3.

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a ratchet, re-record a series without a stated reason, or tune an instrument to a fix.
