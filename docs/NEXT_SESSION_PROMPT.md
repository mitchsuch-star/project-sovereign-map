# NEXT SESSION PROMPT — Pre-Deploy S8b: CODE-2a "`_execute_attack` split into named stages", CODE-1 batch 6 at its head

> Overwritten each time a session hands off. Current hand-off: **October 12,
> 2026, after S7b landed CODE-3 + DD-C with CODE-1 batch 5 at its head** —
> `backend/errors.py` (`report(exc, site)` once per site at WARNING, the
> stack without Python's "Traceback" header, a display-only tally behind
> `/debug errors`), the census's `reports` class and broad-tuple reading,
> **silent handlers 367 → 6** (the console tee's five and the reporter's
> own guard, named in `TestEveryBroadExceptSpeaks`), **0 report sites in
> five played campaigns**; DD-C's typed `SaveError` raised by the save
> path's stages and converted at every door into a sentence and a WARNING
> with its site (the doors never raise — FA-S15-2's ruling), the Load menu
> listing what it cannot read, a failed Final save on the rail, **40 of 40
> injected faults reaching the player over the commanded forty-turn
> campaign**; batch 5 retired 71 levers (**429 → 358**) and found the
> retire tool's `False`-lever seed (DDC-6, fixed and pinned). Landing
> records `docs/CODE_HEALTH_PLAN.md` §CODE-1 BATCH 5 + §CODE-3 parts 1–2
> and `docs/PRE_DEPLOY_PLAN.md` §3 "DD-C landing record"; rules
> `SYSTEMS_REFERENCE.md` §110; rows `BUG_FIXES.md` DDC-1 … DDC-6 (all
> FIXED). Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2 (S7b STRUCK;
> **S8b = CODE-2a is NEXT**) → `CODE_HEALTH_PLAN.md` §CODE-2; `docs/STATUS.md`
> ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line point there. The Score
> Finish residue (`SCORE_FINISH_SPEC.md` §3 Step 9) stays PAUSED until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S8b — CODE-2a: `_execute_attack` split into named stages behind one context object, CODE-1 batch 6 at its head.** Routing authority = `docs/PRE_DEPLOY_PLAN.md` §2 → `docs/CODE_HEALTH_PLAN.md` §CODE-2 (the recipe, the risk and its control, the done-when). Work directly on master per `CLAUDE.md`'s workflow; commit and push at each clean slice. `git fetch origin` first and read `git log -3 --stat` before touching anything. Plan Mode first (the user's standing preference for a non-trivial session).

**The head: CODE-1 batch 6** (`CODE_HEALTH_PLAN.md` §CODE-1 BATCH 5's "Next batches"): the **125** pre-October levers no batch named — the `backend/ai/` and `backend/commands/` modules OVER 1,500 lines and the top-level / `models/` modules (`strategic.py` 19, `clause_guards.py` 15, `question_desk.py` 15, `economy_executor.py` 12, `llm_client.py` 11, `executor.py` 9, `dialogue_routing.py` 7, `disobedience.py` 7, `parser.py` 7, three each in `campaign_log.py` / `diplomatic_executor.py` / `movement_executor.py` / `objection_v2.py` / `strategic_executor.py` / `dialogue_manager.py`, one each in `meta_executor.py` / `display_names.py` / `intel_report.py` / `authority.py` / `marshal.py`). NOT in it: `LITERALS_DRILL_TO_HEAL` (AIDR-D1's decided `False` — a decision, it stays) and `THE_LEAGUE_TREATS_WHEN_SPENT` (a staging device; it retires with its October bundle). Re-run `tools/retire_lever.py --list backend` first (in the background — it blames every lever); the October ones keep their session. Record the batch in the landing record; lower `LEVERS_CAP` to the census's reading.

**Read first, in this order:** `CODE_HEALTH_PLAN.md` §CODE-2 whole (the recipe: the stage list written in the landing record BEFORE editing; one `@dataclass AttackContext` built once at the head, never on the wire; move code, do not rewrite it — a stage body is a cut-and-paste with its locals renamed `ctx.<name>`; early `return`s become stage results the driver loop checks; after each stage the fast gate); `backend/commands/combat_executor.py::_execute_attack` (**3,921 lines, 378 `if`s** today) and the pipeline its own comments document (pre-validation → crossing gate → objection → coordination → reinforcements → resolve → the post-combat pipeline steps 1–12 → capture → report → events); `tests/test_combat_sweep_metrics.py` (M1–M7) and the series pins (`tests/test_ai_intent_threat_migration.py`, `_variance`, `_assurance`) — the net; `tests/test_ep_f2_the_display_name_pass.py::test_the_humaniser_is_the_module_level_name_in_the_combat_executor` (the function-local-import shadow pin — ⚠ the plan names a `tools/_local_import_census.py` that DOES NOT EXIST; this pin is the census, and it forbids ANY function-local import inside `_execute_attack`); `tests/test_code_health_ratchet.py` (`FUNCTIONS_OVER_500_CAP` 34 — it falls by one when `_execute_attack` is staged).

