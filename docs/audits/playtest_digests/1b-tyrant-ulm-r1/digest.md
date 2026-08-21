# Playtest digest — 1b-tyrant-ulm-r1

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "decline", "capture": "plunder", "estate": "confiscate", "glorious_charge": "charge", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 717) vs Mack (lost 16826) — Davout, Lannes and Napoleon's timely arrival aided Ney. Soult, Murat and Bernadotte, however, were conspicuously absent.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (25,221; 94,072 if all march) vs Mack (strength unknown) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 73) vs Mack (lost 22634) — Ney, Murat and Massena's timely arrival bolstered Davout's position. Well-coordinated, Sire.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 2864 · net +2165 · provinces 28
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Murat, charge Mack` → ✗ Murat needs to build momentum first! Win battles as attacker to increase recklessness (currently 0).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, attack Mack` → ✓ Soult pursues Mack (at Tyrol). Moves to Swabia. "Soult attack Mack." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — [!] ArchdukeJohn is EXPOSED! (Just retreated, no ally to cover) · [!] ArchdukeCharles is EXPOSED! (Just retreated, no ally to cover) · [!] ArchdukeCharles is EXPOSED! (Just retreated, no ally to cover)
  - ⚔ Deroy (lost 453) vs Archduke John (lost 8186) — A grievous defeat for Archduke John, Sire. The losses are severe.
  - ⚔ Deroy (lost 4057) vs Archduke Charles (lost 3133) — Archduke Charles's men formed square and weathered the storm. Discipline held the line.
  - ⚔ Deroy (lost 3848) vs Archduke Charles (lost 1940) — The square held its ground. Archduke Charles's infantry stood like a fortress on the field.
  - verbs: attack×3, retreat×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 358) vs Mack (lost 7225) — Massena's timely arrival aided Murat. Ney and Davout, however, were conspicuously absent.
