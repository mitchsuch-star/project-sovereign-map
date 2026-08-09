# CA9 Creative Audit — 16-turn France/1805 campaign, August 8 2026

**Evidence base:** `docs/audits/CA9_PLAY_NOTES_2026_08_08.md` + `docs/audits/CA9_CAMPAIGN_DIGEST_2026_08_08.md`, played live over HTTP against the real backend at `de5af03`. Every claim below was verified against a file:line I opened or a verbatim transcript line, then attacked by a skeptic pass. Findings that did not survive are listed, not deleted.

---

## 1. The verdict

Sixteen turns of France winning almost every battle and losing the campaign to its own systems. The army fought 25 battles, won nearly all of them, annihilated Mack's corps and took him prisoner at Franconia — and lost **~52,700 men to supply attrition and marching against ~38,000 to the enemy**, because the game's central affordance (muster + `support`) concentrates six corps in one province, prices that concentration nowhere, and then bills it at 6%/turn under a headline that prescribes a supply depot the executor refuses to build. The one time I asked for that depot: *"Cannot build in Tyrol — region stability too low (35/100). Need 51+."* Three corps ended up in **Ottoman Albania** — soil no legal order can reach, teleported there by a jealousy-driven autonomous attack that voided a standing MOVE_TO with no message — where they starved for two turns and Murat could no longer reach Vienna. Four times an unrendered war-purpose dialogue silently ate every subsequent command *including `end turn`*, answering `Ney, march on Bohemia` with *"I don't understand that choice, Sire. Options: 1=Conquest, 2=Forced Alliance…"* for a question never displayed. And the terminal step: at war score +19, seven battles won, none lost, enemy holding nothing of ours, the recommended one-click peace was **France paying Austria 77 gold a turn**, labelled *"generous"*, and not even predicted to be accepted (`"outcome": "COUNTER"`). The writing throughout is the best it has ever been — Talleyrand correctly reporting that Austria's revenge design had retargeted onto **Russia**, its own coalition partner, is genuinely superb — but that sentence arrived on turn 16, under a dispatch whose headline was a recruitment bulletin about the price of 10,000 foot at Paris. The game is currently a beautifully-narrated machine for punishing the player for using it as designed.

---

## 2. Findings

### Confirmed

