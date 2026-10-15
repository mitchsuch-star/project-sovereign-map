# NEXT SESSION PROMPT — Pre-Deploy S13b part 4: DD-B fixes — the voice, the client and the sea (DDB-45 … 62, DDB-21) and the naval rail alerts (DDB-X6)

> Overwritten each time a session hands off. Current hand-off: **October 15,
> 2026, after S13b part 3 landed.**
>
> **What part 3 delivered** (three commits on master, run straight through):
> - `eba57ba4` the head — DDB-X17: the player's glorious charge (typed, answered, or fired by an attack's
>   reckless stage) is refused onto peace soil in the attack's own words, and the reckless auto-charge picks
>   no target there; the AI keeps PT-F1.
> - `ab6314a9` the orders — DDB-R1 ask first (a typed attack out of reach asks, naming the pursuit's price
>   and first march); R2 the muster gate widened to "potential disaster" for any lead, the free preview
>   taught; R4 no auto-end on either pool (the end-turn mirror, WO-22's defer, C3's guard and the warning
>   copy retired); R5 a named marshal's mismatched arm refused at no cost; R7 the rich peace's sink named.
>   The sweep's X23 (the parked muster reads the lead's reach) and X24 (the bare attack asks too).
> - `89db8acc` the garrison and the retreat — DDB-R3 a detachment at ≥ 4:1 capitulates whole (one
>   arithmetic, both boards); X1 the landing reads the one garrison predicate; X2 / X25 the copy names the
>   thresholds; R6 the engaged move names the withdrawal and its price; X3 the AI's retreat reads AAR-D4's
>   friendly set — the part's one series move (`BASELINE_SERIES` [28] 0 → 2, re-pinned with the row named).
> - the close: rows, docs, this prompt.
> - Rules `SYSTEMS_REFERENCE.md` §118; pins `tests/test_ddb_s13b_the_rulings.py` (86 by the end of part 3).
> - The series: `tools/_ddb_s13b_series_arms.py`, twenty-seven arms (`tools/_ddb_s13b_series_arms_final.json`);
>   every lever byte-identical but DDB-X3's. `tools/playtest_driver.py` gained `--seam MODULE:NAME=EXPR`
>   (hold a function seam down for a run; `docs/PLAYTESTING.md`).
>
> **The sibling sweeps found three rows** (DDB-X23 … X25), all FIXED in the part. Nothing heads part 4
> but its own rows.
>
> **Nothing waits on the user** (a code-signing certificate and the UXR-4 review are theirs before S15,
> not before this part). Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S13b part 4 — DD-B fixes: the voice, the client and the sea (DDB-45 … 62 and DDB-21) and the naval rail alerts (DDB-X6).**

Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S13b (four parts):
- **parts 1, 2 and 3** — LANDED October 14 and 15, 2026;
- **part 4** — this prompt; it closes S13b.

After S13b: S14 (SF-RR7 + the Score Finish residue, with DDB-X4 / SFR-B3 at its head), S14b VP-1, S14c the events, S14d the table lesson, S14e DD-B's re-measure (S14f its rows), S15 UXR-4 + code signing + the deploy.

Each row in `docs/BUG_FIXES.md` §DD-B carries its cause (file:line) and its **decided fix**: that is the spec, so implement it as written. Line numbers were read on `0e2002e8`; parts 1 – 3 moved `combat_executor.py`, `executor.py`, `strategic.py`, `strategic_executor.py`, `objection_v2.py`, `world_state.py`, `movement_executor.py`, `economy_executor.py`, `naval_executor.py`, `garrison_report.py`, `meta_executor.py`, `main.py` and `main.gd`, so navigate by the symbol.

**How to work:**
- Work directly on master per `CLAUDE.md`. Commit and push each slice.
- Run `git fetch origin` first and read `git log -8 --stat` before touching anything.
- **Every decision is already made.** The user's rulings ("make all decisions … nothing hanging", October 13; "make design calls …", October 14) make this prompt the approved plan.
  - Do not stop for Plan Mode approval, and do not pause between slices.
  - The rules below settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

