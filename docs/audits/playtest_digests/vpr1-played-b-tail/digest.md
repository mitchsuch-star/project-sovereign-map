# Playtest digest — vpr1-played-b-tail

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "breakout", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "decline_from": "Hanover,Austria"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 17 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `08ed3d374c35` (dirty) · content `ac2f6d51ede2` · driver `196c4ee545c1`
  - loaded save `vpr1-played-b5.save.json` → Loaded: Autosave - Turn 17

## Turn 17 — Late May 1806
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, wait×1
- ORDER Massena [continues]: Massena marches to Burgundy. 2 regions to Paris.
- ORDER Napoleon [completed]: Napoleon arrives at Paris.
- ORDER Soult [completed]: The order was "the road home — safe passage granted by the peace". Soult arrives at Franche-Comte. I await further instruction.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
  - POPUP vassal_rebellion_imminent: Hesse #33 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Hesse's loyalty reaches zero, rebellion will follow. → display-only
- LEDGER treasury 26582 · net +1587 · threat 62 · provinces 32 · ceiling 41893 · army 82800 · vassals Hesse 4 · Holland 98 · Switzerland 85
  - NET income 3773 · trade 473 · admin 50 · tribute 712 · upkeep 648 · charges 2546 · occupation 137 · admiralty 90
- DISPATCH: Sire — under the peace with Britain. Soult is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 5 …
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Hesse is on the verge of rebellion!
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 6
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as war.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Hanover rebuffs Austria (defensive alliance)
  - LOG nation_eliminated: Hanover has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Spain and Denmark rebuff Hanover (non-aggression pact)
  - LOG ai_proposal_rejected: We rejected Hanover's armistice proposal
  - LOG ai_proposal_rejected: We rejected Hanover's armistice proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 1 more — France is not forgiven
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 8 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×4, unfortify×2, recruit×2
- ORDER Massena [continues]: Massena marches to Limousin. 1 region to Paris.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 28708 · net +1962 · threat 50 · provinces 32 (+0) · ceiling 54252 · army 82800 · vassals Holland 97 · Switzerland 84
  - NET income 3883 · trade 473 · admin 50 · tribute 450 · upkeep 648 · charges 2051 · occupation 105 · admiralty 90
- DISPATCH: Sire — Hesse is no longer ours. Austria is their protector now.
  - RAIL diplomatic_vassal_transferred: Hesse passes from France's suzerainty to Austria's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Austria's gold turns Hesse against France.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 19 — Late June 1806
  - MAILBOX #22 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #34 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Deroy. Heavy casualti… · Hiller's forces press forward aggressively. Davout holds the line. Casualties: Hiller's army 2,762, Davout's army 676. … · ArchdukeCharles marches from Franconia into Tyrol unopposed! (398 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Franconia into Tyrol unopposed! (398 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 1757, own corps) vs Deroy (lost 1533, own corps) — Stalemate. Deroy and Archduke Charles glare at each other across the field.
  - ⚔ Hiller (lost 493, own corps) vs Davout (lost 296, own corps) — The prepared defenses proved their worth. Hiller could not dislodge Davout.
  - verbs: attack×3
- ORDER Massena [completed]: Massena arrives at Paris. Massena: "Accomplished. The men want a battle, not another road."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 30259 · net +1580 · threat 48 · provinces 31 (-1) · ceiling 49610 · army 79392 · vassals Holland 97 · Switzerland 84
  - NET income 3743 · trade 423 · admin 50 · tribute 450 · upkeep 616 · charges 2305 · occupation 75 · admiralty 90
- DISPATCH: Sire — Tyrol has been taken by Austria.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, recruit×2, move×1
- LEDGER treasury 31562 · net +1193 · threat 46 · provinces 31 (+0) · ceiling 45620 · army 79392 · vassals Holland 96 · Switzerland 83
  - NET income 3764 · trade 423 · admin 50 · tribute 450 · upkeep 616 · charges 2506 · occupation 70 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Massena's claim is 12 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, blockade_begins)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 32668 · net +1009 · threat 44 · provinces 31 (+0) · ceiling 44125 · army 79392 · vassals Holland 97 · Switzerland 82
  - NET income 3772 · trade 423 · admin 50 · tribute 450 · upkeep 616 · charges 2698 · occupation 70 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Massena's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 33583 · net +1056 · threat 42 · provinces 31 (+0) · ceiling 45157 · army 79392 · vassals Holland 98 · Switzerland 81
  - NET income 3776 · trade 423 · admin 50 · tribute 675 · upkeep 616 · charges 2880 · occupation 70 · blockade 212 · admiralty 90
