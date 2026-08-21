# Playtest digest — 1b-pacifist-ulm-r1

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Ney, hold position` → ✓ Ney will hold Rhineland. Holding position. Ney: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground turn af…
- CMD `Davout, hold position` → ✓ Davout will hold Rhineland. Holding position. Davout: "Good. Let them come to us." (2 AP — a standing strategic order to hold this ground turn after turn. For a single-t…
- CMD `end turn` → ✓ Turn 1 ended. Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Archduke Charles (lost 4324) vs Massena (lost 5782) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×1
- LEDGER treasury 2491 · net +1962 · provinces 28
- DISPATCH: Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Naples: Open Borders Agreement → accept
- CMD `request terms from Austria` → ✗ No court names terms this early in a war, Sire. (1 turn remaining.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, hold position` → ✓ Soult will hold Lorraine. [Immovable: +15% defense] "Soult, hold position." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, hold position` → ✓ Massena will hold Milan. Holding position. Massena: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground tur…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action(s) unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles … · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 2585) vs Deroy (lost 5497) — A narrow defeat for Deroy, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Archduke Charles (lost 672) vs Deroy (lost 8508) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, stance_change×1, wait×1
- LEDGER treasury 4494 · net +1921 · provinces 28 (+0)
- DISPATCH: Sire — our ally's marshal Deroy was broken at Bohemia. Bavaria reels.

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `request terms from Russia` → ✓ Russia fights under Britain's lead in France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's to…
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations Austria. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Austria. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 4 actions, 4 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination) · [Square broken — Mack breaks formation to attacks] · ArchdukeCharles flanks from Franconia while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - ⚔ Archduke Charles (lost 921) vs Bernadotte (lost 6796) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke John (lost 30) vs Deroy (lost 3249) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Mack (lost 6203) vs Bernadotte (lost 216) — Lannes and Massena arrived to reinforce Bernadotte! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Archduke Charles (lost 5441) vs Lannes (lost 630) — Murat failed to arrive in time. Lannes's army fought without expected support.
  - verbs: attack×4
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Franconia, Sire. Investigate?' → investigate
- LEDGER treasury 6432 · net +2201 · provinces 28 (+0)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `request terms from Britain` → ✗ The court was asked recently, Sire. (4 turns remaining.)
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Murat, hold position` → ✓ Murat will hold Franche-Comte. Holding position. Murat: "I will hold. They had best not come close enough to tempt me." (2 AP — a standing strategic order to hold this g…
- CMD `Lannes, hold position` → ✓ Lannes will hold Munich. Holding position. Lannes: "I will hold. They had best not come close enough to tempt me." (2 AP — a standing strategic order to hold this ground…
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 3 actions, 1 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 2547) vs Bernadotte (lost 165) — An exemplary engagement by Bernadotte. The outcome was never in doubt.
  - verbs: attack×1, fortify×1, grant_dotation×1
- LEDGER treasury 8794 · net +2179 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Bernadotte holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 5 — Late November 1805
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Bernadotte, hold position` → ✗ Bernadotte is recovering from retreat (2 turn(s) remaining) and cannot accept strategic orders.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: retreat×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 136) vs Archduke Charles (lost 19203) — Davout, Lannes, Massena and Napoleon's timely arrival aided Ney. Murat, however, was conspicuously absent.
- LEDGER treasury 10985 · net +2022 · provinces 29 (+1)
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Archduke Charles's corps is broken and flees.

## Turn 6 — Early December 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Talleyrand, improve relations with Russia` → ✓ Sire, I shall begin efforts to improve relations Russia. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Austria.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Russia. (1 DP/turn) → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `release naples` → ✗ Naples is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 112) vs Archduke Charles (lost 7861) — Davout, Lannes, Massena and Napoleon arrived to reinforce Murat, but Ney failed to reach the field in time.
- LEDGER treasury 13373 · net +2054 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Murat holds the field at Franconia — Archduke Charles's corps is broken and flees.

## Turn 7 — Late December 1805
- CMD `Talleyrand, propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 14) vs Archduke Charles (lost 3084) — Reinforcements! Davout, Lannes, Massena and Napoleon marched onto the field beside Murat. The enemy's advantage melted …
- LEDGER treasury 15246 · net +1751 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Archduke Charles of Austria is taken at Bohemia — he is our prisoner, and their order of battle is one commander shorter.

## Turn 8 — Early January 1806
- CMD `make amends with Prussia` → ✗ There is nothing to repair with Prussia, Sire. They hold no living grievance against France.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Russia, peace → (left standing)
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- LEDGER treasury 17113 · net +1737 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Lannes, Murat, Massena and Napoleon stand 81,142 men at Bohemia, which feeds 40,000. 41,142 too many. 10,351 men lost in 2 turns. No depot may be laid at Bohemia — not controlled by Fr…

## Turn 9 — Late January 1806
- CMD `Talleyrand, propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: shadow_command, Marshal Davout asks for a command → detach
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- LEDGER treasury 18891 · net +1649 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Lannes, Murat, Massena and Napoleon stand 76,647 men at Bohemia, which feeds 40,000. 36,647 too many. 14,846 men lost in 3 turns. No depot may be laid at Bohemia — not controlled by Fr…

