# Playtest digest — 1b-merchant-ulm-r1

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 837) vs Mack (lost 13501) — Davout, Lannes and Napoleon arrived to reinforce Ney, but Soult, Murat and Bernadotte failed to reach the field in time.
- CMD `Davout, fortify` → ✗ Davout cannot fortify while engaged with enemy forces! Enemy present: Mack. Attack or retreat first.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: 3 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Archduke Charles (lost 3024) vs Massena (lost 6243) — A narrow defeat for Massena, Sire. Better-prepared troops might have tipped the balance.
  - verbs: move×1, stance_change×1, attack×1
- LEDGER treasury 2375 · net +2008 · provinces 28
- DISPATCH: Supply cost you 3,447 men, at Swabia and Milan.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `build market in Paris` → ✓ Construction started: Market in Paris (2 turns, 350 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, m…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, fortify` → ✗ Massena cannot fortify while engaged with enemy forces! Enemy present: ArchdukeCharles, ArchdukeJohn. Attack or retreat first.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 2187) vs Massena (lost 6942) — Not one corps reached Massena. Murat was expected; Massena fought the battle single-handed.
  - ⚔ Archduke John (lost 284) vs Massena (lost 6104) — Where was Murat? Massena held the field alone — reinforcement never came.
  - verbs: attack×2, form_square×2
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 704) vs Mack (lost 19754) — Reinforcements from Lannes and Napoleon bolstered Murat's position — though Ney and Davout never arrived, Sire.
- LEDGER treasury 3865 · net +2485 · provinces 28 (+0)
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `build depot in Lorraine` → ✓ Construction started: Supply Depot in Lorraine (2 turns, 300 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `Murat, fortify` → ✓ Murat firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Murat, Murat firmly objects: 'I would rather attack than sit idle.' → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 218) vs Mack (lost 15567) — Lannes and Napoleon arrived to reinforce Murat! The timely arrival swung the battle in our favor, Sire.
  - POPUP capture_choice[capture]: Tyrol, Murat → secure
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!'
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 6930) vs Archduke Charles (lost 1029) — Lannes stood alone, Sire. Murat never came.
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 action(s) unused) Turn 4 begins!
- enemy phase: 5 actions, 3 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks] · [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeJohn breaks formation to attacks]
  - ⚔ Archduke Charles (lost 2236) vs Massena (lost 2575) — Ney arrived to reinforce Massena, but Davout, Murat and Bernadotte failed to reach the field in time.
  - ⚔ Archduke John (lost 332) vs Lannes (lost 496) — Reinforcements from Davout bolstered Lannes's position — though Murat and Bernadotte never arrived, Sire.
  - ⚔ Archduke Charles (lost 3223) vs Murat (lost 2820) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×3, form_square×2
- LEDGER treasury 5662 · net +2735 · provinces 29 (+1)
- DISPATCH: Sire — Lannes's corps has been broken at Tyrol. He must reform before he fights again.

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `build market in Lyonnais` → ✗ Cannot build in Lyonnais — town regions don't support buildings (need city or larger)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `Bernadotte, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Bernadotte fortifies position at Franconia. Defense bonus: +7% (grows +3% per t…
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 action(s) unused) Turn 5 begins!
- enemy phase: 5 actions, 4 attacks — [Square broken — ArchdukeJohn breaks formation to attacks] · [Square broken — ArchdukeCharles breaks formation to attacks] · ArchdukeCharles holds them at Franconia while allies attack from Munich! (+1 coordination) · ArchdukeCharles holds them at Franconia while allies attack from Munich! (+1 coordination)
  - ⚔ Archduke John (lost 2900) vs Lannes (lost 156) — Complete dominance on the field. Archduke John crumbled before Lannes.
  - ⚔ Archduke Charles (lost 1713) vs Bernadotte (lost 3307) — Where was Ney? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 1711) vs Bernadotte (lost 1025) — Ney arrived in time to steady Bernadotte's position. The field was held, nothing further.
  - ⚔ Archduke Charles (lost 1072) vs Bernadotte (lost 3286) — The battle unfolded without particular distinction.
  - verbs: attack×4, form_square×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 1414) vs Archduke John (lost 450) — Davout and Napoleon arrived to reinforce Ney, but Murat failed to reach the field in time.
