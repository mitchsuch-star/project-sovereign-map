# Playtest digest — CMD-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `e631f4bd4a79` (dirty) · content `c4151b82bd80` · driver `f7650c682a9c`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 85,373 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2157, own corps) vs Mack (lost 17054) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult and Bernadotte never arr… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu…
  - ⚔ Archduke Charles (lost 4213) vs Massena (lost 6225) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1645 · net +1469 · threat 76 · provinces 28 · ceiling 34790 · army 173942 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 2126 · blockade 250 · admiralty 90
- DISPATCH: Supply cost you 2,636 men, at Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,808; expect about 86,811 with the corps likely to arrive, up to 96,441 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 818, own corps) vs Mack (lost 22289) — Davout and Massena arrived to reinforce Ney, but Napoleon failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,058; expect about 44,348 with the corps likely to arrive) vs Mack (large force) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 4931, own corps) vs Archduke Charles (lost 2078, own corps) — Ney marched to Davout's guns as ordered. It was not enough. — The corps system brought Ney in.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✓ Murat moves from Swabia to Franche-Comte
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Deroy delivers an effective strike. Archduke John holds the line. Casualties: Deroy 3,495, Archduke John 1,414. Both ar… · Deroy's forces advance steadily. Archduke John holds the line. Casualties: Deroy 3,250, Archduke John 1,063. Both armie…
  - ⚔ Archduke Charles (lost 1829) vs Bernadotte (lost 5729) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Deroy (lost 3495) vs Archduke John (lost 1414) — Archduke John's fortifications held firm, Sire. Deroy broke against our walls.
  - ⚔ Deroy (lost 3250) vs Archduke John (lost 1063) — The prepared defenses proved their worth. Deroy could not dislodge Archduke John.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2940 · net +1985 · threat 82 · provinces 28 (+0) · ceiling 35149 · army 155100 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 901 · upkeep 1578 · charges 57 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 5,729 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (15,910; expect about 60,316 with the corps likely to arrive, up to 61,564 if all march) vs Mack (10,747 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 507, own corps) vs Mack (lost 7805, own corps) — Davout and Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire. — The corps system brought Davout in.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (17,114; expect about 28,128 with the corps likely to arrive) vs Mack (large force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 3560, own corps) vs Archduke Charles (lost 1862) — Ney reached Davout in time, Sire — but even together, the field could not be held.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (167 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 665 gold (×3 at war) (×1.11 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 665g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4202 · net +2022 · threat 90 · provinces 29 (+1) · ceiling 24251 · army 148865 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 91
  - NET income 2610 · trade 525 · admin 50 · tribute 905 · upkeep 1376 · charges 221 · occupation 52 · blockade 329 · admiralty 90
- DISPATCH: Sire — Ney, crowned two turns ago, has been driven back.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 7
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 7 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Vienna into Bohemia unopposed! (1,235 lost to march) Captured: Bavaria → Austria · Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charl… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charles…
  - 🏴 Austria: ArchdukeCharles marches from Vienna into Bohemia unopposed! (1,235 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Carniola. (1,391 lost to march) Carniola has been captured by Austria!
  - ⚔ Archduke Charles (lost 1312) vs Deroy (lost 5273) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - ⚔ Archduke Charles (lost 238) vs Deroy (lost 4430) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, stance_change×2, retreat×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 6375 · net +1845 · threat 88 · provinces 29 (+0) · ceiling 24115 · army 147842 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 89
  - NET income 2609 · trade 587 · admin 50 · tribute 910 · upkeep 1346 · charges 455 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 2 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Lannes, attack Mack` → ✗ Mack is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (234 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #9 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 39g a turn — 20g of income forfeited, 52g of occupation relieved, 15g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 8391 · net +2017 · threat 86 · provinces 28 (-1) · ceiling 34512 · army 142945 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 587 · admin 50 · tribute 929 · upkeep 1188 · charges 493 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney and Massena stand 42,678 men at Tyrol, which feeds 24,000. 18,678 too many. 3,073 men lost in 3 turns. Living off the land: this stripped country feeds a French army 80%. The Train des Équ…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 8.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action unused) Turn 7 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Ney. Casualties: Archduke Charles 7… · Archduke John attacks with overwhelming force. Bernadotte holds the line. Casualties: Archduke John 2,171, Bernadotte 1…
  - ⚔ Archduke Charles (lost 722) vs Ney (lost 6973, own corps) — Davout's timely arrival aided Ney. Bernadotte, however, was conspicuously absent.
  - ⚔ Archduke John (lost 2171) vs Bernadotte (lost 1160) — Where was Soult? Bernadotte held the field alone — reinforcement never came.
  - verbs: move×2, attack×2, wait×1
- ORDER Ney [awaiting_response]: Ney is cornered at Tyrol with 4,794 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Tyrol with 4,794 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 9675 · net +1484 · threat 84 · provinces 28 (+0) · ceiling 21876 · army 120347 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 587 · admin 50 · tribute 694 · upkeep 936 · charges 933 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 12
- DIPLO +5 medium/low (enemy_marshal_commissioned, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, coercive_demand)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Franconia to Bohemia. Bohemia lies open, but Davout's men are still rallying from the rout — a corps in recovery holds no ground it walks onto. (83 los…
  - ↳ walked in and annexed nothing — the corps is still rallying from the rout (FA-9)
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (19,067) vs Archduke Charles (28,139 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 6558) vs Archduke Charles (lost 1737) — The terrain heavily favored Archduke Charles. Murat's men paid the price.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Tyrol where he stands! Captured: KingdomOfItaly → Austria
  - 🏴 Austria: ArchdukeCharles takes Tyrol where he stands! Captured: KingdomOfItaly → Austria
  - verbs: attack×1, fortify×1, wait×1
  - POPUP marshal_audience: shadow_command, Marshal Lannes asks for a command → detach
  -     ↳ Lannes straightens. "You will not regret it, Sire." March him to Normandy and the front is his — the order is…
- LEDGER treasury 10946 · net +1365 · threat 82 · provinces 28 (+0) · ceiling 21380 · army 111610 · vassals Holland 93 · Kingdom of Italy 99 · Switzerland 91
  - NET income 2590 · trade 587 · admin 50 · tribute 698 · upkeep 872 · charges 1170 · contributions 110 · requisitions 50 · blockade 368 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 12
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +5 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'Sire, the enemy is too strong. We need reinforcements.' (Trust him and he will retreat from current position instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'Sire, the enemy is too strong. We need reinforcements.' (Trust him and he will retreat from current position instead.) → trust
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena: 'ArchdukeCharles bars the way!' Engaging!
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 11391) vs Archduke Charles (lost 473) — Massena stood alone, Sire. Bernadotte never came.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 11821 · net +1208 · threat 80 · provinces 28 (+0) · ceiling 20185 · army 96359 · vassals Holland 91 · Kingdom of Italy 98 · Switzerland 88
  - NET income 2590 · trade 587 · admin 50 · tribute 703 · upkeep 736 · charges 1418 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 7 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy engages in solid combat. Archduke John holds the line. Casualties: Deroy 2,254, Archduke John 1,118. Both armies …
  - ⚔ Deroy (lost 2254) vs Archduke John (lost 1118) — Archduke John's fortifications held firm, Sire. Deroy broke against our walls.
  - verbs: move×3, fortify×1, attack×1, wait×1, recruit×1
- LEDGER treasury 13009 · net +982 · threat 78 · provinces 28 (+0) · ceiling 19655 · army 92871 · vassals Holland 91 · Kingdom of Italy 99 · Switzerland 87
  - NET income 2590 · trade 587 · admin 50 · tribute 707 · upkeep 720 · charges 1624 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 16 approaches from Bavaria and Austria are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn,…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Franconia, Munich, Swabia.
  - saved `CMD-H_t10` → Game saved: CMD-H_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 7 actions, 2 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Davout. Casualties: Archduke Ch… · ArchdukeCharles holds them at Franconia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 716) vs Davout (lost 1867, own corps) — Napoleon's timely arrival aided Davout. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 596) vs Bernadotte (lost 4385) — Where was Soult? Bernadotte held the field alone — reinforcement never came.
  - verbs: unfortify×2, attack×2, naval_expedition×1, move×1, form_square×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13715 · net +877 · threat 76 · provinces 28 (+0) · ceiling 19277 · army 80143 · vassals Holland 87 · Kingdom of Italy 96 · Switzerland 82
  - NET income 2590 · trade 587 · admin 50 · tribute 712 · upkeep 608 · charges 1846 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 9
- DIPLO +5 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Andalusia stays British by the treaty. Status quo: Tyrol stays Bavarian by the treaty. Status quo: Franconia stays Austrian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: break_square×1, wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 16934 · net +3180 · threat 41 · provinces 28 (+0) · ceiling 281916 · army 80337 · vassals Holland 85 · Kingdom of Italy 95 · Switzerland 81
  - NET income 2590 · trade 623 · admin 50 · tribute 712 · upkeep 616 · charges 179
- DISPATCH: Sire — Davout, Soult, Lannes, Murat, Bernadotte, Massena and Napoleon have been 6 turns over what Swabia can feed. 13,406 men dead. The country will ask where the army went. Bavaria's magazines feed …
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 10
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad, diplomatic_dp_regen, blockade_broken ×3, agenda_shift)
  - LOG ai_ai_proposal_refused: 14 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 76 to 38.

## Turn 12 — Early March 1806
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney demands to be heard → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 19809 · net +2841 · threat 44 · provinces 28 (+0) · ceiling 256500 · army 75819 · vassals Holland 94 · Kingdom of Italy 94 · Switzerland 80
  - NET income 2590 · trade 623 · admin 50 · tribute 375 · upkeep 584 · charges 213
- DISPATCH: Sire — Davout, Soult, Lannes, Murat, Bernadotte, Massena and Napoleon have been 7 turns over what Swabia can feed. 14,436 men dead. The country will ask where the army went. Bavaria's magazines feed …
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 10
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #14 → 1
  -     ↳ refused: The armistice with Austria holds for 3 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #15 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +7 (93 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 22698 · net +2479 · threat 45 · provinces 28 (+0) · ceiling 229250 · army 71573 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 79
  - NET income 2590 · trade 623 · admin 50 · upkeep 536 · charges 248
- DISPATCH: Sire — 7 turns without settlement on Marshal Bernadotte. A rente would close it today; the arrears will not close themselves.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, coercive_demand)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25201 · net +2698 · threat 45 · provinces 28 (+0) · ceiling 250000 · army 67582 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 78
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 512 · charges 278
- DISPATCH: Sire — Davout, Soult, Lannes, Murat, Bernadotte, Massena and Napoleon have been 9 turns over what Swabia can feed. 12,755 men dead. The country will ask where the army went. Bavaria's magazines feed …
  - RAIL diplomatic_offensive_cascade: Austria has joined Russia's war against Sweden, honoring their alliance.
  - RAIL broken_bargain: The compact with Sweden lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, blockade_begins, diplomatic_relation_shift)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 27923 · net +2689 · threat 45 · provinces 28 (+0) · ceiling 252000 · army 63829 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 77
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 488 · charges 311
- DISPATCH: Sire — Marshal Bernadotte's claim is 9 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (77 → 87); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
- LEDGER treasury 30411 · net +2459 · threat 45 · provinces 28 (+0) · ceiling 235250 · army 60303 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · upkeep 464 · charges 340
- DISPATCH: Sire — Marshal Bernadotte's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Karelia. A new design hardens in their court.
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Revanche — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Swabia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2
- LEDGER treasury 32910 · net +2469 · threat 45 · provinces 28 (+0) · ceiling 238583 · army 56988 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · upkeep 424 · charges 370
- DISPATCH: Sire — Marshal Bernadotte's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG design_promoted: REVANCHE: Sweden swears to retake Karelia — Russia is not forgiven

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2, recruit×1
- LEDGER treasury 35395 · net +2455 · threat 45 · provinces 28 (+0) · ceiling 239916 · army 53872 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · upkeep 408 · charges 400
- DISPATCH: Sire — the establishment stands 76,128 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 5
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- LEDGER treasury 37882 · net +2794 · threat 45 · provinces 28 (+0) · ceiling 270666 · army 50942 · vassals Holland 87 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 337 · upkeep 376 · charges 430
- DISPATCH: Sire — Marshal Bernadotte's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-H_t20` → Game saved: CMD-H_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 40692 · net +2776 · threat 45 · provinces 28 (+0) · ceiling 272000 · army 48189 · vassals Holland 86 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 337 · upkeep 360 · charges 464
- DISPATCH: Sire — Marshal Bernadotte's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #17 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (86 → 96); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, recruit×2, garrison×1
- LEDGER treasury 43155 · net +2809 · threat 45 · provinces 28 (+0) · ceiling 277166 · army 45601 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 375 · upkeep 336 · charges 493
- DISPATCH: Sire — Marshal Bernadotte's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, recruit×1
- LEDGER treasury 45988 · net +2799 · threat 45 · provinces 28 (+0) · ceiling 279166 · army 43169 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 375 · upkeep 312 · charges 527
- DISPATCH: Sire — Marshal Bernadotte's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 48803 · net +3006 · threat 45 · provinces 28 (+0) · ceiling 299250 · army 40882 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 600 · upkeep 296 · charges 561
- DISPATCH: Sire — Marshal Bernadotte's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, recruit×2
- LEDGER treasury 51817 · net +2978 · threat 45 · provinces 28 (+0) · ceiling 299916 · army 38732 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 600 · upkeep 288 · charges 597
- DISPATCH: Sire — Marshal Bernadotte's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, recruit×1
- LEDGER treasury 54803 · net +2950 · threat 45 · provinces 28 (+0) · ceiling 300583 · army 36711 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 600 · upkeep 280 · charges 633
- DISPATCH: Sire — Marshal Bernadotte's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 57785 · net +2946 · threat 45 · provinces 28 (+0) · ceiling 303250 · army 34811 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 600 · upkeep 248 · charges 669
- DISPATCH: Sire — Marshal Bernadotte's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 60739 · net +2919 · threat 45 · provinces 28 (+0) · ceiling 303916 · army 33026 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 600 · upkeep 240 · charges 704
- DISPATCH: Sire — Marshal Bernadotte's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×4
- LEDGER treasury 63682 · net +3244 · threat 45 · provinces 28 (+0) · ceiling 334000 · army 31349 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 937 · upkeep 216 · charges 740
- DISPATCH: Sire — the establishment stands 98,651 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Britain (defensive alliance)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, recruit×1
  - POPUP redemption: Bernadotte, 20 → grant_autonomy
  -     ↳ Bernadotte has been granted autonomy. They will act independently for 3 turns, using their own judgment in ba…
- LEDGER treasury 66942 · net +3221 · threat 49 · provinces 28 (+0) · ceiling 335333 · army 29772 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 937 · upkeep 200 · charges 779
- DISPATCH: Sire — Marshal Bernadotte's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Revanche — an ultimatum is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-H_t30` → Game saved: CMD-H_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2
- LEDGER treasury 70163 · net +3183 · threat 53 · provinces 28 (+0) · ceiling 335333 · army 28289 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 937 · upkeep 200 · charges 817
- DISPATCH: Sire — Marshal Bernadotte's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 73362 · net +3160 · threat 57 · provinces 28 (+0) · ceiling 336666 · army 26895 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 937 · upkeep 184 · charges 856
- DISPATCH: Sire — Marshal Bernadotte's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, move×1
- LEDGER treasury 76530 · net +3130 · threat 60 · provinces 28 (+0) · ceiling 337333 · army 25584 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 937 · upkeep 176 · charges 894
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 79668 · net +3100 · threat 58 · provinces 28 (+0) · ceiling 338000 · army 24351 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 623 · admin 50 · tribute 937 · upkeep 168 · charges 932
- DISPATCH: Sire — Marshal Bernadotte's claim is 27 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
- LEDGER treasury 82738 · net +3034 · threat 56 · provinces 28 (+0) · ceiling 335500 · army 23194 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 585 · admin 50 · tribute 937 · upkeep 160 · charges 968
- DISPATCH: Sire — Marshal Bernadotte's claim is 28 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2
- LEDGER treasury 83687 · net +657 · threat 54 · provinces 28 (+0) · ceiling 102340 · army 22106 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 549 · admin 50 · tribute 937 · upkeep 160 · charges 2875 · blockade 344 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sardinia has declared war on France, with 2 allied courts poised to follow.
  - RAIL +5 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +16 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken, cs_tier_shift, blockade_begins ×4, agenda_shift, diplomatic_relation_shift ×5)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG coalition_declared: The Fourth Austrian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia, Sweden
  - LOG third_party_peace: THE CONGRESS: Russia and Sweden make peace without France

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Franconia instead.)
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Franconia instead.) → trust
  - ↳ MUSTER — Massena (3,243; expect about 8,806 with the corps likely to arrive, up to 9,564 if all march) vs Archduke Charles (49,179 men) at Franconia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 1266, own corps) vs Archduke Charles (lost 363, own corps) — Lannes, Murat and Napoleon arrived to reinforce Massena, but Soult failed to reach the field in time.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [retired]: Lannes's question is overtaken, Sire — Lannes has marched clear of Franconia. He awaits new orders.
