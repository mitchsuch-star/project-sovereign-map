Repo note first: the tree is **no longer clean** — a concurrent build session has 27 modified files (`world_state.py`, `executor.py`, `combat_executor.py`, `marshal.py`, `main.py`, …). **None is `naval.py` or `naval_executor.py`**, and my 12-turn series prefix still reproduces `BASELINE_SERIES[0:13]` exactly, so every measurement below is on the same code the reporter read. Their "git status empty" was true at their time.

---

# Refutation pass on FA-31

## Claims I attacked

### 1. The boot arithmetic (53.82 / 55.2 / 0.975)
**CLAIM** France 31.5 + 0.8×19.5 + 0.8×8.4 = 53.82 vs RN halved 55.2 → 0.975 OPEN; only sea link touching London is Normandy.
**MY MEASUREMENT** (`r1_boot.py`) — identical to the digit:
```
A no window        allowed=False shut   cov=100.0 mover=53.8 ratio=0.54 floor=1.25
B window only      allowed=True  window cov= 50.0 mover=53.8 ratio=1.08 floor=0.9
C window + derive  allowed=True  window cov= 55.2 mover=53.8 ratio=0.97 floor=0.9
UNROUNDED mover=53.82 coverage=55.2 ratio=0.975 ; London links = [('London','Normandy')]
```
**VERDICT: CONFIRMED.**

### 2. "The prior repro's 'unreachable, the board's number is 39.3' is FALSE"
**CLAIM** The row's 41.3 reproduces because the row builds keels.
**MY MEASUREMENT** Two independent checks. (a) `r2` with `ships=49` and all three at readiness 50 → `coverage 55.2, mover_effective 41.3, ratio 0.75, verdict shut` — exact. (b) I read the row's machine record: its `repro` field **literally contains `fr['ships']=49`**, and its `evidence` says "*the digest's turn-5 state, reproduced by the fold+rot arithmetic 70→69→64→63→58→58→53→50*". (c) Reachability, `build_rate`=1 under blockade: `45@70 → 46@69 → 47@63 → 48@58 → 49@53 → t=4: 49 sail @ readiness 50`.
**VERDICT: CONFIRMED** (and the reporter's correction of the prior repro is itself correct — the state is reachable and the row's own recipe specifies it).

### 3. The headline — "by the time the camp is staged a WON roll leaves it SHUT"
**CLAIM** Reproduces at the natural timing (0.786 same-turn); the Sept-2 verification's "FALSE" is over-corrected.
**MY MEASUREMENT** (`r4_natural.py`; Lorraine→Normandy measured at 4 hops by BFS, Rhineland 5):
```
t= 4 read=50 camp=0            GB=blockade  mover=39.3 cov=50.0 ratio=0.7900 allowed=False
t= 6 read=50 camp=2 staged=True GB=blockade mover=39.3 cov=50.0 ratio=0.7900 allowed=False
t= 7 read=55 camp=3 staged     GB=guard     mover=43.2 cov=56.0 ratio=0.7700 allowed=False
t= 9 read=65 camp=5 staged     GB=guard     mover=51.1 cov=56.0 ratio=0.9100 allowed=True
```
**VERDICT: CONFIRMED.** The headline reproduces; the cure reproduces; the 3-turn delay reproduces.

### 4. "Staging the camp is the CURE" (arm B)
**CLAIM** Arm B (50,000 at Normandy from tick 0) shows the camp lifting the blockade and the window opening at tick 3.
**MY MEASUREMENT** Arm B reproduces byte-for-byte (offset one tick for post-tick printing). **But arm B's starting state cannot be reached in play.** No French marshal boots in a camp province (`camp_strength(France)==0`), and the nearest camp province is 2 hops from Lorraine. Sweeping the arrival turn (`r5_fastest.py`, staging at Flanders):
```
arrive t=0 (impossible): STAGED t=2 ratio 0.92 allowed=True
arrive t=1:              STAGED t=3 ratio 0.84 allowed=False ; first staged+open t=6
arrive t=2:              STAGED t=4 ratio 0.79 allowed=False ; first staged+open t=7
arrive t=4:              STAGED t=6 ratio 0.79 allowed=False ; first staged+open t=9
```
**VERDICT: NARROWED.** On *every reachable* schedule the window is already shut when the camp first stages. "The camp is the cure" is true only as "the cure costs 3 more turns after staging" — the reporter's demonstration arm starts from a state the game never produces.

