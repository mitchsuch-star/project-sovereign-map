# NEXT SESSION PROMPT — Score Finish Step 7: the frames, then the Step 7 exit, then Step 7b

> Overwritten each time a session hands off. Current hand-off: **October 4, 2026
> (late evening), after Step 7 slices 1–8 landed** (last commits `3dd9a89a`
> slice 7 and the slice-8 commit that carries this file, both pushed). The user ended the session with
> *"finish up make next session do that part"* — "that part" being the frames.
> Routing authority: `docs/SCORE_FINISH_SPEC.md` §3 Step 7 (the landing records
> of slices 1–8 are its "Step 7's progress" bullets); `docs/STATUS.md` ▶ NEXT UP
> and the `CLAUDE.md` LIVE STATE line point there.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Score Finish Step 7, the closing part: the frames, the Step 7 exit, then Step 7b ("The front page of the peace").** Work directly on master per `CLAUDE.md`'s workflow. Commit and push at every clean slice.

**Where things stand.** Step 7 slices 1–8 are landed and pushed. The census reads **defect 0 OPEN, design 1 OPEN** — SF-NAV-1-D1, which is the user's (`tools/defect_census.py --open`). Waiting on the user, all FOR USER CONFIRMATION:
- §6 rows 17–21 (`docs/SCORE_FINISH_SPEC.md` §6). Row 17's Tilsit clause build did not meet its done-when: 1 of 3 seeds.
- Slice 3's scope decision: the charge and the garrison assault keep the lead's province.
- The clause's name, `continental_system_join`.
- The standing sign-offs: the end screen's four registers, F3's six surfaces, F5's header, the Congress surfaces, VP-R1's muster rows.

**1. The frames.** ⛔ **ASK the user before launching any Godot window.** They play games on this machine, and a new window can steal focus from a fullscreen game. The sign-offs stay theirs.
- **The IQ-10 re-shoot at both Interface Scales.** Cover every surface Steps 1–6 touched, plus slice 7–8's:
  - the Build fold and its header;
  - the gold End Turn button and the once-a-turn auto-end line;
  - the counter-punch rail row's "Strike … — free" button;
  - the campaign log's tier sizes;
  - the ORDERS tab's display names.
  - Commands: `.venv/Scripts/python.exe tools/iq10_capture_payloads.py`, then `.venv/Scripts/python.exe tools/iq10_run_captures.py --scales 1.0,2.0 --date <today>`. Windows are parked off-screen at x=2565; register any new shot in the runner's `SHOTS`.
- **The settlement panel's contradictions, on screen.** SF-V2 was fixed in Step 2; this is the eyes-on check.
- **One 5-turn Mode C session** (`docs/PLAYTESTING.md` Mode C). Run a backend on `SOVEREIGN_PORT=8006` beside the user's live 8005 game, with `INK_IRON_SAVE_DIR` set to a scratch dir. Confirm Godot is frontmost before any synthetic input.
- **What the frames find:** file it as rows tagged `⟨SF step=7 · <slice> · pillar=…⟩` and fix it as a slice (each `.gd` change gets the parse harness, a boot smoke and a sweep).

**2. The Step 7 exit.**
- **Two readings**, each with `tools/score_run.py run --skip SUITE --jobs 2`:
  - the final tree (`--out tools/playtest_runs/score_<date>_step7_final`);
  - the session start `bc93ffaf` (`--tree C:/Users/User/AppData/Local/Temp/wt_start_bc93`; a detached worktree already exists there — verify `git -C <it> rev-parse --short HEAD` reads `bc93ffaf`, or recreate it with `git worktree add --detach`).
  - Memory runs tight (about 2.5 GB free while the user's game runs), so keep it at two jobs.
- **Read the readings:**
  - `check` both;
  - `compare` start→final;
  - `compare --base docs/audits/score_runs/2026_09_29_c20d5bba` → final;
  - read every exit digest for SCRIPT PRECONDITION.
- **Archive** to `docs/audits/score_runs/<date>_step7/` the way `2026_10_04_step6/` is.
- **Report item flips per seed ("on 2 of 3 seeds"), never a score** (§5).
- **Record the exit** as Step 7's closing bullet in the spec, STATUS, the CLAUDE.md line and the census.
- **Arms added during Step 7** (e.g. NAV1T-H/A/M) do not exist at `bc93ffaf`; they read as unmeasured on the start arm, which is expected.

**3. Then Step 7b** (`docs/SCORE_FINISH_SPEC.md` §3 Step 7b): every morning has a front page, and the next coalition, with the price to keep each court out, is its news. Then Step 8, SF-R the final reading.

**Rules (the user's, verbatim where quoted):**
- **The user's own words:**
  - "ASK me before driving the game window — I play games on this machine. The sign-offs stay mine."
  - "Never edit tracked files while it runs, never use --no-verify, and never kill a `-m backend.main` process (my live game)."
  - "If an M-metric leaves its band, report it with attribution and put it to me; do not tune."
- **Committing:** from the Bash tool, in the background: `env -u PYTHONIOENCODING git commit -F <msg>` with the output in a scratch log; check the log for `[pre-commit] OK` (~25 min).
- **Scripts:** write patch scripts with the Write tool, never heredocs; the Bash tool mangles backslashes and quotes.
- **Benchmark runs:** `score_run.py run --only` is append-style; repeat the flag, since a comma list selects nothing.
- **Any `.gd` change:** run the parse harness (Start-Process, exit code) and a boot smoke (grep `SCRIPT ERROR`).
- **Every slice gets a mutation sweep.** Never run it while the suite runs; run `git diff` after it, then re-run the parse harness after a `.gd` sweep (restored mtimes stale `tools/godot_parse_report.json`).
- **`BASELINE_SERIES` and M1–M7** stay byte-identical unless the slice says otherwise.
- **Every commit carries:** the landing record, STATUS ▶ NEXT UP, the CLAUDE.md LIVE STATE line, the BUG_FIXES / DESIGN_REFINEMENT dispositions (new open rows tagged), the SYSTEMS_REFERENCE section and the census line.
- **Overwrite this file with your own hand-off in your last commit.**

**Traps learned on October 4** (more in the Step 7 memory file):
- The upper-case phrase OPEN REMAINDER anywhere in a ledger row marks it partial in the census and wins over every closing word. Never write it in a closing note.
- A pin read through `/notifications` or any response re-derives the counter-punch row (`main._pending_notifications`). Read `world.notifications.get_pending()` to pin what a seam posted.
- The counter-punch is a cautious commander's strike (`has_counter_punch`): stage pins on Davout, not Ney. Davout objects to striking Mack on bad odds, so drive the objection (`POST /respond_to_objection {"choice": "insist"}`) and pin `apply_mood_variance` at both importers (executor and strategic_executor).
- A driven harness that sets state before it renders hides the default, and the sweep reads the default's mutation as INERT. Record the default first.
- Godot-driven tests error in a scratch worktree (no fonts, no import cache). Run them on master after the patch transfer: `git add -N` the new files, `git diff --binary HEAD`, then `git apply`.
- After re-basing a scratch worktree onto a new master commit, `git checkout HEAD -- docs CLAUDE.md <master-only files>` before diffing, or the transfer reverts master's edits.
