# Playtest digest — REACH-GEVB

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "client_petition": "grant"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `47eb92ffc944` (dirty) · content `aae077cedc7a` · driver `e498338939cb`
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
- LEDGER treasury 383 · net +1308 · threat 85 · provinces 28 · ceiling 29250 · army 192898 · vassals Bavaria 60 · Holland 100 · Kingdom of Italy 100 · Switzerland 98
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
- LEDGER treasury 2031 · net +1587 · threat 89 · provinces 28 (+0) · ceiling 33015 · army 187244 · vassals Bavaria 64 · Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 1453 · upkeep 2546 · charges 1 · blockade 219 · admiralty 90
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
- LEDGER treasury 3936 · net +1723 · threat 88 · provinces 28 (+0) · ceiling 35602 · army 180821 · vassals Bavaria 68 · Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 437 · admin 50 · tribute 1459 · upkeep 2344 · charges 105 · blockade 274 · admiralty 90
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
- LEDGER treasury 6102 · net +1936 · threat 87 · provinces 28 (+0) · ceiling 39708 · army 170067 · vassals Bavaria 72 · Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2590 · trade 512 · admin 50 · tribute 1466 · upkeep 2036 · charges 236 · blockade 320 · admiralty 90
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
- LEDGER treasury 8210 · net +1967 · threat 86 · provinces 28 (+0) · ceiling 40552 · army 165144 · vassals Bavaria 76 · Holland 100 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 512 · admin 50 · tribute 1472 · upkeep 1870 · charges 377 · blockade 320 · admiralty 90
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
- LEDGER treasury 9797 · net +1418 · threat 84 · provinces 28 (+0) · ceiling 24872 · army 160812 · vassals Bavaria 80 · Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 512 · admin 50 · tribute 1254 · upkeep 1736 · charges 732 · contributions 110 · blockade 320 · admiralty 90
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
- LEDGER treasury 11410 · net +1431 · threat 82 · provinces 28 (+0) · ceiling 26125 · army 154609 · vassals Bavaria 84 · Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 512 · admin 50 · tribute 1261 · upkeep 1548 · charges 914 · contributions 110 · blockade 320 · admiralty 90
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
- LEDGER treasury 12753 · net +1178 · threat 80 · provinces 28 (+0) · ceiling 24480 · army 149703 · vassals Bavaria 88 · Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 512 · admin 50 · tribute 1267 · upkeep 1642 · charges 1079 · contributions 110 · blockade 320 · admiralty 90
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
- LEDGER treasury 14048 · net +1126 · threat 78 · provinces 28 (+0) · ceiling 24915 · army 144298 · vassals Bavaria 92 · Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 512 · admin 50 · tribute 1274 · upkeep 1492 · charges 1248 · contributions 150 · blockade 320 · admiralty 90
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
- LEDGER treasury 13900 · net +1001 · threat 96 · provinces 27 (-1) · ceiling 22073 · army 135619 · vassals Bavaria 96 · Holland 99 · Kingdom of Italy 98 · Switzerland 94
  - NET income 2418 · trade 487 · admin 50 · tribute 1214 · upkeep 1204 · charges 1456 · contributions 150 · requisitions 37 · blockade 305 · admiralty 90