- LEDGER treasury 5185 · net +2278 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Mack of Austria is taken at Tyrol — he is our prisoner, and their order of battle is one commander shorter.

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `Ney, attack Mack` → ✗ Region 'Mack' not found. Did you mean 'La Mancha'?
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `Lannes, attack Mack` → ✗ Region 'Mack' not found. Did you mean 'La Mancha'?
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 5 actions, 3 attacks — Deroy marches from Bohemia into Bohemia unopposed! (131 lost to march) Captured: Austria → Bavaria · Deroy marches from Bohemia into Hungary unopposed! (129 lost to march) Captured: Austria → Bavaria · [Shield] ArchdukeJohn's DEFENSIVE stance strengthens the line! (+15% defense)
  - 🏴 Bavaria: Deroy marches from Bohemia into Bohemia unopposed! (131 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy marches from Bohemia into Hungary unopposed! (129 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: [Shield] ArchdukeJohn's DEFENSIVE stance strengthens the line! (+15% defense)
  - ⚔ Deroy (lost 259) vs Archduke John (lost 3043) — A grievous defeat for Archduke John, Sire. The losses are severe.
  - verbs: attack×3, move×1, stance_change×1
- LEDGER treasury 7589 · net +2300 · provinces 28 (+0)
- DISPATCH: Sire — Ney and Davout stand 43,075 men at Munich, which feeds 37,500. 5,575 too many. 7,669 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large for the province…

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `grant Ney a rente` → ✓ By Imperial decree, Marshal Ney is granted a rente of 80g/turn upon the treasury. With fees and arrears it will cost the crown 120g/turn — paper is dearer than land, Sir…
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `Murat, charge Mack` → ✗ Mack has no troops to fight!
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 4 actions, 0 attacks
  - 🏴 Austria: ArchdukeCharles moves from Vienna to Bohemia. Bohemia falls to Austria! (was Bavaria) (1,391 lost to march)
  - verbs: wait×2, move×1, grant_dotation×1
- LEDGER treasury 9808 · net +2141 · provinces 28 (+0)
- DISPATCH: Sire — Murat and Massena stand 52,257 men at Tyrol, which feeds 20,000. 32,257 too many. 6,301 men lost in 3 turns. No depot may be laid at Tyrol — not controlled by France. Milan can feed 75,000 mor…

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `revoke Ney's rente` → ✓ Marshal Ney's rente of 80g/turn is withdrawn — the treasury keeps its 120g/turn. He will remember who stopped paying, Sire: unmet expectation frays loyalty after its gra…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Ney, attack Mack` → ✗ Region 'Mack' not found. Did you mean 'La Mancha'?
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 4 actions, 3 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [!] Deroy is EXPOSED! (Just retreated, no ally to cover)
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [!] Deroy is EXPOSED! (Just retreated, no ally to cover)
  - ⚔ Archduke Charles (lost 1203) vs Deroy (lost 4759) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 209) vs Deroy (lost 4058) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, form_square×1
- LEDGER treasury 12109 · net +2212 · provinces 28 (+0)
- DISPATCH: Sire — Murat and Massena stand 50,471 men at Tyrol, which feeds 20,000. 30,471 too many. 5,809 men lost in 3 turns. No depot may be laid at Tyrol — not controlled by France. Milan can feed 75,000 mor…

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Davout, attack Mack` → ✓ Davout firmly objects: 'Sire, the enemy is too strong. We need reinforcements.' (His loyalty is frayed by neglect — his victories remain unrewarded.)
  - POPUP objection: Davout, Davout firmly objects: 'Sire, the enemy is too strong. We need reinforcements.' (His loyalty is frayed by neglect — his victories remain unrewarded.) → insist
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Bernadotte, attack Mack` → ✓ Bernadotte challenges the order: 'Sire, the enemy is too strong. We need reinforcements.'
  - POPUP objection: Bernadotte, Bernadotte challenges the order: 'Sire, the enemy is too strong. We need reinforcements.' → insist
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 action(s) unused) Turn 7 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 13959 · net +1752 · provinces 28 (+0)
- DISPATCH: Sire — 3 turns of famine at Tyrol now. 5,374 men gone, and not one of them to the enemy. No depot may be laid at Tyrol — not controlled by France. Milan can feed 75,000 more and Carniola can feed 45,…

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `grant Davout a rente` → ✓ By Imperial decree, Marshal Davout is granted a rente of 80g/turn upon the treasury (his previous rente of 80g/turn is folded in). With fees and arrears it will cost the…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `Ney, move to Munich` → ✗ Ney is already in Munich.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- LEDGER treasury 15708 · net +1676 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 8 — Early January 1806
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `revoke Davout's rente` → ✓ Marshal Davout's rente of 80g/turn is withdrawn — the treasury keeps its 120g/turn. He will remember who stopped paying, Sire: unmet expectation frays loyalty after its …
  - POPUP marshal_petition: shadow_command, Marshal Lannes asks for a command → detach
- CMD `Murat, charge Mack` → ✗ Mack has no troops to fight!
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 4 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 4235) vs Bernadotte (lost 304) — Lannes and Massena's timely arrival aided Bernadotte. Ney and Soult, however, were conspicuously absent.
  - verbs: move×1, form_square×1, attack×1, grant_pension×1
- LEDGER treasury 17460 · net +1726 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 9 — Late January 1806
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Ney, attack Deroy` → ✗ Ney cannot attack Bavaria — they are our ally, Sire, and we are not at war with them.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 555) vs Archduke Charles (lost 4233) — Massena arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire.
- LEDGER treasury 19156 · net +1666 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney has now gone unrewarded 3 turns. The staff have noticed which of us he no longer looks at.

## Turn 10 — Early February 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Massena, attack Archduke John` → ✗ Enemy 'ArchdukeJohn' not found. Did you mean 'ArchdukeCharles'?
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `Lannes, move to Munich` → ✓ Lannes begins marching to Munich (distance: 2). Moved to Franconia. Route: Franconia -> Munich.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 action(s) unused) Turn 11 begins!
- LEDGER treasury 20775 · net +1510 · provinces 28 (+0)
- DISPATCH: Sire — 4 turns without settlement on Marshal Ney. A rente would close it today; the arrears will not close themselves.