## Turn 10 — Early February 1806
- CMD `Talleyrand, improve relations with Britain` → ✓ Sire, I shall begin efforts to improve relations Britain. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Russia.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Britain. (1 DP/turn) → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- LEDGER treasury 20615 · net +1593 · provinces 29 (+0)
- DISPATCH: Sire — 4 turns without settlement on Marshal Ney. A rente would close it today; the arrears will not close themselves.

## Turn 11 — Late February 1806
- CMD `request terms from Austria` → ✓ Austria fights under Britain's lead in France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's t…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- LEDGER treasury 22163 · net +1426 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Lannes, Murat, Massena and Napoleon have been 4 turns over what Bohemia can feed. 12,397 men. The country will ask where the army went. No depot may be laid at Bohemia — not controlled…

## Turn 12 — Early March 1806
- CMD `release saxony` → ✗ Saxony is not a vassal.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `guarantee bavaria` → ✓ France guarantees Bavaria. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility st…
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- LEDGER treasury 23559 · net +1281 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Lannes, Murat, Massena and Napoleon have been 5 turns over what Bohemia can feed. 11,390 men. The country will ask where the army went. No depot may be laid at Bohemia — not controlled…

## Turn 13 — Late March 1806
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- LEDGER treasury 24806 · net +1140 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 7 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 14 — Early April 1806
- CMD `Talleyrand, improve relations with Prussia` → ✓ Sire, I shall begin efforts to improve relations Prussia. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Britain.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Prussia. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: stance_change×1, wait×1, recruit×1
- LEDGER treasury 25900 · net +997 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Lannes, Murat, Massena and Napoleon have been 7 turns over what Bohemia can feed. 9,704 men. The country will ask where the army went. No depot may be laid at Bohemia — not controlled …

## Turn 15 — Late April 1806
- CMD `request terms from Russia` → ✗ The court was asked recently, Sire. (1 turn remaining.)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 3 actions, 2 attacks — [Square broken — Mack breaks formation to attacks] · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Mack (lost 6668) vs Davout (lost 193) — A decisive victory for Davout! Mack was thoroughly outmatched.
  - ⚔ Mack (lost 11531) vs Davout (lost 80) — An exemplary engagement by Davout. The outcome was never in doubt.
  - verbs: attack×2, wait×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 57) vs Archduke John (lost 6345) — Reinforcements! Davout, Murat, Massena and Napoleon marched onto the field beside Lannes. The enemy's advantage melted …
  - POPUP capture_choice[capture]: Vienna, Lannes → secure
- LEDGER treasury 25845 · net +15 · provinces 30 (+1)
- DISPATCH: Sire — Marshal Davout holds the field at Vienna — Mack's corps is broken and flees.

## Turn 16 — Early May 1806
- CMD `Talleyrand, propose non-aggression with Prussia` → ✓ Sire, regarding the Non-Aggression Pact proposal to Prussia, I have prepared terms that reflect the current diplomatic climate.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
  - POPUP proposal_result: Talleyrand departs for the Prussia court with your Non-Aggression Pact proposal. Expect a response by next turn. (2 DP spent) → display-only
  - POPUP diplomatic_dialogue: Saxony, non_aggression → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 2 actions, 1 attacks — [Square broken — Buxhowden breaks formation to attacks]
  - ⚔ Buxhowden (lost 5680) vs Davout (lost 206) — Complete dominance on the field. Buxhowden crumbled before Davout.
  - verbs: attack×1, wait×1
- LEDGER treasury 25779 · net -22 · provinces 30 (+0)
- DISPATCH: Sire — Vienna is taken — Austria's own capital, and the tricolor flies over it this morning.

## Turn 17 — Late May 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Prussia.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP diplomatic_dialogue: Prussia, non_aggression → (left standing)
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Austria. (1 DP/turn) → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Britain court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 4 actions, 1 attacks — [Square broken — Buxhowden breaks formation to attacks]
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (97 lost to march)
  - ⚔ Buxhowden (lost 1673) vs Massena (lost 268) — Complete dominance on the field. Buxhowden crumbled before Massena.
  - verbs: move×1, attack×1, wait×1, recruit×1
  - POPUP proposal_result: Britain has rejected our Peace Treaty. → display-only
