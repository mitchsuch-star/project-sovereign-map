# Playtest digest — 1b-eagle-ulm-r1

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "charge", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Napoleon, move to Rhineland` → ✓ Napoleon moves from Lorraine to Rhineland
- CMD `Ney, hold position` → ✓ Ney will hold Rhineland. Holding position. Ney: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground turn af…
- CMD `Davout, hold position` → ✗ Not enough actions! Need 2, have 1.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Archduke Charles (lost 4324) vs Massena (lost 5782) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×1
- LEDGER treasury 2537 · net +2006 · provinces 28
- DISPATCH: Supply cost you 1,200 men, at Rhineland.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Napoleon, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Mack.
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
- LEDGER treasury 4599 · net +1977 · provinces 28 (+0)
- DISPATCH: Sire — our ally's marshal Deroy was broken at Bohemia. Bavaria reels.

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `Napoleon, attack Mack` → ✓ MUSTER — Napoleon (9,604; 109,853 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 60) vs Mack (lost 15109) — Ney, Davout, Lannes and Murat arrived to reinforce Napoleon! The timely arrival swung the battle in our favor, Sire.
- CMD `Murat, hold position` → ✓ Murat firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Murat, Murat firmly objects: 'I would rather attack than sit idle.' → insist
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action(s) unused) Turn 4 begins!
- enemy phase: 4 actions, 3 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination) · ArchdukeCharles holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - ⚔ Archduke Charles (lost 1069) vs Bernadotte (lost 6127) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke John (lost 32) vs Deroy (lost 3190) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 314) vs Bernadotte (lost 6317) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×3, form_square×1
- LEDGER treasury 6670 · net +2568 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `Napoleon, attack Mack` → ✓ MUSTER — Napoleon (8,883; 133,826 if all march) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 12) vs Mack (lost 32091) — Ney, Davout, Murat and Massena's timely arrival aided Napoleon. Lannes, however, was conspicuously absent.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 action(s) unused) Turn 5 begins!
- enemy phase: 4 actions, 2 attacks — [Square broken — ArchdukeJohn breaks formation to attacks] · [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke John (lost 3204) vs Lannes (lost 973) — Reinforcements! Napoleon marched onto the field beside Lannes. The enemy's advantage melted away.
  - ⚔ Archduke Charles (lost 1148) vs Lannes (lost 3176) — The toll on Lannes's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, stance_change×1, form_square×1
- LEDGER treasury 9288 · net +2749 · provinces 28 (+0)
- DISPATCH: Sire — Lannes, crowned last turn, has been beaten in the field.

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Napoleon, attack Mack` → ✗ Napoleon is recovering from retreat (2 turn(s) remaining) and cannot accept strategic orders.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Lannes, hold position` → ✓ Lannes will hold Swabia. Holding position. Lannes: "Standing guard while others win laurels. As you command." (2 AP — a standing strategic order to hold this ground turn…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 action(s) unused) Turn 6 begins!
- enemy phase: 3 actions, 3 attacks — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Lannes. Heavy casualt… · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Alert] ArchdukeCharles's troops are exhausted from repeated attacks! (2nd attack: -10%)
  - ⚔ Archduke Charles (lost 1818) vs Lannes (lost 656) — Reinforcements from Massena bolstered Lannes's position — though Ney, Davout and Murat never arrived, Sire.
  - ⚔ Archduke John (lost 368) vs Lannes (lost 603) — Ney arrived to reinforce Lannes, but Davout and Murat failed to reach the field in time.
  - ⚔ Archduke Charles (lost 355) vs Lannes (lost 7182) — Lannes stood alone, Sire. Davout and Murat never came.
  - verbs: attack×3
- LEDGER treasury 11697 · net +2746 · provinces 28 (+0)
- DISPATCH: Sire — Lannes, crowned two turns ago, has been hunted on consecutive turns by Archduke Charles.

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Napoleon, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Napoleon can give chase.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 6 actions, 1 attacks — ArchdukeCharles delivers an effective strike. Lannes holds the line. Casualties: ArchdukeCharles's army 1,669, Lannes's…
  - ⚔ Archduke Charles (lost 1211) vs Lannes (lost 101) — Massena's timely arrival aided Lannes. Ney, Davout, Murat and Napoleon, however, were conspicuously absent.
  - verbs: retreat×2, stance_change×2, attack×1, grant_dotation×1
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes awaits your orders. → fight_to_the_last
- LEDGER treasury 14391 · net +2543 · provinces 28 (+0)
- DISPATCH: Sire — Ney, Davout and Murat stand 55,863 men at Munich, which feeds 37,500. 18,363 too many. 12,095 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large for the…

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `Napoleon, move to Munich` → ✓ Napoleon begins marching to Munich (distance: 2). Moved to Swabia. Route: Swabia -> Munich.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `Bernadotte, hold position` → ✗ Marshal Bernadotte is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 action(s) unused) Turn 8 begins!
- LEDGER treasury 16106 · net +1520 · provinces 29 (+1)
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.

## Turn 8 — Early January 1806
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `Napoleon, move to Tyrol` → ✓ Napoleon begins marching to Tyrol (distance: 2). Moved to Franconia. Route: Franconia -> Tyrol.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 action(s) unused) Turn 9 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 2325) vs Napoleon (lost 126) — Reinforcements from Massena bolstered Napoleon's position — though Ney, Davout and Murat never arrived, Sire.
  - verbs: attack×1
- LEDGER treasury 17472 · net +1237 · provinces 30 (+1)
- DISPATCH: Sire — Ney, Davout and Murat have been 4 turns over what Munich can feed. 4,586 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too large fo…

## Turn 9 — Late January 1806
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Napoleon, attack Archduke John` → ✓ MUSTER — Napoleon (6,295; 34,559 if all march) vs ArchdukeJohn (small force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 124) vs Archduke John (lost 469) — Massena arrived to reinforce Napoleon! The timely arrival swung the battle in our favor, Sire.
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 action(s) unused) Turn 10 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: unfortify×1, recruit×1
  - POPUP strategic_interrupt: Napoleon, contact, Berthier: 'Enemy at Bohemia. How shall I proceed?' → attack
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 86) vs Archduke Charles (lost 4100) — Complete dominance on the field. Archduke Charles crumbled before Napoleon.
  - POPUP capture_choice[capture]: Bohemia, Napoleon → secure
