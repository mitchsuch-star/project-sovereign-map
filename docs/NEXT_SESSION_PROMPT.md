# NEXT SESSION PROMPT — Score Finish Step 9: SF-RR1 part (ii), then RR2 … RR6

> Overwritten each time a session hands off. Current hand-off: **October 5, 2026,
> after the economy gate (`docs/audits/ECONOMY_GATE_2026_10_05.md`;
> `SCORE_FINISH_SPEC.md` §6.8), which followed the economy audit (§6.7).**
> SF-RR1 part (ii) is still next. The census reads no P1.
> Routing authority: `docs/SCORE_FINISH_SPEC.md` §3 Step 9; `docs/STATUS.md`
> ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line point there.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Score Finish Step 9, SF-RR1 part (ii) "the orders the reading met", then SF-RR2 … RR6.** Work directly on master per `CLAUDE.md`'s workflow. Commit and push at every clean slice.

**Where things stand.**
- **The final reading** (`docs/audits/SCORE_FINAL_2026_10_05.md`, authoritative; it stands as measured):
  - directional 6.71 → 7.50 over 13 of 14, with 8 of 14 pillars at target;
  - command was capped at 6.00 by SFR-D11;
  - the done-when is NOT met.
- **SF-RR1 part (i) landed after the reading** (rules `SYSTEMS_REFERENCE.md` §96; pins `tests/test_sf_rr1_the_orders_the_reading_met.py`):
  - SFR-D11: `march home/back to <province>` names the province;
  - SFR-H1: the contracted premise `if Mack's still in Swabia` is read;
  - the fresh HOLD arm reads command C3 **12 of 20** (bar 18).
- **The economy audit** (memo `docs/audits/ECONOMY_AUDIT_2026_10_05.md`; rules `SYSTEMS_REFERENCE.md` §97; pins `tests/test_economy_audit_2026_10_05.py`):
  - the open list ruled under the user's delegation (§6.7): the EYES marks, §6 rows 17–22, and **SFR-DR1 ruled and BUILT** (each league member declares in its own right);
  - the books fixed, the AI spends its purse, checklist v1.1 (`docs/SCORE_CHECKLIST_V1_1.json`; a v1.1 re-read with `tools/score_reread.py`);
  - `BASELINE_SERIES` re-recorded once with fifteen-arm attribution (`tools/_econ_audit_series_arms.py`).
- **The economy gate** (memo `docs/audits/ECONOMY_GATE_2026_10_05.md`; rules `SYSTEMS_REFERENCE.md` §98; pins `tests/test_economy_gate_2026_10_05.py`):
  - EAD-1 campaign pay, EAD-2 the Charges named, EAD-4 a third of Europe's men, EAD-7 the lawful road + the league's aim, EAD-8 the league's silent courts BUILT; EAD-3/5/6/9 KEPT; EA-19 (a truce binds the league), EA-7's recovery road and EA-E8 FIXED;
  - the reading's gaps closed: the client arm, the live-key arm, and a driven client session (`tools/mode_c_driven_session.py` — engine events only, safe beside the user's running game; now part of the client arm);
  - the reading (`docs/audits/score_runs/2026_10_05_econ_gate/`): like for like 7.69 → 7.42 — campaign pay and the road cost items, every flip lever-attributed (`tools/_econ_gate_exit_attribution.json`); EG-D2 is the user's;
  - `BASELINE_SERIES` re-recorded once, twelve arms attributed (`tools/_econ_gate_series_arms.py`).
