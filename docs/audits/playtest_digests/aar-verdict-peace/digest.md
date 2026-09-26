# Playtest digest — aar-verdict-peace

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `44e06929008d` · content `344bd7945dbe` · driver `196c4ee545c1`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on …
  - ⚔ Archduke Charles (lost 4875) vs Massena (lost 5379) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2512 · net +1961 · threat 68 · provinces 28 · ceiling 54105 · army 183621 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
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
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties… · Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,166, Lan… · ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archduke…
  - ⚔ Archduke Charles (lost 3902) vs Massena (lost 5293) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 5166) vs Lannes (lost 1487, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 1757) vs Bernadotte (lost 4559) — The engagement proceeded as one might expect, Sire.
  - verbs: attack×3
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4276 · net +2288 · threat 66 · provinces 28 (+0) · ceiling 50020 · army 169638 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3382 · trade 450 · admin 50 · tribute 856 · upkeep 2022 · charges 113 · blockade 225 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,559 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +5 medium/low (diplomatic_treaty_signed ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A… · Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4,438, Lan… · ArchdukeCharles faces a difficult fight. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles 1,… · Mack delivers an effective strike. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack 3,839,…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 982) vs Bernadotte (lost 7071) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 4438) vs Lannes (lost 1427, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 1811) vs Deroy (lost 4964) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - ⚔ Mack (lost 3839) vs Murat (lost 2224, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6395 · net +2611 · threat 64 · provinces 28 (+0) · ceiling 47187 · army 153859 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3352 · trade 525 · admin 50 · tribute 860 · upkeep 1542 · charges 281 · blockade 263 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 12 approaches from Prussia, Naples and Denmark are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #9 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). → display-only
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, fortify×1, wait×1
- LEDGER treasury 9804 · net +3265 · threat 32 · provinces 28 (+0) · ceiling 281833 · army 153282 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3354 · trade 623 · admin 50 · tribute 865 · upkeep 1534 · charges 93
- DISPATCH: Bernadotte's army is recovering. Effectiveness penalty: -15%.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: Austria, Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 64 to 32.

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 13097 · net +3253 · threat 32 · provinces 28 (+0) · ceiling 284166 · army 152717 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 86
  - NET income 3356 · trade 623 · admin 50 · tribute 869 · upkeep 1512 · charges 133
- DISPATCH: Bernadotte's army has fully recovered and is combat ready.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Spain rebuffs Prussia, Naples and Denmark (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 6 — Early December 1805
  - MAILBOX #9 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #10 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +8 (92 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 16028 · net +2896 · threat 32 · provinces 28 (+0) · ceiling 257333 · army 152163 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3358 · trade 623 · admin 50 · tribute 537 · upkeep 1504 · charges 168
- DISPATCH: Supply cost you 554 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 7 — Late December 1805
  - MAILBOX #10 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 18735 · net +2675 · threat 32 · provinces 28 (+0) · ceiling 241583 · army 151620 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 93
  - NET income 3360 · trade 623 · admin 50 · tribute 316 · upkeep 1474 · charges 200
- DISPATCH: Supply cost you 543 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 21417 · net +2649 · threat 32 · provinces 28 (+0) · ceiling 242166 · army 151088 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 92
  - NET income 3362 · trade 623 · admin 50 · tribute 321 · upkeep 1474 · charges 233
- DISPATCH: Supply cost you 532 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 24094 · net +2645 · threat 32 · provinces 28 (+0) · ceiling 244500 · army 150566 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3364 · trade 623 · admin 50 · tribute 325 · upkeep 1452 · charges 265
- DISPATCH: Supply cost you 522 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 26754 · net +2628 · threat 32 · provinces 28 (+0) · ceiling 245750 · army 150055 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3366 · trade 623 · admin 50 · tribute 330 · upkeep 1444 · charges 297
- DISPATCH: Supply cost you 511 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 29410 · net +2625 · threat 32 · provinces 28 (+0) · ceiling 248083 · army 149555 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 89
  - NET income 3368 · trade 623 · admin 50 · tribute 334 · upkeep 1422 · charges 328
- DISPATCH: Supply cost you 500 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 32050 · net +2608 · threat 32 · provinces 28 (+0) · ceiling 249333 · army 149064 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3370 · trade 623 · admin 50 · tribute 339 · upkeep 1414 · charges 360
- DISPATCH: Supply cost you 491 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 34694 · net +2949 · threat 30 · provinces 28 (+0) · ceiling 280416 · army 148583 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 87
  - NET income 3372 · trade 623 · admin 50 · tribute 680 · upkeep 1384 · charges 392
- DISPATCH: Supply cost you 481 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 37650 · net +3146 · threat 28 · provinces 28 (+0) · ceiling 299750 · army 148112 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 86
  - NET income 3374 · trade 623 · admin 50 · tribute 910 · upkeep 1384 · charges 427
- DISPATCH: Supply cost you 471 men, at Franche-Comte.
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
- LEDGER treasury 40487 · net +2803 · threat 26 · provinces 28 (+0) · ceiling 274000 · army 147650 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 85
  - NET income 3376 · trade 623 · admin 50 · tribute 577 · upkeep 1362 · charges 461
- DISPATCH: Supply cost you 462 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 16 — Early May 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (85 → 95); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 43072 · net +2554 · threat 24 · provinces 28 (+0) · ceiling 255833 · army 147197 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3378 · trade 623 · admin 50 · tribute 357 · upkeep 1362 · charges 492
- DISPATCH: Supply cost you 453 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 45670 · net +2566 · threat 22 · provinces 28 (+0) · ceiling 259500 · army 146753 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3380 · trade 623 · admin 50 · tribute 361 · upkeep 1324 · charges 524
- DISPATCH: Supply cost you 444 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 48243 · net +2543 · threat 20 · provinces 28 (+0) · ceiling 260083 · army 146318 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3382 · trade 623 · admin 50 · tribute 366 · upkeep 1324 · charges 554
- DISPATCH: Supply cost you 435 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 50814 · net +2540 · threat 18 · provinces 28 (+0) · ceiling 262416 · army 145892 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3384 · trade 623 · admin 50 · tribute 370 · upkeep 1302 · charges 585
- DISPATCH: Supply cost you 426 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 53361 · net +2516 · threat 16 · provinces 28 (+0) · ceiling 263000 · army 145474 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3386 · trade 623 · admin 50 · tribute 375 · upkeep 1302 · charges 616
- DISPATCH: Supply cost you 418 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 55879 · net +2488 · threat 14 · provinces 28 (+0) · ceiling 263166 · army 145065 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3388 · trade 623 · admin 50 · tribute 375 · upkeep 1302 · charges 646
- DISPATCH: Supply cost you 409 men, at Franche-Comte.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 58407 · net +2835 · threat 12 · provinces 28 (+0) · ceiling 294583 · army 144664 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3390 · trade 623 · admin 50 · tribute 712 · upkeep 1264 · charges 676
- DISPATCH: Supply cost you 401 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 61244 · net +3028 · threat 10 · provinces 28 (+0) · ceiling 313500 · army 144271 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3392 · trade 623 · admin 50 · tribute 937 · upkeep 1264 · charges 710
- DISPATCH: Supply cost you 393 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 64296 · net +3015 · threat 8 · provinces 28 (+0) · ceiling 315500 · army 143886 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3394 · trade 623 · admin 50 · tribute 937 · upkeep 1242 · charges 747
- DISPATCH: Supply cost you 385 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 67313 · net +2981 · threat 6 · provinces 28 (+0) · ceiling 315666 · army 143508 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3396 · trade 623 · admin 50 · tribute 937 · upkeep 1242 · charges 783
- DISPATCH: Supply cost you 378 men, at Franche-Comte.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 70304 · net +2955 · threat 4 · provinces 28 (+0) · ceiling 316500 · army 143139 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3398 · trade 623 · admin 50 · tribute 937 · upkeep 1234 · charges 819
- DISPATCH: Supply cost you 369 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 73283 · net +2943 · threat 2 · provinces 28 (+0) · ceiling 318500 · army 142777 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1212 · charges 855
- DISPATCH: Supply cost you 362 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 76234 · net +2916 · threat 0 · provinces 28 (+0) · ceiling 319166 · army 142422 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1204 · charges 890
- DISPATCH: Supply cost you 355 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
  - MAILBOX #13 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #14 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 79150 · net +2881 · threat 0 · provinces 28 (+0) · ceiling 319166 · army 142074 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1204 · charges 925
- DISPATCH: Supply cost you 348 men, at Franche-Comte.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 30 — Early December 1806
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 82053 · net +2868 · threat 0 · provinces 28 (+0) · ceiling 321000 · army 141732 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1182 · charges 960
- DISPATCH: Supply cost you 342 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 84921 · net +2833 · threat 0 · provinces 28 (+0) · ceiling 321000 · army 141398 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1182 · charges 995
- DISPATCH: Supply cost you 334 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Spain rebuffs Naples and Denmark (open borders agreement)

## Turn 32 — Early January 1807
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 87762 · net +2807 · threat 0 · provinces 28 (+0) · ceiling 321666 · army 141071 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1174 · charges 1029
- DISPATCH: Supply cost you 327 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
  - MAILBOX #14 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #15 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 90591 · net +2795 · threat 0 · provinces 28 (+0) · ceiling 323500 · army 140750 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 1152 · charges 1063
- DISPATCH: Supply cost you 321 men, at Franche-Comte.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 93356 · net +2732 · threat 0 · provinces 28 (+0) · ceiling 321000 · army 140435 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1144 · charges 1096
- DISPATCH: Supply cost you 315 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 96088 · net +2699 · threat 0 · provinces 28 (+0) · ceiling 321000 · army 140126 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1144 · charges 1129
- DISPATCH: Supply cost you 309 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 36 — Early March 1807
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 98791 · net +2671 · threat 0 · provinces 28 (+0) · ceiling 321333 · army 139824 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1140 · charges 1161
- DISPATCH: Supply cost you 302 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 37 — Late March 1807
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 101462 · net +2639 · threat 0 · provinces 28 (+0) · ceiling 321333 · army 139528 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1140 · charges 1193
- DISPATCH: Supply cost you 296 men, at Franche-Comte.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 104109 · net +2615 · threat 0 · provinces 28 (+0) · ceiling 322000 · army 139237 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1132 · charges 1225
- DISPATCH: Supply cost you 291 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 106728 · net +2588 · threat 0 · provinces 28 (+0) · ceiling 322333 · army 138953 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1128 · charges 1256
- DISPATCH: Supply cost you 284 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 109316 · net +2557 · threat 0 · provinces 28 (+0) · ceiling 322333 · army 138675 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1128 · charges 1287
- DISPATCH: Supply cost you 278 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)

