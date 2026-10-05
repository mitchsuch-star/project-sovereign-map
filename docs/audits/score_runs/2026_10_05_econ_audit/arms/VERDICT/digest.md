# Playtest digest — VERDICT

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `c14678984809` (dirty) · content `d4a1fdd2fc4f` · driver `e498338939cb`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Bernadotte. Casualties: Archdu…
  - ⚔ Archduke Charles (lost 1973) vs Bernadotte (lost 5788) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1679 · net +1168 · threat 67 · provinces 28 · ceiling 29037 · army 183096 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2450 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 5,788 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Bernadotte. Casualties:… · ArchdukeCharles flanks from Franconia while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 977) vs Bernadotte (lost 7248) — A grievous defeat for Bernadotte, Sire. The losses are severe. And Bernadotte was taken on that field — Austria holds h…
  - ⚔ Archduke Charles (lost 1339) vs Deroy (lost 6510) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×2, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2853 · net +1491 · threat 65 · provinces 28 (+0) · ceiling 30872 · army 171200 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2082 · charges 45 · blockade 219 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 24 approaches from Bavaria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_proposal_rejected: We rejected the Ottoman Empire's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Mack delivers an effective strike. Mack gains the advantage over Deroy. Casualties: Mack 451, Deroy 4,427. Both armies … · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charles… · Mack holds them at Franche-Comte while allies attack from Swabia! (+1 coordination) · ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,404 troops. G…
  - ⚔ Mack (lost 451) vs Deroy (lost 4427) — Deroy's army has been badly mauled. Mack proved the stronger force today.
  - ⚔ Archduke Charles (lost 115) vs Deroy (lost 3133) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Mack (lost 4822) vs Lannes (lost 1960, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - verbs: attack×4
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4219 · net +1402 · threat 63 · provinces 28 (+0) · ceiling 20076 · army 166685 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2559 · trade 350 · admin 50 · tribute 937 · upkeep 1940 · charges 196 · contributions 49 · blockade 219 · admiralty 90
- DISPATCH: Sire — Mack has crossed into Franche-Comte. Lannes and Murat stand in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 approaches from Austria, Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charl… · ArchdukeCharles assaults the Munich garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 2,430 troops in th…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -121g, Bavaria -175g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 66) vs Deroy (lost 1099) — A grievous defeat for Deroy, Sire. The losses are severe.
  - verbs: attack×2, retreat×1, stance_change×1, form_square×1
- LEDGER treasury 5683 · net +1367 · threat 61 · provinces 28 (+0) · ceiling 27860 · army 166685 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 88
  - NET income 2561 · trade 200 · admin 50 · tribute 937 · upkeep 1940 · charges 226 · blockade 125 · admiralty 90
- DISPATCH: Sire — London now pays Vienna 300 gold a turn against us — her war with us is paid for.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected the Papal States' open borders agreement proposal
  - LOG ai_ai_proposal_refused: Spain rebuffs Prussia and Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, move×1, form_square×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Switzerland client petition
- LEDGER treasury 7051 · net +1267 · threat 59 · provinces 28 (+0) · ceiling 26598 · army 166685 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 86
  - NET income 2562 · trade 200 · admin 50 · tribute 937 · upkeep 1940 · charges 327 · blockade 125 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - MAILBOX #8 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #10 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #8 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #10 → refuse the petition
  - POPUP diplomatic_dialogue: Prussia, open_borders #8 → reject
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (86 → 76); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → refuse the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 1 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos engages in solid combat. Castanos gains the advantage over Paget. Casualties: Castanos 762, Paget 1,297. Both …
  - ⚔ Castanos (lost 762) vs Paget (lost 1297) — Paget was close. A period of drilling could have changed the outcome. — The Line Holds +15% (Paget)
  - verbs: move×2, wait×1, attack×1
