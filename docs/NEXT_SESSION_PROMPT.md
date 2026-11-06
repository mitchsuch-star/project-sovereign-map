# NEXT SESSION PROMPT — S15 the deploy: the user's walk, the certificate, the build, the clean-environment run, the release record

> Overwritten each time a session hands off. Current hand-over: **November 6, 2026 — S15's head ✅ LANDED: the last
> three defect rows closed, the deploy gate at 0 open defect rows** (`SYSTEMS_REFERENCE.md` §177; `BUG_FIXES.md` §RE3
> ALL 10 FIXED and §S15H; three commits through the hook — RE3-9 `a31ae7a0` the 188 `.import` sidecars force-added,
> RE3-6 `cfcc9544` the Crown of the Reich asks a vassal Francis and his loyalty pays (S15H-1 … S15H-5 with it), RE3-7 the road record re-recorded on the
> final tree; the user's three words in Plan Mode: "Force-add all 188", "Ask him; loyalty pays", "Teeth: re-record,
> re-pin"). `tools/defect_census.py --open` reads **0 open defect rows, 0 open design rows**.
>
> **NOW — S15 the deploy proper, the user's own** (`docs/PRE_DEPLOY_PLAN.md` §2's S15 row, `docs/UX_UI_REVIEW_PLAN.md`
> §UXR-4, `SYSTEMS_REFERENCE.md` §153.3–§153.4): (1) **the walk** at the user's monitor — the UXR-4 marks (rows UXR3-2,
> 24, 29, 41, 79 … 81 and the walk's own UXR3-82 / 83; their frames `docs/audits/uxr4_s15/`), each ✓ or ✗ in
> `UX_UI_REVIEW_PLAN.md` §UXR-4; a ✗ is a row, fixed before the build; (2) **the certificate** — owed by the user,
> nothing on this machine (no signtool, no certificate in either store): the day it arrives set
> `INK_IRON_SIGNTOOL_ARGS` (and `SIGNTOOL` if the SDK's tool is off PATH) for the session, never in a file; (3) **the
> build** — `deploy\build.bat` from the repository root: it imports and exports THIS working tree's client
> (`%cd%\godot-client\project-sovereign`, Godot 4.4.1 from `%USERPROFILE%\Downloads\...`), freezes the server, zips
> the bundle; UNSIGNED until the certificate (the banner says so; a configured signing that fails stops the build;
> `tools/release_smoke.py --expect-signed` once signed; pinned by `tests/test_s15_the_signed_build.py`); the first
> Godot import of an empty cache logs the theme's fonts "not yet imported" and a second pass logs 0 — the build's own
> import pass is that first pass (§177.1); (4) **the clean-environment run** — `tools/clean_env_run.ps1`: the zip
> unpacked OUTSIDE the repository, a PATH of the system alone (no Python, no Godot), no `.env`, its own `APPDATA`,
> `launch.bat` the one door; recorded as a clean-ENVIRONMENT run, never a clean machine (§153.4); (5) **the release
> record** — `docs/audits/RELEASE_<version>.md` from `docs/audits/RELEASE_TEMPLATE.md`. **After the deploy, first:**
> S14k part 3 (goals for Bavaria, Spain and Naples — `PRE_DEPLOY_PLAN.md` §2 row S14k-3; the strict xfail
> `test_every_armed_court_carries_a_goal` turns red the day it lands), then S16 (the `main.gd` split) and S17c.
> Plan Mode first; the user's review per slice.
>
> **Open with the user (none blocks the deploy):** the flip's two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3), the
> Crown's readings (`EVENTS_SPEC.md` §18 — the loyalty price −10, the quote's line, a vassal of another lord asked
> too, Decline free), the road record's readings (`VP1_DESIGNS_SPEC.md` §14.6 — the lapse arm's flags, the kept
> file, the scripts left as written), S14d's A1, AO's three questions (`REFORMS_SPEC.md` §5a), the crown term's level
> (`docs/audits/ECONOMY_REBALANCE_2026_10_27.md` §4.2), SF-NAV-1-D1.
>
> **Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are
> named functions), functions over 500 lines 28 of 28, `WorldState.to_dict` 497 of 500 (every new field in an
> existing store), CLAUDE.md within 62,000 LF bytes (a handful of bytes of headroom: pay a row by a trim), STATUS at
> most 7 "▶ ▶ ▶" entries (archive the oldest to the top of `docs/archive/STATUS_2026_Q4.md`); every `except Exception`
> must speak; a measure chain runs ALONE and no backend or deck edit lands while it runs; the driver reads `--seam`,
> never `INK_IRON_SEAMS`; **an instrument drifts under the slices — check each measure's flags against its record's
> note** (S15H-1: Road I answered had run without `--moment accept` since November 1) **and every rig shim passes
> through `*a, **k`** (S15H-2: a fixed-arity `grant_edict` shim raised a TypeError the courts' admin step swallowed and
> the rig's board decreed nothing — the series pin itself was the tell: the rig's "shipped" arm differed from a series
> the pin reproduced); a record diff is read WHOLE (every row, every key — `tools/playtest_runs/.../re3_6/` holds the
> idiom), and a move is attributed by a second run with the one flag or seam changed; a rig re-run writes its OWN
> record (`--out`) — a prior slice's record stays that slice's (its pins read it); the scenario
> (`godot-client/project-sovereign/assets/maps/europe_1805.json`) and every asset sidecar sit under the ignored
> `assets/` — `git add -f` them, every time (`tests/test_s15_head_import_sidecars.py` asks git for the whole project);
> a fresh clone's Godot import regenerates an untracked sidecar's `uid=` and nothing else — track every sidecar; the
> docs are CRLF or LF per file (edit through Python on bytes, asserting each replacement matches once; write patch
> scripts with the Write tool — the heredoc eats backslashes); the deck JSON files are hand-formatted — insert text,
> never re-dump; the three decks (the scenario, `tests/fixtures/moments_block.json`, `tests/fixtures/affairs_block.json`)
> are one deck, in lockstep; the moments' `deck_sha` is the deck's mechanical identity — an op added reds
> `tests/test_moments_pacing.py` until the chain re-records; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F
> <file>` from Bash in the background (the hook runs ruff and the full suite, 10:20 on November 6; never `--no-verify`)
> and read the log's EXIT line; Godot: one engine at a time, `--log-file` and every capture path ABSOLUTE; a `.gd` edit
> with the morning's parse report FAILS the hook (regenerate `tools/godot_parse_report.json`); `tools/playtest_runs/` is
> gitignored; run a probe under `python -X utf8`; the pulse takes the matter whose premise has stood LONGEST; a letter
> whose Accept is priced in authority alone books a purchase wherever an accept dial answers it; a new card option goes
> LAST; a reused node keeps its scene position; a letter's answers are planned at every read (`moments.refresh_letter`);
> the courts boot at 60, so anything a court may buy in authority moves the series; `get_visible_enemies` is the
> PLAYER's fog (a court's sight is `get_live_visible_enemies`); a rung's structured field reaches the executor only
> through `enemy_ai.execute_admin_phase`'s whitelist.
