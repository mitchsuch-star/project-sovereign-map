# The Generals' Odds of Death: a measured memo

> **Filed:** September 25, 2026. **Status:** measured and recommended only. Nothing is built, and the ruling belongs to the user. The design row is `DESIGN_REFINEMENT.md` **GE-D1 "The Generals' Mortality"**.
> **The ask (user, September 25, 2026):** "check the odds of death for generals". It rides with GE-1 (`docs/NEXT_SESSION_PROMPT.md` §B).
> **Engine:** master `1d3f2535` (content hash `87953a91a5f5`, driver `0a40b28e8a35`, tree clean), measured in an isolated worktree. Platform: CPython 3.13.12 on Windows 11, `PYTHONHASHSEED=0`, mock parser, Mode A.
> **Sample:** 25 seeded 40-turn campaigns on `tools/playtest_driver.py`, containing 884 battles. The 96 archived digests in `docs/audits/playtest_digests/` were also mined.

---

## §0 The answer in one screen

1. **A general has no personal death roll.** He falls only when his corps is removed at `WorldState.destroy_marshal`.
   - In practice that means one of two things: his corps is ground below the 50-man rubble floor in a battle or charge, or his nation is eliminated.
   - Four other removal roads exist in code. None was taken in 1,000 measured turns: attrition, internment, dismissal and bombardment.
   - The Emperor never dies. The same seam converts his removal into a capture.
2. **Capture, not death, is how generals leave the field.** Across the 25 runs:
   - 11 generals died in the field: 8 French and 3 AI.
   - 19 were removed by nation elimination. Every one is Deroy of Bavaria.
   - 156 were captured: 120 French and 36 AI.
   - For France, captures outnumber field deaths about **15 to 1**.
   - Only 2 of the 120 French captives were ever released. Both came home at the turn-4 peace on the commanded arm.
3. **Per battle, attackers never died** (0 of 884 attacker-sides).
   - A beaten defender died **2.2%** of the time and was captured **21.9%**.
   - A stalemate killed nobody.
   - The 20 decisive defeats (`attacker_victory`) killed the defender 8 times and captured him 10 times. These were almost all remnants being finished off.
4. **Every field death was a corps that was already a remnant, or one hit by a charge or a stacked field.**
   - Six of the eleven were remnants of 59–3,615 men that the rubble floor finished. Five were overkill.
   - **One British cavalry marshal, Paget** (commissioned turn 4, aggressive, shock 8), made **6 of the 8 French kills**. He also struck the final blow in 4 of the Emperor's 12 captures.
5. **France's losses by turn 20 / 30 / 40:**
   - **Commanded arm (as PLAYTESTING prescribes):** 0 dead and 0 captive at every checkpoint on all three seeds.
   - **Ambient arm:** 0/0/1, 0/0/1 and 0/0/0 dead. Captives were 1/6/7, 1/5/7 and 1/1/1.
   - **The September 11 re-score's "four French marshals destroyed between turns 30 and 37" does not reproduce** on either commanded variant (§3.7).
6. **Napoleon's corps was destroyed in battle in 12 of 25 campaigns** (turns 15–35), and never on the commanded-accept arm. Each time the engine converted his death into capture.
   - Each time the corps had first been ground down by 3–6 Guard tolls to a remnant of 55–255 men.
   - **The "Guard is spent" question never reached the player** (0 of 80 sovereign fate checks).
   - At GE-1's recommended 0.15 death roll, he would die in about **7% of campaigns** (§3.8).
7. **Recommendation:**
   - **(a) Yes to a personal roll**, bounded to the *leading* general of the *losing* side in a real battle: 8% wounded (out 3 turns), 1% killed. That gives about one wound and about 0.13 deaths per French campaign, which matches the historical marshal rate.
   - **(b) No death on the attrition, internment and nation-elimination roads,** nor as a side effect of the 50-man floor. The man survives his corps. The floor still ends the corps and sends the man through the capture/escape check.
   - **(c)** The interplay with the Marshalate, the glory ladder, the reward economy, GE-1 and GR5 is in §5.

---

## §1 Facts, stated first (read from code at `1d3f2535`)

### 1.1 There is no personal death roll; there is a removal seam

- `WorldState.destroy_marshal(marshal, cause, victor="", log=True)` (`backend/models/world_state.py:3096`) is the PC15-1 removal seam. It performs these steps in order:
  1. Refuses a prisoner (`:3120`, `captured_by` set).
  2. Converts a sovereign into a capture (`:3131–3137`: `capture_marshal(..., context=f"death_guard:{cause}")`, returns `False`).
  3. Pops the marshal (`:3143`).
  4. Retires his reward and ask notices (`:3153`).
  5. Writes the tombstone `fallen_marshals[name] = {nation, turn, location, cause}` (`:3160`; serialized at `:7639` / `:8168`).
  6. Unless `log=False`, logs `marshal_destroyed` (`:3168`).
- **No function anywhere rolls for a general's life.** He dies only when his *corps* is removed. The man and the corps are one object.
- **"ONE seam" holds for every standing marshal, but not for every removal.**
  - `_eliminate_nation` (`world_state.py:4498`) sweeps its own marshals through the seam (`:4577`).
  - It pops a **prisoner** of the eliminated court directly (`:4586`), writes the tombstone itself, and logs no event.
  - That second removal site should be named in any spec that says "the death roll lives at the ONE seam".

### 1.2 The cause census (every `destroy_marshal` caller in `backend/`)

The expected list was `battle`, `charge`, `attrition`, `interned`, `dismissed` and `nation_eliminated`. It is confirmed with **one addition, `bombardment`**, and with dismissal having two callers.

