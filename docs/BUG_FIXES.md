# Bug Fixes

> **Archives (October 9, 2026, CODE-4):** sections closed before the current quarter live in `docs/archive/BUG_FIXES_2026_Q3.md`, read by the census tools and the test pins exactly as if they were still here. OPEN and PARTIAL rows never move.

> Broken-now implementation document.
> Treat the current findings as frozen truth until the open items below are fixed.
>
> Last Updated: **September 28, 2026 — the Score Finish census**
> (`docs/SCORE_FINISH_SPEC.md` §1).
> - **The ledger, counted.** `tools/defect_census.py` counts every row in this
>   file and in `DESIGN_REFINEMENT.md`. Six read-only agents then verified each
>   open row at `c20d5bba`.
> - **99 live defect rows**, each with a slice in the spec's build order.
> - **Stale rows:** 29 defect rows and 45 design rows are fixed but never
>   struck. Step 0's SF-0 marks them, with their evidence.
> - **Four new rows** are filed below as §Score Finish Verification, SF-V1 …
>   SF-V4. The first, SF-V1, is an AI treaty offer its own ratification
>   refuses.
>
> Previously: **September 28, 2026 — the Full Play Retest** filed 29 rows
> (§Full Play Retest below, memo `docs/audits/PLAYTEST_FULL_RESCORE_2026_09_28.md`):
> a 28-turn hand-played campaign summoned the Congress of Paris for the first time
> (47 of 45 titled, turn 24) and watched it dissolve on day 3. Two P1s:
> RS-1 (a fresh peace re-broken by an ally's cascade) and RS-2 (the War of the
> Congress unsigns a refusing ceder's titles). They jump the queue as "The peace holds".
>
> Previously: **September 25, 2026 (evening) — the Creative AAR playtest**
> filed 32 rows (§Creative AAR Playtest below, memo
> `docs/audits/PLAYTEST_CREATIVE_AAR_2026_09_25.md`): eighteen turns played
> by hand at the command line; the P1 is a lord's separate peace that leaves
> its vassal at war with no army (AAR-1 — Austria ate the Kingdom of Italy
> under the French peace). Nothing built; NEXT stays Update 1.
>
> Previously: **September 14, 2026 — IQ-2 "The Collapse Is Legible"**
> landed; see §Collapse Legibility (IQ-2) below, which is authoritative.
> A landless France fell off the roster and fielded a FREE army while every
> surface narrated an ordinary campaign; she is now billed and every surface
> names the collapse — none ends the campaign.
>
> Previously: **August 30, 2026 — the whole-systems review (row REV):**
> a 14-finder / 2-refuter-per-finding fleet at `e206869` confirmed 45 defects
> across every system and all 45 are fixed; see §Whole-Systems Review below,
> which is authoritative. One PRE-EXISTING harness defect is filed there
> A live VISUAL PASS then signed the client fixes off on screen and found one
> more defect the tests could not see — REV-V1, a key the review itself read
> without copying, so the end-turn lapse gate saw 0 forever. The harness row
> named REV-X1 — the AI-V control arm's cold-cache non-determinism — was
> then ROOT-CAUSED AND FIXED the same day: the harness drained the event log
> by `id()`, which is unique only among LIVE objects, so a recycled address
> silently dropped a genuinely new event from the digest. The game is
> deterministic; the instrument was not. The first pass's hypothesis blamed
> the AI path and is corrected on the record.
>
> Previously: **August 23, 2026 — the four live-report defects (row UX23).**
> Landing record = §Live UX Report (Aug 23, 2026) below, authoritative.
> Four user reports from a live turn-3 France/1805 campaign, all fixed:
> the 38.6-second envoy sound; the end-turn soft-lock (THREE stacked faults,
> the load-bearing one being that the typed `end turn` route could never
> confirm the lapse it was told to confirm); the reward rail that asked to be
> paid and then went on asking; and Bernadotte's counter-punch, which was
> unusable at 0 AP — the only state in which "free" means anything.
> `tests/test_ux_fixes_2026_08_23.py` (54) + `tests/test_counter_punch_ap_gate.py`
> (21); **45 mutations swept over two rounds, 45 killed — thirteen pins were
> INERT on first sweep and were repaired**, plus one pre-existing pin proven
> inert and corrected. Suite 18,718 passed / 3 skipped. M1–M7 and
> `BASELINE_SERIES` byte-identical, no re-record.
>
> A 13-agent review round at `4b09e59` then found **26 more defects,
> including a P1 this slice itself introduced** (the counter-punch waiver
> also disabled the 2-AP gate for `pursue`). All fixed; see §Review round.
>
> Last Updated: August 21, 2026, third entry (**WO slice 7 "The Cabinet Is
> The Only Door" LANDED — the G1 ruling**: typed diplomacy is redirected in
> character on the terminal path (nothing sent, nothing spent) and the
> wizard is completed enough to be the only door. **WO-4 and WO-5 are
> CLOSED BY RULING** — the typed dead-ends are retired, not repaired.
> Landing record = `WEIRD_OUTCOMES_SPEC.md` §3 slice 7.)
>
> Last Updated: August 21, 2026, second entry (**WO-17 "The Trojan Corridor"
> FIXED — WO slice 13**: the WIN-D3 evacuation grant gains its direction term
> at the ONE `can_enter_territory` arm; a corps that can already reach the
> body of its own realm has no claim on the corridor. Landing record =
> `WEIRD_OUTCOMES_SPEC.md` §3 slice 13; the five WIN-D3 §3.4 pins
> byte-identical; `BASELINE_SERIES` byte-identical by real subprocess run.)
>
> Last Updated: August 21, 2026 (**WO section EXTENDED — rows WO-17..WO-32 from
> the spec-authoring session's defect hunt, incl. three hand-verified new P1s:
> **Slice 16 landed August 21, 2026: WO-21 and WO-23 FIXED, plus WO-37
> found in passing. WO-21's filed MECHANISM was wrong (the named bail is
> unreachable) and its stated consequence was refuted; the landing record
> says which and why.**
> **Slice 15 landed August 21, 2026: WO-22/26/27/29/30 FIXED, plus WO-34
> found in passing; WO-35/WO-36 newly filed by its census. Two of the five
> filed FIXES were wrong as written and the landing record says which and
> why (`WEIRD_OUTCOMES_SPEC.md` §3 slice 15).**
> WO-17 the direction-less WIN-D3 evacuation corridor, WO-21 the objection
> channel's free-trust + dead cancel arm, WO-22 auto-end-turn crossing an
> unanswered capture — plus WO-32 (P1, owned by PC15-10). Build contract for
> the whole WO row = `docs/WEIRD_OUTCOMES_SPEC.md`.**) Prior: August 16, 2026
> (**Weird-Outcomes Playtest (WO) section added — 16
> game rows + 3 harness rows, ALL OPEN** (report-only session): 3 game P1s ⛔ — the
> enemy-name addressee executing on your own army, the parser rewriting an unknown
> place into a real one and marching there, and a detachment garrison that can
> never fall — plus a harness P1 that reports campaigns which never happened.
> Verified by a 40-agent find-then-refute fleet: 21 CONFIRMED, 5 REFUTED, 4
> ALREADY_FILED. Memo: `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md`.)
>
> Last Updated: August 15, 2026 (**Comprehensive Playtest PC15 section added — 18
> game rows + 1 harness row, ALL OPEN** (report-only session): 4 P1 ⛔ Round-0
> gates (silent marshal destruction · the interrupt route swallowing addressed
> commands · the settlement confirm wedge · dead-name silent substitution), the
> neutral-soil family, and the measured petition-firehose number for CA9-D3.
> Memo: `docs/audits/PLAYTEST_COMPREHENSIVE_2026_08_15.md`.)
>
> Last Updated: August 1, 2026, second session (**Live-Playthrough Aug-1 section CLOSED**
> — the 2 routed rows PT-F1 + PT-F6 FIXED under the user's delegated grant, alongside the
> four PT-D design items; the section's 10 defects are now 10/10 FIXED. This session's
> tests: `test_neutral_soil_pursuit_capture.py` (7), `test_ai_square_thrash.py` (6),
> `test_enemy_phase_presentation.py` (13), diorama/digest extensions. Prior session:
> 8 FIXED with pins (`tests/test_playthrough_fixes_2026_08_01.py`, 12). Record:
> `docs/audits/AI_V_SWEEP_2026_08_01.md` §10 + `docs/STATUS.md` top entry.)
>
> Last Updated: July 18, 2026 (**July-18 Playtest Sweep section added — ALL 25 rows FIXED**:
> the two user-reported issues ("give them hell" did nothing; the settle-a-war window ran off
> the screen) plus their families, found by a 34-agent find→verify workflow and hardened by a
> 50-agent pre-commit review that caught a P1 regression before it shipped. Record:
> `docs/STATUS.md` top entry.)
>
> Last Updated: July 17, 2026 (**EC-W Review Findings section added** — 2 routed OPEN
> rows from the Econ War-Coupling pre-push find→verify review; the review's other 7
> confirmed findings were FIXED in-session before the commit, memo
> `docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md` §6.)
>
> Last Updated: July 16, 2026 (**Sweep-5 Findings section added** — the P0 end-turn 500
> FIXED in-session; 5 routed OPEN rows from the Combat Overhaul Sweep-5 12-component
> review, memo `docs/audits/SWEEP_5_2026_07_16.md`.)
>
> Last Updated: July 14, 2026 (**Vassal Playtest Findings — F1/F1c/F3/F6/F8b/C1/C2/F5/F7/F4 ALL FIXED** this session from a live europe_1805 playtest + 14-agent adversarial verification; memo `docs/audits/VASSAL_PLAYTEST_2026_07_14.md`, tests `tests/test_playtest_fixes_2026_07_14.py`. Prior: July 12, 2026 (**Playtest Sweep PS-1..PS-9 — 3 user-reported issues + same-family sweep + the generosity-inversion fix (PS-9: "More generous" lowered a hawk's acceptance); ALL FIXED + verified, suite 12,964/3, Godot parse-clean**). Prior: July 11, 2026 (**Estate-Second-Pass Eval Findings section added** — ESP-EV-1 muster typed-answer misroute + ESP-EV-2 expectation-note under-fire FIXED in-session; ESP-EV-3 battles_won seam inconsistency + ESP-EV-4 attack-region silent redirect ROUTED to 8.EVAL. Prior: **MC-V Enemy-AI Personality Findings section added** — 5 ROUTED items from the Marshal Content Pass MC-V assurance/eval slice, headline MC-V-2 = enemy literal AI aliased to cautious, a design decision owned by the MC exit review / Jealousy gate; none is a forced fix. Prior: the **Creative-Audit Findings section** — 10 correctness defects (ALL FIXED across Wave 6 W6-0/W6-1). Earlier state: CR-0 parser roster pinning + **EC-0 advance-turn AP reset** + **MC-0 marshal-overview ability display** all FIXED. Historical context: the April 12, 2026 renderer notes below predate the July 2, 2026 real-map cutover — the running game is the 126-province 1805 campaign; Session-8 renderer work is COMPLETE.)

---


## The Economy Gate — found building, October 5, 2026 (**8 rows — EG-X1, EG-X2, EG-I1, EG-I2, EG-I3 FIXED in the gate; EG-X3, EG-X4, EG-X5 OPEN, owned** — found once the gate's rulings changed the board: NPC-12's driven name census and the front page's driven arms went red, and the gate's own reading flipped items; each failure was traced to its cause, and every flip attributed by lever-down arms (`tools/_econ_gate_exit_attribution.py`), before anything was re-seated; gate record `SCORE_FINISH_SPEC.md` §6.8; rules `SYSTEMS_REFERENCE.md` §98.9–§98.11; pins `tests/test_economy_gate_2026_10_05.py`; sweep `tools/_sweep_econ_gate.json`; design rows `DESIGN_REFINEMENT.md` EG-D1 … EG-D3)

| Row | Pri | Finding | Status |
|---|---|---|---|
| **EG-X1** | P3 | **A standing order's target printed as its key.** Once the lawful road sent a French marshal after Archduke Charles on the commanded arm, six surfaces printed "ArchdukeCharles": the ledger's order line ("Pursue ArchdukeCharles (tracking)", 16 reads in 12 turns), the campaign log's order line, the dispatch's status note on POST and GET, and the march report's pursuit line on the command response and in the strategic reports. A latent defect: any pursuit of either archduke showed it; the board had never reached one inside the census's window. | ✅ FIXED October 5, 2026: ONE display form, `display_names.order_target_display` (lever `THE_ORDER_NAMES_ITS_TARGET`), at the ledger line, the dispatch note, the campaign log line and every player-facing march report in `strategic.py`, `relay.py` and `marshal_voice.py` (13 + 2 + 1 lines; the console debug print stays raw). The driven census reads PASS again. Pins `TestTheOrderNamesItsTarget`, including a census of the three march files. |
| **EG-X2** | P3 | **The league's news was crowded off the page by a busy morning.** On the gate's CMD-M arm a war ending and a truce signed took both sub-beat slots on turns 11 and 12, so "St Petersburg now pays Vienna 400 gold a turn against us" and "London now pays St Petersburg 400 …" never reached the page on the morning they were fresh. Living balance C5 read ✗, two sponsorships missed. | ✅ FIXED October 5, 2026: a fresh `league_paid` or `league_joins` candidate not already on the page rides beneath the lead, at most one line of each class — SF-NAR-1's standing-line idiom (`dispatch.THE_LEAGUES_NEWS_RIDES_BENEATH`). Display only. Pins `TestTheLeaguesNewsRidesBeneath`. |
| **EG-I1** | instrument | **Living balance C5 judged a late log row on the wrong morning.** The driver recorded the turn-24 grant (`log_turn` 24) again in turn 34's group, and the reader judged it against turn 34's page and reported it "missed", though turn 24's page had led with it ("London now pays St Petersburg 500 gold a turn against us"). | ✅ FIXED October 5, 2026: a row is judged on the page of its own morning (group `log_turn` − 1) and counted once (`_score_probes.THE_C5_READER_JUDGES_A_ROW_ON_ITS_OWN_MORNING`). Pins `TestTheC5ReaderJudgesRowsOnTheirOwnMorning`. |
| **EG-I2** | instrument | **Living balance C5 looked back one table-less morning.** On the gate's CMD-A arm the old league stood for two mornings (no table recorded), and the page told "Prussia would now join a league against us" on the first of them; EA-16's rule read only the second and reported Prussia "missed". | ✅ FIXED October 5, 2026: the news counts on any page of the run of table-less mornings before the table — EA-16's rule widened, riding on EA-16's lever too (`THE_C5_READER_KNOWS_A_RUN_OF_TABLELESS_MORNINGS`). Pins `TestTheC5ReaderKnowsARunOfTablelessMornings`. |
| **EG-I3** | instrument | **The descent arm's staging fell 18 gold short.** With campaign pay (EAD-1) Bernadotte's corps at Franconia costs 204 a turn from the boot; the DESC arm's turn-4 commission met "Commissioning Oudinot costs 3,500g — the treasury holds 3,482g", the landing line was answered "There is no Marshal 'Oudinot'" (the driver's clarification policy then sent Soult), Munster never fell, and the driver did not flag a precondition — naval C3 read ✗ for the staging, not the navy. | ✅ FIXED October 5, 2026: the commission moves to turn 5 and the landing to turn 6 (SF-V6's precedent; the camp, blockade and diversion keep their turns; `naval_descent.json` `_note_eg_i3`); the driver's expedition tracker counts an `unknown_name` clarification as a line that never ran (`playtest_driver.THE_TRACKER_KNOWS_AN_UNKNOWN_NAME`). Re-run: Oudinot commissioned, the expedition quoted at 64 in 100, Munster secured; naval C3 ✓. Pins `TestTheTrackerKnowsAnUnknownName`; `test_fa_slice17_f…`'s commission pin re-seated 4 → 5. |
| **EG-X3** | P3 | **A lost satellite can be crowded off the page.** On the gate's CMD-H arm the Kingdom of Italy, our satellite, is eliminated on world turn 6 (`nation_eliminated`, lord France) and that morning's page never names it: the lead is Teulie's capture (95) and the two sub-beats Ney's reversal (91) and Massena broken (90), so `vassal_lost` (84) has no slot. Narration C6 (the delegate's EYES sample) reads 9 of 10 for it. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9): a satellite's fall rides beneath the lead like the league's news (EG-X2) or the standing line, behind a lever; done when the CMD-H turn-6 page names the Kingdom of Italy and its pin flips with its lever. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **EG-X4** | P3 | **A morning intel row and the store's last sighting disagree.** On the gate's CMD-M arm at turn 20 the dispatch's row places Kutuzov at Vienna (a turn-17 snapshot, marked stale) while `get_last_known_location` returns Bohemia; Kutuzov in fact stands at Vienna. Either the row should read the newest sighting (AAR-5's rule) or the store's last sighting is the stale one — not yet traced. Narration C4 reads ✗ for it; it needs the gate's road and campaign pay together (either lever down reads ✓). | OPEN — owned by SF-RR6 "the instrument reads what the player sees" (§3 Step 9): trace which store is stale on the CMD-M t20 save, fix the dispatch builder or the probe's reference behind a lever; done when narration C4 reads ✓ on the gate's CMD arms with the cause recorded. ⟨SF step=9 · SF-RR6 · pillar=narration⟩ |
| **EG-X5** | P3 | **A capital whose works were just emptied falls with no word of them.** On the gate's CMD-H arm Austria takes Munich from Bavaria on turn 6 (the capture clears the loser's garrison) and Lannes's field win at Munich the same turn takes the capital; the report names no garrison and no fight for its works. Combat legibility C3 reads ✗ (the road's board — with the lawful road down no capital falls after a field battle on the arms). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9): the capture report states an empty garrison ("its works stood empty — Austria's capture had cleared them") or RS-3's halt applies, behind a lever; done when combat legibility C3 reads ✓ on the gate's CMD-H arm. ⟨SF step=9 · SF-RR4 · pillar=combat_legibility⟩ |

## The Economy Audit — filed October 5, 2026 (**28 rows: EA-1 … EA-19 and EA-E1 … EA-E9 — EA-1, EA-3 … EA-6 and EA-8 … EA-18 FIXED in the audit (with SFR-D23 and SFR-D39 above); EA-7, EA-19 and EA-E8 RULED / FIXED in the economy gate the same day (`SCORE_FINISH_SPEC.md` §6.8); EA-2 and EA-E1 … EA-E7, EA-E9 OPEN, owned (the client and the instrument)** — the user's *"make these decisions, and do full audit of economy to make sure it works well, is engaging and isn't too easy"*; memo `docs/audits/ECONOMY_AUDIT_2026_10_05.md`; rules `SYSTEMS_REFERENCE.md` §97; pins `tests/test_economy_audit_2026_10_05.py`; the series attribution `tools/_econ_audit_series_arms.py`, the reading's `tools/_econ_audit_exit_attribution.py`; gate record `SCORE_FINISH_SPEC.md` §6.7; design rows `DESIGN_REFINEMENT.md` §The Economy Audit EAD-1 … EAD-8)

| Row | Pri | Finding | Status |
|---|---|---|---|
| **EA-1** | P2 | **Every recurring transfer between courts was off the books.** A sponsorship (SFR-D39, IQ1-3a′), the paymaster's war subsidy and London's Congress subsidy moved gold every turn on both chests and appeared on neither Net: the player's sponsor chip moved the projected Net by 0 while the chest fell 200 a turn, and every AI purse test read a Britain whose Net was positive while its chest fell (8 of 9 late turns of the commanded arm, investigator A's tracer). A short payment was silent (N8). | ✅ FIXED October 5, 2026: ONE signed "Subsidies" Net line on both sides, the applied-transfer idiom, each engine's own planner for the projection; "paid N of M" on a short term (`instruments.THE_SUBSIDIES_ARE_ON_THE_BOOKS`; §97.1). |
| **EA-2** | P3 | **Economy F1 cannot see an off-books flow.** The driver's `net_residual` is the ledger's Net minus the sum of the ledger's own components — zero by construction; it never reads a treasury, so 12 of 12 records read 0 on the sponsorship arm while France lost 200 a turn outside the books (investigator A, N7). | OPEN — owned by SF-RR6 "the instrument reads what the player sees" (§3 Step 9): compare the measured chest change across the end turn, less the Butcher's Bill and the one-shot purchases, with the applied Net; done when its pin flips with its lever and the economy arms re-read clean. ⟨SF step=9 · SF-RR6 · pillar=economy⟩ |
| **EA-3** | P3 | **Trade depended on whether a pair had ever fought.** A PEACE written by a war's end traded 50 while the 175 unwritten boot pairs traded nothing (N5); an eliminated court kept trading — the dead Kingdom of Italy earned +87 a turn and France and Austria +12 from it (N4). | ✅ FIXED October 5, 2026: a PEACE earns no trade, written or not; a court that no longer stands trades with nobody; `calculate_trade_breakdown` the one per-partner source (§97.2). |
| **EA-4** | P3 | **The Continental System charged trade nobody earned.** Each member and Britain lost `min(75, the state's face trade)` on no Net line — a satellite (which trades with nobody) paid 50 or 25 a turn, Britain the 200 cap (N6, staged). | ✅ FIXED October 5, 2026: the closure takes the trade a member actually earns from Britain, on a "Continental System" Net line (§97.3). |
| **EA-5** | P3 | **A vassal's Net omitted the tribute it paid** — Holland's projected Net +426 with a tribute line of 0 while it paid 337 (N2). | ✅ FIXED October 5, 2026 (§97.4). |
| **EA-6** | P3 | **A serving contingent's men were billed to nobody** — Dumonceau's 6,500 and Teulie's 5,447, ~88 a turn, while the levy's refusal told the player Holland "raises and pays them" (N3). | ✅ FIXED October 5, 2026: the satellite pays (§97.4). |
| **EA-7** | P4 | **A court with no marshal never runs an admin phase** — no +25 a turn per unused action and no purchase, so nine courts' chests (Portugal, Saxony, Hanover, Hesse, the Papal States, Sardinia, Holland, the Kingdom of Italy, Switzerland) only ever grow (N9). | ✅ RULED October 5, 2026 in the economy gate (§6.8, EAD-6): the marshal-less courts stay inert by design (no bench, nothing to buy that would matter; an admin phase measured as growing the hoard and reshaping the board); the one real defect inside the skip FIXED — a court left with no general runs the Marshalate's commission rung alone (`EnemyAI.execute_commission_only`, lever `enemy_ai.A_COURT_WITHOUT_A_GENERAL_MAY_COMMISSION`; §98.7; pins `tests/test_economy_gate_2026_10_05.py::TestACourtWithoutAGeneralMayCommission`). |
| **EA-8** | P2 | **Exploit: a chest just below zero bought halved upkeep forever.** The first deficit turn halves upkeep, the halved bill leaves the chest solvent, one solvent turn resets the count — a greedy spender alternated just under zero from turn 30 to 38 (upkeep 3,190 → 1,642, 3,454 → 1,846 …), grew to 224,000 men and never saw a deserter (investigator B). | ✅ FIXED October 5, 2026: the army remembers its arrears; three deficits in a row desert as always, and so does a deficit every other turn at the fourth (§97.6). |
| **EA-9** | P3 | **A market did not pay.** After its tier upkeep a market netted +7 a turn on every French city slot (+15 at Paris) — a 50-turn payback a 40-turn campaign never repays — since SR-5a's trim made a French city earn 110. | ✅ FIXED October 5, 2026: a market keeps itself (+27 on a French city, +56 at Paris; §97.7). |
| **EA-10** | P3 | **The AI built 80 watchtowers for nothing** — a tower lifts the player's fog and the AI plays without fog (investigator C). | ✅ FIXED October 5, 2026 (§97.8). |
| **EA-11** | P2 | **The AI could not spend its gold on its army.** Its recruit rungs stopped at each corps' 1805 boot strength, a limit the executor does not have and the player never meets: Sweden at war with Britain and Russia, 14,000 gold and 61,000 men in its pool, raised nobody; ~300,000 gold sat in AI chests at turn 40. | ✅ FIXED October 5, 2026: P7.5 "the court arms with its purse" (§97.8). |
| **EA-12** | P3 | **The paymaster paid a court with no army** — Britain's purse sent Sardinia 13,000 over forty turns. | ✅ FIXED October 5, 2026 (§97.8). |
| **EA-13** | P3 | **Most Net lines moved in silence.** The final reading's CMD-H arm: 42 moves of 10% or more, unnamed by any note on five of the first five turns (economy C2 ✗). | ✅ FIXED October 5, 2026: the Net names every line that moved since yesterday's accounts, with its cause (§97.9); economy C2 ✓ on the audit's reading. |
| **EA-14** | P3 | **The counsel never named the law worth buying.** On the commanded turn-20 save France held 32,903 gold with no law in force; "what can I do" offered a 230-gold levy and a 300-gold depot, and the Staff (an order every day, 9,000) was named nowhere a player asks what to buy. | ✅ FIXED October 5, 2026 (§97.10). |
| **EA-15** | P3 | **The desk shrugged at the purse** — "what should I spend gold on", "what should we buy" and "how are our finances" (SFR-D1's class). | ✅ FIXED October 5, 2026 (§97.10). |
| **EA-16** | P4 | **Living balance C5's reader keys "newly free" off the rows, which can lag the news.** On the audit's CMD-M arm the turn-12 page said "Austria and Prussia would now join a league against us"; THE NEXT LEAGUE's rows first carried Prussia on turn 13, and the reader asked turn 13's page for the sentence. | ✅ FIXED October 5, 2026 in the audit: the cause is the dispatch, not the timing — the coalition section records no league table on a morning the old league still stands, while the page's beat reads the same forecast every morning, so the news can come one page before the rows. The reader accepts the previous morning's page only when that morning carried no table at all (`_score_probes.THE_C5_READER_KNOWS_A_TABLELESS_MORNING`); the audit's reading re-checked: C5 ✓ (6 of 6 newly free courts on the page), the pre-correction files kept beside (`*_before_ea16.json`). |
| **EA-17** | P4 | **A top-rung confrontation card promised a harder quarrel** — "the quarrel may harden further", and a Promise that it "cannot harden further", at the ladder's top rung (investigator E). | ✅ FIXED October 5, 2026 (§97.11). |
| **EA-18** | P3 | **The counsel refused the Staff to a court for being rich.** Found pinning EA-14: the law line's purse test asks the forecast Net to carry the law's upkeep, but the Charges of Empire are a share of the chest above its floor, so a rich chest's Net reads low only because the Charges grow with it — France at 30,000 nets +47 and was told to levy 3,000 infantry; at 40,000 it nets −305. | ✅ FIXED October 5, 2026: the counsel reads the Net BEFORE the Charges (`reforms.ai_purse_refusal(..., net_before_charges=True)`, lever `counsel.THE_COUNSEL_SEES_THROUGH_THE_CHARGES`) — the Charges fall as the chest falls, so a law the pre-Charges Net carries is sustainable. The AI rung keeps the plain read; whether it should follow is `DESIGN_REFINEMENT.md` EAD-9 (§97.10). |
| **EA-19** | P3 | **The league forecast names a court in a truce with us as free to join.** Found tracing EA-16, on the audit's CMD-M arm: turn 12's page said "Austria and Prussia would now join a league against us (relations −77 and −25)"; turn 13's said "our peace binds Austria for 4 more turns". The truce wrote the armistice cooldown, which refuses her declaration (R99), and a court whose declaration fails is not a member (§97.12) — but `qualifies_for_coalition`, which the forecast, the beat and THE NEXT LEAGUE all read, asks only whether the pair is at WAR. | ✅ FIXED October 5, 2026 in the economy gate (§6.8; rules §98.6): `diplomacy.declaration_cooldown_left` is the one reading R99, the offensive cascade, the war council and the coalition gate share; a court the declaration would refuse does not qualify (`coalition.A_TRUCE_BINDS_THE_LEAGUE`); the forecast's own `truce` status ("our truce binds her N more turns"). Riders found tracing it: a standing league enrols nobody new, so the line no longer says "She will march" (`A_STANDING_LEAGUE_IS_NOT_REOPENED`); a league whose declarations failed down to one court is no league (`A_LEAGUE_NEEDS_TWO_MEMBERS`). The series byte-identical alone (no truce with the passive France). Pins `TestATruceBindsTheLeague` + two rider classes. |
| **EA-E1** | P3 | **The compact top bar's navigation buttons draw blank.** `Utils.apply_button_icon` sets `expand_icon = true`; in compact mode each button's content width is 0, so neither the icon nor the letter draws (the fallback tests `btn.icon != null`, which is true). Measured at Interface Scale 2.0; any player under 1,180 logical pixels sees six unlabelled boxes. Investigator F, re-filing SFR-I3, whose "capture artefact" diagnosis is wrong. | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9): done when the compact bar draws its icons (or letters) at both Interface Scales and the frame is shot. ⟨SF step=9 · SF-RR5 · pillar=ui_ux⟩ |
| **EA-E2** | P4 | **`gear.svg` and `book-open.svg` draw black** — they still use `stroke="currentColor"`, unlike the five preprocessed navigation icons. | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9): done when both are preprocessed and the frame is shot. ⟨SF step=9 · SF-RR5 · pillar=ui_ux⟩ |
| **EA-E3** | P4 | **The Admiralty chip's blockade border is amber**, against NAVAL_SPEC §17's "crimson-bordered under blockade" (the crimson is only the text). | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9). ⟨SF step=9 · SF-RR5 · pillar=naval⟩ |
| **EA-E4** | P4 | **"seats 1 courts"** — `settlement_multi_court_table_talleyrand` hard-codes the plural. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9): done when its pin flips with its lever. ⟨SF step=9 · SF-RR3 · pillar=diplomacy⟩ |
| **EA-E5** | P3 | **The wizard's step-2 assessment shrinks to a sliver at Interface Scale 2.0** — one row of glyph tops in a second scroll area, 3 of 6 action chips shown. | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9). ⟨SF step=9 · SF-RR5 · pillar=ui_ux⟩ |
| **EA-E6** | P3 | **SETTLEMENT_THREE_COURTS_X2 fails its must_show** — Britain's Press/Ease/Drop row is cut and four scroll thumbs stack. | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9). ⟨SF step=9 · SF-RR5 · pillar=ui_ux⟩ |
| **EA-E7** | P4 | **The Generals screen's filigree draws over scrolled text** ("[1] Ney" under the bottom-left corner). | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9). ⟨SF step=9 · SF-RR5 · pillar=ui_ux⟩ |
| **EA-E8** | P3 | **An IQ-10 capture row fires a real request at port 8005** — the formables entry row is staged as `method: "open"`, and `diplomacy_wizard.open()` sends `_fetch_nations`; `score_run._env` sets no `SOVEREIGN_PORT`, so the capture talks to whatever runs on the player's own port. | ✅ FIXED October 5, 2026 in the economy gate (§6.8; rules §98.8): every child of the reading reads `SOVEREIGN_PORT` = `score_run.INSTRUMENT_PORT` (8021), never the player's 8005; the formables entry row renders its captured step-1 payload. Pins `TestTheInstrumentTalksToNoLivePort`. |
| **EA-E9** | P3 | **An advertised hotkey is eaten by a common overlay.** The README advertises "R / Alt+R" for the dispatch while typing; the NVIDIA overlay takes Alt+R — FA-N56's class (Alt+Tab was replaced by Alt+` for exactly that reason). | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9): a second binding the common overlays leave alone, the README and the help updated; done when a live session presses it. ⟨SF step=9 · SF-RR5 · pillar=ui_ux⟩ |

