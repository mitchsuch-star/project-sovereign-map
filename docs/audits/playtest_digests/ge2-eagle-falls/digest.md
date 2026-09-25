# Playtest digest — ge2-eagle-falls

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `da91683b56dc` (dirty) · content `4fdb803f0fdd` · driver `296621f2139c`
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
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6128 · net +2541 · threat 64 · provinces 28 (+0) · ceiling 45828 · army 153859 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3352 · trade 350 · admin 50 · tribute 860 · upkeep 1542 · charges 264 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
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
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → reject_settlement_offer
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
  - MAILBOX #9 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #9 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #11 → refuse the petition
  - POPUP diplomatic_dialogue: Prussia, open_borders #9 → reject
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (84 → 74); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → refuse the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn attacks with overwhelming force. Brutal stalemate between ArchdukeJohn and Lannes. Heavy casualties on bot… · ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeCharles…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franche-Comte. (956 lost to march) Franche-Comte has been captured by Austria!
  - ⚔ Archduke John (lost 2316) vs Lannes (lost 653, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 671, own corps) vs Lannes (lost 2248, own corps) — Lannes fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×2, move×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 12590 · net +1946 · threat 57 · provinces 27 (-1) · ceiling 29018 · army 128539 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 69
  - NET income 3300 · trade 237 · admin 50 · tribute 833 · upkeep 1012 · charges 1253 · blockade 119 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. ArchdukeJohn's corps of 16,364 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Spain will not forgive Britain the loss of Aragon and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 7 — Late December 1805
  - MAILBOX #12 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #12 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×2
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 14527 · net +1701 · threat 54 · provinces 27 (+0) · ceiling 28513 · army 126310 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 66
  - NET income 3300 · trade 237 · admin 50 · tribute 838 · upkeep 992 · charges 1523 · blockade 119 · admiralty 90
- DISPATCH: Lannes's army is recovering. Effectiveness penalty: -15%.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 1 more — Britain is not forgiven
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 8 — Early January 1806
  - MAILBOX #13 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #13 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces strike with perfect coordination! ArchdukeCharles gains the advantage over Murat. Casualties: …
  - ⚔ Archduke Charles (lost 2244, own corps) vs Murat (lost 977, own corps) — Reinforcements from Davout bolstered Murat's position — though Ney never arrived, Sire.
  - verbs: move×2, attack×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 15398 · net +1020 · threat 51 · provinces 27 (+0) · ceiling 21738 · army 116047 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 61
  - NET income 3288 · trade 237 · admin 50 · tribute 842 · upkeep 896 · charges 2154 · contributions 138 · blockade 119 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Lorraine. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3977 gold.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 9 — Late January 1806
  - MAILBOX #14 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #14 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack attacks with overwhelming force. Brutal stalemate between Mack and Bernadotte. Heavy casualties on both sides: Mac…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Lorraine!
  - ⚔ Mack (lost 2417) vs Bernadotte (lost 310, own corps) — Ney failed to arrive in time. Bernadotte's army fought without expected support. And Bernadotte was taken on that field…
  - verbs: attack×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 16811 · net +1353 · threat 49 · provinces 27 (+0) · ceiling 26786 · army 108227 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 58
  - NET income 3276 · trade 237 · admin 50 · tribute 847 · upkeep 840 · charges 2008 · blockade 119 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 35% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…

## Turn 10 — Early February 1806
  - MAILBOX #15 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #15 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18140 · net +1144 · threat 47 · provinces 27 (+0) · ceiling 26380 · army 106470 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 55
  - NET income 3279 · trade 237 · admin 50 · tribute 851 · upkeep 824 · charges 2240 · blockade 119 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 19057 · net +786 · threat 45 · provinces 26 (-1) · ceiling 24591 · army 104766 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 52
  - NET income 3082 · trade 237 · admin 50 · tribute 856 · upkeep 808 · charges 2422 · blockade 119 · admiralty 90
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Corsica.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's assault collapses into chaos! Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack 2,…
  - ⚔ Mack (lost 2858) vs Massena (lost 2073) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: move×1, attack×1, recruit×1
- LEDGER treasury 19697 · net +635 · threat 43 · provinces 26 (+0) · ceiling 24028 · army 101040 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 49
  - NET income 3085 · trade 237 · admin 50 · tribute 838 · upkeep 776 · charges 2590 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 1,653 men, at Rhineland.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Ma…
  - ⚔ Mack (lost 2550) vs Massena (lost 3354) — Stalemate. Massena and Mack glare at each other across the field.
  - verbs: attack×1, fortify×1
