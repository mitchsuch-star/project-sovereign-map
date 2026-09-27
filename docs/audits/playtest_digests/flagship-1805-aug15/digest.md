# Playtest digest — flagship-1805

seed `historical` · llm `anthropic` · transport in-process · policy `{"objection": "insist", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `Bernadotte, attack Mack` → ✓ Bernadotte challenges the order: 'Sire, the enemy is too strong. We need reinforcements.'
  - POPUP objection: Bernadotte, Bernadotte challenges the order: 'Sire, the enemy is too strong. We need reinforcements.' → insist
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Bernadotte (lost 2063) vs Mack (lost 3625) — Lannes's timely arrival aided Bernadotte. Ney and Soult, however, were conspicuously absent.
- CMD `Marshal Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 48,858 if all march) vs Mack (48,375 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1802) vs Mack (lost 8460) — Reinforcements from Davout bolstered Ney's position — though Soult, Murat and Bernadotte never arrived, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 0 attacks
- LEDGER treasury 2394 · net +2258
- DISPATCH: Supply cost you 560 men, at Swabia.

## Turn 2 — Early October 1805
- CMD `Davout, attack Mack` → ✓ Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."
  - POPUP strategic_interrupt: Davout, Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."

The muster reads unfavorable. [b]Commit the Attack[/b] to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (23,753) vs Mack (substantial force) at Nassau — the balance of force looks unfavorable.
  WILL NOT — Ney: cannot march — the field is on soil we are not at war with
  WILL NOT — Bernadotte: cannot march — the field is on soil we are not at war with → attack_anyway
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 2222) vs Mack (lost 5391) — Davout stood alone, Sire. Ney never came.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. Nearby: Wales, Balearics, Ulster
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 0 attacks
- LEDGER treasury 4470 · net +2085
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil.

## Turn 3 — Late October 1805
- CMD `Murat, attack Mack` → ✓ MUSTER — Murat (22,000; 27,030 if all march) vs Mack (substantial force) at Rhineland — the balance of force looks even.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 1757) vs Mack (lost 6805) — Davout's timely arrival aided Murat. Ney and Soult, however, were conspicuously absent.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 action(s) unused) Turn 4 begins!
- enemy phase: 5 actions, 0 attacks
- LEDGER treasury 6526 · net +2188
- DISPATCH: Sire — our ally's marshal Deroy was broken at Croatia. Bavaria reels.

## Turn 4 — Early November 1805
- CMD `Soult, deal with the Austrians` → ✓ MUSTER — Soult (40,000; 80,866 if all march) vs Mack (24,292 men) at Rhineland — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 571) vs Mack (lost 15171) — Ney never reached the guns. The battle was decided without them, Sire.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer → decline
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Franche-Comte to Swabia (158 lost to march)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 action(s) unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks
- LEDGER treasury 8647 · net +2001
- DISPATCH: Sire — Marshal Soult holds the field at Rhineland — Mack's corps is broken and flees.

## Turn 5 — Late November 1805
- CMD `Ney, attack Mack` → ✗ Our purpose in this war awaits your answer, Sire — nothing was relayed. Answer with one of: 1=Conquest, 2=Forced Alliance, 3=Subjugation, 4=Back Out.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Hesse. Our threat level stands at 92 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Hesse → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
- CMD `Davout, attack Mack` → ✓ Davout advances from Rhineland to Swabia, moving toward ArchdukeCharles at Croatia! (Now 4 regions away) (183 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 3 action(s) unused) Turn 6 begins!
- LEDGER treasury 10669 · net +1841
- DISPATCH: Sire — Marshal Ney has now gone unrewarded 3 turns. The staff have noticed which of us he no longer looks at.

## Turn 6 — Early December 1805
- CMD `Massena, attack Archduke Charles` → ✓ Massena pursues ArchdukeCharles (at Croatia). Moves to Tyrol. Massena: "Run him to ground, then. My sabers are hungry."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
- CMD `Bernadotte, move to Swabia` → ✓ Bernadotte moves from Franconia to Swabia (132 lost to march)
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action(s) unused) Turn 7 begins!
- enemy phase: 2 actions, 0 attacks
- LEDGER treasury 12516 · net +1940
- DISPATCH: Sire — Ney, Davout, Lannes and Bernadotte stand 64,219 men at Swabia, which feeds 40,000. 24,219 too many. 4,094 men lost in 2 turns. No depot may be laid at Swabia — not controlled by France. Move a…

