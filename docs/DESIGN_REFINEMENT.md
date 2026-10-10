# Design Refinement

> **Archives (October 9, 2026, CODE-4):** sections closed before the current quarter live in `docs/archive/DESIGN_REFINEMENT_2026_Q2.md`, `docs/archive/DESIGN_REFINEMENT_2026_Q3.md`, read by the census tools and the test pins exactly as if they were still here. OPEN and PARTIAL rows never move.

> **Design items and addons for evaluation.** This is the design-refinement backlog; execution routes through `docs/ROADMAP.md`'s current phase queue. (The old "work begins after `BUG_FIXES.md` is clear" gate cleared April 2026.)
>
> **Last Updated:** September 28, 2026 — **the Full Play Retest filed RS-D1 … RS-D3** (§Full Play Retest below: recognition by defeat, the user's ruling; the standing levy offer, SR-6a; the quiet middle, evidence for SR-G7). Prior: September 27, 2026 — **SR-D1 RULED and SR-D2's doctrines RULED** (the SR-D1 and SR-D2 rows in §Score Mandate rulings; gate records + build contracts `docs/REFORMS_SPEC.md` and `docs/DOCTRINES_SPEC.md`). Prior: September 26, 2026 (evening) — **the Score Mandate rulings recorded** (§Score Mandate rulings, the first section below: L-D approved; SR-D3 ruled (c) first with its AP premise corrected; SR-D1/SR-D2 re-slotted to Chunks 5/7; the standing-alarm-floor gate question; one exit per session and one full re-score at the end). Prior: September 25, 2026 (evening) — **AAR-D1..D8 filed** by the Creative AAR playtest (the client's war is the lord's war; status quo is a cession; the jealousy cadence; dispersion taxed and punished; DP as the bottleneck; the paying peace from the player's chair; the naval throw; the AI's garrison grind) — memo `docs/audits/PLAYTEST_CREATIVE_AAR_2026_09_25.md`. Prior: August 21, 2026 — **WO-D7..D10 filed** (the zero-battle war that bills both treasuries → EC-2 pass 2; the player's missing truce floor; the objection-economy shape; the exiled Marshalate) by the WO spec-authoring session — **build contract = `docs/WEIRD_OUTCOMES_SPEC.md`**. Prior: August 16, 2026 — **Weird-Outcomes design questions filed (WO-D1..D6, the WO-EVAL docket)**: the funnel (every non-military strategy loses the map), the 1:13.9 battle exchange, vassals and naval as primary strategies, the reward for not fighting, whether a war ever ends on its own, and the missing `capital_lost` headline class; memo `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md`. Prior: August 15, 2026 — **Comprehensive Playtest questions filed** (PC15-D1..D4: neutrality vs broken armies, ally-soil supply, tutorial expectation-dormancy, the exhausted-pair truce floor; memo `docs/audits/PLAYTEST_COMPREHENSIVE_2026_08_15.md`). Prior: August 1, 2026 — **Live-Playthrough design items filed** (PT-D1..D4, from the played-world creative-audit re-measure; memo `docs/audits/AI_V_SWEEP_2026_08_01.md` §10 — PT-D1/D2/D4 share the PT-F6 enemy-phase slice, PT-D3 is copy-level). Prior: July 11, 2026 — **Estate Second Pass deferrals filed** (ESP-1..4, from the ES-7 second-pass design conversation; owner spec `ECONOMY_REVISIT_SPEC.md` §0.6.8). Prior: July 10, 2026 — **Wave 6 APPROVED IN FULL same day it was filed** (+2 gate additions: Dynamic Battle Naming, Literal Doctrine); the build-ready owner is **`docs/WAVE6_FUN_FACTOR_SPEC.md`** (12 slices, blessed default numbers recorded there). Wave 6 items came from `docs/audits/CREATIVE_AUDIT_2026_07_10.md`; live-evidence revisions recorded on R154, R59/R153 (now SUPERSEDED by W6-5), R129/R131/R132, R155/R156, R117 (absorbed into W6-9). Prior: July 2, 2026 present-tense pass. April 16, 2026 rescope context preserved below as history.

---

## The Economy Audit — design items (EAD) — filed October 5, 2026 (**9 rows — ALL RULED October 5, 2026 under the user's delegation: EAD-1, 2, 4, 7, 8 BUILT; EAD-3, 5, 6, 9 KEPT (gate record `SCORE_FINISH_SPEC.md` §6.8, memo `docs/audits/ECONOMY_GATE_2026_10_05.md`); three new rows EG-D1 … EG-D3 OPEN with the user** — memo `docs/audits/ECONOMY_AUDIT_2026_10_05.md` §10; defects `BUG_FIXES.md` §The Economy Audit)

Each is a balance or design change the audit measured and did not build: a blessed number moves, or a mechanic is new. Recommendations, not applied (the user's rule — do not tune).

| Row | Item | Recommendation | Owner |
|---|---|---|---|
| **EAD-1** | **The opening war costs France nothing.** On every arm the lowest Net on turns 2–12 is +398 to +1,298 (investigator B, 27 campaigns); the chest reaches 11–14k by turn 10 while fighting Austria, Britain and Russia. The blessed E1 band (France's turn-1 absorption 62–70%, SR-5a) leaves the surplus by design. | **A war footing:** upkeep at war ×1.25 (or the Charges' war term priced on income, not the chest, so it bites while the chest is small) — measured against E1 first, since France's turn-1 absorption would leave the band; the band is the user's to re-bless. Rejected: a lower boot chest (the opening choices depend on it). | ✅ **RULED + BUILT October 5, 2026 under the user's delegation ("fix and decide on these"; gate record `SCORE_FINISH_SPEC.md` §6.8; rules `SYSTEMS_REFERENCE.md` §98.1): campaign pay** — at war, a corps outside its court's 1805 homeland on allied or neutral soil pays 12 gold per 1,000 men a turn; enemy soil feeds itself, a satellite's soil feeds the lord's corps (`world_state.CAMPAIGN_PAY_ON_FOREIGN_SOIL`). France's turn-10 chest 12.4k / 17.2k / 14.5k → 5.3k / 14.7k / 10.3k on the three commanded seeds; the Staff affordable at turns 14 / 11 / 13 (REFORMS T1's 10–15) instead of 11 / 8 / 8; no AI decision moves (the series byte-identical alone). E1 re-blessed 0.66–0.74 (0.670 → 0.722). Economy C1 (LAW by loop 10) reads ✗ under it — the arm also buys and re-buys two laws (memo §3). **the user** — an economy gate (ROADMAP 13 owns the post-Step-9 balance pass). Done-when: the gate rules, the band is re-blessed or kept, and the commanded arms re-read. ⟨SF step=9 · ROADMAP 13 · pillar=economy⟩ |
| **EAD-2** | **The Charges of Empire are a tax with no decision attached.** They are the economy's brake — 37–44k of a hoarding France's gold over 40 turns, 43–55% of its gross on the conquest road — and the player has no lever on them. | **Give the chest a use that answers the Charges:** an act of state that converts gold into something the Charges cannot reach (a monument with authority, a forced loan with war score, the Congress's own prices), or a law that halves the crown term at an upkeep. SF-ECON-1 ("Acts of the Empire", §6 row 11) is the natural owner. | ✅ **RULED + BUILT October 5, 2026 (gate record §6.8; rules §98.2): the decision made visible** — the counsel's law line, the ledger's Charges line and the desk's purse answer say what spending cuts from next turn's Charges (`WorldState.charges_relief`, one source); a political law that takes the Emperor's grip under 70 names the grip term on its quote and its result (`ledger.charges_grip_clause`). A law halving the crown term REJECTED (it pays the hoarder); an act of state stays SF-ECON-1's gate. **the user** — SF-ECON-1's gate. ⟨SF step=9 · SF-ECON-1 · pillar=economy⟩ |
| **EAD-3** | **The levy's price never matters.** 10,000 drafted infantry cost 210–260 gold at peace and 620–740 at war; upkeep, manpower and where a corps stands decide the army. Commissions cost 700–1,100 gold per 1,000 men. | **Price men by scarcity** (the draft's price rises as the pool empties) or cap the draft per turn by the court's administration; measure against the M1–M7 harness before any re-record. | ✅ **RULED October 5, 2026 (gate record §6.8): KEEP.** France's draft gold is 1–9% of its men's upkeep; upkeep, the class and the levy ground decide the army; scarcity is priced on substitutes (4× → 16× the draft price), where history put it. Both candidates land on the AI under GR5 and move the series (scarcity k = 2: Britain's levies 33 → 10). Re-open: a played campaign in which the class never binds a France that keeps losing men. **the user** — the economy gate (EAD-1's). ⟨SF step=9 · ROADMAP 13 · pillar=economy⟩ |
| **EAD-4** | **An army carries no alarm.** The `military_establishment` threat term needs 40% of Europe's men; even 213,000 French soldiers reach 35%, and on austerlitz the threat against France fell to 0 by turn 35 with 209–213k under arms. | **Align the term to the Armed Peace's own share** (a third of Europe's power, §6.2), and measure the series and the Armed Peace's fuse before ruling. | ✅ **RULED + BUILT October 5, 2026 (gate record §6.8; rules §98.3): the line at one third of Europe's standing men**, still a MEN measure (`coalition.THE_ARMY_LINE_IS_A_THIRD`). The row's symptom is answered elsewhere (the Armed Peace holds the alarm at its watch line; Europe re-arms in peace, EA-11). The bloc-share version REJECTED (fires at boot, duplicates the hegemony term, slips around the fuse). **the user** — the coalition's gate. ⟨SF step=9 · ROADMAP 13 · pillar=living_balance⟩ |
| **EAD-5** | **Commissions are 59% of the buy-everything bill and the worst gold-to-men rate** (30,000 for seven 5,000-man corps). | **A commissioned corps raises 8,000–10,000 men, or the price falls with the bench's rank**; the Marshalate's gate. | ✅ **RULED October 5, 2026 (gate record §6.8): KEEP** the 5,000-man corps and the authored prices — a commission buys a general, France's only guns and a corps at the capital (45–95% of the price); the 8,000-man corps measured as an AI buff (France 28 / 29 / 28 → 19 / 18 / 16 provinces at turn 40). **the user** — the Marshalate's gate. ⟨SF step=9 · ROADMAP 13 · pillar=economy⟩ |
| **EAD-6** | **The neutral's hoard.** A court with one marshal and no law deck has nothing to buy after its slots fill (the Ottoman 58,000 at turn 40, Spain 30–47k), and a court with no marshal never runs an admin phase at all (EA-7). | **Content first:** author two or three law decks for the secondaries (the rung exists — content only); let `AI_RECRUIT_MAX_STANDING` rise from 3 to 4 when the chest holds twice the commission; decide what the marshal-less courts are for (a commander each, or inert, and their chests a prize the settlement already prices at 15% + base). | ✅ **RULED October 5, 2026 (gate record §6.8): KEEP the peaceful hoard inert by design** (invisible, capped by the Charges, priced into indemnities, a latent war chest P7.5 spends at war); R6 not re-opened; a fourth standing marshal not built (it misses every hoarder). **EA-7's real defect BUILT:** a court left with no general runs the commission rung (`enemy_ai.A_COURT_WITHOUT_A_GENERAL_MAY_COMMISSION`, §98.7). A bench for the secondaries at war offered, not built — EG-D3. **the user**; content is SF-RR4's (§3 Step 9). ⟨SF step=9 · SF-RR4 · pillar=ai_aliveness⟩ |
| **EAD-7** | **The march step cannot follow a lawful road** (investigator D). `_consider_strategic_move` aims at the nearest province of any court the AI is at war with — including a fellow league member (Britain's Baltic corps aimed at Sweden on 14 of 18 corps-turns) — and takes one hop that shortens the straight distance, so a lawful 7–9-province road (Russia: Estonia → … → Vienna → Bohemia) is never found. | **Aim at the coalition's declared enemy, never a fellow member, and follow `world.find_path(..., passable_for=nation)`** with the first hop re-checked by `_can_ai_move_to`. A series re-record. | ✅ **RULED + BUILT October 5, 2026 (gate record §6.8; rules §98.4): the league aims at its enemy and the march reads the lawful road** (the straight hop first; the lawful road when no straight hop is open — `enemy_ai.THE_LEAGUE_AIMS_AT_ITS_ENEMY`, `THE_MARCH_READS_THE_LAWFUL_ROAD`). `BASELINE_SERIES` re-recorded once, twelve-arm attributed (arm 0, each lever alone, all: the road the sole mover). On seven commanded seeds France holds 22–29 provinces at turn 40 on six; on austerlitz Kutuzov walks to Paris through an undefended France (7; 29 without the road) — EG-D2, the user's. SF-RR4 "war, truce and the standing order" (§3 Step 9). Done-when: built behind a lever, the series re-recorded once with attribution, AI aliveness C6 re-read. ⟨SF step=9 · SF-RR4 · pillar=ai_aliveness⟩ |
| **EAD-9** | **The AI's purse test refuses a rich court a law for being rich** (the AI side of EA-18). `reforms.ai_purse_refusal` asks the forecast Net to carry the upkeep; the Charges of Empire, a share of the chest, depress that Net in proportion to the chest, so a court refuses a law exactly when it is best able to afford one. The rival courts enact 19–20 laws in forty turns on the audit's arms (above AI aliveness C1's 13–18 band), so the plain read is acting as a brake. | **Decide whether the brake is the rule.** Either keep the plain read and name it (the band is what the rivals should enact), or read the Net before the Charges as the player's counsel now does (EA-18) and re-band C1 — measured against the series and C1 first. | ✅ **RULED October 5, 2026 (gate record §6.8): KEEP the plain read; the record corrected** — the brake is the chest-plus-reserve test (240 refusals on the commanded seeds against 1 for the Net clause); the pre-Charges read changes no purse and no enactment on any commanded seed. AI aliveness C1 fails at the content's ceiling (20 laws) under either read — EG-D1, the user's. **the user** — the economy gate (EAD-1's). Done-when: the gate rules; if built, behind a lever, the series re-recorded once with attribution and AI C1 re-read. ⟨SF step=9 · ROADMAP 13 · pillar=ai_aliveness⟩ |
| **EAD-8** | **The league says nothing of the courts that have not marched.** Even with SFR-DR1 built, Britain cannot cross the Channel and Russia's armies stand in Finland, and the dispatch is silent about why. | **A court-level beat:** "Russia's armies are in Finland, at war with Sweden; Prussia's neutrality bars their road west"; "Britain's 40,000 cannot cross the Channel"; "Hanover and Sardinia have no army in the field" — read off the same predicates (`find_path`, `_region_passable_for`, `crossing_check`). Display only. | ✅ **RULED + BUILT October 5, 2026 (gate record §6.8; rules §98.5): a court-level reading from public facts only** (`coalition.league_march_reading`) — the dispatch's coalition rows every morning a league stands, and the front page's `league_unmarched` beat when the reasons change (`THE_LEAGUE_SAYS_WHO_HAS_NOT_MARCHED`). SF-RR3 "the page and the copy" (§3 Step 9). Done-when: the beat pinned through the dispatch, the league's first silent turn on the CMD-A arm named. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **EG-D1** | **AI aliveness C1's band sits under the content's ceiling** (found ruling EAD-9). The four rival decks hold 20 laws; the rivals enact 19–20 with 0 lapses on the audit's arms, so the item's "13–18" fails a fully competent AI under either purse read. The band was RF-3's measured 16 ± 2, not the user's target (REFORMS §11 T3: two great powers enact by turn 25, no lapse in a court not losing provinces). **On the gate's own reading C1 reads ✓ (17 / 13 / 17)**: the lawful road's wars spend the rivals' purses (with the road's lever down, 20 / 20 / 20 and ✗ — `tools/_econ_gate_exit_attribution.json`); the band question stands for a peaceful board. | **Recommendation, not applied** (the checklist is the user's): re-band C1 to "≥ 13 of the decks' 20, with 0 lapses" in a checklist v1.2, and re-read the three archives beside their records. Rejected: tightening the AI's purse to land in the band (tuning to the instrument). | **the user** — `SCORE_FINISH_SPEC.md` §6 row 23. Done-when: the user rules; if re-banded, `docs/SCORE_CHECKLIST_V1_2.json` and the archives re-read by `tools/score_reread.py`. ⟨SF step=9 · SF-RR6 · pillar=ai_aliveness⟩ |
| **EG-D2** | **Living balance F1 under a real war** (EAD-7's measured consequence). With the lawful road, the commanded France holds 22–29 provinces at turn 40 on six of seven seeds; on austerlitz the truce with Russia collapses at turn 12 and Kutuzov walks from Piedmont to Paris while the scripted army stands fortified in Franconia — France 7 (29 with the road's lever down), so F1 ("≥ 20 on 3 of 3") reads ✗. The scripted arm never answers a march on its homeland. **Narration C1 follows it on that seed:** a homeland province falls nearly every morning from turn 9, and the page leads with it (`home_captured` 9 of 10 mornings) — event news, which the rotation rule exempts by its own statement; historical and marengo stay at ≤ 4. **Measured on the gate's attribution arms (`tools/_econ_gate_exit_attribution.json`): the collapse needs the road AND campaign pay together** — with campaign pay alone down the seed holds 26 (France 25 / 26 / 21 on the three seeds), with the road alone down 29; narration C4 (EG-X4) and AI aliveness C6 also need both, while narration C1 and combat legibility C3 (EG-X5) are the road's. On the reading this costs living balance 8.0 → 6.0 (F1 is a floor) and narration 7.5 → 6.5. | **Recommendation:** keep the road (the AI's corps finally reach the war they declared) and read F1 as the benchmark's measure of a France that does not come home; if the floor must stay green, either lever does it — `enemy_ai.THE_MARCH_READS_THE_LAWFUL_ROAD` or `world_state.CAMPAIGN_PAY_ON_FOREIGN_SOIL` — never a tuned AI constant. Rejected: re-scripting the commanded arm (the benchmark is fixed, §4.2). | **the user** — `SCORE_FINISH_SPEC.md` §6 row 24. Done-when: the user rules (keep, flip the lever, or amend F1). ⟨SF step=9 · SF-RR4 · pillar=living_balance⟩ |
| **EG-D3** | **A bench for the secondaries at war** (found ruling EAD-6). Spain at war holds 37–50k gold it cannot spend (its one corps stands on foreign soil; it has no bench); the Marshalate's rung needs an authored pool. Measured with a bench for Sweden, Spain and Bavaria: each commissions 4–5 marshals per seed; enemy attacks +8 / +23 / +16; France 22 / 26 / 28 provinces at turn 40; the series diverges at [10]. | **Offered, not built** — authored content (two or three historical generals a court: Spain's Cuesta, Blake, La Romana; Sweden's Armfelt's peers Toll and Adlercreutz; Bavaria's Wrede) with a balance consequence. | **the user** — SF-RR4's content (§3 Step 9). Done-when: the user rules; if built, the pools authored and validated, the series re-recorded once with attribution. ⟨SF step=9 · SF-RR4 · pillar=ai_aliveness⟩ |

## Score Finish Step 8 — the final reading's design items (SFR-DR) — filed October 5, 2026 (**1 row — SFR-DR1 RULED and BUILT October 5, 2026 in the economy audit (`SCORE_FINISH_SPEC.md` §6.7)** — memo `docs/audits/SCORE_FINAL_2026_10_05.md`; defects `BUG_FIXES.md` §Score Finish Step 8)

| Row | Item | Recommendation | Owner |
|---|---|---|---|
| **SFR-DR1** | **The league declares and rarely strikes.** On the final reading's CMD-A arm the next league (Britain, Russia, Austria, Hanover, Sardinia, Sweden) declares at turn 31 and then attacks on 1 of its 10 turns: enemy phases of 1–3 actions and 0 attacks, "their formations remain beyond our sight", while France's Net runs −985 to −1,177 a turn at war. AI aliveness C6 (visible attacks on ≥ 50% of the turns at war) reads 5/19 there, so the item fails with or without SFR-I5's reader correction (CMD-H 8/10 and CMD-M 11/17 pass under it). At the baseline the only war was the opening one and the item read 5/9, 8/10, 7/10. The league's armies are not measured on the arm (fog); which gate holds them — AI-3r's rear-security reserve, the doctrines' slow concentration, or the targets out of reach — is not yet known. | **Recommendation, not applied:** read it first — one probe on the CMD-A save at turn 31 naming, per league court, the rung each corps chose and the restraint that held it (`war_council._restraint_block_reason`, the AI's own reasons), then rule between (a) the league marches on what it declared (the restraint reads the league's combined strength, not each court's alone), (b) the league is a threat that holds France's corps at home and the item is re-worded (a war is alive when France must answer it, not when it is struck), or (c) a beat that says the league has not marched and why. Rejected: tuning any AI aggression constant before the probe (the user's rule — do not tune). | **the user**, after the probe; the probe is SF-RR4's first task (`SCORE_FINISH_SPEC.md` §3 Step 9). Done-when: the ruling built and AI aliveness C6 re-read on the CMD arms, or the item re-worded by the user and the baseline re-read under it; test `tests/test_sf_rr4_the_league_strikes.py`; STATUS line: Step 9's.<br>**✅ RULED + BUILT October 5, 2026 in the economy audit, under the user's delegation (gate record `SCORE_FINISH_SPEC.md` §6.7 item 5, authoritative):** the probe ran first (81 corps-turns of CMD-A classified, four counterfactuals — memo `docs/audits/ECONOMY_AUDIT_2026_10_05.md` §9): no strength restraint held the league; the wall was diplomatic — `form_coalition` declared each member's war without `suppress_unresolved_offensive_cascade`, so the first declarer's offensive cascade swept the others into a war against France alone, at peace with France's allies, whose closed frontiers walled Austria in. **Option (a) re-cast:** each member declares in its own right, as the player's own declaration does, and draws France's defensive allies on itself (`coalition.THE_LEAGUE_DECLARES_IN_ITS_OWN_RIGHT`); **the rider:** a court whose declaration fails is not a member (`A_FAILED_DECLARATION_IS_NOT_A_MEMBER`); rules `SYSTEMS_REFERENCE.md` §97.12; pins `tests/test_economy_audit_2026_10_05.py::TestTheLeagueDeclaresInItsOwnRight` (the named test file above is not created — the pins live with the audit's). **Measured:** AI aliveness C6 ✗ → ✓ on the audit's reading (visible attacks on 14 of 18, 12 of 18 and 19 of 30 turns at war; with the league's two levers down CMD-A reads 7 of 18). Not built here, homed: the court-level beat that says who has not marched and why (EAD-8, SF-RR3) and the march step's lawful road (EAD-7, SF-RR4). ⟨SF step=9 · SF-RR4 · pillar=ai_aliveness⟩ |

## CA9 Design Answers — ✅ ANSWERED Aug 9, BUILT Aug 9–10, REGRESSIONS CLOSED BY ROW PT

> **Record = `docs/audits/CA9_GATE_ANSWERS_2026_08_09.md` (authoritative).**
> **Routing reconciled Aug 14, 2026 (health-check gate):** all three WERE
> built before the Aug-10 playtest that then measured them (the war-age
> penalty PASSED live −30/−15/0; the D2 gate's input defect and the D3
> delivery-seam AP refresher were the playtest's row-2/row-3 findings, both
> closed by row PT Aug 12–14, with PT-J2 landing D1's battle/territory
> re-weight). **The only outstanding acceptance is the played 20-turn
> campaign showing the D2 gate arm fire once — owned by row PT / the HC
> queue** (`docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md` §8). The
> table below is the historical contract:

| Row | Decision | Owner / landing | Done when |
|---|---|---|---|
| ✅ **CA9-D1** peace terms | F14 STAYS; the cheese is the cheap SCORE, not the recommendation. Battles + decisive are ±50 of ±100 with zero territory (EU4 caps battles at 25%); no term reads the war's AGE. Recommended: war-age penalty on acceptance FIRST, battle/territory re-weight after the playtest | `diplomacy.calculate_war_score` + `settlement_scoring`; next session | A short war cannot be settled for cash; a genuinely won war still has an exit (watch the TERRITORY arm); acceptance breakdown NAMES the new term; `BASELINE_SERIES` re-recorded with flip-experiment attribution — ✅ CLOSED (SF-0, Sept 29, 2026): RULED Aug 9, 2026 (`docs/audits/CA9_GATE_ANSWERS_2026_08_09.md`) and BUILT in row PT (PT-I3, the war-age penalty) |
| ✅ **CA9-D2** attack confirm popup | Arm only when band is `unfavorable` (not `even`) AND the marshal is `cautious`. Preview still prints honest numbers on every attack; only the BLOCK narrows | `combat_executor._execute_attack` muster gate; next session | An aggressive marshal charges bad odds unasked (in character); a cautious one asks; one predicate decides both the popup and the copy; CR-5's own bad-odds gate untouched — ✅ CLOSED (SF-0, Sept 29, 2026): RULED Aug 9, 2026 and BUILT in row PT (the attack confirm arms only on unfavorable + cautious) |
| **CA9-D3** grievances + popups | A REVISIT slice, NOT a TTL on N4. Audit every popup producer, queue slot, blocking class and retirement path, then fix. **AUDIT + FIX DESIGN COMPLETE Aug 15, 2026 (PC15-10 attached the number: 19 petition modals in 24 flagship turns) AND THE §6 GATE RULED THE SAME DAY at the recommended defaults under the user's delegated grant ("establish recommendation yourself"): spec + gate record = `docs/PETITION_POPUP_REVISIT_SPEC.md` v1.1, authoritative** — §2 ledgers what already landed (N4 half-fixed by A3/PT-A1, N8 fixed by A9, N21 half-fixed by A13, A4/A10 done, the objection-leak item REFUTED on master), §4 designs the remainder (F1 "The Antechamber" tier split · F2 subject-linked retirement · F5 four latents incl. the cappable mutual-spiral beat · F6 W7 preempt · F7 three surviving drains + census pin · F8 justified queue order · F9 stash-and-raise chokepoint · F10 load validity), §6 = the RULED gate (Q1(a)/Q2(a)/Q3/Q4/Q5 + the Q1 L1-liveness re-open condition riding §8) | ✅ **BUILT AND ACCEPTED September 27, 2026** — B0 → B5 all landed (spec §9); the §8 acceptance re-run passed all five items (3 blocking petition modals in 24 flagship turns, was 19; 0 silent losses; Q1(a) stands) — record `docs/audits/PC15_10_B5_ACCEPTANCE_2026_09_27.md`. Old starting list superseded by spec §2/§4 | Every producer has a retirement path; nothing blocks a channel indefinitely; the queue order is justified rather than accreted — mapped to fixes in spec §4 preamble; acceptance = spec §8 (≤9 modals/24 flagship turns, zero silent losses) |

**Then ONE playtest** covering the three new slices AND the 31 rows landed
August 9 — which also discharges the owed visual sign-off on `Supply: Unknown`
(region panel + map tooltip) and the per-court fog line.

---

## HC-D1 — Glory as a diplomatic TERM (the mechanical half of HC-3)

> **Filed August 14, 2026 by the health-check design gate**
> (`docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md` §4). HC-3 built the
> FLAVOR half only: envoy refusal/capitulation variants naming the opposing
> crowned (★) marshal (`diplomatic_templates.crowned_name_clause` /
> `crowned_incoming_clause`, display-only, GR6). **The mechanical half — an
> acceptance/intent term that READS glory (a crowned marshal on the border
> pricing into a court's willingness to sign or to fight) — is deliberately
> NOT built.**

| Row | Owner / landing | Done when |
|---|---|---|
| **HC-D1** glory → acceptance/intent term | **The Victory & Objectives Pass gate (ROADMAP positions 12–13)** rules it in or out | A gate ruling that BUILDS it (named acceptance component + shown-in-breakdown + test file named there) or REJECTS it with reasons recorded in that gate's record; either disposition closes this row — RE-HOMED → ROADMAP 13 (the Victory & Objectives Pass gate) (SF-0, Sept 29, 2026; `SCORE_FINISH_SPEC.md` §1.3 'owned elsewhere') |

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Player Feedback (Wave 3 remaining) | 7 | Open — R129/R128 → 8.EVAL triage; R131/R132/R17d-f → queue item 6 (8.EVAL) |
| Nation Rivalry System (EU4-inspired) | 1 | Superseded by Memory and Pressure v2.4.3 (COMPLETE); dynamic-agenda residual → queue item 5 |
| Territorial Promises (Wave 3) | 1 | ✅ LANDED April 2026 as war bargains (`WAR_BARGAIN_SPEC.md`) |
| War System Overhaul (EU4-inspired) | 4 | ✅ LANDED — war_objectives / power cap / forced_alliance / liberation live in code |
| AI Diplomacy Improvements | 3 | N1 verified live; A4 historical note; A3 residual rides queue item 5 (8.EVAL) |
| Gold Sink Options (B4) | 1 | Re-pointed → `docs/ECONOMY_REVISIT_SPEC.md` EC-2 |
| Wave 4 — New Features | 19 | **✅ DISPOSED at 8.EVAL July 16, 2026** (`docs/audits/EVAL_8_2026_07_16.md` §2): R117/R59/R153/R154 already handled; R26 → EC-5, R161 → EC-8, R158 → CR-7, R162 stays gated behind the Nation-Agendas gate; R22/R25/R27/R35/R118/R127/R133 → the Pre-EA Diplomacy & Flavor Content Menu row; R32/power_score/R24/R33/R36 DROPPED with reasons |
| Wave 5 — Game Review Findings | 8 | **✅ DISPOSED at 8.EVAL July 16, 2026** — routed items verified: R155/R157 residuals ride the promoted Nation-Agendas core + landed voice work; R152 residual folds into the closed queue-item-6 record; R158 → `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-7 |
| Jealousy System | 1 | Separate design gate; Marshal Content Pass MC-3 now an effective prerequisite |
| **Wave 6 — Creative Capstone (July 10, 2026)** | 14 | **✅ APPROVED IN FULL July 10** (6 expansions + 6 escalations + 2 gate additions: Dynamic Battle Naming, Literal Doctrine); owner = `WAVE6_FUN_FACTOR_SPEC.md` (12 build slices W6-0..W6-11) |
| **Estate Second Pass deferrals (July 11, 2026)** | 4 | **ESP-1 + ESP-2 + ESP-4 ✅ LANDED July 11, 2026 with the Jealousy v3.2 build** (ESP-4 folded per its own row's fold-in clause; record = `JEALOUSY_SPEC.md` §0.3/§0.4, tests `test_estate_riders_esp.py`); ESP-3 respect-by-treaty → diplomacy gate (unchanged) |
| **Total** | **63** | |

---

## Post-Fix Routing Update

The old bug-phase gate is now cleared. Sessions 1-7 in `docs/BUG_FIXES.md` are complete, and the diplomacy contract is now stable enough to plan legitimacy and strategy work on top of it.

### Live foundations now documented

- `PL-27`, `PL-34`, and `PL-32` are complete.
- The Envoys inbox / mailbox panel is live, including `GET /mailbox`, `POST /mailbox/activate`, stable mailbox identity, and `dialogue_manager.get_mailbox_count()` as the badge source.
- `world.diplomatic_queue` is gone; the shipped follow-up refactor replaced the old cross-turn mailbox persistence with current-turn envoy items (`Not Now`, same-turn reopen, end-turn lapse).
- Proposal / clause display ownership is centralized in backend formatters, so popup payloads and reopen flows use the same labels.
- Session 6 contract refactors are complete: `/command` starts from `build_base_response()`, remaining diplomacy popups use typed response paths, and `main.gd` routes modals through the registry/dispatcher layer.

### Historical spec queue (April 16, 2026 rescope; superseded by April 28 status)

This queue records the April 16 diplomacy rescope. It is no longer the live implementation queue. Current status is tracked in `docs/STATUS.md`; items 1-4 below are ALL LANDED — BPH, WPS, and WB landed, and Ally Participation + Common Peace LANDED as the Imperial Settlement system, complete through Slice G1 (July 2, 2026, commit `1a9da53`).

1. `Memory and Pressure` (renamed from `Reliability + Commitments` April 16)
   **✅ COMPLETE — Memory and Pressure v2.4.3, all slices landed (see `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`). The remaining-work list and the "~68-74 tests, ~3 sessions remaining" estimate below are historical v2.2-era text.**
   Substrate (betrayal memory, concern witness scope, hard-reject posture, episode_id, structured warnings) is **shipped**. Remaining work this phase: seed `nation_concerns` (4 authored pairs), wire `direct_concern_mod` + `concern_conflict_mod` + graduated `bilateral_betrayal_mod` into acceptance, wire third-party anger on ratification, redemption tick (`actor_honored_turns` +3 / 5 honored turns at OPEN_BORDERS+), rename `alliance_paradox` → `commitment_paradox`, ship C3-lite presentation pass (spotlight tier, split-voice render, named-diplomat resolution per Voice Bible). See `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.2, `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` v0.4 (C3-lite). ~68-74 tests, ~3 sessions remaining (Slice C split into Godot-surfaces + tests/mock-prose sessions; v2.2 renames rivalry→concern for balance-of-power scale architecture + adds auto-downgrade rule + France-Austria concern pair + Make Amends verb).
   **Scale note (v2.2):** `nation_concerns` is named for the target dynamic balance-of-power architecture (see spec §7.7). v0.1 ships static seeded values; dynamic concern evaluation is `Nation Agendas` scope (queue item 5).
2. `Bilateral Peace Hardening`
   **✅ LANDED — shipped per `docs/BILATERAL_PEACE_HARDENING_SPEC.md`.**
   Tighten separate peace / bilateral peace preview, explicit term ownership, promise-breach warnings, and peace-treaty legibility before any ally-aware settlement system exists. **Needs dedicated spec.**
3. `War Purpose + Score Semantics`
   **✅ LANDED — shipped per `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`; `war_objectives`, forced alliance, and liberation are live in code.**
   Collapse war objectives, ticking war score, vassalage power cap, forced alliance, and liberation into one war-goal / score-legibility spec. **Needs dedicated spec.**
3.5. `War Bargains` — `docs/WAR_BARGAIN_SPEC.md`
   **✅ LANDED April 2026 — the `war_bargain` mechanic shipped per the spec.**
   The named-enemy bilateral promise mechanic split out of `Reliability + Commitments` v1.0 in the April 16 rescope. Adds `war_bargain` clause type, lifecycle (active / triggered / fulfilled / void / breached), `join_opportunity` ally-entry contract, counter-bargains, `war_entry_score`, Bargain Review surface, and the WB-D presentation extension (bargain spotlights, scope-branched copy, response routes). **Depends on items 1-3.** Implementable as a single Peace Deals phase precursor before item 4. ~80-90 tests.
4. `Ally Participation + Common Peace`
   **✅ LANDED — shipped as the Imperial Settlement system, complete through Slice G1 (July 2, 2026, commit `1a9da53`); see `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 and `docs/STATUS.md`.**
   Build contribution, consultation, ally beneficiaries, and common peace as a separate wartime-flow system. **Current state:** the dedicated spec and implementation plan now own the active Slice A handoff; this item is no longer merely a later-direction draft.
5. `Nation Agendas + Motive Legibility`
   **✅ DESIGN GATE HELD July 17, 2026 — the agenda core is SPECCED and owned: `docs/NATION_AGENDAS_SPEC.md` (§0 gate record; authored decks + dynamic activation, full coupling in pass 1, R162 owned as slice NA-5). R123/R124/A3/R155-residual/R156 all consume through that spec's §5 seams; this queue item is CLOSED as a routing row.**
   **✅ RE-SCOPED + PROMOTED at 8.EVAL (July 16, 2026 — record `docs/audits/EVAL_8_2026_07_16.md` §1).** The motive-LEGIBILITY half is LANDED piecemeal (W6-9 war room + assess chip, W6-10 register bank + ask variety, UI-6 surfaces, DEF-1 voices; verified with file:line evidence in the gate record) and the `nation_concerns`-to-dynamic sub-item is OBSOLETE (zero code presence — superseded by the live hegemony/bloc-share machinery). **What survives is the AGENDA core — `R123` (econ-strategy triggers), `R124` (isolation/alliance-splitting plays), `A3` (enemy-AI war-vs-diplomacy choice), the `R155` residual (personality-driven timing/persistence/target choice), `R156` (diplomacy strategically optional) — and it is PROMOTED to the Phase 8.5 design-gate centerpiece** (8.5 = Events, Goals & National Identity; the agenda system IS the "Goals & National Identity" diplomacy pillar). Needs its user design gate at 8.5; propose-then-build.
6. `Talleyrand Desk + Explanation Layer`
   **✅ CLOSED at 8.EVAL (July 16, 2026 — DROPPED as landed; record `EVAL_8_2026_07_16.md` §1).** ~6 of the 7 collapsed items shipped piecemeal: R131 cooldown pre-check (`diplomatic_executor.py:270-286`), R132 vassal transparency (W6-3/W6-9 + the UI-6 ledger trend), R17d DP breakdown, R17e trend arrows, R17f mission projection (all in `diplomatic_ledger.py`), R157 voice depth (PL-25 + C3-lite + W6-10 + DEF-1). The sole live residual **R159 (screens should teach mechanics) is RE-HOMED to the Pre-EA Onboarding & Teaching Pass row (§8.EVAL Dispositions below)** — GR9 satisfied, no unowned promise survives.
7. `Economic Diplomacy`
   **RE-POINTED — owner: `docs/ECONOMY_REVISIT_SPEC.md` EC-8 (economic diplomacy, incl. R161). Original text kept as historical context.**
   Collapse `R161` plus diplomacy-facing B4 candidates into one reciprocal-trade / subsidy / pressure spec.

**Diplo-wide ledger rows `DWL-DIP-E7` + `DWL-DIP-METTERNICH`:** ~~their "settlement final gate closes" trigger goes LIVE when the user confirms the Gate 4 visual half~~ **✅ BOTH DECIDED at 8.EVAL July 16, 2026 and ✅ BOTH BUILT + LANDED July 16, 2026 (Batch Q Chunk 2 — see STATUS top entry): E7 = authority-banded defiance floor** — `diplomatic_defiance._defiance_floor_for_authority`: 5% at authority ≥70 (single source `STRONG_EMPEROR_DEFIANCE_FLOOR`), easing to the ordinary 2% below; the whole sabotage arc is reachable again; `DIPLOMACY_SPEC.md §3a` trust-term drift removed in the same slice (`test_session6_diplomacy.py` re-anchored). **Metternich = BUILT small** — `coalition.record_schemer_peace_rejection` at the reject seam plants a once-per-rejection, 5-turn-expiring war-pressure marker (`+2`/marker, cap `+4`) summed in `process_coalition_turn`; anti-stacking (dict keyed by nation); new serialized `WorldState.schemer_rejection_pressure`; `DIPLOMACY_SPEC.md §5c` updated to the landed mechanic; `test_batch_q_metternich_dd8.py` (12). BOTH ROWS CLOSED.

### 8.EVAL Dispositions (July 16, 2026) — the pre-EA rows this gate created

> Gate record = `docs/audits/EVAL_8_2026_07_16.md` (authoritative; §4 = this list's charter). Each row is a GR9 home: owner = the named pass, landing = that pass's build session, completion = the referenced item's own definition.

| Row | Contents | Completion definition |
|-----|----------|----------------------|
| **Pre-EA Balance Pass** | DW-2 war-score-credit calibration (bilateral ×0.3 vs settlement ×0.65 — one constant + dependent-pin retune); co-homed with the STATUS:537 Europe-balance items | Bilateral acceptance credits war dominance consistently with the settlement scorer's felt weight; G4F-9 ladder re-verified |
| **Pre-EA AI Correctness Pass** | AUD-f `_evaluate_marshal` deferred-commit refactor (threat-responder claims + serialized `ai_refortify_cooldown` writes during candidate evaluation) | Evaluation is side-effect-free; M1–M7 harness + `test_ai_audit_2026_07.py` green |
| **Pre-EA AI Depth Pass** | MC-V-4 cautious force-husbanding (design gate FIRST — must coexist with the anti-stagnation machinery); the ROADMAP 8c trio (AI-AI wars, AI vassalization, cross-AI threat) stays at its own 8c row | Gate-blessed design lands with liveness metrics held; **if no pass materializes pre-EA, drop cleanly — no player promise outstanding** |
| **Pre-EA Dialogue Robustness** | S5-4 queue-cap overflow-to-mailbox (push + preempt together) | No dialogue silently dropped at cap; docstring already fixed in Batch Q |
| **Pre-EA Onboarding & Teaching Pass** | R159 (screens teach mechanics) — companion to `TUTORIAL_SCRIPT.md`; **+ "The Congress" candidate (Aug 14 health-check gate, HC-5 deferral): a second authored lesson — a diplomacy/settlement miniature — considered at this pass's gate** | Each core screen names the mechanic it displays; new-player path verified; The Congress built or explicitly dropped at the gate |
| **Pre-EA Diplomacy Polish Pass** | AUD-d M3 territory-sweetener rebuild (reuse VS-3 worth-scaling + the BPH `territory_cede` seam; delete the 2 dead `NATION_DESIRES` territory rows either way) | AI counters can cede real regions with correct direction; ratification live-verified |
| **Pre-EA Diplomacy & Flavor Content Menu** | R22 marriage alliances · R25 vassal personality events · R27 secret treaties · R35 player counter-offers on bilateral incoming offers · R118 acceptance preview · R127 nation-specific advisory intel · R133 point-of-no-return popup · Gneisenau Staff Work | Per-item R-row definitions; user picks the menu at the pass's gate |
| **Next refactoring slice** | S5-D3 hygiene batch (edit-distance triplication, VS-4 predicate single-sourcing = priority, lazy-import documentation, AUD-a's dead `QUEUE_MAX_SIZE`) | Byte-identical behavior, existing VS-4/muster pins green |

**DROPPED at 8.EVAL (explicit strikes, reasons in the gate record §1–§2):** DR-6/queue-item-6 as chartered (landed) · AUD-a envoy flood (fixed twice over, measured 4→7) · AUD-e behavior half (shipped sort canonized; Enemy AI 8.0 held — docs reconciled instead) · arch-plan #23 fixed nation order (canonized; harness-load-bearing) · R32 peace conferences · numeric `power_score` · R24 signing ceremonies · R33 puppet rulers · R36 personal summits · the battle/war narration toggle (narration measured 8.0).

### Still lower priority

- `R162: AI Ultimatums to Player` is no longer blocked by the old attention contract, but it should still wait until the commitment and agenda specs above are written. It adds interruption surface before the core diplomacy has enough political weight. **(July 2, 2026: R162 stays gated behind queue items 5-6, which are owned by the 8.EVAL evaluation gate.)**
- Presentation-only diplomacy polish remains downstream of the grouped spec work above, except for the narrow post-commitments presentation pass proposed in `docs/COMMITMENTS_PRESENTATION_SPEC.md`.

---

## Secondary Post-Fix Items

These refine existing systems and are still implementation-ready later, but they should not displace the grouped spec tracks above.

### R119: Nations Remember Betrayal — **COVERED**
- **Category:** Player Feedback
- **Status:** **Fully covered** by the Memory and Pressure substrate (shipped April 15-16, 2026). `world.betrayal_history` with severity-scaled decay, per-episode strike caps, bilateral `bilateral_betrayal_mod` in acceptance formula, hard-reject posture at 3 active strikes, witness scoping, Make Amends active-redemption verb (v2.1). The original R119 design (flat -10/-20/-30 with half-witness, 20-turn redemption) was superseded by the spec's graded model. No further work needed on R119 itself.
- **Files:** `diplomacy.py`

### ~~R131: Cooldown Pre-Check Warning~~ ✅ LANDED
- **Status:** **LANDED** (`diplomatic_executor.py` cooldown pre-check — recorded shipped at 8.EVAL queue-item-6 below; this row was left open by drift, reconciled Aug 2026 health-check audit).
- **Category:** Player Feedback
- **Summary:** Warn player of proposal cooldowns before opening negotiation dialogue.
- **Details:** Pre-check cooldown before dialogue opens. Show remaining turns + Talleyrand message.
- **Files:** `diplomatic_executor.py`

### R129: Override Feedback in Dispatch
- **Category:** Player Feedback
- **Owner (July 2, 2026):** 8.EVAL triage.
- **Summary:** Add feedback when diplomatic override actions succeed/fail.
- **Details:** Success: +2 trust + dispatch note. Failure: +1 concern boost + dispatch note. Fix timing bug at diplomatic_defiance.py:741.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R128: Sabotage Consequence Feedback
- **Category:** Player Feedback
- **Owner (July 2, 2026):** 8.EVAL triage.
- **Summary:** Track and report sabotage outcomes with Talleyrand feedback.
- **Details:** Track in `world.sabotage_history`. Dispatch note next turn. Trust +3 if Talleyrand was correct.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R132: Vassal Loyalty Transparency — **80/20 LANDED July 10, 2026 (W6-3 `reason` field + W6-9 war-room trend/cause block)**
- **Category:** Player Feedback
- **Summary:** Real-time vassal loyalty deltas and trend tracking.
- **Details:** Lower warning threshold to 30. Show delta when |change| >= 2. Store `prev_loyalty`. Trend arrow in ledger. **Landed shape:** `vassal_loyalty` events carry the dominant-cause `reason` at emission (W6-3 §5.4); the W6-9 assessment renders loyalty + drift trend + the most recent cause per vassal. The residual (ledger trend arrow, threshold tune) stays queue-item-6 (8.EVAL).
- **Files:** `dispatch.py`, `vassal.py`, `diplomatic_ledger.py`, `diplomatic_advisory.py`

### ~~R17d: DP Breakdown Display~~ ✅ LANDED
- **Status:** **LANDED** in `diplomatic_ledger.py` (recorded shipped at 8.EVAL queue-item-6 below; row reconciled Aug 2026 health-check audit).
- **Category:** QoL
- **Summary:** Show DP source/cost components in ledger.

### ~~R17e: Relation Trend Arrows~~ ✅ LANDED
- **Status:** **LANDED** in `diplomatic_ledger.py` (same 8.EVAL record; reconciled Aug 2026).
- **Category:** QoL
- **Summary:** 3-turn history showing direction of relationships in ledger.

### ~~R17f: Mission Progress Projection~~ ✅ LANDED
- **Status:** **LANDED** in `diplomatic_ledger.py` (same 8.EVAL record; reconciled Aug 2026).
- **Category:** QoL
- **Summary:** Estimated completion turn for active missions.

### Memory and Pressure interaction notes (updated for v2.4.3)

These are not new items — they annotate existing items whose scope or interaction changes now that Memory and Pressure v2.4.3 is the active spec.

- **R162 (AI Ultimatums to Player):** Hard-reject posture (3+ bilateral strikes) still informs ultimatum behavior, but the surrounding political pressure is now hegemony-driven rather than rivalry-seeded. A nation at hard-reject posture toward France is both more likely to issue ultimatums (anger-driven) and less likely to accept French counter-offers. Wire this interaction when R162 ships.
- **R123 / R124 (Economic Strategy & Diplomatic Isolation AI):** These collapse into queue item 5 (Nation Agendas + Motive Legibility). AI should now read `hegemony_target_mod`, `bilateral_betrayal_mod`, and (when DG-4 lands) `grievance_modifier` plus bloc geometry to drive subsidy offers, alliance-breaking proposals, and isolation strategy. Static `nation_rivalries` / `rival_conflict_mod` are no longer the data source.
- **R17d (DP Breakdown Display):** Show the live Memory and Pressure acceptance components individually rather than reviving the old composite term: `hegemony_target_mod`, `bilateral_betrayal_mod`, `reliability_modifier`, and later `grievance_modifier` / `composite_floor` when DG-4 is active.
- **R155 / R157 (AI Proposal Voice / Talleyrand Voice Depth):** The C3-lite presentation pass (`COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1) now commits named-diplomat CRITICAL / NORMAL notices, the paradox popup, Balance-of-Europe threshold beats, and Make Amends acknowledgments per `DIPLOMAT_VOICE_BIBLE.md`. The broader scope (personality-driven proposal timing, AI-initiated proposal voice, deep Talleyrand commentary across all diplomacy) remains open and routes to queue items 5-6.

---

## Needs Design Gate

### R160: Nation Rivalry System (EU4-Inspired) — **SUPERSEDED BY Memory and Pressure v2.4.3**
- **Category:** Diplomacy — Balance
- **Status:** Static rivalry seed and the old rivalry-specific acceptance terms were dropped in the v2.4 hegemony refactor. The live political-pressure layer is now `hegemony_target_mod` + `bilateral_betrayal_mod`, with `grievance_modifier` joining later via DG-4. The original R160 design is therefore superseded by `RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3 rather than partially awaiting completion.
- **Remaining (unshipped):** any future dynamic rivalry / agenda system must grow out of bloc geometry, betrayal memory, grievance persistence, and AI agendas rather than restoring `nation_rivalries` / `direct_rivalry_mod` / `rival_conflict_mod`. That work still belongs to queue item 5 (`Nation Agendas + Motive Legibility`).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_ledger.py`, `world_state.py`

### R151: Territorial Promise Clauses — **LANDED via WAR_BARGAIN_SPEC (April 2026)**
- **Category:** Diplomacy Feature
- **Disposition (July 2, 2026):** ✅ LANDED — the `war_bargain` mechanic shipped April 2026; the "scheduled in the Peace Deals phase" text below is historical.
- **Status:** The broader concept (France makes named-enemy promises to allies, tracking obligation, breach/fulfillment, betrayal consequences) is now fully designed as the `war_bargain` clause type in `docs/WAR_BARGAIN_SPEC.md`. The spec covers creation, validation, lifecycle, fulfillment, breach/void, war-entry integration, and the Bargain Review surface. Scheduled in the Peace Deals phase after `Bilateral Peace Hardening` + `War Purpose + Score Semantics` (queue items 2-3.5).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_executor.py`

### Jealousy System (v3.1 spec)
- **Category:** Marshal Feature
- **Summary:** Glory Ladder targeting, personality expressions, escalation, confrontation popups.
- **Details:** Full spec at `docs/JEALOUSY_SPEC.md`. Core design settled. Top of ladder: +1 all core stats while #1. Defeats cost glory. DO NOT CODE WITHOUT USER APPROVAL.
- **Sequencing note July 2, 2026:** the Marshal Content Pass (`docs/MARSHAL_CONTENT_PASS_SPEC.md`, MC-3 relationship authoring) is effectively a prerequisite — the shipped 21-marshal roster has zero authored relationships; a v3.2 addendum must re-derive scenario impact/tuning against that roster before the gate.

---

## War System Overhaul (EU4-Inspired — Design Gate) — **✅ LANDED**

**Disposition (July 2, 2026):** this entire section LANDED via the War Purpose + Score Semantics work (`docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`) — `world.war_objectives` ticking score, the vassalage power cap, the `forced_alliance` clause type, and the liberation mechanic are all live in code. The text below is preserved as historical design intent.

Full design spec in `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` lines 215-722. Addresses core balance problem: defensive play is overwhelmingly superior because no ticking score incentivizes holding territory over time.

### War Objectives + Ticking War Score (5th Component)
- **Summary:** Player-chosen war goals at war declaration (Conquest, Subjugation, Forced Alliance) and auto-assigned goals (Defense, Liberation). Each goal has a ticking target region — holding it accumulates war score over time (±25 cap).
- **Ticking rates:** Conquest +2/turn (enemy capital), Subjugation +3/turn (enemy capital, power cap gated), Forced Alliance +2/turn (enemy capital), Defense +1/turn (any enemy region), Liberation +1/turn per vassal capital.
- **New field:** `world.war_objectives: Dict[str, Dict]` — diplo_key to `{type, target, accumulated}`
- **Files:** `diplomacy.py` (calculate_war_score 5th component), `world_state.py` (field + per-turn accumulation), `war_status.py` + `war_detail_popup.gd` (display), `diplomatic_executor.py` (war goal selection dialogue)
- **Est. sessions:** 2-3, ~20 tests

### Vassalage Power Cap
- **Summary:** Gate vassalization on National Power ratio: target must be ≤ 50% of player's power. Power = sum of base income of controlled regions + partial vassal contribution.
- **Why:** Prevents France from vassalizing Austria at war_score 80 — only small nations should be vassalizable.
- **Files:** `vassal.py`, `diplomacy.py`, `diplomatic_ledger.py`, `diplomatic_templates.py`
- **Est. sessions:** 1, ~10 tests

### Forced Alliance Clause Type
- **Summary:** New clause type — war goal forces enemy into ALLIANCE + Continental System on peace. Follows vassalage pattern for wiring (acceptance values, harshness, keywords, display names, state mapping).
- **Historical:** Napoleon's primary war objective (Austerlitz, Tilsit, Jena).
- **Files:** `diplomacy.py`, `diplomatic_dialogue.py`, `diplomatic_executor.py` (4 state maps), `display_names.py`, `diplomatic_templates.py`, `world_state.py`
- **Est. sessions:** 1-2, ~10 tests

### Liberation Mechanic
- **Summary:** Coalition war goal — liberating vassals. On peace: `release_vassal()` + auto `DEFENSIVE_ALLIANCE` with liberator.
- **Files:** `world_state.py` (_ratify_treaty), `vassal.py` (release reason)
- **Est. sessions:** 1, ~6 tests

---

## AI Diplomacy Improvements (Ready — Small Fixes)

### N1: AI Preemptive Alliance Against Rising Threat
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 69-130
- **Summary:** Trigger 5 in AI-AI diplomatic evaluation. When threat > 40, nations with negative relations toward France form defensive alliances with each other. Creates diplomatic web before coalitions.
- **Audit status (Apr 10):** Already implemented in `ai_diplomacy.py` Trigger 5. Keep as verified reference, not as a pending refinement unless the behavior needs expansion.
- **Files:** `ai_diplomacy.py`
- **Est. tests:** ~7

### A3: AI War Exhaustion Integration
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 55-61
- **Disposition (July 2, 2026):** the proposal-side integration is LANDED in `ai_diplomacy.py`; the residual (the `enemy_ai.py` war-vs-diplomacy choice) rides queue item 5 (`Nation Agendas + Motive Legibility`), per the Memory and Pressure interaction note above.
- **Summary:** Proposal-side war exhaustion integration is already partially landed in `ai_diplomacy.py` (`effective_p1_threshold`, `effective_stalemate_turns`). Remaining work, if any, is broader war-exhaustion integration in `enemy_ai.py` and diplomacy-vs-war choice, so this item now needs re-scope rather than blind implementation.
- **Files:** `ai_diplomacy.py`, `enemy_ai.py`
- **Est. tests:** ~4

### A4: AI Harsh Peace Gold Formula Rebalance
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 47-53
- **Summary:** Historical note only: the focused audit confirmed the live formula already uses `max(200, int(war_score * 5 * gold_mult))` in `ai_diplomacy.py`. Keep this item only if further rebalance is desired.
- **Files:** `ai_diplomacy.py`
- **Est. tests:** ~2

---

## Wave 4 — Decide Gate (Per-Item Approval)

These are new feature designs. Each needs individual approval before implementation.

**July 2, 2026:** per-item user approval is still required. Items already re-pointed above have new owners: R26 → `docs/ECONOMY_REVISIT_SPEC.md` EC-5 (Continental System); R161 → `ECONOMY_REVISIT_SPEC.md` EC-8; R162 → gated behind queue items 5-6 (8.EVAL).

| ID | Item | Summary |
|----|------|---------|
| R22 | Marriage Alliances | Dynastic bonds: +20 rel, block war 5 turns, 3 DP |
| R32 | Peace Conferences | Multi-nation negotiations, 3 DP, +15 acceptance |
| R117 | Advisory Actionability — **✅ LANDED July 10, 2026 via W6-9** (the war-room assessment's ONE recommendation ends in an executable option: `execute_suggestion` / `expand_options`) | Advisory ends with executable options |
| R123 | Economic Strategy AI (P9) | Gold > 600 triggers subsidy offers, trade pressure |
| R124 | Diplomatic Isolation AI (P10) | Split enemy alliances with generous terms |
| R133 | Point of No Return Event | One-time Talleyrand popup at threat 40 |
| R28 | Talleyrand Voice Bank | 5-8 variants per situation type |
| R127 | Nation-Specific Intelligence | Per-nation personality lines in advisory |
| R24 | Treaty Signing Ceremonies | Talleyrand ceremony text on ratification |
| R25 | Vassal Personality Events | 3-4 random loyalty-gated events per game |
| R26 | Continental System Buff | Backend exists, needs player command + creative rebalance |
| R27 | Secret Treaties | Hidden treaties, 10%/turn discovery chance |
| R33 | Puppet Rulers | Named rulers with personality, events |
| R35 | Player Counter-Offer Terms | Player specifies clauses (Godot popup) |
| R36 | Personal Summits | Face-to-face meetings, +15 acceptance 3 turns |
| R59 | ~~Literal Personality Triggers~~ | **SUPERSEDED by W6-5 The Literal Doctrine (user call, July 10, 2026):** literal marshals never object BY DESIGN — the fantasy is "generals who do what they're ordered." Engagement = order echo + fidelity beat + precision captions + muster-preview warnings (`WAVE6_FUN_FACTOR_SPEC.md` §7; triggers converted to a doctrine comment in `personality.py`, pinned by `test_w6_literal_doctrine.py`). |
| R118 | Enhanced Acceptance Preview | Top 3 positive/negative components + Talleyrand hints |
| R161 | One-Time Trade | Trade gold, manpower, territory directly without ultimatum or state change |
| R162 | AI Ultimatums to Player | Building Blocks: AI uses same ultimatum system as player. Needs popup, response flow, AI decision tree |

---

### R161: One-Time Trade (Expanded)
- **Category:** Diplomacy Feature
- **Owner (July 2, 2026):** re-pointed to `docs/ECONOMY_REVISIT_SPEC.md` EC-8 (economic diplomacy, alongside queue item 7). Original design text kept as historical context.
- **Summary:** Voluntary, consensual resource exchange between nations — no state change, no coercion. The "carrot" complement to ultimatums (the "stick").
- **Details:** Player proposes a trade (gold, manpower, territory) to any nation at OPEN_BORDERS or better. Both sides give and receive. Uses existing conversational diplomacy flow with `generate_trade_terms()`. Acceptance via full formula. No threat increase, no relation penalty — pure commerce.
- **Building Blocks principle:** Reuses `_ratify_treaty` clause processing, `calculate_acceptance()`, dialogue enrichment, splash damage (none for trades). Same executor path as proposals but with `type: "trade"` and no state transition.
- **Distinction from ultimatums:** Trades are voluntary (both sides benefit), ultimatums are coercive (one-sided demands with diplomatic cost).
- **Gates needed:** Trade balance formula (what's fair?), AI trade evaluation, frequency limits.
- **Files:** `diplomatic_executor.py`, `diplomatic_templates.py`, `diplomacy.py` (new base disposition for trade), `diplomatic_dialogue.py`
- **Est. sessions:** 1-2, ~8 tests

### R162: AI Ultimatums to Player
- **Category:** AI Diplomacy — Building Blocks
- **Status (July 17, 2026):** ✅ **OWNED — slice NA-5 of `docs/NATION_AGENDAS_SPEC.md` (§8 answers the gate questions: trigger rung, agenda-target terms, rejection → bounded expiring coalition-pressure marker not a free war, mailbox transport + dtype whitelist).** Built after NA-0..NA-3 land and are verified live; no further gate. The details below are historical context.
- **Status (July 2, 2026):** stays gated behind queue items 5-6 (Nation Agendas + Talleyrand Desk), which are owned by the 8.EVAL evaluation gate.
- **Summary:** AI nations issue ultimatums to the player using the same ultimatum system the player uses. Building Blocks principle (§23): same systems, different input values.
- **Details:** AI evaluates ultimatum opportunity in `enemy_ai.py` decision tree (new P-trigger). Conditions: military superiority over player in a region, low relations, not in coalition with player. Generates terms via `generate_ultimatum_terms()` (same function player uses). Delivered as popup with [Accept][Reject] options. Rejection gives AI casus belli. Same splash damage, threat (reduces player threat if AI is aggressor), and cooldown mechanics.
- **Building Blocks reuse:** `generate_ultimatum_terms()`, `calculate_acceptance()` (inverted — player is target), `_ratify_treaty` clause processing, splash damage formula, global cooldown (separate AI cooldown counter).
- **Gates needed:** AI trigger conditions (when is ultimatum better than war declaration?), player response popup design, threat direction (does AI ultimatum reduce or increase player threat?).
- **Files:** `enemy_ai.py` (new P-trigger), `diplomatic_executor.py` (AI ultimatum handler), `main.gd` (new popup), `ai_diplomacy.py`
- **Est. sessions:** 2-3, ~12 tests

### National Power Tiers (Great Power / Secondary / Minor) — Design Gate
- **SUPERSEDED — April 17, 2026.** Canonical `power_tier` is now defined in `docs/SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy". Under the canonical definition, `power_tier` is **authored scenario data** with values `major / secondary / minor` and is **never recomputed at runtime**. The dynamic numeric-tier model below is superseded and must not be implemented. If a numeric strength-derived signal is needed for AI threat weighting, coalition calculations, or dispatch priority, it lives in a separate `power_score` field that does not overwrite `power_tier`. The original text is preserved below as historical design intent.
- **Residual disposition (July 2, 2026):** the tier model stays SUPERSEDED — Phase 0's authored `power_tier` shipped with the real-map cutover. The optional numeric `power_score` idea: evaluate at the 8.EVAL gate, else drop.
- **Category:** Diplomacy + War — Balance + Immersion
- **Summary:** Dynamic numeric power tiers (`great_power / secondary_power / minor_power`) calculated from controlled regions, income, military strength, and partial vassal contribution. Affects acceptance formula (great powers resist vassalization), coalition formation (great powers lead coalitions, minor powers join), war settlement (consultation rights scale with tier), and AI threat assessment (great powers escalate coalition faster).
- **Origin:** Conceptual three-tier model exists in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §8.3. Data fields (`nation_power_scores`, `nation_power_tiers`) listed as deferred in `RELIABILITY_COMMITMENTS_SPEC.md` §12.3.
- **Design decision from WAR_SETTLEMENT spec (superseded):** "These tiers come from numbers, not authored nation labels. The map can create a new quadrangle if power shifts." — This position is reversed by the Phase 0 canonicalization: tiers are now authored, not numeric. A separate `power_score` may still be derived from numbers for non-tier uses.
- **Interaction with Memory and Pressure:** great powers could have different rivalry intensity defaults (primary only between great powers; secondary between great-and-minor), betrayal tolerance thresholds (great powers hold grudges longer), and Make Amends cost scaling (reparations to a great power should cost more than to a minor).
- **Gates needed:** numeric formula for calculating power scores, threshold ranges (what income/strength makes a "great power"), whether tiers are recalculated per turn or per-war, how tiers interact with the acceptance formula's existing modifier caps.
- **Natural home:** alongside `War Purpose + Score Semantics` (queue item 3) since power tiers inform war objectives and settlement legitimacy. Or as a sub-item of the later `Ally Participation + Common Peace` (queue item 4).
- **Files:** `world_state.py` (data), `diplomacy.py` (formula + tiers), `diplomatic_ledger.py` (display), `ai_diplomacy.py` (threat evaluation)
- **Est. sessions:** 1-2 for the data layer + formula, plus formula-integration touches across existing systems

---

## Gold Sink Options (B4 Balance — Design Gate)

**Priority:** MEDIUM | **Phase:** Pre-EA refinement

**RE-POINTED (July 2, 2026):** owner is `docs/ECONOMY_REVISIT_SPEC.md` EC-2 (the B4 gold-sinks gate). The candidates below are re-cost candidates for the ~3.4k/turn 1805 economy — France income is ~3.4k/turn on 28 provinces, upkeep ~950g, and the whole building stock costs ~1.85k — so this section's "~700g vs ~250g" numbers are legacy (19-region map). Original text kept as historical context.

Gold accumulation is a known design gap (~700g/turn income vs ~250g upkeep). Manpower-gated recruitment means gold piles up with no meaningful spending options. This section tracks candidate gold sinks for evaluation.

**Forced march REJECTED** — trivializes cavalry's 2-region movement advantage, which is cavalry's core identity.

### Leading Candidate: Province Development
- **Cost:** Variable (200-500g per investment)
- **Effect:** Invest gold in controlled region to boost supply cap, income, or repair war damage faster
- **Design appeal:** Creates invest-now-vs-save tension, rewards holding territory, ties gold to strategic positioning
- **Needs:** Investment tiers, per-region cooldown, diminishing returns formula, AI investment priority

### Other Candidates (evaluate after Province Development)

| Option | Cost | Effect | Notes |
|--------|------|--------|-------|
| Diplomatic gifts/bribes | 200g | +5 relation (once/turn/nation) | Gold becomes diplomacy tool |
| Mercenary garrisons | 400g | Defensive garrison without stationing marshal | Frees marshals for offense |
| Recruitment bounties | 300g | Double manpower regen for 1 turn | Accelerates rebuilding |

---

## Enemy AP Rebalancing (Deferred — Post Full Map)

**Priority:** LOW | **Phase:** After full 1805 map implementation

**RE-POINTED (July 2, 2026):** owner is `docs/ECONOMY_REVISIT_SPEC.md` EC-4 (enemy AP). The revisit trigger fired July 2, 2026 — the full 1805 map shipped with the real-map cutover. NOTE: the EC-0 AP-reset defect must land first. Original text kept as historical context.

Enemy AI action budget (currently 4 paid AP per nation) may need rebalancing once the full map is implemented with all nations, regions, and marshal counts at scale. Current 4-nation, 19-region map doesn't stress the action economy the same way a full campaign will. Revisit AP values, per-nation scaling, and aggregate action counts after full map playtesting.

---

## Wave 5 — Game Review Findings (Design Gate)

Cross-system findings from comprehensive review. Needs design gate as a batch.

**July 2, 2026:** per-item user approval is still required. Items already re-pointed above have new owners: R158 → `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-7 (parser confidence feedback).

**Diplomatic Term Novelty — PARTIALLY ABSORBED into PL-25 (BUG_FIXES.md).** PL-25 covers the 80/20: amount jitter, personality-biased pen nudge, nation desire profile bias in `_build_base_terms()`, situational flavor lines. R155/R157 retain the remaining full scope: hawk/dove personality weight table for ALL AI proposals (not just Talleyrand's pen nudge), deep `TALLEYRAND_COMMENTARY` integration, and AI-initiated proposal personality voice.

**Focused audit routing (updated July 2, 2026):** R155 / R156 remain validated by code evidence and route to queue items 5-6 (8.EVAL). R160 is SUPERSEDED by Memory and Pressure v2.4.3 (see its row above) — it is no longer a pending upgrade. The diplomacy mailbox / recovery surface LANDED long since; R162 is not transport-blocked, it stays gated behind queue items 5-6.

| ID | Item | Summary |
|----|------|---------|
| R152 | Authority System UI Visibility | Authority impact not visible enough to players |
| R153 | ~~Literal Personality Triggers~~ | **SUPERSEDED by W6-5 The Literal Doctrine (user call, July 10, 2026)** — see the R59 row; literal never objects by design. |
| R154 | Combat Morale Spiral | Morale death spiral needs circuit breaker |
| R155 | AI Proposal Personality Voice | Partially absorbed into PL-25. Remaining: visible motive / personality in timing, terms, persistence, and player-facing explanation |
| R156 | Diplomacy Strategic Optionality | Diplomacy feels optional vs military path |
| R157 | Talleyrand Voice Depth | Partially absorbed into PL-25 (situational flavor, personality pen nudge). Remaining: deep commentary integration |
| R158 | ~~NL Parser Confidence Feedback~~ | ~~Show parse confidence to player~~ **STRUCK by the CR-6 triage, September 23, 2026** (`COMMAND_ROBUSTNESS_SPEC.md` §12.5, its owner row CR-7 having closed with it in "backlog"): the fast parser's confidence is **0.90–1.00 on every measured cell where the game acted on an order the player did not give** (STATUS ruling D6, September 20, 2026), so displaying it would tell the player the game is sure exactly when it is wrong. The feedback R158 asked for ships another way — the relay (`relay_note`), the named refusals and the completer's offers. **Re-open** only if a CALIBRATED confidence exists (HC-L's L-0/L-2 model, if built, with a measured calibration). |
| R159 | Information Screen Teaching | Screens don't teach mechanics |

---

## Historical Precision (1805 Campaign — Future Refinement)

These items are conscious trade-offs where v0.1 chose recognizability, immersion, or implementation speed over strict period accuracy. Each has an audit trail, not a bug. Track for EA scope when the full 1805 campaign lands. Added April 16, 2026 from the Memory and Pressure creative audit.

### P1: Period-accurate diplomat roster for 1805
- **Summary:** The four foreign diplomats in `backend/models/diplomat.py` (Hardenberg / Metternich / Castlereagh / Einsiedel) are recognizable Napoleonic-era names but historically took their depicted roles **after** the 1805 campaign start: Hardenberg as Prussian chancellor from 1810, Metternich as Austrian foreign minister from 1809, Castlereagh as British foreign secretary from 1812, Einsiedel as Saxon minister from 1813. The actual 1805 ministers were Haugwitz (Prussia), Stadion or Cobenzl (Austria), Mulgrave (Britain), and Bose or Löss (Saxony).
- **Design trade-off (deliberate):** recognizability was prioritized for v0.1 because the four chosen figures are well known to strategy players and the Voice Bible's Hawk / Schemer / Dove register distinctions were drawn from their historical voices. Swapping them in v0.1 would lose the established register voices without adding mechanical value and would force the Voice Bible exemplars to be re-authored before any useful commitments work shipped.
- **When to revisit:** once the full 1805 campaign ships (Early Access) and the game claims period fidelity as a feature. Swap to the 1805-accurate ministers and port the register notes. The Voice Bible's "Characteristic openings" / "Never says" framework should transfer cleanly — Haugwitz was a Prussian Hawk in the Hardenberg mold, Stadion a Schemer adjacent to Metternich, Mulgrave less distinctive than Castlereagh but workable, Bose closer to Einsiedel's dove register.
- **Revisit condition MET July 2, 2026:** the full 1805 campaign shipped (real-map cutover complete). Still EA-scope; interacts with DEF-1 Roster Voices register authoring.
- **Files:** `backend/models/diplomat.py`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `backend/game_logic/diplomatic_templates.py`, any committed breach / hard-reject mock prose
- **Est. sessions:** 1 (cast swap + voice port + test refresh)

### P2: Britain reactive bloc pressure (continental-hegemon pattern)
- **Summary:** The v0.1 rivalry model has Britain as France's direct rival but gives Britain no *reactive* posture when France deepens ties with a continental power. Historically Britain opposed any continental hegemon on principle, paying subsidies to any continental power willing to fight France. Flagged in `RELIABILITY_COMMITMENTS_SPEC.md` v2.1 §7.4.C as the #1 historical-texture debt for Memory and Pressure.
- **When to land:** `Coalition Generalization` (D2, follow-up after Memory and Pressure). D2 should include continental-hegemon reactive threat accumulation — not just bloc-target parameterization — so Britain gains automatic threat against any power approaching continental hegemony, not only France by name.
- **Owner (updated July 2, 2026):** the `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` deferred-ledger D2 row. The previously-named "Coalition Generalization (D2)" is not a landed slice — this item rides that deferred-ledger row.
- **Files:** `backend/game_logic/coalition.py`, `backend/game_logic/diplomacy.py`
- **Est. sessions:** folded into D2 spec work

### P3: Diplomatic Ledger sort / filter at scale
- **Summary:** The Diplomatic Ledger's Nations tab currently renders one row per nation. At 5 nations this is clean; at 6-8 full 1805 nations with multiple rivals each, the list becomes dense. Commitments rows (active rivals, betrayal warnings, posture markers) multiply the cell count.
- **When to land:** Pre-EA polish alongside Map Renderer UX pass, or absorbed into the Talleyrand Desk + Explanation Layer spec (diplomacy queue item 6).
- **Urgency raised (July 2, 2026):** 20 nations render now in the shipped 1805 campaign. Owner: queue item 6 (Talleyrand Desk + Explanation Layer) or pre-EA polish.
- **Files:** `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`
- **Est. sessions:** 1 as a standalone UX slice, or folded into the Talleyrand Desk pass

---

## FA slice 16 — rulings the build could not take for itself

| id | P | item | seam(s) | build shape | behaviour test |
|---|---|---|---|---|---|
| **FA-S16-D1** | P2 | **The cannon-fire tax: obeying a standing order costs 2 trust, abandoning it for the guns costs 0** — and slice 3 already priced the identical popup the other way. See the section below for the measured table, the reachability (19 organic asks in the archive, three French marshals, every other turn each) and the three options. | `strategic.StrategicOrderProcessor._respond_cannon_fire` · its sibling `_respond_combat_stalemate` | recommended default (a): `continue_order` → 0, matching the sibling; the resentment stays in the ASK | `test_fa_slice16b_the_price_on_the_button_2026_09_06.py::TestTheTaxIsStillCharged` records the state the ruling changes | ✅ **RULED (a) AND BUILT September 6, 2026** — `continue_order` → 0. Landing record = the boxed **FA-S16-D1 + FA-S16-D2** block in `BUG_FIXES.md`. ⚠ The argument that carried it is **recurrence, not inversion** — see the amended section below. |
| **FA-S16-D2** | P3 | **The cannon-fire trigger is nation-blind** — measured, a French marshal was interrupted, and charged, over Blücher vs Hohenlohe, a Prussian pair neither of whose sides is France. | `strategic._check_interrupts` → `world.get_battles_within_range(marshal.location, 2)` | either a nation predicate, or a docstring saying why there is none | a marshal under orders is not charged for a battle his nation has no stake in | ✅ **RULED AND BUILT September 6, 2026** — the predicate `_cannon_fire_concerns`, behind the lever `CANNON_FIRE_READS_THE_FLAGS`. Landing record = the same boxed block. ⚠ The row's own reproduction is not fixed by its own fix — see below. |

| **FA-S16-D5** | P3 | **The stalemate popup charges −3 on hold AND on cancel and quotes neither** — the same scene as FA-S16-D1, the same "Hold Position" label, one function over. FA-49 put prices on the cannon-fire buttons; `_respond_combat_stalemate` was correctly out of that slice's scope and is still unpriced. | `strategic.StrategicOrderProcessor._respond_combat_stalemate` · `strategic.interrupt_option_costs` | extend the existing pure quoter to the stalemate interrupt type, or state at the seam why this popup carries no numbers | the price on the button is the price charged, for both of its paying arms | ✅ **FIXED September 11, 2026** (slice 17 part h; landing record = the boxed **SLICE 17 (part h)** block in `BUG_FIXES.md`) — `STALEMATE_ABANDON_TRUST` extracted from the two bare literals, the quoter prices hold and cancel from it (`repeated_combat` alike), continue free; quote == charge pinned through the real responder and the wire; lever `THE_STALEMATE_QUOTES_ITS_PRICE`. Original: **OPEN.** Filed September 6, 2026 by the FA-S16-D1/D2 build, which found it beside its own seam and did not absorb it. |
| **FA-S16-D3** | P3 | **A second absolute casualty floor, for a question a landed sibling already answered with a different number** — see the section below. | `battle_report._pick_observation` priority 4 · `dispatch.OWN_MAULED_MIN_CASUALTIES` | pick ONE of the two existing floors; do not mint a third | a 1-vs-58 exchange does not draw the "even the favorable ground could not save him" verdict | ✅ **RULED AND BUILT September 6, 2026** — none of the three filed options: the floor count goes **3 → 2** by extracting the war score's own bare `1000` into `battle_scale`, read by both. Landing record = the boxed **FA-S16-D3 + FA-S16-D4** block in `BUG_FIXES.md`. |
| **FA-S16-D4** | P3 | **The crown beat leaks into the School** — the tutorial has no gate on the glory beats, and the precedent points the other way. | `dispatch.py` · `campaign_log.py` (zero `scenario_name` references in either) | gate the BEAT, or gate the STATE, or neither | a tutorial dispatch does not report a crowning the lesson never taught | ✅ **RULED (a) AND BUILT September 6, 2026** — glory itself sleeps in the School, on its own lever, and PC15-D3's written carve-out is consciously OVERRULED with its defence measured. Landing record = the boxed **FA-S16-D3 + FA-S16-D4** block in `BUG_FIXES.md`. |

### FA-S16-D3 — a second casualty floor, against a landed dissent

> ✅ **RULED AND BUILT September 6, 2026 — and the answer is none of (a),
> (b) or (c).** Landing record = the boxed **FA-S16-D3 + FA-S16-D4** block in
> `BUG_FIXES.md`.
>
> The ruling reframed the question. There were never two floors — there were
> **four answers**, and a `MIN_CASUALTIES` grep finds one of them. The bare
> `1000` inside `diplomacy.record_battle` was already the right number for
> the right quantity (the SUM of both sides), so it was extracted into
> `backend/game_logic/battle_scale.py` and the narrator reads the same
> object. **Floor count 3 → 2, not 3 → 4.** Option (a) is refuted (500 is
> ONE side's dead ANDed with 25% of that corps — two referents a factor of
> two apart, and it under-fires the measured population by 8 points); option
> (b) is refuted by measurement (a national fraction is 1,890 at boot and
> 1,196 by turn 20 while the corps producing these lines fall to 1,148 and
> 593 — it drifts away from FA-44's own case); option (c) is what the
> reframing avoids. **WO-16's 500 is untouched and untuned, so its dissent
> stands unamended.**
>
> ⚠ **The obvious SHAPE was measured and rejected too.** A
> `we_lost and total < FLOOR` early return at priority 3.5 reds a standing
> behaviour pin (total 350, France defending, enemy cavalry over our guns)
> and re-buries PT-D4's rout arm. The gate is **per-arm** on the five
> gravity verdicts; every mechanical-state arm fires at any scale.
>
> ⚠ **A FOURTH answer exists and neither this ruling nor the row saw it**:
> `_pick_bombardment_observation` already answers "how small is small" in the
> same file with a **3% fraction**. It is named in `battle_scale`'s docstring
> and deliberately not changed.

**Filed September 6, 2026 by FA slice 16 (part c).** FA-44 is real: a 1-vs-58
exchange with a defender terrain bonus draws the verdict *"Even the favorable
ground could not save Massena, Sire"* — `_pick_observation` has no scale gate
anywhere in its ladder, and casualties are bound at the top of the function
and never consulted again.

**Why it is a ruling.** The row proposes a **second absolute floor at 1,000**
for the same question a landed sibling already answered:
`dispatch.OWN_MAULED_MIN_CASUALTIES = 500` (WO-16) suppresses the sub-500
briefing headline, and **that constant carries a written dissent** — *"if 500
is tuned TWICE, take the fraction-of-national-strength form."* Minting a
third number for one question, in a different file, with a different value,
is how a game ends up with three answers to "what is a small battle".

**Options.** (a) Reuse `OWN_MAULED_MIN_CASUALTIES` at the report's verdict —
one number, one place, and the existing dissent keeps governing it.
(b) Take the dissent's own escape now and make BOTH a fraction of national
strength. (c) Mint the second absolute floor as filed, and record why two are
better than one.

⚠ **Also correct the row's placement before building any of them.** Its
`_corrected` says "before line 815, priority 2" and its `fix_shape` says
"before :818" — one priority tier apart, and the earlier position is wrong:
it would outrank the fort arms.

**Owner:** the next FA design gate. **Done when** one floor governs the
question, or the record says why two do.

### FA-S16-D4 — the crown beat in the School

> ✅ **RULED (a) AND BUILT September 6, 2026** — glory is dormant in the
> lesson, so the beat stops on its own and PC15-D3's shape is followed
> rather than departed from. Landing record = the boxed **FA-S16-D3 +
> FA-S16-D4** block in `BUG_FIXES.md`.
>
> ⚠ **PC15-D3's written carve-out is CONSCIOUSLY OVERRULED**, and the
> defence is measured, not argued. That clause said glory keeps accruing so
> "the Generals screen stays honest" — but the crown it produces is **+1
> shock / +1 defense / +1 administration**, Ney's admin 3→4 crosses the
> MC-2b Intendance tier boundary (a recruit price), and **Austria's
> Schwarzenberg is crowned in the lesson too**, so it is an AI-side combat
> modifier and not a display at all. What the clause was really protecting
> is `battles_won` — measured **byte-identical** with the lever either way
> (Ney 6 / Davout 5 / Senarmont 5 / Soult 0). Option (b) cannot reach the
> +1 skills; option (c) leaves a live modifier in the classroom.
>
> ⚠ **The leak was FIVE wide, not the four this row counts.**
> `glory_crown_lost` fires twice in the shipped trust lesson and is **never
> written to `event_log`** — only the gain branch logs — so an `event_log`
> census is structurally blind to half of it.
>
> ⚠ **And gating glory alone SWAPS a leak instead of closing it.** §4's
> restlessness loop has a literal arm that never reads the ladder; measured,
> silencing the ladder frees the single allowed warning and **Soult's line
> appears where it does not fire today**. A second guard ships on its own
> lever. ⚠ `marshal_management.gd` is deliberately NOT touched: its "only
> glory answers envy" header is a pinned conscious flip of the R159
> contract, and deleting it costs a second conscious flip.

**Filed with the above.** The archived tutorial digest reads *"Sire — Ney,
crowned four turns ago, has been beaten in the field."* The lesson never
teaches glory, never mentions a crown, and has no gate: `dispatch.py` and
`campaign_log.py` contain **zero** `scenario_name` references between them.

**Why it is a ruling and not a patch.** PC15-D3 is the precedent and it
points the OTHER way — it was ruled "gate the STATE, not the beats", and the
expectation dormancy it built folds into the one `is_dotation_world`
chokepoint so the state is gated and the beats simply follow. FA-98 would be
the first tutorial gate to suppress a BEAT while leaving its state
deliberately alive, which is a different rule, and it should be taken
deliberately rather than inherited.

**Options.** (a) Follow PC15-D3: make glory dormant in the lesson world, and
the beat stops on its own. (b) Gate the beat only, and write down that the
tutorial now has two kinds of gate. (c) Leave it: a tutorial that mentions a
crown is odd but harmless, and the lesson is nine turns long.

⚠ The row's routing note is stale — it defers to PC15-D3 as though that gate
were open. It was ruled and built on August 15, 2026.

**Owner:** the next FA design gate. **Done when** the lesson's dispatch
mentions no mechanic the lesson does not teach, or the record says why it
may.

### FA-S16-D1 — the cannon-fire tax: obedience costs 2, abandonment costs 0

> ✅ **RULED (a) AND BUILT September 6, 2026.** `continue_order` → 0.
> `hold_position` keeps its −3, `investigate` keeps its 0. Landing record =
> the boxed **FA-S16-D1 + FA-S16-D2** block in `BUG_FIXES.md`.
>
> ⚠ **The argument below is corrected by the measurement that took the
> ruling.** "Obedience must not cost more than abandonment" is NOT what
> carries it — the objection channel charges −10 to insist and pays +3 to
> defer, so a price for having your way is house idiom, and five other arms
> charge −3 for abandoning an order. What indicts *this* number is that it
> was **the only recurring trust charge in the game**: the re-ask guard is
> `ignored_turn >= current_turn - 1`, and continuing is the only answer that
> keeps the order alive to be asked again. Bernadotte boots at trust 40 and
> reaches `check_redemption_threshold`'s gate **on his tenth act of
> obedience**. A one-off overrule charge is idiom; a metronome is not.
>
> ⚠ **The rider was factually wrong.** Napoleon was never *charged* —
> `SovereignTrust.modify` returns 0 and moves nothing. He was *told* he had
> paid: a shown-vs-applied, sitting inside the ruling's own rider. Fixed at
> both ends (`trust_change = marshal.trust.modify(trust_change)` at all seven
> responder arms; `interrupt_option_costs` returns `{}` for a sovereign
> holder, so no price reaches his button).
>
> **The dissent is recorded at the constant.** If 0 ever feels wrong, do NOT
> re-tune: re-open as *"charge once per ORDER, not once per ask"*.

**Filed September 6, 2026 by FA slice 16 (part b). The copy half of FA-52 is
BUILT; this is its mechanical half, and it needs a ruling, not a patch.**

A marshal under a standing order hears guns two provinces away and asks what
to do. The three buttons are priced like this:

| button | what happens to the order | trust |
|---|---|---|
| Investigate | the order is ABANDONED, he marches to the guns | **0** |
| Continue as Ordered | the order STANDS, he obeys | **−2** |
| Hold Position | the order is ABANDONED, he stands still | **−3** |

**Obeying is the second-most expensive thing the player can do, and the only
free option is the one that throws the order away.** The stated reason in the
source is "Non-literal acting literal" — a cautious marshal resents being
made to ignore a fight.

**Why this is a ruling and not a bug.** Slice 3 already decided the identical
question the other way, in the same file, for the same popup:
`_respond_combat_stalemate` prices `continue_order` at **0** with
`"order_cleared": False` and the same "Continue as Ordered" label. So the
game currently charges 2 trust for pressing a button that costs nothing when
a different interrupt raises it. One of the two is wrong and the build cannot
choose which.

**Measured reachability:** the ask fires for exactly three French marshals at
boot (Davout and Bernadotte, cautious; Napoleon, sovereign), every other turn
each, and the archived campaigns contain **19 organic asks** — so a player
who obeys a dozen times pays up to 24 trust for obedience. ⚠ Every archived
answer is `investigate`, because the playtest driver has no interrupt-policy
flag; the corpus proves the ASK's frequency and has never recorded a payment.

**Options.**

**(a) Follow slice 3 — obedience is free.** `continue_order` → 0, matching
its own sibling popup. The resentment then lives entirely in the ASK (he
still interrupts you, every other turn), which is where the drama is. This is
the recommended default: it makes the two popups agree, and it removes the
only case in the game where doing what you said costs more than changing your
mind.

**(b) Keep the tax and make it legible.** The price is now ON the button
(FA-49, landed in this slice), so a player who pays it has been told. Keep 2,
and let the asymmetry stand as characterisation.

**(c) Re-price the whole row.** Investigate is the one that abandons an order
and it is free; charge it instead. ⚠ This is the largest change and would
move a mechanic the AI never touches but the archived digests answer 19 times
out of 19 — it would make every archived run's behaviour more expensive
retroactively.

**Whichever is chosen, one line rides with it and is not in scope until then:
Napoleon is charged −2 trust, off 100, for continuing HIS OWN order.**

**Owner:** the next FA design gate. **Done when** the price on the button and
the price charged agree with the sibling popup, or the divergence is written
down at both seams as deliberate.

### FA-S16-D2 — the cannon-fire trigger is nation-blind

> ✅ **RULED AND BUILT September 6, 2026** as `_cannon_fire_concerns` behind
> `CANNON_FIRE_READS_THE_FLAGS`: he is asked about his own soil, a
> satellite's soil, and any battle with a court he is fighting or allied
> with — and nothing else. Landing record = the boxed block in
> `BUG_FIXES.md`.
>
> ⚠ **This row's own reproduction is not fixed by this row's own fix.**
> France boots at WAR with Russia, so the Blücher-vs-Hohenlohe case still
> ASKS under the predicate — correctly, we are fighting one of them. The
> genuinely third-party case on the shipped board is Prussia vs **Sweden**.
> ⚠ A participants-only reading would have silenced two neutrals fighting
> inside Holland, which is why a satellite's soil is its own arm.

**Filed with the above, same function, smaller.** `_check_interrupts` scans
`world.get_battles_within_range(marshal.location, 2)` and skips only battles
the marshal is himself IN — there is no nation filter anywhere. Measured: a
French marshal was interrupted, and charged, over **Blucher vs Hohenlohe**, a
Prussian pair neither of whose sides is France.

It is arguably correct that a marshal reacts to guns he can hear regardless
of whose they are. It is not arguably correct that he does so for a battle
France has no stake in, at a price, while under orders. **Owner:** the same
gate. **Done when** the trigger either states a nation predicate or the
docstring says why it has none.

## FA slice 17 Phase 3 — what the re-score routed rather than built

> Filed September 11, 2026 by the full re-score (memo of record `docs/audits/PLAYTEST_FULL_RESCORE_2026_09_11.md`). Each item is a design question the playtest raised and the phase deliberately did not answer; each names an owner.

| id | item | why it is a design question | proposed owner | disposition (September 12, 2026) |
|---|---|---|---|---|
| **FA-S17-D1** | **A Defense war purpose should tick once per WAR, not +1/turn per held home region per opposing court.** | FA-S17-5 clamped the war-level sum and scoped the claim to the court that holds the province, which stops a lost war being a paid one. But the underlying model is still "every lost province, every turn, forever, capped at 25" — a France losing its whole frontier accrues the same claim as one losing a single province nine times. The clamp is a bound, not a model. | `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` (the WPS-A ticking table) | ❌ **DECLINED — the premise is refuted by measurement.** Across 212 archived driver runs there are **178 defence objectives; 11 tick at all** (mean accumulated 0.81) and **3 reach the 25 cap — all three the same board on three repeats of one seed**. The saturation the row objects to occurs on roughly one board in seventy and is already bounded by FA-S17-5's clamp, while the per-province rate is the ONLY signal distinguishing a collapsing frontier from a single lost province; flattening it to once-per-war would delete that distinction to fix a 1.7% case. **Dissent recorded in full: if the model is wrong it is wrong in the direction the row says.** ⚠ **Re-open condition: a measured campaign in which the cap binds on a majority of at-war pairs.** Landing record = the boxed SLICE 17 (Phase 4) block in `BUG_FIXES.md`. |
| **FA-S17-D2** | **Peace is a money printer with nothing to buy.** | Every peace arm ends turn 40 holding 65k–113k gold while 10,000 infantry cost 150g; the EB-1 charges bound a WARRING treasury and nothing bounds a peaceful one. Measured across 11 accept/propose runs. | ~~EC-2 pass 2 (`ECONOMY_REVISIT_SPEC.md` Track 3 / ES-4 development)~~ **re-homed September 28, 2026** | ✅ **ANSWERED by its successors, September 28, 2026:** the peacetime sink is SR-5r's laws with upkeep (`REFORMS_SPEC.md`; T2 36.7% of a saving France's Net), and SR-5a's ruled balance ("Britain up, France trimmed") takes a quarter of France's homeland yield. ES-4, the owner this row named, was STRUCK the same day (`ECONOMY_REVISIT_SPEC.md` Track 3). The end-of-mandate re-score is the re-open condition. The record as it stood: ❌ **DECLINED to its named owner — EC-2 pass 2** (`ECONOMY_REVISIT_SPEC.md` Track 3 / ES-4 development), unchanged. A gold sink is an economy pass with its own blessed numbers and its own gate; building one inside an audit slice would move balance constants with no measurement behind them. The measurement stands as filed (every peace arm ends turn 40 holding 65k–113k gold while 10,000 infantry cost 150g, across 11 accept/propose runs) and is the evidence that pass inherits. |
| **FA-S17-D3** | **The peace that cannot hold.** | With the coalition threat sitting at a structural floor above the formation threshold, Britain re-declares the instant the 8-turn `PAIR_EXIT_TRUCE_FLOOR` expires on every seed, then offers terms three turns later — an eleven-turn war/peace metronome with no cause narrated. | a diplomacy gate beside WO-D8 | ✅ **NARRATION HALF BUILT September 12, 2026** · ❌ structural half declined to the diplomacy gate. A war declared ON US now names its cause (`dispatch.war_declaration_cause`, lever `THE_DECLARATION_NAMES_ITS_CAUSE`): AI-3's pin 4 — no unexplained war — was honoured for a war between two OTHER powers and not for a war on France, which read *"Britain and France are at war."* and stopped. Derived only, through a ladder the engine already records: a broken treaty → the declaring court's own active design → the largest grievance our own conduct fed into its alarm this turn, labelled through the diplomatic ledger's OWN source so the two surfaces cannot name one cause two ways. The **metronome itself** — the coalition threat floor that makes Britain re-declare the turn `PAIR_EXIT_TRUCE_FLOOR` lapses — is untouched and stays with the diplomacy gate beside WO-D8. |
| **FA-S17-D4** | **Deliver-time validation for the confrontation channel.** | 7 of 12 jealousy audiences resolved "The moment has passed" in the block they were delivered: the petition is built before the enemy phase and validated at answer time, with the battle-time resolution in between. ⚠ Re-measure with FA-S17-H1's petition key fixed before building. | `PETITION_POPUP_REVISIT_SPEC.md` B1 | ✅ **BUILT September 12, 2026, folded into FA-S17-12.** ONE liveness predicate (`jealousy.petition_is_still_live`) at the delivery chokepoint the slice-6 petition ride created; the answer-time guard that produced "The moment has passed" is untouched and still stands behind it. Re-measured on the FA-S17-H1-fixed instrument first, as the row required. `PETITION_POPUP_REVISIT_SPEC.md` B1 keeps the wider antechamber work. |
| **FA-S17-D5** | **The Peril needs a warning rung.** | FA-S17-7 stopped the Guard's toll from taking the Emperor off the field, but the Guard's dwindling ranks are still never named before the moment of capture — the Peril has a capture and no approach. | `NAPOLEON_SPEC.md` §7 (NP-4) + NPC-D1 | ✅ **BUILT September 12, 2026** (lever `THE_GUARD_COUNTS_ITS_ROADS`, with `GUARD_RUBBLE_FLOOR`). The Guard's last road is NAMED while the Emperor still has a choice, and the escape toll can no longer buy a road the Guard cannot pay — which is what had been taking him off the field silently (FA-S17-7's sibling). NP-4's approach now exists; NPC-D1's dimming-battle-row half stays with `NAPOLEON_SPEC.md` §7. |
| **FA-S17-D6** | **A COMMANDED driver arm.** | The scripted "fighting" France spends 9–22 of 160 AP over 40 turns and its script ends at loop 22–30, and the driver breaks every peace it signs (`force_declare_war_confirmation` answered with its first option, 9 of 10 runs). Until both are fixed, no balance condition can be measured on a France that is still being played — which is why the FA-D27 re-open reading needs a human. | `docs/PLAYTESTING.md` + `tools/playtest_scripts/` (a full-40 commanded script + a `force_declare_war` policy) | ✅ **BUILT AND MEASURED September 12, 2026 — and the measurement corrects Phase 3.** `tools/playtest_scripts/commanded_full40.json` runs forty loops spending all four military actions every turn (160 of 160 AP), and the driver gained `--declare-war` (default **cancel**) for the player's own declaration confirm — which was in no policy table, so it fell to the generic diplomacy block where "Proceed — break the treaty" matches no accept needle and the fallback took `options[0]`, i.e. Proceed. **Measured on three seeds: a commanded France ends turn 40 holding 20 / 24 / 22 of 28 provinces, so the FA-D27 re-open condition does NOT fire on a France that is still being played** (0 of 3, against 4 of 5 on the tyrant-accept arm whose script stops at loop 22–30). ⚠ **FOR USER CONFIRMATION** — this dates the re-open rather than retiring it; the ruling stands at (a). ⚠ Honest limit: four French marshals die between turns 30 and 37 on the historical seed, so the arm's last ten turns spend about half their orders on dead men — Fr@30 is the sounder read. `docs/PLAYTESTING.md` owns the dial. |
| **FA-S17-D7** | **Vassal drama exists only for a France that is losing.** | 0 rebellions or defections on 11 fighting-and-answering boards against 11 of 17 unattended ones. Decide whether loyalty should carry any tension for a competent Emperor. | the FA-D27 balance owner | ❌ **DECLINED to the FA-D27 balance owner (the user).** The measurement is not in dispute — 0 rebellions or defections on 11 fighting-and-answering boards against 11 of 17 unattended ones — but "should loyalty carry tension for a competent Emperor" is a balance intent, not a defect, and answering it means moving vassal drift or the grip coupling: blessed numbers with an owner. Filed unchanged for that owner. **Partially relieved by FA-S17-D8**, which makes the loyalty a competent Emperor DOES lose legible at the two bands where it costs him something. ✅ **CLOSED September 16, 2026 by row IQ-7 "The Satellites Have a Position"** (the owner the improvement queue named for it; `IMPROVEMENT_QUEUE_SPEC.md` §1.6). **The premise had flipped by then:** after IQ-3 a COMMANDED France is at peace from turn 5 to 29 and loses **2 / 3 / 3** of its satellites to the −2 drift by turns 30–33, so the drama had become a competent Emperor's failure mode too. Built: "The Client's Petition" — a loyal satellite petitions while it is still loyal, and the answer decides the web (GRANT holds 3 / 3 / 3 at turn 40, REFUSE 0 / 0 / 0; `docs/audits/IQ7_SATELLITES_2026_09_16.md`). |
| **FA-S17-D8** | **The rebellion warning arrives one tick before the rebellion.** | FA-S17-6 retires the stale question; it does not widen the window. Warn at the "wavering" band (latched once), or let the question mount over a letter. | `PETITION_POPUP_REVISIT_SPEC.md` F1 "The Antechamber" | ✅ **BUILT September 12, 2026** (lever `THE_TIER_CROSSING_IS_ANNOUNCED`) — **and the row's framing does not survive its own reproduction.** The modal fires at loyalty ≤ 10 and the rebellion at ≤ 0, so the ordinary −2 drift gives five turns of warning, and the passive unrest beat already covers 11–39: the warning is not one tick early. What is genuinely silent is the **CROSSING**. VS-4 gives loyalty military teeth at exactly 59 (a wavering satellite withholds its assimilated ex-marshals from musters and reinforcements) and at 34 (a disaffected one refuses the next call to arms outright), and no surface said either boundary had been passed — the per-tick line printed a number that moved by two while the contract underneath it changed. The beat is now the crossing, derived from the VS-4 constants so shown equals applied. ⚠ The first cut latched it on the vassal row and **VS-R's own guardrail caught that and was right to**; a crossing is a single-tick event, so this tick's own old and new loyalty fire each boundary exactly once with no store to go stale, and a satellite that recovers and falls again is announced again. |
| **FA-S17-D9** | **Retire or route `proposal_result_popup`.** | The backend stages it on every proposal outcome, the client's scene is an orphan, and CLAUDE.md's "Adding a new popup" row still tells builders to set it. | harness / doc hygiene | ✅ **RULED AND BUILT September 12, 2026 — RETIRE.** `proposal_result_popup.tscn`, its script, its `.uid` and its parse-harness row are DELETED: the scene was referenced by no `.gd`, no `.tscn` and no autoload, while the backend field already reaches the player twice — as the response's `proposal_result` and as a persistent `DIPLOMATIC_PROPOSAL_RESULT` rail notice. Routing it would have added a modal for information already on screen and re-opened the popup-drain family (IGR-X7) for nothing. The backend field is KEPT and documented as a legacy informational channel; `dialog_manager.gd`'s layer note and **CLAUDE.md's troubleshooting row — which told the next builder to set that field for a new dialogue type — are corrected**. |

---

## SF-CL-1 "The forecast keeps its word" — routed, not built (filed October 3, 2026)

| Row | Item | Recommendation | Owner |
|---|---|---|---|
| **SF-CL-1-D1** | **An attack from next door earns no coordination from the corps that answer it.** The resolver relocates every arriving reinforcer INTO the battle province and reads the lead's coordination context in HIS province (`_calculate_coordination_context(primary)` ← `primary.location`), so when Ney at Rhineland attacks Mack at Swabia, Davout, Lannes, Murat and the Emperor all march to Swabia and none of them is in Ney's context — no combined arms, no per-ally term, and Davout, who stood beside Ney, counts as gone. Only a lead who already stands on the field (the Emperor at Swabia) gets the +25%. Measured in SF-CL-1 while making the forecast mirror the resolver; the forecast now says exactly what the resolver does. | A mechanics question, not a forecast one: either the lead's context should be read on the FIELD (where the arrivals are) or the arrivals' coordination should be read in the lead's province — both move combat. The forecast must keep matching whichever is chosen (`_priced_coordination` is the one seam to update). | the next combat-mechanics row (IQ5-R1's owner) — a series re-record, flip-attributed Put to the user as `SCORE_FINISH_SPEC.md` §6 row 16 at Step 4's exit (Oct 3, 2026): "the next combat-mechanics row" named no slice once Step 4 closed. <br>**The user's ruling, October 3, 2026** (`SCORE_FINISH_SPEC.md` §6 row 16, recorded by Step 5's session): **read the lead's coordination context on the FIELD**, the battle province where the arriving corps stand. **The build is Step 7's slot and stays open here:** `_calculate_coordination_context` reads the battle province; `_priced_coordination` follows in lockstep; ONE `BASELINE_SERIES` re-record, flip-attributed; the M1–M7 harness re-read. Completion: Ney at Rhineland on Mack at Swabia counts the corps that answer at Swabia, the muster preview prices the same figure, and the re-record names the coordination read as its sole mover. ⟨SF step=7 · §6 row 16 (ruled by the user; built in Step 7's slot, before SF-R) · pillar=combat_legibility⟩ <br>✅ **BUILT October 4, 2026** (Score Finish Step 7 slice 3, alone in its own commit; landing record `SCORE_FINISH_SPEC.md` §3 Step 7, rules `SYSTEMS_REFERENCE.md` §93.3, pins `tests/test_sf_cl1_d1_the_coordination_is_read_on_the_field.py`): the completion met — Ney at Rhineland on Mack at Swabia counts Davout, Lannes and the Emperor on the field; the muster's ceiling equals the massed strength whenever every promised corps fights, with and without a gun corps; the re-record names the field read (`combat_executor.THE_COORDINATION_IS_READ_ON_THE_FIELD`) as its mover, and the gate's lockstep (`THE_GATE_READS_THE_PREVIEWS_CONTEXT`, SF7-X4) is inert alone. The cavalry charge and the garrison assault keep the lead's province (neither rolls reinforcements — FOR USER CONFIRMATION, landing record). |

## SF-NAV-1 "The strangulation, played" — the user's question (filed October 4, 2026; `SCORE_FINISH_SPEC.md` §6 row 17; **CLOSED October 5, 2026** — confirmed with A2 re-anchored, §6.7)

| Row | Item | Recommendation | Owner |
|---|---|---|---|
| **SF-NAV-1-D1** | **The Continental System cannot outlast Spain's exit — the A2 anchor.** Played on three seeds (`docs/audits/SF_NAV1_STRANGULATION_2026_10_04.md`): SHUT OUT held for 1–3 turns on two (historical turn 11; marengo 13–15) and never for a sitting's 8; tier 2 (16 of 26) never reached (peak 14). Spain's war with Britain ends on turn 16 on every seed (the exhausted-pair exit), the British bench keeps a corps ashore until turns 12–17, and the Tilsit lever (a peace that enrols the beaten court) is settlement-tier, unsealable while Britain fights on in the same war. Britain sues on turn 8 on every seed from her own war's exhaustion. | **(a) The Tilsit clause on a separate peace** ("joins the Continental System", no forced alliance, priced at today's CS surcharge, on a beaten court) — the historical mechanism and the only option that changes no AI's war behaviour; rejected (b) binding a hegemon's ally to the war, (c) counting an ally's ports at peace, (d) keeping the rule and re-anchoring A2 to tier 1. Full arguments on §6 row 17. | **the user** — `SCORE_FINISH_SPEC.md` §6 row 17; built in Step 7's slot, before SF-R. Done-when: the ruling's re-read on the benchmark's `NAV1-H/A/M` — SHUT OUT held through a sitting, or tier 2 reached (options a–c) — or A2 re-anchored in `NAVAL_SPEC.md` §5.1 (option d); test: `tests/test_sf_nav1_the_strangulation_played.py` gains the ruling's pin; STATUS line: Step 7's.<br>**The ruling, October 4, 2026, under the user's delegation (Step 7; FOR USER CONFIRMATION; gate record `SCORE_FINISH_SPEC.md` §6.6, authoritative):** option **(a), the Tilsit clause on a separate peace**, plus the System's missing exit (a member at war with France leaves it, as a named beat) and A2 re-anchored to *SHUT OUT held for 8 consecutive turns on a played road, on ≥ 2 of 3 seeds — Britain sues from her own war, the System is the squeeze*. The research (memo `docs/audits/SF_NAV1_D1_THE_A2_ANCHOR_2026_10_04.md`): the conquest road the Step 6 arm never tried, played on the three seeds — Vienna not taken on any seed, Hanover lost to Prussia on two, peaks 10–13 of 26, SHUT OUT held at most 3 turns and never after Spain's exit; the record hand-played board reads 9 of 26; after Spain's exit the 50% line wants all eight capitals at once with no margin. **The build stays open here:** Step 7's row-17 slice (the clause, ONE membership write, the honest-availability predicate, the price in both harshness dialects, the separate peace carrying it, the exit at `set_diplomatic_state`, A2's new wording); done-when = an arm holding SHUT OUT 8 consecutive turns on ≥ 2 of 3 seeds, the record naming the road(s); test `tests/test_sf_nav1_d1_the_tilsit_clause.py`.<br>**Built October 4, 2026 (Step 7 slice 4; landing addendum `SCORE_FINISH_SPEC.md` §6.6) — the done-when is NOT met (1 of 3 seeds), so the row stays OPEN with the user:** the Tilsit road (`tools/playtest_scripts/sf_nav1_tilsit_road.json` (benchmark `NAV1T-H/A/M`)) holds SHUT OUT 17 consecutive turns on historical (peak 16, tier 2 for the first time) and never on austerlitz or marengo (peak 16 on both): the next coalition draws a signatory back to war 5–9 turns after the separate peaces and the exit takes its ports; on austerlitz British corps stay ashore all game behind Austria's closed frontier in France (SF7-X7). The 50% line is not tuned. Open question: may a court that keeps the System by treaty be drawn into the next coalition while its peace is young (today: after the pair floor), or does A2 read 1 of 3 as enough?<br>**CLOSED October 5, 2026 — CONFIRMED under the user's delegation (gate record `SCORE_FINISH_SPEC.md` §6.7 item 4):** the clause confirmed as built (`continental_system_join`); **A2 re-anchored to what play measures:** *a played road holds SHUT OUT for a sitting (8 consecutive turns) on at least one benchmark seed, and the record names what breaks it on the others* (`NAVAL_SPEC.md` §7, A2). The 50% line and the clause's +10 alarm are not tuned: seeds are roads, not laws; both failure modes are counterplay a player can answer (the alarm after the peaces; the corps on the Continent the Congress price already names); and buying the second seed by cheapening the clause's alarm would make the System cheaper than its politics. **Re-open:** a reading in which no seed holds, or the user wants the System to decide the war. ⟨SF step=7 · row 17 · pillar=naval⟩ |

## SF-LB-2 "The Defenceless Prize" — the user's question (filed October 3, 2026; ✅ RULED + BUILT the same day as SF-LB-2b, and its remainder (§6 row 15) BUILT as SF-LB-2c "The patient ask" — the variance clause MET; the row below is struck; its remainder was `SCORE_FINISH_SPEC.md` §6 row 15)

| Row | Item | Recommendation | Owner |
|---|---|---|---|
| ~~**SF-LB-2-D1**~~ ✅ **BUILT October 3, 2026 as SF-LB-2b "The Chest the Council Can Spend"** (`SCORE_FINISH_SPEC.md` §6 row 14 RULED the same day; landing record §6.4's second addendum; rules `SYSTEMS_REFERENCE.md` §85.8) — **and the clause is still NOT MET** (first openings {5 ×6, 9}: the recommendation's "the ladder varies 3–8" was wrong by measurement); the remainder and the live recommendation are `SCORE_FINISH_SPEC.md` §6 row 15, the user's. | **The crisis turn does not vary across the seeds.** §6.4's acceptance asks the opening to span ≥ 3 turns across the seeds; measured, Prussia's crisis on Hanover opens on turn 9 on six seeds and 10 on marengo. The ladder climbs on turns 3–8 seed by seed, but `process_war_council` runs BEFORE the turn's income and reads `penniless` (the chest under `AI_WAR_TREASURY_FLOOR` 500 after the admin phase's spending) until Prussia's economy — unseeded, Tier 1 by D7 — clears the floor on the same turn everywhere. The ruling said not to tune when every seed gives the same turn. | **Read the chest the council can spend:** the turn's income forecast as the ledger quotes it (IQ1-5-1's tick-staleness family, one seam at `_restraint_block_reason`'s `penniless` read for the OPENING only; the declaration keeps the live chest). The opening then falls to the ladder's own turn, which already varies 3–8. Rejected: seeding the treasury (D7 fixes it Tier 1), lowering the floor (a tune). | the user (`SCORE_FINISH_SPEC.md` §6 row 14); the xfail `TestTheDrivenBoard::test_the_crisis_turn_varies_across_seeds` flips the day it is met ⟨SF step=4 · SF-LB-2 · pillar=living_balance⟩ |

## UXR — the adjustability review's design rows (filed October 9, 2026; memo `docs/audits/UXR_ADJUSTABILITY_REVIEW_2026_10_09.md` §4, decision 6; nothing here is built in S1)

| Row | Item | Recommendation | Owner |
|---|---|---|---|
| **UXR-D1** | **Text size apart from Interface Scale.** On an ultra-wide the panels have room and the type is the problem; one global scale enlarges the chrome with the text. | A second slider *Text size* scaling the theme's named sizes only (Body/Caption/Heading). Needs UXR-2's override diet first — the raw overrides that survive at ≥ 15 ignore the theme — so it cannot land honestly in S1. ≈ 0.3. | UXR-2 (Pre-Deploy S9); done-when: the slider moves every text node the census sees and no panel rect; test: the census at text-size 1.5 / scale 1.0 reads 0 RED on the five named surfaces ⟨SF step=pre-deploy S9 · UXR-2 · pillar=ui_ux⟩ |
| **UXR-D2** | **Dim type.** The grey-on-navy `UI_TEXT_DIM` hint style (now Caption 14) is the second killer after size. | A *High contrast* toggle raising the dim text classes one step (`Utils.UI_TEXT_DIM` → a brighter token), measured off the frames (UXR-3's R3 contrast item). ≈ 0.2. | UXR-2 / UXR-3 ⟨SF step=pre-deploy S9 · UXR-2 · pillar=ui_ux⟩ |
| **UXR-D3** | **The HUD spreads to the corners of a 49-inch panel.** Terminal bottom-left, war HUD bottom-right, the top bar's counters and nav at opposite edges: 4,300–5,000 px apart at 5120 wide. | *HUD width: Full · Centred* — confine the terminal, rail, top bar and war panel to a central band (≈ 2560 logical) with the map still full-bleed; the layout law's natural second rule. A **⌂ Fit Europe** button beside the map's zoom rides with it (today only the `Home` key recentres). ≈ 0.4. | UXR-2 ⟨SF step=pre-deploy S9 · UXR-2 · pillar=ui_ux⟩ |
| **UXR-D4** | **"The Side Desk."** Every ledger is a full-screen modal; a 32:9 player has room to keep the Strategic / Diplomatic Ledger or the Generals screen open on the right third while commanding on the left. | A second placement mode for the layer-50 screens (a NON-modal dock at a third of the width) + a 📌 pin on each header; the screens already render into a panel, so the change is placement + modality, not content. The one feature a 32:9 player would name first. ≈ 1.0. | its own gate after UXR-2 (the user rules on modality); done-when: a pinned ledger survives a command, a popup and an end turn beside a live map ⟨SF step=pre-deploy S9 · UXR-2 · pillar=ui_ux⟩ |
| **UXR-D5** | **Only the terminal remembers.** The war HUD's edge-drag is invisible (no cursor) and forgotten on every `update_wars`; no other screen resizes. | The war HUD gets a visible grip persisted like the terminal's (`get/set_panel_size(name)`); the five big screens get grips — UXR-2's own row 1. ≈ 0.1. | UXR-2 ⟨SF step=pre-deploy S9 · UXR-2 · pillar=ui_ux⟩ |

## Source Documents (Archived Reference)

| Document | Items Moved Here |
|----------|-----------------|
| `docs/DIPLO_REFINEMENT.md` | Wave 3-5 open items, all R-IDs |
| `docs/DIPLOMACY_DESIGN_FIXES.md` | Design discussion items, N1/A3/A4 AI fixes |
| `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` | War Objectives, Ticking War Score, Vassalage Power Cap, Forced Alliance, Liberation (lines 215-722) |
| `docs/JEALOUSY_SPEC.md` | Jealousy pointer (spec kept as-is) |
