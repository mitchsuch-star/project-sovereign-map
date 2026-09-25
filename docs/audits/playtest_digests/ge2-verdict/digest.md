# Playtest digest — ge2-verdict

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `da91683b56dc` (dirty) · content `4fdb803f0fdd` · driver `296621f2139c`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeC…
  - ⚔ Archduke Charles (lost 1643) vs Bernadotte (lost 7799) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2493 · net +2062 · threat 67 · provinces 28 · ceiling 51571 · army 181109 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 3400 · trade 350 · admin 50 · tribute 937 · upkeep 2390 · charges 20 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Franconia into Franconia unopposed! (1,517 lost to march) Captured: Bavaria → Austria · Mack's forces advance steadily. Mack gains the advantage over Deroy. Casualties: Mack 2,583, Deroy 6,440. Both armies r… · ArchdukeCharles flanks from Franconia while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles marches from Franconia into Franconia unopposed! (1,517 lost to march) Captured: Bavaria → Austria
  - ⚔ Mack (lost 2583) vs Deroy (lost 6440) — Even the favorable ground could not save Deroy, Sire. Mack overcame the terrain.
  - ⚔ Archduke Charles (lost 1152) vs Deroy (lost 8650) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×3, retreat×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4599 · net +2011 · threat 65 · provinces 28 (+0) · ceiling 49079 · army 180158 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3400 · trade 350 · admin 50 · tribute 937 · upkeep 2344 · charges 117 · blockade 175 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 22 approaches from Bavaria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, retreat×1, stance_change×1
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6624 · net +1927 · threat 63 · provinces 28 (+0) · ceiling 46421 · army 179375 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 92
  - NET income 3400 · trade 350 · admin 50 · tribute 937 · upkeep 2322 · charges 223 · blockade 175 · admiralty 90
- DISPATCH: Bernadotte's army has fully recovered and is combat ready.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia and Naples (open borders agreement)
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 8574 · net +1849 · threat 61 · provinces 28 (+0) · ceiling 44403 · army 178608 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3400 · trade 350 · admin 50 · tribute 937 · upkeep 2284 · charges 339 · blockade 175 · admiralty 90
- DISPATCH: Supply cost you 767 men, at Franche-Comte.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected PapalStates's open borders agreement proposal

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Bernadotte. Heavy casualties … · ArchdukeJohn engages in solid combat. Massena holds the line. Casualties: ArchdukeJohn's army 6,316, Massena 3,367. Bot…
  - 🏴 Austria: Bernadotte retreats! ArchdukeCharles pursues into Munich. (2,252 lost to march) Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 4637) vs Bernadotte (lost 552, own corps) — Lannes and Massena reached the field beside Bernadotte, Sire — it saved the line, no more.
  - ⚔ Archduke John (lost 2284, own corps) vs Massena (lost 3367) — The engagement proceeded as one might expect, Sire.
  - verbs: attack×2, move×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Switzerland client petition
