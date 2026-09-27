# Reforms of State — SR-D1 "Reforms, not research"

> **Status: RULED September 27, 2026 by the user, at Chunk 5's gate** (`SCORE_MANDATE_PLAN.md` §4 SR-D1). **Nothing is built.**
>
> This file holds two things:
> - **The gate record (§0)**, which is authoritative.
> - **The build contract** for Chunk 5's head (§1–§13).
>
> What may change at the build:
> - Numbers marked **DRAFT** are in-band tunable; the build measures them against §11.
> - A new effect type, a change to the lapse rule, or a new currency is structural and escalates to the user.
>
> Reading map:
> - §0 the rulings, and the readings taken where they meet;
> - §1–§2 what a law is and its lifecycle;
> - §3 the currencies;
> - §4 the effect types;
> - §5 the Staff;
> - §6 the draft catalogue;
> - §7 the AI;
> - §8 what the player sees;
> - §9 diplomatic points;
> - §10 the save format;
> - §11 acceptance;
> - §12 the build slices;
> - §13 what v1 leaves out.

---

## §0 Gate record — RULED September 27, 2026

| # | Question | Ruling | Note |
|---|---|---|---|
| Q1 | Reforms or nothing — and what a reform is | **Laws with upkeep.** Five to eight named 1805 acts per great power. Each is bought once, then paid for in gold every turn, and lapses when the treasury cannot pay. None is in force at boot. | **The recommended default ("permanent laws") was NOT taken.** The upkeep is the point: the long peace gets something to pay for (`SCORE_MANDATE_PLAN.md` §1's economy row: "the long peace with nothing to buy"). A peaceful France banked 82,524 gold by turn 30 (`docs/audits/PLAYTEST_RESCORE_2026_09_12.md`). The IQ-1 control arm ended on 88,556 gold with zero treasury falls in forty turns (`IMPROVEMENT_QUEUE_SPEC.md` §0.6b). |
| Q2 | The currency | **Mixed.** Enacting costs gold for a material act, or authority for a political one, plus one admin action. | As recommended. |
| Q3 | How reachable the Staff is | **Mid-campaign.** A large one-off price that most campaigns can afford around turns 10–15. The AI pays the same price. | As recommended. |
| Q4 | Both boards | **Yes (GR5).** Every AI great power enacts from its own authored deck, in order, at the same prices — the agendas idiom. | Stated as the default; not objected. |
| Q5 | Is the Staff the action-point lever? | **Yes.** SR-D3's ruling of September 26, 2026 (evening) already answered it: the Staff is the only road to a new action point, on both boards. | — |
| Q6 | Seasons | **Not here.** The Russian winter stays with SR-D2 + HC-6 at Chunk 7's gate. | Stated as the default; not objected. |
| SR-D3 Q3 | Diplomatic points | **Bank one turn.** Unspent points carry over one turn; the pool is capped at 7. | As recommended (AAR-D5). |
| SR-D3 Q5 | The admin pool | **Unchanged.** An unused admin action still pays 25 gold. | Stated as the default. Converting admin actions to diplomatic points would mint points without their price. |

### §0.1 Readings taken where the answers meet — FOR USER CONFIRMATION

Each reading is one catalogue field or one constant to flip.

- **R1 — The Staff pays upkeep like every law.**
  - This combines Q1 (upkeep) with Q3's one-off enactment price.
  - So a court that cannot pay loses its fifth action.
  - The other reading — the Staff exempt from upkeep — is one catalogue field.
- **R2 — Upkeep is always gold, political laws included.**
  - Q1's own words: "each costs gold every turn".
  - Authority is spent once, at enactment.
- **R3 — A lapse is a repeal.** Re-enacting a lapsed law costs the full price again: no discount, no cooldown.
- **R4 — The player may repeal a law at any time.** It costs one admin action (the `revoke_pension` idiom) and refunds nothing.
- **R5 — Laws lapse before rentes.**
  - When the treasury cannot pay, the law with the largest upkeep lapses first, and so on until the chest is whole.
  - The bounced upkeep is refunded: ESP-4's shape, one obligation over.
  - The principle: the state sheds its machinery before it breaks faith with its marshals.
  - The forecast names the doomed law a turn early. Repealing a different law first is how the player chooses which one goes.
- **R6 — Five decks in v1:** France, Austria, Prussia, Russia, Britain. No minor court has laws.
- **R7 — v1 mints ONE new action point, the fifth.**
  - A sixth (a second tier of the Staff) is not built.
  - It re-opens only on a named condition (§13).

---

## §1 What a law is

**Where it lives.** A law is a named 1805-period act, authored per court under a new scenario key, `reforms`, in `europe_1805.json` and validated by `modding/validator.py`. Each row carries:

| Field | Meaning |
|---|---|
| `id` | the law's key |
| `name` | its display name |
| `date` | the historical act, e.g. "decree of 26 March 1807" |
| `currency` | `gold` or `authority` |
| `price` | the enactment price |
| `upkeep` | gold per turn |
| `effects` | one or two clauses from §4's closed set |
| `says` | the one-sentence description the ledger prints verbatim |

**The AI's order.** A row's position in its court's list is the order in which that AI court enacts.

**Authored content, not formulas** (`SCORE_MANDATE_PLAN.md` §4, the rule of the house):
- Every price, upkeep and parameter is a number in the scenario, reviewable by reading the file.
- The code owns only the closed set of effect types (§4) and the lifecycle (§2).

**Nothing is in force at boot, on any board.**
- The legacy 19-region world authors no `reforms` key, so it has no laws (N1).
- Every act is one its court had not carried out by September 1805, so "none at boot" is history, not a balance convenience.
- The acts dated after 1807 are the counterfactual a sandbox exists for.

---

## §2 The lifecycle

1. **Enact.**
   - The verb `enact <law>` goes through the shared executor as an `ADMIN_ACTIONS` member, costing one admin action plus the price.
   - One predicate, `reforms.law_refusal(world, nation, law_id)`, gates the verb, its chip, the AI rung and the preview.
   - It refuses free, naming the reason: not this court's law, already in force, the price, or no admin action left.
   - The law is in force from that moment. Each effect applies from the next time its seam is read — for the Staff, the next action refill.
2. **Pay.**
   - Every income phase charges the court's upkeep for its laws in force as ONE signed Net component, **"Laws"**.
   - It is threaded through the whole EC-U2 recipe:
     - `process_income_phase` and its applied-results record;
     - `ledger.NET_GOLD_COMPONENTS`;
     - `meta_executor`;
     - the dispatch;
     - both end-turn banners;
     - `strategic_ledger.gd`.
3. **Lapse.**
   - After the income phase, while the chest is negative and laws remain in force:
     - the law with the largest upkeep lapses (tie: the most recently enacted);
     - its charge is refunded into the chest and folded into the applied record, so Net and the measured change in the chest agree (the ESP-4 refund);
     - the lapse is logged.
   - This loop runs immediately BEFORE ESP-4's rente default, in the same post-income window, and both run before `_update_bankruptcy`.
   - GR5: every court, one rule.
4. **Repeal.** `repeal <law>` costs one admin action and refunds nothing. Its effects end at the same reads.
5. **Re-enact.** A lapsed or repealed law is available again at its full price.

**Effects are derived, never written.**
- Every effect is read at its seam from the set of laws in force. A lapse or a repeal therefore removes it by construction, and no second store can drift.
- The Staff's +1 is read at `calculate_max_actions`. It is never written into `bonus_actions`, whose one writer stays the administrative role.
- This refines SR-D3's wording ("through the `calculate_max_actions` → `bonus_actions` seam"): the seam is honoured; the store is not written.

---

## §3 The currencies

**Gold** — the chest.

**Authority.**
- Where it lives:
  - the player: `world.authority_tracker` (`modify_authority`; boot 100);
  - an AI court: `world.nation_authority[nation]` (boot 60 for every Europe court, `nation_config`).
- It has teeth, and every authority price is read against them:

  | Authority | What changes |
  |---|---|
  | 60 and above | +1 diplomatic point a turn (`calculate_dp`) |
  | 70 | the jealousy calm (`JEALOUSY_SPEC.md` §0.2-11b) and the "Whispers of Weakness" event |
  | below 30 | −1 diplomatic point a turn, and "Emperor in Name Only" |

- The player's authority also feeds the VS-R grip.
- It comes back with victories (+2 or +5 a battle at the combat seams). A political reform is therefore paid for in the Emperor's standing and bought back on the field.
- **An AI court boots exactly at the 60 line.** Its first political act costs it a diplomatic point a turn at once. That price is real, and the AI rung weighs it (§7).

**Admin action** — one to enact, one to repeal.

---

## §4 The effect types — a closed set, each on ONE existing single source

Every seam below was verified at HEAD `b858b806`.

| Type | Parameter | The seam |
|---|---|---|
| `actions` | +1 (the Staff only) | the player: `WorldState.calculate_max_actions`; the AI: the per-turn restore of `nation_actions` from `base_nation_actions` in `WorldState` |
| `manpower_regen` | +N% on a named pool | `WorldState.get_manpower_regen_rates` |
| `recruit_price` | ×m on a named arm, or on all arms | `EconomyExecutor._calculate_recruit_cost` — so `recruit_quote` and every chip quote it too |
| `recruit_morale` | ±N on a named arm's green-conscript morale | the readers of `EconomyExecutor.RECRUIT_MORALE_BASE` (the executor and the quote's rung) |
| `drill_morale` | +N | the readers of `WorldState.DRILL_MORALE_GAIN` and `_TRAINED` |
| `supply_capacity` | ×m on the fed multiplier | `WorldState.get_effective_supply_cap` / `_supply_multiplier` |
| `satellite_loyalty` | +N a turn for every satellite of the enacting lord | `vassal.process_vassal_loyalty` and `vassal.forecast_vassal_loyalty` (applied and forecast from one term) |
| `cs_closure` | who counts toward the closure | `naval.closure_against` |
| `blockade_denial` | ×m on a blockaded court's trade loss | the blockade arm of `diplomacy.process_trade_income` |

