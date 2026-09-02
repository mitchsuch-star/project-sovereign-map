# Playtest digest — audit-flagship-mock

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `Bernadotte, attack Mack` → ✓ Bernadotte challenges the order: 'Sire, the enemy is too strong. We need reinforcements.'
  - POPUP objection: Bernadotte, Bernadotte challenges the order: 'Sire, the enemy is too strong. We need reinforcements.' → insist
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Bernadotte (lost 1750) vs Mack (lost 4463) — Lannes's timely arrival aided Bernadotte. Ney and Soult, however, were conspicuously absent.
- CMD `Marshal Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 56,553 if all march) vs Mack (47,537 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1323) vs Mack (lost 9924) — Davout and Napoleon arrived to reinforce Ney, but Soult, Murat and Bernadotte failed to reach the field in time.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 action(s) unused) Turn 2 begins!
- enemy phase: 4 actions, 2 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · ArchdukeJohn holds them at Milan while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn holds them at Milan while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 2356) vs Massena (lost 8011) — A narrow defeat for Massena, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Archduke John (lost 383) vs Massena (lost 6089) — The margin was slim. Training and preparation would serve Massena well.
  - verbs: attack×2, move×1, stance_change×1
- LEDGER treasury 2104 · net +2348 · provinces 28
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (24,075; 76,922 if all march) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 432) vs Mack (lost 7548) — Ney, Lannes and Napoleon arrived to reinforce Davout, but Murat failed to reach the field in time.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: stance_change×1
- LEDGER treasury 4550 · net +2370 · provinces 28 (+0)
- DISPATCH: Sire — Bohemia has been taken by Austria.

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Murat, attack Mack` → ✓ MUSTER — Murat (22,000; 31,247 if all march) vs Mack (27,371 men) at Milan — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 348) vs Mack (lost 26371) — Lannes and Napoleon's timely arrival aided Murat. Ney and Davout, however, were conspicuously absent.
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory #6 → dismiss
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 action(s) unused) Turn 4 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: stance_change×1, wait×1
- LEDGER treasury 7042 · net +2378 · provinces 28 (+0)
- DISPATCH: Sire — Hungary has been taken by Austria.

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Soult, deal with the Austrians` → ✓ Soult will not presume your meaning, Sire. "deal with Archduke John" — give battle, or observe Archduke John?
  - POPUP clarification: Soult, delegation, Soult will not presume your meaning, Sire. "deal with Archduke John" — give battle, or observe Archduke John?

Berthier: "You may hand a marshal a task and let him solve it his own way, Sire — each acts to his character." → 1 (first option: Attack)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer #9 → reject_settlement_offer
- CMD `Lannes, move to Swabia` → ✓ Lannes begins marching to Swabia (distance: 2). Moved to Munich. Route: Munich -> Swabia.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action(s) unused) Turn 5 begins!
- enemy phase: 8 actions, 1 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 2060) vs Bernadotte (lost 1817) — Reinforcements from Lannes bolstered Bernadotte's position — though Ney and Soult never arrived, Sire.
  - verbs: move×3, attack×1, retreat×1, stance_change×1, wait×1, recruit×1
- LEDGER treasury 9433 · net +2399 · provinces 28 (+0)
- DISPATCH: Sire — Ney, Davout and Lannes stand 52,162 men at Munich, which feeds 37,500. 14,662 too many. 5,865 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large for the…

## Turn 5 — Late November 1805
- CMD `Ney, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Ney can give chase.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `Davout, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Davout can give chase.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 4 actions, 0 attacks
  - verbs: wait×2, retreat×1, stance_change×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 477) vs Archduke Charles (lost 4350) — Ney's timely arrival aided Lannes. Davout and Soult, however, were conspicuously absent.
- LEDGER treasury 11788 · net +2273 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
- CMD `Massena, attack Archduke Charles` → ✓ Massena pursues Archduke Charles (at Bohemia). Moves to Milan. Massena: "Run him to ground, then. My sabers are hungry."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders #11 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `Bernadotte, move to Swabia` → ✓ Bernadotte moves from Franconia to Swabia (126 lost to march)
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action(s) unused) Turn 7 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: fortify×1, wait×1
- LEDGER treasury 14082 · net +2127 · provinces 28 (+0)
- DISPATCH: Sire — Leon has been taken by Britain.

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `endow Ney with the Duchy of Swabia` → ✗ We do not hold Swabia — an estate must stand on our own soil.
- CMD `Murat, march to Munich` → ✓ Murat begins march to Munich. Moves to Munich. Murat: "At the double, Sire — the men will smell powder soon enough."
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 action(s) unused) Turn 8 begins!
- enemy phase: 5 actions, 2 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 2257) vs Ney (lost 1293) — Davout and Soult failed to arrive in time. Ney's army fought without expected support.
  - ⚔ Archduke Charles (lost 2132) vs Lannes (lost 452) — Davout, Soult, Murat and Bernadotte never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×2, move×1, fortify×1, recruit×1
- LEDGER treasury 16138 · net +2046 · provinces 28 (+0)
- DISPATCH: Sire — Asturias has been taken by Britain.

## Turn 8 — Early January 1806
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `Ney, march to Munich` → ✓ Ney begins march to Munich. Moves to Munich. Ney: "At the double, Sire — the men will smell powder soon enough."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `Davout, march to Munich` → ✓ Davout begins march to Munich. Davout: "We move deliberately — arrival is worth little if the army arrives broken."
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 7 actions, 3 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · ArchdukeCharles marches from Bohemia into Carniola unopposed! (807 lost to march) Captured: Bavaria → Austria · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: ArchdukeCharles marches from Bohemia into Carniola unopposed! (807 lost to march) Captured: Bavaria → Austria
  - ⚔ Buxhowden (lost 3373) vs Lannes (lost 254) — Reinforcements from Ney and Massena bolstered Lannes's position — though Davout, Soult, Murat and Bernadotte never arri…
  - ⚔ Archduke Charles (lost 1645) vs Deroy (lost 3024) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: move×3, attack×3, unfortify×1
- LEDGER treasury 18140 · net +1897 · provinces 28 (+0)
- DISPATCH: Sire — Carniola has been taken by Austria.

## Turn 9 — Late January 1806
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  - POPUP diplomatic_dialogue: advisory #20 → dismiss
  - POPUP diplomatic_dialogue: Russia, armistice_losing #17 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #19 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #19 already answered this chain)
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (stale passthrough — #17 already answered this chain)
- CMD `Soult, march to Swabia` → ✓ Soult begins march to Swabia. "Soult, march to Swabia." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP diplomatic_dialogue: Russia, armistice_losing #17 → (left standing)
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 action(s) unused) Turn 10 begins!
- enemy phase: 5 actions, 3 attacks — [Square broken — Buxhowden breaks formation to attacks] · ArchdukeCharles marches from Croatia into Croatia unopposed! (540 lost to march) Captured: Bavaria → Austria · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: ArchdukeCharles marches from Croatia into Croatia unopposed! (540 lost to march) Captured: Bavaria → Austria
  - ⚔ Buxhowden (lost 2027) vs Ney (lost 2345) — Ney stood alone, Sire. Davout never came.
  - ⚔ Archduke Charles (lost 875) vs Deroy (lost 3880) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, form_square×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 325) vs Archduke John (lost 9655) — Lannes, Massena and Napoleon arrived to reinforce Murat, but Davout failed to reach the field in time.
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Tyrol, Sire. Investigate?' → investigate
  - POPUP capture_choice[capture]: Tyrol, Murat → secure
- LEDGER treasury 19329 · net +1140 · provinces 29 (+1)
- DISPATCH: Sire — Marshal Archduke John of Austria is taken at Tyrol — he is our prisoner, and their order of battle is one commander shorter.

## Turn 10 — Early February 1806
  - LETTER Ottoman: Open Borders Agreement → decline
- CMD `grant Murat a rente` → ✓ By Imperial decree, Marshal Murat is granted a rente of 80g/turn upon the treasury. With fees and arrears it will cost the crown 120g/turn — paper is dearer than land, S…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders #22 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `Lannes, march to Munich` → ✓ Lannes begins march to Munich. Moves to Munich. Lannes: "Good. An army rots standing still."
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 action(s) unused) Turn 11 begins!
- enemy phase: 7 actions, 3 attacks — [Square broken — Castanos breaks formation to attacks] · Castanos holds them at Galicia while allies attack from Leon! (+1 coordination) · Castanos holds them at Galicia while allies attack from Leon! (+1 coordination)
  - 🏴 Spain: Castanos holds them at Galicia while allies attack from Leon! (+1 coordination)
  - ⚔ Castanos (lost 716) vs Paget (lost 1187) — Paget was close. A period of drilling could have changed the outcome.
  - ⚔ Castanos (lost 391) vs Paget (lost 1242) — Paget's army has been badly mauled. Castanos proved the stronger force today.
  - ⚔ Castanos (lost 183) vs Paget (lost 777) — Paget's army has been badly mauled. Castanos proved the stronger force today.
  - verbs: attack×3, retreat×1, stance_change×1, grant_pension×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 435) vs Buxhowden (lost 4916) — Massena and Napoleon's timely arrival aided Ney. Davout, however, was conspicuously absent.
- LEDGER treasury 20333 · net +970 · provinces 29 (+0)
- DISPATCH: Sire — Davout and Murat stand 36,514 men at Tyrol, which feeds 30,000. 6,514 too many. 4,520 men lost in 2 turns. No depot may be laid at Tyrol — region stability too low (35/100). Need 51+. Franconi…

## Turn 11 — Late February 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `Ney, march to Vienna` → ✓ Ney: 'Mack blocks the path at Vienna. Odds unfavorable. Your orders?'
  - POPUP strategic_interrupt: Ney, contact_bad_odds → attack_anyway
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 536) vs Mack (lost 4563) — Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #24 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `Davout, march to Vienna` → ✓ Davout firmly objects: 'I have concerns about this order, Sire.'
  - POPUP objection: Davout, Davout firmly objects: 'I have concerns about this order, Sire.' → insist
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action(s) unused) Turn 12 begins!
- enemy phase: 2 actions, 1 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Kutuzov (lost 3024) vs Massena (lost 553) — Davout arrived to reinforce Massena! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×1, wait×1
- LEDGER treasury 20137 · net -24 · provinces 30 (+1)
- DISPATCH: Sire — Leon has been taken by Britain.

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Murat, march to Vienna` → ✓ Murat begins march to Vienna. Cavalry charges through Bohemia -> Vienna. Murat: "We march. Pity whatever slows us."
- CMD `recruit 10000 infantry` → ✗ Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.' Recruits join a marshal who can reach the depot: Ney (out of range - 7 regions …
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 action(s) unused) Turn 13 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 499) vs Deroy (lost 4824) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×2, naval_expedition×1, form_square×1
- LEDGER treasury 20088 · net -42 · provinces 29 (-1)
- DISPATCH: Sire — Bohemia has been taken by Austria.

