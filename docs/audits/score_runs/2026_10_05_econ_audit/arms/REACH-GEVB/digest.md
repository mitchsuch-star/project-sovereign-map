# Playtest digest — REACH-GEVB

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "client_petition": "grant"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `c14678984809` (dirty) · content `d4a1fdd2fc4f` · driver `e498338939cb`
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
  - LOG ai_ai_proposal_refused: 17 approaches from Prussia and Austria are rebuffed (open borders agreement)
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
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (open borders agreement)
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
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 4
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

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
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_proposal_sent ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

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
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 13 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

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
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 8 — Early January 1806
- CMD `Lannes, retreat` → ✗ Lannes is not in danger. No retreat necessary.
- CMD `Massena, attack Archduke John` → ✗ No intelligence on Archduke John's position, Sire. Scout for him before Massena can give chase.
- CMD `Soult, move to Brunswick` → ✓ Soult begins marching to Brunswick (distance: 2). Moved to Frankfurt. Route: Frankfurt -> Brunswick.
- CMD `Napoleon, move to Franconia` → ✓ Napoleon moves from Swabia to Franconia (90 lost to march)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Soult [active]: Soult is marching to Brunswick (2 turns remaining).
- LEDGER treasury 13781 · net +1327 · threat 75 · provinces 28 (+0) · ceiling 26990 · army 149703 · vassals Bavaria 88 · Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 512 · admin 50 · tribute 1267 · upkeep 1390 · charges 1182 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Spain rebuffs Austria and Prussia (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Frankfurt! Range: 1, Distance: 2
- CMD `Bernadotte, attack Hanover` → ✗ Bernadotte cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Massena, move to Milan` → ✓ Massena moves from Piedmont to Milan (985 lost to march)
- CMD `Ney, move to Franconia` → ✗ Ney is already in Franconia.
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Soult [completed]: As ordered: "move to Brunswick". Soult arrives at Brunswick. Soult stands ready for instruction.
- LEDGER treasury 15225 · net +1256 · threat 73 · provinces 28 (+0) · ceiling 27347 · army 144298 · vassals Bavaria 92 · Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 512 · admin 50 · tribute 1274 · upkeep 1240 · charges 1370 · contributions 150 · blockade 320 · admiralty 90
- DISPATCH: Sire — Hanover and Prussia have made peace without us.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
  - RAIL agenda_violation: Prussia seethes: France's columns cross Brunswick in defiance of its declared neutrality.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `Soult, attack Hanover` → ✓ Choose your war purpose against Prussia. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #14 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #15 → force_declare_war
  - POPUP diplomatic_objection: diplomatic_declare_war, Prussia → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #16 → ally_entry_proceed_without
- CMD `Bernadotte, move to Oldenburg` → ✓ Bernadotte begins marching to Oldenburg (distance: 4). Moved to Frankfurt. Route: Frankfurt -> Brunswick -> Hanover -> Oldenburg.
- CMD `Deroy, move to Franconia` → ✗ Deroy is already in Franconia.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 1 action unused) Turn 11 begins!
- enemy phase: 5 actions, 5 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Brutal stalemate between Archduke Charles and Massena. Heavy casualties on bo… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Ch… · Brunswick marches from East Frisia into Artois unopposed! (1,180 lost to march) Captured: France → Prussia · Brunswick assaults the Paris garrison! Garrison: 25,000 -> 12,500 (-12,500). Brunswick loses 6,313 troops. Garrison hol…
  - 🏴 Prussia: Brunswick marches from East Frisia into Artois unopposed! (1,180 lost to march) Captured: France → Prussia
  - ⚔ Archduke Charles (lost 4385) vs Massena (lost 3037, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 2515) vs Teulie (lost 1266, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×5
- ORDER Bernadotte [active]: Bernadotte is marching to Oldenburg (4 turns remaining).
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 15068 · net +990 · threat 91 · provinces 27 (-1) · ceiling 23151 · army 135619 · vassals Bavaria 96 · Holland 99 · Kingdom of Italy 98 · Switzerland 94
  - NET income 2418 · trade 487 · admin 50 · tribute 1214 · upkeep 1072 · charges 1599 · contributions 150 · requisitions 37 · blockade 305 · admiralty 90
- DISPATCH: Sire — Artois has fallen to Prussia. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing t…
  - RAIL diplomatic_war_declared: France has declared war on Prussia, shattering the Open Borders Agreement, with 1 allied court poised to follow.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 2835 gold.
  - TURN EVENTS 6
- DIPLO +5 medium/low (witness_strike_recorded, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Britain, Russia and Austria (defensive alliance)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG diplomatic_treaty_broken: France has broken the Open Borders Agreement with Prussia by declaring war.
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG vassal_auto_join_war: Vassal Bavaria joined France's war.

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → reject_settlement_offer
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Deroy, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Hiller.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, move to Franconia` → ✓ Soult begins marching to Franconia (distance: 2). Moved to Frankfurt. Route: Frankfurt -> Franconia.
- CMD `Napoleon, move to Swabia` → ✓ Napoleon moves from Franconia to Swabia (76 lost to march)
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Brunswick assaults the Paris garrison! Garrison collapses (8,250 -> 0). Brunswick loses 2,083 troops in the assault. Br… · Brunswick assaults the Normandy garrison! Garrison collapses (6,000 -> 0). Brunswick loses 1,894 troops in the assault.… · Brunswick marches from Normandy into Berry unopposed! (209 lost to march) Captured: France → Prussia
  - 🏴 Prussia: [Materiel] Guns, horses and stores lost with the fallen: Prussia -104g, France -206g. Captured: France → Prussia
  - 🏴 Prussia: [Materiel] Guns, horses and stores lost with the fallen: Prussia -94g, France -150g. Captured: France → Prussia
  - 🏴 Prussia: Brunswick marches from Normandy into Berry unopposed! (209 lost to march) Captured: France → Prussia
  - verbs: attack×3
- ORDER Bernadotte [continues]: Bernadotte marches to Brunswick. 2 regions to Oldenburg.
- ORDER Soult [active]: Soult is marching to Franconia (2 turns remaining).
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14491 · net +24 · threat 91 · provinces 25 (-2) · ceiling 14618 · army 133647 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2107 · trade 487 · admin 50 · tribute 1221 · upkeep 1076 · charges 2318 · occupation 52 · blockade 305 · admiralty 90
- DISPATCH: Sire — Paris HAS FALLEN. Our capital is in Prussia's hands, and every courier in Europe is already carrying the news.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #18 → grant the petition
  - POPUP proposal_result: Brunswick is ceded to Holland. Loyalty +0 (100 → 100, already full); bond -15 → 5 (+0 a turn). Cost: 1 DP. Our net rises by 35g a turn — 37g of income forfeited, 52g of occupation relieved, 28g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- CMD `invest in Saxony` → ✗ Saxony is not a vassal.
- CMD `Soult, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Davout, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Hiller.
- CMD `Massena, move to Swabia` → ✓ Massena begins marching to Swabia (distance: 2). Moved to Munich. Route: Munich -> Swabia.
- CMD `Murat, move to Franconia` → ✗ Murat is already in Franconia.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Brunswick marches from Berry into Gascony unopposed! (399 lost to march) Captured: France → Prussia · Brunswick marches from Gascony into Limousin unopposed! (195 lost to march) Captured: France → Prussia
  - 🏴 Prussia: Brunswick marches from Berry into Gascony unopposed! (399 lost to march) Captured: France → Prussia
  - 🏴 Prussia: Brunswick marches from Gascony into Limousin unopposed! (195 lost to march) Captured: France → Prussia
  - verbs: attack×2
- ORDER Bernadotte [continues]: Bernadotte marches to Hanover. 1 region to Oldenburg.
- ORDER Massena [active]: Massena is marching to Swabia (2 turns remaining).
- ORDER Soult [completed]: As ordered: "move to Franconia". Soult arrives at Franconia. Soult stands ready for instruction.
- ENVOYS WAITING 1 · Prussia peace
- LEDGER treasury 14826 · net +242 · threat 88 · provinces 22 (-3) · ceiling 16345 · army 128682 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 1850 · trade 487 · admin 50 · tribute 1255 · upkeep 1044 · charges 2036 · requisitions 75 · blockade 305 · admiralty 90
- DISPATCH: Sire — Gascony has fallen to Prussia. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
  - MAILBOX #12 Prussia incoming_proposal: Prussia — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Prussia, peace #19 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: At War → Peace with Prussia. → display-only
  - RATIFIED Prussia · PEACE · enemy_victory
- CMD `Soult, attack Vienna` → ✗ Soult cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `Deroy, attack Vienna` → ✗ Deroy cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `Davout, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `Napoleon, move to Lorraine` → ✓ Napoleon moves from Swabia to Lorraine
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 4 actions, 1 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks with overwhelming force. Castanos gains the advantage over Paget. Casualties: Castanos 631, Paget 1,90…
  - ⚔ Castanos (lost 631) vs Paget (lost 1903) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price. — The Line Holds +15% (Paget)
  - verbs: move×3, attack×1
- ORDER Bernadotte [continues]: Bernadotte marches to Oldenburg. 1 region to Flanders.
- ORDER Massena [completed]: Massena arrives at Swabia. Massena: "Done — and I trust the next order has more fire in it."
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 13289 · net +735 · threat 85 · provinces 22 (+0) · ceiling 18360 · army 125333 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 99 · Switzerland 92
  - NET income 1841 · trade 487 · admin 50 · tribute 1487 · upkeep 1000 · charges 1634 · contributions 101 · blockade 305 · admiralty 90
- DISPATCH: Sire — the Emperor's star rises. The Presence stands at +4% this morning, up from where the defeats had left it.
  - RAIL status_quo_conceded: Artois, Berry, Gascony, Limousin, Normandy and Paris — left with Prussia by the peace, titled to them by treaty.
  - RAIL peace_ratified: Peace ratified between Prussia and France.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +6 medium/low (status_quo_titled, diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 14 — Early April 1806
  - MAILBOX #13 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #20 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (2568g forgone). Loyalty +1 (99 → 100); bond -15 → 5 (+0 a turn). Cost: 1 DP. → display-only
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Franconia to Swabia (190 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Napoleon, move to Orleanais` → ✓ Napoleon moves from Lorraine to Orleanais
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos delivers an effective strike. Castanos gains the advantage over Paget. Casualties: Castanos 145, Paget 815. Bo…
  - ⚔ Castanos (lost 145) vs Paget (lost 815) — Paget was driven from the field. His men are scattered. — The Line Holds +15% (Paget)
  - verbs: attack×1, form_square×1
- ORDER Bernadotte [completed]: Bernadotte arrives at Flanders. Bernadotte: "Done, and done properly — no stragglers, no surprises."
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 13746 · net +353 · threat 82 · provinces 22 (+0) · ceiling 16128 · army 123797 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 100 · Switzerland 90
  - NET income 1836 · trade 487 · admin 50 · tribute 1169 · upkeep 976 · charges 1738 · contributions 80 · blockade 305 · admiralty 90
- DISPATCH: Sire — Paris, Artois, Berry and 3 more lie in enemy hands — the capital among them. Prussia holds them.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_ai_proposal_refused: 8 courts rebuff Prussia (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Bernadotte, move to Hanover` → ✗ Cannot enter Hanover — it is controlled by Prussia (diplomatic state: PEACE). Open borders or higher required.
- CMD `Napoleon, move to Paris` → ✗ Cannot enter Paris — it is controlled by Prussia (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, move to Paris` → ✗ Cannot enter Paris — it is controlled by Prussia (diplomatic state: PEACE). Open borders or higher required.
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke John faces a difficult fight. Ney holds the line. Casualties: Archduke John 7,055, Ney's army 4,263. Both armi… · Castanos delivers an effective strike. Castanos gains the advantage over Paget. Casualties: Castanos 57, Paget 499. Bot…
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Anjou!
  - ⚔ Archduke John (lost 2284, own corps) vs Ney (lost 1094, own corps) — Reinforcements from Massena bolstered Ney's position — though Soult never arrived, Sire.
  - ⚔ Castanos (lost 57) vs Paget (lost 499) — Paget's corps broke, Sire. They are streaming back from the field. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - verbs: attack×2, fortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Britain, armistice_losing #22 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #23 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- ENVOYS WAITING 2 · Britain armistice losing · Russia armistice losing
- LEDGER treasury 14168 · net +825 · threat 79 · provinces 22 (+0) · ceiling 20834 · army 116958 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 1829 · trade 487 · admin 50 · tribute 952 · upkeep 900 · charges 1503 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 16 — Early May 1806
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Napoleon, recruit infantry` → ✓ Napoleon recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 518 gold (×3 at war) (×1.02 over the ordinance) (Napoleon's intendance: -1…
- CMD `Massena, move to Paris` → ✗ Cannot enter Paris — it is controlled by Prussia (diplomatic state: PEACE). Open borders or higher required.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 17, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 actions unused) Turn 17 begins!
- SPENT 518g on this turn's orders
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Hiller's forces advance steadily. Hiller gains the advantage over Teulie. Casualties: Hiller 735, Teulie 1,118. Both ar… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Teulie. Casualties: Archduk…
  - ⚔ Hiller (lost 735) vs Teulie (lost 1118) — The margin was slim. Training and preparation would serve Teulie well.
  - ⚔ Archduke Charles (lost 421) vs Teulie (lost 2887) — The toll on Teulie's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 1,800 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 1,800 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 14297 · net +724 · threat 76 · provinces 22 (+0) · ceiling 19861 · army 117526 · vassals Bavaria 100 · Holland 94 · Kingdom of Italy 88 · Switzerland 95
  - NET income 1832 · trade 487 · admin 50 · tribute 955 · upkeep 912 · charges 1598 · admiralty 90
- DISPATCH: Sire — Teulie was mauled at Milan: a third of his corps — 1,118 men — lost in a single action.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Paymaster of Coalitions — alliance is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, blockade_broken ×2)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Hiller delivers an effective strike. Ney holds the line. Casualties: Hiller 3,736, Ney's army 629. Both armies remain i…
  - ⚔ Hiller (lost 3736) vs Ney (lost 156, own corps) — Ney fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 15022 · net +616 · threat 63 · provinces 22 (+0) · ceiling 19627 · army 114596 · vassals Bavaria 100 · Holland 93 · Switzerland 95
  - NET income 1837 · trade 487 · admin 50 · tribute 943 · upkeep 872 · charges 1739 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - TURN EVENTS 10
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Provence unopposed! (1,291 lost to march) Captured: France → Austria · ArchdukeCharles marches from Provence into Lyonnais unopposed! (1,252 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (1,291 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Provence into Lyonnais unopposed! (1,252 lost to march) Captured: France → Austria
  - verbs: attack×2
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 59, own corps) vs Hiller (lost 4327) — Lannes and Massena arrived to reinforce Ney, but Murat and Deroy failed to reach the field in time. And Hiller was take…
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 15437 · net +323 · threat 63 · provinces 20 (-2) · ceiling 17787 · army 114418 · vassals Bavaria 100 · Holland 92 · Switzerland 95
  - NET income 1611 · trade 487 · admin 50 · tribute 946 · upkeep 888 · charges 1843 · requisitions 50 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 9
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Lyonnais into Savoy unopposed! (2,430 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Savoy unopposed! (2,430 lost to march) Captured: France → Austria
  - verbs: unfortify×1, attack×1, form_square×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1308, own corps) vs Archduke John (lost 4080) — Reinforcements from Ney, Lannes and Massena bolstered Murat's position — though Deroy never arrived, Sire. — The corps system brought Ney in. — Berthier: the corps marched apart and arrived together.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 15489 · net +154 · threat 60 · provinces 19 (-1) · ceiling 16570 · army 110876 · vassals Bavaria 100 · Holland 90 · Switzerland 94
  - NET income 1533 · trade 437 · admin 50 · tribute 949 · upkeep 860 · charges 1915 · requisitions 50 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_auto_downgrade, paymaster_subsidy, agenda_shift)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 33% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 20 — Early July 1806
  - MAILBOX #17 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #24 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (3368g forgone). Loyalty +10 (90 → 100); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Davout. Heavy casua… · ArchdukeJohn strikes back after successfully defending! · ArchdukeCharles flanks from Milan while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 2230) vs Davout (lost 2196) — Davout stood alone, Sire. Soult and Deroy never came. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke John (lost 1072, own corps) vs Davout (lost 2088) — Not one corps reached Davout. Soult and Deroy were expected; Davout fought the battle single-handed.
  - ⚔ Archduke Charles (lost 1679) vs Davout (lost 1956) — Where were Soult and Deroy? Davout held the field alone — reinforcement never came.
  - verbs: attack×3, break_square×1, move×1
- ORDER Lannes [retired]: Lannes's question is overtaken, Sire — Lannes has marched clear of Tyrol. He awaits new orders.
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 2241, own corps) vs Archduke John (lost 863) — Ney and Lannes arrived to reinforce Murat, but Massena and Deroy failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- LEDGER treasury 14371 · net -581 · threat 57 · provinces 19 (+0) · ceiling 10535 · army 101075 · vassals Bavaria 100 · Holland 97 · Switzerland 91
  - NET income 1535 · trade 437 · admin 50 · tribute 354 · upkeep 768 · charges 1875 · requisitions 50 · blockade 274 · admiralty 90
- DISPATCH: Sire — Ney, crowned four turns ago, has been driven back.
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - TURN EVENTS 10
- DIPLO +7 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy, blockade_begins ×2)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Ney. Casualties: Archduke C… · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Davout. Casualties: Archduke C…
  - ⚔ Archduke Charles (lost 1435) vs Ney (lost 2046, own corps) — Soult and Deroy never reached the guns. The battle was decided without them, Sire.
  - ⚔ Archduke Charles (lost 649) vs Davout (lost 2838) — Not one corps reached Davout. Soult and Deroy were expected; Davout fought the battle single-handed.
  - verbs: attack×2, fortify×1
- LEDGER treasury 13406 · net -527 · threat 54 · provinces 19 (+0) · ceiling 10090 · army 92716 · vassals Bavaria 98 · Holland 94 · Switzerland 86
  - NET income 1537 · trade 437 · admin 50 · tribute 282 · upkeep 704 · charges 1815 · requisitions 50 · blockade 274 · admiralty 90
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Provence.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 2,382 troops in th…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -119g, Bavaria -175g. Captured: Bavaria → Austria
  - verbs: attack×1, form_square×1
- LEDGER treasury 12880 · net -218 · threat 51 · provinces 19 (+0) · ceiling 11510 · army 91592 · vassals Bavaria 100 · Holland 95 · Switzerland 85
  - NET income 1540 · trade 437 · admin 50 · tribute 481 · upkeep 680 · charges 1732 · requisitions 50 · blockade 274 · admiralty 90
- DISPATCH: Sire — 3 turns now with Paris, Artois, Berry and 6 more in enemy hands — the capital among them. The country counts every one of them.
  - TURN EVENTS 11
- DIPLO +6 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Lannes. Casualties: Arc… · Schwarzenberg attacks with overwhelming force. Schwarzenberg gains the advantage over Deroy. Casualties: Schwarzenberg'… · ArchdukeCharles holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: [!] No word came for Lannes, cornered at Bohemia — the enemy did not wait. [!] MARSHAL CAPTURED — Lannes is taken by Austria at Bohemia!
  - 🏴 Austria: [!] MARSHAL CAPTURED — Deroy is taken by Austria at Franconia!
  - ⚔ Archduke Charles (lost 449, own corps) vs Lannes (lost 2318, own corps) — Lannes fought without Deroy's support. The roads, or the will, proved insufficient. And Lannes was taken on that field …
  - ⚔ Schwarzenberg (lost 776, own corps) vs Deroy (lost 2195, own corps) — Murat's timely arrival aided Deroy. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 463, own corps) vs Deroy (lost 3607) — Not one corps reached Deroy. Soult was expected; Deroy fought the battle single-handed. And Deroy was taken on that fie…
  - verbs: attack×3, move×1, unfortify×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 2683, own corps) vs Archduke John (lost 1247) — Lannes arrived to reinforce Massena, but Deroy failed to reach the field in time.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #25 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (78 → 88); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 11854 · net -384 · threat 48 · provinces 19 (+0) · ceiling 9565 · army 66975 · vassals Bavaria 96 · Holland 90 · Switzerland 88
  - NET income 1540 · trade 437 · admin 50 · tribute 112 · upkeep 504 · charges 1655 · blockade 274 · admiralty 90
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 12
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Wrede. Casualties: Archduke Charl… · Schwarzenberg's forces press forward aggressively. Schwarzenberg gains the advantage over Massena. Casualties: Schwarze…
  - 🏴 Austria: Casualties: Schwarzenberg's army 416, Massena's army 5,309. Both armies remain in the field. Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 476, own corps) vs Wrede (lost 2172, own corps) — Reinforcements from Ney bolstered Wrede's position — though Soult never arrived, Sire.
  - ⚔ Schwarzenberg (lost 209, own corps) vs Massena (lost 4571, own corps) — Soult failed to arrive in time. Massena's army fought without expected support.
  - verbs: attack×2, unfortify×1, fortify×1, form_square×1
