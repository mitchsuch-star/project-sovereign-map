# Playtest digest — CMD-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `9b9b7327d476` (dirty) · content `a3638e3d717d` · driver `d2a9aec0bf9f`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 85,373 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2621, own corps) vs Mack (lost 14668) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a devastating assault! Archduke Charles gains the advantage over Bernadotte. Casualties: Arch…
  - ⚔ Archduke Charles (lost 2451) vs Bernadotte (lost 5442, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1611 · net +1525 · threat 75 · provinces 28 · ceiling 33508 · army 172915 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2112 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,442 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,438; expect about 93,034 with the corps likely to arrive, up to 104,029 if all march) vs Mack (substantial force) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 761, own corps) vs Mack (lost 22620) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,754; expect about 32,543 with the corps likely to arrive) vs Mack (substantial force) at Tyrol — the balance of force looks even — a hard fight that …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 2199, own corps) vs Archduke John (lost 2804) — Reinforcement from Ney kept Davout standing, Sire — but neither side yielded the ground.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Bernadotte. Casualties:… · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Ch…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 865) vs Bernadotte (lost 7491) — A grievous defeat for Bernadotte, Sire. The losses are severe. And Bernadotte was taken on that field — Austria holds h… — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 1681) vs Deroy (lost 6407) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, wait×2, fortify×1, retreat×1, stance_change×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 3231 · net +2159 · threat 81 · provinces 28 (+0) · ceiling 38266 · army 149919 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 937 · upkeep 1422 · charges 75 · blockade 281 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 25 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (15,341; expect about 76,013 with the corps likely to arrive, up to 87,718 if all march) vs Mack (12,624 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 440, own corps) vs Mack (lost 10483, own corps) — Davout, Massena and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was taken on t…
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 669 gold (×3 at war) (×1.12 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 actions unused) Turn 4 begins!
- SPENT 669g on this turn's orders
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria · Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charl… · ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,472 troops. G…
  - 🏴 Austria: ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 666) vs Deroy (lost 7937) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, move×1, stance_change×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 5064, own corps) vs Archduke Charles (lost 3420) — Reinforcements from Lannes bolstered Murat's position — though Soult never arrived, Sire.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4747 · net +2267 · threat 89 · provinces 29 (+1) · ceiling 27059 · army 140377 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 91
  - NET income 2621 · trade 525 · admin 50 · tribute 937 · upkeep 1116 · charges 279 · occupation 52 · blockade 329 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is taken at Tyrol — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 8
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as service to the strong.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 27 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 2,430 troops in th… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Murat. Casualties: Archduke…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -121g, Bavaria -175g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1795) vs Murat (lost 4198) — Where was Soult? Murat held the field alone — reinforcement never came.
  - verbs: attack×2
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 6916 · net +2019 · threat 87 · provinces 29 (+0) · ceiling 25533 · army 132239 · vassals Holland 95 · Kingdom of Italy 96 · Switzerland 87
  - NET income 2615 · trade 524 · admin 50 · tribute 937 · upkeep 1032 · charges 532 · contributions 73 · occupation 52 · blockade 328 · admiralty 90
- DISPATCH: Sire — Archduke Charles has crossed into Franche-Comte. Murat stands in his path.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 5 — Late November 1805
  - MAILBOX #8 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #9 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `Ney, attack Archduke Charles` → ✗ Cannot attack Archduke Charles — armistice with Austria (5 turns remaining).
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✗ Cannot enter Swabia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Soult can already reach the body of the realm from wher…
- CMD `Murat, move to Swabia` → ✗ Cannot enter Swabia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Murat can already reach the body of the realm from wher…
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, fortify×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 9270 · net +2146 · threat 85 · provinces 29 (+0) · ceiling 35566 · army 128645 · vassals Holland 95 · Kingdom of Italy 94 · Switzerland 85
  - NET income 2684 · trade 524 · admin 50 · tribute 937 · upkeep 1008 · charges 593 · occupation 30 · blockade 328 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon stand 67,521 men at Tyrol, which feeds 30,000. 37,521 too many. 11,875 men lost in 3 turns. A supply depot at Tyrol would ease it; Milan can feed 75,000 more …
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 6 — Early December 1805
  - MAILBOX #9 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #10 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +6 (94 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 5g a turn — 99g of income forfeited, 30g of occupation relieved, 74g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 8.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 94% -> 89%
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action unused) Turn 7 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10545 · net +1439 · threat 83 · provinces 28 (-1) · ceiling 23071 · army 128356 · vassals Holland 95 · Kingdom of Italy 99 · Switzerland 93
  - NET income 2586 · trade 524 · admin 50 · tribute 787 · upkeep 1000 · charges 980 · contributions 110 · blockade 328 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +3 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 7.
