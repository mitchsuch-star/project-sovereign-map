# The economy gate (October 5, 2026)

**The brief, in the user's words:** *"fix and decide on these"* — the list the economy audit left open (`docs/audits/ECONOMY_AUDIT_2026_10_05.md` §10–§11):
1. the nine design rows EAD-1 … EAD-9 (the opening war's price, a lever on the Charges of Empire, the levy's price, the army's alarm, commissions, the neutral courts' hoards, the march step, the league's silence, the AI's spending rule);
2. the defect EA-19 (the next league's forecast counted a court in a truce with France as free to join);
3. the reading's gaps (no game window driven, no live-key arm, UI/UX unmeasured, the EYES marks the delegate's).

**Gate record:** `docs/SCORE_FINISH_SPEC.md` §6.8 (authoritative). **Rules:** `docs/SYSTEMS_REFERENCE.md` §98. **Pins:** `tests/test_economy_gate_2026_10_05.py`. **Series attribution:** `tools/_econ_gate_series_arms.py` (record `tools/_econ_gate_series_arms_final.json`). **Sweep:** `tools/_sweep_econ_gate.json` (47 rows, 47 killed). **Attribution:** `tools/_econ_gate_exit_attribution.py`. **The reading:** `docs/audits/score_runs/2026_10_05_econ_gate/`.

## In one paragraph

Six read-only investigators measured each question on the live board before anything was ruled (§1). **Built:** campaign pay (EAD-1), the Charges named where gold is spent (EAD-2), the army's alarm line at a third of Europe's men (EAD-4), the march step's lawful road and the league's aim (EAD-7), the league's silent courts (EAD-8), the truce that binds a league (EA-19, with two riders), a recovery road for a court left without a general (EA-7), and the instrument's own port (EA-E8). **Kept, with the record corrected:** the levy's price (EAD-3), the commission's price and corps (EAD-5), the peaceful hoard (EAD-6), the AI's purse read (EAD-9). The headline consequence is EAD-7's: Europe's armies can now walk a lawful road to France, and on one of seven commanded seeds (austerlitz) a Russian corps does, while the scripted France stands in Germany (§7). **The reading's gaps are closed** — the client arm (262 frames at both scales, the parse check, the boot smoke and a new driven client session that passes 95 of 95 checks over five turns), the live-key arm, and the EYES marks re-taken from fresh evidence (§10). **The gate costs items:** like for like over 13 pillars the directional reads 7.69 → 7.42 — campaign pay empties the opening chest (economy C1, first contact C4), and with the road it lets the austerlitz collapse happen (living balance F1, narration C1/C4, AI aliveness C6); every flip is attributed by lever-down arms and each has its lever (§11, EG-D2).

## 1. How it was decided

| Investigator | Question | Method |
|---|---|---|
| EAD-1 | Why does the opening war cost France nothing; what war footing would? | A per-advance observer on `_build_economy` (applied mode, every nation) over 15 turns of the three commanded seeds; five candidate rules simulated by monkeypatch (×1.25 upkeep at war, a 10/15/20% war draw on revenue, the Charges' war terms on revenue, campaign pay ×2.5 / ×3.0, the stricter variant); E1's boot replicas; 40-turn provinces and enemy attacks; the ambient series |
| EAD-2 | Is there already a decision attached to the Charges; what lever would add one? | The Charges' anatomy per turn and term on three commanded seeds and the LAW arm; counterfactual 10,000g and Staff-priced sinks; candidate (A) a law halving the crown term, simulated; what each surface tells the player |
| EAD-3 / EAD-5 | Does the levy's price ever matter; are commissions overpriced? | 33 instrumented 40-turn runs (commanded, spender, a max-draft scratch arm, ambient); scarcity pricing k = 1/2/3 and a one-levy-a-turn cap simulated on the one pricing seam; the 8,000-man commission simulated |
| EAD-4 | Should the army's alarm line read a third of Europe? | Both share measures (men; the bloc's power) at boot and per turn on the commanded, spender, max-army and ambient arms; the 0.33 line and the bloc-share version simulated; an 89-file pin census under each |
| EAD-6 / EAD-9 / EA-7 | Who hoards and why; does the AI's purse read matter? | Every court's chest at turns 10–40 on the commanded and ambient boards; the laws rung under both reads; secondary decks, a fourth standing marshal, a bench for the secondaries and an admin phase for marshal-less courts simulated |
| EA-19 / EAD-7 / EAD-8 | The truce gate; the march step's road; the league's silence | Reproduced on CMD-M; prototypes by monkeypatch (the truce gate; the fellow filter and the lawful path); 9 commanded and ambient arms; the fog boundary of every draft line checked against what France sees |

