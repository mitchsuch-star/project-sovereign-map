# Playtest digest — ambient

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on …
  - ⚔ Archduke Charles (lost 4875) vs Massena (lost 5379) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2512 · net +1961 · threat 68 · provinces 28 · ceiling 54105 · army 183621 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 3400 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · charges 19 · blockade 175 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 1
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #1 already answered this chain)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 action(s) unused) Turn 3 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles 2,… · Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,290, L… · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Casualties: ArchdukeCharles's army 1,318, Deroy 8,956. Both armies remain in the field. Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 2527) vs Deroy (lost 5698) — The battle unfolded without particular distinction.
  - ⚔ Mack (lost 5290) vs Lannes (lost 1524, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 917, own corps) vs Deroy (lost 8956) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×4, stance_change×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4384 · net +1994 · threat 66 · provinces 28 (+0) · ceiling 50518 · army 179386 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 3382 · trade 350 · admin 50 · tribute 901 · upkeep 2322 · charges 102 · blockade 175 · admiralty 90
- DISPATCH: Sire — Carniola has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archd… · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination) · Mack completes the encirclement from Swabia! (+2 coordination) · ArchdukeJohn delivers an effective strike. Bernadotte holds the line. Casualties: ArchdukeJohn 5,862, Bernadotte's army…
  - 🏴 Austria: Both armies remain in the field. Mack advances into Franconia. (1,332 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1263, own corps) vs Bernadotte (lost 6757) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke John (lost 88, own corps) vs Deroy (lost 3095) — Deroy's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Mack (lost 740, own corps) vs Bernadotte (lost 5637) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke John (lost 5862) vs Bernadotte (lost 111, own corps) — Lannes and Massena arrived to reinforce Bernadotte! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×4, wait×1, recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6179 · net +2338 · threat 64 · provinces 28 (+0) · ceiling 46212 · army 163130 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 91
  - NET income 3384 · trade 350 · admin 50 · tribute 905 · upkeep 1842 · charges 244 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte, crowned last turn, has been beaten in the field.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +5 medium/low (diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #8 already answered this chain)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 8 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Lannes. Heavy casualt… · Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,705, Lan… · ArchdukeCharles attacks with overwhelming force. Brutal stalemate between ArchdukeCharles and Bernadotte. Heavy casualt…
  - ⚔ Archduke Charles (lost 4441) vs Lannes (lost 1346, own corps) — Neither Lannes nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Mack (lost 5705) vs Lannes (lost 1216, own corps) — Neither Lannes nor Mack could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 2723) vs Bernadotte (lost 355, own corps) — Stalemate. Bernadotte and Archduke Charles glare at each other across the field.
  - verbs: attack×3, stance_change×2, grant_dotation×1, retreat×1, wait×1
- LEDGER treasury 8351 · net +2586 · threat 62 · provinces 28 (+0) · ceiling 46367 · army 149370 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 89
  - NET income 3386 · trade 350 · admin 50 · tribute 910 · upkeep 1414 · charges 431 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte, crowned two turns ago, has been hunted across the frontier by Archduke Charles.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 5 approaches from Austria, Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected PapalStates's open borders agreement proposal

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack struggles in a costly engagement. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 3…
  - ⚔ Mack (lost 3323) vs Lannes (lost 1012, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: retreat×1, attack×1, stance_change×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 2123, own corps) vs Archduke Charles (lost 3690) — The terrain heavily favored Archduke Charles. Murat's men paid the price.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #9 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Switzerland client petition
- LEDGER treasury 10721 · net +2614 · threat 60 · provinces 28 (+0) · ceiling 44053 · army 139610 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 85
  - NET income 3388 · trade 350 · admin 50 · tribute 914 · upkeep 1140 · charges 683 · blockade 175 · admiralty 90
- DISPATCH: Bernadotte's army is recovering. Effectiveness penalty: -15%.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — A Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → refuse the petition
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (85 → 75); standing 0 → -20 (-1 loyalty a turn). Nothing is charged. → display-only
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #12 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression #13 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 2 · Austria armistice losing · Denmark non aggression
- LEDGER treasury 13321 · net +2388 · threat 58 · provinces 28 (+0) · ceiling 42575 · army 139190 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 72
  - NET income 3389 · trade 350 · admin 50 · tribute 919 · upkeep 1132 · charges 923 · blockade 175 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Spain will not forgive Britain the loss of Aragon and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Bavaria (open borders agreement)

