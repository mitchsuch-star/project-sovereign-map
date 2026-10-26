# NEXT SESSION PROMPT — Pre-Deploy S14h part 2: the P3s, D4 / D5, S14G-I1, the five mentions, the re-play; then S15's deploy

> Overwritten each time a session hands off. Current hand-over: **October 26, 2026, after S14h part 1** — the third
> measure's twelve P2s S14G-1 … 12 FIXED, the rulings S14G-D1, D2, D3, D6 BUILT as recommended, 55 siblings S14G-X1 … X55
> filed and fixed (3 closed by pin or judgement), `BASELINE_SERIES` byte-identical on every arm, the parse harness green on
> 80 scripts and 17 scenes, the ratchet held. `SYSTEMS_REFERENCE.md` §155; `BUG_FIXES.md` §S14G; `DESIGN_REFINEMENT.md`
> §S14G; commits through the hook (`git log --format=%h -5`). **The census: 22 open defect rows (S14G-13 … 33 and the
> instrument row S14G-I1) and 2 open design rows (D4, D5).** The release build (S15) waits for 0.
>
> **What the last session delivered, in one breath:** an ally's ground retaken is a liberation handed back at once, on
> both sides, said on every surface (D1); the aggressive marshal's interrupt kept and said at the order, on the quote and
> at End Turn's gate (D2); only a great court's letter, an ultimatum or a war decision shuts the Cabinet, and the lock
> stands wherever the player looks (D3); a bought-off court still counts toward the league and every page says so (D6); a
> plain support lapses alike whatever the supporter's name; a march to where he stands is refused free; the petition card
> names its live quarry and asks before sending him at another man; the truce's consequence and the front note ride every
> road; the design counsel opens a pre-loaded confirm and every generic menu opens a confirm instead of sending; the
> licence and the guarantee name what they cost; guarded ground is asked about before the order and said on every reply;
> the table's gold ceiling is where the player looks and no gold that buys nothing is authored.
>
> **Traps the last session paid for:**
> - **A "down" switch for player-only text wants no module-level lever** — the ratchet caps them at 231; two slipped in and
>   were struck. Every seam is a function or a `Class.method` the series tool can patch.
> - **A sibling found in another builder's file that wave goes to the next wave; one found in the builder's OWN file is
>   the builder's** — send it back for it rather than filing it.
> - **Placeholder sibling ids live in CODE comments too** (`S14G-X<row>.<k>` in `.py` and `.gd`): renumber them with the
>   tests and the ledger in one pass (the one merged failure was a `.gd` comment the test read).
> - **The series tool chains from the prior record's arm "0"** (the shipped tree), never its "ALL" (every seam down — the
>   old series); an arm's name is the set of seams held DOWN.
> - **The Godot exe sits INSIDE a folder of the same name** (`Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe`);
>   `Start-Process` on the folder fails with "cannot find all the information required" and leaves the old report in place.
> - **The row-7 build's one flake** was a 10 % mood-variance roll (Ney objected to a retreat): patch `apply_mood_variance`
>   to the identity in such a test, never seed around it.
> - The Bash heredoc eats quotes and `\b`; `ruff` and `python` are not on the Bash PATH (use `.venv\Scripts\python.exe -m ruff`).
>
> **For the user:** the certificate (not on this machine — the build is unsigned until it arrives); S14d's A1 as applied,
> AO's three questions (`REFORMS_SPEC.md` §5a), SF-NAV-1-D1.
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14h part 2 — the third measure's P3s, the two remaining rulings, the instrument row, the five mentions and the closing re-play — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log --format=%h -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `SYSTEMS_REFERENCE.md` §155 (what part 1 changed — the helpers and sentences to reuse: `liberation_line`, `aggressive_interrupt_clause`, `support_terms_clause`, `truce_runs_on_consequence`, `front_line`, `buyoff_league_clause`, `licensed_war_cost_clause`, `declaration_cost_clause(aggressor=)`, `guarded_provinces_for` / `march_guard_sentence`, `credit_ceiling_note`, `letter_locks_cabinet`, `Utils.cabinet_shut_line`) and §154 (the measure); `docs/audits/DD_B_THIRD_MEASURE_2026_10_25.md` (§4 the families, §7 where the players were wrong, §8 the five mentions); `docs/BUG_FIXES.md` §S14G (the twenty-one OPEN rows S14G-13 … 33 and S14G-I1 — each with its traced cause, prior row, sightings and decided fix; the part-1 rows and the sibling table S14G-X1 … X55 show the form); `docs/DESIGN_REFINEMENT.md` §S14G (D4, D5 — ruled as recommended October 26, 2026: D4 the band names the unscouted provinces and gives both readings; D5 one diplomat slot kept, the trade priced); `docs/PLAYTESTING.md` Mode C and the S14f part 2 re-play (§151.17); CLAUDE.md's Golden Rules (5, 9, 10).

Scope: **Part 2 of S14h.** (1) **The twenty-one P3s S14G-13 … 33**, each reproduced on the shipped board (or the fixture world) first, fixed at the cause, pinned (`tests/test_s14h_the_third_measure_rows.py::TestS14G<n>` — add to the ONE module; a row file per builder merged at the end, helpers prefixed `_r<n>_`, sibling placeholders `S14G-X<row>.<k>` / `TestS14GX<row>_<k>` renumbered from X56 by origin row in the tests, the code comments and the ledger alike), then its sibling sweep (Rule 10) carrying each fixed sentence to EVERY surface where its choice is made. Rule 5 applies to S14G-33 (the pathfinder's tie-break moves the AI's roads too): behind ONE seam the series arms can hold down, `BASELINE_SERIES` attributed (`tools/_s14h_series_arms.py` is the pattern — chain from `_s14h_series_arms_final.json`'s arm "0"). (2) **D4 and D5** built as ruled, each with its defect half (S14G-17 for D4, S14G-28 for D5 — read the rows), pinned `TestS14GD4` / `TestS14GD5`. (3) **S14G-I1** — the DD-B instrument strips a bracketed `[+]` link's text (`tools/dd_b_client.gd` ~81-82, ~845-847), so a player cannot name it: list bracketed links as controls with their own words; pin on the sea #8 frames' state. (4) **The five mentions** (`DD_B_THIRD_MEASURE_2026_10_25.md` §8): reproduce each on the boot board or a crafted save, then file-and-fix (a row S14G-M<k>, FIXED in the part) or refute in one line in the write-up. (5) **The closing re-play** of every part-1 and part-2 sighting on the DD-B instrument from crafted saves (`tools/_s14f_replay_scenes.py --out <run>/saves`, BEFORE `start`; the record under `docs/audits/dd_b/replay_2026_10_26/`), its finds filed and fixed. Done when the census reads 0 open S14G (`.venv/Scripts/python.exe tools/defect_census.py --open`), the parse harness, the ratchet and the full suite are green through the hook, and `docs/STATUS.md`, `SYSTEMS_REFERENCE.md` §156, `BUG_FIXES.md`, `DESIGN_REFINEMENT.md`, `PRE_DEPLOY_PLAN.md` §2 (S14h COMPLETE) and this prompt (for S15) are written. **No fourth measure** before the deploy unless the user calls one (S14G-D7). Then S15 resumes: `deploy\build.bat` (unsigned until the certificate arrives), the clean-machine run (`tools/clean_env_run.ps1`), `docs/audits/RELEASE_<version>.md` from `docs/audits/RELEASE_TEMPLATE.md`.
