# The full re-score — FA slice 17, Phase 3 (September 11, 2026)

> Report of record for the FA audit's third phase: every pillar played and
> re-scored against the August 16, 2026 baseline. The scoring runs were taken
> on master `1ae82476` (Phase 1 = all 38 defect rows + a review round,
> `e6c9880b`; Phase 2a = fifteen legibility rulings, `8b91c06e`; Phase 2b =
> the seven mechanics rulings, `ea97ec0e`; Phase 3 part 1 = the playtest's own
> fixes, `1ae82476`). Instrument = the committed driver
> `tools/playtest_driver.py` (Mode A, in-process, `PYTHONHASHSEED=0`, the
> turn-boundary reseed), plus one live-parser arm and a Mode C client pass on
> port 8006. **⚠ Four of the defects scored below were FIXED after the scoring
> runs (Phase 3 part 2, §4b) — the pillars they drag are expected to move on
> the next pass, and this memo does not pre-credit them.**

## 0. What ran

| arm | instrument | runs | turns | what it answers |
|---|---|---|---|---|
| ambient | no orders, decline everything | 5 seeds (historical, ulm, austerlitz, jena, marengo) | 40 | the AI alone; the FA-D27 passive board |
| accept | no orders, `--diplomacy accept` | 3 seeds | 40 | the coalition's offer answered |
| propose | no orders, `--diplomacy propose` | 3 seeds | 40 | France sues |
| tyrant | `weird_tyrant.json` (all-out attack, plunder, insist, rentes granted and revoked) | 3 seeds | 40 | marshal abuse; the jealousy spiral |
| emperor | `np_campaign_emperor.json` (the Emperor at the front) | 3 seeds | 40 | the Peril |
| emperor-accept / tyrant-accept | the two scripts WITH `--diplomacy accept` | 5 seeds each | 40 | **the FA-D27 re-open condition's own arm** — a France that fights AND answers |
| naval | `naval_descent.json` on the marshalate road | 1 | 24 | the Descent, Trafalgar, the expedition |
| tutorial | `tutorial_lesson.json`, scenario `tutorial` | 1 | 14 | the School end to end |
| t10 / t20 | `--from-save` fixtures | 1 each | 20 | mid-campaign and late-war shapes |
| reload | `--reload-every 5` | 1 | 20 | FA-102: save/load at the boundary |
| anthropic | `flagship_1805.json` on the LIVE parser | 1 | 20 | the live parser (one escalation in 59 commands) |
| Mode C | Godot on `SOVEREIGN_PORT=8006`, its own `INK_IRON_SAVE_DIR` | 4 screenshots | — | the Phase-2 surfaces on screen |

**34 driver runs, 34 `completed`, 0 `blocked`, 0 unknown blockers, 0 script
preconditions.** (The first pass over the Phase-2 tree BLOCKED one run —
tyrant/austerlitz at world turn 7 — which is FA-S17-3 in §4a.) 447 battles
and 680 dispatch headlines over 680 driven turns in the five D27 arms alone.

Levers measured for FA-D27 option (b): France's starting treasury 800 → 2,000
on the ten fighting-and-answering runs; France's base actions 4 → 5 (inert BY
CONSTRUCTION — the player's AP is the hardcoded 4 of
`WorldState.calculate_max_actions`, and the scripts never spend a fourth
action: "N action(s) unused" on every turn of every run).

## 1. The board (`Fr@N` = French provinces after N end-turns; boot = 28)

### 1.1 The FA-D27 five arms, every Phase-2 lever up (`p3_d27_runs_final`)

