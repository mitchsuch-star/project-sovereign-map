# Playtest digest — PROP-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `c14678984809` (dirty) · content `d4a1fdd2fc4f` · driver `e498338939cb`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Massena. Heavy casualties o…
  - ⚔ Archduke Charles (lost 4747) vs Massena (lost 5557) — Stalemate. Massena and Archduke Charles glare at each other across the field. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1649 · net +1126 · threat 68 · provinces 28 · ceiling 29330 · army 183443 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · blockade 219 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
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
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles struggles in a costly engagement. Brutal stalemate between Archduke Charles and Massena. Heavy casualt… · Mack struggles in a costly engagement. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5… · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Teulie. Casualties: Archduke C…
  - ⚔ Archduke Charles (lost 4029) vs Massena (lost 4246, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 5198) vs Lannes (lost 2314, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 2839) vs Teulie (lost 1298, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×3, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2472 · net +1426 · threat 66 · provinces 28 (+0) · ceiling 29274 · army 171473 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2575 · trade 450 · admin 50 · tribute 829 · upkeep 2082 · charges 25 · blockade 281 · admiralty 90
- DISPATCH: Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +6 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #8 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Massena. Casualties: Archduke Cha… · Mack struggles in a costly engagement. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Teulie. Casualties: Arc… · Mack struggles in a costly engagement. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack 3,…
  - ⚔ Archduke Charles (lost 2737) vs Massena (lost 4628, own corps) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Mack (lost 4356) vs Lannes (lost 2022, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 1586) vs Teulie (lost 1623, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 3865) vs Murat (lost 3270, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 3,504 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 3,504 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3533 · net +1817 · threat 64 · provinces 28 (+0) · ceiling 29050 · army 154456 · vassals Holland 94 · Kingdom of Italy 89 · Switzerland 88
  - NET income 2551 · trade 525 · admin 50 · tribute 799 · upkeep 1580 · charges 109 · blockade 329 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 2
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #11 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 3,205, Lan… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc… · Mack's forces press forward aggressively. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack… · Mack flanks from Swabia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Mack (lost 3205) vs Lannes (lost 2026, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 1717) vs Bernadotte (lost 4639) — The engagement proceeded as one might expect, Sire.
  - ⚔ Mack (lost 3045) vs Murat (lost 3366, own corps) — Soult failed to arrive in time. Murat's army fought without expected support.
  - ⚔ Mack (lost 1581) vs Bernadotte (lost 3090) — Bernadotte was close. A period of drilling could have changed the outcome.
  - verbs: attack×4
- LEDGER treasury 5171 · net +2039 · threat 62 · provinces 28 (+0) · ceiling 22868 · army 138696 · vassals Holland 90 · Kingdom of Italy 73 · Switzerland 82
  - NET income 2551 · trade 587 · admin 50 · tribute 802 · upkeep 1128 · charges 365 · blockade 368 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 3
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 5 — Late November 1805
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #12 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduk… · Mack's attack falters disastrously! Mack gains the advantage over Bernadotte. Casualties: Mack 2,110, Bernadotte's army… · Mack holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeCharles flanks from Franconia while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Swabia!
  - ⚔ Archduke Charles (lost 524) vs Bernadotte (lost 5615) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 2110) vs Bernadotte (lost 646, own corps) — Ney and Lannes arrived to reinforce Bernadotte, but Soult failed to reach the field in time. And Bernadotte was taken o… — Berthier: the corps marched apart and arrived together.
  - ⚔ Mack (lost 3303) vs Deroy (lost 2600) — Neither Deroy nor Mack could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1691) vs Deroy (lost 4320) — Deroy was close. A period of drilling could have changed the outcome.
  - verbs: attack×4
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 6935 · net +1915 · threat 60 · provinces 28 (+0) · ceiling 22079 · army 127112 · vassals Holland 86 · Kingdom of Italy 69 · Switzerland 76
  - NET income 2553 · trade 587 · admin 50 · tribute 806 · upkeep 1000 · charges 623 · blockade 368 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Russia` → ✗ Talleyrand advises patience, Sire. Russia refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria · Mack attacks with overwhelming force. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 2,… · ArchdukeCharles flanks from Munich while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria
  - ⚔ Mack (lost 2298) vs Lannes (lost 1270, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 926) vs Lannes (lost 2698, own corps) — Lannes fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×3, wait×1
- LEDGER treasury 8127 · net +1253 · threat 58 · provinces 28 (+0) · ceiling 15746 · army 119006 · vassals Holland 84 · Kingdom of Italy 67 · Switzerland 83
  - NET income 2541 · trade 587 · admin 50 · tribute 617 · upkeep 936 · charges 1007 · contributions 141 · blockade 368 · admiralty 90
- DISPATCH: Sire — Lannes's corps has been broken at Franche-Comte. He must reform before he fights again.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +6 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke… · Mack assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). Mack loses 3,063 troops. Garrison holds — 5,000 … · ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,736 troops in the assa…
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Franche-Comte has been captured by Austria!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -86g, Bavaria -125g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 266) vs Deroy (lost 5648) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt. And Deroy was taken on that field — Austria holds …
  - verbs: attack×3, form_square×1
- LEDGER treasury 9374 · net +1019 · threat 56 · provinces 27 (-1) · ceiling 15448 · army 117473 · vassals Holland 84 · Kingdom of Italy 67 · Switzerland 82
  - NET income 2510 · trade 512 · admin 50 · tribute 622 · upkeep 920 · charges 1235 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of 24,336 stands there. A garrison you detach (3,000 men) holds a province against a …
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #15 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,671 troops. Garrison… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,483 troops in the assau…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -74g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - verbs: attack×2, form_square×1, fortify×1
- LEDGER treasury 10274 · net +722 · threat 54 · provinces 27 (+0) · ceiling 14500 · army 115987 · vassals Holland 84 · Kingdom of Italy 67 · Switzerland 81
  - NET income 2510 · trade 512 · admin 50 · tribute 487 · upkeep 904 · charges 1413 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — Franche-Comte lies in enemy hands. Austria holds it.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +5 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Spain rebuffs Prussia (open borders agreement)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
  - RATIFIED Russia · PEACE · stalemate
- LEDGER treasury 10932 · net +517 · threat 46 · provinces 26 (-1) · ceiling 13902 · army 114546 · vassals Holland 84 · Kingdom of Italy 67 · Switzerland 80
  - NET income 2470 · trade 512 · admin 50 · tribute 487 · upkeep 888 · charges 1554 · contributions 150 · blockade 320 · admiralty 90
- DISPATCH: Sire — Franche-Comte and Nivernais lie in enemy hands. Austria and Russia hold them.
  - RAIL peace_ratified: Peace ratified between France and Russia.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 2
- DIPLO +7 medium/low (diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, diplomatic_treaty_signed, paymaster_subsidy, balance_of_europe_shifted, agenda_shift)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 33% of active European bloc power.
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #17 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack faces a difficult fight. Mack gains the advantage over Massena. Casualties: Mack 1,326, Massena 3,486. Both armies…
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Piedmont. (311 lost to march) Piedmont has been captured by Austria!
  - ⚔ Mack (lost 1326) vs Massena (lost 3486) — Massena held superior ground, yet Mack prevailed. A grim day, Sire.
  - verbs: move×2, attack×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11171 · net +311 · threat 33 · provinces 26 (+0) · ceiling 12894 · army 109662 · vassals Holland 82 · Switzerland 77
  - NET income 2470 · trade 512 · admin 50 · tribute 337 · upkeep 848 · charges 1650 · contributions 150 · blockade 320 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Piedmont. He must reform before he fights again.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL settlement_offer_arrival: Britain's terms to settle France vs Britain, under Russia's good offices. Asking 3683 gold.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer, under Russia's good offices → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #19 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (4 pairs resolved). Status quo: Franche-Comte stays Austrian by the treaty. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: break_square×1, stance_change×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 9872 · net +2355 · threat 15 · provinces 26 (+0) · ceiling 206083 · army 118306 · vassals Holland 80 · Switzerland 76
  - NET income 2470 · trade 512 · admin 50 · tribute 337 · upkeep 920 · charges 94
- DISPATCH: Sire — the enemy has held Franche-Comte and Nivernais 4 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL status_quo_conceded: Franche-Comte — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain: Gold indemnity: 3683 gold from France to Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And Austria stirs at its own design.
- DIPLO +6 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 33 to 16.
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 12 — Early March 1806
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (80 → 90); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 11898 · net +2002 · threat 14 · provinces 26 (+0) · ceiling 178666 · army 116990 · vassals Holland 89 · Switzerland 75
  - NET income 2470 · trade 512 · admin 50 · upkeep 912 · charges 118
- DISPATCH: Sire — London now pays St Petersburg 300 gold a turn against us. Her peace with us binds her 2 more turns.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 13908 · net +2211 · threat 13 · provinces 26 (+0) · ceiling 198083 · army 115713 · vassals Holland 88 · Switzerland 74
  - NET income 2470 · trade 512 · admin 50 · tribute 225 · upkeep 904 · charges 142
- DISPATCH: Sire — London now pays Vienna 300 gold a turn against us. Her peace with us binds her 2 more turns.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 34% of active European bloc power.

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 16143 · net +2208 · threat 12 · provinces 26 (+0) · ceiling 200083 · army 114475 · vassals Holland 87 · Switzerland 73
  - NET income 2470 · trade 512 · admin 50 · tribute 225 · upkeep 880 · charges 169
- DISPATCH: Sire — Russia would now join a league against us — relations −67. Britain pays her 300 gold a turn against us. The price to keep her out: Talleyrand brings her to −10 in 7 turns (7 DP); buying off he…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (73 → 83); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 18126 · net +1959 · threat 11 · provinces 26 (+0) · ceiling 181333 · army 113274 · vassals Holland 86 · Switzerland 83
  - NET income 2470 · trade 512 · admin 50 · upkeep 880 · charges 193
- DISPATCH: Sire — Austria and Britain would now join a league against us (relations −75 and −85). The Balance of Europe names the price to keep each out.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 20101 · net +1951 · threat 10 · provinces 26 (+0) · ceiling 182666 · army 112109 · vassals Holland 85 · Switzerland 83
  - NET income 2470 · trade 512 · admin 50 · upkeep 864 · charges 217
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 12,891 men at Paris, and nobody has gone to collect them.
  - TURN EVENTS 1
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22060 · net +1936 · threat 9 · provinces 26 (+0) · ceiling 183333 · army 110979 · vassals Holland 84 · Switzerland 83
  - NET income 2470 · trade 512 · admin 50 · upkeep 856 · charges 240
- DISPATCH: Sire — St Petersburg now pays Vienna 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 7 turns (7 DP); buying off her design …
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 23996 · net +1913 · threat 8 · provinces 26 (+0) · ceiling 183333 · army 109883 · vassals Holland 83 · Switzerland 83
  - NET income 2470 · trade 512 · admin 50 · upkeep 856 · charges 263
- DISPATCH: Sire — the enemy has held Franche-Comte and Nivernais 11 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 25917 · net +2234 · threat 7 · provinces 26 (+0) · ceiling 212083 · army 108820 · vassals Holland 82 · Switzerland 83
  - NET income 2470 · trade 512 · admin 50 · tribute 337 · upkeep 848 · charges 287
- DISPATCH: Sire — the establishment stands 16,180 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 28151 · net +2208 · threat 4 · provinces 26 (+0) · ceiling 212083 · army 107789 · vassals Holland 81 · Switzerland 83
  - NET income 2470 · trade 512 · admin 50 · tribute 337 · upkeep 848 · charges 313
- DISPATCH: Sire — the enemy has held Franche-Comte and Nivernais 13 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 31 · popups 31 · battles 20
