# Playtest digest — weird-merchant

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 624) vs Mack (lost 13879) — Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Soult, Bernadotte and Napoleon never arr…
- CMD `Davout, fortify` → ✗ Davout cannot fortify while engaged with enemy forces! Enemy present: Mack. Attack or retreat first.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - verbs: attack×1
- LEDGER treasury 2583 · net +2183 · provinces 28
- DISPATCH: Supply cost you 3,211 men, at Swabia.

## Turn 2 — Early October 1805
- CMD `build market in Paris` → ✓ Construction started: Market in Paris (2 turns, 350 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, m…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' → trust
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 173) vs Mack (lost 23528) — Reinforcements! Ney, Davout, Lannes, Murat and Bernadotte marched onto the field beside Massena. The enemy's advantage …
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeJohn breaks formation to attacks]
  - verbs: form_square×2, attack×2
- LEDGER treasury 4696 · net +2412 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Massena holds the field at Munich — Mack's corps is broken and flees.

## Turn 3 — Late October 1805
- CMD `build depot in Lorraine` → ✓ Construction started: Supply Depot in Lorraine (2 turns, 300 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `Murat, fortify` → ✓ Murat firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Murat, Murat firmly objects: 'I would rather attack than sit idle.' → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 412) vs Mack (lost 7465) — Massena arrived to reinforce Murat, but Ney, Davout and Lannes failed to reach the field in time.
  - POPUP capture_choice[capture]: (no summary fields) → secure
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action(s) unused) Turn 4 begins!
- LEDGER treasury 6863 · net +2352 · provinces 29 (+1)
- DISPATCH: Sire — Marshal Mack of Austria is taken at Tyrol — he is our prisoner, and their order of battle is one commander shorter.

## Turn 4 — Early November 1805
- CMD `build market in Lyonnais` → ✗ Cannot build in Lyonnais — town regions don't support buildings (need city or larger)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Bernadotte, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Bernadotte fortifies position at Munich. Defense bonus: +7% (grows +3% per turn…
  - POPUP diplomatic_dialogue: incoming_settlement_offer → decline
  - POPUP diplomatic_dialogue: incoming_proposal → decline
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 action(s) unused) Turn 5 begins!
- LEDGER treasury 9371 · net +2308 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes and Bernadotte stand 68,704 men at Munich, which feeds 37,500. 31,204 too many. 14,576 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too …

## Turn 5 — Late November 1805
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- LEDGER treasury 12087 · net +2572 · provinces 29 (+0)
- DISPATCH: Sire — 3 turns of famine at Munich now. 9,448 men gone, and not one of them to the enemy. Bavaria's magazines feed us as our own — the army is simply too large for the province. Milan can feed 75,000…

## Turn 6 — Early December 1805
- CMD `build training ground in Paris` → ✓ Construction started: Training Ground in Paris (2 turns, 250 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- LEDGER treasury 14473 · net +2512 · provinces 29 (+0)
- DISPATCH: Sire — 4 turns without settlement on Marshal Ney. A rente would close it today; the arrears will not close themselves.

## Turn 7 — Late December 1805
- CMD `sponsor prussia against austria, 200 gold` → ✗ Talleyrand: "Prussia's design is aimed at Hanover, not Austria. We can only arm the grievance they already hold."
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- LEDGER treasury 16301 · net +1719 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes and Bernadotte have been 5 turns over what Munich can feed. 8,168 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply…

## Turn 8 — Early January 1806
- CMD `build market in Burgundy` → ✗ Cannot build in Burgundy — rural regions don't support buildings (need city or larger)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 2 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks]
  - verbs: attack×2
- LEDGER treasury 17991 · net +1724 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Bernadotte and Massena have been 6 turns over what Munich can feed. 10,502 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army…

## Turn 9 — Late January 1806
- CMD `buy off austria` → ✗ Talleyrand: "We are at WAR with Austria, Sire. Designs are bought off at the peace table, not across a battlefield."
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → let_be
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks]
  - 🏴 Austria: [Square broken — ArchdukeCharles breaks formation to attacks]
  - verbs: attack×2, wait×1, grant_dotation×1