## Turn 13 — Late March 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `build depot in Swabia` → ✗ Cannot build in Swabia — not controlled by France
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `Bernadotte, attack Archduke John` → ✓ Bernadotte refuses outright: 'The odds are not in our favor. Perhaps we should reconsider.'
  - POPUP objection: Bernadotte, Bernadotte refuses outright: 'The odds are not in our favor. Perhaps we should reconsider.' → insist
  - POPUP redemption: Bernadotte, 9 → dismiss
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 7 actions, 7 attacks — [Square broken — Kutuzov breaks formation to attacks] · [Square broken — Bennigsen breaks formation to attacks] · [Square broken — Buxhowden breaks formation to attacks] · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Kutuzov (lost 2216) vs Ney (lost 384) — Davout and Napoleon arrived to reinforce Ney, but Massena failed to reach the field in time.
  - ⚔ Bennigsen (lost 160) vs Massena (lost 260) — Ney arrived to reinforce Massena! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Buxhowden (lost 2371) vs Ney (lost 312) — A decisive victory for Ney! Buxhowden was thoroughly outmatched.
  - ⚔ Archduke Charles (lost 646) vs Lannes (lost 3673) — Lannes stood alone, Sire. Soult never came.
  - ⚔ Archduke Charles (lost 187) vs Lannes (lost 2654) — Where was Soult? Lannes held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 82) vs Lannes (lost 1056) — Where was Soult? Lannes held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 55) vs Lannes (lost 496) — Where was Soult? Lannes held the field alone — reinforcement never came.
  - verbs: attack×7
