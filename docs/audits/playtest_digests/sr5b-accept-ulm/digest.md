# Playtest digest — sr5b-accept-ulm

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `00a9b4d7c278` (dirty) · content `d7175e3f0b67` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `declare war on Portugal` → ✓ Choose your war purpose against Portugal.
  - POPUP diplomatic_dialogue: war_purpose_selection #1 → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Portugal. Our threat level stands at 66 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Portugal → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #2 → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Portugal! Holland follows France into the war against Portugal! KingdomOfItaly follows France into the war against Portugal! Switzerland follows France into the war against Portugal! → display-only
- CMD `declare war on the Papal States` → ✓ Choose your war purpose against PapalStates.
  - POPUP diplomatic_dialogue: war_purpose_selection #3 → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on PapalStates. Our threat level stands at 86 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #4 → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on PapalStates! Holland follows France into the war against PapalStates! KingdomOfItaly follows France into the war against PapalStates! Switzerland follows France into the war against PapalStates! → display-only
- CMD `Soult, march to Lisbon` → ✓ Soult begins march to Lisbon. Route: Orleanais → Burgundy → Limousin → Gascony → Bearn → Cartagena → Andalusia → Lisbon. Moves to Orleanais. "Soult, march to Lisbon." Un…
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Route: Piedmont → Rome. Moves to Piedmont. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A…
  - ⚔ Archduke Charles (lost 1690) vs Bernadotte (lost 7247) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
- ORDER Massena [active]: Massena is marching to Rome (1 turn remaining).
- ORDER Soult [active]: Soult is marching to Lisbon (7 turns remaining).
- ENVOYS WAITING 1 · Denmark open borders
- LEDGER treasury 1756 · net +1318 · threat 97 · provinces 28 · ceiling 31419 · army 178949 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2300 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_war_declared: France has declared war on Portugal, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: France has declared war on PapalStates, with 2 allied courts poised to follow.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 2 — Early October 1805
  - LETTER Denmark: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1867, own corps) vs Mack (lost 13536) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Murat never arrived, Sire.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `sr5b-accept-ulm_t2` → Game saved: sr5b-accept-ulm_t2
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 actions unused) Turn 3 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! (1,516 lost to march) Captured: Bavaria → Austria · ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCha…
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! (1,516 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 493) vs Bernadotte (lost 5607) — Bernadotte held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: stance_change×2, attack×2, retreat×1, wait×1
- ORDER Soult [continues]: Soult marches to Burgundy. 6 regions to Lisbon.
- ORDER Massena [interrupted]: Massena hears cannon fire! Abandoning orders — rushing to Munich! Massena moves from Piedmont to Milan (1,178 lost to march)
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 3119 · net +1883 · threat 97 · provinces 28 (+0) · ceiling 36503 · army 160815 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 1728 · charges 63 · requisitions 37 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- COURTS: The court of Prussia eases over The Hanoverian Prize — alliance is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_treaty_signed, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 4 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 3 — Late October 1805
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,509; expect about 68,084 with the corps likely to arrive, up to 72,841 if all march) vs Mack (34,981 men) at Swabia — the balance of force looks favorab…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 871, own corps) vs Mack (lost 19258) — An exemplary engagement by Ney. The outcome was never in doubt.
  - POPUP capture_choice[capture]: Swabia, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (21,578; expect about 67,263 with the corps likely to arrive, up to 73,459 if all march) vs Mack (15,645 men) at Franconia — the balance of force looks f…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 98, own corps) vs Mack (lost 10879) — Reinforcements! Ney, Lannes and Napoleon marched onto the field beside Davout. The enemy's advantage melted away. And M…
  - POPUP capture_choice[capture]: Franconia, Davout → secure
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Franconia to Swabia (148 lost to march)
- CMD `Massena, attack Rome` → ✗ Massena cannot reach Rome from Milan! Range: 1, Distance: 2
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- enemy phase: 5 actions, 5 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,125 troops. G… · ArchdukeCharles assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,736 troops in th… · ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archduke…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,166 lost to march) Swabia has been captured by Austria!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -86g, Bavaria -125g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1563) vs Lannes (lost 5351) — Lannes stood alone, Sire. Murat never came.
  - ⚔ Archduke Charles (lost 94) vs Bernadotte (lost 1833) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1628) vs Murat (lost 4569) — The battle unfolded without particular distinction.
  - verbs: attack×5
