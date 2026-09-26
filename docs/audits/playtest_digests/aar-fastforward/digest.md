# Playtest digest — aar-fastforward

seed `historical` · llm `mock` · transport http://127.0.0.1:8007 · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "pay", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `None` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `None`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `44e06929008d` · content `344bd7945dbe` · driver `196c4ee545c1`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles struggles in a costly engagement. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualtie…
  - ⚔ Archduke Charles (lost 4258) vs Massena (lost 5585) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2501 · net +1961 · threat 68 · provinces 28 · ceiling 54105 · army 183415 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 3400 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · charges 19 · blockade 175 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Massena. Casualties: Arch… · Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4,794, L… · Mack engages in solid combat. Mack gains the advantage over Murat. Casualties: Mack 3,388, Murat's army 5,836. Both arm…
  - ⚔ Archduke Charles (lost 3389) vs Massena (lost 5996) — Massena was close. A period of drilling could have changed the outcome.
  - ⚔ Mack (lost 4794) vs Lannes (lost 1642, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Mack (lost 3388) vs Murat (lost 3210, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×3
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4008 · net +2097 · threat 66 · provinces 28 (+0) · ceiling 28964 · army 166245 · vassals Holland 96 · Kingdom of Italy 98 · Switzerland 92
  - NET income 3362 · trade 450 · admin 50 · tribute 712 · upkeep 1932 · charges 168 · contributions 62 · blockade 225 · admiralty 90
- DISPATCH: Sire — Mack has crossed into Franche-Comte. Lannes and Murat stand in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_treaty_signed ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 22 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeChar…
  - ⚔ Archduke Charles (lost 3059) vs Massena (lost 5173) — The margin was slim. Training and preparation would serve Massena well.
  - verbs: attack×1, move×1, wait×1
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6295 · net +2310 · threat 64 · provinces 28 (+0) · ceiling 43548 · army 159930 · vassals Holland 94 · Kingdom of Italy 98 · Switzerland 88
  - NET income 3364 · trade 525 · admin 50 · tribute 712 · upkeep 1722 · charges 266 · blockade 263 · admiralty 90
- DISPATCH: Supply cost you 1,142 men, at Rhineland.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia and Naples are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 24 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #9 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). → display-only
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 9536 · net +3098 · threat 32 · provinces 28 (+0) · ceiling 267666 · army 158834 · vassals Holland 92 · Kingdom of Italy 98 · Switzerland 86
  - NET income 3366 · trade 623 · admin 50 · tribute 833 · upkeep 1684 · charges 90
- DISPATCH: Supply cost you 1,096 men, at Rhineland.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 2
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 64 to 32.

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 12663 · net +3090 · threat 32 · provinces 28 (+0) · ceiling 270083 · army 157782 · vassals Holland 90 · Kingdom of Italy 98 · Switzerland 84
  - NET income 3368 · trade 623 · admin 50 · tribute 838 · upkeep 1662 · charges 127
- DISPATCH: Supply cost you 1,052 men, at Rhineland.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 6 — Early December 1805
  - MAILBOX #9 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #10 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 15460 · net +2763 · threat 32 · provinces 28 (+0) · ceiling 245666 · army 156771 · vassals Holland 99 · Kingdom of Italy 98 · Switzerland 82
  - NET income 3370 · trade 623 · admin 50 · tribute 505 · upkeep 1624 · charges 161
- DISPATCH: Supply cost you 1,011 men, at Rhineland.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 7 — Late December 1805
  - MAILBOX #10 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 18027 · net +2536 · threat 32 · provinces 28 (+0) · ceiling 229333 · army 155798 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 91
  - NET income 3372 · trade 623 · admin 50 · tribute 285 · upkeep 1602 · charges 192
- DISPATCH: Supply cost you 973 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 20599 · net +2541 · threat 32 · provinces 28 (+0) · ceiling 232333 · army 154861 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 90
  - NET income 3374 · trade 623 · admin 50 · tribute 289 · upkeep 1572 · charges 223
- DISPATCH: Supply cost you 937 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 23177 · net +2547 · threat 32 · provinces 28 (+0) · ceiling 235416 · army 153959 · vassals Holland 96 · Kingdom of Italy 98 · Switzerland 89
  - NET income 3376 · trade 623 · admin 50 · tribute 294 · upkeep 1542 · charges 254
- DISPATCH: Supply cost you 902 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 25738 · net +2531 · threat 32 · provinces 28 (+0) · ceiling 236583 · army 153089 · vassals Holland 95 · Kingdom of Italy 98 · Switzerland 88
  - NET income 3378 · trade 623 · admin 50 · tribute 298 · upkeep 1534 · charges 284
- DISPATCH: Supply cost you 870 men, at Rhineland.
  - TURN EVENTS 1
- COURTS: The court of Austria hardens over Redeem Italy — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 28306 · net +2537 · threat 32 · provinces 28 (+0) · ceiling 239666 · army 152250 · vassals Holland 94 · Kingdom of Italy 98 · Switzerland 87
  - NET income 3380 · trade 623 · admin 50 · tribute 303 · upkeep 1504 · charges 315
- DISPATCH: Supply cost you 839 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 30879 · net +2542 · threat 32 · provinces 28 (+0) · ceiling 242666 · army 151427 · vassals Holland 93 · Kingdom of Italy 98 · Switzerland 86
  - NET income 3382 · trade 623 · admin 50 · tribute 307 · upkeep 1474 · charges 346
- DISPATCH: Supply cost you 823 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 33458 · net +2885 · threat 30 · provinces 28 (+0) · ceiling 273833 · army 150621 · vassals Holland 92 · Kingdom of Italy 98 · Switzerland 85
  - NET income 3384 · trade 623 · admin 50 · tribute 649 · upkeep 1444 · charges 377
- DISPATCH: Supply cost you 806 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 36371 · net +3103 · threat 28 · provinces 28 (+0) · ceiling 294916 · army 149831 · vassals Holland 91 · Kingdom of Italy 98 · Switzerland 84
  - NET income 3386 · trade 623 · admin 50 · tribute 878 · upkeep 1422 · charges 412
- DISPATCH: Supply cost you 790 men, at Rhineland.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 15 — Late April 1806
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #12 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 39152 · net +2748 · threat 26 · provinces 28 (+0) · ceiling 268083 · army 149056 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 83
  - NET income 3388 · trade 623 · admin 50 · tribute 546 · upkeep 1414 · charges 445
- DISPATCH: Supply cost you 775 men, at Rhineland.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 16 — Early May 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 41711 · net +2528 · threat 24 · provinces 28 (+0) · ceiling 252333 · army 148297 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3390 · trade 623 · admin 50 · tribute 325 · upkeep 1384 · charges 476
- DISPATCH: Supply cost you 759 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 44276 · net +2534 · threat 22 · provinces 28 (+0) · ceiling 255416 · army 147553 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3392 · trade 623 · admin 50 · tribute 330 · upkeep 1354 · charges 507
- DISPATCH: Supply cost you 744 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 46838 · net +2531 · threat 20 · provinces 28 (+0) · ceiling 257750 · army 146824 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3394 · trade 623 · admin 50 · tribute 334 · upkeep 1332 · charges 538
- DISPATCH: Supply cost you 729 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 49384 · net +2516 · threat 18 · provinces 28 (+0) · ceiling 259000 · army 146110 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3396 · trade 623 · admin 50 · tribute 339 · upkeep 1324 · charges 568
- DISPATCH: Supply cost you 714 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 51936 · net +2521 · threat 16 · provinces 28 (+0) · ceiling 262000 · army 145410 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3398 · trade 623 · admin 50 · tribute 343 · upkeep 1294 · charges 599
- DISPATCH: Supply cost you 700 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 54486 · net +2520 · threat 14 · provinces 28 (+0) · ceiling 264416 · army 144724 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 348 · upkeep 1272 · charges 629
- DISPATCH: Supply cost you 686 men, at Rhineland.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 57018 · net +2838 · threat 12 · provinces 28 (+0) · ceiling 293500 · army 144052 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 689 · upkeep 1264 · charges 660
- DISPATCH: Supply cost you 672 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 59891 · net +3064 · threat 10 · provinces 28 (+0) · ceiling 315166 · army 143393 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 919 · upkeep 1234 · charges 694
- DISPATCH: Supply cost you 659 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 62981 · net +3053 · threat 8 · provinces 28 (+0) · ceiling 317333 · army 142747 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 923 · upkeep 1212 · charges 731
- DISPATCH: Supply cost you 646 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 66047 · net +3029 · threat 6 · provinces 28 (+0) · ceiling 318416 · army 142114 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 928 · upkeep 1204 · charges 768
- DISPATCH: Supply cost you 633 men, at Rhineland.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: 23 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 69110 · net +3026 · threat 4 · provinces 28 (+0) · ceiling 321250 · army 141494 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 932 · upkeep 1174 · charges 805
- DISPATCH: Supply cost you 620 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Bavaria (open borders agreement)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 72163 · net +3017 · threat 2 · provinces 28 (+0) · ceiling 323500 · army 140886 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1152 · charges 841
- DISPATCH: Supply cost you 608 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 10 courts rebuff Bavaria (open borders agreement)

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 75180 · net +2980 · threat 0 · provinces 28 (+0) · ceiling 323500 · army 140290 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1152 · charges 878
- DISPATCH: Supply cost you 596 men, at Rhineland.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 29 — Late November 1806
  - MAILBOX #13 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #14 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 78180 · net +2964 · threat 0 · provinces 28 (+0) · ceiling 325166 · army 139707 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1132 · charges 914
- DISPATCH: Supply cost you 583 men, at Rhineland.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 30 — Early December 1806
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 81144 · net +2929 · threat 0 · provinces 28 (+0) · ceiling 325166 · army 139136 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1132 · charges 949
- DISPATCH: Supply cost you 571 men, at Rhineland.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

---
finished: **completed** · commands 30 · popups 20 · battles 5
