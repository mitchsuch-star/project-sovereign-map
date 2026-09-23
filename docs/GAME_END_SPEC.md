# Game End & Defeat State — "The Verdict and the Fall" (row GE)

> **Status: RULED September 23, 2026 — BUILD-READY.** The rulings in §2 were
> taken by Claude under the user's delegated grant (*"make calls please and then
> separate out game end and defeat state as session after these"*). They are
> recorded rather than gated; each carries its argument and its re-open
> condition. The user has not separately confirmed them.
>
> **Where it sits:** **▶ NEXT** — before the release build (ROADMAP row **GE**,
> ahead of position 10), by the user's direction: a playable game has an ending
> (*"thought we wanted end state first?"*). The release build carries it. Routing
> authority = `docs/STATUS.md` ▶ NEXT UP.
>
> **What it is carved from:** the Victory & Objectives pass (ROADMAP positions
> 12–13). This row takes **the loss condition** and **a game end**. VP-1
> ("The Emperor's Designs") and the rest of VP-2 stay with their own gate — §3.

---

## §0 Why this row exists

The 1805 campaign cannot end. `WorldState.sandbox_mode` is `True` on every
Europe world. It is the first statement of `TurnManager._check_victory_conditions`
and of `_check_enemy_victory`, so a France reduced to nothing plays on forever,
and so does a France that conquers Europe. IQ-2 (Sept 14, 2026) made the collapse
*legible* but ruled it "never terminal", because win conditions were then excluded
by direction. **The user has now asked for a game end and a defeat state as their
own session.** That supersedes the IQ-2 scope note for scenarios that author the
rules (§2 R9).

## §1 Measured facts (research at HEAD `289697ef`, Sept 23, 2026)

The source is the read-only research fleet for this spec: 12 fresh 40–60-turn
driver runs plus 250 archived digests. Scripts and tables were in the session
scratchpad. The fresh runs are gitignored under `tools/playtest_runs/gameend-*`.

- **The collapse is unrecoverable in practice.**
  - Of 250 archived runs, 105 fell to ≤ 24 provinces and 75 to ≤ 20; **none regained 3**.
  - Paris fell in 17 archived runs and 2 of the fresh ones (turns 5–40). None of the 17 archived runs that end with a save had retaken it.
- **The Emperor is never freed without the peace table.** He was captured in 5 of the 12 fresh runs and released in none. The captor's offers kept coming (Britain about every 5 turns, "Asking 4,977–5,672 gold").
- **A passive France keeps its army while it loses the map**: 107k men standing while it went from 28 to 5 provinces. So "no army" alone is a weak defeat signal, and "no province" alone arrives very late.
- **"Peace with the coalition" cannot be a victory rule yet.** Before PR-D1b, every accept arm signs a 6–7-pair coalition peace on **turn 4** at war score 0, with Britain paying France 1,358g. Afterwards the enemy made 0 attacks for 36 turns.
- **Candidate defeat rules on the 12 fresh runs:**
  - collapse (≤1 province) or no army and no commission, with a 5-turn grace: fires 1× by t40, 2× by t60;
  - Emperor captive, 10-turn grace: 3× by t40 (turns 34 / 36 / 37);
  - legacy parity (0 provinces or no free corps, immediate): fires with Paris and 10 provinces still held → **rejected**.
- **Churn.** 20 test files (97 lines) mention `game_over`. The ROADMAP's "42 files / 115 assertions" does not reproduce: it matches only when `__pycache__` and fixture files are counted.
  - `sandbox_mode` is read 13× in 8 modules, mostly to mean "this is the Europe world". **It must not be flipped.** Flipping it would re-arm the 75% fraction and the 60-turn defeat that EC-6 removed.
  - **Bare flag world:** the suite pins `SOVEREIGN_SCENARIO=none`, so a rule that only a *scenario* authors leaves most tests untouched.
- **What the code has today:**
  - **Client:** `main.gd::_show_game_over_screen` renders terminal text only. It shows "VICTOIRE!/DÉFAITE", defaults `total_regions` to 13 (the legacy map) and disables input permanently.
  - **Load path:** it never raises the end screen, so a finished save loads into a board that refuses every order.
  - **Autosave:** both end-turn paths autosave unconditionally, so the game-over turn itself is autosaved.
  - **Endpoints:** 11 POST endpoints refuse with "The war is over."; `/mailbox/activate` does not.
  - **Stale comment:** `max_turns` is 60 on Europe and inert there, because every reader is behind the sandbox gate. turn_manager's "already handled in advance_turn" comment is stale: `advance_turn` never reads it.

## §2 The rulings (gate record — authoritative)

**R1 — Defeat: "The Fall of the Empire."** Two arms. Each arm runs a visible
clock, and each is warned through the **existing** defeat-imminent channel
(`get_defeat_imminent_state` → terminal, dispatch, rail) with the clock and its
exits named. **Losing Paris alone never triggers either arm** (PL-31 honoured).

