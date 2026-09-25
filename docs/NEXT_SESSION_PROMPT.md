# NEXT SESSION PROMPT — GE-V "the played campaign": the Congress arc measured from the 1805 boot, the ending re-scored

> Overwritten each time a session hands off. Current hand-off: **September 25,
> 2026.** Row EP's GE-3 "The Congress of Paris" is landed (the commit that
> carries `ENDGAME_PLAN.md` §6's GE-3 landing record and its review-round
> addendum): `backend/game_logic/congress.py`, the `summon_congress` and
> `recognition_sweetener` verbs, the recognition table, the eight-turn sitting,
> THE IMPERIAL PEACE through the declared register, the CONGRESS ledger tab,
> the beats, the two arms (Pressburg wins turn 36 on 4 of 4 seeds, Premature
> loses on 3 of 3) pinned DRIVEN; a 69-finding review round, all fixed.
> Pushed, hook green. The next slice is GE-V, the measurement the ending was
> built to be measured by.
>
> Paste everything below the line as the opening message of a fresh session.

---

Row EP, the Endgame Program: **run GE-V "the played campaign" — play (or drive the client through) a France/1805 campaign from the boot to a Congress, measure the arc §2.8 asks for, publish the measurements, and re-score the pillar "the ending" (3.0 → target ≥ 7). Commit and push when done.** Work directly on master per `CLAUDE.md`'s workflow; read its Golden Rules first.

**Repo state:** master (the GE-3 commit), pushed, suite green. Routing = `docs/STATUS.md` ▶ NEXT UP (top block) → `docs/ENDGAME_PLAN.md` (§6's GE-V row is the contract; GE-3's landing record and review-round addendum sit after GE-2's).

## Reading order

1. `docs/STATUS.md` ▶ NEXT UP, the top block.
2. `docs/ENDGAME_PLAN.md` §2 (THE CONGRESS OF PARIS — read §2.4–§2.6 WITH the GE-3 landing record's amendments: only a peace signed while the Congress sits, or a beaten court's, latches; the peace dividend runs from the summons' own end turn; the War of the Congress only where `march_blocker` is empty), §2.8 (the measurement), §6 (the GE-V row; GE-3's landing record), §8 (done-when — items 2 and 3 are discharged on staged fixtures; the played reach is GE-V's).
3. `docs/SYSTEMS_REFERENCE.md` §66 (the Congress — what every surface reads and why), §64 (title), §65 (the end screen).
4. `docs/PLAYTESTING.md` (Mode A the driver, Mode C the client; the GE-3 arm commands).
5. `docs/DESIGN_REFINEMENT.md` GE-D1 and GE-D2 (the two rulings still open for the user).

## GE-V — the contract (ENDGAME_PLAN §6 row + §2.8)

- **The reach, played.** From the 1805 boot (not a staged fixture), a campaign that gets to 50 titled provinces and summons the Congress. §2.8: the Pressburg shape (Ulm → Vienna → a Pressburg that cedes and vassalizes → Hanover held twelve quiet turns → summon) reaches 50 titled between turns 25 and 40 and wins between turns 33 and 48. **If it cannot reach 50 by turn 40, `hold_titled` comes down to 45 before anything else moves.** Measure it on the driver (a scripted commanded arm; `--diplomacy accept`; three seeds) and, if possible, in the client (Mode C on `SOVEREIGN_PORT=8006`).
- **The table reads, the prices are true, the sitting is a crisis.** In the played sitting: at least one declaration of war (the War of the Congress, or a refuser's), one bill (the collective petition, a satellite's ask, the ×1.5 rentes), one flip (a court turned by a price the table named). Record each with its surface.
- **The D1 band.** The AI-3 ladder's council wars measured on a played board (arm (a) of the AI-V memo) — the Congress's refusal term is a new input to it.
- **The naval pillar.** The Continental System's SHUT OUT arm played: does closing 16 of 26 ports feel reachable; does a British landing on the mainland, answered, restore it?
- **GE-D2.** On any arm that reaches "The Eagle Falls", was the Guard's question asked before the fatal battle? Record the answer; the ruling is the user's.
- **The re-score.** The pillar "the ending" from 3.0; publish the memo `docs/audits/GE_V_PLAYED_CAMPAIGN_<date>.md`.

## What GE-3 hands GE-V

- The two arms' fixtures and scripts (`tests/fixtures/playtest_saves/fixture_ge3_{pressburg,premature}.json`, `tools/playtest_scripts/ge3_{pressburg,premature}.json`, `tools/gen_ge3_congress_fixtures.py`) — STAGED starting states; GE-V's job is the road to them from the boot.
- The driver prints the Congress's clock line every sitting turn (`- CONGRESS …`), a gate line once 50 are titled (blocked or open), the END SCREEN block for THE IMPERIAL PEACE, and `--stop-on-ending`.
- `GET /congress` is the table's one payload; the CONGRESS tab (Diplomatic Ledger, key 7) renders it; the wizard's step-1 row summons.

## Gates

- The four-file rule (`STATUS` ▶ NEXT UP, `ENDGAME_PLAN.md` §6 + the GE-V record, the rows disposed, `CLAUDE.md` LIVE STATE). Overwrite this prompt file at hand-off.
- Any mechanic moved by a measurement (e.g. `hold_titled` 50 → 45): a pin for it, `BASELINE_SERIES` + M1–M7 byte-identical (the Congress is dormant on the ambient board — measured, `tools/_ge3_series_arms.py`), the mutation sweep if code changes.
- The full suite runs in the pre-commit hook (~17 min) — commit in the background and read the log; stage by name.

## Hazards (verbatim constraints)

The Bash tool mangles quotes and backslashes in heredocs — write scripts with the Write tool and run them by path (it planted a literal backspace byte in a regex this session); files in this repo have MIXED line endings (some CRLF, some LF) — an exact-string edit must try both; `PYTHONIOENCODING` is forbidden; every `/command` staging under the suite needs `tests._chip_census.board_env(monkeypatch)` and a function-scoped fixture that restores `M.world` / `M.game_state["world"]` / `M.parser`; the campaign log's type count is 167 (`congress`); never run anything beside `tools/mutation_sweep.py` (it mutates the tree in place); a user's live game may hold port 8005 — test on `SOVEREIGN_PORT=8006`.

## Finish

Commit, `git push origin master`, then report where we are and what the next session opens (the release build, ROADMAP 10 — its part 1 is parked in `git stash` "release-build part 1 …" and `deploy/parked/release_build_part1.patch`). Still open for the user: GE-D1 (the generals' mortality — recommended, not built), GE-D2 (the Guard's question), the in-game feel of the end screen's registers and the Congress's surfaces (`docs/audits/IQ10_*CONGRESS*_2026_09_25.png`).
