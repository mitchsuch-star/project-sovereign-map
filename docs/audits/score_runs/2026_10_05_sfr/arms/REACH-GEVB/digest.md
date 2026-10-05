# Playtest digest — REACH-GEVB

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "client_petition": "grant"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `vassalize Bavaria` → ✓ Sire, regarding the Vassalage proposal to Bavaria, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → confirm
  - POPUP proposal_result: Talleyrand departs for the Bavaria court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1968, own corps) vs Mack (lost 20822) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult and Bernadotte never arr… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Lannes, attack Mack` → ✓ MUSTER — Lannes (16,894; expect about 107,448 with the corps likely to arrive) vs Mack (31,178 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 471, own corps) vs Mack (lost 31178) — Soult and Bernadotte never reached the guns. The battle was decided without them, Sire.
- CMD `Davout, attack Mack` → ✓ Mack fell at Swabia on turn 1, Sire — his corps is no more. The nearest in sight is Archduke John at Tyrol — shall Davout engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Swabia on turn 1, Sire — his corps is no more. The nearest in sight is Archduke John at Tyrol — shall Davout engage him? → 1 (first option: Archduke John at Tyrol)
- CMD `Murat, move to Swabia` → ✗ Not enough actions! Need 1, have 0 — Murat cannot march to Swabia today.
- CMD `end turn` → ✓ Turn 1 ended. Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Massena. Casualties: Archdu…
  - ⚔ Archduke Charles (lost 4083) vs Massena (lost 6756) — The margin was slim. Training and preparation would serve Massena well.
  - verbs: attack×1, wait×1
- ORDER Davout [active]: Davout is pursuing Archduke John (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Bavaria, vassalage #6 → accept
  - POPUP proposal_result: You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #3 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 4 · Bavaria vassalage · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1619 · net +1308 · threat 84 · provinces 28 · ceiling 29250 · army 192898 · vassals Bavaria 60 · Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 275 · admin 50 · tribute 1351 · upkeep 2696 · blockade 172 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is destroyed at Swabia — his corps annihilated, his name struck from their order of battle.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Bavaria with a response.
  - TURN EVENTS 4
- DIPLO +11 medium/low (diplomatic_proposal_sent, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, move to Munich` → ✓ Ney moves from Swabia to Munich (460 lost to march)
- CMD `Davout, move to Munich` → ✓ Davout moves from Franconia to Munich (781 lost to march) Davout's pursuit of Archduke John is set aside.
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Swabia to Munich (317 lost to march)
- CMD `Murat, move to Munich` → ✓ Murat moves from Swabia to Munich (461 lost to march)
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 3267 · net +1524 · threat 87 · provinces 28 (+0) · ceiling 33015 · army 187244 · vassals Bavaria 64 · Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 1453 · upkeep 2546 · charges 64 · blockade 219 · admiralty 90
- DISPATCH: Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +8 medium/low (diplomatic_carved_vassal_created, diplomatic_treaty_signed ×4, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 15 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, ma…
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (900 lost to march)
- CMD `Massena, move to Piedmont` → ✓ Massena moves from Milan to Piedmont (2,114 lost to march)
- CMD `end turn` → ✓ Turn 3 ended. Turn 4 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 5108 · net +1659 · threat 85 · provinces 28 (+0) · ceiling 35602 · army 180821 · vassals Bavaria 68 · Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 437 · admin 50 · tribute 1459 · upkeep 2344 · charges 169 · blockade 274 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes and Murat stand 71,436 men at Munich, which feeds 37,500. 33,936 too many. 6,993 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large …
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Soult, move to Munich` → ✓ Soult moves from Swabia to Munich (1,641 lost to march)
- CMD `Bernadotte, move to Munich` → ✓ Bernadotte moves from Franconia to Munich (332 lost to march)
- CMD `Deroy, move to Munich` → ✓ Deroy moves from Franconia to Munich (564 lost to march)
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will move to Milan instead.)
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will move to Milan instead.) → insist
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 7211 · net +1872 · threat 83 · provinces 28 (+0) · ceiling 39708 · army 170067 · vassals Bavaria 72 · Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2590 · trade 512 · admin 50 · tribute 1466 · upkeep 2036 · charges 300 · blockade 320 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Soult, Lannes, Murat, Bernadotte and Deroy stand 128,025 men at Munich, which feeds 37,500. 90,525 too many. 15,160 men lost in 3 turns. Bavaria's magazines feed us as our own — t…
  - TURN EVENTS 4
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria, Naples and Denmark rebuff Prussia (open borders agreement)

## Turn 5 — Late November 1805
- CMD `vassalize Hesse` → ✓ Sire, regarding the Vassalage proposal to Hesse, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #11 → confirm
  - POPUP proposal_result: Talleyrand departs for the Hesse court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `vassalize Saxony` → ✓ Sire, regarding the Vassalage proposal to Saxony, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #12 → confirm
  - POPUP proposal_result: Talleyrand departs for the Saxony court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `declare war on Hanover` → ✗ Talleyrand is currently en route to a foreign court. He cannot negotiate until he returns.
- CMD `Soult, move to Franconia` → ✓ Soult moves from Munich to Franconia (558 lost to march)
- CMD `Bernadotte, move to Franconia` → ✓ Bernadotte moves from Munich to Franconia (153 lost to march)
- CMD `Ney, move to Franconia` → ✓ Ney moves from Munich to Franconia (172 lost to march)
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Munich to Franconia (133 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP proposal_result: Saxony has rejected our Vassalage. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 9255 · net +1903 · threat 81 · provinces 28 (+0) · ceiling 40552 · army 165144 · vassals Bavaria 76 · Holland 100 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 512 · admin 50 · tribute 1472 · upkeep 1870 · charges 441 · blockade 320 · admiralty 90
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Saxony with a response.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the w…
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_proposal_sent ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
  - MAILBOX #9 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Soult, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Bernadotte, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Ney, attack Archduke John` → ✗ No intelligence on Archduke John's position, Sire. Scout for him before Ney can give chase.
- CMD `Deroy, move to Franconia` → ✓ Deroy moves from Munich to Franconia (191 lost to march)
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10747 · net +1328 · threat 79 · provinces 28 (+0) · ceiling 24872 · army 160812 · vassals Bavaria 80 · Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 512 · admin 50 · tribute 1254 · upkeep 1736 · charges 822 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - TURN EVENTS 4
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, coercive_demand)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 14 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, move to Osnabruck` → ✗ Cannot enter Osnabruck — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Munich to Franconia (167 lost to march)
- CMD `Lannes, attack Archduke John` → ✗ No intelligence on Archduke John's position, Sire. Scout for him before Lannes can give chase.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 12270 · net +1347 · threat 77 · provinces 28 (+0) · ceiling 26125 · army 154609 · vassals Bavaria 84 · Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 512 · admin 50 · tribute 1261 · upkeep 1548 · charges 998 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — Ney, Soult, Lannes, Murat, Bernadotte and Deroy stand 93,911 men at Franconia, which feeds 60,000. 33,911 too many. 12,389 men lost in 3 turns. Bavaria's magazines feed us as our own — the arm…
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 8 — Early January 1806
- CMD `Lannes, retreat` → ✗ Lannes is not in danger. No retreat necessary.
- CMD `Massena, attack Archduke John` → ✗ No intelligence on Archduke John's position, Sire. Scout for him before Massena can give chase.
- CMD `Soult, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Napoleon, move to Franconia` → ✓ Napoleon moves from Swabia to Franconia (90 lost to march)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13819 · net +1361 · threat 75 · provinces 28 (+0) · ceiling 27368 · army 148306 · vassals Bavaria 88 · Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 512 · admin 50 · tribute 1267 · upkeep 1352 · charges 1186 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Sweden 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design …
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 9 — Late January 1806
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, attack Hanover` → ✗ Bernadotte cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Massena, move to Milan` → ✓ Massena moves from Piedmont to Milan (985 lost to march)
- CMD `Ney, move to Franconia` → ✗ Ney is already in Franconia.
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15341 · net +1326 · threat 73 · provinces 28 (+0) · ceiling 28138 · army 141524 · vassals Bavaria 92 · Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 512 · admin 50 · tribute 1274 · upkeep 1158 · charges 1382 · contributions 150 · blockade 320 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Sardinia 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her desig…
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, move to Oldenburg` → ✓ Bernadotte begins marching to Oldenburg (distance: 4). Moved to Frankfurt. Route: Frankfurt -> Brunswick -> Hanover -> Oldenburg.
- CMD `Deroy, move to Franconia` → ✗ Deroy is already in Franconia.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Brutal stalemate between Archduke Charles and Massena. Heavy casualties on … · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Charle…
  - ⚔ Archduke Charles (lost 3777) vs Massena (lost 3140, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 2313) vs Teulie (lost 1237, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×2, naval_expedition×1
- ORDER Bernadotte [active]: Bernadotte is marching to Oldenburg (4 turns remaining).
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 16326 · net +1180 · threat 71 · provinces 28 (+0) · ceiling 26822 · army 130906 · vassals Bavaria 94 · Holland 98 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2590 · trade 512 · admin 50 · tribute 1214 · upkeep 1016 · charges 1610 · contributions 150 · blockade 320 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 3137 gold.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #14 → reject_settlement_offer
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Deroy, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Hiller.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, move to Franconia` → ✗ Soult is already in Franconia.
- CMD `Napoleon, move to Swabia` → ✓ Napoleon moves from Franconia to Swabia (74 lost to march)
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- ORDER Bernadotte [continues]: Bernadotte marches to Brunswick. 2 regions to Oldenburg.
- ENVOYS WAITING 1 · Naples open borders
- LEDGER treasury 17615 · net +1094 · threat 69 · provinces 28 (+0) · ceiling 27077 · army 127896 · vassals Bavaria 98 · Holland 98 · Kingdom of Italy 99 · Switzerland 92
  - NET income 2590 · trade 512 · admin 50 · tribute 1221 · upkeep 984 · charges 1805 · contributions 80 · blockade 320 · admiralty 90
- DISPATCH: Sire — Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL agenda_violation: Prussia seethes: France's columns cross Brunswick in defiance of its declared neutrality.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
- CMD `invest in Saxony` → ✗ Saxony is not a vassal.
- CMD `Soult, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Davout, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Hiller.
- CMD `Massena, move to Swabia` → ✓ Massena begins marching to Swabia (distance: 2). Moved to Munich. Route: Munich -> Swabia.
- CMD `Murat, move to Franconia` → ✗ Murat is already in Franconia.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 10 actions, 3 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos's assault collapses into chaos! Brutal stalemate between Castanos and Paget. Heavy casualties on both sides: C… · Castanos struggles in a costly engagement. Brutal stalemate between Castanos and Paget. Heavy casualties on both sides:… · Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 534, Paget's army 803…
  - ⚔ Castanos (lost 759) vs Paget (lost 700, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 647) vs Paget (lost 583, own corps) — Stalemate. Paget and Castanos glare at each other across the field. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 534) vs Paget (lost 536, own corps) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better. — The Line Holds +15% (Paget)
  - verbs: move×4, attack×3, fortify×2, wait×1
