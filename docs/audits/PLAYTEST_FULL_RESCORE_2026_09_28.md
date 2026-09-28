# The Full Play Retest — September 28, 2026: the Congress summoned at last, and dissolved by its own war

> **What this is.** The user's direction, after ruling SR5B-D1 and SRX-D1: *"make these decisions, commit, push, then do a full play retest and rescore with a steam review blurb."* The two rulings landed as `91796f25`. This memo is the retest and the re-score:
> - a campaign played by hand from the boot;
> - eighteen driver arms covering every pillar;
> - six verification agents that traced each suspected defect to its producer;
> - a Steam-style review.
>
> Defects are filed in **`BUG_FIXES.md` §Full Play Retest (RS-1 … RS-29)**. Design items are in **`DESIGN_REFINEMENT.md` §Full Play Retest (RS-D1 … RS-D3)**. Nothing was built in this session after the rulings.
>
> **How it was played.** France, the 1805 campaign, on a fresh backend on port 8009 with saves sandboxed and `DEBUG_MODE=false`. The live Anthropic parser was configured (`LLM_MODE=anthropic`). Every order was typed through `POST /command` from the scratchpad terminal `tent.py`, which renders what `main.gd` renders and answers every popup through the client's own endpoints.
> - **Scale:** 28 turns, 295 requests, 165 typed commands (113 distinct, 31 of them questions).
> - **Outcomes:** 156 carried out, 9 refused.
> - **Parser:** 160 read by the offline parser at 0.80–0.95; the model was consulted 4 times.
> - **Answered:** 11 captures, 8 marshal petitions, 67 dialogue answers and 15 envoy letters, plus the Congress.
> - **Archive:** the trimmed transcript, the diary and the saves are in `docs/audits/playtest_digests/rs0928-hand-played/`.
>
> **Honest limits.**
> 1. **No client pass.** The Godot client was not driven: the user's own game was open on the machine, so no window was opened on their screen. UI/UX is carried at its prior 7.0 and not re-scored.
> 2. **Interim score.** This is an interim, user-directed full re-score. It does not replace the one full re-score `SCORE_MANDATE_PLAN.md` §5 reserves for the end of the mandate, and every score below is **FOR USER CONFIRMATION**.
> 3. **No passive ending.** The eighteen driver arms run the mock parser, in process and seeded. None was played past turn 40, so this retest never saw the Verdict at turn 44 on a passive arm (the Creative AAR did).
>
> **Verification.** Every defect below was either reproduced at the wire during play or reproduced on a fresh boot by one of six read-only agents (scripts in the session scratchpad under `agentA` … `agentF` and `rsprobe`). Each row names its producer and a fix shape. Where a cause was not isolated, the row says so.

---

## §0 The verdict in five lines

1. **The Congress of Paris was summoned from a played road for the first time.** On turn 24, 47 of 45 provinces stood titled: the homeland, Vienna and its neighbours retained by two signed peaces, the six Hanoverian provinces after twelve quiet turns, and the clients' soil. The best road before today stopped at 39 and eroded. Prussia signed at the table for 1,800 gold.
2. **Then the Congress destroyed itself.** Austria and Russia refused. On day 3 the league the summons had made possible marched them to war, and Austria's war unsigned every province Austria had ceded: 47 fell to 41. The Congress dissolved on the same end turn, at the moment Austria's own answer became "SUES — we hold Vienna". The Congress's own review had filed this class of defect as a P1 and fixed it only for courts that sign. It is back, because SR-1a created great-power ceders who refuse (RS-2).
3. **A signed peace can be annulled two turns later by an ally's alliance.** Britain and Russia made peace on turn 10. On turn 12 Austria's coalition declaration dragged both back to war through the old Third Coalition alliances, inside the fresh-peace floor (RS-1, P1).
4. **The war reads, and the command line holds.** Ulm fell on turn 1: Mack was destroyed at Munich by Murat's charge after the Emperor's decisive assault. Vienna fell on turn 4 and Dresden, Moravia and Carniola by turn 16. The muster names who marches and at what odds, the band names its reasons, and the scout names the garrison. The rough edges are natural phrasings the parser does not know ("in support of Ney", "improve **our** relations", "where are the Russians?"), plus one real combat loophole: a capital's 25,000-man garrison never fights if a corps stands in it (RS-3).
5. **The middle of a winning campaign is quiet and rich.** From turn 19 to turn 28 France ended every turn with five actions unused, and the chest grew from 15,083 to 30,016 gold after roughly 29,000 had been spent. For thirteen turns the dispatch's lead or sub-beat was the same nag: "the levy has stood open N turns".