**The sibling sweep (the user's ruling, October 14 — it holds for every row):**
- Every fix ends with a search for its class: the same mechanism on the other courts, dialogues, popups and roads, both combat copies (the executor's pipeline and the reckless auto-charge in `world_state._process_reckless_cavalry_turn_start`), and the AI's side of the same executor.
- Each sibling found is filed in §DD-B's second table as `DDB-X<n>` (the next is **DDB-X26**), with its tag `⟨SF step=pre-deploy S13 · DD-B · pillar=…⟩`.
- It is fixed in the same slice with its own test (`tests/test_ddb_s13b_the_rulings.py::TestDDBX<n>`).
- A sibling too large for the slice heads the next session's work (S14's head). Nothing found is homed after the deploy.
- Each commit message names its sweep: what was searched, and what was found.

**Read first:**
- `BUG_FIXES.md` §DD-B: its preamble, the rows DDB-21 and DDB-45 … 62, and DDB-X6 in the second table;
- `SYSTEMS_REFERENCE.md` §116 – §118 (parts 1 – 3's rules — §118.4 no auto-end, §118.7 the capitulation, §118.8 the withdrawal);
- `NAVAL_SPEC.md` §14 (the landing record), §17.3 and §18.4 (the rail alerts DDB-X6 builds);
- `CLAUDE.md` "Before Modifying": the naval row, the popup recipe, the question desk (`question_desk.py`), the notice rail (`notifications.py`, `notification_bar.gd`).

**Tests** — each slice's rows in `tests/test_ddb_s13b_<slice>.py::TestDDB<n>` as the row names it (`the_voice`, `the_client`, `the_sea`), and DDB-X6 in `tests/test_ddb_s13b_the_rulings.py::TestDDBX6`. Drive the real endpoints (the in-process TestClient on the 1805 boot or the board the row was seen on), never a mocked executor. When a row lands, mark it FIXED in its Status cell with the commit and the test, keep its tag, and say that the sighting's re-play is S14e's.

### Slice 1 — the voice: DDB-45 … 53 (one commit)

The question desk, the notice rail, the command reference and the dispatch's lines: the two-part question (45), stale rail cards (46), "to join Ney and Davout" (47), "How do I …?" (48), the reference's developer note and Congress count (49), a released marshal announced (50), a war purpose against an eliminated court (51), the alarm that "holds" (52), one siege's three contradicting lines (53). Each row's decided fix is the spec.

### Slice 2 — the client: DDB-54 … 57 (one commit)

Escape after a typed order (54), the title caption (55), an ally's lost province in good news's colour (56), the command window's four lines and the wheel (57). `.gd` edits: regenerate `tools/godot_parse_report.json` (the Start-Process harness, `EXIT=0`), and drive what can be driven headlessly (`tools/cx7_predictor_harness.gd`'s idiom). The UXR-4 marks are the user's at S15 — do not pre-empt them.

### Slice 3 — the sea: DDB-21, 58 … 62 and DDB-X6 (one commit)

The stranded corps on titled soil (21, P2), the Admiralty's ports (58), its automatic states (59), the postures (60), the readiness rot and the blockade's price (61), the named yard (62), and the rail alerts for a blockade's start / end and a diversion window's opening / shutting (X6). Run `tools/gen_port_anchors.py --audit` and `--check` if anything touches a coast. Re-measure `BASELINE_SERIES` with an attribution arm for any rule the AI also reads (a seam in `tools/_ddb_s13b_series_arms.py`; re-pin with the row named if it moves).

### The close (S13b struck)

**Rows:**
- DDB-21, DDB-45 … 62 and DDB-X6 FIXED in `BUG_FIXES.md` §DD-B (commits and tests); any found rows FIXED, or heading S14.
- §DD-B's preamble: S13b STRUCK — every row of DDB-1 … 62, R1 … R7 and X1 … X25 closed but DDB-X4 (S14's head with SFR-B3).

**Docs:**
- `PRE_DEPLOY_PLAN.md` §2: S13b part 4 landed, S13b STRUCK; **NEXT = S14**.
- `STATUS.md` ▶ NEXT UP: a new block (seven kept; the oldest to the top of `docs/archive/STATUS_2026_Q4.md`).
- `CLAUDE.md` LIVE STATE: the cap is ≤ 62,000 B, so trim the oldest line as you add one.
- `SYSTEMS_REFERENCE.md` §119: the new rules.
- This file, rewritten for **S14** (SF-RR7 + the Score Finish residue, DDB-X4 / SFR-B3 at its head; read `docs/SCORE_FINISH_SPEC.md` §3 Step 9 and the S14 row of `PRE_DEPLOY_PLAN.md` §2 first).

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Check `tasklist | grep -ci godot` before any engine start. The user may have the game open ("Ink & Iron (DEBUG)") — never touch that window or its process. The hook drives Godot (the engine group), so start no engine during a commit. After any `.gd` edit, regenerate `tools/godot_parse_report.json`.
- **Never touch the user's live 8005 backend.** A driven check runs on `SOVEREIGN_PORT=8006` or above with `INK_IRON_SAVE_DIR` set.
- **The hook tests the working tree, not the index.**
  - Park a later slice's test edits outside `tests/` before committing an earlier slice. An untracked test in `tests/` runs in the hook.
  - Do not edit files the tests read while a commit's hook (or your own full-suite run) is running — the backend and the docs included (the census and the plan pins read `BUG_FIXES.md`). Draft in the scratchpad, apply after.