| ID | P | One-line | Root cause | Verdict |
|---|---|---|---|---|
| **F6** | P1 | The war-purpose hard stop is armed but never delivered — swallows every command incl. `end turn`, four times | `combat_executor.py:4489`, `:5410`, `:6323` discard the staged dialogue; only `:3176` stamps `diplomatic_dialogue` | CONFIRMED |
| **F13** | P1 | A jealousy autonomous attack teleported three corps into neutral Ottoman Albania and voided their orders silently | `combat_executor.py:4288` (relocation, no diplomatic guard) + `:5141-5146` (order clear, no event) | CONFIRMED |
| **F12** | P1 | `marshal_captured` (w=95) has no ownership guard — France's own triumph led as a French disaster, twice | `dispatch.py:444-454` never reads `e["nation"]`, which `combat_executor.py:2498` stamps | CONFIRMED |
| **N2** | P1 | The Berthier note on that headline is direction-blind — *"consider his ransom… or make his captors regret the keeping"* when France **is** the captor | `dispatch.py:275` — flat class→string lookup, no direction | CONFIRMED |
| **N1** | P1 | Every arrived reinforcement banks **two** battle-wins for one battle; the lead banks one — the whole ES-7 reward economy is priced off a doubled number | `combat_executor.py:4668-4674` and `:4950-4967`, no dedupe against `atk_participants` | CONFIRMED |
| **N3** | P1 | `DOTATION_EROSION` is created and **never dismissed by any code path** — a paid marshal's "unrewarded, holds 0g/turn" alert persists for the rest of the campaign | `world_state.py:5337-5351` dismisses only `DOTATION_EXPECTATION`; created `:5420`, dismissed nowhere | CONFIRMED |
| **N4** | P1 | The pending marshal petition never expires, never re-validates, and is answered against **live** state — a turn-11 card served on turn 16 would have spent 1 AP on the wrong quarrel | `jealousy.py:1390` (only clear site), `:1408-1448` never compares `context["target"]` to `marshal.jealous_of` | CONFIRMED |
| **N5** | P1 | A pending objection blocks *everything* including free reads (`status`), never names the two words that clear it, and rejects plain English meaning one of them | `executor.py:520-528` returns `choices` in the payload and omits them from the sentence | CONFIRMED |
| **F10** | P2 | The `supply_strain` headline prescribes a depot the executor will refuse — 6 identical false firings | `dispatch.py:1382-1393` models 2 preconditions; `economy_executor.py:1400-1431` enforces 8 | CONFIRMED |
| **F14** | P2 | The recommended peace pays tribute to a court France is beating, in the entire ±20 war-score dead band | `diplomatic_templates.py:3584` — `elif war_score < -20 or relation < -50:`; every 1805 war boots at −80 | CONFIRMED |
| **F11** | P2 | `pursue` has **zero** typo/display-name tolerance; `attack` is fully tolerant | `strategic_parser.py:537-554` exact-key-only → `:647-653` misfiles as region → `strategic_executor.py:580` | CONFIRMED |
| **F3** | P2 | Every 2-AP strategic order reports `cost=1` while charging 2; four code paths disagree | `executor.py:1788-1789` reassigns `action_result` in the loop instead of accumulating | CONFIRMED |
| **F7** | P2 | The fog fallback is whole-phase, not per-nation — fired once in 15 phases, and named nine courts when it did | `main.py:944-953`; `raw_nations` captured at `:940` and discarded | CONFIRMED |
| **N6** | P2 | The AI's own attack rungs sum their army and divide by **one** enemy marshal; P0 picks the *weakest* present | `enemy_ai.py:2578` (P4), `:1532-1535` (P0) | CONFIRMED |
| **N7** | P2 | The futility brake cannot fire on the shape that happens (gated on `fortified`), and P0 bypasses both brakes | `enemy_ai.py:2620-2632`, `:1575-1583` | CONFIRMED |
| **N8** | P2 | "Separate Them" is a permanent, un-cancellable warning subscription — 5 consecutive byte-identical turns | `jealousy.py:1566-1567`; `separation_flagged` never set False anywhere in `backend/` | CONFIRMED |
| **N9** | P2 | Sub-beats have no cross-turn memory: the Tyrol supply sentence ran 6 consecutive dispatches; T15/T16 are the same three sentences permuted | `dispatch.py:849-858` dedupes against a set built fresh per call | CONFIRMED |
| **N10** | P2 | Jealousy fires and escalates on the same tick — 10 of 10 escalations, 6 of 7 French pairs on fire #1 | `_check_escalation` has one caller, `jealousy.py:750`; gate `stored_rel <= -1` vs the MC-3 authored web | CONFIRMED |
| **N11** | P2 | `treasury_delta` is a fresh forward projection rendered as the turn's change; wrong on all 15 turns, wrong *sign* twice | `dispatch.py:1639` recomputes; `meta_executor.py:283` uses the applied cache | CONFIRMED |
| **N12** | P2 | AI admin actions (build/commission) can never be shown at any visibility — Prussia built three structures invisibly | `main.py:1382-1398` derives region only from `ai_action["marshal"]`; admin actions carry none | CONFIRMED |
| **N13** | P2 | 32% of "ENEMY PHASE" actions belong to France's formal allies; T15's entire enemy phase is Bavaria recruiting | `turn_manager.py:452` loops `enemy_nations` = "not the player"; `enemy_phase_dialog.gd:47` | CONFIRMED |
| **N14** | P2 | A fogged coalition member's exhaustion and treasury render as literal `0` beside a sibling that says "Unknown" | `dispatch.py:2883`, `:2886` | CONFIRMED |
| **N15** | P2 | Voice rotation keys on the **region's** battle count — two marshals said the identical line in consecutive battles | `combat_executor.py:5006`/`:5033` pass `world.battle_counts[region]` as `rotation_key` | CONFIRMED |
| **F9** | P2 | Capturing the enemy commander **subtracts 10** from your own war score — a prisoner in Paris reads as "Austria contests the French capital" | `diplomacy.py:2899-2901`, no `strength > 0` / `captured_by` guard (siblings at `:7040`, `:9671` have it) | CONFIRMED |
| **F5** | P2 | Supply capacity renders as a fabricated `0` at PARTIAL — the exact pre-commitment state | `world_state.py:7612` sentinel; `region_panel.gd:179`, `map_renderer_base.gd:2581` print it bare | CONFIRMED |
| **N16** | P2 | All six `europe_*`/`war_touches_us` arms share one dedupe identity — T16 reported the **wrong** congress | `dispatch.py:351` defaults `identity` to the class name | CONFIRMED |
| **N17** | P2 | `counter_punch_earned` is never dismissed; the rail advertised an expired opportunity for eight turns | Created `combat_executor.py:1508-1514`; `world_state.py:10348-10363` clears the flag, not the notification | CONFIRMED |
| **N18** | P2 | A marshal France announced as its own prisoner stays on the enemy order of battle for six turns | `dispatch.py:1966-2028` `_build_intelligence` has no `captured_by` check; its sibling at `:1823-1825` does | CONFIRMED |
| **N19** | P2 | Requisitions of War paid **0 on all 15 turns** — it requires standing on soil the enemy still controls, and capture is instantaneous | `world_state.py:4577-4591` `region.controller != marshal.nation` | CONFIRMED |
| **N20** | P2 | Starvation reads as an economic *win*: 40,000 dead retired both upkeep surcharges, −1,224g/turn | Post-EC-U1-reversal upkeep on fielded strength; nothing joins the two facts | CONFIRMED |
| **N21** | P2 | The drama channel has no dispatch budget — peak 13 marshal-drama lines in one briefing, flat and unranked | `jealousy.py:1781`/`:1789`/`:1845` cap fires only; resolutions/escalations/crowns/warnings uncapped | CONFIRMED |
| **F2** | P3 | Two "Casualties:" lines a few rows apart disagree ~6× on French losses, distinguished only by an apostrophe-s | `combat_executor.py:1366-1369` (CO-5, lead-only) vs `:1410-1418` (CA8-1, whole-army) | CONFIRMED |
| **N22** | P3 | The crown "passes" to nobody — 2 of 3 `glory_crown_lost` name no successor; the real transfer prints crowning *before* loss | `jealousy.py:376-380` vacancy paths share the transfer wording | CONFIRMED |
| **N23** | P3 | `jealousy_restlessness` has exactly one hardcoded template, rendered 7×, beside a sibling with a 7-variant bank | `jealousy.py:1822-1825` | CONFIRMED |
| **N24** | P3 | `"Davout, Soult and Murat **was** expected"` — the plural fix landed on one of two banks | `battle_report.py:462` hardcodes `was`; sibling `:445` uses `{failed_was}` correctly | CONFIRMED |
| **N25** | P3 | `"again, 1 turns after the last"` — no singular arm | `jealousy.py:687` | CONFIRMED |
| **N26** | P3 | `"Starving — supply has failed at Tyrol two turns running"` ×17, on a famine the headline calls "3 turns" on the same screen | `dispatch.py:1289-1293` hardcodes the phrase; `len(turns)` is in scope | CONFIRMED |
| **N27** | P3 | Raw camelCase marshal keys reach terminal, enemy-phase dialog and diorama nameplate — 135 occurrences to 44 spaced | `humanize_entity_name` (`display_names.py:1147`) called only by `_build_intelligence`; `utils.gd` repairs nation tags only | CONFIRMED |
| **N28** | P3 | `"Our scouts report activity within **Ottoman**'s borders"` — a raw tag the client is documented as unable to repair | `main.py:947-951`; `utils.gd:186` names Ottoman as the documented exclusion | CONFIRMED |
| **N29** | P3 | Berthier can never speak about the treasury — 21 classes, 21 notes, rung 2/3 unreachable | `dispatch.py:2186` short-circuits on `headline_class in _HEADLINE_BERTHIER_NOTES` | CONFIRMED |
| **N30** | P3 | The anti-monotony cooldown keys on the internal P-rule label, not the pact the player reads — Hesse re-raised one pact 5× | `ai_diplomacy.py:322` `_cooldown_keys`; `TYPE_LAPSE_COOLDOWN = 6` | CONFIRMED |
| **N31** | P3 | Vassal loyalty prints a `+2` that a clamp at 100 discarded, 4 times | `vassal.py:577` clamps, `:586` gates on the unclamped delta, `:597`/`:623` print it | CONFIRMED |
| **N32** | P3 | Talleyrand's vassal trend derives from autonomy tier alone — *"Holland: loyalty 100, falling"* against its own `+2` events | `diplomatic_advisory.py:529-531` | CONFIRMED |
| **N33** | P3 | `"Other"` is up to 36% of the revenue side and is the only unnamed line; every drain is itemised | `meta_executor.py:284-288` computes it as a residual; `ledger.py:384-389` already breaks it out | CONFIRMED |
| **N34** | P3 | `[HINT] X is undefended — attack to capture it!` never looks past the target province; contradicted the objection two turns later | `movement_executor.py:661-669` | CONFIRMED |
| **N35** | P3 | The mutual-spiral line says *"is now mutual"* every time it re-fires | `jealousy.py:826-851` | CONFIRMED |
| **N36** | P3 | One grievance resolution narrates twice, back to back, structurally | `jealousy.py:1714-1724` appends after `clear_jealousy` already emitted | CONFIRMED |
| **N37** | P3 | A rout's recovery is `severity: "good"` and missing a sentence terminator: *"penalty: -40% The rout's disorder lingers"* | `world_state.py:10210`; `dispatch.py:2124` | CONFIRMED |
| **N38** | P3 | The Fontainebleau quote says "carry" and computes the *increment* — latent, did not bite (all pensions were 0) | `jealousy.py:1255` uses `get_shortfall`; applied cost uses `compute_rente_face` | CONFIRMED |
| **N39** | P3 | AI-vs-AI rivalry/downgrade events have no persistent surface; 12 sponsorships (all aimed at France) reach only the campaign log | `ai_diplomacy.py:2591-2626` not logged, not a dispatch type; `instruments.py:199-209` carries no `message` | CONFIRMED |
| **N40** | P3 | Per-nation `action_count` is stale after the composition collapse — wrong on 8 nation-turns | `main.py:761` sets `actions` and not `action_count` | CONFIRMED (latent) |
| **N41** | P3 | War exhaustion runs to 200 and stops narrating at 80 — the whole second half of the campaign, raw integer, no denominator | `coalition.py:61` vs `:1447` | CONFIRMED |
| **N42** | P3 | The pursue confirmation narrates the raw key back (`"pursuing ArchdukeCharles"`) — merge with open **S5-2** | `BUG_FIXES.md:1387`, `strategic_executor.py:393` | CONFIRMED (already filed) |
| **N43** | P3 | The `literal_fidelity` beat asserts a cause it never checked — *"per your orders"* when three unrelated mechanics produced the absence | `marshal_voice.py:118-130` is a pure per-turn scan | CONFIRMED |
| **N44** | P3 | Silent retarget: `attack Charles at Bohemia` fought at Franconia; the rejected destination is never echoed | `executor.py:449-459` resolves enemy-first and returns his location | CONFIRMED (executor half) |
| **N45** | P3 | Glory — the number the whole drama system runs on — is readable on exactly one screen | `get_glory_score` has one consumer outside `jealousy.py`: `marshal_overview.py:166-169` | CONFIRMED |
| **N46** | P3 | The rente is a treadmill by construction: face sized at grant time, expectation keeps climbing to 300 | `dotation.py:446-458` vs `get_expectation` | CONFIRMED |
| **N47** | P3 | `_STANDING_ESCALATION` has **never fired** — reachable only via a `for…else` that needs the standing class to be the sole candidate | `dispatch.py:810` | CONFIRMED |

