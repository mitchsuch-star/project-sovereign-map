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
> - §8 what the player sees; §8a the UI/UX plan; §8b fun and engagement;
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
| Q6 | Seasons | **Not here.** The Russian winter stays with SR-D2 + HC-6 at Chunk 7's gate. | Stated as the default; not objected. *Superseded the same day by the doctrines ruling: the seasons keep their own post-playtest slot, not Chunk 7 (`DOCTRINES_SPEC.md` §0 Q3).* |
| SR-D3 Q3 | Diplomatic points | **Bank one turn.** Unspent points carry over one turn; the pool is capped at 7. | As recommended (AAR-D5). |
| SR-D3 Q5 | The admin pool | **Unchanged.** An unused admin action still pays 25 gold. | Stated as the default. Converting admin actions to diplomatic points would mint points without their price. |
| Q7 | Laws at the start | **None, France included.** No court starts with a law in force. The rivals' law descriptions name what they copy from France (e.g. "the corps system France has used since 1800"). | Asked September 27, 2026, with the doctrines (`DOCTRINES_SPEC.md`). As recommended. |

### §0.1 Readings taken where the answers meet — ✅ CONFIRMED by the user, September 27, 2026 (R3 + R8 replaced by "The Arrears")

Each reading is one catalogue field or one constant to flip. **The user confirmed R1, R2, R4, R5, R6 and R7 as written. For R3 + R8 they asked for "a creative solution to punish and cost money to bring back", and chose "The Arrears" from three options; it replaces both.** RF-1 builds from this list.

- **R1 — The Staff pays upkeep like every law.** ✅ CONFIRMED.
  - This combines Q1 (upkeep) with Q3's one-off enactment price.
  - So a court that cannot pay loses its fifth action.
  - The other reading — the Staff exempt from upkeep — is one catalogue field.
- **R2 — Upkeep is always gold, political laws included.** ✅ CONFIRMED.
  - Q1's own words: "each costs gold every turn".
  - Authority is spent once, at enactment.
- ~~**R3 — A lapse is a repeal.** Re-enacting a lapsed law costs the full price again: no discount, no cooldown.~~ **Replaced by R8 "The Arrears" (below)** for a law that LAPSED. A law the player REPEALED still costs its full price again.
- **R4 — The player may repeal a law at any time.** ✅ CONFIRMED. It costs one admin action (the `revoke_pension` idiom) and refunds nothing.
- **R5 — Laws lapse before rentes.** ✅ CONFIRMED.
  - When the treasury cannot pay, the law with the largest upkeep lapses first, and so on until the chest is whole.
  - The bounced upkeep is refunded: ESP-4's shape, one obligation over.
  - The principle: the state sheds its machinery before it breaks faith with its marshals.
  - The forecast names the doomed law a turn early. Repealing a different law first is how the player chooses which one goes.
- **R6 — Five decks in v1:** France, Austria, Prussia, Russia, Britain. No minor court has laws. ✅ CONFIRMED.
- **R7 — v1 mints ONE new action point, the fifth.** ✅ CONFIRMED.
  - A sixth (a second tier of the Staff) is not built.
  - It re-opens only on a named condition (§13).
- **R8 — "The Arrears": a lapsed law's officers are owed their pay** (✅ RULED by the user, September 27, 2026; replaces R3 for a lapse and the fun review's half-price proposal):
  - A law that **lapsed** — not one the court repealed — may be restored within **10 turns** of its lapse for **half its price plus its arrears**: the law's upkeep for every turn it lay dead, counted from the lapse. Upkeep after restoration is unchanged. One admin action, as at enactment.
  - **Worked for the Staff (9,000 gold, 300 a turn):** 4,800 a turn after the lapse, 6,000 after five, 7,500 after ten. On the eleventh turn it has **dispersed** and costs the full 9,000 again.
  - **Why it punishes:** a lapse never saves gold — every dead turn is still owed if the law comes back, and it comes back without its effect in the meantime. Waiting makes it dearer, so the choice is real: find the money quickly, or let it disperse.
  - **Why it is not a death spiral:** the struggling court's fastest road back to the Staff (4,800) is half the full price, and the forecast warns a turn before any lapse (T7).
  - **A currency law** (authority) restores for half its authority price, rounded up, plus its arrears in gold.
  - **Derived, one store:** the lapse turn rides the `reforms` world field beside the laws in force (§10). The price is computed at every read — the chip, the confirm, the AI rung and the executor — from one function (`reforms.restoration_price`), so shown = applied.
  - GR5: the same rule for every court; the AI rung reads the same price.

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
5. **Re-enact.** A **repealed** law is available again at its full price. A **lapsed** law may be restored within 10 turns for half its price plus its arrears (R8 "The Arrears"), and after that at its full price. The price is `reforms.restoration_price`, read by every surface.

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
- ⚠ **Found by the doctrines review (September 27, 2026): an AI court's authority never comes back.** It has no live writer, so each AI court makes exactly two political acts in a campaign, and "bought back on the field" holds for the player only. The purse test has no diplomatic-point term yet, so "the AI rung weighs it" is RF-3's to make true or strike (§7).

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
| `cures` | removes one named doctrine flaw | the doctrine's own seam (`DOCTRINES_SPEC.md` §3). **Added September 27, 2026 by the doctrines ruling (D-R4); lands at Chunk 7 (DC-2).** No cure clause is authored before its flaw exists. |

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

