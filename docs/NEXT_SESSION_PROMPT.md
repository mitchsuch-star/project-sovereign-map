# NEXT SESSION PROMPT — UPDATE 1: PR-D1b + the PB-7 doc housekeeping

> Overwritten each time a session hands off. Current hand-off: **September 25,
> 2026, after THE RELEASE BUILD (ROADMAP position 10) landed** — landing
> record `ROADMAP.md` position 10, rules `SYSTEMS_REFERENCE.md` §69, pins
> `tests/test_release_build_2026_09_25.py`. The zip
> `deploy/dist/ink_iron_<stamp>.zip` is on the dev PC (gitignored); the user
> uploads it to itch.io. Pushed, hook green. The next slice is Update 1 —
> the plan's next line (`docs/STATUS.md` ▶ NEXT UP, "THE PLAN — September 23").
>
> Paste everything below the line as the opening message of a fresh session.

---

**Row: UPDATE 1 — PR-D1b "the AI settlement offer at war-age 2" + PB-7 doc housekeeping. Commit and push when done.** Work directly on master per `CLAUDE.md`'s workflow; read its Golden Rules first.

**Repo state:** master (the release-build commit), pushed, suite green. Routing = `docs/STATUS.md` ▶ NEXT UP (top block "THE PLAN — September 23, 2026": *Fix Updates, player reports re-order them: 1 PR-D1b + doc housekeeping → 2 CRT-3 + WO-32 → 3 L-D + CX5-L5-F2 + CQ-30 → 4 petition Antechamber B1 → 5 PR-D1c + PR-D1d*).

## Reading order

1. `docs/STATUS.md` ▶ NEXT UP — the top block, then the THE RELEASE BUILD block (what shipped, what is measured, what is open for the user).
2. `docs/DESIGN_REFINEMENT.md` PR-D1b (the row and its evidence: on the commanded arm, Britain's turn-3/4 settlement is accepted, all 7 war pairs end and Britain pays 1,358g; after that the enemy makes 0 attacks for 36 turns). ⚠ **The gate is P1's own coalition break-ranks clause, NOT `effective_peace_threshold`** (`docs/STATUS.md` "THE PLAN" block, and the September 23 memory).
3. `docs/BUG_FIXES.md` PB-7 — the doc-drift census: 9 rows that say OPEN but are closed at HEAD (CQ-31, NPC-8, NP-X4, EAS-1, UI-2d-1, EWC-F1, WIN-H5, the NV-P1 wheel check, CA9-F3), ROADMAP row 16's stale "only open soft-lock class", and ~45 rows with no live owner (NP-X1/8/9/10 naming the retired "CR-6 proper", the NPC tail, the CA9 tail, IQ1-5-1, econ question (c), VD-C, petition slices B1–B5). GR9: every ownerless row gets an owner row and a landing slice, or is struck with a reason.
4. `docs/PLAYTESTING.md` — Mode A (`tools/playtest_driver.py --diplomacy accept`) reproduces PR-D1b's board; the driver's `--settlement` / `--decline-from` dials.

## The contract

- **PR-D1b:** reproduce on the commanded arm first (the digest of a `--diplomacy accept` run: the turn-3/4 acceptance and the 36 quiet turns). Then build behind a lever, attributed by a flip experiment if `BASELINE_SERIES` moves. The four-file rule on landing.
- **PB-7:** docs only — mark the 9 closed rows with their closing evidence, give every ownerless row an owner, fix ROADMAP row 16. No production code.
- **Player reports re-order the Updates:** if the itch.io build produces a report before this session, its row jumps the queue (the plan's own rule).

## What the release build leaves behind (read `SYSTEMS_REFERENCE.md` §69)

- **The zip is built by `deploy/build.bat` alone** — stamp → PyInstaller → frozen smoke (`tools/release_smoke.py`, which PLAYS a turn on the exe) → release export → pack check (`tools/list_pck.py`) → zip. Re-run it for every build; never hand-copy an exe. `GODOT_EXE` overrides the editor path. `deploy/build_stamp.json` is generated and gitignored.
- **A frozen build's paths derive from imported modules, never from `main.py`'s `__file__`** (PB-1). If the server ever reads a NEW file at runtime, add it to the spec's datas AND derive its path from a module that mirrors the repo layout (region.py's idiom); the release smoke will catch a missed one because it boots the exe from a foreign folder.
- **The logs**: `%APPDATA%\InkAndIron\logs\server.log` + `transcript.jsonl` in the frozen build (or `INK_IRON_LOG_DIR`). A player report should carry both plus the build number (the main menu and the pause menu print it; launch.bat refuses a mismatched server).
- **The key section ships**: `/config/llm` checks a connected key (one free GET) and never installs a refused one; `key_status` states; a failed live parse is said once per session (`parser_notice`); the once-ever keyless hint is latched in `UiSettings` (`parser/hint_seen`). Under the suite every non-loopback connection is refused, so `_check_anthropic_key` reads `unreachable` there — tests monkeypatch it.
- **PB-2's rule is pinned:** README and boot-help examples EXECUTE on a fresh 1805 boot; `help`'s quoted examples are READ. A new example that the game refuses to parse, or that names a nation as a province, reds `tests/test_release_build_2026_09_25.py`.
- **Open for the user (not sessions):** upload the zip; the first outside launch is the no-Python confirmation; the in-game look at the new Settings copy, the menu's build line and the once-ever hint.

## Gates

- The pre-commit hook runs `ruff check backend/` + the full suite (~22 min at 26k tests): commit in the BACKGROUND and read the log; never `--no-verify`.
- Any `.gd` change → the parse harness (`Godot…exe --headless --quit --path godot-client/project-sovereign --script ../../tools/godot_parse_check.gd`, EXIT=0; commit the refreshed `tools/godot_parse_report.json`) and a windowed boot with `--audio-driver Dummy --log-file <abs path>` grepping `SCRIPT ERROR` (expect 0).
- `BASELINE_SERIES` + M1–M7: byte-identical unless attributed by a flip experiment (`tools/_vpr1_series_arms.py` is the latest pattern).
- The four-file rule on every landing: STATUS ▶ NEXT UP, the landing record, the rows disposed, `CLAUDE.md` LIVE STATE.