| `cause` | Caller(s) | What it means | Measured (25 runs) |
|---|---|---|---|
| `battle` | `combat_executor.py:7657` (defender), `:7664` (attacker), `:7749` (a non-primary participant in a coordinated battle) | the corps reached 0 in the exchange | **9** removals (France 6, Austria 2, Britain 1); all defenders |
| `charge` | `combat_executor.py:9221` / `:9226` (the charge executor); `world_state.py:13737` / `:13743` (the reckless-cavalry auto-charge, `_process_reckless_cavalry_turn_start` `:13296`) | the corps reached 0 in a charge (×2 casualties both ways, `combat.py:666`) | **2** (France 2, both by Paget) |
| `bombardment` | `combat_executor.py:6615` (the auto-bombardment dead-defender exit) | guns killed the defender before the assault | 0 |
| `attrition` | `world_state.py:7285` (the V2-29 zero-strength sweep in `process_supply_attrition`, `:7174`) | a corps at 0 strength that nothing else removed | 0 |
| `interned` | `game_logic/withdrawal.py:1361` (`_intern`, `:1333`) | the safe passage lapsed on sovereign soil | 0 |
| `dismissed` | `commands/disobedience.py:1955` (the redemption "dismiss" arm); `commands/meta_executor.py:1796` (debug) | the player dismissed him | 0 (the driver answers redemption with `grant_autonomy`, `playtest_driver.py:521`) |
| `nation_eliminated` | `world_state.py:4577` (+ the direct prisoner pop `:4586`) | his court ceased to exist | **19** (every one Deroy of Bavaria, turns 3–10, taking 4,730–16,767 men with him) |
| *(refused: prisoner)* | the `:3120` guard | the coordinated cleanup (`:7749`) reached a man the rout loop had just captured | 22 — the PC15-1 guard working |
| *(refused: sovereign → capture)* | `:3131–3137` | the Emperor's corps reached 0; he was taken instead | **12** (all `death_guard:battle`) |

- **The `attrition` road is structurally rare.**
  - Supply attrition is capped at 6% a turn (`world_state.py` `supply_attrition_rate`, `min(0.06, …)`), so it can never take the last man.
  - The sweep catches only corps that reached 0 by some other road without a removal of their own. The garrison assault is one: it writes `strength = max(0, …)` with no rubble floor (`combat_executor.py:3537`).

### 1.3 What kills a corps: the rubble rule, the remnant rule, and overkill

- **Casualties to a beaten defender:**
  - `combat.py:1192–1216`: `min(0.60, 0.15 × attacker_eff / defender_eff)` of his body pool.
  - × shock `(1 + attacker_shock/20)` (`:493`).
  - × defense `(1 − defender_defense/20)` / stance (`:639–642`).
  - × the 2d6 multiplier `0.85 + 0.025 × modified roll`, i.e. 0.90–1.20 (`:165–220`).
  - × 2 on a glorious charge (`:666`).
  - In a coordinated field the pool is the whole field and the losses are distributed (FA-D29).
- **The rubble rule.** `Marshal.take_casualties` (`models/marshal.py:1552`) zeroes any corps left with **fewer than 50 men** (`:1555`).
- **The remnant rule, in numbers.**
  - A lone defender loses at most about 0.6 × 1.4 × 0.75 × 1.2 ≈ **0.76** of his corps against a shock-8 attacker, and about **0.89** at the extremes.
  - So a corps above roughly **200–450 men** cannot be rubbled by one lone attack. Below that line the 50-man floor finishes it.
  - The F4 landing record measured both cases (`ENDGAME_PLAN.md` §1 F4). A 900-man corps attacked by 52,000 men lost 136–467 and stood. A 60-man remnant was destroyed outright.
- **Overkill.** A glorious charge, or a coordinated field whose pooled losses land on one corps, pushes the fraction past 1.0. Five mid-sized corps (1,382–3,615 men) died this way (§3.6).
- **A rout never kills.** `rout_survivors` (`combat.py:115`) floors the survivors at 1,000 and never lets them exceed the army. The surrounded "shatter" (`combat_executor.py:4446`) sends 3–10% to the capital.
- **A rubbled corps never reaches the fate check.**
  - The removal at `:7657` runs *before* the forced-retreat arm (`:7671`).
  - `_check_marshal_fate` also returns `None` for strength ≤ 0 (`:3883`).
  - So a general whose corps is annihilated is killed. He is never captured and never asked.

### 1.4 The capture road: the W6-7 fate check, and how a captive comes home

- **Trigger.** `_check_marshal_fate` (`combat_executor.py:3864`) runs when a beaten corps is forced to retreat (morale ≤ 25, `combat.py:76`; 15 for Habsburg Resolve) and at least one of these holds:
  - post-battle strength is **under 5,000** (`MARSHAL_FATE_STRENGTH_FLOOR`, `:3800`);
  - there is no safe retreat;
  - the only retreat is desperation soil.
- **Outcomes:**
  - **Encircled:** captured outright (`:4046`).
  - **Aggressive player marshal:** asked "fight to the last / attempt breakout".
    - Fighting bleeds the enemy and is **always** followed by capture (`_resolve_last_stand_fight`, `:4186`).
    - A breakout escapes **50%** of the time (`0.60 − 0.10`, `:3801/:3803`).
  - **Aggressive AI marshal:** fights on home or capital-adjacent ground, otherwise breaks out at 50%.
  - **Everyone else:** escapes **60%** / captured **40%** (`:4122`).
- **On capture** (`capture_marshal`, `world_state.py:5194`), half his remaining men go home to the manpower pool, and he is held at the captor's capital at strength 0.
- **Release.** A captive comes home only by one of these roads, at 5,000 men (`RANSOM_RETURN_STRENGTH`, `:5184`):
  - a peace between the two courts (`release_mutual_prisoners`, `:5379`);
  - a `prisoner_return` clause (`:11682`);
  - for the sovereign only, the storming of the city where he is held (`:4487`).

### 1.5 The Emperor

- When the Emperor is cornered but not encircled, the Guard buys the road and **30%** of his corps dies covering it (`GUARD_ESCAPE_TOLL`, `:3809`).
- The toll is refused when paying it would leave him under 50 men (`THE_GUARD_CANNOT_BUY_A_ROAD_IT_CANNOT_PAY` / `GUARD_RUBBLE_FLOOR = 50`, `:3820–3821`, `:3963–3965`). The player is then asked to fight or cut his way out.
- When his corps is destroyed, `destroy_marshal` converts the removal into capture: "a sovereign never dies in v1" (`NAPOLEON_SPEC.md:511`).
- GE-1 now owns his death (`GAME_END_SPEC.md` §3 as amended September 25, 2026; `ENDGAME_PLAN.md` §3).

---

## §2 Method