- ENVOYS WAITING 2 · Austria armistice losing · Denmark non aggression
- LEDGER treasury 8320 · net +1167 · threat 57 · provinces 28 (+0) · ceiling 25470 · army 166685 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 73
  - NET income 2564 · trade 200 · admin 50 · tribute 937 · upkeep 1940 · charges 429 · blockade 125 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,212g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 2
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (law_enacted_abroad ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_proposal_rejected: We rejected the Ottoman Empire's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
  - MAILBOX #11 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #12 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Denmark. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #12 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression #12 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 6 actions, 2 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos takes Leon where he stands! Captured: Britain → Spain · Castanos launches a decisive assault. Castanos gains the advantage over Paget. Casualties: Castanos 384, Paget 1,336. B…
  - 🏴 Spain: Castanos takes Leon where he stands! Captured: Britain → Spain
  - ⚔ Castanos (lost 384) vs Paget (lost 1336) — Paget held superior ground, yet Castanos prevailed. A grim day, Sire. — The Line Holds +15% (Paget)
  - verbs: move×2, attack×2, retreat×1, stance_change×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 9489 · net +1065 · threat 57 · provinces 28 (+0) · ceiling 24443 · army 166685 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 70
  - NET income 2566 · trade 200 · admin 50 · tribute 937 · upkeep 1940 · charges 533 · blockade 125 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design …
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 8 — Early January 1806
  - MAILBOX #13 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #13 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Massena holds the line. Casualties: Mack 6,952, Massena's army 2,933. Both armies remai… · Mack's forces advance steadily. Teulie holds the line. Casualties: Mack 6,980, Teulie's army 1,844. Both armies remain … · Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 137, Paget 873. Both …
  - ⚔ Mack (lost 6952) vs Massena (lost 2650, own corps) — The exchange went Massena's way, Sire — Mack paid twice what Massena did, though the day decided nothing yet.
  - ⚔ Mack (lost 6980) vs Teulie (lost 362, own corps) — The exchange went Teulie's way, Sire — Mack paid twice what Teulie did, though the day decided nothing yet.
  - ⚔ Castanos (lost 137) vs Paget (lost 873) — Even the favorable ground could not save Paget, Sire. Castanos overcame the terrain. — The Line Holds +15% (Paget)
  - verbs: attack×3, form_square×2
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 10047 · net +688 · threat 57 · provinces 28 (+0) · ceiling 16485 · army 162553 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 69
  - NET income 2560 · trade 200 · admin 50 · tribute 874 · upkeep 1812 · charges 859 · contributions 110 · blockade 125 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Lisbon into Leon unopposed! (50 lost to march) Captured: Spain → Britain
  - 🏴 Britain: Wellesley marches from Lisbon into Leon unopposed! (50 lost to march) Captured: Spain → Britain
  - verbs: attack×1
- LEDGER treasury 10703 · net +558 · threat 57 · provinces 28 (+0) · ceiling 15772 · army 162553 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 66
  - NET income 2564 · trade 200 · admin 50 · tribute 878 · upkeep 1812 · charges 957 · contributions 150 · blockade 125 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Berry. No French corps stands in his path.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 11 courts rebuff Prussia (open borders agreement)

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 11268 · net +473 · threat 57 · provinces 28 (+0) · ceiling 15445 · army 162553 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 63
  - NET income 2566 · trade 200 · admin 50 · tribute 883 · upkeep 1812 · charges 1049 · contributions 150 · blockade 125 · admiralty 90
- DISPATCH: Sire — Britain's gold reaches Russia — the subsidy stands at 300 this season.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos's forces press forward aggressively. Castanos gains the advantage over Wellesley. Casualties: Castanos 355, We… · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - ⚔ Castanos (lost 355) vs Wellesley (lost 562) — The walls were not enough. Castanos broke through Wellesley's prepared defenses. — The Line Holds +15% (Wellesley)
  - ⚔ Castanos (lost 217) vs Wellesley (lost 395) — Scarcely an action, Sire. Wellesley and Castanos came to blows on too small a scale to signify. — The Line Holds +15% (Wellesley)
  - verbs: move×2, attack×2
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #14 → reject_settlement_offer
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11821 · net +459 · threat 55 · provinces 28 (+0) · ceiling 15762 · army 162553 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 60
  - NET income 2570 · trade 200 · admin 50 · tribute 887 · upkeep 1812 · charges 1143 · contributions 78 · blockade 125 · admiralty 90
- DISPATCH: Sire — Hanover and Prussia have made peace without us.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,351 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 7 actions, 4 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Massena holds the line. Casualties: Mack 9,631, Massena's army 1,421. Both ar… · Castanos takes Leon where he stands! Captured: Britain → Spain · Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 217, Paget 697. Both … · Castanos holds them at Aragon while allies attack from Leon! (+1 coordination)
  - 🏴 Spain: Castanos takes Leon where he stands! Captured: Britain → Spain
  - ⚔ Mack (lost 9631) vs Massena (lost 1282, own corps) — Mack bled two men for each of Massena's. A clear exchange, not yet a decision.
  - ⚔ Castanos (lost 217) vs Paget (lost 697) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 55) vs Paget (lost 286) — Paget's aggressive posture left the troops exposed when Castanos's attack came. — The Line Holds +15% (Paget)
  - verbs: attack×4, unfortify×1, retreat×1, form_square×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 12574 · net +719 · threat 58 · provinces 28 (+0) · ceiling 20517 · army 161271 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 58
  - NET income 2574 · trade 200 · admin 50 · tribute 847 · upkeep 1782 · charges 955 · blockade 125 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos's forces advance steadily. Castanos gains the advantage over Wellesley. Casualties: Castanos 93, Wellesley 374… · Castanos attacks with overwhelming force. Castanos gains the advantage over Paget. Casualties: Castanos 12, Paget 108. …
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Gascony!
  - ⚔ Castanos (lost 93) vs Wellesley (lost 374) — Wellesley's corps broke, Sire. They are streaming back from the field. — The Line Holds +15% (Wellesley)
  - ⚔ Castanos (lost 12) vs Paget (lost 108) — Paget's corps broke, Sire. They are streaming back from the field. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - verbs: attack×2, retreat×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 13282 · net +608 · threat 56 · provinces 28 (+0) · ceiling 19767 · army 161271 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 55
  - NET income 2559 · trade 200 · admin 50 · tribute 851 · upkeep 1782 · charges 1055 · blockade 125 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 6 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 14 — Early April 1806
  - MAILBOX #15 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #15 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos engages in solid combat. Castanos gains the advantage over Wellesley. Casualties: Castanos 26, Wellesley 236. …
  - 🏴 Spain: [!] MARSHAL CAPTURED — Wellesley is taken by Spain at Berry!
  - ⚔ Castanos (lost 26) vs Wellesley (lost 236) — The line gave way. Wellesley is falling back, and not in good order. And Wellesley was taken on that field — Spain hold… — The Line Holds +15% (Wellesley)
  - verbs: attack×1, fortify×1
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 13889 · net +512 · threat 54 · provinces 28 (+0) · ceiling 19169 · army 161271 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 52
  - NET income 2553 · trade 200 · admin 50 · tribute 856 · upkeep 1782 · charges 1150 · blockade 125 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 15 — Late April 1806
  - MAILBOX #16 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #16 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Britain, armistice_losing #17 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #18 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 2 · Britain armistice losing · Russia armistice losing