| run | Fr@10 | Fr@20 | Fr@30 | Fr@40 | threat (last 6) | Paris | Napoleon | battles |
|---|---|---|---|---|---|---|---|---|
| ambient-historical | 28 | 24 | 7 | **4** | 6 3 2 1 0 0 | held | free | 24 |
| ambient-ulm | 28 | 26 | 26 | **22** | 55 54 53 50 47 44 | held | free (105 men) | 44 |
| ambient-austerlitz | 27 | 14 | 14 | **18** | 45 44 43 42 41 38 | held | free | 21 |
| ambient-jena | 28 | 17 | 8 | **8** | 17 14 11 8 7 6 | held | free | 27 |
| ambient-marengo | 29 | 25 | 2 | **1** | 9 6 3 2 1 0 | held | **captured (Austria)** | 34 |
| accept-historical | 28 | 27 | 27 | **27** | 34 32 30 28 26 24 | held | free | 16 |
| accept-ulm | 28 | 27 | 27 | **27** | 35 33 31 29 27 25 | held | free | 10 |
| accept-austerlitz | 28 | 27 | 27 | **27** | 23 21 19 17 15 13 | held | free | 8 |
| propose-historical | 28 | 26 | 26 | **26** | 34 32 30 28 26 24 | held | free | 17 |
| propose-ulm | 28 | 27 | 27 | **27** | 30 28 26 24 22 20 | held | free | 6 |
| propose-austerlitz | 28 | 27 | 27 | **27** | 61 59 59 59 59 59 | held | free | 16 |
| tyrant-historical | 28 | 28 | 14 | **4** | 46 33 30 27 26 25 | held | free | 50 |
| tyrant-ulm | 27 | 17 | 7 | **5** | 19 18 17 16 13 10 | held | free | 25 |
| tyrant-austerlitz | 11 | 3 | 2 | **1** | 7 4 1 0 0 0 | held | **captured (Britain)** | 36 |
| emperor-historical | 22 | 12 | 4 | **2** | 5 2 0 0 0 0 | held | **captured (Russia)** | 43 |
| emperor-ulm | 29 | 28 | 19 | **12** | 49 48 45 44 43 42 | held | free (454 men) | 33 |
| emperor-austerlitz | 28 | 18 | 10 | **6** | 46 45 34 31 28 25 | held | free | 37 |

