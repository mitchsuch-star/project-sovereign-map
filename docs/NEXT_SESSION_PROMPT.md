# NEXT SESSION PROMPT — Pre-Deploy S13b part 2: DD-B fixes — the two found rows at its head, the table's P3s and the field

> Overwritten each time a session hands off. Current hand-off: **October 14,
> 2026, after S13b part 1 landed.**
>
> **What part 1 delivered** (three commits on master, run straight through):
> - `08c54539` the three P1s: the objection arrives with the proposal (DDB-1); France is asked to join an
>   ally's offensive war by a letter (DDB-2, DDB-D8 built); a truce keeps a contingent at its post (DDB-3,
>   DDB-D9 built).
> - `6f360d03` the table's P2s DDB-4 … DDB-12 and DW-2 (DDB-X5): Counter's dry run, what the treaty titles,
>   France's gold as a concession, the counsel first, the paradox before the click, the Cabinet's controls
>   named, the chip's own estimate, the homeland clause, one war-score credit (×0.65).
> - the close: rows, docs, this prompt.
> - Rules `SYSTEMS_REFERENCE.md` §116; pins `tests/test_ddb_s13b_the_p1s.py` (24),
>   `tests/test_ddb_s13b_the_table.py` (26), `tests/test_ddb_s13b_the_rulings.py` (8).
> - The series: `tools/_ddb_s13b_series_arms.py`, eight arms, every one byte-identical to `BASELINE_SERIES`
>   (reach 0 on the 1805 board — the passive France is never called, never truced, never at the table).
>
> **The sibling sweep found five rows.** DDB-X7, X8 and X10 are FIXED. **DDB-X9 and DDB-X11 head this part**
> (`BUG_FIXES.md` §DD-B, the second table).
>
> **Nothing waits on the user** (a code-signing certificate is theirs before S15, not before this part).
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S13b part 2 — DD-B fixes: DDB-X9 and DDB-X11 at the head, then the table's P3s (DDB-22 … 35) and the field (DDB-13 … 20, 36 … 44).**

Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S13b (four parts):
- **part 1** — LANDED October 14, 2026;
- **part 2** — this prompt;
- **part 3** — the rulings and their siblings (DDB-R1 … R7, X1 … X3);
- **part 4** — the voice, the client and the sea (DDB-21, 45 … 62) and the naval rail alerts (DDB-X6).

After S13b: S14 (SF-RR7 + the Score Finish residue), S14b VP-1, S14c the events, S14d the table lesson, S14e DD-B's re-measure (S14f its rows), S15 UXR-4 + code signing + the deploy.

Each row in `docs/BUG_FIXES.md` §DD-B carries its cause (file:line) and its **decided fix**: that is the spec, so implement it as written. Line numbers were read on `0e2002e8`; part 1 moved `diplomacy.py`, `diplomatic_executor.py`, `settlement_staging.py`, `settlement_actions.py`, `game_end.py` and `main.gd`, so navigate by the symbol.

**How to work:**
- Work directly on master per `CLAUDE.md`. Commit and push each slice.
- Run `git fetch origin` first and read `git log -8 --stat` before touching anything.
- **Every decision is already made.** The user's rulings ("make all decisions … nothing hanging", October 13; "make design calls …", October 14) make this prompt the approved plan.
  - Do not stop for Plan Mode approval, and do not pause between slices.
  - The rules below settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