## Turn 7 — Late December 1805
- CMD `endow Ney with the Duchy of Swabia` → ✗ We do not hold Swabia — an estate must stand on our own soil.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `Murat, march to Munich` → ✓ Murat begins march to Munich. Cavalry charges through Swabia -> Munich. Murat: "At the double, Sire — the men will smell powder soon enough."
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 action(s) unused) Turn 8 begins!
- enemy phase: 5 actions, 0 attacks
- LEDGER treasury 14072 · net +1932
- DISPATCH: Sire — Massena's corps has been broken at Tyrol. He must reform before he fights again.

## Turn 8 — Early January 1806
- CMD `Ney, march to Munich` → ✓ Ney begins march to Munich. Ney: "At the double, Sire — the men will smell powder soon enough."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
- CMD `Davout, march to Munich` → ✓ Davout begins march to Munich. Davout: "We move deliberately — arrival is worth little if the army arrives broken."
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 1 actions, 0 attacks
- LEDGER treasury 15996 · net +1788
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 9 — Late January 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: advisory → (left standing)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, march to Swabia` → ✓ Soult begins march to Swabia. Moves to Swabia. "Soult, march to Swabia." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP diplomatic_dialogue: incoming_settlement_offer → decline
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 action(s) unused) Turn 10 begins!
- LEDGER treasury 17830 · net +1678
- DISPATCH: Sire — Ney, Davout, Lannes, Murat and Massena stand 71,527 men at Munich, which feeds 25,000. 46,527 too many. 14,610 men lost in 3 turns. No depot may be laid at Munich — not controlled by France. M…

## Turn 10 — Early February 1806
- CMD `grant Murat a rente` → ✓ By Imperial decree, Marshal Murat is granted a rente of 240g/turn upon the treasury (his previous rente of 120g/turn is folded in). With fees and arrears it will cost th…
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `Lannes, march to Munich` → ✓ Lannes begins march to Munich. Lannes: "Good. An army rots standing still."
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 action(s) unused) Turn 11 begins!
- enemy phase: 5 actions, 0 attacks
- LEDGER treasury 19278 · net +1361
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 11 — Late February 1806
- CMD `Ney, march to Vienna` → ✓ Ney begins march to Vienna. Route: Franconia -> Bohemia -> Vienna. Moves to Franconia. Ney: "At the double, Sire — the men will smell powder soon enough."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
- CMD `Davout, march to Vienna` → ✓ Davout begins march to Vienna. Route: Franconia -> Dresden -> Vienna. Moves to Franconia. Davout: "We move deliberately — arrival is worth little if the army arrives bro…
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: 4 actions, 0 attacks
- LEDGER treasury 20595 · net +1196
- DISPATCH: Sire — Lannes, Murat and Massena have been 4 turns over what Munich can feed. 9,933 men. The country will ask where the army went. No depot may be laid at Munich — not controlled by France. Move a co…

## Turn 12 — Early March 1806
- CMD `Murat, march to Vienna` → ✓ Murat begins march to Vienna. Route: Bohemia -> Vienna. Cavalry charges through Franconia -> Bohemia. Murat: "We march. Pity whatever slows us."
- CMD `recruit 10000 infantry` → ✗ Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.' Recruits join a marshal who can reach the depot: Ney (out of range - 6 regions …
  - saved `flagship-1805_t12` → Game saved: flagship-1805_t12
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 action(s) unused) Turn 13 begins!
- enemy phase: 6 actions, 0 attacks
- LEDGER treasury 20391 · net +437
- DISPATCH: Sire — Murat, crowned three turns ago, has been beaten in the field — and the laurels have passed to another.

## Turn 13 — Late March 1806
- CMD `build depot in Swabia` → ✗ Cannot build in Swabia — not controlled by France
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `Bernadotte, attack Archduke John` → ✓ Bernadotte pursues ArchdukeJohn (at Bohemia). Moves to Franconia. Bernadotte: "Pursuit, then. I do not intend to be led into anything."
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 action(s) unused) Turn 14 begins!
- enemy phase: 9 actions, 0 attacks
- LEDGER treasury 21543 · net +1245
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.

## Turn 14 — Early April 1806
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (11,559) vs ArchdukeCharles (20,282 men) at Bohemia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 886) vs Archduke Charles (lost 1045) — Lannes's timely arrival aided Ney. Bernadotte, however, was conspicuously absent.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 action(s) unused) Turn 15 begins!
- enemy phase: 12 actions, 0 attacks
- LEDGER treasury 22140 · net +1064
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.

## Turn 15 — Late April 1806
- CMD `Talleyrand, request terms from Austria` → ✗ Requesting enemy terms is not available for this pair.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 3 actions, 0 attacks
  - POPUP capture_choice[capture]: (no summary fields) → secure
- LEDGER treasury 22511 · net +277
- DISPATCH: Sire — Marshal Shrapnel of Britain is taken at Carniola — he is our prisoner, and their order of battle is one commander shorter.

## Turn 16 — Early May 1806
- CMD `Soult, march to Vienna` → ✓ Soult begins march to Vienna. Route: Franconia -> Bohemia -> Vienna. Moves to Franconia. "Soult, march to Vienna." Understood to the letter. (1 AP — Soult executes preci…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `Massena, march to Tyrol` → ✓ Massena begins march to Tyrol. Moves to Tyrol. Massena: "Good. An army rots standing still."
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action(s) unused) Turn 17 begins!
- enemy phase: 4 actions, 0 attacks
- LEDGER treasury 22645 · net +167
- DISPATCH: Sire — Carniola has been taken by Austria.

## Turn 17 — Late May 1806
- CMD `Ney, attack Kutuzov` → ✓ Ney pursues Kutuzov (at Podolia). Moves to Bohemia. Ney: "Run him to ground, then. My sabers are hungry."
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `Davout, attack Kutuzov` → ✓ Davout firmly objects: 'I have concerns about this order, Sire.'
  - POPUP objection: Davout, Davout firmly objects: 'I have concerns about this order, Sire.' → insist
- CMD `end turn` → ✓ Turn 17 ended. Turn 18 begins!
- enemy phase: 9 actions, 0 attacks
- LEDGER treasury 22410 · net +160
- DISPATCH: Sire — Lannes, crowned last turn, has been driven back.

## Turn 18 — Early June 1806
- CMD `offer peace to Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks
- LEDGER treasury 21572 · net -692
- DISPATCH: Davout's army is recovering. Effectiveness penalty: 0% (recovered).

