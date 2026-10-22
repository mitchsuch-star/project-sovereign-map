# NEXT SESSION PROMPT — Pre-Deploy S14c part 2: the client, the instruments, and three letters armed

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14c part 1 LANDED**
> (`docs/EVENTS_SPEC.md` §13; `SYSTEMS_REFERENCE.md` §147; commits through the hook — `git log -4`).
>
> **What the last session delivered:**
> - **S14c part 1 — the moments' engine and its transport, UNARMED** (`backend/game_logic/moments.py`): the store
>   `world.moments`, the four predicates, the closed op table with one `plan` (shown = applied), the tick (R1 the
>   foreground, R2 the crowd-out receipt, R3 one a morning, `max_open`, `min_gap`), the validator, the variance branch,
>   the serialization and the backfill, the ten transport seams at their backend halves — pinned on the staged deck
>   `tests/fixtures/moments_block.json` (88 pins, `tests/test_moments_engine.py`). The shipped boot authors no block.
> - **The head reproduced:** §1 on ten seeds (Bavaria warm in T8–12 on 0 of 10, Holland slips in T17–21 on 7 of 10, the
>   Decree bites on 0 of 10, a settlement offer stands as the current letter from T9–11 to T35 on every seed).
> - **The siblings:** S14C-X4, X6, X7, X8, X9, X13, X16, X17 FIXED, and the finds **X18–X20** (reproducing X8 found its
>   second half LIVE: every AI ultimatum's Yield and every offered crown's Accept from a court at peace was closed as
>   "a downgrade" on the first read) — fixed by one registry, `treaty.NON_TREATY_LETTERS`. X10, X14, X15 landed their
>   backend halves and stay OPEN for part 2 with X1, X2, X3, X11.
>
> **Traps the last session paid for:**
> - **Never edit a backend file while a full suite runs** (the workers import lazily) — draft doc and code edits into
>   scratch files and apply them after the run.
> - **The Bash heredoc halves backslashes** (it bit again: a `\\` line-continuation broke an edit script) — write
>   scripts with the Write tool. **CRLF files** in this area: `treaty.py`, `dialogue_manager.py`, `turn_manager.py`,
>   `gazette.py`, `notifications.py`, `envoy_digest.py`, `tools/ai_v_sweep.py`, `docs/MODDING_FORMAT.md`, `CLAUDE.md` —
>   byte-level scripts that keep `\r\n`.
> - **The dismissal sites are 18, not 2** (S14C-X14): the lapse hook and 17 in the executors call
>   `dismiss_by_type(DIPLOMATIC_PROPOSAL)` unfiltered; route them through one helper that spares a still-open letter.
> - **A moment letter rides behind a standing settlement offer on every seed** — the rail notice's button must open it
>   in one click (a new `review_target` with the mailbox id; `main.gd _on_notification_review_requested`).
> - **Every new `add_threat` source needs a `_THREAT_SOURCE_LABELS` row** — the X4 census walks every call by AST.
> - **The code-health ratchet is at every cap** (levers 231, functions over 500 lines 28 with `WorldState.to_dict` at
>   exactly 500, silent handlers 6, `CLAUDE.md` near 62,000 bytes); `TurnManager.end_turn` has 15 lines of headroom and
>   `filter_campaign_log` one.
> - The full suite is ~22,200 + tests, ~6 minutes at `-n 8`; commit with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING`.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1 and
> A1 — the gate's reduction of the row — are theirs to overrule). Paste everything below the line as the opening
> message of a fresh session.

---

Pre-Deploy S14c part 2 — the client, the instruments, and three letters armed (two landings) — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -4` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/EVENTS_SPEC.md` (§2 the deck, §3.4 the ten seams, §6 the surfaces and the client, §7 the series and the arms, §9 Part 2, §10 the siblings, §13 part 1's landing record), `SYSTEMS_REFERENCE.md` §147, `docs/BUG_FIXES.md` §S14C, `backend/game_logic/moments.py`, `tests/test_moments_engine.py`, `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd` (the `is_petition` / `is_call_to_arms` registers), `mailbox_panel.gd`, `main.gd` (`_on_mailbox_activate_result`, the LAPSED ENVOYS block, `_on_notification_review_requested`), `dispatch_view.gd`, `tools/playtest_driver.py`, `tools/ai_v_sweep.py`, `tools/iq10_capture_payloads.py`, `tools/_s14c_series_arms.py`.

Scope (the record's §9 Part 2 — the design is the record's; flag any reversal):
0. **The rules:** every answer is a button whose command is the executor's; the LLM never affects mechanics; ints only to Godot; no module lever; serialization for any new field.
1. **First landing — the client and the instruments:** reproduce each first — S14C-X1 (`get_lapsing_count(current_turn)`, `keeps_open`-aware for the call to arms and the moment, its five `main.py` callers), X2 (read DDB-2's ruling before building a `blocks_wizard` predicate), X3 (the sweep's `RunCapture`, `BEAT_TYPES`, the driver's `AI_AI_LOG_TYPES`, `--moment accept|decline` answering by intent), X10 (the wizard row reads `vassal.autonomy_change_plan`; the closure derived), X11 (`_on_mailbox_activate_result`'s else branch), X14 (the 18 sites through one helper; the notice's one-click route), X15 (both Godot lapse renderers print a carried line; the census over the six readers of `lapse["nation"]`). The `is_moment` register in `incoming_proposal_popup.gd` (the header "A MOMENT OF HISTORY — {label}", the record, the board, "What each answer does", the unanswered line, Counter hidden, captions from the payload), the mailbox label, IQ-10 frames (`cap_moment()` — the Match and the Decree at Interface Scale 1.0 and 2.0, both answers above the fold), the parse harness covering the popup.
2. **Second landing — three letters armed:** the shipped block with M1, M2, M4 (pinned equal to the fixture's entries); the M1 / M2 / M4 matrix cells; the suite-reach head (arm the block on a scratch tree, run the suite, list every test that reads the dialogue queue, the mailbox counts, `lapsed_offers`, the `offer_lapsed` rows or the Gazette past turn 17 — re-seat consciously or keep dormant, the choice recorded); `tools/_s14c_series_arms.py` extended (MW, ML, MK, MN, MH, MR) and the archived arms attributed; re-pin as `SERIES_BEFORE_S14C` if any arm bites.

Done when (§9 Part 2): each letter arrives on a staged board at its resolved turn (M2 also on the `historical` passive board where Holland's loyalty dips) and is `passed(premise)` where its premise fails; each answer applies exactly its quote through `/respond_to_diplomatic_dialogue`; the Holland closure line equals `closed_ports_against` after the op (at war with Britain: unchanged, said so); the Decree arrives only where `decree_clients` would be non-empty, its line `terms_line` plus the admin clause and the real closure delta; every lapse surface prints a whole sentence; a standing letter's notice survives an unrelated lapse; the `iter_queue` census green; frames at 1.0 and 2.0 show both answers above the fold; the parse harness exits 0; the series byte-identical or re-pinned naming S14c; S14C-X1, X2, X3, X10, X11, X14, X15 FIXED with their pins; the full suite green through the hook; STATUS ▶ NEXT UP names part 3 and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with `BASELINE_SERIES` byte-identical or every movement attributed (count the reach); grep-verify any agent's bulk `.gd` edits. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
