# NEXT SESSION PROMPT — Pre-Deploy S14f part 1: the re-measure's rows — the P1, the four rulings, the P2s

> Overwritten each time a session hands off. Current hand-over: **October 24, 2026, after S14e — DD-B's re-measure —
> MEASURED; S14e COMPLETE, the done-when NOT met, S14f sized 2.0** (`docs/audits/DD_B_RE_MEASURE_2026_10_24.md`;
> `SYSTEMS_REFERENCE.md` §149 and §115.3; commits through the hook — `git log -5`).
>
> **What the last session delivered:** three fresh players (the brief verbatim, nothing else) played conquest,
> diplomacy-first and the sea to Turn 21 in the real client on the DD-B instrument — 1,149 actions, 0 script errors.
> Their 35 rows were traced to file:line, de-duplicated and read by the one metric tool: **35 causes, 5.8 rows per 10
> turns (conquest 6.5, diplomacy-first 4.5, the sea 7.0), 1 P1** — the done-when (under 5, 0 P1) missed by one P1 and
> five causes; the first measure read 11.5 and 3 P1, and none of its 69 causes returned. Every row is filed and homed:
> `BUG_FIXES.md` §S14E (S14E-1 … 35, OPEN, owner S14f) and `DESIGN_REFINEMENT.md` §S14E (S14E-D1 … D4, the design
> halves, each with a recommendation). The instrument gained four corrections (§115.3) and `tools/dd_b_metric.py`.
>
> **Traps the last session paid for:**
> - **A line typed while a modal holds the command line is never sent** (`ok: false`, "not taking orders now") — the
>   judge now skips them; the client's own silence there rides S14E-21.
> - **The Bash tool's heredoc trap bit twice** (a `\n` in a string became a newline; a patch with `\"` died with
>   "unexpected EOF"): write every patch script with the Write tool and run it by path, assert every anchor's count.
> - **Narrow a judge phrase only after** re-classifying the 4,350 census orders AND re-reading every committed HOLD
>   arm (`command_c3_hold_orders` with both `score_hold_*.json` scripts).
> - **`dd_b_play.py export` keeps stale frames** after a re-judge drops a row — delete the orphan.
> - **The settlement's legitimacy tier reads the whole package** for every court (`settlement_baseline.py:2171-2185`,
>   `settlement_scoring.py:2453-2468`); the bilateral armistice is typed by the pair score on the counsel's road and by
>   the side sum in the preview (`diplomatic_templates.py:4340`) — the 44-vs-24 row.
>
> **For the user before part 1 (not blocking — the session builds the recommendations unless overruled):** the four
> rulings S14E-D1 … D4 (`DESIGN_REFINEMENT.md` §S14E); a third measure after S14f (recommended, 1.0). Also theirs:
> S14d's A1 as applied, UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1.
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14f part 1 — the re-measure's rows: the P1, the four rulings' builds, the fourteen P2s — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/PRE_DEPLOY_PLAN.md` §2 row S14f; `docs/audits/DD_B_RE_MEASURE_2026_10_24.md` (the measure — §4 the P1, §5 the shape, §8 where the rows go); `BUG_FIXES.md` §S14E (every row's cause, sightings, decided fix, test name); `DESIGN_REFINEMENT.md` §S14E (S14E-D1 … D4 with recommendations); the records `docs/audits/dd_b/{conquest,diplomacy,sea}_2026_10_24/summaries.md` and the cited frames when a row's screen matters; `SYSTEMS_REFERENCE.md` §149, §115 (the instrument), §116–§118 and §132 (what S13b built — the siblings these rows name), §127.1 (ruling J), §123.3 (F81's pass); CLAUDE.md's Golden Rules (1, 5, 9, 10).

Scope (the row, part 1): **S14E-1 (the P1) with S14E-D1's build as recommended** — the first step of a TYPED march that meets an enemy asks, every personality alike (one modal, the muster shown, nothing spent; the aggressive marshal argues for the attack in his own line; `attack anyway` runs today's attack, `go around` re-plots the lawful road; a standing order's later contacts keep today's rule; the AI's side and delegation-inferred orders unchanged) — **then the other three halves as the user rules them, the recommendations by default** (S14E-D2 the legitimacy tier reads the court's own slice — on the series arms, the moved pins named; S14E-D3 the table's shut-out price kept and stated before the click, the grievance labelled with its Make Amends; S14E-D4 a floor on the war title's ground rung), **then the fourteen P2s S14E-2 … 15** in the ledger's order: the campaign pay priced in the muster and the what-if (2); the concessions wizard's exits (3); the peace preview's sanctuary line and the what-if's `field_on_peace_soil` (4); the war-purpose card and the Cabinet page on a rump, the elimination line (5); the legitimacy blocker's named clause and the dial's refusal (6); the End Turn gate's army line (7); one armistice score across the wizard row, the roads line, the preview and the send (8); the mission row's earned / shocks / paused (9); the shut-out price stated (10); the counsel's lever for an ally's slide (11); the muster's floor and bad day, coordination priced per outcome (12); `camp_leave_line` on the march reply (13); `fleet_action_forecast` on the Diversion's card (14); `formations.road_notes` at every point of action on the Ireland road (15). Each row: reproduce on the shipped board first, fix, pin (`tests/test_s14f_the_remeasure_rows.py::TestS14E<n>`), then the sibling sweep (the other courts, dialogues, popups, roads; the AI's side) — every sibling found filed as `S14E-X<n>` in §S14E and fixed in the part or heading part 2. `BASELINE_SERIES` byte-identical on every arm except where a ruling moves it consciously, the moved pins named. Part 2 (a later session): the twenty P3s S14E-16 … 35 and the closing re-play of every sighting on the DD-B instrument.

Done when: S14E-1 … 15 and the part's siblings are FIXED with their tests; the four rulings recorded in `DESIGN_REFINEMENT.md` §S14E as built (or as the user ruled); `SYSTEMS_REFERENCE.md` gains §150 (the part's rules); the census reads 20 open S14E (the P3s) and 0 S14E-X; STATUS ▶ NEXT UP names part 2 and this file is overwritten for it.

Rules: "diplomacy is never typed"; Golden Rule 1 (combat modifiers in `marshal.py` only), 5 (the AI uses the same executor), 9 (no open-ended deferrals), 10 (the sibling sweep); grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process (`tools/godot_parse_check.gd`, expect EXIT=0, commit the refreshed report); subagents on sonnet or haiku, never the orchestrator's model. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches; never start a DD-B engine while the hook runs.