- LEDGER treasury 10154 · net +1842 · threat 59 · provinces 28 (+0) · ceiling 41472 · army 170152 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 89
  - NET income 3400 · trade 237 · admin 50 · tribute 895 · upkeep 2052 · charges 479 · blockade 119 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Spain rebuffs 4 courts (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - MAILBOX #9 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #9 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #11 → refuse the petition
  - POPUP diplomatic_dialogue: Prussia, open_borders #9 → reject
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (89 → 79); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → refuse the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn faces a difficult fight. Massena holds the line. Casualties: ArchdukeJohn 5,768, Massena 1,258. Both armie… · Mack's attack meets fierce resistance. Massena holds the line. Casualties: Mack 5,079, Massena 3,103. Both armies remai…
  - ⚔ Archduke John (lost 5768) vs Massena (lost 1258) — An exemplary engagement by Massena. The outcome was never in doubt.
  - ⚔ Mack (lost 5079) vs Massena (lost 3103) — The battle unfolded without particular distinction.
  - verbs: attack×2, form_square×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #12 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression #13 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 2 · Austria armistice losing · Denmark non aggression
- LEDGER treasury 11861 · net +1800 · threat 57 · provinces 28 (+0) · ceiling 39810 · army 164911 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 78
  - NET income 3400 · trade 237 · admin 50 · tribute 829 · upkeep 1872 · charges 635 · blockade 119 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Spain will not forgive Britain the loss of Aragon and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 7 — Late December 1805
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Hesse, non_aggression #14 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 13650 · net +1668 · threat 57 · provinces 28 (+0) · ceiling 38316 · army 164048 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 75
  - NET income 3400 · trade 237 · admin 50 · tribute 833 · upkeep 1856 · charges 787 · blockade 119 · admiralty 90
- DISPATCH: Bernadotte's army has fully recovered and is combat ready.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 1 more — Britain is not forgiven

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → reject_settlement_offer
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 15308 · net +1540 · threat 57 · provinces 28 (+0) · ceiling 37056 · army 163202 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 72
  - NET income 3400 · trade 237 · admin 50 · tribute 838 · upkeep 1834 · charges 942 · blockade 119 · admiralty 90
- DISPATCH: Sire — Galicia has been taken by Britain.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 16840 · net +1418 · threat 57 · provinces 28 (+0) · ceiling 36000 · army 162372 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 69
  - NET income 3400 · trade 237 · admin 50 · tribute 842 · upkeep 1804 · charges 1098 · blockade 119 · admiralty 90
- DISPATCH: Sire — Asturias has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 10 — Early February 1806
  - MAILBOX #16 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #16 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack launches a decisive assault. Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack 3,859… · ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on … · Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 691, Paget … · Castanos holds them at Asturias while allies attack from Galicia! (+1 coordination)
  - ⚔ Mack (lost 3859) vs Massena (lost 3434) — Neither Massena nor Mack could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 2388) vs Massena (lost 3171) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Castanos (lost 691) vs Paget (lost 1259) — Paget was close. A period of drilling could have changed the outcome.
  - ⚔ Castanos (lost 461) vs Paget (lost 1117) — The toll on Paget's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4
- LEDGER treasury 18066 · net +1429 · threat 57 · provinces 28 (+0) · ceiling 35750 · army 154954 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 66
  - NET income 3400 · trade 237 · admin 50 · tribute 829 · upkeep 1580 · charges 1298 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 813 men, at Franche-Comte.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on bo… · Mack's attack meets fierce resistance. Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack … · Castanos marches from Asturias into Asturias unopposed! (111 lost to march) Captured: Britain → Spain · Castanos's attack meets fierce resistance. Castanos gains the advantage over Paget. Casualties: Castanos 129, Paget 1,0…
  - 🏴 Spain: Castanos marches from Asturias into Asturias unopposed! (111 lost to march) Captured: Britain → Spain
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Galicia!
  - ⚔ Archduke Charles (lost 1995) vs Massena (lost 2975) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Mack (lost 2415) vs Massena (lost 3019) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Castanos (lost 129) vs Paget (lost 1026) — A grievous defeat for Paget, Sire. The losses are severe. And Paget was taken on that field — Spain holds him.
  - verbs: attack×4, fortify×1
- LEDGER treasury 19287 · net +1386 · threat 55 · provinces 28 (+0) · ceiling 35176 · army 148165 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 63
  - NET income 3400 · trade 237 · admin 50 · tribute 799 · upkeep 1384 · charges 1507 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 795 men, at Franche-Comte.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack launches a decisive assault. Mack gains the advantage over Massena. Casualties: Mack 2,076, Massena 3,141. Both ar… · ArchdukeJohn delivers an effective strike. Brutal stalemate between ArchdukeJohn and Massena. Heavy casualties on both …
  - ⚔ Mack (lost 2076) vs Massena (lost 3141) — A narrow defeat for Massena, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Archduke John (lost 641, own corps) vs Massena (lost 2030) — Neither Massena nor Archduke John could claim the field. The armies remain locked.
  - verbs: attack×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 20207 · net +1067 · threat 53 · provinces 27 (-1) · ceiling 31553 · army 142213 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 58
  - NET income 3200 · trade 237 · admin 50 · tribute 712 · upkeep 1212 · charges 1711 · blockade 119 · admiralty 90
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Corsica.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Mack gains the advantage over Massena. Casualties: Mack 1,561, Massena 2,458. Both armi… · ArchdukeJohn flanks from Tyrol while allies attack from Milan! (+1 coordination) · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Massena. Casualties: Arch…
  - 🏴 Austria: ArchdukeJohn advances into Milan. (60 lost to march — forward supply lines reduce losses) Milan has been captured by Austria!
  - ⚔ Mack (lost 1561) vs Massena (lost 2458) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Archduke John (lost 417, own corps) vs Massena (lost 3188) — A standard affair. Nothing unusual to report.
  - ⚔ Archduke Charles (lost 127, own corps) vs Massena (lost 3659) — The hills were ours, but Archduke Charles took them. Massena's position was overrun.
  - verbs: attack×3, unfortify×1, move×1
