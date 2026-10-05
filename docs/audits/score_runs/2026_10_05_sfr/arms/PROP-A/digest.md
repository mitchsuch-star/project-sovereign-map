# Playtest digest — PROP-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke Ch…
  - ⚔ Archduke Charles (lost 1753) vs Bernadotte (lost 6674) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1665 · net +1198 · threat 67 · provinces 28 · ceiling 29227 · army 182221 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2420 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 6,674 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #5 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke … · Mack's assault collapses into chaos! Bernadotte holds the line. Casualties: Mack 8,540, Bernadotte's army 3,847. Both a…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 550) vs Bernadotte (lost 5652) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Mack (lost 8540) vs Bernadotte (lost 386, own corps) — Lannes, Massena and Teulie's timely arrival bolstered Bernadotte's position. Well-coordinated, Sire. — Berthier: the corps marched apart and arrived together.
  - verbs: attack×2, move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2855 · net +1558 · threat 70 · provinces 28 (+0) · ceiling 31485 · army 170482 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 937 · upkeep 2052 · charges 46 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte, crowned last turn, has been hunted across the frontier by Archduke Charles.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 22 approaches from Bavaria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #8 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc… · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,777 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,562 troops in the…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Munich!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -78g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - ⚔ Archduke Charles (lost 843) vs Bernadotte (lost 2406, own corps) — The hills were ours, but Archduke Charles took them. Bernadotte's position was overrun. And Bernadotte was taken on tha…
  - verbs: attack×3, stance_change×1
- ORDER Teulie [awaiting_response]: Teulie is cornered at Munich with 3,712 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1657, own corps) vs Mack (lost 28658) — Reinforcements from Ney, Davout, Lannes, Massena and Napoleon bolstered Murat's position — though Soult and Teulie neve… — The corps system brought Lannes in. — Berthier: the corps marched apart and arrived together.
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Munich with 3,712 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP capture_choice[capture]: Swabia, Murat → secure
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4294 · net +1651 · threat 78 · provinces 29 (+1) · ceiling 21632 · army 153352 · vassals Holland 96 · Kingdom of Italy 91 · Switzerland 90
  - NET income 2590 · trade 525 · admin 50 · tribute 712 · upkeep 1514 · charges 218 · occupation 75 · blockade 329 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 24 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #12 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,063 troops. G… · ArchdukeCharles assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,702 troops in th… · ArchdukeCharles marches from Munich into Franche-Comte unopposed! (997 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -85g, Bavaria -125g. Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles marches from Munich into Franche-Comte unopposed! (997 lost to march) Captured: France → Austria
  - verbs: attack×3, move×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 69, own corps) vs Mack (lost 13735) — Ney, Davout, Murat, Massena and Napoleon's timely arrival bolstered Lannes's position. Well-coordinated, Sire. — The corps system brought Murat in.
  - POPUP capture_choice[capture]: Franconia, Lannes → secure
- LEDGER treasury 6189 · net +1562 · threat 86 · provinces 29 (+0) · ceiling 21989 · army 145474 · vassals Holland 97 · Kingdom of Italy 80 · Switzerland 89
  - NET income 2541 · trade 524 · admin 50 · tribute 712 · upkeep 1282 · charges 413 · occupation 152 · blockade 328 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps sta…
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 6
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×1
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7982 · net +1596 · threat 84 · provinces 29 (+0) · ceiling 23627 · army 138549 · vassals Holland 97 · Kingdom of Italy 80 · Switzerland 87
  - NET income 2572 · trade 524 · admin 50 · tribute 712 · upkeep 1112 · charges 610 · occupation 122 · blockade 328 · admiralty 90
- DISPATCH: Sire — Franche-Comte lies in enemy hands. Austria holds it.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #15 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Russia` → ✗ Talleyrand advises patience, Sire. Russia refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: shadow_command, Marshal Ney asks for a command → detach
  -     ↳ Ney straightens. "You will not regret it, Sire." March him to Franconia and the front is his — the order is y…