- LEDGER treasury 19549 · net -9 · provinces 29 (+0)
- DISPATCH: Sire — Lannes was mauled at Munich: three-quarters of his corps — 3,673 men — lost in a single action.

## Turn 14 — Early April 1806
  - LETTER Ottoman: Open Borders Agreement → decline
- CMD `Ney, attack Archduke Charles` → ✓ Ney pursues Archduke Charles (at Munich). Ney: "He is already beaten — he merely has not been told. I will tell him."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders #31 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #33 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #31 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Prussia, open_borders #31 → (left standing)
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 action(s) unused) Turn 15 begins!
- enemy phase: 6 actions, 5 attacks — ======================================== · [Square broken — Kutuzov breaks formation to attacks] · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Square broken — Mack breaks formation to attacks]
  - ⚔ Kutuzov (lost 4455) vs Massena (lost 189) — Reinforcements! Davout, Murat and Napoleon marched onto the field beside Massena. The enemy's advantage melted away.
  - ⚔ Archduke Charles (lost 42) vs Lannes (lost 382) — Lannes stood alone, Sire. Soult never came.
  - ⚔ Archduke Charles (lost 12) vs Lannes (lost 158) — Lannes stood alone, Sire. Soult never came.
  - verbs: attack×5, form_square×1