Rules:
- **Strike, never invent.** If the build cannot site a type on ONE existing single source, the type is struck with its laws and recorded — never invented. A new type is structural and escalates; a number inside a type is in-band.
- **Shown = applied, by construction.** The source that applies an effect is the source every surface quotes: the LAWS tab, the recruit quote, the supply headline, the vassal forecast.
- **At most two clauses per law**, so an act can carry its own trade-off. Russia's Extraordinary Levy is cheap men at low morale.

---

## §5 The Staff — the only road to a new action point

**One law per court, one price for all.**
- Every great power's deck carries exactly ONE law with `actions: +1`. Each is its own institution:
  - France's Grand Quartier Général;
  - Austria's Corps d'Armée;
  - Prussia's General Staff;
  - Russia's Divisional System;
  - Britain's Horse Guards reforms.
- All five share ONE enactment price and ONE upkeep (GR5 and Q3): the only road to a new action point costs every court the same.

**How it counts.**
- The player: `calculate_max_actions` = 4 + `bonus_actions` + the Staff (0 or 1) — at most 6, with an administrative marshal.
- The AI: the per-turn restore adds the same derived term.

**Asymmetric value, by design.**
- AI rosters are 1–3 corps on 2–4 actions; France fields 8 corps on 4 (`SCORE_MANDATE_PLAN.md` §4 SR-D3). The fifth point is worth most to France.
- The action-point gap is France's problem; the Staff is France's answer, open to every court at the same price.