- LEDGER treasury 14412 · net +432 · threat 52 · provinces 28 (+0) · ceiling 18730 · army 161271 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 49
  - NET income 2560 · trade 200 · admin 50 · tribute 860 · upkeep 1782 · charges 1241 · blockade 125 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 6,000 men ashore at Andalusia.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack faces a difficult fight. Massena holds the line. Casualties: Mack 8,929, Massena's army 1,798. Both armies remain …
  - ⚔ Mack (lost 8929) vs Massena (lost 1620, own corps) — A costly day for Mack: the losses ran two to one in Massena's favour, and Mack is still in the field.
  - verbs: form_square×1, attack×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 14792 · net +381 · threat 57 · provinces 28 (+0) · ceiling 18451 · army 159651 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 42
  - NET income 2569 · trade 200 · admin 50 · tribute 829 · upkeep 1722 · charges 1330 · blockade 125 · admiralty 90
- DISPATCH: Sire — Marshal Massena holds the field at Milan — Mack's corps is driven from Milan yet again — broken, and fleeing.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG ai_ai_proposal_refused: Spain rebuffs Bavaria (open borders agreement)

## Turn 17 — Late May 1806
  - MAILBOX #19 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #19 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 15187 · net +312 · threat 57 · provinces 28 (+0) · ceiling 18091 · army 159651 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 34
  - NET income 2579 · trade 200 · admin 50 · tribute 833 · upkeep 1722 · charges 1413 · blockade 125 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Vienna 400 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 18 — Early June 1806
  - MAILBOX #20 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #20 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Britain: Shrapnel moves from Cartagena to Bearn. Bearn falls to Britain!
  - verbs: move×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 15191 · net -39 · threat 49 · provinces 27 (-1) · ceiling 14835 · army 159651 · vassals Holland 100 · Kingdom of Italy 100
  - NET income 2503 · trade 200 · admin 50 · tribute 613 · upkeep 1734 · charges 1456 · blockade 125 · admiralty 90
