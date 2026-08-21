# Playtest digest — 1b-pacifist-historical-r1

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
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
- enemy phase: 3 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Archduke Charles (lost 4036) vs Massena (lost 6497) — The margin was slim. Training and preparation would serve Massena well.
  - verbs: move×1, stance_change×1, attack×1
- LEDGER treasury 2303 · net +1815 · provinces 28
- DISPATCH: Supply shortage at Milan: Massena loses 418 troops

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `request terms from Austria` → ✗ No court names terms this early in a war, Sire. (1 turn remaining.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, hold position` → ✓ Soult will hold Lorraine. [Immovable: +15% defense] "Soult, hold position." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, hold position` → ✓ Massena will hold Milan. Holding position. Massena: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground tur…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action(s) unused) Turn 3 begins!
- enemy phase: 6 actions, 3 attacks — ======================================== · [Square broken — Mack breaks formation to attacks] · ArchdukeJohn marches from Tyrol into Bohemia unopposed! (160 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Bohemia unopposed! (160 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke John (lost 2423) vs Bernadotte (lost 1730) — Stalemate. Bernadotte and Archduke John glare at each other across the field.
  - ⚔ Mack (lost 2109) vs Bernadotte (lost 5199) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: attack×3, retreat×1, form_square×1, stance_change×1
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Franconia, Sire. Investigate?' → investigate
- LEDGER treasury 4281 · net +2045 · provinces 29 (+1)
- DISPATCH: Sire — Bernadotte was mauled at Franconia: 5,199 men lost in a single action.

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `request terms from Russia` → ✓ Russia fights under Britain's lead in France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's to…
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations Austria. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Austria. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 3 actions, 1 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - 🏴 Austria: [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Mack (lost 765) vs Bernadotte (lost 5245) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: move×2, attack×1
- LEDGER treasury 6527 · net +2214 · provinces 30 (+1)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `request terms from Britain` → ✗ The court was asked recently, Sire. (4 turns remaining.)
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Murat, hold position` → ✓ Murat firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Murat, Murat firmly objects: 'I would rather attack than sit idle.' → trust
- CMD `Lannes, hold position` → ✓ Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!'
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' → trust
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: move×1
- LEDGER treasury 8888 · net +2051 · provinces 30 (+0)
- DISPATCH: Bernadotte's army is recovering. Effectiveness penalty: -15%.

## Turn 5 — Late November 1805
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Bernadotte, hold position` → ✗ Bernadotte is recovering from retreat (2 turn(s) remaining) and cannot accept strategic orders.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 3 actions, 2 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 752) vs Deroy (lost 7118) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 4872) vs Massena (lost 3452) — Stalemate. Massena and Mack glare at each other across the field.
  - verbs: attack×2, fortify×1
- LEDGER treasury 10963 · net +2031 · provinces 30 (+0)
- DISPATCH: Sire — our ally's marshal Deroy was broken at Hungary. Bavaria reels.

## Turn 6 — Early December 1805
- CMD `Talleyrand, improve relations with Russia` → ✓ Sire, I shall begin efforts to improve relations Russia. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Austria.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Russia. (1 DP/turn) → display-only
- CMD `release naples` → ✗ Naples is not a vassal.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 4 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Mack (lost 5273) vs Massena (lost 2926) — A standard affair. Nothing unusual to report.
  - verbs: fortify×1, attack×1, move×1, grant_dotation×1
- LEDGER treasury 12938 · net +1907 · provinces 30 (+0)
- DISPATCH: Supply cost you 1,011 men, at Swabia.

## Turn 7 — Late December 1805
- CMD `Talleyrand, propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `increase autonomy` → ✗ Specify which vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 4 actions, 4 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Archduke Charles (lost 3166) vs Massena (lost 3086) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 4317) vs Massena (lost 2061) — An exemplary engagement by Massena. The outcome was never in doubt.
  - ⚔ Archduke Charles (lost 2142) vs Massena (lost 3102) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Mack (lost 3045) vs Massena (lost 1853) — A standard affair. Nothing unusual to report.
  - verbs: attack×4
- LEDGER treasury 14592 · net +1922 · provinces 30 (+0)
- DISPATCH: Supply cost you 991 men, at Swabia.

## Turn 8 — Early January 1806
- CMD `make amends with Prussia` → ✗ There is nothing to repair with Prussia, Sire. They hold no living grievance against France.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Russia, peace → (left standing)
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 5 actions, 3 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · ArchdukeCharles holds them at Tyrol while allies attack from Carniola! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles holds them at Tyrol while allies attack from Carniola! (+1 coordination)
  - ⚔ Archduke Charles (lost 1663) vs Massena (lost 2952) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - ⚔ Mack (lost 2024) vs Massena (lost 1942) — Neither Massena nor Mack could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1007) vs Massena (lost 3292) — Massena held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, unfortify×1, move×1
- LEDGER treasury 16723 · net +2313 · provinces 29 (-1)
- DISPATCH: Sire — Massena, crowned three turns ago, has been hunted across the frontier by Archduke Charles.

## Turn 9 — Late January 1806
- CMD `Talleyrand, propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 3 actions, 3 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · ArchdukeCharles holds them at Milan while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 167) vs Massena (lost 3695) — Massena's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke John (lost 15) vs Massena (lost 1781) — A grievous defeat for Massena, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 34) vs Massena (lost 1157) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: attack×3
- LEDGER treasury 18029 · net +1427 · provinces 29 (+0)
- DISPATCH: Sire — Massena, crowned four turns ago, has been hunted across the frontier by Archduke Charles.

