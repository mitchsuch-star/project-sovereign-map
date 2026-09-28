# Playtest digest — rs0928-propose

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `91796f250248` · content `8f597da58501` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on …
  - ⚔ Archduke Charles (lost 3508, own corps) vs Massena (lost 6876) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1613 · net +1156 · threat 68 · provinces 28 · ceiling 29523 · army 182124 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2420 · blockade 219 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #5 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles struggles in a costly engagement. ArchdukeCharles gains the advantage over Massena. Casualties: Archduk… · Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,018, L… · Mack engages in solid combat. Mack gains the advantage over Murat. Casualties: Mack 3,582, Murat's army 5,503. Both arm…
  - ⚔ Archduke Charles (lost 3426) vs Massena (lost 5269) — Massena was close. A period of drilling could have changed the outcome.
  - ⚔ Mack (lost 5018) vs Lannes (lost 1607, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Mack (lost 3582) vs Murat (lost 3027, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×3
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2339 · net +1398 · threat 66 · provinces 28 (+0) · ceiling 18364 · army 166102 · vassals Holland 96 · Kingdom of Italy 98 · Switzerland 92
  - NET income 2559 · trade 450 · admin 50 · tribute 712 · upkeep 1924 · charges 29 · contributions 49 · blockade 281 · admiralty 90
- DISPATCH: Sire — Mack has crossed into Franche-Comte. Lannes and Murat stand in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +6 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 22 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #8 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4,083, L… · ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual… · Mack faces a difficult fight. Mack gains the advantage over Murat. Casualties: Mack 2,404, Murat's army 4,062. Both arm…
  - ⚔ Mack (lost 4083) vs Lannes (lost 1060, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 3366) vs Massena (lost 4481) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Mack (lost 2404) vs Murat (lost 2234, own corps) — Soult failed to arrive in time. Murat's army fought without expected support.
  - verbs: attack×3
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3677 · net +1672 · threat 64 · provinces 28 (+0) · ceiling 20734 · army 153990 · vassals Holland 94 · Kingdom of Italy 98 · Switzerland 88
  - NET income 2541 · trade 525 · admin 50 · tribute 712 · upkeep 1542 · charges 164 · contributions 31 · blockade 329 · admiralty 90
- DISPATCH: Sire — Mack has crossed into Franche-Comte. Lannes and Murat stand in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 24 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #11 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeCharles …
  - ⚔ Archduke Charles (lost 2566) vs Massena (lost 4335) — A narrow defeat for Massena, Sire. Better-prepared troops might have tipped the balance.
  - verbs: attack×1
- LEDGER treasury 5465 · net +1751 · threat 62 · provinces 28 (+0) · ceiling 28742 · army 149655 · vassals Holland 92 · Kingdom of Italy 98 · Switzerland 84
  - NET income 2542 · trade 587 · admin 50 · tribute 712 · upkeep 1422 · charges 260 · blockade 368 · admiralty 90
- DISPATCH: 2 satellites drifted — Holland and Switzerland.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 1
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #12 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Massena. Casualties: Archduke… · ArchdukeJohn marches from Tyrol into Bohemia unopposed! (153 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Bohemia unopposed! (153 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1812) vs Massena (lost 4925) — Massena was close. A period of drilling could have changed the outcome.
  - verbs: move×3, attack×2, unfortify×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7040 · net +1605 · threat 60 · provinces 28 (+0) · ceiling 21264 · army 144730 · vassals Holland 90 · Kingdom of Italy 98 · Switzerland 80
  - NET income 2554 · trade 587 · admin 50 · tribute 712 · upkeep 1272 · charges 568 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Russia` → ✗ Talleyrand advises patience, Sire. Russia refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeCha… · ArchdukeJohn marches from Bohemia into Carniola unopposed! (163 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Milan has been captured by Austria!
  - 🏴 Austria: ArchdukeJohn marches from Bohemia into Carniola unopposed! (163 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 990) vs Massena (lost 5932) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: move×3, attack×2
- LEDGER treasury 8279 · net +1333 · threat 58 · provinces 28 (+0) · ceiling 19277 · army 138697 · vassals Holland 88 · Kingdom of Italy 96 · Switzerland 87
  - NET income 2556 · trade 587 · admin 50 · tribute 487 · upkeep 1128 · charges 761 · blockade 368 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Bohemia into Hungary unopposed! (969 lost to march) Captured: Bavaria → Austria · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu…
  - 🏴 Austria: ArchdukeCharles marches from Bohemia into Hungary unopposed! (969 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1481) vs Deroy (lost 4233) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, fortify×1, move×1
- LEDGER treasury 9614 · net +1149 · threat 56 · provinces 28 (+0) · ceiling 18848 · army 138697 · vassals Holland 88 · Kingdom of Italy 96 · Switzerland 86
  - NET income 2558 · trade 587 · admin 50 · tribute 487 · upkeep 1128 · charges 947 · blockade 368 · admiralty 90
- DISPATCH: Sire — Hungary has been taken by Austria.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #15 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 10 actions, 5 attacks — Russia, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · Mack's forces press forward aggressively. Brutal stalemate between Mack and Bernadotte. Heavy casualties on both sides:… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCh… · Mack's forces strike with perfect coordination! Mack gains the advantage over Deroy. Casualties: Mack 51, Deroy 643. Bo…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Moravia. (422 lost to march — forward supply lines reduce losses) Moravia has been captured by Austria!
  - ⚔ Archduke Charles (lost 490) vs Deroy (lost 5680) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Mack (lost 2363) vs Bernadotte (lost 3057) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 55) vs Deroy (lost 1791) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Mack (lost 51) vs Deroy (lost 643) — Deroy's corps broke, Sire. They are streaming back from the field.
  - ⚔ Castanos (lost 620) vs Paget (lost 1714) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: attack×5, move×4, unfortify×1
- LEDGER treasury 10289 · net +672 · threat 54 · provinces 28 (+0) · ceiling 14506 · army 135640 · vassals Holland 88 · Kingdom of Italy 96 · Switzerland 85
  - NET income 2547 · trade 587 · admin 50 · tribute 487 · upkeep 1084 · charges 1319 · contributions 138 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Berry. No French corps stands in his path.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharle… · Mack struggles in a costly engagement. Brutal stalemate between Mack and Bernadotte. Heavy casualties on both sides: Ma…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Deroy is taken by Austria at Croatia!
  - ⚔ Archduke Charles (lost 30) vs Deroy (lost 504) — The line gave way. Deroy is falling back, and not in good order. And Deroy was taken on that field — Austria holds him.
  - ⚔ Mack (lost 1950) vs Bernadotte (lost 2456) — Stalemate. Bernadotte and Mack glare at each other across the field.
  - verbs: attack×2, move×2, recruit×1
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
  - RATIFIED Russia · PEACE · stalemate
- LEDGER treasury 10933 · net +614 · threat 47 · provinces 27 (-1) · ceiling 14683 · army 133184 · vassals Holland 88 · Kingdom of Italy 96 · Switzerland 84
  - NET income 2512 · trade 599 · admin 50 · tribute 487 · upkeep 1068 · charges 1461 · contributions 40 · blockade 375 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Normandy. No French corps stands in his path.
  - RAIL peace_ratified: Peace ratified between France and Russia.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
- DIPLO +6 medium/low (diplomatic_proposal_sent, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_treaty_signed, paymaster_subsidy)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #17 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Mack gains the advantage over Bernadotte. Casualties: Mack 1,547, Bernadotte 2,750. Bot… · ArchdukeJohn engages in solid combat. ArchdukeJohn gains the advantage over Bernadotte. Casualties: ArchdukeJohn's army…
  - ⚔ Mack (lost 1547) vs Bernadotte (lost 2750) — A narrow defeat for Bernadotte, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Archduke John (lost 387, own corps) vs Bernadotte (lost 2940) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: attack×2, unfortify×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11340 · net +545 · threat 45 · provinces 27 (+0) · ceiling 14511 · army 127379 · vassals Holland 84 · Kingdom of Italy 92 · Switzerland 79
  - NET income 2516 · trade 599 · admin 50 · tribute 487 · upkeep 1000 · charges 1602 · contributions 40 · blockade 375 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 2,750 men — lost in a single action.
  - RAIL settlement_offer_arrival: Britain's terms to settle France vs Britain, under Russia's good offices. Asking 3427 gold.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer, under Russia's good offices → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #19 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (6 pairs resolved). Status quo: Milan stays Austrian by the treaty. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 10524 · net +2579 · threat 22 · provinces 27 (+0) · ceiling 225416 · army 127379 · vassals Holland 82 · Kingdom of Italy 90 · Switzerland 78
  - NET income 2521 · trade 623 · admin 50 · tribute 487 · upkeep 1000 · charges 102
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria: Gold indemnity: 3427 gold from France to Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 1
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +5 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 45 to 22.

## Turn 12 — Early March 1806
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 12771 · net +2220 · threat 22 · provinces 27 (+0) · ceiling 197750 · army 127379 · vassals Holland 91 · Kingdom of Italy 88 · Switzerland 77
  - NET income 2526 · trade 623 · admin 50 · tribute 150 · upkeep 1000 · charges 129
- DISPATCH: KingdomOfItaly loyalty 88 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad ×3, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
  - MAILBOX #11 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #21 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 14842 · net +2271 · threat 22 · provinces 27 (+0) · ceiling 204083 · army 127379 · vassals Holland 90 · Kingdom of Italy 97 · Switzerland 76
  - NET income 2527 · trade 623 · admin 50 · tribute 225 · upkeep 1000 · charges 154
- DISPATCH: THE LAWS: Russia enacts the War Ministry under Arakcheev — +5 morale from every drill.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 17115 · net +2246 · threat 22 · provinces 27 (+0) · ceiling 204250 · army 127379 · vassals Holland 89 · Kingdom of Italy 96 · Switzerland 75
  - NET income 2529 · trade 623 · admin 50 · tribute 225 · upkeep 1000 · charges 181
- DISPATCH: Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: 18 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #22 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (75 → 85); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 19137 · net +1998 · threat 22 · provinces 27 (+0) · ceiling 185583 · army 127379 · vassals Holland 88 · Kingdom of Italy 95 · Switzerland 85
  - NET income 2530 · trade 623 · admin 50 · upkeep 1000 · charges 205
- DISPATCH: Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 10 courts rebuff Bavaria (open borders agreement)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21137 · net +1976 · threat 22 · provinces 27 (+0) · ceiling 185750 · army 127379 · vassals Holland 87 · Kingdom of Italy 94 · Switzerland 85
  - NET income 2532 · trade 623 · admin 50 · upkeep 1000 · charges 229
- DISPATCH: Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 23115 · net +1954 · threat 22 · provinces 27 (+0) · ceiling 185916 · army 127379 · vassals Holland 86 · Kingdom of Italy 93 · Switzerland 85
  - NET income 2534 · trade 623 · admin 50 · upkeep 1000 · charges 253
- DISPATCH: Sire, I believe Naples may be ready to discuss improved relations. The diplomatic winds favor us.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25070 · net +1932 · threat 22 · provinces 27 (+0) · ceiling 186000 · army 127379 · vassals Holland 85 · Kingdom of Italy 92 · Switzerland 85
  - NET income 2535 · trade 623 · admin 50 · upkeep 1000 · charges 276
- DISPATCH: THE LAWS: Austria enacts the New Infantry Regulations — +5 morale from every drill.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 27004 · net +2247 · threat 22 · provinces 27 (+0) · ceiling 214250 · army 127379 · vassals Holland 84 · Kingdom of Italy 91 · Switzerland 85
  - NET income 2537 · trade 623 · admin 50 · tribute 337 · upkeep 1000 · charges 300
- DISPATCH: THE LAWS: Russia enacts Arakcheev's Artillery — artillery levies cost 15% less (×0.85).
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 29252 · net +2371 · threat 20 · provinces 27 (+0) · ceiling 226833 · army 127379 · vassals Holland 83 · Kingdom of Italy 90 · Switzerland 85
  - NET income 2538 · trade 623 · admin 50 · tribute 487 · upkeep 1000 · charges 327
- DISPATCH: Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Bavaria (open borders agreement)

---
finished: **completed** · commands 31 · popups 32 · battles 20