- ORDER Massena [awaiting_response]: Massena is cornered at Swabia with 1,977 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
- ORDER Murat [retired]: Murat's question is overtaken, Sire — Murat has marched clear of Franconia. He awaits new orders.
- ORDER Napoleon [retired]: Napoleon's question is overtaken, Sire — Napoleon has marched clear of Franconia. He awaits new orders.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Swabia with 1,977 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 84099 · net +272 · threat 52 · provinces 28 (+0) · ceiling 90811 · army 16669 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2590 · trade 549 · admin 50 · tribute 937 · upkeep 104 · charges 3316 · blockade 344 · admiralty 90
- DISPATCH: Sire — Massena was mauled at Franconia: a third of his corps — 1,266 men — lost in a single action.
  - RAIL settlement_offer_arrival: Russia has offered terms to settle Russia vs Sweden.
  - RAIL third_party_peace: THE CONGRESS: Britain and Sweden have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes o…
  - TURN EVENTS 4
- DIPLO +8 medium/low (diplomatic_dp_regen, sovereign_takes_field, paymaster_subsidy, cs_tier_shift, blockade_broken, law_lapsed_abroad ×2, agenda_shift)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (open borders agreement)

## Turn 37 — Late March 1807
  - MAILBOX #15 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #18 already answered this chain)
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination) · Deroy marches from Bohemia into Franconia unopposed! (97 lost to march — forward supply lines reduce losses) Captured: … · Deroy assaults the Bohemia garrison! Garrison: 3,000 -> 1,500 (-1,500). Deroy loses 833 troops. Garrison holds — 1,500 …
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Swabia!
  - 🏴 Bavaria: Deroy marches from Bohemia into Franconia unopposed! (97 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - ⚔ Archduke Charles (lost 604, own corps) vs Murat (lost 1032, own corps) — Murat's aggressive posture left the troops exposed when Archduke Charles's attack came.
  - ⚔ Archduke John (lost 35, own corps) vs Bernadotte (lost 302, own corps) — The walls were not enough. Archduke John broke through Bernadotte's prepared defenses. And Bernadotte was taken on that…
  - verbs: attack×4, unfortify×2, move×1
- ORDER Murat [awaiting_response]: Murat is cornered at Swabia with 566 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Swabia — 466 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Swabia with 566 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Swabia — 466 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 2 · Russia settlement offer · Austria armistice losing
- LEDGER treasury 83655 · net -2074 · threat 50 · provinces 28 (+0) · ceiling 53147 · army 8775 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 787 · upkeep 64 · charges 5552 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Massena has been taken. Austria holds him prisoner.
  - RAIL expedition_landed: THE LANDING: Paget has put 7,323 men ashore at Piedmont.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Austria and Sweden have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes o…
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).

