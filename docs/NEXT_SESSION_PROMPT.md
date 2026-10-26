# NEXT SESSION PROMPT — Pre-Deploy S15: the user's walk, the signed build, the clean-machine run

> Overwritten each time a session hands off. Current hand-over: **October 25, 2026, after S14f p3 — the nine
> rulings D12 … D20 BUILT (and D21 / D22, the two the build found), the two homed rows and 40 siblings FIXED, S15's
> head LANDED** (`SYSTEMS_REFERENCE.md` §152; commits through the hook — `git log -5`).
>
> **What the last session delivered:** every ruling built as recommended under the standing delegation (two
> judgements against a row's letter, recorded: D12's ratio is a RATIO OF EXPECTATIONS, D14's `live_war_score_for`
> stays live and is pinned equal to the store at every stamp); S14E-X76, X77, X98, X101, X108, X120, X130, X142,
> X155, X188 … X190, X195, X196, X210 … X213 FIXED; the sweeps' S14E-X214 … X251 (38 FIXED, X235 closed by ruling,
> X246 by census); `BASELINE_SERIES` re-pinned and attributed to ONE ruling (D12 — the AI's muster price had never
> carried a coordination stamp; `tools/_s14f_p3_series_arms_final.json`, the D1 war-count band held); the driven arms
> hold their archives with every seam down; S15's head: the re-homed marks' decided fixes BUILT and re-shot
> (`docs/audits/uxr4_s15/`), UXR3-41's two boards RE-STAGED, PC-F46 / F47 FIXED, the signing seam wired
> (`deploy/build.bat`, `INK_IRON_SIGNTOOL_ARGS` / `SIGNTOOL`, `tools/release_smoke.py --expect-signed`). **The census:
> 1 open defect row (UXR3-2 — the user's mark; its decided fix is "none to the bar's order"), 0 open design rows.**
>
> **Traps the last session paid for:**
> - **The Bash heredoc eats quotes and `\b`** — it ate a quoted row text twice; write every script with the Write
>   tool and run it by path.
> - **A length pin on a live text drifts** — an agent pinned the manual at 22,573 characters; the merge read 22,572
>   (the manual splices live figures); a pin that a text IS the manual reads a band, never the character.
> - **A seam that is a class method** needs the driver's new `Class.method` form (`--seam
>   backend.commands.combat_executor:CombatExecutor._defender_mean_exact=None`).
> - **The IQ-10 capture runner's `--log-file` works windowed**; the crash is the headless parse harness's alone.
> - **Ten agents in one checkout, each on its own functions**, worked with Edit-only writes; the one collision was a
>   test (X198) whose draft used the dict dialect another agent had just retired.
>
> **For the user:** the walk at the monitor (below), the certificate, a third DD-B measure (recommended, 1.0 —
> before or after the build), S14d's A1 as applied, AO's three questions (`REFORMS_SPEC.md` §5a), SF-NAV-1-D1.
> Paste everything below the line as the opening message of a fresh session — AFTER the walk.

---

Pre-Deploy S15 — the deploy — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/PRE_DEPLOY_PLAN.md` §2 row S15; `SYSTEMS_REFERENCE.md` §152.11 (S15's head — what the walk reads) and §152.12; `docs/UX_UI_REVIEW_PLAN.md` §UXR-4 (the walk and what it inherits); `BUG_FIXES.md` UXR3-2 (the one open row) and the user's marks from the walk; `deploy/build.bat` (the signing seam) and `deploy/README_TESTER.txt`; `tests/test_s15_the_signed_build.py`; `tools/release_smoke.py`; CLAUDE.md's Golden Rules (9, 10).

Scope: **the user's marks first** — for each ✗ the user gave at the walk, the row's own decided fix lands (`BUG_FIXES.md` §UXR-3: UXR3-2's is the Cabinet chip moved to the head of the bar's right-hand cluster before the Admiralty chip, if the user wants it to lead; the two residuals of `docs/audits/uxr4_s15/README.md` — the sovereign card's order on the Generals' boot board, Austria's card on the doctrine board — get rows and fixes only on a ✗), re-shot on its frames at 1920×1080 and 5120×1440, the sweep after each (Rule 10); a ✓ closes the row with the user's words quoted in its status cell. **Then the deploy gate:** the census at 0 OPEN defect rows (`tools/defect_census.py --open`); the user's certificate in the environment (`INK_IRON_SIGNTOOL_ARGS`, and `SIGNTOOL` if the SDK's tool is off PATH); `deploy\build.bat` — the stamp, PyInstaller, the server SIGNED and verified, the smoke with `--expect-signed`, the Godot import and export, the client SIGNED and verified, the pack check, the zip; the clean-machine run (a machine with no Python, no Godot, no .env: unzip, `launch.bat`, SmartScreen raises no block, the tutorial's first card, one order, one end turn, Save and Load); the release record (`docs/audits/RELEASE_<version>.md`: the stamp, the zip's hash, the smoke's transcript, the clean-machine checklist). **If the user calls a third DD-B measure first,** run it per `docs/PLAYTESTING.md` (Mode C, three roads, the metric tool) on the build the testers get, home its rows, and the build waits for them.

Done when: every UXR-4 mark is ✓ (the rows closed in the user's words) or its fix landed and re-shot; the census reads 0 OPEN defect rows; the signed zip exists with its record; the clean-machine run is recorded; STATUS ▶ NEXT UP names Round 0 (the testers) and this file is overwritten for it; then the commit is pushed.

Rules: "diplomacy is never typed"; Golden Rule 9 (no open-ended deferrals), 10 (the sibling sweep); grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process (`tools/godot_parse_check.gd`, expect EXIT=0, commit the refreshed report — never pass `--log-file` to the harness); the code-health ratchet (`tests/test_code_health_ratchet.py`: levers ≤ 231, functions over 500 lines ≤ 28, `CLAUDE.md` ≤ 62,000 LF-folded bytes — it stands at 61,979); subagents on sonnet or haiku, never the orchestrator's model. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches; never start a DD-B engine while the hook runs; never write the certificate or its password into any file.
