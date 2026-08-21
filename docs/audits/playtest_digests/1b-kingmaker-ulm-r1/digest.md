# Playtest digest — 1b-kingmaker-ulm-r1

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "first", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `vassalize Saxony` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
- CMD `Massena, move to Piedmont` → ✓ Massena moves from Milan to Piedmont (2,520 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 1750) vs Bernadotte (lost 6672) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- LEDGER treasury 2609 · net +2118 · provinces 28
- DISPATCH: Sire — Bernadotte was mauled at Franconia: 6,672 men lost in a single action.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Naples: Open Borders Agreement → accept
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, move to Rome` → ✗ Cannot enter Rome — it is controlled by PapalStates (diplomatic state: PEACE). Open borders or higher required.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 758) vs Mack (lost 13806) — Davout, Lannes and Napoleon arrived to reinforce Ney, but Soult and Murat failed to reach the field in time.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 6 actions, 2 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense)
  - 🏴 Austria: [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 254) vs Bernadotte (lost 6764) — Bernadotte stood alone, Sire. Ney never came.
  - ⚔ Archduke Charles (lost 1944) vs Deroy (lost 6198) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×2, fortify×1, retreat×1, stance_change×1, wait×1
- LEDGER treasury 4608 · net +2260 · provinces 28 (+0)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `increase autonomy` → ✗ Specify which vassal.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 2 actions, 2 attacks — ======================================== · [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: ========================================
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 91) vs Bernadotte (lost 2147) — Bernadotte held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 1930) vs Murat (lost 7337) — Not one corps reached Murat. Soult was expected; Murat fought the battle single-handed.
  - verbs: attack×2
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1197) vs Archduke Charles (lost 4083) — Reinforcement from Ney, Davout, Lannes and Napoleon kept Murat standing, Sire — but neither side yielded the ground.
- LEDGER treasury 6673 · net +2420 · provinces 25 (-3)
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil.

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `declare war on Papal States` → ✓ Choose your war purpose against PapalStates.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on PapalStates. Our threat level stands at 67 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on PapalStates! Holland follows France into the war against PapalStates! KingdomOfItaly follows France into the war against PapalStates! Switzerland follows France into the war against PapalStates! → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 6 actions, 3 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · ArchdukeCharles assaults the Flanders garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,000 troops.… · ArchdukeCharles assaults the Flanders garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,500 troops in …
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: ArchdukeCharles assaults the Flanders garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,500 troops in the assault. ArchdukeCharles m…
  - verbs: attack×3, grant_dotation×2, form_square×1
- LEDGER treasury 8540 · net +1979 · provinces 23 (-2)
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil.

## Turn 5 — Late November 1805
- CMD `Massena, attack Rome` → ✓ Massena assaults the Rome garrison! Garrison: 10,000 -> 5,000 (-5,000). Massena loses 2,173 troops. Garrison holds — 5,000 defenders remain.
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 3 action(s) unused) Turn 6 begins!
- enemy phase: 1 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - ⚔ Mack (lost 12347) vs Murat (lost 87) — Ney, Davout, Lannes and Napoleon arrived to reinforce Murat! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×1
- LEDGER treasury 10438 · net +1814 · provinces 22 (-1)
- DISPATCH: Sire — Picardy has fallen. Enemy colours fly over French homeland soil.

## Turn 6 — Early December 1805
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (19,605; 58,026 if all march) vs Mack (substantial force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 77) vs Mack (lost 14957) — Reinforcements from Ney, Lannes and Napoleon bolstered Davout's position — though Soult and Murat never arrived, Sire.
  - POPUP capture_choice[capture]: Swabia, Davout → secure
- CMD `cede tyrol to bavaria` → ✗ No province is eligible to cede to Tyrol — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 action(s) unused) Turn 7 begins!
- enemy phase: 3 actions, 3 attacks — ArchdukeCharles marches from Picardy into Artois unopposed! (707 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,000 troops.… · ArchdukeCharles assaults the Normandy garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,500 troops in …
  - 🏴 Austria: ArchdukeCharles marches from Picardy into Artois unopposed! (707 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles assaults the Normandy garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,500 troops in the assault. ArchdukeCharles m…
  - verbs: attack×3
- LEDGER treasury 11317 · net +1139 · provinces 21 (-1)
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil.

## Turn 7 — Late December 1805
- CMD `request terms from Papal States` → ✓ PapalStates fights under Britain's lead in France + Spain + Holland + KingdomOfItaly + Switzerland vs Britain + Austria + Russia + PapalStates, Sire — the coalition's te…
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- LEDGER treasury 11702 · net +326 · provinces 20 (-1)
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil.

## Turn 8 — Early January 1806
- CMD `invest in bavaria` → ✗ "Sire, I must confess this order eludes me," Berthier admits. "Shall I relay an order to Ney? Valid actions include: attack, move, scout, defend, fortify, recruit. For d…
  - POPUP marshal_petition: shadow_command, Marshal Lannes asks for a command → detach
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → confirm_settlement
- CMD `Ney, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Ney can give chase.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 6 actions, 3 attacks — [Combat] Moore's DEFENSIVE stance hampers offensive operations (-10% attack) · Moore holds them at Paris while allies attack from Normandy! (+1 coordination) · Moore holds them at Paris while allies attack from Normandy! (+1 coordination)
  - ⚔ Moore (lost 1570) vs Castanos (lost 3001) — Even Castanos's fortifications could not hold, Sire. Moore overran the position.
  - ⚔ Moore (lost 1294) vs Castanos (lost 2070) — Castanos's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Moore (lost 804) vs Castanos (lost 2344) — Castanos's fortified position was overwhelmed. A costly investment lost, Sire.
  - verbs: attack×3, unfortify×1, move×1, grant_pension×1
