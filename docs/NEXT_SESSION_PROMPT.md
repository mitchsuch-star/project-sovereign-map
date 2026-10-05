# NEXT SESSION PROMPT — Score Finish Step 8: SF-R, the final reading

> Overwritten each time a session hands off. Current hand-off: **October 5, 2026,
> after Step 7b "The front page of the peace" landed** (the Step 7 exit `88cd6378`
> and the Step 7b commit that carries this file, both pushed).
> Routing authority: `docs/SCORE_FINISH_SPEC.md` §3 Step 8 (and §4 for the
> method); `docs/STATUS.md` ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line point
> there.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Score Finish Step 8, SF-R "the final reading".** Work directly on master per `CLAUDE.md`'s workflow. Commit and push at every clean slice.

**Where things stand.** Steps 0–7b are landed and pushed. The census reads **defect 0 OPEN, design 1 OPEN (SF-NAV-1-D1, the user's)** (`tools/defect_census.py --open`). Waiting on the user, all FOR USER CONFIRMATION:
- §6 rows 17–22 (`docs/SCORE_FINISH_SPEC.md` §6). Row 22: economy C1 and marshal drama F1, the field read's measured cost.
- **Step 7b's frames:** the dispatch view and the Balance of Europe tab at both Interface Scales. They launch Godot windows, so they wait on the user's word.
- The standing sign-offs: the end screen's four registers, F3's six surfaces, F5's header, the Congress surfaces, VP-R1's muster rows.

**Step 8** (`docs/SCORE_FINISH_SPEC.md` §3 Step 8):
1. **The instrument on the final tree,** with the same checklist version as the baseline: `.venv/Scripts/python.exe tools/score_run.py run --skip SUITE --jobs 2 --out tools/playtest_runs/score_<date>_sfr`, then `check`, then `compare --base docs/audits/score_runs/2026_09_29_c20d5bba`. Run the SUITE arm too, or record why not.
2. **The blind panel and the user's EYES items.** ⛔ The EYES items and any frame need Godot windows: ASK the user first.
3. **HOLD, written fresh,** then read on BOTH trees in the same session: the final tree, and `c20d5bba` on a detached worktree (`git worktree add --detach <path> c20d5bba`).
4. **One hand-played depth campaign** (keyed, then a keyless stretch), for the findings rate, not the score.
5. **The re-score memo:** every pillar's item flips since the baseline, the median and the spread, and the census.

**What Step 7b left on the board** (`docs/SYSTEMS_REFERENCE.md` §94):
- The next league is read by ONE function, `coalition.league_forecast`. It feeds the dispatch's coalition section, the Balance of Europe tab (THE NEXT LEAGUE), the desk ("who will march against us?", "what keeps Austria out?"), the counsel (at peace) and the morning's league headlines.
- Every morning has a headline. The standing family shares one lead allowance, and no class leads more than 4 of any 10 turns unless it is that turn's event news.
- The driver records the whole page (`headline_text`, `sub_beats`, `league_rows`, `league_line`). Living balance C5's probe reads it and checks every quoted keep-out lever on the arms' saves.
- The Step 7b exit's archive is `docs/audits/score_runs/2026_10_05_step7b/`. Its `compare.md` holds the flips against the Step 7 final reading and against the baseline.

**Rules (the user's, verbatim where quoted):**
- **The user's own words:**
  - "ASK me before driving the game window — I play games on this machine. The sign-offs stay mine."
  - "Never edit tracked files while it runs, never use --no-verify, and never kill a `-m backend.main` process (my live game)."
  - "If an M-metric leaves its band, report it with attribution and put it to me; do not tune."
- **Committing:** from the Bash tool, in the background: `env -u PYTHONIOENCODING git commit -F <msg>` with the output in a scratch log; check the log for `[pre-commit] OK` (~25 min).
- **Scripts:** write patch scripts with the Write tool, never heredocs. The Bash tool mangles backslashes and quotes, and a heredoc holding an em dash or an apostrophe can fail outright.
- **Benchmark runs:** `score_run.py run --only` is append-style; repeat the flag, since a comma list selects nothing. `run --only X --out DIR` REWRITES `DIR/run.json` with X alone, so copy the run record first and merge.
- **Any `.gd` change:** run the parse harness (Start-Process, exit code) and a boot smoke (`--headless … res://scenes/main.tscn --quit-after 400 --log-file <log>` with `SOVEREIGN_PORT` set to an unused port; grep `SCRIPT ERROR`). The project's main scene is the main menu, so name `main.tscn` explicitly.
- **Every slice gets a mutation sweep.** Never run it while the suite runs; run `git diff` after it.
- **`BASELINE_SERIES` and M1–M7** stay byte-identical unless the slice says otherwise.
- **Every commit carries:** the landing record, STATUS ▶ NEXT UP, the CLAUDE.md LIVE STATE line, the BUG_FIXES / DESIGN_REFINEMENT dispositions, the SYSTEMS_REFERENCE section and the census line.
- **Overwrite this file with your own hand-off in your last commit.**

**Traps learned on October 5:**
- **The coalition tick runs after `advance_turn` moves the turn on.** A forecast of the next tick must read every clock one turn ahead (SF7-X45), and a pin that ticks without advancing the turn cannot see the difference.
- **A sweep of a heading or rotation rule needs a staged board with VARIETY.** Two classes cannot satisfy "≤ 4 of 10".
- **A court within a buy-off's +5 of the bar is the only board that shows the buy-off "enough alone".** The pin must stage one, or the sweep calls the rule INERT.
- **`Arm.blocks()` needs a newline before the first `## Turn` heading.** A hand-built digest must start with a header line.