Seed means at turn 40: ambient **10.6** (Phase-1 memo, Phase-1 tree: 12.8;
the slice-4 review's "after" tree: 2.2), accept **27.0** (27.7), propose
**26.7** (28.0), tyrant **3.3** (7.7), emperor **6.7** (21.7). Paris held on
17 of 17.

**The Emperor is captured on 3 of 17 here** — ambient-marengo (Austria),
tyrant-austerlitz (Britain), emperor-historical (Russia) — and on no other
run (**3 of 31 runs with a final autosave**, read from `Napoleon.captured_by`
in each run's last save, NOT from the digest: the run summariser's "Napoleon
captured" column matched *"Napoleon's army … Franconia has been captured by
Austria"* and over-counted it as six — an instrument artefact, recorded in
§6). One of the three is the PASSIVE marengo board, where he was never
ordered anywhere. Where he is not captured he is often a rump: 105 men
(ambient-ulm), 81 (emperor-austerlitz), 73 (tyrant-accept-austerlitz), 161
(tyrant-historical) — the Guard's escape toll paid over and over.

### 1.2 The re-open condition's own arm — a France that fights AND answers

| run | Fr@10 | Fr@20 | Fr@30 | Fr@40 | Paris | battles |
|---|---|---|---|---|---|---|
| emperor-accept-historical | 28 | 28 | 24 | **19** | held | 21 |
| emperor-accept-ulm | 28 | 27 | 27 | **26** | held | 22 |
| emperor-accept-austerlitz | 28 | 25 | 22 | **18** | held | 19 |
| emperor-accept-jena | 28 | 26 | 25 | **22** | held | 34 |
| emperor-accept-marengo | 28 | 25 | 24 | **21** | held | 22 |
| tyrant-accept-historical | 27 | 24 | 24 | **19** | held | 38 |
| tyrant-accept-ulm | 27 | 18 | 15 | **13** | held | 27 |
| tyrant-accept-austerlitz | 22 | 11 | 10 | **10** | held | 28 |
| tyrant-accept-jena | 25 | 14 | 8 | **8** | held | 37 |
| tyrant-accept-marengo | 29 | 26 | 25 | **25** | held | 30 |

emperor-accept: below 20 on **2 of 5** seeds (18, 19); tyrant-accept: below
20 on **4 of 5** (19, 13, 10, 8). Every run signed the coalition's settlement
(the five emperor runs at turn 4, the tyrant runs at 4, 4, 8, 13 and 19) and
fought on after Britain re-declared. ⚠ The Phase-3 fleet's balance lens
qualified this arm and the qualification is carried: the driver answers
`force_declare_war_confirmation` with its first option, so the script's next
attack line on a court France has just signed with RE-DECLARES that war — on
9 of 10 played runs — and the scripts spend only 9–22 of 160 AP over 40
turns. **The arm that trips the condition is a France breaking its own
peace, not a France being beaten while playing well.**

### 1.3 The other arms

| run | turns | Fr@end | Paris | battles | note |
|---|---|---|---|---|---|
| p3-tutorial | 14 | 26 | held | 13 | SCHOOL steps 6 → 15 "The Lesson Ends" reached |
| p3-naval | 24 | 14 | held | 39 | Diversion fired → **TRAFALGAR** (23 sail lost); Oudinot commissioned, marched, LANDED at Munster |
| p3-t10 | 20 | 7 | held | 26 | the mid-campaign passive France collapses |
| p3-t20 | 20 | 4 | held | 3 | the late-war rump |
| p3-reload | 20 | 24 | held | 22 | four reloads, "re-raised on load: nothing" each time |
| p3-anthropic | 20 | 31 | held | 33 | 59 commands, ONE live escalation: the literal ASK |

## 2. Pillar scores

Method: eight pillars were scored by an adversarial review fleet (one lens
finder each, two refuters per defect); four — combat legibility, narration,
AI aliveness, naval — were scored by hand from the same digests after the
fleet exhausted its budget, and are marked ‡. Every score cites evidence.

| Pillar | Aug 16 | **Now** | Δ | Why |
|---|---|---|---|---|
| Command & parsing | 6.5 | **7.5** | ▲ | ~1,500 typed commands, 0 unknown blockers; the NPC-1 printed-spelling family and NPC-7's prisoner refusals are gone (tyrant-historical T2 *"Mack is our prisoner at Paris, Sire — he leads no army"*); refusals name the remedy and the roads (p3-anthropic T2 *"From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais"*). Held below 8 by the pursuit that prints "(at unknown)" and dies next turn, and by one state (a court at peace) answering four different ways |
| Marshal drama | 7.5 | **7.0** | ▼ | Breadth is the best it has been (the crown reads on the dispatch, 68 last-stand asks named the man and the place, the FA-D5 settle arm is live in-client) — but three high-drama beats misfire: the Emperor captured off the field by the Guard toll, Berthier calling the battle that took him *"a skirmish"*, and 7 of 12 jealousy audiences resolving *"The moment has passed"* in the block they arrive |
| Combat legibility ‡ | 7.0 | **7.0** | = | 447 battles; musters quote committed AND potential strength (*"Ney (24,000; 78,676 if all march, up to 96,789 if every corps arrives)"*), reinforcement attribution is specific (*"Where was Ney? Murat held the field alone"*), Materiel lines are signed. Held flat by the two surfaces still disagreeing on the ENEMY attacker's losses — 14 of 14 compared pairs (ambient-jena T3: prose *"Mack's army 1,253"*, record *"Mack (lost 892)"*), CA8-1's family one phase over |
| Narration & briefing ‡ | 6.5 | **7.0** | ▲ | A dispatch headline on all 680 turns, never silent; eight distinct headline classes with named causes; the AI-AI log is alive and legible (49 THE CONGRESS beats, 39 REVANCHE promotions, 365 subsidy rows, 172 sponsorships). Held below 7.5 because 1,032 of ~2,500 log rows are still refusals, and on a collapsing board 121 of 680 headlines are the same fall-of-province class |
| Economy | 6.5 | **6.0** | ▼ | EB-1's Charges of Empire really do bound a warring treasury (ambient-historical 24,194 at t17 → 3,151 at t40); rentes are shown = applied. But **the peace table paid the loser** (P1, §4b: Britain *"Offering 3169 gold"* to a France that had just lost Paris), and peace is a money printer with nothing to buy (65k–113k at t40) |
| Diplomacy & settlement | 6.0 | **6.0** | = | The machinery is the most reliable it has been — the offer arrives, activates, ratifies and dissolves the coalition on all 11 accept/propose runs, FA-D7's greying pins are green, 0 confirm chains in 34 runs — but the outcomes are not yet credible: the victors paid the loser, a court sent a bilateral peace AND a settlement offer for the same war in one turn, and Britain re-declares the instant the 8-turn truce floor expires |
| AI aliveness ‡ | 7.5 | **7.5** | = | Europe acts with purpose: 5–10 actions per enemy phase, 134 province captures across the five ambient runs, third-party peaces and emergent REVANCHE designs firing unprompted, and a passive France beaten on 4 of 5 seeds. FA-D4's boot purpose and FA-S2-D1's one-turn wait are improvements inside a pillar that was already strong, not a new axis |
| Vassals | 6.5 | **6.5** | = | The lifecycle fires organically for the first time (Switzerland rebels on 11 of 17 unattended boards; THE DEFECTION fires four times; Holland's graceful exit is briefed honestly) — but the climax is wrong on every seed it reaches: the "rebellion imminent" question outlives the rebellion (P2, §4b) |
| Naval ‡ | 6.5 | **7.0** | ▲ | The whole arc played end to end in one run for the first time: the blockade closes Austrian and Russian ports, the Grand Diversion fires, **TRAFALGAR** takes 23 sail, the Channel stays SHUT with the ratio quoted (*"97 sail (97 effective) against our 19"*), Britain lands at Lisbon, and a commissioned Oudinot lands at Munster and is thrown back. FA-S17-4 (the committed script could never sail) is fixed |
| UI/UX | 7.0 | **7.5** | ▲ | First score on something a player sees (Aug 16 carried "no visual pass taken"): the redemption audience leads with a priced Settle arm and the receipt states the true cost, the war-detail popup teaches the purpose verb in both states, the fog sentinels render. Three P3/P4 copy items open |
| **Directional** | **≈6.8** | **≈6.9** | ▲ | |

## 3. FA-D27 — the re-open condition fired; option (b) measured; disposition

The ruling's condition: *"if the Phase-3 played campaign (a scripted France
that fights AND answers diplomacy) ends below 20 provinces on 3 or more of 5
seeds at turn 40, or if the PLAYED (human) campaign loses Paris before turn
20 without a refused peace offer on the record, re-open at option (b) — a
France-side lever (starting AP or treasury), never an AI-side nerf."*

**Clause 1 fires on the letter** (tyrant-accept: 4 of 5 below 20) and does
NOT fire on the emperor-accept arm (2 of 5). **Clause 2 never fired** — Paris
held on 34 of 34 runs. Option (b) was then measured on the same ten runs:

- **Starting treasury 800 → 2,000:** the lever LANDED (turn-1 treasury 3,712
  against 2,512) and produced **ten identical outcomes**. Nobody buys what
  the extra gold gates.
- **Starting AP 4 → 5:** inert BY CONSTRUCTION — `EUROPE_BASE_ACTIONS` is
  read by no backend file for the player, `calculate_max_actions` returns
  `int(4 + bonus_actions)`, and the scripted France never spends its fourth
  action on any turn of any run.

**Disposition — ⚠ FOR USER CONFIRMATION:** no blessed number is moved on an
inert measurement. **The ruling stands at (a) with the re-open recorded as
fired-and-measured**, and with two corrections to the condition itself: the
arm that trips it is a France breaking a peace it has just signed (the
driver's own `force_declare_war` answer, 9 of 10 runs), and "treasury" should
be struck from option (b) because it is measurably inert. The France-side
lever can only be judged by a HUMAN campaign that actually spends the extra
AP. Two numbers a human campaign should check first: the passive board's
drift (12.8 → 10.6 provinces, no constant changed) and the Emperor's
captivity (3 of 31 saved runs, once on a passive board).

### 3a. Re-taken on the shipped tree (after the FA-S17-5 fix)

The §3 reading was taken on `1ae82476`, before the P1 that paid the loser was
fixed. The ten played arms were re-run on the shipped tree; the gate's
numbers there are:

| arm | Fr@40, five seeds | below 20 |
|---|---|---|
| emperor-accept | 17, 22, 23, 21, 26 (mean **21.8**, was 21.2) | **1 of 5** (was 2) |
| tyrant-accept | 19, 13, 8, 25, 13 (mean **15.6**, was 15.0) | **4 of 5** (unchanged) |

So the disposition is unchanged and now rests on the shipped board: clause 1
still fires on the tyrant-accept arm and still does not on emperor-accept,
Paris still holds everywhere, and the indemnity direction is right — the same
turn that read *"Britain has offered terms … Offering 3169 gold"* to a France
that had just lost Paris now reads *"Asking 5987 gold"*.

## 4. What Phase 3 fixed

### 4a. Before the scoring runs (`1ae82476`)

- **FA-S17-3 (P1):** `end turn` raised `'NoneType' object has no attribute
  'command_type'` and the turn could not be ended on any retry — tyrant /
  austerlitz, world turn 7: Bernadotte's PURSUE beat Mack, his advance into
  Hungary took the co-located Ney along, the attack-movement cleared Ney's
  fresh MOVE_TO, and pass 1 of `process_strategic_orders` dereferenced the
  None. Fixed with a None check that REPORTS the consumed order; a re-read I
  first added was measured INERT by the sweep and removed.
- **FA-S17-2 (root cause, FIXED):** the School's "process-state leak" was the
  process HASH SEED — `get_live_visible_enemies` iterated a set of region
  names, so the AI's contact list and P4's first target were seed-ordered.
  The list is in map order now; one event list across every seed after.
- **FA-S17-4 (P3):** the committed naval script could never sail (Soult's
  28,940 against a 15,000-man lift); it follows the lift counsel's own
  marshalate road and lands.

### 4b. After the scoring runs — what the re-score itself found

- **FA-S17-5 (P1) — the peace table paid the LOSER.** A France that had lost
  Paris and ten provinces read as winning the coalition war and was OFFERED
  indemnities by the courts beating her (tyrant-accept/austerlitz T11–12:
  *"Paris has been captured by Austria! … Britain has offered terms …
  Offering 3169 gold"*). Two seams, one cause: the DEFENSE objective ticked
  +1 per lost home province per turn on EVERY pair the defender had, whoever
  held the province — so under FA-D4's boot purpose a France that lost Paris
  to Austria accrued a claim against Prussia, Russia and every court that
  took nothing — and `calculate_side_war_score` re-clamped every component at
  its pair cap EXCEPT `ticking`. **Measured before/after on the ambient
  board:** at turn 31 France holds 13 of 28 provinces and the old code scored
  the war **+2 (winning)**; the new code reads **−29**. At turn 41, 9
  provinces: **−14 → −39**; the ticking component 56 → 25 (clamped).
  **Verified in the wild** by re-running the ten played arms: Britain's offer
  to a beaten France turned from *"Offering 3169 gold"* into *"Asking 5987
  gold"*. ⚠ **One standing pin was re-sited consciously and the re-site is
  the point of the fix**: CA8's ±100 total-clamp pin reached 100 by giving
  two pairs `accumulated_ticking: 70` — the un-clamped component itself, and
  a state the engine cannot produce (the per-pair cap is 25). The claim is
  unchanged; the vehicle is now a real two-front conquest.
- **FA-S17-6 (P2):** the "rebellion imminent" question outlived the
  rebellion — delivered the turn AFTER *"Switzerland has rebelled"*,
  answering *"rebellion will follow"*, and standing as the current dialogue
  it refused the letter-book and a settlement offer for 2–5 turns. Nine of
  seventeen boards. One helper now retires it at every rebellion exit.
- **FA-S17-7 (P2):** the Emperor was captured OFF the field by the Guard's
  toll — the report said *"The Guard bought the road … flees to Lorraine"*
  and the next morning said *"the Emperor himself is TAKEN. Russia holds
  him"* after BRITAIN had beaten him. The 30% toll was paid even when it left
  him under the 50-man rubble floor. A road the Guard cannot pay for is no
  road: he is ASKED instead, and no toll is taken.
- **FA-S17-8 (P3):** the campaign log printed *"Defensive cascade: Unknown
  joins war via France"* — the producer writes `defender`, the one-liner read
  `nation`. 20 rows across 17 runs.
- **Harness:** the driver never read `deferred_marshal_petition` — the key
  the backend has delivered the end-turn petition under since slice 6 — so
  the marshal-petition channel was unexercised on every Phase-3 arm (12
  petitions answered across 34 runs, 7 of them after the grievance lapsed).
  **Every Phase-3 claim about the Jealousy channel is therefore weaker than
  it looks, and the marshal-drama score carries that caveat.**

`BASELINE_SERIES` is byte-identical on both arms of the part-2 levers, and
that is a fact about the instrument, not evidence of safety: the ambient
threat scalar does not read war scores, and the ambient arm declines every
offer. The war-score change is measured directly instead (above).

## 5. Mode C — the Phase-2 surfaces on screen (port 8006, its own save dir)

- `FA_P3_MODEC_1_REDEMPTION_SETTLE_ARM_2026_09_11.png` — "LANNES REQUESTS
  AUDIENCE": the FIRST arm is *Settle Lannes's account — a rente of 160g a
  turn* above Grant Autonomy / Dismiss / Transfer to Staff (FA-D5).
- `FA_P3_MODEC_2_ACCOUNT_SETTLED_2026_09_11.png` — the answer runs the
  executor's own `grant_pension`: "THE ACCOUNT SETTLED … a rente of 160g/turn
  … it will cost the crown 240g/turn"; Admin 2/2 → 1/2 (shown = applied).
- `FA_P3_MODEC_3_WAR_DETAIL_OBJECTIVE_HINT_2026_09_11.png` — the war-detail
  popup on a pre-Phase-2 save: *No war purpose set — 'set war purpose against
  Britain' names one…* plus FA-D10's standing rows.
- `FA_P3_MODEC_4_BOOT_WAR_DETAIL_DEFENSIVE_HINT_2026_09_11.png` — the boot:
  *Objective: Defense … (against Britain)* and *A defensive purpose only
  (hold the homeland) — 'set war purpose against Britain' names a purpose of
  your own.*

Unseen by this pass (owed to the next played session): the ledger's Materiel
line, the diplomatic ledger's armistice projection (FA-D18), the Admiralty
tab's lift counsel (FA-D16), the Gazette's laurels row.

## 6. Instrument limits — what this evidence cannot say

1. **The marshal-petition channel was not exercised** (§4b): the driver read
   `marshal_petition`, the end-turn response carries
   `deferred_marshal_petition`. 25 of 34 runs answered zero petitions. Fixed
   now; every Jealousy claim here predates the fix.
2. **`unknown_blockers: []` means "no popup KEY the driver does not
   recognise", not full coverage** — a key it never checks is invisible to
   that counter by construction. That is how limit 1 hid.
3. **The enemy phase is the FOGGED view.** Turns with nothing visible run to
   12 of 40 on some arms; an absence in a digest is not an absence on the
   board.
4. **The answer policy is a stated robot**, not a player: objections
   trust/insist, diplomacy decline or accept-everything, redemption
   grant_autonomy, rewards ignored. The FA-D5 settle arm, the petition arms
   and the reward rail are therefore unexercised by the driver and were
   checked in Mode C instead.
5. **The scripted "fighting" France spends 9–22 of 160 AP** over 40 turns and
   its script ends at loop 22–30 of 40, so Fr@30/Fr@40 on those arms measure
   a France that has stopped being played.
6. **The driver breaks every peace it signs** — `force_declare_war_confirmation`
   is answered with its first option, so the next scripted attack on a court
   just signed with re-declares the war (9 of 10 played runs).
7. **One live parse in 59 commands.** The fast parser cleared 58 at ≥0.7, so
   live-LLM parsing is a single data point.
8. **The run summariser's "Napoleon captured" column is a regex artefact** in
   both directions; captivity here is read from `Napoleon.captured_by` in
   each run's final autosave.
9. **`meta.json` records the driver's content hash but no backend tree
   identity** — a run cannot prove which commit it ran on.
10. **The LEDGER rows are the projection read at turn start**, not the
    applied phase; they drift ~1% of net per turn.

## 7. Defects — routed to `BUG_FIXES.md`

**Fixed this phase:** FA-S17-2, FA-S17-3, FA-S17-4 (part 1); FA-S17-5,
FA-S17-6, FA-S17-7, FA-S17-8 and the harness petition key (part 2).

**Routed, not fixed** (ranked; each carries its evidence on its row):

| id | P | one line |
|---|---|---|
| FA-S17-9 | P2 | A pursuit accepted on a real sighting prints "(at unknown)", is reported ACTIVE, and is cancelled next turn — its own first step's visibility refresh erased the intelligence that justified it |
| FA-S17-10 | P2 | The two surfaces still disagree on the ENEMY attacker's casualties in the enemy phase: 14 of 14 compared pairs (ambient-jena T3 prose *"Mack's army 1,253"* vs record *"Mack (lost 892)"*) — CA8-1's family, one phase over |
| FA-S17-11 | P2 | Berthier calls the battle that took the Emperor *"a skirmish … no battle to speak of"* — the FA-S16-D3 scale gate has no exemption for an arm reporting a sovereign's capture |
| FA-S17-12 | P2 | Jealousy confrontation audiences are dead on arrival: 7 of 12 resolve *"The moment has passed … Nothing was spent"* in the block they are delivered |
| FA-S17-13 | P3 | One state, four answers: a court now at peace refuses `pursue` flat with a raw key, `charge` with *"Cannot find target"*, while `march` names the road and the in-range attack stages the declaration |
| FA-S17-14 | P3 | The literal marshal quotes words the Emperor never typed — the ASK renders the engine's resolved target in quotation marks |
| FA-S17-15 | P3 | The same court sends a bilateral Peace Treaty envoy AND a coalition settlement offer for the same war in the same turn |
| FA-S17-16 | P3 | One letter, two names: the letter-book titles a `friendly_gift` ask "Open Borders Agreement" while the Event Log records "gift of friendship" |
| FA-S17-17 | P3 | FA-D4's boot purpose reaches only scenario boots — a campaign saved before Sept 11 (and both committed fixtures) keeps a purposeless spine war |
| FA-S17-18 | P3 | The War Detail Standing block lists both sides with no side marker; France and its allies render as peers of the enemy |
| FA-S17-19 | P4 | The objective line prints a ticking rate beside "not ticking" — *"(not ticking, +0, +1/turn)"* |

## 8. Design items — routed to `DESIGN_REFINEMENT.md`

| id | item | proposed owner |
|---|---|---|
| FA-S17-D1 | **A Defense war purpose should tick once per WAR**, not +1/turn per held home region per opposing court — the multi-court sum is what turned a lost war into a paid one, and the clamp is a bound, not a model | `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` (WPS-A ticking table) |
| FA-S17-D2 | **Peace is a money printer with nothing to buy** — every peace arm ends t40 at 65k–113k gold while 10,000 foot cost 150g | EC-2 pass 2 (`ECONOMY_REVISIT_SPEC.md` Track 3 / ES-4) |
| FA-S17-D3 | **The peace that cannot hold**: Britain re-declares the instant the 8-turn truce floor expires on every seed, then offers terms three turns later — an eleven-turn metronome with no cause narrated | a diplomacy gate beside WO-D8 |
| FA-S17-D4 | **Deliver-time validation for the confrontation channel** — a petition whose grievance has already cooled should not be delivered | `PETITION_POPUP_REVISIT_SPEC.md` B1 |
| FA-S17-D5 | **The Peril needs a warning rung**: the Guard's dwindling ranks should be named before a toll can take the Emperor | `NAPOLEON_SPEC.md` §7 (NP-4) + NPC-D1 |
| FA-S17-D6 | **A COMMANDED driver arm**: scripts that spend all four actions and run the full 40-turn horizon, and a `force_declare_war` policy that will not break a peace France just signed — without both, no balance condition can be measured on a France that is still being played | `docs/PLAYTESTING.md` + `tools/playtest_scripts/` |
| FA-S17-D7 | **Vassal drama exists only for a France that is losing** — 0 rebellions on 11 fighting-and-answering boards against 11 of 17 unattended ones | the FA-D27 balance owner |
| FA-S17-D8 | **The rebellion warning arrives one tick before the rebellion** — widen the window (warn at the wavering band) or let it mount over a letter | `PETITION_POPUP_REVISIT_SPEC.md` F1 |
| FA-S17-D9 | **Retire or route `proposal_result_popup`** — the backend stages it on every proposal outcome and the client's scene is an orphan | harness/doc hygiene |

## 9. Top-5 missing features · top-5 broken things

**Missing** (the game does not do it at all)

1. **A gold sink for a France at peace** — the treasury compounds to six
   figures with nothing to spend it on (FA-S17-D2).
2. **A reason the wars restart** — Britain re-declares on a timer with no
   narrated cause (FA-S17-D3).
3. **A warning rung before the Emperor is lost** — the Peril has a capture
   and no approach (FA-S17-D5).
4. **Loyalty tension for a competent Emperor** — the vassal arc only fires
   for a France already losing (FA-S17-D7).
5. **Any victory condition** — 34 runs, 40 turns, nothing ends; the game
   stops because the driver stops (the Victory & Objectives pass, ROADMAP
   positions 12–13).

**Broken** (the game does it wrong)

1. ~~The peace table paid the loser~~ — **FIXED this phase** (FA-S17-5).
2. ~~The Emperor captured off the field by his own escape~~ — **FIXED**
   (FA-S17-7).
3. ~~The rebellion question outliving the rebellion and shutting the
   mailbox~~ — **FIXED** (FA-S17-6).
4. **A pursuit that erases its own justification** and dies unexplained
   (FA-S17-9, open).
5. **The enemy attacker's casualties differ between the two surfaces that
   report them** (FA-S17-10, open).

## 10. What this discharges, and what it does not

**Discharged:** the brief's Phase-3 mandate — every pillar played on the
committed driver across 34 seeded runs, the FA-D27 arms re-run with every
Phase-2 lever up, the tutorial, naval, both fixtures, a reload arm and one
live-parser arm, a Mode C visual pass, and a re-score of all ten pillars
against the Aug-16 baseline with named evidence.

**Not discharged:** a HUMAN campaign. Every limit in §6 points the same way —
the driver is a camera with reflexes, and the three things the audit most
wants to know next (does a competently played France hold; is the AP lever
worth pulling; does the Jealousy channel feel alive when its petitions are
actually delivered) need a person at the keyboard. The Phase-3 fixes to the
instrument (the petition key) and to the scripts (FA-S17-D6) are the
precondition for that being worth measuring.