- DISPATCH: Sire — the levy has stood open 7 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. Davout holds the line. Casualties: ArchdukeCharles's army 2,968, Davou… · Hiller's forces press forward aggressively. Davout holds the line. Casualties: Hiller's army 3,721, Davout's army 478. …
  - ⚔ Archduke Charles (lost 2587, own corps) vs Davout (lost 663, own corps) — The prepared defenses proved their worth. Archduke Charles could not dislodge Davout.
  - ⚔ Hiller (lost 532, own corps) vs Davout (lost 209, own corps) — A decisive victory for Davout! Hiller was thoroughly outmatched.
  - verbs: attack×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #35 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #36 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Holland, client_petition #37 → grant the petition
  - POPUP proposal_result: Osnabruck is ceded to Holland. Loyalty +0 (100 → 100, already full); bond 25 → 40 (+2 a turn). Cost: 1 DP. Our net falls by 8g a turn — 50g of income forfeited, 5g of occupation relieved, 37g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- ENVOYS WAITING 3 · Austria armistice losing · Britain settlement offer · Holland client petition
- LEDGER treasury 34400 · net +819 · threat 40 · provinces 30 (-1) · ceiling 42962 · army 77403 · vassals Holland 100 · Switzerland 82
  - NET income 3690 · trade 423 · admin 50 · tribute 712 · upkeep 592 · charges 3097 · occupation 65 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Hiller's corps is driven from Bohemia yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Schwarzenberg's forces advance steadily. Davout holds the line. Casualties: Schwarzenberg 1,457, Davout's army 224. Bot…
  - ⚔ Schwarzenberg (lost 1457) vs Davout (lost 98, own corps) — Davout's fortifications held firm, Sire. Schwarzenberg broke against our walls.
  - verbs: move×2, attack×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 35089 · net +631 · threat 40 · provinces 30 (+0) · ceiling 41473 · army 77179 · vassals Holland 100 · Switzerland 82
  - NET income 3674 · trade 423 · admin 50 · tribute 712 · upkeep 592 · charges 3269 · occupation 65 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Schwarzenberg's corps is driven from Bohemia yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
  - MAILBOX #26 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #38 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. Davout holds the line. Casualties: ArchdukeCharles 3,924, Davout's army 778.…
  - ⚔ Archduke Charles (lost 3924) vs Davout (lost 341, own corps) — A wise investment in fortification. Davout's position was impregnable to Archduke Charles's assault.
  - verbs: attack×1, move×1, wait×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Davout: Murat turns openly discontent (trust -3; expect defiance).
- LEDGER treasury 35326 · net +247 · threat 40 · provinces 30 (+0) · ceiling 37732 · army 76401 · vassals Holland 100 · Switzerland 93
  - NET income 3658 · trade 423 · admin 50 · tribute 487 · upkeep 592 · charges 3412 · occupation 65 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Archduke Charles's corps is driven from Bohemia yet again — broken, and fleeing.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, wait×2, move×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 35470 · net +129 · threat 40 · provinces 30 (+0) · ceiling 36687 · army 76401 · vassals Holland 100 · Switzerland 93
  - NET income 3662 · trade 423 · admin 50 · tribute 487 · upkeep 592 · charges 3534 · occupation 65 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Massena's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. Davout holds the line. Casualties: ArchdukeCharles 3,253, Davout's army 954.…
  - ⚔ Archduke Charles (lost 3253) vs Davout (lost 418, own corps) — The prepared defenses proved their worth. Archduke Charles could not dislodge Davout.
  - verbs: attack×1, wait×1
- LEDGER treasury 35423 · net +0 · threat 40 · provinces 30 (+0) · ceiling 35421 · army 75447 · vassals Holland 100 · Switzerland 94
  - NET income 3654 · trade 423 · admin 50 · tribute 487 · upkeep 584 · charges 3663 · occupation 65 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Archduke Charles's corps is driven from Bohemia yet again — broken, and fleeing.
  - TURN EVENTS 2
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, move×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 35320 · net -91 · threat 38 · provinces 30 (+0) · ceiling 34508 · army 75447 · vassals Holland 100 · Switzerland 94
  - NET income 3658 · trade 423 · admin 50 · tribute 487 · upkeep 584 · charges 3758 · occupation 65 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Massena's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
  - MAILBOX #27 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #39 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Davout holds the line. Casualties: ArchdukeCharles 3,274, Davout's army 1,…
  - ⚔ Archduke Charles (lost 3274) vs Davout (lost 483, own corps) — A wise investment in fortification. Davout's position was impregnable to Archduke Charles's assault.
  - verbs: attack×1