- LEDGER treasury 19413 · net +1533 · provinces 28 (-1)
- DISPATCH: Sire — Murat's corps has been broken at Tyrol. He must reform before he fights again.

## Turn 10 — Early February 1806
- CMD `build depot in Rhineland` → ✓ Construction started: Supply Depot in Rhineland (2 turns, 300 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `guarantee bavaria` → ✓ France guarantees Bavaria. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility st…
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- LEDGER treasury 20648 · net +1446 · provinces 28 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Bernadotte and Massena have been 8 turns over what Munich can feed. 16,009 men. The country will ask where the army went. Bavaria's magazines feed us as our own — t…

## Turn 11 — Late February 1806
- CMD `commission Grouchy` → ✓ Marshal Grouchy accepts his commission and raises a corps of 5,000 at Paris — 4500g. He arrives with a history: Davout (Friendly), Murat (Rival).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- LEDGER treasury 17889 · net +1631 · provinces 28 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Bernadotte and Massena have been 9 turns over what Munich can feed. 15,656 men. The country will ask where the army went. Bavaria's magazines feed us as our own — t…

## Turn 12 — Early March 1806
- CMD `build market in Normandy` → ✗ Cannot build in Normandy — rural regions don't support buildings (need city or larger)
  - POPUP marshal_petition: shadow_command, Marshal Soult asks for a command → detach
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: move×1
- LEDGER treasury 19485 · net +1467 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney has now gone unrewarded 3 turns. The staff have noticed which of us he no longer looks at.

## Turn 13 — Late March 1806
- CMD `build fort in Rhineland` → ✗ No building slots available in Rhineland (1/1)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×1
  - POPUP capture_choice[capture]: (no summary fields) → secure
- LEDGER treasury 20218 · net +754 · provinces 29 (+1)
- DISPATCH: Sire — Davout, Lannes, Murat and Bernadotte have been 11 turns over what Munich can feed. 10,741 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is si…

## Turn 14 — Early April 1806
- CMD `sponsor prussia against austria, 300 gold` → ✗ Talleyrand: "Prussia's design is aimed at Hanover, not Austria. We can only arm the grievance they already hold."
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- LEDGER treasury 20976 · net +668 · provinces 29 (+0)
- DISPATCH: Sire — Davout, Lannes, Murat and Bernadotte have been 12 turns over what Munich can feed. 7,022 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is sim…

## Turn 15 — Late April 1806
- CMD `build market in Provence` → ✓ Construction started: Market in Provence (2 turns, 350 gold)
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- LEDGER treasury 21252 · net +575 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 6 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 16 — Early May 1806
- CMD `commission Suchet` → ✓ Marshal Suchet accepts his commission and raises a corps of 5,000 at Paris — 5500g. He arrives with a history: Lannes (Friendly).
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 4 actions, 1 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: unfortify×1, move×1, form_square×1, attack×1
- LEDGER treasury 16026 · net +315 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Tyrol — Archduke Charles's corps is broken and flees.

## Turn 17 — Late May 1806
- CMD `build depot in Flanders` → ✓ Construction started: Supply Depot in Flanders (2 turns, 300 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (97 lost to march)
  - verbs: move×1, defend×1, recruit×1
- LEDGER treasury 16419 · net +650 · provinces 28 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
- CMD `buy off russia` → ✗ Talleyrand: "We are at WAR with Russia, Sire. Designs are bought off at the peace table, not across a battlefield."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Suchet seeks an audience → acknowledge
- CMD `guarantee saxony` → ✗ France already guarantees Saxony.
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 7 actions, 1 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: move×2, attack×1, unfortify×1, form_square×1, grant_pension×1, wait×1
- LEDGER treasury 16789 · net +538 · provinces 27 (-1)
- DISPATCH: Sire — Ney's corps has been broken at Tyrol. He must reform before he fights again.

## Turn 19 — Late June 1806
- CMD `build market in Brittany` → ✗ Cannot build in Brittany — town regions don't support buildings (need city or larger)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 5 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Square broken — ArchdukeJohn breaks formation to attacks]
  - verbs: attack×2, form_square×1, move×1, wait×1
- LEDGER treasury 17238 · net +451 · provinces 27 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 20 — Early July 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: form_square×1, grant_pension×1, wait×1
- LEDGER treasury 17135 · net +59 · provinces 27 (+0)
- DISPATCH: Sire — Murat was mauled at Tyrol: 3,414 men lost in a single action.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×1, recruit×1
- LEDGER treasury 16841 · net -259 · provinces 25 (-2)
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil.

## Turn 22 — Early August 1806
- CMD `build market in Gascony` → ✓ Construction started: Market in Gascony (2 turns, 350 gold)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer → decline
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 4 actions, 1 attacks — [Square broken — Hiller breaks formation to attacks]
  - 🏴 Austria: [Square broken — Hiller breaks formation to attacks]
  - verbs: move×1, attack×1, form_square×1, wait×1
- LEDGER treasury 16068 · net -335 · provinces 24 (-1)
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil.

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×2, form_square×1, wait×1
- LEDGER treasury 15509 · net -402 · provinces 23 (-1)
- DISPATCH: Sire — Bordelais has fallen. Enemy colours fly over French homeland soil.

## Turn 24 — Early September 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 3 actions, 2 attacks — [Square broken — ArchdukeCharles breaks formation to attacks] · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - verbs: attack×2, wait×1
- LEDGER treasury 14069 · net -1189 · provinces 22 (-1)
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×1, recruit×1
- LEDGER treasury 12903 · net -1015 · provinces 22 (+0)
- DISPATCH: Sire — the levy has stood open 14 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.

## Turn 26 — Early October 1806
- CMD `build depot in Burgundy` → ✗ Cannot build in Burgundy — rural regions don't support buildings (need city or larger)
- CMD `commission Oudinot` → ✓ Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 9 actions, 0 attacks
  - 🏴 Britain: [!] DRILL CANCELLED: Paget's drill was interrupted - troops dispersed before training completed.
  - verbs: move×3, form_square×2, recruit×2, garrison×1, wait×1
- LEDGER treasury 8305 · net -897 · provinces 20 (-2)
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 2 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - verbs: attack×1, wait×1
- LEDGER treasury 7425 · net -720 · provinces 20 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 28 — Early November 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 6495 · net -780 · provinces 16 (-4)
- DISPATCH: Sire — Savoy has fallen. Enemy colours fly over French homeland soil.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 6 actions, 0 attacks
  - 🏴 Britain: Paget moves from Gascony to Guyenne. Guyenne falls to Britain! (was France) (66 lost to march)
  - 🏴 Britain: Paget moves from Guyenne to Anjou. Anjou falls to Britain! (was France) (66 lost to march)
  - 🏴 Austria: Schwarzenberg moves from Picardy to Artois. Artois falls to Austria! (was France) (45 lost to march)
  - verbs: move×4, form_square×1, wait×1
- LEDGER treasury 4957 · net -1261 · provinces 13 (-3)
- DISPATCH: Sire — Guyenne has fallen. Enemy colours fly over French homeland soil.

## Turn 30 — Early December 1806
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → (left standing)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 6 actions, 3 attacks — [Square broken — Buxhowden breaks formation to attacks] · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — ArchdukeCharles breaks formation to attacks]
  - verbs: attack×3, move×1, form_square×1, wait×1
- LEDGER treasury 3660 · net -996 · provinces 13 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke Charles's corps is broken and flees.

---
finished: **completed** · commands 84 · popups 37 · battles 3