- LEDGER treasury 20005 · net +458 · provinces 28 (-1)
- DISPATCH: Sire — Bohemia has been taken by Austria.

## Turn 15 — Late April 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `Talleyrand, request terms from Austria` → ✓ Austria fights under Britain's lead in France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's t…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 4 actions, 3 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — Mack breaks formation to attacks]
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Square broken — Mack breaks formation to attacks]
  - ⚔ Archduke Charles (lost 5) vs Lannes (lost 69) — Where was Soult? Lannes held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 2) vs Lannes (lost 31) — Not one corps reached Lannes. Soult was expected; Lannes fought the battle single-handed.
  - verbs: attack×3, form_square×1
- LEDGER treasury 19825 · net -147 · provinces 29 (+1)
- DISPATCH: Sire — Marshal Lannes's corps has been DESTROYED at Munich. He will not return to the order of battle.

## Turn 16 — Early May 1806
  - LETTER Naples: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Soult, march to Vienna` → ✓ Soult begins march to Vienna. Route: Rhineland -> Frankfurt -> Berlin -> Dresden -> Vienna. Moves to Rhineland. "Soult, march to Vienna." Understood to the letter. (1 AP…
  - POPUP marshal_petition: shadow_command, Marshal Davout asks for a command → detach
  - POPUP diplomatic_dialogue: Britain, armistice_losing #36 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #39 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (stale passthrough — #36 already answered this chain)
- CMD `Massena, march to Tyrol` → ✓ Massena begins march to Tyrol. Route: Bohemia -> Tyrol. Moves to Bohemia. Massena: "Good. An army rots standing still."
  - POPUP diplomatic_dialogue: Britain, armistice_losing #36 → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action(s) unused) Turn 17 begins!
- enemy phase: 5 actions, 1 attacks — [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Mack (lost 3628) vs Ney (lost 125) — Davout and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire.
  - verbs: attack×1, move×1, fortify×1, wait×1, grant_dotation×1
- LEDGER treasury 19844 · net +143 · provinces 29 (+0)
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field.

## Turn 17 — Late May 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Ney, attack Kutuzov` → ✗ No intelligence on Kutuzov's position, Sire. Scout for him before Ney can give chase.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders #40 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `Davout, attack Kutuzov` → ✗ No intelligence on Kutuzov's position, Sire. Scout for him before Davout can give chase.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 6 actions, 0 attacks
  - verbs: move×4, unfortify×1, grant_pension×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 92) vs Paget (lost 2639) — Davout and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire.
  - POPUP capture_choice[capture]: Carniola, Ney → secure
- LEDGER treasury 19881 · net -1 · provinces 30 (+1)
- DISPATCH: Sire — Marshal Ney holds the field at Carniola — Paget's corps breaks a second time on this ground and flees.

## Turn 18 — Early June 1806
  - LETTER Ottoman: Open Borders Agreement → decline
