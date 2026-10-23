# NEXT SESSION PROMPT — Pre-Deploy S14d part 2: the Table (the lesson); then part 3

> Overwritten each time a session hands off. Current hand-over: **October 23, 2026, after S14d part 1's second
> landing and part 1b LANDED — part 1 COMPLETE** (`docs/TABLE_LESSON_SPEC.md` §13–§14; `SYSTEMS_REFERENCE.md` §148,
> §148.8; commits through the hook — `git log -5`).
>
> **What the last session delivered:** the nine IQ-10 frames with the first-open line at the head and the first answer
> above the fold at 1.0 and 2.0, pinned on the record (`tests/test_sf_rr5_the_frames.py`, the S14D classes), and the
> three finds the frames made — the table's line moved to the footer (the head is one line at 2.0), `/pending_envoy`
> and `/mailbox/activate` wired (S14D-X48), the `muster_confirm` interrupt's answers kept on the screen (S14D-X47, a
> scrolling message); the class sweep (the Formable Nations page lined as the eighth id `formables`; the Congress row,
> the capture modal, the commission chooser and the call-to-arms letter ruled covered; the lapsed call's price restored,
> S14D-X45); the fifteen copy rows; and part 1b's engine rows (the counsel's table roads at 0 DP, the flip's value the
> term's own, the PEACE vassal row, the refusal stamp following the feedback's ranking with two new reasons, the envoy
> walking the purse stamped at send, and a counter the chest cannot pay refused aloud — S14D-X46). 56 pins in
> `tests/test_first_open.py`; the series byte-identical; the census 23 open rows (14 S14D homed to parts 2 and 3).
>
> **Traps the last session paid for:**
> - **The Bash heredoc halves backslashes** — an edit script with `\n` in a replacement writes a RAW newline and
>   reports success; write every script as a file (the Write tool) and run it by path.
> - **The frame record reads a plain Label only when its WHOLE rect stands inside the window** — a message that scrolls
>   must be a RichTextLabel (BBCode off is as literal as a Label) or it reads as unseen.
> - **The settlement popup's head region is ONE line at Interface Scale 2.0** (the EA-E6 fit's floor) and that line is
>   the verdict; nothing else at the head of the table is seen at 2.0.
> - **`tools/iq10_capture_payloads.py --only` takes the groups as SEPARATE arguments**, not comma-joined; a capture
>   into an `--out` dir rewrites its manifest, so re-capture one group into its own dir.
> - **`_button(frame, prefix)` matches by prefix** — "Proclaim Road I" matches "Proclaim Road III"; name the dash.
> - **A pytest-xdist run holds the test files open** — an edit during the run can fail with `Errno 22`; wait it out.
> - **The muster counts the corps likely to arrive** — an outmatched board needs the enemy heavier than the whole
>   French concentration, not one corps.
> - **`core.autocrlf` is per file** (the scratchpad's `edit.py` detects and keeps each file's ending; the JSON spec
>   aborts WHOLE on a missed anchor — nothing is written, re-check every entry). **`git add` exits 1 on
>   `europe_1805.json`.** The ratchet counts CLAUDE.md LF-normalized (62,000 cap; 34 bytes of headroom).
>
> **Nothing waits on the user before S15** (S14d's A1 and the re-size, S14c's A1 and the X2 ruling, UXR-4, the
> code-signing certificate, AO's three questions, SF-NAV-1-D1 are theirs to overrule). Paste everything below the line
> as the opening message of a fresh session.

---

Pre-Deploy S14d part 2 — the Table (the lesson) — then part 3, on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/TABLE_LESSON_SPEC.md` §4 (the board §4.1, the cards §4.2, the frame §4.4), §5 (the authoring contract, A4), §6 (the instruments of part 2), §9 (parts 2 and 3), §14.6 (the traps); `SYSTEMS_REFERENCE.md` §148; `BUG_FIXES.md` §S14D (the 14 open rows: X13–X17, X19–X22, X40, X41 are part 2's; X18, X42, X43 part 3's); `godot-client/project-sovereign/scripts/tutorial_overlay.gd` (the Danube's `const STEPS`, `on_world_swap`, the predicates) and `tutorial_state.py`; `tests/test_tutorial_unbreakable_2026_09_23.py` (the recorder + harness); `docs/PLAYTESTING.md` (Mode A, Mode C).

Scope:
1. **The registry refactor, FIRST and committed alone:** `LESSONS` keyed by `scenario_name` in the overlay, `on_world_swap` picking by name and `_reset_lesson_state()` clearing every latch (S14D-X20), `UiSettings.get_tutorial_done(lesson := "tutorial")`, `main.gd._on_tutorial_boot_requested(scenario := "tutorial")`, `tutorial_state.SCHOOL_SCENARIOS` with `main.SCENARIO_ALLOWLIST` derived from it, `is_school_world(world)` consumed by `jealousy_dormant`, `dotation`'s carve-out, `petitions_live` and `_autosave` (S14D-X16's doc row corrected), the per-lesson released-step notes (S14D-X19), the unused predicate and the stale counts (X21, X22) — the Danube BYTE-IDENTICAL: every lesson pin green, `_shipped_steps`, T-B1, the mirror drift pin, `test_fa_slice8` with no flips.
2. **The board** `godot-client/project-sovereign/assets/maps/tutorial_table_1805.json`, tuned by instrument: commit `tools/_table_board_probe.py` (from the gate's sweeps) and author §4.1's table — one France-led war on Austria and Russia with explicit Bavaria → Austria and KingdomOfItaly → Austria entries; Vienna, the Tyrol and Moravia French with `nation_starting_regions` authored; the record's wins on `decisive_battles`/`battle_records`; `campaign_ledgers` with France's losses at 3,000; `war_exhaustion {"Austria": 60}`; `war_start_turns` past the window; Russia small and far east; Bavaria ALLIANCE at relation 65; `proposal_cooldowns` for every court off the lesson; the five engine hints pre-set; `first_opens: {}`; `start_date 1805-12-04`; France's five laws copied from the Danube and pinned equal. The arithmetic pins (`tests/test_tutorial_table_scenario.py`): Austria ≥ 50 with the 3-point margin and ACCEPT, Russia < 50, the chip available, Bavaria's suggested vassalage COUNTER then ACCEPT after one "More generous", no stray letter in the first three mornings, no battle in the first three enemy phases; S14D-X13 (the counter names the struck tribute), X14 (the keys' contract in `MODDING_FORMAT.md` + the validator's shape checks, A4), X15 (the release pin names every school scenario), X17 (TUTORIAL_SCRIPT's typed row → the Cabinet door, A3), X40 (the Danube's three comments), X41 (the cards name offices, never a man's office he did not hold).
3. **The cards** `scripts/tutorial_table_steps.gd` (§4.2, seven over three turns, Berthier's voice, every step a button or a door chip): the new door kind `open:settlement:war_1:Austria` (`main.gd` → `_on_war_settlement_clicked(war_id, nation)`), the predicates on response fields only; the driven pins (`tests/test_tutorial_table_driven.py`: the committed script `tools/playtest_scripts/tutorial_table_lesson.json` sees all seven cards in order through the real overlay and reaches the hand-off with zero skips; the refused act and the skip release; the mirror never ahead of the turn; `TestTheRearm`); the menu row "The School of War — The Table (a guided peace)"; the lesson's IQ-10 frames and the menu's seventh button re-shot with `must_show` at both scales.
4. **Then part 3:** the Mode C walk of both lessons and the campaign's eight lines on BEGIN (`SOVEREIGN_PORT=8007`, `tools/dd_b_play.py`; `tutorial_screenshot.gd`'s 8005 refusal, X18); the release build's fourth file; `TUTORIAL_SCRIPT.md` §The Table Lesson, `MODDING_FORMAT.md`, `SAVE_FORMAT_REFERENCE.md`, `DESIGN_REFINEMENT.md` (A2), `ROADMAP.md`, `PRE_DEPLOY_PLAN.md`'s row and total (A1); X42 (verify Verhuell before any edit), X43; the census 0 open S14D.

Done when: the registry lands with the Danube byte-identical; the arithmetic pins hold on the authored board; the committed script plays all seven cards through the real overlay; every school scenario is dormant and autosave-skipped; the series untouched; the full suite green through the hook; STATUS ▶ NEXT UP names part 3 (or S14e once part 3 lands) and this file is overwritten for it.

Rules: the registry refactor is committed before any Table content; reproduce each row on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); "diplomacy is never typed" (every lesson step a button or a door); Berthier keeps the school, the Cabinet's own lines are Talleyrand's; a card never dresses a game step as history; a line's fact the board does not deliver changes the line, never the board; grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process (`tools/godot_parse_check.gd`, expect EXIT=0, commit the refreshed report). Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
