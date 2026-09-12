# Playtest digest — amb-jena

seed `jena` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles faces a difficult fight. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on both…
  - ⚔ Archduke Charles (lost 4284) vs Massena (lost 5552) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2503 · net +1961 · threat 72 · provinces 28
  - NET income 3400 · trade 350 · tribute 895 · upkeep 2450 · charges 19 · blockade 175 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Ottoman envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Portugal envoy has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #1 already answered this chain)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCh… · Mack faces a difficult fight. Mack gains the advantage over Bernadotte. Casualties: Mack 2,370, Bernadotte 5,286. Both … · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Casualties: ArchdukeCharles's army 1,275, Deroy 8,728. Both armies remain in the field. Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 2641) vs Deroy (lost 5778) — The margin was slim. Training and preparation would serve Deroy well.
  - ⚔ Mack (lost 2370) vs Bernadotte (lost 5286) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 890, own corps) vs Deroy (lost 8728) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today. And Deroy was taken on that field…
  - verbs: attack×4
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4373 · net +2035 · threat 70 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 901 · upkeep 2292 · charges 109 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,286 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - TURN EVENTS 1
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Britain and Russia rebuff Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Mack gains the advantage over Bernadotte. Casualties: Mack's army 1,253, Bernadotte 5,9… · ArchdukeJohn faces a difficult fight. Bernadotte holds the line. Casualties: ArchdukeJohn 6,397, Bernadotte's army 1,38…
  - 🏴 Austria: Casualties: Mack's army 1,253, Bernadotte 5,930. Both armies remain in the field. Franconia has been captured by Austria!
  - ⚔ Mack (lost 892, own corps) vs Bernadotte (lost 5930) — Bernadotte's army has been badly mauled. Mack proved the stronger force today.
  - ⚔ Archduke John (lost 6397) vs Bernadotte (lost 131) — Lannes and Massena arrived to reinforce Bernadotte! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×2, stance_change×2, grant_dotation×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6316 · net +2180 · threat 68 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 905 · upkeep 2022 · charges 238 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte, crowned last turn, has been hunted across the frontier by Mack.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A PapalStates envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #8 already answered this chain)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Brutal stalemate between Mack and Bernadotte. Heavy casualties on both sides: Mack 5,65…
  - ⚔ Mack (lost 5658) vs Bernadotte (lost 371) — Stalemate. Bernadotte and Mack glare at each other across the field.
  - verbs: attack×1, retreat×1, stance_change×1, move×1, grant_dotation×1