- ORDER Bernadotte [continues]: Bernadotte marches to Hanover. 1 region to Oldenburg.
- ORDER Massena [active]: Massena is marching to Swabia (2 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- LEDGER treasury 19442 · net +1478 · threat 67 · provinces 28 (+0) · ceiling 36076 · army 123491 · vassals Bavaria 100 · Holland 98 · Kingdom of Italy 99 · Switzerland 91
  - NET income 2590 · trade 537 · admin 50 · tribute 1227 · upkeep 952 · charges 1548 · blockade 336 · admiralty 90
- DISPATCH: Sire — London now pays St Petersburg 400 gold a turn against us — her war with us is paid for.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: 30 approaches rebuffed, chiefly from Denmark and Prussia (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Soult, attack Vienna` → ✗ Soult cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `Deroy, attack Vienna` → ✗ Deroy cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `Davout, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `Napoleon, move to Lorraine` → ✓ Napoleon moves from Swabia to Lorraine
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 5 actions, 1 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos delivers an effective strike. Castanos gains the advantage over Wellesley. Casualties: Castanos 261, Wellesley…
  - ⚔ Castanos (lost 261) vs Wellesley (lost 424) — A skirmish, Sire. Wellesley's men traded shots with Castanos; there was no battle to speak of. — The Line Holds +15% (Wellesley)
  - verbs: recruit×2, unfortify×1, wait×1, attack×1
- ORDER Bernadotte [completed]: Bernadotte arrives at Oldenburg. Bernadotte: "Done, and done properly — no stragglers, no surprises."
- ORDER Massena [completed]: Massena arrives at Swabia. Massena: "Done — and I trust the next order has more fire in it."
- LEDGER treasury 20959 · net +1546 · threat 65 · provinces 28 (+0) · ceiling 37760 · army 120242 · vassals Bavaria 100 · Holland 98 · Kingdom of Italy 99 · Switzerland 90
  - NET income 2590 · trade 537 · admin 50 · tribute 1459 · upkeep 920 · charges 1744 · blockade 336 · admiralty 90
- DISPATCH: Sire — London now pays Vienna 400 gold a turn against us — her war with us is paid for.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_ai_proposal_refused: 18 approaches from Prussia, Naples and Denmark are rebuffed (open borders agreement)

## Turn 14 — Early April 1806
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Franconia to Swabia (161 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Napoleon, move to Orleanais` → ✓ Napoleon moves from Lorraine to Orleanais
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 10 actions, 3 attacks — Russia, the Ottoman Empire, Sweden and 2 other courts stirred as well, but their formations remain beyond our sight. — Castanos takes Andalusia where he stands! Captured: Britain → Spain · Castanos engages in solid combat. Castanos gains the advantage over Wellesley. Casualties: Castanos 104, Wellesley 343.… · Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 255, Paget 643. Both …
  - 🏴 Spain: Castanos takes Andalusia where he stands! Captured: Britain → Spain
  - ⚔ Castanos (lost 104) vs Wellesley (lost 343) — The line gave way. Wellesley is falling back, and not in good order. — The Line Holds +15% (Wellesley)
  - ⚔ Castanos (lost 255) vs Paget (lost 643) — Hardly an engagement, Sire — a brush between Paget and Castanos, and the day moved on. — The Line Holds +15% (Paget)
  - verbs: recruit×3, attack×3, move×1, unfortify×1, form_square×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 21872 · net +738 · threat 63 · provinces 28 (+0) · ceiling 27758 · army 118594 · vassals Bavaria 100 · Holland 98 · Kingdom of Italy 99 · Switzerland 89
  - NET income 2590 · trade 537 · admin 50 · tribute 1466 · upkeep 912 · charges 2487 · contributions 80 · blockade 336 · admiralty 90
- DISPATCH: Sire — Wellesley has crossed into Bearn. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 15 — Late April 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (89 → 99); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Bernadotte, move to Hanover` → ✓ Bernadotte moves from Oldenburg to Hanover (108 lost to march)
- CMD `Napoleon, move to Paris` → ✓ Napoleon begins marching to Paris (distance: 3). Moved to Burgundy. Route: Burgundy -> Limousin -> Paris.
- CMD `Murat, move to Paris` → ✓ Murat begins marching to Paris (distance: 6). Moved to Swabia. Route: Swabia -> Lorraine -> Orleanais -> Burgundy -> Limousin -> Paris.
- CMD `end turn` → ✓ Turn 15 ended. Turn 16 begins!
- enemy phase: 11 actions, 3 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Hiller attacks with overwhelming force. Brutal stalemate between Hiller and Teulie. Heavy casualties on both sides: Hil… · Castanos faces a difficult fight. Castanos gains the advantage over Paget. Casualties: Castanos 109, Paget 506. Both ar… · Castanos launches a devastating assault! Castanos gains the advantage over Wellesley. Casualties: Castanos 86, Wellesle…
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Bearn!
  - 🏴 Spain: [!] MARSHAL CAPTURED — Wellesley is taken by Spain at Gascony!
  - ⚔ Hiller (lost 552) vs Teulie (lost 764) — Stalemate. Teulie and Hiller glare at each other across the field.
  - ⚔ Castanos (lost 109) vs Paget (lost 506) — Paget was driven from the field. His men are scattered. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 86) vs Wellesley (lost 287) — Wellesley was driven from the field. His men are scattered. And Wellesley was taken on that field — Spain holds him. — The Line Holds +15% (Wellesley)
  - verbs: attack×3, unfortify×2, move×2, recruit×2, break_square×1, fortify×1
- ORDER Murat [active]: Murat is marching to Paris (3 turns remaining).
- ORDER Napoleon [active]: Napoleon is marching to Paris (3 turns remaining).
- ENVOYS WAITING 2 · Britain armistice losing · Russia armistice losing
- LEDGER treasury 22994 · net +982 · threat 61 · provinces 28 (+0) · ceiling 32931 · army 117360 · vassals Bavaria 100 · Holland 98 · Kingdom of Italy 98 · Switzerland 99
  - NET income 2574 · trade 537 · admin 50 · tribute 1225 · upkeep 904 · charges 2074 · blockade 336 · admiralty 90
- DISPATCH: Sire — Wellesley has crossed into Gascony. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 16 — Early May 1806
  - MAILBOX #13 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #14 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #17 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Russia. Your earlier answer was not delivered; the mat…
  - POPUP diplomatic_dialogue: incoming_proposal #18 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
  - POPUP diplomatic_dialogue: Britain, armistice_losing #17 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #18 → accept
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Napoleon, recruit infantry` → ✓ Napoleon recruits 3,000 infantry at Burgundy (field levy — no depot; capped at 3,000) - Cost: 510 gold (×3 at war) (Napoleon's intendance: -15%). Morale: 70% -> 61%
- CMD `Massena, move to Paris` → ✓ Massena begins marching to Paris (distance: 5). Moved to Lorraine. Route: Lorraine -> Orleanais -> Burgundy -> Limousin -> Paris.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 17, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- SPENT 510g on this turn's orders
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Teulie. Casualties: Arc… · Hiller engages in solid combat. Ney holds the line. Casualties: Hiller 1,635, Ney's army 316. Both armies remain in the… · Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Ney. Heavy casualties on bo…
  - ⚔ Archduke Charles (lost 553) vs Teulie (lost 3414) — The toll on Teulie's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Hiller (lost 1635) vs Ney (lost 124, own corps) — Reinforcements! Murat marched onto the field beside Ney. The enemy's advantage melted away. — The corps system brought Murat in.
  - ⚔ Archduke Charles (lost 3360) vs Ney (lost 1420, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×3, recruit×2, fortify×1
- ORDER Massena [active]: Massena is marching to Paris (5 turns remaining).
- ORDER Murat [active]: Murat answered the guns this turn and stands at Franconia; his march resumes next turn.
- ORDER Napoleon [continues]: Napoleon marches to Limousin. 1 region to Paris.
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 1,642 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 1,642 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +5 (95 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 23291 · net +673 · threat 59 · provinces 28 (+0) · ceiling 29565 · army 115247 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 91 · Switzerland 98
  - NET income 2578 · trade 537 · admin 50 · tribute 768 · upkeep 888 · charges 2282 · admiralty 90
- DISPATCH: Sire — Teulie was mauled at Milan: half of his corps — 3,414 men — lost in a single action.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 7
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And Britain stirs at its own design.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, blockade_broken ×2)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Brutal stalemate between Archduke Charles and Ney. Heavy casualties on both s… · Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Lannes. Casualties: Archduke Char…
  - ⚔ Archduke Charles (lost 2729) vs Ney (lost 1346, own corps) — Soult failed to arrive in time. Ney's army fought without expected support.
  - ⚔ Archduke Charles (lost 2432) vs Lannes (lost 976, own corps) — Lannes fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×2, recruit×2, retreat×1, stance_change×1
- ORDER Napoleon [completed]: Napoleon arrives at Paris.
- ORDER Massena [interrupted]: Massena hears cannon fire! Abandoning orders — rushing to Franconia! Massena moves from Lorraine to Swabia (390 lost to march)
- ORDER Murat [continues]: Murat hears cannon fire at Franconia but cannot answer it — no road leads there. His march continues.
- LEDGER treasury 23562 · net +493 · threat 57 · provinces 28 (+0) · ceiling 27821 · army 106715 · vassals Bavaria 100 · Holland 97 · Kingdom of Italy 81 · Switzerland 96
  - NET income 2581 · trade 537 · admin 50 · tribute 723 · upkeep 816 · charges 2492 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ORDER Murat [continues]: Murat marches to Lorraine. 4 regions to Paris.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 24066 · net +375 · threat 55 · provinces 28 (+0) · ceiling 27218 · army 106631 · vassals Bavaria 100 · Holland 96 · Kingdom of Italy 81 · Switzerland 96
  - NET income 2585 · trade 537 · admin 50 · tribute 730 · upkeep 816 · charges 2621 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Vienna 300 gold a turn against us — her war with us is paid for.
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Ney. Casualties: Archduke Charl… · ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,671 troops. Garrison…
  - ⚔ Archduke Charles (lost 1214) vs Ney (lost 2957, own corps) — Massena never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×2, unfortify×1, move×1, recruit×1
- ORDER Murat [interrupted]: Murat hears cannon fire! Abandoning orders — rushing to Franconia! [Cavalry] Murat's cavalry thunders across Swabia to strike! (Cavalry Charge: 2-reg…
  - ⚔ [Cavalry] Murat's cavalry thunders across Swabia to strike! (Cavalry Charge: 2-region attack)
- LEDGER treasury 23541 · net +153 · threat 53 · provinces 28 (+0) · ceiling 24661 · army 84707 · vassals Bavaria 100 · Holland 91 · Kingdom of Italy 77 · Switzerland 92
  - NET income 2590 · trade 537 · admin 50 · tribute 660 · upkeep 656 · charges 2938 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 9
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha…
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 2586) vs Deroy (lost 1254, own corps) — Massena's timely arrival aided Deroy. Soult, however, was conspicuously absent. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: attack×2, move×1
- LEDGER treasury 22703 · net -505 · threat 41 · provinces 28 (+0) · ceiling 19171 · army 77599 · vassals Bavaria 100 · Holland 88 · Switzerland 90
  - NET income 2590 · trade 549 · admin 50 · tribute 296 · upkeep 592 · charges 2964 · blockade 344 · admiralty 90
- DISPATCH: Sire — Deroy's corps has been broken at Munich. He must reform before he fights again.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_begins ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Davout. Casualties: Archduke Ch… · ArchdukeJohn marches from Piedmont into Provence unopposed! (196 lost to march) Captured: France → Austria · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Massena. Casualties: Archduke C…
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (196 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 1439) vs Davout (lost 3657) — Davout stood alone, Sire. Soult never came.
  - ⚔ Archduke Charles (lost 1738) vs Massena (lost 3441, own corps) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×3, fortify×1
- LEDGER treasury 21476 · net -637 · threat 39 · provinces 27 (-1) · ceiling 17168 · army 67197 · vassals Bavaria 100 · Holland 85 · Switzerland 86
  - NET income 2440 · trade 549 · admin 50 · tribute 144 · upkeep 504 · charges 2882 · blockade 344 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Piedmont.
  - RAIL agenda_violation: Prussia seethes: France's columns cross Hanover in defiance of its declared neutrality.
  - TURN EVENTS 7
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Ch… · ArchdukeJohn marches from Provence into Lyonnais unopposed! (194 lost to march) Captured: France → Austria · ArchdukeJohn marches from Lyonnais into Limousin unopposed! (192 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Lyonnais unopposed! (194 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Limousin unopposed! (192 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 936) vs Deroy (lost 2339, own corps) — A grievous defeat for Deroy, Sire. The losses are severe.
  - verbs: attack×3
- ORDER Murat [awaiting_response]: Murat is cornered at Swabia with 3,572 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Swabia with 3,572 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 20316 · net -412 · threat 36 · provinces 25 (-2) · ceiling 17605 · army 54859 · vassals Bavaria 100 · Holland 84 · Switzerland 84
  - NET income 2250 · trade 549 · admin 50 · tribute 373 · upkeep 416 · charges 2784 · blockade 344 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 7
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, balance_of_europe_shifted, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria · Archduke John engages in solid combat. Archduke John gains the advantage over Napoleon. Casualties: Archduke John 1,068… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Soult. Casualties: Archduke Cha… · ArchdukeJohn marches from Limousin into Berry unopposed! (179 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeJohn marches from Limousin into Berry unopposed! (179 lost to march) Captured: France → Austria
  - ⚔ Archduke John (lost 1068) vs Napoleon (lost 2440) — The margin was slim. Training and preparation would serve Napoleon well.
  - ⚔ Archduke Charles (lost 783) vs Soult (lost 3770, own corps) — Soult held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×4
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 18404 · net -1132 · threat 33 · provinces 24 (-1) · ceiling 12936 · army 45171 · vassals Bavaria 100 · Holland 81 · Switzerland 80
  - NET income 2082 · trade 549 · admin 50 · tribute 355 · upkeep 336 · charges 3398 · blockade 344 · admiralty 90
- DISPATCH: Sire — Berry has fallen to Austria. Enemy colours fly over French homeland soil. Archduke John's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as …
  - RAIL expedition_landed: THE LANDING: Paget has put 4,909 men ashore at Piedmont.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
  - MAILBOX #16 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #20 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 17201 · net -617 · threat 30 · provinces 24 (+0) · ceiling 14220 · army 45171 · vassals Bavaria 100 · Holland 82 · Switzerland 80
  - NET income 2086 · trade 549 · admin 50 · tribute 697 · upkeep 336 · charges 3149 · contributions 80 · blockade 344 · admiralty 90
- DISPATCH: Sire — Berry, Limousin, Lyonnais and 1 more lie in enemy hands. Austria holds them.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: 7 courts rebuff Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (400g/turn)

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 16593 · net -482 · threat 27 · provinces 24 (+0) · ceiling 14263 · army 45171 · vassals Bavaria 100 · Holland 83 · Switzerland 80
  - NET income 2091 · trade 549 · admin 50 · tribute 701 · upkeep 336 · charges 3023 · contributions 80 · blockade 344 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Savoy. No French corps stands in his path.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 16116 · net -378 · threat 24 · provinces 24 (+0) · ceiling 14287 · army 45171 · vassals Bavaria 100 · Holland 84 · Switzerland 80
  - NET income 2095 · trade 536 · admin 50 · tribute 706 · upkeep 336 · charges 2924 · contributions 80 · blockade 335 · admiralty 90
- DISPATCH: Sire — relations between France and Prussia have collapsed: Open Borders → Peace.
  - TURN EVENTS 1
- DIPLO +6 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: France–Prussia (OPEN BORDERS → PEACE)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 16250 · net +110 · threat 21 · provinces 24 (+0) · ceiling 16870 · army 45171 · vassals Bavaria 100 · Holland 85 · Switzerland 80
  - NET income 2100 · trade 536 · admin 50 · tribute 710 · upkeep 336 · charges 2525 · blockade 335 · admiralty 90
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
  - TURN EVENTS 1
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 15858 · net -311 · threat 18 · provinces 24 (+0) · ceiling 14355 · army 45171 · vassals Bavaria 100 · Holland 86 · Switzerland 80
  - NET income 2100 · trade 536 · admin 50 · tribute 715 · upkeep 336 · charges 2871 · contributions 80 · blockade 335 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Savoy. No French corps stands in his path.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 2
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria, Britain and Russia remain at war with us.
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Davout. Casualties: Arc… · Archduke John's forces advance steadily. Archduke John gains the advantage over Napoleon. Casualties: Archduke John 604… · Hiller delivers an effective strike. Hiller gains the advantage over Deroy. Casualties: Hiller 108, Deroy 1,155. Both a…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franche-Comte. (1,045 lost to march) Franche-Comte has been captured by Austria!
  - 🏴 Austria: [!] MARSHAL CAPTURED — Deroy is taken by Austria at Munich!
  - ⚔ Archduke Charles (lost 614) vs Davout (lost 2584, own corps) — Massena arrived to reinforce Davout, but Deroy failed to reach the field in time.
  - ⚔ Archduke John (lost 604) vs Napoleon (lost 3368) — A grievous defeat for Napoleon, Sire. The losses are severe.
  - ⚔ Hiller (lost 108) vs Deroy (lost 1155) — Even the favorable ground could not save Deroy, Sire. Hiller overcame the terrain. And Deroy was taken on that field — …
  - verbs: attack×3, unfortify×2
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 14653 · net -540 · threat 15 · provinces 23 (-1) · ceiling 12428 · army 32768 · vassals Bavaria 98 · Holland 81 · Switzerland 74
  - NET income 2002 · trade 536 · admin 50 · tribute 697 · upkeep 248 · charges 3072 · contributions 80 · blockade 335 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps sta…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent)

## Turn 30 — Early December 1806
  - MAILBOX #17 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #21 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Davout. Casualties: Archduke Char… · ArchdukeJohn assaults the Normandy garrison! Garrison: 12,000 -> 6,584 (-5,416). ArchdukeJohn loses 3,333 troops. Garri… · Archduke Charles executes a brilliant maneuver! Archduke Charles gains the advantage over Soult. Casualties: Archduke C…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Davout is taken by Austria at Munich!
  - 🏴 Austria: [!] MARSHAL CAPTURED — Soult is taken by Austria at Munich!
  - ⚔ Archduke Charles (lost 480) vs Davout (lost 2059, own corps) — Davout's fortified position was overwhelmed. A costly investment lost, Sire. And Davout was taken on that field — Austr…
  - ⚔ Archduke Charles (lost 215) vs Soult (lost 1875, own corps) — The hills were ours, but Archduke Charles took them. Soult's position was overrun. And Soult was taken on that field — …
  - verbs: attack×3, move×1, grant_dotation×1
- LEDGER treasury 13676 · net -314 · threat 12 · provinces 23 (+0) · ceiling 12410 · army 23216 · vassals Bavaria 85 · Holland 78 · Switzerland 70
  - NET income 2002 · trade 536 · admin 50 · tribute 679 · upkeep 176 · charges 2900 · contributions 80 · blockade 335 · admiralty 90
- DISPATCH: Sire — Marshal Davout has been taken. Austria holds him prisoner.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Massena. Casualties: Archduke C… · ArchdukeJohn assaults the Normandy garrison! Garrison collapses (6,584 -> 0). ArchdukeJohn loses 1,829 troops in the as… · ArchdukeCharles marches from Franche-Comte into Lorraine unopposed! (984 lost to march) Captured: France → Austria · Archduke John attacks with overwhelming force. Archduke John gains the advantage over Napoleon. Casualties: Archduke Jo…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -91g, France -164g. Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Franche-Comte into Lorraine unopposed! (984 lost to march) Captured: France → Austria
  - 🏴 Austria: FORCED RETREAT! ArchdukeJohn advances into Artois. (117 lost to march) Artois has been captured by Austria!
  - ⚔ Archduke Charles (lost 273) vs Massena (lost 4606) — The hills were ours, but Archduke Charles took them. Massena's position was overrun.
  - ⚔ Archduke John (lost 165) vs Napoleon (lost 1444) — Napoleon's army has been badly mauled. Archduke John proved the stronger force today.
  - verbs: attack×4
- ORDER Massena [awaiting_response]: Massena is cornered at Munich with 4,714 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Munich with 4,714 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 13163 · net -5 · threat 9 · provinces 20 (-3) · ceiling 13139 · army 11926 · vassals Bavaria 83 · Holland 73 · Switzerland 64
  - NET income 1751 · trade 536 · admin 50 · tribute 649 · upkeep 88 · charges 2478 · blockade 335 · admiralty 90
- DISPATCH: Sire — Normandy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL agenda_violation: Prussia seethes: France's columns cross Hanover in defiance of its declared neutrality.
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_relation_shift)

## Turn 32 — Early January 1807
  - MAILBOX #18 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (73 → 77); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John's forces advance steadily. Archduke John gains the advantage over Napoleon. Casualties: Archduke John 57,… · ArchdukeCharles marches from Lorraine into Rhineland unopposed! (955 lost to march) Captured: France → Austria · ArchdukeJohn marches from Artois into Champagne unopposed! (115 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Lorraine into Rhineland unopposed! (955 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Artois into Champagne unopposed! (115 lost to march) Captured: France → Austria
  - ⚔ Archduke John (lost 57) vs Napoleon (lost 629) — Napoleon was driven from the field. His men are scattered.
  - verbs: attack×3
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Paris — 601 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Paris — 601 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 2 · Austria peace · Switzerland client petition
- LEDGER treasury 12257 · net -654 · threat 6 · provinces 18 (-2) · ceiling 9658 · army 10696 · vassals Bavaria 81 · Holland 75 · Switzerland 60
  - NET income 1583 · trade 536 · admin 50 · tribute 346 · upkeep 80 · charges 2584 · contributions 80 · blockade 335 · admiralty 90
- DISPATCH: Sire — Rhineland has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standin…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 33 — Late January 1807
  - MAILBOX #19 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #20 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, peace #23 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #24 → grant the petition
  - POPUP diplomatic_dialogue: Austria, peace #23 → accept
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (60 → 64); bond 40 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
  - POPUP diplomatic_dialogue: Switzerland, client_petition #24 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Dumonceau [continues]: Dumonceau marches to Flanders. 3 regions to Paris.
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 10346 · net +48 · threat 4 · provinces 18 (+0) · ceiling 10641 · army 57696 · vassals Bavaria 79 · Holland 75 · Switzerland 54
  - NET income 1588 · trade 548 · admin 50 · tribute 126 · upkeep 400 · charges 1352 · contributions 80 · blockade 342 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL status_quo_conceded: Artois, Berry, Champagne, Franche-Comte, Limousin, Lorraine, Lyonnais, Normandy, Provence and Rhineland — left with Austria by the peace, titled to t…
  - RAIL status_quo_conceded: Franconia and Swabia — left with Austria by the peace, titled to them by treaty.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_coalition_brewing_other)
  - LOG coalition_brewing_started: Coalition brewing against Austria — Russia consulting (their alarm: 63)

## Turn 34 — Early February 1807
  - MAILBOX #21 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #25 → grant the petition
  - POPUP proposal_result: Bavaria's tribute is remitted for 8 collections (1008g forgone). Loyalty +4 (79 → 83); bond 59 → 59 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Dumonceau [continues]: Dumonceau marches to Picardy. 2 regions to Paris.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 10253 · net -77 · threat 2 · provinces 18 (+0) · ceiling 9771 · army 54876 · vassals Bavaria 81 · Holland 75 · Switzerland 44
  - NET income 1592 · trade 498 · admin 50 · upkeep 400 · charges 1336 · contributions 80 · blockade 311 · admiralty 90
- DISPATCH: Sire — Artois, Berry, Champagne and 7 more lie in enemy hands. Austria holds them.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 35 — Late February 1807
  - MAILBOX #22 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #26 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Normandy into Maine unopposed! (956 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Normandy into Maine unopposed! (956 lost to march) Captured: France → Britain
  - verbs: attack×1
- ORDER Dumonceau [continues]: Dumonceau marches to Artois. 1 region to Paris.
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 10180 · net -62 · threat 0 · provinces 17 (-1) · ceiling 9796 · army 52226 · vassals Bavaria 79 · Holland 75 · Switzerland 34
  - NET income 1516 · trade 498 · admin 50 · upkeep 400 · charges 1325 · blockade 311 · admiralty 90
- DISPATCH: Sire — Maine has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 36 — Early March 1807
  - MAILBOX #23 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #27 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Berry into Gascony unopposed! (1,800 lost to march) Captured: France → Britain · Paget struggles in a costly engagement. Paget gains the advantage over Ney. Casualties: Paget's army 2,590, Ney's army …
  - 🏴 Britain: Moore marches from Berry into Gascony unopposed! (1,800 lost to march) Captured: France → Britain
  - ⚔ Paget (lost 549, own corps) vs Ney (lost 937, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - verbs: attack×2
- ORDER Dumonceau [active]: Dumonceau answered the guns this turn and stands at Artois; his march resumes next turn.
- LEDGER treasury 9821 · net -72 · threat 0 · provinces 16 (-1) · ceiling 9378 · army 45299 · vassals Bavaria 75 · Holland 72 · Switzerland 22
  - NET income 1389 · trade 498 · admin 50 · upkeep 320 · charges 1288 · blockade 311 · admiralty 90
- DISPATCH: Sire — Gascony has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 2
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_treaty_signed, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, agenda_shift)
  - LOG ai_ai_proposal_refused: Austria rebuffs Russia (design ask)

## Turn 37 — Late March 1807
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Dumonceau [completed]: Dumonceau arrives at Paris. Dumonceau: "Accomplished as ordered. The army is intact."
- LEDGER treasury 9761 · net -51 · threat 0 · provinces 16 (+0) · ceiling 9451 · army 43228 · vassals Bavaria 73 · Holland 72 · Switzerland 12
  - NET income 1393 · trade 498 · admin 50 · upkeep 312 · charges 1279 · blockade 311 · admiralty 90
- DISPATCH: Sire — Artois, Berry, Champagne and 9 more lie in enemy hands. Austria and Britain hold them.
  - TURN EVENTS 2
- DIPLO +6 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 38 — Early April 1807
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 9763 · net +2 · threat 0 · provinces 16 (+0) · ceiling 9773 · army 41280 · vassals Bavaria 71 · Holland 72 · Switzerland 2
  - NET income 1398 · trade 498 · admin 50 · upkeep 264 · charges 1279 · blockade 311 · admiralty 90
- DISPATCH: Sire — Marshal Murat's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Maine into Anjou unopposed! (466 lost to march) Captured: France → Britain · Moore marches from Anjou into Guyenne unopposed! (435 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Maine into Anjou unopposed! (466 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Anjou into Guyenne unopposed! (435 lost to march) Captured: France → Britain
  - verbs: attack×2
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 9276 · net -55 · threat 0 · provinces 14 (-2) · ceiling 8991 · army 39446 · vassals Bavaria 69 · Holland 72
  - NET income 1182 · trade 498 · admin 50 · tribute 337 · upkeep 264 · charges 1417 · contributions 40 · blockade 311 · admiralty 90
- DISPATCH: Sire — Anjou has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_vassal_transferred: Switzerland passes from France's suzerainty to Britain's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Britain's gold turns Switzerland against France.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3905 gold.
  - TURN EVENTS 2
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
  - MAILBOX #24 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #29 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Guyenne into Bordelais unopposed! (463 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Guyenne into Bordelais unopposed! (463 lost to march) Captured: France → Britain
  - verbs: attack×1
- ENVOYS WAITING 1 · Switzerland open borders
- LEDGER treasury 9157 · net -96 · threat 0 · provinces 13 (-1) · ceiling 8663 · army 37726 · vassals Bavaria 67 · Holland 72
  - NET income 1106 · trade 510 · admin 50 · tribute 337 · upkeep 256 · charges 1394 · contributions 40 · blockade 319 · admiralty 90
- DISPATCH: Sire — Bordelais has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standin…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - RAIL diplomatic_armistice_expired_peace: The armistice between France and Russia has concluded. Peace declared.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

---
finished: **completed** · commands 109 · popups 60 · battles 36
