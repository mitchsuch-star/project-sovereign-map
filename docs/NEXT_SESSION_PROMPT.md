# NEXT SESSION PROMPT — Pre-Deploy S14f part 2: the P3s, the homed siblings, the rulings' builds, the re-play

> Overwritten each time a session hands off. Current hand-over: **October 24, 2026, after S14f part 1 — the
> re-measure's rows: the P1, the four rulings, the fourteen P2s — LANDED** (`SYSTEMS_REFERENCE.md` §150; commits
> through the hook — `git log -5`).
>
> **What the last session delivered:** S14E-1 (the P1) with S14E-D1 built as recommended (a typed order's first
> step ASKS, every personality alike), the fourteen P2s S14E-2 … 15, S14E-31 (D4's floor on the war title IS its
> fix), D2 (the court's own slice) and D3 (the shut-out price kept and stated on both roads) — each row reproduced
> on the shipped board, fixed at its cause, pinned in `tests/test_s14f_the_remeasure_rows.py` (397 tests), then
> swept: 68 siblings S14E-X1 … X68 filed in `BUG_FIXES.md` §S14E, 49 FIXED in the part (every P2 among them), 12
> homed to part 2, 6 awaiting a ruling (D5 … D11 in `DESIGN_REFINEMENT.md` §S14E, each with a recommendation), 1
> closed by ruling. `BASELINE_SERIES` byte-identical on seven arms (`tools/_s14f_series_arms_final.json`); the
> ratchet held (levers 231 — two old ones retired for the two new; `_muster_supply_quote` lifted out of the muster
> builder); the Table lesson's probe record refreshed.
>
> **Traps the last session paid for:**
> - **`--log-file` crashes the Godot engine at start on this machine** (an access violation right after the banner;
>   `--import`, headless and windowed alike; HEAD's scripts and a fresh `.godot` cache too — an hour lost suspecting
>   the project). The parse harness runs green without it: `Start-Process <godot> @("--headless","--quit","--path",
>   "godot-client/project-sovereign","--script","../../tools/godot_parse_check.gd") -Wait -PassThru`, EXIT=0, the
>   report regenerated; its console goes to `%APPDATA%\Godot\app_userdata\Ink & Iron\logs\godot.log`.
> - **Eleven row agents in one checkout:** every agent edited by anchored Edit calls only and re-grepped its
>   markers at its close; two transient NameErrors (`mission_gate`, `feedback_phrase`) and one `_muster_spread`
>   AttributeError surfaced in neighbours' runs mid-flight and vanished at the close — run a sibling's test file
>   once more before reading a failure as yours. Tests went in per-row files and were merged by a script with a
>   rename map; module-level helpers prefixed `_r<n>_` kept the merge mechanical.
> - **A new lever is a ratchet failure** (`test_code_health_ratchet.py`: levers ≤ 231, functions over 500 lines
>   ≤ 28): retire one before adding one, or inline the rule at once; a pin that reproduces the old behaviour by
>   flipping a lever makes the lever load-bearing (`THE_MUSTER_STATES_ITS_SPREAD`,
>   `A_CORPS_THAT_CANNOT_ARRIVE_IS_NOT_PRESENT`).
> - **The shut-out price's clock clause** fires on the boot board (Spain stands at the alliance's line, 40), so
>   any pin on Spain's exact sentence carries `SPAIN_CLOCK`.
>
> **For the user before part 2 (not blocking — the session builds the recommendations unless overruled):** the
> seven rulings S14E-D5 … D11 (`DESIGN_REFINEMENT.md` §S14E); the two calls taken under the standing delegation
> (S14E-X30 once per End Turn; S14E-X61 the ready road's warning); a third measure after part 2 (recommended, 1.0).
> Also theirs: S14d's A1 as applied, UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1.
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14f part 2 — the re-measure's rows: the nineteen P3s, the twelve homed siblings, the seven rulings' builds, the closing re-play — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/PRE_DEPLOY_PLAN.md` §2 row S14f; `SYSTEMS_REFERENCE.md` §150 (part 1's rules — what the rows' siblings now read) and §149 (the measure); `BUG_FIXES.md` §S14E (every row's cause, sightings, decided fix, test name — the P3s S14E-16 … 30, 32 … 35 and the homed siblings S14E-X6, X22, X25, X31, X33, X36, X37, X38, X39, X51, X63, X67); `DESIGN_REFINEMENT.md` §S14E (D5 … D11 with recommendations); `docs/audits/DD_B_RE_MEASURE_2026_10_24.md`; the records `docs/audits/dd_b/{conquest,diplomacy,sea}_2026_10_24/summaries.md` and the cited frames; `docs/PLAYTESTING.md` (the DD-B instrument, Mode C); `SYSTEMS_REFERENCE.md` §115 (the instrument); CLAUDE.md's Golden Rules (1, 5, 9, 10).

Scope (the row, part 2): **the seven rulings' builds as the user rules them, the recommendations by default** (D5 the harshness penalty on the court's slice — on the series arms; D6 the commentary tag off the pair; D7 the offer row prefilled — an expansion, only on a yes; D8 the pass reaching only the allies whose war the table ends — on the series arms; D9 one war-card line for a Class T dream; D10 the camp tinted on the map; D11 the mean re-seated — on the series arms, the gate's and the band's pins named); **then the twelve homed siblings and the nineteen P3s** in the ledger's order, each reproduced on the shipped board first, fixed, pinned in `tests/test_s14f_the_remeasure_rows.py::TestS14E<n>` / `::TestS14EX<n>` (append to the one module), then swept (Rule 10 — new siblings filed as S14E-X69 … and fixed in the part); **then the closing re-play** of every sighting of the 35 rows on the DD-B instrument (`tools/dd_b_play.py` against a sandboxed backend on 8006, never 8005; the cited frames re-shot into `docs/audits/dd_b/replay_2026_10_*/`; each sighting's frame read and the row's fix seen). `BASELINE_SERIES` byte-identical on every arm except where a ruling moves it consciously, the moved pins named (`tools/_s14f_series_arms.py` chained from part 1's record).

Done when: every S14E and S14E-X row is FIXED with its test; the seven rulings recorded in `DESIGN_REFINEMENT.md` §S14E as built (or as the user ruled); `SYSTEMS_REFERENCE.md` gains §151 (part 2's rules and the re-play's record); the census reads 0 open S14E and 0 open S14E-X; the parse report refreshed and committed (never with `--log-file`); STATUS ▶ NEXT UP names what follows S14f (the deploy gate per `PRE_DEPLOY_PLAN.md` §2, and the user's call on a third measure) and this file is overwritten for it.

Rules: "diplomacy is never typed"; Golden Rule 1 (combat modifiers in `marshal.py` only), 5 (the AI uses the same executor), 9 (no open-ended deferrals), 10 (the sibling sweep); grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process (`tools/godot_parse_check.gd`, expect EXIT=0, commit the refreshed report); the code-health ratchet (`tests/test_code_health_ratchet.py`: retire a lever before adding one; no function over 500 lines); subagents on sonnet or haiku, never the orchestrator's model. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches; never start a DD-B engine while the hook runs.