## Turn 38 — Early April 1807
  - MAILBOX #15 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - MAILBOX #16 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → request_settlement_revision
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #19 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #19 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Russia. Your earlier answer was not delivered; the mat…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → request_settlement_revision
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #18 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Massena, drill` → ✗ Marshal Massena is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, fortify` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Piedmont into Provence unopposed! (73 lost to march) Captured: France → Britain · Deroy marches from Franconia into Swabia unopposed! (93 lost to march — forward supply lines reduce losses) Captured: A…
  - 🏴 Britain: Paget marches from Piedmont into Provence unopposed! (73 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Provence to Lyonnais. Lyonnais falls to Britain!
  - 🏴 Bavaria: Deroy marches from Franconia into Swabia unopposed! (93 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - verbs: attack×2, move×1, wait×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 81351 · net -2401 · threat 48 · provinces 26 (-2) · ceiling 47617 · army 8775 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2360 · trade 549 · admin 50 · tribute 787 · upkeep 64 · charges 5649 · blockade 344 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sardinia (design ask)
  - LOG third_party_peace: THE CONGRESS: Austria and Sweden make peace without France
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG ai_ai_proposal_refused: Britain rebuffs Austria (open borders agreement)
  - LOG third_party_peace: THE CONGRESS: Britain and Sweden make peace without France
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Britain (defensive alliance)
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG ai_ai_proposal_refused: Russia and Naples rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Britain (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (500g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_ai_proposal_refused: 6 courts rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)

## Turn 39 — Late April 1807
  - MAILBOX #15 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → reject_settlement_offer
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `recruit 10000 infantry with Lannes` → ✓ Ney recruits 10,000 infantry (nearest to capital) - Cost: 518 gold (capital discount) (×3 at war) (Ney's intendance: +15%). Morale: 100% -> 60%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 518g on this turn's orders
- enemy phase: 4 actions, 2 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Lyonnais into Savoy unopposed! (115 lost to march) Captured: France → Britain · Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 709, Paget 1,656. Bot…
  - 🏴 Britain: Paget marches from Lyonnais into Savoy unopposed! (115 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Savoy to Burgundy. Burgundy falls to Britain!
  - ⚔ Castanos (lost 709) vs Paget (lost 1656) — Paget's aggressive posture left the troops exposed when Castanos's attack came. — The Line Holds +15% (Paget)
  - verbs: attack×2, move×1, wait×1
- LEDGER treasury 75879 · net -4664 · threat 46 · provinces 24 (-2) · ceiling 31195 · army 18775 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2240 · trade 549 · admin 50 · tribute 787 · upkeep 144 · charges 7712 · blockade 344 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Marshal Massena is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-H_t40` → Game saved: CMD-H_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 73431 · net -2495 · threat 44 · provinces 24 (+0) · ceiling 41278 · army 18775 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2240 · trade 549 · admin 50 · tribute 787 · upkeep 144 · charges 5543 · blockade 344 · admiralty 90
- DISPATCH: Sire — Savoy lies in enemy hands. Britain holds it.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)

---
finished: **completed** · commands 200 · popups 56 · battles 22