## Turn 10 — Early February 1806
- CMD `Talleyrand, improve relations with Britain` → ✓ Sire, I shall begin efforts to improve relations Britain. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Russia.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Britain. (1 DP/turn) → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 3 actions, 3 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 19) vs Massena (lost 697) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke John (lost 2) vs Massena (lost 370) — Massena's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Archduke Charles (lost 6) vs Massena (lost 209) — Massena's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3
- LEDGER treasury 19354 · net +1205 · provinces 29 (+0)
- DISPATCH: Sire — Massena, crowned five turns ago, has been hunted across the frontier by Archduke Charles.

## Turn 11 — Late February 1806
- CMD `request terms from Austria` → ✓ Austria fights under Britain's lead in France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's t…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 3 actions, 3 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 5) vs Massena (lost 120) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke John (lost 0) vs Massena (lost 45) — Massena's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Archduke Charles (lost 1) vs Massena (lost 68) — Massena's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3
- LEDGER treasury 20677 · net +1166 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Massena's corps has been DESTROYED at Milan. He will not return to the order of battle.

## Turn 12 — Early March 1806
- CMD `release saxony` → ✗ Saxony is not a vassal.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `guarantee bavaria` → ✓ France guarantees Bavaria. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility st…
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 3 actions, 2 attacks — ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,215 troops. G… · ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,531 troops in the assa…
  - 🏴 Austria: ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,531 troops in the assault. ArchdukeJohn marches into…
  - verbs: attack×2, form_square×1
- LEDGER treasury 21767 · net +950 · provinces 29 (+0)
- DISPATCH: Supply cost you 897 men, at Swabia.

## Turn 13 — Late March 1806
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- LEDGER treasury 22318 · net +479 · provinces 28 (-1)
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil.

## Turn 14 — Early April 1806
- CMD `Talleyrand, improve relations with Prussia` → ✓ Sire, I shall begin efforts to improve relations Prussia. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Britain.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Prussia. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- LEDGER treasury 21680 · net -533 · provinces 25 (-3)
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil.

## Turn 15 — Late April 1806
- CMD `request terms from Russia` → ✗ The court was asked recently, Sire. (1 turn remaining.)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: stance_change×1
- LEDGER treasury 20382 · net -701 · provinces 23 (-2)
- DISPATCH: Sire — Normandy has fallen. Enemy colours fly over French homeland soil.

## Turn 16 — Early May 1806
- CMD `Talleyrand, propose non-aggression with Prussia` → ✓ Sire, regarding the Non-Aggression Pact proposal to Prussia, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Prussia court with your Non-Aggression Pact proposal. Expect a response by next turn. (2 DP spent) → display-only
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 8 actions, 3 attacks — Moore assaults the Paris garrison! Garrison: 25,000 -> 12,500 (-12,500). Moore loses 5,787 troops. Garrison holds — 12,… · Moore assaults the Paris garrison! Garrison: 12,500 -> 6,250 (-6,250). Moore loses 2,893 troops. Garrison holds — 6,250… · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 2700) vs Bernadotte (lost 50) — Reinforcements! Lannes marched onto the field beside Bernadotte. The enemy's advantage melted away.
  - verbs: move×4, attack×3, fortify×1
- LEDGER treasury 18584 · net -678 · provinces 23 (+0)
- DISPATCH: Supply cost you 1,763 men, at Swabia.

