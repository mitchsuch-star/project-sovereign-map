# NEXT SESSION PROMPT — Pre-Deploy S14e: DD-B's re-measure (three fresh players in the client)

> Overwritten each time a session hands off. Current hand-over: **October 24, 2026, after S14d part 3 — the walk
> and the close — LANDED; S14d COMPLETE** (`docs/TABLE_LESSON_SPEC.md` §13–§17; `SYSTEMS_REFERENCE.md` §148–§148.11;
> commits through the hook — `git log -5`).
>
> **What the last session delivered:** S14d part 2's Table lesson (the board tuned by `tools/_table_board_probe.py`,
> seven cards, the settlement door, 15 driven pins) and part 3 — the Mode C walk on the DD-B instrument (the Table played
> to its hand-off by the buttons alone; the Danube's twenty cards reached; the campaign's six turn-1 first-open lines each
> once, then gone on turn 2 — records `docs/audits/dd_b/table_walk_2026_10_24/` and `campaign_lines_2026_10_24/`), the
> frozen build's smoke booting every School scenario, and the rows S14D-X18, X42 (the Throne of Holland speaks for the
> deputation under Ver Huell — a new `named` moment voice), X43, X49, X50 and the walk's find X51 (the Cabinet's mission
> row before its first tick) FIXED. The census reads 0 open S14D rows; 9 UXR-4 rows wait for S15.
>
> **Traps the last session paid for:**
> - **A running sandbox backend reads the scenario JSON from disk at every `/new_game`** — edit `europe_1805.json`'s
>   content under it and the next BEGIN fails validation (the client prints "New campaign failed: …"); restart the pair.
> - **The DD-B instrument's keys obey the client's own rules:** a focused command line swallows `key T`; a modal (the
>   battle diorama, the mailbox panel) swallows `key F1` and the top bar's menu icon — close it first (`key Escape`) or
>   click the top bar's own buttons (`click Ledger (T)`; note `Diplomacy (D)` is the Diplomatic Ledger, the Cabinet is
>   `⚖ The Cabinet` / F1). `act click <words>` takes bare words — no inner quotes.
> - **The Cabinet's first-open line is drawn on the court LIST only** (part 1's rule at Interface Scale 2.0); a door that
>   opens a court's page shows none — by design, recorded.
> - **A Python heredoc through the Bash tool halves backslashes AND can silently write nothing** — write patch scripts
>   with the Write tool, run them by path, assert every anchor's count.
> - **The moments validator caps a letter's `record` at 240 characters** and the staged deck fixture
>   (`tests/fixtures/moments_block.json`) must equal the shipped deck entry for entry.
>
> **Nothing waits on the user before S15** (S14d's A1 as applied — mounts in the campaign, signs in the lesson; the
> re-size 1.5 → 2.5 — UXR-4, the code-signing certificate, AO's three questions, SF-NAV-1-D1 are theirs to overrule).
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14e — DD-B's re-measure — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/PRE_DEPLOY_PLAN.md` §2 rows S14e and S14f; `SYSTEMS_REFERENCE.md` §115 (the DD-B instrument — the engine side `tools/dd_b_client.gd`, the player's side `tools/dd_b_play.py`, its traps §115.3); `docs/audits/dd_b/PLAYER_BRIEF.md` (the players' brief) and `docs/audits/DD_B_FRESH_EYES_2026_10_14.md` (the first measure's method and its rows); `docs/audits/dd_b/metric.json` and `causes.json` (the first measure's figures); `BUG_FIXES.md` §DD-B (what the first measure filed and S13b fixed); `docs/PLAYTESTING.md` §Mode C.

Scope (the row): **three fresh players, the same brief and roads (conquest, diplomacy, sea), 20 turns each IN THE CLIENT on the DD-B instrument**, reading the game Round 0 will meet — the DD-B fixes, the rulings, VP-1, the events, the table lesson and the first-open lines. Each player is a fresh-mind agent given ONLY the brief and the road, acting one action at a time through `dd_b_play.py act` (never a ledger, never the code); the judge classifies every typed line; every confusion is filed with `row` by DD-B's rule (did / expected / saw, the frame cited), then de-duplicated and homed. One engine at a time (never while a hook runs); the sandboxed backend from 8006; export each run to `docs/audits/dd_b/<road>_2026_<date>/`; the metric beside the first measure's (`metric.json`: rows per 10 turns, P1 count, the typed-line misread rate).

Done when: three 20-turn runs are recorded and exported; every row filed, de-duplicated and homed with an owner; the measure reads **under 5 rows per 10 turns and 0 P1** — then STATUS ▶ NEXT UP names S15 and this file is overwritten for it; otherwise every new row is homed to **S14f (the re-measure's rows)**, sized at the close, P1s first, and this file is overwritten for S14f.

Rules: the players see only what a player sees; a run is never steered by a reading of the code; the sibling sweep after every fix (CLAUDE.md Rule 10); "diplomacy is never typed"; grep-verify any agent's bulk `.gd` edits and run the Godot parse harness via Start-Process (`tools/godot_parse_check.gd`, expect EXIT=0, commit the refreshed report). Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
