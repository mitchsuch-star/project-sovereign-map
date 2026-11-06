# NEXT SESSION PROMPT — Row AU "Authority as a currency": the courts' flip on the user's word, then the row closes (before S15)

> Overwritten each time a session hands off. Current hand-over: **November 5, 2026 — AU-4 the courts' flip, part 1 ✅ LANDED**
> (`docs/AUTHORITY_CURRENCY_SPEC.md` §6.7 the landing record; the rules `SYSTEMS_REFERENCE.md` §175; AU-1 ✅ `6b9d61c4` §6.1;
> AU-2a ✅ `ebf2e393` and the clamp `33d4ac72` §6.2; AU-2b ✅ `ca6dec23` §6.3; AU-2c ✅ `a9e40e4b`, armed `7d34b5f6` §6.4;
> AU-3a ✅ `3567af83` §6.5; AU-3b ✅ `f7b5abe2`, re-premised `0e508aac`, armed `884cddc4` §6.6; AU-4 part 1 the commit after).
> **AU-19 at its head** (the user's "Fix at AU-4's head"): a capital is lost only by its defender, when it falls
> (`standing.capital_lost_by`) — the player had been booked "the capital at Milan, lost" for every battle lost at its
> satellites' capitals, 248 bookings on the 59 measured rows; the shipped records re-measured (the player's mean end
> 60.1 → 68.9, the Haiti letter 18 → 28 arrivals) and `BASELINE_SERIES` re-pinned at [22] with RE-6's series kept as
> `SERIES_BEFORE_AU` (the rig's arm 0 and AUF reproduce it); the front page held by AUF. **Built and PARKED behind
> `standing.courts_move()`:** the courts' field, garrison and charge writes (`standing.courts_battle`, `courts_garrison` —
> the player's own rules, AI against AI included), a court's Bulletin (+4, no repayment), the courts' cooldowns in the
> tracker's `held`, a court's Proclamation on its own eve of battle (none on the 1805 board), AU-4's one reader, the grip's
> seam (`standing.court_grip_reads_books`, AU-5), the Nations row. **Measured up** (`tools/_standing_courts_au4.json`):
> the courts book 469 Bulletins, 374 fields lost, 283 assaults repulsed, 188 capitals stormed; Britain ends at 40 on
> average (31 parked), Prussia 37; the player's end moves on 41 runs (mean 68.9 → 72.8); `BASELINE_SERIES` moves at [10];
> the grip reading their books changes little (no court fields a sovereign). **Open with the user:** the flip (§6.7.4) and
> AU-4's seven readings (§6.7.3).
>
> **NOW — the user's word on the flip** (§6.7.4): **"Flip, flat grip"** or **"Flip, grip reads books"** →
> `standing.courts_move()` → True (and `standing.court_grip_reads_books()` → True for the second) in its own commit with
> its re-measure: the shipped chain copied (`tools/playtest_runs/au4_2026_11_05/chain.sh`'s `measure` on the shipped
> phase), the reach / standing / probe records reproducing the review's courts-up records
> (`tools/playtest_runs/au4_2026_11_05/courts_{flat,grip}/`) WHOLE; `BASELINE_SERIES` re-pinned at [10] with this series
> kept (`SERIES_BEFORE_THE_COURTS`) and the attribution by event (`tools/_rf3_board_events.py`, or the in-process
> HEAD-pipeline idiom of `tools/playtest_runs/au4_2026_11_05/` — the courts' moves at turns 9–10); the rig's AUC+ arms
> retired (ALL is that arm; `UP_ARMS` empty); the courts' pins flipped consciously
> (`tests/test_standing_buys.py::TestDecreeIt::test_the_courts_decree_is_parked_with_the_courts_flip`,
> `tests/test_standing_books.py`'s court regrowth, `tests/test_standing_courts.py`'s parked pins); the front page measured
> with the courts up (a `SEAMS_DOWN` entry for AUC if it moves); AU-5 decided with its test; then **the row closes** (§10)
> and S15 is next (RE3-6 and RE3-7 at its head by the user's word; RE3-9 the same — NEVER act on them before). Plan Mode
> first; one commit; the user's review.
>
> **Traps the row has paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are named
> functions), functions over 500 lines 28 of 28, `WorldState.to_dict` 497 of 500 (every new field in the tracker's `held`),
> CLAUDE.md within 62,000 LF bytes (28 bytes of headroom: pay a row by a trim); every `except Exception` must speak; a new
> card option goes LAST (the driver picks the first enabled); a reused node keeps its scene position; a letter's answers are
> planned at every read — read them through `moments.refresh_letter`; the courts boot at 60, so `ai_refusal`'s floors pass —
> anything a court may buy in authority moves the series (AU-14); the pulse takes the matter whose premise has stood LONGEST —
> a premise shared with an older letter (the Proclamation's afield with the Chancellor's) loses the morning, and a premise of
> the war itself (the re-premised Proclamation's) out-stands nearly every letter — it leads the deck whenever its latch holds; an
> arming's re-measure copies the shipped chain and must reproduce the review's armed records WHOLE (reach rows, the
> standing rows, the probe's seeds) — compare whole rows, not one key; a letter whose Accept is priced in authority alone
> books a purchase (`edict_decreed`) wherever an accept dial answers it — the band pin names those rows; a rule inside a
> big function (the battle step) is made a named function so a replay can hold the old rule down by a lambda (AU-19's
> `capital_lost_by`, the front page's `SEAMS_DOWN`); `get_visible_enemies` reads the PLAYER's fog — a court's sight is
> `get_live_visible_enemies`; the 1805 board fields one sovereign, Napoleon; a whole template
> held out is an entry's `since` (`affairs.entry_armed`), measured up by the rig's `UP_ARMS` and, in the sweep's and the
> probe's children, by `INK_IRON_SEAMS` (`tools/_seams_env.py`); `tools/_affairs_au2c_letters.py --letters` writes any held-out
> letter's review record; NEVER edit backend code or the deck while a measure chain runs, and run a chain ALONE (a background
> test finishing beside one froze every driver on November 5); `tools/playtest_runs/` is gitignored; Godot: one engine per
> machine; `--log-file` and every capture path ABSOLUTE (a relative one dies at start, 0xC0000005); the frames harness's
> `scroll_to` reads a label's paragraph within the label — pass `in_content: true` for a label among many (the road page);
> the validator counts a `button_line`'s slots at four and caps it at 40; the affairs deck is the fixture's verbatim and the
> Acts' block is `tests/fixtures/vp1_imperial_designs_block.json`'s; `test_affairs_nondominance.py` fills a module-level set
> — run it with `--dist loadgroup`; the docs are CRLF or LF per file — edit through Python on bytes, asserting each
> replacement matches once; write patch scripts with the Write tool (the heredoc eats backslashes); the deck JSON files are
> hand-formatted — insert text, never re-dump; attribute a series or reach move by event; commit with `env -u
> PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the background (the hook runs ruff and the full suite, about ten
> minutes; never `--no-verify`) and read the log's EXIT line; run a probe under `python -X utf8`.