- LEDGER treasury 11810 · net +91 · provinces 20 (+0)
- DISPATCH: Sire — Moore has crossed into Paris. No French corps stands in his path.

## Turn 9 — Late January 1806
- CMD `vassalize Switzerland` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: VASSAL).
  - POPUP diplomatic_dialogue: PapalStates, armistice_losing → (left standing)
- CMD `guarantee bavaria` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — perhaps 'attack', 'move', 'def…
  - POPUP diplomatic_dialogue: PapalStates, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 4 actions, 3 attacks — [Combat] Moore's DEFENSIVE stance hampers offensive operations (-10% attack) · Moore marches from Limousin into Lyonnais unopposed! (455 lost to march) Captured: France → Britain · Moore marches from Lyonnais into Languedoc unopposed! (425 lost to march) Captured: France → Britain
  - 🏴 Britain: [Combat] Moore's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Britain: Moore marches from Limousin into Lyonnais unopposed! (455 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Lyonnais into Languedoc unopposed! (425 lost to march) Captured: France → Britain
  - ⚔ Moore (lost 311) vs Castanos (lost 2761) — The toll on Castanos's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×3, move×1
- LEDGER treasury 11977 · net +145 · provinces 17 (-3)
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil.

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 6 actions, 3 attacks — [Combat] Moore's DEFENSIVE stance hampers offensive operations (-10% attack) · ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,723 troops. Garrison… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,361 troops in the assau…
  - 🏴 Britain: [Combat] Moore's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,361 troops in the assault. ArchdukeJohn marches into …
  - ⚔ Moore (lost 148) vs Castanos (lost 1815) — Castanos held superior ground, yet Moore prevailed. A grim day, Sire.
  - verbs: attack×3, grant_dotation×1, unfortify×1, move×1
- LEDGER treasury 11792 · net -161 · provinces 16 (-1)
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil.

## Turn 11 — Late February 1806
- CMD `Ney, move to Munich` → ✗ Cannot move into Munich - enemy forces present! Use ATTACK to engage Mack.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `increase autonomy` → ✗ Specify which vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 2 actions, 2 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke John (lost 6196) vs Massena (lost 1211) — An exemplary engagement by Massena. The outcome was never in doubt.
  - ⚔ Mack (lost 10106) vs Massena (lost 1347) — A decisive victory for Massena! Mack was thoroughly outmatched.
  - verbs: attack×2
- LEDGER treasury 11516 · net -129 · provinces 16 (+0)
- DISPATCH: Sire — Marshal Massena holds the field at Piedmont — Mack's corps is broken and flees.

