# NEXT SESSION PROMPT — Row AU "Authority as a currency": AU-2c's arming, then AU-3a the three buys (the fifth of seven slices, before S15)

> Overwritten each time a session hands off. Current hand-over: **November 4, 2026 — AU-2c the Bank and the Pope ✅ LANDED, HELD OUT until the user's word arms them**
> (`docs/AUTHORITY_CURRENCY_SPEC.md` §6.4 the landing record; the rules `SYSTEMS_REFERENCE.md` §172; AU-1 the books ✅ `6b9d61c4`
> §6.1; AU-2a the hits ✅ `ebf2e393` §6.2 and the clamp ✅ `33d4ac72` §6.2.5; AU-2b the lumps and the Show ✅ `ca6dec23` §6.3 —
> its seven readings CONFIRMED by the user's "Keep it, start AU-2c", the Bulletin kept after a replay of its two trims). Two
> affairs letters priced in authority alone, authored `since: "AU-2c"` and held WHOLE out of the deck while
> `standing.letters_armed()` reads False (`affairs.entry_armed` in `moments.affairs_deck`): **the Bank's Panic**
> (`affairs._chest_strained`, LATCHED — the premise at war with the purse able to pay 1,000 + the reserve, the latch bit the
> ledger's forecast Net emptying the chest within 20 turns, 4 of the last 12 mornings; the Regents of the Bank of France write;
> "Pay the Bank in coin" −1,000 gold · 1 action, or "Let the notes fall" −4) and **the Pope's Refusal** (`affairs._ports_defied`
> — at war with Britain twelve mornings, the Papal States active, not France's client, not at war with her, outside the System;
> Caprara writes; "Occupy the ports" −800 gold · 1 action · the Papal States −10, or "Let the Pope refuse" −5) — the user's two
> answers at the head (the war with Britain, the Decree never in force on a measured run; −10 with the Papal court, which
> exists — AU-11). Measured ARMED on 55 runs (`tools/_affairs_au2c_letters.json`): the Bank arrives 5 times on 4 runs (the
> scripted boards where the war outruns the chest; all five lapsed to the Decline) — its first definition, the deficit as the
> premise itself, never arrived (`tools/_affairs_au2c_letters_first.json`: a blinking premise loses every pulse) and was
> re-latched; the Pope 13 times on 13 runs (12 lapsed, 1 accepted; first due T13–T15, never on the commanded arms, whose peace
> with Britain comes first); the pulse is one stream — the others lost 13 arrivals (the Marine 5, the Chancellor 3, the
> Memorial 2, the Remounts 2, the Magazines 1; the Memorial gained 1). The shipped records reproduce AU-2b's; `BASELINE_SERIES` byte-identical on nine arms (AUL+, both
> letters up, among them). AU-10 (a court's possessive mid-quote) and AU-11 fixed.
>
> **FIRST — the user's word on the arming** (§6.4.4 reading 1, with the six readings beside it — the Bank's latch and horizon
> first). On "arm": `standing.letters_armed` → True (one line) in its own commit through the hook, with: the shipped chain
> re-run (copy `tools/playtest_runs/au2c_2026_11_04/chain.sh`; with the seam up by default the shipped records ARE the armed
> ones), the reach pins re-pinned by event (`tests/test_affairs_reach.py` `HELD_OUT` → the two letters' measured verdicts; the
> per-template reach; the first-arrival record), `BASELINE_SERIES` measured on every arm (AUL+ was byte-identical), the front
> page's down arm (`tests/test_sf_page_the_front_page_of_the_peace.py` `SEAMS_DOWN` gains `standing:letters_armed=False` if
> CMD-H's page moves), `tests/test_affairs_bank_and_pope.py::TestTheSeamHoldsThemOut` flipped consciously, the spec, STATUS,
> CLAUDE.md. A reading reversed: change its one number, re-run `chain_armed.sh` and re-compose the review record
> (`tools/_affairs_au2c_letters.py`) before arming.
>
> **THEN — AU-3a the three buys** (§5.3's first four rows, the §6 AU-3a row, §4.1's readings on the Word; about 1.9 sessions;
> Plan Mode first; one commit through the hook, then the user's review): **"Decree it"** — a third answer on the three Edict
> letters, the Edict block taking the laws' `currency` key (5 / 3 / 4 standing and the same administrative action; the
> payload, the verdict, the three validator loops, the popup's Counter node as the third slot, the driver's answerer, the trace
> wrapper, the Correspondence slips; the courts' rung `find_ai_edict` at the floors); **"By my word"** — the fifth objection
> answer on both paths (2 / 3 / 4 / 5 by trust tier, no trust cost, no defiance roll; a commanded battle lost within three turns
> −5 trust / −3 standing, never the +5: the executors' early branch, the floor gate, the four stamp sites, the typed words, a
> code-built button, the vindication's `word` branch); **"Honour him" / "By decree"** on the marshals' cards (4 and 5: the
> option lists, the apply branches, the affordability gate — the honour writes `held["honoured:<marshal>"]` so AU-2b's
> `standing.honour_repaid` pays back +2); the recency rise (+1 per push of §5.3 in the last six turns, at most +3); every price
> refused under 60 with its reason (`standing.refusal`). The nondominance pin extended to three answers; the dialog-text pins
> (`test_v2b_session1.py`, `test_severity_modifiers.py`, `test_disobedience.py`); the frames at both scales; the series unmoved
> (the passive runner answers nothing). Then the records and the user's review; AU-3b and AU-4 follow.
>
> **Traps the row has paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are named
> functions), functions over 500 lines 28 of 28, `WorldState.to_dict` 497 of 500 (every new field in the tracker's `held`),
> CLAUDE.md within 62,000 LF bytes (pay a row by a trim); every `except Exception` must speak (`backend.errors.report`); the
> pulse takes the matter whose premise has stood LONGEST (`affairs.pick`) — a premise that blinks for a morning resets its
> streak and loses every pulse to matters holding from the first mornings: latch the blinking part (the Haiti idiom,
> `LATCHED_PREDICATES`); a whole template held out is an entry's `since` (`affairs.entry_armed`), its seam DOWN by default
> measured up by the rig's `UP_ARMS` and, in the sweep's and the probe's children, by `INK_IRON_SEAMS` (`tools/_seams_env.py`;
> the driver keeps `--seam`); NEVER edit backend code or the deck while a measure chain runs (its later phases spawn on the new
> tree) — and a TaskStop on the wrapper leaves the inner `bash chain.sh` running (it rewrote the committed records from partial
> data once): check the processes, then re-run; `tools/playtest_runs/` is gitignored — a record worth keeping goes under
> `tools/`; a deck op or clause a slice adds carries `since` / `bites_since` naming its row; the validator counts a
> `button_line`'s slots at four and caps it at 40; a dispatch event's payload sits under `template_vars`; a `moment_receipt`
> lands in `diplomatic_events`; `_affairs_measure.py --driver-flags` must be passed as `--driver-flags="--standing-trace"`;
> THREE dated decks are locked equal (the scenario, `tests/fixtures/moments_block.json`, the affairs fixture's copy) and the
> affairs deck is the fixture's verbatim; a new campaign-log type moves FOURTEEN count pins — the census is
> `test_iq7_satellites_have_a_position.py`; the front page's down arm must hold every behavioural seam that moves it;
> `test_affairs_nondominance.py` fills a module-level set — run it with `--dist loadgroup`; a shell with
> `PYTHONDONTWRITEBYTECODE` set fails two bytecode pins the hook passes; the docs are CRLF or LF per file — edit through Python
> on bytes and assert each replacement matches once; write patch scripts with the Write tool (the heredoc eats `\r` and `\n`);
> the deck JSON files are hand-formatted — insert text, never re-dump; the series rig's `prior` is HEAD's baseline; attribute a
> series or reach move by event; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the background
> (the hook runs ruff and the full suite, about eleven minutes; never `--no-verify`) and read the log's EXIT line; a cp1252
> stdout kills a "→" print — run a probe under `python -X utf8`; read a spec's claim about the map against the boot (the
> standing trace's `courts` named the Papal States the spec said did not exist).