- LEDGER treasury 35064 · net -177 · threat 36 · provinces 30 (+0) · ceiling 33537 · army 74346 · vassals Holland 100 · Switzerland 95
  - NET income 3654 · trade 423 · admin 50 · tribute 487 · upkeep 576 · charges 3848 · occupation 65 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Archduke Charles's corps is driven from Bohemia yet again — broken, and fleeing.
  - TURN EVENTS 1
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 30 — Early December 1806
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Hiller's forces advance steadily. Davout holds the line. Casualties: Hiller's army 2,431, Davout's army 333. Both armie…
  - ⚔ Hiller (lost 999, own corps) vs Davout (lost 146, own corps) — A wise investment in fortification. Davout's position was impregnable to Hiller's assault.
  - verbs: move×3, attack×1, recruit×1
- LEDGER treasury 34754 · net -259 · threat 34 · provinces 30 (+0) · ceiling 32591 · army 74013 · vassals Holland 100 · Switzerland 96
  - NET income 3654 · trade 423 · admin 50 · tribute 487 · upkeep 576 · charges 3930 · occupation 65 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Hiller's corps is driven from Bohemia yet again — broken, and fleeing.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. Davout holds the line. Casualties: ArchdukeCharles 2,796, Davout's army 1,085.…
  - ⚔ Archduke Charles (lost 2796) vs Davout (lost 476, own corps) — Davout's fortifications held firm, Sire. Archduke Charles broke against our walls.
  - verbs: move×2, wait×2, attack×1, recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #40 → grant the petition
  - POPUP proposal_result: Oldenburg is ceded to Holland. Loyalty +0 (100 → 100, already full); bond 40 → 40 (+2 a turn). Cost: 1 DP. Our net falls by 15g a turn — 100g of income forfeited, 10g of occupation relieved, 75g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 34346 · net -325 · threat 32 · provinces 29 (-1) · ceiling 31708 · army 72928 · vassals Holland 100 · Switzerland 97
  - NET income 3554 · trade 423 · admin 50 · tribute 562 · upkeep 560 · charges 3997 · occupation 55 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Archduke Charles's corps is driven from Bohemia yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 32 — Early January 1807
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, move×1, fortify×1
- LEDGER treasury 33921 · net -146 · threat 30 · provinces 29 (+0) · ceiling 32764 · army 72928 · vassals Holland 100 · Switzerland 97
  - NET income 3558 · trade 423 · admin 50 · tribute 787 · upkeep 560 · charges 4047 · occupation 55 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Massena's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. Davout holds the line. Casualties: ArchdukeCharles 2,358, Davout's army 1…
  - ⚔ Archduke Charles (lost 2358) vs Davout (lost 475, own corps) — A wise investment in fortification. Davout's position was impregnable to Archduke Charles's assault.
  - verbs: attack×1, fortify×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #41 → reject_settlement_offer
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 33617 · net -217 · threat 28 · provinces 29 (+0) · ceiling 31946 · army 71846 · vassals Holland 100 · Switzerland 98
  - NET income 3554 · trade 423 · admin 50 · tribute 787 · upkeep 552 · charges 4122 · occupation 55 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Archduke Charles's corps is driven from Bohemia yet again — broken, and fleeing.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 33302 · net -272 · threat 26 · provinces 29 (+0) · ceiling 31258 · army 71846 · vassals Holland 100 · Switzerland 98
  - NET income 3558 · trade 423 · admin 50 · tribute 787 · upkeep 552 · charges 4181 · occupation 55 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Massena's claim is 26 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Davout holds the line. Casualties: ArchdukeCharles's army 2,223, Davout's … · ArchdukeCharles's forces press forward aggressively. Davout holds the line. Casualties: ArchdukeCharles 2,223, Davout's…
  - ⚔ Archduke Charles (lost 1978, own corps) vs Davout (lost 587, own corps) — The prepared defenses proved their worth. Archduke Charles could not dislodge Davout.
  - ⚔ Archduke Charles (lost 2223) vs Davout (lost 438, own corps) — A wise investment in fortification. Davout's position was impregnable to Archduke Charles's assault.
  - verbs: attack×2, unfortify×1, wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 32792 · net -340 · threat 24 · provinces 29 (+0) · ceiling 30330 · army 69511 · vassals Holland 100 · Switzerland 100
  - NET income 3554 · trade 423 · admin 50 · tribute 787 · upkeep 536 · charges 4261 · occupation 55 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Bohemia — Archduke Charles's corps is driven from Bohemia yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 36 — Early March 1807
  - MAILBOX #30 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #42 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, unfortify×1