### Corrected or killed

| ID | Original claim | What actually holds |
|---|---|---|
| **F1** | "The muster preview sums only the PLAYER side; is enemy fog ever considered?" | **NARROWED.** The enemy *primary* is in the denominator at ground truth — this is not a fog defect at all. The omission is the enemy's **muster** (`objection_v2.py:880` has no `committed_defender`), violating `COMBAT_OVERHAUL_SPEC.md:155`'s own "Symmetric for a reinforced defender (GR5)". Measured once (+4,800); the *attacker* over-promise is 4–8× larger (Franconia: 54,408 predicted, 18,101 fought). **P2**, and a sub-row of the already-owned VP-D2, not a standalone P1. |
| **F2** | "P2 — the battle report shows lead-only casualties, no label" | **NARROWED to P3.** CO-5's reconciler is a *pinned contract* (`test_combat_overhaul_co5_report_consistency.py`); CA8-1 moved the terminal to whole-army four weeks later and created the collision. Confined to `main.gd` — `_format_berthier_report` prints no casualty numbers, so the enemy phase is unaffected. The intervening ally line closes the arithmetic. The three-number T2 claim is unverifiable (pre-reset). |
| **F3** | "P2 — the action economy's advertised price is wrong" | **NARROWED to P3.** No player-visible number is wrong: `main.gd:2866-2870` uses `cost` only as a `>0` gate and prints the honest post-deduction `remaining`. It is an API-contract defect plus a separate copy gap (non-literal strategic orders quote no price at all) plus a latent arithmetic fragility (the loop conflates iteration count with AP total). |
| **F4** | "The muster preview never mentions supply" | **NARROWED to P2 as scoped.** True, but **all four musters read "favorable"**, so the gate at `:4091` never armed and the block was *prepended to an already-resolved battle* — a `supply_note` in `_build_muster_preview` would print after relocation and after the battle. Also Swabia is 6 of 64 attrition events; the general defect is "no order-time supply disclosure on **any** path". And the dominant term is the undisclosed `(num_marshals-1)×1%` stacking penalty, which fires **under capacity**. |
| **F5** | "Supply capacity is UNLOOKUPABLE off own soil" | **NARROWED.** It is lookupable at FULL (scout, 1 AP, or stand there) on both the region panel and map tooltip. The defect is the fabricated `0` at PARTIAL specifically. Note the proposed `-1` sentinel fix needs both `.gd` sites edited — `format_number(-1)` returns `"-1"`. |
| **F8** | "Soult's SUPPORT order binds to the ally's LOCATION at issue time" | **NARROWED to P2.** It binds to his **name**, tracks him dynamically, and fails on `order.target == primary.name` (`combat_executor.py:1071-1073`) — he must lead the battle. Only **one** of the cited refusals is that defect (T6/Tyrol, where Ney was *in the battle* as a reinforcement); T8 is correct-by-doctrine (Ney absent entirely); T13+ is a second mechanism — silent auto-completion on `ally_safe` (`strategic.py:1935`), which does announce itself. What is genuinely P1-shaped is the **copy**: `strategic_executor.py:1326-1329` states an unconditional guarantee the code scopes twice. |
| **F9** | "P1 — `base_side_pressure` is the root cause; leverage is unconvertible" | **NARROWED.** Three of the four mechanisms are the specification implemented verbatim: the flat ±3 battle term (`DIPLOMACY_SPEC.md:1179-1183`), the 2-decisive cap (`:1190`, *"prevents farming"*), and the power-weighted average (`WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md:218,261` — *"This is intentional anti-farming behavior"*). Only the captured-marshal capital inversion is a defect, and Mack was taken on **turn 8**, four turns after the observation. The bilateral route previewed `COUNTER` at 45, not a wall. Tuning question at the Victory & Objectives gate, plus one guard. |
| **F14b** | "No draft at any harshness can demand territory" | **KILLED as stated.** `modify_harsh` round 2 does append one (`diplomatic_executor.py:3888-3894`), and `_ease_suggestion_until_not_rejected` (`:3519-3529`) is the stronger suppressor. |
| **CA9-P2** | "Even harsher is byte-identical" | **UNDETERMINED — do not file.** The digest EOFs at the initial confirm; the two harsher rounds are absent. Code predicts escalation to 450g + territory, so the observed 300 is evidence round 2 *never executed* — a dialogue-routing defect, a separate row. |
| **CA9-P2 (parser)** | "`accept Portugal's proposal` → fuzzy Por→Pru" | **CORRECTED, and worse.** No nation matching happens at all. `main.py:2092` substring-matches the *option label* against the raw text and applies it to whichever dialogue is **active** (`diplomatic_executor.py:3218`). Prussia **was** ACTIVE (`digest:637`), contradicting the note. Any court name in an accept/reject sentence is ignored, including the correct one. Three copies of the rule: `main.py:2092`, `main.py:1901`, `diplomatic_executor.py:3380`. **P1.** |
| **CA8-15** | "still unbuilt" | The prune half **is** live (`main.py:764-780`). The unbuilt half is the §2a remediation — route suppressed nations to the fog line. |
| **CA8-12** | (Aug-4) digest doesn't latch | Remains **REFUTED** against the shipped client. |
| **Play notes T7-T8** | "13 actions across Austria, Bavaria and Spain by T8" | Turn **7**, and the third nation is **Britain**, not Bavaria. |
| **CA9-P3** | "AI never commissions a marshal" | **UNDETERMINED.** By T13 Austria met both visible gates (roster 2 < 3; treasury 4,577 ≥ 3,500+1,000) and never fired. Which downstream gate blocked it — manpower, AP, or admin-rung contention — I could not determine. Worth measuring. |