- DISPATCH: Sire — Bearn has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_vassal_transferred: Switzerland passes from France's suzerainty to Britain's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Britain's gold turns Switzerland against France.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 1 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Bearn into Gascony unopposed! (116 lost to march) Captured: France → Britain
  - 🏴 Britain: Shrapnel marches from Bearn into Gascony unopposed! (116 lost to march) Captured: France → Britain
  - verbs: move×2, attack×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 3106, own corps) vs Archduke Charles (lost 3228) — Murat, Massena and Teulie marched to Lannes's guns as ordered. It was not enough. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- LEDGER treasury 14870 · net -98 · threat 50 · provinces 26 (-1) · ceiling 14035 · army 155307 · vassals Holland 98 · Kingdom of Italy 99
  - NET income 2395 · trade 200 · admin 50 · tribute 617 · upkeep 1622 · charges 1523 · blockade 125 · admiralty 90
- DISPATCH: Sire — Gascony has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 34% of active European bloc power.

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Gascony into Berry unopposed! (57 lost to march) Captured: France → Britain · Mack engages in solid combat. Massena holds the line. Casualties: Mack 7,676, Massena's army 2,572. Both armies remain …
  - 🏴 Britain: Shrapnel marches from Gascony into Berry unopposed! (57 lost to march) Captured: France → Britain
  - ⚔ Mack (lost 7676) vs Massena (lost 2342, own corps) — The exchange went Massena's way, Sire — Mack paid twice what Massena did, though the day decided nothing yet.
  - verbs: attack×2, form_square×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 14546 · net -212 · threat 54 · provinces 25 (-1) · ceiling 12819 · army 152965 · vassals Holland 99 · Kingdom of Italy 100
  - NET income 2246 · trade 200 · admin 50 · tribute 604 · upkeep 1552 · charges 1545 · blockade 125 · admiralty 90
- DISPATCH: Sire — Berry has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 21 — Late July 1806
  - MAILBOX #21 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #21 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Berry into Guyenne unopposed! (56 lost to march) Captured: France → Britain
  - 🏴 Britain: Shrapnel marches from Berry into Guyenne unopposed! (56 lost to march) Captured: France → Britain
  - verbs: attack×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  - POPUP diplomatic_dialogue: Hesse, non_aggression #22 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → reject_settlement_offer
- ENVOYS WAITING 2 · Hesse non aggression · Britain settlement offer
- LEDGER treasury 14222 · net -323 · threat 53 · provinces 24 (-1) · ceiling 11659 · army 152965 · vassals Holland 99 · Kingdom of Italy 100
  - NET income 2138 · trade 200 · admin 50 · tribute 608 · upkeep 1560 · charges 1544 · blockade 125 · admiralty 90
- DISPATCH: Sire — Guyenne has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Guyenne into Anjou unopposed! (55 lost to march) Captured: France → Britain
  - 🏴 Britain: Shrapnel marches from Guyenne into Anjou unopposed! (55 lost to march) Captured: France → Britain
  - verbs: attack×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 13784 · net -416 · threat 50 · provinces 23 (-1) · ceiling 10560 · army 152965 · vassals Holland 99 · Kingdom of Italy 100
  - NET income 2030 · trade 200 · admin 50 · tribute 613 · upkeep 1572 · charges 1522 · blockade 125 · admiralty 90
- DISPATCH: Sire — Anjou has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 23 — Late August 1806
  - MAILBOX #24 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #24 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 4 actions, 1 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Anjou into Maine unopposed! (55 lost to march) Captured: France → Britain
  - 🏴 Britain: Shrapnel marches from Anjou into Maine unopposed! (55 lost to march) Captured: France → Britain
  - verbs: move×2, attack×1, recruit×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 2719, own corps) vs Archduke Charles (lost 2590) — Murat, Massena and Teulie reached Lannes in time, Sire — but even together, the field could not be held. — Berthier: the corps marched apart and arrived together.
- LEDGER treasury 13179 · net -321 · threat 49 · provinces 22 (-1) · ceiling 10738 · army 148968 · vassals Holland 97 · Kingdom of Italy 99
  - NET income 1950 · trade 200 · admin 50 · tribute 617 · upkeep 1452 · charges 1471 · blockade 125 · admiralty 90