**The sibling sweep (the user's ruling, October 14 — it holds for every row):**
- Every fix ends with a search for its class: the same mechanism on the other courts, dialogues, popups and roads, and the AI's side of the same executor.
- Each sibling found is filed in §DD-B's second table as `DDB-X<n>` (the next is **DDB-X12**), with its tag `⟨SF step=pre-deploy S13 · DD-B · pillar=…⟩`.
- It is fixed in the same slice with its own test (`tests/test_ddb_s13b_the_rulings.py::TestDDBX<n>`).
- A sibling too large for the slice heads part 3. Nothing found is homed after the deploy.
- Each commit message names its sweep: what was searched, and what was found.

**Read first:**
- `BUG_FIXES.md` §DD-B: its preamble, DDB-X9 and DDB-X11 (the second table), and the rows DDB-13 … 20, 22 … 44;
- `SYSTEMS_REFERENCE.md` §116 (part 1's rules: the objection's road, the call to arms, the truce, the table, the homeland clause);
- `docs/audits/DD_B_FRESH_EYES_2026_10_14.md` §4 and the cited frames (`docs/audits/dd_b/<road>/frames/NNNN.jpg`), with the players' words (`rows.json`, `summaries.md`);
- `CLAUDE.md` "Before Modifying": combat execution, multi-marshal coordination, objections, diplomacy, settlement, the economy, the popup recipe.

**Tests** — one module per slice, as each row's completion names it:
- the found rows: `tests/test_ddb_s13b_the_rulings.py` (add `TestDDBX9`, `TestDDBX11`);
- the table's P3s: `tests/test_ddb_s13b_the_table.py` (add `TestDDB22` … `TestDDB35`);
- the field: `tests/test_ddb_s13b_the_field.py` (new; `TestDDB13` … `TestDDB20`, `TestDDB36` … `TestDDB44`).

Each row gets one class, `TestDDB<n>`. Drive the real endpoints (the in-process TestClient on the 1805 boot or the board the row was seen on), never a mocked executor. When a row lands, mark it FIXED in its Status cell with the commit and the test, keep its tag, and say that the sighting's re-play is S14e's.

### Slice 1 — the head: DDB-X9 and DDB-X11 (one commit)

**DDB-X9 — the letter's status quo is the ratifier's.**
- `settlement_offers._derive_status_quo_lines` gives way to the ratifier's own `status_quo_forecast_lines`, per cross-side pair, exactly as part 1's review reads them (`settlement_staging.settlement_status_quo_review`), less the provinces the package moves (`_provinces_the_terms_move`).
- The letter and the review then say the same thing on one board: a conquest titled outside a homeland is listed; an ally's retaken homeland reads "returns to us / <court> by the treaty".
- `main.py`'s re-show of a cached offer (the comment near `_derive_status_quo_lines`, ~`:6825`) re-reads it the same way.
- **Test:** the sea #18 board (Franche-Comte retaken by Bavaria, Vienna held by France) — a court's settlement offer and the review list the same lines.

**DDB-X11 — one demand-side reading at ×0.65.**
- Scale `WAR_AGE_PENALTY_MAX` (`diplomacy.py`) by the credit ratio: 30 × 0.65 / 0.3 ≈ **65**. Re-read CA9 row 1's arm A at the shipped weight: a two-turn war at +30 yields no recommended extraction.
- Re-read the AI letter's thresholds at the shipped weight, so a beaten court's honest truce or peace letter clears the send filter (< 20). The bilateral's war-age and harshness terms sit beside the table's — one demand-side reading, as DDB-X5 gave one credit.
- **Lift every isolation:** the fifteen pins that patch `bilateral_war_score_weight` to 0.3 (five in `test_da1_ai_intelligence` via `_p1_board_at_the_old_weight`, three in `test_nation_agendas`, two in `test_session4_diplomacy`, three in `test_settlement_gate4_leg1_fixes`, one in `test_sf_nav1_d1_the_tilsit_clause`, CA9 arm A) read at the shipped weight, each retuned with "DDB-X11" named if its number moves.
- Re-measure `BASELINE_SERIES` with an attribution arm (add the seam to `tools/_ddb_s13b_series_arms.py`); re-pin with "DDB-X11" as the reason if it moves. M1–M7 must hold.
- **Test:** `TestDDBX11` — CA9 arm A at ×0.65 recommends nothing at two turns; a beaten court's P1 letter on the da1 board is sent at ×0.65.

### Slice 2 — the table's P3s: DDB-22 … DDB-35 (one commit; each row's decided fix as written)

These forks are already decided:
- **DDB-23:** a stream's line says "for as long as the treaty stands" (or its turns).
- **DDB-24:** the war's sides are labelled by court ("France" / "The Third Coalition"), never attacker / defender.
- **DDB-30:** "Less generous" restores exactly the previous round's terms, and is absent on round 1.
- **DDB-33:** Ease stops raising gold at the scorer's gold ceiling and says so; the promised-region check reads `create_client` provinces.
- **DDB-34:** the auction's dispatch line names "F1 → <court> → Bid for Their Allegiance", and the advice menu offers the bid while an auction is open.
- **DDB-35:** Propose Peace stands in the WAR state, with the ARMISTICE state's ally-at-war hard stop (part 1's `commitment_paradox` / `separate_peace_paradox` is that stop; reuse it).
- The rest (DDB-22, 25 … 29, 31, 32): each row's decided fix as written.

### Slice 3 — the field: DDB-13 … DDB-20 and DDB-36 … DDB-44 (one commit, or two if a hook run is long)

Each row's decided fix as written. Where a fix touches combat or the muster, Golden Rule 1 holds (modifiers live in `marshal.py` only) and the AI's side of the same executor is part of the sweep. A fix that moves a byte-pinned series re-pins it in the same slice with the row named and its attribution arm recorded.