### 5. `resolve_diversion` never re-derives postures; the second window turn is worse
**CLAIM** The success arm sets `window_turns` and returns; the next tick's `derive_ai_postures` flips Britain to `guard`, which *recruits Russia* into the coverage pool.
**MY MEASUREMENT** Read `resolve_diversion` (naval.py:1568) — confirmed, no posture call. `derive_ai_postures` flips on `camp_turns>=2` **or `window_turns>0`** — so the player's own success causes the flip. Measured coverage 50.0 (blockade) → 56.0 (guard, Russia at 0.8×15 = 12).
**VERDICT: CONFIRMED.**

### 6. Regression (a) — the row's `fix_shape` forecast contradicts the truth
**MY MEASUREMENT** (`r6_regressions.py`):
```
t=1 read=65 | TRUE allowed=True  r=1.00 cov=50.0 | ROW-FORECAST allowed=False r=0.90 cov=55.6  <-- CONTRADICTS
t=2 read=60 | TRUE allowed=True  r=0.92 cov=50.0 | ROW-FORECAST allowed=False r=0.82 cov=56.0  <-- CONTRADICTS
```
**VERDICT: CONFIRMED**, with one narrowing: the reporter says the fix would black out "the only two turns of the campaign where spending it opens the strait". There are **three** at the opening (t=0,1,2 are all open in truth; the forecast agrees only at t=0), and it opens again permanently from t≈9.

### 7. Regression (b) — a 4th `diversion_terms` row disables the chip and deletes the odds
**MY MEASUREMENT** Read: `report["diversion_available"] = all(t["met"] …)` (naval.py:2205) gates the chip at :2380; `strategic_ledger.gd` renders `note` **only** inside `if enabled:` and `reason` **only** in the `else:`. Then I built the row's own filed fix as a pytest plugin and ran it:
```
BEFORE  [trap] terms=3 available=True  enabled=True  note='45% — and once only, this war'
AFTER   [trap] terms=4 available=False enabled=False note='' reason='even a success leaves it shut…'
AFTER   [boot] terms=4 available=True  enabled=True  note unchanged
```
Baseline selection (7 files, `-p no:randomly`): **243 passed**. Same selection **with the row's own fix installed: 243 passed.** I proved the plugin is live, not inert (`r7_patch_live.py`) before trusting that number.
**VERDICT: CONFIRMED** — including the reporter's real point, that 243 green tests say nothing because every diversion pin is written at boot readiness 70.

### 8. Isolation — the no-`finally` shape leaks
**MY MEASUREMENT**
```
mutate, no finally, exception mid-forecast: world unchanged = False
   LEAK: France.window_turns=2 | Britain.posture=guard | blockaded=[]
deepcopy-swap of world.fleets in try/finally: world unchanged = True
crossing_check purity: fleets byte-identical True, event_log delta 0
```
**VERDICT: CONFIRMED.** A free 2-turn window and a lifted blockade, granted by opening the ledger.

### 9. Series / harness inertness
**CLAIM** 40 turns: `find_ai_diversion` 446/0 hits, `resolve_diversion` 0, `build_admiralty_report` 0, `crossing_check` 5190, `MATCHES_BASELINE True`.
**MY MEASUREMENT** I ran an instrumented 12-turn `_emit_series` replica: `crossing_check 1044 · find_ai_diversion 169, hits 0 · resolve_diversion 0 · build_admiralty_report 0 · camp_turns never >0 · window_turns never >0 · zero naval events`, and `series[0:13]` == `BASELINE_SERIES[0:13]`. Rates are consistent with their 40-turn figures.
**VERDICT: CONFIRMED — and I found a stronger argument they did not make.** `camp_provinces` is authored for **France alone**; France is the player; `find_ai_diversion` is called from exactly one place, `enemy_ai.py:5912` (AI nations only). The rung is therefore dead **by construction**, not empirically. Likewise `resolve_diversion` has one production caller, `naval_executor.py:623`, reachable only via the player's verb, and `build_admiralty_report` has exactly one caller, `ledger.py:50` ← `main.py:4811` (`GET /ledger`).
`tests/test_combat_sweep_metrics.py` contains **0** occurrences of naval/fleet/crossing — M1–M7 confirmed unreachable.

### 10. Bonus (d) — "a window waives the host rule, and no surface knows"
**MY MEASUREMENT** The waiver is real (`crossing_check`: `if allowed and not window_open and is_hostile_shore(...)`; Britain London→Normandy `landing 2.05` → `window 4.10 allowed`). But with a live window the ledger already prints:
```
London–Normandy: WINDOW — open 2 more turn(s) (their coverage halved; the defended-shore rule waived)
```
**VERDICT: REFUTED as stated.** The surface knows; what is missing is saying it *in advance*.