- LEDGER treasury 8446 · net +2184 · threat 66 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 910 · upkeep 1872 · charges 389 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte, crowned two turns ago, has been hunted across the frontier by Mack.
  - TURN EVENTS 4
  - LOG ai_ai_proposal_refused: 8 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected PapalStates's open borders agreement proposal

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Lannes. Heavy casualt…
  - ⚔ Archduke Charles (lost 5228) vs Lannes (lost 1259) — Neither Lannes nor Archduke Charles could claim the field. The armies remain locked.
  - verbs: attack×1
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 10543 · net +2137 · threat 64 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 914 · upkeep 1752 · charges 560 · blockade 175 · admiralty 90
- DISPATCH: Sire — Lannes and Massena stand 43,108 men at Munich, which feeds 37,500. 5,608 too many. 2,903 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large for the prov…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Ottoman envoy has arrived with a proposal.
  - TURN EVENTS 6
  - LOG ai_ai_proposal_refused: Spain rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Spain rebuffs 4 courts (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - MAILBOX #9 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #9 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #9 already answered this chain)
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 3 · Austria armistice losing · Portugal open borders · Denmark open borders
- LEDGER treasury 12680 · net +1990 · threat 62 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 919 · upkeep 1730 · charges 734 · blockade 175 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: A Austria envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Portugal envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Spain will not forgive Britain the loss of Aragon and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 6
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 14648 · net +1826 · threat 61 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 923 · upkeep 1722 · charges 910 · blockade 175 · admiralty 90
- DISPATCH: Sire — Asturias has been taken by Britain.
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 3
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 2 more — Britain is not forgiven
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Denmark's open borders agreement proposal

## Turn 8 — Early January 1806
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Lannes (40g/turn); Bernadotte (40g/turn); Massena (40g/turn). Th…
- ENVOYS WAITING 3 · Naples open borders · Britain settlement offer · PapalStates open borders
- LEDGER treasury 16468 · net +1504 · threat 60 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 928 · upkeep 1692 · charges 1087 · blockade 175 · admiralty 90 · rentes 180
- DISPATCH: Sire — Lannes and Massena have been 5 turns over what Munich can feed. 1,535 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too large for t…
  - RAIL diplomatic_ai_proposal: A Naples envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A PapalStates envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 6
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 9 — Late January 1806
  - LETTER Naples: Open Borders Agreement → decline
  - LETTER PapalStates: Open Borders Agreement → decline
  - MAILBOX #18 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #18 already answered this chain)
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, move×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Lannes: They settle into cold war.
  - POPUP diplomatic_dialogue: Prussia, open_borders #19 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 17929 · net +1347 · threat 60 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 932 · upkeep 1692 · charges 1248 · blockade 175 · admiralty 90 · rentes 180
- DISPATCH: Sire — Lannes and Massena have been 6 turns over what Munich can feed. 1,490 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too large for t…
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - TURN EVENTS 7
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 37% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Naples's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected PapalStates's open borders agreement proposal
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (open borders agreement)

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Lannes. Heavy casualt…
  - ⚔ Archduke Charles (lost 3193) vs Lannes (lost 899) — Bernadotte never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 2211, own corps) vs Archduke John (lost 1221) — Lannes reached the field beside Massena, Sire — it saved the line, no more.
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 19060 · net +1311 · threat 60 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 914 · upkeep 1512 · charges 1446 · blockade 175 · admiralty 90 · rentes 180
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 4

## Turn 11 — Late February 1806
  - MAILBOX #20 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #20 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #20 already answered this chain)
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. Brutal stalemate between ArchdukeCharles and Lannes. Heavy casualties on … · Mack delivers an effective strike. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 2,521… · ArchdukeCharles launches a decisive assault. Massena holds the line. Casualties: ArchdukeCharles 4,590, Massena's army …
  - ⚔ Archduke Charles (lost 2048, own corps) vs Lannes (lost 1050) — Lannes fought without Bernadotte's support. The roads, or the will, proved insufficient.
  - ⚔ Mack (lost 2521) vs Lannes (lost 1032) — Bernadotte never reached the guns. The battle was decided without them, Sire.
  - ⚔ Archduke Charles (lost 4590) vs Massena (lost 464) — Reinforcements from Murat bolstered Massena's position — though Bernadotte never arrived, Sire.
  - verbs: attack×3, recruit×2, fortify×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 3978, own corps) vs Archduke John (lost 471) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: Hesse, non_aggression #21 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 19735 · net +1223 · threat 58 · provinces 27 (-1)
  - NET income 3200 · trade 350 · tribute 919 · upkeep 1128 · charges 1723 · blockade 175 · admiralty 90 · rentes 180
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Corsica.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 8
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Lannes holds the line. Casualties: ArchdukeCharles 3,289, Lannes's army 1,… · Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 2,313, L… · ArchdukeCharles launches a decisive assault. Murat holds the line. Casualties: ArchdukeCharles 5,619, Murat's army 1,13… · Mack's forces advance steadily. Massena holds the line. Casualties: Mack 4,352, Massena's army 1,128. Both armies remai…
  - ⚔ Archduke Charles (lost 3289) vs Lannes (lost 449) — Bernadotte arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Mack (lost 2313) vs Lannes (lost 724) — Neither Lannes nor Mack could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 5619) vs Murat (lost 721) — A decisive victory for Murat! Archduke Charles was thoroughly outmatched.
  - ⚔ Mack (lost 4352) vs Massena (lost 348) — A decisive victory for Massena! Mack was thoroughly outmatched.
  - verbs: attack×4
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 20633 · net +1101 · threat 56 · provinces 27 (+0)
  - NET income 3200 · trade 350 · tribute 923 · upkeep 1040 · charges 1937 · blockade 175 · admiralty 90 · rentes 180
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - TURN EVENTS 5
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mac… · Mack engages in solid combat. Murat holds the line. Casualties: Mack 4,683, Murat 758. Both armies remain in the field.
  - ⚔ Mack (lost 965) vs Lannes (lost 1344) — The line gave way. Lannes is falling back, and not in good order.
  - ⚔ Mack (lost 4683) vs Murat (lost 758) — A decisive victory for Murat! Mack was thoroughly outmatched.
  - verbs: attack×2