**A lapse costs the fifth action at the next refill**, and the morning dispatch says so.

**Q0 is re-measured after the Staff lands** (`SCORE_MANDATE_PLAN.md` §4 SR-D3): the three roads' titled count, by `tools/sr1e_titled_probe.py`. 45 is not moved.

---

## §6 The draft catalogue — DRAFT numbers, authored at RF-2, measured against §11

**Three pricing rules:**
- The Staff costs the same for every court: **9,000 gold and 300 a turn**.
- Every political act costs **15 authority**.
- Upkeep runs 100–300 gold a turn.

**France — 6 laws.** The full slate's upkeep is 1,050 gold a turn, sized for §11 T2.

| Law | The act | Currency | Price | Upkeep | Effect |
|---|---|---|---|---|---|
| The Grand Quartier Général | Berthier's Imperial Headquarters, expanded 1805–07 | gold | 9,000 | 300 | `actions` +1 |
| The Train des Équipages | decree of 26 March 1807 | gold | 3,500 | 200 | `supply_capacity` ×1.25 |
| The Artillery Reserve | the Guard's reserve batteries, 1806–09 | gold | 3,000 | 150 | `recruit_price` artillery ×0.85 |
| The Anticipated Class | the senatus-consultes calling the class early, 1806–07 | authority | 15 | 150 | `manpower_regen` infantry +25% |
| The Berlin Decree | 21 November 1806 | authority | 15 | 150 | `cs_closure`: every client of the decreeing lord counts, whatever its autonomy (today only puppets and satellites do) |
| The Code Abroad | the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808) | authority | 15 | 100 | `satellite_loyalty` +1 a turn |

