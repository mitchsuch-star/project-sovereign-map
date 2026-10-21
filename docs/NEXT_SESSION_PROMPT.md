# NEXT SESSION PROMPT — the Score Finish residue, its fourth session: SF-RR5 "the frames at both scales"

> Overwritten each time a session hands off. Current hand-over: **October 21, 2026, after SF-RR4 "war, truce and
> the standing order" landed** (commits through the hook — `git log -2`).
>
> **What the session delivered** (`SYSTEMS_REFERENCE.md` §139; rows `BUG_FIXES.md` §Score Finish Step 8 SFR-D3, D4,
> D5, D6, D22, D29, D31, D35, B14 FIXED and SFR-D18 CLOSED by its reproduction, §The Economy Gate EG-X5 FIXED, §RR4
> RR4-X1 … X12 FIXED, `DESIGN_REFINEMENT.md` EG-D3 BUILT; pins `tests/test_sf_rr4_war_truce_and_the_standing_order.py`, 53):
> - **Reproduced first:** four read-only investigators (Sonnet), one per family; their boards became the pins. SFR-D18
>   (DDB-19 had fixed it) and the organic SFR-B14 (0 lapses on every CMD arm) did not reproduce as written.
> - **The fixes:** the Trust arm names its price; the contact interrupt reads the muster's figure; the quotes name the
>   man the cover rule puts in the field; trusting Ney issues his chase; a HOLD keeps its post; only a court at war
>   harasses; the AI no longer hops back; the AI repeals before a lapse; the road home names the enclave and the desk
>   answers it; a field win names the works it took.
> - **The bench:** Spain's La Romana, Blake, Cuesta; Sweden's Toll, Adlercreutz; Bavaria's Wrede — each court commissions
>   from it at war on the CMD arms; `BASELINE_SERIES` re-recorded once (`tools/_sf_rr4_series_arms_final.json`), the old
>   series kept as `SERIES_BEFORE_THE_BENCH`.
> - **The reading (CMD arms):** combat legibility C3 ✗ → ✓; AI aliveness C1 0 lapses (its 13–18 band ✗ at 19–20 on both
>   trees — EG-D1's re-band, SF-RR6's), C6 ✓; living balance F1 ✓.
>
> **Traps this session paid for:**
> - **An attribution tool must prove its levers bite.** `tools/_sf_rr4_series_arms.py` first checked each seam in the
>   PARENT (`importlib` from `tools/` cannot see `backend`), silently dropped all seven code levers, and arm 0 still
>   vetoed three backtracks. Read arm 0's reach counters as well as its series.
> - **A data change can be held down through a function seam:** the front page's `SEAMS_DOWN` holds the bench down with
>   `recruitment:get_marshal_pool=…` (the driver's `--seam` takes callables only).
> - **A pin that relied on a defect re-stages honestly:** the ACH-F / action-cost / CA9 pins needed the pursuit's
>   objection, which RR4-X1 made read the muster — their boards now stage a Mack the muster cannot carry (400,000).
> - `_build_muster_preview` sits at 494 lines (the ratchet caps functions over 500 at 28); `CLAUDE.md` at 61,893 of 62,000.
> - Run pytest with `env -u PYTHONDONTWRITEBYTECODE` or two `test_fa_slice8` bytecode pins fail spuriously.
> - `score_run.py check` prints ✓/✗ as "?" on this console; read `checklist.json` in the run dir.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

The Score Finish residue, its fourth session — SF-RR5 "the frames at both scales" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/SCORE_FINISH_SPEC.md` §3 Step 9 (the SF-RR5 row — its rows, done-when and test), `docs/BUG_FIXES.md` §Score Finish Step 8 (SFR-B10, B11) and §The Economy Audit (EA-E1, E2, E3, E5, E6, E7, E9; `tools/defect_census.py --open` lists them), `docs/UX_UI_REVIEW_PLAN.md` (the frames and UXR-4), and the IQ-10 capture tools (`tools/iq10_capture_payloads.py`, `tools/iq10_run_captures.py`; the memory note on the Godot harness: screenshots need `--windowed`, never `--headless`).

Scope — the design is the spec's; rule the details at the head, measured, and flag any reversal:
0. **The user's rule (October 20, 2026): diplomacy is never typed.** No new line teaches a typed diplomatic order.
1. **SF-RR5 "the frames at both scales":** SFR-B10 (the diorama's standard over a portrait, the Close button over the frame — IQ10_DIORAMA_DADJ at both scales), SFR-B11 (the Proclamation and the petition push their choices below a scroll fold at Interface Scale 2.0), the agendas C6 re-shoot, and the economy audit's client rows EA-E1 (the compact top bar's blank navigation buttons — supersedes SFR-I3), EA-E2 (gear / book icons draw black), EA-E3 (the Admiralty chip's blockade border), EA-E5 (the wizard's step-2 assessment shrinks at 2.0), EA-E6 (SETTLEMENT_THREE_COURTS_X2's must_show), EA-E7 (the Generals screen's filigree over scrolled text), EA-E9 (an advertised hotkey eaten by a common overlay). **Reproduce each on its frame first** (shoot the entry tree; a row whose frame is clean today is closed by its reproduction, named); fix each at its one seam in the client (the `.gd` and its layout law, UXR-2); re-shoot at both scales.
2. **Done when** the diorama and the 2.0 decision modals re-shot clean, every row's pin in `tests/test_sf_rr5_the_frames.py` flips with its fix (a layout census or the IQ-10 frame's `must_show`), the re-shot frames are listed in `docs/UX_UI_REVIEW_PLAN.md` §UXR-4 for the user's eye, the Godot parse harness EXIT 0.
3. **If the session has room:** SF-RR6 "the instrument reads what the player sees" (SFR-I2 … I7, EA-2, EG-X4, EG-D1's re-band of AI aliveness C1 in `docs/SCORE_CHECKLIST_V1_2.json`) — sized at RR5's close; otherwise it heads the next session, named in STATUS with its pin.

Rules: reproduce each gap on its frame before building; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this session or heading the next); a change that reaches the AI runs the attribution arms (`tools/_sf_rr4_series_arms.py`'s idiom) with `BASELINE_SERIES` byte-identical or every movement attributed; the Godot parse harness for every `.gd` changed; edit CRLF `.gd` files with a script that preserves line endings. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when SF-RR5's rows are FIXED (or closed by their reproduction) with their pins and frames, STATUS ▶ NEXT UP names what follows (SF-RR6, then S14b), and this file is overwritten for it.
