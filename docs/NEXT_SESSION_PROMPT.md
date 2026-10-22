# NEXT SESSION PROMPT — Pre-Deploy S14b: VP-1 "The Emperor's Designs" — the gate first

> Overwritten each time a session hands off. Current hand-over: **October 21, 2026, after S14b's head landed —
> RR6-X3 "one sighting rule" and UXR3-F11 "the titled tally"** (commits through the hook — `git log -2`).
>
> **What the session delivered** (`SYSTEMS_REFERENCE.md` §142; rows `BUG_FIXES.md` §RR6 RR6-X3 FIXED with the
> siblings RR6-X4 … X11, §UXR-3 UXR3-F11 FIXED; pins `tests/test_rr6_x3_one_sighting_rule.py`,
> `tests/test_uxr3_f11_the_titled_tally.py`; the reading `docs/audits/score_runs/2026_10_21_rr6x3/`):
> - **One sighting rule, `intel_surfaces.last_seen`:** in sight now (his province reads PARTIAL or better — the
>   map's rule) a man is where he stands; out of sight, his newest sighting, each snapshot entry its own turn; and
>   the store learns what the enemy-phase dialog SHOWS (`record_shown_sightings`, the filter lifted to
>   `backend/game_logic/enemy_phase_fog.py`). Every reader of an enemy's place asks it — the order, its gate, the
>   objections, the desk, the dispatch, the Ledger, the status report, the map, the muster.
> - **UXR3-F11:** "50 titled, 45 needed" past the bar everywhere (`congress.titled_tally`); the end screen prints the
>   backend's line.
> - **Measured:** `BASELINE_SERIES` byte-identical (reach 0 — the ambient sim never reaches the rule); four commanded
>   arms (FLD, CMD-H, LAW, VOLTE) part at turn 7 at the one line and are the entry archive byte for byte with the
>   rule held down (`tools/_rr6_x3_arm_attribution.py`). On CMD-H the re-timed war meets EG-D2's lawful road
>   (France 25 → 9 at turn 40) and the reading moves with it — recorded per seed, never claimed as a defect.
>
> **Traps this session paid for:**
> - **The Bash tool's heredoc eats backslashes** — again: `"\\n"` in a heredoc'd Python replacement. Scripts with
>   the Write tool, edits with Edit; a CRLF doc is edited by normalising to LF and writing CRLF back.
> - **A commanded arm moved by a fix is re-timed for the rest of its forty turns** — the first parting names the
>   cause; the reading after it is a different campaign. Attribute with the fix held down at its seam
>   (`--seam MODULE:NAME=EXPR` takes an expression over the call's args `a`), never by reading the end state.
> - **`_score_probes` C3 explained battles only:** an enemy-phase walk-in moves the bill too (the grip term) —
>   RR6-X9 counts captures. A reader that explains one enemy-phase cause should be asked about the others.
> - **The ambient series never runs `meta_executor`'s end turn** (`tm.end_turn` directly) — a store write placed
>   there reaches no series arm; count the reach before calling a series byte-identical "proven".
> - `CLAUDE.md` at 61,894 of 62,000 bytes.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate and AO's three questions are theirs).
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14b — VP-1 "The Emperor's Designs": its GATE first, ruled under the standing delegation, then the build the S14b row names — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -2` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/PRE_DEPLOY_PLAN.md` §2 (the S14b row), `docs/audits/ROAD_TO_EA_REPLAN_2026_08_03.md` row 6 (line 52: "bring Plan 3's five gate questions verbatim", with its recommendations — objective-shaped, not a region race; two to three paths; the branch irreversible; mark the triumph and continue), `docs/ROADMAP.md` rows 12–13 (what VP-1 and VP-2 own, the churn count corrected to 20 files / 97 lines), `docs/NATION_AGENDAS_SPEC.md` (the substrate the AI's designs use — §9 names this pass), `docs/GAME_END_SPEC.md` (`record_ending`, the Verdict, the Imperial Peace, mark-and-continue), `docs/DESIGN_REFINEMENT.md` WO-D4(b) and the SF-ECON-1 row, and the feedback rules in memory (history with teeth, expansions welcome but fix conservatively, diplomacy is never typed).

Scope — the design is the gate's; rule it, measured, and flag any reversal of a user ruling:
0. **The user's rule (October 20, 2026): diplomacy is never typed.** Every act a design asks of the player has a UI control on an existing screen.
1. **Research, then rule:** Plan 3's five questions verbatim; what the designs are (history-first — the Rhine, Italy, the Continental System, humbling a court; each an objective on the nation-agendas substrate with its progress on the Balance of Europe and the morning dispatch, and a reward on completion); the two or three paths and the irreversible branch; how the decisive-peace triumph sits beside the Congress of Paris and the Verdict (GE's `record_ending`, mark and continue); and the two parked ideas it absorbs (WO-D4(b) winning by economic dominance; SF-ECON-1 "Acts of the Empire", a gold road into the designs). Record the gate (a spec, `docs/VP1_DESIGNS_SPEC.md` or the owning spec's section) before any build.
2. **Size the build at the gate** (the row says three parts): name each part's done-when — the designs playable and pinned through the real endpoints, a commanded 40-turn arm completing one design and the triumph recording, the series moved re-pinned with this row named, the store page's entry condition (c) read met.
3. **Build part 1 if it fits**, else hand it to the next session with this file overwritten.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this session or heading the next); a change that reaches the AI or the backend runs the attribution arms with `BASELINE_SERIES` byte-identical or every movement attributed (count the reach); the Godot parse harness for every `.gd` changed; edit CRLF files with a script that preserves line endings. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when VP-1's gate is recorded, the build is sized into named parts with their done-whens, STATUS ▶ NEXT UP names what follows, and this file is overwritten for it.