- ENVOYS WAITING 2 · Denmark non aggression · Britain settlement offer
- LEDGER treasury 20124 · net +504 · threat 41 · provinces 26 (+0) · ceiling 23444 · army 96083 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 41
  - NET income 3088 · trade 237 · admin 50 · tribute 829 · upkeep 744 · charges 2747 · blockade 119 · admiralty 90
- DISPATCH: Supply cost you 1,603 men, at Rhineland.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5349 gold.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
  - MAILBOX #16 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - MAILBOX #17 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #16 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Denmark, non_aggression #16 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeChar…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Milan. (340 lost to march — forward supply lines reduce losses) Milan has been captured by Austria!
  - ⚔ Archduke Charles (lost 1164) vs Massena (lost 5063) — Massena was driven from the field. His men are scattered.
  - verbs: attack×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 20211 · net +286 · threat 38 · provinces 26 (+0) · ceiling 22006 · army 89344 · vassals Holland 88 · Kingdom of Italy 98 · Switzerland 31
  - NET income 3091 · trade 237 · admin 50 · tribute 712 · upkeep 696 · charges 2899 · blockade 119 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +5 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 15 — Late April 1806
  - MAILBOX #18 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #18 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 20450 · net +200 · threat 35 · provinces 26 (+0) · ceiling 21679 · army 87836 · vassals Holland 88 · Kingdom of Italy 98 · Switzerland 23
  - NET income 3094 · trade 237 · admin 50 · tribute 712 · upkeep 688 · charges 2996 · blockade 119 · admiralty 90
- DISPATCH: Sire — Britain and Spain have made peace without us.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 16 — Early May 1806
  - MAILBOX #19 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #19 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 20185 · net -221 · threat 24 · provinces 25 (-1) · ceiling 18847 · army 86372 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 2897 · trade 237 · admin 50 · tribute 487 · upkeep 672 · charges 3011 · blockade 119 · admiralty 90
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. Paget's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garriso…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Provence.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_vassal_transferred: Switzerland passes from France's suzerainty to Russia's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Russia's gold turns Switzerland against France.
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_vassal_courting, balance_of_europe_shifted, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 36% of active European bloc power.

## Turn 17 — Late May 1806
  - MAILBOX #20 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #20 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Provence into Lyonnais unopposed! (50 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Provence into Lyonnais unopposed! (50 lost to march) Captured: France → Britain
  - verbs: attack×1