- DISPATCH: Sire — Artois has fallen to Prussia. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing t…
  - RAIL diplomatic_war_declared: France has declared war on Prussia, shattering the Open Borders Agreement, with 1 allied court poised to follow.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 2818 gold.
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
- LEDGER treasury 13284 · net -4 · threat 96 · provinces 25 (-2) · ceiling 13260 · army 133647 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2107 · trade 487 · admin 50 · tribute 1221 · upkeep 1328 · charges 2094 · occupation 52 · blockade 305 · admiralty 90
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
- LEDGER treasury 13807 · net +404 · threat 93 · provinces 22 (-3) · ceiling 16345 · army 128682 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 1850 · trade 487 · admin 50 · tribute 1255 · upkeep 1044 · charges 1874 · requisitions 75 · blockade 305 · admiralty 90
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
- LEDGER treasury 12438 · net +726 · threat 90 · provinces 22 (+0) · ceiling 17448 · army 125333 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 99 · Switzerland 92
  - NET income 1841 · trade 487 · admin 50 · tribute 1487 · upkeep 1132 · charges 1511 · contributions 101 · blockade 305 · admiralty 90
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
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 141, Paget …
  - ⚔ Castanos (lost 141) vs Paget (lost 895) — The toll on Paget's forces is heavy, Sire. This defeat will be felt. — The Line Holds +15% (Paget)
  - verbs: attack×1, form_square×1
- ORDER Bernadotte [completed]: Bernadotte arrives at Flanders. Bernadotte: "Done, and done properly — no stragglers, no surprises."
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 13018 · net +461 · threat 87 · provinces 22 (+0) · ceiling 16128 · army 123797 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 100 · Switzerland 90
  - NET income 1836 · trade 487 · admin 50 · tribute 1169 · upkeep 976 · charges 1630 · contributions 80 · blockade 305 · admiralty 90
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
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke John faces a difficult fight. Ney holds the line. Casualties: Archduke John 7,055, Ney's army 4,263. Both armi… · Castanos launches a decisive assault. Castanos gains the advantage over Paget. Casualties: Castanos 60, Paget 513. Both…
  - ⚔ Archduke John (lost 2284, own corps) vs Ney (lost 1094, own corps) — Reinforcements from Massena bolstered Ney's position — though Soult never arrived, Sire.
  - ⚔ Castanos (lost 60) vs Paget (lost 513) — Paget's corps broke, Sire. They are streaming back from the field. — The Line Holds +15% (Paget)
  - verbs: attack×2, fortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Britain, armistice_losing #22 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #23 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- ENVOYS WAITING 2 · Britain armistice losing · Russia armistice losing
- LEDGER treasury 13528 · net +904 · threat 84 · provinces 22 (+0) · ceiling 20834 · army 116958 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 1829 · trade 487 · admin 50 · tribute 952 · upkeep 900 · charges 1424 · admiralty 90
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
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Hiller faces a difficult fight. Brutal stalemate between Hiller and Teulie. Heavy casualties on both sides: Hiller 751,… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Teulie. Casualties: Arc…
  - ⚔ Hiller (lost 751) vs Teulie (lost 1042) — Stalemate. Teulie and Hiller glare at each other across the field.
  - ⚔ Archduke Charles (lost 476) vs Teulie (lost 2802) — The toll on Teulie's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 1,961 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 1,961 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 13748 · net +800 · threat 81 · provinces 22 (+0) · ceiling 19916 · army 117526 · vassals Bavaria 100 · Holland 96 · Kingdom of Italy 91 · Switzerland 97
  - NET income 1832 · trade 487 · admin 50 · tribute 955 · upkeep 912 · charges 1522 · admiralty 90
