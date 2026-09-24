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
- **The rest of VP-2:** the Napoleon Comparison (which may anchor on this row's verdict date), HC-D1, NPC-D2, NP-D7 (the Victory-Pass interlock)~~, and the Emperor's death~~. **Amended September 25, 2026: the Emperor's death moved INTO GE-1 by user direction** — the third defeat arm "The Eagle Falls" (`ENDGAME_PLAN.md` §3; the build note in `docs/NEXT_SESSION_PROMPT.md`). NP-4's "a sovereign never dies in v1" is superseded where the rules are authored.
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

---

## §7 THE IMPERIAL PEACE — the victory arm (PROPOSED September 23, 2026 — awaiting the user's ruling; nothing built)

> **Status: PROPOSAL.** Written after the live review (`docs/audits/PLAYTEST_LIVE_REVIEW_2026_09_23.md`) at the user's direction: *"determine how the end can work. one suggestion is holding X for X and this involves 'stabilization of new status quo'; also how defeat conditions should work and what happens if nations eliminated globally."* It amends §2 only where it says so. R1 (the Fall), R2 (the Verdict at 44) and R3–R9 stand unless a ruling in §7.8 changes them. **GE-1 does not start until §7.8 is ruled**, because the title record (§7.2) is written at the same seams GE-1 touches.

### §7.0 Why the game needs an earned ending — measured, not argued

- **A. The turn-4 peace.** On the commanded-accept driver arm France accepts Britain's paying peace on turn 4 at war score 0; the coalition is spent, the alarm falls 90 → 45 → 0 by turn 40, the enemy makes **0 attacks in 56 turns**, France holds 28 provinces throughout and banks 152,941 gold. The Verdict at 44 would *grade* this campaign; nothing in it could ever be *won*.
- **B. The fiat conquest.** A cheat probe handed France one court's provinces per turn while every enemy army stayed in the field: 91 provinces by turn 6, then alarm **97 for 25 turns**, six Revanche designs in six turns, Charges of Empire ~9,900g/turn, Net negative from turn 17, the map bleeding back 91 → 66 by turn 30 with Russian corps walking into Provence unopposed and Holland breaking free. Holding land is not winning; the board already says so, mechanically.
- **C. Global elimination.** With every rival court torn down by the engine's own `_eliminate_nation` (probe A: rivals; probe B: vassals too) the game runs twelve more turns with no error and no ending: the alarm climbs to **99 "Brewing"** (+8 hegemony, +3 for half the map, +2 for the largest army, every turn) while Talleyrand says "No coalition stands against us" and "France wages no war — a rare and precious quiet"; the treasury grows ~14,000g a turn; the satellites drift (Holland 100 → 59); `enemy_nations` is never pruned; "how do I win" still answers "there is no laurel to be handed out".
- **D. What the code cannot say.** `Region` has no ownership-history field; `previous_treaties` stores what was proposed, not what was applied; the campaign ledgers' captures are cleared at peace. Nothing today can tell a province *ceded by treaty* from one *seized last turn*. Britain's `low_countries` and Austria's `redeem_italy` target French homeland (Flanders, Savoy), so those designs can never read satisfied while France keeps her 1805 borders; a partitioned power's Revanche is permanent.

Therefore the ending must: (1) be reachable only by **settling** conquests, not by occupying them; (2) be unreachable through the turn-4 peace; (3) fire when no one is left to contest the order; (4) be a clock the player can read on the surfaces they already use.

### §7.1 The rule — "hold X for X"

**THE IMPERIAL PEACE.** France wins when, for `stabilization_turns` = **8** consecutive turns:

1. the French bloc (France plus her satellites) holds at least `hold_provinces` = **51** provinces **by title** (§7.2). 51 is 40% of the 126-province map, the middle `region_control` gate; the boot bloc is 35, so sixteen provinces must be won AND settled;
2. no great power (`_CANONICAL_MAJORS` minus France: Britain, Russia, Austria, Prussia) is at WAR with France — PEACE or any treaty counts, an **ARMISTICE does not** (a truce is not an order);
3. no coalition stands or brews against France, and Europe's alarm is below the Brewing line (`threat < 60`);
4. no satellite is in rebellion, and every satellite's loyalty is ≥ 40;
5. the titled count never dips below `hold_provinces` inside the window — a lost province resets the window; a province gained mid-window may join the count.

The numbers are authored in the scenario's `campaign_end` block beside `verdict_turn` and are tunable there (R7: the rules arm only where a scenario authors them).

### §7.2 Title — the stabilization of the new status quo

A province is **held by title** when one of these holds:

- **homeland** — it is in `nation_starting_regions` for France (28), or in a satellite's own starting regions (a satellite's share counts only while it is a satellite with loyalty ≥ 40);
- **ceded by treaty** — it was transferred by a `territory_cede` / settlement clause the other court signed. The three ratify seams already exist (`_ratify_treaty`, `settlement_ratify._apply_settlement_terms`, `formations.apply_create_client_clause`); title is immediate;
- **quiet possession** — it was captured by force and then held for `title_turns` = **12** consecutive turns (the `AGENDA_GRUDGE_TURNS` window) during which no hostile army entered it AND the court it was taken from is not at war with France (an armistice counts as not-at-war here; a new war restarts the clock);
- **a client's soil** — the provinces of a court France created (Warsaw, the Roman Republic…) are that client's homeland, which formations already set at birth.

