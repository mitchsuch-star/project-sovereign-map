# Recurring era events — "Affairs of State": the gate

**Status:** ✅ **SPEC AUTHORED October 27, 2026 — ⚠ USER GATE PENDING (§0).**
- **Design only.** Nothing is built and no game code changed. Nothing here holds the deploy.
- **Owner:** a proposed row **RE**, recommended after S15 (§15).
- **The code name is "affairs".** Module `backend/game_logic/affairs.py`; authored deck `moments.affairs`; runtime store `world.moments["affairs"]`; log type `moment`, with the phases `affair` and `court`. "Event" already means `event_log`, and the deck rides S14c's moments engine rather than forking it.

**The question it answers.** The user asked whether Ink & Iron has recurring events built on blocks of attributes — simpler, repeatable, era-flavoured events that could serve as gold sinks or slow a runaway advance. It has none. S14c (`docs/EVENTS_SPEC.md`) built four one-shot letters for France, each latched forever by its id, and struck the situational class (A1). This spec designs the recurring class against the game as it stands after S14i.

**The answer, before the detail.**
1. **The game already covers most recurring pressures,** so a deck that doubles nothing is small. Seven systems already cover them: the Charges of Empire, the coalition's sixteen alarm producers, stability, attrition, the dotations, the clients' drift and petitions, and the laws (whose morning line DDB-R7 already names). The two critics probed every premise on the boot and on 22 boards (16 measured, 6 hand-played). **Three templates pass every test and fire on real boards** (§6.1):
   - **the Arch-Chancellor's Letters** — the Emperor afield while his standing is spent;
   - **the Host's Claims** — corps quartered on an ally;
   - **Berthier's Memorial** — the Staff, offered at war, where DDB-R7 is silent.
2. **Ten more templates are written and wait on a mechanic the user may rule** (§6.2), so the catalogue holds thirteen:
   - **the Edicts** (three offers);
   - **three safe setters** (bread, the yearly class, fever);
   - **Imperial Governance** (the conquered provinces);
   - **a Papal province on the map** (the Holy See);
   - **EC-5b's leakage** (licences or burnings);
   - **a regrowth writer for a court's authority** (the courts' credit).
3. **Not a tax, and not the runaway brake.**
   - A France that holds its ground ends turn 30 with 41–47k gold on all three commanded seeds. The user's own ruling (IQ-1, September 13, 2026) is that such a France is *not* taxed: "the defect is not the size of the pile but that no decision touches it".
   - The scripted conqueror is already pulled down by the coalition: alarm 95–97 by turns 5–10, eclipsed by turns 30–34 on two of three seeds.
   - Gold cannot brake a France at war. At the war-time Charges rates (100–450), most of a gold answer comes back as lower Charges within ten to twenty turns. So the deck's brakes are priced in standing and the Emperor's administrative day.
4. **As a gold sink the core deck converts; it does not drain.** It takes at most about 1,800 gold an act beyond the Staff's own price. **The honest recurring sink is the Edicts** (§0 Q2): fixed-term decrees bought again and again, the era's own instrument. This spec recommends them in principle.

