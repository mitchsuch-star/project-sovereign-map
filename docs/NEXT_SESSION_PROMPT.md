# NEXT SESSION PROMPT — Pre-Deploy S14b part 2: VP-1's road, armed on the existing screens

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14b part 1 LANDED**
> (`docs/VP1_DESIGNS_SPEC.md` §12; commits through the hook — `git log -3`).
>
> **What the last session delivered:**
> - **S14b part 1 LANDED** (`SYSTEMS_REFERENCE.md` §143): `backend/game_logic/imperial_designs.py` — the store
>   `world.imperial_designs` (unarmed without an authored block: the shipped boot shows nothing), three roads of a
>   construction and a seal, the gate, the irreversible proclamation's one predicate (`proclaim_refusal`), the terms
>   latch at every treaty the Emperor signs, the holds, lapses and rewards, THE DECISIVE PEACE's rule with its stamp
>   held (`decisive_peace_released()` False); the validator, serialization, the backfill; VP1-X1, X2, X3, X9 and the
>   part's own finds X11, X12 FIXED.
> - **The head measured:** the Tilsit road no longer latches the Blockade at K = 6 on any seed (3 / 4 / 3 end turns at
>   13 or more), so **VP1-RH carries part 3's done-when** (the record's own condition, §10 / §12.1); K stays 6.
> - **Filed:** VP1-X13 (the AI courts open the campaign with empty purses while France opens with her regen) heads
>   this part.
>
> **Traps the last session paid for:**
> - **A module-level cache keyed by `id(world)` serves a dead world's payload to a new one** (ids are reused) and never
>   sees a mid-turn treaty — the designs' payload is built on every read; a cache, if ever needed, hangs on the world.
> - **The code-health ratchet counts functions over 500 lines (cap 28):** `WorldState.to_dict` sits at 500 — a new
>   field there costs ONE line (comment on the same line).
> - **The ambient series never reaches the player's systems** (no armistice exit, no held cession, no dry run before a
>   purse is written on it): count each seam's reach, and say "dormant by construction" only with the zero printed.
> - **The full suite is ~32,580 tests, ~7.5 minutes at `-n 8`**; a `-x` run stops early and hides failures.
> - The Bash tool's heredoc eats backslashes: scripts with the Write tool, edits with Edit, CRLF docs normalised
>   to LF and written back CRLF.
> - `CLAUDE.md` at ~61,890 of 62,000 bytes (LF-normalised).
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions and
> SF-NAV-1-D1 are theirs). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14b part 2 — VP-1 "The Emperor's Designs": the road armed on the existing screens — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -3` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/VP1_DESIGNS_SPEC.md` (§2 the designs and their progress lines, §3 the branch, §6 the surfaces, §7 the series, §9 Part 2, §12 part 1's landing record), `docs/BUG_FIXES.md` §VP1 (VP1-X4 … X8, X10, X13), `backend/game_logic/imperial_designs.py` (the store, `proclaim_refusal`, `proclaim`, `build_designs_payload`, `progress_line`), `backend/ai/validation.py` + `backend/commands/parser.py` + CLAUDE.md's "Adding a new action" recipe (`proclaim_design`), `godot-client/project-sovereign/scripts/diplomacy_wizard.gd` (the Cabinet, F1) and `diplomatic_ledger.gd` (the Balance of Europe), `backend/game_logic/dispatch.py`, `backend/ai/state_desk.py` (`_answer_closure`), `backend/ai/first_contact.py`, `backend/ai/counsel.py`, `tests/fixtures/vp1_imperial_designs_block.json` (the block this part ships).

Scope (the record's §9 Part 2 — the design is the record's; flag any reversal):
0. **The user's rule (October 20, 2026): diplomacy is never typed.** The proclamation is a Cabinet button whose command is the executor's; every disabled reason is `proclaim_refusal`'s; no line anywhere tells the player to type a diplomatic order.
1. **The head — VP1-X13, reproduce first:** which AI spends turn 1 would make with a purse; then seed every active court's purse at boot from the regen's own reading (`diplomacy.regen_dp_for` + the seat) at the one boot seam, behind its own seam with its reach counted; `BASELINE_SERIES` attributed and re-pinned if it moves (naming VP1-X13), the commanded arms attributed.
2. **Build:** the shipped `europe_1805.json` gains the `imperial_designs` block (`MODDING_FORMAT.md`; the validator green); `proclaim_design` (the recipe — VALID_ACTIONS, the parser, `_action_costs` 1 admin action + 2 DP, the mock keywords + `python -m tools.gen_routed_order_words`, display names, the campaign log type, a golden-corpus entry, the door pin `tests/test_wo_slice7_cabinet_door.py`); the Cabinet road page with its confirm (the three roads, each design's progress line, the gate and the refusal, the irreversible warning); the Balance block, `designs_clock`, the TODAY door, the desk and first-contact goal answer (condition (c)'s sentence verbatim), the counsel, the manner line on the table, the bilateral preview and the incoming-proposal popup, the Admiralty "N of 26"; VP1-X4 … X8, X10.
3. **Measure:** `BASELINE_SERIES` byte-identical (the ambient France never proclaims) with the reach counted, or every movement attributed; the commanded arms attributed (`tools/_vp1_arm_attribution.py` — the new digest text named).

Done when (§9 Part 2) each of the six designs fulfils on a staged board through real clicks (the button's command is the executor's; every disabled reason is the executor's refusal); a second proclamation is refused with its reason; a forsworn design never fulfils; the VOLTE board fails guard 6; a drift pin shows every surface carries the payload's one slice; a census finds no line that tells the player to type a diplomatic order; the Godot parse harness EXIT 0; the IQ-10 frames of the road page at Interface Scale 1.0 and 2.0 show every button above the fold; VP1-X4 … X8, X10, X13 FIXED with their pins; the full suite green through the hook; STATUS ▶ NEXT UP names part 3 and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with `BASELINE_SERIES` byte-identical or every movement attributed (count the reach); edit CRLF files with a script that preserves line endings; grep-verify any agent's bulk `.gd` edits. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