## Turn 41 — Late May 1807
- CMD `end turn` → ✓ Turn 41 ended. (Warning: 4 actions unused) Turn 42 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 111873 · net +2526 · threat 0 · provinces 28 (+0) · ceiling 322333 · army 138402 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1128 · charges 1318
- DISPATCH: Supply cost you 273 men, at Franche-Comte.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 42 — Early June 1807
- CMD `end turn` → ✓ Turn 42 ended. (Warning: 4 actions unused) Turn 43 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 114407 · net +2504 · threat 0 · provinces 28 (+0) · ceiling 323000 · army 138135 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1120 · charges 1348
- DISPATCH: Supply cost you 267 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 43 — Late June 1807
- CMD `end turn` → ✓ Turn 43 ended. (Warning: 4 actions unused) Turn 44 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 116915 · net +2478 · threat 0 · provinces 28 (+0) · ceiling 323333 · army 137873 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1116 · charges 1378
- DISPATCH: Supply cost you 262 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 44 — Early July 1807
- CMD `end turn` → ✓ Turn 44 ended. (Warning: 4 actions unused) Turn 45 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - ENDING — THE VERDICT OF HISTORY: The reign, unfinished, is judged as it stands. [AN EMPIRE CONTESTED]
  -     ↳ Early July 1807 (turn 44) · register `verdict` · marked — the campaign continues
  -     ↳ THE VERDICT — AN EMPIRE CONTESTED: The Empire holds what it held, and Europe has not accepted it. / The field has gone against it more often than not, and the table is no kinder. / History will call it unfinished — the question of 1805, still open.
  -     ↳ The Verdict of History: an empire contested, the question of 1805 still open.
  -     ↳ THE RECORD — battles 7 (0 won, 2 lost) · men lost 34,440, inflicted 24,959 · provinces taken 0, lost 0 · marshals fallen 0, taken 0 · coalitions faced 1 · peaces signed 1
- LEDGER treasury 119401 · net +2456 · threat 0 · provinces 28 (+0) · ceiling 324000 · army 137616 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 1108 · charges 1408
- DISPATCH: Supply cost you 257 men, at Franche-Comte.
  - TURN EVENTS 1
- COURTS: The court of Russia eases over Arbiter of Europe — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - ENDING reached — stopping (--stop-on-ending)

---
finished: **ending-reached** · commands 44 · popups 21 · battles 8
