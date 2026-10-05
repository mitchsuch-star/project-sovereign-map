# Playtest digest — PROP-M

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `88cd6378f016` (dirty) · content `08fe8a7fc9ef` · driver `2cbaf8455dd8`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke Ch…
  - ⚔ Archduke Charles (lost 1908) vs Bernadotte (lost 6282) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 1684 · net +1198 · threat 64 · provinces 28 · ceiling 29227 · army 182608 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2420 · blockade 219 · admiralty 90
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
- LEDGER treasury 2772 · net +1553 · threat 62 · provinces 28 (+0) · ceiling 31301 · army 170305 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 93
  - NET income 2590 · trade 425 · admin 50 · tribute 937 · upkeep 2052 · charges 41 · blockade 266 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 22 approaches from Bavaria and Prussia are rebuffed (open borders agreement)
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
- LEDGER treasury 4572 · net +1827 · threat 70 · provinces 29 (+1) · ceiling 24252 · army 153073 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 90
  - NET income 2590 · trade 424 · admin 50 · tribute 937 · upkeep 1506 · charges 238 · occupation 75 · blockade 265 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Prussia (open borders agreement)
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
- LEDGER treasury 6350 · net +1461 · threat 68 · provinces 30 (+1) · ceiling 21562 · army 146554 · vassals Holland 97 · Switzerland 89
  - NET income 2621 · trade 511 · admin 50 · tribute 562 · upkeep 1304 · charges 417 · occupation 152 · blockade 320 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is destroyed at Franconia — his corps annihilated, his name struck from their order of battle.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,164g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +8 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (155 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (155 lost to march) Captured: France → Austria
  - verbs: move×1, attack×1, stance_change×1
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7989 · net +1347 · threat 66 · provinces 29 (-1) · ceiling 21566 · army 141405 · vassals Holland 97 · Switzerland 87
  - NET income 2502 · trade 536 · admin 50 · tribute 562 · upkeep 1162 · charges 594 · occupation 122 · blockade 335 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL crisis_passed: Prussia stands down over Hanover, Sire — the moment passed — opportunism decayed.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

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
- LEDGER treasury 8955 · net +848 · threat 63 · provinces 27 (-2) · ceiling 17234 · army 136680 · vassals Holland 97 · Switzerland 96
  - NET income 2380 · trade 536 · admin 50 · tribute 337 · upkeep 1108 · charges 712 · contributions 110 · occupation 100 · blockade 335 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 5
- DIPLO +5 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✗ Talleyrand advises patience, Sire. Austria refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Limousin into Berry unopposed! (150 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Limousin into Berry unopposed! (150 lost to march) Captured: France → Austria
  - verbs: attack×1
- LEDGER treasury 10101 · net +1037 · threat 60 · provinces 26 (-1) · ceiling 23812 · army 132331 · vassals Holland 97 · Switzerland 95
  - NET income 2297 · trade 536 · admin 50 · tribute 337 · upkeep 1076 · charges 612 · occupation 70 · blockade 335 · admiralty 90
- DISPATCH: Sire — Berry has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Normandy garrison! Garrison collapses (7,300 -> 0). ArchdukeJohn loses 2,253 troops in the as… · ArchdukeJohn marches from Normandy into Artois unopposed! (92 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -112g, France -164g. Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Normandy into Artois unopposed! (92 lost to march) Captured: France → Austria
  - verbs: attack×2
- LEDGER treasury 10617 · net +813 · threat 57 · provinces 24 (-2) · ceiling 20246 · army 128314 · vassals Holland 97 · Switzerland 94
  - NET income 2152 · trade 536 · admin 50 · tribute 337 · upkeep 1040 · charges 727 · occupation 70 · blockade 335 · admiralty 90
- DISPATCH: Sire — Normandy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #17 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 4 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Normandy into Maine unopposed! (859 lost to march) Captured: France → Britain · ArchdukeJohn marches from Artois into Champagne unopposed! (91 lost to march) Captured: France → Austria · ArchdukeCharles marches from Munich into Franche-Comte unopposed! (1,125 lost to march) Captured: France → Austria
  - 🏴 Britain: Moore marches from Normandy into Maine unopposed! (859 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeJohn marches from Artois into Champagne unopposed! (91 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Munich into Franche-Comte unopposed! (1,125 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn moves from Champagne to Burgundy. Burgundy falls to Austria!
  - verbs: attack×3, move×1
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
  - RATIFIED Russia · PEACE · white_peace
- LEDGER treasury 11259 · net +558 · threat 54 · provinces 20 (-4) · ceiling 17627 · army 124595 · vassals Holland 97 · Switzerland 93
  - NET income 1953 · trade 548 · admin 50 · tribute 337 · upkeep 1032 · charges 811 · occupation 55 · blockade 342 · admiralty 90
- DISPATCH: Sire — Maine has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL peace_ratified: Peace ratified between France and Russia.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_proposal_sent, enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, diplomatic_treaty_signed, paymaster_subsidy)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `request terms from Britain` → ✓ I shall ask Britain's chancery to name its terms for France + Spain + Holland vs Britain + Austria, Sire. Expect an answer with the next dispatches.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 4 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Maine into Anjou unopposed! (785 lost to march) Captured: France → Britain · Moore marches from Anjou into Guyenne unopposed! (720 lost to march) Captured: France → Britain · ArchdukeCharles marches from Franche-Comte into Nivernais unopposed! (1,091 lost to march) Captured: France → Austria · ArchdukeJohn marches from Burgundy into Savoy unopposed! (179 lost to march) Captured: France → Austria
  - 🏴 Britain: Moore marches from Maine into Anjou unopposed! (785 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Anjou into Guyenne unopposed! (720 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeCharles marches from Franche-Comte into Nivernais unopposed! (1,091 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Burgundy into Savoy unopposed! (179 lost to march) Captured: France → Austria
  - verbs: attack×4
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11139 · net -135 · threat 51 · provinces 16 (-4) · ceiling 10013 · army 121142 · vassals Holland 97 · Switzerland 92
  - NET income 1654 · trade 548 · admin 50 · tribute 337 · upkeep 1044 · charges 1103 · contributions 110 · occupation 35 · blockade 342 · admiralty 90
- DISPATCH: Sire — Anjou has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,188g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #19 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (4 pairs resolved). Status quo: Anjou, Guyenne and Maine stay British by the treaty. Status quo: Franconia and Swabia stay ours by the treaty — titled. Status quo: Artois, Berry, Burgundy, Champagne, Franche-Comte, Limousin, Lyonnais, Nivernais, Normandy, Provence and Savoy stay Austrian by the treaty. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout marches to Swabia. 5 regions to Paris.
- ORDER Dumonceau [continues]: Dumonceau marches to Flanders. 3 regions to Paris.
- ORDER Lannes [continues]: Lannes marches to Swabia. 5 regions to Paris.
- ORDER Massena [continues]: Massena marches to Swabia. 5 regions to Paris.
- ORDER Murat [continues]: Murat marches to Lorraine. 4 regions to Paris.
- ORDER Napoleon [continues]: Napoleon marches to Swabia. 5 regions to Paris.
- ORDER Ney [continues]: Ney marches to Lorraine. 4 regions to Paris.
- ORDER Soult [continues]: Soult marches to Orleanais. 3 regions to Paris.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 12551 · net +1395 · threat 23 · provinces 16 (+0) · ceiling 128750 · army 124463 · vassals Holland 95 · Switzerland 91
  - NET income 1661 · trade 572 · admin 50 · tribute 337 · upkeep 1064 · charges 126 · occupation 35
- DISPATCH: Sire — Anjou, Artois, Berry and 11 more lie in enemy hands. Britain and Austria hold them.
  - RAIL status_quo_conceded: Anjou, Guyenne and Maine — left with Britain by the peace, titled to them by treaty.
  - RAIL status_quo_conceded: Artois, Berry, Burgundy, Champagne, Franche-Comte, Limousin, Lyonnais, Nivernais, Normandy, Provence and Savoy — left with Austria by the peace, titl…
  - RAIL settlement_summary: Settlement of France vs Austria + Britain: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 2
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: And Russia stirs at its own design.
- DIPLO +8 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent, coercive_demand, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 51 to 25.
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (open borders agreement)

## Turn 12 — Early March 1806
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +5 (95 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout marches to Lorraine. 4 regions to Paris.
- ORDER Dumonceau [completed]: Dumonceau arrives at Amsterdam. Dumonceau: "Accomplished as ordered. The army is intact."
- ORDER Lannes [continues]: Lannes marches to Lorraine. 4 regions to Paris.
- ORDER Massena [continues]: Massena marches to Lorraine. 4 regions to Paris.
- ORDER Murat [continues]: Murat marches to Burgundy. 2 regions to Paris.
- ORDER Napoleon [continues]: Napoleon marches to Lorraine. 4 regions to Paris.
- ORDER Ney [continues]: Ney marches to Orleanais. 3 regions to Paris.
- ORDER Soult [continues]: Soult marches to Burgundy. 2 regions to Paris.
- LEDGER treasury 13664 · net +1100 · threat 21 · provinces 16 (+0) · ceiling 105250 · army 120250 · vassals Holland 99 · Switzerland 90
  - NET income 1668 · trade 572 · admin 50 · upkeep 1016 · charges 139 · occupation 35
- DISPATCH: Sire — Prussia would now join a league against us — relations −25. The price to keep her out: Talleyrand brings her to −10 in 2 turns (2 DP); buying off her design costs 1,296 gold.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,188g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 1
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +6 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, diplomatic_relation_shift)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout marches to Orleanais. 3 regions to Paris.
- ORDER Lannes [continues]: Lannes marches to Orleanais. 3 regions to Paris.
- ORDER Massena [continues]: Massena marches to Orleanais. 3 regions to Paris.
- ORDER Murat [completed]: Murat arrives at Paris. Murat: "Done — and I trust the next order has more fire in it."
- ORDER Napoleon [continues]: Napoleon marches to Orleanais. 3 regions to Paris.
- ORDER Ney [continues]: Ney marches to Burgundy. 2 regions to Paris.
- ORDER Soult [continues]: Soult marches to Limousin. 1 region to Paris.
- LEDGER treasury 14804 · net +1351 · threat 19 · provinces 16 (+0) · ceiling 127333 · army 117355 · vassals Holland 98 · Switzerland 89
  - NET income 1672 · trade 572 · admin 50 · tribute 225 · upkeep 980 · charges 153 · occupation 35
- DISPATCH: Sire — 3 turns now with Anjou, Artois, Berry and 11 more in enemy hands. The country counts every one of them.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, coercive_demand)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout marches to Burgundy. 2 regions to Paris.
- ORDER Lannes [continues]: Lannes marches to Burgundy. 2 regions to Paris.
- ORDER Massena [continues]: Massena marches to Burgundy. 2 regions to Paris.
- ORDER Napoleon [continues]: Napoleon marches to Burgundy. 2 regions to Paris.
- ORDER Ney [continues]: Ney marches to Limousin. 1 region to Paris.
- ORDER Soult [completed]: The order was "the road home — safe passage granted by the peace". Soult arrives at Paris. I await further instruction.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 16207 · net +1386 · threat 17 · provinces 16 (+0) · ceiling 131666 · army 113474 · vassals Holland 97 · Switzerland 88
  - NET income 1676 · trade 572 · admin 50 · tribute 225 · upkeep 932 · charges 170 · occupation 35
- DISPATCH: Sire — General Paget of Britain is destroyed at Gascony — his corps annihilated, his name struck from their order of battle.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_offensive_cascade: Austria has joined Russia's war against Sweden, honoring their alliance.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 1
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- DIPLO +5 medium/low (diplomatic_dp_regen, blockade_begins, agenda_shift ×2, diplomatic_relation_shift)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout marches to Limousin. 1 region to Paris.
- ORDER Lannes [continues]: Lannes marches to Limousin. 1 region to Paris.
- ORDER Massena [continues]: Massena marches to Limousin. 1 region to Paris.
- ORDER Napoleon [continues]: Napoleon marches to Limousin. 1 region to Paris.
- ORDER Ney [completed]: Ney arrives at Paris. Ney: "Done — and I trust the next order has more fire in it."
- LEDGER treasury 17436 · net +1214 · threat 15 · provinces 16 (+0) · ceiling 118583 · army 109489 · vassals Holland 96 · Switzerland 98
  - NET income 1680 · trade 572 · admin 50 · upkeep 868 · charges 185 · occupation 35
- DISPATCH: Sire — Austria and Britain would now join a league against us (relations −75 and −85). The Balance of Europe names the price to keep each out.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,222 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 2
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [completed]: Davout arrives at Paris. Davout: "Accomplished as ordered. The army is intact."
- ORDER Lannes [completed]: Lannes arrives at Paris. Lannes: "It is done. Point me at something that shoots back, Sire."
- ORDER Massena [completed]: Massena arrives at Paris. Massena: "Accomplished. The men want a battle, not another road."
- ORDER Napoleon [completed]: Napoleon arrives at Paris.
- LEDGER treasury 18730 · net +1279 · threat 13 · provinces 16 (+0) · ceiling 125250 · army 102922 · vassals Holland 95 · Switzerland 98
  - NET income 1684 · trade 572 · admin 50 · upkeep 792 · charges 200 · occupation 35
- DISPATCH: Sire — Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena and Napoleon stand 102,922 men at Paris, which feeds 75,000. 27,922 too many. 8,543 men lost in 2 turns. A supply depot at Paris would ea…
  - TURN EVENTS 1
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 20061 · net +1315 · threat 11 · provinces 16 (+0) · ceiling 129583 · army 96751 · vassals Holland 94 · Switzerland 98
  - NET income 1688 · trade 572 · admin 50 · upkeep 744 · charges 216 · occupation 35
- DISPATCH: Sire — Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena and Napoleon stand 96,751 men at Paris, which feeds 75,000. 21,751 too many. 14,714 men lost in 3 turns. A supply depot at Paris would ea…
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21428 · net +1350 · threat 9 · provinces 16 (+0) · ceiling 133916 · army 90950 · vassals Holland 93 · Switzerland 98
  - NET income 1692 · trade 572 · admin 50 · upkeep 696 · charges 233 · occupation 35
- DISPATCH: Sire — the court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
  - TURN EVENTS 1
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22830 · net +1723 · threat 7 · provinces 16 (+0) · ceiling 166333 · army 85497 · vassals Holland 92 · Switzerland 98
  - NET income 1696 · trade 572 · admin 50 · tribute 337 · upkeep 648 · charges 249 · occupation 35
- DISPATCH: Sire — Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena and Napoleon have been 5 turns over what Paris can feed. 17,425 men dead. The country will ask where the army went. A supply depot at Par…
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 24597 · net +1745 · threat 4 · provinces 16 (+0) · ceiling 170000 · army 80371 · vassals Holland 91 · Switzerland 98
  - NET income 1700 · trade 572 · admin 50 · tribute 337 · upkeep 608 · charges 271 · occupation 35
- DISPATCH: Sire — Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena and Napoleon have been 6 turns over what Paris can feed. 16,380 men dead. The country will ask where the army went. A supply depot at Par…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 31 · popups 33 · battles 6
