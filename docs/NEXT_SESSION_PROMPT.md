# NEXT SESSION PROMPT — Row RE "Affairs of State": RE-6 LANDED and the courts' Edicts ARMED (the user's review first), then RE-5 the close; row AU after RE

> Overwritten each time a session hands off. Current hand-over: **November 2, 2026 — RE-6 the Edicts LANDED in three
> commits** (`bb9b89d7` the lifecycle, the three offers, the courts' rung and the measure; `f967ca07` the LAWS book's EDICTS
> block, the frames and the records; then the flip — the courts' Edicts ARMED by the user's word, §25.6; rules `SYSTEMS_REFERENCE.md` §167; the record `RECURRING_EVENTS_SPEC.md` §25),
> after RE-R the reactions (`ed28edf4`, §24 / §166), RE-C the Correspondence (`009eae6e`, §23 / §165) and RE-H the
> Haiti letter (`247e4e27`, `2b47a93a`, `98bb5910`; §22 / §164); the row before S15 by the user's ruling of October 31
> (§0c). **All four tiers of §16b have their content:** the letter, the home, the reactions, the squadron — and the
> Edicts: a decree for a term on the laws' own seams (`reforms.effect_terms`' second source, expiry derived from the
> turn), three offers under the one register — the Magazines (Daru), the Remounts (Dejean → Lacuée de Cessac), the
> Camps of Instruction (Berthier → Clarke) — the LAWS book's EDICTS block, the slip's "In force until …", and the
> courts' rung at the same prices (`affairs.find_ai_edict`, the `decree_edict` verb), **built, measured with the rung
> up, PARKED for the ruling because the measure found a shape change (§25.3) — and ARMED the same evening by the
> user's word, "Flip it on" (§25.6)**: the five courts with a laws deck decree two to four edicts a campaign, the
> ambient series moves from turn 10 and every road arm's end turn moves against the unarmed control — France falls
> earlier on all three Throne-road arms — while the letters alone move none; the reach, the roads, the probe and the
> series re-measured and re-pinned, RE6-4 (the judge's stale board) fixed in the measure.
>
> **FIRST — the user's review and rulings, before any code:**
> 1. **The courts' Edicts are ARMED (§25.6) — the user's word of November 2, "Flip it on".** Nothing is owed here;
>    to park them again is one line (`affairs.ai_decrees()` → False) and the chain. What the flip moved: the Marine's
>    letter leaves the treaty road and the Rhine road's `historical` arm to the offers (the Remounts' and the
>    Magazines' premises stand longer) — RE-5's reach review weighs it with RE3-6 / RE3-7.
> 2. **The readings:** RE-H (§22.1, §22.2, §22.4), RE-C (§23.2), RE-R (§24.2), RE-6 (§25.4 — the store and its
>    derived expiry; one gate with two bars; the Remounts' corps clause; Berthier writing twice; the prices as
>    drafted; the `later` chapters).
> 3. **The reach the measure found (§25.2, §25.6):** the Memorial's scripted mornings went to the offers (the Remounts'
>    bar of 2,500 against the Staff's 11,500 — the longer-standing premise picks); with the courts armed the Remounts
>    on 31 of 55 arms through the corps clause, none on the six hand-played boards; the Camps on 7; the Magazines on
>    15; the Host 20, the Memorial 13, the Haiti letter 22. The levers are
>    in-band (`below_pct`, a corps threshold of its own, the prices) — RE-5's reach review is the venue, with
>    RE3-6 (the Crown fires nowhere since S14k) and RE3-7 (the roads since S14j/k), and RE3-9 (the untracked
>    `.import` files). **Build nothing on RE3-6 / RE3-7 / RE3-9 without the user's word.**
> 4. **Row AU — authority as a currency, the push and the pull — stays queued AFTER RE and before S15**
>    (`docs/AUTHORITY_CURRENCY_SPEC.md`; the gate first, in its own session, after RE-5).
>
> **THEN — RE-5 the close (§16b, 0.5 session), its own commit; records §26 / `SYSTEMS_REFERENCE.md` §168 / finds
> `BUG_FIXES.md` §RE5.** (a) **The Mode C walk on 8007** (`docs/PLAYTESTING.md` Mode C; `SOVEREIGN_PORT=8007`,
> `INK_IRON_SAVE_DIR` set, one engine per machine): a sealed letter answered (the apostille and the seal), the
> Correspondence read, a squadron sailed and settled (the `haiti` family's board: the Emperor home under the
> blockade, 45 sail, the chest past 1,500), an edict decreed and seen on the LAWS book and in the recruit quote,
> the Watch naming the next letter; every frame read at both scales. (b) **The reach review** — each template's reach
> recorded (§21.3, §22.1, §22.4, §25.2) and the user keeping, re-premising or deleting any letter the review judges
> (the count pin in `tests/test_affairs_pacing.py`), the courts' rung armed by the user's word (§25.6). (c) **`tools/_affairs_lapse_share.py`**
> (§17's dial instrument: the share of affairs lapsing, read from the testers' saves' occurrence rows — written at
> RE-5, the dial itself struck from v1). (d) STATUS's four tier lines closed; `PRE_DEPLOY_PLAN.md` §2's RE row ✅ and
> S15 next after AU. Then **AU's gate** in its own session.
>
> **Traps the row has paid for (do not re-discover):** the spec, `SYSTEMS_REFERENCE.md`, `BUG_FIXES.md` and
> `MODDING_FORMAT.md` are CRLF files — edit through Python with the file's own endings, never `cat >>`; **`Path.write_text`
> on Windows turns LF into CRLF — write bytes** (it bit the scenario and the fixture once tonight); a write by a
> RELATIVE path raised `Errno 22` once — write by the absolute path; the shell heredoc eats a long block AND turns
> `\\n` into a real newline — write scripts with the Write tool and run them by path; the JSON deck files are
> hand-formatted (the scenario at indent 4 with compact leaf objects, the fixture at indent 2) — insert entries
> textually after the Haiti letter, never re-dump the file; `moments._clean_runtime` keeps ONLY ints and `{str: int}`
> maps in the affairs runtime (a list or a nested dict is dropped on load — the edict store is a flat
> `{"lord|template": until}` map for that reason); `affairs.runtime()` CREATES the key on an armed world — a reader
> goes through `MO._store` (the boot-purity pins); the premise memo caches a predicate's whole read for the turn, so a
> gate the same morning must be read fresh (`edict_refusal` outside the memo); `affairs.pick` takes the
> longest-standing premise, so a cheap offer's streak beats a dear door's — mind the bars when authoring; a `passed`
> row written at turn 1 cools a template for its cooldown (`tests/_affairs_boards.py::rest_the_offers`), never an
> ARRIVED row (it counts toward the act's cap of six); `tools/_affairs_series_arms.py --out` to a NEW file (its default
> is the committed RE-H record a pin reads); `_vp1_road_arms.py`'s record keeps `results` as a list keyed by `arm` /
> `seed`; the hand-played saves live under `tools/playtest_runs/dd_b_2026_10_2*/*/saves/autosave.json` inside a
> `world` wrapper; `GET /dispatch` and the morning build must not mutate; `compose_issue` is a pure read; the OPS table
> binds each apply function at import (a seam is the function it calls by name); `filter_campaign_log` is 499 lines
> against a cap of 500 — the "moment" token was the last free line; the client censuses: a code-built `fit_content`
> RichTextLabel must chain `add_child` to an `@onready` node under the scene's ScrollContainer in ONE function; a
> scene ScrollContainer needs `custom_minimum_size`; sizes by `theme_type_variation` only; every `bb_button_chip(` url
> expression needs a `test_cn4` REVIEWED row; the IQ10 `press` verb matches a Button's text EXACTLY; the parse harness
> via `Start-Process`; the frames: `tools/iq10_capture_payloads.py --out <dir> --only moments`, then
> `tools/iq10_run_captures.py --payload-dir <dir> --only <ids> --date … --out-dir <run> --png-dir docs/audits` and once
> `--physical --physical-scale auto` to a scratch dir, then `tools/uxr0_readability_report.py <physical>/index.json
> --record docs/audits/uxr0/readability_<label>_<date>.json --surfaces a,b`; `ruff` is not on the Bash PATH
> (`.venv\Scripts\python.exe -m ruff check backend/`); the hook runs the full suite in parallel (~10 min) — commit from
> Bash in the background with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` and edit no tracked file while it
> runs; STATUS keeps at most seven session entries (archive the oldest to `docs/archive/STATUS_2026_Q4.md`, newest
> first); CLAUDE.md sits at its byte cap (`tr -d '\r' < CLAUDE.md | wc -c` against 62,000 — every added line is paid
> for by a trim).
>
> **Open with the user, unchanged:** RE3-6, RE3-7, RE3-9 (above); the certificate (`INK_IRON_SIGNTOOL_ARGS`); S14d's A1
> as applied; AO's three questions (`REFORMS_SPEC.md` §5a); SF-NAV-1-D1.

> **Traps the flip paid for (November 2, 2026):** the series rig's `prior` is HEAD's `BASELINE_SERIES` (`git show`),
> so a flip's committed rig record carries the OLD series as its prior and the pin reads it so (`test_ai_drill_fix`);
> keep the previous rig record under its own name (`_affairs_series_arms_reh.json`) before re-recording `_final`;
> attribute a series move by event on the ambient board (the `tools/_rf3_board_events.py` loop with the seam up and
> down), never by guess — the courts' decrees re-roll the turn's draws (an admin action at 1.79) and a satellite's exit
> can change KIND (a bribe for a rebellion) as well as turn; the moments' blindness pin needs a letters-only arm once
> the courts act on the armed tree; the judge's `shown` is the driver's copy of the board, not the client's re-read —
> compare against a re-plan at the answer before calling a quote false.