**How it was designed** (the S14c gate pattern; every subagent on Sonnet; the synthesis the orchestrator's own):
1. **Three read-only code maps:** the moments engine and its seams; the economy's sinks and brakes; the measuring tools.
2. **Two researchers with web access:**
   - comparable games — EU4, CK3, Victoria 3, HOI4, Total War, Civilization and the Napoleonic titles;
   - a sourced catalogue of 31 recurring pressures, 1805–1815.
3. **A fresh Mode A measurement** (§1): the three commanded arms; the Rhine road on three seeds; the treaty road; the ten-seed ambient sweep. Plus a read-only probe of the six hand-played DD-B saves (turn 21).
4. **Three designers:**
   - A, history first (twelve templates);
   - B, the player's experience first (twelve);
   - C, systems and economy first (twelve).
5. **Three judges.** Each lens picked its own designer's base (§18):

   | Judge | A | B | C |
   |---|---|---|---|
   | the historian | 44 | 35 | 28 |
   | the architect | 36 | 41 | 46 |
   | the playtester | 40 | 41 | 34 |

6. **A synthesis:**
   - from A, the voice and the sources;
   - from C, the engine and the arithmetic;
   - from B, the presentation (the Watch, the quiet card, the nondominance pin).
7. **Two adversarial critics.**
   - One probed the code and the 22 boards.
   - The other checked the rules, the rulings and the history.
   - Together they returned 37 corrections, eight of them blocking.
   - Their probes struck nine of the first draft's twelve templates (its T2, T4–T9, T11 and T12, in its own numbering): dead premises, dominated forks, map accidents, VP-1's strikes, A1's class. The deck below is what survived, renumbered T1–T3.
   - §18.3 records every correction and what was done with it.

**Reading map.**

| Section | What it holds |
|---|---|
| §0 | The questions for the user |
| §1 | Why, measured |
| §2 | What the game already has |
| §3 | What players value and resent |
| §4 | The record, 1805–1815 |
| §5 | The attribute block |
| §6 | The catalogue: §6.1 the three live templates; §6.2 the ten conditional ones; §6.3 the struck; §6.4 the reach table |
| §7 | Pacing |
| §8 | The courts |
| §9 | The engine |
| §10 | Seeds |
| §11 | Saves |
| §12 | The client |
| §13 | Rule 8 |
| §14 | Sizing |
| §15 | Placement |
| §16 | The build |
| §17 | Rule 9 |
| §18 | The record |

---

## §0 The gate — the questions for the user (◆ = the recommended default)

Answering at the defaults blesses §5–§16 as the build contract. Numbers marked as bands are in-band tunable after landing. A shape change — a new op, a new currency, a change to the lapse rule — re-escalates. Each answer is one block field or one constant, so the user may take any mix.

| # | Question | ◆ Recommended | The alternatives, and the historically fuller option with its cost |
|---|---|---|---|
| **Q1** | **What to build** | **(a)** The engine with the three live templates (§6.1), **and the Edicts' three offers** (§6.2 E1–E3) if Q2 rules the Edicts in: a small deck of the bills of the player's own acts, a door, and the offers that give a rich peace something real to buy. | **(b) The engine and the three live templates only.** A seasoning: two to four letters an act, converting at most about 1,800 gold an act. **(c) Hold RE** until a fuller option is ruled. Three letters do not repay the engine's four or five sessions, and that is the honest alternative. **(d) The full catalogue:** every §6.2 template, each with the mechanic it waits on (Q3). |
| **Q2** | **The gold-sink ask — the Edicts** | **Yes in principle.** An Edict is a fixed-term decree (eight turns, bought again after an eight-turn rest) on REFORMS §4's closed effect set. It costs gold and one administrative action, with no upkeep. France's three are those its laws do not already carry: **the Magazines** (supply capacity ×1.25), **the Remounts** (cavalry recruit price ×0.8) and **the Camps of Instruction** (drill morale +5). These are the era's own instruments: the magazines stocked before a campaign, the remounts after a winter, the camps of 1803–05 and 1807–08. They give the golden peace a recurring purchase with a real effect, and the affairs push each on the morning it is live. The Edicts' build contract is written at RE-6's head (DRAFT numbers here). | **No:** the deck stays a seasoning, and the laws' upkeep stays the only recurring drain. **Cost of yes:** a second lifecycle for an effect (a source that expires; structural by REFORMS §4, so it is put here); an AI rung at the same prices (GR5), which reopens EAD-6 for the courts' war chests; one more slice. |
| **Q3** | **The other fuller options** | **None now.** Each is named in §6.2 with its cost and the templates it would unlock. | **The domestic setters** — a signed war-exhaustion setter, a manpower credit that is not truncated at regen, a strength op — unlock the bread, the class and the fever. They reverse S14c §3.2 in three subsystems. **Imperial Governance** unlocks the conquered provinces with faces; it needs its own spec. **A Papal province on the map** unlocks the Holy See; it needs a map change and the reopening of VP-1's "Rome 1809" strike. **EC-5b's leakage with the Decree in force** unlocks licences or burnings; it needs EC-5b and the reopening of VP-1's "Trianon licences" strike. **A court's authority regrowth** (REFORMS §3) unlocks the courts' credit. |
| **Q4** | **Whose events — GR5, and S14c Q6** | **France's content, on code shared by every court.** Each template is a function of `(world, lord)`; the block's `scope` field names who meets it, as S14c Q6 kept for the moments ("an asymmetry of content, not of code"). v1 authors every template `owner`. | **(b) The Host's Claims for every court.** Measured: AI armies quarter on their allies (Russia on Austria, Spain on France). A court that will not pay gold (EAD-6) lives off the land, and its allies' relations fall. Those relations feed `coalition.get_coalition_friction`, and so the AI's co-location and joint-attack bonuses: **a court-run Host's Claims weakens coalitions and helps a runaway France.** It also has to hold AI Intent's soap-opera share (pin 13, measured at 0.91–0.98). |
| **Q5** | **EAD-6, the courts' hoard** | **Kept.** No court pays gold in an affair (moot under Q4's default). | The courts' Edicts (Q2) and a court-run deck would spend the measured 260–329k at turns 30–40. At war that strengthens the AI, a brake on France of the kind the user asked about; at peace it is inert. **Cost:** EAD-6 reopened, and the pinned series moves. |
| **Q6** | **The new ops** | **Two, each on an existing clamped setter.** **`authority`:** the player's `AuthorityTracker.modify_authority`. **Its floor is on the grip:** it never takes the grip below 71, so it never trips the Charges' +50 and never ends the marshals' calm at 70. It never raises a France already under the floor, and a template priced in it arrives only when the price bites (§5). **`admin`:** one of today's administrative actions (`use_admin_action`). | **Fuller: `tempo`** — one order of the day lost at the next refill (the treaty AP clause's body, already symmetric). It is the Emperor's real attention. **Cost:** two seams in `_advance_turn_internal`, which S17a moves, and a brake a campaigning player feels at once. **Struck:** `reconcile` (with its only template, §6.3). |
| **Q7** | **The alarm** | **Barred** from every affair by the validator. | **Fuller:** a dynastic match carrying "Europe's alarm +3", as M1 does. Struck (§6.3). |
| **Q8** | **How an affair arrives** | **Quietly:** a NORMAL rail card, pinned against the rail's 50-row eviction while it stands, and a mailbox row whose **Read the letter** button opens it. The campaign's first affair opens itself once, with its first-open line. **Cost:** the delivery must not write the popup slot; `main.py`'s safety valve must stop re-sending an affair; the readers that hard-code "A Moment of History" read the letter's register (RE-2). | **Modal, like the moments:** an interruption every few turns (Victoria 3 halved its notifications for this). **A dispatch row only:** no button, so the DD-B "unfound surface" again. |
| **Q9** | **Pacing** | **The moments are blind to affairs.** S14c's arrival turns are invariant by construction: the moments' pacing never reads an affair's row, and a standing affair is withdrawn free (nothing applied, its cooldown re-armed, one line) when a moment falls due. Affairs keep out of the moments' way: one open letter, a gap of 5 turns (band 4–7) from either deck's last arrival, the first no sooner than turn 7 (band 6–9), at most 6 an act, and a cooldown and a cap per template. | **Reserved seasons around each moment's window** (the first draft): exact only while a moment's premise is stable. The critic's re-run found Holland's letter slipping a turn when its premise flipped, the Bavarian Match lost, and the Crown moved. |
| **Q10** | **The seed** | **Timing only.** The premise, held for its streak, decides whether; the seeded gap decides when. There is no per-turn chance. `historical` collapses every band to its value, and the default campaign seed is `historical`. | **A per-morning chance** (design C; EU4's pulse): a die on the default seed, with a premise true on screen and no letter. |
| **Q11** | **The calendar** | **No template reads the season** (HC-0's never-do pin is kept). The bread of §6.2 keys to war and the blockade, never to autumn. | **Fuller:** a harvest letter in autumn. **Cost:** amending the pin outside the Seasons gate (HC-6). |
| **Q12** | **The Verdict and the continued reign** | **The deck runs on after the Verdict** (turn 44, "Continue the reign"), and its caps reset there: a second act. Half-month turns reach about mid-1809 by turn 88, the years of Spain and the Pope's arrest. | **Stop at the Verdict:** the second act meets nothing. |
| **Q13** | **A dial** | **None in v1.** The live deck is two to four letters an act; the free lapse, the quiet card and the caps are the player's control. | **A two-position "Affairs: Off / Standard" now** (designers A and B, judge 3). It re-opens on Round 1 evidence (§17). **Cost:** a setting that switches off a ruled system. |
| **Q14** | **Placement** | **After S15**, as a new row **RE**: RE-1 and RE-2 after S16 (the `main.gd` split), and ordered against S17c, which moves `main.py`'s routers and with them the safety valve RE-2 edits. RE-3 is measured on its own Mode A arms. Round 1 (ROADMAP row 16) is the deck's first meeting with players. | **Brought forward:** only RE-1 (the engine, unarmed and byte-identical) could ride before S15. |

### §0.1 What this gate does not reopen

- **S14c's rulings:** A1's three struck examples; the four moments, their windows, pacing and matrix cells (Q9 keeps them invariant by construction); S14c Q7's strikes (a marriage bond, AI-court marriages, R25's random quota).
- **The economy's rulings:** IQ-1's ruling (the golden peace is not taxed); EAD-2; EAD-6 by default (Q5).
- **VP-1's strikes "from every surface, not deferred":** "Rome 1809" and the Trianon licences (`VP1_DESIGNS_SPEC.md` §11). §6.2 names what reopening each would take; nothing here reopens them.
- **The standing rules:** HC-0's calendar pin (Q11); VP-1 Q6 (no dynasty store); "diplomacy is never typed"; GR6.

---

## §1 Why — measured on today's tree

**The measurement** (October 27, 2026, master `f33a8858`, after S14i). Mode A, in process, mock LLM, `PYTHONHASHSEED=0`, the runs kept in the session's scratch folder and not archived. Every figure is per seed: a seeded path, not a law.

**The hoarding France.** The three commanded arms hold the 1805 ground, recruit, accept diplomacy and never conquer.

| Arm (seed) | Chest T10 | T20 | T30 | T40 | Charges paid in 40 turns | Purchases recorded in 40 turns | Provinces |
|---|---|---|---|---|---|---|---|
| CMD-H (historical) | 5,207 | 21,029 | 47,404 | 42,980 (58,817 at T35, before a six-court war) | 39,815 | 1,261 | 27–29 |
| CMD-A (austerlitz) | 15,660 | 26,186 | 43,217 | 75,439 | 40,470 | 1,567 | 28–29 |
| CMD-M (marengo) | 11,268 | 27,611 | 41,814 | 49,704 | 54,315 | 927 | 28 |

- On all three seeds the chest passes 41,000 by T30 and the script buys almost nothing.
- Threat sits at the Armed Peace's watch line, 45, from T15–T20.
- France's gross income is about 2,400–2,800 a turn.

**The conquering France.** The Rhine road (VP1-RH) and the treaty road (REACH-AAR).

| Arm (seed) | The win | Chest peak | Provinces T10 / T20 / T30 / end | Alarm T5–T10 | End of the run |
|---|---|---|---|---|---|
| VP1-RH (historical) | the Decisive Peace on Austria, T13 | 20,167 (T25) | 28 / 28 / 20 / 20 | 97 | eclipsed at T34 |
| VP1-RH (austerlitz) | the Decisive Peace, T13 | 14,499 (T20) | 28 / 28 / 17 / 13 | 95–97 | T35, with 13 provinces and Switzerland in revolt |
| VP1-RH (marengo) | the Decisive Peace, T13 | 18,869 (T15) | 28 / 28 / 28 / 28 | 97 | eclipsed at T30 |
| REACH-AAR (historical) | the Treaty of Vienna, T9 | 44,893 (T40) | 29 / 24 / 22 / 22 | 76–81 | T40 |

- The scripted conqueror beats Austria at T9–T13 (Pressburg historically fell around T7), but it does not run away.
- The coalition breaks it on two of three Rhine-road seeds.

**The struggling France.** In the ambient sweep the passive France (ten seeds) has a median chest of:

| Turn | Median chest | Range |
|---|---|---|
| T10 | 8,652 | |
| T20 | 5,229 | |
| T30 | 2,990 | |
| T40 | 3,812 | −1,044 to 5,426 |

The passive France has no surplus.

**The courts' purses.** In the same sweep the courts' total chest has a median of 98,000 at T10, 189,000 at T20, 260,000 at T30 and 329,000 at T40. At T40 the Ottoman Empire holds 74,892, Sweden 34,382, Spain 32,905 and Denmark 28,080. EAD-6 (October 5, 2026) keeps this peaceful hoard inert by ruling.

**The hand-played boards** (a read-only probe of the six DD-B saves at turn 21, October 24–25, 2026; all on the `historical` seed):

| Road | Chest | Charges rate | Authority | Foreign provinces | Clients (loyalty) | Infantry pool | At war with | Laws in force |
|---|---|---|---|---|---|---|---|---|
| conquest, Oct 25 | 14,758 | 30 | 100 | 2 (Vienna, Hungary) | Holland 100, Italy 100, Switzerland 100 | 88,195 | — | the Staff (T11), the Train (T20) |
| diplomacy, Oct 25 | 22,609 | 30 | 85 | 0 | Holland 95, Italy 94, Switzerland 94, Bavaria 100, Hesse 73 | 100,000 | — | the Staff (T12), the Code (T12) |
| sea, Oct 25 | 5,694 | 612 | 85 | 2 (Ulster, Munster) | Holland 87, Switzerland 74 | 100,000 | Austria, Russia | — |
| conquest, Oct 24 | 6,081 | 322 | 95 | 1 (Vienna) | three at 100 | 60,732 | seven courts | the Staff (T9), the Train (T14) |
| diplomacy, Oct 24 | 20,770 | 30 | 85 | 0 | Holland 84, Italy 100, Switzerland 87 | 100,000 | — | the Code (T14) |
| sea, Oct 24 | 27,890 | 30 | 100 | 1 (Munster) | three at 92–97 | 100,000 | — | — |

Two facts follow from the six boards.

- **People reach the golden peace.** Four of the six sit at the golden-peace rate of 30 with chests of 15–28k by turn 21. Four of the six had found the laws.
- **People hold little ground.** Even the human conqueror holds only one or two foreign provinces at turn 21; the 1805 game settles its conquests at the table. A premise keyed to "four or more provinces held" is dead on every board here.

**The Charges' rebate depends on the rate.**
- **The levy.** The Charges of Empire take (chest − 2,000) × rate // 2,500 every turn (`world_state.py`: `WAR_EFFORT_DIVISOR`, `get_state_charges_rate`, `charges_relief`).
- **The rate** = war exhaustion + 30 (the crown) + 50 (at war) + 75 (a war going ill) + 75 (a restless interior) + 50 (grip under 70) + min(150, fallen // 750) + 25 for each tier of a refused dictated peace.
- **The effect on a sink.** A chest lowered by S pays S × rate ÷ 2,500 less on every later turn, so the gap a sink leaves shrinks by (1 − rate ÷ 2,500) each turn. The half-life of a sink:

| Rate | Half-life |
|---|---|
| 28 | 61 turns |
| 80 | 21 |
| 176 | 9.5 |
| 240 | 7 |
| 340 | 4.7 |
| 450 | 3.5 |

The rate implied on today's arms (the Charges applied ÷ ((chest − 2,000) ÷ 2,500)):

| Arm | T10 | T20 | T30 | T40 |
|---|---|---|---|---|
| CMD-H | 274 | 26 | 28 | 342 |
| CMD-A | 170 | 239 | 28 | 29 |
| CMD-M | 118 | 100 | 176 | 76 |
| VP1-RH (historical) | | 251 | 449 (T25) | |

- **The hoarding France reaches the golden peace by T20–T30 on two of three seeds.** There a gold answer is a real purchase: about 89% of it is still missing from the chest ten turns later.
- **A France at war pays rates of 100–450.** There a gold answer comes back as lower Charges. A 2,500-gold answer taken at T15 on the Rhine road leaves 511 or 127 gold of difference in the chest by T30, at the measured rates of 251 and 449 (2,500 × (1 − rate ÷ 2,500)^15; the repo critic's check).
- **So gold cannot brake a warring, conquering France.**

**Authority, the deck's other currency.** The player's grip is his authority, less the territorial terms (`authority.get_imperial_grip`). Its teeth sit at fixed lines:
- **85:** the aura of invincibility is full at grip 85 and fades to nothing at 30 (`AURA_GRIP_FULL`, `sovereign_aura_strength`). It drives both the combat aura and the enemy's fear.
- **80:** the strong-leader defiance bonus needs authority 80 or more.
- **70:** "Whispers of Weakness"; the jealousy calm ends; under 70 the grip term adds +50 to the Charges' rate.
- **60 and 30:** each moves a diplomatic point a turn.

**How authority behaves on these boards.**
- A winning France sits at 100 and wins authority back in battle (+2 or +5). Authority between 100 and 85 is a reserve; between 85 and 70 it costs the aura and the defiance bonus.
- **The Charges and the aura read the grip, not the raw authority.** The grip is authority less 40 for a lost capital, 25 for a homeland minority, and 8 or 15 for a losing war. The October 25 sea road shows the gap: authority 85, grip 52.
- **The deck's floor is therefore on the grip, at 71.** It never trips the Charges' +50, and the marshals' calm, which holds only above 70, survives.
- **A template priced in authority arrives only where its price bites** (§5): not at 100, where the unbroken Emperor's standing carries the Council, and not under the floor. The conquering arms end at authority 35–50 and grip 17–50, where no authority-priced letter comes.

**What the rulings already settled.**
- **The user, August 7, 2026:** *"economy shouldn't go crazy unless you are doing very well and stable."* The econ gate implemented it as the golden peace, "effectively unbounded — allowed, that is the blessing" (`docs/audits/ECON_BALANCE_GATE_2026_08_07.md`).
- **IQ-1 §0.2, September 13, 2026:** the blessed rate stands; *"the defect is not the size of the pile but that no decision touches it. So IQ-1 does not tax a winning, peaceful, stable France."*
- **SRX-D1:** "a golden peace may grow rich".
- **ES-4, struck September 28, 2026:** "the peacetime sink it was held for now exists".
- **EAD-2, October 5, 2026:** the Charges were made legible (`charges_relief`); a sink should buy "something the Charges cannot reach".
- **DDB-R7:** the morning dispatch already names the next affordable gold law or Act on a peaceful morning (`reforms.peace_sink_line`, `imperial_designs.act_sink_line`). It is silent at war (`peace_sink_law` returns None at war or truce).
- **S14c's M4** is the precedent for a letter as **a second door** to an existing verb: kept because LAWS had been opened 0 times, and arriving only when the law bites.

So the deck is not a tax. **It brings decisions to the board where the player's own acts have made them due, and it opens three doors where a law would bite.**

---

## §2 What the game already has — the map no template may double

| A pressure a recurring event might model | The surface that already covers it | So no template may… |
|---|---|---|
| A treasury levy, a forced loan, a wealth tax | the Charges of Empire | take a share of the chest, or price by the chest |
| Europe's fear of France | the coalition alarm: at least sixteen producers (battles +3/+5, capitals +15, provinces +2, declarations +20/+10, annexation +8 a province, a conquest vassal +25, ultimatums 5–25, holding over 30/40/50% of the provinces, the bloc share, an army over a third of Europe's men), and the Armed Peace's watch at 45 | add alarm (the validator bars the op) |
| Unrest, brigands, partisans in a held province | stability (+5 a turn, +5 more with a marshal or garrison; −2 under a hostile army; −10 a battle); occupation upkeep (0.50 → 0.10 of base income); contributions; the Charges' restless term (+75) | sell a province's calm (A1: stability heals itself, so the purchase is fake) |
| Disease and desertion | supply attrition (up to 6% a turn), bankruptcy desertion (5% a marshal after three deficits), a losing lead's mortality | kill men |
| Conscription's limits | the pool caps; the war-exhaustion regen cut; the levy's ceiling, scarcity and alarm price; the Anticipated Class | sell men for gold (the substitutes market does) |
| Prestige | the Temple of Glory (8,000 gold → +15 authority, once); the laws' authority prices | sell authority for gold |
| A marshal's reward | ES-7's dotations and rentes (an expectation of 40 a battle won, capped at 300; trust erodes when unmet) | pay a marshal |
| A marshal's quarrel | jealousy's petition channel | stage a quarrel (A1) |
| A court's overture | the AI ladder's asks | stage an overture (A1) |
| A client's loyalty | vassal drift (−4 / −2 / +1 by autonomy, garrison +2, shared war +2, wins and losses, relation // 20); the `invest` verb (200 gold + 1 DP → +10 loyalty, cooldown 3); rebellion at 0; VS-4's petitions | sell loyalty for gold at the `invest` verb's own rate |
| The Emperor away from Paris | the Seat (+1 DP only while the sovereign holds court in his own capital) | charge DP for absence |
| The System's leaks | the ×0.4 trade floor; **EC-5b smuggling**, a named, unbuilt sub-slice (`docs/ECONOMY_REVISIT_SPEC.md`) | build EC-5b's leakage mechanic here |
| Diplomatic goodwill with one court | the DP missions, Improve Relations, Make Amends (200 gold + 1 DP) | sell one court's goodwill for gold or DP alone |

**The currencies with a safe setter today** are the moments' closed op table:
- `gold` — a purchase, through `instruments.chest_of` for the player and `instruments.purse_of` for any court;
- `dp`, `relation`, `loyalty` (`vassal.adjust_loyalty`), `autonomy` (`vassal.autonomy_change_plan` and `change_vassal_autonomy`), and `enact_law` (the full verb).

**Proposed here**, each on an existing clamped setter:
- `authority` — `AuthorityTracker.modify_authority` for the player, floored on the grip. `diplomacy.modify_nation_authority`, the court's setter, has zero production callers and is not used: a court's authority never regrows.
- `admin` — `use_admin_action`.

**No safe setter, so out:** stability, war exhaustion, manpower, war score, glory. Trust has a per-marshal clamped setter and no roster-wide helper.

**The DP trap.** France sits at or near its cap of 7 diplomatic points from turn 4 on every measured board (6–7 on all sixteen measured saves). A DP price is close to free for France, so no template's fork rests on DP alone.

---

## §3 What players value and resent — the research

The full table is the researcher's, sourced to Paradox dev diaries, wikis, reviews and forum threads; items marked † were seen only as search snippets. The lines that bind this deck:

- **Repetition is the first complaint.** CK3's random events recycled "a small set of 20 or 30"†; Imperator's roughly 100 events were seen a dozen times†; Old World's common events repeat. CK3 fixed it with a first-class per-event cooldown (patch 1.5) and once-a-generation events. **→ Each template has a cooldown per court and a cap per act, and up to three record variants keyed to a board fact.**
- **Spam while busy.** CK3's war and travel interruptions; its developers avoided battlefield events as a nuisance†. **→ No affair while a war crisis is foregrounded (R1, kept from the moments), and a quiet arrival.**
- **Randomness without counterplay** (Total War: Pharaoh's Sea Peoples, "a repetitive, arbitrary kick in the teeth"; EU4's "−1 stability event fiesta"†) **and invisible triggers** (old EU4 chains; Stellaris; Victoria 3's own diary). **→ Every template is the bill of the player's own act; no die decides it; its premise is on screen before the letter (the Watch).**
- **Dominated or hidden-downside answers** (EU4's Neapolitan Succession; Imperator's "objectively correct" answers†). **→ Two answers in different currencies, the lapse named and priced like a third answer, every figure quoted before the choice (shown = applied), and a nondominance pin on three boards.**
- **Flat costs that evaporate** (Warhammer II's dilemmas, crippling early and ignorable late) **and hoards with nothing to buy** (EU4's ducats). **→ Prices scale with the act (corps parked, provinces held), never with the chest; the gold answers sit where gold is real.**
- **Demands after success** (EU4's estates, "a chore after a hard-won war"†) **and rubber-banding** (the blue shell; Civ VI's pile-ons). **→ Brake on acts, not rank; never punish winning as such; a floor that never piles onto a failing France.**
- **What players value:**
  - premises visible before the event (EU4's disasters tab; Victoria 3's inactive journal entries);
  - pull beside push (HOI4's decisions; CK3's opt-in court events);
  - truthful previews (Age of Wonders 4 shows every effect);
  - counterplay on a brake (Stellaris' switchable approaches);
  - a dial (Civ VI's intensity; Civ VII's Crisis Picker);
  - varied repeatables (Hold Court; King of Dragon Pass);
  - the same rules for everyone (Age of Wonders 4 runs its events for the AI; Victoria 3's Opium Wars can break out anywhere).
- **Paradox's own path away from spam,** in order: EU4 1.9's disasters made causes visible; HOI4's 2017 decisions offered a pull channel; CK3 1.5 added an engine cooldown and opt-in court events; Victoria 3 moved to journal entries and halved its notifications; EU5 routes each message to the log or a popup.

---

## §4 The record, 1805–1815 — what history makes recurring

The history researcher's sourced catalogue holds 31 entries; this table maps them to the deck. Its sources include:
- Forrest, *Conscripts and Deserters* (1989); Woloch, "Napoleonic Conscription" (*Past & Present* 111, 1986); Rouanet & Piano, "Drafting the Great Army" (*JEH* 83, 2023);
- Broers, *Napoleon's Other War* (2010); Esdaile, *Fighting Napoleon* (2004);
- Branda, *Le prix de la gloire* (2007); Crouzet (*JEH* 24, 1964); Heckscher, *The Continental System* (1922); Ellis, *Napoleon's Continental Blockade* (1981);
- Sherwig, *Guineas and Gunpowder* (1969); Bergeron, *France under Napoleon* (1981); Lieven, *Russia against Napoleon* (2009);
- the Fondation Napoléon's *Revue du Souvenir Napoléonien*.

The historian judge and the rules-and-history critic rechecked the figures quoted in §6 on the web.

| Pressure (research entry) | Years; recurrence | The recorded fork | In this catalogue |
|---|---|---|---|
| The Emperor governing from camp; plots in his absence (#15) | 1805–12; each campaign | delegate to the Council, or govern by courier. In August 1809 Napoleon rebuked Cambacérès for making so little use of the powers he had left him; Malet's forgery took Paris for a morning, 23 October 1812. | **T1 The Arch-Chancellor's Letters** (live) |
| Quartering: "war must feed war" (#6) | each campaign | pay the claims, or live off the land. The rule: Napoleon to Soult, 14 July 1810. | **T2 The Host's Claims** (live) |
| The laws of the army (the Staff) | 1805–07 | enact or wait | **T3 Berthier's Memorial** (live, at war) |
| The magazines, the remounts, the camps of instruction | each campaign; each peace | decree them for a term, or not | **E1–E3, the Edicts** (Q2; citations owed before arming) |
| Bread and the maximum (#1); the class and the réfractaires (#2–#3); fever in the camps (#13) | 1805–13 | buy grain or fix the price; columns or amnesty; ambulances or not | **D1–D3** (Q3: each needs a setter the game lacks) |
| Conquered lands: Calabria, the Tyrol, Spain (#4–#6) | 1806–14; chronic | terror or amnesty | **G1** (Q3: Imperial Governance; A1 struck the class) |
| The Papacy (#16) | 1805–13; escalating | negotiate, or coerce: Ancona held from November 1805; to Pius VII, 13 February 1806, "You are sovereign in Rome, but I am its Emperor"; Rome annexed 1809 | **P1** (Q3: a Papal province beyond Rome; VP-1 struck "Rome 1809") |
| Contraband: licences against burnings (#7) | 1809–10; waves | sell licences (1809), or burn the cargoes (the Fontainebleau decree, 18–19 October 1810) | **S1** (Q3: EC-5b's leakage; VP-1 struck the Trianon licences) |
| Credit and paper money (#9, #22, #25, #27, #28) | each long war | cap the redemptions, or pay in paper. In autumn 1805 the Bank of France held 782,000 francs against 68 million in obligations; Austrian paper stood at 489 for 100 by 1810. | **C1** (Q3: a court's authority regrowth) |
| The satellites' leakage; the clients' constitutions (#8) | 1806–10; chronic | tolerate, or impose. The treaty of 16 March 1810 put French customs men in every Dutch port, and the kingdom was incorporated on 9 July 1810. The constitutions (Westphalia 15 November 1807, Warsaw 22 July 1807) bound the new states to France. | **struck** — the autonomy chips, VS-4's petitions and M2 cover it (§6.3) |
| The Protector's arbitration | 1806–13 | — | **struck** — the Act of 12 July 1806 gave the members' disputes to a Diet that never met (§6.3) |
| Vaccination, indirect taxes, income tax, the Luddites, the Regency, the Janissaries, Sweden's coup, Denmark's bankruptcy (#11, #14, #19–#24, #29–#31) | various | various | **struck** — no player agency, or another court's domestic history |
| Dotations, honours, monuments (#12, #17) | after victories | reward in land or cash; build or save | **struck** — ES-7 and the Temple of Glory cover them |
| Indemnities, subsidies, the Krümper system, Russia's reopening (#18, #21, #26, #27) | | | **struck** — the settlement table, the instruments, the AI intent ladder |
| The marriages (Bavaria 1806; the three-bride council of 21 Jan 1810) | one-off | | **struck** — M1 already, and VP-1 Q6 / S14c Q7 struck a dynasty store and marriage bonds |

**The register:**
- **The record line.** Every template's record is written in the moments' past-tense "Historically …" frame. A future fact is allowed and marked as history (the Throne of Holland's record already cites 1810).
- **The voice.** Office first. A name is used only where the man held the office throughout the reachable years: Cambacérès; Berthier; Montgelas for Bavaria. Otherwise a display-only table keyed to the turn names the holder (§12), for example the Treasury's Barbé-Marbois until January 1806 (about T9), then Mollien. A displayed name is display; no mechanic reads the calendar.

---

## §5 The attribute block

**Where it lives.**
- **The authored deck** lives in `europe_1805.json` inside the existing `moments` key, as `moments.affairs`. At boot `from_block` copies every authored key into `world.moments["block"]`, so the deck lands at `block.affairs`, which `store_from_data` already deep-copies: no new line is needed for the deck.
- **The runtime state** lives in `world.moments["affairs"]` and needs one line in `store_from_data` (§11): the streaks, the act counter, and the courts' rows if Q4(b) is ever ruled.
- **Validation:** a new `_validate_affairs` beside `_validate_moments`.
- **No block means unarmed:** the tutorial, the bare flag world and the legacy rollback.

```
"affairs": {
  "pacing": { "first": {"value": 7, "band": [6, 9]},
              "gap":   {"value": 5, "band": [4, 7]},
              "cap_act": 6, "wait": 4 },
  "deck":   [ { ...one template... }, … ]
}
```

| Field | Type, bounds | Default | Validator |
|---|---|---|---|
| `id` | str ≤ 32, `[a-z_]+` | — | unique across the affairs, the moments and the laws; `#` and `@` reserved (an occurrence is `id#n`) |
| `kind` / `shape` | `"affair"` / `bill` · `door` · `offer` | — | a `door` carries exactly one `enact_law` on Accept and an empty Decline; an `offer` (the Edicts) an empty Decline |
| `title`, `record` or `variants[]`, `watch` | ≤ 40; ≤ 240 each, up to 3 variants keyed to a board fact; ≤ 120 | — | **`watch` required** (a format string over the premise's own measure, worded "may", never "will"); every record in the moments' "Historically …" frame |
| `source` | non-empty: a research entry, a dated decree, or a repo doc | — | **a template without one cannot be armed** (an ERROR in the shipped block) |
| `scope` | `owner` · `any_lord` | `owner` | v1 authors `owner` only (Q4) |
| `roads` | as the moments | `["any"]` | as the moments |
| `when`, `streak` | `{predicate, params}`; 1–12 mornings | streak 1 | the predicate and its params named in code (`affairs.PREDICATES`) |
| `bites` | for a template priced in `authority`: the price must bite (below) | required with `authority` | — |
| `cooldown`, `cap` | 6–30 turns per subject per template; 1–4 per subject per act | 12; 2 | `cooldown ≥ pacing.gap` |
| `scale` | `{measure, from, step, max ≤ 3}` → a tier multiplying the listed amounts, or `{measure, at, then}` → one step at a threshold | none | the tiered amount within `AFFAIR_OP_BOUNDS` |
| `voice` | `{speaker: named · office · host, name?}`, with optional turn-keyed holders (§12) | — | a `named` voice ≤ 80 characters; each holder's turn checked against `calendar.turn_for_date` (validator only) |
| `accept`, `decline` | `{caption ≤ 36, ops[]}` | — | the op rules below |

**The op rules.**
- **The table.** The ops are the moments' closed table plus two proposed ones, `authority` and `admin`.
- **Selectors.** Each op takes its subject: `$lord`, or the premise's bound `$host`.
- **Bounds** (`AFFAIR_OP_BOUNDS`):

| Op | Bounds |
|---|---|
| `gold` | 1–2,000 after the tier, except the door's law price |
| `authority` | −10 to 0 |
| `admin` | 1 |
| `dp` | 1–2 |
| `relation`, `loyalty` | ±20 |
| `enact_law` | one of the owner's laws |

- **No `alarm` op in any affair**, and no VP-1 source.
- **A Decline carries only** `relation`, `loyalty` and a grip-floored `authority`. It never carries `gold`, `dp`, `admin`, `autonomy` or `enact_law`.
- **The occurrence is frozen at delivery.** `{lord, bind, tier}` is written into the occurrence's `state` row; ints and short strings only. `plan(world, e, answer, occ)` reads that row, so "the_host#2 = Bavaria, tier 2" survives a save, a premise that changes, and the lapse two turns later (critic 1, C6).
- **The `authority` op, exactly.**
  - The floor is on the grip, which is what the Charges and the aura read (`authority.get_imperial_grip`: authority less 40 for a lost capital, 25 for a homeland minority, 8 or 15 for a losing war). The floor is 71, so the marshals' calm, which holds only above 70 (`reforms.CALM_ABOVE`), survives.
  - On a negative delta, the delivered loss is `min(|delta|, max(0, grip − 71))`. It is never more, and never a rise.
  - The plan line prints `reforms.authority_line(before, after)` and `ledger.charges_grip_clause`, the two lines the laws' authority prices already print.
- **`bites`.** A template priced in `authority` arrives only when its Decline's loss would land below 85, the aura's full line (`AURA_GRIP_FULL`), **and** the floor allows the whole loss. Otherwise its Watch line says the Council acts for the Emperor, and no letter comes. An unbroken Emperor's standing carries the Council; a France already failing is never fined (critics 1 and 2, C4 and C13).
- **The `admin` op.** It spends one of today's administrative actions (`world.use_admin_action(1)`). With none left, the Accept is greyed: "the day's administration is already spoken for".

---

## §6 The catalogue — thirteen templates: three live, ten waiting on a ruling

**Shared by every template:**
- **The letter.** It stands two player turns, with a grace of 2; every quote is `plan()`'s own (shown = applied).
- **The lapse.** It is the Decline, which may not charge a purse or take a decision; its price is printed before the choice and at the end-turn gate.
- **The test.** No template adds alarm, moves stability, touches manpower, taxes the chest, pays a marshal or stages A1's three.
- **Reach.** Each reach figure is the repo critic's probe of the boot and 22 boards (§6.4): seeded paths, not laws.

### §6.1 The three live templates

**T1 `chancellors_letters` — The Arch-Chancellor's Letters** · bill · `owner`
- **Source:** research #15. In August 1809 the Emperor rebuked Cambacérès for making so little use of the powers he had left him (Fondation Napoléon, "Walcheren et l'affaire Fouché"). Malet's forged dispatch took Paris for a morning (23 October 1812).
- **Premise:** `sovereign_afield` — the lord's standing sovereign (`fall.sovereign_of`, never a captive) stands outside its homeland (`nation_starting_regions`), streak 6 — **and `bites`**.
- **Reach:**
  - **With `bites`:** CMD-H's four measured saves (authority 80, the Emperor in Swabia) and the October 25 diplomacy road (authority 85, Franconia).
  - **Without it:** 15 of 22 boards.
  - **It never arrives at 100** (CMD-A, CMD-M: the unbroken Emperor) **or under the floor** (the Rhine-road finals, authority 35–50).
- **Frequency:** cooldown 10, cap 2 an act.
- **Scale:** −5; −8 once afield 12 mornings running.
- **Face:** Cambacérès, Arch-Chancellor of the Empire (named; in office throughout).
- **Record:** "Historically the Emperor governed from his camp, and in August 1809 he rebuked Cambacérès for making so little use of the powers he had left him."
- **Watch:** "The Emperor afield: {n} of 6 mornings — Cambacérès may write."
- **Accept, "Dictate from the field":** `admin` 1.
- **Decline, "Let the Council act":** `authority` −5, or −8 once afield 12 mornings; grip-floored at 71.
- **Not a double:** the Seat prices absence in DP (+1 only in his capital); the thresholds and the grip price damage done; nothing asks for the Emperor's attention.
- **Each answer the better one somewhere:**
  - An idle administration — an unused action earns 25 gold — takes the Accept.
  - A France that drafts or decrees every morning, with standing to spare above 80, takes the Decline.
  - Across the 85 line the Decline costs the aura; across 80, the strong-leader bonus.

**T2 `the_host` — The Host's Claims** · bill · `owner`
- **Source:** research #6. Napoleon to Soult, 14 July 1810: "war must feed war" (Fondation Napoléon; Branda, *Le prix de la gloire*).
- **Premise:** `corps_on_host` — three or more of the lord's corps, the sovereign not counted, stand on the soil of an ally (ALLIANCE or DEFENSIVE_ALLIANCE) or a client, streak 3. One host per letter: the one with the most corps, ties by authored order.
- **Reach:** 11 of 16 measured (Bavaria from the opening, with 3–7 corps; the Kingdom of Italy on two CMD saves) and 0 of 6 hand-played.
- **Scale:** tier = 1 + (corps − 3) // 2, at most 3.
- **Frequency:** cooldown 10 per host, cap 2 per host an act.
- **Face:** the host's first minister (Bavaria: Montgelas, minister 1799–1817); a client's head; otherwise the host's chancery.
- **Record:** "Historically the Emperor's rule was that war must feed war (to Soult, 14 July 1810): a corps lived on the country it stood in."
- **Watch:** "{n} corps on {host}'s soil: {m} of 3 mornings — its court may present its claims."
- **Accept, "Pay the host's claims":** `gold` 300 × tier.
- **Decline, "Live off the land":** the host −2 × tier; for a client host, its loyalty −2 × tier.
- **The plan line prints the host's distance to the alliance's downgrade** (`STATE_RELATION_THRESHOLDS`: an alliance at relation 10 or less for five turns steps down). Friends cool a point a turn above +10 and never heal (`relation_drift_step`). The measured Bavaria drifts 46 → 18 → 10 → 2 on CMD-H with no Decline at all, so a Decline brings the downgrade nearer, and the player sees by how much. A vassal–lord pair does not drift, so a client's loss stands until drift, a garrison or `invest` moves its loyalty.
- **Not a double:** supply attrition and campaign pay cost men and gold; France's doctrine flaw "living off the land" prices supply; Improve Relations warms a court and never prices the cause. Nothing bills the host's own goodwill.
- **Each answer the better one somewhere:**
  - A France at war or at the golden peace pays (at war the gold mostly comes back as lower Charges).
  - A tight chest, with the host far from its line, bears.

**T3 `berthiers_memorial` — Berthier's Memorial** · door · `owner`
- **Source:** Berthier, Major-General of the Grande Armée from 1805; the law's own record, "Berthier's Imperial Headquarters, expanded 1805–07" (`REFORMS_SPEC.md` §6).
- **Premise:**
  - at war four turns running;
  - the Staff (`grand_quartier_general`) not in force, with `reforms.law_refusal` open;
  - the purse (`instruments.purse_of(world, lord)[1]`) at or above the price plus `AI_PURSE_RESERVE` plus `AI_PURSE_UPKEEP_TURNS` × upkeep — one source with the AI's own law rung.
- **Reach:** 5 of 16 measured (CMD-A T10, CMD-H T40, CMD-M T30, two Rhine-road finals) and 0 of 6 hand-played. Three of those roads had already enacted the Staff; the others were at peace or short of the bar.
- **Frequency:** cooldown 14, cap 2 an act.
- **Face:** Berthier (named).
- **Record:** "Historically Berthier's Imperial Headquarters grew with every campaign from 1805 into the staff that carried the Emperor's orders."
- **Watch:** "At war {n} of 4 turns, and the chest could found the headquarters — Berthier may write."
- **Accept, "Found the headquarters":** `enact_law` grand_quartier_general — 9,000 gold, 300 a turn and one administrative action, for one more order a day. The quote is `reforms.terms_line`, plus `world.charges_relief`: "at today's rate the Charges would ease by N a turn".
- **Decline, "Not now":** nothing.
- **Not a double:**
  - DDB-R7's morning line names the next affordable gold law only at peace (`peace_sink_law` returns None at war or truce); this is the war's door, S14c M4's precedent.
  - It never arrives once the Staff is in force.
  - At war the price mostly comes back as lower Charges: the door turns taxed gold into an order of the day.

### §6.2 The ten conditional templates — each waits on one ruling (§0 Q2, Q3)

Each is written to the same block. It is armed only when its ruling lands, and it is struck if the ruling is refused. Numbers are DRAFT.

| # | Template | Waits on | Source | Premise | Accept | Decline (= the lapse) | Why the ruling is needed |
|---|---|---|---|---|---|---|---|
| E1 | `the_magazines` — The Magazines (offer) | **the Edicts** (Q2) | the campaign magazines (citation owed before arming) | a war-intent against the lord foregrounded (`war_council.foreground_in_tenure`), or at war with a corps drawing campaign pay | edict: supply capacity ×1.25 for 8 turns — 2,500 gold, 1 admin | nothing | an effect that expires is a second lifecycle (REFORMS §4) |
| E2 | `the_remounts` — The Remounts (offer) | the Edicts | the remount purchases after the winter campaigns (citation owed) | cavalry pool below 60% of its cap | edict: cavalry recruit price ×0.8 for 8 turns — 1,500 gold, 1 admin | nothing | as E1 |
| E3 | `camps_of_instruction` — The Camps of Instruction (offer) | the Edicts | the camps of Boulogne, 1803–05 (citation owed) | at peace with every great power six turns, the Charges at the golden peace (rate ≤ 60) | edict: drill morale +5 for 8 turns — 2,000 gold, 1 admin | nothing | as E1. **The golden peace's recurring purchase** — the decision IQ-1 asked to touch the pile |
| D1 | `price_of_bread` — The Price of Bread (bill) | a signed war-exhaustion setter (Q3) | research #1: the 1811–12 crisis; the maximum of May 1812; Rumford soup | at war eight turns while a blockade cuts the lord's trade (`naval.blockade_trade_loss`); never the season (Q11) | "Buy grain abroad": gold 1,500 | "Fix the maximum": war exhaustion +6 | war exhaustion has no signed setter (S14c §3.2) |
| D2 | `the_refractaires` — The Réfractaires (bill) | a manpower credit not truncated at regen (Q3) | research #2: the garnisaires and the mobile columns; the 1810 amnesty | the infantry pool below 50% of its cap within four turns of a levy | "Send the mobile columns": admin 1, authority −3 (grip-floored), infantry +5,000 | "Let the class be short": nothing | manpower is truncated at the next regen (S14c §3.2); and no measured or hand-played pool falls below 60% |
| D3 | `fever_in_the_camps` — Fever in the Camps (bill) | a strength op (Q3) | research #13: Walcheren 1809; typhus 1812–13; Larrey and Percy | a corps on poor or stripped country (`doctrines.corps_drawing_now`) for three mornings | "Larrey's ambulances": gold 800 | "Let the surgeons cope": that corps −4% of its men | no op removes men safely; supply attrition is the only writer |
| G1 | `conquered_provinces` — The Conquered Provinces (bill) | **Imperial Governance** (Q3) | research #4–#6: Calabria 1806–11; the Tyrol 1809; Spain | two or more provinces held outside the 1805 homeland for six mornings; the dispossessed by `game_end.home_nation_of` | a governor's answer with a marshal's face | — | A1 struck the class (the capture choice covers a province's fate); its home is Imperial Governance (`FUTURE_DESIGN.md`) |
| P1 | `the_holy_see` — The Holy See (bill) | **a Papal province beyond Rome on the map, and the reopening of VP-1's "Rome 1809"** (Q3) | research #16: Ancona from November 1805; to Pius VII, 13 February 1806: "You are sovereign in Rome, but I am its Emperor" (napoleon.org's wording) | a French corps on Papal soil other than Rome | "Offer a Concordat clause": gold 800, DP 1; the Papal States +10; each Catholic court (Austria, Spain, Portugal, Naples, Bavaria, Sardinia) +2 | "Press the occupation": the Papal States −10; each Catholic court −3 | the map's only Papal province is Rome; a corps there ends the court, and its neighbour Piedmont is France's client's (the critics' probe) |
| S1 | `licences_or_burnings` — Licences or Burnings (bill) | **EC-5b's leakage with the Decree in force, and the reopening of VP-1's "Trianon licences"** (Q3) | research #7: licences from 1809; the Trianon tariff (5 August 1810); the Fontainebleau decree and its bonfires (18–19 October 1810) | the Berlin Decree in force six turns and a client's ports counted in the closure | "Burn the cargoes": admin 1; each counted client −3; the closure held | "Grant licences": the closure leaks through EC-5b's term; authority −4 (grip-floored) | without the leak the Accept buys nothing (dominated, critics 1 and 2); the Decree is in force on none of the 22 boards |
| C1 | `paper_and_credit` — Paper and Credit, every court (bill) | **a regrowth writer for a court's authority** (Q3) | research #9, #22, #25, #27, #28 (the Bank of France held 782,000 francs against 68 million in obligations, autumn 1805; Austrian paper at 489 for 100 by 1810) | at war eight turns with a purse at or under 1,000 | "Cap the redemptions": DP 1, admin 1 (France) | "Pay in paper": authority −5 (grip-floored) | France meets it on 0 of 22 boards; a court's authority never regrows, so one bill would strip it for good. Inert narration would be a placeholder (GR9; AI Intent pin 11) |

### §6.3 Struck — every candidate the gate weighed, beside the surface that covers it

| Candidate (designer) | Struck because | Covering surface |
|---|---|---|
| The client's letter; a constitution (A, B, C) | 0 of 22 boards (the clients sit at 73–100; the "falling" clause never holds with the threshold); the Accept is the live autonomy chip; "Grant a constitution" inverts the record (the constitutions bound Westphalia and Warsaw to France) | the Vassals card's autonomy chips; VS-4 petitions; M2 (the dated case); R25's random quota stays struck (S14c Q7) |
| The customs of the coast (B) | 0 of 22; the autonomy chip reversed on a timer | the autonomy chips; M4 |
| The Protector's arbitration (C) | the Act of 12 July 1806 (Art. 9) gives the members' disputes to a Diet that never met, so the framing contradicts its source; the premise is the resting floor of any cool pair; a court-run version moves coalition friction | the 1810 border treaties were redistributions, not arbitrations; no surface needed |
| The Train's door; the Code's door (A, B, C) | 0 of 22: `corps_drawing_now` is 0 on every board, even with the Staff in force; the Code's two clauses are anti-correlated (slipping clients follow a low grip, the Code needs authority ≥ 85) | the LAWS tab; DDB-R7's peace line; the doctrines' cure |
| The Anticipated Class's door; the Artillery Reserve's door (A, B, C) | no board drains the pool (60,700–100,000 of 100,000); no artillery corps on any board | LAWS; the levy's price |
| The Bulletin of the Army (C) | 1,500 gold for +3 authority: a Temple double, and a winner sits at 100 | the Temple of Glory |
| The matches — the house match, the Imperial match, the three-bride council (A; judge 1) | M1 is the match; VP-1 Q6 struck a dynasty store; S14c Q7 struck AI-court marriages and a marriage bond; the council is a one-off moment, not a recurrence | M1 |
| Two Embassies (B) | dead on every board (no great-power pair at ≥ 30 with France and ≤ 0 with each other); no recorded fork | courtship missions |
| The echoes (B) | a second-order state for what a tier already does | the Host's Claims' tiers |
| The Secretariat's bill; the Council of State (B, C) | no recorded fork; the administrative budget is itself the price | T1's `admin` answer |
| An ally grown cold (the orchestrator's) | a free answer exists: Improve Relations costs DP, and France sits at 6–7 | D5's sliding-ally warning; Improve Relations |
| The calm and pressed forms (B) | two prices per answer, re-derived from the Charges rate at every read | the rebate said aloud on the gold line (§12) |
| A1's three (S14c) | ruled | jealousy's petitions; stability and the capture choice; the AI ladder's asks |

### §6.4 The reach table (critic 1's probe; France as owner; streaks ignored)

| Board | T1 (with `bites`) | T2 | T3 |
|---|---|---|---|
| boot, turn 1 | — (home, Lorraine) | — | — |
| CMD-H T10 / T20 / T30 / T40 | Y / Y / Y / Y (authority 80, Swabia) | Y (Bavaria, 5) / Y (7) / Y (7) / — | — / — / — / Y |
| CMD-A T10 / T20 / T30 / T40 | — (authority 100) | Y / Y (Kingdom of Italy, 4) / Y / Y | Y / — / — / — |
| CMD-M T10 / T20 / T30 / T40 | — (100; then at home) | Y / Y / — / — | — / — / Y / — |
| REACH-AAR, last | — (Paris) | Y (Bavaria, 6) | — |
| VP1-RH historical / austerlitz / marengo, finals | — (authority 35 / 50 / 45: under the floor) | Y / — / — | Y / — / Y |
| Hand-played, Oct 25: conquest / diplomacy / sea | — / Y (85, Franconia) / — | — / — (counting the Emperor only) / — | — (the Staff in force) / — / — |
| Hand-played, Oct 24: conquest / diplomacy / sea | — (95, Vienna) / — / — | — / — / — | — (the Staff in force) / — / — |

- **Nothing fires on turn 1.**
- **Without `bites`,** T1 is true on 15 of 22 boards.
- **The first draft's other nine templates** were true on 0–5 of 22: T4, T5, T8, T11 and T12 on none; T6 on 2; T9 on 1; T7 on 5, all of them an accident of Rome's adjacency to Piedmont.

---

## §7 Pacing — the moments first, and blind to affairs

**The moments never see an affair** (critic 1's fix, replacing the first draft's reserved seasons):
- `moments._tick` computes its open letters, its arrivals and its gap from `state` rows whose id has no `#`. An affair's row therefore never delays, crowds out or shifts a moment, dated or causal.
- **When a moment is delivered while an affair letter stands, the affair is withdrawn free:** nothing is applied, its cooldown is re-armed (a `withdrawn` occurrence row), and one dispatch line reads "The Arch-Chancellor's letter was set aside for the Throne of Holland".
- **S14c's arrival turns, its pins and its matrix are therefore invariant by construction.** A pin holds every shipped moment's arrival on a premise that flips inside its lead, and on the Crown's anchor morning, armed against unarmed.

**Affairs keep out of the way.**
- `affairs.deliver_due(world)` is called from `moments.tick` **after** `_tick` returns, because `_tick` returns early on a morning with no moment candidate.
- An affair arrives only when all of these hold:
  - no letter stands, of either kind;
  - no war-intent record is foregrounded (R1, `war_council.foreground_in_tenure`);
  - nothing else arrived that morning (R3);
  - the gap since the last arrival of either deck has run.
- **The pulse.**
  - The first affair arrives no sooner than `first`: turn 7, band 6–9. The E1 band at T1–T5 is untouched, and pinned armed against unarmed.
  - Each later one arrives no sooner than the last arrival of either deck plus `gap`: 5 turns, band 4–7. The gap is drawn per arrival (§10).
  - **Which affair:** among those due — premise held for its streak, off cooldown, under cap, road open — the one whose premise has stood longest. Ties go by `seeded_tiebreak` (authored order on `historical`). Never the same template twice in a row.

**Crowded out.**
- A due affair waits up to `wait` (4) mornings. Still waiting, it writes a `passed(crowded)` occurrence row; that row is not an arrival, so it moves no gap, and it arms the cooldown.
- If its Watch line had shown, one aggregated dispatch line every six turns at most says so: "The Cabinet set aside two matters".
- The Watch says "may", never "will" (critic 2), so nothing promised goes unsaid.
- **A delivered affair that lapses** ends on screen through the existing lapse surfaces, one sentence each.

**Caps and acts.**
- France: 6 affairs an act, plus each template's own caps.
- **The act ends at the Verdict** (turn 44). The caps reset there, and the deck runs on (Q12).

**What a player meets** (from §6.4; seeded paths, not laws):

| Player | Affairs an act | Which |
|---|---|---|
| A hoarder like CMD-A at full standing | 1–2 | the Host's Claims (Bavaria, from the opening) and, at war with the chest to spare, Berthier's door |
| A France that has spent its standing (CMD-H at 80) | 2–4 | adds the Arch-Chancellor's letters while the Emperor campaigns |
| The golden peace, T25–T44 | 0–1 | the Host's Claims if corps stay on an ally |

The golden peace meets almost nothing, because nothing in the core deck touches a peace. **The Edicts' Camps of Instruction (E3) are the deck's answer to the idle pile** (Q2).

---

## §8 The courts — one function, France's content (GR5, GR6, EAD-6)

**One function.** A court's affair, if ever scoped, and the player's run through the same `moments.plan` and `_apply`:
- **The lord rides in the plan dict** and in the occurrence row. `_apply(world, p)` keeps its two parameters, because `tools/_moments_trace.py` wraps exactly that signature, and `tests/test_moments_armed.py`, `test_moments_pacing.py`, `ai_v_sweep` and the driver install the trace (§9).
- **The answers are the same for every lord:** the same template and the same ops. There is no player-only or AI-only branch (GR5, as `SEASONS_WEATHER_SPEC.md` reads it).

**v1 is France's content** (Q4, S14c Q6's precedent). Every template is authored `scope: owner`.
- **What a court-run deck would do, measured** (critic 1, on the 22 boards):
  - Courts meet the Host's Claims when an AI army quarters on its ally (Russia on Austria; Spain on France — the player as host, where an AI decision would move the player's own relations).
  - A court will not pay gold (EAD-6), so it lives off the land. Its allies' relations fall, and with them `coalition.get_coalition_friction` and the AI's co-location and joint-attack bonuses (`enemy_ai.py`). **It weakens coalitions and helps a runaway France.**
- **What Q4(b) would need:**
  - exclude the player as host, and a vassal as lord;
  - a court never takes an answer that charges gold — EAD-6, the one named exception on the court's *choice*, never on the op set;
  - AI Intent's soap-opera share held per seed (pin 13; S14c Q6's reason, measured at 0.91–0.98), with the courts' rows kept out of the dispatch queue;
  - seam AFA held down byte-identical, then up and attributed.

**GR6.** No premise, answer or price reads the LLM; every answer is a button whose command is the executor's.

---

## §9 The engine — the moments engine, extended, not forked

**One engine.**
- **`backend/game_logic/affairs.py` holds what is new:**
  - the premises (each behind a per-turn memo) and the streaks;
  - the pulse;
  - `deliver_due`;
  - the Watch reader;
  - `resolve_courts`, which does nothing in v1 (Q4).
- **`moments.py` stays** the one transport, op table, `plan`, pacing and tick. A separate engine would rebuild the ten transport seams S14c built (`EVENTS_SPEC.md` §3.4).

**What `moments.py` gains** (each checked at `f33a8858` by the repo critic):
- **Occurrence ids.**
  - The store latches a moment by its id forever (`_tick` skips any id already in `state`).
  - An affair's arrival is written as `"<template>#<n>"`, and `moments.entry()` (`:198`) resolves an occurrence id to its template. So every reader keyed on a moment id stays unique per arrival: the rail notice's `moment_id`, the mailbox row, the lapse row.
  - The occurrence's row carries `{lord, bind, tier}` from delivery (§5).
- **The moments blind to affairs (§7).** `_tick`'s open letters, arrivals and gap (`:1081–1093`) read only rows whose id has no `#`. A moment delivered while an affair stands withdraws the affair free.
- **`deliver_due` called from `tick`, after `_tick` returns.** `_tick` returns early on a morning with no moment candidate (`:1081`).
- **The lord in the plan.**
  - `plan(world, e, answer, occ)` reads the occurrence row's lord; a moment has none, so `owner(world)` as today.
  - `_apply(world, p)` reads the lord from `p`. **Its signature does not change** (`:661`; the trace wraps it at `tools/_moments_trace.py:122`).
  - The op halves already take a lord.
- **`gold` reads `instruments.purse_of(world, lord)[1]`** — a tuple; for France it equals `chest_of`, byte-identical.
- **Two ops, `authority` and `admin`** (§5). `tests/test_moments_engine.py:911` pins `set(MO.OPS)` at seven; it flips to nine, consciously, at RE-1.
- **The validator.** `_validate_affairs` sits beside `_validate_moments`.

**The trace grows with it** (`tools/_moments_trace.py`, RE-1; critic 1, C7):
- affair premises are wired into the frame's true and false lists;
- `judge` splits `#` ids: R3, `max_open` and R1 apply to both decks; the floor is the affairs' own;
- `_record_application` reads `p["lord"]`;
- `_delivered` gains arms for the two new ops.

Without this, every affair delivery reads as a ceiling breach in `tests/test_moments_armed.py:237` (a live 31-turn campaign), and `:254`'s `fired == ["throne_of_holland"]` sees affair rows.

**Shown = applied, kept.**
- Every quote is `plan`'s, and the answer re-plans and applies that same plan.
- A closed Accept is greyed with the executor's own words; a Decline is never disabled.
- The trace judges every delivered figure against its quote.

**`world_state.py` is not touched.**
- `moments.tick` already runs in `_advance_turn_internal` after the action refills and the treaty clauses (`:12906`, `:12912`, `:13044`; the tick at `:13179`).
- RE needs no line of `world_state.py`, so S17a's split cannot collide with it.
- Only Q6's `tempo` would touch it.

---

## §10 Seeds — timing only, no dice

- **No per-turn chance.**
  - **Whether** an affair is due is decided by its premise, held for its streak.
  - **When** it arrives is decided by the pulse.
  - **The answer** is the player's.
  - Nothing rolls a die: "personality over randomness" (VISION).
- **The draws are stateless:**
  - the first turn: `seeded_int(seed, "affair::first", lo, hi)`;
  - each gap: `seeded_int(seed, "affair::gap::<n>", lo, hi)`, with n the number of occurrence rows already in `state` (derived, not stored);
  - equally due templates: `seeded_tiebreak(seed, namespace, candidates)`.
- **On `historical` every band collapses to its authored value and ties fall to authored order.** The default campaign seed is `historical` (`campaign_variance.resolve_campaign_seed`), so the default campaign meets the deck deterministically.
- **Nothing draws from `enemy_ai.ai_rng`** or the module `random`; an import census over `affairs.py` pins it.
- **What is fixed on every seed:** the deck, the premises, the streaks, the prices, the floors, the caps, the cooldowns and the copy.
- **What varies:** the first turn and the gaps, inside their bands.
- **The variance signature.** `_variance_signature` gains `affair_turns`, run-sourced like `moment_turns`. The same seed twice compares EQUAL, and variance forced off compares EQUAL to `historical` (S14c's clause idiom, `AI_INTENT_SPEC.md` §3.8.1).

---

## §11 Saves

- **No new `WorldState` field and no `to_dict` line** (497 of 500 lines today).
  - The store rides `world.moments`, already serialized on the stacked line.
  - `from_dict` is untouched.
  - `tests/test_serialization_enforcement.py` needs no new field.
- **The authored deck** lands at `world.moments["block"]["affairs"]` through `from_block` / `_clean_block`; `store_from_data` already deep-copies `block`.
- **The runtime store**, `world.moments["affairs"] = {"streaks": {"<template>|<subject>": n}, "act": n}`, needs **one line** in `store_from_data`, which today copies only `block`, `state` and `due`. Ints and short strings only, with at most one row per template per subject.
- **Occurrence rows join `state`:** `{status: fired | answered | lapsed | withdrawn | passed, reason?, turn, lord, bind, tier, answer?, answered_turn? / lapsed_turn?}`. France's cooldowns and caps are derived from them, in the `reforms._last_enactment_turn` idiom; a `passed(crowded)` row arms a cooldown without counting as an arrival (critic 1, C17).
- **The backfill.**
  - `save_manager._backfill_moments` (`:759`) **returns early for a store that already exists** (`:766`), so the backfill is its own function, `moments.backfill_affairs(world, data)`.
  - A pre-RE save gains the shipped deck, every streak at 0, and `first ≥ save turn + 3`. Nothing fires retroactively.
- **The docs.** `SAVE_FORMAT_REFERENCE.md` gets the `moments` row (occurrence ids, the runtime store); `MODDING_FORMAT.md` gets `moments.affairs`. The store's key-set pins flip consciously at RE-1.

---

## §12 The client — a quiet arrival, every choice a button

**The transport is the moment letter** (`proposal_type "moment_letter"`).
- Every reader it already joins is joined for free.
- No new dtype, and no new modal.

**The quiet arrival (Q8).** An affair arrives as:
- a NORMAL-priority rail card, "An Affair of State: {title} — answer by {date}", whose **Read the letter** button opens the letter;
- and a mailbox row.

Only the campaign's first affair opens itself, once, with its `affair_letter` first-open line. RE-2's work:
- `moments.deliver_letter` (`:1001`) must not write `incoming_proposal_popup` for an affair; today it writes it whenever the letter heads the queue (`:1013`).
- `main.py`'s safety valve (`SAFETY_VALVE_DIALOGUE_TYPES` `:2671`, `_digest_owns` `:2679`) must exempt an affair.
- `deliver_letter`'s hard-coded HIGH priority and `MAILBOX_PRIORITY = 2` (ahead of AI mail) become NORMAL and a lower mailbox rank for an affair.
- The card keeps its `letter_notice_key` (`notifications.py:574`) and is spared the rail's 50-row eviction while it stands (critic 1, C20).

**Every reader that hard-codes the moments' register** reads the letter's `register` and `header` instead (critic 1, C18):

| Reader | Where |
|---|---|
| `moments.DISPLAY` | the notice title, `proposal_type_display` |
| `display_names.py` | `:364` |
| `dialogue_manager.py` | `:277`, `:653` |
| `envoy_digest.ROW_REASON_MOMENT` | — |
| `first_open.py` | `:211` |
| `mailbox_panel.gd` | `:17`, `:203` |
| `incoming_proposal_popup.gd` | the "A MOMENT OF HISTORY" header at `:122`, the moments' default kept |

An affair sends "AN AFFAIR OF STATE — {dateline}".

**The letter's body is the moments' register:**
- **the record** — one of up to three variants, by a board fact;
- **the board lines** — the premise's facts, named;
- **"What each answer does"** — the plan's lines. A gold answer appends `world.charges_relief` ("the Charges ease by N a turn"); an `authority` answer appends `reforms.authority_line` and `ledger.charges_grip_clause`; the Host's Claims prints the distance to the downgrade;
- **the unanswered line.**

Every figure is an `int` (GR2).

**The Watch.** `affairs.watch(world)` returns at most two lines a morning: the nearest-due templates' `watch` strings, worded "may", for measures the player controls. They ride one `situation["affairs_watch"]` key in the dispatch's `_build_situation`, beside `law_sink` and `act_sink` (`:6066`, `:6075`), and one `dispatch_view.gd` line.

**The voices by year.** A display-only table keyed to the turn names an office's holder where it changed hands inside the reachable years. Each turn is checked against `calendar.turn_for_date` by the validator only (S14C-X6); no mechanic reads it.

| Office | Holder | Until |
|---|---|---|
| the Treasury | Barbé-Marbois | about T9, then Mollien |
| the Customs | Collin de Sussy | January 1812 |
| War Administration | Dejean | January 1810 |
| the Intendance | Daru | 1809 |
| the Holy See's Secretary of State | Consalvi | June 1806 |

**The lapse.** The letter's last line prices it; the end-turn gate names it (S14C-X26's `lapse_gate_rows`); LAPSED ENVOYS prints its own sentence (S14C-X15).

**The driver and the frames.**
- The driver already answers every moment letter through its `--moment` dial (`_is_moment_surface`, `playtest_driver.py:3841`; `"moment"` is already in `POLICY_FLAG_KEYS`). So `--affair accept|decline` needs a branch **ahead** of it; absent means decline, and it is appended to `POLICY_FLAG_KEYS`.
- IQ-10 frames of a bill and a door at Interface Scale 1.0 and 2.0.
- The Godot parse harness.
- A census that no affair copy tells the player to type an order.

---

## §13 Rule 8 — no province scan in the tick

**No premise iterates `world.regions`.** Each reads a bounded source:
- **The sovereign:** one marshal (`fall.sovereign_of`, never a captive).
- **Corps on a host's soil:** one pass over the marshal list (about sixty), the sovereign excluded.
- **The diplomatic states:** a handful of `get_diplomatic_state` lookups.
- **The purse:** `instruments.purse_of`.
- **The war's age:** `world.war_start_turns`.

Each premise sits behind a per-turn memo keyed `(turn, measure, lord)`. A census pins that `affairs.py` contains no `.regions.values()` or `.regions.items()`. The G4 tripwires (`tests/test_scale_readiness_phase2.py`; the campaign turn measured 6.1× legacy against a 15× ceiling) stay green.

---

## §14 Sizing and the brakes

**The core deck's own gold, in one act:**
- **The Host's Claims:** 300 × tier, at most 900 a letter, capped at two letters a host an act — **at most 1,800 a host an act**.
- **Berthier's Memorial:** the Staff's own price, 9,000 once, then 300 a turn of upkeep.

**Against the measured surplus** (the net after the Charges, T20–T39: CMD-H 29.2k, CMD-A 44.0k, CMD-M 25.5k):
- the Host's Claims is 4–7%;
- the Staff's upkeep is about a tenth of a golden-peace turn's net (+2,300–3,000 on CMD-H and CMD-A).

**It converts; it does not drain.**
- At the golden peace about 89% of a sink is still missing ten turns later (rate about 28).
- At war most of it comes back: 2,500 gold paid at T15 on the Rhine road leaves 511 or 127 of difference at T30, at the measured rates of 251 and 449 (§1).

**The Edicts, if Q2 rules them in:**
- **Prices:** the Magazines 2,500, the Remounts 1,500 and the Camps of Instruction 2,000, each for eight turns and then an eight-turn rest.
- **The peace's own offer:** the Camps alone, bought at every chance, take 2,000 every 16 turns — about 5,500 an act, a real fraction of a golden-peace pile, spent on drilled men.
- **All three** at every chance: up to about 16,000 an act.

**The brakes, none of them gold:**

| Brake | Its weight |
|---|---|
| **Standing** | the Arch-Chancellor's two letters an act take at most 16 points, grip-floored at 71, and only where the price bites |
| **Administrative actions** | at most two an act (T1) |
| **Goodwill** | the host −2 × tier, at most −6 a letter and −12 a host an act, with the downgrade's distance printed |

**The alarm is never doubled:**
- the validator bars the op;
- none of the ops' setters reaches `add_threat` (`modify_relation_booked`, `adjust_loyalty`, `enact_law`, `modify_authority`, `use_admin_action`, `record_gold_spent` — the repo critic's check);
- a behavioural pin holds `threat_by_target` and `threat_sources_this_turn` byte-identical across every answer on three boards.

**Against the measured pace:**
- The Rhine road's eclipse turns (T34, T35, T30) must stand unmoved with the lapse default, pinned at RE-3.
- The E1 band (T1–T5) is untouched (`first ≥ 6`), pinned armed against unarmed.

**The economy gate** (`AUDIT_GUIDELINE.md`):
- every gold subtraction goes through `moments._apply_gold`, which calls `record_gold_spent`;
- the AST outflow census and `UNRECORDED_OUTFLOWS` (10) are unchanged;
- the lumps show on the existing "Spent" line (a separate `affairs_spent` line would duplicate it, judge 2);
- the Staff's upkeep rides the laws' line;
- **this spec, ruled, is the gate's record for the Host's Claims; the Edicts' prices are RE-6's own record.**

---

## §15 Placement

- **◆ After S15**, as a new row **RE**:
  - RE-1 and RE-2 after S16, the `main.gd` split, so RE-2's client edits land in the new scripts;
  - **ordered against S17c**, which moves `main.py`'s routers and with them the safety valve RE-2 edits: before S17c, or after with the valve's new address;
  - S17a (`world_state.py`) on either side, since RE touches no line of it.
- **Measured on its own arms.** RE-3 is measured on its own Mode A arms. Round 0 (ROADMAP row 11) carries no economy instrument (its three questions are the launch, the first ten minutes and the typed-transcript misreads), so it is a control only.
- **Round 1** (row 16) is the deck's first meeting with players.
- **Size:**
  - **About three and a half sessions** for the core (§16);
  - about one and a half more for the Edicts if Q2 rules them in;
  - one more for a court-run deck if Q4(b) is ruled.
- **Brought forward:** only RE-1 (unarmed, byte-identical) could ride before S15.
- **The gate commit's own lines:** this file, a ROADMAP row, a `PRE_DEPLOY_PLAN.md` row and a STATUS entry. CLAUDE.md's Document Map gains its row at RE-1, paid for by a trim (30 bytes of headroom today).

---

## §16 The build — four slices for the core, two by ruling

**The series and the seams.**
- **The series tool** is `tools/_affairs_series_arms.py`, a child-process tool in the `tools/_s14c_series_arms.py` style, chained from `tools/_s14i_p2_series_arms_final.json`.
- **The seams** are named **functions**, listed in `tests/_affairs_seams.py`; no levers:
  - **AF0** — `affairs.deliver_due`
  - **AFB** — the moments' blindness to `#` rows, and the free withdrawal
  - **AFP** — the pulse
  - **AFN** — the rows and notices
  - **AFA** — `affairs.resolve_courts` (inert in v1)
- **The rule.** Each seam is held down and up with `REACH=` counted, and arm 0 reproduces the prior record byte for byte. Any movement is attributed and re-pinned **in the slice that causes it**, because the hook runs the series.

**RE-1 — the engine, unarmed** (about 1 session)
- **Scope:**
  - `moments.py`: occurrence ids and their rows, the moments' blindness and the free withdrawal, `deliver_due` from `tick`, the lord in the plan, `purse_of`, and the `authority` and `admin` ops with the grip floor and `bites`;
  - `affairs.py`: the premises and their memos, the pulse, the Watch reader, and a `resolve_courts` that does nothing;
  - the runtime store and its `store_from_data` line;
  - `_validate_affairs` and `backfill_affairs`;
  - **the trace extended** (§9);
  - CLAUDE.md's Document Map row, paid for by a trim.
- **Done when:**
  - the shipped boot is unarmed;
  - `BASELINE_SERIES` is byte-identical with every reach counted at 0;
  - the ratchet is unchanged (`to_dict` 497, levers 231, functions over 500 lines 28);
  - the conscious flips are named: `set(MO.OPS)` 7 → 9, and the store's key-set pins;
  - the full suite is green through the hook.
- **Pins, `tests/test_affairs_engine.py`:**
  - occurrence ids, rows and their frozen `{lord, bind, tier}`;
  - derived cooldowns and caps, and a `passed(crowded)` row arming a cooldown;
  - the pulse (`historical` gives the values; ten seeds fall in band; a census finds no `random` and no `ai_rng`);
  - shown = applied for both ops on three boards (rich, poor, clamped), **including the grip floor on a war-score −35 board and no raise below it**;
  - `bites` (no letter at authority 100, none under the floor);
  - **the moments' arrival turns invariant**, armed against unarmed, on a board where Holland's premise flips inside its lead and on the Crown's anchor morning, and the free withdrawal;
  - a save round trip and the backfill;
  - at least 25 validator refusals, among them an op the table lacks (§6.2's ops cannot be authored until their mechanic exists) and a missing `source` or `watch`;
  - the Rule 8 census;
  - the alarm-untouched pin;
  - the trace's teeth on the new ops.

**RE-2 — the client** (about 1 session; after S16, ordered against S17c)
- **Scope:**
  - the header and the register on every reader (§12);
  - the quiet arrival: the popup slot skipped, the safety valve exempted, the NORMAL card pinned against eviction, the mailbox rank, the first letter opening itself;
  - the Watch: the situation key and one `dispatch_view.gd` line;
  - the `affair_letter` first-open line, the voices-by-year table and the lapse sentences;
  - the driver's `--affair` branch ahead of `--moment`;
  - the IQ-10 frames, the parse harness and the no-typed-order census.
- **Done when:**
  - a staged affair arrives quietly and opens from its card, and the first opens itself;
  - both answers apply exactly their quotes through `/respond_to_diplomatic_dialogue`;
  - the frames show both answers above the fold;
  - the harness exits 0;
  - the series is byte-identical (still unarmed).
- **Pins:** `tests/test_affairs_client.py`.

**RE-3 — the three armed** (about 1 session)
- **Scope:**
  - T1–T3 in the shipped block, each with its `source` and `watch`;
  - **the suite-reach head first:** arm on a scratch tree and run the suite. About fifty test files boot a scenario and advance turns directly; list every reactor, then re-seat each consciously or keep it dormant with a conftest pin, and record the choice;
  - the series arms, the attribution and the re-pin;
  - the measure: CMD-H, CMD-A and CMD-M; the Rhine road on three seeds; REACH-AAR; the ten-seed sweep's ceilings; and the six hand-played saves as `--from-save` starts.
- **Done when:**
  - every template's reach is reported per seed and per save;
  - none fires with its premise false;
  - the ceilings hold;
  - **the Rhine road's end turns are unmoved with the lapse default;**
  - the totals sit in §14's band.
- **Pins:**
  - `tests/test_affairs_pacing.py`;
  - `tests/test_affairs_nondominance.py`, rewritten per the critics: on three boards per template (a hoarder at the golden peace, an expander at war, a France that has spent its standing), **each answer is strictly better than the other on at least one delivered axis on each board**, the Decline is free of every purse, there is no alarm, and the letter is absent where `bites` fails;
  - `tests/test_affairs_reach.py`, the per-save table.

**RE-5 — the close** (about half a session)
- **Scope:**
  - the sibling sweep (Rule 10);
  - **the Mode C walk** on `SOVEREIGN_PORT=8007`: one affair answered, one lapsed, the Watch seen, the withdrawal seen;
  - the docs: `SYSTEMS_REFERENCE.md`, `SAVE_FORMAT_REFERENCE.md`, `MODDING_FORMAT.md`, STATUS, the ROADMAP row;
  - **the reach review:** each template's reach per seed recorded; one with zero reach across RE-3's arms and the hand-played starts is deleted with its count pin, or kept, at the user's word from that record;
  - the hand-off to Round 1.

**RE-6 — the Edicts, only if Q2 rules them in** (about 1.5 sessions)
- **Scope:**
  - the Edicts' build contract written at its head: the second lifecycle in `reforms.effect_terms` (a source that expires), the LAWS tab's Edicts section, and the AI rung at the same prices, with its EAD-6 consequence measured;
  - then E1–E3 armed as offers.
- **Pins:** `tests/test_affairs_edicts.py`.

**RE-4 — a court-run deck, only if Q4(b) is ruled** (about 1 session)
- **Scope:** `resolve_courts` with the exclusions of §8, seam AFA held down then up, the soap-opera share per seed (AI Intent pin 13), and coalition friction measured.
- **Pins:** `tests/test_affairs_courts.py`.

---

## §17 Rule 9 — what is struck, and where everything deferred lives

| Item | Disposition | Owner · landing · completion · STATUS line · test |
|---|---|---|
| **The Edicts** (Q2) | gate | **No:** struck; the laws' upkeep stays the recurring drain. **Yes:** RE-6, owner this spec; done when an edict is granted and expires through `reforms.effect_terms` and E1–E3 arrive on their mornings; STATUS "Recurring events: the Edicts"; `tests/test_affairs_edicts.py` |
| **D1–D3, G1, P1, S1, C1** (§6.2) | options, not promises | Each waits on a mechanic named in Q3, whose own gate would write its landing slice. Until then the validator refuses their ops, so none can ship (pinned in RE-1's refusals), and no player-facing text names them. STATUS: the gate line below |
| **A dial** (Q13) | struck from v1; no player-facing promise | Re-opens only on Round 1 evidence: more than 60% of affairs lapsing, read from the testers' saves (the occurrence rows carry `lapsed` and `answered`) by `tools/_affairs_lapse_share.py`, written at RE-5. Owner ROADMAP row 16 ("Settings completed"); done when the Settings panel carries the control; STATUS "Affairs dial — row 16"; `tests/test_affairs_dial.py` |
| **`tempo`** (Q6) | gate | **No:** struck. **Yes:** RE-1 adds it through the treaty AP clause's body (`world_state.py:15225`); done when a debt applies once at the next refill, never below 2 orders; STATUS "Affairs: tempo"; `tests/test_affairs_engine.py` |
| **A court-run deck** (Q4(b)) | gate | **No:** France's content stands (S14c Q6). **Yes:** RE-4; done when §8's exclusions hold and the soap-opera share and coalition friction are measured per seed; STATUS "Affairs: the courts' pass"; `tests/test_affairs_courts.py` |
| **A court's authority** | struck from v1 | Not used by any v1 template. C1 waits on REFORMS §3's regrowth writer (Q3), which has no row today, so nothing here is homed to it. |
| **EC-5b smuggling, and a System member's defection** | stay EC-5b's | `ECONOMY_REVISIT_SPEC.md` EC-5b. S1 waits on it; this deck promises no leakage mechanic |
| **Every candidate in §6.3** | **struck** | each beside its covering surface |
| **A harvest's seasonal arm** | **struck** here | HC-6 (`SEASONS_WEATHER_SPEC.md`) owns any seasonal mechanic |
| **The Chaos Engine** (`FUTURE_DESIGN.md`) | stays unhomed: an idea, not a promise | dice, against VISION; this deck is its board-driven answer |
| **Imperial Governance** | stays where `ROADMAP.md` homes it ("Later", behind its own gate) | G1 is written for it, not promised |
| **The reach review** (RE-5) | owned | RE-5. Done when each core template's reach is recorded and the user has kept or deleted any with zero reach (its count pin in `tests/test_affairs_pacing.py`); STATUS "Affairs: the reach review" |
| **This gate** | open with the user | STATUS "Open with you: the recurring-events gate (`RECURRING_EVENTS_SPEC.md` §0)". The questions live in §0, not in `BUG_FIXES.md` or `DESIGN_REFINEMENT.md`: the census pin `tests/test_the_plan_homes_every_row.py` forbids an open ledger row homed after the deploy |

---

## §18 The record — the judges, the synthesis, the critics

### 18.1 The judges

| Judge | A (history first) | B (the player first) | C (systems first) | Base |
|---|---|---|---|---|
| The historian | **44** | 35 | 28 | A — the only design with record copy for every template; a validated source field, roads, voices, a cross-court finance letter |
| The architect | 36 | 41 | **46** | C — the lightest new state; nothing in `world_state.py`; the only plan that budgets the arming risk |
| The playtester | 40 | **41** | 34 | B — the Watch, the quiet card, no dice, a priced lapse, the courts' row budget |
| **Total** | 120 | 117 | 108 | |

### 18.2 The synthesis

**What it took:**
- **From A:** the voice, the sources, the Arch-Chancellor, the Staff's war-time door, the finance letter (now C1).
- **From C:** the engine (occurrence ids; derived counts; `purse_of`; the backfill trap; the suite-reach head) and the arithmetic (the rate-dependent rebate).
- **From B:** the Watch, the quiet card, the Host's Claims, the nondominance pin, and the Edicts as the fuller option.

**The judges' corrections:**
- "The Regent" renamed the Arch-Chancellor (no Regent before 1813).
- C's authority formula, which raised a France below its floor, corrected.
- The trace carried, with the lord in the plan dict.
- The pulse in place of dice on `historical`.
- The Train never without the Staff.
- Loyalty thresholds, never drift alone.
- The quiet card's real cost named.
- No fork resting on DP alone.
- Every dead premise said plainly.

### 18.3 The critics — 37 corrections (8 blocking), every one applied or answered

The critics read the first draft, whose twelve templates were numbered T1–T12 (T3 was the Host's Claims, T10 Berthier's Memorial). The rows below keep that draft's names; the final numbering is §6's.

**Critic 1, the repo critic** (probes on the boot and 22 boards; one scratch simulation of `moments._tick`):

| # | Severity | Correction | Disposition |
|---|---|---|---|
| C1 | blocking | The reserved seasons kept S14c's arrival turns only for a stable premise: a re-run moved Holland's letter a turn, lost the Bavarian Match and moved the Crown | **Applied** — the moments are blind to `#` rows, and a standing affair is withdrawn free (§7, §9); pinned on a flipping premise and the Crown's anchor morning |
| C2 | blocking | `region.starting_controller` does not exist on the Europe world | **Applied** — `game_end.home_nation_of` (G1) |
| C3 | blocking | The Holy See fired on a corps in Piedmont, the client province beside Rome; a corps on Rome ends the court | **Applied** — moved to P1, conditional on a Papal province beyond Rome and VP-1's "Rome 1809" (§6.2) |
| C4 | blocking | The floor was on raw authority; the Charges and the aura read the grip; 70 ends the marshals' calm | **Applied** — the floor is on the grip, at 71 (§5) |
| C5 | blocking | Licences or Burnings was true from T9 with no System in play, and its Accept bought nothing | **Applied** — moved to S1, conditional on EC-5b and the Decree in force (§6.2) |
| C6 | major | The occurrence's binding and tier were stored nowhere | **Applied** — `{lord, bind, tier}` in the occurrence row (§5, §11) |
| C7 | major | The trace would read every affair as a ceiling breach and see none of the new ops | **Applied** — the trace extended at RE-1 (§9) |
| C8 | major | The arbitration's premise was the resting floor of any cool pair; a court's settlement moves coalition friction | **Applied** — struck (§6.3) |
| C9 | major | Europe is not quiet: Prussia meets the conquered-provinces bill on every board from T20; an AI's Host's Claims could move the player's own relation | **Applied** — v1 is France's content (Q4); Q4(b) excludes the player as host and a vassal as lord |
| C10 | major | Relations with friends and clients never heal; a Decline could break the Bavarian alliance | **Applied** — the Decline halved (−2 × tier), and the downgrade's distance printed (T2) |
| C11 | major | The client's letter and the customs are the live autonomy chips, and the client's premise never held | **Applied** — struck (§6.3) |
| C12 | major | The reach claims were wrong; five templates fired on no board | **Applied** — §6.4's table; those five are struck or conditional |
| C13 | major | A Decline was free at the floor and at 100 | **Applied** — `bites` (§5) |
| C14 | major | Rule 9: the courts' authority had no landing, and T8's narration was a placeholder | **Applied** — the court's authority struck from v1; T8 becomes C1, conditional (§17) |
| C15 | major | The authored deck already rides `block` | **Applied** (§5, §11) |
| C16 | minor | `_tick` returns early with no moment candidate | **Applied** — `deliver_due` is called from `tick` (§9) |
| C17 | minor | A crowded-out affair had no row, so no cooldown | **Applied** — a `passed(crowded)` row (§11) |
| C18 | minor | Readers hard-code the moments' register; HIGH priority; mailbox rank; the driver's `--moment` dial | **Applied** (§12) |
| C19 | minor | The residual figures | **Applied** — 511 and 127 (§1, §14) |
| C20 | minor | Captives, the `purse_of` tuple, the rail's eviction, the `scale` step | **Applied** (§5, §6.1, §12) |

**Critic 2, the rules and history critic** (the rulings and the web; two probes):

| # | Severity | Correction | Disposition |
|---|---|---|---|
| 1 | blocking | The Holy See fired on garrisons | **Applied** (as C3) |
| 2 | blocking | The conquered provinces and the licences were dominated forks, and the nondominance pin could not see dominance | **Applied** — both struck or made conditional; the pin rewritten: each answer strictly better on at least one delivered axis on each board, and absent where `bites` fails (§16 RE-3) |
| 3 | blocking | Rule 9: a "homed" row had no slice | **Applied** (as C14) |
| 4 | major | The Watch promised letters the pulse could drop; seven templates had no Watch | **Applied** — "may", `watch` required by the validator, one aggregated line when crowded |
| 5 | major | The licences priced a System not in force | **Applied** (as C5) |
| 6 | major | S14c Q6 was reopened without answering its reason (the soap-opera share, AI Intent pin 13) | **Applied** — v1 is France's content; Q4(b) must hold pin 13 |
| 7 | major | The floor was on the wrong variable | **Applied** (as C4) |
| 8 | major | The conquered provinces reopened A1's Calabria class (the capture choice covers a province's fate) | **Applied** — moved to G1, homed with Imperial Governance |
| 9 | major | The Host's Claims sold goodwill for gold, and its source was the Spanish war | **Applied** — the Accept buys no goodwill; the source is Napoleon to Soult, 14 July 1810 |
| 10 | major | The client letters were uncounted second doors that brought back R25's class | **Applied** — struck |
| 11 | major | The reserved seasons were premise-conditional | **Applied** (as C1) |
| 12 | major | The arbitration's source contradicted its framing | **Applied** — struck |
| 13 | major | Placement: S17c moves the safety valve; Round 0 has no economy instrument; the gate commit's lines | **Applied** (§15) |
| 14 | major | The weak-row judgement and the dial had no instrument | **Applied** — the reach review from RE-3's record; the dial's data path from the testers' saves (§17) |
| 15 | major | History: Holland's coast; "war must feed war"; "obligations"; the Pius quotation; the Code's dates; T1's single-source line; Bavaria's unsourced line | **Applied** — every line corrected or dropped (§4, §6) |
| 16 | minor | The numbers disagreed | **Applied** — reconciled for the smaller deck (Q9, §7, §14) |
| 17 | minor | The voices by year; Q12's reach | **Applied** — the table extended and its turns validated; Q12 says mid-1809 by T88 |

**What the critique changed.**
- The first draft's twelve templates became **three live and ten conditional**. The deck shrank because the critics' probes found most candidates dead on real boards, dominated, or doubling a ruled surface.
- Nothing promised in this spec rests on a premise the probes did not see hold.