- ORDER Lannes [awaiting_response]: Lannes is cornered at Munich with 4,348 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1748, own corps) vs Archduke John (lost 965) — Massena arrived in time to steady Murat's position. The field was held, nothing further.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Munich with 4,348 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_petition: shadow_command, Marshal Soult asks for a command → detach
  -     ↳ Soult straightens. "You will not regret it, Sire." March him to Lorraine and the front is his — the order is …
  - POPUP diplomatic_dialogue: incoming_settlement_offer #22 → reject_settlement_offer
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 21467 · net +1050 · threat 54 · provinces 27 (+0)
  - NET income 3200 · trade 350 · tribute 928 · upkeep 952 · charges 2141 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Sire — Massena, crowned three turns ago, has been beaten in the field.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 7
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. Massena holds the line. Casualties: ArchdukeCharles 2,870, Massena's army…
  - ⚔ Archduke Charles (lost 2870) vs Massena (lost 440) — An exemplary engagement by Massena. The outcome was never in doubt.
  - verbs: unfortify×1, attack×1, form_square×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 22408 · net +885 · threat 52 · provinces 27 (+0)
  - NET income 3200 · trade 350 · tribute 932 · upkeep 944 · charges 2318 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.
  - RAIL third_party_peace: THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes …
  - TURN EVENTS 4
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (open borders agreement)

## Turn 15 — Late April 1806
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: defend×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Russia, armistice_losing #23 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 23233 · net +728 · threat 50 · provinces 27 (+0)
  - NET income 3200 · trade 350 · tribute 937 · upkeep 944 · charges 2480 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Sire — Marshal Murat's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 5
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Prussia are rebuffed (open borders agreement)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: defend×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 23910 · net +595 · threat 50 · provinces 27 (+0)
  - NET income 3200 · trade 350 · tribute 937 · upkeep 928 · charges 2629 · blockade 175 · admiralty 90 · rentes 120
- DISPATCH: Sire — Marshal Murat's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - TURN EVENTS 2
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG third_party_peace: THE CONGRESS: Austria and Bavaria make peace without France

## Turn 17 — Late May 1806
  - MAILBOX #24 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #24 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #24 already answered this chain)
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks — Russia, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, stance_change×1, naval_expedition×1
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Murat (200g/turn); Bernadotte (80g/turn); Massena (240g/turn). T…
  - POPUP diplomatic_dialogue: Britain, armistice_losing #25 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression #26 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 2 · Britain armistice losing · Denmark non aggression
- LEDGER treasury 23414 · net -950 · threat 50 · provinces 27 (+0)
  - NET income 3184 · trade 350 · tribute 937 · upkeep 928 · charges 3314 · contributions 184 · blockade 175 · admiralty 90 · rentes 780