- LEDGER treasury 24402 · net -1161 · provinces 29 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
- CMD `request terms from Britain` → ✓ I shall ask Britain's chancery to name its terms for France + Holland + KingdomOfItaly vs Britain + Austria + Russia, Sire. Expect an answer with the next dispatches.
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 3 actions, 2 attacks — [Square broken — Kutuzov breaks formation to attacks] · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Kutuzov (lost 7187) vs Davout (lost 100) — Complete dominance on the field. Kutuzov crumbled before Davout.
  - ⚔ Mack (lost 9563) vs Davout (lost 64) — An exemplary engagement by Davout. The outcome was never in doubt.
  - verbs: attack×2, wait×1
- LEDGER treasury 23157 · net -1051 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout holds the field at Vienna — Mack's corps is broken and flees.

## Turn 19 — Late June 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP proposal_result: Talleyrand departs for the Britain court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
  - POPUP proposal_result: Britain has rejected our Peace Treaty. → display-only
- LEDGER treasury 22046 · net -959 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout's household goes unpaid. His patience erodes with his purse.

## Turn 20 — Early July 1806
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
  - POPUP proposal_result: Austria has accepted our Peace Treaty! → display-only
- LEDGER treasury 21667 · net -330 · provinces 29 (+0)
- DISPATCH: Sire — the war with Austria is over. The peace grants safe passage home.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 3 actions, 1 attacks — [Square broken — Buxhowden breaks formation to attacks]
  - ⚔ Buxhowden (lost 1818) vs Davout (lost 145) — Complete dominance on the field. Buxhowden crumbled before Davout.
  - verbs: attack×1, stance_change×1, wait×1
- LEDGER treasury 21246 · net -340 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout holds the field at Vienna — Buxhowden's corps is broken and flees.

## Turn 22 — Early August 1806
- CMD `Talleyrand, propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 20877 · net -319 · provinces 29 (+0)
- DISPATCH: Sire — 4 turns without settlement on Marshal Davout. A rente would close it today; the arrears will not close themselves.

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 3 actions, 2 attacks — Mack assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). Mack loses 2,777 troops. Garrison holds — 5,000 d… · Mack assaults the Milan garrison! Garrison collapses (5,000 -> 0). Mack loses 1,388 troops in the assault. Mack marches…
  - 🏴 Austria: Mack assaults the Milan garrison! Garrison collapses (5,000 -> 0). Mack loses 1,388 troops in the assault. Mack marches into Milan! (744 lost to marc…
  - verbs: attack×2, wait×1
- LEDGER treasury 20978 · net +90 · provinces 29 (+0)
- DISPATCH: Sire — Milan has been taken by Austria.

## Turn 24 — Early September 1806
- CMD `request terms from Britain` → ✗ Their terms are already on the desk, Sire — answer the offer in the mailbox.
  - POPUP diplomatic_dialogue: Austria, open_borders → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: incoming_proposal → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: PEACE → OPEN_BORDERS with Austria. → display-only
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×2
- LEDGER treasury 20600 · net -363 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout's grievance is 6 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 4 actions, 1 attacks — [Square broken — Buxhowden breaks formation to attacks]
  - ⚔ Buxhowden (lost 5292) vs Davout (lost 113) — An exemplary engagement by Davout. The outcome was never in doubt.
  - verbs: wait×2, attack×1, grant_dotation×1
- LEDGER treasury 20206 · net -330 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout holds the field at Vienna — Buxhowden's corps is broken and flees.

## Turn 26 — Early October 1806
- CMD `Talleyrand, improve relations with Britain` → ✓ Sire, I shall begin efforts to improve relations Britain. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Austria.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Britain. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: wait×2, grant_pension×1
- LEDGER treasury 19896 · net -274 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout's grievance is 8 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×2
- LEDGER treasury 19715 · net -161 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout's grievance is 9 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 28 — Early November 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → execute_suggestion
  - POPUP proposal_result: I shall ask Britain's chancery to name its terms for France + Holland vs Britain + Austria + Russia, Sire. Expect an answer with the next dispatches. → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×2
- LEDGER treasury 19568 · net -130 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout's grievance is 10 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 3 actions, 1 attacks — [Square broken — Buxhowden breaks formation to attacks]
  - ⚔ Buxhowden (lost 3526) vs Lannes (lost 75) — Complete dominance on the field. Buxhowden crumbled before Lannes.
  - verbs: wait×2, attack×1
- LEDGER treasury 19414 · net -115 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Lannes holds the field at Vienna — Buxhowden's corps is broken and flees.

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, non_aggression → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP proposal_result: Talleyrand departs for the Britain court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×2
- LEDGER treasury 19305 · net -96 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Davout's grievance is 12 turns old and has stopped being a household matter. It is now a question of the army.

---
finished: **completed** · commands 77 · popups 106 · battles 21