- DISPATCH: Sire — Teulie was mauled at Milan: a third of his corps — 1,042 men — lost in a single action.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Paymaster of Coalitions — alliance is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, blockade_broken ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 8 approaches from Britain and Russia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Brutal stalemate between Archduke Charles and Ney. Heavy casualties o… · Hiller faces a difficult fight. Ney holds the line. Casualties: Hiller 3,731, Ney's army 662. Both armies remain in the… · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,086 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,736 troops in the…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -86g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - ⚔ Archduke Charles (lost 3869) vs Ney (lost 1307, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
  - ⚔ Hiller (lost 3731) vs Ney (lost 156, own corps) — Ney fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 14290 · net +686 · threat 78 · provinces 22 (+0) · ceiling 19330 · army 109517 · vassals Bavaria 100 · Holland 95 · Kingdom of Italy 84 · Switzerland 97
  - NET income 1837 · trade 487 · admin 50 · tribute 913 · upkeep 840 · charges 1671 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - TURN EVENTS 11
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles faces a difficult fight. Davout holds the line. Casualties: Archduke Charles 2,980, Davout's army 1,92… · Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Ney. Heavy casualties on bo…
  - ⚔ Archduke Charles (lost 2980) vs Davout (lost 1563, own corps) — Reinforcements from Ney bolstered Davout's position — though Soult and Deroy never arrived, Sire.
  - ⚔ Archduke Charles (lost 2371) vs Ney (lost 1099, own corps) — Ney fought without Soult and Deroy's support. The roads, or the will, proved insufficient.
  - verbs: attack×2
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 47, own corps) vs Hiller (lost 4665) — Lannes, Murat and Massena arrived to reinforce Ney, but Deroy failed to reach the field in time.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 14703 · net +540 · threat 68 · provinces 22 (+0) · ceiling 18500 · army 104272 · vassals Bavaria 100 · Holland 95 · Switzerland 98
  - NET income 1841 · trade 487 · admin 50 · tribute 797 · upkeep 792 · charges 1803 · requisitions 50 · admiralty 90
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Provence unopposed! (1,023 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (1,023 lost to march) Captured: France → Austria
  - verbs: unfortify×1, attack×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 987, own corps) vs Hiller (lost 1359, own corps) — Lannes and Murat arrived to reinforce Massena, but Ney and Deroy failed to reach the field in time. — The corps system brought Murat in.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14992 · net +276 · threat 68 · provinces 21 (-1) · ceiling 16876 · army 100747 · vassals Bavaria 100 · Holland 94 · Switzerland 98
  - NET income 1693 · trade 437 · admin 50 · tribute 805 · upkeep 760 · charges 1896 · requisitions 37 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 20 — Early July 1806
  - MAILBOX #17 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #24 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (3368g forgone). Loyalty +6 (94 → 100); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Provence into Lyonnais unopposed! (992 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Provence into Lyonnais unopposed! (992 lost to march) Captured: France → Austria
  - verbs: recruit×2, retreat×1, move×1, attack×1, stance_change×1
- LEDGER treasury 14502 · net -459 · threat 65 · provinces 20 (-1) · ceiling 11423 · army 99937 · vassals Bavaria 100 · Holland 99 · Switzerland 97
  - NET income 1615 · trade 437 · admin 50 · tribute 391 · upkeep 760 · charges 1865 · requisitions 37 · blockade 274 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - TURN EVENTS 6