- DISPATCH: Sire — Flanders holds. Paget left 1,633 men before the works; 8,946 of ours are still under arms.
  - RAIL expedition_landed: THE LANDING: Paget has put 4,750 men ashore at Flanders.
  - RAIL diplomatic_ai_proposal: A Britain envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 4
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 4 actions, 4 attacks — Russia, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Flanders into Orleanais unopposed! (31 lost to march) Captured: France → Britain · Paget marches from Orleanais into Nivernais unopposed! (30 lost to march) Captured: France → Britain · Paget marches from Nivernais into Burgundy unopposed! (30 lost to march) Captured: France → Britain · Paget marches from Burgundy into Limousin unopposed! (30 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Flanders into Orleanais unopposed! (31 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Orleanais into Nivernais unopposed! (30 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Nivernais into Burgundy unopposed! (30 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Burgundy into Limousin unopposed! (30 lost to march) Captured: France → Britain
  - verbs: attack×4
- ENVOYS WAITING 2 · Hesse non aggression · Britain settlement offer
- LEDGER treasury 22876 · net -470 · threat 49 · provinces 23 (-4)
  - NET income 2838 · trade 350 · tribute 937 · upkeep 928 · charges 2672 · blockade 175 · admiralty 90 · rentes 780
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 2
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 34% of active European bloc power.

## Turn 19 — Late June 1806
  - MAILBOX #27 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #28 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #27 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #27 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 9 actions, 4 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Limousin into Berry unopposed! (29 lost to march) Captured: France → Britain · Paget marches from Berry into Gascony unopposed! (59 lost to march) Captured: France → Britain · Paget marches from Gascony into Guyenne unopposed! (29 lost to march) Captured: France → Britain · ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Murat. Heavy casualti…
  - 🏴 Britain: Paget marches from Limousin into Berry unopposed! (29 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Berry into Gascony unopposed! (59 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Gascony into Guyenne unopposed! (29 lost to march) Captured: France → Britain
  - ⚔ Archduke Charles (lost 3325) vs Murat (lost 1648) — Stalemate. Murat and Archduke Charles glare at each other across the field.
  - verbs: attack×4, unfortify×2, move×2, recruit×1
- LEDGER treasury 21082 · net -1392 · threat 48 · provinces 20 (-3)
  - NET income 2342 · trade 350 · tribute 937 · upkeep 920 · charges 3106 · blockade 175 · admiralty 90 · rentes 780
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - TURN EVENTS 4
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 9 actions, 6 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Guyenne into Anjou unopposed! (28 lost to march) Captured: France → Britain · Paget marches from Anjou into Maine unopposed! (28 lost to march) Captured: France → Britain · Paget marches from Maine into Brittany unopposed! (28 lost to march) Captured: France → Britain · ArchdukeCharles struggles in a costly engagement. Brutal stalemate between ArchdukeCharles and Murat. Heavy casualties …
  - 🏴 Britain: Paget marches from Guyenne into Anjou unopposed! (28 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Anjou into Maine unopposed! (28 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Maine into Brittany unopposed! (28 lost to march) Captured: France → Britain
  - ⚔ Archduke Charles (lost 2361) vs Murat (lost 2286) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke John (lost 1923) vs Murat (lost 934) — A decisive victory for Murat! Archduke John was thoroughly outmatched.
  - verbs: attack×6, recruit×2, move×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Ney and Murat: They settle into cold war.
- LEDGER treasury 19677 · net -1074 · threat 45 · provinces 17 (-3)
  - NET income 1996 · trade 350 · tribute 919 · upkeep 912 · charges 2432 · blockade 175 · admiralty 90 · rentes 780
- DISPATCH: Sire — Anjou has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - TURN EVENTS 9
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 4 actions, 4 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Normandy into Artois unopposed! (27 lost to march) Captured: France → Britain · Paget marches from Artois into Champagne unopposed! (27 lost to march) Captured: France → Britain · ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCharl… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeJohn loses 1,740 troops in the assau…
  - 🏴 Britain: Paget marches from Normandy into Artois unopposed! (27 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Artois into Champagne unopposed! (27 lost to march) Captured: France → Britain
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -87g, Kingdom of Italy -175g. Captured: KingdomOfItaly -> Austria
  - ⚔ Archduke Charles (lost 1240) vs Murat (lost 2823) — Even the favorable ground could not save Murat, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×4
- LEDGER treasury 17996 · net -1319 · threat 42 · provinces 15 (-2)
  - NET income 1800 · trade 350 · tribute 712 · upkeep 896 · charges 2290 · blockade 175 · admiralty 90 · rentes 780
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces…
  - TURN EVENTS 7
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 5 actions, 3 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Champagne into Ile-de-France unopposed! (27 lost to march) Captured: France → Britain · Paget marches from Ile-de-France into Picardy unopposed! (26 lost to march) Captured: France → Britain · ArchdukeJohn marches from Piedmont into Provence unopposed! (89 lost to march) Captured: France → Austria
  - 🏴 Britain: Paget marches from Champagne into Ile-de-France unopposed! (27 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Ile-de-France into Picardy unopposed! (26 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (89 lost to march) Captured: France → Austria
  - verbs: attack×3, unfortify×1, move×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: Russia, armistice_losing #29 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 15360 · net -2118 · threat 29 · provinces 12 (-3)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 924 · charges 2623 · blockade 188 · admiralty 90 · rentes 780
- DISPATCH: Sire — Ile-de-France has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - TURN EVENTS 6
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Provence into Lyonnais unopposed! (88 lost to march) Captured: France → Austria · ArchdukeJohn marches from Lyonnais into Savoy unopposed! (176 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Lyonnais unopposed! (88 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Savoy unopposed! (176 lost to march) Captured: France → Austria
  - verbs: attack×2, recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #30 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
- ENVOYS WAITING 2 · Prussia open borders · Britain settlement offer
- LEDGER treasury 12955 · net -1926 · threat 28 · provinces 10 (-2)
  - NET income 1300 · trade 375 · tribute 525 · upkeep 936 · charges 2182 · blockade 188 · admiralty 90 · rentes 780
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 50% of active European bloc power.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5104 gold.
  - TURN EVENTS 8
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, wait×1, recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #32 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 10991 · net -1573 · threat 27 · provinces 10 (+0)
  - NET income 1300 · trade 375 · tribute 487 · upkeep 936 · charges 1791 · blockade 188 · admiralty 90 · rentes 780
- DISPATCH: Sire — Gelderland has been taken by Britain.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 9
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 50% of active European bloc power.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Lyonnais into Languedoc unopposed! (29 lost to march) Captured: France → Britain
  - 🏴 Britain: Shrapnel marches from Lyonnais into Languedoc unopposed! (29 lost to march) Captured: France → Britain
  - verbs: attack×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 118, own corps) vs Paget (lost 2546) — Davout and Napoleon's timely arrival aided Ney. Soult, however, was conspicuously absent.
  - POPUP capture_choice[capture]: Brabant, Ney → secure
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 9092 · net -1468 · threat 31 · provinces 10 (+0)
  - NET income 1200 · trade 375 · tribute 487 · upkeep 872 · charges 1625 · occupation 25 · blockade 188 · admiralty 90 · rentes 780
- DISPATCH: Sire — Languedoc has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 4
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 26 — Early October 1806
  - MAILBOX #33 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #34 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression → (stale passthrough — #34 already answered this chain)
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 7675 · net -1092 · threat 30 · provinces 10 (+0)
  - NET income 1207 · trade 375 · tribute 487 · upkeep 836 · charges 1300 · occupation 17 · blockade 188 · admiralty 90 · rentes 780
- DISPATCH: Sire — Ney, Davout and Napoleon stand 54,220 men at Brabant, which feeds 22,500. 31,720 too many. 5,059 men lost in 2 turns. No depot may be laid at Brabant — rural regions don't support buildings (n…
  - RAIL diplomatic_ai_proposal: A Austria envoy has arrived with a proposal.
  - TURN EVENTS 4
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 27 — Late October 1806
  - MAILBOX #34 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #35 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (stale passthrough — #35 already answered this chain)
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 6391 · net -990 · threat 19 · provinces 10 (+0)
  - NET income 1208 · trade 375 · tribute 262 · upkeep 804 · charges 1006 · occupation 17 · blockade 188 · admiralty 90 · rentes 780
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_alliance_cascade: Bavaria enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Switzerland has rebelled against France. It is war.
  - TURN EVENTS 8
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.
  - LOG coalition_dissolved: Coalition against France has dissolved.
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy assaults the Bern garrison! Garrison: 10,000 -> 5,000 (-5,000). Deroy loses 3,472 troops. Garrison holds — 5,000 … · Deroy assaults the Bern garrison! Garrison collapses (5,000 -> 0). Deroy loses 1,929 troops in the assault. Deroy march…
  - 🏴 Bavaria: [Materiel] Guns, horses and stores lost with the fallen: Bavaria -96g, Switzerland -125g. Captured: Switzerland -> Bavaria
  - verbs: attack×2, move×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 5591 · net -641 · threat 18 · provinces 10 (+0)
  - NET income 1225 · trade 387 · tribute 262 · upkeep 776 · charges 715 · occupation 10 · blockade 194 · admiralty 90 · rentes 780
- DISPATCH: Sire — Switzerland is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Switzerland has been eliminated from the war.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 2556 gold.
  - TURN EVENTS 5

## Turn 29 — Late November 1806
  - MAILBOX #35 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #37 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #37 already answered this chain)
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Gascony into Bearn unopposed! (56 lost to march) Captured: France → Britain · Shrapnel marches from Bearn into Bordelais unopposed! (55 lost to march) Captured: France → Britain
  - 🏴 Britain: Shrapnel marches from Gascony into Bearn unopposed! (56 lost to march) Captured: France → Britain
  - 🏴 Britain: Shrapnel marches from Bearn into Bordelais unopposed! (55 lost to march) Captured: France → Britain
  - verbs: attack×2, wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 4746 · net -677 · threat 17 · provinces 8 (-2)
  - NET income 1025 · trade 387 · tribute 262 · upkeep 780 · charges 547 · occupation 10 · blockade 194 · admiralty 90 · rentes 780
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - TURN EVENTS 6
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG nation_eliminated: Switzerland has been eliminated from the war.

## Turn 30 — Early December 1806
  - MAILBOX #36 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #38 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (stale passthrough — #38 already answered this chain)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #39 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 4094 · net -522 · threat 18 · provinces 8 (+0)
  - NET income 1026 · trade 387 · tribute 262 · upkeep 756 · charges 417 · occupation 10 · blockade 194 · admiralty 90 · rentes 780
- DISPATCH: Sire — Ney, Davout and Napoleon have been 5 turns over what Brabant can feed. 5,746 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support buildi…
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - TURN EVENTS 6
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 action(s) unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Ney (40g/turn); Davout (40g/turn); Murat (240g/turn). The treasu…
  - POPUP diplomatic_dialogue: Denmark, non_aggression #40 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 3611 · net -566 · threat 17 · provinces 8 (+0)
  - NET income 1036 · trade 387 · tribute 262 · upkeep 732 · charges 320 · occupation 5 · blockade 194 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 6 turns over what Brabant can feed. 5,342 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support buildi…
  - RAIL balance_of_europe_shifted: British Interest leads the current largest alignment at 53% of active European bloc power.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 4
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 32 — Early January 1807
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 action(s) unused) Turn 33 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 3062 · net -440 · threat 16 · provinces 8 (+0)
  - NET income 1037 · trade 387 · tribute 262 · upkeep 716 · charges 211 · occupation 5 · blockade 194 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 7 turns over what Brabant can feed. 4,978 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support buildi…
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 6
  - LOG balance_of_europe_shifted: British Interest leads the current largest alignment at 53% of active European bloc power.

## Turn 33 — Late January 1807
  - MAILBOX #39 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #41 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression → (stale passthrough — #41 already answered this chain)
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 action(s) unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 2655 · net -326 · threat 15 · provinces 8 (+0)
  - NET income 1038 · trade 387 · tribute 262 · upkeep 684 · charges 130 · occupation 5 · blockade 194 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 8 turns over what Brabant can feed. 4,650 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support buildi…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 1224 gold.
  - TURN EVENTS 2
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 34 — Early February 1807
  - MAILBOX #40 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #42 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #42 already answered this chain)
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 action(s) unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 2331 · net -259 · threat 12 · provinces 8 (+0)
  - NET income 1039 · trade 349 · tribute 262 · upkeep 664 · charges 65 · occupation 5 · blockade 175 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 9 turns over what Brabant can feed. 4,354 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support buildi…
  - TURN EVENTS 3
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 action(s) unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 2097 · net -188 · threat 9 · provinces 8 (+0)
  - NET income 1040 · trade 349 · tribute 262 · upkeep 640 · charges 19 · occupation 5 · blockade 175 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 10 turns over what Brabant can feed. 4,086 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support build…
  - TURN EVENTS 1

## Turn 36 — Early March 1807
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 action(s) unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 1922 · net -156 · threat 6 · provinces 8 (+0)
  - NET income 1041 · trade 349 · tribute 262 · upkeep 628 · occupation 5 · blockade 175 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 11 turns over what Brabant can feed. 3,843 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support build…
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - TURN EVENTS 1

## Turn 37 — Late March 1807
  - MAILBOX #41 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #43 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (stale passthrough — #43 already answered this chain)
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 action(s) unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 1779 · net -143 · threat 5 · provinces 8 (+0)
  - NET income 1042 · trade 349 · tribute 262 · upkeep 616 · occupation 5 · blockade 175 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 12 turns over what Brabant can feed. 3,620 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support build…
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - TURN EVENTS 1
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 38 — Early April 1807
  - MAILBOX #42 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #44 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #44 already answered this chain)
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 action(s) unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Britain settlement offer
- LEDGER treasury 1653 · net -126 · threat 4 · provinces 8 (+0)
  - NET income 1043 · trade 349 · tribute 262 · upkeep 600 · occupation 5 · blockade 175 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 13 turns over what Brabant can feed. 3,417 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support build…
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 711 gold.
  - TURN EVENTS 1
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 39 — Late April 1807
  - MAILBOX #43 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - MAILBOX #44 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #45 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #46 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Denmark, non_aggression #45 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #46 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 action(s) unused) Turn 40 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 2 · Austria armistice losing · Hesse non aggression
- LEDGER treasury 1536 · net -117 · threat 3 · provinces 8 (+0)
  - NET income 1044 · trade 349 · tribute 262 · upkeep 592 · occupation 5 · blockade 175 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 14 turns over what Brabant can feed. 3,230 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support build…
  - RAIL diplomatic_ai_proposal: A Austria envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 1
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 40 — Early May 1807
  - MAILBOX #45 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #46 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #47 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #48 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #47 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #48 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 action(s) unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 1428 · net -108 · threat 4 · provinces 8 (+0)
  - NET income 1045 · trade 349 · tribute 262 · upkeep 584 · occupation 5 · blockade 175 · admiralty 90 · rentes 960
- DISPATCH: Sire — Ney, Davout and Napoleon have been 15 turns over what Brabant can feed. 3,059 men. The country will ask where the army went. No depot may be laid at Brabant — rural regions don't support build…
  - TURN EVENTS 1
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

---
finished: **completed** · commands 40 · popups 110 · battles 27