---

## 3. The through-line

**Every system in this game computes the right answer and then tells the player a different one — and the divergence is always in the direction that makes the player commit.**

This is not a narration problem. It is one architectural pattern repeated across seven subsystems: *the surface that informs a decision and the code that executes it are separate implementations of the same rule, and only one of them is maintained.*

- The **muster preview** models the enemy as one man; the resolver models both musters and says so in a comment (`"Symmetric for a reinforced defender (GR5)"`, `combat_executor.py:4610`). Preview 43,778 v 32,131; reality 26,219 v 36,931. Both errors point at "favorable" (F1).
- The **supply headline** models depot legality with two predicates; `_execute_build` enforces eight. It prescribed the same illegal depot six times (F10).
- The **peace draft** offers tribute on a hostility term while the war-score term sits one line above, unfired (F14).
- The **notification rail** was written once and never re-derived, so it tells you to pay a marshal you already pay 240g/turn, on a screen whose other half correctly shows `"pension": 240` (N3).
- The **AI's attack calculus** divides its whole army by the *weakest* enemy corps present (`enemy_ai.py:1532`), which is the same defender-invisibility bug on the other side of the board — and produced a 4.7:1 exchange against itself across twelve failed assaults.
- The **petition card** is a build-time snapshot answered against live state, so the sentence you read and the grievance you modify are different objects (N4).
- The **`support` confirmation** promises what the mechanic does not scope (F8's copy half).

The reason this is *structural* and not a list of bugs is that the same fix shape closes most of it: **make the advisory surface call the executor's own predicate.** Not a copy of it, not a simplified model of it — the same function. The codebase already knows this: `_build_intelligence` is the one surface that calls `humanize_entity_name` and it is the one surface with clean names; the capture prompt is one builder that both quotes and pays (IGR-E's shown=applied), and it is the one blocking refusal nobody found confusing.