- DIPLO +7 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy, blockade_begins ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Savoy unopposed! (1,810 lost to march) Captured: France → Austria · ArchdukeCharles marches from Savoy into Burgundy unopposed! (758 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Savoy unopposed! (1,810 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Savoy into Burgundy unopposed! (758 lost to march) Captured: France → Austria
  - verbs: attack×2
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 439, own corps) vs Hiller (lost 4757) — Lannes's timely arrival aided Massena. Murat and Deroy, however, were conspicuously absent. And Hiller was taken on tha…
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Davout and Murat: They settle into cold war.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #25 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 13963 · net -721 · threat 65 · provinces 18 (-2) · ceiling 9238 · army 99098 · vassals Bavaria 100 · Holland 100 · Switzerland 97
  - NET income 1497 · trade 437 · admin 50 · tribute 399 · treaty 163 · upkeep 1076 · charges 1827 · blockade 274 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +5 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG ai_ai_proposal_refused: 15 approaches from Britain and Russia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen attacks with overwhelming force. Bennigsen gains the advantage over Lannes. Casualties: Bennigsen 412, Lannes…
  - ⚔ Bennigsen (lost 412) vs Lannes (lost 2811) — Not one corps reached Lannes. Murat, Massena and Deroy were expected; Lannes fought the battle single-handed.
  - verbs: attack×1
- ORDER Massena [continues]: Massena marches to Munich. 1 region to Franche-Comte.
- ORDER Murat [completed]: Murat arrives at Franche-Comte. Murat: "Accomplished. The men want a battle, not another road."
- ORDER Lannes [awaiting_response]: Lannes is cornered at Bohemia with 2,448 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Bohemia with 2,448 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 13428 · net -83 · threat 62 · provinces 18 (+0) · ceiling 12895 · army 93383 · vassals Bavaria 100 · Holland 99 · Switzerland 94
  - NET income 1500 · trade 437 · admin 50 · tribute 630 · treaty 163 · upkeep 712 · charges 1787 · blockade 274 · admiralty 90
- DISPATCH: Sire — Lannes was mauled at Bohemia: half of his corps — 2,811 men — lost in a single action.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_treaty_signed, law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, diplomatic_auto_downgrade, paymaster_subsidy, balance_of_europe_shifted)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG ai_ai_proposal_refused: 10 approaches from Russia, Sardinia and Austria are rebuffed (defensive alliance)

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- ORDER Massena [completed]: Massena arrives at Franche-Comte. Massena: "Accomplished. The men want a battle, not another road."
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #26 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +7 (93 → 100); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 13353 · net -288 · threat 59 · provinces 18 (+0) · ceiling 11507 · army 93383 · vassals Bavaria 100 · Holland 100 · Switzerland 100
  - NET income 1500 · trade 437 · admin 50 · tribute 413 · treaty 163 · upkeep 712 · charges 1775 · blockade 274 · admiralty 90
- DISPATCH: Sire — Marshal Lannes has been taken. Russia holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13073 · net -236 · threat 56 · provinces 18 (+0) · ceiling 11558 · army 93383 · vassals Bavaria 100 · Holland 100 · Switzerland 100
  - NET income 1500 · trade 437 · admin 50 · tribute 421 · treaty 163 · upkeep 712 · charges 1731 · blockade 274 · admiralty 90
- DISPATCH: Sire — 3 turns now with Paris, Artois, Berry and 7 more in enemy hands — the capital among them. The country counts every one of them.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (design ask)

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov's forces advance steadily. Kutuzov gains the advantage over Deroy. Casualties: Kutuzov 1,065, Deroy 3,706. Both…
  - ⚔ Kutuzov (lost 1065) vs Deroy (lost 3706) — Not one corps reached Deroy. Ney and Soult were expected; Deroy fought the battle single-handed.
  - verbs: attack×1
- LEDGER treasury 12683 · net -173 · threat 53 · provinces 18 (+0) · ceiling 11589 · army 89649 · vassals Bavaria 100 · Holland 99 · Switzerland 98
  - NET income 1500 · trade 437 · admin 50 · tribute 413 · treaty 163 · upkeep 680 · charges 1692 · blockade 274 · admiralty 90
- DISPATCH: Sire — Deroy's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 7
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout demands to be heard → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Russia, armistice_losing #27 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 12354 · net -277 · threat 50 · provinces 18 (+0) · ceiling 10604 · army 89649 · vassals Bavaria 100 · Holland 100 · Switzerland 98
  - NET income 1500 · trade 437 · admin 50 · tribute 420 · upkeep 680 · charges 1640 · blockade 274 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 7 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 7
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Napoleon. Casualties: Archduke …
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Orleanais. (1,123 lost to march) Orleanais has been captured by Austria!
  - ⚔ Archduke Charles (lost 1132) vs Napoleon (lost 3960) — A grievous defeat for Napoleon, Sire. The losses are severe.
  - verbs: fortify×2, unfortify×1, attack×1
- LEDGER treasury 11547 · net -43 · threat 47 · provinces 17 (-1) · ceiling 11317 · army 85689 · vassals Bavaria 100 · Holland 99 · Switzerland 96
  - NET income 1420 · trade 437 · admin 50 · tribute 879 · upkeep 648 · charges 1817 · blockade 274 · admiralty 90