- **Arm 1 — "The Empire Without Soil or Sword."**
  - **Condition:** the player holds ≤ `collapse.COLLAPSE_PROVINCE_CEILING` (1) provinces, **or** has no free corps (no standing marshal who is not a prisoner) **and** `recruitment.first_affordable_commission` returns nothing.
  - **Clock:** the condition must hold for `FALL_GRACE_TURNS = 5` consecutive turns.
  - **Exits:** retake a province, commission a marshal, or make peace.
  - This rides W6-7 attrition, as the Victory gate note asked.
- **Arm 2 — "The Eagle in Chains."**
  - **Condition:** the sovereign (`Marshal.is_sovereign`) is a prisoner.
  - **Clock:** `CAPTIVITY_GRACE_TURNS = 10` consecutive turns without being freed; then the regency falls.
  - **Exits:** accept the captor's terms (the existing ransom/peace road), or a prisoner exchange.
  - NAPOLEON_SPEC §7 calls captivity "peace leverage"; this arm gives that leverage its consequence. It does not add a new status effect.
  - **Reachability is part of the arm.** An exit must be legal even with the treasury at 0. GE-1 proves which road provides it: the captor's offer priced to the purse per EC-W4, or the exchange. If none exists, GE-1 builds the purse-priced road **before** it arms the clock.
- **Numbers:** both graces are blessed and tunable in-band.
- **Symmetric predicate (GR5):** `fall.get_fall_state(world, nation)` answers for any nation, but only the player's fall ends the game. AI nations keep losing the way they do today, by elimination and by suing through the existing peace rungs.
- **Re-open:** if player reports or a played campaign show a fall the player could not see coming, lengthen the grace. If it shows a hopeless state that drags on without firing, shorten it.

**R2 — The game end: "The Verdict of History".**
- **When:** the scenario authors a verdict date. `europe_1805.json` gets a new `campaign_end` block with `verdict_turn: 44`, which is Early July 1807, the summer of Tilsit and the zenith of the historical Empire.
- **What happens:** at the end of that turn a ceremonial verdict grades the reign. **The campaign then continues** (mark and continue — EC-6 is preserved; there is no hard stop and no defeat for falling short). The verdict is stamped once and never fires again.
- **Tier inputs** are derived at the moment and never stored beyond the stamped result:
  - provinces held vs the 28 held at the opening;
  - Paris held;
  - the Emperor free;
  - great powers still at war with France, and each war's score;
  - satellites kept;
  - the treasury.
- **Tiers:** four, from a triumph down to an eclipse. The thresholds are in-band tunable, and GE-1 measures the tier distribution on the driver arms (ambient, and the commanded accept/decline arms) and reports it in the landing record.
- **Why Tilsit and not 60.** Turn 60 (March 1808) has no historical anchor. Turn 44 is the natural close of the 1805–07 arc, and VP-2's Napoleon Comparison can later anchor on the same date. Both are after turn 40, so `BASELINE_SERIES` and M1–M7 cannot see either.
- **Not in this row:**
  - An objective-shaped victory — VP-1 owns it.
  - "Coalition peace = victory" — PR-D1b's turn-4 peace would make it trivial. The decisive-peace triumph belongs to VP-1/VP-2.
- **Re-open:** if the played campaign shows 44 turns is too short or too long for a first campaign, move the authored turn. It is scenario data, not code.

**R3 — Keep playing.** After the verdict, play continues. After a defeat, the game
is terminal: Load, Main Menu, and read-only review (GET endpoints keep working).
There is no "play on regardless" arm after a defeat, because a defeat you can
ignore is not a defeat.

**R4 — The end screen.**
- **Scene:** a new `campaign_end.tscn` on its own CanvasLayer, in the Proclamation style.
- **Data:** fed by ONE backend builder, `build_campaign_summary(world)`. The same payload serves the verdict and the fall.
- **Final Moniteur:** a closing issue is written (a gazette special).
- **Replaces** the six calls to `_show_game_over_screen`'s terminal text; the text stays as a fallback. The legacy defaults (13 regions, French-only headings) go.
- **One display-only accumulator** is added: serialized `campaign_totals` (battles fought / won / lost, men lost and inflicted, provinces taken / lost, coalitions faced).
  - **Why:** per-war casualty data is cleared when a war ends, and `event_log` fills within about 10 turns.
  - **Where:** written at the existing battle-record and capture chokepoints.
  - **Rule:** never read by mechanics (GR6). The later Napoleon Comparison reuses it.

**R5 — AI symmetry.** Covered in R1. `_check_enemy_victory` stays inert on
Europe: its 75% fraction is exactly what DG-5 forbids.

**R6 — Saves.**
- **Stamp and load:** the ending is stamped in the save's `metadata.ending`. `/load` returns it and the client raises the end screen.
- **Autosave on defeat:** the autosave is not overwritten, so Continue lands one turn before the fall. A named "Final — <calendar date>" save is written instead.
- **Endpoint guard:** `/mailbox/activate` gets the same "The war is over." guard as its eleven siblings.

