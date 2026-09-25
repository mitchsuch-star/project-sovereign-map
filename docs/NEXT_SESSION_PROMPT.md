# NEXT SESSION PROMPT — THE RELEASE BUILD (ROADMAP 10): part 1 un-parked, the export, the clean-machine run

> Overwritten each time a session hands off. Current hand-off: **September 25,
> 2026.** Row EP is COMPLETE through GE-V (the commit that carries
> `ENDGAME_PLAN.md` §6's GE-V landing record): the played reach measured and
> found not on the road (`hold_titled` 45, GEV-D1 filed for the user), GE-D1
> and GE-D2 both ruled and built, a P1 subjugation hole closed. Pushed, hook
> green. The next slice is the release build — the plan's next line after GE-V.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Row: THE RELEASE BUILD (ROADMAP position 10) — un-park part 1, finish the export, run it on a clean machine, and hand the user a zip a stranger can unzip and play in mock mode. Commit and push when done.** Work directly on master per `CLAUDE.md`'s workflow; read its Golden Rules first.

**Repo state:** master (the GE-V commit), pushed, suite green. Routing = `docs/STATUS.md` ▶ NEXT UP (top block) → `docs/ROADMAP.md` position 10 → the September 23 plan block in STATUS ("THE PLAN") for the build's own contract.

## Reading order

1. `docs/STATUS.md` ▶ NEXT UP — the top block and the "THE PLAN — September 23, 2026" block (the build's part 1 is written and SAVED: the local `git stash` "release-build part 1 …" and the committed patch `deploy/parked/release_build_part1.patch`; apply the patch first).
2. `docs/ROADMAP.md` position 10 (the shippable build) and position 14 (the keys ship — call C1).
3. `docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md` §9 + the pre-build fix pass entry in STATUS (August 15, 2026): launcher mock-default + health poll, cheats gated on explicit debug, saves under `%APPDATA%\InkAndIron\saves` when frozen, README_TESTER.
4. `deploy/` — the existing pipeline (predates the July-18 SDK migration; regenerate its spec) and the March-10 build that proves the export runs end to end.
5. `docs/PLAYTESTING.md` (Mode B on `SOVEREIGN_PORT=8006` for the live-key smoke; the driver's new `--settlement` / `--decline-from` dials).

## The contract

- **Part 1 (parked):** PB-1's fix — the frozen server could not find `europe_1805.json` because PyInstaller's entry-script `__file__` is `_internal\main.py` — the runtime log + transcript, the build stamp, the API-key check + `key_status` + parser notice (keys SHIP), `launch.bat`, the help/debug copy. Apply `deploy/parked/release_build_part1.patch`, reconcile against master (GE-1..GE-V landed since), commit it as its own step.
- **The rest:** boot help + README + `build.bat` (frozen boot + release export) + the verify JSONs in the `.pck` + tests + the live-key smoke → the clean-machine run → the user uploads to itch.io.
- **Done when:** a stranger unzips it and plays in mock mode; the frozen server boots the 1805 campaign; the Godot export carries every JSON the boot reads; the licence notices ship (FA-43/FA-N84).

## What GE-V leaves the build

- `hold_titled` is **45** (`congress.HOLD_TITLED` + `europe_1805.json`); the Congress fixtures were regenerated.
- **VP-M1 "The Fortunes of War"** is live on both boards (`fortunes_of_war.py`, `SYSTEMS_REFERENCE.md` §67): a wounded marshal cannot attack for 3 turns; a general may be killed (1%). The Godot client renders the card's `is_wounded` / `wounded_until_turn` only through whatever the marshal card already shows — **no `.gd` was touched**; the release build should confirm the wound reads on the card (a "WOUNDED — until turn N" line on the marshal card is the one client touch owed, if the card does not already surface `retreat_recovery`-style status generically).
- `GUARD_SPENT_FLOOR` 1,000 — the Emperor is asked before the fatal battle.
- `vassalize <court>` needs the court BEATEN.
- **Open for the user (rulings, not sessions):** **GEV-D1 "The Road to Forty-Five"** (`DESIGN_REFINEMENT.md` — the two cheap reach levers: the muster preview quotes the EXPECTED arrival; a garrison default on the coast; then re-measure), the in-game feel of the Congress surfaces and the end screen's registers (frames in `docs/audits/IQ10_*_2026_09_25.png`), GEV-5/GEV-6 (two Congress copy nits).

## Gates

- The four-file rule on every slice (`STATUS` ▶ NEXT UP, the owning spec's landing record, the rows disposed, `CLAUDE.md` LIVE STATE). Overwrite this prompt file at hand-off.
- `BASELINE_SERIES` + M1–M7 byte-identical unless a mechanic moves (none should in a build slice); the mutation sweep if code changes.
- The full suite runs in the pre-commit hook (~17 min) — commit in the background and read the log; stage by name.

## Hazards (verbatim constraints)

The Bash tool mangles quotes and backslashes in heredocs — write scripts with the Write tool and run them by path; files in this repo have MIXED line endings — an exact-string edit must try both; `PYTHONIOENCODING` is forbidden; every `/command` staging under the suite needs `tests._chip_census.board_env(monkeypatch)` and a fixture that restores `M.world` / `M.game_state["world"]` / `M.parser`; the campaign log's type count is **168** (`marshal_wounded`); never run anything beside `tools/mutation_sweep.py`; a user's live game may hold port 8005 — test on `SOVEREIGN_PORT=8006`; the scratchpad path's session id has a near-twin — check `ls` before writing there.

## Finish

Commit, `git push origin master`, then report where we are and what the next session opens (Updates 1–5 in the plan's order; Update 1 also carries GEV-D1's levers if the user rules for them).
