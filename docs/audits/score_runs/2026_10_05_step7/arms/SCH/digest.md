# Playtest digest — SCH

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "missions": "begin"}`
- played: board `tutorial` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `e83be52a3dea` (dirty) · content `d32f29a1b134` · driver `393aff09ac1c`
  - new game → New campaign started. Your campaign autosave is untouched.

## Turn 1 — Late September 1805
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Senarmont, move to Munich` → ✓ Senarmont moves from Franche-Comte to Munich (280 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 actions unused) Turn 2 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 6 (VI. The Guns Speak) — approximate
- LEDGER treasury 4663 · net +3661 · threat 23 · provinces 28 · ceiling 99994 · army 103720 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 98
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 824 · charges 102
- DISPATCH: Sire — the establishment stands 26,280 men under the ordinance, and the depots hold 82,400. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (open borders agreement)

## Turn 2 — Early October 1805
- CMD `Ney, defend` → ✓ Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Kienmayer at Swabia instead.)
  - POPUP objection: Ney, Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Kienmayer at Swabia instead.) → insist
- CMD `Senarmont, bombard Jellacic` → ✓ Senarmont firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will adopt DEFENSIVE stance instead.)
  - POPUP objection: Senarmont, Senarmont firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will adopt DEFENSIVE stance instead.) → insist
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 1 attacks — Archduke Charles engages in solid combat. Brutal stalemate between Archduke Charles and Senarmont. Heavy casualties on …
  - ⚔ Archduke Charles (lost 1925) vs Senarmont (lost 2196) — Neither Senarmont nor Archduke Charles could claim the field. The armies remain locked.
  - verbs: attack×1, fortify×1, move×1, stance_change×1
- SCHOOL step 7 (VII. The Cabinet) — approximate
- LEDGER treasury 8232 · net +3513 · threat 26 · provinces 28 (+0) · ceiling 90294 · army 101332 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 96
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 808 · charges 266
- DISPATCH: Sire — the establishment stands 28,668 men under the ordinance, and the depots hold 84,700. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Austria (open borders agreement)

## Turn 3 — Late October 1805
- CMD `gather intel on Austria` → ✓ Sire, I shall begin efforts to gather intelligence on Austria. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #1 → start_mission
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 3 attacks — Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Senarmont. Heavy casualties… · Schwarzenberg's forces advance steadily. Schwarzenberg gains the advantage over Senarmont. Casualties: Schwarzenberg 1,… · Kienmayer flanks from Swabia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 1611) vs Senarmont (lost 1889) — Stalemate. Senarmont and Archduke Charles glare at each other across the field.
  - ⚔ Schwarzenberg (lost 1241) vs Senarmont (lost 2193) — The hills were ours, but Schwarzenberg took them. Senarmont's position was overrun.
  - ⚔ Kienmayer (lost 1032) vs Senarmont (lost 899) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×3, fortify×1
- SCHOOL step 8 (VIII. First Blood) — approximate
- LEDGER treasury 11529 · net +3351 · threat 29 · provinces 28 (+0) · ceiling 79621 · army 96351 · vassals Holland 92 · Kingdom of Italy 92 · Switzerland 92
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 768 · charges 468
- MISSION Gathering Intel — Austria · net +0 a turn · 2 turns left, then 7 provinces of Austria open to us for 5 turns · beat running
- DISPATCH: Sire — Senarmont was mauled at Munich: a quarter of his corps — 2,193 men — lost in a single action.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (open borders agreement)