- LEDGER treasury 7930 · net +2576 · provinces 29 (+0)
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field — and the laurels have passed to another.

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 5 actions, 2 attacks — ======================================== · Deroy marches from Bohemia into Franconia unopposed! (174 lost to march) Captured: Austria → Bavaria
  - 🏴 Austria: ========================================
  - 🏴 Bavaria: Deroy moves from Vienna to Bohemia. Bohemia falls to Bavaria! (was Austria) (176 lost to march)
  - 🏴 Bavaria: Deroy marches from Bohemia into Franconia unopposed! (174 lost to march) Captured: Austria → Bavaria
  - ⚔ Archduke Charles (lost 727) vs Bernadotte (lost 981) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×3, attack×2
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 762) vs Archduke Charles (lost 3312) — Davout and Napoleon's timely arrival aided Ney. Murat, however, was conspicuously absent.
- LEDGER treasury 10008 · net +2040 · provinces 29 (+0)
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field — and the laurels have passed to another.

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `build training ground in Paris` → ✓ Construction started: Training Ground in Paris (2 turns, 250 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 4 actions, 2 attacks — [Shield] ArchdukeJohn's DEFENSIVE stance strengthens the line! (+15% defense) · [!] ArchdukeJohn is EXPOSED! (Just retreated, no ally to cover)
  - 🏴 Bavaria: [Shield] ArchdukeJohn's DEFENSIVE stance strengthens the line! (+15% defense)
  - 🏴 Bavaria: [!] ArchdukeJohn is EXPOSED! (Just retreated, no ally to cover)
  - ⚔ Deroy (lost 868) vs Archduke John (lost 3004) — Archduke John held superior ground, yet Deroy prevailed. A grim day, Sire.
  - ⚔ Deroy (lost 210) vs Archduke John (lost 3305) — The toll on Archduke John's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, wait×1, grant_dotation×1
- LEDGER treasury 11805 · net +1807 · provinces 29 (+0)
- DISPATCH: Sire — 3 turns of famine at Tyrol now. 9,429 men gone, and not one of them to the enemy. No depot may be laid at Tyrol — region stability too low (45/100). Need 51+. Franconia can feed 60,000 more an…

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `sponsor prussia against austria, 200 gold` → ✗ Talleyrand: "Prussia's design is aimed at Hanover, not Austria. We can only arm the grievance they already hold."
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 13950 · net +1924 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Lannes, Murat, Bernadotte, Massena and Napoleon have been 4 turns over what Tyrol can feed. 11,158 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Fr…

## Turn 8 — Early January 1806
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `build market in Burgundy` → ✗ Cannot build in Burgundy — rural regions don't support buildings (need city or larger)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 15863 · net +1710 · provinces 29 (+0)
- DISPATCH: Sire — 4 turns without settlement on Marshal Murat. A rente would close it today; the arrears will not close themselves.

## Turn 9 — Late January 1806
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `buy off austria` → ✗ Talleyrand: "We are at WAR with Austria, Sire. Designs are bought off at the peace table, not across a battlefield."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 5 actions, 4 attacks — ArchdukeCharles assaults the Moravia garrison! Garrison: 6 -> 3 (-3). ArchdukeCharles loses 349 troops. Garrison holds … · ArchdukeCharles assaults the Moravia garrison! Garrison: 3 -> 2 (-1). ArchdukeCharles loses 342 troops. Garrison holds … · ArchdukeCharles assaults the Moravia garrison! Garrison: 2 -> 1 (-1). ArchdukeCharles loses 336 troops. Garrison holds … · ArchdukeCharles assaults the Moravia garrison! Garrison collapses (1 -> 0). ArchdukeCharles loses 329 troops in the ass…
  - 🏴 Austria: ArchdukeCharles assaults the Moravia garrison! Garrison collapses (1 -> 0). ArchdukeCharles loses 329 troops in the assault. ArchdukeCharles marches …
  - verbs: attack×4, forced_march×1
- LEDGER treasury 17547 · net +1500 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Lannes, Murat, Bernadotte, Massena and Napoleon have been 6 turns over what Tyrol can feed. 9,859 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Mil…

## Turn 10 — Early February 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `build depot in Rhineland` → ✓ Construction started: Supply Depot in Rhineland (2 turns, 300 gold)
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `guarantee bavaria` → ✓ France guarantees Bavaria. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility st…
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 18784 · net +1389 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Lannes, Murat, Bernadotte, Massena and Napoleon have been 7 turns over what Tyrol can feed. 9,228 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Mil…

## Turn 11 — Late February 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `commission Grouchy` → ✓ Marshal Grouchy accepts his commission and raises a corps of 5,000 at Paris — 4500g. He arrives with a history: Davout (Friendly), Murat (Rival).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 2 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 1277) vs Murat (lost 1869) — Even the favorable ground could not save Murat, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 887) vs Archduke Charles (lost 1531) — Reinforcements from Lannes, Massena and Napoleon bolstered Ney's position — though Murat never arrived, Sire.
- LEDGER treasury 15851 · net +1642 · provinces 29 (+0)
- DISPATCH: Sire — Ney's corps has been broken at Tyrol. He must reform before he fights again.

## Turn 12 — Early March 1806
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `build market in Normandy` → ✗ Cannot build in Normandy — rural regions don't support buildings (need city or larger)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- LEDGER treasury 17460 · net +1410 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Murat's grievance is 8 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 13 — Late March 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `build fort in Rhineland` → ✗ No building slots available in Rhineland (1/1)
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 4 actions, 3 attacks — ArchdukeCharles marches from Vienna into Bohemia unopposed! (378 lost to march — forward supply lines reduce losses) Ca… · [Square broken — ArchdukeCharles breaks formation to attacks] · ArchdukeCharles holds them at Hungary while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles marches from Vienna into Bohemia unopposed! (378 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1470) vs Deroy (lost 3340) — A narrow defeat for Deroy, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Archduke Charles (lost 994) vs Deroy (lost 2855) — The engagement proceeded as one might expect, Sire.
  - verbs: attack×3, form_square×1
- LEDGER treasury 18831 · net +1197 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Murat's grievance is 9 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 14 — Early April 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `sponsor prussia against austria, 300 gold` → ✗ Talleyrand: "Prussia's design is aimed at Hanover, not Austria. We can only arm the grievance they already hold."
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 6 actions, 2 attacks — ArchdukeCharles marches from Hungary into Hungary unopposed! (257 lost to march — forward supply lines reduce losses) C… · [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: ArchdukeCharles marches from Hungary into Hungary unopposed! (257 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 378) vs Deroy (lost 4432) — A grievous defeat for Deroy, Sire. The losses are severe.
  - verbs: attack×2, move×1, form_square×1, wait×1, recruit×1
- LEDGER treasury 19985 · net +1004 · provinces 29 (+0)
- DISPATCH: Sire — our ally's marshal Deroy was broken at Bohemia. Bavaria reels.

## Turn 15 — Late April 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `build market in Provence` → ✓ Construction started: Market in Provence (2 turns, 350 gold)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 7 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 1104) vs Lannes (lost 43) — Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away.
  - verbs: recruit×2, form_square×1, move×1, attack×1, fortify×1, wait×1
- LEDGER treasury 20587 · net +871 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Archduke John of Austria is taken at Tyrol — he is our prisoner, and their order of battle is one commander shorter.

## Turn 16 — Early May 1806
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `commission Suchet` → ✓ Marshal Suchet accepts his commission and raises a corps of 5,000 at Paris — 5500g. He arrives with a history: Lannes (Friendly).
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 7 actions, 0 attacks
  - verbs: recruit×2, form_square×1, move×1, fortify×1, wait×1, grant_pension×1
- LEDGER treasury 16630 · net +1358 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Lannes, Murat, Bernadotte, Massena and Napoleon stand 30,511 men at Tyrol, which feeds 30,000. 511 too many. 4,468 men lost in 3 turns. A supply depot at Tyrol would ease it; Milan can fe…

## Turn 17 — Late May 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `build depot in Flanders` → ✓ Construction started: Supply Depot in Flanders (2 turns, 300 gold)
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 5 actions, 0 attacks
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (97 lost to march)
  - verbs: move×2, form_square×1, fortify×1, wait×1
- LEDGER treasury 17344 · net +897 · provinces 28 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
- CMD `buy off russia` → ✗ Talleyrand: "We are at WAR with Russia, Sire. Designs are bought off at the peace table, not across a battlefield."
- CMD `guarantee saxony` → ✗ France already guarantees Saxony.
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 4 actions, 0 attacks
  - verbs: form_square×1, move×1, fortify×1, wait×1
- LEDGER treasury 18239 · net +768 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 19 — Late June 1806
- CMD `build market in Brittany` → ✗ Cannot build in Brittany — town regions don't support buildings (need city or larger)
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_proposal → reject_ai_proposal
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 8 actions, 0 attacks
  - verbs: move×2, recruit×2, form_square×1, fortify×1, grant_pension×1, wait×1
- LEDGER treasury 18478 · net +204 · provinces 28 (+0)
- DISPATCH: Sire — the levy has stood open 9 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.

## Turn 20 — Early July 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Saxony, non_aggression → (left standing)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 5 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 1101) vs Ney (lost 391) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: recruit×2, form_square×1, attack×1, wait×1
- LEDGER treasury 17988 · net -339 · provinces 28 (+0)
- DISPATCH: Sire — Ney's corps has been broken at Tyrol. He must reform before he fights again.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 8 actions, 2 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 348) vs Lannes (lost 310) — Even the favorable ground could not save Lannes, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke Charles (lost 198) vs Lannes (lost 256) — The hills were ours, but Archduke Charles took them. Lannes's position was overrun.
  - verbs: attack×2, recruit×2, unfortify×1, move×1, garrison×1, wait×1
- LEDGER treasury 17570 · net -267 · provinces 28 (+0)
- DISPATCH: Sire — Lannes, crowned three turns ago, has been beaten in the field.

## Turn 22 — Early August 1806
- CMD `build market in Gascony` → ✓ Construction started: Market in Gascony (2 turns, 350 gold)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 5 actions, 3 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — Hiller breaks formation to attacks]
  - ⚔ Archduke Charles (lost 210) vs Lannes (lost 160) — Napoleon reached Lannes in time, Sire — but even together, the field could not be held.
  - ⚔ Archduke Charles (lost 173) vs Lannes (lost 203) — Lannes held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Hiller (lost 26) vs Lannes (lost 159) — Lannes held superior ground, yet Hiller prevailed. A grim day, Sire.
  - verbs: attack×3, form_square×1, wait×1
- LEDGER treasury 16899 · net -164 · provinces 28 (+0)
- DISPATCH: Sire — Lannes, crowned four turns ago, has been hunted on consecutive turns by Archduke Charles.

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 6 actions, 4 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Hiller's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Hiller's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 369) vs Lannes (lost 30) — Ney and Massena arrived in time to steady Lannes's position. The field was held, nothing further.
  - ⚔ Hiller (lost 21) vs Lannes (lost 144) — Lannes held superior ground, yet Hiller prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 72) vs Lannes (lost 99) — The hills were ours, but Archduke Charles took them. Lannes's position was overrun.
  - ⚔ Hiller (lost 17) vs Lannes (lost 87) — Even the favorable ground could not save Lannes, Sire. Hiller overcame the terrain.
  - verbs: attack×4, grant_pension×1, wait×1
