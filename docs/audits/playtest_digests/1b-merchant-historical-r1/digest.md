# Playtest digest — 1b-merchant-historical-r1

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 797) vs Mack (lost 12882) — Davout, Lannes and Napoleon arrived to reinforce Ney, but Soult, Murat and Bernadotte failed to reach the field in time.
- CMD `Davout, fortify` → ✗ Davout cannot fortify while engaged with enemy forces! Enemy present: Mack. Attack or retreat first.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Archduke Charles (lost 4271) vs Massena (lost 6140) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×1
- LEDGER treasury 2540 · net +2155 · provinces 28
- DISPATCH: Supply cost you 2,531 men, at Swabia.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `build market in Paris` → ✓ Construction started: Market in Paris (2 turns, 350 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, m…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' → trust
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 287) vs Mack (lost 30733) — Ney, Lannes, Murat and Napoleon arrived to reinforce Massena, but Davout and Bernadotte failed to reach the field in ti…
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeJohn breaks formation to attacks]
  - verbs: form_square×2, attack×2
- LEDGER treasury 4577 · net +2349 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Massena holds the field at Munich — Mack's corps is broken and flees.

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `build depot in Lorraine` → ✓ Construction started: Supply Depot in Lorraine (2 turns, 300 gold)
- CMD `Murat, fortify` → ✓ Murat firmly objects: 'Sire, we have the advantage. Let me strike!'
  - POPUP objection: Murat, Murat firmly objects: 'Sire, we have the advantage. Let me strike!' → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 174) vs Mack (lost 5159) — Reinforcements from Lannes, Massena and Napoleon bolstered Murat's position — though Ney never arrived, Sire.
  - POPUP capture_choice[capture]: Tyrol, Murat → secure
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action(s) unused) Turn 4 begins!
- enemy phase: 5 actions, 3 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense) · [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 517) vs Deroy (lost 6310) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 1756) vs Bernadotte (lost 5001) — Bernadotte stood alone, Sire. Ney never came.
  - verbs: attack×3, form_square×1, wait×1
- LEDGER treasury 6627 · net +2442 · provinces 29 (+1)
- DISPATCH: Sire — Bernadotte was mauled at Franconia: 5,001 men lost in a single action.

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `build market in Lyonnais` → ✗ Cannot build in Lyonnais — town regions don't support buildings (need city or larger)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Bernadotte, fortify` → ✗ Bernadotte cannot fortify while engaged with enemy forces! Enemy present: ArchdukeCharles. Attack or retreat first.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 4 actions, 2 attacks — [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense) · [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - 🏴 Austria: [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense)
  - ⚔ Archduke Charles (lost 151) vs Deroy (lost 3652) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 2390) vs Bernadotte (lost 511) — Reinforcements from Massena bolstered Bernadotte's position — though Ney never arrived, Sire.
  - verbs: attack×2, move×2
- LEDGER treasury 9163 · net +2400 · provinces 29 (+0)
- DISPATCH: Sire — Lannes, Murat, Massena and Napoleon stand 66,519 men at Tyrol, which feeds 30,000. 36,519 too many. 7,459 men lost in 2 turns. No depot may be laid at Tyrol — region stability too low (45/100)…

## Turn 5 — Late November 1805
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 4 actions, 3 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 2528) vs Bernadotte (lost 544) — Massena's timely arrival aided Bernadotte. Ney, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 651) vs Bernadotte (lost 5307) — Where was Ney? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 4264) vs Ney (lost 718) — Davout arrived to reinforce Ney, but Murat and Napoleon failed to reach the field in time.
  - verbs: attack×3, form_square×1
  - ⚡ AUTONOMOUS: Lannes is fortified at Tyrol and cannot attack. Order 'unfortify' first to make the army mobile.
- LEDGER treasury 11767 · net +2840 · provinces 29 (+0)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `build training ground in Paris` → ✓ Construction started: Training Ground in Paris (2 turns, 250 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 5 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 3795) vs Ney (lost 258) — Massena and Napoleon arrived to reinforce Ney, but Murat failed to reach the field in time.
  - verbs: form_square×2, move×1, attack×1, grant_dotation×1
  - ⚡ AUTONOMOUS: Lannes is fortified at Tyrol and cannot attack. Order 'unfortify' first to make the army mobile.
- LEDGER treasury 14352 · net +2709 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 7 — Late December 1805
  - LETTER Denmark: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `sponsor prussia against austria, 200 gold` → ✗ Talleyrand: "Prussia's design is aimed at Hanover, not Austria. We can only arm the grievance they already hold."
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 70) vs Archduke John (lost 11013) — Massena and Napoleon arrived to reinforce Murat, but Ney and Davout failed to reach the field in time.
  - POPUP capture_choice[capture]: Franconia, Murat → secure
- LEDGER treasury 15677 · net +1141 · provinces 30 (+1)
- DISPATCH: Sire — Marshal Murat holds the field at Franconia — Archduke John's corps is broken and flees.