## Turn 4 — Early November 1805
- CMD `Ney, attack Kienmayer` → ✓ MUSTER — Ney (24,000; expect about 47,991 with the corps likely to arrive, up to 53,142 if all march) vs Kienmayer (small force) at Swabia — the balance of force looks f…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 463, own corps) vs Kienmayer (lost 5773) — Davout's timely arrival aided Ney. Senarmont, however, was conspicuously absent.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: stance_change×1, fortify×1
- SCHOOL step 10 (X. Standing Orders) — approximate
- LEDGER treasury 14471 · net +2703 · threat 35 · provinces 28 (+0) · ceiling 47108 · army 95187 · vassals Holland 91 · Kingdom of Italy 91 · Switzerland 91
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 752 · charges 1032 · contributions 100
- MISSION Gathering Intel — Austria · net +0 a turn · 1 turn left, then 7 provinces of Austria open to us for 5 turns · beat running
- DISPATCH: Sire — Kienmayer has crossed into Franche-Comte. No French corps stands in his path.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 5 — Late November 1805
- CMD `Davout, march to Franconia` → ✓ Davout begins march to Franconia. Moves to Franconia. Davout: "We move deliberately — arrival is worth little if the army arrives broken."
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: unfortify×1, forced_march×1
- ORDER Davout [active]: Davout is marching to Franconia (0 turns remaining).
- SCHOOL step 12 (XII. The Conqueror's Choice) — approximate
- LEDGER treasury 17124 · net +2385 · threat 38 · provinces 28 (+0) · ceiling 44848 · army 94638 · vassals Holland 89 · Kingdom of Italy 89 · Switzerland 89
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 752 · charges 1300 · contributions 150
- MISSION ended: Gathering Intel — Austria, done — 7 provinces open to us until turn 11
- DISPATCH: Sire — Kienmayer has crossed into Lorraine. No French corps stands in his path.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_completed)

## Turn 6 — Early December 1805
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (510 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Davout → secure
- CMD `Davout, attack Archduke Charles` → ✓ Davout notes the risks but prepares the attack. Davout halts before the order is carried out. "I will go if you order it, Sire — but look at the ground first. This is no…
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I will go if you order it, Sire — but look at the ground first. This is not a battle, it is an arithmetic problem."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (24,641) vs Archduke Charles (19,757 men) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Senarmont: is willing to march if the roads allow — he will NOT make it from the mountains at Munich in time; order 'Senarmont, support Davout' and it rises to about 76%
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.
  The band weighs more than the men: the ground favors the defender (+25%, mountains); Archduke Charles stands +53% on the defense (his stance, his character and his works).
  Tyrol feeds 20,000 — the whole muster standing there would lose ~85 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Davout (24,641) vs Archduke Charles (19,757 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 4634) vs Archduke Charles (lost 745, own corps) — Davout stood alone, Sire. Senarmont never came.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 6 actions, 2 attacks — ArchdukeCharles strikes back after successfully defending! · Jellacic holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: Casualties: Jellacic's army 1,171, Davout 2,760. Both armies remain in the field. Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1197, own corps) vs Davout (lost 2917) — A narrow defeat for Davout, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Jellacic (lost 454, own corps) vs Davout (lost 2760) — The margin was slim. Training and preparation would serve Davout well.
  - verbs: move×3, attack×2, unfortify×1
- ENVOYS WAITING 1 · Austria armistice losing
- SCHOOL step 13 (XIII. The Depots) — approximate
- LEDGER treasury 18998 · net +2108 · threat 43 · provinces 28 (+0) · ceiling 40500 · army 83746 · vassals Holland 81 · Kingdom of Italy 81 · Switzerland 81
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 664 · charges 1665 · contributions 150
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 7 — Late December 1805
  - MAILBOX #1 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #3 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `Soult, recruit troops` → ✓ Soult recruits 10,000 infantry at Paris - Cost: 450 gold (capital discount) (×3 at war). Morale: 100% -> 88%
- CMD `build watchtower in Lorraine` → ✓ Construction started: Watchtower in Lorraine (2 turns, 250 gold)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- SPENT 700g on this turn's orders
- enemy phase: 5 actions, 0 attacks
  - verbs: move×3, unfortify×1, fortify×1
- SCHOOL step 14 (XIV. The Fog) — approximate
- LEDGER treasury 20344 · net +1837 · threat 45 · provinces 28 (+0) · ceiling 38492 · army 93746 · vassals Holland 79 · Kingdom of Italy 79 · Switzerland 79
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 744 · charges 1856 · contributions 150
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 8 — Early January 1806
- CMD `Davout, scout Bohemia` → ✓ Davout scouts Bohemia: Controlled by Austria. Terrain: Plains. Enemy forces: Jellacic (Austria): ~6,266 troops; Schwarzenberg (Austria): ~19,687 troops
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: move×1, fortify×1
- SCHOOL step 15 (XV. The Counter-Blow) — approximate
- LEDGER treasury 22161 · net +1569 · threat 47 · provinces 28 (+0) · ceiling 37181 · army 93746 · vassals Holland 77 · Kingdom of Italy 77 · Switzerland 77
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 744 · charges 2104 · contributions 150 · infrastructure 20
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 9 — Late January 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Kienmayer at Lorraine instead.)
  - POPUP objection: Ney, Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Trust him and he will attack Kienmayer at Lorraine instead.) → insist
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 6 actions, 1 attacks — Schwarzenberg executes a brilliant maneuver! Schwarzenberg gains the advantage over Davout. Casualties: Schwarzenberg 6…
  - ⚔ Schwarzenberg (lost 606) vs Davout (lost 5223) — Where was Senarmont? Davout held the field alone — reinforcement never came.
  - verbs: unfortify×2, move×2, attack×1, fortify×1