- LEDGER treasury 16680 · net -119 · provinces 28 (+0)
- DISPATCH: Sire — Lannes, crowned five turns ago, has been hunted on consecutive turns by Archduke Charles — and the laurels sit vacant.

## Turn 24 — Early September 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_proposal → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 7 actions, 4 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Hiller's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Hiller's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 64) vs Lannes (lost 71) — Napoleon marched to Lannes's guns as ordered. It was not enough.
  - ⚔ Hiller (lost 8) vs Lannes (lost 83) — Even the favorable ground could not save Lannes, Sire. Hiller overcame the terrain.
  - ⚔ Archduke Charles (lost 43) vs Lannes (lost 66) — Even the favorable ground could not save Lannes, Sire. Archduke Charles overcame the terrain.
  - ⚔ Hiller (lost 6) vs Lannes (lost 61) — Even the favorable ground could not save Lannes, Sire. Hiller overcame the terrain.
  - verbs: attack×4, unfortify×1, move×1, wait×1
- LEDGER treasury 16518 · net -93 · provinces 28 (+0)
- DISPATCH: Sire — Napoleon's corps has been broken at Tyrol. He must reform before he fights again.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 9 actions, 6 attacks — [Square broken — Kutuzov breaks formation to attacks] · Kutuzov holds them at Tyrol while allies attack from Bohemia! (+1 coordination) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Hiller's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Kutuzov (lost 48) vs Lannes (lost 41) — Lannes held superior ground, yet Kutuzov prevailed. A grim day, Sire.
  - ⚔ Kutuzov (lost 40) vs Lannes (lost 34) — Lannes held superior ground, yet Kutuzov prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 21) vs Lannes (lost 48) — The hills were ours, but Archduke Charles took them. Lannes's position was overrun.
  - ⚔ Hiller (lost 3) vs Lannes (lost 32) — Lannes held superior ground, yet Hiller prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 16) vs Lannes (lost 26) — Lannes held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Hiller (lost 2) vs Lannes (lost 20) — Lannes held superior ground, yet Hiller prevailed. A grim day, Sire.
  - verbs: attack×6, form_square×1, grant_pension×1, wait×1
