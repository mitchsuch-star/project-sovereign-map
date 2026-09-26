# Playtest digest — sr2-exit-loser

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `b3b95a0395fb` (dirty) · content `262c6dc45ebe` · driver `f870e9ba2f5e`
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
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties… · Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,166, Lan… · ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archduke…
  - ⚔ Archduke Charles (lost 3902) vs Massena (lost 5293) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 5166) vs Lannes (lost 1487, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 1757) vs Bernadotte (lost 4559) — The engagement proceeded as one might expect, Sire.
  - verbs: attack×3
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4166 · net +2243 · threat 66 · provinces 28 (+0) · ceiling 49020 · army 169638 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3382 · trade 350 · admin 50 · tribute 856 · upkeep 2022 · charges 108 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,559 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A… · Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4,438, Lan… · ArchdukeCharles faces a difficult fight. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles 1,… · Mack delivers an effective strike. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack 3,839,…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 982) vs Bernadotte (lost 7071) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 4438) vs Lannes (lost 1427, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 1811) vs Deroy (lost 4964) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - ⚔ Mack (lost 3839) vs Murat (lost 2224, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6128 · net +2541 · threat 64 · provinces 28 (+0) · ceiling 45828 · army 153859 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3352 · trade 350 · admin 50 · tribute 860 · upkeep 1542 · charges 264 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 12 approaches from Prussia, Naples and Denmark are rebuffed (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Brutal stalemate between Mack and Bernadotte. Heavy casualties on both sides: Mack 4,794,… · Mack engages in solid combat. Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack 3,427, Ma…
  - 🏴 Austria: Bernadotte retreats! Mack pursues into Munich. (1,932 lost to march) Munich has been captured by Austria!
  - ⚔ Mack (lost 4794) vs Bernadotte (lost 400, own corps) — Reinforcement from Lannes and Massena kept Bernadotte standing, Sire — but neither side yielded the ground.
  - ⚔ Mack (lost 3427) vs Massena (lost 3124) — Stalemate. Massena and Mack glare at each other across the field.
  - verbs: attack×2, retreat×1, stance_change×1, form_square×1
- LEDGER treasury 8460 · net +2486 · threat 62 · provinces 28 (+0) · ceiling 43362 · army 146303 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3354 · trade 237 · admin 50 · tribute 829 · upkeep 1316 · charges 459 · blockade 119 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Spain rebuffs Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected PapalStates's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack executes a brilliant maneuver! Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack 3,4… · Mack delivers an effective strike. Mack gains the advantage over Bernadotte. Casualties: Mack 1,196, Bernadotte's army …
  - ⚔ Mack (lost 3424) vs Massena (lost 3084) — Neither Massena nor Mack could claim the field. The armies remain locked.
  - ⚔ Mack (lost 1196) vs Bernadotte (lost 939, own corps) — Bernadotte fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×2
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Switzerland client petition
- LEDGER treasury 10794 · net +2443 · threat 60 · provinces 28 (+0) · ceiling 41784 · army 139113 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3352 · trade 237 · admin 50 · tribute 829 · upkeep 1124 · charges 692 · blockade 119 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franche-Comte. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Spain rebuffs Prussia, Naples and Denmark (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - MAILBOX #8 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #10 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #8 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #10 → refuse the petition
  - POPUP diplomatic_dialogue: Prussia, open_borders #8 → reject
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (84 → 74); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → refuse the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn attacks with overwhelming force. Brutal stalemate between ArchdukeJohn and Lannes. Heavy casualties on bot… · ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeCharles…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franche-Comte. (956 lost to march) Franche-Comte has been captured by Austria!
  - ⚔ Archduke John (lost 2316) vs Lannes (lost 653, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 671, own corps) vs Lannes (lost 2248, own corps) — Lannes fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×2, move×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 12590 · net +1946 · threat 58 · provinces 27 (-1) · ceiling 29018 · army 128539 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 69
  - NET income 3300 · trade 237 · admin 50 · tribute 833 · upkeep 1012 · charges 1253 · blockade 119 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. ArchdukeJohn's corps of 16,364 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 7 — Late December 1805
  - MAILBOX #11 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #11 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×2
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 14527 · net +1701 · threat 56 · provinces 27 (+0) · ceiling 28513 · army 126310 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 66
  - NET income 3300 · trade 237 · admin 50 · tribute 838 · upkeep 992 · charges 1523 · blockade 119 · admiralty 90
- DISPATCH: Lannes's army is recovering. Effectiveness penalty: -15%.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 8 — Early January 1806
  - MAILBOX #12 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #12 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces strike with perfect coordination! ArchdukeCharles gains the advantage over Murat. Casualties: …
  - ⚔ Archduke Charles (lost 2244, own corps) vs Murat (lost 977, own corps) — Reinforcements from Davout bolstered Murat's position — though Ney never arrived, Sire.
  - verbs: move×2, attack×1
- LEDGER treasury 15398 · net +1020 · threat 54 · provinces 27 (+0) · ceiling 21738 · army 116047 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 61
  - NET income 3288 · trade 237 · admin 50 · tribute 842 · upkeep 896 · charges 2154 · contributions 138 · blockade 119 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Lorraine. He must reform before he fights again.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos launches a decisive assault. Castanos gains the advantage over Paget. Casualties: Castanos 700, Paget 1,617. B… · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Castanos (lost 700) vs Paget (lost 1617) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - ⚔ Castanos (lost 352) vs Paget (lost 1483) — Paget's aggressive posture left the troops exposed when Castanos's attack came.
  - verbs: attack×2, move×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 16939 · net +1335 · threat 52 · provinces 27 (+0) · ceiling 26895 · army 113804 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 58
  - NET income 3291 · trade 237 · admin 50 · tribute 847 · upkeep 880 · charges 2001 · blockade 119 · admiralty 90
- DISPATCH: Murat's army is recovering. Effectiveness penalty: -15%.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
  - MAILBOX #13 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #13 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos launches a decisive assault. Castanos gains the advantage over Paget. Casualties: Castanos 70, Paget 817. Both…
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Galicia!
  - ⚔ Castanos (lost 70) vs Paget (lost 817) — Paget's corps broke, Sire. They are streaming back from the field. And Paget was taken on that field — Spain holds him.
  - verbs: attack×1, fortify×1
- LEDGER treasury 18249 · net +1130 · threat 50 · provinces 27 (+0) · ceiling 26482 · army 111617 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 55
  - NET income 3294 · trade 237 · admin 50 · tribute 851 · upkeep 864 · charges 2229 · blockade 119 · admiralty 90
- DISPATCH: Murat's army has fully recovered and is combat ready.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 19351 · net +947 · threat 48 · provinces 27 (+0) · ceiling 26095 · army 109485 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 52
  - NET income 3297 · trade 237 · admin 50 · tribute 856 · upkeep 848 · charges 2436 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 2,132 men, at Rhineland and Lorraine.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5177 gold.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 12 — Early March 1806
  - MAILBOX #14 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #14 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's assault collapses into chaos! Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack 2,…
  - ⚔ Mack (lost 2858) vs Massena (lost 2262) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: move×1, attack×1, recruit×1
- LEDGER treasury 20142 · net +774 · threat 46 · provinces 27 (+0) · ceiling 25480 · army 105144 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 49
  - NET income 3300 · trade 237 · admin 50 · tribute 838 · upkeep 816 · charges 2626 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 2,079 men, at Rhineland and Lorraine.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack struggles in a costly engagement. Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack …
  - ⚔ Mack (lost 2722) vs Massena (lost 2878) — Stalemate. Massena and Mack glare at each other across the field.
  - verbs: attack×1, fortify×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 20754 · net +642 · threat 44 · provinces 27 (+0) · ceiling 25041 · army 100240 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 41
  - NET income 3300 · trade 237 · admin 50 · tribute 829 · upkeep 760 · charges 2805 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 2,026 men, at Rhineland and Lorraine.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
  - MAILBOX #15 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #15 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeCharles …
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Milan. (334 lost to march — forward supply lines reduce losses) Milan has been captured by Austria!
  - ⚔ Archduke Charles (lost 1304) vs Massena (lost 4272) — Massena was driven from the field. His men are scattered.
  - verbs: attack×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 21004 · net +391 · threat 42 · provinces 27 (+0) · ceiling 23492 · army 93859 · vassals Holland 88 · Kingdom of Italy 98 · Switzerland 31
  - NET income 3300 · trade 237 · admin 50 · tribute 712 · upkeep 720 · charges 2979 · blockade 119 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 15 — Late April 1806
  - MAILBOX #16 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #16 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Britain armistice losing · Russia armistice losing
- LEDGER treasury 21358 · net +297 · threat 40 · provinces 27 (+0) · ceiling 23212 · army 91932 · vassals Holland 88 · Kingdom of Italy 98 · Switzerland 23
  - NET income 3300 · trade 237 · admin 50 · tribute 712 · upkeep 696 · charges 3097 · blockade 119 · admiralty 90
- DISPATCH: Sire — Britain and Spain have made peace without us.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy, blockade_broken)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 16 — Early May 1806
  - MAILBOX #17 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #18 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #17 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Russia. Your earlier answer was not delivered; the mat…
  - POPUP diplomatic_dialogue: incoming_proposal #18 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Britain, armistice_losing #17 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #18 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Prussia open borders · Britain settlement offer
- LEDGER treasury 21593 · net +197 · threat 40 · provinces 27 (+0) · ceiling 22796 · army 90052 · vassals Holland 88 · Kingdom of Italy 98 · Switzerland 15
  - NET income 3300 · trade 237 · admin 50 · tribute 712 · upkeep 696 · charges 3197 · blockade 119 · admiralty 90
- DISPATCH: Massena's army has fully recovered and is combat ready.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5693 gold.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal

## Turn 17 — Late May 1806
  - MAILBOX #19 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #20 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #19 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders #19 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21518 · net -62 · threat 30 · provinces 27 (+0) · ceiling 21140 · army 88219 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 3300 · trade 237 · admin 50 · tribute 487 · upkeep 680 · charges 3247 · blockade 119 · admiralty 90
- DISPATCH: Sire — Switzerland is no longer ours. Austria is their protector now.
  - RAIL diplomatic_vassal_transferred: Switzerland passes from France's suzerainty to Austria's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Austria's gold turns Switzerland against France.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21201 · net -263 · threat 29 · provinces 26 (-1) · ceiling 19647 · army 86431 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 3100 · trade 237 · admin 50 · tribute 487 · upkeep 672 · charges 3256 · blockade 119 · admiralty 90
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. Paget's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison…
  - RAIL expedition_landed: THE LANDING: Paget has put 9,750 men ashore at Corsica.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 20893 · net -255 · threat 28 · provinces 26 (+0) · ceiling 19413 · army 84689 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 3100 · trade 237 · admin 50 · tribute 487 · upkeep 656 · charges 3264 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 1,742 men, at Rhineland and Lorraine.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 20 — Early July 1806
  - saved `sr2-exit-loser_t20` → Game saved: sr2-exit-loser_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 20593 · net -247 · threat 25 · provinces 26 (+0) · ceiling 19187 · army 82990 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 3100 · trade 237 · admin 50 · tribute 487 · upkeep 640 · charges 3272 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 1,699 men, at Rhineland and Lorraine.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 21 — Late July 1806
  - MAILBOX #21 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #21 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Hesse non aggression · Britain settlement offer
- LEDGER treasury 20303 · net -238 · threat 22 · provinces 26 (+0) · ceiling 18969 · army 81332 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 3100 · trade 237 · admin 50 · tribute 487 · upkeep 624 · charges 3279 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 1,658 men, at Rhineland and Lorraine.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5508 gold.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 22 — Early August 1806
  - MAILBOX #22 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #23 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #22 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #22 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Russia armistice losing · Austria armistice losing
- LEDGER treasury 20608 · net +259 · threat 19 · provinces 26 (+0) · ceiling 22325 · army 79716 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 3100 · trade 237 · admin 50 · tribute 487 · upkeep 608 · charges 2798 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 1,616 men, at Rhineland and Lorraine.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria, Britain and Russia remain at war with us.
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 23 — Late August 1806
  - MAILBOX #24 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #25 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #24 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #25 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #24 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #25 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, recruit×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 20883 · net +233 · threat 20 · provinces 26 (+0) · ceiling 22432 · army 78141 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 3100 · trade 237 · admin 50 · tribute 487 · upkeep 592 · charges 2840 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 1,575 men, at Rhineland and Lorraine.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 24 — Early September 1806
  - MAILBOX #26 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #26 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Massena. Casualties: Arch… · ArchdukeCharles marches from Piedmont into Provence unopposed! (1,179 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles advances into Piedmont. (1,216 lost to march — forward supply lines reduce losses) Piedmont has been captured by Austria!
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (1,179 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 928) vs Massena (lost 7884) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×2
- LEDGER treasury 19880 · net -497 · threat 11 · provinces 25 (-1) · ceiling 17184 · army 68720 · vassals Holland 86
  - NET income 2900 · trade 262 · admin 50 · tribute 337 · upkeep 528 · charges 3297 · blockade 131 · admiralty 90
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. ArchdukeCharles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does a…
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeChar… · Mack faces a difficult fight. Mack gains the advantage over Bernadotte. Casualties: Mack 1,425, Bernadotte's army 4,411…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Lorraine!
  - ⚔ Archduke Charles (lost 99) vs Massena (lost 2889) — Massena's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 1425) vs Bernadotte (lost 449, own corps) — Ney failed to arrive in time. Bernadotte's army fought without expected support. And Bernadotte was taken on that field…
  - verbs: attack×2, move×1, naval_expedition×1, grant_dotation×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Lorraine with 2,722 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
- ORDER Massena [awaiting_response]: Massena is cornered at Lyonnais with 2,414 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Lorraine with 2,722 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Lyonnais with 2,414 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 18467 · net -788 · threat 12 · provinces 25 (+0) · ceiling 14857 · army 53634 · vassals Holland 82
  - NET income 2880 · trade 262 · admin 50 · tribute 337 · upkeep 408 · charges 3596 · contributions 92 · blockade 131 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Piedmont.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Lyonnais where he stands! (1,071 lost to march) Captured: France → Austria · ArchdukeCharles marches from Lyonnais into Limousin unopposed! (1,039 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Paris garrison! Garrison: 25,000 -> 14,417 (-10,583). ArchdukeCharles loses 6,944 troops. …
  - 🏴 Austria: ArchdukeCharles takes Lyonnais where he stands! (1,071 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Limousin unopposed! (1,039 lost to march) Captured: France → Austria
  - verbs: attack×3
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 17461 · net -385 · threat 13 · provinces 23 (-2) · ceiling 15474 · army 52851 · vassals Holland 82
  - NET income 2586 · trade 262 · admin 50 · tribute 337 · upkeep 400 · charges 2999 · blockade 131 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil. ArchdukeCharles's corps of 36,465 stands there. A garrison you detach (3,000 men) holds a province against a march, as does an…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5840 gold.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, agenda_shift ×2)

## Turn 27 — Late October 1806
  - MAILBOX #27 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #27 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Paris garrison! Garrison: 16,417 -> 8,209 (-8,208). ArchdukeCharles loses 4,560 troops. Ga… · ArchdukeCharles assaults the Paris garrison! Garrison collapses (8,209 -> 0). ArchdukeCharles loses 2,533 troops in the… · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 7,120 (-4,880). ArchdukeCharles loses 4,166 troops.…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -126g, France -205g. Captured: France → Austria
  - verbs: attack×3
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 15737 · net -673 · threat 10 · provinces 22 (-1) · ceiling 12702 · army 52083 · vassals Holland 82
  - NET income 2340 · trade 262 · admin 50 · tribute 337 · upkeep 392 · charges 3049 · blockade 131 · admiralty 90
- DISPATCH: Sire — Paris HAS FALLEN. Our capital is in Austria's hands, and every courier in Europe is already carrying the news.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 28 — Early November 1806
  - MAILBOX #28 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #28 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Normandy garrison! Garrison collapses (7,120 -> 0). ArchdukeCharles loses 1,977 troops in …
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -98g, France -178g. Captured: France → Austria
  - verbs: attack×1, defend×1
- ENVOYS WAITING 2 · Austria peace · Hesse non aggression
- LEDGER treasury 14890 · net -520 · threat 7 · provinces 21 (-1) · ceiling 12545 · army 51331 · vassals Holland 82
  - NET income 2297 · trade 262 · admin 50 · tribute 337 · upkeep 384 · charges 2861 · blockade 131 · admiralty 90
- DISPATCH: Sire — Normandy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 29 — Late November 1806
  - MAILBOX #29 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #30 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Austria, peace #29 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #30 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, peace #29 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #30 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 5 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Normandy into Berry unopposed! (847 lost to march) Captured: France → Britain · Mack attacks with overwhelming force. Brutal stalemate between Mack and Soult. Heavy casualties on both sides: Mack 4,0… · Mack delivers an effective strike. Mack gains the advantage over Napoleon. Casualties: Mack 764, Napoleon's army 3,150.…
  - 🏴 Britain: Moore marches from Normandy into Berry unopposed! (847 lost to march) Captured: France → Britain
  - 🏴 Austria: Both armies remain in the field. Mack advances into Lorraine. (934 lost to march) Lorraine has been captured by Austria!
  - ⚔ Mack (lost 4093) vs Soult (lost 650, own corps) — Ney, Davout and Murat arrived in time to steady Soult's position. The field was held, nothing further.
  - ⚔ Mack (lost 764) vs Napoleon (lost 792, own corps) — Napoleon's army has been badly mauled. Mack proved the stronger force today.
  - verbs: attack×3, unfortify×1, move×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 13837 · net -577 · threat 6 · provinces 19 (-2) · ceiling 11234 · army 44001 · vassals Holland 80
  - NET income 1950 · trade 262 · admin 50 · tribute 337 · upkeep 328 · charges 2627 · blockade 131 · admiralty 90
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 30 — Early December 1806
  - MAILBOX #31 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #31 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - saved `sr2-exit-loser_t30` → Game saved: sr2-exit-loser_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 5 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Berry into Gascony unopposed! (1,079 lost to march) Captured: France → Britain · Mack engages in solid combat. Mack gains the advantage over Soult. Casualties: Mack 287, Soult 3,073. Both armies remai… · Mack holds them at Orleanais while allies attack from Lorraine! (+1 coordination) · Mack holds them at Orleanais while allies attack from Lorraine! (+1 coordination)
  - 🏴 Britain: Moore marches from Berry into Gascony unopposed! (1,079 lost to march) Captured: France → Britain
  - ⚔ Mack (lost 287) vs Soult (lost 3073) — The toll on Soult's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Mack (lost 79) vs Napoleon (lost 676) — Napoleon was driven from the field. His men are scattered.
  - ⚔ Mack (lost 214) vs Murat (lost 2540) — The toll on Murat's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4, grant_dotation×1
- ORDER Murat [awaiting_response]: Murat is cornered at Orleanais with 2,872 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Orleanais — 1,115 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Orleanais with 2,872 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Orleanais — 1,115 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 12468 · net -765 · threat 7 · provinces 18 (-1) · ceiling 9428 · army 33725 · vassals Holland 74
  - NET income 1754 · trade 262 · admin 50 · tribute 337 · upkeep 256 · charges 2637 · contributions 54 · blockade 131 · admiralty 90
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 31 — Late December 1806
  - MAILBOX #32 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #32 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 5 actions, 5 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Gascony into Guyenne unopposed! (464 lost to march) Captured: France → Britain · Moore marches from Guyenne into Anjou unopposed! (433 lost to march) Captured: France → Britain · Mack takes Orleanais where he stands! (643 lost to march) Captured: France → Austria · Mack launches a decisive assault. Mack gains the advantage over Soult. Casualties: Mack 156, Soult 2,056. Both armies r…
  - 🏴 Britain: Moore marches from Gascony into Guyenne unopposed! (464 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Guyenne into Anjou unopposed! (433 lost to march) Captured: France → Britain
  - 🏴 Austria: Mack takes Orleanais where he stands! (643 lost to march) Captured: France → Austria
  - 🏴 Austria: [!] Soult's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Burgundy. (582 lost to march) Burgundy has been captured by Austria!
  - 🏴 Austria: Mack marches from Burgundy into Savoy unopposed! (1,080 lost to march) Captured: France → Austria
  - ⚔ Mack (lost 156) vs Soult (lost 2056) — A grievous defeat for Soult, Sire. The losses are severe.
  - verbs: attack×5
- ENVOYS WAITING 2 · Britain settlement offer · Holland client petition
- LEDGER treasury 11503 · net -671 · threat 8 · provinces 13 (-5) · ceiling 8477 · army 31669 · vassals Holland 70
  - NET income 1250 · trade 262 · admin 50 · tribute 337 · upkeep 240 · charges 2109 · blockade 131 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 4946 gold.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 32 — Early January 1807
  - MAILBOX #33 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #34 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #33 → reject_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #34 → refuse the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #33 → reject_settlement_offer
  - POPUP proposal_result: Holland's petition for relief is refused: loyalty −10 (70 → 60); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #34 → refuse the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 6 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Anjou into Maine unopposed! (229 lost to march) Captured: France → Britain · ArchdukeCharles marches from Normandy into Artois unopposed! (190 lost to march) Captured: France → Austria · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Soult. Casualties: ArchdukeCh… · ArchdukeCharles marches from Champagne into Picardy unopposed! (186 lost to march) Captured: France → Austria
  - 🏴 Britain: Moore marches from Anjou into Maine unopposed! (229 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeCharles marches from Normandy into Artois unopposed! (190 lost to march) Captured: France → Austria
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Champagne. (188 lost to march) Champagne has been captured by Austria!
  - 🏴 Austria: ArchdukeCharles marches from Champagne into Picardy unopposed! (186 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 70) vs Soult (lost 1247) — The toll on Soult's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4, move×2
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 10442 · net -778 · threat 9 · provinces 9 (-4) · ceiling 6936 · army 30422 · vassals Holland 47
  - NET income 900 · trade 262 · admin 50 · tribute 337 · upkeep 232 · charges 1874 · blockade 131 · admiralty 90
- DISPATCH: Sire — Maine has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 53% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 33 — Late January 1807
  - MAILBOX #35 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #35 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 4 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Maine into Brittany unopposed! (218 lost to march) Captured: France → Britain · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Soult. Casualties: ArchdukeCh… · ArchdukeCharles assaults the Flanders garrison! Garrison: 12,000 -> 6,623 (-5,377). ArchdukeCharles loses 3,527 troops.…
  - 🏴 Britain: Moore marches from Maine into Brittany unopposed! (218 lost to march) Captured: France → Britain
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Ile-de-France. (184 lost to march) Ile-de-France has been captured by Austria!
  - ⚔ Archduke Charles (lost 30) vs Soult (lost 635) — Soult's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×3, move×1
- LEDGER treasury 9274 · net -676 · threat 10 · provinces 7 (-2) · ceiling 6225 · army 29787 · vassals Holland 34
  - NET income 734 · trade 262 · admin 50 · tribute 337 · upkeep 224 · charges 1614 · blockade 131 · admiralty 90
- DISPATCH: Sire — Brittany has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 53% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Soult. Casualties: Archdu… · Mack attacks with overwhelming force. Mack gains the advantage over Soult. Casualties: Mack 8, Soult 135. Both armies r…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Ardennes. (145 lost to march) Ardennes has been captured by Austria!
  - 🏴 Austria: [!] MARSHAL CAPTURED — Soult is taken by Austria at Ile-de-France!
  - ⚔ Archduke Charles (lost 13) vs Soult (lost 302) — The line gave way. Soult is falling back, and not in good order.
  - ⚔ Mack (lost 8) vs Soult (lost 135) — The line gave way. Soult is falling back, and not in good order. And Soult was taken on that field — Austria holds him.
  - verbs: attack×2, move×1, fortify×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 8173 · net -840 · threat 0 · provinces 6 (-1) · ceiling 4387 · army 29183 · vassals none
  - NET income 688 · trade 212 · admin 50 · upkeep 224 · charges 1370 · blockade 106 · admiralty 90
- DISPATCH: Sire — Ardennes has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL balance_of_europe_shifted: Russian Sphere leads the current largest alignment at 57% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_vassal_transferred: Holland passes from France's suzerainty to Russia's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Russia's gold turns Holland against France.
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_auto_downgrade, blockade_broken)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 35 — Late February 1807
  - MAILBOX #36 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #36 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 3 actions, 1 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Guyenne into Bordelais unopposed! (394 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Guyenne into Bordelais unopposed! (394 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore moves from Bordelais to Bearn. Bearn falls to Britain!
  - verbs: attack×1, move×1, unfortify×1
- ENVOYS WAITING 2 · Austria peace · Hesse non aggression
- LEDGER treasury 7137 · net -806 · threat 0 · provinces 4 (-2) · ceiling 3504 · army 29183 · vassals none
  - NET income 492 · trade 212 · admin 50 · upkeep 224 · charges 1140 · blockade 106 · admiralty 90
- DISPATCH: Sire — Bordelais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG balance_of_europe_shifted: Russian Sphere leads the current largest alignment at 57% of active European bloc power.

## Turn 36 — Early March 1807
  - MAILBOX #37 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #38 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Austria, peace #37 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #38 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, peace #37 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #38 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack assaults the Flanders garrison! Garrison collapses (6,623 -> 0). Mack loses 1,803 troops in the assault. Mack marc… · ArchdukeCharles marches from Orleanais into Nivernais unopposed! (142 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -90g, France -165g. Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Orleanais into Nivernais unopposed! (142 lost to march) Captured: France → Austria
  - verbs: attack×2, move×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 5961 · net -787 · threat 0 · provinces 2 (-2) · ceiling 2414 · army 29183 · vassals none
  - NET income 250 · trade 212 · admin 50 · upkeep 224 · charges 879 · blockade 106 · admiralty 90
- DISPATCH: Sire — Flanders has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL balance_of_europe_shifted: Russian Sphere leads the current largest alignment at 61% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal

## Turn 37 — Late March 1807
  - MAILBOX #39 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #39 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 6 actions, 1 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Gascony into Languedoc unopposed! (470 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Gascony into Languedoc unopposed! (470 lost to march) Captured: France → Britain
  - verbs: fortify×2, recruit×2, attack×1, move×1
- ENVOYS WAITING 2 · Prussia open borders · Britain settlement offer
- LEDGER treasury 5074 · net -690 · threat 1 · provinces 1 (-1) · army 29183 · vassals none
  - NET income 150 · trade 212 · admin 50 · upkeep 224 · charges 682 · blockade 106 · admiralty 90
- DISPATCH: Sire — France holds a single province: Rhineland. Paris is in Austria's hands. 2 corps still stand under our colours — Ney and Davout, 29,183 men in all. The Emperor is a prisoner of Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 2384 gold.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 38 — Early April 1807
  - MAILBOX #40 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #41 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #40 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #41 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders #40 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #41 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack delivers an effective strike. Ney holds the line. Casualties: Mack 3,252, Ney's army 1,947. Both armies remain in … · Mack engages in solid combat. Davout holds the line. Casualties: Mack 2,838, Davout's army 1,225. Both armies remain in…
  - ⚔ Mack (lost 3252) vs Ney (lost 985, own corps) — The engagement proceeded as one might expect, Sire.
  - ⚔ Mack (lost 2838) vs Davout (lost 605, own corps) — Complete dominance on the field. Mack crumbled before Davout.
  - verbs: attack×2, recruit×2, move×1, wait×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 4257 · net -513 · threat 2 · provinces 1 (+0) · army 26011 · vassals none
  - NET income 122 · trade 212 · admin 50 · upkeep 200 · charges 501 · blockade 106 · admiralty 90
- DISPATCH: Sire — France holds a single province: Rhineland. Paris is in Austria's hands. 2 corps still stand under our colours — Ney and Davout, 26,011 men in all. The Emperor is a prisoner of Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and Holland has collapsed. War resumes!
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, blockade_begins)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 39 — Late April 1807
  - MAILBOX #42 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #42 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack delivers an effective strike. Ney holds the line. Casualties: Mack 3,573, Ney's army 1,569. Both armies remain in … · Mack engages in solid combat. Davout holds the line. Casualties: Mack 4,507, Davout's army 666. Both armies remain in t…
  - ⚔ Mack (lost 3573) vs Ney (lost 794, own corps) — Complete dominance on the field. Mack crumbled before Ney.
  - ⚔ Mack (lost 4507) vs Davout (lost 329, own corps) — An exemplary engagement by Davout. The outcome was never in doubt.
  - verbs: attack×2
- LEDGER treasury 3648 · net -387 · threat 3 · provinces 1 (+0) · army 23776 · vassals none
  - NET income 96 · trade 212 · admin 50 · upkeep 184 · charges 365 · blockade 106 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Rhineland — Mack's corps is driven from Rhineland yet again — broken, and fleeing.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 7 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Ney. Heavy casualties on both… · ArchdukeJohn launches a devastating assault! Brutal stalemate between ArchdukeJohn and Ney. Heavy casualties on both si… · ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Davout. Heavy casualties on b…
  - ⚔ Archduke Charles (lost 1802) vs Ney (lost 1184, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke John (lost 773, own corps) vs Ney (lost 1100, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 1205) vs Davout (lost 792, own corps) — Neither Davout nor Archduke Charles could claim the field. The armies remain locked.
  - verbs: attack×3, unfortify×2, recruit×2
  - ENDING — THE FALL OF THE EMPIRE: The Emperor, a prisoner these 10 turns, is deposed. [THE ECLIPSE]
  -     ↳ Early May 1807 (turn 40) · register `fall` · TERMINAL — Load / Main Menu
  -     ↳ THE VERDICT — THE ECLIPSE: The Empire is smaller and more alone than it began. / Its enemies have learned that it can be beaten. / History will call it the beginning of the end.
  -     ↳ The Verdict of History: the eclipse.
  -     ↳ THE RECORD — battles 44 (8 won, 21 lost) · men lost 155,882, inflicted 104,085 · provinces taken 0, lost 27 · marshals fallen 0, taken 6 · coalitions faced 1 · peaces signed 0
  -     ↳ THE EXILE (captivity) — In early May 1807, the Empire fell. The Emperor, taken in late December 1806, had been a prisoner of Austria for 10 turns, and Paris stopped waiting. Austria sent him to the fortress of Olmütz — where Austria once kept Lafayette, and knew how to keep a man.
  -     ↳ Davout asked to share his captivity, and was refused. Bernadotte and Lannes were still prisoners of the enemy.
  -     ↳ In 44 battles the Empire won 8 and lost 21; 104,085 of the enemy fell against 155,882 of our own. The assault on Paris (early October 1806) was the high-water mark. The Battle of Piedmont was the worst day. 27 provinces were lost to the enemy; Austria took the most. One coalition stood against him — the Third Coalition.
  -     ↳ The Verdict of History: the eclipse. Metternich, with perfect politeness: "A small inconvenience of residence. The air at Olmütz is said to be bracing."
- LEDGER treasury 3042 · net -235 · threat 4 · provinces 1 (+0) · army 17660 · vassals none
  - NET income 58 · trade 212 · admin 50 · upkeep 128 · charges 231 · blockade 106 · admiralty 90
- DISPATCH: Sire — the Empire has stood reduced 4 turns, and every province retaken would pay again. France holds a single province: Rhineland. Paris is in Austria's hands. 2 corps still stand under our colours …
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - GAME OVER reported — stopping

---
finished: **game-over** · commands 40 · popups 92 · battles 41