- LEDGER treasury 9325 · net +1183 · threat 82 · provinces 29 (+0) · ceiling 20564 · army 132038 · vassals Holland 97 · Kingdom of Italy 80 · Switzerland 96
  - NET income 2574 · trade 524 · admin 50 · tribute 487 · upkeep 1032 · charges 770 · contributions 110 · occupation 122 · blockade 328 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,212g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 8 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
  - POPUP marshal_audience: shadow_command, Marshal Davout asks for a command → detach
  -     ↳ Davout straightens. "You will not regret it, Sire." March him to Franconia and the front is his — the order i…
- LEDGER treasury 10659 · net +1166 · threat 80 · provinces 29 (+0) · ceiling 21409 · army 125918 · vassals Holland 97 · Kingdom of Italy 80 · Switzerland 95
  - NET income 2639 · trade 524 · admin 50 · tribute 487 · upkeep 976 · charges 938 · contributions 110 · occupation 92 · blockade 328 · admiralty 90
- DISPATCH: Sire — 3 turns now with Franche-Comte in enemy hands. The country counts every one of them.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_proposal_sent, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #17 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 11861 · net +1040 · threat 78 · provinces 29 (+0) · ceiling 21175 · army 120166 · vassals Holland 97 · Kingdom of Italy 80 · Switzerland 94
  - NET income 2643 · trade 524 · admin 50 · tribute 487 · upkeep 944 · charges 1100 · contributions 110 · occupation 92 · blockade 328 · admiralty 90
- DISPATCH: Sire — Prussia would now join a league against us — relations −25. Courtship needs 2 turns; a league stands declared. She will march.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 2
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #18 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Russia peace
- LEDGER treasury 12997 · net +974 · threat 76 · provinces 29 (+0) · ceiling 21477 · army 114758 · vassals Holland 97 · Kingdom of Italy 80 · Switzerland 93
  - NET income 2717 · trade 524 · admin 50 · tribute 487 · upkeep 904 · charges 1262 · contributions 150 · occupation 70 · blockade 328 · admiralty 90
- DISPATCH: Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #9 Russia counter_offer_response: Russia — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Russia, peace #19 → accept
  - POPUP proposal_result: You have accepted Russia's counter-proposal. Treaty signed: At War → Peace with Russia. → display-only
  - RATIFIED Russia · PEACE · stalemate
- CMD `propose peace with Austria` → ✗ Talleyrand advises patience, Sire. Austria refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: naval_expedition×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13554 · net +987 · threat 74 · provinces 29 (+0) · ceiling 21915 · army 109675 · vassals Holland 97 · Kingdom of Italy 80 · Switzerland 92
  - NET income 2758 · trade 536 · admin 50 · tribute 487 · upkeep 856 · charges 1363 · contributions 150 · occupation 50 · blockade 335 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL peace_ratified: Peace ratified between France and Russia.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 3105 gold.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #21 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (5 pairs resolved). Status quo: Franconia and Swabia stay ours by the treaty — titled. Status quo: Franche-Comte stays Austrian by the treaty. Status quo: Andalusia stays British by the treaty. Status quo: Milan stays Austrian by the treaty. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +5 (95 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 19399 · net +2370 · threat 40 · provinces 29 (+0) · ceiling 216833 · army 114907 · vassals Holland 100 · Kingdom of Italy 78 · Switzerland 91
  - NET income 2764 · trade 560 · admin 50 · tribute 150 · upkeep 896 · charges 208 · occupation 50
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Napoleon have been 6 turns over what Franconia can feed. 15,259 men dead. The country will ask where the army went. Living off the land: this stripped c…
  - RAIL status_quo_conceded: Franche-Comte — left with Austria by the peace, titled to them by treaty.
  - RAIL status_quo_conceded: Milan — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain: Gold indemnity: 3105 gold from Britain to France.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,351 gold. Prussia is now free to look elsewhere.
  - RAIL +3 more
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Primacy in Germany — service to the strong is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift ×2)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 74 to 37.

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 21815 · net +2387 · threat 43 · provinces 29 (+0) · ceiling 220666 · army 110536 · vassals Holland 99 · Kingdom of Italy 76 · Switzerland 90
  - NET income 2770 · trade 560 · admin 50 · tribute 150 · upkeep 856 · charges 237 · occupation 50
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Napoleon have been 6 turns over what Franconia can feed. 14,222 men dead. The country will ask where the army went. A supply depot at Franconia would ea…
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 14 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 13 — Late March 1806
  - MAILBOX #12 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #23 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24088 · net +2470 · threat 45 · provinces 29 (+0) · ceiling 229916 · army 106826 · vassals Holland 98 · Kingdom of Italy 85 · Switzerland 89
  - NET income 2774 · trade 560 · admin 50 · tribute 225 · upkeep 824 · charges 265 · occupation 50