**Q0 is re-measured after the Staff lands** (`SCORE_MANDATE_PLAN.md` §4 SR-D3): the three roads' titled count, by `tools/sr1e_titled_probe.py`. 45 is not moved. **✅ Re-measured at RF-1 (September 27, 2026): 35 / 35 / 22 on both arms — §12.2.**

---

## §6 The draft catalogue — DRAFT numbers, authored at RF-2, measured against §11

**Three pricing rules:**
- The Staff costs the same for every court: **9,000 gold and 300 a turn**.
- Every political act costs **15 authority**.
- Upkeep runs 100–300 gold a turn.

**France — 6 laws: 5 at Chunk 5, and the Train des Équipages joins at Chunk 7 as the cure for France's doctrine flaw.** The full slate's upkeep is 1,050 gold a turn once the Train joins, sized for §11 T2.

| Law | The act | Currency | Price | Upkeep | Effect |
|---|---|---|---|---|---|
| The Grand Quartier Général | Berthier's Imperial Headquarters, expanded 1805–07 | gold | 9,000 | 300 | `actions` +1 |
| The Train des Équipages | decree of 26 March 1807 | gold | 3,500 | 200 | ~~`supply_capacity` ×1.25~~ **Moved to Chunk 7 by the doctrines ruling** (`DOCTRINES_SPEC.md` D-R3): its only effect becomes `cures` "living off the land" |
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

**The doctrines ruling (September 27, 2026 — `DOCTRINES_SPEC.md`) changes this list at Chunk 7 (DC-2):**
- **Cure clauses are added:** the Corps d'Armée and the Divisional System cure their court's slow arrival (the arrival bar 10 higher — `DOCTRINES_SPEC.md` RV-1); the Militia Transfer cures Britain's dear recruits; the Articles of War cure Prussia's brittleness.
- **A cure works only while its court's Staff is in force** (`DOCTRINES_SPEC.md` RV-15, ✅ CONFIRMED September 27, 2026). The Militia Transfer and the Articles of War keep their other clauses from enactment; their cures wait for the Horse Guards Reforms and the General Staff. The Train des Équipages, a cure only, does nothing until the Grand Quartier Général stands.
- **The rivals' descriptions (`says`) name what they copy from France** (Q7).
- **Stacking with the doctrines (the review, `DOCTRINES_SPEC.md` §2):** Austria's Generalissimus (×0.9, every arm) stacks with Austria's Hereditary Lands (×0.85) if RV-3 is confirmed. Without RV-3, the artillery laws of France, Russia and Britain above would each buy exactly Austria's drafted strength, "The Guns" (artillery ×0.85). After RV-4, Prussia's Military Reorganisation Commission no longer duplicates Prussia's strength.

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

