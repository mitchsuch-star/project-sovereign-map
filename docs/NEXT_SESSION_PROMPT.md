# NEXT SESSION PROMPT — Pre-Deploy S14c part 2, second landing: three letters armed

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14c part 2's first landing**
> (`docs/EVENTS_SPEC.md` §13–§14; `SYSTEMS_REFERENCE.md` §147; commits through the hook — `git log -4`).
>
> **What the last session delivered:**
> - **Part 1 — the moments' engine, UNARMED** (`backend/game_logic/moments.py`, §13): the store, the four predicates,
>   the closed op table and its one `plan`, the tick (R1–R4), the court-less letter transport, the validator, the bands,
>   the backfill; the finds S14C-X18 … X20 (an ultimatum's Yield, an offered crown's Accept closed "a downgrade").
> - **Part 2's first landing — the client and the instruments** (§14): one lapse predicate for the lapse and the warning
>   (X1); the wizard lock RULED for a standing call (X2); one dismissal sparing a standing letter's row, the moment's row
>   opening its letter in one click (X14); the autonomy plan's gold and ports on every surface (X10); the popup's
>   `is_moment` register, the whole letter above the fold at 1.0 and 2.0; X11, X15, the finds X21 (a court-less letter
>   swallowed by the empty "Not Now" key) and X22; the sweep and the driver see a moment (`--moment`, X3). The census
>   reads 0 open S14C rows.
>
> **Traps the last session paid for:**
> - **Committing with `core.autocrlf` rewrites every touched file to CRLF in the working tree** — edit through a script
>   that keeps the file's own endings (the session's `eu.py` helper idiom: read bytes, normalize, write back).
> - **The Bash heredoc halves backslashes — every time.** Write scripts with the Write tool; scan for `\x08`.
> - **Never edit a backend file while a suite runs.** Draft in scratch; apply after.
> - **The driver's `Digest.campaign_log(events, turn)`** takes the events first; stub digests borrow public methods
>   (module-level constants only).
> - **IQ-10:** `tools/iq10_capture_payloads.py --only moments`, then `tools/iq10_run_captures.py --payload-dir <dir>
>   --only moment_letter --date <date>` (a windowed Godot parked at x=5200); the parse harness by `Start-Process`.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1, A1
> and the X2 ruling are theirs to overrule). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14c part 2, second landing — three letters armed — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -4` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/EVENTS_SPEC.md` (§2 the deck, §3.6 the hand-off and the matrix, §5 the bands, §7 the series and the arms, §9 Part 2, §13–§14 the landing records), `SYSTEMS_REFERENCE.md` §147, `backend/game_logic/moments.py`, `tests/fixtures/moments_block.json`, `tests/test_moments_engine.py`, `tools/_s14c_series_arms.py`, `tools/_vp1_arm_attribution.py`, `tools/ai_v_sweep.py`.

Scope (the record's §9 Part 2, second landing — the design is the record's; flag any reversal):
0. **The rules:** every answer is a button whose command is the executor's; the LLM never affects mechanics; ints only to Godot; no module lever; no per-region scan in a hot path.
1. **The suite-reach head, FIRST:** arm the block (M1, M2, M4) on a scratch tree, run the full suite, list every test that reads the dialogue queue, the mailbox counts, `lapsed_offers`, the `offer_lapsed` rows or the Gazette past turn 17; re-seat each consciously or keep it dormant by a conftest pin (the `SOVEREIGN_SCENARIO=none` idiom), the choice recorded.
2. **Ship the block:** `europe_1805.json` gains `moments` with M1, M2, M4 (pinned equal to the fixture's entries; M3 waits for part 3); the validator passes it; the backfill arms a pre-S14c save (the T10 / T20 fixtures: `passed(before_save)` where the window closed).
3. **The matrix cells:** M1, M2 road-agnostic, M4 with no road and on Road III, silent on I and II — pinned now.
4. **Measure:** `tools/_s14c_series_arms.py` extended (MW the window resolver, ML the lapse default, MK the queue residence, MN the notice and log rows, MH the wizard exclusion, MR the crowd-out receipt) with each reach counted; `BASELINE_SERIES` byte-identical or re-pinned as `SERIES_BEFORE_S14C` naming this row; the nine commanded arms attributed (`tools/_vp1_arm_attribution.py --baseline` against the first landing's run); each letter's reach per seed reported.

Done when (§9 Part 2): each letter arrives on a staged board at its resolved turn (M2 also on the `historical` passive board where Holland's loyalty dips) and is `passed(premise)` where its premise fails; each answer applies exactly its quote through `/respond_to_diplomatic_dialogue`; the Holland closure line equals `closed_ports_against` after the op; the Decree arrives only where `decree_clients` would be non-empty; a standing letter's notice survives an unrelated lapse; the series byte-identical or re-pinned naming S14c; the full suite green through the hook; STATUS ▶ NEXT UP names part 3 and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with every movement attributed (count the reach); grep-verify any agent's bulk `.gd` edits. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
