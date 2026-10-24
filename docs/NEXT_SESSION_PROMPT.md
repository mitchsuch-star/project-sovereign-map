# NEXT SESSION PROMPT — Pre-Deploy S14d part 3: the walk and the close; then S14e

> Overwritten each time a session hands off. Current hand-over: **October 24, 2026, after S14d part 2's second
> landing — the Table lesson — LANDED; part 2 COMPLETE** (`docs/TABLE_LESSON_SPEC.md` §15–§16; `SYSTEMS_REFERENCE.md`
> §148.9–§148.10; commits through the hook — `git log -5`).
>
> **What the last session delivered:** the registry refactor committed alone with the Danube byte-identical (§15);
> then the Table — `tutorial_table_1805.json` tuned by `tools/_table_board_probe.py` (the probe plays the three turns
> for real through the client's endpoints and commits its record with the board's hash), the seven cards
> (`tutorial_table_steps.gd`, every step a door or a button), the settlement door kind, the Table's `alt` arms, the
> registry's second entry, the menu's second row, the driver script, 15 driven pins through the real overlay, the
> arithmetic pins, the frames at both scales; the engine rows X13 (the counter names the struck tribute), X14 (the
> lesson keys' contract — `MODDING_FORMAT.md` + `_validate_lesson_keys`), X15, X17, X40, X41 FIXED; X49 and X50 filed.
> Three findings corrected the gate's board: `war_scores` is NOT cosmetic (turn 1 reads the stored score everywhere —
> authored to the live 85), France's ledger losses never reached the table (now the record's 9,000; the record's five
> battles are the lever), and the chip's peace is the staged slice (200 gold + Carniola, 68 Favorable), not Talleyrand's
> typed draft.
>
> **Traps the last session paid for:**
> - **A Python heredoc through the Bash tool halves backslashes AND can silently write nothing** — write every patch
>   script with the Write tool and run it by path; assert every anchor's count.
> - **The settlement table does not open on a one-to-one war** (`one_to_one_war`) — after a separate peace with every
>   court but one, the court's own page settles it.
> - **A ratified peace purges the pair's battle records** — count a script's battles by their turn.
> - **A sent proposal leaves no `events` entry on its reply** — `proposal_result {outcome: PENDING}` is the mark (its
>   `proposal_type` reads "Diplomatic Action", S14D-X49).
> - **The tutor card renders on an advance or a turn change only** — a branch state must re-render itself.
> - **`tutorial_table_1805.json` is under `.gitignore`'s `assets/` rule** — `git add -f` before a commit by path.
> - **PL-23's drafting pushback is a 5–15% random roll on harsh terms** — a test that sends "harsh" pins the roll off.
>
> **Nothing waits on the user before S15** (S14d's A1 and the re-size, UXR-4, the code-signing certificate, AO's three
> questions, SF-NAV-1-D1 are theirs to overrule). Paste everything below the line as the opening message of a fresh
> session.

---

Pre-Deploy S14d part 3 — the walk and the close — then S14e, on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/TABLE_LESSON_SPEC.md` §9 (part 3), §16 (the Table's landing record and its traps), §4.2 (the cards); `SYSTEMS_REFERENCE.md` §148.10; `BUG_FIXES.md` §S14D (the 5 open rows: X18, X42, X43, X49, X50); `docs/PLAYTESTING.md` (Mode C); `tools/dd_b_play.py`; `tools/tutorial_screenshot.gd`.

Scope:
1. **The Mode C walk** on `SOVEREIGN_PORT=8007` via `tools/dd_b_play.py` and the shipped client: the title's two School rows; the Table's seven cards played to the hand-off by the buttons alone (the Cabinet's Reassure row, the table's chip, the chooser's Proceed, Send as suggested; the vassalage eased once); the Danube's twenty cards reached (a skim); the campaign's eight first-open lines on BEGIN — each once, then gone, then still gone after a save and load. S14D-X18 (`tutorial_screenshot.gd`'s 8005 refusal) on the way.
2. **The release build's fourth file:** build through `deploy/build.bat`, boot the frozen backend, `POST /new_game {"scenario": "tutorial_table"}` answers on the build (the spec and pins already name the file — S14D-X15 landed; this is the live proof).
3. **The sweep's two rows:** S14D-X49 — the PENDING `proposal_result` carries the proposal's display name (`proposal_display_name` from the dialogue's terms at `main.py`'s PL-14 safety net), pinned in `tests/test_tutorial_table_scenario.py::TestTheDispatchNamesItsProposal`; S14D-X50 — `incoming_proposal_popup.gd::_build_peace_preview_section` also prints a counter's clause lines beginning "Struck" when `is_counter_offer` is set (a client change; a staged peace counter frame pins it).
4. **The doc sweep:** `TUTORIAL_SCRIPT.md` §The Table Lesson (the mirror of the seven cards, as §The Danube Lesson is), `SAVE_FORMAT_REFERENCE.md` (no new fields — confirm), `DESIGN_REFINEMENT.md`'s row (A2), `ROADMAP.md`, `PRE_DEPLOY_PLAN.md`'s S14d row and total (A1 — the reduction named for the user: mounts in the campaign, signs in the lesson; the re-size 1.5 → about 2.5 sessions), `docs/PLAYTESTING.md` (the Table script and the probe); S14D-X42 (verify Verhuell before any edit) and X43; the census 0 open S14D.

Done when: the walk shows the Table played to its hand-off by buttons alone and a fresh campaign showing each line once; the frozen build answers `/new_game` on the fourth file; X18, X42, X43, X49, X50 FIXED; the full suite green through the hook; STATUS ▶ NEXT UP names S14e and this file is overwritten for it.

Rules: reproduce each row on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); "diplomacy is never typed" (every lesson step a button or a door); a card never dresses a game step as history; a line's fact the board does not deliver changes the line, never the board; grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process (`tools/godot_parse_check.gd`, expect EXIT=0, commit the refreshed report). Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