- ORDER Massena [awaiting_response]: Massena is cornered at Piedmont with 4,522 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Piedmont with 4,522 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 3 · Austria armistice losing · Britain settlement offer · Denmark non aggression
- LEDGER treasury 20647 · net +855 · threat 51 · provinces 27 (+0) · ceiling 28742 · army 127539 · vassals Holland 92 · Kingdom of Italy 94 · Switzerland 49
  - NET income 3200 · trade 237 · admin 50 · tribute 562 · upkeep 1016 · charges 1969 · blockade 119 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 14 — Early April 1806
  - MAILBOX #17 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #19 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #18 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #17 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Denmark. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #18 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #19 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Austria, armistice_losing #17 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #19 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #18 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (117 lost to march) Captured: France → Austria · ArchdukeCharles marches from Piedmont into Lyonnais unopposed! (342 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (117 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Lyonnais unopposed! (342 lost to march) Captured: France → Austria
  - verbs: attack×2, fortify×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 20604 · net -37 · threat 40 · provinces 25 (-2) · ceiling 20335 · army 126789 · vassals Holland 92 · Switzerland 41
  - NET income 2900 · trade 262 · admin 50 · tribute 562 · upkeep 1008 · charges 2582 · blockade 131 · admiralty 90
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 36% of active European bloc power.
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 15 — Late April 1806
  - MAILBOX #20 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #20 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Lyonnais into Limousin unopposed! (321 lost to march) Captured: France → Austria · ArchdukeJohn marches from Provence into Languedoc unopposed! (115 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Limousin unopposed! (321 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Languedoc unopposed! (115 lost to march) Captured: France → Austria
  - verbs: attack×2, unfortify×1, move×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 20242 · net -311 · threat 39 · provinces 23 (-2) · ceiling 18049 · army 126055 · vassals Holland 92 · Switzerland 33
  - NET income 2650 · trade 262 · admin 50 · tribute 562 · upkeep 1024 · charges 2590 · blockade 131 · admiralty 90
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 2
- DIPLO +6 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy, blockade_broken, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 16 — Early May 1806
  - MAILBOX #21 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #21 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: 3 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Piedmont into Savoy unopposed! (58 lost to march) Captured: France → Britain · ArchdukeJohn marches from Languedoc into Gascony unopposed! (229 lost to march) Captured: France → Austria · ArchdukeCharles marches from Limousin into Berry unopposed! (302 lost to march) Captured: France → Austria
  - 🏴 Britain: Shrapnel marches from Piedmont into Savoy unopposed! (58 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeJohn marches from Languedoc into Gascony unopposed! (229 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Limousin into Berry unopposed! (302 lost to march) Captured: France → Austria
  - verbs: attack×3
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 19395 · net -724 · threat 40 · provinces 20 (-3) · ceiling 14403 · army 125336 · vassals Holland 92 · Switzerland 25
  - NET income 2200 · trade 262 · admin 50 · tribute 562 · upkeep 1052 · charges 2525 · blockade 131 · admiralty 90
- DISPATCH: Sire — Savoy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 2
- COURTS: The court of Austria eases over Redeem Italy — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Spain, Sardinia and Holland rebuff Austria (defensive alliance)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 17 — Late May 1806
  - MAILBOX #22 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #22 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 4 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Lyonnais into Burgundy unopposed! (28 lost to march) Captured: France → Britain · ArchdukeCharles assaults the Normandy garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,815 troops in … · ArchdukeJohn marches from Gascony into Guyenne unopposed! (112 lost to march) Captured: France → Austria · ArchdukeCharles marches from Normandy into Artois unopposed! (163 lost to march) Captured: France → Austria
  - 🏴 Britain: Shrapnel marches from Lyonnais into Burgundy unopposed! (28 lost to march) Captured: France → Britain
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -90g, France -150g. Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Gascony into Guyenne unopposed! (112 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Normandy into Artois unopposed! (163 lost to march) Captured: France → Austria
  - verbs: attack×4
- LEDGER treasury 17702 · net -1051 · threat 41 · provinces 16 (-4) · ceiling 10892 · army 124630 · vassals Holland 92 · Switzerland 17
  - NET income 1800 · trade 262 · admin 50 · tribute 562 · upkeep 1080 · charges 2424 · blockade 131 · admiralty 90
- DISPATCH: Sire — Burgundy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 4 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Normandy into Maine unopposed! (49 lost to march) Captured: France → Britain · ArchdukeCharles marches from Artois into Champagne unopposed! (162 lost to march) Captured: France → Austria · ArchdukeJohn marches from Guyenne into Bordelais unopposed! (222 lost to march) Captured: France → Austria
  - 🏴 Britain: Paget marches from Normandy into Maine unopposed! (49 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Maine to Anjou. Anjou falls to Britain!
  - 🏴 Austria: ArchdukeCharles marches from Artois into Champagne unopposed! (162 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Guyenne into Bordelais unopposed! (222 lost to march) Captured: France → Austria
  - verbs: attack×3, move×1
- ENVOYS WAITING 2 · Austria peace · Britain settlement offer
- LEDGER treasury 15634 · net -1701 · threat 30 · provinces 12 (-4) · ceiling 6054 · army 123939 · vassals Holland 82
  - NET income 1400 · trade 262 · admin 50 · tribute 337 · upkeep 1108 · charges 2421 · blockade 131 · admiralty 90
- DISPATCH: Sire — Maine has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 50% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 6565 gold.
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - RAIL +1 more
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 19 — Late June 1806
  - MAILBOX #23 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #24 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Austria, peace #23 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #24 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Austria, peace #23 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #24 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Anjou into Brittany unopposed! (48 lost to march) Captured: France → Britain · Mack executes a brilliant maneuver! Mack gains the advantage over Bernadotte. Casualties: Mack 1,727, Bernadotte's army… · ArchdukeCharles marches from Champagne into Ile-de-France unopposed! (160 lost to march) Captured: France → Austria
  - 🏴 Britain: Paget marches from Anjou into Brittany unopposed! (48 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeCharles marches from Champagne into Ile-de-France unopposed! (160 lost to march) Captured: France → Austria
  - ⚔ Mack (lost 1727) vs Bernadotte (lost 976, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×3
- LEDGER treasury 13608 · net -1540 · threat 31 · provinces 10 (-2) · ceiling 5198 · army 120208 · vassals Holland 82
  - NET income 1242 · trade 262 · admin 50 · tribute 337 · upkeep 1084 · charges 2126 · blockade 131 · admiralty 90
- DISPATCH: Sire — Brittany has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, sovereign_takes_field, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 50% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Bordelais into Bearn unopposed! (218 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Bordelais into Bearn unopposed! (218 lost to march) Captured: France → Austria
  - verbs: attack×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 11289 · net -1818 · threat 30 · provinces 9 (-1) · ceiling 2887 · army 119319 · vassals Holland 84
  - NET income 1144 · trade 262 · admin 50 · tribute 337 · upkeep 1080 · charges 2010 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 21 — Late July 1806
  - MAILBOX #25 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #26 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Ile-de-France into Picardy unopposed! (158 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Ile-de-France into Picardy unopposed! (158 lost to march) Captured: France → Austria
  - verbs: attack×1
- ENVOYS WAITING 2 · Hesse non aggression · Switzerland settlement offer
- LEDGER treasury 9386 · net -1485 · threat 29 · provinces 8 (-1) · ceiling 2619 · army 118448 · vassals Holland 86
  - NET income 1096 · trade 262 · admin 50 · tribute 337 · upkeep 1088 · charges 1621 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — Picardy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 22 — Early August 1806
  - MAILBOX #26 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #27 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #27 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #27 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Orleanais into Ardennes unopposed! (155 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles moves from Picardy to Orleanais. Orleanais falls to Austria!
  - 🏴 Austria: ArchdukeCharles marches from Orleanais into Ardennes unopposed! (155 lost to march) Captured: France → Austria
  - verbs: move×1, attack×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 7709 · net -1303 · threat 28 · provinces 6 (-2) · army 117596 · vassals Holland 88
  - NET income 948 · trade 262 · admin 50 · tribute 337 · upkeep 1108 · charges 1271 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Spain and Holland rebuff Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 23 — Late August 1806
  - MAILBOX #28 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #29 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Prussia open borders · Britain settlement offer
- LEDGER treasury 6413 · net -1006 · threat 27 · provinces 6 (+0) · army 116761 · vassals Holland 90
  - NET income 950 · trade 262 · admin 50 · tribute 337 · upkeep 1100 · charges 984 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3083 gold.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 24 — Early September 1806
  - MAILBOX #29 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #30 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #30 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders #30 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 5431 · net -763 · threat 26 · provinces 6 (+0) · ceiling 2008 · army 115942 · vassals Holland 92
  - NET income 950 · trade 262 · admin 50 · tribute 337 · upkeep 1076 · charges 765 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_ai_proposal_refused: Spain rebuffs Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Spain rebuffs Austria (defensive alliance)

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 4676 · net -587 · threat 25 · provinces 6 (+0) · ceiling 2044 · army 115139 · vassals Holland 94
  - NET income 950 · trade 262 · admin 50 · tribute 337 · upkeep 1068 · charges 597 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 6 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Flanders garrison! Garrison collapses (6,000 -> 0). ArchdukeJohn loses 1,338 troops in the as…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -66g, France -150g. Captured: France → Austria
  - verbs: unfortify×1, move×1, attack×1
- ENVOYS WAITING 1 · Switzerland settlement offer
- LEDGER treasury 3517 · net -547 · threat 24 · provinces 5 (-1) · army 114353 · vassals Holland 96
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1080 · charges 345 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — Flanders has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 27 — Late October 1806
  - MAILBOX #31 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #32 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 2978 · net -416 · threat 21 · provinces 5 (+0) · army 113582 · vassals Holland 98
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1072 · charges 222 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 8 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 28 — Early November 1806
  - MAILBOX #32 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #33 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Hesse non aggression · Britain settlement offer
- LEDGER treasury 2570 · net -315 · threat 18 · provinces 5 (+0) · army 112827 · vassals Holland 100
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1064 · charges 129 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 9 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 1191 gold.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria, Britain, Russia and Switzerland remain at war with us.
  - LOG ai_ai_proposal_refused: Spain rebuffs Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 29 — Late November 1806
  - MAILBOX #33 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #34 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #34 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #35 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #34 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #35 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 2263 · net -237 · threat 15 · provinces 5 (+0) · army 112087 · vassals Holland 100
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1056 · charges 59 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 10 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL balance_of_europe_shifted: British Interest leads the current largest alignment at 57% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 30 — Early December 1806
  - MAILBOX #35 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #36 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 2050 · net -165 · threat 14 · provinces 5 (+0) · army 111362 · vassals Holland 100
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1032 · charges 11 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 11 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG balance_of_europe_shifted: British Interest leads the current largest alignment at 57% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG ai_ai_proposal_refused: Spain and Holland rebuff Austria (defensive alliance)

## Turn 31 — Late December 1806
  - MAILBOX #36 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #37 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland settlement offer
- LEDGER treasury 1893 · net -146 · threat 13 · provinces 5 (+0) · army 110651 · vassals Holland 100
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1024 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 12 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 32 — Early January 1807
  - MAILBOX #37 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #38 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 1755 · net -138 · threat 12 · provinces 5 (+0) · army 109955 · vassals Holland 100
  - NET income 675 · trade 262 · admin 50 · tribute 337 · upkeep 1016 · contributions 225 · blockade 131 · admiralty 90
- DISPATCH: Sire — Spain and Switzerland have made peace without us.
  - RAIL third_party_peace: THE CONGRESS: Spain and Switzerland have made their peace without France. Both courts are spent; their side of the war ends while the greater war goe…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Switzerland armistice losing · Britain settlement offer
- LEDGER treasury 1633 · net -122 · threat 11 · provinces 5 (+0) · army 109273 · vassals Holland 100
  - NET income 675 · trade 262 · admin 50 · tribute 337 · upkeep 1000 · contributions 225 · blockade 131 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 14 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 702 gold.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG third_party_peace: THE CONGRESS: Spain and Switzerland make peace without France

## Turn 34 — Early February 1807
  - MAILBOX #38 Switzerland incoming_proposal: Switzerland — Armistice → activated
  - MAILBOX #39 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Switzerland, armistice_losing #39 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #40 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Switzerland, armistice_losing #39 → reject
  - POPUP proposal_result: You have rejected Switzerland's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #40 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 1494 · net -139 · threat 8 · provinces 5 (+0) · army 108604 · vassals Holland 100
  - NET income 675 · trade 212 · admin 50 · tribute 337 · upkeep 992 · contributions 225 · blockade 106 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 15 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: 3 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Switzerland's armistice proposal

## Turn 35 — Late February 1807
  - MAILBOX #40 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #41 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 1322 · net -172 · threat 5 · provinces 5 (+0) · army 107949 · vassals Holland 100
  - NET income 675 · trade 212 · admin 50 · tribute 300 · upkeep 988 · contributions 225 · blockade 106 · admiralty 90
- DISPATCH: Sire — Friesland has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 36 — Early March 1807
  - MAILBOX #41 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #42 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Russia armistice losing · Switzerland settlement offer
- LEDGER treasury 1170 · net -152 · threat 2 · provinces 5 (+0) · army 107306 · vassals Holland 100
  - NET income 675 · trade 212 · admin 50 · tribute 300 · upkeep 968 · contributions 225 · blockade 106 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 17 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 37 — Late March 1807
  - MAILBOX #42 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #43 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #43 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #44 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Russia, armistice_losing #43 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #44 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 1018 · net -152 · threat 1 · provinces 5 (+0) · army 106676 · vassals Holland 100
  - NET income 675 · trade 212 · admin 50 · tribute 300 · upkeep 968 · contributions 225 · blockade 106 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 18 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 38 — Early April 1807
  - MAILBOX #44 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #45 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 870 · net -148 · threat 0 · provinces 5 (+0) · army 106059 · vassals Holland 100
  - NET income 675 · trade 212 · admin 50 · tribute 300 · upkeep 964 · contributions 225 · blockade 106 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 19 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 407 gold.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 39 — Late April 1807
  - MAILBOX #45 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #46 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn launches a decisive assault. Brutal stalemate between ArchdukeJohn and Bernadotte. Heavy casualties on bot… · Mack delivers an effective strike. Mack gains the advantage over Lannes. Casualties: Mack 1,956, Lannes's army 3,052. B… · Mack holds them at Franche-Comte while allies attack from Munich! (+1 coordination)
  - ⚔ Archduke John (lost 2668) vs Bernadotte (lost 194, own corps) — Lannes arrived to reinforce Bernadotte, but Ney failed to reach the field in time.
  - ⚔ Mack (lost 1956) vs Lannes (lost 1161, own corps) — Lannes was close. A period of drilling could have changed the outcome.
  - ⚔ Mack (lost 2936) vs Murat (lost 1167, own corps) — Reinforcements from Napoleon bolstered Murat's position — though Soult never arrived, Sire.
  - verbs: attack×3, move×1
- LEDGER treasury 341 · net -164 · threat 0 · provinces 5 (+0) · army 98018 · vassals Holland 100
  - NET income 645 · trade 212 · admin 50 · tribute 300 · upkeep 868 · contributions 307 · blockade 106 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Lorraine. He must reform before he fights again.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland armistice losing
- LEDGER treasury 272 · net -69 · threat 0 · provinces 5 (+0) · army 97561 · vassals Holland 100
  - NET income 650 · trade 212 · admin 50 · tribute 300 · upkeep 860 · contributions 225 · blockade 106 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 21 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 3 approaches from Russia and Austria are rebuffed (defensive alliance)

## Turn 41 — Late May 1807
  - MAILBOX #46 Switzerland incoming_proposal: Switzerland — Armistice → activated
  - POPUP diplomatic_dialogue: Switzerland, armistice_losing #47 → reject
  - POPUP proposal_result: You have rejected Switzerland's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 41 ended. (Warning: 4 actions unused) Turn 42 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Denmark non aggression · Switzerland settlement offer
- LEDGER treasury 212 · net -60 · threat 0 · provinces 5 (+0) · army 97113 · vassals Holland 100
  - NET income 655 · trade 212 · admin 50 · tribute 300 · upkeep 856 · contributions 225 · blockade 106 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 22 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Spain rebuffs Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Switzerland's armistice proposal
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Spain rebuffs Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain (defensive alliance)

## Turn 42 — Early June 1807
  - MAILBOX #47 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - MAILBOX #48 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #48 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #49 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Denmark, non_aggression #48 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #49 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 42 ended. (Warning: 4 actions unused) Turn 43 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Naples non aggression · Hesse non aggression
- LEDGER treasury 157 · net -55 · threat 0 · provinces 5 (+0) · army 96674 · vassals Holland 100
  - NET income 660 · trade 212 · admin 50 · tribute 300 · upkeep 856 · contributions 225 · blockade 106 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 23 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 43 — Late June 1807
  - MAILBOX #49 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - MAILBOX #50 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #50 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #51 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Naples, non_aggression #50 → reject
  - POPUP proposal_result: You have rejected Naples's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #51 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 43 ended. (Warning: 4 actions unused) Turn 44 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Mack gains the advantage over Lannes. Casualties: Mack 2,188, Lannes's army 3,681. Both…
  - ⚔ Mack (lost 2188) vs Lannes (lost 935, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - verbs: move×1, attack×1
- ENVOYS WAITING 2 · Russia armistice losing · Britain settlement offer
- LEDGER treasury -99 · net +322 · threat 0 · provinces 5 (+0) · ceiling 3378 · army 92136 · vassals Holland 100
  - NET income 655 · trade 212 · admin 50 · tribute 300 · upkeep 394 · contributions 305 · blockade 106 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franche-Comte. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 44 — Early July 1807
  - MAILBOX #51 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #52 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #52 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #53 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Russia, armistice_losing #52 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #53 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 44 ended. (Warning: 4 actions unused) Turn 45 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack delivers an effective strike. Mack gains the advantage over Lannes. Casualties: Mack 1,680, Lannes's army 3,278. B… · ArchdukeJohn flanks from Swabia while allies attack from Franche-Comte! (+1 coordination)
  - ⚔ Mack (lost 1680) vs Lannes (lost 937, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke John (lost 274, own corps) vs Murat (lost 5163) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×2
- ORDER Murat [awaiting_response]: Murat is cornered at Franche-Comte with 3,052 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Franche-Comte with 3,052 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - ENDING — THE VERDICT OF HISTORY: The reign, unfinished, is judged as it stands. [THE ECLIPSE]
  -     ↳ Early July 1807 (turn 44) · register `verdict` · marked — the campaign continues
  -     ↳ THE VERDICT — THE ECLIPSE: The Empire is smaller, poorer and more alone than it began. / Its enemies have learned that it can be beaten. / History will call it the beginning of the end.
  -     ↳ The Verdict of History: the eclipse.
  -     ↳ THE RECORD — battles 25 (5 won, 12 lost) · men lost 87,071, inflicted 64,515 · provinces taken 0, lost 23 · marshals fallen 0, taken 1 · coalitions faced 1 · peaces signed 0
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury -144 · net +390 · threat 0 · provinces 5 (+0) · ceiling 3635 · army 79725 · vassals Holland 98
  - NET income 471 · trade 212 · admin 50 · tribute 300 · upkeep 326 · contributions 121 · blockade 106 · admiralty 90
- DISPATCH: Sire — Lannes's corps has been broken at Franche-Comte. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - ENDING reached — stopping (--stop-on-ending)

---
finished: **ending-reached** · commands 44 · popups 111 · battles 26