## Turn 7 — Late December 1805
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: Hesse, non_aggression #14 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 15679 · net +2159 · threat 58 · provinces 28 (+0) · ceiling 41127 · army 139190 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 69
  - NET income 3392 · trade 350 · admin 50 · tribute 923 · upkeep 1132 · charges 1159 · blockade 175 · admiralty 90
- DISPATCH: Sire — Asturias has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 2 more — Britain is not forgiven

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCh…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Tyrol. (1,394 lost to march) Tyrol has been captured by Austria!
  - 🏴 Austria: ArchdukeJohn moves from Bohemia to Franconia. Franconia falls to Austria!
  - ⚔ Archduke Charles (lost 1202) vs Deroy (lost 3250) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: unfortify×2, attack×1, move×1, wait×1, recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → reject_settlement_offer
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 17821 · net +1953 · threat 58 · provinces 28 (+0) · ceiling 40011 · army 138574 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 66
  - NET income 3394 · trade 350 · admin 50 · tribute 928 · upkeep 1112 · charges 1392 · blockade 175 · admiralty 90
- DISPATCH: Sire — Tyrol has been taken by Austria.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Massena. Casualties: Arch…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Franconia. (345 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1244) vs Massena (lost 3532) — Massena's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 2034, own corps) vs Archduke John (lost 993, own corps) — Lannes reached the field beside Massena, Sire — it saved the line, no more.
  - POPUP capture_choice[capture]: Franconia, Massena → secure
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 19446 · net +1761 · threat 60 · provinces 28 (+0) · ceiling 37781 · army 131335 · vassals Holland 93 · Kingdom of Italy 93 · Switzerland 61
  - NET income 3396 · trade 350 · admin 50 · tribute 932 · upkeep 1028 · charges 1674 · blockade 175 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #16 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #17 → reject
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Lannes (40g/turn); Bernadotte (40g/turn); Massena (40g/turn). Th…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #17 already answered this chain)
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 7 actions, 3 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Asturias into Leon unopposed! (47 lost to march) Captured: Spain → Britain · Castanos engages in solid combat. Castanos gains the advantage over Paget. Casualties: Castanos 790, Paget 1,299. Both … · Castanos holds them at Leon while allies attack from Galicia! (+1 coordination)
  - 🏴 Britain: Paget marches from Asturias into Leon unopposed! (47 lost to march) Captured: Spain → Britain
  - ⚔ Castanos (lost 790) vs Paget (lost 1299) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - ⚔ Castanos (lost 438) vs Paget (lost 1383) — Paget's aggressive posture left the troops exposed when Castanos's attack came.
  - verbs: attack×3, unfortify×1, grant_pension×1, wait×1, recruit×1
- LEDGER treasury 20982 · net +1383 · threat 60 · provinces 28 (+0) · ceiling 34923 · army 130874 · vassals Holland 93 · Kingdom of Italy 93 · Switzerland 58
  - NET income 3398 · trade 350 · admin 50 · tribute 937 · upkeep 1024 · charges 1883 · blockade 175 · admiralty 90 · rentes 180
- DISPATCH: Sire — Leon has been taken by Britain.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Castanos marches from Leon into Leon unopposed! (110 lost to march) Captured: Britain → Spain · Castanos faces a difficult fight. Castanos gains the advantage over Paget. Casualties: Castanos 81, Paget 809. Both arm…
  - 🏴 Spain: Castanos marches from Leon into Leon unopposed! (110 lost to march) Captured: Britain → Spain
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Castanos advances into Asturias. (108 lost to march) Asturias has been captured by Spain!
  - ⚔ Castanos (lost 81) vs Paget (lost 809) — Paget's corps broke, Sire. They are streaming back from the field. And Paget was taken on that field — Spain holds him.
  - verbs: attack×2, fortify×1
- LEDGER treasury 22307 · net +1189 · threat 58 · provinces 28 (+0) · ceiling 33914 · army 130874 · vassals Holland 93 · Kingdom of Italy 93 · Switzerland 55
  - NET income 3400 · trade 350 · admin 50 · tribute 937 · upkeep 1024 · charges 2079 · blockade 175 · admiralty 90 · rentes 180
