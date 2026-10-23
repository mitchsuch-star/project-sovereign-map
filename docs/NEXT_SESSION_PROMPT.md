# NEXT SESSION PROMPT — Pre-Deploy S14d part 1, second landing: the frames and the copy rows; then part 1b

> Overwritten each time a session hands off. Current hand-over: **October 23, 2026, after S14d's gate RULED and
> part 1's first landing LANDED** (`docs/TABLE_LESSON_SPEC.md` §0–§13; `SYSTEMS_REFERENCE.md` §148; commits through
> the hook — `git log -5`).
>
> **What the last session delivered:** the S14d gate (eight researchers, a synthesis, two adversarial critics with probes
> on a built Table board — 31 corrections applied or answered, §12), with one user-visible reduction named for the user
> (A1: "reaches the table on turn 1" reads as MOUNTS in the campaign and SIGNS in the lesson; the row re-sized
> 1.5 → about 2.5 sessions in four parts); and part 1's first landing: `world.first_opens`, the seven lines in
> `backend/game_logic/first_open.py`, attached at the response edge on a copy (the GET wrappers for the Cabinet, the
> road page, the ledger's two books; one envelope chokepoint for every dialogue-borne payload), `POST /first_open`
> returning a tiny non-draining dict, the client drawing each line at the head of its surface and acknowledging once
> per screen per world, the LAWS book's R159 subtitle, `what_if_line` on the muster's gate road, the burned guidance
> latch guarded (S14D-X1). 32 pins in `tests/test_first_open.py`; the series byte-identical; the census 35 open S14D.
>
> **Traps the last session paid for:**
> - **A builder with a drift pin cannot be attached to** — `laws_payload` and `build_designs_payload` are compared
>   equal to the ledger's / the endpoint's copy by existing pins; attach on the ENDPOINT's own dict (`/ledger`,
>   `/imperial_designs`), never in `ledger.py` or the builder.
> - **`build_base_response` drains even with `include_popup_passthroughs=False`** (draft notices, the relay's let-go):
>   an acknowledgement endpoint returns a plain dict.
> - **`_build_result_response` forwards every executor key** — a wire at the `/command` placement sites alone misses
>   the settlement table; the one chokepoint is the tail of `build_base_response` (`_wire_result_dialogues`).
> - **The settlement popup hides on every dial** (`_on_option_selected`, `_on_settlement_tier2_affordance`) and re-shows
>   on the restage — a client copy cleared on hide loses the line; the backend's turn rule carries it instead.
> - **The ratchet counts a silent `except Exception: pass` in a new module** and CLAUDE.md sits 34 bytes under its cap
>   after this landing's row (61,966 of 62,000): every new row is paid for by a trim.
> - **`core.autocrlf` is per file here** (world_state.py, main.py, combat_executor.py, proposal_confirm_popup.gd and
>   the docs are CRLF; ledger.py, strategic.py, the other .gd files and the JSON are LF) — edit through a script that
>   detects and keeps each file's ending (`scratchpad/edit_part1*.py`'s shape).
> - **The Bash heredoc halves backslashes**; Write-tool scripts only. **`git add` exits 1 on `europe_1805.json`.**
> - **The series runs the engine in process**: a seam on the wire (a payload key) reads reach 0 there by construction;
>   say so rather than inflate it.
>
> **Nothing waits on the user before S15** (S14d's A1 and the re-size, S14c's A1 and the X2 ruling, UXR-4, the
> code-signing certificate, AO's three questions, SF-NAV-1-D1 are theirs to overrule). Paste everything below the line
> as the opening message of a fresh session.

---

Pre-Deploy S14d part 1, second landing — the frames and the copy rows — then part 1b, on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/TABLE_LESSON_SPEC.md` §0 Q3 (the class sweep), §2 (the lines and their draw sites), §9 (parts 1, 1b), §13 (the first landing and §13.4 what this landing owes); `SYSTEMS_REFERENCE.md` §148; `BUG_FIXES.md` §S14D (the open rows homed to part 1 and part 1b); `tools/iq10_run_captures.py` (the frames: `settlement_three_courts`, `cap_moments` ~1365–1395, the road page, the Cabinet) and `tests/test_sf_rr5_the_frames.py` (`must_show`); `docs/PLAYTESTING.md` (Mode C).

Scope:
1. **The frames (part 1's second landing):** re-shoot the IQ-10 frames of the table, the chooser, the letter, the road page and the Cabinet's step 1 at Interface Scale 1.0 and 2.0 with the first-open line at the head, and add a `muster_confirm` frame; a `must_show` clause per frame for the line AND the surface's first button above the fold — a line that fails it is shortened, never moved below the fold (the record's §10). A5: `EVENTS_SPEC.md` §2/§6 gain the sixth part (S14D-X5).
2. **The class sweep (Q3):** walk the other action surfaces — the Congress summons row, Formable Nations, the capture modal, the commission chooser, the call-to-arms letter — and for each either file a new S14D row and line it on the store (one more id, one attach site, one draw site, one pin) or rule it covered on the row (the capture modal's priced buttons and card XII; the commission hint latch; the call's whole-sentence reasons).
3. **The copy rows homed to part 1:** S14D-X3 (a LAWS door chip on the dispatch's law line), X6 (the PROPOSE heading says "ratified"), X9 (the Cabinet titled DIPLOMACY — the pins flipped consciously), X10 (the DP header), X26 (the dead camp fallback and its pin), X27 (a lapsed law's two prices), X28, X29, X30 (`what_if_line`'s post-swap foe), X31, X32, X33, X34 (one name for the separate peace), X35, X44 — each reproduced on a board before it is built, each pinned where its seam lives.
4. **Part 1b:** S14D-X11, X12, X37, X38, X39 — the diplomacy engine's class found by the gate's probe — reproduced on the booted 1805 world, fixed, pinned in the owning file; the series byte-identical or re-pinned with the row named (X37's stamp may reach memory — count it).

Done when: every frame shows its line at the head and its first button above the fold at both scales; every action surface is lined or ruled; the part-1 and part-1b rows read FIXED with their pins; `BASELINE_SERIES` byte-identical (or re-pinned, named); the full suite green through the hook; STATUS ▶ NEXT UP names part 2 (the Table) and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with every movement attributed (count the reach); "diplomacy is never typed"; every new line ≤ 220 characters, from the live constants, clean under `_TYPED`, "Sire" in its opening; attach on the endpoint's own dict, never a builder with a drift pin; grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