- LEDGER treasury 18742 · net +1015 · provinces 31 (+1)
- DISPATCH: Sire — Ney, Davout and Murat have been 5 turns over what Munich can feed. 4,361 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too large fo…

## Turn 10 — Early February 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Napoleon, attack Archduke John` → ✓ MUSTER — Napoleon (5,849; 30,120 if all march) vs ArchdukeJohn (small force) at Vienna — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 33) vs Archduke John (lost 4546) — Massena's timely arrival bolstered Napoleon's position. Well-coordinated, Sire.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 action(s) unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 19853 · net +981 · provinces 31 (+0)
- DISPATCH: Sire — Archduke Charles has crossed into Bohemia. No French corps stands in his path.

## Turn 11 — Late February 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `Napoleon, move to Carniola` → ✗ Cannot advance while engaged with enemy forces. You may retreat to friendly territory.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 3 actions, 2 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · Mack marches from Hungary into Bohemia unopposed! (592 lost to march) Captured: France → Austria
  - 🏴 Austria: Mack marches from Hungary into Bohemia unopposed! (592 lost to march) Captured: France → Austria
  - ⚔ Kutuzov (lost 2285) vs Napoleon (lost 128) — A decisive victory for Napoleon! Kutuzov was thoroughly outmatched.
  - verbs: attack×2, move×1
- LEDGER treasury 20865 · net +914 · provinces 30 (-1)
- DISPATCH: Sire — Bohemia has been taken by Austria.