## Score Finish Step 8 — the final reading's findings, October 5, 2026 (**SFR-D11 (the P1) and SFR-H1 FIXED by SF-RR1 part (i) the same day, after the reading; SFR-D1, SFR-D23 and SFR-D39 FIXED and SFR-I3 superseded (by EA-E1) in the economy audit the same day; at filing: 80 rows: 77 OPEN (1 P1 · 30 P2 · 39 P3 · 7 P4), owned by the residue slices SF-RR1 … RR6 (`SCORE_FINISH_SPEC.md` §3 Step 9) and, for one, ROADMAP 13; SFR-I1 FIXED in the step; SFR-D12 + D13 folded into SFR-I2** — SFR-H1 … H14 by the fresh blind HOLD (command C3: 11 of 20 orders as meant on the final tree, 6 of 20 on `c20d5bba`); SFR-D1 … D44 by the hand-played depth campaign (26 turns, 16 keyed and 10 keyless; the playtester's report verbatim in `docs/audits/SFR_DEPTH_CAMPAIGN_2026_10_05.md`; SFR-D11 verified at the wire and the reading's one P1, which caps command; the three other P1s the playtester claimed, D5, D28 and D29, verified as P2, each row says why); SFR-B1 … B13 by the blind panel's flags, each checked against the digest line or frame it cites, and SFR-B14 + B15 by the reading's own items; SFR-I1 … I7 the instrument; memo `docs/audits/SCORE_FINAL_2026_10_05.md`)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SFR-I1**~~ | P3 (instrument) | **The SUITE arm handed its pytest children PYTHONIOENCODING=utf-8**, and the BASELINE_SERIES pin — which decodes its own child's output in the console code page — errored at setup on the final reading (3 errors; the same tests green in the pre-commit hook the same hour). Unseen since the baseline: every session exit ran `--skip SUITE`. | ✅ **FIXED — Step 8, October 5, 2026:** the arm runs the suite as the hook does (`score_run._run_suite`: no PYTHONIOENCODING, `errors="replace"`); re-run alone on the final reading, 577 green across the seven files. Pins `tests/test_score_finish_step8.py::TestTheSuiteArm`. ⟨SF step=8 · SF-R · pillar=none⟩ |
| **SFR-H1** | P2 | **An issuance premise with a contraction is refused as a contingency.** `Ney, if Mack's still in Swabia, attack him` → "that is a contingency, not an order" (HOLD t2). `condition_grammar._PREMISE_RE` takes `'s` only after whitespace and lets the name swallow the apostrophe, so "Mack's still in" never matches; "Mack is still in" does. Root cause measured on the regex alone. | ✅ **FIXED — SF-RR1 part (i), October 5, 2026:** the premise grammar reads the foe lazily and takes an attached "'s" ("Mack's", "Mack’s") as the verb; the order runs at issuance like "Mack is still in Swabia". Lever `condition_grammar.A_CONTRACTED_PREMISE_IS_READ`; pins `tests/test_sf_rr1_the_orders_the_reading_met.py::TestAContractedPremiseIsRead`; the HOLD arm re-read on the slice's tree: command C3 12 of 20 (11 at the reading); rules `SYSTEMS_REFERENCE.md` §96.2. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-H2** | P2 | **`pass the Staff law` asks for a marshal named Staff.** `Please pass the Staff law` → "There is no Marshal 'Staff' in the order of battle" (HOLD t2). The law router knows `enact` / `reenact` / `repeal` only; "pass", "adopt" and "decree" fall to the proper-name ask. | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-H3** | P3 | **A typo after `Tell X to` is not repaired, and "in case …" is no reason clause.** `Tell Massena to fortfy at Milan in case Archduke John comes down from the Tyrol` → "the instruction is unclear" (HOLD t2). `repair_leading_verb_typo` repairs a LEADING verb only. | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-H4** | P3 | **"Could Soult drill his corps today?" gets the desk's shrug.** → "I cannot answer that from the dispatches" (HOLD t2). CRT-3 reads it as a question, rightly; the drill's own state probe (`state_probe.order_state_refusal`) answers it. | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-H5** | P3 | **An affordability premise is refused as a contingency.** `If we can still afford it, put a supply depot up in the Rhineland` → "a contingency" (HOLD t2). The build's own price check is the premise. | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-H6** | P3 | **`Commission another marshal` reads "another" as a candidate's name.** → "No candidate named 'Another' awaits a commission" (HOLD t2). Expected: the bench. | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-H7** | P3 | **A levy refused on enemy ground names the ground, not the marshal standing there.** `raise more infantry for Davout's corps` → "We do not control Swabia … Recruitment is impossible there." (HOLD t2; Davout had been mustered into Swabia by Lannes's attack — true, but nameless, W9's class). The same for `recruit some calvary for Murat` and `Buy substitutes to fill out Ney's ranks`. | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-H8** | P2 | **The march-time question reads the wrong province and says no road exists.** `How many turns would it take Davout to march from Rhineland to Lorraine?` → "No lawful road runs from Rhineland to Rhineland for Davout, Sire." (HOLD t1) — the desk took the FIRST province as the destination; `Davout, march to Lorraine` executes on the same board. | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-H9** | P3 | **The fortify what-if answers a march.** `What happens if I order Davout to fortify in the Rhineland?` → "Davout already stands at Rhineland, Sire." (HOLD t1). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-H10** | P3 | **"Which of my marshals can get at Mack soonest?" answers where Mack stands.** → "Mack stands at Swabia, Sire — large force …" (HOLD t1). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-H11** | P3 | **The coalition's membership and the strength figure's scope go unanswered.** `who's in the Third Coalition besides Britain?` → the shrug ("who am I fighting" names all three); `…enemy strength is 44% of ours. Does that count the Russians…?` → "Russia: no word of Buxhowden; no word of Kutuzov." — whereabouts, not what the figure counts (HOLD t1). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-H12** | P3 | **"why did that fail" after a refused order gets the shrug.** TYPED arm, after a refusal: "I cannot answer that from the dispatches, Sire." The refusal's own reason is on the wire the turn it happened. | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-H13** | P3 | **A premise that is already true is refused as a contingency.** `If Ney beat Mack, give him a rente for it` → "Sire, that is a contingency, not an order" (HOLD t2; Ney had beaten Mack on turn 1). The premise is a fact the game holds — SFR-H1's and H5's class, a past event. | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-H14** | P3 | **"whats the flaw in our doctrine" gets the desk's shrug.** HOLD t1 → "I cannot answer that from the dispatches". The doctrines (SR-7d) name France's flaw on the ledger; the desk does not, and the missing apostrophe may be the trigger. | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-D1** | P2 | **"how is the treasury?" gets the desk's shrug.** c00/c01 t1–2, k03 t22; "how much gold do we have?" answers. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | ✅ FIXED October 5, 2026 in the economy audit (EA-15): "how is the treasury?", "how's the treasury?", "how are our finances" and "are we going broke?" are the state desk's `net` kind — the chest and its Net, line by line (`state_desk.classify_state_question`; the contraction and the fear found closing the row); pins `tests/test_economy_audit_2026_10_05.py::TestTheCounselNamesTheLaw` (driven through `POST /command`); rules `SYSTEMS_REFERENCE.md` §97.10. |
| **SFR-D2** | P3 | **The desk shrugs at plain questions.** "what happened at Swabia?", "who holds Bavaria?", "who can stop Paget?", "who deserves a reward?", "who are we STILL at war with?", "is the war with Austria over?", "how loyal are my marshals?", "who could become our vassal?", "is Sardinia still in play?" (t1–26, both stretches). Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-D3** | P2 | **Trusting an objection silently cost two orders.** c01 t1: the Trust arm's fortify spent the turn's last action; the Insist arm states its price, the Trust arm did not. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=marshal_drama⟩ |
| **SFR-D4** | P2 | **The interrupt and the muster give different figures and opposite verdicts for one corps.** c01 t2: "35,833 with the muster committed … Odds unfavorable" then "expect about 42,734 … favorable". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=combat_legibility⟩ |
| **SFR-D5** | P2 | **A holding marshal is drawn into a muster with no word that he leaves his post.** c02 t3: the Emperor's muster named Massena and Teulie, who held Milan; Milan fell on t5. (The playtester filed it P1 with two cannon-fire redirects; those were the driver's fixed `investigate` answer — its own harness note — so the row is the muster alone, P2.) Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=ai_aliveness⟩ |
| **SFR-D6** | P2 | **The Trust arm named one army and attacked another.** c02 t3: `Massena, fortify Milan` (he stood at Munich) → "Trust him and he will attack Mack at Tyrol"; the battle was against Archduke Charles. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=marshal_drama⟩ |
| **SFR-D7** | P2 | **An order naming a province the marshal is not in is carried out where he stands, without a word.** c03 t6 `Massena, drill your men and rest them at Munich` → drills at Franconia; c05 t10 `Ney, defend Swabia` → defends at Rhineland. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D8** | P2 | **A reward read as a cavalry charge.** c02 t3: `reward Murat for his charge at Swabia` → "Murat needs one victory first …". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D9** | P2 | **`drill your guard` became a standing HOLD.** c05 t10: `Napoleon, drill your guard` → "Napoleon will hold Munich". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D10** | P2 | **Compound orders lose their second half.** c01 t1 `dig in at Milan and hold the line` → a HOLD, no fortify; c06 t11 `Lannes, unfortify and march on Bohemia` → the march dropped silently; c03 t5 `break camp and march …` refused though "breaks camp" is the game's own word. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D11** | P1 | **`march home to <province>` / `march back to <province>` marches to another province.** **Verified at the wire on the final tree** (`POST /command`, fresh 1805 board, Lannes placed at Rhineland): `Lannes, march home to Franche-Comte` → "Lannes begins march to Lorraine … (Our maps read Lorraine as the province nearest your order, Sire.)"; `march back to Franche-Comte` → Lorraine; `Massena, march home to Franche-Comte` → Piedmont; `Lannes, march to Franche-Comte` targets Franche-Comte. The adverb rides into the destination and the nearest-province reading replaces a province the player named — CRT-2's rule, the name is never replaced (depth c08 t15, k01 t17: corps sent away from home under an internment warning). The disclosure is honest; the march still begins. | ✅ **FIXED — SF-RR1 part (i), October 5, 2026** (after the final reading; the reading's cap stands as measured, and the next reading reads command without it): `strategic_parser.province_named_after_relative` — a relative word (home, back, the rear) followed by a connector and a province the map names is an adverb of the march, so the province is the destination; only a province on the map takes the order ("march home to rest the men" still goes home), accents folded. Found in passing and fixed by the same reader: `march home toward Franche-Comte` stored the phantom order target "Home Toward Franche-Comte". Lever `strategic_parser.A_NAMED_PLACE_OUTRANKS_HOME`; pins `tests/test_sf_rr1_the_orders_the_reading_met.py::TestTheNamedProvinceOutranksHome` (driven through `POST /command`) + two golden-corpus rows (`sfr-d11-*`); rules `SYSTEMS_REFERENCE.md` §96.1. Still refused, honestly and free, and left to SFR-D37 (part (ii)): `return home to …`, `go back to …`, and `withdraw home to …` (read as the enemy's retreat). ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D14** | P3 | **Copy slips.** "the Emperor Napoleon stands at…" (lower-case start), "Under a standing move to order", "Massena, Murat hold under your own orders", "Milan is Kingdom of Italy's", "the Austria court", "under the peace with Austria" for a truce. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-D15** | P3 | **A battle reported with no outcome.** c02 t4: the battle line is "Murat leads the charge! (Aggressive: +15% attack)" alone. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=combat_legibility⟩ |
| **SFR-D16** | P3 | **Asking Talleyrand about his mission returns a generic brief on the court.** c02 t4, c08 t16. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=diplomacy⟩ |
| **SFR-D17** | P3 | **One battle reported at two places.** c02 t4: "broken at Munich" beside "mauled at Tyrol". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=combat_legibility⟩ |
| **SFR-D18** | P3 | **The objection prices the attack alone while six corps stand beside it.** c01 t1 "The odds are not in our favor"; the next day the same attack with the muster read "favorable". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=marshal_drama⟩ |
| **SFR-D19** | P3 | **`how many action points do I have?` returns the rules, not the count.** c01 t1; `how many actions do I have left?` counts. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=first_contact⟩ |
| **SFR-D20** | P3 | **`attack Mack if he is still standing` is refused as a contingency.** c01 t1 — SFR-H1's premise class. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D21** | P3 | **A one-step march finishes at once but its order lingers ("0 turns remaining").** c04 t7 onward, both stretches; the lingering order drew a cannon-fire question. The OP arm's digest carries the same line ("Soult is marching to Swabia (0 turns remaining)", t2). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-D22** | P2 | **An objection that names no alternative: trusting it spends an order and leaves the marshal idle.** c03 t6 `Ney, support Davout` → "Give me a battle of my own." → trust → idle. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=marshal_drama⟩ |
| **SFR-D23** | P2 | **Two surfaces disagree on the treasury the same morning.** c04 t9: "the treasury holds -167" beside "LEDGER treasury 1398". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | ✅ FIXED October 5, 2026 in the economy audit: the crisis beat's buy-off line was priced against the mid-advance chest (the council sits inside the advance, before the income phase); it now reads `ledger.chest_forecast` — the chest the turn will leave, the ledger's own figure (`war_council.THE_BEAT_READS_THE_MORNINGS_CHEST`); pins `tests/test_economy_audit_2026_10_05.py::TestTheBeatReadsTheMorningsChest`; rules `SYSTEMS_REFERENCE.md` §97.5. |
| **SFR-D24** | P2 | **`Ney, stop chasing John and hold where you are` is refused for a destination.** c04 t8 → "I could not make out a destination in that order". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D25** | P3 | **`Lannes and Murat, scout Tyrol`: Murat dropped silently.** c04 t8. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D26** | P3 | **A raw code word in the answer, and Talleyrand gives no estimate.** c05 t10 "scores 30 — COUNTER_OFFER, Sire"; c04 t7 a generic brief. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=diplomacy⟩ |
| **SFR-D27** | P3 | **A province's listed neighbours read strangely.** c05 t9: "Orleanais borders … Ile-de-France"; Paris does not border Ile-de-France. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=ui_ux⟩ |
| **SFR-D28** | P2 | **A truce with Austria leaves Bavaria's war running under French corps, unannounced.** c07 t13–15: Austria stormed Munich and marched into Swabia while four French corps stood there under the truce, and Bavaria was eliminated; the armistice offer said nothing of the ally's war. (Filed P1 by the playtester; the engine kept the truce's own rule — the row is the missing warning, P2.) Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=diplomacy⟩ |
| **SFR-D29** | P2 | **An internment warning for corps on French-held soil, and the rule cannot be asked.** c07 t13–15: "Massena and Murat are no nearer home … their corps will be interned where they stand" while they drilled at Milan, which France held; no internment came; "why must Massena go home?" and three like it shrug. (Filed P1 by the playtester; verified in the digest as a false warning, P2.) | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=narration⟩ |
| **SFR-D30** | P2 | **The dispatch strands a marshal who has arrived.** c08: "Ney arrives at Franche-Comte" then "Ney is on the wrong side of the frontier at Swabia". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-D31** | P2 | **"Enemy harassment" losses during a truce.** c07 t13–14: Davout lost 469 and Lannes 213 "to enemy harassment" with only Austria near, under the truce. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=combat_legibility⟩ |
| **SFR-D32** | P2 | **A false levy reminder, and a famine count dated before a newcomer arrived.** c07 t14. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-D33** | P3 | **The famine toll shrinks as its turn count grows.** c06 t12–13: "2,760 men lost in 3 turns" → "4 turns … 2,655 men gone". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-D34** | P2 | **Terms "prepared" — or Talleyrand's own counsel executed — then refused for an alliance paradox the advisor never named.** c04 t7 (Austria/Bavaria), c06 t12 (Britain/Spain). **Verified on the OP arm, turn 1:** `Talleyrand, assess our situation` → expand → `execute_proposal` → "refused: Making peace with Britain while allied with Spain (who is still at war with Britain) creates a diplomatic con[flict]…". The counsel offers an order the game refuses (CN-4's rule: a remedy names an order the game takes); raised P3 → P2 on that evidence. | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=diplomacy⟩ |
| **SFR-D35** | P3 | **An enemy forced march bounces back and forth.** c08 t15: "Piedmont → Lyonnais → Piedmont → Lyonnais". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=ai_aliveness⟩ |
| **SFR-D36** | P3 | **Losing a satellite kingdom ranks below a mauled corps.** c03 t6. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-D37** | P2 | **Common phrasings fail without the key.** k01–k03: `Soult, take Lyonnais back from Paget`, `Napoleon, return to Paris`, `Ney, keep going to Provence`, `Ney, take Provence back`. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D38** | P2 | **The second half of `march to X and then fortify` is dropped while reported done.** k05 t25: "executed as written. Soult arrives at Burgundy"; `is Soult fortified?` → "No, Sire". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D39** | P2 | **A sponsorship is paid off the books.** k04–k05: "200 gold per turn" to Sardinia; the Net omits it and the treasury grows 152–202 less than the Net each turn. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | ✅ FIXED October 5, 2026 in the economy audit (EA-1): every recurring transfer between courts — a sponsorship, the paymaster's subsidy, London's Congress subsidy — is ONE signed "Subsidies" Net line on both sides, payer − and recipient +, recorded as the engine moved it (`instruments.THE_SUBSIDIES_ARE_ON_THE_BOOKS`); the Net and the chest agree again; pins `tests/test_economy_audit_2026_10_05.py::TestTheSubsidiesAreOnTheBooks`; rules `SYSTEMS_REFERENCE.md` §97.1. |
| **SFR-D40** | P2 | **The allegiance auction gives no way to bid.** k03 t21: `Talleyrand, bid for Sardinia` → "I await your instructions". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=diplomacy⟩ |
| **SFR-D41** | P2 | **Asked for cavalry, paid for infantry.** k03 t22: `Soult, recruit cavalry at Lyonnais` → "Soult recruits 3,000 infantry … 302 gold". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR1 "the orders the reading met" (`SCORE_FINISH_SPEC.md` §3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR1 · pillar=command⟩ |
| **SFR-D42** | P2 | **An ally keeps a liberated French home province, unannounced, and it cannot be asked back.** k03 t21–t27: Provence held by Spain; `Talleyrand, ask Spain to give back Provence` → "I await your instructions". Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR2 "the desk answers what was asked" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR2 · pillar=diplomacy⟩ |
| **SFR-D43** | P2 | **"The war with Britain is over" headlines a truce, and repeats stale the next day.** k01 t19–20. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-D44** | P3 | **"fortifications decay: 6% → 6%" every morning.** k02–k05. Unverified beyond the playtester's quoted digest lines (the chunk digests sit in the depth archive). | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-B1** | P2 | **An AI settlement offer for a war France does not lead reaches France and cannot be answered.** "Only the war leader can settle this side." on accept AND on revision, the letter re-offered: CMD-H t31/32/36/37 (Austria's offer for Austria vs Bavaria, France in by its client), and on CMD-A, CMD-M, CMD-ULM and VOLTE (16 lines). SF-V1's net covers the letters France can sign; this war has another leader (`settlement_validation.evaluate_open_settlement_eligibility`, `not_side_leader`). Verified in the five digests. | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=diplomacy⟩ |
| **SFR-B2** | P3 | **An accepted AI alliance letter is refused at ratification, then logged as our rejection.** REACH-AAR t10–11: `Prussia, alliance #26 → accept` → "refused: … Relations with Prussia stand at 35; an Alliance needs 40.", then "LOG ai_proposal_rejected: We rejected Prussia's full alliance proposal". Verified in the digest. | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=diplomacy⟩ |
| **SFR-B3** | P2 | **The Imperial Peace and a new coalition on the same morning.** PRESS: "THE IMPERIAL PEACE — Europe signs at Paris. Britain, Russia, Austria and Prussia sign." beside "Ottoman has declared war on France … Sweden … Sardinia" and "A coalition has formed against France! Members: Ottoman, Sardinia, Sweden." The Imperial Peace binds the great powers only and spends none of the alarm (66 that morning). Verified in the digest. A design question for the triumph's aftermath — what the Imperial Peace does to the alarm and to the minor courts — owned by ROADMAP 13 (VP-2); its completion: the morning of the peace carries no coalition formation, or the page names why one forms; pin `tests/test_vp2_the_imperial_peaces_morning.py`. | OPEN — owned by ROADMAP row 13, VP-2 "The Ending" — the triumph's aftermath is that gate's; done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=gate · VP-2 (ROADMAP 13) · pillar=ending⟩ |
| **SFR-B4** | P3 | **"The allegiance of Sardinia is in play" recurs every few turns with no outcome the player sees.** On 19 of the reading's arms (CMD-A 8 times in 40 turns); no line ever says who won the bid or that the auction closed. Verified by count. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=ai_aliveness⟩ |
| **SFR-B5** | P3 | **A counsel-sent alliance proposal goes stale in transit.** OP t13–14: "Talleyrand departs for the Prussia court with your Full Alliance proposal" then "The diplomatic situation with Prussia has changed — our proposal is no longer viable." (no word of what changed). Verified in the digest. | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR4 · pillar=diplomacy⟩ |
| **SFR-B6** | P3 | **A petition's Let-it-stand line threatens "For 0 more turns …".** Frame `IQ10_PETITION_COMMAND_CLOSED`: "Free, and it fixes nothing. For 0 more turns he brings NONE of his 22,000 men to any battle Ney leads …" — a grievance on its last turn reads as a threat with no duration. Verified in the frame's recorded text. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=marshal_drama⟩ |
| **SFR-B7** | P3 | **A remitted client reads "Tribute: +0g/turn (75% of their income)".** Frame (THE VASSALS, Switzerland with relief running): the rate is quoted beside a zero without naming the remission. Verified in the frame's recorded text. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=vassals⟩ |
| **SFR-B8** | P3 | **A second fleet action is headlined "TRAFALGAR" again.** SEA: "TRAFALGAR: Nelson's line has shattered the French fleet — 26 sail lost" then, a turn later, "TRAFALGAR: … 12 sail lost". Verified in the digest. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-B9** | P3 | **The morning leads with a client general's capture over the loss of the fleet.** DESC t6: "DISPATCH: Sire — General Teulie has been taken" while "TRAFALGAR: … 22 sail lost" and "THE LANDING" ride beneath it on the rail. Verified in the digest. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=narration⟩ |
| **SFR-B10** | P3 | **The diorama draws a standard over a portrait and the Close button over the frame.** Frame `IQ10_DIORAMA_DADJ` (both scales): Davout's tricolour overlaps Ney's locket; the Close button sits on the corner filigree; the faith line is small crimson italic on dark green. Verified in the frame. | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR5 · pillar=combat_legibility⟩ |
| **SFR-B11** | P3 | **At Interface Scale 2.0 the Proclamation and the petition push their choices below a scroll fold.** Frames `IQ10_PROCLAMATION*_X2`, `IQ10_PETITION_COMMAND_CLOSED_X2`: the terms and the four choices start below the visible area (scrollable — not a soft-lock). Cited by the panel. | OPEN — owned by SF-RR5 "the frames at both scales" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR5 · pillar=ui_ux⟩ |
| **SFR-B12** | P4 | **The intent ladder reads "prepared to go as far as service to the strong".** The nation card's Intent line (Prussia, boot): the rung's name is opaque without the ladder beside it. Verified in the frame's recorded text. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=agendas⟩ |
| **SFR-B13** | P3 | **The war-purpose prompt and the ratification popup print a raw court tag.** "Choose your war purpose against PapalStates." and "France vs Austria + Britain + Naples + Ottoman + PapalStates + …" (CONG t30). Cited by the panel; the CONG digest carries the popup line. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=diplomacy⟩ |
| **SFR-B14** | P3 | **A rival court lets two laws lapse in a long war instead of repealing one.** CMD-M (marengo) t35–37: "THE LAWS: Austria cannot pay for the Landwehr — the law lapses." then "… the Generalissimus — the law lapses." (ai_aliveness C1 ✓ → ✗: 15 laws, 2 lapses). RF-3's purse test keeps 1,000 + five turns of upkeep at the ENACTMENT; nothing reads the purse after it, while the player has `reforms.lapse_forecast` and its repeal lever (GR5 — the same lever for the AI). Found by the reading's own item. | OPEN — owned by SF-RR4 "war, truce and the standing order" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. Note, October 5, 2026: not reproduced on the economy audit's reading (0 lapses on the three commanded seeds, 19–20 laws enacted) — the books now carry the subsidies every purse test reads; the missing rung (an AI court repeals before a law lapses) is still the row's. ⟨SF step=9 · SF-RR4 · pillar=ai_aliveness⟩ |
| **SFR-B15** | P3 | **A satellite under 40 loyalty is reported with no remedy named.** Vassals C4 on BOTH readings (never filed): CMDR-H t14 "Switzerland at 32", t18 "Kingdom of Italy at 39", t20 "Holland at 34" — the reader finds no line naming invest / garrison / autonomy beside them. VS-1's `recovery_hint` rides a fall in the healthy band (≥ 40) and Talleyrand's < 35 advisory is not on the page the item reads; which surface owes the line below 40 is the slice's to read. Found by the reading's own item. | OPEN — owned by SF-RR3 "the page and the copy" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR3 · pillar=vassals⟩ |
| **SFR-I2** | P4 | **The digest prints enemy-phase text the client never renders, and both readers took it for the game.** The driver's `enemy phase:` lines quote each action's `message` and the phase's `summary[]`, which `enemy_phase_dialog.gd` never renders (it rebuilds every line from structured fields — `tools/_name_census.py` UNRENDERED_PATHS, pinned by `tests/test_sf7_s7_the_name_and_the_rank.py`). The raw keys ("ArchdukeJohn assaults the Milan garrison!", "Captured: KingdomOfItaly → Austria") and the first-person enemy lines ("cannot be reached, Sire — … Mack falls back") the depth campaign filed as SFR-D12 and SFR-D13, and the panel flagged, are that field. | OPEN — owned by SF-RR6 "the instrument reads what the player sees" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR6 · pillar=none⟩ |
| **SFR-I3** | P4 | **The IQ-10 capture cannot import the SVG icons, so the compact top bar draws blank squares.** Frames `IQ10_TOP_BAR_*_X2`: the six nav buttons render empty and the gear black (the live client draws both; `top_bar._fit_bar`'s letter fallback fires only for a NULL icon, and the harness loads a non-null icon that draws nothing). The panel could not judge the compact bar from the frames. | SUPERSEDED October 5, 2026 by EA-E1 (§The Economy Audit): investigator F read the client code — the blank squares are a real client defect (`Utils.apply_button_icon` sets `expand_icon` and the compact button's content width is 0), not a capture artefact; the row's work is EA-E1's, owned by SF-RR5. |
| **SFR-I4** | P4 | **Marshal drama C5 cannot read an unmet claim any more, so it reads unmeasured.** The reader (`_score_probes.drama_c5_expectation_before_erosion`) keys on "Marshal X's claim" and "turns without settlement on Marshal X"; since SF5-X3's style helper the dispatch says "Lannes's claim is 21 turns in arrears" and "7 turns without settlement on Lannes", so neither the notice nor the escalation is seen (C5 ✓ → unmeasured; the escalations stand in the OP, CMD-H and CMD-A digests). The digest also does not record the dispatch's Unmet Marshals block or its `expectation_rises`, where the earlier notice lives — corrected for the copy alone, the reader would read OP's Soult (escalated t16, no notice in the digest) as unannounced. Completion: the driver records both blocks, the reader reads both copies, re-read on the next arms. | OPEN — owned by SF-RR6 "the instrument reads what the player sees" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR6 · pillar=none⟩ |
| **SFR-I5** | P4 | **AI aliveness C6 counts any court's declaration as France at war.** `score_run._turns_at_war` opens France's war on every `diplomatic_war_declared` row, so on CMD-M "Prussia has declared war on Hanover" (t12, the same turn as France's settlement) counts turns 12–33 of peace as war (11/39). Read with a France-only rule the arms give CMD-H 8/10, CMD-A 5/19, CMD-M 11/17: the item still fails on CMD-A, where the league that declared at t31 attacks on 1 of its 10 turns (DESIGN_REFINEMENT SFR-DR1). The frozen reader is kept for this reading; the France-only rule must still count a war France joins through its client (CMD-H t27, Austria vs Bavaria). | OPEN — owned by SF-RR6 "the instrument reads what the player sees" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR6 · pillar=none⟩ |
| **SFR-I6** | P4 | **The DL arm's staging has drifted: two items read a board the script did not mean.** DL t1: `Davout, fortify` → "Fortifying from neutral stance requires 2 actions … only 1 remaining", so `what if Davout attacks Mack?` asks about an UNFORTIFIED man and rightly musters — combat legibility C4 reads ✗ for a refusal the arm never staged (RS-12's own fix is not what failed); and Ney's muster carries Davout into Swabia, so `recruit 10000 infantry with Davout` is refused for the ground — economy C5 reads the ground, not the zero-military-actions rule (AAR-6). Both items read ✗ on both readings. Completion: the script stages its preconditions (actions spent on the right turn, the levy on French ground) and the driver flags SCRIPT PRECONDITION when they fail. | OPEN — owned by SF-RR6 "the instrument reads what the player sees" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR6 · pillar=none⟩ |
| **SFR-I7** | P4 | **Combat legibility C5 counts raw keys in text the client never renders.** `score_run.r_combat_legibility_C5` reads `- enemy phase:` lines with the ⚔ and MUSTER lines; every raw key it finds on BOTH readings is in the enemy-phase text (baseline 124, final 46: ArchdukeCharles 27, ArchdukeJohn 18, KingdomOfItaly 1), which the client never renders (SFR-I2). The ⚔ and MUSTER lines carry none on either tree. Read on rendered text, the item passes on both readings (combat legibility: baseline 2 → 3 ceilings, final 3 → 4, its target). The frozen reader is kept for this reading; the corrected marks are shown beside it in the memo and not claimed. | OPEN — owned by SF-RR6 "the instrument reads what the player sees" (§3 Step 9); done when its pin flips with its lever and the arm it came from re-reads clean. ⟨SF step=9 · SF-RR6 · pillar=none⟩ |
| ~~**SFR-D12**~~ | P3 → instrument | **Raw roster keys in enemy-phase text (ArchdukeCharles, KingdomOfItaly, ArchdukeJohn).** Not player-facing: the depth campaign read the digest's enemy-phase lines, which quote a field the client never renders. | ✅ **CLOSED — folded into SFR-I2** (the instrument's row, owned by SF-RR6). ⟨SF step=9 · SF-RR6 · pillar=none⟩ |
| ~~**SFR-D13**~~ | P3 → instrument | **Enemy narration in the first person, addressed to "Sire".** Not player-facing: the depth campaign read the digest's enemy-phase lines, which quote a field the client never renders. | ✅ **CLOSED — folded into SFR-I2** (the instrument's row, owned by SF-RR6). ⟨SF step=9 · SF-RR6 · pillar=none⟩ |

