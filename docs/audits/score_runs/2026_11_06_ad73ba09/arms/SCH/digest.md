# Playtest digest — SCH

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "missions": "begin"}`
- played: board `tutorial` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - new game → New campaign started. Your campaign autosave is untouched.

## Turn 1 — Late September 1805
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Senarmont, move to Munich` → ✓ Senarmont moves from Franche-Comte to Munich (280 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 actions unused) Turn 2 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 6 (VI. The Guns Speak) — approximate
- LEDGER treasury 4507 · net +3289 · threat 23 · provinces 28 · ceiling 30356 · army 103720 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 98
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 980 · charges 318
- DISPATCH: Sire — the ordinance allows 26,280 more men to the establishment, and the depots hold 82,375. 10,000 foot cost 450 gold at Paris under Soult — 'recruit infantry in Paris'.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 2 — Early October 1805
- CMD `Ney, defend` → ✓ Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Kienmayer at Swabia instead.)
  - POPUP objection: Ney, Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Kienmayer at Swabia instead.) → insist
- CMD `Senarmont, bombard Jellacic` → ✓ Senarmont firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will retreat from current position instead.)
  - POPUP objection: Senarmont, Senarmont firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will retreat from current position instead.) → insist
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 1 attacks — Archduke Charles attacks Senarmont
  - ⚔ Archduke Charles (lost 1717) vs Senarmont (lost 2285) — Neither Senarmont nor Archduke Charles could claim the field. The armies remain locked.
  - verbs: attack×1, fortify×1, move×1, stance_change×1
- SCHOOL step 7 (VII. The Cabinet) — approximate
- LEDGER treasury 7731 · net +2889 · threat 26 · provinces 28 (+0) · ceiling 29545 · army 101243 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 96
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 940 · charges 758
- DISPATCH: Sire — At this pace the courts consult on turn 24 and declare on turn 27: Britain and Russia would march. The cheapest court to keep out of it is Britain: Talleyrand brings her to −10 in 1 turn (1 DP…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 3 — Late October 1805
- CMD `gather intel on Austria` → ✓ Sire, I shall begin efforts to gather intelligence on Austria. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #1 → start_mission
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 3 attacks — Archduke Charles attacks Senarmont · Schwarzenberg attacks Senarmont · Kienmayer attacks Senarmont
  - ⚔ Archduke Charles (lost 1426) vs Senarmont (lost 2136) — Stalemate. Senarmont and Archduke Charles glare at each other across the field.
  - ⚔ Schwarzenberg (lost 1344) vs Senarmont (lost 2046) — The hills were ours, but Schwarzenberg took them. Senarmont's position was overrun.
  - ⚔ Kienmayer (lost 1005) vs Senarmont (lost 919) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×3, fortify×1
- SCHOOL step 8 (VIII. First Blood) — approximate
- LEDGER treasury 10476 · net +2561 · threat 29 · provinces 28 (+0) · ceiling 28764 · army 96142 · vassals Holland 92 · Kingdom of Italy 92 · Switzerland 92
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 840 · charges 1186
- MISSION Gathering Intel — Austria · net +0 a turn · 2 turns left, then 7 provinces of Austria open to us for 5 turns · beat running
- DISPATCH: Sire — Senarmont was mauled at Munich: a quarter of his corps — 2,136 men — lost in a single action.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 4 — Early November 1805
- CMD `Ney, attack Kienmayer` → ✓ MUSTER — Ney (24,000; expect about 47,991 with the corps likely to arrive, up to 48,570 if all march; certain 24,000) vs Kienmayer (small force) at Swabia — the balance …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 465, own corps) vs Kienmayer (lost 5797) — Davout's timely arrival aided Ney. Senarmont, however, was conspicuously absent.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 actions unused) Turn 5 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 10 (X. Standing Orders) — approximate
- LEDGER treasury 12088 · net +1336 · threat 35 · provinces 28 (+0) · ceiling 19782 · army 94975 · vassals Holland 91 · Kingdom of Italy 91 · Switzerland 91
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1400 · charges 1751 · contributions 100
- MISSION Gathering Intel — Austria · net +0 a turn · 1 turn left, then 7 provinces of Austria open to us for 5 turns · beat running
- DISPATCH: Sire — Kienmayer has crossed into Franche-Comte. No French corps stands in his path.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 5 — Late November 1805
- CMD `Davout, march to Franconia` → ✓ Davout begins march to Franconia. Moves to Franconia. Davout: "We move deliberately — arrival is worth little if the army arrives broken."
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: unfortify×1, forced_march×1, recruit×1
- ORDER Davout [completed]: Davout arrives at Franconia. Davout: "Done, and done properly — no stragglers, no surprises."
- SCHOOL step 12 (XII. The Conqueror's Choice) — approximate
- LEDGER treasury 13374 · net +1027 · threat 38 · provinces 28 (+0) · ceiling 19177 · army 94426 · vassals Holland 89 · Kingdom of Italy 89 · Switzerland 89
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1400 · charges 2010 · contributions 150
- MISSION ended: Gathering Intel — Austria, done — 7 provinces open to us until turn 11
- DISPATCH: Sire — Kienmayer has crossed into Lorraine. No French corps stands in his path.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_completed)