## Turn 11 — Late February 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `Ney, attack Archduke John` → ✗ Enemy 'ArchdukeJohn' not found. Did you mean 'ArchdukeCharles'?
- CMD `Murat, attack Archduke John` → ✗ Enemy 'ArchdukeJohn' not found. Did you mean 'ArchdukeCharles'?
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- LEDGER treasury 22277 · net +1396 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 5 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 12 — Early March 1806
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Davout, move to Munich` → ✗ Davout is already in Munich.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, move to Swabia` → ✗ Soult is already in Swabia.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- LEDGER treasury 23646 · net +1268 · provinces 28 (+0)
- DISPATCH: Sire — Ney, Davout and Lannes stand 54,034 men at Munich, which feeds 45,000. 9,034 too many. 2,649 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the …

## Turn 13 — Late March 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Ney, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Ney can give chase.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- LEDGER treasury 24875 · net +1135 · provinces 28 (+0)
- DISPATCH: Sire — Ney, Davout and Lannes stand 52,792 men at Munich, which feeds 45,000. 7,792 too many. 3,891 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large for the …

## Turn 14 — Early April 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Murat, charge Archduke Charles` → ✗ ArchdukeCharles is too far for Glorious Charge! Distance: 3, Range: 2
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `Massena, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Massena can give chase.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- LEDGER treasury 25440 · net +520 · provinces 28 (+0)
- DISPATCH: Sire — Austria and Bavaria have made peace without us.

## Turn 15 — Late April 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `grant Murat a rente` → ✓ By Imperial decree, Marshal Murat is granted a rente of 80g/turn upon the treasury (his previous rente of 80g/turn is folded in). With fees and arrears it will cost the …
- CMD `Ney, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Ney can give chase.
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: defend×1, recruit×1, grant_pension×1
- LEDGER treasury 25906 · net +453 · provinces 28 (+0)
- DISPATCH: Sire — Ney, Davout and Lannes have been 4 turns over what Munich can feed. 4,351 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too large f…

## Turn 16 — Early May 1806
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `revoke Murat's rente` → ✓ Marshal Murat's rente of 80g/turn is withdrawn — the treasury keeps its 120g/turn. He will remember who stopped paying, Sire: unmet expectation frays loyalty after its g…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `Lannes, attack Archduke Charles` → ✓ Lannes pursues Archduke Charles (at Vienna). Moves to Franconia. Lannes: "Run him to ground, then. My sabers are hungry."
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 2 action(s) unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 26415 · net +490 · provinces 28 (+0)
- DISPATCH: Bernadotte's fortifications decay: 9% → 8%

## Turn 17 — Late May 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Ney, attack Kutuzov` → ✗ No intelligence on Kutuzov's position, Sire. Scout for him before Ney can give chase.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (97 lost to march)
  - verbs: move×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 6011) vs Archduke Charles (lost 2758) — Attacking prepared positions cost Massena dearly. The fortifications held.
- LEDGER treasury 26459 · net +311 · provinces 27 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Murat, charge Kutuzov` → ✗ Kutuzov is too far for Glorious Charge! Distance: 3, Range: 2
- CMD `Davout, attack Kutuzov` → ✗ No intelligence on Kutuzov's position, Sire. Scout for him before Davout can give chase.
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 3 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 4202) vs Lannes (lost 199) — Ney and Napoleon's timely arrival aided Lannes. Davout and Soult, however, were conspicuously absent.
  - ⚔ Archduke Charles (lost 3259) vs Murat (lost 2359) — Where was Davout? Murat held the field alone — reinforcement never came.
  - verbs: attack×2, wait×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 5467) vs Archduke Charles (lost 1700) — Attacking prepared positions cost Massena dearly. The fortifications held.
- LEDGER treasury 26210 · net +167 · provinces 27 (+0)
- DISPATCH: Sire — Massena's corps has been broken at Bohemia. He must reform before he fights again.

## Turn 19 — Late June 1806
- CMD `Ney, attack Kutuzov` → ✗ No intelligence on Kutuzov's position, Sire. Scout for him before Ney can give chase.
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 6 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 4244) vs Murat (lost 354) — Reinforcements from Ney and Napoleon bolstered Murat's position — though Davout never arrived, Sire.
  - verbs: recruit×2, move×1, form_square×1, attack×1, wait×1
- LEDGER treasury 26286 · net +111 · provinces 27 (+0)
- DISPATCH: Sire — Marshal Murat holds the field at Tyrol — Archduke Charles's corps is broken and flees.

## Turn 20 — Early July 1806
- CMD `Massena, attack Kutuzov` → ✗ Massena is recovering from retreat and cannot attack. Recovery: 1 turn(s) remaining.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 26327 · net +37 · provinces 27 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 21 — Late July 1806
- CMD `Ney, attack Kutuzov` → ✗ No intelligence on Kutuzov's position, Sire. Scout for him before Ney can give chase.
- CMD `Murat, charge Kutuzov` → ✗ Kutuzov is too far for Glorious Charge! Distance: 3, Range: 2
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 26294 · net -29 · provinces 27 (+0)
- DISPATCH: Sire — Ney, Murat and Napoleon stand 33,816 men at Tyrol, which feeds 20,000. 13,816 too many. 3,468 men lost in 3 turns. No depot may be laid at Tyrol — not controlled by France. Milan can feed 75,0…

## Turn 22 — Early August 1806
- CMD `revoke Ney's rente` → ✓ Marshal Ney's rente of 80g/turn is withdrawn — the treasury keeps its 120g/turn. He will remember who stopped paying, Sire: unmet expectation frays loyalty after its gra…
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `Davout, attack Kutuzov` → ✗ No intelligence on Kutuzov's position, Sire. Scout for him before Davout can give chase.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 25758 · net -447 · provinces 27 (+0)
- DISPATCH: Sire — Ney, Murat and Napoleon stand 32,790 men at Tyrol, which feeds 20,000. 12,790 too many. 3,267 men lost in 3 turns. No depot may be laid at Tyrol — not controlled by France. Milan can feed 75,0…

