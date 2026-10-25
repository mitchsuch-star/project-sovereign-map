# NEXT SESSION PROMPT — the nine rulings, then Pre-Deploy S15 (UXR-4's marks and the deploy gate)

> Overwritten each time a session hands off. Current hand-over: **October 25, 2026, after S14f part 2 — the
> nineteen P3s, the twelve homed siblings, the seven rulings' builds, the part's sweep and the closing re-play —
> LANDED; S14f COMPLETE** (`SYSTEMS_REFERENCE.md` §151; commits through the hook — `git log -5`).
>
> **What the last session delivered:** S14E-16 … 30 and 32 … 35 FIXED; S14E-X6, X22, X25, X31, X33, X36 … X39, X51,
> X63, X67 FIXED; D5, D6, D8, D9, D10, D11 BUILT as recommended and **D7 BUILT on the user's yes** (the Cabinet's new
> "Open Settlement with Britain alone" row opens the table with the offer row at the counsel's sum); the part's own
> sweep filed **128 siblings S14E-X69 … X196 and fixed 114; the re-play and its sweep seventeen more (X197 … X213, one a P2 — the camp wash blackened the map), all fixed but X210 and X213 (rulings) and X211, X212 (homed to this session's head)** (one a crash in HEAD — X149, a killing barrage on an
> ally's soil returned no reply); **16 defect halves wait on nine rulings S14E-D12 … D20, and two one-line rows (X211, X212) wait on this session's head** (`DESIGN_REFINEMENT.md`
> §S14E); `BASELINE_SERIES` byte-identical on six arms (`tools/_s14f_p2_series_arms_final.json`), the Table lesson's
> probe re-run (Russia −39 → −25 by D5, Austria and the chip unchanged), the parse harness green on 80 scripts, the
> re-play of the 35 rows' sightings on the DD-B instrument (`docs/audits/dd_b/replay_2026_10_25/`, §151.17). The
> census: 0 open S14E, 18 open S14E-X (16 ruling-tied, 2 homed here), 9 UXR-4; 9 open design rows.
>
> **Traps the last session paid for:**
> - **Thirty agents in one checkout** need placeholder ids per agent letter and ONE renumbering pass at the merge
>   (`S14E-X<letter><k>` → `S14E-X<n>`, in the test files AND the source comments — part 1 left two of its own
>   placeholders in `counsel.py` and `naval.py`); two agents who choose the same letter collide (XW1 twice this
>   part), so hand out FINAL numbers from the second wave on.
> - **The Bash heredoc eats backslashes AND `\b`** (a regex `\b` became a backspace byte in a script written
>   through a heredoc); write every script with the Write tool and run it by path. `grep -c $'\r'` inside a `for`
>   loop counted lines, not carriage returns — audit line endings with a Python script.
> - **A text-mode `read_text()` + write flips a CRLF file to LF** (and an agent's editor flipped two `.gd` files and
>   `objection_dialog.gd` to CRLF); normalise against HEAD before the commit (`git status` says "CRLF will be
>   replaced by LF" for a flipped working copy).
> - **`CLAUDE.md` stands at 61,989 of 62,000 LF-folded bytes** — every edit to its Current Phase must give back
>   the bytes it takes.
> - **The MM arm never bites on the passive run** (an AI lead's outcome set is None by design, and a passive France
>   attacks only on the glory gate's judgment): a seam whose reach is 0 is recorded as such, never passed off as a
>   byte-identity.
>
> **For the user (not blocking — the session builds the recommendations unless overruled):** the nine rulings
> S14E-D12 … D20 (`DESIGN_REFINEMENT.md` §S14E, each with a recommendation): D12 the defender's committed mean
> re-seated (moves the AI's muster price — arms), D13 an AI court's downgrade costs it with every court, D14 the
> stored pair war scores recomputed after a battle or a capture (arms), D15 subjugation quoted first, D16 a fleet
> action restarts Europe's fuse, D17 a "how do I …" line that names no section gets a section index (overturns
> DDB-48's letter), D18 the notice rail filled at boot without the bells, D19 ONE chest (the treasury less the
> recurring payments owed) for every lump gold verb and the AI's own buy-off (arms), D20 a drawn battle counting as contact for the AI's peace gate (arms). Three calls taken under the
> standing delegation and recorded for the user's eyes: S14E-X110 (a REASSURE_ALLY mission ends when its alliance
> lapses or breaks), X118 (every field battle restarts the fuse — the AI's clock too), X157 (the Congress sweetener
> and the buy-off verb refuse on the chest their words quote). **A third measure** stays the user's call
> (recommended, 1.0 — the diplomacy road already met the done-when; a measure after S14f reads the build the testers
> get). Also theirs: S14d's A1 as applied, UXR-4 at their monitor, the code-signing certificate, AO's three
> questions, SF-NAV-1-D1.
> Paste everything below the line as the opening message of a fresh session.

---

The nine rulings' builds, then Pre-Deploy S15 — UXR-4's marks and the deploy gate — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/PRE_DEPLOY_PLAN.md` §2 rows S14f (COMPLETE) and S15; `SYSTEMS_REFERENCE.md` §151 (part 2's rules — the seams, the one chest, the one HUD sync, the booked writes, the fuse) and §150; `DESIGN_REFINEMENT.md` §S14E (D12 … D20 with recommendations; the user rules at the head); `BUG_FIXES.md` §S14E (the sixteen ruling-tied rows S14E-X76, X77, X98, X101, X108, X120, X130, X142, X155, X188, X189, X190, X195, X196, X210, X213 — each names its design half and its test class; and the two homed rows X211, X212 with their one-line fixes); `docs/UX_UI_REVIEW_PLAN.md` §UXR-4 (the nine marks for S15's head); `docs/PLAYTESTING.md` (the DD-B instrument; the re-play's crafted saves); CLAUDE.md's Golden Rules (1, 2, 5, 8, 9, 10).

Scope: **first, the two homed rows X211 and X212 (one-line fixes, pinned), then the nine rulings as the user rules them, the recommendations by default** — D12, D14, D20 and D19's AI half on the series arms (`tools/_s14f_p2_series_arms.py`'s pattern, chained from `_s14f_p2_series_arms_final.json`; the moved pins named), D13 through the ONE `execute_downgrade`, D15 the `_quote_instrument` channel with `vassal.subjugation_quote` (the ~30 driven files confirm), D16 a stamp at the fleet resolver's start, D17 the section index in `help_topics` / `meta_executor`'s DDB-48 block (flip DDB-48's pin consciously), D18 `/test` carrying `notifications` with a silent first fill; each defect half's test class appended to `tests/test_s14f_the_remeasure_rows.py`; the sweep after each (Rule 10 — new siblings filed as S14E-X195 … and fixed in the slice). **Then S15's head:** the nine UXR-4 marks (`UX_UI_REVIEW_PLAN.md` §UXR-4; the user's eyes at 5120×1440) read and fixed; **then the deploy gate** per `PRE_DEPLOY_PLAN.md` §2 S15: the census at 0 OPEN defect rows (`tools/defect_census.py --open`), the release build signed with the user's certificate (owed by the user), the clean-machine run; the user's call on a third DD-B measure before or after the build.

Done when: every S14E-X row is FIXED with its test (the census 0 open S14E-X); the nine rulings recorded in `DESIGN_REFINEMENT.md` §S14E as built (or as the user ruled); `SYSTEMS_REFERENCE.md` gains §152 (the rulings' rules); the UXR-4 marks FIXED; the parse report refreshed and committed (never with `--log-file`); STATUS ▶ NEXT UP names the deploy (or the third measure, as the user calls it) and this file is overwritten for it; then the commit is pushed.

Rules: "diplomacy is never typed"; Golden Rule 1 (combat modifiers in `marshal.py` only), 2 (every number to Godot an `int()`), 5 (the AI uses the same executor — a change on its path rides the series arms), 8 (no per-region scans in hot paths), 9 (no open-ended deferrals), 10 (the sibling sweep); grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process (`tools/godot_parse_check.gd`, expect EXIT=0, commit the refreshed report — never pass `--log-file`); the code-health ratchet (`tests/test_code_health_ratchet.py`: levers ≤ 231, functions over 500 lines ≤ 28, `CLAUDE.md` ≤ 62,000 LF-folded bytes — it stands at 61,989); subagents on sonnet or haiku, never the orchestrator's model; hand agents FINAL row numbers, renumber nothing at the merge. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches; never start a DD-B engine while the hook runs.