## Turn 6 — Early December 1805
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (510 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Davout → secure
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will adopt DEFENSIVE stance instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will adopt DEFENSIVE stance instead.) → insist
  - ↳ MUSTER — Davout (24,640) vs Archduke Charles (23,023 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 5095) vs Archduke Charles (lost 754, own corps) — Davout stood alone, Sire. Senarmont never came.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 1 attacks — Archduke Charles attacks Davout
  - 🏴 Austria: Archduke Charles attacks Davout — Bohemia CAPTURED! (was France) (secured)
  - ⚔ Archduke Charles (lost 1268) vs Davout (lost 3710) — Davout's corps broke, Sire. They are streaming back from the field.
  - verbs: unfortify×1, attack×1, forced_march×1, move×1
- ENVOYS WAITING 1 · Austria armistice losing
- SCHOOL step 13 (XIII. The Depots) — approximate
- LEDGER treasury 14156 · net +957 · threat 43 · provinces 28 (+0) · ceiling 19254 · army 85032 · vassals Holland 83 · Kingdom of Italy 83 · Switzerland 83
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1200 · charges 2280 · contributions 150
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 7 — Late December 1805
  - MAILBOX #1 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #3 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `Soult, recruit troops` → ✓ Soult recruits 10,000 infantry at Paris - Cost: 450 gold (capital discount) (×3 at war). Morale: 100% -> 88%
- CMD `build watchtower in Lorraine` → ✓ Construction started: Watchtower in Lorraine (2 turns, 250 gold)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- SPENT 700g on this turn's orders
- enemy phase: 5 actions, 0 attacks
  - verbs: move×3, unfortify×1, fortify×1
- SCHOOL step 14 (XIV. The Fog) — approximate
- LEDGER treasury 14414 · net +789 · threat 45 · provinces 28 (+0) · ceiling 18546 · army 95032 · vassals Holland 81 · Kingdom of Italy 81 · Switzerland 81
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1280 · charges 2368 · contributions 150
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 8 — Early January 1806
- CMD `Davout, scout Bohemia` → ✓ Davout scouts Bohemia: Controlled by Austria. Terrain: Plains. Enemy forces: Archduke Charles (Austria): ~20,630 troops; Schwarzenberg (Austria): ~19,629 troops
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 5 actions, 0 attacks
  - verbs: move×2, recruit×2, fortify×1
- SCHOOL step 15 (XV. The Counter-Blow) — approximate
- LEDGER treasury 15183 · net +580 · threat 47 · provinces 28 (+0) · ceiling 18170 · army 95032 · vassals Holland 79 · Kingdom of Italy 79 · Switzerland 79
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1280 · charges 2557 · contributions 150 · infrastructure 20
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 9 — Late January 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Kienmayer at Lorraine instead.)
  - POPUP objection: Ney, Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Kienmayer at Lorraine instead.) → insist
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 5 actions, 2 attacks — Schwarzenberg attacks Davout · Schwarzenberg attacks Senarmont
  - ⚔ Schwarzenberg (lost 648) vs Davout (lost 4892) — Where was Senarmont? Davout held the field alone — reinforcement never came.
  - ⚔ Schwarzenberg (lost 757) vs Senarmont (lost 1787) — Senarmont held superior ground, yet Schwarzenberg prevailed. A grim day, Sire.
  - verbs: attack×2, recruit×2, fortify×1
- SCHOOL step 16 (XVI. The Wooden Wall) — approximate
- LEDGER treasury 15563 · net +527 · threat 49 · provinces 28 (+0) · ceiling 18158 · army 88299 · vassals Holland 73 · Kingdom of Italy 73 · Switzerland 73
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1140 · charges 2750 · contributions 150 · infrastructure 20
- DISPATCH: Sire — Davout's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 5 actions, 1 attacks — Jellacic attacks Senarmont
  - ⚔ Jellacic (lost 533) vs Senarmont (lost 909) — Even the favorable ground could not save Senarmont, Sire. Jellacic overcame the terrain.
  - verbs: unfortify×3, attack×1, move×1
- SCHOOL step 17 (XVII. The Congress of Paris) — approximate
- LEDGER treasury 16089 · net +410 · threat 51 · provinces 28 (+0) · ceiling 18070 · army 86627 · vassals Holland 69 · Kingdom of Italy 69 · Switzerland 69
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1100 · charges 2907 · contributions 150 · infrastructure 20
- DISPATCH: Sire — Senarmont's corps has been broken at Munich. He must reform before he fights again.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 18 (XVIII. The Laws of State) — approximate
- LEDGER treasury 16499 · net +279 · threat 51 · provinces 28 (+0) · ceiling 17825 · army 85896 · vassals Holland 67 · Kingdom of Italy 67 · Switzerland 67
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1100 · charges 3038 · contributions 150 · infrastructure 20
- MISSION ended: Gathering Intel — Austria, done
- DISPATCH: Sire — the enemy has stood on our ground 8 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 12 — Early March 1806
- CMD `enact the Staff` → ✓ The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day…
  - POPUP clarification: The Council of State, The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day. 9,000 gold now, then 300 gold a turn; one more order each day from the next refill. The treasury holds 16,499 gold. Enact it? (yes / no) → 1 (first option: Enact the Grand Quartier Général)
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- SPENT 9000g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 19 (XIX. The Instruments) — approximate
- LEDGER treasury 9359 · net +1472 · threat 51 · provinces 28 (+0) · ceiling 16271 · army 85180 · vassals Holland 65 · Kingdom of Italy 65 · Switzerland 65
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 1080 · charges 1565 · contributions 150 · infrastructure 20 · laws 300
- DISPATCH: Sire — the enemy has stood on our ground 9 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 27 · popups 11 · battles 10