- LEDGER treasury 16411 · net -63 · provinces 28 (+0)
- DISPATCH: Sire — Lannes was mauled at Tyrol: 136 men lost in a single action.

## Turn 26 — Early October 1806
- CMD `build depot in Burgundy` → ✗ Cannot build in Burgundy — rural regions don't support buildings (need city or larger)
- CMD `commission Oudinot` → ✓ Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 8 actions, 3 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Kutuzov (lost 457) vs Lannes (lost 0) — Ney, Massena and Napoleon's timely arrival bolstered Lannes's position. Well-coordinated, Sire.
  - ⚔ Kutuzov (lost 862) vs Lannes (lost 0) — A decisive victory for Lannes! Kutuzov was thoroughly outmatched.
  - ⚔ Archduke Charles (lost 295) vs Lannes (lost 0) — Victory for Lannes, but at terrible cost. The ranks are thinned dangerously.
  - verbs: attack×3, wait×3, recruit×2
- LEDGER treasury 13439 · net +462 · provinces 28 (+0)
- DISPATCH: Sire — Lannes was mauled at Tyrol: 55 men lost in a single action.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: move×1, wait×1
- LEDGER treasury 13901 · net +378 · provinces 28 (+0)
- DISPATCH: Sire — the levy has stood open 17 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.