### The close

**Rows:**
- DDB-X9, DDB-X11, DDB-13 … 20 and DDB-22 … 44 FIXED in `BUG_FIXES.md` §DD-B (commits and tests).
- Any found rows FIXED, or heading part 3.

**Docs:**
- `PRE_DEPLOY_PLAN.md` §2: S13b part 2 noted landed.
- `STATUS.md` ▶ NEXT UP: a new block (seven kept; the oldest to the top of `docs/archive/STATUS_2026_Q4.md`).
- `CLAUDE.md` LIVE STATE: the cap is ≤ 62,000 B, so trim the oldest line as you add one.
- `SYSTEMS_REFERENCE.md` §117: the new rules.
- This file, rewritten for **S13b part 3**: the rulings' builds DDB-R1 … R7 and their siblings X1 … X3, each ruling's build as `DESIGN_REFINEMENT.md` §DD-B and `docs/audits/DD_B_RULINGS_2026_10_14.md` §2 state it, with any found row of part 2 at its head.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Check `tasklist | grep -ci godot` before any engine start. The hook drives Godot (the engine group), so start no engine during a commit.
- **Never touch the user's live 8005 backend.** A driven check runs on `SOVEREIGN_PORT=8006` or above with `INK_IRON_SAVE_DIR` set; `uxr3_action_probe.start_backend` does both.
- **The hook tests the working tree, not the index.**
  - Park a later slice's test edits outside `tests/` before committing an earlier slice. An untracked test in `tests/` runs in the hook.
  - Do not edit files the tests read while a commit's hook runs — the docs included (the census and the plan pins read `BUG_FIXES.md`).
- **`PYTHONDONTWRITEBYTECODE=1`** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING`.
- **The hook** runs ruff and the full parallel suite (about 6–12 minutes under load; 31,041 tests at part 1's end).
  - Commit with `run_in_background: true` from Bash, with a message file, and never `--no-verify`.
  - Read the log's `[pre-commit]` and `EXIT=` lines before believing a commit.
  - The G4 timing pin can fail under load. Re-run it alone; if it passes, re-commit unchanged.
- **A byte-pinned series.** If a decided fix moves one (`BASELINE_SERIES`, the M-pins, a seeded digest), re-pin it in the same slice, naming the row as the reason, with its attribution arm recorded. A move no row explains is a bug in the slice. **No new module lever:** the code-health ratchet (`LEVERS_CAP`) forbids one, so an attribution arm patches a function seam in the child (part 1's `tools/_ddb_s13b_series_arms.py` idiom; a down value that needs the original reads `_orig`).
- **A function at 500 lines.** `turn_manager.end_turn` sits at exactly 500 (`FUNCTIONS_OVER_500_CAP`); a line added there goes in a helper.
- **The judge is shared.** `tools/_score_probes.py` is read by the census records and the score archive. Check any edit against every committed census record (`docs/audits/unrehearsed/`) and the HOLD arms first. A help line the census executes must not quote an order that refuses on the boot (part 1's bid is taught in single quotes for that reason).
- **The answer-binding shuffle** (`tools/answer_binding_shuffle.py`) counts a refusal that leaves the letter standing as a misbind unless its judge knows the reply; part 1 taught it "the offer stands". Teach it any new standing refusal.
- **The census reads closing words.** In a Status cell, an uppercase FIXED / RULED / BUILT / RE-HOMED closes a row. Write them only when the row is truly closed, and keep them lowercase in an OPEN row's prose.
- **Dialogue and popup wiring** (`CLAUDE.md` "Adding a new popup/dialog"):
  - every POST handler goes through `build_base_response`;
  - a new dtype goes on the `main.gd` whitelist;
  - a popup that must arrive with its dialogue carries the dialogue's id (DDB-1's whole defect).
- **Monkeypatch the type, never a method on `M.executor` / `M.parser`.** In a TestClient world swap, swap `M.world`, `M.game_state` and `M.parser` together.
- **Shell:**
  - Bash heredocs mangle backslashes and quotes, and a Python script piped on stdin is decoded as cp1252. Write scripts with the Write tool and run them with `-X utf8`.
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

**Open with the user:** UXR-4 at S15 (S12's eleven R2 marks, and S12b's and DD-B's frames), and a code-signing certificate before S15. Nothing in part 2 waits on either.

**Do not:**
- edit `docs/UX_CHECKLIST_V1.json`;
- re-score, add a lever, or weaken a gate or a ratchet;
- change a rule no row or ruling names;
- touch the Score Finish residue or start S14.