- DISPATCH: Sire — Orleanais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standin…
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (NON AGGRESSION → OPEN BORDERS)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: 8 courts rebuff Russia (defensive alliance)

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Bernadotte. Casualties: Archdu… · Archduke Charles faces a difficult fight. Archduke Charles gains the advantage over Napoleon. Casualties: Archduke Char…
  - 🏴 Austria: ArchdukeJohn moves from Bohemia to Franconia. Franconia falls to Austria!
  - ⚔ Archduke Charles (lost 1752) vs Bernadotte (lost 2461, own corps) — Dumonceau marched to Bernadotte's guns as ordered. It was not enough.
  - ⚔ Archduke Charles (lost 225) vs Napoleon (lost 2763) — Napoleon's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, move×1
- LEDGER treasury 11136 · net -76 · threat 44 · provinces 17 (+0) · ceiling 10739 · army 79296 · vassals Bavaria 100 · Holland 96 · Switzerland 92
  - NET income 1392 · trade 437 · admin 50 · tribute 769 · upkeep 592 · charges 1768 · blockade 274 · admiralty 90
- DISPATCH: Sire — Napoleon's corps has been broken at Flanders. He must reform before he fights again.
  - TURN EVENTS 9
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Bernadotte. Casualties:…
  - ⚔ Archduke Charles (lost 1103) vs Bernadotte (lost 3103, own corps) — Dumonceau reached Bernadotte in time, Sire — but even together, the field could not be held.
  - verbs: fortify×2, attack×1, move×1
- LEDGER treasury 10866 · net -31 · threat 41 · provinces 17 (+0) · ceiling 10706 · army 76165 · vassals Bavaria 100 · Holland 94 · Switzerland 90
  - NET income 1381 · trade 437 · admin 50 · tribute 774 · upkeep 568 · charges 1741 · blockade 274 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Flanders. He must reform before he fights again.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 30 — Early December 1806
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Flanders garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,333 troops.… · ArchdukeCharles assaults the Flanders garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,851 troops in … · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduk… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Napoleon. Casualties: Archd…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -92g, France -150g. Captured: France → Austria
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Amsterdam!
  - ⚔ Archduke Charles (lost 147) vs Bernadotte (lost 2440) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today. And Bernadotte was taken on …
  - ⚔ Archduke Charles (lost 80) vs Napoleon (lost 1019) — The toll on Napoleon's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4
- LEDGER treasury 10182 · net -50 · threat 38 · provinces 16 (-1) · ceiling 9933 · army 68932 · vassals Bavaria 100 · Holland 91 · Switzerland 86
  - NET income 1270 · trade 437 · admin 50 · tribute 736 · upkeep 520 · charges 1659 · blockade 274 · admiralty 90
