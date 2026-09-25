# NEXT SESSION PROMPT — GE-3 "The Congress of Paris": the summons, the recognition table, the eight-turn sitting, THE IMPERIAL PEACE

> Overwritten each time a session hands off. Current hand-off: **September 25,
> 2026.** Row EP's GE-2 "the client" is landed (the commit that carries
> `ENDGAME_PLAN.md` §6's GE-2 landing record): the end screen with its four
> registers and the exile epilogue, the clock line on three surfaces from one
> source, the driver's END SCREEN block and the four ending arms archived,
> `tests/test_ge2_the_client.py` (60, driven). Pushed, hook green.
> The next slice is GE-3, the victory arm — the mechanic the user asked for.
>
> Paste everything below the line as the opening message of a fresh session.

---

Row EP, the Endgame Program: **land GE-3 "The Congress of Paris" — `backend/game_logic/congress.py`, the `summon_congress` verb, the recognition table, the eight-turn sitting under pressure, THE IMPERIAL PEACE through the register GE-2 declared, the CONGRESS ledger tab and the war-room rows, the beats, the Pressburg and Premature driver arms. Commit and push when done.** Work directly on master per `CLAUDE.md`'s workflow; read its Golden Rules first.

**Repo state:** master (the GE-2 commit), pushed, suite green. The working tree is clean. Routing = `docs/STATUS.md` ▶ NEXT UP (top block) → `docs/ENDGAME_PLAN.md` (the routing authority for row EP; GE-2's landing record is in §6 after GE-1's) → `docs/GAME_END_SPEC.md` §7 (the proposal §8 records as RULED by the plan).

## Reading order

1. `docs/STATUS.md` ▶ NEXT UP, the top block.
2. `docs/ENDGAME_PLAN.md` §2 (THE CONGRESS OF PARIS — §2.1 the shape, §2.2 title, §2.3 the summons, §2.4 the table, §2.5 the sitting, §2.6 resolution, §2.7 the numbers, §2.8 the measurement before landing), §5 (E1 the Universal Monarchy), §6 (the GE-3 row is the contract; GE-1's and GE-2's landing records sit under the table), §8 (done-when items 2 and 3), §9.
3. `docs/SYSTEMS_REFERENCE.md` §64 (`province_title`, `titled_provinces`, the reconciliation — the Congress's substrate) and §65 (what GE-2 put on the wire and how the end screen is raised; the clock line's one source).
4. `docs/GAME_END_SPEC.md` §7.1–§7.5 (the rule "hold X for X", the title, the clock the player sees, the ending, global elimination) and §7.10 (never-do pins).
5. `docs/AI_INTENT_SPEC.md` §11 Stage C/D (the intent weights, the instrument transport, the paymaster) — the refuser pressure hooks ride them.

## What GE-2 hands GE-3

- **The register is declared and rendered.** `game_end.CAUSE_IMPERIAL_PEACE` (register `imperial_peace`, title THE IMPERIAL PEACE, cause line "Europe accepts the order of the French Empire.") is marked, never terminal; `record_ending(world, "victory", CAUSE_IMPERIAL_PEACE)` stamps it through the one seam and the client raises the gold card (Continue the reign / Retire to the Tuileries) from the end-turn road's `ending` with NO client change. GE-3 adds its own blocks to `build_campaign_summary` for that register — the four flags with SIGNED / SHUT OUT / GONE, the titled count, the sitting's eight turns as a strip, the final Moniteur line (ENDGAME_PLAN §4) — and `campaign_end.gd` renders them (the scene reads `summary`; add a block, keep the common ones).
- **The clock line has ONE source.** `fall.clock_line` / `fall.clock_lines` feed the end-turn banner (`main._add_fall_clock_lines`), the R screen (`dispatch_view.gd`), the Territories tab (`ledger.fall_clock`, `strategic_ledger._fall_clock_lines`) and the war room. §4's Congress gate line ("THE CONGRESS OF PARIS — 43 of 50 titled (7 held, unsettled: Vienna, Bohemia …) · summon from the Cabinet (F1)") and the sitting's clock join the same readers — compose them beside `clock_line`, ride them on the same payload keys (or a sibling `congress_clock`), never a second implementation per surface.
- **The end screen's discipline.** Every ending is stashed on arrival (`api_client.response_received` → `main._stash_ending`) and raised at control return; a cause the compact list names that the client has not shown is fetched off `GET /campaign_end`. A Congress beat that is NOT an ending (the summons, a court's answer, the dissolution) is a dispatch beat / popup, not an `endings` record — do not stamp it through `record_ending`.
- **The driver** prints the END SCREEN's blocks under each ending and stops on a marked ending with `--stop-on-ending`; the Pressburg and Premature arms (§2.8) are scripts under `tools/playtest_scripts/` and their digests are archived with `--archive`. The two GE-2 fixtures show the pattern for a STAGED starting state (`tools/gen_ge2_ending_fixtures.py`) if the Pressburg arm needs one.
- **Every response carries `game_state.endings`**; `GET /campaign_end` returns every ending with its summary; the Verdict at 44 still grades after THE IMPERIAL PEACE (D7).