- **The census:** `.venv/Scripts/python.exe -X utf8 tools/defect_census.py --by-pillar`. Defect **83 OPEN, 0 P1**; design 3 OPEN (EG-D1 … EG-D3 — the user's).

**SF-RR1 part (ii) — the 16 open command rows** (all in `docs/BUG_FIXES.md` §Score Finish Step 8, tagged `⟨SF step=9 · SF-RR1 · pillar=command⟩`). **Reproduce every row at `POST /command` before writing a line.** The D-rows say "unverified beyond the playtester's quoted digest lines", and an agent-played depth campaign over-grades.
- **From the HOLD arm** (verified at the wire):
  - SFR-H2 — `pass the Staff law` asks for a marshal named Staff. "pass" and "adopt" should be the law router's `enact`.
  - SFR-H3 — a typo after `Tell X to` is not repaired, and `in case …` is not read as a reason clause.
  - SFR-H5 — an affordability premise is refused as a contingency. The build's own price check IS the premise.
  - SFR-H6 — `commission another marshal` reads "Another" as a candidate's name. It should open the bench.
  - SFR-H7 — a levy refused on enemy ground names the ground, not the marshal standing there.
  - SFR-H13 — a premise that is already true is refused as a contingency. Ney had beaten Mack, so the premise is a checkable fact.
- **From the depth campaign:**
  - SFR-D7 — an order naming a province the marshal is not in is carried out where he stands, without a word.
  - SFR-D8 — a reward read as a charge. The quoted reply looks like the reward road's own deed gate (F4), so it may close as not-a-defect.
  - SFR-D9 — `drill your guard` became a HOLD.
  - SFR-D10 and SFR-D38 — compounds lose their second half, and one is reported done while it was not. Read CR-7-1's relay first (`SYSTEMS_REFERENCE.md` §4 Stage 2a–2f).
  - SFR-D20 — a trailing `if he is still standing` premise.
  - SFR-D24 — `stop chasing John and hold where you are` is refused for a destination.
  - SFR-D25 — `Lannes and Murat, scout Tyrol` drops Murat. CQ-8/CQ-38 relay the second name by design, so check whether the relay line was simply unseen.
  - SFR-D37 — common phrasings that fail keyless. Part (i) left `return home to …`, `go back to …` and `withdraw home to …` honestly refused.
  - SFR-D41 — asked for cavalry, paid for infantry. Check PF-7's surfaced correction and CN-1's landing record (`docs/audits/RECRUIT_ARM_UX_2026_09_20.md`) before treating it as mechanics; the fix may be copy.

**Then the remaining slices** (`SCORE_FINISH_SPEC.md` §3 Step 9 — the table names each slice's rows, its done-when and its test file):
- **SF-RR2 "the desk answers what was asked"** — the HOLD's question misses and the depth campaign's desk shrugs.
- **SF-RR3 "the page and the copy"** — now also owns EG-X3 (a lost satellite crowded off the page: the CMD-H turn-6 page never names the Kingdom of Italy's elimination; ride it beneath the lead like the league's news, EG-X2).
- **SF-RR4 "war, truce and the standing order"** — SFR-DR1, EA-19 and EAD-7 are done (the economy audit and the economy gate). The slice owns EG-X5 (a capital whose works Austria's capture had just emptied falls to a field win with no word of them) and, if the user takes it, EG-D3's bench for the secondaries.
- **SF-RR5 "the frames at both scales"** — ⛔ needs Godot windows: ASK the user first. Now also owns the economy audit's client rows EA-E1 (the compact top bar draws blank — supersedes SFR-I3), E2, E3, E5, E6, E7 and E9.
- **SF-RR6 "the instrument reads what the player sees"** — the three wrong readers and the drifted DL arm (SFR-I2 … I7), plus EA-2 (economy F1 cannot see an off-books flow) and EG-X4 (the CMD-M turn-20 intel row places Kutuzov at Vienna from a turn-17 snapshot while the store's last sighting says Bohemia — trace which store is stale). EA-E8 is done. Then re-read BOTH archives (`docs/audits/score_runs/2026_09_29_c20d5bba` and `…/2026_10_05_sfr`) with the corrected readers and publish the deltas.

**Traps from the economy gate:** a board change surfaces LATENT display defects a census never reached (EG-X1) — trace each red driven pin before re-seating; digest groups hold the END TURN's response and a log row can surface late — judge it on its own morning (EG-I1); a benchmark arm's staging purchase can drift below its price when the economy changes (EG-I3) — read the digest for a refused commission; `score_run.py run --only X --out DIR` rewrites DIR/run.json — run into a scratch folder and merge.

**After each slice:** its session exit re-reads the AUTO items it touched with `score_run.py check` and reports item flips, never a score (§5). For SF-RR1 the cheap read is the HOLD arm:
```
score_run.py run --only HOLD --out <dir>
score_run.py check <dir>
```
Report command C3's count of 20.

**Waiting on the user:**
- EAD-1 … EAD-9, the economy gate (ROADMAP 13): the opening war's price (the E1 band), a lever on the Charges, the levy's price, the army's alarm, commissions, the neutral's hoard, the AI's purse test;
- the EYES marks are the delegate's (`eyes_delegate.json`) — the user's own marks override them;
- the rulings of §6.7 stand until the user says otherwise.

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
- **Every commit carries:** the landing record, STATUS ▶ NEXT UP, the CLAUDE.md LIVE STATE line, the BUG_FIXES / DESIGN_REFINEMENT dispositions, the SYSTEMS_REFERENCE section (Step 9 is §96) and the census line.
- **Overwrite this file with your own hand-off in your last commit.**

**Traps learned on October 5:**
- **The digest's `enemy phase:` lines quote text the client never renders** (`tools/_name_census.py` UNRENDERED_PATHS). Never file a raw key or a voice from them.
- **A reader keyed on copy goes blind when the copy changes.** An item that falls from ✓ to `·` is the first sign (SFR-I4: "Marshal X's claim" became "X's claim").
- **An item's evidence string is truncated** (`misses[:4]`). Read the reader's full list before filing.
- **The ledger's census reads tags and upper-case words:** never write the phrase OPEN REMAINDER in a closing note, and keep an OPEN row's last cell free of FIXED / CLOSED / BUILT.
- **A digest line beats an agent's summary.** The depth campaign's claimed P1s were re-graded on the digests: one was the driver's own fixed answer, and one was a warning, not a loss.
- **The strategic parser's purpose cut** (`_clean_target_text`: `\s+(?:in order to|so as to|so that|to)\s+\w+.*$`) reads any " to <word>" as a purpose clause. A destination after a connector must be read from the RAW line, as SFR-D11's `province_named_after_relative` does — not from the cleaned target.
- **`tests/data/parser_golden_corpus.json` is CRLF.** Edit it through a load/save that keeps the line endings.
- **The wire-test fixture that works:** delenv SOVEREIGN_SCENARIO/MAP/SMOKE_START, `LLM_MODE=mock`, `M._reset_world_state()`, then `monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))`. Copy `shipped` from `tests/test_sf_rr1_the_orders_the_reading_met.py`.

**Traps learned in the economy audit:**
- **The Charges of Empire are a share of the chest above its floor.** A purse test on the forecast Net refuses a rich court for being rich (EA-18); read the Net before the Charges where sustainability is the question.
- **The dispatch records no league table while the old league stands** (`_coalition_section` skips it while `_formed`), but the page's beat reads the same forecast every morning — a reader keyed on the rows lags the news by a page (EA-16).
- **A truce writes the armistice cooldown that refuses a declaration** — fixed in the economy gate: `diplomacy.declaration_cooldown_left` is the one reading the declaration, the cascade, the war council and the coalition gate share (EA-19).
- **Britain boots AT its paymaster floor (2,000):** stage its chest before asking who pays.
- **A lever read at a call site is invisible to a pin that calls the rung directly** — pin it through the chain, both arms (the sweep found exactly that).
- **Patch scripts and line endings:** keep CRLF with `newline=bytes([13, 10]).decode()`; a heredoc ate a `\r\n` literal this session.
- **The mutation sweep's apply now retries a transient lock** like its restore (`tools/mutation_sweep.py`); it had died at row 19 of 30 on `coalition.py`.