- DISPATCH: Sire — Maine has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 6 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Maine into Brittany unopposed! (54 lost to march) Captured: France → Britain · Archduke John engages in solid combat. Brutal stalemate between Archduke John and Massena. Heavy casualties on both sid… · Archduke John faces a difficult fight. Archduke John gains the advantage over Teulie. Casualties: Archduke John 1,636, …
  - 🏴 Britain: Shrapnel marches from Maine into Brittany unopposed! (54 lost to march) Captured: France → Britain
  - ⚔ Archduke John (lost 3278) vs Massena (lost 3233, own corps) — Stalemate. Massena and Archduke John glare at each other across the field.
  - ⚔ Archduke John (lost 1636) vs Teulie (lost 961, own corps) — A grievous defeat for Teulie, Sire. The losses are severe. — Massena's faith in you is spent (trust 28) — he committed 12,593 to the fight where he would have brought 25,187.
  - verbs: attack×3, move×2, recruit×1
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 3,526 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 3,526 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 12610 · net -197 · threat 48 · provinces 21 (-1) · ceiling 11149 · army 142343 · vassals Holland 95 · Kingdom of Italy 95
  - NET income 1870 · trade 200 · admin 50 · tribute 604 · upkeep 1272 · charges 1434 · blockade 125 · admiralty 90