## GE-3 — the contract (ENDGAME_PLAN §6 row, as ruled)

`backend/game_logic/congress.py` (`can_summon`, `summon`, `answer`, `price`, `tick`, `resolve`, `state_line`; ONE serialized `congress`), the `summon_congress` verb through the shared executor (2 DP + 1 admin; corpus rows; the wizard row with gate terms), the `recognition` proposal type + sweetener clause on the instrument transport, the refuser pressure hooks (intent weight, paymaster, alarm gate, Revanche weight), the recognition clause on the sue seam, the hold predicate, the dissolution, E1; the CONGRESS ledger tab + war-room rows; beats 1–4 + the Moniteur column + Talleyrand's rung; the Pressburg and Premature driver arms; `BASELINE_SERIES` re-recorded once (the pressure hooks are dormant with no Congress — attribution must show arm 0 byte-identical); `tests/test_congress_of_paris.py`. Done-when §8 items 2 and 3.

## Gates (every slice)

- The four-file rule (`STATUS` ▶ NEXT UP, `ENDGAME_PLAN.md` §6 + landing record, the rows disposed, `CLAUDE.md` LIVE STATE); `SYSTEMS_REFERENCE.md` gains §66; `SAVE_FORMAT_REFERENCE.md` for the one new serialized field. Overwrite this prompt file at hand-off.
- `tools/mutation_sweep.py` with 0 INERT at close (it mutates the tree in place — never run anything beside it).
- `BASELINE_SERIES`: GE-3 is one of the three slices allowed ONE re-record (D15) — a flip-experiment attribution with arm 0 byte-identical; M1–M7 byte-identical.
- Any `.gd` change: the parse harness (`tools/godot_parse_check.gd` — add every touched script, scene and harness) and a driven boot of `main.tscn` (the GE-2 harness `tools/ge2_campaign_end_harness.gd` is the model for driving a card through the real client); IQ-10 frames via `tools/iq10_capture_payloads.py --only <group>` then `tools/iq10_run_captures.py --payload-dir <dir> --only <ids> --date 2026_09_XX`.
- The full suite runs in the pre-commit hook (~15 min) — commit in the background and read the log; stage by name.

## Hazards (verbatim constraints)

The Bash tool mangles quotes and backslashes in heredocs — write scripts with the Write tool and run them by path; files in this repo have MIXED line endings (some CRLF, some LF) — an exact-string edit must try both; `PYTHONIOENCODING` is forbidden; every `/command` staging under the suite needs `tests._chip_census.board_env(monkeypatch)` and a function-scoped fixture that restores `M.world` / `M.game_state["world"]` / `M.parser`; a `const` Dictionary is read-only at runtime in Godot 4; the campaign log's type count is 166 (`campaign_ending`) — a Congress beat type moves it and the five census pins; the terminal trims its scrollback past 100 messages, so a driven pin reads the LAST lines printed; the IQ-10 harness's `scroll_to` step brings a paragraph into the frame when the surface is long.

## Finish

Commit, `git push origin master`, then report where we are and what the next session opens (GE-V — the played campaign that measures the Congress arc, the D1 band, the naval pillar and the GE-D2 question; then the release build). Still open for the user: GE-D1 (the generals' mortality — recommended, not built), GE-D2 (the Eagle-Falls arm dies with no Guard question — measured by GE-2, the floor not built), the in-game feel of the end screen's four registers (`docs/audits/IQ10_CAMPAIGN_END_*_2026_09_25.png`) and of F3's surfaces.
