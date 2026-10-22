# NEXT SESSION PROMPT — Pre-Deploy S14d: the table lesson, the onboarding pass

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14c COMPLETE**
> (`docs/EVENTS_SPEC.md` §13–§17; `SYSTEMS_REFERENCE.md` §147–§147.12; commits through the hook — `git log -5`).
>
> **What the last sessions delivered:** S14c, "Events and Historical Moments", in four parts — the moments' engine on the
> letter transport, the client and the instruments, the four letters armed (the Bavarian Match, the Throne of Holland,
> the Crown of the Reich, the Decree of Berlin), and part 4's measurement: a production-time trace
> (`tools/_moments_trace.py`) on every sweep run, driver arm and road arm — 0 ceiling breaches, 0 floor breaches,
> shown = applied on all 45 runs — and a Mode C walk in the real client (a letter answered from its rail row, one
> lapsed into the dispatch). Part 4's finds S14C-X24 … X28 are FIXED; the census reads 9 open rows, all S15's UXR-4.
>
> **Traps the last sessions paid for:**
> - **`core.autocrlf` rewrites committed files to CRLF in the working tree**; edit through a script that keeps endings.
> - **The Bash heredoc halves backslashes** (a `"\n"` in an f-string became a real newline) — Write-tool scripts only.
> - **`git add` exits 1 on `europe_1805.json`** (a tracked file under a gitignored folder) — `git commit -- <paths>`.
> - **`tools/dd_b_play.py` is the real-client instrument** (Mode C): `start --road … --out <fresh dir> --port 8007` in
>   the background, then one `act` per player action; pre-seat saves in `<out>/saves` and load them from the title's
>   "Load a Campaign…". A look prints only what CHANGED — read `<out>/state/NNNN.json` (`buttons`, `texts`) for the
>   whole screen; a diorama's Close appears only after its replay.
> - **The client's envelope join is hand-copied key by key** (`main.gd`, the Aug 30 trap): a key the client reads must
>   also be copied into `diplo_data`.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1, A1
> and the X2 ruling are theirs to overrule). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14d — the table lesson, the onboarding pass — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/PRE_DEPLOY_PLAN.md` §2 the S14d row (its scope, its done-when and S14c's hand-off line); `docs/DESIGN_REFINEMENT.md` 8.EVAL "Pre-EA Onboarding & Teaching Pass" (R159 and "The Congress" lesson); the School of War's first lesson (the Danube — `tutorial_overlay.gd` and its backend scenario) and `docs/TUTORIAL_SCRIPT.md`; `docs/PLAYTESTING.md` (Mode C, `tools/dd_b_play.py`).

Scope:
1. **The gate first, under the standing delegation** (research, then rule, the S14b / S14c pattern): for each core screen the row names — the Cabinet, the settlement table, the per-court separate peace, the LAWS book, the Admiralty's camp and staging, the muster's free "what if" preview, VP-1's designs, a moment letter — the one line that names its mechanic the first time it opens, where it lives (a first-open latch that serializes), and how it is pinned; and "The Table", a second School of War lesson teaching a separate peace, a vassal proposal and Talleyrand's missions in a few steps, built like the Danube lesson. Record the gate in a spec, its siblings filed (`BUG_FIXES.md`), its parts sized.
2. **Then build** in the parts the gate sizes (the row is 1.5 sessions): the first-open lines, the lesson, its pins.

Done when (the row): every core screen carries its line, the lesson plays through on the real client (the DD-B instrument) and its pins hold, and a new-player run reaches the table on turn 1; the series byte-identical or re-pinned with the row named; the full suite green through the hook; STATUS ▶ NEXT UP names S14e and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with every movement attributed (count the reach); "diplomacy is never typed" — every lesson step is a button; grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