**The cures (added September 27, 2026 by the doctrines review, `DOCTRINES_SPEC.md` RV-10, RV-15).**
- A doctrine's cure takes effect only while its court's Staff is in force (RV-15, ✅ CONFIRMED September 27, 2026). So every rival's catch-up arrives with its Staff, and no deck reorder is needed.
- For Austria and Russia the cure IS the Staff: 9,000 gold, with a purse bar of about 11,500. This rung takes the first law a court can afford, so cheaper laws may be enacted first, and their upkeep raises that bar.
- Measured before the build (`tools/_dc_reach_census.py`): Austria's treasury reaches the bar around turn 20 at peace and after turn 30 under French pressure; Russia's around turn 30 at peace. Only the treasury half of the purse test was measured; the forecast-Net half may hold a pressed court back even with the gold in hand.
- `DOCTRINES_SPEC.md` §6 T8 records, per rival, the turn its cure takes effect, with a target of two of the four by turn 30 on the historical seed and no flaw cured before turn 10. **A miss is this rung's to fix.** The recommended fix: the rung saves for the Staff — which carries every rival's cure — and enacts nothing cheaper once the chest passes half its price.
- Moving a cure to a cheaper law is structural and goes to the user.

**AI authority does not come back (found by the doctrines review, September 27, 2026).**
- `diplomacy.modify_nation_authority` has no callers, and `_process_nation_authority` is a `pass`. So an AI court's authority stays at its boot 60, less what it spends. The only other write is the sovereign-capture shock, and no AI court has a sovereign at boot.
- **So each AI court can make exactly two political acts in a campaign** (60 → 45 → 30, the floor this rung keeps). §3's "bought back on the field" holds for the player only.
- §3 also says this rung weighs the diplomatic point a court loses when its first political act takes it below 60. The purse test above has no such term. **RF-3 either adds the term or strikes the sentence**, and records which in `ENEMY_AI_REFERENCE.md`.

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

## §8a The UI/UX plan — every surface, its file, and its proof

*Added September 27, 2026 by the UI/UX pass. This is build contract; no ruling changed.*

**The rule:** every law says what it does, what it costs and what would take it away, on the surface where the player decides — and nothing about a law ever surprises the player at the end of a turn.