**Austria — 5 laws.**

| Law | The act | Currency | Price | Upkeep | Effect |
|---|---|---|---|---|---|
| The Corps d'Armée | Archduke Charles, 1809 | gold | 9,000 | 300 | `actions` +1 |
| The Landwehr | patent of 9 June 1808 | authority | 15 | 150 | `manpower_regen` infantry +25% |
| The Jäger battalions | raised 1808 | gold | 2,500 | 100 | `recruit_morale` infantry +10 |
| The new infantry regulations | 1806–07 | gold | 2,000 | 100 | `drill_morale` +5 |
| The Generalissimus | Charles over the Hofkriegsrat, 1806 | authority | 15 | 100 | `recruit_price` all arms ×0.9 |

**Prussia — 5 laws.**

| Law | The act | Currency | Price | Upkeep | Effect |
|---|---|---|---|---|---|
| The General Staff | Scharnhorst, 1808 | gold | 9,000 | 300 | `actions` +1 |
| The Krümper System | 1808 | gold | 2,500 | 100 | `manpower_regen` infantry +25% |
| The Articles of War | August 1808 | authority | 15 | 100 | `recruit_morale` infantry +10 |
| The Military Reorganisation Commission | July 1807 | gold | 2,000 | 100 | `drill_morale` +5 |
| The Emancipation Edict | 9 October 1807 | authority | 15 | 100 | `recruit_price` infantry ×0.9 |

**Russia — 5 laws.**

| Law | The act | Currency | Price | Upkeep | Effect |
|---|---|---|---|---|---|
| The Divisional System | 1806 | gold | 9,000 | 300 | `actions` +1 |
| Arakcheev's Artillery | the system of 1805, to 1808 | gold | 3,000 | 150 | `recruit_price` artillery ×0.85 |
| The Opolchenie | manifesto of 30 November 1806 | authority | 15 | 150 | `manpower_regen` infantry +25% |
| The Extraordinary Levy | the recruit levies | gold | 2,000 | 100 | `recruit_price` infantry ×0.8, **and** `recruit_morale` infantry −10 |
| The War Ministry under Arakcheev | January 1808 | gold | 2,000 | 100 | `drill_morale` +5 |

**Britain — 5 laws.**

| Law | The act | Currency | Price | Upkeep | Effect |
|---|---|---|---|---|---|
| The Horse Guards Reforms | the Duke of York, 1795–1809 | gold | 9,000 | 300 | `actions` +1 |
| The Orders in Council | January and November 1807 | authority | 15 | 150 | `blockade_denial` ×1.25 |
| The Militia Transfer | Castlereagh, 1807–08 | authority | 15 | 150 | `manpower_regen` infantry +25% |
| The Commissariat | reorganised 1809–10 | gold | 3,000 | 150 | `supply_capacity` ×1.25 |
| Congreve's Rockets | Boulogne, October 1806 | gold | 2,500 | 100 | `recruit_price` artillery ×0.85 |

---

## §7 The AI

**Which law.** The deck order is authored: the list order in `reforms[court]`. The rung takes the first law that `law_refusal` passes and whose purse test passes:
- the treasury ≥ the price + 1,000 + 5 × the court's upkeep in force *including* the new law;
- the court's forecast Net (the ledger's own projection) stays ≥ 0 after the new upkeep;
- an authority price never takes the court below 30.

**How often, and where.**
- At most one enactment per court every 3 turns.
- The rung sits in the admin chain beside P1.75 (commissions). The exact slot is the build's, recorded in `ENEMY_AI_REFERENCE.md`.