- ORDER Soult [continues]: Soult marches to Limousin. 5 regions to Lisbon.
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 2368, own corps) vs Archduke Charles (lost 4617) — Davout and Massena marched to Murat's guns as ordered. It was not enough.
- LEDGER treasury 4355 · net +2166 · threat 97 · provinces 29 (+1) · ceiling 24188 · army 135188 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2613 · trade 300 · admin 50 · tribute 937 · upkeep 1064 · charges 257 · contributions 65 · occupation 70 · blockade 188 · admiralty 90
- DISPATCH: Sire — Lannes's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_we_threshold ×3, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Route: Piedmont → Rome. Moves to Piedmont. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `Massena, attack Rome` → ✓ ASSAULT — Massena storms the works at Rome alone: 31,891 men, 36,674 in the assault's reckoning, against a garrison of 10,000. the garrison breaks below 5,000.
  - ↳ Massena assaults the Rome garrison! Garrison: 10,000 -> 5,000 (-5,000). Massena loses 2,173 troops. Garrison holds — 5,000 defenders remain. It regains up to 2,000 a tur…
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
  - saved `sr5b-accept-ulm_t4` → Game saved: sr5b-accept-ulm_t4
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: retreat×1, stance_change×1, wait×1
- ORDER Soult [continues]: Soult marches to Gascony. 4 regions to Lisbon.
- LEDGER treasury 6545 · net +2028 · threat 95 · provinces 29 (+0) · ceiling 24263 · army 130067 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2616 · trade 300 · admin 50 · tribute 937 · upkeep 1008 · charges 519 · occupation 70 · blockade 188 · admiralty 90
- DISPATCH: Lannes's army is recovering. Effectiveness penalty: -15%.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Russia and Naples rebuff Prussia (open borders agreement)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 5 — Late November 1805
- CMD `Massena, attack Rome` → ✓ ASSAULT — Massena storms the works at Rome alone: 29,718 men, 34,175 in the assault's reckoning, against a garrison of 7,000. the garrison breaks below 5,000.
  - ↳ Massena assaults the Rome garrison! Garrison collapses (7,000 -> 0). Massena loses 1,521 troops in the assault. Massena marches into Rome! (744 lost to march)
  - POPUP capture_choice[capture]: Rome, Massena → secure
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (14,331; expect about 30,265 with the corps likely to arrive, up to 39,047 if all march) vs Archduke Charles (26,912 men) at Swabia — the balance of force…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 959, own corps) vs Archduke Charles (lost 3321) — Ney, Davout and Napoleon arrived in time to steady Murat's position. The field was held, nothing further.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,777 troops. Garrison… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,543 troops in the assau…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - verbs: move×2, attack×2, unfortify×1
- ORDER Soult [continues]: Soult marches to Bearn. 3 regions to Lisbon.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 8203 · net +1689 · threat 97 · provinces 30 (+1) · ceiling 22412 · army 122942 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2760 · trade 262 · admin 50 · tribute 712 · upkeep 960 · charges 736 · occupation 145 · blockade 164 · admiralty 90
- DISPATCH: Sire — Papal States is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: PapalStates has been eliminated from the war.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy, cs_tier_shift)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 9 approaches from Ottoman Empire, Sweden and Naples are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria, Prussia and Naples (open borders agreement)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Naples and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 5 approaches from Austria, Prussia and Naples are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Naples and Spain are rebuffed (open borders agreement)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Naples and Russia (Open Borders Agreement)

## Turn 6 — Early December 1805
  - MAILBOX #2 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond -30 → -10 (-1 a turn). Cost: 1 DP. → display-only
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "We march. Pity whatever slows us."
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Bearn! Range: 1, Distance: 3
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (17,168; expect about 42,462 with the corps likely to arrive, up to 46,455 if all march) vs Archduke Charles (22,549 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1787, own corps) vs Archduke Charles (lost 1943, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - saved `sr5b-accept-ulm_t6` → Game saved: sr5b-accept-ulm_t6
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action unused) Turn 7 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeJohn's forces advance steadily. ArchdukeJohn gains the advantage over Lannes. Casualties: ArchdukeJohn's army 2…
  - ⚔ Archduke Charles (lost 814) vs Murat (lost 5735) — A grievous defeat for Murat, Sire. The losses are severe.
  - ⚔ Archduke John (lost 116, own corps) vs Lannes (lost 4106) — Where was Bernadotte? Lannes held the field alone — reinforcement never came.
  - verbs: attack×2
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
- ORDER Soult [continues]: Soult marches to Cartagena. 2 regions to Lisbon.
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franche-Comte with 4,127 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franche-Comte with 4,127 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
- LEDGER treasury 9002 · net +1355 · threat 95 · provinces 30 (+0) · ceiling 18991 · army 102137 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 93
  - NET income 2750 · trade 262 · admin 50 · tribute 487 · upkeep 792 · charges 949 · contributions 54 · occupation 145 · blockade 164 · admiralty 90
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field.
  - TURN EVENTS 8
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG nation_eliminated: PapalStates has been eliminated from the war.
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: PapalStates rebuffs Britain (defensive alliance)

## Turn 7 — Late December 1805
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Cartagena! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✓ MUSTER — Soult (28,909) vs Paget (screening force) at Aragon — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 703) vs Paget (lost 3911) — An exemplary engagement by Soult. The outcome was never in doubt.
- CMD `Davout, attack Archduke Charles` → ✓ Davout pursues Archduke Charles (at Franche-Comte). Moves to Swabia. Davout: "He will be watched at every step. Patience closes traps."
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franche-Comte where he stands! (190 lost to march) Captured: France → Austria · ArchdukeJohn engages in solid combat. ArchdukeJohn gains the advantage over Murat. Casualties: ArchdukeJohn's army 269,… · ArchdukeCharles holds them at Nivernais while allies attack from Franche-Comte! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles takes Franche-Comte where he stands! (190 lost to march) Captured: France → Austria
  - ⚔ Archduke John (lost 104, own corps) vs Murat (lost 4481) — Murat's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Archduke Charles (lost 48, own corps) vs Bernadotte (lost 1363) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3