The second-order consequence is what makes the campaign feel the way it does. Because every advisory error is optimistic, the player's model of the board diverges monotonically from the board. You attack because the preview said favorable. You concentrate because the muster affordance recruited you and never priced the stack. You hold position because the depot the briefing recommended will surely land next turn. Forty thousand men die of arithmetic nobody showed you, and then the peace screen — the one place all of it should convert — quotes you a bill.

A useful reframing for the road to EA: the pillar that regressed hardest is not narration (which improved). It is **trust**. Six of the campaign's seven worst moments were the game asserting something false at the exact moment the player was committing resources. That is a fixable class, and it is cheaper to fix than anything on the feature roadmap.

---

## 4. Pillar scores

| Pillar | Aug 4 | CA9 | Δ | What moves it |
|---|---|---|---|---|
| Combat | 6.5 | **5.5** | −1.0 | Symmetric `committed_defender` in the muster band (`objection_v2.py:867` + `combat_executor.py:828`) — the same ratio gates the bad-odds modal, so the game starts *asking* before the disaster |
| Marshal drama | 7.5 | **6.5** | −1.0 | Re-target SUPPORT to the ally's current province each tick; until then stop the confirmation promising it already does |
| Economy | 6.5 | **6.0** | −0.5 | Let a low-stability province take a depot at a **premium** (extend `economy_executor.py:703`'s existing tier down) instead of refusing — the only change that connects 16,000 idle gold to 52,000 starved men |
| Diplomacy | 7.0 | **6.5** | −0.5 | Drop `or relation < -50` from `diplomatic_templates.py:3584` and lower the territory gate from `>30` to the existing `20` tier — the cheapest edit in the audit, and it converts the military pillar into currency |
| Narration | 6.0 | **6.5** | +0.5 | Hoist `_STANDING_ESCALATION` out of the `for…else` at `dispatch.py:810` so its (never-seen) variant bank actually fires |
| Command/parsing | 7.0 | **6.0** | −1.0 | One helper that prints the live dialogue's own option list, applied at `executor.py:524` and `main.py:2111` — the idiom already ships in the capture prompt and works |
| AI aliveness | 7.0 | **7.0** | 0.0 | Raise the four `europe_*` weights (`dispatch.py:117-120`, currently the four lowest slots) above `estate_eroding` 55 / `levy_open` 54 — the content is already written and has never led |

**Directional: ≈6.3** (Aug 4: ≈6.9; Jul 25: ≈7.4). Nothing regressed by being changed — as in August, every scorer independently attributed the drop to campaign *length*. These are accumulation failures, and the trend is that each longer campaign finds a deeper layer of them.

---

## 5. What is genuinely excellent

Do not touch any of this.

1. **The muster preview's WILL-NOT rows tell you the exact sentence that fixes them.** `WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Murat' and he will march` / `WILL NOT — Bernadotte: will not lift a finger for this marshal`. An affordance and a character beat in one line.

2. **The order of battle prints the refusal as a table cell.** `defender order of battle: Massena 32,962(routed); Soult 34,876(refused)` — a province lost to a personality trait, with the work shown, no prose required.

3. **Berthier's after-action roll-call joins cause to outcome.** *"Not one corps reached Ney. Davout, Soult and Murat was expected; Ney fought the battle single-handed."* (Fix the `was`; keep the sentence.)

4. **Talleyrand's war room is the best information surface in the game.** *"Austria's design: Revanche — Their court will not rest while Russia holds Bohemia. Their price: prepared to go as far as an ultimatum — Russia stands in the way (weight 72)."* Nothing scripted a coalition member turning its revenge on its own ally.

5. **…and it closes on executable counsel.** *"Britain's war has a purpose we can price — 'The Low Countries'. We hold what their court wants; offer it at the table and their reason to fight goes with it."*

6. **The capture prompt is the model blocking refusal** — both options, one priced, each consequence stated: *"Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')"*. It is the only blocking state in the campaign nobody found confusing, and the event paid exactly the 800 it quoted.

7. **The signed income line reconciles to the digit, every turn, with every drain named.** `Income: 3428g | Occupation: -52g | Charges of Empire: -1142g | Rentes: -2010g | Admiralty: -90g | Blockade: -250g | Upkeep: 944g | Other: +1158g | Net: +98g`.

8. **The levy headline states stock, flow, price, place and gate in two sentences of period voice.** *"the establishment stands 38,287 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them."* → *"The depots are full and the ordinance allows it, Sire. Conscripts do not improve with keeping."*

9. **Refusals name their own threshold.** *"Cannot build in Tyrol — region stability too low (35/100). Need 51+."* / *"Murat cannot reach Vienna from Albania! Range: 2, Distance: 3"*.

10. **The CA8-8 recurrence register is real writing, and level-aware.** *"Bernadotte's resentment of Ney has cooled for now. What was settled between them at the staff table has not been."* — a different sentence for a different fact, correctly keyed on escalation level.

11. **Character expressed as mechanic.** *"Soult has thrown himself into his post with obsessive diligence"* → four `intel_updated … "source": "obsessive_patrols"` reveals, four lines later.

12. **The Butcher's Bill does GR5 in public and reads like period prose.** *"[Materiel] Guns, horses and stores lost with the fallen: France -97g, Austria -805g."*

13. **The AI plays the same economy, unprompted, with both numbers stated.** `Castanos is granted a rente upon the treasury` — `{"face": 80, "cost": 120}` — in the same enemy phase he won two battles for Spain.

14. **The Stage-D congress beat, twice, unprompted.** *"THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on."*

15. **The ally/conquest distinction, stated at the moment it bites.** *"Swabia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take."*

16. **Battle naming: 23 battles, 23 unique names, correctly ordinal per region, with a "Great" tier.** Zero collisions.

17. **The minor-court voices earn their place.** Reis Efendi: *"The Porte has outlasted a hundred ascendancies by trading with each at its noon; France's noon has come, and the bazaar is open."*

18. **EB-1 cured the disease it was built for.** Treasury converges 14,903 → 16,329 with Net crossing zero at T10, under a player doing nothing — the hard case.

---

## 6. Recommended order of work

Ordering principle: **restore trust before adding reach.** Every item in tier 1 is a case of the game asserting something false while the player commits; none needs a design gate; several are one line. Feature work on top of a lying advisory layer compounds the problem.

### Tier 1 — unblocked, days, highest trust-per-line

1. **F6 — stamp `diplomatic_dialogue` at the three PT-F1 sites** (`combat_executor.py:4489/5410/6323`, copying `:3176`). One line each. This is a total input lockout that ate `end turn`; it has no defence. Also widen `_unresolved_choice_failure`'s re-attach from the settlement family to all `HARD_STOP_TYPES` as a backstop for the next unwired dialogue type. **Do this first.**
2. **The typed dialogue router (`main.py:2092`)** — read the court the player named, or refuse and say which court is being answered. An unconfirmed permanent treaty with a great power is the most serious correctness defect in the audit. Note the client-side fix for this exact class already shipped (`diplomatic_executor.py:3222-3224`); the typed path — this game's premise — was never given it.
3. **N5 — one helper that prints the live dialogue's own option list**, applied at `executor.py:524` and `main.py:2111-2118`. `choices` is already in the return dict and thrown away. While there: swap the hard-stop substring matcher for the option-matcher twenty lines below it, or `garrison Paris` will keep declaring wars of conquest. Cheap, and it converts six "the game stopped listening" moments into questions.
4. **F1 — symmetric `committed_defender` in the muster band.** One new defaulted parameter; all four `inferred_attack_favorable` call sites stay byte-identical. Fog-safe (the formula already reads ground truth; keep `_fog_banded_strength` on the printed figure). Add a hedge row for unseen adjacent corps, and change `43,778` to `43,778 if all march`.
5. **F10 — extract `can_build(region, type, nation) -> (ok, reason)` and have both `_execute_build` and `_supply_strain_candidate` call it.** The written contract already requires this (`ECONOMY_REVISIT_SPEC.md:175`, *"names whichever remedy is LEGAL"*); it is a recurrence of closed CA8-2 on a different gate arm. Add the `repair` arm for damaged depots.
6. **F14 — drop `or relation < -50` from the sweetener branch** (`diplomatic_templates.py:3584`) and make the demand arm continuous through zero. One `if/elif`; one pin to re-bless as "hostile *and not winning*". *(Caveat: the current behaviour is gate-blessed at `CREATIVE_AUDIT_2026_08_04.md:934-936`, so this is a re-open, not a bug fix — but it is a one-line re-open of a decision the campaign falsified.)*
7. **N3 + N17 — dismiss `DOTATION_EROSION` and `COUNTER_PUNCH_EARNED`.** Two `dismiss_by_type` calls at seams that already exist (`world_state.py:5337`, `:10348`). The tray's own docstring says *"a list of things still true"*; make it true.
8. **F12 + N2 — branch `marshal_captured` on `e["nation"]`**, which the event already carries, and give the Berthier note the same direction. Apply the existing D6 ruling (*"a third party's kill is never our triumph"*). Fixture note: the CA8 pin builds its event with no `nation` key and will red on first run.
9. **N1 — dedupe the double `battles_won` increment** (`combat_executor.py:4950-4967` against `atk_participants`). This one is *not* cosmetic — it doubles the price of the entire reward economy and inverts the fiction. Re-measure the ES-7 band after.
10. **The narration one-liners**: N24 (`{failed_was}`), N25, N26, N37, N31, N28, N32. Each is one line and each is quotable, which means each is disproportionately damaging.

### Tier 2 — unblocked, one slice each

11. **N9 + N47 — cross-turn sub-beat memory, and hoist `_STANDING_ESCALATION` out of its `for…else`.** The best-written lines in `dispatch.py` have never been rendered. This kills both dominant repeats at once.
12. **F7 / CA8-15 §2a — per-nation fog fallback**, under a *new* key rendered after the nation blocks (reusing `fog_hidden_summary` would delete visible actions — `enemy_phase_dialog.gd:68` branches *instead of* the loop). Fix N40's stale `action_count` first, since the honest line will carry it.
13. **N6 + N7 — give the AI a committed-defender estimate and put the futility brake on P0.** Same root as F1; twelve suicide assaults for a 4.7:1 exchange against itself is why Europe is busy and not threatening.
14. **F13 — gate the muster relocation with the PT-F1 predicate**, and emit one event per cleared strategic order naming what it voided. *(Caution: the artillery arm it would copy omits the marshal from `arrived_names`, so extending it to infantry touches committed-strength accounting — measure M1–M7.)* Also read `jealousy_attack_results` in `turn_manager.py:187`; it is assigned and never consumed.
15. **N27 — route the three remaining surfaces through `humanize_entity_name`**, and pair it with F11's `_plausible_name_typo`-gated marshal arm in `pursue`. Note `_plausible_name_typo("Archduke Charles", "ArchdukeCharles")` is already **True** (edit distance 1) while the bare surname is correctly **False** — so the CA8-28 discipline is preserved, and only the `len(token.split()) != 1` phrase gate at `strategic_executor.py:127/152` needs relaxing.
16. **F8's copy half + F5's `-1` sentinel** (both `.gd` sites) + **N11's `treasury_delta`** (read the applied cache, like both banners do).

### Tier 3 — needs a design gate

- **F9's captured-marshal capital inversion** is a one-guard defect and can ship in tier 1; but the leverage question behind it — the flat ±3 battle term, the shared 2-decisive cap, the power-weighted side-pressure average — is all specified, blessed, and documented as anti-farming. That belongs at the **Victory & Objectives** gate with the scope boundary corrected, not in a bug sweep.
- **N19 Requisitions** — the mechanic pays only a stalled invasion. Re-scoping it to reward an army *living off* conquered ground is a design call.
- **N20** — joining "the army starved" to "upkeep fell" is an economy-design decision, not a copy fix.
- **F4's general form** — order-time supply disclosure on *every* path (not just the muster preview, which on this evidence is a post-hoc header) touches the stacking penalty, which is undisclosed even in `SYSTEMS_REFERENCE.md`.
- **N10** — separating jealousy's fire from its escalation is a mechanics change (`_check_escalation` has one caller), and it moves M7.

---

## 7. Open questions for the developer

1. **Should the muster preview be a *decision* surface at all?** Today all four musters read "favorable", so the gate at `combat_executor.py:4091` never armed and the block was prepended to an already-resolved battle. Fixing the arithmetic (F1) makes more previews read unfavorable, which arms the confirm modal — is that the intended texture, or should the preview move to a pre-commit seam (the `support`/`move` response) where it can be acted on?

2. **Is 6% attrition on a six-corps stack a trap or a lesson?** The stacking term (`(n-1)×1%`, fires under capacity) is documented as intentional (`SYSTEMS_AUDIT_V2_FIX_PLAN.md:334`, "intentional design") and is disclosed nowhere — not in the ledger, not in the region panel, not in `SYSTEMS_REFERENCE.md`, which describes the formula without it. Disclose it, or reduce it? Both are defensible; the current state is neither.

3. **Should conquest pay?** France took four provinces and income moved +4.2%. With `Requisitions` structurally unreachable for a winning army (N19) and 16,000g idle, the war has no economic payoff and the treasury has no sink. Is the intent "war is a money pit and that's the point", or should taking Vienna feel like taking Vienna?

4. **What is the war-score → terms curve meant to look like?** At +19, seven wins, zero losses, the game recommends paying tribute. At +30 it would demand territory. Is the ±20 dead band deliberate, and if so what is the player supposed to do with a war they are winning but not winning *enough*?

5. **What should a national design change cost in credibility?** Austria shifted design three turns running (Revanche → survival → Revanche), each a MEDIUM dispatch beat. The content is excellent; the churn devalues the beat. Hysteresis, a cooldown, or accept it?

6. **Does the player need a verb for a foreign war they can see coming?** Talleyrand reported Austria at weight 72 against Russia — one rung and thirteen points from the first AI-initiated war in the game's history — and the assessment surface offered no action, while `sponsor_design` exists at 1 DP and was never named there.

7. **Should the "ENEMY PHASE" be renamed, or split?** 32% of its actions are France's own allies; T15's entire phase is Bavaria recruiting. It is Europe's phase, not the enemy's.

8. **Is the marshal petition meant to expire?** It currently blocks the whole channel indefinitely (turn-11 card still pending at turn 16, with at least four petition-worthy events unable to queue behind it) and is answered against live state. A TTL, a re-validation at serve time, or a queue?

9. **How much drama per turn?** AI-6 landed a 2-per-dispatch cap on intent narration for exactly this failure mode; jealousy — the noisier producer — has caps on fires only, and peaked at 13 lines in one briefing, unranked. Should the same budget apply?

10. **Was any AI commission blocked, or just not attempted?** By T13 Austria met both visible gates in `find_ai_commission` and never fired. The Marshalate's stated both-sides recovery path produced zero enemy commissions in a campaign that annihilated one enemy marshal and routed two more. I could not determine which downstream gate held — worth measuring before EA, since it is the AI's only path back from attrition.