**The AI never repeals.** The lapse rule is its discipline — the same rule the player meets when a forecast goes unanswered.

**Balance.**
- Nothing is in force at boot, so turn 0 is byte-identical. The first AI enactment moves the ambient board.
- With the lever `reforms.THE_STATE_HAS_LAWS` down, the prior `BASELINE_SERIES` reproduces byte for byte.
- The series is re-recorded ONCE, with a flip-arm attribution in the `tools/_vpr1_series_arms.py` pattern, counting enactments and lapses per court.

---

## §8 What the player sees

**The LAWS tab** — the Strategic Ledger's eighth tab, on key 8.
- One row per law in the player's deck:
  - name, date, and the one-sentence `says`;
  - the effect in numbers;
  - price and upkeep;
  - status: in force since turn N, available, or refused with its reason.
- Honest-availability chips (Enact, Repeal) send the typed command through the shared pipeline (the CN-3 idiom).
- The footer shows the slate's upkeep a turn, and the forecast.

**The forecast.**
- When the ledger's own projection says next turn's chest cannot pay the slate, three surfaces name the law that would lapse first and the gold that would save it:
  - the LAWS tab;
  - the end-turn banner;
  - the morning dispatch.
- Shown = applied: the forecast reads the same lapse rule as §2.

**Authority, priced aloud.** The enactment confirm and the chip name every threshold the spend crosses. Example: "Authority 100 → 85 — the marshals' calm holds above 70."

**The Net line.** "Laws" appears on every surface that prints Net (§2, step 2).

**The events.**
- `law_enacted`, `law_repealed` and `law_lapsed` join `CAMPAIGN_LOG_TYPES`; the census pins flip consciously.
- A dispatch beat reports when another court enacts ("Austria raises the Landwehr") — diplomacy has no fog.
- The Diplomatic Ledger's Nations tab lists each court's laws in force.

**The words.**
- Verbs: `enact the Staff`, `enact the Berlin Decree`, `repeal the Code Abroad`.
- Golden-corpus rows pass under both arms of CX-1's lever.
- Regenerate `python -m tools.gen_routed_order_words` after the parser gains the verbs.
- The help block names the verbs.
- The School of War gains a card for the LAWS tab: 19 → 20.

---

## §9 Diplomatic points bank one turn (SR-D3 Q3) — and the admin pool (Q5)

**The rule.** In `diplomacy._process_dp_regen`, for every court (GR5):
- `carry = min(unspent, regen)`;
- `pool = min(DP_BANK_CAP = 7, regen + carry)`.

**Zero new serialized fields.** The unspent pool before the refill IS the carry.

**How long a point lasts.**
- A point carries at most one turn while the regen holds steady, because spending draws the oldest points first.
- If the regen rises between turns, one point can carry twice. This is recorded, not engineered away.

