# VP-1 — "The Emperor's Designs": the gate record

**Status:** ✅ **RULED October 22, 2026 under the user's standing delegation** ("make design calls please do research"), on master at `200cdf91`. **Owner:** Pre-Deploy S14b (`docs/PRE_DEPLOY_PLAN.md` §2), built in three parts (§9). **Part 1 — the substrate, unarmed — ✅ LANDED October 22, 2026 (landing record §12).** Parts 2 and 3 to build.

**How it was ruled.** Eight read-only researchers verified the mechanics each design would hook; three designers drafted complete proposals from three angles (history-first, player-experience-first, systems-reuse-first); three judges scored them through a historian's, an architect's and a playtester's lens; one synthesis merged the highest-scored (history-first) with the best of the others; two adversarial critics checked it against the repo and the project's rules and returned 35 corrections, every one applied below or answered. Plan 3's "five gate questions" (`docs/audits/ROAD_TO_EA_REPLAN_2026_08_03.md` line 52) are not in the repo — only their recommendations are — so Q1–Q5 answer those recommendations and say so.

**No user ruling is reversed.** Six amendments of ruled specs are flagged, each carried into its spec when its part lands:

| | Amends | What |
|---|---|---|
| **A1** | `NATION_AGENDAS_SPEC.md` §9 ("on the agenda substrate") | read as the substrate's schema, predicates and payload shapes — France's designs live in their own store, never `world.agendas` (§0 Q5) |
| **A2** | `GAME_END_SPEC.md` R2 / `game_end` tier table ("the SHAPE is the ruling") | the Verdict gains one +2 score term for the decisive peace (§4) |
| **A3** | `VASSAL_DEEPENING_SPEC.md` (autonomy drift −2 a turn for a satellite) | a Confederation member's downward drift is suspended while the Rhine construction holds (§2.1) |
| **A4** | `ENDGAME_PLAN.md` D10 / §4 ("ONE scene with four registers") | a fifth register, THE DECISIVE PEACE (§4) |
| **A5** | `NATION_AGENDAS_SPEC.md` §9 seed note ("reuse the NA-6 §11.3 reward shape", +2,000 gold) | no design pays gold — DDB-D7's idle chest (§0 Q9) |
| **A6** | `ROADMAP.md` row 13 (VP-2 "what remains") | the objective-shaped triumph and the decisive-peace victory move here; "un-gate `_check_victory_conditions`" is struck (mark-and-continue is ruled) |