- ORDER Ney [retired]: Ney's question is overtaken, Sire — Ney has marched clear of Franconia. He awaits new orders.
- LEDGER treasury 11107 · net -246 · threat 45 · provinces 19 (+0) · ceiling 9679 · army 59307 · vassals Bavaria 79 · Holland 87 · Switzerland 84
  - NET income 1540 · trade 437 · admin 50 · tribute 112 · upkeep 448 · charges 1573 · blockade 274 · admiralty 90
- DISPATCH: Sire — General Wrede has been taken. Austria holds him prisoner.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Schwarzenberg launches a decisive assault. Brutal stalemate between Schwarzenberg and Ney. Heavy casualties on both sid… · Archduke John struggles in a costly engagement. Soult holds the line. Casualties: Archduke John 2,567, Soult's army 1,1…
  - ⚔ Schwarzenberg (lost 1187) vs Ney (lost 584, own corps) — Ney was driven from the field. His men are scattered. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke John (lost 1605, own corps) vs Soult (lost 1060, own corps) — The exchange went Soult's way, Sire — Archduke John paid twice what Soult did, though the day decided nothing yet.
  - verbs: attack×2, move×1, fortify×1
- ORDER Ney [awaiting_response]: Ney is cornered at Swabia with 3,529 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Swabia with 3,529 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 10739 · net -170 · threat 42 · provinces 19 (+0) · ceiling 9763 · army 52403 · vassals Bavaria 82 · Holland 89 · Switzerland 85
  - NET income 1540 · trade 437 · admin 50 · tribute 91 · upkeep 400 · charges 1524 · blockade 274 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Swabia. He must reform before he fights again.
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 10572 · net -137 · threat 39 · provinces 19 (+0) · ceiling 9780 · army 51916 · vassals Bavaria 84 · Holland 90 · Switzerland 85
  - NET income 1540 · trade 437 · admin 50 · tribute 94 · upkeep 400 · charges 1494 · blockade 274 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 12
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John engages in solid combat. Brutal stalemate between Archduke John and Soult. Heavy casualties on both sides… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Soult. Casualties: Archduke Cha…
  - 🏴 Austria: [!] No word came for Massena, cornered at Swabia — the enemy did not wait. [!] MARSHAL CAPTURED — Massena is taken by Austria at Swabia!
  - ⚔ Archduke John (lost 917, own corps) vs Soult (lost 1673, own corps) — Stalemate. Soult and Archduke John glare at each other across the field.
  - ⚔ Archduke Charles (lost 878, own corps) vs Soult (lost 2346, own corps) — A narrow defeat for Soult, Sire. Better-prepared troops might have tipped the balance.
  - verbs: attack×2, unfortify×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 10187 · net +346 · threat 36 · provinces 19 (+0) · ceiling 12141 · army 42309 · vassals Bavaria 84 · Holland 89 · Switzerland 83
  - NET income 1540 · trade 437 · admin 50 · tribute 450 · upkeep 320 · charges 1447 · blockade 274 · admiralty 90