**Shown = applied.**
- The dispatch's regen breakdown gains "+N carried".
- `displayed_dp_ceiling` and the top bar show the pool as regen + carried — never a pool over its own printed maximum (the NP audit's "DP: 6/5" lesson).

**⚠ Measure before landing.**
- AI courts spend diplomatic points at four sites only: two in `ai_diplomacy`, the treaty break, and vassal courting. Most AI pools would therefore sit at 7.
- The build counts what a full AI pool unlocks on the ambient board before it lands.
- Lever: `DIPLOMATIC_POINTS_CARRY`. Any series move is attributed by a flip arm.

**The admin pool is unchanged:** 25 gold per unused admin action (`WorldState._calculate_admin_bonus`).

---

## §10 The save format

**ONE new serialized world field, `reforms`.** Per court it holds:
- the catalogue, copied from the scenario at `from_scenario` (the agendas-deck idiom);
- the laws in force, with their enactment turns.

**Old saves.** A pre-reform save backfills the catalogue from the scenario at load, with nothing in force — the EB-2 idiom, drift-pinned.

**Docs and tests.** Update `SAVE_FORMAT_REFERENCE.md` and the serialization enforcement test.

**Nothing else is serialized.**
- Effects are derived (§2).
- The forecast is computed.
- The diplomatic-point carry is the pool itself.

**A created client** (NA-6c `formations.create_client_nation`) gets no deck.

---

## §11 Acceptance — falsifiable targets

| # | Target | Pass condition |
|---|---|---|
| T0 | Boot | No law is in force on any board. `BASELINE_SERIES` turn 0 and M1–M7 are byte-identical; with the lever down, the whole 40-turn series is byte-identical. |
| T1 | The Staff's reach (Q3) | On the commanded arm, a France that saves for the Staff can enact it between turns 10 and 15, on three seeds. |
| T2 | The sink (Q1) | A France holding its full slate at peace spends 40–60% of its golden-peace surplus on upkeep, with the IQ-1 control arm as the baseline. |
| T3 | AI competence (GR5) | On the ambient board, at least two AI great powers enact at least one law by turn 25, and no AI law lapses before turn 40 in a court that is not losing provinces. |
| T4 | The lapse | On a staged insolvent France: the largest law lapses first; the refund makes the chest whole; the forecast named that law a turn earlier; re-enacting charges the full price. |
| T5 | The Staff on both boards | The fifth action appears at the first refill after enactment and is gone at the first refill after a lapse — for France and for an AI court. |
| T6 | The bank | A court that spends nothing carries one turn's points, up to 7 and no further. The pool, the dispatch and the top bar agree. |
| Q0 | The road to 45 | Re-measured after the Staff lands. |

**Gates for every slice:**
- every pin mutation-swept to 0 INERT;
- any `.gd` change passes the parse harness (EXIT=0) and a boot with 0 SCRIPT ERROR.

---

## §12 The build slices — Chunk 5's head, "SR-5r The Laws"

| Slice | Scope | Size (sessions) |
|---|---|---|
| **RF-0** | **The substrate.** `backend/game_logic/reforms.py` (catalogue load, `law_refusal`, `law_upkeep_bill`, the laws in force); the scenario `reforms` key and its validator block; save and backfill. No law can be enacted yet, so behaviour is unchanged. | 0.3 |
| **RF-1** | **The player's road.** `enact_law` and `repeal_law` through the shared executor (CLAUDE.md's new-action checklist); the "Laws" Net line through the EC-U2 recipe; the lapse loop before ESP-4; the Staff at `calculate_max_actions` and at the AI restore; the three log types. | 0.5 |
| **RF-2** | **The rest of the catalogue.** The other eight effect types, each at its seam with a pin and a sweep row; §6 authored and measured against T1 and T2. | 0.5 |
| **RF-3** | **The AI.** The rung and its purse test; the flip arm; `BASELINE_SERIES` re-recorded once; T3. | 0.3 |
| **RF-4** | **The client.** The LAWS tab (key 8) with its chips, the forecast, the authority line, the Diplomatic Ledger's laws column, and the School card. Parse harness and boot. | 0.4 |
| **DP-1** | **The bank.** The carry rule, the shown ceiling, the AI measurement, and the flip arm. | 0.2 |

**Size.** About 2.2 sessions. Chunk 5 grows from about 2.0 sessions to about 4.2; SR-5a/5b/5c and the reserve are unchanged.

**Order.** RF-0 → RF-1 → RF-2 → RF-3 → RF-4. DP-1 is independent and may ride any session.

**What not to build first:**
- anything in force at boot;
- an AI rung before the player's road has its pins;
- a sixth action point.

---

## §13 Not in v1 — each with its home, or struck

| Item | Disposition |
|---|---|
| A sixth action point (a second tier of the Staff) | **Re-opens on one condition** (R7): Q0's re-measure after RF-1 shows the road still stopped short by action points. Owner: this spec. Measured by `tools/sr1e_titled_probe.py`. |
| Laws for minor courts | Not in v1, and nothing in the client promises them. If they are wanted, SR-D2's gate at Chunk 7 (national flavor) is where to ask. |
| Reforms delivered by events (Q1's third option) | Rejected by the ruling. |
| A peace clause that repeals a law | Not planned and not promised; it would need its own diplomacy gate. |
| The Code in one named client | Struck. The Code Abroad reaches every satellite of the enacting lord. |
| Seasons and the Russian winter | SR-D2 + HC-6, at Chunk 7's gate. |
