# NEXT SESSION PROMPT — Pre-Deploy S14h: the third measure's rows, then S15's deploy

> Overwritten each time a session hands off. Current hand-over: **October 26, 2026, after S14g — DD-B's third
> measure**: three fresh players, the same brief and roads, 20 turns each in the real client at 5120×1440 on the build
> the testers will get (master `a47bc116`), 990 actions, 0 script errors. **33 causes in 60 turns = 5.5 rows per 10
> turns, 0 P1** — the done-when (under 5 per 10 turns, 0 P1) is **NOT met on the rate** (four causes over: 33 against
> 29) and is met on the P1 bar for the first time (3 → 1 → 0). `docs/audits/DD_B_THIRD_MEASURE_2026_10_25.md`;
> `SYSTEMS_REFERENCE.md` §154; commits through the hook (`git log --format=%h -5`).
>
> **What the last session delivered:** the three roads' records (`docs/audits/dd_b/{conquest,diplomacy,sea}_2026_10_25/`),
> the causes record and the metric read by the ONE tool, the write-up, **34 OPEN defect rows** (`BUG_FIXES.md` §S14G:
> S14G-1 … 33 — twelve P2s first — and the instrument row S14G-I1), the seven design questions S14G-D1 … D7 with
> recommendations (`DESIGN_REFINEMENT.md` §S14G), the pins (`tests/test_dd_b_the_client_hands.py::TestTheThirdMeasureRecords`),
> S14h in the plan (`PRE_DEPLOY_PLAN.md` §2: 2.0, two parts) and one judge correction (`ALREADY_HELD_RX`, a repeat of a
> standing order is the board declining, free — the sea road's one P1 proxy was an instrument false positive). Nothing in
> the game changed.
>
> **What the measure found, in one breath:** none of the second measure's 35 rows came back as filed; five came back in
> part (S14E-11, 13, 15, 17, 18 — the fix fired as built and the player asked for what it withheld); **27 of the 33 causes
> are siblings of, or partial returns of, a row an earlier slice fixed**, six are new. Thirteen are a price or consequence
> unstated at the point of choice, eleven two readings of one fact (the advice, card or record against the act), nine a
> control that does something other than it says or hides its answer. The shape the partial returns share: **the fix
> states the consequence in ONE place — a tooltip, a reply, a page — while the player decides in another.**
>
> **Traps the last session paid for:**
> - **A hook run sweeps the working tree** — two sessions committed in one checkout; whoever commits first takes the other's
>   half-written doc sections, so the second session's ledger edits waited for the first's commit message.
> - **The judge's `misread` is a proxy, not a verdict** — read the reply by hand and the standing order it repeats before
>   filing a P1; a new reply shape goes in `_score_probes` as its own regex AFTER the action words, never into
>   `BOARD_GATE_RX` (that moved a committed row).
> - **A player's `--n` can be off by one or two** — read the neighbouring states and `actions.log` for the true frame.
> - **A row can be half right** — eight of the 37 are partly the player's misreading; the cause as traced is in the ledger
>   row, not the player's account.
> - **The Bash heredoc eats quotes and `\b`** — write every script and every row's text with the Write tool.
>
> **For the user:** the seven rulings S14G-D1 … D7 (recommendations in `DESIGN_REFINEMENT.md` §S14G; the standing
> delegation of October 14 and 16 applies if you want them taken as recommended); the certificate (not on this machine —
> the build is unsigned until it arrives); S14d's A1 as applied, AO's three questions (`REFORMS_SPEC.md` §5a), SF-NAV-1-D1.
> The S15 session reported the walk done (seven ✓, UXR3-2 closed, UXR3-82 / 83 fixed and re-shot).
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14h — the third measure's rows — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log --format=%h -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/audits/DD_B_THIRD_MEASURE_2026_10_25.md` (§4 the families, §5 what came back, §7 where the players were wrong, §8 the five mentions); `docs/BUG_FIXES.md` §S14G (the 33 rows and S14G-I1 — each with its traced cause, prior row, sightings and decided fix); `docs/DESIGN_REFINEMENT.md` §S14G (D1 … D7, and the user's rulings if given); `SYSTEMS_REFERENCE.md` §154 (this measure) and §150–§152 (what S14f changed — the sentences to carry to the surface beside); `docs/PLAYTESTING.md` Mode C and the S14f part 2 re-play (§151.17); CLAUDE.md's Golden Rules (5, 9, 10).

Scope: **the user's rulings first** — D1 (retaking an ally's ground: liberation, handed back at once), D2 (the aggressive marshal's support interrupt: keep it, say it at the order and the gate), D3 (which letters shut the Cabinet: a great court's and an ultimatum), D6 (a bought-off court in the league: keep the predicate, state it) are the part-1 builds; D4 (the band's fog policy) and D5 (one diplomat slot: keep it, price the trade) part 2; D7 is the done-when's own question. **Part 1: the twelve P2s S14G-1 … 12**, each reproduced on the shipped board (or the fixture world) first, fixed at the cause, pinned (`tests/test_s14h_the_third_measure_rows.py::TestS14G<n>`), then its sibling sweep (Rule 10) — and the sweep this time carries each fixed sentence to EVERY surface where its choice is made (a tooltip, the reply, the badge, the letter's body, the chip, the page; the lesson of the five partial returns). Rule 5 applies to S14G-1 (the AI's capture path), S14G-3 (the strategic processing order) and S14G-33 (the pathfinder's tie-break moves the AI's roads too): each behind ONE seam the series arms can hold down, with `BASELINE_SERIES` attributed (`tools/_s14f_p3_series_arms.py` is the pattern). **Part 2: the twenty-one P3s S14G-13 … 33, S14G-I1, the five mentions** (`DD_B_THIRD_MEASURE_2026_10_25.md` §8 — reproduce each on the boot board or a crafted save, then file-and-fix or refute in one line), and **the closing re-play** of every sighting on the DD-B instrument from crafted saves (`tools/_s14f_replay_scenes.py --out <run>/saves`, BEFORE `start`; the record under `docs/audits/dd_b/replay_2026_10_26/`). Done when the census reads 0 open S14G (`.venv/Scripts/python.exe tools/defect_census.py --open`) and the parse harness, the ratchet and the full suite are green through the hook. **No fourth measure** before the deploy unless the user calls one (S14G-D7). Then S15 resumes: `deploy\build.bat` (unsigned until the certificate arrives), the clean-machine run, `docs/audits/RELEASE_<version>.md`.