- DISPATCH: Sire — Marshal Massena has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 28 — Early November 1806
  - MAILBOX #19 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #26 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, unfortify×1, drill×1
- LEDGER treasury 10890 · net +579 · threat 33 · provinces 19 (+0) · ceiling 14160 · army 42113 · vassals Bavaria 84 · Holland 90 · Switzerland 83
  - NET income 1540 · trade 437 · admin 50 · tribute 507 · treaty 300 · upkeep 320 · charges 1571 · blockade 274 · admiralty 90
- DISPATCH: Sire — the war with Austria is over. The peace grants safe passage home.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 11490 · net +494 · threat 30 · provinces 19 (+0) · ceiling 14279 · army 41921 · vassals Bavaria 84 · Holland 91 · Switzerland 83
  - NET income 1540 · trade 437 · admin 50 · tribute 528 · treaty 300 · upkeep 320 · charges 1677 · blockade 274 · admiralty 90
- DISPATCH: Sire — Murat's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy)

## Turn 30 — Early December 1806
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, drill×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 11987 · net +409 · threat 27 · provinces 19 (+0) · ceiling 14296 · army 41733 · vassals Bavaria 84 · Holland 92 · Switzerland 83
  - NET income 1540 · trade 437 · admin 50 · tribute 531 · treaty 300 · upkeep 320 · charges 1765 · blockade 274 · admiralty 90
