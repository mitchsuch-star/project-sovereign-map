# NEXT SESSION PROMPT — the Score Finish residue: SF-RR1 (ii)'s re-read, then SF-RR2 "the desk answers what was asked"

> Overwritten each time a session hands off. Current hand-over: **October 20, 2026, after S14 part 4 (SF-RR7 "the
> morning of the peace") landed — SFR-B3, PC-X69 and DDB-X4 FIXED; S14's head is COMPLETE** (commits through the hook —
> `git log -2`).
>
> **What part 4 delivered** (`SYSTEMS_REFERENCE.md` §136; rows `BUG_FIXES.md` SFR-B3, §PC PC-X69, §DD-B DDB-X4 and the
> siblings §RR7 RR7-X1 … X9, all FIXED; pins `tests/test_vp2_the_imperial_peaces_morning.py`):
> - **The hold** (`congress.league_waits_on_paris`, read once by `coalition.process_coalition_turn`): while the Congress
>   sits and fewer than two great powers refuse it, no new league declares against France — a brew holds at its last turn
>   and the instant bar brews instead; the two-refuser gate untouched; a failed Congress lets it declare the next end turn
>   (`congress.hold_lifts_in`).
> - **The signing** (`congress.the_signing_spends`, from `_proclaim` on the Congress's route): the alarm to the Armed
>   Peace's watch (45, never raised), any brew dismissed; **the page** (`congress.bought_line`) on the end screen, the
>   dispatch and the desk. The PRESS arm's morning: no league, the alarm 45.
> - **PC-X69, ruled:** a bonded great power's Congress suit is her priced separate peace — `congress.sue_line` reads the
>   bond's depth, every surface tells it (`bond.letter_line` on any peace letter), the renege stands.
> - **DDB-X4:** `tools/_ge3_series_arms.py` holds fourteen live seams down; six arms re-read `BASELINE_SERIES` byte for byte.
>
> **Traps part 4 paid for:**
> - Write every edit script with the Write tool (the bash heredoc mangles backslashes: a `.gd` edit with `\n` in its
>   strings failed its match from a heredoc) and run it with the venv Python; edit by exact substring with a count assert.
> - `tests/test_congress_of_paris.py`'s helpers (`_boot`, `_sit`, `_satisfy_all`, `_latch`, `_tick`) stage a sitting on
>   the boot board in a second; `_tick` runs only the Congress's own tick — drive `coalition.process_coalition_turn` beside
>   it for anything the coalition does.
> - The PRESS arm drives in ~5 s (`tools/playtest_driver.py --script tools/playtest_scripts/ge3_pressburg.json
>   --from-save tests/fixtures/playtest_saves/fixture_ge3_pressburg.json --diplomacy accept --stop-on-ending --turns 12`);
>   `--seam MODULE:NAME=EXPR` holds a rule down for the sensitivity arm.
> - `CLAUDE.md` stands at 61,952 bytes (cap 62,000): swap its live-state rows, shorten as you swap.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

The Score Finish residue, its first session — SF-RR1 (ii)'s done-when re-read, then SF-RR2 "the desk answers what was asked" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/PRE_DEPLOY_PLAN.md` §2 S14, `docs/SCORE_FINISH_SPEC.md` §3 Step 9 (the SF-RR1 … RR6 table — each slice's rows, done-when and test), `docs/BUG_FIXES.md` §Score Finish Step 8 (the SFR rows; `tools/defect_census.py --open` lists the open ones), `docs/audits/SCORE_FINAL_2026_10_05.md` (the reading that filed them) and `docs/PLAYTESTING.md` (Mode A; the HOLD arm is `tools/score_run.py`'s, two turns of a blind script).

Scope — the design is the spec's; rule the details at the head, measured, and flag any reversal:
0. **The user's rule (October 20, 2026): diplomacy is never typed.** Anything new the player does is a Cabinet row or a row's `choices`; the desk ANSWERS typed questions (that is its job), but no answer teaches a typed diplomatic order.
1. **SF-RR1 part (ii):** every row it owned is already FIXED (DD-0 S4, October 10, 2026; CR-7-3; CRT-11 / CQ-8). Re-read its done-when on today's tree: the HOLD arm, command C3 ≥ 15 of 20 with no misread (`tests/test_sf_rr1_the_orders_the_reading_met.py`). Met → close the slice in the spec with the reading; not met → file each miss by the reading's rule (reproduced, with its trace) and fix it in this session or head the next.
2. **SF-RR2 "the desk answers what was asked":** SFR-H4, H8 … H12, H14, D2, D16, D19, D26 (D1, D40, D42 already FIXED) — each reproduced through `POST /command` first, then answered from the state desk's own builders (never a new fact source; fog honoured — `get_visible_enemies`), each pinned in `tests/test_sf_rr2_the_desk_answers.py`; done when the HOLD's question shrugs ≤ 1 of 20 with no wrong answer on its re-read.
3. **If the session has room:** SF-RR3 "the page and the copy" (its rows in the spec's table) — sized at RR2's close; otherwise it heads the next session, named in STATUS with its pin.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this session or heading the next); desk answers are display-only, but any change that reaches the AI runs the attribution arms (`tools/_pc_s14p3_series_arms.py`'s idiom: one seam per change) with `BASELINE_SERIES` byte-identical or every movement attributed and named; a new parser route adds its golden-corpus row (`tests/data/parser_golden_corpus.json`) and regenerates the routed words if a verb moves (`python -m tools.gen_routed_order_words`); the Godot parse harness if a `.gd` changes. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when SF-RR1 is closed by its re-read (or its misses filed and owned), SF-RR2's rows are FIXED with their pins and the HOLD re-read meets its line, STATUS ▶ NEXT UP names what follows (SF-RR3 … RR6, then S14b), and this file is overwritten for it.