- **The driver.** `tools/playtest_driver.py` Mode A: in-process, seeded, popup-answering, with the policy logged in every digest header.
- **The probe.** The driver was wrapped with class-level hooks. The source is in Appendix B; it is not committed. It recorded, **uncapped**:
  - every `WorldState.destroy_marshal`, `capture_marshal` and `release_captured_marshal` call (with the marshal's strength at the call and the return value);
  - every `battle`, `garrison_assault`, `last_stand`, forced `retreat` and `marshal_commissioned` event (with strength-before and casualties);
  - every `CombatExecutor._check_marshal_fate` call (strength, personality, and whether it ended in a capture, a question, a Guard toll or a free retreat);
  - a board snapshot after every end turn (`fallen_marshals`, every marshal's `captured_by`, provinces).
  - The hooks call the original and record. They never draw RNG or change a return value.
  - **Verified:** the six primary arms were run twice, without and with the fate-check hook. Battles, casualties, removals, captures and per-turn provinces were identical.
- **Arms.** Each arm ran 40 turns on seeds `historical`, `ulm` and `austerlitz` unless stated. The exact commands are in Appendix A.

| Arm | Driver flags | Runs | What it is |
|---|---|---|---|
| **ambient** (primary) | `--turns 40 --seed <s>` | 3 | France issues no orders; policy defaults (objection trust, diplomacy decline, last stand `first` = fight to the last, redemption grant_autonomy) |
| **commanded** (primary) | `--script tools/playtest_scripts/commanded_full40.json --turns 40 --seed <s> --diplomacy accept` | 3 | the PLAYTESTING.md commanded arm; France signs the table, and peace lands on turn 4 |
| ambient, more seeds (supplementary) | as ambient, seeds `jena marengo wagram eylau friedland borodino leipzig` | 7 | enlarges the per-battle denominator |
| **war-long** (supplementary) | commanded script with `--diplomacy decline` | 3 | a France that fights every turn and refuses peace |
| **tyrant** (supplementary) | `--script tools/playtest_scripts/weird_tyrant.json --turns 40 --seed <s>` | 3 | aggressive script (insist, charge); orders end at loop 30 |
| **breakout** (sensitivity) | ambient and war-long with `--last-stand breakout` | 6 | the driver's other answer to the last-stand question |

- **Linking a fate to its battle.** A charge logs its battle event just *after* the removal, so the battle that immediately follows in the same turn (within 3 events) is taken first. Otherwise the fate is linked to the most recent earlier battle, within two turns, in which the man was attacker or defender. Nation-elimination removals are never linked.
- **Stated limits.**
  - The driver is a camera with reflexes, not a player.
    - The ambient France is *undefended by construction*, which inflates its captures.
    - The default last-stand answer is fight-to-the-last, which ends in **certain** capture (`playtest_driver.py:550`, `:2279–2282`). The breakout arms show the alternative.
    - France never commissions from the Marshalate on any arm, because the scripts never type the verb. The AI did so 1–6 times per run.
  - No human-played or live-parser campaign is in the sample.

---

## §3 Results

### 3.1 The primary arms, per campaign

France's roster at boot is 8: Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena, and Napoleon.

| Arm · seed | Battles | Fallen (turn, cause) | French captured (turn, how) | Other captures · releases | France at t40: standing / captive / dead / provinces |
|---|---|---|---|---|---|
| ambient · historical | 38 | Deroy (Bav.) t4 nation_eliminated · **Davout t30 battle (Paget)** | Bernadotte t9 overrun · Massena t22 last stand · Lannes t25 LS · Murat t25 LS · Soult t29 overrun · Ney t30 LS · **Napoleon t31 death_guard (Britain)** | Paget (Brit.) by Spain t10 · released t16 (peace) | 0 / 7 / 1 / 5 |
| ambient · ulm | 63 | Deroy t5 nation_eliminated · **Bernadotte t35 battle (Charles)** | Lannes t9 LS · Davout t24 overrun · Massena t26 LS · Murat t26 LS · Ney t27 LS · **Napoleon t31 death_guard (Austria)** · Soult t35 overrun | Paget by Spain t11 · released t16 | 0 / 7 / 1 / 0 |
| ambient · austerlitz | 23 | Deroy t5 nation_eliminated | Massena t14 LS | Paget by Spain t11 · released t16 | 7 / 1 / 0 / 5 |
| commanded · historical | 10 | — | — | — | 8 / 0 / 0 / 28 |
| commanded · ulm | 12 | Deroy t3 nation_eliminated | Bernadotte t2 overrun | released t4 (peace) | 8 / 0 / 0 / 28 |
| commanded · austerlitz | 11 | Deroy t3 nation_eliminated | Bernadotte t3 overrun | Mack (Aust.) taken by France t3 · both released t4 (peace) | 8 / 0 / 0 / 28 |

### 3.2 Per campaign, by pool

| Pool | Runs | Battles / run | French field deaths / run | French captured / run | Emperor's corps destroyed | AI field deaths / run | AI nation-elim / run | AI captured / run |
|---|---|---|---|---|---|---|---|---|
| ambient (10 seeds) | 10 | 39.0 | 0.30 | 5.2 | 5 of 10 | 0.10 | 1.00 | 0.9 |
| commanded + accept | 3 | 11.0 | 0 | 0.67 (both home in 2 turns) | 0 of 3 | 0 | 0.67 | 0.33 |
| war-long (war + tyrant) | 6 | 36.0 | 0.33 | 5.7 | 3 of 6 | 0.17 | 0.33 | 3.0 |
| breakout sensitivity | 6 | 40.8 | 0.50 | 5.3 | 4 of 6 | 0.17 | 0.83 | 1.3 |
| **all** | **25** | **35.4** | **0.32** | **4.8** | **12 of 25** | **0.12** | **0.76** | **1.4** |

**French captures by how they happened, all 25 runs (120):**

| How | Count | What it means |
|---|---|---|
| last stand | 57 | the driver's "fight to the last", or the FA-1 "no word came" resolution |
| overrun | 35 | the 40% roll, or a failed AI-rule breakout |
| failed breakout | 12 | breakout arms only |
| `death_guard` | 12 | the Emperor |
| overrun unanswered | 3 | FA-1 |
| encircled | 1 | |

- Choosing breakout instead of fight barely moves the total: 17 vs 15 on the ambient trio, and 18 vs 19 on the war-long trio. A man who breaks out is usually cornered again.
- **AI captures (36)** are 35 overrun and 1 encircled.
- **Releases:** 22, all by peace treaty (France 2, AI 20).
- **Captives still held at turn 40:** France 118, AI 16.

### 3.3 Per-battle odds, all 25 runs (884 battles)

Outcomes: `attacker_tactical_victory` 486 · `defender_tactical_victory` 176 · `stalemate` 202 · `attacker_victory` 20 · `defender_victory` 0.

| Role · result | Side-instances | General died | General captured |
|---|---|---|---|
| attacker · won | 506 | 0 | 0 |
| attacker · stalemate | 202 | 0 | 2 (1.0%) |
| attacker · lost | 176 | **0** | 11 (6.2%) |
| defender · won | 176 | 0 | 3 (1.7%) † |
| defender · stalemate | 202 | 0 | 13 (6.4%) |
| defender · lost, tactical | 486 | 3 (0.6%) | 101 (20.8%) |
| defender · lost, decisive (`attacker_victory`) | 20 | **8 (40%)** | **10 (50%)** |
| **defender · lost, all** | **506** | **11 (2.2%)** | **111 (21.9%)** |
| — of which France | 339 | 8 (2.4%) | 81 (23.9%) |
| — of which AI | 167 | 3 (1.8%) | 30 (18.0%) |

† The link window assigns a few captures from a later, unlogged action to a battle the man won. That noise is at most 3 of 884.

**Losing side, by corps strength before the battle (both roles):**

| Corps before | Losing sides | Died | Captured |
|---|---|---|---|
| under 1,000 | 66 | 6 (9.1%) | 17 (25.8%) |
| 1,000–4,999 | 141 | 5 (3.5%) | 41 (29.1%) |
| 5,000–14,999 | 246 | 0 | 57 (23.2%) |
| 15,000 and over | 229 | 0 | 7 (3.1%) |

- Per pool, a beaten defender died 1.9% of the time on the ambient pool, 0% on commanded, 2.2% on war-long and 3.1% on breakout. It was captured 20.8%, 12.5%, 28.9% and 18.3% of the time respectively.
- No garrison assault killed a general.

### 3.4 The fate check, all 25 runs (670 checks)

| Who | Corps | Checks | Captured on the spot | Asked (player) | Slipped away / no fate | Other |
|---|---|---|---|---|---|---|
| France (marshals) | under 5,000 | 204 | 49 | 85 | 63 | 7 |
| France (marshals) | 5,000+ | 218 | 7 (encircled / desperation) | 17 | 194 | — |
| AI | under 5,000 | 79 | 34 | — | 45 | — |
| AI | 5,000+ | 89 | 2 | — | 87 | — |
| the Emperor | any | 80 | 0 | **0** | 6 (no trigger) | **74 Guard tolls** |

- Where no question was asked, 49 of 112 French remnants under 5,000 were taken (44%), and 34 of 79 AI remnants (43%). This matches the 40% rule plus encirclement.

### 3.5 Removals by nation, all 25 runs

| Nation | Died in the field | Nation elimination | Captured | Released |
|---|---|---|---|---|
| France | 8 (battle 6, charge 2) | — | 120 | 2 |
| Bavaria | — | 19 | 2 | 2 |
| Austria | 2 (Mack, t9, twice — `cmdwar-ulm` and its breakout twin share the opening) | — | 15 | 1 |
| Britain | 1 (Paget, t25, by Ney) | — | 18 | 17 |
| Spain | — | — | 1 | — |

### 3.6 How the eleven died

| Run | Turn | General | Killed by | Corps before | Casualties | Mechanism |
|---|---|---|---|---|---|---|
| ambient · historical | 30 | Davout (Fr.) | Paget | 3,120 | 3,338 | overkill (decisive) |
| ambient · ulm | 35 | Bernadotte (Fr.) | Archduke Charles | 72 | 44 | rubble (28 left) |
| ambient · jena | 36 | Bernadotte (Fr.) | Mack | 59 | 29 | rubble (30 left) |
| ambient · wagram | 25 | Paget (Brit.) | Ney | 3,615 | 3,576 | rubble (39 left) |
| war-long · ulm | 9 | Mack (Aust.) | Lannes | 106 | 89 | rubble (17 left) |
| tyrant · austerlitz | 29 | Soult (Fr.) | Paget | 1,382 | 1,436 | overkill |
| tyrant · austerlitz | 30 | Davout (Fr.) | Paget (charge) | 1,635 | 2,826 | overkill (×2 charge) |
| breakout · historical | 31 | Davout (Fr.) | Paget | 642 | 598 | rubble (44 left) |
| breakout · historical | 32 | Soult (Fr.) | Paget (charge) | 3,348 | 5,536 | overkill (×2 charge) |
| breakout · ulm | 40 | Soult (Fr.) | Paget | 232 | 238 | overkill |
| breakout-war · ulm | 9 | Mack (Aust.) | Lannes | 106 | 89 | rubble (17 left) |

- **Paget made 6 of the 8 French kills.** He is Britain's commissioned cavalry marshal (aggressive, shock 8, no ability), with a corps of 3,270–4,755 men. No general died while attacking. No general died in a stalemate.

### 3.7 France by turn 20 / 30 / 40 — and the September 11 claim

**France dead / captive after 20 / 30 / 40 turns, with provinces at turn 40:**

| Arm · seed | t20 | t30 | t40 | Prov. t40 | Emperor taken |
|---|---|---|---|---|---|
| ambient · historical | 0 / 1 | 1 / 6 | 1 / 7 | 5 | t31 |
| ambient · ulm | 0 / 1 | 0 / 5 | 1 / 7 | 0 | t31 |
| ambient · austerlitz | 0 / 1 | 0 / 1 | 0 / 1 | 5 | — |
| **commanded · historical / ulm / austerlitz** | **0 / 0** | **0 / 0** | **0 / 0** | 28 / 28 / 28 | — |
| ambient · jena / marengo / wagram | 0/2 · 0/0 · 0/2 | 0/3 · 0/2 · 0/4 | 1/7 · 0/3 · 0/7 | 1 · 4 · 4 | t35 · — · t31 |
| ambient · eylau / friedland / borodino / leipzig | 0/3 · 0/2 · 0/2 · 0/1 | 0/4 · 0/7 · 0/7 · 0/1 | 0/4 · 0/8 · 0/7 · 0/1 | 8 · 1 · 5 · 7 | — · t28 · — · — |
| war-long · historical / ulm / austerlitz | 0/2 · 0/6 · 0/2 | 0/4 · 0/7 · 0/6 | 0/4 · 0/8 · 0/7 | 27 · 0 · 10 | — · t15 · t29 |
| tyrant · historical / ulm / austerlitz | 0/3 · 0/0 · 0/2 | 0/4 · 0/5 · 2/6 | 0/4 · 0/5 · 2/6 | 4 · 3 · 2 | — · — · t28 |

- On 4 of 10 ambient seeds France has no standing marshal at turn 40, and on 6 of 10 it has one or none.
- **The September 11 claim** (`PLAYTEST_FULL_RESCORE_2026_09_11.md:433`, repeated in `PLAYTESTING.md:424`, `DESIGN_REFINEMENT.md` FA-S17-D6 and `CLAUDE.md`) was "four French marshals are destroyed between turns 30 and 37 on the historical seed" of the commanded arm. **It does not reproduce.**
  - Today the commanded historical arm destroys **0** and captures **0** French marshals in 40 turns. It fights 10 battles, is at peace from about turn 4, and holds 28 provinces.
  - The war-long variant (the same script with `--diplomacy decline`) destroys **0** and captures **4**: Davout t16, Ney t17, Lannes t29, Murat t29.
  - The September 11 run has no archive (`PLAYTESTING.md` marks that row UNCITABLE). The nearest archived run is `docs/audits/playtest_digests/cmd-historical` (September 12, 15:19). It records Massena and Ney as *prisoners of Austria* by turns 14–15, and carries no "corps DESTROYED" headline.
  - That fits a count that took captives for dead, but it cannot be confirmed. The claim should be dated, not cited.

### 3.8 Napoleon (the raw figure for GE-1's "The Eagle Falls")

| Run | Taken (turn, captor) | Guard tolls before | Corps at the last toll | Final blow: attacker vs. corps |
|---|---|---|---|---|
| ambient · historical | t31, Britain | 3 | 90 → 63 | Paget vs 63 |
| ambient · ulm | t31, Austria | 5 | 106 → 75 | Charles vs 74 |
| ambient · jena | t35, Austria | 6 | 99 → 70 | Mack vs 70 |
| ambient · wagram | t31, Austria | 4 | 90 → 63 | Charles vs 63 |
| ambient · friedland | t28, Austria | 5 | 79 → 56 | Mack vs 55 |
| war-long · ulm | t15, Austria | 6 | 79 → 56 | Charles vs 141 |
| war-long · austerlitz | t29, Austria | 4 | 82 → 58 | Charles vs 58 |
| tyrant · austerlitz | t28, Britain | 3 | 236 → 166 | Paget vs 163 |
| breakout · historical | t32, Britain | 3 | 378 → 265 | Paget vs 255 |
| breakout · ulm | t31, Austria | 6 | 81 → 57 | Charles vs 56 |
| breakout-war · ulm | t16, Austria | 6 | 79 → 56 | (unlinked) |
| breakout-war · austerlitz | t27, Britain | 5 | 201 → 141 | Paget vs 139 |

- Not taken on 13 of 25 runs, including all 3 commanded-accept runs.
- Two ambient seeds ended turn 40 with the Emperor alive on a remnant: borodino (55 men after 6 tolls) and eylau (129 men after 3).
- **All 12 captures are `death_guard:battle`.** His corps was destroyed in a battle, and the seam turned a death into a capture.
- The Guard's "spent" question fired **0 times in 80 checks**. The toll rule pays down to about 56 men, and the next defeat rubbles the corps before the question can be asked.
  - A zero-strength marshal never reaches the fate check (`:3883`).
  - The next-toll warning (`THE_GUARD_COUNTS_ITS_ROADS`) can fire. The question cannot.
- **Under GE-1's recommended `SOVEREIGN_DEATH_CHANCE = 0.15`** at the corps-destroyed seam, expected Emperor deaths in this sample are 0.15 × 12 = **1.8 of 25 campaigns, about 7%**.
  - Ambient: 0.75 of 10 (7.5%). Commanded-accept: 0 of 3. War-long: 0.45 of 6 (7.5%).
- No foreign sovereign is authored in 1805, so the arm is France-only in practice. (NP-6 "The Three Emperors" would change that.)

### 3.9 The committed archives (96 digests, 2,885 turns)

- The digest keeps a French destruction only if it wins the morning dispatch headline, so these counts are a lower bound.
- **Before September 4, 2026** (52 runs, 1,269 turns): 17 French "corps has been DESTROYED" headlines in 12 runs, 14 French captures, and the Emperor taken in 4 runs.
- **From September 4 onward** (44 runs, 1,616 turns): **0** destroyed headlines, 26 captures, and the Emperor taken in 2 runs.
- The swing lands on FA-1 slice 2, "No word came" (September 4). That slice ended the loop in which a cornered marshal was shot six times standing. `BUG_FIXES.md` records the prior run's four DESTROYED French marshals becoming "three PRISONERS and one loss".
- Archived French losses by general: Lannes 9 destroyed, Ney 5, Massena 2, Murat 1. Bernadotte appears as a captive in 20 runs, the most-captured French marshal on the September boards.
- France took an enemy general prisoner in 33 archived runs, most often Mack (turns 2–7) and Archduke John.

---

## §4 Against history

- In the 1805–07 campaigns the game models, **no Marshal of the Empire died in the field.** Defeated corps ended in capitulation, not annihilation:
  - Mack at Ulm (October 1805);
  - Hohenlohe at Prenzlau (October 1806);
  - Blücher at Ratekau (November 1806).
- The one army commander killed was the Duke of Brunswick, mortally wounded at Auerstedt (1806). Prince Louis Ferdinand fell at Saalfeld (1806).
- The only marshal captured was Victor, taken in early 1807 and exchanged for Blücher within weeks.
- Across the whole 1805–1815 era, three Marshals of the Empire died of battle wounds: Lannes (Aspern-Essling, 1809), Bessières (Rippach, 1813) and Poniatowski (Leipzig, 1813, three days a marshal). Duroc, the Grand Marshal of the Palace, fell in 1813.
- That is roughly **1.5% per marshal-year** in the field, and about **0.5% per marshal-year** captured.
- Generals of division and brigade died far more often: Valhubert at Austerlitz, and d'Hautpoul at Eylau.
- Marshals were **wounded** far more often than killed. Augereau was wounded at Eylau when his corps was shattered in the snow. Oudinot is credited with some thirty-four wounds.
- **The game at its current settings.** France fields 8 generals for 40 turns, about 1.64 years, or 13.1 marshal-years per campaign.

| Pool | French deaths per marshal-year | French captures per marshal-year |
|---|---|---|
| ambient | 2.3% | 40% |
| war-long | 2.5% | 43% |
| commanded | 0% | 5% (both released within two turns) |
| history (1805–1815) | about 1.5% | about 0.5% |

- **The death rate is the right order of magnitude,** about 1.5 to 2 times history, but it arises from the wrong mechanism. A marshal dies only when his corps is ground to a remnant and finished off, which almost never happened in 1805–07. He never dies as Lannes, Brunswick and Bessières did: hit at the head of a real army in a real battle.
- **The capture rate is about 80 times history** wherever France fights on. The captives are never ransomed short of a peace.
- The history the game cannot yet tell is the wound: a corps broken, the general carried from the field, and back in the line a few turns later.

---

## §5 Recommendations (measure-and-recommend; nothing built)

### (a) A personal wound-or-death roll for the leading general of a lost battle: **yes, bounded**

**Proposed shape: "The Fortunes of War".**

- **Who rolls.** Only the *leading* marshal (the primary attacker or defender) of the side that **lost** a battle, and only when both of these hold:
  - his corps lost **at least 25%** of its pre-battle strength;
  - the engagement is a battle by `battle_scale.is_a_battle` (at least 1,000 casualties on both sides together, `battle_scale.py:75–78`). Skirmishes never roll.
  - Winners and stalemates never roll. That matches the measured fact that nobody died winning, and it keeps success from being punished.
- **The roll.** One draw per qualifying loss, taken through the campaign-seed helpers (`campaign_variance.seeded_int`, `game_logic/campaign_variance.py:67–107`). Never the module RNG, so a campaign seed replays its wounds.
  - **Killed 1%. Wounded 8%.** Otherwise unhurt. Both numbers are in-band tunable.
- **A wound.**
  - He is out of command for **3 turns**, on one serialized field (`wounded_until_turn`).
  - His corps stays on the map under his chief of staff. It defends and moves but cannot attack or take a strategic order, and his ability is off.
  - He keeps his glory, estates and trust. The dispatch and the Moniteur carry the beat.
- **A death.**
  - The man dies and **his corps survives**. Its men pass to the nearest friendly corps within three regions, or disperse to the manpower pool. This reuses the dismissal's transfer, `disobedience.py` redemption "dismiss" arm.
  - The tombstone goes through `destroy_marshal` with a new cause, `killed_in_action`, and the Moniteur and the dispatch carry the death.
- **The sovereign is excluded from this roll.** His death belongs to GE-1's "The Eagle Falls" at the corps-destroyed seam. A wounded Emperor, which would suspend the Presence aura, stays out of v1 and is re-opened at the Victory & Objectives pass.
- **Expected rates.** Measured qualifying losses per campaign:

| Pool | France: qualifying losses | France: wounds / deaths | AI courts together: qualifying losses | AI: wounds / deaths |
|---|---|---|---|---|
| ambient | 12.2 | about 1.0 / 0.12 | 6.1 | 0.5 / 0.06 |
| war-long | 13.0 | about 1.0 / 0.13 | 10.8 | 0.9 / 0.11 |
| commanded | 4.0 | 0.3 / 0.04 | 5.0 | 0.4 / 0.05 |

  - The historical anchor is about 1.5% per marshal-year × 13.1 marshal-years ≈ 0.2 deaths per campaign. The proposal sits at that anchor, with wounds as the common case.

### (b) Should attrition, internment and nation elimination kill a general? **No. The man survives his corps.**

- **Nation elimination** is the largest single source of general removals in the sample: 19 of 30, every one Deroy, each taking 4,730–16,767 men.
  - A general whose court falls should leave the field **alive**. Tombstone him as `exiled`, which the dispatch, the chronicle and GE-1's exile story must never narrate as a death.
  - The real Deroy served on and died at Polotsk in 1812. Optionally, an exile could join the Marshalate bench of a court at war with his destroyer; that is out of scope for v1.
- **Attrition** (0 of 1,000 turns) and **internment** (0) cost nothing to change, and there is no measured balance risk.
  - A general whose corps starves or is interned should return to his capital in the existing **depot** state: strength 0, exempt from the sweep (`ADMINISTRATIVE_EXEMPT_FROM_ATTRITION`, `world_state.py:52`), raised again with a levy.
  - Internment is already homed as "The Interned Column", captivity by the neutral court (`DESIGN_REFINEMENT.md:514`).
  - Dismissal is correct as a removal, but its `dismissed` tombstone must also never read as a death.
- **Annihilation of a remnant in battle** made 6 of the 11 field deaths: the 50-man floor finished corps already at or below 642 men, and one of 3,615.
  - Route a corps rubbled in battle or charge (non-sovereign) through the **fate check** — capture 40% / escape 60%, encircled = capture — instead of an automatic death.
  - Death then comes **only** from roll (a), and it becomes legible as a risk to the *man* rather than a side effect of a floor.
  - This moves AI outcomes (Mack's turn-9 death on the war-long ulm arm becomes a capture or an escape). It needs a flip lever and one `BASELINE_SERIES` re-record with attribution.

### (c) Interplay

- **The Marshalate** (`MARSHAL_RECRUITMENT_SPEC.md`).
  - France's authored bench is six men (Mortier, Grouchy, Suchet, Oudinot, Augereau, Marmont; 3,500–6,000 gold). It is the recovery path for deaths, and after (b) the depot is the recovery path for survivors.
  - The AI commissioned 1–6 times per run through the P1.75 rung (GR5 holds).
  - The dispatch's PT-J4 bench note, which already rides the destruction beat, should ride the death and the wound beats.
- **The glory ladder and jealousy.**
  - A dead marshal leaves the ladder, so the crown may pass.
  - The build must verify three things: envy aimed at a dead rival resolves (CA8-D3's rival memory re-fixes on the man "while he still stands above"); a wounded man accrues no glory while out; and a wound does not count as the literal's sidelining.
- **The reward economy (ES-7).** A death ends his rente and returns his estates. The seam already retires his reward notices (`world_state.py:3153`). A wounded man keeps his estates and his expectation.
- **GE-1.**
  - **(i)** The exile story reads `fallen_marshals`, and 19 of the 30 tombstones in this sample are Bavaria's fallen court. It must branch on `cause` and never tell a `nation_eliminated`, `dismissed` or `exiled` tombstone as a death in the field.
  - **(ii)** The Emperor's arm sits at the corps-destroyed seam, which (b) leaves untouched for the sovereign.
  - **(iii)** Measured input: the "Guard is spent" question never fires, because the toll pays him down to about 56 men and the next defeat rubbles him. GE-1 should consider treating the Guard as spent below a real floor (for example `rout_survivors`' 1,000), so the player is asked **before** the fatal battle. That is GE-1's ruling.
  - **(iv)** R1's "no free corps and no affordable commission" clock counts both captivity and death as a lost corps. A wounded man's corps still counts as free.
- **GR5.** One roll, one seam, both boards, drawn through the campaign-seed helpers. The AI takes the same odds.
  - The asymmetry the sample shows (France never commissions) is the driver's, not the game's.
- **Pins.** The roll changes AI outcomes, so `BASELINE_SERIES` is re-recorded once with a flip attribution (levers set in the child). M1–M7 run no end turns and should stay byte-identical.

### Re-open condition

If the user declines or defers (a) or (b), re-open when any one of these is measured:

1. A human-played session, or the GE-V pass, reports a named general dying to the 50-man floor, and it reads as arbitrary.
2. On the driver's war-long arm (3 seeds × 40 turns), French field deaths exceed **1 per campaign**, or French captures exceed **5 per campaign** while releases stay at 0.
3. GE-1's Emperor death arm lands with a trigger or a seam that a general roll would have to share.

---

## Appendix A: Exact commands

All commands run from the repository root with `.venv\Scripts\python.exe`.

**The driver arms, digest only, as `PLAYTESTING.md` prescribes:**

```
PYTHONHASHSEED=0 .venv/Scripts/python.exe tools/playtest_driver.py --turns 40 --seed historical --name amb-historical --fresh
PYTHONHASHSEED=0 .venv/Scripts/python.exe tools/playtest_driver.py --script tools/playtest_scripts/commanded_full40.json --turns 40 --seed historical --diplomacy accept --name cmd-historical --fresh
```

Repeat with `--seed ulm` and `--seed austerlitz`.

**The probe (Appendix B), run on each arm.** Each run takes 13–45 seconds of wall time; six to thirteen ran in parallel, each with its own save directory and output directory. The launcher set `PYTHONHASHSEED=0` and `INK_IRON_SAVE_DIR=<scratch>/runs/<name>/saves` per process:

```
python <scratch>/death_probe.py <scratch>/out/<name>.json <driver args> --name <name> --out <scratch>/runs --fresh
```

| `<name>` | `<driver args>` |
|---|---|
| `amb-<s>` for s in historical ulm austerlitz jena marengo wagram eylau friedland borodino leipzig | `--turns 40 --seed <s>` |
| `cmd-<s>` for s in historical ulm austerlitz | `--script tools/playtest_scripts/commanded_full40.json --turns 40 --seed <s> --diplomacy accept` |
| `cmdwar-<s>` | `--script tools/playtest_scripts/commanded_full40.json --turns 40 --seed <s> --diplomacy decline` |
| `tyrant-<s>` | `--script tools/playtest_scripts/weird_tyrant.json --turns 40 --seed <s>` |
| `ambbo-<s>` | `--turns 40 --seed <s> --last-stand breakout` |
| `cmdwarbo-<s>` | `--script tools/playtest_scripts/commanded_full40.json --turns 40 --seed <s> --diplomacy decline --last-stand breakout` |

- Every run's `digest.md` header reads the same provenance line: engine `1d3f2535034a`, content `87953a91a5f5`, driver `0a40b28e8a35`, `dirty: false`, CPython 3.13.12, Windows 11, `PYTHONHASHSEED 0`.
- **Archive mining.** Regex counts over `docs/audits/playtest_digests/*/digest.md` of these lines, bucketed on each archive's `meta.json` `started` date:
  - "Marshal X's corps has been DESTROYED";
  - "MARSHAL CAPTURED — X is taken by";
  - "the Emperor himself is TAKEN";
  - "Marshal X is a prisoner of";
  - "Marshal X of <court> is taken at".

## Appendix B: The probe (`death_probe.py`; not committed; run from the repository root)

```python
"""Generals' death-odds probe (Sept 25, 2026 memo).

Runs tools/playtest_driver.py IN-PROCESS (Mode A) with class-level hooks on
WorldState so every removal / capture / release / battle is recorded
UNCAPPED (the world's event_log rolls at 500 rows; these hooks do not).
Read-only instrumentation: the wrappers call the original and record; they
never consume RNG or change a return value.

Usage (from the worktree root, PYTHONHASHSEED=0 set in the env):
  python death_probe.py <out_json> <driver args...>
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

WORKTREE = os.getcwd()
sys.path.insert(0, WORKTREE)

OUT_JSON = sys.argv[1]
DRIVER_ARGS = sys.argv[2:]

import tools.playtest_driver as D  # noqa: E402

REC = {
    "args": DRIVER_ARGS,
    "events": [],        # recorded log_event rows of interest (uncapped)
    "destroy": [],       # destroy_marshal calls
    "capture": [],       # capture_marshal calls
    "release": [],       # release_captured_marshal calls
    "snapshots": [],     # per-turn board snapshot (after end turn)
}
SEQ = [0]

KEEP_TYPES = {
    "battle", "garrison_assault", "bombardment", "last_stand",
    "marshal_broken", "marshal_destroyed", "marshal_captured",
    "marshal_released", "marshal_interned", "marshal_commissioned",
    "retreat",
}


def _seq():
    SEQ[0] += 1
    return SEQ[0]


def install_hooks():
    from backend.models.world_state import WorldState

    orig_log = WorldState.log_event
    orig_destroy = WorldState.destroy_marshal
    orig_capture = WorldState.capture_marshal
    orig_release = WorldState.release_captured_marshal

    def log_event(self, event, *a, **k):
        try:
            t = event.get("type") if isinstance(event, dict) else None
            if t in KEEP_TYPES:
                if t == "retreat" and not event.get("forced"):
                    pass
                else:
                    row = {}
                    for key, val in event.items():
                        if isinstance(val, (str, int, float, bool)) or val is None:
                            row[key] = val
                        elif isinstance(val, dict):
                            row[key] = {kk: vv for kk, vv in val.items()
                                        if isinstance(vv, (str, int, float, bool))}
                    row["_turn"] = int(getattr(self, "current_turn", 0))
                    row["_seq"] = _seq()
                    row["_ai"] = str(getattr(self, "_ai_phase_nation", "") or "")
                    REC["events"].append(row)
        except Exception as exc:  # never break the game
            REC.setdefault("hook_errors", []).append(f"log:{exc}")
        return orig_log(self, event, *a, **k)

    def destroy_marshal(self, marshal, cause, victor="", log=True):
        m = marshal
        if isinstance(m, str):
            m = self.marshals.get(m)
        info = None
        try:
            if m is not None:
                info = {
                    "name": m.name, "nation": m.nation,
                    "cause": str(cause), "victor": str(victor or ""),
                    "strength": int(getattr(m, "strength", 0)),
                    "location": m.location,
                    "sovereign": bool(getattr(m, "is_sovereign", False)),
                    "already_captured": bool(getattr(m, "captured_by", "")),
                    "in_marshals": m.name in self.marshals,
                    "_turn": int(getattr(self, "current_turn", 0)),
                    "_seq": _seq(),
                    "_ai": str(getattr(self, "_ai_phase_nation", "") or ""),
                }
        except Exception as exc:
            REC.setdefault("hook_errors", []).append(f"destroy:{exc}")
        ret = orig_destroy(self, marshal, cause, victor=victor, log=log)
        if info is not None:
            info["returned"] = bool(ret)
            REC["destroy"].append(info)
        return ret

    def capture_marshal(self, marshal, captor_nation, context=""):
        try:
            info = {
                "name": marshal.name, "nation": marshal.nation,
                "captor": captor_nation, "context": str(context),
                "strength": int(getattr(marshal, "strength", 0)),
                "location": marshal.location,
                "sovereign": bool(getattr(marshal, "is_sovereign", False)),
                "_turn": int(getattr(self, "current_turn", 0)),
                "_seq": _seq(),
                "_ai": str(getattr(self, "_ai_phase_nation", "") or ""),
            }
            REC["capture"].append(info)
        except Exception as exc:
            REC.setdefault("hook_errors", []).append(f"capture:{exc}")
        return orig_capture(self, marshal, captor_nation, context=context)

    def release_captured_marshal(self, marshal_name, reason="ransom"):
        m = self.marshals.get(marshal_name)
        captor = getattr(m, "captured_by", "") if m is not None else ""
        ret = orig_release(self, marshal_name, reason=reason)
        try:
            REC["release"].append({
                "name": marshal_name,
                "nation": getattr(m, "nation", "") if m is not None else "",
                "captor": captor, "reason": str(reason), "returned": bool(ret),
                "_turn": int(getattr(self, "current_turn", 0)),
                "_seq": _seq(),
            })
        except Exception as exc:
            REC.setdefault("hook_errors", []).append(f"release:{exc}")
        return ret

    WorldState.log_event = log_event
    WorldState.destroy_marshal = destroy_marshal
    WorldState.capture_marshal = capture_marshal
    WorldState.release_captured_marshal = release_captured_marshal

    # The W6-7 fate check: every time a beaten corps is forced to retreat,
    # does the man himself come into question, and how is it answered?
    from backend.commands.combat_executor import CombatExecutor
    orig_fate = CombatExecutor._check_marshal_fate

    def _check_marshal_fate(self, marshal, enemy, world):
        before = {
            "name": marshal.name, "nation": marshal.nation,
            "strength": int(getattr(marshal, "strength", 0)),
            "sovereign": bool(getattr(marshal, "is_sovereign", False)),
            "personality": str(getattr(marshal, "personality", "")),
            "enemy": getattr(enemy, "name", "") if enemy else "",
            "enemy_nation": getattr(enemy, "nation", "") if enemy else "",
            "_turn": int(getattr(world, "current_turn", 0)),
            "_seq": _seq(),
            "_ai": str(getattr(world, "_ai_phase_nation", "") or ""),
        }
        ret = orig_fate(self, marshal, enemy, world)
        try:
            pend = getattr(marshal, "pending_interrupt", None)
            before.update({
                "consumed": ret is not None,
                "message": (ret or "")[:160],
                "captured_after": getattr(marshal, "captured_by", "") or "",
                "strength_after": int(getattr(marshal, "strength", 0)),
                "asked": bool(isinstance(pend, dict)
                              and pend.get("interrupt_type") == "last_stand"),
                "toll_note": bool(getattr(marshal, "_sovereign_toll_note", "")),
            })
            REC.setdefault("fate_checks", []).append(before)
        except Exception as exc:
            REC.setdefault("hook_errors", []).append(f"fate:{exc}")
        return ret

    CombatExecutor._check_marshal_fate = _check_marshal_fate


def snapshot(label="turn"):
    main = sys.modules.get("backend.main")
    world = getattr(main, "world", None) if main else None
    if world is None:
        return
    marshals = []
    for m in world.marshals.values():
        marshals.append({
            "name": m.name, "nation": m.nation,
            "strength": int(getattr(m, "strength", 0)),
            "captured_by": getattr(m, "captured_by", "") or "",
            "sovereign": bool(getattr(m, "is_sovereign", False)),
            "location": m.location,
        })
    fallen = {}
    for name, row in (getattr(world, "fallen_marshals", {}) or {}).items():
        fallen[name] = dict(row) if isinstance(row, dict) else row
    provinces = {}
    try:
        for r in world.regions.values():
            if r.controller:
                provinces[r.controller] = provinces.get(r.controller, 0) + 1
    except Exception:
        pass
    REC["snapshots"].append({
        "label": label,
        "turn": int(world.current_turn),
        "player": world.player_nation,
        "marshals": marshals,
        "fallen": fallen,
        "provinces": provinces,
    })


def main():
    orig_make = D.make_inprocess_transport

    def make(args, out_dir):
        tx = orig_make(args, out_dir)
        install_hooks()
        return tx

    D.make_inprocess_transport = make

    orig_ledger_line = D.Digest.ledger_line

    def ledger_line(self, *a, **k):
        ret = orig_ledger_line(self, *a, **k)
        try:
            snapshot()
        except Exception as exc:
            REC.setdefault("hook_errors", []).append(f"snap:{exc}")
        return ret

    D.Digest.ledger_line = ledger_line

    sys.argv = ["playtest_driver.py", *DRIVER_ARGS]
    code = 0
    try:
        D.main()
    except SystemExit as e:
        code = e.code
    REC["exit_code"] = code
    try:
        snapshot("final")
    except Exception:
        pass
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(REC, fh, indent=1, default=str)
    print(f"[probe] wrote {OUT_JSON} exit={code} events={len(REC['events'])} "
          f"destroy={len(REC['destroy'])} capture={len(REC['capture'])} "
          f"release={len(REC['release'])} snaps={len(REC['snapshots'])}")


if __name__ == "__main__":
    main()
```

- **Probe result on every run:** `hook_errors: None`.
- **Snapshots.** The "turn" snapshot taken after end-turn *N* carries `current_turn = N+1`. "At t20 / t30 / t40" means after 20 / 30 / 40 end turns.