- DISPATCH: Massena's army has fully recovered and is combat ready.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 13 approaches from Naples, Denmark and Bavaria are rebuffed (open borders agreement)

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Mack marches from Bohemia into Franconia unopposed! (581 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Mack marches from Bohemia into Franconia unopposed! (581 lost to march) Captured: Bavaria → Austria
  - verbs: unfortify×2, attack×1, move×1, grant_pension×1
- LEDGER treasury 23431 · net +1005 · threat 56 · provinces 28 (+0) · ceiling 32946 · army 130874 · vassals Holland 93 · Kingdom of Italy 93 · Switzerland 52
  - NET income 3400 · trade 350 · admin 50 · tribute 937 · upkeep 1024 · charges 2263 · blockade 175 · admiralty 90 · rentes 180
- DISPATCH: Sire — Franconia has been taken by Austria.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeChar… · ArchdukeCharles's forces strike with perfect coordination! ArchdukeCharles gains the advantage over Bernadotte. Casualt…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Munich. (944 lost to march) Munich has been captured by Austria!
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Franche-Comte!
  - ⚔ Archduke Charles (lost 1282) vs Lannes (lost 1368, own corps) — Murat and Bernadotte never reached the guns. The battle was decided without them, Sire.
  - ⚔ Archduke Charles (lost 127) vs Bernadotte (lost 1829) — Bernadotte stood alone, Sire. Soult never came. And Bernadotte was taken on that field — Austria holds him.
  - verbs: attack×2
- ENVOYS WAITING 2 · Denmark non aggression · Britain settlement offer
- LEDGER treasury 22774 · net -314 · threat 54 · provinces 28 (+0) · ceiling 20960 · army 122370 · vassals Holland 89 · Kingdom of Italy 89 · Switzerland 45
  - NET income 3392 · trade 350 · admin 50 · tribute 937 · upkeep 968 · charges 3598 · contributions 92 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)

## Turn 14 — Early April 1806
  - MAILBOX #17 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - MAILBOX #18 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #18 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #19 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Denmark, non_aggression #18 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #19 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy's attack meets fierce resistance. Deroy gains the advantage over ArchdukeJohn. Casualties: Deroy 374, ArchdukeJoh… · Deroy marches from Bohemia into Carniola unopposed! (115 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: FORCED RETREAT! Deroy advances into Bohemia. (297 lost to march) Bohemia has been captured by Bavaria!
  - 🏴 Bavaria: Deroy marches from Bohemia into Carniola unopposed! (115 lost to march) Captured: Austria → Bavaria
  - ⚔ Deroy (lost 374) vs Archduke John (lost 2668) — Not one corps reached Archduke John. Mack was expected; Archduke John fought the battle single-handed.
  - verbs: attack×2, retreat×1, stance_change×1, move×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 23111 · net +288 · threat 52 · provinces 28 (+0) · ceiling 25073 · army 121708 · vassals Holland 89 · Kingdom of Italy 89 · Switzerland 37
  - NET income 3394 · trade 350 · admin 50 · tribute 937 · upkeep 968 · charges 3090 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Sire — Austria and Bavaria have made peace without us.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes …
  - TURN EVENTS 5