**Directional ≈7.0 → ≈7.1** (FOR USER CONFIRMATION). The ending, first contact, economy and naval rise; nothing falls. The ending stops short of its 7.0 target because of RS-2 and RS-D1.

---

## §1 The Steam review

> **👍 Recommended — 7/10**
>
> I typed *"Ney, you have the honour of the first blow — fall upon Mack at Swabia before the Russians can reach him"* and Ney did exactly that. Then I took the second blow myself, and Murat rode the broken Austrians down at Munich. By turn four I was in Vienna; by turn twenty-four I had summoned the Congress of Paris and bought Prussia's signature for 1,800 gold.
>
> Then Austria, whom I had beaten twice, "answered the Congress with cannon", and the war it started unsigned the very provinces it had ceded to me. Four turns in, the Congress dissolved.
>
> That is this game in one paragraph. A command line that actually understands you. Marshals who sulk, petition and object like men with careers. A Europe that remembers what you did. And an ending you can finally reach, whose last step still gives way under you.
>
> The writing is the best I've seen in the genre, and every refusal tells you exactly why. But when a peace you signed two turns ago gets dragged back into war by somebody else's alliance, it feels like a bug — because it is one.
>
> Buy it for the tent and the dispatches. The Congress needs one more patch.

---

## §2 The campaign diary (twenty-eight turns in the Emperor's tent)

*Entries in the Emperor's hand; the reviewer's marginalia in italics after each.*

**Late September 1805 (turn 1).** I asked Berthier who we fight and why: the Third Coalition, three designs, the homeland to defend. I asked what I could do: five orders the board would take. I told Soult to "bring your corps up in support of Ney" and he replied that he could not find a marshal called "Of Ney". Put more plainly, he went. Ney struck Mack at Swabia and cost him 15,612 men. I led the second blow myself: "Napoleon launches a decisive assault", and Mack lost 33,179 and fled to Munich, where Murat rode him down — "Mack's army is destroyed". Swabia stayed Bavaria's: "we drove the enemy from our ally's province; it is not ours to take." I sent Talleyrand "to Berlin to improve our relations with Prussia" and he answered that he awaited my instructions; without the word "our" he went.
*— Ulm in one turn, and the report names every modifier. The two misreads are RS-6 and RS-7: natural phrasings the fast parser reads at 0.9–0.95 and so never passes to the model.*

**Early and late October (turns 2–3).** The Porte, Lisbon and Berlin wrote; I opened my borders to all three. The Emperor broke Archduke Charles at Franconia (25,383 Austrian casualties to 3,402 of ours). Massena walked into Tyrol. Murat scouted Vienna: "Garrison: 25,000 — it must be assaulted — a march halts before it." Ney beat Archduke John at Bohemia. Talleyrand put the count at "35 of 45 titled". I enacted the Berlin Decree for 15 authority.
*— The scout's garrison line is SR-4a's, and it is true of a march. It is not true of an attack (next entry).*

**Early November (turn 4).** Metternich offered an armistice and I refused it. Davout broke Charles inside Vienna and "advances into Vienna", and Ney broke John's last 1,024 men: "Vienna has been captured by France!" The 25,000 of the garrison never fired a shot. I opened the settlement table, dropped Britain and Russia from coverage, eased the terms and ratified a white peace with Austria: "Bohemia, Tyrol and Vienna stay ours by the treaty — titled." That made 38 of 45. The Emperor marched home to Paris.
*— RS-3: a capital's garrison fights only when no corps stands in it. Win the field battle against the corps inside and the capture erases the garrison, 25,000 → 0. Measured on a fresh boot: the empty capital cost Davout 6,127 men to bleed its garrison to 15,719; the occupied one fell to a 1,000-man corps. The same road runs against Paris.*

