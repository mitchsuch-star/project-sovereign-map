# Playtest digest — 1b-pacifist-austerlitz-r1

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
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
  - ⚔ Archduke Charles (lost 2696) vs Massena (lost 6683) — A narrow defeat for Massena, Sire. Better-prepared troops might have tipped the balance.
  - verbs: move×1, stance_change×1, attack×1
- LEDGER treasury 2323 · net +1844 · provinces 28
- DISPATCH: Supply shortage at Milan: Massena loses 911 troops

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `request terms from Austria` → ✗ No court names terms this early in a war, Sire. (1 turn remaining.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, hold position` → ✓ Soult will hold Lorraine. [Immovable: +15% defense] "Soult, hold position." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, hold position` → ✓ Massena firmly objects: 'Sire, we have the advantage. Let me strike!'
  - POPUP objection: Massena, Massena firmly objects: 'Sire, we have the advantage. Let me strike!' → trust
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 2 actions, 2 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 1983) vs Massena (lost 7129) — Massena was close. A period of drilling could have changed the outcome.
  - ⚔ Archduke John (lost 284) vs Massena (lost 6034) — The battle unfolded without particular distinction.
  - verbs: attack×2
- LEDGER treasury 4040 · net +2199 · provinces 28 (+0)
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `request terms from Russia` → ✓ Russia fights under Britain's lead in France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's to…
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations Austria. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Austria. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 3 actions, 3 attacks — [Square broken — Mack breaks formation to attacks] · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · Mack holds them at Franconia while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: Mack holds them at Franconia while allies attack from Swabia! (+1 coordination)
  - ⚔ Mack (lost 2249) vs Bernadotte (lost 5573) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke John (lost 744) vs Massena (lost 5825) — Massena held superior ground, yet Archduke John prevailed. A grim day, Sire.
  - ⚔ Mack (lost 1507) vs Bernadotte (lost 5363) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: attack×3
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Franconia, Sire. Investigate?' → investigate
- LEDGER treasury 5839 · net +2288 · provinces 28 (+0)
- DISPATCH: Sire — Massena's corps has been broken at Piedmont. He must reform before he fights again.

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
- CMD `Lannes, hold position` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.'
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' → trust
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 6 actions, 3 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · Deroy marches from Bohemia into Franconia unopposed! (172 lost to march) Captured: Austria → Bavaria
  - 🏴 Austria: [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - 🏴 Austria: [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Bavaria: Deroy moves from Vienna to Bohemia. Bohemia falls to Bavaria! (was Austria) (174 lost to march)
  - 🏴 Bavaria: Deroy marches from Bohemia into Franconia unopposed! (172 lost to march) Captured: Austria → Bavaria
  - ⚔ Mack (lost 2483) vs Bernadotte (lost 428) — Reinforcement from Lannes kept Bernadotte standing, Sire — but neither side yielded the ground.
  - ⚔ Archduke John (lost 409) vs Massena (lost 6215) — Massena's army has been badly mauled. Archduke John proved the stronger force today.
  - verbs: attack×3, move×2, form_square×1
- LEDGER treasury 7886 · net +1953 · provinces 28 (+0)
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil.

## Turn 5 — Late November 1805
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Bernadotte, hold position` → ✗ Bernadotte is recovering from retreat (1 turn(s) remaining) and cannot accept strategic orders.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 6 actions, 3 attacks — [Square broken — Mack breaks formation to attacks] · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · Mack holds them at Franconia while allies attack from Munich! (+1 coordination)
  - 🏴 Austria: [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Mack (lost 2567) vs Deroy (lost 4509) — A narrow defeat for Deroy, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Archduke John (lost 284) vs Massena (lost 3487) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Mack (lost 1631) vs Deroy (lost 4456) — Deroy's army has been badly mauled. Mack proved the stronger force today.
  - verbs: attack×3, retreat×1, stance_change×1, wait×1
- LEDGER treasury 9553 · net +1526 · provinces 27 (-1)
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil.

## Turn 6 — Early December 1805
- CMD `Talleyrand, improve relations with Russia` → ✓ Sire, I shall begin efforts to improve relations Russia. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Austria.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Russia. (1 DP/turn) → display-only
- CMD `release naples` → ✗ Naples is not a vassal.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 7 actions, 3 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · Mack marches from Franconia into Franconia unopposed! (1,044 lost to march) Captured: Bavaria → Austria · ArchdukeJohn holds them at Paris while allies attack from Limousin! (+1 coordination)
  - 🏴 Austria: Mack marches from Franconia into Franconia unopposed! (1,044 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke John (lost 165) vs Massena (lost 2440) — Massena's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Archduke John (lost 90) vs Massena (lost 1096) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: attack×3, grant_dotation×2, move×1, wait×1
- LEDGER treasury 10754 · net +1134 · provinces 27 (+0)
- DISPATCH: Sire — Massena was mauled at Paris: 2,440 men lost in a single action.

## Turn 7 — Late December 1805
- CMD `Talleyrand, propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 6 actions, 3 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · Mack launches a decisive assault. Ney holds the line. Casualties: Mack 5,836, Ney's army 2,006. Both armies remain in t… · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke John (lost 57) vs Massena (lost 784) — Massena's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Mack (lost 5836) vs Ney (lost 960) — Reinforcements from Lannes and Napoleon bolstered Ney's position — though Murat and Bernadotte never arrived, Sire.
  - ⚔ Archduke John (lost 43) vs Massena (lost 438) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×3, grant_dotation×2, wait×1
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
- LEDGER treasury 11859 · net +1060 · provinces 26 (-1)
- DISPATCH: Sire — Massena was mauled at Paris: 784 men lost in a single action.

## Turn 8 — Early January 1806
- CMD `make amends with Prussia` → ✗ There is nothing to repair with Prussia, Sire. They hold no living grievance against France.
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 action(s) unused) Turn 9 begins!
- enemy phase: 3 actions, 2 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke John (lost 26) vs Massena (lost 245) — A grievous defeat for Massena, Sire. The losses are severe.
  - ⚔ Archduke John (lost 15) vs Massena (lost 159) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: attack×2, wait×1
- LEDGER treasury 12886 · net +873 · provinces 26 (+0)
- DISPATCH: Sire — Massena was mauled at Paris: 245 men lost in a single action.

## Turn 9 — Late January 1806
- CMD `Talleyrand, propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 action(s) unused) Turn 10 begins!
- enemy phase: 2 actions, 2 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke John (lost 11) vs Massena (lost 96) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke John (lost 5) vs Massena (lost 53) — Massena's army has been badly mauled. Archduke John proved the stronger force today.
  - verbs: attack×2
- LEDGER treasury 13725 · net +703 · provinces 26 (+0)
- DISPATCH: Sire — Massena was mauled at Paris: 96 men lost in a single action.

## Turn 10 — Early February 1806
- CMD `Talleyrand, improve relations with Britain` → ✓ Sire, I shall begin efforts to improve relations Britain. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Russia.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Britain. (1 DP/turn) → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 action(s) unused) Turn 11 begins!
- enemy phase: 3 actions, 2 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke John (lost 3) vs Massena (lost 34) — A grievous defeat for Massena, Sire. The losses are severe.
  - ⚔ Archduke John (lost 2) vs Massena (lost 21) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, wait×1
- LEDGER treasury 14573 · net +713 · provinces 25 (-1)
- DISPATCH: Sire — Paris has fallen. Enemy colours fly over French homeland soil.

## Turn 11 — Late February 1806
- CMD `request terms from Austria` → ✗ Their terms are already on the desk, Sire — answer the offer in the mailbox.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → execute_suggestion
  - POPUP proposal_result: I shall ask Britain's chancery to name its terms for France + Spain + Holland + Bavaria vs Britain + Austria, Sire. Expect an answer with the next dispatches. → display-only
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 action(s) unused) Turn 12 begins!
- enemy phase: 2 actions, 1 attacks — [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense)
  - 🏴 Austria: [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense)
  - ⚔ Mack (lost 169) vs Deroy (lost 2469) — A grievous defeat for Deroy, Sire. The losses are severe.
  - verbs: attack×1, wait×1
- LEDGER treasury 14819 · net +206 · provinces 24 (-1)
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil.

## Turn 12 — Early March 1806
- CMD `release saxony` → ✗ Saxony is not a vassal.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `guarantee bavaria` → ✓ France guarantees Bavaria. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility st…
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 3 action(s) unused) Turn 13 begins!
- enemy phase: 4 actions, 1 attacks — [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense)
  - ⚔ Mack (lost 65) vs Deroy (lost 643) — Deroy's army has been badly mauled. Mack proved the stronger force today.
  - verbs: attack×1, retreat×1, grant_dotation×1, wait×1
- LEDGER treasury 14763 · net +143 · provinces 24 (+0)
- DISPATCH: Sire — our ally's marshal Deroy was broken at Swabia. Bavaria reels.

## Turn 13 — Late March 1806
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_confirm) answered `confirm` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `increase autonomy` → ✗ Specify which vassal.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 action(s) unused) Turn 14 begins!
- enemy phase: 2 actions, 1 attacks — ArchdukeJohn assaults the Normandy garrison! Garrison collapses (7,438 -> 0). ArchdukeJohn loses 2,066 troops in the as…
  - 🏴 Austria: ArchdukeJohn assaults the Normandy garrison! Garrison collapses (7,438 -> 0). ArchdukeJohn loses 2,066 troops in the assault. ArchdukeJohn marches in…
  - verbs: attack×1, wait×1
- LEDGER treasury 14646 · net +48 · provinces 23 (-1)
- DISPATCH: Sire — Normandy has fallen. Enemy colours fly over French homeland soil.

## Turn 14 — Early April 1806
- CMD `Talleyrand, improve relations with Prussia` → ✓ Sire, I shall begin efforts to improve relations Prussia. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Britain.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Prussia. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 action(s) unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 14509 · net -112 · provinces 22 (-1)
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil.

## Turn 15 — Late April 1806
- CMD `request terms from Russia` → ✗ France is not at war with this court.
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, peace → (left standing)
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 action(s) unused) Turn 16 begins!
- enemy phase: 7 actions, 5 attacks — ArchdukeCharles assaults the Moravia garrison! Garrison: 2 -> 1 (-1). ArchdukeCharles loses 603 troops. Garrison holds … · ArchdukeCharles assaults the Moravia garrison! Garrison collapses (1 -> 0). ArchdukeCharles loses 591 troops in the ass… · [Combat] Castanos's DEFENSIVE stance hampers offensive operations (-10% attack) · [!] Paget is EXPOSED! (Just retreated, no ally to cover)
  - 🏴 Austria: ArchdukeCharles assaults the Moravia garrison! Garrison collapses (1 -> 0). ArchdukeCharles loses 591 troops in the assault. ArchdukeCharles marches …
  - ⚔ Castanos (lost 453) vs Shrapnel (lost 758) — A narrow defeat for Shrapnel, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Castanos (lost 442) vs Paget (lost 960) — The hills were ours, but Castanos took them. Paget's position was overrun.
  - ⚔ Castanos (lost 257) vs Paget (lost 1166) — Even the favorable ground could not save Paget, Sire. Castanos overcame the terrain.
  - verbs: attack×5, stance_change×1, grant_pension×1
- LEDGER treasury 13873 · net -501 · provinces 22 (+0)
- DISPATCH: Sire — Paget has crossed into Bearn. No French corps stands in his path.

## Turn 16 — Early May 1806
- CMD `Talleyrand, propose non-aggression with Prussia` → ✓ Sire, regarding the Non-Aggression Pact proposal to Prussia, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Prussia court with your Non-Aggression Pact proposal. Expect a response by next turn. (2 DP spent) → display-only
  - POPUP diplomatic_dialogue: Saxony, non_aggression → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 action(s) unused) Turn 17 begins!
- enemy phase: 4 actions, 0 attacks
  - verbs: move×3, fortify×1
- LEDGER treasury 13686 · net -152 · provinces 21 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 17 — Late May 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Prussia.
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Austria. (1 DP/turn) → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → confirm_settlement
- CMD `invest in bavaria` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — perhaps 'attack', 'move', 'def…
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 3 action(s) unused) Turn 18 begins!
- enemy phase: 4 actions, 0 attacks
  - verbs: move×4
- LEDGER treasury 13520 · net -135 · provinces 21 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 9 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 18 — Early June 1806
- CMD `request terms from Britain` → ✓ I shall ask Britain's chancery to name its terms for France + Holland vs Britain + Austria, Sire. Expect an answer with the next dispatches.
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 action(s) unused) Turn 19 begins!
- enemy phase: 6 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 1698) vs Bernadotte (lost 118) — Ney and Lannes arrived to reinforce Bernadotte! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Mack (lost 3944) vs Napoleon (lost 208) — Murat's timely arrival bolstered Napoleon's position. Well-coordinated, Sire.
  - verbs: attack×2, recruit×2, form_square×1, move×1
- LEDGER treasury 13272 · net -137 · provinces 21 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 10 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 19 — Late June 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP proposal_result: Talleyrand departs for the Britain court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 action(s) unused) Turn 20 begins!
- enemy phase: 5 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — Mack breaks formation to attacks]
  - ⚔ Archduke Charles (lost 3465) vs Murat (lost 1348) — Lannes's timely arrival aided Murat. Ney, however, was conspicuously absent.
  - ⚔ Mack (lost 6068) vs Murat (lost 942) — Ney never reached the guns. The battle was decided without them, Sire.
  - verbs: form_square×2, attack×2, recruit×1
  - POPUP proposal_result: Britain has accepted our Peace Treaty! → display-only
- LEDGER treasury 13098 · net +20 · provinces 20 (-1)
- DISPATCH: Sire — Marshal Murat holds the field at Swabia — Mack's corps is broken and flees.

## Turn 20 — Early July 1806
- CMD `Talleyrand, propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 2 action(s) unused) Turn 21 begins!
- enemy phase: 5 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 3320) vs Murat (lost 701) — Reinforcements! Ney and Lannes marched onto the field beside Murat. The enemy's advantage melted away.
  - ⚔ Archduke Charles (lost 180) vs Bernadotte (lost 2049) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: attack×2, move×1, form_square×1, grant_dotation×1
  - POPUP proposal_result: Austria has accepted our Peace Treaty! → display-only