## Score Finish Step 5 — found in passing, October 3, 2026 (**3 rows — SF5-X1 + SF5-X2 FIXED in the step; SF5-X3 FIXED in Step 7 slice 7** — found while building VD-C, when a first-draft contingent's march raised an interrupt in the R39 hard-stop pin; reproduced on the shipped boot without it; rules `SYSTEMS_REFERENCE.md` §90.11; pins `tests/test_sf5_the_question_and_the_interrupt.py`; sweep `tools/_sweep_step5.json`)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SF5-X1**~~ | P1 | **A QUESTION answered a strategic interrupt — and fought.** The typed interrupt route (`main.py`, PENDING STRATEGIC INTERRUPT CHECK) runs before every other reader of the line and maps option words with no question guard, so with Ney's bad-odds interrupt on Mack pending (attack anyway / hold / cancel) "should we attack?", "should I attack anyway?", "can we attack him?" and "would it be wise to proceed?" each FOUGHT the battle the player had only asked about (measured on the shipped boot: four phrasings, four battles). CRT-3's "a question never orders", one road over — the dialogue families have refused this since IQ-7's review round; the interrupt road never learned it. | **FIXED in Step 5:** `main.A_QUESTION_NEVER_ANSWERS_AN_INTERRUPT` — a question-shaped line (`dialogue_routing.line_asks_a_question`) that names one of the interrupt's own answers orders nothing; the reply restates the interrupt's question with its answers, labelled as the popup labels them (`_INTERRUPT_OPTION_LABELS`, drift-pinned against `interrupt_popup.gd`), and re-carries `pending_interrupt` so the popup stands again. A question naming none of the answers goes on to the desk; an exact option id still answers. ⟨SF step=5 · found in passing · pillar=command⟩ |
| ~~**SF5-X3**~~ | P3 | **A client's general is styled "Marshal".** A contingent's commander (and a VS-4 assimilated corps' general) is his own court's general, never a Marshal of the Empire (R12), but the copy styles every marshal-object "Marshal {name}" — measured on the commanded completion run: *"Sire — Marshal Teulie has been taken. Austria holds him prisoner."* A census finds 90 `Marshal {…}` templates under `backend/`. | ✅ **FIXED — Score Finish Step 7 slice 7, October 4, 2026:** ONE style helper, `display_names.marshal_title` (the court's own honorific with the display name; "General" for `contingent.is_clients_general`, lever `A_CLIENTS_GENERAL_IS_STYLED_GENERAL`), read by every template that styled a marshal object — 79 sites converted, the 18 survivors allowlisted with their reasons; a tombstone keeps `original_nation`. The AST census over `backend/` fails on a new `Marshal {…}` literal and on a stale allowlist row. **Done-when met on the Jena road arm (historical):** *"Sire — General Teulie has been taken. Austria holds him prisoner."* where the pre-slice tree printed *"Marshal Teulie"*; on this tree the VD-C commanded arm no longer captures Teulie on either seed re-run (historical, austerlitz), so the line cannot be read there, and a staged pin holds it. Rules `SYSTEMS_REFERENCE.md` §93.9; pins `tests/test_sf7_s7_the_name_and_the_rank.py::TestTheOneStyle` / `::TestTheCensus` / `::TestTheSurfacesSpeakTheRank`. ⟨SF step=7 · Rows · pillar=narration⟩ |
| ~~**SF5-X2**~~ | P2 | **The interrupt route ran ahead of a standing hard stop, and a refused answer destroyed the decision.** With the war's purpose waiting (a HARD_STOP), a typed "attack anyway" reached Ney's interrupt first; the attack was refused downstream by the hard stop's diplomacy gate, and the refusal cleared the interrupt AND Ney's standing order with nothing done — the war-purpose question still on the desk, the pursuit gone (measured on the shipped boot). | **FIXED in Step 5:** `main.A_HARD_STOP_OUTRANKS_AN_INTERRUPT` — while a hard stop stands the line falls through to the hard-stop gate, which names its own question; the interrupt waits for its answer after it. ⟨SF step=5 · found in passing · pillar=command⟩ |

## Score Finish Step 7 — found in passing, October 4, 2026 (**49 rows: all 49 closed — 41 in the step, SF7-X37 … X39 (found by the exit) and SF7-X45 … X49 (found building it, reading its exit and shooting its frames) closed in Step 7b** — SF7-X36 and SF7-X40 … X44 found and closed by the Step 7 exit (three instrument readers — narration F1, ending F2, command C5 — the judge's vocabulary, the action pre-gate's sentence and the sponsorship idiom; pins `tests/test_step7_exit_fixes.py`; sweep `tools/_sweep_step7_exit.json`), SF7-X37 … X39 found by the exit's reading and owned by Step 7b; SF7-X33 and X34 closed in slice 10, and SF7-X35 found by slice 10's own board and closed with them (rules `SYSTEMS_REFERENCE.md` §93.12; pins `tests/test_sf7_s10_the_ais_own_accounting.py`; the series attribution `tools/_sf7_s10_series_arms.py`); SF7-X17 … X32 found by the frames (the IQ-10 re-shoot at both Interface Scales and a five-turn Mode C session on the live client) and closed in slice 9 (rules `SYSTEMS_REFERENCE.md` §93.11; pins `tests/test_sf7_s9_the_frames.py` + `tests/test_cx7_predictor_driven.py`; the before pack `docs/audits/SF7_MODEC_BEFORE_*_2026_10_04.png`, the frames `docs/audits/IQ10_*_2026_10_05.png`); SF7-X33 and X34, two AI mechanics defects the frames' own reading found, owned by slice 10; SF7-X16 found and SF7-X7 closed in slice 7 (rules `SYSTEMS_REFERENCE.md` §93.9; pins `tests/test_sf7_s7_the_name_and_the_rank.py`); SF7-X12 … X15 found by SF-DC-1's doctrine census and closed in slice 6 (rules `SYSTEMS_REFERENCE.md` §93.8; pins `tests/test_sf_dc1_nothing_unnamed.py`); SF7-X1 found researching §6 row 17, SF7-X4 found building §6 row 16, SF7-X2 and SF7-X3 found by slice 3's own measurement and closed in slice 3b, SF7-X5 and SF7-X6 found building the Tilsit clause and closed in slice 4, SF7-X7 found by slice 4's austerlitz arm and homed to the Chunk 9 slice, SF7-X8 found and closed in slice 5a, SF7-X9 … X11 found driving the HOLD arm and the map's names and closed in slice 5b; rules `SYSTEMS_REFERENCE.md` §93.1 / §93.3 / §93.5 / §93.6 / §93.7; pins `tests/test_sf_nav1_d1_the_conquest_road.py`, `tests/test_sf_cl1_d1_the_coordination_is_read_on_the_field.py`, `tests/test_vp_r1_the_road_to_forty_five.py::TestCTheGloryAttackObeysTheOdds`, `tests/test_sf_nav1_d1_the_tilsit_clause.py`)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SF7-X7**~~ | P2 | **A separate peace says nothing about the French soil it leaves with the enemy.** Under SR-1a's rule (status quo is a cession, both directions) a bilateral peace titles every province each side holds of the other's homeland, and at peace that soil is a closed frontier. The player's own separate-peace road (`propose common peace with X` → "Make peace with X only" → the proposal confirm) never names what the enemy keeps — only an incoming settlement offer carries the "X retains …" line (`settlement_offers._derive_status_quo_lines`, W6-10) — and the ratification names France's retained gains ("Franconia and Swabia — retained by the peace with Austria") and not the court's. Found by slice 4's austerlitz arm: Austria's Tilsit peace on turn 13 left it Champagne, Burgundy and Berry, and from turn 14 every French march south was refused ("There is no open road to Bearn, Sire — every route crosses Austria's closed frontier at Champagne") while Moore's 25,000 campaigned in Guyenne and Maine. | ✅ **FIXED — Score Finish Step 7 slice 7, October 4, 2026** (lever `game_end.THE_PEACE_NAMES_WHAT_EACH_SIDE_KEEPS`): every peace proposal from war or truce — the typed road and the separate peace's handoff alike, through `diplomatic_dialogue._enrich_proposal_summary` — carries the status quo from the player's chair: *"Status quo: Bohemia stays ours by the treaty — titled."* and *"WARNING: Burgundy and Champagne stay with Austria by this peace — French soil behind a closed frontier once it is signed."*; the morning after, the dispatch names the soil ceded (`status_quo_conceded`) beside the soil kept. **One deviation from the row, measured and recorded:** the forecast reads the RATIFIER's own `status_quo_retentions` (`forecast=True`), not the incoming offer's `settlement_offers._derive_status_quo_lines` — the letter's derivation is war-wide and reads the home rolls only, while the ratifier titles the pair's bloc with its conquest records, so only the ratifier's rule makes the forecast what the treaty applies (pinned: forecast == the entries the setter writes on signing). The ratification summary already carried both directions (`game_end.status_quo_summary_lines`). Rules `SYSTEMS_REFERENCE.md` §93.9; pins `tests/test_sf7_s7_the_name_and_the_rank.py::TestThePeaceNamesWhatEachSideKeeps`. ⟨SF step=7 · slice=Chunk 9 (found by slice 4) · pillar=diplomacy⟩ |
| ~~**SF7-X5**~~ | P2 | **The plain "Force X into alliance" enrolled the court in the Continental System anyway.** The settlement table offers two links — "Force Austria into alliance" and "[+ Continental System]" — and the plain one wrote no flag (`settlement_actions._handle_settlement_demand_action`), which every ratification reader takes as the canonical True (`settlement_ratify` and `_ratify_treaty`): the court joined the System, the alarm was charged +25 where the plain alliance costs +15 (`compute_forced_alliance_threat_preview`), and the staged row and the incoming-offer summary — which read a missing flag as False — printed "Forced alliance". Found building the Tilsit clause (the one membership write reads the same flag). | **FIXED in Step 7 slice 4** (`settlement_actions.THE_PLAIN_ALLIANCE_KEEPS_NO_SYSTEM`; pins `tests/test_sf_nav1_d1_the_tilsit_clause.py::TestTheAddVerb` + `::TestTheDisplaysReadTheCanonicalDefault`): the add verb writes the choice either way, and every display that reads the flag reads a keyless clause as ratification does — the staged row, the offer summary, and the bilateral label ("Austria enters ALLIANCE with France" when the flag says no). ⟨SF step=7 · slice 4 (found building row 17) · pillar=diplomacy⟩ |
| ~~**SF7-X6**~~ | P4 | **The forced-alliance toggle row named the Emperor as the court joining the System.** `compute_forced_alliance_continental_toggle_differential` read "Adds France to the Continental System; extra threat cost applies." for an alliance forced on Austria — it named `to`, the imposer — and a pin enshrined it. The row rides the settlement payload; no client renders it today. | **FIXED in Step 7 slice 4** (`tests/test_settlement_forced_alliance_continental_toggle.py` consciously flipped; `tests/test_sf_nav1_d1_the_tilsit_clause.py::TestTheToggleRowNamesTheJoiner`): the row names the court forced into the alliance. ⟨SF step=7 · slice 4 (found building row 17) · pillar=diplomacy⟩ |
| ~~**SF7-X8**~~ | P4 | **The targetless named-court refusal said "No Prussia force".** PT-H3's arm put the court's NAME where its adjective belongs ("No Prussia force is within Ney's reach"), and `tests/test_iq9_keyless_parser_gate.py` pinned the slip. | ✅ **FIXED — Score Finish Step 7 slice 5a (SF-CMD-2's remainder), October 4, 2026:** found writing NPC-26's sibling sentence; both named-court refusals take `display_names.nation_adjective` ("No Prussian force …", behind `combat_executor.A_NAMED_NATION_IS_ANSWERED`); the IQ-9 pin re-seated consciously. ⟨SF step=7 · SF-CMD-2 (the census's remainder) · pillar=command⟩ |
| ~~**SF7-X9**~~ | P2 | **A scout of an unknown province scouted every neighbour instead, for an action.** `Ney, scout Alsace` — the mock chain extracts only names it knows, so the unknown place was dropped and the bare scout ran (1 action); `scout Alsace` unaddressed was read as a marshal named Alsace. | ✅ **FIXED — Score Finish Step 7 slice 5b (SF-CMD-2's remainder, part b), October 4, 2026:** the place a scout names is kept for the executor's matcher (`llm_client.scouted_place_phrase`, lever `A_SCOUTED_PLACE_IS_KEPT`; generic objects keep the bare scout) and the scout executor answers with the roads out of his province — refused free. Pins `::TestTheScoutKeepsItsPlace`; corpus `sfcmd2r-scout-keeps-its-place`. ⟨SF step=7 · SF-CMD-2 (the census's remainder) · pillar=command⟩ |
| ~~**SF7-X10**~~ | P4 | **A condition clause's foe became the order's destination.** `Ney, fall back while Mack advances` (and `before …`) retreated correctly and then answered *"Mack cannot be reached, Sire — no such province is known to the staff"*: the parser's fuzzy target scan blanked reason clauses (CRT-1) but not condition clauses. The trailing `in case …` precaution (SF-V9) inherited it. | ✅ **FIXED — Score Finish Step 7 slice 5b (SF-CMD-2's remainder, part b), October 4, 2026:** the scan blanks condition clauses too (`parser.A_BLANKED_CLAUSE_NAMES_NO_TARGET`; `until` / `while` / `before` orders read as before). Pins `::TestAConditionsFoeIsNoTarget`; corpus `sfcmd2r-condition-foe-no-target`. ⟨SF step=7 · SF-CMD-2 (the census's remainder) · pillar=command⟩ |
| ~~**SF7-X11**~~ | P2 | **A levy named for one province was raised in another — gold spent.** `Davout, recruit infantry in Rhineland` with Davout at Lorraine raised 3,000 men at **Lorraine** for 741 gold, the named province silently replaced by where the corps stands (CRT-2's class; the HOLD arm's `Raise more infantry for Davout in Rhineland` was refused about Swabia for the same reason). | ✅ **FIXED — Score Finish Step 7 slice 5b (SF-CMD-2's remainder, part b), October 4, 2026:** PF-7's road stands (a named marshal levies where he stands), but a different province named beside him is refused free, naming both roads (`economy_executor.A_NAMED_LEVY_GROUND_IS_HONOURED`; player orders only — the AI names the marshal's own province). Pins `::TestTheLevyGroundIsHonoured`. ⟨SF step=7 · SF-CMD-2 (the census's remainder) · pillar=command⟩ |
| ~~**SF7-X12**~~ | P2 | **A doctrine-decided arrival on defence was carried and never drawn.** The enemy-phase dialog's report whitelist (`enemy_phase_dialog.gd::_format_berthier_report`) read neither `doctrine_lines` nor `morale_line`, which the shared `_execute_attack` composes for every battle — so *"The Hofkriegsrat's orders reached Archduke John too late."*, *"The corps system brought Ney in."* and a Brittle or Stubborn rout reached the player only when HE attacked. Measured by the census: 6 doctrine-decided arrivals in the enemy phase unnamed on the two arms (the Hofkriegsrat ×3, the corps system ×2, Russia's slow concentration ×1) — UX23-R8's whitelist lesson again. | ✅ **FIXED — Score Finish Step 7 slice 6 (SF-DC-1), October 4, 2026:** both keys drawn, after the trust note and before Berthier's observation (main.gd's order); parse harness EXIT=0, boot 0 SCRIPT ERROR. Pins `::TestTheClientDrawsTheDoctrineLines`. ⟨SF step=7 · SF-DC-1 · pillar=combat_legibility⟩ |
| ~~**SF7-X13**~~ | P2 | **An AI levy's doctrine note was read off the wrong dict.** `_format_action` read `ai_action.get("doctrine_note")` — the AI's DECISION dict — while the executor puts the note on its RESULT, the action entry itself (`economy_executor._execute_recruit`; `enemy_ai` sets `result["ai_action"] = action`), so *"Mack recruits troops (The Hereditary Lands, ×0.85)"* never rendered: 33 of 33 visible Austrian levies on CMD-H unnamed. The SR-7d pin asserted the backend half only. | ✅ **FIXED — Score Finish Step 7 slice 6 (SF-DC-1), October 4, 2026:** read off the action entry (`action.get("doctrine_note")`); the census reads the dict a client renderer uses, not the key's presence. Pins `::TestTheClientDrawsTheDoctrineLines::test_the_levys_note_is_read_off_the_action_entry`. ⟨SF step=7 · SF-DC-1 · pillar=combat_legibility⟩ |
| ~~**SF7-X14**~~ | P3 | **A standing order's battle printed its outcome and dropped Berthier's report.** `main.gd::_show_strategic_reports` drew the row's `battle_message` and `outcome`; the row has carried `battle_report` since WO-33 and nothing drew it, so a battle a MOVE_TO or PURSUE fought at the end of a turn lost its breakdown, its casualties, its voices and its doctrine lines. Found by the census's own model of the client (no doctrine effect rode this route on the two arms). | ✅ **FIXED — Score Finish Step 7 slice 6 (SF-DC-1), October 4, 2026:** the row's report renders through `_display_berthier_report`, as the autonomous attacks' report does (PT-F1); ⚠ a visual sign-off on the strategic block is the user's (Step 7's frames). Pins `::TestTheClientDrawsTheDoctrineLines::test_a_standing_orders_battle_draws_berthiers_report`. ⟨SF step=7 · SF-DC-1 · pillar=ui_ux⟩ |
| ~~**SF7-X15**~~ | P3 | **A supply bite's own attrition line never named the clause that caused it.** *"Supply shortage at Franconia: Ney loses 210 troops"* — 10 of them living off the land's — and the supply_strain headline names the clause only when attrition has run two turns and it leads the dispatch. 5 bites unnamed on the two arms. | ✅ **FIXED — Score Finish Step 7 slice 6 (SF-DC-1), October 4, 2026:** the line names the clause and its share, from the engine's own arithmetic re-read with the clause off (`world_state.THE_SUPPLY_BITE_IS_NAMED`; `get_effective_supply_cap(..., with_doctrine=False)`, exact — the clause is the multiplier's last step): *"… loses 1,440 troops — 576 of them to living off the land (this poor country feeds a French army 80%)"*; `doctrine` / `doctrine_losses` ride the event; display only (the loss is unchanged). Pins `::TestTheSupplyBiteIsNamed`. ⟨SF step=7 · SF-DC-1 · pillar=living_balance⟩ |
| ~~**SF7-X16**~~ | P4 | **The Admiralty refused the Emperor in his own name.** `naval_executor._admiralty_misaddressed` refuses a naval order put to a marshal in the field — *"The Admiralty takes its orders from the Emperor, Sire, not from Marshal {name} in the field"* — and never exempted the sovereign, so `Napoleon, build ships` was refused; under the court's own honorific (slice 7's style helper) the sentence became *"not from the Emperor Napoleon in the field"*, contradicting itself. The laws' `reforms_executor._misaddressed` already exempts him. Found converting the copy to the style helper. | ✅ **FIXED — Score Finish Step 7 slice 7, October 4, 2026:** the sovereign is the Admiralty's master, as he is of the laws (lever `naval_executor.THE_EMPEROR_COMMANDS_THE_ADMIRALTY`); a marshal is still refused, by his title. Pins `tests/test_sf7_s7_the_name_and_the_rank.py::TestTheSurfacesSpeakTheRank::test_the_admiralty_takes_the_emperors_orders`. ⟨SF step=7 · slice 7 · pillar=naval⟩ |
| ~~**SF7-X17**~~ | P2 | **The terminal's first trim wiped the whole scrollback.** `main._trim_old_messages` read `output_display.text`, and in Godot 4 `append_text()` never fills `.text` — every line reaches the terminal through `add_output`'s `append_text` — so "keep the last 75%" kept 75% of an empty string. The first time a session passed `MAX_MESSAGES` (turn 1 of the 1805 boot: the briefing, the help and one battle) everything was replaced by the trim marker, the report being printed with it. Seen twice in the Mode C session's five turns. | ✅ **FIXED — Score Finish Step 7 slice 9 (the frames), October 5, 2026:** the messages are kept as `add_output` appends them (BBCode intact, so the battle links still click), and the trim keeps the newest 75% of them (`main.THE_TRIM_KEEPS_THE_MESSAGES`). Driven from an empty terminal: 130 lines through the one writer leave TRIMTEST 50 … 129 standing (80 lines; the old trim kept the 30 written after its clear) — and the engine fact is pinned too (fifty lines appended, `.text` still empty). ⛔ The first cut of the pin started wherever the boot's messages left the count, so the old trim fell early and still left ~69 lines: the sweep found it INERT and the fixed start is the repair. Pins `tests/test_cx7_predictor_driven.py::TestTheFramesTerminalText::test_the_trim_keeps_three_quarters_of_the_scrollback`. ⟨SF step=7 · slice 9 · pillar=ui_ux⟩ |
| ~~**SF7-X18**~~ | P3 | **`[b]` and `[i]` rendered in the regular face everywhere.** The theme set `default_font` (EB Garamond Regular) and no RichTextLabel bold, italic or bold-italic face, and a theme's default font answers every font item it leaves unset — 127 `[b]` and 76 `[i]` sites in the client scripts said nothing. | ✅ **FIXED — slice 9:** `main_theme.tres` names three faces — bold and bold-italic as weight 700 on EB Garamond's own `wght` axis (never the engine's embolden), italic as `EBGaramond-Italic[wght].ttf`, its `.import` sidecar force-added (the font was tracked and the sidecar was not; `assets/` is git-ignored). The two labels that use `[b]` as INLINE emphasis — the terminal (11) and the dispatch (12) — carry bold / italic / bold-italic sizes equal to their body; the ledgers' `[b]` headings keep the theme's 16 on purpose. Driven: the terminal's bold and italic faces differ from its normal face and share its 11px. Pins `tests/test_cx7_predictor_driven.py::TestTheFramesTerminalText` + `tests/test_sf7_s9_the_frames.py::TestTheThemeHasItsFaces`. ⟨SF step=7 · slice 9 · pillar=ui_ux⟩ |
| ~~**SF7-X19**~~ | P3 | **The auto-end line promised an end the game did not make — and printed in the middle of the order.** Slice 8's line ("the order that spends your last action ends the turn at once") was false while a current-turn envoy waits: WO-22 defers the end of the day then (`executor._auto_end_deferral_reason`). And `_update_status` runs before `_display_result`, so the line printed between the echoed order and its result (the Mode C session's turn 2). | ✅ **FIXED — slice 9:** the line is said after the order's own output (`call_deferred`) and names what waits when envoys stand (`AUTO_END_WAITS_WARNING`: "…the day waits on the envoys — answer them, or end the turn and let them lapse"), read off the client's own `pending_lapsing_count`, which is the deferral's own predicate (`dialogue_manager.get_lapsing_count`) (lever `main.THE_DAY_SAYS_WHAT_WAITS`). §6 row 21's re-open condition does not fire: the line now tells the truth, and no turn ended by surprise in the session. Driven: the line is absent the frame it is triggered and present the next; with two envoys waiting it names them and promises nothing. Pins `tests/test_cx7_predictor_driven.py::TestTheDaySaysWhenItEnds`. ⟨SF step=7 · slice 9 · pillar=ui_ux⟩ |
| ~~**SF7-X20**~~ | P3 | **The famine headline counted the page's turns, not the famine's.** Turn 5 of the Mode C session: the headline read "3 turns of famine at Swabia now" while the roster beneath it read "Starving — supply has failed at Swabia four turns running". The escalated variant's `{turns}` was the page's run (the turns the class had been on the page); CA9-N26 had recorded the disagreement and left it to the headline's own row. | ✅ **FIXED — slice 9:** the famine candidate carries the province's own trailing consecutive run, by the roster's window and rule (`dispatch._famine_run`), and the escalation states it (`dispatch.THE_FAMINE_COUNTS_ITS_OWN_TURNS`); every other standing class keeps the page's run. Pins `tests/test_sf7_s9_the_frames.py::TestTheFamineCountsItsOwnTurns`. ⟨SF step=7 · slice 9 · pillar=narration⟩ |
| ~~**SF7-X21**~~ | P3 | **Stale province tooltips under modals and beside screens.** A map hover set before a screen or a modal opened was cleared only by a mouse motion, and a modal's dim backdrop let motion through to the map — so a still cursor drew "Dumonceau: Professional (5)" over the battle tableau and "Anatolia — No intelligence" beside the envoy's letter. | ✅ **FIXED — slice 9:** the map asks its owner whether a modal covers it (`map_renderer_base.pointer_blocked_check`, handed `main._is_modal_dialog_open`); a covered or screen-dimmed map (`panning_enabled` false) clears its hover at once and takes no pointer event (`THE_COVERED_MAP_HAS_NO_HOVER`). Driven on the real map: uncovered the hover stands (the control arm), under a screen and under a modal it clears. Pins `tests/test_cx7_predictor_driven.py::TestTheFramesTerminalText::test_a_covered_map_holds_no_hover` + `tests/test_sf7_s9_the_frames.py::TestTheScreenSays::test_the_main_scene_hands_the_map_its_modal_check`. ⟨SF step=7 · slice 9 · pillar=ui_ux⟩ |
| ~~**SF7-X22**~~ | P4 | **The map tooltip hedged our own soil.** Normandy, French and empty of corps, read "Intel: Partial (reports only)" above four exact figures — WO-V-D2 had dropped the hedge from the region panel in slice 8; the tooltip is its twin. | ✅ **FIXED — slice 9:** no Partial / Stale line where the controller is the player (`map_renderer_base.OUR_SOIL_CARRIES_NO_HEDGE`). Pins `::TestTheScreenSays::test_our_own_soil_carries_no_hedge`. ⟨SF step=7 · slice 9 · pillar=ui_ux⟩ |
| ~~**SF7-X23**~~ | P3 | **The battle tableau drew its fourth contingent outside the frame.** The line's steps were fixed (118px outward, 66px up), so the cap's fourth contingent stood at x ≈ −8 on the 948px stage and its locket climbed into the odometer — Lannes at the Second Battle of Swabia. | ✅ **FIXED — slice 9:** the steps shrink to the room the stage leaves, the authored steps the ceiling (two or three contingents draw as before) (`battle_diorama.THE_LINE_FITS_THE_BAIZE`); the reserve tail follows the steps. Pins `tests/test_sf7_s9_the_frames.py::TestTheLineFitsTheBaize` (the formula read off the scene's own constants). ⟨SF step=7 · slice 9 · pillar=combat_legibility⟩ |
| ~~**SF7-X24**~~ | P4 | **The ledgers' book keys did nothing while the command line held the caret — which is nearly always — and the copy said "Keys 1-7" over eight books.** The Aug 30 review rightly gave a typed digit to whoever holds the caret (so "recruit 5000" no longer turned a tab), and the command line takes the caret back after nearly every order, so in the live session the advertised keys typed into the order instead of turning the book; the strategic ledger has had eight books since RF-4a. | ✅ **FIXED — slice 9:** both ledgers turn their books with Alt+digit while a line edit holds focus (PC15-18's idiom for the screen keys) and with the bare digit otherwise — a bare digit still belongs to the caret (RF-4a's pin re-seated consciously, `tests/test_rf4a_the_laws_tab.py::TestTheClient::test_the_digit_belongs_to_the_caret`) (`strategic_ledger.ALT_TURNS_THE_BOOKS`, `diplomatic_ledger.ALT_TURNS_THE_BOOKS`); the copy reads "Keys 1–8 turn the ledger's books (Alt+1–8 while you type)". Pins `::TestTheScreenSays::test_the_books_turn_while_you_type` / `::test_the_ledger_copy_counts_its_books`. ⟨SF step=7 · slice 9 · pillar=ui_ux⟩ |
| ~~**SF7-X25**~~ | P4 | **Six copy nits on the frames.** "Berry, Burgundy and Corsica and 4 more" (two "and"s in one list); "+1032" (the treasury delta skipped the formatter its own line used); "Morale:0%"; the LAWS tab's cure line "0 corps drawing 80% now ; needs …"; the whole-war table's "Sire, this settlement … seats 3 courts at the table. Sire, Austria will not sign"; a white peace held out because "the terms cut against their national design" (a white peace has no terms); and an ally's petition saying it "fought for this coalition" (on the 1805 board the Coalition is the enemy). | ✅ **FIXED — slice 9:** one "and" when a tail follows (`dispatch.THE_LIST_JOINS_ONCE`); `_format_number` on both treasury deltas; "Morale: "; "no corps drawing 80% now; needs …" (`doctrines.THE_CURE_LINE_READS_CLEAN`); the hold-out line drops its own "Sire, " inside the table's narration (`diplomatic_templates.THE_TABLE_SAYS_SIRE_ONCE`); three white-peace phrases that name no terms (`SPOKEN_BLOCKER_PHRASES_WHITE_PEACE_NO_TERMS`, lever `THE_WHITE_PEACE_NAMES_NO_TERMS`); "Bavaria fought beside France in this war" (`settlement_offers.THE_PETITION_NAMES_ITS_SIDE`). Pins `tests/test_sf7_s9_the_frames.py::TestTheCopyReadsClean` + the flipped SR-6a list pin. ⟨SF step=7 · slice 9 · pillar=narration⟩ |
| ~~**SF7-X26**~~ | P3 | **An ally's victory was printed as a defeat.** The enemy phase coloured a battle's result green only when FRANCE won and every "forced to retreat!" red whoever retreated — so Bavaria, our ally, beating Mack read in the colour of a loss, Mack's retreat in the same red as ours (turn 1 of the Mode C session), and an assault on a foe's garrison was red. | ✅ **FIXED — slice 9:** each enemy-phase event that names its sides carries their standing toward the player (`attacker_alignment` / `defender_alignment`: player, friend — allied or bound by vassalage — foe or neutral; diplomacy has no fog), stamped on COPIES of the producer's events (`main.battle_standing`, `main._stamp_battle_standing`, lever `main.THE_COLOURS_KNOW_OUR_FRIENDS`); the dialog colours the result, both retreat lines and the garrison assault by ONE rule — good news green, bad news red, a war not ours grey — and an unstamped event keeps the France-only colour (`enemy_phase_dialog.THE_COLOURS_KNOW_OUR_FRIENDS`). Driven through the real end turn on the 1805 boot; frame `IQ10_ENEMY_PHASE_T20_2026_10_05.png` (Deroy holding against Archduke John, the result now green). Pins `::TestTheColoursKnowOurFriends`. ⟨SF step=7 · slice 9 · pillar=combat_legibility⟩ |
| ~~**SF7-X27**~~ | P4 | **The last-stand question sat on a box twice its size.** "Teulie is cornered at Milan with 2,840 men, Sire…" — two lines and two buttons on the interrupt popup's fixed 600×360 panel, ~130px of it empty below the buttons. | ✅ **FIXED — slice 9:** after the viewport clamp (which keeps the authored rect as the ceiling) the panel shrinks to its content's height and re-centres, never grows — read once the containers have sorted (`interrupt_popup.THE_QUESTION_FITS_ITS_BOX`). ⛔ The first cut fitted in a `call_deferred` read the frame the text was set, when the label, with no width yet, wraps per character (a 3,328px minimum that frame, 208px two frames later): it never shrank, a source pin passed over it, and the re-shot frame showed the box unchanged — the fit now waits two frames and the pin measures. Driven on the registered popup: opened at the clamp's height, settled at its content's, centred. Pins `tests/test_cx7_predictor_driven.py::TestTheFramesTerminalText::test_the_last_stand_question_fits_its_box` + `::TestTheScreenSays::test_the_interrupt_popup_fits_its_question`; frame `IQ10_INTERRUPT_LAST_STAND_2026_10_05.png`. ⟨SF step=7 · slice 9 · pillar=ui_ux⟩ |
| ~~**SF7-X28**~~ | P4 | **The Formable Nations step opened a blank band above its list.** Its prompt is a fixed two-line quote, laid out like Talleyrand's step-2 assessment (an expanding region). | ✅ **FIXED — slice 9:** step 3 hugs its quote (`diplomacy_wizard.THE_FORMABLES_PROMPT_HUGS_ITS_QUOTE`); EP F3's "steps two and three expand" pin flipped consciously. Pins `::TestTheScreenSays::test_the_formables_prompt_hugs_its_quote` + `tests/test_ep_f3_the_client_layout_pass.py::TestTheWizardWraps::test_step_one_pins_the_prompt_and_step_two_expands`. Frame `IQ10_WIZARD_FORMABLES_STEP3_2026_10_05.png` (a new shot: the step-3 rows rendered from the captured `GET /formables`). ⟨SF step=7 · slice 9 · pillar=agendas⟩ |
| ~~**SF7-X29**~~ | P4 | **The tableau's reserve tail hid its own dead.** A corps the cap could not seat still bled, and its dead rode the side's odometer while the tail said only "+1 corps in reserve" — the figures on the baize did not add up to the total over them. | ✅ **FIXED — slice 9:** the side payload carries `reserve_casualties` (the unseated corps' own dead; a hidden no-show bled nothing) and the tail reads "+1 corps in reserve — 258 lost", right-aligned by its own width (`battle_diorama.THE_RESERVE_NAMES_ITS_DEAD`, both halves). Pins `::TestTheReserveNamesItsDead`. ⟨SF step=7 · slice 9 · pillar=combat_legibility⟩ |
| ~~**SF7-X30**~~ | P4 | **An ally's petition named a different war than the table it sat at.** "The chancery of Bavaria petitions for Tyrol in the settlement of France vs Britain" inside a review headed "France vs Austria + Britain + Russia": the petition read the war's LEADER pair, while the settlement dialogue has named its table by coverage since G4F-7. | ✅ **FIXED — slice 9:** both petition builders name the table as the dialogue does — our side's leader against every covered court (`settlement_offers._petition_table_label`, lever `THE_PETITION_NAMES_THE_TABLE`); the Grant option's "Open the settlement of France vs Britain first (War Detail → …)" keeps the war's own name (a war-scoped surface, G4F-7's rule). Pins `::TestThePetitionNamesItsTable`. ⟨SF step=7 · slice 9 · pillar=diplomacy⟩ |
| ~~**SF7-X31**~~ | P3 | **A garrison that gave way vanished without a word.** A capital's garrison below the collapse line does not fight; the next attack cleared it in silence — the enemy phase read "Garrison: … 5,000 still under arms" and then "Region captured: Milan", and the capture message said the attacker "marches … unopposed". Only a DETACHMENT under the surrender floor was said to lay down its arms. | ✅ **FIXED — slice 9:** the capture says "The last N of the garrison at X give way." and the conquest (or occupation) event carries `garrison_gave_way`, which the enemy phase prints (`CombatExecutor.A_GARRISON_THAT_GIVES_WAY_IS_SAID`); both sides (GR5). Display only — the garrison was already cleared there. Pins `::TestAGarrisonThatGivesWayIsSaid`. ⟨SF step=7 · slice 9 · pillar=combat_legibility⟩ |
| ~~**SF7-X32**~~ | P4 | **Berthier called a tactical victory decisive.** "Decisive" is the game's word for a RESULT — the line above Berthier's prints "Decisive defender victory" or "Defender tactical victory" — and his two-to-one casualty arm used it of the exchange alone. The turn-20 enemy phase: "Result: Defender tactical victory (Deroy victorious)" and, two lines below, "A decisive victory for Deroy!" | ✅ **FIXED — slice 9:** a tactical victory won two to one speaks of the exchange (`won_the_exchange`: "The exchange went Deroy's way, Sire — Archduke John paid twice what Deroy did, though the day decided nothing yet."), naming both commanders and never "we" (Berthier narrates an ally's battle too); a decisive result keeps its bank (`battle_report.THE_DECISIVE_WORD_IS_THE_RESULTS`). Display only — the observation's own rotation draws once either way. Pins `tests/test_sf7_s9_the_frames.py::TestTheDecisiveWordIsTheResults`. ⟨SF step=7 · slice 9 · pillar=narration⟩ |
| ~~**SF7-X33**~~ | P3 | **A refused raid destroys the garrison it cannot take.** In `_execute_attack`'s unopposed branch a capital's garrison under the collapse line (or a detachment under the surrender floor) is cleared BEFORE the raiding-party check (VP-R1 (b)), so a corps under 5,000 attacking such a homeland province empties its garrison and is then refused ("… lies open, but … a raiding party, not an army"): the garrison is gone, the province untaken, the next corps walks in. Found reading the branch slice 9's garrison sentence lives in. | ✅ **FIXED — Score Finish Step 7 slice 10 (the AI's own accounting), October 5, 2026:** the raiding-party question is asked BEFORE the garrison is touched, so a refused raid leaves the garrison standing (`CombatExecutor.A_REFUSED_RAID_LEAVES_THE_GARRISON`; the lever down = the old order). Both sides (GR5): Ney's 3,000 refused at Vienna, Mack's 3,000 at Munich, each garrison intact; an army over the floor still finds the garrison giving way and takes the province. Inert BY CONSTRUCTION on the ambient board — 0 raid refusals at the attack seam in 40 turns (the AI's rungs pre-check the raiding party); the player's typed attack is the road it closes. Pins `tests/test_sf7_s10_the_ais_own_accounting.py::TestARefusedRaidLeavesTheGarrison`. ⟨SF step=7 · slice 10 · pillar=living_balance⟩ |
| ~~**SF7-X34**~~ | P3 | **The AI's stagnation tracker counts a capture as "achieved nothing".** `EnemyAI`'s stagnation block reads only `battle` events for an attack's achievement, so an attack that took a province through a garrison's collapse (`garrison_destroyed` + `conquest` / `occupation_started`) or by an unopposed capture (`conquest`) leaves the marshal idle — the Mode C session's log printed "[STAGNATION] ArchdukeJohn attacked but achieved nothing" twice on the turn he took Milan, and the counter feeds the stagnation-forced actions. | ✅ **FIXED — slice 10:** a capture is an achievement, in ONE predicate (`enemy_ai.attack_achieved_something`: the battle rule unchanged — won, conquered or destroyed — plus `conquest`, `occupation_started` and `garrison_destroyed`; a garrison that HELD is not one), read by the tracker's attack arm (lever `enemy_ai.THE_STAGNATION_COUNTS_A_CAPTURE`). Measured on the 40-turn ambient board: 28 of 63 attack readings change; the P7.5 breaker's reach moves (Britain fires 16 times, not 17; Prussia is reached 69 times, not 71); **`BASELINE_SERIES` byte-identical on all four arms** (no re-record), while the board shifts late — Britain ends turn 40 with 20 provinces (21), the unattended France with 5 (4) — recorded beside the series; M1–M7 byte-identical. Pins `::TestACaptureIsAnAchievement` (the event shapes, the Milan turn, the AST call site). ⟨SF step=7 · slice 10 · pillar=ai_aliveness⟩ |
| ~~**SF7-X35**~~ | P2 | **A war opened by any road but a declaration had no purpose — until the next load gave it one.** `declare_war` gives the defender `defense` (and the aggressor its named purpose), but a cascade, an ally's entry, a rebellion, a defection or a collapsed truce opened its war through `set_diplomatic_state` with NO objectives, and FA-S17-17's load migration — whose docstring claimed the live engine could not create such a war — filled them at the next load. So a saved campaign and the live one disagreed about the war's purpose (the war-detail "No war purpose set" live, a `defense` after a reload; the score's defense ticking switched on by saving). Found when slice 10's board reached Switzerland's rebellion inside the census's twelve turns: the played round trip (`tests/test_serialization_played_world_census.py`) diverged on `war_objectives` for France, Holland and Spain against Switzerland, and the pre-commit hook refused the commit. | ✅ **FIXED — slice 10:** ONE rule, `diplomacy.give_the_war_its_purpose` (FA-D4's ruling, confirmed Sept 23: a pair at WAR with no objective on either side gets `defense` both ways; a pair with any purpose untouched; Europe worlds only, N1), applied LIVE at the war-entry seam in `set_diplomatic_state` for every road but a declaration and the settlement's ARMISTICE→WAR→VASSAL bookkeeping hop (lever `diplomacy.A_NEW_WAR_HAS_A_PURPOSE`), and by the load migration for saves from before it. Measured on the 40-turn ambient board: the live seam purposes 3 wars, `BASELINE_SERIES` byte-identical, provinces unchanged by the lever alone. Pins `tests/test_sf7_s10_the_ais_own_accounting.py::TestEveryWarHasItsPurpose` (a cascade and a rebellion war purposed live, a declaration and the treaty hop left to themselves, a set purpose untouched, the live war's round trip, an old save still migrated, the legacy world purposeless by design) + the census round trip green. ⟨SF step=7 · slice 10 · pillar=diplomacy⟩ |
| ~~**SF7-X2**~~ | P3 | **The muster's expected figure prices an arriving gun corps at nothing; the battle counts him whole.** `_expected_arrival_weight` returns 0.0 for artillery on the claim that an arriving gun "never enters `_get_casualty_participants` and contributes exactly zero to the resolver's committed term" — but the resolver's Gate-4 block appends every adjacent gun that answered to the participants after that function returns, and `_committed_reinforcement_strength(marshal, atk_participants, world)` then sums him at full weight. Measured on the boot board with Lannes staged as a gun corps and every promised corps arriving (`Ney, attack Mack`): expected 54,544 against 84,266 massed with the field read down, 61,882 against 88,684 up — the ceiling and the battle agree to the man, the expectation is a gun short. The enemy AI reads the same weight in its defender muster (`enemy_ai` → `_committed_reinforcement_strength(expected_at=…)`), so a French gun beside a target is priced at nothing there too. The muster row's own copy says the same false thing ("a gun never relocates (its weight is 0 in the sum and a coordination bonus instead)"). | **FIXED in Step 7 slice 3b** (`combat_executor.AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL`; pins `tests/test_sf7_3b_the_gun_and_the_purse.py::TestTheGunIsWeighedByHisRoll`): an arriving gun is weighed by his own arrival roll and his muster row states his odds; measured with Lannes as a gun corps and every promised corps arriving, expected 61,882 → 84,005 against 88,684 massed, the ceiling unchanged and still equal to the battle's figure; `BASELINE_SERIES` byte-identical with the reach counted (0 gun weights read on the ambient board in forty turns — `tools/_sf7_3b_series_arms.py`). **Conscious re-seats (the hook found four, each attributed to the lever by re-running it down):** PT-A's `test_artillery_is_priced_at_zero_because_it_never_relocates` asserted the premise this row measured false — flipped to `test_an_arriving_gun_is_weighed_by_his_roll` (the roll-weighted share up, 0.0 down); three AI fixtures on the legacy world parked Drouot's 25,000 guns beside the battle (at Paris beside Belgium; `_legacy` parks the roster at Bordeaux, which borders Paris) and the AI now prices him as the battle counts him, so an aggressive Uxbridge retreats at 0.64 and a cautious Wellington keeps his free blow — honest on that board; each test's subject is not the gun, so Drouot is sent to Marseille (`test_enemy_ai_behavior.py::…::test_encirclement_aggressive_attacks`, `test_fa_slice4_…::TestTheCounterPunchIsPriced`, `test_fa_slice4r_…::TestTheFieldPricesTheTargetToo`); the GR5 half is pinned where they found it (`TestTheAISeesTheGunToo`: the counter-punch declines with the gun next door, strikes with the lever down). Was homed: Score Finish Step 7, **slice 3b** (found by slice 3's lockstep probe; slice 3 had to land alone): weight an arriving gun by his own arrival roll like every reinforcer (he rolls the same die), behind a lever; the muster row states his odds; the docstring and the row's copy corrected; `BASELINE_SERIES` measured with the reach counted (no gun corps boots on the 1805 board — six sit in `marshal_pool`). Done-when: with a gun corps among the promised, the expected figure moves with his arrival odds and the census rule (ceiling == massed when every promised corps fights) holds. ⟨SF step=7 · slice 3b (found by slice 3) · pillar=combat_legibility⟩ |
| ~~**SF7-X3**~~ | P3 | **"What can I do" names nothing to buy while the whole army campaigns abroad.** The counsel's build line (`counsel._build_terms`) looks only at `_first_own_region_with_a_corps` — the first French province with a French corps standing on it — though building needs no corps (`region.can_build` is the gate; the executor reads no marshal). Found by slice 3's exit flipping economy C6 ✓ → ✗: on the field-read board the commanded army stands in Franconia, Swabia, Munich and Tyrol at turns 20 and 30 of CMD-H, so the counsel offers four field orders and no purchase against chests of 32,570 and 51,120 gold (the levy line is honest — a levy needs a corps on our soil — and refuses on every corps: "not our soil"). The desk already holds the right finder: `question_desk._first_own_region_that_can_build` (capital first, then by income). Pre-existing on every tree; slice 3's course only exposed it. | **FIXED in Step 7 slice 3b** (`counsel.THE_BUILD_LINE_NEEDS_NO_CORPS`; pins `tests/test_sf7_3b_the_gun_and_the_purse.py::TestTheBuildLineNeedsNoCorps`): with no corps on our own soil the build line reads the desk's finder (`question_desk._first_own_region_that_can_build`, capital first, then by income) — a corps province, when there is one, still comes first, so the line is byte-identical whenever a corps stands at home; CMD-H turns 20 and 30 now name a supply depot (300g) and a fortification (400g) in Paris, and **economy C6 re-reads ✗ → ✓** (9 of 9 samples on the CMD arms). Display only (the AI reads no counsel; 0 corps-free build lines served on the ambient board). Was homed: Score Finish Step 7, **slice 3b**: the counsel's build line reads the desk's finder (ONE finder for both surfaces, capital first), behind a lever; display only (the counsel is the player's). Done-when: CMD-H turns 20 and 30 on the field-read board name a priced building, and economy C6 re-reads on the CMD arms. ⟨SF step=7 · slice 3b (found by slice 3's exit) · pillar=economy⟩ |
| ~~**SF7-X4**~~ | P3 | **The glory gate read stale coordination stamps.** VP-R1 (c)'s `muster_odds` claims to be "the band `_build_muster_preview` would print … so a gate that reads it cannot disagree with the screen" — but since SF-CL-1 the preview prints its band under `_priced_coordination` (the context the resolver will stamp), while `muster_odds` read the attack modifier with whatever transient coordination fields the last battle had left. Measured on the boot board with the field read down: a 25,000-man Archduke John read 'even' at the gate while 20,000 and 30,000 read 'unfavorable' — the preview 'unfavorable' on all three; with the field read up, Murat on Mack read 'even' at the gate against the preview's 'favorable' (VP-R1's own drift pin caught it). The gate is the jealousy glory hunt's, both boards (GR5). | **FIXED in Step 7 slice 3** (`combat_executor.THE_GATE_READS_THE_PREVIEWS_CONTEXT`): `muster_odds` reads under the same priced context as the preview; on the old (lever-down field) reading the lever alone is byte-identical on the series board (46 gate reads, the same band either way), on the field read it moves three reads after turn 32. ⟨SF step=7 · slice 3 (found building §6 row 16) · pillar=ai_aliveness⟩ |
| ~~**SF7-X1**~~ | P3 (instrument) | **The driver signed armistices with courts on its own `--decline-from` list.** When several envoys arrive in one turn, an answer to the first is refused as stale ("Sire, another matter has arrived since — this concerns Hanover") and the refusal re-carries the STORED dialogue, whose court lives in `context.source_nation` (and, on an incoming proposal, `target_nation`) — fields `_court_of` never read. The re-carried envoy named no court, the decline list did not fire, and the accepting dial signed: Hanover, Portugal or Naples on 8 of the 12 conquest-road draft runs, and **Step 6's own committed NAV1-H arm accepted Portugal's armistice on turn 20 under `--decline-from Portugal`**. | **FIXED in Step 7** (`tools/playtest_driver.py::_court_of`, lever `THE_DECLINE_LIST_READS_THE_STORED_SHAPE`): the stored shape's `context.source_nation` (stamped only by the AI's envoy producers) and an incoming proposal's `target_nation` are read; the player's own confirms — whose `target_nation` is the court France writes TO — stay untouched. **Step 6's table reproduces with the fix** (NAV1 re-read on the three seeds: peaks 14 / 12 / 13, SHUT OUT historical t11 and marengo t13–15, Spain's exit t16): Lisbon in French hands counts Portugal's ports either way (NV-10), so the stray armistice moved no port. ⟨SF step=7 · found in passing · pillar=none⟩ |
| ~~**SF7-X36**~~ | P2 (instrument) | **Narration F1's reader counted a turn event as the morning's headline.** When the morning carried no headline, the driver's call site passed the first "text" a breadth-first `dig` reached — a turn event (*"DISPATCH: Supply cost you 3,331 men, at Swabia."*) — and `score_run.r_narration_F1` counted any dispatch record as a headline. The baseline read *"0/40 turns without a headline"* on all three commanded arms while its own records hold **3 / 25 / 30** turns with no headline class (the spec's own "58 of 120"); Step 7's start reading on `bc93ffaf` held **4 / 0 / 11**. Found by the Step 7 exit, reading the archives before the run. | ✅ **FIXED — the Step 7 exit, October 5, 2026:** the reader reads a run whose dispatch records carry classes by the class (`score_run.THE_HEADLINE_IS_ITS_CLASS`; a pre-SF-M archive keeps the old reading), and the driver records the headline's own text or `(no headline)` (`playtest_driver.THE_DIGEST_RECORDS_THE_HEADLINE_ITSELF`, the call site lifted into `_record_morning_headline`). Both readings of the exit were checked with the corrected reader, so narration F1 reads **✗ on the start and the baseline** — the item was never met; the instrument could not see it. Pins `tests/test_step7_exit_fixes.py` (9, incl. the baseline archive read by the corrected reader: 3 / 25 / 30). ⟨SF step=7 · the exit · pillar=narration⟩ |
| ~~**SF7-X37**~~ | P2 | **France's own truce ending never reaches the morning headline.** `diplomacy._process_armistice_expiration` returns its events into the turn's tactical list and queues a rail row; the headline builder reads only `world.event_log`, so a truce collapsing back into war, or ripening into peace, is told on the rail and never led. Measured on Step 7's start reading: CMD-H turn 15 led *"Russia moves toward war with Sweden"* the morning *"The armistice between Austria and France has collapsed. War resumes!"*; CMD-M turn 13 led Prussia's war on Hanover over France's own resumed war with Russia; CMD-M turn 24 — the morning the Russian truce became a peace — carried no headline at all. | ✅ **FIXED — Step 7b, October 5, 2026:** the front page reads the turn's queue — a truce collapsing leads as `war_touches_us` ("Sire — the truce with Russia has collapsed — the war resumes where it stood."), one ripening into peace as `peace_signed` (`dispatch.A_TRUCES_END_IS_NEWS`, `_armistice_expiry_candidates`). Measured on the exit: the morning the Austrian truce collapsed (CMD-H turn 38) led with Lannes's 32-turn arrears at Step 7's exit and now leads with the collapse. Pins `tests/test_sf_page_the_front_page_of_the_peace.py::TestTheTruceEndingIsNews`. ⟨SF step=7b · SF-NAR-1 · pillar=narration⟩ |
| ~~**SF7-X38**~~ | P3 | **Raw nation keys on the diplomatic rail.** Two dispatch templates interpolate the raw tag where every sibling uses the PR-2 `_display` suffix: `diplomatic_treaty_signed` (*"PapalStates and France have signed the Open Borders Agreement"*, *"Ottoman and France …"*) and `blockade_begins` (*"Britain closes KingdomOfItaly's ports"*). Found reading Step 7's start reading (CMD-H turns 2–4, CMD-M turn 39). | ✅ **FIXED — Step 7b, October 5, 2026:** both named templates take the PR-2 `_display` forms ("Sire — the Papal States and France have signed …", "BLOCKADE: Britain closes the Kingdom of Italy's ports"), and so do the rows the front page now leads with — the armistice pair, the relation shift, allegiance in play, the paymaster, the laws abroad, war exhaustion, the enemy commission, unrest and the auto-downgrade (its states by `STATE_DISPLAY`); a promoted row's camelCase court is named at the page's own seam (`_front_page_prose`). Pins `…::TestTheRawKeysAreNamed`, `…::TestEveryMorningHasAFrontPage::test_a_raw_court_tag_is_named_on_the_page`. ⟨SF step=7b · SF-NAR-1 · pillar=narration⟩ |
| ~~**SF7-X39**~~ | P3 (instrument) | **Living balance C5's probe reads the headline line only.** The frozen item says a sponsorship against France or a newly qualifying great power *"leads or sub-beats the next dispatch"*, and that *"each quoted keep-out lever flips `qualifies_for_coalition(relation_shift=)`"*; the probe (`_score_probes.living_balance_c5_front_page`) reads only the dispatch record's first line — the driver never recorded the sub-beats — never reads a newly qualifying court, and accepts any keep-out phrase without the flip. Found reading the probe for Step 7b. | ✅ **FIXED — Step 7b, October 5, 2026:** the driver records the whole page (`playtest_driver.THE_DIGEST_READS_THE_WHOLE_PAGE`: `headline_text`, `sub_beats`, `league_rows`, `league_line`), and the probe (`_score_probes.THE_PROBE_READS_THE_WHOLE_PAGE`) reads it for every sponsorship against France and every great power newly free to join after the peace, and checks every quoted keep-out lever on the arms' saves against `qualifies_for_coalition(relation_shift=)`. Measured on the three commanded arms: 1 sponsorship and 4 newly free great powers, all on the page; 22 quoted levers, 22 flip the gate — living balance C5 ✗ → ✓. Pins `…::TestTheInstrumentReadsTheWholePage`, `…::TestTheDrivenArms`. ⟨SF step=7b · SF-LB-3 · pillar=living_balance⟩ |
| ~~**SF7-X40**~~ | P3 (instrument) | **Ending F2's reader took a battle report for the Verdict.** `score_run._blocks_with` matches without case, so `battle_report`'s observation *"The reinforcement arrived, Sire. The verdict of the field went against us regardless."* read as THE VERDICT: Step 7's start reading took a turn-21 battle line on the Verdict arm for its ending and read F2 ✗ while the arm reached the turn-44 register. Found by the Step 7 exit, attributing the flip. | ✅ **FIXED — the Step 7 exit, October 5, 2026:** the ending is matched by its own capitals (`score_run.THE_VERDICT_IS_THE_ENDINGS_OWN`); ending F2 reads ✓ on both trees. Pins `tests/test_step7_exit_fixes.py::TestTheVerdictIsTheEndingsOwn` (incl. a pin on the battle copy that caused it). ⟨SF step=7 · the exit · pillar=ending⟩ |
| ~~**SF7-X41**~~ | P3 (instrument) | **Command C5's reader expected a spend from a free order.** The reader required every carried order on an order turn to spend an action, but the general retreat is free by the game's own rule (FA-R3): typed_road's turn 9 carried `ok retreat` (its attacks refused out of range) and spent nothing, so C5 read ✗ on Step 7's start and final trees — and had never been read since the baseline (the TYPED arm ran at no exit in between); the baseline's board refused that retreat (no corps in danger) and read ✓. Found by the Step 7 exit. | ✅ **FIXED — the Step 7 exit, October 5, 2026:** a carried retreat expects no spend (`score_run.THE_FREE_ORDER_SPENDS_NOTHING`); a carried attack that spent nothing still fails. Pins `::TestTheFreeOrderSpendsNothing` (incl. the premise driven through the real parser and executor: the general retreat leaves the actions where they were). ⟨SF step=7 · the exit · pillar=command⟩ |
| ~~**SF7-X42**~~ | P3 | **The action pre-gate named neither the man nor the order.** *"Not enough actions! Need 2, have 1."* — W9's class one gate over; five of the HOLD arm's misses were this sentence (SF-V9's closing note left the arm's reading to "the session exit"). Found by the Step 7 exit's re-read of the HOLD arm. | ✅ **FIXED — the Step 7 exit, October 5, 2026:** when the order names one of our marshals the sentence says what waits — *"Not enough actions! Need 2, have 1 — Davout cannot hold Lorraine today."*, *"… — Massena cannot hold Milan today."* (the target as the board names it), and the administrative pool's *"… Soult cannot raise his levy today."* — and the Substitutes chip quotes the gate's own words (`economy_executor.substitute_quote`, CN-4's drift pin) (`executor.THE_SPENT_DAY_NAMES_THE_ORDER`, `spent_day_sentence`); the head is unchanged, so every reader of the old words still finds them. Pins `::TestTheSpentDayNamesTheOrder` (driven at `POST /command` on the 1805 boot). ⟨SF step=7 · the exit · pillar=command⟩ |
| ~~**SF7-X43**~~ | P3 | **"Back Prussia's quarrel with Austria" was not read as a sponsorship.** The HOLD arm's blind order *"Have Talleyrand back Prussia's quarrel with Austria - a couple of hundred gold a turn."* answered *"Sire, I await your instructions regarding Prussia"* — the one order SF-V9's worklist left unread (the row named "the sponsorship idiom"; slice 5b's closing note did not). | ✅ **FIXED — the Step 7 exit, October 5, 2026:** backing (bankrolling, funding, financing) a court's quarrel, cause, claim or grievance with another court is `sponsor <court> against <court>`, both courts known to the world (`parser.A_BACKED_QUARREL_IS_A_SPONSORSHIP`, in the plain-forms rewrite beside the pledge); the verb's own executor then prices it — the HOLD line is refused with Talleyrand's reason (Prussia's design is aimed at Hanover), `back Prussia's quarrel with Hanover` is granted at 200 gold a turn. Pins `::TestABackedQuarrelIsASponsorship`; corpus row `sf7-exit-a-backed-quarrel-is-a-sponsorship` (900 of 900). ⟨SF step=7 · the exit · pillar=command⟩ |
| ~~**SF7-X44**~~ | P3 (instrument) | **The ONE judge could not read four of the board's own refusals.** On the HOLD arm: the levy a named marshal raises where he stands (§6 row 19's refusal), the town that holds no building, a retreat for a marshal in no danger, and the design a sponsorship would arm aimed at another court (SF7-X43's verb). Found by the Step 7 exit's re-read of the HOLD arm. | ✅ **FIXED — the Step 7 exit, October 5, 2026:** `_score_probes.BOARD_GATE_RX` reads all four; the committed census records were grepped first — the fresh record holds one *"rural regions don't support buildings"* read `as_meant`, so the town refusal is matched by its own words and every committed record re-reads unchanged (pinned over all three). Pins `::TestTheJudgeReadsTheBoardsRefusals`. **With X42–X44, command C3 reads 20 of 20 on the final tree** (9 of 20 on `bc93ffaf`). ⟨SF step=7 · the exit · pillar=command⟩ |
| ~~**SF7-X45**~~ | P3 | **The alarm forecast read the clock one turn early.** `advance_turn` moves the turn on BEFORE the coalition tick, but RS-16's `forecast_alarm_tick` read the Armed Peace's quiet count, the two expiring markers, the DG-4 memory and the agenda / Congress grudges on today's clock — measured: at 19 quiet turns the forecast said 45 and `advance_turn` gave 49 (the fuse lit a turn before the forecast said it would), and a marker on its last turn was counted live by the forecast and dead by the tick. The pin (`test_rs16s_forecast_equals_the_tick`) ticked without advancing the turn, so it could not see either. Found building the league's forecast, which steps the same tick. | ✅ **FIXED — Step 7b, October 5, 2026:** the forecast reads every clock-dependent producer as the next tick will (`coalition.THE_FORECAST_READS_THE_TICKS_CLOCK`; `armed_peace_reading(world, ahead=)`, `hegemon_quiet_turns(..., ahead=)`, a `turn=` on the DG-4, agenda and Congress grudge producers — the tick's own calls unchanged). Pins `…::TestTheForecastReadsTheTicksClock`. ⟨SF step=7b · SF-LB-3 · pillar=ending⟩ |
| ~~**SF7-X46**~~ | P3 | **"The safe passage runs out in 0 turns."** The road-home warning's figure is the SLACK — turns to spare once the march home is counted (`withdrawal._warn`'s surplus) — and both the headline and the rail told a corps with no turn to spare that its passage had run out. Found reading Step 7b's own pages (CMD-H turn 38). | ✅ **FIXED — Step 7b, October 5, 2026:** "the safe passage leaves no turn to spare — he must march today" / "leaves 2 turns to spare" (`dispatch.THE_PASSAGE_COUNTS_ITS_SLACK`, `withdrawal.THE_PASSAGE_COUNTS_ITS_SLACK`). Pins `…::TestThePassageCountsItsSlack`, `…::TestTheEdges::test_the_withdrawal_warning_counts_its_slack`. ⟨SF step=7b · SF-NAR-1 · pillar=narration⟩ |
| ~~**SF7-X47**~~ | P3 | **The first morning's TODAY list read as a plan it is not.** The boot briefing printed "Orders the board will take at once:" over four orders that, typed top to bottom on one boot, refuse each other: Ney's attack draws Davout into the field (his march: "Davout is engaged with Mack and cannot begin a strategic march"), and its materiel bill leaves the levy unpaid ("Need 846 gold, have 532" — the levy falling to Soult where the line quoted 741g under Davout); the levy and the depot alone ask 1,041g of an 800g treasury. Each order alone is carried out (EP F1's contract; first contact C5), and the sequence note had ridden every reading since the baseline as "reported, not scored". Found reading the Step 7b exit's re-check: the note's count moved between two checks of the same arms (2 refusals, then 1), because the attack's arrivals and its battle are rolled. | ✅ **FIXED — Step 7b, October 5, 2026:** the backend owns the header and both screens render it — "Orders the board will take at once — choose among them; they share one treasury and one army:" (`dispatch.THE_TODAY_LIST_IS_A_CHOICE`, `TODAY_ORDERS_HEADER`, the TODAY payload's `orders_header`, read by `main.gd` and `dispatch_view.gd`). The orders are unchanged, so first contact C5 reads as before. Pins `tests/test_sf_page_the_front_page_of_the_peace.py::TestTheTodayListIsAChoice`. ⟨SF step=7b · the exit · pillar=first_contact⟩ |
| ~~**SF7-X48**~~ | P3 | **The alarm wore two names.** The Balance of Europe tab printed "Threat Level: 45 / 100 [MODERATE]" — its own severity band (LOW < 30 ≤ MODERATE < 60 ≤ HIGH < 80 ≤ CRITICAL) — beside a dispatch reading "Threat: 45/100 [Murmurs]"; the dispatch's coalition section, the desk and the advisory all name the alarm by `coalition.get_threat_tier` (Calm / Tension / Murmurs / Brewing / Formed, the Congress's lowered gate included). The two bands even disagree on where a level sits (40–59 is MODERATE and Murmurs; 60 is HIGH and Brewing). And the dispatch view and the terminal coloured the tier red only on "CRITICAL" / "HIGH", which the dispatch never sends — a brewing league printed in amber. Found shooting Step 7b's frames (the dispatch and the tab side by side). | ✅ **FIXED — Step 7b's frames, October 5, 2026:** ONE name, `coalition.threat_tier_name(world, level)` (`get_threat_tier` with the player's own formed league and `brewing_gate`); the tab carries it as `threat_name` and prints it in the bracket, its severity band still colouring the bar and pulsing at 80 (`diplomatic_ledger.THE_ALARM_HAS_ONE_NAME`); the IQ-2 collapse line names it too; the dispatch view and the terminal colour Brewing and Formed red. Pins `tests/test_sf_page_the_front_page_of_the_peace.py::TestTheAlarmHasOneName` (45, 65, a formed league, the Congress's gate at 40). ⟨SF step=7b · the frames · pillar=ui_ux⟩ |
| ~~**SF7-X49**~~ | P3 (instrument) | **The IQ-10 runner dropped a row's own steps when the row named a tab.** `tools/iq10_run_captures.py` `build_spec` REPLACED `steps` with the tab switch, so a ledger shot that must scroll (THE NEXT LEAGUE, the first row ever to carry both) photographed the tab's top in silence — the frame passed every check and showed the wrong thing at scale 2.0. Found shooting Step 7b's frames. | ✅ **FIXED — Step 7b's frames, October 5, 2026:** the tab switch runs first, then the row's steps. Pins `tests/test_sf_page_the_front_page_of_the_peace.py::TestTheFramesRunnerKeepsTheRowsSteps`. ⟨SF step=7b · the frames · pillar=ui_ux⟩ |

## Score Finish Step 6 — found in passing, October 4, 2026 (**2 rows, both FIXED in the step** — SF6-X1 found playing the descent arm's re-stage, SF6-X2 found by the exit; rules `SYSTEMS_REFERENCE.md` §92.2 / §92.4; pins `tests/test_sf_nav1_the_strangulation_played.py::TestSailingEndsTheStandingOrder` + `::TestTheSeaArmReachesAYard`)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SF6-X1**~~ | P3 | **A confirmed sea expedition left the marshal's standing order standing.** Oudinot, marched to the Normandy yard under a MOVE_TO and landed at Munster the next turn, "marches to Ulster. 7 regions to Normandy" — the order that brought him to the yard walked him off his own beachhead until the Royal Navy barred the crossing at the Highlands. Sailing is not one of the executor's strategic-override verbs, and the expedition resolver never touched the order. | **FIXED in Step 6:** `naval_executor.SAILING_ENDS_THE_STANDING_ORDER` — a CONFIRMED expedition (landed, intercepted or turned back) ends the corps' standing order and the interrupts it raised; the QUOTE touches nothing, so "Stand down" leaves the march as it was. GR5 (the AI's expeditions ride the same executor) — measured reach on the series board: 2 AI sailings in 40 turns (Paget to Lisbon turn 5, Wellesley to Piedmont turn 10), neither carrying a standing order, so `BASELINE_SERIES` is byte-identical by construction. ⟨SF step=6 · found in passing · pillar=naval⟩ |
| ~~**SF6-X2**~~ | P3 (benchmark precondition) | **The SEA arm's landing never reached a yard — naval F2 read ✓ at the baseline and ✗ since, unseen because no exit re-ran SEA.** The board drifted under the arm: Paget's Peninsula corps (landed at Lisbon on turn 5 on both trees) now meets Oudinot at Guyenne on his loop-5 road to the Bordelais yard and fights him twice, so Oudinot reaches the yard on loop 9 — after both landing lines (`Oudinot must stand at one of our yards`), and the digest read SCRIPT PRECONDITION. Measured on Step 5's tree (`d1018208`) too — not caused by Step 6. | **FIXED in Step 6:** the arm marches Oudinot to the NORMANDY yard (one march from Paris; the descent arm's yard): the loop-7 quote is answered "Sail" by the driver and intercepted (−1,500), the confirmed line lands 3,500 at Munster on loop 8; naval F2 reads ✓ again. ⟨SF step=6 · found by the exit · pillar=naval⟩ |

## Score Finish Step 5 quick check — October 4, 2026 (**13 rows — SF5-RV1 … SF5-RV12 FIXED in the quick-check commit; SF5-RV13 OPEN, homed to Step 7** — two read-only reviewers attacked Step 5 at `fe720296` after it landed: one the VD-C contingent lifecycle, one the slice's riders; every finding reproduced on the shipped board before it was fixed; rules `SYSTEMS_REFERENCE.md` §90.12; pins `tests/test_sf5_quick_check_2026_10_04.py`, each flipping with its lever; `BASELINE_SERIES` and M1–M7 byte-identical)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SF5-RV1**~~ | P2 | **The lord filled his client's ranks for free.** A serving contingent is outside its lord's establishment BY NAME (`calculate_turn_upkeep` skips it), and nothing stopped the lord levying into it: the typed `Dumonceau, recruit infantry` drew 3,000 men from France's pool for 872g that France's upkeep, force limit, levy price and Grande Armée surcharge never counted; the region panel's unnamed levy and the AI's weakest-corps pick chose a contingent on their own; at the stand-down the lord's men went to the SATELLITE's pool, and a contingent bled below half and topped back up came home "crowned" (+8) instead of decimated. | **FIXED (the Step 5 quick check, October 4, 2026):** `contingent.THE_LORD_DOES_NOT_FILL_THE_CLIENTS_RANKS` — ONE predicate (`contingent.lord_fill_refusal` / `levy_passes_over`): a named levy or substitutes into a serving contingent is refused free ("Dumonceau's men belong to Holland, Sire — it raises and pays them"), the levy's own selectors pass him over with the reason named (`ready_marshals_near(for_levy=True)` at all six levy sites; the combat auto-pick keeps him), the market never names him, and the AI's admin pick skips him (GR5). Pins `tests/test_sf5_quick_check_2026_10_04.py::TestTheLordDoesNotFillTheClientsRanks`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV2**~~ | P2 | **A renewed war left the contingent marching home.** When the shared war resumed during the walk home the record flipped back to "serving" but the satellite's own home order stood: the AI's P1.2 road-home rung (which reads only the order's marker) walked an AI lord's contingent back to its capital for the whole renewed war, and the player's kept marching under an order he never gave — the hazard R10 rejected. | **FIXED:** `contingent.THE_RENEWED_WAR_RECALLS_THE_COLOURS` — the satellite's home order is withdrawn (interrupts cleared) with a beat ("The war is renewed — Dumonceau's contingent halts its march home and awaits the orders of France"); an order the LORD gave stands. Pins `TestTheRenewedWarRecallsTheColours`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV3**~~ | P2 | **The raise beat leaked an unseen rival lord's army.** "The nearest host is Archduke Charles at Carniola" rode an AI satellite's raise line, and the end-turn fog filter checked only the muster province (measured with the Kingdom of Italy transferred to Austria: France had no intel on Carniola). | **FIXED:** `contingent.THE_RAISE_BEAT_KEEPS_THE_FOG` — the host's name and province are named only for the player's own lord or where the player sees the host (PARTIAL+, the captive rule); the event's `host` key follows the line. Pins `TestTheRaiseBeatKeepsTheFog`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV4**~~ | P3 | **Any tactical order dodged the kept-from-home bleed.** The executor's strategic override cancels the home march on `fortify` / `drill` / `move`; with the order gone `contingent_kept_from_home` read False, and the satellite re-issued the march at its next pass — so the lord kept the contingent at the front with no −2 a turn until the eight-turn fallback. | **FIXED:** `contingent.THE_OVERRIDE_KEEPS_THEM_FROM_HOME` — the override stamps the record (`note_lord_override`, `kept_turn`) and the next tick charges the bleed once while the road stays cancelled; a REFUSED override restores the home order (SR5B-1) and costs nothing. Pins `TestAnOverrideKeepsThemFromHome`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV5**~~ | P3 | **A conquered satellite's contingent was "recalled" into a court that no longer existed.** The reconciliation read the deleted row as a recall: "The Kingdom of Italy recalls its contingent — Teulie leads 7,500 of 7,500 men home", the men credited to the pool of a nation holding no province. | **FIXED:** `contingent.THE_FALLEN_CROWN_DISBANDS_ITS_MEN` — a contingent whose satellite holds no province disbands where it stands (`contingent.disband`: no pool credit, no tombstone, no homecoming judged; "The Kingdom of Italy has fallen — Teulie's contingent has no court left to serve, and its 7,500 men disband"). Pins `TestAFallenCrownDisbandsItsMen`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV6**~~ | P3 | **A contingent that went home was reported fallen.** `stand_down_marshal` left other marshals' orders aimed at him standing, so a SUPPORT on Dumonceau broke with the strategic processor's "Dumonceau has fallen" beside the homecoming beat. | **FIXED:** `WorldState.stand_down_marshal` cancels every strategic order aimed at the departing general (the elimination idiom, interrupts cleared). Pin `TestAnOrderAimedAtHimEndsWithHim`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV7**~~ | P2 | **SF5-X2 guarded only the typed answer; the popup button still destroyed the decision.** `POST /strategic_response` (what `interrupt_popup.gd` and the driver send) ran the answer under a standing hard stop; the hard stop's own diplomacy gate refused the attack and the refusal ended the order and cleared the interrupt (measured: `declare war on Prussia` staged, then Attack Anyway — 0 battles, interrupt and order gone). Reachable in the client: an end turn can raise both a deferred hard stop and an interrupt, and the interrupt popup shows first. | **FIXED:** the endpoint reads `A_HARD_STOP_OUTRANKS_AN_INTERRUPT` too — nothing is relayed, the refusal names the waiting dialogue and its answers, and the interrupt waits. Pins `TestThePopupButtonWaitsOnAHardStop`. ⟨SF step=5 · the quick check · pillar=command⟩ |
| ~~**SF5-RV8**~~ | P2 | **R12 missed the literal personality's fallback.** When `find_jealousy_target` answers None — always, for a client's general — the literal branch fell back to the top of the lord's ladder, and the restlessness warning was unfiltered: Deroy, assimilated from Bavaria, turned jealous of Ney after three sidelined turns, with the derived −1 relationship and the literal's mechanical expression. | **FIXED:** the jealousy trigger loop and the restlessness warning skip `contingent.is_clients_general` outright. Pins `TestNoClientsGeneralIsJealous` (staged as measured: Ney marching each turn so the sidelining counter climbs; the lever-down arm makes Deroy jealous on turn 3). ⟨SF step=5 · the quick check · pillar=marshal drama⟩ |
| ~~**SF5-RV9**~~ | P3 | **The SF5-X1 re-prompt was built outside the response contract.** It drained the popup queue (the interrupt route renders only its own table, so a queued sabotage or rebellion popup was lost), dropped the FA-49 option costs (attached after the builder ran — a cannon-fire Hold Position's −3 trust disappeared), and let go a CR-7 relayed tail still waiting behind the interrupt. | **FIXED:** `main.A_QUESTION_REPROMPT_CONSUMES_NOTHING` — the re-prompt rides the non-draining refusal builder with the interrupt passed in (so its costs are stamped) and the relayed tail is put back to wait for the answer. Pins `TestTheRepromptConsumesNothing`. ⟨SF step=5 · the quick check · pillar=command⟩ |
| ~~**SF5-RV10**~~ | P3 | **France's satellites began courting the clients of France's allies.** Once IQ7-X1 walked every lord, the lord's-ally guard read only the courtier's OWN treaties: with Spain (France's ALLY) lord of Portugal, Holland courted Portugal for −5 — both inside France's bloc. | **FIXED:** `vassal.A_SATELLITE_COURTS_AS_ITS_LORD` — `courtier_is_the_lords_ally` also spares a target whose lord is the courtier's LORD's ally (the same-house case stays the courting cap's guard, under its own lever). Pin `TestASatelliteCourtsAsItsLord`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV11**~~ | P3 | **The IQ7-X3 hint memory outlived the row.** `vassal_hint_spent` was touched only by the loyalty tick, so a court released (or broken, or conquered) and re-vassalized later rode its first fall silent. | **FIXED:** `vassal.THE_HINT_MEMORY_FOLLOWS_THE_ROW` — the loyalty pass drops the mark of any court that is no satellite, and `transfer_vassal` re-arms it (a new lord, a new account). Pins `TestTheHintMemoryFollowsTheRow`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV12**~~ | P3 | **A rival lord's satellite wavering reached the player's terminal.** The cascade event carried no nation, marshal or location key, so the end-turn fog filter kept it as a neutral alert ("Saxony is wavering! The war against France shakes their loyalty" for an Austrian-lorded Saxony), and its prose printed raw tags. | **FIXED:** `vassal.THE_CASCADE_LINE_KEEPS_THE_FOG` — the event carries its lord (the player's own web always shows) and the satellite's capital (another lord's only where the player sees it), and the line speaks display names. Pins `TestTheCascadeLineKeepsTheFog`. ⟨SF step=5 · the quick check · pillar=vassals⟩ |
| ~~**SF5-RV13**~~ | P3 | **An emphatic order reads as a question.** The SF5-X1 question test (`dialogue_routing.line_asks_a_question`) treats a rhetorical tail as the line's mood: "hold, do as I say", "attack, what are you waiting for" and "do what I say: attack" now order nothing where they executed as meant before the fix (plain answers and the buttons' labels are not misread). | **OPEN — homed to Step 7's SF-CMD-2** (`SCORE_FINISH_SPEC.md` §3 Step 7): an order word leading the line followed by a rhetorical clause answers the interrupt; a question that only names an option still orders nothing. Done when the four phrasings answer as meant at `POST /command` with the SF5-X1 pins green. ⟨SF step=7 · SF-CMD-2 · pillar=command⟩ ✅ **FIXED — Score Finish Step 7 slice 2 (SF-CMD-2's head), October 4, 2026:** `clause_guards.strip_emphasis` (lever `AN_EMPHATIC_ORDER_IS_AN_ORDER`) — a CLOSED list of emphatic clauses ("what are you waiting for", "do as I say", "do what I say", "that's an order", …), each a whole clause between separators, is removed before the question tests run, ONLY when an order verb remains; read by `is_question`, by `dialogue_routing.line_asks_a_question` (the interrupt answer) and by the parser before its readers. Measured on Ney's bad-odds interrupt: `attack, what are you waiting for` (with and without "?") and `do what I say: attack` fight; `hold, do as I say` holds; on the general road `Ney, do as I say and attack Mack` attacks (it had the desk's shrug — the same class, found in the slice). CRT-3 holds: `what are you waiting for?` and `should we attack, what are you waiting for` still order nothing. pins `tests/test_crt6_the_retreat_is_a_word.py::TestTheGuardIsSometimesANoun` + `::TestAPositionIsNotAPlace` and `tests/test_sf_cmd2_the_head.py`; corpus `sfcmd2-*`; sweep `tools/_sweep_sf_cmd2_head.json` 13 → 13 killed; rules `SYSTEMS_REFERENCE.md` §93.2. |

