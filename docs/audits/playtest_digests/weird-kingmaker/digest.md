# Playtest digest — weird-kingmaker

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "first", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `vassalize Saxony` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
- CMD `Massena, move to Piedmont` → ✓ Massena moves from Milan to Piedmont (2,520 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - verbs: move×1, attack×1
- LEDGER treasury 2622 · net +2088 · provinces 28
- DISPATCH: Sire — Bernadotte was mauled at Franconia: 5,804 men lost in a single action.

## Turn 2 — Early October 1805
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, move to Rome` → ✗ Cannot enter Rome — it is controlled by PapalStates (diplomatic state: PEACE). Open borders or higher required.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 471) vs Mack (lost 16915) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult never arrived, Sire.
  - POPUP capture_choice[capture]: (no summary fields) → secure
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 5 actions, 1 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - 🏴 Austria: [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - verbs: form_square×2, attack×1, move×1, wait×1
- LEDGER treasury 4673 · net +2263 · provinces 29 (+1)
- DISPATCH: Sire — Ney, crowned last turn, has been driven back.

## Turn 3 — Late October 1805
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 5 actions, 3 attacks — Mack marches from Franche-Comte into Franche-Comte unopposed! (980 lost to march) Captured: France → Austria · [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks]
  - 🏴 Austria: Mack marches from Franche-Comte into Franche-Comte unopposed! (980 lost to march) Captured: France → Austria
  - 🏴 Austria: [Square broken — ArchdukeJohn breaks formation to attacks]
  - verbs: attack×3, move×1, grant_dotation×1
- LEDGER treasury 7047 · net +2177 · provinces 28 (-1)
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil.

## Turn 4 — Early November 1805
- CMD `declare war on Papal States` → ✓ Choose your war purpose against PapalStates.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP diplomatic_dialogue: incoming_settlement_offer → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on PapalStates. Our threat level stands at 74 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: settlement_confirm → 1
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 6 actions, 3 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks] · ArchdukeCharles holds them at Swabia while allies attack from Munich! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles holds them at Swabia while allies attack from Munich! (+1 coordination)
  - verbs: attack×3, form_square×2, grant_dotation×1
- LEDGER treasury 8861 · net +2547 · provinces 27 (-1)
- DISPATCH: Sire — Ney, crowned three turns ago, has been driven back.

## Turn 5 — Late November 1805
- CMD `Massena, attack Rome` → ✓ Choose your war purpose against PapalStates. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on PapalStates. Our threat level stands at 72 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 3 action(s) unused) Turn 6 begins!
- enemy phase: 5 actions, 2 attacks — Mack assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). Mack loses 2,671 troops. Garrison holds — 5,000 d… · Mack assaults the Milan garrison! Garrison collapses (5,000 -> 0). Mack loses 1,335 troops in the assault. Mack marches…
  - 🏴 Austria: Mack assaults the Milan garrison! Garrison collapses (5,000 -> 0). Mack loses 1,335 troops in the assault. Mack marches into Milan! (527 lost to marc…
  - verbs: form_square×2, attack×2, grant_dotation×1
- LEDGER treasury 11237 · net +2121 · provinces 27 (+0)
- DISPATCH: Sire — Milan has been taken by Austria.

## Turn 6 — Early December 1805
- CMD `Davout, attack Mack` → ✓ Davout pursues Mack (at Munich). Moves to Franche-Comte. Davout: "He will be watched at every step. Patience closes traps."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
- CMD `cede tyrol to bavaria` → ✗ No province is eligible to cede to Tyrol — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 action(s) unused) Turn 7 begins!
- enemy phase: 4 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - verbs: move×2, attack×1, form_square×1
  - POPUP capture_choice[capture]: (no summary fields) → secure
- LEDGER treasury 13011 · net +1795 · provinces 28 (+1)
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil.

## Turn 7 — Late December 1805
- CMD `request terms from Papal States` → ✗ France is not at war with this court.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: move×1, fortify×1, stance_change×1
- LEDGER treasury 14657 · net +1449 · provinces 28 (+0)
- DISPATCH: Sire — 3 turns of famine at Lorraine now. 15,085 men gone, and not one of them to the enemy. A supply depot at Lorraine would ease it; Rhineland can feed 60,000 more and Orleanais can feed 52,500 mor…

## Turn 8 — Early January 1806
- CMD `invest in bavaria` → ✗ Berthier peers at the dispatch with concern. "I cannot make sense of this, Sire. A clear order might be: 'Ney, attack ArchdukeCharles' or 'end turn'. For diplomacy: 'dec…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `Ney, attack Mack` → ✓ Ney pursues Mack (at Munich). Moves to Swabia. Ney: "Run him to ground, then. My sabers are hungry."
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 action(s) unused) Turn 9 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: fortify×1, grant_pension×1
- LEDGER treasury 16077 · net +1246 · provinces 29 (+1)
- DISPATCH: Sire — Swabia has fallen to our arms. The tricolor flies over it this morning.

## Turn 9 — Late January 1806
- CMD `vassalize Switzerland` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: VASSAL).
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `guarantee bavaria` → ✗ "Sire, I must confess this order eludes me," Berthier admits. "Shall I relay an order to Ney? Valid actions include: attack, move, scout, defend, fortify, recruit. For d…
  - POPUP diplomatic_dialogue: incoming_settlement_offer → 1
  - POPUP diplomatic_dialogue: incoming_proposal → 1
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: PEACE → OPEN_BORDERS with Prussia. → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 4 actions, 1 attacks — [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: move×1, attack×1, wait×1, recruit×1
- LEDGER treasury 17312 · net +1182 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees.

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: unfortify×1
- LEDGER treasury 18581 · net +1148 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon stand 56,657 men at Munich, which feeds 25,000. 31,657 too many. 6,378 men lost in 2 turns. No depot may be laid at Munich — not controlled by France.…

## Turn 11 — Late February 1806
- CMD `Ney, move to Munich` → ✗ Ney is already in Munich.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- LEDGER treasury 19713 · net +980 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon stand 53,317 men at Munich, which feeds 25,000. 28,317 too many. 9,718 men lost in 3 turns. No depot may be laid at Munich — not controlled by France.…

## Turn 12 — Early March 1806
- CMD `cede swabia to bavaria` → ✗ No province is eligible to cede to Swabia — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- LEDGER treasury 20278 · net +786 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 13 — Late March 1806
- CMD `Davout, attack Archduke John` → ✗ No intelligence on Archduke John's position, Sire. Scout for him before Davout can give chase.
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- LEDGER treasury 21142 · net +960 · provinces 28 (-1)
- DISPATCH: Sire — Milan has been taken by Austria.

## Turn 14 — Early April 1806
- CMD `vassalize Naples` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer → 1
  - POPUP diplomatic_dialogue: incoming_proposal → 1
  - POPUP proposal_result: You have accepted Saxony's proposal. Treaty signed: PEACE → OPEN_BORDERS with Saxony. → display-only
- CMD `invest in bavaria` → ✗ Berthier peers at the dispatch with concern. "I cannot make sense of this, Sire. A clear order might be: 'Ney, attack Castanos' or 'end turn'. For diplomacy: 'declare wa…
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- LEDGER treasury 21077 · net -56 · provinces 25 (-3)
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil.

## Turn 15 — Late April 1806
- CMD `cede munich to bavaria` → ✗ No province is eligible to cede to Munich — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `guarantee saxony` → ✗ France already guarantees Saxony.
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- LEDGER treasury 19862 · net -771 · provinces 24 (-1)
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil.

## Turn 16 — Early May 1806
- CMD `Ney, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Ney can give chase.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- LEDGER treasury 18697 · net -849 · provinces 22 (-2)
- DISPATCH: Sire — Normandy has fallen. Enemy colours fly over French homeland soil.

## Turn 17 — Late May 1806
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (97 lost to march)
  - verbs: move×2, unfortify×1
- LEDGER treasury 17713 · net -820 · provinces 21 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `request terms from Austria` → ✓ Austria fights under Britain's lead in France + Holland vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's to name, not each court's own. I sha…
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 7 actions, 6 attacks — Moore assaults the Paris garrison! Garrison: 25,000 -> 12,500 (-12,500). Moore loses 5,787 troops. Garrison holds — 12,… · Moore assaults the Paris garrison! Garrison: 12,500 -> 6,250 (-6,250). Moore loses 2,893 troops. Garrison holds — 6,250… · Moore assaults the Paris garrison! Garrison collapses (6,250 -> 0). Moore loses 1,446 troops in the assault. Moore marc… · ArchdukeCharles marches from Artois into Picardy unopposed! (180 lost to march) Captured: France → Austria
  - 🏴 Britain: Moore assaults the Paris garrison! Garrison collapses (6,250 -> 0). Moore loses 1,446 troops in the assault. Moore marches into Paris! (785 lost to m…
  - 🏴 Austria: ArchdukeCharles marches from Artois into Picardy unopposed! (180 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles assaults the Flanders garrison! Garrison collapses (6,362 -> 0). ArchdukeCharles loses 1,767 troops in the assault. ArchdukeCharles m…
  - verbs: attack×6, defend×1
- LEDGER treasury 14523 · net -1310 · provinces 18 (-3)
- DISPATCH: Sire — Paris has fallen. Enemy colours fly over French homeland soil.

## Turn 19 — Late June 1806
- CMD `Massena, move to Naples` → ✗ Cannot enter Naples — it is controlled by Naples (diplomatic state: PEACE). Open borders or higher required.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → 1
  - POPUP diplomatic_dialogue: settlement_confirm → 1
- CMD `invest in bavaria` → ✗ "Sire, I must confess this order eludes me," Berthier admits. "Shall I relay an order to Ney? Valid actions include: attack, move, scout, defend, fortify, recruit. For d…
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: unfortify×1, defend×1
- LEDGER treasury 13208 · net -1036 · provinces 18 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon have been 10 turns over what Munich can feed. 5,559 men. The country will ask where the army went. No depot may be laid at Munich — not controlled by …

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `cede tyrol to bavaria` → ✗ No province is eligible to cede to Tyrol — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×1
- LEDGER treasury 12152 · net -805 · provinces 18 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Mack's corps is broken and flees.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×1
- LEDGER treasury 11339 · net -608 · provinces 18 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon have been 12 turns over what Munich can feed. 4,684 men. The country will ask where the army went. No depot may be laid at Munich — not controlled by …

## Turn 22 — Early August 1806
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `guarantee bavaria` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — perhaps 'attack', 'move', 'def…
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×1
- LEDGER treasury 10739 · net -456 · provinces 18 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Buxhowden's corps is broken and flees.

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- LEDGER treasury 10294 · net -350 · provinces 18 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon have been 14 turns over what Munich can feed. 3,920 men. The country will ask where the army went. No depot may be laid at Munich — not controlled by …

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 2 actions, 1 attacks — [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: ArchdukeCharles moves from Flanders to Orleanais. Orleanais falls to Austria! (was France) (701 lost to march)
  - verbs: attack×1, move×1
- LEDGER treasury 9119 · net -907 · provinces 17 (-1)
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 5 actions, 2 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — ArchdukeCharles breaks formation to attacks]
  - verbs: attack×2, retreat×1, stance_change×1, recruit×1
- LEDGER treasury 7900 · net -863 · provinces 17 (+0)
- DISPATCH: Sire — Murat's corps has been broken at Lorraine. He must reform before he fights again.

## Turn 26 — Early October 1806
- CMD `invest in bavaria` → ✗ Berthier peers at the dispatch with concern. "I cannot make sense of this, Sire. A clear order might be: 'Ney, attack ArchdukeCharles' or 'end turn'. For diplomacy: 'dec…
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks
  - 🏴 Austria: ArchdukeCharles moves from Franche-Comte to Swabia. Swabia falls to Austria! (was France) (725 lost to march)
  - verbs: move×1
- LEDGER treasury 6945 · net -749 · provinces 16 (-1)
- DISPATCH: Sire — Swabia has been taken by Austria.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 3 actions, 3 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · ArchdukeCharles holds them at Lorraine while allies attack from Swabia! (+1 coordination) · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: ArchdukeCharles holds them at Lorraine while allies attack from Swabia! (+1 coordination)
  - verbs: attack×3
- LEDGER treasury 5824 · net -569 · provinces 15 (-1)
- DISPATCH: Sire — Lorraine has fallen. Enemy colours fly over French homeland soil.

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 3 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · ArchdukeCharles holds them at Nivernais while allies attack from Lorraine! (+1 coordination)
  - verbs: attack×2, form_square×1
- LEDGER treasury 4891 · net -434 · provinces 15 (+0)
- DISPATCH: Sire — Soult's corps has been broken at Nivernais. He must reform before he fights again.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 4 actions, 4 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×4
- LEDGER treasury 4550 · net -204 · provinces 14 (-1)
- DISPATCH: Sire — Nivernais has fallen. Enemy colours fly over French homeland soil.

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×1
- LEDGER treasury 4135 · net -213 · provinces 12 (-2)
- DISPATCH: Sire — Burgundy has fallen. Enemy colours fly over French homeland soil.

---
finished: **completed** · commands 81 · popups 44 · battles 1