## Turn 19 — Late June 1806
- CMD `Murat, attack Buxhowden` → ✓ Soult attacks ArchdukeJohn and wins! Continuing his march.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 1070) vs Archduke John (lost 2090) — Reinforcements! Davout and Bernadotte marched onto the field beside Soult. The enemy's advantage melted away.
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `Lannes, attack Buxhowden` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn(s) remaining.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → decline
  - POPUP diplomatic_dialogue: incoming_proposal → decline
  - POPUP proposal_result: You have rejected Ottoman's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 6 actions, 0 attacks
- LEDGER treasury 20574 · net -533
- DISPATCH: Sire — Lannes, crowned three turns ago, has been beaten in the field.

## Turn 20 — Early July 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_sabotage: (no summary fields) → display-only
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `endow Davout with an estate` → ✗ Which province, Sire? Eligible estates: Tyrol, Bohemia. Example: 'endow Davout with Tyrol'.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - saved `flagship-1805_t20` → Game saved: flagship-1805_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 2 actions, 0 attacks
- LEDGER treasury 19993 · net -465
- DISPATCH: Sire — Lannes was mauled at Bohemia: 177 men lost in a single action.

## Turn 21 — Late July 1806
- CMD `Ney, march to Vienna` → ✗ Bernadotte has no active strategic order.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → let_be
- CMD `Davout, march to Vienna` → ✓ Davout begins march to Vienna. Moves to Vienna. Davout: "The roads will be scouted before each march, Sire."
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 action(s) unused) Turn 22 begins!
- enemy phase: 4 actions, 0 attacks
- LEDGER treasury 19513 · net -359
- DISPATCH: Sire — Massena's corps has been broken at Bohemia. He must reform before he fights again.

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 3 actions, 0 attacks
- LEDGER treasury 19204 · net -250
- DISPATCH: Sire — Marshal Soult's household goes unpaid. His patience erodes with his purse.

## Turn 23 — Late August 1806
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Soult (26,515) vs ArchdukeCharles (substantial force) at Moravia — the balance of force looks even.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 2137) vs Archduke Charles (lost 1518) — The walls of the region bear fresh scars, Your Majesty. Their fortifications weaken -- another assault may crack them.
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 3 action(s) unused) Turn 24 begins!
- enemy phase: 6 actions, 0 attacks
- LEDGER treasury 18746 · net -221
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.

## Turn 24 — Early September 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 8 actions, 0 attacks
- LEDGER treasury 19383 · net +539
- DISPATCH: Sire — Massena's corps has been broken at Bohemia. He must reform before he fights again.

---
finished: **completed** · commands 68 · popups 54 · battles 8