**R7 — The flag.**
- **New flag:** the rules arm only when the scenario authors a `campaign_end` block. It is a new derived flag, not `sandbox_mode`.
- **Where they arm:** `europe_1805.json` authors the block; the tutorial scenario and the bare flag world do not. The suite's `SOVEREIGN_SCENARIO=none` pin therefore keeps every sandbox test as it is.
- **First contact:** `first_contact._is_open_ended` is re-pointed to the new flag, so "how do I win" names the verdict and the fall.
- **Validation:** `modding/validator.py` validates the block, and `MODDING_FORMAT.md` documents it (DG-5: scenario-authored and optional).
- **One entry point:** a single `record_ending(world, kind, cause)` seam records every ending. VP-1's triumphs reuse it later.

**R8 — WO-D10, the mechanic half: YES.**
- **Change:** when no home soil remains, commissioning spawns at the richest HELD province (`find_spawn_region`). Today a France in exile, holding a dozen rich conquests, cannot rebuild its Marshalate at all.
- **Why it belongs here:** arm 1's commission exit reads the same predicate, and the exile game only matters once losing is a state the game recognises.
- **Scope:** symmetric (GR5) and behind a flip lever. If it moves `BASELINE_SERIES`, re-record it once with a flip-experiment attribution.

**R9 — IQ-2's scope note is superseded where the rules are authored.**
- The collapse warning now names the clock and its exits instead of promising that the campaign continues.
- The "never terminal" pins flip consciously and are each named in the commit: `_dispatch` (the forbidden-phrase list and `endswith(CAMPAIGN_CONTINUES)`), `_economy_status`, `_war_room`, `_chronicle`, `_client` — about 5 files, 10–15 assertions.
- `collapse.py` stays the one collapse predicate. `fall.py` reads it and never forks it.

## §3 What stays with the Victory & Objectives pass (positions 12–13)

- **VP-1, "The Emperor's Designs":** France's objective deck, branching, and the decisive-peace triumph.
- **The rest of VP-2:** the Napoleon Comparison (which may anchor on this row's verdict date), HC-D1, NPC-D2, NP-D7 (the Victory-Pass interlock), and the Emperor's death.
- **Hand-off:** VP-2's "chosen loss condition" is **discharged by R1** unless VP-2 re-opens it.
- **Churn:** the ROADMAP's churn note for rows 12–13 is corrected to the §1 count.

## §4 Slices

| Slice | Contents | Effort |
|---|---|---|
| **GE-1** backend | `backend/game_logic/fall.py` (the fall predicate + clocks, ONE serialized `fall_clock`); the verdict (the `campaign_end` block, validator, the tier derivation); `record_ending` + the `ending` record (serialized); `campaign_totals`; the defeat-imminent copy with clock and exits; the three end-turn exits and `/load` carry the ending; `/mailbox/activate` guard; the autosave rule + the "Final" save; WO-D10; the captivity-exit reachability proof; tests | ~1 |
| **GE-2** client | `campaign_end.tscn/.gd` (verdict + fall), raised from every end-turn flow and from `/load`, keep-playing after the verdict, Load / Main Menu after the fall, the final Moniteur, the legacy text fallback de-legacied; XR-1 boot smoke + parse harness; a Mode-A driver arm that reaches the verdict and one that reaches each fall | ~1 |

## §5 Done when (falsifiable)

1. **Verdict fires once.** On a fresh 1805 boot driven to turn 44, the verdict fires **once**, the campaign continues, and a later turn never re-fires it (driver arm + test).
2. **Arm 1 clock.** A staged France with 1 province (or no free corps and no affordable commission) sees the warning name the clock and exits on the first turn and falls on the 5th. Retaking a province (or commissioning) on turn 3 stops the clock.
3. **Arm 2 clock.** A staged captive Emperor falls on the 10th turn unransomed. Accepting the captor's terms or an exchange stops the clock. With the treasury at 0, an exit is still legal.
4. **Paris alone never triggers** (PL-31 pin).
5. **The bare flag world and the tutorial never arm** (flag pin), and every legacy terminal-rule test stays green.
6. **Saves.** A defeated save loads onto the end screen, never onto a board that silently refuses orders. The autosave after a fall is the pre-fall turn, and a "Final" save exists.
7. **AI symmetry.** An AI nation that meets the fall predicate does not end the game (GR5 pin).
8. **Series and harness.** `BASELINE_SERIES` and M1–M7 are byte-identical, or re-recorded once with attribution if WO-D10 moves them. `tools/ai_v_sweep.py` handles `game_over` (its marengo seed falls at turns 37–40).

## §6 Pins consciously flipped (to be named in each commit)

- **`test_first_contact_keyless`:** 2 tests (the open-ended answer).
- **`test_economy_ec6_sandbox::test_1805_no_end_screen_at_turn_60`:** its meaning is re-blessed. It stays green because the verdict never sets `game_over`.
- **The IQ-2 "never terminal" pins** listed in R9.
- **Legacy:** 0 flipped.