## Turn 23 — Late August 1806
- CMD `Ney, attack Archduke Charles` → ✓ Ney pursues Archduke Charles (at Hungary). Moves to Bohemia. Ney: "He is already beaten — he merely has not been told. I will tell him."
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 action(s) unused) Turn 24 begins!
- enemy phase: 2 actions, 1 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 3351) vs Ney (lost 499) — Reinforcements from Lannes and Massena bolstered Ney's position — though Murat and Napoleon never arrived, Sire.
  - verbs: attack×1, wait×1
- LEDGER treasury 24367 · net -1119 · provinces 28 (+1)
- DISPATCH: Sire — Bohemia has fallen to our arms. The tricolor flies over it this morning.

## Turn 24 — Early September 1806
- CMD `Murat, charge Archduke Charles` → ✓ [Cavalry][Combat] GLORIOUS CHARGE! Murat leads a devastating cavalry assault!
  - ⚔ Murat (lost 6820) vs Archduke Charles (lost 5466) — The walls of the region bear fresh scars, Your Majesty. Their fortifications weaken -- another assault may crack them.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 action(s) unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
  - POPUP capture_choice[capture]: Hungary, Ney → plunder
- LEDGER treasury 23473 · net -1046 · provinces 29 (+1)
- DISPATCH: Sire — Murat was mauled at Hungary: 6,820 men lost in a single action.

## Turn 25 — Late September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 3 actions, 2 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · Buxhowden holds them at Hungary while allies attack from Moravia! (+1 coordination)
  - ⚔ Buxhowden (lost 2617) vs Massena (lost 887) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Buxhowden (lost 2155) vs Lannes (lost 584) — The battle unfolded without particular distinction.
  - verbs: attack×2, wait×1
- LEDGER treasury 22280 · net -848 · provinces 29 (+0)
- DISPATCH: Sire — Massena's corps has been broken at Hungary. He must reform before he fights again.

## Turn 26 — Early October 1806
- CMD `Ney, attack Archduke Charles` → ✗ Cannot attack elsewhere while engaged with enemy forces! Buxhowden must be dealt with first.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `Lannes, attack Archduke Charles` → ✗ Cannot attack elsewhere while engaged with enemy forces! Buxhowden must be dealt with first.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 3 actions, 2 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 1686) vs Lannes (lost 777) — Neither Lannes nor Buxhowden could claim the field. The armies remain locked.
  - ⚔ Buxhowden (lost 1451) vs Lannes (lost 699) — Stalemate. Lannes and Buxhowden glare at each other across the field.
  - verbs: attack×2, wait×1
- LEDGER treasury 21271 · net -700 · provinces 29 (+0)
- DISPATCH: Sire — Buxhowden has crossed into Hungary. Ney and Lannes stand in his path.