| Surface | Client file | Notes |
|---|---|---|
| **The LAWS tab**, the Strategic Ledger's eighth tab | `strategic_ledger.gd` and `strategic_ledger.tscn` | Three pieces: a `LawsTab` button in `SubTabRow`, `KEY_8` in `_input`, and `_render_laws()`. `_input` maps only `KEY_1`…`KEY_7` today. The digit rule stays: a digit belongs to whoever has the caret (the August 30 review). Eight buttons must fit the tab row at Interface Scale 2.0 — the IQ-10 record flags any button off the viewport — so the labels shorten there if they do not. |
| **Enact and Repeal chips** | `strategic_ledger.gd`, in the CN-3 idiom: a chip sends the typed command through the shared pipeline | Honest availability. An unavailable chip is dimmed beside `law_refusal`'s reason; an available one states its terms: price, upkeep, and the authority lines it crosses. |
| **The enactment confirm** — authority priced aloud | the chip's confirm, in an existing confirm idiom (no new modal type) | "Authority 100 → 85 — the marshals' calm holds above 70." |
| **The forecast** | the LAWS tab's footer, the end-turn banner (`main.gd`), the morning dispatch (`dispatch_view.gd`) | It names the law that would lapse first and the gold that saves it. It offers "repeal X instead" as a chip when an admin action remains, and says so when none does. |
| **The Net line "Laws"** | every surface that prints Net (RF-1's EC-U2 recipe, including `strategic_ledger.gd`) | — |
| **Other courts' laws** | `diplomatic_ledger.gd` `_render_nations`: one line per court | Shares the two-line density budget with the doctrine line (`DOCTRINES_SPEC.md` §4a). |
| **The beats** | the morning dispatch and the campaign log | "Austria raises the Landwehr"; a lapse is named as a lapse, and a cure beat names its flaw (`DOCTRINES_SPEC.md` §4). |
| **The fifth action** | the top bar's action count (`top_bar.gd`) | It appears at the refill after enactment, and the dispatch names why. The compact mode below 1,180 logical px must still show it. |
| **The bank** (DP-1) | the dispatch's regen breakdown ("+N carried") and the top bar's DP | The pool shows as regen + carried, never over its own printed maximum. |
| **The School card, 19 → 20** | `tutorial_overlay.gd`, with the tutorial state's card list | The card opens the LAWS tab and names one law; driven by `tools/tutorial_overlay_harness.gd`. |
| **Help and the desk** | the help block (`first_contact.py`); `question_desk.py` ("what laws are in force?", "what does the Staff cost?") | Golden-corpus rows. |

**Visual proof.**
- `tools/iq10_capture_payloads.py` gains `cap_laws()`. It stages four boards: the tab at boot; the Staff in force; a forecast naming a doomed law; a rival's laws on its nation card.
- Each is rendered at Interface Scale 1.0 and 2.0, and the machine record must show no overflow. The frames are committed, dated.
- The user's visual sign-off closes RF-4.

**Bandwidth.** The client work grows from 0.4 to 1.0 session, split across RF-4a, RF-4b and RF-4c (§12).

## §8b Fun and engagement — what the laws are for

**The promise:** the long peace has something to pay for; every law is a choice between a stronger state and a fuller chest; and every court's reform is a story the player can watch.

**The decisions:**
- **Which law first.** The Staff — the fifth action, 9,000 gold and 300 a turn — against three cheaper acts, or the Train des Équipages before a war in the east.
- **Upkeep or war chest.** France's full slate costs about 1,050 a turn. Every law in force is gold not saved for the next coalition.
- **Authority as a currency.** A political act spends the Emperor's standing, and victories buy it back. The marshals' calm lives above 70.
- **What to lose.** When the chest cannot pay, the player chooses which law lapses by repealing another first.

**The moments:**
- "The Grand Quartier Général is established — the fifth action is ours."
- "Austria raises the Landwehr."
- "Vienna adopts the corps d'armée."
- The forecast's drama: "The Grand Quartier Général lapses next turn unless 400 gold is found."

**The death-spiral watch.** R5 lapses the largest upkeep first, and that is always the Staff — the one law a struggling France most needs. The mitigations:
- the forecast warns a turn early, on three surfaces;
- repealing another law first keeps the Staff, for one admin action, and the forecast says when none remains;
- **R8 "The Arrears" (✅ RULED September 27, 2026):** a law that lapsed may be restored within 10 turns for half its price plus its upkeep for every turn it lay dead (the Staff: 4,800 a turn after the lapse, 7,500 after ten); then it disperses and costs the full price.

T7 measures all three.

**For the rival courts too.** The deck order gives every AI court a visible arc, and its enactments and lapses are dispatch beats — diplomacy has no fog. With the doctrines (`DOCTRINES_SPEC.md` §4b), a rival's reform is the moment its flaw closes, and an uncured flaw is a window the player can read.

**The fun targets are falsifiable:** T7 (no death spiral) and T8 (nothing unnamed), §11.

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

**Old saves.** A pre-reform save backfills the catalogue from the scenario at load, with nothing in force — the EB-2 idiom, drift-pinned. It does so **only when the save's `scenario_name` is the 1805 campaign** (the doctrines review, `DOCTRINES_SPEC.md` §9): a tutorial or modded-scenario save receives no deck.

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
| T2 | The sink (Q1) | A France holding its full slate at peace spends 40–60% of its golden-peace surplus on upkeep, with the IQ-1 control arm as the baseline. Measured at RF-2 on the five-law slate, and re-run at DC-2 with the Train des Équipages in it (`DOCTRINES_SPEC.md` §7). |
| T3 | AI competence (GR5) | On the ambient board, at least two AI great powers enact at least one law by turn 25, and no AI law lapses before turn 40 in a court that is not losing provinces. |
| T4 | The lapse | On a staged insolvent France: the largest law lapses first; the refund makes the chest whole; the forecast named that law a turn earlier; restoring it within 10 turns charges its Arrears price (R8: half its price plus the dead turns' upkeep), and after that its full price. *(R8 amendment, September 27, 2026: this line read "re-enacting charges the full price" — R3, which R8 replaced for a lapse.)* |
| T5 | The Staff on both boards | The fifth action appears at the first refill after enactment and is gone at the first refill after a lapse — for France and for an AI court. |
| T6 | The bank | A court that spends nothing carries one turn's points, up to 7 and no further. The pool, the dispatch and the top bar agree. |
| T7 | No death spiral (§8b) | On a staged insolvent France holding the Staff and two cheaper laws:<br>• the forecast names the doomed law a turn early on the LAWS tab, the end-turn banner and the dispatch;<br>• a "repeal X instead" chip keeps the Staff when an admin action remains, and the forecast says so when none does;<br>• after solvency returns on the commanded arm, a lapsed Staff can be restored within 10 turns at its Arrears price (R8: half its price plus the dead turns' upkeep), and the LAWS tab, the chip and the AI rung all quote that one price. |
| T8 | Nothing unnamed (§8b) | Every law effect the player can see is named where it applies: the fifth action at the refill, the recruit price's named term, the supply headline, the vassal forecast. The census idiom is the doctrines' T10. |
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
| **RF-4a** | **The LAWS tab** (§8a). The eighth tab: its button and `KEY_8`, keeping the digit-belongs-to-the-caret rule. Its rows; its Enact and Repeal chips with honest availability; its footer; the enactment confirm with authority priced aloud. Parse harness and boot. | 0.4 |
| **RF-4b** | **The laws everywhere else** (§8a): the forecast on three surfaces, with its "repeal X instead" chip; the nation cards' laws line; the beats; the fifth action on the top bar, in compact mode too; the DP bank's display; help and the desk. Parse harness and boot. | 0.3 |
| **RF-4c** | **The School card and the visual pass.** The School card (19 → 20, driven by the tutorial overlay harness). `cap_laws()` frames at Interface Scale 1.0 and 2.0, and the overflow fixes the machine record asks for. T7 and T8. The user's visual sign-off. | 0.3 |
| **DP-1** | **The bank.** The carry rule, the shown ceiling, the AI measurement, and the flip arm. | 0.2 |

**Size.** About 2.8 sessions, 1.0 of them client work (§8a — the September 27 UI/UX pass raised it from 0.4). Chunk 5 grows from about 2.0 sessions to about 4.8; SR-5a/5b/5c and the reserve are unchanged.

**Order.** RF-0 → RF-1 → RF-2 → RF-3 → RF-4a → RF-4b → RF-4c. DP-1 is independent and may ride any session.

**What not to build first:**
- anything in force at boot;
- an AI rung before the player's road has its pins;
- a sixth action point.


### §12.1 RF-0 — LANDED September 27, 2026 (landing record)

**The substrate** (rules `SYSTEMS_REFERENCE.md` §74.1). `backend/game_logic/reforms.py` holds the closed effect set (§4) with `WIRED_EFFECT_TYPES` (`actions` alone), the deck and in-force readers, `law_upkeep_bill`, `staff_actions`, the ONE predicate `law_refusal`, and the ONE price `restoration_price` (R8 "The Arrears"). ONE serialized world field, `reforms`, carries the in-force state ON each row (`enacted_turn`, `lapsed_turn`); the scenario and the save share its shape (`from_dict` reads both). `europe_1805.json` authors each great power's Staff at one price for all (9,000 gold, 300 a turn), nothing in force. The validator block refuses an unwired or unknown type, a third clause, a second or unequal Staff, and any in-force state in a scenario. `save_manager._backfill_reforms` arms a pre-reform 1805 save only (a tutorial or modded save gets no deck).

- **Pins:** `tests/test_rf0_the_laws_substrate.py` (35). Sweep `tools/_sweep_rf0.json` 19/19 killed, 0 INERT.
- **Measured:** nothing is in force at boot and no verb exists, so `BASELINE_SERIES` + M1–M7 cannot move.

### §12.2 RF-1 — LANDED September 27, 2026 (landing record)

**The player's road** (rules `SYSTEMS_REFERENCE.md` §74.2). `enact_law` and `repeal_law` through the shared executor (the whole new-action checklist); the "Laws" Net line through the EC-U2 recipe; the lapse loop before ESP-4; the Staff at `calculate_max_actions` and at the AI restore; the three log types. Lever `reforms.THE_STATE_HAS_LAWS`.

- **The verbs.** One admin action each; the price is `restoration_price`'s quote, charged by the ONE mutation `reforms.enact_law` (shown = applied); a repeal refunds nothing and never earns the Arrears. Refusals are free and in the predicate's own words. The authority spend names the thresholds it crosses.
- **The words.** `enact the Staff` · the authored name (accents and case folded) · `re-enact` · `repeal`. A QUESTION or a hedge is answered with the court's laws and prices, and nothing is enacted. An order put to a marshal is refused in words, free (the Admiralty's idiom); the foreign minister and the Emperor are decoration. **Two defects measured and fixed before the pins:** `Talleyrand, enact the Staff` answered CR-2's "Did you mean Ney?", and `Ney, enact the Staff` got Berthier's generic shrug. `routed_order_words` regenerated (`enact`, `reenact`, `repeal`); 15 golden-corpus rows pass under both arms of CX-1's lever.
- **The lapse (T4, R5).** It runs after the income phase and immediately BEFORE ESP-4's rente default and the bankruptcy check — pinned in the turn itself. The largest upkeep lapses first (tie: the most recently enacted); the refund makes the chest whole and is folded out of the applied record; `lapsed_turn` starts the Arrears clock; the player's lapse is told in the end-turn report with its Arrears price. GR5.
- **The Staff (T5).** Felt at the next refill, never the turn it is enacted; lost at the refill after a lapse or repeal; the same derived term for the player and for an AI court.
- **The prompt.** The action list and two board-independent examples changed the parse prompt, and "enacts"/"repeals" the recovery prompt's verb list. The 17 authored IQ-9 cassettes are re-stamped, and both attribution records re-derived for the change common to both arms (`tests/data/l1_prompt_restamp.json`, CRT-7's recovery constant).
- **Pins consciously flipped:** the fourteen campaign-log count pins (168 → 171) and IQ-7's census; the Net-component tripwire (`test_economy_ledger_reconciliation.EXPECTED_NET_SIGNS` gains `laws`).
- **Pins:** `tests/test_rf1_the_players_road.py` (73). Sweep `tools/_sweep_rf1.json` 54/54 killed, 0 INERT (the first pass found two INERT — the Emperor's exemption and the route's own hedge guard, each a defence in depth the shipped road never reaches; both are now pinned on the road they guard).
- **Measured.** `BASELINE_SERIES` + M1–M7 + the AI-V assurance byte-identical — nothing is enacted on the ambient board (the AI's rung is RF-3's). Parse harness EXIT=0, boot 0 `SCRIPT ERROR`.
- **Q0 after RF-1 (§5):** the three roads re-driven at HEAD, as authored and with the Staff bought at its first affordable turn (turn 4 on all three): **35 / 35 / 22 at turn 41 on both arms**. The roads spend 35–50 of their actions in forty turns, so the fifth goes unused — but for three orders on opening B, whose tail holds longer (35 titled at turn 30 against 26) and ends at the same 22. The as-authored arms equal the pre-RF commit's (measured on a scratch worktree at `e9d32403`), so RF-1 is inert on them; their drift since SR-2e (37 / 31 / 31) belongs to the slices landed between. The best point on any road is still 39; **45 is not moved.** Archives `docs/audits/playtest_digests/rf1-q0-*` (scripts `tools/playtest_scripts/rf1_q0_*_staff.json`); the standing xfail reads them. **For RF-2's T1:** the chest crosses 9,000 on turn 4 of all three roads — earlier than Q3's "around turns 10–15"; the price is in-band tunable and RF-2's T1 measurement owns it.
- **§11 against this slice:** T4 MET on its lapse clauses (the forecast clause is RF-4b's); T5 MET for the player and an AI court; T0's boot clause MET. T1, T2, T3, T6, T7 and T8 belong to later slices.
- **Amended in this slice:** §2 item 5 and T4 read "full price" for a lapsed law (R3, which R8 replaced for a lapse); both now state the Arrears.
- **Not built here, each owned:** the forecast on three surfaces, the dispatch beats, the rivals' laws on the nation cards and the help block's verbs (RF-4b); the LAWS tab (RF-4a); the other eight effect types and the catalogue (RF-2); the AI rung (RF-3); the School card (RF-4c).

---

## §13 Not in v1 — each with its home, or struck

| Item | Disposition |
|---|---|
| A sixth action point (a second tier of the Staff) | **Re-opens on one condition** (R7): Q0's re-measure after RF-1 shows the road still stopped short by action points. Owner: this spec. Measured by `tools/sr1e_titled_probe.py`. |
| Laws for minor courts | Not in v1, and nothing in the client promises them. If they are wanted, SR-D2's gate at Chunk 7 (national flavor) is where to ask. |
| Reforms delivered by events (Q1's third option) | Rejected by the ruling. |
| A peace clause that repeals a law | Not planned and not promised; it would need its own diplomacy gate. |
| The Code in one named client | Struck. The Code Abroad reaches every satellite of the enacting lord. |
| Seasons and the Russian winter | ~~SR-D2 + HC-6, at Chunk 7's gate.~~ The seasons keep their own slot after the first outside playtest (`SEASONS_WEATHER_SPEC.md`); Russia's doctrine excludes the winter (`DOCTRINES_SPEC.md` §0 Q3). |
