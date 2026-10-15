# NEXT SESSION PROMPT — Pre-Deploy S13b part 3: DD-B fixes — DDB-X17 at its head, then the rulings' builds and their siblings

> Overwritten each time a session hands off. Current hand-off: **October 15,
> 2026, after S13b part 2 landed.**
>
> **What part 2 delivered** (three commits on master, run straight through):
> - `8f3f1141` the head: a court's offer letter lists the status quo by the ratifier's own rule (DDB-X9);
>   one demand-side reading at ×0.65 — `WAR_AGE_PENALTY_MAX` 65 and the AI's send floor re-read
>   (DDB-X11); a court's bilateral peace letter names the status quo (DDB-X12).
> - `33643c45` the table's P3s DDB-22 … 35 (labels, stream terms, sides by court, the assessment, the
>   counter-aware band, the petition at the table, Less generous / Milder terms, the auction's control,
>   Propose Peace in the WAR state) and the found rows DDB-X13 … X16.
> - `cd8f3210` the field DDB-13 … 20 and 36 … 44 (the treasury's net and the bill; the player's lead
>   refused peace soil and the joiners said; the walk-in; the cornered marshal's fate; the outcome's
>   register; the hopeless counsel; one reading of an attack; SUPPORT at the approach; the posture
>   header; the advance; the routed's counter-punch; morale; fortify's price; Cancel; Europe's alarm on
>   the province; provinces changing hands; the supply warning) and the found rows DDB-X18 … X22.
> - the close: rows, docs, this prompt.
> - Rules `SYSTEMS_REFERENCE.md` §117; pins `tests/test_ddb_s13b_the_rulings.py` (30),
>   `tests/test_ddb_s13b_the_table.py` (49), `tests/test_ddb_s13b_the_field.py` (48).
> - The series: `tools/_ddb_s13b_series_arms.py`, eighteen arms, every one byte-identical to
>   `BASELINE_SERIES` (`tools/_ddb_s13b_series_arms_final.json`).
>
> **The sibling sweep found eleven rows** (DDB-X12 … X22). Ten are FIXED. **DDB-X17 heads this part**
> (`BUG_FIXES.md` §DD-B, the second table).
>
> **Nothing waits on the user** (a code-signing certificate and the UXR-4 review are theirs before S15,
> not before this part). Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S13b part 3 — DD-B fixes: DDB-X17 at the head, then the rulings' builds DDB-R1 … R7 and their siblings DDB-X1 … X3.**

Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S13b (four parts):
- **parts 1 and 2** — LANDED October 14 and 15, 2026;
- **part 3** — this prompt;
- **part 4** — the voice, the client and the sea (DDB-21, 45 … 62) and the naval rail alerts (DDB-X6).

After S13b: S14 (SF-RR7 + the Score Finish residue), S14b VP-1, S14c the events, S14d the table lesson, S14e DD-B's re-measure (S14f its rows), S15 UXR-4 + code signing + the deploy.

Each row in `docs/BUG_FIXES.md` §DD-B carries its cause (file:line) and its **ruling** or **decided fix**: that is the spec, so implement it as written. The rulings' full text is `DESIGN_REFINEMENT.md` §DD-B (DDB-D1 … D7) and `docs/audits/DD_B_RULINGS_2026_10_14.md` §2. Line numbers were read on `0e2002e8`; parts 1 and 2 moved `combat_executor.py`, `executor.py`, `strategic.py`, `strategic_executor.py`, `objection_v2.py`, `world_state.py`, `movement_executor.py` and `main.gd`, so navigate by the symbol.

**How to work:**
- Work directly on master per `CLAUDE.md`. Commit and push each slice.
- Run `git fetch origin` first and read `git log -8 --stat` before touching anything.
- **Every decision is already made.** The user's rulings ("make all decisions … nothing hanging", October 13; "make design calls …", October 14) make this prompt the approved plan.
  - Do not stop for Plan Mode approval, and do not pause between slices.
  - The rules below settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