- **`PYTHONDONTWRITEBYTECODE=1`** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING`.
- **The hook** runs ruff and the full parallel suite (about 7 minutes; 31,2xx tests at part 3's end).
  - Commit with `run_in_background: true` from Bash, with a message file, and never `--no-verify`.
  - Read the log's `[pre-commit]` and `EXIT=` lines before believing a commit.
  - Run the full suite yourself once (in the background) before the commit to find a slice's fallout; the hook is then a confirmation.
  - `test_fa_slice12_the_road_home …::test_the_offer_is_reported_before_the_warning_it_answers` failed once under the hook in part 3 and passed alone and under every seed: a flake — re-run it alone, then re-commit unchanged.
  - The G4 timing pin can fail under load. Re-run it alone; if it passes, re-commit unchanged.
- **A byte-pinned series.** If a decided fix moves one (`BASELINE_SERIES`, the M-pins, a seeded digest), re-pin it in the same slice, naming the row as the reason, with its attribution arm recorded. A move no row explains is a bug in the slice. **No new module lever:** the code-health ratchet (`LEVERS_CAP`) forbids one, so an attribution arm patches a function seam in the child; run the arms with `--prior <the HEAD series>`. A re-pin adds a link to the series chain pins (`test_ai_drill_fix`, `test_dp1`, `test_rf3`, `test_vp_r1`, `test_economy_audit`): the last record's ALL arm is the new record's prior.
- **Paid for in part 3:**
  - **A pause can strand a commit.** R2 pauses non-cautious leads, and the parked muster's live check read adjacency — a cavalryman's committed attack was retired (DDB-X23). When a change makes a path common, read the path's own re-validation.
  - **An exemption on the objection battery skips its validations too.** The `if should_check_objection:` block also refuses (fortified, AP …): exempt the DRAW only, at the evaluation, never the whole block.
  - **A driven arm re-routes by a decided fix.** Diff HEAD and the tree (a `git worktree` at HEAD in the scratchpad) on the world stream with message text stripped; re-seat only on the row's own decided effect. A function seam can be held down for a driven arm with the driver's `--seam MODULE:NAME=EXPR`.
  - **Raw keys in new copy.** Every marshal name in a new line goes through `humanize_entity_name` ("ArchdukeJohn" failed the display census).
  - **Copy changes move pins in files you would not guess** (the scout, the works halt, the help, the engaged refusal each had pins in three or four files): run the suite before the commit.
- **The function at 500 lines.** `turn_manager.end_turn` is under 500 again (C3's guard retired); `FUNCTIONS_OVER_500_CAP` still holds — a line added to a function near 500 goes in a helper.
- **The judge is shared.** `tools/_score_probes.py` is read by the census records and the score archive. Check any edit against every committed census record (`docs/audits/unrehearsed/`) and the HOLD arms first.
- **The census reads closing words.** In a Status cell, an uppercase FIXED / RULED / BUILT / RE-HOMED closes a row. Write them only when the row is truly closed, and keep them lowercase in an OPEN row's prose.
- **Dialogue and popup wiring** (`CLAUDE.md` "Adding a new popup/dialog"): every POST handler goes through `build_base_response`; a new dtype goes on the `main.gd` whitelist; a popup that must arrive with its dialogue carries the dialogue's id.
- **Monkeypatch the type, never a method on `M.executor` / `M.parser`.** In a TestClient world swap, swap `M.world`, `M.game_state` and `M.parser` together.
- **Shell:**
  - Bash heredocs mangle backslashes and quotes: write scripts with the Write tool and run them with `-X utf8`; an exact-substring helper with a `PAIRS` spec file keeps each file's line endings.
  - A redirect into a directory that does not exist fails the command before it runs; write logs to the absolute scratchpad path.
  - GDScript `:=` cannot infer from an untyped value; type such locals explicitly.
- **Git:** never `git add -A`; stage by name. **Line endings:** the tree is mixed CRLF / LF; keep each file's own.
- **Docs caps:** `CLAUDE.md` ≤ 62,000 B; `STATUS.md` keeps seven ▶ blocks.

**Code-health rules in force:**
- A new font size is a theme step, not an override (`RAW_RATCHET` 1).
- A grey is a named palette token.
- A control that cannot act is disabled with its reason (`Utils.set_available`).
- A fix lands in the stage that owns it.
- Golden Rule 1: combat modifiers live in `marshal.py` alone.
- Golden Rule 5: player and AI share systems; the rulings name where they differ.
- Golden Rule 6: the LLM never affects mechanics.
- Golden Rule 8: no per-region scan in a hot path.
- Golden Rule 9: nothing deferred without a home.

**Open with the user:** UXR-4 at S15 (S12's eleven R2 marks, and S12b's and DD-B's frames), and a code-signing certificate before S15. Nothing in part 4 waits on either.

**Do not:**
- edit `docs/UX_CHECKLIST_V1.json`;
- re-score, add a lever, or weaken a gate or a ratchet;
- change a rule no row or ruling names;
- touch the Score Finish residue or start S14.