- DISPATCH: Sire — Flanders has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 7
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (design ask)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces stumble badly! Archduke Charles gains the advantage over Dumonceau. Casualties: Archduke Char… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Napoleon. Casualties: Archduke … · ArchdukeCharles marches from Flanders into Picardy unopposed! (638 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Flanders into Picardy unopposed! (638 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 196) vs Dumonceau (lost 2686) — Dumonceau's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 29) vs Napoleon (lost 559) — Napoleon's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×3
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Brabant — 604 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Brabant — 604 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 2 · Britain settlement offer · Holland client petition
- LEDGER treasury 9941 · net +161 · threat 35 · provinces 15 (-1) · ceiling 10725 · army 67769 · vassals Bavaria 98 · Holland 81 · Switzerland 80
  - NET income 1230 · trade 437 · admin 50 · tribute 946 · upkeep 512 · charges 1626 · blockade 274 · admiralty 90
- DISPATCH: Sire — Picardy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 4008 gold.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - TURN EVENTS 4
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 32 — Early January 1807
  - MAILBOX #21 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #22 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → reject_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #29 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → reject_settlement_offer
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (3104g forgone). Loyalty +4 (81 → 85); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #29 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 8 actions, 3 attacks — Britain, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Dumonceau. Casualties: Archduke… · ArchdukeCharles marches from Orleanais into Ile-de-France unopposed! (759 lost to march) Captured: France → Austria · ArchdukeCharles marches from Ile-de-France into Champagne unopposed! (697 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Orleanais into Ile-de-France unopposed! (759 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Ile-de-France into Champagne unopposed! (697 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 75) vs Dumonceau (lost 1701) — The toll on Dumonceau's forces is heavy, Sire. This defeat will be felt.
  - verbs: unfortify×4, attack×3, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 9564 · net -232 · threat 32 · provinces 13 (-2) · ceiling 8434 · army 67769 · vassals Bavaria 98 · Holland 80 · Switzerland 76
  - NET income 1150 · trade 437 · admin 50 · tribute 562 · upkeep 512 · charges 1555 · blockade 274 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 33 — Late January 1807
  - MAILBOX #23 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #30 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (76 → 80); bond 40 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Dumonceau. Casualties: Archduke… · Archduke John launches a decisive assault. Brutal stalemate between Archduke John and Ney. Heavy casualties on both sid… · Schwarzenberg delivers an effective strike. Brutal stalemate between Schwarzenberg and Ney. Heavy casualties on both si…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Lorraine. (528 lost to march) Lorraine has been captured by Austria!
  - ⚔ Archduke Charles (lost 811) vs Dumonceau (lost 489, own corps) — Reinforcements from Murat and Massena bolstered Dumonceau's position — though Soult and Deroy never arrived, Sire. And … — Massena's faith in you is spent (trust 26) — he committed 5,704 to the fight where he would have brought 11,408.
  - ⚔ Archduke John (lost 1721, own corps) vs Ney (lost 822, own corps) — Soult and Deroy failed to arrive in time. Ney's army fought without expected support.
  - ⚔ Schwarzenberg (lost 1256, own corps) vs Ney (lost 750, own corps) — Soult and Deroy never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×3, move×2, recruit×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 8658 · net -387 · threat 29 · provinces 12 (-1) · ceiling 6814 · army 58499 · vassals Bavaria 98 · Holland 71 · Switzerland 76
  - NET income 1040 · trade 437 · admin 50 · tribute 296 · upkeep 448 · charges 1398 · blockade 274 · admiralty 90
- DISPATCH: Sire — Lorraine has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 34 — Early February 1807
  - MAILBOX #24 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #31 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 7 actions, 4 attacks — Prussia, Spain, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen launches a decisive assault. Brutal stalemate between Bennigsen and Ney. Heavy casualties on both sides: Benn… · Kutuzov delivers an effective strike. Kutuzov gains the advantage over Ney. Casualties: Kutuzov 1,264, Ney's army 2,560… · Bennigsen's forces advance steadily. Brutal stalemate between Bennigsen and Davout. Heavy casualties on both sides: Ben… · Kutuzov's forces press forward aggressively. Kutuzov gains the advantage over Davout. Casualties: Kutuzov 572, Davout 2…
  - 🏴 Russia: [!] No word came for Ney, cornered at Munich — the enemy did not wait. [!] MARSHAL CAPTURED — Ney is taken by Russia at Munich!
  - ⚔ Bennigsen (lost 1589) vs Ney (lost 609, own corps) — Soult and Deroy never reached the guns. The battle was decided without them, Sire.
  - ⚔ Kutuzov (lost 1264) vs Ney (lost 801, own corps) — Ney fought without Soult and Deroy's support. The roads, or the will, proved insufficient.
  - ⚔ Bennigsen (lost 842) vs Davout (lost 1059, own corps) — Soult and Deroy never reached the guns. The battle was decided without them, Sire.
  - ⚔ Kutuzov (lost 572) vs Davout (lost 2235) — Davout stood alone, Sire. Soult and Deroy never came.
  - verbs: attack×4, fortify×2, unfortify×1
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 6893 · net +3 · threat 27 · provinces 12 (+0) · ceiling 6905 · army 65192 · vassals Bavaria 92 · Holland 67 · Switzerland 70
  - NET income 1040 · trade 437 · admin 50 · tribute 141 · upkeep 472 · charges 829 · blockade 274 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Russia holds him prisoner.
  - RAIL status_quo_conceded: Burgundy, Champagne, Flanders, Ile-de-France, Lorraine, Lyonnais, Orleanais, Picardy, Provence and Savoy — left with Austria by the peace, titled to …
  - RAIL status_quo_conceded: Franconia — left with Austria by the peace, titled to them by treaty.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 6
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (OPEN BORDERS → PEACE)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 35 — Late February 1807
  - MAILBOX #25 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #32 → grant the petition
  - POPUP proposal_result: Bavaria's tribute is remitted for 8 collections (1128g forgone). Loyalty +4 (92 → 96); bond 44 → 44 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, wait×1
  - POPUP redemption: Massena, 20 → grant_autonomy
  -     ↳ Massena has been granted autonomy. They will act independently for 3 turns, using their own judgment in battl…
- LEDGER treasury 6763 · net -108 · threat 25 · provinces 12 (+0) · ceiling 6121 · army 61754 · vassals Bavaria 94 · Holland 67 · Switzerland 68
  - NET income 1040 · trade 437 · admin 50 · upkeep 464 · charges 807 · blockade 274 · admiralty 90
- DISPATCH: Sire — Paris, Artois, Berry and 13 more lie in enemy hands — the capital among them. Prussia and Austria hold them.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 36 — Early March 1807
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 6679 · net -70 · threat 23 · provinces 12 (+0) · ceiling 6262 · army 59462 · vassals Bavaria 92 · Holland 67 · Switzerland 66
  - NET income 1040 · trade 437 · admin 50 · upkeep 440 · charges 793 · blockade 274 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 17 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 2705 gold.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Britain (defensive alliance)

## Turn 37 — Late March 1807
  - MAILBOX #26 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #33 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 6757 · net +67 · threat 21 · provinces 12 (+0) · ceiling 7236 · army 58008 · vassals Bavaria 90 · Holland 67 · Switzerland 64
  - NET income 1040 · trade 437 · admin 50 · upkeep 432 · charges 664 · blockade 274 · admiralty 90
- DISPATCH: Sire — Austria enacts the New Infantry Regulations — +5 morale from every drill.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 38 — Early April 1807
  - MAILBOX #27 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #34 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 6824 · net +58 · threat 19 · provinces 12 (+0) · ceiling 7236 · army 56600 · vassals Bavaria 88 · Holland 67 · Switzerland 54
  - NET income 1040 · trade 437 · admin 50 · upkeep 432 · charges 673 · blockade 274 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 19 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG coalition_dissolved: Coalition against France has dissolved — Britain remains at war with us.

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 6930 · net +517 · threat 17 · provinces 12 (+0) · ceiling 10631 · army 55235 · vassals Bavaria 86 · Holland 67 · Switzerland 44
  - NET income 1040 · trade 437 · admin 50 · tribute 426 · upkeep 384 · charges 688 · blockade 274 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 20 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 7453 · net +675 · threat 15 · provinces 12 (+0) · ceiling 12286 · army 53912 · vassals Bavaria 84 · Holland 67 · Switzerland 34
  - NET income 1040 · trade 437 · admin 50 · tribute 657 · upkeep 384 · charges 761 · blockade 274 · admiralty 90
- DISPATCH: Sire — Talleyrand reports unrest in Switzerland. The Emperor's grip is slipping - coin and concessions no longer hold them. Cede them a province, win a decisive battle to restore your grip, or releas…
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

---
finished: **completed** · commands 109 · popups 74 · battles 36