- LEDGER treasury 14588 · net +1644 · provinces 18 (-2)
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 1 action(s) unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: fortify×1, wait×1
- LEDGER treasury 16248 · net +1607 · provinces 18 (+0)
- DISPATCH: Sire — Ney, Lannes, Murat and Napoleon stand 45,311 men at Swabia, which feeds 40,000. 5,311 too many. 2,969 men lost in 2 turns. No depot may be laid at Swabia — not controlled by France. Rhineland …

## Turn 22 — Early August 1806
- CMD `Talleyrand, propose peace with Russia` → ✗ We already have Peace with Russia. Talleyrand sees no purpose in proposing what we already possess.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 1 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 17863 · net +1563 · provinces 18 (+0)
- DISPATCH: Sire — Ney, Lannes, Murat and Napoleon stand 43,863 men at Swabia, which feeds 40,000. 3,863 too many. 4,417 men lost in 3 turns. No depot may be laid at Swabia — not controlled by France. Rhineland …

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action(s) unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: unfortify×1
- LEDGER treasury 18639 · net +733 · provinces 18 (+0)
- DISPATCH: Sire — Lannes, Murat, Napoleon and Ney are no nearer home, and the safe passage runs out in 2 turn(s). After that their corps will be interned where they stand.

## Turn 24 — Early September 1806
- CMD `request terms from Britain` → ✗ France is not at war with this court.
  - POPUP vassal_rebellion_imminent: Holland → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 1 action(s) unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 19335 · net +655 · provinces 18 (+0)