- LEDGER treasury 19833 · net -293 · threat 23 · provinces 24 (-1) · ceiling 18095 · army 84952 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 2800 · trade 237 · admin 50 · tribute 487 · upkeep 648 · charges 3010 · blockade 119 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil. Paget's corps of ~2,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison…
  - TURN EVENTS 1
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Lyonnais into Limousin unopposed! (48 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Lyonnais into Limousin unopposed! (48 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Limousin to Berry. Berry falls to Britain!
  - verbs: attack×1, move×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 19141 · net -573 · threat 22 · provinces 22 (-2) · ceiling 15808 · army 83575 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 2450 · trade 237 · admin 50 · tribute 487 · upkeep 640 · charges 2948 · blockade 119 · admiralty 90
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5724 gold.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 19 — Late June 1806
  - MAILBOX #21 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #21 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Limousin into Gascony unopposed! (94 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Limousin into Gascony unopposed! (94 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Gascony to Languedoc. Languedoc falls to Britain!
  - verbs: attack×1, move×1
- LEDGER treasury 18271 · net -717 · threat 21 · provinces 20 (-2) · ceiling 14174 · army 82239 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 2200 · trade 237 · admin 50 · tribute 487 · upkeep 632 · charges 2850 · blockade 119 · admiralty 90
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Lyonnais into Savoy unopposed! (90 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Lyonnais into Savoy unopposed! (90 lost to march) Captured: France → Britain
  - verbs: attack×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 17410 · net -708 · threat 18 · provinces 19 (-1) · ceiling 13440 · army 80944 · vassals Holland 88 · Kingdom of Italy 98
  - NET income 2100 · trade 237 · admin 50 · tribute 487 · upkeep 624 · charges 2749 · blockade 119 · admiralty 90
- DISPATCH: Sire — Savoy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria, Britain and Russia remain at war with us.

## Turn 21 — Late July 1806
  - MAILBOX #22 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #22 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Berry into Guyenne unopposed! (43 lost to march) Captured: France → Britain · Mack engages in solid combat. Mack gains the advantage over Massena. Casualties: Mack 849, Massena 5,443. Both armies r…
  - 🏴 Britain: Paget marches from Berry into Guyenne unopposed! (43 lost to march) Captured: France → Britain
  - ⚔ Mack (lost 849) vs Massena (lost 5443) — Even the favorable ground could not save Massena, Sire. Mack overcame the terrain.
  - verbs: attack×2, move×1
- ORDER Massena [awaiting_response]: Massena is cornered at Piedmont with 6,677 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Piedmont with 6,677 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 16134 · net -770 · threat 15 · provinces 18 (-1) · ceiling 11983 · army 67567 · vassals Holland 86 · Kingdom of Italy 96
  - NET income 1950 · trade 237 · admin 50 · tribute 337 · upkeep 512 · charges 2623 · blockade 119 · admiralty 90
- DISPATCH: Sire — Guyenne has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 22 — Early August 1806
  - MAILBOX #23 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #23 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Limousin into Burgundy unopposed! (41 lost to march) Captured: France → Britain · Mack marches from Piedmont into Piedmont unopposed! (1,676 lost to march) Captured: KingdomOfItaly → Austria
  - 🏴 Britain: Paget marches from Limousin into Burgundy unopposed! (41 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Burgundy to Orleanais. Orleanais falls to Britain!
  - 🏴 Austria: Mack marches from Piedmont into Piedmont unopposed! (1,676 lost to march) Captured: KingdomOfItaly → Austria
  - verbs: attack×2, move×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 15227 · net -738 · threat 2 · provinces 16 (-2) · ceiling 11245 · army 66347 · vassals Holland 86
  - NET income 1800 · trade 262 · admin 50 · tribute 337 · upkeep 512 · charges 2454 · blockade 131 · admiralty 90
- DISPATCH: Sire — Burgundy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 1
- COURTS: The court of Austria eases over Redeem Italy — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Spain, Sardinia and Holland rebuff Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 23 — Late August 1806
  - MAILBOX #24 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #24 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Orleanais into Nivernais unopposed! (40 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Orleanais into Nivernais unopposed! (40 lost to march) Captured: France → Britain
  - verbs: attack×1
- ENVOYS WAITING 2 · Prussia open borders · Britain settlement offer
- LEDGER treasury 14455 · net -629 · threat 1 · provinces 15 (-1) · ceiling 11062 · army 65164 · vassals Holland 86
  - NET income 1750 · trade 262 · admin 50 · tribute 337 · upkeep 496 · charges 2311 · blockade 131 · admiralty 90
- DISPATCH: Sire — Nivernais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5924 gold.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 24 — Early September 1806
  - MAILBOX #25 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #26 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #25 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #26 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders #25 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #26 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Orleanais into Ile-de-France unopposed! (39 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Orleanais into Ile-de-France unopposed! (39 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Ile-de-France to Champagne. Champagne falls to Britain!
  - verbs: attack×1, move×1
- LEDGER treasury 13477 · net -777 · threat 0 · provinces 13 (-2) · ceiling 9694 · army 64017 · vassals Holland 86
  - NET income 1650 · trade 262 · admin 50 · tribute 337 · upkeep 496 · charges 2359 · blockade 131 · admiralty 90
- DISPATCH: Sire — Ile-de-France has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 3 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Champagne into Artois unopposed! (38 lost to march) Captured: France → Britain · ArchdukeCharles's attack falters disastrously! Brutal stalemate between ArchdukeCharles and Lannes. Heavy casualties on… · ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Ney. Heavy casualties on both…
  - 🏴 Britain: Paget marches from Champagne into Artois unopposed! (38 lost to march) Captured: France → Britain
  - 🏴 Austria: 790 enemy casualties; the pursuit is halted. [!] MARSHAL CAPTURED — Lannes is taken by Austria at Rhineland!
  - ⚔ Archduke Charles (lost 3170) vs Lannes (lost 341, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 2567) vs Ney (lost 1390, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×3
- LEDGER treasury 11635 · net -1088 · threat 0 · provinces 12 (-1) · ceiling 7100 · army 48978 · vassals Holland 86
  - NET income 1472 · trade 262 · admin 50 · tribute 337 · upkeep 376 · charges 2312 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces…
  - RAIL balance_of_europe_shifted: Russian Sphere leads the current largest alignment at 50% of active European bloc power.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Ney. Heavy casualties on both… · ArchdukeCharles attacks with overwhelming force. Brutal stalemate between ArchdukeCharles and Davout. Heavy casualties …
  - ⚔ Archduke Charles (lost 2342) vs Ney (lost 1186, own corps) — Reinforcements from Napoleon bolstered Ney's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 1675) vs Davout (lost 1106, own corps) — Davout fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×2
- ENVOYS WAITING 2 · Britain peace · Austria armistice losing
- LEDGER treasury 10353 · net -778 · threat 0 · provinces 12 (+0) · ceiling 7140 · army 43844 · vassals Holland 86
  - NET income 1446 · trade 262 · admin 50 · tribute 337 · upkeep 328 · charges 2024 · contributions 300 · blockade 131 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Paris. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG balance_of_europe_shifted: Russian Sphere leads the current largest alignment at 50% of active European bloc power.

## Turn 27 — Late October 1806
  - MAILBOX #27 Britain incoming_proposal: Britain — Peace Treaty → activated
  - MAILBOX #28 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, peace #27 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #28 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Britain, peace #27 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #28 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's attack meets fierce resistance. ArchdukeCharles gains the advantage over Ney. Casualties: ArchdukeCha… · ArchdukeCharles holds them at Rhineland while allies attack from Swabia! (+1 coordination)
  - ⚔ Archduke Charles (lost 1611) vs Ney (lost 1160, own corps) — Napoleon arrived to reinforce Ney, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 1137) vs Davout (lost 1257, own corps) — Soult failed to arrive in time. Davout's army fought without expected support.
  - verbs: attack×2
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 9288 · net -599 · threat 0 · provinces 12 (+0) · ceiling 6845 · army 38137 · vassals Holland 82
  - NET income 1408 · trade 262 · admin 50 · tribute 337 · upkeep 288 · charges 1789 · contributions 358 · blockade 131 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG ai_proposal_rejected: We rejected Britain's peace treaty proposal

## Turn 28 — Early November 1806
  - MAILBOX #29 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #29 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 6 actions, 5 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Champagne into Picardy unopposed! (37 lost to march) Captured: France → Britain · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Davout. Casualties: Archd… · Mack attacks with overwhelming force. Brutal stalemate between Mack and Soult. Heavy casualties on both sides: Mack 2,7… · ArchdukeCharles flanks from Rhineland while allies attack from Swabia! (+1 coordination)
  - 🏴 Britain: Paget marches from Champagne into Picardy unopposed! (37 lost to march) Captured: France → Britain
  - 🏴 Austria: Casualties: ArchdukeCharles 820, Davout's army 3,757. Both armies remain in the field. Rhineland has been captured by Austria!
  - ⚔ Archduke Charles (lost 820) vs Davout (lost 1405, own corps) — Napoleon's timely arrival aided Davout. Soult, however, was conspicuously absent.
  - ⚔ Mack (lost 2782) vs Soult (lost 3926) — Neither Soult nor Mack could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1492) vs Soult (lost 2993) — The margin was slim. Training and preparation would serve Soult well.
  - ⚔ Mack (lost 1416) vs Soult (lost 3429) — Soult was close. A period of drilling could have changed the outcome.
  - verbs: attack×5, grant_dotation×1
- ENVOYS WAITING 2 · Hesse non aggression · Britain settlement offer
- LEDGER treasury 8152 · net -324 · threat 0 · provinces 10 (-2) · ceiling 6865 · army 21829 · vassals Holland 76
  - NET income 1219 · trade 262 · admin 50 · tribute 337 · upkeep 152 · charges 1550 · contributions 269 · blockade 131 · admiralty 90
- DISPATCH: Sire — Picardy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3434 gold.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Spain, Sardinia and Holland rebuff Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 29 — Late November 1806
  - MAILBOX #30 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #31 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #30 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #30 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces strike with perfect coordination! ArchdukeCharles gains the advantage over Napoleon. Casualtie… · Mack engages in solid combat. Mack gains the advantage over Davout. Casualties: Mack 221, Davout 1,653. Both armies rem… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Ney. Casualties: Archduke…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Soult is taken by Austria at Lorraine!
  - ⚔ Archduke Charles (lost 321) vs Napoleon (lost 842, own corps) — A grievous defeat for Napoleon, Sire. The losses are severe.
  - ⚔ Mack (lost 221) vs Davout (lost 1653) — A grievous defeat for Davout, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 107) vs Ney (lost 2465) — Ney's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, unfortify×1, move×1
- ORDER Ney [awaiting_response]: Ney is cornered at Lorraine with 2,431 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Lorraine with 2,431 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 7787 · net +71 · threat 0 · provinces 10 (+0) · ceiling 8067 · army 4053 · vassals Holland 70
  - NET income 1169 · trade 262 · admin 50 · tribute 300 · upkeep 24 · charges 1458 · contributions 19 · requisitions 12 · blockade 131 · admiralty 90
- DISPATCH: Sire — Marshal Soult has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 30 — Early December 1806
  - MAILBOX #32 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #32 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 5 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget launches a decisive assault. Paget decisively defeats Davout! Davout's army is destroyed. Paget's army suffered 1… · Shrapnel marches from Orleanais into Ardennes unopposed! (28 lost to march) Captured: France → Britain · Paget holds them at Nivernais while allies attack from Orleanais! (+1 coordination) · ArchdukeCharles marches from Lorraine into Lorraine unopposed! (181 lost to march) Captured: France → Austria
  - 🏴 Britain: Shrapnel marches from Orleanais into Ardennes unopposed! (28 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeCharles marches from Lorraine into Lorraine unopposed! (181 lost to march) Captured: France → Austria
  - ⚔ Paget (lost 92, own corps) vs Davout (lost 3120) — A grievous defeat for Davout, Sire. The losses are severe.
  - ⚔ Paget (lost 38) vs Napoleon (lost 843) — Napoleon was driven from the field. His men are scattered.
  - verbs: attack×4, fortify×1
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 7832 · net +197 · threat 1 · provinces 8 (-2) · ceiling 8716 · army 63 · vassals Holland 68
  - NET income 1100 · trade 262 · admin 50 · tribute 300 · charges 1294 · blockade 131 · admiralty 90
- DISPATCH: Sire — Ardennes has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 31 — Late December 1806
  - MAILBOX #33 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #33 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 1 actions, 1 attacks — Paget delivers an effective strike. Paget decisively defeats Napoleon! Napoleon's army is destroyed. Paget suffered 1 c…
  - 🏴 Britain: Glorious Charge popup next attack. (Recklessness: 3) THE EMPEROR NAPOLEON HAS FALLEN — killed at the head of his corps.
  - ⚔ Paget (lost 1) vs Napoleon (lost 63) — The Emperor himself fell on that field.
  - verbs: attack×1
  - ENDING — THE FALL OF THE EMPIRE: The Emperor is dead. [THE ECLIPSE]
  -     ↳ Late December 1806 (turn 31) · register `fall` · TERMINAL — Load / Main Menu
  -     ↳ THE VERDICT — THE ECLIPSE: The Empire is smaller and more alone than it began. / Its enemies have learned that it can be beaten. / History will call it the beginning of the end.
  -     ↳ The Verdict of History: the eclipse.
  -     ↳ THE RECORD — battles 35 (0 won, 18 lost) · men lost 127,753, inflicted 74,215 · provinces taken 0, lost 20 · marshals fallen 2, taken 6 · coalitions faced 1 · peaces signed 0
  -     ↳ THE EXILE (funeral) — In late December 1806, at Burgundy, the Emperor was killed in the fighting, his corps annihilated by Britain. France has no heir; within the week the Senate declared the Empire at an end. He lay in state in Paris, and the city that had cheered his coronation walked past the bier in silence.
  -     ↳ Some had not lived to see it: Davout at Nivernais had fallen before him. Bernadotte and Lannes were still prisoners of the enemy.
  -     ↳ In 35 battles the Empire won 0 and lost 18; 74,215 of the enemy fell against 127,753 of our own. The Second Battle of Franconia was the worst day. 20 provinces were lost to the enemy; Britain took the most. One coalition stood against him — the Third Coalition.
  -     ↳ The Verdict of History: the eclipse. Berthier closed the last order book and did not open another.
- LEDGER treasury 8027 · net +154 · threat 0 · provinces 8 (+0) · ceiling 8716 · army 0 · vassals Holland 68
  - NET income 1100 · trade 262 · admin 50 · tribute 300 · charges 1337 · blockade 131 · admiralty 90
- DISPATCH: THE EMPEROR IS DEAD. He fell at Burgundy at the head of his corps, which was annihilated by Britain. France has no heir; the Empire dies with him.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - GAME OVER reported — stopping

---
finished: **game-over** · commands 31 · popups 64 · battles 36