- CMD `Davout, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Murat, attack Archduke Charles` → ✗ Cannot attack Archduke Charles — armistice with Austria (3 turns remaining).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12004 · net +1259 · threat 81 · provinces 28 (+0) · ceiling 22669 · army 125332 · vassals Holland 95 · Kingdom of Italy 98 · Switzerland 92
  - NET income 2588 · trade 524 · admin 50 · tribute 789 · upkeep 984 · charges 1180 · contributions 110 · blockade 328 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 4 turns over what Tyrol can feed. 9,907 men dead. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the ar…
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.) → trust
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Tyr…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shi…
- CMD `Massena, move to Milan` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13306 · net +1112 · threat 79 · provinces 28 (+0) · ceiling 22478 · army 122542 · vassals Holland 95 · Kingdom of Italy 97 · Switzerland 91
  - NET income 2590 · trade 524 · admin 50 · tribute 790 · upkeep 944 · charges 1370 · contributions 110 · blockade 328 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Rhineland and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Franche-Comte (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Co…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13431 · net +1007 · threat 77 · provinces 28 (+0) · ceiling 21525 · army 122962 · vassals Holland 95 · Kingdom of Italy 96 · Switzerland 90
  - NET income 2590 · trade 524 · admin 50 · tribute 793 · upkeep 960 · charges 1422 · contributions 150 · blockade 328 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Tyrol to Franconia. Franconia falls to France! (was Austria) (102 lost to march)
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, fortify` → ✗ Davout is already fortified at Tyrol (+12% defense).
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
  - saved `CMD-A_t10` → Game saved: CMD-A_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 4 actions, 1 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Murat. Casualties: Archduke Cha…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Franche-Comte. (578 lost to march) Franche-Comte has been captured by Austria!
  - ⚔ Archduke Charles (lost 1068) vs Murat (lost 7932) — Not one corps reached Murat. Soult was expected; Murat fought the battle single-handed.
  - verbs: naval_expedition×1, unfortify×1, attack×1, form_square×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 14011 · net +809 · threat 77 · provinces 28 (+0) · ceiling 20011 · army 113663 · vassals Holland 93 · Kingdom of Italy 95 · Switzerland 87
  - NET income 2550 · trade 524 · admin 50 · tribute 822 · upkeep 880 · charges 1619 · contributions 150 · occupation 70 · blockade 328 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps sta…
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 15 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 13 approaches from Austria and Prussia are rebuffed (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Franconia stays ours by the treaty — titled. Status quo: Franche-Comte stays Austrian by the treaty. Status quo: Andalusia stays British by the treaty. Status quo: Tyrol stays ours by the treaty — titled. → display-only
- CMD `Ney, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #15 → 1
  -     ↳ refused: The armistice with Austria holds for 5 more turns. We cannot declare war until it expires.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Rhineland and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ The route from Lorraine to Franconia crosses Swabia — Austria soil, and the frontier is closed. The peace grants us no passage.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 16502 · net +2386 · threat 41 · provinces 28 (+0) · ceiling 73309 · army 117461 · vassals Holland 91 · Kingdom of Italy 94 · Switzerland 86
  - NET income 2551 · trade 560 · admin 50 · tribute 824 · upkeep 920 · charges 609 · occupation 70
- DISPATCH: Sire — Franche-Comte lies in enemy hands. Austria holds it.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_coalition_dissolved, status_quo_titled ×2, diplomatic_dp_regen, blockade_broken ×3, agenda_shift)
  - LOG ai_ai_proposal_refused: 23 approaches rebuffed, chiefly from Austria and Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 77 to 38.

## Turn 12 — Early March 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #16 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, m…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Rhineland (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 79% -> 72%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, recruit×1
- LEDGER treasury 18863 · net +2555 · threat 44 · provinces 28 (+0) · ceiling 231750 · army 119318 · vassals Holland 99 · Kingdom of Italy 93 · Switzerland 85
  - NET income 2636 · trade 560 · admin 50 · tribute 487 · upkeep 936 · charges 202 · occupation 40