## Turn 27 — Late October 1806
- CMD `Murat, charge Kutuzov` → ✗ Murat needs to build momentum first! Win battles as attacker to increase recklessness (currently 0).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → let_be
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Davout, attack Kutuzov` → ✗ No intelligence on Kutuzov's position, Sire. Scout for him before Davout can give chase.
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 7 actions, 3 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 1166) vs Lannes (lost 666) — Neither Lannes nor Buxhowden could claim the field. The armies remain locked.
  - ⚔ Buxhowden (lost 1038) vs Lannes (lost 687) — Lannes was close. A period of drilling could have changed the outcome.
  - ⚔ Buxhowden (lost 211) vs Lannes (lost 2104) — A grievous defeat for Lannes, Sire. The losses are severe.
  - verbs: attack×3, unfortify×1, move×1, grant_pension×1, wait×1
- LEDGER treasury 20476 · net -444 · provinces 29 (+0)
- DISPATCH: Sire — Ney, crowned five turns ago, has been driven back.

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Hesse, non_aggression → (left standing)
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 12 actions, 7 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Bennigsen's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 290) vs Lannes (lost 238) — Massena marched to Lannes's guns as ordered. It was not enough.
  - ⚔ Bennigsen (lost 7) vs Lannes (lost 1367) — The toll on Lannes's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Buxhowden (lost 8) vs Lannes (lost 620) — A grievous defeat for Lannes, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 415) vs Ney (lost 3321) — Ney stood alone, Sire. Napoleon never came.
  - ⚔ Archduke Charles (lost 1029) vs Ney (lost 475) — Reinforcement from Napoleon kept Ney standing, Sire — but neither side yielded the ground.
  - ⚔ Archduke Charles (lost 103) vs Ney (lost 1216) — A grievous defeat for Ney, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 67) vs Ney (lost 565) — A grievous defeat for Ney, Sire. The losses are severe.
  - verbs: attack×7, grant_pension×2, move×1, unfortify×1, wait×1
- LEDGER treasury 19165 · net -679 · provinces 29 (+0)
- DISPATCH: Sire — Massena's corps has been broken at Hungary. He must reform before he fights again.

## Turn 29 — Late November 1806
- CMD `Ney, attack Kutuzov` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn(s) remaining.
  - POPUP vassal_rebellion_imminent: Switzerland → display-only
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 11 actions, 8 attacks — [Combat] Bennigsen's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · ========================================
  - 🏴 Russia: [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Bennigsen (lost 1) vs Lannes (lost 322) — Lannes's army has been badly mauled. Bennigsen proved the stronger force today.
  - ⚔ Buxhowden (lost 1) vs Lannes (lost 126) — Lannes's army has been badly mauled. Buxhowden proved the stronger force today.
  - ⚔ Kutuzov (lost 2) vs Lannes (lost 73) — Lannes's army has been badly mauled. Kutuzov proved the stronger force today.
  - ⚔ Archduke Charles (lost 43) vs Ney (lost 543) — The toll on Ney's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 19) vs Ney (lost 248) — The toll on Ney's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 10) vs Ney (lost 96) — Ney's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 4) vs Ney (lost 52) — A grievous defeat for Ney, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 3) vs Ney (lost 29) — Ney's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×8, grant_pension×2, fortify×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1191) vs Archduke Charles (lost 1263) — Napoleon marched to Murat's guns as ordered. It was not enough.
- LEDGER treasury 18626 · net -280 · provinces 28 (-1)
- DISPATCH: Sire — Marshal Lannes's corps has been DESTROYED at Hungary. He will not return to the order of battle.

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 6 actions, 4 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 50) vs Ney (lost 49) — Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Archduke Charles (lost 213) vs Napoleon (lost 2221) — Where was Murat? Napoleon held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 340) vs Massena (lost 4557) — Where was Murat? Massena held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 313) vs Murat (lost 2291) — The hills were ours, but Archduke Charles took them. Murat's position was overrun.
  - verbs: attack×4, wait×1, form_square×1
- LEDGER treasury 18798 · net +533 · provinces 27 (-1)
- DISPATCH: Sire — Marshal Ney's corps has been DESTROYED at Bohemia. He will not return to the order of battle.

---
finished: **completed** · commands 89 · popups 83 · battles 45