Everything else — an enemy province occupied during a war, a province taken last turn — is *held*, shown on the ledger, and not *titled*. That is the "stabilization" the user named: a conquest joins the order only when the loser signs for it or when Europe has stopped contesting it.

**The record.** ONE new serialized field, `province_title: {region: {"kind": "treaty" | "conquest", "since": turn, "from": nation}}`, written at the capture chokepoint (`capture_region` — kind `conquest`, `since` = the turn) and at the three ratify seams (kind `treaty`). Homeland needs no record. A hostile army entering a `conquest` province resets `since`; the title check reads `since <= turn − title_turns`. GR5: the record is written for every nation; only the player's ending reads it. `Region` itself is not changed.

**Rider — reconciliation (gated separately, Q6).** A court that signs a cession is *reconciled* for that province: its Revanche design's weight for that province reads 0 while the treaty holds and re-arms if the treaty is broken. Today Revanche is permanent (`emergent_designs.py`), which is right for a forced peace and wrong for a signed one — without the rider a partitioned Austria is never content even after a Pressburg it signed. Zero new fields: it reads the treaty record.

### §7.3 The clock the player sees

ONE source, `game_end.imperial_peace_state(world)`, rendered as one line on the war room, the Strategic Ledger's Territories tab and the end-turn banner:

`THE IMPERIAL PEACE — 51 titled provinces needed · 43 titled (8 held, unsettled: Vienna, Bohemia, …) · window 0 of 8 · blocked by: Britain at war; Europe's alarm 97 (Brewing)`

With the window open: `window 3 of 8 · nothing blocks`. A reset is a dispatch beat that names its cause ("Provence is lost — the Imperial Peace must wait"). Talleyrand's counsel rung names the nearest gap ("Sign with Vienna and Bohemia is yours by title; London still fights"). Reuses the design-line and `enemy_eliminated` idioms; no new popup, no PopupQueue slot.

### §7.4 The ending

When the window completes: `record_ending(world, "victory", "imperial_peace")` through R7's seam; the R4 screen in the Proclamation style — *THE IMPERIAL PEACE — Europe accepts the order of the French Empire* — with the campaign totals and a final Moniteur, and two buttons: **Continue the reign** (EC-6: mark and continue; the Verdict at 44 still grades) and **Retire to the Tuileries** (Main Menu). The ending is stamped once and never re-fires. Symmetric predicate (GR5): `imperial_peace_state` answers for any nation; only the player's ends the game, exactly as R1.

### §7.5 Global elimination — the rulings