## Turn 28 — Early November 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 8 actions, 3 attacks — [Square broken — Buxhowden breaks formation to attacks] · [Square broken — ArchdukeCharles breaks formation to attacks] · ArchdukeCharles holds them at Carniola while allies attack from Bohemia! (+1 coordination)
  - ⚔ Buxhowden (lost 539) vs Lannes (lost 0) — Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away.
  - ⚔ Archduke Charles (lost 509) vs Ney (lost 876) — Even the favorable ground could not save Ney, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke Charles (lost 352) vs Lannes (lost 0) — A decisive victory for Lannes! Archduke Charles was thoroughly outmatched.
  - verbs: attack×3, recruit×2, move×1, form_square×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 7) vs Kutuzov (lost 3022) — Lannes, Massena and Napoleon arrived to reinforce Murat, but Ney failed to reach the field in time.
  - POPUP capture_choice[capture]: Carniola, Murat → secure
- LEDGER treasury 14125 · net +307 · provinces 29 (+1)
- DISPATCH: Sire — Napoleon's corps has been broken at Carniola. He must reform before he fights again.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 6 actions, 3 attacks — [Square broken — Buxhowden breaks formation to attacks] · Buxhowden holds them at Carniola while allies attack from Hungary! (+1 coordination) · [Square broken — Hiller breaks formation to attacks]
  - ⚔ Buxhowden (lost 503) vs Ney (lost 545) — The hills were ours, but Buxhowden took them. Ney's position was overrun.
  - ⚔ Buxhowden (lost 20) vs Lannes (lost 0) — Neither Lannes nor Buxhowden could claim the field. The armies remain locked.
  - ⚔ Hiller (lost 375) vs Ney (lost 177) — Stalemate. Ney and Hiller glare at each other across the field.
  - verbs: attack×3, form_square×1, grant_pension×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 727) vs Kutuzov (lost 376) — Reinforcements from Lannes and Massena bolstered Ney's position — though Murat never arrived, Sire.
- LEDGER treasury 14325 · net +283 · provinces 29 (+0)
- DISPATCH: Sire — Ney was mauled at Hungary: 1,458 men lost in a single action.

## Turn 30 — Early December 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 9 actions, 4 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — ArchdukeCharles breaks formation to attacks] · ArchdukeCharles holds them at Carniola while allies attack from Bohemia! (+1 coordination)
  - ⚔ Buxhowden (lost 34) vs Lannes (lost 0) — Reinforcements! Napoleon marched onto the field beside Lannes. The enemy's advantage melted away.
  - ⚔ Buxhowden (lost 413) vs Lannes (lost 0) — An exemplary engagement by Lannes. The outcome was never in doubt.
  - ⚔ Archduke Charles (lost 348) vs Ney (lost 368) — The hills were ours, but Archduke Charles took them. Ney's position was overrun.
  - ⚔ Archduke Charles (lost 244) vs Murat (lost 2) — Murat carried the field, but the butcher's bill is steep, Sire.
  - verbs: attack×4, recruit×2, move×1, form_square×1, wait×1
  - ⚡ AUTONOMOUS: Cannot attack elsewhere while engaged with enemy forces! Buxhowden must be dealt with first.
- LEDGER treasury 14869 · net +478 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Lannes's corps has been DESTROYED at Carniola. He will not return to the order of battle.

---
finished: **completed** · commands 84 · popups 75 · battles 60
