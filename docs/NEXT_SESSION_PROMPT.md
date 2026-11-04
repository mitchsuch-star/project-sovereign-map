# NEXT SESSION PROMPT — Row AU "Authority as a currency": AU-2c the Bank and the Pope (the fourth of seven slices, before S15)

> Overwritten each time a session hands off. Current hand-over: **November 4, 2026 — AU-2b the lumps and the Show ✅ LANDED**
> (`docs/AUTHORITY_CURRENCY_SPEC.md` §6.3 the landing record; the rules `SYSTEMS_REFERENCE.md` §171; AU-1 the books
> ✅ `6b9d61c4` §6.1; AU-2a the hits ✅ `ebf2e393` §6.2 and the clamp ✅ `33d4ac72` §6.2.5 — the twelve readings of
> §6.2.3 and §6.2.5.3 CONFIRMED by the user's "Confirm, start AU-2b"). Standing comes back by play, never by waiting,
> each lump through `standing.regrow` (the ceiling 95, a keyed cooldown in the tracker's `held`), the courts' parked:
> the Te Deum (`standing.te_deum_on_peace` in `diplomacy.cleanup_war_end` — the stored war score +25 or better at a
> war's END: +4 once per twelve turns per lord; Le Moniteur's generic line through the campaign log's new `te_deum`
> type), the Bulletin of the Field (`standing.bulletin` at battle step 12 and the auto-charge mirror — a laurel
> victory, `standing.laurel_victory` = `jealousy.is_laurel`'s battle AND France's dead at most half the enemy's: +4
> one per three turns, and the field's dents of the last ten turns repaid up to +8, each point once), the Return
> (`standing.the_return` each morning — back on the held seat after eight turns away: the Council's tally
> `held["council_owed"]` repaid up to 5), the honour's payback seam (`standing.honour_repaid`, inert until AU-3a
> writes `held["honoured:<marshal>"]`), the Show (the Feast of Saint Napoleon +5 for 2,500 gold, the Arc de Triomphe
> +8 for 5,000, `ceiling: 95`, `since: "AU-2b"`) and the ceremonies (+2 on the Bavarian Match's and the Throne of
> Holland's Accept). The seam AUS (`standing.sources_armed`); `BASELINE_SERIES` byte-identical on seven arms;
> 64 Bulletins on 35 of the 58 runs, the bled war roads come back by the field (the Rhine road on marengo 24 → 68).
> AU-9 fixed (two causes read a raw id).
>
> **FIRST — the user's review of AU-2b** (the seven landing readings of `AUTHORITY_CURRENCY_SPEC.md` §6.3.3 — each
> one line to reverse; the laurel's two halves and the Bulletin's size are the ones with teeth: the Bulletin paid
> +494 of the +536 the lumps paid, with its two alternatives named). Then AU-2c.
>
> **THEN — AU-2c the Bank and the Pope (§5.4's two rows, §4.1 reading 14, the §6 AU-2c row; about 0.6 sessions;
> one commit through the hook; then stop for the user's review).** Two dated letters priced in authority, on the
> affairs engine, within its closed ops:
> 1. **Author both at the head** in `europe_1805.json` and `tests/fixtures/affairs_block.json` (the lockstep):
>    **the Bank's Panic** (January 1806 — the Treasury crisis, Barbé-Marbois out and Mollien in; the Emperor back in
>    Paris 26 January): the premise "the chest strained at war" — define it as a predicate the engine holds and
>    PROBE it before arming; the Accept pays the Bank in coin (gold and one action), the Decline "Let the notes fall"
>    −4 with the Bank's regents as creditor. **The Pope's Refusal** (the demand that the Papal States close their
>    ports under the System; Ancona occupied): the premise the Berlin Decree in force and France at war with Britain;
>    the Accept the occupation's price (gold and one action), the Decline "Let the Pope refuse" −5; NO relation op
>    (no Papal court on the map — RE §6.2 P1's strike stands).
> 2. **Both refusals are priced in authority alone, so both take `bites: "floor"`** — the clamp's rule, which the
>    validator enforces ("clamp" only beside a Decline priced besides authority). Their content carries `since:
>    "AU-2c"` / `bites_since: "AU-2c"` — extend `affairs.SINCE_ROWS` and `row_armed` with a new seam (arm AUL,
>    `standing.letters_armed`) in `tests/_standing_seams.py` and `tools/_standing_series_arms.py`.
> 3. **The reach probe** (`tools/_affairs_first_arrival_probe.py`), the reach record on the 58 runs, the nondominance
>    pins for both (each answer the better one somewhere: the Accept on authority, the Decline on gold and the
>    action), the validator, the frames of both letters at both scales (`tools/iq10_capture_payloads.py` +
>    `tools/iq10_run_captures.py`, a Godot run one per machine).
> 4. **Put both to the user before arming** (RE's rule: a template without a measured premise is not armed) — the
>    reach and the premise's measured mornings in the landing record, the arming the user's word.
> 5. The records: spec §6.4, `SYSTEMS_REFERENCE.md` §172, `BUG_FIXES.md` §AU's new rows, STATUS's AU-2c line (the
>    oldest entry to `docs/archive/STATUS_2026_Q4.md`, newest first), the plan and the roadmap, this prompt for
>    AU-3a; `BASELINE_SERIES` measured on every arm, never assumed.
>
> **Traps the row has paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are
> named functions), functions over 500 lines 28 of 28 (`_execute_diplomatic_declare_war` sits at 497 — compose text
> in `standing`), `WorldState.to_dict` 497 of 500 (every new field in the tracker's `held`), CLAUDE.md within 62,000
> LF bytes (61,971 now — pay a row by a trim); every `except Exception` must speak (`backend.errors.report`); a deck
> op or clause a slice adds carries `since` / `bites_since` naming its row; the validator counts a `button_line`'s
> slots at four and caps it at 40 ("auth" fits beside a relation, "authority" does not); a dispatch event's payload
> sits under `template_vars`; a `moment_receipt` lands in `diplomatic_events`; `_affairs_measure.py --driver-flags`
> must be passed as `--driver-flags="--standing-trace"`; the measure chain is `tools/playtest_runs/<slice>/chain.sh`
> (copy the last one, change `OUT`, the series arms and the record's note; about eight minutes); THREE dated decks
> are locked equal (the scenario, `tests/fixtures/moments_block.json`, the affairs fixture's copy) and the designs
> block is pinned equal to `tests/fixtures/vp1_imperial_designs_block.json`; a new campaign-log type moves FOURTEEN
> count pins (`len(CAMPAIGN_LOG_TYPES)`), each line naming every flip — the census is
> `test_iq7_satellites_have_a_position.py`; the front page's down arm (`test_sf_page_the_front_page_of_the_peace.py`
> `SEAMS_DOWN`) must hold every new behavioural seam down; Le Moniteur's lines stay generic where history is
> undocumented (§4.1 reading 4); `test_affairs_nondominance.py` fills a module-level set — run it with
> `--dist loadgroup`; a shell with `PYTHONDONTWRITEBYTECODE` set fails two bytecode pins the hook passes; count line
> endings with Python, never Git Bash `grep -c $'\r$'`; a `cd` inside a Bash call persists; the docs are CRLF or LF
> per file — edit through Python on bytes with the file's own ending and assert each replacement matches once; the
> shell heredoc eats `\r` and `\n` — write patch scripts with the Write tool; the deck JSON files are hand-formatted —
> insert text, never re-dump; the series rig's `prior` is HEAD's baseline (`git show`); attribute a series or reach
> move by event; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the background (the
> hook runs ruff and the full suite, about eleven minutes; never `--no-verify`) and read the log's EXIT line; a cp1252
> stdout kills a "→" print — run a probe under `python -X utf8`, never set `PYTHONIOENCODING` for pytest.