- **E1 — The Universal Monarchy.** If every great power is eliminated or vassalized to France, the Imperial Peace fires at once, without the window: no court is left to contest the order. Same ending, a different subtitle. Today this state is an eternal "Brewing".
- **E2 — Nobody left to be alarmed.** The threat scalar stops climbing when no non-vassal court can qualify for a coalition: the hegemony / army-share / region-control producers early-return (or `add_threat` decays to 0) while `get_qualifying_nations` is structurally empty, and Talleyrand says "There is no Europe left to alarm" instead of "Brewing". Measured: 99 with nobody left, +13 a turn.
- **E3 — The dead stay dead.** An eliminated court contributes no "X: No marshals (eliminated?)" row to the enemy phase; its fleets leave the pooling, the blockade board and `continental_ports_total`; `trade_dominance_nation` never returns it; its agenda deck is retired rather than skipped. The research read these by code; GE-1 pins them.
- **E4 — Knocking out a great power is an ending beat**, not a rail row: a special Moniteur, the existing dispatch headline, and a verdict-tier input ("great powers eliminated or vassalized" beside "great powers still at war").
- **E5 — Great powers stay eliminable on the battlefield.** D2 governs only the AI-vs-AI term generator. No capital immunity for the player: the last-province teardown is the fair end of a war the player fought to the finish.
- **E6 — The AI roster shrinking** needs no change: coalitions need two members (guarded), the paymaster stops with Britain (guarded), ultimatums have no issuer; the probe played twelve turns after a total elimination with zero errors.

### §7.6 Defeat — how it should work (R1 confirmed; one addition)

- **R1's two clocks stand.** "The Empire Without Soil or Sword" (≤1 province, or no free corps and no affordable commission, for 5 turns) and "The Eagle in Chains" (the Emperor captive for 10 turns): warned, with exits, and Paris alone never triggers them. The research shows the shape is right — a passive France keeps 107,000 men while losing the map, so "no army" alone arrives late; Paris fell in 19 of 262 archived and fresh runs and was never retaken, so "Paris alone" would end campaigns the player had not given up.
- **Addition — "The Humbled Peace", a marked, non-terminal ending.** If France ratifies a settlement that cedes Paris, or at least half the homeland, or makes France a vassal, `record_ending(world, "defeat", "humbled_peace")` stamps the campaign (the R4 screen in crimson; the Verdict grades it as an eclipse) and play **continues** — Prussia after Tilsit is a game, not a game over. It is not terminal because the player chose it; R3's "a defeat you can ignore is not a defeat" applies to the clocks, which the player did not choose.
- **No third clock.** Grip collapse and treasury collapse are already legible and already reach R1 through attrition; a separate clock would double-count. Re-open if a played campaign shows a hopeless state that neither R1 arm reaches within ten turns.
- Symmetry (GR5): AI courts keep losing by elimination and by suing; `fall.get_fall_state` answers for them and never ends the game.

### §7.7 Numbers and the measurement plan (GE-1 owns it)

Defaults, all in `campaign_end`: `hold_provinces: 51`, `stabilization_turns: 8`, `title_turns: 12`, `alarm_ceiling: 60`, `satellite_loyalty_floor: 40`, `verdict_turn: 44`. Measured before landing, on committed driver arms:

- the commanded-accept arm must NOT win (it holds 28 — passes by construction; pinned);
- the fiat arm must NOT win (alarm 97, at war with everyone — passes by construction; pinned);
- a scripted **"Pressburg" arm** (Ulm → Vienna → a settlement that cedes Vienna's neighbours and the satellites' claims → eight quiet turns) should reach the Imperial Peace between turns 25 and 40. If it cannot, `hold_provinces` comes down to 45 (the 30% gate plus the satellites' seven) before anything else moves;
- the global-elimination probe must fire E1 on the first turn after the last great power falls.

The window, title and alarm constants are in-band tunable; `hold_provinces` and the title rule are the gate.

### §7.8 Questions for the user (recommended default first)

- **Q1 — The shape.** (a) "Hold X titled provinces for X quiet turns", §7.1–§7.2 **[recommended]**; (b) an authored objective set (Vienna, Berlin, the Rhine…) held for X turns — VP-1's territory, it would pre-empt that gate; (c) a pure province count with no title rule — rejected by §7.0-B: it rewards the occupation the board itself punishes.
- **Q2 — The numbers.** 51 / 8 / 12 **[recommended]**, or 45 / 6 / 10 for a shorter first campaign. Both are scenario data.
- **Q3 — After the victory.** Mark and continue, with a Retire button **[recommended]**; or terminal.
- **Q4 — The Humbled Peace.** A marked, non-terminal defeat ending **[recommended]**; or nothing; or terminal.
- **Q5 — The Universal Monarchy (E1)** fires without the window **[recommended]**; or requires the eight-turn window like any other Imperial Peace.
- **Q6 — The reconciliation rider** (a signed cession silences that province's Revanche while the treaty holds): in GE **[recommended — it is what makes a signed peace worth more than an occupation]**; or deferred to the Victory pass.

### §7.9 Slices (if ruled)

- **GE-1 riders:** the `province_title` record at the four seams; the E2 alarm guard; the E3 "dead stay dead" pins; the Humbled Peace stamp at the three ratify seams.
- **GE-3 "The Imperial Peace" (~1 session):** `game_end.imperial_peace_state` and the window clock (ONE serialized `imperial_peace_window`), the ledger / war-room / banner line, Talleyrand's rung, the Pressburg driver arm, the ending-screen variant (shares GE-2's scene), the E1 arm, `tests/test_game_end_imperial_peace.py`.
- Row GE becomes ~3 sessions (GE-1 + GE-2 + GE-3). The release build still follows GE.

### §7.10 Never-do pins (for the build)

- The turn-4 paying peace never satisfies the Imperial Peace (the titled count stays 35 < 51; pinned on the commanded-accept archive).
- An ARMISTICE never opens the window.
- A province held by force and never signed for is never titled before `title_turns`.
- The Imperial Peace never fires twice; a Humbled Peace after an Imperial Peace stamps a second ending and the Verdict reads both.
- Nothing here writes `sandbox_mode`; the bare flag world and the tutorial never arm (R7).

### §7.11 Evidence

`docs/audits/PLAYTEST_LIVE_REVIEW_2026_09_23.md` §4 (the three probes, with numbers) and §1 (the played campaign). The probe scripts lived in the session scratchpad; the commanded arm is the committed `tools/playtest_scripts/commanded_full40.json` run with `--turns 60 --diplomacy accept`.

---

## §8 RULED — September 23, 2026 (evening): §7's questions are answered in `docs/ENDGAME_PLAN.md`

> **`docs/ENDGAME_PLAN.md` is the routing authority for the build (row EP).** Under the user's direction (*"make all decisions … it should be a challenge to force a new status quo … hold the win state for X turns with a mechanic that makes it fun"*) §7's proposal became **"The Congress of Paris"**: with **50 titled provinces** the Emperor *summons the Congress*; every great power answers — recognizes or refuses — on a public table with its reason and its PRICE, re-answered every turn; the Congress **sits 8 turns** during which refusers are driven toward war (+15 intent a turn), Britain funds them, the coalition gate drops to 40, the marshals and the satellites present their bills, and every titled province, Paris and the Emperor's freedom must be held with no new war declared; Britain is *shut out* rather than beaten when the Continental System closes ≥ 60% of the ports. Full recognition on the eighth turn = **THE IMPERIAL PEACE**; otherwise the Congress dissolves (alarm +15, 10-turn cooldown, grudges) and can be summoned again. §7.8: Q1 (a) with the Congress mechanic · Q2 50 / 8 / 12 · Q3 mark-and-continue with Retire · Q4 the Humbled Peace, marked and non-terminal · Q5 E1 fires without the window · Q6 reconciliation IN. Defeat (§7.6) and global elimination (§7.5) RULED as written. §1–§6 of this spec stand; where §7 and `ENDGAME_PLAN.md` differ, the plan governs. Slices: the plan's F1–F6 (the live review's fixes) FIRST, then GE-1 → GE-2 → GE-3 → GE-V.
