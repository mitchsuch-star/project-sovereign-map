# NEXT SESSION PROMPT — the Score Finish residue, its third session: SF-RR4 "war, truce and the standing order"

> Overwritten each time a session hands off. Current hand-over: **October 21, 2026, after SF-RR3 "the page and the
> copy" landed** (commits through the hook — `git log -2`).
>
> **What the session delivered** (`SYSTEMS_REFERENCE.md` §138; rows `BUG_FIXES.md` §Score Finish Step 8 SFR-D14, D15,
> D17, D21, D30, D32, D33, D36, D43, D44, B4, B6, B7, B8, B9, B12, B13, B15 FIXED and SFR-D27 CLOSED by its reproduction,
> EA-E4 and EG-X3 FIXED, §RR3 RR3-X1 … X15 FIXED; pins `tests/test_sf_rr3_the_page_and_the_copy.py`, 82):
> - **Reproduced first:** four read-only investigators (Sonnet) staged every row on today's tree; their boards became
>   the pins. SFR-D27 (the neighbours answer is the authored map's) and SFR-D15 (the page was right; the playtest digest
>   read the wrong field) did not reproduce as written.
> - **The copy and the page:** every row ONE function seam; the courts the desks name carry their article; a truce is
>   "paused, not over"; the page's order (a satellite over a mauled corps, the fleet over a client general); a top-up,
>   a brewing and a declaration are news once; the famine's count, toll and subject agree.
> - **Narration C6 re-read by hand** (the gate's CMD-H sample): 8 of 10 on the entry tree, **10 of 10** on the slice's.
>   The re-read found RR3-X13 (one settlement ending three wars led as "the war with Britain is over") and X15 (six
>   declarations told as one court's, and again the next morning) — both FIXED.
>
> **Traps this session paid for:**
> - **The front page's lever-down arm** (`tests/test_sf_page_the_front_page_of_the_peace.py::TestTheDrivenArms`) replays
>   the Step 7 page turn for turn: every new seam that can move a CMD-H headline joins its `SEAMS_DOWN` (the driver's
>   `--seam MODULE:NAME=EXPR`, a lambda over `a`/`k`). A weight change must be a seam too (`_vassal_lost_weight`), never
>   a table edit — `--seam` holds callables only.
> - **Escalation variants may only name fields the class's own template supplies** (`test_pc2_pc7…::test_escalation_copy_is_formattable`):
>   override `fmt["who"]` in the escalation block rather than adding `{who_run}` to a variant.
> - **The page's dedupe keys on (class, identity) AND text:** candidates added with no identity share the class as their
>   identity, so the first to lead strikes every other one off the page (RR3-X15's cause). Give a merged or per-court
>   candidate its own identity.
> - **Events stamped at the tick** (the coalition's turn, the corridor's top-ups, the league's declarations) carry the
>   NEW turn and sit two mornings in the window — gate them (`int(e["turn"]) == world.current_turn`) or remember them.
> - Write edit scripts with the Write tool and run them; a heredoc with quotes and `→` broke twice.
> - `CLAUDE.md` stands near its 62,000-byte cap: swap its live-state rows, shorten as you swap.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

The Score Finish residue, its third session — SF-RR4 "war, truce and the standing order" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/SCORE_FINISH_SPEC.md` §3 Step 9 (the SF-RR4 row — its rows, done-when and test), `docs/BUG_FIXES.md` §Score Finish Step 8 (the SFR-D / SFR-B rows; `tools/defect_census.py --open` lists the open ones) and §The Economy Gate (EG-X5), `docs/DESIGN_REFINEMENT.md` EG-D3 (the bench, ruled October 13), `docs/audits/SFR_DEPTH_CAMPAIGN_2026_10_05.md` (the playtester's report the D rows quote), and `docs/PLAYTESTING.md` (Mode A; the CMD arms are `tools/score_run.py`'s).

Scope — the design is the spec's; rule the details at the head, measured, and flag any reversal:
0. **The user's rule (October 20, 2026): diplomacy is never typed.** No new line teaches a typed diplomatic order; every diplomatic act it names is a Cabinet row or a row's `choices`.
1. **SF-RR4 "war, truce and the standing order":** SFR-D3, D4, D5, D6, D18, D22, D29, D31, D34, D35; SFR-B1, B2, B5, B14; the economy gate's EG-X5; and **EG-D3's bench** (the long pole — Spain: Cuesta, Blake, La Romana; Sweden: Toll, Adlercreutz; Bavaria: Wrede — authored in `europe_1805.json`'s `marshal_pool`, validated by `modding/validator.py`, each court commissioning from it at war on the seeded board). Most D rows are "unverified beyond the playtester's quoted digest lines" — **reproduce each first** on a board (the depth archive `docs/audits/score_runs/2026_10_05_sfr/depth/` holds the chunk digests and scripts; a fixture save or `--save-at N` stages the turn; read-only Sonnet investigators, one per family, worked well in SF-RR3); a row that does not reproduce on today's tree is closed by its reproduction attempt, named, not by assumption. Each fix pinned in `tests/test_sf_rr4_war_truce_and_the_standing_order.py`, its seam held down reproducing the row.
2. **Done when** every row's pin flips with its seam, AI aliveness C1 reads 0 lapses on the CMD arms, and the bench is built: each of Spain, Sweden and Bavaria commissions from it at war, `BASELINE_SERIES` re-recorded once with attribution (the series arms' idiom, one seam per change), AI aliveness C6 and living balance F1 re-read.
3. **If the session has room:** SF-RR5 "the frames at both scales" — sized at RR4's close; otherwise it heads the next session, named in STATUS with its pin.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this session or heading the next); a change that reaches the AI runs the attribution arms (`tools/_pc_s14p3_series_arms.py`'s idiom: one seam per change) with `BASELINE_SERIES` byte-identical or every movement attributed and named; a new parser route adds its golden-corpus row and regenerates the routed words if a verb moves (`python -m tools.gen_routed_order_words`); the Godot parse harness if a `.gd` changes; a page seam that can move a CMD-H headline joins the front page's `SEAMS_DOWN`. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when SF-RR4's rows are FIXED (or closed by their reproduction) with their pins, the bench is built and measured, STATUS ▶ NEXT UP names what follows (SF-RR5, RR6, then S14b), and this file is overwritten for it.