**Early December 1805 to Early January 1806 (turns 5–8).** Prussia signed a non-aggression pact, then a defensive alliance. "Where are the Russians?" Berthier could not answer from the dispatches; "where is Kutuzov?" got an honest "no word". I enacted the Grand Quartier Général (9,000 of my 10,494) and the Code Abroad. The Kingdom of Italy petitioned for Tyrol and I granted it; Switzerland asked for eight collections of relief and I granted that too. Murat, told to support Davout, objected: *"March to another man's guns, Sire? Give me a battle of my own."* I trusted him, and the answer came back that there was "no intelligence on Kutuzov's position" — the order he had wanted instead. The objection was gone and the support order with it. Davout, fortified at Vienna, accepted a march to Vilna and never moved.
*— RS-5 (the Trust arm offers a man he cannot find, and the refusal costs the order); RS-4 (a fortified marshal accepts a march he can never make, charged, with no reason given for the stall); RS-14 (the desk cannot answer a nation's name).*

**Late January to Late February (turns 9–11).** Britain offered a white peace covering Russia too, and I accepted it: "Leon stays British by the treaty." We were at war with no one. I sent Hanover an ultimatum, it refused, and I declared war over Talleyrand's warning (alarm 70). Holland, Italy and Switzerland followed. Ney took Osnabruck and Oldenburg, Lannes took Westphalia and East Frisia, and Ney stormed Hanover twice (10,000 → 5,000 → collapsed).
*— The ultimatum road is clean: casus belli, a halved penalty, and the clients following at the declaration. The rail titled my own declaration "Diplomatic Action Rejected" (RS-20).*

**Early March (turn 12).** "Hanover is taken — Hanover's own capital." And in the same dispatch: "Austria and France are at war. Austria tears up the Peace Treaty to do it", "Paget has crossed into Normandy", and "The Fourth Austrian Coalition declared! (Instant — threat 97)". Britain and Russia, two turns out of their peace, were back at war with me through their alliances with Austria. Napoleon beat Paget at Normandy. Bernadotte bought 10,000 substitutes at Munich, and Berthier warned that at 24% morale he stood "ON his own breaking line".
*— RS-1, the retest's first P1. The fresh-peace floor (PR-1) guards coalition enrolment; the offensive cascade reads neither it nor the pair cooldown, and the settlement writes no cooldown at all.*

**Late March to Early May (turns 13–16).** Hanover and Saxony were knocked out of the war. I trusted Murat again and this time he charged Archduke Charles at Vienna at odds the what-if had called unfavorable: Murat lost 5,426 men and Davout's broken corps fled to Bohemia. There was no muster before the charge (RS-13). I refused the Kingdom of Italy's petition for Bohemia (loyalty −10, priced) and commissioned Marmont for 4,500 gold. Massena and Ney broke Charles at Dresden and John at Moravia. Davout unfortified for free and took Carniola. I bought off Prussia's design (1,152 gold). The second Austrian peace dropped seven covered courts and eased four times to "Will sign": "Bohemia, Carniola, Dresden, Moravia and Vienna stay ours by the treaty — titled."
*— The table works, but it is labour: every cover dropped re-drafts the settlement and resets the dial. The ratification rail named "France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia" for a peace with Austria alone (RS-9). The battle lines repeated: Ney's "bravest of the brave" after five of his six wins (RS-24).*

**Late May to Late July (turns 17–22).** Archduke John was taken prisoner at Carniola. Britain signed an armistice. The minors' peace resolved 42 pairs. "Why is Europe alarmed?" Berthier pointed me at the campaign log. Marmont petitioned for a front of his own. I granted rentes to Massena, Murat and Davout as each household "went unpaid". I let the Kingdom of Italy have Bohemia after all. The count held at 41; the Congress tab said the six Hanoverian provinces "title on turn 24".
*— The title road's promise was kept to the turn. The morning dispatch spent these weeks announcing that "the levy has stood open N turns" (RS-D2).*

**Early August to Early September (turns 23–24).** 47 of 45. I summoned the Congress: "The Congress sits for 8 turns, to the end of turn 32." Britain refused (at war: the truce had lapsed on turn 22, "it sues at +40"). Russia refused at −73, Austria at −92, and Prussia "will not sign". I laid 1,800 gold before Berlin: "Prussia now RECOGNIZES the order." 2,000 before Vienna moved it to −73 of 50, and 2,000 before St Petersburg to −76. I bought off Russia's design for 1,248. I offered Britain peace. Two "more generous" steps took the offer to 750 gold a turn plus one of my action points a turn, and it still read "COUNTER expected". I let it lie.
*— RS-D1: the table's price for Austria ("court them to 40, then an alliance") is true and unpayable. By the agents' measure, every lever for eight turns lifts Austria to about 0 and Russia to about 25, against a bar of 50.*

**Late September to Early November (turns 25–28).** "The courts of Europe are drawing together against us." "London pays St Petersburg 200g a turn to refuse the Congress." Then, on the end turn of the 27th: "St Petersburg answers the Congress with cannon. Vienna answers the Congress with cannon." The dispatch led: **"THE CONGRESS OF PARIS DISSOLVES — the titled provinces fell short (41 of 45) — Austria's war reopened what it ceded (Bohemia, Carniola, Dresden …). London and St Petersburg had not signed. Europe's alarm rises by 15, to 74, and the powers will not answer another summons for 9 turns."**
*— RS-2 and RS-10. The summons lowered the league's gate to 40 and started a three-turn brewing fuse; the Congress row kept saying no coalition stood; no fore-warning fired. A league formed and marched two refusers, and the ceder's war broke the titles the Congress sits on, all in one tick.*

---

## §3 The eighteen driver arms

Mode A, in process, seeded, mock parser, sandboxed saves, archived to `docs/audits/playtest_digests/rs0928-*` (driver `tools/playtest_driver.py`; runner in the scratchpad `run_arms.py`). "Titled" is read off each run's own save by `tools/sr1e_titled_probe.py`.

| Arm | Script / dials | Turns | Last ledger (provinces · treasury · Net · threat) | Titled | What it shows |
|---|---|---|---|---|---|
| `cmd-historical` | `commanded_full40`, accept | 40 | 30 · 91,878 · +2,545 · 3 | 36 | The commanded France holds and hoards. 90 of 160 actions spent. |
| `cmd-austerlitz` | same, seed austerlitz | 40 | 29 · 86,368 · +2,409 · 0 | 34 | Same shape on a second seed. |
| `cmd-marengo` | same, seed marengo | 40 | 27 · 91,827 · +2,355 · 0 | 36 | Same shape on a third seed. |
| `spender` | `commanded_spender40`, accept | 40 | 30 · 43,778 · +2,028 · 3 | — | Spending halves the hoard and does not end it. |
| `ambient` | no script | 40 | 4 · 503 · +53 · 12 | — | The unattended France is overrun, as on every exit. |
| `reach-aar-road` | `sr1e_aar_road` | 40 | 25 · 22,452 · +103 · 0 | 30 | The scripted roads stop well short of 45. |
| `reach-gev-b` | `sr1e_gev_b` | 40 | 20 · 14,875 · +101 · 1 | 23 (+3 held) | Same. |
| `aar-typed` | `sr_exit_aar_typed`, insist + accept | 18 | 26 · 11,208 · +1,313 · 31 | — | The AAR player's 127 lines; 48 of 145 commands refused (the board has moved under them). |
| `first-contact` | `sr_exit_first_contact` | 2 | 28 · 2,725 · +1,557 · 82 | — | All 28 sourced first questions answered; **0 shrugs**. |
| `field` | `sr_exit_chunk4_field`, insist + decline | 10 | 28 · 11,341 · +1,150 · 97 | — | 27 battles, petitions at the crisis tier only. |
| `laws` | `sr_exit_chunk5_laws`, accept | 10 | 30 · 12,335 · +591 · 93 | — | The laws road reads true; six rival-law beats. |
| `sea` | `sr_exit_chunk5_sea`, decline | 12 | 15 · 10,077 · −285 · 50 | — | Two Trafalgars and the second diversion throw; with the corps on the coast and diplomacy declined, Austria walks through the interior (28 → 15). |
| `volte` | `volte_court_austria` | 40 | 27 · 89,817 · +2,283 · 0 | — | Austria allies on turns 30 and 33 through ordinary proposals; the `volte_face` beat does not fire (RS-27). |
| `propose` | `--diplomacy propose` | 20 | 27 · 29,252 · +2,371 · 20 | — | One peace ratified. |
| `advisor` | `--missions advisor`, accept | 20 | 21 · 19,140 · +1,448 · 0 | — | The counsel arm; one peace ratified. |
| `flagship` | `flagship_1805`, insist/decline/proceed | 24 | 28 · 16,450 · −703 · 69 | — | The stress arm spends its army (297 men at turn 24; 4,054 on Sept 27). |
| `tutorial` | `tutorial_lesson` | 12 | 28 · 18,224 · +1,440 · 33 | — | The School of War walks to card XIX. |
| `pressburg` | the GE-3 fixture, `--stop-on-ending` | 9 (t28–36) | 39 · 31,194 · +2,412 · 59 | 55 | **THE IMPERIAL PEACE** at turn 36: Britain SHUT OUT; Russia, Austria and Prussia SIGNED; eight days held. |

Every arm completed. No traceback or server error in any of them, or in the hand-played campaign.

---

## §4 The re-score (interim, user-directed — FOR USER CONFIRMATION)

"Now" is `SCORE_MANDATE_PLAN.md` §1 as it stood before this retest.

| Pillar | Now | Retest | Why |
|---|---|---|---|
| **The ending** | 6.5 | **6.75** | **Up:** the Congress summoned from a played road (47 of 45 at turn 24); the title roads kept their promised turns; Prussia's price paid and latched; the staged Pressburg arm reaches THE IMPERIAL PEACE. **Short of 7.0:** the sitting self-destructs when a refusing ceder is marched (RS-2), and the beaten powers' recognition cannot be bought inside eight turns (RS-D1). |
| **Diplomacy** | 6.75 | **6.75** | **Worked:** four ratifications by hand, the ultimatum road, the buy-offs and the client petitions. **Offset by:** a fresh peace re-broken by an ally's cascade (RS-1, P1), a ratification label naming courts that were dropped (RS-9), "improve **our** relations" dead-ending (RS-7), and the copy in RS-18 to RS-23. Held. |
| **First contact** | 6.5 | **7.0** | The sourced first-contact arm is 28 of 28 answered with 0 shrugs (11 on Sept 26 before its residue). The boot briefing, "who am I fighting and why", "what can I do" and "how do I win" all land. The novel phrasings in the first twenty lines still slip (RS-6, RS-7, RS-14). |
| **Economy** | 6.5 | **6.75** | The laws give the early game a real decision: the Staff at 9,000 of 10,494 on turn 6. The ledger says why the bills moved, and the Charges of Empire grow with the chest (−1,424 at 30,016). The hoard remains: 30,016 by turn 28 after spending ~29,000 by hand, 86–92k on the commanded arms, and five actions unused a turn at peace (SRX-D1 ruled keep; RS-D3). |
| **Naval** | 6.5 | **6.75** | The second road plays: two diversion throws, two Trafalgars, a fleet action leading the dispatch, the expedition's levers, the yard. SHUT OUT held on the staged Pressburg board, not on a played one. The ports lever reads "(now 0)" through a truce without saying why (RS-25). |
| **Living balance** | 6.5 | **6.5** | Chunk 7 not yet built. The passive France still falls to 4; the commanded France still hoards; the Congress's failure raised the alarm by 15 and restarted two great-power wars, which is living balance working. Held. |
| **Combat legibility** | 7.0 | **7.0** | **Legible:** the muster's odds and absentees, the band's reasons, the ASSAULT block and the scout's garrison line. **Undermined by:** the garrison loophole (RS-3), no muster on an attack pressed through an objection (RS-13), a what-if blind to fortification (RS-12), and raw roster keys in the combat lines (RS-26). Held. |
| **Marshal drama** | 7.0 | **7.0** | **Better:** 8 petitions in 28 turns (was 9 in 18: SR-4c's fuse), audiences instead of modals, Murat's and Marmont's voices, the Congress raising every rente. **Offset by:** the Trust arm losing its own question (RS-5) and Ney's victory line five times in six (RS-24). Held. |
| **Vassals** | 7.0 | **7.0** | The client petitions flow about every two to three turns, each priced, granted or refused with a named cost; the clients follow the lord to war and to peace. Held. |
| **UI/UX** | 7.0 | **7.0 (not re-scored)** | The client was not opened. |
| **Command & parsing** | 7.5 | **7.5** | 156 of 165 typed orders carried out, 160 read offline at 0.80–0.95. The misreads are phrasings, not grammar: "in support of", "our relations", "take", "march on X and destroy Y" (RS-6 … RS-8, RS-11). Held. |
| **Narration** | 7.5 | **7.5** | **Strong:** the Congress beats ("St Petersburg answers the Congress with cannon", "London pays St Petersburg 200g a turn to refuse the Congress"), the capture headlines and the Verdict registers. **Weak:** the levy nag's thirteen turns (RS-D2), no headline when the Congress becomes summonable (RS-17), and repeated battle lines. Held. |
| **AI aliveness** | 7.5 | **7.5** | The Fourth Austrian Coalition, Paget's landing, rival laws enacted on every arm (13–18), design promotions, and the War of the Congress with London paying the refusers. Held. |
| **Agendas & formables** | 8.5 | **8.5** | The designs are priced and bought off, and the Congress levers name them. Not otherwise exercised. Held. |
| **Directional** | ≈7.0 (98.25 / 14) | **≈7.1 (99.5 / 14)** | Target ≥ 7.5 not met. |

---

## §5 What the play found — defects

Twenty-nine rows are filed in `BUG_FIXES.md` §Full Play Retest, each with its producer, fix shape and owner. The routing is in §7.

| Row | Sev | The observation |
|---|---|---|
| RS-1 | **P1** | **A fresh peace is re-broken by an ally's offensive cascade.** Britain and Russia signed on turn 10. On turn 12 Austria's coalition declaration dragged both back to war through the Third Coalition alliance triangle, inside `FRESH_PEACE_FLOOR_TURNS`. `diplomacy._process_war_cascade`'s offensive arm reads neither the fresh-peace test nor `armistice_cooldowns`, and the settlement never writes a cooldown. The cascaded courts end up at war but outside the coalition's member list. |
| RS-2 | **P1** | **The War of the Congress dissolves the Congress.** A refusing ceder is enrolled by the league the summons makes possible. Its war breaks the treaty titles (`game_end.break_signed_titles`), and `congress.process_end_of_turn` reads the hold on the same tick, with no window and no French act. GE-3's own review classed this as a P1 and fixed it for recognizers only; SR-1a's unlatched great-power ceders brought it back. |
| RS-3 | P2 | **A garrisoned capital falls to a field win over the corps standing in it.** The garrison fights only when no marshal is present. The winner "advances into Vienna" beside a 25,000 garrison, and a second win over the last corps captures the capital and erases the garrison (25,000 → 0). Measured on a fresh boot: the empty capital cost 6,127 men to bleed to 15,719, while the occupied one fell to a 1,000-man corps. GR5: the same road runs against Paris. |
| RS-4 | P2 | **A fortified marshal accepts a standing order he can never carry out.** March, hold or pursue is charged 2 actions. Every later turn reads "could not advance" with no reason, while the ledger holds "5 turns left" forever and the desk says he "can reach Paris in 5 turns". `march_state_refusal` has no fortified arm; `_stall_verdict` hides the reason. |
| RS-5 | P2 | **The aggressive objection's Trust arm offers a man we have never seen.** "Trust: Murat pursues Kutuzov" (or Moore at London, across a shut crossing) is refused as "No intelligence on Kutuzov's position", and the refused press consumes the objection, so the support order the player gave is lost. `disobedience._get_aggressive_preferred` ranks every enemy by true distance, fog-blind. |
| RS-6 | P2 | **Support phrasings misread.** "bring your corps up in support of Ney" → "Cannot find marshal 'Of Ney'". "march in support of Ney" → a 1-action march to a province named "In Support Of Ney". "come to Ney's support" → "You wish me to support Bernadotte?". |
| RS-7 | P2 | **"Talleyrand, improve our relations with Prussia" dead-ends** at a Dismiss-only card, as do "mend relations", "improve ties", "warm our relations" and five more. The mission phrase list is exact-match. |
| RS-8 | P2 | **"Ney, march on Swabia and destroy Mack" loses the destroy clause silently.** It becomes a plain march with no arrival target. "march against Mack" marches to a province called "Against Mack". Only attack / engage / assault join a march's tail. |
| RS-9 | P2 | **The ratification's rail, dispatch and ledger name the whole war's sides**, including courts the player dropped, while the terminal names the covered court. |
| RS-10 | P2 | **The Congress never warns that the summons lowers the league's gate to 40.** `march_blocker` reads only a standing coalition, never `coalition_brewing`. The row said "no coalition stands" for three turns while a league brewed and formed. No fore-warning fired. |
| RS-11 | P2 (keyless) | **"Bernadotte, take Bohemia" shrugs without a key** ("take" is excluded by design; "capture", "seize" and "occupy" work), and the shrug never suggests them. |
| RS-12 | P3 | The what-if weighs a muster for a fortified (and, by reading, a drilling, wounded or gun) marshal whose order would be refused. |
| RS-13 | P3 | An attack pressed through an objection (trust, insist, compromise) prints no muster. |
| RS-14 | P3 | The desk shrugs at "where are the Russians / the Austrians / the enemy?" and every alarm question. "Why is Europe alarmed?" points at the campaign log. |
| RS-15 | P3 | "What can I do" at zero military actions offers only "end turn" while 48 builds are legal. |
| RS-16 | P3 | The Congress's alarm line promises a fall of 3 a turn. In 27 turns it never fell by itself: gains are clipped at 100, then decayed. |
| RS-17 | P3 | No headline when the Congress becomes summonable. The Moniteur's near-miss column goes silent at 47 of 45. |
| RS-18 | P3 | The voiced settlement summary reads "Returning Gold indemnity: 100 gold … while Gold indemnity: 100 gold … buys quiet": both slots are filled with the first term. |
| RS-19 | P3 | The settlement's "Still at war:" line loses dropped courts; "Whole-war settlement" is printed while a court stands uncovered. |
| RS-20 | P3 | The player's own declaration of war is titled "Diplomatic Action Rejected" on the rail. |
| RS-21 | P3 | Raw warning keys ("Settlement Tier Legitimacy", "Agenda Settlement Mod") appear on a review every court has consented to. |
| RS-22 | P3 | The separate-peace hint names six courts and quotes one price. |
| RS-23 | P3 | "Prussia enters the war via alliance with France" is printed eight times a turn with no enemy named; the rail reads "(x16)". |
| RS-24 | P3 | Marshal battle lines repeat: Ney's "bravest of the brave" after 5 of 6 wins, Davout 3 of 3, both Archdukes 3 of 3. The rotation keys on the province's battle count, not the man's. |
| RS-25 | P3 | The Congress's ports lever reads "shut 13 of 26 ports (now 0)" through a truce. The System counts only a court at war with Britain, and the Berlin Decree's "whatever its autonomy" clause works only at war. Neither says so. |
| RS-26 | P3 | Raw roster keys in the muster and combat lines: "ArchdukeCharles does not stand alone", "ArchdukeCharles's DEFENSIVE stance", "ArchdukeJohn's troops are BROKEN". The client's name net rewrites nation tags only (NPC-12's census). |
| RS-27 | P3 | The volte-face beat does not fire on its own arm (IQ-6 measured turn 21; now none in 40 turns). Austria allies on turns 30 and 33 through ordinary proposals, unannounced. Cause not isolated. |
| RS-28 | P3 | Test hygiene: `test_napoleon_npv_review.py::TestPresenceReachesTheMarchingArmy::test_the_emperor_marching_to_the_guns_carries_his_presence` fails in one 12-way shard's order (1 of 1,008). It passes alone, in all 17 file pairs tried, and in the full suite; also on untouched HEAD `6ea98f93`. |
| RS-29 | P4 | "reinforcement orders stands and resumes next turn"; "Marshal Archduke John of Austria is taken". |

---

## §6 The Congress of Paris — why it dissolved, and what the design needs

**The trace.** The turn-24 save was replayed in memory and the dissolution reproduced exactly. On the end turn of the 27th:
1. The AI diplomacy phase ran first, while Austria was still at peace, so Austria's sue rung could not fire.
2. `advance_turn` ran next. `coalition.form_coalition` declared war for Austria and Russia, and the treaty-titled count fell from 47 to 41.
3. Then `congress.process_end_of_turn` read the hold and dissolved the Congress.

It was all one tick. Austria's own answer, once at war, was already "SUES — we hold Vienna". The only sitting-time shelter, `spared_from_coalition`, covers courts that recognize, are shut out, or hold a truce. A refuser gets nothing.

**The contract says otherwise.** `ENDGAME_PLAN.md` §2.5's counter-play is "beat a refuser to −40 (or take its capital)"; §2.4 says "a refuser whose capital France holds sues at once"; Berthier's line says "Beat them to the table, and lose no titled province doing it." GE-3's review (#10/#19/#41) filed "its war … un-titled its cessions and dissolved the Congress with no French act" as a P1 and fixed it for the case that existed then. RS-2 is that P1, reopened by SR-1a's ruling (2).

**Three more gaps on the same road:**
- **RS-D1, recognition by defeat.** At −90 the table cannot reach 50 within one sitting. Every lever for eight turns lifts Austria to about 0 and Russia to about 25. Only the latches work: a peace with explicit cessions, a peace signed while the Congress sits, elimination, vassalization, or shutting Britain out. The price on the table ("court them to 40 (+132)") is true and cannot be paid in time.
- **RS-10, the unwarned league.** The summons itself lowered the league's gate to 40 and started a three-turn fuse.
- **RS-16, the alarm road that never runs.**

**Recommended fixes** (the rows carry them):
- **RS-2:** while the Congress sits, a war France neither declared nor joined marks a refusing ceder's titles **contested but counted**. The break applies when that war ends. A real loss still breaks the hold, and the sue peace re-titles and latches recognition. At minimum, the gate warns: "Vienna's war would reopen 6 titles (41 of 45)."
- **RS-D1:** recognition by defeat. A signed peace that leaves a great power's capital in the French bloc latches recognition as Pressburg does. The table quotes each lever's cost in turns. This amends SR-1a's ruling (2), so it is the user's.
- **RS-10 and RS-16:** make the two Congress lines truthful, and warn before the summons that it lowers the gate.

---

## §7 Method, limits, routing

**Method.**
- **The hand-played campaign:** 28 turns, as above.
- **The eighteen driver arms.** In process and seeded: the three commanded seeds, the spender, the ambient, the two reach roads, the four standing exit arms (first contact, the AAR's typed lines, the Chunk 4 field, the Chunk 5 laws), the sea, the volte-face, propose, advisor, flagship, the tutorial, and the staged Pressburg ending.
- **Six read-only verification agents,** one per defect family: (A) the peace floor, (B) fortification and the what-if, (C) the objection arms, (D) settlement and narration copy, (E) the parser and desk without a key, (F) the Congress and the ending. Each reproduced its rows on a fresh boot or replayed a save, and traced the producer.
- **Two findings of my own,** reproduced on a fresh boot or read from the saves: RS-3 (the garrison probe) and RS-25.

**Limits.** No Godot client pass (UI/UX not re-scored). The interim score does not replace the end-of-mandate re-score. The driver arms are mock-parsed. RS-27's cause is not isolated.

**Routing.**
- **Now (§0-4, a played campaign's P1s jump the queue):** RS-1 + RS-2 as one slice, "The peace holds", ahead of SR-6a. Each fix sits behind its own lever, and `BASELINE_SERIES` is attributed.
- **Chunk 6 (narration, dispatch and copy):**
  - SR-6a: RS-9, RS-17, RS-20, RS-23, RS-24, RS-D2.
  - SR-6b: RS-18, RS-19, RS-21, RS-22, RS-25, RS-26, RS-29.
- **The quick-win bank (`SCORE_MANDATE_PLAN.md` §3), for the next reserves:** RS-4, RS-5, RS-10, RS-12, RS-13, RS-14, RS-15, RS-16, RS-28.
- **Chunk 3b (the CRT queue):** RS-6, RS-7, RS-8, RS-11, unless a reserve takes them first.
- **Chunk 7:** RS-3 (it moves AI behaviour and needs a flip arm) and RS-27 (measure first).
- **The user's gate:** RS-D1. RS-D3 is evidence for SR-G7, the standing alarm floor.