- DISPATCH: Sire — Davout, Massena and Napoleon have been 9 turns over what Tyrol can feed. 3,610 men dead. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army is…
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as alliance.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Tyrol to Franconia (122 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 21421 · net +2527 · threat 45 · provinces 28 (+0) · ceiling 232000 · army 119196 · vassals Holland 98 · Kingdom of Italy 92 · Switzerland 84
  - NET income 2639 · trade 560 · admin 50 · tribute 487 · upkeep 936 · charges 233 · occupation 40
- DISPATCH: Sire — 3 turns now with Franche-Comte in enemy hands. The country counts every one of them.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Austria and Prussia (defensive alliance)

## Turn 14 — Early April 1806
  - MAILBOX #13 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #17 → grant the petition
  - POPUP proposal_result: Franconia is ceded to the Kingdom of Italy. Loyalty +8 (92 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. Our net rises by 8g a turn — 129g of income forfeited, 40g of occupation relieved, 97g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Rhineland (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Tyrol and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23958 · net +2732 · threat 45 · provinces 27 (-1) · ceiling 251583 · army 119196 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 83
  - NET income 2510 · trade 560 · admin 50 · tribute 811 · upkeep 936 · charges 263
- DISPATCH: Sire — the enemy has held Franche-Comte 4 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 94%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 26445 · net +2680 · threat 45 · provinces 27 (+0) · ceiling 249750 · army 122196 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 82
  - NET income 2510 · trade 560 · admin 50 · tribute 813 · upkeep 960 · charges 293
- DISPATCH: Sire — the enemy has held Franche-Comte 5 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 16 — Early May 1806
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #18 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Ney can already reach the body of the realm from where…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Rhineland. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 28937 · net +2462 · threat 45 · provinces 27 (+0) · ceiling 234083 · army 122196 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 625 · upkeep 960 · charges 323
- DISPATCH: Sire — the enemy has held Franche-Comte 6 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — service to the strong is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31402 · net +2436 · threat 45 · provinces 27 (+0) · ceiling 234333 · army 122196 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 628 · upkeep 960 · charges 352
- DISPATCH: Sire — the enemy has held Franche-Comte 7 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Austria and Prussia (defensive alliance)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 33841 · net +2409 · threat 45 · provinces 27 (+0) · ceiling 234583 · army 122196 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 631 · upkeep 960 · charges 382
- DISPATCH: Sire — the enemy has held Franche-Comte 8 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes begins marching to Franconia (distance: 2). Moved to Frankfurt. Route: Frankfurt -> Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 1 action unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [active]: Lannes is marching to Franconia (2 turns remaining).
- LEDGER treasury 36253 · net +2720 · threat 45 · provinces 27 (+0) · ceiling 262916 · army 122013 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 971 · upkeep 960 · charges 411
- DISPATCH: Sire — the enemy has held Franche-Comte 9 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Lorraine (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-A_t20` → Game saved: CMD-A_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [completed]: Lannes arrives at Franconia. Lannes: "Done — and I trust the next order has more fire in it."
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 38976 · net +2691 · threat 45 · provinces 27 (+0) · ceiling 263166 · army 121831 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 974 · upkeep 960 · charges 443
- DISPATCH: Sire — the enemy has held Franche-Comte 10 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 21 — Late July 1806
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 40940 · net +2306 · threat 45 · provinces 27 (+0) · ceiling 233083 · army 124831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 637 · upkeep 984 · charges 467
- DISPATCH: Sire — the enemy has held Franche-Comte 11 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 43246 · net +2279 · threat 45 · provinces 27 (+0) · ceiling 233083 · army 124831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 637 · upkeep 984 · charges 494
- DISPATCH: Sire — the enemy has held Franche-Comte 12 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot sh…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 45525 · net +2476 · threat 45 · provinces 27 (+0) · ceiling 251833 · army 124831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 862 · upkeep 984 · charges 522
- DISPATCH: Sire — the enemy has held Franche-Comte 13 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Austria and Prussia (defensive alliance)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 47755 · net +2425 · threat 45 · provinces 27 (+0) · ceiling 249833 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 862 · upkeep 1008 · charges 549
- DISPATCH: Sire — the enemy has held Franche-Comte 14 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 14 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 50180 · net +2396 · threat 45 · provinces 27 (+0) · ceiling 249833 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 862 · upkeep 1008 · charges 578
- DISPATCH: Sire — the enemy has held Franche-Comte 15 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: 8 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 52576 · net +2368 · threat 45 · provinces 27 (+0) · ceiling 249833 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 862 · upkeep 1008 · charges 606
- DISPATCH: Sire — the enemy has held Franche-Comte 16 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 54944 · net +2339 · threat 45 · provinces 27 (+0) · ceiling 249833 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 862 · upkeep 1008 · charges 635
- DISPATCH: Sire — the enemy has held Franche-Comte 17 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 57283 · net +2648 · threat 45 · provinces 27 (+0) · ceiling 277916 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 1199 · upkeep 1008 · charges 663
- DISPATCH: Sire — the enemy has held Franche-Comte 18 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot sh…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 59931 · net +2616 · threat 49 · provinces 27 (+0) · ceiling 277916 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 1199 · upkeep 1008 · charges 695
- DISPATCH: Sire — the enemy has held Franche-Comte 19 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 3
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Austria and Prussia (defensive alliance)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-A_t30` → Game saved: CMD-A_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 62547 · net +2585 · threat 53 · provinces 27 (+0) · ceiling 277916 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 1199 · upkeep 1008 · charges 726
- DISPATCH: Sire — the enemy has held Franche-Comte 20 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 65132 · net +2554 · threat 57 · provinces 27 (+0) · ceiling 277916 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 1199 · upkeep 1008 · charges 757
- DISPATCH: Sire — the enemy has held Franche-Comte 21 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 67686 · net +2523 · threat 60 · provinces 27 (+0) · ceiling 277916 · army 127831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 1199 · upkeep 1008 · charges 788
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 69807 · net +2462 · threat 58 · provinces 27 (+0) · ceiling 274916 · army 130831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 560 · admin 50 · tribute 1199 · upkeep 1044 · charges 813
- DISPATCH: Sire — the enemy has held Franche-Comte 23 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 72219 · net +2383 · threat 56 · provinces 27 (+0) · ceiling 270750 · army 130831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 510 · admin 50 · tribute 1199 · upkeep 1044 · charges 842
- DISPATCH: Sire — the enemy has held Franche-Comte 24 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot sh…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 72775 · net +312 · threat 54 · provinces 27 (+0) · ceiling 81630 · army 130831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2510 · trade 474 · admin 50 · tribute 1199 · upkeep 1044 · charges 2491 · blockade 296 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_alliance_cascade: Spain enters the war against Britain, Austria, Sweden, Hanover and Sardinia via its alliance with France.
  - RAIL diplomatic_offensive_cascade: Russia has joined Britain's war against France, honoring their alliance.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 1 allied court poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 1 allied court poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 1 allied court poised to follow.
  - RAIL +5 more
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And Sweden, Austria and Sardinia stir at their own designs.
- DIPLO +14 medium/low (diplomatic_dp_regen, witness_strike_recorded ×2, diplomatic_treaty_broken, blockade_begins ×4, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG coalition_declared: The Fourth Austrian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia, Sweden
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Prussia (defensive alliance)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Munich instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Munich instead.) → trust
  - ↳ MUSTER — Ney (10,168; expect about 60,353 with the corps likely to arrive, up to 67,843 if all march) vs Archduke Charles (62,723 men) at Munich — the balance of force looks even — a hard fight that may go against us.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1427, own corps) vs Archduke Charles (lost 8333) — Reinforcement from Lannes, Massena and Napoleon kept Ney standing, Sire — but neither side yielded the ground. — Berthier: the corps marched apart and arrived together.
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Munich instead.)
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Munich instead.) → trust
  - ↳ MUSTER — Massena (22,433; expect about 30,664 with the corps likely to arrive, up to 30,738 if all march) vs Archduke Charles (54,390 men) at Munich — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 5254, own corps) vs Archduke Charles (lost 2782) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 96%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- SPENT 600g on this turn's orders
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Massena. Casualties: Archduke … · ArchdukeCharles holds them at Tyrol while allies attack from Munich! (+1 coordination) · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,404 troops. Ga…
  - 🏴 Austria: Casualties: Archduke Charles 1,108, Napoleon's army 3,681. Both armies remain in the field. Tyrol has been captured by Austria!
  - ⚔ Archduke Charles (lost 2810) vs Massena (lost 2428, own corps) — Neither Massena nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 2063) vs Massena (lost 2684, own corps) — The hills were ours, but Archduke Charles took them. Massena's position was overrun.
  - ⚔ Archduke Charles (lost 1108) vs Napoleon (lost 1223, own corps) — Even the favorable ground could not save Napoleon, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×4, unfortify×1
