# Playtest digest — weird-pacifist

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `Ney, hold position` → ✓ Ney will hold Rhineland. Holding position. Ney: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground turn af…
- CMD `Davout, hold position` → ✓ Davout will hold Rhineland. Holding position. Davout: "Good. Let them come to us." (2 AP — a standing strategic order to hold this ground turn after turn. For a single-t…
- CMD `end turn` → ✓ Turn 1 ended. Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - verbs: attack×1
- LEDGER treasury 2504 · net +1991 · provinces 28
- DISPATCH: Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.

## Turn 2 — Early October 1805
- CMD `request terms from Austria` → ✗ No court names terms this early in a war, Sire. (1 turn remaining.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, hold position` → ✓ Soult will hold Lorraine. [Immovable: +15% defense] "Soult, hold position." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, hold position` → ✓ Massena will hold Milan. Holding position. Massena: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground tur…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action(s) unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCh… · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - verbs: attack×3, stance_change×1, wait×1
- LEDGER treasury 4500 · net +1912 · provinces 28 (+0)
- DISPATCH: Sire — our ally's marshal Deroy was broken at Bohemia. Bavaria reels.

## Turn 3 — Late October 1805
- CMD `request terms from Russia` → ✓ Russia fights under Britain's lead in France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's to…
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations Austria. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission → (left standing)
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 6 actions, 4 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination) · [Square broken — Mack breaks formation to attacks] · [!] Deroy is EXPOSED! (Just retreated, no ally to cover)
  - 🏴 Austria: ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - verbs: attack×4, grant_dotation×1, wait×1
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Franconia, Sire. Investigate?' → investigate
- LEDGER treasury 6263 · net +2125 · provinces 28 (+0)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.

## Turn 4 — Early November 1805
- CMD `request terms from Britain` → ✗ The court was asked recently, Sire. (4 turns remaining.)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer → 1
  - POPUP diplomatic_dialogue: settlement_confirm → 1
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Murat, hold position` → ✓ Murat will hold Franche-Comte. Holding position. Murat: "I will hold. They had best not come close enough to tempt me." (2 AP — a standing strategic order to hold this g…
- CMD `Lannes, hold position` → ✓ Lannes will hold Franche-Comte. Holding position. Lannes: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this grou…
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 7 actions, 2 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · [Square broken — Mack breaks formation to attacks]
  - verbs: attack×2, fortify×1, retreat×1, grant_dotation×1, move×1, wait×1
- LEDGER treasury 8359 · net +2152 · provinces 28 (+0)
- DISPATCH: Sire — Lannes, Bernadotte and Massena stand 58,629 men at Munich, which feeds 45,000. 13,629 too many. 2,312 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large…

## Turn 5 — Late November 1805
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Bernadotte, hold position` → ✗ Bernadotte is recovering from retreat (2 turn(s) remaining) and cannot accept strategic orders.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 5 actions, 1 attacks — [Square broken — ArchdukeJohn breaks formation to attacks]
  - verbs: stance_change×1, form_square×1, attack×1, wait×1, recruit×1
  - POPUP capture_choice[capture]: (no summary fields) → secure
- LEDGER treasury 10369 · net +1907 · provinces 29 (+1)
- DISPATCH: Sire — Marshal Murat holds the field at Swabia — Mack's corps is broken and flees.

## Turn 6 — Early December 1805
- CMD `Talleyrand, improve relations with Russia` → ✓ Sire, I shall begin efforts to improve relations Russia. This will cost 1 DP per turn.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: mission → (left standing)
- CMD `release naples` → ✗ Naples is not a vassal.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 3 actions, 1 attacks — Deroy marches from Munich into Franconia unopposed! (55 lost to march — forward supply lines reduce losses) Captured: A…
  - 🏴 Bavaria: Deroy marches from Munich into Franconia unopposed! (55 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - verbs: attack×1, move×1, wait×1
- LEDGER treasury 12346 · net +1859 · provinces 29 (+0)
- DISPATCH: Sire — Swabia has fallen to our arms. The tricolor flies over it this morning.

## Turn 7 — Late December 1805
- CMD `Talleyrand, propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 14333 · net +1828 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Murat holds the field at Bohemia — Archduke John's corps is broken and flees.

## Turn 8 — Early January 1806
- CMD `make amends with Prussia` → ✗ There is nothing to repair with Prussia, Sire. They hold no living grievance against France.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Russia, peace → (left standing)
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 16224 · net +1696 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Murat, Massena and Napoleon stand 70,833 men at Bohemia, which feeds 40,000. 30,833 too many. 6,566 men lost in 2 turns. No depot may be laid at Bohemia — not controlled by France. Vie…

## Turn 9 — Late January 1806
- CMD `Talleyrand, propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- LEDGER treasury 16877 · net +584 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Murat, Massena and Napoleon stand 68,518 men at Bohemia, which feeds 60,000. 8,518 too many. 8,881 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too …

## Turn 10 — Early February 1806
- CMD `Talleyrand, improve relations with Britain` → ✓ Sire, I shall begin efforts to improve relations Britain. This will cost 1 DP per turn.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: mission → (left standing)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- LEDGER treasury 17500 · net +555 · provinces 29 (+0)
- DISPATCH: Sire — 3 turns of famine at Bohemia now. 7,676 men gone, and not one of them to the enemy. Bavaria's magazines feed us as our own — the army is simply too large for the province. Franconia can feed 6…

## Turn 11 — Late February 1806
- CMD `request terms from Austria` → ✓ Austria fights under Britain's lead in France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's t…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 18620 · net +1027 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Murat, Massena and Napoleon have been 4 turns over what Bohemia can feed. 6,606 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simp…

## Turn 12 — Early March 1806
- CMD `release saxony` → ✗ Saxony is not a vassal.
  - POPUP marshal_petition: shadow_command, Marshal Massena asks for a command → detach
  - POPUP diplomatic_dialogue: incoming_settlement_offer → 1
  - POPUP diplomatic_dialogue: settlement_confirm → 1
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `guarantee bavaria` → ✓ France guarantees Bavaria. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility st…
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 3 actions, 0 attacks
  - 🏴 Bavaria: Deroy moves from Carniola to Tyrol. Tyrol falls to Bavaria! (was Austria) (66 lost to march — forward supply lines reduce losses)
  - verbs: move×3
- LEDGER treasury 19638 · net +931 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Murat, Massena and Napoleon have been 5 turns over what Bohemia can feed. 7,031 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simp…

## Turn 13 — Late March 1806
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 6 actions, 1 attacks — [Square broken — Buxhowden breaks formation to attacks]
  - verbs: recruit×2, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP capture_choice[capture]: (no summary fields) → secure
- LEDGER treasury 19809 · net +281 · provinces 30 (+1)
- DISPATCH: Sire — Austria and Bavaria have made peace without us.

## Turn 14 — Early April 1806
- CMD `Talleyrand, improve relations with Prussia` → ✓ Sire, I shall begin efforts to improve relations Prussia. This will cost 1 DP per turn.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: mission → (left standing)
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 7 actions, 0 attacks
  - verbs: move×3, recruit×2, form_square×1, wait×1
- LEDGER treasury 20105 · net +260 · provinces 30 (+0)
- DISPATCH: Sire — Hungary has fallen to our arms. The tricolor flies over it this morning.

## Turn 15 — Late April 1806
- CMD `request terms from Russia` → ✗ The court was asked recently, Sire. (1 turn remaining.)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 6 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - verbs: wait×2, recruit×2, form_square×1, attack×1
- LEDGER treasury 20295 · net +183 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Davout holds the field at Hungary — Mack's corps is broken and flees.

## Turn 16 — Early May 1806
- CMD `Talleyrand, propose non-aggression with Prussia` → ✓ Sire, regarding the Non-Aggression Pact proposal to Prussia, I have prepared terms that reflect the current diplomatic climate.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
  - POPUP proposal_result: Talleyrand departs for the Prussia court with your Non-Aggression Pact proposal. Expect a response by next turn. (2 DP spent) → display-only
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 8 actions, 0 attacks
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (69 lost to march)
  - verbs: move×2, wait×2, grant_pension×2, form_square×1, recruit×1
  - POPUP proposal_result: Prussia has rejected our Non-Aggression Pact. → display-only
- LEDGER treasury 20390 · net +82 · provinces 29 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 17 — Late May 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations Austria. This will cost 1 DP per turn.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: mission → (left standing)
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → 1
  - POPUP diplomatic_dialogue: mission → (left standing)
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: garrison×1, wait×1, recruit×1
- LEDGER treasury 20507 · net +105 · provinces 29 (+0)
- DISPATCH: Supply cost you 1,542 men, at Hungary.

## Turn 18 — Early June 1806
- CMD `request terms from Britain` → ✗ Their terms are already on the desk, Sire — answer the offer in the mailbox.
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 5 actions, 0 attacks
  - verbs: form_square×2, move×2, wait×1
- LEDGER treasury 20580 · net +65 · provinces 29 (+0)
- DISPATCH: Supply cost you 1,495 men, at Hungary.

## Turn 19 — Late June 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — Buxhowden breaks formation to attacks] · [Square broken — Mack breaks formation to attacks]
  - verbs: attack×2, form_square×1, wait×1
- LEDGER treasury 20524 · net +0 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout holds the field at Hungary — Mack's corps is broken and flees.

## Turn 20 — Early July 1806
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 4 actions, 1 attacks — [Square broken — ArchdukeJohn breaks formation to attacks]
  - verbs: wait×2, move×1, attack×1
  - POPUP proposal_result: Austria has accepted our Peace Treaty! → display-only
- LEDGER treasury 20913 · net +358 · provinces 29 (+0)
- DISPATCH: Sire — the war with Austria is over. 4 corps stand on the wrong side of the new frontier. Berthier has given them the road home — Davout to Swabia, Murat to Swabia, Massena to Swabia, Napoleon to Swa…

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 5 actions, 2 attacks — ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,777 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,388 troops in the…
  - 🏴 Austria: ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,388 troops in the assault. ArchdukeCharles marc…
  - verbs: attack×2, break_square×1, move×1, wait×1
- LEDGER treasury 20988 · net +67 · provinces 29 (+0)
- DISPATCH: Sire — Milan has been taken by Austria.

## Turn 22 — Early August 1806
- CMD `Talleyrand, propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer → 1
  - POPUP diplomatic_dialogue: settlement_confirm → 1
- CMD `end turn` → ✗ The terms on the table awaits your answer, Sire — nothing was relayed. Answer with one of: 1=Make peace with Britain only, 2=Armistice with Britain only, 3=Open War Deta…
  - POPUP diplomatic_dialogue: settlement_confirm → 1
- CMD `end turn (retry)` → ✗ The terms on the table awaits your answer, Sire — nothing was relayed. Answer with one of: 1=Make peace with Britain only, 2=Armistice with Britain only, 3=Open War Deta…
  - POPUP diplomatic_dialogue: settlement_confirm → 1
  - ⚠ end turn still refused after the answer pass — stopping the run

---
finished: **blocked** · commands 64 · popups 70 · battles 0