- DISPATCH: Sire — Brittany has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 25 — Late September 1806
  - MAILBOX #25 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #25 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,298 troops. Ga… · Archduke John delivers an effective strike. Brutal stalemate between Archduke John and Lannes. Heavy casualties on both… · Mack launches a decisive assault. Mack gains the advantage over Lannes. Casualties: Mack 2,561, Lannes's army 3,953. Bo… · Mack holds them at Franche-Comte while allies attack from Munich! (+1 coordination)
  - ⚔ Archduke John (lost 3597) vs Lannes (lost 1129, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time. — The Hofkriegsrat's orders reached Archduke Charles too late.
  - ⚔ Mack (lost 2561) vs Lannes (lost 2442, own corps) — Lannes fought without Soult's support. The roads, or the will, proved insufficient.
  - ⚔ Mack (lost 2968) vs Murat (lost 3729, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney demands to be heard → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 11681 · net -328 · threat 49 · provinces 21 (+0) · ceiling 9757 · army 131266 · vassals Holland 93 · Kingdom of Italy 81
  - NET income 1821 · trade 200 · admin 50 · tribute 604 · upkeep 1104 · charges 1653 · contributions 31 · blockade 125 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - TURN EVENTS 12
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mac… · ArchdukeCharles flanks from Munich while allies attack from Franche-Comte! (+1 coordination) · ArchdukeJohn assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeJohn loses 1,869 troops in the assau…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -93g, Kingdom of Italy -175g. Captured: KingdomOfItaly → Austria
  - ⚔ Mack (lost 2811) vs Lannes (lost 1069, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 455) vs Lannes (lost 2363, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×3, fortify×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franche-Comte with 1,881 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franche-Comte with 1,881 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes demands to be heard → acknowledge
  -     ↳ Lannes's grievance runs its course.
  - POPUP redemption: Massena, 19 → grant_autonomy
  -     ↳ Massena has been granted autonomy. They will act independently for 3 turns, using their own judgment in battl…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #26 → reject_settlement_offer
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 10733 · net -452 · threat 50 · provinces 21 (+0) · ceiling 8523 · army 121248 · vassals Holland 91 · Kingdom of Italy 79
  - NET income 1800 · trade 200 · admin 50 · tribute 487 · upkeep 976 · charges 1788 · contributions 10 · blockade 125 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Franche-Comte. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 12
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franche-Comte where he stands! Captured: France → Austria · Mack engages in solid combat. Murat holds the line. Casualties: Mack 9,087, Murat's army 3,433. Both armies remain in t…
  - 🏴 Austria: ArchdukeCharles takes Franche-Comte where he stands! Captured: France → Austria
  - ⚔ Mack (lost 9087) vs Murat (lost 653, own corps) — Ney and Davout arrived to reinforce Murat! The timely arrival swung the battle in our favor, Sire. — The corps system brought Ney in.
  - verbs: attack×2, form_square×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 10463 · net -81 · threat 54 · provinces 20 (-1) · ceiling 9998 · army 113415 · vassals Holland 92 · Kingdom of Italy 80
  - NET income 1781 · trade 200 · admin 50 · tribute 487 · upkeep 892 · charges 1492 · blockade 125 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. Mack's corps of 38,287 stands there. A garrison you detach (3,000 men) holds a province against a march, as do…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 28 — Early November 1806
  - MAILBOX #27 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #27 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John launches a decisive assault. Archduke John gains the advantage over Massena. Casualties: Archduke John 2,… · ArchdukeJohn marches from Lyonnais into Provence unopposed! (545 lost to march) Captured: France → Austria
  - 🏴 Austria: FORCED RETREAT! ArchdukeJohn advances into Lyonnais. (588 lost to march) Lyonnais has been captured by Austria!
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Provence unopposed! (545 lost to march) Captured: France → Austria
  - ⚔ Archduke John (lost 2291) vs Massena (lost 3533) — Massena's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×2
- ENVOYS WAITING 2 · Austria armistice losing · Hesse non aggression
- LEDGER treasury 9910 · net -310 · threat 43 · provinces 18 (-2) · ceiling 8171 · army 105788 · vassals Holland 90
  - NET income 1553 · trade 200 · admin 50 · tribute 337 · upkeep 824 · charges 1411 · blockade 125 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 29 — Late November 1806
  - MAILBOX #28 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #29 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #28 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #29 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #28 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #29 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Savoy unopposed! (874 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Savoy unopposed! (874 lost to march) Captured: France → Austria
  - verbs: attack×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 9546 · net -299 · threat 42 · provinces 17 (-1) · ceiling 7868 · army 101972 · vassals Holland 90
  - NET income 1475 · trade 200 · admin 50 · tribute 337 · upkeep 800 · charges 1346 · blockade 125 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Sardinia are rebuffed (design ask)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 30 — Early December 1806
  - MAILBOX #30 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #30 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Savoy into Burgundy unopposed! (380 lost to march) Captured: France → Austria · Archduke John's forces press forward aggressively. Archduke John gains the advantage over Massena. Casualties: Archduke…
  - 🏴 Austria: ArchdukeJohn marches from Savoy into Burgundy unopposed! (380 lost to march) Captured: France → Austria
  - 🏴 Austria: FORCED RETREAT! ArchdukeJohn advances into Limousin. (285 lost to march) Limousin has been captured by Austria!
  - ⚔ Archduke John (lost 1214) vs Massena (lost 4683) — The line gave way. Massena is falling back, and not in good order.
  - verbs: attack×2, move×1, form_square×1
- LEDGER treasury 8961 · net -287 · threat 43 · provinces 15 (-2) · ceiling 7370 · army 93722 · vassals Holland 88
  - NET income 1327 · trade 200 · admin 50 · tribute 337 · upkeep 728 · charges 1258 · blockade 125 · admiralty 90
- DISPATCH: Sire — Burgundy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John's attack meets fierce resistance. Archduke John gains the advantage over Massena. Casualties: Archduke Jo… · ArchdukeJohn marches from Limousin into Languedoc unopposed! (242 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Limousin into Languedoc unopposed! (242 lost to march) Captured: France → Austria
  - ⚔ Archduke John (lost 510) vs Massena (lost 5920) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 8387 · net -227 · threat 44 · provinces 14 (-1) · ceiling 7152 · army 84465 · vassals Holland 86
  - NET income 1232 · trade 200 · admin 50 · tribute 337 · upkeep 656 · charges 1175 · blockade 125 · admiralty 90
- DISPATCH: Sire — Languedoc has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standin…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3466 gold.
  - TURN EVENTS 3
- DIPLO +6 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 32 — Early January 1807
  - MAILBOX #31 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 8196 · net -156 · threat 45 · provinces 14 (+0) · ceiling 7347 · army 81336 · vassals Holland 86
  - NET income 1236 · trade 200 · admin 50 · tribute 337 · upkeep 624 · charges 1140 · blockade 125 · admiralty 90
- DISPATCH: Sire — Anjou, Bearn, Berry and 11 more lie in enemy hands. Britain and Austria hold them.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Murat holds the line. Casualties: Mack 9,632, Murat's army 1,674. Both armies remain in…
  - ⚔ Mack (lost 9632) vs Murat (lost 267, own corps) — A costly day for Mack: the losses ran two to one in Murat's favour, and Mack is still in the field.
  - verbs: attack×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP redemption: Massena, 18 → grant_autonomy
  -     ↳ Massena has been granted autonomy. They will act independently for 3 turns, using their own judgment in battl…
- LEDGER treasury 8004 · net -89 · threat 49 · provinces 14 (+0) · ceiling 7519 · army 76822 · vassals Holland 87
  - NET income 1232 · trade 200 · admin 50 · tribute 337 · upkeep 584 · charges 1109 · blockade 125 · admiralty 90
- DISPATCH: Sire — Marshal Murat holds the field at Lorraine — Mack's corps breaks a second time on this ground and flees.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: retreat×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 1509, own corps) vs Archduke Charles (lost 4221) — Davout and Murat's timely arrival aided Ney. Soult and Napoleon, however, were conspicuously absent.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #32 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 7833 · net -28 · threat 49 · provinces 14 (+0) · ceiling 7681 · army 73129 · vassals Holland 88
  - NET income 1238 · trade 150 · admin 50 · tribute 337 · upkeep 552 · charges 1087 · requisitions 20 · blockade 94 · admiralty 90
- DISPATCH: Sire — 3 turns now with Anjou, Bearn, Berry and 11 more in enemy hands. The country counts every one of them.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 758, own corps) vs Archduke Charles (lost 7252) — Reinforcements from Davout, Murat and Napoleon bolstered Ney's position — though Soult never arrived, Sire. — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Swabia, Ney → secure
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 7549 · net -218 · threat 51 · provinces 16 (+2) · ceiling 6544 · army 70102 · vassals Holland 89
  - NET income 1245 · trade 150 · admin 50 · tribute 337 · upkeep 536 · charges 1205 · occupation 75 · blockade 94 · admiralty 90
- DISPATCH: Sire — the enemy has held Anjou, Bearn, Brittany and 10 more 4 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 36 — Early March 1807
  - MAILBOX #33 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #34 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Davout and Murat: They settle into cold war.
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack struggles in a costly engagement. Ney holds the line. Casualties: Mack 9,184, Ney's army 929. Both armies remain i…
  - ⚔ Mack (lost 9184) vs Ney (lost 395, own corps) — Ney fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×1
- ENVOYS WAITING 2 · Russia armistice losing · Austria armistice losing
- LEDGER treasury 7513 · net +8 · threat 53 · provinces 17 (+1) · ceiling 7554 · army 67813 · vassals Holland 90
  - NET income 1284 · trade 150 · admin 50 · tribute 337 · upkeep 520 · charges 1034 · occupation 75 · blockade 94 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Mack's corps is driven from Swabia yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 37 — Late March 1807
  - MAILBOX #34 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #35 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #35 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #36 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #35 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #36 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Anjou into Berry unopposed! (113 lost to march) Captured: France → Britain
  - 🏴 Britain: Shrapnel marches from Anjou into Berry unopposed! (113 lost to march) Captured: France → Britain
  - verbs: attack×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 7412 · net -79 · threat 54 · provinces 16 (-1) · ceiling 7045 · army 66721 · vassals Holland 90
  - NET income 1309 · trade 150 · admin 50 · tribute 337 · upkeep 512 · charges 1177 · occupation 52 · blockade 94 · admiralty 90
- DISPATCH: Sire — Berry has fallen to Britain. Enemy colours fly over French homeland soil. Shrapnel's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 38 — Early April 1807
  - MAILBOX #36 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #37 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Massena
  - verbs: attack×1
- LEDGER treasury 7478 · net +54 · threat 55 · provinces 16 (+0) · ceiling 7760 · army 65267 · vassals Holland 90
  - NET income 1310 · trade 150 · admin 50 · tribute 337 · upkeep 488 · charges 1029 · contributions 40 · occupation 52 · blockade 94 · admiralty 90
- DISPATCH: Sire — Anjou, Bearn, Berry and 10 more lie in enemy hands. Britain and Austria hold them.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Normandy into Artois unopposed! (109 lost to march) Captured: France → Britain · Archduke Charles's assault collapses into chaos! Brutal stalemate between Archduke Charles and Ney. Heavy casualties on…
  - 🏴 Britain: Shrapnel marches from Normandy into Artois unopposed! (109 lost to march) Captured: France → Britain
  - ⚔ Archduke Charles (lost 1893, own corps) vs Ney (lost 964, own corps) — Soult failed to arrive in time. Ney's army fought without expected support.
  - verbs: attack×2
- ORDER Murat [awaiting_response]: Murat is cornered at Swabia with 4,641 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Swabia with 4,641 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP redemption: Massena, 20 → grant_autonomy
  -     ↳ Massena has been granted autonomy. They will act independently for 3 turns, using their own judgment in battl…
- LEDGER treasury 7269 · net -42 · threat 56 · provinces 15 (-1) · ceiling 7072 · army 57521 · vassals Holland 90
  - NET income 1251 · trade 150 · admin 50 · tribute 337 · upkeep 440 · charges 1154 · occupation 52 · blockade 94 · admiralty 90
- DISPATCH: Sire — Artois has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing t…
  - RAIL diplomatic_alliance_cascade: Russia and Austria enter the war against Switzerland via their alliance with Britain.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Holland's gold turns Switzerland against Britain.
  - TURN EVENTS 1
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG defensive_cascade: Defensive cascade: Russia joins war via Britain
  - LOG defensive_cascade: Defensive cascade: Austria joins war via Britain

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Brutal stalemate between Archduke Charles and Ney. Heavy casualties o…
  - ⚔ Archduke Charles (lost 1259, own corps) vs Ney (lost 1197, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena demands to be heard → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 7097 · net -34 · threat 57 · provinces 16 (+1) · ceiling 6941 · army 54362 · vassals Holland 90
  - NET income 1249 · trade 150 · admin 50 · tribute 300 · upkeep 424 · charges 1123 · occupation 52 · blockade 94 · admiralty 90
- DISPATCH: Sire — Marshal Murat has been taken. Austria holds him prisoner.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)

## Turn 41 — Late May 1807
- CMD `end turn` → ✓ Turn 41 ended. (Warning: 4 actions unused) Turn 42 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 7339 · net +204 · threat 54 · provinces 17 (+1) · ceiling 8407 · army 53783 · vassals Holland 90
  - NET income 1342 · trade 150 · admin 50 · tribute 300 · upkeep 408 · charges 1016 · occupation 30 · blockade 94 · admiralty 90
- DISPATCH: Sire — Berry is French again. The enemy is driven out and the province restored.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)

## Turn 42 — Early June 1807
  - MAILBOX #37 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #38 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 42 ended. (Warning: 4 actions unused) Turn 43 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Hesse non aggression · Britain settlement offer
- LEDGER treasury 7580 · net +195 · threat 51 · provinces 18 (+1) · ceiling 8601 · army 53216 · vassals Holland 90
  - NET income 1371 · trade 150 · admin 50 · tribute 300 · upkeep 400 · charges 1062 · occupation 30 · blockade 94 · admiralty 90
- DISPATCH: Sire — 3 turns now with Artois, Bearn, Brittany and 8 more in enemy hands. The country counts every one of them.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 2935 gold.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 43 — Late June 1807
  - MAILBOX #38 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #39 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #39 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #40 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #39 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #40 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 43 ended. (Warning: 4 actions unused) Turn 44 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Russia armistice losing · Austria armistice losing
- LEDGER treasury 7840 · net +211 · threat 48 · provinces 18 (+0) · ceiling 8943 · army 52766 · vassals Holland 90
  - NET income 1428 · trade 150 · admin 50 · tribute 300 · upkeep 392 · charges 1111 · occupation 30 · blockade 94 · admiralty 90
- DISPATCH: Sire — Anjou is French again. The enemy is driven out and the province restored.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 44 — Early July 1807
  - MAILBOX #40 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #41 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #41 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #42 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #41 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #42 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 44 ended. (Warning: 4 actions unused) Turn 45 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Ney. Casualties: Archduke Charles…
  - ⚔ Archduke Charles (lost 1047, own corps) vs Ney (lost 1493, own corps) — Ney fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: unfortify×2, move×2, attack×1
  - ENDING — THE VERDICT OF HISTORY: The reign, unfinished, is judged as it stands. [THE ECLIPSE]
  -     ↳ Early July 1807 (turn 44) · register `verdict` · marked — the campaign continues
  -     ↳ THE VERDICT — THE ECLIPSE: The Empire is smaller and more alone than it began. / Its enemies have learned that it can be beaten. / History will call it the beginning of the end.
  -     ↳ The Verdict of History: the eclipse.
  -     ↳ THE RECORD — battles 28 (10 won, 11 lost) · men lost 94,358, inflicted 121,755 · provinces taken 6, lost 16 · marshals fallen 0, taken 4 · coalitions faced 1 · peaces signed 0
- LEDGER treasury 7852 · net +142 · threat 49 · provinces 18 (+0) · ceiling 8585 · army 48716 · vassals Holland 88
  - NET income 1419 · trade 150 · admin 50 · tribute 300 · upkeep 360 · charges 1125 · contributions 78 · occupation 30 · blockade 94 · admiralty 90
- DISPATCH: Sire — the enemy has held Artois, Bearn, Brittany and 8 more 5 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (NON AGGRESSION → OPEN BORDERS)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - ENDING reached — stopping (--stop-on-ending)

---
finished: **ending-reached** · commands 44 · popups 98 · battles 42