- DISPATCH: Sire — Murat's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 12398 · net +563 · threat 24 · provinces 19 (+0) · ceiling 15580 · army 41548 · vassals Bavaria 84 · Holland 93 · Switzerland 83
  - NET income 1540 · trade 437 · admin 50 · tribute 758 · treaty 300 · upkeep 320 · charges 1838 · blockade 274 · admiralty 90
- DISPATCH: Sire — Britain's gold reaches Russia — the subsidy stands at 400 this season.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 32 — Early January 1807
  - MAILBOX #20 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #27 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1
- LEDGER treasury 12663 · net +218 · threat 21 · provinces 19 (+0) · ceiling 13894 · army 41548 · vassals Bavaria 84 · Holland 94 · Switzerland 83
  - NET income 1540 · trade 437 · admin 50 · tribute 760 · upkeep 320 · charges 1885 · blockade 274 · admiralty 90
- DISPATCH: Sire — the truce with Austria has collapsed — the war resumes where it stood.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 5
- DIPLO +4 medium/low (enemy_marshal_commissioned ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
- LEDGER treasury 12883 · net +181 · threat 18 · provinces 19 (+0) · ceiling 13906 · army 41548 · vassals Bavaria 86 · Holland 95 · Switzerland 83
  - NET income 1540 · trade 437 · admin 50 · tribute 762 · upkeep 320 · charges 1924 · blockade 274 · admiralty 90
- DISPATCH: Sire — Murat's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved)
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria, Britain and Russia remain at war with us.

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Schwarzenberg launches a decisive assault. Schwarzenberg gains the advantage over Soult. Casualties: Schwarzenberg's ar… · Schwarzenberg's forces press forward aggressively. Schwarzenberg gains the advantage over Davout. Casualties: Schwarzen…
  - 🏴 Austria: Schwarzenberg advances into Swabia. (436 lost to march — forward supply lines reduce losses) Swabia has been captured by Austria!
  - 🏴 Austria: 994 enemy casualties; the pursuit is halted. [!] MARSHAL CAPTURED — Murat is taken by Austria at Lorraine!
  - ⚔ Schwarzenberg (lost 923, own corps) vs Soult (lost 3977, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Schwarzenberg (lost 1030) vs Davout (lost 1036, own corps) — Napoleon reached Davout in time, Sire — but even together, the field could not be held.
  - verbs: attack×2, move×1
- LEDGER treasury 12269 · net -180 · threat 5 · provinces 19 (+0) · ceiling 11412 · army 30625 · vassals Holland 92 · Switzerland 79
  - NET income 1531 · trade 437 · admin 50 · tribute 675 · upkeep 240 · charges 2168 · contributions 101 · blockade 274 · admiralty 90
- DISPATCH: Sire — Marshal Murat has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Ottoman rebuffs Austria (design ask)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Schwarzenberg launches a devastating assault! Schwarzenberg gains the advantage over Soult. Casualties: Schwarzenberg's… · Schwarzenberg delivers an effective strike. Schwarzenberg gains the advantage over Davout. Casualties: Schwarzenberg 17… · Liechtenstein marches from Swabia into Rhineland unopposed! (482 lost to march) Captured: France → Austria
  - 🏴 Austria: Casualties: Schwarzenberg's army 479, Soult's army 5,935. Both armies remain in the field. Lorraine has been captured by Austria!
  - 🏴 Austria: Liechtenstein marches from Swabia into Rhineland unopposed! (482 lost to march) Captured: France → Austria
  - ⚔ Schwarzenberg (lost 464, own corps) vs Soult (lost 2844, own corps) — Napoleon marched to Soult's guns as ordered. It was not enough.
  - ⚔ Schwarzenberg (lost 172) vs Davout (lost 1409) — The walls were not enough. Schwarzenberg broke through Davout's prepared defenses.
  - verbs: attack×3, stance_change×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 11337 · net -427 · threat 2 · provinces 17 (-2) · ceiling 9593 · army 23115 · vassals Holland 89 · Switzerland 75
  - NET income 1313 · trade 437 · admin 50 · tribute 675 · upkeep 176 · charges 2289 · contributions 73 · blockade 274 · admiralty 90
- DISPATCH: Sire — Lorraine has fallen to Austria. Enemy colours fly over French homeland soil. Schwarzenberg's corps of 26,107 stands there. A garrison you detach (3,000 men) holds a province against a march, a…
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 6
- COURTS: The court of Britain hardens over The Paymaster of Coalitions — prepared now to go as far as war.
- COURTS: The court of Austria hardens over The Eastern Question — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 36 — Early March 1807
  - MAILBOX #21 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #28 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Schwarzenberg attacks with overwhelming force. Schwarzenberg gains the advantage over Soult. Casualties: Schwarzenberg … · Schwarzenberg launches a decisive assault. Schwarzenberg gains the advantage over Napoleon. Casualties: Schwarzenberg 1… · Liechtenstein marches from Lorraine into Franche-Comte unopposed! (210 lost to march — forward supply lines reduce loss…
  - 🏴 Austria: [!] Napoleon's troops are BROKEN (morale 0%)! FORCED RETREAT! Orleanais has been captured by Austria!
  - 🏴 Austria: Liechtenstein marches from Lorraine into Franche-Comte unopposed! (210 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - ⚔ Schwarzenberg (lost 54) vs Soult (lost 1091) — Where was Bernadotte? Soult held the field alone — reinforcement never came.
  - ⚔ Schwarzenberg (lost 176) vs Napoleon (lost 2886) — Napoleon's army has been badly mauled. Schwarzenberg proved the stronger force today.
  - verbs: attack×3, move×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 10985 · net -121 · threat 0 · provinces 15 (-2) · ceiling 10425 · army 17657 · vassals Holland 86 · Switzerland 71
  - NET income 1160 · trade 437 · admin 50 · tribute 675 · upkeep 128 · charges 1951 · blockade 274 · admiralty 90
- DISPATCH: Sire — Orleanais has fallen to Austria. Enemy colours fly over French homeland soil. Schwarzenberg's corps of 24,631 stands there. A garrison you detach (3,000 men) holds a province against a march, …
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 4455 gold.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen)

## Turn 37 — Late March 1807
  - MAILBOX #22 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #29 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Schwarzenberg's forces advance steadily. Schwarzenberg gains the advantage over Davout. Casualties: Schwarzenberg 601, … · Liechtenstein marches from Franche-Comte into Nivernais unopposed! (406 lost to march) Captured: France → Austria · Schwarzenberg's forces press forward aggressively. Schwarzenberg gains the advantage over Soult. Casualties: Schwarzenb…
  - 🏴 Austria: Liechtenstein marches from Franche-Comte into Nivernais unopposed! (406 lost to march) Captured: France → Austria
  - ⚔ Schwarzenberg (lost 601) vs Davout (lost 906, own corps) — Dumonceau reached Davout in time, Sire — but even together, the field could not be held.
  - ⚔ Schwarzenberg (lost 797) vs Soult (lost 332, own corps) — Soult's army has been badly mauled. Schwarzenberg proved the stronger force today.
  - verbs: attack×3, move×1, grant_dotation×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10598 · net -105 · threat 0 · provinces 14 (-1) · ceiling 10118 · army 13914 · vassals Holland 83 · Switzerland 67
  - NET income 1092 · trade 437 · admin 50 · tribute 675 · upkeep 104 · charges 1891 · blockade 274 · admiralty 90
- DISPATCH: Sire — Nivernais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standin…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 38 — Early April 1807
  - MAILBOX #23 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #30 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (67 → 71); bond 40 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Liechtenstein's forces press forward aggressively. Liechtenstein gains the advantage over Napoleon. Casualties: Liechte… · Schwarzenberg holds them at Flanders while allies attack from Orleanais! (+1 coordination) · Liechtenstein flanks from Orleanais while allies attack from Flanders! (+1 coordination) · Liechtenstein flanks from Orleanais while allies attack from Flanders! (+1 coordination)
  - ⚔ Liechtenstein (lost 466) vs Napoleon (lost 1184, own corps) — Dumonceau reached Napoleon in time, Sire — but even together, the field could not be held.
  - ⚔ Schwarzenberg (lost 801) vs Bernadotte (lost 3541) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Liechtenstein (lost 41) vs Napoleon (lost 505) — Hardly an engagement, Sire — a brush between Napoleon and Liechtenstein, and the day moved on.
  - ⚔ Liechtenstein (lost 19) vs Napoleon (lost 210) — Scarcely an action, Sire. Napoleon and Liechtenstein came to blows on too small a scale to signify.
  - verbs: attack×4, unfortify×1, move×1
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Flanders — 220 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Flanders — 220 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 9626 · net -434 · threat 0 · provinces 14 (+0) · ceiling 7900 · army 8217 · vassals Holland 74 · Switzerland 63
  - NET income 989 · trade 437 · admin 50 · tribute 450 · upkeep 56 · charges 1921 · contributions 19 · blockade 274 · admiralty 90
- DISPATCH: Sire — Dumonceau's corps has been broken at Flanders. He must reform before he fights again.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing_other)
  - LOG coalition_brewing_started: Coalition brewing against Austria — Russia consulting (their alarm: 76)

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Schwarzenberg attacks with overwhelming force. Schwarzenberg gains the advantage over Soult. Casualties: Schwarzenberg … · Liechtenstein delivers an effective strike. Liechtenstein gains the advantage over Soult. Casualties: Liechtenstein 8, … · Schwarzenberg's forces advance steadily. Schwarzenberg gains the advantage over Bernadotte. Casualties: Schwarzenberg 1…
  - ⚔ Schwarzenberg (lost 25) vs Soult (lost 377) — Soult was driven from the field. His men are scattered.
  - ⚔ Liechtenstein (lost 8) vs Soult (lost 307) — Soult was driven from the field. His men are scattered.
  - ⚔ Schwarzenberg (lost 170) vs Bernadotte (lost 3330) — Bernadotte's army has been badly mauled. Schwarzenberg proved the stronger force today.
  - verbs: attack×3, stance_change×1
- LEDGER treasury 9022 · net -303 · threat 0 · provinces 14 (+0) · ceiling 7817 · army 4182 · vassals Holland 69 · Switzerland 47
  - NET income 990 · trade 437 · admin 50 · tribute 405 · upkeep 32 · charges 1769 · contributions 20 · blockade 274 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Liechtenstein engages in solid combat. Liechtenstein gains the advantage over Bernadotte. Casualties: Liechtenstein 143… · Schwarzenberg's attack falters disastrously! Schwarzenberg decisively defeats Soult! Soult's army is destroyed. Schwarz… · Schwarzenberg's forces press forward aggressively. Schwarzenberg gains the advantage over Dumonceau. Casualties: Schwar… · Liechtenstein launches a decisive assault. Liechtenstein gains the advantage over Dumonceau. Casualties: Liechtenstein …
  - ⚔ Liechtenstein (lost 143) vs Bernadotte (lost 4068) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Schwarzenberg (lost 1) vs Soult (lost 60) — A skirmish, Sire. Soult's men traded shots with Schwarzenberg; there was no battle to speak of.
  - ⚔ Schwarzenberg (lost 140) vs Dumonceau (lost 2063) — The toll on Dumonceau's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Liechtenstein (lost 72) vs Dumonceau (lost 2429) — The toll on Dumonceau's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 8349 · net -183 · threat 0 · provinces 14 (+0) · ceiling 7619 · army 54 · vassals Holland 55
  - NET income 991 · trade 437 · admin 50 · tribute 323 · charges 1599 · contributions 21 · blockade 274 · admiralty 90
- DISPATCH: Sire — Marshal Soult's corps has been DESTROYED at Amsterdam. He will not return to the order of battle.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_vassal_transferred: Switzerland passes from France's suzerainty to Britain's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Britain's gold turns Switzerland against France.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Ottoman rebuffs Austria (design ask)

---
finished: **completed** · commands 109 · popups 64 · battles 49
