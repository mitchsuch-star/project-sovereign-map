# NEXT SESSION PROMPT — THE RELEASE BUILD (ROADMAP 10): part 1 un-parked, the export, the clean-machine run

> Overwritten each time a session hands off. Current hand-off: **September 25,
> 2026, after VP-R1 "The Road to Forty-Five"** (the GEV-D1 follow-on, taken
> ahead of the build by the user's direction — landing record
> `DESIGN_REFINEMENT.md` GEV-D1, probes memo `docs/audits/VP_R1_PROBES_2026_09_25.md`,
> rules `SYSTEMS_REFERENCE.md` §68). Row EP is COMPLETE through GE-V + VP-R1.
> Pushed, hook green. The next slice is the release build — the plan's next
> line.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Row: THE RELEASE BUILD (ROADMAP position 10) — un-park part 1, finish the export, run it on a clean machine, and hand the user a zip a stranger can unzip and play in mock mode. Commit and push when done.** Work directly on master per `CLAUDE.md`'s workflow; read its Golden Rules first.

**Repo state:** master (the VP-R1 commit), pushed, suite green. Routing = `docs/STATUS.md` ▶ NEXT UP (top block) → `docs/ROADMAP.md` position 10 → the September 23 plan block in STATUS ("THE PLAN") for the build's own contract.

## Reading order

1. `docs/STATUS.md` ▶ NEXT UP — the top block and the "THE PLAN — September 23, 2026" block (the build's part 1 is written and SAVED: the local `git stash` "release-build part 1 …" and the committed patch `deploy/parked/release_build_part1.patch`; apply the patch first).
2. `docs/ROADMAP.md` position 10 (the shippable build) and position 14 (the keys ship — call C1).
3. `docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md` §9 + the pre-build fix pass entry in STATUS (August 15, 2026): launcher mock-default + health poll, cheats gated on explicit debug, saves under `%APPDATA%\InkAndIron\saves` when frozen, README_TESTER.
4. `deploy/` — the existing pipeline (predates the July-18 SDK migration; regenerate its spec) and the March-10 build that proves the export runs end to end.
5. `docs/PLAYTESTING.md` (Mode B on `SOVEREIGN_PORT=8006` for the live-key smoke; the driver's `--settlement` / `--decline-from` dials).

## The contract

- **Part 1 (parked):** PB-1's fix — the frozen server could not find `europe_1805.json` because PyInstaller's entry-script `__file__` is `_internal\main.py` — the runtime log + transcript, the build stamp, the API-key check + `key_status` + parser notice (keys SHIP), `launch.bat`, the help/debug copy. Apply `deploy/parked/release_build_part1.patch`, reconcile against master (GE-1..GE-V and VP-R1 landed since), commit it as its own step.
- **The rest:** boot help + README + `build.bat` (frozen boot + release export) + the verify JSONs in the `.pck` + tests + the live-key smoke → the clean-machine run → the user uploads to itch.io.
- **Done when:** a stranger unzips it and plays in mock mode; the frozen server boots the 1805 campaign; the Godot export carries every JSON the boot reads; the licence notices ship (FA-43/FA-N84).

## What VP-R1 leaves the build (read `SYSTEMS_REFERENCE.md` §68)

- **The shut-out line is 50%** (`congress.CS_SHUTOUT_PCT` and `europe_1805.json campaign_end.cs_shutout_pct`; the two Congress fixtures regenerated). **A save keeps the line it was authored under** — a campaign begun before VP-R1 keeps 60 in its `campaign_end` until a new campaign; the build ships fresh boots, so nothing to do, but do not "fix" an old save's 60 into 50 without a migration decision.
- **Four levers, all up:** `combat_executor.MUSTER_ROWS_NAME_THEIR_ODDS` (display), `movement_executor.RAIDING_PARTY_HOLDS_NO_HOMELAND` (a corps under 5,000 holds no homeland — the series mover, re-recorded once), `jealousy.GLORY_ATTACK_OBEYS_THE_ODDS` (both boards), and the objection's `description` (stamped by the executor, preferred by `objection_dialog.gd`). One `.gd` touched (`objection_dialog.gd`); parse harness EXIT=0 and a windowed boot 0 SCRIPT ERROR at the VP-R1 commit.
- **The muster preview's new copy** ("expect about X with the corps likely to arrive, up to Y if all march"; per-row odds and the SUPPORT lever) and the objection's "(Trust him and he will attack Archduke Charles at Tyrol instead.)" are owed an in-game look by the user — display only, no build blocker.
- **`test_a_played_arm_reaches_forty_five_by_turn_forty` is a STRICT xfail** over the committed `titled.json` records beside the two re-measure tails (`docs/audits/playtest_digests/vpr1-played-{a,b}-tail`). It turns RED the day an archived road reaches 45 — then retire the xfail and re-record. Do not "fix" it by loosening.
- **Open for the user (rulings, not sessions):** the deeper reach gate (§68.6 — an action point for every corps, the supply cap on ally soil, the capture cascade, the harness's `--diplomacy accept` signing every armistice mid-conquest); VP-R1-X1 (`BUG_FIXES.md` — the objection's attack alternative can name an ALLY's corps in range; the executor refuses it); the in-game feel of the Congress surfaces and the end screen's registers (frames in `docs/audits/IQ10_*_2026_09_25.png`); GEV-5/GEV-6 (two Congress copy nits).

## Gates

- The pre-commit hook runs `ruff check backend/` + the full suite (~20 min): commit in the BACKGROUND and read the log; never `--no-verify`.
- Any `.gd` change → the parse harness (`Godot…exe --headless --quit --path godot-client/project-sovereign --script ../../tools/godot_parse_check.gd`, EXIT=0; commit the refreshed `tools/godot_parse_report.json`) and a windowed boot with `--audio-driver Dummy --log-file <abs path>` grepping `SCRIPT ERROR` (expect 0).
- `BASELINE_SERIES` + M1–M7: byte-identical unless attributed by a flip experiment (`tools/_vpr1_series_arms.py` is the latest pattern).
- The four-file rule on every landing: STATUS ▶ NEXT UP, the landing record, the rows disposed, `CLAUDE.md` LIVE STATE.
