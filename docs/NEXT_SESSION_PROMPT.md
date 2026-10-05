# NEXT SESSION PROMPT — Score Finish Step 9: the residue of the final reading

> Overwritten each time a session hands off. Current hand-off: **October 5, 2026,
> after Step 8, SF-R "the final reading", was read** (memo
> `docs/audits/SCORE_FINAL_2026_10_05.md`).
> Routing authority: `docs/SCORE_FINISH_SPEC.md` §3 Step 9; `docs/STATUS.md`
> ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line point there.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Score Finish Step 9, "the residue of the final reading".** Work directly on master per `CLAUDE.md`'s workflow. Commit and push at every clean slice.

**Where things stand.**
- **The final reading** (`docs/audits/SCORE_FINAL_2026_10_05.md`):
  - directional 6.71 → 7.50 over 13 of 14;
  - 8 of 14 pillars at target;
  - **command capped at 6.00 by SFR-D11**, a P1 the reading verified at the wire: `Lannes, march home to Franche-Comte` marches to Lorraine;
  - the done-when NOT met.
- **The census:** defect **77 OPEN** (1 P1 · 30 P2 · 39 P3 · 7 P4); design 2 OPEN (SF-NAV-1-D1, SFR-DR1 — the user's). Run `tools/defect_census.py --by-pillar` to see them.
- **The rows:** every one is in `docs/BUG_FIXES.md` §Score Finish Step 8, tagged `⟨SF step=9 · SF-RRn · pillar=…⟩`.

**The slices** (`SCORE_FINISH_SPEC.md` §3 Step 9 — the table names each slice's rows, its done-when and its test file):
1. **SF-RR1 "the orders the reading met"** — **SFR-D11 first** (the adverb "home"/"back" rides into the destination and the nearest-province reading replaces a province the player named; reproduce at `POST /command` with Lannes placed at Rhineland), then the HOLD's order misses SFR-H1 … H3, H5 … H7, H13 (H1's root is measured: `condition_grammar._PREMISE_RE` cannot read "Mack's still in") and the depth campaign's command rows.
2. **SF-RR2 "the desk answers what was asked"** — the HOLD's question misses and the depth campaign's desk shrugs.
3. **SF-RR3 "the page and the copy"**.
4. **SF-RR4 "war, truce and the standing order"** — opens with **SFR-DR1's probe**: on the CMD-A save at turn 31, name per league court the rung each corps chose and the restraint that held it. The ruling after the probe is the user's.
5. **SF-RR5 "the frames at both scales"** — ⛔ needs Godot windows: ASK the user first.
6. **SF-RR6 "the instrument reads what the player sees"** — the three wrong readers and the drifted DL arm (SFR-I2 … I7), then re-read BOTH archives (`docs/audits/score_runs/2026_09_29_c20d5bba` and `…/2026_10_05_sfr`) with the corrected readers and publish the deltas.

**After each slice:** its session exit re-reads the AUTO items it touched with `score_run.py check` and reports item flips, never a score (§5). The reading itself stands as measured.

**Waiting on the user:**
- §6 rows 18 and 22 (recommendations not applied — before any next reading);
- rows 17 and 19–21 (FOR USER CONFIRMATION);
- SFR-DR1;
- the six provisional EYES marks the panel gave (memo §1), and UI/UX C5/C6 (unmarked).

**Rules (the user's, verbatim where quoted):**
- **The user's own words:**
  - "ASK me before driving the game window — I play games on this machine. The sign-offs stay mine."
  - "Never edit tracked files while it runs, never use --no-verify, and never kill a `-m backend.main` process (my live game)."
  - "If an M-metric leaves its band, report it with attribution and put it to me; do not tune."
- **Committing:** from the Bash tool, in the background: `env -u PYTHONIOENCODING git commit -F <msg>` with the output in a scratch log; check the log for `[pre-commit] OK` (~25 min).
- **Scripts:** write patch scripts with the Write tool, never heredocs (backslashes, quotes and em dashes break).
- **Benchmark runs:** `score_run.py run --only` is append-style (repeat the flag); `run --only X --out DIR` REWRITES `DIR/run.json` with X alone — copy it first and merge. `run --live` (or `--only OP-LIVE`) spends API calls; a session exit never does.
- **The panel:** `tools/score_panel.py eyes RUN`, then `check --eyes RUN/eyes_panel.json`, then `score_panel.py publish RUN`, then `compare`.
- **Any `.gd` change:** run the parse harness (Start-Process, exit code) and a boot smoke (`--headless … res://scenes/main.tscn --quit-after 400 --log-file <log>` with `SOVEREIGN_PORT` set to an unused port; grep `SCRIPT ERROR`).
- **Every slice gets a mutation sweep.** Never run it while the suite runs; run `git diff` after it.
- **`BASELINE_SERIES` and M1–M7** stay byte-identical unless the slice says otherwise.
- **Every commit carries:** the landing record, STATUS ▶ NEXT UP, the CLAUDE.md LIVE STATE line, the BUG_FIXES / DESIGN_REFINEMENT dispositions, the SYSTEMS_REFERENCE section and the census line.
- **Overwrite this file with your own hand-off in your last commit.**

**Traps learned on October 5:**
- **The digest's `enemy phase:` lines quote text the client never renders** (`tools/_name_census.py` UNRENDERED_PATHS). Never file a raw key or a voice from them.
- **A reader keyed on copy goes blind when the copy changes.** An item that falls from ✓ to `·` is the first sign (SFR-I4: "Marshal X's claim" became "X's claim").
- **An item's evidence string is truncated** (`misses[:4]`). Read the reader's full list before filing.
- **The ledger's census reads tags and upper-case words:** never write the phrase OPEN REMAINDER in a closing note, and keep an OPEN row's last cell free of FIXED / CLOSED / BUILT.
- **A digest line beats an agent's summary.** The depth campaign's claimed P1s were re-graded on the digests: one was the driver's own fixed answer, and one was a warning, not a loss.