## Turn 12 — Early March 1806
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Napoleon, attack Archduke Charles` → ✓ MUSTER — Napoleon (5,504; 26,431 if all march) vs ArchdukeCharles (substantial force) at Moravia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 63) vs Archduke Charles (lost 4977) — Massena arrived to reinforce Napoleon! The timely arrival swung the battle in our favor, Sire.
  - POPUP diplomatic_dialogue: Russia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 3 action(s) unused) Turn 13 begins!
- enemy phase: 11 actions, 8 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · Kutuzov holds them at Moravia while allies attack from Ukraine! (+1 coordination) · Bennigsen holds them at Moravia while allies attack from Ukraine! (+1 coordination) · Kutuzov holds them at Moravia while allies attack from Ukraine! (+1 coordination)
  - ⚔ Kutuzov (lost 1816) vs Massena (lost 3008) — Massena was close. A period of drilling could have changed the outcome.
  - ⚔ Kutuzov (lost 1431) vs Massena (lost 4284) — Massena's corps broke, Sire. They are streaming back from the field.
  - ⚔ Bennigsen (lost 34) vs Massena (lost 2871) — The line gave way. Massena is falling back, and not in good order.
  - ⚔ Kutuzov (lost 665) vs Massena (lost 4707) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Mack (lost 131) vs Napoleon (lost 1307) — A grievous defeat for Napoleon, Sire. The losses are severe.
  - ⚔ Mack (lost 79) vs Napoleon (lost 613) — The toll on Napoleon's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Mack (lost 821) vs Massena (lost 2781) — Massena's corps broke, Sire. They are streaming back from the field.
  - ⚔ Mack (lost 708) vs Massena (lost 2259) — Massena's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×8, grant_pension×2, unfortify×1
- LEDGER treasury 20557 · net +705 · provinces 30 (+0)
- DISPATCH: Sire — Napoleon's corps has been broken at Moravia. He must reform before he fights again.

## Turn 13 — Late March 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Napoleon, attack Archduke Charles` → ✓ MUSTER — Napoleon (973) vs ArchdukeCharles (substantial force) at Hungary — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 378) vs Archduke Charles (lost 42) — A grievous defeat for Napoleon, Sire. The losses are severe.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon is ENCIRCLED at Vienna with 2,008 men, Sire — the Guard dies; it does not surrender. Fight to the last, or cut our way out. → fight_to_the_last
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 action(s) unused) Turn 14 begins!
- enemy phase: 10 actions, 7 attacks — [Combat] Bennigsen's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · Buxhowden flanks from Ukraine while allies attack from Moravia! (+1 coordination) · Bennigsen holds them at Moravia while allies attack from Ukraine! (+1 coordination)
  - ⚔ Bennigsen (lost 5) vs Massena (lost 2448) — A grievous defeat for Massena, Sire. The losses are severe.
  - ⚔ Kutuzov (lost 104) vs Massena (lost 1253) — Massena's army has been badly mauled. Kutuzov proved the stronger force today.
  - ⚔ Buxhowden (lost 33) vs Massena (lost 1004) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Bennigsen (lost 0) vs Massena (lost 375) — A grievous defeat for Massena, Sire. The losses are severe.
  - ⚔ Archduke John (lost 5) vs Massena (lost 213) — A grievous defeat for Massena, Sire. The losses are severe.
  - ⚔ Mack (lost 15) vs Massena (lost 120) — A grievous defeat for Massena, Sire. The losses are severe.
  - ⚔ Archduke John (lost 2) vs Massena (lost 78) — Massena's army has been badly mauled. Archduke John proved the stronger force today.
  - verbs: attack×7, grant_pension×2, move×1
- LEDGER treasury 20534 · net +219 · provinces 30 (+0)
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.

## Turn 14 — Early April 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Napoleon, attack Archduke Charles` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 8 actions, 2 attacks — [Combat] Bennigsen's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Bennigsen (lost 0) vs Massena (lost 60) — A grievous defeat for Massena, Sire. The losses are severe.
  - ⚔ Buxhowden (lost 0) vs Massena (lost 66) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: attack×2, fortify×2, grant_pension×1, stance_change×1, wait×1, recruit×1
- LEDGER treasury 21343 · net +690 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Massena's corps has been DESTROYED at Moravia. He will not return to the order of battle.

## Turn 15 — Late April 1806
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `Napoleon, move to Hungary` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 5 actions, 0 attacks
  - verbs: wait×3, fortify×1, recruit×1
- LEDGER treasury 22000 · net +555 · provinces 30 (+0)
- DISPATCH: Supply cost you 1,701 men, at Munich.

## Turn 16 — Early May 1806
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Napoleon, attack Kutuzov` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 22539 · net +454 · provinces 30 (+0)
- DISPATCH: Supply cost you 1,598 men, at Munich.

## Turn 17 — Late May 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Napoleon, attack Kutuzov` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 5 actions, 3 attacks — Shrapnel marches from Toledo into Bearn unopposed! (57 lost to march) Captured: France → Britain · [Square broken — Castanos breaks formation to attacks] · [Square broken — Castanos breaks formation to attacks]
  - 🏴 Britain: Shrapnel marches from Toledo into Bearn unopposed! (57 lost to march) Captured: France → Britain
  - 🏴 Spain: [Square broken — Castanos breaks formation to attacks]
  - ⚔ Castanos (lost 389) vs Paget (lost 768) — Paget's army has been badly mauled. Castanos proved the stronger force today.
  - verbs: attack×3, form_square×1, wait×1