- DISPATCH: Sire — Lannes, Murat, Napoleon and Ney are no nearer home, and the safe passage runs out in 1 turn(s). After that their corps will be interned where they stand.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action(s) unused) Turn 26 begins!
- LEDGER treasury 19935 · net +563 · provinces 18 (+0)
- DISPATCH: Sire — Marshal Paget of Britain is destroyed at Orleanais — his corps annihilated, his name struck from their order of battle.

## Turn 26 — Early October 1806
- CMD `Talleyrand, improve relations with Britain` → ✓ Sire, I shall begin efforts to improve relations Britain. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations Austria.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: mission → start_mission
  - POPUP proposal_result: Talleyrand begins efforts to improve relations Britain. (1 DP/turn) → display-only
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 1 action(s) unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 20456 · net +784 · provinces 18 (+0)
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action(s) unused) Turn 28 begins!
- LEDGER treasury 21180 · net +675 · provinces 18 (+0)
- DISPATCH: Sire — Marshal Ney's corps was interned at Swabia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.

## Turn 28 — Early November 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 1 action(s) unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 21794 · net +570 · provinces 18 (+0)
- DISPATCH: Sire — Marshal Bernadotte has now gone unrewarded 3 turns. The staff have noticed which of us he no longer looks at.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action(s) unused) Turn 30 begins!
- LEDGER treasury 22301 · net +469 · provinces 18 (+0)
- DISPATCH: Sire — 4 turns without settlement on Marshal Bernadotte. A rente would close it today; the arrears will not close themselves.

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → expand_options
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - POPUP diplomatic_dialogue: proposal_options → execute_proposal
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (proposal_options) answered `execute_proposal` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 1 action(s) unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 22705 · net +373 · provinces 18 (+0)
- DISPATCH: Sire — Marshal Bernadotte's grievance is 5 turns old and has stopped being a household matter. It is now a question of the army.

---
finished: **completed** · commands 77 · popups 84 · battles 33