### 11. Stale symbols / line numbers
Row's `:958ff` `:1573` `:2091` `:2293` — all four land inside the wrong or a shifted symbol (actual: `_fleet_covers_link` 947, `resolve_diversion` 1568, `diversion_terms` 2193, chip 2393-2398). **CONFIRMED.** Every symbol/line the *reporter* cites checks out except `TestClientConsumesThePayload`, which is actually `TestClientConsumption` (tests/test_naval_ui_clarity.py:244).

### 12. Small numbers that don't reproduce where they're placed
- "the Royal Navy at **2.6×**" is the **trap-state** Crossings line; at boot it is **1.9×**.
- The confirm quoted as "*fights at readiness 40*" is the readiness-50 state; at boot it is **60**, at my t=7 trap **45** (`diversion_failure_readiness` = current − 10).
- The §7 sample "PHASE 3 t7 read 50, STAGED … 39 against 56" is an **unreachable** state: the same pass that flips Britain to `guard` also un-blockades France and ticks +5, so at the real t=7 readiness is 55 and the numbers are **43 against 56**.
**VERDICT: NARROWED** — the conclusions survive, the printed sample copy must not be lifted.

---

## What the reporter MISSED — a builder must know these

1. **`link_verdicts` already IS the scan §7.1 proposes to write.** `_tracked_links` (naval.py:1726) = every sea link touching the player's provinces **or armies**; `_player_travel_direction` picks the direction; `_link_key` uses `sorted(pair)`; and `report["crossings"]` (naval.py:2136) already renders from it. Measured minimal forecast — `link_verdicts` on a `copy.deepcopy(world.fleets)` with `window_turns` forced — works and leaves the world byte-identical. Reinventing the scan is the CA9 through-line again.

2. **GR5 trap in the reporter's own rec #5.** `_tracked_links` and `link_verdicts` are hard-keyed to `world.player_nation`. Gating `find_ai_diversion` on a forecast built from them would forecast **for France** while gating **Britain**. They need an actor parameter, exactly as `blockade_forecast(world, actor)` does.

3. **The window opens THREE links, not one.** At boot, `link_verdicts` returns `Corsica|Piedmont`, `London|Normandy`, `Cagliari|Corsica` — all SHUT at 1.9×, all → ratio 1.08 under a forced window. "London–Normandy" is not the forecast; the row's hardcode and the reporter's single-link sentence are both too narrow.

4. **The derived-guard flip REMOVES coverage, it doesn't only raise it.** `_fleet_covers_link`: a `guard` fleet covers only links touching **its own** nation's provinces. Measured with the flip applied: `Corsica|Piedmont` and `Cagliari|Corsica` become verdict **`open`, ratio None** while `London|Normandy` falls to 0.97. A single "the window ratio" number is wrong in both directions at once.

5. **Determinism trap.** `tuple(frozenset({"London","Normandy"}))` is hash-seed dependent — measured across 4 fresh processes: `('London','Normandy')` twice, `('Normandy','London')` twice. Any forecast string built that way is flaky, and any pin on it is worse. The reporter's own sample says "London–Normandy" while my patch printed "Normandy–London" — that is this bug, already visible in the report. Use `sorted(pair)`.

6. **The confirm is `type: "clarification"` / `state: "awaiting_clarification"`** (naval_executor.py:586-589) — a LOCAL_PLANNING question, not a hard stop. The player can end the turn between the quote and "yes", and readiness moves ±5. A number quoted there goes stale exactly as the UX23-A reward price did; re-derive at the answer or don't quote it there.

7. **The surfaces are not literally blind, and the row's title over-reaches.** The Crossings line already publishes the no-window ratio and tracks the rot (1.9× → 2.6×), and the confirm already publishes the falling failure readiness (60 → 45). The one thing nothing computes is the **window** ratio (coverage×0.5 vs floor 0.9).

8. **FA-N82, the sibling the reporter recommends landing in the same slice, carries the same stale-line disease**: it cites `_camp_tick` at 1597, `derive_ai_postures` at 1550-1555, `camp_staged` at 1439-1441; actual 1693, 1639, 1541. Navigate by symbol.

9. **FA-31's stored `verification_2026_09_02.corrected_reading` is TRUNCATED in the machine record** (it ends `"Sta…"`). The Sept-2 reasoning the reporter is arguing against cannot be recovered from the JSON — only its verdict can.