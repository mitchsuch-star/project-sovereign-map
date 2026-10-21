# NEXT SESSION PROMPT — the Score Finish residue, its fifth session: SF-RR6 "the instrument reads what the player sees"

> Overwritten each time a session hands off. Current hand-over: **October 21, 2026, after SF-RR5 "the frames at both
> scales" landed** (commits through the hook — `git log -2`).
>
> **What the session delivered** (`SYSTEMS_REFERENCE.md` §140; rows `BUG_FIXES.md` §Score Finish Step 8 SFR-B11 FIXED
> and SFR-B10 CLOSED by its reproduction, §The Economy Audit EA-E1, E2, E5, E6, E9 FIXED and EA-E3, E7 CLOSED by their
> reproduction, §RR5 RR5-X1 … X9 FIXED; pins `tests/test_sf_rr5_the_frames.py`; frames `docs/audits/IQ10_*_2026_10_21.png`,
> listed at `UX_UI_REVIEW_PLAN.md` §UXR-4):
> - **Reproduced first** on the whole IQ-10 table at both Interface Scales; S12 part 2 had already fixed three rows.
> - **The 2.0 decision modals:** every answer of every modal in the table stands above the fold at both scales, inside
>   the window — the petition's answers in a row under its letter, the Proclamation's closing line under its body, the
>   objection's rows wrapping, the settlement table's court rows kept, the reward dialog's choices kept; a tall panel
>   stands under the bar at a short window (`Utils.clamp_centered_panel`), a block of answers keeps its rows
>   (`relax_floor`).
> - **The top bar, the glyphs, the snap, the key:** the compact bar draws its glyphs (the full bar keeps its words —
>   ruled); 62 curated glyphs whitened (`tools/ui_icons_white.py`); the whole-line snap cuts a tall box rather than hide
>   it behind a dead band; Alt+B opens the Dispatch where an overlay keeps Alt+R (the Mode C session pressed it).
>
> **Traps this session paid for:**
> - **The IQ-10 harness runs HEADLESS in record-only mode** (`record_only: true` in the spec): the layout record is the
>   windowed one's (measured), with no picture — pins and before/after comparisons use it; pictures still need
>   `--windowed`.
> - **A relative `--png-dir` lands under the Godot project** (`godot-client/project-sovereign/docs/audits/`) — pass an
>   absolute path.
> - **Capture roads drift silently** when the backend adds a step: the Talleyrand objection (S14 part 2's articles card)
>   and the collapse war detail (S13d's tier) had shot blank or not at all for days. Both captures now raise; read a
>   manifest's empty facts after any backend change to a staged road.
> - **After changing an SVG, run `--headless --import`** or the harness draws the stale imported texture.
> - **The heredoc backslash trap again:** a `\\n` inside a quoted heredoc became a real newline in a test file — write
>   scripts with the Write tool.
> - Harness logs carry "Lambda capture at index 0 was freed" engine ERRORs on every run (teardown noise, 32 on the entry
>   tree) — not SCRIPT ERRORs.
> - `CLAUDE.md` sits at 61,900 of 62,000 bytes.
>
> **Nothing waits on the user before S15** (UXR-4 — now with SF-RR5's frames and two rulings — the code-signing
> certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

The Score Finish residue, its fifth session — SF-RR6 "the instrument reads what the player sees" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/SCORE_FINISH_SPEC.md` §3 Step 9 (the SF-RR6 row — its rows, done-when and test), §4 (the instrument and its frozen-reader rule) and §6 row 23, `docs/BUG_FIXES.md` §Score Finish Step 8 (SFR-I2, I4, I5, I6, I7), §The Economy Audit (EA-2) and §The Economy Gate (EG-X4) — `tools/defect_census.py --open` lists them — `docs/DESIGN_REFINEMENT.md` EG-D1 (ruled: re-band), and the instrument (`tools/score_run.py`, `tools/score_reread.py`, `tools/_score_probes.py`, `tools/playtest_driver.py`, `docs/SCORE_CHECKLIST_V1_1.json`).

Scope — the design is the spec's; rule the details at the head, measured, and flag any reversal:
0. **The user's rule (October 20, 2026): diplomacy is never typed.** No new line teaches a typed diplomatic order.
1. **SF-RR6 "the instrument reads what the player sees":** SFR-I2 with SFR-I7 (the digest marks or drops the enemy-phase text the client never renders — `enemy_phase_dialog.gd` rebuilds every line from structured fields — and combat legibility C5 reads rendered text), SFR-I4 (drama C5 reads both copies of an unmet claim; the driver records the dispatch's Unmet Marshals block and its `expectation_rises`), SFR-I5 (AI aliveness C6 counts France's wars — a war France joins through its client too — never another court's declaration), SFR-I6 (the DL arm stages its preconditions — actions spent on the right turn, the levy on French ground — and the driver flags SCRIPT PRECONDITION when one fails), EA-2 (economy F1 sees an off-books flow: the chest's measured change across the end turn, less the Butcher's Bill and the one-shot purchases, against the applied Net), EG-X4 (trace which store is stale on the gate's CMD-M turn-20 board — the dispatch's intel row or the store's last sighting — and fix the stale one at its seam; narration C4 ✓ with the cause recorded), and EG-D1's re-band (a new `docs/SCORE_CHECKLIST_V1_2.json` whose AI aliveness C1 reads "the rival courts enact at least 13 of their decks' 20 laws, with 0 lapses"; the AI's purse untouched). **Reproduce each first** (every reader misread shown on the archived digest that carries it); fix each at its one seam in the instrument.
2. **The frozen reading stands as measured** (§4): the corrected readers never rewrite a past mark — both archives (the baseline's and the final reading's, and the latest CMD arms) are re-read by `tools/score_reread.py` beside their records and the deltas published, the frozen marks kept.
3. **Done when** every row's pin in `tests/test_sf_rr6_the_instrument.py` flips with its lever, the re-reads and their deltas are published (the memo beside the archives), `docs/SCORE_CHECKLIST_V1_2.json` carries the re-band and both archives read it the same way, and STATUS ▶ NEXT UP names S14b.

Rules: reproduce each gap on its archived digest before building; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this session or heading the next); a change that reaches the AI or the backend runs the attribution arms (`tools/_sf_rr4_series_arms.py`'s idiom) with `BASELINE_SERIES` byte-identical or every movement attributed; the Godot parse harness for every `.gd` changed; edit CRLF files with a script that preserves line endings (`objection_dialog.gd`, `popup_base.gd`, `proposal_confirm_popup.gd/.tscn`, two map scripts and `deploy/README_TESTER.txt` are CRLF). Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when SF-RR6's rows are FIXED (or closed by their reproduction) with their pins and re-reads, STATUS ▶ NEXT UP names what follows (S14b, VP-1), and this file is overwritten for it.