## Turn 17 — Late May 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Prussia.
  - POPUP marshal_petition: shadow_command, Marshal Soult asks for a command → detach
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP diplomatic_dialogue: Prussia, non_aggression → (left standing)
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Austria. (1 DP/turn) → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → confirm_settlement
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `invest in bavaria` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — perhaps 'attack', 'move', 'def…
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 6 actions, 4 attacks — Moore assaults the Paris garrison! Garrison collapses (8,250 -> 0). Moore loses 1,909 troops in the assault. Moore marc… · [Combat] Castanos's DEFENSIVE stance hampers offensive operations (-10% attack) · Castanos holds them at Toledo while allies attack from Aragon! (+1 coordination) · Castanos holds them at Toledo while allies attack from Aragon! (+1 coordination)
  - 🏴 Britain: Moore assaults the Paris garrison! Garrison collapses (8,250 -> 0). Moore loses 1,909 troops in the assault. Moore marches into Paris! (769 lost to m…
  - 🏴 Spain: Castanos holds them at Toledo while allies attack from Aragon! (+1 coordination)
  - ⚔ Castanos (lost 421) vs Wellesley (lost 687) — Wellesley's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Castanos (lost 276) vs Wellesley (lost 578) — The margin was slim. Training and preparation would serve Wellesley well.
  - ⚔ Castanos (lost 165) vs Wellesley (lost 446) — Wellesley's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×4, wait×1, grant_pension×1
- LEDGER treasury 16911 · net -1182 · provinces 18 (-5)
- DISPATCH: Sire — Paris has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
- CMD `request terms from Britain` → ✓ I shall ask Britain's chancery to name its terms for France + Holland vs Britain + Austria + Russia, Sire. Expect an answer with the next dispatches.
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: fortify×1
- LEDGER treasury 15700 · net -972 · provinces 18 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 19 — Late June 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP proposal_result: Talleyrand departs for the Britain court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 3 actions, 0 attacks
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (67 lost to march)
  - verbs: move×2, form_square×1
  - POPUP proposal_result: Britain has accepted our Peace Treaty! → display-only
- LEDGER treasury 14969 · net -593 · provinces 16 (-2)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 20 — Early July 1806
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 action(s) unused) Turn 21 begins!
- enemy phase: 5 actions, 1 attacks — [Square broken — Buxhowden breaks formation to attacks]
  - ⚔ Buxhowden (lost 8636) vs Murat (lost 353) — Ney, Lannes and Napoleon's timely arrival aided Murat. Davout, however, was conspicuously absent.
  - verbs: unfortify×2, move×2, attack×1
  - POPUP proposal_result: Austria has accepted our Peace Treaty! → display-only
- LEDGER treasury 14652 · net -232 · provinces 15 (-1)
- DISPATCH: Sire — Marshal Murat holds the field at Franche-Comte — Buxhowden's corps is broken and flees.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 action(s) unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×1, recruit×1
- LEDGER treasury 14365 · net -249 · provinces 15 (+0)
- DISPATCH: Sire — Friesland has been taken by Britain.

## Turn 22 — Early August 1806
- CMD `Talleyrand, propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 action(s) unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×1, recruit×1
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
- LEDGER treasury 15548 · net +1145 · provinces 15 (+0)
- DISPATCH: Sire — Ney, Lannes, Murat and Napoleon stand 56,680 men at Franche-Comte, which feeds 52,500. 4,180 too many. 5,859 men lost in 3 turns. No depot may be laid at Franche-Comte — town regions don't sup…

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 action(s) unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 16719 · net +1133 · provinces 15 (+0)
- DISPATCH: Sire — 3 turns of famine at Franche-Comte now. 5,572 men gone, and not one of them to the enemy. No depot may be laid at Franche-Comte — town regions don't support buildings (need city or larger). Lo…

## Turn 24 — Early September 1806
- CMD `request terms from Britain` → ✗ France is not at war with this court.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 action(s) unused) Turn 25 begins!
- LEDGER treasury 17791 · net +1038 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Moore of Britain is destroyed at Flanders — his corps annihilated, his name struck from their order of battle.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 action(s) unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 18861 · net +1036 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Paget of Britain is destroyed at Gelderland — his corps annihilated, his name struck from their order of battle.

## Turn 26 — Early October 1806
- CMD `Talleyrand, improve relations with Britain` → ✓ Sire, I shall begin efforts to improve relations Britain. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Austria.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Britain. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 2 action(s) unused) Turn 27 begins!
- LEDGER treasury 19684 · net +797 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 5 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 action(s) unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 19996 · net +295 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 6 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 28 — Early November 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP vassal_rebellion_imminent: Holland → display-only
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  - POPUP diplomatic_dialogue: proposal_options → start_mission
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Austria. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 2 action(s) unused) Turn 29 begins!
- LEDGER treasury 20254 · net +242 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 7 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 2 action(s) unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 20446 · net +180 · provinces 15 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 8 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 2 action(s) unused) Turn 31 begins!
- LEDGER treasury 20403 · net -40 · provinces 15 (+0)
- DISPATCH: Supply cost you 1,369 men, at Franche-Comte.

---
finished: **completed** · commands 77 · popups 92 · battles 28
