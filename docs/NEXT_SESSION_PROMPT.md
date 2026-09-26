# NEXT SESSION PROMPT — ROW SR, CHUNK 1: "Paris must be reachable"

> Overwritten each time a session hands off. Current hand-off: **September 26,
> 2026, after THE SCORE MANDATE was ruled** (`docs/SCORE_MANDATE_PLAN.md`, the
> routing authority; STATUS ▶ NEXT UP and `CLAUDE.md` LIVE STATE point there).
> The release build is on itch.io's doorstep (the user uploads the zip); the
> September 25 evening review filed 32 AAR rows and 8 AAR-D rows; nothing was
> built. The next slice is Chunk 1 of the plan.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Row: SR, Chunk 1 — "THE ENDING: Paris must be reachable" (`docs/SCORE_MANDATE_PLAN.md` §2 Chunk 1, ≈3 sessions). Commit and push at every slice.** Work directly on master per `CLAUDE.md`'s workflow; read its Golden Rules first, then the plan's §0 mandate (every pillar rises, weakest first, 30% of the chunk reserved for the quick-win bank §3, nothing under §4 built before its gate).

**Reading order**

1. `docs/SCORE_MANDATE_PLAN.md` — §0, §1 (the scoreboard), §2 Chunk 1, §3 (draw the chunk's quick wins at the start), §5 (how the chunk is scored), §6.
2. `docs/audits/PLAYTEST_CREATIVE_AAR_2026_09_25.md` §1 turns 4, 7, 9 and 18 (the road as it was played; AAR-1 and AAR-D2's evidence) and `docs/audits/GE_V_PLAYED_CAMPAIGN_2026_09_25.md` §2 (the six measured mechanics), `SYSTEMS_REFERENCE.md` §68.6 (the deeper gate's four levers).
3. `docs/ENDGAME_PLAN.md` §2.2 (title), §2.8 (the 45 rule — not moved a third time), `backend/game_logic/congress.py` (the gate terms), `DESIGN_REFINEMENT.md` AAR-D1 / AAR-D2 / GEV-D1 / PR-D1b, `BUG_FIXES.md` AAR-1 and PB-7.
4. `docs/PLAYTESTING.md` — and the AAR's lesson: **`tools/playtest_driver.py --http` opens with `POST /new_game`; save first, or play by hand.**

**The contract, in order**

- **SR-1a Status quo is a cession.** A province retained by a ratified status-quo clause is titled `ceded_by_treaty` at ratification (`province_title`), on every ratify seam (incoming offer, the editor, the pair substitute, the third-party path); the Congress line flips it from "held, unsettled" the same turn. Drive it: the AAR road's Treaty of Vienna shape (four held provinces) → 36 titled at turn 9. Pins on every seam; `BASELINE_SERIES` byte-identical (the ambient board never ratifies a retention) — say so with the reason measured.
- **SR-1b The client's war is the lord's war.** Rule AAR-D1 at the recommended default (a): a lord's PEACE or ARMISTICE resolves its satellites' pairs with the same court through the common-peace path; the offer surface lists what would remain at war; the AI's war council treats the lord's fresh peace as a restraint on the client pair (`FRESH_PEACE_FLOOR` one hop down). GR5: any lord. The AAR's sequence (Austria takes Piedmont, Tyrol, Milan under the French peace) is the reproduction and the pin. If the series moves, attribute it by a flip experiment.
- **SR-1c The gate line teaches the road.** For each held-unsettled province, its shortest road to title on the Congress line, the war room and the Territories tab; the alarm term names what lowers it; the war room's counsel names the DP price of the road it recommends (AAR-D5's counsel half).
- **SR-1d PR-D1b + PB-7.** Reproduce PR-D1b on the commanded arm first (`--diplomacy accept`: the turn-3/4 acceptance, the quiet turns); the gate is P1's own coalition break-ranks clause, NOT `effective_peace_threshold`; build behind a lever, attributed. PB-7 is docs only (the 9 closed-but-OPEN rows, ROADMAP row 16, the ownerless rows — every one gets an owner or is struck with a reason).
- **SR-1e The re-measure.** Re-drive the AAR road (chunked by hand, `--script` per chunk) and GE-V's played A/B with 1a–1d landed; the target is the standing strict xfail `test_a_played_arm_reaches_forty_five_by_turn_forty`. **Report the count honestly. If it stops short, write the §68.6 levers into SR-D3's gate questions with the numbers, and do not move 45.**
- **The reserve:** ≈0.9 session of §3 quick wins, chosen at the start (AAR-12, AAR-15, the GE-V §4 nits and the School's Congress card are the natural picks).
- **Exit:** the ending re-scored on the played arm (the four asks), the scoreboard row in the plan updated with the date and the evidence, the four-file rule (STATUS ▶ NEXT UP, the landing record in the plan's §2, the rows disposed, `CLAUDE.md` LIVE STATE).

**Gates**

- The pre-commit hook runs `ruff check backend/` + the full suite (~20–24 min at 26k tests): commit in the BACKGROUND and read the log; never `--no-verify`.
- Any `.gd` change → the parse harness (`Godot…exe --headless --quit --path godot-client/project-sovereign --script ../../tools/godot_parse_check.gd`, EXIT=0; commit the refreshed `tools/godot_parse_report.json`) and a windowed boot with `--audio-driver Dummy --log-file <abs path>` grepping `SCRIPT ERROR` (expect 0). Check the foreground window before any windowed run — the user plays other games on this machine.
- `BASELINE_SERIES` + M1–M7: byte-identical unless attributed by a flip experiment (`tools/_vpr1_series_arms.py` is the latest pattern).
- A stale backend from September 23 may still listen on port 8006; `netstat -ano | grep :800` before choosing a port.
