# NEXT SESSION PROMPT — GE-2 "The Client": the end screen, its four registers and the exile epilogue

> Overwritten each time a session hands off. Current hand-off: **September 25,
> 2026.** Row EP's GE-1 "The Verdict and the Fall" is landed (`975f1f13`)
> with the user's three September 25 additions — the Emperor's death, the
> generals' death-odds memo, the exile story — AND its adversarial review
> round (`e5d67800`: 38 surviving findings, all fixed and pinned,
> `tests/test_ge1_review_round.py`) AND a verification round on those fixes
> (the commit after it, see `git log`: 27 more, all fixed,
> `tests/test_ge1_verification_round.py`). Pushed, hook green.
> The next slice is GE-2, the client half of the ending.
>
> Paste everything below the line as the opening message of a fresh session.

---

Row EP, the Endgame Program: **land GE-2 "the client" — `campaign_end.tscn` with the four registers, the exile epilogue on the Fall register, the clock line on three surfaces, and the driver arms that reach each ending. Commit and push when done.** Work directly on master per `CLAUDE.md`'s workflow; read its Golden Rules first.

**Repo state:** master (the GE-1 verification-round commit), pushed, suite green. The working tree is clean. Routing = `docs/STATUS.md` ▶ NEXT UP (top block) → `docs/ENDGAME_PLAN.md` (the routing authority for row EP; GE-1's landing record is in §6) → `docs/GAME_END_SPEC.md` (the spec).

## Reading order

1. `docs/STATUS.md` ▶ NEXT UP, the top block.
2. `docs/ENDGAME_PLAN.md` §4 (the screens, RULED), §6 (GE-2's row is the contract; GE-1's landing record sits under the table), §8 (done-when items 4 and 5).
3. `docs/SYSTEMS_REFERENCE.md` §64 — what GE-1 put on the wire and where.
4. `docs/GAME_END_SPEC.md` §2 R3 (keep playing after the Verdict; Load / Main Menu after the Fall), R4 (the end screen), R6 (saves).
5. `DESIGN_REFINEMENT.md` GE-D1 (the generals' mortality — the user's ruling), GE-D2 (the spent Guard → GE-V).

## What GE-1 hands GE-2 (the payload — do not recompute any of it in the client)

- Every response carries `game_state.endings` — the compact list `{kind, cause, register, title, cause_line, turn, calendar_label, terminal, tier, tier_title}` of every ending stamped. The end-turn road, `/load` and a `/command` that ended the war carry `ending` (the last one) with its full `summary`: `{register, title, cause_line, turn, calendar_label, nation, provinces_held, total_regions, totals, greatest_victory, worst_defeat, coalition_names, verdict: {tier, title, lines, closing, score}, epilogue?: {variant, paragraphs, facts}}`. `GET /campaign_end` returns every ending with its summary (re-opening the screen after a load).
- Registers: `fall` (crimson, terminal — the three causes `soil_or_sword`, `chains`, `eagle_falls`; the epilogue variants `captivity`, `abdication`, `funeral`), `humbled_peace` (crimson-grey, continue; epilogue variant `humbled`), `verdict` (parchment, continue). The fourth, THE IMPERIAL PEACE (gold), is GE-3's; build the scene to take it.
- The warning's structured `fall` key (`morning_dispatch.defeat_imminent_warning.fall.arms[]` — `{arm, title, turns, grace, turns_left, ticking, paused_by, falls_at_end_of_turn, exits}`) is what the clock line reads on the war room, the Strategic Ledger's Territories tab and the end-turn banner. `falls_at_end_of_turn` is null while the arm is paused (`paused_by` = `truce` / `captor`) — render "the clock stands still", never a date. Two more keys (verification round): `truce_ends` (`war`/`peace`/`""`) and `resuming` — a truce that ends in war THIS turn is a clock that ticks this turn, and it carries its fall date (`falls_at_end_of_turn`) and a `critical` severity; the arm's own sentence (`fall.arm_clock_sentence`) says "the truce ends this turn and the war resumes". A Fall's Verdict is ALWAYS the eclipse — the Fall register never renders another tier.
- **Every POST response of a fallen campaign carries `game_over` + `ending`** (the review round closed the war at `build_base_response`, so the popup, typed and objection roads carry it too, and the `/command` game-over guard's refusal does). **The death on the command road has NO dispatch and NO special edition** — the war ends inside the command and no end turn follows — so the end screen is the fall's ONLY surface there: GE-2 owns it (review finding #10; the pin is a driven `Napoleon, attack Mack` at `SOVEREIGN_DEATH_CHANCE_PCT = 100` that raises the funeral register from the `/command` response).
- A backfilled pre-GE-1 save's summary carries `record_since_turn` (the epilogue already says "(The record was kept from … only.)"); show the totals as "since" that date. The captor's offer popup carries `captor_terms: true` and a clause naming the release.
- Saves: a "Final — <date>" save exists after a Fall and sorts after every playable save; `/load` of it carries `ending` and `game_over`. The client's Continue takes `saves[0]`, which is already the playable one.

## GE-2 — the contract (ENDGAME_PLAN §6 row, as ruled)

`campaign_end.tscn/.gd` (CanvasLayer 122) with the four registers, raised from every end-turn flow, from `/load`, and from the ratify path (a Humbled Peace arrives on the settlement ratify response through `game_state.endings`) by the NA-6b stash-and-raise discipline — never blocking the turn; keep-playing after a marked ending (Continue), Load / Main Menu after the Fall with input disabled; the legacy `_show_game_over_screen` text kept as the fallback and de-legacied (no "13 regions"); the clock line on the three surfaces; the XR-1 parse harness + a driven boot of `main.tscn` with 0 `SCRIPT ERROR`; a Mode-A driver arm that reaches each fall and the Verdict (GE-1 measured them — the ambient historical seed dies on turn 31, the ambient ulm seed falls to the chains on turn 40, every arm that lives reaches the Verdict at 44); IQ-10 frames for all registers at both Interface Scales.

## Gates (every slice)

- The four-file rule (`STATUS` ▶ NEXT UP, `ENDGAME_PLAN.md` §6 + landing record, the rows disposed, `CLAUDE.md` LIVE STATE); `SYSTEMS_REFERENCE.md` gains §65. Overwrite this prompt file at hand-off.
- `tools/mutation_sweep.py` with 0 INERT at close (it mutates the tree in place — never run anything beside it).
- `BASELINE_SERIES` and M1–M7 byte-identical (GE-2 touches no mechanic).
- Any `.gd` change: the parse harness and a driven boot of `main.tscn`; IQ-10 frames via `tools/iq10_capture_payloads.py` then `tools/iq10_run_captures.py --payload-dir <dir> --only <ids> --date 2026_09_XX`.
- The full suite runs in the pre-commit hook (~15 min) — commit in the background and read the log; stage by name.

## Hazards (verbatim constraints)

The Bash tool mangles quotes and backslashes in heredocs — write scripts with the Write tool and run them by path; files in this repo have MIXED line endings (some CRLF, some LF) — an exact-string edit must try both; `PYTHONIOENCODING` is forbidden; every `/command` staging under the suite needs `tests._chip_census.board_env(monkeypatch)` and a function-scoped fixture that restores `M.world` / `M.game_state["world"]` / `M.parser`; a `const` Dictionary is read-only at runtime in Godot 4; the campaign log's type count is now 166 (`campaign_ending`).

## Finish

Commit, `git push origin master`, then report where we are and what the next session opens (GE-3 "The Congress of Paris" — the summons, the recognition table, the eight-turn sitting, THE IMPERIAL PEACE; then GE-V, the release build). Still open for the user: GE-D1 (the generals' mortality — recommended, not built), the in-game feel of F3's surfaces and F5's settlement header.
