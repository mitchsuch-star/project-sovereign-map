# Playtest digest — PROP-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `88cd6378f016` (dirty) · content `08fe8a7fc9ef` · driver `2cbaf8455dd8`
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
  - LOG ai_ai_proposal_refused: 22 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
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
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia and Naples (open borders agreement)
  - LOG ai_ai_proposal_refused: 24 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
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
  - TURN EVENTS 3
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (open borders agreement)

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
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Russia` → ✗ Talleyrand advises patience, Sire. Russia refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria · Mack attacks with overwhelming force. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 2,… · ArchdukeCharles flanks from Munich while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria
  - ⚔ Mack (lost 2298) vs Lannes (lost 1270, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 1023) vs Lannes (lost 2329, own corps) — Lannes fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×3, wait×1
- LEDGER treasury 8152 · net +1252 · threat 58 · provinces 28 (+0) · ceiling 15780 · army 119531 · vassals Holland 84 · Kingdom of Italy 67 · Switzerland 83
  - NET income 2541 · trade 587 · admin 50 · tribute 617 · upkeep 936 · charges 1008 · contributions 141 · blockade 368 · admiralty 90
- DISPATCH: Sire — Lannes's corps has been broken at Franche-Comte. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +5 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, coercive_demand, agenda_shift)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke… · Mack assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). Mack loses 3,063 troops. Garrison holds — 5,000 … · ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,736 troops in the assa…
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Franche-Comte has been captured by Austria!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -86g, Bavaria -125g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 266) vs Deroy (lost 5648) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt. And Deroy was taken on that field — Austria holds …
  - verbs: attack×3, form_square×1
- LEDGER treasury 9394 · net +1014 · threat 56 · provinces 27 (-1) · ceiling 15456 · army 117982 · vassals Holland 84 · Kingdom of Italy 67 · Switzerland 82
  - NET income 2510 · trade 524 · admin 50 · tribute 622 · upkeep 928 · charges 1236 · contributions 110 · blockade 328 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of 24,246 stands there. A garrison you detach (3,000 men) holds a province against a …
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: Spain rebuffs 4 courts (open borders agreement)

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #15 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,671 troops. Garrison… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,483 troops in the assau…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -74g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - verbs: attack×2, form_square×1, fortify×1
- LEDGER treasury 10289 · net +719 · threat 54 · provinces 27 (+0) · ceiling 14505 · army 116480 · vassals Holland 84 · Kingdom of Italy 67 · Switzerland 81
  - NET income 2510 · trade 524 · admin 50 · tribute 487 · upkeep 912 · charges 1412 · contributions 110 · blockade 328 · admiralty 90
- DISPATCH: Sire — Franche-Comte lies in enemy hands. Austria holds it.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Prussia (open borders agreement)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
  - RATIFIED Russia · PEACE · stalemate
- LEDGER treasury 10957 · net +526 · threat 46 · provinces 26 (-1) · ceiling 13981 · army 115024 · vassals Holland 84 · Kingdom of Italy 67 · Switzerland 80
  - NET income 2470 · trade 536 · admin 50 · tribute 487 · upkeep 888 · charges 1554 · contributions 150 · blockade 335 · admiralty 90
- DISPATCH: Sire — Franche-Comte and Nivernais lie in enemy hands. Austria and Russia hold them.
  - RAIL peace_ratified: Peace ratified between France and Russia.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +7 medium/low (diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, diplomatic_treaty_signed, paymaster_subsidy, balance_of_europe_shifted, agenda_shift)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #17 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 4 actions, 1 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack faces a difficult fight. Mack gains the advantage over Massena. Casualties: Mack 1,326, Massena 3,486. Both armies…
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Piedmont. (311 lost to march) Piedmont has been captured by Austria!
  - ⚔ Mack (lost 1326) vs Massena (lost 3486) — Massena held superior ground, yet Mack prevailed. A grim day, Sire.
  - verbs: move×2, naval_expedition×1, attack×1
- LEDGER treasury 11206 · net +318 · threat 33 · provinces 26 (+0) · ceiling 12972 · army 110125 · vassals Holland 82 · Switzerland 77
  - NET income 2470 · trade 548 · admin 50 · tribute 337 · upkeep 848 · charges 1657 · contributions 150 · blockade 342 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Piedmont. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 3
- DIPLO +5 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×3)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 11 — Late February 1806
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #18 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Mack gains the advantage over Massena. Casualties: Mack 439, Massena 7,057. Both armies r… · Mack marches from Lyonnais into Provence unopposed! (146 lost to march) Captured: France → Austria
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Lyonnais. (148 lost to march) Lyonnais has been captured by Austria!
  - 🏴 Austria: Mack marches from Lyonnais into Provence unopposed! (146 lost to march) Captured: France → Austria
  - ⚔ Mack (lost 439) vs Massena (lost 7057) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: move×2, attack×2, fortify×1
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
- LEDGER treasury 11252 · net +298 · threat 30 · provinces 24 (-2) · ceiling 12907 · army 101698 · vassals Holland 80 · Switzerland 74
  - NET income 2240 · trade 548 · admin 50 · tribute 337 · upkeep 784 · charges 1661 · blockade 342 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 12 — Early March 1806
- CMD `request terms from Britain` → ✓ I shall ask Britain's chancery to name its terms for France + Spain + Holland vs Britain + Austria, Sire. Expect an answer with the next dispatches.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 8 actions, 6 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Savoy unopposed! (222 lost to march) Captured: France → Austria · Mack marches from Provence into Languedoc unopposed! (145 lost to march) Captured: France → Austria · Mack's forces advance steadily. Mack gains the advantage over Massena. Casualties: Mack 271, Massena 3,627. Both armies… · Castanos's forces advance steadily. Brutal stalemate between Castanos and Paget. Heavy casualties on both sides: Castan…
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Savoy unopposed! (222 lost to march) Captured: France → Austria
  - 🏴 Austria: Mack marches from Provence into Languedoc unopposed! (145 lost to march) Captured: France → Austria
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Limousin. (141 lost to march) Limousin has been captured by Austria!
  - ⚔ Mack (lost 271) vs Massena (lost 3627) — Massena's army has been badly mauled. Mack proved the stronger force today.
  - ⚔ Castanos (lost 795) vs Paget (lost 770, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 556) vs Paget (lost 779, own corps) — Paget's aggressive posture left the troops exposed when Castanos's attack came. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 472) vs Wellesley (lost 203, own corps) — The enemy's repeated assaults have leveled our defenses. We fight without cover. — The Line Holds +15% (Wellesley)
  - verbs: attack×6, move×2
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11126 · net +16 · threat 27 · provinces 21 (-3) · ceiling 11209 · army 96742 · vassals Holland 78 · Switzerland 71
  - NET income 1970 · trade 548 · admin 50 · tribute 337 · upkeep 760 · charges 1697 · blockade 342 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 4428 gold.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Ottoman rebuffs Austria (design ask)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: Spain rebuffs Naples, Denmark and Bavaria (open borders agreement)

## Turn 13 — Late March 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #19 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #20 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (4 pairs resolved). Status quo: Franche-Comte, Languedoc, Limousin, Lyonnais, Provence and Savoy stay Austrian by the treaty. Status quo: Andalusia stays British by the treaty. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: break_square×1, stance_change×1, fortify×1, wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 8747 · net +2250 · threat 10 · provinces 21 (+0) · ceiling 196166 · army 105452 · vassals Holland 76 · Switzerland 70
  - NET income 1970 · trade 572 · admin 50 · tribute 562 · upkeep 824 · charges 80
- DISPATCH: Sire — the Emperor's star rises. The Presence stands at +8% this morning, up from where the defeats had left it.
  - RAIL status_quo_conceded: Franche-Comte, Languedoc, Limousin, Lyonnais, Provence and Savoy — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain: Gold indemnity: 4428 gold from France to Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 3
- COURTS: The court of Austria hardens over The Eastern Question — prepared now to go as far as service to the strong.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, coercive_demand, blockade_broken ×3)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 27 to 13.

## Turn 14 — Early April 1806
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #21 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10676 · net +1905 · threat 7 · provinces 21 (+0) · ceiling 169416 · army 104201 · vassals Holland 85 · Switzerland 69
  - NET income 1970 · trade 572 · admin 50 · tribute 225 · upkeep 808 · charges 104
- DISPATCH: Sire — Franche-Comte, Languedoc, Limousin and 4 more lie in enemy hands. Austria and Russia hold them.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_offensive_cascade: Britain has joined Russia's war against Sweden, honoring their alliance.
  - RAIL diplomatic_offensive_cascade: Austria has joined Russia's war against Sweden, honoring their alliance.
  - RAIL broken_bargain: The compact with Sweden lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 2
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_dp_regen, blockade_begins, agenda_shift, diplomatic_relation_shift)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #22 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (69 → 79); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12356 · net +1660 · threat 4 · provinces 21 (+0) · ceiling 150666 · army 102987 · vassals Holland 84 · Switzerland 79
  - NET income 1970 · trade 572 · admin 50 · upkeep 808 · charges 124
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 14032 · net +1656 · threat 1 · provinces 21 (+0) · ceiling 152000 · army 101810 · vassals Holland 83 · Switzerland 79
  - NET income 1970 · trade 572 · admin 50 · upkeep 792 · charges 144
- DISPATCH: Sire — the establishment stands 10,690 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15704 · net +1652 · threat 0 · provinces 21 (+0) · ceiling 153333 · army 100670 · vassals Holland 82 · Switzerland 79
  - NET income 1970 · trade 572 · admin 50 · upkeep 776 · charges 164
- DISPATCH: Sire — Austria and Britain would now join a league against us (relations −75 and −85). The Balance of Europe names the price to keep each out.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Karelia. A new design hardens in their court.
  - TURN EVENTS 1
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, diplomatic_coalition_brewing_other, agenda_shift)
  - LOG coalition_brewing_started: Coalition brewing against Austria — Russia consulting (their alarm: 61)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17356 · net +1632 · threat 0 · provinces 21 (+0) · ceiling 153333 · army 99563 · vassals Holland 81 · Switzerland 79
  - NET income 1970 · trade 572 · admin 50 · upkeep 776 · charges 184
- DISPATCH: Sire — the enemy has held Franche-Comte, Languedoc, Limousin and 4 more 6 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Karelia — Russia is not forgiven

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18996 · net +1621 · threat 0 · provinces 21 (+0) · ceiling 154000 · army 98490 · vassals Holland 80 · Switzerland 79
  - NET income 1970 · trade 572 · admin 50 · upkeep 768 · charges 203
- DISPATCH: Sire — Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 20617 · net +1601 · threat 0 · provinces 21 (+0) · ceiling 154000 · army 97449 · vassals Holland 79 · Switzerland 79
  - NET income 1970 · trade 572 · admin 50 · upkeep 768 · charges 223
- DISPATCH: Sire — Russia, Britain, Austria, Prussia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Prussia: Talleyrand brings her…
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_coalition_formed_other, diplomatic_coalition_dissolved_other)
  - LOG coalition_declared: The Fourth Russian Coalition — Coalition formed against Austria! Members: Russia, Sweden
  - LOG coalition_dissolved: Coalition against Austria has dissolved.

---
finished: **completed** · commands 33 · popups 34 · battles 25