- LEDGER treasury 32357 · net -373 · threat 22 · provinces 29 (+0) · ceiling 29718 · army 69511 · vassals Holland 100 · Switzerland 100
  - NET income 3558 · trade 423 · admin 50 · tribute 787 · upkeep 536 · charges 4298 · occupation 55 · blockade 212 · admiralty 90
- DISPATCH: Sire — peace with Russia is signed. A white peace — the map stands as it was.
  - RAIL peace_ratified: Peace ratified between Russia and France.
  - TURN EVENTS 4
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Hanover (non-aggression pact)

## Turn 37 — Late March 1807
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Hiller's forces press forward aggressively. Brutal stalemate between Hiller and Davout. Heavy casualties on both sides:…
  - ⚔ Hiller (lost 192, own corps) vs Davout (lost 391, own corps) — The enemy's assault has weakened our works. We must repair or consider withdrawal. — Deroy's faith in you is spent (trust 29) — he committed 3,681 to the fight where he would have brought 7,362.
  - verbs: move×1, attack×1, retreat×1, stance_change×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 31833 · net -410 · threat 20 · provinces 29 (+0) · ceiling 29004 · army 68573 · vassals Holland 100 · Switzerland 100
  - NET income 3554 · trade 423 · admin 50 · tribute 787 · upkeep 536 · charges 4331 · occupation 55 · blockade 212 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Prussia against France (400g/turn)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Prussia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Prussia lapses
  - LOG sponsorship_granted: Russia sponsors Sweden against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Prussia lapses
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 7 approaches from Sardinia and Prussia are rebuffed (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Prussia against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Prussia against France (400g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Prussia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Sweden against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Prussia lapses
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Hesse rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Russia and Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: 3 approaches from Russia, Austria and Prussia are rebuffed (defensive alliance)

## Turn 38 — Early April 1807
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 31331 · net -427 · threat 18 · provinces 29 (+0) · ceiling 28448 · army 68573 · vassals Holland 100 · Switzerland 100
  - NET income 3558 · trade 423 · admin 50 · tribute 787 · upkeep 536 · charges 4352 · occupation 55 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Massena's claim is 30 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria and Britain remain at war with us.

## Turn 39 — Late April 1807
  - MAILBOX #31 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #43 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Davout. Casualties: Archd… · ArchdukeCharles holds them at Dresden while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Bohemia. (331 lost to march — forward supply lines reduce losses) Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1185) vs Deroy (lost 2816) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 680) vs Davout (lost 1683) — Even Davout's fortifications could not hold, Sire. Archduke Charles overran the position.
  - ⚔ Archduke Charles (lost 284) vs Deroy (lost 3199) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, unfortify×2, move×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 30284 · net -559 · threat 16 · provinces 28 (-1) · ceiling 26740 · army 60494 · vassals Holland 96 · Switzerland 94
  - NET income 3450 · trade 423 · admin 50 · tribute 787 · upkeep 464 · charges 4468 · occupation 35 · blockade 212 · admiralty 90
- DISPATCH: Sire — Deroy's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
  - MAILBOX #32 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #44 → grant the petition
  - POPUP proposal_result: Westphalia is ceded to Holland. Loyalty +4 (96 → 100); bond 40 → 40 (+2 a turn). Cost: 1 DP. Our net falls by 7g a turn — 50g of income forfeited, 5g of occupation relieved, 38g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Davout. Casualties: ArchdukeChar… · Schwarzenberg launches a decisive assault. Schwarzenberg gains the advantage over Deroy. Casualties: Schwarzenberg 157,…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Davout is taken by Austria at Berlin!
  - ⚔ Archduke Charles (lost 259) vs Davout (lost 1645) — Davout's fortified position was overwhelmed. A costly investment lost, Sire. And Davout was taken on that field — Austr…
  - ⚔ Schwarzenberg (lost 157) vs Deroy (lost 795) — Deroy was driven from the field. His men are scattered.
  - verbs: attack×2, fortify×1, grant_dotation×1, wait×1
- LEDGER treasury 29521 · net -538 · threat 14 · provinces 27 (-1) · ceiling 26213 · army 54534 · vassals Holland 98 · Switzerland 90
  - NET income 3400 · trade 423 · admin 50 · tribute 825 · upkeep 424 · charges 4480 · occupation 30 · blockade 212 · admiralty 90
- DISPATCH: Sire — Marshal Davout has been taken. Austria holds him prisoner.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

---
finished: **completed** · commands 24 · popups 28 · battles 19