- LEDGER treasury 70286 · net -916 · threat 52 · provinces 27 (+0) · ceiling 53684 · army 108615 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2510 · trade 474 · admin 50 · tribute 1045 · upkeep 840 · charges 3769 · blockade 296 · admiralty 90
- DISPATCH: Sire — Napoleon's corps has been broken at Tyrol. He must reform before he fights again.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, sovereign_takes_field, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes cannot drill with enemy forces nearby! Hiller is at Bohemia, just one region away.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 1,906 troops in the…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -95g, Kingdom of Italy -175g. Captured: KingdomOfItaly → Austria
  - verbs: attack×1, garrison×1
- LEDGER treasury 69053 · net -1379 · threat 50 · provinces 27 (+0) · ceiling 45424 · army 106825 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2510 · trade 474 · admin 50 · tribute 712 · upkeep 824 · charges 3915 · blockade 296 · admiralty 90
- DISPATCH: Sire — Piedmont has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 14,116 men ashore at Piedmont.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG ai_ai_proposal_refused: 15 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke John at Bohemia instead.)
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke John at Bohemia instead.) → trust
  - ↳ MUSTER — Lannes (14,861; expect about 35,273 with the corps likely to arrive, up to 37,963 if all march) vs Archduke John (substantial force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1741, own corps) vs Archduke John (lost 4085, own corps) — Ney, Davout and Napoleon reached the field beside Lannes, Sire — it saved the line, no more.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 8 actions, 2 attacks — Russia, Spain, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Piedmont into Provence unopposed! (141 lost to march) Captured: France → Britain · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Massena. Casualties: Archduke C…
  - 🏴 Britain: Wellesley marches from Piedmont into Provence unopposed! (141 lost to march) Captured: France → Britain
  - ⚔ Archduke Charles (lost 2045) vs Massena (lost 1123, own corps) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, move×2, wait×2, retreat×1, stance_change×1
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Franconia — 1,264 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Franconia — 1,264 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 64923 · net -4886 · threat 48 · provinces 26 (-1) · ceiling 22945 · army 97641 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2360 · trade 474 · admin 50 · tribute 700 · upkeep 760 · charges 7324 · blockade 296 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sardinia (design ask)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (500g/turn)
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG ai_ai_proposal_refused: 5 approaches from Britain and Prussia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain and Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 22 approaches rebuffed, chiefly from Britain and Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain and Prussia (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (500g/turn)
  - LOG ai_ai_proposal_refused: Austria and Sweden rebuff Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_ai_proposal_refused: 22 approaches rebuffed, chiefly from Britain and Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain and Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 22 approaches rebuffed, chiefly from Britain and Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain and Prussia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke Charles is at Bohemia, just one region away.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Austria, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Provence into Lyonnais unopposed! (139 lost to march) Captured: France → Britain · Wellesley marches from Lyonnais into Savoy unopposed! (276 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley marches from Provence into Lyonnais unopposed! (139 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley marches from Lyonnais into Savoy unopposed! (276 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley moves from Savoy to Burgundy. Burgundy falls to Britain!
  - verbs: attack×2, move×1, wait×1
- LEDGER treasury 59840 · net -4676 · threat 45 · provinces 23 (-3) · ceiling 20737 · army 97459 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2160 · trade 474 · admin 50 · tribute 703 · upkeep 760 · charges 6917 · blockade 296 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 500g reaches Sweden
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 36% of active European bloc power.

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke John is at Bohemia, just one region away.
- CMD `Massena, fortify` → ✗ Massena is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
  - saved `CMD-A_t40` → Game saved: CMD-A_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 8 actions, 3 attacks — Russia, Spain, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Lyonnais into Limousin unopposed! (132 lost to march) Captured: France → Britain · Wellesley's forces advance steadily. Wellesley gains the advantage over Bernadotte. Casualties: Wellesley 315, Bernadot… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Ney. Casualties: Archdu…
  - 🏴 Britain: Wellesley marches from Lyonnais into Limousin unopposed! (132 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley moves from Limousin to Berry. Berry falls to Britain!
  - ⚔ Wellesley (lost 315) vs Bernadotte (lost 2532) — Bernadotte's army has been badly mauled. Wellesley proved the stronger force today.
  - ⚔ Archduke Charles (lost 1572) vs Ney (lost 947, own corps) — Ney's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, move×3, retreat×1, wait×1
- ORDER Ney [awaiting_response]: Ney is cornered at Franconia with 4,370 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Franconia with 4,370 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 54346 · net -4669 · threat 42 · provinces 21 (-2) · ceiling 17867 · army 86617 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 1882 · trade 474 · admin 50 · tribute 691 · upkeep 680 · charges 6700 · blockade 296 · admiralty 90
- DISPATCH: Sire — Limousin has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy, agenda_shift ×2)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Sardinia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG ai_ai_proposal_refused: Prussia and Spain rebuff Russia (defensive alliance)

---
finished: **completed** · commands 200 · popups 44 · battles 20