## 2. The rulings

| Row | Ruling | Why |
|---|---|---|
| **EAD-1** the opening war's price | **BUILT — campaign pay**, a satellite's soil exempt (§3) | The war was cheap because the battles shed the overpriced boot army (the Grande Armée surcharge and the over-limit band: +940 to +1,090 a turn to France's Net on turns 2–10), the user's own "you pay for the soldiers you have". No symmetric war footing took France's opening Net to zero without bankrupting Austria (its boot chest of 700 is the binding constraint) or France itself; the economy-wide ones thinned the AI's purse and undid EA-11's attacks (marengo 39 → 17–19). Campaign pay bites where the war is actually fought — allied Germany — and changes no AI decision |
| **EAD-2** the Charges' lever | **BUILT — the decision made visible** (§4); a law that halves the crown term REJECTED; an act of state (SF-ECON-1) left with its gate | The decision already exists and is strong: a 10,000g purchase at turn 12 costs the turn-41 chest only 2,434–4,149, because 59–76% comes back as lower Charges. Nobody said so. A law halving the crown term pays the hoarder (its break-even chest is 27,000 at 150 a turn) and gives a spender nothing — against "isn't too easy" |
| **EAD-3** the levy's price | **KEPT** | France's draft gold is 1–9% of what its men cost in upkeep; upkeep, the class (the pool) and the levy ground decide the army. Scarcity is already priced where history put it — on substitutes, 4× the draft price with a full class and 16× with an empty one. Either candidate lands on the AI under GR5 (scarcity pricing at k = 2: Britain's levies 33 → 10) and moves the series |
| **EAD-4** the army's alarm | **BUILT — the line at a third of Europe's men**, still a MEN measure (§5) | Consistency with the Armed Peace's own fraction. The symptom the row named (the alarm at 0 under a 213,000-man army) is already answered: the Armed Peace holds the alarm at its watch line, and Europe re-arms in peace (EA-11), so France's share falls to 18–29%. The bloc-power version is rejected: it fires at boot, duplicates the hegemony term and lets the alarm slip around the Armed Peace's fuse |
| **EAD-5** commissions | **KEPT** | A commission buys a general (45–95% of the price), France's only artillery arm (Marmont, Senarmont) and a corps within reach of the Paris levy; gold per man is the wrong yardstick. The 8,000-man corps is an AI buff: the commanded France ends turn 40 with 19 / 18 / 16 provinces instead of 28 / 29 / 28 |
| **EAD-6** the neutral's hoard | **KEPT inert by design**; EA-7's recovery road FIXED (§9) | The peaceful hoard (the Ottoman 73,000 at turn 40 on every seed) is invisible to the player, capped by the Charges and priced into indemnities, and a latent war chest: at war P7.5 arms with it. A fourth standing marshal misses every hoarder (only the great powers have benches). Decks for the secondaries would re-open R6, which the user confirmed ("no minor court has laws"). A bench for the secondaries at war is the one lever that reaches the at-war hoarders (Spain 37–50k): measured, enemy attacks +8 / +23 / +16 and France 22 / 26 / 28 provinces — offered, not built |
| **EAD-7** the march step | **BUILT — the league aims at its enemy; the march reads the lawful road** (§7) | The fellow-member aim did not reproduce on this tree but is cheap and correct. The lawful road is AI competence the old straight hop lacked: a corps whose straight road crossed a closed neutral stood still forever |
| **EAD-8** the league's silence | **BUILT — public facts only** (§8) | France never sees most league corps (on CMD-A not one Russian, Swedish, Hanoverian or Sardinian corps during the league's war), so the row's own example lines ("Russia's armies are in Finland") would leak; the reading uses provinces, states, crossing verdicts and France's own sightings |
| **EAD-9** the AI's purse read | **KEPT — the plain read; the record corrected** | The brake is not the Charges: the chest-plus-reserve test refused 240 times on the three commanded seeds, the Net clause once. The pre-Charges read changes no purse and no enactment on any commanded seed. AI aliveness C1 fails at the content's ceiling (the four decks hold 20 laws; the rivals enact 19–20) under either read — put to the user, §6 row 23 |
| **EA-19** | **FIXED** (§6) | — |
| **EA-E8** | **FIXED** (§10) | — |

## 3. EAD-1 — campaign pay

**Why the opening war was cheap** (the investigator's per-advance observer, mean effect on France's Net over turns 2–10 against the boot projection of +1,032, historical / austerlitz / marengo):

| Component | Effect on Net |
|---|---|
| Shed surcharges (the Grande Armée's 882 and the over-limit band's 236 vanish as the army falls 189k → 110–130k) | +940 / +1,090 / +990 |
| Base upkeep falls | +439 / +481 / +485 |
| Trade | +215 / +215 / +207 |
| The Charges of Empire | −563 / −429 / −655 |
| Tribute falls | −317 / −375 / −147 |
| Blockade and Admiralty | −179 / −128 / −174 |

Requisitions were about zero: France fights on allied Bavarian soil and captures what it enters.

**The candidates** (boot replicas of the E1 tests; 15-turn and 40-turn commanded runs):

| Rule | France boot absorption | France boot Net | First court to break | France min · mean Net t2–10 | Chest t10 (k) | 40-turn provinces · enemy attacks |
|---|---|---|---|---|---|---|
| shipped | 0.670 | 1,032 | — | 867/1,309/1,241 · 1,520/1,892/1,783 | 12.4 / 17.2 / 14.5 | 28/29/28 · 39/29/39 |
| upkeep ×1.25 at war | 0.837 | 374 | Austria's homeland arm, at any multiplier | 902/989/1,306 · 1,375/1,662/1,568 | 10.5 / 12.8 / 12.6 | 28/23/29 · 40/30/**17** |
| 15% of revenue at war | 0.670 | 644 | Austria at ~31% | 990/884/1,171 · 1,384/1,549/1,477 | 10.2 / 11.9 / 11.9 | 25/23/29 · 41/33/**19** |
| the Charges' war terms on revenue | — | — | Austria bankrupt 7 turns (14 arrears), deserting | 54/307/675 · 624/1,110/1,044 | 3.5 / 8.0 / 8.0 | — |
| campaign pay ×2.5, every non-enemy soil | 0.850 | 324 | France itself at ×3.2 | 312/1,145/847 · 830/1,714/1,233 | 5.4 / 14.4 / 8.2 | 28/29/28 · 40/29/39 |
| **campaign pay ×2.5, a satellite's soil exempt (ruled)** | **0.722** | **828** | none (France at ×8.6) | **564/1,116/1,294 · 858/1,689/1,413** | **5.3 / 14.7 / 10.3** | **28/29/28 · 40/29/39** |

**The ruling.** At boot only Bernadotte pays (17,000 men at Franconia, allied Bavaria: 204 a turn). Massena at Milan stands on the Kingdom of Italy's soil — a satellite fed the corps quartered on it — and pays nothing. Through the war the bill follows the corps that quarter in allied Swabia, Franconia and Bavaria. The Staff — the purchase REFORMS Q3 placed "mid-campaign, turns 10–15" — was affordable at turns 11 / 8 / 8 on the commanded seeds (the counsel's own bar, 11,500); with campaign pay, at 14 / 11 / 13, inside the window on all three. No AI decision moves: `BASELINE_SERIES` is byte-identical with only this lever up.

**What it costs the instrument.**
- The E1 band's turn-1 test (0.62–0.70) is re-blessed to 0.66–0.74 (measured 0.722). France's homeland-only Net is pinned at −244 (was −40); the satellites' tribute still carries the army.
- The LAW arm is a 10-loop arm that also enacts two cheaper laws and repeals and re-buys one. It reaches the Staff after loop 10, so economy C1 (v1.1: "by loop 10, the arm's last") reads ✗.
- REFORMS T1 as written ("on the commanded arm, a France that saves for the Staff can enact it between turns 10 and 15, on three seeds") reads 3 of 3, where the shipped tree read 1 of 3 (8 and 8 were before the window).
- The item is not re-anchored here; that would be the ruler moving for the ruling.

**History.** In 1805 the march through allied Germany was fed by contract. The army's contractors, Vanlerberghe's Négociants Réunis, ran on Treasury paper; the Banque de France faced a run in the autumn, and Barbé-Marbois fell after Austerlitz. Contributions on enemy soil and the Pressburg indemnity paid the debt back — the game's requisitions and indemnities.

## 4. EAD-2 — the Charges name their price

**The anatomy** (commanded arm, 40 turns, historical / austerlitz / marengo):
- **Totals:** the Charges took 55,867 / 44,846 / 49,361 gold — 54% / 46% / 41% of France's income before them.
- **At peace** only the crown term (30 points) fires — about 16% of income.
- **At war** the rate rises to 80–390, and a war of 8–10 turns takes 22–41k of an idle hoard.
- **By term:** crown 27–34%, war establishment 17–26%, war exhaustion 16–25%, pensions 12–14%, wars going ill 0–14%, the Emperor's grip 0–22%, restless interior 1–3%.

**The decision already exists.**
- A 10,000g purchase at turn 12 costs the turn-41 chest only 3,230 / 4,149 / 2,434 — 59–76% of it comes back as lower Charges.
- A Staff-priced purchase (9,000, then 300 a turn) bought at turn 12 costs 6,988 of the turn-41 chest against 17,700 paid in all.
- At turn 40, at war (rate 361), the Staff's 9,000 would cut the Charges by 1,300 a turn — four times its upkeep.
- **Nobody said so.** The counsel quoted "9,000g, then 300g a turn"; the end-turn banner showed the amount alone; the desk's purse answer never named the Charges.

**Found measuring it.** A political law that takes the Emperor's grip under 70 switches on the grip term's +50 rate points, and at peace there is no road back: the player's authority returns through battles and a few marshal outcomes. On marengo, authority sat at 37 through the peace from turn 32, and the grip term alone took 9,081 gold. The confirm named the marshals' calm and the diplomatic-point lines, never the Charges.

**Built:** `WorldState.charges_relief` (one source) on the counsel's law line, the ledger's Charges line and the desk's purse answer; `ledger.charges_grip_clause` on the political law's quote and its result.

**Rejected:** (A) a law halving the crown term. Its break-even chest is 27,000 at 150 a turn, so it pays the hoarder and gives a spender nothing; and no existing effect type reaches the Charges (an eleventh type is structural, REFORMS §4).

**Left with its gate:** (B) an act of state turning gold into something the Charges cannot reach. A monument for authority would be the one lever that answers the grip term. It belongs to SF-ECON-1, which §6 row 11 opens only if economy C6 fails; it does not.

## 5. EAD-4 — a third of Europe's men

**The two measures** at boot, on every seed: France holds 31.5% of Europe's standing men (189,000 of 600,000), and its bloc holds 39.6% of Europe's power. Power is provinces × tier weight over the leader, its vassals and its formal allies — the measure the hegemony term and the Armed Peace read.

| Arm | Men share, turns 2–6 | Men share, long peace | Bloc power |
|---|---|---|---|
| Commanded (historical / austerlitz / marengo) | 31–34% | 18–22 / 21–26 / 6–19% | 36–41% |
| Max army (scratch: a levy and 30,000 substitutes every turn) | 31–34% | 21–29.5% (195–208k) | 35–41% |
| Ambient (passive France) | 30–32.8% | at war throughout | under 1/3 by turn 9 |

Europe re-arms in peace (EA-11): its standing men grow from 440–500k to 650–780k, so even a maximal French army stays under 30%. The row's "213,000 = 35%" predates EA-11.

**The candidates.**
- **The men line at 0.33** adds +3 / 0 / +4 alarm on the commanded seeds, all in the Ulm opening (a league already stands; the alarm is 75–99). It never fires in peace or for another court; `BASELINE_SERIES` is byte-identical and no pin moves.
- **The bloc-share line** adds +39 / +39 / +40 over 40 turns and fires at boot on exactly the hegemony term's turns — a duplicate. It makes the alarm creep +1 a turn above the Armed Peace's watch whenever a grudge runs, a road around the fuse, and moves 13 pins.

**Ruled:** the men line at exactly one third, its own constant beside the Armed Peace's 0.33 power floor. The passive France's peak share across 10 seeds is 32.84%, 0.49 points under the line.

## 6. EA-19 — a truce binds the league

**Reproduced** on CMD-M. Turn 12's page (read at turn 13) named Austria as a court that "would now join a league", though Austria was in an ARMISTICE with France with its cooldown at 4 (relation −77). `declare_war` refuses a pair the cooldown binds (R99); `qualifies_for_coalition` read only WAR.

**Fixed at the gate.** `diplomacy.declaration_cooldown_left` is the one reading that R99, the offensive cascade, the war council and the gate share. The forecast files a truce partner under its own status, kept out of the joiners and out of the courts a fresh peace binds. So the turn-13 headline — when the truce becomes a peace — still names Austria as newly bound.

**Riders**, found tracing it:
- While a league stands, the single-court line said "a league stands declared. She will march." But no road enrols a newly free court into a standing league (`join_coalition` is the War of the Congress's alone). The line now names the next league.
- `form_coalition` checked "at least two members" before the failed declarations were dropped (SFR-DR1's rider), so a league of one court could form. It no longer does.

On the ambient board the gate never fires (no court is in a truce with the passive France), so the series is byte-identical.

## 7. EAD-7 — the march finds its road

**The aim.** On this tree no league member is at war with a fellow member on any measured board: the filter reads 320 decisions on the ambient board and changes none. On the pre-audit board, Britain, Russia and Sweden aimed at each other on 32 corps-turns (Paget at Livonia aiming at Stralsund). Built as a guard.

**The road.** The march hop had to shorten the straight distance, so a corps whose straight road crossed a closed neutral stood still. Staged: Deroy (Bavaria) at Franconia against an Austrian corps at Moravia. The one straight hop is Dresden, which is Saxon and closed; the lawful road runs Franconia → Bohemia → Vienna → Moravia. Shipped: no move. Built: Bohemia.

**Three forms measured** on the commanded arm (France's provinces at turn 40):

| Form | historical | austerlitz | marengo | ulm | jena | eylau | friedland |
|---|---|---|---|---|---|---|---|
| no road (shipped) | 28 | 29 | 28 | 23 | 24 | 23 | 28 |
| **straight first, the lawful road when stuck (built)** | **26** | **7** | **29** | **23** | **24** | **22** | **22** |
| straight first, never back along the road | 26 | 6 | 29 | — | — | — | — |
| the lawful road alone | 26 | 6 | 29 | — | — | — | — |

The three forms agree wherever measured, so the smallest change ships.

**The austerlitz seed.**
- France accepts Russia's armistice at turn 8; it collapses at turn 12 ("the war resumes where it stood").
- Kutuzov, who before could never find a road to France, marches between turns 13 and 21 from Piedmont through Provence, Lyonnais, Limousin and Berry to Normandy, Picardy, Flanders, Orleanais and Ile-de-France, taking Bernadotte prisoner at Paris.
- Meanwhile the scripted French army stands fortified and drilling in Franconia.
- In the old game, the war with Russia on this seed was a war Russia could not fight; now it can.

**Living balance F1** ("on CMD, France holds ≥ 20 provinces at turn 40 on 3 of 3 seeds") therefore reads ✗ on this tree. It is put to the user as §6 row 24 (`DESIGN_REFINEMENT.md` EG-D2). The lever restores the floor; no AI constant was tuned.

## 8. EAD-8 — the league's silent courts

**Fog.** On CMD-A, France never sees a Russian, Swedish, Hanoverian or Sardinian corps during the league's war; Britain's only sighting was a leftover at Aragon. The row's own example lines ("Russia's armies are in Finland") would leak. The reading is built from provinces, diplomatic states, the naval crossing verdicts and the corps France itself sees at FULL / PARTIAL.

**At boot** (the Third Coalition stands; no court has struck yet): *Austria has an open road to us — 1 march — and has not struck us. Britain has no road to us but the sea, and Normandy is a defended shore: she can land only by expedition, 15,000 men at a time. Russia has no lawful road to us — the neutrality of Prussia and Hesse bars it.*

**Surfaces:**
- The dispatch's coalition section carries the rows every morning a league stands (`active_coalition.unmarched`, rendered by `dispatch_view.gd`).
- The front page's `league_unmarched` beat (weight 56, below the league's own news) fires when the set of reasons changes, never as a streak.

## 9. EA-7 — a court without a general may commission

`TurnManager._process_enemy_turns` skips a court with no standing marshal whole, and with it the Marshalate's commission rung (P1.75). So a court whose last general fell could never field another; the investigator saw this hold Austria for four turns on one variant run.

The court now runs that one rung alone, through the shared executor, and a court that commissions is not reported eliminated. The nine marshal-less courts measured idle have no bench and stay as they were (`execute_commission_only` returns nothing for them). The fix is inert by construction on the ambient board.

## 10. The gaps — the client arm, the live arm, a driven client session, the instrument's port

The economy audit's reading left four gaps: no game window driven, no live-key arm, UI/UX unmeasured, and EYES marks taken from saved screenshots. This reading closes the first three on the final tree, and re-marks the EYES items from fresh evidence. The marks stay the delegate's; yours override them.

- **The client arm** (`arms/CLI/`): 131 surfaces × 2 Interface Scales = 262 frames from the real scenes, windowed off-screen. 0 SCRIPT ERROR; the parse harness EXIT 0 (64 scripts, 9 scenes); a headless boot smoke of `main.tscn` on its own port, 0 SCRIPT ERROR. UI/UX is exercised for the first time since the final reading: F1, F2, C1, C2 and C3 ✓ (no button off-screen, no clipped text, no raw key in any frame).
- **The live-key arm** (`arms/OP-LIVE/`, the key from `.env`): the fast parser read 144 of the 145 typed lines. One line, a bare "yes", reached the model, which answered in character and asked for an order. 0 misreads, so command C6 ✓. The arm's one expedition line is refused, the same SCRIPT PRECONDITION its mock twin carries on the last three readings.
- **A driven client session** (new: `tools/mode_c_driven_session.py` + `.gd`, now part of the client arm, record `arms/CLI/modec/`):
  - **The rig:** the real `main.tscn` and the real API client, headless, against a backend on an unused port with its own save directory. Every advertised key is pushed into the viewport as an engine event, never an operating-system keystroke, so your running game was never touched.
  - **Keys:** each key is tried in both focus states. Six screen keys, Alt+1–8 and 1–8 in the strategic ledger, 1–7 in the diplomatic ledger, F1, Tab / Alt+backtick, M, +, -, Home and Escape.
  - **Turns:** five, each ended by its own road — typed, E, Alt+E, the End Turn button.
  - **Result:** 95 of 95 checks pass, 5 turns, nothing blocked. Modals answered: enemy phase ×5, the battle diorama ×5 (Escape skips the tableau, then Close), the letter-book ×4, one envoy and one last stand.
  - **What it cannot see** is a key the operating system eats before the engine — EA-E9's NVIDIA overlay on Alt+R.
- **The instrument's port:** every child of the reading talks to 8021; the formables entry frame renders its payload, with no "Loading…" (EA-E8).
- **The EYES marks** (`eyes_delegate.json`, from this reading's frames and records):
  - ✓ agendas C6, combat legibility C6, vassals C6.
  - ✗ first contact C2 (SFR-H8, unchanged).
  - ✗ narration C6: 9 of 10. World turn 6's page never names the Kingdom of Italy's elimination (EG-X3).
  - ✗ naval C6, strict: the compact top bar's blank buttons (EA-E1) and the chip's amber border (EA-E3).
  - ✗ UI/UX C5: 8 of 10 frames; TOP_BAR_BOOT_X2 (EA-E1, EA-E2) and WIZARD_STEP2_AUSTRIA_X2 (EA-E5) still fail at 2.0.
  - ✗ UI/UX C6, strict: the driven session passes everything; EA-E9 alone remains.
  - ✗ marshal drama C6 (the petitions' voice, unchanged).

## 11. The series, the metrics, the reading

- **`BASELINE_SERIES`** was re-recorded once, twelve-arm attributed (`tools/_econ_gate_series_arms.py`): arm 0, each of the ten levers alone, and all of them.
  - Arm 0 reproduces the economy audit's record byte for byte.
  - The lawful road is the sole mover (divergence at [18]); all levers against the road alone diverge at [25].
  - The unattended France ends turn 40 with 1 province (12 on arm 0).
  - Holland is eliminated; Austria holds 25, Britain 28, Russia 11.
  - The WO slice-9 and slice-10 ungated boards are re-seated with their own attribution (`tools/_econ_gate_wo_attribution.py`): every gate lever down returns the audit's figures byte for byte. Seams 14 → 9, cooldowns 14 → 10, the uncapped rebellion 12 → 13.
  - M1–M7 are byte-identical.
- **Found building, all fixed** (`BUG_FIXES.md` §The Economy Gate):
  - EG-X1: an order's target printed as its key on six surfaces.
  - EG-X2: the league's news crowded off a busy morning.
  - EG-I1 and EG-I2: living balance C5's reader.
  - EG-I3: the descent arm's staging, 18 gold short.
- **Filed open, owned:**
  - EG-X3: a lost satellite crowded off the page — SF-RR3.
  - EG-X4: an intel row against the store's last sighting — SF-RR6.
  - EG-X5: a capital's emptied works unnamed — SF-RR4.
- **Sweep:** `tools/_sweep_econ_gate.json`, 47 rows, 47 killed, 0 INERT, 0 BROKEN at close. The first pass found one inert pin, my own: its fixture recorded the late row on both mornings. It was repaired and re-swept.
- **The reading** (`docs/audits/score_runs/2026_10_05_econ_gate/`): all 41 arms on the final tree — the drivers, the client arm, the suite arm (all green), the parser eval (902 of 902; replay 6 of 6), the live arm, and the AI-V sweep linked from the first pass (the AI is unchanged since). Checklist v1.1 with the delegate's marks:
  - **Directional 7.43 over 14 of 14.**
  - **Like for like** over the 13 pillars both readings exercise: **7.69 → 7.42** against the economy audit's v1.1 reading.
- **Item flips**, each attributed by lever-down arms (`tools/_econ_gate_exit_attribution.json`). With every gate lever down, all of them return to the audit's marks.

| Item | Flip | Cause |
|---|---|---|
| AI aliveness C1 | ✗ → ✓ (17 / 13 / 17 laws) | the lawful road: its wars spend the rivals' purses (20 / 20 / 20 with it down) |
| command C6 | · → ✓ | the live arm ran |
| UI/UX F1, F2, C1, C2, C3 | · → ✓ | the client arm ran |
| economy C1 | ✓ → ✗ | campaign pay: the LAW arm reaches the Staff after loop 10 |
| first contact C4 | ✓ → ✗ | campaign pay: on the DL arm the army marches into allied Germany. Net −22 on turn 1; the chest 209 / 96 / 502; on turn 3 the counsel can name no purchase it would carry out |
| living balance F1 | ✓ → ✗ (26 / 7 / 29) | the road AND campaign pay together: either alone down holds the austerlitz seed (26, 29). EG-D2 |
| narration C1 | ✓ → ✗ | the road: the collapse leads every morning with its event news. EG-D2 |
| narration C4 | ✓ → ✗ | the road and campaign pay together. EG-X4 |
| AI aliveness C6 | ✓ → ✗ (14 of 39 turns at war on marengo) | the road and campaign pay together |
| combat legibility C3 | · → ✗ | the road: Munich, emptied by Austria's capture, falls to Lannes the same turn. EG-X5 |
| naval C3 | ✓ → ✗ → ✓ | the arm's staging (EG-I3), re-staged and re-read |

**What it means.** The gate's two board rulings make the game harder. The opening war costs France real money (campaign pay). Europe's armies can now walk to the war their courts declared (the lawful road). Together they let a Russian corps walk to Paris on one seed of three while the scripted France stands in Germany. Nothing was tuned to restore the items; each has its lever, and the choice is yours (EG-D2, §6 row 24).

## 12. Limits

- The EYES marks are the delegate's, taken from this reading's frames and records; yours override them.
- The driven client session pushes engine events. It shows that every key the client advertises works in the engine and that five turns pass unblocked. It cannot see a key the operating system takes first, or whether a screen looks right — those are the frames and your eye.
- The live arm reached the model on one line. Command C6 measures that the escalation stays honest, not how well the model reads prose.
- Naval C3 now reads ✓ on a re-staged arm (EG-I3). The re-stage moves only the staging commission; it is recorded beside the arm and pinned.
- The austerlitz collapse is one seed of three on the commanded benchmark, whose France never answers a march on its homeland. A human France would; the item measures the script.
- AI-V was linked from the reading's first pass. Its arms are AI-only, and the later changes (EG-X1, EG-X2, the reader corrections, the re-staged arm) touch no AI decision; `BASELINE_SERIES` passes on the final tree.
