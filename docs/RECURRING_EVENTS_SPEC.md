# Recurring era events — "Affairs of State": the gate

**Status:** ✅ **SPEC AUTHORED and ✅ RULED October 27, 2026.** The user took every recommended default (§0 Q1–Q14), the Edicts in principle; RE stayed after S15 until the October 31 re-route (§0c). **✅ The October 30 design pass RULED October 30, 2026 — every recommended default (§0b P1–P20) taken; the user: "Take the defaults".** **▶ ✅ RE-ROUTED October 31, 2026 — the user's word (§0c): the whole row is built BEFORE S15, in §16's order, on today's unsplit `main.gd` and today's `main.py`; §0c governs every placement line below.**
- **▶ October 30, 2026 — the design pass, ✅ RULED the same day.** The user: *"i want the events to be good, maybe a haiti one, this should be icing on cake and have good and creative navigation and interface and reaction etc. make sure design is top notch."* A second gate ran (three researchers, three designers on Opus, three judges, the orchestrator's synthesis, two rendered mocks, three critics — the record `docs/audits/AFFAIRS_DESIGN_PASS_2026_10_30.md`). Its product — **§0b the questions, §6.5 the Haiti letter, §12b the home and the letter's dress, §12c the reaction layer, §16b the slices re-sized, §17b what it struck — was written beside the ruled contract and is now part of it: the user took every recommended default ("Take the defaults"), so each section is ruled where it stands and §5–§16 read with §6.5, §12b, §12c and §16b.** Where an October 27 line and an October 30 line differ (the Host's Claims at two corps, the look-ahead, the sizing), the October 30 line governs. The ruling's own lines, the same day: `NAVAL_SPEC.md` NV-D5 amended (P5); the errata renamed ERR-1…ERR-4 (their E-names collided with the Edicts' offers E1–E3); the sizing moved in its four places.
- **The rulings, in the user's words:** October 27 — "Take the recurring-events gate's recommended defaults (docs/RECURRING_EVENTS_SPEC.md §0 Q1–Q14), including the Edicts in principle; RE stays after S15." October 30 — "Take the defaults" (§0b P1–P20). October 31 — "NOPE EVENTS FIRST DO IT IN NEW SESSION" (§0c: RE before S15, in a session of its own).
- **RE-1 the engine ✅ LANDED October 31, 2026 (§19) and RE-2 the client and the dress ✅ LANDED October 31, 2026 (§20), the deck still UNARMED — the shipped boot byte-identical; RE-3 the three armed is next, after the user's review.** From October 31, 2026 the row precedes the deploy (§0c): S15 follows RE.
- **S14j re-measured the economy the same day (`SYSTEMS_REFERENCE.md` §159, `docs/audits/ECONOMY_REBALANCE_2026_10_27.md`):** the Charges' crown term is 250, a detached garrison keeps its pay and conquered soil costs 0.15 more. This spec's measurement (§1) and its "the golden peace is not taxed" / EAD-6 readings predate it. RE-6's head re-sizes the Edicts against S14j's numbers (France levels off at 16–40k, the courts at 146–193k together) before E1–E3 arm.
- **Owner:** row **RE**, before S15 from October 31, 2026 (§0c; §15); **about ten and a half sessions in four shippable tiers** (§16b, ruled October 30): the letter 5.5 (RE-1, RE-2, RE-3 with H0, RE-5), + the home (RE-C) 6.75, + the reactions (RE-R) 7.5, + the squadron (RE-H in full) 8.75, with the Edicts (RE-6) 10.5 — the October 27 ruling's five, re-sized.
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
4. **As a gold sink the core deck converts; it does not drain.** It takes at most about 1,800 gold an act beyond the Staff's own price. **The honest recurring sink is the Edicts** (§0 Q2): fixed-term decrees bought again and again, the era's own instrument. Ruled in, in principle (October 27, 2026); their build contract is RE-6's.

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
| §0 | The questions for the user (ruled October 27); §0b the October 30 pass's questions (ruled October 30) |
| §1 | Why, measured |
| §2 | What the game already has |
| §3 | What players value and resent |
| §4 | The record, 1805–1815 |
| §5 | The attribute block |
| §6 | The catalogue: §6.1 the three live templates; §6.2 the ten conditional ones; §6.3 the struck; §6.4 the reach table; §6.5 the Haiti letter |
| §7 | Pacing |
| §8 | The courts |
| §9 | The engine |
| §10 | Seeds |
| §11 | Saves |
| §12 | The client; §12b the Correspondence and the letter's dress; §12c the reaction layer |
| §13 | Rule 8 |
| §14 | Sizing |
| §15 | Placement |
| §16 | The build; §16b the slices re-sized (the ruled sizing) |
| §17 | Rule 9; §17b the October 30 pass's strikes and deferrals |
| §18 | The record |

---

## §0 The gate — ✅ RULED October 27, 2026: every recommended default (◆) taken

**The ruling.** The user, October 27, 2026: *"Take the recurring-events gate's recommended defaults (docs/RECURRING_EVENTS_SPEC.md §0 Q1–Q14), including the Edicts in principle; RE stays after S15."*
- Every ◆ below is therefore the ruling, and §5–§16 are the build contract.
- The alternatives stand as the record of what was weighed. Each re-opens only by a new ruling.

**One reading taken where two answers meet, Q2 and Q5.**
- **Q5 governs the affairs:** no court pays gold in an affair.
- **The Edicts' AI rung at the same prices (GR5)** is Q2's own stated cost, which the ruling accepted in principle.
- **RE-6's head** therefore writes the Edicts' build contract and measures that rung's spend of the courts' war chests per seed — the EAD-6 reopening Q2 named — before E1–E3 are armed. A shape change found there re-escalates, as below.

**What the ruling leaves open.** Numbers marked as bands are in-band tunable after landing. A shape change — a new op, a new currency, a change to the lapse rule — re-escalates. Each answer is one block field or one constant, so a later ruling may change any one of them alone.

| # | Question | ◆ Ruled — the recommended default, taken October 27, 2026 | The alternatives, and the historically fuller option with its cost |
|---|---|---|---|
| **Q1** | **What to build** | **(a)** The engine with the three live templates (§6.1), **and the Edicts' three offers** (§6.2 E1–E3; Q2 ruled the Edicts in, in principle): a small deck of the bills of the player's own acts, a door, and the offers that give a rich peace something real to buy. | **(b) The engine and the three live templates only.** A seasoning: two to four letters an act, converting at most about 1,800 gold an act. **(c) Hold RE** until a fuller option is ruled. Three letters do not repay the engine's four or five sessions, and that is the honest alternative. **(d) The full catalogue:** every §6.2 template, each with the mechanic it waits on (Q3). |
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
| **Q14** | **Placement** | **Superseded October 31, 2026 (§0c): RE is built before S15, on the unsplit `main.gd` and today's `main.py`.** The October 27 ruling — **After S15**, as a new row **RE**: RE-1 and RE-2 after S16 (the `main.gd` split), and ordered against S17c, which moves `main.py`'s routers and with them the safety valve RE-2 edits. RE-3 is measured on its own Mode A arms. Round 1 (ROADMAP row 16) is the deck's first meeting with players. | **Brought forward:** only RE-1 (the engine, unarmed and byte-identical) could ride before S15 — the October 31 ruling brought the whole row (§0c). |

### §0.1 What this gate does not reopen

- **S14c's rulings:** A1's three struck examples; the four moments, their windows, pacing and matrix cells (Q9 keeps them invariant by construction); S14c Q7's strikes (a marriage bond, AI-court marriages, R25's random quota).
- **The economy's rulings:** IQ-1's ruling (the golden peace is not taxed); EAD-2; EAD-6 by default (Q5).
- **VP-1's strikes "from every surface, not deferred":** "Rome 1809" and the Trianon licences (`VP1_DESIGNS_SPEC.md` §11). §6.2 names what reopening each would take; nothing here reopens them.
- **The standing rules:** HC-0's calendar pin (Q11); VP-1 Q6 (no dynasty store); "diplomacy is never typed"; GR6.

---

## §0b The October 30 pass — ✅ RULED October 30, 2026: every recommended default (◆) taken

**What the pass found, before the questions.** The ruled design is defensive by construction — a quiet card, no reaction beyond the plan's figures, a plain navy text panel — and the catalogue had no Atlantic entry at all. Measured against the six hand-played DD-B runs, **the ruled deck reaches real players almost nowhere**: every run made peace with Britain between turn 6 and turn 19, and only T1 (on one run) meets any of them (the playtester, `AFFAIRS_DESIGN_PASS_2026_10_30.md` §G.1). The four moments do the work the dress, the home and the reactions pay for (the Match arrived on four of six runs). The pass therefore proposes: a Haiti letter that follows the player's own peace (P7), the Host's Claims at two corps (P6), a home, a dress and a reaction layer for every letter of state, and the historically fuller option for Haiti — a squadron with its fate on the naval module's own roll — as the default rather than a tier behind the bill (P2). Three critics then read the synthesis against the code, the record and the rules (§I of the record); every confirmed finding is in the text below, and the questions their findings raised are P18–P20.

**The ruling.** The user, October 30, 2026: "Take the defaults." Every ◆ below is therefore the ruling, and §6.5, §12b, §12c, §16b and §17b are part of the build contract with §5–§16; the right-hand column is the record of what was not taken. A shape change re-escalates only through this table; numbers marked as bands stay in-band tunable. **What the ruling moved the same day:** `NAVAL_SPEC.md` §10's NV-D5 row amended (P5 — its copy-scan pin, promised at NV-0, was never written; it lands at RE-H as an allow-list); the sizing in its four places (§15, `PRE_DEPLOY_PLAN.md` §2, `ROADMAP.md`, STATUS ▶ NEXT UP); the errata renamed ERR-1…ERR-4 (E1–E4 in the pass's text and in the record's critic quotes — the names collided with the Edicts' offers E1–E3, §6.2). **What it owes to the slices:** ERR-2 at RE-1, ERR-3 at RE-3, the NV-D5 pin at RE-H; the two UNVERIFIED claims (P7's windows, P8's T13) measured where §17b homes them.

| # | Question | ◆ Ruled — the recommended default, taken October 30, 2026 | The alternatives, and the historically fuller option with its cost |
|---|---|---|---|
| **P1** | **The content stance for the Haiti letter** | ◆ As §6.5 writes it: a standing **ground** record on every arrival (the law of 20 May 1802 kept slavery where Amiens returned the colonies; the acts of 16 July and 7 December 1802 restored it in Guadeloupe and Guiana; the expedition sent to break Toussaint Louverture's rule ended in Haiti's independence on 1 January 1804) and a **chapter** keyed by arrival and by the last squadron's fate (the killings of 1804; Ferrand's decree of 6 January 1805 and what it did; Dessalines's march and the civilians killed at Moca and Santiago; Missiessy; Leissègues); **Haiti's own documents** in their own typeface, alternating by arrival (the Constitution's Article 2, three years to the day after the law; the proclamation that opens the Act of 1 January 1804, Boisrond-Tonnerre's draft for Dessalines, in French); no answer restores, reconquers or trades; relief priced in gold and the squadron in ships; the Decline priced as the Emperor's own word to Decrès on 5 August 1805 — "il est honteux d'abandonner ces braves gens" — as standing, where it bites (P16). **The default's cost, said plainly:** it fines a player for refusing the commander whose decree the record names. The colons' memorial struck (the record's answer was relief, never indemnity; its fork stakes the planters' claim). | A free Decline (the playtester's flag). Cost: the Accept becomes a pure gamble, and "each answer the better one somewhere" rests on hulls alone. |
| **P2** | **The Haiti letter's form** | ◆ The squadron (RE-H): five of the line sail at the naval module's own odds; the men and the stores land either way; the ships are what is risked. When no hunter is at sea the letter arrives in its **bill form** instead (flour and muskets by two frigates), frozen at delivery (P18) — never a sale at 100. | The bill alone (§6.5 H0; 0.25 session). Cost: the letter prices in gold what history priced in ships — six of seven Antilles sailings of 1805–09 were lost or broken. |
| **P3** | **Q10, narrowly** | ◆ One seeded outcome roll per sailing on the naval family's draw (`_pct_roll`), its namespace carrying the issued turn, the nation and the occurrence, frozen at the letter's arrival; `historical` deterministic; the odds printed before the choice and on the button. **Reported per seed, never a law:** on `historical` the sailings issued at T14, T15, T18 and T19 come home at 36 and T17 and T20 also at 62; the likeliest first arrival, T13, draws 90 and is lost at any odds below 91. | A scripted outcome (home if and only if a window is open): no roll — and no Leissègues. Cost: the Diversion becomes the one road. |
| **P4** | **Q6 — the `squadron` op** | ◆ One Accept-only op `squadron{ships, away, to}` writing the fleet record through one new naval setter pair (`detach_squadron` / `settle_squadron`), ints and short strings only, the readiness floor kept; the odds from the one expedition model, `expedition_slip_odds`, given one new override `escort` (the sailing force alone, ships × readiness / 100) beside `window` and `escort_extra` — a second model is barred (`naval.py:2507`). Measured on the 15 blockaded boards: **36 in 100 at war against Britain's 100 sail, 62 with a window won (64 at readiness 70, 71 at 80), 100 with no hunter**; at war the coverage ratio sits on the cap for any squadron of eight or fewer, so ships move the odds only in a window; Python rounds half to even (36.5 → 36, 61.5 → 62), pinned. **No positive-authority op.** `set(MO.OPS)` 9 → 10. | A `readiness` Decline (design B). Cost: a lapse the blockade never heals, and the Decline rule reopened. |
| **P5** | **NV-D5** | ◆ Amend the row and write the pin it promised, as an allow-list: colonial strings may ship in the affairs' authored copy, the Net line (`economy_executor.py:1236`), the ledger's "Overseas trade" row and the Admiralty's squadron line (which reads its destination `to` from the fleet record, frozen there at the sailing — `naval.py` never imports the deck). | Retire the clause. Cost: nothing pins the copy. |
| **P6** | **The Host's Claims at two corps** | ◆ Yes: `min_corps 2`, tier 1 + (corps − 2) // 2, the top unchanged. **The tier table, said plainly** — as ruled: 3–4 corps tier 1 (300 gold / −2), 5–6 tier 2 (600 / −4), 7+ tier 3 (900 / −6); at two corps: 2–3 tier 1, 4–5 tier 2, 6+ tier 3 — the price rises one tier at four corps and at six. Reach 12 → 16 of 29 and 0 → 2 of 6 hand-played — the deck's only reach onto real players' boards; the four boards it adds host the Kingdom of Italy, Prussia and Bavaria, so the copy carries `{host}`, `{seat}` and `{minister}` slots with the chancery fallback (§12c); measured at RE-3 that it stays an event (true on 9 of 12 scripted boards). | Keep three. Cost: no affair but T1 meets a hand-played board. |
| **P7** | **The blockade latch** | ◆ Yes: the premise clause "blockaded on at least 4 of the last 12 mornings" — **a 12-bit mask int per template in the affairs store, shifted every morning, popcount ≥ 4** — so the letter answers the player's own peace; all six hand-played runs fall inside T13–T17 (UNVERIFIED until RE-H's `--from-save` runs); at peace the squadron arm refuses (no hunter: 100 is a sale) and the bill arrives. | The live streak only. Cost: a player who makes peace with Britain by turn 19 (every hand-played run) never meets the letter. |
| **P8** | **Q9 — the look-ahead** | ◆ Yes: an affair skips a morning when a dated moment's window opens within 2 mornings and its premise reads true; the first affair lands about T13 (UNVERIFIED until RE-1). The moments stay blind; the free withdrawal stays as the net for the causal Reich letter. | As ruled. Cost: a T7 affair withdrawn by the T8 Match — the first letter a player opens vanishes overnight. |
| **P9** | **The home** | ◆ **The Correspondence**: a page of the Dispatch screen behind a Button in its action row — one column of slips inside the Dispatch's ScrollContainer (the Dispatch is one RichTextLabel today, so the page is a new node subtree with its own state; `clamp_ceiling_override` raises the 700 × 500 panel for this page as `_raise_letter_ceiling` does for the letter); no hotkey, no top-bar button, no new endpoint (`GET /dispatch` carries a `correspondence` key); sections On the Desk / Answered / In the Offing; rows from the state rows with the frozen receipt, the apostille under the seal, "what came of it", and chips — the court's Cabinet page (a new signal), ADMIRALTY and LAWS (the existing `ledger:6/7` doors), "Read the letter ▸" (which closes the view first, as Open Envoys does); a first-open line; DD-B `click Dispatch`, then `click Correspondence`, `click#N` for repeated chips. | The Portfolio, a ninth Ledger book. Cost: three "Keys 1–8" captions and three pins (`test_sf7_s9_the_frames.py:635`, `test_s14h_the_third_measure_rows.py:10703`, `test_rf4a_the_laws_tab.py:442`), Mode C's hard-coded 8, about 90 px of a full tab strip at 2.0. The State Papers, a seventh top-bar screen on P. Cost: a seventh nav button and `COMPACT_BELOW_PX` raised for every player, two endpoints, and a badge the player feels obliged to clear. |
| **P10** | **Where the receipt shows** | ◆ The morning's SITUATION block — a `situation["affair_receipt"]` key in `_build_situation` beside `law_sink` / `act_sink`, rendered **in both views that print the Staff's line**: `dispatch_view.gd` and the terminal's morning dispatch in `main.gd` (`test_rf4b_the_laws_everywhere.py:454, 462` pins both for the laws); amber on the morning a squadron's fate lands (situation keys carry no priority — the renderer styles by key); the court's reply or the marshal's remark rides the answer's own response message (`moments.py:912`). | A MEDIUM DIPLOMATIC EVENTS line (the ruled `moment_receipt` class). Cost: grey, after SITUATION, MARSHAL STATUS and both ENVOYS blocks — unseen unless scrolled. |
| **P11** | **The price on the button** | ◆ Yes: two-line buttons at one size — `Button.text` with a newline (the caption; an authored `button_line` ≤ 40 characters with the plan's figures inserted, so DD-B's `click` still matches and the 2.0 row of 632 px holds); the full quote stays in the body; an opaque disabled plaque for this register (the theme's translucent one reads 1.7 : 1 on paper). | A tooltip. Cost: the Decree of Berlin's 2.0 frame already puts its second price below the fold. |
| **P12** | **The dress and a counsel line on every letter of state** | ◆ Yes: one register for the four moments, the affairs and the Edicts' offers — the parchment, the device, the two-line buttons, a counsel line under the buttons; the four moments' counsel lines authored in §12c; RE-3 and RE-6 re-sized for it (§16b); the Match and the Decree re-shot. | Affairs only. Cost: two registers side by side. |
| **P13** | **A sequel letter (`answered{}`), and the file's end** | ◆ No sequel in v1: the next Haiti letter remembers the last squadron's fate in its chapter and board line. **The file ends at T76** (Ferrand's death, 7 November 1808 — a validator-checked `ends` date, the first in the deck) **or earlier when the cap is spent after a loss** (*the earlier close is NOT BUILT — RE-C, November 1, 2026: the page prints the closing record from the morning after `ends` alone; the earlier close has no engine seam and is a question for RE-5's reach review, beside RE3-6 and RE3-7*); the Correspondence then prints the closing record (Palo Hincado, the July 1809 surrender) and the 1825 line as marked future facts. | Design B's "The Last Relief" (nine of the line, 31 December 1808; `answered{}` and a `retires` field; +0.5 session). Cost: a predicate and an anchor for one letter that fires only after a loss. |
| **P14** | **Faces and the seal** | ◆ The monogram locket and the court's arms now; the shipped `wax_seal.png` (an 1840 Russian seal with a Cyrillic legend) overdrawn with a gold N cipher, never shown above 48 px, and re-imported with mipmaps (it aliases at 48 px today). | A Commons pass on your yes (the S14k precedent): public-domain portraits of Cambacérès, Decrès, Berthier, Montgelas and Talleyrand, and a period imperial seal. Cost: about 0.25 session and `THIRD_PARTY_LICENSES.md` rows. |
| **P15** | **The Moniteur on a lost squadron** | ◆ A line in the paper's voice — "Our squadron sustained the honour of the flag against a superior enemy" — true to what the Moniteur did on 30 March 1806 (it printed Cocault's letter altered — nine British of the line against four French — and suppressed Leissègues's report; James IV); never a special. | The paper's own house euphemism ("executes a manoeuvre of the greatest delicacy", `gazette.py:723`). Both are lies the paper told; the default is this one. |
| **P16** | **H1's `bites` (Q6's own clause)** | ◆ **As ruled, both halves**: the letter arrives only where the Decline's −3 would land below 85 (the aura's full line) and the floor allows it whole. At full standing no letter comes — the Marine's portfolio, like the Arch-Chancellor's, waits for a standing that is spent. **Reach on the 29 boards: none by the instantaneous read** (the five candidate boards all sit at authority 100; pc_ulm_t18_paris_fallen's grip of 52 floors the loss to 0); the real reach is the hand-played runs' blockaded windows (T13–T17; four of six below 100 at T21), measured at RE-H. **AMENDED November 1, 2026 at RE-H by the user's word ("we want to make sure these events are good, have conditions that make them appear and don't make the game repetitive … fun factor high"): for the Haiti letter alone the "below 85" half is WAIVED — authored `bites: "floor"` (`affairs.BITES_MODES`; the floor half stays: a −3 is never half-delivered) — so the letter arrives at full standing, where the Decline is a dent (100 → 97) and the squadron the stake; T1 keeps `bites: true`. The old reading is a line away (`"floor"` → `true` in the deck). The measured reach is §22.1's.** | Waive the "below 85" half only (the floor half kept): reach 4 of 29. Cost: at 100 the Decline is a three-point dent that changes nothing, so the Accept — 500 gold, an action, 64 in 100 to lose five hulls — is near-dominated, and RE-3's nondominance pin passes on a technicality. **Taken November 1, 2026 (above).** |
| **P17** | **Sizing** | ◆ Over the ruled 5 sessions (§16b): the letter +1.75 (RE-1, RE-2, RE-3 with H0, RE-5 = 5.5 incl. RE-5), + the home 1.25, + the reactions 0.75, + the squadron 1.25, + the Edicts' register 0.25 — **10.5 in all**, each tier with its own STATUS line and done-when. | Any tier left out has its player-facing promise removed (Rule 9; §17b). |
| **P18** | **The block's shape — the ground, the chapters, the frozen form** | ◆ `record` is the **ground** (every arrival) and `variants[]` the **chapter**, up to 5, keyed by `arrival` (first / later) and `last_fate` (home / lost) beside the ruled board-fact key; a `form` (`squadron` / `bill`) with its own title, captions, ops and counsel, **frozen in `bind` at delivery** with `{lord, bind, tier}` — a standing letter never changes form; if the hunter vanishes while the letter stands, the Accept closes with the refusal text (never a silent re-plan). Cost: §5's variant bound and keys, a `form` field, the validator's rules. | One form only (the squadron). Cost: at peace the letter never comes. |
| **P19** | **The state rows and the log row** | ◆ The state rows carry stored copy beside the ruled ints and short strings — `receipt` ≤ 120, `echo` ≤ 160, `outcome_line` ≤ 160, `remark_by`, `form`, `bind` — because the event log rolls at 500 rows and is full by turn 21; the `moment` log row gains `register: "affair"` and the phase `outcome` in place of the ruled phases `affair` / `court`, and the one-liner gains an `outcome` arm (today the phase would fall to "A moment of history: {title}"). Cost: the row-shape pins; the readers' else arm. | The log rows only. Cost: the home empties by T21. |
| **P20** | **The Gazette, the economy gate, the alarm pin** | ◆ A per-row predicate in `compose_issue` (an affair's `arrived` row never prints; a squadron letter prints its `outcome` row, not its `answered` row) — in `compose_issue` (70 lines), never `filter_campaign_log` (499 lines against the cap of 500); one `press` COURTS line per affair, best-effort against the column's last-8 cap; §14's economy-gate record gains H1 (500 or 600 gold, at most twice an act — at most 1,200 an act, converting, not draining); the alarm-untouched pin extends to the sailing and its settlement. | No COURTS line for affairs. Cost: the Moniteur silent on the Emperor's own acts. |

**Errata to the ruled text** (ERR-1…ERR-4; E1–E4 in the pass's text and the record's critic quotes — renamed at the ruling because the Edicts' offers are E1–E3)**.** (ERR-1, **applied October 30** — a factual correction, no shape change) §4's table and §6.1 T2's record and source said "to Berthier, 14 July 1810"; the letter of 14 July 1810 (Rambouillet, "que la guerre nourrit la guerre") is to Berthier, for Reynier and Dorsenne, and the Soult attribution rests on Branda — both now read "to Berthier, 14 July 1810". (ERR-2, **at RE-1**) the moments' voice and the mailbox's source "The Cabinet" (`moments.py:91`, `dialogue_manager.py:651`, one pin `test_moments_engine.py:510`, §7's "The Cabinet set aside two matters") collide with the top bar's "The Cabinet (F1)", the diplomacy wizard — a Rule 10 sibling; the voice becomes **"the Secretariat"** ("the Council" would collide with the Council of State — the laws' confirm voice and T1's own caption). (ERR-3, **at RE-3**) §1's and §6.4's CMD figures came from unarchived October 27 runs; the archived arms (`docs/audits/score_runs/2026_10_21_rr6/slice`) pre-date S14c and S14j, so every reach count is re-measured at RE-3 on the live tree. (ERR-4, **applied October 30**) §9's "tick at `world_state.py:13336`" is stale — the moments tick sits at `:13336`, after the naval tick at `:13004`. **ERR-5 (applied November 1, 2026 — the user's word at RE-H's review, a shape change on the Haiti letter's premise alone, re-measured the same evening — §22.4):** §6.5 clause 2's "at home" is dropped — "Let Decrès write to headquarters. The Haiti letter requires the Emperor at home, so the player who marches never sees it. Napoleon read the Marine's dispatches in the field." The predicate keeps "standing, not a captive"; the board says court or headquarters; the Watch loses the phrase.

---

## §0c The October 31 re-route — ✅ RULED October 31, 2026: RE before S15

**The ruling.** The user, October 31, 2026: *"NOPE EVENTS FIRST DO IT IN NEW SESSION"* — in answer to the hand-over that placed the deploy (S15) next and this row after it and after S16.

**What it moves.** The whole row RE — the eight slices of §16 in their order (RE-1, RE-2, RE-3, RE-H, RE-C, RE-R, RE-6, then RE-5's close), in the four shippable tiers of §16b — is built **before S15**, in a session of its own started for it. S15 (the deploy) follows RE; S16 (the `main.gd` split) and S17a–d (the file splits; S17c moves `main.py`'s routers) stay after the deploy, so they now follow RE too:
- RE-2, RE-C and RE-R land on today's **unsplit `main.gd`** and `dispatch_view.gd` (the October 27 placement "after S16" is superseded; the scripts S16 cuts inherit the lines);
- the safety valve RE-2 edits stays **at its current address in `main.py`** — the "before S17c" arm of the October 27 ordering, taken by the calendar;
- RE-1 is no longer the only slice that could ride before S15 (Q14's right-hand column, §15's "Brought forward" line): the whole row rides;
- the deck's first meeting with players is **Round 0** (ROADMAP row 11, the signed build), not Round 1; Q13's dial still re-opens only on Round 1 evidence, as ruled;
- S14k-3 keeps its place at the head of the slices after the deploy (the user's October 28 ruling "After S15"), behind S15.

**What it does not move.** No ruling of §0 or §0b (every ◆ stands); the slices' scope, order, sizes and done-whens (§16, §16b); the cadence — each slice its own commit through the hook and a pause for the user's review before the next, the low-risk slice first; the deploy gate's own condition (0 open defect rows — RE opens no ledger row, and `tests/test_the_plan_homes_every_row.py` is untouched); the pins RE-1 must keep (the shipped boot unarmed and byte-identical, `historical` reproducing today's boot).

**Where the old placement stands.** The October 27 lines that say "after S15", "after S16" or "ordered against S17c" — the header's Status and Owner lines, Q14, §15, the heads of RE-2 and RE-C in §16 and §16b, the two STATUS lines in §17 — are the record of the ruling they came from, and each now points here; this section governs. Recorded the same day in `PRE_DEPLOY_PLAN.md` §2 (the RE row moved before S15), `ROADMAP.md` (the row moved to "Before the deploy"), STATUS ▶ NEXT UP and CLAUDE.md's Current Phase.

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
| Quartering: "war must feed war" (#6) | each campaign | pay the claims, or live off the land. The rule: Napoleon to Berthier, 14 July 1810. | **T2 The Host's Claims** (live) |
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

## §6 The catalogue — fourteen templates: seven live (T1–T3 ruled October 27; H1 the Haiti letter, §6.5, ruled October 30; E1–E3 the Edicts, §6.2, armed November 2, 2026 — §25), seven waiting on a ruling

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
- **Source:** research #6. Napoleon to Berthier, 14 July 1810: "war must feed war" (Fondation Napoléon; Branda, *Le prix de la gloire*).
- **Premise:** `corps_on_host` — three or more of the lord's corps, the sovereign not counted, stand on the soil of an ally (ALLIANCE or DEFENSIVE_ALLIANCE) or a client, streak 3. One host per letter: the one with the most corps, ties by authored order.
- **Reach:** 11 of 16 measured (Bavaria from the opening, with 3–7 corps; the Kingdom of Italy on two CMD saves) and 0 of 6 hand-played.
- **Scale:** tier = 1 + (corps − 3) // 2, at most 3.
- **Frequency:** cooldown 10 per host, cap 2 per host an act.
- **Face:** the host's first minister (Bavaria: Montgelas, minister 1799–1817); a client's head; otherwise the host's chancery.
- **Record:** "Historically the Emperor's rule was that war must feed war (to Berthier, 14 July 1810): a corps lived on the country it stood in."
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
| E1 | `the_magazines` — The Magazines (offer) — **✅ ARMED November 2, 2026 (RE-6, §25)** | **the Edicts** (Q2) | the frontier magazines of Strasbourg, Mainz and Ulm and the field magazines of 1805 (Bertaud, napoleon.org; Bergerot, *Daru, intendant général de la Grande Armée*; Daru Intendant-General from 1805, of the Grande Armée from October 1806 — Britannica) | at war with a corps drawing campaign pay (`campaign_pay_at`, the bill's own predicate), **or the storm gathering** — for the player a coalition brewing against the lord and not yet formed (`coalition.brewing_gate`); for a court a war-intent record in tenure against it (**RE-6**: the drafted "war-intent against the lord" never fires for France — `war_intents` are court-against-court only, RE6-2); then the offers' shared clause (available, and the purse at the laws rung's bar) | edict: supply capacity ×1.25 for 8 turns — 2,500 gold, 1 admin | nothing | an effect that expires is a second lifecycle (REFORMS §4) — built as `reforms.effect_terms`' second source, derived from the turn (§25.1) |
| E2 | `the_remounts` — The Remounts (offer) — **✅ ARMED November 2, 2026** | the Edicts | the remount service of the War Administration — the Prussian horses of 1806 entrusted to Bourcier and the depot at Potsdam (Petre); Dejean Minister of War Administration March 1802 – January 1810, then Lacuée de Cessac (napoleon.org) | the cavalry pool below 60 % of the one cap (`MAX_CAVALRY_POOL`, 30,000), **or a cavalry corps below 60 % of its establishment** (`starting_strength` — **RE-6, RE6-3**: the pool alone reached no board, 0 of 55 arms and the six hand-played boards at the cap; the horse is lost on campaign, not in the depots); then the shared clause | edict: cavalry recruit price ×0.8 for 8 turns — 1,500 gold, 1 admin | nothing | as E1 |
| E3 | `camps_of_instruction` — The Camps of Instruction (offer) — **✅ ARMED November 2, 2026** | the Edicts | the camps of the Army of the Ocean Coasts, 1803–05 — Boulogne and Saint-Omer under Soult, Montreuil under Ney, Bruges under Davout — raised 17 August 1805 (Bertaud, napoleon.org; history-pas-de-calais.com); Berthier Minister of War to 9 August 1807, then Clarke | at peace with every other great power six mornings, **the Charges' rate carrying the crown term alone** (**RE-6, RE6-1**: the drafted "rate ≤ 60" was dead under S14j's crown term of 250 — the clause meant the golden peace: no war establishment, no war exhaustion left, no ill war, no pensions of the fallen, no refused peace); then the shared clause | edict: drill morale +5 for 8 turns — 2,000 gold, 1 admin | nothing | as E1. **The golden peace's recurring purchase** — the decision IQ-1 asked to touch the pile |
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

### §6.5 The Haiti letter — ✅ ruled October 30, 2026 (the October 30 pass; §0b P1–P5, P7, P13, P15, P16, P18–P20)

**Why this letter.** R1's rows 1 and 2 (`AFFAIRS_DESIGN_PASS_2026_10_30.md` §E.1): Ferrand's garrison at Santo Domingo, 1803–09, and the seven sailings sent toward it, each a real fork — a true squadron, a half-measure, or nothing — each priced in ships, and six of seven lost or broken. Napoleon's own words carry both answers: to Decrès on 5 August 1805, "Il faut s'empresser de secourir ces braves gens … non-seulement il est important de ne point perdre la partie espagnole, mais il est honteux d'abandonner ces braves gens"; and after the colony fell, on 26 September 1809, "si on y avait envoyé un vaisseau, deux frégates et 600 hommes, on aurait sauvé cette importante colonie". The stake is a flag and a garrison, never plantation yield. Haiti acts in the record and speaks on the page in its own documents. **One template; the two optional slots stay empty** (the colons' memorial is a dominated fork staked on the planters' claim; the fifth dated moment has no French fork — France made no approach to either Haitian state in 1804–13).

**The attribute block.**
- **`id`** `santo_domingo` · **two forms, frozen at delivery (P18):** `squadron` — title "The Squadron for Santo Domingo" (30) — and `bill` — title "The Relief of Santo Domingo" (27), the form taken when no hunter is at sea.
- **`source`:** R1 rows 1, 2, 7 (S1 Reyes Sánchez 2022, printing Ferrand's decree of 16 Nivôse XIII; S2 the *Correspondance*, 29 September 1804, 5 August 1805, 26 September 1809; S4 Leissègues at San Domingo, 6 February 1806; S15 the law of 20 May 1802 and the consular acts of 16 July and 7 December 1802).
- **Premise `colony_cut_off`** (a memo on the world-attached per-turn cache, never a module dict; no region scan — Rule 8), five clauses:
  1. the lord blockaded by the trade-dominant power on **at least 4 of the last 12 mornings** (P7: `naval.is_blockaded` and `naval.blockader_against` against `naval.trade_dominance_nation`; a 12-bit mask per template, shifted every morning, popcount ≥ 4);
  2. the sovereign standing — not `captured_by` — **wherever he is** (`fall.sovereign_of`). *Amended November 1, 2026 by the user's word* ("Let Decrès write to headquarters … Napoleon read the Marine's dispatches in the field"; ERR-5, §22.4): the October 30 clause **at home** (located in `world.nation_starting_regions[lord]`, "the Marine's portfolio comes before the Council when the Emperor holds court; afield the Arch-Chancellor writes instead") is **dropped** — the player who marches never saw the letter. The board says whether the letter found the Emperor at court or at headquarters; the pulse's gap of five mornings keeps H1 and T1 apart;
  3. at least **25 sail in port** (`naval.get_fleet`);
  4. the purse at or above 500 + `AI_PURSE_RESERVE` (1,000) (`instruments.purse_of`);
  5. **`bites`, as ruled (P16) and AMENDED November 1, 2026 at RE-H by the user's word:** the floor half alone — `bites: "floor"` — the Decline's −3 must land whole above the floor (grip ≥ 74); the "below 85" half is waived for this letter, so it arrives at full standing too (P16's amendment, §0b).
  **Reach (RE-H, November 1, 2026; re-measured the same evening after ERR-5 — §22.4):** the letter arrives on every France at war with Britain, blockaded four of the last twelve mornings, with 25 sail in port and 1,500 gold in the chest, wherever the Emperor stands — the passive board from the pulse's first morning (T7), the roads whose marching Emperor keeps the war with Britain (`VP1-TH-historical` T13 and T28, `VP1-RH-historical` T23), the treaty road twice (T23, T38); never a France at peace with Britain (the latch empties in twelve mornings): the six hand-played turn-21 starts made peace by turn 19 with their latch windows (T13–T17) behind the save, and the commanded arms' driver accepts Britain's peace by T10–T19, so the one free morning in their window goes to the Host's Claims (its premise the older — `pick`). On 55 runs: 24 (§22.4's table). *The first measure (H0, with the at-home clause): 16 of 52 — the passive board and the treaty road, never the commanded arms.* *The October 30 reading, superseded:* none of the 29 boards by the instantaneous read (the five boards where clauses 1–4 held all sat at authority 100).
- **`scale`** none (five of the line always) · **`cooldown`** 12 · **`cap`** 2 an act · **`ends`** 1808-11-07 (Ferrand's death — T76, validator-checked against `calendar.turn_for_date`; the first `ends` in the deck). **The file closes at T76, or earlier when the cap is spent after a loss** (P13; *the earlier close is not built — RE-C prints the closing record from the morning after `ends` alone, §23.2 reading 5*).
- **Voice** `named`: "Decrès, Minister of Marine and the Colonies" (3 October 1801 – 1 April 1814, every reachable year). **Face:** the monogram locket "D" and France's arms (P14 ruled: no portrait in v1; a Commons pass re-opens only by the user's word — §17b). The header band names him.
- **The writer's line** (`line`, ≤ 200) — squadron form: "Sire, Ferrand wrote last February that he had bread for twenty days and no credit; Your Majesty called it shameful to abandon these brave men. Brest can put five of the line to sea in a month." Bill form: "Sire, Ferrand wrote last February that he had bread for twenty days and no credit from France. The sea is open; two frigates can carry flour and muskets by the spring tide." (The February is 1805, *Clío* pp. 92–93; a letter arriving after T26 says "two years ago" — authored as the template's `slots` table `{wrote: [{until: 1806-10-16 / T27, "last February"}, {"two years ago"}]}`, the engine reading turns alone — HC-0; RE-H.)
- **The ground** (`record`, every arrival, ≤ 240; "Historically …"): "Historically the law of 20 May 1802 kept slavery in the colonies Amiens returned, and acts of 1802 restored it in Guadeloupe and Guiana; the expedition sent to break Toussaint Louverture's rule ended in Haiti's independence, 1 January 1804."
- **The chapter** (`variants[]`, ≤ 240 each, keyed by arrival and by the last squadron's fate, frozen at delivery — P18):
  - **first arrival:** "Historically Haiti killed the French who stayed in 1804; Ferrand's decree of 6 January 1805 let his raiders sell the Haitians they took, and Dessalines marched on Santo Domingo, killing civilians at Moca and Santiago on his retreat."
  - **a later arrival, no squadron yet:** "Historically Ferrand could buy twenty days' bread in February 1805 and his credit from France had not come; the Emperor ordered flour bought in America and small expeditions of muskets and men (5 August 1805)."
  - **the last squadron came home:** "Historically Missiessy's squadron reached Santo Domingo on 27 March 1805 and Dessalines raised his siege the next day; it came home whole, and the Emperor thought it home too soon."
  - **the last squadron was caught:** "Historically Leissègues landed a thousand men at Santo Domingo and was caught at anchor on 6 February 1806: five of the line lost, 1,510 killed or wounded, 1,156 taken. The Moniteur printed a doctored account."
- **The exhibit** ("FROM HAITI —", IM Fell roman, its own voice; ≤ 160; alternating by arrival): (odd arrivals) "'Slavery is forever abolished.' — the Constitution of Haiti, 20 May 1805, Article 2: three years to the day after the law." (even arrivals) "'Nous avons osé être libres, osons l'être par nous-mêmes et pour nous-mêmes…' — the Act of Independence, 1 January 1804, Boisrond-Tonnerre's draft." Both genuine (the historian, §G.2; the rules critic, §I.2).
- **The board lines:** "France blockaded {n} of the last 12 mornings; the Emperor holds court at {region}." at court (the sovereign sits at Lorraine or Orléanais on the probed boards, never Paris), or "…; the letter reaches headquarters at {region}." in the field (ERR-5, November 1, 2026) · "Britain's squadrons hold the coast: {their} sail effective against our {ours}." (ints, cast as `naval.py:1982` does) · "The passage: {odds} in 100 to come home whole." (the Diversion lever is named on the Admiralty, never here) · from the second arrival: "Your last squadron sailed {date}: {home whole | five of the line lost}."
- **`watch`** (≤ 120): "Blockaded {n} of the last 12 mornings — Decrès may write of Santo Domingo." ("the Emperor at home" struck November 1, 2026 — ERR-5)
- **Accept — squadron form, "Send five of the line":** `gold` 500, `admin` 1, **`squadron{ships: 5, away: 4, to: "Santo Domingo"}`**. The quote: "Send five of the line: 500 gold (the treasury holds {g}); 1 administrative action ({k} left today); five of the line sail (45 → 40 in port until {date}) — {odds} in 100 they come home whole; caught, the five are lost and the men are ashore." `button_line` (≤ 40 rendered): "−500 gold · 1 action · {odds} in 100 home". **Bill form, "Send flour and muskets":** `gold` 600, `admin` 1 — the frigates sail unopposed; `button_line` "−600 gold · 1 action".
- **Decline, "Ferrand must hold alone":** `authority` −3, grip-floored at 71, never a rise; the quote is `reforms.authority_line(a, a − 3)` with `ledger.charges_grip_clause`; `button_line` "standing {a} → {b}". **The lapse is the Decline.**
- **Counsel** (under the buttons, ≤ 160): squadron form, Berthier — "Five sail are five sail, Sire; Boulogne counts them too." Bill form, Berthier — "Two frigates and flour, Sire: the garrison thanks you in the spring and writes again in the autumn."
- **The reaction set** (§12c): the seal and apostille; the response message carries the echo — "Decrès: the squadron slips out of Brest on the night tide." / "Decrès files Ferrand's letter; the garrison of Santo Domingo holds alone."; next morning's SITUATION line in both views ("Five of the line are at sea for Santo Domingo; Decrès expects them home by {date}."); the Admiralty's `squadron_line` while they are away (its destination from the record's `to`); **the fate on its morning, amber:** home — "The squadron is home from Santo Domingo, all five sail; Ferrand has his men, his flour and his muskets." / caught — "The British found the squadron at anchor off Santo Domingo: five of the line are lost; the men and the stores were ashore. Decrès asks for an inquiry."; one COURTS line in the next issue, in the paper's voice: home "SANTO DOMINGO — The Emperor's squadron is home; the garrison is relieved.", caught "SAN DOMINGO — Our squadron sustained the honour of the flag against a superior enemy." (P15), declined "SANTO DOMINGO — General Ferrand holds the city for His Majesty."; the memory on the next letter (the chapter and the board line); the Correspondence row ("⧗ At sea …" then the fate). **When the file closes** the Correspondence prints the closing record — "Historically the Spanish colonists rose in 1808, armed by Pétion and Christophe; Ferrand killed himself after Palo Hincado on 7 November 1808, and the garrison surrendered to the British in July 1809." — and the 1825 line: "Historically France recognised Haiti only in 1825, for 150 million francs paid to the former colonists; Mackau's squadron carried the ordinance, and Boyer accepted it on 11 July 1825."
- **Not a double:** §2 maps no colony and EB-2's pool is untouched (no answer gives France trade); no naval verb sends ships off the map (`resolve_expedition` needs a `world.regions` key, `naval_executor.py:586`); the Diversion keeps the fleet home.
- **Each answer the better one somewhere** (under `bites`, the Decline always crosses the aura's full line): the Accept where the fleet idles at the blockade floor and the standing sits at 85–88 — a −3 costs the aura, five hulls are a ninth of the fleet, and the men land either way; the Decline where every hull counts (the sea road: ddb24_sea and ddb25_sea hold 28 and 41 ships) or the chest is thin. Seeded paths, not laws (P3).
- **The AI's side:** the functions work for any court (Spain is blockaded on 13 boards with 30–45 sail); no relation or loyalty op, so no moment premise is touched; a court's squadron would be all cost, so `scope` stays `owner`. A squadron at sea shrinks the port fleet Britain's AI reads (`naval.py:2440`) — measured in memory on the 15 blockaded boards: no crossing verdict flips, the blockade, trade loss and Diversion odds unchanged, the fleet-action ratio about 6 % worse (winner and "decisive" unchanged) — a predicted mover of the accept arm, attributed at RE-H.
- **The economy gate (§14):** 500 gold (the squadron) or 600 (the bill), at most twice an act — at most 1,200 an act, through `moments._apply_gold` and `record_gold_spent`; this entry is the gate's record for H1, as §14 is for the Host's Claims.
- **The content stance, applied:** no answer restores, reconquers or trades; relief in gold, the squadron in ships, the abandonment in standing with the Emperor's own word on the page; the ground names the law, the acts and what the expedition was on every arrival; the first chapter names the killings of 1804, Ferrand's decree and what it did, and the civilians killed at Moca and Santiago; Haiti, Dessalines, Pétion and Christophe act; the exhibits are Haiti's own words with their author named; no copy uses the period words for Haitians.

**The mechanism (the squadron, P2–P4, P18).**
1. **The op `squadron{ships, away, to}`** takes `OPS` from 9 to 10. Bounds in `AFFAIR_OP_BOUNDS`: `ships` 1–8, `away` 3–6, `to` ≤ 32 characters; Accept-only (on the Decline-forbidden list); at most one per entry; an entry carrying it must author a `bill` form and the owner must have a `navies` row.
2. **The form is frozen in `bind` at delivery:** `squadron` when a hunter is at sea, else `bill`; the letter's title, writer's line, captions, ops and counsel are the form's. If the hunter vanishes while the letter stands, `_plan_squadron` returns a refusal and the Accept closes with its text — never a silent re-plan (`refresh_letter` re-plans on every read).
3. **`_plan_squadron`** returns `{ships, away, to, before, after, odds, hunter, home_by, refusal, line}`; it refuses with no fleet, with fewer than `ships + 20` sail in port, or with a squadron already at sea.
4. **The odds** are the one expedition model asked one question: `naval.expedition_slip_odds(world, lord, None, 0, escort=ships × readiness / 100)` — the open-water arm (no target region: `_controller` is None, guard fleets are skipped, blockade fleets hunt), no troops, and a new `escort` override (the sailing force's own effective strength) beside the existing `window` and `escort_extra`; every live caller passes none, so nothing moves. **Measured on the 15 blockaded boards: 36 at war against Britain's 100 sail (the ratio on the cap, so any squadron of eight or fewer reads the same), 62 with a window won at readiness 50 (64 at 70, 71 at 80 — ships move the odds only in a window), 100 with no hunter (then the bill).** Python rounds half to even (36.5 → 36; 61.5 → 62) — pinned.
5. **`naval.detach_squadron(world, lord, ships, away, to, odds, tag, issued)`** writes `rec["ships"] -= ships` and `rec["squadron"] = {ships, readiness, sailed, returns, to, odds, tag, issued}` — ints and short strings — frozen at the answer, so shown = applied.
6. **`naval._squadron_tick(world)`** runs in `process_naval_turn` after `_readiness_tick`, over `iter_fleet_records` (not `iter_fleets`, which drops a fleet at zero ships — a squadron outliving a Trafalgar must still settle), on `turn >= returns`. The draw is `seeded_int(seed, f"naval::squadron::{issued}::{lord}::{tag}", 0, 99) < odds` (the `_pct_roll` idiom; **the namespace carries the issued turn** — on `historical` the sailings issued at T13–T20 draw 90, 27, 16, 76, 56, 10, 19, 37). Home: the ships fold back at their sailing readiness (the `lay_down_ship` fold). Caught: the squadron is lost whole (the exemplar: five of five). It writes `rec["squadron_last"] = {tag, sailed, returned, outcome, ships, lost, odds}`; no battle clock, no diorama, no rail notice.
7. **`affairs.settle_squadrons(world)`** is the affairs tick's first step inside `moments.tick`: it writes the `moment` row with phase `outcome`, sets the SITUATION key for the morning, appends the outcome to the occurrence's `receipt` and `outcome_line`, and settles the row. The naval module stays pure naval.
8. **The Admiralty:** `naval.build_admiralty_report` (`naval.py:4696`) gains `own_fleet["squadron_line"]` while a squadron is away, its destination from the record's `to`; `strategic_ledger.gd:922-958` draws it beside the rot line.
9. **The memory:** the next occurrence's chapter and board line read `naval.last_squadron(world, lord)`. No `answered{}` predicate in v1 (P13).
10. **The trace** (`tools/_moments_trace.py`): a `squadron` arm in `_delivered` and a fate row (the frozen odds, the draw, the outcome).
11. **The validator** (`_validate_affairs`): the op's bounds; `min_ships ≥ ships + 20`; the `navies` row; both forms authored; `ends` against `calendar.turn_for_date`; the ground and chapter lengths; the exhibit and counsel lengths; the chapter keys named in `affairs.VARIANT_FACTS`; the no-typed-order census over every new field.
12. **Pins:** `set(MO.OPS)` 9 → 10; `BASELINE_SERIES` byte-identical under the default decline policy (no squadron sails); the accept arm's movers (the port fleet Britain reads; a loss leaves the fleet five short) attributed and re-pinned in RE-H as seams **AFH** (`naval._squadron_tick`) and **AFS** (`_apply_squadron` + `settle_squadrons`); the alarm-untouched pin extended to the sailing and the settlement; `test_france_authors_no_overseas_pool` unchanged; a mid-voyage save round-trips in `world.fleets` (probed: `to_dict` / JSON / `from_dict` and every existing naval reader pass with a nested `squadron` key).

**H0 — the bill alone (P2 ruled the squadron; H0 is RE-H's first step and the tier-1 fallback should the squadron ever be cut — Rule 9, §17b).** The same id, voice, ground, chapters and exhibits; the premise with the latch and `bites` (the Emperor at home until ERR-5 dropped the clause, November 1, 2026); Accept "Send flour and muskets" = `gold` 600 + `admin` 1; Decline as above. Honest and narrow; it ships at RE-3 for 0.25 session.

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
- If its Watch line had shown, one aggregated dispatch line every six turns at most says so: "The Secretariat set aside two matters" (ERR-2 — "The Cabinet" until the October 30 ruling).
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

## §12b The home and the letter's dress — ✅ ruled October 30, 2026 (the October 30 pass; §0b P9, P11, P12, P14)

**The arrival stays as ruled** (Q8: the NORMAL rail card, the mailbox row, the first affair opening itself once). What changes is the letter's look, the home it goes to, and what follows. Two rendered mocks stand beside this text — `docs/audits/affairs_mocks/letter_1600.png`, `letter_800.png`, `letter_1600_sealed.png`, `home_correspondence_1600.png`, `home_correspondence_800.png` — **as approximations in HTML over the client's own fonts, parchment, arms and seal, not as frames of the client: the IQ-10 frame shot at RE-2 is the floor.** Every `main.gd:NNNN` cite below is a cite of today's file; CODE-6 (S16) splits `main.gd` before RE-2 lands, so the build reads the symbols.

### 12b.1 The Correspondence — the home

- **What and where.** A page of the Dispatch screen (`dispatch_view.gd`, CanvasLayer 50), opened by a Button in its action row — **"The Correspondence"**, reading "The Correspondence (1 standing)" or "(a squadron at sea)" in amber when it has news, like the Envoys badge — and closed by "◂ The Dispatch". The Dispatch is reachable by the top bar and by R and B, so the home needs no hotkey, no top-bar button and no new endpoint. **The Dispatch is one RichTextLabel in a ScrollContainer today, so the page is a new node subtree with its own page state**: `_on_dispatch_received` and `refresh_pinned` rewrite `content_label` from every GET and must respect the open page; the panel is clamped and gripped (`dispatch_view.gd:34`), and `clamp_ceiling_override` raises its 700 × 500 ceiling for this page as `_raise_letter_ceiling` does for the letter. The name echoes the *Correspondance de Napoléon Ier* and appears nowhere in the code; "the Cabinet" is avoided (ERR-2).
- **Payload.** `GET /dispatch` (`main.py:6825`) gains `payload["correspondence"] = moments.correspondence(world)` — a fresh dict with `first_open.attach`; a GET, so the POST rule does not apply; the Side Desk's `refresh_pinned` (`dispatch_view.gd:67`) re-reads it only while the screen is pinned, so "Read the letter ▸" **closes the view first** (`close_view()`, as Open Envoys does) and the next open re-reads; ordered against S17c.
- **Rows and their source.** Every row reads `world.moments["state"]` plus the deck and the fleet record — **never the event log, which rolls at 500 rows and is already full by turn 21 on three saves** (`world_state.py:3879, 3910-3911`). Four fields are written into the state row at the answer, the lapse or the settlement and frozen there (P19): `receipt` (the plan's short line, ≤ 120), `echo` (the morning's reply, ≤ 160), `outcome_line` (a squadron's fate, ≤ 160) and `remark_by`. A pre-RE save shows its captions only; on an unarmed world the button is hidden.
- **The sections,** one column, each entry a plain slip in ink (the inner field of `old-parchment_alpha.png` as a `region_rect` — no torn edge inside the page; the mocks' torn slips are illustrative):
  - **ON THE DESK (n)** — the standing letters, Not Now's included: "SEALED · answer by {date}" in the rubric Caption with the court's arms or the monogram; the title and the writer; the two `button_line`s; **"Read the letter ▸"** (the rail card's road, `POST /mailbox/activate`, after `close_view()`).
  - **ANSWERED** (newest first) — line 1, the rubric Caption: "{DATELINE} · {TITLE}" with the device right-aligned; line 2, the **apostille** in IM Fell italic at `Lead` with the seal glyph at 18 px: "{caption}. — N." and nothing else (lapsed: "Filed unanswered — {caption}", sepia, no seal; withdrawn: "Set aside for {moment} — nothing was spent"); line 3, what it did: the `receipt`; line 4, what came of it: the `echo`, dated the answered turn + 1, or "At sea — five of the line; word expected about {date}" (no hourglass glyph: no shipped face carries U+29D7), then the fate in rubric; **chips** as `[url]` links (the DD-B instrument presses them): the court's Cabinet page (a new signal into the wizard's `open_for_nation`), **ADMIRALTY ▸** / **LAWS ▸** (the existing `ledger:6` / `ledger:7` doors), **Read the letter ▸**; repeated chips are told apart by `click#N`.
  - **IN THE OFFING** — the Watch's at most two "may" lines (`affairs.watch`), **text only, no pips** (a counter invites gaming the premise).
  - **LEFT UNANSWERED / SET ASIDE** — one dim line each; rows passed for premise, forsworn, verdict or before_save never show.
  - **The closing record and the 1825 line** when the Haiti file closes (§6.5).
  - **Empty states:** "No letter of state lies on the desk, Sire." / "Nothing has yet been answered." / "Nothing is gathering, Sire."
- **Two pointers in.** "No pending envoys at this time." (`main.gd:8270, :8312`) gains ", and the Correspondence (the Dispatch) keeps every letter answered."; the mailbox panel gains a footer button.
- **First-open lines** (`first_open.SCREENS` gains `correspondence`; `affair_letter` was ruled at RE-2 and is authored here; ≤ 220 each): `correspondence` — "The Correspondence, Sire: each letter of state laid before you, the answer you gave, what it did and what came of it; below, the matters that may yet write to you. Nothing here asks for an order." · `affair_letter` — "An affair of state, Sire: a bill of your own acts, laid before you by the office it touches. Each answer is priced on its button; Not Now sets it aside; left unanswered by the date, it takes the second answer for you."
- **No badge beyond the button's own count; no sound.** The page is read-only but for "Read the letter ▸": not a loop. **DD-B:** `click Dispatch` (or `key Alt+R`; a bare `key R` types into a caret-holding line), then `click Correspondence`.
- **At 2.0** (800 × 450 logical): the clamp gives the page 394 px; its scroll window holds about two slips (the 800-px mock overflows instead of scrolling — illustrative only), the buttons stand outside the scroll.
- **Amended at the landing (RE-C, November 1, 2026 — §23.2's readings):** Not Now is the client's, so every `fired` row is on the desk; Read the letter ▸ stands on the desk only (an answered letter has no dialogue to re-open and no new endpoint is cut; an answered slip carries its court / Admiralty / Laws chips); ANSWERED holds the answered rows and LEFT UNANSWERED / SET ASIDE the lapsed (with the price the lapse took), withdrawn and crowded-out ones — the silent passes never show; the Watch is read pure (`affairs.watch(world, record=False)`); the closing record appears from the morning after `ends`; the first-open line rides the page's dict and is acknowledged the Strategic Ledger's way (a screen, not a dialogue); the at-sea line stands in for the echo while the squadron is out, the fate follows in rubric.

### 12b.2 The letter's dress

One register for every letter of state — the four moments, the affairs and the Edicts' offers — gated by `is_moment` in `show_proposal` (`incoming_proposal_popup.gd:67`); every other letter keeps the flat navy panel. A real player called the plain moment letters "the best-explained parts of the game" (the conquest road, October 25): **the quote is never traded for ornament.**

**The type sits on the user-ruled ladder** (`tests/test_uxr2_override_diet.py`: `RAW_RATCHET` 1, `BBCODE_SIZE_RATCHET` 0, the theme ladder exact; `test_uxr1_scale_fix.py` forbids raw sizes under 14): the body 16; line 2 `BodyLarge` 17; the rubric and small-caps lines Labels at `Caption` 14 with font and colour overrides (allowed — `campaign_end.gd:141-160` is the precedent); the apostille and the cipher `Lead` 18; the buttons 16 on both lines. No `[font_size=]`, no raw size.

**At 1.0** (720 × up to 720 at 1600 × 900; `_raise_letter_ceiling`, `:381`), top to bottom:
1. **The sheet.** A `StyleBoxTexture` built in `_ready` over **`assets/textures/old-parchment_alpha.png`** (RGBA 640 × 480, the torn edge transparent; the brief's `parchment_paper_antique_cc0.png` is RGB on a black rectangle — the same art): `texture_margin` 48 / 40, `expand_margin` 12 (the rim drawn outside the box), `content_margin` kept at 24, so no text area is lost; swapped in with `add_theme_stylebox_override("panel", …)` and back for every other register. (A StyleBoxTexture has one border width at every scale — the mock's thinner rim at 2.0 is unreachable, and unneeded.)
2. **Ink** (new `Utils.INK_*` constants; no gold on paper): body `#2B1D12` (8.8 : 1 on the sheet's measured p10 tone), rubric `#6A1410` (6.6 : 1), sepia `#4E3820` (5.9 : 1); under High contrast a flat cream `#EFE3C6`. **Every inline colour this register emits is an `INK_*`** — today's `COLOR_INFO` first-open line (1.4 : 1 on paper), the closed-Accept line (`:248`, 1.8 : 1) and gold (1.05 : 1) are remapped — and a census pins it.
3. **The letterhead,** an HBox above `ContentLabel`, no taller than today's two header lines: **the device** at 44 px — `PortraitLocket.setup` (`portrait_locket.gd:78`) with its gold monogram on leather for an office ("C", "B", "D", "T"), the court's arms for a court (`Utils.nation_flag_path`), France's sheet for the Secretariat's moments — never Napoleon's portrait (he reads, and never speaks; `Napoleon.jpg` exists and is excluded); **the dateline**, a Cinzel `Caption` in rubric, letter-spaced: "AN AFFAIR OF STATE — LATE MARCH 1806" or "A MOMENT OF HISTORY"; **the seal well,** a faint wax-red ring at the right.
4. **Line 2,** `BodyLarge`: "**The Host's Claims** — Montgelas, for the court of Munich" — the writer and the office named here, always.
5. **The body,** the RichTextLabel at 16 in ink: the first-open line (sepia); the writer's own line (`line`); **the ground and the chapter in IM Fell italic** — `[font=res://assets/fonts/IMFeENit28P.ttf]` parses (the file name carries no brackets; Cinzel's does, so Cinzel is a Label font, never a bbcode font); IM Fell has no arrow or minus glyph, so it is scoped to the record and the exhibit and never the `italics_font` slot — history's voice, set apart from the writer's; **the Haitian exhibit** in IM Fell roman under a run-in "FROM HAITI —" in small caps; the board lines led by a 10 px fleuron; "WHAT EACH ANSWER DOES" in small caps; the two quotes with their captions bold; the unanswered line (rubric italic). (No paragraph gaps: the RichTextLabel has none; the mock's 6-px gaps are illustrative.)
6. **The buttons,** the theme's gold-on-navy plaques, legible on their own fill, **two lines at one size** — `Button.text` with a newline, so DD-B's `click` still matches: "Pay the host's claims / −900 gold", "Live off the land / Bavaria 46 → 40", "Send five of the line / −500 gold · 1 action · 5 sail at 36 in 100", "Not Now / waits on the desk". The second line is an authored `button_line` of **≤ 40 characters** with the plan's figures inserted (a Button does not wrap; the 2.0 row has 632 px), pinned; it is also the row's `receipt`. A closed Accept's second line gives its reason ("the day's administration is spoken for") on **an opaque disabled plaque** (the theme's translucent one reads 1.7 : 1 on paper) — a closed-Accept frame joins the IQ-10 rows. Counter stays hidden.
7. **The counsel line** under the buttons, in the existing `_set_aside_line` Label (`:58-63`, hidden for moments today; the pins keep it a `Label.new()`): one style, Caption italic in sepia — "Berthier — An army quartered on a friend eats his goodwill with his bread, Sire." Always visible, never a body line; it colours the stake and never restates the price; the grey assessment slot at `:173` is skipped for this register.

**At 2.0** (800 × 450 logical): `clamp_centered_panel` gives the popup **394 px** (min(440, 450 − 44 − 12); the committed X2 frame measures y 44–438), the content 346, the fixed chrome (the letterhead, a two-line Button of 56, the counsel, three gaps) about 130, **so the scrolling body is about 216 px**: line 2 (two lines), the writer's line and the record stand above the fold and the exhibit's first line sits at its edge; **the exhibit's rest, the board and the quotes scroll, as the RichTextLabel does today — both prices stand on the buttons, so nothing a decision needs is below the fold.** On a campaign's first letter the first-open line pushes the record's end under too. (The true-size mock `letter_800.png` shows the record cut mid-sentence at the fold; a two-line record on the Haiti letter's later arrivals is the one lever, and the ground is already at its cap.) Nothing folds into a toggle. The IQ-10 frame at RE-2 is the floor; `must_show` reads it.

**The answer** (under 0.8 s): the popup hides and `choice_made` emits at once (`:465-489`), so `is_any_modal_open` — which reads `.visible` (`dialog_manager.gd:84`) — is false, hotkeys unblock, and the DD-B instrument sees today's semantics. **The beat starts on `response.success` in `_on_command_result`, from the button rect stored at the press, and is cancelled by a response carrying `diplomatic_dialogue`** (a refusal — `moment_stands` — reaches no client script and `/dialogue_response` passes only error keys, so the verdict is read off the response, never assumed). **It draws on a small parchment slip of its own** (the sheet is gone; ink on the bare map is unreadable), as a Control parented under an existing layer — `CanvasLayer.new()` in a script fails `tests/test_uxr2_layout_law.py:252-259` unless registered with a clamp proof: the apostille fades in (IM Fell italic at `Lead`: "{caption}. — N.", nothing else), **`assets/ui/ornaments/wax_seal.png` presses at ≤ 48 px with a 6° settle and a gold N cipher overdrawn on its centre** (the shipped seal is an 1840 Russian seal; at 48 px its rim legend never reads — a period seal is P14; the texture is re-imported with mipmaps, or a 96-px copy ships, because it aliases at 48 px today), and the `wax_seal` cue (`audio_manager.gd:73`; `AudioManager.play(cue, max_seconds)`; its first caller) plays — one foley, never music; then the slip frees itself. **Not Now:** no slip, no seal, no sound beyond the Buttons' own wood tap; the unsealed letter stays on the desk.

**The payload** (`letter_payload`, `moments.py:760-794`, today `diplomat_name` only) gains `register`, `header`, `arms`, `monogram`, `writer`, `office`, `line`, `ground`, `chapter`, `exhibit`, `counsel` (mirrored into `talleyrand_assessment`), `button_accept`, `button_decline`, and the squadron's `odds`. Every figure an `int`.

**The frames.** `cap_moments` (`tools/iq10_capture_payloads.py:2008`) re-stages the Match and the Decree and adds a tier-2 Host's Claims, Berthier's door, the Haiti letter in both forms, a closed-Accept letter, and the Correspondence (the desk, an answered page, a squadron at sea), each at 1.0 and 2.0; `must_show` adds the parchment, the device, the writer and office on line 2, the two-line buttons, the counsel under the buttons, the exhibit above the fold at 1.0 and the writer's line and record above it at 2.0; `tests/test_moments_client.py:162-185` is **extended, never replaced** (the `_2026_10_22.png` names stay); the Godot parse harness is re-run (its guard is by mtime) over the popup, the dispatch view and any new script; the UXR-0 readability census is re-shot and must stay at ALL_RED / P1 = 0.

---

## §12c The reaction layer — ✅ ruled October 30, 2026 (the October 30 pass; §0b P10, P12, P15, P19, P20)

**The budget, on every template:** at most one line per surface per letter; at most three per letter across all surfaces over three turns; one Gazette COURTS line per letter; no new rail notice beyond the arrival's own; the only sound the seal. **The seams, by tier:**

| Tier | Seam | What it carries |
|---|---|---|
| T0 | the seal and the apostille (client only) | every answer |
| T0 | **the answer's own response message** (`moments.py:912`; printed green by `_display_result`) — the one surface the player is already reading | the court's reply, the marshal's remark, or the minister's acknowledgement (`echo`) |
| T0 | **the morning's SITUATION line** — a `situation["affair_receipt"]` key in `_build_situation` beside `law_sink` / `act_sink`, rendered **in both views that print the Staff's line**: `dispatch_view.gd:177-179` and the terminal's morning dispatch (`main.gd:5562-5565`); amber on the morning a squadron's fate lands (situation keys carry no priority — the renderer styles by key); a two-view pin like `test_rf4b_the_laws_everywhere.py:454, 462` | the receipt, next morning; a fate, on its morning |
| T0 | one Gazette COURTS line, from the answered row's `press` field through the shared one-liner (`campaign_log.py:2504-2514`, `gazette.py:795, 817`), **gated by a per-row predicate in `compose_issue`** (an affair's `arrived` row never prints; a squadron letter prints its `outcome` row, not its `answered` row) — never in `filter_campaign_log` (499 lines against the cap of 500); the column keeps the last 8, so one line per letter is best-effort | the Moniteur's voice, in the next issue |
| T0 | the `remember` board line on the next occurrence of the same template, read from the previous occurrence's row | "In {month} you let the Council act; Cambacérès writes again." |
| T0 | the Correspondence row (§12b.1) | the receipt and "what came of it" |
| T1 | the Admiralty's `squadron_line` while five sail are away | — |
| T3 | the squadron's fate (§6.5) | — |

**No new log type** (`CAMPAIGN_LOG_TYPES` stays at 180; the `moment` row gains `register: "affair"` and the phase `outcome`, and the one-liner gains an `outcome` arm — today an unknown phase falls to "A moment of history: {title}"). **No Gazette special** (an unlisted caption raises, `gazette.py:264`). **The marshal's remark** lives in an affairs-owned table `affairs.HOST_REMARKS`, never in `pick_marshal_voice`'s banks (a sixth situation key costs a five-line bank per named marshal under the every-marshal voice census, `test_sf_md1_every_man_his_own_voice.py:170-186`, and a new bank line shifts the modulo picks on unarmed boards); the speaker is the marshal with the most men on the host's soil, frozen into the row as `remark_by` at the answer.

**The copy, per template** (each line ≤ 160; the host's lines carry `{host}`, `{seat}` and `{minister}` slots — Bavaria / Munich / Montgelas, the Kingdom of Italy / Milan / its chancery, Prussia / Berlin / Hardenberg while in office, else "the {host} chancery" through `resolve_named_diplomat` with the tenure guard: Hardenberg out of office 1806 – April 1807, Cevallos after T60, Schimmelpenninck after June 1806):

| Letter · answer | The echo (T, the response message) | SITUATION (T + 1, both views) | COURTS (next issue) |
|---|---|---|---|
| T1 · Dictate from the field | "Cambacérès: the Council has registered the decrees Your Majesty dictated from the field." | "The estafette carried the Emperor's dictation to Paris; the Council sits on his orders." | "PARIS — The Council of State registers the decrees His Majesty sends from headquarters." |
| T1 · Let the Council act | "Cambacérès: the Council has acted in Your Majesty's name; Paris will mark whose hand signed." | "The Council of State sat under the Arch-Chancellor; Paris remarked the Emperor's absence." | "PARIS — The Arch-Chancellor presides at the Council in His Majesty's absence." |
| T2 · Pay the host's claims | "{minister}: the account between {host} and Paris is square for the season." | "{seat} acknowledges the payment for the army's quarters." | "{SEAT} — The court of {host} acknowledges the scrupulous payment of the army's quarters." |
| T2 · Live off the land | the marshal's remark — Davout: "I will hang the first man who takes a hen unpaid, Sire — but discipline does not feed a corps." · Masséna: "{host} is a fat country, Sire. My men will not go hungry, nor will I." · Ney: "My men will eat, Sire. The minister may send his bill to me." · Lannes: "They fought beside us, Sire. Eating their harvest is a poor way to say so." · Murat: "My horses want oats, Sire, and the country grows them." · Soult: "The quartermasters have their lists, Sire; {seat} shall have its receipts in good time." · Bernadotte: "I will give receipts, Sire, though no one will ever pay them." · by personality otherwise (aggressive "The country is rich, Sire, and my quartermasters are thorough." · cautious "I will have every requisition signed for, Sire. A hungry ally makes a poor neighbour." · literal "The order is to live off the land, Sire. The corps lives off the land.") | "The army lives on the country of {host}; {seat} keeps the account." | "{SEAT} — The Grand Army is quartered upon the country of {host}." |
| T3 · Found the headquarters | "Berthier: the Imperial Headquarters is founded; the orders of the day go out under his seal." | the existing `staff_arrived` line, free | "HEADQUARTERS — Marshal Berthier's staff becomes the Imperial Headquarters of the Grand Army." |
| T3 · Not now | — | — | — (the log row only) |
| H1 | §6.5 | §6.5 | §6.5 |

**The counsel lines** (under the buttons, ≤ 160 each; the affairs' in §6.1 / §6.5): T1 Berthier — "Every hour you give the Council, Sire, is an hour the army waits for its orders." · T2 Talleyrand — "An ally presents his bill once as an account, Sire. The second time, he presents it as a grievance." · T3 Daru — "The Intendance can pay for clerks, Sire. It cannot pay for an order that reaches a corps a day late." **The four moments' (P12):** M1 the Bavarian Match, Talleyrand — "A match binds Munich to the family, Sire; Baden will remember who was passed over." · M2 the Throne of Holland, Talleyrand — "A king of your blood in Amsterdam is a king with his own treasury, Sire." · M3 the Crown of the Reich, Talleyrand — "The crown is a word, Sire; but the princes read words." · M4 the Decree of Berlin, Decrès — "The Decree shuts their ports, Sire. It does not open ours." (Talleyrand counsels and never forbids — the Voice Bible.)

**A player's three mornings after T2's "Live off the land"** (CMD-H, answered on turn 14): *turn 14* — the apostille inks, the seal presses, the response carries Davout's hen line under the plan's figures, the rail card retires, the slip is filed; *turn 15* — SITUATION, on screen and in the terminal: "The army lives on the country of Bavaria; Munich keeps the account."; *the next issue* — COURTS: "MUNICH — The Grand Army is quartered upon the country of Bavaria." Two lines in all beyond the answer's own.

**Amended at the landing (RE-R, November 2, 2026 — §24.2's readings):** the lapse's record is the LAPSED ENVOYS line both views already print (no SITUATION receipt, no new log row); the remark's speaker is the largest corps on the host's soil at the answer — by name, else by personality, else one default; no corps left there, no remark; the remember line reads the previous occurrence of the same template AND subject and stands last on the board; THE COURTS' predicate prints the authored `press` of `answered` and `outcome` rows only (the shared one-liner untouched); the echo rides the answer's response as its second line; `moment_answered` is forwarded at the response edge (RER-1 — the seal's trigger never left the backend before).

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

**The Edicts, ruled in principle (Q2; DRAFT prices, set at RE-6's head):**
- **Prices:** the Magazines 2,500, the Remounts 1,500 and the Camps of Instruction 2,000, each for eight turns and then an eight-turn rest.
- **The peace's own offer:** the Camps alone, bought at every chance, take 2,000 every 16 turns — about 5,500 an act, a real fraction of a golden-peace pile, spent on drilled men.
- **All three** at every chance: up to about 16,000 an act.
- **RE-6 (November 2, 2026) — the prices stand as drafted, re-sized against S14j (§25.2).** S14j's crown term of 250 (divisor 2,500, floor 2,000) returns a spend S as S × (1 − rate/2,500)ⁿ: at peace about 57 % of an edict's price is back by the end of its 8-turn term and 81 % by the end of its rest; at war (rate ≥ 300) 64 % and 87 % — a chest at the floor gets nothing back. An edict's gold is mostly a timing cost — a lower chest for its term — not a drain; the brakes that pace the Edicts are the ones above and none is gold: one administrative action per decree, the term and the rest, the cap of two letters an act, the pulse. Against the live chests (France 15–18k at T20, 7–32k at T40; a major court 10–26k at T40) a decree is 8–25 % of a chest for a term. A price change is in-band (a line each in the deck); **the courts' Edicts are PARKED pending the user's ruling (§25.3): measured with the rung up they moved every road arm against the control while the letters alone moved none.**

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

- **◆ Before S15, from October 31, 2026 (§0c — the user: "NOPE EVENTS FIRST DO IT IN NEW SESSION")**, as the row **RE** at the head of `PRE_DEPLOY_PLAN.md` §2's remaining order: RE-1, RE-2, RE-3, RE-H, RE-C, RE-R, RE-6, RE-5 (§16), each its own commit and review pause; S15 the deploy after RE; S16 and S17a–d after the deploy as before.
  - RE-2's client edits land on today's unsplit `main.gd` (S16's split, when it comes, inherits them);
  - the safety valve RE-2 edits stays at its current address in `main.py` — the "before S17c" arm of the October 27 ordering;
  - S17a (`world_state.py`) on either side, since RE touches no line of it;
  - **the October 30 slices:** RE-H after RE-3; RE-C after RE-2 (on today's `dispatch_view.gd`); RE-R after RE-C (its SITUATION renderers in today's scripts).
  - *The October 27 placement, superseded by §0c:* after S15; RE-1 and RE-2 after S16, the `main.gd` split, so RE-2's client edits would land in the new scripts; ordered against S17c, which moves `main.py`'s routers and with them the safety valve: before S17c, or after with the valve's new address.
- **Measured on its own arms.** RE-3 is measured on its own Mode A arms. Round 0 (ROADMAP row 11) carries no economy instrument (its three questions are the launch, the first ten minutes and the typed-transcript misreads), so it measures nothing of the deck, though its testers are the first to meet it (§0c).
- **Round 0** (row 11, the signed build) is the deck's first meeting with players from October 31, 2026 (§0c); the October 27 line said Round 1 (row 16), now its second, and the Q13 dial still reads Round 1's evidence (§17).
- **Size:**
  - **About ten and a half sessions**, as ruled October 30, 2026 (§16b): the letter 5.5 (RE-1 1.25, RE-2 2.0, RE-3 1.5 with H0 0.25, RE-5 0.5), + the home (RE-C 1.25) 6.75, + the reactions (RE-R 0.75) 7.5, + the squadron (RE-H in full, +1.25) 8.75, with the Edicts (RE-6 1.75) 10.5 — the October 27 ruling's five (three and a half for the core and one and a half for the Edicts), re-sized.
  - A court-run deck is struck by the ruling (Q4).
- **Brought forward:** the whole row, by the October 31 ruling (§0c); the October 27 line allowed only RE-1 (unarmed, byte-identical) before S15.
- **The gate commit's own lines:** this file, a ROADMAP row, a `PRE_DEPLOY_PLAN.md` row and a STATUS entry. CLAUDE.md's Document Map gains its row at RE-1, paid for by a trim (30 bytes of headroom today).

---

## §16 The build — eight slices: RE-1, RE-2, RE-3, RE-H, RE-C, RE-R, RE-6, then RE-5's close (the five ruled October 27 are written below; three were added and all eight re-sized October 30 — §16b is the ruled sizing and each slice's added scope)

**The series and the seams.**
- **The series tool** is `tools/_affairs_series_arms.py`, a child-process tool in the `tools/_s14c_series_arms.py` style, chained from `tools/_s14i_p2_series_arms_final.json`.
- **The seams** are named **functions**, listed in `tests/_affairs_seams.py`; no levers:
  - **AF0** — `affairs.deliver_due`
  - **AFB** — the moments' blindness to `#` rows, and the free withdrawal
  - **AFP** — the pulse
  - **AFN** — the rows and notices
  - **AFA** — `affairs.resolve_courts` (inert in v1)
- **The rule.** Each seam is held down and up with `REACH=` counted, and arm 0 reproduces the prior record byte for byte. Any movement is attributed and re-pinned **in the slice that causes it**, because the hook runs the series.

**RE-1 — the engine, unarmed** (about 1 session; ✅ LANDED October 31, 2026 — the record §19)
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

**RE-2 — the client** (about 1 session; on today's unsplit `main.gd`, the safety valve at its current address — §0c) — **✅ LANDED October 31, 2026; the record §20**
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

**RE-6 — the Edicts, ruled in principle (Q2)** (about 1.5 sessions; after RE-3, before RE-5's close) — **✅ LANDED November 2, 2026 (§25; the courts' rung PARKED pending the user's ruling, §25.3)**
- **Scope:**
  - the Edicts' build contract written at its head: the second lifecycle in `reforms.effect_terms` (a source that expires), the LAWS tab's Edicts section, and the AI rung at the same prices;
  - **the AI rung's spend of the courts' war chests measured per seed** (the EAD-6 reopening Q2 named, §0's reading), with any series movement attributed and re-pinned in the slice — a shape change found there re-escalates;
  - then E1–E3 armed as offers, each with its `source` cited (the citations owed in §6.2).
- **Done when:** an edict is granted, takes effect through `effect_terms` and expires on its turn; E1–E3 arrive on their mornings and pass the nondominance pin; the AI rung's spend is recorded per seed; the full suite is green through the hook.
- **Pins:** `tests/test_affairs_edicts.py`.

**RE-4 — a court-run deck: struck by the ruling (Q4).** v1 is France's content (S14c Q6's precedent), and the code stays symmetric. A court-run deck would need a new ruling; its scope would be `resolve_courts` with §8's exclusions, seam AFA held down and then up, the soap-opera share per seed (AI Intent pin 13), and coalition friction measured. It is kept here as the record of what that ruling would build.

---

## §16b The slices re-sized — ✅ ruled October 30, 2026 (the October 30 pass; §0b P17)

Each added slice behind named seams held down and up in `tools/_affairs_series_arms.py` (§16's rule); arm 0 reproduces the prior record byte for byte; unarmed is byte-identical by construction.

| Slice | Ruled | Added by the pass | Total |
|---|---|---|---|
| RE-1 the engine, unarmed | 1.0 | the look-ahead (P8); the latch mask and `grace` (P7); the form frozen in `bind` (P18); the state rows' `receipt` / `echo` / `outcome_line` / `remark_by` (P19); `register` and the `outcome` phase with the one-liner's arm (P19); `ends` in the validator; `mechanical_block` descending into `affairs.deck` to strip display keys — `variants[].text` only, never the keys (`tools/_s14c_sweep_record.py:47-61` hashes `affairs` wholesale today); `DISPLAY_KEYS` + `ANSWER_DISPLAY_KEYS` (`line`, `counsel`, `exhibit`, `ground`, `watch`, `source`, `button_line`; `echo`, `press`, `remember`); the premise memo on the world-attached cache | 1.25 |
| RE-2 the client — ✅ landed October 31, 2026 (§20) | 1.0 | **the dress** (§12b.2) on the ruled ladder: the StyleBoxTexture register, the `INK_*` constants and their census, the letterhead, the two-line buttons and the opaque disabled plaque, the counsel slot, the answer beat on `response.success` with its own slip under an existing layer, the seal re-import, the payload keys; the `affair_letter` and `correspondence` first-open lines; six letters × two scales of frames plus a closed-Accept frame; the parse harness re-run; the UXR-0 census re-shot | 2.0 |
| RE-3 the three armed | 1.0 | T2 at two corps with the `{host}` / `{seat}` / `{minister}` slots and the tenure guard (P6); the writers' lines, counsel and reaction copy for T1–T3 and the four moments' counsel lines (P12); the reach re-measured on the live tree (ERR-3); the lockstep of `tests/fixtures/moments_block.json` and the frame names | 1.5 |
| **RE-H the Haiti letter** (new; after RE-3) — **✅ LANDED November 1, 2026: H0 the bill alone (§22.1), then the squadron (§22.2); tiers 1 and 4's letter closed** | — | the premise with the latch and `bites`; the two forms; the squadron op with `to`, the `escort` override on `expedition_slip_odds`, `detach_squadron` / `settle_squadron`, `_squadron_tick` over `iter_fleet_records`, `last_squadron`, the Admiralty line and its renderer, `settle_squadrons`; the ground, chapters and exhibits; `ends`; the validator rules; the trace arm; the half-even rounding pin; the NV-D5 allow-list pin (P5); the alarm pin extended; the accept arm attributed (seams AFH / AFS); the hand-played windows measured from `--from-save` starts. **P2 ruled the squadron: H0 (the bill alone, 0.25) is RE-H's first step and the tier-1 fallback (Rule 9, §17b).** | 1.5 |
| **RE-C the Correspondence** (new; after RE-2, on today's `dispatch_view.gd` — §0c) — **✅ LANDED November 1, 2026 (§23); tier 2 "the home" closed** | — | the builder (`moments.correspondence`), the `GET /dispatch` key, the page subtree and its state in `dispatch_view.gd` with `clamp_ceiling_override`, the slips and `[url]` chips, the court signal, `close_view()` before "Read the letter", the two pointers in, the empty states, the frames at both scales, the pins | 1.25 |
| **RE-R the reactions** (new) — **✅ LANDED November 2, 2026 (§24); tier 3 "the reactions" closed** | — | the SITUATION key for the answers' receipts and both renderers with the two-view pin (the squadron's FATE line and its amber styling land at RE-H's second landing — §22.2, reading 0c), the COURTS predicate in `compose_issue`, the echo on the response message, `HOST_REMARKS` and `remark_by`, the `remember` line, a noise census (≤ 1 line per surface per letter, ≤ 3 per letter, one COURTS line) | 0.75 |
| **RE-6 the Edicts** — **✅ LANDED November 2, 2026 (§25); the fourth tier's offers closed, the courts' rung parked (§25.3)** | 1.5 | the Edicts' offers under the one register: a writer's line, a counsel line, the echo, SITUATION and COURTS lines and the Correspondence row for E1–E3 (P12) | 1.75 |
| RE-5 the close | 0.5 | the Mode C walk on 8007 adds: a sealed letter, the Correspondence read, a squadron sailed and settled | 0.5 |

**The shippable tiers** (all four ruled in October 30, 2026; each its own STATUS line and done-when; a tier later cut has its player-facing promise removed — Rule 9, §17b): **(1) the letter** — RE-1, RE-2, RE-3 with H0, RE-5: **5.5**; **(2) + the home** — RE-C: **6.75**; **(3) + the reactions** — RE-R: **7.5**; **(4) + the squadron** — RE-H in full: **8.75**; **with the Edicts (RE-6): 10.5 in all, against the October 27 ruling's 5.** Placement (§15, §0c): before S15 from October 31, 2026 — every slice on today's unsplit client scripts and today's `main.py`.

**Pins flipped when built, beyond §16's:** `set(MO.OPS)` 7 → 9 → 10; the deck hash at RE-3 and again at RE-H, re-measured by `tools/_s14c_sweep_record.py`; the state-row shape (`receipt`, `echo`, `outcome_line`, `remark_by`, `form`, `bind`; the squadron fields); `first_open.SCREENS` + `affair_letter` (ruled) + `correspondence`; the IQ-10 frames and `test_moments_client.py` (extended, the 2026-10-22 names kept); `test_first_open.py`'s screen tuple; the trace's `_delivered`; the no-literal census extended to `affairs.py`; the Gazette pin that no affair's arrival reaches COURTS; the two-view SITUATION pin; the `INK_*` census; the UXR-0 census; two new tests (`test_affairs_haiti.py`; `test_nv_d5_colonial_copy.py`). **Unchanged:** the moments' count pin, the road matrix, `test_france_authors_no_overseas_pool`, the voice banks' picks, `to_dict` 497 / 500, levers 231, functions over 500 lines 28 (`filter_campaign_log` at 499 untouched), `CAMPAIGN_LOG_TYPES` 180, the HC-0 importer pin, the Gazette's special ladder, `_set_aside_line = Label.new()`, the `show_proposal` strings the S14h pins read.

---

## §17 Rule 9 — what is struck, and where everything deferred lives

| Item | Disposition | Owner · landing · completion · STATUS line · test |
|---|---|---|
| **The Edicts** (Q2) | **✅ ruled in, in principle** (October 27, 2026); **✅ LANDED November 2, 2026 (§25)** | RE-6, owner this spec, after RE-3 and before RE-5's close. Done when an edict is granted and expires through `reforms.effect_terms` ✓, E1–E3 arrive on their mornings ✓ (§25.2's table), and the AI rung's spend is recorded per seed ✓ (§25.3 — measured with the rung up, then PARKED behind `affairs.ai_decrees` pending the user's ruling; the flip is one line, the re-measure the chain). STATUS "Recurring events: the Edicts (RE-6)". `tests/test_affairs_edicts.py` |
| **D1–D3, G1, P1, S1, C1** (§6.2) | options, not promises | Each waits on a mechanic named in Q3, whose own gate would write its landing slice. Until then the validator refuses their ops, so none can ship (pinned in RE-1's refusals), and no player-facing text names them. STATUS: the gate line below |
| **A dial** (Q13) | struck from v1; no player-facing promise | Re-opens only on Round 1 evidence: more than 60% of affairs lapsing, read from the testers' saves (the occurrence rows carry `lapsed` and `answered`) by `tools/_affairs_lapse_share.py`, written at RE-5. Owner ROADMAP row 16 ("Settings completed"); done when the Settings panel carries the control; STATUS "Affairs dial — row 16"; `tests/test_affairs_dial.py` |
| **`tempo`** (Q6) | **struck by the ruling** (Q6: two ops) | The treaty AP clause stays the only writer of a lost order; nothing here promises one. It re-opens only by a new ruling. |
| **A court-run deck** (Q4(b)) | **struck for v1 by the ruling** (Q4: France's content) | Covering surface: S14c Q6's precedent. The code stays symmetric, and RE-4 (§16) records what a new ruling would build. |
| **A court's authority** | struck from v1 | Not used by any v1 template. C1 waits on REFORMS §3's regrowth writer (Q3), which has no row today, so nothing here is homed to it. |
| **EC-5b smuggling, and a System member's defection** | stay EC-5b's | `ECONOMY_REVISIT_SPEC.md` EC-5b. S1 waits on it; this deck promises no leakage mechanic |
| **Every candidate in §6.3** | **struck** | each beside its covering surface |
| **A harvest's seasonal arm** | **struck** here | HC-6 (`SEASONS_WEATHER_SPEC.md`) owns any seasonal mechanic |
| **The Chaos Engine** (`FUTURE_DESIGN.md`) | stays unhomed: an idea, not a promise | dice, against VISION; this deck is its board-driven answer |
| **Imperial Governance** | stays where `ROADMAP.md` homes it ("Later", behind its own gate) | G1 is written for it, not promised |
| **The reach review** (RE-5) | owned | RE-5. Done when each core template's reach is recorded and the user has kept or deleted any with zero reach (its count pin in `tests/test_affairs_pacing.py`); STATUS "Affairs: the reach review" |
| **This gate** | **✅ RULED October 27, 2026** — every default taken | STATUS "Recurring events: the gate ruled — RE after S15" (re-routed before S15 October 31, 2026, §0c). The record lives in §0, not in `BUG_FIXES.md` or `DESIGN_REFINEMENT.md`; the census pin `tests/test_the_plan_homes_every_row.py` forbids an open ledger row homed after the deploy, and none is open. RE's slices are homed by `PRE_DEPLOY_PLAN.md` §2's RE row. |
| **The October 30 pass** (§0b P1–P20) | **✅ RULED October 30, 2026** — every default taken ("Take the defaults") | STATUS "Recurring events: the October 30 pass ruled — RE about 10.5 in four tiers after S15" (re-routed before S15 October 31, 2026, §0c). The record lives in §0b and `docs/audits/AFFAIRS_DESIGN_PASS_2026_10_30.md`; no ledger row is opened; the eight slices are homed by `PRE_DEPLOY_PLAN.md` §2's RE row and §16b; the pass's own strikes and deferrals are §17b's |

---

## §17b Rule 9 — what the pass struck or deferred, and where each lives (✅ ruled October 30, 2026)

| Item | Disposition | Owner and landing | Done-when | Test |
|---|---|---|---|---|
| The colons' memorial (R1 row 3) | **struck** — a fork staked on the planters' claim; the record's answer was relief, never indemnity | none; its one fact (1825) lives in the Correspondence's closing line (§6.5) | the closing line prints when the Haiti file closes | `test_affairs_haiti.py` |
| The fifth dated moment (T35–41) | **struck** — no French fork; France made no approach to either Haitian state in 1804–13 | none | — | the count pin stays at four (`test_moments_engine.py:142`) |
| The two optional deck slots | **left empty by design** (the cap, "icing") | §0b; a later template needs its own gate | — | the affair ids pinned in `test_affairs_engine.py` |
| A sequel letter, `answered{}`, `retires` | **not in v1** (P13, ruled October 30); re-opens only by the user's word | if re-opened: a new RE-H2 slice after RE-H (+0.5) | the sequel fires only after a lost squadron; its own nondominance pin | `test_affairs_haiti.py` |
| The portraits and a period seal (P14) | **not taken** (P14 ruled the monogram locket and the court's arms, October 30); no player-facing promise; re-opens only by the user's word | if re-opened: RE-2 (+0.25): the Commons pass, the imports, `THIRD_PARTY_LICENSES.md` rows | each named writer's key resolves to a file; the seal reads no legend at 48 px | `test_moments_client.py` (the locket falls back to the monogram when absent) |
| The four moments' counsel lines (P12) | authored in §12c | RE-3 | the four lines ship with `DISPLAY_KEYS` widened; the Match and the Decree re-shot | `test_moments_client.py` |
| The Edicts under the one register (P12) | RE-6 re-sized (+0.25) | RE-6 | each offer carries a writer's line, a counsel, the echo and SITUATION lines and a Correspondence row | `test_affairs_edicts.py` |
| The hand-played reach of H1 (the latch windows T13–T17) | **UNVERIFIED until RE-H** | RE-H's `--from-save` runs | the reach reported per run; a letter with zero reach on the six runs is re-premised or deleted at RE-5's reach review | `test_affairs_reach.py` |
| "The first affair about T13" (P8) | **✅ MEASURED at RE-1 (October 31, 2026; §19)** — on the staged board (three corps quartered on Bavaria from the opening) the Host's Claims is due from T3, the look-ahead holds T7 for the Match at T8, the Match's gap holds T9–T12 and the first affair lands at **T13** (pinned, `test_affairs_engine.py`); on the passive ten-seed board (`tools/_affairs_first_arrival.json`) the first affair reaches **2 of 10 seeds by T20** — Berthier's Memorial at T19 on ulm and austerlitz — because a passive France keeps the Emperor home and quarters no second corps on an ally's soil (T1 and T2 never premise); the moments' turns identical armed against unarmed on every seed | RE-1 | the look-ahead measured on the ten `SWEEP_SEEDS` ✓ (the commanded and hand-played boards are RE-3's measure) | `test_affairs_pacing.py` |

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
| 9 | major | The Host's Claims sold goodwill for gold, and its source was the Spanish war | **Applied** — the Accept buys no goodwill; the source is Napoleon to Berthier, 14 July 1810 |
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

### 18.4 The October 30 pass — the record

The second gate's record is `docs/audits/AFFAIRS_DESIGN_PASS_2026_10_30.md`: §A the brief and the rubric (two pass/fail gates — icing inside a noise budget; buildable with a claims ledger), §B–§C the client and backend maps, §D the 29-board fact sheet, §E the research (R1 the Haiti record 1804–1810 with twenty-two sources; R2 how the best games present events), §F the three designs (A history-first, B player-first, C systems-first, each on Opus), §G the three judges (each judging every element of every design, never its own lens; keep / kill / graft per element), §H the synthesis and the mocks, §I the critics' corrections and their disposition. Those sections (§0b, §6.5, §12b, §12c, §16b, §17b) are that synthesis; **the user ruled §0b on October 30, 2026 — "Take the defaults" — and they are the build contract with §5–§16.** The fold's lines: this spec's header, §0b, the section heads, §6's head, §15's size and placement, §16's head, §17's new row; `NAVAL_SPEC.md` NV-D5; the four sizing sites; the errata renamed ERR-1…ERR-4.

---

## §19 RE-1 — the engine, unarmed — the landing record (✅ October 31, 2026)

*Row RE before S15 by the user's ruling of October 31, 2026 (§0c); the plan approved in Plan Mode; one session; the review pause taken before RE-2 (the user's cadence: the low-risk slice, then the review).*

### 19.1 Built

- **`backend/game_logic/moments.py` — the transport grows, nothing forks.** Occurrence ids `"<template>#<n>"` (`OCCURRENCE_SEP`, `is_occurrence`, `template_of`); `entry()` resolves an occurrence or an affairs template after the dated deck; `deck()` stays the dated deck alone (`affairs_block` / `affairs_deck` beside it); `moment_rows()` is the moments' blindness (§7 — `_tick`'s open letters, arrivals and gap read it). `plan(world, e, answer, occ)` reads the occurrence row's lord, bound host (`$host` / `$lord` selectors, `_bind_op`), frozen tier (`scaled_op`) and form (`_answer_side`, P18), returns the occurrence's `id`, the `lord` and the `receipt` (the authored `button_line` with the figures inserted, ≤ 120; P19); `_apply` reads the plan's lord — its signature unchanged (the trace wraps it). `gold` reads `instruments.purse_of` (the chest for the owner, byte-identical). **Two ops:** `authority` (the delivered loss min(|price|, max(0, grip − 71)) on `get_imperial_grip`; never a rise; the line `reforms.authority_line` + `ledger.charges_grip_clause`; a lord without a tracker skipped) and `admin` (`use_admin_action`; closed with "the day's administration is already spoken for"); `set(MO.OPS)` 7 → 9. `deliver_letter(…, mid, row)` writes the frozen row `{id, lord, bind, tier, form}`; `build_letter` / `refresh_letter` / `answer` / `lapse_default` / `answer_verdict` / `lapse_gate_rows` thread the row; `_stamp_receipt` freezes `receipt` and `echo` on an occurrence at the answer or the lapse. `tick` → `_tick` then `_affairs_tick` (the withdrawal, `deliver_due`, `resolve_courts`; [] while unarmed). `_log` gains `lord`, `register: "affair"`, `occurrence`; the phases `withdrawn` and `outcome` (`campaign_log.py`'s arms; a moment's rows byte-identical). `STATUS_WITHDRAWN`. The runtime key `affairs` in `store_from_data` (`_clean_runtime`: ints and {str: int} maps); `backfill_affairs` (`not_before` = the save turn + 3) wired as `save_manager._backfill_affairs` (a no-op on the shipped scenario). **ERR-2:** `SECRETARIAT = "The Secretariat"` (the `cabinet` speaker key stays), `dialogue_manager.py`'s mailbox source, the pin re-pinned.
- **`backend/game_logic/affairs.py` (new; what is new lives here).** The three premises — `sovereign_afield` (T1), `corps_on_host` (T2: one pass over the marshal list, the sovereign, captives and a contingent's commander not counted; the host with the most corps), `staff_offered` (T3: `law_refusal` open, the purse at the price + `AI_PURSE_RESERVE` + `AI_PURSE_UPKEEP_TURNS` × upkeep — one source with the AI's rung) — each `{holds, bind, measure, latch}` behind the per-turn memo on the world object (`_affairs_memo`, never serialized); the streaks per subject and the latch masks (`update_morning`, once a morning); the pulse (`pulse_first`, `pulse_gap` — `historical` the values, every seed in band, no die; §10); `candidates` (the premise held for its streak, the latch, the road, `ends`, `bites`, the cooldown and the cap, both derived from the rows); `tier_of` (both scale shapes); `bites`; `pulse_block` / `desk_block` (reading 2 below); `pick`; `deliver_due`; `_crowd_out` and the aggregated set-aside line (`write_receipt`, at most one in six turns, for a matter whose Watch had shown); `withdraw_standing` (the affair's dialogue popped, its notice dismissed, the row `withdrawn` with `set_aside_for`, one line, the moment's popup slot re-checked); `watch` (at most two "may" lines; `watched`); the copy's slots (`fill_slots`: `{host}`, `{seat}`, `{minister}` as the chancery fallback until RE-R, `{n}`, `{m}`), the ground and the chapter (`record_text`, `chapter_of` keyed `arrival`), `title_of` (the form's), the board lines; `resolve_courts` (inert, seam AFA). No `random`, no `ai_rng`, no nation literal, no calendar import, no province scan (pinned).
- **The validator** (`_validate_affairs` beside `_validate_moments`; the id charset `[a-z_]{1,32}` on both decks): 43 refusal cases pinned — an op the table lacks, the alarm and autonomy barred, a priced Decline, a missing `source` or `watch`, a watch that promises, an `authority` price without `bites`, the reserved `#`, an id that is a moment's or a law's, the shapes (a door's one `enact_law`, an offer's empty Decline), the lengths, the bands, the pulse's bands, the voices, `ends` against its date, the scale and latch shapes, a `button_line` past 40 rendered (a `{slot}` counts four), a relation op on an unknown court.
- **The fixture** `tests/fixtures/affairs_block.json`: the S14c deck + T1–T3 exactly as §6.1 authors them (the Host's Claims at two corps, P6; the counsel and echo lines from §12c; T1's Decline −5 with `tiers {"2": −8}`); RE-3 copies it into the scenario.
- **The instruments.** `tools/_moments_trace.py`: the affairs frame on every morning (`true` / `false`, `due`, `delivered`, `withdrawn`, `passed`), both decks judged (R3, `max_open` with withdrawn letters subtracted, R1, the premise), the affairs' floors (ok / pending / released — the engine's exits are explicit) and the floor with teeth (an occurrence delivered or crowded with no row is silent), the `authority` / `admin` arms of `_delivered`. `tools/_s14c_sweep_record.py`: `mechanical_block` descends into `affairs.deck` (the display keys struck); the shipped hash unchanged. `tools/ai_v_sweep.py`: `moment_turns` the dated deck's alone, `affair_turns` beside it in the signature (`test_moments_reich.py`'s text pin kept). `tests/_affairs_seams.py` (AF0, AFB, AFP, AFN, AFA) and `tools/_affairs_series_arms.py` → `tools/_affairs_series_arms_final.json`; `tools/_affairs_first_arrival_probe.py` → `tools/_affairs_first_arrival.json`.
- **The docs and the map.** `SAVE_FORMAT_REFERENCE.md`'s `moments` row (the occurrence rows, the runtime key), `MODDING_FORMAT.md`'s `moments.affairs` row, `EVENTS_SPEC.md` §3.4 seam 8 and §13.2 (ERR-2), `SYSTEMS_REFERENCE.md` §161 (the rules) and its §147 transport line; CLAUDE.md's Document Map row, paid for by a trim of the closed AI Intent phase's correction note (61,996 of 62,000 LF bytes).

### 19.2 The readings taken (each flagged in the approved plan; each reversible by a line)

1. **"Never the same template twice in a row"** (§7) is a preference among the candidates due that morning — the last-arrived template is set behind the others — never a bar on a lone candidate: its own cooldown (10–14 turns) spaces it, and a bar would silence the Host's Claims on boards where it is the only live template.
2. **The pulse and the desk are two gates.** The pulse (`first`, the gap since the last arrival of either deck, the look-ahead, the act's cap) decides WHEN the deck may speak; the desk (a foregrounded crisis, a standing letter of either kind, a moment's arrival that morning) decides whether the Emperor can be reached. A matter the pulse holds back is not waiting on a busy desk and is never crowded out by it; the wait toward `passed(crowded)` counts the pulse-open mornings the desk was busy or another affair took the morning (R3), and past the template's `grace` (1–6; default `pacing.wait`, 4) the matter is set aside. **Without the split the ruled numbers (gap 5 > wait 4) crowd out the first letter at T11 and P8's ruled "about T13" cannot hold** — found by the first run of the invariance pins.
3. **`grace`** is that per-template wait bound; **the latch mask** (`latch {of ≤ 16, at_least}`, shifted every morning) is the substrate every premise may feed, used by no v1 template until RE-H's `colony_cut_off`.
4. **`ends`** is `{date, turn}`; the validator checks the date against the turn, the engine reads the turn (HC-0).
5. **A tier multiplies gold, relation, loyalty and authority** (`SCALED_OPS`); `admin` and `dp` change only by an authored `tiers` override — found when the step-form tier doubled T1's Accept to two administrative actions and closed it.
6. **`voice.speaker`** ∈ named | office | host; `host` reads "The court of {host}" until RE-2's display table names the minister by the turn.

### 19.3 Measured

- **The series:** seven arms (0, AF0, AFB, AFP, AFN, AFA, ALL) byte-identical to `BASELINE_SERIES` (divergence `None` on every arm), every reach 0 — the deck is unarmed, so no seam bites (`tools/_affairs_series_arms_final.json`).
- **P8, the look-ahead and the first arrival** (§17b's row closed): on the staged board the first affair lands at **T13** (pinned); on the passive ten-seed board (`tools/_affairs_first_arrival.json`, the fixture deck grafted on the shipped boot, 20 turns, the trace riding) the moments' arrival turns are **identical armed against unarmed on every seed** (Holland at 18 on `historical`), 0 ceiling and 0 floor breaches, and the first affair reaches **2 of 10 seeds** — Berthier's Memorial at T19 on ulm and austerlitz, lapsed (a passive France answers nothing), where the hoard clears the Staff's bar; none on the other eight by T20: the passive Emperor stays home (T1 never premises) and Bernadotte alone stands on an ally's soil (under the two-corps bar). Seeded paths, not laws; the commanded and hand-played boards are RE-3's reach measure (ERR-3).
- **The three boards for the two ops** (pinned): authority 80 → 75 (loss 5); 73 → 71 (the floor takes 2); 70 → 70 (no raise under the floor); on a war-score −35 board (grip = authority − 8) 85 → 80 and 75 → 75; `admin` 2 → 1, closed at 0 with its own words and the letter standing.
- **The ratchet unchanged:** `to_dict` 497 lines, levers 231, functions over 500 lines 28, silent handlers 6, CLAUDE.md 61,996 LF bytes (cap 62,000), STATUS under its cap; the shipped block's `deck_sha` unchanged (no `affairs` key); the `historical` boot's store `{block, state}` byte-identical through five ticks.
- **The pins:** 113 in `tests/test_affairs_engine.py`, 26 in `tests/test_affairs_pacing.py`; the moments family (`test_moments_engine` / `armed` / `pacing` / `transport` / `reich` / `letters` / `client`), `test_serialization_enforcement`, `test_serialization_played_world_census`, `test_code_health_ratchet`, `test_hc0_calendar`, `test_first_open` green; the full suite green through the hook.

### 19.4 The done-when, item by item

- the shipped boot is unarmed ✓ — no `affairs` key in the scenario; `AF.armed(world)` False; five ticks write nothing; the store's key set `{block, state}`;
- `BASELINE_SERIES` byte-identical with every reach counted at 0 ✓ (19.3);
- the ratchet unchanged ✓ (`to_dict` 497, levers 231, functions over 500 lines 28);
- the conscious flips named ✓ — `set(MO.OPS)` 7 → 9 (`tests/test_moments_engine.py:911`), the mailbox source "The Secretariat" (`:510`), the store's key set: `block.affairs` and the runtime `affairs` on an ARMED world only (the shipped store unchanged), the `moment` log row's `register` / `occurrence` on an affair's rows only;
- the full suite green through the hook ✓.

### 19.5 The sibling sweep (Rule 10)

- **ERR-2:** code — `moments.py` (`SECRETARIAT`; every `CABINET` use), `dialogue_manager.py` (the mailbox source), the pin; tools' copy — `iq10_run_captures.py` (the frame's label and `must_show`), `iq10_capture_payloads.py` (`cap_moments`); docs — `EVENTS_SPEC.md` §3.4 seam 8 and §13.2, `SYSTEMS_REFERENCE.md` §147's transport line; the committed IQ-10 frames still show the old name and re-shoot at RE-2 (the dress). The diplomacy wizard's "The Cabinet (F1)" family (the top bar, the tutorial's lesson VII, the state desk's door lines, the clarification speaker, the IQ-4 rail row) is a different feature and is untouched.
- **The occurrence-id sweep** (a Sonnet reader over every consumer of a moment id, before the build): one string per arrival on every producer (the state row, the context, the payload, the notice's detail, the log row, the plan's id — `notifications.standing_letter_keys` compares two of them); `deck()` the dated deck alone (`test_moments_reich.py:158-183`, `test_moments_armed.py:72-75`); the whole-state scanners split `#` rows (`_tick`, the trace, the sweep's `fire_turns` and `moments_passed`, the sweep record's hash and reach); `STATUS_WITHDRAWN` read as ended on screen; no seed read in `moments.py` (`test_moments_reich.py:185-188`).
- **RE-3's suite-reach head, recorded now:** when the deck arms, these react and are re-seated consciously or kept dormant with a conftest pin — `test_moments_armed.py:72-75, 117, 232-254`, `test_moments_reich.py:84-86, 140`, `test_ai_intent_assurance.py` (the signature's `affair_turns`), `test_serialization_played_world_census.py`, `BASELINE_SERIES` (the rig attributes), `test_moments_pacing.py`'s deck hash (the S14c sweep re-recorded).

### 19.6 What RE-2 inherits

The quiet arrival (`deliver_letter` still writes the popup slot and a HIGH notice for an affair; `MAILBOX_PRIORITY` 2; the valve exemption); the register and header on every reader (§12's table); the Watch's surface (`affairs.watch` is built; nothing renders it); the `affair_letter` first-open line; the driver's `--affair` dial ahead of `--moment`; the dress (§12b) and the frames; the display table for `office` / `host` voices.


## §20 RE-2 — the client and the dress — the landing record (✅ October 31, 2026)

*The second slice, on today's unsplit `main.gd` and today's `main.py` (§0c); the plan approved in Plan Mode; two commits (A the backend half, B the client half) in one session; the review pause taken before RE-3. The deck stays UNARMED: the shipped scenario gains no `affairs` key, so every affair surface is exercised through the fixture (`tests/fixtures/affairs_block.json`) in the pins and the frames.*

### 20.1 Built — the backend half (commit A)

- **The quiet arrival (§12, Q8).** `moments.deliver_letter`: an affair's mailbox row ranks below the courts' mail (`AFFAIR_MAILBOX_PRIORITY` 5; a moment keeps `MAILBOX_PRIORITY` 2); its rail card is NORMAL, titled "An Affair of State: {title}", carries `details.standing_letter` and `expires_after_turn` = the answer-by turn, and is spared the tray's eviction while the letter stands (`notifications._eviction_candidate` skips a standing letter; the letter's own dismissal retires it at the answer, the lapse or the withdrawal; the UX23-A pins untouched); the popup slot is never written for an affair — **the campaign's first affair excepted, once**, when it heads the queue (exactly one occurrence row in the store); `main.py`'s safety valve never re-derives a modal from a standing affair (`_quiet_letter`; `SAFETY_VALVE_DIALOGUE_TYPES` untouched); `DialogueManager.push` lets a court's letter take the head from a quiet affair, which returns to the queue (reading 5). `moments.is_quiet_letter` / `register_of` are the predicates (a moment letter whose id is an occurrence).
- **The register on every reader (§12's table).** `letter_payload` carries the dress for BOTH registers: `register`, `header` ("AN AFFAIR OF STATE — {DATELINE}" / "A MOMENT OF HISTORY — …"), `device` {kind arms | monogram | sheet, nation, letter} with the spec's flat `arms` / `monogram` beside it, `writer` / `office` (line 2), `line`, `ground`, `chapter`, `exhibit` ("" until RE-H), `counsel` (mirrored into `talleyrand_assessment`), `button_accept` / `button_decline`, `odds` 0; `proposal_type_display` per register. The mailbox row carries `register` and reads "The Secretariat — An Affair of State" with its own reason (`envoy_digest.ROW_REASON_AFFAIR`, which names the lapse); the lapse row and the dispatch's envoy list name the register; `first_open.SCREENS` gains `affair_letter` (the ninth; §12b.1's line, 217 characters) and `dialogue_screen` picks it by the payload's register; a moment's rows are byte-unchanged (no `register` key).
- **The voices.** `voice_of` reads an office's `holders` by the issued turn (§12's display table — the holder until its turn, then the authored name); a `host` speaker is the court's minister from the cast (`resolve_named_diplomat("envoy", host)` — Montgelas for Bavaria), "for the court of {seat}" as the office, and the chancery alone where the cast names none.
- **The button lines (P11).** `_receipt` is `plan()`'s `receipt` for EVERY letter: the authored `button_line` with the figures, else `_derived_button_line` — the plan's figures as short tokens ("−2 DP · −1,000 gold · Bavaria 60 → 80"; a law priced in authority says "standing 100 → 85"), cut at a token boundary to `BUTTON_LINE_MAX` 40. The admin refusal reads "the day's administration is spoken for." (39, the spec's words).
- **The Watch** rides `situation["affairs_watch"]` (`dispatch._build_situation`) only when the deck is armed — the unarmed dispatch byte-identical. **The driver** answers an affair from its own dial, `--affair accept|decline` (absent = decline; `POLICY_FLAG_KEYS` + `affair`, never `POLICY_DEFAULTS`), ahead of `--moment`.
- **BUG_FIXES RE2-1 — RE-1's defect, found by the register pins.** `build_letter` and `refresh_letter` pass every letter's STATUS ROW as the occurrence, and RE-1's `letter_payload` read `bool(occ)` as "this is an affair": every delivered MOMENT was dressed as an affair (register "affair") with the premise board of a predicate the affairs do not read — empty. The register is the occurrence id's (`is_occurrence`), the one discriminator the engine keeps everywhere else; the Match's board is the moments' own again, pinned. The sweep of the class (`bool(occ)` / `if occ` as a register test): `plan()`'s `if occ` binds selectors and is harmless on a status row; every other site keys on the id.

### 20.2 Built — the client half (commit B)

- **The ink** (`utils.gd`): `INK_BODY` 2B1D12, `INK_RUBRIC` 6A1410, `INK_SEPIA` 4E3820, `INK_RULE` 8A7A5A, `INK_SHEET_HC` EFE3C6 — constants, never retoned; the census pins that every inline colour the letter register emits is one of them (the S14c tokens remapped by `_ink`: the grey first-open line to sepia; the closed-Accept red, the gold header and the lapse line to the rubric; the grey assessment slot skipped).
- **The dress** (`incoming_proposal_popup.gd`, gated by `is_moment`; every other letter keeps the flat navy panel): a `StyleBoxTexture` over `old-parchment_alpha.png` (texture margins 48 / 40, expand 12, content 24) swapped in by `add_theme_stylebox_override` and the flat box restored for any other register; under High contrast a flat cream sheet under the same ink; the letterhead HBox at the VBox's head (the device 44 px — the court's arms by `Utils.nation_flag_path`, the owner's for the Secretariat's moments, a `PortraitLocket` monogram on leather for an office — the Cinzel dateline letter-spaced in the rubric, the seal well a faint wax-red ring); line 2 in the body — "**The Host's Claims** — Montgelas, for the court of Munich"; the body inked whole, the first-open line in sepia, the writer's line, the ground and the chapter in IM Fell italic (`[font=…]`), the exhibit in IM Fell roman under a rubric run-in ("FROM HAITI —" until RE-H authors `exhibit_from`), the board led by EB Garamond's hedera ❧ in the rubric, "WHAT EACH ANSWER DOES" in the rubric, the unanswered line in rubric italic; **the two-line buttons** (`caption\nbutton_line`, min height 56; "Not Now / waits on the desk"; a closed Accept on an opaque plaque with its reason as the second line when it fits the 40, else its price — the body's line carries the whole); **the counsel** in `_set_aside_line` (still a `Label.new()`), IM Fell italic at Caption in sepia, hidden when "". No `[font_size=]`, no size override, no `CanvasLayer.new()`.
- **The answer beat** (`play_answer_beat`, `main.gd`'s hook on `response.moment_answered` — the backend's own word; a refusal carries `diplomatic_dialogue` and never reaches it; Not Now writes no key): a parchment slip under the top bar's layer at the pressed button's rect (stored by `_on_accept` / `_on_reject`), the apostille "{caption}. — N." in IM Fell italic at Lead, the seal at 48 px with a 6° settle under a gold N cipher (`wax_seal.png` re-imported with mipmaps), the `wax_seal` cue (its first caller), freed after 0.8 s.
- **The readers.** `mailbox_panel.gd` tags an affair's row "Affair" (the pinned "Moment" entry kept); `dispatch_view.gd` prints one "IN THE OFFING:" line per `affairs_watch` entry after the law forecast.
- **The instruments.** `cap_moments` re-stages the Match and the Decree and adds `affair_letter_the_host` (tier 2, four corps on Swabia, the chest at 5,000 so the door stays out), `affair_letter_berthiers_memorial` (the chest at 20,000) and `affair_letter_closed_accept` (afield at standing 80, no action left); the SHOTS rows with `must_show` for the dress; the frames `IQ10_{MOMENT_LETTER_BAVARIAN_MATCH, MOMENT_LETTER_DECREE_OF_BERLIN, AFFAIR_LETTER_THE_HOST, AFFAIR_LETTER_BERTHIERS_MEMORIAL, AFFAIR_LETTER_CLOSED_ACCEPT}{,_X2}_2026_10_31.png` (the `_2026_10_22` frames stay as the S14c record); the UXR-4 frame list names them; the parse harness re-run (80 scripts, 0 bad); the readability census re-shot into `docs/audits/uxr0/readability_affairs_2026_10_31.json`.

### 20.3 The readings taken (each flagged in the approved plan or found while building; each reversible by a line)

1. **Line 2 lives in the body** at the body size (the title bold, the writer and the office), not a 17-px node: the scroll-where-unbounded census forbids a second code-built RichTextLabel and the ladder is exact.
2. **The dress is a pass over the composed letter** (`_dress_letter`, before `show()`), never a rewrite of `show_proposal`: the S14c literals and the S14h insertion windows stay where they were.
3. **A moment's second button line is derived** when no `button_line` is authored, and cut at the 40 at a token boundary — the Decree's "1 action" drops from the button and is read in the quote. RE-3 authors the moments' lines (P12).
4. **The first affair opens itself only when it heads the queue** on its morning; behind AI mail it opens from its card, its first-open line attached there.
5. **A quiet affair never holds the head against real mail** — `push` swaps a non-quiet dialogue over a quiet head; else a court's letter behind a standing affair got no popup for two turns.
6. **`correspondence`'s first-open line waits for RE-C** (its screen); only `affair_letter` joined `SCREENS`.
7. **The Watch renders on the Dispatch screen only**; the terminal's SITUATION receipt is RE-R's.
8. **Under High contrast the sheet is a flat cream under the same ink** — `Utils.contrast_node` raises mid greys only (luminance ≥ 0.15), so the ink stands and the letter is the highest-contrast surface in the client.
9. **The board's fleuron is a glyph** — EB Garamond's hedera (U+2767), measured present with a headless probe; the 10-px `[img]` of `fleuron_flowers.svg` (595 × 166 mm) aliased to a black square.
10. **The counsel is set in IM Fell italic** at Caption in sepia (the record's face, so the counsel reads as an aside in the same hand); the spec's "Caption italic" with the theme's face is one line away.
11. **A host speaks through the cast's minister**; where the cast names none the chancery writes alone ("The Chancery of X", no office line).
12. **The sheet fills PC-F46's box**: the letter grows with the window (0.8 of the viewport's height at 1600 × 900), so a short letter shows bare parchment under its text at 1.0 — the S15-head rule, unchanged; shrinking the box to the content is PC-F46's call, not this slice's.

### 20.4 Measured

- **The frames** (`tools/iq10_run_captures.py --only moment_letter,affair_letter`, windowed 1600 × 900 at 1.0 and 2.0): 0 `SCRIPT ERROR`; at both scales no button sits below a fold and the panel stands under the bar (y 90, 720 tall at 1.0; y 44, 394 tall at 2.0); the first-open line and the first answer's button are seen at both scales; at 2.0 the body scrolls as the spec says — "WHAT EACH ANSWER DOES" sits under the fold on the three affairs while both prices stand on the buttons.
- **The readability census** (five letters × five physical resolutions at the derived scales, 140 rows): RED 0, P1 0 (`readability_affairs_2026_10_31.json`); the 10_12 whole-client record untouched.
- **The parse harness:** 80 scripts, 0 parse or load failures; the boot smoke inside the captures 0 `SCRIPT ERROR`.
- **The series:** seven arms byte-identical to `BASELINE_SERIES`, every reach 0 (`tools/_affairs_series_arms_final.json` unchanged); the deck hash unchanged; the ratchet unchanged (commit A's hook: 37,494 passed).
- **The pins:** `tests/test_affairs_client.py` 39 (part 1 the backend, part 2 the client); `tests/test_moments_client.py` + 3 (extended, never replaced); `tests/test_first_open.py`'s tuple and `tests/test_affairs_engine.py`'s host voice and refusal words flipped consciously; the moments family green.

### 20.5 The done-when, item by item

- a staged affair arrives quietly and opens from its card, and the campaign's first opens itself ✓ (`TestTheQuietArrival`);
- both answers apply exactly their quotes through `/respond_to_diplomatic_dialogue` ✓ (RE-1's endpoint pin, re-run on the dressed payload);
- the frames show both answers above the fold at both scales ✓ (20.4);
- the harness exits 0 ✓; the series byte-identical ✓ (still unarmed — RE-3 arms the deck);
- the full suite green through the hook ✓ (both commits).

### 20.6 The sibling sweep (Rule 10)

- **The register's class** — every reader that hard-coded the moments' register (§12's table): `moments.DISPLAY` sites, `dialogue_manager.py` (the row), `envoy_digest.py` (the reason), `first_open.py` (the screen), `dispatch.py` (the lapse row, the envoy list), `mailbox_panel.gd` (the tag), `incoming_proposal_popup.gd` (the header); `display_names.py`'s `PROPOSAL_TYPE_DISPLAY` stays keyed by type — the payload's own display wins.
- **RE2-1's class** (a status row read as an occurrence): swept over `moments.py`, `affairs.py`, the trace and the sweep — one site, fixed; the rest key on the id.
- **The docs pin found by the hook:** `MODDING_FORMAT.md`'s `first_opens` row names every screen id (`test_tutorial_table_scenario.py`) — the ninth added.

### 20.7 What RE-3 inherits

The deck's arming (the scenario's `affairs` key copied from the fixture; the S14c sweep re-recorded; the suite-reach head of §19.5 re-seated); the writers' lines and the four moments' counsel lines (P12 — the dress draws `line` and `counsel` today; both "" on the shipped moments); the moments' authored `button_line`s where the derived ones fall short; `exhibit_from` for RE-H; the Correspondence's `correspondence` first-open line (RE-C).

---

## §21 RE-3 — the three armed — the landing record (✅ November 1, 2026)

*The third slice; the plan approved in Plan Mode; two commits in one session — part 1 the copy, the instruments and the arming-independent re-seats with the deck STILL UNARMED (`b0c05642`), part 2 the arming, the measure, the records and the pins that read them; the review pause taken before RE-H. From this commit the shipped 1805 scenario carries the recurring deck — `moments.affairs`, the fixture `tests/fixtures/affairs_block.json`'s block verbatim (the lockstep pinned) — and every player meets the Arch-Chancellor's Letters, the Host's Claims and Berthier's Memorial where their premises hold. The tutorial scenarios stay unarmed by design. H0 (the Haiti bill alone) is RE-H's first step, not this slice's (§16b's later, specific text): tier 1 "the letter" closes with RE-H's first step.*

### 21.1 Built — part 1, the deck unarmed (`b0c05642`)

- **The copy (P12).** The writers' lines for T1–T3 (`line`, ≤ 200, each in the writer's own voice — Cambacérès, the host's minister, Berthier); the reaction copy of §12c's table — `echo`, `situation` (a NEW authored answer key, ≤ 160, that RE-R renders), `press` and `remember` — on the fixture's deck; the four moments' counsel lines (Talleyrand on the Match, Holland and the Reich; Decrès on the Decree) and the Reich's authored `button_line` ("Austria {relation_before} → {relation_after} · the princes +10") on the scenario's dated deck, `tests/fixtures/moments_block.json` and the fixture's own copy of it, in lockstep (pinned). The dated deck's MECHANICAL hash is unchanged by copy: the sweep record strikes `counsel` and `button_line` with the display keys.
- **The tenure guard (P6) as authored data on the host voice** — `voice.tenure` {court: [{from: {date, turn}, to?: {date, turn}}]}: Hardenberg out 14 January 1806 (T8) to 30 April 1807 (T39); Schimmelpenninck gone from 5 June 1806 (T18); Cevallos gone from Bayonne, 6 May 1808 (T64 by the calendar — §12c's "after T60" was a round figure; the date is the authored fact). The validator checks each date against its turn (HC-0); the engine reads turns. `affairs.minister_of` (the cast's envoy through `resolve_named_diplomat`, "" inside a gap or where the cast names a chancery), `chancery_of` ("the chancery of the Kingdom of Italy" — the display name with its own article, never "the The"), the slots `{host}` / `{Host}`, `{seat}` / `{SEAT}`, `{minister}` / `{Minister}` and `{month}` (the previous occurrence's answered dateline) in `fill_slots`; every host of the 1805 roster renders clean (pinned).
- **The validator:** `situation`; `tenure`'s shape; a moment's `counsel` (≤ 160) and `button_line` (≤ 40 rendered, a slot counting four).
- **The instruments.** `--affair lapse` on the driver (the letter left standing to lapse on its answer-by turn — the lapse default the Rhine road is measured against); `tools/_s14c_sweep_record.py` reports the recurring deck's reach per arm (`affairs_reach` — each occurrence's fate, what each answer took, the mornings the premise held, the first due mark, ONE verdict word), carries the families `reach_aar` and `saves`, writes `deck_sha_note` itself; `tools/ai_v_sweep.py` no longer counts an affair's set-aside receipt as a moment crowded out (BUG_FIXES RE3-1); `tools/_vp1_road_arms.py --driver-flags`; the probe's control arm strips the deck and its armed arm reads the shipped block; `tools/_affairs_measure.py` (new) runs the nine commanded arms, the three accept arms, REACH-AAR and the six hand-played DD-B starts (`--from-save`, twenty turns on) with the trace, and composes the record. Smoked unarmed (every family runs; every reach 0).
- **The arming-independent re-seats:** the "unarmed" pins read an explicitly unarmed world; the save-manager backfill's no-op half reads a scenario without the key; `TestThePassiveBoard` holds the affairs' delivery down beside the sweep's seams; the accept arms' pin reads the dated deck's answers with the `#` rows apart. `tests/test_affairs_nondominance.py` (new, per §16 and the critics): three boards per template — a hoarder at the golden peace (40,000 gold, at peace, standing 100), an expander at war (the boot, Napoleon afield at Swabia, standing 85), a France that has spent its standing (72) — where the letter can arrive each answer is strictly better than the other on at least one delivered axis, the Decline touches no purse, no answer carries `alarm`, the letter is absent where `bites` fails.

### 21.2 Built — part 2, the arming and the measure (this commit)

- **The arming.** `godot-client/project-sovereign/assets/maps/europe_1805.json` gains `moments.affairs` — the fixture's block verbatim (227 lines, a text insertion keeping the file's own formatting); the three scenarios validate (the tutorials carry no `moments` key at all); `TestUnarmed::test_the_shipped_scenario_authors_no_affairs_key` flipped to `test_the_shipped_scenario_is_armed_as_ruled` (the lockstep, the mechanical keys `{owner, pacing, deck, affairs}`, the tutorials unarmed).
- **The kill switches first.** The series rig (`tools/_affairs_series_arms.py --jobs 4`, the record re-committed): every arm byte-identical to the prior `BASELINE_SERIES`, the reach now COUNTED — 39 armed ticks, 62 pulse draws, 0 delivered on the runner's passive board (the Emperor home, no corps quartered, the chest under the Staff's bar on `historical`), so `BASELINE_SERIES` is left alone with the reach recorded (reading 7). The unarmed CONTROL: the nine road arms on a scratch clone of the same commit without the key (`--affair lapse`), then the armed nine — **every arm UNMOVED to the turn** after RE3-2 (below): the Rhine road ends T34 / T40 / T28 and stamps T12 / T13 / never on historical / austerlitz / marengo, armed and control alike (`tools/_s14c_sweep_final.json` `road_control`).
- **The suite-reach head** (a scratch clone, armed; `-n 8 --dist loadgroup`): 35 assertion reds and 600-odd fixture errors. The errors were the clone's — every Godot-driven module (the clone has no import cache; the same modules pass on this tree) — and the bytecode-purge pins (`PYTHONDONTWRITEBYTECODE` in the shell). The reds that were the arming's, re-seated consciously: (a) five engine pins and one Watch pin whose crafted boards built at turn 1 read the BOOT's morning memo of the premises (the shipped boot is armed and reads its first morning before the test re-arms the board) — the `armed` fixture pops `_affairs_memo` (the nondominance pins had paid for the same trap); (b) the two "unarmed" pins flipped; (c) the deck hash and the record (re-measured); (d) the seal's `.import` file, untracked (RE3-3). No conftest pin was needed: nothing stays dormant.
- **The measure (ERR-3)** — 52 runs with the trace on the armed tree: the nine commanded arms and the three accept arms (`tools/_affairs_measure.py run`), the nine road arms (lapse) and Road I answered (accept), the 21 sweep runs (`ai_v_sweep.py --all`), REACH-AAR, the six hand-played DD-B starts; the first-arrival probe re-run (identical to the committed record on all ten seeds: Berthier at T19 on ulm and austerlitz, the moments' arrival turns identical armed against unarmed, 0 breaches). `tools/_s14c_sweep_final.json` re-recorded (the hash now `f5e50492…`, the deck note the tool's own; `affairs_reach` on every row; `road_control`; `context_drift`).
- **The driver's lapse mode (RE3-2)**, the judge's purse-in-passing (RE3-5) and the Watch's empty map (RE3-10, found by the hook: the boot briefing's Watch created `moments.affairs = {"watched": {}}` on the armed boot, and EP-F1's pin — a new world differs from a fresh one only by its briefing — caught it; the Watch writes on a shown line alone) — §21.4, §21.6.

### 21.3 The reach, re-measured (the done-when's table; seeded paths, not laws)

| Arm | T1 the Arch-Chancellor | T2 the Host's Claims | T3 Berthier's Memorial |
|---|---|---|---|
| CMD-A (hoarder) | never due (standing 100 all 40 mornings) | T15, T30 (declined / accepted on the accept arm) | T26 |
| CMD-H (conqueror) | T13, T28 on the accept arm | T23, T33 | T38 |
| CMD-M (middle) | never due (standing 100, then home) | T14, T26 | due, released (the chest never held the Staff's price on a free morning) |
| FC / DL / FLD / LAW / OP (the short arms) | OP at T13 | due, pending at the last morning (FLD, LAW, OP) | premise never held |
| VOLTE | T13 | T23, T33 | T39 |
| VP1-RH historical / austerlitz / marengo (lapse) | released / T26 / never due (held 19 mornings) | T13 / T14 / T14 and T27 — every one lapsed to its decline the next morning | T23 / never due (6 mornings) / T22 |
| Road I answered (accept) | — / T26 / — | T13 / T14 / T14 and T24 — 900, 600, 900 and 600 gold (the tiers) | T23 / released / never due |
| VP1-CS (three seeds) | never due | historical: T13, withdrawn T20 (free — the Act closed the host's matter); marengo: released; austerlitz: the run stops at T4 (RE3-8) | premise never held |
| VP1-TH (three seeds) | T21 / released / T14 | never due / T14 and T24 / T24 | T16 and T30 / never due / released |
| REACH-AAR (the treaty road) | released | T15, T25 | T32 |
| Hand-played Oct 24 — conquest / diplomacy / sea | — / — / — | — / — / — | — / T31 / T33 |
| Hand-played Oct 25 — conquest / diplomacy / sea | — / T29, T39 / — | — / T24, T34 / — | — / — / — |
| The 21 passive sweep runs | 7 (armB austerlitz and ulm, three scripted-France runs, armC ulm, austerlitz, marengo) | 3 (armB austerlitz, armC eylau, lodi) | 9 (six scripted-France runs, armB austerlitz and ulm, armC marengo) — the earliest letter of the tree, T7 on the scripted historical runs |

- **Totals:** T1 arrives on 16 of 52 runs (8 of the 25 scripted arms), T2 on 21 (17 of 25), T3 on 21 (10 of 25). The gate's §6.4 table was read at three corps and streaks ignored; at two corps (P6) the Host's Claims reaches more boards and **stays an event** — 17 of 25 scripted arms, never a passive France whose corps are home (the fraction recorded beside P6's 9 of 12).
- **Ceilings 0, floors 0 on every run; none fires with its premise false; shown = applied on every run** (the one context drift recorded apart, RE3-5).
- **The band (§14):** every Host's letter 300 × tier ≤ 900, every host's act ≤ 1,800; the Arch-Chancellor's standing ≤ 8 a letter, ≤ 16 an act; the Decline and the lapse touch no purse; the E1 band untouched — the earliest arrival on the tree is T7, the pulse's own first (`first ≥ 6`).
- **The Rhine road's end turns unmoved** with the lapse default on every seed, against the unarmed control (above). **ERR-3 is closed.**
- **The dated deck on today's tree** (the same control, not RE-3's): the Crown of the Reich fires on no measured arm (RE3-6 — M3's rule asks no vassal court for the crown and today's Pressburg subjugates Austria; marengo falls at T28); the Throne of Naples road never stamps and the Rhine road falls on marengo (RE3-7). Both for the user's ruling; the October 22 road record and its pins stand.

### 21.4 The readings taken (each flagged in the approved plan or found while building; each reversible by a line)

1. **The tenure guard is authored data on the host template**, never a table in the engine (RE-1's census forbids a nation literal in `affairs.py`); Cevallos at T64 by the date, the spec's "after T60" a round figure.
2. **A host whose cast minister is inside a gap, or whom the cast does not name, writes as its chancery** — "the chancery of the Kingdom of Italy"; a cast name containing "chancery" counts as one (no office line). The cast wins where §12c guessed.
3. **`situation` is an authored answer key** (≤ 160): §12c's SITUATION column has its own sentences; RE-R renders a key that exists. `{n}` is not used in the letter's copy (the row freezes host and tier; a count would drift on a standing letter).
4. **The moments gain `counsel` and ONE authored `button_line` (M3)**; nothing else on the dated deck; both struck from the measured identity.
5. **The lapse default is `--affair lapse`** — the letter left IN THE MAILBOX, unopened, to lapse on its answer-by turn; `decline` (answered on arrival) stays the driver's default, `accept` the accept arms'. A driver that opened the letter each turn moved the Rhine road for a reason that was never the letter's (RE3-2).
6. **One record, not two:** `affairs_reach`, `road_control` and `context_drift` live in `tools/_s14c_sweep_final.json`; the nine commanded arms stay exactly nine; the October 22 road record is not re-recorded.
7. **`BASELINE_SERIES` is left alone with the reach recorded** — the runner's passive board delivers nothing; the seams count 39 ticks and 62 draws.
8. **The suite-reach head ran on a scratch clone**, classifying only; a fixture that builds a crafted board on the armed boot pops the morning's memo (the memo is the morning's reading, by design; a test that mutates the board inside the same turn must drop it).
9. **A quote that differs only in the purse it names in passing is context drift, not a mismatch** (`strip_context`); a figure off its quote is still seen.
10. **The Crown's reach is reported, not forced:** the floors pin and the accepted-set pin ask for the Match and Holland, and for the Crown where it fires, with its fate per arm (RE3-6 for the user).
11. **The five letters were re-shot under their RE-2 names** (`_2026_10_31`) in part 1 — the writers' lines and the counsel change every frame.

### 21.5 The done-when, item by item

- every template's reach reported per seed and per save ✓ (21.3; `tests/test_affairs_reach.py`);
- none fires with its premise false ✓ (0 premise ceilings, 0 silent floors on 52 runs);
- the ceilings hold ✓ (0 on 52 runs; the sweep's own ceilings on all 21);
- the Rhine road's end turns unmoved with the lapse default ✓ (against the unarmed control, every road and seed);
- the totals sit in §14's band ✓ (21.3);
- the full suite green through the hook ✓.

### 21.6 The sibling sweep (Rule 10)

- **RE3-2's class** (an instrument that opens what a player would leave shut): the letter-book pass answers only its own rows (an affair never rides it); the first affair that opens itself on its morning is left standing by the dial, not re-activated; the sweep's passive France never opens the mailbox. One site, fixed.
- **RE3-3's class** (a tracked asset's untracked `.import`): 190 more under the same ignore line — RE3-9, for the user at S15's head.
- **RE3-5's class** (a context figure compared as a promise): one site, the judge; the receipt's "(the treasury holds N)" and "(you hold N)" are the two phrases.
- **The memo's class** (a crafted board read through the boot's morning): the `armed` fixtures of the engine and the client pins, the Watch pin; the nondominance pins had already popped it.
- **RE3-10's class** (a read that creates the runtime key): `runtime()` creates the key on an armed world for any caller; the Watch now writes on a shown line alone (the boot briefing on a passive opening shows none, so `moments` is born equal to a fresh boot — EP-F1's rule); the tick, the receipts and the answers write only what happened.

### 21.7 What RE-H inherits

H0 the Haiti bill alone, then the squadron (§6.5, §16b); `exhibit_from`; RE3-8 at its head (the driver answers the objection it can afford); the reach review of RE-5 reads §21.3 — no template has zero reach across the arms and the hand-played starts, so none is up for deletion by that rule; the user's rulings on RE3-6 and RE3-7 before S15.

---

## §22 RE-H — the Haiti letter — the landing record (✅ November 1, 2026: H0 the bill alone, then the squadron)

*The fourth slice; the plan approved in Plan Mode; two landings, each its own commit through the hook — H0 the bill alone (tier 1 "the letter" closes with it), then the squadron (tier 4). At the head, RE3-8 (the driver answers the objection it can afford). The user's word at the plan's review, November 1, 2026: "we want to make sure these events are good, have conditions that make them appear and don't make the game repetitive … fun factor high" — read as P16's amendment (§0b) and as this record's first paragraph.*

**What the letter adds, in plain words.** Decrès, Minister of Marine, writes when Britain has had France blockaded on four of the last twelve mornings, the Emperor at court or at headquarters (the first measure's at-home clause was dropped the same evening by the user's word — §22.4), the fleet has 25 sail in port and the chest holds 1,500 — the first winter of nearly every campaign whose Emperor stays in France, and the quiet seasons between campaigns afterwards; never while the Emperor marches with the army (the Arch-Chancellor writes then), never at peace with Britain (the latch empties in twelve mornings). On the passive board it is the campaign's first letter of state, at turn 6–9. The bill is a fork with a plain cost on each side — 600 gold and the day's action for honour, or three points of standing for thrift (a dent at full standing, a wound across the aura's line at 85) — and the letter says why it was written: Haiti's own words under "FROM HAITI —", the ground of 1802–1804 on every arrival, and a chapter that never repeats in a row (the killings of 1804 and Ferrand's decree the first time; Ferrand's bread the second; the last squadron's fate, once the squadron lands). Against repetition: twice an act at most, twelve turns apart, a gap of five mornings from any other letter of state, two exhibits alternating, two forms by the sea's state, and a file that closes at Ferrand's death in November 1808. The squadron — five of the line at the naval module's own odds, the Admiralty showing them at sea and the fate landing as one amber morning line — is the second landing's.

### 22.1 H0 — the bill alone — ✅ LANDED November 1, 2026

**Built.**
- **The deck** (`tests/fixtures/affairs_block.json` and the shipped `europe_1805.json` in lockstep, pinned): `santo_domingo`, `shape bill`, "The Relief of Santo Domingo", Decrès's named voice, `when: colony_cut_off {min_ships 25, min_purse 500}`, `streak 1`, `latch {of 12, at_least 4}`, `bites: "floor"`, `cooldown 12`, `cap 2`, `grace 4`, `ends` 1808-11-07 / T76 (the deck's first), the ground, four chapters (`last_fate` home / caught authored before `arrival` later), two exhibits alternating under `exhibit_from` "FROM HAITI —", the `{wrote}` slot ("last February" to T26, "two years ago" from T27), the Watch, Berthier's counsel, the two closing lines (RE-C renders them), Accept "Send flour and muskets" (600 gold, one action) and Decline "Ferrand must hold alone" (−3 standing, grip-floored) with their echo / situation / press / remember copy.
- **The engine** (`affairs.py`): the predicate `_colony_cut_off` — the latch bit first (blockaded this morning by the trade-dominant power; `naval.blockader_against` against `naval.trade_dominance_nation`), then the sovereign not captive (at home until §22.4 dropped the clause the same day), the sail in port, the purse above `min_purse` + `AI_PURSE_RESERVE`; `latch_count` / `latch_distance` (the Watch's `{n}` and its distance to due; the Watch silent past `ends`); `bites()` reads `BITES_MODES` (`true` both halves, `"floor"` the floor half); `VARIANT_FACTS` + `last_fate`, `VARIANTS_MAX` 4; `exhibit_of` (a list walks the arrivals); `authored_slots` and `{date}` in `fill_slots`; the board's two lines (the latch's count and the Emperor's seat; the hunter's sail against ours, or the open sea). `moments.letter_payload` reads `exhibit_of` and passes `exhibit_from` only when authored — the engine spells no colony (pinned).
- **The validator:** `colony_cut_off`'s params and the owner's `navies` row; `bites` `true | "floor"`; four variants with `value` on the fact's list; the exhibit list with its required run-in; `closing`; the `slots` table (dates against turns — HC-0; the last entry open); sixteen refusal rows added.
- **RE3-8:** the reply to `/respond_to_objection` carries the refusal's own `objection_kept` and `choices`; the driver answers the first open road (trust → compromise → cancel) when the policy's answer cannot be paid and says so once. VP1-CS austerlitz now runs to T24 on the armed arm and the control alike (the Emperor falls there), where it stopped at T4.
- **NV-D5's pin** (P5): `tests/test_nv_d5_colonial_copy.py` — the allow-list scan (string literals; docstrings, comments and bare keys are not surfaces) over the backend and the client scripts and the scenario outside `moments.affairs`; nine allowed rows, each live.
- **The instruments:** the road CONTROL is the same tree with the engine held unarmed through the driver's own seam (`--seam backend.game_logic.affairs:armed=False`); `tools/_s14c_sweep_record.py` reads the standing figure from "Authority N → M" as well as "standing N → M" (REH-1); the frames `IQ10_AFFAIR_LETTER_SANTO_DOMINGO_BILL{,_X2}_2026_11_01.png` and the readability record `readability_affairs_2026_11_01.json` (RED 0 / P1 0 at five resolutions).

**The readings taken (each a line to reverse).**
1. **P16 amended for the Haiti letter** — `bites: "floor"` (the user's word; §0b). The old reading: `"floor"` → `true` in the deck.
2. **Four chapters, keyed by `arrival` and `last_fate`,** the fate chapters authored first; `chapter_of` takes the first match in authored order.
3. **The exhibit is a list the arrivals walk,** under an authored `exhibit_from`; the engine holds no "FROM HAITI" literal (the client's default is a fallback only); the quotation marks are typographic (‘ ’).
4. **The `slots` table** is authored data (dates checked by the validator, turns read by the engine), not a rule in code.
5. **The closing record and the 1825 line are authored now** as display keys; RE-C prints them (§12b.1 owns the Correspondence).
6. **The road control is the in-tree seam,** not a scratch clone (RE-3's clone control stands as its record).
7. **No new measure family:** with the aura half waived the letter reaches the spec's own arms (the sweep, the treaty road); the squadron's movers are attributed on the accept arms and crafted boards at the second landing.
8. **`BASELINE_SERIES` re-pinned with the attribution** (below) — the letter premises on the passive board by the user's word, so the unattended France's series moves; arm 0 and AF0 of the rig reproduce RE-3's series byte for byte.
9. **The door's pin keeps the fleet under 25 sail** (`test_the_door_arrives_at_war_with_the_chest_above_the_bar`), so it reads Berthier's door alone where the Marine's letter would have taken the morning.
10. **A passive France's lapse costs 3 standing** (the lapse is the Decline, §6.5) — on the passive board 75 → 72 at T9.

**Measured — 52 runs with the trace (`tools/_s14c_sweep_final.json`; the hash `bc919f82…`).**

| Arm | The Haiti letter | The three (unchanged in kind) |
|---|---|---|
| The 21 passive sweep runs | **arrives on 15** — the campaign's FIRST affair on 13 (T6 on jena and lodi, T7 on historical, eylau and rivoli, T9 on ulm and austerlitz; T16 on the scripted austerlitz runs after the Memorial), a second letter at T19–T22 on four (lodi, rivoli, the scripted ulm pair); every one lapsed (−3 standing; 1 on rivoli's second and 0 on lodi's where the floor clamped); never due on austerlitz and marengo (the Emperor driven from home by T3), friedland and wagram (held 24 / 20 mornings, the latch empty — peace with Britain) | T1 7, T2 2, T3 9 |
| REACH-AAR (the treaty road) | **T23 and T38** (90 → 87, 77 → 74), the cooldown of twelve between; declined on the driver's dial | T2 T15 / T25, T3 T32 |
| CMD-A / CMD-H / VOLTE / FC / DL / FLD / LAW | premise never held — the Emperor marches with the army (the Arch-Chancellor's domain) | as RE-3's |
| CMD-M | held 18 mornings from T24 (the Emperor home), never due — the white peace with Britain emptied the latch | as RE-3's |
| OP (20 turns) | due T14–T19, pending at the last morning (the desk busy) | — |
| The three accept arms | as the commanded (the Emperor afield) | the bills accepted as RE-3's |
| VP1-RH / CS / TH (lapse) and Road I answered | never — premise never held (afield), or due and released / never due where peace with Britain came first (CS historical and marengo; RH austerlitz 11 mornings; TH marengo 25) | the Host T13 / T14 / T14 … as RE-3's |
| The six hand-played T21 starts | never due (held 20 / 20 / 5 mornings on the October 24 diplomacy and sea boards and the October 25 sea board; the rest afield) — peace with Britain by T19, the latch behind the save | as RE-3's |

- **Totals:** the Haiti letter on 16 of 52 runs (1 of the 25 scripted arms — the treaty road — and 15 of the 21 passive); T1 on 16, T2 on 20 (17 of 25 scripted; one passive arrival moved — eylau's dice shift under the lapse's standing), T3 on 21. Ceilings 0, floors 0, none with its premise false, shown = applied on every run.
- **The band (§14):** every Haiti Decline 3 or less (the floor clamps it); ≤ 6 an act; the Decline and the lapse touch no purse; the earliest arrival on the tree is now T6 (the pulse's band low, on jena and lodi), T7 on `historical` — the E1 band (T1–T5) untouched.
- **The standing figures are read for the first time** (REH-1): the Arch-Chancellor's lapses 5 and 8, the Haiti lapses 3 — RE-3's "≤ 8 a letter" held, measured on nothing until now.
- **The roads unmoved** against the in-tree control on every arm and seed — the Rhine road T34 / T40 / T28, stamps T12 / T13 / never; VP1-CS austerlitz T24 on both (RE3-8).
- **The first-arrival probe** (`tools/_affairs_first_arrival.json`): the first affair is the Haiti letter on nine of ten seeds (T6–T9), none on wagram; the moments' arrival turns identical armed against unarmed on every seed; 0 breaches.
- **The ambient series moved, attributed** (`tools/_affairs_series_arms_final.json`; `BASELINE_SERIES` re-pinned): the letter lapses at T9 on the passive board (standing 75 → 72); `authority_vassal_drift` — the one-way coupling of the Emperor's faltering grip to his clients' loyalty — takes Holland into rebellion at T19 instead of T20 (the alarm's −10 at index 18: 0, was 3; the hegemony's passive +3 shows as 2 at index 25), and the unattended France falls at T38 instead of T40. Arm 0 (every seam down) and AF0 (`deliver_due` down) reproduce RE-3's series byte for byte; every arm with the delivery up diverges at index 18 with one occurrence delivered.
- **The dress:** the frames at 1.0 and 2.0 (both prices on the buttons at 2.0, the writer's line and the record's head above the fold); the readability census RED 0 / P1 0.

**The done-when (the hand-over's), item by item:** the fixture and the scenario in lockstep ✓ (pinned); the reach reported per arm and per hand-played start ✓ (above; `tests/test_affairs_reach.py`); `set(MO.OPS)` unchanged at 9 — H0 adds no op; the flip to 10 is the squadron's ✓; no new `WorldState` field ✓; the dress draws the new letter ✓ (the frames); the frames re-shot ✓; the full suite green through the hook ✓ (this commit).

**The sibling sweep (Rule 10).** REH-1's class (a record read on the wrong word): the gold lump reads "(the treasury holds" — the quote's own phrase ✓; the trace's `_delivered` compares figures, never words ✓. RE3-8's class (a reply that drops the executor's own keys): the strategic objection's refusal (`_handle_strategic_objection_from_endpoint`) rides the same `_respond_to_objection_sync` ✓; the typed road (`_pending_answer_token`) reaches the same function ✓. The `bites` amendment's class: T1 keeps both halves by design (the Council acts for an unbroken Emperor); no other template prices standing. The ambient series' class: the three pins that read `BASELINE_SERIES` import the one constant ✓.

### 22.2 The squadron — ✅ LANDED November 1, 2026

**Built.**
- **The op** `squadron{ships, away, to}` — `set(MO.OPS)` 9 → 10, flipped consciously (`test_moments_engine.py`, `test_affairs_engine.py`); `moments._plan_squadron` quotes through `naval.squadron_quote` (the sail in port before and after, the odds, the hunter, the expected return; the refusal with no fleet, under `ships` + 20 in port, a squadron already at sea, or **no hunter at sea** — a squadron at 100 is a sale, the bill is that road), the line as §6.5 quotes it ("five of the line sail (45 → 40 in port until {date}) — 36 in 100 they come home whole; caught, the five are lost and the men are ashore"); `_apply_squadron` → `naval.detach_squadron`; `plan` stamps the occurrence id as the op's `tag`, so the fate finds its row; the receipt's `{odds}` / `{ships}` figures, the derived button arm, `letter_payload["odds"]`, the row's `home_by` (`{date}` in the reaction copy).
- **The odds** — `expedition_slip_odds(world, lord, None, 0, escort=ships × readiness / 100)`: a third override beside `window` and `escort_extra`, every live caller passing none; the open-water arm (guard fleets skipped, blockade fleets hunt). At war against Britain's 100 sail the ratio sits on the cap for any squadron of eight or fewer — **36 in 100** (36.5 rounded half to even, pinned); with a window won 62 / 64 / 71 at readiness 50 / 70 / 80; no hunter → the quote refuses.
- **The voyage** — `naval.detach_squadron` writes `rec["ships"] -= ships` and `rec["squadron"]` {ships, readiness, sailed, returns, to, odds, tag, issued}; `naval._squadron_tick` in `process_naval_turn` after `_readiness_tick`, over `iter_fleet_records` (a squadron outliving a Trafalgar still settles): the squadron **drills at sea** (`READINESS_TICK` a turn toward 100 — reading 0b, the §3.3 sea-time rule; 70 → 90 over four turns), and on its morning the one draw `seeded_int(seed, "naval::squadron::{issued}::{lord}::{tag}", 0, 99) < odds` — home: the ships fold back at their sea readiness (`lay_down_ship`'s fold; the annihilated fleet takes them back whole); caught: lost whole; `rec["squadron_last"]` {tag, sailed, returned, outcome, ships, lost, odds, draw, readiness, to}. No battle clock, no diorama, no rail notice.
- **The settlement** — `affairs.settle_squadrons`, the affairs tick's first step: the row's `outcome` / `outcome_turn` / `outcome_line` (the Accept's authored `outcome` copy by fate) and its `receipt` ("… — home whole" / "… — five of the line lost"); one `moment` log row with phase `outcome` (the line, the Moniteur's `press`, the figures). **The fate's morning line** (reading 0c, pulled forward from RE-R): `situation["affair_fate"]` from `affairs.fate_lines` (the rows whose `outcome_turn` is the morning), printed amber as "THE SQUADRON: …" in both views that print the Staff's line (`dispatch_view.gd`, `main.gd`).
- **The two forms** (P18) — `forms.squadron {requires: hunter_at_sea, title "The Squadron for Santo Domingo", line, counsel "Five sail are five sail, Sire; Boulogne counts them too.", accept {gold 500, admin 1, squadron 5 / 4 / Santo Domingo; echo, situation, remember, outcome {home, caught}}}` and `forms.bill {}` — the entry's own title, line, counsel and Accept are the bill (`_answer_side`, `title_of` and `form_block` fall back to the entry). `affairs.form_of` takes the first form whose `requires` holds (`naval.squadron_hunter` — a blockade-posture enemy at war), else the fallback; frozen in the row at delivery; `refresh_letter` re-plans the frozen form, and a hunter that left the coast closes the Accept with the quote's own refusal — never a silent re-plan.
- **The memory** — `_deliver` freezes `last_fate`, `last_sailed` and `last_ships` from `naval.last_squadron`; the chapter reads `last_fate` (Missiessy home / Leissègues caught) and the board prints "Your last squadron sailed {date}: home whole | five of the line lost."; the squadron form's board prints "The passage: {odds} in 100 to come home whole."
- **The Admiralty** — `build_admiralty_report` → `own_fleet["squadron_line"]` ("Five of the line are at sea for Santo Domingo, readiness 70; expected home by Late February 1806."), drawn amber beside the rot line (`strategic_ledger.gd`); the parse harness re-run (80 scripts, 0 bad).
- **The validator** — the op's bounds (ships 1–8, away 3–6, `to` ≤ 32), Accept-only, one per entry, a fallback form required, the owner's `navies` row, `when.min_ships ≥ ships + 20`, `requires` on the engine's list, the `outcome` copy complete on the squadron's Accept and absent elsewhere; eleven refusal rows added.
- **The instruments** — the trace's `_delivered` squadron arm ("sail in port") and the fate row (`settle_squadrons` wrapped: the frozen odds, the draw, the outcome); the record tool prints the fate on the occurrence line; the `haiti` family in `tools/_affairs_measure.py` (reading 7); the seams **AFH** (`naval._squadron_tick`) and **AFS** (`affairs.settle_squadrons` + `naval.detach_squadron` — the setter `_apply_squadron` calls by name, because the OPS table binds the apply function at import) in `tests/_affairs_seams.py` and the series rig with their reach counted.
- **The frames** — `IQ10_AFFAIR_LETTER_SANTO_DOMINGO_SQUADRON{,_X2}_2026_11_01.png` (the blockade's form) and the bill re-shot after a peace (`…_BILL{,_X2}_2026_11_01.png`); the readability record covers both at five resolutions, RED 0 / P1 0.

**The readings taken (each a line to reverse).**
1. **The squadron drills at sea** (reading 0b): `READINESS_TICK` a turn toward 100 while away, folded back on return — the honest small upside for the Accept at full standing; no new op, no reward figure. Reverse by one line in `_squadron_tick`.
2. **The fate's morning line lands here, not at RE-R** (reading 0c): `situation["affair_fate"]`, both views, amber. RE-R keeps the answers' receipts, the echo, the COURTS predicate, the remarks and the `remember` line.
3. **No hunter at sea refuses the squadron's quote** (P2 / P18's letter): a letter frozen in the squadron form whose hunter leaves the coast closes its Accept with the refusal; the player declines or lets it lapse. The bill form is the open sea's answer at delivery.
4. **The fallback form is `{}`** — the entry's own copy and Accept are the bill; the validator requires one form without `requires`.
5. **The AFS seam is `naval.detach_squadron`,** not `moments._apply_squadron` (the OPS tuple binds the function at import, so a seam on the module attribute would not bite).
6. **The `haiti` measure family** (reading 7): a passive France at home under the blockade with the accept dial on the three benchmark seeds — the one family that sails; the spec's own arms never do (the commanded Emperor marches, the passive runs lapse, the treaty road declines).
7. **The letter's own name on every reply and row** (REH-2): `moments.letter_title`.
8. **`last_ships` rides the row** beside `last_fate` and `last_sailed`, so the board's "five of the line lost" never reads a later sailing.

**Measured — the same 52 runs re-run on the squadron tree (the hash `a929539dfcf7`), plus the `haiti` family.**
- **Byte-identical reach on every spec arm:** the Haiti letter on 16 of 52 (the 15 passive sweep runs and the treaty road twice), T1 16, T2 20, T3 21 — the form changes nothing where the letter lapses or is declined; ceilings 0, floors 0, shown = applied; the roads unmoved against the in-tree control (the Rhine road T34 / T40 / T28, VP1-CS austerlitz T24 on both); `BASELINE_SERIES` unmoved from H0's (the passive France lapses, so nothing sails — the series rig's AFH / AFS arms byte-identical with their reach counted); the first-arrival probe identical to H0's on every seed.
- **The squadron sails on the `haiti` family alone:** on `historical` the letter at T7 and the squadron sent at once: HOME at T11 (36 in 100, drew 18), the five back in port with their crews drilled at sea, the flour and the muskets landed, the passive France falling at T38 all the same; on `austerlitz` the letter at T14 and the squadron CAUGHT at T18 (drew 93): five of the line lost, Decrès asking for an inquiry; on `marengo` never due (the premise held two mornings only; the France falls at T33). Two sailings, one home and one lost, reported per seed and never a law.
- **The squadron's movers on Britain's reads** (pinned on the boot board): the blockade verdict, the trade loss and the Diversion odds unchanged; the fleet-action ratio against Britain worse by the five sail's share (under 15 %).
- **The alarm untouched** across the sailing, the tick and the settlement; `test_france_authors_no_overseas_pool` unchanged; a mid-voyage save round-trips the nested `squadron` key.

**The done-when (the hand-over's), item by item:** `set(MO.OPS)` 9 → 10 flipped consciously ✓; no new `WorldState` field ✓ (the squadron rides the fleet record and the occurrence row); the dress draws both forms ✓ (the frames); the frames re-shot ✓; the reach reported per arm and per hand-played start ✓ (above); the full suite green through the hook ✓ (this commit).

**The sibling sweep (Rule 10).** REH-2's class (a letter named by its entry where its form has a name): the rail card and the mailbox row read `payload["title"]` ✓ (RE-2); the lapse gate rows and the lapse's dispatch line now read `letter_title` ✓; the Correspondence (RE-C) must read `title_of(e, row)` — noted in its prompt. The `escort` override's class (a counterfactual that could become a second model): `window` and `escort_extra` keep their one caller each ✓. The "no hunter refuses" class: the Diversion's own refusal at peace (`naval.diversion_hostile`) is the same shape ✓.

### 22.3 What RE-C inherits

The Correspondence (§12b.1): the desk, the answered page with the apostille, the `receipt` / `echo` / `outcome_line` the rows now carry ("At sea — five of the line; word expected about {date}" from `home_by`, then the fate), the closing record and the 1825 line from the Haiti template's `closing`, `letter_title` for every row, the chips; `first_open` gains `correspondence`; the frames at both scales. Open for the user: RE3-6, RE3-7, RE3-9; RE-5's reach review reads §22.1's table.

### 22.4 The clause dropped — Decrès writes to headquarters (the user's word, November 1, 2026, the same evening; ERR-5)

**The word.** At RE-H's review the user ruled: *"I agree with 'Let Decrès write to headquarters.' The Haiti letter requires the Emperor at home, so the player who marches never sees it. Napoleon read the Marine's dispatches in the field. Dropping that one clause is a line in the premise and the Watch."* §6.5 clause 2's **at home** is struck; "standing, not a captive" stays. The same review queued **row AU — authority as a currency, the push and the pull** — after RE and before S15 (`docs/AUTHORITY_CURRENCY_SPEC.md`).

**Built.** `_colony_cut_off` no longer reads `nation_starting_regions`; the bind's `region` is wherever the sovereign stands. `_board_colony_cut_off` says where the letter found him — "the Emperor holds court at {region}" at home, "the letter reaches headquarters at {region}" in the field, "the letter reaches the Emperor" with no region. The Watch loses "the Emperor at home" (the fixture and the scenario in lockstep; the deck hash unmoved — the Watch is display copy). **Pins:** the afield board now HOLDS with its bind at Swabia and a captive still silences it; the board's three readings; the Watch; the alarm census on the commanded board gains the fourth letter at T27 (`test_the_alarm_is_never_touched_by_an_affair`); the nondominance boards measure H1 wherever its premise holds; the reach pin re-seated (below).

**Measured — the same instruments, re-run on the dropped-clause tree (55 runs).**

| Family (runs) | The Haiti letter, before ERR-5 → after | Where it changed, and why not |
|---|---|---|
| the passive sweep (21) | 15 → **17** | `armC_02_austerlitz` and `armC_04_marengo` at T14 — their ambient Emperor stands afield; two runs gain a second arrival (T23, T30) inside the cooldown of twelve |
| the commanded arms (9) | 0 → 0 | due at T6–T9 on CMD-A / CMD-H / CMD-M / VOLTE, then RELEASED: the driver's `diplomacy: accept` makes peace with Britain by T10–T19, the latch empties within twelve mornings, and the one free morning in the window went to the Host's Claims, whose premise had stood since T2 against the Marine's T4 (`affairs.pick` — the matter that has waited longest); FLD / OP due but pending at their short end (10 / 18 mornings); DL / LAW / FC never due |
| the accept arms (3) | 0 → 0 | as the commanded arms |
| the roads, lapse (9) | 0 → **2** | `VP1-TH-historical` T13 and T28; `VP1-RH-historical` T23 — the marching Emperor, the war with Britain kept; the other seven release it with Britain's peace |
| the roads, accept (3) | 0 → **1** | `VP1-RH-historical` T23 accepted in the squadron form: the five CAUGHT at T27 (36 in 100, drew 94) |
| the treaty road (1) | 1 → 1 | T23 and T38, as before |
| the T21 saves (6) | 0 → 0 | peace with Britain by T19, the latch windows behind the save |
| the `haiti` family (3) | 2 → **3** | `marengo` now T16 (its Emperor had been driven from home): the five CAUGHT at T20 (drew 69); `historical` HOME at T11 (drew 18) and `austerlitz` CAUGHT at T18 (drew 93) unchanged |

- **The letters trade places; the deck's total barely moves.** The Marine's letter, reaching the field, took mornings from the Arch-Chancellor's on four sweep runs and from the Memorial on two: the Arch-Chancellor 16 → 12 runs of 55, the Memorial 21 → 19, the Host 21 → 22, the Haiti letter 18 → 24; affairs per run on the passive sweep 2.19 → 2.24, on the roads 1.67 → 1.78, on the commanded arms 1.67 unmoved. The pulse's gap of five and the letters' cooldowns, not the deck's size, set how many letters a campaign sees — a fifth letter adds variety before it adds volume until the pulse is loosened (a reading for RE-5's review, beside RE3-6 and RE3-7).
- The roads: unmoved against the in-tree control on all nine arms (the lapse's −3 on `VP1-TH-historical` at T14 and T29 and on `VP1-RH-historical` at T24 moved neither an end turn nor a stamp). `BASELINE_SERIES` unmoved (the rig's ALL arm byte-identical to the standing series; arms 0 and AF0 reproduce RE-3's, as before; the record `tools/_affairs_series_arms_final.json` unchanged) (the passive board already held the Emperor at home). The first-arrival probe identical on every seed (the Marine's letter the campaign's first affair at T6–T9 on nine of ten; `wagram` none). Ceilings 0, floors 0, shown = applied on all 55.

**The sibling sweep (Rule 10).** The Arch-Chancellor's letter keeps its `sovereign_afield` clause: the two letters may now both come to the field, five mornings apart by the pulse (the commanded board's census shows the order — T1 at 7, the Host at 12, T1 at 17, the Host at 22, the Marine at 27). No other template reads the sovereign's seat (the Host's Claims read the corps' quarters; the Memorial reads the war and the chest); no other Watch line names a seat. The spec's own at-home sentences — §6.5 clause 2, the Reach paragraph, the board and Watch lines, H0's paragraph, §22's opening and §22.1's engine line — are amended in place with the date; `SYSTEMS_REFERENCE.md` §164.1's row and §164.3; STATUS; the next prompt.


## §23 RE-C — the Correspondence, the home of the letters — the landing record (✅ November 1, 2026)

**What the page adds, in plain words.** A letter of state used to be a popup and then nothing. The Correspondence is a page of the Morning Dispatch, turned by a button in its action row — "The Correspondence (1 standing)" in amber when a letter waits, "(a squadron at sea)" while five of the line are out, plain otherwise, absent on a world whose scenario carries no deck — and turned back by "◂ The Dispatch". One column of parchment slips: **ON THE DESK** (the letters that wait: the answer-by date in rubric with the court's arms or the minister's monogram, the title and the writer, both priced answers, the chip Read the letter ▸ that closes the page and opens the letter), **IN THE OFFING** (the Watch's one or two lines, text only), **ANSWERED** newest first (the dateline and the title in rubric; the apostille — a wax seal and "{caption}. — N." in IM Fell italic; what it did, the receipt; what came of it, the echo dated the next morning or "At sea — five of the line; word expected about {date}." and later the fate in rubric; the chips from the consequence to its remedy — the court's Cabinet page, Admiralty ▸, Laws ▸), **LEFT UNANSWERED / SET ASIDE** (one dim line each), the closing record and the 1825 line when the Haiti file closes, and three empty states. The first visit carries one sepia line that never returns. Read-only but for Read the letter ▸: no badge beyond the button's count, no sound, no hotkey, no new endpoint — a page the player re-reads, not a loop.

### 23.1 Built

- **The builder** `moments.correspondence(world)` — pure (a `GET /dispatch` writes nothing: `to_dict` byte-identical before and after, `runtime["watched"]` untouched), cheap (one pass over `world.moments["state"]`, no region scan), `{}` unarmed. `standing[]` — every `fired` row: the title through `letter_title`, the writer and the office through `voice_of` / `_writer_and_office`, the device through `device_of`, `answer_by` = issued + `ANSWER_TURNS` − 1 with its dateline, both answers' captions and receipts from `plan`, the `mailbox_id` through the new `mailbox_id_of` (the dialogue manager's scan `lapse_gate_rows` runs). `answered[]` newest first — the caption derived by `_answer_side`, the row's `receipt` and `echo` with the echo dated `answered_turn` + 1, `at_sea` from the fleet record's `squadron` tagged with the row's id, `fate` from the row's `outcome` / `outcome_turn` / `outcome_line`, the chips (the court from the bound host, the envoy's nation or a moment's `when.court`; the Admiralty for a `squadron` op; the Laws for an `enact_law` op). `offing[]` = `affairs.watch(world, record=False)` (the new keyword; the morning builder keeps `record=True`). `set_aside[]` newest first (lapsed, withdrawn, crowded). `closing[]` = `affairs.closing_record(world)` (new). `empty{}`, `button`, `counts`, `at_sea`; every figure an int.
- **`GET /dispatch`** carries `payload["correspondence"]` with `first_open.attach(…, "correspondence")` on the fresh dict; `first_open.SCREENS` gains `correspondence` and its authored line (195 characters); `MODDING_FORMAT.md`'s `first_opens` row names it.
- **The client** (`dispatch_view.tscn` / `.gd`): the scene authors `CorrespondenceScroll` (a floor of 160 px — the floorless-scroll ratchet sits at its cap) with `CorrespondenceBox`, and the two buttons; the script holds the page state (`_corr`, `_corr_open`, `_corr_pending_open`, `_corr_scroll_hold`), reads the page's dict FIRST in `_on_dispatch_received` (before the failure and empty returns; the driven harnesses' hand-built responses carry no key and hide the button), renders the slips (`_add_slip`: a `PanelContainer` wearing the parchment's un-torn inner field as a `region_rect` — the first on this texture — a Cinzel `Caption` rubric in `INK_RUBRIC` with the device at the right, the apostille as an 18-px seal and a `Lead` Label in IM Fell italic, a `RichTextLabel` body whose every inline colour is an `INK_*` and whose chips are `Utils.bb_button_chip` metas), holds and restores the page's own scroll in `_on_pinned_dispatch`, raises the ceiling with the letter's fractions on page open and removes the meta on back and in `close_view()`, gains `refit()`; `_on_corr_meta` closes the view and emits `read_letter_requested` / `open_diplomacy_for`, or takes the dispatch's own `ledger:` road. `main.gd` connects the two signals (the rail card's `activate_mailbox_item`; the ledger's guarded `_on_ledger_open_diplomacy_for`), appends the pointer clause to both "No pending envoys" lines once the client has seen the page (`_no_envoys_line`), and opens the Dispatch on the page from the letter-book's new footer button (`mailbox_panel.correspondence_requested`).
- **The censuses** the page passed as authored: the floorless-scroll ratchet (8), the override diet (sizes by variation only), the Side Desk's refresh pins, the chip honesty census (three REVIEWED rows), the display-name pass, the layout law, the parse harness (80 scripts, 0 bad).

### 23.2 The readings taken (each a line to reverse)

1. **ON THE DESK is every `fired` row** — Not Now is the client's; the row stays `fired` and the dialogue stays in the manager (`main.gd`'s `_dismissed_proposal_nation`).
2. **The caption is derived, never stored** — `_answer_side(e, answer, form)["caption"]`; no row field, no `WorldState` field.
3. **The Watch is read pure:** `watch(world, record=False)`; a GET never writes `runtime["watched"]`.
4. **"Read the letter ▸" stands on the desk only** — answer, lapse and withdrawal pop the dialogue, and §12b.1 forbids a new endpoint; an answered slip carries its court / Admiralty / Laws chips.
5. **The closing record appears from the morning after `ends.turn`** (T77 for Haiti). P13's "or earlier when the cap is spent after a loss" is built nowhere; §0b P13 and §6.5 say so now.
6. **The three "set aside" meanings get one section:** ANSWERED = `answered` rows; LEFT UNANSWERED / SET ASIDE = lapsed ("Filed unanswered — {caption} · {receipt}" — the lapse applied the Decline, so its price is printed), withdrawn ("Set aside for {moment} — nothing was spent"), crowded ("Set aside on a busy desk — its second answer taken"); the premise / forsworn / verdict / before_save passes never show.
7. **A slip is a node subtree** (the panel, the rubric row, the apostille row, the body), not BBCode alone; the section heads are Labels on the navy panel in the Dispatch's gold.
8. **The ceiling is the letter's** (`clamp_ceiling_override` at 0.45 × / 0.8 ×, floors 680 × 440, the width capped at 860), removed on back and close; `refit()` re-applies it; a drag made on the page may raise the grip's remembered size — recorded, not re-designed.
9. **The device:** arms as a 24-px flag; an office's monogram as the locket at 24 px.
10. **The pointer clause joins only once the client has seen a `correspondence` key;** the letter-book's footer button is built at runtime beside Close.
11. **The first-open line rides inside the page's dict** and is acknowledged the Strategic Ledger's way (`note_first_open` behind the draw); a screen, not a dialogue — no `first_open_seen` signal.
12. **The sailing's echo yields to the at-sea line while the squadron is out** ("or", as §12b.1 writes it); the fate follows in rubric.

### 23.3 The frames and the pins

The frames `IQ10_CORRESPONDENCE_{DESK,ANSWERED,FATE}{,_X2}_2026_11_01.png` — the desk (the Host's Claims standing with Bavaria's arms and Read the letter ▸, the Watch's line below), the answered page (the squadron at sea under Decrès's monogram beside the Bavarian Match's slip), the fate (the squadron home whole in rubric under its receipt, the Arch-Chancellor's lapsed letter set aside) — staged inside `cap_moments` and shot through `open_correspondence` (the button's text carries the amber count, so the step calls what the button calls); the readability record `docs/audits/uxr0/readability_correspondence_2026_11_01.json` RED 0 / P1 0 over the five physical resolutions. `tests/test_correspondence.py`: the desk and its road, the mailbox row's title (REC-1), the client's Not Now, the squadron at sea and then its fate, a moment's captions only, newest first and the Host's slip, the law's door, the three set-aside kinds and the four silent passes, the pure Watch, the closing record at T76 and T77, the empty states, the GET with its first-open line, the unarmed world, the save round-trip, the client by source (the ink, the ceiling, the pinned refresh, the roads, the scene), the frames and the record. Flipped: `tests/test_first_open.py` (SCREENS, ten), `tests/test_cn4_the_chip_honesty_census.py` (three rows).

### 23.4 Done-when, and the sibling sweep (Rule 10)

Every item of §16b's RE-C row ✓ — the builder, the GET key, the page subtree with its ceiling, the slips and chips, the court signal, `close_view()` before Read the letter, the two pointers in, the empty states, the frames at both scales, the pins; `to_dict` 497, levers 231, functions over 500 lines 28 unchanged; no new `WorldState` field; the full suite green through the hook. **The sweep.** REH-2's class (a letter named by its entry where its form has a name): the letter-book's row (`build_letter`'s `proposal_terms_summary`) still named the Haiti letter by its entry while the letter read "The Squadron for Santo Domingo" — fixed in this slice as **REC-1** (`BUG_FIXES.md` §REC). The pure-read class (a GET that writes): `watch` was the one; `fate_lines`, `squadron_line` and `_readable_dispatch` read only ✓. The ceiling-meta class: `proposal_confirm_popup` and `pause_menu` already remove it per state ✓. **What RE-R inherits:** the rows' `receipt` / `echo` / `outcome_line` the page already prints; `remark_by` (nothing writes it yet; the page reads none); the SITUATION receipt line; the COURTS predicate in `compose_issue`; the `remember` line; the noise census.


## §24 RE-R — the reactions — the landing record (✅ November 2, 2026)

**What the player meets, in plain words.** An answer has a voice and a wake. Under the green line that prices the answer, a second green line — the minister's acknowledgement ("Cambacérès: the Council has registered the decrees Your Majesty dictated from the field."; "Decrès: the squadron slips out of Brest on the night tide.") or, on "Live off the land", the marshal who eats the harvest: "Davout: I will hang the first man who takes a hen unpaid, Sire — but discipline does not feed a corps." Next morning the SITUATION block, on the Dispatch screen and in the terminal alike, carries one plain line ("The army lives on the country of Bavaria; Munich keeps the account."; "Five of the line are at sea for Santo Domingo; Decrès expects them home by Late February 1806."). In the next Gazette THE COURTS prints the Moniteur's line once ("MUNICH — The Grand Army is quartered upon the country of Bavaria."), the arrival never; a lost squadron gets the paper's lie ("SAN DOMINGO — Our squadron sustained the honour of the flag against a superior enemy."). When the same court writes again the letter's board ends with "In Late December 1805 the army lived on the country of Bavaria; its court writes again." And the seal presses: the answer beat shipped at RE-2 fires in the live client now that its key reaches it. Two lines beyond the answer's own, within §12c's budget; no popup, no rail card, no sound.

### 24.1 Built

- **The echo on the response** — `moments.answer` returns `message = "{title} — {quote}" + "\n" + echo` when the row carries one (`_stamp_receipt` freezes it); the client's `_display_result` → `add_output` prints the two green rows as they are; the letter-book's road prints the same message in grey.
- **The marshal's remark** — `affairs.HOST_REMARKS` (the seven lines of §12c under the names `world.marshals` spells: Davout, Massena, Ney, Lannes, Murat, Soult, Bernadotte), `HOST_REMARKS_BY_PERSONALITY` (aggressive / cautious / literal), `HOST_REMARK_DEFAULT`; `largest_corps_on_host` (the `_corps_on_host` filter — the lord's marshals, no sovereign, captive or contingent commander; the region's controller the host; the most men); `host_remark` → "{name}: {line}" with `{Host}` / `{seat}` filled over the row. Written at the answer into `row["echo"]` and `row["remark_by"]` when the side authors no echo and the row binds a host; no corps left on the soil → no remark, no field.
- **The morning's receipt** — `affairs.receipt_lines` (the occurrence rows answered on the previous turn whose side authors `situation`, filled over the row — `{date}` for the squadron) → `situation["affair_receipt"]` in `_build_situation` beside `affair_fate`; rendered plain (`COLOR_INFO`, no prefix) after the Staff's line and before the amber fate in `dispatch_view.gd` and in `main.gd`'s morning dispatch.
- **THE COURTS** — `gazette._affair_courts_line`: an affair's `moment` row prints its authored `press` on an `answered` or `outcome` row and nothing on any other — the arrival, a withdrawal, a crowding-out, Berthier's Not now, the squadron form's Accept (its paper line is the `outcome` row's); `compose_issue` filters and maps through it; the shared one-liner and `filter_campaign_log` untouched; `affairs.press_of` stamps the `answered` log row's `press` at the answer (`settle_squadrons` already stamped the outcome's).
- **The remember line** — `affairs.remember_line` (the previous occurrence of the same template and subject, answered or lapsed, its side's `remember` filled over that row — its `{month}`, its host) appended last by `board_lines`.
- **The forwarded key** — `_respond_to_dialogue_sync` copies `moment_answered` onto the response (RER-1).
- **The row** gains `remark_by` (`SAVE_FORMAT_REFERENCE.md`); no `WorldState` field, no log type, no phase, no Gazette special, no popup, no sound, no rail notice.

### 24.2 The readings taken (each a line to reverse)

1. **The echo rides the answer's own response as its second line** — no new response key.
2. **The remark's speaker is the largest corps on the host's soil at the answer;** by name, else by personality, else one default (the retired `balanced` / `loyal` types); no corps left there → no remark.
3. **The receipt is plain and prefix-less,** after the Staff's line and before the fate; **a lapse gets none** — LAPSED ENVOYS already says it in both views, and the budget is one line per surface.
4. **THE COURTS' transform prints `press` on `answered` and `outcome` rows only;** the arrival, a withdrawal, a crowding-out and an empty press print nothing; a moment's rows keep today's lines; the lapse writes no new log row.
5. **`remember` reads the previous occurrence with the same subject** (the Host's Claims: the same host; the others: the previous occurrence), answered or lapsed, and stands last on the board — on the Haiti letter after the sailing's own memory line.
6. **`moment_answered` is forwarded at the response edge** — the seal's trigger.
7. **The noise census is a pin, not an instrument** — the response's two lines, one receipt on T + 1 and none on T + 2, one COURTS line, the alarm untouched, no popup / sound / notice in the answer road.
8. **Nothing else is new.**

### 24.3 The frame and the pins

`IQ10_DISPATCH_AFFAIR_RECEIPT{,_X2}_2026_11_02.png` — the Dispatch screen's SITUATION the morning after the Host's Claims were declined, the receipt plain under the Watch — staged in `cap_moments`; `docs/audits/uxr0/readability_reactions_2026_11_02.json` RED 0 / P1 0. `tests/test_reactions.py`: the echo on the squadron's and the bill's answers, a refusal's bare message; Davout's remark by name with `remark_by`, Masséna's and Soult's slots, the personality fallbacks and the default, no corps → no remark, the table within the cap and naming no nation; the receipt on T + 1 only, the squadron's date, Berthier's Accept silent, a lapse silent, both views by source (plain, before the fate), the pure build; THE COURTS — the press once and the arrival never, Not now silent, the squadron silent until its fate (home or the Moniteur's lie), a moment's rows and the one-liner unchanged; the remember line on the second letter from the same host and not from another, after an answer and after a lapse, last on the letter's board; the budget; every line filled on every host; the lockstep; the frame and the record. Flipped consciously: `tests/test_affairs_engine.py` (the Host's Decline's echo is the remark), `tests/test_affairs_haiti.py` (the Haiti board's last line is the remember line, the sailing's before it).

### 24.4 Done-when, and the sibling sweep (Rule 10)

§16b's RE-R row ✓ item by item — the SITUATION key in both views with the two-view pin, the COURTS predicate in `compose_issue`, the echo on the response, `HOST_REMARKS` and `remark_by`, the `remember` line, the noise census; the budget held on every template; `to_dict` 497, levers 231, functions over 500 lines 28 unchanged; the full suite green through the hook. **The sweep.** RER-1's class (a key the client reads that the backend never sends): the refusal's `diplomatic_dialogue` is forwarded and the letter stands on the client ✓; `open_reward_for` and `objection_kept` are copied at their edges ✓. RER-2's class (authored copy nobody renders): `echo` (the response), `press` (THE COURTS), `situation` (the receipt), `remember` (the board), `outcome` (RE-H), `counsel` (RE-2) — every authored reaction key now has a reader; the validator checks them all. The pure-read class: `receipt_lines` and `remember_line` write nothing; the morning build and `compose_issue` stay pure reads ✓.

---

## §25 RE-6 — the Edicts — the landing record (✅ November 2, 2026)

**What the player meets, in plain words.** Three new letters of state under the parchment register, each an **offer** — a decree the Emperor may take rather than a bill he answers. Daru writes when the corps are abroad on campaign pay or a coalition gathers against France ("Sire, the magazines of the Rhine hold bread for a fortnight…") — **Stock the magazines / −2,500 gold · 1 action · 8 turns**, or **Let the army forage / no change**. The War Administration writes when the horse falls under 60 % of its establishment, in the depots or in the squadrons — **Buy the remounts / −1,500 gold · 1 action · 8 turns**. At the golden peace — six mornings at peace with every great power, the Charges carrying the crown term alone — the Minister of War (Berthier; Clarke after 9 August 1807) writes of the camps of Boulogne: **Form the camps / −2,000 gold · 1 action · 8 turns** — every drill yields five more morale for eight turns. The seal presses; the echo answers; next morning SITUATION says it plainly and names the morning it ends; the Moniteur prints one line; the LAWS book carries an **EDICTS** block ("the Magazines — fed provinces feed 25% more men (×1.25) — until Late January 1806"); the recruit quote and the drill note name the decree as they name a law; on its morning it is gone, and eight turns later the letter may come again. A decreed edict cannot be offered again for sixteen turns, a declined one for eight; a later letter carries a shorter chapter and remembers what the Emperor did last time.

### 25.1 Built

- **The second lifecycle** — `reforms.effect_terms` yields, after the laws in force, `(pseudo_row, clause)` for every edict in force (`affairs.edicts_in_force`; the pseudo-row carries `name`, so `display_name` names it): `supply_capacity_factor`, `recruit_price_terms`, `drill_morale_bonus`, `effect_line`, the recruit quote's memo key (`laws_signature` gains the edicts in force) and the drill note read an edict as they read a law, unchanged. **The store** is ONE `{lord|template: until}` map in the affairs runtime (`edicts`; `moments._clean_runtime` round-trips it; no `WorldState` field): in force while `until > turn`, resting until `until + rest`, available after — **derived from the turn, never ticked.** Every reader is pure (`_store`, never `runtime()`); `affairs.grant_edict` is the one writer (the price through `moments._apply_gold` → `record_gold_spent`; the tallies `decreed` / `edict_gold` for the measure).
- **The `edict` op** — `moments.OPS` 10 → 11 (flipped consciously); Accept-only; the price, term, rest and effect clauses on the template's `edict` block (the door's `enact_law` idiom — the price outside the gold bound); `plan` stamps the entry's id into the op (the squadron's `tag` idiom); the plan row carries `amount`, `term`, `until`, the words from `reforms.effect_line`; `_receipt` fills `{gold}` / `{term}` on the authored button line (one source for the price); `_stamp_receipt` writes the row's `until`; `_chips_of` gives a LAWS chip; the Correspondence's answered slip carries `until` / `in_force`; `DECLINE_FORBIDDEN_OPS` bars it from any Decline; the trace's `_delivered` counts it.
- **One gate** — `affairs.edict_refusal(world, lord, e, treasury=None, with_reserve=False)`: not armed / no block; in force until …; resting until …; the chest under the price — or, `with_reserve`, under the laws rung's own bar (price + `AI_PURSE_RESERVE` + `AI_PURSE_UPKEEP_TURNS` × the slate's upkeep). The premise reads it with the reserve, the letter's plan and the courts' verb with the price alone.
- **The three premises** — `magazines_wanted` (at war with a corps drawing campaign pay, `campaign_pay_homeland` / `campaign_pay_at` over the marshal list; or the storm gathering — the player: `threat_level ≥ coalition.brewing_gate` with no coalition yet formed against the lord; a court: a `war_intents` record in tenure whose target is the lord), `remounts_wanted` (the pool under `below_pct` of `MAX_CAVALRY_POOL`, or the weakest cavalry corps under `below_pct` of its `starting_strength`; the measure the weaker percent), `camps_wanted` (at peace with every other `reforms.GREAT_POWERS` and the Charges' rate's term keys ⊆ {crown}); each names its own entry in `when.edict` as the door names its law. The boards name the facts and the chest against the price.
- **The deck** — `the_magazines`, `the_remounts`, `camps_of_instruction` in `europe_1805.json` and `tests/fixtures/affairs_block.json` in lockstep (§25.2's table of copy); `holders` on E2 (Dejean → Lacuée de Cessac, T104) and E3 (Berthier → Clarke, T46); a `later` chapter on each; `cooldown` 8, `cap` 2, `grace` 4, `streak` 2 / 1 / 6; the sources cited.
- **The courts' rung** — `affairs.find_ai_edict` at priority 1.79 beside the laws (`ENEMY_AI_REFERENCE.md`): the first of E1–E3 whose premise holds this morning for a court that keeps a laws deck (`reforms.REFORM_DECKS`) and whose purse clears the laws rung's bar, one decree every `AI_ENACTMENT_EVERY_TURNS`, never while a law would lapse, never the player; the `decree_edict` executor verb (the top chain beside `enact_law`; not in `VALID_ACTIONS`, not in the parser — the player's road is the letter) grants through the one writer and logs one `moment` / `outcome` row whose `press` the Moniteur prints ("VIENNA — The court of Austria buys remounts for its horse."); `filter_campaign_log`'s no-fog tuple gains `"moment"` (one token, zero lines — the only non-player `moment` rows are these). **Shipped PARKED:** `affairs.ai_decrees()` returns False pending the user's ruling (§25.3); the seam row AFE holds it down in the series rig.
- **The validator** — `_validate_edict`: an offer's `edict` block (name ≤ 40, price 500–5,000, term and rest 4–16, 1–2 clauses of the ruling's three types through `_validate_law_clause`, court_press ≤ 160), its Accept exactly `admin` + `edict`, `when.edict` the entry itself, `below_pct` 10–90; the `edict` op anywhere else — a bill, a door, a Decline, a dated letter — refused.
- **The LAWS book** — `reforms.laws_payload` gains `edicts` (one row per decree in force: the name, the effect lines, `until`, its dateline, a status line) when the deck is armed; the client's EDICTS block lands in the slice's second commit with the frames.
- **The measure's instruments** — `tools/_moments_trace.py`'s summary carries the tallies, `tools/_s14c_sweep_record.py` tabulates them per arm and per family, `strip_entry` strips the block's copy from the hash; the series rig gains the AFE arm and counts `decree_reads` / `edicts_granted`; `tests/_affairs_boards.py` (`rest_the_offers`) lets the older pins read their one letter's morning.

### 25.2 Measured — the reach on the shipped default (the courts' rung parked; 55 arms with the trace, the ten-seed probe; seeded paths, not laws)

| Template | Arrived (of 55) | Scripted (25) | Passive sweep (21) | Hand-played T21 starts (6) | Before RE-6 (55) |
|---|---|---|---|---|---|
| the Arch-Chancellor's Letters | 11 | 8 | 2 | 1 | 12 |
| the Host's Claims | 22 | 17 | 3 | 1 | 22 |
| Berthier's Memorial | 11 | 0 | 9 | 2 | 19 |
| the Haiti letter | 24 | 4 | 17 | 0 | 24 |
| **E1 the Magazines** | **8** | 3 | 2 | 3 | — |
| **E2 the Remounts** | **29** | 14 | 14 | 0 | — |
| **E3 the Camps of Instruction** | **6** | 3 | 0 | 3 | — |

- **First arrivals:** the Magazines at T6–T37 (the war's letter — three of the nine road arms, three of the six hand-played starts, two of the passive sweeps); the Camps at T27–T38 (the golden peace's — the commanded arms whose France makes peace, never the passive sweep at war with Britain); the Remounts at T11–T38 (with the pool clause alone it reached no board — 0 of 55 arms, the six hand-played boards at the cap of 30,000; the corps clause is its road onto the war arms where the horse bleeds; a France that levies its cavalry meets the pool clause).
- **What the older letters yield:** the Magazines' premise (a corps on campaign pay) stands on the Memorial's and the Host's war boards and its purse bar (3,500) clears before the Staff's (11,500), so where both are due the longer-standing premise picks (`affairs.pick`); the Memorial's and the Haiti letter's counts above against their pre-RE-6 figures are the honest cost, re-derived floors — the reach review (RE-5) weighs them with RE3-6 / RE3-7.
- **France's own decrees on the accept arms:** accept/CMD-A-ACCEPT: the_remounts, camps_of_instruction; accept/CMD-H-ACCEPT: the_remounts; accept/CMD-M-ACCEPT: the_remounts; haiti/HAITI-historical: the_remounts; road_accept/VP1-RH-austerlitz: the_remounts; road_accept/VP1-RH-marengo: the_remounts (the measured drivers decline by default; the accept dial takes the first offer it can pay).
- **The passive board (the probe, ten seeds, twenty turns):** the first affair is the Haiti letter on 9 of 10 seeds (T6–T9), as at RE-H; offers on the passive board in twenty turns: the_remounts.
- **The brakes:** the Rhine road's end turns and stamps are the unarmed control's on every arm — the armed deck against the in-tree control, unmoved True: (28, -1), (34, 12), (40, 13); the E1 band T1–T5 empty on every arm (`first` ≥ 6); the alarm untouched across every answer and decree; `BASELINE_SERIES` byte-identical (the series rig's AFE arm — the letters alone move nothing).

### 25.3 The courts' Edicts — measured with the rung up, then PARKED (the escalation §16 "RE-6" names)

Run once with `affairs.ai_decrees()` True on the same 55 arms before the default was parked (`tools/_affairs_series_arms_re6.json`; the road and record logs under `tools/playtest_runs/re6_2026_11_02/courts_up/`):

- **The spend.** The five courts with a laws deck decree two to four edicts a campaign at the player's prices — on the passive sweep, per arm: Russia 3.4 decrees / 7,333 gold, the Porte 3.8 / 7,024, Britain 3.2 / 6,333, Prussia 2.2 / 3,976, Austria 1.3 / 2,643 — 15–30 % of a court's T40 chest (10–26k). Which: Britain and Austria the Magazines and the Remounts (at war with corps abroad; the pool under 60 %); the Porte and Prussia the Camps (at peace, the crown alone) and the Remounts; Russia the Magazines above all (45 of 71 on the sweep). The EAD-6 hoard is spent, as Q5 foresaw.
- **The move.** The ambient alarm series diverges from `BASELINE_SERIES` at turn 10 (13 edicts granted on the 40-turn board); **every road arm's end turn moved against the unarmed control** — the Confederation road austerlitz 24 → 38, historical 30 → 35, marengo 27 → 24; the Rhine road austerlitz 40 → 36, historical 34 → 40, marengo 28 unstamped → 40 **sealed** on turn 13; the Throne road austerlitz 40 → 28, historical 40 → 33, marengo 40 → 21 — **France falls earlier on all three Throne-road arms** (the Fall of the Empire where the control reached turn 40) — while the letters alone (the rung held down) left all nine arms byte-identical to the control. The courts' Edicts are a real strengthening of the AI — ×1.25 supply for the corps that march on France, cheaper horse, +5 morale on every drill — the brake on France Q5's note foresaw ("at war that strengthens the AI, a brake on France of the kind the user asked about").
- **The ruling owed.** A shape change found at the head re-escalates (§0 the reading for Q2 and Q5; §16 "RE-6"). The rung ships PARKED: `affairs.ai_decrees()` returns False, the player's three offers stand armed, the mechanism is complete and pinned both ways (`tests/test_affairs_edicts.py::TestTheCourts`). **Recommended: flip it on** — history with teeth, the courts spending their hoards on the instruments of the era, the underdog stories the user asked for at S14k — after the user has read the move above; the flip is one line (`ai_decrees` → True), the re-measure the chain (`tools/playtest_runs/re6_2026_11_02/chain.sh`), the series and the road pins re-seated with the attribution. Alternatives: arm the rung at war only (a clause in `find_ai_edict`); arm it for the great powers without the Porte; leave it parked through RE-5's reach review. **Reversible either way; the user's word decides.**

### 25.4 The readings taken (each a line to reverse)

1. The edict is a `{lord|template: until}` entry in the affairs runtime store; expiry is derived; every reader is pure; `grant_edict` is the one writer.
2. `reforms.effect_terms` is the second source's one door — every law seam applies an edict unchanged; the recruit quote and the drill note name it; the supply seam applies it unnamed, as it does a law.
3. One op, `edict`, Accept-only, its terms on the template's block; `plan` stamps the entry's id; the button line's figures come from the plan.
4. One gate, `edict_refusal` — with the laws rung's bar for the premise and the courts, the price alone for the letter's plan and the verb.
5. The courts' rung is an executor verb reached by the AI's structured command alone, for the courts that keep a laws deck, on the instantaneous read; **shipped parked** (§25.3).
6. A court's decree writes one `moment` / `outcome` row through `MO._log`; `filter_campaign_log`'s no-fog tuple gains `"moment"`.
7. E1's storm clause is the brewing gauge for the player and a war-intent record for a court (the drafted clause never fired for France — RE6-2); E2 takes the horse in the squadrons as well as the depots (the pool alone reached no board — RE6-3); E3's "rate ≤ 60" is the crown term alone (RE6-1).
8. The faces: Daru (Intendant-General, true from 1805); Dejean → Lacuée de Cessac (T104); Berthier → Clarke (T46) — Berthier writes twice in the deck, at war and at peace, never on the same morning; the reaction copy of E2 and E3 names the office, not the man, so a change of holder never puts the old name in a new mouth.
9. The prices stand as drafted (§14's bullet); a change is in-band.
10. A `later` chapter and the remember line against repetition; `streak` 2 / 1 / 6, `cooldown` 8, `cap` 2.
11. Nothing else is new: no popup, no sound, no rail notice beyond the arrival's, no `WorldState` field, no log type or phase, the one-liner untouched.

### 25.5 The pins, the frames, the sibling sweep

`tests/test_affairs_edicts.py` (the deck, the holders, the premises clause by clause, the lifecycle through the letter and the endpoint — the two lines, the chest, the row's `until`, the supply cap ×1.25, the LAWS payload on GET /ledger, the slip, the log row's press, the receipt on T + 1, the premise closed, the term's end by the turn alone, the rest, the save round trip, the Remounts on the cavalry levy alone, the Camps on every drill and named, the Decline free and the offer's return with its chapter and remember line, the standing letter's closed Accept; the courts — parked by default, the flip, the AFE seam, the rung's order and bars, the verb's grant and the Moniteur's line, the cadence and the lapse guard, the player never reaching the verb, the admin chain's 1.79, the courts-up series record; the validator's nineteen refusals; the register — the court press on every court with a deck, no slot left open, the budget's two lines and one receipt and one COURTS line; purity on a fresh boot, the one writer by source, the log filter's token without growth, the hash's strip, the trace's figures). **Flipped consciously:** `set(MO.OPS)` 10 → 11 (three files); the deck's id lists 4 → 7 (the engine, the Haiti letter, the reach, the pacing, the nondominance — with an `edict` axis); the Watch and arrival pins on the Host's and the door's boards read their letter alone through `rest_the_offers` (the Magazines premise on any board where a corps draws campaign pay), the Haiti board keeps every corps home and the depots full; two admin-chain pins skip `decree_edict`; the reach floors re-derived from the record. **The frames** land with the client's EDICTS block in the second commit. **The sweep (Rule 10).** RE6-1's class (a numeric clause written against a figure another slice moved): the Host's tiers (300 × tier — the economy gate's own record, §14 ✓), the Haiti letter's `min_purse` 500 + the reserve ✓, the Staff door's bar (one source with the AI's rung ✓) — none reads a pre-S14j rate. RE6-2's class (a premise that names a source that cannot fire for the player): `sovereign_afield`, `corps_on_host`, `staff_offered`, `colony_cut_off` all read the player's own state ✓. RE6-3's class (a letter whose premise no measured board meets): the reach table above is the census; the Remounts' second clause is the one re-premise, and RE-5's review holds the rest.
