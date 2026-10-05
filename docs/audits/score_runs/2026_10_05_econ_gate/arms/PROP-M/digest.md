# Playtest digest — PROP-M

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `47eb92ffc944` (dirty) · content `aae077cedc7a` · driver `e498338939cb`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke Ch…
  - ⚔ Archduke Charles (lost 1908) vs Bernadotte (lost 6282) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 1564 · net +1078 · threat 64 · provinces 28 · ceiling 26500 · army 182608 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2540 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 6,282 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #4 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's attack falters disastrously! Archduke Charles gains the advantage over Bernadotte. Casualties: Archd… · Mack launches a decisive assault. Bernadotte holds the line. Casualties: Mack 8,885, Bernadotte's army 4,565. Both armi…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 708) vs Bernadotte (lost 5573) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Mack (lost 8885) vs Bernadotte (lost 500, own corps) — Lannes, Massena and Teulie's timely arrival bolstered Bernadotte's position. Well-coordinated, Sire. — Berthier: the corps marched apart and arrived together.
  - verbs: attack×2, move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 1968 · net +910 · threat 62 · provinces 28 (+0) · ceiling 18727 · army 170305 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 93
  - NET income 2590 · trade 425 · admin 50 · tribute 937 · upkeep 2736 · blockade 266 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 24 approaches from Bavaria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #7 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke … · ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,685 troops in the assa…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Munich!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -84g, Bavaria -125g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 118) vs Bernadotte (lost 2667) — The hills were ours, but Archduke Charles took them. Bernadotte's position was overrun. And Bernadotte was taken on tha…
  - verbs: attack×2, stance_change×1, unfortify×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1592, own corps) vs Mack (lost 29631) — Reinforcements from Ney, Davout, Lannes, Massena, Napoleon and Teulie bolstered Murat's position — though Soult never a… — The corps system brought Lannes in. — The corps system brought Teulie in. — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Swabia, Murat → secure
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 3807 · net +1893 · threat 70 · provinces 29 (+1) · ceiling 24198 · army 153073 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 90
  - NET income 2590 · trade 412 · admin 50 · tribute 937 · upkeep 1506 · charges 167 · occupation 75 · blockade 258 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 12 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #11 → confirm
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 85, own corps) vs Mack (lost 13417) — Davout, Murat, Massena, Napoleon and Teulie's timely arrival aided Lannes. Ney, however, was conspicuously absent.
  - POPUP capture_choice[capture]: Franconia, Lannes → secure
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 5647 · net +1519 · threat 68 · provinces 30 (+1) · ceiling 21468 · army 146554 · vassals Holland 97 · Switzerland 89
  - NET income 2621 · trade 487 · admin 50 · tribute 562 · upkeep 1304 · charges 350 · occupation 152 · blockade 305 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is destroyed at Franconia — his corps annihilated, his name struck from their order of battle.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,164g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +8 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (155 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (155 lost to march) Captured: France → Austria
  - verbs: attack×1
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7344 · net +1402 · threat 66 · provinces 29 (-1) · ceiling 21475 · army 141405 · vassals Holland 97 · Switzerland 87
  - NET income 2502 · trade 512 · admin 50 · tribute 562 · upkeep 1162 · charges 530 · occupation 122 · blockade 320 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL crisis_passed: Prussia stands down over Hanover, Sire — the moment passed — opportunism decayed.
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG ai_ai_proposal_refused: 13 approaches from Bavaria and Prussia are rebuffed (open borders agreement)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign a Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign a Open Borders Agreement

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #15 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Russia` → ✗ Talleyrand advises patience, Sire. Russia refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Provence into Lyonnais unopposed! (153 lost to march) Captured: France → Austria · ArchdukeJohn marches from Lyonnais into Limousin unopposed! (152 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Lyonnais unopposed! (153 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Limousin unopposed! (152 lost to march) Captured: France → Austria
  - verbs: attack×2
  - POPUP marshal_audience: shadow_command, Marshal Davout asks for a command → detach
  -     ↳ Davout straightens. "You will not regret it, Sire." March him to Franconia and the front is his — the order i…
- LEDGER treasury 8365 · net +900 · threat 63 · provinces 27 (-2) · ceiling 17146 · army 136680 · vassals Holland 97 · Switzerland 96
  - NET income 2380 · trade 512 · admin 50 · tribute 337 · upkeep 1108 · charges 651 · contributions 110 · occupation 100 · blockade 320 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 5
- DIPLO +5 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✗ Talleyrand advises patience, Sire. Austria refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Lyonnais into Savoy unopposed! (298 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Savoy unopposed! (298 lost to march) Captured: France → Austria
  - verbs: attack×1
- LEDGER treasury 9615 · net +1135 · threat 60 · provinces 26 (-1) · ceiling 24619 · army 132331 · vassals Holland 97 · Switzerland 95
  - NET income 2367 · trade 512 · admin 50 · tribute 337 · upkeep 1076 · charges 575 · occupation 70 · blockade 320 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10811 · net +1077 · threat 57 · provinces 26 (+0) · ceiling 24474 · army 128314 · vassals Holland 97 · Switzerland 94
  - NET income 2372 · trade 512 · admin 50 · tribute 337 · upkeep 1020 · charges 694 · occupation 70 · blockade 320 · admiralty 90
- DISPATCH: Sire — Limousin, Lyonnais, Provence and 1 more lie in enemy hands. Austria holds them.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #17 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Russia peace
- LEDGER treasury 11574 · net +649 · threat 54 · provinces 26 (+0) · ceiling 17366 · army 124595 · vassals Holland 97 · Switzerland 93
  - NET income 2413 · trade 512 · admin 50 · tribute 337 · upkeep 976 · charges 1072 · contributions 150 · occupation 55 · blockade 320 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Berry. No French corps stands in his path.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_proposal_sent, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 12 approaches from Bavaria and Prussia are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #9 Russia counter_offer_response: Russia — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Russia, peace #18 → accept
  - POPUP proposal_result: You have accepted Russia's counter-proposal. Treaty signed: At War → Peace with Russia. → display-only
  - RATIFIED Russia · PEACE · stalemate
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #19 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 12123 · net +632 · threat 51 · provinces 26 (+0) · ceiling 17607 · army 121142 · vassals Holland 97 · Switzerland 92
  - NET income 2454 · trade 512 · admin 50 · tribute 337 · upkeep 960 · charges 1166 · contributions 150 · occupation 35 · blockade 320 · admiralty 90
- DISPATCH: Sire — 3 turns now with Limousin, Lyonnais, Provence and 1 more in enemy hands. The country counts every one of them.
  - RAIL peace_ratified: Peace ratified between France and Russia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,188g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_treaty_signed, diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 14 approaches from Russia and Prussia are rebuffed (defensive alliance)
  - LOG coalition_member_left: Russia has left the coalition.

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #21 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (4 pairs resolved). Status quo: Franconia and Swabia stay ours by the treaty — titled. Status quo: Limousin, Lyonnais, Provence and Savoy stay Austrian by the treaty. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14367 · net +2217 · threat 24 · provinces 26 (+0) · ceiling 199083 · army 122926 · vassals Holland 95 · Switzerland 91
  - NET income 2461 · trade 512 · admin 50 · tribute 337 · upkeep 960 · charges 148 · occupation 35
- DISPATCH: Sire — Davout, Lannes, Murat, Massena and Napoleon have been 6 turns over what Franconia can feed. 10,388 men dead. The country will ask where the army went. Living off the land: this stripped countr…
  - RAIL status_quo_conceded: Limousin, Lyonnais, Provence and Savoy — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 2
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, status_quo_titled, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_vassal_contingent, coercive_demand, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 51 to 25.

## Turn 12 — Early March 1806
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +5 (95 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16278 · net +1888 · threat 23 · provinces 26 (+0) · ceiling 173583 · army 119928 · vassals Holland 99 · Switzerland 90
  - NET income 2468 · trade 512 · admin 50 · upkeep 936 · charges 171 · occupation 35
- DISPATCH: Sire — Davout, Lannes, Murat, Massena and Napoleon have been 6 turns over what Franconia can feed. 9,667 men dead. The country will ask where the army went. A supply depot at Franconia would ease it;…
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 1
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18186 · net +2110 · threat 22 · provinces 26 (+0) · ceiling 194000 · army 117371 · vassals Holland 98 · Switzerland 89
  - NET income 2472 · trade 512 · admin 50 · tribute 225 · upkeep 920 · charges 194 · occupation 35
- DISPATCH: Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: 8 courts rebuff Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Bavaria (open borders agreement)

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Yorck assaults the Hanover garrison! Garrison collapses (5,000 -> 0). Yorck loses 1,052 troops in the assault. Yorck ma…
  - 🏴 Prussia: [Materiel] Guns, horses and stores lost with the fallen: Prussia -52g, Hanover -103g. Captured: Hanover → Prussia
  - verbs: attack×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 20324 · net +2113 · threat 21 · provinces 26 (+0) · ceiling 196333 · army 114957 · vassals Holland 97 · Switzerland 88
  - NET income 2476 · trade 512 · admin 50 · tribute 225 · upkeep 896 · charges 219 · occupation 35
- DISPATCH: Sire — Russia would now join a league against us — relations −75. Britain pays her 400 gold a turn against us. The price to keep her out: Talleyrand brings her to −10 in 8 turns (8 DP); buying off he…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 15 — Late April 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #23 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22232 · net +1885 · threat 20 · provinces 26 (+0) · ceiling 179250 · army 112643 · vassals Holland 96 · Switzerland 98
  - NET income 2480 · trade 512 · admin 50 · upkeep 880 · charges 242 · occupation 35
- DISPATCH: Sire — Austria and Britain would now join a league against us (relations −75 and −85). The Balance of Europe names the price to keep each out.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,294 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24145 · net +1890 · threat 19 · provinces 26 (+0) · ceiling 181583 · army 110423 · vassals Holland 95 · Switzerland 98
  - NET income 2484 · trade 512 · admin 50 · upkeep 856 · charges 265 · occupation 35
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 14,577 men at Paris, and nobody has gone to collect them.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26047 · net +1879 · threat 18 · provinces 26 (+0) · ceiling 182583 · army 108291 · vassals Holland 94 · Switzerland 98
  - NET income 2488 · trade 512 · admin 50 · upkeep 848 · charges 288 · occupation 35
- DISPATCH: Sire — St Petersburg now pays Vienna 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 7 turns (7 DP); buying off her design …
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 27946 · net +1876 · threat 17 · provinces 26 (+0) · ceiling 184250 · army 106245 · vassals Holland 93 · Switzerland 98
  - NET income 2492 · trade 512 · admin 50 · upkeep 832 · charges 311 · occupation 35
- DISPATCH: Sire — the enemy has held Limousin, Lyonnais, Provence and 1 more 11 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 1
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 29842 · net +2210 · threat 16 · provinces 26 (+0) · ceiling 214000 · army 104281 · vassals Holland 92 · Switzerland 98
  - NET income 2496 · trade 512 · admin 50 · tribute 337 · upkeep 816 · charges 334 · occupation 35
- DISPATCH: Sire — the establishment stands 20,719 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 32080 · net +2212 · threat 13 · provinces 26 (+0) · ceiling 216333 · army 102395 · vassals Holland 91 · Switzerland 98
  - NET income 2500 · trade 512 · admin 50 · tribute 337 · upkeep 792 · charges 360 · occupation 35
- DISPATCH: Sire — the enemy has held Limousin, Lyonnais, Provence and 1 more 13 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 31 · popups 37 · battles 6