**The sibling sweep (the user's ruling, October 14 — it holds for every row):**
- Every fix ends with a search for its class: the same mechanism on the other courts, dialogues, popups and roads, both combat copies (the executor's pipeline and the reckless auto-charge in `world_state._process_reckless_cavalry_turn_start`), and the AI's side of the same executor.
- Each sibling found is filed in §DD-B's second table as `DDB-X<n>` (the next is **DDB-X23**), with its tag `⟨SF step=pre-deploy S13 · DD-B · pillar=…⟩`.
- It is fixed in the same slice with its own test (`tests/test_ddb_s13b_the_rulings.py::TestDDBX<n>`).
- A sibling too large for the slice heads part 4. Nothing found is homed after the deploy.
- Each commit message names its sweep: what was searched, and what was found.

**Read first:**
- `BUG_FIXES.md` §DD-B: its preamble, the second table (DDB-R1 … R7, X1 … X3, X17);
- `DESIGN_REFINEMENT.md` §DD-B (the seven rulings) and `docs/audits/DD_B_RULINGS_2026_10_14.md`;
- `SYSTEMS_REFERENCE.md` §116 and §117 (parts 1 and 2's rules — §117.4 the peace-soil lead, §117.6 the one reading of an attack, §117.10 the alarm on the province);
- `CLAUDE.md` "Before Modifying": combat execution, multi-marshal coordination, objections, the garrison, the economy, the turn, the popup recipe.

**Tests** — all of this part's rows in `tests/test_ddb_s13b_the_rulings.py`: `TestDDBX17`, `TestDDBR1` … `TestDDBR7`, `TestDDBX1` … `TestDDBX3`. Drive the real endpoints (the in-process TestClient on the 1805 boot or the board the row was seen on), never a mocked executor. When a row lands, mark it FIXED (a ruling's build: BUILT) in its Status cell with the commit and the test, keep its tag, and say that the sighting's re-play is S14e's.

### Slice 1 — the head: DDB-X17 (one commit)

**DDB-X17 — no charge onto peace soil.** Part 2's DDB-14 refuses the player's attack LEAD a field on soil France is at peace with (`combat_executor.field_on_peace_soil`); the charge never read it.
- The player's glorious charge (`_execute_glorious_charge`) reads `field_on_peace_soil` before it rides: a charge onto peace soil is refused at no cost and names the court, in the attack's own words, and is pre-validated so no objection or confirm comes first.
- The player's reckless auto-charge (`world_state._process_reckless_cavalry_turn_start`) picks no target on peace soil (its "finds no enemies to charge" line names why when that is the only target).
- The AI keeps PT-F1 (GR5's named difference, `SYSTEMS_REFERENCE.md` §117.4).
- The eight WO-24 / WO-25 pins that move (`tests/test_wo_slice17_frontier_halts_the_charge.py` and its siblings — part 2 measured eight when it tried this at the charge's door) re-read the rule with "DDB-X17" named.
- Re-measure `BASELINE_SERIES` with an attribution arm (a seam in `tools/_ddb_s13b_series_arms.py`); re-pin with the row named if it moves.

### Slice 2 — the orders: DDB-R1, R2, R4, R5, R7 (one commit, or two if a hook run is long)

Each ruling's build as `DESIGN_REFINEMENT.md` DDB-D1 / D2 / D4 / D5 / D7 states it:
- **R1 — ask first.** An attack on a marshal out of reach asks, at no cost ("Kutuzov stands at Moravia, two marches off. Pursue him (2 AP — a standing order; the first march takes him to Dresden, Saxony's soil), or cancel?"); typed yes / pursue / no / cancel answer it. Typed player orders only.
- **R2 — the muster gate widened.** An unfavourable band pauses ANY personality's attack on Commit / Cancel (Cancel 0 AP), Berthier naming the band for a non-cautious lead; the sovereign never pauses; a favourable attack fires at once; a new player-only predicate at the gate site (`MUSTER_GATE_BAND` / `MUSTER_GATE_PERSONALITIES` untouched, so the AI and the series hold); a committed attack draws its objection once; every muster riding a result ends with the what-if line, and the help and the tutor's card name it. Part 2's DDB-19 made the objection read the muster's own totals, so the gate and the objection now read one band.
- **R4 — no auto-end on either pool.** Spending the last action leaves the turn with "the last order of the day"; the end-turn mirror (`executor.py`), WO-22's defer, the unread `should_end_turn` keys and the AUTO_END_WARNING copy are retired; old saves load (`auto_advanced_to_turn` stays readable). `turn_manager.end_turn` sits at 500 lines: nothing is added there.
- **R5 — refuse at no cost, naming both roads.** "recruit artillery for Augereau" spends nothing and names "'Augereau, recruit'" and the nearest gun marshal in reach or "commission Marmont (4,500g)"; PF-7's pin flips with the row named.
- **R7 — the rich peace's sink, surfaced.** At peace with a chest above the next unenacted law's price, "what can I do" and the morning dispatch's treasury line name that law and its price; nothing at war or when no law is affordable.

### Slice 3 — the garrison and the retreat: DDB-R3 with X1 and X2, DDB-R6 with X3 (one commit)

- **R3 — a detachment capitulates at 4:1.** At ≥ 4:1 effective odds an assault takes a detachment whole (its garrison event emitted); below 4:1 today's capped exchange; a capital's own garrison and a DEF-6 depot keep the 0.50 cap; one arithmetic for both boards (GR5). This is expected to move `BASELINE_SERIES` — re-pin it with "DDB-R3" named and its attribution arm recorded.
- **X1** — a naval landing on a detachment under 500 takes its surrender (`garrison_report`'s predicate). **X2** — the assault, scout and works-halt lines name the 500 floor, the 4:1 capitulation and a capital's 5,000 line.
- **R6 — keep the rule, fix the sentence.** An engaged marshal's `move` onto an ally's province refuses, reading `retreat_soil_is_friendly`, says "withdraw" and names "'Davout, retreat to Swabia' — free, −X% effectiveness, once a turn". **X3** — the AI's retreat finder's first tier reads `retreat_soil_is_friendly`; re-measure the series and re-pin with "DDB-X3" named if it moves.

### The close

**Rows:**
- DDB-X17 FIXED; DDB-R1 … R7 BUILT; DDB-X1 … X3 FIXED in `BUG_FIXES.md` §DD-B (commits and tests).
- Any found rows FIXED, or heading part 4.

**Docs:**
- `PRE_DEPLOY_PLAN.md` §2: S13b part 3 noted landed.
- `STATUS.md` ▶ NEXT UP: a new block (seven kept; the oldest to the top of `docs/archive/STATUS_2026_Q4.md`).
- `CLAUDE.md` LIVE STATE: the cap is ≤ 62,000 B, so trim the oldest line as you add one.
- `SYSTEMS_REFERENCE.md` §118: the new rules.
- `DESIGN_REFINEMENT.md` §DD-B: each ruling's landing record.
- This file, rewritten for **S13b part 4**: the voice, the client and the sea (DDB-21, 45 … 62) and DDB-X6, with any found row of part 3 at its head.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Check `tasklist | grep -ci godot` before any engine start. The hook drives Godot (the engine group), so start no engine during a commit. After any `.gd` edit, regenerate `tools/godot_parse_report.json` (the Start-Process harness; read `EXIT=0` and that every script and scene parses).
- **Never touch the user's live 8005 backend.** A driven check runs on `SOVEREIGN_PORT=8006` or above with `INK_IRON_SAVE_DIR` set.
- **The hook tests the working tree, not the index.**
  - Park a later slice's test edits outside `tests/` before committing an earlier slice. An untracked test in `tests/` runs in the hook.
  - Do not edit files the tests read while a commit's hook runs — the docs included (the census and the plan pins read `BUG_FIXES.md`).
- **`PYTHONDONTWRITEBYTECODE=1`** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING`.
- **The hook** runs ruff and the full parallel suite (about 7–15 minutes under load; 31,1xx tests at part 2's end).
  - Commit with `run_in_background: true` from Bash, with a message file, and never `--no-verify`.
  - Read the log's `[pre-commit]` and `EXIT=` lines before believing a commit.
  - The G4 timing pin can fail under load. Re-run it alone; if it passes, re-commit unchanged.
- **A byte-pinned series.** If a decided fix moves one (`BASELINE_SERIES`, the M-pins, a seeded digest), re-pin it in the same slice, naming the row as the reason, with its attribution arm recorded. A move no row explains is a bug in the slice. **No new module lever:** the code-health ratchet (`LEVERS_CAP`) forbids one, so an attribution arm patches a function seam in the child; run the arms with `--prior <the HEAD series>`.
- **Paid for in part 2:**
  - **A pipeline reads the province after the battle.** The post-combat pipeline runs after the capture, so "whose soil was this" must come from before the battle (`conquered`, or a value read first). Part 2's own-soil seam got this wrong before its re-run caught it.
  - **A refusal must be pre-validated.** A new refusal inside `_execute_attack` needs its predicate in `executor.py`'s objection battery too (the PF-4 idiom), or the objection fires first and Insist is paid for an attack that is then refused.
  - **One reading of an attack.** The objection reads the muster's expected totals (`muster_expected_totals`), so an objection board must be bad at the muster's weight (every corps in reach), not the lead's own.
  - **A decided fix can re-route a seeded campaign.** When a driven arm (the sf_page CMD-A arm, a commanded seed) changes its page, run the playtest driver on HEAD and on the working tree side by side (a temporary `git worktree` at HEAD in the scratchpad, removed after) and diff the digests for the first divergence; re-seat the pin with the row named only when the divergence is the row's own decided effect, and re-check it on the FINAL tree (part 2's first re-seat was wrong by the time the slice landed).
  - **A third party's soil is not the enemy's own.** `field_on_peace_soil` takes `enemy_nation`: an army on its own court's soil is a declaration of war, which the war-purpose road owns.
  - **Narrow a rule to what the ruling says.** "Adds no threat" gated war exhaustion and the coalition shock too until the gate was moved onto the threat rows alone.
- **The function at 500 lines.** `turn_manager.end_turn` sits at exactly 500 (`FUNCTIONS_OVER_500_CAP`); a line added there goes in a helper.
- **The judge is shared.** `tools/_score_probes.py` is read by the census records and the score archive. Check any edit against every committed census record (`docs/audits/unrehearsed/`) and the HOLD arms first.
- **The answer-binding shuffle** (`tools/answer_binding_shuffle.py`) counts a refusal that leaves the letter standing as a misbind unless its judge knows the reply. Teach it any new standing refusal.
- **The census reads closing words.** In a Status cell, an uppercase FIXED / RULED / BUILT / RE-HOMED closes a row. Write them only when the row is truly closed, and keep them lowercase in an OPEN row's prose.
- **Dialogue and popup wiring** (`CLAUDE.md` "Adding a new popup/dialog"):
  - every POST handler goes through `build_base_response`;
  - a new dtype goes on the `main.gd` whitelist;
  - a popup that must arrive with its dialogue carries the dialogue's id.
- **Monkeypatch the type, never a method on `M.executor` / `M.parser`.** In a TestClient world swap, swap `M.world`, `M.game_state` and `M.parser` together.
- **Shell:**
  - Bash heredocs mangle backslashes: a `\n` inside a Python heredoc becomes a real newline in the file it writes (part 2 broke an f-string that way). Write scripts with the Write tool and run them with `-X utf8`; fix a file with the Edit tool.
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

**Open with the user:** UXR-4 at S15 (S12's eleven R2 marks, and S12b's and DD-B's frames), and a code-signing certificate before S15. Nothing in part 3 waits on either.

**Do not:**
- edit `docs/UX_CHECKLIST_V1.json`;
- re-score, add a lever, or weaken a gate or a ratchet;
- change a rule no row or ruling names;
- touch the Score Finish residue or start S14.