## Turn 8 — Early January 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `build market in Burgundy` → ✗ Cannot build in Burgundy — rural regions don't support buildings (need city or larger)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 1 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 7758) vs Lannes (lost 26) — Reinforcements from Ney, Davout, Massena and Napoleon bolstered Lannes's position — though Murat never arrived, Sire.
  - verbs: attack×1
  - ⚡ AUTONOMOUS: Lannes is fortified at Tyrol and cannot attack. Order 'unfortify' first to make the army mobile.
- LEDGER treasury 16847 · net +1053 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Lannes holds the field at Tyrol — Archduke Charles's corps is broken and flees.

## Turn 9 — Late January 1806
- CMD `buy off austria` → ✗ Talleyrand: "We are at WAR with Austria, Sire. Designs are bought off at the peace table, not across a battlefield."
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → let_be
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_proposal → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 1 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - ⚔ Mack (lost 7087) vs Murat (lost 263) — Massena and Napoleon arrived to reinforce Murat, but Ney and Davout failed to reach the field in time.
  - verbs: attack×1
- LEDGER treasury 17903 · net +972 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Murat holds the field at Franconia — Mack's corps is broken and flees.

## Turn 10 — Early February 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `build depot in Rhineland` → ✓ Construction started: Supply Depot in Rhineland (2 turns, 300 gold)
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `guarantee bavaria` → ✓ France guarantees Bavaria. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility st…
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- LEDGER treasury 18565 · net +879 · provinces 30 (+0)
- DISPATCH: Sire — 3 turns of famine at Tyrol now. 9,563 men gone, and not one of them to the enemy. A supply depot at Tyrol would ease it; Milan can feed 75,000 more and Bohemia can feed 40,000 more — a corps m…

## Turn 11 — Late February 1806
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `commission Grouchy` → ✓ Marshal Grouchy accepts his commission and raises a corps of 5,000 at Paris — 4500g. He arrives with a history: Davout (Friendly), Murat (Rival).
  - POPUP marshal_petition: shadow_command, Marshal Massena asks for a command → detach
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 4 actions, 0 attacks
  - verbs: move×2, form_square×2
- LEDGER treasury 15854 · net +1660 · provinces 30 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes and Bernadotte have been 4 turns over what Tyrol can feed. 6,367 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000…

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `build market in Normandy` → ✗ Cannot build in Normandy — rural regions don't support buildings (need city or larger)
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: move×1, form_square×1
  - ⚡ AUTONOMOUS: Lannes is fortified at Tyrol and cannot attack. Order 'unfortify' first to make the army mobile.
- LEDGER treasury 17500 · net +1499 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Ney has now gone unrewarded 3 turns. The staff have noticed which of us he no longer looks at.

## Turn 13 — Late March 1806
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `build fort in Rhineland` → ✗ No building slots available in Rhineland (1/1)
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 3 actions, 1 attacks — [Square broken — Mack breaks formation to attacks]
  - ⚔ Mack (lost 14975) vs Ney (lost 72) — Murat, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
  - verbs: move×1, attack×1, form_square×1
- LEDGER treasury 18967 · net +1345 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Tyrol — Mack's corps is broken and flees.

## Turn 14 — Early April 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `sponsor prussia against austria, 300 gold` → ✗ Talleyrand: "Prussia's design is aimed at Hanover, not Austria. We can only arm the grievance they already hold."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
  - ⚡ AUTONOMOUS: Lannes is fortified at Tyrol and cannot attack. Order 'unfortify' first to make the army mobile.
- LEDGER treasury 20303 · net +1209 · provinces 30 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Bernadotte, Massena and Napoleon have been 7 turns over what Tyrol can feed. 11,683 men. The country will ask where the army went. A supply depot at Tyrol would eas…

## Turn 15 — Late April 1806
  - LETTER Denmark: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `build market in Provence` → ✓ Construction started: Market in Provence (2 turns, 350 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 6 actions, 0 attacks
  - verbs: unfortify×2, move×2, form_square×2
- LEDGER treasury 21203 · net +1151 · provinces 30 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Bernadotte, Massena and Napoleon have been 8 turns over what Tyrol can feed. 14,307 men. The country will ask where the army went. A supply depot at Tyrol would eas…

## Turn 16 — Early May 1806
  - LETTER Naples: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `commission Suchet` → ✓ Marshal Suchet accepts his commission and raises a corps of 5,000 at Paris — 5500g. He arrives with a history: Lannes (Friendly).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 2 actions, 1 attacks — [Square broken — ArchdukeJohn breaks formation to attacks]
  - 🏴 Austria: [Square broken — Mack breaks formation to moves to]
  - ⚔ Archduke John (lost 2757) vs Bernadotte (lost 12) — An exemplary engagement by Bernadotte. The outcome was never in doubt.
  - verbs: attack×1, move×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 753) vs Archduke John (lost 309) — Massena and Napoleon's timely arrival aided Ney. Murat, however, was conspicuously absent.
- LEDGER treasury 17113 · net +1385 · provinces 29 (-1)
- DISPATCH: Sire — Franconia has been taken by Austria.