- LEDGER treasury 22633 · net +78 · provinces 29 (-1)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
- CMD `Napoleon, attack Kutuzov` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: wait×1, recruit×1
- LEDGER treasury 22559 · net -61 · provinces 28 (-1)
- DISPATCH: Sire — Bordelais has fallen. Enemy colours fly over French homeland soil.

## Turn 19 — Late June 1806
- CMD `Napoleon, hold position` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 22511 · net -40 · provinces 28 (+0)
- DISPATCH: Supply cost you 1,455 men, at Munich.

## Turn 20 — Early July 1806
- CMD `Napoleon, attack Kutuzov` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 22461 · net -41 · provinces 28 (+0)
- DISPATCH: Sire — Britain and Spain have made peace without us.

## Turn 21 — Late July 1806
- CMD `Napoleon, attack Archduke Charles` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 22443 · net -15 · provinces 28 (+0)
- DISPATCH: Supply cost you 1,288 men, at Munich.

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Napoleon, hold position` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Ney, attack Mack` → ✓ Ney pursues Mack (at Moravia). Moves to Franconia. Ney: "He is already beaten — he merely has not been told. I will tell him."
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 22435 · net -7 · provinces 28 (+0)
- DISPATCH: Supply cost you 511 men, at Munich.

## Turn 23 — Late August 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `request terms from Austria` → ✓ Austria fights under Britain's lead in France + Holland + KingdomOfItaly vs Britain + Austria + Russia, Sire — the coalition's terms are the leader's to name, not each c…
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 21810 · net -501 · provinces 29 (+1)
- DISPATCH: Sire — Bohemia has fallen to our arms. The tricolor flies over it this morning.

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Napoleon, move to Vienna` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 3 actions, 2 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · ArchdukeCharles holds them at Bohemia while allies attack from Vienna! (+1 coordination)
  - ⚔ Archduke Charles (lost 1345) vs Ney (lost 3031) — A standard affair. Nothing unusual to report.
  - ⚔ Archduke Charles (lost 726) vs Ney (lost 4060) — A grievous defeat for Ney, Sire. The losses are severe.
  - verbs: attack×2, wait×1
  - POPUP strategic_interrupt: Ney, last_stand, Ney awaits your orders. → fight_to_the_last
- LEDGER treasury 20939 · net -269 · provinces 29 (+0)
- DISPATCH: Sire — Ney was mauled at Bohemia: 3,031 men lost in a single action.

## Turn 25 — Late September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 20125 · net -649 · provinces 24 (-5)
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil.

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 2 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 2550) vs Davout (lost 475) — An exemplary engagement by Davout. The outcome was never in doubt.
  - verbs: attack×1, wait×1
- LEDGER treasury 19103 · net -780 · provinces 21 (-3)
- DISPATCH: Sire — Anjou has fallen. Enemy colours fly over French homeland soil.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 4 actions, 1 attacks — [Square broken — ArchdukeCharles breaks formation to attacks]
  - ⚔ Archduke Charles (lost 690) vs Murat (lost 934) — Murat held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: form_square×1, attack×1, fortify×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 3486) vs Archduke Charles (lost 1434) — Murat stood alone, Sire. Davout never came.
- LEDGER treasury 17179 · net -1238 · provinces 21 (+0)
- DISPATCH: Sire — Davout, crowned two turns ago, has been driven back.

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 15725 · net -1155 · provinces 18 (-3)
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
- LEDGER treasury 14173 · net -1232 · provinces 15 (-3)
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil.

## Turn 30 — Early December 1806
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks
  - 🏴 Austria: ArchdukeJohn moves from Franconia to Swabia. Swabia falls to Austria! (was France) (88 lost to march)
  - verbs: move×1, wait×1
- LEDGER treasury 12809 · net -1083 · provinces 14 (-1)
- DISPATCH: Sire — Swabia has been taken by Austria.

---
finished: **completed** · commands 74 · popups 66 · battles 44
