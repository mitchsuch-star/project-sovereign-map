# NEXT SESSION PROMPT — the Score Finish residue, its second session: SF-RR3 "the page and the copy"

> Overwritten each time a session hands off. Current hand-over: **October 21, 2026, after SF-RR2 "the desk answers
> what was asked" landed and SF-RR1 part (ii) was closed by its re-read** (commits through the hook — `git log -2`).
>
> **What the session delivered** (`SYSTEMS_REFERENCE.md` §137; rows `BUG_FIXES.md` §Score Finish Step 8 SFR-H4,
> H8 … H12, H14, D2, D16, D19, D26 FIXED and §RR2 RR2-X1 … X12 FIXED; pins `tests/test_sf_rr2_the_desk_answers.py`):
> - **SF-RR1 (ii) closed by its re-read:** every row it owned was already FIXED (DD-0 S4); the HOLD arm on the entry
>   tree read command C3 18 of 20 (line 15), no misread; 19 of 20 on the slice's tree. Archive
>   `docs/audits/score_runs/2026_10_21_rr2/`.
> - **SF-RR2:** the HOLD's twenty questions shrug 0 times (2 at entry) with no wrong answer by hand — the march reads
>   its destination, the what-if its verb, who can strike Mack is ranked by the attack's reach and the march's clock,
>   the coalition by its name, the 44% by what it counts, "why did that fail" by the last reply's own words, the AP
>   counted, the nine plain questions answered, and Talleyrand's questions the desk owns (his mission, a peace's
>   chances, vassals, the auction, a court's design …) answered from the desk instead of his generic brief.
> - **The census:** the October 3 blind file's 150 questions now 150 answered (114 shrugs at its record); its sweep
>   found RR2-X12, a P2 misread ("Davout strikes Mack, cavalry to follow." marched him to support Bernadotte) — FIXED.
>
> **Traps this session paid for:**
> - `world.last_morning_dispatch` nests its figures (`strength_ratio_pct` is not top-level) — search it, or call the
>   dispatch's own helper.
> - **No new module lever** — `LEVERS_CAP` (231) and `FUNCTIONS_OVER_500_CAP` (28) are ratchets: each row is ONE function
>   seam a pin patches down (SF-RR2's `state_desk._THE_ROWS_THE_READING_FILED`), and additions to a function near 500
>   lines go in helpers (`classify_state_question` stands at ~495).
> - The census's order halves drift with every board change since their record — read each moved row against its
>   message before calling it a regression; `tools/unrehearsed_census.py` runs six files in ~30 s each, keyless.
> - `CLAUDE.md` stands at 61,938 bytes (cap 62,000): swap its live-state rows, shorten as you swap.
> - Run the suite with `PYTHONDONTWRITEBYTECODE` unset (`env -u PYTHONDONTWRITEBYTECODE …`): two `fa_slice8` bytecode
>   pins fail under it, the hook unsets it.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

The Score Finish residue, its second session — SF-RR3 "the page and the copy" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/SCORE_FINISH_SPEC.md` §3 Step 9 (the SF-RR3 row — its rows, done-when and test), `docs/BUG_FIXES.md` §Score Finish Step 8 (the SFR-D / SFR-B rows; `tools/defect_census.py --open` lists the open ones), `docs/audits/SCORE_FINAL_2026_10_05.md` and `docs/audits/SFR_DEPTH_CAMPAIGN_2026_10_05.md` (the playtester's report the D rows quote), and `docs/PLAYTESTING.md` (Mode A; the CMD arms are `tools/score_run.py`'s).

Scope — the design is the spec's; rule the details at the head, measured, and flag any reversal:
0. **The user's rule (October 20, 2026): diplomacy is never typed.** No new line teaches a typed diplomatic order; every diplomatic act it names is a Cabinet row or a row's `choices`.
1. **SF-RR3 "the page and the copy":** SFR-D14, D15, D17, D21, D27, D30, D32, D33, D36, D43, D44; SFR-B4, B6, B7, B8, B9, B12, B13, B15; the economy audit's EA-E4. Most D rows are "unverified beyond the playtester's quoted digest lines" — **reproduce each first** on a board (the depth archive `docs/audits/score_runs/2026_10_05_sfr/depth/` holds the chunk digests and scripts; a fixture save or `--save-at N` stages the turn); a row that does not reproduce on today's tree is closed by its reproduction attempt, named, not by assumption. Each fix pinned in `tests/test_sf_rr3_the_page_and_the_copy.py`, its seam held down reproducing the row.
2. **Done when** every row's pin flips with its seam and narration C6's sampled dispatches lead with their turn's biggest event on the CMD arms (the panel's re-read — read the sample by hand and record it in the spec's row).
3. **If the session has room:** SF-RR4 "war, truce and the standing order" (EG-D3's bench is its long pole) — sized at RR3's close; otherwise it heads the next session, named in STATUS with its pin.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this session or heading the next); a change that reaches the AI runs the attribution arms (`tools/_pc_s14p3_series_arms.py`'s idiom: one seam per change) with `BASELINE_SERIES` byte-identical or every movement attributed and named; a new parser route adds its golden-corpus row and regenerates the routed words if a verb moves (`python -m tools.gen_routed_order_words`); the Godot parse harness if a `.gd` changes. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when SF-RR3's rows are FIXED (or closed by their reproduction) with their pins, STATUS ▶ NEXT UP names what follows (SF-RR4 … RR6, then S14b), and this file is overwritten for it.
