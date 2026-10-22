# NEXT SESSION PROMPT — Pre-Deploy S14b part 3: the Acts, THE DECISIVE PEACE and the arms

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14b part 2 LANDED**
> (`docs/VP1_DESIGNS_SPEC.md` §13; commits through the hook — `git log -3`).
>
> **What the last session delivered:**
> - **S14b part 2 LANDED, in two landings** (`SYSTEMS_REFERENCE.md` §144–§145): every court opens with its regen purse
>   (VP1-X13); the shipped `europe_1805.json` carries the `imperial_designs` block (hints, Cabinet rows, aliases) so
>   the 1805 campaign boots armed; `proclaim_design` — a Cabinet button quoted first, free, then confirmed (1
>   administrative action, 2 diplomatic points, the teeth), its every refusal ONE predicate (`price_refusal`); the
>   road page (the Cabinet's step 4, GET `/imperial_designs`); the Balance block, `designs_clock`, the TODAY door, the
>   events (86 / 82 / 67) and the quiet morning's `realm_designs` line, Le Moniteur's specials, the goal answer led
>   by condition (c), Talleyrand's reading of a court, the manner and the Revanche on the four peace surfaces;
>   VP1-X4 … X8, X10, X13 … X19 FIXED — the census reads 0 open VP1 rows (9 open in all, every one S15's UXR-4).
> - **Measured:** `BASELINE_SERIES` byte-identical on every arm (the armed store read 396 times, never moved); six
>   commanded arms equal record for record; CMD-A and CMD-M part at one campaign-log line each (the prologue's one
>   log entry moves the 500-row roll) and equal the archive with it held down; FC's goal answer leads with (c).
>
> **Traps the last session paid for:**
> - **While a quote is pending, re-sending the same command resolves as its confirm** (the option's label
>   matches) — drive a quote-then-confirm through the quote's own option, never by sending the command twice.
> - **The event log rolls at 500 rows** (`MAX_EVENT_LOG_SIZE`): ONE new log entry on a 40-turn arm moves an IGR-B
>   collapse ("4 courts" → three named). Hold the entry's `_log` call down in a child run to attribute it.
> - **`headline_lead_memory` is REBUILT every morning from an allowlist** (`dispatch._select_headline`: "league",
>   "realm", "designs") — a new memory key that is not added there vanishes silently.
> - **The CX-R1 generator harvests only branches that assign `action = "<id>"` and call module-level
>   predicates**; regenerate `routed_order_words` after any new verb (`python -m tools.gen_routed_order_words`).
> - **The parser cassettes re-stamp keylessly** — a throwaway test that calls `tests.test_iq9_keyless_parser_gate`
>   and `tests._parser_replay.fingerprint`; the recovery cassette has its own prompt and its own re-stamp.
> - **A full run reads files mid-edit, and two pins need bytecode** — re-run a failure alone, with
>   `env -u PYTHONDONTWRITEBYTECODE`, before chasing it. The suite is ~32,630 tests, ~7.5 minutes at `-n 8`.
> - `tools/score_run.py run --only` takes ONE arm per flag (`--only CMD-A --only CMD-M`); a comma list runs nothing.
> - The Godot binary is `C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe`
>   (the folder of the same name is not the exe).
> - `CLAUDE.md` at ~61,900 of 62,000 bytes (LF-normalised).
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions and
> SF-NAV-1-D1 are theirs). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14b part 3 — VP-1 "The Emperor's Designs": the Acts of the Empire, THE DECISIVE PEACE and the arms — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -3` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/VP1_DESIGNS_SPEC.md` (§4 THE DECISIVE PEACE, §5 the Acts, §6 the surfaces, §7 the series, §8 the numbers, §9 Part 3, §12–§13 the landing records), `backend/game_logic/imperial_designs.py` (`decisive_peace_reading`, `decisive_peace_released`, `build_designs_payload`, `price_refusal` — the one-refusal idiom the Acts copy), `backend/game_logic/game_end.py` (`record_ending`, the causes, `_attach_endings`' lead order, the Verdict's score terms and tier lines), `godot-client/project-sovereign/scripts/campaign_end.gd` (`REGISTER_STYLE`, `_cause_line`), `backend/commands/reforms_executor.py` (the quote idiom), `tools/playtest_driver.py` (the dials) and `tools/playtest_scripts/` (the Tilsit road the CS script copies).

Scope (the record's §9 Part 3 — the design is the record's; flag any reversal):
0. **The user's rule (October 20, 2026): diplomacy is never typed.** The Acts are Cabinet rows on the road page whose commands are the executor's; every disabled reason is the act's one refusal predicate; no line tells the player to type one.
1. **The Acts of the Empire:** `decree_act {act}` — the full recipe (its own head "decree the …"; "enact the <act>" resolves to the act before the laws, corpus-pinned; not in `objection_actions` — a purchase); the four acts of §5 (the Temple of Glory, the Princes' Dotations, the Abolition of Feudalism, the Raft on the Niemen), each one-shot, gold + 1 administrative action, one refusal predicate and one price function (quoted net through `charges_relief`, shown = applied); the road page's Decree rows; the dispatch's `peace_sink` line names the next act once the laws are bought (`TestDDBR7` re-seated).
2. **THE DECISIVE PEACE:** release `decisive_peace_released()`; `CAUSE_DECISIVE_PEACE` stamped through `record_ending` (mark and continue); the fifth register in `campaign_end.gd` ("Continue the reign"), `_cause_line` naming the treaty, the summary block, the lead order (terminal, imperial_peace, decisive_peace, then the last stamped), the Verdict's +2 score term and tier lines (A2), the dispatch's `decisive_peace` class and Le Moniteur's "THE PEACE OF <TREATY>"; condition (c) marked met (ROADMAP's store-page row), A2, A4 and A6 written into their specs.
3. **The arms:** VP1-CS (`tools/playtest_scripts/sf_vp1_cs.json` copied from the Tilsit road, 40 loops, Road III proclaimed on turn 1 with the Cabinet button's command and the quote's option; the driver dial `--decline-until-latch <court>`, absent by default — every archived arm byte-identical, pinned); **VP1-RH carries the done-when** (the Rhine; the Tilsit road no longer latches the Blockade on any seed); VP1-TH beside it; each reported per seed with its reason.
4. **Measure:** `BASELINE_SERIES` byte-identical with every reach counted, or re-pinned naming VP-1 (S14b); the commanded arms attributed (`tools/_vp1_arm_attribution.py`).

Done when (§9 Part 3) the decisive peace records on at least one benchmark seed, every seed reported with its reason (seeded paths, not laws); the negative boards never stamp; the end card raises and the next end turn still reads `game_over` False; a staged turn-44 board with no negative term reads ascendant with the decisive peace and contested without it; each act charges exactly its quote and refuses the second time; the Godot parse harness EXIT 0 and the IQ-10 frames of the fifth register at 1.0 and 2.0; the series byte-identical or re-pinned with VP-1 named; condition (c) reads met; the census reads 0 open VP1 rows; the full suite green through the hook; STATUS ▶ NEXT UP names S14c and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with `BASELINE_SERIES` byte-identical or every movement attributed (count the reach); edit CRLF files with a script that preserves line endings; grep-verify any agent's bulk `.gd` edits. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
