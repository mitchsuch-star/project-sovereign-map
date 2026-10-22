# NEXT SESSION PROMPT — Pre-Deploy S14c: events and historical moments — THE GATE

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14b COMPLETE**
> (`docs/VP1_DESIGNS_SPEC.md` §12–§14; commits through the hook — `git log -4`).
>
> **What the last session delivered (S14b parts 2 and 3):**
> - **VP-1 "The Emperor's Designs" landed whole** (`SYSTEMS_REFERENCE.md` §143–§146): three roads of a construction
>   and a seal, proclaimed from the Cabinet's road page (a button whose command is the executor's, quoted then
>   confirmed); every surface reading the one payload; THE DECISIVE PEACE stamped at the end-of-turn chokepoint
>   (once, marked and continued, the fifth register, the Verdict's +2, the front page and Le Moniteur); the four
>   Acts of the Empire (the road page's Decree rows, a peace-road gold sink). The census reads 9 open rows, every
>   one S15's UXR-4; condition (c) on the store page MET.
> - **The arms, per seed** (`tools/_vp1_road_arms_final.json`): VP1-RH stamps on turn 13 on all three seeds
>   (Austria subjugated once Vienna falls), VP1-TH on turn 20 on all three (the Pressburg partition), VP1-CS on none
>   (the Blockade never latches at K = 6; the Fall). S14e's re-measure should read the Rhine's fast subjugation.
>
> **Traps the last session paid for:**
> - **Copy a found script WHOLE** — a script's `policy_at` (per-loop dials) is part of the road; dropping it moved
>   the Rhine arm from turn 13 to 18 on one seed and to the Fall on another.
> - **A search over scripted roads works best on a FROZEN snapshot** (`git archive <sha> backend tools tests
>   godot-client/project-sovereign/assets/maps | tar --force-local -xf - -C <dir>`; or, for an uncommitted tree,
>   `git ls-files -co --exclude-standard … | tar --force-local -cf - -T - | tar --force-local -xf - -C <dir>` —
>   a plain `cp -r tests tools` copies ~8 GB of untracked run data), parallel agents iterating through the real
>   driver; then re-run the winners on the live tree with the same flags.
> - **A new verb's head can be stolen by a DD-0 rewrite** (`backend/ai/dd0_rewrites.py`): "decree X" was rewritten
>   "enact X" before the parser saw it. Add the verb's golden-corpus rows FIRST and run them.
> - **The Bash heredoc halves backslashes** — a `\b` became a backspace byte in a .py file. Write scripts with the
>   Write tool; scan for `\x08` after any shell-written edit.
> - **The executor's administrative pre-gate answers before the verb** — a test of a once-only refusal must refill
>   `admin_actions_remaining` first.
> - **`headline_lead_memory` is rebuilt every morning from an allowlist**; dispatch weights must stay tie-free.
> - `tools/score_run.py run --only` takes ONE arm per flag; the full suite is ~32,700 tests, ~7.5 minutes at `-n 8`;
>   two pins need bytecode (`env -u PYTHONDONTWRITEBYTECODE`).
> - `CLAUDE.md` at ~61,900 of 62,000 bytes (LF-normalised).
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions and
> SF-NAV-1-D1 are theirs). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14c — Events and historical moments: THE GATE, ruled under the standing delegation — work on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -4` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/PRE_DEPLOY_PLAN.md` (§2 the order; the S14c row in full, including the VP-1 hand-off), `docs/VP1_DESIGNS_SPEC.md` §11 (the hand-off row) and §14, `docs/AI_INTENT_SPEC.md` §4.6a (the one-foregrounded-crisis tempo rule) and §3.8.1 (D7's authored bounds), `docs/DESIGN_REFINEMENT.md` 8.EVAL (the Diplomacy & Flavor Content Menu), `docs/audits/ROAD_TO_EA_REPLAN_2026_08_03.md` (the August 3 memo's question: does the derived drama already cover a moment?), `docs/VISION.md`, and the transports an event would ride (`backend/models/dialogue_manager.py`, the mailbox endpoints in `backend/main.py`, `backend/game_logic/dispatch.py`'s classes, `backend/game_logic/gazette.py`).

Scope (the gate, not the build):
0. **The user's rules:** diplomacy is never typed (every answer an event offers is a button whose command is the executor's); the LLM never affects mechanics; events about AI courts reach them through the same functions (Golden Rule 5); no open-ended deferrals (Rule 9).
1. **Research, read-only, in parallel:** the existing transports an event can ride without a new modal; the derived drama that already covers each candidate moment (Trafalgar's news, the Confederation of the Rhine, the end of the Holy Roman Empire, the Berlin Decree, Tilsit) and what an authored event would add; the seams each answer would use (gold, trust, relations, stability, a court's alarm); the pacing caps (IGR-1, §4.6a); the content menu's rows; how D7's authored bounds would vary the deck per seed.
2. **Draft the gate from more than one angle** (history-first, player-first, systems-reuse-first), judge them (historian, architect, playtester), take the best base and graft; send it to adversarial critics; answer every correction.
3. **Rule:** the engine's shape (an event = a decision letter on the mailbox road or a dispatch beat), the first deck (its historical moments and situational events, each with its trigger, its answers and their seams), the cap and the pacing, the per-seed variation, the content-menu picks, the VP-1 hand-off (an event on one of the four moments reads `world.imperial_designs`, never fires on a forsworn road, never doubles a proclamation), the series' attribution plan, and the parts it is sized into (about one session each, each landing green). Flag any reversal of a user ruling.

Done when the gate is recorded in a new spec (`docs/EVENTS_SPEC.md`), its siblings filed in `docs/BUG_FIXES.md` with owners, the S14c row and STATUS ▶ NEXT UP name part 1, and this file is overwritten for it. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