Kept as ruled, and named so no part reverses it: ruling J / PC-R7 (ii) — the paid compensation (Salzburg for Tyrol) **is** the moderate Pressburg, and `compensation_offsets` nets either form (§2.2's manners read it, never change it); EG-D2 — the commanded arm is never re-scripted; SF-NAV-1-D1 — the Continental System anchor (SHUT OUT for 8 turns) stays the user's (§2.5); G2 / EAD-2 / ES-4 — gold never wins, the crown term is not halved, no licence income (§5).

---

## §0 The gate record

| # | Question | Ruling | Rejected (the historically fuller option named) |
|---|---|---|---|
| 1 | Objective, or a region race? | **Objective-shaped.** A design names courts, at most three provinces, one port line, or a signed peace. No design counts provinces; the Congress's 45 stays the only count in the game. | "Hold N provinces"; Natural Frontiers (France holds them at boot). *Fuller:* Napoleon's 1807 map as a map-state target — it completes with no French act and counts allies' conquests and status-quo titles. |
| 2 | How many paths; how do they branch? | **Three roads, two designs each — a construction, then a seal.** The road is chosen by an irreversible, priced **proclamation** from the Cabinet (F1) road page (§3). | The deed-lock (the first peace's shape picks the road): an accepted AI letter could take it, and a netted moderate Pressburg would read as the wrong road — its shape test survives as the manner preview. Locking on the first fulfilled design (Bavaria's vassalage is cheap on turn 1). *Fuller:* all three roads at once — Napoleon's overreach; no choice, and alarm passes the hold ceiling (80). |
| 3 | Hard stop, or mark and continue? | **Mark and continue.** The decisive peace stays out of `TERMINAL_CAUSES`. | *Fuller:* the campaign closes at its treaty — reopens 20 test files / 97 `game_over` lines and EC-6. |
| 4 | A new loss condition? | **None.** The Fall and the Humbled Peace stand (GE R1). A road can **lapse** (§3). | *Fuller:* "the Grand Empire collapses" as a defeat — a second defeat register stamped by a seeded roll. |
| 5 | Where do the designs live? | **Their own store, `world.imperial_designs` (§3)**, reusing the substrate's predicates and shapes: `agendas._controlled_by_self_or_vassal`, `game_end.province_title_kind`, `formations.format_progress`, the formations `rewarded` latch, `formations._announce`. `get_active_agenda("France")` stays None (A1). | *Fuller:* a France deck in `world.agendas`, so Europe prices Napoleon's aims — measured: `agenda_acceptance_mod` fires −8 on turn 8, the glory hunters re-target, a `forms` block would rename France, four deckless pins go red, and every AI arm moves. New `AGENDA_TYPES` members (the same reach). |
| 6 | What are the designs? | **Six (§2):** the Rhine is clientage, Italy is two crowns, the System is ports and then Britain's own signature. | A minted Confederation tag (reverses NA §9 / SR-8c; unbuildable without the new-tag checklist). *Fuller:* a Westphalia carve, a Bonaparte Naples template, Rome 1809 — **struck from every surface, not deferred** (the authored `RomanRepublic` formable is untouched). |
| 7 | Is humbling a court its own road? | **No — it is the seal of each land road**, in one closed set of **manners**: `partition`, `subjugation`, `moderate` (§2.2). No title says "humble", so nothing collides with THE HUMBLED PEACE. | A break-her / win-her deck per court. *Fuller:* a two-emperor Tilsit with Russia — it falls in July 1807 (turn 44, the Verdict's own turn), outside the 40-turn frame. |
| 8 | Read live, or latched? | **Latched on completion; the live reading is shown as held or lapsed.** Holds: clients 4 end turns, ports K = 6, titles 1; peaces are events. Hold counters run only once the road is proclaimed; **terms are facts** and are always recorded (§3). | Live "active-while" predicates: closure reads 0 at any truce with Britain; a one-turn touch of 13 makes Spain's exit (turn 15–16) a coin flip. |
| 9 | Rewards? | **Never gold (A5).** Paid by the construction designs: one one-shot (Naples's +15 authority) and two live-gated (the Rhine's suspended drift, the Continent's order). The seals pay the triumph (§4). | NA-6's +2,000 gold (feeds DDB-D7's idle hoard). Latching Britain SHUT OUT (counts twice). *Fuller:* Trianon licence income (ES-4, rejected by the user's own economy ruling). |
| 10 | Teeth; how Europe reacts? | **No AI code reads the store.** Europe reacts through what it already reads — alarm, relations, the Revanche, the volte-face, the Congress latch — moved at the proclamation, at fulfilment, and by each native act. | *Fuller:* an AI rung reading France's road (Prussia's war weight rising on the Act) — moves every arm and needs `AI_INTENT_SPEC` §6's gate; struck. |
| 11 | The triumph? | **THE DECISIVE PEACE, `CAUSE_DECISIVE_PEACE` (§4).** | "Britain sues" (turn 8 on every seed); "at peace with every great power" (CMD-A from turn 14); "N peaces signed"; the name "triumph" (the Verdict's top tier). |
| 12 | Beside the Congress and the Verdict? | **A waypoint toward the Congress**: the Verdict +2 as a score term, not a floor (A2); no Congress term granted. The Rhine construction **can** move the Congress count (§10). | A tier floor of 2 (erases the Congress's distinction); granting Congress recognition (counts twice). |
| 13 | WO-D4(b)? | **Absorbed as Road III (§5).** | §5 |
| 14 | SF-ECON-1? | **Absorbed: one verb, four Acts of the Empire (§5).** | §5 |
| 15 | The done-when arm? | **VP1-CS**, a new script copied from the Tilsit road (§9 Part 3); the land roads' arms reported per seed beside it. *Part 1's head measured (§12.1): the Tilsit road latches the Blockade on no seed at K = 6 today, so by §10's own condition **VP1-RH carries the done-when** and VP1-CS is reported per seed beside it.* | `commanded_full40` (peaks at 10/26 ports, never cedes a province to France); staged fixtures alone; tuning the 50% line. |
| 16 | Condition (c)? | **The sentence below.** | A Congress-only sentence (the Congress is unreached on every played road); copy promising Westphalia, a Bonaparte Naples or a peacetime System. |
| 17 | Siblings (Rule 10)? | **VP1-X1 … X10 (§10)**, filed in `BUG_FIXES.md` §VP1 with this record; each reproduced before it is built. | Building on any of them unreproduced. |

**Condition (c)** — the store page's one sentence, printed verbatim by the desk's goal answer:

> *"A campaign is for deciding what Napoleon's empire will be — Protector of the Rhine, master of Italy from Milan to Naples, or a Continent shut against Britain — and forcing the decisive peace that seals it, while the coalitions you provoke, the satellites' bills and the Verdict of History in July 1807 judge the reign; the Congress of Paris, where Europe signs or is shut out, crowns the greatest."*

---

## §1 Why (measured)

- **No road reaches an ending.** DD-B found none within 20 turns. The Congress is unreached on every played road (SR-1e peaked at 39 titled provinces; GE-V reached 35 by turn 12, its best 41; the boot bloc holds 35). On today's tree (`docs/audits/score_runs/2026_10_21_rr6x3/`) the commanded France holds **9 / 27 / 28** provinces at turn 40 on historical / austerlitz / marengo (historical walks EG-D2's lawful road since RR6-X3 re-timed it); its ports peak at 10 of 26; it signs no cession to France. GE-1's Verdict read contested on every commanded seed.
- **The long peace has nothing in it.** On the austerlitz and marengo arms the chest grows +19,000–28,000 gold over turns 15–30 (47,904 by turn 30 on austerlitz) while France stands at peace with every great power; on DD-B's peace road it reached 29,419–31,889 by turn 20 and LAWS was opened 0 times (DDB-D7). On the historical arm's war road the chest shrinks (6,142 at turn 15 → 4,249 at turn 30): the Acts are a **peace-road** sink, and the record says so (§5).
- **Nothing says what a campaign is for.** Condition (c) was unmet.

---

## §2 The designs

All predicates are nation-parameterized over the store's authored `owner` ("France"); every number is an in-band tunable (§8). "Reproduce first" marks a fact Part 1's head re-measures on the day's tree before it is pinned.

### Road I — The Protector of the Rhine (proclamation: "The Act of Confederation"; gate: Bavaria is France's ally or vassal)

**2.1 `rhine.confederation` — The Confederation of the Rhine** (the construction)
- **History.** The Act was signed 12 July 1806; Francis II laid down the imperial crown on 6 August; Saxony joined at Posen on 11 December; Westphalia came in 1807. On this map Swabia folds in Württemberg and Baden, Hesse carries Nassau, and Hanover stands in for Jérôme's Westphalia.
- **Predicate (`clients`).** At least **3 of [Bavaria, Hesse, Saxony, Hanover]** have `world._top_overlord(court) == owner` and loyalty ≥ `SATELLITE_TITLE_LOYALTY` (40 — the `province_title_kind` line, made one named constant). A court that is gone counts if its capital is titled to the owner's bloc. Held 4 end turns, then latched. Never `acquire_regions` — `AN_ALLY_IS_NOT_COVETED` would read Bavaria's boot alliance as already satisfied. Boot reading: 0 of 3.
- **Progress** (the Balance block, the road page): "2 of 3 German courts under the Emperor's protection · Hesse 31 → 40 in 3 turns · Saxony at peace: Cabinet → Propose Open Borders, then Propose Vassal" (loyalty forecasts from `vassal.forecast_vassal_loyalty`; every hint names a control, never a typed order).
- **Reward — the Protector's shield (A3, live-gated).** While the road stands and the design holds, a member's downward autonomy drift (`AUTONOMY_DRIFT`: satellite −2, puppet −4 a turn) is suspended — read through one seam in `process_vassal_loyalty`, keyed on the store's owner and the members, so every loyalty surface (the forecast, the Ledger, the dispatch) shows what is applied. *Why not the contingent floor:* the loyal tier (60, `CONTRIBUTION_LOYAL_MIN`) is VS-4's single source for the auto-join, reinforcement eligibility, the muster and petitions, and `contingent_size` is linear in loyalty with a 3,000 minimum — at 40–59 Saxony would send nothing and Hesse almost nothing (measured on the boot world), so a lowered floor would be a reward that does not bite.
- **Teeth.** At the proclamation: alarm +8 (`act_of_confederation`), Austria −10, Prussia −10. At fulfilment: alarm +10, Austria −30, Prussia −30, the grudge "The German Question". Native costs stand: alarm +5 per treaty vassal and +25 per conquest, bribes below loyalty 35, the defection cascade, the contingents' dead, Austria's `primacy_germany` live.
- **Europe.** Prussia's −40 reaches her war council by machinery, so Jena can come of the Act (reproduce first: measured per seed, never promised).

**2.2 `rhine.german_crown` — a German crown brought to terms** (the seal)
- **History.** Pressburg (26 December 1805); Tilsit's partition of Prussia (July 1807); the road not taken, Talleyrand's Strasbourg memorandum of 17 October 1805 — beat Austria, then make her an ally against Russia by pointing her east.
- **Predicate (`brought_to_terms`).** Courts [Austria, Prussia]; an unbroken latch in `state.terms[court]`, written by `note_terms` at every war-ending treaty the owner signs, in one closed set of manners:
  - `partition` — the punitive record: at least 2 of her own homeland provinces, or her capital, ceded to the owner's chain **without** a compensation (Pressburg as signed; Tilsit when the court is Prussia);
  - `subjugation` — she becomes the owner's vassal;
  - `moderate` — a peace with at least 1 homeland cession **and** a compensation (either form — ruling J's moderate Pressburg, `compensation_offsets` unchanged), followed by the volte-face alliance within `VOLTE_FACE_WINDOW` (20 turns).
  - Guard: no province of the owner's opening homeland stands in her bloc at the signature. A new war between them breaks the latch. Manner precedence when one treaty reads two: `subjugation`, then `partition`, then `moderate`; the set is pinned.
- **Progress.** Live war score, each manner's bar, and `volte_face_courtship`'s turns left.
- **Teeth.** `partition` arms the Revanche and forecloses the volte-face. `moderate` with the **pointed** compensation suspends the designs ahead of the pointed one (Austria's `redeem_italy` and `primacy_germany`) for `COMPENSATION_TERM_TURNS` (15) and costs the Ottoman −15 (`RELATION_SOLD_OUT_VS_FRANCE`) — fifteen quiet turns bought at the Porte's expense; when the term lapses, `primacy_germany` wakes against a Germany that is now the Emperor's (measured on the Rhine arm, reported). Britain's bond (Chaumont) prices a separate peace — breaking it reneges on the bond. Prussia boots at peace: her seal needs a war France chooses.

### Road II — The Crowns of Italy (proclamation: "The Schönbrunn Proclamation"; gate: the Kingdom of Italy is France's vassal)

**2.3 `crowns.naples` — The Throne of Naples** (the construction)
- **History.** Naples's neutrality (21 September 1805), then the Anglo-Russian landing (20 November); Schönbrunn, 27 December: "the dynasty of Naples has ceased to reign"; Joseph king on 30 March 1806. The copy says plainly that the Sicilian rump and the Bonaparte throne itself are not modelled — the design is Naples brought into the Empire.
- **Predicate (`titled`).** `province_title_kind(world, "Naples", owner)` ∈ {homeland, treaty, conquest}: Naples a vassal at loyalty ≥ 40, or a conquest after 12 quiet turns (R81 eliminates the court on capture). No guided row cedes a capital (`settlement_baseline.py:1103-1112`), so that road is not promised.
- **Reward (one-shot).** +15 authority, paid once through the formations `rewarded` latch — it answers the grip term below 70 and funds the 15-authority laws.
- **Teeth — the Bourbon compact.** At the proclamation: alarm +8 (`schonbrunn`), Naples −10, Spain −10 (France and Spain stand at exactly 40, the alliance line; the blow can cost the alliance — reproduce first). The way to a war France may declare cheaply is the existing one: **issue Naples an ultimatum** from the Cabinet; its rejection grants the casus belli that halves the declaration's penalty (`diplomatic_executor.py:5394`). The way in: through Rome, or an expedition of at most 15,000 men into the Royal Navy's coverage.

**2.4 `crowns.iron_crown` — The Iron Crown** (the seal)
- **History.** The coronation at Milan (26 May 1805); Pressburg's Venetia — Carniola stands in for it on this map.
- **Predicate.** `titled` [Milan, Piedmont, Carniola] **and** `brought_to_terms` [Austria] (the shared latch). Progress opens at 2 of 3 (reproduce first). Carniola comes by a cession to the Kingdom of Italy at the table (PC-F52 / F53) or a conquest after 12 quiet turns, and joins the War Purpose card's article pool on this road.
- **Teeth.** Archduke Charles's 54,000 stand at Carniola; Milan is fragile (lost on CMD-A turn 5); Austria's `redeem_italy` and Sardinia's `house_of_savoy_restored` aim at the same ground; a gift of Naples or Piedmont to the Kingdom of Italy feeds its dormant risorgimento design.

### Road III — The Continental System, "Break Perfidious Albion" (proclamation: "The Blockade of the British Isles"; gate: France is at war with the trade-dominance court)

**2.5 `system.blockade` — The Blockade of the British Isles** (the construction)
- **Name.** Not "The Berlin Decree" — that is the live law id `berlin_decree`.
- **Predicate (`shut_ports`).** `closed_ports_against(world, trade_dominance_nation(world))` ≥ ceil(`cs_shutout_pct` × `continental_ports_total` / 100) = **13** (derived from the Congress line, never tuned), held **K = 6** end turns, then latched; if the trade-dominance court is gone, fulfilled.
- **K, ruled.** Six end turns — a season, Berlin's decree to the next spring's sailing — in band 4–8. It is **not** SF-NAV-1-D1's anchor (SHUT OUT, which also needs no British corps on the Continent, for 8 turns on 2 of 3 seeds — still the user's to rule); the Blockade counts ports only. Part 1's head re-measures the latch on today's tree on three seeds and **reports** it; if no seed latches at 6, the land arms carry the done-when (§9), and K is not moved to fit.
- **Arithmetic** (reproduce first). At boot 10 of 26 shut (France 4, Holland 2, the Kingdom of Italy 1, Spain 3). Spain's exit on turn 15–16 takes it to 7, so the 13 needs six more — the levers the progress line and the counsel name: members by treaty clause (Austria 1, Russia 2, Prussia, Denmark, the Ottoman), conquered coasts (Lisbon, Rome, Naples — NV-10's conquered-coast rule; this is how the archived Tilsit road held 14–15 after turn 16), and satellites. No margin is promised.
- **Progress** (the Balance block, the Admiralty): "11 of 26 ports shut to Britain — 13 needed, held 0 of 6 · open: Denmark (2), Ottoman (3) … · a truce with Britain opens every port that is not a member".
- **Reward — the Continent's order (live-gated).** France's alarm decays `CS_ORDER_DECAY` (2) more each turn while the road stands and closure is ≥ 13 — beside `coalition.py:1592-1597`, on the owner's slot, outside the decay cap.
- **Teeth.** At the proclamation: alarm +8 (`blockade`), Portugal −15, Denmark −15, and the proclamation turns **off** `continental_system_lift_offered` (`diplomatic_templates.py:4121`) for the road's life — Talleyrand stops drafting the System's lifting into French peace offers to Britain. At the latch: Russia, Sweden and Denmark −10 each ("the System's resentment" — the historical answer to the decay). Native costs stand: the war with Britain must go on; each Tilsit clause costs +10 alarm; members lose trade; a member at war with France leaves.

**2.6 `system.continent_peace` — The Peace of the Continent** (the seal)
- **History.** A counterfactual, and the copy says so: Fox's 1806 talks broke on Hanover and Sicily; London signed only in 1814.
- **Predicate (`britain_signs`).** After the Blockade has latched, the trade-dominance court signs a war-ending peace with the owner (never an armistice), and at the signature at least one great power stands in the System by the owner's own clause (satellites auto-join and do not count), the treaty carries no lift clause, and the owner's homeland is whole.
- **The seal exempts its own construction.** Britain's peace reopens every port that is not a member, so the Blockade reads below 13 at the signature by construction: at that moment Road III's construction is read by the member test instead of the port count (pinned: a Blockade that reads lapsed at the signing still seals; a member that walks out before it does not).
- **Teeth.** The Congress's SHUT OUT reading is lost and Britain must RECOGNIZE instead — except a peace signed while the Congress sits, which latches "table".

---

## §3 The paths and the irreversible branch

- **The verb.** `proclaim_design {road}` — a diplomatic act (it spends 2 DP and moves relations), so its only player road is the **Cabinet (F1) road page's Proclaim button** with a "This cannot be undone" confirm; the button sends the command line, and a typed proclamation is redirected to the Cabinet like every diplomatic verb (its head joins the parser's diplomatic funnel and `main.gd`'s `DIPLO_FAMILY_KEYWORDS`; `tests/test_wo_slice7_cabinet_door.py` re-seated). Cost: 1 administrative action + 2 DP + its teeth. The full new-action recipe (CLAUDE.md), with `gen_routed_order_words` and a golden-corpus row. Not in `objection_actions` (a decree, not an order — the `purchase_levy` judgement); Talleyrand's pre-proposal objection does not apply (it is no proposal).
- **The refusal.** One predicate, `proclaim_refusal`, shared by the executor, the row and the counsel; keyed on the store's owner (a nation with no authored block is refused). It refuses a second road (naming the road and its date), a lost Paris, a captive Emperor, a vassal France, a terminal ending, and a failed road gate. All three gates are true at boot (reproduce first).
- **Before the proclamation** every road can be read, nothing pays, no hold counter runs, no triumph is possible — but `note_terms` records the owner's terms with each court from the first turn (a fact, not a counter), so a Pressburg signed on turn 7 seals Road I proclaimed on turn 8 (pinned).
- **The forsworn roads** stay on the page, marked "Forsworn when the Emperor proclaimed …".
- **The prologue (copy only).** The first war-ending peace with Austria or Russia (or Vienna taken) while no road is proclaimed raises "THE SUN OF AUSTERLITZ": a HIGH dispatch beat, a Moniteur special, and Talleyrand's road counsel (which names the seal the peace already satisfies). It carries no reward; its turn is stored (`state.prologue_turn`) so it fires once, across a load.
- **The second, smaller branch — the manner.** `manner_for_terms(world, victor, court, terms)` (nation-parameterized) prints its line beside the Revanche line on the settlement table, the bilateral preview and the incoming-proposal popup (VP1-X7 builds the Revanche line on the two payloads that lack it); a drift pin holds the line shown to the manner applied.
- **The one new serialized field.** `world.imperial_designs` = the authored block (copied from the scenario's `imperial_designs` key at boot) + `state = {road, proclaimed_turn, prologue_turn, fulfilled, rewarded, hold, terms, acts}`. Old saves backfilled by `_backfill_imperial_designs` (the `_backfill_reforms` idiom); a world without the block is **unarmed** (payload None, rows hidden — the bare flag world and the tutorial). `to_dict` / `from_dict` with `.get`, `SAVE_FORMAT_REFERENCE.md`, `MODDING_FORMAT.md`, the validator, and `tests/test_serialization_enforcement.py`. Completion is pinned on the store, never on the event log (capped at 500).
- **Lapse.** A latched design that stops holding reads "lapsed": its one-shot reward stays paid, its live-gated reward switches off, and its road's triumph waits until it is restored (Road III's seal excepted, above).

---

## §4 THE DECISIVE PEACE

- **Rule.** `imperial_designs.tick`, called from `game_end.process_end_of_turn` after the Congress tick and before the Verdict — the only place the cause is stamped — stamps at the first end turn where:
  1. a road is proclaimed;
  2. both its designs are latched;
  3. the construction holds now (Road III: the seal's member test);
  4. the sealing court is at neither WAR nor ARMISTICE with the owner, or is gone, or is the owner's vassal;
  5. Paris is held, the Emperor is free, France is no vassal, no Fall clock runs, and no Humbled Peace has been stamped (a humbled reign cannot claim the decisive peace);
  6. no province of France's 28 opening provinces is held by the sealing court's bloc or by a court at war with France.
- **The stamp.** `record_ending(world, "victory", CAUSE_DECISIVE_PEACE, detail={route, court, manner, treaty, designs, turn})`, once per campaign.
- **Register (A4).** `decisive_peace`, titled THE DECISIVE PEACE, the fifth `REGISTER_STYLE` in `campaign_end.gd` with "Continue the reign"; `_cause_line` names the treaty — "the Peace of Pressburg" (Austria), "the Peace of Tilsit" (Prussia), "the Peace of the Continent" (Britain) — with its manner. A register the client does not know falls back to the Verdict's parchment, so the client lands with it (§9 Part 3).
- **Reward.** Alarm −15, floored at `ARMED_PEACE_WATCH` (45), source `decisive_peace` (with its ledger label); the Verdict +2.
- **Beside the Congress and the Verdict.** Lead order on the end turn (`_attach_endings`): terminal, then imperial_peace, then decisive_peace, then the last stamped. The Verdict reads the +2 as a score term (A2): a status-quo reign with the decisive peace reads ascendant when no negative term (a lost satellite, a great power at war) pulls it down — Part 3 stages that board and says so; the Imperial Peace keeps its exclusive floor of 2; `_tier_lines` gains a "decisive" branch so the copy stops saying "unbeaten at the table". VP-1 grants no Congress term; a sealing cession already latches "beaten" or "capital" where the Congress's own rule reads it.
- **Not trivially reachable.** Never by the turn 9–14 status-quo league peace, Britain's turn-8 suit, an indemnity, an ally's peace, or VOLTE's turn-30 board (Austria holding French soil fails guard 6). The earliest predicted stamp (marengo, turn 14–15) is ruled intended — a counterfactual peace, and the Congress still waits after it.
- **The Moniteur.** The stamp lands in the end-turn tail, after the paper went to press inside the advance — so "THE PEACE OF <TREATY>" runs in the **next** issue, as the Congress's stamp does (`gazette.py:359-366`), deduped on `decisive_peace:<turn>`; pinned.

---

## §5 The absorbed ideas

**WO-D4(b) — yes, as Road III.** Dominance is measured as Britain shut out of the Continent, never as France's hoard; WO-EVAL's three missing pieces answered — the share (ports of 26), the stock (the hold counter), the opposition hook (closure cuts Britain's income ×max(0.4, 1 − closure), which shrinks her paymaster tiers). G2, EAD-2 and ES-4 stand. Rejected: a hoard or income-share win; gold in `power_score` (would reverse G2); Trianon licence income (ES-4); the Milan Decree's floor cut (inert at closure ≤ 60%, and the arms peak near 61%); a peacetime road into the System (an unasked mechanic).

**SF-ECON-1 — absorbed as the Acts of the Empire.** One verb, `decree_act {act}` (its own head, "decree the …"; "enact the <act>" resolves to the act before the laws, golden-corpus pinned, so it never answers "no such law"); full recipe; not in `objection_actions` (a purchase). Each act is one-shot, costs gold + 1 administrative action, has one refusal predicate and one price function (shown = applied; quoted net through `charges_relief`). Effects from a closed set {relation, client_loyalty, authority}; alarm through `add_threat(…, "acts_of_the_empire")`. Refused before its road is proclaimed, on a forsworn road, once enacted, or without its board-won precondition. Never income, never war score, never completes a design alone. The Acts are a diplomatic act where they move relations, so they too live on the road page (typed redirected).

| Act | Road | Price | Effect |
|---|---|---|---|
| The Temple of Glory (decree of Posen, 2 December 1806) | any | 8,000 | authority +15 |
| The Princes' Dotations | I | 6,000 | alarm +3; France–Hesse and France–Saxony +20; members already vassals +15 loyalty |
| The Abolition of Feudalism (2 August 1806) | II | 6,000 | alarm +3; Naples +25 loyalty, only while Naples is France's vassal |
| The Raft on the Niemen (25 June 1807) | III | 6,000 | alarm +3; +20 relation with a great power at war with France, only once France holds a province of hers or her war score against France is ≤ −25 |

A road's two acts cost 14,000 — a **peace-road** sink (the chest's +19,000–28,000 over turns 15–30 on the austerlitz and marengo arms, beside the 15,500 law deck); on the historical war road the chest cannot pay them, and the counsel never offers what it cannot pay. The dispatch's `peace_sink` line names the next act once the laws are bought (`TestDDBR7` re-seated). Rejected: income acts (ES-4), a forced loan, halving the crown term (EAD-2), a stored progress stock, three identical monuments, "the existing verbs are the sink" (DD-B found them none).

---

## §6 The surfaces (never a typed diplomatic order)

One payload, `imperial_designs.build_designs_payload(world)` — ints only, None on an unarmed world, cached per turn **and invalidated** by `proclaim_design`, `decree_act` and every `note_terms` write (the `invalidate_active_nations_cache` pattern; pinned: a proclaim then a GET in the same turn shows the road proclaimed). It reads only named courts, named provinces, the fleet records and the 28 opening provinces (GR8). No surface recomputes it.

1. **The Cabinet (F1).** Step 1: a row after `_add_congress_row` ("The Emperor's Designs — no road proclaimed / Road I: 2 of 3 …"). A new wizard step (the next free id after 3 = formables) — **the road page**, served by GET `/imperial_designs`: the three roads with their designs, gates and teeth, the Proclaim buttons and confirm, the Decree rows, and deep links to the controls each hint names (Propose Vassal, Propose Open Borders, Ultimatum, the table's guided rows, the War Purpose card, Invest).
2. **The Diplomatic Ledger, Balance of Europe.** A "THE EMPEROR'S DESIGNS" block after `headline_case`; the France mirror gains a road line; the tab's title matches every pointer to it (VP1-X6).
3. **The morning dispatch.** `designs_clock` beside `congress_clock` (both renderers), printed once a road is proclaimed — and before it, on the first morning, one TODAY door to the road page so the roads are discoverable on turn 1. Event classes `design_proclaimed`, `design_fulfilled`, `decisive_peace` and the prologue beat; a `realm_designs` front-page class; every weight tie-free in the census.
4. **Le Moniteur.** The proclamation and fulfilment specials and "THE PEACE OF <TREATY>", each with its `_SPECIAL_WEIGHTS` row.
5. **The table, the bilateral preview, the incoming-proposal popup** — the Revanche line and the manner line (VP1-X7).
6. **The desk and first contact.** "How do I win" / "what is the goal" leads with condition (c), then names the door (Cabinet F1 → the road page), then the proclaimed road with its two designs' progress and the next act — or, before any proclamation, the three roads and that the choice cannot be undone — then the decisive peace beside the Congress, the Verdict and the Fall (`tests/test_first_contact_keyless.py`). A "designs" help kind answers each design ✓ / ✗. **Talleyrand's counsel** names the road page's control and reads the road and the manner (ruling K: a reading, not a lookup).
7. **The Admiralty** prints "N of 26" (VP1-X5). **The end screen** — the fifth register (§4).

New threat sources carry ledger labels (`act_of_confederation`, `schonbrunn`, `blockade`, `acts_of_the_empire`, `decisive_peace`) — an unlabelled source prints its raw key (`combat_executor.py:5693`).

---

## §7 AI symmetry and the series

- **No AI code reads the store.** The predicates are nation-parameterized and keyed on the store's authored owner; the roads are player content — an asymmetry of **content** (as the minors have no laws), not of code. VP1-X9 adds the player guard `intent._derive_intent`'s docstring already claims (byte-identical).
- **`BASELINE_SERIES` dormant by construction, proven by measurement.** The ambient France never proclaims, and the series runner ends its turns at the turn manager. `tools/_vp1_series_arms.py` holds each seam that could reach AI-read state down and up and **counts its reach**: the store and the rewards; VP1-X1 (the bilateral cession), X2 (the dictated exit through `note_ratification` — it runs on every armistice pair, AI–AI included), X3 (the beaten latch), the suspended drift (A3) and `CS_ORDER_DECAY`. Any non-zero reach is attributed and re-pinned as `SERIES_BEFORE_VP1`, naming "VP-1 (S14b)".
- **The archived arms** (CMD-A / H / M, DL, FLD, LAW, OP, VOLTE) re-run each part with every AI-read field byte-identical; the new store field and the digest text (the goal answer, the TODAY door, the prologue beat) attributed by `tools/_vp1_arm_attribution.py`.
- **Untouched pins:** `test_nation_agendas.py` (France deckless), `test_ai_intent_emergent_designs.py:160-165`, `test_ai_intent_system_wiring.py:280-297`, the historical envelope.
- **Re-seated consciously, named in each part's commit:** `test_ge2_the_client.py`, `test_ge3_the_client.py` (four registers → five; the IQ-10 shots); `test_ge1_the_verdict_and_the_fall.py`, `test_ge1_review_round.py`, `test_ge1_verification_round.py` (the tier lines and the +2); `test_first_contact_keyless.py` (the goal answer); `test_wo_slice7_cabinet_door.py` (the door's drift mirror); `test_cx_r1_the_unbound_name_spends_nothing.py` and `tests/data/parser_golden_corpus.json` (both verbs); the `CAMPAIGN_LOG_TYPES`, `HEADLINE_WEIGHTS` and gazette weight censuses; `test_ddb_s13b_the_rulings.py::TestDDBR7`; the validator pins.

---

## §8 Numbers (in-band tunables, all ints)

| Tunable | Value | Band |
|---|---|---|
| Proclamation alarm / DP / admin actions | 8 / 2 / 1 | 5–10 / 1–3 / 1 |
| Proclamation relation blows | −10 (System −15) | −5 to −20 |
| Rhine fulfilment blow / alarm | −30 / +10 | −15 to −30 / 5–15 |
| Clients needed / hold | 3 of 4 / 4 turns | 2–4 / 3–6 |
| Ports needed | 13 | derived from the Congress line; never tuned |
| Port hold K | 6 | 4–8 (reported per seed, never moved to fit an arm) |
| Member loyalty line | 40 (`SATELLITE_TITLE_LOYALTY`) | 40–50 |
| Naples authority | +15 | 10–20 |
| `CS_ORDER_DECAY` / the System's resentment | 2 / −10 | 1–3 / −5 to −15 |
| Decisive peace alarm (floor) / Verdict | −15 (45) / +2 | 10–20 / 1–2 |
| Act prices / act alarm | 6,000–8,000 / 3 | 5,000–10,000 / 0–5 |

---

## §9 The build — three parts, each about one session, each landing green

**Part 1 — the substrate, unarmed** (no player road exists yet, so nothing typed-only can ship)
- *Head (reproduce first):* the §2 "reproduce first" facts on today's tree; the Tilsit road re-run on three seeds (Britain's bond has bound Austria from turn 10 since the archive) with the Blockade's latch reported at K = 6; VP1-X1, X2, X3 reproduced on boards.
- *Scope:* `backend/game_logic/imperial_designs.py` (the store, the six predicates, the holds and latches, `note_terms` at `note_ratification`, `maybe_fire_volte_face` and the dictated exit, broken beside `note_war_entry`, the tick in `process_end_of_turn` with the triumph's rule computed but its stamp seam held off until Part 3); the `imperial_designs` block authored in a **staged test scenario only** (the shipped `europe_1805.json` gains it in Part 2); `_validate_imperial_designs`; serialization and the backfill; the three reward seams; VP1-X1, X2, X3, X9; the series levers.
- *Done when* (`tests/test_vp1_the_emperors_designs.py`): on a staged armed world the boot readings are Rhine 0 / 3, Iron Crown 2 / 3, System 10 / 26; each predicate latches on its staged board and lapses when broken; a Pressburg before the proclamation seals after it; the reward seams apply only while held (the drift, the decay) and the one-shot authority pays once across a save and load; the shipped boot is **unarmed** (no row, no payload); the deckless pins pass unedited; X1–X3 pinned red then green; `BASELINE_SERIES` byte-identical on every lever with the reach counted; the full suite green through the hook.

**Part 2 — the road armed on the existing screens**
- *Scope:* the shipped scenario's `imperial_designs` block (`MODDING_FORMAT.md`); `proclaim_design` (recipe, redirect, door pin) and the Cabinet road page with its confirm; the Balance block, `designs_clock`, the TODAY door, the desk / first-contact answer, the counsel, the manner line on the three surfaces, the Admiralty count; VP1-X4 … X7, X10.
- *Done when:* each of the six designs fulfils on a staged board **through real clicks** (the button's command is the executor's; every disabled reason is the executor's refusal); a second proclamation is refused with its reason; a forsworn design never fulfils; the VOLTE board fails guard 6; a drift pin shows every surface carries the payload's one slice; a census finds no line that tells the player to type a diplomatic order; the Godot parse harness EXIT 0; the IQ-10 frames of the road page at Interface Scale 1.0 and 2.0 show every button above the fold.

**Part 3 — the Acts, the decisive peace and the arms**
- *Scope:* `decree_act` and the four acts; `CAUSE_DECISIVE_PEACE` stamped (the seam released), the register (`campaign_end.gd`), `_cause_line`, the summary block, the Verdict term and tier lines, the lead order, the dispatch and Moniteur rows, the condition (c) copy (ROADMAP's store-page row marked met; A6 written into ROADMAP row 13). **VP1-CS:** a new script `tools/playtest_scripts/sf_vp1_cs.json` copied from the Tilsit road (the NAV1T archive reproduces unchanged), extended to 40 loops, proclaiming Road III on turn 1 with the command the Cabinet button sends, and a new driver dial `--decline-until-latch <court>` (absent by default — every archived arm byte-identical — pinned) that declines the court's offers until the Blockade latches, then accepts the first qualifying one. **VP1-RH** (the Rhine) and **VP1-TH** (the Crowns) run beside it, reported per seed, not gated.
- *Done when:* the decisive peace records on at least one benchmark seed, every seed reported with its reason (seeded paths, not laws); the negative boards never stamp; the end card raises and the next end turn still reads `game_over` False; a staged turn-44 board with no negative term reads ascendant with the decisive peace and contested without it; each act charges exactly its quote and refuses the second time; the Godot parse harness EXIT 0 and the IQ-10 frames of the fifth register at 1.0 and 2.0; the series byte-identical or re-pinned with VP-1 named; condition (c) reads met; the census reads 0 open VP1 rows.

---

## §10 Risks, re-open conditions, siblings

**Risks and re-open conditions**
- **No road is measured to complete on today's tree.** Road III was, on the October 4 archive (the Tilsit road latched K = 6 on turns 16 / 16 / 13); part 1's head re-ran it and it no longer does (§12.1). No played arm has reached a partition Pressburg or a clean volte-face (France's war score against Austria runs +8 to −7 on the archives). The record and the store copy say so; VP1-RH carries the done-when, and VP1-CS and VP1-TH report per seed.
- **Road III has no margin.** Spain's exit and the coalition pulling members back can unlatch it — reported per seed.
- **The Rhine road may be too easy** (Bavaria's vassalage is cheap on turn 1). If it latches before turn 10 on every seed, the need rises to 4 of 4 or the hold to 6, in band.
- **The Rhine road can open the Congress.** A satellite at loyalty ≥ 40 titles its homeland (`province_title_kind`): with Bavaria (3), Hesse (2) and Hanover (6) the bloc reaches 46 against `hold_titled` 45. That is a real interplay, not a defect — the Confederation was the Empire's bid for recognition — measured on VP1-RH, and its alarm against the Congress's hold ceiling (80) reported per arm.
- **The arm may not complete.** If no seed latches at K = 6, VP1-RH becomes the done-when arm, and the record says so. **Fired (§12.1):** the Tilsit road latches on no seed today; VP1-RH is the done-when arm.
- **Re-open:** a France deck in `world.agendas` only if S14e finds Europe blind to France's road; a larger act deck only if S14e sees DDB-D7's idle chest again.

**Siblings (Rule 10)** — filed in `BUG_FIXES.md` §VP1 with this record; each reproduced on a board before it is built.

| Row | Finding | Fix | Part |
|---|---|---|---|
| VP1-X1 | The bilateral ratifier skips a cession of a province France already occupies (`world_state.py:13171-13179`), so the partition record misses it. | Record it at the seam, behind its own series lever. | 1 |
| VP1-X2 | The dictated exit (`diplomacy.py:12077-12109`) bypasses `note_ratification`. | Route it through the hook (it latches as signed, PC-R2), its own lever; the docstring at `congress.py:2527` corrected. | 1 |
| VP1-X3 | The Congress's beaten latch reads `term["to"] == player` (`game_end.py:2001`) while its own comment says "ceded to the Emperor's bloc". | Read the bloc (`_top_overlord`), its own lever. | 1 |
| VP1-X4 | `_answer_closure` reads the literal "Britain", calls closure a share of trade, and inverts the posture rule. | Correct the copy on the derived court. | 2 |
| VP1-X5 | The Admiralty prints the closure as a percentage only. | Add "N of 26". | 2 |
| VP1-X6 | The ledger tab reads "THREAT & COALITION" (`diplomatic_ledger.tscn:87`) while every pointer says Balance of Europe. | One title. | 2 |
| VP1-X7 | The Revanche line rides only the settlement preview, the ratify result and the counsel — not the bilateral preview or the incoming-proposal payload, and no `.gd` renders it. | Build it on both payloads and render it with the manner line. | 2 |
| VP1-X8 | "Summon the Congress ('summon the congress', or the Cabinet, F1)" — first contact quotes a typed diplomatic command (`first_contact.py:282-288`), and the door does not claim "summon". | Drop the typed form from the copy; claim the head in the funnel and the door's mirror. | 2 |
| VP1-X9 | `intent._derive_intent` has no player gate despite its docstring. | Add the guard (byte-identical). | 1 |
| VP1-X10 | GR5 "Britain" literals in `SPECIAL_BONUSES` and `continental_system_losses`. | Read the derived trade-dominance court. | 2 |

---

## §11 Deferrals and hand-offs (Rule 9)

| Item | Owner / landing | Completion | Test | STATUS line |
|---|---|---|---|---|
| The land roads' played reach (Rhine, Crowns) | this row, Part 3 | VP1-RH and VP1-TH reported per seed; any seal unreached stated on its design's row of this record | `tests/test_vp1_the_decisive_peace.py` (an archived-digest pin) | "S14b part 3 — VP-1's arms" |
| HC-D1, NP-D7, NPC-D2, the Napoleon Comparison, the seed display | VP-2 (ROADMAP row 13, after the deploy) | their existing done-whens | their existing rows | unchanged |
| WO-D4(b), SF-ECON-1, the EAD-2 residue | this row, Part 3 | closed against this record (§5) | `tests/test_vp1_the_decisive_peace.py` | "VP-1 landed" |
| S14c's events deck (the Confederation of the Rhine, the end of the Holy Roman Empire, the Berlin Decree, Tilsit) | S14c (`PRE_DEPLOY_PLAN.md` §2) — a hand-off line written into its row with this record | an event on one of these moments reads `world.imperial_designs`, never fires on a forsworn road, never doubles a proclamation | S14c's own pins | S14c's row |

**Struck from every surface, not deferred:** Westphalia, a Bonaparte Naples, Rome 1809, a peacetime road into the System, Trianon licences, the Milan Decree's cut, an AI reading of France's road, a France deck in `world.agendas`.

---

## §12 Part 1 landing record — the substrate, unarmed (October 22, 2026)

*Built on master after `6bc0564e`; rows `BUG_FIXES.md` §VP1 (X1, X2, X3, X9 FIXED; X11, X12 found and FIXED; X13 found and OPEN at part 2's head); rules `SYSTEMS_REFERENCE.md` §143; pins `tests/test_vp1_the_emperors_designs.py`; the authored block `tests/fixtures/vp1_imperial_designs_block.json` (the shipped scenario carries none until part 2); the instruments `tools/_vp1_series_arms.py` and `tools/_vp1_arm_attribution.py` (`_final.json` each).*

### 12.1 The head — reproduced first

- **The §2 facts hold on today's tree.** Rhine 0 of 3 (Bavaria allied, Hesse, Saxony and Hanover at peace and free); Iron Crown 2 of 3 (Milan and Piedmont titled as the Kingdom of Italy's homeland, Carniola Austria's); the System 10 of 26 against a derived line of 13 (France 4, Spain 3, Holland 2, the Kingdom of Italy 1 — as a satellite of a lord at war); all three road gates open at boot; with Bavaria, Hesse and Hanover as satellites the bloc titles 46 against the Congress's 45 (§10's interplay, as recorded).
- **The Tilsit road does not latch the Blockade at K = 6 on any seed.** The NAV1T arms on the archive's own argv (`sf_nav1_tilsit_road.json`, 30 turns, decline-from Britain, Portugal, the Papal States, Naples, Austria, Russia; mock LLM, `PYTHONHASHSEED=0`) peak at 15 / 14 / 15 of 26 (historical / austerlitz / marengo); the longest run at 13 or more is **3 / 4 / 3 end turns**. The ports leave on the same beats on every seed: Spain's exit −3 at end turn 15 (Britain and Spain sign); on historical Russia and Austria, enrolled at turns 12–13, leave together at end turn 20 when the Fourth Coalition forms (marengo: Austria at 17, Russia at 20; austerlitz: Russia never enrolls — it countered, and the decline-from policy refused). Britain's bond binds Austria from turn 4 on every seed and Russia from turn 9 (10 on austerlitz); both renege into the coalition. The October 4 archive's latch (turns 16 / 16 / 13) does not reproduce. **Ruled by the record's own condition (§10):** K stays 6 — never moved to fit an arm — and VP1-RH carries part 3's done-when; VP1-CS is built and reported per seed beside it.
- **VP1-X1** reproduced only partly (the title, the gained list and the Revanche's reconciliation read the signed terms and saw the held cession; the punitive record alone missed it); **X2** and **X3** reproduced on boards. Each is recorded on its row.
- **One new find, VP1-X12**: turn 1's Cabinet withheld the counter the advance makes (no AI purse is written before the first regen). Fixed here; its sweep filed **VP1-X13** (the AI courts open with empty purses while France opens with her regen) at part 2's head.

### 12.2 Built

- **`backend/game_logic/imperial_designs.py`** — the store `world.imperial_designs = {block, state}` (`fresh_state`, `from_block`, `store_from_data`: one shape for the scenario key and the save), the closed sets (three roads, six design types, three gate types, the manners `subjugation` › `partition` › `moderate`), the §8 tunables as named ints; the six predicates (`design_reading`: `client_rows`, `ports_reading` derived from `cs_shutout_pct`, `province_title_kind`, `terms_met`), the gate (`gate_met`), the branch (`proclaim_refusal` — the one predicate the part-2 executor, the road page and the counsel ask; `proclaim` writes once and applies the teeth); the terms latch (`note_ratification`: the manner read off the treaty's own terms with ruling J's netting — `compensation_offsets` / `net_of_compensation` exactly as the Revanche line nets it — written before any proclamation, so a Pressburg signed first seals the road proclaimed after it; `note_war` breaks it); the tick (`tick`: holds run only on the proclaimed road, latch, lapse, the one-shot reward through the `rewarded` latch); the live-gated rewards (`drift_suspended`, `order_decay`); THE DECISIVE PEACE's rule (`decisive_peace_reading`, the six conditions named) with its stamp seam `decisive_peace_released()` returning False until part 3; the payload (`build_designs_payload` — ints, None unarmed, built on every read: a handful of courts, three provinces and the port list, no region scan).
- **The hooks:** `game_end.note_ratification` (the one chokepoint both ratifiers and now the armistice's exits pass) → the terms latch; `diplomacy.set_diplomatic_state` (beside `note_war_entry`) → `note_war`; `game_end.process_end_of_turn` (after the Congress, before the Verdict) → `tick`; `vassal.autonomy_drift` (the tick's and the forecast's one drift reading) → the shield; `coalition._calculate_threat_decay` → the order; `diplomatic_templates.continental_system_lift_offered` → off for the proclaimed System's life.
- **Content and persistence:** `_validate_imperial_designs` (the closed sets, the courts against the roster, the provinces against the registry, one construction and one seal per road); `WorldState.imperial_designs` serialized, read by `store_from_data`; `save_manager._backfill_imperial_designs` (the `_backfill_reforms` idiom — the 1805 campaign only, a carried store never overwritten).
- **The siblings:** VP1-X1 (`RatifyTreatyContext._held_cessions`, the seam `emergent_designs.held_cessions_are_punitive`), X2 (`game_end.note_armistice_exit`), X3 and X11 (`game_end.receiver_in_bloc`), X9 (the guard in `intent._derive_intent`), X12 (`diplomacy.regen_dp_for`).

### 12.3 Measured

- **`BASELINE_SERIES` byte-identical** on every arm — none, the store (D), X1, X2, X3, X12 and all down together — with every reach counted and **zero**: the shipped boot is unarmed, so no read finds an armed store, and the ambient sim signs no held cession, no cession to a vassal, no armistice exit and builds no dry-run counter before a purse is written (`tools/_vp1_series_arms_final.json`).
- **The eight commanded arms** (CMD-H, CMD-A, CMD-M, OP, FLD, DL, LAW, VOLTE) re-run on the part's tree: every digest record equal to the S14b head's archive `docs/audits/score_runs/2026_10_21_rr6x3/` but the run's own stamps (`tools/_vp1_arm_attribution_final.json`).
- **Untouched pins pass unedited:** `test_nation_agendas.py` (France deckless), `test_ai_intent_emergent_designs.py`, `test_ai_intent_system_wiring.py`, the historical envelope.

### 12.4 The done-when (§9 Part 1), item by item

| Item | Pin |
|---|---|
| boot readings Rhine 0 / 3, Iron Crown 2 / 3, System 10 / 26 | `TestTheStore::test_the_boot_readings` |
| each predicate latches on its staged board and lapses when broken | `TestThePredicates` (the Confederation on its fourth end turn, Naples, the Blockade on its sixth, the partition, subjugation, the moderate peace and its window, the Iron Crown, Britain's signature and the lift clause) |
| a Pressburg before the proclamation seals after it | `test_a_partition_before_the_proclamation_seals_after_it` |
| the reward seams apply only while held; the one-shot pays once across a save and load | `test_the_confederation_latches_on_its_fourth_end_turn_and_shields`, `test_the_blockade_latches_on_its_sixth_end_turn_and_orders_the_continent`, `test_the_throne_of_naples_pays_its_authority_once` |
| the shipped boot is unarmed | `test_the_shipped_boot_is_unarmed`; a pre-VP-1 save armed by its scenario, never overwritten: `test_a_pre_vp1_save_is_armed_by_its_scenario_and_never_overwritten` |
| the deckless pins pass unedited | §12.3 |
| X1–X3 pinned red (seam down) then green | `TestVP1X1…`, `TestVP1X2…`, `TestVP1X2OnThePcR2Board`, `TestVP1X3…` |
| `BASELINE_SERIES` byte-identical with the reach counted | §12.3 |
| THE DECISIVE PEACE's rule computed, the stamp held | `TestTheDecisivePeaceRule` |
| the full suite green through the hook | the part's commit |

### 12.5 Carried into their specs (the amendments this part lands)

- **A1** — `NATION_AGENDAS_SPEC.md` §9's player-France row: France's goals live in `world.imperial_designs`, never `world.agendas`.
- **A3** — `VASSAL_DEEPENING_SPEC.md` §2.3: the Protector's shield suspends a member's downward `AUTONOMY_DRIFT` term (the grip term untouched).
- **A5** — `NATION_AGENDAS_SPEC.md` §9's seed note: no design pays gold.
- A2, A4 (the Verdict's term, the fifth register) and A6 (ROADMAP row 13) land with part 3.
