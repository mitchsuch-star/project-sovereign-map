# Playtest digest — weird-eagle-in-chains

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "charge", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Napoleon, move to Rhineland` → ✓ Napoleon moves from Lorraine to Rhineland
- CMD `Ney, hold position` → ✓ Ney will hold Rhineland. Holding position. Ney: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground turn af…
- CMD `Davout, hold position` → ✗ Not enough actions! Need 2, have 1.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - verbs: attack×1
- LEDGER treasury 2557 · net +2027 · provinces 28
- DISPATCH: Supply cost you 1,200 men, at Rhineland.

## Turn 2 — Early October 1805
- CMD `Napoleon, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Mack.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, hold position` → ✓ Soult will hold Lorraine. [Immovable: +15% defense] "Soult, hold position." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, hold position` → ✓ Massena will hold Milan. Holding position. Massena: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground tur…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action(s) unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharle… · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - verbs: attack×3, stance_change×1, wait×1
- LEDGER treasury 4619 · net +1977 · provinces 28 (+0)
- DISPATCH: Sire — our ally's marshal Deroy was broken at Bohemia. Bavaria reels.

## Turn 3 — Late October 1805
- CMD `Napoleon, attack Mack` → ✓ MUSTER — Napoleon (9,604; 109,853 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 66) vs Mack (lost 14759) — Reinforcements! Ney, Davout, Lannes and Murat marched onto the field beside Napoleon. The enemy's advantage melted away.
- CMD `Murat, hold position` → ✓ Murat firmly objects: 'Sire, we have the advantage. Let me strike!'
  - POPUP objection: Murat, Murat firmly objects: 'Sire, we have the advantage. Let me strike!' → insist
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action(s) unused) Turn 4 begins!
- enemy phase: 5 actions, 2 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - 🏴 Austria: ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - verbs: attack×2, form_square×2, wait×1
- LEDGER treasury 6859 · net +2575 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.

## Turn 4 — Early November 1805
- CMD `Napoleon, attack Mack` → ✓ MUSTER — Napoleon (8,877; 133,730 if all march) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 9) vs Mack (lost 28650) — Ney, Davout, Lannes, Murat and Massena's timely arrival bolstered Napoleon's position. Well-coordinated, Sire.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → decline
  - POPUP diplomatic_dialogue: incoming_proposal → decline
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 action(s) unused) Turn 5 begins!
- enemy phase: 5 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks]
  - verbs: attack×2, stance_change×1, form_square×1, wait×1
- LEDGER treasury 9617 · net +2632 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke John's corps is broken and flees.

## Turn 5 — Late November 1805
- CMD `Napoleon, attack Mack` → ✓ MUSTER — Napoleon (8,139; 88,185 if all march) vs Mack (5,042 men) at Franconia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 1) vs Mack (lost 4474) — Davout, Lannes and Massena arrived to reinforce Napoleon, but Ney and Murat failed to reach the field in time.
  - POPUP capture_choice[capture]: (no summary fields) → secure
- CMD `Lannes, hold position` → ✓ Lannes will hold Franconia. Holding position. Lannes: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground t…
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action(s) unused) Turn 6 begins!
- enemy phase: 4 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - verbs: attack×1, stance_change×1, wait×1, recruit×1
- LEDGER treasury 11902 · net +2107 · provinces 29 (+1)
- DISPATCH: Sire — Archduke Charles has crossed into Rhineland. No French corps stands in his path.

## Turn 6 — Early December 1805
- CMD `Napoleon, attack Mack` → ✓ Napoleon pursues Mack (at Bohemia). Moves to Franconia. (1 AP — the Emperor commands in his own name.)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 action(s) unused) Turn 7 begins!
- enemy phase: 4 actions, 1 attacks — ArchdukeCharles marches from Rhineland into Rhineland unopposed! (480 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Rhineland into Rhineland unopposed! (480 lost to march) Captured: France → Austria
  - verbs: move×2, attack×1, wait×1
- LEDGER treasury 14096 · net +1989 · provinces 28 (-1)
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil.

## Turn 7 — Late December 1805
- CMD `Napoleon, move to Munich` → ✓ Napoleon moves from Franconia to Munich (144 lost to march)
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `Bernadotte, hold position` → ✗ Marshal Bernadotte is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 action(s) unused) Turn 8 begins!
- enemy phase: 7 actions, 3 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · Deroy marches from Franconia into Swabia unopposed! (45 lost to march — forward supply lines reduce losses) Captured: A… · [!] ArchdukeCharles is EXPOSED! (Just retreated, no ally to cover)
  - 🏴 Bavaria: Deroy marches from Franconia into Swabia unopposed! (45 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - 🏴 Bavaria: [!] ArchdukeCharles is EXPOSED! (Just retreated, no ally to cover)
  - verbs: attack×3, grant_dotation×2, form_square×1, wait×1
  - POPUP strategic_interrupt: Napoleon, cannon_fire, Berthier: 'Cannon fire at Munich, Sire. Investigate?' → investigate
- LEDGER treasury 15167 · net +975 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 8 — Early January 1806
- CMD `Napoleon, move to Tyrol` → ✓ Napoleon moves from Munich to Tyrol. Tyrol falls to France! (was Austria) (132 lost to march)
  - POPUP capture_choice[capture]: (no summary fields) → secure
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 action(s) unused) Turn 9 begins!
- enemy phase: 2 actions, 1 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×1, wait×1
- LEDGER treasury 16089 · net +836 · provinces 29 (+1)
- DISPATCH: Sire — the Emperor Napoleon holds the field at Tyrol — Buxhowden's corps is broken and flees.