- ORDER Davout [active]: Davout is pursuing Archduke Charles (0 turns remaining).
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "It is done. Point me at something that shoots back, Sire."
- ORDER Murat [awaiting_response]: Murat is cornered at Nivernais with 3,156 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Nivernais with 3,156 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 10213 · net +1319 · threat 97 · provinces 30 (+0) · ceiling 19340 · army 90800 · vassals Holland 90 · Kingdom of Italy 91 · Switzerland 89
  - NET income 2847 · trade 262 · admin 50 · tribute 487 · upkeep 704 · charges 1185 · contributions 32 · occupation 152 · blockade 164 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. Archduke Charles's corps of 19,023 stands there. A garrison you detach (3,000 men) holds a province against a march, as d…
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Prussia (defensive alliance)

## Turn 8 — Early January 1806
  - MAILBOX #3 Britain incoming_proposal: Britain — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #10 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "Good. An army rots standing still."
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✗ Cannot attack Paget — armistice with Britain (5 turns remaining).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `sr5b-accept-ulm_t8` → Game saved: sr5b-accept-ulm_t8
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Nivernais where he stands! (179 lost to march) Captured: France → Austria · ArchdukeJohn faces a difficult fight. ArchdukeJohn gains the advantage over Bernadotte. Casualties: ArchdukeJohn's army… · ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl… · ArchdukeJohn marches from Burgundy into Lyonnais unopposed! (101 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles takes Nivernais where he stands! (179 lost to march) Captured: France → Austria
  - 🏴 Austria: Both armies remain in the field. ArchdukeJohn advances into Burgundy. (102 lost to march) Burgundy has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Limousin. (176 lost to march) Limousin has been captured by Austria!
  - 🏴 Austria: ArchdukeJohn marches from Burgundy into Lyonnais unopposed! (101 lost to march) Captured: France → Austria
  - ⚔ Archduke John (lost 11, own corps) vs Bernadotte (lost 310) — Bernadotte's corps broke, Sire. They are streaming back from the field.
  - ⚔ Archduke Charles (lost 7) vs Bernadotte (lost 249) — Bernadotte was driven from the field. His men are scattered. And Bernadotte was taken on that field — Austria holds him.
  - verbs: attack×4
- ORDER Davout [continues]: Davout pursues ArchdukeCharles. 1 region away.
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 11262 · net +859 · threat 94 · provinces 26 (-4) · ceiling 16093 · army 90027 · vassals Holland 84 · Kingdom of Italy 87 · Switzerland 84
  - NET income 2630 · trade 262 · admin 50 · tribute 487 · upkeep 704 · charges 1644 · occupation 132 · admiralty 90
- DISPATCH: Sire — Nivernais has fallen. Enemy colours fly over French homeland soil. Archduke Charles's corps of 17,904 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Cagliari–Rome crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- DIPLO +8 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted, cs_tier_shift, blockade_broken ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 36% of active European bloc power.
  - LOG ai_ai_proposal_refused: 14 approaches rebuffed, chiefly from Britain (defensive alliance)