## Turn 17 — Late May 1806
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `build depot in Flanders` → ✓ Construction started: Supply Depot in Flanders (2 turns, 300 gold)
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (73 lost to march)
  - verbs: move×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 301) vs Mack (lost 6576) — Massena and Napoleon's timely arrival aided Ney. Murat, however, was conspicuously absent.
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- LEDGER treasury 16592 · net -190 · provinces 29 (+0)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `buy off russia` → ✗ Talleyrand: "We are at WAR with Russia, Sire. Designs are bought off at the peace table, not across a battlefield."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `guarantee saxony` → ✗ France already guarantees Saxony.
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
  - ⚡ AUTONOMOUS: Lannes is fortified at Tyrol and cannot attack. Order 'unfortify' first to make the army mobile.
- LEDGER treasury 16438 · net -132 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Lannes, Murat and Bernadotte have been 11 turns over what Tyrol can feed. 6,348 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,…

## Turn 19 — Late June 1806
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `build market in Brittany` → ✗ Cannot build in Brittany — town regions don't support buildings (need city or larger)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 4 actions, 0 attacks
  - verbs: move×2, form_square×2
- LEDGER treasury 16263 · net -149 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Lannes, Murat and Bernadotte have been 12 turns over what Tyrol can feed. 3,323 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,…

## Turn 20 — Early July 1806
  - LETTER Naples: Open Borders Agreement → decline
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 1 actions, 1 attacks — [Square broken — ArchdukeJohn breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeJohn breaks formation to attacks]
  - ⚔ Archduke John (lost 3408) vs Davout (lost 26) — Massena's timely arrival bolstered Davout's position. Well-coordinated, Sire.
  - verbs: attack×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 2163) vs Archduke John (lost 80) — Napoleon arrived to reinforce Ney, but Murat and Massena failed to reach the field in time.
- LEDGER treasury 15957 · net -128 · provinces 29 (+0)
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field — and the laurels sit vacant.

## Turn 21 — Late July 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks
  - 🏴 Austria: [Square broken — Mack breaks formation to moves to]
  - verbs: move×1
- LEDGER treasury 16268 · net +273 · provinces 28 (-1)
- DISPATCH: Sire — Franconia has been taken by Austria.

## Turn 22 — Early August 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `build market in Gascony` → ✓ Construction started: Market in Gascony (2 turns, 350 gold)
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · ArchdukeCharles holds them at Tyrol while allies attack from Bohemia! (+1 coordination)
  - ⚔ Archduke Charles (lost 1202) vs Ney (lost 570) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Archduke Charles (lost 451) vs Bernadotte (lost 312) — The hills were ours, but Archduke Charles took them. Bernadotte's position was overrun.
  - verbs: attack×2, move×1, form_square×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 626) vs Mack (lost 9290) — Reinforcements from Massena and Napoleon bolstered Murat's position — though Davout never arrived, Sire.
  - POPUP capture_choice[capture]: Franconia, Murat → secure
- LEDGER treasury 15361 · net -294 · provinces 29 (+1)
- DISPATCH: Sire — Bernadotte, crowned two turns ago, has been beaten in the field — and the laurels sit vacant.

## Turn 23 — Late August 1806
  - LETTER Denmark: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 3 actions, 3 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 1474) vs Davout (lost 518) — Reinforcement from Murat, Massena and Napoleon kept Davout standing, Sire — but neither side yielded the ground.
  - ⚔ Archduke Charles (lost 1037) vs Davout (lost 2039) — Even the favorable ground could not save Davout, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke Charles (lost 727) vs Davout (lost 1931) — The hills were ours, but Archduke Charles took them. Davout's position was overrun.
  - verbs: attack×3
- LEDGER treasury 14925 · net -141 · provinces 28 (-1)
- DISPATCH: Sire — Massena's corps has been broken at Tyrol. He must reform before he fights again.

## Turn 24 — Early September 1806
  - LETTER Naples: Open Borders Agreement → decline
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- LEDGER treasury 14438 · net -406 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 6 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 25 — Late September 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- LEDGER treasury 13829 · net -527 · provinces 25 (-3)
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil.

## Turn 26 — Early October 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `build depot in Burgundy` → ✗ Cannot build in Burgundy — rural regions don't support buildings (need city or larger)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Suchet seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `commission Oudinot` → ✓ Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 1070) vs Grouchy (lost 270) — Stalemate. Grouchy and Archduke Charles glare at each other across the field.
  - verbs: attack×1
- LEDGER treasury 10178 · net -71 · provinces 25 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 8 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 27 — Late October 1806
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- LEDGER treasury 9787 · net -326 · provinces 24 (-1)
- DISPATCH: Sire — Bordelais has fallen. Enemy colours fly over French homeland soil.

## Turn 28 — Early November 1806
  - LETTER Naples: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: move×1, form_square×1
- LEDGER treasury 9499 · net -249 · provinces 24 (+0)
- DISPATCH: Sire — the levy has stood open 18 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- LEDGER treasury 9277 · net -192 · provinces 24 (+0)
- DISPATCH: Sire — the levy has stood open 19 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.

## Turn 30 — Early December 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- LEDGER treasury 9105 · net -149 · provinces 24 (+0)
- DISPATCH: Sire — the levy has stood open 20 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.

---
finished: **completed** · commands 84 · popups 95 · battles 28