- SCHOOL step 16 (XVI. The Wooden Wall) — approximate
- LEDGER treasury 23448 · net +1311 · threat 49 · provinces 28 (+0) · ceiling 35104 · army 88478 · vassals Holland 73 · Kingdom of Italy 73 · Switzerland 73
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 696 · charges 2410 · contributions 150 · infrastructure 20
- DISPATCH: Sire — Davout's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 6 actions, 1 attacks — Schwarzenberg launches a devastating assault! Schwarzenberg gains the advantage over Senarmont. Casualties: Schwarzenbe…
  - ⚔ Schwarzenberg (lost 830) vs Senarmont (lost 1846) — Senarmont held superior ground, yet Schwarzenberg prevailed. A grim day, Sire.
  - verbs: move×2, recruit×2, unfortify×1, attack×1
- SCHOOL step 17 (XVII. The Congress of Paris) — approximate
- LEDGER treasury 24659 · net +1082 · threat 51 · provinces 28 (+0) · ceiling 33885 · army 86632 · vassals Holland 69 · Kingdom of Italy 69 · Switzerland 69
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 680 · charges 2655 · contributions 150 · infrastructure 20
- DISPATCH: Sire — Senarmont was mauled at Munich: a quarter of his corps — 1,846 men — lost in a single action.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 1 attacks — Schwarzenberg engages in solid combat. Schwarzenberg gains the advantage over Senarmont. Casualties: Schwarzenberg 720,…
  - ⚔ Schwarzenberg (lost 720) vs Senarmont (lost 652, own corps) — Davout marched to Senarmont's guns as ordered. It was not enough.
  - verbs: attack×1
- SCHOOL step 18 (XVIII. The Laws of State) — approximate
- LEDGER treasury 25602 · net +881 · threat 51 · provinces 28 (+0) · ceiling 32792 · army 83039 · vassals Holland 65 · Kingdom of Italy 65 · Switzerland 65
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 648 · charges 2888 · contributions 150 · infrastructure 20
- MISSION ended: Gathering Intel — Austria, done
- DISPATCH: Sire — Senarmont's corps has been broken at Munich. He must reform before he fights again.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 12 — Early March 1806
- CMD `enact the Staff` → ✓ The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day…
  - POPUP clarification: The Council of State, The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day. 9,000 gold now, then 300 gold a turn; one more order each day from the next refill. The treasury holds 25,602 gold. Enact it? (yes / no) → 1 (first option: Enact the Grand Quartier Général)
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- SPENT 9000g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
- SCHOOL step 19 (XIX. The Instruments) — approximate
- LEDGER treasury 18259 · net +1427 · threat 51 · provinces 28 (+0) · ceiling 29619 · army 82379 · vassals Holland 63 · Kingdom of Italy 63 · Switzerland 63
  - NET income 3400 · trade 200 · admin 50 · tribute 937 · upkeep 648 · charges 2042 · contributions 150 · infrastructure 20 · laws 300
- DISPATCH: Sire — the enemy has stood on our ground 9 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 27 · popups 11 · battles 11
