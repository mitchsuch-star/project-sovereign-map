# Playtest digest — tutorial-run

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Your campaign autosave is untouched.

## Turn 1 — Late September 1805
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Senarmont, move to Munich` → ✓ Senarmont moves from Franche-Comte to Munich (280 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 6 (VI. The Guns Speak) — approximate
- LEDGER treasury 4663 · net +3670 · threat 20 · provinces 28
  - NET income 3400 · trade 200 · tribute 937 · upkeep 824 · charges 93
- DISPATCH: Sire — the establishment stands 26,280 men under the ordinance, and the depots hold 82,400. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (open borders agreement)

## Turn 2 — Early October 1805
- CMD `Ney, defend` → ✓ Ney firmly objects: 'Sire, we have the advantage. Let me strike!'
  - POPUP objection: Ney, Ney firmly objects: 'Sire, we have the advantage. Let me strike!' → insist
- CMD `Senarmont, bombard Jellacic` → ✓ Senarmont firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.'
  - POPUP objection: Senarmont, Senarmont firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' → insist
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 1 attacks — ArchdukeCharles engages in solid combat. Brutal stalemate between ArchdukeCharles and Senarmont. Heavy casualties on bo…
  - ⚔ Archduke Charles (lost 1925) vs Senarmont (lost 2217) — Neither Senarmont nor Archduke Charles could claim the field. The armies remain locked.
  - verbs: attack×1, fortify×1, move×1, stance_change×1
- SCHOOL step 6 (VI. The Guns Speak) — approximate
- LEDGER treasury 8231 · net +3533 · threat 20 · provinces 28 (+0)
  - NET income 3400 · trade 200 · tribute 937 · upkeep 808 · charges 246
- DISPATCH: Sire — the establishment stands 28,689 men under the ordinance, and the depots hold 84,700. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: Sweden rebuffs Austria (open borders agreement)

## Turn 3 — Late October 1805
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 4 actions, 3 attacks — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Senarmont. Heavy casualties o… · Schwarzenberg's forces advance steadily. Schwarzenberg gains the advantage over Senarmont. Casualties: Schwarzenberg 1,… · Kienmayer flanks from Swabia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 1608) vs Senarmont (lost 1938) — Stalemate. Senarmont and Archduke Charles glare at each other across the field.
  - ⚔ Schwarzenberg (lost 1232) vs Senarmont (lost 2147) — The hills were ours, but Schwarzenberg took them. Senarmont's position was overrun.
  - ⚔ Kienmayer (lost 1029) vs Senarmont (lost 848) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×3, fortify×1
- SCHOOL step 7 (VII. First Blood) — approximate
- LEDGER treasury 11530 · net +3381 · threat 20 · provinces 28 (+0)
  - NET income 3400 · trade 200 · tribute 937 · upkeep 768 · charges 438
- DISPATCH: Sire — Senarmont was mauled at Munich: a quarter of his corps — 2,147 men — lost in a single action.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (open borders agreement)

## Turn 4 — Early November 1805
- CMD `Ney, attack Kienmayer` → ✓ MUSTER — Ney (24,000; 46,849 if all march, up to 51,992 if every corps arrives) vs Kienmayer (small force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 373, own corps) vs Kienmayer (lost 5501) — Davout's timely arrival aided Ney. Senarmont, however, was conspicuously absent.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 action(s) unused) Turn 5 begins!
- enemy phase: 3 actions, 1 attacks — Schwarzenberg delivers an effective strike. Brutal stalemate between Schwarzenberg and Senarmont. Heavy casualties on b…
  - ⚔ Schwarzenberg (lost 2655) vs Senarmont (lost 206) — Ney reached the field beside Senarmont, Sire — it saved the line, no more.
  - verbs: attack×1, stance_change×1, fortify×1
- SCHOOL step 8 (VIII. Standing Orders) — approximate
- LEDGER treasury 14389 · net +2750 · threat 23 · provinces 28 (+0)
  - NET income 3400 · trade 200 · tribute 937 · upkeep 736 · charges 1001 · contributions 100
- DISPATCH: Sire — Kienmayer has crossed into Franche-Comte. No French corps stands in his path.

## Turn 5 — Late November 1805
- CMD `Davout, march to Franconia` → ✓ Davout begins march to Franconia. Moves to Franconia. Davout: "We move deliberately — arrival is worth little if the army arrives broken."
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 action(s) unused) Turn 6 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- ORDER Davout [active]: Davout is marching to Franconia (0 turn(s) remaining).
- SCHOOL step 10 (X. The Conqueror's Choice) — approximate
- LEDGER treasury 17050 · net +2437 · threat 23 · provinces 28 (+0)
  - NET income 3400 · trade 200 · tribute 937 · upkeep 736 · charges 1264 · contributions 150
- DISPATCH: Sire — Kienmayer has crossed into Lorraine. No French corps stands in his path.
  - TURN EVENTS 2

## Turn 6 — Early December 1805
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (503 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Davout → secure
- CMD `Davout, attack Archduke Charles` → ✓ Davout notes the risks but prepares the attack. Davout halts before the order is carried out. "I will go if you order it, Sire — but look at the ground first. This is no…
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I will go if you order it, Sire — but look at the ground first. This is not a battle, it is an arithmetic problem."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (24,550) vs ArchdukeCharles (19,813 men) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Senarmont: is willing to march if the roads allow
  ArchdukeCharles does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.
  Tyrol feeds 20,000 — the whole muster standing there would lose ~83 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 4341) vs Archduke Charles (lost 686) — Davout stood alone, Sire. Senarmont never came.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 action(s) unused) Turn 7 begins!
- enemy phase: 4 actions, 2 attacks — ArchdukeCharles strikes back after successfully defending! · Jellacic holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 1146, own corps) vs Davout (lost 2764) — A narrow defeat for Davout, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Jellacic (lost 362, own corps) vs Davout (lost 2446) — The margin was slim. Training and preparation would serve Davout well.
  - verbs: attack×2, unfortify×1, move×1
- ENVOYS WAITING 1 · Austria armistice losing
- SCHOOL step 11 (XI. The Depots) — approximate
- LEDGER treasury 18869 · net +2077 · threat 25 · provinces 29 (+1)
  - NET income 3400 · trade 200 · tribute 937 · upkeep 648 · charges 1612 · contributions 150 · occupation 100
- DISPATCH: Sire — Bohemia has fallen to our arms. The tricolor flies over it this morning.
  - RAIL diplomatic_ai_proposal: A Austria envoy has arrived with a proposal.
  - TURN EVENTS 2

## Turn 7 — Late December 1805
  - MAILBOX #1 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #2 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (stale passthrough — #2 already answered this chain)
- CMD `Soult, recruit troops` → ✓ Soult recruits 10,000 infantry at Paris - Cost: 450 gold (capital discount). Morale: 100% -> 88%
- CMD `build watchtower in Lorraine` → ✓ Construction started: Watchtower in Lorraine (2 turns, 250 gold)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 5 actions, 2 attacks — ArchdukeCharles's attack meets fierce resistance. ArchdukeCharles gains the advantage over Davout. Casualties: Archduke… · Kienmayer marches from Lorraine into Lorraine unopposed! (14 lost to march) Captured: France → Austria
  - 🏴 Austria: Casualties: ArchdukeCharles's army 927, Davout 2,829. Both armies remain in the field. Bohemia has been captured by Austria!
  - 🏴 Austria: Kienmayer marches from Lorraine into Lorraine unopposed! (14 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 677, own corps) vs Davout (lost 2829) — Davout was driven from the field. His men are scattered.
  - verbs: attack×2, unfortify×1, fortify×1, move×1
- SCHOOL step 12 (XII. The Fog) — approximate
- LEDGER treasury 20577 · net +2418 · threat 26 · provinces 27 (-2)
  - NET income 3250 · trade 200 · tribute 937 · upkeep 704 · charges 1315
- DISPATCH: Sire — Lorraine has fallen. Enemy colours fly over French homeland soil. Kienmayer's corps of ~2,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garr…
  - TURN EVENTS 2
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 8 — Early January 1806
- CMD `Davout, scout Bohemia` → ✗ Davout is recovering from retreat and cannot scout. Recovery: 1 turn(s) remaining.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 5 actions, 2 attacks — ArchdukeCharles engages in solid combat. Brutal stalemate between ArchdukeCharles and Davout. Heavy casualties on both … · Schwarzenberg's forces press forward aggressively. Schwarzenberg gains the advantage over Senarmont. Casualties: Schwar…
  - ⚔ Archduke Charles (lost 1992) vs Davout (lost 761) — Reinforcements from Ney bolstered Davout's position — though Senarmont never arrived, Sire.
  - ⚔ Schwarzenberg (lost 677) vs Senarmont (lost 1801) — The hills were ours, but Schwarzenberg took them. Senarmont's position was overrun.
  - verbs: attack×2, unfortify×1, move×1, fortify×1
- SCHOOL step 13 (XIII. The Counter-Blow) — approximate
- LEDGER treasury 21481 · net +950 · threat 27 · provinces 27 (+0)
  - NET income 3250 · trade 200 · tribute 937 · upkeep 672 · charges 2665 · contributions 150
- DISPATCH: Sire — Davout's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 2

## Turn 9 — Late January 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' → insist
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 action(s) unused) Turn 10 begins!
- enemy phase: 1 actions, 1 attacks — Schwarzenberg launches a decisive assault. Schwarzenberg gains the advantage over Davout. Casualties: Schwarzenberg 620…
  - ⚔ Schwarzenberg (lost 620) vs Davout (lost 2959) — Even the favorable ground could not save Davout, Sire. Schwarzenberg overcame the terrain.
  - verbs: attack×1
- SCHOOL step 14 (XIV. The Instruments) — approximate
- LEDGER treasury 22928 · net +1437 · threat 28 · provinces 27 (+0)
  - NET income 3250 · trade 200 · tribute 937 · upkeep 640 · charges 2360
- DISPATCH: Sire — Davout's corps has been broken at Munich. He must reform before he fights again.
  - TURN EVENTS 5

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 14 (XIV. The Instruments) — approximate
- LEDGER treasury 24298 · net +1211 · threat 29 · provinces 27 (+0)
  - NET income 3250 · trade 200 · tribute 937 · upkeep 640 · charges 2586
- DISPATCH: Sire — the levy has stood open 10 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 25288 · net +872 · threat 28 · provinces 27 (+0)
  - NET income 3250 · trade 200 · tribute 937 · upkeep 640 · charges 2775 · contributions 150
- DISPATCH: Sire — Kienmayer has crossed into Rhineland. No French corps stands in his path.
  - TURN EVENTS 2

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 26934 · net +1494 · threat 27 · provinces 27 (+0)
  - NET income 3250 · trade 200 · tribute 937 · upkeep 640 · charges 2303
- DISPATCH: Sire — the levy has stood open 12 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 2

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 28348 · net +1279 · threat 26 · provinces 27 (+0)
  - NET income 3250 · trade 200 · tribute 937 · upkeep 640 · charges 2518
- DISPATCH: Sire — the levy has stood open 13 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 2

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 1 actions, 1 attacks — Kienmayer marches from Lorraine into Rhineland unopposed! (73 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Lorraine into Rhineland unopposed! (73 lost to march) Captured: France → Austria
  - verbs: attack×1
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 29392 · net +941 · threat 25 · provinces 26 (-1)
  - NET income 3100 · trade 200 · tribute 937 · upkeep 640 · charges 2706
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil. Kienmayer's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any ga…
  - TURN EVENTS 2

## Turn 15 — Late April 1806
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 30246 · net +766 · threat 24 · provinces 26 (+0)
  - NET income 3100 · trade 200 · tribute 937 · upkeep 640 · charges 2881
- DISPATCH: Sire — the levy has stood open 15 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 2

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 2 actions, 2 attacks — Kienmayer marches from Lorraine into Orleanais unopposed! (73 lost to march) Captured: France → Austria · Kienmayer marches from Orleanais into Flanders unopposed! (72 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Lorraine into Orleanais unopposed! (73 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Orleanais into Flanders unopposed! (72 lost to march) Captured: France → Austria
  - verbs: attack×2
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 30622 · net +336 · threat 23 · provinces 24 (-2)
  - NET income 2800 · trade 200 · tribute 937 · upkeep 640 · charges 3011
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - TURN EVENTS 2

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 3 actions, 3 attacks — Kienmayer marches from Flanders into Picardy unopposed! (71 lost to march) Captured: France → Austria · Kienmayer marches from Picardy into Artois unopposed! (71 lost to march) Captured: France → Austria · Kienmayer marches from Artois into Champagne unopposed! (70 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Flanders into Picardy unopposed! (71 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Picardy into Artois unopposed! (71 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Artois into Champagne unopposed! (70 lost to march) Captured: France → Austria
  - verbs: attack×3
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 29758 · net -744 · threat 22 · provinces 21 (-3)
  - NET income 2550 · trade 200 · tribute 937 · upkeep 640 · charges 3841
- DISPATCH: Sire — Picardy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - TURN EVENTS 2

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 1 actions, 1 attacks — Kienmayer marches from Champagne into Limousin unopposed! (69 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Champagne into Limousin unopposed! (69 lost to march) Captured: France → Austria
  - verbs: attack×1
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 28775 · net -844 · threat 21 · provinces 20 (-1)
  - NET income 2400 · trade 200 · tribute 937 · upkeep 640 · charges 3791
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil. Kienmayer's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any gar…
  - TURN EVENTS 2

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 2 actions, 2 attacks — Kienmayer marches from Limousin into Berry unopposed! (68 lost to march) Captured: France → Austria · Kienmayer marches from Berry into Gascony unopposed! (136 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Limousin into Berry unopposed! (68 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Berry into Gascony unopposed! (136 lost to march) Captured: France → Austria
  - verbs: attack×2
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 27495 · net -1094 · threat 20 · provinces 18 (-2)
  - NET income 2050 · trade 200 · tribute 937 · upkeep 640 · charges 3691
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - TURN EVENTS 2

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 4 actions, 4 attacks — Kienmayer marches from Gascony into Guyenne unopposed! (66 lost to march) Captured: France → Austria · Kienmayer marches from Guyenne into Anjou unopposed! (66 lost to march) Captured: France → Austria · Kienmayer marches from Anjou into Maine unopposed! (65 lost to march) Captured: France → Austria · Kienmayer marches from Maine into Brittany unopposed! (64 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Gascony into Guyenne unopposed! (66 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Guyenne into Anjou unopposed! (66 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Anjou into Maine unopposed! (65 lost to march) Captured: France → Austria
  - 🏴 Austria: Kienmayer marches from Maine into Brittany unopposed! (64 lost to march) Captured: France → Austria
  - verbs: attack×4
- SCHOOL step 15 (XV. The Lesson Ends) — approximate
- LEDGER treasury 25819 · net -1428 · threat 19 · provinces 14 (-4)
  - NET income 1550 · trade 200 · tribute 937 · upkeep 640 · charges 3525
- DISPATCH: Sire — Guyenne has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - TURN EVENTS 2

---
finished: **completed** · commands 33 · popups 10 · battles 13