## SF-CMD-1 census worklist — filed October 3, 2026 (**9 rows W1 … W9, ALL FIXED in part (ii) the same day — the held-out census's classes, each a parser or desk gap measured on the boot board; none executed a line the player did not mean**; memo `docs/audits/UNREHEARSED_CENSUS_2026_10_03.md`; records `docs/audits/unrehearsed/2026_10_03_{keyless,keyed}.json`; part (ii) of SF-CMD-1 builds them, with CRT-8/CRT-9 — `SCORE_FINISH_SPEC.md` §3 Step 4)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SF-CMD-1-W1**~~ | P2 | **The desk shrugs 114 of 150 natural questions** (keyless; 113 keyed — the model is never asked a question). The classes: money ("what's our net", "what does recruiting infantry cost", "why is our upkeep so high"), odds and what-ifs in natural phrasing ("what are the odds if Ney attacks Mack", "what if Mack attacks Davout"), marshal attributes ("what is Ney's trust", "what does Davout's ability do", "is anyone fortified"), naval ("how many ships do we have", "is the Channel open"), diplomacy ("is Prussia against us", "who leads the coalition", "would Austria accept peace"), the rules ("what does fortify do"), the map ("what terrain is Swabia", "how many provinces do we hold"), the calendar, last turn, the ground, counsel. The pointer-to-a-screen reply is the shrug one register over. | **FIXED in SF-CMD-1 (ii) / CRT-9, Oct 3, 2026:** `backend/ai/state_desk.py` — the desk's second table, one kind per class (money, odds, marshals, naval, diplomacy, the rules, the map, the calendar, last turn, the ground, counsel), read after every older kind; three question leads (`clause_guards.NATURAL_QUESTION_LEADS`), a question never split (`parser.A_QUESTION_IS_NEVER_SPLIT`), an unknown name refused never substituted, a one-letter typo disclosed. Measured on the committed census: question shrugs **114 → 0 of 150**; on the FRESH blind file: questions shrug **1 of 150** (orders shrug 4, as meant 73; the two readings the judge files as dangerous are recorded designs — the desk relaying an order of state, FA-50's hold idiom). Rules §88.1; pins `tests/test_sf_cmd1_part_ii_the_fixes.py::TestW1TheDeskAnswers`. ~~SF-CMD-1 (ii) with CRT-9 "the state speaks first": one desk kind per class, answering the terse form AND the natural one; completion = the census's question shrugs ≤ 30 of 150 on a FRESH blind file. ⟨SF step=4 · SF-CMD-1 (ii) / CRT-9 · pillar=first_contact⟩~~ |
| ~~**SF-CMD-1-W2**~~ | P2 | **Contingency phrasings are refused as "a contingency, not an order":** "march to Swabia and attack Mack when you get there", "if Mack is still in Swabia, attack him", "attack Mack if he moves", "once Ney engages Mack, hit his flank", "head for Swabia but stop if Mack turns on you". CR-7's condition vocabulary has no *when you get there / if he moves / once X / but stop if*; the arrival object exists for "when Davout arrives" only. | **FIXED in SF-CMD-1 (ii), Oct 3, 2026:** `condition_grammar` — the arrival idiom IS the tail (`strip_arrival_idiom`), a premise is checked at issuance against what the player sees (`split_premise` / `premise_refusal`, in `main.py`), an engagement clause is SUPPORT (`rewrite_engagement_support`), a halt tail is the road's own rule (`strip_halt_tail` + the `warning` note); "if he moves" stays refused and names `pursue`. Rules §88.2; pins `TestW2TheContingencyPhrasings`. ~~SF-CMD-1 (ii): the arrival object for *when you get there*; the two conditions CR-7 can hold (*if he moves* → the contact interrupt; *once X engages* → the SUPPORT road) said in those words; the rest refused with the sentence CR-7 already prints. ⟨SF step=4 · SF-CMD-1 (ii) / CR-7 · pillar=command⟩~~ |
| ~~**SF-CMD-1-W3**~~ | P2 | **Basic forms shrugged:** "end the turn", "Ney, go", "could Ney please fortify", "everyone converge on Swabia", "keep an eye on Berlin", "reward Lannes" (keyless; the keyed arm read all but the polite fortify). | **FIXED in SF-CMD-1 (ii), Oct 3, 2026:** `END_TURN_PHRASINGS` widened in both gates (the client mirrors it; a leading filler stripped; the negated compound ASKS rather than ending the turn behind the lapse confirm); `Ney, go` asks where; `could X please` is an order; `converge on` + the collective address relayed one man at a time; `keep an eye on` scouts; `reward X` = the Reward desk + `open_reward_for`. Rules §88.3; pins `TestW3TheBasicForms`. ~~SF-CMD-1 (ii): "end the turn" and the polite auxiliary ("could X please") are one keyword rule each; "go" asks for a destination; "everyone converge on" is the collective march; "keep an eye on" is scout; "reward X" opens the reward dialog. ⟨SF step=4 · SF-CMD-1 (ii) · pillar=command⟩~~ |
| ~~**SF-CMD-1-W4**~~ | P2 | **Bare diplomacy without the desk's name shrugs:** "propose an alliance to Prussia", "ask Austria for terms" (keyless). | **FIXED in SF-CMD-1 (ii) / CRT-8, Oct 3, 2026:** a bare Cabinet verb at the head naming a court routes to the Cabinet (`THE_CABINET_VERBS_NEED_NO_ADDRESS`); "ask X for terms" is Request Terms; RS-7's relation phrasings normalised; CQ-36 and CX-X3 taken with it. Rules §88.4; pins `TestW4TheCabinetsVerbs`. ~~CRT-8 "the Cabinet's rules on every road" — the Cabinet's verbs read without "Talleyrand," in front. ⟨SF step=4 · CRT-8 · pillar=command⟩~~ |
| ~~**SF-CMD-1-W5**~~ | P3 | **The pronoun in a compound:** "Ney attack Mack, Davout support him" → "Cannot find marshal 'Him' to support". CR-4 resolves "him" from history, not from the same line. | **FIXED in SF-CMD-1 (ii), Oct 3, 2026:** `, <marshal> <verb>` is a boundary in `_split_sequential_orders` (CRT-11's seam); in the relayed tail a pronoun after a support verb is the man last addressed (`context_carryover.A_SUPPORTED_PRONOUN_IS_OURS`). Rules §88.5; pins `TestW5TheSecondNameIsHeard`. ~~SF-CMD-1 (ii): the compound's second clause reads "him" as the first clause's subject. ⟨SF step=4 · SF-CMD-1 (ii) / CR-7 · pillar=command⟩~~ |
| ~~**SF-CMD-1-W6**~~ | P3 | **Epithets are unknown names:** "Iron Marshal, dig in", "the Bravest of the Brave, attack Mack" → "There is no Marshal 'Bravest' in the order of battle". | **FIXED in SF-CMD-1 (ii), Oct 3, 2026:** `parser.rewrite_epithets` — the two famous epithets plus every authored `ability.name` of ours resolve in address position; a title the board does not carry stays refused. Rules §88.6; pins `TestW6TheEpithets`. ~~SF-CMD-1 (ii): the authored ability names and the two famous epithets resolve to their men at the addressee seam (CX-R1's). ⟨SF step=4 · SF-CMD-1 (ii) · pillar=command⟩~~ |
| ~~**SF-CMD-1-W7**~~ | P3 | **The adverb and the reason clause:** "hunt Mack down" → 'Mack Down'; "Ney, fall back - I don't like Swabia" → "could not make out a destination"; "make Bavaria a vassal" asks for a marshal; "Emperor to Rhineland" is bewilderment. | **FIXED in SF-CMD-1 (ii) / CRT-6's part, Oct 3, 2026:** the trailing particle stripped from a target (`_clean_target_text`); a bare retreat with a reason clause is a retreat (`A_REASON_TAIL_IS_NOT_A_DESTINATION`); `make X a vassal` parses (gated by CRT-8 §8a); `Emperor to Rhineland` is a move (`rewrite_telegraphic_march`). Rules §88.7; pins `TestW7TheAdverbAndTheReasonClause`. ~~SF-CMD-1 (ii) with CRT-6 "the retreat is a word" (the bare fall-back with a trailing clause) and CRT-2 (the trailing adverb). ⟨SF step=4 · SF-CMD-1 (ii) / CRT-6 · pillar=command⟩~~ |
| ~~**SF-CMD-1-W8**~~ | P3 | **Naval phrasings:** "bring the fleet home", "ship Davout to London" shrug keyless (the model reads both). | **FIXED in SF-CMD-1 (ii), Oct 3, 2026:** "bring the fleet home" is the guard posture on both halves (`naval._GUARD_NOUN_RE` / `_POSTURE_VERB_RE` + the mock arm); ship / transport / ferry / carry <corps> to <shore> and "by sea" are the landing verb. Rules §88.8; pins `TestW8TheNavalPhrasings`. ~~SF-CMD-1 (ii): "bring the fleet home" = the guard posture; "ship X to Y" = the landing verb. ⟨SF step=4 · SF-CMD-1 (ii) · pillar=command⟩~~ |
| ~~**SF-CMD-1-W9**~~ | P3 | **A board refusal that names neither the man nor the order** — "The treasury cannot support this, Sire. Need 1,504 gold, have 800" for `Murat, recruit cavalry` — reads as the parser's under the HOLD rule (a board refusal counts as read only when it names the intended marshal). | **FIXED in SF-CMD-1 (ii) / CRT-9, Oct 3, 2026:** `_msg_treasury` / `_msg_pool_short` name the man and the arm with comma-formatted figures at all three sites; the census judge reads the refusal as the board's. Rules §88.9; pins `TestW9TheRefusalNamesTheMan`. ~~CRT-9: every board refusal names the man and the order it refused. ⟨SF step=4 · CRT-9 · pillar=command⟩~~ |

## SF-CL-1 "The forecast keeps its word" — filed October 3, 2026 (**2 rows SF-CL-1-X1 … X2, both FIXED in the slice**; landing record `docs/SCORE_FINISH_SPEC.md` §3 Step 4; rules `SYSTEMS_REFERENCE.md` §86; instrument `tools/playtest_driver.py::ForecastLedger` + `tools/forecast_census.py`)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SF-CL-1-X1**~~ | P2 | **The muster's ceiling was not a ceiling: the resolver stamps a coordination attack bonus (combined arms + per-ally + dedicated + adjacent, capped +25%) on every participant BEFORE it sums the committed strength, and the preview never priced it.** Measured on the FLD and OP arms, turn 1: the Emperor's co-located attack printed "expect about 103,383 … up to 112,775 if all march" and the resolver weighed **138,604** (144,339 against 117,651 on OP) — every reinforcer's attack modifier read 1.1 → 1.375 at resolve. FA-61 had folded the sovereign aura into the ceiling and named "the resolver can exceed it" as a known gap; this was the other, larger cause. | **FIXED in SF-CL-1:** `combat_executor.THE_MUSTER_PRICES_THE_COORDINATION` — `_priced_coordination` stamps the context the resolver will stamp for the hypothetical "every WILL JOIN present" set (assumed present only where the resolver would find him: in the lead's own province when that is the field; the co-located partner marked GONE when the field is next door; adjacent guns neither) and restores every transient; the expected figure, the ceiling, the defender's committed term and the odds band are read under it. Measured: expected == ceiling == massed strength to the man on the co-located case; the ceiling exact when every promised corps fought from next door. Pins `tests/test_sf_cl1_the_forecast_keeps_its_word.py::TestTheMusterPricesTheCoordination`; the CA9 band-invariance pin re-seated under the same context. ⟨SF step=4 · SF-CL-1 · pillar=combat_legibility⟩ |
| ~~**SF-CL-1-X2**~~ | P3 | **The structured muster never reached the wire.** W6-4 built `muster_preview` onto the executor result "for UI rendering", but `main.py`'s `_COMMAND_RESULT_SIMPLE_FIELDS` never carried it (the client renders the muster from `message`), so no instrument could set the preview's figures beside the battle's — the ledger's first run recorded six scout rows and no muster at all. | **FIXED in SF-CL-1:** `muster_preview` and the new display-only `massed_strength` {lead, committed, total, arrived, contributors, absent} ride the `/command` allowlist and the two hand-enumerated roads (the insist and the charge). Pins `TestTheWire`. ⟨SF step=4 · SF-CL-1 · pillar=combat_legibility⟩ |

## SF-LB-2 "The Defenceless Prize" — filed October 3, 2026 (**1 row SF-LB-2-X1, FIXED in the slice**; landing record `docs/SCORE_FINISH_SPEC.md` §6.4 addendum)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SF-LB-2-X1**~~ | P1 | **The AI could declare a war on Hanover and never fight it: a province that shares its name with the attacker's own marshal is unreachable by `attack`.** Prussia's marshal Brunswick and Hanover's province Brunswick (beside Berlin) share a name; the undefended-capture rung (P4.5) emits `attack Brunswick` for the province and the attack arm's 4D-4 refusal read the name as the friendly marshal ("Cannot attack friendly marshal Brunswick!") — WO-13's one exact collision, one seam over. Measured on the ambient board after the council's declaration (turn 11): "No valid actions remaining for Prussia" for twelve turns, both corps in Berlin, Hanover untouched at turn 40. `move to Brunswick` worked all along. | **FIXED in SF-LB-2:** `combat_executor.A_PROVINCE_OUTRANKS_A_FRIENDLY_NAMESAKE` — where no enemy answered the name and a province on the map carries it, the province is the reading (a friend who is no province is still refused; the enemy-marshal read stays first). Prussia takes Brunswick and the Hanover capital by turn 14 on every seed. Pins `tests/test_sf_lb2_the_defenceless_prize.py::TestAProvinceOutranksAFriendlyNamesake`; rules §85.5. ⟨SF step=4 · SF-LB-2 · pillar=living_balance⟩ |

## SR-7d "The Doctrines" — filed October 3, 2026 (**2 rows SR-7d-X1 … SR-7d-X2, both owned; 0 P1 · 1 P2 · 1 P3** — X2's T5 measured at Step 4's exit, October 3, 2026 (a pass); X1 and X2's T9 + T10 homed to Step 7's SF-DC-1 — found while landing the doctrines; landing record `docs/DOCTRINES_SPEC.md` §7.1; **both CLOSED by Score Finish Step 7 slice 6, SF-DC-1, October 4, 2026** — rules `SYSTEMS_REFERENCE.md` §93.8)

| ID | Priority | Finding | Owner / landing |
|----|----------|---------|-----------------|
| ~~**SR-7d-X1**~~ | P3 | **The volte-face arm no longer shows the beat on the shipped tree.** `tools/playtest_scripts/volte_court_austria.json` was scripted around Austria's losing armistice at turn 11; with France's corps system in force (`FRANCE_DOCTRINE`) France wins the Austrian war through the coalition's own status-quo settlement at turn 12, in which Austria is never the beaten party, so `maybe_fire_volte_face`'s "beaten" clause has nothing to stand on and the beat never fires in forty turns — measured by a per-court bisect (every lever down: 3 beats; France alone up: 0). `tests/test_rs27_the_volte_face_fires_on_its_arm.py` keeps its purpose with France's lever DOWN. The arm wants re-scripting for the doctrine board (a courted peace with Austria the beaten party). | Step 4's exit (`SCORE_FINISH_SPEC.md` §3), beside SR-7d-X2; done when the in-window pin runs on the shipped tree with no lever. Not taken at Step 4's exit (Oct 3, 2026: the exit measured T5 and homed the rest); homed to Step 7's **SF-DC-1 "Nothing unnamed"** so the volte arm reads on the shipped tree before SF-R reads diplomacy C3. **Step 5's exit (October 4, 2026) adds two constraints to the re-script:** (1) the boot satellites' contingents change the arm's war — on the doctrine-down drive the beat fires 3 times with the raise lever down and 0 with it up (`tests/test_rs27_the_volte_face_fires_on_its_arm.py` re-seated with the raise lever down too); (2) IQ6-D2 as ruled closes the door on the shipped arm's own board — Bavaria takes Bohemia and two more provinces, Austria's revanche hardens against France's bloc, and with the raise lever down alone the beat still does not fire (both down: it fires as at `f3ce1b57`). Diplomacy C3 reads ✗ on the shipped tree until the re-script: a courted peace in which Austria is the beaten party AND no member of France's bloc holds Austrian homeland. ⟨SF step=7 · SF-DC-1 (the volte arm re-scripted) · pillar=diplomacy⟩ ✅ **FIXED — Score Finish Step 7 slice 6 (SF-DC-1), October 4, 2026, through a ruling, not a re-script:** the re-script was played eleven ways on the historical seed (the arm's own war; France holding Bohemia or nothing; attacking or standing fast after Ulm; the turn-4 separate peace — refused, *"Making peace with Austria while allied with Bavaria"*; terms asked of London — refused, the league not spent; the Bavarian alliance broken — refused, *"a bond of 1805"*) and on every road Bavaria, at war with Austria from the boot, took a second Austrian province between turns 8 and 11, before the league was spent; the revanche was charged to Bavaria and IQ6-D2's bloc reading closed Austria's door for the campaign. With IQ6-D2's lever down the arm fires unchanged — the one blocker. **§6 row 20 (`SCORE_FINISH_SPEC.md`), RULED under the delegation, FOR USER CONFIRMATION:** the NOT-HUMILIATED clause's treaty arm keeps the bloc; its battlefield arm (the emergent revanche) reads the hegemon's vassal chain — a sovereign ally's conquest in its own war is its own quarrel (`emergent_designs.AN_ALLYS_WAR_IS_ITS_OWN`). The arm is unchanged and reads, per seed: **historical** — Austria's peace on turn 11 leaves Tyrol and Croatia Bavarian, she is courted to 42 by turn 26 and takes France's hand on turn 27; **austerlitz** — the beat on turn 24; **marengo** — none (Austria is at war again on turn 23, before the courtship reaches the floor). `tests/test_rs27_the_volte_face_fires_on_its_arm.py` runs with NO lever; its arm-0 attribution pin carries the new lever down with Step 3's. Pins `tests/test_sf_dc1_nothing_unnamed.py::TestAnAllysWarIsItsOwn`; SR-8c's client pin re-seated onto a true client (the Kingdom of Italy). |
| ~~**SR-7d-X2**~~ | P2 | **Three of the doctrines' acceptance targets are not yet measured as written.** T5 (the road to 45: Q0 re-measured after the doctrines, pass = the best road's titled count falls by no more than two — `tools/sr1e_titled_probe.py` on the three roads), T10's instrumented census (every bar shift that changed an arrival, every supply bite, every scaled penalty and priced recruit on the Jena road and one commanded arm, compared with the named lines — the digest shows the named moments; the unnamed count is not built), and T9's driven-route drift pin (every marshal's `_doctrine_terms` equals a fresh derivation after every mutating route of a driven arm — pinned at load, at the setter, at a commission and at every enactment / repeal / lapse today). | Step 4's exit (`SCORE_FINISH_SPEC.md` §3); done when the three measurements are in the landing record with a pass or an attributed miss. **T5 measured at Step 4's exit (Oct 3, 2026):** the three roads re-driven on this tree with the doctrines up and with `doctrines.DOCTRINES_ACTIVE` down (the counterfactual on the SAME tree; the RF-1 reading of Sept 27 predates Steps 1–4), `tools/sr1e_titled_probe.py` at turns 10 / 20 / 30 / 40 — AAR road 32 / 31 / 31 / 23 against 36 / 36 / 36 / 36; opening A 35 / 35 / 35 / 35 (36 at turn 41) against 21 / 23 / 23 / 21; opening B 25 / 14 / 15 / 11 against 37 / 37 / 35 / 35. **The best point falls from 37 (opening B, doctrines down) to 36 (opening A at turn 41; 35 through turns 10–40) — within the two provinces T5 allows: a pass** (pinned: `tests/test_sr7d_the_doctrines.py::TestT5TheRoadToFortyFiveAfterTheDoctrines`). The doctrines re-rank the roads (A rises fourteen; the AAR road's and B's unattended tails erode harder), recorded for SF-R's reach reading; archives `docs/audits/playtest_digests/sf4-q0-*`. The remainder (closed at Step 7, below): T9's driven-route drift pin and T10's unnamed-effect census — homed to Step 7's **SF-DC-1 "Nothing unnamed"** (`SCORE_FINISH_SPEC.md` §3 Step 7), which builds the instrument both need (an in-process transport observer comparing every marshal's `_doctrine_terms` with `doctrines.derive_terms` after every POST, beside the census of doctrine effects against the named lines). ⟨SF step=7 · SF-DC-1 (T9 + T10) · pillar=living_balance⟩ ✅ **FIXED — Score Finish Step 7 slice 6 (SF-DC-1), October 4, 2026:** the instrument is `tools/_doctrine_census.py` (`tools/playtest_driver.py --doctrine-census`); measured on the Jena road and CMD-H, historical seed. **T9 — PASS:** 0 drift in 11,448 marshal checks over 438 POSTs. **T10 — before the fixes 44 visible doctrine effects unnamed, after 0 of 53** (0 phantom lines; six distinct moments: Austria's Hofkriegsrat and Hereditary Lands, France's corps system and living off the land, Prussia's Frederick's Drill, Russia's slow concentration); CMD-H passes outright; the Jena road misses on per-court coverage alone, attributed — Britain fought in sight once, attacking (Paget on Massena), and its defence clause fired only in Castanos's attacks on Wellesley in Spain, out of sight. The four misses the census found: SF7-X12 … SF7-X15. Rules `SYSTEMS_REFERENCE.md` §93.8; pins `tests/test_sf_dc1_nothing_unnamed.py`. |

## IGR-X3 — The player can never end a boot war bilaterally, in EITHER direction (was OPEN, P1)

**Found July 25, 2026** while landing IGR-D, which hit it as a hard residual: a
`create_client` carve can only travel on the bilateral peace route, and that route is
unreachable for the three wars the campaign opens with. Measured, not argued — every
number below is from a live probe on the shipped `europe_1805` board.

**The rule.** `STATE_RELATION_REQUIREMENTS["PEACE"] = -60` (`diplomacy.py:86-93`), enforced
at `world_state.py:7950-7959` under `if is_player_treaty:`.

**Why it is unreachable.**

| | |
|---|---|
| Boot relations | France/Britain **−90**, France/Russia **−80**, France/Austria **−80** |
| Can they recover? | **No.** `_process_relation_decay` (`diplomacy.py:9698-9700`) explicitly skips `WAR` **and** `ARMISTICE`, so the +1/turn drift toward the neutral band never runs while the war is on |
| The armistice escape | `ARMISTICE_DURATION = 5`, and armistice also skips decay — a treadmill, never a path to PEACE |
| Scope | `is_player_treaty = (proposer == player OR target == player)` (`world_state.py:7915`) — **both directions** |

**Three things make it a defect rather than a difficulty:**

1. **Accepting the AI's OWN peace offer fails.** Probed: Austria proposes peace to France,
   France accepts → `diplomatic_treaty_failed`, *"Relations with France are insufficient
   for PEACE."* The AI offers a treaty the engine will not let the player take.
2. **The AI is exempt (GR5).** Probed: an AI↔AI peace at relation **−95** ratifies
   normally (`ai_ai_treaty`, state → PEACE). Two courts that hate each other may end their
   war; the player may not. Golden Rule 5 exists to forbid exactly this.
3. **The joint settlement route does not apply the check at all** — `settlement_ratify`
   never calls `check_relation_requirement`. So the identical peace is legal or illegal
   depending only on which surface the player used. The gate is a route artefact, not a
   rule.

**The design argument (user, July 25, 2026):** *"relation shouldn't impact war, people in
war hate each other anyway."* Historically exact: Pressburg (1805) and Tilsit (1807) were
signed at the maximum of mutual hatred, *because* of the war's outcome. War score,
military position and exhaustion are what should price a peace — the acceptance formula
already models all three. A relation floor on top double-counts the hostility and then
makes it absolute.

**Not fixed in IGR-D, deliberately:** removing or reshaping the floor re-prices every
bilateral peace in the game and touches the AI counter-offer path
(`ai_diplomacy.py:1926`). It needs its own investigation and a decision.

**Owner:** the next session (investigate + propose; see `docs/STATUS.md` Next Steps).

</details>

---

## How To Use This Doc

- This is the implementation source of truth for the current open PL items.
- Follow the session order below unless a direct dependency note inside an item says otherwise.
- Inspect only the exact implicated code surfaces and same-family helper paths for the active item.
- Use `docs/GPT_AUDIT_PLAN_RESULTS.md` for routing, collapse rules, and phase sequencing only.
- Use `docs/DESIGN_REFINEMENT.md` for post-fix spec routing. The old "design refinement stays blocked" rule below is historical now that Sessions 1-7 are complete.
- Update `docs/STATUS.md` whenever the open count, duplicate status, or active session changes.

---

## Scope Guard

- No new audit pass during this fix phase.
- No re-scoring, re-prioritizing, or widening of the problem space.
- No new PL items unless a direct code contradiction forces one.
- Approved exception: the shipped Session 2 mailbox lifetime model is reopened inside the owning `PL-27` / `PL-34` family because it now conflicts with the desired diplomacy-gating behavior. Use `docs/DIPLOMATIC_OFFER_LIFETIME_SPEC.md` as the source of truth for that follow-up.
- Same-family sibling failures on the same code path are absorbed into the owning PL item and called out explicitly below.
- Historical note: during the active bug phase, `docs/DESIGN_REFINEMENT.md` stayed blocked. That gate is now cleared because Sessions 1-7 are complete. Do not reopen bug sessions to do design work; use `docs/STATUS.md` + `docs/DESIGN_REFINEMENT.md` for the post-fix spec queue instead.

---

## Active Summary

| Session | Priority | ID | Status | Summary | Routing Note |
|---------|----------|----|--------|---------|--------------|
| 1 | P1 | PL-30 | **FIXED** | Godot null-instance crash on diplomacy button after a masked proposal result | Fixed Apr 10, 2026 |
| 1 | P1 | PL-31 | **FIXED** | Capital-loss instant defeat still live, with a false-negative regression test | Fixed Apr 10, 2026. Unblocks PL-28 |
| 2 | P2 | PL-27 | **FIXED** | Diplomacy interrupt contract: hard-stop/soft-stop taxonomy enforced, envoy recovery surface, typed responses | Fixed Apr 10, 2026 |
| 2 | P2 | PL-34 | **FIXED** | Queued proposals: arrival/expiry/overflow now logged in campaign log | Fixed Apr 10, 2026 |
| 2 | P2 | PL-33 | **CLOSED** (duplicate) | `status` works with soft-stop dialogue — verified as PL-27 duplicate | Closed Apr 10, 2026 |
| 2f | P2 | PL-27/34 | **COMPLETE** | Session 2 follow-up: mailbox inbox panel, `diplomatic_queue` eliminated, badge formula consolidated | Implemented Apr 11, 2026 |
| 2r | P2 | PL-27/34 | **COMPLETE** | Offer lifetime refactor: current-turn lapse, `Not Now`, envoy rename, client-side end-turn gate | Implemented Apr 11, 2026 |
| 2u | UX pass | Informational UI | **COMPLETE** | Notice rail, informational popup downgrade, direct Envoys recovery buttons, mailbox readability pass, adjacent HUD/log polish | Implemented Apr 11, 2026 |
| 3 | P2 | PL-32 | **FIXED** | Raw diplomacy labels can leak into popups because display ownership is split | Fixed Apr 12, 2026 |
| 4 | P2 | PL-28 | **FIXED** | No defeat-imminent warning before game over | Fixed Apr 12, 2026 |
| 4 | P2 | PL-26 | **FIXED** | Combat feels hopeless because the obvious opener teaches the wrong lesson | Fixed Apr 12, 2026 |
| 5 | P3 | PL-29 | **FIXED** | No new-game / restart endpoint | Fixed Apr 12, 2026 |

**Current routed-open set (August 3, 2026)** — the Creative-Audit rows below are ALL FIXED and are kept as a record: **IGR-X9** (razing sheds the EC-U2 bill — homed at ROADMAP row **EC-P3**) · **EWC-F1** / **EWC-F2** · **UI-2d-1** · **S5-4** (Pre-EA Dialogue Robustness) · **NV-P1's live wheel check** (§NV-P1 — evidence, not code). Historical note: BUG-CA-7 (dialogue-stack misroute) was the priority item. Overall routing lives in `docs/ROADMAP.md` §Current Phase Queue.

---

## Same-Family Decisions

- `PL-30` absorbs both diplomacy-wizard crash paths: Step 1 nation rendering and Step 2 preview rendering. Both failures come from the same masked-result plus coarse `dialogue_pending` contract and the same null-prone `add_output()` recovery path.
- `PL-27` absorbs the nearby same-family command-guard failures on `status`, `help`, `economy`, `treasury`, and `finances`, plus the active-envoy count mismatch, envoy-button recovery failure, and remaining popup handlers that still synthesize parser commands. `PL-33` remains only as a duplicate-candidate verification gate.
- Session 2 follow-up does not create a new PL item. It finishes the player-facing mailbox UX and folds in the same-family regressions found after Session 2 completion: browsable mailbox/inbox flow for 2+ pending items, defer/reopen UX, soft-stop reply routing drift, `/pending_envoy` payload shape drift, badge vs recovery mismatch when queued work exists behind a hard-stop, and the boundary between mailbox-worthy diplomacy and noisy top-bar notifications.
- `PL-34` is the queue/expiry branch of `PL-27`. Do not build a separate UX track for it.
- The approved current-turn offer lifetime refactor also stays inside the owning `PL-27` / `PL-34` family. It supersedes the shipped cross-turn mailbox lifetime behavior without creating a new PL id.
- `PL-32` absorbs all duplicate proposal/clause display maps and raw-token fallback leaks on the active diplomacy popup paths.
- `PL-29` absorbs backend `/new_game`, pause-menu wiring, frontend local-state reset, and autosave semantics as one restart contract.

---

## Architecture Blocker Decision

- Sessions 6-8 do not move earlier as full sessions.
- Only the bug-owned slices needed to close the active PL items ship earlier:
  - Session 2: backend soft-stop taxonomy, authoritative active-plus-queued count contract, typed responses for affected popups
  - Session 2 follow-up: Godot mailbox inbox browsing, defer/reopen UX completion, and PL-27 same-family hardening found after the fix landed
  - Session 2 current-turn offer refactor: replace cross-turn mailbox persistence with same-turn reopen plus turn-end lapse while preserving non-diplomatic soft-stop behavior
  - Session 3: backend-owned display formatting for active diplomacy popups
- Renderer replacement remains in Session 8. `/command` unification follow-up and Session 7 scale-sensitive backend hardening are complete.

---

## Session Order

### Session 1 - Stability And Defeat Truth

**Items:** `PL-30`, `PL-31`

**Goal:** remove the crash and align defeat-state truth across code, tests, and docs.

**Exit criteria**

- Opening Diplomacy after a masked proposal result no longer crashes Godot.
- Capital capture no longer contradicts the intended rule or its regression coverage.
- `docs/STATUS.md` no longer implies the capital-loss issue is already fixed.

### Session 2 - Diplomacy Interrupt Contract

**Items:** `PL-27`, `PL-34`, `PL-33` duplicate check

**Goal:** enforce the hard-stop vs soft-stop split, provide a real recovery surface for soft-stop diplomacy, and stop silent expiry/drop behavior.

**Exit criteria**

- Soft-stop diplomacy no longer blocks ordinary commands.
- Active plus queued diplomatic work is visible and reopenable.
- Expiry and overflow no longer resolve unseen proposals silently.
- `status` is verified after the guard split and either closes as a duplicate or remains as a true separate bug.

### Session 2 Follow-Up - Mailbox UX Completion, Inbox Browsing, And Contract Hardening — COMPLETE

**Items:** follow-up slice under `PL-27` / `PL-34` only. No new PL id.

**Status: COMPLETE** (April 11, 2026). `diplomatic_queue` eliminated. Mailbox panel built in Godot. `GET /mailbox` + `POST /mailbox/activate` endpoints. Badge formula uses `dialogue_manager.get_mailbox_count()`. 37 new tests, 8189 total passing.

**Historical note (April 11, 2026):** The cross-turn mailbox lifetime behavior shipped here is no longer the forward target. Keep this section as shipped-history only. The approved next-step behavior is documented in `docs/DIPLOMATIC_OFFER_LIFETIME_SPEC.md`.

**Goal:** finish the player-facing mailbox UX so soft-stop diplomacy is actually deferrable and browsable in Godot, and harden the Session 2 transport contract where the audit found live regressions.

**Why this is a separate follow-up**

- Session 2 fixed the backend taxonomy and recovery surface, but Godot still treats incoming proposals as a modal dead-end.
- The shipped mailbox button/hitbox fix made a single pending item reliable, but `Mailbox (N)` is still opaque when `N > 1`; the player cannot inspect or choose among multiple pending diplomatic items.
- This follow-up stays inside the owning `PL-27` family. It does not reopen `PL-33` or create a new tracked PL item.
- `PL-32` should not start until the active proposal contract and recovery payload are stable again.

**Next implementation item**

- Build a formal browsable mailbox/inbox panel behind the mailbox button.
- Do this before `PL-32`, before any broad notification redesign, and before any more popup display cleanup.
- Treat the current mailbox button as an interim reliability fix, not the finished UX.

**Exact scope**

- Keep the existing local `Later` / `Ask Later` path in `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd`.
- Add a mailbox panel/list in Godot instead of treating the mailbox button as "reopen one arbitrary pending item."
- Add a backend mailbox-list contract that returns the active soft-stop item plus queued soft-stop diplomacy in one ordered list.
- Add stable mailbox item identity (`mailbox_id`) for every pending diplomacy item that can appear in the mailbox.
- Add a backend activation contract so selecting a queued mailbox item makes it the active soft-stop item before the popup opens.
- Keep the pending dialogue alive when the player defers locally; the inbox is the mechanism for browsing, not implicit destruction or parser workarounds.
- Harden `backend/main.py` soft-stop reply routing so valid delayed replies still work through `/command`, including numeric choices and the common `accept` / `counter` / `reject` path.
- Fix `/pending_envoy` payload construction so it matches the `incoming_proposal_popup.gd` contract exactly instead of rebuilding a parallel shape.
- Eliminate `world.diplomatic_queue` — consolidate into `dialogue_manager` as the single pending-diplomacy queue.
- Fix badge formula to use `dialogue_manager.get_mailbox_count()` exclusively, eliminating the dual-source mismatch.
- Do not widen this slice into a general notification redesign. Record the clutter policy boundary, but keep the implementation focused on diplomacy inbox behavior.

**Mailbox behavior spec**

- **Dual-queue elimination (APPROVED):** The codebase has two separate pending-diplomacy queues. `world.diplomatic_queue` (world_state.py:443) holds raw AI proposals waiting for delivery — max 3, 3-turn expiry, drained by `_dequeue_best()` during end_turn. `dialogue_manager._queue` (dialogue_manager.py:75) holds delivered dialogues that couldn't become active — max 20, auto-promoted on pop. The current badge formula (main.py:170-172) counts `len(diplomatic_queue) + (1 if dm.is_soft_stop() else 0)` which counts undelivered proposals and ignores `dialogue_manager._queue`. `DialogueManager.get_soft_stop_count()` is broader than the mailbox because it includes hybrid soft-stops; the mailbox needs its own count contract. `diplomatic_queue` existed to throttle delivery to one-per-turn and defer acceptance-score calculation. Both purposes are obsolete: the mailbox IS the multi-proposal UI, and `POST /mailbox/activate` can recalculate acceptance scores at display time. **Eliminate `diplomatic_queue` entirely.** Deliver all AI proposals through `deliver_ai_proposal()` → `dialogue_manager.push()` at generation time. Remove the one-per-turn throttle in `turn_manager._process_ai_diplomatic_phase()`. Remove `_enqueue_proposal()`, `_dequeue_best()`, `_expire_queue()`, `try_deliver_queued_proposal()`, and the `diplomatic_queue` field from WorldState (including `to_dict`/`from_dict`). Migrate the PL-34 overflow/expiry ownership into `DialogueManager` itself — queue cap, any retained expiry sweep, and recorded outcomes must all come from the surviving queue, not from legacy raw-proposal helpers. Update all badge count formulas in main.py to use `dialogue_manager.get_mailbox_count()` exclusively (fix the 4 occurrences at lines ~170, ~498, ~858, ~1946). Remove `getattr(world, 'diplomatic_queue', [])` references in `main.py`, `diplomatic_ledger.py`, `meta_executor.py`.
- Mailbox badge count continues to mean: active soft-stop diplomacy item plus queued soft-stop diplomacy items. **Single source of truth: `dialogue_manager.get_mailbox_count()`** — counts `SOFT_STOP_MAILBOX_TYPES` in active slot + all items in `dialogue_manager._queue`. Exclude hybrid soft-stops from the count (see below).
- Clicking the mailbox with count `0` must produce a deterministic empty state, not a no-op.
- Clicking the mailbox with count `1+` opens a mailbox panel/list, not a proposal popup directly.
- True hard-stop modals still block mailbox interaction. Visible hybrid/local-planning popups that are not mailbox items also block mailbox open/activate; the inbox must not steal focus from them. The count may remain visible while blocked.
- The mailbox panel shows one row per pending diplomacy item with, at minimum:
  - `ACTIVE` vs `WAITING` state
  - source nation / actor
  - item type (`incoming_proposal`, `counter_offer`, `counter_offer_response`, `conflict_alert`)
  - arrival turn
  - short summary line suitable for list display
- **Hybrid soft-stop exclusion:** `sabotage_confrontation` and `vassal_rebellion_imminent` are counted by `is_soft_stop()` / `get_soft_stop_count()` but are NOT diplomacy proposals and must NOT appear in the mailbox panel or badge count. **Exclude hybrids from the count.** Add `get_mailbox_count()` to `DialogueManager` that counts `SOFT_STOP_MAILBOX_TYPES` only (not `HYBRID_SOFT_STOP_TYPES`). Use this for badge and `GET /mailbox`. Hybrids keep their own popup flows unchanged.
- **`conflict_alert` dispatch:** `conflict_alert` items currently route to `proposal_confirm_popup`, not `incoming_proposal_popup`. The mailbox panel must dispatch to the correct popup type based on `dialogue_type`. Add a type→popup mapping instead of assuming all items use `incoming_proposal_popup`.
- Ordering rule:
  - active soft-stop item first
  - then queued items by backend urgency/priority ascending
  - then FIFO within equal priority
  - preserve stable order across reopen, save/load, and non-diplomatic commands
- **Ordering metadata ownership:** When raw proposals become dialogues, copy the AI proposal urgency onto the dialogue (`mailbox_priority` or equivalent) and preserve a stable arrival sequence (`mailbox_id` seq or explicit `mailbox_order`) for FIFO ties. Do not rely on incidental list append order after save/load or activation swaps. Same-nation dedup must scan the active slot plus `dialogue_manager._queue`, not the removed `diplomatic_queue`.
- **Ordering consumer rule:** `mailbox_priority` / `mailbox_order` are the authoritative sort keys for both `GET /mailbox` and `DialogueManager._promote()` on `SOFT_STOP_MAILBOX_TYPES`. Keep `DIALOGUE_PRIORITY` only as fallback for non-mailbox types, and keep its mailbox-type fallback values aligned with the implementation order below (`counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4`).
- Selecting the active row simply reopens the current popup.
- Selecting a queued row must activate that item server-side before opening its popup. The previously active soft-stop item returns to the queue without data loss.
  - **Activation guard:** Only swap when the active slot is empty, already holds a `SOFT_STOP_MAILBOX` item, or holds a *disposable read-out*. If the active slot holds a `HARD_STOP`, `HYBRID_SOFT_STOP`, or a **staged** `LOCAL_PLANNING` type, both mailbox open and `POST /mailbox/activate` must return a blocked message — **naming the blocker** — instead of burying the active non-mailbox flow.
    - **AMENDED Aug 23, 2026** (live turn-3 report: *"i cant end my turn ... it says i cant answer lesser courts ... but i see nothing else to resolve"*). The blanket `LOCAL_PLANNING` refusal was measured making every routine envoy unanswerable behind a Talleyrand `advisory` — a read-out with no flow to bury, rendered on a CanvasLayer the mailbox panel is drawn *over*. `DialogueManager.DISPOSABLE_ACTIVE_TYPES` (`advisory` / `feasibility` / `command_clarification`) is now discarded to make way; the wizard and confirm types are deliberately NOT in that set, because displacing a half-drafted set of terms is a worse bug than the one being fixed. The discard happens AFTER the queue lookup so the stale-`mailbox_id` rule below still holds. Anything in NO taxonomy set is now DENIED rather than silently overwritten (it used to fall through). Refusals name the blocker via `display_names.dialogue_display_name`.
  - **Cache invalidation:** `world.incoming_proposal_popup` (main.py:1898-1904) caches the popup payload set at delivery time. `POST /mailbox/activate` must overwrite this cache with the newly activated item's data, or the recovery path (`/pending_envoy`, response polling) will show data for the wrong proposal. The same rule applies when an active item mutates in place (for example incoming proposal → `counter_offer`): rebuild the cached popup payload from the new terms, do not only flip flags such as `is_counter_offer`.
  - **Re-queued item lifetime:** When the previously active item is re-queued, preserve its original `turn_created`. Do not refresh the timestamp — this keeps `clear_stale` consistent and prevents indefinite keep-alive via repeated activation cycling.
- **Active popup-cache ownership:** `world.incoming_proposal_popup` is active-item-only state. Queued mailbox arrivals must NOT overwrite it just because a new item was pushed behind another current dialogue. Either store a popup-safe payload on each mailbox dialogue or guarantee `GET /mailbox` / `POST /mailbox/activate` / load-time recovery can rebuild it from dialogue context through one shared helper (including `counter_offer_response` created during `advance_turn`). On load or legacy `diplomatic_queue` migration, rebuild/validate the global cache from the active mailbox item only; ignore stale serialized popup data that points at a different mailbox item.
- **Mailbox identity continuity:** `mailbox_id`, `mailbox_order`, `mailbox_priority`, and the original arrival turn belong to the mailbox item, not to one specific dialogue type string. Preserve that metadata when the active item is enriched or replaced in place (for example `incoming_proposal` → `counter_offer` in `diplomatic_executor.py`) so the inbox row, dismissal state, and stale-selection handling still refer to the same pending item instead of a phantom "new" one.
- **Stale selection handling:** If a `mailbox_id` disappears between `GET /mailbox` and `POST /mailbox/activate` (expired, answered elsewhere, dropped on load cleanup), return a clean stale/not-found response with refreshed counts and leave the current active item untouched.
- `Ask Later` remains local and non-destructive:
  - close popup
  - re-enable normal input
  - keep the selected item pending
  - do not auto-consume or auto-reply
  - **Mailbox lifetime rule:** Do not inherit generic `clear_stale()` timeout behavior for mailbox items. Mailbox-eligible diplomacy is player-deferred, non-blocking inbox content and must not silently disappear on turn N+3. In this follow-up, remove generic mailbox expiry entirely. If any mailbox item ever gets an expiry later, it must be explicit on that item (`expires_on_turn` or equivalent), surfaced in the inbox UI, and covered by outcome logging/tests.
- The inbox panel, not repeated mailbox-button clicking, is the browsing mechanism for `Mailbox (2+)`.
- Accept / Counter / Reject always apply to the currently active item only. The activation step makes that deterministic.

**Recommended backend contract**

- Keep `/pending_envoy` for the simple "reopen current active item" path and backward compatibility, but make it active-item-only once the inbox exists. It must not silently choose a queued item. If there is no active mailbox item (queued-only state, or a hard-stop/hybrid/local-planning item is active with diplomacy queued behind it), return `has_pending = false` with an accurate `pending_envoy_count`; `GET /mailbox` is the authoritative browse surface for queued items.
- **Queued-only steady state:** After `diplomatic_queue` elimination, a mailbox-only queue with no active mailbox item should exist only when a non-mailbox current dialogue is in front, or during legacy-save migration before the first promotion pass. If the active slot is empty and only mailbox items remain, auto-promote the next mailbox item immediately instead of inventing a second long-lived steady state.
- Add `GET /mailbox` returning ordered mailbox-list summaries.
- Add `POST /mailbox/activate` with `mailbox_id`, returning the popup-safe payload for the now-active item.
- Add `mailbox_id` at proposal creation time and preserve it through:
  - `dialogue_manager.push()` (the sole queue after `diplomatic_queue` elimination)
  - delivery to active soft-stop
  - in-place enrichment / replacement of the active mailbox item (for example `incoming_proposal` → `counter_offer`)
  - re-queue of a previously active item
  - `counter_offer_response` items created during advance_turn (world_state.py:4488)
  - save/load serialization
- **`mailbox_id` generation:** Use `f"mb-{turn}-{seq}"` where `seq` is a per-turn monotonic counter on WorldState (e.g., `_next_mailbox_seq`). Serialize the counter. Avoids UUID dependency and stays deterministic for save/load. Reset per-turn is safe because `turn` prefix guarantees uniqueness.
- **Legacy-load metadata backfill:** On load, assign `mailbox_id` / `mailbox_order` / `mailbox_priority` to any restored mailbox dialogue that lacks them, including (a) current or queued `dialogue_manager` entries from pre-mailbox saves and (b) old `diplomatic_queue` items migrated during backward compat. After restoration/backfill, advance `_next_mailbox_seq` past every mailbox item already present for the current turn before generating new IDs, or a same-turn post-load arrival can collide with a restored item.
- Prefer preserving the original arrival metadata when an item is activated from queue; opening an old message should not make it look newly arrived.
- **Add `counter_offer` and `counter_offer_response` to `DIALOGUE_PRIORITY`** (dialogue_manager.py:66-71) as mailbox-type fallback values only. Currently these default to 99, causing incoming proposals (priority 3) to always sort before counter-offers whenever mailbox metadata is missing. Keep the fallback aligned with the ordering rule above: `counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4`.

**Recommended frontend contract**

- Mailbox button opens a lightweight inbox panel anchored to the existing top bar, not a full-screen modal.
- The panel should be non-destructive and easy to close; clicking outside or pressing the mailbox button again can dismiss it.
- Selecting a row triggers `activate -> popup open`.
- The panel should refresh after:
  - local defer
  - response submission
  - queue change from `/command` or `end turn`
  - save/load
- **End-turn rule:** Active mailbox soft-stops do NOT block `end turn` after this follow-up; only true hard-stop dialogues do. `end turn` should close the inbox panel first, then refresh mailbox state from the backend after turn advancement.
- **End-turn while panel open:** Close the inbox panel before submitting `end turn`. `advance_turn` can deliver new proposals, expire queue items, and clear stale dialogues — the panel would become stale. Simplest: close panel on any `/command` submission, reopen from fresh `GET /mailbox` after.
- If count drops to `0` while the panel is open, show an explicit empty state and close cleanly on next dismiss.
- **Replace `_dismissed_proposal_nation`** (main.gd:97): The current single-string tracker only suppresses one nation at a time. With the mailbox panel, either (a) disable auto-show entirely when the panel exists (preferred — the panel IS the browse mechanism), or (b) replace with a Set of dismissed `mailbox_id`s cleared on panel open.

- **Notification clear contract:** Once mailbox-eligible `DIPLOMATIC_PROPOSAL` notifications are suppressed/dismissed, the response/HUD path must explicitly clear the icon strip when none remain. Do not rely on omission of the `notifications` key to clear stale mailbox-related icons.

**Non-goals / adjacent note**

- Do not turn the mailbox into a generic notification center in this slice.
- Record the policy boundary for later HUD cleanup:
  - mailbox is for pending diplomatic decisions
  - mailbox-eligible diplomacy should not also create separate persistent `DIPLOMATIC_PROPOSAL` icon-strip entries once the inbox exists; use the mailbox badge plus campaign log/dispatch, and only a transient terminal/toast surface if an immediate arrival ping is still desired
  - persistent top-bar notifications should be reserved for action-required / strategically urgent items
  - routine combat/readiness notices such as `counterpunch ready` should be demoted later to event log, terminal feed, or transient toast instead of living indefinitely in the top-bar icon strip

**Exit criteria**

- The player can click `Later` on an incoming proposal and keep issuing commands immediately.
- Clicking the mailbox badge with multiple pending items opens a browsable inbox instead of one arbitrary proposal popup.
- The player can inspect and choose a specific pending diplomacy item when `Mailbox (2+)` is present.
- Clicking a queued mailbox row opens that chosen item, not whichever proposal happens to be active already.
- Delayed replies still work via typed popup buttons and through `/command` for `1/2/3`, `accept`, `counter`, and `reject`.
- `/pending_envoy` returns popup-safe data in the same display shape expected by `incoming_proposal_popup.gd` when an active reopenable mailbox item exists.
- Badge count and recovery behavior stay in sync for:
  - active soft-stop only
  - queued proposal only
  - active soft-stop plus queued proposals
  - five pending proposals in stable order
  - hard-stop active with queued proposals behind it
- No pending diplomacy item is lost, silently reordered, or spuriously consumed when the player browses the inbox.

**Regression test matrix**

- Extend Godot-facing popup tests for local defer behavior and re-enable-input flow.
- Add mailbox-list endpoint tests for:
  - active soft-stop only
  - queued-only (only when a non-mailbox current dialogue is in front, or during legacy-load migration before promotion)
  - active plus queue ordering
  - five pending items with stable order
  - hard-stop active with queued proposals still counted but not active
- Add activation tests proving a selected queued item becomes active and the previous active item is safely re-queued.
- Add endpoint tests for `/pending_envoy` covering:
  - active soft-stop returns reopenable popup payload
  - queued-only-behind-blocker (or pre-promotion legacy-load state) returns `has_pending = false` but keeps accurate `pending_envoy_count`
  - hard-stop-plus-queue returns no active popup payload and keeps accurate `pending_envoy_count`
- Add command-path tests proving soft-stop delayed replies still route for numeric and keyword inputs.
- Add save/load tests proving `mailbox_id` and queue order survive round-trip serialization.
- Add mailbox identity continuity tests proving:
  - `incoming_proposal` → `counter_offer` replacement keeps the same `mailbox_id` / `mailbox_order`
  - inbox refresh after a counter-offer still points at the same mailbox row instead of a duplicate/new item
- Add popup-cache ownership tests proving:
  - queued mailbox arrival does NOT overwrite the currently active item's popup payload
  - legacy-load / `diplomatic_queue` migration rebuilds the active popup cache from the promoted mailbox item, not stale serialized `incoming_proposal_popup`
  - `counter_offer_response` mailbox reopen/activation uses the same popup-safe builder as other mailbox items
- Add end-turn guard tests proving mailbox soft-stops do not block `end turn`, while true hard-stops still do.
- Add mailbox lifetime tests after `diplomatic_queue` removal:
  - deferred mailbox items are not force-cleared by generic `clear_stale()` timeout
  - active and queued mailbox items follow the same no-silent-expiry rule
  - if explicit per-item expiry is introduced later, it must be visible in inbox data and outcome logging
- Add hybrid soft-stop edge case tests:
  - hybrid active + diplomacy queued: badge count correct, mailbox shows only diplomacy
  - hybrid active does NOT appear in `GET /mailbox` response
  - hybrid active blocks mailbox open/activate instead of being swapped behind the inbox
- Add queue elimination migration tests:
  - all AI proposals reach `dialogue_manager._queue` after `diplomatic_queue` removal
  - badge count uses `get_mailbox_count()` exclusively (NOT `get_soft_stop_count()`)
  - PL-34 overflow logging fires from `DialogueManager`, not old `_enqueue_proposal` / `_expire_queue`
  - same-source dedup still works when the active item and queued item both live in `dialogue_manager`
  - `GET /mailbox` ordering and `DialogueManager._promote()` ordering both follow `mailbox_priority` + `mailbox_order`
  - no code calls `get_soft_stop_count()` for badge/UI purposes after `get_mailbox_count()` is added
  - `from_dict` backward compat: saved `diplomatic_queue` items are delivered into `dialogue_manager` on load, deduped by source+turn
  - legacy `dialogue_manager` mailbox items missing `mailbox_id` / `mailbox_order` are backfilled on load
  - `_next_mailbox_seq` is advanced past restored current-turn mailbox IDs before any new proposal is generated post-load
- Add `clear_stale` mailbox exemption tests:
  - `clear_stale()` skips `SOFT_STOP_MAILBOX_TYPES` in active slot regardless of `blocking` field value
  - mailbox item with `blocking=True` survives indefinitely (not force-cleared after `BLOCKING_TIMEOUT_TURNS`)
  - non-mailbox blocking dialogues still obey the existing safety valve timeout
- Add activation guard tests:
  - swap blocked when active slot holds `HARD_STOP`, `HYBRID_SOFT_STOP`, or a **staged** `LOCAL_PLANNING` type — and the refusal NAMES it (Aug 23, 2026 amendment above)
  - swap ALLOWED when the active slot holds a disposable read-out (`DISPOSABLE_ACTIVE_TYPES`), which is discarded only once the swap is certain
  - swap blocked for a dialogue type in no taxonomy set (deny, never overwrite)
  - `incoming_proposal_popup` cache updated on successful swap
  - `counter_offer` transition rebuilds cached popup clauses instead of only mutating `is_counter_offer`
  - re-queued item preserves original `turn_created`
  - stale `mailbox_id` activation fails cleanly without disturbing the current active item
- Add `counter_offer` priority ordering tests:
  - `counter_offer` vs `incoming_proposal` queue ordering after priority fix
- Add numeric-reply routing tests for soft-stop mailbox items:
  - "1" typed while soft-stop active matches first option
  - "2" typed while soft-stop active matches second option
  - numeric reply when no soft-stop active does NOT misroute
- Add dismiss-then-reopen tests for counter_offer_response:
  - "Dismiss" action on counter_offer_response keeps item pending
  - dismissed counter_offer_response reopenable from mailbox inbox
- Add dedup-after-elimination tests:
  - `_has_pending_proposal_from()` scans `dialogue_manager._queue` and active slot, not `diplomatic_queue`
  - same-nation proposal blocked when another from that nation is active or queued in dialogue_manager
- Add mailbox-vs-notification tests proving mailbox-eligible arrivals do not also leave behind duplicate persistent `DIPLOMATIC_PROPOSAL` icon-strip entries, and that the icon strip clears once no mailbox-related notifications remain.
- Re-run the existing Session 2 guard/count/history suite after the mailbox follow-up lands.

**Implementation trap warnings (sixth audit pass)**

These are concrete code paths that previous spec text covers implicitly but does not name. Missing any one will cause a runtime or logic bug:

- **`_has_pending_proposal_from()` (ai_diplomacy.py:277-301):** Scans `_get_queue(world)` for same-source dedup. After `diplomatic_queue` elimination, redirect this scan to `dialogue_manager._queue` (and active slot). Without this, duplicate proposals from the same nation will pile up.
- **`try_deliver_queued_proposal` import in turn_manager.py:302-303, call at 322-324:** Must be removed alongside the ai_diplomacy.py function body, or `ImportError` at runtime.
- **Inline `diplomatic_queue` expiry in world_state.py:4098-4101:** `self.diplomatic_queue = [q for q in self.diplomatic_queue if ...]` is a second expiry path outside `ai_diplomacy._expire_queue()`. Remove this block during step 0.
- **`meta_executor.py:2014-2016` debug cheat fallback:** Creates `world.diplomatic_queue` on demand and appends proposals directly. Redirect to `dialogue_manager.push()` with mailbox metadata.
- **`diplomatic_ledger.py:623`:** `len(getattr(world, 'diplomatic_queue', []))` — replace with `dialogue_manager.get_mailbox_count()` or equivalent pending-proposal query.
- **`diplomatic_executor.py:3217` `replace()` call (incoming_proposal → counter_offer):** Must copy `mailbox_id` / `mailbox_order` / `mailbox_priority` from the current dialogue onto the replacement dict. This is the only mailbox→mailbox `replace()` mutation; other `replace()` calls are local-planning flows that don't carry mailbox metadata.
- **`counter_offer_response` at world_state.py:4488-4514 sets `blocking: True`:** This type is in `SOFT_STOP_MAILBOX_TYPES`, so the step 4 `clear_stale` exemption must cover it specifically — without the exemption, the 2-turn safety valve force-clears it.
- **`_build_pending_envoy_popup_from_queue()` (main.py:1918-1929):** After queue elimination this helper has no callers. Remove it, and update the `elif result["pending_envoy_count"] > 0` branch at main.py:1964-1971 which uses it.
- **`is_soft_stop()` usage in badge formulas (main.py:172, 499, 859, 1947):** `is_soft_stop()` includes hybrids. All four sites must switch to the new `get_mailbox_count()`.

**Implementation order inside Session 2 follow-up**

0. **Eliminate `diplomatic_queue`:** Remove field from WorldState, remove `_enqueue_proposal`/`_dequeue_best`/`_expire_queue`/`try_deliver_queued_proposal` from ai_diplomacy.py, deliver all AI proposals via `deliver_ai_proposal()` → `dialogue_manager.push()` at generation time, and carry forward mailbox ordering/dedup metadata on the dialogue objects themselves. Remove one-per-turn throttle in `turn_manager._process_ai_diplomatic_phase()`. Migrate PL-34 overflow logging into DialogueManager (the 3-turn expiry from `advance_turn:4098` is removed entirely — mailbox items do not silently expire; overflow cap remains). Update all 4 badge formulas in main.py (`build_base_response:170`, `_include_popup_passthroughs:497`, end-turn response `:857`, `get_pending_envoy:1945`) to use `get_mailbox_count()`. Deprecate `get_soft_stop_count()` — it counts all queue items regardless of type and must not be used for badge/mailbox logic after `get_mailbox_count()` exists. Remove `diplomatic_queue` from `to_dict`/`from_dict` (add `from_dict` backward compat: if saved data has `diplomatic_queue`, deliver each item into `dialogue_manager` on load without duplicating already-active/queued items; dedup by source nation + turn since raw proposals lack `mailbox_id`). Suppress `DIPLOMATIC_PROPOSAL` persistent notification for mailbox-eligible proposals (`ai_diplomacy.py:905`) — use transient terminal arrival ping instead; the mailbox badge is the persistent surface. Also update: `_has_pending_proposal_from()` (ai_diplomacy.py:296), `meta_executor.py:2014-2016` cheat fallback, `diplomatic_ledger.py:623`, `turn_manager.py:302-324` import+call, and `world_state.py:4098-4101` inline expiry (see trap warnings above).
1. Add `counter_offer`/`counter_offer_response`/`conflict_alert` to `DIALOGUE_PRIORITY` (suggested: `counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4` — same-urgency as `incoming_proposal` for counter-offers, slightly lower for conflict alerts). Add `get_mailbox_count()` to `DialogueManager` that counts `SOFT_STOP_MAILBOX_TYPES` only (excludes hybrids).
   Use `mailbox_priority` / `mailbox_order` in both `DialogueManager._promote()` and `GET /mailbox`; `DIALOGUE_PRIORITY` is fallback only.
2. Add stable `mailbox_id` ownership (generation via `f"mb-{turn}-{seq}"` with per-turn counter on WorldState, serialization, presence on all mailbox-eligible dialogue types including `counter_offer_response` from advance_turn).
   Preserve mailbox metadata when the active item is replaced in place (`incoming_proposal` → `counter_offer`), and backfill missing mailbox metadata for restored legacy mailbox dialogues before advancing `_next_mailbox_seq`.
3. Add `GET /mailbox` plus `POST /mailbox/activate` (with cache invalidation for `incoming_proposal_popup`, activation guard for `HARD_STOP` / `HYBRID_SOFT_STOP` / `LOCAL_PLANNING`, re-queue with preserved `turn_created`). Lock ordering semantics with tests.
   Treat `incoming_proposal_popup` as active-item-only state: queued arrivals/load migration must rebuild per-item payloads instead of overwriting the active cache.
4. **Add type-based exemption in `clear_stale()` for `SOFT_STOP_MAILBOX_TYPES`:** skip clearing entirely when current dialogue type is in `SOFT_STOP_MAILBOX_TYPES`. Do NOT change the `blocking` field to `False` — that would trigger the non-blocking branch which clears on the very next turn. The `blocking=True` field is legacy; the type taxonomy is authoritative. Also confirm `is_blocking()` is not used in any guard path for soft-stops (it shouldn't be — guards use `is_hard_stop()`). Keep mailbox lifetime semantics inside the inbox contract. If explicit expiry is ever added later, make it per-item, visible in the inbox payload/UI, and logged.
5. Build the Godot mailbox panel/list. Wire mailbox button -> inbox open/close. Replace `_dismissed_proposal_nation` with panel-aware suppression. Add type→popup dispatch for `conflict_alert`.
6. Keep local defer behavior, but make inbox selection the authoritative "open this specific item" path.
7. Fix `/pending_envoy` shape and active-item-only backward-compat semantics so queued-only / hard-stop-plus-queue states are handled through `GET /mailbox`, not arbitrary queue reopening.
8. Fix soft-stop `/command` delayed-reply routing for numeric and keyword responses without widening back to global keyword misroutes. Specifically: add numeric-index matching (e.g. "1" → first option, "2" → second) against the active dialogue's `options` list for soft-stop dialogues (main.py:639-650), alongside the existing label/action text matching.
9. Lock the whole flow with mailbox browse/defer/select/respond-later regressions (including expanded test matrix above) before moving to `PL-32`.

### Session 2 Refactor Follow-Up - Current-Turn Diplomatic Offer Lifetime — COMPLETE

**Items:** follow-up slice under `PL-27` / `PL-34` only. No new PL id.

**Status: COMPLETE** (April 11, 2026). See `docs/DIPLOMATIC_OFFER_LIFETIME_SPEC.md`.

**Goal:** replace the persistent diplomacy mailbox model with current-turn envoy items that can be reopened this turn, lapse automatically at end turn, and block only new diplomacy during that same turn.

**What shipped:**

- `CURRENT_TURN_OFFER_TYPES` constant + `lapse_pending_offers()` + `has_current_turn_offers()` in `DialogueManager`
- `conflict_alert` reclassified from `SOFT_STOP_MAILBOX_TYPES` to `LOCAL_PLANNING_TYPES`
- AI proposals created with `blocking=False` — do not block end-turn or ordinary commands
- End-turn narrowed to hard-stop only (`is_hard_stop()` guard replaces blanket blocking check)
- Diplomacy gating narrowed: `is_hard_stop() or has_current_turn_offers() or is_local_planning()`
- Lapse hook at start of `TurnManager.end_turn()` — offers lapsed before enemy phase / AI diplomacy
- Campaign log `offer_lapsed` event type + morning dispatch `lapsed_offers` section
- Frontend: "Not Now" button rename, lapse warning text, "Envoys" rename (top bar + mailbox panel)
- Client-side end-turn confirmation gate with inline terminal warning
- Dispatch view renders lapsed offers section
- Diplomacy wizard blocked message updated
- Save/load migration: normalize `blocking=False` on offer types, remove legacy `conflict_alert` mailbox items
- 51 new tests in `tests/test_offer_lifetime.py`, 8249 total passing

### Session 3 - Diplomacy Display Contract

**Items:** `PL-32`

**Goal:** make the backend the single owner of player-facing diplomacy labels once the Session 2 follow-up transport contract is stable.

**Status: COMPLETE** (April 12, 2026). Proposal/clause label ownership is centralized in `backend/display_names.py`. `main.py`, `diplomatic_dialogue.py`, `mailbox_payloads.py`, `world_state.py`, `diplomatic_defiance.py`, and `ai_diplomacy.py` now consume shared backend formatters. `incoming_proposal_popup.gd` reads backend `proposal_type_display` instead of keeping its own proposal-type map. Added targeted regressions for raw-token leaks and popup payload display contract coverage.

**Exit criteria**

- Incoming proposal, counter-offer, sabotage, and fallback popup text all come from the same backend formatter.
- Godot stops rebuilding proposal labels from raw identifiers.

### Session 4 - First-Hour Pressure Cleanup

**Items:** `PL-28`, `PL-26`

**Status:** COMPLETE Apr 12, 2026. Audit handoff: `docs/SESSION4_AUDIT_HANDOFF.md`.

**Goal:** remove unfair defeat surprise and make the first combat lesson legible without flattening combat depth.

**Exit criteria**

- Players receive an explicit defeat-imminent warning before the live loss rule fires.
- The obvious early French attack line is no longer a hidden trap with no surfaced counterplay.

### Session 5 - Restart Flow

**Items:** `PL-29`

**Goal:** allow a clean restart from the live client/server flow without manual process kill or stale autosave leakage.

**Exit criteria**

- A supported `POST /new_game` contract exists.
- The pause menu exposes it.
- Autosave/restart behavior is explicit and regression-tested.

---

## Active Bug Specs

### ~~NV-P1: the Strategic Ledger panel ignores the mouse wheel~~ ✅ FIXED August 2, 2026 (NV-6) — ⚠ **live wheel check still OPEN**

**Cause, confirmed:** the ledger's content area is a `RichTextLabel`
inside a `ScrollContainer`, and a `RichTextLabel` defaults to
`MOUSE_FILTER_STOP` — it consumed the wheel event before its own parent
ever saw it. Dragging the thumb worked because the drag lands on the
scrollbar, not on the label. Fixed in `strategic_ledger.gd::_ready()` with
`content_area.mouse_filter = Control.MOUSE_FILTER_PASS`: PASS still
delivers `_gui_input`, so `meta_clicked` and every chip on the screen keep
working, and then lets the parent scroll. Guessed correctly in the row
below ("likely one `mouse_filter` line") — recorded because the guess was
worth something. Landed with the NV-6 Admiralty chips, which is what made
it bite hardest.

<details><summary>Original report</summary>

**Problem statement.** In the live client the Strategic Ledger's content
area does not scroll on mouse wheel. During the naval visual pass the
ECONOMY tab's content (income-by-region, then THE ADMIRALTY block at the
bottom) could only be reached by DRAGGING the scrollbar thumb — 60 wheel
clicks with the cursor squarely inside the content area moved nothing,
while a thumb drag scrolled instantly.

**Why it matters.** THE ADMIRALTY block renders at the END of the economy
tab, so on a France with many provinces the whole naval surface sits below
a long income list that a player will instinctively try to wheel past.
Same family as the IGR fix "the command terminal swallowed the mouse
wheel" — this is the ledger's turn.

**Scope.** PRE-EXISTING, not caused by the naval slices (the naval work
appended a render arm to `_render_economy`; it added no scroll handling
and changed none). Reproduced on `strategic_ledger.gd`'s panel.

**Owner / landing.** The next UI pass (or a standalone fix — it is likely
one `mouse_filter` / `ScrollContainer` focus line). **Completion
definition:** wheel scrolling works in every ledger sub-tab.
**Behavior test:** a `.gd` source pin that the scroll container accepts
wheel input, plus a live wheel check in the next in-client review.
</details>

⚠ **Still open:** the live wheel check in the client — the fix is a
one-line filter change with no headless test that can prove a wheel event
reaches a `ScrollContainer`. Verify on the next play session.

### NV-P2 (recorded, working-as-designed): a blockading Britain stops tinting a crossing it owns outright

Observed in the same pass: once Britain captured Normandy, the
London–Normandy sea link's map tint went from crimson (SHUT) to the
neutral/uncovered dash. That is `naval._fleet_covers_link` behaving
exactly as `NAVAL_SPEC.md` §3.3/§4.1 specify — a **blockade** posture
covers links touching an at-war ENEMY's provinces, and with Britain
holding BOTH ends neither endpoint qualifies (a **guard** posture, which
covers links touching its own provinces, would still cover it). It reads
correctly in fiction too: an internal ferry between two British-held
shores is not a contested strait. **Recorded so it is never re-filed as a
bug**; re-open only if a played session shows a player exploiting an
own-both-ends crossing.

### PL-30: Godot crash after a masked proposal result

**Problem statement**

A proposal result can be hidden behind a higher-priority popup, then the next Diplomacy-button interaction crashes Godot with `attempt to call function add_output on a base null instance`.

**Confirmed evidence**

- Playtest Session D reproduction: send a proposal, let a higher-priority popup win, then open Diplomacy on the next turn and hit the crash.
- The current popup pipeline only forwards one winner per response cycle through `_include_popup_passthroughs()`.
- The frontend crash string points at a stale/null `add_output` path rather than a cleanly recoverable deferred result.
- `diplomacy_wizard.gd` has two matching fallback branches: `_render_nations()` and `_render_preview()` both close the wizard and call `get_node("/root/Main").add_output(...)` whenever `dialogue_pending` is true.
- `/command` still has an enemy-phase path that consumes `proposal_result_popup` outside the main response builder, so proposal-result ownership is already split.

**Root-cause notes**

- `_include_popup_passthroughs()` only surfaces one winning popup per response cycle, so lower-priority proposal results can remain pending after a different popup displays first.
- The diplomacy preview contract is too coarse. Step 1 preview in `backend/main.py` and Step 2 preview in `backend/game_logic/diplomacy.py` both collapse multiple states into `dialogue_pending`, even when the real condition is "recoverable proposal result is still pending."
- The frontend wizard treats that coarse flag as a fatal block and routes through a null-prone terminal logging path instead of a structured recovery surface.
- Step 1 and Step 2 are the same failure family and stay under `PL-30`; do not split them into separate work.

**Exact code surfaces**

- `backend/main.py` - `build_base_response()`, `_include_popup_passthroughs()`, enemy-phase `/command` proposal-result handling, `/diplomatic_preview`.
- `backend/game_logic/diplomacy.py` - `get_available_diplomatic_actions()`, `get_diplomatic_preview()`.
- `godot-client/project-sovereign/scripts/main.gd` - `add_output()`, `_on_proposal_result_dismissed()`, `_on_diplomacy_button_pressed()`, `_open_diplomacy_wizard()`.
- `godot-client/project-sovereign/scripts/diplomacy_wizard.gd` - `_render_nations()`, `_render_preview()`.

**Exact failure modes**

- A higher-priority popup wins the current response, leaving `proposal_result_popup` deferred.
- The player reopens diplomacy. Step 1 or Step 2 sees only `dialogue_pending = true`, not the real deferred-result state.
- The wizard closes itself and tries to log via `get_node("/root/Main").add_output(...)`.
- If that node lookup is invalid in the current tree state, Godot throws the observed null-instance crash.
- Even when no crash occurs, the deferred result is still on an ambiguous contract and can be lost or redisplayed incorrectly.

**Edge cases / sibling failure scan**

- Reopen diplomacy from the button and from any shortcut/hotkey path.
- Reopen on the same turn as the masked popup and after a turn advance.
- Reproduce both Step 1 nation-list rendering and Step 2 action preview rendering.
- Verify the flow when a proposal result is pending but a true blocking dialogue is not.
- Verify dismissal does not create double-delivery on the next response cycle.

**State-transition risks**

- Clearing or dismissing the proposal result must happen in one source of truth; otherwise the same popup can reappear after the wizard or after enemy phase.
- `_on_proposal_result_dismissed()` currently refreshes war data and input state only. If proposal-result ownership moves, the dismissal hook must clear the retained result state as well.
- Save/load and turn-advance flows must not resurrect a stale deferred result after it has been dismissed.

**Backend / frontend contract risks**

- `dialogue_pending` is not precise enough for the diplomacy wizard. The fix needs an explicit distinction between a blocking diplomacy dialogue and a recoverable deferred result.
- Wizard-side code should not depend on a hard-coded `/root/Main` lookup to report contract state.
- The fix should not pull full Session 6 popup-registry work earlier; it only needs to restore single-source ownership for proposal results.

**Acceptance criteria**

- Reproducing the original masked-result flow no longer crashes the client.
- A proposal result that loses popup priority remains recoverable until it is displayed or explicitly dismissed.
- Opening the Diplomacy wizard after a masked result distinguishes "blocking dialogue" from "deferred result" instead of treating both as generic `dialogue_pending`.
- Neither Step 1 nor Step 2 of the wizard calls the null-prone `get_node("/root/Main").add_output(...)` fallback for this flow.
- Lower-priority proposal results are not discarded just because another popup displayed first.

**Regression test matrix**

- Backend response test: a lower-priority `proposal_result_popup` survives a higher-priority popup cycle and remains present until dismissed.
- Backend preview test: `/diplomatic_preview` and the Step 2 preview path return a structured non-crashing state when a deferred proposal result exists.
- Frontend smoke: `proposal reply masked -> next turn diplomacy open` via diplomacy button.
- Frontend smoke: the same flow through Step 2 preview and result dismissal.
- Re-run popup contract suites after the ownership change.

**Dependencies / blockers**

- No upstream blocker.
- Re-check this flow after Session 2 if mailbox semantics touch the same proposal-result surfaces.

**Implementation order inside Session 1**

1. Normalize proposal-result ownership so `_include_popup_passthroughs()` and the `/command` enemy-phase path stop diverging.
2. Replace the coarse wizard gating path with an explicit backend/frontend distinction between blocking dialogue and deferred result.
3. Remove the null-prone `add_output()` recovery call from both Step 1 and Step 2 render paths.
4. Add persistence tests for masked results, then rerun the original repro flow manually.

---

### PL-31: Capital-loss instant defeat is still live, and its regression test is broken

**Problem statement**

The game still hard-loses when Paris falls, even though the project history and regression test claim that capital-loss defeat was removed.

**Confirmed evidence**

- `backend/game_logic/turn_manager.py::_check_victory_conditions()` still returns defeat on captured capital.
- `tests/test_playtest_bugfixes.py::TestCapitalLossNotDefeat` targets `Ile-de-France`, which is not a live region key, so the test passes vacuously.
- Direct reproduction with `world.regions["Paris"].controller = "Prussia"` returns `Your capital has fallen!`.
- Historical status text still contains a now-false March 9 claim that capital-loss defeat was removed.

**Root-cause notes**

- `_check_victory_conditions()` still contains the obsolete capital-capture defeat branch even though the intended rule and prior notes say capital loss should be survivable.
- The regression test never exercised the live branch because it points at a nonexistent region key.
- `docs/STATUS.md` inherited the false "already fixed" claim, so code, test, and docs all drifted together.

**Exact code surfaces**

- `backend/game_logic/turn_manager.py` - `_check_victory_conditions()`.
- `tests/test_playtest_bugfixes.py` - `TestCapitalLossNotDefeat`.
- `docs/STATUS.md` - current-phase summary plus the March 9 historical note that now needs a superseded marker.

**Exact failure modes**

- Capturing Paris immediately ends the campaign even while France still has armies and other regions.
- The false-negative regression test allows the obsolete branch to survive future refactors.
- Downstream warning work in `PL-28` would otherwise target the wrong defeat rule.

**Edge cases / sibling failure scan**

- Capital loss with surviving armies and surviving territory must continue the game.
- Zero armies must still lose.
- Zero controlled regions must still lose.
- Time-expiry victory/defeat logic must remain unchanged.

**State-transition risks**

- Removing the capital-loss branch must not weaken the existing `game_over` flow for the real defeat paths.
- Any defeat summary, dispatch text, or end-turn path that referenced capital loss as terminal must be aligned to the surviving rules before `PL-28` starts.

**Backend / frontend contract risks**

- The live defeat rule is backend-owned; frontend and docs must not preserve stale capital-loss wording after the code fix.
- The repaired regression test must target the real live region key so future refactors fail loudly if the branch returns.

**Acceptance criteria**

- Capturing Paris alone does not end the game while France still has territory or armies.
- The regression test targets `Paris` and fails if capital-loss defeat comes back.
- `docs/STATUS.md` no longer implies this bug is already resolved.
- PL-28 warning logic is based on the surviving defeat rules, not the obsolete capital-loss branch.

**Regression test matrix**

- Repair `tests/test_playtest_bugfixes.py` to use `Paris`.
- Add or keep a direct defeat-state test that proves capital loss alone is non-fatal.
- Re-run defeat-condition coverage around zero-territory, all-marshals-destroyed, and time-expiry paths.

**Dependencies / blockers**

- Unblocks PL-28.
- If design direction changes later and capital loss becomes fatal again, reopen PL-31 rather than silently changing the rule.

**Implementation order inside Session 1**

1. Remove the capital-loss defeat branch from `_check_victory_conditions()`.
2. Repair the regression test to target `Paris` and add a direct non-fatal capital-loss assertion.
3. Re-run defeat-path tests to confirm only the intended loss rules remain.
4. Update `docs/STATUS.md` so the historical note is explicitly marked as disproven rather than silently left in place.

---

### PL-27: Diplomacy interrupt contract is broken

**Problem statement**

Soft-stop diplomacy is still treated like a hard-stop crisis. Incoming AI proposals and related items block ordinary commands, the player has no authoritative mailbox/recovery surface, pending counts are wrong, and several popup buttons still route back through stringly parser commands.

**Confirmed evidence**

- `backend/commands/executor.py` and `backend/main.py` both hard-stop on any `pending_diplomatic_dialogue`.
- `backend/game_logic/ai_diplomacy.py` still delivers incoming proposals with `blocking = True`.
- `backend/main.py::build_base_response()` and `backend/game_logic/diplomatic_ledger.py` both derive `pending_envoy_count` from queue length only, ignoring an active pending dialogue.
- `godot-client/project-sovereign/scripts/main.gd::_on_envoy_clicked()` only prefills `Talleyrand, report on the waiting envoy`; it does not open a real recovery surface.
- `backend/campaign_log.py` does not retain proposal-arrival events, so masked or auto-rejected opportunities are not authoritatively recoverable from history.
- Remaining popup handlers still use parser-shaped command text instead of typed dialogue responses.

**Root-cause notes**

- Both backend command paths treat any `pending_diplomatic_dialogue` as a global blocker before ordinary command handling can continue.
- The codebase already has a blocking taxonomy signal (`dialogue.get("blocking")`, `dialogue_manager.is_blocking()`, `meta_executor` special-casing for `end_turn`), but that taxonomy is not enforced consistently across `/command`, executor routing, previews, or UI entry points.
- Incoming proposals are still delivered as `blocking = True`, which collapses mailbox-style diplomacy into crisis-style interruption.
- The pending-envoy badge is not authoritative because it ignores the active pending item and counts only queued items.
- Recovery is not authoritative because the envoy button only pre-fills parser text and several popup responses still synthesize English commands instead of stable option ids.
- Same-family command failures on `status`, `help`, `economy`, `treasury`, and `finances` belong here. Do not create new PL items for those paths unless a post-fix repro survives the contract cleanup.

**Exact code surfaces**

- `backend/commands/executor.py` - pending-dialogue guard in `execute()`.
- `backend/main.py` - `/command` dialogue guard, `build_base_response()`, typed dialogue endpoint.
- `backend/game_logic/ai_diplomacy.py` - incoming proposal delivery, cooldown/frequency behavior, queue handling.
- `backend/game_logic/diplomatic_ledger.py` - pending envoy count and related visibility.
- `backend/models/dialogue_manager.py` and `backend/models/world_state.py` - stale-dialogue clearing and turn-advance behavior.
- `backend/campaign_log.py` - diplomacy event whitelist/history retention.
- `godot-client/project-sovereign/scripts/main.gd` - incoming proposal response handlers, envoy click target, remaining `send_command` fallbacks.
- `godot-client/project-sovereign/scripts/top_bar.gd` and related diplomacy UI entry points - badge/count presentation for the mailbox surface.

**Exact failure modes**

- A soft-stop incoming proposal freezes `status` and other ordinary commands because the guard fires before command execution.
- The active pending proposal is invisible to the top-bar badge if the queue is empty.
- Clicking the envoy badge does not reopen the pending item; it only sends a parser phrase and depends on brittle keyword recovery.
- Popup handlers for incoming proposal, objection, sabotage, and rebellion still route through parser text, which can drift from valid dialogue option ids.
- Queue promotion, dismissal, and stale-dialogue cleanup can all happen without an authoritative mailbox/history record of what the player actually missed.

**Edge cases / sibling failure scan**

- No pending dialogue: normal command execution must remain unchanged.
- Hard-stop dialogue active: command blocking must remain intact for true hard-stop crises.
- Soft-stop dialogue active with no queue: read-only and ordinary non-dialogue commands must still work.
- Soft-stop dialogue active with queued items behind it: badge/count and recovery surface must show both active and queued work.
- `end_turn` remains special: it may still require explicit handling or auto-default behavior for certain dialogue families.
- Same-family nearby commands `status`, `help`, `economy`, `treasury`, and `finances` must all be verified under the new guard split.

**State-transition risks**

- Reclassifying dialogue types without aligning stale cleanup can cause items to clear unexpectedly on turn advance.
- Active-to-queued-to-history transitions must update the badge/count exactly once at each step.
- If only one backend command path is fixed, the parser and direct executor paths will drift and create inconsistent behavior.
- Typed popup responses must not bypass the same world-state transitions used by parser-driven dialogue handling.

**Backend / frontend contract risks**

- The response contract needs more than a coarse `dialogue_pending` boolean. The frontend needs an authoritative distinction between hard-stop dialogue, active soft-stop item, and queued mailbox items.
- The envoy badge must be derived from the same backend-owned count in every response path.
- Recovery should reuse the existing envoy/desk surface rather than inventing a second parallel inbox flow.
- Popup handlers should send stable response ids to `/respond_to_diplomatic_dialogue`, not synthesized English text.

**Acceptance criteria**

- Hard-stop vs soft-stop taxonomy is enforced in both backend command paths.
- For the current fix phase, the minimum taxonomy is:
  - hard-stop: `force_declare_war_confirmation`, `commitment_paradox` (legacy `alliance_paradox` alias still accepted on load)
  - soft-stop mailbox: `incoming_proposal`, `counter_offer`, `counter_offer_response`, `conflict_alert`
  - hybrid soft-stop with end-turn default: `sabotage_confrontation`, `vassal_rebellion_imminent`
  - local planning flow, not global blocker: `proposal_confirm`, `advisory`, `mission`, `terms_guidance`, `ultimatum_demand_wizard`
- Incoming proposals, counter-offers, conflict alerts, and similar soft-stop items no longer freeze ordinary commands.
- Soft-stop diplomacy has a visible mailbox or desk surface with a trustworthy badge/count.
- Pending envoy count includes both the active soft-stop item and queued items.
- Envoy click opens the recovery surface instead of only prefilling terminal text.
- Auto-reject, dismissal, and expiry outcomes are recorded in dispatch/history so the player can tell what happened.
- Popup choices for dialogue-shaped diplomacy flows use typed response ids instead of synthesized English commands.

**Regression test matrix**

- Extend `tests/test_dialogue_manager.py` for hard-stop vs soft-stop classification and stale-clear behavior.
- Extend `tests/test_bugfix_proposal_flow.py` for non-blocking proposals, mailbox recovery, queued visibility, and auto-outcome logging.
- Extend `tests/test_endpoint_wiring.py` or `tests/test_response_pipeline.py` for authoritative pending counts and mailbox payload shape.
- Add command-path regressions for `status`, `help`, `economy`, `treasury`, and `finances` with no dialogue, soft-stop dialogue, and hard-stop dialogue.
- Re-run popup response tests after migrating the affected handlers to typed response ids.

**Dependencies / blockers**

- Root dependency for PL-34 and PL-33.
- Blocks PL-32.
- Blocks diplomacy refinement items that need a trustworthy interrupt model, especially R162.

**Implementation order inside Session 2**

1. Normalize the blocking taxonomy and enforce it in both backend command paths before parser execution.
2. Reclassify incoming proposals and other soft-stop flows so they stop acting like hard-stop crises.
3. Make the pending-envoy count authoritative by including both the active soft-stop item and queued items in one backend-owned contract.
4. Wire the envoy badge to a real recovery surface and migrate the affected popup handlers to typed dialogue responses.
5. Add history/dispatch outcomes for arrival, dismissal, expiry, overflow, and auto-default behavior.
6. Run the `PL-33` duplicate verification pass last, after the guard split and recovery surface are both live.

---

### PL-34: Queued diplomatic proposals can expire unseen behind blockers

**Problem statement**

Queued proposals can age out or get dropped before the player ever sees them, so diplomacy is currently being resolved by hidden queue expiry and overflow rules instead of explicit player choice.

**Confirmed evidence**

- Queue expiry removes proposals after three turns.
- Queue overflow keeps only the top three items and silently drops the rest.
- Queued delivery expires items before attempting delivery.
- Blocking dialogues can linger until the stale-dialogue cleanup path, which lets unseen queued items die behind them.
- The focused reproduction showed a later Prussian proposal expiring before it was ever surfaced because an Austrian blocker remained active first.

**Root-cause notes**

- Queue age currently starts at generation time, not at first player visibility.
- `try_deliver_queued_proposal()` expires queued work before attempting delivery, so a proposal can die on the same turn it would otherwise become visible.
- Queue overflow silently drops lower-ranked items once `QUEUE_MAX_SIZE` is exceeded.
- There is no authoritative mailbox/history record at enqueue time, so "waiting envoy" state is invisible until delivery succeeds.
- This belongs under `PL-27` because the real fix is the mailbox/visibility contract, not a separate proposal subsystem.

**Exact code surfaces**

- `backend/game_logic/ai_diplomacy.py` - `_expire_queue()`, `_enqueue_proposal()`, `_dequeue_best()`, `try_deliver_queued_proposal()`.
- `backend/models/dialogue_manager.py` - stale-dialogue cleanup timing.
- `backend/models/world_state.py` - dialogue clear path on turn advance.
- `backend/game_logic/turn_manager.py` - delivery timing relative to turn flow.
- Mailbox/count surfaces introduced by PL-27.

**Exact failure modes**

- A queued proposal generated behind another blocker can expire before first surface.
- Overflow beyond queue capacity silently discards proposals with no player-visible record.
- Badge/count state does not reveal that proposals are waiting or that they were dropped/expired.
- Clearing a blocker does not guarantee the player can inspect what arrived while that blocker was active.

**Edge cases / sibling failure scan**

- One active soft-stop item plus one queued item.
- One hard-stop item plus queued proposals behind it.
- Queue reaches capacity and receives one more proposal.
- A blocker clears on the same turn an older queued item would otherwise expire.
- Expiry, dismissal, and promotion all occur around turn advance or stale-dialogue cleanup.

**State-transition risks**

- Making queued arrivals visible at enqueue time must not double-count the item when it later becomes active.
- Expiry and overflow outcomes must remove the item from badge counts exactly once.
- Delivery-order policy should stay stable while visibility/accounting changes; do not mix count fixes with a ranking rewrite.

**Backend / frontend contract risks**

- If the mailbox payload only exposes the active item, queued proposals will remain invisible and this bug will survive under a new badge.
- If expiry/overflow are only logged in history but not reflected in the active count, the top bar will drift out of sync.

**Acceptance criteria**

- Queued proposal arrival becomes visible immediately through the authoritative envoy/mailbox contract, even if another item is currently blocking delivery.
- Unseen soft-stop proposals do not disappear silently.
- Expiry and overflow create explicit recorded outcomes; they never remove an item without a player-visible record.
- Delivery after the blocker clears preserves the existing queue policy unless a direct test proves the policy itself is wrong.
- The player can review what arrived, what expired, and what was auto-rejected through the mailbox/history flow introduced by `PL-27`.

**Regression test matrix**

- Extend `tests/test_bugfix_proposal_flow.py` for blocker-behind-queue visibility, hidden-expiry conversion into recorded outcomes, and overflow recording.
- Extend `tests/test_dialogue_manager.py` for promotion and stale-clear timing around queued items.
- Add a regression proving that a queued proposal generated behind another soft-stop item is still visible in the mailbox and is either surfaced or explicitly logged before removal.

**Dependencies / blockers**

- Implement inside the PL-27 batch.
- Depends on the new soft-stop/mailbox contract.

**Implementation order inside Session 2**

1. After the `PL-27` mailbox contract exists, make queued arrivals visible at enqueue time.
2. Convert expiry and overflow into explicit recorded outcomes.
3. Verify badge/count transitions across active, queued, expired, and dismissed states.
4. Re-run the focused unseen-expiry repro before closing the item.

---

### PL-33: `status` is blocked by the diplomacy guard and recovery path

**Problem statement**

The first-hour command most players are likely to try, `status`, is currently being swallowed by the same diplomacy guard/recovery failure that blocks ordinary commands.

**Confirmed evidence**

- The parser already recognizes `status`.
- `_execute_status()` exists and returns a valid intel report.
- The observed failure path happened while an incoming diplomatic dialogue was active.
- Current evidence does not show a clean no-dialogue reproduction.

**Root-cause notes**

- Current evidence points to the same global-guard failure family as `PL-27`, not to a broken `status` implementation.
- `meta_executor._execute_status()` already exists and is valid; the likely fault is that the guard fires before the command reaches it.
- Same-family read-only commands should be verified together instead of patching `status` alone.

**Exact code surfaces**

- `backend/commands/executor.py` - pending-dialogue guard.
- `backend/main.py` - parser-side dialogue guard.
- `backend/commands/meta_executor.py` - `_execute_status()`.

**Exact failure modes**

- `status` is blocked when a soft-stop diplomacy item is pending.
- The same failure family can also swallow other read-only commands that should remain available.
- Shipping a separate `status` patch before the taxonomy fix risks treating the symptom and leaving the family bug alive.

**Edge cases / sibling failure scan**

- `status` with no dialogue pending.
- `status` with soft-stop dialogue pending.
- `status` with true hard-stop dialogue pending.
- The same matrix for `help`, `economy`, `treasury`, and `finances`.

**State-transition risks**

- If `status` is special-cased instead of fixing the guard contract, the next read-only command will fail in the same way.

**Backend / frontend contract risks**

- None beyond the `PL-27` guard split; this item should not create new contract surfaces unless a post-fix repro survives.

**Acceptance criteria**

- After `PL-27` lands, `status` works with no pending dialogue.
- After `PL-27` lands, `status` also works while soft-stop diplomacy is pending.
- True hard-stop dialogue still blocks `status` where intended.
- If a non-dialogue-guard failure still exists after those checks, keep `PL-33` open and split it into a true standalone bug.

**Regression test matrix**

- Add a focused command-path regression for `status` with no dialogue, with soft-stop dialogue, and with a true hard-stop dialogue.
- Add the same verification sweep for `help`, `economy`, `treasury`, and `finances` under the owning `PL-27` test family.

**Dependencies / blockers**

- Blocked on PL-27.
- Duplicate-candidate; do not ship separate code unless a post-PL-27 reproduction remains.

**Implementation order inside Session 2**

1. Leave `PL-33` untouched until the `PL-27` guard split, mailbox contract, and typed-response recovery path are live.
2. Run the focused read-only command matrix.
3. Close as duplicate if the matrix passes; keep open only if a non-guard repro remains.

---

### PL-32: Raw diplomacy labels can leak into popups

**Status:** FIXED (April 12, 2026; audit follow-up added a pause-menu confirmation before `New Campaign` replaces autosave).

**Problem statement**

Proposal and clause display ownership is split across backend and Godot, so raw identifiers such as treaty enums or underscore tokens can leak into popups or degrade wording on fallback paths.

**Confirmed evidence**

- Backend and Godot both keep proposal display mappings.
- `backend/main.py` still formats fallback proposal text ad hoc.
- `backend/game_logic/diplomatic_dialogue.py` rebuilds clause display separately.
- `backend/models/world_state.py` builds counter-offer popup clauses directly from raw clause ids.
- `backend/commands/diplomatic_defiance.py` and `backend/game_logic/ai_diplomacy.py` still own separate formatting paths.

**Root-cause notes**

- Display ownership is split across `backend/display_names.py`, multiple backend helpers, and Godot popup scripts.
- The strongest live raw-leak path is counter-offer popup construction in `world_state.py`, which still builds clauses from raw ids.
- `_include_popup_passthroughs()`, `diplomatic_dialogue.py`, `ai_diplomacy.py`, and sabotage summary code all keep separate fallback formatting logic, so wording can drift even when raw ids do not leak.
- The duplicate Godot proposal-type map is part of the same family and belongs here rather than in a new frontend-only item.

**Exact code surfaces**

- `backend/display_names.py` - canonical display source.
- `backend/main.py` - popup safety-valve formatting.
- `backend/game_logic/diplomatic_dialogue.py` - proposal/clause rendering helpers.
- `backend/models/world_state.py` - counter-offer popup payload construction.
- `backend/commands/diplomatic_defiance.py` - sabotage proposal summary formatting.
- `backend/game_logic/ai_diplomacy.py` - secondary clause display map.
- `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd` - duplicate proposal-type map and underscore fallback.

**Exact failure modes**

- Counter-offer popups can show raw clause ids such as `territory_cede`.
- Proposal type labels can diverge between backend and Godot because both sides keep their own display maps.
- Safety-valve fallback paths can degrade into inconsistent title-casing such as `Open_Borders` or `Non_Aggression`.
- Sabotage and AI proposal summaries can describe the same clause family differently from incoming-proposal popups.

**Edge cases / sibling failure scan**

- Unknown or newly added clause ids should still render through one centralized fallback instead of leaking raw tokens.
- Counter-offer, incoming proposal, sabotage, and fallback popup paths must all be tested together.
- Legacy save data or modded clause ids should degrade consistently through the same formatter.

**State-transition risks**

- Removing the Godot-side map before all backend payloads are normalized can make some popups go blank.
- If one popup path still ships raw ids after the formatter centralization, the bug will survive in a fallback path and be harder to detect.

**Backend / frontend contract risks**

- The backend should ship fully rendered labels plus canonical ids only where machine logic still needs them.
- Godot should render provided display strings, not rebuild labels from ids.

**Acceptance criteria**

- Backend becomes the only owner of human-readable proposal and clause labels.
- Incoming proposal, counter-offer, sabotage, and fallback popup paths all consume the same backend formatter.
- Godot no longer rebuilds proposal labels from enum names or underscore replacement.
- Unknown ids degrade through one centralized fallback formatter instead of leaking raw tokens.
- Popup payload tests fail on raw tokens such as `NON_AGGRESSION`, `territory_cede`, or `Open_borders`.

**Regression test matrix**

- Add backend formatter tests for proposal type and clause rendering.
- Extend popup payload contract tests so raw underscore or enum-style tokens fail.
- Re-run proposal-flow and popup suites after removing the Godot duplicate map.

**Dependencies / blockers**

- Depends on Session 2 transport cleanup so the popup contract is stable before display ownership is collapsed.

**Implementation order inside Session 3**

1. Centralize proposal-type and clause-label rendering in `backend/display_names.py`.
2. Replace backend duplicate formatters in `main.py`, `diplomatic_dialogue.py`, `world_state.py`, `diplomatic_defiance.py`, and `ai_diplomacy.py`.
3. Remove the duplicate Godot proposal-type map and fallback formatting.
4. Re-run popup payload tests, especially counter-offer and sabotage paths.

---

### PL-28: No defeat-imminent warning before game over

**Status:** FIXED Apr 12, 2026.

**Problem statement**

The player can cross from a damaged position into defeat without any clear "you are about to lose" warning in the notification or dispatch layer.

**Confirmed evidence**

- Current defeat-state rules are already inconsistent enough that the player cannot predict what will end the campaign.
- The playtest loss happened without visible warning.
- The fix must follow the surviving defeat rule after PL-31, not the obsolete capital-loss branch.

**Root-cause notes**

- `turn_manager.py` checks terminal defeat only; it has no near-defeat helper that can emit warnings before the loss condition fires.
- After `PL-31`, the live battlefield defeat rules are "all armies destroyed" and "all territory lost." Time-limit warning already has its own system and should stay separate.
- The current item should not expand into predictive enemy-intent simulation. It only needs a deterministic warning tied to the actual surviving defeat thresholds.

**Exact code surfaces**

- `backend/game_logic/turn_manager.py` - defeat evaluation order.
- `backend/models/world_state.py` - any surviving defeat-threshold tracking.
- `backend/notifications.py` - defeat-imminent notification type.
- `backend/game_logic/dispatch.py` - morning-dispatch warning surfacing.

**Exact failure modes**

- The player can step into terminal defeat with no prior warning when only one army or one region remains.
- Warning wording can drift toward the obsolete capital-loss rule if `PL-31` is not treated as the source of truth first.
- If warning logic mixes in time-limit or enemy-intent prediction, the result will spam or mislead instead of clarifying the live loss rule.

**Edge cases / sibling failure scan**

- Exactly one surviving marshal remains.
- Exactly one controlled region remains.
- The player recovers above the threshold after a warning and should not keep stale warning spam.
- Time-limit warning stays on its separate path and is not merged into this item.

**State-transition risks**

- Warning state must persist long enough to appear in both notifications and the next dispatch, but it must also clear if the player stabilizes.
- The warning should fire before defeat resolution, not after a terminal result has already been returned.

**Backend / frontend contract risks**

- The warning should reuse the existing notification and dispatch surfaces, not create a one-off popup path.
- Wording must match the live defeat rule after the capital-loss branch is removed.

**Acceptance criteria**

- After `PL-31`, a high-visibility warning is emitted when France is down to exactly one living marshal and/or exactly one controlled region.
- The player receives the warning before the live defeat rule fires.
- Warning wording matches the actual surviving defeat condition after `PL-31`.
- The warning appears in both notifications and the following dispatch/readout path while the condition persists.
- The warning clears or stops repeating once the player climbs back above the threshold.

**Regression test matrix**

- Add defeat-warning coverage around the surviving loss threshold.
- Add notification/dispatch assertions so the warning is emitted before the actual defeat result.
- Verify that time-limit warnings are unchanged and remain separate.

**Dependencies / blockers**

- Blocked on PL-31.

**Implementation order inside Session 4**

1. Remove the obsolete capital-loss path via `PL-31` first.
2. Add a deterministic near-defeat helper keyed to one remaining marshal and one remaining region.
3. Wire it into notifications and morning dispatch.
4. Add non-spam coverage for warning persistence and recovery above the threshold.

---

### PL-26: Combat feels hopeless because the obvious opener teaches the wrong lesson

**Status:** FIXED Apr 12, 2026.

**Problem statement**

The common early "Ney attacks Wellington" line is punishing before the game has taught bombardment, coordination, or setup counters, so the player learns "attacking is hopeless" instead of learning the system.

**Confirmed evidence**

- Repeated attacks in playtest produced defender victories or punishing stalemates.
- Existing audit synthesis says this is primarily a teaching/setup problem, not proof that the combat system lacks depth.
- The current opener surfaces defender stacking before it surfaces viable French preparation lines.

**Root-cause notes**

- The likely first-hour attack line (`Ney` into `Wellington`) presents stacked defensive advantages before the game teaches the counters.
- The old coordination preview is gone, and the first-time coordination tutorial only fires after the player already achieves combined arms.
- The existing bombardment advisory fires only after the player already used artillery correctly.
- This makes the current problem a teaching/order-of-information failure first. Narrow numeric tuning is the fallback only if guidance plus setup still leave the opener feeling hopeless.

**Exact code surfaces**

- `backend/game_logic/combat.py` - modifier surfacing and common-opener outcome messaging.
- `backend/commands/combat_executor.py` - first-time coordination tutorial, bombardment advisory, and any added opener guidance on the attack flow.
- `backend/models/marshal.py` and region/terrain data only if number tuning is still required after surfacing fixes.
- Any tutorial, advisory, dispatch, or wizard surface used to expose the better line.

**Exact failure modes**

- The naive `Ney, attack Wellington` line produces a punishing result before the player is told about bombardment, combined arms, or defender terrain advantages.
- The game teaches combined arms only after success instead of before commitment.
- The post-bombardment advisory is useful but arrives too late to teach the player what to try first.

**Edge cases / sibling failure scan**

- If `Drouot` is unavailable, advice should still surface a non-artillery preparation line rather than naming an impossible move.
- The added guidance should target the common first-hour opener, not spam every later battle.
- Prepared assaults should improve the outcome materially without making all direct attacks trivially safe.

**State-transition risks**

- Guidance added only after the battle result may still be too late if the first failed assault already ends the campaign.
- Broad stat nerfs or buffs could mask the teaching failure while flattening later combat depth.

**Backend / frontend contract risks**

- Reuse existing advisory, objection, tutorial, or result surfaces; this item does not need a new UI system.
- If the advice is conditional, the trigger conditions must stay deterministic enough for regression coverage.

**Acceptance criteria**

- At least one obvious early French preparation line is surfaced as materially better than the naive direct assault.
- The game exposes the key counters behind the Wellington opener before or at the point the player is likely to commit.
- The prepared line is measurably better in the deterministic regression scenario than the naive line.
- Combat depth stays intact; this item does not flatten the system into guaranteed attack wins.

**Regression test matrix**

- Add a deterministic scenario test for the common opener and one prepared alternative.
- If guidance is added to objections, dispatch, or preview text, add a regression that the surfaced advice names the relevant counterplay.
- If narrow number tuning is required, add a regression proving the prepared line improves while the naive unsupported line is still risky.

**Dependencies / blockers**

- No hard code dependency.
- Intentionally sequenced after Sessions 1-3 so crash/defeat/diplomacy noise does not contaminate first-hour tuning.

**Implementation order inside Session 4**

1. Add or restore pre-commit guidance on the common opener attack path.
2. Reuse the existing tutorial/advisory surfaces instead of adding new UI.
3. Build a deterministic naive-vs-prepared comparison test.
4. Only if guidance still leaves the opener hopeless, apply narrow opener-specific tuning and capture it in tests.

---

### PL-29: No supported new-game / restart endpoint

**Status:** FIXED (April 12, 2026).

**Problem statement**

The player still has no clean restart path from the running build. Starting fresh requires server restarts and sometimes manual autosave cleanup.

**Confirmed evidence**

- No formal `POST /new_game` implementation exists in the live backend route set.
- The client pause flow exposes save/load only.
- Existing tests already call `/new_game` indirectly without making it a real supported contract.

**Root-cause notes**

- The backend world is initialized at startup only; there is no reset helper and no restart endpoint.
- The frontend already has save/load wiring, but the pause menu and API client never expose a restart path.
- The pause menu also needs an explicit destructive-action confirmation so one misclick does not immediately replace the current autosave.
- Local client reset logic already exists in the load flow and should be reused instead of inventing a second partial reset path.
- The test suite already assumes `/new_game` exists, so the current state is a direct contract contradiction rather than a speculative feature request.

**Exact code surfaces**

- `backend/main.py` - new-game endpoint wiring and world reset.
- `backend/save_manager.py` - explicit autosave reset/retention behavior.
- `godot-client/project-sovereign/scripts/api_client.gd` - client call.
- `godot-client/project-sovereign/scripts/pause_menu.gd` and `godot-client/project-sovereign/scripts/main.gd` - pause-menu button and UI refresh.

**Exact failure modes**

- Starting fresh requires a process restart and can inherit stale autosave state.
- Existing tests can call `/new_game` even though the route is not supported.
- Frontend local state such as pending popups, dialogue state, or cached world data can leak across a manual restart unless the reset path is centralized.

**Edge cases / sibling failure scan**

- Restart immediately after unsaved play.
- Restart after a manual save/load round trip.
- Restart while popups or dialogues are active.
- Manual saves must remain intact.
- Autosave from the previous campaign must not resurrect stale state after restart.

**State-transition risks**

- Resetting the world must also reset dialogue/mailbox state, notifications, eliminated nations, and any singleton references kept by `backend/main.py`.
- The client must clear local popup/dialogue caches before hydrating the fresh world response.
- Restart and load should share as much UI reset code as possible to avoid parallel bugs.

**Backend / frontend contract risks**

- `/new_game` should return the same kind of hydrated response shape the client already knows how to consume.
- Autosave behavior must be explicit. For the current fix phase, write a fresh autosave immediately after creating the new world so stale autosave state cannot be restored by accident.

**Acceptance criteria**

- `POST /new_game` returns a fresh world state without restarting the process.
- The fresh world is equivalent to a new campaign start: starting regions and marshals restored, `current_turn` reset, no pending diplomacy/dialogue carry-over, eliminated nations cleared.
- Autosave handling on new game is explicit and consistent, and stale autosave state cannot resurrect the previous campaign.
- The pause menu exposes restart/new game and returns the player to a fresh turn-one state.
- The pause menu requires explicit confirmation before restart/autosave replacement.
- Manual saves are preserved.

**Regression test matrix**

- Add formal endpoint coverage in `tests/test_endpoint_wiring.py` or equivalent.
- Add save/load interaction coverage so new-game does not accidentally reload stale autosave state.
- Add a client smoke or manual verification for the pause-menu flow if no Godot harness exists.
- Update or retain the existing `/new_game`-using tests so they now exercise a supported contract instead of an accidental assumption.

**Dependencies / blockers**

- No upstream blocker.
- Keep last in the fix phase because it is QoL, not game-truth or contract-critical.

**Implementation order inside Session 5**

1. Extract a backend world-reset helper that can be used at startup and by `/new_game`.
2. Implement `POST /new_game` and return a fully hydrated fresh-world response.
3. Persist a fresh autosave immediately after reset.
4. Reuse the frontend load-reset path for new-game hydration, then expose the action in the pause menu.
5. Add endpoint, autosave, and pause-flow regression coverage.

---

## Open Judgment Points

- `PL-30`: the exact null object in the crash stack should still be confirmed if the repro is rerun, but the implementation should harden both wizard render paths now rather than waiting on another trace.
- `PL-26`: if pre-commit guidance plus prepared-line verification still leaves the opener reading as hopeless, approve the narrow numeric tuning inside this item; do not jump straight to broad combat rebalance.

---

## Fixed Bug Archive

28 bugs fixed across playtest Sessions 1-12 and Sessions A-C.

| ID | Summary | Fixed In |
|----|---------|----------|
| PL-1 to PL-4 | Early combat/display bugs | Sessions 1-6 |
| PL-5 | Proposal race condition plus no feedback popup | Sessions 7-8 |
| PL-6 | "Harsher" terms on friendship pacts demanded territory | Session 7 |
| PL-7 | Counter-offer accept/reject missing AI cooldowns | Session 7 |
| PL-8 | Counter-offer popup looked like an unsolicited AI proposal | Session 9 |
| PL-9 | Acceptance mismatch between display and resolution | Session 10 |
| PL-10 | "More generous" downgraded proposal type | Session 10 |
| PL-11 | Incoming AI proposals hijacked player diplomatic commands (API-only) | Session 10 |
| PL-12 | Harsher terms increased acceptance estimate | Session 11 |
| PL-13 | Viable proposal falsely rejected as surpassed | Session 11 |
| PL-14 | Ultimatum delivery reworked into a conversational diplomacy tool | Session 12 |
| PL-15 | Ultimatum demand wizard replaced blind escalation | Session A |
| PL-16 | Harsher-demand multiplier retuned | Session A |
| PL-17 | Manpower demand zero-penalty bug absorbed into PL-18 | Session A |
| PL-18 | Typed manpower demands plus `DEMAND_VALUES` key fixes | Session A |
| PL-19 | Dynamic ultimatum relation penalty | Session B |
| PL-20 | Territory cost scaling plus elimination guards | Session B |
| PL-21 | Phantom `connections` attribute | Fixed in code |
| PL-22 | Phantom `income` attribute | Fixed in code |
| PL-23 | Authority-driven pushback, pen nudge, trust removal | Session C |
| PL-24 | Harshness scoring for all demand types | Session C |
| PL-25 | Term novelty: jitter, personality nudge, desire bias, flavor | Session C |

---

## UXR-0 / UXR-1 — the adjustability review's rows (October 9, 2026; Pre-Deploy Plan S1)

> Memo `docs/audits/UXR_ADJUSTABILITY_REVIEW_2026_10_09.md` §2b; rules `SYSTEMS_REFERENCE.md` §99; pins `tests/test_uxr1_scale_fix.py` + `tests/test_uxr0_readability.py`. Found by the read-only census and by the instrument's own first frames.

| ID | Priority | Status | Summary |
|---|---|---|---|
| **UXR-X1** | P2 | FIXED | **The saved Interface Scale was never applied at launch.** `main_menu.gd` never read `UiSettings.get_ui_scale()` in `_ready`; the first apply was `main.gd:760` when a campaign started, so a player who chose 150% saw the menu at 100% every launch while the slider read 150%. Fixed: `_apply_boot_scale()` at the head of the menu's `_ready` (§99.2), which also derives the scale for the screen when none is stored. |
| **UXR-X2** | P3 | FIXED | **The pause menu's Settings were squeezed to one slider.** The panel is authored 360×400 and `clamp_centered_panel` keeps the authored rect as its ceiling; the settings scroll's own minimum is 440 and it is the only shrinkable child, so the relax pass cut it toward the 48-px floor (`IQ10_WAR_ROOM_PAUSE_SETTINGS` before: INTERFACE and a sliver). Fixed: the clamp ceiling raised to 360×900 while the settings are unfolded, removed with them (§99.6). |
| **UXR-X3** | P2 | FIXED | **The tutor card had no height bound.** `fit_content` with scrolling off and no bottom edge; card XIX is ≈ 1,400 characters, and at the new 3.0 cap on a 1440-px panel the logical viewport is 480 px tall — the card ran off the screen with no scrollbar. Fixed: `_fit_card_height` bounds the body by the viewport and scrolls past it (§99.5); width as a viewport fraction. |
| **UXR-X4** | P3 | OPEN — owner UXR-2 "the layout law" (`docs/UX_UI_REVIEW_PLAN.md`), with the map renderer as its seam | **The map's own furniture does not follow Interface Scale.** The name stacks, garrison chips ("25k", "?") and sail counts are world-space Labels inside the map SubViewport, sized by the camera zoom alone: at the whole-map fit they read 6.75–9 px em on every monitor (the census's `map` tier, counted beside the floor). The five raw sizes in `scenes/map_renderer_base.gd` are the sweep's recorded exemption. Completion: the furniture's font size carries a term in `content_scale_factor` (or a Map-label-size setting), the five sites leave the exemption, and the `map_small` count in the physical census reads 0 at the derived scale. ⟨SF step=pre-deploy S9 · UXR-2 · pillar=ui_ux⟩ |