## Turn 9 — Late January 1806
- CMD `Napoleon, attack Archduke John` → ✓ MUSTER — Napoleon (6,106; 67,250 if all march) vs ArchdukeJohn (small force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 24) vs Archduke John (lost 1474) — Davout, Lannes and Massena arrived to reinforce Napoleon, but Ney failed to reach the field in time.
  - POPUP capture_choice[capture]: (no summary fields) → secure
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 action(s) unused) Turn 10 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 16905 · net +743 · provinces 30 (+1)
- DISPATCH: Sire — the Emperor Napoleon holds the field at Bohemia — Archduke John's corps is broken and flees.

## Turn 10 — Early February 1806
- CMD `Napoleon, attack Archduke John` → ✓ MUSTER — Napoleon (5,835; 56,922 if all march) vs ArchdukeJohn (small force) at Vienna — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 9) vs Archduke John (lost 7817) — Lannes and Massena's timely arrival aided Napoleon. Davout, however, was conspicuously absent.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 action(s) unused) Turn 11 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: move×3
- LEDGER treasury 17777 · net +782 · provinces 30 (+0)
- DISPATCH: Sire — the Emperor Napoleon holds the field at Vienna — Archduke John's corps is broken and flees.

## Turn 11 — Late February 1806
- CMD `Napoleon, move to Carniola` → ✓ Napoleon begins marching to Carniola (distance: 2). Moved to Bohemia. Route: Bohemia -> Carniola.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 action(s) unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 19190 · net +1300 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Ney has now gone unrewarded 3 turns. The staff have noticed which of us he no longer looks at.

## Turn 12 — Early March 1806
- CMD `Napoleon, attack Archduke Charles` → ✗ Enemy 'ArchdukeCharles' not found. Did you mean 'ArchdukeJohn'?
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- LEDGER treasury 20411 · net +1138 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Massena holds the field at Hungary — Archduke John's corps is broken and flees.

## Turn 13 — Late March 1806
- CMD `Napoleon, attack Archduke Charles` → ✗ Enemy 'ArchdukeCharles' not found. Did you mean 'ArchdukeJohn'?
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: move×1, wait×1
- LEDGER treasury 21494 · net +1000 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Massena holds the field at Moravia — Archduke John's corps is broken and flees.

## Turn 14 — Early April 1806
- CMD `Napoleon, attack Archduke Charles` → ✓ MUSTER — Napoleon (5,034; 46,568 if all march) vs ArchdukeCharles (small force) at Vienna — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 4) vs Archduke Charles (lost 2595) — Davout, Lannes and Massena arrived to reinforce Napoleon! The timely arrival swung the battle in our favor, Sire.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 action(s) unused) Turn 15 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: retreat×1, stance_change×1, wait×1
- LEDGER treasury 22551 · net +964 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Archduke Charles of Austria is taken at Vienna — he is our prisoner, and their order of battle is one commander shorter.

## Turn 15 — Late April 1806
- CMD `Napoleon, move to Hungary` → ✗ Cannot move into Hungary - enemy forces present! Use ATTACK to engage Mack.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: move×1, wait×1
- LEDGER treasury 22479 · net -65 · provinces 30 (+0)
- DISPATCH: Sire — Britain and Spain have made peace without us.

## Turn 16 — Early May 1806
- CMD `Napoleon, attack Kutuzov` → ✓ Napoleon pursues Kutuzov (at Podolia). (1 AP — the Emperor commands in his own name.)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 action(s) unused) Turn 17 begins!
- enemy phase: 6 actions, 2 attacks — Mack marches from Hungary into Bohemia unopposed! (493 lost to march — forward supply lines reduce losses) Captured: Fr… · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (97 lost to march)
  - 🏴 Austria: Mack marches from Hungary into Bohemia unopposed! (493 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - verbs: move×2, attack×2, unfortify×1, wait×1
- LEDGER treasury 22088 · net -278 · provinces 28 (-2)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 17 — Late May 1806
- CMD `Napoleon, attack Kutuzov` → ✓ Napoleon is already carrying out that order. No change.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- LEDGER treasury 21151 · net -815 · provinces 29 (+1)
- DISPATCH: Sire — Moravia has fallen to our arms. The tricolor flies over it this morning.

## Turn 18 — Early June 1806
- CMD `Napoleon, attack Kutuzov` → ✓ MUSTER — Napoleon (4,495) vs Kutuzov (substantial force) at Podolia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 1753) vs Kutuzov (lost 285) — Napoleon's army has been badly mauled. Kutuzov proved the stronger force today.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 action(s) unused) Turn 19 begins!
- enemy phase: 5 actions, 2 attacks — [Combat] Bennigsen's DEFENSIVE stance hampers offensive operations (-10% attack) · [Shield] Massena steps forward to cover Napoleon's retreat! "Napoleon is in no condition to fight - I'll handle this!"
  - verbs: attack×2, unfortify×1, move×1, recruit×1
