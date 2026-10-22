# NEXT SESSION PROMPT — Pre-Deploy S14b: RR6-X3 and UXR3-F11 at its head, then VP-1 "The Emperor's Designs" (the gate first)

> Overwritten each time a session hands off. Current hand-over: **October 21, 2026, after SF-RR6 "the instrument
> reads what the player sees" landed — the Score Finish residue COMPLETE** (commits through the hook — `git log -2`).
>
> **What the session delivered** (`SYSTEMS_REFERENCE.md` §141; rows `BUG_FIXES.md` §Score Finish Step 8 SFR-I2, I4, I5,
> I6, I7, §The Economy Audit EA-2 and §The Economy Gate EG-X4 FIXED, `DESIGN_REFINEMENT.md` EG-D1 BUILT, §RR6 RR6-X1
> and X2 FIXED, RR6-X3 heading S14b; pins `tests/test_sf_rr6_the_instrument.py`; the checklist
> `docs/SCORE_CHECKLIST_V1_2.json`; the re-reads and deltas `docs/audits/score_runs/2026_10_21_rr6/README.md`):
> - **The driver records what the player sees:** the enemy phase in the dialog's own words (the message kept in the
>   jsonl, marked `unrendered`), the Unmet Marshals block, France's wars, the chest across every end turn against the
>   applied Net, a script's preconditions (⚠ SCRIPT PRECONDITION). The DL script re-staged; its items read their rows.
> - **EG-X4 traced and fixed at the store's seam** (`intel.scouted_view_expired`: a scout's FULL view expires beside a
>   French corps); `BASELINE_SERIES` byte-identical with it up and down.
> - **Checklist v1.2** (ten items, EG-D1's band among them); the baseline, the final reading, the gate's and the entry
>   arms re-read beside their records, the frozen marks kept.
>
> **Traps this session paid for:**
> - **An older digest's enemy-phase line is the server `message`**, which the client never renders; a new digest
>   quotes the dialog (meta `enemy_phase_text: rendered`). A reader must not count the message as the game.
> - **`score_run.py check` defaults to the frozen v1** (the step-0 pins hold it there) — pass
>   `--checklist docs/SCORE_CHECKLIST_V1_2.json` for the corrected readers. `score_reread.py` re-reads only items
>   marked `amended`; an amended probe that reads saves (`reread_needs: saves`) keeps its archived mark where the
>   archive kept none (saves are gitignored — the baseline and the final reading have none).
> - **A board change that breaks the DL staging now says so** (⚠ SCRIPT PRECONDITION): re-stage the script, never the
>   reader. The levy needs gold too — turn 1's chest cannot pay it (that is why it runs on turn 3).
> - **The heredoc backslash trap again** (a `"\n"` inside a quoted heredoc's Python replacement) — scripts with the
>   Write tool, edits with Edit.
> - **`docs/BUG_FIXES.md` is CRLF in the working copy, LF in the index** (`core.autocrlf`): a Python rewrite with
>   `newline="\n"` changes only the rows in git's eyes; STATUS / SYSTEMS_REFERENCE / CLAUDE.md are kept CRLF on disk.
> - **`PYTHONDONTWRITEBYTECODE` in the shell fails `test_fa_slice8`'s bytecode pins** outside the hook — unset it, as
>   the hook's commit command does.
> - **`Digest.__init__` may not subscript a new `meta` key** (test_fa_slice15b's AST pin) — use `meta.update`.
> - **The commanded arms' games are byte-identical across a pure-instrument change**: `tools/_sf_rr6_arm_attribution.py`
>   splits each arm into its GAME and VIEW streams — use it before blaming the driver.
> - `CLAUDE.md` at 61,904 of 62,000 bytes.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14b — its head first, RR6-X3 (one sighting rule) and UXR3-F11 (the imperial peace's "50 of 45"), then VP-1 "The Emperor's Designs", the gate first — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/PRE_DEPLOY_PLAN.md` §2 (the S14b row), `docs/BUG_FIXES.md` §RR6 (RR6-X3) and §UXR-3 the review (UXR3-F11), `docs/SYSTEMS_REFERENCE.md` §141.8–§141.9 (EG-X4's trace and the sibling), and the readers RR6-X3 names: `backend/game_logic/intel_surfaces.py` (`enemy_sightings`), `backend/models/world_state.py` (`get_last_known_location`, `calculate_visibility`), `backend/commands/strategic.py` (`pursue_known_location` and the per-turn PURSUE gate), `backend/commands/disobedience.py` (the cautious objection's intel read), `backend/ai/question_desk.py` (`_answer_enemy`, `_answer_what_if`), `backend/main.py` (`_filter_enemy_phase_by_visibility`); for UXR3-F11 `godot-client/project-sovereign/scripts/campaign_end.gd` (the titled line) and `backend/game_logic/congress.py` (the gate text); for VP-1 `docs/audits/ROAD_TO_EA_REPLAN_2026_08_03.md` §52 and the S14b row's gate questions.

Scope — the design is the spec's; rule the details at the head, measured, and flag any reversal:
0. **The user's rule (October 20, 2026): diplomacy is never typed.** No new line teaches a typed diplomatic order.
1. **RR6-X3 first:** reproduce it (the slice tree's FLD arm, turn 7: `what are Ney's odds against Archduke John` → "beyond reach of Archduke John at Provence"; `Ney, attack Archduke John` → "No intelligence on Archduke John's position"), then rule under the standing delegation, measured on boards, which reader of "where the player last saw a man" is canonical — (a) a shown enemy-phase action writes its sighting into the store, so the store knows what the player was shown (recommended, every surface through `intel_surfaces`); (b) the order reads the desk's rule; (c) the desk reads the store's — and build it at its seams so the order, its per-turn gate, the cautious objection, the desk and the dispatch place a man by one rule. The sibling sweep: every surface that names an enemy's place (the map, the Ledger, the status report, the war table). `BASELINE_SERIES` byte-identical (the player's fog only) with every commanded arm's movement attributed (`tools/_sf_rr6_series_arms.py`, `tools/_sf_rr6_arm_attribution.py`). Pin `tests/test_rr6_x3_one_sighting_rule.py`.
2. **UXR3-F11:** the imperial peace's summary (the client's `campaign_end.gd`) and the Congress's gate text (`congress.py`) name the held count against the bar it cleared in words that cannot read as "more than all" ("50 titled provinces — 45 were needed"); a backend pin and the Godot parse harness for the `.gd`.
3. **Then VP-1's gate** (its own session if it does not fit — size it at the head): the drafted questions, what the designs are (history-first), their rewards, how the triumph sits beside the Congress and the Verdict, and the two parked ideas it absorbs, ruled under the standing delegation; then the build the S14b row names.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this session or heading the next); a change that reaches the AI or the backend runs the attribution arms with `BASELINE_SERIES` byte-identical or every movement attributed; the Godot parse harness for every `.gd` changed; edit CRLF files with a script that preserves line endings (`objection_dialog.gd`, `popup_base.gd`, `proposal_confirm_popup.gd/.tscn`, two map scripts and `deploy/README_TESTER.txt` are CRLF). Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when RR6-X3 and UXR3-F11 are FIXED with their pins, VP-1's gate is recorded (or sized to its own session and named), STATUS ▶ NEXT UP names what follows, and this file is overwritten for it.