**Corrections the reads established (do not re-derive):** a stage that moves a function-local import changes which names are LOCAL to the function it leaves — F2's regression (an `UnboundLocalError` on every AI attack against a corps that had just retreated); every moved import is re-checked against the shadow pin. The tool `tools/retire_lever.py` now seeds each climb with the lever's OWN value (`definition_value`) — a `False` lever's rewrites are right; still read every `False` lever's diff by eye, and scan for dead code after an inlined `return` and for a `getattr` folded to `if True:` (batch 5 found three of each shape and fixed them by hand). Every broad `except` in `backend/` now reports (`backend.errors.report`, a literal site); a moved handler keeps its site string verbatim — the site literals are unique across `backend/` and pinned so.

**Slices, each landed with its pin:**
1. **CODE-1 batch 6** — the tool, the hand sites, the dead-code scans, the orphaned lever headers (comments only, AST-verified against a snapshot), the test arms decided one by one (agents on disjoint file groups, the recipe and the traps as the brief, grep-verified).
2. **CODE-2a** — the stage list in the landing record first; then `AttackContext`, one stage at a time, the fast gate after each (M1–M7, the series pin, the combat test files, the shadow pin); the function's docstring becomes the stage index; the `CLAUDE.md` "Before Modifying" combat row names the stages, not the lines.

**Done when:** `_execute_attack` is a driver of named stages, none over 500 lines; `FUNCTIONS_OVER_500_CAP` lowered to the reading; `BASELINE_SERIES` + M1–M7 byte-identical with no re-record; the corpus identical; the full suite green on the hook; levers lowered by batch 6.

**Records the commits carry:** `CODE_HEALTH_PLAN.md` §CODE-1 BATCH 6 + §CODE-2 "CODE-2a landing record" (the stage list), `PRE_DEPLOY_PLAN.md` §2 (the CODE-2a row struck), `STATUS.md` ▶ NEXT UP (seven ▶ blocks at most — the oldest to `docs/archive/STATUS_2026_Q4.md`, newest first), the `CLAUDE.md` LIVE STATE line (62,000-byte cap, lower-only, and within 8,000 of it — this session left it at 61,998: pay for a new row by cutting an older one), `SYSTEMS_REFERENCE.md` §111 if a rule moves (a pure refactor may need none — say so), `BUG_FIXES.md` rows filed for anything found, this file rewritten for the next row (`PRE_DEPLOY_PLAN.md` §2: S9 UXR-2).

**Traps.** A Bash heredoc halves backslashes, turns `\b` into a BACKSPACE byte, and aborts on a `'` inside an inline `python - <<EOF` — write every script AND every doc insertion with the Write tool, run it by path (this session hit it three times). `git add -A` never; stage by name. The hook runs ruff + the full parallel suite (~7 min): commit with `run_in_background: true` from Bash, a message file, never `--no-verify`, no tracked edit while it runs — the suite reads the WORKING TREE, so a half-landed next slice in the tree is tested too (park it in the scratchpad). Read the hook log's `[pre-commit]` and `EXIT=` lines before believing a commit; an aborted commit leaves the index staged — fix, re-stage, re-commit, and record what the hook found. `ruff` is not on Bash's PATH — `".venv/Scripts/python.exe" -m ruff check backend/`. The console is cp1252. `-n 8` without `--dist loadgroup` scatters a module's tests over workers and fakes order failures — always pass `--dist loadgroup`. `tools/playtest_driver.py` re-execs itself to pin `PYTHONHASHSEED` — set `PYTHONHASHSEED=0` to keep a monkeypatching runner in-process. The driver's default policy loses the Empire at turn 34 (The Eclipse); a forty-turn reading needs `--script tools/playtest_scripts/commanded_full40.json`. A scratch `WorldState` (a round trip, a clone) passes `WorldState.__init__`, which resets Berthier's display rotation (IQ-8 item 8) — an instrument that builds one restores `battle_report._OBSERVATION_COUNTS` around it. `core.autocrlf=true`: keep each file's own newline. Never kill a `-m backend.main` process. The blind census files stay blind.

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever, rewrite a stage's body while moving it, weaken a gate, edit a committed blind file, tune an instrument to a fix.