- LEDGER treasury 20730 · net -242 · provinces 28 (-1)
- DISPATCH: Sire — Napoleon's corps has been broken at Moravia. He must reform before he fights again.

## Turn 19 — Late June 1806
- CMD `Napoleon, hold position` → ✗ Napoleon is recovering from retreat (2 turn(s) remaining) and cannot accept strategic orders.
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 10 actions, 4 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · ======================================== · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×4, recruit×4, wait×2
- LEDGER treasury 20271 · net -241 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Lannes holds the field at Vienna — Buxhowden's corps is broken and flees.

## Turn 20 — Early July 1806
- CMD `Napoleon, attack Kutuzov` → ✓ Napoleon pursues Kutuzov (at Podolia). (1 AP — the Emperor commands in his own name.)
  - POPUP diplomatic_dialogue: incoming_settlement_offer → decline
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 action(s) unused) Turn 21 begins!
- LEDGER treasury 19979 · net -259 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney has now gone unrewarded 3 turns. The staff have noticed which of us he no longer looks at.

## Turn 21 — Late July 1806
- CMD `Napoleon, attack Archduke Charles` → ✗ Enemy 'ArchdukeCharles' not found. Did you mean 'ArchdukeJohn'?
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
  - POPUP strategic_interrupt: Napoleon, contact, Berthier: 'Enemy forces discovered at Moravia! How shall I proceed?' → attack
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 6) vs Bennigsen (lost 157) — Reinforcements! Davout, Lannes and Massena marched onto the field beside Napoleon. The enemy's advantage melted away.
- LEDGER treasury 19671 · net -303 · provinces 28 (+0)
- DISPATCH: Sire — 4 turns without settlement on Marshal Ney. A rente would close it today; the arrears will not close themselves.

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `Napoleon, hold position` → ✓ Napoleon will hold Moravia. Holding position. (1 AP — the Emperor commands in his own name.)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (13,719) vs Mack (substantial force) at Bohemia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2974) vs Mack (lost 1842) — An inconclusive affair. Both sides bloodied but unbroken.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×1
- LEDGER treasury 19244 · net -239 · provinces 28 (+0)
- DISPATCH: Sire — the Emperor Napoleon holds the field at Moravia — Buxhowden's corps is broken and flees.

## Turn 23 — Late August 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP marshal_petition: shadow_command, Marshal Massena asks for a command → detach
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `request terms from Austria` → ✓ Austria fights under Britain's lead in France + Holland + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's to name, not each c…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 5 actions, 0 attacks
  - verbs: recruit×2, retreat×1, stance_change×1, wait×1
- LEDGER treasury 18931 · net -259 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Vienna — Archduke John's corps is broken and flees.

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → decline
- CMD `Napoleon, move to Vienna` → ✗ Napoleon is already in Vienna.
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 6 actions, 0 attacks
  - verbs: move×2, wait×2, recruit×2
- LEDGER treasury 18655 · net -240 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 7 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 25 — Late September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×2
- LEDGER treasury 18430 · net -197 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 8 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 4 actions, 0 attacks
  - verbs: move×4
- LEDGER treasury 17942 · net -425 · provinces 26 (-2)
- DISPATCH: Sire — Tyrol has been taken by Austria.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 2 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - verbs: fortify×1, attack×1
- LEDGER treasury 17437 · net -339 · provinces 26 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 10 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 5 actions, 3 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — ArchdukeJohn breaks formation to attacks] · [Square broken — Mack breaks formation to attacks]
  - verbs: attack×3, move×1, wait×1
- LEDGER treasury 16917 · net -268 · provinces 26 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Vienna — Buxhowden's corps is broken and flees.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — ArchdukeJohn breaks formation to attacks] · [Square broken — Mack breaks formation to attacks]
  - verbs: attack×2, form_square×1, recruit×1
- LEDGER treasury 16561 · net -198 · provinces 26 (+0)
- DISPATCH: Sire — Marshal Murat holds the field at Munich — Archduke John's corps is broken and flees.

## Turn 30 — Early December 1806
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 5 actions, 0 attacks
  - verbs: move×3, form_square×1, recruit×1
  - POPUP capture_choice[capture]: (no summary fields) → secure
- LEDGER treasury 15875 · net -604 · provinces 27 (+1)
- DISPATCH: Sire — Marshal Ney holds the field at Moravia — Bennigsen's corps is broken and flees.

---
finished: **completed** · commands 74 · popups 38 · battles 9