## Turn 9 — Late January 1806
  - MAILBOX #4 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #11 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (84 → 94); bond -30 → -10 (-1 a turn). Cost: 1 DP. → display-only
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✗ Cannot attack Paget — armistice with Britain (4 turns remaining).
- CMD `Soult, attack Wellesley` → ✗ Cannot attack Wellesley — armistice with Britain (4 turns remaining).
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Limousin into Berry unopposed! (175 lost to march) Captured: France → Austria · ArchdukeJohn marches from Lyonnais into Provence unopposed! (100 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 6,263 (-5,737). ArchdukeCharles loses 3,174 troops.…
  - 🏴 Austria: ArchdukeCharles marches from Limousin into Berry unopposed! (175 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Provence unopposed! (100 lost to march) Captured: France → Austria
  - verbs: attack×3
- ORDER Davout [breaks]: Order cancelled: Davout arrives at Nivernais but finds no sign of ArchdukeCharles. Last intelligence was 1 turn old. Awaiting orders, Sire.
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "Done — and I trust the next order has more fire in it."
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11235 · net +182 · threat 91 · provinces 25 (-1) · ceiling 12222 · army 89883 · vassals Holland 93 · Kingdom of Italy 87 · Switzerland 83
  - NET income 2345 · trade 262 · admin 50 · tribute 150 · upkeep 704 · charges 1699 · occupation 132 · admiralty 90
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3706 gold.
  - TURN EVENTS 2
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- DIPLO +4 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 6 approaches rebuffed, chiefly from Britain and Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 22 approaches rebuffed, chiefly from Naples and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Naples are rebuffed (defensive alliance)

## Turn 10 — Early February 1806
  - MAILBOX #5 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #13 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Portugal + Russia (10 pairs resolved). Status quo: Franconia and Swabia stay ours by the treaty — titled. Status quo: Berry, Burgundy, Franche-Comte, Limousin, Lyonnais and Provence stay Austrian by the treaty. Status quo: Milan stays Austrian by the treaty. → display-only
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
  - saved `sr5b-accept-ulm_t10` → Game saved: sr5b-accept-ulm_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #14 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (83 → 93); bond -30 → -10 (-1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 9331 · net +1577 · threat 64 · provinces 25 (+0) · ceiling 46857 · army 104583 · vassals Holland 90 · Kingdom of Italy 93 · Switzerland 80
  - NET income 2426 · trade 310 · admin 50 · upkeep 800 · charges 307 · occupation 102
- DISPATCH: Sire — the establishment stands 17,917 men under the ordinance, and the depots hold 98,764. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Kingdom of Italy + Switzerland vs Britain + Austria + Russia + Portugal: Gold indemnity: 3706 gold from Fran…
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 7
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +6 medium/low (diplomatic_coalition_dissolved, status_quo_titled, law_enacted_abroad ×2, diplomatic_dp_regen, blockade_broken)
  - LOG ai_ai_proposal_refused: 23 approaches rebuffed, chiefly from Austria and Naples (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 91 to 65.

## Turn 11 — Late February 1806
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "Accomplished. The men want a battle, not another road."
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- ENVOYS WAITING 1 · Hesse open borders
- LEDGER treasury 11229 · net +1875 · threat 63 · provinces 25 (+0) · ceiling 167416 · army 104289 · vassals Holland 87 · Kingdom of Italy 90 · Switzerland 77
  - NET income 2505 · trade 310 · admin 50 · upkeep 800 · charges 110 · occupation 80
- DISPATCH: Sire — Marshal Soult's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 12 — Early March 1806
  - LETTER Hesse: Open Borders Agreement → accept
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "We march. Pity whatever slows us."
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `sr5b-accept-ulm_t12` → Game saved: sr5b-accept-ulm_t12
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 13303 · net +1901 · threat 62 · provinces 25 (+0) · ceiling 171666 · army 104001 · vassals Holland 84 · Kingdom of Italy 87 · Switzerland 74
  - NET income 2519 · trade 347 · admin 50 · upkeep 800 · charges 135 · occupation 80
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 18,499 men at Paris, and nobody has gone to collect them.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 13 — Late March 1806
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Moore` → ✗ We are not at war with Britain, Sire — Moore may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "It is done. Point me at something that shoots back, Sire."
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 15217 · net +2116 · threat 61 · provinces 25 (+0) · ceiling 191500 · army 103719 · vassals Holland 81 · Kingdom of Italy 84 · Switzerland 71
  - NET income 2532 · trade 347 · admin 50 · tribute 225 · upkeep 800 · charges 158 · occupation 80
- DISPATCH: Sire — Marshal Soult has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - TURN EVENTS 7
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Prussia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "Good. An army rots standing still."
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Moore` → ✗ We are not at war with Britain, Sire — Moore may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
  - saved `sr5b-accept-ulm_t14` → Game saved: sr5b-accept-ulm_t14
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (68 → 78); bond -10 → 10 (+0 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 17350 · net +1882 · threat 60 · provinces 25 (+0) · ceiling 174166 · army 103443 · vassals Holland 78 · Kingdom of Italy 81 · Switzerland 78
  - NET income 2549 · trade 347 · admin 50 · upkeep 800 · charges 184 · occupation 80
- DISPATCH: Sire — Marshal Archduke Charles of Austria is destroyed at Berry — his corps annihilated, his name struck from their order of battle.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Prussia, Ottoman, Sweden, Naples, Portugal, Saxony, Hanover, Hesse, Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: 5 approaches from Britain, Prussia and Naples are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 14 approaches rebuffed, chiefly from Naples and Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 5 approaches from Britain, Prussia and Naples are rebuffed (defensive alliance)

## Turn 15 — Late April 1806
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Moore` → ✗ We are not at war with Britain, Sire — Moore may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "Done — and I trust the next order has more fire in it."
- LEDGER treasury 19241 · net +1869 · threat 59 · provinces 25 (+0) · ceiling 174916 · army 103173 · vassals Holland 75 · Kingdom of Italy 78 · Switzerland 76
  - NET income 2558 · trade 347 · admin 50 · upkeep 800 · charges 206 · occupation 80
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Primacy in Germany — service to the strong is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Moore` → ✗ We are not at war with Britain, Sire — Moore may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
  - saved `sr5b-accept-ulm_t16` → Game saved: sr5b-accept-ulm_t16
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21157 · net +2230 · threat 58 · provinces 25 (+0) · ceiling 206916 · army 102909 · vassals Holland 72 · Kingdom of Italy 75 · Switzerland 74
  - NET income 2590 · trade 347 · admin 50 · tribute 337 · upkeep 800 · charges 229 · occupation 65
- DISPATCH: Sire — Marshal Archduke John of Austria is destroyed at Provence — his corps annihilated, his name struck from their order of battle.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Naples and Austria (defensive alliance)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 22668 · net +1397 · threat 57 · provinces 25 (+0) · ceiling 62340 · army 102651 · vassals Holland 69 · Kingdom of Italy 72 · Switzerland 72
  - NET income 2594 · trade 262 · admin 50 · tribute 337 · upkeep 800 · charges 727 · occupation 65 · blockade 164 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_offensive_cascade: Russia has joined Britain's war against France, honoring their alliance.
  - RAIL diplomatic_offensive_cascade: Austria has joined Britain's war against France, honoring their alliance.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 3 allied courts poised to follow.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL +22 more
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +25 medium/low (law_enacted_abroad, diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken ×3, cs_tier_shift, blockade_begins ×4, diplomatic_relation_shift ×12)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG coalition_declared: The Fourth Russian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Hesse, Naples, Ottoman, Portugal, Prussia, Russia…
  - LOG ai_ai_proposal_refused: Russia and Austria rebuff Prussia (defensive alliance)

## Turn 18 — Early June 1806
  - MAILBOX #9 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #17 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (69 → 79); bond -10 → 10 (+0 a turn). Cost: 1 DP. → display-only
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✓ Soult pursues Paget (at Leon). Moves to Leon. "Soult attack Paget." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
- CMD `Soult, attack Moore` → ✗ No intelligence on Moore's position, Sire. Scout for him before Soult can give chase.
  - saved `sr5b-accept-ulm_t18` → Game saved: sr5b-accept-ulm_t18
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Brunswick launches a decisive assault. Brunswick gains the advantage over Ney. Casualties: Brunswick 2,189, Ney's army … · Brunswick holds them at Franconia while allies attack from Berlin! (+1 coordination)
  - 🏴 Prussia: Casualties: Brunswick 1,173, Napoleon's army 4,028. Both armies remain in the field. Franconia has been captured by Prussia!
  - ⚔ Brunswick (lost 2189) vs Ney (lost 3501, own corps) — Ney's army has been badly mauled. Brunswick proved the stronger force today.
  - ⚔ Brunswick (lost 1173) vs Napoleon (lost 1197, own corps) — Napoleon's army has been badly mauled. Brunswick proved the stronger force today.
  - verbs: attack×2, unfortify×1
- ORDER Soult [active]: Soult is pursuing Paget (0 turns remaining).
- LEDGER treasury 22437 · net +287 · threat 54 · provinces 24 (-1) · ceiling 26188 · army 91652 · vassals Holland 93 · Kingdom of Italy 85 · Switzerland 86
  - NET income 2397 · trade 262 · admin 50 · tribute 150 · upkeep 712 · charges 1561 · occupation 45 · blockade 164 · admiralty 90
- DISPATCH: Sire — Napoleon's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 14,056 men ashore at Provence.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, paymaster_subsidy)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 9 actions, 7 attacks — Russia, Austria, the Ottoman Empire and 2 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Provence into Languedoc unopposed! (140 lost to march) Captured: France → Britain · Brunswick attacks with overwhelming force. Brunswick gains the advantage over Ney. Casualties: Brunswick 263, Ney 4,788… · Brunswick holds them at Swabia while allies attack from Franconia! (+1 coordination) · Castanos assaults the Lisbon garrison! Garrison collapses (7,000 -> 0). Castanos loses 1,944 troops in the assault. Cas…
  - 🏴 Britain: Wellesley marches from Provence into Languedoc unopposed! (140 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley moves from Languedoc to Gascony. Gascony falls to Britain!
  - 🏴 Spain: [Materiel] Guns, horses and stores lost with the fallen: Spain -97g, Portugal -175g. Captured: Portugal → Spain
  - 🏴 Spain: Castanos marches from Lisbon into Porto unopposed! (117 lost to march) Captured: Portugal → Spain
  - ⚔ Brunswick (lost 263) vs Ney (lost 4788) — The toll on Ney's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Brunswick (lost 83) vs Napoleon (lost 935) — The toll on Napoleon's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Damas (lost 3725) vs Massena (lost 1734) — An exemplary engagement by Massena. The outcome was never in doubt.
  - ⚔ Damas (lost 3264) vs Massena (lost 1265) — A decisive victory for Massena! Damas was thoroughly outmatched.
  - verbs: attack×7, move×2
- ORDER Soult [breaks]: Order cancelled: The trail has gone cold, Sire — Paget was last making for Leon, and Soult has no further word of him. Scout for him to take up the c…
- ORDER Ney [awaiting_response]: Ney is cornered at Swabia with 3,954 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Swabia with 3,954 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
- LEDGER treasury 21298 · net -663 · threat 51 · provinces 22 (-2) · ceiling 15555 · army 78232 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2093 · trade 262 · admin 50 · tribute 150 · upkeep 616 · charges 2230 · contributions 58 · occupation 60 · blockade 164 · admiralty 90
- DISPATCH: Sire — Languedoc has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL design_promoted: REVANCHE: Portugal will not forgive Spain the loss of Beira and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +6 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×3)
  - LOG british_subsidy: Britain's gold: 400g reaches Naples
  - LOG ai_ai_proposal_refused: 3 approaches from Britain and Russia are rebuffed (defensive alliance)
  - LOG british_subsidy: Britain's gold: 400g reaches Sardinia
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (400g/turn)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: 13 approaches from Britain, Prussia and Naples are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_ai_proposal_refused: 10 approaches from Britain and Prussia are rebuffed (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 20 — Early July 1806
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ No intelligence on Paget's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Moore` → ✗ No intelligence on Moore's position, Sire. Scout for him before Soult can give chase.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `sr5b-accept-ulm_t20` → Game saved: sr5b-accept-ulm_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 5 actions, 4 attacks — Russia, Austria, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Gascony into Guyenne unopposed! (136 lost to march) Captured: France → Britain · Wellesley marches from Guyenne into Anjou unopposed! (135 lost to march) Captured: France → Britain · Brunswick takes Swabia where he stands! (1,271 lost to march) Captured: France → Prussia · Brunswick delivers an effective strike. Brunswick gains the advantage over Napoleon. Casualties: Brunswick 39, Napoleon…
  - 🏴 Britain: Wellesley marches from Gascony into Guyenne unopposed! (136 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley marches from Guyenne into Anjou unopposed! (135 lost to march) Captured: France → Britain
  - 🏴 Prussia: Brunswick takes Swabia where he stands! (1,271 lost to march) Captured: France → Prussia
  - ⚔ Brunswick (lost 39) vs Napoleon (lost 446) — Napoleon stood alone, Sire. Davout never came.
  - verbs: attack×4, fortify×1
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Lorraine — 712 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Lorraine — 712 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
- LEDGER treasury 20322 · net -1268 · threat 48 · provinces 19 (-3) · ceiling 11209 · army 76831 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 1813 · trade 262 · admin 50 · tribute 150 · upkeep 608 · charges 2550 · contributions 101 · occupation 30 · blockade 164 · admiralty 90
- DISPATCH: Sire — Guyenne has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Sardinia
  - LOG ai_ai_proposal_refused: Naples and Sardinia rebuff Britain (defensive alliance)
  - LOG design_promoted: REVANCHE: Portugal swears to retake Beira and 2 more — Spain is not forgiven
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Naples (defensive alliance)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 7 actions, 6 attacks — Russia, Austria, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Anjou into Maine unopposed! (133 lost to march) Captured: France → Britain · Wellesley assaults the Normandy garrison! Garrison collapses (6,263 -> 0). Wellesley loses 1,739 troops in the assault.… · Brunswick takes Lorraine where he stands! (1,176 lost to march) Captured: France → Prussia · Brunswick's forces advance steadily. Brunswick gains the advantage over Davout. Casualties: Brunswick 1,215, Davout 4,2…
  - 🏴 Britain: Wellesley marches from Anjou into Maine unopposed! (133 lost to march) Captured: France → Britain
  - 🏴 Britain: [Materiel] Guns, horses and stores lost with the fallen: Britain -86g, France -156g. Captured: France → Britain
  - 🏴 Prussia: Brunswick takes Lorraine where he stands! (1,176 lost to march) Captured: France → Prussia
  - 🏴 Prussia: FORCED RETREAT! Brunswick advances into Nivernais. (1,104 lost to march) Nivernais has been captured by Prussia!
  - 🏴 Prussia: [Materiel] Guns, horses and stores lost with the fallen: Prussia -108g, Switzerland -125g. Captured: Switzerland → Prussia
  - ⚔ Brunswick (lost 1215) vs Davout (lost 4244) — Davout's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×6, form_square×1
- ENVOYS WAITING 1 · Naples armistice losing
- LEDGER treasury 19061 · net -844 · threat 35 · provinces 15 (-4) · ceiling 11974 · army 72347 · vassals Holland 100 · Kingdom of Italy 100
  - NET income 1558 · trade 274 · admin 50 · tribute 150 · upkeep 552 · charges 2033 · occupation 30 · blockade 171 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Prussia holds him, and the Empire holds its breath.
  - RAIL nation_eliminated: Switzerland has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Naples
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Naples (defensive alliance)

## Turn 22 — Early August 1806
  - MAILBOX #10 Naples incoming_proposal: Naples — Armistice → activated
  - POPUP diplomatic_dialogue: Naples, armistice_losing #18 → accept
  - POPUP proposal_result: You have accepted Naples's proposal. Treaty signed: At War → Armistice with Naples. → display-only
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ No intelligence on Paget's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Moore` → ✗ No intelligence on Moore's position, Sire. Scout for him before Soult can give chase.
  - saved `sr5b-accept-ulm_t22` → Game saved: sr5b-accept-ulm_t22
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Brunswick marches from Bern into Savoy unopposed! (1,473 lost to march) Captured: France → Prussia
  - 🏴 Prussia: Brunswick marches from Bern into Savoy unopposed! (1,473 lost to march) Captured: France → Prussia
  - verbs: attack×1
- ENVOYS WAITING 1 · Prussia peace
- LEDGER treasury 18002 · net -984 · threat 22 · provinces 14 (-1) · ceiling 9957 · army 72113 · vassals Holland 100
  - NET income 1484 · trade 298 · admin 50 · upkeep 552 · charges 1958 · occupation 30 · blockade 186 · admiralty 90
- DISPATCH: Sire — Savoy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL armistice_ratified: A truce with Naples: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL nation_eliminated: Portugal has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 2
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, blockade_broken, agenda_shift)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia and Austria (defensive alliance)
  - LOG coalition_member_left: Portugal has left the coalition.
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Russia (defensive alliance)

## Turn 23 — Late August 1806
  - MAILBOX #11 Prussia incoming_proposal: Prussia — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Prussia, peace #19 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: At War → Peace with Prussia. → display-only
  - RATIFIED Prussia · PEACE · enemy_victory
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Massena [continues]: Massena marches to Piedmont. 3 regions to Champagne.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 14607 · net -516 · threat 19 · provinces 14 (+0) · ceiling 10125 · army 79585 · vassals Holland 100
  - NET income 1490 · trade 310 · admin 50 · upkeep 600 · charges 1452 · occupation 30 · blockade 194 · admiralty 90
- DISPATCH: Sire — the war with Prussia is over. 1 corps stands on the wrong side of the new frontier. Berthier has given them the road home — Massena to Champagne. They have safe passage for 7 turns while they …
  - RAIL peace_ratified: Peace ratified between Prussia and France.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL design_promoted: REVANCHE: Ottoman Empire will not forgive Spain the loss of Oran and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Naples
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria, Britain, Hanover, Hesse, Ottoman Empire, Russia, Sardinia, Saxony and Sweden remain at war with us.
  - LOG coalition_member_left: Prussia has left the coalition.
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - LOG nation_eliminated: Portugal has been eliminated from the war.
  - LOG nation_eliminated: Switzerland has been eliminated from the war.

## Turn 24 — Early September 1806
  - saved `sr5b-accept-ulm_t24` → Game saved: sr5b-accept-ulm_t24
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [continues]: Massena marches to Lyonnais. 2 regions to Champagne.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #21 → confirm_settlement
  - POPUP nation_proclamation: Normandy → display-only
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Hanover + Hesse + Naples + Ottoman + Prussia + Russia + Sardinia + Saxony + Sweden (27 pairs resolved). Status quo: Anjou, Gascony, Guyenne, Languedoc and Maine stay British by the treaty. Status quo: Berry, Burgundy, Franche-Comte, Limousin and Provence stay Austrian by the treaty. Status quo: Algiers and Oran stay Spanish by the treaty. → display-only
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 8628 · net +956 · threat 16 · provinces 15 (+1) · ceiling 24032 · army 78406 · vassals Holland 100
  - NET income 1516 · trade 430 · admin 50 · upkeep 600 · charges 410 · occupation 30
- DISPATCH: Sire — Lyonnais is French again. The enemy is driven out and the province restored.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle Britain vs France. Asking 5111 gold.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 40% of active European bloc power.
  - LOG design_promoted: REVANCHE: Ottoman Empire swears to retake Oran and 1 more — Spain is not forgiven

## Turn 25 — Late September 1806
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Moore` → ✗ We are not at war with Britain, Sire — Moore may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [continues]: Massena marches to Limousin. 1 region to Champagne.
- ORDER Soult [continues]: Soult marches to Aragon. 4 regions to Paris.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 9606 · net +1254 · threat 14 · provinces 15 (+0) · ceiling 29822 · army 76125 · vassals Holland 98
  - NET income 1522 · trade 430 · admin 50 · tribute 337 · upkeep 584 · charges 471 · occupation 30
- DISPATCH: Sire — the war with Britain is over. 1 corps stands on the wrong side of the new frontier. Berthier has given them the road home — Soult to Paris. They have safe passage for 8 turns while they march.
  - RAIL nation_created: By the fortune of arms and the pen at the table — Duchy of Normandy is erected upon the map, a client of Britain.
  - RAIL settlement_summary: Settlement of Britain + Russia + Austria + Prussia + Ottoman Empire + Sweden + Naples + Saxony + Hanover + Hesse + Sardinia vs France + Spain + Holla…
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Cagliari–Rome crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Ottoman Empire eases over Revanche — alliance is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — service to the strong is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +6 medium/low (balance_of_europe_shifted, diplomatic_dp_regen, cs_tier_shift, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Russia, Austria and Prussia are rebuffed (defensive alliance)

## Turn 26 — Early October 1806
  - saved `sr5b-accept-ulm_t26` → Game saved: sr5b-accept-ulm_t26
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [completed]: Massena arrives at Champagne. Massena: "It is done. Point me at something that shoots back, Sire."
- ORDER Soult [continues]: Soult marches to Bearn. 3 regions to Paris.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 10866 · net +1182 · threat 12 · provinces 15 (+0) · ceiling 29919 · army 75365 · vassals Holland 96
  - NET income 1528 · trade 430 · admin 50 · tribute 337 · upkeep 584 · charges 549 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
  - MAILBOX #13 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (96 → 100); bond 10 → 30 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Soult [continues]: Soult marches to Gascony. 2 regions to Paris.
- LEDGER treasury 11725 · net +806 · threat 9 · provinces 15 (+0) · ceiling 24709 · army 73577 · vassals Holland 99
  - NET income 1534 · trade 430 · admin 50 · upkeep 576 · charges 602 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 28 — Early November 1806
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✗ We are not at war with Britain, Sire — Paget may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Moore` → ✗ We are not at war with Britain, Sire — Moore may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
  - saved `sr5b-accept-ulm_t28` → Game saved: sr5b-accept-ulm_t28
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Soult [continues]: Soult marches to Berry. 1 region to Paris.
- LEDGER treasury 12884 · net +1122 · threat 6 · provinces 15 (+0) · ceiling 47937 · army 72453 · vassals Holland 98
  - NET income 1580 · trade 430 · admin 50 · upkeep 560 · charges 348 · occupation 30
- DISPATCH: Sire — the levy has stood open 19 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 2
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Soult [completed]: The order was "the road home — safe passage granted by the peace". Soult arrives at Paris. I await further instruction.
- LEDGER treasury 14038 · net +1117 · threat 3 · provinces 15 (+0) · ceiling 48937 · army 70441 · vassals Holland 97
  - NET income 1580 · trade 430 · admin 50 · upkeep 528 · charges 385 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `sr5b-accept-ulm_t30` → Game saved: sr5b-accept-ulm_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15163 · net +1089 · threat 0 · provinces 15 (+0) · ceiling 49187 · army 68527 · vassals Holland 96
  - NET income 1580 · trade 430 · admin 50 · upkeep 520 · charges 421 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16260 · net +1062 · threat 0 · provinces 15 (+0) · ceiling 49437 · army 66709 · vassals Holland 95
  - NET income 1580 · trade 430 · admin 50 · upkeep 512 · charges 456 · occupation 30
- DISPATCH: Sire — the levy has stood open 22 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 32 — Early January 1807
  - saved `sr5b-accept-ulm_t32` → Game saved: sr5b-accept-ulm_t32
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17330 · net +1036 · threat 0 · provinces 15 (+0) · ceiling 49687 · army 64983 · vassals Holland 94
  - NET income 1580 · trade 430 · admin 50 · upkeep 504 · charges 490 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18394 · net +1030 · threat 0 · provinces 15 (+0) · ceiling 50562 · army 63344 · vassals Holland 93
  - NET income 1600 · trade 430 · admin 50 · upkeep 496 · charges 524 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 26 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 34 — Early February 1807
  - saved `sr5b-accept-ulm_t34` → Game saved: sr5b-accept-ulm_t34
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 19448 · net +1357 · threat 0 · provinces 15 (+0) · ceiling 61843 · army 61787 · vassals Holland 92
  - NET income 1600 · trade 430 · admin 50 · tribute 337 · upkeep 472 · charges 558 · occupation 30
- DISPATCH: Sire — the levy has stood open 25 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 35 — Late February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 20813 · net +1321 · threat 0 · provinces 15 (+0) · ceiling 62093 · army 60304 · vassals Holland 91
  - NET income 1600 · trade 430 · admin 50 · tribute 337 · upkeep 464 · charges 602 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 28 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 36 — Early March 1807
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #23 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 30 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - saved `sr5b-accept-ulm_t36` → Game saved: sr5b-accept-ulm_t36
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21805 · net +961 · threat 0 · provinces 15 (+0) · ceiling 51812 · army 58899 · vassals Holland 100
  - NET income 1600 · trade 430 · admin 50 · upkeep 456 · charges 633 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 29 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22798 · net +961 · threat 0 · provinces 15 (+0) · ceiling 52812 · army 57561 · vassals Holland 100
  - NET income 1600 · trade 430 · admin 50 · upkeep 424 · charges 665 · occupation 30
- DISPATCH: Sire — the levy has stood open 28 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
  - saved `sr5b-accept-ulm_t38` → Game saved: sr5b-accept-ulm_t38
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23759 · net +930 · threat 0 · provinces 15 (+0) · ceiling 52812 · army 56291 · vassals Holland 100
  - NET income 1600 · trade 430 · admin 50 · upkeep 424 · charges 696 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 31 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_auto_downgrade)
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 40% of active European bloc power.

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24697 · net +908 · threat 0 · provinces 15 (+0) · ceiling 53062 · army 55085 · vassals Holland 100
  - NET income 1600 · trade 430 · admin 50 · upkeep 416 · charges 726 · occupation 30
- DISPATCH: Sire — Marshal Soult's claim is 32 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `sr5b-accept-ulm_t40` → Game saved: sr5b-accept-ulm_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25613 · net +887 · threat 0 · provinces 15 (+0) · ceiling 53312 · army 53938 · vassals Holland 100
  - NET income 1600 · trade 430 · admin 50 · upkeep 408 · charges 755 · occupation 30
- DISPATCH: Sire — the levy has stood open 31 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 125 · popups 64 · battles 26
