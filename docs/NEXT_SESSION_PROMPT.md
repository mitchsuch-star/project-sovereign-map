# NEXT SESSION PROMPT — Pre-Deploy S14c part 3: the Crown of the Reich, the windows, the matrix

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after S14c part 2 LANDED**
> (`docs/EVENTS_SPEC.md` §13–§15; `SYSTEMS_REFERENCE.md` §147; commits through the hook — `git log -4`).
>
> **What the last session delivered:**
> - **Part 1** — the moments' engine (`backend/game_logic/moments.py`, §13), the finds S14C-X18 … X20.
> - **Part 2, first landing** — the client and the instruments (§14): one lapse predicate, one envoy-row dismissal
>   that spares a standing letter (a call, a moment, an open auction — X23), the autonomy plan's gold and ports on every
>   surface, the popup's `is_moment` register, the sweep and the driver; X2 RULED (a standing call keeps the wizard lock).
> - **Part 2, second landing** — three letters armed (§15): the Match, Holland and the Decree ship in `europe_1805.json`
>   (verbatim the staged deck's); `BASELINE_SERIES` byte-identical on ten arms with real reach (Holland arrives on turn
>   18 on the passive board and lapses as its empty decline); the commanded arms meet the Match (7 of 9) and Holland (5),
>   the decline's −5 with Bavaria their one game-stream movement, attributed by holding the tick down.
>
> **Traps the last session paid for:**
> - **`core.autocrlf` rewrites every committed file to CRLF in the working tree** — edit through a script that keeps
>   the file's own endings (the scratchpad `eu.py` idiom). **The Bash heredoc halves backslashes and chokes on nested
>   quotes** — Write-tool scripts.
> - **The suite-reach head on a scratch tree** (`git archive HEAD | tar -x`) carries no Godot import cache, untracked
>   art or `.git` — its Godot / art / stamp failures are the tree's own; read only the failures your change can reach.
> - **The commanded arms' attribution:** re-run a parted arm with `--seam backend.game_logic.moments:tick=[]` through
>   `tools/score_run.py`'s `_run_driver` and compare with `tools/_vp1_arm_attribution.py --baseline`.
> - **The event log rolls at 500 rows** — a pin on a row from turn 19 must read it before the roll (capture mid-run).
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1, A1
> and the X2 ruling are theirs to overrule). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14c part 3 — the Crown of the Reich, the windows, the matrix — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -4` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/EVENTS_SPEC.md` (§2 M3, §3.6 the hand-off, §4 R1–R2, §5 the bands and clauses A–G, §9 Part 3, §13–§15 the landing records), `SYSTEMS_REFERENCE.md` §147, `backend/game_logic/moments.py` (`ANCHORS`, `_anchor_design_fulfilled`, `road_gate`, `_crowd_out`), `backend/game_logic/gazette.py` (`_SPECIAL_WEIGHTS`, `_special_candidates`), `tests/test_moments_armed.py`, `tests/test_ai_intent_assurance.py` (the teeth controls), `tools/ai_v_sweep.py` (`_variance_signature`).

Scope (the record's §9 Part 3 — the design is the record's; flag any reversal):
0. **The rules:** every answer is a button whose command is the executor's; the LLM never affects mechanics; ints only to Godot; no module lever; serialization for any new field.
1. **M3, the Crown of the Reich:** the block gains the fixture's `crown_of_the_reich` (causal, `lag` 1 from the morning the Confederation is told; Road I only); Accept raises each Confederation member that is France's vassal by 10 loyalty, costs Austria 15 goodwill and Europe's alarm 3 (`moment_reich`); Le Moniteur's special "THE EMPIRE IS NO MORE" (81, free in `_SPECIAL_WEIGHTS`) runs in the next issue on that answer only.
2. **The matrix:** the Reich's three cells (Road I only; Roads II and III never) — all twelve green.
3. **R1 and R2 on staged boards:** a foregrounded crisis defers a letter within its grace; a crowded-out letter ends on screen (the receipt, its decline applied).
4. **Clauses A–G** over `SWEEP_SEEDS` (AI_INTENT §3.8.1 gains them — amendment A3): `_variance_signature` gains `moment_turns` (run-sourced, never the boot — the graft pin), the same seed twice EQUAL, variance forced off EQUAL to `historical`.
5. **The backfill's causal entry** on the T10 / T20 fixtures (the Reich `passed(before_save)` where its anchor + lag is at or before the save turn).

Done when (§9 Part 3): on a staged Road I board the Confederation fulfils and the Reich letter arrives a turn later; Accept raises each vassal member's loyalty, costs Austria 15 and the alarm 3, and the special runs in the next issue; on Roads II and III it never arrives; all 12 cells pass; a staged crisis defers a letter and a crowded-out letter ends on screen; the same seed twice compares EQUAL and variance forced off compares EQUAL to `historical`; the series byte-identical or every movement attributed (the road arms `tools/_vp1_road_arms.py` — VP1-RH reaches the Confederation, so M3); the full suite green through the hook; STATUS ▶ NEXT UP names part 4 and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with every movement attributed (count the reach); grep-verify any agent's bulk `.gd` edits. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