- DISPATCH: Sire — Europe has watched us 10 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Prussia and 4 lesser courts would march. Bound for now by a fresh peace: Britain, Austr…
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 26639 · net +2521 · threat 45 · provinces 29 (+0) · ceiling 236666 · army 103373 · vassals Holland 97 · Kingdom of Italy 84 · Switzerland 88
  - NET income 2816 · trade 560 · admin 50 · tribute 225 · upkeep 800 · charges 295 · occupation 35
- DISPATCH: Sire — Russia would now join a league against us — relations −75. The price to keep her out: Talleyrand brings her to −10 in 8 turns (8 DP); buying off her design costs 1,080 gold and shortens the ro…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Austria sign a Defensive Alliance
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #24 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 28963 · net +2296 · threat 45 · provinces 29 (+0) · ceiling 220250 · army 100154 · vassals Holland 96 · Kingdom of Italy 83 · Switzerland 98
  - NET income 2820 · trade 560 · admin 50 · upkeep 776 · charges 323 · occupation 35
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Austria, Russia, Prussia and 4 lesser courts would march.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31279 · net +2288 · threat 45 · provinces 29 (+0) · ceiling 221916 · army 97147 · vassals Holland 95 · Kingdom of Italy 82 · Switzerland 98
  - NET income 2824 · trade 560 · admin 50 · upkeep 760 · charges 351 · occupation 35
- DISPATCH: Sire — the establishment stands 35,353 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 33603 · net +2296 · threat 45 · provinces 29 (+0) · ceiling 224916 · army 94292 · vassals Holland 94 · Kingdom of Italy 81 · Switzerland 98
  - NET income 2828 · trade 560 · admin 50 · upkeep 728 · charges 379 · occupation 35
- DISPATCH: Sire — the enemy has held Franche-Comte 13 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 35919 · net +2288 · threat 45 · provinces 29 (+0) · ceiling 226583 · army 91580 · vassals Holland 93 · Kingdom of Italy 80 · Switzerland 98
  - NET income 2832 · trade 560 · admin 50 · upkeep 712 · charges 407 · occupation 35
- DISPATCH: Sire — Europe has watched us 15 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Austria, Russia, Prussia and 4 lesser courts would march. The cheapest court t…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 38235 · net +2626 · threat 45 · provinces 29 (+0) · ceiling 257000 · army 89003 · vassals Holland 92 · Kingdom of Italy 79 · Switzerland 98
  - NET income 2836 · trade 560 · admin 50 · tribute 337 · upkeep 688 · charges 434 · occupation 35
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Austria, Russia, Prussia and 4 lesser courts would march.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 40881 · net +2764 · threat 45 · provinces 29 (+0) · ceiling 271166 · army 86555 · vassals Holland 91 · Kingdom of Italy 78 · Switzerland 98
  - NET income 2840 · trade 560 · admin 50 · tribute 487 · upkeep 672 · charges 466 · occupation 35
- DISPATCH: Sire — Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

---
finished: **completed** · commands 31 · popups 41 · battles 6