- CMD `offer peace to Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #45 → confirm
  -     ↳ refused: Making peace with Austria while allied with Bavaria (who is still at war with Austria) creates a diplomatic c…
  - POPUP diplomatic_dialogue: proposal_confirm → (stale passthrough — #45 already answered this chain)
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: move×1, wait×1, recruit×1
- LEDGER treasury 19998 · net +98 · provinces 30 (+0)
- DISPATCH: Sire — Carniola has fallen to our arms. The tricolor flies over it this morning.

## Turn 19 — Late June 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `Murat, attack Buxhowden` → ✓ MUSTER — Murat (14,141) vs Buxhowden (strength unknown) at Podolia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 4328) vs Buxhowden (lost 807) — The enemy fortifications proved formidable, Sire. Murat's assault was repulsed.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `Lannes, attack Buxhowden` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Munich. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 action(s) unused) Turn 20 begins!
- enemy phase: 11 actions, 5 attacks — ======================================== · ======================================== · Mack marches from Munich into Franche-Comte unopposed! (973 lost to march) Captured: France → Austria · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: Mack marches from Munich into Franche-Comte unopposed! (973 lost to march) Captured: France → Austria
  - 🏴 Austria: Mack marches from Franche-Comte into Lorraine unopposed! (943 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 2358) vs Massena (lost 221) — Reinforcements! Ney, Davout, Murat and Napoleon marched onto the field beside Massena. The enemy's advantage melted awa…
  - verbs: attack×5, unfortify×2, recruit×2, move×1, form_square×1
- LEDGER treasury 18559 · net -981 · provinces 28 (-2)
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil.

## Turn 20 — Early July 1806
  - LETTER Naples: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory #50 → dismiss
- CMD `endow Davout with an estate` → ✗ Which province, Sire? Eligible estates: Bohemia, Carniola. Example: 'endow Davout with Bohemia'.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 11 actions, 2 attacks — Mack marches from Lorraine into Swabia unopposed! (915 lost to march) Captured: Bavaria → Austria · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: Mack marches from Lorraine into Swabia unopposed! (915 lost to march) Captured: Bavaria → Austria
  - ⚔ Mack (lost 8449) vs Soult (lost 1564) — A decisive victory for Soult! Mack was thoroughly outmatched.
  - verbs: move×3, recruit×3, attack×2, fortify×1, wait×1, form_square×1
- LEDGER treasury 17398 · net -896 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Soult holds the field at Rhineland — Mack's corps is broken and flees.

## Turn 21 — Late July 1806
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `Ney, march to Vienna` → ✓ Ney begins march to Vienna. Moves to Vienna. Ney: "Good. An army rots standing still."
  - POPUP diplomatic_dialogue: Prussia, open_borders #51 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #53 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #51 already answered this chain)
- CMD `Davout, march to Vienna` → ✓ Davout begins march to Vienna. Moves to Vienna. Davout: "The roads will be scouted before each march, Sire."
  - POPUP diplomatic_dialogue: Prussia, open_borders #51 → (left standing)
- CMD `end turn` → ✓ Turn 21 ended. Turn 22 begins!
- enemy phase: 5 actions, 0 attacks
  - verbs: stance_change×1, move×1, fortify×1, wait×1, recruit×1
- LEDGER treasury 16535 · net -711 · provinces 28 (+0)
- DISPATCH: Supply cost you 491 men, at Bohemia.

## Turn 22 — Early August 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 3 actions, 1 attacks — ========================================
  - verbs: stance_change×1, attack×1, wait×1
  - POPUP strategic_interrupt: Ney, last_stand, Ney awaits your orders. → fight_to_the_last
- LEDGER treasury 16408 · net +390 · provinces 28 (+0)
- DISPATCH: Supply cost you 482 men, at Bohemia.

## Turn 23 — Late August 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `Ney, attack Archduke Charles` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
  - POPUP marshal_petition: shadow_command, Marshal Murat asks for a command → detach
  - POPUP diplomatic_dialogue: Britain, armistice_losing #56 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 2 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - 🏴 Britain: Shrapnel moves from Lorraine to Orleanais. Orleanais falls to Britain! (was France) (23 lost to march)
  - 🏴 Austria: [Square broken — Mack breaks formation to attacks]
  - verbs: move×1, attack×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 56) vs Paget (lost 1751) — Reinforcements! Massena and Napoleon marched onto the field beside Murat. The enemy's advantage melted away.
  - POPUP capture_choice[capture]: Franconia, Murat → secure
  - POPUP capture_choice[estate]: Franconia, Murat, ArchdukeCharles → respect
- LEDGER treasury 16139 · net -291 · provinces 27 (-1)
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil.

## Turn 24 — Early September 1806
  - LETTER Naples: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: advisory #64 → dismiss
  - POPUP diplomatic_dialogue: Prussia, open_borders #60 → reject
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #60 already answered this chain)
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 2 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — Mack breaks formation to attacks]
  - 🏴 Austria: [Square broken — Mack breaks formation to attacks]
  - ⚔ Archduke Charles (lost 1577) vs Murat (lost 752) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×2
- LEDGER treasury 15735 · net -246 · provinces 26 (-1)
- DISPATCH: Sire — Napoleon's corps has been broken at Franconia. He must reform before he fights again.

---
finished: **completed** · commands 68 · popups 111 · battles 41