## Turn 12 — Early March 1806
- CMD `cede swabia to bavaria` → ✗ No province is eligible to cede to Swabia — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
  - POPUP marshal_petition: shadow_command, Marshal Ney asks for a command → detach
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 4 actions, 4 attacks — Moore marches from Gascony into Bearn unopposed! (639 lost to march) Captured: France → Britain · Moore marches from Bearn into Aragon unopposed! (566 lost to march) Captured: Spain → Britain · Moore assaults the Madrid garrison! Garrison: 15,000 -> 8,386 (-6,614). Moore loses 4,166 troops. Garrison holds — 8,38… · Moore assaults the Madrid garrison! Garrison collapses (8,386 -> 0). Moore loses 2,329 troops in the assault. Moore mar…
  - 🏴 Britain: Moore marches from Gascony into Bearn unopposed! (639 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Bearn into Aragon unopposed! (566 lost to march) Captured: Spain → Britain
  - 🏴 Britain: Moore assaults the Madrid garrison! Garrison collapses (8,386 -> 0). Moore loses 2,329 troops in the assault. Moore marches into Madrid! (145 lost to…
  - verbs: attack×4
- LEDGER treasury 11280 · net -203 · provinces 15 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 13 — Late March 1806
- CMD `Davout, attack Archduke John` → ✗ No intelligence on Archduke John's position, Sire. Scout for him before Davout can give chase.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → confirm_settlement
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- LEDGER treasury 11083 · net -168 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Soult's grievance is 7 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 14 — Early April 1806
- CMD `vassalize Naples` → ✓ Naples has become a Satellite vassal of France (loyalty: 60). Marshals assimilated: Damas.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `invest in bavaria` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — perhaps 'attack', 'move', 'def…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- LEDGER treasury 11009 · net -63 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Soult's grievance is 8 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 15 — Late April 1806
- CMD `cede munich to bavaria` → ✗ No province is eligible to cede to Munich — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Britain, peace → (left standing)
- CMD `guarantee saxony` → ✗ France already guarantees Saxony.
  - POPUP diplomatic_dialogue: Britain, peace → (left standing)
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- LEDGER treasury 10701 · net -262 · provinces 15 (+0)
- DISPATCH: Supply cost you 1,375 men, at Piedmont and Swabia.

## Turn 16 — Early May 1806
- CMD `Ney, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Ney can give chase.
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- LEDGER treasury 10447 · net -215 · provinces 15 (+0)
- DISPATCH: Supply cost you 1,334 men, at Piedmont and Swabia.

## Turn 17 — Late May 1806
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Mack (lost 7987) vs Ney (lost 115) — Reinforcements from Murat bolstered Ney's position — though Soult never arrived, Sire.
  - verbs: attack×1
- LEDGER treasury 10207 · net -182 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees.

## Turn 18 — Early June 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `request terms from Austria` → ✗ Their terms are already on the desk, Sire — answer the offer in the mailbox.
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- LEDGER treasury 10054 · net -128 · provinces 15 (+0)
- DISPATCH: Supply cost you 2,107 men, at Piedmont and Swabia.

## Turn 19 — Late June 1806
- CMD `Massena, move to Naples` → ✓ Massena begins marching to Naples (distance: 2). Moved to Rome. Route: Rome -> Naples.
- CMD `invest in bavaria` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — perhaps 'attack', 'move', 'def…
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 action(s) unused) Turn 20 begins!
- LEDGER treasury 9982 · net -60 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `cede tyrol to bavaria` → ✗ No province is eligible to cede to Tyrol — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- LEDGER treasury 9873 · net -91 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- LEDGER treasury 9785 · net -73 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney has now gone unrewarded 3 turns. The staff have noticed which of us he no longer looks at.

## Turn 22 — Early August 1806
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `guarantee bavaria` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — perhaps 'attack', 'move', 'def…
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - ⚔ Mack (lost 4563) vs Murat (lost 231) — Soult never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×1
- LEDGER treasury 9689 · net -39 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Murat holds the field at Swabia — Mack's corps is broken and flees.

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- LEDGER treasury 9672 · net -14 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 5 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- LEDGER treasury 9220 · net -374 · provinces 15 (+0)
- DISPATCH: Supply cost you 1,574 men, at Swabia.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- LEDGER treasury 8860 · net -299 · provinces 15 (+0)
- DISPATCH: Supply cost you 1,511 men, at Swabia.

## Turn 26 — Early October 1806
- CMD `invest in bavaria` → ✗ "Sire, I must confess this order eludes me," Berthier admits. "Shall I relay an order to Ney? Valid actions include: attack, move, scout, defend, fortify, recruit. For d…
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → confirm_settlement
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `increase autonomy` → ✗ Specify which vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 1 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - ⚔ Mack (lost 5009) vs Murat (lost 166) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×1
- LEDGER treasury 8545 · net -232 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Murat holds the field at Swabia — Mack's corps is broken and flees.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- LEDGER treasury 8339 · net -171 · provinces 15 (+0)
- DISPATCH: Supply cost you 1,366 men, at Swabia.

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- LEDGER treasury 8039 · net -248 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- LEDGER treasury 6953 · net -845 · provinces 13 (-2)
- DISPATCH: Sire — Bordelais has fallen. Enemy colours fly over French homeland soil.

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 2 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - ⚔ Mack (lost 2353) vs Ney (lost 152) — Soult never reached the guns. The battle was decided without them, Sire.
  - verbs: wait×1, attack×1
- LEDGER treasury 6096 · net -641 · provinces 13 (+0)
- DISPATCH: Sire — Shrapnel has crossed into Paris. No French corps stands in his path.

---
finished: **completed** · commands 81 · popups 56 · battles 20
