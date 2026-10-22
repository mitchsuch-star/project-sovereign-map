# NEXT SESSION PROMPT — Pre-Deploy S14c part 4: the sweep, the walk, the close

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14c part 3 LANDED**
> (`docs/EVENTS_SPEC.md` §13–§16; `SYSTEMS_REFERENCE.md` §147–§147.11; commits through the hook — `git log -4`).
>
> **What the last sessions delivered:** the moments' engine (part 1), the client and the instruments and three letters
> armed (part 2), the Crown of the Reich with its Moniteur special, the twelve matrix cells and clauses A–G (part 3). The
> whole deck ships in `europe_1805.json`. `BASELINE_SERIES` is byte-identical on every arm; the nine commanded arms meet
> the Match (7 of 9) and Holland (5), the default decline their one game movement (attributed); the VP-1 road arms stamp
> as before, and on VP1-RH marengo the Reich arrives (turn 17) while Holland's letter behind it is crowded out with its
> receipt — R2 on a real arm. 0 open S14C rows.
>
> **Traps the last sessions paid for:**
> - **`core.autocrlf` rewrites committed files to CRLF in the working tree**; edit through a script that keeps endings.
> - **`git add` exits 1 on `europe_1805.json`** (its folder matches a `.gitignore` rule though the file is tracked) — use
>   `git commit -- <paths>` alone, which takes tracked files directly.
> - **The Bash heredoc halves backslashes and chokes on nested quotes** — Write-tool scripts.
> - **Never edit the tree while a suite or an arm runs** (lazy imports read mid-run).
> - **Attribute a parted commanded arm** by re-running it with `--seam backend.game_logic.moments:tick=[]`
>   (`tools/score_run.py` `_run_driver`) and comparing with `tools/_vp1_arm_attribution.py --baseline`.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1, A1
> and the X2 ruling are theirs to overrule). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14c part 4 — the sweep, the walk, the close — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -4` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/EVENTS_SPEC.md` (§7 the series and the arms, §9 Part 4, §10–§11, §13–§16 the landing records), `SYSTEMS_REFERENCE.md` §147, `tools/ai_v_sweep.py` (`derive_metrics`'s moment metrics, `run_all`'s arm C), `tests/test_moments_pacing.py`, `tools/_s14c_arm_attribution_final.json`, `docs/PLAYTESTING.md` (Mode C).

Scope (the record's §9 Part 4):
1. **The sweep:** `tools/ai_v_sweep.py`, the 10 `SWEEP_SEEDS` × 40 turns; `tests/test_moments_pacing.py` gains the ceilings on every arm (≤ 1 moment a producing turn, ≤ 1 open letter, 0 letters during a foregrounded crisis, no moment with its premise false) read from the authored block, and the floors where moments can fire (the commanded arms and the VP-1 road arms — every moment whose premise holds in its window arrives or ends on screen as a receipt); each moment's reach reported per seed.
2. **The accept arm:** a commanded arm with `--moment accept` — every delivered figure equals its quote.
3. **The archived arms** (CMD-A / H / M, DL, FLD, LAW, OP, VOLTE, FC) attributed (part 2b's record holds the reading; re-read on part 4's tree).
4. **The walk (Mode C):** the client on `SOVEREIGN_PORT=8007` — a letter answered through its buttons, one lapsed, the rail row opening its letter, the lapse sentence in the dispatch (`docs/PLAYTESTING.md`).
5. **The close:** the sibling sweep; `ROADMAP.md`'s 8.5 rows and the S14c row's text per A1; STATUS; S14d's row gains its hand-off line ("the first moment letter names the mechanic when it first opens").

Done when (§9 Part 4): ceilings green on every arm, floors green where moments can fire, each moment's reach reported per seed; the accept arm's figures equal their quotes; the walk shows a letter answered and one lapsed; the census reads 0 open S14C rows; the full suite green through the hook; STATUS ▶ NEXT UP names S14d and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with every movement attributed (count the reach); grep-verify any agent's bulk `.gd` edits. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