- COURTS: The court of Bavaria eases over Revanche — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 16 courts rebuff Bavaria (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 15 — Late April 1806
  - MAILBOX #19 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #20 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression → (stale passthrough — #20 already answered this chain)
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, wait×1, grant_dotation×1
- ENVOYS WAITING 2 · Britain armistice losing · Russia armistice losing
- LEDGER treasury 23758 · net +569 · threat 40 · provinces 28 (+0) · ceiling 28513 · army 121058 · vassals Holland 89 · Kingdom of Italy 89
  - NET income 3396 · trade 350 · admin 50 · tribute 712 · upkeep 952 · charges 2602 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Sire — Switzerland is no longer ours. Britain is their protector now.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_vassal_transferred: Switzerland passes from France's suzerainty to Britain's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Britain's gold turns Switzerland against France.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG ai_ai_proposal_refused: Austria and Switzerland rebuff Bavaria (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 16 — Early May 1806
  - MAILBOX #20 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #21 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #21 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Russia. Your earlier answer was not delivered; the mat…
  - POPUP diplomatic_dialogue: incoming_proposal #22 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Britain, armistice_losing #21 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #22 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 24260 · net +440 · threat 40 · provinces 28 (+0) · ceiling 27838 · army 120422 · vassals Holland 89 · Kingdom of Italy 89
  - NET income 3398 · trade 350 · admin 50 · tribute 712 · upkeep 952 · charges 2733 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 636 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal
  - LOG third_party_peace: THE CONGRESS: Austria and Bavaria make peace without France

## Turn 17 — Late May 1806
  - MAILBOX #22 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #23 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #23 already answered this chain)
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 23771 · net -413 · threat 40 · provinces 27 (-1) · ceiling 21121 · army 119798 · vassals Holland 89 · Kingdom of Italy 89
  - NET income 3200 · trade 350 · admin 50 · tribute 712 · upkeep 944 · charges 3396 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Corsica.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 200g reaches Russia

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 23950 · net +156 · threat 40 · provinces 27 (+0) · ceiling 25150 · army 119186 · vassals Holland 89 · Kingdom of Italy 89
  - NET income 3200 · trade 350 · admin 50 · tribute 712 · upkeep 936 · charges 2835 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 612 men, at Franche-Comte.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5755 gold.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 19 — Late June 1806
  - MAILBOX #23 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #24 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #24 already answered this chain)
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 23672 · net -241 · threat 30 · provinces 27 (+0) · ceiling 21848 · army 118586 · vassals Holland 89
  - NET income 3200 · trade 375 · admin 50 · tribute 337 · upkeep 936 · charges 2869 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 20 — Early July 1806
  - MAILBOX #24 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #25 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (stale passthrough — #25 already answered this chain)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Provence unopposed! (297 lost to march) Captured: France → Austria · ArchdukeCharles marches from Provence into Lyonnais unopposed! (281 lost to march) Captured: France → Austria · ArchdukeCharles marches from Lyonnais into Limousin unopposed! (265 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (297 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Provence into Lyonnais unopposed! (281 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Limousin unopposed! (265 lost to march) Captured: France → Austria
  - verbs: attack×3, wait×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 22262 · net -1177 · threat 29 · provinces 24 (-3) · ceiling 15152 · army 117999 · vassals Holland 89
  - NET income 2750 · trade 375 · admin 50 · tribute 337 · upkeep 936 · charges 3355 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 1
- COURTS: The court of Austria eases over Revanche — service to the strong is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 21 — Late July 1806
  - MAILBOX #25 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #26 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #26 already answered this chain)
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 7 actions, 5 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Piedmont into Savoy unopposed! (98 lost to march) Captured: France → Britain · Paget marches from Burgundy into Orleanais unopposed! (47 lost to march) Captured: France → Britain · ArchdukeCharles marches from Limousin into Berry unopposed! (251 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,333 troops.…
  - 🏴 Britain: Paget marches from Piedmont into Savoy unopposed! (98 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Savoy to Burgundy. Burgundy falls to Britain!
  - 🏴 Britain: Paget marches from Burgundy into Orleanais unopposed! (47 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeCharles marches from Limousin into Berry unopposed! (251 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -92g, France -150g. Captured: France -> Austria
  - verbs: attack×5, move×1, wait×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 19999 · net -1496 · threat 28 · provinces 19 (-5) · ceiling 11439 · army 117424 · vassals Holland 89
  - NET income 2250 · trade 375 · admin 50 · tribute 337 · upkeep 964 · charges 3146 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Savoy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 22 — Early August 1806
  - MAILBOX #26 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #27 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression → (stale passthrough — #27 already answered this chain)
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Normandy into Artois unopposed! (153 lost to march) Captured: France → Austria · ArchdukeCharles marches from Artois into Champagne unopposed! (152 lost to march) Captured: France → Austria · ArchdukeCharles marches from Champagne into Ile-de-France unopposed! (150 lost to march) Captured: France → Austria · ArchdukeCharles marches from Ile-de-France into Picardy unopposed! (149 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Normandy into Artois unopposed! (153 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Artois into Champagne unopposed! (152 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Champagne into Ile-de-France unopposed! (150 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Ile-de-France into Picardy unopposed! (149 lost to march) Captured: France → Austria
  - verbs: attack×4, wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 18060 · net -1596 · threat 27 · provinces 15 (-4) · ceiling 9030 · army 116860 · vassals Holland 89
  - NET income 1950 · trade 375 · admin 50 · tribute 262 · upkeep 996 · charges 2839 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces…
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 23 — Late August 1806
  - MAILBOX #27 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #28 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (stale passthrough — #28 already answered this chain)
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Orleanais into Ardennes unopposed! (45 lost to march) Captured: France → Britain · Moore marches from Normandy into Maine unopposed! (859 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Orleanais into Ardennes unopposed! (45 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Normandy into Maine unopposed! (859 lost to march) Captured: France → Britain
  - verbs: attack×2, wait×1
- ENVOYS WAITING 3 · Austria peace · Britain settlement offer · Prussia open borders
- LEDGER treasury 15977 · net -1673 · threat 28 · provinces 13 (-2) · ceiling 7472 · army 116307 · vassals Holland 89
  - NET income 1800 · trade 375 · admin 50 · tribute 262 · upkeep 1012 · charges 2750 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Ardennes has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 7149 gold.
  - TURN EVENTS 1
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 24 — Early September 1806
  - MAILBOX #28 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #30 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #29 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Austria, peace #29 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #30 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Austria, peace #29 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: Prussia, open_borders #30 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Maine into Anjou unopposed! (785 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Maine into Anjou unopposed! (785 lost to march) Captured: France → Britain
  - verbs: attack×1, wait×1
- LEDGER treasury 14154 · net -1464 · threat 29 · provinces 12 (-1) · ceiling 6710 · army 115766 · vassals Holland 89
  - NET income 1650 · trade 375 · admin 50 · tribute 262 · upkeep 1012 · charges 2391 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Anjou has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Anjou into Guyenne unopposed! (720 lost to march) Captured: France → Britain · Moore marches from Guyenne into Gascony unopposed! (1,325 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Anjou into Guyenne unopposed! (720 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Guyenne into Gascony unopposed! (1,325 lost to march) Captured: France → Britain
  - verbs: attack×2, wait×1
- LEDGER treasury 11813 · net -1810 · threat 30 · provinces 10 (-2) · ceiling 3829 · army 115235 · vassals Holland 89
  - NET income 1350 · trade 375 · admin 50 · tribute 262 · upkeep 1024 · charges 2225 · contributions 200 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Guyenne has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL balance_of_europe_shifted: British Interest leads the current largest alignment at 51% of active European bloc power.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 4 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Gascony into Bearn unopposed! (1,123 lost to march) Captured: France → Britain · Moore marches from Bearn into Bordelais unopposed! (963 lost to march) Captured: France → Britain · ArchdukeCharles assaults the Flanders garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,543 troops in …
  - 🏴 Britain: Moore marches from Gascony into Bearn unopposed! (1,123 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Bearn into Bordelais unopposed! (963 lost to march) Captured: France → Britain
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, France -150g. Captured: France -> Austria
  - verbs: attack×3, wait×1
- LEDGER treasury 9663 · net -1357 · threat 31 · provinces 7 (-3) · ceiling 2927 · army 114715 · vassals Holland 89
  - NET income 950 · trade 375 · admin 50 · tribute 262 · upkeep 1052 · charges 1544 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG balance_of_europe_shifted: British Interest leads the current largest alignment at 51% of active European bloc power.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 8048 · net -1290 · threat 30 · provinces 7 (+0) · army 114205 · vassals Holland 89
  - NET income 950 · trade 375 · admin 50 · upkeep 1048 · charges 1219 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Friesland has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_ai_proposal_refused: 10 courts rebuff Bavaria (open borders agreement)

## Turn 28 — Early November 1806
  - MAILBOX #31 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #32 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #32 already answered this chain)
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Gascony into Languedoc unopposed! (214 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Gascony into Languedoc unopposed! (214 lost to march) Captured: France → Britain
  - verbs: attack×1, wait×1
- ENVOYS WAITING 2 · Hesse non aggression · Britain settlement offer
- LEDGER treasury 6654 · net -1113 · threat 27 · provinces 6 (-1) · army 113705 · vassals Holland 89
  - NET income 850 · trade 375 · admin 50 · upkeep 1052 · charges 938 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Languedoc has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3219 gold.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: 6 courts rebuff Bavaria (open borders agreement)

## Turn 29 — Late November 1806
  - MAILBOX #32 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #33 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #33 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #34 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #33 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #34 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 5557 · net -876 · threat 24 · provinces 6 (+0) · army 113215 · vassals Holland 89
  - NET income 850 · trade 375 · admin 50 · upkeep 1036 · charges 717 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 490 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Bavaria against Austria (400g/turn)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 30 — Early December 1806
  - MAILBOX #34 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #35 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (stale passthrough — #35 already answered this chain)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 4906 · net -519 · threat 23 · provinces 6 (+0) · ceiling 2327 · army 112735 · vassals Holland 89
  - NET income 850 · trade 375 · admin 50 · tribute 225 · upkeep 1036 · charges 585 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 480 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 1
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 31 — Late December 1806
  - MAILBOX #35 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #36 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #36 already answered this chain)
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 action(s) unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Austria: ArchdukeCharles moves from Burgundy to Nivernais. Nivernais falls to Austria!
  - verbs: move×1, wait×1
- LEDGER treasury 4317 · net -471 · threat 22 · provinces 5 (-1) · army 112265 · vassals Holland 89
  - NET income 800 · trade 375 · admin 50 · tribute 225 · upkeep 1056 · charges 467 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Sire — Nivernais has fallen. Enemy colours fly over French homeland soil. ArchdukeCharles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 32 — Early January 1807
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 action(s) unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 3846 · net -376 · threat 21 · provinces 5 (+0) · army 111805 · vassals Holland 89
  - NET income 800 · trade 375 · admin 50 · tribute 225 · upkeep 1056 · charges 372 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 460 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 action(s) unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 3486 · net -287 · threat 20 · provinces 5 (+0) · ceiling 2059 · army 111354 · vassals Holland 89
  - NET income 800 · trade 375 · admin 50 · tribute 225 · upkeep 1040 · charges 299 · blockade 188 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 451 men, at Franche-Comte.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 1538 gold.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 34 — Early February 1807
  - MAILBOX #36 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #37 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #37 already answered this chain)
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 action(s) unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 3180 · net -244 · threat 17 · provinces 5 (+0) · army 110911 · vassals Holland 89
  - NET income 800 · trade 337 · admin 50 · tribute 225 · upkeep 1040 · charges 237 · blockade 169 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 443 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy, diplomatic_coalition_dissolved)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria, Britain and Russia remain at war with us.
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 35 — Late February 1807
  - MAILBOX #37 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #38 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #38 already answered this chain)
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 action(s) unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 2960 · net -176 · threat 14 · provinces 5 (+0) · ceiling 2084 · army 110477 · vassals Holland 89
  - NET income 800 · trade 337 · admin 50 · tribute 225 · upkeep 1016 · charges 193 · blockade 169 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 434 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 36 — Early March 1807
  - MAILBOX #38 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #39 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression → (stale passthrough — #39 already answered this chain)
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 action(s) unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 2784 · net -141 · threat 11 · provinces 5 (+0) · ceiling 2084 · army 110052 · vassals Holland 89
  - NET income 800 · trade 337 · admin 50 · tribute 225 · upkeep 1016 · charges 158 · blockade 169 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 425 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 37 — Late March 1807
  - MAILBOX #39 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #40 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (stale passthrough — #40 already answered this chain)
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 action(s) unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 2651 · net -106 · threat 10 · provinces 5 (+0) · ceiling 2124 · army 109635 · vassals Holland 89
  - NET income 800 · trade 337 · admin 50 · tribute 225 · upkeep 1008 · charges 131 · blockade 169 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 417 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 38 — Early April 1807
  - MAILBOX #40 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #41 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #41 already answered this chain)
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 action(s) unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 2553 · net -78 · threat 9 · provinces 5 (+0) · ceiling 2163 · army 109228 · vassals Holland 89
  - NET income 800 · trade 337 · admin 50 · tribute 225 · upkeep 1000 · charges 111 · blockade 169 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 407 men, at Franche-Comte.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 1060 gold.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 39 — Late April 1807
  - MAILBOX #41 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #42 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #42 already answered this chain)
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 action(s) unused) Turn 40 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Soult
  - verbs: attack×1, wait×1
- LEDGER treasury 2499 · net -43 · threat 8 · provinces 5 (+0) · ceiling 2281 · army 107495 · vassals Holland 89
  - NET income 800 · trade 337 · admin 50 · tribute 225 · upkeep 976 · charges 100 · blockade 169 · admiralty 90 · rentes 120
- DISPATCH: Supply cost you 400 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Bavaria lapses

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 action(s) unused) Turn 41 begins!
- enemy phase: 7 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Soult · BOMBARDMENT: Shrapnel → Napoleon · ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeChar…
  - ⚔ Archduke Charles (lost 1347) vs Lannes (lost 514, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Soult never arrived, Sire.
  - verbs: attack×3, move×2, unfortify×1, wait×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franche-Comte with 3,127 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franche-Comte with 3,127 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Britain peace
- LEDGER treasury 2264 · net +67 · threat 7 · provinces 5 (+0) · ceiling 2547 · army 97169 · vassals Holland 87
  - NET income 792 · trade 337 · admin 50 · tribute 225 · upkeep 864 · charges 62 · contributions 92 · blockade 169 · admiralty 90 · rentes 60
- DISPATCH: Sire — Massena's corps has been broken at Franche-Comte. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Bavaria against Austria (400g/turn)

---
finished: **completed** · commands 40 · popups 103 · battles 23