### UXR-1b — the whole-client census's residue (October 9, 2026; routed)

| ID | Priority | Status | Summary |
|---|---|---|---|
| **UXR-X5** | P3 | OPEN — owner UXR-2 "the layout law" (the diorama's tableau is a scaled surface, not a flowed one) | **The battle diorama's labels are under the floor on every monitor.** `battle_diorama._mk_label(…, fsize)` sizes its lockets, odometers and the "Faith spent" line in DESIGN px (8–12) inside a 1000×660 tray that `_fit_tray_to_viewport` scales by 0.35–1.0 — never above 1.0, so a 4K panel gets the same 9-px type a 1600×900 window does. Census: 20 P1 + 14 RED per diorama frame at the derived scales. Completion: the tray scales ABOVE 1.0 when the viewport allows (the inverse of its clamp) and its design sizes respect the floor at tray scale 1.0; the census reads 0 P1 on `diorama_*`. ⟨SF step=pre-deploy S9 · UXR-2 · pillar=ui_ux⟩ |
| **UXR-X6** | P3 | OPEN — owner UXR-2 (the sweep's recorded exemption) | **The war-detail popup's bar tags are 8 px.** `war_detail_popup.gd` sizes the "FR" / "BR" score-bar labels `max(7, font_size − 3)` — computed, so the floor's sweep left them; they read P1 on every frame (13 P1 per war-detail reading). Completion: the tags take the Caption class or the bar grows to hold 14-px tags; the census reads 0 P1 on `war_detail_*`. ⟨SF step=pre-deploy S9 · UXR-2 · pillar=ui_ux⟩ |
